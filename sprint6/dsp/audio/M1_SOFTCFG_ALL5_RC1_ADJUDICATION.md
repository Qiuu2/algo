# M1 softcfg ALL rc[0..4]=1 semantics -- [L1] installed-header adjudication (HALT)

> dsp-algorithm teammate, 2026-06-08. Board re-run: g_m1_softcfg_rc[0..4] ALL = 1, open_rc=0, addr_rc=0,
> audio works (rx=tx=7078). This is NOT in any R44 row (R44 assumed individual rc=1). CTO: characterize
> rc=1 from the SOURCE + ADI semantics -- NOT from convention-guess, NOT from "loopback works". ASCII. No
> commit. HALT. Does NOT predict CTO ruling.
>
> BREAKTHROUGH SOURCE [L1]: the REAL installed CCES 2.12.1 TWI driver header exists on this machine:
>   /opt/analog/cces/2.12.1/ARM/arm-none-eabi/.../drivers/twi/adi_twi.h -> selects adi_twi_2156x.h for
>   __ADSP21569_FAMILY__ (line 21) -> so adi_twi_2156x.h IS the 21569 TWI contract (same header the SHARC
>   21569 build uses; the family macro routes both ARM and SHARC 2156x to this file). The result enum + the
>   adi_twi_Write doc/signature below are READ DIRECTLY from it = [L1], not convention-guess.
>   (board-confirm residual: the SHARC-toolchain copy is not installed here; the FILE is the 2156x-family
>    header the 21569 selects -- bring-up can diff the SHARC include if paranoid, but the API contract is
>    the same SSL across cores.)

================================================================================
## 1. THE PREMISE WAS WRONG: 4th arg = bRestart, and adi_twi_Write is BLOCKING
================================================================================
PM/R44/my-own-prior-doc assumed the 4th arg `false` = "bWaitFlag non-blocking". The installed header
FALSIFIES this:
- adi_twi_2156x.h:221 doc: **"Write data to a TWI device (blocking)."** adi_twi_Write IS BLOCKING.
- adi_twi_2156x.h:223-228 signature: `adi_twi_Write(hDevice, pBuffer, nBufSize, bool const bRestart)`.
  The 4th param is **bRestart** (I2C repeated-start), NOT bWaitFlag. (grep: the header has `bRestart` x4,
  `bWaitFlag` x0.)
- The NON-blocking write is a DIFFERENT function: `adi_twi_SubmitTxBuffer(...)` (:151 doc "non-blocking",
  paired with adi_twi_IsTxBufferAvailable / adi_twi_GetTxBuffer). M1 does NOT call that -- M1 calls the
  BLOCKING adi_twi_Write.
=> `adi_twi_Write(h, buf, 2u, false)` = a BLOCKING 2-byte write with bRestart=false (normal STOP-terminated
   register write). It blocks until the transfer completes and returns the REAL transfer result. There is
   NO non-blocking ambiguity, NO "submit-OK-but-pending" code, NO buffer-reuse race (blocking = prior write
   completes before the shared s_m1_u6_buf is overwritten). PM's leads (a)/(b) both rest on the non-blocking
   premise and are MOOT.

## 2. rc=1 SEMANTICS (from source + the [L1] enum): a REAL, DETERMINISTIC write FAILURE
================================================================================
- m1_softconfig.c:61 `return (adi_twi_Write(...) == ADI_TWI_SUCCESS) ? 0 : 1;` -- returns 0 iff the BLOCKING
  write returned ADI_TWI_SUCCESS, else 1.
- [L1] enum (adi_twi_2156x.h:64-79): `ADI_TWI_SUCCESS = 0u` ("The API call succeeded"), then 14 distinct
  ERROR codes (1=FAILURE, 2=TRANSFER_IN_PROGRESS, 6=BAD_ADDRESS, 7=DEVICE_IN_USE, 11=PERIPHERAL_ERROR
  "error processing the buffer", ...). For the BLOCKING write there is no benign non-SUCCESS code -- any
  non-zero is a genuine failure of that transfer.
=> **rc=1 = the blocking write returned a real ERROR (non-SUCCESS).** It is NOT "success with non-zero
   semantics", NOT a non-blocking submit code. ALL FIVE writes returned a real error. open/addr returned
   SUCCESS (U6 reachable, addr 0x22 accepted at the API layer).
   (board-confirm: WHICH of the 14 codes -- m1_u6_write collapses 1..14 to "1", so the actual code is lost;
    section 4 instrumentation recovers it.)

## 3. THREE-POSSIBILITY ADJUDICATION of "all 5 fail + open/addr ok + audio works"
================================================================================
With the blocking/bRestart fact established, PM's (a) "non-blocking submit misjudged" and (b) "non-blocking
+ buffer-reuse race" are BOTH ELIMINATED (no non-blocking here). The live possibilities:
- **(c1) the 5 BLOCKING writes genuinely failed at the bus/peripheral layer** (e.g. U6 NACKs the data byte,
  or a config/state error) -> the data NEVER reached U6 -> U6's ~EN/RESET/dir were NOT driven by M1 ->
  **the codec is enabled by the CARRIER DEFAULT, F-SRU-1 is a NO-OP** -> a board with a codecs-OFF default
  goes SILENT. This is the natural reading: a deterministic, all-5, repeatable failure of blocking writes
  means the writes did not take, and the working audio is the carrier default (exactly the trap F-SRU-1
  was built to prevent). STRONGLY INDICATED but the ACTUAL error code is needed to confirm + to fix.
- **(c2) a benign-but-non-SUCCESS blocking return** -- searched the [L1] enum: there is NO such code for
  the blocking Write (TRANSFER_IN_PROGRESS=2 is for the non-blocking path; the blocking call does not
  return until done). So (c2) is NOT supported by the header. (If the SHARC variant differed, that is the
  board-confirm residual -- but the 2156x header shows no benign blocking-error.)
- **(c3) writes failed yet U6 latched anyway** -- not credible: a failed I2C transfer (NACK/abort) does not
  latch the register. So if the writes failed, U6 was NOT configured by M1.

LEAN: **(c1) -- the writes really failed, the codec rides the carrier default, F-SRU-1 is NOT in effect.**
The all-5 + repeatable + open/addr-OK pattern is the signature of the WRITES failing (not the device being
absent). Working audio does NOT contradict this (carrier default). I do NOT use "audio works" to claim
success -- per the CTO rule; the [L1] semantics say the writes failed.

## 4. CAN WE SETTLE (I) vs (II) FROM THIS DATA? -- NO direct confirm; but the [L1] semantics already FLAG (II)
================================================================================
- (I) F-SRU-1 EFFECTIVE (all 5 wrote OK): CONTRADICTED -- all 5 returned non-SUCCESS [L1] = the writes did
  NOT succeed. (I) is OUT.
- (II) codec rides carrier default, swap-silence risk, MUST FIX: **INDICATED** -- 5 failed blocking writes
  mean M1 did not configure U6; the codec is on the carrier default; F-SRU-1 a no-op. The remaining unknown
  is only WHY the writes fail (which error code) and HOW to fix, NOT whether F-SRU-1 took effect (it did not).
- So unlike the previous (individual-rc) case, this data is NOT "indeterminate" -- the [L1] blocking
  semantics + all-5-failed DETERMINE that F-SRU-1 is NOT in effect (state II). What still needs a re-run is
  the ROOT CAUSE (capture the raw ADI_TWI_RESULT code) to pick the fix. Honest: F-SRU-1 = NOT EFFECTIVE
  (high confidence from [L1]); the fix path needs the error code.

## 5. FIX -- NOT "bWaitFlag false->true" (that premise is dead). The real next step = capture the raw code
================================================================================
The CTO-suggested fix (false->true blocking) is MOOT: adi_twi_Write is ALREADY blocking; `false` is bRestart
not bWaitFlag; flipping it to `true` would WRONGLY insert an I2C repeated-start (no STOP) into a simple
register write and likely make it WORSE. DO NOT flip bRestart.

The definitive next step is DIAGNOSTIC, not a behavior change: **capture the RAW ADI_TWI_RESULT per write**
(which of the 14 codes), so the board re-run names the failure -> then fix the named cause. This is still
OBSERVATION-ONLY (no codec-enable logic change), so it does not need the parallel-safety CTO merge gate that
a real logic change would.

### change block A (OBSERVATION-ONLY -- raw error code; guard-checked clean, NOT applied)
Change m1_u6_write (m1_softconfig.c:57-62) to return the raw result; the rc |= / return rc semantics are
preserved (rc nonzero iff any write != SUCCESS):
```c
static int m1_u6_write(ADI_TWI_HANDLE h, uint8_t reg, uint8_t val)
{
    s_m1_u6_buf[0] = reg;
    s_m1_u6_buf[1] = val;
    return (int)adi_twi_Write(h, s_m1_u6_buf, 2u, false);   /* RAW ADI_TWI_RESULT: 0=SUCCESS, 1..14=which error */
}
```
Now g_m1_softcfg_rc[i] holds the ACTUAL code per write. Board re-run -> read which code (e.g. all =11
ADI_TWI_PERIPHERAL_ERROR = bus NACK/abort; =6 BAD_ADDRESS; =1 generic FAILURE). (Optionally also call
adi_twi_GetHWErrorStatus (:180) after a failure for the HW-level reason -- a second observation-only add.)

### change block B (LOGIC CHANGE -- DO NOT apply without CTO; parallel-safety gate)
Only AFTER the raw code names the cause. Likely candidates, depending on the code:
- if PERIPHERAL_ERROR/NACK: the data byte is NAK'd -> check U6 part/addr/sub-addr-mode (MCP23017 BANK bit;
  reg 0x12/0x13/0x00/0x01 assume BANK=0) or add a retry; possibly the write needs the device addressed
  differently. This is a CODEC-ENABLE LOGIC change -> STOP, report to CTO, do not self-merge (line B M2 is
  committed 12a5920; no file collision, but changing the enable chain still needs CTO's call per parallel
  safety). NOT provided as an apply-ready block until the cause is known -- guessing the fix before the code
  is read would repeat the "don't assume" error.

## 6. ALT / POST comparison (the bRestart usage cross-check)
================================================================================
- ALT SoftConfig (the SAME codec-enable use case): `adi_twi_Write(hDevice, twiBuffer, 2, false)` -- SAME
  blocking call, SAME bRestart=false, SAME one-buffer-reuse across the write loop, no Enable, Close after.
  [SoftConfig_ADC_DAC.c:166] It treats `!= ADI_TWI_SUCCESS` as failure (CHECK_RESULT aborts, :167). So ALT
  EXPECTS these blocking writes to SUCCEED. M1 uses the identical pattern -- so M1's all-5-fail is anomalous
  vs the ALT contract = a real bus/config problem on M1's run, not a coding-pattern error.
- ALT loopback Write_TWI_8bit_Reg (codec PLL/reg writes that DEMONSTRABLY work): `adi_twi_Write(..., 2u,
  false)` blocking, bRestart=false, devBuffer reuse, IGNORES the return [ALT.c:482]. Its WRITE-then-READ
  uses bRestart=true (:492) ONLY before a Read (repeated-start to turn the bus around for the read). So
  bRestart=false for a standalone write is CORRECT and PROVEN-WORKING in ALT -- M1's false is right; the
  failure is NOT the bRestart value.
=> ALT confirms M1's call form is correct. M1's all-5-fail is therefore a runtime bus/peripheral condition
   (named by the raw code on re-run), NOT a wrong API usage.

## 7. R44 TABLE BACKFILL ROW
================================================================================
```
| g_m1_softcfg_rc[0..4] ALL =1, open/addr=0 (NOT a single-write case) | [L1 adi_twi_2156x.h:221 "blocking",
  :223 bRestart not bWaitFlag] adi_twi_Write is BLOCKING; 4th arg=bRestart(false=normal write), NOT a
  non-blocking flag. So rc=1 = a REAL blocking-write FAILURE (enum :65 SUCCESS=0; non-SUCCESS=genuine error,
  no benign blocking code). ALL 5 failing + open/addr OK = M1 did NOT configure U6 -> codec rides CARRIER
  DEFAULT -> F-SRU-1 NOT in effect (state II, swap-silence risk) -> MUST FIX. NOT (I). Fix is NOT
  bRestart false->true (already blocking; flipping inserts a wrong repeated-start). NEXT = capture raw
  ADI_TWI_RESULT per write (obs-only change block A) to name the cause, THEN a CTO-gated logic fix. |
```

================================================================================
## SUMMARY (HALT)
================================================================================
- [L1 installed header] adi_twi_Write is BLOCKING; 4th arg = bRestart (false=normal write), NOT bWaitFlag.
  The non-blocking premise (PM/R44/CTO framing) is FALSIFIED. The non-blocking API is the separate
  adi_twi_SubmitTxBuffer, which M1 does not call.
- rc=1 = a REAL blocking-write FAILURE (enum SUCCESS=0, no benign blocking non-SUCCESS). ALL 5 writes failed.
- (I)/(II): (I) F-SRU-1 effective is OUT (writes did not succeed). (II) codec rides carrier default,
  F-SRU-1 NOT in effect, swap-silence risk -- INDICATED by [L1] semantics (NOT by "audio works"). Working
  audio = carrier default. High confidence state II; the only open item is the ROOT-CAUSE code, not the
  verdict.
- FIX: NOT bRestart false->true (premise dead). NEXT = capture raw ADI_TWI_RESULT per write (obs-only change
  block A, guard-checked, NOT applied) to name the failure code on a re-run; THEN a CTO-gated logic fix
  (change block B framework, not apply-ready until the code is known -- no guessing the fix).
- ALT/POST: identical blocking + bRestart=false + buffer-reuse pattern; ALT expects SUCCESS and its codec
  writes work -> M1's call form is correct; the all-5-fail is a runtime bus/peripheral condition.
- HALT: awaiting CTO -> apply obs-only change block A (after critic R48) -> board re-run -> read the raw
  codes -> CTO-gated logic fix. No commit. No CTO ruling predicted.
