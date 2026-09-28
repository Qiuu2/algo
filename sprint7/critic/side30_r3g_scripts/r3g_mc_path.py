"""critic R3g: (i) FIR V1 taps symmetry; (ii) MC CSV vs log summary consistency; (iii) F.mc_cell duck-typing path:
real-table F.Design vs complex CDesign carrying the same table must give identical results (small M)."""
import csv, os, sys, re
import numpy as np
SIDE = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint7/sim/side30"
h = np.zeros((8, 127))
with open(os.path.join(SIDE, "fir/s7_fir_coeffs_127tap.csv")) as fp:
    for r in csv.DictReader(fp):
        if r["variant"] == "V1" and int(r["taps"]) == 127:
            h[int(r["channel"])] = [float(r[f"h{i}"]) for i in range(127)]
print("FIR V1 max |h - flip(h)|:", np.abs(h - h[:, ::-1]).max(), " max|h|", np.abs(h).max())
# (ii) CSV vs log
J = {}
with open(os.path.join(SIDE, "s7_hybrid_lpxo_mc.csv")) as fp:
    for r in csv.DictReader(fp):
        J.setdefault((r["design"], r["error_model"], r["strategy"]), set()).add((r["joint7_yield_pct_DEC1_1k-4k"], r["seed"], r["arrays"]))
bad = [k for k, v in J.items() if len(v) != 1]
print("MC CSV: cells", len(J), " cells with inconsistent joint7/seed across bands:", bad)
log = open(os.path.join(SIDE, "s7_hybrid_lpxo.log")).read().splitlines()
i0 = [i for i, l in enumerate(log) if l.startswith("=== SUMMARY")][0]
nchk = 0; mism = []
for l in log[i0 + 1:i0 + 9]:
    name = l[:28].strip()
    if name.startswith("FIR"):
        continue
    vals = re.findall(r"(\d+\.\d)/\s*(\d+\.\d)", l)
    for (u, g), st in zip(vals, ("asbuilt", "amp", "pair", "cplx", "paircplx")):
        for em, v in (("U-flat", u), ("G-p0.5-l1oct+jig0.25", g)):
            cv = next(iter(J[(name, em, st)]))[0]
            nchk += 1
            if abs(float(cv) - float(v)) > 1e-9:
                mism.append((name, em, st, cv, v))
print("log SUMMARY vs CSV joint7:", nchk, "values, mismatches:", mism)
seeds = {(k[1], k[2]): next(iter(v))[1] for k, v in J.items()}
fir_seed = {}
with open(os.path.join(SIDE, "fir/s7_fir_mc.csv")) as fp:
    for r in csv.DictReader(fp):
        if r["design"] == "V1-128t":
            fir_seed[(r["error_model"], r["strategy"])] = (r["seed"], r["arrays"], r["joint7_yield_pct_DEC1_1k-4k"])
print("seeds equal to s7_fir_mc.csv V1-128t cells:", all(seeds[k] == fir_seed[k][0] for k in fir_seed), "; FIR joint7 (U asbuilt/pair):",
      fir_seed[("U-flat", "asbuilt")][2], fir_seed[("U-flat", "pair")][2])
# (iii) duck typing
sys.path.insert(0, SIDE)
import s7_alt_algos as A
F = A.F
t = F.d20_norm()
d_real = F.Design("Dolph-20", "table", table=t)
d_cplx = A.CDesign("D20-cplx", lambda f, t=t: np.tile(t, (len(f), 1)).astype(complex))
for st, _ in F.STRATS:
    for mname, model, sm in F.MODELS:
        res, side = F.mc_cell([d_real, d_cplx], model, sm, st, 25, 12345)
        print(f"  mc_cell {mname[:6]} {st:8s}: max |R90 real-path - complex-path| = {np.abs(res['Dolph-20'] - res['D20-cplx']).max():.2e} dB")
