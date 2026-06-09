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
/* [R50 build-configurable address fix mechanism, CTO-gated] U6 7-bit address. DEFAULT = 0x22 (R39, byte-
 * identical behavior to before). IF the R50 address self-probe (m1_u6_addr_sweep) shows the U6 ACKs at a
 * DIFFERENT address (R1a address-error), the tester/PM rebuilds with  -DM1_U6_TWI_ADDR_OVERRIDE=0x2X  to
 * point the enable chain at the swept-found address -- NO source edit. CTO-gated: applying an override is
 * an enable-chain address change (CTO call); the MECHANISM is pre-built here, the override is NOT set. */
#ifdef M1_U6_TWI_ADDR_OVERRIDE
#define M1_U6_TWI_ADDR    M1_U6_TWI_ADDR_OVERRIDE
#else
#define M1_U6_TWI_ADDR    0x22u    /* U6 HW addr [SoftConfig_*.c:108] (default; -D override available) */
#endif
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

/* [R50 address self-probe -- HARMLESS, probe-only] sweep 7-bit addresses 0x20..0x27 (MCP23017 base+strap)
 * with a NON-MUTATING register READ (read IODIRA 0x00); record per-address ACK. 1=ACK (device answered),
 * 0=NACK, -99=not-run. Index i = address (0x20 + i). Exactly-one-ACK => that is the real U6 7-bit address.
 * SAFETY: a register READ writes NO GPIOA / NO ~EN bit -- it cannot change codec-enable state. */
volatile int g_m1_u6_addr_sweep[8] = { -99, -99, -99, -99, -99, -99, -99, -99 };
#define M1_U6_SWEEP_BASE  0x20u    /* MCP23017-class 7-bit base; A2:A0 strap -> 0x20..0x27 */
#define M1_U6_SWEEP_N     8u

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

/* [R50 HARMLESS probe] does an address answer? Set the candidate 7-bit address, then do a NON-MUTATING
 * register READ of IODIRA (0x00): write the 1-byte register pointer (bRestart=true = repeated-start, the
 * proven ALT Read_TWI_8bit_Reg pattern, ALT.c:485-506) then read 1 byte. Returns 1 if BOTH phases ACK
 * (device answered at that address), else 0. SAFETY: a READ writes NO device register -- in particular it
 * touches NO GPIOA / NO ~EN bit, so it cannot change codec-enable state. Uses its OWN open handle. */
static int m1_u6_addr_responds(uint32_t addr7)
{
    ADI_TWI_HANDLE hp = NULL;
    uint8_t regptr = M1_U6_IODIRA;   /* 0x00 = a read-only-from-our-side direction register; harmless to read */
    uint8_t rxbyte = 0u;
    int ok = 0;

    if (adi_twi_Open(M1_U6_TWI_DEV, ADI_TWI_MASTER, s_m1_u6_mem, ADI_TWI_MEMORY_SIZE, &hp) != ADI_TWI_SUCCESS)
        return 0;
    if (adi_twi_SetHardwareAddress(hp, (uint16_t)addr7) == ADI_TWI_SUCCESS) {
        (void)adi_twi_SetPrescale(hp, M1_U6_TWI_PRESCALE);
        (void)adi_twi_SetBitRate(hp, M1_U6_TWI_BITRATE);
        (void)adi_twi_SetDutyCycle(hp, M1_U6_TWI_DUTY);
        /* write register pointer (repeated-start) then read 1 byte; ACK on both phases == device answered */
        if (adi_twi_Write(hp, &regptr, 1u, true) == ADI_TWI_SUCCESS &&
            adi_twi_Read(hp, &rxbyte, 1u, false) == ADI_TWI_SUCCESS) {
            ok = 1;
        }
    }
    (void)adi_twi_Close(hp);
    return ok;
}

/* [R50 PROBE-ONLY] sweep 0x20..0x27, fill g_m1_u6_addr_sweep. Changes NO codec-enable state (read-only
 * probe per address). Run once at diagnostic time (e.g. before m1_softconfig_enable_codecs). */
void m1_softconfig_addr_sweep(void)
{
    uint32_t i;
    for (i = 0u; i < M1_U6_SWEEP_N; i++)
        g_m1_u6_addr_sweep[i] = m1_u6_addr_responds(M1_U6_SWEEP_BASE + i);
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

    /* [R50 PROBE-ONLY] run the harmless address self-probe FIRST (read-only per address; opens+closes its
     * own handle; touches NO ~EN bit). Fills g_m1_u6_addr_sweep so a SINGLE diagnostic run yields both the
     * NACK code (codec_write_rc/hwerr/softcfg_rc) AND which address the U6 actually answers. The enable
     * sequence below is UNCHANGED -- it still uses M1_U6_TWI_ADDR (default 0x22 unless -D override). */
    m1_softconfig_addr_sweep();

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
int  m1_softconfig_enable_codecs(void) { return 1; }
void m1_softconfig_addr_sweep(void) { }   /* desktop no-op: no TWI bus */
#endif
