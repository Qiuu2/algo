#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PREREQUISITE #2 (CTO-ordered). Sprint 5 / efficacy_sim.
v1 ON-AXIS FOCUSING / DEPTH-ZONING ACOUSTIC EFFICACY SIMULATION -- NUMPY PRIMARY TRACK.

Workflow role: POLICY v1.8 三道关 = GATE 1 SCREENING ONLY. Independent critic + CTO follow.
NO efficacy verdict produced here -- METRICS only; sufficiency judgment belongs to CTO/PRD.

L-grades:
  - spherical-wave near-field sim outputs = [L2/仿真]
  - L^2/lambda closed-form feasibility table = [L3/解析]
  - NO L1 here (no bench / anechoic data in scope).

Authoritative spec: sprint5/efficacy_sim/SIM_PLAN.md
Weights: READ from sprint4/dsp/fira/dolph_w8_q15.csv (float column) -- NOT hardcoded.

DISCIPLINE: validation anchors are computed and asserted FIRST. If broadside BW@1k does
not reproduce ~29.27 deg within ~0.1 deg, the script raises and STOPS before producing any
focusing metric (no unanchored results shipped).
"""
import os
import csv
import json
import numpy as np

# ---------------------------------------------------------------------------
# 0. Locked physical constants & geometry [L1/teardown + DEC-S3-GEOM-01]
# ---------------------------------------------------------------------------
C = 343.0                      # speed of sound m/s (20 C), declared explicitly
N = 16                         # elements
D = 0.055                      # element pitch m (55 mm)
L_APERTURE = (N - 1) * D       # 0.825 m acoustic aperture (NOT box length N*d=0.880)

# centered element positions on the column axis (z-axis), x_n along the array
# x_n = (n - (N-1)/2)*d : -0.4125 .. +0.4125 m
X_N = (np.arange(N) - (N - 1) / 2.0) * D

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
W8_CSV = os.path.join(REPO, "sprint4", "dsp", "fira", "dolph_w8_q15.csv")

FREQS = [500.0, 1000.0, 2000.0, 4000.0, 6000.0]
FOCALS = [2.0, 3.0, 5.0, 8.0, 12.0]

# zone pairs for cross-zone isolation
ZONE_PAIRS = [(3.0, 8.0), (2.0, 5.0)]


# ---------------------------------------------------------------------------
# 1. Read frozen Dolph-Chebyshev -20 dB channel weights (8 half-aperture vals)
# ---------------------------------------------------------------------------
def read_w8_float(path):
    """Read the 8 channel float weights (scipy track-1 column) from the frozen CSV."""
    w8 = [None] * 8
    with open(path, "r") as fp:
        rdr = csv.DictReader(fp)
        for row in rdr:
            c = int(row["ch"])
            w8[c] = float(row["w_float_track1_scipy"])
    if any(v is None for v in w8):
        raise RuntimeError("dolph_w8_q15.csv: missing channel rows")
    return np.array(w8, dtype=float)


def expand_w16(w8):
    """16-element symmetric weight vector = [w0..w7, w7..w0]
    (mirror reproduced physically by A/B series pair, NOT in DSP)."""
    return np.concatenate([w8, w8[::-1]])


W8 = read_w8_float(W8_CSV)
W16 = expand_w16(W8)

# FG1: all 8 channel weights pairwise distinct; symmetric expansion w_n == w_{15-n}
assert len(np.unique(np.round(W8, 12))) == 8, "FG1 FAIL: channel weights not all-distinct"
assert np.allclose(W16, W16[::-1], atol=0.0), "symmetric expansion broken: w_n != w_{15-n}"
assert np.all(W8 <= 1.0 + 1e-12), "weight > 1.0"


# ---------------------------------------------------------------------------
# 2. Far-field array factor (for anchors A1/A3). Matches sweep_d55 /
#    m3_numpy_superdir_8pair conventions: centered positions, theta=0=broadside,
#    BW = -6 dB FULL angle = 2 x half angle (interpolated), normalized dB.
# ---------------------------------------------------------------------------
def array_factor_db_farfield(theta_deg, freq, weights):
    """Far-field normalized array-factor in dB. theta=0 = broadside (axis)."""
    k = 2 * np.pi * freq / C
    st = np.sin(np.deg2rad(theta_deg))
    phase = k * np.outer(st, X_N)            # (n_theta, N)
    af = np.abs((weights * np.exp(1j * phase)).sum(axis=1))
    return 20 * np.log10(af / af.max() + 1e-12)


def bw_neg6_full(P, ang):
    """-6 dB FULL-angle beamwidth (deg), interpolated. Matches bw_neg6 in
    m3_numpy_superdir_8pair.py (symmetric scan -90..90, broadside peak)."""
    i0 = int(np.argmax(P))
    iR = i0
    while iR < len(P) - 1 and P[iR] > -6:
        iR += 1
    iL = i0
    while iL > 0 and P[iL] > -6:
        iL -= 1
    if iR >= len(P) - 1 or iL <= 0:
        return 180.0
    aR = np.interp(-6, [P[iR], P[iR - 1]], [ang[iR], ang[iR - 1]])
    aL = np.interp(-6, [P[iL], P[iL + 1]], [ang[iL], ang[iL + 1]])
    return float(aR - aL)


def peak_sll_db(P, ang):
    """Peak side-lobe level (dB rel main). Matches peak_sll in m3 script."""
    i0 = int(np.argmax(P))
    iR = i0
    while iR < len(P) - 1 and P[iR + 1] <= P[iR]:
        iR += 1
    iL = i0
    while iL > 1 and P[iL - 1] <= P[iL]:
        iL -= 1
    mask = np.ones(len(P), dtype=bool)
    mask[iL:iR + 1] = False
    if not mask.any():
        return -60.0
    return float(np.max(P[mask]))


# ---------------------------------------------------------------------------
# 3. Near-field spherical-wave field model -- the CORE [L2]
#     p(P) = sum_n w_n/(4 pi r_n) * exp(-j k (r_n - c tau_n))
#     field point P = (y_lateral, z_axial); element at (x_n, 0) on the column axis.
#     r_n = sqrt((z - 0)^2 ... ) -- element is on the array axis at coordinate x_n,
#     field point off-axis by lateral y at axial distance z from array center.
# ---------------------------------------------------------------------------
def focusing_delays(focal_dist):
    """On-axis focusing delays tau_n. Focal point F=(y=0, z=focal_dist).
    r_n(F) = sqrt(x_n^2 + focal_dist^2); tau_n = (r_n - min_m r_m)/c >= 0.
    Symmetric automatically: r_n == r_{15-n} => tau_n == tau_{15-n}."""
    r = np.sqrt(X_N ** 2 + focal_dist ** 2)
    return (r - r.min()) / C


def pressure(y, z, freq, weights, tau):
    """Complex pressure at field point(s) P=(y,z). y,z may be arrays (broadcast).
    Element n at array-axis coordinate x_n; distance r_n = sqrt((y)^2 + (z)^2 ...).

    Geometry: the array lies along the x-axis (vertical column), broadside-normal
    propagation is along z. A field point on the broadside axis is (x=0, y=0, z).
    For element n at x=x_n, the field point P at axial z and lateral offset y
    (in the plane containing the array axis) has:
        r_n = sqrt( (P_x - x_n)^2 + z^2 )   with P_x = y  (lateral coord along array axis)
    i.e. we evaluate in the 2-D plane through the array axis: lateral y measured
    along the array-axis direction, axial z perpendicular (broadside-normal)."""
    k = 2 * np.pi * freq / C
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float)
    shp = np.broadcast(y, z).shape
    yb = np.broadcast_to(y, shp)
    zb = np.broadcast_to(z, shp)
    p = np.zeros(shp, dtype=complex)
    for n in range(N):
        rn = np.sqrt((yb - X_N[n]) ** 2 + zb ** 2)
        rn = np.maximum(rn, 1e-9)
        p = p + weights[n] / (4 * np.pi * rn) * np.exp(-1j * k * (rn - C * tau[n]))
    return p


def spl_db(p):
    """20*log10|p| (relative dB; absolute level not modeled)."""
    return 20 * np.log10(np.abs(p) + 1e-300)


# ---------------------------------------------------------------------------
# 4. VALIDATION ANCHORS -- run FIRST, halt on failure
# ---------------------------------------------------------------------------
def run_anchors():
    ang = np.arange(-90.0, 90.0 + 1e-9, 0.01)

    # A1: far-field broadside -6 dB full BW @ 1 kHz must reproduce 29.269 deg
    P_ff = array_factor_db_farfield(ang, 1000.0, W16)
    bw1k_ff = bw_neg6_full(P_ff, ang)

    # A3: peak SLL with Dolph -20 dB weights
    sll = peak_sll_db(P_ff, ang)

    # A2: symmetric-pair equivalence. Build the near-field field two ways and
    # compare over a grid:
    #   (i)  16 independent elements with weights/delays satisfying w_n=w_{15-n},
    #        tau_n=tau_{15-n}  -> use W16 directly (already symmetric).
    #   (ii) 8-pair model: assign each channel c's (w_c, tau_c) to BOTH {c,15-c}.
    focal = 3.0
    tau16 = focusing_delays(focal)             # already symmetric by construction
    # 8-pair reconstruction of the 16-vector:
    tau8 = tau16[:8]
    tau16_from8 = np.concatenate([tau8, tau8[::-1]])
    w16_from8 = expand_w16(W8)
    yy = np.linspace(-0.5, 0.5, 41)
    zz = np.linspace(1.0, 6.0, 51)
    Y, Z = np.meshgrid(yy, zz, indexing="ij")
    p_i = pressure(Y, Z, 2000.0, W16, tau16)
    p_ii = pressure(Y, Z, 2000.0, w16_from8, tau16_from8)
    a2_diff = float(np.max(np.abs(p_i - p_ii)))

    # A1b: near-field far-pushed angular -6dB width converges to far-field BW.
    # Evaluate unfocused (tau=0) pressure on an arc at large radius and convert
    # angular width; just confirm with the far-field model here (A1 already does it).

    print("=" * 64)
    print("VALIDATION ANCHORS (must pass before focusing metrics)")
    print("=" * 64)
    print(f"A1  far-field BW@1k (-6dB full)  = {bw1k_ff:.4f} deg   (target 29.269)")
    print(f"A3  peak SLL                     = {sll:.4f} dB    (target -20.00)")
    print(f"A2  8-pair vs 16-elem max|dp|    = {a2_diff:.3e}    (target ~0)")

    # Halt conditions
    if abs(bw1k_ff - 29.269) > 0.1:
        raise SystemExit(
            f"ANCHOR A1 FAIL: BW@1k = {bw1k_ff:.4f} deg, off target 29.269 by "
            f"{abs(bw1k_ff-29.269):.4f} deg (> 0.1). STOP -- debug before shipping.")
    if abs(sll - (-20.0)) > 0.1:
        raise SystemExit(f"ANCHOR A3 FAIL: SLL = {sll:.4f} dB, off -20.00. STOP.")
    if a2_diff > 1e-9:
        raise SystemExit(f"ANCHOR A2 FAIL: 8-pair equivalence diff {a2_diff:.3e} > 1e-9. STOP.")
    print("ALL ANCHORS PASS -> proceeding to focusing metrics.")
    print()
    return {"A1_farfield_BW_1k_deg": round(bw1k_ff, 6),
            "A3_peak_SLL_dB": round(sll, 6),
            "A2_paired_vs_16elem_max_abs_diff": a2_diff}


# ---------------------------------------------------------------------------
# 5. Near-field feasibility table [L3/解析]  (compute in-script, don't trust table)
# ---------------------------------------------------------------------------
def nearfield_table():
    tbl = {}
    for f in FREQS:
        lam = C / f
        l2lam = L_APERTURE ** 2 / lam        # Fresnel-onset L^2/lambda
        rayleigh = 2 * l2lam                 # Rayleigh distance
        tbl[int(f)] = {
            "lambda_m": round(lam, 6),
            "L_over_lambda": round(L_APERTURE / lam, 6),
            "L2_over_lambda_m": round(l2lam, 6),
            "rayleigh_2L2_over_lambda_m": round(rayleigh, 6),
        }
    return tbl


# ---------------------------------------------------------------------------
# 6. Focusing metrics (a)-(d)
# ---------------------------------------------------------------------------
def focal_gain_db(focal_dist, freq):
    """SPL(at F, focused to F) - SPL(at F, broadside-unfocused). Same weights."""
    tau_focus = focusing_delays(focal_dist)
    tau_zero = np.zeros(N)
    p_focus = pressure(0.0, focal_dist, freq, W16, tau_focus)
    p_broad = pressure(0.0, focal_dist, freq, W16, tau_zero)
    return float(spl_db(p_focus) - spl_db(p_broad))


def axial_zone_depth(focal_dist, freq):
    """-6 dB axial zone depth along on-axis (y=0), focused at focal_dist.
    Returns (z_near, z_far, depth). z_far may be open (capped at search end)."""
    tau_focus = focusing_delays(focal_dist)
    # sweep axial z around the focal point; fine grid, wide enough to bracket
    z_lo = max(0.2, focal_dist * 0.1)
    z_hi = focal_dist * 6.0 + 20.0
    z = np.linspace(z_lo, z_hi, 60001)
    p = pressure(0.0, z, freq, W16, tau_focus)
    db = spl_db(p)
    ipk = int(np.argmax(db))
    pk = db[ipk]
    thr = pk - 6.0
    # near edge
    iL = ipk
    while iL > 0 and db[iL] > thr:
        iL -= 1
    if db[iL] > thr:
        z_near = z[0]
        near_open = True
    else:
        z_near = float(np.interp(thr, [db[iL], db[iL + 1]], [z[iL], z[iL + 1]]))
        near_open = False
    # far edge
    iR = ipk
    while iR < len(db) - 1 and db[iR] > thr:
        iR += 1
    if db[iR] > thr:
        z_far = z[-1]
        far_open = True
    else:
        z_far = float(np.interp(thr, [db[iR - 1], db[iR]], [z[iR - 1], z[iR]]))
        far_open = False
    return (z_near, z_far, z_far - z_near, near_open, far_open, float(z[ipk]), float(pk))


def lateral_width(focal_dist, freq):
    """-6 dB lateral width at focal plane (fix z=focal_dist, vary lateral y),
    focused at focal_dist. Returns full width in meters."""
    tau_focus = focusing_delays(focal_dist)
    y = np.linspace(-focal_dist, focal_dist, 40001)  # symmetric, wide
    p = pressure(y, focal_dist, freq, W16, tau_focus)
    db = spl_db(p)
    ipk = int(np.argmax(db))   # ~y=0
    pk = db[ipk]
    thr = pk - 6.0
    # right edge
    iR = ipk
    while iR < len(db) - 1 and db[iR] > thr:
        iR += 1
    if db[iR] > thr:
        yR = y[-1]
    else:
        yR = float(np.interp(thr, [db[iR - 1], db[iR]], [y[iR - 1], y[iR]]))
    # left edge
    iL = ipk
    while iL > 0 and db[iL] > thr:
        iL -= 1
    if db[iL] > thr:
        yL = y[0]
    else:
        yL = float(np.interp(thr, [db[iL], db[iL + 1]], [y[iL], y[iL + 1]]))
    return float(yR - yL)


def cross_zone_isolation(z1, z2, freq):
    """2x2 SPL table for focus@z1 / focus@z2 measured@z1 / measured@z2.
    isolation_z1 = SPL(focus@z1, meas@z1) - SPL(focus@z1, meas@z2)  (on minus off)
    isolation_z2 = SPL(focus@z2, meas@z2) - SPL(focus@z2, meas@z1).

    HONESTY: the raw on-minus-off isolation is partly just geometric 1/r spreading
    (a nearer point is louder regardless of focusing). We therefore also report:
      - geometric_spreading_dB = 20*log10(z2/z1) : the isolation a single point source
        would already give between the near and far point (NO array, NO focusing).
      - focusing_excess_z1/z2 = (on-minus-off isolation) - geometric_spreading_dB :
        the part attributable to FOCUSING beyond trivial spreading. This is the metric
        that actually evidences depth-zoning. ~0 => isolation is all spreading, focusing
        adds nothing (premise empty at that f,F)."""
    tau1 = focusing_delays(z1)
    tau2 = focusing_delays(z2)
    # measured points on-axis
    def S(tau, zmeas):
        return float(spl_db(pressure(0.0, zmeas, freq, W16, tau)))
    s_f1_m1 = S(tau1, z1)
    s_f1_m2 = S(tau1, z2)
    s_f2_m1 = S(tau2, z1)
    s_f2_m2 = S(tau2, z2)
    iso1 = s_f1_m1 - s_f1_m2     # focus near, near minus far (z1<z2 => positive even from spreading)
    iso2 = s_f2_m2 - s_f2_m1     # focus far, far minus near (spreading works AGAINST this)
    spread = 20.0 * np.log10(z2 / z1)   # near louder than far by this much from 1/r alone
    return {
        "focus_z1_meas_z1_dB": s_f1_m1,
        "focus_z1_meas_z2_dB": s_f1_m2,
        "focus_z2_meas_z1_dB": s_f2_m1,
        "focus_z2_meas_z2_dB": s_f2_m2,
        "isolation_z1_on_minus_off_dB": iso1,
        "isolation_z2_on_minus_off_dB": iso2,
        "geometric_spreading_dB": float(spread),
        "focusing_excess_z1_dB": iso1 - float(spread),
        "focusing_excess_z2_dB": iso2 + float(spread),
    }


def feasible(focal_dist, freq):
    """Y if focal point inside near field (F < Rayleigh = 2 L^2/lambda)."""
    lam = C / freq
    rayleigh = 2 * L_APERTURE ** 2 / lam
    return focal_dist < rayleigh


# ---------------------------------------------------------------------------
# 7. MAIN
# ---------------------------------------------------------------------------
def main():
    anchors = run_anchors()
    nf = nearfield_table()

    results = {
        "metadata": {
            "task": "PREREQUISITE #2 v1 on-axis focusing/depth-zoning efficacy sim (numpy primary)",
            "role": "POLICY v1.8 三道关 GATE-1 SCREENING ONLY -- NO efficacy verdict",
            "L_grade": {"sim_field": "L2/仿真", "feasibility_table": "L3/解析", "L1": "none-in-scope"},
            "geometry": {"N": N, "d_m": D, "L_aperture_m": L_APERTURE,
                         "L_box_m": N * D, "c_m_s": C,
                         "element_positions_m_centered": list(np.round(X_N, 6))},
            "weights_source": os.path.relpath(W8_CSV, REPO),
            "w8_float": list(np.round(W8, 12)),
            "model": "near-field spherical-wave sum p=sum w_n/(4 pi r_n) exp(-j k (r_n - c tau_n))",
            "freqs_hz": FREQS, "focal_dists_m": FOCALS,
            "boundaries": ["point-source isotropic elements (no element directivity / diffraction / "
                           "mutual coupling; underestimates real HF directivity >=2kHz)",
                           "band capped 6 kHz (grating lobes >=6236 Hz excluded)",
                           "relative dB only (absolute SPL not modeled)",
                           "symmetric-only excitation (off-axis steering excluded, DEC-S3-DSP-03)"],
        },
        "validation_anchors": anchors,
        "nearfield_limit_table_L3": nf,
        "per_cell": {},
        "cross_zone_isolation": {},
        "physically_void_cells": [],
    }

    print("=" * 96)
    print("HEADLINE METRICS  [L2/仿真]  (focal gain / axial -6dB zone depth / lateral -6dB width)")
    print("=" * 96)
    hdr = f"{'f(Hz)':>6} {'F(m)':>5} {'feas':>5} {'focal_gain_dB':>14} {'axial_depth_m':>14} {'lateral_w_m':>12} {'depth_note':>12}"
    print(hdr)
    print("-" * len(hdr))

    for f in FREQS:
        fkey = str(int(f))
        results["per_cell"][fkey] = {}
        for F in FOCALS:
            fg = focal_gain_db(F, f)
            (zn, zf, depth, n_open, f_open, zpk, pkdb) = axial_zone_depth(F, f)
            lw = lateral_width(F, f)
            feas = feasible(F, f)
            note = ""
            if n_open and f_open:
                note = "both-open"
            elif f_open:
                note = "far-open"
            elif n_open:
                note = "near-open"
            results["per_cell"][fkey][str(int(F))] = {
                "feasible_F_lt_rayleigh": bool(feas),
                "focal_gain_dB": round(fg, 4),
                "axial_zone_depth_m": round(depth, 4),
                "axial_z_near_m": round(zn, 4),
                "axial_z_far_m": round(zf, 4),
                "axial_depth_near_open": bool(n_open),
                "axial_depth_far_open": bool(f_open),
                "axial_peak_z_m": round(zpk, 4),
                "lateral_width_m": round(lw, 4),
            }
            # physically void cell: not feasible AND negligible focal gain
            if (not feas) and abs(fg) < 0.5:
                results["physically_void_cells"].append(
                    {"freq_hz": int(f), "focal_dist_m": int(F),
                     "focal_gain_dB": round(fg, 4),
                     "reason": "F beyond Rayleigh (far-field); focusing collapses to broadside"})
            print(f"{int(f):>6} {F:>5.0f} {'Y' if feas else 'N':>5} "
                  f"{fg:>14.4f} {depth:>14.4f} {lw:>12.4f} {note:>12}")

    print()
    print("=" * 96)
    print("CROSS-ZONE ISOLATION  [L2/仿真]  (on-target minus off-target, per freq)")
    print("=" * 96)
    for (z1, z2) in ZONE_PAIRS:
        pkey = f"{int(z1)}m_vs_{int(z2)}m"
        results["cross_zone_isolation"][pkey] = {}
        spread = 20.0 * np.log10(z2 / z1)
        print(f"\nzone pair {pkey}  (geometric-spreading baseline = {spread:.3f} dB; "
              f"focusing_excess isolates the FOCUSING part beyond 1/r):")
        print(f"{'f(Hz)':>6} {'iso@z1':>9} {'iso@z2':>9} {'fexc@z1':>9} {'fexc@z2':>9} "
              f"{'f1m1':>8} {'f1m2':>8} {'f2m1':>8} {'f2m2':>8}")
        for f in FREQS:
            ci = cross_zone_isolation(z1, z2, f)
            results["cross_zone_isolation"][pkey][str(int(f))] = {k: round(v, 4) for k, v in ci.items()}
            print(f"{int(f):>6} {ci['isolation_z1_on_minus_off_dB']:>9.3f} "
                  f"{ci['isolation_z2_on_minus_off_dB']:>9.3f} "
                  f"{ci['focusing_excess_z1_dB']:>9.3f} {ci['focusing_excess_z2_dB']:>9.3f} "
                  f"{ci['focus_z1_meas_z1_dB']:>8.3f} {ci['focus_z1_meas_z2_dB']:>8.3f} "
                  f"{ci['focus_z2_meas_z1_dB']:>8.3f} {ci['focus_z2_meas_z2_dB']:>8.3f}")

    # write machine-readable JSON
    out_json = os.path.join(HERE, "results_numpy.json")
    with open(out_json, "w") as fp:
        json.dump(results, fp, indent=2, ensure_ascii=False)

    print()
    print("=" * 96)
    print(f"PHYSICALLY VOID CELLS (F beyond Rayleigh, focal gain ~0 dB): "
          f"{len(results['physically_void_cells'])}")
    for v in results["physically_void_cells"]:
        print(f"  f={v['freq_hz']}Hz F={v['focal_dist_m']}m  focal_gain={v['focal_gain_dB']}dB")
    print("=" * 96)
    print(f"WROTE: {out_json}")
    return results


if __name__ == "__main__":
    main()
