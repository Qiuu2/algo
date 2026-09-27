#!/usr/bin/env python3
"""critic R3f Q2: (a) independent re-solve of the X3-LR4 band gains (null-space elimination + Gauss-Legendre sector
integrals, NOT the script's KKT block / 0.25-deg rule); (b) first-order optimality; (c) drive-level claim (+1.2/+0.6 dB
vs D20 per channel, -3.3 dB on-axis if held <= D20) which is not in any log/CSV; (d) transient (L1) headroom of the
IIR channels vs the sine figure; (e) plausibility of 'free low band -> superdirective, 12-15 dB on-axis loss'."""
import csv
import os
import sys

import numpy as np
from scipy import signal

REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
for p in ("sprint7/sim/side30", "sprint7/sim/side30/fir", "sprint7/sim/acoustic", "sprint7/dsp/wtbl"):
    sys.path.insert(0, os.path.join(REPO, p))
import s7_alt_algos as A          # noqa: E402  module import only
import s7_common as S             # noqa: E402

FS = 48000.0
C, D = 343.0, 0.055
XC = ((np.arange(16) - 7.5) * D)[:8]


def params(name):
    with open(os.path.join(REPO, "sprint7/sim/side30/s7_alt_algos_params.csv")) as fp:
        rows = [r for r in csv.DictReader(fp) if r["design"] == name]
    return np.array([[float(r[f"c{i}"]) for i in range(8)] for r in sorted(rows, key=lambda r: int(r["band_or_param"]))])


def seccov_gl(t0, t1, f, n=200):
    """Sector covariance by Gauss-Legendre quadrature in theta (continuous mean), independent of the 0.25-deg rule."""
    x, w = np.polynomial.legendre.leggauss(n)
    th = np.deg2rad(0.5 * (t1 - t0) * x + 0.5 * (t1 + t0))
    a = 2 * np.cos(2 * np.pi * f / C * np.outer(np.sin(th), XC))
    return (a.T * (w / 2)) @ a


def lrm(f, xo=(700.0, 1600.0), order=4):
    t = lambda fc: (np.tan(np.pi * f / FS) / np.tan(np.pi * fc / FS)) ** order  # noqa: E731
    l1, h1, l2, h2 = 1 / (1 + t(xo[0])), t(xo[0]) / (1 + t(xo[0])), 1 / (1 + t(xo[1])), t(xo[1]) / (1 + t(xo[1]))
    return np.array([l2 * l1, l2 * h1, h2])


def main():
    name = "X3-LR4-700/1600-e0.1m35"
    wk = params(name)
    d20 = S.read_w8()[0]
    d20n = d20 / (2 * d20.sum())
    print(f"(a0) band 1 row == frozen D20 normalised: max diff {np.abs(wk[0] - d20n).max():.1e}; "
          f"sum 2w per band: {np.array2string(2 * wk.sum(1), precision=15)}")
    # ---- (a) independent solve: x = x0 + Z y (null space), minimise mean_f |Q^1/2 (m1 d20 + m2 w2 + m3 w3)|^2 ------
    b = np.array([A.F.band_freqs(fc) for fc in A.B7]).ravel()
    sg = float(np.sinh(np.log(10) / 10) / (np.log(10) / 10) - 2 * np.sinh(np.log(10) / 20) / (np.log(10) / 20)
               * np.sin(np.deg2rad(5)) / np.deg2rad(5) + 1)
    sx2 = (0.5e-3) ** 2 / 3
    for tag, covf in (("0.25-deg rule (script's)", lambda t0, t1, f: A.F.sector_cov(t0, t1, f)),
                      ("Gauss-Legendre (continuous)", seccov_gl)):
        Hm = np.zeros((16, 16))
        gv = np.zeros(16)
        for f in b:
            k = 2 * np.pi * f / C
            Q = covf(60.0, 90.0, f) + 0.1 * covf(35.0, 60.0, f) + 2 * (sg + k * k * sx2) * np.eye(8)
            m = lrm(f)
            Mf = np.hstack([m[1] * np.eye(8), m[2] * np.eye(8)])      # W = m1 d20n + Mf x
            Hm += Mf.T @ Q @ Mf / len(b)
            gv += Mf.T @ Q @ (m[0] * d20n) / len(b)
        Cc = np.kron(np.eye(2), 2 * np.ones((1, 8)))
        x0 = np.linalg.lstsq(Cc, np.ones(2), rcond=None)[0]
        _, _, Vt = np.linalg.svd(Cc)
        Z = Vt[2:].T                                                 # null-space basis (16 x 14)
        y = np.linalg.solve(Z.T @ Hm @ Z, -Z.T @ (Hm @ x0 + gv))
        x = x0 + Z @ y
        grad = Hm @ x + gv
        pg = Z.T @ grad
        print(f"(a) {tag:28s}: max|w - script| = {np.abs(x.reshape(2, 8) - wk[1:]).max():.2e} "
              f"(rel {np.abs(x.reshape(2, 8) - wk[1:]).max() / np.abs(wk[1:]).max():.1e}); projected gradient "
              f"{np.abs(pg).max():.1e}; min eig of reduced Hessian {np.linalg.eigvalsh(Z.T @ Hm @ Z).min():.2e} (>0 -> unique min)")
    # ---- (c) drive level per channel vs D20 (full-drive normalisation = max over channels and 20 Hz-20 kHz) ---------------
    fd = np.geomspace(20.0, 20000.0, 4000)
    W = np.stack([lrm(f) for f in fd]) @ wk                          # (F, 8) real, >= 0
    amax = W.max()
    d20r = d20 / d20.max()                                           # today's table at full drive (c7 = 1.0)
    rel = 20 * np.log10((W / amax) / d20r[None, :])                  # dB above today's same channel
    print(f"(c) full-drive normalisation: amax = {amax:.5f} at channel {np.unravel_index(W.argmax(), W.shape)[1]} "
          f"f = {fd[np.unravel_index(W.argmax(), W.shape)[0]]:.0f} Hz; on-axis vs D20 = "
          f"{20 * np.log10(1 / amax / (2 * d20.sum() / d20.max())):+.3f} dB")
    for c in range(8):
        i = np.argmax(rel[:, c])
        print(f"    channel c{c} (elements {{{c},{15 - c}}}, |x| = {abs(XC[c]) * 1e3:5.1f} mm): max over f of drive vs D20 same "
              f"channel = {rel[i, c]:+6.2f} dB at {fd[i]:7.0f} Hz ; at >=1.6 kHz max {rel[fd >= 1600, c].max():+6.2f} dB")
    worst = rel.max()
    print(f"    -> to keep every channel <= D20 same channel: extra attenuation {max(worst, 0):.3f} dB -> on-axis "
          f"{20 * np.log10(1 / amax / (2 * d20.sum() / d20.max())) - max(worst, 0):+.3f} dB")
    # ---- (d) transient headroom: L1 norm of each channel impulse response (real biquads) vs its max sine gain ------------
    def lr(fc, kind):
        s = signal.butter(2, fc, btype=kind, fs=FS, output="sos")
        return np.vstack([s, s])

    def ap(fc):
        s = signal.butter(2, fc, btype="low", fs=FS, output="sos")[0]
        return np.array([[s[5], s[4], s[3], s[3], s[4], s[5]]])
    imp = np.zeros(1 << 15)
    imp[0] = 1.0
    b1 = signal.sosfilt(lr(1600, "low"), signal.sosfilt(lr(700, "low"), imp))
    b2 = signal.sosfilt(lr(1600, "low"), signal.sosfilt(lr(700, "high"), imp))
    b3 = signal.sosfilt(lr(1600, "high"), signal.sosfilt(ap(700), imp))
    h = wk.T @ np.stack([b1, b2, b3])                               # (8, n) channel impulse responses
    l1 = np.abs(h).sum(1)
    sine = W.max(0)
    print(f"(d) per-channel L1 / max-sine gain ratio (dB): {np.array2string(20 * np.log10(l1 / sine), precision=2)}")
    lvl_l1 = 20 * np.log10(1 / l1.max() / (2 * d20.sum() / d20.max()))
    print(f"    on-axis full-drive vs D20: sine convention {20 * np.log10(1 / amax / (2 * d20.sum() / d20.max())):+.2f} dB, "
          f"L1 (worst-case transient) convention {lvl_l1:+.2f} dB  (FIR V1-128t: -1.77 / -6.76 dB, s7_fir_summary.csv)")
    # ---- (e) free low band plausibility: band 1 free too, same 7-band objective -----------------------------------------
    Hm = np.zeros((24, 24))
    for f in b:
        k = 2 * np.pi * f / C
        Q = A.F.sector_cov(60.0, 90.0, f) + 0.1 * A.F.sector_cov(35.0, 60.0, f) + 2 * (sg + k * k * sx2) * np.eye(8)
        Mf = np.hstack([mm * np.eye(8) for mm in lrm(f)])
        Hm += Mf.T @ Q @ Mf / len(b)
    Cc = np.kron(np.eye(3), 2 * np.ones((1, 8)))
    kkt = np.block([[Hm, Cc.T], [Cc, np.zeros((3, 3))]])
    xf = np.linalg.solve(kkt, np.concatenate([np.zeros(24), np.ones(3)]))[:24].reshape(3, 8)
    Wf = np.stack([lrm(f) for f in fd]) @ xf
    print(f"(e) all 3 bands free (7-band objective only): band-1 weights {np.array2string(xf[0], precision=3)}; "
          f"max|W| = {np.abs(Wf).max():.3f} -> on-axis full drive vs D20 {20 * np.log10(1 / np.abs(Wf).max() / (2 * d20.sum() / d20.max())):+.2f} dB")


if __name__ == "__main__":
    main()
