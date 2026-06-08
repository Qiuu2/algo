# M1 softcfg_rc=1 semantics adjudication -- "gamble on carrier default" hunt (HALT)

> dsp-algorithm teammate, 2026-06-08. M1 board run: g_m1_main_softcfg_rc = 1 (NON-zero) BUT audio works
> (stream_live=1, rx=tx=5757 closed loop). Question: is rc=1 "success (non-zero==good)" or "a TWI write
> failed"? If failed: is the codec actually riding the CARRIER DEFAULT (F-SRU-1 software enable NOT really
> in effect), so a different board could go silent? Read code + ADI API convention -- NOT "audio works =>
> rc=1 ok". ASCII. No commit. HALT. Does NOT predict CTO ruling.
>
> SOURCES: m1_softconfig.c @ m1_cces_project/src; ADI TWI convention (KB usage, no local enum body);
> R39 routing survey sec 2 (U6 bit map); ALT SoftConfig_*.c.

================================================================================
## 1. rc=1 SEMANTICS: it is a FAILURE, not "non-zero==success"
================================================================================
### The code says rc is a FAILURE count, not a status
- `m1_u6_write` (m1_softconfig.c:53): `return (adi_twi_Write(...) == ADI_TWI_SUCCESS) ? 0 : 1;`
  -> returns **0 on success, 1 on any non-SUCCESS**. There is NO "non-zero == good" path. rc=1 from a
  single write means that write did NOT return ADI_TWI_SUCCESS.
- `m1_softconfig_enable_codecs` (:65-88): `rc = 0`, then `rc |= <5 writes>`, `return rc`. rc=1 = at least
  one of the 5 writes returned non-SUCCESS. (The `@return 0 = ok, !=0 = honest fail` header :59 confirms
  the AUTHORED intent: non-zero = fail.)
=> **rc=1 = a genuine write failure.** It is NOT a "success with non-zero semantics."

### ADI API convention check -- could non-SUCCESS still be benign? [convention firm; enum body board-confirm]
- ADI SSL/driver convention: `ADI_<MOD>_SUCCESS` is the all-good code; EVERY KB example treats
  `!= ADI_<MOD>_SUCCESS` as failure and aborts (ALT SoftConfig CHECK_RESULT :115-122 aborts on
  `!= ADI_TWI_SUCCESS`; adi_spu/adi_tmr/adi_dmc usages identical). ADI_TWI_SUCCESS = 0 is the convention
  (first enumerator).
- The real `ADI_TWI_RESULT` enum BODY is NOT in the local KB (only config headers + usage). So the EXACT
  numeric value of ADI_TWI_SUCCESS and whether a benign/partial code exists is [board-confirm] -- but NO
  KB usage anywhere tolerates a non-SUCCESS as OK, and a TWI NACK/bus-error is a DISTINCT error code,
  still `!= SUCCESS`. So even a NACK makes m1_u6_write return 1 = correctly flagged failure.
=> No evidence of a benign non-SUCCESS. rc=1 is a real failed write. (board-confirm: the precise enum body
   only matters to NAME which error; it does not change "failed".)

================================================================================
## 2. WHICH write failed -> codec-enable dependency  (the OR masks it)
================================================================================
The 5 writes and their codec-enable criticality (R39 U6 bit map; ~ADAUxx_EN are active-low on Port A):
| # | write | reg/val | codec-enable critical? | if THIS one fails |
|---|-------|---------|------------------------|-------------------|
| W0 | IODIRA | 0x00/0x18 | **YES** (makes Port A b7,6,5 OUTPUTS) | GPIOA latch has no pin effect -> ~EN/RESET pins stay default dir -> codec NOT sw-driven |
| W1 | IODIRB | 0x01/0x00 | NO (Port B dir; jack/eth/spdif) | codec still enabled via W0+W3+W4 |
| W2 | GPIOB | 0x13/0xFD | NO (Port B latch; no ~ADAUxx_EN) | codec still enabled; only jack/eth/spdif affected |
| W3 | GPIOA | 0x12/0x25 | **YES** (~EN=0 enable + RESET=1 assert) | ~EN not driven low / reset not pulsed -> codec NOT sw-enabled |
| W4 | GPIOA | 0x12/0x05 | **YES** (~EN=0 enable + RESET=0 deassert, run) | final run state not set; if W3 also weak -> codec NOT sw-enabled |

KEY: the codec ~EN lines are on **Port A (W3/W4 via GPIOA), and require W0 (IODIRA) to be outputs.**
Port B (W1/W2) is OFF the codec-enable path. So:
- rc=1 from W1 or W2 (Port B) ONLY -> **codec IS software-enabled (W0+W3+W4 succeeded) -> F-SRU-1 EFFECTIVE.**
- rc=1 from W0, W3, or W4 -> **codec NOT software-driven -> it is riding the CARRIER DEFAULT** (the trap).

The `rc |=` (m1_softconfig.c:75-84) OR-collapses all 5 into one bit -> **from rc=1 alone we CANNOT tell
which failed**, hence cannot tell whether F-SRU-1 took effect. (This is the same OR-masking visibility gap
the H2 ISR work hit -- aggregate hides the mechanism.)

### Why "audio works" does NOT settle it (the WO's hard rule)
Audio working (stream_live=1, rx=tx=5757) proves the codec IS enabled RIGHT NOW on THIS board. It does
NOT prove WHY: either (path-sw) W3/W4 drove ~EN low, OR (path-default) W3/W4 failed but the SOMCRR carrier
already had the codecs enabled by its power-on/CPLD default (which is exactly what ALT relied on -- its
Switch_Configurator was commented out, F-SRU-1 root). On THIS board both paths produce working audio. They
diverge on a board whose default is codecs-OFF: path-sw still works, path-default goes SILENT. So "audio
works" is consistent with BOTH the safe and the unsafe case -- it cannot discriminate. Must read per-write.

================================================================================
## 3. F-SRU-1 EFFECTIVENESS -- three-state (cannot resolve locally; lean III)
================================================================================
- **(I) rc=1 non-fatal (W1/W2 Port-B), F-SRU-1 effective, no swap risk**: POSSIBLE. If only a Port-B write
  NACK'd, W0+W3+W4 succeeded -> codec software-enabled -> swapping boards is safe. Cannot CONFIRM from rc=1.
- **(II) W0/W3/W4 (codec-critical) failed, codec rides carrier default, swap risk SILENT, MUST FIX**:
  ALSO POSSIBLE. If a codec-critical write failed, the working audio is the carrier default doing the job,
  and F-SRU-1 is NOT actually in effect -> the "gamble on carrier default" trap is live -> a board with a
  codecs-OFF default goes silent. Cannot CONFIRM or RULE OUT from rc=1.
- **(III) local evidence insufficient -> per-write board re-run REQUIRED**: **THIS IS THE HONEST STATE.**
  The OR-mask + "audio works on this board" cannot distinguish (I) from (II). Resolving it needs the
  per-write rc (section 4) on a board re-run. I do NOT assume (I) just because audio works (that would be
  the exact assumption the WO forbids).

LEAN: **(III)**. Do not declare F-SRU-1 effective on the strength of working audio. The fix is cheap
(per-write instrumentation + one re-run) and definitive. Pending that, treat F-SRU-1 as **NOT CONFIRMED**
and the swap-silence risk as **OPEN**.

================================================================================
## 4. PER-WRITE INSTRUMENTATION change block (CTO board re-run; NOT applied -- critic gate first)
================================================================================
Replaces the OR-masked rc with independent per-write rc globals. Does NOT change behavior (rc |= kept for
the same return value); only ADDS visibility. Apply to m1_cces_project/src/m1_softconfig.c. Guard-checked
clean (gcc -fsyntax-only, board-guarded region, RC=0).

(a) ADD globals (after `static uint8_t s_m1_u6_buf[2];`, m1_softconfig.c:47):
```c
/* [R44 per-write instrumentation -- CTO board re-run] independent rc per write (NOT OR-masked).
 * Index: 0=IODIRA 1=IODIRB 2=GPIOB 3=GPIOA-reset 4=GPIOA-run. -99=not-run. Read at idle (free-run). */
volatile int g_m1_softcfg_rc[5]    = { -99, -99, -99, -99, -99 };
volatile int g_m1_softcfg_open_rc  = -99;   /* adi_twi_Open rc (0=ok) */
volatile int g_m1_softcfg_addr_rc  = -99;   /* SetHardwareAddress rc (0=ok) */
```

(b) REPLACE the open + addr guards (m1_softconfig.c:67-69):
```c
    g_m1_softcfg_open_rc = (adi_twi_Open(M1_U6_TWI_DEV, ADI_TWI_MASTER, s_m1_u6_mem, ADI_TWI_MEMORY_SIZE, &h)
        == ADI_TWI_SUCCESS) ? 0 : 1;
    if (g_m1_softcfg_open_rc != 0) return 1;
    g_m1_softcfg_addr_rc = (adi_twi_SetHardwareAddress(h, M1_U6_TWI_ADDR) == ADI_TWI_SUCCESS) ? 0 : 1;
    if (g_m1_softcfg_addr_rc != 0) { (void)adi_twi_Close(h); return 1; }
```

(c) REPLACE the 5 `rc |=` writes (m1_softconfig.c:75-84) -- capture each index, keep rc |= for return:
```c
    g_m1_softcfg_rc[0] = m1_u6_write(h, M1_U6_IODIRA, M1_U6_IODIRA_VAL); rc |= g_m1_softcfg_rc[0]; /* 0x18 IODIRA */
    g_m1_softcfg_rc[1] = m1_u6_write(h, M1_U6_IODIRB, M1_U6_IODIRB_VAL); rc |= g_m1_softcfg_rc[1]; /* 0x00 IODIRB */
    g_m1_softcfg_rc[2] = m1_u6_write(h, M1_U6_GPIOB,  M1_U6_PORTB_VAL);  rc |= g_m1_softcfg_rc[2]; /* 0xFD GPIOB  */

    /* (2) assert codec reset (b5=1), codecs enabled (active-low ~EN=0) -- clean reset pulse */
    g_m1_softcfg_rc[3] = m1_u6_write(h, M1_U6_GPIOA, M1_U6_PORTA_RESET); rc |= g_m1_softcfg_rc[3]; /* 0x25 GPIOA reset */
    for (d = 0xffff; d > 0; d--) { /* hold reset */ }

    /* (3) deassert reset (b5=0), keep both codecs enabled -- run state */
    g_m1_softcfg_rc[4] = m1_u6_write(h, M1_U6_GPIOA, M1_U6_PORTA_RUN);   rc |= g_m1_softcfg_rc[4]; /* 0x05 GPIOA run */
    for (d = 0xffff; d > 0; d--) { /* let codecs come out of reset */ }
```
(Also expose the new globals in m1_loopback_tdm.h or a small header / extern in m1_main.c for the debugger;
or just read them by symbol name in the JTAG view.)

### CTO board re-run readout map (decides the three state)
| reading | meaning | verdict |
|---|---|---|
| g_m1_softcfg_rc = {0,0,0,0,0} | all 5 wrote OK -> but main rc was 1? re-check (shouldn't happen) | inconsistent -> re-scope |
| rc[1]=1 or rc[2]=1 only (Port B), rc[0]=rc[3]=rc[4]=0 | only Port-B write failed | **(I) F-SRU-1 EFFECTIVE, codec sw-enabled, NO swap risk** |
| rc[0]=1 (IODIRA) OR rc[3]=1 OR rc[4]=1 (GPIOA) | a codec-critical write failed | **(II) codec rides CARRIER DEFAULT, F-SRU-1 NOT in effect, SWAP-SILENCE RISK, FIX** (retry/TWI timing) |
| open_rc=1 or addr_rc=1 | U6 not reachable at all | codec entirely on carrier default -> (II) worst, fix bus |

================================================================================
## 5. SWAP-SILENCE RISK ASSESSMENT
================================================================================
- **Current board: NOT at risk** (audio demonstrably works; whatever enabled the codec is present here).
- **A different board: RISK = OPEN/UNKNOWN until the per-write re-run.** If the re-run shows a codec-critical
  write (W0/W3/W4) failed, then THIS board's audio is the carrier default, F-SRU-1 is a no-op, and a board
  with a codecs-OFF default WILL be silent -- the exact trap F-SRU-1 was created to prevent. If only Port-B
  failed, no swap risk.
- Do NOT ship/conclude "F-SRU-1 works" on this rc=1 until the per-write result is in. The whole point of
  F-SRU-1 (not gambling on carrier default) is undermined if a codec-critical write is silently failing.

### Secondary note (found while reading; not the rc cause)
ALT's SwitchConfig writes GPIO latch FIRST then direction (ALT SoftConfig array: {0x12,..},{0x13,..} then
{0x00,0x18},{0x01,0x00}); my code writes direction (IODIRA/B) FIRST then GPIO. My order (dir-then-latch) is
the conventional MCP23017 sequence and is arguably MORE correct, but it is a difference from ALT. It does
NOT cause rc=1 (a failed write fails regardless of order). Flagged for completeness; no change proposed.

================================================================================
## SUMMARY (HALT)
================================================================================
- rc=1 = a REAL TWI write FAILURE (m1_u6_write returns 1 on any non-SUCCESS; no benign-non-zero path; ADI
  convention SUCCESS=0/else=fail, firm across KB; exact enum body board-confirm but irrelevant to "failed").
- WHICH write failed is OR-MASKED -> cannot tell if a codec-critical (W0/W3/W4) or a harmless Port-B (W1/W2)
  write failed -> cannot tell if F-SRU-1 took effect or the codec rides the carrier default.
- "Audio works" does NOT settle it: working audio is consistent with BOTH sw-enable and carrier-default;
  they diverge only on a codecs-OFF-default board. Per the WO rule, NOT assuming success from working audio.
- THREE-STATE: lean **(III) insufficient -> per-write board re-run required** (section 4 instrumentation).
  Until then F-SRU-1 = NOT CONFIRMED, swap-silence risk = OPEN.
- Instrumentation change block ready (guard-checked, not applied, not commit) + CTO re-run readout map.
- HALT: awaiting CTO -> apply instrumentation (after critic R44) -> board re-run -> read g_m1_softcfg_rc[5].
