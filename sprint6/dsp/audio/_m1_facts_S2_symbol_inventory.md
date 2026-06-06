# FACTS S2_symbol_inventory (SPORT/codec/DMA real symbol clean-list)

> Scope: adi_sport* / adi_twi* / adi_spu* / adi_pdma* / codec symbols findable locally.
> Primary [L1-example-called] call site: Audio_Loopback_TDM example (ADAU1979 ADC -> SPORT4 TDM -> ADAU1962A DAC loopback),
> path prefix ALT = knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/src/Audio_Loopback_TDM.c
> Header-path evidence (.d) = knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/EV-SOMCRR-EZKIT/Debug/src/Audio_Loopback_TDM.d (abbrev ALT.d)
> Cross-check secondary call site: Audio_Passthrough_I2S (path prefix API2 below).
> CRITICAL CAVEAT: the real BSP header BODIES (install-tree adi_sport.h / adi_sport_2156x.h / adi_twi.h / adi_twi_2156x.h /
>   adi_spu.h / adi_spu_v3.h / adi_pdma_2156x.h) are NOT present locally -- per .d they live under
>   "C:/Analog Devices/CrossCore Embedded Studio 2.11.1/SHARC/include/..." on the CTO Windows board machine
>   (NOTE: .d shows CCES *2.11.1*, the task brief mentions 2.12.1 -- version delta unverified, [board-confirm]).
>   The only local same-name files (sprint6/dsp/audio/guard_stub_inc/*) are explicit DESKTOP-ONLY parse-stubs
>   ("NOT the real BSP header") -- they are NOT used as signature evidence here. All function signatures below
>   are reconstructed from the actual ARGUMENT lists at the L1 call sites; exact parameter TYPES/return-enum
>   definitions are [board-confirm] against the install-tree headers.

## F-header-asymmetry (the suffix non-symmetry -- R25/R31 trap, independently re-verified from .d)
- FACT: SPORT ships TWO coexisting install-tree headers: drivers/sport/adi_sport.h (no suffix, API) AND drivers/sport/adi_sport_2156x.h (device suffix); app source #includes the NO-suffix <drivers/sport/adi_sport.h>.
  SRC: ALT.d:40-41 (both paths listed); ALT:16 (#include <drivers/sport/adi_sport.h>)
  GRADE: [L1-example-called]
- FACT: SPU ships TWO coexisting install-tree headers but the variant suffix is _v3 NOT _2156x: services/spu/adi_spu.h (no suffix, API) AND services/spu/adi_spu_v3.h (_v3 impl); app source #includes the NO-suffix <services/spu/adi_spu.h>.
  SRC: ALT.d:49-50 (both paths); ALT:17 (#include <services/spu/adi_spu.h>)
  GRADE: [L1-example-called]
- FACT: TWI ships TWO coexisting install-tree headers: drivers/twi/adi_twi.h (no suffix, API) AND drivers/twi/adi_twi_2156x.h (device suffix); BOTH exist in the install tree.
  SRC: ALT.d:51 (adi_twi_2156x.h); Audio_Passthrough_I2S/EV-SOMCRR-EZKIT/Debug/src/Audio_Passthrough_I2S.d:51-52 (lists BOTH adi_twi.h and adi_twi_2156x.h); BSP build dep system/drivers/twi/adi_twi.d:25 (adi_twi.h)
  GRADE: [L1-example-called]
- FACT: TWI source-include choice DIFFERS per example -- Audio_Loopback_TDM #includes the _2156x suffix variant, Audio_Passthrough_I2S #includes the no-suffix variant (both compile).
  SRC: ALT:18 (#include <drivers/twi/adi_twi_2156x.h>) vs Audio_Passthrough_I2S/src/Audio_Passthrough_I2S.c:20 (#include <drivers/twi/adi_twi.h>)
  GRADE: [L1-example-called]
- FACT: PDMA ships ONLY the suffixed install-tree header services/pdma/adi_pdma_2156x.h -- NO plain adi_pdma.h exists in any local .d; and it is pulled in TRANSITIVELY (no direct #include of any adi_pdma header in ALT.c app source).
  SRC: ALT.d:46 (adi_pdma_2156x.h, only pdma path); grep "pdma/adi_pdma.h" across all *.d = zero hits; ALT:10-24 (#include block has no pdma line)
  GRADE: [L1-example-called]
- FACT: Per-driver config headers (compile-time generated, NOT the API) are local: adi_sport_config_2156x.h, adi_twi_config_2156x.h, adi_pdma_config_2156x.h -- always _2156x-suffixed; these are the only sport/twi/pdma .h with local BODIES.
  SRC: ALT.d:47-48,52 (../system/drivers/.../*_config_2156x.h); local file e.g. Audio_Loopback_TDM/EV-SOMCRR-EZKIT/system/drivers/sport/adi_sport_config_2156x.h
  GRADE: [L1-example-called]

## F-sport-functions (signatures = argument pattern at L1 call site; param TYPES [board-confirm])
- FACT: adi_sport_Open(uint32_t nDevNum, ADI_SPORT_CHANNEL eChannel(half A/B), ADI_SPORT_DIRECTION eDir(TX/RX), ADI_SPORT_TYPE eType(MC mode), void *pMemory, uint32_t nMemSize, ADI_SPORT_HANDLE *phDevice) -> ADI_SPORT_RESULT. Called with (SPORT_DEVICE_4A, ADI_HALF_SPORT_A, ADI_SPORT_DIR_TX, ADI_SPORT_MC_MODE, SPORTMemory4A, ADI_SPORT_MEMORY_SIZE, &hSPORTDev4ATx).
  SRC: ALT:292,295
  GRADE: [L1-example-called]
- FACT: adi_sport_ConfigData(handle, ADI_SPORT_DATA_TYPE eDataType, uint8_t WordLen, bool, bool, bool) -> RESULT. Called (h, ADI_SPORT_DTYPE_SIGN_FILL, 31, false, false, false).
  SRC: ALT:299,311
  GRADE: [L1-example-called]
- FACT: adi_sport_ConfigClock(handle, uint32_t ClockRatio/ClkDiv, bool, bool, bool) -> RESULT. Called (h, 32, false, false, false).
  SRC: ALT:301,313
  GRADE: [L1-example-called]
- FACT: adi_sport_ConfigFrameSync(handle, uint32_t FsDiv, bool, bool, bool, bool, bool, bool) -> RESULT (6 bool flags after FsDiv). Called (h, 31, false,false,false,true,false,false).
  SRC: ALT:303,315
  GRADE: [L1-example-called]
- FACT: adi_sport_ConfigMC(handle, uint8_t nMFD, uint8_t nWindowSize, uint8_t nWindowOffset, bool bEnable) -> RESULT. Called (h, 1u, 7u, 0u, true) (window size 7u => 8 TDM slots).
  SRC: ALT:305,317
  GRADE: [L1-example-called]
- FACT: adi_sport_SelectChannel(handle, uint8_t nStartCh, uint8_t nEndCh) -> RESULT. Called (h, 0u, 11u) for TX and (h, 0u, 3u) for RX.
  SRC: ALT:307,319
  GRADE: [L1-example-called]
- FACT: adi_sport_RegisterCallback(handle, ADI_CALLBACK pfCallback, void *pCBParam) -> RESULT. Called (hSPORTDev4BRx, SPORTCallback, NULL).
  SRC: ALT:323
  GRADE: [L1-example-called]
- FACT: adi_sport_DMATransfer(handle, void *pDescList, uint32_t nNumDesc, ADI_SPORT_DMA_XFER_MODE eXferMode, ADI_SPORT_CHANNEL_TYPE eChannel) -> RESULT. Called (h, &iSRC_LIST_1_SP4B, DMA_NUM_DESC, ADI_PDMA_DESCRIPTOR_LIST, ADI_SPORT_CHANNEL_PRIM) -- descriptor-list DMA mode.
  SRC: ALT:330,333
  GRADE: [L1-example-called]
- FACT: adi_sport_Enable(handle, bool bEnable) -> RESULT. Called (h, true).
  SRC: ALT:337,340
  GRADE: [L1-example-called]
- FACT: adi_sport_StopDMATransfer(handle) -> RESULT. Called (hSPORTDev4BRx) / (hSPORTDev4ATx).
  SRC: ALT:353,356
  GRADE: [L1-example-called]
- FACT: adi_sport_Close(handle) -> RESULT. Called (hSPORTDev4BRx) / (hSPORTDev4ATx).
  SRC: ALT:359,362
  GRADE: [L1-example-called]
- FACT: SPORT callback prototype matches ADI_CALLBACK = void SPORTCallback(void *pAppHandle, uint32_t nEvent, void *pArg); inside it switches on nEvent.
  SRC: ALT:167-172
  GRADE: [L1-example-called]

## F-sport-enums-macros (used as token at L1; underlying enum/define value [board-confirm])
- FACT: ADI_SPORT_MEMORY_SIZE used to size static driver memory: static uint8_t SPORTMemory4A[ADI_SPORT_MEMORY_SIZE].
  SRC: ALT:131-132
  GRADE: [L1-example-called]
- FACT: ADI_SPORT_HANDLE = opaque device handle type (declared static ADI_SPORT_HANDLE hSPORTDev4ATx).
  SRC: ALT:135-136
  GRADE: [L1-example-called]
- FACT: ADI_SPORT_RESULT = return/status type for all adi_sport_* calls (local var ADI_SPORT_RESULT eResult).
  SRC: ALT:176,289,350
  GRADE: [L1-example-called]
- FACT: Enums consumed as call args: ADI_HALF_SPORT_A / ADI_HALF_SPORT_B (half-SPORT), ADI_SPORT_DIR_TX / ADI_SPORT_DIR_RX, ADI_SPORT_MC_MODE, ADI_SPORT_DTYPE_SIGN_FILL, ADI_SPORT_CHANNEL_PRIM, ADI_PDMA_DESCRIPTOR_LIST (xfer mode token).
  SRC: ALT:292,295,299,330,333
  GRADE: [L1-example-called]
- FACT: ADI_SPORT_EVENT_RX_BUFFER_PROCESSED = the callback nEvent case the example handles (RX buffer done).
  SRC: ALT:181
  GRADE: [L1-example-called]

## F-pdma-descriptor (ADI_PDMA_DESC_LIST struct -- field set proven by member assignments)
- FACT: ADI_PDMA_DESC_LIST is the descriptor-list struct used for chained SPORT DMA; instances declared as plain objects (ADI_PDMA_DESC_LIST iDESC_LIST_1_SP4A;).
  SRC: ALT:114-119 (4 instances: iDESC_LIST_1/2_SP4A, iSRC_LIST_1/2_SP4B)
  GRADE: [L1-example-called]
- FACT: ADI_PDMA_DESC_LIST fields written at L1: .pStartAddr (buffer ptr), .Config (= ENUM_DMA_CFG_XCNT_INT), .XCount, .XModify, .YCount, .YModify, .pNxtDscp (self-referential next-descriptor ptr, ring-linked).
  SRC: ALT:253-283 (all 7 members assigned for each descriptor; .pNxtDscp chains 1<->2)
  GRADE: [L1-example-called]
- FACT: ENUM_DMA_CFG_XCNT_INT used as .Config value (DMA config word enabling X-count interrupt); this is a system/cdef-level enum, comes in via cdef21569.h / pdma config not app header.
  SRC: ALT:254 (and 262,270,278); ALT:21 (#include <cdef21569.h>)
  GRADE: [L1-example-called]
- FACT: ADI_PDMA_DESC_LIST type symbol resolves from install-tree services/pdma/adi_pdma_2156x.h (transitive; suffix-only header per F-header-asymmetry).
  SRC: ALT.d:46
  GRADE: [board-confirm]

## F-twi-functions (codec control bus; signatures = arg pattern at L1)
- FACT: adi_twi_Open(uint32_t nDevNum, ADI_TWI_MODE eMode, void *pMemory, uint32_t nMemSize, ADI_TWI_HANDLE *phDevice) -> ADI_TWI_RESULT. Called (TWIDEVNUM, ADI_TWI_MASTER, &TwideviceMemory[0], ADI_TWI_MEMORY_SIZE, &hTwiDevice).
  SRC: ALT:513-514
  GRADE: [L1-example-called]
- FACT: adi_twi_SetPrescale(handle, uint32_t nPrescale) -> RESULT. Called (hTwiDevice, PRESCALEVALUE).
  SRC: ALT:520
  GRADE: [L1-example-called]
- FACT: adi_twi_SetBitRate(handle, uint32_t nBitRate) -> RESULT. Called (hTwiDevice, BITRATE).
  SRC: ALT:526
  GRADE: [L1-example-called]
- FACT: adi_twi_SetDutyCycle(handle, uint32_t nDutyCycle) -> RESULT. Called (hTwiDevice, DUTYCYCLE).
  SRC: ALT:533
  GRADE: [L1-example-called]
- FACT: adi_twi_SetHardwareAddress(handle, uint32_t nAddress) -> RESULT. Called (hTwiDevice, TARGETADDR / TARGETADDR_1962 / TARGETADDR_1979) -- re-targeted per codec before each register burst.
  SRC: ALT:539,584,648
  GRADE: [L1-example-called]
- FACT: adi_twi_Write(handle, void *pData, uint32_t nNumBytes, bool bRepeatStart) -> RESULT. Called (hTwiDevice, devBuffer, 2u, false) for reg+val; (hTwiDevice, devBuffer, 1u, true) for addr-then-read with repeat-start true.
  SRC: ALT:482,492
  GRADE: [L1-example-called]
- FACT: adi_twi_Read(handle, void *pData, uint32_t nNumBytes, bool bRepeatStart) -> RESULT. Called (hTwiDevice, &Rx_Data, 1u, false).
  SRC: ALT:499
  GRADE: [L1-example-called]
- FACT: adi_twi_Close(handle) -> RESULT. Called (hTwiDevice).
  SRC: ALT:552
  GRADE: [L1-example-called]
- FACT: TWI types/macros at L1: ADI_TWI_HANDLE (static ADI_TWI_HANDLE hTwiDevice), ADI_TWI_RESULT, ADI_TWI_SUCCESS (compare), ADI_TWI_MASTER (mode), ADI_TWI_MEMORY_SIZE (sizes uint8_t TwideviceMemory[ADI_TWI_MEMORY_SIZE]).
  SRC: ALT:139,142,487,493,513-514
  GRADE: [L1-example-called]

## F-spu-functions (bus security needed before SPORT DMA on this part)
- FACT: adi_spu_Init(uint32_t nDevNum, void *pMemory, <2 extra ptr args, NULL,NULL in example>, ADI_SPU_HANDLE *phDevice) -> ADI_SPU_RESULT. Called (0, SpuMemory, NULL, NULL, &ghSpu).
  SRC: ALT:455
  GRADE: [L1-example-called]
- FACT: adi_spu_EnableMasterSecure(handle, uint32_t nMasterID, bool bEnable) -> RESULT. Called (ghSpu, SPORT_4A_SPU, true) and (ghSpu, SPORT_4B_SPU, true) -- makes SPORT4 master generate secure transactions.
  SRC: ALT:462,469
  GRADE: [L1-example-called]
- FACT: SPU types/macros at L1: ADI_SPU_HANDLE (static ADI_SPU_HANDLE ghSpu), ADI_SPU_RESULT, ADI_SPU_SUCCESS (compare), ADI_SPU_MEMORY_SIZE (sizes uint8_t SpuMemory[ADI_SPU_MEMORY_SIZE]).
  SRC: ALT:145,148,455,462
  GRADE: [L1-example-called]
- FACT: SPU API resolves from install-tree services/spu/adi_spu.h (+ impl adi_spu_v3.h); exact prototype/return-enum bodies not local.
  SRC: ALT.d:49-50
  GRADE: [board-confirm]

## F-codec (ADAU1979 ADC + ADAU1962A DAC -- driven register-level over TWI, no adi_adau* driver)
- FACT: There is NO ADI codec driver (no adi_adau*/adi_codec* symbol); codecs are configured by raw TWI 8-bit register writes via helper Write_TWI_8bit_Reg(reg, val) / Read_TWI_8bit_Reg(reg) wrapping adi_twi_Write/Read.
  SRC: ALT:478-506 (helper defs); grep adi_adau / adi_codec across knowledge_base = zero hits in driver/service dirs
  GRADE: [L1-example-called]
- FACT: Codec bring-up entry points (static, app-level not BSP): ADAU_1962_init(), ADAU_1962_Pllinit(), ADAU_1979_init(), ADAU_1979_Pllinit() -- each re-points TWI hardware address then bursts the register table.
  SRC: ALT:152-156 (prototypes), 560,578,622,641 (defs)
  GRADE: [L1-example-called]
- FACT: Codec common register-macro headers present locally: ADAU_1962Common.h / ADAU_1979Common.h (alongside ALT.c) -- define reg-address macros (e.g. ADAU1962_PLL_CTL_CTRL0, REG_SAI_CTRL0) used in the TWI write tables.
  SRC: knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/src/ADAU_1962Common.h ; .../ADAU_1979Common.h ; used ALT:590,604
  GRADE: [L1-example-called]
- FACT: External soft-switch reset hook (board mux, not codec): ConfigSoftSwitches_ADAU_Reset(void) called in init.
  SRC: ALT:59 (extern decl), 392 (call)
  GRADE: [L1-example-called]

## F-include-paths (exact install-tree paths from .d -- the authoritative header locations)
- FACT: drivers/sport/adi_sport.h + drivers/sport/adi_sport_2156x.h resolve to CCES 2.11.1 SHARC/include (Windows install tree, not local).
  SRC: ALT.d:40-41
  GRADE: [board-confirm]
- FACT: drivers/twi/adi_twi.h + drivers/twi/adi_twi_2156x.h resolve to CCES 2.11.1 SHARC/include.
  SRC: Audio_Passthrough_I2S.d:51-52 (both); ALT.d:51 (_2156x)
  GRADE: [board-confirm]
- FACT: services/spu/adi_spu.h + services/spu/adi_spu_v3.h resolve to CCES 2.11.1 SHARC/include.
  SRC: ALT.d:49-50
  GRADE: [board-confirm]
- FACT: services/pdma/adi_pdma_2156x.h resolves to CCES 2.11.1 SHARC/include (suffix-only, no plain adi_pdma.h).
  SRC: ALT.d:46
  GRADE: [board-confirm]
- FACT: services/int/adi_int.h (interrupt service, prerequisite for SPORT DMA callbacks) is included by ALT and resolves to CCES 2.11.1 SHARC/include.
  SRC: ALT:15 (#include <services/int/adi_int.h>); ALT.d:33
  GRADE: [L1-example-called]

## NOT_FOUND
- Real BSP header bodies (adi_sport.h, adi_sport_2156x.h, adi_twi.h, adi_twi_2156x.h, adi_spu.h, adi_spu_v3.h, adi_pdma_2156x.h) -- absent locally; only on CTO Windows install tree (CCES 2.11.1 per .d; 2.12.1 per brief = version delta unconfirmed).
- Exact enum value definitions for ADI_SPORT_* / ADI_TWI_MASTER / ADI_HALF_SPORT_* / ADI_PDMA_DESCRIPTOR_LIST / ADI_SPORT_CHANNEL_PRIM -- used as tokens only; numeric values not in any local file.
- Exact numeric of MEMORY_SIZE macros (ADI_SPORT_MEMORY_SIZE / ADI_TWI_MEMORY_SIZE / ADI_SPU_MEMORY_SIZE) -- referenced symbolically only; real values in install-tree headers.
- Precise parameter TYPE names / full prototype declarations for every adi_* function -- reconstructed from call-site argument lists only; type spellings need install-tree header confirm.
- ADI_PDMA_DESC_LIST exact field declared types (ptr/uint32_t/int32_t) -- inferred from assignment RHS; struct definition not in any local non-stub file.
- adi_spu_v3.h contents / whether adi_spu.h merely forwards to it -- not local.
- Any standalone adi_pdma.h (no suffix) -- confirmed ABSENT (zero .d hits); PDMA is _2156x-only.

## VERIFIER_REPORT
- ROLE: adversarial citation verifier (REFUTE pass). Independently opened every cited source file; did NOT trust M1_SYMBOL_SURVEY.
- SCOPE OF TAGS PRESENT: file uses only [L1-example-called] (49 FACT lines across 8 sections) and [board-confirm] (header-body/install-tree facts). No [datasheet], [declared-only], or [inferred] tags exist in this file -> those refute-categories N/A here.
- CHECKED: 49 / 49 FACT lines (full census, no sampling). All [L1-example-called] call sites opened in Audio_Loopback_TDM.c (ALT) and Audio_Passthrough_I2S.c; all .d citations opened in the two Debug/src/*.d + system/drivers/twi/adi_twi.d.
- L1 CALL-SITE CENSUS (all line numbers + API names + actual args matched EXACTLY, 0 drift):
  - SPORT: Open ALT:292,295 / ConfigData 299,311 / ConfigClock 301,313 / ConfigFrameSync 303,315 (6 bool after FsDiv confirmed) / ConfigMC 305,317 (1u,7u,0u,true) / SelectChannel 307(0u,11u),319(0u,3u) / RegisterCallback 323 / DMATransfer 330,333 (ADI_PDMA_DESCRIPTOR_LIST,ADI_SPORT_CHANNEL_PRIM) / Enable 337,340 / StopDMATransfer 353,356 / Close 359,362 / SPORTCallback proto 167-172 -- all verbatim.
  - TWI: Open 513-514 / SetPrescale 520 / SetBitRate 526 / SetDutyCycle 533 / SetHardwareAddress 539,584,648 (TARGETADDR/_1962/_1979) / Write 482(2u,false),492(1u,true) / Read 499(1u,false) / Close 552 -- all verbatim.
  - SPU: Init 455 (0,SpuMemory,NULL,NULL,&ghSpu) / EnableMasterSecure 462(SPORT_4A_SPU),469(SPORT_4B_SPU) -- verbatim.
  - PDMA desc: 4 instances decl 114,115,118,119 / members 253-283 / ENUM_DMA_CFG_XCNT_INT 254,262,270,278 + cdef include ALT:21 -- verbatim.
  - codec: helpers 478-506 / init protos 152-156 + defs 560,578,622,641 / reg macros ADAU1962_PLL_CTL_CTRL0=0x00,CTRL1=0x01 in ADAU_1962Common.h used ALT:590,604 / ConfigSoftSwitches_ADAU_Reset extern ALT:59 call ALT:392 -- verbatim.
- .d / INSTALL-PATH CITATIONS (re-opened, 100% checked, > 60% bar exceeded): ALT.d:40-41 sport(API+_2156x BOTH) / 46 pdma_2156x(only) / 49-50 spu(adi_spu.h+adi_spu_v3.h, _v3 confirmed not _2156x) / 51 twi_2156x / 33 adi_int.h / 47-48,52 config headers -- all match. Passthrough .d:51-52 lists BOTH adi_twi.h+adi_twi_2156x.h -- confirmed. system/drivers/twi/adi_twi.d:25 = adi_twi.h -- confirmed. Source-include asymmetry confirmed: ALT:18 = adi_twi_2156x.h vs Passthrough:20 = adi_twi.h.
- NEGATIVE CLAIMS RE-RUN: grep "pdma/adi_pdma.h" (no suffix) across all Debug .d = exit 1 / ZERO hits (PDMA suffix-only claim holds). grep adi_adau/adi_codec in knowledge_base driver/service dirs = zero (no ADI codec driver claim holds).
- [board-confirm] JUDGMENT AUDIT: real BSP header bodies (adi_sport*/adi_twi*/adi_spu*/adi_pdma_2156x) absent locally -- only matches are sprint6/dsp/audio/guard_stub_inc/* which self-label "NOT the real BSP header" / DESKTOP-ONLY parse-stubs (verified by grep). Correctly excluded from signature evidence; correctly graded [board-confirm]. No L1-callable example was wrongly downgraded; no local real header wrongly labeled board-confirm. Distinction (functions = L1 by call site / types+enum-values+MEMORY_SIZE+header-bodies = board-confirm) is sound.
- VERSION-DELTA FLAG AUDIT: every install path in both .d files shows "CrossCore Embedded Studio 2.11.1"; task brief says 2.12.1. Fact file flags this as unverified [board-confirm] delta rather than asserting either -- honest, not fabrication.
- VERDICT: CLEAN
- MISMATCH: (none)

## SUMMARY
The Audio_Loopback_TDM example (knowledge_base/.../Audio_Loopback_TDM/src/Audio_Loopback_TDM.c) is a real ADSP-21569 ADAU1979->SPORT4 TDM->ADAU1962A loopback and gives [L1-example-called] evidence for the full SPORT/SPU/TWI/PDMA call set: adi_sport_Open/ConfigData/ConfigClock/ConfigFrameSync/ConfigMC/SelectChannel/RegisterCallback/DMATransfer/Enable/StopDMATransfer/Close (descriptor-list DMA via ADI_PDMA_DESC_LIST 7-field ring), adi_twi_Open/SetPrescale/SetBitRate/SetDutyCycle/SetHardwareAddress/Write/Read/Close, and adi_spu_Init/EnableMasterSecure. Codecs are NOT driven by any adi_adau/adi_codec driver -- they are register-level TWI bursts (Write_TWI_8bit_Reg wrappers; ADAU_19xxCommon.h reg macros). The header suffix asymmetry (R25/R31 trap) is independently re-confirmed from the .d dependency files: SPORT = adi_sport.h(API)+adi_sport_2156x.h(device) BOTH; SPU = adi_spu.h(API)+adi_spu_v3.h (note _v3, not _2156x) BOTH; TWI = adi_twi.h(API)+adi_twi_2156x.h BOTH exist but the SOURCE #include differs per example (loopback picks _2156x, passthrough picks plain); PDMA = adi_pdma_2156x.h ONLY (no plain adi_pdma.h anywhere) and is pulled in transitively. Function signatures here are argument-pattern reconstructions from L1 call sites -- exact parameter TYPES, return-enum and MEMORY_SIZE numeric values require the install-tree headers on the CTO board machine ([board-confirm]); the .d shows CCES 2.11.1 whereas the brief says 2.12.1 (version delta flagged, unverified). The local guard_stub_inc/* same-name files are explicit desktop parse-stubs and were deliberately NOT used as signature evidence.
