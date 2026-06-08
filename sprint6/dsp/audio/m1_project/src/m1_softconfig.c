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

static int m1_u6_write(ADI_TWI_HANDLE h, uint8_t reg, uint8_t val)
{
    s_m1_u6_buf[0] = reg;
    s_m1_u6_buf[1] = val;
    return (adi_twi_Write(h, s_m1_u6_buf, 2u, false) == ADI_TWI_SUCCESS) ? 0 : 1;
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

    if (adi_twi_Open(M1_U6_TWI_DEV, ADI_TWI_MASTER, s_m1_u6_mem, ADI_TWI_MEMORY_SIZE, &h)
        != ADI_TWI_SUCCESS) return 1;
    if (adi_twi_SetHardwareAddress(h, M1_U6_TWI_ADDR) != ADI_TWI_SUCCESS) { (void)adi_twi_Close(h); return 1; }
    (void)adi_twi_SetPrescale(h, M1_U6_TWI_PRESCALE);
    (void)adi_twi_SetBitRate(h, M1_U6_TWI_BITRATE);
    (void)adi_twi_SetDutyCycle(h, M1_U6_TWI_DUTY);

    /* (1) direction: make the ~EN / RESET pins driven outputs */
    rc |= m1_u6_write(h, M1_U6_IODIRA, M1_U6_IODIRA_VAL);   /* 0x18 */
    rc |= m1_u6_write(h, M1_U6_IODIRB, M1_U6_IODIRB_VAL);   /* 0x00 */
    rc |= m1_u6_write(h, M1_U6_GPIOB,  M1_U6_PORTB_VAL);    /* 0xFD: audio jack sel etc */

    /* (2) assert codec reset (b5=1), codecs enabled (active-low ~EN=0) -- clean reset pulse */
    rc |= m1_u6_write(h, M1_U6_GPIOA, M1_U6_PORTA_RESET);   /* 0x25 */
    for (d = 0xffff; d > 0; d--) { /* hold reset */ }

    /* (3) deassert reset (b5=0), keep both codecs enabled -- run state */
    rc |= m1_u6_write(h, M1_U6_GPIOA, M1_U6_PORTA_RUN);     /* 0x05 */
    for (d = 0xffff; d > 0; d--) { /* let codecs come out of reset */ }

    (void)adi_twi_Close(h);
    return rc;
}

#else  /* desktop: no carrier, honest no-op (never fakes an enable) */
int m1_softconfig_enable_codecs(void) { return 1; }
#endif
