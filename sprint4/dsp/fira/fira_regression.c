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
volatile int     g_f4_mismatch_idx  = -1;   /* first per-sample mismatch index within subband; -1 = none */
volatile int     g_f4_mismatch_sb   = -1;   /* which subband (0..3) of first mismatch; -1 = none */
volatile int32_t g_f4_core_val      = 0;    /* core (golden) value at first mismatch */
volatile int32_t g_f4_fira_val      = 0;    /* FIRA path value at first mismatch */
volatile uint32_t g_f4_crc_fira     = 0;    /* FIRA SUBBAND CRC (sb0|sb1|sb2|sb3 concatenated) */
volatile uint32_t g_f4_crc_core     = 0;    /* core SUBBAND CRC = live golden; F4b self-check anchor = 0x2E0D8C6E
                                             *   (computed desktop, sbgold.c). NOT the e2e 0x90556BC7 (that is
                                             *   g_bench_result.crc32, a separate end-to-end check). */
volatile uint32_t g_f4_crc_core_e2e = 0;    /* SEPARATE: end-to-end core CRC written ONLY by fira_harness_selfcheck()
                                             *   (==0x90556BC7); kept distinct so it never clobbers the subband golden. */

/* ---- F4b ratio-diagnostic dump (emulator reads on FAIL) ----
 * idx0 / coarse-band samples are ~0 (filter group delay) and give NO ratio. These capture the first
 * SUBSTANTIAL (|core| >= F4_PROBE_THRESH) core/FIRA pair PER subband, plus 8 consecutive sb3 pairs.
 * sb3 (detail @f0, ~1e6, clean ramp; desktop core[frame0,idx1]=0x0018CB1E) is the cleanest shift probe:
 *   ratio g_f4_probe_fira[3]/g_f4_probe_core[3] reveals the missing >>shift (2^k), the x2 (INT), or a
 *   phase/index offset. Per-band lets us tell a GLOBAL shift error (all 4 off by same 2^k) from a
 *   band-specific one (e.g. only INT/detail bands off by x2). */
#define F4_PROBE_THRESH 256
#define F4_DUMP_N       8
volatile int32_t g_f4_probe_core[4] = {0, 0, 0, 0};   /* first substantial core sample, per subband 0..3 */
volatile int32_t g_f4_probe_fira[4] = {0, 0, 0, 0};   /* paired FIRA value (ratio = shift/x2/phase clue) */
volatile int     g_f4_probe_idx[4]  = {-1, -1, -1, -1};/* flattened sample index of that probe, per subband */
volatile int32_t g_f4_dump_core[F4_DUMP_N];           /* 8 consecutive sb3 core samples from its 1st substantial pt */
volatile int32_t g_f4_dump_fira[F4_DUMP_N];           /* paired FIRA sb3 samples */
volatile int     g_f4_dump_idx0     = -1;             /* flattened sb3 index where the 8-sample dump starts */

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
    g_f4_crc_core_e2e = c ^ 0xFFFFFFFFu;   /* end-to-end (own global; does NOT clobber subband g_f4_crc_core) */
    return (g_f4_crc_core_e2e == GOLDEN_CRC32) ? 1 : 0;
}

/**
 * R14 regression (REDESIGNED 2026-06-03, intermediate-layer): compare FIRA-computed SUBBAND
 * intermediates (sb0..sb3 from fira_tfb_analyze) vs core subbands (tfb_analyze), per-sample, lockstep.
 *
 * WHY NOT end-to-end out: the dyadic tree is perfect-reconstruction -> analyze->synthesize telescopes
 * to out=in ALGEBRAICALLY, independent of filter values (PF-4 Sub-1: "PR ~300dB, independent of coeff
 * precision"). So end-to-end CRC (0x90556BC7 = CRC(in)) verifies telescoping+arithmetic only, NOT the
 * FIR segments -> a placeholder (FIRA segs=0, out=in) passes it = FALSE GREEN (caught 2026-06-03).
 * Subband intermediates sb0..sb3 DO depend on the filter (sb3=in-interp2(decimate2(in)) etc.), so
 * comparing them tests the real FIRA decimate/interp segments. Core subbands are the live golden
 * (numpy-backed: PF-4 Sub-2 xcheck_subband.py independently validated sb0..3).
 *  @param[out] out_crc  CRC32 of FIRA subbands (bench grabs)
 *  @return 1 = R14 single-channel PASS (all FIRA subbands bit-identical to core); 0 = FAIL/mismatch.
 *
 * [L1/EZKIT] must run on board. Desktop: fira_tree_setup()<0 -> returns 0 (no FIRA, no faking).
 * Granularity = subband (sb0..3), the finest core intermediate exposed WITHOUT touching frozen
 * tree_filterbank.c (hb_decimate2/a1 are static/internal there).
 */
int fira_r14_regression(uint32_t *out_crc)
{
    const int32_t *chirp = bench_chirp_input();
    /* [L1/EZKIT] bench: fira_tree_setup() (Open/CreateTask). Desktop returns -1 (disabled, no faking). */
    if (fira_tree_setup() != 0) {
        if (out_crc) *out_crc = 0u;
        return 0;
    }

    /* STREAMING lockstep: per frame, FIRA analyze AND core analyze; compare the 4 SUBBANDS per-sample.
     * No full 65536 buffers; working set = one frame. */
    FiraChannelState fa;
    TreeChannelState ca;
    int32_t fsb0[BENCH_FRAME/8], fsb1[BENCH_FRAME/4], fsb2[BENCH_FRAME/2], fsb3[BENCH_FRAME];
    int32_t csb0[BENCH_FRAME/8], csb1[BENCH_FRAME/4], csb2[BENCH_FRAME/2], csb3[BENCH_FRAME];
    const int sz[4] = { BENCH_FRAME/8, BENCH_FRAME/4, BENCH_FRAME/2, BENCH_FRAME };
    uint32_t cf = 0xFFFFFFFFu, cc = 0xFFFFFFFFu;

    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);    /* core (golden) Q15 coeffs; FIRA coeffs set in setup */
    fira_channel_init(&fa, BENCH_FRAME);
    tfb_channel_init(&ca);
    g_f4_mismatch_idx = -1; g_f4_mismatch_sb = -1;

    for (int f = 0; f < BENCH_NFR; f++) {
        const int32_t *xin = &chirp[f * BENCH_FRAME];
        fira_tfb_analyze(&fa, xin, BENCH_FRAME, fsb0, fsb1, fsb2, fsb3);
        tfb_analyze(&ca, xin, BENCH_FRAME, csb0, csb1, csb2, csb3);
        const int32_t *fb[4] = { fsb0, fsb1, fsb2, fsb3 };
        const int32_t *cb[4] = { csb0, csb1, csb2, csb3 };
        for (int b = 0; b < 4; b++) {
            if (g_f4_mismatch_idx < 0) {
                for (int i = 0; i < sz[b]; i++) {
                    if (fb[b][i] != cb[b][i]) {      /* first FIRA-vs-core subband mismatch */
                        g_f4_mismatch_sb = b; g_f4_mismatch_idx = f * sz[b] + i;
                        g_f4_core_val = cb[b][i]; g_f4_fira_val = fb[b][i];
                        break;
                    }
                }
            }
            /* ratio-diagnostic probe: first substantial core/FIRA pair per subband (skips group-delay ~0
             *   samples that give no ratio). sb3 additionally grabs 8 consecutive pairs (cleanest shift probe). */
            if (g_f4_probe_idx[b] < 0) {
                for (int i = 0; i < sz[b]; i++) {
                    int32_t cv = cb[b][i];
                    int32_t mag = (cv < 0) ? -cv : cv;
                    if (mag >= F4_PROBE_THRESH) {
                        g_f4_probe_idx[b]  = f * sz[b] + i;
                        g_f4_probe_core[b] = cv;
                        g_f4_probe_fira[b] = fb[b][i];
                        if (b == 3 && g_f4_dump_idx0 < 0) {   /* sb3: 8 consecutive for shift confirmation */
                            g_f4_dump_idx0 = f * sz[b] + i;
                            for (int d = 0; d < F4_DUMP_N; d++) {
                                int j = i + d;
                                g_f4_dump_core[d] = (j < sz[b]) ? cb[b][j] : 0;
                                g_f4_dump_fira[d] = (j < sz[b]) ? fb[b][j] : 0;
                            }
                        }
                        break;
                    }
                }
            }
            crc32_update(&cf, fb[b], sz[b]);          /* CRC of FIRA subbands (concatenated) */
            crc32_update(&cc, cb[b], sz[b]);          /* CRC of core subbands (live golden) */
        }
    }

    g_f4_crc_fira = cf ^ 0xFFFFFFFFu;
    g_f4_crc_core = cc ^ 0xFFFFFFFFu;                 /* core-subband golden (numpy-backed PF-4 Sub-2) */
    if (out_crc) *out_crc = g_f4_crc_fira;

    fira_tree_teardown();
    /* PASS = FIRA subbands bit-identical to core (filter-segment-level, NOT telescoping). On FAIL,
     * emulator reads g_f4_mismatch_sb (which subband) / g_f4_mismatch_idx / g_f4_core_val / g_f4_fira_val
     * -> drives postscale tuning (F4b). NOTE: a placeholder FIRA (segs=0) FAILS here (sb0..2!=core),
     * unlike the old end-to-end test it could fool. */
    return (g_f4_mismatch_idx < 0) && (g_f4_crc_fira == g_f4_crc_core);
}

/* ============================================================
 * cycle plan (plan S5.1 F8): FIRA version cyc_8ch_frame measured with existing CCNT (bench_cyc_target)
 *   -> compare to pure core 1,006,935 -> compute new margin + 16ch deadline.
 * [L1/EZKIT] bench-side; iron rule 8/C9: before R14 (fira_r14_regression==1, on board) passes,
 *   cycle/margin benefit **must not be written into any selection basis** (violation = BLOCKER). This file contains no benefit numbers.
 * ============================================================ */
