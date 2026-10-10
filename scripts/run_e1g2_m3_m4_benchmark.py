#!/usr/bin/env python3
"""Exploratory E1G2 benchmark: M3 baselines and M4 frozen foundation-model probes.

Run from the repository root (after the M3 preprocessing and label scripts):
  uv run --no-project --python 3.11 --with numpy --with scipy --with matplotlib \
      --with scikit-learn --with torch==2.5.1 \
      python scripts/run_e1g2_m3_m4_benchmark.py --methods m3
  torch==2.5.1 (CUDA 12.4) is pinned because this machine's driver supports CUDA
  12.5; newer default wheels (CUDA 13) silently fall back to the CPU.
  M4 linear probes read embeddings saved by scripts/extract_e1g2_foundation_embeddings.py;
  use the same environment and pass --methods m4 --m4-features "Name=path.npy,...". The probe is
  one linear layer trained with AdamW (GPU when available), early-stopped on val blocks.

EXPLORATORY, PRE-GATE. The labels are coarse groups from the USGS Unified
Geologic Map of the Moon (1:5M) rasterized onto provisional geometry. They are
proxy labels, not reviewed ground truth. Inputs are provisional apparent
reflectance (845-2460 nm, topography-normalized, destriped, polished, despiked).

Contact buffer (fixed before scoring): a pixel is used only if every pixel
within 25 px (about 2 km) along-track and across-track has the same label,
because shifting the 1:5M map by 2 km changes about 21% of unit labels.

Frozen split (declared before any score was computed): the 12,210 lines are
cut into 250-line blocks; blocks follow the repeating pattern train, train,
val, test; 25 lines at each block edge are dropped as guards. Classes with
fewer than MIN_TEST test pixels are excluded from scoring and listed.
Training uses at most 20,000 pixels per class (fixed seed). Validation is used
only for early stopping of the CNN. Metrics on test blocks: macro F1 and
balanced accuracy, with 95% intervals from 1,000 bootstrap resamples of test
blocks.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data/derived/e1g2"
OUT = ROOT / "results/phase-2/m4-transfer"
OUT_M3 = ROOT / "results/phase-1/m3-supervised-baselines"
BLOCK, GUARD, MIN_TEST, PER_CLASS, BUFFER = 250, 25, 5000, 20000, 25
PATTERN = ["train", "train", "val", "test"]
SEED = 0


def split_lines(nl, guard=GUARD):
    split = np.full(nl, "none", dtype=object)
    block_id = np.arange(nl) // BLOCK
    pos = np.arange(nl) % BLOCK
    keep = (pos >= guard) & (pos < BLOCK - guard)
    for b in np.unique(block_id):
        m = (block_id == b) & keep
        split[m] = PATTERN[b % len(PATTERN)]
    return split, block_id


def load_inputs(label_file):
    cube = np.load(DERIVED / "m3_preprocessed_reflectance.npy", mmap_mode="r")
    good = np.load(DERIVED / "m3_preprocessed_good.npy")
    wl = np.loadtxt(DERIVED / "m3_preprocessed_wavelengths_nm.txt")
    labels = np.load(DERIVED / label_file).astype(np.int16)
    from scipy.ndimage import maximum_filter, minimum_filter
    size = 2 * BUFFER + 1
    lab = np.where(labels >= 0, labels, -1)
    interior = (maximum_filter(lab, size=size, mode="nearest") ==
                minimum_filter(lab, size=size, mode="nearest"))
    labels = np.where(interior, labels, -1)
    return cube, good, wl, labels


def sample_indices(y, split, rng):
    out = {}
    for name in ("train", "val", "test"):
        idx = np.where(split == name)[0]
        if name == "test":
            out[name] = idx
            continue
        chosen = []
        for c in np.unique(y[idx]):
            ci = idx[y[idx] == c]
            chosen.append(rng.choice(ci, min(PER_CLASS, len(ci)), replace=False))
        out[name] = np.concatenate(chosen)
    return out


def confusion(y_true, y_pred, n):
    return np.bincount(y_true * n + y_pred, minlength=n * n).reshape(n, n)


def scores_from_confusion(cm):
    tp = np.diag(cm).astype(float)
    support, predicted = cm.sum(1), cm.sum(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        f1 = np.where(support + predicted > 0, 2 * tp / (support + predicted), 0.0)
        recall = np.where(support > 0, tp / support, np.nan)
    present = support > 0
    return float(f1[present].mean()), float(np.nanmean(recall))


def metrics(y_true, y_pred, classes):
    return scores_from_confusion(confusion(y_true, y_pred, len(classes)))


def bootstrap(y_true, y_pred, blocks, classes, rng, n=1000):
    """Resample test blocks with replacement; per-block confusion matrices make this exact and fast."""
    k = len(classes)
    ub = np.unique(blocks)
    per_block = np.stack([confusion(y_true[blocks == b], y_pred[blocks == b], k) for b in ub])
    f1s, bas = [], []
    for _ in range(n):
        cm = per_block[rng.integers(0, len(ub), len(ub))].sum(0)
        f, b = scores_from_confusion(cm)
        f1s.append(f)
        bas.append(b)
    return [float(np.percentile(f1s, 2.5)), float(np.percentile(f1s, 97.5))], \
           [float(np.percentile(bas, 2.5)), float(np.percentile(bas, 97.5))]


def band_parameters(X, wl):
    def at(w):
        return X[:, int(np.argmin(np.abs(wl - w)))]
    def ibd(lo, hi):
        s = (wl > lo) & (wl < hi)
        r_lo, r_hi = at(lo), at(hi)
        c = r_lo[:, None] + (r_hi - r_lo)[:, None] * (wl[s] - lo) / (hi - lo)
        return (1 - X[:, s] / c).mean(1)
    return np.stack([np.log(at(1580)), ibd(850, 1580), ibd(1580, 2450), at(2400) / at(1000)], 1)


def spectral_features(X):
    return np.hstack([X / X.mean(1, keepdims=True), np.log(X.mean(1, keepdims=True))])


def train_cnn(Xtr, ytr, Xva, yva, n_cls, device):
    import torch
    import torch.nn as nn
    torch.manual_seed(SEED)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    net = nn.Sequential(
        nn.Conv1d(1, 32, 7, padding=3), nn.BatchNorm1d(32), nn.ReLU(), nn.MaxPool1d(2),
        nn.Conv1d(32, 64, 5, padding=2), nn.BatchNorm1d(64), nn.ReLU(), nn.MaxPool1d(2),
        nn.Conv1d(64, 64, 3, padding=1), nn.BatchNorm1d(64), nn.ReLU(), nn.AdaptiveAvgPool1d(4),
        nn.Flatten(), nn.Dropout(0.2), nn.Linear(256, n_cls)).to(device)
    def t(a):
        return torch.tensor((a - mu) / sd, dtype=torch.float32, device=device)[:, None, :]
    xtr, xva = t(Xtr), t(Xva)
    ytr_t = torch.tensor(ytr, device=device)
    opt = torch.optim.AdamW(net.parameters(), 1e-3, weight_decay=1e-4)
    best, best_state, patience = -1, None, 0
    for epoch in range(40):
        net.train()
        perm = torch.randperm(len(xtr), device=device)
        for i in range(0, len(perm), 512):
            j = perm[i:i + 512]
            opt.zero_grad()
            nn.functional.cross_entropy(net(xtr[j]), ytr_t[j]).backward()
            opt.step()
        net.eval()
        with torch.no_grad():
            acc = (net(xva).argmax(1).cpu().numpy() == yva).mean()
        if acc > best:
            best, best_state, patience = acc, {k: v.clone() for k, v in net.state_dict().items()}, 0
        else:
            patience += 1
            if patience >= 5:
                break
    net.load_state_dict(best_state)
    net.eval()
    def predict(X):
        out = []
        with torch.no_grad():
            for i in range(0, len(X), 65536):
                out.append(net(t(X[i:i + 65536])).argmax(1).cpu().numpy())
        return np.concatenate(out)
    return predict, epoch + 1


def train_linear_probe(Etr, ytr, Eva, yva, n_cls, device):
    """Linear probe on frozen embeddings: one linear layer, AdamW, early stop on val."""
    import torch
    import torch.nn as nn
    torch.manual_seed(SEED)
    mu, sd = Etr.mean(0), Etr.std(0) + 1e-6
    def t(a):
        return torch.tensor((a - mu) / sd, dtype=torch.float32, device=device)
    xtr, xva, ytr_t = t(Etr), t(Eva), torch.tensor(ytr, device=device)
    head = nn.Linear(Etr.shape[1], n_cls).to(device)
    opt = torch.optim.AdamW(head.parameters(), 1e-3, weight_decay=1e-4)
    best, best_state, patience = -1, None, 0
    for epoch in range(100):
        perm = torch.randperm(len(xtr), device=device)
        for i in range(0, len(perm), 4096):
            j = perm[i:i + 4096]
            opt.zero_grad()
            nn.functional.cross_entropy(head(xtr[j]), ytr_t[j]).backward()
            opt.step()
        with torch.no_grad():
            acc = (head(xva).argmax(1).cpu().numpy() == yva).mean()
        if acc > best:
            best, best_state, patience = acc, {k: v.clone() for k, v in head.state_dict().items()}, 0
        else:
            patience += 1
            if patience >= 8:
                break
    head.load_state_dict(best_state)
    def predict(E):
        out = []
        with torch.no_grad():
            for i in range(0, len(E), 131072):
                out.append(head(t(E[i:i + 131072])).argmax(1).cpu().numpy())
        return np.concatenate(out)
    return predict, epoch + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="geologic_group_labels.npy")
    ap.add_argument("--methods", default="m3", help="m3, m4, or m3,m4")
    ap.add_argument("--m4-features", default="", help="comma list of name=path.npy embeddings (lines,samples,D)")
    ap.add_argument("--guard", type=int, default=GUARD, help="guard lines at each block edge (leakage control)")
    ap.add_argument("--context", type=int, default=64, help="window (px) for the ctx spatial-context control")
    args = ap.parse_args()
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import NearestCentroid
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    rng = np.random.default_rng(SEED)
    cube, good, wl, labels = load_inputs(args.labels)
    nb, nl, ns = cube.shape
    split_line, block_line = split_lines(nl, args.guard)
    split2d = np.broadcast_to(split_line[:, None], (nl, ns))
    block2d = np.broadcast_to(block_line[:, None], (nl, ns))
    valid = good & (labels >= 0) & (split2d != "none")
    flat = np.where(valid.ravel())[0]
    y_all = labels.ravel()[flat].astype(int)
    split_all = split2d.ravel()[flat]
    block_all = block2d.ravel()[flat]
    test_counts = {int(c): int(np.sum((y_all == c) & (split_all == "test"))) for c in np.unique(y_all)}
    train_counts = {int(c): int(np.sum((y_all == c) & (split_all == "train"))) for c in np.unique(y_all)}
    classes = [c for c in test_counts if test_counts[c] >= MIN_TEST and train_counts.get(c, 0) >= MIN_TEST]
    keep = np.isin(y_all, classes)
    flat, y_all, split_all, block_all = flat[keep], y_all[keep], split_all[keep], block_all[keep]
    remap = {c: i for i, c in enumerate(classes)}
    y = np.array([remap[c] for c in y_all])
    print(f"classes {classes}; train/test counts {train_counts} {test_counts}", flush=True)
    idx = sample_indices(y, split_all, rng)
    X_rows = {}
    for name, ii in idx.items():
        X = cube.reshape(nb, -1)[:, flat[ii]].T.astype(np.float32)
        ok = np.all(np.isfinite(X), 1) & np.all(X > 0, 1)
        idx[name] = ii[ok]
        X_rows[name] = X[ok]
    ytr, yva, yte = y[idx["train"]], y[idx["val"]], y[idx["test"]]
    bte = block_all[idx["test"]]
    cls_ids = list(range(len(classes)))
    results, preds = [], {}

    def record(name, family, pred, seconds, note=""):
        f1, ba = metrics(yte, pred, cls_ids)
        f1_ci, ba_ci = bootstrap(yte, pred, bte, cls_ids, np.random.default_rng(SEED))
        results.append({"method": name, "family": family, "macro_f1": f1, "macro_f1_ci95": f1_ci,
                        "balanced_accuracy": ba, "balanced_accuracy_ci95": ba_ci,
                        "fit_seconds": round(seconds, 1), "note": note})
        preds[name] = pred
        print(results[-1], flush=True)

    if "m3" in args.methods:
        maj = np.bincount(ytr).argmax()
        record("majority class", "M3 reference", np.full(len(yte), maj), 0.0)
        t0 = time.time()
        Ptr, Pte = band_parameters(X_rows["train"], wl), band_parameters(X_rows["test"], wl)
        m = make_pipeline(StandardScaler(), NearestCentroid()).fit(Ptr, ytr)
        record("band parameters + nearest centroid", "M3 physical", m.predict(Pte), time.time() - t0,
               "log albedo 1.58 µm, IBD 1 µm, IBD 2 µm, R2.4/R1.0")
        Ftr, Fte = spectral_features(X_rows["train"]), spectral_features(X_rows["test"])
        t0 = time.time()
        m = make_pipeline(StandardScaler(), PCA(20, random_state=SEED),
                          LogisticRegression(max_iter=500)).fit(Ftr, ytr)
        record("spectra PCA20 + logistic regression", "M3 classical", m.predict(Fte), time.time() - t0)
        t0 = time.time()
        m = RandomForestClassifier(300, min_samples_leaf=5, n_jobs=-1, random_state=SEED).fit(Ftr, ytr)
        record("spectra + random forest", "M3 classical", m.predict(Fte), time.time() - t0)
        import torch
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        t0 = time.time()
        predict, epochs = train_cnn(Ftr, ytr, spectral_features(X_rows["val"]), yva, len(classes), dev)
        record("1D spectral CNN (from scratch)", "M3 learned", predict(Fte), time.time() - t0,
               f"device {dev}; stopped after {epochs} epochs")

    if "ctx" in args.methods:
        # Spatial-context control: the same classical methods on spectra averaged
        # over a context x context window (valid pixels only), matching the
        # 64 x 64 px tile that HyperSIGMA sees, but with no Earth pretraining.
        from scipy.ndimage import uniform_filter
        t0 = time.time()
        w = good.astype(np.float32)
        den = uniform_filter(w, size=args.context, mode="nearest")
        ctx = np.empty((nb, len(flat)), dtype=np.float32)
        for k in range(nb):
            band = np.where(good, np.nan_to_num(np.asarray(cube[k], dtype=np.float32)), 0.0)
            ctx[k] = (uniform_filter(band, size=args.context, mode="nearest") / np.maximum(den, 1e-6)).ravel()[flat]
        C = {name: ctx[:, ii].T for name, ii in idx.items()}
        prep = time.time() - t0
        t0 = time.time()
        Ptr, Pte = band_parameters(C["train"], wl), band_parameters(C["test"], wl)
        m = make_pipeline(StandardScaler(), NearestCentroid()).fit(Ptr, ytr)
        record(f"context {args.context}px band parameters + nearest centroid", "M3 context control",
               m.predict(Pte), time.time() - t0 + prep, "same band parameters on window-mean spectra")
        Ftr, Fte = spectral_features(C["train"]), spectral_features(C["test"])
        t0 = time.time()
        m = make_pipeline(StandardScaler(), PCA(20, random_state=SEED),
                          LogisticRegression(max_iter=500)).fit(Ftr, ytr)
        record(f"context {args.context}px spectra PCA20 + logistic regression", "M3 context control",
               m.predict(Fte), time.time() - t0)
        t0 = time.time()
        m = RandomForestClassifier(300, min_samples_leaf=5, n_jobs=-1, random_state=SEED).fit(Ftr, ytr)
        record(f"context {args.context}px spectra + random forest", "M3 context control",
               m.predict(Fte), time.time() - t0)

    if "m4" in args.methods and args.m4_features:
        for item in args.m4_features.split(","):
            name, path = item.split("=")
            emb = np.load(path, mmap_mode="r")
            D = emb.shape[-1]
            flat_emb = emb.reshape(-1, D)
            Etr = np.asarray(flat_emb[flat[idx["train"]]], dtype=np.float32)
            Eva = np.asarray(flat_emb[flat[idx["val"]]], dtype=np.float32)
            Ete = np.asarray(flat_emb[flat[idx["test"]]], dtype=np.float32)
            import torch
            dev = "cuda" if torch.cuda.is_available() else "cpu"
            t0 = time.time()
            predict, epochs = train_linear_probe(Etr, ytr, Eva, yva, len(classes), dev)
            record(f"{name} frozen + linear probe", "M4 transfer", predict(Ete), time.time() - t0,
                   f"embedding dim {D}; device {dev}; stopped after {epochs} epochs")

    tag = args.methods.replace(",", "_") + ("" if args.guard == GUARD else f"_guard{args.guard}")
    for out_dir in ([OUT] if "m4" in args.methods else [OUT_M3]):
        (out_dir / "metrics").mkdir(parents=True, exist_ok=True)
        meta = {"labels": args.labels, "classes_scored": classes, "test_pixels_by_class": test_counts,
                "train_pixels_by_class": train_counts, "split": {"block_lines": BLOCK, "guard_lines": GUARD,
                "pattern": PATTERN, "min_test_pixels": MIN_TEST, "max_train_per_class": PER_CLASS,
                "contact_buffer_px": BUFFER, "guard_lines_used": args.guard,
                "context_window_px": args.context if "ctx" in args.methods else None},
                "n_train": int(len(ytr)), "n_val": int(len(yva)), "n_test": int(len(yte)),
                "test_blocks": int(len(np.unique(bte))), "results": results}
        (out_dir / f"metrics/e1g2_benchmark_{tag}.json").write_text(json.dumps(meta, indent=2) + "\n")
        with (out_dir / f"metrics/e1g2_benchmark_{tag}.csv").open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["method", "family", "macro_f1", "macro_f1_ci_lo", "macro_f1_ci_hi",
                        "balanced_accuracy", "ba_ci_lo", "ba_ci_hi", "fit_seconds", "note"])
            for r in results:
                w.writerow([r["method"], r["family"], r["macro_f1"], *r["macro_f1_ci95"],
                            r["balanced_accuracy"], *r["balanced_accuracy_ci95"], r["fit_seconds"], r["note"]])
    np.save(DERIVED / f"benchmark_test_predictions_{tag}.npy",
            {"test_flat_index": flat[idx["test"]], "y_true": yte, "classes": classes, "preds": preds},
            allow_pickle=True)


if __name__ == "__main__":
    main()
