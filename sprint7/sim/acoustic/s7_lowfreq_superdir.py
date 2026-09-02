#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S7 / B4  -- low-frequency directivity: what the algorithm layer can / cannot do on the 825 mm aperture.
L-grade: [L2/numpy] for every simulated number; the L/lambda table is [L3/closed-form].

MODEL / CONVENTIONS: s7_common.py (N=16, d=55 mm, isotropic point sources, far-field array factor,
centre-symmetric real weights, c=343 m/s; BW = -6 dB FULL angle; WNG_norm re uniform (uniform = 0 dB),
WNG_abs = m3 convention (uniform = +12.04 dB); DI closed form 3-D).

SUPERDIRECTIVE WEIGHTS (same formula as sprint3/audit/m3_numpy_superdir_8pair.py and the two MATLAB
tracks of matlab_verify_m3_superdir_8pair.md):
    Gamma_ij = sinc(k |x_i - x_j|)   (3-D isotropic diffuse noise coherence)
    w = (Gamma + eps I)^-1 a / (a^T (Gamma + eps I)^-1 a),   a = ones (broadside)
Solved TWICE per cell: (i) 16 free weights, (ii) 8 free weights under the A/B-pair constraint
w_n = w_{15-n} (reduced 8x8 system). The two must agree to machine precision (the MVDR optimum is
centre-symmetric because Gamma is centro-symmetric and a is symmetric) -- asserted per cell.

ANCHORS (raise = stop):
    s7_common.assert_anchors()  (Dolph-20 BW@1k 29.269, BW@2k 14.515, SLL -20.00, uniform -13.15 ...)
    m3 tri-track values (sprint3/audit/m3_numpy_superdir_d55.csv): 1 kHz eps=0.3 -> BW 24.96 deg,
    WNG_abs 10.94 dB; eps=0.01 -> BW 22.87 deg, WNG_abs 4.57 dB  (tolerance 0.02).

ASSUMPTION (declared, not established): "acceptable" robustness floor WNG_norm >= -10 dB
(i.e. WNG_abs >= +2.04 dB). This is an assumption for framing only; the real limit is set by
element amplitude/phase scatter and must come from M2 Monte-Carlo + measurement.

OUTPUT: s7_lowfreq_superdir.csv (table rows), s7_lowfreq_eps_scan.csv (fine eps scan per frequency),
        console: physical-boundary table and the cross-check against the [L3] statement in
        deliverables/algorithm_validation/EXP_COMPET_BEAM_VS_FREQ.md:5
        ("1k 距超指向天花板仅 1.9dB 且需 WNG=-43dB").
"""
import os
import csv
import warnings
import numpy as np

warnings.filterwarnings("ignore")
import s7_common as S

HERE = S.HERE
FREQS = [250.0, 500.0, 750.0, 1000.0]
EPS_TABLE = [1.0, 0.3, 0.1, 0.03, 0.01]
EPS_QUASI0 = 1e-8
WNG_NORM_FLOOR_ASSUMED = -10.0     # dB, ASSUMPTION
A = np.ones(S.N)
S_PAIR = np.zeros((S.N, 8))
for c in range(8):
    S_PAIR[c, c] = 1.0
    S_PAIR[S.N - 1 - c, c] = 1.0


def mvdr16(f, eps):
    G = S.gamma_sinc(f) + eps * np.eye(S.N)
    v = np.linalg.solve(G, A)
    return v / (A @ v)


def mvdr8pair(f, eps):
    G = S.gamma_sinc(f) + eps * np.eye(S.N)
    Gr = S_PAIR.T @ G @ S_PAIR
    ar = S_PAIR.T @ A
    v = np.linalg.solve(Gr, ar)
    v = v / (ar @ v)
    return S_PAIR @ v


def fmt(x, nd=2):
    if isinstance(x, float) and np.isnan(x):
        return "nan"
    return f"{x:.{nd}f}"


def main():
    S.assert_anchors()
    cat = S.window_catalog()
    w_uni = cat["uniform"]
    w_d20 = cat["dolph20_frozen"]

    # ---- m3 anchor (superdirective formula reproduces the tri-track numbers) ----
    for eps, bw_ref, wng_ref in ((0.3, 24.96, 10.94), (0.01, 22.87, 4.57)):
        w = mvdr16(1000.0, eps)
        m = S.metrics(1000.0, w)
        if abs(m["bw6_deg"] - bw_ref) > 0.02 or abs(m["wng_abs_db"] - wng_ref) > 0.02:
            raise SystemExit(f"m3 ANCHOR FAIL @1k eps={eps}: BW {m['bw6_deg']:.3f} (ref {bw_ref}), "
                             f"WNG_abs {m['wng_abs_db']:.3f} (ref {wng_ref}). STOP.")
    print("m3 tri-track anchor (1k eps=0.3 -> 24.96 deg / 10.94 dB ; eps=0.01 -> 22.87 / 4.57): PASS\n")

    # ---- physical boundary table [L3] ----
    print("=" * 96)
    print("PHYSICAL BOUNDARY  [L3 closed form]  aperture L = 0.825 m")
    print("=" * 96)
    print(f"{'f Hz':>6}{'lambda m':>10}{'L/lambda':>10}{'d/lambda':>10}{'BW_uniform':>12}{'BW_dolph20':>12}")
    for f in FREQS:
        lam = S.C / f
        print(f"{f:>6.0f}{lam:>10.4f}{S.L_APERTURE/lam:>10.3f}{S.D/lam:>10.3f}"
              f"{S.bw_full(S.pattern_db(f, w_uni)):>12.2f}{S.bw_full(S.pattern_db(f, w_d20)):>12.2f}")
    print()

    # ---- main table ----
    rows = []
    print("=" * 120)
    print("B4 TABLE  [L2/numpy]   (WNGn re uniform; WNGa = m3 convention; att30/att90 positive dB)")
    print("=" * 120)
    hdr = (f"{'f':>5}{'design':<20}{'eps':>8}{'BW6':>8}{'BW3':>8}{'SLL':>8}{'DI':>7}{'WNGn':>8}{'WNGa':>8}"
           f"{'att30':>7}{'att90':>7}{'pair=16?':>9}")
    print(hdr)
    for f in FREQS:
        cells = [("uniform", None, w_uni), ("dolph20_frozen", None, w_d20)]
        for eps in EPS_TABLE + [EPS_QUASI0]:
            w16 = mvdr16(f, eps)
            w8 = mvdr8pair(f, eps)
            pair_ok = float(np.max(np.abs(w16 - w8)) / np.max(np.abs(w16)))
            tag = "mvdr_sym8" if eps != EPS_QUASI0 else "mvdr_quasi_unconstr"
            cells.append((tag, eps, w16, pair_ok))
        for cell in cells:
            name, eps, w = cell[0], cell[1], cell[2]
            pair_ok = cell[3] if len(cell) > 3 else 0.0
            m = S.metrics(f, w)
            unstable = (pair_ok > 1e-6) or (not m["peak_at_0"]) or (abs(w.sum() - 1.0) > 1e-6 and eps is not None)
            if eps is not None and pair_ok > 1e-6 and eps > 1e-6:
                raise SystemExit(f"8-pair vs 16 MVDR mismatch {pair_ok:.2e} at f={f} eps={eps}. STOP.")
            r = {"freq_hz": int(f), "design": name, "eps": eps, **m, "pair_vs_16_reldiff": pair_ok,
                 "numerically_unstable": unstable, "w8": list(w[:8])}
            rows.append(r)
            print(f"{f:>5.0f}{name:<20}{('' if eps is None else f'{eps:g}'):>8}{m['bw6_deg']:>8.2f}{m['bw3_deg']:>8.2f}"
                  f"{fmt(m['sll_db']):>8}{m['di_db']:>7.2f}{m['wng_norm_db']:>8.2f}{m['wng_abs_db']:>8.2f}"
                  f"{m['att30_db']:>7.2f}{m['att90_db']:>7.2f}{pair_ok:>9.1e}{'  UNSTABLE' if unstable else ''}")
        print()

    # ---- fine eps scan: "narrowest BW subject to WNG_norm >= floor" + unconstrained limit ----
    eps_scan = np.geomspace(1e-8, 10.0, 241)
    scan_rows = []
    boundary = []
    print("=" * 96)
    print(f"ALGORITHM-LAYER BOUNDARY  [L2/numpy]  (assumed floor WNG_norm >= {WNG_NORM_FLOOR_ASSUMED:.0f} dB)")
    print("=" * 96)
    print(f"{'f':>6}{'BW_uni':>9}{'BW_d20':>9}{'BW@floor':>10}{'eps@floor':>11}{'DI@floor':>9}"
          f"{'BW_eps->0':>11}{'WNGn_eps->0':>12}{'DI_eps->0':>10}")
    for f in FREQS:
        bws, wns, was, dis, slls = [], [], [], [], []
        for eps in eps_scan:
            w = mvdr16(f, eps)
            m = S.metrics(f, w)
            bws.append(m["bw6_deg"]); wns.append(m["wng_norm_db"]); was.append(m["wng_abs_db"])
            dis.append(m["di_db"]); slls.append(m["sll_db"])
            scan_rows.append([int(f), f"{eps:.4e}", f"{m['bw6_deg']:.3f}", f"{m['wng_norm_db']:.3f}",
                              f"{m['wng_abs_db']:.3f}", f"{m['di_db']:.3f}", fmt(m["sll_db"], 3), m["peak_at_0"]])
        bws, wns, was, dis = map(np.array, (bws, wns, was, dis))
        ok = wns >= WNG_NORM_FLOOR_ASSUMED
        i_floor = int(np.argmin(np.where(ok, bws, np.inf)))
        b_uni = S.bw_full(S.pattern_db(f, w_uni))
        b_d20 = S.bw_full(S.pattern_db(f, w_d20))
        boundary.append(dict(f=f, bw_uni=b_uni, bw_d20=b_d20, bw_floor=bws[i_floor], eps_floor=eps_scan[i_floor],
                             di_floor=dis[i_floor], bw_0=bws[0], wng_0=wns[0], di_0=dis[0], di_uni=S.di_db(f, w_uni),
                             di_d20=S.di_db(f, w_d20)))
        print(f"{f:>6.0f}{b_uni:>9.2f}{b_d20:>9.2f}{bws[i_floor]:>10.2f}{eps_scan[i_floor]:>11.2e}{dis[i_floor]:>9.2f}"
              f"{bws[0]:>11.2f}{wns[0]:>12.1f}{dis[0]:>10.2f}")
        if f == 1000.0:
            # cross-check of the [L3] statement "1k: 1.9 dB from the superdirective ceiling, needs WNG = -43 dB"
            di_gain_vs_d20 = dis - S.di_db(f, w_d20)
            di_gain_vs_uni = dis - S.di_db(f, w_uni)
            j43a = int(np.argmin(np.abs(was + 43.0)))
            j43n = int(np.argmin(np.abs(wns + 43.0)))
            print()
            print("  cross-check vs EXP_COMPET_BEAM_VS_FREQ.md:5 [L3] '1k ceiling 1.9 dB / WNG -43 dB':")
            print(f"    DI(uniform)={S.di_db(f, w_uni):.2f}  DI(dolph20)={S.di_db(f, w_d20):.2f}  "
                  f"DI(eps->0)={dis[0]:.2f} dB  -> max DI gain over Dolph-20 = {di_gain_vs_d20[0]:.2f} dB, "
                  f"over uniform = {di_gain_vs_uni[0]:.2f} dB, at WNG_norm={wns[0]:.1f} dB / WNG_abs={was[0]:.1f} dB")
            print(f"    at WNG_abs ~ -43 dB (eps={eps_scan[j43a]:.1e}): BW={bws[j43a]:.2f} deg, DI gain vs Dolph-20 = "
                  f"{di_gain_vs_d20[j43a]:.2f} dB, vs uniform = {di_gain_vs_uni[j43a]:.2f} dB")
            print(f"    at WNG_norm ~ -43 dB (eps={eps_scan[j43n]:.1e}): BW={bws[j43n]:.2f} deg, DI gain vs Dolph-20 = "
                  f"{di_gain_vs_d20[j43n]:.2f} dB, vs uniform = {di_gain_vs_uni[j43n]:.2f} dB")
            # DI gain of 1.9 dB over Dolph-20: where is it and what WNG?
            j19 = int(np.argmin(np.abs(di_gain_vs_d20 - 1.9)))
            print(f"    DI gain = +1.9 dB over Dolph-20 reached at eps={eps_scan[j19]:.1e}: BW={bws[j19]:.2f} deg, "
                  f"WNG_norm={wns[j19]:.1f} dB, WNG_abs={was[j19]:.1f} dB")
            print()

    # ---- CSVs ----
    out = os.path.join(HERE, "s7_lowfreq_superdir.csv")
    with open(out, "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(["freq_hz", "design", "eps", "BW6dB_full_deg", "BW3dB_full_deg", "peak_SLL_dB", "sll_at_edge",
                     "interior_SLL_dB", "DI_dB", "WNG_norm_dB_re_uniform", "WNG_abs_dB", "att30_dB", "att90_dB",
                     "peak_at_0", "pair8_vs_16_reldiff", "numerically_unstable"] + [f"w_c{c}" for c in range(8)]
                    + ["L_grade"])
        for r in rows:
            wr.writerow([r["freq_hz"], r["design"], ("" if r["eps"] is None else f"{r['eps']:g}"),
                         f"{r['bw6_deg']:.3f}", f"{r['bw3_deg']:.3f}", fmt(r["sll_db"], 3), r["sll_at_edge"],
                         fmt(r["sll_interior_db"], 3), f"{r['di_db']:.3f}", f"{r['wng_norm_db']:.3f}", f"{r['wng_abs_db']:.3f}",
                         f"{r['att30_db']:.3f}", f"{r['att90_db']:.3f}", r["peak_at_0"],
                         f"{r['pair_vs_16_reldiff']:.2e}", r["numerically_unstable"]]
                        + [f"{v:.6g}" for v in r["w8"]] + ["L2/numpy"])
    print(f"[CSV] {out}")
    out2 = os.path.join(HERE, "s7_lowfreq_eps_scan.csv")
    with open(out2, "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(["freq_hz", "eps", "BW6dB_full_deg", "WNG_norm_dB", "WNG_abs_dB", "DI_dB", "peak_SLL_dB", "peak_at_0"])
        wr.writerows(scan_rows)
    print(f"[CSV] {out2}")
    out3 = os.path.join(HERE, "s7_lowfreq_boundary.csv")
    with open(out3, "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(["freq_hz", "lambda_m", "L_over_lambda", "BW_uniform_deg", "BW_dolph20_deg",
                     f"BW_min_at_WNGnorm_ge_{WNG_NORM_FLOOR_ASSUMED:.0f}dB_deg(ASSUMED_floor)", "eps_at_floor",
                     "DI_at_floor_dB", "BW_eps_to_0_deg", "WNG_norm_eps_to_0_dB", "DI_eps_to_0_dB",
                     "DI_uniform_dB", "DI_dolph20_dB", "L_grade"])
        for b in boundary:
            wr.writerow([int(b["f"]), f"{S.C/b['f']:.4f}", f"{S.L_APERTURE*b['f']/S.C:.3f}", f"{b['bw_uni']:.3f}",
                         f"{b['bw_d20']:.3f}", f"{b['bw_floor']:.3f}", f"{b['eps_floor']:.2e}", f"{b['di_floor']:.3f}",
                         f"{b['bw_0']:.3f}", f"{b['wng_0']:.2f}", f"{b['di_0']:.3f}", f"{b['di_uni']:.3f}",
                         f"{b['di_d20']:.3f}", "L2/numpy (L/lambda: L3)"])
    print(f"[CSV] {out3}\n")
    print("DONE s7_lowfreq_superdir. All numbers [L2/numpy]; isotropic array factor; WNG floor is an ASSUMPTION.")


if __name__ == "__main__":
    main()
