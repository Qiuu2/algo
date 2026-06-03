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
extern volatile uint32_t g_FIRTaskDoneCount; /* defined in fira_tree.c (set by ALL_CHANNEL_DONE cb) */
volatile int g_fira_f2_rc = -99;             /* F2 single-channel template rc (emulator; 0=PASS) */
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
        static int32_t s_f2_coef[63];            /* F2 arbitrary coeffs (smoke only; F3 = real) */
        static int32_t s_f2_in[63 + 64 - 1];     /* in_count = ntaps+out_count-1 = 126 */
        static int32_t s_f2_out[64];             /* out_count = 64 (window) */
        unsigned i;
        for (i = 0u; i < 63u; i++) s_f2_coef[i] = 0;
        s_f2_coef[31] = (int32_t)0x40000000;     /* center tap (any nonzero) */
        for (i = 0u; i < (63u + 64u - 1u); i++) s_f2_in[i] = (int32_t)((uint32_t)i << 20);
        fira_tree_set_coeffs(s_f2_coef, 63u);
        g_fira_f2_rc = fira_single_channel_template(s_f2_in, 63u + 64u - 1u,
                                                    s_f2_out, 64u, 63u);
        /* breakpoint here: read g_fira_f2_rc / g_FIRTaskDoneCount (verdict in DOC-S4-FIRA-IMPL-01) */
    }
#endif

    /* ---- breakpoint here, emulator read g_bench_result:
     *   .bitexact_pass / .crc32 (== 0x90556BC7) / .cyc_8ch_frame / .mcps_8ch / .mcps_16ch_est
     *   -> S2 bit-exact [L1/EZKIT] + S3-S5 cycle/MCPS + R1 verdict (WCET<1.333ms and margin>=10x) ---- */

    while (1) { /* idle: keep results in memory for emulator */ }
}
