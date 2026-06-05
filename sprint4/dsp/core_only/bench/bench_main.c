/*
 * bench_main.c -- grafted main (target-only): ADI scaffold boot + our harness slot.
 * (ASCII-only: CCES SHARC compiler chokes on UTF-8 comments; synced to bench tree 2026-06-03.)
 *
 * Graft boundary (red lines):
 *   - ADI base (keep, do not modify): adi_initComponents() (clock/power/pinmux/sru,
 *     from ADSP21569_LED example system/startup_ldf + adi_initialize).
 *   - Our algorithm (graft): bench_run() runs core-only (verbatim tree_filterbank.c
 *     + tfb_8ch + hb63).
 *   - NO float layer / NO example coeffs(437-tap) / NO codec/A2B/DMA (memory-vector method).
 *
 * Usage: in the FIRA-derived bench_core_only project, replace src/main.c with this file
 *   (keep system/ board init); add tree_filterbank.c, tfb_8ch.c, bench_harness.c;
 *   include path -> ../src ../include + bench/.
 * Build: CCES -proc ADSP-21569 -DTARGET_SHARC (target 0err = [L1/CCES-target], bench-side).
 *
 * Results: read in CCES emulator (Expressions window): g_bench_result, g_ccnt_selftest,
 *   and (FIRA build) g_fira_f2_rc / g_FIRTaskDoneCount. No LED indicator (idle after run).
 */
#include "adi_initialize.h"       /* adi_initComponents() decl */
#include "bench_harness.h"
#include <stdint.h>
#include <time.h>                 /* clock() -> CCLK cycles on CCES SHARC */

/* results to known memory for emulator / later deploy (volatile = keep) */
volatile BenchResult g_bench_result;
volatile uint32_t    g_ccnt_selftest;   /* CCNT self-test (known-loop cycles) */

#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
#include "fira_tree.h"                       /* F2 FIRA smoke (only when FIRA wired) */
#include "fir_coeffs_q31.h"                  /* F3 real coeffs g_hb63_fira32 */
#if defined(TARGET_SHARC)
#include <services/pwr/adi_pwr.h>            /* F7-FIX: adi_pwr_Init at startup (BSP-supplied; G6 evidence in fira_regression.c) */
#endif
extern volatile uint32_t g_FIRTaskDoneCount; /* defined in fira_tree.c (set by ALL_CHANNEL_DONE cb) */
volatile int g_fira_f2_rc = -99;             /* F2/F3 single-channel template rc (emulator; 0=PASS) */
volatile int32_t g_fira_f3_out0 = 0;         /* F3 spot: output buf head words (CTO emulator spot-check) */
volatile int32_t g_fira_f3_out1 = 0;
volatile int32_t g_fira_f3_out2 = 0;
volatile int32_t g_fira_f3_out3 = 0;
/* F4b: single-channel bit-exact (fira_regression.c). Decls (defined in fira_regression.c). */
extern int      fira_r14_regression(uint32_t *out_crc);
extern volatile int      g_f4_mismatch_idx;  /* first subband-sample mismatch index (-1 = none) */
extern volatile int      g_f4_mismatch_sb;   /* which subband 0..3 of first mismatch (-1 = none) */
extern volatile int32_t  g_f4_core_val;      /* core (golden) value at first mismatch */
extern volatile int32_t  g_f4_fira_val;      /* FIRA path value at first mismatch */
extern volatile uint32_t g_f4_crc_core;      /* core SUBBAND CRC = live golden; self-check anchor 0x2E0D8C6E
                                              *   (NOT e2e 0x90556BC7; that is g_bench_result.crc32) */
/* F4b ratio-diagnostic dump (read on FAIL; idx0/coarse ~0 give no ratio -> use these substantial pairs).
 * sb3 (b=3) is the cleanest shift probe: ratio g_f4_probe_fira[3]/g_f4_probe_core[3] (core ref 0x0018CB1E). */
extern volatile int32_t  g_f4_probe_core[4]; /* first substantial core sample, per subband 0..3 */
extern volatile int32_t  g_f4_probe_fira[4]; /* paired FIRA value (ratio reveals >>shift / x2 / phase) */
extern volatile int      g_f4_probe_idx[4];  /* flattened sample index of probe, per subband */
extern volatile int32_t  g_f4_dump_core[32]; /* 32 consecutive sb3 core samples (DEC-PHASE FIX 2026-06-04: 8->32) */
extern volatile int32_t  g_f4_dump_fira[32]; /* paired FIRA sb3 samples (all-zero residual if fix correct) */
extern volatile int      g_f4_dump_idx0;     /* sb3 flattened index where the 32-sample dump starts */
volatile int      g_fira_f4_pass = -99;      /* F4b verdict: 1=PASS / 0=mismatch / -99 not-run */
volatile uint32_t g_fira_f4_crc  = 0;        /* F4b FIRA-subband CRC */

/* F5-A: 8-channel subband bit-exact (fira_regression.c). Per-channel readout (NO aggregate masking).
 *   Criterion is PER-CHANNEL subband: for each c, FIRA sb0..3 == core sb0..3 over chirp*w[c], and the
 *   live core CRC == the frozen per-channel golden g_f5_golden_crc[c] (dolph_f5_goldens.h, 8 DISTINCT). */
extern int      fira_r14_regression_8ch(void);
extern volatile int      g_f5_pass[8];          /* per channel 1=PASS/0=FAIL */
extern volatile uint32_t g_f5_crc_fira[8];      /* per channel FIRA subband CRC */
extern volatile uint32_t g_f5_crc_core[8];      /* per channel live core CRC (== frozen golden g_f5_golden_crc[c]) */
extern volatile int      g_f5_mismatch_sb[8];   /* per channel first-mismatch subband (-1 none) */
extern volatile int      g_f5_mismatch_idx[8];  /* per channel first-mismatch index (-1 none) */
extern volatile int32_t  g_f5_mismatch_core[8]; /* per channel core value at first mismatch */
extern volatile int32_t  g_f5_mismatch_fira[8]; /* per channel FIRA value at first mismatch */
extern volatile int      g_f5_pass_all;         /* convenience AND over channels (-99 not-run) */
extern volatile int      g_f5_fail_chan;        /* first failing channel (-1 none); selects the dump */
extern volatile int32_t  g_f5_dump_core[32];    /* first-failing-channel sb3 core 32-dump */
extern volatile int32_t  g_f5_dump_fira[32];    /* paired FIRA sb3 samples */
extern volatile int      g_f5_dump_idx0;        /* sb3 flattened index where the dump starts (-1 none) */
volatile int g_fira_f5_pass = -99;              /* F5-A overall verdict mirror: 1=all8 PASS/0=FAIL/-99 not-run */

/* F7: per-frame wall-cycle measurement + CCLK read (G6). RAW counters / Hz ONLY (no margin/benefit -- C9).
 *   Defined in fira_regression.c. Runs AFTER F4/F5 with its OWN setup/state/buffers (does NOT perturb
 *   the F4/F5 PASS paths). All g_f7_* are [L1/EZKIT] board-measured; ALL derived results (margin vs >=10x,
 *   FIRA-vs-core ratio) are [L4/to-verify] and MUST NOT enter selection until the CTO rules R14 CLOSED. */
extern int      fira_f7_measure(void);
extern volatile uint32_t g_f7_cyc_8ch_fira;     /* full 8ch FIRA path (analyze+synth) one steady frame, ALL overhead */
extern volatile uint32_t g_f7_cyc_8ch_core;     /* core-only 8ch (8 indep chains, NO sum; new F5-B semantic) same frame */
extern volatile uint32_t g_f7_cyc_1ch_fira;     /* one-channel FIRA (analyze+synth) steady frame (c=7 unity) */
extern volatile uint32_t g_f7_cyc_analyze_fira; /* one-channel FIRA analyze-only (overhead-breakdown split, c=7) */
extern volatile uint32_t g_f7_cyc_synth_fira;   /* one-channel FIRA synthesize-only (split, c=7) */
extern volatile uint32_t g_f7_cclk_hz;          /* measured core clock Hz (G6); 0 = not read / desktop */
extern volatile int      g_f7_valid;            /* 1 = ran on board with FIRA; 0 = desktop/no-FIRA (numbers meaningless) */
extern volatile int      g_f7_pwrinit_rc;       /* F7-FIX: adi_pwr_Init rc (0=SUCCESS); -99 not-run/desktop */
extern volatile int      g_f7_cclk_rc;          /* F7-FIX: adi_pwr_GetCoreClkFreq rc (0=SUCCESS); -99 not-run/desktop */
/* H1 (WO-S5-H1): focusing-increment + WCET combined measure (defined in sprint5/dsp/harness/h1_wcet_measure.c) */
extern int      h1_wcet_measure(void);
extern volatile uint32_t g_h1_cyc_8ch_focus, g_h1_cyc_8ch_nofocus, g_h1_cyc_focus_only;
extern volatile uint32_t g_h1_cyc_8ch_cold, g_h1_cyc_8ch_warm, g_h1_cyc_8ch_max, g_h1_cyc_8ch_min;
extern volatile uint32_t g_h1_cclk_hz, g_h1_focus_crc, g_h1_nofocus_crc;
extern volatile int      g_h1_cclk_rc, g_h1_fg_focus_differs, g_h1_fg_zero_recovers, g_h1_valid;
volatile int g_h1_done = -99;   /* 1=on-board w/ FIRA / 0=desktop no-FIRA / -99 not-run */
volatile int g_fira_f7_done = -99;              /* F7 measure ran: 1=on-board w/ FIRA / 0=desktop no-FIRA / -99 not-run */
#endif

/* ---- target CCNT read (true CCLK cycles) ----
 * Source: ADI ADSP-21569 example FIR_Throughput_21569.c:18-20,42,86-89 uses standard C
 *   clock() to count CCLK cycles (comment line 4 "measure the number of CCLK cycles ... on
 *   ADSP-21569"); Pipelined / *_Driver_Benchmark examples likewise. Underlying = REGF_EMUCLK
 *   32-bit core cycle counter (SHARC+ Core Programming Reference sec.29, user-space readable).
 * Width/wrap: clock_t 32-bit (example prints %d); @1GHz wraps ~4.29s. Per-frame (<2ms,
 *   ~1.3M cycles) far from wrap; bench_harness uses unsigned diff end-start (single wrap OK).
 *   Long accumulation needs EMUCLK2 (64-bit combined) or per-frame accumulate -- not needed here. */
#ifdef TARGET_SHARC
uint32_t bench_cyc_target(void)
{
    return (uint32_t)clock();   /* CCES SHARC: clock() = CCLK cycles (same as ADI 21569 example) */
}
#endif

void main(void)
{
    /* ---- ADI base: full board init (clock/power/pinmux/sru), keep unchanged ---- */
    adi_initComponents();

    /* ---- F7-FIX (board crash bbcf1fc root-cause): init the power service at STARTUP, right after
     *   adi_initComponents() and BEFORE any app code, mirroring the BSP exemplars' timing exactly
     *   (ADSP21569_DDR/src/main.c:28, Power_On_Self_Test/.../post.c:172, ADSP21569_UART/src/main.c:25
     *   all call adi_pwr_Init BEFORE the app runs).  RATIONALE: the FIRA-example adi_initComponents()
     *   (knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/ADSP_2156x_FIRA_Performance/
     *    system/adi_initialize.c -- body `result = adi_sec_Init(); return result;`) calls ONLY
     *   adi_sec_Init(); it does NOT init the power service.  Calling adi_pwr_GetCoreClkFreq later
     *   (F7, fira_f7_measure) on an UNINITIALIZED pwr service is the suspected NULL-vector fault.
     *   Doing the init ONCE here (not mid-run inside the measure function) removes any re-init hazard.
     *   Args: dev 0, CLKIN=25 MHz per the three exemplars (DDR main.h:56,59).  rc in g_f7_pwrinit_rc.
     *   DISCRIMINATOR: if the board STILL stops cleanly at adi_initComponents() (the line above) even
     *   WITH this startup pwr-init present, the fault is NOT the pwr call -> it cleanly indicts the
     *   link/startup hypothesis (a) (pulling adi_pwr into the link perturbed the generated startup /
     *   system.svc), NOT an uninitialized-pwr call. */
#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)
    g_f7_pwrinit_rc = (int)adi_pwr_Init(0u, 25u * 1000000u);
#endif

    /* ---- CCNT self-test (verify clock() reads true cycles; known 1,000,000 volatile loop) ----
     * emulator g_ccnt_selftest: should be >0 and ~ 1e6 * cycles-per-iter (order of M cycles);
     * 0 or erratic -> clock() not reading true CCNT, debug before trusting cyc_8ch_frame. */
    {
        volatile uint32_t k; uint32_t a, b;
        a = bench_cyc_target();
        for (k = 0u; k < 1000000u; k++) { }
        b = bench_cyc_target();
        g_ccnt_selftest = b - a;   /* known-loop cycle reference */
    }

    /* ---- our algorithm graft: run core-only S2-S5 harness (F0 baseline, kept) ---- */
    bench_run((BenchResult *)&g_bench_result);

#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    /* ---- F2 FIRA smoke: single-channel full Legacy lifecycle + Path B fixed-point (any coeffs) ----
     * F2 verdict = pipeline PASS: g_fira_f2_rc==0 (all 6 steps SUCCESS) + g_FIRTaskDoneCount==1 (cb).
     * NOTE: rc==0 does NOT prove SIGNED took effect (adi_fir_legacy_2156x.c: FixedPointEnable returns
     *   SUCCESS unless task RUNNING, independent of config macro) -> G2 true closure is F4 bit-exact
     *   vs golden, not F2.
     * rc codes: 1=Open 2=RegisterCallback 3=CreateTask
     *           4=FixedPointEnable (only non-SUCCESS if task==RUNNING = call-order bug; check order,
     *             DO NOT touch config)  5=QueueTask 6=Close / -1=real header undefined / -2=coeffs or buf null. */
    {
        /* F3: real coeff path (replaces F2 arbitrary-coeff smoke). Coeffs = frozen g_hb63_fira32
         *   (Q15 sign-extended, fir_coeffs_q31.h). Out buffer = out_count*3 (DP-01: 3x32-bit/sample). */
        static int32_t s_f2_in[63 + 64 - 1];     /* in_count = ntaps+out_count-1 = 126 */
        static int32_t s_f2_out[64 * 3];         /* DP-01: WINDOWSIZE*3 (LSW/MSW/overflow per sample) */
        unsigned i;
        for (i = 0u; i < (63u + 64u - 1u); i++) s_f2_in[i] = (int32_t)((uint32_t)i << 20);
        fira_tree_set_coeffs(g_hb63_fira32, FIR_HB63_FIRA_NTAPS);   /* F3 real coeffs */
        g_fira_f2_rc = fira_single_channel_template(s_f2_in, 63u + 64u - 1u,
                                                    s_f2_out, 64u, FIR_HB63_FIRA_NTAPS);
        /* expose output buffer head (3x32-bit of sample 0 + LSW of sample 1) for CTO emulator spot-check */
        g_fira_f3_out0 = s_f2_out[0]; g_fira_f3_out1 = s_f2_out[1];
        g_fira_f3_out2 = s_f2_out[2]; g_fira_f3_out3 = s_f2_out[3];
        /* breakpoint here: read g_fira_f2_rc / g_FIRTaskDoneCount / g_fira_f3_out* (verdict in DOC-S4-FIRA-IMPL-01) */
    }

    /* ---- F4b: single-channel SUBBAND bit-exact (FIRA decimate/interp + postscale vs core subbands) ----
     * Compares FIRA sb0..3 vs core sb0..3 (filter-dependent), NOT end-to-end out (telescoping-blind).
     * Runs AFTER the F3 smoke (sequenced; smoke does Open..Close, regression does its own Open..Close via
     *   fira_tree_setup/teardown; separate coeff stores + buffers -> no state clash).
     * PASS: g_fira_f4_pass==1  <=>  g_f4_mismatch_idx==-1 AND g_fira_f4_crc == g_f4_crc_core (the LIVE
     *   core-subband golden, == 0x2E0D8C6E). This is the filter-level criterion -- a placeholder FIRA
     *   (segs=0) FAILS it (unlike the retired e2e 0x90556BC7 test it could fool).
     * Self-check: g_f4_crc_core MUST == 0x2E0D8C6E (core-subband golden, desktop sbgold.c). If it differs,
     *   the core path / chirp / coeffs diverged on board -> diagnosis invalid, fix that first.
     *   (0x90556BC7 is the SEPARATE end-to-end check = g_bench_result.crc32, already PASS above.)
     * FAIL (expected first run, iterate postscale): read g_f4_mismatch_sb (which subband) / g_f4_mismatch_idx;
     *   then the ratio probe g_f4_probe_core[0..3] vs g_f4_probe_fira[0..3] (sb3 cleanest, core ref
     *   0x0018CB1E) + g_f4_dump_core[0..31]/g_f4_dump_fira[0..31] -> reveals missing >>shift / x2 / phase.
     *   DEC-PHASE FIX (2026-06-04): with the fix, g_f4_dump_fira == g_f4_dump_core (residual all-zero);
     *   if still even-phase the residual grows 0,-2,0,+2,0,-2,0,+6,...,0,-10,0,+22,... (predicted). */
    g_fira_f4_pass = fira_r14_regression((uint32_t *)&g_fira_f4_crc);
    /* breakpoint here: g_fira_f4_pass / g_fira_f4_crc / g_f4_crc_core(==0x2E0D8C6E) / g_f4_mismatch_sb /
     *   g_f4_mismatch_idx / g_f4_probe_core[] / g_f4_probe_fira[] / g_f4_dump_core[] / g_f4_dump_fira[] */

    /* ---- F5-A: 8-channel SUBBAND bit-exact (8 independent FIRA chains, per-channel Dolph weight) ----
     * Runs AFTER F4 (sequenced; its own fira_tree_setup/teardown; channel-major serial on the shared
     *   handle s_hFir -- 8ch x 9seg = 72 serial QueueTask, [ASSUME-A1] single-threaded, no shared-static
     *   overwrite window; fa[8] keep per-channel cross-frame history).
     * The Dolph -20dB weight w[c] (dolph_w8_q15.h) is applied at INPUT-SCALE on BOTH the FIRA and the
     *   core side, so the per-channel compare is apples-to-apples (weight INSIDE the bit-exact boundary).
     *
     * CRITERION = PER-CHANNEL subband (NOT a single constant). g_fira_f5_pass==1  <=>  for EVERY c:
     *   g_f5_pass[c]==1, i.e. g_f5_mismatch_idx[c]==-1 AND g_f5_crc_fira[c]==g_f5_crc_core[c]
     *   AND g_f5_crc_core[c]==g_f5_golden_crc[c]. A placeholder FIRA (segs=0) FAILs every channel.
     * SELF-CHECK ANCHOR = the 8 PER-CHANNEL goldens (dolph_f5_goldens.h), NOT a single constant:
     *   g_f5_crc_core[c] MUST equal g_f5_golden_crc[c]  ->  {0x8E807729, 0xB2F1E13F, 0x7B109C71,
     *   0xD7BD23E7, 0xA000D606, 0x2403E085, 0xB88D91B5, 0x2E0D8C6E} for c=0..7 (8 DISTINCT; c=7 unity
     *   == the F4 baseline 0x2E0D8C6E -> F4 continuity cross-check). If any g_f5_crc_core[c] differs from
     *   its golden, the core path/chirp/weight drifted on board -> diagnosis invalid, fix that first.
     * FAIL (iterate): g_f5_pass_all==0; read g_f5_fail_chan (first failing channel), then that channel's
     *   g_f5_mismatch_sb[c] / g_f5_mismatch_idx[c] / g_f5_mismatch_core[c] / g_f5_mismatch_fira[c], plus
     *   the sb3 32-dump g_f5_dump_core[0..31] vs g_f5_dump_fira[0..31] (idx0 = g_f5_dump_idx0). */
    g_fira_f5_pass = fira_r14_regression_8ch();
    /* breakpoint here: g_fira_f5_pass / g_f5_pass_all / g_f5_pass[0..7] / g_f5_crc_fira[0..7] /
     *   g_f5_crc_core[0..7] (== per-channel goldens above) / g_f5_fail_chan / g_f5_mismatch_sb[] /
     *   g_f5_mismatch_idx[] / g_f5_dump_core[] / g_f5_dump_fira[] */

    /* ---- F7: per-frame wall-cycle (full 8ch FIRA analyze+synth, ALL overhead) + core-only 8ch on the
     *   SAME frame + CCLK read (G6). Steady-state (warm-up frames then ONE measured frame). RAW NUMBERS
     *   ONLY -- the margin = (g_f7_cclk_hz * BENCH_FRAME/BENCH_FS) / g_f7_cyc_8ch_fira (criterion >=10x)
     *   and the FIRA-vs-core ratio are computed OFF-BOARD by PM/CTO; this code bakes in NO conclusion.
     *   Runs with its OWN FIRA setup/state/buffers AFTER F4/F5 -> does not perturb their PASS paths.
     *   C9 / iron rule 8: all derived results are [L4/to-verify], MUST NOT enter selection until R14 CLOSED.
     *   SEMANTIC CAVEAT (off-board): BOTH g_f7_cyc_8ch_fira and g_f7_cyc_8ch_core differ from the OLD
     *   1,006,935 cyc [L1/EZKIT, DEC-S4-R1-8CH-01] (that was the 8-in-1-out SUMMED-WCET incl. the
     *   cross-channel digital sum F5-B has since removed) -- do not ratio against it without noting this. */
    g_fira_f7_done = fira_f7_measure();
    /* breakpoint here: g_f7_valid (1=on-board) / g_f7_cclk_hz (G6, vs ~1GHz CGU + g_ccnt_selftest sanity) /
     *   g_f7_cyc_8ch_fira / g_f7_cyc_8ch_core / g_f7_cyc_1ch_fira / g_f7_cyc_analyze_fira / g_f7_cyc_synth_fira
     *   -> off-board: margin vs >=10x + FIRA-vs-core ratio, ALL [L4/to-verify] until CTO rules R14 closed. */

    /* ---- H1 (WO-S5-H1): focusing-increment same-build A/B + WCET cold/warm/max. Runs AFTER F7 with
     *   its OWN setup/state/buffers -> does NOT perturb F4/F5/F7 PASS paths. RAW counters only (C9).
     *   FREE-RUN: read g_h1_* at idle only (no mid-loop breakpoints). ---- */
    g_h1_done = h1_wcet_measure();
    /* breakpoint here (idle, after the run): read
     *   A focus increment: g_h1_cyc_8ch_focus - g_h1_cyc_8ch_nofocus (= g_h1_cyc_focus_only) [L1 cyc]
     *   B WCET (LOWER BOUND, cold=PARTIAL proxy I-cache warm): g_h1_cyc_8ch_cold/warm + g_h1_cyc_8ch_max/min
     *   C sanity: g_h1_cclk_hz(==1e9?)/g_h1_cclk_rc(==0?) + FG g_h1_fg_focus_differs(==1)/g_h1_fg_zero_recovers(==1)
     *   off-board: focus MCPS = increment*750/1e6; WCET multiplier = max/warm (lower-bound caveat); pair section-8 denom (C9). */

#endif

    /* ---- breakpoint here, emulator read g_bench_result:
     *   .bitexact_pass / .crc32 (== 0x90556BC7) / .cyc_8ch_frame / .mcps_8ch / .mcps_16ch_est
     *   -> S2 bit-exact [L1/EZKIT] + S3-S5 cycle/MCPS + R1 verdict (WCET<1.333ms and margin>=10x) ---- */

    while (1) { /* idle: keep results in memory for emulator */ }
}
