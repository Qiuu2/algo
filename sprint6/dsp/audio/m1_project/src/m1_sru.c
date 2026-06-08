/*
 * m1_sru.c -- WO-S6-AUDIO-M1-PROJ: SRU audio routing glue (R39-confirmed routing table).
 *   Routes the shared TDM bus: DAC (master) -> BCLK/FS -> SPORT4A/4B + ADC ; data SPORT4A->DAC, ADC->SPORT4B.
 *   SRU mis-route = signal never reaches the codec = SILENT no-sound, NO compile error. So every route
 *   below is the R39-verified one with its DAI pin + direction + group.
 *
 * ASCII-only. NEW board-only TU (M1 independent project; does NOT touch FIRA bench / compute line).
 *   board-guarded; desktop path is a no-op honest stub.
 *
 * SRU MODEL [HRM ch.22]: SRU2(<src>_O, <dst>_I) routes a DAI1 source-output to a dest-input. Group A=clock,
 *   B=serial-data, C=frame-sync, D=pin-assign, F=pin-out-enable. DAI1_PBENxx_I sets pin drive (HIGH=output,
 *   LOW=input). *pREG_PADS0_DAI1_IE enables the DAI1 input buffers.
 * CLOCK DIRECTION (the silent-no-sound risk): DAC is bus MASTER (DAC_CTRL1 SAI_MS=1) -> sources BCLK on
 *   DAI1_PB05, FS on DAI1_PB04; SPORT4A/4B + ADC are all SLAVES receiving them. Getting this backwards =
 *   silent. Verified by R39 + the M1 codec config (DAC master / ADC+SPORT slave).
 * D5: the data-direction macros are verified (sru21569.h): SPT4_BD0_I = GROUP_B2 serial-data IN (RX into
 *   SPORT4B), SPT4_AD0_O = serial-data OUT (TX from SPORT4A). 4A=TX-out / 4B=RX-in -- swapping = silent.
 */
#include <stdint.h>

#if defined(M1_TARGET_BOARD) && defined(TARGET_SHARC)

#include <sys/platform.h>   /* pREG_PADS0_DAI1_IE */
#include <cdef21569.h>      /* register defs */
#include <sru21569.h>       /* [L1] SRU2() + DAI1 and SPT4 routing macros (ALT.c:23; all 45 ALT tokens resolve) */

/*
 * m1_sru_init -- apply the R39 audio routing. Call AFTER adi_initComponents, BEFORE codec/SPORT enable.
 */
void m1_sru_init(void)
{
    /* enable DAI0/DAI1 input buffers (pins 1..20; bit0 reserved) [ALT.c:417-418] */
    *pREG_PADS0_DAI0_IE = (unsigned int)0x1ffffe;
    *pREG_PADS0_DAI1_IE = (unsigned int)0x1ffffe;

    /* ---- CLOCK fan-out (DAC master -> SPORT4A/4B + ADC) ---- */
    SRU2(LOW, DAI1_PBEN05_I);            /* PB05 = INPUT: DAC drives BCLK in [R39 C/F; ALT.c:420] */
    SRU2(DAI1_PB05_O, SPT4_ACLK_I);      /* BCLK -> SPORT4A clk (Group A) [ALT.c:422] */
    SRU2(DAI1_PB05_O, SPT4_BCLK_I);      /* BCLK -> SPORT4B clk (Group A) [ALT.c:423] */

    SRU2(LOW, DAI1_PBEN04_I);            /* PB04 = INPUT: DAC drives FS in [ALT.c:427] */
    SRU2(DAI1_PB04_O, SPT4_AFS_I);       /* FS -> SPORT4A FS (Group C) [ALT.c:425] */
    SRU2(DAI1_PB04_O, SPT4_BFS_I);       /* FS -> SPORT4B FS (Group C) [ALT.c:426] */

    /* re-drive BCLK/FS out to the ADC (ADC is slaved to the SAME master clocks) */
    SRU2(DAI1_PB05_O, DAI1_PB12_I);      /* BCLK -> PB12 (-> ADC BCLK pin) [ALT.c:432] */
    SRU2(HIGH, DAI1_PBEN12_I);           /* PB12 = OUTPUT: chip re-drives BCLK to ADC [ALT.c:433] */
    SRU2(DAI1_PB04_O, DAI1_PB20_I);      /* FS -> PB20 (-> ADC FS pin) [ALT.c:435] */
    SRU2(HIGH, DAI1_PBEN20_I);           /* PB20 = OUTPUT: chip re-drives FS to ADC [ALT.c:436] */

    /* ---- DATA paths ---- */
    SRU2(SPT4_AD0_O, DAI1_PB02_I);       /* TX: SPORT4A SDATA-out -> PB02 (-> DAC SDATA-in) (Group B) [ALT.c:429] */
    SRU2(HIGH, DAI1_PBEN02_I);           /* PB02 = OUTPUT: chip drives SDATA out to DAC [ALT.c:430] */

    SRU2(DAI1_PB06_O, SPT4_BD0_I);       /* RX: ADC SDATA (PB06) -> SPORT4B SDATA-in (Group B) [ALT.c:438] */
    SRU2(LOW, DAI1_PBEN06_I);            /* PB06 = INPUT: ADC drives SDATA in [ALT.c:439] */
}

#else  /* desktop: no DAI/SRU hardware -- honest no-op */
void m1_sru_init(void) { }
#endif
