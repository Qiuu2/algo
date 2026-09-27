import os, sys
import numpy as np
REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
for p in ("sprint7/sim/side30", "sprint7/sim/side30/fir", "sprint7/sim/acoustic", "sprint7/dsp/wtbl"):
    sys.path.insert(0, os.path.join(REPO, p))
import s7_alt_algos as A
F = A.F
sig2g = F.sigma2_gain(np.random.default_rng(F.SEED))
Wraw, Qs, brob, Ra = F.perbin_design(F.CFG["V1"], sig2g)
P, h = F.fit_fir(F.smooth_logf(Wraw, F.SMOOTH_FWHM_OCT), Qs, brob, 127, Ra, F.FIT_GAMMA)
class FD:
    def __init__(s, d): s.d = d
    def A(s, f): return s.d.A(f).astype(complex)
fir = A.CDesign("FIR V1-128", lambda f: F.Design("V1", "fir", taps=127, P=P).A(f).astype(complex))
x3 = A.xo_designobj((700.0, 1600.0), 4, 0.1, 35.0)
d20 = A.table_design("D20", A.S.read_w8()[0])
bands = (250, 315, 400, 500, 630, 800, 5000, 6300, 8000)
print("R90 band [worst 60-90 sector] outside the 7 DEC bands, and BW(-6) single f   [L2 critic calc]")
for d in (d20, fir, x3):
    r = " ".join(f"{fc}:{A.band_att(d, fc, 90.0):5.1f}[{A.sector_worst(d, fc):5.1f}]" for fc in bands)
    bw = " ".join(f"{f}:{A.bw_at(d, float(f)):5.1f}" for f in (500, 5000, 6300, 8000))
    print(f"  {d.label():12s} {r}\n  {'':12s} BW {bw}")
