/**
 * @file    fira_regression.c
 * @brief   [DRAFT, uncompiled, real Legacy API, bench-side] FIRA subband bit-exact regression harness.
 *          F4 single-channel + F5-A 8-channel; per-channel FIRA-vs-core SUBBAND CRC compare.
 *
 * +-----------------------------------------------------------------------+
 * | CRITERION (R14 / DEC-S4-R14-GRANULARITY -- SUBBAND-GRANULARITY)        |
 * |  The verdict is PER-SUBBAND, NOT a single end-to-end constant.         |
 * |   - F4 single-channel: FIRA sb0..3 == core sb0..3 bit-for-bit          |
 * |     (live core-subband golden self-check anchor 0x2E0D8C6E).           |
 * |   - F5-A 8-channel: for EACH channel c, FIRA sb0..3 == core sb0..3     |
 * |     over the SAME weighted input chirp*w[c]; board CRC g_f5_crc_fira[c] |
 * |     compared to the frozen per-channel golden g_f5_golden_crc[c]       |
 * |     (dolph_f5_goldens.h; 8 DISTINCT goldens, weight inside the         |
 * |     bit-exact boundary).                                               |
 * |                                                                       |
 * | WHY NOT end-to-end out / the retired 0x90556BC7 e2e criterion:         |
 * |  the dyadic tree is perfect-reconstruction -> analyze->synthesize      |
 * |  telescopes to out=in ALGEBRAICALLY, independent of filter values.     |
 * |  So an end-to-end CRC (0x90556BC7 == CRC(in)) verifies telescoping +   |
 * |  arithmetic only, NOT the FIR segments -> a placeholder (segs=0,       |
 * |  out=in) PASSES it = FALSE GREEN (caught 2026-06-03). The e2e          |
 * |  constant 0x90556BC7 is therefore a RETIRED pass criterion; it now     |
 * |  survives ONLY as the separate end-to-end self-check                   |
 * |  fira_harness_selfcheck() (infra sanity, not the FIRA verdict).        |
 * |  Subband intermediates DO depend on the filter, so comparing them      |
 * |  tests the real FIRA decimate/interp segments (and, in F5-A, that the  |
 * |  per-channel weight was applied bit-exactly on BOTH FIRA and core      |
 * |  sides). Core subbands are the live golden (numpy-backed, PF-4 Sub-2). |
 * +-----------------------------------------------------------------------+
 *
 * +-----------------------------------------------------------------------+
 * | HONESTY STATUS: no FIRA hardware on this host -> this file **cannot   |
 * |  produce valid FIRA output**. It defines "how to compare on bench".   |
 * |  Desktop build safety: fira_tree_setup() returns <0 on desktop, so    |
 * |  fira_r14_regression()/fira_r14_regression_8ch() **return 0 / leave   |
 * |  every g_f5_pass[c]=0** (FAIL honestly), **never fake** a pass (FG2).  |
 * +-----------------------------------------------------------------------+
 *
 * Hookup (FIRA_IMPL.md S4): the FIRA version **replaces the convolution segment** -- swap
 *   tfb_analyze for fira_tfb_analyze, output goes through the same per-subband CRC compare.
 *   Frozen chirp / weights / goldens reused, do NOT change them (else lose the reference baseline).
 *
 * F4/F5 PREP / BUILD STATUS: this translation unit is **Exclude from Build by default** in the CCES
 *   bench project. It cannot compile without the real Legacy header (FIRA_USE_REAL_ADI_FIR_HEADER) +
 *   the core_only/bench include path. Step: clear "Exclude from Build" once the EZKIT BSP header is
 *   wired, then run fira_r14_regression_8ch() on board and compare per channel
 *   g_f5_crc_fira[c] == g_f5_crc_core[c] == g_f5_golden_crc[c] (dolph_f5_goldens.h). Until then inert.
 */

#include "fira_tree.h"
#include "fir_coeffs_hb63.h" /* g_hb63_q15: core (Q15) coeffs for the parallel core golden run */
/* Bench CCES project must set -I.../sprint4/dsp/core_only/bench AND -I.../core_only/include
 *    (headers below live in core_only/bench/ + core_only/include/, bare names resolved via -I) */
#include "golden_ref.h"     /* GOLDEN_CRC32 (0x90556BC7) used ONLY by fira_harness_selfcheck (e2e infra check) */
#include "bench_harness.h"  /* BENCH_FRAME/NFR/FS same convention */
#include "dolph_w8_q15.h"   /* F5-C frozen per-channel Dolph weights g_dolph_w8_q15[8] (input-scale) */
#include "dolph_f5_goldens.h" /* F5-A frozen 8 per-channel core-subband goldens g_f5_golden_crc[8] */
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
                                             *   (==0x90556BC7, RETIRED pass criterion -> infra self-check only);
                                             *   kept distinct so it never clobbers the subband golden. */

/* ---- F4b ratio-diagnostic dump (emulator reads on FAIL) ----
 * idx0 / coarse-band samples are ~0 (filter group delay) and give NO ratio. These capture the first
 * SUBSTANTIAL (|core| >= F4_PROBE_THRESH) core/FIRA pair PER subband, plus 8 consecutive sb3 pairs.
 * sb3 (detail @f0, ~1e6, clean ramp; desktop core[frame0,idx1]=0x0018CB1E) is the cleanest shift probe:
 *   ratio g_f4_probe_fira[3]/g_f4_probe_core[3] reveals the missing >>shift (2^k), the x2 (INT), or a
 *   phase/index offset. Per-band lets us tell a GLOBAL shift error (all 4 off by same 2^k) from a
 *   band-specific one (e.g. only INT/detail bands off by x2). */
#define F4_PROBE_THRESH 256
#define F4_DUMP_N       32   /* bumped 8->32 (2026-06-04, DEC-PHASE FIX): wider sb3 window so the next
                              * board run sharply confirms the fix -- residual all-zero if fixed, or the
                              * predicted even-phase explosion 0,-10,0,+22,-40,+72,... if still even-phase.
                              * (j<sz[b]) guard below keeps it safe past the subband end. */
volatile int32_t g_f4_probe_core[4] = {0, 0, 0, 0};   /* first substantial core sample, per subband 0..3 */
volatile int32_t g_f4_probe_fira[4] = {0, 0, 0, 0};   /* paired FIRA value (ratio = shift/x2/phase clue) */
volatile int     g_f4_probe_idx[4]  = {-1, -1, -1, -1};/* flattened sample index of that probe, per subband */
volatile int32_t g_f4_dump_core[F4_DUMP_N];           /* 8 consecutive sb3 core samples from its 1st substantial pt */
volatile int32_t g_f4_dump_fira[F4_DUMP_N];           /* paired FIRA sb3 samples */
volatile int     g_f4_dump_idx0     = -1;             /* flattened sb3 index where the 8-sample dump starts */

/* ============================================================
 * F5-A 8-channel per-channel readout globals (emulator reads). NO aggregate-bool masking:
 *   every channel has its OWN pass/crc/mismatch so a failure is localizable to channel + subband + index
 *   (plan 1.4 / section 12 IO1/IO2). g_f5_pass_all = AND over channels, but ONLY a convenience -- the
 *   per-channel arrays are the source of truth for diagnosis.
 * ============================================================ */
volatile int      g_f5_pass[DOLPH_W8_NCH];          /* per channel: 1=PASS / 0=FAIL or not-run */
volatile uint32_t g_f5_crc_fira[DOLPH_W8_NCH];      /* per channel: FIRA subband CRC (compare vs golden) */
volatile uint32_t g_f5_crc_core[DOLPH_W8_NCH];      /* per channel: live core subband CRC (self-check vs g_f5_golden_crc[c]) */
volatile int      g_f5_mismatch_sb[DOLPH_W8_NCH];   /* per channel: first-mismatch subband 0..3 (-1 none) */
volatile int      g_f5_mismatch_idx[DOLPH_W8_NCH];  /* per channel: first-mismatch flattened index (-1 none) */
volatile int32_t  g_f5_mismatch_core[DOLPH_W8_NCH]; /* per channel: core value at first mismatch */
volatile int32_t  g_f5_mismatch_fira[DOLPH_W8_NCH]; /* per channel: FIRA value at first mismatch */
volatile int      g_f5_pass_all = -99;              /* convenience AND over all channels (-99 = not run) */
volatile int      g_f5_fail_chan = -1;              /* first failing channel index (-1 = none); selects the dump below */
/* 32-sample sb3 dump for the FIRST FAILING channel (plan 1.4): on FAIL the emulator reads these to see
 * the exact divergence (same sharp-falsifier scheme as g_f4_dump_*). Populated only when a failing
 * channel exists; left -1/zero when all channels pass. */
volatile int32_t  g_f5_dump_core[F4_DUMP_N];        /* first-failing-channel sb3 core samples */
volatile int32_t  g_f5_dump_fira[F4_DUMP_N];        /* paired FIRA samples */
volatile int      g_f5_dump_idx0 = -1;              /* sb3 flattened index where the dump starts (-1 none) */

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

/* input-scale per-channel weight (plan 1.2). BIT-EXACT to gen_f5_goldens.c apply_w and to dolph_w8_q15.h:
 *   x_weighted_q31 = (int32_t)(((int64_t)w_q15 * x_q31) >> 15). Same Q15xQ31>>15 truncation as the chain. */
static int32_t f5_apply_w(int32_t w_q15, int32_t x_q31)
{
    return (int32_t)(((int64_t)w_q15 * (int64_t)x_q31) >> DOLPH_W8_QBITS);
}

/**
 * F5-A 8-channel subband bit-exact regression (plan section 1). The 8 broadside channels are SAME-
 * topology, fully INDEPENDENT instances of the F4-verified single-channel FIRA chain; the ONLY
 * difference between channels is the input-scale Dolph weight w[c] (dolph_w8_q15.h). For each channel
 * c = 0..7, run the FIRA analyze AND the core analyze over the SAME weighted input chirp*w[c], and
 * compare the 4 subbands per-sample, lockstep. The weight is INSIDE the bit-exact boundary: it is
 * applied identically (same f5_apply_w) on both the FIRA and the core side, so the comparison stays
 * apples-to-apples (plan 1.2, section 12 FG1). On board g_f5_crc_core[c] is the live core golden and
 * MUST equal the frozen g_f5_golden_crc[c] (self-check); g_f5_crc_fira[c] MUST also equal it (verdict).
 *
 * SERIAL DISCIPLINE [ASSUME-A1] (plan 1.3 -- PRE-CONDITION, recorded verbatim):
 *   8ch x 9seg = 72 QueueTask all run on the SINGLE shared FIRA handle s_hFir; the 4 shared statics
 *   (s_seg_in / s_seg_out3 / s_taskMem / s_hFir) are reused under a STRICT SINGLE-THREADED SERIAL
 *   discipline. This function calls fira_tfb_analyze for one channel, fully drains it (reads its
 *   subbands, compares, advances the next FRAME for that channel) before touching the next channel --
 *   there is NEVER concurrent use of the shared statics, so no overwrite window exists. A FiraChannelState
 *   is allocated PER channel (fa[8]) so each channel keeps its OWN cross-frame history (ST1); only the
 *   FIRA-device-level scratch is shared, and only serially. If task grouping / concurrency is ever
 *   introduced this [ASSUME-A1] breaks and per-task scratch is required (F4 handoff section 6 open item).
 *   Board closes [ASSUME-A1] en bloc via "all 8 channels bit-exact".
 *
 * Channel-major loop order (NOT frame-major across channels): for each channel we run all NFR frames
 *   to completion, then move to the next channel. This keeps each channel's 9-segment chain + cross-frame
 *   history strictly serial on the shared handle and matches the per-channel independent topology.
 *
 *  @return 1 = all 8 channels PASS; 0 = at least one FAIL / desktop no-FIRA. Per-channel localizable
 *          via g_f5_pass[]/g_f5_mismatch_*[]/g_f5_dump_* (NO aggregate-only masking).
 * [L1/EZKIT] must run on board. Desktop: fira_tree_setup()<0 -> all g_f5_pass[c]=0, return 0 (FG2 honest FAIL).
 */
int fira_r14_regression_8ch(void)
{
    const int32_t *chirp = bench_chirp_input();
    const int sz[4] = { BENCH_FRAME/8, BENCH_FRAME/4, BENCH_FRAME/2, BENCH_FRAME };

    /* init per-channel readout to FAIL/none (desktop-safe defaults; never fake a pass) */
    for (int c = 0; c < DOLPH_W8_NCH; c++) {
        g_f5_pass[c] = 0; g_f5_crc_fira[c] = 0u; g_f5_crc_core[c] = 0u;
        g_f5_mismatch_sb[c] = -1; g_f5_mismatch_idx[c] = -1;
        g_f5_mismatch_core[c] = 0; g_f5_mismatch_fira[c] = 0;
    }
    g_f5_fail_chan = -1; g_f5_dump_idx0 = -1;
    for (int d = 0; d < F4_DUMP_N; d++) { g_f5_dump_core[d] = 0; g_f5_dump_fira[d] = 0; }

    /* [L1/EZKIT] bench: fira_tree_setup() (Open/CreateTask). Desktop returns -1 -> honest FAIL (FG2). */
    if (fira_tree_setup() != 0) {
        g_f5_pass_all = 0;
        return 0;
    }

    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);   /* core (golden) Q15 coeffs; FIRA coeffs set in setup */

    /* Per-channel state arrays. fa[c] = independent FIRA channel (own cross-frame history, ST1).
     * Channel-major: drain all frames of channel c before channel c+1 (serial on shared s_hFir).
     * STATIC (not stack): 8 x FiraChannelState + 8 x TreeChannelState ~= 37 KB; static placement
     *   matches the codebase's static-allocation discipline (s_seg_in etc.) and avoids a ~37 KB
     *   stack frame on the SHARC bench. fira_channel_init/tfb_channel_init re-zero them each run, so
     *   static carries no stale cross-run state (each fira_r14_regression_8ch call re-inits all 8). */
    static FiraChannelState fa[DOLPH_W8_NCH];
    static TreeChannelState ca[DOLPH_W8_NCH];
    int32_t fsb0[BENCH_FRAME/8], fsb1[BENCH_FRAME/4], fsb2[BENCH_FRAME/2], fsb3[BENCH_FRAME];
    int32_t csb0[BENCH_FRAME/8], csb1[BENCH_FRAME/4], csb2[BENCH_FRAME/2], csb3[BENCH_FRAME];
    int32_t xw[BENCH_FRAME];   /* per-frame weighted input (input-scale) */

    for (int c = 0; c < DOLPH_W8_NCH; c++) {
        const int32_t w = g_dolph_w8_q15[c];
        uint32_t cf = 0xFFFFFFFFu, cc = 0xFFFFFFFFu;
        int local_mis_idx = -1;

        fira_channel_init(&fa[c], BENCH_FRAME);
        tfb_channel_init(&ca[c]);

        for (int f = 0; f < BENCH_NFR; f++) {
            const int32_t *xin = &chirp[f * BENCH_FRAME];
            /* input-scale weight BEFORE analyze, identical on FIRA and core side (apples-to-apples). */
            for (int i = 0; i < BENCH_FRAME; i++) xw[i] = f5_apply_w(w, xin[i]);

            fira_tfb_analyze(&fa[c], xw, BENCH_FRAME, fsb0, fsb1, fsb2, fsb3);
            tfb_analyze(&ca[c], xw, BENCH_FRAME, csb0, csb1, csb2, csb3);

            const int32_t *fb[4] = { fsb0, fsb1, fsb2, fsb3 };
            const int32_t *cb[4] = { csb0, csb1, csb2, csb3 };
            for (int b = 0; b < 4; b++) {
                if (local_mis_idx < 0) {
                    for (int i = 0; i < sz[b]; i++) {
                        if (fb[b][i] != cb[b][i]) {
                            g_f5_mismatch_sb[c]  = b;
                            g_f5_mismatch_idx[c] = f * sz[b] + i;
                            g_f5_mismatch_core[c] = cb[b][i];
                            g_f5_mismatch_fira[c] = fb[b][i];
                            local_mis_idx = g_f5_mismatch_idx[c];
                            break;
                        }
                    }
                }
                crc32_update(&cf, fb[b], sz[b]);   /* FIRA subband CRC */
                crc32_update(&cc, cb[b], sz[b]);   /* core subband CRC (live golden) */
            }
        }

        g_f5_crc_fira[c] = cf ^ 0xFFFFFFFFu;
        g_f5_crc_core[c] = cc ^ 0xFFFFFFFFu;
        /* PASS = no per-sample mismatch AND FIRA CRC == live core CRC AND live core == frozen golden
         *   (the frozen-golden term is the self-check: if the live core diverges from the desktop golden,
         *    the core path/chirp/weight drifted on board -> diagnosis invalid, treat as FAIL). */
        g_f5_pass[c] = (g_f5_mismatch_idx[c] < 0)
                    && (g_f5_crc_fira[c] == g_f5_crc_core[c])
                    && (g_f5_crc_core[c] == g_f5_golden_crc[c]) ? 1 : 0;
    }

    fira_tree_teardown();

    /* Aggregate AND + locate first failing channel; capture its sb3 32-dump for the sharp falsifier.
     * The per-channel arrays above are the source of truth; this is only a convenience + dump selector. */
    int all = 1;
    for (int c = 0; c < DOLPH_W8_NCH; c++) {
        if (!g_f5_pass[c]) {
            all = 0;
            if (g_f5_fail_chan < 0) g_f5_fail_chan = c;   /* first failing channel */
        }
    }
    if (g_f5_fail_chan >= 0) {
        /* Re-run ONLY the failing channel's sb3 to dump 32 consecutive samples from its first substantial
         * point (group-delay ~0 samples give no signal). Serial, after teardown's matching setup re-open. */
        if (fira_tree_setup() == 0) {
            int c = g_f5_fail_chan;
            const int32_t w = g_dolph_w8_q15[c];
            FiraChannelState fad; TreeChannelState cad;
            fira_channel_init(&fad, BENCH_FRAME); tfb_channel_init(&cad);
            tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);
            for (int f = 0; f < BENCH_NFR && g_f5_dump_idx0 < 0; f++) {
                const int32_t *xin = &chirp[f * BENCH_FRAME];
                for (int i = 0; i < BENCH_FRAME; i++) xw[i] = f5_apply_w(w, xin[i]);
                fira_tfb_analyze(&fad, xw, BENCH_FRAME, fsb0, fsb1, fsb2, fsb3);
                tfb_analyze(&cad, xw, BENCH_FRAME, csb0, csb1, csb2, csb3);
                for (int i = 0; i < BENCH_FRAME; i++) {
                    int32_t cv = csb3[i]; int32_t mag = (cv < 0) ? -cv : cv;
                    if (mag >= F4_PROBE_THRESH) {
                        g_f5_dump_idx0 = f * BENCH_FRAME + i;
                        for (int d = 0; d < F4_DUMP_N; d++) {
                            int j = i + d;
                            g_f5_dump_core[d] = (j < BENCH_FRAME) ? csb3[j] : 0;
                            g_f5_dump_fira[d] = (j < BENCH_FRAME) ? fsb3[j] : 0;
                        }
                        break;
                    }
                }
            }
            fira_tree_teardown();
        }
    }

    g_f5_pass_all = all;
    return all;
}

/* ============================================================
 * cycle plan (plan S5.1 F8): FIRA version cyc_8ch_frame measured with existing CCNT (bench_cyc_target)
 *   -> compare to pure core 1,006,935 -> compute new margin + 16ch deadline.
 * [L1/EZKIT] bench-side; iron rule 8/C9: before R14 (fira_r14_regression_8ch==1, on board) passes,
 *   cycle/margin benefit **must not be written into any selection basis** (violation = BLOCKER). This file contains no benefit numbers.
 * ============================================================ */
