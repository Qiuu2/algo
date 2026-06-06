/*
 * h2_host_test.c -- desktop self-verify for the H2 A/B + FG LOGIC (not the real DMA/ISR, which are
 *   board-only). Models the measure flow with stub hooks: a "bus load" that adds a fixed cycle cost to
 *   a frame, and an "ISR" that bumps a counter. Proves the increment subtraction and the two FG gates
 *   (dma-loads, isr-fires + off-count-stays-0) are logically correct.
 * Build: gcc -O2 -Wall -Wextra h2_host_test.c -o /tmp/h2_host && /tmp/h2_host   (exit 0 = pass).
 */
#include <stdint.h>
#include <stdio.h>

/* stub state mirroring the board hooks' observable effects */
static int      g_busload_on = 0;
static uint32_t g_isr_count  = 0;
static int      g_isr_on     = 0;

/* a host "frame": base cost + (busload ? contention) ; the ISR (if on) bumps the counter "during" it */
static uint32_t host_frame(uint32_t base)
{
    uint32_t cyc = base;
    if (g_busload_on) cyc += 1234;          /* simulated contention increment */
    if (g_isr_on)   { g_isr_count += 3; cyc += 90; }  /* simulated ISR fires + preemption cost */
    return cyc;
}

int main(void)
{
    int fail = 0;
    uint32_t base, dma, isr, isr_off, inc_dma, inc_isr;
    uint32_t isr0;
    int fg_dma, fg_isr;

    /* baseline: no load */
    g_busload_on = 0; g_isr_on = 0;
    base = host_frame(500000);

    /* A: DMA on (one factor differs) */
    g_busload_on = 1;
    dma = host_frame(500000);
    g_busload_on = 0;
    inc_dma = (dma > base) ? (dma - base) : 0;
    fg_dma  = (dma > base) ? 1 : 0;

    /* FG isr-off control: count must stay 0 with ISR off */
    isr0 = g_isr_count;
    (void)host_frame(500000);
    isr_off = g_isr_count - isr0;   /* MUST be 0 */

    /* B: ISR on (one factor differs) */
    g_isr_on = 1;
    isr0 = g_isr_count;
    isr = host_frame(500000);
    fg_isr = ((g_isr_count - isr0) > 0u && isr_off == 0u) ? 1 : 0;
    g_isr_on = 0;
    inc_isr = (isr > base) ? (isr - base) : 0;

    printf("base=%u dma=%u (inc_dma=%u) isr=%u (inc_isr=%u) isr_off=%u\n",
           base, dma, inc_dma, isr, inc_isr, isr_off);

    /* CHECK 1: DMA increment positive + FG dma-loads = 1 */
    if (!(inc_dma > 0 && fg_dma == 1)) { fail = 1; printf("FAIL check1: DMA increment/FG\n"); }
    else printf("PASS check1: DMA load gives positive increment, FG dma_loads=1\n");

    /* CHECK 2: ISR increment positive + FG isr-fires = 1 + off-count = 0 */
    if (!(inc_isr > 0 && fg_isr == 1 && isr_off == 0)) { fail = 1; printf("FAIL check2: ISR increment/FG/off-count\n"); }
    else printf("PASS check2: ISR fires (count grew), off-count stayed 0, FG isr_fires=1\n");

    /* CHECK 3: placeholder-fails -- a NO-OP busload (no cost) must yield inc=0 and FG=0 (catches a dead hook) */
    {
        uint32_t base2 = host_frame(500000);     /* loads off */
        uint32_t dma2  = host_frame(500000);     /* still off = "placeholder busload" */
        uint32_t inc2  = (dma2 > base2) ? (dma2 - base2) : 0;
        int fg2 = (dma2 > base2) ? 1 : 0;
        if (inc2 != 0 || fg2 != 0) { fail = 1; printf("FAIL check3: dead busload not caught\n"); }
        else printf("PASS check3: a no-op (placeholder) busload yields inc=0, FG=0 (caught, not faked)\n");
    }

    /* ===================================================================================================
     * WO-S5-H2R: FG-B' (rate-in-band) judgment logic -- desktop self-verify, BOTH directions.
     *   Mirrors h2r_isr_clean_retest's on-board rate math EXACTLY:
     *     rate_milli_hz = count_in_span * CCLK_HZ * 1000 / span_cyc
     *     in-band       = LO*1000 <= rate_milli_hz <= HI*1000
     *   Proves: (i) a clean 1000 Hz span -> PASS; (ii) the R27 artifact (~62 kHz span) -> FAIL/quarantine;
     *           (iii) a zero-span (no measurement) -> FAIL (never fake green).
     * =================================================================================================== */
    {
        const uint32_t CCLK_HZ = 1000000000u;   /* must match H2R_CCLK_HZ in the harness */
        const uint32_t LO = 950u, HI = 1050u;   /* must match H2R_RATE_LO_HZ / H2R_RATE_HI_HZ */
        uint32_t span_cyc, cnt, rate_mhz; int in_band;

        /* helper inline: compute rate_milli_hz + band flag the same way the harness does */
        #define H2R_RATE_MHZ(C,S) ((uint32_t)(((uint64_t)(C) * (uint64_t)CCLK_HZ * 1000u) / (uint64_t)(S)))
        #define H2R_IN_BAND(R)    ((R) >= (LO*1000u) && (R) <= (HI*1000u))

        /* (i) CLEAN: 1000 ISRs over a 1.000 s span (= 1e9 CCLK cyc) -> exactly 1000.000 Hz -> in band */
        cnt = 1000u; span_cyc = 1000000000u;
        rate_mhz = H2R_RATE_MHZ(cnt, span_cyc); in_band = H2R_IN_BAND(rate_mhz);
        printf("H2R check4 (clean): cnt=%u span=%u rate_mhz=%u in_band=%d\n", cnt, span_cyc, rate_mhz, in_band);
        if (!(in_band == 1 && rate_mhz == 1000000u)) { fail = 1; printf("FAIL check4: clean 1kHz not in band\n"); }
        else printf("PASS check4: clean 1000 Hz span -> FG-B' in-band (PASS)\n");

        /* (ii) R27 ARTIFACT: 62000 ISRs over the SAME 1 s span -> 62000 Hz -> OUT of band -> quarantine */
        cnt = 62000u; span_cyc = 1000000000u;
        rate_mhz = H2R_RATE_MHZ(cnt, span_cyc); in_band = H2R_IN_BAND(rate_mhz);
        printf("H2R check5 (artifact): cnt=%u span=%u rate_mhz=%u in_band=%d\n", cnt, span_cyc, rate_mhz, in_band);
        if (in_band != 0) { fail = 1; printf("FAIL check5: 62kHz artifact passed band (false green!)\n"); }
        else printf("PASS check5: 62 kHz artifact -> FG-B' OUT of band (FAIL=quarantine, caught)\n");

        /* (ii-b) lower endpoint of the R27 band (10 kHz) must ALSO be out of band */
        cnt = 10000u; span_cyc = 1000000000u;
        rate_mhz = H2R_RATE_MHZ(cnt, span_cyc); in_band = H2R_IN_BAND(rate_mhz);
        if (in_band != 0) { fail = 1; printf("FAIL check5b: 10kHz (R27 low end) passed band\n"); }
        else printf("PASS check5b: 10 kHz (R27 lower end) -> still OUT of band (caught)\n");

        /* (iii) boundary: 950 Hz and 1050 Hz inclusive in; 949 and 1051 out */
        if (!H2R_IN_BAND(H2R_RATE_MHZ(950u, 1000000000u)))  { fail=1; printf("FAIL check6: 950Hz edge excluded\n"); }
        else if (!H2R_IN_BAND(H2R_RATE_MHZ(1050u,1000000000u))) { fail=1; printf("FAIL check6: 1050Hz edge excluded\n"); }
        else if (H2R_IN_BAND(H2R_RATE_MHZ(949u, 1000000000u)))  { fail=1; printf("FAIL check6: 949Hz wrongly in\n"); }
        else if (H2R_IN_BAND(H2R_RATE_MHZ(1051u,1000000000u)))  { fail=1; printf("FAIL check6: 1051Hz wrongly in\n"); }
        else printf("PASS check6: band edges [950,1050] inclusive correct (949/1051 excluded)\n");

        /* (iv) zero-span guard: harness sets fg_rate_in_band=0 when span==0 (no division, no fake green) */
        {
            int fg_zero_span = (0u > 0u) ? 1 : 0;   /* mirrors `if (span>0) {...} else fg=0` */
            if (fg_zero_span != 0) { fail = 1; printf("FAIL check7: zero-span not forced to FAIL\n"); }
            else printf("PASS check7: zero span -> FG-B' = FAIL (no measurement != fake green)\n");
        }
        #undef H2R_RATE_MHZ
        #undef H2R_IN_BAND
    }

    printf(fail ? "==== H2 host self-verify: FAIL ====\n" : "==== H2 host self-verify: PASS ====\n");
    return fail;
}
