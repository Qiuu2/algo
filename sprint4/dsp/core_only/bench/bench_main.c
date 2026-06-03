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
extern volatile uint32_t g_f4_crc_core;      /* core chain CRC (self-check: must == 0x90556BC7) */
volatile int      g_fira_f4_pass = -99;      /* F4b verdict: 1=PASS / 0=mismatch / -99 not-run */
volatile uint32_t g_fira_f4_crc  = 0;        /* F4b FIRA-chain CRC */
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

    /* ---- F4b: single-channel bit-exact (FIRA+postscale full chain vs core golden 0x90556BC7) ----
     * Runs AFTER the F3 smoke (sequenced; smoke does Open..Close, regression does its own Open..Close;
     *   separate coeff stores (FIRA g_hb_fira vs core g_hb63_q15) + separate buffers -> no state clash).
     * PASS: g_fira_f4_pass==1 (g_f4_mismatch_idx==-1 AND g_fira_f4_crc==0x90556BC7).
     * FAIL (expected, iterate): emulator reads g_f4_mismatch_idx / g_f4_core_val / g_f4_fira_val
     *   (first diverging sample: index, core golden value, FIRA value) -> drives postscale tuning.
     * Self-check: g_f4_crc_core MUST == 0x90556BC7 (harness/golden intact, else diagnosis invalid). */
    g_fira_f4_pass = fira_r14_regression((uint32_t *)&g_fira_f4_crc);
    /* breakpoint here: g_fira_f4_pass / g_fira_f4_crc / g_f4_mismatch_idx / g_f4_core_val / g_f4_fira_val / g_f4_crc_core */
#endif

    /* ---- breakpoint here, emulator read g_bench_result:
     *   .bitexact_pass / .crc32 (== 0x90556BC7) / .cyc_8ch_frame / .mcps_8ch / .mcps_16ch_est
     *   -> S2 bit-exact [L1/EZKIT] + S3-S5 cycle/MCPS + R1 verdict (WCET<1.333ms and margin>=10x) ---- */

    while (1) { /* idle: keep results in memory for emulator */ }
}
