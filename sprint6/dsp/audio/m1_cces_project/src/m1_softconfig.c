/*
 * m1_softconfig.c -- WO-S6-AUDIO-M1-PROJ: explicit carrier codec-enable (F-SRU-1 hard constraint).
 *   CTO ruling (R39): M1 EXPLICITLY enables the codecs -- it does NOT gamble on the carrier default.
 *   ALT's Switch_Configurator() is COMMENTED OUT (ALT.c:701) -> ALT relies on the carrier; copying that
 *   = silent no-sound with NO compile/run error. M1 writes the U6 I/O-expander itself.
 *
 * ASCII-only. NEW board-only TU (M1 independent project; does NOT touch FIRA bench / compute line).
 *   board-guarded (#if M1_TARGET_BOARD && TARGET_SHARC); desktop path is a no-op honest stub.
 *
 * THE CARRIER GATE (SOMCRR/EZKIT): a U6 I/O-expander (MCP23017-class) on TWI dev 2, HW addr 0x22, gates
 *   the codecs. [SoftConfig_EV_SOMCRR_EZKIT_ADC_DAC.c:107-108; R39 routing survey sec 2]
 * D5 per-bit decode (NOT blind-copied -- today's 0x1B/0x0A/F-SRU-1 lessons): every value below is the
 *   R39-verified value with its bit-field decomposition in the comment. U6 Port A bit map
 *   [SoftConfig_ADC_DAC.c:80-92]:
 *     b7 ~ADAU1979_EN (ADC, active-low)   b6 ~ADAU1962_EN (DAC, active-low)   b5 ADAU_RESET (active-high)
 *     b4,b3 NotUsed   b2 ~MicroSD_SPI   b1 PUSHBUTTON_EN   b0 EEPROM_EN
 */
#include <stdint.h>

#if defined(M1_TARGET_BOARD) && defined(TARGET_SHARC)

#include <stddef.h>
#include <stdbool.h>
#include <drivers/twi/adi_twi_2156x.h>   /* [L1] adi_twi_* (ALT.c:18, SoftConfig_*.c) */

/* ---- carrier U6 I/O-expander constants (R39-verified) ---- */
#define M1_U6_TWI_DEV     2u       /* TWI dev 2 [SoftConfig_*.c SoftSwitch.TWIDevice] */
#define M1_U6_TWI_ADDR    0x22u    /* U6 HW addr [SoftConfig_*.c:108] */
#define M1_U6_TWI_PRESCALE 12u
#define M1_U6_TWI_BITRATE  100u
#define M1_U6_TWI_DUTY     50u

/* U6 register addresses (MCP23017-class) */
#define M1_U6_IODIRA      0x00u    /* port A direction (1=in,0=out) */
#define M1_U6_IODIRB      0x01u    /* port B direction */
#define M1_U6_GPIOA       0x12u    /* port A output latch */
#define M1_U6_GPIOB       0x13u    /* port B output latch */

/* R39-verified values (D5-decoded in comments at the write sites) */
#define M1_U6_IODIRA_VAL  0x18u    /* b4,b3 inputs; b7,b6,b5 outputs (drive ~EN / RESET lines) */
#define M1_U6_IODIRB_VAL  0x00u    /* port B all outputs */
#define M1_U6_PORTA_RESET 0x25u    /* b7 ~ADAU1979_EN=0(ADC en) b6 ~ADAU1962_EN=0(DAC en) b5 ADAU_RESET=1(ASSERT) */
#define M1_U6_PORTA_RUN   0x05u    /* b7=0(ADC en) b6=0(DAC en) b5 ADAU_RESET=0(DEASSERT) b2=1 b0=1 */
#define M1_U6_PORTB_VAL   0xFDu    /* b3 AUDIO_JACK_SEL=1 (+ eth/spdif/mlb gates; R39 sec 2) */

static uint8_t        s_m1_u6_mem[ADI_TWI_MEMORY_SIZE];
static uint8_t        s_m1_u6_buf[2];

/* [R44 per-write instrumentation -- CTO board re-run] independent rc per write (NOT OR-masked).
 * Index: 0=IODIRA 1=IODIRB 2=GPIOB 3=GPIOA-reset 4=GPIOA-run. -99=not-run. Read at idle (free-run),
 * by JTAG symbol name (file-scope here for parallel-line safety; debugger reads by symbol, not by TU).
 * OBSERVATION ONLY -- codec-enable logic + return value are unchanged (rc |= kept identical). */
volatile int g_m1_softcfg_rc[5]    = { -99, -99, -99, -99, -99 };
volatile int g_m1_softcfg_open_rc  = -99;   /* adi_twi_Open rc (0=ok) */
volatile int g_m1_softcfg_addr_rc  = -99;   /* SetHardwareAddress rc (0=ok) */
/* [R49 obs-only] capture the 3 clock-config Set rc (were (void)-ignored) + the HW error detail after the
 * first failed write. g_m1_softcfg_set_rc: 0=SetPrescale 1=SetBitRate 2=SetDutyCycle (raw ADI_TWI_RESULT).
 * g_m1_softcfg_hwerr = adi_twi_GetHWErrorStatus bits -> ANAK(addr-phase NAK = wrong addr/U6 absent) /
 * DNAK(data-phase NAK = U6 answers, NAKs data) / LOSTARB(arbitration loss = BUS-LEVEL) / BUFWR/RDERR.
 * OBSERVATION ONLY -- enable/write/return logic unchanged. */
volatile int      g_m1_softcfg_set_rc[3] = { -99, -99, -99 };
volatile uint32_t g_m1_softcfg_hwerr     = 0xFFFFFFFFu;

static int m1_u6_write(ADI_TWI_HANDLE h, uint8_t reg, uint8_t val)
{
    s_m1_u6_buf[0] = reg;
    s_m1_u6_buf[1] = val;
    /* [R48 block A obs-only] return RAW ADI_TWI_RESULT (0=SUCCESS, 1..14=which error) instead of
     * collapsing 1..14 to 1 -- names the failure code per write. rc|=/return rc aggregate semantics
     * unchanged (rc nonzero iff any write != SUCCESS). adi_twi_Write is BLOCKING, 4th arg = bRestart
     * (I2C repeated-start), NOT bWaitFlag (R48 [L1] installed header). */
    return (int)adi_twi_Write(h, s_m1_u6_buf, 2u, false);
}

/*
 * m1_softconfig_enable_codecs -- explicitly enable + reset-toggle the ADAU codecs via U6 (F-SRU-1).
 *   Sequence (R39): set direction -> assert reset (clean codec reset) -> deassert + dual-enable.
 *   @return 0 = ok, !=0 = honest fail (a dead carrier U6 -> codecs stay disabled -> caller can FG-0).
 */
int m1_softconfig_enable_codecs(void)
{
    ADI_TWI_HANDLE h = NULL;
    volatile int d;
    int rc = 0;

    g_m1_softcfg_open_rc = (adi_twi_Open(M1_U6_TWI_DEV, ADI_TWI_MASTER, s_m1_u6_mem, ADI_TWI_MEMORY_SIZE, &h)
        == ADI_TWI_SUCCESS) ? 0 : 1;
    if (g_m1_softcfg_open_rc != 0) return 1;
    g_m1_softcfg_addr_rc = (adi_twi_SetHardwareAddress(h, M1_U6_TWI_ADDR) == ADI_TWI_SUCCESS) ? 0 : 1;
    if (g_m1_softcfg_addr_rc != 0) { (void)adi_twi_Close(h); return 1; }
    g_m1_softcfg_set_rc[0] = (int)adi_twi_SetPrescale(h, M1_U6_TWI_PRESCALE);   /* [R49 obs] was (void) */
    g_m1_softcfg_set_rc[1] = (int)adi_twi_SetBitRate(h, M1_U6_TWI_BITRATE);     /* [R49 obs] was (void) */
    g_m1_softcfg_set_rc[2] = (int)adi_twi_SetDutyCycle(h, M1_U6_TWI_DUTY);      /* [R49 obs] was (void) */

    /* (1) direction: make the ~EN / RESET pins driven outputs (dir-then-latch order kept, R44 INFO) */
    g_m1_softcfg_rc[0] = m1_u6_write(h, M1_U6_IODIRA, M1_U6_IODIRA_VAL); rc |= g_m1_softcfg_rc[0]; /* 0x18 IODIRA */
    /* [R49 obs-only] read the HW error detail after the first write -> ANAK/DNAK/LOSTARB names the failure
     * mode (addr-phase vs data-phase vs bus-level arbitration). No behavior change. */
    (void)adi_twi_GetHWErrorStatus(h, (uint32_t *)&g_m1_softcfg_hwerr);
    g_m1_softcfg_rc[1] = m1_u6_write(h, M1_U6_IODIRB, M1_U6_IODIRB_VAL); rc |= g_m1_softcfg_rc[1]; /* 0x00 IODIRB */
    g_m1_softcfg_rc[2] = m1_u6_write(h, M1_U6_GPIOB,  M1_U6_PORTB_VAL);  rc |= g_m1_softcfg_rc[2]; /* 0xFD GPIOB  */

    /* (2) assert codec reset (b5=1), codecs enabled (active-low ~EN=0) -- clean reset pulse */
    g_m1_softcfg_rc[3] = m1_u6_write(h, M1_U6_GPIOA, M1_U6_PORTA_RESET); rc |= g_m1_softcfg_rc[3]; /* 0x25 GPIOA reset */
    for (d = 0xffff; d > 0; d--) { /* hold reset */ }

    /* (3) deassert reset (b5=0), keep both codecs enabled -- run state */
    g_m1_softcfg_rc[4] = m1_u6_write(h, M1_U6_GPIOA, M1_U6_PORTA_RUN);   rc |= g_m1_softcfg_rc[4]; /* 0x05 GPIOA run */
    for (d = 0xffff; d > 0; d--) { /* let codecs come out of reset */ }

    (void)adi_twi_Close(h);
    return rc;
}

#else  /* desktop: no carrier, honest no-op (never fakes an enable) */
int m1_softconfig_enable_codecs(void) { return 1; }
#endif
