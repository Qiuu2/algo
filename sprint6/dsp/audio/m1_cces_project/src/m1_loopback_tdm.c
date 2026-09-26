/*
 * m1_loopback_tdm.c -- WO-S6-AUDIO M1: ADAU1979 -> SPORT4 TDM -> 21569 -> SPORT4 -> ADAU1962A passthrough.
 *   Stage-4 foundation: sound in -> same sound out. M2 inserts the beamformer where M1 fans out 1->8.
 *   ARCHITECTURE LOCKED: DEC-S6-M1-ARCH-01 (fb597f6). This file is REWRITTEN against the final four
 *   openings -- the pre-arch draft (256-frame, 4->8 copy, blind 0x1B) was used only as symbol material;
 *   every spec-bearing value below follows the locked openings + D5 per-bit decode (see DRAFT-DIFF notes).
 *
 * ASCII-only. NEW board-side TU. Frozen files untouched (tree_filterbank.c / tfb_8ch.c / golden_ref.h /
 *   chirp_input.h / fir_coeffs_hb63.h / .ldf). RAW counters only (C9); margins off-board. FREE-RUN.
 *
 * ===== FOUR OPENINGS (DEC-S6-M1-ARCH-01) =====
 *   (1) block-rate = 750 Hz, FRAME = 64 samples/frame (M1_FRAME).
 *   (2) fan-out = 1 mono RX slot -> 8 identical TX slots (M1 copies; beamform deferred to M2).
 *   (3) TX buffer = 4096B (8 slot x 64 x 4B x pingpong2); RX buffer = 512B (1 captured slot x 64 x 4B x 2).
 *   (4) M1 no-pin (no FIRA working set in this build); buffers default to L1 Block 0.
 *
 * ===== RX 512B = THREE-LAYER CONFIG (CTO opening 3; shared-bus reasoning) =====
 *   The DAC is the TDM bus master (DAC_CTRL1 SAI_MS=1) driving ONE frame = TDM8 (8 slot, 256 BCLK, 48k)
 *   onto BCLK/FS shared by SPORT4A, SPORT4B and the ADC (SRU DAI1_PB05/PB04 -> all three, ALT.c:422-435).
 *   So the RX SPORT sees an 8-slot master frame. RX 512B is achieved by THREE independent layers:
 *     LAYER-1 WINDOW (WSIZE): RX MC window = 8 slots (WSIZE arg = M1_TX_SLOTS-1) to MATCH the master frame.
 *       (Shrinking the window below the master frame is NOT valid -- the FS period is the master's TDM8.)
 *     LAYER-2 CHANNEL-SELECT (CS): enable ONLY slot 0 -> adi_sport_SelectChannel(hRx, 0u, M1_RX_SLOTS-1u)
 *       = (0u,0u) for 1 slot. [board-confirm-CRITICAL: HRM proves slot0-only is HARDWARE-legal (WSIZE/CS
 *       are independent, R36); the DRIVER WRAPPER may floor select at 2 -> CTO board-grep G1-G2. If it
 *       floors, bump M1_RX_SLOTS to 2 (-> 1024B) -- the ONLY change needed, no structural edit.]
 *     LAYER-3 PACKING (MCPDE=1): packed DMA writes ONE word per ENABLED channel (HRM: packed buffer =
 *       enabled-channel count), so 1 enabled slot -> 1 word/frame -> 64 words/half -> 512B over 2 halves.
 *       MCPDE is set by the BSP sport config (adi_sport_config MCPDE=1u); the driver honors it via MC mode.
 *
 * PROVENANCE: primary [L1] reference = Audio_Loopback_TDM (ALT.c, real 21569 ADAU1979->SPORT4->ADAU1962A);
 *   every adi_sport_/adi_twi_/adi_spu_/ADI_PDMA_ symbol is example-called (M1_FACT_BASE sec 2, ALT.c lines).
 *
 * CACHE COHERENCY (CLAUDE.md IO1): 21569 L1 RAM is NOT data-cached for the core (DM/PM caches serve
 *   external/L2 only). Buffers live in L1 (opening 4 default) -> NO core flush/invalidate needed (ALT does
 *   none for the same reason). Hook M1_BUFFERS_IN_CACHED_MEM wires flush_data_buffer if ever moved off L1.
 */
#include <stdint.h>
#include "m1_loopback_tdm.h"

/* ============================================================================================
 * WO-S6-M2 FIRA BEAM IN-LOOP (broadside v1, DEC-S6-M2-ARCH-01, CTO 5 openings, 2026-06-08)
 * ------------------------------------------------------------------------------------------
 * COMPILE SWITCH M2_FIRA_INLOOP selects the callback datapath WITHOUT losing M1's board-PASS:
 *   #if M2_FIRA_INLOOP -> callback does 1 mono RX frame -> 8ch FIRA broadside beam -> 8 TX slots.
 *   #else (default)    -> the unchanged M1 fan-out 1->8 passthrough (M1 board-PASS path, R37/R38).
 * Same project builds M1(transparent) or M2(FIRA) by defining/not-defining M2_FIRA_INLOOP.
 *
 * FIVE LOCKED OPENINGS (CTO, do not re-open):
 *   (1) granularity = whole-frame rebuild: per-frame 64-sample RX -> 8ch FIRA -> 8-slot interleave TX.
 *   (2) buffer pin = L1 Block 1: FIRA working set s_m2_fa + SPORT buffers s_m1_rx_buf/s_m1_tx_buf
 *       pinned to seg_l1_block1 (away from Block 0; R24 self-conflict lesson). See .ldf + pragmas below.
 *   (3) O1 EQ = NOT in M2 (minimal path).
 *   (4) beam weight = broadside (+0): input-scale Dolph Q15 weight only (already in the core), NO
 *       frac-delay focusing (focusing deferred to v2). Mirrors the H2 8ch frame model
 *       (h2_dma_isr_measure.c:115-120): per ch xw = w*xin (Q15 x Q31 >> 15) -> analyze -> synthesize,
 *       8 ch independent, NO cross-channel sum (product = 8 DACs, acoustic superposition).
 *   (5) Q boundary = ZERO-TRANSFORM identity: 24-bit left-aligned IS legal Q31 (R46 bit-exact run
 *       evidence), RX/TX with NO shift / NO mask. board-confirm SPORT alignment (HRM + g_m1_rx_buf
 *       dump); if RIGHT-aligned -> RX<<8 / TX>>8 (R46 mechanical discriminant). See M2_Q_BOUNDARY note.
 *
 * FROZEN ZERO-TOUCH (M2 only CALLs these; never edits): tree_filterbank.c / tfb_8ch.c / fira_tree.c /
 *   golden_ref.h / chirp_input.h / fir_coeffs_hb63.h / sprint4 .ldf. M2 calls fira_tree.h entry points
 *   (fira_tree_setup/tfb_set_coeffs/fira_channel_init x8 init; per-frame per-ch fira_tfb_analyze->
 *   synthesize) -- the SAME call sequence as the H2 harness (h2_dma_isr_measure.c:138-150,115-120).
 *   PROJECT WIRING (board/import, NOT a code edit): the M2 build must add the sprint4 include dirs
 *   (dsp/fira, dsp/core_only/src, dsp/core_only/include, dsp/core_only/bench) and LINK the frozen
 *   sources fira_tree.c / tree_filterbank.c / tfb_8ch.c. This is an import-time .cproject/source-link
 *   step (CTO action list), kept OUT of this TU so M1's transparent build needs none of it.
 *
 * ---- WO-S6-M2FIX (2026-06-11, CTO-approved plan A): BEAM MOVED OUT OF THE INTERRUPT CONTEXT ----
 *   ROOT CAUSE [L1 board-pinned]: the M2 board run deadlocked on the FIRST frame. Call stack:
 *     __dispatcher_SEC_rtn -> sport_DataHandler -> m1_sport_rx_callback -> m2_fira_beam_frame ->
 *     fira_tfb_analyze -> fira_run_segment_stateful -> fira_run_segment, PC parked at fira_tree.c:481
 *     `while (g_FIRTaskDoneCount < 1u)`. The FIRA busy-wait ran INSIDE the SPORT DMA SEC interrupt, so
 *     the FIR DONE interrupt that releases the spin could never preempt -> spin forever (board readout:
 *     valid=1 / setup_rc=0 / rx_block_count=0 / beam_live=-99 / output all-0). H1/H2 ran the SAME FIRA
 *     chain from MAIN context and is board-verified -- the bug is the CALLING CONTEXT, not FIRA.
 *   FIX (this TU, all guarded by M2_FIRA_INLOOP): the RX-done ISR no longer computes. It publishes the
 *     completed ping-pong half (s_m2_pending_half) + a ready flag (s_m2_ready) and returns; the beam runs
 *     in m2_beam_poll(), called from the m1_main.c while(1) idle loop = MAIN context, where the FIR DONE
 *     interrupt CAN land and release the fira_tree spin (the verified H1/H2 working mode). If main has
 *     not consumed the previous frame when the next RX-done fires, the ISR counts g_m2_overrun_count and
 *     overwrites with the latest half (drop-oldest, never block, never queue). New raw readouts:
 *     g_m2_overrun_count / g_m2_poll_count. FROZEN FIRA sources remain call-only zero-touch; the M1
 *     transparent build is byte-identical (every change sits behind M2_FIRA_INLOOP).
 * ============================================================================================ */
#ifndef M2_FIRA_INLOOP
#define M2_FIRA_INLOOP 0          /* default 0 = M1 transparent passthrough (board-PASS path preserved) */
#endif

/* ============================================================================================
 * WO-S7-B6 (DEC-S7-RULINGS-01 D3 / DEC-S7-IMPL-01 item 2, CTO_OK=1, 2026-09-02): build-gate #error
 * guards + 6 runtime build fingerprints + M2_SELFTEST (eight-anchor init self-test) + M2_SEG_CYC (three-
 * segment CCNT brackets) + g_m2_beam_cyc_min. DEFAULT-BYTE-EQUIVALENT: with none of the new macros defined,
 * the ONLY change to the preprocessed TU is the 6 fingerprint globals + g_m2_beam_cyc_min (and its reset/
 * update sites) -- proven by sprint7/dsp/host/run_s7_preproc_equiv.sh (gcc -E diff against HEAD for the
 * M1 and the default-M2 macro sets). Everything else sits behind M2_SELFTEST / M2_SEG_CYC.
 * ------------------------------------------------------------------------------------------
 * #error GUARDS. fw audit sec 9.C [L2 gcc]: -DM2_STATIC_TXTEST=1 WITHOUT M2_FIRA_INLOOP compiled clean, the
 * main.c #if M2_FIRA_INLOOP idle block vanished and the ISR fell into the M1 fan-out, which rewrote the
 * "static" TX every 1.33 ms -- the diagnostic premise failed SILENTLY and no readout showed it. Each guard
 * turns such a silently-wrong macro combination into a build FAIL (the tester's CCES build is the gate).
 * Value-style macros (M2_STATIC_TXTEST / M2_STXT_LOCALIZE / M2_SELFTEST / M2_SELFTEST_NEGCTRL / M2_SEG_CYC)
 * are tested with #if X exactly as their use sites test them; an undefined macro is 0 in #if (C99 6.10.1p4).
 * Falsifiers (expected build FAIL) are in run_guard_check.sh configs X1..X7 (X6/X7 = M2_WTBL_SEL, S7-SIDE30).
 * M2_WTBL_SEL (S7-SIDE30, 2026-09-26) is #ifdef-style: ANY definition turns it ON, including -DM2_WTBL_SEL=0;
 * to turn it off the symbol must be REMOVED from Defined symbols. It has no unconditional _built fingerprint
 * (precedent M2_SEG_CYC, DEC-S7-RULINGS-03): symbol visibility of g_m2_wtbl_sel in the .map is its fingerprint. */
#if M2_STATIC_TXTEST && !M2_FIRA_INLOOP
#error "M2_STATIC_TXTEST requires M2_FIRA_INLOOP=1 (without it the M1 fan-out rewrites the static TX every frame; fw audit 9.C)"
#endif
#if M2_STXT_LOCALIZE && !M2_STATIC_TXTEST
#error "M2_STXT_LOCALIZE requires M2_STATIC_TXTEST=1 (it is a variant of the static TX test; alone it is a silent no-op)"
#endif
#if M2_SELFTEST && !M2_FIRA_INLOOP
#error "M2_SELFTEST requires M2_FIRA_INLOOP=1 (the self-test drives the in-loop FIRA chain; without it there is nothing to test)"
#endif
#if M2_SELFTEST_NEGCTRL && !M2_SELFTEST
#error "M2_SELFTEST_NEGCTRL requires M2_SELFTEST=1 (a negative control of a self-test that is not built = silent no-op)"
#endif
#if M2_SEG_CYC && !M2_FIRA_INLOOP
#error "M2_SEG_CYC requires M2_FIRA_INLOOP=1 (the three-segment brackets live inside m2_fira_beam_frame)"
#endif
/* S7-SIDE30 (DEC-S7-SIDE30-01 (2)(4)): runtime weight-table select, #ifdef-style macro. CTO 2026-09-26 verbatim:
 * "...改板上固件 这些我都同意"; that THIS package falls under it is a PM reading pending CTO review (DEC (4)). */
#if defined(M2_WTBL_SEL) && !M2_FIRA_INLOOP
#error "M2_WTBL_SEL requires M2_FIRA_INLOOP=1 (the selectable table feeds m2_fira_beam_frame; alone it is a silent no-op)"
#endif
#if defined(M2_WTBL_SEL) && M2_STATIC_TXTEST
#error "M2_WTBL_SEL is meaningless with M2_STATIC_TXTEST=1 (the static TX test bypasses the beam; build one or the other)"
#endif

/* BUILD-FINGERPRINT DERIVATION. fw audit sec 9.H: 6 optional macros, 5 had no runtime fingerprint, so a
 * Defined-symbol left over from a previous CCES session (R52 stale-state trap) was invisible in every
 * readout. Each M2_FP_* / M1_FP_* is 1/0 derived from EXACTLY the test the code's own use sites apply:
 *   #ifdef-style macros -> defined(X):  M2_RX_RIGHT_ALIGNED (#ifdef, two shift sites), M2_CHMAP_FIX (#ifdef),
 *                                       M1_U6_TWI_ADDR_OVERRIDE (#ifdef, m1_softconfig.c; -D is project-wide)
 *   (7th optional macro, 2026-09-26: M2_WTBL_SEL, #ifdef-style, deliberately NOT fingerprinted here so the
 *    default build stays byte-identical; fingerprint = g_m2_wtbl_sel symbol visibility, see the guard note)
 *   #if-value-style      -> #if X:      M2_STATIC_TXTEST, M2_STXT_LOCALIZE (this TU + m1_main.c), M2_SELFTEST
 * so a fingerprint reads 1 iff the guarded code path is actually compiled in (e.g. -DM2_STATIC_TXTEST=0 must
 * read 0, which defined() would get wrong). NOTHING is #defined for the fingerprinted macros themselves, so
 * deriving the fingerprint can never change the #ifdef semantics of an existing use site. */
#if defined(M2_RX_RIGHT_ALIGNED)
#define M2_FP_RX_RIGHT_ALIGNED   1
#else
#define M2_FP_RX_RIGHT_ALIGNED   0
#endif
#if defined(M2_CHMAP_FIX)
#define M2_FP_CHMAP_FIX          1
#else
#define M2_FP_CHMAP_FIX          0
#endif
#if M2_STATIC_TXTEST
#define M2_FP_STATIC_TXTEST      1
#else
#define M2_FP_STATIC_TXTEST      0
#endif
#if M2_STXT_LOCALIZE
#define M2_FP_STXT_LOCALIZE      1
#else
#define M2_FP_STXT_LOCALIZE      0
#endif
#if M2_SELFTEST
#define M2_FP_SELFTEST           1
#else
#define M2_FP_SELFTEST           0
#endif
#if M2_SELFTEST_NEGCTRL
#define M2_FP_SELFTEST_NEGCTRL   1
#else
#define M2_FP_SELFTEST_NEGCTRL   0
#endif
#if defined(M1_U6_TWI_ADDR_OVERRIDE)
#define M1_FP_U6_ADDR_OVERRIDE   1
#else
#define M1_FP_U6_ADDR_OVERRIDE   0
#endif

#if M2_FIRA_INLOOP
/* M2 build pulls the frozen FIRA orchestration + core + weights (read-only call surface). Guarded so the
 * M1 transparent build (M2_FIRA_INLOOP=0) carries NONE of these includes and stays byte-clean. */
#include "fira_tree.h"           /* [frozen, call-only] FiraChannelState, fira_tree_setup/channel_init,
                                  *  fira_tfb_analyze/synthesize, fira_tree_teardown (sprint4/dsp/fira) */
#include "tree_filterbank.h"     /* [frozen, call-only] tfb_set_coeffs (core golden Q15 coeff inject) */
#include "fir_coeffs_hb63.h"     /* [frozen, read-only]  g_hb63_q15, FIR_HB63_NTAPS */
#include "dolph_w8_q15.h"        /* [frozen, read-only]  g_dolph_w8_q15[8], DOLPH_W8_NCH (broadside taper) */
#if M2_SELFTEST
#include "dolph_f5_goldens.h"    /* [frozen, read-only]  g_f5_golden_crc[8] = the F5 eight anchors (WO-S7-B6 self-test) */
#endif
#ifdef M2_WTBL_SEL
#include "m2_wtbl_q15.h"         /* [NOT frozen, generated by sprint7/dsp/wtbl/gen_m2_wtbl.py] Dolph -25/-30/-35 rows */
#endif
#endif

/* ---- COMPILE-TIME spec lock (DEC-S6-M1-ARCH-01): catch a four-opening regression at build, not runtime.
 *   A negative array size triggers a compile error if any locked geometry drifts. (C89-portable assert.) */
typedef char M1_ASSERT_BLOCKRATE_750[(M1_FS_HZ / M1_FRAME == 750u) ? 1 : -1];
typedef char M1_ASSERT_TX_4096B[((M1_TX_HALF_WORDS * M1_WORD_BYTES * 2u) == 4096u) ? 1 : -1];
typedef char M1_ASSERT_RX_512B_OR_1024B[(((M1_RX_HALF_WORDS * M1_WORD_BYTES * 2u) == 512u) ||
                                         ((M1_RX_HALF_WORDS * M1_WORD_BYTES * 2u) == 1024u)) ? 1 : -1];
typedef char M1_ASSERT_TX_8SLOT[(M1_TX_SLOTS == 8u) ? 1 : -1];

/* ---- raw readouts (definitions; declared extern in the header) ---- */
volatile uint32_t g_m1_rx_block_count  = 0u;
volatile uint32_t g_m1_tx_block_count  = 0u;
volatile uint32_t g_m1_cb_cyc_last     = 0u;
volatile uint32_t g_m1_cb_cyc_max      = 0u;
volatile uint32_t g_m1_cb_cyc_min      = 0xFFFFFFFFu;
volatile uint32_t g_m1_nonzero_samples = 0u;
volatile uint32_t g_m1_max_abs_sample  = 0u;
volatile int      g_m1_fg_stream_live  = -99;
volatile int      g_m1_valid           = 0;

/* [R49 obs-only - F49-MAJOR-1 discriminant] raw rc of the LAST codec TWI write (m1_twi_w8 was (void)).
 * THE R1-vs-bus-level discriminant: codec write ACK (0) on the SAME TWI2 -> bus good, U6 NACK is
 * address/device specific (R1); codec write also NACK (11=PERIPHERAL_ERROR) or LOSTARB -> BUS-LEVEL
 * (pull-up/SCL/SDA/actual-prescale), NOT U6-specific. -99 = not run. OBSERVATION ONLY -- codec config
 * and the m1_twi_w8 write itself are unchanged. */
volatile int      g_m1_codec_write_rc  = -99;

/* ---- M2 raw readouts (idle reads only; raw -- C9). Defined in BOTH builds so a debugger always finds
 *      the symbol; on the M1 transparent build they stay at their honest 0/sentinel (FIRA never ran). ---- */
volatile int      g_m2_fira_inloop      = M2_FIRA_INLOOP; /* 1 = built with FIRA beam in-loop; 0 = M1 passthrough */
volatile int      g_m2_setup_rc         = -99;            /* fira_tree_setup() rc (0=ok); -99 not-run/M1-build */
volatile uint32_t g_m2_out_nonzero      = 0u;             /* count of non-zero FIRA TX output samples (FG: beam alive) */
volatile uint32_t g_m2_out_max_abs      = 0u;             /* peak |FIRA TX output sample| (FG: silent beam detector) */
volatile int      g_m2_fg_beam_live     = -99;            /* 1 = blocks grew AND FIRA output non-zero; 0 = FAIL; -99 not-run */
volatile int      g_m2_valid            = 0;              /* 1 = ran on board with FIRA beam in-loop; 0 = M1/desktop */

/* ---- WO-S7-B6 BUILD FINGERPRINTS (fw audit 9.H; DEC-S7-IMPL-01 item 2). Defined in BOTH builds, volatile int,
 *      so a debugger always finds them and nothing folds them. READ THEM FIRST every session: a value that does
 *      not match the intended Defined-symbols set = wrong/stale build -> do not record its other readouts.
 *      Derivation rule (defined() vs #if X, mirroring each macro's own use sites) is documented above. ---- */
volatile int      g_m2_rx_right_aligned_built = M2_FP_RX_RIGHT_ALIGNED; /* 1 = R57 RX<<8 / TX>>8 fallback compiled in */
volatile int      g_m2_chmap_fix_built        = M2_FP_CHMAP_FIX;        /* 1 = weight-index chmap permutation compiled in */
volatile int      g_m2_static_txtest_built    = M2_FP_STATIC_TXTEST;    /* 1 = static TX tone diagnostic (beam poll skipped) */
volatile int      g_m2_stxt_localize_built    = M2_FP_STXT_LOCALIZE;    /* 1 = 375Hz polarity-localize variant compiled in */
volatile int      g_m2_selftest_built         = M2_FP_SELFTEST;         /* 1 = M2_SELFTEST eight-anchor init self-test compiled in */
volatile int      g_m1_u6_addr_override_built = M1_FP_U6_ADDR_OVERRIDE; /* 1 = M1_U6_TWI_ADDR_OVERRIDE in effect (m1_softconfig.c) */

#if M2_FIRA_INLOOP
/* WO-S6-M2FIX readouts (raw counters only -- C9). GUARDED, unlike the g_m2_* block above: the M1
 * transparent build must stay BYTE-IDENTICAL (M2FIX hard constraint), so these symbols exist only in
 * the M2 .dxe (they are meaningless on the M1 build anyway -- no poll path there). */
volatile uint32_t g_m2_overrun_count    = 0u;             /* RX-done found the previous frame unconsumed -> dropped oldest */
volatile uint32_t g_m2_poll_count       = 0u;             /* beam frames actually computed by main (m2_beam_poll) */
/* R56 MAJOR-3: beam-only CCNT bracket (raw -- C9). CALIBER = exactly the m2_fira_beam_frame call in
 * m2_beam_poll, nothing else (R42 lesson: a bracket's span IS its caliber) -- claim/FG-accumulate/
 * counters/latch stay OUTSIDE the bracket. Purpose: (a) main-context beam compute cost observable
 * on-board; (b) covers the overrun blind band -- tearing can occur with overrun==0 when claim+compute
 * lands inside (frame_period - beam_cost, frame_period), and beam_cyc_max makes the compute leg of
 * that sum observable (see the m2_beam_poll DEGRADATION note). */
volatile uint32_t g_m2_beam_cyc_last    = 0u;             /* CCNT of the LAST beam call (main-context compute, raw) */
volatile uint32_t g_m2_beam_cyc_max     = 0u;             /* max beam-call CCNT over the run (beam WCET, raw) */
/* WO-S7-B6 (DEC-S7-IMPL-01 1a, S7_DSP_ASSESSMENT 6.3 hypothesis a): the steady-state FLOOR of the same bracket.
 * max carries the cold first frame(s); min/last together show whether the run-max is the steady state. Raw. */
volatile uint32_t g_m2_beam_cyc_min     = 0xFFFFFFFFu;    /* min beam-call CCNT over the run (same bracket as _last/_max, raw) */

#if M2_SEG_CYC
/* WO-S7-B6 (DEC-S7-IMPL-01 1c) THREE-SEGMENT (+TX) CCNT brackets INSIDE m2_fira_beam_frame, summed over the 8
 * channels of ONE frame, raw (C9). Symbol names are cross-referenced by sprint7/docs/S7_B63_WALLCLOCK_GAP.md --
 * do NOT rename. CALIBER (R42: a bracket's span IS its caliber), per channel, chained reads:
 *   w   = from the previous channel's tx-close (or the pre-loop read for c=0) to after the Q15 weight loop:
 *         weight-index read (incl. the chmap lookup when M2_CHMAP_FIX) + 64 multiplies + loop overhead
 *   ana = exactly the fira_tfb_analyze call   (INCLUDES the FIR-DONE busy-waits inside frozen fira_tree.c)
 *   syn = exactly the fira_tfb_synthesize call (same)
 *   tx  = the 8-slot interleave write + FG nz/peak scan loop
 * claim / FG accumulate / counters / latch stay OUTSIDE every bracket (m2_beam_poll). The instrumentation adds
 * 4 CCNT reads per channel (+1 per frame) INSIDE g_m2_beam_cyc_*, so a SEG_CYC build's beam_cyc is not directly
 * comparable to a non-SEG_CYC build's -- read both builds, compare off-board. */
volatile uint32_t g_m2_seg_w_cyc_last   = 0u;             /* last frame: sum over 8 ch of the weight-loop bracket */
volatile uint32_t g_m2_seg_w_cyc_max    = 0u;
volatile uint32_t g_m2_seg_ana_cyc_last = 0u;             /* last frame: sum over 8 ch of the fira_tfb_analyze bracket */
volatile uint32_t g_m2_seg_ana_cyc_max  = 0u;
volatile uint32_t g_m2_seg_syn_cyc_last = 0u;             /* last frame: sum over 8 ch of the fira_tfb_synthesize bracket */
volatile uint32_t g_m2_seg_syn_cyc_max  = 0u;
volatile uint32_t g_m2_seg_tx_cyc_last  = 0u;             /* last frame: sum over 8 ch of the TX interleave + FG scan bracket */
volatile uint32_t g_m2_seg_tx_cyc_max   = 0u;
#endif

#if M2_SELFTEST
/* WO-S7-B6 M2_SELFTEST readouts (DEC-S7-IMPL-01 item 2 / S7_VERIFICATION_PLAN B6-4). Written ONCE by
 * m2_selftest_run() during m1_loopback_init (after FIRA setup, before the SPORT is armed); idle reads only.
 * PASS[c] uses the F5 definition (fira_regression.c:369-371): no per-sample FIRA-vs-core mismatch AND FIRA CRC
 * == live core CRC AND live core CRC == frozen anchor g_f5_golden_crc[c]. All values raw (C9). */
volatile int      g_m2_selftest_rc            = -99;      /* -99 not run | -1 FIRA not ready (setup failed) | 0 all 8 PASS | n = # FAILING channels */
volatile int      g_m2_selftest_negctrl_built = M2_FP_SELFTEST_NEGCTRL; /* 1 = unity-weight NEGATIVE-CONTROL build (expect rc=7) */
volatile int      g_m2_selftest_pass[DOLPH_W8_NCH]         = { 0, 0, 0, 0, 0, 0, 0, 0 };        /* 1 = channel c PASS */
volatile uint32_t g_m2_selftest_crc[DOLPH_W8_NCH]          = { 0u, 0u, 0u, 0u, 0u, 0u, 0u, 0u }; /* FIRA-path subband CRC (sb0|sb1|sb2|sb3 streaming) */
volatile uint32_t g_m2_selftest_crc_core[DOLPH_W8_NCH]     = { 0u, 0u, 0u, 0u, 0u, 0u, 0u, 0u }; /* frozen-core subband CRC over the SAME weighted chirp (live golden) */
volatile int      g_m2_selftest_mismatch_sb[DOLPH_W8_NCH]  = { -1, -1, -1, -1, -1, -1, -1, -1 }; /* first subband (0..3) where FIRA != core; -1 = none */
volatile int      g_m2_selftest_mismatch_idx[DOLPH_W8_NCH] = { -1, -1, -1, -1, -1, -1, -1, -1 }; /* f*sz[sb]+i of that first mismatch; -1 = none */
volatile uint32_t g_m2_selftest_frames        = 0u;       /* frames processed; expect 8 x 1024 = 8192 when the self-test completed */
volatile uint32_t g_m2_selftest_cyc           = 0u;       /* whole self-test wall CCNT, raw. 32-bit: wraps at 2^32 cyc (4.29 s @ 1 GHz) -> cross-check _cyc_ch */
volatile uint32_t g_m2_selftest_cyc_ch[DOLPH_W8_NCH]       = { 0u, 0u, 0u, 0u, 0u, 0u, 0u, 0u }; /* per-channel wall CCNT (1024 frames each; far below wrap) */
#endif
#endif

#if defined(M1_TARGET_BOARD) && defined(TARGET_SHARC)

#include <stddef.h>                       /* NULL */
#include <stdbool.h>                      /* true/false for the SPORT/SPU config calls */
/* ---- board headers: ALL [L1] paths from ALT.d (CCES SHARC/include); see M1_FACT_BASE sec 5 ---- */
#include <drivers/sport/adi_sport.h>      /* [L1] adi_sport_* (ALT.c:16) */
#include <services/pdma/adi_pdma_2156x.h> /* [L1] ADI_PDMA_DESC_LIST / ENUM_DMA_CFG_XCNT_INT (ALT.c) */
#include <drivers/twi/adi_twi_2156x.h>    /* [L1] adi_twi_* (ALT.c:18) */
#include <services/spu/adi_spu.h>         /* [L1] adi_spu_* (ALT.c:17) */
#include "ADAU_1962Common.h"             /* [L1] ADAU1962 register name macros (ALT project) */
#include "ADAU_1979Common.h"             /* [L1] ADAU1979 register name macros (ALT project) */

#ifdef M1_BUFFERS_IN_CACHED_MEM
#include <sys/cache.h>                    /* flush_data_buffer (only if buffers moved to cached mem) */
#endif

extern uint32_t bench_cyc_target(void);   /* [L1] CCNT (bench_main.c:118); reused for the callback probe */

/* board soft-switch config (SoftConfig_*.c in the board project; ALT.c:57-59) */
extern void ConfigSoftSwitches_ADC_DAC(void);
extern void ConfigSoftSwitches_ADAU_Reset(void);

/* ---- board constants (ALT.h) ---- */
#define M1_SPORT_DEV_4       4u            /* SPORT4 (ALT.h SPORT_DEVICE_4A/4B = 4u) */
#define M1_TWI_DEVNUM        2u            /* TWI2 (ALT.h:28) */
#define M1_TWI_PRESCALE      12u
#define M1_TWI_BITRATE       100u
#define M1_TWI_DUTYCYCLE     50u
#define M1_TWI_ADDR_1962     0x04u         /* ADAU1962A DAC (ALT.h:36) */
#define M1_TWI_ADDR_1979     0x11u         /* ADAU1979 ADC (ALT.h:37) */
#define M1_SPORT_4A_SPU      57            /* ALT.h:39 */
#define M1_SPORT_4B_SPU      58            /* ALT.h:40 */
#define M1_DMA_NUM_DESC      2u            /* ping-pong (ALT.h:42) */
#define M1_TWI_BUF_SZ        8u

/* ---- file-scope state: ALL decls at TOP (R16 declaration-order discipline) ---- */

/* ping-pong DMA buffers.
 *   M1 transparent build (M2_FIRA_INLOOP=0): opening-4 default = L1 Block 0, uncached -> coherency-free,
 *     no FIRA working set in the build -> NO Block-0 self-conflict (M1 no-pin, R34 ROUTE-A4-1).
 *   M2 FIRA build (M2_FIRA_INLOOP=1, OPENING-2): the FIRA working set s_m2_fa now lives in the build.
 *     To avoid the R24 intra-Block-0 single-port self-conflict (SPORT-PDMA vs core FIRA accesses in ONE
 *     L1 block), pin BOTH SPORT buffers to L1 Block 1 via seg_l1_block1 -- the same pragma+section ADI's
 *     own FIRA/IIRA accelerator examples use for accelerator-DMA buffers (bsp/app_notes/fira_accel_code/
 *     .../FIR_Throughput_21569.c:23 / IIR_Throughput_21569_V2.c:23, [L1] proven; H2_MAP_PLACEMENT_
 *     ADJUDICATION.md:103-117). s_m2_fa is pinned to the SAME seg_l1_block1 below, so SPORT buffers and
 *     the FIRA set are CO-resident in Block 1 and DISJOINT from Block 0 (heap/stack/code). The intra-block
 *     single-port note: Block-1 RX/TX + FIRA share Block 1, but the product contention we must avoid is
 *     DMA-vs-FIRA across Block 0 (R24); board .map re-read confirms the actual placement (gap below).
 *   RX = 1 captured slot/frame (512B over 2 halves); TX = 8 slots/frame (4096B over 2 halves). */
#if M2_FIRA_INLOOP
#pragma section("seg_l1_block1")
static int32_t s_m1_rx_buf[2][M1_RX_HALF_WORDS];   /* ADC RX ping-pong -> L1 Block 1 (M2 pin, OPENING-2) */
#pragma section("seg_l1_block1")
static int32_t s_m1_tx_buf[2][M1_TX_HALF_WORDS];   /* DAC TX ping-pong -> L1 Block 1 (M2 pin, OPENING-2) */
#else
static int32_t s_m1_rx_buf[2][M1_RX_HALF_WORDS];   /* ADC RX ping-pong (M1: default Block 0, no-pin) */
static int32_t s_m1_tx_buf[2][M1_TX_HALF_WORDS];   /* DAC TX ping-pong (M1: default Block 0, no-pin) */
#endif

/* M2 FIRA per-channel working set (8 ch broadside). static off-stack (R37 FIX2 stack discipline -- a
 * FiraChannelState[8] is ~18KB, must NEVER live on the callback stack). Pinned to L1 Block 1 alongside
 * the SPORT buffers (OPENING-2). Cross-frame history (62 samp/seg x 9 segs/ch) persists between frames,
 * so this is file-scope persistent, advanced by fira_tfb_analyze/synthesize each frame. */
#if M2_FIRA_INLOOP
#pragma section("seg_l1_block1")
static FiraChannelState s_m2_fa[DOLPH_W8_NCH];     /* FIRA working set -> L1 Block 1 (M2 pin, OPENING-2) */
#endif

static ADI_PDMA_DESC_LIST s_m1_rx_desc[2];         /* RX descriptor ring (circular) */
static ADI_PDMA_DESC_LIST s_m1_tx_desc[2];         /* TX descriptor ring (circular) */

static uint8_t          s_m1_sport_mem_tx[ADI_SPORT_MEMORY_SIZE];
static uint8_t          s_m1_sport_mem_rx[ADI_SPORT_MEMORY_SIZE];
static ADI_SPORT_HANDLE s_m1_hsport_tx = NULL;     /* SPORT4A = Tx (to DAC) */
static ADI_SPORT_HANDLE s_m1_hsport_rx = NULL;     /* SPORT4B = Rx (from ADC) */

static uint8_t          s_m1_twi_mem[ADI_TWI_MEMORY_SIZE];
static ADI_TWI_HANDLE   s_m1_htwi = NULL;

static uint8_t          s_m1_spu_mem[ADI_SPU_MEMORY_SIZE];
static ADI_SPU_HANDLE   s_m1_hspu = NULL;

static uint8_t          s_m1_twi_txbuf[M1_TWI_BUF_SZ];   /* TWI register-write scratch */
static volatile uint32_t s_m1_pp_index = 0u;            /* which ping-pong half the callback services next */

#if M2_FIRA_INLOOP
/* WO-S6-M2FIX ISR->main handoff (the ONLY state shared between the RX-done ISR and m2_beam_poll).
 * Single-word volatile accesses (SHARC word-atomic). ORDERING CONTRACT:
 *   ISR (producer):  write s_m2_pending_half FIRST, then set s_m2_ready = 1.
 *   main (consumer): see s_m2_ready != 0, read s_m2_pending_half, THEN clear s_m2_ready (claim).
 * The consumer must NOT clear ready before reading the half -- doing so re-opens the slot and a new
 * RX-done could republish, making poll compute the SAME half twice = the cross-frame FIRA state is
 * advanced twice on one input (state corruption). See m2_beam_poll for the full race ledger. */
static volatile uint32_t s_m2_ready        = 0u;        /* 1 = a beam frame is pending for main */
static volatile uint32_t s_m2_pending_half = 0u;        /* which ping-pong half holds that frame */
#endif

/* ---- codec register tables: D5 per-bit DECODED + 48k-self-checked (NOT blind-copied from ALT) ----
 * Each value carries its bit-field decomposition. CRITICAL D5 catch (R35): ALT ADC SAI_CTRL0=0x1B has
 * FS=011=64-96k -- WRONG for 48k. R37 FIX: change the FS field ONLY -> 0x1A (SAI stays TDM8 to match the
 * DAC master frame); the earlier 0x0A also changed SAI->TDM2, which broke frame-match (over-correction).
 * DAC values re-decoded against the DAC-side field tables (DAC FS is [2:1], distinct from ADC FS [2:0]). */
typedef struct { uint8_t reg; uint8_t val; } M1_RegPair;

/* ADAU1962A DAC (TX, TDM8 master @48k). [datasheet decodes: M1_FACT_BASE sec 3.11-3.13] */
static const M1_RegPair s_m1_dac_cfg[28] = {
    {ADAU1962_PDN_CTRL_1, 0x00}, /* power-down ctrl staged: master block on */
    {ADAU1962_PDN_CTRL_2, 0xff}, /* DAC ch power-down (staged off first, re-enabled below) */
    {ADAU1962_PDN_CTRL_3, 0x0f},
    {ADAU1962_DAC_CTRL0,  0x01}, /* DECODE: SDATA_FMT=00(I2S) SAI=000(Stereo) FS=00 MMUTE=1 -- reset-class, MUTED while configuring */
    {ADAU1962_DAC_CTRL1,  0x01}, /* DECODE: SAI_MS=1 -> DAC is the TDM bus MASTER (drives BCLK/LRCLK) [Table 32] */
    {ADAU1962_DAC_CTRL2,  0x00}, /* DECODE: BCLK_TDMC=0(32 BCLK/slot) AUTO_MUTE_EN=0(disabled) -- so silent/zero data won't auto-mute at bring-up [Table 33] */
    {ADAU1962_DAC_MUTE1,  0x00}, /* per-ch soft mute off (ch1..8) */
    {ADAU1962_DAC_MUTE2,  0x00}, /* per-ch soft mute off (ch9..12) */
    {ADAU1962_MSTR_VOL,   0x00}, /* master volume 0x00 = 0 dB (unattenuated) */
    {ADAU1962_DAC1_VOL,   0x00}, {ADAU1962_DAC2_VOL, 0x00}, {ADAU1962_DAC3_VOL, 0x00},
    {ADAU1962_DAC4_VOL,   0x00}, {ADAU1962_DAC5_VOL, 0x00}, {ADAU1962_DAC6_VOL, 0x00},
    {ADAU1962_DAC7_VOL,   0x00}, {ADAU1962_DAC8_VOL, 0x00}, /* ch1..8 = our 8 TX slots, 0 dB */
    {ADAU1962_DAC9_VOL,   0x00}, {ADAU1962_DAC10_VOL,0x00}, {ADAU1962_DAC11_VOL,0x00},
    {ADAU1962_DAC12_VOL,  0x00}, /* ch9..12 unused (0 dB; muted via not-driven slots) */
    {ADAU1962_PAD_STRGTH, 0x00}, /* pad drive strength default */
    {ADAU1962_DAC_PWR1,   0xaa}, {ADAU1962_DAC_PWR2, 0xaa}, {ADAU1962_DAC_PWR3, 0xaa}, /* DAC ch power up */
    {ADAU1962_PDN_CTRL_2, 0x00}, {ADAU1962_PDN_CTRL_3, 0x00}, /* re-enable blocks (final power) */
    {ADAU1962_DAC_CTRL0,  0x18}  /* DECODE (DAC-side fields, NOT the ADC table): SDATA_FMT=00 SAI[5:3]=011(TDM8) FS[2:1]=00(=32/44.1/48k per ADAU1962A.pdf Table 31 -- DAC FS is the 2-bit [2:1] field, distinct position from ADC FS[2:0]) MMUTE=0(UNMUTED). Final enable; matches TX TDM8 @48k. [ADAU1962A.pdf Table 31 P30] */
};

/* ADAU1979 ADC (RX). D5 FIX (FS field ONLY, R37): SAI_CTRL0 = 0x1A. [adau1979.pdf Table 20 P30; FACT_BASE sec 3.3] */
static const M1_RegPair s_m1_adc_cfg[16] = {
    {ADAU1979_REG_BOOST,         0x00}, /* input boost off */
    {ADAU1979_REG_MICBIAS,       0x00}, /* mic bias off */
    {ADAU1979_REG_BLOCK_POWER_SAI,0x30},/* staged block power (partial) */
    {ADAU1979_REG_SAI_CTRL0,     0x1A}, /* D5-FIX (FS ONLY): SDATA_FMT=00(I2S) SAI=011(TDM8, matches DAC 8-slot master frame; only slot0 carries valid mono audio, RX captures 1 word via SPORT packing) FS=010(32-48k). = (ALT 0x1B & ~0x07)|0x02. ALT's FS=011=64-96k was the lone bug (R35); SAI[5:3] must NOT change (R37: ADC=TDM2 on a TDM8 master desyncs the frame counter) [Table 20] */
    {ADAU1979_REG_SAI_CTRL1,     0x08}, /* DECODE: SDATA_SEL=0(OUT1) SLOT_WIDTH=00(32 BCLK/slot) DATA_WIDTH=0(24-bit) LR_MODE=1(pulse) SAI_MS=0(SLAVE -- DAC is master) [Table 21] */
    {ADAU1979_REG_CMAP12,        0x01}, /* channel->slot map ch1/2 (ch1 to slot0, our 1 mono source) */
    {ADAU1979_REG_CMAP34,        0x23}, /* channel->slot map ch3/4 -- ALT 4ch inheritance, UNUSED in 1-mono (only slot0 captured); left as ALT default (harmless; those slots not captured) */
    {ADAU1979_REG_SAI_OVERTEMP,  0xf0}, /* overtemp thresholds (datasheet default-class) */
    {ADAU1979_REG_POST_ADC_GAIN1,0xA0}, {ADAU1979_REG_POST_ADC_GAIN2,0xA0}, /* per-ch post-ADC gain (0 dB nominal) */
    {ADAU1979_REG_POST_ADC_GAIN3,0xA0}, {ADAU1979_REG_POST_ADC_GAIN4,0xA0},
    {ADAU1979_REG_ADC_CLIP,      0x00}, /* clip status clear */
    {ADAU1979_REG_DC_HPF_CAL,    0x00}, /* dc high-pass / cal off */
    {ADAU1979_REG_BLOCK_POWER_SAI,0x3f},/* full block power (final) */
    {ADAU1979_REG_MISC_CONTROL,  0x00}  /* misc default */
};

/* ---- TWI 8-bit register write (ALT.c:478-483) ---- */
static void m1_twi_w8(uint8_t reg, uint8_t val)
{
    s_m1_twi_txbuf[0] = reg;
    s_m1_twi_txbuf[1] = val;
    /* [R49 obs-only - F49-MAJOR-1] capture the raw rc (was (void)) -> g_m1_codec_write_rc holds the LAST
     * codec write's result = the R1-vs-bus-level discriminant. Write behavior unchanged. */
    g_m1_codec_write_rc = (int)adi_twi_Write(s_m1_htwi, s_m1_twi_txbuf, 2u, false);
}

#if M2_FIRA_INLOOP
/* ============================================================================================
 * M2 Q-BOUNDARY NOTE (OPENING-5, board-confirm) -- the one place RX int32 meets FIRA Q31, and back.
 * ------------------------------------------------------------------------------------------
 * M1 audio word = 24-bit codec data in a 32-bit SPORT slot (ADC SAI_CTRL1 DATA_WIDTH=0=24-bit,
 *   SPORT ConfigData DTYPE_SIGN_FILL 31 -> sign-filled to bit31). FIRA core arithmetic = Q31
 *   (tree_filterbank.h: coeff Q15, state/intermediate Q31). OPENING-5 = ZERO-TRANSFORM identity:
 *   a 24-bit LEFT-aligned sample IS a legal Q31 value (high 24 bits significant, low 8 bits zero =
 *   a coarser-LSB Q31). So RX feeds FIRA with NO shift / NO mask, and FIRA Q31 output writes the TX
 *   slot with NO shift / NO mask (the DAC takes the high 24 bits). R46 = bit-exact run evidence that
 *   left-aligned == legal Q31.
 *
 *   *** BOARD-CONFIRM (must verify on the bench, NOT assumable on desktop) ***
 *   The identity holds ONLY IF the SPORT delivers/consumes LEFT-aligned (MSB-justified) samples.
 *   DTYPE_SIGN_FILL 31 strongly implies left-align, but the HRM + a g_m1_rx_buf dump are the proof.
 *   R46 MECHANICAL DISCRIMINANT (run on board): dump g_m1_rx_buf with a known mid-scale input.
 *     - If the low 8 bits are ~0 and the magnitude sits in the high 24 bits -> LEFT-aligned ->
 *       zero-transform is correct (this code as-is).
 *     - If the magnitude sits in the low 24 bits (sign-extended high byte) -> RIGHT-aligned ->
 *       apply  RX: x_q31 = rx[f] << 8 ;  TX: tx_slot = (out_q31) >> 8  (arithmetic shifts).
 *   This discriminant is a board action (CTO list); the code path here assumes LEFT-aligned (R46).
 *
 * ---- M2_RX_RIGHT_ALIGNED (R57 contingency pre-build, CTO-approved) ----
 *   The RIGHT-aligned prescription above is now PRE-BUILT behind #ifdef M2_RX_RIGHT_ALIGNED at the two
 *   shift sites in m2_fira_beam_frame (RX <<8 before the Dolph weight; TX >>8 at slot pack-out).
 *   DEFAULT OFF: the macro is NOT defined anywhere in source; the #else paths are token-identical to
 *   the pre-R57 code, so the default M2 build (and the M1 build) is byte-level unchanged. Rebuild with
 *   -DM2_RX_RIGHT_ALIGNED ONLY if the 1A alignment dump / scalar rule proves RIGHT-aligned; CTO-gated
 *   to apply (same rebuild-only-no-source-edit precedent as M1_U6_TWI_ADDR_OVERRIDE, b3d7f74).
 *   FG CALIBER IS SHIFT-INVARIANT BY DESIGN: the output FG scan (nz/peak -> g_m2_out_nonzero/
 *   g_m2_out_max_abs) reads the PRE-SHIFT Q31 value in BOTH modes, so out_max_abs stays comparable
 *   against 0x7FFFFFFF (the amp-safety / near-full-scale indicator) regardless of alignment mode.
 *   SIGN-BIT SEMANTICS OF THE TWO SHIFTS:
 *     RX <<8 : implemented as (int32_t)((uint32_t)rx[i] << 8). A bare signed left shift of a NEGATIVE
 *       value is UNDEFINED in C (C11 6.5.7p4), so we shift the uint32 bit pattern and reinterpret --
 *       the standard two's-complement idiom. Value-exact: a right-aligned 24-bit sample lies in
 *       [-2^23, 2^23-1], so x*256 fits int32 with sign landing in bit31 = legal Q31, low 8 bits zero.
 *     TX >>8 : signed right shift is IMPLEMENTATION-DEFINED in C, arithmetic (sign-extending) on BOTH
 *       toolchains in play -- evidenced by PRECEDENT IN THIS VERY DATAPATH, not assumption: the Q15
 *       ">> 15" postscale on signed products (this file + the frozen FIRA core) ran BIT-EXACT vs
 *       golden with negative samples on desktop gcc (R46) and on-board CCES SHARC (H1/H2 [L1]); a
 *       logical (zero-filling) shift would have failed every negative-sample compare. Result =
 *       sign-extended 24-bit right-aligned word, which is what a right-aligned DAC slot consumes.
 * ============================================================================================ */

/* M2 scratch: one channel's 4 analyzed subbands + that channel's reconstructed full-rate output.
 * file-scope static (R37 FIX2: off the callback stack -- these + s_m2_fa must not live on the ISR
 * stack). Subband sizes per the dyadic tree (frame/8, frame/4, frame/2, frame): 8/16/32/64 @ frame=64. */
static int32_t s_m2_sb0[M1_FRAME / 8];
static int32_t s_m2_sb1[M1_FRAME / 4];
static int32_t s_m2_sb2[M1_FRAME / 2];
static int32_t s_m2_sb3[M1_FRAME];
static int32_t s_m2_xw[M1_FRAME];      /* per-channel input-scaled (Dolph-weighted) frame */
static int32_t s_m2_chout[M1_FRAME];   /* per-channel FIRA synthesize output (full-rate, Q31) */

/* ---- M2 one-frame 8ch broadside beam: 1 mono RX frame (64 samp) -> 8 channel FIRA outputs,
 *      interleaved into the 8-slot TX layout. Mirrors the H2 8ch frame model EXACTLY
 *      (h2_dma_isr_measure.c:115-120): per ch  xw = Dolph_w[c] * rx  (Q15 x Q31 >> 15)
 *      -> fira_tfb_analyze -> fira_tfb_synthesize. 8 ch INDEPENDENT, NO cross-channel sum
 *      (product topology = 8 DACs, broadside = ACOUSTIC superposition, NOT a digital sum).
 *      OPENING-4: broadside = input-scale Dolph weight ONLY, NO frac-delay focusing (v2 deferred).
 *      OPENING-5: rx[] used as Q31 with NO shift (zero-transform identity; board-confirm align above).
 *        DEFAULT mode. R57: the RIGHT-aligned fallback (RX<<8 / TX>>8) is pre-built behind
 *        #ifdef M2_RX_RIGHT_ALIGNED (default OFF, CTO-gated rebuild -- see Q-BOUNDARY NOTE above).
 *      @param rx   packed mono RX frame, M1_FRAME int32 (Q31 by identity)
 *      @param tx   8-slot interleaved TX frame, M1_FRAME*M1_TX_SLOTS int32 ; tx[f*8 + c] = ch c, samp f
 *      @return     accumulates FG stats into *pnz / *ppeak over the 8-channel output. */
#ifdef M2_CHMAP_FIX
/* CHANNEL->PHYSICAL-POSITION remap (basis: BEAM_POLARITY_CLOSURE_20260708.md sec5/6 + EXP_STATIC_POL375.md).
 * The frozen g_dolph_w8_q15 is indexed edge(0)->center(7) ASSUMING TX slot c drives physical rank c.
 * Phase A (375Hz solo) measured the ACTUAL wiring on this rig: slot3=center C7, slot4=edge C0, ... so
 * the Dolph taper lands on the WRONG physical positions (the center pair gets w=0.733 instead of 1.0).
 * FIX: channel c reads the weight for the physical RANK it actually drives -> g_dolph_w8_q15[perm[c]].
 * perm[c] = physical rank (edge=0..center=7) of the pair driven by slot c:
 *   slot 0->C4(r4) 1->C5(r5) 2->C6(r6) 3->C7(r7,center) 4->C0(r0,edge) 5->C1(r1) 6->C2(r2) 7->C3(r3).
 * WHY WEIGHT-INDEX ONLY (state s_m2_fa[c] and slot tx[..+c] stay = c): common mono input + IDENTICAL
 * per-channel broadside filter (NO frac-delay) => each ch output = w_c * y with y shared, so permuting
 * the weight index is bit-equivalent to permuting TX slots. *** BROADSIDE v1 ONLY *** -- once v2 adds
 * per-channel FRAC-DELAY focusing, the delay is ALSO position-dependent and must be permuted/re-derived
 * too (a scalar-weight permute no longer suffices).
 * *** ASSUMPTION (hard-gate on FAR-FIELD A/B before any lock): only C0=edge and C7=center are user-
 * confirmed; the intermediate rank order C1..C6 is ASSUMED monotonic. A mid-pair swap only perturbs two
 * near-equal weights (graceful); the raised edge g0=0.867 vs g1=0.504 is the one that matters (C0 IS the
 * confirmed anchor). EFFECT [L2 numpy]: restores the DESIGN Dolph -> -6dB mainlobe WIDENS 25.7->29.3deg
 * (@1k, still <=30 spec) but SLL -9.67->-20dB and 30deg rejection 10.3->23.1dB. The current narrow
 * 25.7deg is a broken edge-heavy artifact (worthless: -9.67dB sidelobes leak to the sides = the "30deg
 * weak" symptom). RIG-SPECIFIC (competitor speakers, our wiring) + HYPOTHESIS.
 * s_m2_chmap is volatile + JTAG-editable: the tester may poke alternative permutations live (e.g. a
 * suspected mid-pair swap) WITHOUT rebuild. Enable via build -D only (NOT .cproject); undefined = byte-
 * identical. Index is masked (& NCH-1) so a mistyped JTAG value can never OOB-read the frozen table. */
static volatile uint8_t s_m2_chmap[DOLPH_W8_NCH] = { 4u, 5u, 6u, 7u, 0u, 1u, 2u, 3u };
#endif

#ifdef M2_WTBL_SEL
/* S7-SIDE30 RUNTIME WEIGHT-TABLE SELECT (DEC-S7-SIDE30-01 (2)(4); sprint7/docs/S7_TESTER_RUNBOOK_WTBL.md).
 * g_m2_wtbl_sel is JTAG-writable: 0 = the FROZEN g_dolph_w8_q15 (Dolph -20, source untouched),
 * 1..M2_WTBL_NEXTRA = g_m2_wtbl_q15[sel-1] (Dolph -25/-30/-35, m2_wtbl_q15.h). Snapshot ONCE per frame
 * (all 8 channels of a frame use one table). Out-of-range -> table 0 + g_m2_wtbl_oob_count++ (never an
 * OOB read). Every table value <= 32768 (<= 1.0) -> same GAP-SAT/headroom premise as the frozen table.
 * Build fingerprint = symbol visibility of g_m2_wtbl_sel in the .map (precedent: M2_SEG_CYC, RULINGS-03);
 * undefined macro = byte-identical to the previous build (proof: sprint7/dsp/wtbl/run_wtbl_checks.sh).
 * M2_SELFTEST is unaffected (its anchor path reads g_dolph_w8_q15 directly, weight index == channel).
 * With M2_CHMAP_FIX the chmap index is applied to the SELECTED table (weight follows physical rank). */
volatile int32_t  g_m2_wtbl_sel         = 0;   /* JTAG write: 0=D20(frozen) 1=D25 2=D30 3=D35 */
volatile int32_t  g_m2_wtbl_sel_applied = -1;  /* read: table actually applied in the last frame (-1 = no frame yet) */
volatile uint32_t g_m2_wtbl_oob_count   = 0u;  /* read: frames where sel was out of range (fell back to 0) */
volatile int32_t  g_m2_wtbl_applied_sum = -1;  /* read: SUM of the 8 Q15 weights actually multiplied in the last
                                                * frame (accumulated from the SAME w used in the multiply) -> proves
                                                * which table's CONTENT was applied, not just the index. Table sums
                                                * are listed in S7_TESTER_RUNBOOK_WTBL.md (desktop identity). */

static const int32_t *m2_wtbl_pick(void)
{
    int32_t sel = g_m2_wtbl_sel;
    if (sel < 0 || sel > (int32_t)M2_WTBL_NEXTRA) { sel = 0; g_m2_wtbl_oob_count++; }
    g_m2_wtbl_sel_applied = sel;
    return (sel == 0) ? g_dolph_w8_q15 : g_m2_wtbl_q15[sel - 1];
}
#endif

static void m2_fira_beam_frame(const int32_t *rx, int32_t *tx, uint32_t *pnz, uint32_t *ppeak)
{
    uint32_t c, i;
    uint32_t nz = *pnz, peak = *ppeak;
#ifdef M2_WTBL_SEL
    const int32_t *wt = m2_wtbl_pick();   /* one table snapshot per frame */
    int32_t wsum = 0;                     /* FG: sum of the weights actually used this frame */
#endif
#if M2_SEG_CYC
    uint32_t sw = 0u, sana = 0u, ssyn = 0u, stx = 0u;   /* WO-S7-B6: per-frame segment sums (8 ch) */
    uint32_t ta, tb;                                     /* chained bracket edges: one read closes a segment and opens the next */
    ta = bench_cyc_target();                             /* opens the w bracket of c=0 (caliber note at the g_m2_seg_* definitions) */
#endif

    for (c = 0u; c < (uint32_t)DOLPH_W8_NCH; c++) {
#if defined(M2_WTBL_SEL) && defined(M2_CHMAP_FIX)
        const int32_t w = wt[s_m2_chmap[c] & (DOLPH_W8_NCH - 1u)];   /* WTBL+MAPFIX: selected table, physical rank (mask = OOB-safe) */
#elif defined(M2_WTBL_SEL)
        const int32_t w = wt[c];                                      /* WTBL: selected table, weight index == channel */
#elif defined(M2_CHMAP_FIX)
        const int32_t w = g_dolph_w8_q15[s_m2_chmap[c] & (DOLPH_W8_NCH - 1u)];  /* MAPFIX: phys pos gets its Dolph weight (JTAG-editable; mask = OOB-safe) */
#else
        const int32_t w = g_dolph_w8_q15[c];            /* Dolph-Cheb -20dB Q15 weight for channel c */
#endif
#ifdef M2_WTBL_SEL
        wsum += w;                                    /* FG: accumulate the weight that feeds the multiply below */
#endif
        /* input-scale weight (== f5_apply_w / H2:117-118): Q15 x Q31 >> 15. rx[i] is Q31 by identity. */
        for (i = 0u; i < M1_FRAME; i++)
#ifdef M2_RX_RIGHT_ALIGNED
            /* R57 fallback (default OFF, CTO-gated -DM2_RX_RIGHT_ALIGNED rebuild; see Q-BOUNDARY NOTE):
             * right-aligned 24-bit RX -> Q31 via <<8 BEFORE the weight. uint32 shift avoids the signed-
             * negative left-shift UB (C11 6.5.7p4); value-exact, sign lands in bit31 (NOTE above). */
            s_m2_xw[i] = (int32_t)(((int64_t)w * (int64_t)(int32_t)((uint32_t)rx[i] << 8)) >> 15);
#else
            s_m2_xw[i] = (int32_t)(((int64_t)w * (int64_t)rx[i]) >> 15);
#endif
#if M2_SEG_CYC
        tb = bench_cyc_target(); sw += tb - ta; ta = tb;      /* w CLOSE / ana OPEN */
#endif

        /* FIRA analyze (1ch -> 4 subbands) then synthesize (4 subbands -> 1ch full-rate). CALL-ONLY into
         * the frozen fira_tree.c; s_m2_fa[c] carries this channel's cross-frame filter state. */
        fira_tfb_analyze(&s_m2_fa[c], s_m2_xw, (uint16_t)M1_FRAME,
                         s_m2_sb0, s_m2_sb1, s_m2_sb2, s_m2_sb3);
#if M2_SEG_CYC
        tb = bench_cyc_target(); sana += tb - ta; ta = tb;    /* ana CLOSE / syn OPEN */
#endif
        /* broadside v1: NO frac-delay on the subbands (focusing = v2). Synthesize straight back. */
        fira_tfb_synthesize(&s_m2_fa[c], s_m2_sb0, s_m2_sb1, s_m2_sb2, s_m2_sb3,
                            (uint16_t)M1_FRAME, s_m2_chout);
#if M2_SEG_CYC
        tb = bench_cyc_target(); ssyn += tb - ta; ta = tb;    /* syn CLOSE / tx OPEN */
#endif

        /* interleave channel c into the 8-slot TX layout (tx[f*8 + c]); OPENING-5: write Q31 with no
         * shift -- the DAC slot takes the high 24 bits. + FG scan of the FIRA output. */
        for (i = 0u; i < M1_FRAME; i++) {
            int32_t o = s_m2_chout[i];
            uint32_t a = (o < 0) ? (uint32_t)(-(int64_t)o) : (uint32_t)o;
#ifdef M2_RX_RIGHT_ALIGNED
            /* R57 fallback pack-out: Q31 -> right-aligned 24-bit via ARITHMETIC >>8 (sign-extending on
             * both toolchains -- bit-exact precedent basis in the Q-BOUNDARY NOTE). FG scan above stays
             * on the PRE-SHIFT o/a, so nz / out_max_abs keep the Q31 caliber in both modes (0x7FFFFFFF
             * amp-safety comparability -- R57 requirement). */
            tx[i * M1_TX_SLOTS + c] = o >> 8;
#else
            tx[i * M1_TX_SLOTS + c] = o;
#endif
            if (o != 0) nz++;
            if (a > peak) peak = a;
        }
#if M2_SEG_CYC
        tb = bench_cyc_target(); stx += tb - ta; ta = tb;     /* tx CLOSE; the same read opens the next channel's w bracket */
#endif
    }
#ifdef M2_WTBL_SEL
    g_m2_wtbl_applied_sum = wsum;
#endif
    *pnz = nz; *ppeak = peak;
#if M2_SEG_CYC
    g_m2_seg_w_cyc_last   = sw;   if (sw   > g_m2_seg_w_cyc_max)   g_m2_seg_w_cyc_max   = sw;
    g_m2_seg_ana_cyc_last = sana; if (sana > g_m2_seg_ana_cyc_max) g_m2_seg_ana_cyc_max = sana;
    g_m2_seg_syn_cyc_last = ssyn; if (ssyn > g_m2_seg_syn_cyc_max) g_m2_seg_syn_cyc_max = ssyn;
    g_m2_seg_tx_cyc_last  = stx;  if (stx  > g_m2_seg_tx_cyc_max)  g_m2_seg_tx_cyc_max  = stx;
#endif
}
#endif /* M2_FIRA_INLOOP */

/* ---- RX-buffer-processed callback: io-callback CCNT probe + FG audio scan + the datapath.
 *   io-callback probe: the CCNT bracket measures the io item-1 "codec/IO DMA" CORE cost. RAW only (C9).
 *   cb_cyc caliber (M2FIX REVISION of the R42 note): the bracket spans the callback body, which under
 *   M2 is now ONLY the RX input FG scan + the ready-flag handoff -- the FIRA beam runs in MAIN context
 *   (m2_beam_poll) and is NOT inside g_m1_cb_cyc_*. Beam fit-vs-frame-budget is evidenced by
 *   g_m2_overrun_count staying ~0 (a too-slow beam would grow it). io-callback-only allowance stays
 *   [L3 reserve 30].
 *   DATAPATH:
 *     M2_FIRA_INLOOP=1 -> publish the completed RX half to main (m2_beam_poll computes the 8ch FIRA
 *                         broadside beam there -- WO-S6-M2FIX; was computed here, deadlocked at
 *                         fira_tree.c:481, see file header). ISR also FG-scans the RX INPUT frame.
 *     M2_FIRA_INLOOP=0 -> M1 FAN-OUT 1->8: copy the one mono sample to all 8 TX slots (M1 board-PASS). */
static void m1_sport_rx_callback(void *pAppHandle, uint32_t nEvent, void *pArg)
{
    uint32_t t0, t1;
    (void)pAppHandle; (void)pArg;

    if (nEvent != ADI_SPORT_EVENT_RX_BUFFER_PROCESSED) return;   /* only the RX-done event */

    t0 = bench_cyc_target();   /* CCNT bracket OPEN (raw -- C9; no derived MCPS here) */
    {
        const uint32_t half = s_m1_pp_index & 1u;
        const int32_t *rx = s_m1_rx_buf[half];   /* M1_RX_HALF_WORDS = 64 words (1 slot x 64 frames, packed) */
        int32_t *tx = s_m1_tx_buf[half];         /* M1_TX_HALF_WORDS = 512 words (8 slot x 64 frames) */
        uint32_t nz = 0u, peak = 0u;

#if M2_FIRA_INLOOP
        /* WO-S6-M2FIX: the ISR NO LONGER runs the beam (fira_tree.c:481 spin in SEC context starved the
         * FIR DONE interrupt -> first-frame deadlock, see file header). ISR work is now only:
         *   (a) FG-scan the RX INPUT frame (64 samples, cheap). CALIBER CHANGE: g_m1_nonzero_samples /
         *       g_m1_max_abs_sample are INPUT-liveness stats in the M2 build (were beam-OUTPUT stats
         *       pre-M2FIX) -- now the SAME caliber as the M1 fan-out path (which scans the RX sample),
         *       so g_m1_fg_stream_live uniformly means "input stream alive" in both builds. The beam-
         *       output stats live in g_m2_out_nonzero/g_m2_out_max_abs, fed by m2_beam_poll.
         *   (b) publish the completed half to main: pending_half FIRST, then ready (ordering contract
         *       at the s_m2_ready definition). Previous frame still unconsumed (ready set) -> count an
         *       overrun and OVERWRITE with the latest half: drop-oldest, never block, never queue.
         *       OVERRUN SIGNAL SEMANTICS (R56 MINOR-1): a dropped frame is a SPLICE in the input each
         *       of the 8 FiraChannelState delay lines sees vs the real audio stream -> after recovery
         *       the filters ring out a ~ntaps-sample transient (an audible glitch per overrun event),
         *       NOT data corruption -- state stays consistent with the spliced stream it was fed.
         * TX POLICY when compute is not ready = KEEP-LAST (the ISR does NOT touch the TX half; the DMA
         * re-transmits its previous contents). WHY keep-last and not silence-fill:
         *   (1) zero ISR cycles -- a 512-word zero-fill would re-grow the very ISR we are evacuating;
         *   (2) audibly milder -- repeating the previous 1.33ms beam frame keeps energy continuous (a
         *       brief stutter at worst); a zero fill guarantees TWO hard discontinuities per overrun
         *       (signal->0 and 0->signal) = a click every time;
         *   (3) honest failure signature -- init zeroes the TX ping-pong, so output before the FIRST
         *       computed frame is silence; a stuck main produces an audible looping last-frame PLUS a
         *       growing g_m2_overrun_count (silence-fill would be ambiguous with a dead codec). */
        (void)tx;                                 /* TX half untouched in the ISR (keep-last policy) */
        {
            uint32_t f;
            for (f = 0u; f < M1_FRAME; f++) {
                int32_t sample = rx[f];
                uint32_t a = (sample < 0) ? (uint32_t)(-(int64_t)sample) : (uint32_t)sample;
                if (sample != 0) nz++;
                if (a > peak) peak = a;
            }
            g_m1_nonzero_samples += nz;
            if (peak > g_m1_max_abs_sample) g_m1_max_abs_sample = peak;
        }
        if (s_m2_ready != 0u) g_m2_overrun_count++;   /* main missed a frame -> drop-oldest (counted) */
        s_m2_pending_half = half;                     /* publish the half BEFORE the ready flag */
        s_m2_ready = 1u;
#else
        {
            uint32_t f, s8;
            /* FAN-OUT 1->8: for each of the 64 frames, take the single packed RX sample and write it into
             * all 8 contiguous TX slots of that frame. RX packed (1 word/frame); TX unpacked 8 words/frame. */
            for (f = 0u; f < M1_FRAME; f++) {
                int32_t sample = rx[f];                 /* the one mono sample for frame f (RX packed) */
                uint32_t a = (sample < 0) ? (uint32_t)(-(int64_t)sample) : (uint32_t)sample;
                int32_t *txf = &tx[f * M1_TX_SLOTS];    /* base of this frame's 8 TX slots */
                for (s8 = 0u; s8 < M1_TX_SLOTS; s8++) txf[s8] = sample;   /* identical to all 8 slots */
                if (sample != 0) nz++;
                if (a > peak) peak = a;
            }
            g_m1_nonzero_samples += nz;
            if (peak > g_m1_max_abs_sample) g_m1_max_abs_sample = peak;
        }
#endif
        g_m1_rx_block_count++;
        g_m1_tx_block_count++;
        s_m1_pp_index++;
    }
    t1 = bench_cyc_target();   /* CCNT bracket CLOSE */

    g_m1_cb_cyc_last = t1 - t0;                       /* raw callback body cost (M1: io-callback; M2: io+beam) */
    if (g_m1_cb_cyc_last > g_m1_cb_cyc_max) g_m1_cb_cyc_max = g_m1_cb_cyc_last;
    if (g_m1_cb_cyc_last < g_m1_cb_cyc_min) g_m1_cb_cyc_min = g_m1_cb_cyc_last;

    /* FG (stream-live, anti-false-green): live iff blocks grew AND non-zero audio seen. Dead codec/DMA ->
     * rx_block_count stays 0; silent/dead input -> nonzero_samples stays 0; either keeps FG from latching. */
    if (g_m1_rx_block_count > 0u && g_m1_nonzero_samples > 0u) g_m1_fg_stream_live = 1;

#if M2_FIRA_INLOOP
    /* M2 beam-live FG latch MOVED to m2_beam_poll (WO-S6-M2FIX): the beam output it gates on is now
     * produced in main context, so the latch lives where the stats are written. Latch condition and
     * its anti-false-green property are UNCHANGED (see m2_beam_poll). */
#endif
}

#if M2_FIRA_INLOOP
/* ---- WO-S6-M2FIX: main-context beam service. Called from the m1_main.c while(1) idle loop (M2 build
 *      only; the call there is #if-guarded so the M1 build is byte-identical). Runs the SAME whole-frame
 *      8ch FIRA broadside rebuild as the pre-fix ISR path -- but from MAIN context, where the
 *      fira_tree.c:481 g_FIRTaskDoneCount busy-wait CAN be released by the FIR DONE interrupt (the
 *      board-verified H1/H2 working mode).
 *      RACE LEDGER (ISR can preempt at any point):
 *        - claim order = read pending half, THEN clear ready, THEN compute. A new RX-done DURING the
 *          compute sees ready==0 -> publishes normally, NO overrun, serviced on the next poll call.
 *        - the 1-2 instruction window between reading the half and clearing ready: an RX-done landing
 *          exactly there counts an overrun and its half is then dropped by our clear -- honest
 *          accounting (a dropped frame is counted as dropped). Clearing ready BEFORE reading the half
 *          would instead allow the same half to be computed twice = the cross-frame FIRA state advances
 *          twice on one input (state corruption) -- that order is deliberately NOT used.
 *      BUFFER TIMING: pending half h is the half the RX DMA just completed; the RX DMA now fills h^1 and
 *      the TX DMA has just wrapped away from h, so rx[h] is stable and tx[h] is not read by the DMA for
 *      ~1.33ms. Beam compute ~130us (H2 account, off-board caliber) fits well inside when overrun==0.
 *      DEGRADATION (R56 honest rewording): g_m2_overrun_count only proves CLAIM latency < the frame
 *      period -- it does NOT bound the read/write of the half. When claim+compute lands inside
 *      (frame_period - beam_cost, frame_period), the DMA can wrap into the half mid-compute (torn
 *      RX read and/or TX write) while overrun stays ==0 -- an overrun-blind band. g_m2_beam_cyc_max
 *      (beam-only CCNT bracket below) makes the compute leg of that sum observable: blind-band entry
 *      requires beam_cyc approaching the frame budget, so beam_cyc_max << 1.33ms-equivalent cycles
 *      rules the band out; expected steady state is overrun ~0 AND beam_cyc_max far below budget. */
void m2_beam_poll(void)
{
    uint32_t half, nz, peak, t0, t1;

    if (s_m2_ready == 0u) return;            /* nothing pending (idle poll) */
    half = s_m2_pending_half;                /* claim: read the half ... */
    s_m2_ready = 0u;                         /* ... THEN release the slot (race ledger above) */

    nz = 0u; peak = 0u;
    /* may spin on the FIR DONE interrupt inside the frozen fira_tree.c -- LEGAL here (main context).
     * R56 MAJOR-3: the CCNT bracket spans ONLY this call (R42: the span IS the caliber); the FG
     * accumulation / counters / latch below are deliberately OUTSIDE it. */
    t0 = bench_cyc_target();
    m2_fira_beam_frame(s_m1_rx_buf[half], s_m1_tx_buf[half], &nz, &peak);
    t1 = bench_cyc_target();
    g_m2_beam_cyc_last = t1 - t0;
    if (g_m2_beam_cyc_last > g_m2_beam_cyc_max) g_m2_beam_cyc_max = g_m2_beam_cyc_last;
    if (g_m2_beam_cyc_last < g_m2_beam_cyc_min) g_m2_beam_cyc_min = g_m2_beam_cyc_last;   /* WO-S7-B6 floor */

    g_m2_out_nonzero += nz;
    if (peak > g_m2_out_max_abs) g_m2_out_max_abs = peak;
    g_m2_poll_count++;

    /* M2 beam-live FG (moved from the ISR -- latch condition UNCHANGED, anti-false-green preserved):
     * green ONLY if blocks grew AND the FIRA beam produced non-zero output. A stubbed/dead FIRA
     * (memset 0 / not-linked) keeps g_m2_out_nonzero at 0 -> never latches (placeholder FAILs,
     * DSP/FIRA special gate). */
    if (g_m1_rx_block_count > 0u && g_m2_out_nonzero > 0u) g_m2_fg_beam_live = 1;
}
#endif /* M2_FIRA_INLOOP */

#if M2_STATIC_TXTEST
#if M2_STXT_LOCALIZE
#include "m2_static_txtest375_table.h"   /* python-baked 375Hz EQUAL-amp cycle (128 mono); board does NO arithmetic */
/* POLARITY LOCALIZATION variant (EXP_STATIC_POL375.md). Instead of the full 8-ch 2250 Dolph tone, emit an
 * EQUAL-amplitude 375Hz tone on a SELECTABLE subset of channels. g_stxt_ch_mask bit c enables channel c
 * (edit via JTAG between measurements); de-selected channels are filled with 0 = silent. 375Hz's single
 * cycle spans the two ping-pong halves (half0 = samples 0..63, half1 = 64..127) so the loop half0,half1,
 * half0,... is seamless (and half-swap-safe: a global phase offset hits all channels equally). Solo one
 * channel (mask = 1u<<c) => alive-check + map channel->element; play a pair (mask = (1u<<R)|(1u<<K),
 * R = a central reference channel found in Phase A) and compare both-vs-each-alone at the pair bisector:
 * same polarity adds (~+6dB), opposite cancels (deep null). Requires M2_FIRA_INLOOP=1 &&
 * M2_STATIC_TXTEST=1. The m2_beam_poll() call stays #if-skipped;
 * m2_stxt_poll_mask() re-applies the buffer ONCE each time the tester changes the mask (no per-frame
 * write -> static between measurements). */
volatile uint32_t g_stxt_ch_mask   = 0xFFu;         /* bit c = channel c audible; JTAG-editable; default all-on */
static uint32_t   s_stxt_mask_seen = 0xFFFFFFFFu;   /* != default => first poll applies once */

static void m2_stxt_apply(void)
{
    int f, c;
    for (f = 0; f < (int)M1_FRAME; f++) {            /* 64 frames per half */
        for (c = 0; c < (int)M1_TX_SLOTS; c++) {     /* 8 TDM slots (channels) */
            int on = (int)((g_stxt_ch_mask >> c) & 1u);
            s_m1_tx_buf[0][f * (int)M1_TX_SLOTS + c] = on ? M2_STXT375[f]      : 0;  /* half0 = n 0..63   */
            s_m1_tx_buf[1][f * (int)M1_TX_SLOTS + c] = on ? M2_STXT375[f + 64] : 0;  /* half1 = n 64..127 */
        }
    }
    s_stxt_mask_seen = g_stxt_ch_mask;              /* 63*8+7 = 511 < 512 : in bounds */
}

void m2_static_txtest_fill(void) { m2_stxt_apply(); }                                   /* ONCE from m1_main */
void m2_stxt_poll_mask(void)     { if (g_stxt_ch_mask != s_stxt_mask_seen) m2_stxt_apply(); }  /* main idle */
#else  /* !M2_STXT_LOCALIZE : original static 2250 Dolph fill (byte-identical to commit 4bf18b6) */
#include "m2_static_txtest_table.h"   /* python-baked final Q31 table (512 = one TX half); board does NO arithmetic */
/* WO diagnostic (EXP_STATIC_TXTEST.md): overwrite BOTH TX halves with the static in-phase Dolph 2250Hz
 * tone. Called ONCE from m1_main after m1_loopback_init; the m2_beam_poll() call is #if-skipped in the
 * same build, so nothing ever rewrites s_m1_tx_buf again -> the TX DMA re-transmits a fixed waveform
 * forever -> read/write tearing (A) is impossible by construction. This partitions A (write-path/timing)
 * from B (DAC/analog polarity): static-directional => A; static-still-flat => B. Requires M2_FIRA_INLOOP=1.
 * M2_STXT_TBL is 512 words = M1_TX_HALF_WORDS (64 frames x 8 slots); both are 512 by construction. */
void m2_static_txtest_fill(void)
{
    int i;
    for (i = 0; i < M1_TX_HALF_WORDS; i++) {
        s_m1_tx_buf[0][i] = M2_STXT_TBL[i];
        s_m1_tx_buf[1][i] = M2_STXT_TBL[i];
    }
}
#endif /* M2_STXT_LOCALIZE */
#endif /* M2_STATIC_TXTEST */

/* ---- build the circular ping-pong descriptor rings (ALT.c:250-284 pattern). RX/TX have DIFFERENT
 *   XCount now (RX = 64 words/half packed, TX = 512 words/half). ---- */
static void m1_prepare_descriptors(void)
{
    s_m1_rx_desc[0].pStartAddr = (int *)s_m1_rx_buf[0];
    s_m1_rx_desc[0].Config     = ENUM_DMA_CFG_XCNT_INT;
    s_m1_rx_desc[0].XCount     = M1_RX_HALF_WORDS;     /* packed: 1 slot x 64 = 64 words */
    s_m1_rx_desc[0].XModify    = (int)M1_WORD_BYTES;
    s_m1_rx_desc[0].YCount     = 0;
    s_m1_rx_desc[0].YModify    = 0;
    s_m1_rx_desc[0].pNxtDscp   = &s_m1_rx_desc[1];

    s_m1_rx_desc[1].pStartAddr = (int *)s_m1_rx_buf[1];
    s_m1_rx_desc[1].Config     = ENUM_DMA_CFG_XCNT_INT;
    s_m1_rx_desc[1].XCount     = M1_RX_HALF_WORDS;
    s_m1_rx_desc[1].XModify    = (int)M1_WORD_BYTES;
    s_m1_rx_desc[1].YCount     = 0;
    s_m1_rx_desc[1].YModify    = 0;
    s_m1_rx_desc[1].pNxtDscp   = &s_m1_rx_desc[0];

    s_m1_tx_desc[0].pStartAddr = (int *)s_m1_tx_buf[0];
    s_m1_tx_desc[0].Config     = ENUM_DMA_CFG_XCNT_INT;
    s_m1_tx_desc[0].XCount     = M1_TX_HALF_WORDS;     /* unpacked window: 8 slot x 64 = 512 words */
    s_m1_tx_desc[0].XModify    = (int)M1_WORD_BYTES;
    s_m1_tx_desc[0].YCount     = 0;
    s_m1_tx_desc[0].YModify    = 0;
    s_m1_tx_desc[0].pNxtDscp   = &s_m1_tx_desc[1];

    s_m1_tx_desc[1].pStartAddr = (int *)s_m1_tx_buf[1];
    s_m1_tx_desc[1].Config     = ENUM_DMA_CFG_XCNT_INT;
    s_m1_tx_desc[1].XCount     = M1_TX_HALF_WORDS;
    s_m1_tx_desc[1].XModify    = (int)M1_WORD_BYTES;
    s_m1_tx_desc[1].YCount     = 0;
    s_m1_tx_desc[1].YModify    = 0;
    s_m1_tx_desc[1].pNxtDscp   = &s_m1_tx_desc[0];
}

/* ---- TWI bring-up (ALT.c:508-546) ---- */
static int m1_twi_init(void)
{
    if (adi_twi_Open(M1_TWI_DEVNUM, ADI_TWI_MASTER, s_m1_twi_mem, ADI_TWI_MEMORY_SIZE, &s_m1_htwi)
        != ADI_TWI_SUCCESS) { s_m1_htwi = NULL; return 1; }
    if (adi_twi_SetPrescale(s_m1_htwi, M1_TWI_PRESCALE)   != ADI_TWI_SUCCESS) return 1;
    if (adi_twi_SetBitRate(s_m1_htwi, M1_TWI_BITRATE)     != ADI_TWI_SUCCESS) return 1;
    if (adi_twi_SetDutyCycle(s_m1_htwi, M1_TWI_DUTYCYCLE) != ADI_TWI_SUCCESS) return 1;
    return 0;
}

/* ---- ADAU1962A DAC bring-up: PLL (ALT.c:578-617) + 28-register table ---- */
static int m1_dac_init(void)
{
    int i; volatile int d;
    if (adi_twi_SetHardwareAddress(s_m1_htwi, M1_TWI_ADDR_1962) != ADI_TWI_SUCCESS) return 1;
    /* PLL: PLL_CLK_CTRL0=0x01 (PUP) -> 0x05 -> PLL_CLK_CTRL1=0x22 (MCS 256xfS @48k); poll lock off-path */
    m1_twi_w8(ADAU1962_PLL_CTL_CTRL0, 0x01); for (d = 0xffff; d > 0; d--) { /* settle */ }
    m1_twi_w8(ADAU1962_PLL_CTL_CTRL0, 0x05); for (d = 0xffff; d > 0; d--) { }
    m1_twi_w8(ADAU1962_PLL_CTL_CTRL1, 0x22); for (d = 0xffff; d > 0; d--) { }
    for (i = 0; i < 28; i++) m1_twi_w8(s_m1_dac_cfg[i].reg, s_m1_dac_cfg[i].val);
    return 0;
}

/* ---- ADAU1979 ADC bring-up: PLL (ALT.c:641-669) + 16-register table ---- */
static int m1_adc_init(void)
{
    int i; volatile int d;
    if (adi_twi_SetHardwareAddress(s_m1_htwi, M1_TWI_ADDR_1979) != ADI_TWI_SUCCESS) return 1;
    m1_twi_w8(ADAU1979_REG_POWER, 0x01);                         /* power up */
    m1_twi_w8(ADAU1979_REG_PLL,   0x03); for (d = 0xffff; d > 0; d--) { /* PLL settle */ }
    for (i = 0; i < 16; i++) m1_twi_w8(s_m1_adc_cfg[i].reg, s_m1_adc_cfg[i].val);
    return 0;
}

/* ---- SPU: SPORT4A/B as secure masters (ALT.c:453-476) ---- */
static int m1_spu_init(void)
{
    if (adi_spu_Init(0, s_m1_spu_mem, NULL, NULL, &s_m1_hspu) != ADI_SPU_SUCCESS) return 1;
    if (adi_spu_EnableMasterSecure(s_m1_hspu, M1_SPORT_4A_SPU, true) != ADI_SPU_SUCCESS) return 1;
    if (adi_spu_EnableMasterSecure(s_m1_hspu, M1_SPORT_4B_SPU, true) != ADI_SPU_SUCCESS) return 1;
    return 0;
}

/* ---- SPORT4 TDM ping-pong (ALT.c:286-345). RX three-layer single-slot (see file header). ---- */
static int m1_sport_init(void)
{
    /* 4A = Tx to DAC, 4B = Rx from ADC */
    if (adi_sport_Open(M1_SPORT_DEV_4, ADI_HALF_SPORT_A, ADI_SPORT_DIR_TX, ADI_SPORT_MC_MODE,
                       s_m1_sport_mem_tx, ADI_SPORT_MEMORY_SIZE, &s_m1_hsport_tx) != 0) return 1;
    if (adi_sport_Open(M1_SPORT_DEV_4, ADI_HALF_SPORT_B, ADI_SPORT_DIR_RX, ADI_SPORT_MC_MODE,
                       s_m1_sport_mem_rx, ADI_SPORT_MEMORY_SIZE, &s_m1_hsport_rx) != 0) return 1;

    /* ---- TX (4A): 32-bit word, 8-slot MC window, all 8 slots selected (TX fan-out drives all 8) ---- */
    if (adi_sport_ConfigData(s_m1_hsport_tx, ADI_SPORT_DTYPE_SIGN_FILL, 31, false, false, false) != 0) return 1;
    if (adi_sport_ConfigClock(s_m1_hsport_tx, 32, false, false, false) != 0) return 1;
    if (adi_sport_ConfigFrameSync(s_m1_hsport_tx, 31, false, false, false, true, false, false) != 0) return 1;
    if (adi_sport_ConfigMC(s_m1_hsport_tx, 1u, (uint8_t)(M1_TX_SLOTS - 1u), 0u, true) != 0) return 1; /* WSIZE = 8 slots */
    if (adi_sport_SelectChannel(s_m1_hsport_tx, 0u, (uint8_t)(M1_TX_SLOTS - 1u)) != 0) return 1;       /* TX: slots 0..7 */

    /* ---- RX (4B): three-layer single-slot 512B ----
     * LAYER-1 WINDOW: WSIZE = 8 slots to MATCH the TDM8 master frame (FS period is the DAC master's). */
    if (adi_sport_ConfigData(s_m1_hsport_rx, ADI_SPORT_DTYPE_SIGN_FILL, 31, false, false, false) != 0) return 1;
    if (adi_sport_ConfigClock(s_m1_hsport_rx, 32, false, false, false) != 0) return 1;
    if (adi_sport_ConfigFrameSync(s_m1_hsport_rx, 31, false, false, false, true, false, false) != 0) return 1;
    if (adi_sport_ConfigMC(s_m1_hsport_rx, 1u, (uint8_t)(M1_TX_SLOTS - 1u), 0u, true) != 0) return 1;  /* WSIZE = 8 (match master frame) */
    /* LAYER-2 CHANNEL-SELECT: enable ONLY slot 0 -> (0u, M1_RX_SLOTS-1u) = (0u,0u) for 1 captured slot.
     * [board-confirm-CRITICAL]: HRM proves slot0-only is HARDWARE-legal (WSIZE/CS independent, R36). The
     * driver wrapper MAY floor select at 2 -> CTO board-grep G1-G2. If it floors: set M1_RX_SLOTS=2 in the
     * header (-> RX buffer auto 1024B) -- the ONLY change, no structural edit here. */
    if (adi_sport_SelectChannel(s_m1_hsport_rx, 0u, (uint8_t)(M1_RX_SLOTS - 1u)) != 0) return 1;        /* RX: slot 0 only */
    /* LAYER-3 PACKING (MCPDE=1): set by the BSP sport config (adi_sport_config_2156x.h MCPDE=1u). Packed
     * MC DMA writes 1 word per ENABLED channel -> 1 word/frame for RX -> 64 words/half -> 512B (2 halves).
     * [board-confirm]: confirm the runtime ConfigMC/driver honors the static MCPDE=1; if the wrapper forces
     * unpacked, RX buffer would be window-sized (8 words/frame) -> see grep G3. */

    if (adi_sport_RegisterCallback(s_m1_hsport_rx, m1_sport_rx_callback, NULL) != 0) return 1;

    m1_prepare_descriptors();

    if (adi_sport_DMATransfer(s_m1_hsport_rx, &s_m1_rx_desc[0], M1_DMA_NUM_DESC,
                              ADI_PDMA_DESCRIPTOR_LIST, ADI_SPORT_CHANNEL_PRIM) != 0) return 1;
    if (adi_sport_DMATransfer(s_m1_hsport_tx, &s_m1_tx_desc[0], M1_DMA_NUM_DESC,
                              ADI_PDMA_DESCRIPTOR_LIST, ADI_SPORT_CHANNEL_PRIM) != 0) return 1;

    if (adi_sport_Enable(s_m1_hsport_rx, true) != 0) return 1;
    if (adi_sport_Enable(s_m1_hsport_tx, true) != 0) return 1;
    return 0;
}

#if M2_FIRA_INLOOP
/* ---- M2 FIRA one-time setup (OPENING-1/4): the SAME init sequence the H2 harness uses
 *      (h2_dma_isr_measure.c:138-150): fira_tree_setup -> tfb_set_coeffs(core golden Q15) ->
 *      fira_channel_init(&s_m2_fa[c], 64) x8. Called ONCE at init, NOT in the frame budget
 *      (fira_tree.h:157-159 real-time discipline). Returns 0 ok, non-zero = no-FIRA/setup-fail. ---- */
static int m2_fira_setup(void)
{
    int c, rc;
    g_m2_setup_rc = -99; g_m2_out_nonzero = 0u; g_m2_out_max_abs = 0u;
    g_m2_fg_beam_live = -99; g_m2_valid = 0;
    g_m2_overrun_count = 0u; g_m2_poll_count = 0u;   /* WO-S6-M2FIX counters */
    g_m2_beam_cyc_last = 0u; g_m2_beam_cyc_max = 0u; /* R56 MAJOR-3 beam-only CCNT bracket */
    g_m2_beam_cyc_min = 0xFFFFFFFFu;                 /* WO-S7-B6 floor (sentinel until the first beam frame) */
#if M2_SEG_CYC
    g_m2_seg_w_cyc_last = 0u;   g_m2_seg_w_cyc_max = 0u;
    g_m2_seg_ana_cyc_last = 0u; g_m2_seg_ana_cyc_max = 0u;
    g_m2_seg_syn_cyc_last = 0u; g_m2_seg_syn_cyc_max = 0u;
    g_m2_seg_tx_cyc_last = 0u;  g_m2_seg_tx_cyc_max = 0u;
#endif
#if M2_SELFTEST
    g_m2_selftest_rc = -99; g_m2_selftest_frames = 0u; g_m2_selftest_cyc = 0u;
    for (c = 0; c < DOLPH_W8_NCH; c++) {
        g_m2_selftest_pass[c] = 0; g_m2_selftest_crc[c] = 0u; g_m2_selftest_crc_core[c] = 0u;
        g_m2_selftest_mismatch_sb[c] = -1; g_m2_selftest_mismatch_idx[c] = -1; g_m2_selftest_cyc_ch[c] = 0u;
    }
#endif
    s_m2_ready = 0u; s_m2_pending_half = 0u;         /* WO-S6-M2FIX ISR->main handoff state */

    rc = fira_tree_setup();          /* Open -> RegisterCallback -> CreateTask -> FixedPointEnable(SIGNED) */
    g_m2_setup_rc = rc;
    if (rc != 0) return 1;           /* no FIRA on this host / setup failed -> honest fail (FG2, no fake) */

    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);                  /* core (golden) Q15 halfband coeffs */
    for (c = 0; c < DOLPH_W8_NCH; c++)
        fira_channel_init(&s_m2_fa[c], (uint16_t)M1_FRAME);      /* 8 per-channel states, zero-init */
    return 0;
}

#if M2_SELFTEST
/* ============================================================================================
 * WO-S7-B6 M2_SELFTEST -- EIGHT-ANCHOR INIT SELF-TEST (DEC-S7-IMPL-01 item 2; S7_VERIFICATION_PLAN B6-4;
 * DEC-S6-M2-BOARD-PASS-01 anti-false-green boundary: "functional PASS != bit-exact verified").
 * ------------------------------------------------------------------------------------------
 * WHAT: after m2_fira_setup() succeeded and BEFORE m1_sport_init() arms the stream, drive the SAME in-loop
 *   FIRA chain the live beam uses (s_m2_fa[c] + fira_tfb_analyze, CALL-ONLY into frozen fira_tree.c) with the
 *   frozen R14 excitation CHIRP_INPUT (64 x 1024 frames) under EXACTLY the F5 eight-anchor definition
 *   (gen_f5_goldens.c:78-98 generator == fira_regression.c:328-372 board harness, commit 44a99e8 [L1]):
 *     for c = 0..7:  fira_channel_init(&s_m2_fa[c], 64); per frame  xw[i] = (int32_t)(((int64_t)w_q15[c]*x[i])>>15)
 *                    -> fira_tfb_analyze -> stream the 4 subbands sb0|sb1|sb2|sb3 into one CRC32
 *                    -> compare with g_f5_golden_crc[c] (dolph_f5_goldens.h, frozen [L2] desktop golden).
 *   The frozen core tfb_analyze runs side by side over the same xw (it is linked in every M2 build; F5 does the
 *   same) so a FAIL is localizable: first mismatching subband / index (FIRA != core) and a separate live core
 *   CRC (core != anchor => chirp/weight/core drifted, not FIRA). PASS[c] = F5's three-term AND (:369-371).
 * WEIGHT INDEX = CHANNEL INDEX, NO chmap permutation, even in an M2_CHMAP_FIX build: the eight anchors are
 *   DEFINED with w_q15[c] on channel c (gen_f5_goldens.c:82). The self-test verifies the CHAIN (weight arith +
 *   FIRA analyze bit-exactness on THIS board/build), not the channel->position mapping; permuting here would
 *   change which anchor each channel must hit and fail for a reason unrelated to the chain (host harness
 *   s7_selftest_host.c mode neg-chmap demonstrates that FAIL).
 * NEGATIVE CONTROL (-DM2_SELFTEST_NEGCTRL=1): every channel uses the unity weight DOLPH_W8_ONE (32768). Same
 *   FG1 double-guard as gen_f5_goldens.c -DF5_GEN_UNWEIGHTED: all 8 CRCs MUST collapse to the F4 unity anchor
 *   0x2E0D8C6E, only c=7 (whose real weight IS unity) passes, rc = 7. That readout is the evidence that this
 *   self-test really depends on the per-channel weights and is not a constant.
 * NOT run when FIRA setup failed (fira_tree_setup != 0, e.g. built without FIRA_USE_REAL_ADI_FIR_HEADER):
 *   rc = -1, honest, nothing faked (FG2). A FIRA that is linked but stubbed (#else placeholder zero-fill) FAILS
 *   every channel with mismatch_sb != -1 (the FG2 placeholder proof, host mode neg-stub).
 * SCRATCH: reuses s_m2_xw / s_m2_sb0..3 (free -- the SPORT is not armed yet) + one core state + 4 core subband
 *   buffers below (~2.8 KB, default placement, init-time only). Q boundary: CHIRP_INPUT is full-Q31 and fed
 *   with NO shift exactly as F5 did (M2_Q_BOUNDARY_SURVEY 3.1); an M2_RX_RIGHT_ALIGNED build self-tests the
 *   same chain (the shifts sit in m2_fira_beam_frame, which the self-test does not call).
 * AFTER the run: fira_channel_init x8 again + zero the shared scratch, so the live stream starts from the
 *   zero delay line exactly as a non-selftest build does (ST1: the self-test advanced every channel state
 *   through 1024 chirp frames; that state must not leak into the first live frame).
 * COST: init-time only (never in the frame budget); wall CCNT in g_m2_selftest_cyc / _cyc_ch (raw, C9).
 * MEMORY: CHIRP_INPUT = 65536 x int32 = 256 KB const, pinned to L2 via the pragma below (input section
 *   seg_l2_dmda_bw -> m1_app.ldf dxe_l2_data_bw > mem_L2_bw 0x20000000-0x200F9FFF, the [L1] ADI-example section
 *   name, POST adc_dac_test.c:43 / H2_MAP_PLACEMENT_ADJUDICATION.md:114). The core reads it (cached L2, read-only
 *   -> coherency-free); the FIRA DMA never touches it (it reads s_m2_xw in L1 like the live path). BOARD-CONFIRM:
 *   the .map must show CHIRP_INPUT inside mem_L2_bw and Block 0/1 untouched by it (runbook check M1).
 * ============================================================================================ */
#pragma section("seg_l2_dmda_bw")
#include "chirp_input.h"                 /* [frozen, read-only] CHIRP_INPUT[CHIRP_INPUT_N=65536]; pragma pins THIS definition to L2 */

#define M2_SELFTEST_NFR   ((uint32_t)CHIRP_INPUT_N / M1_FRAME)   /* 1024 frames = BENCH_NFR, the full F5 span */

static TreeChannelState s_m2_st_core;            /* frozen-core reference state (re-init per channel; init-time only) */
static int32_t s_m2_st_csb0[M1_FRAME / 8];        /* core-side subbands for the per-sample compare */
static int32_t s_m2_st_csb1[M1_FRAME / 4];
static int32_t s_m2_st_csb2[M1_FRAME / 2];
static int32_t s_m2_st_csb3[M1_FRAME];

/* Incremental CRC32 (IEEE 802.3 reflected poly 0xEDB88320, init 0xFFFFFFFF, final ^0xFFFFFFFF), each int32 fed as
 * 4 little-endian bytes. VERBATIM twin (C89 form, R16) of fira_regression.c:71-81 == gen_f5_goldens.c:54-64 (the
 * eight anchors' generator) == sprint7/dsp/host/s7_selftest_host.c s7_crc32_update. Same bytes, same order. */
static void m2_st_crc32_update(uint32_t *c, const int32_t *d, int n)
{
    int i, b, k;
    for (i = 0; i < n; i++) {
        uint32_t v = (uint32_t)d[i];
        for (b = 0; b < 4; b++) {
            uint8_t by = (uint8_t)(v >> (8 * b));
            *c ^= by;
            for (k = 0; k < 8; k++) *c = (*c & 1u) ? (*c >> 1) ^ 0xEDB88320u : (*c >> 1);
        }
    }
}

static void m2_selftest_run(void)
{
    const int32_t *chirp = CHIRP_INPUT;
    const int sz[4] = { M1_FRAME / 8, M1_FRAME / 4, M1_FRAME / 2, M1_FRAME };
    const int32_t *fb[4];
    const int32_t *cb[4];
    uint32_t c, f, i, t0, t1, tc0, tc1;
    int b, nfail = 0;

    fb[0] = s_m2_sb0;     fb[1] = s_m2_sb1;     fb[2] = s_m2_sb2;     fb[3] = s_m2_sb3;
    cb[0] = s_m2_st_csb0; cb[1] = s_m2_st_csb1; cb[2] = s_m2_st_csb2; cb[3] = s_m2_st_csb3;

    t0 = bench_cyc_target();                                     /* whole-run wall bracket OPEN */
    for (c = 0u; c < (uint32_t)DOLPH_W8_NCH; c++) {
#if M2_SELFTEST_NEGCTRL
        const int32_t w = DOLPH_W8_ONE;                          /* NEGATIVE CONTROL: unity on every channel */
#else
        const int32_t w = g_dolph_w8_q15[c];                     /* anchor definition: weight index == channel index (NO chmap) */
#endif
        uint32_t cf = 0xFFFFFFFFu, cc = 0xFFFFFFFFu;             /* streaming CRC state: FIRA path / core path */
        int mis = -1;                                            /* first per-sample mismatch found? (idx) */

        tc0 = bench_cyc_target();
        fira_channel_init(&s_m2_fa[c], (uint16_t)M1_FRAME);      /* same init as the live path (zero delay line) */
        tfb_channel_init(&s_m2_st_core);

        for (f = 0u; f < M2_SELFTEST_NFR; f++) {
            const int32_t *xin = &chirp[f * M1_FRAME];
            /* input-scale weight, bit-exact F5 arithmetic (f5_apply_w / gen_f5_goldens.c apply_w): Q15 x Q31 >> 15 */
            for (i = 0u; i < M1_FRAME; i++)
                s_m2_xw[i] = (int32_t)(((int64_t)w * (int64_t)xin[i]) >> DOLPH_W8_QBITS);

            fira_tfb_analyze(&s_m2_fa[c], s_m2_xw, (uint16_t)M1_FRAME,
                             s_m2_sb0, s_m2_sb1, s_m2_sb2, s_m2_sb3);              /* device under test */
            tfb_analyze(&s_m2_st_core, s_m2_xw, (uint16_t)M1_FRAME,
                        s_m2_st_csb0, s_m2_st_csb1, s_m2_st_csb2, s_m2_st_csb3);  /* frozen-core reference */

            for (b = 0; b < 4; b++) {
                if (mis < 0) {
                    int j;
                    for (j = 0; j < sz[b]; j++) {
                        if (fb[b][j] != cb[b][j]) {
                            g_m2_selftest_mismatch_sb[c]  = b;
                            g_m2_selftest_mismatch_idx[c] = (int)(f * (uint32_t)sz[b]) + j;
                            mis = g_m2_selftest_mismatch_idx[c];
                            break;
                        }
                    }
                }
                m2_st_crc32_update(&cf, fb[b], sz[b]);           /* sb0|sb1|sb2|sb3 order, every frame */
                m2_st_crc32_update(&cc, cb[b], sz[b]);
            }
            g_m2_selftest_frames++;
        }

        g_m2_selftest_crc[c]      = cf ^ 0xFFFFFFFFu;
        g_m2_selftest_crc_core[c] = cc ^ 0xFFFFFFFFu;
        /* F5 PASS (fira_regression.c:369-371): no mismatch AND FIRA == live core AND live core == frozen anchor */
        g_m2_selftest_pass[c] = ((mis < 0)
                               && (g_m2_selftest_crc[c] == g_m2_selftest_crc_core[c])
                               && (g_m2_selftest_crc_core[c] == g_f5_golden_crc[c])) ? 1 : 0;
        if (g_m2_selftest_pass[c] == 0) nfail++;
        tc1 = bench_cyc_target();
        g_m2_selftest_cyc_ch[c] = tc1 - tc0;
    }
    t1 = bench_cyc_target();                                     /* whole-run wall bracket CLOSE */
    g_m2_selftest_cyc = t1 - t0;
    g_m2_selftest_rc  = nfail;                                   /* 0 = all 8 PASS; n = failing channels */

    /* clean slate for the live stream (ST1): re-zero all 8 FIRA channel states + the shared scratch */
    for (c = 0u; c < (uint32_t)DOLPH_W8_NCH; c++)
        fira_channel_init(&s_m2_fa[c], (uint16_t)M1_FRAME);
    for (i = 0u; i < M1_FRAME; i++) { s_m2_xw[i] = 0; s_m2_chout[i] = 0; s_m2_sb3[i] = 0; }
    for (i = 0u; i < M1_FRAME / 2; i++) s_m2_sb2[i] = 0;
    for (i = 0u; i < M1_FRAME / 4; i++) s_m2_sb1[i] = 0;
    for (i = 0u; i < M1_FRAME / 8; i++) s_m2_sb0[i] = 0;
}
#endif /* M2_SELFTEST */
#endif /* M2_FIRA_INLOOP */

int m1_loopback_init(void)
{
    volatile int d;
    uint32_t b, k;

    /* reset readouts */
    g_m1_rx_block_count = 0u; g_m1_tx_block_count = 0u;
    g_m1_cb_cyc_last = 0u; g_m1_cb_cyc_max = 0u; g_m1_cb_cyc_min = 0xFFFFFFFFu;
    g_m1_nonzero_samples = 0u; g_m1_max_abs_sample = 0u;
    g_m1_fg_stream_live = -99; g_m1_valid = 0;
    s_m1_pp_index = 0u;

    /* zero both ping-pong directions so a dead RX path outputs silence, never stale L1 garbage (honest). */
    for (b = 0u; b < 2u; b++) {
        for (k = 0u; k < M1_RX_HALF_WORDS; k++) s_m1_rx_buf[b][k] = 0;
        for (k = 0u; k < M1_TX_HALF_WORDS; k++) s_m1_tx_buf[b][k] = 0;
    }

    if (m1_spu_init() != 0) return 1;          /* secure SPORT masters */
    /* board soft-switch + SRU pin routing are board-project responsibilities (ALT.c ConfigSoftSwitches_* +
     * SRU_Init from main); M1 assumes adi_initComponents + board SRU already routed SPORT4<->DAI1<->codecs.
     * If not, bring-up wires ConfigSoftSwitches_ADC_DAC()/_ADAU_Reset() before this. */
    (void)ConfigSoftSwitches_ADC_DAC;
    (void)ConfigSoftSwitches_ADAU_Reset;

    if (m1_twi_init() != 0) return 1;          /* TWI master for codec control */
    for (d = 0xffff; d > 0; d--) { /* codec power settle */ }
    if (m1_dac_init() != 0) return 1;          /* ADAU1962A (master) FIRST -- it drives the shared bus clocks */
    if (m1_adc_init() != 0) return 1;          /* ADAU1979 (slave) */
    (void)adi_twi_Close(s_m1_htwi); s_m1_htwi = NULL;   /* codec configured; release TWI (ALT.c:733) */

#if M2_FIRA_INLOOP
    /* OPENING-1/4: bring the FIRA beam up BEFORE the SPORT callback can fire. If FIRA setup fails, do NOT
     * arm the stream -- the callback would call into an un-setup FIRA (undefined). Honest fail (no fake). */
#if M2_SELFTEST
    /* WO-S7-B6: setup fail -> self-test honestly NOT run (rc=-1, FG2); setup ok -> run the eight-anchor
     * self-test HERE, after FIRA is up and BEFORE the SPORT is armed (scratch + main context are ours). */
    if (m2_fira_setup() != 0) { g_m2_selftest_rc = -1; return 1; }
    m2_selftest_run();
#else
    if (m2_fira_setup() != 0) return 1;        /* g_m2_setup_rc carries the rc; stream NOT armed on fail */
#endif
#endif

    if (m1_sport_init() != 0) return 1;        /* SPORT4 TDM ping-pong + callback armed */

    g_m1_valid = 1;
#if M2_FIRA_INLOOP
    g_m2_valid = 1;                            /* M2 beam path is up and the stream is armed */
#endif
    return 0;
}

int m1_loopback_stop(void)
{
    if (s_m1_hsport_rx != NULL) { (void)adi_sport_StopDMATransfer(s_m1_hsport_rx); (void)adi_sport_Close(s_m1_hsport_rx); s_m1_hsport_rx = NULL; }
    if (s_m1_hsport_tx != NULL) { (void)adi_sport_StopDMATransfer(s_m1_hsport_tx); (void)adi_sport_Close(s_m1_hsport_tx); s_m1_hsport_tx = NULL; }
#if M2_FIRA_INLOOP
    /* release the FIRA device (adi_fir_Close via fira_tree_teardown); safe to call after stream stop. */
    if (g_m2_setup_rc == 0) { fira_tree_teardown(); g_m2_setup_rc = -99; }
#endif
    return 0;
}

#else  /* desktop / non-board: honest degrade (no codec, no SPORT, no DMA) */

int m1_loopback_init(void)
{
    /* honest 0-state: no board peripherals on this host. g_m1_* stay 0/sentinel; FG never fakes green. */
    g_m1_rx_block_count = 0u; g_m1_tx_block_count = 0u;
    g_m1_cb_cyc_last = 0u; g_m1_cb_cyc_max = 0u; g_m1_cb_cyc_min = 0u;
    g_m1_nonzero_samples = 0u; g_m1_max_abs_sample = 0u;
    g_m1_fg_stream_live = 0;   /* explicit not-live on desktop (no stream) */
    g_m1_valid = 0;
    /* M2 globals honest-0 too (no FIRA + no SPORT off-board; g_m2_fira_inloop keeps the build identity). */
    g_m2_setup_rc = -99; g_m2_out_nonzero = 0u; g_m2_out_max_abs = 0u;
    g_m2_fg_beam_live = 0; g_m2_valid = 0;
#if M2_FIRA_INLOOP
    g_m2_overrun_count = 0u; g_m2_poll_count = 0u;   /* WO-S6-M2FIX counters (desktop honest-0) */
    g_m2_beam_cyc_last = 0u; g_m2_beam_cyc_max = 0u; /* R56 beam CCNT (desktop honest-0) */
    g_m2_beam_cyc_min = 0u;                          /* WO-S7-B6 floor (desktop honest-0: no beam ran) */
#if M2_SELFTEST
    g_m2_selftest_rc = -99;                          /* WO-S7-B6: never runs off-board (no FIRA, no init path) */
#endif
#endif
    return 1;                  /* non-zero: cannot run loopback off-board (honest fail, no fake) */
}

int m1_loopback_stop(void) { return 0; }

#if M2_FIRA_INLOOP
/* WO-S6-M2FIX: desktop M2 build keeps the symbol so any host harness links; no stream, no FIRA here. */
void m2_beam_poll(void) { /* honest no-op off-board */ }
#endif

#endif /* M1_TARGET_BOARD && TARGET_SHARC */
