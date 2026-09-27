import sys, numpy as np
sys.path.insert(0, "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint7/sim/acoustic")
import s7_common as S
from scipy.signal.windows import chebwin, taylor
S.assert_anchors(verbose=False)
X = S.X; X8 = X[:8]; C = S.C
BANDS = [1000, 1250, 1600, 2000, 2500, 3150, 4000]
def fgrid(fc, n=25): return np.geomspace(fc * 2 ** (-1/6), fc * 2 ** (1/6), n)
FS = {fc: fgrid(fc) for fc in BANDS}
def w16(w8): w8 = np.asarray(w8, float); w8 = w8 / w8.max(); return np.concatenate([w8, w8[::-1]])
def band_att90(w, fc, e=None, dx=None):
    x = X if dx is None else X + dx; ww = w if e is None else w * e
    st = np.array([0.0, 1.0, -1.0]); p = np.zeros(3)
    for f in FS[fc]:
        p += np.abs((ww[None, :] * np.exp(1j * 2 * np.pi * f / C * np.outer(st, x))).sum(1)) ** 2
    return 10 * np.log10(p[0] / max(p[1], p[2]))
def a_vec(th, f): return 2 * np.cos(2 * np.pi * f / C * X8 * np.sin(np.deg2rad(th)))
def robust_table(eta, lam, sector=(60, 90), mid=(35, 60)):
    RD = np.zeros((8, 8)); RM = np.zeros((8, 8)); nd = nm = 0
    for fc in BANDS:
        for f in FS[fc][::4]:
            for th in np.arange(sector[0], sector[1] + 0.1, 2.0): a = a_vec(th, f); RD += np.outer(a, a); nd += 1
            for th in np.arange(mid[0], mid[1] + 0.1, 2.0): a = a_vec(th, f); RM += np.outer(a, a); nm += 1
    w = np.linalg.solve(RD / nd + eta * RM / nm + lam * np.eye(8), np.ones(8))
    return w16(w)
sig2 = 0.00698   # project-convention per-driver error variance (FIR teammate log line 3)
w = robust_table(0.1, 2 * sig2)[:8]
formal = np.array([3470, 6948, 11598, 16960, 22469, 27318, 30876, 32768]) / 32768.0
print("original altwin.py robust_table(0.1):", np.round(w, 4))
print("formal RS-A (Q15/32768)            :", np.round(formal, 4))
print("max |dw| = %.4f   (at channel %d)" % (np.abs(w - formal).max(), int(np.argmax(np.abs(w - formal)))))
