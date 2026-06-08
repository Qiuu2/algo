# M1 HW-Confirm 1B: RX single-slot -- hardware-layer ruling + CTO board-grep recipe (HALT)

> dsp-algorithm teammate, 2026-06-08. Follows M1_HWCONFIRM1_RX_SINGLE_SLOT.md (which left it (c) board-
> confirm). PM established the driver header body (adi_sport.h w/ SelectChannel prototype) is NOT local --
> only adi_sport_config_2156x.h (config struct) + .d refs. So: hand-1 = squeeze the HARDWARE manuals
> (MC window is a hw capability independent of the driver wrapper); hand-2 = exact grep recipe for the CTO
> Windows CCES 2.12.1 install tree. ASCII. No commit. No implementation. HALT at the conclusion.
>
> SOURCES: ADSP-21569 SHARC+ Hardware Reference (HRM); the local adi_sport_config_2156x.h (Audio_Loopback_TDM).

================================================================================
## HAND 1 -- HARDWARE-LAYER RULING: 1-slot RX is HARDWARE-LEGAL [HRM]  =>  512B
================================================================================
The SPORT multichannel (MC) window is a HARDWARE feature controlled by SPORT_MCTL + SPORT_CS0..3
registers, fully specified in the HRM independent of the driver wrapper. Findings (all cited):

### F1. WSIZE = (number of channels) - 1, 7-bit, NO floor above WSIZE=0  [HRM]
- "Select the number of channels used in multichannel operation by programming the 7-bit
  SPORT_MCTL_A.WSIZE field. This field must be set to the actual number of channels minus one
  (SPORT_MCTL_A.WSIZE = Number of channels - 1)."  [HRM, "Window Size (WSIZE)", pdftotext l.103403-103406]
- WSIZE is R/W, 7-bit; max window = 128 channels. [HRM register-fields table l.107355; l.103372]
- => the encoding for a **1-channel window is WSIZE = 0** (1 - 1). The HRM states NO reserved/minimum
  value above 0 for WSIZE; the only stated constraints are the 128-channel max and the out-of-range
  window+offset rule (l.103418-103419). So a 1-channel MC window is HARDWARE-LEGAL.
- Local config header corroborates the formula verbatim: "WSIZE = (number of channel slots) -1"
  [adi_sport_config_2156x.h:123-124,219-220 in Audio_Loopback_TDM]. (That file sets WSIZE=15u = a
  16-ch generic SPORT0 config -- NOT the loopback runtime, which uses ConfigMC=7u=8ch; it only proves
  the formula + field, not a minimum.)

### F2. Per-channel enable is a SEPARATE bitmask (SPORT_CS0..CS3): enable exactly 1 channel  [HRM]
- "Each channel can be individually enabled or disabled using the multichannel selection registers
  (SPORT_CS0_A to SPORT_CS3_A) ... Setting any bit within these registers enables the associated
  channel."  [HRM, "Active Channel Selection Registers", l.103372-103377]
- => you can enable EXACTLY ONE channel (set 1 bit) within the window. The window (WSIZE) and the
  per-channel enable (CS regs) are independent: a wider window with a single enabled channel is legal,
  AND a 1-channel window is legal.

### F3. DMA buffer size depends on MCPDE (packing) -- and the BSP uses PACKED  [HRM + config]
- MCPDE=1 (packed): "the SPORT expects the data in the DMA buffer to correspond only with ENABLED
  SPORT channels. For example, if only channels 1 and 9 are enabled in a 10-channel window
  (WSIZE=9), the SPORT expects the buffer to be exactly TWO words in length."  [HRM l.103432-103441]
- MCPDE=0 (unpacked): "the DMA buffer size must be exactly the size of the WINDOW" (one word per
  window channel, enabled or not).  [HRM l.103442-103445]
- The BSP loopback config sets **MCPDE = 1 (packed)**: ADI_SPORT0A/0B_MCTL_MCPDE = 1u.
  [adi_sport_config_2156x.h:129,225]
- => WITH PACKING (the BSP default), the RX DMA buffer = (number of ENABLED channels) words/frame.
  ENABLE 1 channel => 1 word/frame => per ping-pong half = FRAME(64) x 1 x 4B = 256B, x2 = **512B**.
  (Even if a wider window is kept and only slot 0 is CS-enabled, packed mode still yields 1 word/frame.)

### HAND-1 RULING
- **Hardware supports a 1-slot RX capture** two independent ways: (i) WSIZE=0 (1-channel window), or
  (ii) any window with exactly one CS-enabled channel + MCPDE=1 packing. Both give a 1-word/frame DMA
  buffer. => **RX buffer = 512B is HARDWARE-SUPPORTABLE [HRM].**
- This SUPERSEDES the earlier Path-A finding's relevance: yes, the ADAU1979 ADC bus frame is >=2 slots
  (no TDM1, M1_HWCONFIRM1 Path A) -- but the SPORT can keep an 8-channel window matching the ADC frame
  while CS-enabling only slot 0 and packing => 1 word/frame RX buffer. The ADC frame width does NOT
  force a larger RX buffer; the SPORT CS-enable + MCPDE packing decide it. [HRM F2+F3]
- **What hardware does NOT settle (honestly):** whether the DRIVER WRAPPER (adi_sport_SelectChannel /
  adi_sport_ConfigMC) EXPOSES WSIZE=0 / single-CS-bit without an artificial software assert or a
  driver-imposed minimum. The hardware permits it; the wrapper MIGHT reject it. That single residual is
  hand-2's grep. (The hw ruling means: if the wrapper allows it, 512B is correct; if the wrapper floors
  at 2, that is a SOFTWARE limit, not hardware -- and a raw-register fallback could still reach 512B.)

================================================================================
## HAND 2 -- CTO board-machine grep recipe (Windows CCES 2.12.1 install tree)
================================================================================
Run on the install tree. Let CCES = the CCES 2.12.1 root (e.g. C:\Analog Devices\CrossCore Embedded
Studio 2.12.1). The SHARC driver headers live under  <CCES>\SHARC\include\drivers\sport\ .

### G1. SelectChannel prototype + start/end semantics  [decides inclusive-index vs count]
- File: `<CCES>\SHARC\include\drivers\sport\adi_sport.h`
- Command (Git-Bash/grep): `grep -n -A25 "adi_sport_SelectChannel" "<CCES>/SHARC/include/drivers/sport/adi_sport.h"`
  (PowerShell: `Select-String -Path "<CCES>\SHARC\include\drivers\sport\adi_sport.h" -Pattern "adi_sport_SelectChannel" -Context 0,25`)
- Also grab the doc-comment block ABOVE the prototype (the -A25 / Context catches the param docs).
- READ: the 2nd/3rd params -- are they named like `nChannelStart`/`nChannelEnd` (INCLUSIVE INDICES) or
  `nStartChannel`/`nChannelCount` (a COUNT)? ALT uses (0u,3u)=4ch and (0u,11u)=12ch, which is consistent
  with INCLUSIVE start..end (3-0+1=4, 11-0+1=12). Confirm the header doc says inclusive.
- JUDGE: if inclusive indices -> `SelectChannel(h, 0u, 0u)` selects exactly slot 0 = 1 channel.
         if it is a count -> the single-slot call is `count = 1`.

### G2. Single-slot accepted? (driver assert / minimum)  [decides 512B vs 1024B]
- Same file. Command: `grep -n -B2 -A40 "adi_sport_SelectChannel" "<CCES>/SHARC/include/drivers/sport/adi_sport.h"`
  AND the IMPL if present: `grep -rn "adi_sport_SelectChannel" "<CCES>/SHARC/..."` (look for a .c/.c-like
  body or an inline body; ADI ships sources for some drivers under <CCES>\SHARC\lib\src\drivers\sport\).
- READ: any `assert`, `if (... < 2) return ADI_SPORT_FAILED`, `ADI_SPORT_ERR_*`, or a documented
  "minimum 2 channels" / "window must be >= N". Also check `adi_sport_ConfigMC` for a WSIZE>=1 guard.
- JUDGE: no minimum/assert against 1 -> single slot ACCEPTED.
         a >=2 guard -> driver floors at 2 (software limit; hw still allows 1, see hand-1 note).

### G3. ConfigMC window-arg meaning (WSIZE = last-index vs count) + window>=enabled  [confirms 1-CS-in-8-window]
- File: `<CCES>\SHARC\include\drivers\sport\adi_sport.h`
- Command: `grep -n -A20 "adi_sport_ConfigMC" "<CCES>/SHARC/include/drivers/sport/adi_sport.h"`
- READ: the window-size param doc -- does the arg map directly to SPORT_MCTL.WSIZE (= channels-1, so 7u
  => 8 ch, matching ALT) or is it a raw channel count? Confirm MCPDE (packing) default the driver sets
  (search `MCPDE` / `Packing` in the header + config). ALT relies on packed (config MCPDE=1u).
- JUDGE: confirms whether keeping an 8-ch window (matching ADC frame) + SelectChannel single slot +
  packing yields a 1-word/frame buffer (the hand-1 F3 path).

### G4. CCES 2.11.1 -> 2.12.1 signature drift  [confirms ALT call-sites still valid]
- Command: `grep -n "adi_sport_SelectChannel\|adi_sport_ConfigMC\|adi_sport_ConfigData"
  "<CCES>/SHARC/include/drivers/sport/adi_sport.h"`  (compare arg lists to ALT.c:299-319 usage).
- JUDGE: signatures identical to ALT (2.11.1) -> no porting; differ -> note the delta before M1 impl.

### Grep-result -> RX buffer decision map
| grep outcome | RX captured slots | RX buffer | note |
|---|---|---|---|
| G1 inclusive + G2 no-min (single slot accepted) + G3 packing | 1 | **512B** | LOCK 512B (matches CTO target) |
| G2 driver floors window/select at 2 (software min) | 2 | **1024B** | software limit; hw allows 1 (hand-1) -- raw-reg fallback could reclaim 512B if worth it |
| G3 MCPDE unpacked + window kept at 8 | 8 (buffer=window) | 2048B | only if packing not used -- avoid by keeping MCPDE=1 |

================================================================================
## CONCLUSION (HALT)
================================================================================
- **HAND 1 (hardware): RX 1-slot is HARDWARE-LEGAL [HRM]** -- WSIZE=0 (1-ch window) OR single CS-enabled
  channel + MCPDE=1 packing, both => 1 word/frame => **RX buffer 512B is hardware-supportable.** Cited:
  HRM "Window Size (WSIZE)" (WSIZE=channels-1, 7-bit, no floor>0), "Active Channel Selection Registers"
  (per-bit enable), "MCPDE" (packed buffer = enabled-channel count); BSP config MCPDE=1.
- **Residual is SOFTWARE only**: whether adi_sport_SelectChannel/ConfigMC expose the single-slot case
  without a driver assert/minimum. That is hand-2's 4-item grep (G1-G4) on the install tree -- NOT a
  hardware question.
- **CTO decision path**: per the WO, "if hardware decides single-slot legal -> RX=512B can be pinned now
  (board grep is only a cross-check)". Hardware DID decide single-slot legal. So **512B is pinnable now
  (= HRM does not block it; if the driver wrapper floors at 2, fall back 1024B via one G1-G2 grep, or
  raw-register MCTL/CS to reclaim 512B -- DO NOT quote "512B" without this fallback clause)** [R36 INFO-2],
  with G1-G3 as a confirmatory cross-check that the driver wrapper doesn't impose a software floor (if it
  does -> fall back 1024B, or raw-register the MCTL/CS to keep 512B). Both candidate values + the exact
  grep that disambiguates are above.
- HONEST boundary: the HRM covers the SPORT hardware fully; the DRIVER wrapper's argument validation is
  NOT in any local file (PM-confirmed) => that one sub-question is genuinely board-grep-only (G1-G2).

```
| M1 HW-confirm-1B RX slot (hardware layer) | HARDWARE RULING [HRM]: 1-slot RX is hardware-legal --
  SPORT_MCTL.WSIZE = channels-1 (7-bit, no floor>0; WSIZE=0 = 1-ch window) + per-channel SPORT_CS0..3
  bit-enable + MCPDE=1 packed (BSP config) => DMA buffer = enabled-channel count = 1 word/frame =>
  RX buffer 512B HARDWARE-SUPPORTABLE. ADC >=2-slot bus frame (no TDM1) does NOT enlarge RX buffer
  (packed capture decides it). Residual = SOFTWARE only: adi_sport_SelectChannel/ConfigMC may assert a
  min; not in any local file -> CTO board-grep G1-G4 (recipe filed). 512B pinnable now; 1024B fallback if
  driver floors at 2. HALT for CTO pin. critic gate pending.
```
> HALT: hardware ruling + grep recipe delivered. Awaiting CTO RX-slot pin (512B unless board-grep shows a
> driver software-minimum) before any M1 implementation (separate WO).
