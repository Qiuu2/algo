/**
 * @file    gen_f5_goldens.c
 * @brief   F5-A desktop generator: 8 per-channel core-subband golden CRCs over the frozen
 *          chirp scaled by each channel's Dolph-Chebyshev weight (input-scale).
 *
 * Plan: sprint4/dsp/fira/F5_F7_PLAN.md section 1.3 (extends the F4 sbgold method to 8 channels).
 *
 * WHAT THIS PRODUCES
 *   For each channel c = 0..7:
 *     1. take the SAME frozen chirp (chirp_input.h, identical pre-weight for every channel),
 *     2. apply the channel weight at INPUT-SCALE, bit-exactly the same arithmetic the on-board
 *        F5-A path uses:  x_weighted_q31 = (int32_t)(((int64_t)w_q15[c] * x_q31) >> 15),
 *     3. run the VERBATIM core subband chain (tree_filterbank.c tfb_analyze) over the weighted
 *        chirp, frame by frame (BENCH_FRAME=64, BENCH_NFR=1024),
 *     4. fold the 4 subbands (sb0|sb1|sb2|sb3, in that order, every frame) into one CRC32 (IEEE
 *        802.3, init 0xFFFFFFFF, final ^0xFFFFFFFF) -- the EXACT same streaming CRC the board
 *        harness (fira_regression.c crc32_update) computes.
 *   The 8 CRCs are the frozen goldens g_f5_golden_crc[8].
 *
 * BIT-EXACT BOUNDARY (plan 1.2, section 12 FG1): the weight is INSIDE the bit-exact boundary.
 *   The golden = core subband CRC over chirp*w[c].  The board criterion is "FIRA subband ==
 *   core subband, both over chirp*w[c]" -- apples-to-apples, weight included on BOTH sides.
 *
 * FG1 (no false-green): because each channel uses a DISTINCT weight, the 8 goldens MUST be
 *   pairwise distinct.  This generator ASSERTS pairwise-distinct (DISTINCT-CHECK below) and
 *   exits non-zero if any two collide -> degenerate / unweighted table caught at generation.
 *
 * FG1 double-guard (plan 1.3 / AC-A2): build with -DF5_GEN_UNWEIGHTED to force w=1.0 on every
 *   channel; that MUST collapse all 8 CRCs to one value and the DISTINCT-CHECK MUST FAIL
 *   (demonstrates the check actually depends on the weight differentiating channels).
 *
 * Build (desktop host gcc, NOT the SHARC target):
 *   gcc -std=c99 -I../core_only/src -I../core_only/bench -I../core_only/include \
 *       gen_f5_goldens.c ../core_only/src/tree_filterbank.c -o /tmp/gen_f5_goldens
 *   (TFB_DISABLE_SAT not defined: weighting only ATTENUATES (w<=1.0), so the 0.289 chirp
 *    stays in the non-saturating regime same as F0/F4; saturation primitives are inert here,
 *    bit-exact to the board which also runs them inert under this excitation.)
 *
 * Output: the frozen header block (paste into / regenerate dolph_f5_goldens.h) + a distinctness
 *   report.  Same-source discipline: values are frozen in the header, NOT recomputed on board;
 *   on board g_f5_crc_core[c] is recomputed live and compared to the frozen golden as a self-check.
 *
 * ASCII-only.
 */
#include "tree_filterbank.h"
#include "fir_coeffs_hb63.h"   /* g_hb63_q15 / FIR_HB63_NTAPS */
#include "bench_harness.h"     /* BENCH_FRAME / BENCH_NFR */
#include "chirp_input.h"       /* CHIRP_INPUT[CHIRP_INPUT_N] (own copy fine on desktop) */
#include "dolph_w8_q15.h"      /* g_dolph_w8_q15[8] / DOLPH_W8_NCH / DOLPH_W8_QBITS */
#include <stdio.h>
#include <stdint.h>

/* Same incremental CRC32 (IEEE 802.3) as fira_regression.c crc32_update -- byte order identical. */
static void crc32_update(uint32_t *c, const int32_t *d, int n)
{
    for (int i = 0; i < n; i++) {
        uint32_t v = (uint32_t)d[i];
        for (int b = 0; b < 4; b++) {
            uint8_t by = (uint8_t)(v >> (8 * b));
            *c ^= by;
            for (int k = 0; k < 8; k++) *c = (*c & 1) ? (*c >> 1) ^ 0xEDB88320u : (*c >> 1);
        }
    }
}

/* Input-scale weight application -- BIT-EXACT to the on-board F5-A path (plan 1.2 / dolph_w8_q15.h). */
static int32_t apply_w(int32_t w_q15, int32_t x_q31)
{
    return (int32_t)(((int64_t)w_q15 * (int64_t)x_q31) >> DOLPH_W8_QBITS);
}

int main(void)
{
    uint32_t golden[DOLPH_W8_NCH];

    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);

    for (int c = 0; c < DOLPH_W8_NCH; c++) {
#ifdef F5_GEN_UNWEIGHTED
        int32_t w = DOLPH_W8_ONE;   /* FG1 negative control: unity on every channel -> all CRCs collapse */
#else
        int32_t w = g_dolph_w8_q15[c];
#endif
        TreeChannelState ca;
        int32_t sb0[BENCH_FRAME/8], sb1[BENCH_FRAME/4], sb2[BENCH_FRAME/2], sb3[BENCH_FRAME];
        int32_t xw[BENCH_FRAME];
        const int sz[4] = { BENCH_FRAME/8, BENCH_FRAME/4, BENCH_FRAME/2, BENCH_FRAME };
        uint32_t crc = 0xFFFFFFFFu;

        tfb_channel_init(&ca);
        for (int f = 0; f < BENCH_NFR; f++) {
            const int32_t *xin = &CHIRP_INPUT[f * BENCH_FRAME];
            for (int i = 0; i < BENCH_FRAME; i++) xw[i] = apply_w(w, xin[i]);  /* input-scale weight */
            tfb_analyze(&ca, xw, BENCH_FRAME, sb0, sb1, sb2, sb3);
            const int32_t *sb[4] = { sb0, sb1, sb2, sb3 };
            for (int b = 0; b < 4; b++) crc32_update(&crc, sb[b], sz[b]);       /* sb0|sb1|sb2|sb3 order */
        }
        golden[c] = crc ^ 0xFFFFFFFFu;
    }

    /* ---- emit the frozen header body ---- */
    printf("/* g_f5_golden_crc[8] -- generated by gen_f5_goldens.c (paste into dolph_f5_goldens.h) */\n");
    printf("static const uint32_t g_f5_golden_crc[DOLPH_W8_NCH] = {\n");
    for (int c = 0; c < DOLPH_W8_NCH; c++) {
        printf("    0x%08Xu,   /* c=%d  w_q15=%6d */\n",
               golden[c], c,
#ifdef F5_GEN_UNWEIGHTED
               DOLPH_W8_ONE
#else
               g_dolph_w8_q15[c]
#endif
        );
    }
    printf("};\n\n");

    /* ---- FG1 DISTINCT-CHECK (pairwise) ---- */
    int collisions = 0;
    for (int a = 0; a < DOLPH_W8_NCH; a++)
        for (int b = a + 1; b < DOLPH_W8_NCH; b++)
            if (golden[a] == golden[b]) {
                printf("FG1 COLLISION: golden[%d] == golden[%d] == 0x%08X\n", a, b, golden[a]);
                collisions++;
            }

    if (collisions == 0) {
        printf("FG1 PASS: all 8 per-channel goldens pairwise DISTINCT (weight differentiates channels).\n");
#ifdef F5_GEN_UNWEIGHTED
        printf("UNEXPECTED: unweighted build produced distinct goldens -- weight path is wrong.\n");
        return 2;   /* unweighted MUST collide */
#endif
        return 0;
    } else {
        printf("FG1 FAIL: %d collision(s) -> weight does NOT differentiate all channels (false-green risk).\n",
               collisions);
#ifdef F5_GEN_UNWEIGHTED
        printf("EXPECTED (unweighted control): collisions confirm the DISTINCT-CHECK depends on the weight.\n");
        return 0;   /* for the negative control, collisions are the expected/correct outcome */
#endif
        return 1;
    }
}
