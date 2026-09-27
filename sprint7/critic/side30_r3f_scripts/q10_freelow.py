import os, sys
import numpy as np
REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
for p in ("sprint7/sim/side30", "sprint7/sim/side30/fir", "sprint7/sim/acoustic", "sprint7/dsp/wtbl"):
    sys.path.insert(0, os.path.join(REPO, p))
import s7_alt_algos as A
F, S = A.F, A.S
C = 343.0; XC = ((np.arange(16) - 7.5) * 0.055)[:8]
sg = A.SIG2G; sx2 = F.SIG_X2
def seccov(t0, t1, f, n=160):          # Gauss-Legendre sector mean (independent of the 0.25-deg rule)
    x, w = np.polynomial.legendre.leggauss(n); th = np.deg2rad(0.5*(t1-t0)*x + 0.5*(t1+t0))
    a = 2*np.cos(2*np.pi*f/C*np.outer(np.sin(th), XC)); return (a.T*(w/2)) @ a
def lrm(f): return A.lr_mags(np.atleast_1d(f), (700.0, 1600.0), 4)[0]
for mu in (1.0,):
    H = np.zeros((24, 24))
    for f in A.F7:
        Q = seccov(60, 90, f) + 0.1*seccov(35, 60, f) + 2*(sg + (2*np.pi*f/C)**2*sx2)*np.eye(8)
        M = np.hstack([m*np.eye(8) for m in lrm(f)]); H += M.T @ Q @ M / len(A.F7)
    f5 = F.band_freqs(500.0)
    for f in f5:
        Q = seccov(30, 90, f) + 2*(sg + (2*np.pi*f/C)**2*sx2)*np.eye(8)
        M = np.hstack([m*np.eye(8) for m in lrm(f)]); H += mu * M.T @ Q @ M / len(f5)
    Cm = np.kron(np.eye(3), 2*np.ones((1, 8)))
    x0 = np.linalg.lstsq(Cm, np.ones(3), rcond=None)[0]; Z = np.linalg.svd(Cm)[2][3:].T
    x = x0 + Z @ np.linalg.solve(Z.T @ H @ Z, -Z.T @ H @ x0); wk = x.reshape(3, 8)
    fd = np.geomspace(20, 20000, 4000); W = A.lr_mags(fd, (700.0, 1600.0), 4) @ wk
    lvl = 20*np.log10(1/np.abs(W).max()/F.d20_axis_level())
    print(f"mu {mu}: on-axis full drive vs D20 {lvl:+.2f} dB (script log: -14.05); band-1 weights (c0..c7, sum 2w=1):")
    print("   ", np.array2string(wk[0], precision=3), " max|w|/mean|w| =", round(float(np.abs(wk[0]).max()/np.abs(wk[0]).mean()), 2))
