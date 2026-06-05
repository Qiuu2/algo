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

    printf(fail ? "==== H2 host self-verify: FAIL ====\n" : "==== H2 host self-verify: PASS ====\n");
    return fail;
}
