#!/usr/bin/env python3
"""
eq_verify.py -- desktop cross-check of eq_test (C) against scipy.signal.

Reads eq_test stdout from a file argument (or stdin) and checks:
  1) Biquad cascade frequency/impulse response: reconstruct the exact
     transfer function from the C-emitted COEF lines using scipy, generate
     the reference impulse response, and compare to the C IMP samples
     point-by-point.  (Linear-algorithm precision discipline.)
  2) Limiter test vectors: out == clamp(in, +/- t_ch), and t_ch == t_base*w[k]
     (Dolph taper-preserving D14), and channel differentiation is real.

The reference is computed in float64; the C path is float32, so the bound is
a float32-accumulation bound, NOT 1e-10.  We report max |err| and check it
against a documented float32 envelope.  (1e-10 is for bit-exact fixed/double
linear paths; this module is intentionally float32 on a float DSP, so the
honest bound is ~1e-5 relative for a 256-tap IIR cascade response.)

Usage:  python3 eq_verify.py eq_out.txt
"""
import sys
import numpy as np
from scipy import signal

# float32 cascade-response envelope. Derived (not invented): a 2-biquad IIR
# cascade evaluated in float32 over 256 samples accumulates roundoff on the
# order of n_ops * eps32 ~ 1e3 * 1.2e-7 ~ 1e-4 worst case; we set a tight
# practical gate and report the actual observed value for the record.
FLOAT32_ABS_GATE = 1e-4


def parse(lines):
    coef, imp, step, lim = [], [], [], []
    for ln in lines:
        t = ln.split()
        if not t:
            continue
        if t[0] == "COEF":
            coef.append((int(t[1]), *map(float, t[2:7])))
        elif t[0] == "IMP":
            imp.append((int(t[1]), float(t[2])))
        elif t[0] == "STEP":
            step.append((int(t[1]), float(t[2])))
        elif t[0] == "LIM":
            lim.append((int(t[1]), float(t[2]), float(t[3]), float(t[4])))
    return coef, imp, step, lim


def main():
    src = open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin
    coef, imp, step, lim = parse(src.readlines())

    print("=== eq_verify.py : C (float32) vs scipy.signal (float64) ===")
    ok = True

    # ---- 1) biquad cascade impulse response ----
    coef = sorted(coef, key=lambda r: r[0])
    sos = np.array([[c[1], c[2], c[3], 1.0, c[4], c[5]] for c in coef],
                   dtype=np.float64)
    print("biquads (sos, a0=1):")
    for c in coef:
        print("  band %d: b=[% .6f % .6f % .6f] a=[1 % .6f % .6f]"
              % (c[0], c[1], c[2], c[3], c[4], c[5]))

    n = len(imp)
    impulse = np.zeros(n, dtype=np.float64)
    impulse[0] = 1.0
    ref = signal.sosfilt(sos, impulse)            # scipy reference response

    c_imp = np.array([v for _, v in sorted(imp, key=lambda r: r[0])],
                     dtype=np.float64)
    err = np.abs(c_imp - ref)
    max_abs = float(err.max())
    # only count where reference is meaningfully non-zero for relative
    nz = np.abs(ref) > 1e-6
    max_rel = float((err[nz] / np.abs(ref[nz])).max()) if nz.any() else 0.0
    print("impulse response: N=%d  max|abs err|=%.3e  max|rel err|=%.3e"
          % (n, max_abs, max_rel))

    # non-trivial guard: a flat (identity) EQ would have ref[0]=1, ref[1:]=0.
    # Confirm the test filter is genuinely non-trivial (filter-dependent test).
    energy_tail = float(np.sum(ref[1:] ** 2))
    print("non-trivial guard: tail energy (ref[1:]) = %.4f (must be > 0.01)"
          % energy_tail)
    if energy_tail <= 0.01:
        print("  FAIL: impulse response is ~identity, test not filter-dependent")
        ok = False

    if max_abs <= FLOAT32_ABS_GATE:
        print("  PASS impulse: max abs err %.3e <= float32 gate %.1e"
              % (max_abs, FLOAT32_ABS_GATE))
    else:
        print("  FAIL impulse: max abs err %.3e > gate %.1e"
              % (max_abs, FLOAT32_ABS_GATE))
        ok = False

    # ---- 1b) magnitude response on a frequency grid (frequency-domain view) ----
    w, h_ref = signal.sosfreqz(sos, worN=512, fs=48000.0)
    # reconstruct C response transfer via its impulse response FFT (zero-pad)
    H_c = np.fft.rfft(c_imp, n=4096)
    f_c = np.fft.rfftfreq(4096, d=1.0 / 48000.0)
    # sample scipy mag at same freqs
    h_ref_grid = np.interp(f_c, w, np.abs(h_ref))
    mag_err = np.abs(np.abs(H_c) - h_ref_grid)
    band = f_c <= 20000.0
    print("magnitude response (0-20kHz): max|err| = %.3e"
          % float(mag_err[band].max()))

    # ---- 2) step response settling (stability) ----
    s = np.array([v for _, v in sorted(step, key=lambda r: r[0])])
    dc_gain = float(np.sum(ref))     # sum of impulse response = DC gain
    settled = float(s[-1])
    print("step response: final value=%.6f  expected DC gain=%.6f  diff=%.3e"
          % (settled, dc_gain, abs(settled - dc_gain)))
    if abs(settled - dc_gain) > 1e-3:
        print("  WARN: step not settled to DC gain (long tail or instability)")

    # ---- 3) limiter vectors ----
    print("limiter check (out == clamp(in, +/-t_ch), t_ch=t_base*w[k]):")
    lim_ok = True
    t_by_ch = {}
    for ch, t_ch, vin, vout in lim:
        expect = max(-t_ch, min(t_ch, vin))
        if abs(expect - vout) > 1e-6:
            print("  FAIL ch=%d in=%.3f t=%.4f out=%.6f expect=%.6f"
                  % (ch, vin, t_ch, vout, expect))
            lim_ok = False
        t_by_ch[ch] = t_ch
    # taper preservation: t_ch ratios must equal Dolph w8 ratios
    w8 = [0.8668296927388105, 0.5043100646541281, 0.6216704381816565,
          0.7333793765883259, 0.8327331038598036, 0.9135146112868511,
          0.9705186581255053, 1.0]
    t0 = t_by_ch[7]               # ch7 weight == 1.0 -> t_base
    for ch in range(8):
        ratio = t_by_ch[ch] / t0
        if abs(ratio - w8[ch]) > 1e-5:
            print("  FAIL taper ch=%d t_ch/t_base=%.6f expect w=%.6f"
                  % (ch, ratio, w8[ch]))
            lim_ok = False
    # channel differentiation real (ch1 weakest != ch7 strongest)
    spread = t_by_ch[7] / t_by_ch[1]
    print("  taper spread t_ch[7]/t_ch[1] = %.4f (Dolph ~1/0.504 = %.4f)"
          % (spread, 1.0 / 0.5043100646541281))
    print("  limiter: %s" % ("PASS" if lim_ok else "FAIL"))
    ok = ok and lim_ok

    print("=== OVERALL: %s ===" % ("PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
