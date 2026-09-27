import os, sys
import numpy as np
REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
for p in ("sprint7/sim/side30", "sprint7/sim/side30/fir", "sprint7/sim/acoustic", "sprint7/dsp/wtbl"):
    sys.path.insert(0, os.path.join(REPO, p))
import s7_alt_algos as A
S = A.S
print("=== DDC-literal checks")
for bw in (30.0, 40.0):
    d = A.ddc_design(bw)
    fclamp = (69.0 / bw) * S.C / 2 / (0.6 * S.D)
    fb = np.geomspace(900, 4500, 400)
    W = d.A(fb).real
    amax_band = W.max()
    lvl_band = 20 * np.log10(1 / amax_band / A.F.d20_axis_level())
    W4 = d.A(np.array([4000.0])).real[0]
    act = (W4 / W4.max() > 0.05).sum()
    print(f"  BW{bw:.0f}: clamp (0.6 d) active above {fclamp:6.0f} Hz ; on-axis full drive with max taken over 0.9-4.5 kHz only: {lvl_band:+.2f} dB"
          f" ; at 4 kHz pairs with weight > 5% of max: {act} (weights edge->centre {np.array2string(W4 / W4.max(), precision=3)})")
print("=== Keele H_T sensitivity (paper text: +1 spacing -> N d ; paper Fig.1/2 13-driver ladder -> (N+1) d)")
for HT in (S.N * S.D, (S.N + 1) * S.D):
    A.HT = HT
    for kw in (dict(arc_deg=20.0, delays=False), dict(arc_deg=20.0), dict(arc_deg=30.0), dict(arc_deg=60.0)):
        d = A.cbt_design(**kw)
        r90 = [A.band_att(d, fc, 90.0) for fc in A.B7]
        print(f"  H_T = {HT / S.D:.0f} d  {d.label():14s} U_edge {d.meta['U'][0]:.3f}  R90 7-band min {min(r90):5.1f}  (per band {' '.join(f'{v:4.1f}' for v in r90)})"
              f"  1k/30 {A.single_att(d, 1000, 30):5.2f}  BW1k {A.bw_at(d, 1000.0):5.1f}")
