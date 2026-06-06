/*
 * h2_board_hooks_21569som.c -- WO-S5-H2 board-side hook implementation for the
 *   ADSP-21569-SOM (REV 1.1) + AD-EXKIT (V2.1), CCES 2.12.1, SHARC+ single core.
 *
 * Implements the 4 extern hooks declared in h2_dma_isr_measure.c (byte-for-byte prototypes):
 *     int  h2_busload_start(uint32_t bytes_per_s);  -- start MDMA mem-to-mem bus-load proxy (auto-refill)
 *     void h2_busload_stop(void);
 *     int  h2_isr_start(uint32_t hz);               -- install periodic timer ISR @hz (handler ++g_h2_isr_count + ack)
 *     void h2_isr_stop(void);
 *
 * ASCII-only. NEW board-only TU (NOT compiled on desktop -- the harness #else honest-0 path covers host).
 *   Frozen files untouched (only #includes BSP service headers + extern repo counters). RAW: the hooks
 *   create/destroy the load; they do NOT compute any derived margin (C9). All margins are off-board.
 *
 * ============================ SYMBOL PROVENANCE (the command of this WO) ============================
 *
 * TIMER ISR PATH -- [L1] PROVEN in a real 21569 example (resolves iface_survey G7):
 *   The GP-timer service <services/tmr/adi_tmr.h> installs its own interrupt internally and dispatches
 *   to a user callback. There is NO need to call adi_int_InstallHandler from application code.
 *   PROOF (real 21569 project, ADSP-21569 SHARC+ single core):
 *     knowledge_base/ezkit/vendor_docs/cces_examples/code/Power_On_Self_Test/common/source/TimerDelay.c
 *       :15  #include <services/tmr/adi_tmr.h>
 *       :22  ADI_TMR_HANDLE hTMR = NULL;
 *       :23  uint8_t TimerMemory[ADI_TMR_MEMORY];
 *       :28  void Timer_Callback(void *pCBParam, uint32_t nEvent, void *pArg) { ... ADI_TMR_EVENT_DATA_INT ... }
 *       :78  adi_tmr_Open(0, TimerMemory, ADI_TMR_MEMORY, Timer_Callback, NULL, &hTMR);
 *       :90  adi_tmr_SetWidth(hTMR, Width/2);
 *       :96  adi_tmr_SetDelay(hTMR, Width/2);
 *       :103 adi_tmr_Enable(hTMR, true);
 *       :115 adi_tmr_Close(hTMR);   (TimerDelayStop)
 *   So on 21569 SHARC+ the install symbol is the adi_tmr service callback, NOT a raw GIC adi_int handler.
 *   G7's adi_int.h/GIC concern was a SC589 (Cortex-A) language confusion -- it does NOT apply to the
 *   timer-service path used here. ==> ISR install symbol RULING: RESOLVED, [L1] (callback-dispatch).
 *
 *   ONE board-confirm gap (flagged, NOT faked): TimerDelay.c uses ADI_TMR_MODE_SINGLE_PWMOUT = a ONE-SHOT.
 *     For a PERIODIC (free-running) ISR at hz I need a CONTINUOUS PWM-out mode. The continuous-mode enum
 *     name (expected ADI_TMR_MODE_CONTINUOUS_PWMOUT, set via ADI_TMR_CFG_PARAMS / a SetMode-class call) is
 *     NOT present in the local evidence DB (only SINGLE_PWMOUT + PINT appear). I therefore re-arm the
 *     one-shot inside the callback (proven primitives only) so the same [L1] symbols give a periodic ISR;
 *     the cleaner continuous-mode enum is left as a TODO for bring-up to confirm against the installed
 *     adi_tmr.h in CCES 2.12.1. Either way the install/ack/count path is the proven service path.
 *
 * MDMA BUS-LOAD PATH -- [L1-header / board-confirm-usage]:
 *   The MDMA (memory-to-memory) service exists for 2156x and exposes adi_mdma_Copy1D / adi_mdma_CopyList.
 *   PROOF (symbol existence + config, real 21569 BSP):
 *     knowledge_base/ezkit/vendor_docs/cces_examples/code/Power_On_Self_Test/EZ-Board/21569/sharc/system/
 *       services/dma/adi_mdma_config_2156x.h
 *       :27  adi_mdma_Copy1D()   (named in ADI_MDMA_CFG_MSIZE_AUTO doc)
 *       :34  adi_mdma_CopyList() (named in ADI_MDMA_CFG_LIST_MULTIPLE_CALLBACKS_ENABLE doc)
 *       header <services/dma/adi_mdma.h> (the BSP service header that declares these; in CCES SHARC/include).
 *   No example in the local DB CALLS adi_mdma_Copy1D, so the exact ADI_MDMA_HANDLE / open / callback
 *   signatures are board-confirm [board] -- I code the documented shape and flag the line.
 *   Bus-class justification (proxy honesty) is in h2_dma_isr_measure.c header: MDMA loads the SAME
 *   system crossbar as the SPORT-PDMA path at the SAME aggregate byte rate (H2_DMA_BYTES_PER_S).
 *
 * I-CACHE INVALIDATE SYMBOL (asked to register in passing -- NOT used this WO):
 *   The only cache symbol in the local DB is flush_data_buffer(void*, void*, int) from <sys/cache.h>
 *   (DATA cache; H1's A5 symbol -- see sprint5/dsp/harness/guard_stub_inc/sys/cache.h). NO instruction-
 *   cache invalidate symbol was found in the offline evidence base. ==> I-cache invalidate symbol:
 *   STILL UNKNOWN, remains a C10 board item (consistent with H2_WORKORDER.md sec-8). Not resolved here.
 *
 * ================================ DESKTOP / NON-BOARD HONESTY ================================
 *   This TU is compiled ONLY in the board build (FIRA_USE_REAL_ADI_FIR_HEADER && TARGET_SHARC). It must
 *   NOT be added to the desktop/gcc source list. The hooks here NEVER fabricate a load: if a BSP open
 *   fails they return non-zero (busload/isr start) or no-op (stop) so the harness FG flags read the
 *   honest failure (FG=0), never a fake pass.
 */

#include <stdint.h>

#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)

#include <stddef.h>                 /* NULL */
#include <stdbool.h>
#include <services/tmr/adi_tmr.h>   /* [L1] adi_tmr_Open/SetWidth/SetDelay/Enable/Close, ADI_TMR_* (TimerDelay.c) */
#include <services/dma/adi_mdma.h>  /* [board-confirm] adi_mdma_Copy1D/CopyList (named in adi_mdma_config_2156x.h) */

/* The harness owns this counter; the timer ISR callback MUST bump it (FG-B cross-check). */
extern volatile uint32_t g_h2_isr_count;

/* ===================================================================================================
 * Block 1: BUSLOAD probe state (MDMA mem-to-mem proxy). Independent block; shares NO mutable state
 *   with the ISR probe (hard-rule 4 -- probe isolation). All decls at top (R16 declaration-order rule).
 * =================================================================================================== */

/* SCLK for descriptor-rate bookkeeping (21569-SOM core ~1 GHz; SCLK = SYSCLK domain feeding GP timer
 * and the DMA engine). TimerDelay.c uses SCLK_MHz 125 for its width math; reuse that class here. The
 * EXACT SCLK is a CGU/clock-tree value bring-up reads from adi_pwr -- left documented, not load-bearing
 * for correctness (the byte-rate target drives the descriptor count, see below). */
#define H2_BH_SCLK_HZ            125000000u

/* Bus-load descriptor sizing. The harness passes bytes_per_s = H2_DMA_BYTES_PER_S = 3,072,000 B/s
 *   (= 8 slot x 4 B x 48000 x 2 dir, the SPORT TDM aggregate -- the bus CLASS the proxy must match).
 * We push a continuous mem-to-mem MDMA: a fixed-size block copied back-to-back, auto-refilled in the
 * MDMA done callback until stop. The block size sets the per-transfer granularity; the AGGREGATE rate is
 * the MDMA engine running as continuously as the crossbar allows (MDMA runs at bus speed, so a
 * back-to-back chain SATURATES its share -- this is the worst-case contention the WCET wants, and it
 * meets-or-exceeds the 3.072 MB/s SPORT class; honest note: continuous MDMA can load MORE than the SPORT
 * average, so the measured contention is an UPPER bound on the SPORT-class share, which is conservative
 * for a worst-case WCET. Documented so the proxy direction is not silently optimistic). */
#define H2_BH_BLOCK_WORDS       1024u                       /* 1024 x 4B = 4096 B per copy work unit */
#define H2_BH_BLOCK_BYTES       (H2_BH_BLOCK_WORDS * 4u)

/* [board-confirm, R24 F24-MAJOR-1] PLACEMENT IS MEASUREMENT-VALIDITY CRITICAL: these buffers have NO
 * section pragma, so the linker decides where they land. Bring-up MUST pin them (section pragma or .ldf
 * input section) to the SAME bus segment the product SPORT-PDMA traverses, and NOT into the same L1
 * block as the FIRA working set (s_h2_fa) -- otherwise inc_dma measures self-conflict (an artifact the
 * product does not have) instead of crossbar contention. Check the .map placement BEFORE interpreting
 * any board reading. */
static uint32_t  s_bh_src[H2_BH_BLOCK_WORDS];               /* mem-to-mem source (off-stack, like s_h2_fa) */
static uint32_t  s_bh_dst[H2_BH_BLOCK_WORDS];               /* mem-to-mem destination */
static volatile int s_bh_active = 0;                        /* 1 = stream should keep auto-refilling */
static uint32_t  s_bh_bytes_per_s = 0u;                     /* requested aggregate rate (bookkeeping only) */

/* MDMA service handle + memory. ADI_MDMA_MEMORY / ADI_MDMA_HANDLE come from <services/dma/adi_mdma.h>.
 * [board-confirm]: the exact memory macro name + open signature are confirmed at bring-up against the
 * installed adi_mdma.h (no local example CALLS the API). Sized generously; bring-up trims. */
#ifndef ADI_MDMA_MEMORY
#define ADI_MDMA_MEMORY 256u   /* TODO[bring-up]: real value is in adi_mdma.h; this fallback only keeps
                                * this TU parseable if the macro name differs. Confirm + replace.
                                * [R24 F24-MINOR-2] SILENT-FALLBACK GUARD: on the BOARD build this fallback
                                * being used means the real header did not supply the value -> the service
                                * memory may be UNDERSIZED (open writes out of bounds). Bring-up MUST verify
                                * the macro comes from the installed adi_mdma.h, e.g. add next to the board
                                * hook TU:  #ifdef H2_BH_USED_FALLBACK_MDMA_MEMORY  #error "..."  #endif
                                * (define the marker in this #ifndef block) or grep the preprocessed output. */
#define H2_BH_USED_FALLBACK_MDMA_MEMORY 1  /* marker so the board build can #error if fallback active */
#endif
static uint8_t          s_bh_mdma_mem[ADI_MDMA_MEMORY];
static ADI_MDMA_HANDLE  s_bh_hmdma = NULL;

/* MDMA done callback: re-issue the next copy so the stream is CONTINUOUS until stop (auto-refill). This
 * is the "persist until stop" contract from hard-rule 2 (one-shot transfer != sustained bus pressure). */
static void h2_bh_mdma_callback(void *pCBParam, uint32_t nEvent, void *pArg)
{
    (void)pCBParam; (void)nEvent; (void)pArg;
    if (s_bh_active) {
        /* re-arm the same mem-to-mem block (back-to-back => sustained crossbar load).
         * [board-confirm] adi_mdma_Copy1D arg order/MSIZE/enum per adi_mdma.h at bring-up. */
        (void)adi_mdma_Copy1D(s_bh_hmdma, s_bh_dst, s_bh_src,
                              ADI_DMA_MSIZE_4BYTES, H2_BH_BLOCK_WORDS);
    }
}

int h2_busload_start(uint32_t bytes_per_s)
{
    uint32_t i;
    ADI_MDMA_RESULT r;        /* [board-confirm] result enum from adi_mdma.h */

    s_bh_bytes_per_s = bytes_per_s;     /* recorded only (RAW; no rate-vs-cycles math here -- C9) */

    /* init payload (any pattern; content is irrelevant to bus arbitration) */
    for (i = 0; i < H2_BH_BLOCK_WORDS; i++) s_bh_src[i] = 0xA5A5A5A5u + i;

    /* open the MDMA stream. [board-confirm] exact open signature per adi_mdma.h.
     * MDMA stream id 0 is the conventional first mem-to-mem stream. */
    r = adi_mdma_Open(0u, s_bh_mdma_mem, ADI_MDMA_MEMORY,
                      h2_bh_mdma_callback, NULL, &s_bh_hmdma);
    if (r != ADI_MDMA_SUCCESS) {
        s_bh_hmdma = NULL;
        return 1;   /* honest non-zero: no fake load -> harness FG-A reads 0 (BLOCKER), never faked */
    }

    s_bh_active = 1;
    /* kick the first copy; the done-callback re-arms continuously until h2_busload_stop. */
    r = adi_mdma_Copy1D(s_bh_hmdma, s_bh_dst, s_bh_src,
                        ADI_DMA_MSIZE_4BYTES, H2_BH_BLOCK_WORDS);
    if (r != ADI_MDMA_SUCCESS) {
        s_bh_active = 0;
        (void)adi_mdma_Close(s_bh_hmdma);
        s_bh_hmdma = NULL;
        return 1;
    }
    return 0;
}

void h2_busload_stop(void)
{
    s_bh_active = 0;                       /* stop the auto-refill first (callback sees this, won't re-arm) */
    if (s_bh_hmdma != NULL) {
        (void)adi_mdma_Close(s_bh_hmdma);  /* aborts any in-flight work unit + frees the stream */
        s_bh_hmdma = NULL;
    }
}

/* ===================================================================================================
 * Block 2: ISR probe state (periodic GP timer). Independent block; shares NO mutable state with the
 *   busload probe. All decls at top (R16).
 * =================================================================================================== */

#define H2_BH_ISR_SCLK_HZ       H2_BH_SCLK_HZ   /* same SYSCLK domain feeds the GP timer (TimerDelay.c) */

static ADI_TMR_HANDLE   s_bh_htmr = NULL;
static uint8_t          s_bh_tmr_mem[ADI_TMR_MEMORY];   /* [L1] ADI_TMR_MEMORY (TimerDelay.c:23) */
static volatile int     s_bh_isr_active = 0;            /* 1 = keep re-arming the one-shot for periodicity */
static uint32_t         s_bh_half_period = 0u;          /* width/delay halves (cycles) for re-arm */

/* Periodic timer callback. MUST: (a) ++g_h2_isr_count (FG-B cross-check), (b) ack the timer event,
 * (c) re-arm so the next interrupt fires (periodic, not one-shot). The adi_tmr service performs the
 * hardware IRQ ack as part of dispatching this callback (proven dispatch path, TimerDelay.c); the
 * re-arm below makes the one-shot SINGLE_PWMOUT behave periodically using ONLY proven primitives.
 * [R24 F24-MINOR-1] DRIFT DIRECTION, stated honestly: re-arm adds a software delay (IRQ -> callback ->
 * Enable) to every period, so the ACTUAL ISR rate is slightly BELOW the nominal hz -> g_h2_inc_isr is
 * the preemption cost at that slightly-lower rate, i.e. directionally an UNDER-estimate of the nominal-
 * rate cost (second-order: delta ~tens of cycles vs ~125k-cycle period, <<1%). Switching to
 * CONTINUOUS_PWMOUT at bring-up removes the drift entirely. */
static void h2_bh_timer_callback(void *pCBParam, uint32_t nEvent, void *pArg)
{
    (void)pCBParam; (void)pArg;
    switch ((ADI_TMR_EVENT)nEvent) {           /* [L1] ADI_TMR_EVENT / ADI_TMR_EVENT_DATA_INT (TimerDelay.c) */
    case ADI_TMR_EVENT_DATA_INT:
        g_h2_isr_count++;                      /* hard-rule 2: FG-B life line (must grow when ISR on) */
        if (s_bh_isr_active && s_bh_htmr != NULL) {
            /* re-arm one-shot for the next period (proven SetWidth/SetDelay/Enable primitives).
             * TODO[bring-up]: if adi_tmr.h in CCES 2.12.1 exposes ADI_TMR_MODE_CONTINUOUS_PWMOUT,
             * configure continuous mode once at start instead of re-arming here -- cleaner, lower
             * callback cost. Symbol not in local evidence DB, so kept as proven-primitive re-arm. */
            (void)adi_tmr_SetWidth(s_bh_htmr, s_bh_half_period);
            (void)adi_tmr_SetDelay(s_bh_htmr, s_bh_half_period);
            (void)adi_tmr_Enable(s_bh_htmr, true);
        }
        break;
    default:
        break;
    }
}

int h2_isr_start(uint32_t hz)
{
    ADI_TMR_RESULT r;                          /* [L1] ADI_TMR_RESULT / ADI_TMR_SUCCESS (TimerDelay.c) */
    uint32_t period_cycles, half;

    if (hz == 0u) return 1;                     /* honest reject (no fake ISR) */

    /* period in SYSCLK cycles; split into width+delay halves (PWMOUT model, TimerDelay.c). */
    period_cycles = H2_BH_ISR_SCLK_HZ / hz;     /* e.g. 125e6 / 1000 = 125000 cycles */
    if (period_cycles < 2u) return 1;           /* too fast for this SCLK -> honest reject */
    half = period_cycles / 2u;
    s_bh_half_period = half;

    r = adi_tmr_Open(0,                          /* GP timer 0 (TimerDelay.c uses instance 0) */
                     s_bh_tmr_mem, ADI_TMR_MEMORY,
                     h2_bh_timer_callback, NULL, &s_bh_htmr);
    if (r != ADI_TMR_SUCCESS) { s_bh_htmr = NULL; return 1; }

    s_bh_isr_active = 1;
    r = adi_tmr_SetWidth(s_bh_htmr, half);   if (r != ADI_TMR_SUCCESS) goto fail;
    r = adi_tmr_SetDelay(s_bh_htmr, half);   if (r != ADI_TMR_SUCCESS) goto fail;
    r = adi_tmr_Enable(s_bh_htmr, true);     if (r != ADI_TMR_SUCCESS) goto fail;
    return 0;

fail:
    s_bh_isr_active = 0;
    (void)adi_tmr_Close(s_bh_htmr);
    s_bh_htmr = NULL;
    return 1;
}

void h2_isr_stop(void)
{
    s_bh_isr_active = 0;                         /* stop re-arming first (callback won't re-enable) */
    if (s_bh_htmr != NULL) {
        (void)adi_tmr_Enable(s_bh_htmr, false);  /* disable before close (graceful) */
        (void)adi_tmr_Close(s_bh_htmr);          /* [L1] adi_tmr_Close (TimerDelay.c:115) */
        s_bh_htmr = NULL;
    }
}

#endif /* FIRA_USE_REAL_ADI_FIR_HEADER && TARGET_SHARC */
