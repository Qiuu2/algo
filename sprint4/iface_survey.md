# DOC-S4-IFACE-SURVEY-01 — 真实系统接口普查（信号链全链路）

> **owner**: dsp-algorithm teammate
> **date**: 2026-06-03
> **挂接**: DEC-S4-DSP-01 / DEC-S4-R1-8CH-01 / DOC-S4-IO-01（系统架构）
> **信号链**: ADAU1979(ADC) → SPORT4(TDM) → 21569(FIRA) → SPORT4(TDM) → ADAU1962A(DAC)，直进直出

---

## ⚠️ 诚实声明（ARM-proxy / 必读，置顶）

本机 CCES（`/opt/analog/cces/2.12.1/`）的 header 全部位于 **ARM 侧**
（`.../ARM/arm-none-eabi/.../cortex-a5/` 与 `.../aarch64-none-elf/.../cortex-a55/`），
即 SC5xx ARM 核（cortex-a5/a55）用的头文件。**SHARC 侧（`__ADSPSHARC__` + 21569）专属变体
`adi_fir_2156x.h` / `adi_iir_2156x.h` 在本机不存在**（已全树 `find` 确认，见下）。

逐项性质如下：

| API 族 | 本机能 grep 到的真实头 | 对 21569 SHARC 的关系 | 可信度 |
|---|---|---|---|
| **adi_sport** | `adi_sport_2156x.h`（cortex-a5 路径，但内容是 2156x SPORT 驱动 API） | 21569 family 走的就是 `adi_sport_2156x.h`（adi_sport.h:34 分支命中），SPORT 是外设、ARM/SHARC 同一套驱动 → **基本可信，作 proxy 偏强** | 高 |
| **adi_fir** | 仅 `adi_fir_v2.h`（SC57x/SC589/215xx 变体）；`adi_fir.h` 对 21569 会 `#include "adi_fir_2156x.h"` 而**该文件本机缺失** | example 实际用的是 2156x 的 **CreateTask / ADI_FIR_CHANNEL_INFO** API，**与本机 v2 的 CreateConfig/AddChannel/CHANNEL_PARAMS API 不同族** → v2 仅作"枚举/概念 proxy"，**确切签名待台架核** | 中（枚举高、函数族低） |
| **adi_twi** | `adi_twi_2156x.h`（cortex-a5 路径） | TWI 外设 ARM/SHARC 同族 → **可信偏强** | 高 |
| **adi_pwr** | `adi_pwr_2156x.h`（cortex-a5 路径） | CGU 时钟，ARM/SHARC 同族 → 可信，但 SHARC 侧 nDeviceNum/clkin 数值待核 | 中高 |
| **adi_int** | `adi_int.h`（cortex-a5） | ARM GIC vs SHARC 中断控制器不同 → **签名作 proxy，SHARC 侧机制不同，须重核** | 低 |
| **adi_pdma / SPORT DMA** | `adi_pdma_2156x.h`（被 adi_sport_2156x.h:72 include） | 同 SPORT，偏强 | 中高 |

**红线**：下表"出处"列只列本机 header / example 中**确实存在**的行（file:行号）。
SHARC 侧确切签名 / 枚举值 / 8-slot TDM 精确寄存器配法 → 一律进 §gaps，**不编**。

---

## §1 SPORT TDM I/O（adi_sport）

**真实头**: `/opt/analog/cces/2.12.1/ARM/arm-none-eabi/arm-none-eabi/include/adi/cortex-a5/drivers/sport/adi_sport_2156x.h`
（`adi_sport.h:34` 对 `__ADSP21569_FAMILY__` → `#include "adi_sport_2156x.h"`，本机存在 ✅）
**example**: `Pipelined/src/Audio_Passthrough_I2S.c`（注：example 用 **I2S 双声道**模式，**不是** TDM 多 slot）

### 1a. 设备/数据流 API

| 函数/宏/字段 | 参数/返回 | example 用了吗 | 我们要吗 | 出处(文件:行号) |
|---|---|---|---|---|
| `adi_sport_Open` | (nDeviceNum, eChannel ADI_HALF_SPORT_A/B, eDirection RX/TX, eMode, *pMem, nMemSize, *phDev) → ADI_SPORT_RESULT | ✅ 4A=TX/4B=RX | ✅ 同样开 TX+RX 两半 sport | adi_sport_2156x.h:286 ｜ 用法 Audio_Passthrough_I2S.c:344,347 |
| `adi_sport_Close` | (hDevice) | ❌ | ✅(收尾) | adi_sport_2156x.h:297 |
| `adi_sport_RegisterCallback` | (hDevice, pfCallback, *pCBparam) | ✅ RX 回调 | ✅ | adi_sport_2156x.h:421 ｜ 用法 :351 |
| `adi_sport_DMATransfer` | (hDevice, *pDescList ADI_PDMA_DESC_LIST, nListSize, ePDMAMode, eSportChEnable) | ✅ 提交首块 ping/pong | ✅(乒乓 DMA) | adi_sport_2156x.h:311 ｜ 用法 :358,361 |
| `adi_sport_2DDMATransfer` | 同上(2D DMA) | ❌ | ⚠可能(8ch 交织布局可能用 2D) | adi_sport_2156x.h:320 |
| `adi_sport_Enable` | (hDevice, bEnable) | ✅ | ✅ | adi_sport_2156x.h:334 ｜ 用法 :365,368 |
| `adi_sport_StopDMATransfer` | (hDevice) | ❌ | ⚠(停机) | adi_sport_2156x.h:329 |
| `ADI_SPORT_MEMORY_SIZE`(宏) | a5 非阻塞=72u / 阻塞=84u+SEM；a55=112u/128u | ✅ 静态分配 SPORTMemory4A/4B | ✅ | adi_sport_2156x.h:98,104 ｜ 用法 :104,105 |
| enum `ADI_SPORT_CHANNEL` | ADI_HALF_SPORT_A=0 / _B=1 | ✅ | ✅ | adi_sport_2156x.h:123-129 |
| enum `ADI_SPORT_MODE` | SERIAL / **MC_MODE(多通道/TDM)** / I2S | ✅ 用 I2S | ✅ **要 MC_MODE**(8-slot TDM) | adi_sport_2156x.h:135-143 |
| enum `ADI_SPORT_DIRECTION` | DIR_RX / DIR_TX | ✅ | ✅ | adi_sport_2156x.h:194-200 |
| enum `ADI_SPORT_EVENT` | RX_BUFFER_PROCESSED=64 / TX=128 / err flags | ✅ 用 RX_BUFFER_PROCESSED | ✅ | adi_sport_2156x.h:166-188 ｜ 用法 :207 |
| enum `ADI_SPORT_CHANNEL_ENABLE` | PRIM / SEC / PRIM_SEC | ✅ 用 PRIM | ✅ | adi_sport_2156x.h:151-159 |

### 1b. 8-slot×32bit TDM 配置接口（**多通道 / MC 模式 — example 未用，但我方核心**）

| 函数 | 参数 | example 用了吗 | 我们要吗 | 出处 |
|---|---|---|---|---|
| `adi_sport_ConfigMC` | (hDevice, **nFrameDelay**, **nNumSlots**, **nWindowSize**, bEnableDMAPack) | ❌(I2S 不用) | ✅✅ **8-slot TDM 核心配置**(nNumSlots=8) | adi_sport_2156x.h:462-468 |
| `adi_sport_SelectChannel` | (hDevice, nStChnlNo, nEndChnlNo) | ❌ | ✅ 选 0..7 slot | adi_sport_2156x.h:471-475 |
| `adi_sport_SelectChannelOrder` | (hDevice, bRightChFirst) | ❌ | ⚠ | adi_sport_2156x.h:478 |
| `adi_sport_ConfigData` | (hDevice, eDataType, **nWordLength=32**, bLSBFirst, bEnablePack, bRightJustifiedMode) | ❌(I2S 走静态配置) | ✅ 32bit 字长 | adi_sport_2156x.h:431-438 |
| `adi_sport_ConfigClock` | (hDevice, nClockRatio, bUseIntlClock, bFallingEdge, bGatedClk) | ❌ | ✅ | adi_sport_2156x.h:441-447 |
| `adi_sport_ConfigFrameSync` | (hDevice, nFsDivisor, bFSRequired, bInternalFS, bDataFS, bActiveHighFS, bLateFS, bEdgeSensitiveFS) | ❌ | ✅ TDM FS | adi_sport_2156x.h:450-459 |
| `adi_sport_ConfigClockDiv` / `ConfigFrameDiv` | (hDevice, nDivisor uint16) | ❌ | ⚠ | adi_sport_2156x.h:401,407 |
| `adi_sport_MuxHalfSport` | (hDevice, bUseOtherFS, bUseOtherClk) | ❌ | ✅ A/B 半 sport 共享 BCLK/FS(SRU 已共享, 见 §3) | adi_sport_2156x.h:386-390 |
| enum `ADI_SPORT_DATATYPE` | ZERO_FILL / SIGN_FILL / u-law / A-law | ❌ | ✅ 用 SIGN_FILL(有符号音频) | adi_sport_2156x.h:271-281 |
| 全局组 API `adi_sport_CreateGlobalGroup`/`GlobalEnable`/`GroupReEnable`/`GlobalRegisterCallback` | DAI 内多 sport 同步全局使能（21569 family 专属 `#if`） | ❌ | ⚠(若 RX/TX 需严格同启) | adi_sport_2156x.h:346-383 |

> ⚠ **example 走的是 I2S 静态路径（不调 ConfigMC/ConfigData）**——I2S 模式下 SLEN/字长由 SRU+静态 config 决定。
> 我方 8-slot TDM **必须显式调用 ConfigMC + SelectChannel + ConfigData(32bit) + ConfigFrameSync**，
> 这条路径 **example 没有覆盖** → 精确参数进 §gaps。

## §2 FIRA 加速器（adi_fir）

> ⚠ **本节最大诚实裂缝**：本机只有 `adi_fir_v2.h`（SC57x/SC589/215xx 变体），
> 而 21569 的真实头 `adi_fir_2156x.h` **全树 find 无结果**（缺失）。
> 偏偏 example 实际调的是 2156x 的 **CreateTask / ADI_FIR_CHANNEL_INFO** API —— **本机 header 里没有这些符号**。
> 所以：枚举/概念用 v2 做强 proxy（R14 命门枚举两边都在），**函数族用 example 源码做证据**，确切签名进 §gaps。

### 2a. 本机 `adi_fir_v2.h` 实有的函数族（CreateConfig/AddChannel 路线 —— **与 example 不同族**）

| 函数 | 参数/返回 | example 用了吗 | 我们要吗 | 出处(file:行号) |
|---|---|---|---|---|
| `adi_fir_Open` | (nDeviceNum, *phDevice) → ADI_FIR_RESULT | ✅(同名同签) | ✅ | adi_fir_v2.h:144 ｜ 用法 FIR_Multi_Channel_Processing.c:243 |
| `adi_fir_Close` | (hDevice) | ❌ | ✅ | adi_fir_v2.h:150 |
| `adi_fir_CreateConfig` | (hDevice, *pMem, nMemSize, *phConfig) | ❌(example 走 CreateTask, **v2 没有 CreateTask**) | ❓ 取决于最终 SHARC 头 | adi_fir_v2.h:154 |
| `adi_fir_AddChannel` | (hConfig, *pMem, nMemSize, *ADI_FIR_CHANNEL_PARAMS, *phChannel) | ❌ | ❓ | adi_fir_v2.h:194 |
| `adi_fir_EnableConfig` / `DisableConfig` | (hConfig, bQueue) | ❌ | ❓ | adi_fir_v2.h:168,173 |
| **`adi_fir_FixedPointEnable`** | (hConfig, **ADI_FIR_FIXED_INPUT_FORMAT** eInputFormat) | ❌(v2 路线) | ✅✅ **R14 定点模式入口** | adi_fir_v2.h:176 |
| `adi_fir_FloatingPointEnable` | (hConfig, ADI_FIR_FLOAT_ROUNDING_MODE) | ❌ | ⚠(若走浮点) | adi_fir_v2.h:179 |
| `adi_fir_RegisterCallback` | (hConfig, pfCallback, *pCBParam) | ✅(同名) | ✅ | adi_fir_v2.h:187 ｜ 用法 :247 |
| `adi_fir_SubmitInputCircBuffer` / `SubmitOutputCircBuffer` | (hChannel, *base, *index, nCount, nModifier) | ❌(v2) | ⚠(数据流入口) | adi_fir_v2.h:210,213 |
| `adi_fir_GetOutputBuffer` / `GetAllOutputBuffers` / `IsOutputAvailable` | 取输出 | ❌ | ⚠ | adi_fir_v2.h:216,222,219 |
| `adi_fir_SetChannelTapLength` / `SetChannelWindowSize` / `SetChannelCoefficientBuffer` / `SetChannelGroup` / `SetChannelSamplingMode` | 逐通道改参 | ❌ | ⚠ | adi_fir_v2.h:228,231,240,234,237 |
| `adi_fir_GetMACStatus` | (hDevice, *pnMACStatus) | ❌ | ⚠(算力监测) | adi_fir_v2.h:243 |
| `adi_fir_WaitForEvent` | (hConfig, eEvent, *pArg) | ❌ | ⚠ | adi_fir_v2.h:190 |

### 2b. example 实际调的 2156x 函数族（**本机 header 无定义 → 源码即唯一证据**）

| 函数 | 参数(从 example 推) | example 用了吗 | 我们要吗 | 出处(example file:行号) |
|---|---|---|---|---|
| `adi_fir_CreateTask` | (hDev, *ADI_FIR_CHANNEL_INFO[], nNumChannels, *pMem, nMemSize, *phTask) | ✅ | ✅(若用 2156x ACM 路线) | FIR_Multi_Channel_Processing.c:251-256 ｜ Pipelined/src/Processing.c:104 |
| `adi_fir_QueueTask` | (hTask) | ✅ | ✅ | FIR_Multi_Channel_Processing.c:270 ｜ Processing.c:159 |
| `ADI_FIR_CHANNEL_INFO`(struct) | {TapLength, WindowSize, Sampling, SamplingRatio, [ACM:CbEnable, GenTrig, WaitTrig, RoundingMode, **FixedPtEnable bool**, **ADI_FIR_FIXED_INPUT_FORMAT**], CoeffCount, CoeffModify, CoeffIndex, OutBase, OutCount, OutModify, OutIndex, InBase, InCount, InModify, InIndex} | ✅ | ✅✅ **这是 example 真实用的通道结构** | FIR_Multi_Channel_Processing.c:128-160 |
| `FIR_MEM_SIZE(n)`(宏) | 通道数→内存字节 | ✅ | ✅ | 用法 .h:36,39；**宏定义本机/example .h 均无 → 来自缺失的 adi_fir_2156x.h** |
| `ADI_FIR_CFG_ACCELERATOR_MODE` / `_ACM` / `_LEGACY`(宏) | ACM vs Legacy 模式开关 | ✅ | ✅ | FIR_Multi_Channel_Processing.c:100,135,281-284；**定义来自缺失头/system cfg** |

### 2c. ★ R14 命门：定点输入格式枚举（**两个头都确认存在**）

| 枚举 | 值 | example 用了吗 | 我们要吗 | 出处 |
|---|---|---|---|---|
| **`ADI_FIR_FIXED_INPUT_FORMAT_UNSIGNED_INTEGER`** | enum 第 0 项 | ✅ example **写死用 UNSIGNED** | ⚠ **R14 风险点**：音频是有符号 PCM，example 却填 UNSIGNED | adi_fir_v2.h:128 ｜ example 用法 FIR_Multi_Channel_Processing.c:141,167,198,224 |
| **`ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER`** | enum 第 1 项 | ❌ | ✅✅ **我方很可能要 SIGNED**（有符号定点 PCM） | adi_fir_v2.h:129 |
| `ADI_FIR_FLOAT_ROUNDING_MODE` | 6 个舍入模式(IEEE…) | ✅ NEAREST_EVEN | ⚠(若浮点) | adi_fir_v2.h:115-123 |
| `ADI_FIR_SAMPLING` | SINGLE_RATE / DECIMATION / INTERPOLATION | ✅ SINGLE_RATE | ✅ SINGLE_RATE | adi_fir_v2.h:70-75 ｜ 用法 :133 |
| `ADI_FIR_EVENT` | CHANNEL_DONE / ALL_CHANNEL_DONE | ✅ | ✅ | adi_fir_v2.h:135-139 ｜ 用法 :101,103 |
| `ADI_FIR_RESULT` | 11 个返回码 | ✅ | ✅ | adi_fir_v2.h:47-60 |

> **R14 确认**：定点格式枚举 = `ADI_FIR_FIXED_INPUT_FORMAT_{UNSIGNED,SIGNED}_INTEGER`，
> 二选一，**adi_fir_v2.h:128-129 实锤**；ACM 模式下由 `ADI_FIR_CHANNEL_INFO` 字段携带（example c:141 处填 UNSIGNED），
> 非 ACM/v2 路线由 `adi_fir_FixedPointEnable(hConfig, eFormat)` 设置（v2.h:176）。
> **命门**：example 用 UNSIGNED 仅因其测试数据是 .dat 无符号样本；**我方有符号 PCM 必须验证用 SIGNED**，
> 否则定点偏差爆表（违反 ≤1e-10 质量约束）。两条路线的"在哪儿设这个枚举"不同 → 见 §gaps。

## §3 SRU 路由（SPORT4 ↔ DAI1）

**头**: `Pipelined/src/sru21569.h`（SRU/SRU2 宏定义，3658 行，CCES 生成）
**用法**: `Pipelined/src/Audio_Passthrough_I2S.c:270-298`（`SRU_Init()`）
SRU2 宏形式：`SRU2(信号源_O, 目的_I)` —— 把 DAI1 引脚和 SPORT4 时钟/帧同步/数据交叉连接。

| 宏/赋值 | 含义（信号流向） | example 用了吗 | 我们要吗 | 出处(file:行号) |
|---|---|---|---|---|
| `*pREG_PADS0_DAI0_IE=0x1ffffe` / `DAI1_IE=0x1ffffe` | DAI0/1 引脚输入使能 | ✅ | ✅ | Audio_Passthrough_I2S.c:272,273 |
| `SRU2(LOW, DAI1_PBEN05_I)` | PB05 设为输入(收外部 BCLK) | ✅ | ✅ | :275 |
| `SRU2(DAI1_PB05_O, SPT4_ACLK_I)` | DAI1_PB05(BCLK) → **SPORT4 A 位时钟** | ✅ | ✅ | :277 |
| `SRU2(DAI1_PB05_O, SPT4_BCLK_I)` | 同一 BCLK → **SPORT4 B 位时钟**(A/B 共享 BCLK) | ✅ | ✅ | :278 |
| `SRU2(DAI1_PB04_O, SPT4_AFS_I)` | DAI1_PB04(FS/LRCLK) → **SPORT4 A 帧同步** | ✅ | ✅ | :280 |
| `SRU2(DAI1_PB04_O, SPT4_BFS_I)` | 同一 FS → **SPORT4 B 帧同步**(A/B 共享 FS) | ✅ | ✅ | :281 |
| `SRU2(LOW, DAI1_PBEN04_I)` | PB04 设为输入(收外部 FS) | ✅ | ✅ | :282 |
| `SRU2(SPT4_AD0_O, DAI1_PB01_I)` | **SPORT4 A 数据输出(TX)** → DAI1_PB01(去 DAC SDATA) | ✅ | ✅ | :284 |
| `SRU2(HIGH, DAI1_PBEN01_I)` | PB01 设为输出 | ✅ | ✅ | :285 |
| `SRU2(DAI1_PB05_O, DAI1_PB12_I)` | BCLK 转发到 PB12(给 codec) | ✅ | ✅ | :287 |
| `SRU2(DAI1_PB04_O, DAI1_PB20_I)` | FS 转发到 PB20(给 codec) | ✅ | ✅ | :291 |
| `SRU2(DAI1_PB06_O, SPT4_BD0_I)` | DAI1_PB06(ADC SDATA) → **SPORT4 B 数据输入(RX)** | ✅ | ✅ | :295 |
| `SRU2(LOW, DAI1_PBEN06_I)` | PB06 设为输入(收 ADC 数据) | ✅ | ✅ | :296 |

> **直接可复用**：example 的 SRU 拓扑就是 ADAU1979(RX←SPT4_BD0) + ADAU1962A(TX→SPT4_AD0)，
> **A/B 半 sport 共享同一 BCLK(PB05)/FS(PB04)** —— 与我方"一个 SPORT4 同时进出"完全一致。
> **唯一差异**：example 是 I2S(2ch)，我方 8-slot TDM。**SRU 物理路由不变**（仍是 ACLK/BCLK/AFS/BFS/AD0/BD0 这 6 根线），
> 改的是 **SPORT 寄存器侧的 slot 数/字长/FS 类型（§1b 的 ConfigMC）**，不是 SRU。
> codec 侧 PB12/PB20 转发也要保留（给 ADAU 喂 BCLK/FS）。

## §4 codec SoftConfig（TWI/I2C + ADAU 寄存器）

**头**: `/opt/analog/cces/2.12.1/ARM/arm-none-eabi/arm-none-eabi/include/adi/cortex-a5/drivers/twi/adi_twi_2156x.h`
（`adi_twi.h` 对 21569 → `adi_twi_2156x.h`，本机存在 ✅）
**用法 A（SoftConfig 板级开关）**: `Pipelined/system/SoftConfig_21569_ADC_DAC.c`（先开 U47/U48 GPIO 扩展器使能 ADAU1979/1962）
**用法 B（ADAU 寄存器配置）**: `Audio_Passthrough_I2S.c:375-532`（PLL + 寄存器表写入）
**寄存器名头**: `Pipelined/src/ADAU_1962Common.h` / `ADAU_1979Common.h`

### 4a. adi_twi 接口

| 函数/宏 | 参数 | example 用了吗 | 我们要吗 | 出处(file:行号) |
|---|---|---|---|---|
| `adi_twi_Open` | (nDeviceNum, ADI_TWI_MASTER, *pMem, ADI_TWI_MEMORY_SIZE, *phDev) | ✅ | ✅ | adi_twi_2156x.h:127 ｜ 用法 Audio_Passthrough_I2S.c:413, SoftConfig:175 |
| `adi_twi_Close` | (hDevice) | ✅(SoftConfig 每开关后关) | ✅ | adi_twi_2156x.h:138 ｜ 用法 SoftConfig:203 |
| `adi_twi_SetHardwareAddress` | (hDevice, addr) | ✅ 切 1962(0x04)/1979(0x11)/开关(0x21,0x22) | ✅ | adi_twi_2156x.h:267 ｜ 用法 :426,458,514; SoftConfig:179 |
| `adi_twi_SetPrescale` | (hDevice, prescale) | ✅(12) | ✅ | adi_twi_2156x.h:243 ｜ 用法 :417; SoftConfig:182 |
| `adi_twi_SetBitRate` | (hDevice, bitrate) | ✅(100kHz) | ✅ | adi_twi_2156x.h:251 ｜ 用法 :420; SoftConfig:185 |
| `adi_twi_SetDutyCycle` | (hDevice, duty) | ✅(50) | ✅ | adi_twi_2156x.h:259 ｜ 用法 :423; SoftConfig:188 |
| `adi_twi_Write` | (hDevice, *pData, nBytes, bNoStop) | ✅ 写 [RegAddr, Value] 2 字节 | ✅ | adi_twi_2156x.h:223 ｜ 用法 :380,391; SoftConfig:199 |
| `adi_twi_Read` | (hDevice, *pData, nBytes, bNoStop) | ✅ 回读校验 | ✅ | adi_twi_2156x.h:233 ｜ 用法 :398 |
| `ADI_TWI_MEMORY_SIZE`(宏) | a5=44u+SEM / a55=72u+SEM / CC21k=48u+SEM | ✅ | ✅ | adi_twi_2156x.h:52-56 |
| enum `ADI_TWI_MASTER` | TWI 主模式 | ✅ | ✅ | adi_twi_2156x.h:88 |
| 进阶: `SubmitTx/RxBuffer`,`RegisterCallback`,`IssueStop`,`Enable` | 非阻塞/中断模式 | ❌(example 用阻塞 Write/Read) | ⚠(可选) | adi_twi_2156x.h:153,188,145,292,216 |

### 4b. ADAU1979(ADC) 寄存器配置序列（example 实测可用，TARGETADDR=0x11）

| 步骤 | 寄存器(宏) | 值 | 含义 | 出处 |
|---|---|---|---|---|
| PLL | `ADAU1979_REG_POWER` / `_REG_PLL` | 0x01 / 0x03，轮询 PLL lock(bit7) | 上电+PLL | Audio_Passthrough_I2S.c:517-528 |
| 配置表 16 项 | BOOST,MICBIAS,**BLOCK_POWER_SAI(0x30→0x33)**, **SAI_CTRL0(0x02)**, SAI_CTRL1(0x00), CMAP12/34, OVERTEMP, POST_ADC_GAIN1-4(0xA0), ADC_CLIP, DC_HPF_CAL, MISC_CONTROL | 见表 | SAI/采样率/增益 | Config_array_ADC[16] :65-82 |

### 4c. ADAU1962A(DAC) 寄存器配置序列（example 实测可用，TARGETADDR=0x04）

| 步骤 | 寄存器(宏) | 值 | 含义 | 出处 |
|---|---|---|---|---|
| PLL | `ADAU1962_PLL_CTL_CTRL0`(0x01→0x05) / `_CTRL1`(0x22)，轮询 lock(bit2) | — | 上电+PLL | Audio_Passthrough_I2S.c:461-485 |
| 配置表 28 项 | PDN_CTRL_1/2/3, **DAC_CTRL0/1/2**, DAC_MUTE1/2, MSTR_VOL, DAC1-12_VOL(0x00), PAD_STRGTH, DAC_PWR1/2/3(0xaa) | 见表 | 12ch DAC 上电/音量/SAI | Config_array_DAC[28] :33-63 |

> **直接可复用**：ADAU1979/1962A 的 PLL 初始化 + TWI 寄存器写序列 example 全给了（地址 0x11/0x04，开关 0x21/0x22）。
> **板级 SoftConfig**（U47/U48 GPIO 扩展器开 `~ADAU1979_EN`/`~ADAU1962_EN`、`ADAU_RESET`）：SoftConfig.c:74-144 完整。
> **待核**：所有寄存器值对应 example 的采样率（SAI_CTRL0=0x02），**我方 48kHz / 8ch TDM 的 SAI_CTRL0/CMAP/BLOCK_POWER 值要按 datasheet 重算** → §gaps。

## §5 DMA / 系统服务（pdma / pwr / int）

### 5a. SPORT 自带 DMA（PDMA 描述符 —— example 用法即我方用法）

| 类型/字段 | 含义 | example 用了吗 | 我们要吗 | 出处 |
|---|---|---|---|---|
| `ADI_PDMA_DESC_LIST`(struct) | {pStartAddr, Config, XCount, XModify, YCount, YModify, pNxtDscp} | ✅ 4 个描述符做乒乓链 | ✅ | 头 adi_pdma_2156x.h（被 adi_sport_2156x.h:72 include）｜ 用法 Audio_Passthrough_I2S.c:94-97,304-334 |
| `.XCount` | =COUNT(=BLOCK_SIZE*2=512) | ✅ | ✅(按 8ch×FRAME 调整) | :306,322 |
| `.XModify` | =4(字节, 32bit int) | ✅ | ✅ | :307 |
| `.Config` | =`ENUM_DMA_CFG_XCNT_INT`(传完中断) | ✅ | ✅ | :305 |
| `.pNxtDscp` | 指向下个描述符(环形链表→乒乓) | ✅ 1↔2 循环 | ✅ | :310,318,326,334 |
| `ADI_PDMA_DESCRIPTOR_LIST`(模式枚举) | 描述符列表流模式 | ✅(传给 DMATransfer) | ✅ | 用法 :358,361 |
| `DMA_NUM_DESC`(宏) | 描述符数 | ✅ | ✅ | 用法 :358（定义在 .h） |

> SPORT 经 `adi_sport_DMATransfer` 直接驱动 PDMA，**无需单独调 adi_dma**。乒乓双缓冲 + RX 回调置 BlockReady → core 处理。

### 5b. SPU（系统保护单元 —— SPORT 安全主控，example 必调）

| 函数 | 参数 | example 用了吗 | 我们要吗 | 出处 |
|---|---|---|---|---|
| `adi_spu_Init` | (nDevNum, *pMem, …, *phSpu) | ✅ | ✅(否则 DMA 被拦) | 用法 Audio_Passthrough_I2S.c:220 |
| `adi_spu_EnableMasterSecure` | (hSpu, SPORT_4A/4B_SPU, true) | ✅ 给 SPORT4A/4B | ✅ | 用法 :227,234 |
| `ADI_SPU_MEMORY_SIZE` / `SPORT_4A_SPU`/`SPORT_4B_SPU` | 宏 | ✅ | ✅ | 用法 :121,227,234 |

### 5c. power / clock（adi_pwr_2156x.h，本机存在 ✅；example 主程序未显式调，由 adi_initComponents/system 配）

| 函数 | 参数 | example 用了吗 | 我们要吗 | 出处 |
|---|---|---|---|---|
| `adi_pwr_Init` | (nDeviceNum uint8, clkin uint32) | ❌(走 adi_initComponents() :154) | ⚠(确认 CGU/CLKIN) | adi_pwr_2156x.h:642 |
| `adi_pwr_ClockInit` | (…) | ❌ | ⚠ | adi_pwr_2156x.h:633 |
| `adi_pwr_GetSystemFreq` | (nDevNum, *fsysclk, *fsclk0, *fsclk1) | ❌ | ⚠(算力核算需 SCLK) | adi_pwr_2156x.h:653 |
| `adi_pwr_GetCoreClkFreq` | (nDevNum, *fcclk) | ❌ | ⚠(核频=1GHz 验证) | adi_pwr_2156x.h:663 |

### 5d. interrupt（adi_int.h，cortex-a5 / **ARM GIC，SHARC 侧机制不同→低可信**）

| 函数 | 参数 | example 用了吗 | 我们要吗 | 出处 |
|---|---|---|---|---|
| `adi_int_InstallHandler` | (iid, ADI_INT_HANDLER_PTR, *pParam, bEnable) | ❌(SPORT/TWI 驱动内部封装) | ⚠(回调够用则不需手动) | adi_int.h:72 |
| `adi_int_EnableInt` | (iid, bEnable) | ❌ | ⚠ | adi_int.h:79 |
| `ADI_INT_HANDLER_PTR` | 处理函数指针类型 | ❌ | ⚠ | adi_int.h:67 |

> 中断绝大多数被 SPORT/TWI 驱动回调封装（`adi_sport_RegisterCallback` 等），应用层一般不直接碰 adi_int。
> ⚠ **adi_int.h 是 ARM(GIC)侧**，SHARC 侧中断控制器不同 → 仅作存在性 proxy。

## §6 真实系统集成接口清单（最小集，按信号链串）

按 **ADAU1979 → SPORT4(RX) → FIRA → SPORT4(TX) → ADAU1962A** 串起来，"最小要调哪些接口"：

```
[0] 系统起：adi_initComponents()  →  adi_spu_Init + adi_spu_EnableMasterSecure(SPORT_4A/4B)   §5b
                                       (DMA 安全主控，否则 SPORT DMA 被拦)

[A] 板级开关：ConfigSoftSwitches_ADC_DAC()  →  内部 adi_twi_Open/SetHWAddr/Write 开 ADAU1979/1962_EN + RESET   §4a/SoftConfig

[B] codec 配置(TWI 0x11/0x04)：
      Init_TWI(): adi_twi_Open → SetPrescale → SetBitRate → SetDutyCycle → SetHardwareAddress     §4a
      ADAU_1979_init(): PLL(REG_POWER/PLL 轮询) + 16 项寄存器表(SAI_CTRL0…) via adi_twi_Write     §4b
      ADAU_1962_init(): PLL(CTRL0/CTRL1 轮询) + 28 项寄存器表(DAC_CTRL…) via adi_twi_Write         §4c
      ★我方差异：寄存器值按 48k/8ch TDM 重算

[C] SRU 路由：SRU_Init()  →  6 根线
      DAI1_PB05→SPT4_ACLK/BCLK(共享 BCLK)，DAI1_PB04→SPT4_AFS/BFS(共享 FS)，
      SPT4_AD0→DAI1_PB01(TX→DAC)，DAI1_PB06→SPT4_BD0(ADC→RX)，PB12/PB20 转发给 codec   §3
      ★物理路由与 example 一致，不随 TDM 变

[D] SPORT 开 + TDM 配置：
      RX: adi_sport_Open(SPORT_4B, HALF_SPORT_B, DIR_RX, ADI_SPORT_MC_MODE, …)                §1a
      TX: adi_sport_Open(SPORT_4A, HALF_SPORT_A, DIR_TX, ADI_SPORT_MC_MODE, …)
      ★MC_MODE 下补：adi_sport_ConfigMC(nNumSlots=8, nFrameDelay, nWindowSize)  +              §1b
                      adi_sport_SelectChannel(0,7) + adi_sport_ConfigData(32bit, SIGN_FILL) +
                      adi_sport_ConfigFrameSync(...) + adi_sport_MuxHalfSport(A/B 共时钟)
      adi_sport_RegisterCallback(RX, cb)  →  cb 置 BlockReady                                   §1a
      PrepareDescriptors(): ADI_PDMA_DESC_LIST 乒乓链(XCount/XModify/pNxtDscp)                  §5a
      adi_sport_DMATransfer(RX/TX, descList, …, ADI_SPORT_CHANNEL_PRIM)                          §1a
      adi_sport_Enable(RX,true) + adi_sport_Enable(TX,true)

[E] FIRA 处理(每 block)：
      一次性：adi_fir_Open → adi_fir_RegisterCallback                                           §2a/2b
              [2156x 路线] adi_fir_CreateTask(ADI_FIR_CHANNEL_INFO[8ch], …)  ← example 路线
              ★R14：CHANNEL_INFO.FixedPtFormat = ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER     §2c
              [v2 路线替代] adi_fir_CreateConfig + adi_fir_AddChannel + adi_fir_FixedPointEnable(SIGNED)
      每帧：  adi_fir_QueueTask(hTask)  →  等 ADI_FIR_EVENT_ALL_CHANNEL_DONE  →  取输出           §2b
              (8 通道各一条 FIR，对应 8 路 A/B 对称串联波束)

[F] 数据搬运：RX DMA buf →(定点格式适配)→ FIRA 输入环形缓冲 → FIRA 输出 → TX DMA buf
      example 用 Block_Fixed_To_Float/Float_To_Fixed(2^-31 scaling, c:535-557)；
      ★我方走纯定点则用 SIGNED 整数路径，无需浮点转换
```

**最小接口集汇总**（去重）：
- SPU：`adi_spu_Init`, `adi_spu_EnableMasterSecure` ×2
- TWI：`adi_twi_Open/Close/SetHardwareAddress/SetPrescale/SetBitRate/SetDutyCycle/Write/Read`
- SRU：`SRU2()` ×约 12 行（§3 全表）
- SPORT：`adi_sport_Open` ×2, `ConfigMC`, `SelectChannel`, `ConfigData`, `ConfigFrameSync`, `MuxHalfSport`, `RegisterCallback`, `DMATransfer` ×2, `Enable` ×2
- PDMA：`ADI_PDMA_DESC_LIST` 描述符 ×N
- FIRA：`adi_fir_Open`, `RegisterCallback`, `CreateTask`(或 CreateConfig+AddChannel), `QueueTask`, +`ADI_FIR_CHANNEL_INFO` 含 **SIGNED** 定点格式
- pwr：`adi_pwr_Init`（多由 adi_initComponents 代办，确认即可）

## §7 gaps（header/example 没有、待台架确认）

| # | gap | 为什么是 gap | 影响 | 怎么关 |
|---|---|---|---|---|
| G1 | **SHARC 侧 `adi_fir_2156x.h` 本机缺失** | 全树 `find adi_fir_2156x.h` 无结果；21569 的 `adi_fir.h` 对 `__ADSPSHARC__` 才 include 它。本机只有 ARM 的 `adi_fir_v2.h` | FIRA 真实函数族(`CreateTask`/`ADI_FIR_CHANNEL_INFO`/`FIR_MEM_SIZE` 宏)签名/字段顺序无法从 header 确证，只能靠 example 源码 | 台架装 SHARC toolchain 后 grep `adi_fir_2156x.h`；或装 SHARC Audio Toolbox |
| G2 | **R14：CHANNEL_INFO 里定点格式字段的确切位置/默认值** | example(c:141)在 ACM 模式 `#if` 内填 `UNSIGNED`；非 ACM 时该字段不出现（被 `#if ADI_FIR_CFG_ACCELERATOR_MODE==ACM` 包裹）。v2 路线则走 `adi_fir_FixedPointEnable()` | 用错 UNSIGNED→有符号 PCM 定点偏差爆表(违反 ≤1e-10) | 台架确认 ACM vs Legacy 模式 + 实测 SIGNED 路径偏差 |
| G3 | **8-slot×32bit TDM 的 ConfigMC 精确参数** | example 全程 I2S(2ch)，**从不调 `adi_sport_ConfigMC`**；nFrameDelay/nWindowSize/FS 类型(早/晚、电平)无 example 实例 | TDM 时序配错→ slot 错位/无声 | 查 ADSP-2156x HW Reference SPORT 章 + 台架示波器对帧 |
| G4 | **FRAME=64 vs example block=256/window=1024** | example BLOCK_SIZE=256, FIR_WINDOW_SIZE=1024, FIR_TAPS=512(Pipelined) / TAPS=64,4096+window=1024(FIR_Multi)；**我方 FRAME=64** 无对应实例；FIRA 要求输入缓冲 ≥ BLOCK+TAPS-1 (c:572) | window/环形缓冲尺寸、延迟线预载长度需按 FRAME=64 重算；FRAME=64 是否过小影响 FIRA 效率待评 | 按我方 N_tap + FRAME=64 重算 WindowSize/InputCount/Modify |
| G5 | **ADAU 寄存器值 ↔ 48k/8ch TDM 对应** | example 寄存器值(SAI_CTRL0=0x02 等)对应其 I2S/采样率配置，非 8ch TDM/48k | 采样率/SAI 模式/通道映射(CMAP)配错→codec 不出声或错通道 | 按 ADAU1979/1962A datasheet 重算 SAI_CTRL0/1、CMAP12/34、BLOCK_POWER_SAI、DAC 通道映射 |
| G6 | **adi_pwr 实际调用点/CLKIN 值** | example 主程序不显式调 adi_pwr，交给 `adi_initComponents()`(c:154)+ system.svc 配置 | 核频(目标 1GHz)/SCLK 数值未在源码暴露→算力核算缺真值 | 读 system/ 下 .svc 或台架 `adi_pwr_GetCoreClkFreq` |
| G7 | **adi_int(GIC) 是 ARM 侧** | `adi_int.h` 在 cortex-a5 路径，SHARC 中断控制器不同 | 若需手动装中断(一般不需)，签名/iid 不可信 | 优先用驱动回调；必要时查 SHARC 侧 adi_int |
| G8 | **FIR vs FIR+IIR / 浮点 vs 定点路线未定** | example(Pipelined)是 FIR(512tap)+5band IIR 且**走浮点**(Fixed↔Float 转换 c:535-557)；我方波束形成是否纯 FIR / 纯定点未锁 | 决定走 §2c 哪条枚举路径 + 是否需 IIR 驱动(adi_iir) | 由 DEC-S4-DSP-01 算法定型后定 |
| G9 | **example FIR 系数=全通(b0=1)占位** | example FIR 是 all-pass 占位(c:8)，非真实波束系数 | 不影响接口，但提醒系数加载路径(`pCoefficientBase`/`CoeffBuff`)要接我方 8 路波束权 | 接入声学 agent 输出的 8 路 FIR 系数 |

---

### 附：本次普查证据基线（防漂移）
- header 树：`/opt/analog/cces/2.12.1/ARM/`（ARM-only，无 SHARC 侧 `adi_*_2156x` 的 fir/iir 变体）
- example 树：`knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/`
- 关键缺失文件（确认不存在）：`adi_fir_2156x.h`、`adi_iir_2156x.h`
- 关键存在文件：`adi_sport_2156x.h`、`adi_fir_v2.h`、`adi_twi_2156x.h`、`adi_pwr_2156x.h`、`adi_int.h`、`adi_pdma_2156x.h`

*DOC-S4-IFACE-SURVEY-01 — dsp-algorithm teammate — 2026-06-03 — 本单仅普查，不跑仿真/不写集成代码*
