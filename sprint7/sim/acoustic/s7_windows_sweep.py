#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S7 / B5  -- side-lobe / beam-width window comparison + per-sub-band "constant beam-width" study.
L-grade: [L2/numpy]. Nothing measured. Single-track unless s7_dualtrack_compare.csv says otherwise.

MODEL / CONVENTIONS: see s7_common.py docstring (N=16, d=55 mm, L=825 mm, isotropic point sources,
far-field array factor, centre-symmetric real weights only, c=343 m/s; BW = -6 dB FULL angle;
SLL = peak side lobe re main lobe; DI closed-form 3-D; WNG_norm relative to uniform;
att30 = -20log10|AF(30)/AF(0)| positive dB).

ANCHORS: s7_common.assert_anchors() runs FIRST and raises (script stops, no CSV written) if the
frozen Dolph -20 dB table does not reproduce BW@1k = 29.269 +/- 0.1 deg, BW@2k = 14.515 +/- 0.1 deg,
SLL = -20.00 dB, and uniform SLL@1k ~ -13.3 dB (negative controls demanded by the task).

PART 1  window sweep: uniform / Dolph-20 (frozen baseline) / Dolph-25 / Dolph-30 / Taylor-25 (nbar=4)
        / Kaiser b=3 / Kaiser b=5 / Hann (edge-nonzero) / Hann (scipy sym, edge pair = 0)
        x  f = 500/750/1k/1.5k/2k/3k/4k/5k/6k Hz.
        -> s7_windows_sweep.csv
PART 2  per-sub-band constant-beam-width study on the IMPLEMENTED sub-band split
        (tree_filterbank.h:19-27: SB0 <1.5k, SB1 1.5-3k, SB2 3-6k, SB3 >6k; ideal brick-wall assumed).
        SB0 is held at the frozen Dolph-20 (the 1 kHz spec anchor is not touched). For SB1/SB2 one scalar
        window each is searched over a parametric family (Dolph SLL 20..120, Kaiser beta 0..30,
        Gaussian sigma 0.8..12 elements, Taylor nbar=4 SLL 20..50, plus the PART-1 catalogue) to
        minimise the global (max BW - min BW) over 1-6 kHz sample points.
        Designs: A = unconstrained; B = WNG_norm >= -3 dB per band; C = JY/T table-9 grade-1 30-deg
        attenuation kept (att30(2k) >= 20 dB in SB1, att30(4k) >= 22 dB in SB2).
        -> s7_constbw_subband_design.csv, s7_constbw_fixedwindow_flatness.csv
        PHYSICS: a scalar shading has BW ~ lambda inside its band, so an octave band carries a 2:1 BW
        ripple no matter which window is chosen; the flatness floor is therefore ~ BW(1k)/2.
        Constant BW buys coverage uniformity by WIDENING 1.5-6 kHz; BW(1k) never gets narrower.
"""
import os
import csv
import warnings
import numpy as np
from scipy.signal.windows import chebwin, kaiser, gaussian, taylor

warnings.filterwarnings("ignore")
import s7_common as S

HERE = S.HERE
FREQS = [500.0, 750.0, 1000.0, 1500.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0]


def fmt(x, nd=2):
    if x is None:
        return ""
    if isinstance(x, float) and np.isnan(x):
        return "nan"
    return f"{x:.{nd}f}" if isinstance(x, float) else str(x)


# ---------------------------------------------------------------------------
def part1(cat):
    rows = []
    print("=" * 100)
    print("PART 1  window sweep  [L2/numpy]  (BW = -6 dB full angle; SLL peak; DI 3-D; WNG_norm re uniform)")
    print("=" * 100)
    for name, w in cat.items():
        for f in FREQS:
            m = S.metrics(f, w)
            if not m["peak_at_0"]:
                raise SystemExit(f"FAIL: peak not at 0 deg for {name} @ {f} Hz")
            if not m["bw6_gt_bw3"]:
                raise SystemExit(f"FAIL: BW(-6) <= BW(-3) for {name} @ {f} Hz")
            rows.append({"window": name, "freq_hz": int(f), **m})
    # negative controls (task-mandated)
    u1k = [r for r in rows if r["window"] == "uniform" and r["freq_hz"] == 1000][0]
    d1k = [r for r in rows if r["window"] == "dolph20_frozen" and r["freq_hz"] == 1000][0]
    d2k = [r for r in rows if r["window"] == "dolph20_frozen" and r["freq_hz"] == 2000][0]
    if abs(u1k["sll_db"] - (-13.26)) > 0.3:
        raise SystemExit(f"NEGATIVE CONTROL FAIL: uniform SLL@1k = {u1k['sll_db']:.3f}")
    if abs(d1k["sll_db"] + 20.0) > 0.05 or abs(d2k["sll_db"] + 20.0) > 0.05:
        raise SystemExit("NEGATIVE CONTROL FAIL: Dolph-20 SLL != -20.00 dB")
    print(f"  negative controls: uniform SLL@1k = {u1k['sll_db']:.2f} dB (expect ~-13.3), "
          f"Dolph-20 SLL@1k/2k = {d1k['sll_db']:.2f}/{d2k['sll_db']:.2f} dB (expect -20.00)  -> PASS")
    print()
    hdr = (f"{'window':<18}{'f':>6}{'BW6':>8}{'BW3':>8}{'SLL':>8}{'edge':>5}{'SLLint':>8}{'DI':>7}{'WNGn':>7}"
           f"{'WNGa':>7}{'att30':>7}{'att90':>7}")
    print(hdr)
    for r in rows:
        print(f"{r['window']:<18}{r['freq_hz']:>6}{r['bw6_deg']:>8.2f}{r['bw3_deg']:>8.2f}"
              f"{fmt(r['sll_db']):>8}{('E' if r['sll_at_edge'] else ''):>5}{fmt(r['sll_interior_db']):>8}{r['di_db']:>7.2f}"
              f"{r['wng_norm_db']:>7.2f}{r['wng_abs_db']:>7.2f}{r['att30_db']:>7.2f}{r['att90_db']:>7.2f}")
    out = os.path.join(HERE, "s7_windows_sweep.csv")
    with open(out, "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(["window", "freq_hz", "BW6dB_full_deg", "BW3dB_full_deg", "peak_SLL_dB", "sll_at_edge",
                     "interior_SLL_dB", "DI_dB", "WNG_norm_dB_re_uniform", "WNG_abs_dB", "att30_dB", "att90_dB",
                     "peak_at_0", "L_grade"])
        for r in rows:
            wr.writerow([r["window"], r["freq_hz"], f"{r['bw6_deg']:.3f}", f"{r['bw3_deg']:.3f}",
                         fmt(r["sll_db"], 3), r["sll_at_edge"], fmt(r["sll_interior_db"], 3), f"{r['di_db']:.3f}",
                         f"{r['wng_norm_db']:.3f}", f"{r['wng_abs_db']:.3f}", f"{r['att30_db']:.3f}",
                         f"{r['att90_db']:.3f}", r["peak_at_0"], "L2/numpy"])
    print(f"\n[CSV] {out}\n")
    return rows


# ---------------------------------------------------------------------------
def candidate_family(cat):
    fam = {}
    for name, w in cat.items():
        fam[name] = w
    for at in np.arange(20.0, 120.0 + 1e-9, 2.5):
        fam[f"dolph{at:g}"] = S.w_norm(chebwin(S.N, at))
    for b in np.arange(0.0, 30.0 + 1e-9, 0.5):
        fam[f"kaiser_b{b:g}"] = S.w_norm(kaiser(S.N, b))
    for sg in np.arange(0.8, 12.0 + 1e-9, 0.2):
        fam[f"gauss_s{sg:.1f}"] = S.w_norm(gaussian(S.N, sg))
    for at in np.arange(20.0, 50.0 + 1e-9, 5.0):
        fam[f"taylor{at:g}_nbar4"] = S.w_norm(taylor(S.N, nbar=4, sll=at, norm=True))
    for k, v in fam.items():
        if not S.is_symmetric(v, 1e-10):
            raise RuntimeError(f"candidate {k} not centre-symmetric")
    return fam


def band_freqs(lo, hi, n):
    return list(np.geomspace(lo, hi, n))


def part2(cat):
    print("=" * 100)
    print("PART 2  per-sub-band constant-beam-width study  [L2/numpy]  (implemented split 1.5k/3k/6k)")
    print("=" * 100)
    fam = candidate_family(cat)
    names = list(fam.keys())
    f_sb0 = band_freqs(1000.0, 1500.0, 5)      # only the 1k-1.5k part of SB0 matters for the 1-6k flatness
    f_sb1 = band_freqs(1500.0, 3000.0, 7)
    f_sb2 = band_freqs(3000.0, 6000.0, 7)

    w_sb0 = cat["dolph20_frozen"]
    bw_sb0 = np.array([S.bw_full(S.pattern_db(f, w_sb0), S.ANG) for f in f_sb0])

    # precompute per-candidate BW arrays for SB1 / SB2 + per-band cost metrics
    bw1 = np.array([[S.bw_full(S.pattern_db(f, fam[n]), S.ANG) for f in f_sb1] for n in names])
    bw2 = np.array([[S.bw_full(S.pattern_db(f, fam[n]), S.ANG) for f in f_sb2] for n in names])
    wng = np.array([S.wng_norm_db(fam[n]) for n in names])
    att30_2k = np.array([S.att_db(30.0, 2000.0, fam[n]) for n in names])
    att30_4k = np.array([S.att_db(30.0, 4000.0, fam[n]) for n in names])

    gmax = np.maximum(bw_sb0.max(), np.maximum(bw1.max(1)[:, None], bw2.max(1)[None, :]))
    gmin = np.minimum(bw_sb0.min(), np.minimum(bw1.min(1)[:, None], bw2.min(1)[None, :]))
    obj = gmax - gmin

    designs = {
        "A_unconstrained": np.ones_like(obj, dtype=bool),
        "B_wng_ge_-3dB": (wng[:, None] >= -3.0) & (wng[None, :] >= -3.0),
        "C_table9_att30_grade1": (att30_2k[:, None] >= 20.0) & (att30_4k[None, :] >= 22.0),
    }

    # trade curve: flatness achievable vs per-band WNG_norm floor
    all_bw_sb0 = bw_sb0
    trade = []
    for floor in (0.0, -0.5, -1.0, -2.0, -3.0, -4.0, -5.0, -6.0):
        mask = (wng[:, None] >= floor) & (wng[None, :] >= floor)
        o = np.where(mask, obj, np.inf)
        if not np.isfinite(o.min()):
            continue
        i1, i2 = np.unravel_index(int(np.argmin(o)), o.shape)
        trade.append((floor, float(o.min()), names[i1], names[i2], float(wng[i1]), float(wng[i2]),
                      float(S.di_db(2000.0, fam[names[i1]])), float(S.di_db(4000.0, fam[names[i2]]))))
    print("  TRADE CURVE  per-band WNG_norm floor -> best achievable max-min over 1-6k (SB0 fixed Dolph-20):")
    print(f"    {'floor dB':>9}{'max-min deg':>13}  {'SB1 window':<16}{'SB2 window':<16}{'WNG1':>7}{'WNG2':>7}{'DI@2k':>7}{'DI@4k':>7}")
    for t in trade:
        print(f"    {t[0]:>9.1f}{t[1]:>13.2f}  {t[2]:<16}{t[3]:<16}{t[4]:>7.2f}{t[5]:>7.2f}{t[6]:>7.2f}{t[7]:>7.2f}")
    print()
    with open(os.path.join(HERE, "s7_constbw_wng_tradecurve.csv"), "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(["WNG_norm_floor_dB_per_band", "best_max_minus_min_1k-6k_deg", "SB1_window", "SB2_window",
                     "WNG_norm_SB1_dB", "WNG_norm_SB2_dB", "DI_SB1_at_2k_dB", "DI_SB2_at_4k_dB", "L_grade"])
        for t in trade:
            wr.writerow([f"{t[0]:.1f}", f"{t[1]:.3f}", t[2], t[3], f"{t[4]:.3f}", f"{t[5]:.3f}", f"{t[6]:.3f}",
                         f"{t[7]:.3f}", "L2/numpy"])

    # reference: fixed full-band windows flatness over the same 1-6k sample set
    all_f = f_sb0 + f_sb1 + f_sb2
    fixed_rows = []
    for name, w in cat.items():
        bws = np.array([S.bw_full(S.pattern_db(f, w), S.ANG) for f in all_f])
        fixed_rows.append((name, bws.max(), bws.min(), bws.max() - bws.min(), bws[0]))
    ref_flat = [r for r in fixed_rows if r[0] == "dolph20_frozen"][0]
    print(f"  reference fixed Dolph-20 over 1-6k: max {ref_flat[1]:.2f}  min {ref_flat[2]:.2f}  "
          f"max-min {ref_flat[3]:.2f} deg")
    print(f"  analytic floor (octave bands, BW ~ lambda): ~BW(1k)/2 = {bw_sb0[0]/2:.2f} deg\n")

    out_rows = []
    summary = {}
    for dname, mask in designs.items():
        o = np.where(mask, obj, np.inf)
        best = o.min()
        cand = np.argwhere(o <= best + 0.05)              # near-optimal set (within 0.05 deg)
        # tie-break 1: smallest RMS deviation of BW from the global mid-point (true "constant BW" sense)
        # tie-break 2: highest WNG sum (cheapest)
        mid = 0.5 * (gmax[cand[:, 0], cand[:, 1]] + gmin[cand[:, 0], cand[:, 1]])
        rms = np.array([np.sqrt(np.mean((np.concatenate([bw_sb0, bw1[i], bw2[j]]) - m0) ** 2))
                        for (i, j), m0 in zip(cand, mid)])
        keep = cand[rms <= rms.min() + 0.05]
        cost = np.array([wng[i] + wng[j] for i, j in keep])
        i1, i2 = keep[int(np.argmax(cost))]
        n1, n2 = names[i1], names[i2]
        gM, gm = float(gmax[i1, i2]), float(gmin[i1, i2])
        summary[dname] = dict(sb1=n1, sb2=n2, gmax=gM, gmin=gm, flat=gM - gm)
        print(f"  DESIGN {dname}: SB0=dolph20_frozen  SB1={n1}  SB2={n2}  ->  "
              f"BW range {gm:.2f}..{gM:.2f} deg, max-min = {gM-gm:.2f} deg "
              f"(vs fixed Dolph-20 {ref_flat[3]:.2f}; improvement {ref_flat[3]-(gM-gm):.2f} deg)")
        for band, fl, wn in (("SB0", f_sb0, "dolph20_frozen"), ("SB1", f_sb1, n1), ("SB2", f_sb2, n2)):
            w = fam[wn]
            for f in fl:
                m = S.metrics(f, w)
                out_rows.append({"design": dname, "band": band, "window": wn, "freq_hz": round(f, 1), **m})
            # band summary print
            ftab = {"SB0": 1000.0, "SB1": 2000.0, "SB2": 4000.0}[band]
            mt = S.metrics(ftab, w)
            print(f"      {band:<4}{wn:<20} BW({fl[0]:.0f})={S.bw_full(S.pattern_db(fl[0], w)):.2f}  "
                  f"BW({fl[-1]:.0f})={S.bw_full(S.pattern_db(fl[-1], w)):.2f}  | @{ftab:.0f}Hz: DI={mt['di_db']:.2f} "
                  f"WNGn={mt['wng_norm_db']:.2f} SLL={fmt(mt['sll_db'])} att30={mt['att30_db']:.2f} dB")
        print()

    out = os.path.join(HERE, "s7_constbw_subband_design.csv")
    with open(out, "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(["design", "band", "window", "freq_hz", "BW6dB_full_deg", "BW3dB_full_deg", "peak_SLL_dB",
                     "sll_at_edge", "DI_dB", "WNG_norm_dB_re_uniform", "WNG_abs_dB", "att30_dB", "att90_dB",
                     "L_grade"])
        for r in out_rows:
            wr.writerow([r["design"], r["band"], r["window"], r["freq_hz"], f"{r['bw6_deg']:.3f}",
                         f"{r['bw3_deg']:.3f}", fmt(r["sll_db"], 3), r["sll_at_edge"], f"{r['di_db']:.3f}",
                         f"{r['wng_norm_db']:.3f}", f"{r['wng_abs_db']:.3f}", f"{r['att30_db']:.3f}",
                         f"{r['att90_db']:.3f}", "L2/numpy"])
    print(f"[CSV] {out}")

    out2 = os.path.join(HERE, "s7_constbw_fixedwindow_flatness.csv")
    with open(out2, "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(["window_fullband", "BW_max_1k-6k_deg", "BW_min_1k-6k_deg", "max_minus_min_deg",
                     "BW_1k_deg", "L_grade"])
        for r in fixed_rows:
            wr.writerow([r[0], f"{r[1]:.3f}", f"{r[2]:.3f}", f"{r[3]:.3f}", f"{r[4]:.3f}", "L2/numpy"])
        for dname, s in summary.items():
            wr.writerow([f"DESIGN_{dname}(SB1={s['sb1']},SB2={s['sb2']})", f"{s['gmax']:.3f}",
                         f"{s['gmin']:.3f}", f"{s['flat']:.3f}", f"{bw_sb0[0]:.3f}", "L2/numpy"])
    print(f"[CSV] {out2}\n")

    # dump chosen weights for traceability
    out3 = os.path.join(HERE, "s7_constbw_chosen_weights.csv")
    with open(out3, "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(["design", "band", "window"] + [f"w_c{c}" for c in range(8)])
        for dname, s in summary.items():
            for band, wn in (("SB0", "dolph20_frozen"), ("SB1", s["sb1"]), ("SB2", s["sb2"])):
                wr.writerow([dname, band, wn] + [f"{v:.6f}" for v in fam[wn][:8]])
    print(f"[CSV] {out3}\n")
    return summary, ref_flat


def main():
    S.assert_anchors()
    cat = S.window_catalog()
    part1(cat)
    part2(cat)
    print("DONE s7_windows_sweep. All numbers [L2/numpy]; isotropic point-source array factor; not measured.")


if __name__ == "__main__":
    main()
