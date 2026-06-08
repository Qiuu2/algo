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

/* ping-pong DMA buffers (opening 4: default L1 Block 0, uncached -> coherency-free; M1 no-pin).
 * RX = 1 captured slot/frame (512B over 2 halves); TX = 8 slots/frame (4096B over 2 halves). Separate
 * sizes -- DRAFT-DIFF: pre-arch draft used one 2048-word block for both; corrected to per-direction. */
static int32_t s_m1_rx_buf[2][M1_RX_HALF_WORDS];   /* ADC RX ping-pong (1 slot x 64 = 64 words/half) */
static int32_t s_m1_tx_buf[2][M1_TX_HALF_WORDS];   /* DAC TX ping-pong (8 slot x 64 = 512 words/half) */

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
    (void)adi_twi_Write(s_m1_htwi, s_m1_twi_txbuf, 2u, false);
}

/* ---- RX-buffer-processed callback: fan-out 1->8 passthrough + io-callback CCNT probe + FG audio scan.
 *   io-callback probe: the CCNT bracket measures the io item-1 "codec/IO DMA" CORE cost the H2 MDMA proxy
 *   could NOT measure -> turns the [L3] io-callback ~30 allowance into an [L1] number. RAW only (C9).
 *   FAN-OUT (opening 2): RX has 1 slot/frame (mono). Copy that ONE sample to ALL 8 TX slots of the same
 *   frame. DRAFT-DIFF: pre-arch draft did a 4->8 (i+=4,j+=8) copy; corrected to 1->8 mono. */
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
        uint32_t f, s8;
        uint32_t nz = 0u, peak = 0u;

        /* FAN-OUT 1->8: for each of the 64 frames, take the single packed RX sample and write it into all
         * 8 contiguous TX slots of that frame. RX is packed (1 word/frame); TX is unpacked 8 words/frame. */
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

        g_m1_rx_block_count++;
        g_m1_tx_block_count++;
        s_m1_pp_index++;
    }
    t1 = bench_cyc_target();   /* CCNT bracket CLOSE */

    g_m1_cb_cyc_last = t1 - t0;                       /* raw callback body cost (io-callback [L1-to-be]) */
    if (g_m1_cb_cyc_last > g_m1_cb_cyc_max) g_m1_cb_cyc_max = g_m1_cb_cyc_last;
    if (g_m1_cb_cyc_last < g_m1_cb_cyc_min) g_m1_cb_cyc_min = g_m1_cb_cyc_last;

    /* FG (stream-live, anti-false-green): live iff blocks grew AND non-zero audio seen. Dead codec/DMA ->
     * rx_block_count stays 0; silent/dead input -> nonzero_samples stays 0; either keeps FG from latching. */
    if (g_m1_rx_block_count > 0u && g_m1_nonzero_samples > 0u) g_m1_fg_stream_live = 1;
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

    if (m1_sport_init() != 0) return 1;        /* SPORT4 TDM ping-pong + callback armed */

    g_m1_valid = 1;
    return 0;
}

int m1_loopback_stop(void)
{
    if (s_m1_hsport_rx != NULL) { (void)adi_sport_StopDMATransfer(s_m1_hsport_rx); (void)adi_sport_Close(s_m1_hsport_rx); s_m1_hsport_rx = NULL; }
    if (s_m1_hsport_tx != NULL) { (void)adi_sport_StopDMATransfer(s_m1_hsport_tx); (void)adi_sport_Close(s_m1_hsport_tx); s_m1_hsport_tx = NULL; }
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
    return 1;                  /* non-zero: cannot run loopback off-board (honest fail, no fake) */
}

int m1_loopback_stop(void) { return 0; }

#endif /* M1_TARGET_BOARD && TARGET_SHARC */
