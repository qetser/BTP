#!/usr/bin/env python3
"""M4 Earth-to-Moon transfer: frozen per-pixel features from HyperFree and HyperSIGMA.

Exact command (run from the repository root; the environment is created by uv):

  /home/anirudhs/.local/bin/uv run --no-project --python 3.11 \
      --with torch==2.5.1 --with torchvision==0.20.1 --with timm==1.0.11 \
      --with einops==0.8.0 --with numpy==1.26.4 \
      python -I scripts/m4_foundation_features.py --selftest

Library use (same environment):
  from m4_foundation_features import extract_features
  emb = extract_features("hyperfree", cube, wavelengths_nm)   # (H, W, 768)

Inputs: `cube` is float32 (H, W, B) reflectance, `wavelengths_nm` holds B band
centres in nm. Output: float32 (H, W, D) per-pixel embeddings. Pixels whose
input spectrum is all NaN get NaN embeddings; other NaNs are set to 0.

Code and weights (untrusted downloads, inspected before use) live under
data/models/ (git-ignored):
  hyperfree_repo   github.com/Jingtao-Li-CVer/HyperFree @ 966f3e3c7deb0fbcff54874924174faaabdf182a
  hypersigma_repo  github.com/WHU-Sigma/HyperSIGMA     @ 07e9ea24e3072fcb5c3a92a2bcb8185e43b295b9
  hyperfree_ckpt/HyperFree-b.pth                       (HF JingtaoLi/HyperFree)
  hypersigma_ckpt/spat-vit-base-ultra-checkpoint-1599.pth, spec-vit-base-... (HF WHU-Sigma/HyperSIGMA)
Checkpoints are loaded with torch.load(weights_only=True). The HyperSIGMA files
also contain an argparse.Namespace, which is the only extra allowlisted type.

Models
------
"hyperfree"  HyperFree ViT-b encoder, tuning-free configuration used in the
  authors' demos (image 1024, patch 16, global attention blocks 2/5/8/11, no
  patch merging). Native wavelength adapter: the band centres are passed to
  the encoder, which builds its patch-embedding layer from two learned weight
  dictionaries (85 key wavelengths, and a 400-2500 nm grid with 10 nm steps).
  Each dictionary entry takes the first input band within 10 nm. Each tile
  (default 256 px) is resized so its long side is 1024 (bilinear,
  antialiased), divided by its own maximum (model.preprocess), and encoded
  with GSD = gsd_m / resize_ratio. Default feature: stage 1 (output of block
  5, 768-d, 64x64 tokens per tile), which the authors' classification demo
  uses. hyperfree_stage=4 gives the 256-d neck output. Tokens are
  bilinearly upsampled to pixels.
"hypersigma"  HyperSIGMA spatial MAE ViT-B encoder (pretrained input:
  100 channels, 64x64 px, patch 8). Wavelength adapter: the spectrum is
  linearly interpolated (np.interp per pixel) onto 100 equally spaced
  wavelengths that span the overlap of the input range with 400-2500 nm. For
  IIRS 845-2460 nm this gives 100 bands from 845 to 2460 nm in 16.31 nm
  steps. The model has no wavelength input. In pretraining, each sample was a
  random window of 100 contiguous native channels (about 10 nm steps) from
  EO-1 Hyperion radiance or GF-5 DN (0.4-1.0 um). Values are multiplied by
  hypersigma_scale (default 1.0, reflectance used as is). Pretraining used
  DN or radiance / 4000, so no exact equivalent exists. 64x64 tiles
  (reflect-padded at the edges) -> patch_embed -> 12 blocks -> norm. No
  position embedding is added: the released pretraining encoder does not use
  one, and the checkpoint pos_embed still has its initial std of 0.0200.
  Output: 768-d, 8x8 tokens per tile, bilinearly upsampled to pixels.
"hypersigma_spec"  HyperSIGMA spectral MAE ViT-B encoder applied to the
  same 100-band, 64x64 tiles (band image -> Linear(4096, 768) token, 100
  tokens). The mean over tokens gives one 768-d vector per tile, which is
  copied to every pixel of that tile. This output is tile-level, not
  pixel-level.

No result from this script is a lunar performance claim.
"""
from __future__ import annotations

import argparse
import math
import sys
import time
import types
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = REPO_ROOT / "data" / "models"
HYPERFREE_REPO = MODEL_DIR / "hyperfree_repo"
HYPERSIGMA_PRETRAIN = MODEL_DIR / "hypersigma_repo" / "Pretrain"
HYPERFREE_CKPT = MODEL_DIR / "hyperfree_ckpt" / "HyperFree-b.pth"
HYPERSIGMA_SPAT_CKPT = MODEL_DIR / "hypersigma_ckpt" / "spat-vit-base-ultra-checkpoint-1599.pth"
HYPERSIGMA_SPEC_CKPT = MODEL_DIR / "hypersigma_ckpt" / "spec-vit-base-ultra-checkpoint-1599.pth"

HYPERSIGMA_BANDS = 100
HYPERSIGMA_TILE = 64
HYPERSIGMA_RANGE_NM = (400.0, 2500.0)

_CACHE: dict = {}


def pick_device(min_free_gb: float = 4.0) -> torch.device:
    if torch.cuda.is_available():
        free, _total = torch.cuda.mem_get_info()
        if free / 1e9 >= min_free_gb:
            return torch.device("cuda")
        print(f"[m4] GPU has only {free / 1e9:.1f} GB free; using CPU", file=sys.stderr)
    return torch.device("cpu")


def _stub_module(name: str, **attrs) -> None:
    """Insert a minimal module so unused optional imports in the repos succeed."""
    if name in sys.modules:
        return
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod


# --------------------------------------------------------------------------- HyperFree
def _load_hyperfree(device: torch.device):
    key = ("hyperfree", str(device))
    if key in _CACHE:
        return _CACHE[key]
    # GDAL is only used by HyperFree's file readers, which this wrapper does not call.
    _stub_module("osgeo", gdal=None)
    sys.path.insert(0, str(HYPERFREE_REPO))
    from HyperFree import HyperFree_model_registry  # noqa: E402
    from HyperFree.utils.transforms import ResizeLongestSide  # noqa: E402

    model = HyperFree_model_registry["vit_b"](checkpoint=None, encoder_global_attn_indexes=-1, merge_indexs=None)
    state = torch.load(HYPERFREE_CKPT, map_location="cpu", weights_only=True)
    missing, unexpected = model.load_state_dict(state, strict=False)
    # contras_modules are only used by convert_semantic_feature, which the encoder
    # forward never calls; the released checkpoint does not contain them.
    enc_missing = [k for k in missing
                   if k.startswith("image_encoder.") and not k.startswith("image_encoder.contras_modules.")]
    if enc_missing:
        raise RuntimeError(f"HyperFree encoder weights missing: {enc_missing[:5]}")
    model = model.to(device).eval()
    info = {"unexpected_keys": list(unexpected), "missing_keys": list(missing)}
    _CACHE[key] = (model, ResizeLongestSide(model.image_encoder.img_size), info)
    return _CACHE[key]


@torch.no_grad()
def _hyperfree_features(cube, wavelengths_nm, device, tile=256, gsd_m=80.0, hyperfree_stage=1):
    model, transform, _info = _load_hyperfree(device)
    enc = model.image_encoder
    H, W, B = cube.shape
    wl = [float(w) for w in wavelengths_nm]
    out = None
    for y0 in range(0, H, tile):
        for x0 in range(0, W, tile):
            sub = cube[y0:y0 + tile, x0:x0 + tile]
            h, w = sub.shape[:2]
            x = torch.from_numpy(np.ascontiguousarray(sub.transpose(2, 0, 1)))[None].float().to(device)
            xr = transform.apply_image_torch(x)  # long side -> 1024
            ratio = enc.img_size / max(h, w)
            xr = model.preprocess(xr)  # x / x.max(), pad to 1024 x 1024
            gsd = torch.tensor([gsd_m / ratio])
            feats = enc(xr, True, wl, gsd)[hyperfree_stage]  # (1, D, 64, 64)
            n_tok = feats.shape[-1]
            vh = max(1, round(h * ratio / enc.img_size * n_tok))
            vw = max(1, round(w * ratio / enc.img_size * n_tok))
            f = F.interpolate(feats[:, :, :vh, :vw], size=(h, w), mode="bilinear", align_corners=False)
            f = f[0].permute(1, 2, 0).float().cpu().numpy()
            if out is None:
                out = np.empty((H, W, f.shape[-1]), dtype=np.float32)
            out[y0:y0 + h, x0:x0 + w] = f
    return out


def hyperfree_band_matching(wavelengths_nm):
    """Report how the HyperFree dictionaries match the given band centres."""
    _stub_module("osgeo", gdal=None)
    if str(HYPERFREE_REPO) not in sys.path:
        sys.path.insert(0, str(HYPERFREE_REPO))
    from HyperFree.utils import spectral_process_utils as spu  # noqa: E402

    wl = [float(w) for w in wavelengths_nm]
    key_data, _, key_bank = spu.find_corresponding_indices(wl, spu.spectral_wavelength, 10)
    blk_data, _, blk_bank = spu.find_corresponding_indices(wl, spu.weight_bank_wavelength, 10)
    blk_kept = [i for i, d in enumerate(blk_data) if d not in set(key_data)]
    return {
        "key_dictionary_size": len(spu.spectral_wavelength),
        "key_entries_matched": len(key_bank),
        "key_wavelengths_matched_nm": [spu.spectral_wavelength[i] for i in key_bank],
        "grid_dictionary_size": len(spu.weight_bank_wavelength),
        "grid_entries_matched": len(blk_bank),
        "grid_entries_used_after_removing_key_bands": len(blk_kept),
        "input_bands_used": len(set(key_data) | {blk_data[i] for i in blk_kept}),
    }


# --------------------------------------------------------------------------- HyperSIGMA
def _load_hypersigma(device: torch.device):
    key = ("hypersigma", str(device))
    if key in _CACHE:
        return _CACHE[key]
    import argparse as _ap

    # mmengine is imported only for get_dist_info, which the encoders never call.
    _stub_module("mmengine")
    _stub_module("mmengine.dist", get_dist_info=lambda: (0, 1))
    sys.path.insert(0, str(HYPERSIGMA_PRETRAIN))
    import models_mae_Spat  # noqa: E402
    import models_mae_Spec  # noqa: E402

    torch.serialization.add_safe_globals([_ap.Namespace])
    args = _ap.Namespace(image_size=HYPERSIGMA_TILE, use_ckpt="False", num_tokens=HYPERSIGMA_BANDS)
    spat = models_mae_Spat.spat_mae_b(args, inchannels=HYPERSIGMA_BANDS)
    spec = models_mae_Spec.spec_mae_b(args, inchannels=HYPERSIGMA_BANDS)
    info = {}
    for name, net, path in (("spat", spat, HYPERSIGMA_SPAT_CKPT), ("spec", spec, HYPERSIGMA_SPEC_CKPT)):
        sd = torch.load(path, map_location="cpu", weights_only=True)["model"]
        res = net.load_state_dict(sd, strict=False)
        enc_missing = [k for k in res.missing_keys if not k.startswith("decoder") and k != "mask_token"]
        if enc_missing:
            raise RuntimeError(f"HyperSIGMA {name} encoder weights missing: {enc_missing[:5]}")
        info[name] = {"missing_keys": list(res.missing_keys), "unexpected_keys": list(res.unexpected_keys)}
        net.to(device).eval()
    _CACHE[key] = (spat, spec, info)
    return _CACHE[key]


def hypersigma_target_wavelengths(wavelengths_nm, n_bands=HYPERSIGMA_BANDS):
    wl = np.asarray(wavelengths_nm, dtype=np.float64)
    lo = max(float(wl.min()), HYPERSIGMA_RANGE_NM[0])
    hi = min(float(wl.max()), HYPERSIGMA_RANGE_NM[1])
    if hi <= lo:
        raise ValueError("input wavelengths do not overlap 400-2500 nm")
    return np.linspace(lo, hi, n_bands)


def resample_linear(cube, wavelengths_nm, target_nm):
    """Linear interpolation along the band axis (same result as np.interp per pixel)."""
    wl = np.asarray(wavelengths_nm, dtype=np.float64)
    order = np.argsort(wl)
    wl = wl[order]
    c = cube[..., order]
    idx = np.clip(np.searchsorted(wl, target_nm, side="right") - 1, 0, len(wl) - 2)
    t = ((target_nm - wl[idx]) / (wl[idx + 1] - wl[idx])).astype(np.float32)
    return c[..., idx] * (1.0 - t) + c[..., idx + 1] * t


def _tiles64(cube):
    H, W, C = cube.shape
    T = HYPERSIGMA_TILE
    Hp, Wp = math.ceil(H / T) * T, math.ceil(W / T) * T
    padded = np.pad(cube, ((0, Hp - H), (0, Wp - W), (0, 0)), mode="reflect" if min(H, W) > 1 else "edge")
    tiles = padded.reshape(Hp // T, T, Wp // T, T, C).transpose(0, 2, 4, 1, 3)  # ny, nx, C, T, T
    return tiles.reshape(-1, C, T, T), Hp // T, Wp // T


@torch.no_grad()
def _hypersigma_features(cube, wavelengths_nm, device, branch="spat", hypersigma_scale=1.0, batch=64):
    spat, spec, _info = _load_hypersigma(device)
    H, W, _ = cube.shape
    target = hypersigma_target_wavelengths(wavelengths_nm)
    x100 = resample_linear(cube, wavelengths_nm, target) * np.float32(hypersigma_scale)
    tiles, ny, nx = _tiles64(x100)
    T = HYPERSIGMA_TILE
    outs = []
    for i in range(0, len(tiles), batch):
        x = torch.from_numpy(np.ascontiguousarray(tiles[i:i + batch])).float().to(device)
        if branch == "spat":
            tok, (hp, wp) = spat.patch_embed(x)  # no pos_embed: unused in pretraining
            for blk in spat.blocks:
                tok = blk(tok, hp, wp)
            tok = spat.norm(tok)  # (b, 64, 768)
            fmap = tok.transpose(1, 2).reshape(x.shape[0], -1, hp, wp)
            fmap = F.interpolate(fmap, size=(T, T), mode="bilinear", align_corners=False)
        else:
            b = x.shape[0]
            tok = spec.patch_embed(x)  # (b, T*T, 100)
            tok = spec.spec_embed(tok).transpose(1, 2)  # (b, 100 tokens, T*T)
            tok = spec.spat_map(tok)  # (b, 100, 768)
            for blk in spec.blocks:
                tok = blk(tok, T, T)
            vec = spec.norm(tok).mean(dim=1)  # (b, 768)
            fmap = vec[:, :, None, None].expand(b, vec.shape[1], T, T)
        outs.append(fmap.float().cpu().numpy())
    f = np.concatenate(outs, 0)  # (ny*nx, D, T, T)
    D = f.shape[1]
    f = f.reshape(ny, nx, D, T, T).transpose(0, 3, 1, 4, 2).reshape(ny * T, nx * T, D)
    return np.ascontiguousarray(f[:H, :W]).astype(np.float32)


# --------------------------------------------------------------------------- public API
def extract_features(model_name, cube, wavelengths_nm, device=None, **opts) -> np.ndarray:
    """Return per-pixel embeddings (H, W, D) for a float32 (H, W, B) reflectance cube.

    model_name: "hyperfree" (D=768 by default, 256 with hyperfree_stage=4),
    "hypersigma" (D=768, spatial encoder), or "hypersigma_spec" (D=768, tile-level).
    Options: hyperfree: tile=256, gsd_m=80.0, hyperfree_stage=1;
             hypersigma*: hypersigma_scale=1.0, batch=64.
    """
    cube = np.asarray(cube, dtype=np.float32)
    if cube.ndim != 3 or cube.shape[2] != len(wavelengths_nm):
        raise ValueError("cube must be (H, W, B) with B == len(wavelengths_nm)")
    device = torch.device(device) if device is not None else pick_device()
    all_nan = np.all(~np.isfinite(cube), axis=2)
    cube = np.nan_to_num(cube, nan=0.0, posinf=0.0, neginf=0.0)
    if model_name == "hyperfree":
        out = _hyperfree_features(cube, wavelengths_nm, device, **opts)
    elif model_name == "hypersigma":
        out = _hypersigma_features(cube, wavelengths_nm, device, branch="spat", **opts)
    elif model_name == "hypersigma_spec":
        out = _hypersigma_features(cube, wavelengths_nm, device, branch="spec", **opts)
    else:
        raise ValueError(f"unknown model {model_name!r}")
    out[all_nan] = np.nan
    return out


def _count_params(module) -> int:
    return int(sum(p.numel() for p in module.parameters()))


def selftest(device=None, repeats=3):
    device = torch.device(device) if device is not None else pick_device()
    print(f"torch {torch.__version__}  cuda_available={torch.cuda.is_available()}  device={device}")
    if device.type == "cuda":
        free, total = torch.cuda.mem_get_info()
        print(f"GPU: {torch.cuda.get_device_name(0)}  free {free / 1e9:.1f} / {total / 1e9:.1f} GB")
    rng = np.random.default_rng(0)
    cube = rng.uniform(0.05, 0.35, size=(64, 64, 110)).astype(np.float32)
    wl = np.linspace(845.0, 2460.0, 110)
    print("HyperFree band matching for 845-2460 nm, 110 bands:", hyperfree_band_matching(wl))
    t = hypersigma_target_wavelengths(wl)
    print(f"HyperSIGMA target grid: {t[0]:.1f}-{t[-1]:.1f} nm, {len(t)} bands, step {t[1] - t[0]:.2f} nm")
    results = {}
    for name in ("hyperfree", "hypersigma", "hypersigma_spec"):
        t0 = time.perf_counter()
        out = extract_features(name, cube, wl, device=device)
        if device.type == "cuda":
            torch.cuda.synchronize()
        first = time.perf_counter() - t0
        times = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            out = extract_features(name, cube, wl, device=device)
            if device.type == "cuda":
                torch.cuda.synchronize()
            times.append(time.perf_counter() - t0)
        peak = torch.cuda.max_memory_allocated() / 1e9 if device.type == "cuda" else float("nan")
        ok = bool(np.isfinite(out).all())
        results[name] = {"shape": list(out.shape), "first_call_s_incl_load": round(first, 3),
                         "warm_call_s_median": round(float(np.median(times)), 4), "finite": ok,
                         "peak_gpu_mem_gb": round(peak, 2)}
        print(f"{name:16s} out {out.shape} dtype {out.dtype} finite={ok} "
              f"first(incl. load)={first:.2f}s warm median={np.median(times):.3f}s peak_gpu={peak:.2f}GB")
    m, _, hf_info = _load_hyperfree(device)
    spat, spec, hs_info = _load_hypersigma(device)
    print("params: HyperFree-b full", _count_params(m), "image_encoder", _count_params(m.image_encoder))
    enc = lambda net: sum(_count_params(getattr(net, n)) for n in ("patch_embed", "spat_map", "blocks", "norm")
                          if hasattr(net, n))
    print("params: HyperSIGMA spat MAE enc+dec", _count_params(spat), "encoder", enc(spat),
          "| spec MAE enc+dec", _count_params(spec), "encoder", enc(spec))
    print("HyperFree unexpected ckpt keys:", hf_info["unexpected_keys"][:8], len(hf_info["unexpected_keys"]),
          "| missing:", sorted({k.split(".")[1] for k in hf_info["missing_keys"]}))
    print("HyperSIGMA load info:", {k: {kk: len(vv) for kk, vv in v.items()} for k, v in hs_info.items()})
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true", help="run all models on a random 64x64x110 cube")
    ap.add_argument("--device", default=None, help="cuda or cpu (default: cuda if enough free memory)")
    ap.add_argument("--json", default=None, help="optional path to write selftest results as JSON")
    a = ap.parse_args()
    if not a.selftest:
        ap.print_help()
        return
    res = selftest(a.device)
    if a.json:
        import json
        Path(a.json).write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
