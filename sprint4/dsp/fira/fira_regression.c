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
#include <string.h>
#include <stdint.h>

/* Frozen chirp: SHARE bench_harness's single copy. chirp_input.h declares `static const CHIRP_INPUT`
 * -> every TU including it gets its own 256KB copy. To avoid a 2nd copy (li1040 L1/L2 overflow),
 * reference the one bench_harness already holds for F0 via this accessor (1-line, bench_harness.c).
 * Combined with the streaming rewrite below (working set = one frame, no full 65536 buffers),
 * this drops fira_regression's data footprint by ~768KB. */
extern const int32_t *bench_chirp_input(void);

/* Incremental CRC32 IEEE 802.3 (STREAMING): init *c=0xFFFFFFFF, update per frame, final ^0xFFFFFFFF.
 * Same polynomial/result as bench_harness.c crc32_buf -- fed frame-by-frame so NO full buffer needed. */
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

/* STREAMING: no full 65536 s_y_fira/s_y_core buffers (they overflowed L1/L2, li1040). Working set
 * = one frame (per-frame stack buffers below). Coverage unchanged: full 65536 CRC (incremental) +
 * first per-sample mismatch + 64 spots.
 * F4a mismatch diagnosis globals (emulator reads on FAIL) */
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
    const int32_t *chirp = bench_chirp_input();
    TreeChannelState ca, cs;
    int32_t b0[BENCH_FRAME/8], b1[BENCH_FRAME/4], b2[BENCH_FRAME/2], b3[BENCH_FRAME];
    int32_t yc[BENCH_FRAME];                       /* per-frame core output (no full buffer) */
    uint32_t c = 0xFFFFFFFFu;
    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);
    tfb_channel_init(&ca); tfb_channel_init(&cs);
    for (int f = 0; f < BENCH_NFR; f++) {
        tfb_analyze(&ca, &chirp[f * BENCH_FRAME], BENCH_FRAME, b0, b1, b2, b3);
        tfb_synthesize(&cs, b0, b1, b2, b3, BENCH_FRAME, yc);
        crc32_update(&c, yc, BENCH_FRAME);         /* incremental CRC, frame by frame */
    }
    g_f4_crc_core = c ^ 0xFFFFFFFFu;
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
    const int32_t *chirp = bench_chirp_input();
    /* [L1/EZKIT] bench: first fira_tree_setup() (Open/CreateTask). Desktop returns -1 (disabled). */
    if (fira_tree_setup() != 0) {
        /* Desktop/non-target platform: do not fake verification, return 0 directly. */
        if (out_crc) *out_crc = 0u;
        return 0;
    }

    /* STREAMING lockstep: per frame, run FIRA frame AND core (golden) frame, compare per-sample
     * (first mismatch), accumulate both CRCs incrementally, check spots. No full 65536 buffers. */
    FiraChannelState fa, fs;
    TreeChannelState ca, cs;
    int32_t fb0[BENCH_FRAME/8], fb1[BENCH_FRAME/4], fb2[BENCH_FRAME/2], fb3[BENCH_FRAME];
    int32_t cb0[BENCH_FRAME/8], cb1[BENCH_FRAME/4], cb2[BENCH_FRAME/2], cb3[BENCH_FRAME];
    int32_t yf[BENCH_FRAME], yc[BENCH_FRAME];      /* per-frame FIRA / core outputs */
    uint32_t cf = 0xFFFFFFFFu, cc = 0xFFFFFFFFu;   /* incremental CRC states */
    int spot_match = 1;

    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);    /* core (golden) Q15 coeffs; FIRA coeffs set in setup */
    fira_channel_init(&fa, BENCH_FRAME); fira_channel_init(&fs, BENCH_FRAME);
    tfb_channel_init(&ca); tfb_channel_init(&cs);
    g_f4_mismatch_idx = -1;

    for (int f = 0; f < BENCH_NFR; f++) {
        const int32_t *xin = &chirp[f * BENCH_FRAME];
        fira_tfb_analyze(&fa, xin, BENCH_FRAME, fb0, fb1, fb2, fb3);
        fira_tfb_synthesize(&fs, fb0, fb1, fb2, fb3, BENCH_FRAME, yf);
        tfb_analyze(&ca, xin, BENCH_FRAME, cb0, cb1, cb2, cb3);
        tfb_synthesize(&cs, cb0, cb1, cb2, cb3, BENCH_FRAME, yc);

        for (int i = 0; i < BENCH_FRAME; i++) {
            int gi = f * BENCH_FRAME + i;
            if (g_f4_mismatch_idx < 0 && yf[i] != yc[i]) {     /* first per-sample mismatch */
                g_f4_mismatch_idx = gi; g_f4_core_val = yc[i]; g_f4_fira_val = yf[i];
            }
            if ((gi % GOLDEN_SPOT_STRIDE) == 0) {              /* spot check vs GOLDEN_SPOT[64] */
                int s = gi / GOLDEN_SPOT_STRIDE;
                if (s < GOLDEN_NSPOT && yf[i] != GOLDEN_SPOT[s]) spot_match = 0;
            }
        }
        crc32_update(&cf, yf, BENCH_FRAME);
        crc32_update(&cc, yc, BENCH_FRAME);
    }

    uint32_t crc_fira = cf ^ 0xFFFFFFFFu;
    g_f4_crc_fira = crc_fira;
    g_f4_crc_core = cc ^ 0xFFFFFFFFu;              /* self-check: must == 0x90556BC7 */
    if (out_crc) *out_crc = crc_fira;

    fira_tree_teardown();
    /* PASS iff no per-sample mismatch AND FIRA crc == golden AND spots match. On FAIL, emulator reads
     * g_f4_mismatch_idx / g_f4_core_val / g_f4_fira_val (+ g_f4_crc_core self-check) to drive F4b tuning. */
    int crc_match = (crc_fira == GOLDEN_CRC32) ? 1 : 0;
    return (g_f4_mismatch_idx < 0) && crc_match && spot_match;
}

/* ============================================================
 * cycle plan (plan S5.1 F8): FIRA version cyc_8ch_frame measured with existing CCNT (bench_cyc_target)
 *   -> compare to pure core 1,006,935 -> compute new margin + 16ch deadline.
 * [L1/EZKIT] bench-side; iron rule 8/C9: before R14 (fira_r14_regression==1, on board) passes,
 *   cycle/margin benefit **must not be written into any selection basis** (violation = BLOCKER). This file contains no benefit numbers.
 * ============================================================ */
