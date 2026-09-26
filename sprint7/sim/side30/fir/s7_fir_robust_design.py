#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S7 side-30 / per-channel filter-and-sum ("每通道滤波器") robust beamformer -- DESKTOP PROTOTYPE.

L-GRADES
  * every simulated number printed/written here ....... [L2/numpy+scipy host simulation]
  * MAC/frame counts (FIR bank and the frozen tree) .... [L3/hand count, formulas printed]
  * driver-error / jig-noise model ..................... [L4 assumption] (project convention, not measured)
  * NOTHING here is measured. No board reading is predicted.

ZERO firmware change. Reads (read-only): sprint7/sim/acoustic/s7_common.py (model, anchors, frozen
Dolph-20 table). Its SUBBANDS dict is NOT used (it is wrong: the frozen pyramid splits at 3k/6k/12k).

MODEL (s7_common): N=16 isotropic point sources, d=55 mm [L1 teardown], far field, c=343 m/s.
8 DSP channels; channel c drives the centre-symmetric SERIES pair {c,15-c}, so per frequency
    AF(theta,f) = sum_c H_c(f) * 2cos(k x_c sin theta),   x_c = (c-7.5) d.
All 8 FIRs are linear-phase with the SAME delay, so H_c(f) = exp(-j w M) A_c(f), A_c real; the
common delay cancels in every ratio below.

DESIGN (per frequency bin, 0..24 kHz, 2049 bins, df = 11.7 Hz)
  Q(f) = R_side(f) + eta(f) R_mid(f) + lam(f) I      (pair coordinates, a_c = 2cos(k x_c sin th))
  W(f) = Q^-1 a0 / (a0^T Q^-1 a0),  a0 = [2..2]  ->  sum_c 2 W_c(f) = 1 (flat on-axis)
  R_side = mean_{th in [ths,90]} a a^T ; R_mid = mean_{th in [thm(f),ths]} a a^T,
  sin thm = min(1, beta*lambda/(N d)) (edge of the uniform main lobe x beta)
  lam = 2 sigma^2(f): mean-performance (Van Trees 2002 eq. 2.208 / Gilbert-Morgan 1955) load for
        iid per-driver complex errors; sigma^2 = E|g-1|^2 of the U-flat tolerance draw + (k sigma_x)^2.
  Band handling: raised-cosine (log f) blend toward the frozen Dolph-20 table below ~420-700 Hz
  (aperture-limited, keeps LF == today's M2) and above ~5.2-6.2 kHz (grating region).
  Smoothing across frequency: Gaussian in log2 f (FWHM 1/6 octave); roughness printed before/after.
  FIR: 8 type-I linear-phase FIRs, length 2M+1 in {63,127,255} (= the 64/128/256-tap class with one
  zero pad; group delay M = 31/63/127 samples), fitted by weighted least squares to the smoothed
  target with the EXACT linear constraint sum_c 2 h_c[n] = delta[n-M] (flat on-axis by construction).
  Fit metric per bin = Q/(W^T Q W) + FIT_GAMMA * R_all/(W^T R_all W) (relative excess side power +
  relative whole-pattern error 0-90 deg, the latter keeps the target main lobe / BW), log-f density.
  (With FIT_GAMMA = 0 the Q-weighted fit to the per-bin optimum equals the direct optimal FIR for the
  mean-side-power cost, because Q W* ~ a0 and a0^T (A - W*) = 0 kill the cross term; with FIT_GAMMA > 0
  it is a deliberate side-power vs pattern-fidelity compromise, not that optimum.)

EVALUATION: of the REALISED FIRs (not the per-bin weights): 1/3-oct bands 250 Hz-6.3 kHz (31 pts/band,
power average), att90 (worse side; ideal model is symmetric), worst of the 60-90 deg sector,
att30, WNG, BW(-6 dB full)@1k/2k/4k (single frequency, s7_common convention), JY/T table-9 points (8 of 12
evaluable: 30/90 deg; the 180-deg thresholds exist but the isotropic model is front/back symmetric -> NA),
each JY/T point also as single-frequency value and in-band minimum, on-axis ripple (float and Q15),
on-axis full-drive level vs Dolph-20, random-error floor sigma^2*||w||^2/|sum w|^2 per band,
near field at r = 1..16 m (1/3-oct band, 41 pts, and single frequency), headroom at equal on-axis gain vs today's chain,
verification-plan numbers (placeholder distinguishability band, ST1 history, IO1 counts, CSV readback),
compute: MAC/frame [L3] and core cycles with the project's 30-50 cyc/MAC board factor.

MONTE CARLO (1000 arrays/cell default, common random numbers across designs): re-implements the critic-verified
convention of the side-30 review (critic2/mc2.py): U-flat +/-1 dB, +/-5 deg, +/-0.5 mm (jig: 0.1 dB/0.5 deg
per-freq noise only) and "G p0.5 l1oct + jig 0.25 dB/1.5 deg" (Gaussian, same variance, 50 % of the variance
redrawn smoothly across log f with 1-octave correlation). Strategies: as-built / +per-ch gain trim /
+jig-measured pairing & trim / +per-ch complex freq-dependent calibration (no pairing) / pairing + complex cal.
Metric: 1/3-oct band power average at +/-90 deg, WORSE side; median, P10; joint yield over the 7 bands of
DEC-S7-SIDE30-01 (1/3-oct 1k,1.25k,1.6k,2k,2.5k,3.15k,4k all >= 30 dB) = HEADLINE, and over 1k&2k&4k (secondary);
the 4 extra bands are evaluated from the SAME random draws (the draw count does not depend on the frequency grid;
jig measurement, pairing and calibration stay on the original grid), so the 3-band numbers are unchanged;
plus the per-side MEAN-power attenuation (to compare with the error floor). The complex calibration is modelled
as ideal (jig-grid 1/pm multiplied into the channel response): its own taps / L1 / per-unit coefficient sets are
NOT modelled, and a calibrated coefficient set no longer satisfies sum_c 2 h_c = delta.
MC anchor: the Dolph-35 table must reproduce the critic reference 26/47/91/100 % (U-flat) and
24/40/65/93 % (G p0.5 + jig) within +/-8 points, else STOP.

Usage: /usr/bin/python3 s7_fir_robust_design.py [--mc 1000] [--no-mc]      (runtime ~1 min)
"""
import os
import sys
import csv
import time
import argparse
import warnings

import numpy as np
from scipy.signal.windows import chebwin

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "acoustic")))
import s7_common as S  # noqa: E402  (read-only import)

SEED = 20260926
FSAMP = 48000.0
FRAME = 64
NBIN = 2049
FGRID = np.linspace(0.0, FSAMP / 2, NBIN)
XC = S.X[:8].copy()                # pair c <-> elements {c, 15-c}
A0 = 2.0 * np.ones(8)
TAPS = (63, 127, 255)              # 64/128/256-tap class (odd -> integer delay, exact flat on-axis)
BANDS = (250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300)
# JY/T table 9 thresholds (grade1, grade2, grade3), dB.  SOURCE: sprint3/audit/std_table9_compliance.csv
# (columns L1_thr/L2_thr/L3_thr), = PRD v2.4 section 3.1 12-point caliber (sprint2/docs/prd_update.md:108-111):
# {30, 90, 180 deg} x {500, 1k, 2k, 4k}.  The 4 points at 180 deg are NOT evaluable in this model (isotropic
# line source radiates the same level front and back, R9 artefact) -> reported as NA, never graded.
JYT = {
    (30, 500): (5, 3, 1), (30, 1000): (18, 15, 12), (30, 2000): (20, 17, 14), (30, 4000): (22, 19, 16),
    (90, 500): (10, 8, 6), (90, 1000): (20, 17, 14), (90, 2000): (25, 22, 19), (90, 4000): (10, 8, 6)}
JYT_NA_180 = {(180, 500): (12, 10, 8), (180, 1000): (20, 17, 14), (180, 2000): (20, 17, 14), (180, 4000): (20, 17, 14)}
BLEND = dict(lf0=420.0, lf1=700.0, hf0=5200.0, hf1=6200.0)
SMOOTH_FWHM_OCT = 1.0 / 6.0
CFG = {
    # V1 "keep 1 kHz narrow": protect 60-90 deg, NO mid-sector push at 1 kHz (keeps BW ~ Dolph-20),
    #    small mid-sector control ramped in above 1.2 kHz for JY/T 30-deg grade 1 at 2k/4k.
    #    BW target "BW@1k <= ~31 deg" = coordinator task brief for V1; reference line = old internal
    #    "BW(-6 dB full)@1k <= 30 deg", now an engineering reference only (sprint2/docs/prd_update.md:111,120,165).
    "V1": dict(ths=60.0, beta=1.2, eta_lo=0.0, eta_hi=0.05, eta_f0=1150.0, eta_f1=1700.0),
    # V1n "narrow at short FIR": as V1 but the protected sector starts at 80 deg below 0.8 kHz and opens to
    #    60 deg above 1.3 kHz (the 0.7-0.9 kHz wide-beam weights otherwise leak into a 128-tap 1 kHz beam).
    "V1n": dict(ths=60.0, ths_lo=80.0, ths_fa=800.0, ths_fb=1300.0, beta=1.2, eta_lo=0.0, eta_hi=0.05,
                eta_f0=1150.0, eta_f1=1700.0),
    # V2 "max side rejection": protect the wider 45-90 deg sector (accepts a wider 1 kHz beam).
    "V2": dict(ths=45.0, beta=1.2, eta_lo=0.02, eta_hi=0.02, eta_f0=1150.0, eta_f1=1700.0),
}
FIT_MU_OUT = 0.3        # relative LS weight of the fixed-taper regions (LF/HF) in the FIR fit
FIT_GAMMA = 1.0         # relative weight of whole-pattern fidelity (0-90 deg) in the FIR fit metric
LOG_LINES = []


def log(s=""):
    print(s)
    LOG_LINES.append(s)


# ---------------------------------------------------------------------------------------------
# error model (U-flat project convention) -> design load
# ---------------------------------------------------------------------------------------------
def sigma2_gain(rng, n=400000):
    g = 10 ** (rng.uniform(-1, 1, n) / 20) * np.exp(1j * np.deg2rad(rng.uniform(-5, 5, n)))
    return float(np.mean(np.abs(g - 1) ** 2))


SIG_X2 = (0.5e-3) ** 2 / 3.0     # U(+/-0.5 mm) variance, position along the line axis


# ---------------------------------------------------------------------------------------------
# per-bin robust design
# ---------------------------------------------------------------------------------------------
def steer(th_deg, f):
    k = 2 * np.pi * f / S.C
    return 2 * np.cos(k * np.outer(np.sin(np.deg2rad(np.atleast_1d(th_deg))), XC))   # (nth, 8)


def sector_cov(th0, th1, f, step=0.25):
    if th1 - th0 < 1e-9:
        return np.zeros((8, 8))
    th = np.arange(th0, th1 + 1e-9, step)
    a = steer(th, f)
    return a.T @ a / len(th)


def rcos(f, f0, f1):
    """0 below f0, 1 above f1, raised cosine in log2 f."""
    f = np.maximum(np.asarray(f, float), 1e-3)
    t = np.clip((np.log2(f) - np.log2(f0)) / (np.log2(f1) - np.log2(f0)), 0, 1)
    return 0.5 - 0.5 * np.cos(np.pi * t)


def d20_norm():
    w8 = S.read_w8()[0]
    return w8 / (2 * w8.sum())


def d35_norm():
    w8 = S.w_norm(chebwin(16, 35))[:8]
    return w8 / (2 * w8.sum())


def eta_of(f, cfg):
    return cfg["eta_lo"] + (cfg["eta_hi"] - cfg["eta_lo"]) * rcos(f, cfg["eta_f0"], cfg["eta_f1"])


def q_matrix(f, cfg, sig2g):
    k = 2 * np.pi * f / S.C
    lam = 2.0 * (sig2g + k * k * SIG_X2)
    sm = min(1.0, cfg["beta"] * S.C / max(f, 1.0) / (S.N * S.D))
    thm = np.rad2deg(np.arcsin(sm))
    ths = cfg["ths"]
    if "ths_lo" in cfg:     # optional frequency-dependent sector start (V1n)
        ths = cfg["ths_lo"] + (cfg["ths"] - cfg["ths_lo"]) * float(rcos(f, cfg["ths_fa"], cfg["ths_fb"]))
    Q = sector_cov(ths, 90.0, f) + eta_of(f, cfg) * sector_cov(min(thm, ths), ths, f)
    return Q + lam * np.eye(8)


def perbin_design(cfg, sig2g):
    """Returns target W (NBIN,8) [blended, unsmoothed], Q (NBIN,8,8), share of robust design beta_rob,
    whole-pattern covariance R_all (NBIN,8,8) = mean over 0-90 deg (used only as a FIT-fidelity metric)."""
    d20 = d20_norm()
    W = np.tile(d20, (NBIN, 1))
    Qs = np.zeros((NBIN, 8, 8))
    Ra = np.zeros((NBIN, 8, 8))
    brob = rcos(FGRID, BLEND["lf0"], BLEND["lf1"]) * (1 - rcos(FGRID, BLEND["hf0"], BLEND["hf1"]))
    for i, f in enumerate(FGRID):
        if f < 50.0:
            Qs[i] = np.eye(8)
            Ra[i] = np.eye(8)
            continue
        Ra[i] = sector_cov(0.0, 90.0, f, step=0.5)
        Q = q_matrix(f, cfg, sig2g)
        Qs[i] = Q
        if brob[i] > 0:
            v = np.linalg.solve(Q, A0)
            h = v / (A0 @ v)
            W[i] = brob[i] * h + (1 - brob[i]) * d20
    return W, Qs, brob, Ra


def smooth_logf(W, fwhm_oct):
    sig = fwhm_oct / 2.3548
    lf = np.log2(np.maximum(FGRID, 20.0))
    K = np.exp(-0.5 * ((lf[:, None] - lf[None, :]) / sig) ** 2)
    K /= K.sum(1, keepdims=True)
    Ws = K @ W
    return Ws / (Ws @ A0)[:, None]          # convex combination keeps a0^T W = 1; renorm = numerics only


def roughness(W, f0=500.0, f1=5500.0, step_oct=1.0 / 48):
    lfg = np.arange(np.log2(f0), np.log2(f1), step_oct)
    Wi = np.stack([np.interp(2 ** lfg, FGRID, W[:, c]) for c in range(8)], 1)
    d2 = np.diff(Wi, 2, axis=0) / step_oct ** 2
    return float(np.sqrt(np.mean(d2 ** 2)) / np.mean(np.abs(Wi)))


# ---------------------------------------------------------------------------------------------
# FIR realisation (type-I linear phase, exact flat on-axis constraint)
# ---------------------------------------------------------------------------------------------
def cos_basis(f, M):
    w = 2 * np.pi * np.asarray(f, float) / FSAMP
    B = 2 * np.cos(np.outer(w, np.arange(M + 1)))
    B[:, 0] = 1.0
    return B                                  # (F, M+1): A_c(f) = B @ p_c


def fit_fir(Wt, Qs, brob, L, Ra=None, gamma=0.0):
    M = (L - 1) // 2
    B = cos_basis(FGRID, M)
    F = NBIN
    # per-bin fit metric: robust region -> Q/(W^T Q W) (relative excess side power) + gamma *
    # R_all/(W^T R_all W) (relative whole-pattern error, keeps the main lobe / BW of the target);
    # fixed-taper region -> mu * I/(W^T W) (relative weight error). log-f density: 1/max(f,200).
    dens = 1.0 / np.maximum(FGRID, 200.0)
    dens /= dens.sum()
    K = np.zeros((F, 8, 8))
    for i in range(F):
        w = Wt[i]
        qn = Qs[i] / max(w @ Qs[i] @ w, 1e-30)
        In = np.eye(8) / (w @ w)
        rn = 0.0 if (Ra is None or gamma == 0.0) else gamma * Ra[i] / max(w @ Ra[i] @ w, 1e-30)
        K[i] = dens[i] * (brob[i] * (qn + rn) + (1 - brob[i]) * FIT_MU_OUT * In)
    Kf = K.reshape(F, 64)
    T = (B[:, :, None] * Kf[:, None, :]).reshape(F, (M + 1) * 64)
    Hraw = (B.T @ T).reshape(M + 1, M + 1, 8, 8)           # [n, m, c, d]
    H = Hraw.transpose(2, 1, 3, 0).reshape(8 * (M + 1), 8 * (M + 1))   # [(c,m),(d,n)]
    H = 0.5 * (H + H.T)
    KW = np.einsum("fcd,fd->fc", K, Wt)                     # (F,8)
    g = (B.T @ KW).T.reshape(-1)                            # [(c,m)]
    nx = 8 * (M + 1)
    Cm = np.zeros((M + 1, nx))
    for c in range(8):
        Cm[:, c * (M + 1):(c + 1) * (M + 1)] = np.eye(M + 1)
    b = np.zeros(M + 1)
    b[0] = 0.5                                              # sum_c p_c[0] = 1/2 ; sum_c p_c[m>0] = 0
    ridge = 1e-10 * np.trace(H) / nx
    KKT = np.block([[H + ridge * np.eye(nx), Cm.T], [Cm, np.zeros((M + 1, M + 1))]])
    sol = np.linalg.solve(KKT, np.concatenate([g, b]))
    P = sol[:nx].reshape(8, M + 1)
    h = np.zeros((8, L))
    h[:, M] = P[:, 0]
    for m in range(1, M + 1):
        h[:, M - m] = P[:, m]
        h[:, M + m] = P[:, m]
    return P, h


class Design:
    """Frequency response provider: A(f) -> (F, 8) real zero-phase channel responses, sum 2A = 1."""

    def __init__(self, name, kind, taps=None, table=None, P=None, Wt=None):
        self.name, self.kind, self.taps = name, kind, taps
        self.table, self.P, self.Wt = table, P, Wt

    def A(self, f):
        f = np.atleast_1d(np.asarray(f, float))
        if self.kind == "table":
            return np.tile(self.table, (len(f), 1))
        if self.kind == "fir":
            return cos_basis(f, self.P.shape[1] - 1) @ self.P.T
        return np.stack([np.interp(f, FGRID, self.Wt[:, c]) for c in range(8)], 1)   # ideal per-bin

    def label(self):
        return f"{self.name}" + (f"-{self.taps + 1}t" if self.taps else "")


# ---------------------------------------------------------------------------------------------
# metrics of a design
# ---------------------------------------------------------------------------------------------
def band_freqs(fc, n=31):
    return np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), n)


def pat_power(des, fs, th_deg):
    """|AF|^2 (F, nth) using the 8-pair form."""
    Af = des.A(fs)                                          # (F,8)
    k = 2 * np.pi * fs / S.C
    st = np.sin(np.deg2rad(np.atleast_1d(th_deg)))
    G = 2 * np.cos(k[:, None, None] * st[None, :, None] * XC[None, None, :])   # (F,nth,8)
    return np.einsum("fc,ftc->ft", Af, G) ** 2


def band_att(des, fc, th):
    fs = band_freqs(fc)
    p = pat_power(des, fs, [0.0, th]).sum(0)
    return float(10 * np.log10(p[0] / p[1]))


def band_sector_worst(des, fc, th0=60.0, th1=90.0):
    fs = band_freqs(fc)
    th = np.concatenate([[0.0], np.arange(th0, th1 + 1e-9, 0.25)])
    p = pat_power(des, fs, th).sum(0)
    return float(10 * np.log10(p[0] / p[1:].max()))


def band_wng(des, fc):
    fs = band_freqs(fc)
    Af = des.A(fs)
    num = (2 * Af.sum(1)) ** 2
    den = S.N * 2 * (Af ** 2).sum(1)
    return float(10 * np.log10(num.sum() / den.sum()))


def bw_at(des, f):
    w16 = S.expand16(des.A([f])[0])
    return S.bw_full(S.pattern_db(f, w16))


def d20_axis_level():
    w8 = S.read_w8()[0]
    return 2 * w8.sum() / w8.max()                          # on-axis sum at full drive, units of one driver


def onaxis_level_band(des, fc):
    fs = band_freqs(fc)
    Af = des.A(fs)
    lvl = np.abs(2 * Af.sum(1)).mean() / np.abs(Af).max()
    return float(20 * np.log10(lvl / d20_axis_level()))


def onaxis_level_global(des):
    Af = des.A(FGRID)
    return float(20 * np.log10(np.abs(2 * Af.sum(1)).mean() / np.abs(Af).max() / d20_axis_level()))


def l1_level(h):
    return float(20 * np.log10(1.0 / np.abs(h).sum(1).max() / d20_axis_level()))


def ripple_db(des, P=None):
    f = np.linspace(20.0, 20000.0, 4000)
    Af = des.A(f) if P is None else cos_basis(f, P.shape[1] - 1) @ P.T
    s = np.abs(2 * Af.sum(1))
    return float(np.max(np.abs(20 * np.log10(s))))


def quantize_q15(P):
    s = 1.0 / np.abs(P).max()
    return np.round(P * s * 32767.0) / (32767.0 * s)


def att_single(des, f, th):
    p = pat_power(des, np.array([float(f)]), [0.0, th])[0]
    return float(10 * np.log10(p[0] / p[1]))


def att_inband_min(des, fc, th):
    fs = band_freqs(fc)
    p = pat_power(des, fs, [0.0, th])
    return float(np.min(10 * np.log10(p[:, 0] / p[:, 1])))


def sig2_tot(f, sig2g):
    return sig2g + (2 * np.pi * np.asarray(f, float) / S.C) ** 2 * SIG_X2     # position term at 90 deg


def err_floor_band(des, fc, sig2g):
    """Mean random-error side floor, band power ratio: sum|sum w|^2 / sum sigma^2 ||w||^2  (element coords)."""
    fs = band_freqs(fc)
    Af = des.A(fs)
    num = ((2 * Af.sum(1)) ** 2).sum()
    den = (sig2_tot(fs, sig2g) * 2 * (Af ** 2).sum(1)).sum()
    return float(10 * np.log10(num / den))


def grade(val, thr):
    for gi, t in enumerate(thr):
        if val >= t:
            return gi + 1
    return 0      # 0 = below grade 3


# ---------------------------------------------------------------------------------------------
# Monte Carlo (re-implementation of critic2/mc2.py convention; own seed)
# ---------------------------------------------------------------------------------------------
MC_BF = {fc: band_freqs(fc) for fc in (1000, 2000, 4000)}
MC_PG = np.geomspace(1000 * 2 ** (-1 / 6), 4000 * 2 ** (1 / 6), 40)     # jig/pairing grid 0.9-4.5 kHz
FALL = np.concatenate([MC_BF[1000], MC_BF[2000], MC_BF[4000], MC_PG])
ULOG = np.log2(FALL / 2000.0)
SLB = {1000: slice(0, 31), 2000: slice(31, 62), 4000: slice(62, 93)}
SPG = slice(93, 133)
NF0 = len(FALL)                                                          # original grid (jig / pairing / cal)
MC_B7 = (1000, 1250, 1600, 2000, 2500, 3150, 4000)                       # DEC-S7-SIDE30-01 (1) bands
FEXT = np.concatenate([band_freqs(fc) for fc in (1250, 1600, 2500, 3150)])
FX = np.concatenate([FALL, FEXT])                                        # extended evaluation grid
ULOGX = np.log2(FX / 2000.0)
SLX = dict(SLB)
SLX.update({1250: slice(NF0, NF0 + 31), 1600: slice(NF0 + 31, NF0 + 62), 2500: slice(NF0 + 62, NF0 + 93),
            3150: slice(NF0 + 93, NF0 + 124)})
I3 = [MC_B7.index(fc) for fc in (1000, 2000, 4000)]
STH = np.array([0.0, 1.0, -1.0])      # sin(theta) for 0, +90, -90
MODELS = [("U-flat", ("U", 1.0, 1.0), 0.0), ("G-p0.5-l1oct+jig0.25", ("G", 0.5, 1.0), 0.25)]
STRATS = [("asbuilt", "as-built"), ("amp", "+gain trim"), ("pair", "+jig-meas pairing+trim"),
          ("cplx", "+complex cal (no pairing)"), ("paircplx", "+pairing+complex cal")]
REF_D35 = {"U-flat": {"asbuilt": 26, "amp": 47, "pair": 91, "paircplx": 100},
           "G-p0.5-l1oct+jig0.25": {"asbuilt": 24, "amp": 40, "pair": 65, "paircplx": 93}}


def gp(rng, n, ell, K=40):
    om = rng.normal(0, 1 / ell, (n, K))
    ph = rng.uniform(0, 2 * np.pi, (n, K))
    return np.sqrt(2 / K) * np.cos(om[:, :, None] * ULOGX[None, None, :] + ph[:, :, None]).sum(1)


def draw(rng, n, model):
    kind, p, ell = model
    if kind == "U":
        a = rng.uniform(-1, 1, n)[:, None] * np.ones(len(FX))
        f = rng.uniform(-5, 5, n)[:, None] * np.ones(len(FX))
    else:
        sa, sf = 1 / np.sqrt(3), 5 / np.sqrt(3)
        a = sa * (np.sqrt(p) * rng.normal(0, 1, n)[:, None] + np.sqrt(1 - p) * gp(rng, n, ell))
        f = sf * (np.sqrt(p) * rng.normal(0, 1, n)[:, None] + np.sqrt(1 - p) * gp(rng, n, ell))
    return 10 ** (a / 20) * np.exp(1j * np.deg2rad(f))


def meas(rng, e, sm):
    n, F = e.shape
    return e * 10 ** ((rng.normal(0, sm, (n, 1)) + rng.normal(0, 0.1, (n, F))) / 20) * \
        np.exp(1j * np.deg2rad(rng.normal(0, 6 * sm, (n, 1)) + rng.normal(0, 0.5, (n, F))))


def greedy(m):
    n = m.shape[0]
    Dm = np.mean(np.abs(m[:, None, :] - m[None, :, :]) ** 2, axis=2)
    Dm[np.arange(n), np.arange(n)] = np.inf
    left = set(range(n))
    pairs = []
    while len(left) >= 2 and len(pairs) < 8:
        Lk = sorted(left)
        sub = Dm[np.ix_(Lk, Lk)]
        i, j = np.unravel_index(np.argmin(sub), sub.shape)
        a, b = Lk[i], Lk[j]
        pairs.append((a, b))
        left -= {a, b}
    return pairs


def mc_cell(designs, model, sm, strat, M, seed):
    """Common random numbers: the same M arrays (errors, jig noise, positions) for every design."""
    rng = np.random.default_rng(seed)
    AF = {d.label(): d.A(FX) for d in designs}                          # (F,8) each, extended grid
    rank = {d.label(): np.abs(AF[d.label()][SPG]).mean(0) for d in designs}
    res = {d.label(): np.empty((M, len(MC_B7))) for d in designs}
    side = {d.label(): np.empty((M, len(MC_B7), 2)) for d in designs}   # per-side P(+-90)/P(0), for mean-power att
    k = 2 * np.pi * FX / S.C
    for t in range(M):
        e = draw(rng, 16, model)                                        # (16, len(FX)); same draws as before
        mm = meas(rng, e[:, :NF0], sm)                                  # jig only on the original grid
        dx = rng.uniform(-5e-4, 5e-4, 16)
        ph = np.exp(1j * k[:, None, None] * STH[None, :, None] * (S.X + dx)[None, None, :])   # (F,3,16)
        pairs_g = greedy(mm) if strat in ("pair", "paircplx") else None
        for d in designs:
            lab = d.label()
            if pairs_g is None:
                pairs = [(c, 15 - c) for c in range(8)]
                chans = list(range(8))
            else:
                pairs = pairs_g
                chans = list(np.argsort(-rank[lab]))
            E = np.empty((16, len(FX)), complex)
            for (i, j), c in zip(pairs, chans):
                pm = (mm[i] + mm[j]) / 2
                if strat == "asbuilt":
                    g = np.ones(len(FX))
                elif strat in ("cplx", "paircplx"):
                    inv = 1 / pm[SPG]
                    g = np.interp(FX, FALL[SPG], inv.real) + 1j * np.interp(FX, FALL[SPG], inv.imag)
                else:
                    g = np.ones(len(FX)) / np.sqrt(np.mean(np.abs(pm[SPG]) ** 2))
                E[c] = e[i] * g
                E[15 - c] = e[j] * g
            w16 = np.concatenate([AF[lab], AF[lab][:, ::-1]], axis=1)       # (F,16) centre-symmetric
            for bi, fc in enumerate(MC_B7):
                sl = SLX[fc]
                amp = np.einsum("fn,fn,fan->fa", w16[sl], E[:, sl].T, ph[sl])
                P = (np.abs(amp) ** 2).sum(0)
                res[lab][t, bi] = 10 * np.log10(P[0] / max(P[1], P[2]))
                side[lab][t, bi, :] = P[1:] / P[0]
    return res, side


# ---------------------------------------------------------------------------------------------
# near-field sensitivity (exact point-source distances, mic on axis extension vs on normal)
# ---------------------------------------------------------------------------------------------
def nf_band_att(des, fc, r, npts=41, single=False):
    fs = np.array([float(fc)]) if single else band_freqs(fc, npts)
    Af = des.A(fs)
    w16 = np.concatenate([Af, Af[:, ::-1]], axis=1)
    k = 2 * np.pi * fs / S.C
    rf = np.sqrt(S.X ** 2 + r ** 2)
    rs = np.abs(r - S.X)
    pf = np.abs((w16 * np.exp(-1j * k[:, None] * rf[None, :]) / rf[None, :]).sum(1)) ** 2
    ps = np.abs((w16 * np.exp(-1j * k[:, None] * rs[None, :]) / rs[None, :]).sum(1)) ** 2
    return float(10 * np.log10(pf.mean() / ps.mean()))


# ---------------------------------------------------------------------------------------------
def write_csv(name, header, rows):
    with open(os.path.join(HERE, name), "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(header)
        wr.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", type=int, default=1000)
    ap.add_argument("--no-mc", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    log(f"S7 side-30 per-channel FIR robust beamformer prototype   SEED={SEED}   [L2 sim; MAC [L3]; error model [L4]]")
    anc = S.assert_anchors(verbose=True)
    log("ANCHORS PASS: " + ", ".join(f"{k}={v:.6g}" for k, v in anc.items()))
    rng = np.random.default_rng(SEED)
    sig2g = sigma2_gain(rng)
    log(f"design load: sigma^2_gain(U +/-1dB,+/-5deg) = {sig2g:.5f} (MC, seed {SEED}); sigma_x^2 = {SIG_X2:.3e} m^2;"
        f" lam(1k)={2*(sig2g+(2*np.pi*1000/S.C)**2*SIG_X2):.5f} lam(4k)={2*(sig2g+(2*np.pi*4000/S.C)**2*SIG_X2):.5f}")
    log(f"band blend: Dolph-20 below {BLEND['lf0']:.0f}->{BLEND['lf1']:.0f} Hz, Dolph-20 above {BLEND['hf0']:.0f}->{BLEND['hf1']:.0f} Hz;"
        f" smoothing FWHM {SMOOTH_FWHM_OCT:.3f} oct; grid {NBIN} bins df={FGRID[1]:.2f} Hz")

    d20 = Design("Dolph-20", "table", table=d20_norm())
    d35 = Design("Dolph-35", "table", table=d35_norm())
    designs_eval = [d20, d35]
    fir = {}
    coef_rows = []
    for vn, cfg in CFG.items():
        log(f"\n--- design {vn}: {cfg}")
        Wraw, Qs, brob, Ra = perbin_design(cfg, sig2g)
        Ws = smooth_logf(Wraw, SMOOTH_FWHM_OCT)
        log(f"  roughness (rms d2W/d(log2f)^2 / mean|W|, 0.5-5.5k): raw {roughness(Wraw):.3f} -> smoothed {roughness(Ws):.3f}")
        ideal = Design(f"{vn}-ideal", "ideal", Wt=Ws)
        designs_eval.append(ideal)
        for L in TAPS:
            ts = time.time()
            P, h = fit_fir(Ws, Qs, brob, L, Ra, FIT_GAMMA)
            des = Design(vn, "fir", taps=L, P=P)
            fir[(vn, L)] = (des, h)
            designs_eval.append(des)
            hs = h.sum(0) * 2
            dl = np.zeros(L)
            dl[(L - 1) // 2] = 1.0
            log(f"  FIR {L:3d} taps (slot {L+1}): fit {time.time()-ts:4.1f}s  max|sum_c 2h_c - delta| = {np.abs(hs-dl).max():.2e}"
                f"  ripple float {ripple_db(des):.2e} dB  Q15 {ripple_db(des, quantize_q15(P)):.4f} dB")
            if L == 127 and vn in ("V1", "V2"):
                for c in range(8):
                    coef_rows.append([vn, L, c] + [f"{v:.10e}" for v in h[c]])

    # ---------------- band table ----------------
    log("\n=== REALISED designs, 1/3-oct band metrics [L2]  (att90 worse side | worst 60-90 sector | att30 | WNG_norm | on-axis full-drive vs D20)")
    brow = []
    for des in designs_eval:
        a90 = [band_att(des, fc, 90.0) for fc in BANDS]
        sec = [band_sector_worst(des, fc) for fc in BANDS]
        a30 = [band_att(des, fc, 30.0) for fc in BANDS]
        wng = [band_wng(des, fc) for fc in BANDS]
        lvl = [onaxis_level_band(des, fc) for fc in BANDS]
        flo = [err_floor_band(des, fc, sig2g) for fc in BANDS]
        for i, fc in enumerate(BANDS):
            brow.append([des.label(), fc, f"{a90[i]:.2f}", f"{sec[i]:.2f}", f"{a30[i]:.2f}", f"{wng[i]:.2f}", f"{lvl[i]:.2f}",
                         f"{flo[i]:.2f}"])
        log(f"  {des.label():14s} att90 " + " ".join(f"{fc}:{v:5.1f}" for fc, v in zip(BANDS, a90)))
        log(f"  {'':14s} sec60 " + " ".join(f"{fc}:{v:5.1f}" for fc, v in zip(BANDS, sec)))
        log(f"  {'':14s} att30 " + " ".join(f"{fc}:{v:5.1f}" for fc, v in zip(BANDS, a30)))
        log(f"  {'':14s} WNGn  " + " ".join(f"{fc}:{v:5.2f}" for fc, v in zip(BANDS, wng)))
        log(f"  {'':14s} lvl   " + " ".join(f"{fc}:{v:+5.2f}" for fc, v in zip(BANDS, lvl)))
        log(f"  {'':14s} floor " + " ".join(f"{fc}:{v:5.1f}" for fc, v in zip(BANDS, flo)))
    write_csv("s7_fir_bands.csv", ["design", "band_fc_hz", "att90_worse_db", "worst_60_90_db", "att30_db",
                                   "wng_norm_db", "onaxis_fulldrive_vs_d20_db", "err_floor_mean_db"], brow)
    log(f"  error floor = sigma^2*||w||^2/|sum w|^2 (mean side power of random errors; sigma^2 = {sig2g:.5f} + (k sigma_x)^2):"
        f" uniform-weight bound sigma^2/16 = {10*np.log10(16/sig2g):.2f} dB (gain+phase only) ;"
        f" {10*np.log10(16/sig2_tot(1000, sig2g)):.2f} / {10*np.log10(16/sig2_tot(2000, sig2g)):.2f}"
        f" / {10*np.log10(16/sig2_tot(4000, sig2g)):.2f} dB @1k/2k/4k incl. the +/-0.5 mm position term")

    # ---------------- summary: BW, JY/T, level, delay ----------------
    log("\n=== SUMMARY [L2]: BW(-6 full, single f) | JY/T: 8 of 12 points evaluable (180 deg NA: isotropic front/back"
        " symmetric, R9), 1/3-oct band grade | on-axis level vs D20")
    srow = []
    jrow = []
    for des in designs_eval:
        bw = {f: bw_at(des, f) for f in (1000, 2000, 4000)}
        pts = {}
        for (th, f), thr in JYT.items():
            v = band_att(des, f, th)
            vs = att_single(des, f, th)
            vm = att_inband_min(des, f, th)
            pts[(th, f)] = (v, grade(v, thr))
            jrow.append([des.label(), th, f, f"{v:.2f}", f"{vs:.2f}", f"{vm:.2f}", thr[0], f"{v-thr[0]:+.2f}", grade(v, thr)])
        for (th, f), thr in JYT_NA_180.items():
            jrow.append([des.label(), th, f, "NA", "NA", "NA", thr[0], "NA", "NA(not evaluable: isotropic front=back, R9)"])
        lg = onaxis_level_global(des)
        l1 = l1_level(fir[(des.name, des.taps)][1]) if des.kind == "fir" else (lg if des.kind == "table" else float("nan"))
        gl = [g for (_, g) in pts.values()]
        worst_grade = 0 if 0 in gl else max(gl)          # grade 1 = best; 0 = below grade 3 (worst)
        srow.append([des.label(), f"{bw[1000]:.2f}", f"{bw[2000]:.2f}", f"{bw[4000]:.2f}", f"{lg:.2f}", f"{l1:.2f}", worst_grade,
                     (des.taps - 1) // 2 if des.taps else 0])
        log(f"  {des.label():14s} BW 1k/2k/4k {bw[1000]:5.1f}/{bw[2000]:5.1f}/{bw[4000]:4.1f}"
            f" | lvl global {lg:+5.2f} dB, L1-bound {l1:+5.2f} dB | JY/T worst grade {worst_grade} (8/12 evaluable, 180 NA) | "
            + " ".join(f"{th}/{f}:{v:4.1f}(g{g})" for (th, f), (v, g) in pts.items()))
    write_csv("s7_fir_summary.csv", ["design", "bw6_1k_deg", "bw6_2k_deg", "bw6_4k_deg", "onaxis_level_global_vs_d20_db",
                                     "onaxis_level_L1bound_vs_d20_db", "jyt_worst_grade_of_8_evaluable(0=below g3; 180deg NA)",
                                     "group_delay_samples"], srow)
    write_csv("s7_fir_jyt.csv", ["design", "angle_deg", "band_fc_hz", "att_band_db", "att_single_f_db", "att_inband_min_db",
                                 "grade1_thr_db", "margin_band_to_grade1_db", "grade(0=below g3; NA=not evaluable)"], jrow)
    log("  JY/T 30-deg detail (band / single-f / in-band min / margin to grade 1) -- NO tolerance MC was run at 30 deg:")
    for r in jrow:
        if r[1] == 30 and r[2] in (1000, 2000, 4000) and (r[0].startswith("V1") or r[0].startswith("V2") or r[0].startswith("Dolph")):
            log(f"    {r[0]:14s} 30/{r[2]}: band {r[3]} | single {r[4]} | in-band min {r[5]} | margin {r[7]} dB")
    write_csv("s7_fir_coeffs_127tap.csv", ["variant", "taps", "channel"] + [f"h{n}" for n in range(127)], coef_rows)

    # ---------------- near field sensitivity ----------------
    log("\n=== NEAR-FIELD sensitivity [L2]: band att90 on the array-axis extension at distance r (front ref on normal at r)")
    nrow = []
    for des in [d20, d35] + [fir[(v, 127)][0] for v in CFG]:
        cells = []
        for fc in (1000, 2000, 4000):
            for r in (1.0, 2.0, 4.0, 8.0, 16.0, 1000.0):
                v = nf_band_att(des, fc, r)
                v1 = nf_band_att(des, fc, r, single=True)
                cells.append(f"{fc}@{r:g}m:{v:5.1f}" + (f"({v1:4.1f})" if r <= 2.0 else ""))
                nrow.append([des.label(), fc, r, f"{v:.2f}", f"{v1:.2f}"])
        log(f"  {des.label():14s} " + " ".join(cells))
    log("  (plain values: 1/3-oct band power average, 41 pts -- same convention and same D20 numbers as s7_nearfield_side.py /"
        " S7_SIDE30_ANALYSIS.md:13; values in brackets at 1-2 m: SINGLE frequency at fc -- the convention of the"
        " 18.5/15.8/15.4 D20 figures at S7_SIDE30_ANALYSIS.md:81 / critic R1 F6. Band sampling 41 vs 81 vs 201 pts changes"
        " the D20 1 m band values by <= 0.02 dB, so the two figures differ by band-vs-single-frequency, not by sampling.)")
    nfd = {(r[0], r[1], r[2]): float(r[3]) for r in nrow}
    for lab in [fir[(v, 127)][0].label() for v in CFG]:
        for rr in (1.0, 2.0, 4.0):
            loss = max(nfd[(lab, fc, 1000.0)] - nfd[(lab, fc, rr)] for fc in (1000, 2000, 4000))
            log(f"  {lab}: max loss vs far field over 1k/2k/4k at r={rr:g} m = {loss:.1f} dB")
    write_csv("s7_fir_nearfield.csv", ["design", "band_fc_hz", "r_m", "att90_band_db_41pt", "att90_single_f_db"], nrow)

    # ---------------- compute & latency [L3] ----------------
    log("\n=== COMPUTE & LATENCY [L3 hand count] (frame = 64 samples @48 kHz, 8 channels)")
    nh, nnz = 63, 33
    pushes = (64 + 32 + 16) + 2 * (8 + 16 + 32) + 2 * (8 + 16 + 32)          # dec + ana-interp + syn-interp
    tree_ascoded = 8 * pushes * nh
    tree_eff = 8 * 3 * 56 * nnz                                           # polyphase + zero-skip, per level-sum 56 inputs
    log(f"  tree, C reference code count (tree_filterbank.c:83-205, full 63-tap conv per push): {pushes} pushes/ch x 63 x 8"
        f" = {tree_ascoded:,} MAC/frame [L3]")
    log("    NOTE: that is the C code's count. M2 runs the tree on FIRA (fira_tfb_analyze/synthesize, m1_loopback_tdm.c),"
        " so it is NOT what M2 executes; the comparison also ignores the non-tree part of the M2 load.")
    log(f"  tree (efficient: polyphase + half-band zero-skip, 33 nnz): 3 x 56 x 33 x 8 = {tree_eff:,} MAC/frame [L3]")
    BUDGET = 1333333
    crow = [["tree_c_code_count", 63, tree_ascoded, "", "", "", "", "", "L3 (C code count; M2 runs the tree on FIRA)"],
            ["tree_polyphase_zero_skip", 63, tree_eff, "", "", "", "", "", "L3"]]
    log("  core cycles IF run on the core, project board factor 30-50 cyc/MAC (.claude/skills/dsp-algorithm/SKILL.md:57,69;"
        " decisions_log.md:234; the 50 end is the [L4] board envelope, S7_DSP_ASSESSMENT.md:90):")
    for L in (64, 128, 256):
        full = 8 * L * FRAME
        fold = 8 * (L // 2) * FRAME
        gd = (L - 2) / 2 if L % 2 == 0 else (L - 1) / 2
        log(f"  FIR {L:3d}-tap slot (type-I {L-1} + 1 zero): direct {full:,} MAC/frame ({full/tree_ascoded:.2f}x tree C count,"
            f" {full/tree_eff:.2f}x efficient tree); symmetric-folded {fold:,} mult/frame; group delay {int(gd)} samples"
            f" = {gd/FSAMP*1e3:.2f} ms [L3]")
        log(f"      core cyc/frame: direct {full*30/1e6:.2f}-{full*50/1e6:.2f} M ({full*30/BUDGET:.2f}-{full*50/BUDGET:.2f}x budget);"
            f" folded {fold*30/1e6:.2f}-{fold*50/1e6:.2f} M ({fold*30/BUDGET:.2f}-{fold*50/BUDGET:.2f}x budget)"
            f"  [L3 MAC x 30-50 factor; FIR alone, non-FIR M2 load not included]")
        crow.append([f"fir_{L}", L, full, fold, int(gd), f"{full*30:.0f}", f"{full*50:.0f}", f"{fold*30:.0f}-{fold*50:.0f}",
                     "L3 MAC; cycles = L3 x 30-50 cyc/MAC board factor (50 end L4)"])
    log("  8.51 cyc/MAC = H1 8-tap flat-int kernel (different kernel class): [L3] reference only; its low end is NOT a lower bound"
        " (precedent S7_DSP_ASSESSMENT.md:90).")
    log("  frame budget 1,333,333 cyc assumes CCLK = 1 GHz; DEC-S7-RULINGS-03: recompute from the board CCLK readback (pending)."
        " M2 today 830,903 cyc/frame [L1] incl. FIRA busy-wait.")
    log("  => 128-tap compromise on the core: marginal (folded, 30 cyc/MAC) to ~2.5x over budget (direct, 50 cyc/MAC);"
        " feasibility depends on the FIRA path [L4], needs a bench measurement.")
    write_csv("s7_fir_compute.csv", ["item", "taps", "mac_per_frame_direct", "mult_per_frame_folded", "group_delay_samples",
                                     "core_cyc_direct_30", "core_cyc_direct_50", "core_cyc_folded_30_50", "L"], crow)

    # ---------------- verification-plan numbers [L2] ----------------
    log("\n=== VERIFICATION-PLAN NUMBERS [L2] (FG1 / IO1 / ST1)")
    d20n = d20_norm()
    # design TARGET == Dolph-20 table outside 0.42-6.2 kHz; the REALISED FIR only approaches it (finite length)
    rng_dev = [("20-300", 20.0, 300.0), ("300-420", 300.0, 420.0), ("6.2k-8k", 6200.0, 8000.0), ("8k-20k", 8000.0, 20000.0),
               ("0.7k-5.2k", 700.0, 5200.0)]
    log("  realised max|A_c(f) - DolphTable_c| / max w (dB) per range -- a 'Dolph table everywhere' placeholder differs from the"
        " FIR by this much:")
    vrow = []
    for (vn, L), (des, h) in fir.items():
        devs = []
        for _, a, b in rng_dev:
            ff = np.linspace(a, b, 400)
            devs.append(20 * np.log10(np.abs(des.A(ff) - d20n).max() / d20n.max()))
        vrow.append([des.label()] + [f"{v:.1f}" for v in devs] + [L - 1, L + FRAME - 1, L + 1 + FRAME - 1])
        log(f"  {des.label():10s} " + " ".join(f"{nm}:{v:6.1f}" for (nm, _, _), v in zip(rng_dev, devs))
            + f" | ST1 history {L-1} samples | IO1(a) input {L+FRAME-1} initialised samples"
            f" ({L+1+FRAME-1} if the zero-padded {L+1}-tap slot is loaded) | IO1(b) out_count {FRAME}/ch/frame")
    hu = np.full((8, 127), 0.0)
    hu[:, 63] = 1.0 / 16.0
    log(f"  sum_c 2h_c = delta is NOT a coefficient check: uniform h_c = delta/16 gives max|sum-delta| ="
        f" {np.abs(2*hu.sum(0) - np.eye(1, 127, 63)[0]).max():.1e} (passes) but is a different beam.")
    rb = {}
    with open(os.path.join(HERE, "s7_fir_coeffs_127tap.csv")) as fp:
        for r in csv.DictReader(fp):
            rb.setdefault(r["variant"], []).append([float(r[f"h{n}"]) for n in range(127)])
    for vn, hh in rb.items():
        hh = np.array(hh)
        log(f"  coefficient CSV readback ({vn}, 11 significant digits): max|sum_c 2h_c - delta| ="
            f" {np.abs(2*hh.sum(0) - np.eye(1, 127, 63)[0]).max():.1e}")
    write_csv("s7_fir_verify.csv", ["design"] + [f"dev_vs_dolph_table_{nm}_db" for nm, _, _ in rng_dev]
              + ["st1_history_samples", "io1_input_samples_odd_len", "io1_input_samples_padded_slot"], vrow)

    # ---------------- headroom at equal on-axis gain [L2] ----------------
    log("\n=== HEADROOM at equal on-axis gain to today's M2 (Dolph-20 table, max weight 1.0) [L2]")
    Sg = d20_axis_level()
    pf4 = 20 * np.log10(1.7309)
    log(f"  today's chain: PF-4 input-headroom convention {pf4:.2f} dB (half-band sum|h| = 1.7309,"
        " sprint3/dsp/pf4/WO_node1_saturation_fix.md:40); the tree output itself is PR (<= input)")
    hrow = []
    for (vn, L), (des, h) in fir.items():
        g_l1 = 20 * np.log10(Sg * np.abs(h).sum(1).max())
        g_sin = 20 * np.log10(Sg * np.abs(des.A(FGRID)).max())
        cmax = Sg * np.abs(h).max()
        accb = 46 + int(np.ceil(np.log2(Sg * np.abs(h).sum(1).max())))
        hrow.append([des.label(), f"{g_l1:.2f}", f"{g_sin:.2f}", f"{g_l1-pf4:+.2f}", f"{cmax:.3f}", accb])
        log(f"  {des.label():10s} worst-case channel gain (L1) {g_l1:+5.2f} dB, sine {g_sin:+5.2f} dB -> needs {g_l1:.2f} dB input headroom,"
            f" i.e. {g_l1-pf4:+.2f} dB vs today's {pf4:.2f} dB; max coefficient {cmax:.3f} (Q15 needs {'1 extra shift bit' if cmax >= 1 else 'no shift'});"
            f" Q15xQ31 int64 accumulator peak {accb} bits <= 63")
    write_csv("s7_fir_headroom.csv", ["design", "worst_case_channel_gain_L1_db", "sine_channel_gain_db",
                                      "extra_vs_pf4_4p77db", "max_coeff_equal_gain", "q15xq31_acc_bits"], hrow)

    # ---------------- Monte Carlo ----------------
    if not args.no_mc:
        M = args.mc
        mc_designs = [d20, d35] + [fir[(v, L)][0] for v in CFG for L in TAPS]
        log(f"\n=== MONTE CARLO [L2 sim of an L4 error model]: {M} arrays/cell, common random numbers across designs;"
            f" metric = 1/3-oct band power avg at +/-90, worse side; JOINT7 = all 7 DEC-S7-SIDE30-01 bands"
            f" (1k..4k 1/3-oct) >= 30 dB [headline]; JOINT3 = 1k,2k,4k >= 30 dB [secondary]")
        J3, J7 = {}, {}
        mrow = []
        for mi, (mname, model, sm) in enumerate(MODELS):
            for si, (st, slab) in enumerate(STRATS):
                seed = SEED + 1000 * (mi + 1) + si
                ts = time.time()
                res, side = mc_cell(mc_designs, model, sm, st, M, seed)
                log(f"  [{mname} | {slab}]  seed={seed}  ({time.time()-ts:.1f}s)   median/P10/yield@1k | 2k | 4k | JOINT3 | JOINT7"
                    f" | medians 1.25k/1.6k/2.5k/3.15k")
                for d in mc_designs:
                    r7 = res[d.label()]
                    r = r7[:, I3]
                    joint = float(np.mean(np.all(r >= 30.0, axis=1)) * 100)
                    joint7 = float(np.mean(np.all(r7 >= 30.0, axis=1)) * 100)
                    J3[(d.label(), mname, st)] = joint
                    J7[(d.label(), mname, st)] = joint7
                    cells = " | ".join(f"{np.median(r[:, b]):5.1f}/{np.percentile(r[:, b], 10):5.1f}/{np.mean(r[:, b] >= 30)*100:3.0f}%"
                                       for b in range(3))
                    ext = "/".join(f"{np.median(r7[:, MC_B7.index(fc)]):4.1f}" for fc in (1250, 1600, 2500, 3150))
                    log(f"     {d.label():12s} {cells} | {joint:5.1f}% | {joint7:5.1f}% | {ext}")
                    mp7 = [-10 * np.log10(side[d.label()][:, b, :].mean()) for b in range(len(MC_B7))]
                    mp = [mp7[b] for b in I3]
                    if st == "asbuilt":
                        log(f"       {'':12s} per-side MEAN-power att 1k/2k/4k = {mp[0]:.2f}/{mp[1]:.2f}/{mp[2]:.2f} dB"
                            f" (worse-side median sits below it by {mp[0]-np.median(r[:, 0]):.2f}/{mp[1]-np.median(r[:, 1]):.2f}/"
                            f"{mp[2]-np.median(r[:, 2]):.2f} dB)")
                    for b, fc in enumerate(MC_B7):
                        mrow.append([d.label(), mname, st, fc, f"{np.median(r7[:, b]):.2f}", f"{np.percentile(r7[:, b], 10):.2f}",
                                     f"{np.mean(r7[:, b] >= 30)*100:.1f}", f"{joint:.1f}", f"{joint7:.1f}", f"{mp7[b]:.2f}", seed, M])
                    if d.name == "Dolph-35" and st in REF_D35[mname]:
                        ref = REF_D35[mname][st]
                        ok = abs(joint - ref) <= 8.0
                        log(f"       MC ANCHOR Dolph-35 {mname}/{st}: {joint:.1f}% vs critic ref {ref}% -> {'PASS' if ok else 'FAIL'}")
                        if not ok:
                            write_csv("s7_fir_mc.csv", ["design", "error_model", "strategy", "band_fc_hz", "median_db", "p10_db",
                                                        "yield_ge30_pct", "joint3_yield_pct_1k2k4k", "joint7_yield_pct_DEC1_1k-4k",
                                                        "meanpower_att_per_side_db", "seed", "arrays"], mrow)
                            raise SystemExit("MC ANCHOR FAIL -- stop (MC re-implementation does not reproduce critic reference)")
        write_csv("s7_fir_mc.csv", ["design", "error_model", "strategy", "band_fc_hz", "median_db", "p10_db",
                                    "yield_ge30_pct", "joint3_yield_pct_1k2k4k", "joint7_yield_pct_DEC1_1k-4k",
                                    "meanpower_att_per_side_db", "seed", "arrays"], mrow)
        # ---- summary statistics quoted in the doc (3-band and 7-band) ----
        log("\n=== MC SUMMARY STATISTICS [L2 on L4] (quoted in S7_SIDE30_PERCH_FIR_DESIGN.md)")
        firs = [d.label() for d in mc_designs if d.kind == "fir"]
        mnames = [m[0] for m in MODELS]
        stn = [s_[0] for s_ in STRATS]
        for tag, J in (("JOINT7", J7), ("JOINT3", J3)):
            ab = [J[(f, m, "asbuilt")] for f in firs for m in mnames]
            pc = [J[(f, m, "paircplx")] for f in firs for m in mnames]
            d35 = {(m, s_): J[("Dolph-35", m, s_)] for m in mnames for s_ in stn}
            lead = [(f, m, s_, J[(f, m, s_)] - J[("Dolph-35", m, s_)]) for f in firs for m in mnames for s_ in stn]
            minlead = min(lead, key=lambda x: x[3])
            v12 = [(J[(f"V1-{t}t", m, s_)] - J[(f"V2-{t}t", m, s_)]) for t in (64, 128, 256) for m in mnames for s_ in stn]
            lg = [abs(J[(f"{v}-64t", m, s_)] - J[(f"{v}-256t", m, s_)]) for v in CFG for m in mnames for s_ in stn]
            pt = [J[(f, m, "pair")] - J[(f, m, "amp")] for f in firs + ["Dolph-35"] for m in mnames]
            log(f"  {tag}: FIR as-built {min(ab):.1f}-{max(ab):.1f}% | FIR pair+cplx {min(pc):.1f}-{max(pc):.1f}% | Dolph-35 as-built"
                f" {d35[(mnames[0], 'asbuilt')]:.1f}/{d35[(mnames[1], 'asbuilt')]:.1f}%, pair+trim {d35[(mnames[0], 'pair')]:.1f}/"
                f"{d35[(mnames[1], 'pair')]:.1f}%, pair+cplx {d35[(mnames[0], 'paircplx')]:.1f}/{d35[(mnames[1], 'paircplx')]:.1f}%")
            log(f"     FIR minus Dolph-35 (same model & strategy): min {minlead[3]:+.1f} points ({minlead[0]}, {minlead[1]}, {minlead[2]});"
                f" cells where FIR <= Dolph-35: {sum(1 for x in lead if x[3] <= 0)}/{len(lead)}")
            log(f"     V1 minus V2 (same taps): {sum(1 for x in v12 if x >= 0)}/{len(v12)} cells V1 >= V2; range {min(v12):+.1f}..{max(v12):+.1f}")
            log(f"     |64-tap minus 256-tap| max {max(lg):.1f} points ; pairing gain over trim {min(pt):+.1f}..{max(pt):+.1f} points")
    log(f"\nruntime {time.time()-t0:.0f}s ; outputs in {HERE}")
    with open(os.path.join(HERE, "s7_fir_robust_design.log"), "w") as fp:
        fp.write("\n".join(LOG_LINES) + "\n")


if __name__ == "__main__":
    main()
