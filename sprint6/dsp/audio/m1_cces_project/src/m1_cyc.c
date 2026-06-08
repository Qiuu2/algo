/*
 * m1_cyc.c -- WO-S6-AUDIO-M1-PROJ: CCNT cycle probe for the io-callback measurement.
 *   The M1 independent project does NOT link bench_main, so it provides its own bench_cyc_target()
 *   (the io-callback CCNT bracket in m1_loopback_tdm.c calls it). Copied verbatim from bench_main.c:118.
 *
 * ASCII-only. RAW (returns raw cycles; no derived math here -- C9). [L1: CCES SHARC clock() = CCLK cycles,
 *   same as the ADI ADSP-21569 FIR_Throughput example; bench_main.c:108-122 provenance].
 */
#include <stdint.h>

#ifdef TARGET_SHARC
#include <time.h>            /* clock() -> CCLK cycles on CCES SHARC */
uint32_t bench_cyc_target(void)
{
    return (uint32_t)clock();   /* CCES SHARC: clock() = CCLK cycles (bench_main.c:118) */
}
#else
/* desktop: clock() is wall-ish, not CCNT; only for plumbing (g_m1_cb_cyc_* meaningless off-board) */
#include <time.h>
uint32_t bench_cyc_target(void)
{
    return (uint32_t)clock();
}
#endif
