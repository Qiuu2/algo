#!/usr/bin/env python3
"""critic R3f Q1: REAL digital-biquad Linkwitz-Riley bank (scipy.signal, bilinear+prewarp), independent of lr_mags().
Checks: in-phase outputs, |B1|+|B2|+|B3| = 1, sum = AP1*AP2 (all-pass), agreement with the closed-form lr_mags,
float32 / fixed-point coefficient quantisation, pole radii, time-domain float32 run, and the effect on X3-LR4 metrics."""
import csv
import os
import sys

import numpy as np
from scipy import signal

REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
sys.path.insert(0, os.path.join(REPO, "sprint7/sim/side30"))
sys.path.insert(0, os.path.join(REPO, "sprint7/sim/side30/fir"))
sys.path.insert(0, os.path.join(REPO, "sprint7/sim/acoustic"))
sys.path.insert(0, os.path.join(REPO, "sprint7/dsp/wtbl"))
FS = 48000.0


def lr_sos(fc, order, kind):
    """LR`order` = Butterworth(order/2) squared, as SOS (bilinear, prewarped by scipy)."""
    s = signal.butter(order // 2, fc, btype=kind, fs=FS, output="sos")
    return np.vstack([s, s])


def ap_sos(fc, order):
    """All-pass of the LR split: AP = LP_LR + HP_LR, built INDEPENDENTLY as B(1/z)/B(z) from the Butterworth denominators."""
    s = signal.butter(order // 2, fc, btype="low", fs=FS, output="sos")
    out = []
    for sec in s:
        a = sec[3:]
        b = a[::-1]                                    # mirror-image numerator -> all-pass
        out.append(np.concatenate([b / a[0] * a[0], a]))
    return np.array(out)


def H(sos, f):
    return signal.sosfreqz(sos, worN=f, fs=FS)[1]


def build_bank(xo, order, cast=None):
    f1, f2 = xo
    parts = {"LP1": lr_sos(f1, order, "low"), "HP1": lr_sos(f1, order, "high"),
             "LP2": lr_sos(f2, order, "low"), "HP2": lr_sos(f2, order, "high"), "AP1": ap_sos(f1, order)}
    if cast is not None:
        parts = {k: cast(v) for k, v in parts.items()}
    return parts


def bank_resp(parts, f):
    h = {k: H(v, f) for k, v in parts.items()}
    return np.stack([h["LP1"] * h["LP2"], h["HP1"] * h["LP2"], h["AP1"] * h["HP2"]], 1), h


def lr_mags_closed(f, xo, order):
    f = np.minimum(np.atleast_1d(np.asarray(f, float)), FS / 2 - 1.0)
    t = lambda fc: (np.tan(np.pi * f / FS) / np.tan(np.pi * fc / FS)) ** order  # noqa: E731
    lp = [1 / (1 + t(fc)) for fc in xo]
    hp = [t(fc) / (1 + t(fc)) for fc in xo]
    return np.stack([lp[1] * lp[0], lp[1] * hp[0], hp[1]], 1)


def qfix(frac_bits):
    def cast(sos):
        return np.round(sos * 2 ** frac_bits) / 2 ** frac_bits
    return cast


def report(tag, B, f, xo, order, hparts):
    tot = B.sum(1)
    ap_ref = hparts["AP1"] * H(ap_sos(xo[1], order), f)            # AP1*AP2 (float64 reference built from float64 poles)
    mag_sum = np.abs(B).sum(1)
    ref_ph = np.angle(tot)
    dph = []
    for k in range(3):
        m = np.abs(B[:, k]) > 1e-6 * np.abs(B).max()
        if not m.any():
            print(f"  {tag:22s} band {k + 1} is IDENTICALLY ZERO after quantisation (numerator gain underflow)")
            return None, None
        dph.append(np.max(np.abs(np.angle(B[m, k] * np.conj(tot[m])))))
    mc = lr_mags_closed(f, xo, order)
    print(f"  {tag:22s} max|sum|B_k| - 1| = {np.abs(mag_sum - 1).max():.2e}   max phase(B_k) - phase(sum) = "
          f"{max(dph):.2e} rad   max||sum B| - 1| = {np.abs(np.abs(tot) - 1).max():.2e}   "
          f"max||B_k| - lr_mags| = {np.abs(np.abs(B) - mc).max():.2e}")
    return mag_sum, dph


def main():
    f = np.concatenate([np.geomspace(10, 23990, 6000), [500.0, 700.0, 1000.0, 1600.0, 4000.0]])
    print("=== Q1 real digital LR bank (scipy.signal.butter fs=48k -> bilinear with prewarp), K=3 [LP1LP2, HP1LP2, AP1HP2]")
    for xo, order in (((700.0, 1600.0), 4), ((700.0, 1600.0), 8), ((700.0, 1400.0), 8)):
        print(f" xo {xo} LR{order}")
        for tag, cast in (("float64", None), ("float32 coeffs", lambda s: s.astype(np.float32).astype(np.float64)),
                          ("Q2.30 coeffs (32-bit)", qfix(30)), ("Q2.14 coeffs (16-bit)", qfix(14))):
            parts = build_bank(xo, order, cast)
            B, hp_ = bank_resp(parts, f)
            report(tag, B, f, xo, order, hp_)
        parts = build_bank(xo, order)
        rad = max(np.abs(np.roots(sec[3:])).max() for v in parts.values() for sec in v)
        print(f"  max pole radius over all sections = {rad:.5f} (stable < 1)")
        # AP cross-check: independent all-pass vs LP_LR + HP_LR (must be identical)
        h1 = H(parts["LP1"], f) + H(parts["HP1"], f)
        print(f"  AP1 (mirror-numerator) vs LP_LR+HP_LR: max diff {np.abs(H(parts['AP1'], f) - h1).max():.2e}")

    # ---- time-domain float32 run of the X3-LR4 bank + 8x3 mixing, compared with the frequency-domain model ----
    print("\n=== time-domain float32 (sosfilt, float32 coeffs + float32 state/data) vs float64 model, X3-LR4-700/1600-e0.1m35")
    wk = None
    with open(os.path.join(REPO, "sprint7/sim/side30/s7_alt_algos_params.csv")) as fp:
        rows = [r for r in csv.DictReader(fp) if r["design"] == "X3-LR4-700/1600-e0.1m35"]
    wk = np.array([[float(r[f"c{i}"]) for i in range(8)] for r in sorted(rows, key=lambda r: int(r["band_or_param"]))])
    print("  band gains wk (3x8) from params CSV:\n" + np.array2string(wk, precision=5))
    rng = np.random.default_rng(1)
    n = 1 << 17
    x = rng.standard_normal(n)
    parts64 = build_bank((700.0, 1600.0), 4)
    parts32 = {k: v.astype(np.float32) for k, v in parts64.items()}

    def run(parts, xx, dt):
        xx = xx.astype(dt)
        b1 = signal.sosfilt(parts["LP2"], signal.sosfilt(parts["LP1"], xx))
        b2 = signal.sosfilt(parts["LP2"], signal.sosfilt(parts["HP1"], xx))
        b3 = signal.sosfilt(parts["HP2"], signal.sosfilt(parts["AP1"], xx))
        return np.stack([b1, b2, b3], 0)
    B64 = run(parts64, x, np.float64)
    B32 = run(parts32, x, np.float32)
    print(f"  dtypes: float32 run output dtype {B32.dtype}")
    Y64 = wk.T @ B64                                               # (8, n)
    Y32 = wk.T.astype(np.float32) @ B32
    err = Y32.astype(np.float64) - Y64
    print(f"  per-channel float32 vs float64 time-domain error: max rel rms = "
          f"{(np.sqrt((err ** 2).mean(1)) / np.sqrt((Y64 ** 2).mean(1))).max():.2e}  "
          f"(= {20 * np.log10((np.sqrt((err ** 2).mean(1)) / np.sqrt((Y64 ** 2).mean(1))).max()):.1f} dB)")
    # sum of the three bands = AP1*AP2 applied to x (false-green identity the doc warns about)
    apx = signal.sosfilt(ap_sos(1600.0, 4), signal.sosfilt(parts64["AP1"], x))
    print(f"  identity check: max|b1+b2+b3 - AP1AP2 x| / rms(x) = {np.abs(B64.sum(0) - apx).max() / x.std():.2e}"
          " (any band-gain set with equal gains per channel passes a sum test -> doc's false-green warning is right)")

    # ---- does the real digital phase change the ideal metrics? W_c(f) = sum_k wk B_k(f) (complex) ----
    import s7_alt_algos as A                                      # module import only (main() not run)

    def cplx_design(cast=None):
        parts = build_bank((700.0, 1600.0), 4, cast)

        def fn(ff):
            B, _ = bank_resp(parts, np.minimum(ff, FS / 2 - 1.0))
            return B @ wk
        return A.CDesign("X3-real", fn)
    ref = A.CDesign("X3-closed", lambda ff: (A.lr_mags(ff, (700.0, 1600.0), 4) @ wk).astype(complex))
    for tag, d in (("closed-form (script)", ref), ("real biquads float64", cplx_design()),
                   ("real biquads Q2.14", cplx_design(qfix(14)))):
        r90 = [A.band_att(d, fc, 90.0) for fc in A.B7]
        jy = [A.single_att(d, ff, th) for th, ff in A.JYT8]
        ib = A.inband_min(d, 1000, 30)
        print(f"  {tag:22s} R90 7 bands {' '.join(f'{v:6.3f}' for v in r90)} | JY/T single {' '.join(f'{v:6.2f}' for v in jy)}"
              f" | 1k/30 in-band min {ib:6.3f} | BW1k {A.bw_at(d, 1000.0):.3f}")
    # imaginary part of W_c(f) / (AP1 AP2)(f): must be ~0 if the channel weight is real up to the common all-pass
    parts = build_bank((700.0, 1600.0), 4)
    B, hparts = bank_resp(parts, f)
    tot = B.sum(1)
    W = B @ wk
    ratio = W / tot[:, None]
    print(f"  max|Im(W_c/AP)| / max|W| = {np.abs(ratio.imag).max() / np.abs(W).max():.2e} ; "
          f"max|Re(W_c/AP) - closed-form W_c| = {np.abs(ratio.real - lr_mags_closed(f, (700.0, 1600.0), 4) @ wk).max():.2e}")
    # group delay of the common all-pass (latency claim 2*sqrt2/wc per LR4 at DC)
    w, gd1 = signal.group_delay(signal.sos2tf(ap_sos(700.0, 4)), w=[1.0, 100.0, 1000.0, 4000.0], fs=FS)
    w, gd2 = signal.group_delay(signal.sos2tf(ap_sos(1600.0, 4)), w=[1.0, 100.0, 1000.0, 4000.0], fs=FS)
    print(f"  group delay AP700 @1/100/1k/4k Hz = {' '.join(f'{v / FS * 1e3:.3f}' for v in gd1)} ms"
          f" (closed 2sqrt2/wc = {2 * np.sqrt(2) / (2 * np.pi * 700) * 1e3:.3f});  AP1600 = {' '.join(f'{v / FS * 1e3:.3f}' for v in gd2)} ms"
          f" (closed {2 * np.sqrt(2) / (2 * np.pi * 1600) * 1e3:.3f});  total @DC {(gd1[0] + gd2[0]) / FS * 1e3:.3f} ms")


if __name__ == "__main__":
    main()
