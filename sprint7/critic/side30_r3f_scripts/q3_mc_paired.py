#!/usr/bin/env python3
"""critic R3f Q3: paired (common-random-number) comparison X3-LR4 rep vs FIR V1-128t, per trial, + out-of-sample re-draw.
Rebuilds V1-128t from F (must reproduce s7_fir_mc.csv joint7 exactly = anchor), rebuilds X3 designs via A.xo_designobj."""
import csv
import math
import os
import sys
import time

import numpy as np

REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
for p in ("sprint7/sim/side30", "sprint7/sim/side30/fir", "sprint7/sim/acoustic", "sprint7/dsp/wtbl"):
    sys.path.insert(0, os.path.join(REPO, p))
import s7_alt_algos as A          # noqa: E402
F = A.F


def binom_two_sided(k, n):
    if n == 0:
        return 1.0
    k = min(k, n - k)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def main():
    t0 = time.time()
    sig2g = F.sigma2_gain(np.random.default_rng(F.SEED))
    Wraw, Qs, brob, Ra = F.perbin_design(F.CFG["V1"], sig2g)
    Ws = F.smooth_logf(Wraw, F.SMOOTH_FWHM_OCT)
    P, h = F.fit_fir(Ws, Qs, brob, 127, Ra, F.FIT_GAMMA)
    fir = F.Design("V1", "fir", taps=127, P=P)
    print(f"rebuilt {fir.label()} in {time.time() - t0:.1f}s")
    x3 = A.xo_designobj((700.0, 1600.0), 4, 0.1, 35.0)
    x3b = A.xo_designobj((700.0, 2000.0), 4, 1.0, 30.0)
    x3c = A.xo_designobj((700.0, 2000.0), 4, 3.0, 30.0)
    x8 = A.xo_designobj((700.0, 1600.0), 8, 0.1, 35.0)
    x8b = A.xo_designobj((700.0, 1400.0), 8, 0.1, 35.0)
    d35 = F.Design("Dolph-35", "table", table=F.d35_norm())
    designs = [fir, x3, x3b, x3c, x8, x8b, d35]
    ref = {}
    with open(os.path.join(REPO, "sprint7/sim/side30/fir/s7_fir_mc.csv")) as fp:
        for r in csv.DictReader(fp):
            if int(r["band_fc_hz"]) == 1000:
                ref[(r["design"], r["error_model"], r["strategy"])] = float(r["joint7_yield_pct_DEC1_1k-4k"])
    alt = {}
    with open(os.path.join(REPO, "sprint7/sim/side30/s7_alt_algos_mc.csv")) as fp:
        for r in csv.DictReader(fp):
            if int(r["band_fc_hz"]) == 1000:
                alt[(r["design"], r["error_model"], r["strategy"])] = float(r["joint7_yield_pct_DEC1_1k-4k"])
    M = 1000
    for phase, off in (("IN-SAMPLE (original seeds)", 0), ("OUT-OF-SAMPLE (fresh seeds, +777777)", 777777)):
        print(f"\n=== {phase}: joint7 %, paired X3-LR4 rep vs FIR V1-128t (b = X3 pass & FIR fail, c = X3 fail & FIR pass)")
        for mi, (mname, model, sm) in enumerate(F.MODELS):
            for si, (st, _slab) in enumerate(F.STRATS):
                seed = F.SEED + 1000 * (mi + 1) + si + off
                res, _ = F.mc_cell(designs, model, sm, st, M, seed)
                j = {d.label(): np.all(res[d.label()] >= 30.0, axis=1) for d in designs}
                a, bb = j[x3.label()], j[fir.label()]
                b = int(np.sum(a & ~bb))
                c = int(np.sum(~a & bb))
                diff = (b - c) / M * 100
                se = math.sqrt(max(b + c - (b - c) ** 2 / M, 0)) / M * 100
                chk = ""
                if off == 0:
                    okf = abs(j[fir.label()].mean() * 100 - ref[(fir.label(), mname, st)]) < 1e-9
                    okx = abs(a.mean() * 100 - alt[(x3.label(), mname, st)]) < 1e-9
                    okd = abs(j["Dolph-35"].mean() * 100 - ref[("Dolph-35", mname, st)]) < 1e-9
                    chk = f"  anchors FIR {'OK' if okf else 'MISMATCH'} X3 {'OK' if okx else 'MISMATCH'} D35 {'OK' if okd else 'MISMATCH'}"
                others = " ".join(f"{d.label().replace('-e', ' e')}:{j[d.label()].mean() * 100:5.1f}" for d in designs[2:6])
                print(f"  [{mname[:6]}|{st:8s}] X3 {a.mean() * 100:5.1f}  FIR {bb.mean() * 100:5.1f}  D35 {j['Dolph-35'].mean() * 100:5.1f}"
                      f" | X3-FIR {diff:+5.1f} pp (paired SE {se:3.1f}, 95% CI {diff - 1.96 * se:+5.1f}..{diff + 1.96 * se:+5.1f})"
                      f"  b/c {b}/{c}  McNemar exact p {binom_two_sided(min(b, c), b + c):.3f}{chk}")
                print(f"        others: {others}")
    print(f"\nruntime {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
