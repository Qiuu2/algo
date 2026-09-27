#!/usr/bin/env python3
"""Critic R3e: the PM's OWN MC code path (F.mc_cell, read-only import) with DIFFERENT seeds, all 10 cells,
to separate seed luck from the table effect. Writes nothing into the repo."""
import os
import sys
import numpy as np

REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
sys.path.insert(0, os.path.join(REPO, "sprint7", "sim", "acoustic"))
sys.path.insert(0, os.path.join(REPO, "sprint7", "sim", "side30", "fir"))
import s7_fir_robust_design as F  # noqa: E402

TAB = {"D35q": [5868, 8179, 12739, 17834, 22954, 27510, 30932, 32768],
       "RS-Aq": [3470, 6948, 11598, 16960, 22469, 27318, 30876, 32768],
       "RS-Bq": [5285, 8787, 13546, 18697, 23762, 28068, 31143, 32768]}
designs = []
for n, q in TAB.items():
    w = np.array(q, float) / 32768.0
    designs.append(F.Design(n, "table", table=w / (2.0 * w.sum())))
M = 1000
seeds = [777, 4242, 90210]
for mi, (mname, model, sm) in enumerate(F.MODELS):
    for si, (st, _slab) in enumerate(F.STRATS):
        J = {d.label(): [] for d in designs}
        for s in seeds:
            res, _side = F.mc_cell(designs, model, sm, st, M, s + 17 * mi + si)
            for d in designs:
                J[d.label()].append(np.all(res[d.label()] >= 30.0, axis=1))
        cat = {k: np.concatenate(v) for k, v in J.items()}
        n = len(cat["D35q"])
        out = f"[{mname[:6]}|{st:8s}] n={n}  " + "  ".join(f"{k} {100*cat[k].mean():5.1f}" for k in cat)
        for k in ("RS-Aq", "RS-Bq"):
            a, b = cat[k], cat["D35q"]
            n10, n01 = int(np.sum(a & ~b)), int(np.sum(~a & b))
            se = 100 * np.sqrt(n10 + n01 - (n10 - n01) ** 2 / n) / n
            out += f"   {k}-D35 {100*(a.mean()-b.mean()):+5.1f}+/-{se:.1f} (per-seed " + "/".join(
                f"{100*(x.mean()-y.mean()):+.1f}" for x, y in zip(J[k], J['D35q'])) + ")"
        print(out, flush=True)
