/*
 * eq_limiter.c  --  O1 master-bus shaping EQ + per-channel protection limiter.
 * See eq_limiter.h for scope / governance. ASCII only. Float (SHARC+ native).
 *
 * MAC ACCOUNTING (source-line anchored; counted, not guessed):
 *   Biquad, Direct-Form-1, per sample (eq_biquad_tick below):
 *     y  = b0*x + z1                     1 mul-add  (b0*x)         -> [c.b0]
 *     z1 = b1*x - a1*y + z2              2 mul-add  (b1*x, a1*y)   -> [c.b1,c.a1]
 *     z2 = b2*x - a2*y                   2 mul-add  (b2*x, a2*y)   -> [c.b2,c.a2]
 *   => 5 multiply-accumulates / sample / biquad. (Canonical DF1 = 5 MAC.)
 *   Master-bus EQ = n_bands biquads on ONE (master) stream:
 *     2 biquad -> 10 MAC/sample ; 3 biquad -> 15 MAC/sample. (ONE stream,
 *     NOT x8 -- that is the master-bus 1/8 saving, EQ_PRD sec.2.2.)
 *   Limiter (eq_limiter_sample): fabsf + compare + (rare) scale. NO multiply
 *     on the in-range path; the clamp path is 1 mul (t*sign). Treated as
 *     ~0 MAC (scalar control), per EQ_PRD sec.2.2 / CO-5. Counted as 0 MAC below.
 *
 * The MCPS rollup (MAC/samp x 48000 x {30,50} cyc/MAC) is in
 *   eq_compute_budget.py + EQ_INTEGRATION_NOTE.md sec.4. This file is the
 *   source of the per-sample MAC counts those use.
 */
#include "eq_limiter.h"
#include <math.h>

/* ----- DF1 biquad single-sample tick. 5 MAC. State convention:
 *   z1,z2 are the two feedback/feedforward accumulator taps of the
 *   transposed-style DF1 (a.k.a. "DF1 with combined state"):
 *     y  = b0*x + z1
 *     z1 = b1*x + z2 - a1*y
 *     z2 = b2*x      - a2*y
 *   This is numerically equivalent to classic DF1 for an LTI biquad and
 *   uses 2 state words instead of 4. -------------------------------------- */
static inline float eq_biquad_tick(eq_biquad_t *bq, float x)
{
    float y  = bq->b0 * x + bq->z1;                 /* MAC 1 */
    bq->z1   = bq->b1 * x + bq->z2 - bq->a1 * y;    /* MAC 2,3 */
    bq->z2   = bq->b2 * x          - bq->a2 * y;    /* MAC 4,5 */
    return y;
}

void eq_biquad_set(eq_biquad_t *bq,
                   float b0, float b1, float b2, float a1, float a2)
{
    bq->b0 = b0; bq->b1 = b1; bq->b2 = b2;
    bq->a1 = a1; bq->a2 = a2;
    bq->z1 = 0.0f; bq->z2 = 0.0f;
}

void eq_master_init_flat(eq_master_t *eq, int n_bands)
{
    int i;
    if (n_bands < 1) n_bands = 1;
    if (n_bands > EQ_MAX_BANDS) n_bands = EQ_MAX_BANDS;
    eq->n_bands = n_bands;
    /* PLACEHOLDER coefficients: unity passthrough (b0=1, rest 0).
     * Final band coefficients wait R3 anechoic on-axis response [L4->R3]. */
    for (i = 0; i < EQ_MAX_BANDS; i++) {
        eq_biquad_set(&eq->band[i], 1.0f, 0.0f, 0.0f, 0.0f, 0.0f);
    }
}

void eq_master_reset_state(eq_master_t *eq)
{
    int i;
    for (i = 0; i < EQ_MAX_BANDS; i++) {
        eq->band[i].z1 = 0.0f;
        eq->band[i].z2 = 0.0f;
    }
}

void eq_master_process(eq_master_t *eq, float *x, size_t n)
{
    size_t i;
    int    b;
    for (i = 0; i < n; i++) {
        float s = x[i];
        for (b = 0; b < eq->n_bands; b++) {
            s = eq_biquad_tick(&eq->band[b], s);
        }
        x[i] = s;
    }
}

/* ----- per-channel protection limiter ----- */

void eq_limiter_init(eq_limiter_t *lim, float t_base, const float w[EQ_NCH])
{
    int k;
    /* t_base is a PLACEHOLDER absolute full-scale fraction [L4].
     * TODO(line-3): replace with measured Xmax / thermal-derived ceiling. */
    lim->t_base = t_base;
    for (k = 0; k < EQ_NCH; k++) {
        lim->w[k]    = w[k];
        /* D14: scale threshold by Dolph weight so the realized taper is
         * preserved under hard drive (common threshold would clip the
         * highest-weight channel first and push taper toward uniform ->
         * sidelobe rise / -20dB SLL degradation, EQ_PRD sec.2.2). */
        lim->t_ch[k] = t_base * w[k];
    }
}

float eq_limiter_sample(const eq_limiter_t *lim, int ch, float x)
{
    float t = lim->t_ch[ch];
    if (x >  t) return  t;
    if (x < -t) return -t;
    return x;
}

void eq_limiter_process_ch(const eq_limiter_t *lim, int ch, float *x, size_t n)
{
    size_t i;
    for (i = 0; i < n; i++) {
        x[i] = eq_limiter_sample(lim, ch, x[i]);
    }
}
