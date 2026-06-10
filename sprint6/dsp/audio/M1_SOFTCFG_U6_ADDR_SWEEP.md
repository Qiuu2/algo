# M1 softcfg U6 address self-probe (R50 batch-pack core) -- diagnostic + pre-built fix (HALT)

> dsp-algorithm teammate, 2026-06-08. Batch-pack goal (STAGE4_BATCH_PLAN.md): compress softcfg
> diagnose -> fix -> verify into ONE diagnostic run. The existing obs (codec_write_rc / hwerr / set_rc,
> 3a3bb50) already splits R1(U6-specific) vs R0(bus-level); this adds a U6 ADDRESS SELF-PROBE so the SAME
> run also finds the correct address if it is an address error (R1a). probe/obs-ONLY -- no codec-enable
> logic change. ASCII. No commit (critic R50). HALT. Does NOT predict board readings.

================================================================================
## 1. WHAT WAS ADDED (m1_softconfig.c only; both copies byte-identical)
================================================================================
### (A) Address self-probe -- harmless ONLY for register-pointer parts (CONDITIONAL, see sec 2), probe-only
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
## 2. self-proof + the CONDITIONAL it rests on (R51 audit correction)
================================================================================
- The probe `m1_u6_addr_responds` Writes ONLY `regptr` whose value is `M1_U6_IODIRA` (0x00) -- a register
  POINTER for the subsequent READ. It does NOT Write GPIOA (0x12) and does NOT write any ~EN data value
  (0x25/0x05). grep confirms: the only `m1_u6_write(h, M1_U6_GPIOA, ...)` calls (0x25/0x05, the ~EN bits)
  are in the ENABLE function, NOT in the probe.
- For an MCP23017 (register-pointer device) a 1-byte 0x00 write only SELECTS the IODIRA register for the
  following READ -> the target's register contents (incl. GPIOA ~EN) are untouched -> codec-enable state
  preserved. The sweep uses its OWN handle per address (open/close), not the enable handle.
- **R51 AUDIT CORRECTION (the R50 "iron-clad harmless" claim was CONDITIONAL, not absolute):** the probe
  DOES put a real 1-byte `0x00` on the wire (m1_softconfig.c:111, `adi_twi_Write(hp,&regptr,1u,true)`) to
  EVERY answering address in 0x20..0x27. 0x20..0x27 is also the PCF8574/PCF857x I/O-expander base range,
  where a part has NO register pointer and a written byte drives the OUTPUT PINS directly. So "harmless" is
  TRUE for MCP23017/PCAL-class (register-pointer) parts and FALSE for a PCF857x-class part in that range.
  And the sweep auto-runs at m1_softconfig.c:144 on the F-SRU-1 BOOT path (every boot), not behind a
  diagnostic flag. **Therefore harmlessness REQUIRES a schematic confirm that only MCP23017-class parts sit
  at 0x20..0x27** (a CTO/PM pre-handoff gate, see runbook). The robust fix (gate the sweep behind a separate
  diagnostic build flag so it is OFF the normal boot path) is a codec-enable-path change = CTO-gated, NOT
  done this round (CTO ruling: doc + schematic-confirm only).

================================================================================
## 3. INTERPRETATION TABLE (sweep + codec_write_rc + hwerr -> root cause; per STAGE4_BATCH_PLAN sec 2)
================================================================================
**hwerr is an ENUM ORDINAL, not a bit-mask** (R51 audit; ADI_TWI_EVENT sequential enum, installed header
adi_twi_2156x.h:99-104): `0`=none, `3`=DNAK (data-phase NAK), `4`=ANAK (addr-phase NAK), `5`=LOSTARB
(arbitration loss). adi_twi_GetHWErrorStatus writes ONE ordinal. **Decode by equality (==4), NOT by bit.**
Also: hwerr is read once after write[0] (IODIRA); if softcfg_rc[1..4] is nonzero but hwerr=0, the failing
write is later -> key off softcfg_rc.
**PRIMARY key = (sweep-pattern, codec_write_rc); hwerr is confirmatory. hwerr disagrees with the primary key
=> ANOMALY (send to PM), do not auto-conclude.**
**SCOPE (R52): this table applies to the DEFAULT-0x22 diagnostic build ONLY.** Under
-DM1_U6_TWI_ADDR_OVERRIDE the sweep STILL scans 0x20-0x27 and naturally reproduces "exactly one ACK, not
0x22" -- that is the EXPECTED board reality (the sweep is independent of the override; the build console line, not the sweep, proves the override took), NOT R1a re-firing. Round-2 (override build) judgment = runbook
"第 2 次测试" (round-2 test) section (expected: sweep unchanged / hwerr==0 / rc all 0), never this table.

| g_m1_u6_addr_sweep | g_m1_codec_write_rc | g_m1_softcfg_hwerr | ROOT CAUSE | FIX |
|---|---|---|---|---|
| **exactly ONE addr = 1 AND it is NOT 0x22 (sweep[2])** | 0 (codec ACK = bus good) | 4=ANAK | **R1a ADDRESS ERROR**: U6 is at the swept addr, not 0x22 | rebuild `-DM1_U6_TWI_ADDR_OVERRIDE=0x2X` (CTO-gated) |
| 0x22 (sweep[2]) = 1 AND others 0 | 0 | 3=DNAK (data-phase) | **R1d (R1-DNAK)**: U6 answers 0x22 but NAKs data (BANK / register-addr) | block B-d BANK/register fix (CTO-gated) |
| **all 8 = 0** (no addr answers) | 0 (codec ACK = bus good) | 4=ANAK | **R1c U6 ABSENT / unpowered / held-in-reset** | block B-c readiness / carrier power-reset (board) |
| all 8 = 0 | **non-zero** (codec ALSO NACK) | 5=LOSTARB | **R0 BUS-LEVEL** (pull-up/SCL-SDA/actual-SCL) -- NOT U6-specific; audio was carrier default | block B-e bus-level (scope, board) |
| **>=2 addr = 1** (multiple answer) | any | any | **ANOMALY: foreign device(s) in range** | **do NOT auto-override**; re-scope (schematic) |
| any sweep = 1 AND codec_write_rc non-zero / LOSTARB | non-zero | 5=LOSTARB | **ANOMALY** (device answers but bus also fails) | re-scope; do not auto-conclude |
Notes: an address that ACKs the probe READ proves a device answers there; "exactly one ACK in 0x20..0x27"
is the MCP23017 strap signature. codec_write_rc is the R1-vs-R0 gate (R49 discriminant) BUT it is the LAST
codec write's rc (m1_loopback_tdm.c:260, last-write-wins); a transient mid-sequence NACK can read back 0 --
if LOSTARB or sweep-all-0 says "bus", do not over-trust cwrc=0. The sweep refines R1 into R1a(address)/
R1c(absent). hwerr cross-confirms by ordinal equality. all-0 + cwrc=0 can ALSO be wrong-actual-prescale/SCL
timing -> require hwerr==4 (ANAK, not 5 LOSTARB) before concluding U6-absent.

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
| g_m1_softcfg_hwerr | uint32 | GetHWErrorStatus after write[0] ONLY -- **enum ordinal** 0=none/3=DNAK/4=ANAK/5=LOSTARB (NOT a bit-mask); if rc[1..4]!=0 but hwerr=0 the failing write is later, key off softcfg_rc |
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
- **(R51 audit) The probe's 0x00 write is harmless ONLY for register-pointer parts (MCP23017); a PCF857x in
  0x20..0x27 would have its outputs driven by 0x00. Harmlessness REQUIRES schematic confirm of the parts in
  range (CTO/PM pre-handoff gate). The sweep is on the F-SRU-1 boot path, not behind a diag flag.**
- **(R51 audit) sweep open rc is NOT separately captured**: the sweep shares the TWI memory (s_m1_u6_mem,
  sized by ADI_TWI_MEMORY_SIZE). If the on-target macro yields an undersized buffer, Open returns
  INSUFFICIENT_MEMORY and EVERY sweep entry collapses to 0 -- indistinguishable from "U6 absent". Before
  concluding all-0 = R1c, confirm g_m1_softcfg_open_rc==0 (proxy for the TWI-mem sizing being OK on target).
- **(R51 audit) codec_write_rc is last-write-wins**, not an OR-aggregate -- a transient mid-sequence codec
  NACK reads back 0 and could mis-route the R1-vs-R0 gate. Treat cwrc=0 with caution if any bus symptom
  (LOSTARB, sweep all-0) is present. (An OR-aggregate g_m1_codec_write_rc_any is a future code change,
  CTO-gated, not this round.)

================================================================================
## SUMMARY (HALT)
================================================================================
- ADDED (probe/obs-only, m1_softconfig.c both copies): g_m1_u6_addr_sweep[8] + a register-READ address probe
  (0x20..0x27) that touches NO ~EN bit, auto-run at the top of the enable fn (m1_main.c not touched). + a
  build-configurable M1_U6_TWI_ADDR override (-D, default 0x22, R1a fix mechanism, CTO-gated).
- Harmless ONLY for register-pointer parts (MCP23017): the probe Writes only the register pointer (0x00),
  reads IODIRA; GPIOA/~EN writes are ONLY in the enable fn. **CONDITIONAL (R51): the 0x00 byte drives outputs
  on a PCF857x-class part in 0x20..0x27 -> harmlessness REQUIRES schematic confirm of the parts in range
  (CTO/PM pre-handoff gate, see sec 2 + sec 6); boot-path gating is CTO-gated, not done this round.**
  Default 0x22 + 5 enable writes + return rc all byte-unchanged.
- ONE diagnostic run now yields: codec_write_rc (R1 vs R0) + hwerr (ANAK/DNAK/LOSTARB) + addr_sweep (which
  address, R1a) -> the interpretation table (sec 3) pins the root cause; if R1a, the -D override rebuild
  fixes it without a source edit (CTO-gated).
- guard both builds PASS (RC=0); override build clean. File boundary clean (only softconfig). ASCII; no commit.
- HALT: PM verifies + lands (probe/obs-only) -> diagnostic board run -> read the sec-4 list -> sec-3 table
  -> CTO-gated fix (override / block B). No CTO ruling predicted.
