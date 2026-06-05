/*
 * h2_dma_isr_measure.c -- WO-S5-H2: DMA bus-contention + ISR-preemption measurement harness.
 *   Closes the T2 (>=1.5x) system-side gap: turns the [L3] sec-8 io (5-30) / irq (2-15) / WCET-unmeasured
 *   (+10-50%) ALLOWANCES into [L1/EZKIT] board measurements, so the whole-system worst end (now 1.46x)
 *   can be lifted above 1.5x with real data.
 *
 * ASCII-only. NEW self-contained file (does NOT edit h1/fira_regression -- their PASS paths stay
 *   byte-identical). Frozen files untouched. RAW counters only (C9 analog; margins computed off-board).
 *   FREE-RUN: read g_h2_* at idle only (CCNT_source.md lesson; mid-loop breakpoints deadlock the loop).
 *
 * WHAT IT MEASURES (same-build A/B, ST1-E discipline -- every A/B differs in EXACTLY one factor):
 *   A. DMA bus-contention increment: 8ch FIRA frame cycles WITH a concurrent bus-load stream vs WITHOUT.
 *      g_h2_cyc_frame_dma  vs  g_h2_cyc_frame_base  ->  increment = the DMA contention cost [L1].
 *   B. ISR-preemption increment: 8ch FIRA frame cycles WITH a periodic timer ISR firing vs WITHOUT.
 *      g_h2_cyc_frame_isr  vs  g_h2_cyc_frame_base  ->  increment = the ISR cost [L1].
 *   C. Combined WCET: A+B active simultaneously, max-over-N frames -> the measured contention WCET
 *      multiplier g_h2_cyc_frame_both_max / g_h2_cyc_frame_base [L1] (I-cache cold still EXCLUDED).
 *   D. FG: prove the load is real (DMA-off control => zero increment; ISR counter cross-check).
 *
 * DMA STREAM = PROXY (CTO-approved): an MDMA (memory-to-memory) descriptor stream as a BUS-LOAD proxy,
 *   NOT the real ADAU codec SPORT path. WHY a proxy is acceptable + its bus-class equivalence:
 *   - The product DMA is SPORT4 TDM ping-pong (ADAU1979 in / ADAU1962A out, 8-slot 32-bit @48k =
 *     BCLK 12.288 MHz, DOC-S4-IO-01). Its CORE cost = the per-block RX/TX callback + descriptor
 *     service + cache-invalidate of the DMA buffer; its CONTENTION cost = the DMA engine stealing
 *     system-crossbar / L2 / external-mem bandwidth from the core.
 *   - The CONTENTION mechanism is bus arbitration on the SAME crossbar regardless of which DMA channel
 *     (SPORT-PDMA or MDMA) drives it. An MDMA stream sized to the SAME aggregate byte rate as the SPORT
 *     TDM (8 slot x 32 bit x 48 kHz x 2 dir = ~3.072 MByte/s ... in/out; see H2_DMA_BYTES_PER_S) loads the
 *     crossbar in the same class. So the MDMA proxy captures the CONTENTION increment honestly.
 *   - WHAT THE PROXY MISSES (stated, not hidden): the real SPORT path also has the per-block callback
 *     core cost (descriptor service + cache-inval) which MDMA-auto-refill does NOT incur; that callback
 *     core cost is the sec-8 item-1 "codec/IO DMA" share and is NOT the contention share. So this harness
 *     measures CONTENTION [L1] via the proxy; the CALLBACK core cost needs the real SPORT bring-up
 *     (a heavier harness / future) -- flagged. The combined io envelope (5-30) splits into
 *     contention (measured here) + callback (still [L3] until SPORT bring-up).
 *
 * ISR = a periodic timer ISR at the product-representative rate (justified): the v1 bare-metal product
 *   has (i) the audio FRAME ISR at FS/FRAME = 48000/64 = 750 Hz (the SPORT block-done rate, DOC-S4-IO-01
 *   ping-pong) + (ii) a low-rate control/UI tick (~1 kHz typical for a bare-metal control loop; no RTOS
 *   per the chip decision = no scheduler tick). We model the dominant preemptor = a ~1 kHz timer ISR
 *   doing a minimal handler (counter increment + ack). H2_ISR_HZ is the knob; default 1000.
 *
 * BOARD-SUPPLIED HOOKS (the CTO/bring-up wires these per the real BSP -- they are the C10 board items;
 *   the harness logic, A/B structure, FG, and counters are all here and desktop-verified):
 *   h2_busload_start()/stop()  -- start/stop the MDMA bus-load stream (BSP adi_mdma_* or PDMA descriptor).
 *   h2_isr_start(hz)/stop()    -- install/remove the periodic timer ISR at hz (BSP adi_tmr_* + the SHARC
 *                                 interrupt install; NOTE iface_survey G7: adi_int.h is ARM/GIC, SHARC
 *                                 side differs -> the install symbol is a board item, like the I-cache one).
 *   The ISR handler MUST increment g_h2_isr_count (the FG cross-check) and ack the timer.
 *   These are declared `extern` and provided in a board-only TU (h2_board_hooks_<board>.c, NOT in this
 *   repo). On desktop they are absent -> the #else honest-0 path returns 0 (FG2), like F7/H1.
 */
#include <stdint.h>
#include "tree_filterbank.h"   /* TreeChannelState, tfb_* (non-frozen header; frozen .c untouched) */
#include "fir_coeffs_hb63.h"   /* g_hb63_q15, FIR_HB63_NTAPS */
#include "bench_harness.h"     /* BENCH_FRAME / BENCH_FS / BENCH_NFR */
#include "dolph_w8_q15.h"      /* g_dolph_w8_q15[8], DOLPH_W8_NCH */
#include "fira_tree.h"         /* FiraChannelState, fira_* (FIRA+TARGET build only) */

extern const int32_t *bench_chirp_input(void);
extern uint32_t bench_cyc_target(void);

/* ---- H2 raw readouts (idle reads; raw counters ONLY -- C9 analog) ---- */
volatile uint32_t g_h2_cyc_frame_base     = 0u;  /* [L1-to-be] 8ch FIRA steady frame, NO dma NO isr (A/B baseline) */
volatile uint32_t g_h2_cyc_frame_dma      = 0u;  /* [L1-to-be] same frame WITH bus-load stream active (contention) */
volatile uint32_t g_h2_cyc_frame_isr      = 0u;  /* [L1-to-be] same frame WITH periodic ISR active (preemption) */
volatile uint32_t g_h2_cyc_frame_both_max = 0u;  /* [L1-to-be] max over N frames with BOTH active (contention WCET) */
volatile uint32_t g_h2_cyc_frame_both_min = 0u;  /* [L1-to-be] min over the same (jitter band) */
volatile uint32_t g_h2_inc_dma            = 0u;  /* [L1-to-be] = dma - base (DMA contention increment, raw) */
volatile uint32_t g_h2_inc_isr            = 0u;  /* [L1-to-be] = isr - base (ISR preemption increment, raw) */
volatile uint32_t g_h2_isr_count          = 0u;  /* [L1-to-be] ISR fire count (FG cross-check: must be > 0 when ISR on) */
volatile uint32_t g_h2_isr_count_off      = 0u;  /* [L1-to-be] ISR count during an ISR-OFF span (FG: must stay 0) */
volatile int      g_h2_fg_dma_loads       = -99; /* [L1-to-be] 1 = dma increment > 0 (bus really loaded); 0 = FAIL; -99 not-run */
volatile int      g_h2_fg_isr_fires       = -99; /* [L1-to-be] 1 = isr_count grew AND off-count stayed 0; 0 = FAIL; -99 not-run */
volatile int      g_h2_valid              = 0;   /* 1 = ran on board w/ FIRA + hooks; 0 = desktop/no-FIRA */

/* DMA proxy sizing: SPORT TDM aggregate byte rate (8 slot x 32 bit x 48 kHz, in+out) for the proxy to
 * match the bus class. = 8*4 bytes/slot-frame * 48000 * 2 dir = 3,072,000 bytes/s. The MDMA proxy stream
 * is sized to push ~this rate continuously (board hook honors it; documented so the proxy is honest). */
#define H2_DMA_BYTES_PER_S  3072000u
#define H2_ISR_HZ           1000u    /* periodic ISR rate (product control-tick class; justified in header) */
#define H2_WARM             4        /* warm-up frames (== H1/F7 discipline) */
#define H2_NFRAMES          64       /* frames swept for both-active WCET max/min */

#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)

/* ---- board-supplied hooks (provided in a board-only TU; C10 bring-up wires to real BSP) ---- */
extern int  h2_busload_start(uint32_t bytes_per_s); /* start MDMA bus-load proxy; 0=ok */
extern void h2_busload_stop(void);
extern int  h2_isr_start(uint32_t hz);              /* install periodic timer ISR (handler bumps g_h2_isr_count); 0=ok */
extern void h2_isr_stop(void);

/* ---- file-scope state: ALL decls at TOP, before any function (R16 hardening) ---- */
static FiraChannelState s_h2_fa[DOLPH_W8_NCH];

/* one 8ch FIRA steady frame (analyze->synthesize), same as the H1/F7 chain. RAW timing target. */
static void h2_fira_frame(const int32_t *xin,
                          int32_t *fsb0, int32_t *fsb1, int32_t *fsb2, int32_t *fsb3,
                          int32_t *fout, int32_t *xw)
{
    int c, i;
    for (c = 0; c < DOLPH_W8_NCH; c++) {
        const int32_t w = g_dolph_w8_q15[c];
        for (i = 0; i < BENCH_FRAME; i++)
            xw[i] = (int32_t)(((int64_t)w * (int64_t)xin[i]) >> 15);   /* input-scale weight (== f5_apply_w) */
        fira_tfb_analyze(&s_h2_fa[c], xw, BENCH_FRAME, fsb0, fsb1, fsb2, fsb3);
        fira_tfb_synthesize(&s_h2_fa[c], fsb0, fsb1, fsb2, fsb3, BENCH_FRAME, fout);
    }
}

/**
 * H2 DMA/ISR measure. Populates g_h2_* raw readouts. RAW ONLY (no derived margin -- C9).
 *   @return 1 if ran on board w/ FIRA + hooks; 0 desktop/no-FIRA/no-hooks (g_h2_* stay 0/sentinel, FG2).
 *   Runs AFTER F4/F5/F7/H1 with its OWN state/buffers -> does NOT perturb their PASS paths.
 *   FREE-RUN: read g_h2_* at idle only.
 */
int h2_dma_isr_measure(void)
{
    g_h2_cyc_frame_base = 0u; g_h2_cyc_frame_dma = 0u; g_h2_cyc_frame_isr = 0u;
    g_h2_cyc_frame_both_max = 0u; g_h2_cyc_frame_both_min = 0u;
    g_h2_inc_dma = 0u; g_h2_inc_isr = 0u;
    g_h2_isr_count = 0u; g_h2_isr_count_off = 0u;
    g_h2_fg_dma_loads = -99; g_h2_fg_isr_fires = -99; g_h2_valid = 0;

    if (fira_tree_setup() != 0) {
        return 0;   /* no FIRA on this host: honest 0 (FG2) */
    }
    {
        const int32_t *chirp = bench_chirp_input();
        int32_t fsb0[BENCH_FRAME/8], fsb1[BENCH_FRAME/4], fsb2[BENCH_FRAME/2], fsb3[BENCH_FRAME];
        int32_t fout[BENCH_FRAME], xw[BENCH_FRAME];
        uint32_t t0, t1, cyc, f;
        uint32_t isr0;
        int c;

        tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);
        for (c = 0; c < DOLPH_W8_NCH; c++) fira_channel_init(&s_h2_fa[c], BENCH_FRAME);

        /* warm-up (steady-state, no load) */
        for (f = 0; f < H2_WARM; f++)
            h2_fira_frame(&chirp[(f % (BENCH_NFR)) * BENCH_FRAME], fsb0, fsb1, fsb2, fsb3, fout, xw);

        /* ===== A/B baseline: NO dma, NO isr (the single reference all increments subtract) ===== */
        {
            const int32_t *xin = &chirp[H2_WARM * BENCH_FRAME];
            t0 = bench_cyc_target();
            h2_fira_frame(xin, fsb0, fsb1, fsb2, fsb3, fout, xw);
            t1 = bench_cyc_target();
            g_h2_cyc_frame_base = t1 - t0;
        }

        /* ===== A: DMA contention -- same frame WITH bus-load active (one factor differs) ===== */
        if (h2_busload_start(H2_DMA_BYTES_PER_S) == 0) {
            const int32_t *xin = &chirp[H2_WARM * BENCH_FRAME];   /* SAME input as baseline */
            t0 = bench_cyc_target();
            h2_fira_frame(xin, fsb0, fsb1, fsb2, fsb3, fout, xw);
            t1 = bench_cyc_target();
            g_h2_cyc_frame_dma = t1 - t0;
            h2_busload_stop();
        }
        g_h2_inc_dma = (g_h2_cyc_frame_dma > g_h2_cyc_frame_base)
                     ? (g_h2_cyc_frame_dma - g_h2_cyc_frame_base) : 0u;
        /* FG-A: the bus-load must actually inflate the frame (contention real). */
        g_h2_fg_dma_loads = (g_h2_cyc_frame_dma > g_h2_cyc_frame_base) ? 1 : 0;

        /* ===== FG isr-OFF control: count must stay 0 across a no-ISR span (placeholder-fails) ===== */
        isr0 = g_h2_isr_count;
        h2_fira_frame(&chirp[(H2_WARM + 1) * BENCH_FRAME], fsb0, fsb1, fsb2, fsb3, fout, xw);
        g_h2_isr_count_off = g_h2_isr_count - isr0;   /* MUST be 0 (no ISR installed yet) */

        /* ===== B: ISR preemption -- same frame WITH periodic ISR active (one factor differs) ===== */
        if (h2_isr_start(H2_ISR_HZ) == 0) {
            const int32_t *xin = &chirp[H2_WARM * BENCH_FRAME];   /* SAME input as baseline */
            isr0 = g_h2_isr_count;
            t0 = bench_cyc_target();
            h2_fira_frame(xin, fsb0, fsb1, fsb2, fsb3, fout, xw);
            t1 = bench_cyc_target();
            g_h2_cyc_frame_isr = t1 - t0;
            /* isr count grew during the timed frame == ISR really fired */
            g_h2_fg_isr_fires = ((g_h2_isr_count - isr0) > 0u && g_h2_isr_count_off == 0u) ? 1 : 0;
            h2_isr_stop();
        } else {
            g_h2_fg_isr_fires = 0;
        }
        g_h2_inc_isr = (g_h2_cyc_frame_isr > g_h2_cyc_frame_base)
                     ? (g_h2_cyc_frame_isr - g_h2_cyc_frame_base) : 0u;

        /* ===== C: combined WCET -- BOTH dma + isr active, max/min over N frames ===== */
        g_h2_cyc_frame_both_max = 0u; g_h2_cyc_frame_both_min = 0xFFFFFFFFu;
        if (h2_busload_start(H2_DMA_BYTES_PER_S) == 0 && h2_isr_start(H2_ISR_HZ) == 0) {
            for (f = 0; f < H2_NFRAMES; f++) {
                const int32_t *xin = &chirp[((H2_WARM + 2) + (f % (BENCH_NFR - (H2_WARM + 2)))) * BENCH_FRAME];
                t0 = bench_cyc_target();
                h2_fira_frame(xin, fsb0, fsb1, fsb2, fsb3, fout, xw);
                t1 = bench_cyc_target();
                cyc = t1 - t0;
                if (cyc > g_h2_cyc_frame_both_max) g_h2_cyc_frame_both_max = cyc;
                if (cyc < g_h2_cyc_frame_both_min) g_h2_cyc_frame_both_min = cyc;
            }
            h2_isr_stop();
            h2_busload_stop();
        }
        g_h2_valid = 1;
    }
    fira_tree_teardown();
    return 1;
}

#else  /* desktop / no-FIRA / no board hooks */
int h2_dma_isr_measure(void)
{
    /* honest 0: no FIRA + no board DMA/ISR on this host. g_h2_* stay 0/sentinel (FG2, never fake). */
    return 0;
}
#endif
