# M1_FACT_BASE — Audio bring-up 事实底座（ADSP-21569 / ADAU1979 ADC + ADAU1962A DAC）

> **调研型产出**：仅事实 + 来源，不写实现代码、不做架构选择、不下选型/闭合裁决。
> **用途**：供 CTO M1 架构设计输入。
> **核验状态**：经 workflow 4 路对抗引用核验（每子任务独立 adversarial citation verifier @ claude-opus-4-8 / 2026-06-06）。
> 各事实带 [来源] 与 [分级] 标签。分级五种：[L1-example-called]=例程真调用过 / [declared-only]=仅声明无例程调用 / [datasheet]=datasheet 正文-表 / [inferred]=推测（明标，不得作事实/架构依据）/ [board-confirm]=本地查无须板上确认。
> 本版替换上一轮 NO_INPUT 占位稿：四个子任务的已核验事实文件（_m1_facts_S1..S4，各带 ## VERIFIER_REPORT）已传入并据实汇总。

---

## 0. 核验记录表（从各文件 VERIFIER_REPORT 如实抄录）

| 子任务 | 源事实文件 | checked | mismatch | verdict | 备注 |
|---|---|---|---|---|---|
| S1 example_anatomy | `_m1_facts_S1_example_anatomy.md` | 42 | 0 | **CLEAN** | 33 [L1] 全开+4 [inferred]+2 [board-confirm]+1 [declared-only] judgment-checked；SoftConfig .doj/.d + main .d 7-header grep 重跑 |
| S2 symbol_inventory | `_m1_facts_S2_symbol_inventory.md` | 49 / 49（全 census 无抽样） | 0 | **CLEAN** | L1 call-site census 0 drift；负向断言（无 plain adi_pdma.h / 无 adi_adau 驱动）重跑确认；版本 delta（.d=2.11.1 vs brief 2.12.1）诚实 flag |
| S3 datasheets | `_m1_facts_S3_datasheets.md` | 43（ADC 25 / DAC 18，[datasheet] 抽核 100%） | 1（表号顺移一位，**非 FABRICATION**，内容/页号全对） | **ISSUES** | 修正已应用入文（见下）；余 42 条逐位相符 |
| S4 topology | `_m1_facts_S4_topology.md` | 49 | 0 | **CLEAN** | [L1] 全核无 ±2 修正；[datasheet] 4/4=100%；[inferred]/[declared-only]/[board-confirm] 判定均正确 |

**已应用的 VERIFIER 修正（S3 唯一 mismatch，修正后入文，原错不入）**：
- S3 `F-DAC-CMAP slot映射` 与 `F-DAC-去爆音与mute序` 中 Soft Mute 的来源标号由「Table 33/34 (P33-P34)」**更正为「Table 34/35 (P33-P34)」**（页号 P33-P34 本就正确且确含逐通道 Soft Mute；Table 33 实为 DAC_CTRL2@P32，逐通道软静音实为 Table 34=DAC_MUTE1 + Table 35=DAC_MUTE2）。本文档已按更正后表号落字（见 §3.11、§3.13）。

**被剔除项（FABRICATION）**：无。四文件均无 FABRICATION 项；S3 唯一 mismatch 经裁定为表号顺移（内容真实），按修正入文而非剔除。

---

## 1. S1 — 例程解剖（Audio_Loopback_TDM bring-up 时序）

> 路径根：`knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/`；src/ = .../src/，EZKIT/ = .../EV-SOMCRR-EZKIT/。

### 1.1 顶层 bring-up 调用序
- main() 调用序：adi_initComponents() → SPU_init() → [Switch_Configurator() **被注释掉**] → SRU_Init() → Init_TWI() → ADAU_1962_init()(DAC) → ADAU_1979_init()(ADC) → Sport_Init() → Stop_TWI()，随后 GPIO LED 设置，再进无限音频环。 [来源: src/Audio_Loopback_TDM.c:688-804] [L1-example-called]
- Switch_Configurator()（含 ConfigSoftSwitches_ADC_DAC + ConfigSoftSwitches_ADAU_Reset）已定义但 main 中调用点被注释 → SoftConfig SoftSwitch 序列**运行时不执行**（codec 上电/复位依赖板默认态）。 [来源: src/Audio_Loopback_TDM.c:701 注释；定义 :378-401] [L1-example-called]
- adi_initComponents()（自动生成）顺序运行 adi_sec_Init() → adi_initpinmux() → adi_SRU_Init()，每步以前一步 result==0 为门。 [来源: EZKIT/system/adi_initialize.c:19-33] [L1-example-called]
- Codec/SPORT init 各自 `if (Result==0u)` 门后，前级非零则跳过其余（顺序短路，非 abort）。 [来源: src/Audio_Loopback_TDM.c:695-734] [L1-example-called]

### 1.2 SPU（总线安全，SPORT DMA 前置）
- SPU_init() 调用 adi_spu_Init(0, SpuMemory, NULL, NULL, &ghSpu)，再 adi_spu_EnableMasterSecure(ghSpu, SPORT_4A_SPU, true) 与 ...(SPORT_4B_SPU, true)。 [来源: src/Audio_Loopback_TDM.c:453-476] [L1-example-called]
- SPORT_4A_SPU=57、SPORT_4B_SPU=58（SPU master 索引）。 [来源: src/Audio_Loopback_TDM.h:39-40] [L1-example-called]
- SPU memory 为 static byte 数组 uint8_t SpuMemory[ADI_SPU_MEMORY_SIZE]；句柄 ghSpu 为 static。 [来源: src/Audio_Loopback_TDM.c:145-148] [L1-example-called]
- 注（traceability，无缺陷）：代码符号是 SPORT_4A_SPU/4B_SPU(=57/58)，源注释 .c:461/468 写「SPORT 0A/0B」为 ADI 陈旧 boilerplate；事实取代码符号/值非注释。

### 1.3 SRU 片上路由
- SRU_Init() 先写 pads enable：*pREG_PADS0_DAI0_IE=0x1ffffe，*pREG_PADS0_DAI1_IE=0x1ffffe。 [来源: src/Audio_Loopback_TDM.c:417-418] [L1-example-called]
- 时钟路由：SRU2(DAI1_PB05_O,SPT4_ACLK_I)+SRU2(DAI1_PB05_O,SPT4_BCLK_I) 把 DAC 位时钟送 SPORT4A/4B 时钟输入；SRU2(DAI1_PB05_O,DAI1_PB12_I) 转发时钟给 ADC。 [来源: src/Audio_Loopback_TDM.c:422-423,432] [L1-example-called]
- 帧同步路由：SRU2(DAI1_PB04_O,SPT4_AFS_I)+...(SPT4_BFS_I) 送 DAC FS 给 SPORT4A/4B；SRU2(DAI1_PB04_O,DAI1_PB20_I) 转发 FS 给 ADC。 [来源: src/Audio_Loopback_TDM.c:425-426,435] [L1-example-called]
- 数据路由：SRU2(SPT4_AD0_O,DAI1_PB02_I) 把 SPORT4A 数据送 DAC；SRU2(DAI1_PB06_O,SPT4_BD0_I) 把 ADC 数据送进 SPORT4B 数据输入。 [来源: src/Audio_Loopback_TDM.c:429,438] [L1-example-called]
- 引脚使能（PBENxx）：PBEN05=LOW、PBEN04=LOW、PBEN02=HIGH、PBEN12=HIGH、PBEN20=HIGH、PBEN06=LOW。 [来源: src/Audio_Loopback_TDM.c:420,427,430,433,436,439] [L1-example-called]

### 1.4 TWI（codec 控制总线）打开与配置
- Init_TWI()：adi_twi_Open(TWIDEVNUM, ADI_TWI_MASTER, &TwideviceMemory[0], ADI_TWI_MEMORY_SIZE, &hTwiDevice) → SetPrescale(PRESCALEVALUE) → SetBitRate(BITRATE) → SetDutyCycle(DUTYCYCLE) → SetHardwareAddress(TARGETADDR)。 [来源: src/Audio_Loopback_TDM.c:508-546] [L1-example-called]
- TWI 常量：TWIDEVNUM=2u、BITRATE=100u(kHz)、DUTYCYCLE=50u(%)、PRESCALEVALUE=12u、TARGETADDR=0x38u、TARGETADDR_1962=0x04u(DAC)、TARGETADDR_1979=0x11u(ADC)。 [来源: src/Audio_Loopback_TDM.h:28-37] [L1-example-called]
- 单寄存器写 Write_TWI_8bit_Reg(Reg,Val)：devBuffer[0]=Reg、devBuffer[1]=Data，adi_twi_Write(hTwiDevice, devBuffer, 2u, false)。 [来源: src/Audio_Loopback_TDM.c:478-483] [L1-example-called]
- 单寄存器回读 Read_TWI_8bit_Reg(Reg)：adi_twi_Write(...,1u,true)（repeated-start，地址相）→ adi_twi_Read(..., &Rx_Data, 1u, false)。 [来源: src/Audio_Loopback_TDM.c:485-506] [L1-example-called]
- Stop_TWI() 调 adi_twi_Close(hTwiDevice)；main 在进音频环**前**关 TWI（流式期不用 TWI）。 [来源: src/Audio_Loopback_TDM.c:548-556,730-734] [L1-example-called]

### 1.5 DAC（ADAU1962A）init 与 PLL
- ADAU_1962_init() = ADAU_1962_Pllinit() + 循环 i=0..27 写 Config_array_DAC[i]（写后回读比对，mismatch 返回 FAILED）。 [来源: src/Audio_Loopback_TDM.c:560-576] [L1-example-called]
- ADAU_1962_Pllinit()：设 TWI hw addr=TARGETADDR_1962(0x04) → 写 PLL_CTL_CTRL0=0x01,(delay),=0x05,(delay) → PLL_CTL_CTRL1=0x22,(delay) → 轮询 PLL_CTL_CTRL1 bit2 ((status&0x4)>>2) 置位=PLL lock。 [来源: src/Audio_Loopback_TDM.c:578-617] [L1-example-called]
- ADAU1962 寄存器宏：PLL_CTL_CTRL0=0x00、PLL_CTL_CTRL1=0x01、PDN_CTRL_1=0x02、PDN_CTRL_2=0x03、PDN_CTRL_3=0x04、DAC_CTRL0=0x06、DAC_CTRL1=0x07、MSTR_VOL=0x0b、PAD_STRGTH=0x1C、DAC_PWR1=0x1D。 [来源: src/ADAU_1962Common.h:10-35] [L1-example-called]
- Config_array_DAC[28] 写序（Reg,Value）：PDN_CTRL_1=0x00、PDN_CTRL_2=0xff、PDN_CTRL_3=0x0f、DAC_CTRL0=0x01、DAC_CTRL1=0x01、DAC_CTRL2=0x00、DAC_MUTE1=0x0、DAC_MUTE2=0x00、MSTR_VOL=0x00、DAC1..12_VOL=0x00(12 寄存器)、PAD_STRGTH=0x00、DAC_PWR1=0xaa、DAC_PWR2=0xaa、DAC_PWR3=0xaa、PDN_CTRL_2=0x00、PDN_CTRL_3=0x00、DAC_CTRL0=0x18。 [来源: src/Audio_Loopback_TDM.c:61-91] [L1-example-called]
- PLL 写间延时用忙等 `int delay1=0xffff; while(delay1--) asm("nop;");`（无 timer/驱动，每步前重装）。 [来源: src/Audio_Loopback_TDM.c:580,591-609] [L1-example-called]

### 1.6 ADC（ADAU1979）init 与 PLL
- ADAU_1979_init() = ADAU_1979_Pllinit() + 循环 i=0..15 写 Config_array_ADC[i]（写后回读比对，mismatch 返回 FAILED）。 [来源: src/Audio_Loopback_TDM.c:622-639] [L1-example-called]
- ADAU_1979_Pllinit()：设 TWI hw addr=TARGETADDR_1979(0x11) → 写 REG_POWER=0x01、REG_PLL=0x03 → 读 REG_PLL → 轮询 REG_PLL bit7 ((status&0x80)>>7) 置位=PLL lock（环内 nop 忙等）。 [来源: src/Audio_Loopback_TDM.c:641-669] [L1-example-called]
- ADAU1979 寄存器宏：REG_POWER=0x00、REG_PLL=0x01、REG_BOOST=0x02、REG_MICBIAS=0x03、REG_BLOCK_POWER_SAI=0x04、REG_SAI_CTRL0=0x05、REG_MISC_CONTROL=0x0e。 [来源: src/ADAU_1979Common.h:11-25] [L1-example-called]
- Config_array_ADC[16] 写序（Reg,Value）：BOOST=0x00、MICBIAS=0x00、BLOCK_POWER_SAI=0x30、SAI_CTRL0=0x1B（注释「I2S 48kHz」）、SAI_CTRL1=0x08、CMAP12=0x01、CMAP34=0x23、SAI_OVERTEMP=0xf0、POST_ADC_GAIN1..4=0xA0、ADC_CLIP=0x00、DC_HPF_CAL=0x00、BLOCK_POWER_SAI=0x3f、MISC_CONTROL=0x00。 [来源: src/Audio_Loopback_TDM.c:93-111] [L1-example-called]

### 1.7 SPORT 打开与配置
- SPORT4A(TX) 打开：adi_sport_Open(SPORT_DEVICE_4A, ADI_HALF_SPORT_A, ADI_SPORT_DIR_TX, ADI_SPORT_MC_MODE, SPORTMemory4A, ADI_SPORT_MEMORY_SIZE, &hSPORTDev4ATx)。 [来源: src/Audio_Loopback_TDM.c:292] [L1-example-called]
- SPORT4B(RX) 打开：adi_sport_Open(SPORT_DEVICE_4B, ADI_HALF_SPORT_B, ADI_SPORT_DIR_RX, ADI_SPORT_MC_MODE, SPORTMemory4B, ...)；4A/4B device num 均 4u（同物理 SPORT4 两半）。 [来源: src/Audio_Loopback_TDM.c:295；宏 src/Audio_Loopback_TDM.h:26-27] [L1-example-called]
- SPORT4A TX 配置（精确实参）：ConfigData(h, ADI_SPORT_DTYPE_SIGN_FILL, 31, false,false,false)；ConfigClock(h, 32, false,false,false)；ConfigFrameSync(h, 31, false,false,false,true,false,false)；ConfigMC(h, 1u, 7u, 0u, true)；SelectChannel(h, 0u, 11u)。 [来源: src/Audio_Loopback_TDM.c:299-308] [L1-example-called]
- SPORT4B RX 配置（精确实参）：ConfigData(h, ADI_SPORT_DTYPE_SIGN_FILL, 31, ...)；ConfigClock(h, 32, ...)；ConfigFrameSync(h, 31, ...,true,false,false)；ConfigMC(h, 1u, 7u, 0u, true)；SelectChannel(h, 0u, 3u)。 [来源: src/Audio_Loopback_TDM.c:311-319] [L1-example-called]
- SelectChannel 差异：TX(4A) 选 0u..11u（DAC 最多 12 输出 slot）；RX(4B) 选 0u..3u（ADC 4 输入 slot）。 [来源: src/Audio_Loopback_TDM.c:307,319] [L1-example-called]
- SPORT static memory：uint8_t SPORTMemory4A/4B[ADI_SPORT_MEMORY_SIZE]；句柄 hSPORTDev4ATx(TX)/hSPORTDev4BRx(RX) 均 static。 [来源: src/Audio_Loopback_TDM.c:131-136] [L1-example-called]
- ConfigMC 实参 (window_size=1u, MC_count/last_active=7u, offset=0u, packed=true) 对 4A/4B 同 ⇒ 8 TDM 通道(slot 0..7)；ConfigData word=31 ⇒ 32-bit 字。 [来源: src/Audio_Loopback_TDM.c:305,317;299,311] [inferred]（slot 数读自 7u "last active channel" 实参；ConfigMC 精确语义须 adi_sport.h 原型，见 board-confirm）

### 1.8 DMA 描述符 / 回调 / 帧逻辑
- DMA 用 ADI_PDMA_DESC_LIST 结构 4 实例：TX 目的链 iDESC_LIST_1/2_SP4A；RX 源链 iSRC_LIST_1/2_SP4B。 [来源: src/Audio_Loopback_TDM.c:113-119] [L1-example-called]
- PrepareDescriptors() 建每方向 2 节点环形 ping-pong：TX iDESC_LIST_1.pNxtDscp=&2 且 2.pNxtDscp=&1（闭环）；RX 同构。 [来源: src/Audio_Loopback_TDM.c:259,267,275,283] [L1-example-called]
- 描述符字段：Config=ENUM_DMA_CFG_XCNT_INT（X 计数完成中断）、XModify=4（字节，32-bit 步进）、YCount=0、YModify=0（1-D）。TX XCount=COUNT*2（缓冲 int_SP0ABuffer1/2）；RX XCount=COUNT（int_SP0ABuffer4/5）。 [来源: src/Audio_Loopback_TDM.c:253-283] [L1-example-called]
- DMA 提交：先 RX adi_sport_DMATransfer(hSPORTDev4BRx, &iSRC_LIST_1_SP4B, DMA_NUM_DESC, ADI_PDMA_DESCRIPTOR_LIST, ADI_SPORT_CHANNEL_PRIM)，再 TX。DMA_NUM_DESC=2u。 [来源: src/Audio_Loopback_TDM.c:330-333；宏 :h:42] [L1-example-called]
- 回调仅注册在 RX：adi_sport_RegisterCallback(hSPORTDev4BRx, SPORTCallback, NULL)；TX 无回调。 [来源: src/Audio_Loopback_TDM.c:323] [L1-example-called]
- Sport_Init() 使能序：RegisterCallback(RX) → PrepareDescriptors → DMATransfer(RX) → DMATransfer(TX) → Enable(RX,true) → Enable(TX,true)。**RX 先于 TX 使能**。 [来源: src/Audio_Loopback_TDM.c:323-341] [L1-example-called]
- SPORTCallback 仅处理 case ADI_SPORT_EVENT_RX_BUFFER_PROCESSED（default 不动作）；递增 TestCallbackCount/CallbackCount。 [来源: src/Audio_Loopback_TDM.c:167-235] [L1-example-called]
- 缓冲切换由 CallbackCount 驱动：==1 拷 buf4→buf1；==2 拷 buf5→buf2 并复位 CallbackCount=0（手动 ping-pong 跟踪）。 [来源: src/Audio_Loopback_TDM.c:185-230] [L1-example-called]
- 拷贝为手动循环(i+=4,j+=8)：每 RX 4-sample 组复制进 8 TX slot（每 ADC sample 写两相邻 DAC slot），即 4-ch ADC fan-out 到 8-ch TDM DAC，i<COUNT。 [来源: src/Audio_Loopback_TDM.c:187-205,210-228] [L1-example-called]
- 回调/DMA 路径**无 cache flush/invalidate** 调用（文件内无 adi_cache_*）；回调仅直接数组拷贝。 [来源: src/Audio_Loopback_TDM.c:167-235,326-334（缺失）] [board-confirm]（是否需 L1 cache 一致性取决于放置/cache 配置，单凭源码不能确认）
- TX 描述符 XCount=COUNT*2(=600) 与 8-slot fan-out（2× RX 的 COUNT）一致。 [来源: src/Audio_Loopback_TDM.c:255,263 vs :187；COUNT=300 @ :h:24] [inferred]

### 1.9 错误处理 / 缓冲声明放置
- SPORT/SPU/DMA 用 CHECK_RESULT(eResult) 宏：非零即从所在函数 return 1（无日志）。 [来源: 宏 src/Audio_Loopback_TDM.h:48-52；用例 :293,296,300...341] [L1-example-called]
- TWI 用不同模式：比对 eResult!=ADI_TWI_SUCCESS 并 REPORT_ERROR(==printf)，但**不 return/abort**（记日志后继续）。 [来源: src/Audio_Loopback_TDM.c:515-543,493-503] [L1-example-called]
- Codec 配置循环以写-回读 mismatch 判失败，return FAILED(=-1) 并 DEBUG_INFORMATION(==printf)。 [来源: src/Audio_Loopback_TDM.c:568-572,631-635] [L1-example-called]
- main 错误模型：阶段仅在 Result==0u 时运行；GPIO 失败 printf 不停；REPORT_ERROR/DEBUG_INFORMATION 均 #define 为 printf。 [来源: src/Audio_Loopback_TDM.c:695-755；宏 :h:54-55] [L1-example-called]
- SPORT 数据缓冲为普通全局 int 数组：int_SP0ABuffer1/2[COUNT*2](TX,=600)、int_SP0ABuffer4/5[COUNT](RX,=300)；COUNT=300。 [来源: src/Audio_Loopback_TDM.c:40-43；:h:24] [L1-example-called]
- SPORT 缓冲**无 #pragma section / 放置指令**，为普通全局（默认 app.ldf 链接放置）。 [来源: src/Audio_Loopback_TDM.c:39-43（缺失）] [L1-example-called]
- 另有流式期未用的 float 缓冲 Audio_channel1..12[256] 声明为全局（未接入 SPORT/DMA 路径）。 [来源: src/Audio_Loopback_TDM.c:26-38] [L1-example-called]
- 驱动 scratch 为 static byte 数组按 MEMORY_SIZE 宏定尺寸：SPORTMemory4A/4B、TwideviceMemory、SpuMemory、devBuffer[BUFFER_SIZE=8]。 [来源: src/Audio_Loopback_TDM.c:55,131-148；BUFFER_SIZE :h:33] [L1-example-called]
- TX 缓冲字节尺寸=COUNT*2*sizeof(int)=600*4=2400 B；RX=COUNT*4=1200 B（与 XModify=4 一致）。 [来源: src/Audio_Loopback_TDM.c:40-43,256,272] [inferred]（sizeof(int)=4 SHARC 假设；算术推导）

### 1.10 编译进 object 的驱动依赖
- 主 TU 依赖文件列出实际编入的驱动头：adi_sport.h、adi_twi_2156x.h、adi_spu.h、adi_gpio.h、adi_pdma_2156x.h、adi_pdma_config_2156x.h、adi_twi_config_2156x.h（确认 SPORT/TWI/SPU/GPIO/PDMA 驱动在本 build）。 [来源: EZKIT/Debug/src/Audio_Loopback_TDM.d] [L1-example-called]
- SoftConfig 源（..._ADC_DAC.c / ..._ADAU_Reset.c）存在且编译（有 .doj/.d），但入口仅经 Switch_Configurator() 到达，而其调用在 main 被注释 → SoftConfig 路径**已声明/已构建但运行时未调用**。 [来源: EZKIT/system/SoftConfig_EV_SOMCRR_EZKIT_ADC_DAC.c:127；src/Audio_Loopback_TDM.c:701] [declared-only]

---

## 2. S2 — 符号清单（SPORT/TWI/SPU/PDMA/codec 真符号 clean-list）

> 路径前缀 ALT = `knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/src/Audio_Loopback_TDM.c`；ALT.d = .../EV-SOMCRR-EZKIT/Debug/src/Audio_Loopback_TDM.d；次核 = Audio_Passthrough_I2S。
> **关键 caveat**：真 BSP 头 BODY（adi_sport.h / adi_sport_2156x.h / adi_twi*.h / adi_spu*.h / adi_pdma_2156x.h）本地无，按 .d 在 CTO Windows install tree（.d 显示 CCES **2.11.1**；brief 称 2.12.1，version delta 未核 [board-confirm]）。本地同名 `guard_stub_inc/*` 为显式 DESKTOP-ONLY parse-stub（自标「NOT the real BSP header」），**未用作签名证据**。下列签名均由 L1 调用点实参列重建；参数 TYPE/return-enum 须 install-tree 头确认 [board-confirm]。

### 2.1 头文件后缀非对称（R25/R31 陷阱，独立从 .d 重核）
- SPORT 双头并存：drivers/sport/adi_sport.h（无后缀，API）+ drivers/sport/adi_sport_2156x.h（device 后缀）；app source #include **无后缀** <drivers/sport/adi_sport.h>。 [来源: ALT.d:40-41；ALT:16] [L1-example-called]
- SPU 双头但后缀为 **_v3 非 _2156x**：services/spu/adi_spu.h（API）+ services/spu/adi_spu_v3.h（impl）；app #include 无后缀 <services/spu/adi_spu.h>。 [来源: ALT.d:49-50；ALT:17] [L1-example-called]
- TWI 双头并存：drivers/twi/adi_twi.h + drivers/twi/adi_twi_2156x.h，install tree **两者都在**。 [来源: ALT.d:51；Audio_Passthrough_I2S.d:51-52；system/drivers/twi/adi_twi.d:25] [L1-example-called]
- TWI source-include 选择**逐例程不同**：Audio_Loopback_TDM #include _2156x 后缀变体，Audio_Passthrough_I2S #include 无后缀变体（两者均编译）。 [来源: ALT:18 vs Audio_Passthrough_I2S/src/Audio_Passthrough_I2S.c:20] [L1-example-called]
- PDMA **仅** 后缀头 services/pdma/adi_pdma_2156x.h —— 任何 .d 无 plain adi_pdma.h；且为**传递引入**（app source 无直接 #include 任何 pdma 头）。 [来源: ALT.d:46；grep "pdma/adi_pdma.h" 跨所有 .d=零命中；ALT:10-24] [L1-example-called]
- 逐驱动 config 头（编译期生成，**非 API**）本地有 BODY：adi_sport_config_2156x.h、adi_twi_config_2156x.h、adi_pdma_config_2156x.h —— 均 _2156x 后缀，是 sport/twi/pdma 唯一本地有 body 的 .h。 [来源: ALT.d:47-48,52；本地 .../system/drivers/sport/adi_sport_config_2156x.h] [L1-example-called]

### 2.2 SPORT 函数（签名=L1 调用点实参模式；参数 TYPE [board-confirm]）
- adi_sport_Open(uint32_t nDevNum, ADI_SPORT_CHANNEL(half A/B), ADI_SPORT_DIRECTION(TX/RX), ADI_SPORT_TYPE(MC), void* pMemory, uint32_t nMemSize, ADI_SPORT_HANDLE* phDevice) → ADI_SPORT_RESULT。 [来源: ALT:292,295] [L1-example-called]
- adi_sport_ConfigData(h, ADI_SPORT_DATA_TYPE, uint8_t WordLen, bool, bool, bool)；调用 (h, ADI_SPORT_DTYPE_SIGN_FILL, 31, false,false,false)。 [来源: ALT:299,311] [L1-example-called]
- adi_sport_ConfigClock(h, uint32_t ClockRatio/ClkDiv, bool, bool, bool)；调用 (h, 32, false,false,false)。 [来源: ALT:301,313] [L1-example-called]
- adi_sport_ConfigFrameSync(h, uint32_t FsDiv, bool×6)；调用 (h, 31, false,false,false,true,false,false)。 [来源: ALT:303,315] [L1-example-called]
- adi_sport_ConfigMC(h, uint8_t nMFD, uint8_t nWindowSize, uint8_t nWindowOffset, bool bEnable)；调用 (h, 1u, 7u, 0u, true)（window 7u ⇒ 8 TDM slots）。 [来源: ALT:305,317] [L1-example-called]
- adi_sport_SelectChannel(h, uint8_t nStartCh, uint8_t nEndCh)；TX (h,0u,11u) / RX (h,0u,3u)。 [来源: ALT:307,319] [L1-example-called]
- adi_sport_RegisterCallback(h, ADI_CALLBACK pfCallback, void* pCBParam)；调用 (hSPORTDev4BRx, SPORTCallback, NULL)。 [来源: ALT:323] [L1-example-called]
- adi_sport_DMATransfer(h, void* pDescList, uint32_t nNumDesc, ADI_SPORT_DMA_XFER_MODE, ADI_SPORT_CHANNEL_TYPE)；调用 (h, &iSRC_LIST_1_SP4B, DMA_NUM_DESC, ADI_PDMA_DESCRIPTOR_LIST, ADI_SPORT_CHANNEL_PRIM)。 [来源: ALT:330,333] [L1-example-called]
- adi_sport_Enable(h, bool)；调用 (h, true)。 [来源: ALT:337,340] [L1-example-called]
- adi_sport_StopDMATransfer(h)；adi_sport_Close(h)。 [来源: ALT:353,356,359,362] [L1-example-called]
- SPORT 回调原型 = ADI_CALLBACK = void SPORTCallback(void* pAppHandle, uint32_t nEvent, void* pArg)；内部 switch(nEvent)。 [来源: ALT:167-172] [L1-example-called]

### 2.3 SPORT 枚举/宏（L1 token；底层 enum/define 值 [board-confirm]）
- ADI_SPORT_MEMORY_SIZE（数组尺寸）、ADI_SPORT_HANDLE（不透明句柄）、ADI_SPORT_RESULT（状态型）。 [来源: ALT:131-132,135-136,176,289,350] [L1-example-called]
- 作实参的枚举 token：ADI_HALF_SPORT_A/B、ADI_SPORT_DIR_TX/RX、ADI_SPORT_MC_MODE、ADI_SPORT_DTYPE_SIGN_FILL、ADI_SPORT_CHANNEL_PRIM、ADI_PDMA_DESCRIPTOR_LIST。 [来源: ALT:292,295,299,330,333] [L1-example-called]
- ADI_SPORT_EVENT_RX_BUFFER_PROCESSED = 例程处理的回调 nEvent case。 [来源: ALT:181] [L1-example-called]

### 2.4 PDMA 描述符（ADI_PDMA_DESC_LIST，字段由成员赋值证）
- ADI_PDMA_DESC_LIST = 链式 SPORT DMA 描述符结构，实例为普通对象。 [来源: ALT:114-119（4 实例）] [L1-example-called]
- L1 写入字段：.pStartAddr、.Config(=ENUM_DMA_CFG_XCNT_INT)、.XCount、.XModify、.YCount、.YModify、.pNxtDscp（自引用 next 指针，环链 1<->2）。 [来源: ALT:253-283] [L1-example-called]
- ENUM_DMA_CFG_XCNT_INT 作 .Config 值（X-count 中断），system/cdef 级枚举，经 cdef21569.h/pdma config 引入。 [来源: ALT:254,262,270,278；ALT:21] [L1-example-called]
- ADI_PDMA_DESC_LIST 类型符号从 install-tree services/pdma/adi_pdma_2156x.h（传递，后缀-only）解析。 [来源: ALT.d:46] [board-confirm]

### 2.5 TWI 函数（codec 控制总线）
- adi_twi_Open(uint32_t nDevNum, ADI_TWI_MODE, void* pMemory, uint32_t nMemSize, ADI_TWI_HANDLE* phDevice)；调用 (TWIDEVNUM, ADI_TWI_MASTER, &TwideviceMemory[0], ADI_TWI_MEMORY_SIZE, &hTwiDevice)。 [来源: ALT:513-514] [L1-example-called]
- adi_twi_SetPrescale / SetBitRate / SetDutyCycle(h, uint32_t)。 [来源: ALT:520,526,533] [L1-example-called]
- adi_twi_SetHardwareAddress(h, uint32_t)；调用 TARGETADDR / _1962 / _1979（每 codec burst 前重定向）。 [来源: ALT:539,584,648] [L1-example-called]
- adi_twi_Write(h, void* pData, uint32_t nNumBytes, bool bRepeatStart)；(h,devBuffer,2u,false) 写 reg+val；(h,devBuffer,1u,true) 地址相 repeat-start。 [来源: ALT:482,492] [L1-example-called]
- adi_twi_Read(h, void*, uint32_t, bool)；调用 (h, &Rx_Data, 1u, false)。 [来源: ALT:499] [L1-example-called]
- adi_twi_Close(h)。 [来源: ALT:552] [L1-example-called]
- TWI 类型/宏 token：ADI_TWI_HANDLE、ADI_TWI_RESULT、ADI_TWI_SUCCESS、ADI_TWI_MASTER、ADI_TWI_MEMORY_SIZE。 [来源: ALT:139,142,487,493,513-514] [L1-example-called]

### 2.6 SPU 函数
- adi_spu_Init(uint32_t nDevNum, void* pMemory, <2 ptr, 例程 NULL,NULL>, ADI_SPU_HANDLE* phDevice)；调用 (0, SpuMemory, NULL, NULL, &ghSpu)。 [来源: ALT:455] [L1-example-called]
- adi_spu_EnableMasterSecure(h, uint32_t nMasterID, bool)；调用 (ghSpu, SPORT_4A_SPU, true) / (ghSpu, SPORT_4B_SPU, true)。 [来源: ALT:462,469] [L1-example-called]
- SPU 类型/宏：ADI_SPU_HANDLE、ADI_SPU_RESULT、ADI_SPU_SUCCESS、ADI_SPU_MEMORY_SIZE。 [来源: ALT:145,148,455,462] [L1-example-called]
- SPU API 从 install-tree services/spu/adi_spu.h(+adi_spu_v3.h impl) 解析；原型/return-enum body 本地无。 [来源: ALT.d:49-50] [board-confirm]

### 2.7 codec（无 ADI codec 驱动，纯 TWI 寄存器）
- **无** ADI codec 驱动（无 adi_adau*/adi_codec* 符号）；codec 由 raw TWI 8-bit 寄存器写（Write_TWI_8bit_Reg/Read 包 adi_twi_Write/Read）。 [来源: ALT:478-506；grep adi_adau/adi_codec 跨 knowledge_base driver/service=零命中] [L1-example-called]
- codec bring-up 入口（static app 级非 BSP）：ADAU_1962_init/ADAU_1962_Pllinit/ADAU_1979_init/ADAU_1979_Pllinit。 [来源: ALT:152-156,560,578,622,641] [L1-example-called]
- codec 寄存器宏头本地有：ADAU_1962Common.h / ADAU_1979Common.h。 [来源: .../Audio_Loopback_TDM/src/ADAU_1962Common.h, ADAU_1979Common.h；用 ALT:590,604] [L1-example-called]
- 外部 soft-switch reset hook（板 mux，非 codec）：ConfigSoftSwitches_ADAU_Reset(void) 在 init 调用。 [来源: ALT:59,392] [L1-example-called]

### 2.8 include 路径（.d 权威定位；install-tree 非本地）
- drivers/sport/adi_sport.h + adi_sport_2156x.h → CCES 2.11.1 SHARC/include。 [来源: ALT.d:40-41] [board-confirm]
- drivers/twi/adi_twi.h + adi_twi_2156x.h → CCES 2.11.1 SHARC/include。 [来源: Audio_Passthrough_I2S.d:51-52；ALT.d:51] [board-confirm]
- services/spu/adi_spu.h + adi_spu_v3.h → CCES 2.11.1 SHARC/include。 [来源: ALT.d:49-50] [board-confirm]
- services/pdma/adi_pdma_2156x.h → CCES 2.11.1（后缀-only，无 plain adi_pdma.h）。 [来源: ALT.d:46] [board-confirm]
- services/int/adi_int.h（中断服务，SPORT DMA 回调前置）被 ALT include。 [来源: ALT:15;ALT.d:33] [L1-example-called]

---

## 3. S3 — codec datasheet 寄存器序事实

> 源 PDF：`knowledge_base/ezkit/bsp/datasheets/adau1979.pdf`（Rev. A, 42 页）+ `.../ADAU1962A.pdf`（Rev. A, 48 页）。表号优先；页号为 pdftotext -layout 物理页，与页脚「Rev. A | Page N of M」核对一致。

### 3.1 ADAU1979（ADC）— I2C 地址
- ADC 控制口默认上电即 I2C 模式；拉 CLATCH 连续 3 次低可切 SPI；I2C 下为纯从机。 [来源: adau1979.pdf P21「I2C MODE」] [datasheet]
- 7-bit 器件地址固定形态 xx10001：Bit7=ADDR1 引脚、Bit6=ADDR0 引脚；第一字节 Bit0=R/W。 [来源: adau1979.pdf Table 11 (P21)] [datasheet]
- 四个可选地址：0x11/0x31/0x51/0x71；0x11=ADDR1/ADDR0 均低。 [来源: adau1979.pdf P21] [datasheet]
- 控制口寄存器全 8-bit 宽，地址 0x00..0x1A。 [来源: adau1979.pdf P21] [datasheet]

### 3.2 ADAU1979 — 上电与复位序
- 单 3.3V 供电，内部 LDO 生 1.8V DVDD；POR 监视 DVDD，达 1.2V 释放内部复位。 [来源: adau1979.pdf P12 + Figure 13] [datasheet]
- PD/RST(Pin6) 拉高后给 CEXT 充电，tC=ROUT×CEXT(ROUT≈20Ω)；CEXT=10µF 时 tC≈200µs；建议等 ≥tC 再发控制信号。 [来源: adau1979.pdf P12] [datasheet]
- 硬复位 PD/RST 拉低须保持 tD=1.32×RINT×CEXT(RINT≈64kΩ)，10µF 时 tD≈0.845s；并联 REXT(典型 3kΩ) 可缩到 ≈37.8ms。 [来源: adau1979.pdf P12-P13] [datasheet]
- 软复位 S_RST=Reg 0x00(M_POWER) Bit7（复位全部到默认）；上下电循环不强制需软复位。 [来源: adau1979.pdf Table 17 (P27) + P13] [datasheet]
- 主上电 PWUP=Reg 0x00 Bit0，须置 1 上电；M_POWER 复位值 0x00。 [来源: adau1979.pdf Table 17 (P27) + Table 16 (P26)] [datasheet]

### 3.3 ADAU1979 — PLL 配置与锁判据
- PLL 由 Reg 0x01(PLL_CONTROL) 配置，复位值 0x41。 [来源: adau1979.pdf Table 18 (P28) + Table 16 (P26)] [datasheet]
- 锁判据 PLL_LOCK=Reg 0x01 Bit7（只读，1=已锁）；建议读此位确认后再解静音。 [来源: adau1979.pdf Table 18 (P28) + P13] [datasheet]
- PLL_MUTE=Bit6（复位 1，失锁自动静音）；CLK_S=Bit4（0=MCLK 作 PLL 输入，1=LRCLK，LRCLK 仅 32k..192k）。 [来源: adau1979.pdf Table 18 (P28)] [datasheet]
- MCS=Bits[2:0]（复位 001=256×fS）：000=128× / 001=256× / 010=384× / 011=512× / 100=768×；101-111=Reserved。 [来源: adau1979.pdf Table 18 (P28)] [datasheet]
- LRCLK 模式时串口须配从机、帧时钟由主器件喂；改 PLL 设置强烈建议先禁 PLL、改、再使能。 [来源: adau1979.pdf P13] [datasheet]

### 3.4 ADAU1979 — 时钟要求（MCLK / 256×fS）
- 电气表条件锚点 = 主时钟 12.288 MHz(48kHz fS, 256×fS)；PLL 锁定时间最大 10 ms；MCLKIN 占空 40-60%。 [来源: adau1979.pdf P3 + P5] [datasheet]
- 48kHz fS 下 MCLKIN vs MCS：128×=6.144 / 256×=12.288 / 384×=18.432 / 512×=24.576 / 768×=36.864 MHz。 [来源: adau1979.pdf Table 9 (P13)] [datasheet]

### 3.5 ADAU1979 — TDM8 与 SAI 字段
- TDM 编程寄存器组 = Reg 0x05..0x08（slot 宽/数据宽/通道分配/输出引脚）。 [来源: adau1979.pdf P18 + Table 16 (P26)] [datasheet]
- SAI 字段 = Reg 0x05(SAI_CTRL0) Bits[5:3]：000=Stereo/001=TDM2/010=TDM4/**011=TDM8**/100=TDM16。 [来源: adau1979.pdf Table 20 (P30)] [datasheet]
- SAI_CTRL0(0x05) 其余：SDATA_FMT=Bits[7:6]（00=I2S/01=LJ/10=RJ24/11=RJ16）；FS=Bits[2:0]（000=8-12k/001=16-24k/010=32-48k/011=64-96k/100=128-192k）；复位 0x02。 [来源: adau1979.pdf Table 20 (P30) + Table 16 (P26)] [datasheet]
- SAI_CTRL1(0x06)（复位 0x00）：SDATA_SEL=Bit7（仅 TDM4+）；SLOT_WIDTH=Bits[6:5]（00=32 BCLK/slot,01=24,10=16,11=Reserved）；DATA_WIDTH=Bit4（0=24-bit/1=16-bit）；LR_MODE=Bit3；SAI_MSB=Bit2（0=MSB first）；BCLKRATE=Bit1（仅主模式）；SAI_MS=Bit0（0=从/1=主）。 [来源: adau1979.pdf Table 21 (P31)] [datasheet]
- 通道→slot 映射 = SAI_CMAP12(0x07)(复位 0x10)/SAI_CMAP34(0x08)(复位 0x32)，每 4-bit 0000=Slot1...1111=Slot16（TDM8+ 才用 Slot5-8）。 [来源: adau1979.pdf Table 22 (P32) + Table 16 (P26)] [datasheet]
- 默认串行从 SDATAOUT1 输出；SDATA_SEL(0x06 Bit7) 可改 SDATAOUT2；未用 slot 期间输出高阻。 [来源: adau1979.pdf P18] [datasheet]

### 3.6 ADAU1979 — 关键默认值与通道结构
- 复位默认（Table 16, P26）：0x00=0x00 / 0x01=0x41 / 0x04=0x3F / 0x05=0x02 / 0x06=0x00 / 0x07=0x10 / 0x08=0x32 / 0x0E=0x02。 [来源: adau1979.pdf Table 16 (P26)] [datasheet]
- BLOCK_POWER_SAI(0x04, 复位 0x3F)：Bit7=LR_POL, Bit6=BCLKEDGE, Bit5=LDO_EN, Bit4=VREF_EN, Bits[3:0]=ADC_EN4..1（各 1=该通道使能）。 [来源: adau1979.pdf Table 16 (P26) + Table 19 (P29)] [datasheet]
- 4 通道 Σ-Δ ADC（两组立体声）；SDATAOUT1=L1/R1、SDATAOUT2=L2/R2；SUM_MODE(0x0E Bits[7:6]) 可两路求和(+3dB)/四路(+6dB)。 [来源: adau1979.pdf P8 + P16] [datasheet]

### 3.7 ADAU1979 — TDM8 自洽（推导）
- TDM8 + SLOT_WIDTH=00(32 BCLK/slot)@48kHz ⇒ BCLK=8×32×48k=12.288 MHz=256×fS，与 codec 原生 TDM8/256×fS 一致。 [来源: adau1979.pdf Table 20+21 (P30-31) 字段推算；数值对齐 Table 9 (P13)] [inferred]

### 3.8 ADAU1962A（DAC）— I2C 地址
- I2C 地址 = 内建 0x04 + ADDR1/ADDR0 引脚，可寻址四片：00→0x04 / 01→0x24 / 10→0x44 / 11→0x64。 [来源: ADAU1962A.pdf Table 15 (P16) + P16] [datasheet]
- SDA 开漏需 2kΩ 上拉；SCL 高且 SDA 拉低=start；数据字前 8 bit=器件地址+R/W。 [来源: ADAU1962A.pdf P16] [datasheet]

### 3.9 ADAU1962A — 上电与复位序
- 供电次序：先 AVDDx 与 IOVDD，再 DVDD（AVDDx 稳定且 IOVDD 在调压 10% 内才加 DVDD）。 [来源: ADAU1962A.pdf P16] [datasheet]
- PU/RST 经外阻拉低、供电稳后驱高；拉低时进 <3µA 低功耗、全功能禁用；驱高后须 **300 ms** 稳定；之后 DAC_CTRL0 MMUTE 须翻转才工作。 [来源: ADAU1962A.pdf P16] [datasheet]
- 标准 5 步启动：1)加电；2)PU/RST 驱高；3)PUP=1；4)编程全部目标寄存器；5)MMUTE=0 解全静音。 [来源: ADAU1962A.pdf P16] [datasheet]
- PUP=PLL_CLK_CTRL0(0x00) Bit0，须作第一条寄存器写置 1；置 0 进 idle 保留设置。 [来源: ADAU1962A.pdf Table 25 (P25) + P16] [datasheet]
- SOFT_RST=PLL_CLK_CTRL0(0x00) Bit3（复位除 I2C/SPI 与 Reg 0x00/0x01 外全部；不产生爆音）。 [来源: ADAU1962A.pdf Table 25 (P25) + P16] [datasheet]

### 3.10 ADAU1962A — PLL/时钟控制与锁判据
- PLL/时钟控制 = PLL_CLK_CTRL0(0x00, 复位 0x00) + PLL_CLK_CTRL1(0x01, 复位 0x2A)；PU/RST 驱高后即可编程。 [来源: ADAU1962A.pdf Table 24 (P24) + Table 25/26 (P25-26) + P15] [datasheet]
- PLL_CLK_CTRL0(0x00)：PLLIN=Bits[7:6]（00=MCLKI/XTALI, 01=DLRCLK）；XTAL_SET=Bits[5:4]（00=晶振使能, 11=XTALO 关）；MCS=Bits[2:1]（00=256×/01=384×/10=512×/11=768× @44.1/48k）。 [来源: ADAU1962A.pdf Table 25 (P25)] [datasheet]
- 锁判据 PLL_LOCK=PLL_CLK_CTRL1(0x01) Bit2（只读，0=未锁/1=已锁）。 [来源: ADAU1962A.pdf Table 26 (P26) + P15] [datasheet]
- PLL_CLK_CTRL1(0x01, 复位 0x2A) 其余：LOPWR_MODE=Bits[7:6]；MCLKO_SEL=Bits[5:4]（复位 10）；PLL_MUTE=Bit3（复位 1）；VREF_EN=Bit1（复位 1）；CLK_SEL=Bit0（0=MCLK 取自 PLL，1=直取 MCLKI/XTALI）。 [来源: ADAU1962A.pdf Table 26 (P26)] [datasheet]
- 直接主时钟模式(CLK_SEL=1) 须 MCLKI 喂 512×fS(48k 参考)并关 PLL；PLL 模式 fMCLK 6.9-40.5 MHz，锁定时间最大 10 ms。 [来源: ADAU1962A.pdf P15 + P6] [datasheet]

### 3.11 ADAU1962A — DAC_CTRL 与 TDM8 / slot 机制
- DAC_CTRL0(0x06, 复位 0x01)：SDATA_FMT=Bits[7:6]；SAI=Bits[5:3]（000=Stereo/001=TDM2/010=TDM4/**011=TDM8**/100=TDM16）；FS=Bits[2:1]；MMUTE=Bit0（复位 1=全静音, 0=正常）。 [来源: ADAU1962A.pdf Table 31 (P30) + Table 24 (P24)] [datasheet]
- DAC_CTRL1(0x07, 复位 0x00)：BCLK_GEN=Bit7；LRCLK_MODE=Bit6；LRCLK_POL=Bit5；SAI_MSB=Bit4；BCLK_RATE=Bit2（0=32/帧,1=16）；BCLK_EDGE=Bit1；SAI_MS=Bit0（0=从/1=主）。 [来源: ADAU1962A.pdf Table 32 (P31)] [datasheet]
- DAC_CTRL2(0x08, 复位 0x06)：BCLK_TDMC=Bit4（0=32 BCLK/slot,1=16）；DAC_POL=Bit3；AUTO_MUTE_EN=Bit2（复位 1=1024 连续零样本自动静音，逐通道）；DAC_OSR=Bit1（0=256×,1=128×）；DE_EMP_EN=Bit0。 [来源: ADAU1962A.pdf Table 33 (P32)] [datasheet]
- ADAU1962A 共 12 路 DAC；寄存器图(Table 24) **无独立 per-channel CMAP 路由寄存器** —— slot→通道为按 TDM 模式固定顺序分配（非可编程映射），由 Table 23 规定。 [来源: ADAU1962A.pdf Table 24 (P24) + Table 23 (P22)] [datasheet]
- TDM8 模式(SAI=011) 固定 slot 线序(Table 23)：DSDATA1 承载 Channel 1..8，DSDATA2 承载 Ch 9..12，DSDATA3-6 不用；TDM8 最大采样率 96 kHz。 [来源: ADAU1962A.pdf Table 23 (P22)] [datasheet]
- 12 路各有独立软静音：DAC_MUTE1(0x09) DAC01..08_MUTE、DAC_MUTE2(0x0A) DAC09..12_MUTE（复位 0）；独立音量 DACxx_VOL(0x0C..0x17)+主音量 DACMSTR_VOL(0x0B)；上下电 DAC_POWERx(0x1D-0x1F, 复位 0xAA)。 [来源: ADAU1962A.pdf Table 24 (P24) + **Table 34/35 (P33-P34)**] [datasheet] *(来源表号经 S3 VERIFIER 修正：原标 33/34→34/35；页号/内容本就正确)*

### 3.12 ADAU1962A — 8-of-12 路由机制（推导）
- 「8-of-12 路由」= 单条 TDM8 数据线上取 DSDATA1 前 8 个 slot(Ch 1..8) 喂 8 路功放；哪 8 路上板由数据线选择+slot 顺序决定，非寄存器重映射。**具体上板 8/12 选哪几路属架构/接线决策，本调研不裁。** [来源: ADAU1962A.pdf Table 23 (P22) 机制；取值留架构] [inferred]

### 3.13 ADAU1962A — 去爆音与 mute 序
- 去爆音/静音序要点：(a)PU/RST 驱高后等 300 ms；(b)第 5 步置 MMUTE(DAC_CTRL0 Bit0)=0（先编程后解静音）；(c)SOFT_RST 翻转无爆音；(d)逐通道 Soft Mute（软静音非硬切）；(e)支持 autoramp(log 音量斜坡)+clickless mute。 [来源: ADAU1962A.pdf P16 + P1 Features + **Table 34/35**] [datasheet] *(来源表号经 S3 VERIFIER 修正：原标 33/34→34/35)*
- AUTO_MUTE_EN(DAC_CTRL2 Bit2, 复位 1) 在 1024 连续零样本时逐通道自动静音 —— bring-up 送测零数据会自动静音，须注意。 [来源: ADAU1962A.pdf Table 33 (P32)] [datasheet]

### 3.14 两片时钟拓扑约束（datasheet 侧）
- 各片 SAI_MS 位决定本片串口主从：ADAU1979 SAI_CTRL1(0x06) Bit0、ADAU1962A DAC_CTRL1(0x07) Bit0（0=从/1=主）。同一 TDM 总线只能一个主器件出 BCLK/LRCLK，其余（含 SHARC SPORT）须配从。**哪片当主属板级接线决策，datasheet 只给约束。** [来源: adau1979.pdf Table 21 (P31) + ADAU1962A.pdf Table 32 (P31)] [datasheet]
- 12.288 MHz 三种来源：(1)外部主时钟直喂 MCLKIN/MCLKI(PLL MCS=256×fS@48k)；(2)ADAU1962A 用晶振由内部反相器起振(XTAL_SET=00)、经 MCLKO 缓冲输出供 ADC；(3)PLL 从 LRCLK/DLRCLK 反推(ADC CLK_S=1 / DAC PLLIN=01)。 [来源: ADAU1962A.pdf P15/P16 + adau1979.pdf P13 + Table 9 (P13)] [datasheet]

---

## 4. S4 — 拓扑（SPORT4 + slot 映射 + 主从时钟 + M2/FIRA 接口预留）

> 主参考 DOC-S4-IO-01 = `sprint4/audio_io_topology.md`；ALT = Audio_Loopback_TDM 例程。

### 4.1 SPORT4 实例 / 半端口分工 / 片上路由
- 音频 SPORT=SPORT4(device 4)，SPORT_DEVICE_4A=4u / 4B=4u 同物理 SPORT 的 A/B 两半。 [来源: ALT.h:26-27] [L1-example-called]
- 4A=Tx(发往 DAC)：adi_sport_Open(...4A, ADI_HALF_SPORT_A, ADI_SPORT_DIR_TX, MC_MODE...)。 [来源: ALT.c:292] [L1-example-called]
- 4B=Rx(自 ADC 收)：adi_sport_Open(...4B, ADI_HALF_SPORT_B, ADI_SPORT_DIR_RX, MC_MODE...)。 [来源: ALT.c:295] [L1-example-called]
- 两半均跑 ADI_SPORT_MC_MODE（TDM）。 [来源: ALT.c:292,295] [L1-example-called]
- SPU 外设号 SPORT_4A_SPU=57 / SPORT_4B_SPU=58。 [来源: ALT.h:39-40] [L1-example-called]
- 片上 SRU 路由：DAC 时钟 DAI1_PB05_O→SPT4_ACLK_I/BCLK_I；DAC FS DAI1_PB04_O→SPT4_AFS_I/BFS_I。 [来源: ALT.c:422-426] [L1-example-called]
- SPORT4A 数据出→DAC：SRU2(SPT4_AD0_O, DAI1_PB02_I)，PB02 输出使能 HIGH。 [来源: ALT.c:429-430] [L1-example-called]
- ADC 数据入→SPORT4B：SRU2(DAI1_PB06_O, SPT4_BD0_I)，PB06 设输入 LOW。 [来源: ALT.c:438-439] [L1-example-called]
- DAI1 引脚组上电使能 *pREG_PADS0_DAI1_IE=0x1ffffe（DAI0 同设 :417）。 [来源: ALT.c:418] [L1-example-called]
- SPORT4↔codec 在 carrier/SOM 上**最终物理网名级走线**（连接器脚、AD2428W-SOM 旁路实体走线）= 板级原理图 PDF 未渲染核名；例程 SRU 仅证片上 DAI 路由。 [来源: schematics/V2.1/*.pdf；DOC-S4-IO-01 G-IO3] [board-confirm]

### 4.2 8 通道 TDM slot：例程口径 vs 产品口径
- 例程 slot 窗口 = 8 slots：adi_sport_ConfigMC(h, 1u, 7u, 0u, true)，window 7u ⇒ 8 slots（4A/4B 同配）。 [来源: ALT.c:305,317] [L1-example-called]
- 例程激活范围：SelectChannel(4A,0u,11u)（Tx 12 ch DAC）/ SelectChannel(4B,0u,3u)（Rx 4 ch ADC）。 [来源: ALT.c:307,319] [L1-example-called]
- 产品锁定口径 = 8 slot×32-bit@48kHz → BCLK=8×32×48k=12.288 MHz(=256×fS)。 [来源: DOC-S4-IO-01:43,53] [inferred]（数学自洽推导，DOC 自标「非寄存器实证」）
- 该 256×fS/12.288MHz@48k 与 codec 原生 TDM8 一致（datasheet 实证：adau1979 TDM8/32bit/slot=256×fS；ADAU1962A 256×fS@48k=12.288MHz）。 [来源: adau1979.pdf TDM8 表 + ADAU1962A.pdf（survey 转引行号）] [datasheet]
- 例程 slot 位宽 32-bit：ConfigData(h,...,31,...)+ConfigClock(h,32,...)。 [来源: ALT.c ConfigData :299/:311 + ConfigClock :301/:313（critic R32 亲核坐实）；ConfigMC :305/:317 本轮亲核] [L1-example-called]（R32 F32-MINOR-2 升级：原 survey 转引行号经 critic 亲开文件核为真）
- 三处差异（均 codec 寄存器/映射选择，非阻塞）：
  - ①slot 计数/宽/fS/BCLK：产品 8slot/32bit/48k/12.288MHz 与例程一致（survey 判 SAME）。 [来源: M1_SYMBOL_SURVEY.md:77-82；底层 slot 数本轮亲核 ALT.c:305/317] [inferred]
  - ②通道映射：例程=4 ADC ch（CMAP12=0x01/CMAP34=0x23）；产品=1 路源 fan-out 到 8 路 TX slot（M2 beamformer 输出），SelectChannel 须改 0..7。属架构待定（survey G-M1-2）。 [来源: M1_SYMBOL_SURVEY.md:84,101,152；ALT.c:307,319] [inferred]
  - ③codec SAI 字段命名：例程 ADC SAI_CTRL0=0x1B 注释「I2S 48kHz」但 SPORT 跑 MC(TDM)，loopback 能工作；产品 8-amp 映射需确认 codec SAI=TDM8(011)（survey G-M1-1）。 [来源: M1_SYMBOL_SURVEY.md:83；ALT.c:98] [inferred]
- DAC 单片 ADAU1962A 12ch，产品仅用 8ch → 1 路 SPORT4 TDM 足够驱 8 路（不触发多片 DAC/2×SPORT）。 [来源: DOC-S4-IO-01:46] [inferred]（DOC 工程推理，非寄存器实证）

### 4.3 主从时钟：MCLK/BCLK/FS 出处 + PLL 路径 + 产品约束
- 例程时钟主控 = DAC(ADAU1962A)：BCLK/FS 由 DAI1_PB05/PB04 输出，扇出到 SPORT4(4A+4B) 与转发 ADC，即 DAC 出时钟，SPORT 与 ADC 均从。 [来源: ALT.c:422-426] [L1-example-called]
- DAC 时钟/FS 转发 ADC：SRU2(DAI1_PB05_O, DAI1_PB12_I)「DAC clock to ADC」+ SRU2(DAI1_PB04_O, DAI1_PB20_I)「DAC FS to ADC」，PB12/PB20 输出使能 HIGH。 [来源: ALT.c:432-436] [L1-example-called]
- DAC(ADAU1962A) PLL bring-up 序：PLL_CTL_CTRL0=0x01→0x05、PLL_CTL_CTRL1=0x22、轮询 PLL_CTL_CTRL1 bit2 锁定。256×fS@48k=12.288MHz 为 datasheet 口径。 [来源: ALT.c:590,596,604,610-613（PLL 写/轮询）；256×fS=ADAU1962A.pdf survey 转引] [L1-example-called]（PLL 写序例程实跑；256×fS 数值为 [datasheet]）
- ADC(ADAU1979) PLL bring-up：REG_PLL(0x01)=0x03、轮询 REG_PLL bit7 锁定；datasheet：PLL 接受帧时钟为参考。 [来源: ALT.c:655-663；adau1979.pdf survey 转引] [L1-example-called]（PLL 写序例程实跑；「帧时钟参考」为 [datasheet]；注：ALT.c:654 REG_POWER=0x01 与 :655 REG_PLL=0x03 为两条写，本条主张 REG_PLL=0x03+轮询 bit7 准确）
- 产品拓扑约束：保留例程「DAC 出时钟、ADC+SPORT 从同步」单时钟域口径属架构沿用；外部 MCLK 晶振源/具体频率、AD2428W-SOM 旁路下时钟物理走线 = 板级未核名。 [来源: DOC-S4-IO-01:63（G-IO3）, :61（G-IO1）] [board-confirm]

### 4.4 M2 / FIRA 接口预留（事实层，均未实现）
- FIRA 链帧口径 = FRAME 64 / 48000 Hz / 8 通道（BENCH_FS=48000, BENCH_FRAME=64；TFB8_FRAME=64, TFB8_NCH=8）。 [来源: sprint4/dsp/core_only/bench/bench_harness.h:30-31；.../src/tfb_8ch.h:32-33] [L1-example-called]（冻结源码常量，非板测）
- EQ 模块帧口径 EQ_FRAME=64 / EQ_FS_HZ=48000 / EQ_NCH=8，M2 须 _Static_assert 对齐 BENCH_FRAME/FS/DOLPH_W8_NCH（编译期断言）。 [来源: sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:38-42] [L1-example-called]
- Q31↔float 边界：FIRA 核 = 定点 Q31(bit-exact)；EQ 模块 = float32。M2 adapter 持边界转换（前 EQ：int32 Q31→float；后 limiter 每通道：float→int32 Q31 给 DAC）。转换缩放为 M2 决策，未实现。 [来源: sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:43-47, :129（gap 4）] [declared-only]
- EQ 在链中位置：master mono → eq_master_process(2-3 biquad shaping, fan-out 前一次) → fan-out×8 + 每通道聚焦分数延迟(FIRA 核) → eq_limiter_process_ch×8(阈值 T_k=T×w[k]) → 8 路功放。 [来源: sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:12-35] [declared-only]（集成意图链，未接入冻结流水线）
- limiter 阈值 t_base = 占位 [L4]（桌面 0.8 满量程），最终值待线③厂家函(Xmax/热额定)+U3 功放增益；唯一开口标量。 [来源: sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:56-58, :125-128（gap 3）] [declared-only]
- EQ 系数 = 当前 flat/unity 占位 + 2 测试 biquad；产品频带系数待 R3 消声室在轴响应(EQ_PRD:45)；接口 eq_biquad_set 已定。 [来源: sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:53-55, :122-124（gap 2）] [declared-only]

### 4.5 io-callback 探针 / buffer 放置（H2 留项）
- io-callback 探针需求（H2 [L3] 项）：SPORT RX-buffer-processed 回调 core 成本 = H2 MDMA proxy 测不到的 io item-1 份额；预留口径 5-30 MCPS [L3]，板上 CCNT bracket 升 [L1]。 [来源: sprint5/H2_PASSLINE_DERIVATION.md:104,108,110；M1_SYMBOL_SURVEY.md:157-171] [declared-only]
- io-callback 探针挂点 = SPORT RX-buffer-processed handler（ALT.c:167 SPORTCallback, event ADI_SPORT_EVENT_RX_BUFFER_PROCESSED）；off-board MCPS = cb_cyc×block-rate/1e6。 [来源: M1_SYMBOL_SURVEY.md:159-166] [inferred]（探针未实现）
- **block-rate 口径不一致点**（仅列差异）：survey 探针示例用 block-rate=FS/256=187.5Hz（对齐例程 256-sample 块）；DOC-S4-IO-01 产品帧 ISR 口径=FS/FRAME=48000/64=750Hz。两口径源不同（例程块 256 vs 产品 FRAME 64），最终随产品块大小定，**待架构**。 [来源: M1_SYMBOL_SURVEY.md:166（187.5）；sprint5/H2_WORKORDER.md:39（750Hz）；DOC-S4-IO-01:66 G-IO6] [inferred]（两数均在档，口径选择待架构，本轮不裁）
- buffer 放置约束（R24/R26 教训）：MDMA proxy 缓冲(s_bh_src/dst)与 FIRA 工作集(s_h2_fa)同处 L1 Block 0(0x2403f0..0x26ffff)→同物理块→R24 gate FAIL→须 #pragma section("seg_l1_block1") 移 proxy 到 L1 Block 1。 [来源: sprint5/audit/H2_MAP_PLACEMENT_ADJUDICATION.md:43-67, :139-148] [L1-example-called]（裁定输入为板 .map [L1]+.ldf [L1]；.map 重读待 bring-up）
- buffer 放置对 M1/M2：例程 SPORT ping-pong 缓冲默认落 L1 Block 0(uncached→无须 flush)；若 M2 beamformer 工作集与 SPORT 缓冲同居 Block 0，bring-up 应将 SPORT 缓冲 pin 到 seg_l1_block1 并重读 .map。 [来源: M1_SYMBOL_SURVEY.md:107-118；H2_MAP_PLACEMENT_ADJUDICATION.md:68-89] [inferred]（M2/SPORT 共置与否未定）
- #pragma section("seg_l1_block1") 形式 + 段名 = ADI FIRA/IIRA accelerator 例程实证([L1])，路由到 mem_block1_bw(app.ldf:460)。 [来源: H2_MAP_PLACEMENT_ADJUDICATION.md:103-117（引 IIR_Throughput_21569_V2.c:23-30）] [inferred]（H2 裁定转引 ADI 例程，本轮未亲开 IIRA 例程原文）

---

## 5. NOT_FOUND 汇总（扫不到，本地不可闭，未编）

> 来源：四子任务各 NOT_FOUND 小节合并（去重）。

- S1/S2/S4: adi_sport_ConfigMC / ConfigData / ConfigFrameSync / ConfigClock / SelectChannel **精确原型与各形参语义**（每 bool/int 实参含义、count-vs-index 约定）—— adi_sport.h 在 install tree，本地无。
- S1/S2/S4: ADI_SPORT_MEMORY_SIZE / ADI_TWI_MEMORY_SIZE / ADI_SPU_MEMORY_SIZE **数值**（用作数组尺寸）—— install-tree 头，本地无。
- S1/S2: 各枚举 token **数值定义**（ADI_HALF_SPORT_A/B、ADI_SPORT_DIR_TX/RX、ADI_SPORT_MC_MODE、ADI_SPORT_DTYPE_SIGN_FILL、ADI_SPORT_CHANNEL_PRIM、ADI_PDMA_DESCRIPTOR_LIST、ADI_SPORT_EVENT_RX_BUFFER_PROCESSED、ENUM_DMA_CFG_XCNT_INT、ADI_TWI_MASTER）—— 仅作 token 用，数值在 install-tree/cdef21569.h。
- S2: 真 BSP 头 BODY（adi_sport*.h / adi_twi*.h / adi_spu*.h / adi_pdma_2156x.h）—— 本地仅 guard_stub_inc/* 桌面 stub（非真头）。
- S2: ADI_PDMA_DESC_LIST 各字段**声明类型**（ptr/uint32_t/int32_t）—— 由赋值 RHS 推断，struct 定义本地无非-stub 处。
- S2: adi_spu_v3.h 内容 / adi_spu.h 是否仅 forward —— 本地无。
- S2: 任何无后缀 adi_pdma.h —— 确认 **ABSENT**（零 .d 命中），PDMA 仅 _2156x。
- S1: adi_gpio init/Open —— 例程调 SetDirection 但无可见 adi_gpio_Init；是否在 adi_initComponents/pinmux 内做需 install gpio service 源。
- S1: ADAU1962/1979 datasheet 页/表号背书具体寄存器值（为何 PLL_CTL_CTRL1=0x22、SAI_CTRL0=0x1B 选 48kHz I2S）—— 本子任务未交叉引 codec datasheet（S3 已独立覆盖大部分）。
- S3: ADAU1962A 无独立 per-channel CMAP/slot 重映射寄存器（slot→通道为 Table 23 固定顺序）—— 故无「CMAP 寄存器取值」可列（机制已说清，非缺失）。
- S3: ADAU1979 PLL 锁后到可解静音的「建议额外等待时间」无具体数值（仅「Lock Time 最大 10 ms」+「读 PLL_LOCK 后再解静音」定性）。
- S3/S4: 两片在本 EZKIT 实际主/从角色 与 12.288 MHz 实际物理来源（SPORT vs codec vs 板载晶振）—— datasheet 无本板记载（亦入 board-confirm）。
- S4: 板级原理图 PDF（schematics/V2.1/V1.2/V1.0）内 SPORT4↔codec 外部网名级连线 / AD2428W-SOM 物理旁路走线 —— PDF 未渲染核名。
- S4: 外部 MCLK 晶振源具体器件/频率 —— 例程仅写 codec PLL 内部生成 256×fS，片外参考晶振未现身。
- S4: 例程实际采样率寄存器解码值（确认例程真跑 48k 而非仅 datasheet 支持）—— G-IO1，本地无寄存器 dump。
- S4: adau1979.pdf/ADAU1962A.pdf 内 TDM/PLL 原文行号本轮未重抽（沿用 survey 转引行号+表/节锚；S3 已用表号优先重锚）。

---

## 6. [board-confirm] 汇总（CTO 板上须确认清单）

> 凡依赖 install 版 CCES include 树（CTO Windows 板机）或板上原理图/示波器才能确认者集中于此，一目了然。

**A. install-tree 头（CCES 版本与头名）**
1. CCES 版本核：.d 全部显示 **2.11.1**，brief 称 **2.12.1** —— version delta 未核，须 grep 安装版 2.12.1 SHARC/include 确认头名是否漂移。 [来源: ALT.d 各 install 路径；M1_SYMBOL_SURVEY.md:143]
2. 头文件后缀非对称（R25 adi_mdma 9-error 类陷阱）：逐驱动核 2.12.1 确切头名 —— SPORT(adi_sport.h+adi_sport_2156x.h 并存)/SPU(adi_spu.h+adi_spu_v3.h，注 _v3 非 _2156x)/TWI(adi_twi.h+adi_twi_2156x.h 并存，源 #include 逐例程不同)/PDMA(仅 adi_pdma_2156x.h)，不得假设 2.11.1 名通用。 [来源: M1_SYMBOL_SURVEY.md:144；S2 §2.1]
3. ADI_SPORT_MEMORY_SIZE / ADI_TWI_MEMORY_SIZE / ADI_SPU_MEMORY_SIZE **数值** —— 安装版头解析。 [来源: M1_SYMBOL_SURVEY.md:145]
4. adi_sport_ConfigMC / ConfigFrameSync 对「8-slot」**形参语义**（ALT 用 7u 表 8 slots，验 count-vs-index 约定）。 [来源: M1_SYMBOL_SURVEY.md:146]
5. 全部 adi_* 函数**精确参数 TYPE/return-enum** + 各枚举 token **数值** + ADI_PDMA_DESC_LIST struct 字段类型 —— install-tree 头确认。 [来源: S2 NOT_FOUND]

**B. codec 寄存器/映射（datasheet 已给约束，本板取值待定）**
6. codec SAI 字段 = TDM8(SAI=011) 用于 8ch + DAC slot/CMAP 8-of-12 映射 —— datasheet adau1979 Reg 0x05-0x08 + ADAU1962A DAC_CTRL/slot 在 bring-up 核（G-M1-1/G-M1-3）。 [来源: M1_SYMBOL_SURVEY.md:147,151-153]
7. 8ch→ADAU1962A 通道映射 + →8 路 A/B 物理连线（哪 DAC ch 驱哪路功放/哪对喇叭）= 产品布线设计，文档无。 [来源: DOC-S4-IO-01:64 G-IO4；M1_SYMBOL_SURVEY.md:153 G-M1-3]

**C. 板级时钟/连线/时序（原理图/示波器）**
8. 两片实际主/从角色 + 12.288 MHz 物理来源（SPORT vs codec vs 板载晶振）—— datasheet 无本板记载，须原理图/板上确认。 [来源: S3 F-两片时钟拓扑；DOC-S4-IO-01:63 G-IO3]
9. SPORT4↔codec carrier/SOM 外部网名级走线 + AD2428W-SOM 旁路实体走线 —— schematics PDF 未渲染核名（例程 SRU 仅证片上 DAI 路由）。 [来源: schematics/V2.1/*.pdf；DOC-S4-IO-01 G-IO3]
10. 外部 MCLK 晶振源具体频率/器件 + 例程实际采样率寄存器解码（真跑 48k 验证）。 [来源: DOC-S4-IO-01:61 G-IO1]
11. TDM slot 精确时序（BCLK/FSYNC 极性、slot 起始、24-in-32 对齐）—— 示波器/逻辑分析仪或 EZKIT 对齐。 [来源: DOC-S4-IO-01:65 G-IO5]
12. SoftConfig 直进直出软开关(U48 Port A/B) 在非 A2B 拓扑下具体配置值 —— 工程师确认（例程用 ConfigSoftSwitches_ADC_DAC extern，且 main 中 Switch_Configurator 调用被注释，运行时未执行）。 [来源: DOC-S4-IO-01:67 G-IO7；M1_SYMBOL_SURVEY.md:136；S1 §1.10]

**D. cache / 放置（板 .map 重读）**
13. DMA 回调/提交路径无 cache flush/invalidate —— 本地已知前提（R32 INFO 补）：loopback 当前放置 = L1 Block 0 uncached（.ldf 实证，L1 RAM 不被 core data-cache，cache 仅服务 external/L2 访问）→ 例程 no-flush 正确-by-placement [L1]。board-confirm 仅针对：M1/M2 最终放置若移出 uncached L1（L2/external），则 flush/invalidate 必须补。 [来源: S1 F-frame-callback-logic + loopback app.ldf cache 注释]
14. DMA 缓冲 cache 操作 flush_data_buffer in <sys/cache.h> —— 仅当缓冲移出 L1 到 cached L2/external 时需要。 [来源: M1_SYMBOL_SURVEY.md:148]
15. 产品流水线块大小待定（例程 COUNT=300 / ALT 256-长 float 通道缓冲；我方 FRAME=64）—— 影响延迟/DMA/io-callback block-rate。 [来源: DOC-S4-IO-01:66 G-IO6；ALT.h:24；ALT.c:26-38]
16. 重建带 #pragma 的 .map 须板上重读确认 s_bh_src/dst 落 ≥0x2c0000(Block 1) 且 s_h2_fa 仍 <0x270000(Block 0)（F24-MAJOR-1 放置验证义务持续）。 [来源: H2_MAP_PLACEMENT_ADJUDICATION.md:87-89, :134-136]
17. sizeof(int) 板上确认（SHARC ABI）—— 缓冲字节尺寸 2400/1200 B 依 sizeof(int)=4 假设（§1.9 [inferred]），DMA 尺寸作架构输入前板上 sizeof 一行确认。 [来源: R32 F32-MINOR-1]

---

## 7. 推测项隔离区（[inferred] 集中放，明标——**不得作架构依据**）

> 以下全部为 [inferred]（推导/survey 转引/架构待定），按硬纪律不得伪装成事实，亦不得作不可逆架构/选型依据。需要时回各子任务源核原始口径。

- **[S1] ConfigMC slot 数**：ConfigMC (1u,7u,0u,true) 4A/4B 同 ⇒ 8 TDM slots —— slot 数读自 7u "last active channel"，精确 ConfigMC 语义须 adi_sport.h 原型（见 board-confirm A.4）。
- **[S1] TX XCount fan-out**：XCount=COUNT*2(=600) 与 8-slot fan-out 一致 —— 算术一致性推断。
- **[S1] 缓冲字节尺寸**：TX 2400 B / RX 1200 B —— sizeof(int)=4 SHARC 假设，算术推导。
- **[S3] ADAU1979 TDM8 自洽**：TDM8+SLOT_WIDTH=00@48kHz ⇒ BCLK=8×32×48k=12.288MHz=256×fS —— 字段推算（与 Table 9 数值一致，但属推导非单条 datasheet 直读）。
- **[S3] ADAU1962A 8-of-12 路由**：取 DSDATA1 前 8 slot(Ch1..8) 喂 8 路功放 —— 机制推断；**上板选哪 8/12 路属架构/接线决策，本调研不裁**。
- **[S4] 产品 256×fS/12.288MHz 口径**：8slot×32bit@48k → 12.288MHz —— DOC-S4-IO-01 自标「非寄存器实证」数学自洽推导。
- ~~[S4] 例程 slot 位宽 32-bit~~ —— 已于 R32 升级为 [L1-example-called]（critic 亲核 ALT.c :299/:311/:301/:313），移出隔离区，正文 §4 为准。
- **[S4] 差异点① SAME 判定**：产品/例程 slot 计数/宽/fS/BCLK 一致 —— survey 转引判定（底层 slot 数本轮亲核）。
- **[S4] 差异点② 1-in/8-out 映射**：产品 1 路源 fan-out 8 路 TX slot，SelectChannel 须改 0..7 —— **架构决策，未实现**（survey G-M1-2）。
- **[S4] 差异点③ SAI=TDM8 确认**：产品 8-amp 须确认 codec SAI=011 —— survey 转引，确认须 datasheet 0x05-0x08 在 bring-up（亦入 board-confirm B.6）。
- **[S4] 单片 DAC 足够**：1 路 SPORT4 TDM 驱 8 路不触发多片 DAC —— DOC-S4-IO-01 工程推理，非寄存器实证。
- **[S4] io-callback 探针挂点/公式**：挂 SPORT RX-done 回调，MCPS=cb_cyc×block-rate/1e6 —— survey 提案，**探针未实现**。
- **[S4] block-rate 口径差**：survey 187.5Hz(FS/256) vs 产品 750Hz(FS/64) —— 两数均在档，**口径选择待架构，本轮不裁**。
- **[S4] M2/SPORT 共置 pin 建议**：若 M2 工作集与 SPORT 缓冲同居 L1 Block 0 应 pin 到 seg_l1_block1 —— survey 转引 + H2 裁定；**产品共置与否未定**。
- **[S4] #pragma seg_l1_block1 形式**：段名/路由 = ADI FIRA/IIRA 例程实证 —— H2 裁定转引 ADI 例程，本轮未亲开 IIRA 例程原文。

---

*M1_FACT_BASE — 调研型事实底座，仅事实+来源，供 CTO M1 架构设计输入。*
*汇总：bring-up 前期调研员 / 2026-06-06。源事实经 workflow 4 路 adversarial citation verifier @ claude-opus-4-8 核验（S1/S2/S4 CLEAN，S3 ISSUES-表号顺移已修正入文，无 FABRICATION）。*
