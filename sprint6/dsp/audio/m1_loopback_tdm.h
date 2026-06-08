/*
 * m1_loopback_tdm.h -- WO-S6-AUDIO M1 passthrough loopback (Stage-4 foundation) interface + readouts.
 *   ARCHITECTURE LOCKED: DEC-S6-M1-ARCH-01 (four openings, fb597f6). Re-vetted vs final spec (NOT the
 *   pre-arch draft): FRAME=64, block-rate 750Hz, fan-out 1->8 mono, TX=4096B, RX=512B (single-slot).
 *
 * ASCII-only. NEW file (sprint6/dsp/audio). Frozen files untouched (tree_filterbank.c / tfb_8ch.c /
 *   golden_ref.h / chirp_input.h / fir_coeffs_hb63.h / .ldf). RAW counters only (C9); margins off-board.
 *   FREE-RUN: read g_m1_* at idle only.
 *
 * Topology (DOC-S4-IO-01): ADAU1979 ADC -> SPORT4B(Rx) ; SPORT4A(Tx) -> ADAU1962A DAC -> 8 amps.
 *   ONE shared TDM bus: the DAC (master, DAC_CTRL1 SAI_MS=1) drives BCLK/FS for SPORT4A, SPORT4B AND the
 *   ADC (SRU routes DAI1_PB05/PB04 to all three, ALT.c:422-435). Master frame = TDM8, 8 slot x 32 bit @
 *   48k = 256 BCLK = 12.288 MHz.
 */
#ifndef M1_LOOPBACK_TDM_H
#define M1_LOOPBACK_TDM_H

#include <stdint.h>

/* ---- four-opening locked geometry (DEC-S6-M1-ARCH-01) ---- */
#define M1_FRAME          64u     /* (1) samples/frame -- FRAME=64 whole-chain base; block-rate=48000/64=750Hz */
#define M1_FS_HZ          48000u  /* 48 kHz */
#define M1_TX_SLOTS       8u      /* (2)(3) TX = TDM8 first-8 slots; fan-out 1 mono -> 8 identical TX slots */
#define M1_WORD_BYTES     4u      /* 32-bit slot word */

/* (3) RX single-slot: shared-bus master frame is TDM8 (8 slots); the RX SPORT MC window WSIZE matches the
 *   8-slot master frame, but CS enables ONLY slot0 and MCPDE=1 (packed) -> DMA writes 1 word/frame.
 *   M1_RX_SLOTS = CAPTURED (packed) slots, NOT the window width (the window stays 8 to match the bus frame).
 *   [board-confirm-CRITICAL fallback]: if the driver wrapper floors single-slot select at 2 (grep G1-G2),
 *   set M1_RX_SLOTS to 2 -> RX buffer auto-becomes 1024B; NO structural change (this macro is the ONLY knob). */
#define M1_RX_SLOTS       1u      /* captured RX slots (CTO-pinned 1 = 512B; fallback 2 = 1024B if driver floors) */

/* ping-pong buffer word counts (each ping-pong array holds TWO halves; see .c) */
#define M1_TX_HALF_WORDS  (M1_FRAME * M1_TX_SLOTS)   /* 64 x 8 = 512 words/half ; x4B x2 halves = 4096B (3) */
#define M1_RX_HALF_WORDS  (M1_FRAME * M1_RX_SLOTS)   /* 64 x 1 = 64 words/half  ; x4B x2 halves = 512B  (3) */

/* ---- entry points ---- */
int  m1_loopback_init(void);   /* codec + SPORT4 TDM ping-pong bring-up; 0 = ok, !=0 = honest fail */
int  m1_loopback_stop(void);   /* tear down SPORT + codec; 0 = ok */

/* ---- raw readouts (idle reads; raw counters ONLY -- C9). All g_m1_* are [L1-to-be] on board. ---- */
extern volatile uint32_t g_m1_rx_block_count;     /* RX ping-pong blocks serviced (FG: must grow w/ live codec) */
extern volatile uint32_t g_m1_tx_block_count;     /* TX blocks serviced */
extern volatile uint32_t g_m1_cb_cyc_last;        /* CCNT of the LAST callback body (io-callback core cost, raw) */
extern volatile uint32_t g_m1_cb_cyc_max;         /* max callback CCNT over the run (WCET of io-callback, raw) */
extern volatile uint32_t g_m1_cb_cyc_min;         /* min callback CCNT (jitter band) */
extern volatile uint32_t g_m1_nonzero_samples;    /* count of non-zero RX samples seen (FG: dead codec => 0) */
extern volatile uint32_t g_m1_max_abs_sample;     /* peak |RX sample| seen (FG: silence/dead-DMA detector) */
extern volatile int      g_m1_fg_stream_live;     /* 1 = blocks grew AND non-zero audio seen; 0 = FAIL; -99 not-run */
extern volatile int      g_m1_valid;              /* 1 = ran on board w/ codec+SPORT; 0 = desktop/no-board */

/* ---- M2 (FIRA beam in-loop) raw readouts -- WO-S6-M2 (DEC-S6-M2-ARCH-01). Defined in BOTH builds;
 *      on the M1 transparent build (M2_FIRA_INLOOP=0) they stay 0/sentinel (FIRA never ran). ---- */
extern volatile int      g_m2_fira_inloop;        /* 1 = built with FIRA beam in-loop; 0 = M1 passthrough */
extern volatile int      g_m2_setup_rc;           /* fira_tree_setup() rc (0=ok); -99 not-run/M1-build */
extern volatile uint32_t g_m2_out_nonzero;        /* count of non-zero FIRA TX output samples (FG: beam alive) */
extern volatile uint32_t g_m2_out_max_abs;        /* peak |FIRA TX output sample| (FG: silent-beam detector) */
extern volatile int      g_m2_fg_beam_live;       /* 1 = blocks grew AND FIRA output non-zero; 0 = FAIL; -99 not-run */
extern volatile int      g_m2_valid;              /* 1 = ran on board w/ FIRA beam in-loop; 0 = M1/desktop */

#endif /* M1_LOOPBACK_TDM_H */
