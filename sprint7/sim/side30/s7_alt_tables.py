#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s7_alt_tables.py -- S7-SIDE30: fixed (frequency-independent) weight tables BEYOND Dolph, evaluated with the SAME
metrics and the SAME Monte Carlo draws as the per-channel FIR prototype, so every number here is comparable with
sprint7/docs/S7_SIDE30_PERCH_FIR_DESIGN.md and sprint7/sim/side30/fir/s7_fir_mc.csv.

L-GRADES
  * ideal metrics ................ [L2/numpy, isotropic point-source far-field model s7_common.py]
  * yields ....................... [L2 on L4 spread] (driver-error model = project assumption, not measured)
  * JY/T points .................. PRD v2.4 caliber: single frequency, 8 evaluable points (30/90 deg x 500/1k/2k/4k);
                                   in-band minimum printed as the stricter secondary view (critic R3b)
  * NOTHING here is measured.

TABLES EVALUATED
  * the Q15 rows READ FROM the generated firmware header m2_wtbl_q15.h (single source of truth), checked equal to a
    fresh gen_m2_wtbl.build(); the frozen D20 Q15 table; Taylor-35 (nbar 5, float) for reference only (not in firmware);
  * Dolph-20 / Dolph-35 in float exactly as s7_fir_robust_design.py builds them = the MC ANCHOR designs.

MC ANCHOR (SystemExit on failure): the two anchor designs must reproduce s7_fir_mc.csv exactly (7 bands x 10 cells:
median, P10, per-band yield, joint3, joint7, mean-power att) -> same draws, same code path (F.mc_cell imported).

RS-B SELECTION RULE (formulated by the PM AFTER an exploratory scan -- see S7_SIDE30_ANALYSIS.md sec 3.1 -- and
reproduced here as a mechanical check): ths = 60 deg, thm = 30 deg (the JY/T angle), eta = the smallest value of the
coarse grid {0.1, 0.3, 1, 3} whose Q15 table is >= the Dolph-35 Q15 table at every one of the 8 evaluable JY/T points.
Must return eta = 1.0 (= gen_m2_wtbl.RS_SPECS), else SystemExit.

EXPLORATION RECORD (critic R3e F4): the grid the PM scanned before fixing the RS-B rule is re-evaluated and logged, and
the exploratory RS-A definition that was proposed to the CTO is reproduced and compared with the formal RS-A row.
Precision (critic R3e F7): each absolute yield cell has ~1.5 points 1-sigma sampling error (1000 arrays; one D35 cell
was found ~3 sigma low on other seeds); table-vs-table comparisons are paired (common random numbers) and much tighter.

Usage: /usr/bin/python3 s7_alt_tables.py [--mc 1000]      (runtime ~2 min)
"""
import argparse
import csv
import os
import re
import sys
import time
import warnings

import numpy as np
from scipy.signal.windows import taylor

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "sprint7", "sim", "acoustic"))
sys.path.insert(0, os.path.join(HERE, "fir"))
sys.path.insert(0, os.path.join(REPO, "sprint7", "dsp", "wtbl"))
import s7_common as S  # noqa: E402
import s7_fir_robust_design as F  # noqa: E402  (module import; its main() does not run)
import gen_m2_wtbl as G  # noqa: E402  (module import; its main() does not run)

HDR = os.path.join(REPO, "sprint6", "dsp", "audio", "m1_cces_project", "src", "m2_wtbl_q15.h")
FIR_MC_CSV = os.path.join(HERE, "fir", "s7_fir_mc.csv")
B7 = F.MC_B7
JYT8 = [(30, 500), (90, 500), (30, 1000), (90, 1000), (30, 2000), (90, 2000), (30, 4000), (90, 4000)]
LOG = []


def log(s=""):
    print(s)
    LOG.append(s)


def read_header_rows():
    t = open(HDR, encoding="utf-8").read()
    nx = int(re.search(r"#define M2_WTBL_NEXTRA\s+(\d+)", t).group(1))
    rows = re.findall(r"\{\s*([\d,\s]+?)\s*\},\s*/\* sel (\d+): (.*?) \*/", t)
    out = []
    for vals, sel, cmt in rows:
        q = np.array([int(v) for v in vals.split(",")], dtype=np.int64)
        out.append((int(sel), q, cmt))
    if len(out) != nx or [r[0] for r in out] != list(range(1, nx + 1)):
        raise SystemExit(f"header parse: NEXTRA={nx}, rows {[r[0] for r in out]}")
    return out


def tdesign(name, w8):
    w8 = np.asarray(w8, float)
    return F.Design(name, "table", table=w8 / (2.0 * w8.sum()))


def jyt_points(d):
    return [F.att_single(d, f, th) for th, f in JYT8]


def ideal_row(d, w8max, d20sum):
    r90 = [F.band_att(d, fc, 90.0) for fc in B7]
    sec = [F.band_sector_worst(d, fc) for fc in B7]
    flo = [F.err_floor_band(d, fc, G.rs_sig2g_closed()) for fc in B7]
    jy = jyt_points(d)
    jyib = [F.att_inband_min(d, f, th) for th, f in JYT8]
    g2m = [v - F.JYT[(th, f)][1] for v, (th, f) in zip(jy, JYT8)]
    w16 = S.expand16(w8max)
    return dict(r90=r90, sec=sec, flo=flo, jy=jy, jyib=jyib, g2m=g2m, bw1k=F.bw_at(d, 1000.0), bw2k=F.bw_at(d, 2000.0),
                ax=20 * np.log10(np.sum(w8max) / d20sum), wng=S.wng_norm_db(w16),
                sll1k=S.peak_sll_interior(S.pattern_db(1000.0, w16)))


def exploration_record(d35_jy):
    """Critic R3e F4: the space the PM explored BEFORE fixing the RS-B rule, re-evaluated here with the canonical
    exact-integral definition (the scratch scan used 0.25-deg sector sums; conclusions identical). Knobs:
    thm (mid-sector start) x eta (mid-sector weight) x nu (500 Hz 1/3-oct 30-90 deg 'narrow LF beam' term), and a
    separate mu family (single-point 30-deg penalty at 500 Hz and 1 kHz). Ideal metrics only [L2]."""
    xg, wg = np.polynomial.legendre.leggauss(64)
    xc = (np.arange(8) - 7.5) * S.D
    sg = G.rs_sig2g_closed()

    def rmean(t1, t2, k):
        t1, t2 = np.deg2rad(t1), np.deg2rad(t2)
        th = 0.5 * (t2 - t1) * xg + 0.5 * (t2 + t1)
        a = 2.0 * np.cos(k * np.outer(np.sin(th), xc))
        return (a.T * (0.5 * wg)) @ a

    def table(thm, eta, nu=0.0, mu=0.0):
        Q = np.zeros((8, 8))
        for f in G.RS_F7:
            k = 2 * np.pi * f / S.C
            Q += rmean(60.0, 90.0, k) + eta * rmean(thm, 60.0, k) + 2 * (sg + k * k * G.RS_SIG_X2) * np.eye(8)
        Q /= len(G.RS_F7)
        if nu:
            f5 = F.band_freqs(500.0)
            Q += nu * np.mean([rmean(30.0, 90.0, 2 * np.pi * f / S.C) for f in f5], 0)
        for f in ((500.0, 1000.0) if mu else ()):
            a = F.steer([30.0], f)[0]
            Q += mu * 0.5 * np.outer(a, a)
        W = np.linalg.solve(Q, np.ones(8))
        return W / W.max()
    d20max = S.read_w8()[0] / S.read_w8()[0].max()
    log("\n=== EXPLORATION RECORD (critic R3e F4): space scanned by the PM before the RS-B rule was fixed [L2 ideal]")
    log("    columns: thinnest JY/T grade-2 margin (point) | all 8 JY/T >= D35 | R90 min7 | BW1k | on-axis vs D20 |"
        " monotone edge->centre | every weight <= D20 same channel")
    grid = [(thm, eta, nu, 0.0) for thm in (30.0, 35.0) for eta in (0.1, 0.3, 1.0, 3.0) for nu in (0.0, 0.03, 0.1, 0.3, 1.0)]
    grid += [(35.0, 0.1, 0.0, mu) for mu in (0.01, 0.03, 0.1, 0.3, 1.0)]
    # critic R3e D1: the scratch scan (rs_dom.py) also looked at eta 0.5-0.8 at thm 30 BEFORE the coarse grid
    # {0.1, 0.3, 1, 3} was chosen; eta 2.0 added here to show the upper edge of the passing window
    grid += [(30.0, eta, 0.0, 0.0) for eta in (0.5, 0.6, 0.7, 0.8, 2.0)]
    for thm, eta, nu, mu in grid:
        w = table(thm, eta, nu, mu)
        d = tdesign("g", w)
        jy = jyt_points(d)
        g2 = [v - F.JYT[(th, f)][1] for v, (th, f) in zip(jy, JYT8)]
        i = int(np.argmin(g2))
        r90 = min(F.band_att(d, fc, 90.0) for fc in B7)
        log(f"  thm {thm:4.0f} eta {eta:<4g} nu {nu:<5g} mu {mu:<5g} | g2 {g2[i]:+6.2f} ({JYT8[i][1]}/{JYT8[i][0]})"
            f" | >=D35 {str(all(a >= b for a, b in zip(jy, d35_jy))):5s} | R90 {r90:5.1f} | BW1k {F.bw_at(d, 1000.0):5.1f}"
            f" | ax {20 * np.log10(np.sum(w) / np.sum(d20max)):+5.2f} | mono {str(bool(np.all(np.diff(w) >= -1e-12))):5s}"
            f" | <=D20 {str(bool(np.all(w <= d20max + 1e-12)))}")
    # the exploratory RS-A definition as proposed to the CTO (scratch altwin.py, 2026-09-27): 2-deg angle sums,
    # 7 frequency points per band (every 4th of 25), load 2 x 0.00698 (gain+phase only, no position term)
    X8 = S.X[:8]
    RD, RM, nd, nm = np.zeros((8, 8)), np.zeros((8, 8)), 0, 0
    for fc in B7:
        for f in np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 25)[::4]:
            for th in np.arange(60, 90.1, 2.0):
                a = 2 * np.cos(2 * np.pi * f / S.C * X8 * np.sin(np.deg2rad(th)))
                RD += np.outer(a, a)
                nd += 1
            for th in np.arange(35, 60.1, 2.0):
                a = 2 * np.cos(2 * np.pi * f / S.C * X8 * np.sin(np.deg2rad(th)))
                RM += np.outer(a, a)
                nm += 1
    we = np.linalg.solve(RD / nd + 0.1 * RM / nm + 2 * 0.00698 * np.eye(8), np.ones(8))
    we = we / we.max()
    wa = [q for lab, q, _m, _c in G.build()[1] if lab == "RS-A"][0] / 32768.0
    log(f"  exploratory RS-A (as proposed) {np.round(we, 4)} vs formal RS-A Q15 {np.round(wa, 4)}:"
        f" max |dw| = {np.abs(we - wa).max():.4f}")
    log("  NOTE (critic R3e D1): before the RS-B rule was fixed the PM also VIEWED exploratory Monte-Carlo yields")
    log("  (scratch rs_explore.py / rs_explore3.py, 2026-09-28 00:03-00:07, same F.mc_cell seeds): D35 plus ~8 RS")
    log("  candidates (thm 35: eta 0.1/0.3/1, the mu family; thm 30: eta 0.1/0.3/1/3; and two nu = 0.03 variants).")
    log("  The coarse eta grid {0.1, 0.3, 1, 3} was chosen after eta 0.5-0.8 had been seen; on the finer rows above the")
    log("  'all 8 JY/T >= D35' rule holds for a window of eta (about 0.7-2), whose tables are nearly identical.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", type=int, default=1000)
    args = ap.parse_args()
    t0 = time.time()
    anc = S.assert_anchors(verbose=False)
    log(f"S7 side-30: fixed tables beyond Dolph [L2; yields L2 on L4]  anchors {', '.join(f'{k}={v:.6g}' for k, v in anc.items())}")

    # ---- tables: header rows == fresh generation -------------------------------------------------------------
    hrows = read_header_rows()
    fz, grows = G.build()
    for (sel, q, cmt), (lab, qg, _m, _c) in zip(hrows, grows):
        if not np.array_equal(q, qg):
            raise SystemExit(f"header row sel {sel} != fresh gen_m2_wtbl.build() row {lab}")
    labels = [lab for lab, _q, _m, _c in grows]
    log(f"header {os.path.relpath(HDR, REPO)}: NEXTRA={len(hrows)} rows {labels} == fresh generation (bit-exact)")
    d20q = fz.astype(float) / 32768.0
    d20sum = float(np.sum(d20q))
    tabs = [("D20q", d20q)] + [(f"{lab}q", q.astype(float) / 32768.0) for lab, q, _m, _c in grows]
    tay = taylor(16, nbar=5, sll=35, norm=False)[:8]
    tabs.append(("Taylor35", tay / tay.max()))
    for n, w in tabs:
        log(f"  {n:9s} w8 edge->centre {np.array2string(np.asarray(w), precision=4, floatmode='fixed')}  sum(max-norm) {np.sum(w):.5f}")

    # ---- ideal metrics ---------------------------------------------------------------------------------------
    log("\n=== IDEAL metrics [L2]: R90 = 1/3-oct band power avg at +-90 deg (worse side = either, model symmetric), 31 pts/band")
    log("    sec = worst point of the 60-90 deg sector (band power);  floor = mean random-error side floor sigma^2||w||^2/|sum w|^2")
    irows, ideal = [], {}
    for n, w in tabs:
        d = tdesign(n, w)
        m = ideal_row(d, w, d20sum)
        ideal[n] = m
        log(f"  {n:9s} R90 min7 {min(m['r90']):5.2f} [{' '.join(f'{v:4.1f}' for v in m['r90'])}]  sec60 min7 {min(m['sec']):5.2f}"
            f"  floor min7 {min(m['flo']):5.2f}  BW1k {m['bw1k']:5.2f}  BW2k {m['bw2k']:5.2f}  on-axis {m['ax']:+5.2f} dB"
            f"  WNGn {m['wng']:+5.2f}  SLL@1k {m['sll1k']:6.2f}")
        for b, fc in enumerate(B7):
            irows.append([n, "R90_band", fc, f"{m['r90'][b]:.3f}"])
            irows.append([n, "sector60_90_worst_band", fc, f"{m['sec'][b]:.3f}"])
            irows.append([n, "err_floor_band", fc, f"{m['flo'][b]:.3f}"])
        for (th, f), v, ib, g in zip(JYT8, m["jy"], m["jyib"], m["g2m"]):
            irows.append([n, f"JYT_{f}_{th}_single", f, f"{v:.3f}"])
            irows.append([n, f"JYT_{f}_{th}_inband_min", f, f"{ib:.3f}"])
            irows.append([n, f"JYT_{f}_{th}_grade2_margin", f, f"{g:.3f}"])
        irows += [[n, "BW_1k_deg", 1000, f"{m['bw1k']:.3f}"], [n, "BW_2k_deg", 2000, f"{m['bw2k']:.3f}"],
                  [n, "onaxis_vs_D20_dB", 0, f"{m['ax']:.3f}"], [n, "WNG_norm_dB", 0, f"{m['wng']:.3f}"],
                  [n, "SLL_1k_dB", 1000, f"{m['sll1k']:.3f}"]]
    log("\n  JY/T 8 evaluable points, single frequency [in-band minimum]  (grade-2 threshold)")
    log("  " + " " * 18 + "".join(f"{f'{f}/{th}':>17s}" for th, f in JYT8))
    log("  " + f"{'grade-2 line':18s}" + "".join(f"{F.JYT[(th, f)][1]:>17d}" for th, f in JYT8))
    for n, _w in tabs:
        m = ideal[n]
        log("  " + f"{n:18s}" + "".join(f"{v:8.2f} [{ib:6.2f}]" for v, ib in zip(m["jy"], m["jyib"])))
        log("  " + f"{'  grade-2 margin':18s}" + "".join(f"{g:+17.2f}" for g in m["g2m"]))
    dom = {n: all(a >= b for a, b in zip(ideal[n]["jy"], ideal["D35q"]["jy"])) for n, _w in tabs}
    log("  single-frequency JY/T >= D35q at all 8 points: " + ", ".join(f"{n} {'YES' if v else 'no'}" for n, v in dom.items()))
    if not dom["RS-Bq"]:
        raise SystemExit("RS-B does not keep all 8 JY/T points >= D35 -- header claim broken")

    # ---- RS-B selection rule, reproduced mechanically -----------------------------------------------------------
    log("\n=== RS-B selection rule (coarse grid eta, ths=60, thm=30; Q15 tables)")
    pick = None
    for eta in (0.1, 0.3, 1.0, 3.0):
        q = G.q15(G.rs_track1(60.0, 30.0, eta))
        d = tdesign("g", q / 32768.0)
        jy = jyt_points(d)
        ok = all(a >= b for a, b in zip(jy, ideal["D35q"]["jy"]))
        worst = min(zip([a - b for a, b in zip(jy, ideal["D35q"]["jy"])], JYT8))
        log(f"  eta {eta:<4} Q15 {q.tolist()}  all 8 >= D35: {ok}   worst (point - D35) {worst[0]:+.3f} dB at {worst[1][1]}/{worst[1][0]}")
        if ok and pick is None:
            pick = eta
    spec_b = [s for s in G.RS_SPECS if s[0] == "RS-B"][0]
    if pick != spec_b[3] or spec_b[1:3] != (60.0, 30.0):
        raise SystemExit(f"selection rule gives eta={pick}, RS_SPECS has {spec_b}")
    log(f"  -> smallest passing eta = {pick} == RS_SPECS RS-B  (PASS)")
    exploration_record(ideal["D35q"]["jy"])

    # ---- Monte Carlo (same draws as the FIR prototype) --------------------------------------------------------
    M = args.mc
    anchors = [F.Design("Dolph-20", "table", table=F.d20_norm()), F.Design("Dolph-35", "table", table=F.d35_norm())]
    designs = anchors + [tdesign(n, w) for n, w in tabs]
    log(f"\n=== MONTE CARLO [L2 on L4 spread]: {M} arrays/cell, common random numbers, seeds = s7_fir_robust_design"
        f" (SEED {F.SEED} + 1000*(model+1) + strategy); JOINT7 = all 7 DEC-S7-SIDE30-01 bands >= 30 dB (headline)")
    ref = {}
    if M == 1000:
        with open(FIR_MC_CSV, newline="") as fp:
            for r in csv.DictReader(fp):
                ref[(r["design"], r["error_model"], r["strategy"], int(r["band_fc_hz"]))] = r
    mrows, J7 = [], {}
    nanchor = 0
    for mi, (mname, model, sm) in enumerate(F.MODELS):
        for si, (st, slab) in enumerate(F.STRATS):
            seed = F.SEED + 1000 * (mi + 1) + si
            ts = time.time()
            res, side = F.mc_cell(designs, model, sm, st, M, seed)
            line = []
            for d in designs:
                r7 = res[d.label()]
                j3 = float(np.mean(np.all(r7[:, F.I3] >= 30.0, axis=1)) * 100)
                j7 = float(np.mean(np.all(r7 >= 30.0, axis=1)) * 100)
                J7[(d.label(), mname, st)] = j7
                mp7 = [-10 * np.log10(side[d.label()][:, b, :].mean()) for b in range(len(B7))]
                for b, fc in enumerate(B7):
                    row = [d.label(), mname, st, fc, f"{np.median(r7[:, b]):.2f}", f"{np.percentile(r7[:, b], 10):.2f}",
                           f"{np.mean(r7[:, b] >= 30)*100:.1f}", f"{j3:.1f}", f"{j7:.1f}", f"{mp7[b]:.2f}", seed, M]
                    mrows.append(row)
                    if d.label() in ("Dolph-20", "Dolph-35") and ref:
                        rr = ref[(d.label(), mname, st, fc)]
                        want = [rr["median_db"], rr["p10_db"], rr["yield_ge30_pct"], rr["joint3_yield_pct_1k2k4k"],
                                rr["joint7_yield_pct_DEC1_1k-4k"], rr["meanpower_att_per_side_db"], rr["seed"]]
                        if [str(x) for x in row[4:11]] != want:
                            raise SystemExit(f"MC ANCHOR FAIL {d.label()} {mname} {st} {fc}: {row[4:11]} vs {want}")
                        nanchor += 1
                line.append(f"{d.label()} {j7:5.1f}%/{np.median(r7.min(1)):4.1f}")
            log(f"  [{mname[:6]}|{st:8s}] seed {seed} ({time.time()-ts:4.1f}s)  joint7 / median(worst of 7 bands):  " + "  ".join(line))
    if ref:
        log(f"  MC ANCHOR: {nanchor} anchor rows (2 designs x 7 bands x 10 cells) reproduce s7_fir_mc.csv exactly -> PASS")
    else:
        log("  MC ANCHOR: skipped (only defined for --mc 1000)")

    log("\n=== SUMMARY (joint7 %, U-flat | G-p0.5+jig) [L2 on L4 spread]")
    for n in ["D20q", "D30q", "D35q", "RS-Aq", "RS-Bq", "Taylor35"]:
        cells = []
        for st in ("asbuilt", "amp", "pair", "cplx", "paircplx"):
            cells.append(f"{st} {J7[(n, 'U-flat', st)]:5.1f} | {J7[(n, 'G-p0.5-l1oct+jig0.25', st)]:5.1f}")
        log(f"  {n:9s} " + "   ".join(cells))

    for name, hdr, rows in (("s7_alt_tables_ideal.csv", ["design", "metric", "freq_hz", "value"], irows),
                            ("s7_alt_tables_mc.csv", ["design", "error_model", "strategy", "band_fc_hz", "median_db", "p10_db",
                                                      "yield_ge30_pct", "joint3_yield_pct_1k2k4k", "joint7_yield_pct_DEC1_1k-4k",
                                                      "meanpower_att_per_side_db", "seed", "arrays"], mrows)):
        with open(os.path.join(HERE, name), "w", newline="") as fp:
            wr = csv.writer(fp, lineterminator="\n")
            wr.writerow(hdr)
            wr.writerows(rows)
    log(f"\nruntime {time.time()-t0:.0f}s ; outputs s7_alt_tables.log / s7_alt_tables_ideal.csv / s7_alt_tables_mc.csv")
    with open(os.path.join(HERE, "s7_alt_tables.log"), "w") as fp:
        fp.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
