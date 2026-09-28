#!/usr/bin/env python3
"""critic R3g -- (A) independent re-derivation of the band gains (own null-space solver, own sector covariance,
own closed-form sigma_g^2, own bisection for the post-hoc cap) vs the stored CSV gains; X3 as a control of the
solver. (B) own U-flat as-built Monte Carlo (own RNG / error draws / pattern code), paired across designs.
Imports nothing from the PM's modules."""
import csv
import os
import sys
import numpy as np

sys.argv = ["x"]
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "r3g_bank_headroom.py")).read().split("# ---------------- (1) bank")[0])

C, NEL, DSP = 343.0, 16, 0.055
X16 = (np.arange(NEL) - 7.5) * DSP
XC = X16[:8]
B7 = (1000, 1250, 1600, 2000, 2500, 3150, 4000)


def bfreqs(fc, n=31):
    return np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), n)


F7 = np.concatenate([bfreqs(fc) for fc in B7])
F75 = np.concatenate([F7, bfreqs(5000.0)])
b, p0 = np.log(10.0) / 10.0, np.deg2rad(5.0)
SIG2G = np.sinh(b) / b - 2 * (np.sinh(b / 2) / (b / 2)) * (np.sin(p0) / p0) + 1
SIGX2 = (0.5e-3) ** 2 / 3


def seccov(t0, t1, f):
    th = np.deg2rad(np.arange(t0, t1 + 1e-9, 0.25))
    k = 2 * np.pi * f / C
    a = 2 * np.cos(k * np.outer(np.sin(th), XC))
    return a.T @ a / len(th)


QC = {}


def Q(f):
    if f not in QC:
        k = 2 * np.pi * f / C
        QC[f] = seccov(60, 90, f) + 0.1 * seccov(35, 60, f) + 2 * (SIG2G + k * k * SIGX2) * np.eye(8)
    return QC[f]


D20N = W8 / (2 * W8.sum())


def solve(mag, fgrid, load_top=0.0):
    """mag(f) -> (K,) band amplitudes; band 1 fixed D20N; bands 2..K: sum 2w = 1. Null-space param."""
    K = len(mag(fgrid[0]))
    nf = K - 1
    # basis of {v in R^8: sum v = 0}
    Nb = np.linalg.qr(np.vstack([np.ones(8), np.eye(8)[:7]]).T)[0][:, 1:]
    x0 = np.tile(np.full(8, 1 / 16), nf)
    NN = np.kron(np.eye(nf), Nb)                      # (8nf, 7nf)
    Hm = np.zeros((8 * nf, 8 * nf))
    gm = np.zeros(8 * nf)
    for f in fgrid:
        m = mag(f)
        q = Q(float(f))
        Hm += np.kron(np.outer(m[1:], m[1:]), q)
        gm += np.kron(m[1:], q @ (m[0] * D20N))
    Hm /= len(fgrid)
    gm /= len(fgrid)
    if load_top:
        Hm[-8:, -8:] += load_top * np.eye(8)
    z = -np.linalg.solve(NN.T @ Hm @ NN, NN.T @ (Hm @ x0 + gm))
    return np.vstack([D20N, (x0 + NN @ z).reshape(nf, 8)])


def lpx_mag(name):
    Bk = bank_of(name)
    return lambda f: np.array([zamp(bb, f, Bk["D"]).real[0] for bb in Bk["bands"]])


def x3_mag(f):
    a1, a2 = lr4_lp(f, 700.0), lr4_lp(f, 1600.0)
    return np.array([a1 * a2, (1 - a1) * a2, 1 - a2])


log("(A) BAND GAINS re-derived (own null-space KKT) vs stored")
wx = solve(x3_mag, F7)
log(f"  control X3-LR4-700/1600-e0.1m35 vs s7_alt_algos_params.csv: max rel |diff| {np.abs(wx - x3_gains()).max() / np.abs(x3_gains()).max():.2e}")
for name, fg in [("LPX3-a", F7), ("LPX3-b", F7), ("LPX4-a", F75), ("LPX4-b", F75)]:
    w = solve(lpx_mag(name), fg)
    log(f"  {name}: max rel |diff| vs CSV {np.abs(w - bank_of(name)['wk']).max() / np.abs(w).max():.2e}")
for name, base, fg in [("LPX4-a-cap", "LPX4-a", F75), ("LPX4-b-cap", "LPX4-b", F75)]:
    mg = lpx_mag(base)
    lo, hi = 0.0, 1e-2
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        w = solve(mg, fg, mid)
        lo, hi = (mid, hi) if w[-1].max() > w[1].max() else (lo, mid)
    w = solve(mg, fg, hi)
    log(f"  {name}: own bisection rho {hi:.4e} (PM log 4.680e-03 / 4.557e-03); top max {w[-1].max():.5f} band-2 max {w[1].max():.5f};"
        f" max rel |diff| vs CSV {np.abs(w - bank_of(name)['wk']).max() / np.abs(w).max():.2e}")
    # is the cap the ONLY change? band 1 identical, bank identical to base
    same_bank = all(np.array_equal(a, bb) for a, bb in zip(bank_of(name)["lps"], bank_of(base)["lps"]))
    log(f"     bank taps identical to {base}: {same_bank}")

# ---------------- (B) own MC ----------------
log("\n(B) OWN MC, U-flat as-built (a~U(+-1 dB), phi~U(+-5 deg) flat per element; dx~U(+-0.5 mm)), paired draws, joint7 = all 7 bands >= 30 dB")
fb = np.concatenate([bfreqs(fc) for fc in B7])
kk = 2 * np.pi * fb / C


def resp_taps(h8, f):
    n = np.arange(h8.shape[1])
    E = np.exp(-1j * 2 * np.pi * np.outer(f, n) / FS)
    return E @ h8.T                                   # (F, 8) complex (common linear phase irrelevant)


designs = {"D20": np.tile(D20N, (len(fb), 1)).astype(complex),
           "X3": (np.stack([x3_mag(f) for f in fb]) @ x3_gains()).astype(complex)}
for name in ["LPX3-a", "LPX3-b", "LPX4-b-cap"]:
    Bk = bank_of(name)
    designs[name] = resp_taps(Bk["wk"].T @ Bk["bands"], fb)
designs["FIR V1-128"] = resp_taps(fir_v1(), fb)


def mc(M, seed):
    rng = np.random.default_rng(seed)
    res = {k: np.empty((M, 7)) for k in designs}
    ch = 500
    for t0 in range(0, M, ch):
        m = min(ch, M - t0)
        a = rng.uniform(-1, 1, (m, NEL))
        ph = rng.uniform(-5, 5, (m, NEL))
        dx = rng.uniform(-5e-4, 5e-4, (m, NEL))
        g = 10 ** (a / 20) * np.exp(1j * np.deg2rad(ph))                 # (m,16)
        xs = X16[None, :] + dx                                          # (m,16)
        st = np.array([0.0, 1.0, -1.0])
        E = np.exp(1j * kk[None, :, None, None] * st[None, None, :, None] * xs[:, None, None, :])   # (m,F,3,16)
        for name, W in designs.items():
            w16 = np.concatenate([W, W[:, ::-1]], axis=1)                  # (F,16)
            amp = np.einsum("fn,mn,mfan->mfa", w16, g, E)
            Pw = np.abs(amp) ** 2
            for bi in range(7):
                Pb = Pw[:, bi * 31:(bi + 1) * 31, :].sum(1)
                res[name][t0:t0 + m, bi] = 10 * np.log10(Pb[:, 0] / np.maximum(Pb[:, 1], Pb[:, 2]))
    return res


M = 6000
res = mc(M, 29092026)
j7 = {k: np.all(v >= 30, axis=1) for k, v in res.items()}
for k in designs:
    p = j7[k].mean()
    log(f"  {k:11s} joint7 {100 * p:5.1f}% (1 sigma {100 * np.sqrt(p * (1 - p) / M):.1f} pp) | median R90 per band "
        + " ".join(f"{np.median(res[k][:, i]):5.1f}" for i in range(7)))
for a_, b_ in [("LPX3-b", "X3"), ("LPX3-a", "X3"), ("LPX3-b", "FIR V1-128"), ("X3", "FIR V1-128"), ("LPX4-b-cap", "FIR V1-128"), ("LPX4-b-cap", "LPX3-b")]:
    n10 = int(np.sum(j7[a_] & ~j7[b_]))
    n01 = int(np.sum(~j7[a_] & j7[b_]))
    chi = (abs(n10 - n01) - 1) ** 2 / max(n10 + n01, 1)
    log(f"  paired {a_} - {b_}: {100 * (j7[a_].mean() - j7[b_].mean()):+5.2f} pp  (discordant {n10}/{n01}, McNemar chi2 {chi:.2f})")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "r3g_kkt_mc.log"), "w") as fp:
    fp.write("\n".join(out) + "\n")
