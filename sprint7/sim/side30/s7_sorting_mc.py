# sprint7/sim/side30/s7_sorting_mc.py -- landed 2026-09-26 (PM). Driver pairing / trims MC on the single-table route, 2 kHz band only, frequency-flat errors, noise-free jig. [L2 on L4 spread]. Seed 2026. NOTE (critic R2 MAJOR-2): single-band, flat-error optimistic; joint-yield & freq-dependent results are in sprint7/critic/CRITIC_H_SIDE30_R2_20260926.md.
# [L2 exploratory] What does driver SORTING/PAIRING buy, on the single-table route (implementable today)?
# Model: far-field isotropic, freq-flat per-driver complex errors, 2 kHz 1/3-oct band, worse of +/-90 deg.
import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "acoustic"))
import s7_common as S
from scipy.signal.windows import chebwin
S.assert_anchors(verbose=False)
RNG = np.random.default_rng(2026)
FS = np.geomspace(2000 * 2 ** (-1 / 6), 2000 * 2 ** (1 / 6), 41)
ST = np.sin(np.deg2rad([0.0, 90.0, -90.0]))
def att(w16, e16, dx16):
    ww = w16 * e16; x = S.X + dx16; p = np.zeros(3)
    for f in FS:
        p += np.abs((ww[None, :] * np.exp(1j * 2 * np.pi * f / S.C * np.outer(ST, x))).sum(1)) ** 2
    return 10 * np.log10(p[0] / max(p[1], p[2]))
def draw(n, conv):
    if conv == "uniform":   # project convention +/-1 dB, +/-5 deg, +/-0.5 mm
        return (10 ** (RNG.uniform(-1, 1, n) / 20) * np.exp(1j * np.deg2rad(RNG.uniform(-5, 5, n))),
                RNG.uniform(-5e-4, 5e-4, n))
    return (10 ** (RNG.normal(0, 1, n) / 20) * np.exp(1j * np.deg2rad(RNG.normal(0, 5, n))), np.zeros(n))
def greedy_pairs(e):
    idx = list(range(len(e))); pairs = []
    while idx:
        best = None
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                d = abs(e[idx[a]] - e[idx[b]])
                if best is None or d < best[0]: best = (d, idx[a], idx[b])
        pairs.append(best); idx.remove(best[1]); idx.remove(best[2])
    return pairs                                   # sorted: best-matched first
def build(w8, e, dx, mode, cal):
    """mode: 'random' | 'pair16' | 'pair24' ; cal: None | 'amp' | 'cplx'. Returns e16, dx16 in element order."""
    if mode == "pair24":                           # buy 24, keep the 16 closest to the batch median
        med = np.median(e.real) + 1j * np.median(e.imag)
        keep = np.argsort(np.abs(e - med))[:16]; e, dx = e[keep], dx[keep]
    if mode == "random":
        pairs = [(0.0, c, 15 - c) for c in range(8)]; order = list(range(8))
    else:
        pairs = greedy_pairs(e)                     # best-matched pair -> highest weight position
        order = list(np.argsort(-w8))
    e16 = np.empty(16, complex); d16 = np.empty(16)
    for rank, (_, i, j) in enumerate(pairs):
        c = order[rank] if mode != "random" else rank
        g = 1.0
        m = (e[i] + e[j]) / 2
        if cal == "amp": g = 1 / abs(m)
        elif cal == "cplx": g = 1 / m
        e16[c], e16[15 - c] = e[i] * g, e[j] * g
        d16[c], d16[15 - c] = dx[i], dx[j]
    return e16, d16
W = {"D20": S.read_w8()[0], "D35": S.w_norm(chebwin(16, 35))[:8]}
M = 800
print("2 kHz band, worse of +/-90 deg: median / P10 / yield(>=30 dB)")
for conv in ("uniform", "gauss"):
    print(f"--- tolerance: {'project convention +/-1dB +/-5deg +/-0.5mm (uniform)' if conv=='uniform' else 'Gaussian sigma 1 dB / 5 deg'}")
    for wn in ("D20", "D35"):
        w8 = W[wn]; w16 = S.expand16(w8)
        for mode, cal, label in (("random", None, "as-built, no cal"),
                                 ("random", "amp", "as-built + per-ch gain trim (0 cyc)"),
                                 ("pair16", "amp", "measure 16 + pair-match + gain trim"),
                                 ("pair24", "amp", "buy 24, keep 16 + pair + gain trim"),
                                 ("pair16", "cplx", "measure 16 + pair + complex trim (needs FIR)")):
            v = np.empty(M)
            for k in range(M):
                n = 24 if mode == "pair24" else 16
                e, dx = draw(n, conv)
                e16, d16 = build(w8, e, dx, mode, cal)
                v[k] = att(w16, e16, d16)
            print(f"  {wn}  {label:44s} {np.median(v):5.1f} / {np.percentile(v,10):5.1f} / {np.mean(v>=30)*100:4.0f}%")
