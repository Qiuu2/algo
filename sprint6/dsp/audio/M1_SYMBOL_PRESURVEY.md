# WO-S6-AUDIO M1 symbol pre-survey (dependency-first, MDMA-9-error lesson)

> dsp-algorithm teammate, 2026-06-06. CTO directive #1: survey BEFORE writing. Every symbol traced to
> a local example line, or marked [board-confirm] with a CTO bring-up grep target. ASCII. No commit.
>
> PRIMARY [L1] REFERENCE PROJECT (a real 21569 ADAU1979->SPORT4 TDM->ADAU1962A loopback, exactly M1):
>   knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/
>     src/Audio_Loopback_TDM.c   (= the loopback driver; cited as ALT.c below)
>     src/Audio_Loopback_TDM.h   (= macros; ALT.h)
>     src/ADAU_1962Common.h / ADAU_1979Common.h  (= codec register name macros)
> Include paths resolved from EV-SOMCRR-EZKIT/Debug/src/Audio_Loopback_TDM.d (CCES 2.11.1 SHARC/include;
>   bench is 2.12.1 -- header NAMES are stable across 2.11->2.12, confirm at bring-up).

## A. [L1] -- symbols an actual local example CALLS (direct use, cite file:line)

### A1. SPORT TDM driver -- header `<drivers/sport/adi_sport.h>` (ALT.c:16; .d confirms path)
| symbol | signature as used | proof (ALT.c) |
|---|---|---|
| `adi_sport_Open` | (devnum, ADI_HALF_SPORT_A/B, ADI_SPORT_DIR_TX/RX, ADI_SPORT_MC_MODE, pMem, ADI_SPORT_MEMORY_SIZE, &h) | :292,:295 |
| `adi_sport_ConfigData` | (h, ADI_SPORT_DTYPE_SIGN_FILL, 31, false,false,false) -- 32-bit word | :299,:311 |
| `adi_sport_ConfigClock` | (h, 32, false,false,false) | :301,:313 |
| `adi_sport_ConfigFrameSync` | (h, 31, false,false,false,true,false,false) | :303,:315 |
| `adi_sport_ConfigMC` | (h, 1u, 7u, 0u, true) -- MC window=7+1=8 slots => 8-slot TDM | :305,:317 |
| `adi_sport_SelectChannel` | (h, 0u, 11u) Tx / (h, 0u, 3u) Rx | :307,:319 |
| `adi_sport_RegisterCallback` | (hRx, SPORTCallback, NULL) | :323 |
| `adi_sport_DMATransfer` | (h, &descList, DMA_NUM_DESC, ADI_PDMA_DESCRIPTOR_LIST, ADI_SPORT_CHANNEL_PRIM) | :330,:333 |
| `adi_sport_Enable` | (h, true) | :337,:340 |
| `adi_sport_StopDMATransfer` / `adi_sport_Close` | (h) | :353-:363 |
| types/enums | `ADI_SPORT_HANDLE`, `ADI_SPORT_RESULT`, `ADI_SPORT_MEMORY_SIZE`, `ADI_HALF_SPORT_A/B`, `ADI_SPORT_DIR_TX/RX`, `ADI_SPORT_MC_MODE`, `ADI_SPORT_DTYPE_SIGN_FILL`, `ADI_SPORT_CHANNEL_PRIM`, `ADI_SPORT_EVENT_RX_BUFFER_PROCESSED` | :135-136,:176,:181,:289 |
| SPORT4 instance | `SPORT_DEVICE_4A=4u`, `SPORT_DEVICE_4B=4u` (A half=Tx, B half=Rx) | ALT.h:26-27 |

### A2. PDMA ping-pong descriptors -- header `<services/pdma/adi_pdma_2156x.h>` (.d:path)
| symbol | use | proof |
|---|---|---|
| `ADI_PDMA_DESC_LIST` | struct {pStartAddr, Config, XCount, XModify, YCount, YModify, pNxtDscp} | ALT.c:114-119,:253-283 |
| `ENUM_DMA_CFG_XCNT_INT` | .Config value (interrupt at XCount done) | ALT.c:254 etc |
| `ADI_PDMA_DESCRIPTOR_LIST` | adi_sport_DMATransfer mode arg | ALT.c:330,:333 |
| ping-pong link | desc1.pNxtDscp=&desc2; desc2.pNxtDscp=&desc1 (circular) | ALT.c:259,:267,:275,:283 |

### A3. TWI codec control -- header `<drivers/twi/adi_twi_2156x.h>` (ALT.c:18; .d:path)
| symbol | signature | proof |
|---|---|---|
| `adi_twi_Open` | (TWIDEVNUM=2u, ADI_TWI_MASTER, pMem, ADI_TWI_MEMORY_SIZE, &h) | ALT.c:513 |
| `adi_twi_SetPrescale` / `SetBitRate` / `SetDutyCycle` / `SetHardwareAddress` | (h, val) | ALT.c:520-:539 |
| `adi_twi_Write` / `adi_twi_Read` | (h, buf, n, bRepeatStart) | ALT.c:482,:492,:499 |
| `adi_twi_Close` | (h) | ALT.c:552 |
| types | `ADI_TWI_HANDLE`, `ADI_TWI_RESULT`, `ADI_TWI_MEMORY_SIZE`, `ADI_TWI_MASTER`, `ADI_TWI_SUCCESS` | ALT.c:139,:142,:487 |
| TWI addrs | DAC 0x04 (TARGETADDR_1962), ADC 0x11 (TARGETADDR_1979) | ALT.h:36-37 |

### A4. Codec register init SEQUENCES (full, [L1] -- exact register/value tables)
- ADAU1962A (DAC): PLL init (ALT.c:578-617: PLL_CTL_CTRL0=0x01->0x05, CTRL1=0x22, poll lock bit2)
  + 28-register Config_array_DAC (ALT.c:61-91). Register name macros: ADAU_1962Common.h.
- ADAU1979 (ADC): PLL init (ALT.c:641-669: REG_POWER=0x01, REG_PLL=0x03, poll lock bit7)
  + 16-register Config_array_ADC (ALT.c:93-111; SAI_CTRL0=0x1B = "I2S 48kHz" per ALT.c:98 comment).
  Register name macros: ADAU_1979Common.h.
  NOTE: ALT uses I2S-mode codec regs in a TDM SPORT frame; M1 copies the ALT tables verbatim
  (they are the proven-working loopback values) and flags any 8-slot-TDM-specific codec reg as a
  bring-up check (G-M1-3 below).

### A5. SPU (secure) / SRU (pin routing) / GPIO -- all [L1] in ALT.c
| symbol | use | proof |
|---|---|---|
| `adi_spu_Init`, `adi_spu_EnableMasterSecure`, `ADI_SPU_HANDLE`, `ADI_SPU_MEMORY_SIZE`, `ADI_SPU_SUCCESS` | SPORT4A/B secure masters (SPORT_4A_SPU=57, _4B_SPU=58) | ALT.c:453-476, ALT.h:39-40 |
| `SRU2(...)`, `pREG_PADS0_DAI1_IE` | DAI1 pin routing SPT4_ACLK/BCLK/AFS/BFS/AD0/BD0 | ALT.c:415-441 (header <sru21569.h>) |
| `adi_gpio_SetDirection`, `adi_gpio_Toggle`, `ADI_GPIO_PORT_C`, `ADI_GPIO_SUCCESS` | LED heartbeat | ALT.c:737-script |
| `adi_initComponents` | full board init (clock/power/pinmux/sru gen-code) | ALT.c:688 (also bench_main.c) |
| `ConfigSoftSwitches_ADC_DAC` / `_ADAU_Reset` | board soft-switch (SoftConfig_*.c) | ALT.c:57-59 |

### A6. CCNT cycle probe (for the io-callback cost probe) -- REUSE bench's
- `bench_cyc_target()` -> CCLK cycles (clock() on SHARC = REGF_EMUCLK). bench_main.c:118-122.
  Reused for the callback-cost CCNT bracket. 32-bit, ~4.29s wrap @1GHz; a callback body is <<wrap.

## B. [board-confirm] -- NOT called by any local example; placeholder + CTO grep target

| item | why board-confirm | CTO bring-up grep |
|---|---|---|
| **DMA-buffer cache coherency** | ALT.c does NO flush/invalidate (SPORT buffers are plain L1 globals; SHARC L1 is NOT data-cached for core access -> no coherency op needed when buffers live in L1). M1 keeps buffers in L1 (default) so the CLAUDE.md "DMA read before invalidate" contract is satisfied vacuously. IF a future variant puts buffers in CACHED L2/external, `flush_data_buffer(start,end,inv)` (sys/cache.h, the H1 A5 symbol) is required. | grep `C:\...\SHARC\include\sys\cache.h` for flush_data_buffer; confirm SPORT bufs land in L1 (.map) -> no-op path valid |
| **exact ADI_SPORT_MEMORY_SIZE / ADI_TWI_MEMORY_SIZE / ADI_SPU_MEMORY_SIZE values** | used as array sizes; macro names [L1] but numeric value is in the installed header | confirm macros resolve (they do in ALT.d) -- value irrelevant to source correctness |
| **CCES 2.11->2.12 header-name drift** | ALT.d is 2.11.1; bench build is 2.12.1 | grep installed 2.12.1 SHARC/include for adi_sport.h / adi_pdma_2156x.h / adi_twi_2156x.h (names expected identical) |
| **8-slot TDM codec-register exactness** | ALT codec tables proven for ITS loopback; our 8-slot mapping to 8 amps (DOC-S4-IO-01) may need DAC channel-map regs | bring-up: verify ADAU1962 DAC_CTRL/channel routing for 8-of-12 used |

## C. Cache-coherency ruling (CLAUDE.md IO1 contract: "DMA output read before cache invalidate")
SHARC+ 21569: L1 RAM is NOT cached for the core's own load/store (the DM/PM caches sit on Block1/Block2
for EXTERNAL/L2 traffic only -- app.ldf:147-157 "DM cache ... caches all the external memory access").
=> SPORT DMA buffers placed in L1 (the ALT default, and M1's choice) need NO core-side invalidate/flush;
the contract is met by PLACEMENT. M1 documents this and provides a compile-time hook so that IF buffers
are moved to cached memory, flush_data_buffer is wired (board-confirm). The ALT example's lack of any
flush is consistent with this ruling (it works precisely because buffers are L1).

## D. Buffer placement (R26 lesson -- validity/perf gate)
ALT.c declares SPORT buffers (int_SP0ABuffer1/2/4/5) as plain file-scope globals -> default-placed by the
.ldf into L1 Block 0 data sections (mem_block0_bw). M1 does the same by default (L1, uncached, lowest-
latency, coherency-free). A `#pragma section("seg_l1_block1")` option is provided (commented) to move RX/TX
buffers to L1 Block 1 if bring-up's .map shows Block-0 pressure -- same proven pragma/section as the R24
fix. Bring-up reads the .map and confirms buffer block (the F24/R26 placement-verify discipline carries).
