# M1 softcfg U6 address self-probe (R50 batch-pack core) -- diagnostic + pre-built fix (HALT)

> dsp-algorithm teammate, 2026-06-08. Batch-pack goal (STAGE4_BATCH_PLAN.md): compress softcfg
> diagnose -> fix -> verify into ONE diagnostic run. The existing obs (codec_write_rc / hwerr / set_rc,
> 3a3bb50) already splits R1(U6-specific) vs R0(bus-level); this adds a U6 ADDRESS SELF-PROBE so the SAME
> run also finds the correct address if it is an address error (R1a). probe/obs-ONLY -- no codec-enable
> logic change. ASCII. No commit (critic R50). HALT. Does NOT predict board readings.

================================================================================
## 1. WHAT WAS ADDED (m1_softconfig.c only; both copies byte-identical)
================================================================================
### (A) Address self-probe -- HARMLESS, probe-only
- `g_m1_u6_addr_sweep[8]` (volatile int, -99 init): per-address ACK. index i = address 0x20 + i.
  1 = device answered at that 7-bit address, 0 = NACK, -99 = not run.
- `m1_u6_addr_responds(addr7)`: opens its OWN handle, SetHardwareAddress(addr7), then a NON-MUTATING
  register READ of IODIRA (0x00): write the 1-byte register POINTER (bRestart=true = repeated-start, the
  proven ALT Read_TWI_8bit_Reg pattern, ALT.c:485-506) then adi_twi_Read 1 byte. ACK on BOTH phases => 1.
  Closes its handle. **It WRITES only the register-pointer byte (value = 0x00 = IODIRA address); it writes
  NO device register, in particular NO GPIOA / NO ~EN bit.**
- `m1_softconfig_addr_sweep()`: loops 0x20..0x27, fills the array.
- It runs ONCE at the TOP of m1_softconfig_enable_codecs (read-only, before any enable write) -> a single
  diagnostic run yields BOTH the NACK code AND the sweep. (Placed there so m1_main.c is NOT touched --
  file-boundary constraint. The enable sequence below it is byte-unchanged.)

### (B) Build-configurable address fix mechanism (R1a) -- pre-built, default OFF
- M1_U6_TWI_ADDR is now `#ifdef M1_U6_TWI_ADDR_OVERRIDE -> that, #else 0x22`. DEFAULT = 0x22 (byte-identical
  behavior). If the sweep finds the U6 at a different address, the tester/PM rebuilds with
  `-DM1_U6_TWI_ADDR_OVERRIDE=0x2X` -> the enable chain uses the swept address. NO source edit.
  CTO-gated: setting the override is an enable-chain address change (CTO call); the MECHANISM is pre-built,
  the override is NOT set here. (Verified: a `-DM1_U6_TWI_ADDR_OVERRIDE=0x21u` build compiles clean.)

================================================================================
## 2. HARMLESS self-proof (probe touches NO codec-enable state)
================================================================================
- The probe `m1_u6_addr_responds` Writes ONLY `regptr` whose value is `M1_U6_IODIRA` (0x00) -- a register
  POINTER for the subsequent READ. It does NOT Write GPIOA (0x12) and does NOT write any ~EN data value
  (0x25/0x05). grep confirms: the only `m1_u6_write(h, M1_U6_GPIOA, ...)` calls (0x25/0x05, the ~EN bits)
  are in the ENABLE function, NOT in the probe.
- A register READ on I2C cannot change the target's register contents -> the codec-enable state (driven by
  GPIOA ~EN bits) is untouched by the sweep. The sweep is a pure address-answer test.
- The sweep opens/closes its OWN handle per address; it does not perturb the enable function's handle/state.

================================================================================
## 3. INTERPRETATION TABLE (sweep + codec_write_rc + hwerr -> root cause; per STAGE4_BATCH_PLAN sec 2)
================================================================================
| g_m1_u6_addr_sweep | g_m1_codec_write_rc | g_m1_softcfg_hwerr | ROOT CAUSE | FIX |
|---|---|---|---|---|
| **exactly ONE addr = 1** (e.g. [0x20..0x27] one ACK) | 0 (codec ACK = bus good) | ANAK on 0x22 | **R1a ADDRESS ERROR**: U6 is at the swept addr, not 0x22 | rebuild `-DM1_U6_TWI_ADDR_OVERRIDE=0x2X` (CTO-gated) |
| 0x22 entry = 1 AND others 0 | 0 | DNAK (data-phase) | **R1-DNAK**: U6 answers 0x22 but NAKs data (BANK / register-addr) | block B-d BANK/register fix (CTO-gated) |
| **all 8 = 0** (no addr answers) | 0 (codec ACK = bus good) | ANAK | **R1c U6 ABSENT / unpowered / held-in-reset** | block B-c readiness / carrier power-reset (board) |
| all 8 = 0 OR LOSTARB | **non-zero** (codec ALSO NACK) | LOSTARB / 11 | **R0 BUS-LEVEL** (pull-up/SCL-SDA/actual-SCL) -- NOT U6-specific; audio was carrier default | block B-e bus-level (scope, board) |
| any sweep = 1 AND codec_write_rc non-zero | non-zero | mixed | ANOMALY (device answers but bus also fails) | re-scope; do not auto-conclude |
Notes: an address that ACKs the probe READ proves a device answers there; "exactly one ACK in 0x20..0x27"
is the MCP23017 strap signature. codec_write_rc is the R1-vs-R0 gate (R49 discriminant); the sweep refines
R1 into R1a(address)/R1c(absent). hwerr ANAK/DNAK/LOSTARB cross-confirms.

================================================================================
## 4. DIAGNOSTIC-BUILD READOUT LIST (one idle read; for the runbook)
================================================================================
Read ALL of these by JTAG symbol name at idle (free-run; no callback breakpoints). All are file-scope
volatiles found by symbol.
### softcfg diagnostics (m1_softconfig.c)
| symbol | type | meaning / expected |
|---|---|---|
| g_m1_softcfg_open_rc | int | adi_twi_Open rc (0=ok) |
| g_m1_softcfg_addr_rc | int | SetHardwareAddress rc (0=ok) -- note: programs addr reg, does NOT bus-transact |
| g_m1_softcfg_set_rc[3] | int[3] | SetPrescale/SetBitRate/SetDutyCycle raw rc (0=ok) |
| g_m1_softcfg_rc[5] | int[5] | per-write raw ADI_TWI_RESULT (0=SUCCESS, 11=PERIPHERAL_ERROR NACK); idx 0=IODIRA..4=GPIOA-run |
| g_m1_softcfg_hwerr | uint32 | GetHWErrorStatus after first write: ANAK/DNAK/LOSTARB/BUFxx |
| **g_m1_u6_addr_sweep[8]** | int[8] | **R50 NEW** -- per-address ACK 0x20..0x27 (1=ACK/0=NACK); exactly-one-ACK = U6 address |
| g_m1_main_softcfg_rc | int | the OR'd enable rc (m1_main.c mirror; non-zero = some write failed) |
### codec discriminant (m1_loopback_tdm.c -- R49)
| g_m1_codec_write_rc | int | raw rc of LAST codec TWI write -- 0=bus good(R1) / non-zero=bus-level(R0) |
### M1 stream health (m1_loopback_tdm.c)
| g_m1_valid | int | 1 = ran on board w/ codec+SPORT |
| g_m1_fg_stream_live | int | 1 = blocks grew AND non-zero audio (NOT a softcfg-success proof -- carrier default also lives) |
| g_m1_rx_block_count / g_m1_tx_block_count | uint32 | should grow + be equal (loopback closed) |
| g_m1_max_abs_sample | uint32 | >0 = live input |
| g_m1_cb_cyc_last / max / min | uint32 | io-callback CCNT (separate WO) |
| g_m1_main_pwrinit_rc / g_m1_main_init_rc | int | adi_pwr_Init / m1_loopback_init rc |
### power/main (m1_main.c)
| g_m1_main_pwrinit_rc | int | 0=ok |

================================================================================
## 5. guard-check (both builds) + build-mechanism verification
================================================================================
- M1 transparent build (M2_FIRA_INLOOP=0): all 5 TUs PASS. M2 FIRA build (M2_FIRA_INLOOP=1): PASS. RC=0.
- `-DM1_U6_TWI_ADDR_OVERRIDE=0x21u` build: compiles clean (the R1a fix mechanism works).
- Default (no override): preprocessor confirms the enable function still uses 0x22 (behavior-identical).
- File boundary: ONLY m1_softconfig.c (2 copies) changed. m1_main.c untouched (0 sweep refs -- the sweep
  auto-runs inside the enable fn, a line-A file). m1_loopback_tdm.c / M2 callback / .ldf untouched this WO.
- ASCII clean; both copies byte-identical.

================================================================================
## 6. HONEST GAPS
================================================================================
- The sweep proves which ADDRESS a device ANSWERS, not that the answering device IS the U6 (another I2C
  device could sit in 0x20..0x27). Exactly-one-ACK in that range + MCP23017 strap convention is strong, but
  the schematic confirms the part. [board-confirm: SOMCRR U6 part + strap.]
- The probe READ ACKing proves address-reachability; it does NOT prove the subsequent ENABLE writes (data
  phase) will ACK -- a DNAK (BANK/register) could still fail writes. codec_write_rc + hwerr DNAK cover that.
- R0 bus-level (if codec_write_rc also NACK) is NOT fixed by an address override -- it needs the board scope
  (B-e). The sweep would likely show all-0 / LOSTARB in that case.
- If the device answers a NON-0x20..0x27 address (out of the MCP23017 range), this sweep misses it -- the
  range is the MCP23017-class assumption; widen only if the schematic shows a different part. [board-confirm.]
- Applying the address override (or any block-B fix) is CTO-gated (enable-chain change, parallel safety vs
  line B M2 commit 12a5920 -- no file collision, but CTO ruling required).

================================================================================
## SUMMARY (HALT)
================================================================================
- ADDED (probe/obs-only, m1_softconfig.c both copies): g_m1_u6_addr_sweep[8] + a HARMLESS register-READ
  address probe (0x20..0x27) that touches NO ~EN bit, auto-run at the top of the enable fn (m1_main.c not
  touched). + a build-configurable M1_U6_TWI_ADDR override (-D, default 0x22, R1a fix mechanism, CTO-gated).
- HARMLESS proven: the probe Writes only the register pointer (0x00), reads IODIRA; GPIOA/~EN writes are
  ONLY in the enable fn. Default 0x22 + 5 enable writes + return rc all byte-unchanged.
- ONE diagnostic run now yields: codec_write_rc (R1 vs R0) + hwerr (ANAK/DNAK/LOSTARB) + addr_sweep (which
  address, R1a) -> the interpretation table (sec 3) pins the root cause; if R1a, the -D override rebuild
  fixes it without a source edit (CTO-gated).
- guard both builds PASS (RC=0); override build clean. File boundary clean (only softconfig). ASCII; no commit.
- HALT: PM verifies + lands (probe/obs-only) -> diagnostic board run -> read the sec-4 list -> sec-3 table
  -> CTO-gated fix (override / block B). No CTO ruling predicted.
