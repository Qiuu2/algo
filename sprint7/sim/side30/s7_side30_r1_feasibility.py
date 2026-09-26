#!/usr/bin/env python3
# sprint7/sim/side30/s7_side30_r1_feasibility.py -- landed 2026-09-26 (PM). ROUND-1 script (critic R1 = FAIL). Its per-subband designs D1/D2/D3 assume the WRONG 1.5k/3k/6k brick-wall split -> those numbers are VOID (DEC-S7-RETRACT-SUBBAND-01). Kept for traceability; the single-table/MC-floor/wiring-fault parts were confirmed by critic R1. Seed 20260926.
"""
Exploratory feasibility sim: side (90 deg / 60-90 deg sector) attenuation 20 -> 30 dB.
L-grade of every number printed here: [L2/numpy, exploratory, this session, NOT critic-gated].
Model = sprint7/sim/acoustic/s7_common.py (isotropic point sources, far field, N=16, d=55 mm,
8 centre-symmetric pairs, no baffle / element directivity / coupling / room).
Sub-bands treated as ideal brick-wall (SB0 <1.5k, SB1 1.5-3k, SB2 3-6k, SB3 >6k), as in S7 report.
Band metrics = 1/3-octave power average (pink / warble-like excitation), not single-frequency points.
"""
import os, sys
import numpy as np

REPO_SIM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "acoustic")
sys.path.insert(0, REPO_SIM)
import s7_common as S  # noqa: E402
from scipy.signal.windows import chebwin, kaiser  # noqa: E402
from scipy.optimize import linprog  # noqa: E402

S.assert_anchors(verbose=False)
W_D20 = S.expand16(S.read_w8()[0])

# --- anchor: reproduce PRD / S7 point values before printing anything -----------------------
for f, ref in [(1000, 22.404), (2000, 23.010), (4000, 26.029)]:
    got = S.att_db(90.0, f, W_D20)
    assert abs(got - ref) < 0.01, (f, got, ref)
assert abs(S.att_db(30.0, 1000, W_D20) - 23.098) < 0.01

RNG = np.random.default_rng(20260926)


def win(name):
    if name == "dolph20":
        return W_D20
    if name.startswith("dolph"):
        return S.w_norm(chebwin(16, float(name[5:])))
    if name.startswith("kaiser_b"):
        return S.w_norm(kaiser(16, float(name[8:])))
    if name == "uniform":
        return np.ones(16)
    raise KeyError(name)


def sb_of(f):
    return "SB0" if f < 1500 else "SB1" if f < 3000 else "SB2" if f < 6000 else "SB3"


def band_freqs(fc, n=41):
    return np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), n)


CENTERS = [250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300]
A_WT = {250: -8.6, 315: -6.6, 400: -4.8, 500: -3.2, 630: -1.9, 800: -0.8, 1000: 0.0, 1250: 0.6,
        1600: 1.0, 2000: 1.2, 2500: 1.3, 3150: 1.2, 4000: 1.0, 5000: 0.5, 6300: -0.1}


def af(theta_deg, f, w, e=None):
    """Complex AF; e = per-element complex error multipliers (16,) or None."""
    ww = np.asarray(w, complex) if e is None else np.asarray(w, float) * e
    k = 2 * np.pi * f / S.C
    st = np.sin(np.deg2rad(np.atleast_1d(theta_deg).astype(float)))
    return (ww[None, :] * np.exp(1j * k * np.outer(st, S.X))).sum(axis=1)


def band_power(theta_deg, fc, design, e=None):
    """Mean over the 1/3-oct band of |AF|^2 at each theta (design = dict SBx -> w16)."""
    fs = band_freqs(fc)
    acc = np.zeros(len(np.atleast_1d(theta_deg)))
    for f in fs:
        acc += np.abs(af(theta_deg, f, design[sb_of(f)], e)) ** 2
    return acc / len(fs)


def band_att(fc, design, e=None, sector=(90.0, 90.0)):
    """Band-averaged attenuation (dB, positive) at worst angle of sector (60-90 -> min atten)."""
    th = np.arange(sector[0], sector[1] + 1e-9, 0.5) if sector[1] > sector[0] else np.array([sector[0]])
    p = band_power(np.concatenate([[0.0], th, -th]), fc, design, e)
    return float(10 * np.log10(p[0] / p[1:].max()))


def mk(sb0, sb1, sb2, sb3=None):
    return {"SB0": win(sb0) if isinstance(sb0, str) else sb0,
            "SB1": win(sb1) if isinstance(sb1, str) else sb1,
            "SB2": win(sb2) if isinstance(sb2, str) else sb2,
            "SB3": win(sb3 or "dolph20") if isinstance(sb3 or "dolph20", str) else sb3}


# =============================================================================================
# LP: per sub-band, minimise worst |AF| over side sector (60-90 deg) across the band,
# subject to AF(0)=1 at every f, JY/T grade-1 30 deg attenuation, 0<=w, 35-60 deg <= -20 dB.
# =============================================================================================
def lp_sector(f_lo, f_hi, t30_db, sector=(60.0, 90.0), nf=15, wmax=0.2):
    X8 = S.X[:8]  # edge (c=0) .. centre (c=7) element positions; mirror = -X8
    fs = np.geomspace(f_lo, f_hi, nf)
    A_ub, b_ub = [], []
    for f in fs:
        k = 2 * np.pi * f / S.C

        def row(th):
            return 2 * np.cos(k * X8 * np.sin(np.deg2rad(th)))
        for th in np.arange(sector[0], sector[1] + 1e-9, 1.0):
            r = row(th)
            A_ub.append(np.r_[r, -1.0]); b_ub.append(0.0)      # AF <= s
            A_ub.append(np.r_[-r, -1.0]); b_ub.append(0.0)     # -AF <= s
        g30 = 10 ** (-t30_db / 20)
        for th in (30.0,):
            r = row(th)
            A_ub.append(np.r_[r, 0.0]); b_ub.append(g30)
            A_ub.append(np.r_[-r, 0.0]); b_ub.append(g30)
        for th in np.arange(35.0, sector[0], 1.0):
            r = row(th)
            A_ub.append(np.r_[r, 0.0]); b_ub.append(0.1)
            A_ub.append(np.r_[-r, 0.0]); b_ub.append(0.1)
    A_eq = [np.r_[2 * np.ones(8), 0.0]]   # AF(0) = sum 2 w_c = 1 (frequency independent)
    b_eq = [1.0]
    c = np.r_[np.zeros(8), 1.0]
    bounds = [(0.0, wmax)] * 8 + [(0, None)]
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=b_eq,
                  bounds=bounds, method="highs")
    if not res.success:
        return None, None
    w8 = res.x[:8]
    return S.expand16(w8 / w8.max()), float(-20 * np.log10(res.x[8]))


def wng_n(w):
    return S.wng_norm_db(w)


def onaxis_rel_d20(w):
    """Full-drive on-axis level vs Dolph-20 (max weight = 1 in both) [L3 bookkeeping]."""
    return 20 * np.log10(np.sum(w) / np.sum(W_D20))


def hr(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


# ---------------------------------------------------------------------------------------------
hr("0. Anchors: point att90 Dolph-20 @1k/2k/4k = 22.40/23.01/26.03 reproduced (assert passed)")

w_lp0, s0 = lp_sector(800, 1500, t30_db=18.0)
w_lp1, s1 = lp_sector(1500, 3000, t30_db=20.0)
w_lp2, s2 = lp_sector(3000, 5000, t30_db=22.0)
print("LP sector designs (min over band of 60-90 deg atten, design value):",
      [None if s is None else round(s, 1) for s in (s0, s1, s2)])
for nm, w in (("LP-SB0 800-1.5k", w_lp0), ("LP-SB1 1.5-3k", w_lp1), ("LP-SB2 3-5k", w_lp2)):
    if w is not None:
        print(f"  {nm:16s} w8(edge->centre) = {np.round(w[:8], 3)}  WNGn={wng_n(w):+.2f} dB  "
              f"on-axis vs D20={onaxis_rel_d20(w):+.2f} dB")

DESIGNS = {
    "D0 now: Dolph-20 all bands": mk("dolph20", "dolph20", "dolph20"),
    "D1: SB0 D20 | SB1 D35 | SB2 D35": mk("dolph20", "dolph35", "dolph35"),
    "D2: SB0 D30 | SB1 D35 | SB2 D35": mk("dolph30", "dolph35", "dolph35"),
    "D3: SB0 LP | SB1 LP | SB2 LP": mk(w_lp0 if w_lp0 is not None else "dolph20",
                                      w_lp1 if w_lp1 is not None else "dolph20",
                                      w_lp2 if w_lp2 is not None else "dolph20"),
}

hr("1. Ideal array: band-averaged attenuation per 1/3-oct band (dB). a90 = at 90 deg; "
   "s = worst angle in 60-90 sector; a30 = at 30 deg")
hdr = "band  " + "".join(f"| {k[:26]:26s} " for k in DESIGNS)
print(hdr)
print("      " + "".join("|  a90   s60-90   a30        " for _ in DESIGNS))
for fc in CENTERS:
    line = f"{fc:5d} "
    for d in DESIGNS.values():
        a90 = band_att(fc, d)
        s = band_att(fc, d, sector=(60.0, 90.0))
        a30 = band_att(fc, d, sector=(30.0, 30.0))
        line += f"| {a90:5.1f}  {s:5.1f}  {a30:5.1f}        "
    print(line)
print("\nWNGn per sub-band (dB re uniform) and full-drive on-axis vs D20 (dB):")
for k, d in DESIGNS.items():
    print(f"  {k:34s} " + "  ".join(f"{sb}:WNG{wng_n(d[sb]):+.2f}/ax{onaxis_rel_d20(d[sb]):+.2f}"
                                     for sb in ("SB0", "SB1", "SB2")))
print("\nBW@1k (-6 dB full, deg): " + ", ".join(
    f"{k[:3]}={S.bw_full(S.pattern_db(1000, d['SB0'])):.2f}" for k, d in DESIGNS.items()))


# ---------------------------------------------------------------------------------------------
def draw_errors(sig_a_db, sig_p_deg):
    a = RNG.normal(0, sig_a_db, 16)
    p = RNG.normal(0, np.deg2rad(sig_p_deg), 16)
    return 10 ** (a / 20) * np.exp(1j * p)


def calibrate(e):
    """Per-channel complex trim: pair-sum at broadside restored (can't fix intra-pair diff)."""
    e = e.copy()
    for c in range(8):
        g = 2.0 / (e[c] + e[15 - c])
        e[c] *= g
        e[15 - c] *= g
    return e


hr("2. Monte Carlo element mismatch (16 independent drivers, freq-flat errors), 1500 arrays each.\n"
   "   Reported: band-avg attenuation at 90 deg -> median / P10 (90% of arrays at least this), "
   "and same after per-channel calibration")
TOLS = [(0.5, 3.0), (1.0, 5.0), (1.5, 10.0), (2.0, 15.0)]
NMC = 1500
for dname in ("D0 now: Dolph-20 all bands", "D2: SB0 D30 | SB1 D35 | SB2 D35", "D3: SB0 LP | SB1 LP | SB2 LP"):
    d = DESIGNS[dname]
    print(f"\n{dname}")
    for fc in (1000, 2000, 4000):
        row = f"  {fc:5d} Hz  ideal {band_att(fc, d):5.1f} |"
        for sa, sp in TOLS:
            v, vc = [], []
            for _ in range(NMC):
                e = draw_errors(sa, sp)
                v.append(band_att(fc, d, e))
                vc.append(band_att(fc, d, calibrate(e)))
            v, vc = np.array(v), np.array(vc)
            row += (f" ±{sa}dB/{sp:g}°: {np.median(v):4.1f}/{np.percentile(v, 10):4.1f}"
                    f" cal {np.median(vc):4.1f}/{np.percentile(vc, 10):4.1f} |")
        print(row)

# ---------------------------------------------------------------------------------------------
hr("3. Wiring faults (deterministic): band-avg attenuation at 90 deg, worst / median over positions")
for dname in ("D0 now: Dolph-20 all bands", "D2: SB0 D30 | SB1 D35 | SB2 D35"):
    d = DESIGNS[dname]
    print(f"\n{dname}")
    for fc in (1000, 2000, 4000):
        out = [f"  {fc:5d} Hz ideal {band_att(fc, d):5.1f}"]
        for label, maker in (
                ("1 driver flipped", lambda n: np.where(np.arange(16) == n, -1.0, 1.0).astype(complex)),
                ("1 driver dead", lambda n: np.where(np.arange(16) == n, 0.0, 1.0).astype(complex)),
                ("1 pair(ch) flipped", lambda c: np.where((np.arange(16) == c) | (np.arange(16) == 15 - c),
                                                          -1.0, 1.0).astype(complex))):
            rng_pos = range(16) if "pair" not in label else range(8)
            vals = np.array([band_att(fc, d, maker(n)) for n in rng_pos])
            out.append(f"{label}: worst {vals.min():5.1f} med {np.median(vals):5.1f}")
        print(" | ".join(out))

# ---------------------------------------------------------------------------------------------
hr("4. Broadband (pink noise, A-weighted, 1/3-oct 250 Hz-5 kHz, ideal array): att at 90 deg vs program HPF")


def broadband_att(design, hpf, bands=CENTERS[:-1]):
    p0 = p90 = 0.0
    for fc in bands:
        if fc < hpf:
            continue
        wgt = 10 ** (A_WT[fc] / 10)
        p = band_power(np.array([0.0, 90.0]), fc, design)
        p0 += wgt * p[0]
        p90 += wgt * p[1]
    return 10 * np.log10(p0 / p90)


for dname in ("D0 now: Dolph-20 all bands", "D2: SB0 D30 | SB1 D35 | SB2 D35", "D3: SB0 LP | SB1 LP | SB2 LP"):
    d = DESIGNS[dname]
    print(f"  {dname:34s} " + "  ".join(f"HPF {h:>4}: {broadband_att(d, h):5.1f}"
                                        for h in (0, 400, 630, 800, 1000)))
print("  (bands above 5 kHz excluded: d=55 grating lobe reaches 90 deg at ~5.8-6.2 kHz in every design;"
      " real side level there is set by driver/box directivity, not modelled)")
