# sprint7/sim/side30/s7_single_table.py -- landed 2026-09-26 (PM). Single frequency-independent table (input-scale weights): ideal far-field metrics + MC (uniform +/-1dB/+/-5deg/+/-0.5mm and Gaussian sigma 1dB/5deg). [L2 on L4 spread]. Seed 99.
# [L2 exploratory] single frequency-independent table (implementable today: input-scale weights, 0 cycles)
import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "acoustic"))
import s7_common as S
from scipy.signal.windows import chebwin
S.assert_anchors(verbose=False)
RNG = np.random.default_rng(99)
W = {"D20(now)": S.expand16(S.read_w8()[0])}
for sll in (25, 30, 35):
    W[f"D{sll}"] = S.w_norm(chebwin(16, sll))
A_WT = {630: -1.9, 800: -0.8, 1000: 0.0, 1250: 0.6, 1600: 1.0, 2000: 1.2, 2500: 1.3, 3150: 1.2, 4000: 1.0, 5000: 0.5, 6300: -0.1}
def bp(th, fc, w, e=None, dx=None):
    fs = np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 41)
    x = S.X if dx is None else S.X + dx
    ww = w if e is None else w * e
    st = np.sin(np.deg2rad(np.asarray(th, float)))
    return np.mean([np.abs((ww[None, :] * np.exp(1j * 2 * np.pi * f / S.C * np.outer(st, x))).sum(1)) ** 2 for f in fs], axis=0)
def att90w(fc, w, e=None, dx=None):
    p = bp([0.0, 90.0, -90.0], fc, w, e, dx); return 10 * np.log10(p[0] / max(p[1], p[2]))
def broadband(w, bands):
    p0 = p9 = 0.0
    for fc in bands:
        g = 10 ** (A_WT[fc] / 10); p = bp([0.0, 90.0], fc, w); p0 += g * p[0]; p9 += g * p[1]
    return 10 * np.log10(p0 / p9)
print("IDEAL single table: band att90 (worse side) | BW@1k | att30@1k | 500Hz/30 | on-axis vs D20 | WNGn")
for k, w in W.items():
    a = " ".join(f"{fc}:{att90w(fc, w):4.1f}" for fc in (630, 800, 1000, 2000, 4000, 5000))
    print(f"  {k:9s} {a} | BW1k {S.bw_full(S.pattern_db(1000, w)):.1f} | a30@1k {S.att_db(30, 1000, w):.1f} | 500/30 {S.att_db(30, 500, w):.1f}"
          f" | ax {20*np.log10(w.sum()/W['D20(now)'].sum()):+.2f} | WNGn {S.wng_norm_db(w):+.2f}")
    print(f"            broadband A-wt 630-5k: {broadband(w, [630,800,1000,1250,1600,2000,2500,3150,4000,5000]):.1f} dB ;"
          f" 630-6.3k: {broadband(w, [630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300]):.1f} dB")
def mc(w, fc, mode, M=1500):
    v = np.empty(M)
    for i in range(M):
        if mode == "uniform":      # project convention: +/-1 dB, +/-5 deg, +/-0.5 mm (uniform half-widths)
            e = 10 ** (RNG.uniform(-1, 1, 16) / 20) * np.exp(1j * np.deg2rad(RNG.uniform(-5, 5, 16)))
            dx = RNG.uniform(-0.0005, 0.0005, 16)
        else:                      # Gaussian sigma 1 dB / 5 deg (what I used before)
            e = 10 ** (RNG.normal(0, 1, 16) / 20) * np.exp(1j * np.deg2rad(RNG.normal(0, 5, 16))); dx = None
        v[i] = att90w(fc, w, e, dx)
    return np.median(v), np.percentile(v, 10), np.mean(v >= 30) * 100
print("\nMC (worse of +/-90 deg, band-avg): median / P10 / yield(>=30 dB, %) ; no calibration")
for k in ("D20(now)", "D30", "D35"):
    for mode in ("uniform", "gauss"):
        cells = []
        for fc in (1000, 2000, 4000):
            m, p, y = mc(W[k], fc, mode); cells.append(f"{fc}: {m:4.1f}/{p:4.1f}/{y:3.0f}%")
        print(f"  {k:9s} {mode:7s} " + "   ".join(cells))
