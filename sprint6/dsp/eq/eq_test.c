/*
 * eq_test.c  --  desktop verification driver for eq_limiter.{c,h}.
 * Compiled with gcc -O2 on host (pure C, no SHARC headers). ASCII only.
 *
 * Emits machine-readable lines to stdout that eq_verify.py cross-checks
 * against scipy.signal references:
 *
 *   COEF band b0 b1 b2 a1 a2          (the test biquad coefficients)
 *   IMP  k y                         (impulse response sample k -> y)
 *   STEP k y                         (unit-step response, settling check)
 *   LIM  ch t_ch in out              (limiter test vectors)
 *
 * The impulse response of the cascade fully determines the (linear) filter,
 * so scipy can reconstruct the exact transfer function from COEF and compare
 * the IMP samples point-by-point. This makes the precision check filter-
 * dependent (a flat/identity EQ would produce a different impulse response
 * and fail the non-trivial-coefficient case).
 */
#include "eq_limiter.h"
#include <stdio.h>

/* Two non-trivial test biquads (peaking + shelf shaped, arbitrary but
 * stable). Used ONLY for verification -- product coefficients wait R3. */
static void load_test_eq(eq_master_t *eq)
{
    eq_master_init_flat(eq, 2);
    /* band 0: a mild peaking biquad (coeffs precomputed, a0 normalized). */
    eq_biquad_set(&eq->band[0],
                  1.026099f, -1.945307f, 0.937821f,   /* b0 b1 b2 */
                  -1.945307f, 0.963920f);             /* a1 a2 */
    /* band 1: a high-shelf-ish biquad (distinct, stable). */
    eq_biquad_set(&eq->band[1],
                  0.965926f, -1.515915f, 0.620204f,
                  -1.470000f, 0.610000f);
}

int main(void)
{
    eq_master_t eq;
    int   i, ch;
    const int NIMP = 256;

    /* ---- COEF dump ---- */
    load_test_eq(&eq);
    for (i = 0; i < eq.n_bands; i++) {
        printf("COEF %d %.9g %.9g %.9g %.9g %.9g\n", i,
               eq.band[i].b0, eq.band[i].b1, eq.band[i].b2,
               eq.band[i].a1, eq.band[i].a2);
    }

    /* ---- impulse response of the cascade ---- */
    load_test_eq(&eq);                 /* fresh state */
    eq_master_reset_state(&eq);
    {
        float buf[1];
        for (i = 0; i < NIMP; i++) {
            buf[0] = (i == 0) ? 1.0f : 0.0f;
            eq_master_process(&eq, buf, 1);
            printf("IMP %d %.9g\n", i, buf[0]);
        }
    }

    /* ---- step response (settling / stability sanity) ---- */
    load_test_eq(&eq);
    eq_master_reset_state(&eq);
    {
        float buf[1];
        for (i = 0; i < NIMP; i++) {
            buf[0] = 1.0f;
            eq_master_process(&eq, buf, 1);
            printf("STEP %d %.9g\n", i, buf[0]);
        }
    }

    /* ---- limiter test vectors ---- */
    {
        /* Dolph -20dB w8 (dolph_w8_q15.csv, w_float_track1_scipy). [L1] weights */
        const float w8[EQ_NCH] = {
            0.8668296927388105f, 0.5043100646541281f, 0.6216704381816565f,
            0.7333793765883259f, 0.8327331038598036f, 0.9135146112868511f,
            0.9705186581255053f, 1.0f
        };
        eq_limiter_t lim;
        const float T_BASE = 0.8f;     /* PLACEHOLDER [L4] absolute threshold */
        float probes[5];
        int p;
        eq_limiter_init(&lim, T_BASE, w8);
        probes[0] =  1.5f;   /* over +thr  */
        probes[1] = -1.5f;   /* over -thr  */
        probes[2] =  0.1f;   /* under thr  */
        probes[3] =  0.0f;   /* zero       */
        for (ch = 0; ch < EQ_NCH; ch++) {
            for (p = 0; p < 4; p++) {
                float out = eq_limiter_sample(&lim, ch, probes[p]);
                printf("LIM %d %.9g %.9g %.9g\n",
                       ch, lim.t_ch[ch], probes[p], out);
            }
        }
    }

    return 0;
}
