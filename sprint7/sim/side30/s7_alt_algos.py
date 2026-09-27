#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s7_alt_algos.py -- S7-SIDE30 desktop evaluation of two cheaper alternatives to the per-channel FIR route
(CTO 2026-09-27 「我同意，你依次干吧」 to the PM proposal "...并在桌面评估 IIR 和延时 CBT 这两个变体"):

  (1) LOW-ORDER IIR frequency-dependent shading.  Source idea: Duran Audio DDC (van Beuningen & Start 2000, Proc.
      IOA 22(6) sec 3.1: per-channel filters, "implemented as Bessel IIR filters ... reduces overall execution time
      compared to a FIR solution"). DDC's own GOAL is constant beamwidth (L_eff = const * lambda); that goal is
      evaluated here as "DDC-literal" (ideal filters). The structure evaluated for OUR goal is a variant:
      a SHARED in-phase Linkwitz-Riley crossover bank on the mono input (K = 2 or 3 bands) + an 8 x K matrix of
      per-channel band gains. Because every LR output of the bank has the same phase and the band magnitudes sum
      to 1, each channel's effective weight W_c(f) = sum_k w_k[c] m_k(f) is REAL and the on-axis response is flat;
      no per-channel delay compensation is needed (DDC needed it). Band 1 (lowest) is FIXED to the frozen Dolph-20
      table (keeps today's 500 Hz behaviour; a free low band went superdirective in the exploratory scan: 12-15 dB
      on-axis loss). The upper bands are designed jointly by the same mean-performance robust criterion as the
      RS tables / FIR prototype (Van Trees 2002 eq. 2.208), over the 7 DEC-S7-SIDE30-01 bands, accounting for
      the crossover blend exactly (KKT solve, constraints sum_c 2 w_k[c] = 1 per band).
  (2) Keele 2002 delay-derived straight-line CBT (AES Conv. paper 5653, eqs 3-7; text registered in
      sprint7/docs/S7_LIT_REGISTER_SIDE30.md #17): Legendre shading U(x) = 1 + 0.066x - 1.8x^2 + 0.743x^3 and
      delays tau = R(1 - cos(asin(h/R)))/c with R = H_T / (2 sin(theta_T/2)), H_T = N d (length extended by one
      spacing, as in the paper). Evaluated with exact delays, with delays rounded to 48 kHz samples, and the
      Legendre shading alone (no delays) as the control.

L-GRADES: ideal metrics [L2/numpy isotropic far-field model s7_common.py]; yields [L2 on L4 spread]; MAC counts [L3
hand count]; core cycles [L3 x the project's 30-50 cyc/MAC board factor; for recursive IIR code the factor itself is
unverified -> L4 envelope]. NOTHING here is measured. Zero firmware change.

CANDIDATE RULE (crossover designs): grid = LR order {4, 8} x crossovers {600, 700, 800, 700/1400, 700/1600, 700/2000,
800/1600 Hz} x objective {(eta 0.1, mid 35-60), (eta 1, mid 30-60), (eta 3, mid 30-60)}; a grid point is a CANDIDATE if
all band gains are >= 0 and all 8 evaluable JY/T points reach grade 1 (single frequency, ideal). Every candidate is
Monte-Carlo'd and listed. The per-family "representative" (families X2-LR4, X3-LR4, X2-LR8, X3-LR8) is the candidate
with the highest U-flat as-built joint7 -- a selection among noisy estimates, so the family spread is printed too.
This rule was written by the PM AFTER an exploratory scan of the same grid (ideal metrics only, no MC).

MC: F.mc_cell imported from fir/s7_fir_robust_design.py, same seeds -> same draws as s7_fir_mc.csv / s7_alt_tables;
anchor: Dolph-20 / Dolph-35 must reproduce s7_fir_mc.csv exactly (else SystemExit). FIR rows are quoted from that CSV.

Usage: /usr/bin/python3 s7_alt_algos.py [--mc 1000]      (runtime ~3-4 min)
"""
import argparse
import csv
import os
import sys
import time
import warnings

import numpy as np
from scipy import signal as sig

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "sprint7", "sim", "acoustic"))
sys.path.insert(0, os.path.join(HERE, "fir"))
sys.path.insert(0, os.path.join(REPO, "sprint7", "dsp", "wtbl"))
import s7_common as S  # noqa: E402
import s7_fir_robust_design as F  # noqa: E402  (module import; main() does not run)
import gen_m2_wtbl as G  # noqa: E402  (module import; main() does not run)

FSAMP = 48000.0
B7 = F.MC_B7
F7 = np.concatenate([F.band_freqs(fc) for fc in B7])
XC = F.XC
ABSX = np.abs(XC)
SIG2G = G.rs_sig2g_closed()
JYT8 = [(30, 500), (90, 500), (30, 1000), (90, 1000), (30, 2000), (90, 2000), (30, 4000), (90, 4000)]
FIR_MC_CSV = os.path.join(HERE, "fir", "s7_fir_mc.csv")
FDENSE = np.geomspace(20.0, 20000.0, 2000)                     # for the full-drive (max gain) normalisation
LOG = []


def log(s=""):
    print(s)
    LOG.append(s)


class CDesign:
    """Complex per-channel responses A(f) -> (F, 8); duck-types F.Design for F.mc_cell."""

    def __init__(self, name, fn, meta=None):
        self.name, self.kind, self.taps, self.fn, self.meta = name, "cplx", None, fn, meta or {}

    def A(self, f):
        return self.fn(np.atleast_1d(np.asarray(f, float)))

    def label(self):
        return self.name


def table_design(name, w8):
    w8 = np.asarray(w8, float)
    t = w8 / (2.0 * w8.sum())
    return CDesign(name, lambda f, t=t: np.tile(t, (len(f), 1)).astype(complex), {"w8": w8})


# ------------------------------------------------------------------------------------------------------------------
# (1) shared in-phase Linkwitz-Riley bank
# ------------------------------------------------------------------------------------------------------------------
def lr_mags(f, xo, order):
    """Band magnitudes of an in-phase LR bank (bilinear, prewarped): LR`order` = Butterworth(order/2)^2.
    K=2: [LP, HP]; K=3: [LP1*LP2, HP1*LP2, AP1*HP2] (AP1 = allpass compensation of the f1 split on the top band).
    All outputs share one phase; magnitudes sum to 1 exactly."""
    f = np.minimum(np.atleast_1d(np.asarray(f, float)), FSAMP / 2 - 1.0)

    def t(fc):
        return (np.tan(np.pi * f / FSAMP) / np.tan(np.pi * fc / FSAMP)) ** order
    lp = [1.0 / (1.0 + t(fc)) for fc in xo]
    hp = [t(fc) / (1.0 + t(fc)) for fc in xo]
    if len(xo) == 1:
        return np.stack([lp[0], hp[0]], 1)
    if len(xo) == 2:
        return np.stack([lp[1] * lp[0], lp[1] * hp[0], hp[1]], 1)
    raise ValueError("K <= 3 only")


def sec_q(f, eta, thm, ths=60.0):
    k = 2 * np.pi * f / S.C
    return F.sector_cov(ths, 90.0, f) + eta * F.sector_cov(thm, ths, f) + 2 * (SIG2G + k * k * F.SIG_X2) * np.eye(8)


_QC = {}


def xo_design(xo, order, eta, thm, fgrid=None):
    """Band 1 fixed = frozen D20 (sum 2w = 1); upper bands minimise mean_f W^T Q W over fgrid (default F7, the 7 DEC
    bands), s.t. sum_c 2 w_k[c] = 1."""
    fgrid = F7 if fgrid is None else fgrid
    K = len(xo) + 1
    nf = K - 1
    d20n = S.read_w8()[0] / (2 * S.read_w8()[0].sum())
    H = np.zeros((8 * nf, 8 * nf))
    g = np.zeros(8 * nf)
    M = lr_mags(fgrid, xo, order)
    for i, f in enumerate(fgrid):
        key = (round(float(f), 6), eta, thm)
        if key not in _QC:
            _QC[key] = sec_q(f, eta, thm)
        Q = _QC[key]
        mf, m1 = M[i, 1:], M[i, 0]
        H += np.kron(np.outer(mf, mf), Q) / len(fgrid)
        g += np.kron(mf, Q @ (m1 * d20n)) / len(fgrid)
    C = np.kron(np.eye(nf), 2 * np.ones((1, 8)))
    kkt = np.block([[H, C.T], [C, np.zeros((nf, nf))]])
    x = np.linalg.solve(kkt, np.concatenate([-g, np.ones(nf)]))[:8 * nf]
    wk = np.vstack([d20n, x.reshape(nf, 8)])
    # self-check: constraints + optimality (random feasible perturbations never lower the objective)
    J = lambda xx: xx @ H @ xx + 2 * g @ xx  # noqa: E731
    rng = np.random.default_rng(7)
    for _ in range(20):
        p = rng.normal(size=8 * nf)
        p -= C.T @ np.linalg.solve(C @ C.T, C @ p)          # project onto the constraint null space
        if J(x + 1e-3 * p) < J(x) - 1e-15:
            raise SystemExit("xo_design: KKT solution not optimal")
    if np.abs(C @ x - 1).max() > 1e-12:
        raise SystemExit("xo_design: constraint violated")
    return wk


def xo_designobj(xo, order, eta, thm, fgrid=None, suffix=""):
    wk = xo_design(xo, order, eta, thm, fgrid)
    name = f"X{len(xo) + 1}-LR{order}-{'/'.join(str(int(v)) for v in xo)}-e{eta:g}m{int(thm)}{suffix}"
    return CDesign(name, lambda f, wk=wk, xo=xo, order=order: (lr_mags(f, xo, order) @ wk).astype(complex),
                   {"wk": wk, "xo": xo, "order": order, "eta": eta, "thm": thm})


def xo_design_freelow(xo, order, eta, thm, mu):
    """EXPLORATORY variant (critic R3f F8): ALL bands free; objective = the 7-band side objective + mu x (500 Hz
    1/3-oct power outside +/-30 deg + error load), i.e. 'also narrow the 500 Hz beam'. Shown only to document why
    band 1 is fixed to D20 (this goes superdirective)."""
    K = len(xo) + 1
    H = np.zeros((8 * K, 8 * K))
    f5 = F.band_freqs(500.0)
    for fs_, wgt, qf in ((F7, 1.0, lambda f: sec_q(f, eta, thm)),
                         (f5, mu, lambda f: F.sector_cov(30.0, 90.0, f) + 2 * (SIG2G + (2 * np.pi * f / S.C) ** 2
                                                                                   * F.SIG_X2) * np.eye(8))):
        M = lr_mags(fs_, xo, order)
        for i, f in enumerate(fs_):
            H += wgt / len(fs_) * np.kron(np.outer(M[i], M[i]), qf(f))
    C = np.kron(np.eye(K), 2 * np.ones((1, 8)))
    Hi = np.linalg.solve(H, C.T)
    wk = (Hi @ np.linalg.solve(C @ Hi, np.ones(K))).reshape(K, 8)
    return CDesign(f"free-low-mu{mu:g}", lambda f, wk=wk: (lr_mags(f, xo, order) @ wk).astype(complex), {"wk": wk})


# ------------------------------------------------------------------------------------------------------------------
# DDC-literal (constant beamwidth) and Keele delay-derived CBT
# ------------------------------------------------------------------------------------------------------------------
def ddc_design(bw_deg):
    """van Beuningen & Start 2000 eq (3-1): L_eff = (69 deg / BW) * lambda; raised-cosine window over the active
    aperture; IDEAL (zero-phase) filters -- an upper bound for what the Bessel-IIR realisation can do.
    Numerical guard only: the active half-aperture is clamped to >= 0.6 spacing (just beyond the centre pair at 0.5 d),
    else all weights vanish at high frequency; the clamp acts only above ~12 kHz (BW 30) and never inside 0.9-4.5 kHz.
    The on-axis full-drive figure of this design is dominated by that high-frequency aperture shrink (flat on-axis with
    ever fewer active drivers = Keele's 6 dB/oct power roll-off); DDC-literal is judged on R90, not on that figure."""
    def fn(f):
        a = np.clip((69.0 / bw_deg) * (S.C / np.maximum(f, 1.0)) / 2, 0.6 * S.D, S.N * S.D / 2)
        u = ABSX[None, :] / a[:, None]
        w = np.where(u < 1, np.cos(np.pi / 2 * u) ** 2, 0.0)
        return (w / (2 * w.sum(1, keepdims=True))).astype(complex)
    return CDesign(f"DDC-BW{bw_deg:.0f}", fn, {"bw": bw_deg})


HT = S.N * S.D      # Keele: "increased in length by one driver-to-driver spacing". NOTE (critic R3f I4): the shading
                    # values in his Fig. 1/2 (13 drivers, outer 0.20) imply H_T = (N+1) d; N d is used here, and the
                    # critic found the conclusion unchanged with (N+1) d.


def legendre_u(x):
    x = np.asarray(x, float)
    return np.where(x <= 1, 1 + 0.066 * x - 1.8 * x ** 2 + 0.743 * x ** 3, 0.0)


def cbt_design(arc_deg, delays=True, qsamp=None):
    R = HT / (2 * np.sin(np.deg2rad(arc_deg) / 2))                      # Keele eq (4)
    tau = R * (1 - np.cos(np.arcsin(ABSX / R))) / S.C                    # eqs (5)-(7)
    if qsamp:
        tau = np.round(tau * qsamp) / qsamp
    U = legendre_u(ABSX / (HT / 2))                                       # eq (3), mapped to position (paper)
    if not delays:
        tau = np.zeros(8)
    name = "Legendre-only" if not delays else f"CBT-arc{arc_deg:.0f}" + ("-int" if qsamp else "")

    def fn(f, tau=tau, U=U):
        return U[None, :] * np.exp(-1j * 2 * np.pi * f[:, None] * tau[None, :]) / (2 * U.sum())
    return CDesign(name, fn, {"arc": arc_deg, "tau_us": tau * 1e6, "U": U})


# ------------------------------------------------------------------------------------------------------------------
# complex-safe metrics
# ------------------------------------------------------------------------------------------------------------------
def patp(d, fs, th):
    A = d.A(fs)
    k = 2 * np.pi * fs / S.C
    st = np.sin(np.deg2rad(np.atleast_1d(th)))
    Gm = 2 * np.cos(k[:, None, None] * st[None, :, None] * XC[None, None, :])
    return np.abs(np.einsum("fc,ftc->ft", A, Gm)) ** 2


def band_att(d, fc, th):
    p = patp(d, F.band_freqs(fc), [0.0, th]).sum(0)
    return float(10 * np.log10(p[0] / p[1]))


def sector_worst(d, fc):
    th = np.concatenate([[0.0], np.arange(60.0, 90.0 + 1e-9, 0.25)])
    p = patp(d, F.band_freqs(fc), th).sum(0)
    return float(10 * np.log10(p[0] / p[1:].max()))


def single_att(d, f, th):
    p = patp(d, np.array([float(f)]), [0.0, th])[0]
    return float(10 * np.log10(p[0] / p[1]))


def inband_min(d, fc, th):
    p = patp(d, F.band_freqs(fc), [0.0, th])
    return float(np.min(10 * np.log10(p[:, 0] / p[:, 1])))


def bw_at(d, f):
    P = patp(d, np.array([float(f)]), S.ANG)[0]
    return S.bw_full(10 * np.log10(P / P.max()))


def onaxis_band(d, fc, amax):
    A = d.A(F.band_freqs(fc))
    return float(20 * np.log10(np.abs(2 * A.sum(1)).mean() / amax / F.d20_axis_level()))


def err_floor(d, fc):
    fs = F.band_freqs(fc)
    A = d.A(fs)
    s2 = SIG2G + (2 * np.pi * fs / S.C) ** 2 * F.SIG_X2
    return float(10 * np.log10((np.abs(2 * A.sum(1)) ** 2).sum() / (s2 * 2 * (np.abs(A) ** 2).sum(1)).sum()))


def ideal(d):
    amax = float(np.abs(d.A(FDENSE)).max())
    m = {"r90": [band_att(d, fc, 90.0) for fc in B7], "sec": [sector_worst(d, fc) for fc in B7],
         "flo": [err_floor(d, fc) for fc in B7], "ax": [onaxis_band(d, fc, amax) for fc in B7],
         "jy": [single_att(d, f, th) for th, f in JYT8], "jyib": [inband_min(d, f, th) for th, f in JYT8],
         "bw1k": bw_at(d, 1000.0), "bw2k": bw_at(d, 2000.0)}
    m["g1"] = [v - F.JYT[(th, f)][0] for v, (th, f) in zip(m["jy"], JYT8)]
    m["g2"] = [v - F.JYT[(th, f)][1] for v, (th, f) in zip(m["jy"], JYT8)]
    grades = [F.grade(v, F.JYT[(th, f)]) for v, (th, f) in zip(m["jy"], JYT8)]   # 1 best .. 3, 0 = below grade 3
    m["grade"] = 0 if 0 in grades else max(grades)                                  # WORST of the 8 points
    return m


# ------------------------------------------------------------------------------------------------------------------
# compute [L3]
# ------------------------------------------------------------------------------------------------------------------
def xo_macs(K, order):
    """MAC per input sample: LR`order` split = LP + HP, each (order/4) biquads squared -> order/2 biquads per side;
    K=3 adds the (order/4)-biquad allpass compensation on the top band; 5 MAC per biquad; + 8K mixing MACs."""
    per_split = 2 * (order // 2) * 5
    ap = (order // 4) * 5 if K == 3 else 0
    return (K - 1) * per_split + ap + 8 * K


# ------------------------------------------------------------------------------------------------------------------
# real filters (critic R3f F1/F2/F4): LR4 biquads, drive premise, transient headroom vs the real FIR V1-128 taps
# ------------------------------------------------------------------------------------------------------------------
def lr4_sos(fc):
    lp = sig.butter(2, fc, "low", fs=FSAMP, output="sos")
    hp = sig.butter(2, fc, "high", fs=FSAMP, output="sos")
    return np.vstack([lp, lp]), np.vstack([hp, hp])                     # LR4 = Butterworth-2 squared


def bank3_sos(xo):
    """Real 3-band LR4 bank [LP1*LP2, HP1*LP2, AP1*HP2]; AP1 = LP1 + HP1 realised as one filter (common denominator).
    Also returns the on-axis all-pass AP1*AP2."""
    LP1, HP1 = lr4_sos(xo[0])
    LP2, HP2 = lr4_sos(xo[1])
    aps = []
    for LP, HP in ((LP1, HP1), (LP2, HP2)):
        bl, al = sig.sos2tf(LP)
        bh, ah = sig.sos2tf(HP)
        if not np.allclose(al, ah):
            raise SystemExit("LR4 LP/HP denominators differ")
        aps.append(sig.tf2sos(bl + bh, al))
    return [np.vstack([LP1, LP2]), np.vstack([HP1, LP2]), np.vstack([aps[0], HP2])], np.vstack(aps)


def real_bank_check(xo):
    """In-phase / sum-to-one on REAL biquads (sosfreqz), not on the closed form (which is an identity)."""
    f = np.linspace(1.0, 20000.0, 20000)
    bands, _ap = bank3_sos(xo)
    Hs = [sig.sosfreqz(s, worN=f, fs=FSAMP)[1] for s in bands]
    ph = max(float(np.max(np.abs(np.angle(Hs[k] / Hs[0])))) for k in (1, 2))
    ms = float(np.max(np.abs(sum(np.abs(h) for h in Hs) - 1)))
    cf = float(np.max(np.abs(np.stack([np.abs(h) for h in Hs], 1) - lr_mags(f, xo, 4))))
    return ph, ms, cf


def fir_taps(variant="V1", taps=127):
    h = np.zeros((8, taps))
    with open(os.path.join(HERE, "fir", "s7_fir_coeffs_127tap.csv"), newline="") as fp:
        for r in csv.DictReader(fp):
            if r["variant"] == variant and int(r["taps"]) == taps:
                h[int(r["channel"])] = [float(r[f"h{i}"]) for i in range(taps)]
    if np.abs(h).sum() == 0:
        raise SystemExit("FIR taps not found")
    return h


def fir_design(name, h):
    return CDesign(name, lambda f, h=h: np.stack([sig.freqz(h[c], worN=f, fs=FSAMP)[1] for c in range(8)], 1))


def headroom_report(d, xo, h_fir):
    """Drive premise and transient headroom of the XO design (real biquads) vs FIR V1-128 (real taps).
    Normalisation = steady-sine full drive (max over channels and frequency of |W_c(f)| = 1, as in the ideal tables).
    Per-channel output peak is compared with TODAY's same channel (D20, pure gain: peak = d20r_c x input peak)."""
    wk = d.meta["wk"]
    d20r = S.read_w8()[0] / S.read_w8()[0].max()
    fl = np.linspace(1.0, 24000.0, 48000)
    Wx = np.abs(lr_mags(fl, xo, 4) @ wk)
    amax_x = float(Wx.max())
    Hf = np.abs(np.stack([sig.freqz(h_fir[c], worN=fl, fs=FSAMP)[1] for c in range(8)], 1))
    amax_f = float(Hf.max())
    ex_all = 20 * np.log10(Wx.max(0) / amax_x / d20r)
    ex_hf = 20 * np.log10(Wx[fl >= 1600.0].max(0) / amax_x / d20r)
    back = max(0.0, float(ex_all.max()))
    log("  drive premise, steady sine (X3): per-channel peak gain vs D20 same channel, c0..c7 (c = 0-based channel =")
    log("  elements {c, 15-c}): all f " + " ".join(f"{v:+5.2f}" for v in ex_all) + " dB;  f >= 1.6 kHz "
        + " ".join(f"{v:+5.2f}" for v in ex_hf) + " dB")
    log(f"  -> keeping every channel <= today (sine) needs {back:.2f} dB extra back-off: on-axis "
        f"{onaxis_band(d, 1000, amax_x):+.2f} -> {onaxis_band(d, 1000, amax_x) - back:+.2f} dB vs D20")
    bands, ap = bank3_sos(xo)
    n = int(FSAMP)
    sigs = {}
    for f0 in (100, 1000, 3000):
        per = int(round(FSAMP / f0))
        sigs[f"square {f0} Hz"] = np.where((np.arange(2 * n) % per) < per // 2, 1.0, -1.0)
    rng = np.random.default_rng(11)
    X = np.fft.rfft(rng.normal(size=10 * n))
    fr = np.fft.rfftfreq(10 * n, 1 / FSAMP)
    X[0] = 0.0
    X[1:] /= np.sqrt(fr[1:])
    pn = np.fft.irfft(X, 10 * n)
    sigs["pink noise"] = pn / np.abs(pn).max()
    log("  transient: per-channel output PEAK vs today's same channel, full-scale input (peak 1), c0..c7, dB;")
    log("  squares start from silence (the onset is included -- it is the worst case; steady state is lower)")
    log(f"  {'signal':14s} | {'X3-LR4 (real biquads)':^56s} | {'FIR V1-128 (real taps)':^56s}")
    rows = []
    for name, x in sigs.items():
        b = [sig.sosfilt(s, x) for s in bands]
        yx = np.array([np.abs(sum(wk[k][c] * b[k] for k in range(3))).max() for c in range(8)]) / amax_x
        yf = np.array([np.abs(sig.lfilter(h_fir[c], 1.0, x)).max() for c in range(8)]) / amax_f
        ox, of = 20 * np.log10(yx / d20r), 20 * np.log10(yf / d20r)
        rows.append((name, ox, of))
        log(f"  {name:14s} | " + " ".join(f"{v:+6.2f}" for v in ox) + " | " + " ".join(f"{v:+6.2f}" for v in of))
    imp = np.zeros(n)
    imp[0] = 1.0
    bi = [sig.sosfilt(s, imp) for s in bands]
    l1x = np.array([np.abs(sum(wk[k][c] * bi[k] for k in range(3))).sum() for c in range(8)])
    l1f = np.abs(h_fir).sum(1)
    ox, of = 20 * np.log10(l1x / amax_x / d20r), 20 * np.log10(l1f / amax_f / d20r)
    rows.append(("L1 bound", ox, of))
    log(f"  {'L1 bound':14s} | " + " ".join(f"{v:+6.2f}" for v in ox) + " | " + " ".join(f"{v:+6.2f}" for v in of))
    lx = 20 * np.log10(1 / l1x.max() / F.d20_axis_level())
    lf = 20 * np.log10(1 / l1f.max() / F.d20_axis_level())
    log(f"  on-axis full drive vs D20, L1 convention (as s7_fir_robust_design l1_level): X3 {lx:+.2f} dB,"
        f" FIR V1-128 {lf:+.2f} dB (s7_fir_summary.csv: -6.76)")
    gd = np.zeros(3)                       # group delay adds over cascaded sections (one 8th-order polynomial is
    for sec in ap:                         # ill-conditioned this close to z = 1)
        gd += sig.group_delay((sec[:3], sec[3:]), w=[10.0, 1000.0, 4000.0], fs=FSAMP)[1]
    log(f"  X3 on-axis response = common all-pass AP{int(xo[0])}*AP{int(xo[1])} (magnitude flat, phase not linear):"
        f" group delay {gd[0] / FSAMP * 1e3:.3f} / {gd[1] / FSAMP * 1e3:.3f} / {gd[2] / FSAMP * 1e3:.3f} ms at 10 Hz / 1 kHz / 4 kHz;"
        f" FIR V1-128: constant 63 samples = {63 / FSAMP * 1e3:.3f} ms")
    return rows, back, lx, lf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", type=int, default=1000)
    args = ap.parse_args()
    t0 = time.time()
    anc = S.assert_anchors(verbose=False)
    log(f"S7 side-30: low-order IIR shading / DDC-literal / Keele delay-CBT [L2; yields L2 on L4; MAC L3]  anchors "
        f"{', '.join(f'{k}={v:.6g}' for k, v in anc.items())}")

    # ---- LR bank check on REAL biquads (critic R3f F2: the closed-form sum-to-1 is an identity and cannot fail) ------
    ph, ms, cf = real_bank_check((700.0, 1600.0))
    if ph > 1e-6 or ms > 1e-9 or cf > 1e-9:
        raise SystemExit(f"real LR4 bank check FAIL: phase {ph:.2e} rad, |sum|-1 {ms:.2e}, closed-form diff {cf:.2e}")
    log(f"LR4 3-band bank 700/1600 Hz on real biquads (scipy butter/sosfreqz, 1 Hz-20 kHz): max inter-band phase"
        f" {ph:.1e} rad, max ||low|+|mid|+|high|-1| {ms:.1e}, max |biquad - closed-form magnitude| {cf:.1e}  -> PASS")

    # ---- reference designs -------------------------------------------------------------------------------------------
    rows = {lab: q for lab, q, _m, _c in G.build()[1]}
    refs = [table_design("D20q", G.frozen_d20() / 32768.0), table_design("D35q", rows["D35"] / 32768.0),
            table_design("RS-Aq", rows["RS-A"] / 32768.0), table_design("RS-Bq", rows["RS-B"] / 32768.0)]

    # ---- crossover grid ----------------------------------------------------------------------------------------------
    log("\n=== (1) shared in-phase LR bank + per-channel band gains; band 1 = frozen D20; grid (ideal [L2])")
    cands, grid_rows = [], []
    for order in (4, 8):
        for xo in ((600.0,), (700.0,), (800.0,), (700.0, 1400.0), (700.0, 1600.0), (700.0, 2000.0), (800.0, 1600.0)):
            for eta, thm in ((0.1, 35.0), (1.0, 30.0), (3.0, 30.0)):
                d = xo_designobj(xo, order, eta, thm)
                m = ideal(d)
                nonneg = bool((d.meta["wk"] >= 0).all())
                ok = nonneg and m["grade"] == 1 and min(m["g1"]) >= 0.0      # all 8 points grade 1 (two equivalent tests)
                d.meta["ideal"] = m
                grid_rows.append(d)
                if ok:
                    cands.append(d)
                log(f"  {d.label():26s} nonneg {str(nonneg):5s} JY/T worst grade {m['grade']} (g1 margin {min(m['g1']):+5.2f})"
                    f"  R90 min7 {min(m['r90']):5.1f}  BW1k {m['bw1k']:5.1f}  on-axis {np.mean(m['ax']):+5.2f} dB"
                    f"  500/30 {m['jy'][0]:5.2f}  1k/30 {m['jy'][2]:5.2f}  {'CANDIDATE' if ok else ''}")
    log(f"  -> {len(cands)} candidates (non-negative band gains and all 8 JY/T points grade 1)")

    # ---- DDC-literal and CBT -------------------------------------------------------------------------------------------
    log("\n=== (2) DDC-literal constant beamwidth (ideal filters) and Keele 2002 delay-derived CBT (ideal [L2])")
    others = [ddc_design(30.0), ddc_design(40.0), cbt_design(20.0, delays=False)]
    for arc in (20.0, 30.0, 45.0, 60.0):
        others.append(cbt_design(arc))
        others.append(cbt_design(arc, qsamp=FSAMP))
    for d in others:
        m = ideal(d)
        d.meta["ideal"] = m
        extra = ""
        if "tau_us" in d.meta:
            extra = f"  max delay {d.meta['tau_us'].max():6.1f} us ({d.meta['tau_us'].max() * 1e-6 * FSAMP:5.2f} samples)"
        log(f"  {d.label():16s} R90 7 bands [{' '.join(f'{v:4.1f}' for v in m['r90'])}] min {min(m['r90']):4.1f}"
            f"  BW1k {m['bw1k']:5.1f}  on-axis {min(m['ax']):+5.1f}..{max(m['ax']):+5.1f} dB  JY/T worst grade {m['grade']}"
            f"  500/30 {m['jy'][0]:5.2f}  1k/30 {m['jy'][2]:5.2f}{extra}")
    log("  Legendre shading U (edge->centre) = " + np.array2string(others[2].meta["U"], precision=3))

    for d in refs:
        d.meta["ideal"] = ideal(d)

    # ---- scope of the comparison (critic R3f F6), 5 kHz-in-objective variant, free-low variants (F8) -------------------
    h_v1 = fir_taps("V1", 127)
    fir_v1 = fir_design("FIR V1-128 (taps)", h_v1)
    rep = [d for d in cands if d.label() == "X3-LR4-700/1600-e0.1m35"][0]
    x5k = xo_designobj((700.0, 1600.0), 4, 0.1, 35.0, fgrid=np.concatenate([F7, F.band_freqs(5000.0)]), suffix="+5k")
    x5k.meta["ideal"] = ideal(x5k)
    log("\n=== SCOPE (critic R3f F6): outside the 7 DEC bands [L2 ideal]  R90 @5 kHz band (observation band) | BW(-6)@500 Hz"
        " | R90 min7 | JY/T worst grade")
    for d in (refs[0], rep, x5k, fir_v1):
        m = d.meta.get("ideal") or ideal(d)
        log(f"  {d.label():30s} {band_att(d, 5000, 90.0):5.1f} dB | {bw_at(d, 500.0):5.1f} deg | {min(m['r90']):5.1f} | {m['grade']}")
    log("  -> the X3 tie with FIR is a 7-band (1k-4k) statement; X3's 5 kHz band sits at D20 level unless 5 kHz is put")
    log("     into the design objective (+5k variant, which is also Monte-Carlo'd below).")
    log("\n=== EXPLORATORY free-low-band variants (critic R3f F8): all 3 bands free, + mu x '500 Hz outside +/-30 deg'")
    for mu in (0.1, 1.0, 10.0):
        dfl = xo_design_freelow((700.0, 1600.0), 4, 0.1, 35.0, mu)
        amax = float(np.abs(dfl.A(FDENSE)).max())
        log(f"  mu {mu:<4g}: on-axis full drive vs D20 {onaxis_band(dfl, 1000, amax):+6.2f} dB, 500/30 {single_att(dfl, 500, 30):5.2f} dB,"
            f" any negative band gain: {bool((dfl.meta['wk'] < 0).any())}")
    log("  (the free low band goes superdirective: large sign-alternating weights, big on-axis loss -> band 1 fixed to D20)")

    # ---- Monte Carlo ---------------------------------------------------------------------------------------------------
    M = args.mc
    anchors = [F.Design("Dolph-20", "table", table=F.d20_norm()), F.Design("Dolph-35", "table", table=F.d35_norm())]
    mc_others = [d for d in others if d.label() in ("DDC-BW30", "Legendre-only", "CBT-arc20", "CBT-arc20-int", "CBT-arc30")]
    designs = anchors + refs + cands + [x5k] + mc_others
    ref = {}
    if M == 1000:
        with open(FIR_MC_CSV, newline="") as fp:
            for r in csv.DictReader(fp):
                ref[(r["design"], r["error_model"], r["strategy"], int(r["band_fc_hz"]))] = r
    log(f"\n=== MONTE CARLO [L2 on L4 spread]: {M} arrays/cell, same seeds/draws as s7_fir_mc.csv; JOINT7 = all 7 bands >= 30 dB")
    J7, MED, mrows, nanchor = {}, {}, [], 0
    for mi, (mname, model, sm) in enumerate(F.MODELS):
        for si, (st, slab) in enumerate(F.STRATS):
            seed = F.SEED + 1000 * (mi + 1) + si
            ts = time.time()
            res, side = F.mc_cell(designs, model, sm, st, M, seed)
            for d in designs:
                r7 = res[d.label()]
                j3 = float(np.mean(np.all(r7[:, F.I3] >= 30.0, axis=1)) * 100)
                j7 = float(np.mean(np.all(r7 >= 30.0, axis=1)) * 100)
                J7[(d.label(), mname, st)] = j7
                MED[(d.label(), mname, st)] = float(np.median(r7.min(1)))
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
            log(f"  [{mname[:6]}|{st:8s}] seed {seed} done ({time.time() - ts:5.1f}s)")
    log(f"  MC ANCHOR: {nanchor} anchor rows reproduce s7_fir_mc.csv exactly -> PASS" if ref else "  MC ANCHOR: skipped (--mc != 1000)")

    # ---- FIR rows from the CSV -----------------------------------------------------------------------------------------
    fir = {}
    for (dsg, em, st, fc), r in ref.items():
        if dsg in ("V1-128t", "V2-128t") and fc == 1000:
            fir[(dsg, em, st)] = float(r["joint7_yield_pct_DEC1_1k-4k"])

    # ---- summary -------------------------------------------------------------------------------------------------------
    fams = {}
    for d in cands:
        fam = d.label().split("-")[0] + "-" + d.label().split("-")[1]
        fams.setdefault(fam, []).append(d)
    reps = []
    log("\n=== XO candidates: joint7 % (U-flat | G) as-built / +pair+trim, per family")
    for fam, ds in sorted(fams.items()):
        ab = [J7[(d.label(), "U-flat", "asbuilt")] for d in ds]
        best = ds[int(np.argmax(ab))]
        reps.append(best)
        log(f"  family {fam}: {len(ds)} candidates, U-flat as-built joint7 {min(ab):.1f}..{max(ab):.1f}%  -> representative {best.label()}")
        for d in ds:
            log(f"     {d.label():26s} U asb {J7[(d.label(), 'U-flat', 'asbuilt')]:5.1f}  U pair {J7[(d.label(), 'U-flat', 'pair')]:5.1f}"
                f"  G asb {J7[(d.label(), 'G-p0.5-l1oct+jig0.25', 'asbuilt')]:5.1f}  G pair {J7[(d.label(), 'G-p0.5-l1oct+jig0.25', 'pair')]:5.1f}")

    log("\n=== SUMMARY table (ideal [L2] | joint7 yield % [L2 on L4], U-flat / G)")
    hdr = (f"  {'design':26s} {'R90min7':>7s} {'sec60':>6s} {'BW1k':>5s} {'1k/30':>6s} {'500/30':>6s} {'JYTg':>4s}"
           f" {'axis':>6s} | {'as-built':>11s} {'+trim':>11s} {'+pair+trim':>11s} {'+cplx':>11s} {'+pair+cplx':>11s}")
    log(hdr)
    summ = []
    for d in refs + reps + [x5k] + mc_others:
        m = d.meta["ideal"]
        cells = [f"{J7[(d.label(), 'U-flat', s)]:5.1f}/{J7[(d.label(), 'G-p0.5-l1oct+jig0.25', s)]:5.1f}"
                 for s in ("asbuilt", "amp", "pair", "cplx", "paircplx")]
        log(f"  {d.label():26s} {min(m['r90']):7.1f} {min(m['sec']):6.1f} {m['bw1k']:5.1f} {m['jy'][2]:6.2f} {m['jy'][0]:6.2f}"
            f" {m['grade']:4d} {np.mean(m['ax']):+6.2f} | " + " ".join(f"{c:>11s}" for c in cells))
        summ.append(d)
    for dsg in ("V1-128t", "V2-128t"):
        if (dsg, "U-flat", "asbuilt") in fir:
            cells = [f"{fir[(dsg, 'U-flat', s)]:5.1f}/{fir[(dsg, 'G-p0.5-l1oct+jig0.25', s)]:5.1f}"
                     for s in ("asbuilt", "amp", "pair", "cplx", "paircplx")]
            log(f"  {dsg + ' (s7_fir_mc.csv)':26s} {'':>7s} {'':>6s} {'':>5s} {'':>6s} {'':>6s} {'':>4s} {'':>6s} | "
                + " ".join(f"{c:>11s}" for c in cells))

    log("\n=== COMPUTE [L3 MAC; cycles = MAC x 30-50 cyc/MAC board factor, recursive-IIR factor unverified -> L4]")
    budget = 1.333e6
    for K, order in ((2, 4), (3, 4), (2, 8), (3, 8)):
        mac = xo_macs(K, order)
        log(f"  X{K}-LR{order}: {mac:3d} MAC/sample -> {mac * 64:5d} MAC/frame (64 samples) -> {mac * 64 * 30 / 1e3:6.0f}-"
            f"{mac * 64 * 50 / 1e3:6.0f} k cyc/frame = {mac * 64 * 30 / budget:.2f}-{mac * 64 * 50 / budget:.2f} of the"
            f" 1.333 M cyc frame (CCLK 1 GHz assumed)")
    log("  reference (s7_fir_compute.csv): FIR-128 x 8 = 65536 MAC/frame direct / 32768 folded -> 0.98-3.28 M cyc/frame;"
        " frozen tree (C-code count) 169344 MAC/frame")

    # ---- transient headroom and drive premise (critic R3f F1/F4) -----------------------------------------------------
    log("\n=== HEADROOM / DRIVE PREMISE (critic R3f F1/F4) [L2 time-domain simulation; real biquads and real FIR taps]")
    headroom_report(rep, (700.0, 1600.0), h_v1)

    # ---- CSVs ------------------------------------------------------------------------------------------------------------
    irows = []
    for d in refs + grid_rows + others:
        m = d.meta["ideal"]
        for b, fc in enumerate(B7):
            irows += [[d.label(), "R90_band", fc, f"{m['r90'][b]:.3f}"], [d.label(), "sector60_90_worst_band", fc, f"{m['sec'][b]:.3f}"],
                      [d.label(), "err_floor_band", fc, f"{m['flo'][b]:.3f}"], [d.label(), "onaxis_fulldrive_vs_D20_band", fc, f"{m['ax'][b]:.3f}"]]
        for (th, f), v, ib in zip(JYT8, m["jy"], m["jyib"]):
            irows += [[d.label(), f"JYT_{f}_{th}_single", f, f"{v:.3f}"], [d.label(), f"JYT_{f}_{th}_inband_min", f, f"{ib:.3f}"]]
        irows += [[d.label(), "BW_1k_deg", 1000, f"{m['bw1k']:.3f}"], [d.label(), "BW_2k_deg", 2000, f"{m['bw2k']:.3f}"],
                  [d.label(), "JYT_worst_grade", 0, m["grade"]]]
    wrows = []
    for d in grid_rows:
        for k, w in enumerate(d.meta["wk"]):
            wrows.append([d.label(), d.meta["order"], "/".join(str(int(v)) for v in d.meta["xo"]), k + 1]
                         + [f"{v:.12e}" for v in w])
    for d in others:
        if "tau_us" in d.meta:
            wrows.append([d.label(), "cbt", d.meta["arc"], "U"] + [f"{v:.12e}" for v in d.meta["U"]])
            wrows.append([d.label(), "cbt", d.meta["arc"], "tau_us"] + [f"{v:.12e}" for v in d.meta["tau_us"]])
    for name, hdr_, rr in (("s7_alt_algos_ideal.csv", ["design", "metric", "freq_hz", "value"], irows),
                           ("s7_alt_algos_mc.csv", ["design", "error_model", "strategy", "band_fc_hz", "median_db", "p10_db",
                                                    "yield_ge30_pct", "joint3_yield_pct_1k2k4k", "joint7_yield_pct_DEC1_1k-4k",
                                                    "meanpower_att_per_side_db", "seed", "arrays"], mrows),
                           ("s7_alt_algos_params.csv", ["design", "order_or_kind", "xo_hz_or_arc_deg", "band_or_param",
                                                        "c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7"], wrows)):
        with open(os.path.join(HERE, name), "w", newline="") as fp:
            wr = csv.writer(fp, lineterminator="\n")
            wr.writerow(hdr_)
            wr.writerows(rr)
    log(f"\nruntime {time.time() - t0:.0f}s ; outputs s7_alt_algos.log / _ideal.csv / _mc.csv / _params.csv")
    with open(os.path.join(HERE, "s7_alt_algos.log"), "w") as fp:
        fp.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
