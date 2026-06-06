/*
 * eq_limiter.h  --  O1 master-bus shaping EQ + per-channel protection limiter.
 *
 * Scope (DEC-S5-EQ-O1-01, EQ_PRD_DECISION_MATERIAL.md):
 *   - master-bus shaping EQ : 2-3 biquad cascade, applied ONCE on the
 *     pre-fanout master signal (fan-out front). LTI / commutes with the
 *     per-channel fractional-delay focusing stage (EQ_PRD sec.2.2).
 *   - protection limiter : per-channel (8 amplifier channels), threshold
 *     scaled by Dolph weight  T_k = T * w[k]  (D14, keep -20dB taper).
 *
 * Numeric type: float32.  Rationale: ADSP-21569 is a SHARC+ floating-point
 *   core (native 32/40-bit float, 1 GHz). Biquad on a float DSP avoids the
 *   Q-format coefficient-quantization / limit-cycle bookkeeping that a
 *   fixed-point IIR would need, and the FIRA beamform core already runs the
 *   bit-exact-critical path; the master-bus EQ is a low-rate (1 stream)
 *   shaping filter where float is both cheaper to get right and accurate.
 *   (Fixed-point would only be justified on a fixed-point part.)
 *
 * Coefficients here are PLACEHOLDER (flat / unity) with a parameterizable
 *   interface. Final band tuning waits R3 anechoic on-axis response
 *   (EQ_PRD:45/sec.5.1). Absolute limiter threshold T is PLACEHOLDER [L4],
 *   pending line-3 vendor letter (Xmax / thermal rating). See TODO markers.
 *
 * This module is INDEPENDENT of the frozen FIRA code. It is NOT wired into
 *   the frozen pipeline here; M2 integration only (adapter note in
 *   EQ_INTEGRATION_NOTE.md). ASCII only.
 */
#ifndef EQ_LIMITER_H
#define EQ_LIMITER_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---- compile-time caliber (independent mirror of the FIRA convention) ----
 * FRAME / FS / NCH match the project caliber (FRAME=64 samples, FS=48 kHz,
 * NCH=8 amplifier channels). These are this module's own constants; they do
 * NOT include or depend on the frozen bench_harness.h. M2 adapter reconciles. */
#define EQ_FRAME      64
#define EQ_FS_HZ      48000
#define EQ_NCH        8        /* 8 amplifier channels (each drives a pair) */
#define EQ_MAX_BANDS  3        /* O1 = 2-3 biquad master-bus cascade */

/* Direct-Form-1 biquad, float. Transposed-Direct-Form-2 (DF2T) would also be
 * a valid float choice (better numeric behavior); DF1 chosen for transparent
 * state mapping (z1/z2 = delayed input/output) and is exact-enough on float
 * for a 2-3 band master-bus shaper. b0,b1,b2 / a1,a2 normalized (a0 == 1). */
typedef struct {
    float b0, b1, b2;   /* feed-forward */
    float a1, a2;       /* feed-back (a0 normalized to 1) */
    float z1, z2;       /* state: DF1 -> x[n-1],x[n-2]? no: see eq_limiter.c */
} eq_biquad_t;

typedef struct {
    int         n_bands;                 /* active biquads, 1..EQ_MAX_BANDS */
    eq_biquad_t band[EQ_MAX_BANDS];
} eq_master_t;

typedef struct {
    /* base absolute threshold T (linear, full-scale 1.0 ref).
     * PLACEHOLDER [L4] -- final value pending line-3 Xmax/thermal. */
    float t_base;
    float t_ch[EQ_NCH];                  /* effective per-ch = t_base * w[k]  */
    float w[EQ_NCH];                     /* Dolph -20dB channel weight w8[k]   */
} eq_limiter_t;

/* ---- master-bus EQ ---- */

/* Initialize all biquads flat (unity passthrough) with n_bands active. */
void eq_master_init_flat(eq_master_t *eq, int n_bands);

/* Load one biquad's coefficients (already normalized, a0==1) and reset state. */
void eq_biquad_set(eq_biquad_t *bq,
                   float b0, float b1, float b2, float a1, float a2);

/* Reset only the filter state (z1,z2) of every band; coefficients kept. */
void eq_master_reset_state(eq_master_t *eq);

/* Process one master-bus frame in place: x[0..n-1] -> EQ(x). Mono stream
 * (master bus, pre fan-out). n = number of samples (e.g. EQ_FRAME). */
void eq_master_process(eq_master_t *eq, float *x, size_t n);

/* ---- per-channel protection limiter ---- */

/* Initialize limiter: base threshold t_base [L4 placeholder] and the 8
 * Dolph weights w[8]; computes t_ch[k] = t_base * w[k] (D14 taper-preserving). */
void eq_limiter_init(eq_limiter_t *lim, float t_base, const float w[EQ_NCH]);

/* Hard peak-protection limiter, one sample, channel k:
 *   |y| clamped to t_ch[k], sign preserved. Scalar, ~0 MAC. */
float eq_limiter_sample(const eq_limiter_t *lim, int ch, float x);

/* Apply limiter to one channel's frame in place. */
void eq_limiter_process_ch(const eq_limiter_t *lim, int ch, float *x, size_t n);

#ifdef __cplusplus
}
#endif

#endif /* EQ_LIMITER_H */
