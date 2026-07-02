/*
 * m1_main.c -- WO-S6-AUDIO-M1-PROJ: thin main for the M1 independent audio project (route B).
 *   Sound in -> same sound out passthrough. NO FIRA / compute line (that stays in the frozen bench).
 *
 * ASCII-only. board-guarded body; desktop builds a no-op main so the TU compiles on host (honest).
 * FREE-RUN: the audio streams in the SPORT ping-pong callback; main idles. Read g_m1_* at idle only
 *   (F2 free-run discipline; no breakpoints inside the callback).
 *
 * POWER-UP ORDER (matters -- DAC is the bus master, its clocks must be stable before SPORT enable):
 *   1. adi_initComponents()  -- ADI base (clock/pinmux/sru-gen/system) [bench_main.c:127]
 *   2. adi_pwr_Init()        -- power service at STARTUP, before app code (F7-FIX) [bench_main.c:130]
 *   3. m1_sru_init()         -- SRU audio routing (R39 table)
 *   4. m1_softconfig_enable_codecs() -- EXPLICIT carrier codec enable (F-SRU-1; NOT carrier default)
 *   5. m1_loopback_init()    -- TWI codec PLL+regs (DAC master FIRST), then SPORT4 TDM ping-pong + cb
 *   6. while(1) idle         -- audio flows in the callback; read g_m1_* at idle. M2 build (WO-S6-M2FIX):
 *      the loop also services m2_beam_poll() -- the FIRA beam runs HERE in main context, NOT in the ISR
 *      (fira_tree.c:481 spin in the SPORT SEC ISR starved FIR DONE -> deadlock; #if-guarded, M1 byte-same)
 * (m1_loopback_init itself does codec-config-before-SPORT-enable internally, so the DAC master clocks
 *  are programmed before the SPORT halves are enabled.)
 */
#include <stdint.h>
#include "m1_loopback_tdm.h"

#if defined(M1_TARGET_BOARD) && defined(TARGET_SHARC)

#include "adi_initialize.h"             /* adi_initComponents() */
#include <services/pwr/adi_pwr.h>       /* adi_pwr_Init (bench_main.c:33) */

extern void m1_sru_init(void);                 /* m1_sru.c */
extern int  m1_softconfig_enable_codecs(void); /* m1_softconfig.c */

/* readouts that mirror the M1 status (idle reads only) -- exposed for JTAG/debugger inspection. */
volatile int g_m1_main_pwrinit_rc = -99;   /* adi_pwr_Init rc */
volatile int g_m1_main_softcfg_rc = -99;   /* codec-enable rc (0=ok) */
volatile int g_m1_main_init_rc    = -99;   /* m1_loopback_init rc (0=ok) */

void main(void)
{
    /* 1. ADI base init (clock/pinmux/sru-gen/system) */
    adi_initComponents();

    /* 2. power service at startup, before any app code (F7-FIX: avoids uninit-pwr NULL-vector fault).
     *    CLKIN = 25 MHz per the BSP exemplars (bench_main.c:130). */
    g_m1_main_pwrinit_rc = (int)adi_pwr_Init(0u, 25u * 1000000u);

    /* 3. SRU audio routing (R39 table: DAC master clocks -> SPORT4A/4B + ADC; data SPT4A->DAC, ADC->SPT4B) */
    m1_sru_init();

    /* 4. EXPLICIT carrier codec enable (F-SRU-1 hard constraint -- NOT carrier default; ALT's was dead-code) */
    g_m1_main_softcfg_rc = m1_softconfig_enable_codecs();

    /* 5. codec (DAC master first) + SPORT4 TDM ping-pong bring-up; arms the RX-done callback */
    g_m1_main_init_rc = m1_loopback_init();

#if M2_STATIC_TXTEST
    /* DIAGNOSTIC (EXP_STATIC_TXTEST.md): freeze BOTH TX halves to a static in-phase Dolph 2250Hz tone.
     * With m2_beam_poll() #if-skipped below, nothing rewrites TX -> the DMA re-transmits a fixed
     * waveform forever -> tearing (A) impossible by construction (isolates A vs B). Requires
     * M2_FIRA_INLOOP=1. Brief <3ms startup transient (TX was zeroed in init), then static. */
    m2_static_txtest_fill();
#endif

    /* 6. FREE-RUN idle: audio flows in m1_sport_rx_callback (fan-out 1->8 + io-callback CCNT probe + FG).
     *    Read g_m1_valid / g_m1_fg_stream_live / g_m1_rx_block_count / g_m1_cb_cyc_* at idle (no mid-loop
     *    breakpoints -- F2). A debugger halt here sees a consistent snapshot. */
    while (1) {
        /* nothing -- the DMA + callback do the work. (No printf in the hot path; RAW counters only.) */
#if M2_FIRA_INLOOP
        /* WO-S6-M2FIX (M2 build ONLY -- this block preprocesses away on the M1 transparent build, so the
         * M1 binary is byte-identical): service the deferred FIRA beam frame from MAIN context. The
         * SPORT RX-done ISR no longer computes (its fira_tree.c:481 busy-wait starved the FIR DONE
         * interrupt -> first-frame deadlock); it publishes the half and m2_beam_poll computes it here,
         * where the FIR DONE interrupt CAN preempt and release the spin (H1/H2-verified context). */
#if !M2_STATIC_TXTEST
        m2_beam_poll();
#else
        (void)0;   /* M2_STATIC_TXTEST diagnostic: poll SKIPPED so nothing overwrites the frozen TX buffer */
#endif
#endif
    }
}

#else  /* desktop: no board -- compile-only main (honest, does nothing) */
int main(void)
{
    (void)m1_loopback_init();   /* desktop honest-0 path inside (returns non-zero) */
    (void)m1_loopback_stop();
    return 0;
}
#endif
