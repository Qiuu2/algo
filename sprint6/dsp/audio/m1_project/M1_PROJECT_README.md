# M1 independent audio project (WO-S6-AUDIO-M1-PROJ) -- build manifest + bring-up

> dsp-algorithm teammate, 2026-06-08. Route B: a THIN standalone CCES project for the M1 passthrough
> loopback ONLY. Contains NO FIRA / compute-line code -> M1 audio bring-up cannot perturb the frozen
> compute golden environment (the core value of route B). ASCII. No commit (PM lands after critic R40).

## File manifest (all NEW, all under sprint6/dsp/audio/ -- frozen bench untouched)
| file | role | lines |
|---|---|---|
| `m1_project/system/startup_ldf/m1_app.ldf` | NEW project .ldf (no-FIRA audio template; buffers default L1 Block 0 = opening 4 no-pin) | ~1340 |
| `m1_project/src/m1_main.c` | thin main: init -> SRU -> codec-enable -> loopback -> idle free-run | ~70 |
| `m1_project/src/m1_sru.c` | SRU audio routing glue (R39 table) | ~60 |
| `m1_project/src/m1_softconfig.c` | EXPLICIT carrier codec-enable (F-SRU-1; U6 @ TWI2 0x22) | ~95 |
| `m1_project/src/m1_cyc.c` | bench_cyc_target() CCNT shim (project doesn't link bench_main) | ~25 |
| `../m1_loopback_tdm.c` + `.h` | the codec/SPORT loopback module (R37-passed; in the project source list) | 408+52 |
| `m1_project/run_guard_check.sh` | guard-stub covering all 5 board-guarded TUs | ~45 |

## Build source list (CCES project)
src: m1_main.c, m1_sru.c, m1_softconfig.c, m1_cyc.c, ../m1_loopback_tdm.c.
LDF: m1_project/system/startup_ldf/m1_app.ldf.
Macros (board build): define `M1_TARGET_BOARD` + `TARGET_SHARC`.
Includes (install tree, CCES 2.12.1): <drivers/sport/adi_sport.h>, <services/pdma/adi_pdma_2156x.h>,
  <drivers/twi/adi_twi_2156x.h>, <services/spu/adi_spu.h>, <services/pwr/adi_pwr.h>, <sru21569.h>,
  <cdef21569.h>, <sys/platform.h>, adi_initialize.h, ADAU_1962Common.h, ADAU_1979Common.h.
  (M1_FACT_BASE sec 5 / M1_SRU_ROUTING_SURVEY list the [L1] provenance; A2 board-confirm = verify
   the exact header NAMES in the 2.12.1 install tree.)

## Key implementation points
1. **Power-up order** (m1_main.c): adi_initComponents -> adi_pwr_Init(0,25MHz) [F7-FIX startup] -> SRU
   -> EXPLICIT codec enable -> m1_loopback_init -> idle. m1_loopback_init programs the DAC (master)
   codec regs BEFORE enabling the SPORT halves, so the master BCLK/FS are stable first.
2. **F-SRU-1 explicit codec enable** (m1_softconfig.c, CTO ruling): writes U6 @ TWI2 addr 0x22 --
   IODIRA=0x18 (drive EN/RESET) -> Port A=0x25 (reset assert, both codecs enabled active-low) ->
   Port A=0x05 (reset deassert) -> Port B=0xFD. M1 does NOT gamble on carrier default (ALT's
   Switch_Configurator was COMMENTED OUT = silent-no-sound trap). All values R39-D5-verified.
3. **SRU routing** (m1_sru.c, R39 table): DAC master BCLK(PB05)/FS(PB04) -> SPORT4A/4B + re-driven
   out (PB12/PB20) -> ADC; data SPORT4A->PB02->DAC (TX), ADC->PB06->SPORT4B (RX). PBEN dirs:
   PB05/04/06=input(LOW), PB02/12/20=output(HIGH). Reversing any = silent.
4. **opening 4 no-pin**: buffers are plain globals -> .ldf default L1 Block 0. No FIRA working set in
   this build -> no Block-0 self-conflict (the R24/R26 concern is moot for M1; it returns at M2).

## guard-stub coverage
run_guard_check.sh compiles the board-guarded region of all 5 TUs with -fsyntax-only + mock BSP +
-Werror promotions (implicit-func-decl / int-conversion / incompatible-pointer-types). Falsifier
proven both ways: GOOD = all PASS; a BSP-symbol typo AND an SRU-token typo both hard-FAIL (the SRU-token
case is exactly the silent-no-sound route-name class). The SRU stub CANNOT validate route LEGALITY
(board-confirm) -- only that the TU parses and tokens are spelled right.

## Honest gaps (board-only; M1 not blocked)
- DAI1-pin -> codec physical traces (SOMCRR carrier schematic) [F-SRU-4].
- MCLK 12.288 MHz source (XTAL-on-DAC vs external) -- board schematic.
- SRU effect latency (HRM 22-22) -- settle after SRU writes; ALT proceeds directly.
- SelectChannel single-slot driver software-minimum (grep G1-G2) -> M1_RX_SLOTS 1 (512B) or 2 (1024B).
- CCES 2.11.1 (ALT) -> 2.12.1 header-name / SRU-macro drift (A2) -- verify install-tree names.
- SoftConfig SoftSwitch register model assumes MCP23017-class U6 (IODIRA/GPIOA at 0x00/0x12) per the
  ALT SoftConfig file; confirm the carrier U6 part if the writes don't take.

## CTO on-board action list
1. **board-confirm-CRITICAL grep (A2/F5)**: in the 2.12.1 install tree, confirm header names
   (adi_sport.h vs adi_sport_2156x.h, etc.) + SRU macro names in sru21569.h.
2. **grep G1-G2** (`adi_sport_SelectChannel` in install adi_sport.h): single-slot select accepted?
   -> keep M1_RX_SLOTS=1 (512B) or bump to 2 (1024B).
3. **Burn + read at idle** (free-run, no callback breakpoints): g_m1_main_pwrinit_rc / softcfg_rc /
   init_rc all 0; g_m1_valid=1; g_m1_fg_stream_live=1 (green ONLY if blocks grew AND non-zero audio);
   g_m1_rx_block_count/tx growing; g_m1_cb_cyc_last/max/min (io-callback [L1] cost); g_m1_max_abs_sample
   (>0 = live input). Run twice, main numbers <0.1% (F3). Any FG not green -> isolate, do not rescue (F4).
