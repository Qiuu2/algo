#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S7 / B2 (task 6) -- numerical proof that, once per-channel FRACTIONAL DELAYS (near-field focusing, v2)
exist, "permute the weight index" is NO LONGER equivalent to "permute the TX slot".
L-grade: [L2/numpy]. Nothing measured.

WHY THIS EXISTS: EXP_CHMAP_AB.md section 8 and sprint6/dsp/audio/m1_cces_project/src/m1_loopback_tdm.c:385-387
state the boundary in words: "*** BROADSIDE v1 ONLY *** -- once v2 adds per-channel FRAC-DELAY focusing,
the delay is ALSO position-dependent and must be permuted/re-derived too (a scalar-weight permute no
longer suffices)."  This script puts numbers on it.

MODEL: near-field spherical-wave sum, IDENTICAL to sprint5/efficacy_sim/focus_sim.py:
    p(y,z) = sum_n w_n /(4 pi r_n) exp(-j k (r_n - c tau_n)),  r_n = sqrt((y-x_n)^2 + z^2)
    focusing delays for on-axis focal point F:  tau_n = (r_n(F) - min_m r_m(F))/c   (symmetric)
    weights = frozen Dolph -20 dB table (dolph_w8_q15.csv float column), c=343, N=16, d=55 mm.

CHANNEL <-> PHYSICAL MAPPING [L1 rig, m1_loopback_tdm.c:380-398]: TX slot c drives physical RANK perm[c]
(rank 0 = edge pair {0,15} ... rank 7 = centre pair {7,8}), perm = {4,5,6,7,0,1,2,3} (an involution).
Cases evaluated (per (f, F) cell):
    REF     : physical rank r gets (w[r], tau[r])                       -- the intended focused beam
    TXPERM  : DSP permutes the whole slot (weight AND delay): rank r gets (w[r], tau[r]) == REF
    WPERM   : DSP permutes ONLY the weight index (the v1 fix), delays stay indexed by slot:
              rank r gets (w[r], tau[perm[r]])  -> outer pairs receive the small inner delays and vice versa
    NOFIX   : nothing permuted (A-arm): rank r gets (w[perm[r]], tau[perm[r]])
    BROADSIDE control (tau = 0 for all): REF == TXPERM == WPERM must hold to machine precision
              (this is the v1 equivalence claimed in EXP_CHMAP_AB.md) -- asserted.

ANCHORS (raise = stop):
    s7_common.assert_anchors()  (far-field Dolph-20 BW@1k / @2k / SLL)
    REF focal gain must reproduce sprint5/efficacy_sim/results_numpy.json per_cell focal_gain_dB
    for every (f,F) cell used here, within 0.01 dB (ties this script to the frozen S5 numbers).
    Broadside control max|dp| < 1e-12 relative.

METRICS per cell: focal gain (REF/WPERM/NOFIX vs unfocused broadside at F), SPL loss at F (WPERM-REF),
lateral -6 dB width at z=F, axial peak location (z of max |p| on axis, 0.3F..3F),
angular pattern on the arc r=F: -6 dB angular width and max |P_WPERM - P_REF| within +/-30 deg.
OUTPUT: s7_focus_chmap_equiv.csv
"""
import os
import csv
import json
import warnings
import numpy as np

warnings.filterwarnings("ignore")
import s7_common as S

HERE = S.HERE
JSON_S5 = os.path.join(S.REPO, "sprint5", "efficacy_sim", "results_numpy.json")
PERM = np.array([4, 5, 6, 7, 0, 1, 2, 3])          # slot c -> physical rank perm[c]
CELLS = [(2000.0, 2.0), (4000.0, 2.0), (4000.0, 3.0), (6000.0, 2.0), (6000.0, 3.0), (6000.0, 5.0)]

assert np.all(PERM[PERM] == np.arange(8)), "perm must be an involution (slot<->rank swap of halves)"


def rank_of_elem(n):
    return n if n < 8 else 15 - n


def tau_focus(F):
    r = np.sqrt(S.X ** 2 + F ** 2)
    return (r - r.min()) / S.C


def pressure(y, z, f, w16, tau16):
    k = 2 * np.pi * f / S.C
    y = np.asarray(y, float); z = np.asarray(z, float)
    shp = np.broadcast(y, z).shape
    yb = np.broadcast_to(y, shp); zb = np.broadcast_to(z, shp)
    p = np.zeros(shp, dtype=complex)
    for n in range(S.N):
        rn = np.maximum(np.sqrt((yb - S.X[n]) ** 2 + zb ** 2), 1e-9)
        p = p + w16[n] / (4 * np.pi * rn) * np.exp(-1j * k * (rn - S.C * tau16[n]))
    return p


def spl(p):
    return 20 * np.log10(np.abs(p) + 1e-300)


def build_case(case, w8, tau8):
    """Return per-element (w16, tau16) for a case. w8/tau8 indexed by physical rank."""
    w16 = np.zeros(S.N); t16 = np.zeros(S.N)
    for n in range(S.N):
        r = rank_of_elem(n)
        if case in ("REF", "TXPERM"):
            w16[n], t16[n] = w8[r], tau8[r]
        elif case == "WPERM":
            w16[n], t16[n] = w8[r], tau8[PERM[r]]
        elif case == "NOFIX":
            w16[n], t16[n] = w8[PERM[r]], tau8[PERM[r]]
        else:
            raise ValueError(case)
    return w16, t16


def width6_lateral(f, F, w16, t16):
    y = np.linspace(-F, F, 40001)
    db = spl(pressure(y, F, f, w16, t16))
    ipk = int(np.argmax(db)); thr = db[ipk] - 6
    iR = ipk
    while iR < len(db) - 1 and db[iR] > thr:
        iR += 1
    iL = ipk
    while iL > 0 and db[iL] > thr:
        iL -= 1
    yR = y[-1] if db[iR] > thr else float(np.interp(thr, [db[iR - 1], db[iR]], [y[iR - 1], y[iR]]))
    yL = y[0] if db[iL] > thr else float(np.interp(thr, [db[iL], db[iL + 1]], [y[iL], y[iL + 1]]))
    return float(yR - yL), float(y[ipk])


def axial_peak(f, F, w16, t16):
    z = np.linspace(0.3 * F, 3.0 * F, 30001)
    db = spl(pressure(0.0, z, f, w16, t16))
    return float(z[int(np.argmax(db))])


def arc_pattern(f, F, w16, t16, ang=S.ANG):
    th = np.deg2rad(ang)
    p = pressure(F * np.sin(th), F * np.cos(th), f, w16, t16)
    db = spl(p)
    return db - db.max()


def main():
    S.assert_anchors()
    w8, _ = S.read_w8()
    with open(JSON_S5) as fp:
        s5 = json.load(fp)

    rows = []
    print("=" * 110)
    print("B2 task-6: weight-index permute vs TX-slot permute under per-channel fractional delay  [L2/numpy]")
    print("=" * 110)
    for f, F in CELLS:
        tau8 = tau_focus(F)[:8]                     # rank-indexed (symmetric by construction)
        tau8_ref16 = tau_focus(F)
        assert np.allclose(np.concatenate([tau8, tau8[::-1]]), tau8_ref16)
        cases = {c: build_case(c, w8, tau8) for c in ("REF", "TXPERM", "WPERM", "NOFIX")}
        w_bs = S.expand16(w8); t0 = np.zeros(S.N)

        # --- anchor: REF focal gain == S5 json ---
        p_bs = pressure(0.0, F, f, w_bs, t0)
        fg = {c: float(spl(pressure(0.0, F, f, *cases[c])) - spl(p_bs)) for c in cases}
        fg_s5 = s5["per_cell"][str(int(f))][str(int(F))]["focal_gain_dB"]
        if abs(fg["REF"] - fg_s5) > 0.01:
            raise SystemExit(f"S5 ANCHOR FAIL: REF focal gain {fg['REF']:.4f} vs results_numpy.json {fg_s5} @ {f}/{F}. STOP.")

        # --- TXPERM == REF, and broadside control ---
        yy = np.linspace(-0.6, 0.6, 61); zz = np.linspace(0.5, 3 * F, 61)
        Y, Z = np.meshgrid(yy, zz, indexing="ij")
        d_tx = float(np.max(np.abs(pressure(Y, Z, f, *cases["TXPERM"]) - pressure(Y, Z, f, *cases["REF"]))))
        pref_bs = pressure(Y, Z, f, w_bs, t0)
        w_wp_bs, _ = build_case("WPERM", w8, np.zeros(8))          # tau=0 -> permuting delays does nothing
        d_bs = float(np.max(np.abs(pressure(Y, Z, f, w_wp_bs, t0) - pref_bs)) / np.max(np.abs(pref_bs)))
        if d_tx > 1e-12 * np.max(np.abs(pressure(Y, Z, f, *cases["REF"]))) or d_bs > 1e-12:
            raise SystemExit("EQUIVALENCE CONTROL FAIL (TXPERM!=REF or broadside WPERM!=REF). STOP.")

        # --- metrics ---
        lat = {c: width6_lateral(f, F, *cases[c]) for c in ("REF", "WPERM", "NOFIX")}
        zpk = {c: axial_peak(f, F, *cases[c]) for c in ("REF", "WPERM")}
        arc = {c: arc_pattern(f, F, *cases[c]) for c in ("REF", "WPERM")}
        bw_arc = {c: S.bw_full(arc[c], S.ANG, 6.0) for c in arc}
        m30 = np.abs(S.ANG) <= 30.0
        dmax30 = float(np.max(np.abs(arc["WPERM"][m30] - arc["REF"][m30])))
        pk_ang_wp = float(S.ANG[int(np.argmax(arc["WPERM"]))])
        sll_ref, _ = S.peak_sll(arc["REF"]); sll_wp, _ = S.peak_sll(arc["WPERM"])
        loss = fg["WPERM"] - fg["REF"]
        r = dict(freq_hz=int(f), focal_m=F, focal_gain_REF_dB=fg["REF"], focal_gain_S5_json_dB=fg_s5,
                 focal_gain_WPERM_dB=fg["WPERM"], focal_gain_NOFIX_dB=fg["NOFIX"], spl_loss_at_F_WPERM_minus_REF_dB=loss,
                 lateral_w6_REF_m=lat["REF"][0], lateral_w6_WPERM_m=lat["WPERM"][0], lateral_w6_NOFIX_m=lat["NOFIX"][0],
                 lateral_peak_offset_WPERM_m=lat["WPERM"][1], axial_peak_REF_m=zpk["REF"], axial_peak_WPERM_m=zpk["WPERM"],
                 arc_bw6_REF_deg=bw_arc["REF"], arc_bw6_WPERM_deg=bw_arc["WPERM"], arc_maxdev_pm30_dB=dmax30,
                 arc_peak_angle_WPERM_deg=pk_ang_wp, arc_sll_REF_dB=sll_ref, arc_sll_WPERM_dB=sll_wp,
                 txperm_vs_ref_max_abs_dp=d_tx, broadside_wperm_vs_ref_rel=d_bs)
        rows.append(r)
        print(f"f={f:>5.0f} F={F:.0f}m | focal gain REF {fg['REF']:+.2f} dB (S5 json {fg_s5:+.2f})  WPERM {fg['WPERM']:+.2f}  "
              f"NOFIX {fg['NOFIX']:+.2f}  -> loss WPERM-REF = {loss:+.2f} dB")
        print(f"            | lateral -6dB width @F: REF {lat['REF'][0]:.3f} m  WPERM {lat['WPERM'][0]:.3f} m  "
              f"(x{lat['WPERM'][0]/lat['REF'][0]:.2f}) | axial peak REF {zpk['REF']:.2f} m  WPERM {zpk['WPERM']:.2f} m")
        print(f"            | arc r=F: BW6 REF {bw_arc['REF']:.2f} deg  WPERM {bw_arc['WPERM']:.2f} deg | "
              f"max|dP| (+/-30deg) = {dmax30:.2f} dB | SLL REF {sll_ref:.2f} WPERM {sll_wp:.2f} dB")
        print(f"            | controls: TXPERM==REF max|dp|={d_tx:.1e} ; broadside(tau=0) WPERM==REF rel={d_bs:.1e}")
        print()

    out = os.path.join(HERE, "s7_focus_chmap_equiv.csv")
    keys = list(rows[0].keys())
    with open(out, "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(keys + ["L_grade"])
        for r in rows:
            wr.writerow([(f"{v:.4g}" if isinstance(v, float) else v) for v in r.values()] + ["L2/numpy"])
    print(f"[CSV] {out}")
    print("DONE s7_focus_chmap_equiv. [L2/numpy]; spherical-wave point sources, free field, no element directivity.")


if __name__ == "__main__":
    main()
