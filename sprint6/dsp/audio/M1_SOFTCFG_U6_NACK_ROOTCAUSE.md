# M1 softcfg U6 all-NACK (code 11=PERIPHERAL_ERROR) root-cause + block B (HALT)

> **R51/R52 CORRECTION (2026-06-10, supersedes the hwerr wording below)**: `g_m1_softcfg_hwerr` is an **enum
> ORDINAL, not a bit-mask** (ADI_TWI_EVENT sequential enum, installed adi_twi_2156x.h:99-104): `0`=none,
> `1/2`=BUFWRERR/BUFRDERR, `3`=DNAK, `4`=ANAK, `5`=LOSTARB. **Decode by EQUALITY (==4 ANAK etc.), never by
> bit-AND** -- bit-decoding flips bus-level vs address-error (e.g. 5=LOSTARB would bit-AND as "ANAK set").
> The readout-map rows below have been REWRITTEN to ordinal equality (==3/==4/==5) in this same
> correction; conditions and next-steps unchanged. Authoritative tables: STAGE4_TESTER_RUNBOOK "PM 判读" (PM-judge) section /
> M1_SOFTCFG_U6_ADDR_SWEEP sec 3.
>
> dsp-algorithm teammate, 2026-06-08. Board re-run with block A: g_m1_softcfg_rc[0..4] ALL = 11 =
> ADI_TWI_PERIPHERAL_ERROR = every U6 write bus-NACKs (systematic, not sporadic); open/addr = 0. Task:
> root-cause from SOURCE + datasheet/installed-header, block B (CTO-gated, no blind fix). ASCII. No commit.
> HALT. Does NOT predict CTO ruling. Does NOT claim swap-safe (F-SRU-1 not fixed + re-verified rc=0).
>
> SOURCES [L1]: installed CCES 2.12.1 adi_twi_2156x.h (the 21569 family header, /opt/analog/cces/2.12.1/...);
> m1_softconfig.c (U6) + m1_loopback_tdm.c (codec) + m1_main.c; ALT SoftConfig / Audio_Loopback_TDM.c.

================================================================================
## 0. R48 ALT-comparison CORRECTION (CTO-flagged, absorbed)
================================================================================
R48 said "ALT uses the same adi_twi_Write and it works." CORRECTED: ALT's U6 write lives in
Switch_Configurator(), which is COMMENTED OUT (ALT.c:701) -> **ALT NEVER actually writes U6**. ALT's
WORKING TWI writes are to the CODECS (0x04/0x11), not U6. So **M1 is the FIRST code to really write U6 (0x22)
-- there is NO ALT precedent of a U6 write succeeding.** The valid comparison is: M1/ALT codec TWI (works) vs
M1 U6 TWI (NACKs). This changes the diagnosis -- 0x22 has never been proven to ACK on this carrier.

================================================================================
## 1. CLOCK-CONFIG eliminated: codec(works) and U6(NACK) use the IDENTICAL config
================================================================================
PM's lead "U6 sets clock, codec doesn't" is INCORRECT for M1. Field-by-field:
| field | M1 codec (m1_loopback_tdm.c) WORKS | M1 U6 (m1_softconfig.c) NACK | ALT codec (ALT.h) WORKS |
|---|---|---|---|
| TWI dev | 2 (:137) | 2 (:27) | 2 (TWIDEVNUM) |
| SetPrescale | 12 (:138,:442) | 12 (:29,:84) | 12 (PRESCALEVALUE) |
| SetBitRate | 100 (:139,:443) | 100 (:30,:85) | 100 (BITRATE, kHz) |
| SetDutyCycle | 50 (:140,:444) | 50 (:31,:86) | 50 (DUTYCYCLE, %) |
| address | 0x04 / 0x11 | **0x22** | 0x04/0x11/0x38 |
- M1's codec path DOES set prescale/bitrate/duty (m1_loopback_tdm.c:442-444), same values as U6. Both M1
  paths use the SAME TWI2 + SAME clock (12/100/50). The clock config is therefore IDENTICAL between the two.
- **[F49-MAJOR-1 CORRECTION] codec-write-ACK is NOT proven.** The earlier claim "the codec writes ACK
  (audio runs)" does NOT hold: m1_twi_w8 (m1_loopback_tdm.c) IGNORED the write rc with (void), and m1_dac_init
  unconditionally returns 0 -- so a codec write that NAK'd would be INVISIBLE, and "audio runs" is equally
  consistent with (codec writes ACK) OR (codec writes ALSO NAK + the carrier default already enabled the
  codecs) -- the same F-SRU-1 trap. So the clock is identical, but whether THAT clock actually transacts on
  this bus is NOT yet proven from this data. **Clock config is the SAME; clock VALIDITY is unproven until
  the codec write rc is captured (sec 4 discriminant).**
- The U6-vs-codec differences are the ADDRESS (0x22 vs 0x04/0x11) and the target DEVICE. Whether the NACK is
  U6-address-SPECIFIC (R1) or BUS-LEVEL (affects codec writes too) CANNOT be split until the codec write rc
  is read.

================================================================================
## 2. CONTROLLED COMPARISON: bus NOT YET proven; R1-vs-bus-level pending codec write rc
================================================================================
Main order (m1_main.c:45-51): SRU -> m1_softconfig (U6, opens TWI2 -> writes -> Close) -> m1_loopback_init
(codec, RE-opens TWI2 -> writes 0x04/0x11 -> Close). The structure IS a clean controlled comparison (same
TWI2, sequential, only the address/device differ).
- **[F49-MAJOR-1 CORRECTION] but the codec arm's outcome is NOT captured.** "codec ACKs, audio works" is
  UNVERIFIED: m1_twi_w8 (void)-ignored the rc; m1_dac_init returns 0 unconditionally. So the codec write
  could ALSO be NAK'ing with the audio coming from the carrier default. => the controller/SCL/SDA/pull-ups/
  actual-prescale are **NOT YET PROVEN healthy**; "bus proven good" is RETRACTED.
- Therefore **R1 (U6-address-specific) and BUS-LEVEL cannot be split from the CURRENT data.** They diverge
  ONLY on the codec write rc: codec write ACK(0) -> bus good, U6 NACK is address/device specific (R1);
  codec write also NACK(11)/LOSTARB -> BUS-LEVEL (pull-up/SCL/SDA/actual-prescale-vs-SCLK). The sec-4
  discriminant (g_m1_codec_write_rc) settles it in one re-run.

================================================================================
## 3. ROOT-CAUSE adjudication (PERIPHERAL_ERROR=11 = "error processing the buffer" = a NACK abort)
================================================================================
The blocking write aborts with PERIPHERAL_ERROR (enum :76) = the transfer NAK'd. The installed header
distinguishes the NAK PHASE (enum :102-103):
- **ADI_TWI_EVENT_ANAK** = NAK during the ADDRESS phase = the device at 0x22 did NOT answer its address
  (wrong address, or U6 absent/unpowered/held-in-reset by the carrier CPLD).
- **ADI_TWI_EVENT_DNAK** = NAK during the DATA phase = U6 answers 0x22 but NAKs the data byte (sub-address
  / BANK-mode / register issue).
adi_twi_GetHWErrorStatus(h, &hwErr) (:180) returns this -- THE single board test that splits the two.

Candidates -- [F49-MAJOR-1] R1 DOWNGRADED from "TOP" to "R1 vs bus-level pending the codec-write-rc
discriminant" (the bus is NOT yet proven good, sec 2). The two top-level branches are NOW co-equal until
the discriminant reads:
- **(R0) BUS-LEVEL** (pull-up / SCL/SDA / actual prescale-vs-SCLK / arbitration): would NAK/LOSTARB the
  codec writes TOO. NOT excluded -- "codec ACKs" is unverified (sec 2). If g_m1_codec_write_rc is also
  non-zero (11/LOSTARB), this is the cause, NOT U6-specific. [discriminant: codec write rc + hwerr LOSTARB.]
- **(R1) U6 ADDRESS / DEVICE-REACHABILITY: 0x22 address-phase NAK (ANAK)** -- ONLY if the codec write ACKs
  (bus good). Indicated by: 0x22 never proven on this carrier (ALT's U6 write was dead-code, sec 0) +
  all-5 systematic. Conditional on the discriminant showing bus-good. Sub-causes:
   - **(R1a) 7-bit vs 8-bit address mismatch**: adi_twi_SetHardwareAddress takes a uint16_t; the ADI driver
     expects the 7-bit address (it shifts in the R/W bit). The SoftConfig passes 0x22 directly. IF the
     carrier U6 actually sits at a different 7-bit address, or IF 0x22 was meant as an 8-bit value (0x22>>1
     = 0x11 -- which COLLIDES with the ADC! -- or 0x22<<1=0x44), the address is wrong -> ANAK. [board-confirm:
     the SoftConfig 0x22 is the carrier's documented 7-bit U6 address per the source comment, but its
     correctness was never runtime-proven.]
   - **(R1b) U6 strap**: MCP23017-class base 0x20 + A2:A0 strap; 0x22 = A1 strapped high. The actual strap
     is a carrier-schematic fact (no local MCP datasheet) -> [board-confirm].
   - **(R1c) U6 not present / not powered / held in reset** by the carrier (different SOMCRR variant, or a
     CPLD gate not released) -> address-phase NAK. [board-confirm: scope/schematic.]
- **(R2) DATA-phase NAK (DNAK)**: U6 answers 0x22 but NAKs the data -- e.g. a register-address/BANK-mode
  mismatch (MCP23017 BANK=1 remaps IODIRA/GPIOA from 0x00/0x12). LESS likely as the SOLE cause of ALL-5
  failing (a BANK issue would still ACK address; some writes might land), but possible -> GetHWErrorStatus
  rules it. [board-confirm.]
- **(R3) clock VALUES**: the values are IDENTICAL to the codec path (sec 1), so a wrong-VALUE clock is
  unlikely -- BUT whether the clock physically transacts (actual SCL freq, pull-up strength) is part of R0
  bus-level and is NOT proven until the codec write rc reads. Not fully eliminated; folded into R0.

VERDICT (honest, cannot resolve locally): **R0 (bus-level) and R1 (U6-address-specific) are CO-EQUAL on the
current data** because codec-write-ACK was never captured (F49-MAJOR-1). The discriminant is ONE value:
g_m1_codec_write_rc (sec 4) -- codec write ACK(0) => bus good => R1; codec write NACK(11)/LOSTARB => R0
bus-level. ADDRESS-vs-DATA NAK (within R1) + the exact wrong-vs-absent further need GetHWErrorStatus
(ANAK/DNAK) + a scope/schematic check. I do NOT pick a fix blind -- the obs re-run names the branch.

================================================================================
## 4. obs-only change block (UPGRADED R49: set_rc + hwerr + codec_write_rc discriminant) -- APPLIED
================================================================================
OBSERVATION ONLY (no write/enable/return-logic change) -> no parallel-safety gate. APPLIED to all copies
(byte-identical): m1_softconfig.c (2 copies) + m1_loopback_tdm.c (canonical + cces). Guard-checked clean,
BOTH builds: M1 transparent (M2_FIRA_INLOOP=0) AND M2 FIRA (M2_FIRA_INLOOP=1), RC=0.

(a) m1_softconfig.c -- globals + capture 3 Set rc + GetHWErrorStatus after first write:
```c
volatile int      g_m1_softcfg_set_rc[3] = { -99, -99, -99 };  /* 0=Prescale 1=BitRate 2=DutyCycle raw rc */
volatile uint32_t g_m1_softcfg_hwerr     = 0xFFFFFFFFu;        /* GetHWErrorStatus: ANAK/DNAK/LOSTARB/BUFxx */
...
    g_m1_softcfg_set_rc[0] = (int)adi_twi_SetPrescale(h, M1_U6_TWI_PRESCALE);   /* was (void) */
    g_m1_softcfg_set_rc[1] = (int)adi_twi_SetBitRate(h, M1_U6_TWI_BITRATE);     /* was (void) */
    g_m1_softcfg_set_rc[2] = (int)adi_twi_SetDutyCycle(h, M1_U6_TWI_DUTY);      /* was (void) */
...
    (void)adi_twi_GetHWErrorStatus(h, (uint32_t *)&g_m1_softcfg_hwerr);  /* after the first (IODIRA) write */
```
(b) m1_loopback_tdm.c -- THE F49-MAJOR-1 DISCRIMINANT (only m1_twi_w8, NOT the M2 callback):
```c
volatile int g_m1_codec_write_rc = -99;   /* raw rc of LAST codec TWI write (m1_twi_w8 was (void)) */
...
static void m1_twi_w8(uint8_t reg, uint8_t val) {
    s_m1_twi_txbuf[0] = reg; s_m1_twi_txbuf[1] = val;
    g_m1_codec_write_rc = (int)adi_twi_Write(s_m1_htwi, s_m1_twi_txbuf, 2u, false);  /* was (void) */
}
```
(GetHWErrorStatus exists in the installed adi_twi_2156x.h :180; ANAK/DNAK/LOSTARB are the ADI_TWI_EVENT
enum :100-105.)

### board re-run readout map (resolves R0 bus-level vs R1 U6-specific -- ONE re-run)
| reading | meaning | next |
|---|---|---|
| **g_m1_codec_write_rc = 0** (codec write ACK) | **BUS GOOD** -> U6 NACK is address/device specific = R1 | -> hwerr ANAK -> block B (B-b/B-c); DNAK -> (B-d) |
| **g_m1_codec_write_rc = 11 / non-zero** (codec write NACK) | **BUS-LEVEL fault (R0)** -- NOT U6-specific; audio was carrier default | -> block B (B-e) bus-level |
| g_m1_softcfg_hwerr == 4 (ANAK, addr-phase) | 0x22 wrong / U6 unreachable (R1, IF bus good) | (B-b) addr / (B-c) readiness |
| g_m1_softcfg_hwerr == 3 (DNAK, data-phase) | U6 answers 0x22, NAKs data (R1-DNAK, IF bus good) | (B-d) BANK / register-addr |
| **g_m1_softcfg_hwerr == 5 (LOSTARB)** (arbitration loss) | **BUS-LEVEL** (another master / SDA stuck / pull-up) | (B-e) bus-level |
| g_m1_softcfg_hwerr == 1 / == 2 (BUFWRERR/BUFRDERR) | driver buffer error | investigate driver memory/handle |
| set_rc all 0 | the 3 clock Sets took (config applied) | -> failure is transact-level, not Set-config |
| set_rc any !=0 | a Set itself rejected the value | rules out clock-config-applied; check value/range |

================================================================================
## 5. block B FIX options (CTO-GATED -- logic change to the enable chain; NOT applied, NOT apply-ready
================================================================================
   until the obs re-run names the branch (codec_write_rc R0-vs-R1, then ANAK/DNAK/LOSTARB). Changing the
   codec-enable chain needs CTO's call per parallel safety -- line B M2 is committed 12a5920, no file
   collision, but the enable logic is shared M1 IP.)
- **(B-e) BUS-LEVEL (if codec_write_rc also NACK or hwerr LOSTARB) [NEW, F49]**: the fault is NOT
  U6-specific. Check pull-up resistors on the TWI2 SCL/SDA (value/presence), bus loading, another master,
  and the ACTUAL SCL frequency vs SCLK0 (prescale=12 -> verify the resulting SCL is in-spec for ALL devices
  on the bus, not just nominal 100 kHz). This is the highest branch if the discriminant shows codec writes
  also fail -- it means the WHOLE TWI2 bus has an issue and the audio was the carrier default. [board-confirm:
  scope SCL/SDA + measure SCL freq.]
- **(B-a) clock VALUES: likely NO CHANGE** (identical to codec path) -- but the ACTUAL SCL (B-e) is the
  bus-level question, not the value.
- **(B-b) ADDRESS fix (if ANAK + bus good)**: verify the U6 7-bit address against the SOMCRR schematic. If 0x22 is
  wrong, set the correct 7-bit address. If 0x22 was an 8-bit value, use 0x22>>1 -- BUT 0x11 collides with
  the ADC, so that interpretation is almost certainly wrong, reinforcing that 0x22 should be the 7-bit
  value and the issue is the device, not the shift. [board-confirm the schematic U6 address.]
- **(B-c) U6 readiness (if ANAK + addr confirmed right)**: the carrier may hold U6 in reset / unpowered at
  this point; add a readiness wait or a carrier-CPLD release step BEFORE the U6 writes (none exists today,
  m1_softconfig.c has no pre-write U6 wait). [board-confirm the carrier power/reset sequencing.]
- **(B-d) BANK / register-address (if DNAK)**: if U6 is MCP23017 in BANK=1, IODIRA/GPIOA addresses differ
  (0x00/0x12 are BANK=0); set BANK=0 first or use the BANK=1 addresses. [board-confirm the U6 part + BANK.]
- DO NOT apply any of these blind. The obs re-run picks the branch; then CTO gates the logic change.

================================================================================
## 6. MUST-CONFIRM-ON-BOARD list (cannot resolve locally)
================================================================================
- ANAK vs DNAK (GetHWErrorStatus) -- the obs re-run.
- The carrier U6 part + its 7-bit I2C address + A2:A0 strap (SOMCRR schematic; no local MCP datasheet).
- U6 power/reset sequencing at the time of the writes (is U6 ready? carrier CPLD gate?).
- (If DNAK) the U6 BANK mode (affects IODIRA/GPIOA register addresses).

================================================================================
## SUMMARY (HALT)
================================================================================
- All-5 = PERIPHERAL_ERROR (11) = systematic NAK abort of every U6 write. [L1 enum]
- CLOCK VALUES are IDENTICAL between U6 and the codec path (same TWI2 + 12/100/50) -- so a wrong clock VALUE
  is unlikely. (PM's "U6 sets clock, codec doesn't" is wrong -- M1 codec sets it too.) But whether that
  clock TRANSACTS on the bus is part of R0 bus-level, unproven until the codec write rc reads.
- [F49-MAJOR-1] "bus proven good / codec ACKs" is RETRACTED -- m1_twi_w8 (void)-ignored the codec write rc
  and m1_dac_init returns 0 unconditionally, so codec-write-ACK was never captured; audio-runs is equally
  consistent with codec-also-NACK + carrier default. So R0 (bus-level) and R1 (U6-specific) are CO-EQUAL.
- DISCRIMINANT (one re-run): g_m1_codec_write_rc -- ACK(0) => bus good => R1 (U6 address/device); NACK(11)/
  LOSTARB => R0 (bus-level). Then GetHWErrorStatus ANAK/DNAK/LOSTARB refines within the branch.
- block B fix = CTO-gated, branches: (B-e) bus-level / (B-b) address / (B-c) readiness / (B-d) BANK. NOT
  apply-ready until the discriminant names the branch. NO blind fix.
- obs block (set_rc + hwerr + codec_write_rc) = UPGRADED + APPLIED (obs-only, all copies byte-identical,
  guard-checked BOTH M1 + M2 builds RC=0). Only m1_twi_w8 touched in the loopback TU -- M2 callback/pin
  untouched.
- F-SRU-1 is NOT in effect and NOT yet fixable to a verified state -> NO swap-safe claim until the fix lands
  AND a board re-run shows g_m1_softcfg_rc all 0.
- HALT: awaiting CTO -> board re-run -> read g_m1_codec_write_rc (R0 vs R1) + hwerr (ANAK/DNAK/LOSTARB) +
  set_rc -> pick block B branch (CTO-gated). No commit (PM verifies + lands; obs-only, R49 content passed).
  No CTO ruling predicted.
