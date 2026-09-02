#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sprint 7 acoustic simulation -- SHARED MODEL (imported by s7_windows_sweep.py,
s7_lowfreq_superdir.py, s7_focus_chmap_equiv.py).

L-grade of everything produced here: [L2/numpy simulation]. Nothing is measured.

MODEL (identical to sweep_d55.py / a1_static_weight_numpy.py / m3_numpy_superdir_8pair.py /
sprint5/efficacy_sim/focus_sim.py):
  * N=16 isotropic point sources on a line, pitch d=55 mm [L1 teardown, DEC-S3-GEOM-01],
    acoustic aperture L=(N-1)d=825 mm, centred positions x_n=(n-7.5)d, c=343 m/s (20 C).
  * Far-field array factor AF(theta)=sum_n w_n exp(j k x_n sin theta), theta=0 broadside.
  * Real, centre-symmetric weights only (8 A/B series pairs {c,15-c} -> w_n == w_{15-n}).
  * NO baffle / enclosure diffraction, NO element directivity (PF-6: optimistic at wide angles
    >= 2 kHz), NO mutual coupling, NO rear hemisphere capability (R9: AF(180)=AF(0) artefact).

METRIC CONVENTIONS (project-wide):
  * BW  = -6 dB FULL angle = 2 x one-sided half angle, linear interpolation on a 0.01 deg grid.
          Sanity: BW(-6) > BW(-3) always; peak must be at 0 deg.
  * SLL = peak side-lobe level (dB re main lobe). Main lobe = region from the peak out to the
          first local minimum on each side; SLL = max of pattern outside it. If the lobe that
          gives the max touches +/-90 deg the flag `sll_at_edge` is set (partial lobe).
          If the main lobe fills the whole visible region -> SLL = NaN (no visible side lobe).
  * DI  = 10 log10( |sum w|^2 / sum_ij w_i w_j sinc(k|x_i-x_j|) )   (3-D, isotropic elements,
          closed form; numerically cross-checked against 2|AF(0)|^2 / int |AF|^2 cos(theta) dtheta).
  * WNG_norm = 10 log10( |sum w|^2 / (N sum w^2) )   -- relative to uniform (uniform = 0 dB).
    WNG_abs  = 10 log10( |sum w|^2 / sum w^2 )       -- m3 convention (uniform = 10log10(16)=12.04 dB).
  * att(theta) = -20 log10 |AF(theta)/AF(0)|  (positive dB; JY/T table-9 "SPL difference").

ANCHOR ASSERTIONS (run by `assert_anchors()` -- every script calls it FIRST and raises on failure,
so no un-anchored number can be shipped; same discipline as sprint5/efficacy_sim/focus_sim.py:19-21):
  A1  frozen Dolph -20 dB table (sprint4/dsp/fira/dolph_w8_q15.csv float column) -> BW@1k = 29.269 +/- 0.1 deg
      (sweep_d55_results.csv row 1000/dolph20; dolph_w8_q15.h:29)
  A2  same weights -> BW@2k = 14.515 +/- 0.1 deg  (sweep_d55_results.csv row 2000/dolph20)
  A3  same weights -> peak SLL = -20.00 +/- 0.05 dB at 1k and 2k
  A4  uniform weights -> peak SLL @1k within 0.3 dB of -13.26 dB (N=16 discrete: -13.15 dB)
  A5  frozen CSV float column == scipy chebwin(16,20)/max to 1e-9 (same-source discipline)
  A6  Q15 quantised table changes BW@1k / SLL by < 1e-3 (dolph_w8_q15.h claim)
  A7  DI closed form == DI numeric integral within 0.01 dB (Dolph-20 @1k)
  A8  BW(-6) > BW(-3) and argmax at 0 deg for the anchor pattern
"""
import os
import csv
import numpy as np
from scipy.signal.windows import chebwin, taylor, kaiser, hann, gaussian

# ---------------------------------------------------------------------------
# Locked constants & geometry
# ---------------------------------------------------------------------------
C = 343.0                       # m/s, 20 C  (skill N.2.1: explicit speed of sound)
N = 16
D = 0.055                       # m  [L1 teardown]
L_APERTURE = (N - 1) * D        # 0.825 m  (box length N*d = 0.880 m is NOT the aperture)
X = (np.arange(N) - (N - 1) / 2.0) * D       # centred element positions (m)
F_GRATING = C / D               # 6236 Hz  (d = lambda)  [skill N.2.2]

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
W8_CSV = os.path.join(REPO, "sprint4", "dsp", "fira", "dolph_w8_q15.csv")

ANG = np.arange(-90.0, 90.0 + 1e-9, 0.01)    # deg, 18001 points, index 9000 == 0 deg
I0 = int(np.argmin(np.abs(ANG)))
assert abs(ANG[I0]) < 1e-9

# Implemented sub-band edges (tree_filterbank.h:19-27; NOT the spec's 8k/4k/2k/1k)
SUBBANDS = {"SB0": (0.0, 1500.0), "SB1": (1500.0, 3000.0), "SB2": (3000.0, 6000.0), "SB3": (6000.0, 12000.0)}


# ---------------------------------------------------------------------------
# Frozen weights
# ---------------------------------------------------------------------------
def read_w8(path=W8_CSV):
    """Return (w8_float, w8_q15) read from the frozen F5-C CSV (NOT recomputed)."""
    w8 = [None] * 8
    q8 = [None] * 8
    with open(path, "r") as fp:
        for row in csv.DictReader(fp):
            c = int(row["ch"])
            w8[c] = float(row["w_float_track1_scipy"])
            q8[c] = int(row["w_q15"])
    if any(v is None for v in w8):
        raise RuntimeError("dolph_w8_q15.csv: missing channel rows")
    return np.array(w8, float), np.array(q8, int)


def expand16(w8):
    """8 channel weights -> 16-element centre-symmetric vector [w0..w7, w7..w0]."""
    w8 = np.asarray(w8, float)
    return np.concatenate([w8, w8[::-1]])


def is_symmetric(w, tol=1e-12):
    w = np.asarray(w, float)
    return bool(np.max(np.abs(w - w[::-1])) <= tol)


# ---------------------------------------------------------------------------
# Far-field array factor & metrics
# ---------------------------------------------------------------------------
def af_complex(theta_deg, f, w):
    """Complex far-field array factor, theta=0 broadside. Returns shape (n_theta,)."""
    k = 2 * np.pi * f / C
    st = np.sin(np.deg2rad(np.atleast_1d(theta_deg).astype(float)))
    ph = k * np.outer(st, X)
    return (np.asarray(w, float) * np.exp(1j * ph)).sum(axis=1)


def pattern_db(f, w, ang=ANG):
    """Normalised (to max) magnitude pattern in dB on grid `ang`."""
    a = np.abs(af_complex(ang, f, w))
    return 20 * np.log10(a / a.max() + 1e-300)


def peak_is_broadside(P):
    return int(np.argmax(P)) == I0


def bw_full(P, ang=ANG, level=6.0):
    """Full -level dB beamwidth (deg), interpolated; 180 if not reached inside +/-90."""
    i0 = int(np.argmax(P))
    thr = P[i0] - level
    iR = i0
    while iR < len(P) - 1 and P[iR] > thr:
        iR += 1
    iL = i0
    while iL > 0 and P[iL] > thr:
        iL -= 1
    if iR >= len(P) - 1 and P[iR] > thr:
        return 180.0
    if iL <= 0 and P[iL] > thr:
        return 180.0
    aR = np.interp(thr, [P[iR], P[iR - 1]], [ang[iR], ang[iR - 1]])
    aL = np.interp(thr, [P[iL], P[iL + 1]], [ang[iL], ang[iL + 1]])
    return float(aR - aL)


def peak_sll(P, ang=ANG):
    """(sll_dB, at_edge). Main lobe = peak out to first local minimum each side."""
    i0 = int(np.argmax(P))
    iR = i0
    while iR < len(P) - 1 and P[iR + 1] <= P[iR]:
        iR += 1
    iL = i0
    while iL > 0 and P[iL - 1] <= P[iL]:
        iL -= 1
    mask = np.ones(len(P), dtype=bool)
    mask[iL:iR + 1] = False
    if not mask.any():
        return float("nan"), False
    idx = np.where(mask)[0]
    j = idx[int(np.argmax(P[idx]))]
    at_edge = bool(j == 0 or j == len(P) - 1)
    return float(P[j] - P[i0]), at_edge


def peak_sll_interior(P, ang=ANG):
    """Highest INTERIOR side lobe (a true local maximum strictly inside +/-90), dB re main lobe.
    Excludes the partial lobe that touches +/-90 deg (grating-lobe shoulder near d ~ lambda).
    NaN if no interior side lobe exists."""
    i0 = int(np.argmax(P))
    iR = i0
    while iR < len(P) - 1 and P[iR + 1] <= P[iR]:
        iR += 1
    iL = i0
    while iL > 0 and P[iL - 1] <= P[iL]:
        iL -= 1
    cand = []
    for j in range(1, len(P) - 1):
        if iL <= j <= iR:
            continue
        if P[j] >= P[j - 1] and P[j] > P[j + 1]:
            cand.append(P[j])
    if not cand:
        return float("nan")
    return float(max(cand) - P[i0])


def att_db(theta_deg, f, w):
    """Positive attenuation at theta relative to broadside (JY/T table-9 SPL difference)."""
    a = np.abs(af_complex([0.0, theta_deg], f, w))
    return float(-20 * np.log10(a[1] / a[0] + 1e-300))


def gamma_sinc(f):
    """Isotropic (3-D diffuse) coherence matrix Gamma_ij = sinc(k|x_i-x_j|), sinc(x)=sin x/x."""
    k = 2 * np.pi * f / C
    dx = k * np.abs(X[:, None] - X[None, :])
    return np.sinc(dx / np.pi)


def di_db(f, w):
    """Directivity index (dB), closed form, isotropic elements, 3-D."""
    w = np.asarray(w, float)
    num = w.sum() ** 2
    den = w @ gamma_sinc(f) @ w
    return float(10 * np.log10(num / den))


def di_db_numeric(f, w, step_deg=0.005):
    """Directivity index by numerical integration 2|AF(0)|^2 / int_{-pi/2}^{pi/2} |AF|^2 cos(theta) dtheta."""
    th = np.arange(-90.0, 90.0 + 1e-9, step_deg)
    a2 = np.abs(af_complex(th, f, w)) ** 2
    a0 = np.abs(af_complex([0.0], f, w))[0] ** 2
    integ = np.trapezoid(a2 * np.cos(np.deg2rad(th)), np.deg2rad(th))
    return float(10 * np.log10(2 * a0 / integ))


def wng_norm_db(w):
    w = np.asarray(w, float)
    return float(10 * np.log10(w.sum() ** 2 / (N * (w ** 2).sum())))


def wng_abs_db(w):
    w = np.asarray(w, float)
    return float(10 * np.log10(w.sum() ** 2 / (w ** 2).sum()))


def metrics(f, w, ang=ANG):
    """All per-cell metrics for weights w at frequency f."""
    P = pattern_db(f, w, ang)
    bw6 = bw_full(P, ang, 6.0)
    bw3 = bw_full(P, ang, 3.0)
    sll, edge = peak_sll(P, ang)
    return {
        "bw6_deg": bw6,
        "bw3_deg": bw3,
        "sll_db": sll,
        "sll_at_edge": edge,
        "sll_interior_db": peak_sll_interior(P, ang),
        "di_db": di_db(f, w),
        "wng_norm_db": wng_norm_db(w),
        "wng_abs_db": wng_abs_db(w),
        "att30_db": att_db(30.0, f, w),
        "att90_db": att_db(90.0, f, w),
        "peak_at_0": peak_is_broadside(P),
        "bw6_gt_bw3": bool(bw6 > bw3) if (bw6 < 180.0 and bw3 < 180.0) else True,
    }


# ---------------------------------------------------------------------------
# Window catalogue (all normalised max=1, all centre-symmetric)
# ---------------------------------------------------------------------------
def w_norm(w):
    w = np.asarray(w, float)
    return w / w.max()


def window_catalog():
    w8f, _ = read_w8()
    cat = {
        "uniform":            np.ones(N),
        "dolph20_frozen":     expand16(w8f),                          # F5-C frozen baseline
        "dolph25":            w_norm(chebwin(N, 25)),
        "dolph30":            w_norm(chebwin(N, 30)),
        "taylor25_nbar4":     w_norm(taylor(N, nbar=4, sll=25, norm=True)),
        "kaiser_b3":          w_norm(kaiser(N, 3.0)),
        "kaiser_b5":          w_norm(kaiser(N, 5.0)),
        "hann_edge_nonzero":  w_norm(hann(N + 2, sym=True)[1:-1]),    # w_n=0.5(1-cos(2pi(n+1)/17)); edge pair NOT zero
        "hann_sym_edge0":     w_norm(hann(N, sym=True)),              # scipy default: edge pair weight 0 (aperture shrinks to 14 elements)
    }
    for k, v in cat.items():
        if not is_symmetric(v):
            raise RuntimeError(f"window {k} is not centre-symmetric -> not realisable on 8 A/B pairs")
    return cat


# ---------------------------------------------------------------------------
# Anchors
# ---------------------------------------------------------------------------
def assert_anchors(verbose=True):
    w8f, q8 = read_w8()
    w16 = expand16(w8f)
    w16_q = expand16(q8 / 32768.0)
    out = {}

    # A5 same-source
    w_sci = w_norm(chebwin(N, 20))
    out["A5_max_abs_diff_csv_vs_chebwin"] = float(np.max(np.abs(w16 - w_sci)))
    if out["A5_max_abs_diff_csv_vs_chebwin"] > 1e-9:
        raise SystemExit(f"ANCHOR A5 FAIL: frozen CSV vs chebwin(16,20) diff {out['A5_max_abs_diff_csv_vs_chebwin']:.3e}")
    if not is_symmetric(w16):
        raise SystemExit("ANCHOR FAIL: frozen weights not centre-symmetric")

    # A1/A2/A3
    m1k = metrics(1000.0, w16)
    m2k = metrics(2000.0, w16)
    out["A1_bw6_1k_deg"] = m1k["bw6_deg"]
    out["A2_bw6_2k_deg"] = m2k["bw6_deg"]
    out["A3_sll_1k_db"] = m1k["sll_db"]
    out["A3_sll_2k_db"] = m2k["sll_db"]
    if abs(m1k["bw6_deg"] - 29.269) > 0.1:
        raise SystemExit(f"ANCHOR A1 FAIL: BW@1k = {m1k['bw6_deg']:.4f} deg (target 29.269 +/- 0.1). STOP.")
    if abs(m2k["bw6_deg"] - 14.515) > 0.1:
        raise SystemExit(f"ANCHOR A2 FAIL: BW@2k = {m2k['bw6_deg']:.4f} deg (target 14.515 +/- 0.1). STOP.")
    for tag, m in (("1k", m1k), ("2k", m2k)):
        if abs(m["sll_db"] - (-20.0)) > 0.05:
            raise SystemExit(f"ANCHOR A3 FAIL: Dolph-20 SLL@{tag} = {m['sll_db']:.4f} dB (target -20.00). STOP.")

    # A4 uniform negative control
    mu = metrics(1000.0, np.ones(N))
    out["A4_uniform_sll_1k_db"] = mu["sll_db"]
    if abs(mu["sll_db"] - (-13.26)) > 0.3:
        raise SystemExit(f"ANCHOR A4 FAIL: uniform SLL@1k = {mu['sll_db']:.3f} dB (expect ~ -13.26). STOP.")

    # A6 Q15 quantisation shift
    mq = metrics(1000.0, w16_q)
    out["A6_q15_bw_shift_deg"] = abs(mq["bw6_deg"] - m1k["bw6_deg"])
    out["A6_q15_sll_shift_db"] = abs(mq["sll_db"] - m1k["sll_db"])
    if out["A6_q15_bw_shift_deg"] > 1e-3 or out["A6_q15_sll_shift_db"] > 1e-3:
        raise SystemExit("ANCHOR A6 FAIL: Q15 quantised table shifts BW/SLL by > 1e-3. STOP.")

    # A7 DI closed vs numeric
    out["A7_di_closed_1k_db"] = di_db(1000.0, w16)
    out["A7_di_numeric_1k_db"] = di_db_numeric(1000.0, w16)
    if abs(out["A7_di_closed_1k_db"] - out["A7_di_numeric_1k_db"]) > 0.01:
        raise SystemExit("ANCHOR A7 FAIL: DI closed-form vs numeric integral disagree > 0.01 dB. STOP.")

    # A8 one-second criterion
    out["A8_bw3_1k_deg"] = m1k["bw3_deg"]
    if not (m1k["bw6_deg"] > m1k["bw3_deg"] and m1k["peak_at_0"]):
        raise SystemExit("ANCHOR A8 FAIL: BW(-6) <= BW(-3) or peak not at 0 deg. STOP.")

    if verbose:
        print("=" * 72)
        print("ANCHORS (must pass before any Sprint-7 number is produced)")
        print("=" * 72)
        for k, v in out.items():
            print(f"  {k:<36} = {v:.6g}")
        print("ALL ANCHORS PASS")
        print()
    return out


if __name__ == "__main__":
    assert_anchors()
