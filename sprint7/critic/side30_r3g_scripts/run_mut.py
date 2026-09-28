"""critic R3g delta: prove each NEW gate in s7_hybrid_lpxo.py can FAIL (copy of the script runs in scratch; outputs land here)."""
import sys, importlib.util
import numpy as np
SIDE = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint7/sim/side30"
MUT = sys.argv[1]
sys.path.insert(0, SIDE)
sys.argv = ["s7_hybrid_lpxo.py", "--mc", "2"]
spec = importlib.util.spec_from_file_location("H", __file__.replace("run_mut.py", "s7_hybrid_lpxo.py"))
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)
orig_lp, orig_db = H.lp_taps, H.design_bands
if MUT == "fit":        # design the 1600 Hz low-pass at 1.3x the crossover; the check still compares with the true target
    H.lp_taps = lambda fc, n: orig_lp(fc * 1.3 if fc == 1600.0 else fc, n)
elif MUT == "sym":      # 1e-9 asymmetry on one tap of every low-pass
    def lp(fc, n):
        h = orig_lp(fc, n).copy(); h[0] += 1e-9; return h
    H.lp_taps = lp
elif MUT == "axis":     # band-2 gains scaled by 1.001 after the design (constraint no longer met)
    def db(*a, **k):
        w = orig_db(*a, **k).copy(); w[1] *= 1.001; return w
    H.design_bands = db
elif MUT == "axis_cap":  # same, but only once the post-hoc cap loading is active (tests the gate on the cap variants)
    def db(*a, **k):
        w = orig_db(*a, **k).copy()
        if k.get("extra_load"):
            w[1] *= 1.001
        return w
    H.design_bands = db
elif MUT == "permute":  # swap band gains 2 and 3 in the taps only (sums still 1/2 each): expected NOT caught by the on-axis gate
    orig_t8 = H.LPBank.taps8
    H.LPBank.taps8 = lambda self, wk: orig_t8(self, np.vstack([wk[0], wk[2], wk[1]] + list(wk[3:])))
try:
    H.main()
    print(f"[{MUT}] MAIN COMPLETED (no gate fired)")
except SystemExit as e:
    print(f"[{MUT}] SystemExit: {str(e)[:160]}")
