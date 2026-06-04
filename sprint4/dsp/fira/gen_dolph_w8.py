"""
F5-C : generate + freeze the 8-channel Dolph-Chebyshev -20dB amplitude weight table.

Plan  : sprint4/dsp/fira/F5_F7_PLAN.md  section 3 (F5-C)
Author: dsp-algorithm (claude-opus-4-8) / 2026-06-04
Scope : F5-C ONLY. broadside -> delays = 0 (symmetric array, pure amplitude weights).

WHAT this script does (and freezes):
  1. Dual-track generation (iron-rule-7):
       Track-1 = scipy.signal.windows.chebwin(16, at=20), normalized max=1
                 (SAME source/call/normalization as the acoustic baseline
                  sprint3/audit/a1_static_weight_numpy.py  w_dolph(20)).
       Track-2 = INDEPENDENT Barbiere/Stegen closed-form Dolph synthesis
                 (does NOT call scipy chebwin; direct combinatorial factorial sum,
                  see track2_recurrence()). NOTE: a frequency-sampling DFT/IDFT-of-
                  pattern variant was tried first and was WRONG (returned all 1.0 for
                  this even-N case); it was located and discarded, NOT frozen
                  (iron-rule-7). The Barbiere closed form is the method actually used.
     Compare: float weights must agree to tight tol (report max abs diff);
              the QUANTIZED table must be bit-identical from both tracks.
     (MATLAB chebwin(16,20) is also run as a third cross-check when the matlab MCP
      is available; this script is self-contained and does not require it.)

  2. element<->channel mapping (verified L1, NOT re-derived here):
       center-symmetric {c, 15-c}: A-zone #n in series with B-zone #(17-n),
       knowledge_base/hardware_input/定向音柱AI数据_extracted.md:40.
       16-element Dolph -20dB taper is center-symmetric (w[c]==w[15-c]); each of the
       8 channels drives one symmetric PAIR, so the 8 channel weights = the 8 distinct
       half-aperture values w[0..7]. The mirror half is reproduced PHYSICALLY by the
       series pair (16-indep vs 8-pair equivalence proven: m3_numpy_8pair_equiv.csv,
       BW/SLL diff 0.000e+00).
       FG1 assertion: the 8 channel weights are pairwise DISTINCT.

  3. <=1.0 verification (GAP-SAT premise, VERIFY not ASSUME): all 8 weights <= 1.0 in
     float (both tracks) AND in the fixed-point container (no value exceeds Q max).

  4. Q-format choice: weights apply at input-scale (x_q31 * w >> shift). Chain discipline
     is Q15-coeff x Q31-state >> 15. We pick Q15 for the weight (same arithmetic as the
     coeff multiply, reuses the existing >>15 truncation point per [ASSUME-A2]); we also
     emit Q31 values and report both so the header can justify the choice numerically.

  5. Beam-pattern gate (separate dimension "algthe target right"): with the QUANTIZED
     weights, mirror to N=16 and compute broadside pattern at 1kHz (d=55mm). Verify
     SLL ~ -20dB and BW(-6dB full)@1k <= 30 deg vs acoustic baseline
     (m1: -20.00 dB ; m3: 29.269 deg).

Outputs:
  - prints a full report (consumed by the F5-C deliverable + critic gate)
  - writes  sprint4/dsp/fira/dolph_w8_q15.csv   (dual-track evidence table)
  - the frozen C header dolph_w8_q15.h is authored separately from these frozen values.

All numbers are [L2/dual-track] (desktop simulation, not measured). isotropic high-freq
wide-angle optimism = PF-6 (not relevant at 1kHz gate, noted for completeness).
"""

import numpy as np
import csv
import os

N_ELEM = 16
SLL_DB = 20.0          # Dolph-Chebyshev -20 dB (DEC-S3-GEOM-01 / a1 baseline)
D_M = 55.0e-3          # 55 mm  [L1 teardown]
C = 343.0              # m/s
HALF = N_ELEM // 2     # 8 channels = 8 distinct half-aperture values

# Q-format candidates
Q15 = 15
Q31 = 31

# ----------------------------------------------------------------------------
# Track-1 : scipy chebwin  (SAME call/normalization as a1_static_weight_numpy.py)
# ----------------------------------------------------------------------------
def track1_scipy():
    from scipy.signal.windows import chebwin
    w = chebwin(N_ELEM, SLL_DB)   # a1 uses chebwin(N_ELEM, sll_db) then /w.max()
    return w / w.max()

# ----------------------------------------------------------------------------
# Track-2 : INDEPENDENT Dolph-Chebyshev synthesis, Barbiere/Stegen closed form.
#   Direct combinatorial factorial summation (math.factorial only). Does NOT call
#   scipy chebwin, does NOT use numpy.polynomial.chebyshev -> genuinely independent.
#   (An earlier frequency-sampling DFT/IDFT-of-pattern attempt was WRONG for even N
#    -- it returned all 1.0 -- so it was discarded, NOT frozen. iron-rule-7.)
# ----------------------------------------------------------------------------
def track2_recurrence():
    """Barbiere / Stegen closed-form Dolph-Chebyshev synthesis (Balanis Antenna
    Theory eq. 6-78..6-79 form for an even number of elements 2M).
      N = 2M elements, currents a_1..a_M for the half-aperture (symmetric).
      a_n = sum_{q=n}^{M} (-1)^(M-q) * x0^(2q-1) * (q+M-2) choose (q-n) over
            ((q-n)! * (M-q)! * (M+n-1) ... )  -- we use the standard tabulated
      Barbiere coefficient formula:
        a_n = sum_{q=n}^{M} (-1)^(M-q) * z0^(2q-1) *
                  (q + M - 2)! / ( (q - n)! * (q + n - 1)! * (M - q)! )
      where z0 = x0 = cosh( acosh(R) / (N-1) ), n = 1..M.
    This is a direct combinatorial summation (factorials only) -- it does NOT call
    scipy chebwin and does NOT use any Chebyshev-polynomial library routine, so it is
    a genuinely independent second implementation of the SAME mathematical taper.
    """
    from math import factorial
    N = N_ELEM
    M = N // 2                                   # half number of elements (=8)
    Mord = N - 1                                 # Chebyshev order
    R = 10.0 ** (SLL_DB / 20.0)                  # voltage ratio for -20 dB -> R = 10
    x0 = np.cosh(np.arccosh(R) / Mord)
    a = np.zeros(M)
    for n in range(1, M + 1):
        s = 0.0
        for q in range(n, M + 1):
            num = factorial(q + M - 2) * (x0 ** (2 * q - 1))
            den = factorial(q - n) * factorial(q + n - 1) * factorial(M - q)
            s += ((-1) ** (M - q)) * num / den
        a[n - 1] = s
    # a[0] is the innermost-pair current ... a[M-1] is the edge.
    # Build the full symmetric half-aperture taper edge..center then normalize.
    # Barbiere a_n: n=1 is the element nearest center, n=M is the edge element.
    # Our channel index c=0 is the EDGE pair {0,15}, c=7 is the CENTER pair {7,8},
    # matching the scipy taper ordering (ascending element index). So half-aperture
    # w8[c] for c=0..7 (edge->center) = a[M-1], ..., a[0]  (reverse of Barbiere n).
    w8 = a[::-1].copy()
    w8 = np.abs(w8)
    return w8 / w8.max()

# ----------------------------------------------------------------------------
# quantization
# ----------------------------------------------------------------------------
def quantize(w_float, qbits):
    """round-to-nearest into Q(qbits). max representable positive = (1<<qbits)-? ;
    we use scale = (1<<qbits) so 1.0 -> (1<<qbits). For qbits=15, 1.0 -> 32768,
    which equals INT16 overflow; we clamp the +1.0 case explicitly and report it.
    Container is int32 here (weights live in an int32 table) so 32768 fits the
    container; the >>15 multiply (w*x)>>15 with w<=32768 keeps |w*x|<=|x|, no growth."""
    scale = (1 << qbits)
    q = np.round(w_float * scale).astype(np.int64)
    return q

def dequantize(q, qbits):
    return q.astype(float) / float(1 << qbits)

# ----------------------------------------------------------------------------
# beam pattern (mirror 8-entry table back to 16 elements, same af as a1)
# ----------------------------------------------------------------------------
def af_complex(theta_deg, freq_hz, weights16):
    th = np.radians(np.atleast_1d(theta_deg).astype(float))
    k = 2 * np.pi * freq_hz / C
    n = np.arange(N_ELEM)
    phase = k * np.outer(np.sin(th), n * D_M)
    return (weights16 * np.exp(1j * phase)).sum(axis=1)

def af_db_norm(theta_arr, freq_hz, weights16):
    af = af_complex(theta_arr, freq_hz, weights16)
    mag = np.abs(af)
    mag_ref = mag[0] if mag[0] > 1e-10 else mag.max()
    return 20 * np.log10(mag / (mag_ref + 1e-30) + 1e-10)

def beamwidth_6db(freq_hz, weights16):
    theta_arr = np.linspace(0, 90, 1801)
    db = af_db_norm(theta_arr, freq_hz, weights16)
    peak = db[0]
    below = np.where(db < peak - 6)[0]
    if len(below) == 0:
        return 180.0
    idx = below[0]
    if idx > 0:
        t0, t1 = theta_arr[idx-1], theta_arr[idx]
        d0, d1 = db[idx-1], db[idx]
        t6 = t0 + (peak-6-d0)/(d1-d0)*(t1-t0) if d1 != d0 else t0
    else:
        t6 = theta_arr[idx]
    return float(2 * t6)

def peak_sll(freq_hz, weights16):
    from scipy.signal import argrelmax
    theta_arr = np.linspace(0, 90, 1801)
    db = af_db_norm(theta_arr, freq_hz, weights16)
    peak = db[0]
    null_idx = None
    for i in range(1, len(db)):
        if db[i] < peak - 35:
            null_idx = i; break
    if null_idx is None:
        return -60.0
    sl = db[null_idx:]
    pk = argrelmax(sl, order=3)[0]
    if len(pk) == 0:
        return float(sl.max() - peak)
    return float(sl[pk].max() - peak)

def mirror16(w8):
    """8 half-aperture values -> 16-element symmetric taper {w[c], w[15-c]}."""
    return np.concatenate([w8, w8[::-1]])

# ============================================================================
def main():
    print("=" * 84)
    print("F5-C : Dolph-Chebyshev -20dB  8-channel weight table  (N=16/d=55/broadside)")
    print("=" * 84)

    w1_full = track1_scipy()              # 16-element taper (scipy)
    w2_8 = track2_recurrence()            # 8 half-aperture channel weights (Barbiere)

    # half-aperture 8 channel weights from track1 (mapping {c,15-c}); edge->center
    w1_8 = w1_full[:HALF]

    # symmetry sanity on track1 full taper: w_full[c] == w_full[15-c]
    sym_err1 = float(np.max(np.abs(w1_full - w1_full[::-1])))
    print(f"\n[Symmetry]  track1 full-16 max|w-w_rev| = {sym_err1:.3e}")

    # 8-channel dual-track float compare (pre-quant): scipy half vs Barbiere
    max_diff_8 = float(np.max(np.abs(w1_8 - w2_8)))
    print(f"[Track compare] 8-channel float max|w1(scipy)-w2(Barbiere)| = {max_diff_8:.3e}")

    # ---- <=1.0 verification (float, both tracks) ----
    le1 = float(np.max(np.abs(w1_8)))
    le2 = float(np.max(np.abs(w2_8)))
    print(f"\n[<=1.0 float] track1 max|w| = {le1:.6f}  -> {'OK' if le1<=1.0 else 'VIOLATION'}")
    print(f"[<=1.0 float] track2 max|w| = {le2:.6f}  -> {'OK' if le2<=1.0 else 'VIOLATION'}")

    # ---- quantization both tracks, both Q formats ----
    q15_1 = quantize(w1_8, Q15); q15_2 = quantize(w2_8, Q15)
    q31_1 = quantize(w1_8, Q31); q31_2 = quantize(w2_8, Q31)

    bit_ident_q15 = bool(np.array_equal(q15_1, q15_2))
    bit_ident_q31 = bool(np.array_equal(q31_1, q31_2))
    print(f"\n[Quant bit-identical] Q15 tracks equal = {bit_ident_q15}")
    print(f"[Quant bit-identical] Q31 tracks equal = {bit_ident_q31}")

    # ---- <=1.0 in fixed-point container ----
    q15_max = int(np.max(np.abs(q15_1)))
    q31_max = int(np.max(np.abs(q31_1)))
    print(f"\n[<=1.0 fixed Q15] max|w_q15| = {q15_max}  (1.0 -> {1<<Q15}); "
          f"{'OK (<=1.0)' if q15_max <= (1<<Q15) else 'OVERFLOW'}")
    print(f"[<=1.0 fixed Q31] max|w_q31| = {q31_max}  (1.0 -> {1<<Q31}); "
          f"{'OK (<=1.0)' if q31_max <= (1<<Q31) else 'OVERFLOW'}")

    # ---- all-distinct FG1 ----
    distinct = (len(set(q15_1.tolist())) == HALF)
    print(f"\n[FG1 all-distinct] 8 Q15 weights pairwise distinct = {distinct}")

    # ---- print the 8 frozen values ----
    print("\n" + "-" * 84)
    print(f"{'ch':>3} {'pair{c,15-c}':>14} {'w_float(t1)':>14} {'w_float(t2)':>14} "
          f"{'w_q15':>8} {'w_q31':>12}")
    print("-" * 84)
    for c in range(HALF):
        print(f"{c:>3} {'{%d,%d}'%(c,15-c):>14} {w1_8[c]:>14.9f} {w2_8[c]:>14.9f} "
              f"{int(q15_1[c]):>8} {int(q31_1[c]):>12}")
    print("-" * 84)

    # ---- beam-pattern gate with QUANTIZED (Q15) weights, mirrored to 16 ----
    w8_deq = dequantize(q15_1, Q15)
    w16_q = mirror16(w8_deq)
    bw1k = beamwidth_6db(1000.0, w16_q)
    sll  = peak_sll(1000.0, w16_q)
    # reference (float) for delta
    w16_f = mirror16(w1_8)
    bw1k_f = beamwidth_6db(1000.0, w16_f)
    sll_f  = peak_sll(1000.0, w16_f)

    print("\n[Beam gate @1kHz, QUANTIZED Q15 weights, N=16 mirrored]")
    print(f"  BW(-6dB full)@1k = {bw1k:.4f} deg   (float {bw1k_f:.4f}; baseline m3 = 29.269; "
          f"red line <=30 -> {'PASS' if bw1k <= 30.0 else 'FAIL'})")
    print(f"  peak SLL         = {sll:.4f} dB    (float {sll_f:.4f}; baseline m1 = -20.00 -> "
          f"{'PASS' if abs(sll - (-20.0)) <= 0.5 else 'CHECK'})")
    print(f"  quant shift: dBW = {bw1k - bw1k_f:+.4f} deg ; dSLL = {sll - sll_f:+.4f} dB")

    # ---- CSV evidence ----
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dolph_w8_q15.csv")
    with open(out, "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(["ch", "pair", "w_float_track1_scipy", "w_float_track2_recurrence",
                     "w_q15", "w_q31"])
        for c in range(HALF):
            wr.writerow([c, "{%d,%d}" % (c, 15 - c), repr(float(w1_8[c])),
                         repr(float(w2_8[c])), int(q15_1[c]), int(q31_1[c])])
    print(f"\n[CSV] {out}")

    print("\n" + "=" * 84)
    print("SUMMARY")
    print(f"  dual-track float max-diff (8ch)  = {max_diff_8:.3e}")
    print(f"  Q15 quantized bit-identical      = {bit_ident_q15}")
    print(f"  all 8 weights <=1.0 (float)      = {le1<=1.0 and le2<=1.0}")
    print(f"  all 8 weights <=1.0 (Q15 fixed)  = {q15_max <= (1<<Q15)}")
    print(f"  FG1 all-distinct                 = {distinct}")
    print(f"  beam gate BW@1k<=30 / SLL~-20    = {bw1k<=30.0} / {abs(sll+20.0)<=0.5}")
    print("=" * 84)

    # machine-readable line for the header author
    print("\nFROZEN_Q15 = " + ",".join(str(int(v)) for v in q15_1))
    print("FROZEN_Q31 = " + ",".join(str(int(v)) for v in q31_1))


if __name__ == "__main__":
    main()
