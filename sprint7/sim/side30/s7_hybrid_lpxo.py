#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s7_hybrid_lpxo.py -- S7-SIDE30 desktop evaluation of the HYBRID "shared LINEAR-PHASE crossover + per-channel band
gains" (CTO 2026-09-29 「好」 to the PM proposal to evaluate it on the desktop while S-B / S-FIRB are pending).

IDEA: keep X3's cheap structure (the crossover runs ONCE on the mono input; each channel = 8 x K band-gain mix) but
realise the crossover with linear-phase FIRs instead of Linkwitz-Riley IIRs, so the common all-pass phase of X3 (the
cause of its +7.4 dB square-wave overshoot, critic R3f F1) disappears. Band k taps are differences of symmetric
low-passes that share ONE delay D (shorter low-passes are zero-padded symmetrically), so
    sum_k band_k = delta[n - D]   (exact perfect reconstruction, any tap lengths)
and every band -- hence every channel filter h_c = sum_k w_k[c] band_k -- is linear phase with the same delay D.
Each low-pass is a least-squares FIR (scipy firls) whose zero-phase amplitude replicates the LR4 LOW-PASS magnitude of
X3 at the same crossover. NOTE (critic R3g F3): the BANDS are not replicas -- X3 forms [A1*A2, (1-A1)*A2, 1-A2], this bank
forms [A1, A2-A1, 1-A2]; low and mid differ by A1*(1-A2) (<= ~0.03 near 1 kHz). After the band gains are re-solved the
per-channel amplitudes nearly coincide with X3's, which is why the yields tie.

VARIANTS (the four below were fixed BEFORE any result was seen; no tuning): crossovers 700 / 1600 Hz (K = 3, as X3) or 700 / 1600 / 4470 Hz
(K = 4: an extra top band for the 5 kHz observation band, critic R3f F6); tap sets 'a' = 255 / 127 / 63 (accurate) and
'b' = 127 / 63 / 31 (lean). Band 1 fixed = frozen D20; bands 2..K designed jointly by the same KKT robust criterion as
X3-LR4-700/1600-e0.1m35 (eta 0.1, mid 35-60 deg), objective over the 7 DEC bands (K = 3) or 7 bands + the 5 kHz band
(K = 4).

POST-HOC VARIANTS (added after the first run, clearly separated in the log): LPX4-a-cap / LPX4-b-cap -- the first run showed
LPX4 about 2.3 dB below LPX3 on axis; diagnosis: the top band (>= 4.47 kHz) gets a steep taper (max/sum 0.26 vs D20
0.155) and the full-drive normalisation is set by it (max on the high-frequency plateau, ~10 kHz to Nyquist, c7). The cap forces the top band's largest weight
<= band 2's, via an extra loading of the top band found by bisection.

L-GRADES: ideal metrics and time-domain simulations [L2]; yields [L2 on L4 spread] (same draws as s7_fir_mc.csv, anchor
checked); MAC counts [L3]; core cycles [L4 envelope] (MAC x the project's 30-50 cyc/MAC board factor). No L1.

Usage: /usr/bin/python3 s7_hybrid_lpxo.py [--mc 1000]      (runtime ~3 min)
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
sys.path.insert(0, HERE)
import s7_alt_algos as A  # noqa: E402  (module import; its main() does not run)

F, S, G = A.F, A.S, A.G
FSAMP = A.FSAMP
B7 = A.B7
F7 = A.F7
F5K = F.band_freqs(5000.0)
JYT8 = A.JYT8
FIR_MC_CSV = os.path.join(HERE, "fir", "s7_fir_mc.csv")
LOG = []


def log(s=""):
    print(s)
    LOG.append(s)


# ------------------------------------------------------------------------------------------------------------------
# linear-phase crossover bank
# ------------------------------------------------------------------------------------------------------------------
def lr4_lp_target(f, fc):
    """Zero-phase amplitude to replicate = the LR4 low-pass magnitude of X3 (bilinear-prewarped, as A.lr_mags)."""
    t = (np.tan(np.pi * np.minimum(f, FSAMP / 2 - 1) / FSAMP) / np.tan(np.pi * fc / FSAMP)) ** 4
    return 1.0 / (1.0 + t)


def lp_taps(fc, n):
    edges = np.unique(np.concatenate([np.linspace(0, 150, 4), np.geomspace(160, 23000, 240), [FSAMP / 2]]))
    return sig.firls(n, np.repeat(edges, 2)[1:-1], np.repeat(lr4_lp_target(edges, fc), 2)[1:-1], fs=FSAMP)


class LPBank:
    def __init__(self, xo, lens):
        if len(xo) != len(lens) or any(n % 2 == 0 for n in lens):
            raise SystemExit("odd tap lengths, one per crossover")
        self.xo, self.lens = tuple(xo), tuple(lens)
        self.N = max(lens)
        self.D = (self.N - 1) // 2
        self.lp = [lp_taps(fc, n) for fc, n in zip(xo, lens)]              # native lengths (what gets computed)
        lps = [np.pad(h, ((self.N - n) // 2, (self.N - n) // 2)) for h, n in zip(self.lp, lens)]
        delta = np.zeros(self.N)
        delta[self.D] = 1.0
        self.bands = [lps[0]] + [lps[i] - lps[i - 1] for i in range(1, len(lps))] + [delta - lps[-1]]

    def mags(self, f):
        f = np.atleast_1d(np.asarray(f, float))
        ph = np.exp(1j * 2 * np.pi * f * self.D / FSAMP)
        return np.stack([(sig.freqz(b, worN=f, fs=FSAMP)[1] * ph).real for b in self.bands], 1)

    def check(self):
        """Real-filter checks on the taps. NOTE (critic R3g F4): 'pr' (sum of bands == delta) is a CONSTRUCTION
        IDENTITY (the bands telescope), reported for completeness only -- it cannot fail. The checks that CAN fail are:
        symmetry (exact, rtol 0), zero-phase imaginary part, the LR4 fit threshold, and (in main) the on-axis identity
        sum_c 2 h_c == delta built from the designed gains, plus the KKT constraint/optimality checks."""
        pr = float(np.abs(sum(self.bands) - np.eye(1, self.N, self.D)[0]).max())
        f = np.linspace(1.0, 20000.0, 20000)
        ph = np.exp(1j * 2 * np.pi * f * self.D / FSAMP)
        im = max(float(np.abs((sig.freqz(b, worN=f, fs=FSAMP)[1] * ph).imag).max()) for b in self.bands)
        sym = all(np.allclose(b, b[::-1], rtol=0.0, atol=1e-15) for b in self.bands)
        fit = [float(np.abs((sig.freqz(h, worN=f, fs=FSAMP)[1] * np.exp(1j * 2 * np.pi * f * ((n - 1) // 2) / FSAMP)).real
                            - lr4_lp_target(f, fc)).max()) for h, n, fc in zip(self.lp, self.lens, self.xo)]
        return pr, im, sym, fit

    def macs_per_sample(self):
        return sum((n + 1) // 2 for n in self.lens) + 8 * (len(self.xo) + 1)   # folded symmetric FIRs + 8K mixing

    def taps8(self, wk):
        return np.array([sum(wk[k][c] * self.bands[k] for k in range(len(self.bands))) for c in range(8)])


def design_bands(mags_fn, K, fgrid, eta=0.1, thm=35.0, extra_load=None):
    """As A.xo_design, with an arbitrary band-amplitude function: band 1 = D20 (sum 2w = 1), bands 2..K free, KKT.
    extra_load = {band index k (1-based): rho} adds rho * I to that band's block (post-hoc cap on its taper)."""
    nf = K - 1
    d20n = S.read_w8()[0] / (2 * S.read_w8()[0].sum())
    M = mags_fn(fgrid)
    H = np.zeros((8 * nf, 8 * nf))
    g = np.zeros(8 * nf)
    for i, f in enumerate(fgrid):
        key = (round(float(f), 6), eta, thm)
        if key not in A._QC:
            A._QC[key] = A.sec_q(f, eta, thm)
        Q = A._QC[key]
        mf, m1 = M[i, 1:], M[i, 0]
        H += np.kron(np.outer(mf, mf), Q) / len(fgrid)
        g += np.kron(mf, Q @ (m1 * d20n)) / len(fgrid)
    for kb, rho in (extra_load or {}).items():
        H[8 * (kb - 2):8 * (kb - 1), 8 * (kb - 2):8 * (kb - 1)] += rho * np.eye(8)
    C = np.kron(np.eye(nf), 2 * np.ones((1, 8)))
    x = np.linalg.solve(np.block([[H, C.T], [C, np.zeros((nf, nf))]]), np.concatenate([-g, np.ones(nf)]))[:8 * nf]
    if np.abs(C @ x - 1).max() > 1e-12:
        raise SystemExit("design_bands: constraint violated")
    J = lambda xx: xx @ H @ xx + 2 * g @ xx  # noqa: E731
    rng = np.random.default_rng(7)
    for _ in range(20):
        p = rng.normal(size=8 * nf)
        p -= C.T @ np.linalg.solve(C @ C.T, C @ p)
        if J(x + 1e-3 * p) < J(x) - 1e-15:
            raise SystemExit("design_bands: KKT solution not optimal")
    return np.vstack([d20n, x.reshape(nf, 8)])


def lp_design(name, xo, lens, fgrid, cap_top=False):
    """cap_top (POST-HOC, added after the LPX4 on-axis drop was diagnosed): the top band's largest weight must not
    exceed band 2's (band 2 sets the full-drive normalisation of the 3-band design); enforced by bisection on an extra
    loading rho of the top band only. Everything else identical."""
    bank = LPBank(xo, lens)
    K = len(xo) + 1
    wk = design_bands(bank.mags, K, fgrid)
    rho = 0.0
    if cap_top and wk[-1].max() > wk[1].max():
        lo, hi = 0.0, 1e-6
        while design_bands(bank.mags, K, fgrid, extra_load={K: hi})[-1].max() > \
                design_bands(bank.mags, K, fgrid, extra_load={K: hi})[1].max():
            hi *= 4
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            w = design_bands(bank.mags, K, fgrid, extra_load={K: mid})
            lo, hi = (mid, hi) if w[-1].max() > w[1].max() else (lo, mid)
        rho = hi
        wk = design_bands(bank.mags, K, fgrid, extra_load={K: rho})
    d = A.CDesign(name, lambda f, bank=bank, wk=wk: (bank.mags(f) @ wk).astype(complex),
                  {"wk": wk, "bank": bank, "taps8": bank.taps8(wk), "rho_top": rho})
    return d


# ------------------------------------------------------------------------------------------------------------------
# headroom (time domain) for any per-channel output generator
# ------------------------------------------------------------------------------------------------------------------
def test_signals():
    n = int(FSAMP)
    out = {}
    for f0 in (100, 1000, 3000):
        per = int(round(FSAMP / f0))
        out[f"square {f0} Hz"] = np.where((np.arange(2 * n) % per) < per // 2, 1.0, -1.0)   # from silence (onset incl.)
    rng = np.random.default_rng(11)
    X = np.fft.rfft(rng.normal(size=10 * n))
    fr = np.fft.rfftfreq(10 * n, 1 / FSAMP)
    X[0] = 0.0
    X[1:] /= np.sqrt(fr[1:])
    pn = np.fft.irfft(X, 10 * n)
    out["pink noise"] = pn / np.abs(pn).max()
    return out


def headroom(name, run8, imp8, amax, d20r):
    """run8(x) -> (8, len x) channel outputs; imp8 = (8, L) impulse responses (truncated). Normalisation: steady-sine
    full drive (max over channels and frequency of |W_c(f)| = amax -> 1). Returns rows of per-channel dB."""
    rows = {}
    for sname, x in test_signals().items():
        y = run8(x)
        rows[sname] = 20 * np.log10(np.abs(y).max(1) / amax / d20r)
    l1 = np.abs(imp8).sum(1)
    rows["L1 bound"] = 20 * np.log10(l1 / amax / d20r)
    rows["L1 abs vs FS"] = 20 * np.log10(l1 / amax)
    lvl = 20 * np.log10(1 / l1.max() / F.d20_axis_level())           # on-axis gain 1 (sum_c 2 h_c = allpass / delta)
    return rows, lvl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", type=int, default=1000)
    args = ap.parse_args()
    t0 = time.time()
    anc = S.assert_anchors(verbose=False)
    log(f"S7 side-30 HYBRID: shared LINEAR-PHASE crossover + 8xK band gains [L2; yields L2 on L4; MAC L3; cycles L4]"
        f"  anchors {', '.join(f'{k}={v:.6g}' for k, v in anc.items())}")
    F75 = np.concatenate([F7, F5K])
    specs = [("LPX3-a", (700.0, 1600.0), (255, 127), F7), ("LPX3-b", (700.0, 1600.0), (127, 63), F7),
             ("LPX4-a", (700.0, 1600.0, 4470.0), (255, 127, 63), F75),
             ("LPX4-b", (700.0, 1600.0, 4470.0), (127, 63, 31), F75)]
    lps = []
    log("\n=== linear-phase bank checks on the REAL taps. PR (sum of bands == delta[n-D]) is a CONSTRUCTION IDENTITY,"
        " shown only for completeness (it cannot fail). Gated checks (any failure -> SystemExit): exact symmetry;"
        " zero-phase imag <= 1e-9; each low-pass within 0.02 of its LR4 target (catches a failed firls design);"
        " on-axis sum_c 2 h_c == delta[n-D] from the DESIGNED per-channel taps (<= 1e-12); KKT checks in design_bands")
    FIT_MAX = 0.02
    for name, xo, lens, fg in specs:
        d = lp_design(name, xo, lens, fg)
        bank = d.meta["bank"]
        pr, im, sym, fit = bank.check()
        ax = float(np.abs(2 * d.meta["taps8"].sum(0) - np.eye(1, bank.N, bank.D)[0]).max())
        if im > 1e-9 or not sym or max(fit) > FIT_MAX or ax > 1e-12:
            raise SystemExit(f"{name}: bank check FAIL (imag {im:.1e}, sym {sym}, fit {fit}, on-axis {ax:.1e})")
        log(f"  {name}: xo {xo} taps {lens} delay D = {bank.D} samples ({bank.D / FSAMP * 1e3:.2f} ms) | [identity] PR err"
            f" {pr:.1e} | zero-phase imag {im:.1e} | symmetric {sym} | max |A - LR4| per split "
            + " / ".join(f"{v:.4f}" for v in fit) + f" | on-axis |sum 2h_c - delta| {ax:.1e}  -> PASS")
        lps.append(d)
    # ---- POST-HOC (documented as such): diagnosis of the LPX4 on-axis drop and the capped top band ------------------------
    log("\n=== POST-HOC (added after the first run showed LPX4 on-axis ~2.3 dB below LPX3): diagnosis and a capped variant")
    fz = np.geomspace(20, 24000, 4000)
    for d in lps:
        wk = d.meta["wk"]
        W = np.abs(d.meta["bank"].mags(fz) @ wk)
        i, c = np.unravel_index(np.argmax(W), W.shape)
        log(f"  {d.label()}: band max/sum " + " ".join(f"{w.max() / w.sum():.4f}" for w in wk)
            + f" (D20 {1 / 6.44293:.4f}); global max |W_c(f)| {W.max():.4f} at c{c}, {fz[i]:.0f} Hz")
    for name, xo, lens, fg in specs[2:]:
        d = lp_design(name + "-cap", xo, lens, fg, cap_top=True)
        pr, im, sym, fit = d.meta["bank"].check()
        ax = float(np.abs(2 * d.meta["taps8"].sum(0) - np.eye(1, d.meta["bank"].N, d.meta["bank"].D)[0]).max())
        if im > 1e-9 or not sym or max(fit) > FIT_MAX or ax > 1e-12:
            raise SystemExit(f"{d.label()}: bank check FAIL")
        wk = d.meta["wk"]
        log(f"  {d.label()}: top-band extra loading rho = {d.meta['rho_top']:.3e}; band max/sum "
            + " ".join(f"{w.max() / w.sum():.4f}" for w in wk) + f"; top max {wk[-1].max():.5f} <= band-2 max {wk[1].max():.5f}")
        lps.append(d)
    x3 = A.xo_designobj((700.0, 1600.0), 4, 0.1, 35.0)
    rows = {lab: q for lab, q, _m, _c in G.build()[1]}
    d35q = A.table_design("D35q", rows["D35"] / 32768.0)
    d20q = A.table_design("D20q", G.frozen_d20() / 32768.0)
    h_v1 = A.fir_taps("V1", 127)
    fir_v1 = A.fir_design("FIR V1-128 (taps)", h_v1)

    # ---- ideal ------------------------------------------------------------------------------------------------------
    log("\n=== IDEAL [L2] (JY/T single frequency; [in-band minimum]); R90 = 1/3-oct band power avg at +-90 deg"
        "   (*-cap = POST-HOC variants)")
    irows = []
    allref = [d20q, d35q, x3] + lps + [fir_v1]
    for d in allref:
        m = A.ideal(d)
        d.meta["ideal"] = m
        r5 = A.band_att(d, 5000, 90.0)
        b5 = A.bw_at(d, 500.0)
        log(f"  {d.label():26s} R90 min7 {min(m['r90']):5.1f} [{' '.join(f'{v:4.1f}' for v in m['r90'])}] | 5k {r5:5.1f}"
            f" | BW1k {m['bw1k']:5.1f} BW@500 {b5:5.1f} | 1k/30 {m['jy'][2]:6.2f} [{m['jyib'][2]:6.2f}]"
            f" 500/30 {m['jy'][0]:5.2f} [{m['jyib'][0]:5.2f}] | JY/T worst grade {m['grade']} (g1 margin {min(m['g1']):+.2f})"
            f" | on-axis {np.mean(m['ax']):+.2f} dB")
        for b, fc in enumerate(B7):
            irows.append([d.label(), "R90_band", fc, f"{m['r90'][b]:.3f}"])
        irows += [[d.label(), "R90_band", 5000, f"{r5:.3f}"], [d.label(), "BW_500_deg", 500, f"{b5:.3f}"],
                  [d.label(), "BW_1k_deg", 1000, f"{m['bw1k']:.3f}"], [d.label(), "JYT_worst_grade", 0, m["grade"]],
                  [d.label(), "onaxis_fulldrive_vs_D20_dB", 0, f"{np.mean(m['ax']):.3f}"]]
        for (th, f), v, ib in zip(JYT8, m["jy"], m["jyib"]):
            irows += [[d.label(), f"JYT_{f}_{th}_single", f, f"{v:.3f}"], [d.label(), f"JYT_{f}_{th}_inband_min", f, f"{ib:.3f}"]]

    # ---- Monte Carlo --------------------------------------------------------------------------------------------------
    M = args.mc
    anchors = [F.Design("Dolph-20", "table", table=F.d20_norm()), F.Design("Dolph-35", "table", table=F.d35_norm())]
    designs = anchors + [x3] + lps
    ref = {}
    if M == 1000:
        with open(FIR_MC_CSV, newline="") as fp:
            for r in csv.DictReader(fp):
                ref[(r["design"], r["error_model"], r["strategy"], int(r["band_fc_hz"]))] = r
    log(f"\n=== MONTE CARLO [L2 on L4 spread]: {M} arrays/cell, same seeds/draws as s7_fir_mc.csv; JOINT7 = all 7 bands >= 30 dB"
        "   (*-cap = POST-HOC variants)")
    J7, mrows, nanchor = {}, [], 0
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
                mp7 = [-10 * np.log10(side[d.label()][:, b, :].mean()) for b in range(len(B7))]
                for b, fc in enumerate(B7):
                    row = [d.label(), mname, st, fc, f"{np.median(r7[:, b]):.2f}", f"{np.percentile(r7[:, b], 10):.2f}",
                           f"{np.mean(r7[:, b] >= 30)*100:.1f}", f"{j3:.1f}", f"{j7:.1f}", f"{mp7[b]:.2f}", seed, M]
                    mrows.append(row)
                    if d.label() in ("Dolph-20", "Dolph-35") and ref:
                        rr = ref[(d.label(), mname, st, fc)]
                        want = [rr["median_db"], rr["p10_db"], rr["yield_ge30_pct"], rr["joint3_yield_pct_1k2k4k"],
                                rr["joint7_yield_pct_DEC1_1k-4k"], rr["meanpower_att_per_side_db"], rr["seed"]]
                        if [str(v) for v in row[4:11]] != want:
                            raise SystemExit(f"MC ANCHOR FAIL {d.label()} {mname} {st} {fc}")
                        nanchor += 1
            log(f"  [{mname[:6]}|{st:8s}] seed {seed} done ({time.time() - ts:5.1f}s)")
    log(f"  MC ANCHOR: {nanchor} anchor rows reproduce s7_fir_mc.csv exactly -> PASS" if ref else "  MC ANCHOR: skipped")
    fir = {}
    for (dsg, em, st, fc), r in ref.items():
        if dsg == "V1-128t" and fc == 1000:
            fir[(em, st)] = float(r["joint7_yield_pct_DEC1_1k-4k"])
    log("\n=== SUMMARY joint7 % (U-flat / G)      as-built       +trim  +pair+trim       +cplx  +pair+cplx   (cplx = ideal"
        " per-channel complex calibration, i.e. an extra per-channel calibration filter)")
    for d in [x3] + lps:
        log(f"  {d.label():26s} " + " ".join(f"{J7[(d.label(), 'U-flat', s)]:5.1f}/{J7[(d.label(), 'G-p0.5-l1oct+jig0.25', s)]:5.1f}"
                                          for s in ("asbuilt", "amp", "pair", "cplx", "paircplx")))
    if fir:
        log(f"  {'FIR V1-128 (s7_fir_mc.csv)':26s} " + " ".join(f"{fir[('U-flat', s)]:5.1f}/{fir[('G-p0.5-l1oct+jig0.25', s)]:5.1f}"
                                                              for s in ("asbuilt", "amp", "pair", "cplx", "paircplx")))

    # ---- headroom -----------------------------------------------------------------------------------------------------
    log("\n=== HEADROOM [L2 time domain]: per-channel output PEAK vs today's same channel (D20, pure gain), full-scale input,"
        " steady-sine full-drive normalisation; squares start from silence (onset included); c0..c7, dB   (*-cap = POST-HOC)")
    d20r = S.read_w8()[0] / S.read_w8()[0].max()
    fl = np.linspace(1.0, 24000.0, 48000)
    cases = []
    wk3 = x3.meta["wk"]
    bands_sos, _ap = A.bank3_sos((700.0, 1600.0))
    amax3 = float(np.abs(A.lr_mags(fl, (700.0, 1600.0), 4) @ wk3).max())
    imp = np.zeros(int(FSAMP))
    imp[0] = 1.0
    bi = [sig.sosfilt(s, imp) for s in bands_sos]
    cases.append((x3.label(), lambda x: np.array([sum(wk3[k][c] * sig.sosfilt(bands_sos[k], x) for k in range(3)) for c in range(8)]),
                  np.array([sum(wk3[k][c] * bi[k] for k in range(3)) for c in range(8)]), amax3))
    for d in lps + [fir_v1]:
        h8 = d.meta["taps8"] if "taps8" in d.meta else h_v1
        amax = float(np.abs(np.stack([sig.freqz(h8[c], worN=fl, fs=FSAMP)[1] for c in range(8)], 1)).max())
        cases.append((d.label(), lambda x, h8=h8: np.array([sig.lfilter(h8[c], 1.0, x) for c in range(8)]), h8, amax))
    hsum, hrows = [], []
    for name, run8, imp8, amax in cases:
        rows_h, lvl = headroom(name, run8, imp8, amax, d20r)
        for k, v in rows_h.items():
            hrows.append([name, k] + [f"{u:.4f}" for u in v])
        hrows.append([name, "onaxis_L1_level_vs_D20_dB", f"{lvl:.4f}"] + [""] * 7)
        log(f"  {name}:")
        for k, v in rows_h.items():
            log(f"     {k:14s} " + " ".join(f"{u:+6.2f}" for u in v) + f"   max {v.max():+6.2f}")
        log(f"     on-axis full drive vs D20 in the L1 convention: {lvl:+.2f} dB")
        hsum.append((name, max(rows_h[s].max() for s in rows_h if s.startswith("square")), rows_h["pink noise"].max(),
                     rows_h["L1 bound"].max(), rows_h["L1 abs vs FS"].max(), lvl))
    log("  summary: design | worst square (vs today) | pink noise | L1 bound vs today (max) | no-clip back-off ="
        " max abs L1 vs FS | on-axis L1 level")
    for name, sq, pk, l1t, l1a, lvl in hsum:
        log(f"     {name:26s} {sq:+6.2f} | {pk:+6.2f} | {l1t:+6.2f} | {l1a:+6.2f} dB | {lvl:+6.2f} dB")

    # ---- drive premise (steady sine) ----------------------------------------------------------------------------------
    log("\n=== DRIVE PREMISE (steady sine): per-channel peak gain vs D20 same channel over all f, c0..c7 (dB) and the"
        " back-off needed to keep every channel <= today")
    for d in lps:
        W = np.abs(d.meta["bank"].mags(fl) @ d.meta["wk"])
        ex = 20 * np.log10(W.max(0) / W.max() / d20r)
        log(f"  {d.label():10s} " + " ".join(f"{v:+5.2f}" for v in ex) + f"  -> back-off {max(0.0, float(ex.max())):.2f} dB")
    Wf = np.abs(np.stack([sig.freqz(h_v1[c], worN=fl, fs=FSAMP)[1] for c in range(8)], 1))
    exf = 20 * np.log10(Wf.max(0) / Wf.max() / d20r)
    log(f"  {'FIR V1-128':10s} " + " ".join(f"{v:+5.2f}" for v in exf) + f"  -> back-off {max(0.0, float(exf.max())):.2f} dB"
        "   (critic R3g F5: FIR needs a similar ~1 dB back-off for the steady-sine premise)")

    # ---- compute & latency -------------------------------------------------------------------------------------------------
    log("\n=== COMPUTE [MAC L3; cycles L4 = MAC x 30-50 cyc/MAC] and LATENCY; frame = 64 samples, 1.333 M cyc at 1 GHz")
    budget = 1.333e6
    for d in lps:
        b = d.meta["bank"]
        mac = b.macs_per_sample()
        macd = sum(b.lens) + 8 * (len(b.xo) + 1)                         # direct form (no symmetry folding)
        log(f"  {d.label():10s} taps {b.lens}: folded {mac:3d} MAC/sample = {mac * 64:5d} MAC/frame -> {mac * 64 * 30 / 1e3:5.0f}-"
            f"{mac * 64 * 50 / 1e3:5.0f} k cyc/frame ({mac * 64 * 30 / budget:.2f}-{mac * 64 * 50 / budget:.2f} of frame);"
            f" direct {macd:3d} MAC/sample = {macd * 64:5d} MAC/frame | latency {b.D} samples = {b.D / FSAMP * 1e3:.2f} ms"
            f" | vs FIR-128x8: folded {32768 / (mac * 64):.1f}x fewer, direct {65536 / (macd * 64):.1f}x fewer")
    log("  references: X3-LR4 69 MAC/sample = 4416 MAC/frame (latency: all-pass, 0.92 ms @ DC); FIR-128 x 8 = 32768"
        " (folded) / 65536 (direct) MAC/frame, latency 63 samples = 1.31 ms; frozen tree C-count 169344 MAC/frame"
        " (polyphase zero-skip 44352)")

    # ---- CSVs -------------------------------------------------------------------------------------------------------
    prow = []
    for d in lps:
        b = d.meta["bank"]
        for i, (fc, n, h) in enumerate(zip(b.xo, b.lens, b.lp)):
            prow.append([d.label(), f"lowpass_{i + 1}", f"{fc:g}", n] + [f"{v:.15e}" for v in h])
        for k, w in enumerate(d.meta["wk"]):
            prow.append([d.label(), f"band_gain_{k + 1}", "", 8] + [f"{v:.15e}" for v in w])
    for name, hdr, rr in (("s7_hybrid_lpxo_ideal.csv", ["design", "metric", "freq_hz", "value"], irows),
                          ("s7_hybrid_lpxo_mc.csv", ["design", "error_model", "strategy", "band_fc_hz", "median_db", "p10_db",
                                                     "yield_ge30_pct", "joint3_yield_pct_1k2k4k", "joint7_yield_pct_DEC1_1k-4k",
                                                     "meanpower_att_per_side_db", "seed", "arrays"], mrows),
                          ("s7_hybrid_lpxo_params.csv", ["design", "item", "fc_hz", "length", "values..."], prow),
                          ("s7_hybrid_lpxo_headroom.csv", ["design", "signal", "c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7"], hrows)):
        with open(os.path.join(HERE, name), "w", newline="") as fp:
            wr = csv.writer(fp, lineterminator="\n")
            wr.writerow(hdr)
            wr.writerows(rr)
    log(f"\nruntime {time.time() - t0:.0f}s ; outputs s7_hybrid_lpxo.log / _ideal.csv / _mc.csv / _params.csv / _headroom.csv")
    with open(os.path.join(HERE, "s7_hybrid_lpxo.log"), "w") as fp:
        fp.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
