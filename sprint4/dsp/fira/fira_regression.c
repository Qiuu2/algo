/**
 * @file    fira_regression.c
 * @brief   [DRAFT, uncompiled, real Legacy API, bench-side] F7 R14 regression harness: FIRA path output
 *          -> CRC32 + spot vs core-only golden (0x90556BC7). Reuses bench/golden_ref.h same baseline.
 *
 * +-----------------------------------------------------------------------+
 * | HONESTY STATUS: no FIRA hardware on this host -> this file **cannot   |
 * |  produce valid FIRA output**.                                         |
 * |  It defines "how to compare on bench" -- feeds fira_tfb_analyze/      |
 * |  synthesize output into the exact same CRC32 + GOLDEN_SPOT comparison |
 * |  as bench_harness.c. Two-valued criterion:                           |
 * |  crc==0x90556BC7 and all 64 spots equal -> R14 PASS (FIRA version     |
 * |  numerically equivalent to core version).                            |
 * |  Cannot produce real values on desktop; R14 [L1] backfilled on board |
 * |  by bench (plan S5.3 step6).                                          |
 * +-----------------------------------------------------------------------+
 *
 * Hookup (FIRA_IMPL.md S4 + task point 2): FIRA version **replaces bench_harness convolution segment** --
 *   i.e. swap tfb_analyze/tfb_synthesize for fira_tfb_analyze/fira_tfb_synthesize,
 *   output still goes through the same crc32_buf + GOLDEN_CRC32/GOLDEN_SPOT comparison. The rest (frozen chirp input,
 *   sat/unsat dual build) fully reuses bench_harness.c, do not change golden (else loses reference baseline).
 *
 * Bench prerequisite: F2 first runs fira_single_channel_template() (single-segment full Legacy lifecycle +
 *   Path B runtime FixedPointEnable(SIGNED)) and passes, then extends to this full-chain regression (F4->F7).
 *
 * Desktop build safety: fira_tree_setup()/fira_single_channel_template() return -1 on desktop,
 *   this function accordingly **returns 0 directly** (FAIL, hints "not bench, result invalid"), **never fakes** R14 pass.
 *
 * F4 PREP / BUILD STATUS: this translation unit is **Exclude from Build by default** in the CCES bench
 *   project. It cannot compile without the real Legacy header (FIRA_USE_REAL_ADI_FIR_HEADER) + the
 *   core_only/bench include path. F4 step: clear "Exclude from Build" on this file (and on the FIRA
 *   group) once the EZKIT BSP header is wired, then run fira_r14_regression() on board and compare
 *   crc == GOLDEN_CRC32 (0x90556BC7) from golden_ref.h. Until then it is inert reference plumbing.
 */

#include "fira_tree.h"
#include "fir_coeffs_hb63.h" /* g_hb63_q15: core (Q15) coeffs for the parallel core golden run (F4a diag) */
/* Bench CCES project must set -I.../sprint4/dsp/core_only/bench AND -I.../core_only/include
 *    (headers below live in core_only/bench/ + core_only/include/, bare names resolved via -I) */
#include "golden_ref.h"     /* reuse core-only golden (0x90556BC7), do not change */
#include "bench_harness.h"  /* BENCH_FRAME/NFR/FS same convention */
#include "chirp_input.h"    /* frozen chirp input (same R14 input, S5.3 step2) */
#include <string.h>
#include <stdint.h>

/* CRC32 IEEE 802.3 -- bit-identical algorithm to bench_harness.c:30 / gen_golden.c (do not change) */
static uint32_t crc32_buf(const int32_t *d, int n)
{
    uint32_t c = 0xFFFFFFFFu;
    for (int i = 0; i < n; i++) {
        uint32_t v = (uint32_t)d[i];
        for (int b = 0; b < 4; b++) {
            uint8_t by = (uint8_t)(v >> (8 * b));
            c ^= by;
            for (int k = 0; k < 8; k++) c = (c & 1) ? (c >> 1) ^ 0xEDB88320u : (c >> 1);
        }
    }
    return c ^ 0xFFFFFFFFu;
}

static int32_t s_y_fira[BENCH_FRAME * BENCH_NFR];
static int32_t s_y_core[BENCH_FRAME * BENCH_NFR];   /* parallel core single-channel golden (F4a diag) */

/* F4a mismatch diagnosis globals (emulator reads on FAIL) */
volatile int     g_f4_mismatch_idx  = -1;   /* first per-sample mismatch index; -1 = none */
volatile int32_t g_f4_core_val      = 0;    /* core (golden) value at first mismatch */
volatile int32_t g_f4_fira_val      = 0;    /* FIRA path value at first mismatch */
volatile uint32_t g_f4_crc_fira     = 0;    /* FIRA chain CRC */
volatile uint32_t g_f4_crc_core     = 0;    /* core chain CRC (self-check: must == 0x90556BC7) */

/* F4a harness self-check (DESKTOP-runnable, no FIRA): run the core single-channel chain over the
 * frozen chirp and confirm it reproduces GOLDEN_CRC32. Verifies the comparison infra + golden anchor
 * are intact (granularity = single-channel full chain, evidence DOC: 0x90556BC7 is single-channel,
 * gen_golden.c:71-75). Returns 1 if crc_core == GOLDEN_CRC32. */
int fira_harness_selfcheck(void)
{
    TreeChannelState ca, cs;
    int32_t b0[BENCH_FRAME/8], b1[BENCH_FRAME/4], b2[BENCH_FRAME/2], b3[BENCH_FRAME];
    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);
    tfb_channel_init(&ca); tfb_channel_init(&cs);
    for (int f = 0; f < BENCH_NFR; f++) {
        tfb_analyze(&ca, &CHIRP_INPUT[f * BENCH_FRAME], BENCH_FRAME, b0, b1, b2, b3);
        tfb_synthesize(&cs, b0, b1, b2, b3, BENCH_FRAME, &s_y_core[f * BENCH_FRAME]);
    }
    g_f4_crc_core = crc32_buf(s_y_core, BENCH_FRAME * BENCH_NFR);
    return (g_f4_crc_core == GOLDEN_CRC32) ? 1 : 0;
}

/**
 * F7 regression: single-channel FIRA chain 65536 samples -> CRC32 + spot vs golden.
 *  @param[out] out_crc  FIRA version CRC32 (bench grabs)
 *  @return 1 = R14 PASS (crc==0x90556BC7 and all 64 spots equal); 0 = FAIL (locate plan S4)
 *
 * [L1/EZKIT] must run on board (incl. real FIRA DMA / 80-bit MR / phase / cache).
 *   No FIRA on desktop -> fira_tfb_* is placeholder in draft build (no FIRA segment connected) -> so this function's
 *   **desktop call result is meaningless**, only plumbing. Do not treat desktop result as R14 pass.
 */
int fira_r14_regression(uint32_t *out_crc)
{
    FiraChannelState ana, syn;
    int32_t sb0[BENCH_FRAME/8], sb1[BENCH_FRAME/4], sb2[BENCH_FRAME/2], sb3[BENCH_FRAME];

    /* [L1/EZKIT] bench: first fira_tree_setup() (Open/CreateTask). Desktop returns -1 (disabled). */
    if (fira_tree_setup() != 0) {
        /* Desktop/non-target platform: do not fake verification, return 0 directly (FAIL -> hints "not bench, result invalid"). */
        if (out_crc) *out_crc = 0u;
        return 0;
    }

    fira_channel_init(&ana, BENCH_FRAME);
    fira_channel_init(&syn, BENCH_FRAME);

    for (int f = 0; f < BENCH_NFR; f++) {
        fira_tfb_analyze(&ana, &CHIRP_INPUT[f * BENCH_FRAME], BENCH_FRAME,
                         sb0, sb1, sb2, sb3);
        fira_tfb_synthesize(&syn, sb0, sb1, sb2, sb3, BENCH_FRAME,
                            &s_y_fira[f * BENCH_FRAME]);
    }

    uint32_t crc = crc32_buf(s_y_fira, BENCH_FRAME * BENCH_NFR);
    if (out_crc) *out_crc = crc;
    g_f4_crc_fira = crc;

    /* F4a diagnosis: run the parallel core single-channel chain (golden) and find the FIRST
     * per-sample mismatch (index + core value + fira value) -> tells which stage/segment diverges.
     * fira_harness_selfcheck() fills s_y_core + g_f4_crc_core (self-check: g_f4_crc_core==0x90556BC7). */
    (void)fira_harness_selfcheck();   /* fills s_y_core (Q15 core coeffs), restores core path */
    g_f4_mismatch_idx = -1;
    for (int i = 0; i < BENCH_FRAME * BENCH_NFR; i++) {
        if (s_y_fira[i] != s_y_core[i]) {
            g_f4_mismatch_idx = i; g_f4_core_val = s_y_core[i]; g_f4_fira_val = s_y_fira[i];
            break;
        }
    }

    int crc_match = (crc == GOLDEN_CRC32) ? 1 : 0;
    int spot_match = 1;
    for (int i = 0; i < GOLDEN_NSPOT; i++) {
        if (s_y_fira[i * GOLDEN_SPOT_STRIDE] != GOLDEN_SPOT[i]) { spot_match = 0; break; }
    }

    fira_tree_teardown();
    /* PASS iff no per-sample mismatch (g_f4_mismatch_idx<0) AND crc/spot match. On FAIL, emulator
     * reads g_f4_mismatch_idx / g_f4_core_val / g_f4_fira_val to drive postscale tuning (F4b). */
    return (g_f4_mismatch_idx < 0) && crc_match && spot_match;
}

/* ============================================================
 * cycle plan (plan S5.1 F8): FIRA version cyc_8ch_frame measured with existing CCNT (bench_cyc_target)
 *   -> compare to pure core 1,006,935 -> compute new margin + 16ch deadline.
 * [L1/EZKIT] bench-side; iron rule 8/C9: before R14 (fira_r14_regression==1, on board) passes,
 *   cycle/margin benefit **must not be written into any selection basis** (violation = BLOCKER). This file contains no benefit numbers.
 * ============================================================ */
