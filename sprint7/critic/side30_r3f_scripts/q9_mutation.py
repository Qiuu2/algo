import os, sys
import numpy as np
from scipy import signal as sig
REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
for p in ("sprint7/sim/side30", "sprint7/sim/side30/fir", "sprint7/sim/acoustic", "sprint7/dsp/wtbl"):
    sys.path.insert(0, os.path.join(REPO, p))
import s7_alt_algos as A
TH = dict(ph=1e-6, ms=1e-9, cf=1e-9)          # thresholds used in main()
def verdict(r):
    ph, ms, cf = r
    fail = ph > TH["ph"] or ms > TH["ms"] or cf > TH["cf"]
    return f"phase {ph:.1e}  |sum|-1 {ms:.1e}  closed-form {cf:.1e}  -> {'FAIL (SystemExit)' if fail else 'PASS'}"
print("unmutated              :", verdict(A.real_bank_check((700.0, 1600.0))))
orig_bank, orig_lr4 = A.bank3_sos, A.lr4_sos
def no_ap(xo):
    bands, ap = orig_bank(xo); LP1, HP1 = orig_lr4(xo[0]); LP2, HP2 = orig_lr4(xo[1])
    return [bands[0], bands[1], HP2], ap
A.bank3_sos = no_ap
print("M1 band 3 without AP1  :", verdict(A.real_bank_check((700.0, 1600.0))))
A.bank3_sos = orig_bank
A.lr4_sos = lambda fc: (sig.butter(4, fc, "low", fs=A.FSAMP, output="sos"), sig.butter(4, fc, "high", fs=A.FSAMP, output="sos"))
print("M2 Butterworth-4 not LR:", verdict(A.real_bank_check((700.0, 1600.0))))
A.lr4_sos = orig_lr4
def wrong_ap(xo):
    bands, ap = orig_bank(xo); b2, _ = orig_bank((xo[1], xo[1]))
    return [bands[0], bands[1], b2[2]], ap          # AP realised at 1600 instead of 700
A.bank3_sos = wrong_ap
print("M3 AP at wrong fc      :", verdict(A.real_bank_check((700.0, 1600.0))))
A.bank3_sos = orig_bank
def scaled(xo):
    bands, ap = orig_bank(xo); b = [s.copy() for s in bands]; b[1][0, :3] *= 1.001
    return b, ap                                     # 0.009 dB gain error in the mid band
A.bank3_sos = scaled
print("M4 mid band +0.009 dB  :", verdict(A.real_bank_check((700.0, 1600.0))))
