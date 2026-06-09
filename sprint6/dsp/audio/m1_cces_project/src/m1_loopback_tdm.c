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
 * ============================================================================================ */
#ifndef M2_FIRA_INLOOP
#define M2_FIRA_INLOOP 0          /* default 0 = M1 transparent passthrough (board-PASS path preserved) */
#endif

#if M2_FIRA_INLOOP
/* M2 build pulls the frozen FIRA orchestration + core + weights (read-only call surface). Guarded so the
 * M1 transparent build (M2_FIRA_INLOOP=0) carries NONE of these includes and stays byte-clean. */
#include "fira_tree.h"           /* [frozen, call-only] FiraChannelState, fira_tree_setup/channel_init,
                                  *  fira_tfb_analyze/synthesize, fira_tree_teardown (sprint4/dsp/fira) */
#include "tree_filterbank.h"     /* [frozen, call-only] tfb_set_coeffs (core golden Q15 coeff inject) */
#include "fir_coeffs_hb63.h"     /* [frozen, read-only]  g_hb63_q15, FIR_HB63_NTAPS */
#include "dolph_w8_q15.h"        /* [frozen, read-only]  g_dolph_w8_q15[8], DOLPH_W8_NCH (broadside taper) */
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
 *      @param rx   packed mono RX frame, M1_FRAME int32 (Q31 by identity)
 *      @param tx   8-slot interleaved TX frame, M1_FRAME*M1_TX_SLOTS int32 ; tx[f*8 + c] = ch c, samp f
 *      @return     accumulates FG stats into *pnz / *ppeak over the 8-channel output. */
static void m2_fira_beam_frame(const int32_t *rx, int32_t *tx, uint32_t *pnz, uint32_t *ppeak)
{
    uint32_t c, i;
    uint32_t nz = *pnz, peak = *ppeak;

    for (c = 0u; c < (uint32_t)DOLPH_W8_NCH; c++) {
        const int32_t w = g_dolph_w8_q15[c];            /* Dolph-Cheb -20dB Q15 weight for channel c */
        /* input-scale weight (== f5_apply_w / H2:117-118): Q15 x Q31 >> 15. rx[i] is Q31 by identity. */
        for (i = 0u; i < M1_FRAME; i++)
            s_m2_xw[i] = (int32_t)(((int64_t)w * (int64_t)rx[i]) >> 15);

        /* FIRA analyze (1ch -> 4 subbands) then synthesize (4 subbands -> 1ch full-rate). CALL-ONLY into
         * the frozen fira_tree.c; s_m2_fa[c] carries this channel's cross-frame filter state. */
        fira_tfb_analyze(&s_m2_fa[c], s_m2_xw, (uint16_t)M1_FRAME,
                         s_m2_sb0, s_m2_sb1, s_m2_sb2, s_m2_sb3);
        /* broadside v1: NO frac-delay on the subbands (focusing = v2). Synthesize straight back. */
        fira_tfb_synthesize(&s_m2_fa[c], s_m2_sb0, s_m2_sb1, s_m2_sb2, s_m2_sb3,
                            (uint16_t)M1_FRAME, s_m2_chout);

        /* interleave channel c into the 8-slot TX layout (tx[f*8 + c]); OPENING-5: write Q31 with no
         * shift -- the DAC slot takes the high 24 bits. + FG scan of the FIRA output. */
        for (i = 0u; i < M1_FRAME; i++) {
            int32_t o = s_m2_chout[i];
            uint32_t a = (o < 0) ? (uint32_t)(-(int64_t)o) : (uint32_t)o;
            tx[i * M1_TX_SLOTS + c] = o;
            if (o != 0) nz++;
            if (a > peak) peak = a;
        }
    }
    *pnz = nz; *ppeak = peak;
}
#endif /* M2_FIRA_INLOOP */

/* ---- RX-buffer-processed callback: io-callback CCNT probe + FG audio scan + the datapath.
 *   io-callback probe: the CCNT bracket measures the io item-1 "codec/IO DMA" CORE cost (+ the M2 beam
 *   compute when M2_FIRA_INLOOP=1). RAW only (C9); cb_cyc caliber = APP LOAD (R42: the bracket spans the
 *   whole callback body, which under M2 INCLUDES the FIRA beam -- so g_m1_cb_cyc_* is core+beam+io, NOT
 *   io-callback alone; off-board separates them. io-callback-only allowance stays [L3 reserve 30].).
 *   DATAPATH:
 *     M2_FIRA_INLOOP=1 -> 1 mono RX frame -> 8ch FIRA broadside beam -> 8-slot interleaved TX (OPENING-1).
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
        /* OPENING-1 whole-frame rebuild: 1 mono RX frame -> 8ch FIRA broadside -> 8-slot interleaved TX. */
        m2_fira_beam_frame(rx, tx, &nz, &peak);
        g_m2_out_nonzero += nz;
        if (peak > g_m2_out_max_abs) g_m2_out_max_abs = peak;
        /* M1's nonzero/peak also track here (so the stream-live FG keeps working in the M2 build too);
         * for M2, nz/peak are the BEAM-output stats (FIRA produced non-zero audio). */
        g_m1_nonzero_samples += nz;
        if (peak > g_m1_max_abs_sample) g_m1_max_abs_sample = peak;
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
    /* M2 beam-live FG (additional, anti-false-green for the FIRA path): green ONLY if blocks grew AND the
     * FIRA beam produced non-zero output. A stubbed/dead FIRA (memset 0 / not-linked) -> g_m2_out_nonzero
     * stays 0 -> g_m2_fg_beam_live never latches (placeholder-fails, DSP/FIRA special gate). */
    if (g_m1_rx_block_count > 0u && g_m2_out_nonzero > 0u) g_m2_fg_beam_live = 1;
#endif
}

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

    rc = fira_tree_setup();          /* Open -> RegisterCallback -> CreateTask -> FixedPointEnable(SIGNED) */
    g_m2_setup_rc = rc;
    if (rc != 0) return 1;           /* no FIRA on this host / setup failed -> honest fail (FG2, no fake) */

    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);                  /* core (golden) Q15 halfband coeffs */
    for (c = 0; c < DOLPH_W8_NCH; c++)
        fira_channel_init(&s_m2_fa[c], (uint16_t)M1_FRAME);      /* 8 per-channel states, zero-init */
    return 0;
}
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
    if (m2_fira_setup() != 0) return 1;        /* g_m2_setup_rc carries the rc; stream NOT armed on fail */
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
    return 1;                  /* non-zero: cannot run loopback off-board (honest fail, no fake) */
}

int m1_loopback_stop(void) { return 0; }

#endif /* M1_TARGET_BOARD && TARGET_SHARC */
