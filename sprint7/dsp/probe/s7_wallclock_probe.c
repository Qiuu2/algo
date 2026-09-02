/*
 * s7_wallclock_probe.c -- WO-S7-B6.3 bench-side wall-clock split probe (target + desktop).
 *
 * ASCII-only (CCES SHARC compiler chokes on UTF-8). NEW self-contained bench TU. It does NOT edit
 *   fira_regression.c (the F4/F5/F7 PASS paths stay byte-identical) and touches NO frozen file
 *   (tree_filterbank.c/.h, tfb_8ch.c, fira_tree.c, dolph_w8_q15.h, fir_coeffs_hb63.h, fir_coeffs_q31.h,
 *   golden_ref.h, chirp_input.h, dolph_f5_goldens.h, sprint4 .ldf).
 *
 * WHAT IT MEASURES (DEC-S7-IMPL-01 (1)b; S7_B63_WALLCLOCK_GAP.md sec 2):
 *   The bench F7 8ch FIRA wall-clock (fira_regression.c:611-619: per channel weight -> fira_tfb_analyze ->
 *   fira_tfb_synthesize, MAIN context, FIRA busy-wait INSIDE the span) split into three per-frame segments,
 *   each the SUM over the 8 channels of ONE frame, plus the outer per-frame bracket:
 *     w    : the input-scale Dolph weight loop, 64 x ((w_q15 * x_q31) >> 15) == f5_apply_w (fira_regression.c:260-263)
 *            (+ the loop increment for c > 0, because the reads are chained -- see below)
 *     ana  : the fira_tfb_analyze call ONLY   (frozen fira_tree.c: 3 DEC + 3 ana_int FIRA segments + detail subtract)
 *     syn  : the fira_tfb_synthesize call ONLY (frozen fira_tree.c: 3 syn_int FIRA segments + sat_add)
 *     beam : the whole 8-channel loop (t_end - t_start) == the F7 span caliber (fira_regression.c:611-619)
 *   Stats over the measured frames: last / max / min. The first S7_WARM frames are RUN (they belong to the
 *   CRC stream and fill the cross-frame history) but EXCLUDED from the stats (steady-state discipline,
 *   bench_harness.c:84-86, F7_WARM). Unlike F7 (ONE measured frame) this probe sweeps ALL BENCH_NFR frames,
 *   so max/min also expose the intra-run jitter band of the same span.
 *
 * CHAINED READS (isomorphic to the board's M2_SEG_CYC brackets, m1_loopback_tdm.c m2_fira_beam_frame):
 *     ta = read  (opens w of c=0)
 *     for c: weight loop; t1 = read (w close / ana open); analyze; t2 = read (ana close / syn open);
 *            synthesize; t3 = read (syn close = w open of c+1); ta = t3
 *   -> 1 + 3 x 8 = 25 reads per frame INSIDE the beam bracket (board: 1 + 4 x 8 = 33, it has a 4th tx segment),
 *   + 2 reads for the beam bracket itself = 27 per frame. Each segment reading contains the cost of ONE read
 *   (its own close) and the sum w+ana+syn contains 24 of the 25; g_s7_probe_ovh_last = beam - sum is therefore
 *   ~ the chain-open read + loop entry/exit (1-2 reads' worth), NOT 24 reads. The probe measures one read
 *   pair back-to-back (g_s7_ccnt_read_cyc) and publishes g_s7_reads_per_frame (25) so the deduction is
 *   reads x g_s7_ccnt_read_cyc [L1 when run]; per segment the perturbation is 8 x g_s7_ccnt_read_cyc.
 *
 * WHY THE THREE SEGMENTS ARE COMPARABLE WITH THE BOARD (M2, m1_loopback_tdm.c m2_fira_beam_frame):
 *   Same frozen API (fira_tree_setup / tfb_set_coeffs / fira_channel_init x8 at init; per frame per channel
 *   weight -> fira_tfb_analyze -> fira_tfb_synthesize), same frame length 64, same 8 channels, same Q15 x
 *   Q31 >> 15 weight, same per-channel cross-frame FiraChannelState, same chained-read bracket structure.
 *   Differences (documented, not hidden): input is the frozen chirp (bench) vs live audio (board) --
 *   fixed-point MAC time is data-independent; bench has NO SPORT DMA / RX ISR running; bench has NO TX
 *   interleave segment (the board's "tx" bracket has no bench counterpart; the board's w of c>0 starts at the
 *   previous channel's tx close, the bench's w of c>0 starts at the previous channel's syn close).
 *
 * ANTI-FALSE-GREEN (FG, CLAUDE.md DSP/FIRA gate + critic sec 12) -- coverage stated honestly:
 *   FG-A (ANALYZE segment only): in the SAME run, the per-channel FIRA subband CRC (sb0|sb1|sb2|sb3 every
 *     frame, streaming over ALL BENCH_NFR frames from a zero-initialized state -- EXACTLY the F5-A criterion,
 *     fira_regression.c fira_r14_regression_8ch) must equal the 8 frozen anchors g_f5_golden_crc[c]
 *     (dolph_f5_goldens.h: 8 DISTINCT values, c=7 == the F4 anchor 0x2E0D8C6E). This proves the analyze
 *     segment timed the REAL FIRA chain: a stubbed / memset-0 / unweighted / phase-wrong analyze FAILS every
 *     anchor -> g_s7_fg_pass_all = 0 -> the cycle numbers are NOT to be used. CRC runs OUTSIDE every bracket.
 *   FG-B (positive control, host + board): the CORE chain (verbatim tree_filterbank.c tfb_analyze) over the
 *     same weighted chirp, through the SAME crc/weight/sequence code of this file, must ALSO hit the 8
 *     anchors (g_s7_core_selfcheck_all = 1) -> the probe's FG machinery is same-source with gen_f5_goldens.c.
 *   FG-C (negative control, desktop): built with -DS7_PROBE_HOST_FORCE the setup gate is bypassed and the
 *     desktop fira_tfb_* placeholders (memset 0, fira_tree.c:711-719 / 754-768) run -> every anchor FAILS.
 *   FG-D (desktop honest 0): without S7_PROBE_HOST_FORCE, fira_tree_setup() < 0 on desktop -> return 0.
 *   SYNTHESIZE HAS NO ANCHOR (pre-existing blind spot shared with F4/F5/F7): the 3 syn_int FIRA segments'
 *     rc are (void)-discarded in the frozen file; a failing/early-returning syn segment would produce a SHORT
 *     syn reading while FG-A stays green. Treat syn readings as one confidence grade below w/ana.
 *   FG-E (OPTIONAL syn-side control, -DS7_PROBE_SYN_FG; mandatory or not = CTO ruling): after the frame's
 *     brackets, the SAME FIRA subbands are fed to the frozen CORE tfb_synthesize (per-channel
 *     TreeChannelState, so both synth histories stay in lockstep) and both synth outputs are CRC'd over all
 *     frames -> g_s7_syn_fg[c] (1 equal / 0 differ) and g_s7_syn_fg_all. Only evaluated when FG-A passed:
 *     with placeholder subbands (0,0,0,in) both synths trivially agree, so on the desktop the flag is
 *     reported as -2 (not evaluated), never as a PASS. Extra cost: ~18 KB static + core synth time OUTSIDE
 *     the brackets -> default OFF.
 *
 * C9 discipline: RAW counters only. NO margin / MCPS / ratio / benefit computed here.
 * FREE-RUN: read g_s7_* at idle only. NO breakpoint inside the frame loop (FIRA spin + breakpoint deadlocks).
 *
 * Build (target): CCES -proc ADSP-21569 -DTARGET_SHARC -DFIRA_USE_REAL_ADI_FIR_HEADER, added to the FIRA
 *   bench project source list next to fira_regression.c / h1_wcet_measure.c (README wiring diff).
 * Build (desktop): see run_s7_probe_host.sh (gcc, -DS7_HOST_MAIN [-DS7_PROBE_HOST_FORCE]).
 * Optional: -DS7_PROBE_INNER with the diagnostic copy fira_tree_probe.c linked INSTEAD OF fira_tree.c
 *   (README sec 4) -> inner split task/spin/flush/postscale/mem/core. -DS7_PROBE_FA_BLOCK1 pins s_s7_fa to
 *   seg_l1_block1 (mirrors the M2 pin of s_m2_fa; the section name exists in m1_app.ldf and ADI's EE408
 *   app.ldf, its presence in the bench .ldf is [L4] until the bench build); default OFF = F7-like placement.
 *   -DS7_PROBE_SYN_FG enables FG-E.
 */
#include <stdint.h>
#include <string.h>
#include "tree_filterbank.h"    /* TreeChannelState, tfb_set_coeffs, tfb_channel_init, tfb_analyze, tfb_synthesize (frozen .c untouched) */
#include "fir_coeffs_hb63.h"    /* g_hb63_q15, FIR_HB63_NTAPS (frozen header, read-only) */
#include "bench_harness.h"      /* BENCH_FRAME / BENCH_NFR */
#include "dolph_w8_q15.h"       /* g_dolph_w8_q15[8], DOLPH_W8_NCH, DOLPH_W8_QBITS (frozen) */
#include "dolph_f5_goldens.h"   /* g_f5_golden_crc[8] (frozen 8 anchors) */
#include "fira_tree.h"          /* FiraChannelState, fira_tree_setup/teardown, fira_channel_init, fira_tfb_* (frozen .c untouched) */
#include "s7_wallclock_probe.h"

#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)
#include <services/pwr/adi_pwr.h>   /* adi_pwr_GetCoreClkFreq (BSP; G6 evidence in fira_regression.c) */
#endif

extern const int32_t *bench_chirp_input(void);   /* the ONE frozen chirp copy (bench_harness.c:32) */

#ifdef S7_HOST_MAIN
/* desktop: bench_main.c (which defines bench_cyc_target under TARGET_SHARC) is not linked; provide a
 * plumbing-only clock() stand-in. Values are MEANINGLESS on host (g_s7_valid stays 0). */
#include <time.h>
#include <stdio.h>
uint32_t bench_cyc_target(void) { return (uint32_t)clock(); }
#else
extern uint32_t bench_cyc_target(void);          /* CCLK cycle counter (clock()); bench_main.c:118 (TARGET_SHARC) */
#endif

#define S7_WARM      4                           /* warm-up frames excluded from stats (== F7_WARM / H1_WARM discipline) */
#define S7_SB0       0                           /* staging layout: sb0[8] | sb1[16] | sb2[32] | sb3[64] = 120 words */
#define S7_SB1       (BENCH_FRAME / 8)
#define S7_SB2       (S7_SB1 + BENCH_FRAME / 4)
#define S7_SB3       (S7_SB2 + BENCH_FRAME / 2)
#define S7_SB_TOTAL  (S7_SB3 + BENCH_FRAME)      /* 120 @ frame 64 */
#define S7_READS_PER_FRAME (1u + 3u * (uint32_t)DOLPH_W8_NCH)   /* chained reads inside the beam bracket = 25 */

/* ---- raw readouts (definitions; extern in the header). Init = honest FAIL / not-run sentinels. ---- */
volatile int      g_s7_valid            = 0;
volatile int      g_s7_host_forced      = 0;
volatile int      g_s7_setup_rc         = -99;
volatile int      g_s7_fa_block1        = 0;
volatile uint32_t g_s7_frames           = 0u;
volatile uint32_t g_s7_frames_total     = 0u;
volatile uint32_t g_s7_cclk_hz          = 0u;
volatile int      g_s7_cclk_rc          = -99;
volatile uint32_t g_s7_ccnt_read_cyc    = 0u;
volatile uint32_t g_s7_reads_per_frame  = S7_READS_PER_FRAME;

volatile uint32_t g_s7_seg_w_cyc_last   = 0u, g_s7_seg_w_cyc_max   = 0u, g_s7_seg_w_cyc_min   = 0xFFFFFFFFu;
volatile uint32_t g_s7_seg_ana_cyc_last = 0u, g_s7_seg_ana_cyc_max = 0u, g_s7_seg_ana_cyc_min = 0xFFFFFFFFu;
volatile uint32_t g_s7_seg_syn_cyc_last = 0u, g_s7_seg_syn_cyc_max = 0u, g_s7_seg_syn_cyc_min = 0xFFFFFFFFu;
volatile uint32_t g_s7_beam_cyc_last    = 0u, g_s7_beam_cyc_max    = 0u, g_s7_beam_cyc_min    = 0xFFFFFFFFu;
volatile uint32_t g_s7_seg_sum_last     = 0u;
volatile uint32_t g_s7_probe_ovh_last   = 0u;

volatile uint32_t g_s7_crc_fira[DOLPH_W8_NCH];
volatile int      g_s7_fg_anchor_pass[DOLPH_W8_NCH];
volatile int      g_s7_fg_pass_all      = -99;
volatile uint32_t g_s7_crc_core[DOLPH_W8_NCH];
volatile int      g_s7_core_anchor_pass[DOLPH_W8_NCH];
volatile int      g_s7_core_selfcheck_all = -99;

#ifdef S7_PROBE_SYN_FG
volatile int      g_s7_syn_fg_built     = 1;
#else
volatile int      g_s7_syn_fg_built     = 0;
#endif
volatile uint32_t g_s7_syn_crc_fira[DOLPH_W8_NCH];
volatile uint32_t g_s7_syn_crc_core[DOLPH_W8_NCH];
volatile int      g_s7_syn_fg[DOLPH_W8_NCH];
volatile int      g_s7_syn_fg_all       = -99;

volatile int      g_s7_inner_valid      = 0;
volatile uint32_t g_s7_in_task_cyc_last  = 0u, g_s7_in_task_cyc_max  = 0u, g_s7_in_task_cyc_min  = 0xFFFFFFFFu;
volatile uint32_t g_s7_in_spin_cyc_last  = 0u, g_s7_in_spin_cyc_max  = 0u, g_s7_in_spin_cyc_min  = 0xFFFFFFFFu;
volatile uint32_t g_s7_in_flush_cyc_last = 0u, g_s7_in_flush_cyc_max = 0u, g_s7_in_flush_cyc_min = 0xFFFFFFFFu;
volatile uint32_t g_s7_in_post_cyc_last  = 0u, g_s7_in_post_cyc_max  = 0u, g_s7_in_post_cyc_min  = 0xFFFFFFFFu;
volatile uint32_t g_s7_in_mem_cyc_last   = 0u, g_s7_in_mem_cyc_max   = 0u, g_s7_in_mem_cyc_min   = 0xFFFFFFFFu;
volatile uint32_t g_s7_in_core_cyc_last  = 0u, g_s7_in_core_cyc_max  = 0u, g_s7_in_core_cyc_min  = 0xFFFFFFFFu;
volatile uint32_t g_s7_in_reads_last     = 0u;

/* ---- static working set (off-stack: a FiraChannelState[8] is ~18 KB, R37/F7-FIX2 stack discipline) ----
 * s_s7_fa: the 8 per-channel FIRA cross-frame states (ST1). Default placement = whatever the bench .ldf gives
 *   seg_dmda (F7's f7_fa[] lives there too -> same placement class as the 463,273 anchor). With
 *   -DS7_PROBE_FA_BLOCK1 it is pinned to seg_l1_block1 like the board's s_m2_fa (m1_loopback_tdm.c:218-219;
 *   pragma form [L1] per ADI FIR_Throughput_21569.c:23) so a placement-driven difference can be A/B'd on bench.
 * s_s7_sb: per-channel subband staging (analyze writes here, synthesize reads here, CRC reads here AFTER the
 *   brackets) -> no memcpy inside any bracket. s_s7_out: per-channel synth output staging (FG-E compares it
 *   after the brackets; with chained reads nothing may run between a syn close and the next w close). */
#if defined(TARGET_SHARC) && defined(S7_PROBE_FA_BLOCK1)
#pragma section("seg_l1_block1")
#endif
static FiraChannelState s_s7_fa[DOLPH_W8_NCH];
static TreeChannelState s_s7_ca;                          /* core positive control, channel-major -> ONE state */
static int32_t          s_s7_sb[DOLPH_W8_NCH][S7_SB_TOTAL];
static int32_t          s_s7_out[DOLPH_W8_NCH][BENCH_FRAME];
static int32_t          s_s7_xw[BENCH_FRAME];
static uint32_t         s_s7_crc[DOLPH_W8_NCH];
#ifdef S7_PROBE_SYN_FG
static TreeChannelState s_s7_cs[DOLPH_W8_NCH];            /* FG-E: core synth states, lockstep with s_s7_fa */
static int32_t          s_s7_cout[BENCH_FRAME];
static uint32_t         s_s7_crc_fout[DOLPH_W8_NCH];
static uint32_t         s_s7_crc_cout[DOLPH_W8_NCH];
#endif

/* Incremental CRC32 IEEE 802.3 (STREAMING): init 0xFFFFFFFF, update per frame, final ^0xFFFFFFFF.
 * SAME polynomial / byte order / result as fira_regression.c:71-81 crc32_update and bench_harness.c crc32_buf
 * (own copy so this TU stays self-contained; fira_regression.c is NOT edited). */
static void s7_crc32_update(uint32_t *c, const int32_t *d, int n)
{
    int i, b, k;
    for (i = 0; i < n; i++) {
        uint32_t v = (uint32_t)d[i];
        for (b = 0; b < 4; b++) {
            uint8_t by = (uint8_t)(v >> (8 * b));
            *c ^= by;
            for (k = 0; k < 8; k++) *c = (*c & 1u) ? (*c >> 1) ^ 0xEDB88320u : (*c >> 1);
        }
    }
}

/* input-scale weight: BIT-EXACT to fira_regression.c:260-263 f5_apply_w, gen_f5_goldens.c apply_w and
 * m1_loopback_tdm.c m2_fira_beam_frame (Q15 x Q31 >> 15, arithmetic shift). Same truncation point as the chain. */
static int32_t s7_apply_w(int32_t w_q15, int32_t x_q31)
{
    return (int32_t)(((int64_t)w_q15 * (int64_t)x_q31) >> DOLPH_W8_QBITS);
}

#define S7_STAT(name, v) do { name##_last = (v); \
                              if ((v) > name##_max) name##_max = (v); \
                              if ((v) < name##_min) name##_min = (v); } while (0)

static void s7_reset_readouts(void)
{
    int c;
    g_s7_valid = 0; g_s7_host_forced = 0; g_s7_setup_rc = -99;
    g_s7_frames = 0u; g_s7_frames_total = 0u; g_s7_cclk_hz = 0u; g_s7_cclk_rc = -99; g_s7_ccnt_read_cyc = 0u;
    g_s7_reads_per_frame = S7_READS_PER_FRAME;
    g_s7_seg_w_cyc_last = 0u;   g_s7_seg_w_cyc_max = 0u;   g_s7_seg_w_cyc_min = 0xFFFFFFFFu;
    g_s7_seg_ana_cyc_last = 0u; g_s7_seg_ana_cyc_max = 0u; g_s7_seg_ana_cyc_min = 0xFFFFFFFFu;
    g_s7_seg_syn_cyc_last = 0u; g_s7_seg_syn_cyc_max = 0u; g_s7_seg_syn_cyc_min = 0xFFFFFFFFu;
    g_s7_beam_cyc_last = 0u;    g_s7_beam_cyc_max = 0u;    g_s7_beam_cyc_min = 0xFFFFFFFFu;
    g_s7_seg_sum_last = 0u; g_s7_probe_ovh_last = 0u;
    for (c = 0; c < DOLPH_W8_NCH; c++) {
        g_s7_crc_fira[c] = 0u; g_s7_fg_anchor_pass[c] = 0;
        g_s7_crc_core[c] = 0u; g_s7_core_anchor_pass[c] = 0;
        g_s7_syn_crc_fira[c] = 0u; g_s7_syn_crc_core[c] = 0u; g_s7_syn_fg[c] = -99;
    }
    g_s7_fg_pass_all = -99; g_s7_core_selfcheck_all = -99; g_s7_syn_fg_all = -99;
    g_s7_inner_valid = 0;
    g_s7_in_task_cyc_last = 0u;  g_s7_in_task_cyc_max = 0u;  g_s7_in_task_cyc_min = 0xFFFFFFFFu;
    g_s7_in_spin_cyc_last = 0u;  g_s7_in_spin_cyc_max = 0u;  g_s7_in_spin_cyc_min = 0xFFFFFFFFu;
    g_s7_in_flush_cyc_last = 0u; g_s7_in_flush_cyc_max = 0u; g_s7_in_flush_cyc_min = 0xFFFFFFFFu;
    g_s7_in_post_cyc_last = 0u;  g_s7_in_post_cyc_max = 0u;  g_s7_in_post_cyc_min = 0xFFFFFFFFu;
    g_s7_in_mem_cyc_last = 0u;   g_s7_in_mem_cyc_max = 0u;   g_s7_in_mem_cyc_min = 0xFFFFFFFFu;
    g_s7_in_core_cyc_last = 0u;  g_s7_in_core_cyc_max = 0u;  g_s7_in_core_cyc_min = 0xFFFFFFFFu;
    g_s7_in_reads_last = 0u;
#if defined(TARGET_SHARC) && defined(S7_PROBE_FA_BLOCK1)
    g_s7_fa_block1 = 1;
#else
    g_s7_fa_block1 = 0;
#endif
}

/* FG-B positive control: the CORE chain over the same weighted chirp must reproduce the 8 anchors.
 * Channel-major with ONE TreeChannelState (re-zeroed per channel) -- the anchors were generated exactly so
 * (gen_f5_goldens.c: zero state, frames 0..NFR-1, crc over sb0|sb1|sb2|sb3 each frame). Runs on host and board.
 * Placed OUTSIDE every timed bracket (before the FIRA sweep). */
static void s7_core_selfcheck(const int32_t *chirp)
{
    int c, f, i, all = 1;
    int32_t *sb = s_s7_sb[0];
    for (c = 0; c < DOLPH_W8_NCH; c++) {
        const int32_t w = g_dolph_w8_q15[c];
        uint32_t crc = 0xFFFFFFFFu;
        tfb_channel_init(&s_s7_ca);
        for (f = 0; f < BENCH_NFR; f++) {
            const int32_t *xin = &chirp[f * BENCH_FRAME];
            for (i = 0; i < BENCH_FRAME; i++) s_s7_xw[i] = s7_apply_w(w, xin[i]);
            tfb_analyze(&s_s7_ca, s_s7_xw, (uint16_t)BENCH_FRAME,
                        sb + S7_SB0, sb + S7_SB1, sb + S7_SB2, sb + S7_SB3);
            s7_crc32_update(&crc, sb, S7_SB_TOTAL);      /* == crc(sb0) then sb1, sb2, sb3 (contiguous staging) */
        }
        g_s7_crc_core[c] = crc ^ 0xFFFFFFFFu;
        g_s7_core_anchor_pass[c] = (g_s7_crc_core[c] == g_f5_golden_crc[c]) ? 1 : 0;
        if (!g_s7_core_anchor_pass[c]) all = 0;
    }
    g_s7_core_selfcheck_all = all;
}

#ifdef S7_PROBE_INNER
#define S7_INNER_RESET() do { g_s7_in_task_cyc = 0u; g_s7_in_spin_cyc = 0u; g_s7_in_flush_cyc = 0u; \
                              g_s7_in_post_cyc = 0u; g_s7_in_mem_cyc = 0u; g_s7_in_core_cyc = 0u; \
                              g_s7_in_reads = 0u; } while (0)
static void s7_inner_capture(void)
{
    S7_STAT(g_s7_in_task_cyc,  g_s7_in_task_cyc);
    S7_STAT(g_s7_in_spin_cyc,  g_s7_in_spin_cyc);
    S7_STAT(g_s7_in_flush_cyc, g_s7_in_flush_cyc);
    S7_STAT(g_s7_in_post_cyc,  g_s7_in_post_cyc);
    S7_STAT(g_s7_in_mem_cyc,   g_s7_in_mem_cyc);
    S7_STAT(g_s7_in_core_cyc,  g_s7_in_core_cyc);
    g_s7_in_reads_last = g_s7_in_reads;
    g_s7_inner_valid = 1;
}
#else
#define S7_INNER_RESET() do { } while (0)
#define s7_inner_capture() do { } while (0)
#endif

/* FG-E per-frame work (OUTSIDE the brackets): core synth on the SAME subbands, both outputs CRC'd. */
#ifdef S7_PROBE_SYN_FG
static void s7_syn_fg_frame(void)
{
    int c;
    for (c = 0; c < DOLPH_W8_NCH; c++) {
        const int32_t *sb = s_s7_sb[c];
        tfb_synthesize(&s_s7_cs[c], sb + S7_SB0, sb + S7_SB1, sb + S7_SB2, sb + S7_SB3,
                       (uint16_t)BENCH_FRAME, s_s7_cout);
        s7_crc32_update(&s_s7_crc_fout[c], s_s7_out[c], BENCH_FRAME);
        s7_crc32_update(&s_s7_crc_cout[c], s_s7_cout,   BENCH_FRAME);
    }
}
#endif

int s7_wallclock_probe(void)
{
    const int32_t *chirp = bench_chirp_input();
    int c, f, i, all;
    int ran_fira = 0;

    s7_reset_readouts();

    /* bracket perturbation unit: one back-to-back read pair (nothing in between) */
    {
        uint32_t a = bench_cyc_target();
        uint32_t b = bench_cyc_target();
        g_s7_ccnt_read_cyc = b - a;
    }

#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)
    {
        uint32_t cclk = 0u;
        g_s7_cclk_rc = (int)adi_pwr_GetCoreClkFreq(0u, &cclk);   /* pwr service inited at startup (bench_main.c) */
        g_s7_cclk_hz = cclk;
    }
#endif

    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);   /* core (golden) Q15 coeffs; FIRA coeffs are set inside fira_tree_setup */

    /* FG-B positive control (host + board), outside every bracket */
    s7_core_selfcheck(chirp);

    /* [L1/EZKIT] bench: fira_tree_setup() (Open/RegisterCallback). Desktop returns -1 -> honest 0 (FG-D). */
    g_s7_setup_rc = fira_tree_setup();
#ifdef S7_PROBE_HOST_FORCE
    /* FG-C negative control (desktop ONLY): bypass the gate so the desktop fira_tfb_* placeholders run and the
     * anchors demonstrably FAIL. Never define this for a target build (it would hide a real setup failure). */
    g_s7_host_forced = 1;
#else
    if (g_s7_setup_rc != 0) {
        g_s7_fg_pass_all = 0;   /* honest FAIL: the FIRA chain never ran */
        return 0;
    }
    ran_fira = 1;
#endif

    for (c = 0; c < DOLPH_W8_NCH; c++) {
        fira_channel_init(&s_s7_fa[c], (uint16_t)BENCH_FRAME);   /* zero cross-frame history (== F5/F7/M2 init) */
        s_s7_crc[c] = 0xFFFFFFFFu;
#ifdef S7_PROBE_SYN_FG
        tfb_channel_init(&s_s7_cs[c]);
        s_s7_crc_fout[c] = 0xFFFFFFFFu; s_s7_crc_cout[c] = 0xFFFFFFFFu;
#endif
    }

    /* ===== the measured sweep: frame-major over ALL frames (== M2 order: per frame, channels 0..7) =====
     * Serial discipline [ASSUME-A1]: one FIRA segment at a time on the shared s_hFir; per-channel state
     * s_s7_fa[c] keeps each channel's own history (ST1), advanced exactly once per frame. */
    for (f = 0; f < BENCH_NFR; f++) {
        const int32_t *xin = &chirp[f * BENCH_FRAME];
        uint32_t sw = 0u, sa = 0u, ss = 0u, tb0, tb1, ta, t1, t2, t3;

        S7_INNER_RESET();
        tb0 = bench_cyc_target();                       /* ---- outer beam bracket OPEN (F7 caliber) ---- */
        ta = bench_cyc_target();                        /* chain open: w bracket of c=0 (== board 'ta' before the loop) */
        for (c = 0; c < DOLPH_W8_NCH; c++) {
            const int32_t w = g_dolph_w8_q15[c];        /* identity channel->weight (== F5/F7; M2 default build) */
            int32_t *sb = s_s7_sb[c];
            for (i = 0; i < BENCH_FRAME; i++) s_s7_xw[i] = s7_apply_w(w, xin[i]);          /* [w] */
            t1 = bench_cyc_target();                    /* w CLOSE / ana OPEN */
            fira_tfb_analyze(&s_s7_fa[c], s_s7_xw, (uint16_t)BENCH_FRAME,                     /* [ana] */
                             sb + S7_SB0, sb + S7_SB1, sb + S7_SB2, sb + S7_SB3);
            t2 = bench_cyc_target();                    /* ana CLOSE / syn OPEN */
            fira_tfb_synthesize(&s_s7_fa[c], sb + S7_SB0, sb + S7_SB1, sb + S7_SB2, sb + S7_SB3, /* [syn] */
                                (uint16_t)BENCH_FRAME, s_s7_out[c]);
            t3 = bench_cyc_target();                    /* syn CLOSE = w OPEN of c+1 (chained, no extra read) */
            sw += t1 - ta; sa += t2 - t1; ss += t3 - t2;
            ta = t3;
        }
        tb1 = bench_cyc_target();                       /* ---- outer beam bracket CLOSE ---- */

        /* ---- everything below is OUTSIDE the brackets (diagnostic work must not pollute the count) ---- */
        for (c = 0; c < DOLPH_W8_NCH; c++)
            s7_crc32_update(&s_s7_crc[c], s_s7_sb[c], S7_SB_TOTAL);   /* FG-A stream (sb0|sb1|sb2|sb3 per frame) */
#ifdef S7_PROBE_SYN_FG
        s7_syn_fg_frame();                                            /* FG-E: core synth on the same subbands */
#endif
        g_s7_frames_total++;
        if (f >= S7_WARM) {
            uint32_t beam = tb1 - tb0;
            S7_STAT(g_s7_seg_w_cyc,   sw);
            S7_STAT(g_s7_seg_ana_cyc, sa);
            S7_STAT(g_s7_seg_syn_cyc, ss);
            S7_STAT(g_s7_beam_cyc,    beam);
            g_s7_seg_sum_last   = sw + sa + ss;
            g_s7_probe_ovh_last = (beam > g_s7_seg_sum_last) ? (beam - g_s7_seg_sum_last) : 0u;
            s7_inner_capture();
            g_s7_frames++;
        }
    }

    /* FG-A verdict: per-channel (NO aggregate-only masking) + convenience AND */
    all = 1;
    for (c = 0; c < DOLPH_W8_NCH; c++) {
        g_s7_crc_fira[c] = s_s7_crc[c] ^ 0xFFFFFFFFu;
        g_s7_fg_anchor_pass[c] = (g_s7_crc_fira[c] == g_f5_golden_crc[c]) ? 1 : 0;
        if (!g_s7_fg_anchor_pass[c]) all = 0;
    }
    g_s7_fg_pass_all = all;

#ifdef S7_PROBE_SYN_FG
    /* FG-E verdict: only meaningful when the analyze anchors passed (else both synths see degenerate
     * subbands and agree trivially -> report -2 "not evaluated", never a PASS). Recorded, not gating. */
    {
        int syn_all = 1;
        for (c = 0; c < DOLPH_W8_NCH; c++) {
            g_s7_syn_crc_fira[c] = s_s7_crc_fout[c] ^ 0xFFFFFFFFu;
            g_s7_syn_crc_core[c] = s_s7_crc_cout[c] ^ 0xFFFFFFFFu;
            if (g_s7_fg_pass_all == 1) {
                g_s7_syn_fg[c] = (g_s7_syn_crc_fira[c] == g_s7_syn_crc_core[c]) ? 1 : 0;
                if (!g_s7_syn_fg[c]) syn_all = 0;
            } else {
                g_s7_syn_fg[c] = -2;
                syn_all = -2;
            }
        }
        g_s7_syn_fg_all = syn_all;
    }
#endif

    if (ran_fira) {
        fira_tree_teardown();
#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)
        g_s7_valid = 1;             /* cycles meaningful ONLY here (board, real FIRA) -- and only if fg_pass_all == 1 */
#endif
    }
    return g_s7_valid;
}

#ifdef S7_HOST_MAIN
/* Desktop harness: prints the readouts and returns 0 iff the HOST expectations hold:
 *   positive control (core anchors) PASS 8/8, FIRA-path FG FAIL 0/8 (placeholder chain on host), valid == 0,
 *   and (S7_PROBE_SYN_FG build) syn_fg_all == -2 (not evaluated because FG-A failed -- never a host PASS).
 * This is the honest-FAIL demonstration requested by DEC-S7-IMPL-01 (cycles on host are MEANINGLESS). */
int main(void)
{
    int c, rc, ok;
    rc = s7_wallclock_probe();
    printf("==== s7_wallclock_probe host run [L2 host plumbing; cycles MEANINGLESS off-board] ====\n");
    printf("valid=%d host_forced=%d setup_rc=%d frames_total=%u frames=%u inner_valid=%d fa_block1=%d syn_fg_built=%d reads_per_frame=%u\n",
           g_s7_valid, g_s7_host_forced, g_s7_setup_rc, (unsigned)g_s7_frames_total, (unsigned)g_s7_frames,
           g_s7_inner_valid, g_s7_fa_block1, g_s7_syn_fg_built, (unsigned)g_s7_reads_per_frame);
    printf("[FG-B core positive control] selfcheck_all=%d\n", g_s7_core_selfcheck_all);
    for (c = 0; c < DOLPH_W8_NCH; c++)
        printf("   c=%d core_crc=0x%08X golden=0x%08X pass=%d\n", c, (unsigned)g_s7_crc_core[c],
               (unsigned)g_f5_golden_crc[c], g_s7_core_anchor_pass[c]);
    printf("[FG-A FIRA-path ANALYZE anchors] fg_pass_all=%d (host: EXPECTED 0 = honest FAIL, placeholder chain)\n",
           g_s7_fg_pass_all);
    for (c = 0; c < DOLPH_W8_NCH; c++)
        printf("   c=%d fira_crc=0x%08X golden=0x%08X pass=%d\n", c, (unsigned)g_s7_crc_fira[c],
               (unsigned)g_f5_golden_crc[c], g_s7_fg_anchor_pass[c]);
    printf("[FG-E syn control] built=%d syn_fg_all=%d (host: EXPECTED -2 = not evaluated, FG-A failed; -99 = not built)\n",
           g_s7_syn_fg_built, g_s7_syn_fg_all);
    printf("[cycles, host = meaningless] beam last/max/min=%u/%u/%u  w=%u ana=%u syn=%u sum=%u ovh=%u read_pair=%u\n",
           (unsigned)g_s7_beam_cyc_last, (unsigned)g_s7_beam_cyc_max, (unsigned)g_s7_beam_cyc_min,
           (unsigned)g_s7_seg_w_cyc_last, (unsigned)g_s7_seg_ana_cyc_last, (unsigned)g_s7_seg_syn_cyc_last,
           (unsigned)g_s7_seg_sum_last, (unsigned)g_s7_probe_ovh_last, (unsigned)g_s7_ccnt_read_cyc);
    ok = (g_s7_core_selfcheck_all == 1) && (g_s7_fg_pass_all == 0) && (g_s7_valid == 0) && (rc == 0);
    if (g_s7_syn_fg_built) ok = ok && (g_s7_syn_fg_all == -2);
    else                   ok = ok && (g_s7_syn_fg_all == -99);
    printf("==== host expectation (core 8/8 PASS, FIRA 0/8 honest FAIL, valid 0, syn_fg not-evaluated): %s ====\n",
           ok ? "MET" : "NOT MET");
    return ok ? 0 : 1;
}
#endif
