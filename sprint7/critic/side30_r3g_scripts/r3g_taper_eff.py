"""critic R3g delta: per-watt on-axis 'taper' term 10log10((sum w)^2 / (N sum w^2)) of the 16-element weights, as in
DEC-S5-SPL-CALIBER-01 (D20: -0.173 dB). Shows whether the doc's 'L1-convention level lowers max SPL, not sensitivity'
is exact (it is only for the digital back-off; the taper part moves the per-watt figure too)."""
import numpy as np, sys
sys.argv = ["x"]
exec(open("r3g_bank_headroom.py").read().split("# ---------------- (1) bank")[0])
def eff(w8):
    w16 = np.concatenate([w8, w8[::-1]])
    return 10 * np.log10(np.abs(w16.sum()) ** 2 / (16 * np.sum(np.abs(w16) ** 2)))
print(f"D20 taper term {eff(W8):+.3f} dB (DEC-S5-SPL-CALIBER-01: -0.173)")
fc = np.array([500, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000])
for name in ["LPX3-b"]:
    B = bank_of(name)
    h8 = B["wk"].T @ B["bands"]
for label, h8 in [("LPX3-b", h8), ("FIR V1-128", fir_v1())]:
    n = np.arange(h8.shape[1]); D = (h8.shape[1] - 1) // 2
    vals = []
    for f in fc:
        W = (h8 @ np.exp(-1j * 2 * np.pi * f * (n - D) / FS))
        vals.append(eff(W) - eff(W8))
    print(f"{label:11s} per-watt on-axis change vs D20 (taper term difference), dB at " + " ".join(f"{f}:{v:+.2f}" for f, v in zip(fc, vals)))
