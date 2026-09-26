# sprint7/sim/side30/s7_nearfield_side.py -- landed 2026-09-26 (PM). Measurement-distance effect on the side (90 deg, endfire) reading, exact 1/r point-source sums. [L2]. No RNG.
# Exploratory [L2/numpy]: does measurement DISTANCE limit the side (90 deg, along array axis) reading?
# Exact point-source near field: mic on the array axis extension at distance r from centre (side, 90 deg)
# vs mic at distance r on the broadside normal (front, 0 deg). Band = 1/3-oct power avg (41 pts).
import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "acoustic"))
import s7_common as S
from scipy.signal.windows import chebwin
S.assert_anchors(verbose=False)
W20 = S.expand16(S.read_w8()[0]); W30 = S.w_norm(chebwin(16, 30)); W35 = S.w_norm(chebwin(16, 35))
def sb(f): return 0 if f < 1500 else 1 if f < 3000 else 2
D0 = [W20, W20, W20]; D2 = [W30, W35, W35]
def p_at(pos, f, w):
    r = np.sqrt((pos[0] - S.X) ** 2 + pos[1] ** 2)
    k = 2 * np.pi * f / S.C
    return abs(np.sum(w * np.exp(-1j * k * r) / r)) ** 2
def band_att(fc, D, r):
    fs = np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 41)
    pf = np.mean([p_at((0.0, r), f, D[sb(f)]) for f in fs])      # front, on normal
    ps = np.mean([p_at((r, 0.0), f, D[sb(f)]) for f in fs])      # side, on axis extension
    return 10 * np.log10(pf / ps)
print("band-avg front/side ratio at distance r (dB); far-field = large r")
for name, D in (("D0 Dolph-20", D0), ("D2 per-band D30/D35/D35", D2)):
    print(name)
    for fc in (1000, 2000, 4000):
        print(f"  {fc:5d} Hz: " + "  ".join(f"r={r:>4}m {band_att(fc, D, r):5.1f}" for r in (1, 2, 4, 8, 16, 1000)))
