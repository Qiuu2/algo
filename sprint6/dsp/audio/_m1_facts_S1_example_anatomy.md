# FACTS S1_example_anatomy (Audio_Loopback_TDM, ADSP-21569)

Scope note: all line numbers below refer to files under
knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/.
Short path prefix used in SRC fields:
- src/ = .../Audio_Loopback_TDM/src/
- EZKIT/ = .../Audio_Loopback_TDM/EV-SOMCRR-EZKIT/

## F-bringup-top-level-order
- FACT: main() bring-up call order is: adi_initComponents() -> SPU_init() -> [Switch_Configurator() is COMMENTED OUT] -> SRU_Init() -> Init_TWI() -> ADAU_1962_init() (DAC) -> ADAU_1979_init() (ADC) -> Sport_Init() -> Stop_TWI(), then GPIO LED setup, then infinite audio loop.
  SRC: src/Audio_Loopback_TDM.c:688-804
  GRADE: [L1-example-called]
- FACT: Switch_Configurator() (which calls ConfigSoftSwitches_ADC_DAC + ConfigSoftSwitches_ADAU_Reset) is defined but its call site in main is commented out, so the SoftConfig SoftSwitch sequence is NOT executed at runtime in this build.
  SRC: src/Audio_Loopback_TDM.c:701 (commented "//Switch_Configurator();"); definition at :378-401
  GRADE: [L1-example-called]
- FACT: adi_initComponents() (auto-generated) runs adi_sec_Init() -> adi_initpinmux() -> adi_SRU_Init(), in that order, each gated on previous result==0.
  SRC: EZKIT/system/adi_initialize.c:19-33
  GRADE: [L1-example-called]
- FACT: Codec/SPORT init are each gated behind `if (Result==0u)`, so a non-zero from any earlier stage skips the rest (sequential short-circuit, not abort).
  SRC: src/Audio_Loopback_TDM.c:695-734
  GRADE: [L1-example-called]

## F-spu-secure
- FACT: SPU_init() calls adi_spu_Init(0, SpuMemory, NULL, NULL, &ghSpu), then adi_spu_EnableMasterSecure(ghSpu, SPORT_4A_SPU, true) and adi_spu_EnableMasterSecure(ghSpu, SPORT_4B_SPU, true).
  SRC: src/Audio_Loopback_TDM.c:453-476
  GRADE: [L1-example-called]
- FACT: SPORT_4A_SPU=57 and SPORT_4B_SPU=58 are the SPU master indices passed to adi_spu_EnableMasterSecure.
  SRC: src/Audio_Loopback_TDM.h:39-40
  GRADE: [L1-example-called]
- FACT: SPU memory is a static byte array sized ADI_SPU_MEMORY_SIZE (uint8_t SpuMemory[ADI_SPU_MEMORY_SIZE]); SPU handle ghSpu is static.
  SRC: src/Audio_Loopback_TDM.c:145-148
  GRADE: [L1-example-called]

## F-sru-routing
- FACT: SRU_Init() first writes pads enable registers: *pREG_PADS0_DAI0_IE=0x1ffffe and *pREG_PADS0_DAI1_IE=0x1ffffe.
  SRC: src/Audio_Loopback_TDM.c:417-418
  GRADE: [L1-example-called]
- FACT: SRU clock routing: SRU2(DAI1_PB05_O,SPT4_ACLK_I) and SRU2(DAI1_PB05_O,SPT4_BCLK_I) route DAC bit-clock to SPORT4A and SPORT4B clock inputs; SRU2(DAI1_PB05_O,DAI1_PB12_I) forwards clock to ADC.
  SRC: src/Audio_Loopback_TDM.c:422-423, 432
  GRADE: [L1-example-called]
- FACT: SRU frame-sync routing: SRU2(DAI1_PB04_O,SPT4_AFS_I) and SRU2(DAI1_PB04_O,SPT4_BFS_I) route DAC FS to SPORT4A/4B; SRU2(DAI1_PB04_O,DAI1_PB20_I) forwards FS to ADC.
  SRC: src/Audio_Loopback_TDM.c:425-426, 435
  GRADE: [L1-example-called]
- FACT: SRU data routing: SRU2(SPT4_AD0_O,DAI1_PB02_I) routes SPORT4A data out to DAC; SRU2(DAI1_PB06_O,SPT4_BD0_I) routes ADC data into SPORT4B data input.
  SRC: src/Audio_Loopback_TDM.c:429, 438
  GRADE: [L1-example-called]
- FACT: SRU pin-enable (PBENxx) lines accompany each route: PBEN05=LOW, PBEN04=LOW, PBEN02=HIGH, PBEN12=HIGH, PBEN20=HIGH, PBEN06=LOW.
  SRC: src/Audio_Loopback_TDM.c:420, 427, 430, 433, 436, 439
  GRADE: [L1-example-called]

## F-twi-open-config
- FACT: Init_TWI() sequence: adi_twi_Open(TWIDEVNUM, ADI_TWI_MASTER, &TwideviceMemory[0], ADI_TWI_MEMORY_SIZE, &hTwiDevice) -> adi_twi_SetPrescale(hTwiDevice, PRESCALEVALUE) -> adi_twi_SetBitRate(hTwiDevice, BITRATE) -> adi_twi_SetDutyCycle(hTwiDevice, DUTYCYCLE) -> adi_twi_SetHardwareAddress(hTwiDevice, TARGETADDR).
  SRC: src/Audio_Loopback_TDM.c:508-546
  GRADE: [L1-example-called]
- FACT: TWI config constants: TWIDEVNUM=2u, BITRATE=100u (kHz), DUTYCYCLE=50u (percent), PRESCALEVALUE=12u, TARGETADDR=0x38u, TARGETADDR_1962=0x04u (DAC), TARGETADDR_1979=0x11u (ADC).
  SRC: src/Audio_Loopback_TDM.h:28-37
  GRADE: [L1-example-called]
- FACT: Per-register TWI write is Write_TWI_8bit_Reg(Reg,Val): loads devBuffer[0]=Reg, devBuffer[1]=Data, then adi_twi_Write(hTwiDevice, devBuffer, 2u, false).
  SRC: src/Audio_Loopback_TDM.c:478-483
  GRADE: [L1-example-called]
- FACT: Per-register TWI readback is Read_TWI_8bit_Reg(Reg): adi_twi_Write(hTwiDevice, devBuffer, 1u, true) (repeated-start, address phase) then adi_twi_Read(hTwiDevice, &Rx_Data, 1u, false).
  SRC: src/Audio_Loopback_TDM.c:485-506
  GRADE: [L1-example-called]
- FACT: Stop_TWI() calls adi_twi_Close(hTwiDevice); main() closes TWI before entering the audio loop (TWI not used during streaming).
  SRC: src/Audio_Loopback_TDM.c:548-556, 730-734
  GRADE: [L1-example-called]

## F-dac-1962-init-and-pll
- FACT: ADAU_1962_init() = ADAU_1962_Pllinit() then a loop i=0..27 writing Config_array_DAC[i] via Write_TWI_8bit_Reg and reading back via Read_TWI_8bit_Reg, comparing write==readback; mismatch returns FAILED.
  SRC: src/Audio_Loopback_TDM.c:560-576
  GRADE: [L1-example-called]
- FACT: ADAU_1962_Pllinit() sets TWI hw addr to TARGETADDR_1962 (0x04), then writes PLL_CTL_CTRL0=0x01, (delay), PLL_CTL_CTRL0=0x05, (delay), PLL_CTL_CTRL1=0x22, (delay), then polls PLL_CTL_CTRL1 until bit2 ((status & 0x4)>>2) is set = PLL lock.
  SRC: src/Audio_Loopback_TDM.c:578-617
  GRADE: [L1-example-called]
- FACT: ADAU1962 register macros: PLL_CTL_CTRL0=0x00, PLL_CTL_CTRL1=0x01, PDN_CTRL_1=0x02, PDN_CTRL_2=0x03, PDN_CTRL_3=0x04, DAC_CTRL0=0x06, DAC_CTRL1=0x07, MSTR_VOL=0x0b, PAD_STRGTH=0x1C, DAC_PWR1=0x1D.
  SRC: src/ADAU_1962Common.h:10-35
  GRADE: [L1-example-called]
- FACT: Config_array_DAC[28] full write order (Reg,Value): PDN_CTRL_1=0x00, PDN_CTRL_2=0xff, PDN_CTRL_3=0x0f, DAC_CTRL0=0x01, DAC_CTRL1=0x01, DAC_CTRL2=0x00, DAC_MUTE1=0x0, DAC_MUTE2=0x00, MSTR_VOL=0x00, DAC1..DAC12_VOL=0x00 (12 regs), PAD_STRGTH=0x00, DAC_PWR1=0xaa, DAC_PWR2=0xaa, DAC_PWR3=0xaa, PDN_CTRL_2=0x00, PDN_CTRL_3=0x00, DAC_CTRL0=0x18.
  SRC: src/Audio_Loopback_TDM.c:61-91
  GRADE: [L1-example-called]
- FACT: DAC delay between PLL writes uses busy-loop `int delay1=0xffff; while(delay1--) asm("nop;");` (no timer, no driver), re-armed before each step.
  SRC: src/Audio_Loopback_TDM.c:580, 591-609
  GRADE: [L1-example-called]

## F-adc-1979-init-and-pll
- FACT: ADAU_1979_init() = ADAU_1979_Pllinit() then loop i=0..15 writing Config_array_ADC[i] via Write_TWI_8bit_Reg with readback compare; mismatch returns FAILED.
  SRC: src/Audio_Loopback_TDM.c:622-639
  GRADE: [L1-example-called]
- FACT: ADAU_1979_Pllinit() sets TWI hw addr to TARGETADDR_1979 (0x11), writes REG_POWER=0x01, REG_PLL=0x03, reads REG_PLL, then polls REG_PLL until bit7 ((status & 0x80)>>7) is set = PLL lock (with nop busy-wait inside loop).
  SRC: src/Audio_Loopback_TDM.c:641-669
  GRADE: [L1-example-called]
- FACT: ADAU1979 register macros: REG_POWER=0x00, REG_PLL=0x01, REG_BOOST=0x02, REG_MICBIAS=0x03, REG_BLOCK_POWER_SAI=0x04, REG_SAI_CTRL0=0x05, REG_MISC_CONTROL=0x0e.
  SRC: src/ADAU_1979Common.h:11-25
  GRADE: [L1-example-called]
- FACT: Config_array_ADC[16] write order (Reg,Value): BOOST=0x00, MICBIAS=0x00, BLOCK_POWER_SAI=0x30, SAI_CTRL0=0x1B (comment "I2S 48kHz"), SAI_CTRL1=0x08, CMAP12=0x01, CMAP34=0x23, SAI_OVERTEMP=0xf0, POST_ADC_GAIN1..4=0xA0, ADC_CLIP=0x00, DC_HPF_CAL=0x00, BLOCK_POWER_SAI=0x3f, MISC_CONTROL=0x00.
  SRC: src/Audio_Loopback_TDM.c:93-111
  GRADE: [L1-example-called]

## F-sport-open-config
- FACT: SPORT 4A (TX) opened: adi_sport_Open(SPORT_DEVICE_4A, ADI_HALF_SPORT_A, ADI_SPORT_DIR_TX, ADI_SPORT_MC_MODE, SPORTMemory4A, ADI_SPORT_MEMORY_SIZE, &hSPORTDev4ATx).
  SRC: src/Audio_Loopback_TDM.c:292
  GRADE: [L1-example-called]
- FACT: SPORT 4B (RX) opened: adi_sport_Open(SPORT_DEVICE_4B, ADI_HALF_SPORT_B, ADI_SPORT_DIR_RX, ADI_SPORT_MC_MODE, SPORTMemory4B, ADI_SPORT_MEMORY_SIZE, &hSPORTDev4BRx). Both 4A and 4B device numbers are 4u (same physical SPORT4, two half-SPORTs A/B).
  SRC: src/Audio_Loopback_TDM.c:295; device-num macros src/Audio_Loopback_TDM.h:26-27
  GRADE: [L1-example-called]
- FACT: SPORT4A TX configured (full call series, exact actuals): adi_sport_ConfigData(hSPORTDev4ATx, ADI_SPORT_DTYPE_SIGN_FILL, 31, false, false, false); adi_sport_ConfigClock(hSPORTDev4ATx, 32, false, false, false); adi_sport_ConfigFrameSync(hSPORTDev4ATx, 31, false, false, false, true, false, false); adi_sport_ConfigMC(hSPORTDev4ATx, 1u, 7u, 0u, true); adi_sport_SelectChannel(hSPORTDev4ATx, 0u, 11u).
  SRC: src/Audio_Loopback_TDM.c:299-308
  GRADE: [L1-example-called]
- FACT: SPORT4B RX configured (full call series, exact actuals): adi_sport_ConfigData(hSPORTDev4BRx, ADI_SPORT_DTYPE_SIGN_FILL, 31, false, false, false); adi_sport_ConfigClock(hSPORTDev4BRx, 32, false, false, false); adi_sport_ConfigFrameSync(hSPORTDev4BRx, 31, false, false, false, true, false, false); adi_sport_ConfigMC(hSPORTDev4BRx, 1u, 7u, 0u, true); adi_sport_SelectChannel(hSPORTDev4BRx, 0u, 3u).
  SRC: src/Audio_Loopback_TDM.c:311-319
  GRADE: [L1-example-called]
- FACT: ConfigMC actuals are (window_size=1u, MC_count/last_active=7u, offset=0u, packed=true) for BOTH 4A and 4B => 8 TDM channels (slots 0..7); ConfigData word length arg 31 => 32-bit words (DTYPE_SIGN_FILL).
  SRC: src/Audio_Loopback_TDM.c:305, 317 (TX/RX ConfigMC); 299, 311 (ConfigData)
  GRADE: [inferred]  (slot-count read of the 7u "last active channel" arg; exact ConfigMC param semantics need adi_sport.h prototype, see NOT_FOUND)
- FACT: SelectChannel differs TX vs RX: TX (4A) selects channels 0u..11u (DAC has up to 12 output slots); RX (4B) selects channels 0u..3u (ADC 4 input slots).
  SRC: src/Audio_Loopback_TDM.c:307, 319
  GRADE: [L1-example-called]
- FACT: SPORT static memory: uint8_t SPORTMemory4A[ADI_SPORT_MEMORY_SIZE], SPORTMemory4B[ADI_SPORT_MEMORY_SIZE]; handles hSPORTDev4ATx (TX) and hSPORTDev4BRx (RX) are static.
  SRC: src/Audio_Loopback_TDM.c:131-136
  GRADE: [L1-example-called]

## F-dma-descriptors
- FACT: DMA uses ADI_PDMA_DESC_LIST descriptor structs, 4 instances: TX destination lists iDESC_LIST_1_SP4A / iDESC_LIST_2_SP4A; RX source lists iSRC_LIST_1_SP4B / iSRC_LIST_2_SP4B.
  SRC: src/Audio_Loopback_TDM.c:113-119
  GRADE: [L1-example-called]
- FACT: PrepareDescriptors() builds a 2-node circular ping-pong ring per direction. TX: iDESC_LIST_1_SP4A.pNxtDscp=&iDESC_LIST_2_SP4A and iDESC_LIST_2_SP4A.pNxtDscp=&iDESC_LIST_1_SP4A (closes loop). RX: iSRC_LIST_1_SP4B.pNxtDscp=&iSRC_LIST_2_SP4B and iSRC_LIST_2_SP4B.pNxtDscp=&iSRC_LIST_1_SP4B.
  SRC: src/Audio_Loopback_TDM.c:259, 267, 275, 283
  GRADE: [L1-example-called]
- FACT: Descriptor fields: Config=ENUM_DMA_CFG_XCNT_INT (interrupt on XCount complete), XModify=4 (bytes, 32-bit stride), YCount=0, YModify=0 (1-D). TX XCount=COUNT*2 over buffers int_SP0ABuffer1/2; RX XCount=COUNT over int_SP0ABuffer4/5.
  SRC: src/Audio_Loopback_TDM.c:253-283
  GRADE: [L1-example-called]
- FACT: DMA submit: RX first via adi_sport_DMATransfer(hSPORTDev4BRx, &iSRC_LIST_1_SP4B, DMA_NUM_DESC, ADI_PDMA_DESCRIPTOR_LIST, ADI_SPORT_CHANNEL_PRIM); then TX adi_sport_DMATransfer(hSPORTDev4ATx, &iDESC_LIST_1_SP4A, DMA_NUM_DESC, ADI_PDMA_DESCRIPTOR_LIST, ADI_SPORT_CHANNEL_PRIM). DMA_NUM_DESC=2u.
  SRC: src/Audio_Loopback_TDM.c:330-333; DMA_NUM_DESC macro src/Audio_Loopback_TDM.h:42
  GRADE: [L1-example-called]
- FACT: Transfer descriptor count passed is DMA_NUM_DESC=2 with mode ADI_PDMA_DESCRIPTOR_LIST on primary channel ADI_SPORT_CHANNEL_PRIM.
  SRC: src/Audio_Loopback_TDM.c:330-333
  GRADE: [L1-example-called]

## F-callback-register-and-enable-order
- FACT: Callback registered ONLY on RX: adi_sport_RegisterCallback(hSPORTDev4BRx, SPORTCallback, NULL) (NULL app handle); no callback registered on TX.
  SRC: src/Audio_Loopback_TDM.c:323
  GRADE: [L1-example-called]
- FACT: Sport_Init() order after open/config: RegisterCallback(RX) -> PrepareDescriptors() -> DMATransfer(RX submit) -> DMATransfer(TX submit) -> adi_sport_Enable(hSPORTDev4BRx,true) (RX) -> adi_sport_Enable(hSPORTDev4ATx,true) (TX). RX enabled before TX.
  SRC: src/Audio_Loopback_TDM.c:323-341
  GRADE: [L1-example-called]

## F-frame-callback-logic
- FACT: SPORTCallback switches on nEvent and only handles case ADI_SPORT_EVENT_RX_BUFFER_PROCESSED; default does nothing. It increments TestCallbackCount and CallbackCount.
  SRC: src/Audio_Loopback_TDM.c:167-235
  GRADE: [L1-example-called]
- FACT: Buffer-index switching is driven by CallbackCount: CallbackCount==1 copies RX buffer int_SP0ABuffer4 -> TX buffer int_SP0ABuffer1; CallbackCount==2 copies int_SP0ABuffer5 -> int_SP0ABuffer2 then resets CallbackCount=0 (manual ping-pong tracking).
  SRC: src/Audio_Loopback_TDM.c:185-230
  GRADE: [L1-example-called]
- FACT: Copy logic is a manual loop (i+=4, j+=8) that duplicates each RX 4-sample group into 8 TX slots (each ADC sample written to two adjacent DAC slots, e.g. buf1[j]=buf4[i] and buf1[j+4]=buf4[i]), i.e. 4-ch ADC fanned out to 8-ch TDM DAC. Loop runs i<COUNT.
  SRC: src/Audio_Loopback_TDM.c:187-205 (CB==1), 210-228 (CB==2)
  GRADE: [L1-example-called]
- FACT: TX descriptor XCount=COUNT*2 (=600) matches the 8-slot fan-out (2x the COUNT-sized RX), consistent with the i+=4/j+=8 duplication.
  SRC: src/Audio_Loopback_TDM.c:255, 263 (XCount=COUNT*2) vs :187 (loop i<COUNT); COUNT=300 at src/Audio_Loopback_TDM.h:24
  GRADE: [inferred]
- FACT: No cache flush/invalidate call appears in the callback path or DMA submit path (no adi_cache_* call in the file); callback does direct array copy only.
  SRC: src/Audio_Loopback_TDM.c:167-235, 326-334 (absence)
  GRADE: [board-confirm]  (whether L1 cache coherence is needed depends on placement/cache config; cannot confirm from source alone)

## F-error-handling-pattern
- FACT: SPORT/SPU/DMA calls use CHECK_RESULT(eResult) macro which returns 1 from the enclosing function on any non-zero result (no logging): `if(eResult != 0){ return (1); }`.
  SRC: macro src/Audio_Loopback_TDM.h:48-52; usage e.g. src/Audio_Loopback_TDM.c:293, 296, 300...341
  GRADE: [L1-example-called]
- FACT: TWI calls use a different pattern: compare eResult!=ADI_TWI_SUCCESS and call REPORT_ERROR (==printf) but do NOT return/abort (execution continues after a logged TWI error).
  SRC: src/Audio_Loopback_TDM.c:515-543 (Init_TWI), 493-503 (Read_TWI)
  GRADE: [L1-example-called]
- FACT: Codec config loops detect failure by write-vs-readback mismatch and return FAILED (=-1) with DEBUG_INFORMATION (==printf) message ("Configuring ADAU_1962/1979 failed").
  SRC: src/Audio_Loopback_TDM.c:568-572 (DAC), 631-635 (ADC)
  GRADE: [L1-example-called]
- FACT: main() error model: stages run only while Result==0u; GPIO failures printf but do not stop; REPORT_ERROR and DEBUG_INFORMATION are both #defined to printf.
  SRC: src/Audio_Loopback_TDM.c:695-755; macros src/Audio_Loopback_TDM.h:54-55
  GRADE: [L1-example-called]

## F-buffer-declaration-and-placement
- FACT: SPORT data buffers are plain global int arrays: int_SP0ABuffer1[COUNT*2], int_SP0ABuffer2[COUNT*2] (TX, =600 each), int_SP0ABuffer4[COUNT], int_SP0ABuffer5[COUNT] (RX, =300 each). COUNT=300.
  SRC: src/Audio_Loopback_TDM.c:40-43; COUNT macro src/Audio_Loopback_TDM.h:24
  GRADE: [L1-example-called]
- FACT: No #pragma section / placement directive is attached to the SPORT buffers in the source file; they are ordinary globals (default linker placement via app.ldf).
  SRC: src/Audio_Loopback_TDM.c:39-43 (absence of pragma)
  GRADE: [L1-example-called]
- FACT: Additional unused-in-streaming float buffers Audio_channel1..12[256] are declared as globals (not wired into the SPORT/DMA path observed).
  SRC: src/Audio_Loopback_TDM.c:26-38
  GRADE: [L1-example-called]
- FACT: Driver scratch memory blocks are static byte arrays sized by driver MEMORY_SIZE macros: SPORTMemory4A/4B[ADI_SPORT_MEMORY_SIZE], TwideviceMemory[ADI_TWI_MEMORY_SIZE], SpuMemory[ADI_SPU_MEMORY_SIZE], devBuffer[BUFFER_SIZE=8].
  SRC: src/Audio_Loopback_TDM.c:55, 131-148; BUFFER_SIZE macro src/Audio_Loopback_TDM.h:33
  GRADE: [L1-example-called]
- FACT: TX buffer byte size = COUNT*2*sizeof(int) = 600*4 = 2400 bytes each; RX buffer byte size = COUNT*sizeof(int) = 300*4 = 1200 bytes each (consistent with XModify=4).
  SRC: src/Audio_Loopback_TDM.c:40-43, 256, 272
  GRADE: [inferred]  (sizeof(int)=4 on SHARC assumed; arithmetic derived, not stated)

## F-compiled-driver-dependencies
- FACT: The build dependency file for the main TU lists these driver headers as actually compiled into the object: adi_sport.h, adi_twi_2156x.h, adi_spu.h, adi_gpio.h, adi_pdma_2156x.h, adi_pdma_config_2156x.h, adi_twi_config_2156x.h (confirms SPORT/TWI/SPU/GPIO/PDMA drivers are in this build).
  SRC: EZKIT/Debug/src/Audio_Loopback_TDM.d (grep of header paths)
  GRADE: [L1-example-called]
- FACT: SoftConfig source files (SoftConfig_EV_SOMCRR_EZKIT_ADC_DAC.c, ..._ADAU_Reset.c) exist and compile (have .doj/.d in Debug/system), but their entry points are only reached via Switch_Configurator(), whose call is commented out in main -> SoftConfig path declared/built but not called at runtime.
  SRC: EZKIT/system/SoftConfig_EV_SOMCRR_EZKIT_ADC_DAC.c:127; src/Audio_Loopback_TDM.c:701 (commented call)
  GRADE: [declared-only]

## NOT_FOUND
- Exact prototype/parameter semantics of adi_sport_ConfigMC, adi_sport_ConfigData, adi_sport_ConfigFrameSync, adi_sport_ConfigClock, adi_sport_SelectChannel (each boolean/int arg's meaning) — adi_sport.h is in the installed CCES include tree, not in this example folder. [board-confirm]
- ADI_SPORT_MEMORY_SIZE, ADI_TWI_MEMORY_SIZE, ADI_SPU_MEMORY_SIZE numeric values — defined in installed driver headers, not present locally. [board-confirm]
- Numeric values of enums ADI_HALF_SPORT_A/B, ADI_SPORT_DIR_TX/RX, ADI_SPORT_MC_MODE, ADI_SPORT_DTYPE_SIGN_FILL, ADI_SPORT_CHANNEL_PRIM, ADI_PDMA_DESCRIPTOR_LIST, ADI_SPORT_EVENT_RX_BUFFER_PROCESSED, ENUM_DMA_CFG_XCNT_INT — defined in installed headers/cdef21569.h, not local. [board-confirm]
- adi_gpio init/Open: example calls adi_gpio_SetDirection but no adi_gpio_Init call is visible in the .c; whether GPIO service init happens inside adi_initComponents/pinmux needs the installed gpio service source. [board-confirm]
- ADAU1962/1979 datasheet page/table numbers backing the specific register values (e.g. why PLL_CTL_CTRL1=0x22, SAI_CTRL0=0x1B for 48kHz I2S) — codec datasheets not cross-referenced in this subtask. [board-confirm]

## SUMMARY
Audio_Loopback_TDM (21569, EV-SOMCRR-EZKIT) brings up audio in this fixed runtime order: adi_initComponents (sec/pinmux/SRU) -> SPU_init (mark SPORT4A/4B masters secure, indices 57/58) -> SRU_Init (DAI1 routing of DAC BCLK/FS/data to SPORT4 and forwarding to ADC) -> Init_TWI (dev 2, 100kHz) -> ADAU_1962 DAC init (PLL: write CTRL0 0x01/0x05, CTRL1 0x22, poll CTRL1 bit2 for lock; then 28-reg write-with-readback at addr 0x04) -> ADAU_1979 ADC init (PLL: REG_POWER 0x01, REG_PLL 0x03, poll REG_PLL bit7; then 16-reg write-with-readback at addr 0x11) -> Sport_Init -> Stop_TWI. Note Switch_Configurator/SoftConfig is COMMENTED OUT, so codec power/reset relies on default board state. SPORT4 is split into half-A (TX, MC mode, 8 TDM slots via ConfigMC 1/7/0/packed, 32-bit words, SelectChannel 0..11) and half-B (RX, SelectChannel 0..3). DMA is a 2-node circular ping-pong of ADI_PDMA_DESC_LIST descriptors per direction (XCount COUNT*2 TX / COUNT RX, XModify 4, interrupt-on-count), submitted via adi_sport_DMATransfer (RX then TX), with a callback registered only on RX. The RX callback handles ADI_SPORT_EVENT_RX_BUFFER_PROCESSED and uses CallbackCount (1 then 2->reset) to ping-pong which TX buffer it fills, copying 4-ch ADC samples fanned out 1->2 into 8-ch TDM DAC slots; no cache maintenance is present. Error handling is two-pattern: CHECK_RESULT (return 1 on non-zero) for SPORT/SPU/DMA, and printf-but-continue for TWI, plus write/readback compare for codec config. Buffers are plain globals with no #pragma placement (default LDF). All numeric enum/MEMORY_SIZE values and the adi_sport_* parameter semantics require the installed CCES include tree (Windows board machine) to confirm and are listed as board-confirm.

## VERIFIER_REPORT
(adversarial citation verifier, claude-opus-4-8, 2026-06-06)
- CHECKED: 42 facts (33 [L1-example-called] all opened+line/API/actuals checked; 4 [inferred] judgment-checked; 2 [board-confirm] + 1 [declared-only] judgment-checked; NOT_FOUND 5-item section spot-checked against source; SoftConfig .doj/.d + main .d 7-header grep re-run)
- METHOD: opened src/Audio_Loopback_TDM.c (full), src/Audio_Loopback_TDM.h, src/ADAU_1962Common.h, src/ADAU_1979Common.h, EZKIT/system/adi_initialize.c, EZKIT/system/SoftConfig_EV_SOMCRR_EZKIT_ADC_DAC.c; re-grepped EZKIT/Debug/src/Audio_Loopback_TDM.d for the 7 driver headers; ls EZKIT/Debug/system for SoftConfig .doj/.d. Verified against Audio_Loopback_TDM (NOT the sibling Audio_Loopback_TDM16).
- VERDICT: CLEAN
- Spot-confirm notes (no defect, recorded for traceability):
  - F-spu: code symbol is SPORT_4A_SPU/SPORT_4B_SPU (=57/58, .h:39-40); source comments at .c:461/468 say "SPORT 0A/0B" (stale ADI boilerplate). Fact correctly reports the CODE symbol/value, not the stale comment. No mismatch.
  - F-bringup-top-level-order: adi_sec_Init at .c(adi_initialize):22, adi_initpinmux:26, adi_SRU_Init:30; cited range :19-33 covers the gated body. CLEAN.
  - All register-macro tables (1962Common.h:10-35, 1979Common.h:11-25) hex values matched line-by-line; SAI_CTRL0=0x1B "I2S 48kHz" comment present at .c:98.
  - [inferred] tags (ConfigMC slot-count, TX XCount fan-out, sizeof(int)=4 byte-size, COUNT*2=600) are honestly labeled inferred, not dressed as fact. [board-confirm] (no-cache, MEMORY_SIZE numerics, adi_sport_* semantics) correctly require installed include tree. [declared-only] SoftConfig judgment correct: source+.doj/.d exist (built) but call site .c:701 is commented out (not called at runtime).
- MISMATCH: (none)
