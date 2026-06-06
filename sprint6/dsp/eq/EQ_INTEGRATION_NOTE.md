# O1 EQ + Limiter -- Integration Note (M2 adapter) + Desktop Closure

Module: `sprint6/dsp/eq/eq_limiter.{h,c}`  (master-bus shaping EQ + per-channel
protection limiter). Decision in archive: DEC-S5-EQ-O1-01. ASCII only.

This module is a STANDALONE desktop deliverable. It is NOT wired into the
frozen FIRA pipeline. Frozen-file zero-touch is honored (no edits to
`sprint4/dsp/...` or `sprint5/dsp/...`). M2 does the wiring.

---

## 1. Where it sits in the chain (per EQ_PRD §2.2)

```
master mono stream
   |
   v
[ eq_master_process ]   <-- 2-3 biquad shaping EQ, ONCE, pre fan-out
   |
   v
   fan-out (x8) + per-channel focusing fractional delay  (STEER-2, FIRA core)
   |
   v
[ eq_limiter_process_ch ] x8  <-- per-channel protection, T_k = T*w[k]
   |
   v
   8 amplifier channels
```

- Master-bus EQ placement is valid in broadside (8ch same signal) AND focusing
  (EQ commutes with the per-channel LTI delay), per EQ_PRD §2.2 -- ~1/8 cost vs
  per-channel EQ.
- Limiter is AFTER fan-out + weighting (it must see each channel's actual peak),
  threshold scaled by the Dolph weight (D14) to preserve the -20dB taper.

## 2. M2 adapter checklist (NOT done here -- M2 only)

1. Frame caliber reconciliation: this module declares its own `EQ_FRAME=64`,
   `EQ_FS_HZ=48000`, `EQ_NCH=8`. The frozen harness uses `BENCH_FRAME/NFR/FS`
   (`bench_harness.h`). M2 must assert `EQ_FRAME == BENCH_FRAME`,
   `EQ_NCH == DOLPH_W8_NCH`, `EQ_FS_HZ == FS` at integration -- a compile-time
   `_Static_assert` in the adapter, NOT a silent assumption.
2. Data type: module is float32 (`float`). The FIRA core path is fixed-point
   Q31 (bit-exact). M2 adapter owns the Q31<->float conversion at the EQ
   boundary (master stream pre-EQ: int32 Q31 -> float; post-limiter per-ch:
   float -> int32 Q31 to the DAC). Conversion scaling is an M2 decision; not
   pre-judged here.
3. Weight source: limiter `w[8]` must be loaded from the SAME single source as
   the beamformer: `sprint4/dsp/fira/dolph_w8_q15.csv` col `w_float_track1_scipy`
   (the 8 values are hard-coded in `eq_test.c` for the desktop test ONLY; M2
   loads from the shared table to avoid a second copy drifting).
4. EQ coefficients: currently flat/unity placeholders + 2 arbitrary test
   biquads (in `eq_test.c`). Product band coefficients wait R3 anechoic on-axis
   response (EQ_PRD:45). M2 loads measured coefficients; the interface
   (`eq_biquad_set`) is final.
5. Limiter threshold `t_base`: PLACEHOLDER [L4] (0.8 full-scale in the test).
   Final value waits line-3 vendor letter (Xmax / thermal rating). TODO marker
   in `eq_limiter.c::eq_limiter_init`.

## 3. Desktop verification result (this deliverable)

Build: `gcc -O2 -Wall -Wextra -std=c99 eq_limiter.c eq_test.c -o eq_test -lm`
(clean compile, no warnings; guard-stub N/A -- pure C compiles fully on host).

| Check | Result | Gate |
|---|---|---|
| Biquad cascade impulse response, C float32 vs scipy.signal float64 | max abs err **1.51e-07**, max rel err 2.09e-04 | <= 1e-4 float32 envelope PASS |
| Non-trivial-filter guard (tail energy of ref impulse) | 0.0279 > 0.01 | PASS (test is filter-dependent, not identity) |
| Step response settles to DC gain | final 0.500418 vs DC gain 0.500418, diff 1.5e-07 | stable PASS |
| Limiter clamp out == clamp(in, +/- t_ch) over/under/zero, 8ch | exact | PASS |
| Taper preserved: t_ch[k]/t_base == Dolph w8[k] | spread t7/t1 = 1.9829 == 1/0.5043 | PASS |

Precision note (honest): the gate is **1e-4 float32**, NOT the 1e-10
linear-algorithm rule. Rationale: this module is intentionally float32 on the
SHARC+ float core; 1e-10 applies to bit-exact fixed-point/double linear paths.
The observed 1.51e-07 is the genuine float32-vs-float64 single-precision
accumulation bound for a 256-sample 2-biquad IIR cascade -- well inside
envelope. If M2 later demands tighter, the path is double or fixed-point Q
with the 1e-10 rule re-applied.

## 4. Desktop compute budget (L2-account; C9 = budget only, no selection)

Source-counted MAC/sample (from `eq_limiter.c::eq_biquad_tick`, 3 arithmetic
lines = 5 MAC/biquad; master-bus = 1 stream, NOT x8):

| Config | MAC/samp | MCPS @30 cyc/MAC | MCPS @50 cyc/MAC |
|---|---|---|---|
| EQ 2 biquad | 10 | 14.4 | 24.0 |
| EQ 3 biquad | 15 | 21.6 | 36.0 |
| limiter 8ch (pessimistic 1 op/samp/ch, really ~0) | 8 | 11.5 | 19.2 |
| **O1 EQ-only** | 10-15 | **14.4 .. 36.0** | |
| **O1 EQ + limiter (pessimistic)** | | **14.4 .. 55.2** | |

cyc/MAC band {30,50} = mandatory board envelope (decisions_log:234/770);
single-source unit conversion (no MMAC mis-attach).

Reconciliation vs in-archive [L4] placeholder (DEC-S5-EQ-O1-01) **29-60 MCPS**
(= 20-25 MAC/samp x 48k x {30,50}): source-counted EQ-only (10/15 MAC/samp) sits
at/below the L4 low end; the L4 60 MCPS high end holds as a conservative ceiling
once limiter + per-segment orchestration are added. **The [L4] placeholder is
not exceeded by the desktop account.**

Grade of this number: **[L2-account / board-factor-band]**. It is a desktop
MAC-count x board-cyc-band, NOT measured cycles. Upgrade to L1 needs on-board
EQ profiling (post M1; not pre-judged here).

## 5. Honest gaps (what desktop CANNOT close)

0. **[R29 F29-MINOR-1] EQ group delay / phase vs limiter peak caliber + total latency
   budget = M2 interface items**: the EQ biquads shift phase, so the per-channel
   limiter (downstream of EQ + fan-out + weighting) sees a peak whose timing/level
   differs from the pre-EQ signal -- the limiter peak caliber after EQ insertion is
   an M2 check item; and the EQ group delay stacks with the focusing fractional
   delays -- the total chain latency budget must be drawn up at M2 integration.
1. **L1 cycle cost** -- desktop gives [L2-account] MCPS only. Real per-segment
   orchestration + cache + concurrent FIRA bus arbitration are board-only
   (post-M1 profiling). The 30-50 cyc/MAC band is the honest envelope; the true
   per-biquad cyc/MAC on SHARC float may differ (float biquad is not a flat-FIR
   kernel -- could be lower than 30 for a tight unrolled loop, or higher with
   stalls). NOT pre-judged.
2. **EQ coefficients** -- flat/test placeholders only. Band count (2 vs 3) and
   curves wait R3 anechoic on-axis response (EQ_PRD:45). Frequency response
   verification here proves the *implementation* is correct, NOT that the
   product needs any particular EQ.
3. **Limiter absolute threshold T** -- [L4] placeholder (0.8 FS). Real ceiling
   waits line-3 Xmax / thermal rating + U3 amp gain. Structure is complete; the
   single scalar `t_base` is the only open value, and the taper-scaling
   structure around it is verified.
4. **Q31<->float boundary** -- not implemented (M2 owns; the FIRA core is Q31,
   this module float). No conversion scaling pre-judged.
5. **DF1 vs DF2T numeric choice on the actual SHARC float ABI** -- DF1 chosen
   and desktop-verified; if board profiling shows DF2T is materially cheaper or
   more accurate, swapping is a localized change (interface unchanged).
6. **Limiter algorithm class** -- this is a hard peak clamp (sign-preserving).
   If the PRD later wants look-ahead / soft-knee / RMS, MAC rises and this
   simple clamp is replaced (EQ_PRD §5 gap 8). Hard clamp is the protection
   floor, sufficient for "防烧功放".

---

reviewer pending: independent critic (gate 2) + CTO sanity (gate 3).
Not committed by this teammate (PM lands after critic passes).
dsp-algorithm teammate (instance-2) @ claude-opus-4-8 / 2026-06-06.
