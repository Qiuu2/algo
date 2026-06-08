# M1 SRU audio-routing survey (independent-project step 1; HALT at the routing table)

> dsp-algorithm teammate, 2026-06-08. M1 = independent project (route B). Step 1: nail the SRU audio
> routing BEFORE writing any project/implementation. SRU mis-route = signal never reaches the codec =>
> SILENT no-sound with NO compile error (ADI's classic foot-gun). ASCII. No commit. No project, no impl.
>
> SOURCES (every row cited): ALT = Audio_Loopback_TDM.c (real 21569 loopback); SoftCfg =
>   SoftConfig_EV_SOMCRR_EZKIT_ADC_DAC.c / _ADAU_Reset.c ; HRM = ADSP-21569 SHARC+ Hardware Reference
>   (SRU/DAI chapter 22, DAI chapter 12); sru21569.h = the SRU2 macro definitions (local copy).
> [R39 F39-MINOR-1] sru21569.h copy used = the one under EE408V02/Pipelined/src/ (FIRA app-notes);
>   SRU2 tokens are chip-level (21569 generic) so it is same-source as ALT's, but the EXACT macro names
>   must be confirmed against the installed 2.12.1 sru21569.h at bring-up (already a board-confirm item).
> D5 discipline: SRU macros + SoftConfig values decoded per HRM/datasheet, NOT blind-copied. ALT-vs-comment
>   and ALT-vs-runtime mismatches flagged explicitly (today's 0x1B/0x0A lesson applied to routing).

================================================================================
## 0. SRU model (HRM ch.22) -- how to read the table
================================================================================
- The SRU connects DAI peripheral I/O to each other and to external DAI pins (HRM l.3162-3165).
- Macro form: `SRU2(<source>_O, <dest>_I)` routes source-OUTPUT -> dest-INPUT. SRU2 = DAI1's SRU. [HRM ch.22]
- Connection-point GROUPS (HRM TOC l.1094-1098): A=Clock routing, B=Serial-Data source, C=Frame-Sync
  source, D=Pin-Signal-Assignment, F=Pin-Output-Enable. (Verified: SPT4_BD0_I is in GROUP_B2 =
  serial-data, sru21569.h:628 -- so the data macros are real serial-data routes, not clock.)
- `DAI1_PBENxx_I` = per-pin OUTPUT-ENABLE (drive the physical pin out=HIGH, or make it an input=LOW).
- `*pREG_PADS0_DAI1_IE = 0x1ffffe` = DAI1 Port Input-Enable (pins 1..20 input buffers on; bit0 reserved).
  [ALT.c:418; HRM "DAI1 Port Input Enable Control Register" l.525/35654]
- All ALT SRU2 macros used below EXIST in sru21569.h (45/45 of the ALT-used tokens resolve, local grep).

================================================================================
## 1. SRU SIGNAL ROUTING TABLE  (SPORT4 <-> DAI1 pins <-> ADAU codecs)
================================================================================
Clock direction (THE silent-no-sound risk): the **DAC (ADAU1962A) is the bus MASTER** (DAC_CTRL1
SAI_MS=1, M1 .c) and SOURCES BCLK + FS onto DAI1_PB05 / DAI1_PB04. SPORT4A, SPORT4B AND the ADC are all
SLAVES that RECEIVE those clocks. The SRU fans the master clocks to all three sinks.

| # | signal | SRU2 route (source_O -> dest_I) | group | DAI1 pin | connects | dir | source |
|---|--------|--------------------------------|-------|----------|----------|-----|--------|
| C1 | BCLK -> SPORT4A | SRU2(DAI1_PB05_O, SPT4_ACLK_I) | A clk | PB05 | DAC BCLK pin -> SPORT4A clk | DAC drives, SPT4A recv | ALT.c:422 |
| C2 | BCLK -> SPORT4B | SRU2(DAI1_PB05_O, SPT4_BCLK_I) | A clk | PB05 | DAC BCLK -> SPORT4B clk | DAC->SPT4B recv | ALT.c:423 |
| C3 | BCLK -> ADC | SRU2(DAI1_PB05_O, DAI1_PB12_I) | D pin | PB05->PB12 | DAC BCLK -> ADC BCLK pin | DAC->ADC recv | ALT.c:432 |
| F1 | FS -> SPORT4A | SRU2(DAI1_PB04_O, SPT4_AFS_I) | C fs | PB04 | DAC FS -> SPORT4A FS | DAC->SPT4A recv | ALT.c:425 |
| F2 | FS -> SPORT4B | SRU2(DAI1_PB04_O, SPT4_BFS_I) | C fs | PB04 | DAC FS -> SPORT4B FS | DAC->SPT4B recv | ALT.c:426 |
| F3 | FS -> ADC | SRU2(DAI1_PB04_O, DAI1_PB20_I) | D pin | PB04->PB20 | DAC FS -> ADC FS pin | DAC->ADC recv | ALT.c:435 |
| D1 | TX data SPORT4A -> DAC | SRU2(SPT4_AD0_O, DAI1_PB02_I) | B data | PB02 | SPORT4A SDATA-out -> DAC SDATA-in | SPT4A drives DAC | ALT.c:429 |
| D2 | RX data ADC -> SPORT4B | SRU2(DAI1_PB06_O, SPT4_BD0_I) | B data | PB06 | ADC SDATA-out (PB06) -> SPORT4B SDATA-in | ADC drives SPT4B | ALT.c:438 |

Pin output-enables (who physically DRIVES each DAI pin):
| pin | PBEN setting | meaning | source |
|-----|--------------|---------|--------|
| PB05 (BCLK) | SRU2(LOW, DAI1_PBEN05_I) | PB05 = INPUT (DAC drives BCLK in from outside; chip receives) | ALT.c:420 |
| PB04 (FS) | SRU2(LOW, DAI1_PBEN04_I) | PB04 = INPUT (DAC drives FS in) | ALT.c:427 |
| PB02 (TX data) | SRU2(HIGH, DAI1_PBEN02_I) | PB02 = OUTPUT (chip drives SDATA out to DAC) | ALT.c:430 |
| PB12 (BCLK->ADC) | SRU2(HIGH, DAI1_PBEN12_I) | PB12 = OUTPUT (chip re-drives BCLK out to ADC) | ALT.c:433 |
| PB20 (FS->ADC) | SRU2(HIGH, DAI1_PBEN20_I) | PB20 = OUTPUT (chip re-drives FS out to ADC) | ALT.c:436 |
| PB06 (RX data) | SRU2(LOW, DAI1_PBEN06_I) | PB06 = INPUT (ADC drives SDATA in) | ALT.c:439 |

### Clock-fan chain (the "DAC clock -> SRU -> SPORT + ADC" link the WO asked to make visible):
```
  DAC (master) --BCLK--> DAI1_PB05 (input) --SRU GroupA--> SPT4_ACLK + SPT4_BCLK  (SPORT4A/4B slaved)
                                            --SRU GroupD--> DAI1_PB12 (output) --> ADC BCLK (ADC slaved)
  DAC (master) --FS----> DAI1_PB04 (input) --SRU GroupC--> SPT4_AFS + SPT4_BFS    (SPORT4A/4B slaved)
                                            --SRU GroupD--> DAI1_PB20 (output) --> ADC FS   (ADC slaved)
  audio data:  SPORT4A --SDATA--> PB02 --> DAC (TX, 8 slots)
               ADC --SDATA--> PB06 --> SPORT4B (RX, slot0 captured)
```
=> ONE shared 256-BCLK/48kHz/12.288MHz TDM8 frame, DAC-sourced, all others slaved. This is exactly the
   shared-bus topology M1 codec config assumes (DAC master, ADC+SPORT slave). Clock direction CONSISTENT.

================================================================================
## 2. SoftConfig (carrier codec-enable) ENABLE LIST  [SoftCfg, D5-decoded]
================================================================================
The SOMCRR/EZKIT carrier gates the codecs behind a U6 I/O-expander (TWI dev 2, HW addr **0x22**)
[SoftConfig_*.c:107-108]. Two register-pairs are written (MCP23017-class I/O expander):

ConfigSoftSwitches_ADC_DAC (the "enable codecs" half) [SoftConfig_ADC_DAC.c:94,100-101]:
| reg | value | D5 decode (U6 Port A bit map, SoftCfg.c:80-92) | effect |
|-----|-------|------------------------------------------------|--------|
| 0x12 (Port A out) | 0x05 | b7 ~ADAU1979_EN=0, b6 ~ADAU1962_EN=0, b5 ADAU_RESET=0, b2 ~MicroSD=1, b0 EEPROM_EN=1 | **ADC ENABLED + DAC ENABLED** (active-low ~EN=0), reset de-asserted |
| 0x13 (Port B out) | 0xFD | b3 AUDIO_JACK_SEL=1 (+ eth/spdif/mlb unrelated) | audio jack select |
| [R39 F39-MINOR-2] note | -- | AUDIO_JACK_SEL may pick the analog INPUT source (jack vs on-board) -- relevant to G-IO2 "1ch source connection 待定"; M1 inherits ALT's 0xFD, but board-confirm this bit when the 1-mono input pin (G-IO2) is decided | board-confirm w/ G-IO2 |
| 0x00 (IODIRA) | 0x18 | b7,6,5 = outputs (drive EN/RESET lines), b4,3 = inputs | direction: EN/RESET pins driven |
| 0x01 (IODIRB) | 0x00 | all Port B = outputs | direction |

ConfigSoftSwitches_ADAU_Reset (the "pulse reset" half) [SoftConfig_ADAU_Reset.c:94]:
| reg | value | D5 decode | effect |
|-----|-------|-----------|--------|
| 0x12 (Port A) | 0x25 | b7 ~ADAU1979_EN=0, b6 ~ADAU1962_EN=0, **b5 ADAU_RESET=1** | codecs enabled, RESET ASSERTED (toggle for a clean reset) |

=> Enable list to make the ADC->SPORT4B / SPORT4A->DAC path physically live on the carrier:
   (1) U6 @ TWI2 0x22, Port A = 0x05  -> ~ADAU1979_EN=0 (ADC on) + ~ADAU1962_EN=0 (DAC on), reset clear.
   (2) IODIRA = 0x18 so those EN/RESET bits are driven outputs.
   (3) Reset toggle: Port A = 0x25 (assert) then back to 0x05 (deassert) for a clean codec reset.
   Without these the carrier leaves the codecs DISABLED (active-low ~EN high) -> silent no-sound.

================================================================================
## 3. NOT-BLIND-COPY FINDINGS (ALT-vs-comment / ALT-vs-runtime mismatches)
================================================================================
- **F-SRU-1 [CRITICAL, ALT-vs-runtime]: ALT does NOT call Switch_Configurator() at runtime.** ALT.c:701
  is `//Switch_Configurator();` -- COMMENTED OUT. So ALT writes NEITHER 0x05 NOR 0x25 at runtime; it relies
  on the carrier's power-on/CPLD DEFAULT codec-enable state. M1 must NOT assume the codecs are auto-enabled:
  either (a) run ConfigSoftSwitches_ADC_DAC()+_ADAU_Reset() explicitly in M1 init, or (b) confirm the
  SOMCRR carrier default already enables them. This is the #1 silent-no-sound trap and is a board-confirm.
  [ALT.c:701; the SoftConfig functions exist (SoftConfig_*.c) but are dead-code in ALT's main.]
- **F-SRU-2 [naming, harmless]: ALT comments label PB05/PB04 routes "DAC clock"/"DAC FS".** Verified
  consistent: PB05=BCLK source, PB04=FS source, both DAC-master-driven. The comment matches the route.
- **F-SRU-3 [data-direction verified]: RX uses SPT4_BD0_I (B-half data IN), TX uses SPT4_AD0_O (A-half
  data OUT).** Confirmed by sru21569.h: SPT4_BD0_I is GROUP_B2 serial-data, REG_DAI1_DAT0 (sru21569.h:628,
  716). So 4A=TX-out / 4B=RX-in is correct -- swapping these = silent (TX would listen, RX would talk).
- **F-SRU-4 [board-confirm]: the PHYSICAL DAI1-pin -> codec-pin wiring (PB02->DAC SDIN, PB06<-ADC SDOUT,
  PB12->ADC BCLK, PB20->ADC FS) is a SOMCRR-carrier SCHEMATIC fact**, not in any local source (pinmux_config.c
  has no DAI1/codec rows -- DAI routing is SRU-only). The SRU routes are L1; the off-chip pin-to-codec
  traces need the carrier schematic. [board-confirm]

================================================================================
## 4. board-confirm checklist (for CTO)
================================================================================
| item | why | confirm how |
|------|-----|-------------|
| F-SRU-1 codec auto-enable | ALT's Switch_Configurator is commented out; M1 must not assume on | run ConfigSoftSwitches explicitly in M1, OR scope U6 @ TWI2/0x22 default; board scope/CPLD doc |
| F-SRU-4 DAI1 pin->codec traces | off-chip wiring not in source | SOMCRR/EZKIT carrier schematic (PB02/06/12/20/04/05 -> ADAU pins) |
| MCLK source | the 12.288MHz master clock origin (XTAL on DAC? external?) -- not in the SRU routes above | datasheet has 3 options (M1_FACT_BASE sec 3.4); board schematic decides which |
| SRU effect latency | HRM "Signal Routing Unit Effect Latency" 22-22 -- settle time after SRU writes | HRM ch.22; ALT just proceeds, likely fine; note for bring-up |
| 2.11.1 vs 2.12.1 sru21569.h macro names | ALT is 2.11.1; bench/M1 build 2.12.1 | grep installed sru21569.h for the macros in the table |

================================================================================
## SUMMARY (HALT)
================================================================================
- **Routing table = section 1** (8 signal routes + 6 pin-enables, each ALT.c-line-cited; SRU group +
  DAI pin + direction). **Clock direction: DAC master sources BCLK(PB05)/FS(PB04); SRU fans to SPORT4A,
  SPORT4B and (re-driven out PB12/PB20) the ADC -- all slaves.** Data: SPORT4A->PB02->DAC (TX),
  ADC->PB06->SPORT4B (RX). Consistent with the M1 codec config (DAC master / ADC+SPORT slave).
- **SoftConfig enable = section 2**: U6 @ TWI2 addr 0x22, Port A=0x05 enables both codecs (active-low),
  IODIRA=0x18, reset toggle via 0x25. Decoded per the SoftCfg bit-map.
- **NOT-blind-copy headline (F-SRU-1)**: ALT's Switch_Configurator() is COMMENTED OUT -> ALT relies on the
  carrier default to enable codecs; M1 must explicitly enable or board-confirm the default, else silent.
- **board-confirm**: codec auto-enable (F-SRU-1), DAI1-pin->codec traces (F-SRU-4), MCLK source, SRU
  latency, CCES version macro drift.
- HALT: routing table delivered for CTO review. No project built, no implementation, no impl WO.
