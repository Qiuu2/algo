# WO-S6-AUDIO M1 survey -- codec/SPORT/TDM research + symbol pre-survey (research-only)

> dsp-algorithm teammate, 2026-06-06. CTO scope (revised): RESEARCH + symbol pre-survey ONLY; M1
> implementation HELD pending CTO architecture. ASCII. No commit. No new implementation code in this round.
> Absorbs M1_SYMBOL_PRESURVEY.md. This is INPUT to the CTO architecture design (data flow / buffer /
> frame timing / M2 interface).
>
> IMPLEMENTATION-DRAFT DISCLOSURE (scope changed mid-task, not a deviation): before the scope narrowed I
> had already written a draft implementation -- m1_loopback_tdm.c / .h + guard_stub_inc/* (5 stub headers)
> under sprint6/dsp/audio/. Per CTO: left on disk, NOT extended, NOT deleted, NOT guard-checked. They are
> a draft only; the authoritative deliverable is THIS survey. (The sprint6/dsp/eq/* files are NOT mine --
> a separate work line; untouched.)
>
> PRIMARY [L1] REFERENCE PROJECT (a real 21569 ADAU1979->SPORT4 TDM->ADAU1962A loopback = exactly M1):
>   knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/  (cited as ALT below)
>     src/Audio_Loopback_TDM.c (ALT.c) / .h (ALT.h) / ADAU_1962Common.h / ADAU_1979Common.h
> DATASHEETS (present locally, cited by line of pdftotext extract; [R31 F31-MINOR-2] extract-line
> numbers can drift with tool version -- table/section anchors (e.g. "adau1979 Table 10") are the
> stable references; line numbers are convenience only):
>   knowledge_base/ezkit/bsp/datasheets/adau1979.pdf  (ADC)   knowledge_base/ezkit/bsp/datasheets/ADAU1962A.pdf (DAC)
> Include paths resolved from ALT Debug/.../Audio_Loopback_TDM.d (CCES 2.11.1 SHARC/include).

================================================================================
## (1) CODEC REGISTER INIT SEQUENCES  (datasheet + ALT register-table cited)
================================================================================

### TWI/I2C device addresses
| codec | 7-bit TWI addr | source |
|---|---|---|
| ADAU1979 (ADC) | 0x11 | ALT.h:37 TARGETADDR_1979; datasheet adau1979.pdf addr set by ADDR0/ADDR1 pins (l.2655-2658) |
| ADAU1962A (DAC) | 0x04 | ALT.h:36 TARGETADDR_1962; datasheet ADAU1962A.pdf addr via ADDR0/ADDR1 pins (l.1451-1463) |
| TWI controller | TWI2 (dev 2u), 100 kHz, prescale 12, duty 50% | ALT.h:28-32 |

### ADAU1979 (ADC) bring-up ORDER -- ALT.c:622-669 + datasheet
Step 0 (PLL, ALT.c:641-669): SetHardwareAddress(0x11) -> REG_POWER(0x00)=0x01 (power up) ->
  REG_PLL(0x01)=0x03 -> poll REG_PLL bit7==1 (PLL lock). Datasheet: PLL accepts frame clock as ref
  (adau1979.pdf l.1821); lock bit is the PLL status.
Step 1 (16-register table, ALT.c:93-111, order as listed):
| # | reg (macro / addr) | val | meaning (datasheet adau1979.pdf) |
|---|---|---|---|
| 1 | REG_BOOST 0x02 | 0x00 | input boost off |
| 2 | REG_MICBIAS 0x03 | 0x00 | mic bias off |
| 3 | REG_BLOCK_POWER_SAI 0x04 | 0x30 | partial block power (staged) |
| 4 | **REG_SAI_CTRL0 0x05** | **0x1B** | **serial-audio fmt + fS; ALT comment "I2S 48kHz"**. SAI field (bits) selects channel count incl TDM (l.2226,2297 "SAI=011=8ch"); SLOT_WIDTH/SDATA_FMT here. ** key TDM-config reg ** |
| 5 | **REG_SAI_CTRL1 0x06** | **0x08** | SLOT_WIDTH / BCLK / LRCLK / SDATA_SEL (bit7) (l.2237). ** key TDM-config reg ** |
| 6 | REG_CMAP12 0x07 | 0x01 | channel-to-slot map ch1/2 |
| 7 | REG_CMAP34 0x08 | 0x23 | channel-to-slot map ch3/4 |
| 8 | REG_SAI_OVERTEMP 0x09 | 0xf0 | overtemp thresholds |
| 9-12 | REG_POST_ADC_GAIN1..4 0x0a-0x0d | 0xA0 each | per-channel post-ADC gain |
| 13 | REG_ADC_CLIP 0x19 | 0x00 | clip status clear |
| 14 | REG_DC_HPF_CAL 0x1a | 0x00 | dc high-pass/cal off |
| 15 | REG_BLOCK_POWER_SAI 0x04 | 0x3f | full block power (final) |
| 16 | REG_MISC_CONTROL 0x0e | 0x00 | misc default |
Each write is read-back-verified in ALT.c:630-635 (write then read, compare).

### ADAU1962A (DAC) bring-up ORDER -- ALT.c:560-617 + datasheet
Step 0 (PLL, ALT.c:578-617): SetHardwareAddress(0x04) -> PLL_CTL_CTRL0(0x00)=0x01 -> =0x05 ->
  PLL_CTL_CTRL1(0x01)=0x22 -> poll PLL_CTL_CTRL1 bit2==1 (PLL lock). Datasheet: after PU/RST high the
  PLL_CLK_CTRLx are written; 256xfS @48k = 12.288 MHz master clock (ADAU1962A.pdf l.2464-2481).
Step 1 (28-register table, ALT.c:61-91, order as listed): PDN_CTRL_1/2/3 (staged power) -> DAC_CTRL0=0x01
  / DAC_CTRL1=0x01 / DAC_CTRL2=0x00 (** DAC_CTRL0[2:1] = sample-rate/mode, TDM, l.2356 **) -> DAC_MUTE1/2=0
  -> MSTR_VOL=0 + DAC1..12_VOL=0 (0 = 0 dB / unattenuated) -> PAD_STRGTH=0 -> DAC_PWR1/2/3=0xaa -> re-write
  PDN_CTRL_2/3=0x00 -> **DAC_CTRL0=0x18 (final enable)**. Read-back-verified ALT.c:567-572.
> M1 NOTE: ALT codec tables are the PROVEN-working loopback values; M1 should reuse verbatim. The 8-slot-
> TDM channel-map (CMAP / DAC slot routing for 8-of-12 DAC ch -> 8 amps) is the one spot to re-verify
> against datasheet TDM slot assignment at bring-up (G-M1-3 below). datasheet register maps: adau1979.pdf
> Register 0x05-0x08 = TDM programmability (l.2226); ADAU1962A.pdf DAC_CTRL0/SAI for slot/format.

================================================================================
## (2) TDM SLOT CONFIG  (our 8slot x 32bit @48k  vs  ALT actual)
================================================================================
Our locked baseline (DOC-S4-IO-01): 8 slot x 32 bit @ 48 kHz -> BCLK = 8x32x48k = 12.288 MHz.
Datasheet CONFIRMS this exact point: adau1979.pdf Table 10 "TDM8, 32 bit/slot = 256 x fS" = 256x48k =
  **12.288 MHz** (l.2449-2474); ADAU1962A.pdf "256 x fS @48k = 12.288 MHz" (l.294, l.2474-2481). So our
  8x32@48k caliber is the codecs' native TDM8 / 256xfS mode -- no contradiction.

| param | our baseline | ALT actual | same? / diff |
|---|---|---|---|
| slots | 8 | ConfigMC count arg = 7 -> window 8 slots (ALT.c:305,:317) | SAME (8) |
| slot width | 32 bit | ConfigData word=31 (=>32-bit), ConfigClock=32 (ALT.c:299-301) | SAME (32-bit) |
| fS | 48 kHz | ADC SAI_CTRL0=0x1B "I2S 48kHz" (ALT.c:98) | SAME (48k) |
| BCLK | 12.288 MHz | derived 8x32x48k = 256xfS (datasheet Table 10) | SAME |
| data fmt | TDM | ALT codec regs set "I2S 48kHz" string but SPORT runs MC(TDM) mode | **DIFF to verify**: ALT mixes an I2S-named codec reg value with SPORT MC/TDM framing; the loopback works, but our 8-amp mapping needs the codec SAI field = TDM8 (SAI=011) confirmed (adau1979.pdf l.2297). G-M1-1. |
| channel map | 8 ch -> 8 amps (DOC-S4-IO-01) | ALT CMAP12=0x01/CMAP34=0x23 (4 ADC ch) | **DIFF**: ALT maps 4 ADC ch; we have 1 src ch fanned to 8 TX slots (M2 beamformer output). Slot/CMAP mapping = architecture decision. G-M1-2. |
> Net: slot count / width / fS / BCLK all MATCH ALT [L1]. The two diffs are (a) codec SAI field TDM-vs-I2S
> naming and (b) channel-to-slot mapping for our 1-in / 8-out topology -- both are codec-register choices
> for the CTO architecture to pin, not blockers.

================================================================================
## (3) SPORT CONFIG  (SPORT4 instance / TDM params / DMA bind / ping-pong buffer placement)
================================================================================
### SPORT instance + half (ALT.c:292-295, ALT.h:26-27)
- SPORT **device 4**; **4A half = Tx (to DAC)**, **4B half = Rx (from ADC)**. ADI_HALF_SPORT_A/B,
  ADI_SPORT_DIR_TX/RX, ADI_SPORT_MC_MODE (multichannel = TDM).
### TDM framing config (ALT.c:298-320, applied to both 4A and 4B identically)
- adi_sport_ConfigData(h, ADI_SPORT_DTYPE_SIGN_FILL, 31, false,false,false)  -- 32-bit word, sign-fill
- adi_sport_ConfigClock(h, 32, false,false,false)                            -- 32 BCLK/slot
- adi_sport_ConfigFrameSync(h, 31, false,false,false,true,false,false)       -- FS config
- adi_sport_ConfigMC(h, 1u, 7u, 0u, true)   -- MC: window-size arg 7 => 8 slots; MFD=1; offset 0; enable
- adi_sport_SelectChannel(h, 0u, 11u) Tx / (h, 0u, 3u) Rx  -- active slot range (ALT uses 0..11 Tx for
  12-ch DAC, 0..3 Rx for 4-ch ADC). ** our 8-slot => SelectChannel 0..7 (architecture). G-M1-2. **
### DMA bind = SPORT-PDMA descriptor list, ping-pong (decls ALT.c:113-119; circular LINKING :259-283; xfer :330-333) [R31 F31-MINOR-1 anchor fix]
- type ADI_PDMA_DESC_LIST {pStartAddr, Config(=ENUM_DMA_CFG_XCNT_INT), XCount, XModify(=4 bytes), YCount=0,
  YModify=0, pNxtDscp}. Two descriptors per direction, **circular** (desc1.pNxtDscp=&desc2, desc2->&desc1).
- adi_sport_DMATransfer(h, &desc1, DMA_NUM_DESC=2, ADI_PDMA_DESCRIPTOR_LIST, ADI_SPORT_CHANNEL_PRIM).
- callback on **ADI_SPORT_EVENT_RX_BUFFER_PROCESSED** (RX half done) -> copy ADC->DAC buffer (ALT.c:181).
### Ping-pong BUFFER allocation + PLACEMENT (R26 validity/perf gate)
- ALT declares buffers as **plain file-scope globals** int_SP0ABuffer1/2 (TX, COUNT*2) + int_SP0ABuffer4/5
  (RX, COUNT) (ALT.c:40-43). **NO #pragma section** (grep: 0 hits) -> linker default placement.
- The loopback app.ldf routes uninit/zero-init data into **mem_block0_bw = L1 Block 0** via
  seg_dmda/seg_bsz/seg_noinit output sections (loopback .ldf:245-340 all "> mem_block0_bw").
  -> SPORT buffers land in **L1 Block 0** by default.
- COHERENCY consequence: L1 is NOT data-cached for the core (DM/PM caches serve external/L2 only,
  app.ldf:147-157) -> ALT does NO flush/invalidate, correctly. The CLAUDE.md IO1 contract ("DMA read
  before invalidate") is satisfied by PLACEMENT (buffers in uncached L1).
- R26 NOTE for architecture: if the M2 beamformer working set + SPORT buffers co-reside in L1 Block 0
  (the H2/R24 self-conflict lesson), bring-up should pin SPORT buffers to L1 Block 1 via
  #pragma section("seg_l1_block1") (the proven R24 fix) and re-read .map. = architecture buffer-map input.

================================================================================
## (4) SYMBOL PATH TABLE
================================================================================
### [L1] -- CALLED by ALT (header path from ALT.d; cite ALT.c line)
| symbol | header | ALT.c line |
|---|---|---|
| adi_sport_Open / ConfigData / ConfigClock / ConfigFrameSync / ConfigMC / SelectChannel | <drivers/sport/adi_sport.h> | :292-320 |
| adi_sport_RegisterCallback / DMATransfer / Enable / StopDMATransfer / Close | same | :323-363 |
| ADI_SPORT_HANDLE/RESULT/MEMORY_SIZE, ADI_HALF_SPORT_A/B, ADI_SPORT_DIR_TX/RX, ADI_SPORT_MC_MODE, ADI_SPORT_DTYPE_SIGN_FILL, ADI_SPORT_CHANNEL_PRIM, ADI_SPORT_EVENT_RX_BUFFER_PROCESSED | same | :135-136,176,181,289 |
| ADI_PDMA_DESC_LIST, ENUM_DMA_CFG_XCNT_INT, ADI_PDMA_DESCRIPTOR_LIST | <services/pdma/adi_pdma_2156x.h> | :114-119,254,330 |
| adi_twi_Open / SetPrescale / SetBitRate / SetDutyCycle / SetHardwareAddress / Write / Read / Close | <drivers/twi/adi_twi_2156x.h> | :482-552 |
| ADI_TWI_HANDLE/RESULT/MEMORY_SIZE, ADI_TWI_MASTER, ADI_TWI_SUCCESS | same | :139,142,487 |
| adi_spu_Init / EnableMasterSecure, ADI_SPU_HANDLE/RESULT/MEMORY_SIZE, ADI_SPU_SUCCESS | <services/spu/adi_spu.h> | :453-476 |
| adi_gpio_SetDirection / Toggle, ADI_GPIO_PORT_C, ADI_GPIO_SUCCESS | <services/gpio/adi_gpio.h> | :737+ |
| SRU2(...), pREG_PADS0_DAI1_IE | <sru21569.h> | :415-441 |
| adi_initComponents | adi_initialize.h | :688 |
| ConfigSoftSwitches_ADC_DAC / _ADAU_Reset | board SoftConfig_*.c (extern) | :57-59 |
| ADAU1979_REG_* / ADAU1962_* register macros | ADAU_1979Common.h / ADAU_1962Common.h | tables :61-111 |
| bench_cyc_target() (CCNT for io-probe, REUSE) | bench_main.c:118 [L1] | n/a (our bench) |

### [board-confirm] -- NOT called by any local example; CTO bring-up grep targets
| item | grep target / action at bring-up |
|---|---|
| CCES 2.11->2.12 header-name drift (ALT is 2.11.1; bench 2.12.1) | grep installed 2.12.1 SHARC/include for adi_sport.h / adi_pdma_2156x.h / adi_twi_2156x.h / adi_spu.h (names expected identical) |
| **[R31 F31-MAJOR-1] header SUFFIX ASYMMETRY (R25 adi_mdma-class trap)**: ALT includes adi_sport.h / adi_spu.h (NO suffix) BUT adi_twi_2156x.h / adi_pdma_2156x.h (WITH suffix); AND adi_sport_2156x.h ALSO exists in the tree alongside adi_sport.h | bring-up MUST confirm the EXACT header name PER DRIVER in the installed 2.12.1 include tree -- a no-suffix name may not exist in a given version (exactly how no-suffix adi_mdma.h produced the 9 CCES errors in R25). Do NOT assume the ALT 2.11.1 names carry over driver-by-driver |
| ADI_SPORT_MEMORY_SIZE / ADI_TWI_MEMORY_SIZE / ADI_SPU_MEMORY_SIZE numeric values | confirm macros resolve in the installed headers (used as array sizes) |
| exact adi_sport_ConfigMC / ConfigFrameSync formal-arg semantics for OUR 8-slot | open installed adi_sport.h, confirm window/MFD/FS arg meaning (ALT used 7u for 8 slots; verify count-vs-index convention) |
| codec SAI field = TDM8 (SAI=011) for 8-ch + DAC slot/CMAP for 8-of-12 | datasheet adau1979.pdf Register 0x05-0x08 (l.2226) + ADAU1962A DAC_CTRL/slot; verify at bring-up |
| DMA-buffer cache op (only if buffers moved off L1) | flush_data_buffer in <sys/cache.h> (H1 A5 symbol); only needed if cached L2/external placement |

### Open gaps (G-M1)
- G-M1-1: codec SAI field TDM-vs-I2S naming (ALT mixes I2S-named reg with MC/TDM SPORT) -> confirm SAI=011 (TDM8).
- G-M1-2: 8-slot SelectChannel range + CMAP/DAC slot map for our 1-in/8-out topology (architecture decision).
- G-M1-3: 8-of-12 DAC channel routing to 8 amps (DOC-S4-IO-01 G-IO4 = product wiring) -> architecture + bring-up.
- (datasheet completeness: both ADAU1979.pdf and ADAU1962A.pdf ARE present locally -- no datasheet missing.)

================================================================================
## (5) io-CALLBACK PROBE EMBEDDING PROPOSAL  (suggestion only -- not implemented)
================================================================================
- WHICH callback: the SPORT RX-buffer-processed handler (ALT.c:167 SPORTCallback, event
  ADI_SPORT_EVENT_RX_BUFFER_PROCESSED). This is the per-block core cost = the io item-1 "codec/IO DMA"
  share that the H2 MDMA proxy could NOT measure (H2 measured CONTENTION only; this is the real CALLBACK
  core cost, turning the [L3] io-callback ~30 MCPS allowance into an [L1] measured number).
- WHAT to bracket (CCNT, RAW only -- C9): wrap bench_cyc_target() around the callback BODY = the
  RX->TX copy (M1) / the beamformer (M2) + the descriptor-service + any cache op. Store raw last/max/min
  CCNT deltas; do NOT compute MCPS in the ISR (margins off-board). Off-board: io-callback MCPS =
  cb_cyc x (block-rate) / 1e6, where block-rate = FS / M1_BLOCK_FRAMES (e.g. 48000/256 = 187.5 Hz).
- WHY max/min: WCET of the callback (max) + jitter band (max-min); the copy is data-independent so
  variance should be small -- a large spread flags cache/preemption interaction (cross-check vs H2).
- FG tie-in: the same callback increments a RX-block counter + scans for non-zero audio (silence/dead-DMA
  detector) so a dead codec or dead DMA leaves counters at 0 and cannot fake a green passthrough.
- FREE-RUN: read all probe globals at idle only (no mid-callback breakpoints), per the H1/H2 CCNT lesson.

================================================================================
## SUMMARY for CTO architecture design
================================================================================
- A complete proven [L1] reference exists (Audio_Loopback_TDM, real 21569 ADAU1979->SPORT4 TDM->ADAU1962A):
  every SPORT/TWI/SPU/PDMA symbol is example-called with file:line; codec init tables are verbatim-usable.
- Our 8slot x 32bit @48k baseline = the codecs' native TDM8 / 256xfS = 12.288 MHz (datasheet-confirmed,
  both ADAU pdfs) -- matches ALT's slot/width/fS/BCLK exactly. Only TWO codec-register choices differ and
  need CTO/bring-up pinning: SAI-field TDM8 confirmation (G-M1-1) + 1-in/8-out slot/CMAP mapping (G-M1-2/3).
- SPORT-PDMA ping-pong (2 desc/dir, circular, RX-done callback) is the data-flow skeleton; buffers default
  to L1 Block 0 (uncached -> no flush needed). Architecture should decide buffer block to avoid the H2/R24
  L1-self-conflict pattern vs the M2 beamformer working set (pin to seg_l1_block1 if co-resident).
- io-callback probe = CCNT bracket on the RX-done callback body -> the [L1] io item-1 core cost the H2
  proxy left as [L3]; plus a stream-live FG (block-count + non-zero audio) against false green.
- board-confirm list (CCES 2.11->2.12 header drift, memory-size macros, ConfigMC 8-slot arg semantics,
  codec TDM/slot regs) is short and grep-pinnable -- no MDMA-style surprise expected (the whole flow is
  one example away). No datasheet missing locally.
