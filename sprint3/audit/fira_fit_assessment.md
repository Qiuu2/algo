# FIRA 适配性评估 — ADI FIR_Multi_Channel_Processing 例程 + 21569 FIRA 加速器 vs 我方 4 子带树形滤波器组

> 任务：dsp-algorithm teammate
> 日期：2026-06-02
> 评估对象：ADSP-21569 SHARC+ FIR 硬件加速器（FIRA）+ ADI EE-408 例程框架
> 我方算法：`sprint3/dsp/tree_filterbank.{c,h}`（4 子带 dyadic 树形半带 FIR，差分金字塔，63-tap 原型，Q15 系数 × Q31 状态，3 级抽取/插值，broadside DAS，LOCKED 定点 DEC-S3-PROC-01）
>
> **铁律纪律**：每条结论挂 `file:line` 或 PDF 页码。L 标签：
> - **[L-src]** = 源码/头文件确定事实（可直引）
> - **[L-doc]** = datasheet/HW reference 手册实证（标页码）
> - **[L-adi]** = ADI 报告 cycle 值（非我方实测）
> - **[待实测]** = 资料未覆盖，需上板/仿真实测

---

## 0. 资料出处清单（本评估引用的全部一手来源）

| 缩写 | 文件 | 关键内容 |
|------|------|---------|
| MCP.c / MCP.h | `knowledge_base/.../FIR_Multi_Channel_Processing/src/FIR_Multi_Channel_Processing.{c,h}` | 例程数据类型、tap/window/通道配置 |
| THR.c / THR.h | `knowledge_base/.../ADSP_2156x_FIRA_Performance/src/FIR_Throughput_21569.{c,h}` | cycle 测量方法、MAX_TAP、TCB 结构 |
| PIPE.c / PIPE.h | `knowledge_base/.../Pipelined/src/Processing.{c,h}` | 实时音频 FIRA+IIRA 链路写法 |
| CFG | `knowledge_base/.../FIR_Multi_Channel_Processing/system/drivers/fir/adi_fir_config_2156x.h` | 定点/浮点模式、单核、ACM 开关（21569 专属） |
| V2 | `/opt/analog/cces/2.12.1/ARM/.../cortex-a5/drivers/fir/adi_fir_v2.h` | 驱动 API：SAMPLING 枚举、CHANNEL_PARAMS 结构、定点/浮点 API |
| EE408 | `knowledge_base/.../app_notes/Using ADSP-2156x High Performance FIRIIR Accelerators.pdf` | cycle/吞吐报告值、使用模型 |
| HWREF | `knowledge_base/.../hw_reference/ADSP-21569 SHARC+® ProcessorHardware Reference.pdf` | FIRA 容量/模式/格式硬规格（第 38 章） |
| DS | `knowledge_base/.../datasheets/ADSP-2156x-Datasheet-EN.pdf` | 单核/浮点/FIRA 总规格 |

> ⚠️ **重要口径说明**：CCES 2.12.1 仅安装了 ARM(cortex-a5) 侧驱动头 `adi_fir_v2.h`（SC5xx 族）；21569 SHARC 侧 `adi_fir_2156x.h` **未安装**（`adi_fir.h` 是分发头，21569 走 `#include "adi_fir_2156x.h"` 但该文件本机缺失，见 adi_fir.h:32-36 [L-src]）。
> 因此**驱动 API 级**枚举/结构引自 ARM 侧 v2 头（API 跨核一致）；**21569 硬件能力**一律以 HWREF/DS/CFG（21569 专属，已 `#if defined(__ADSP21569_FAMILY__)` 守卫）为准，不以 ARM 头冒充硬件规格。

---

## 1. FIRA 容量边界

### 1.1 单次最大 tap（硬规格）

- **硬滤波器长度 = 1024 tap**：FIRA 数据通路含 "1024 word coefficient memory" + "1024 deep delay line for data"，HWREF 第 38-1/38-2 页（hwref.txt:75234-75235, 75291-75292）**[L-doc]**；DS 第 1142-1146 行同述 "1024 word coefficient memory, a 1024 word deep delay line"（ds.txt:1144-1146）**[L-doc]**。
- **浮点模式可超 1024（多迭代）**：soft filter length > 1024 时分多次 1024-tap 迭代（如 2048 tap = 2×1024 迭代），不整除则迭代至满足（HWREF 38-8，hwref.txt:75636-75643）**[L-doc]**。例程 MCP.c 实测跑到 **TAPS2 = 4096**（MCP.h:18）**[L-src]**，THR.h 定义 `MAX_TAP_LENGTH (4096)`（THR.h:15）**[L-src]** → 浮点下 4096 tap 被 ADI 实测验证可行。
- **定点模式硬上限 = 1024 tap**："Multi-iteration mode is not supported in fixed-point format. Therefore, the maximum TAP length is 1024."（HWREF 38-9，hwref.txt:75656, 75724）**[L-doc]**。

### 1.2 最大通道数

- **Legacy 模式：最多 32 通道（TDM）**："Up to 32 filter channels available in TDM in legacy mode"（HWREF 38-1，hwref.txt:75212）**[L-doc]**。
- **ACM 模式：无理论上限**：ACM 下加速器按 TCB 链处理直到遇到 CHNPTR=0 的 TCB，"there is no theoretical limit on the number of channels"（EE408 第 2 页，eenote.txt:63-68）**[L-doc]**；DS 第 1166-1168 行 "dynamic queuing of unlimited FIR/IIR channels"（ds.txt:1166-1168）**[L-doc]**。21569 同时支持 Legacy 与 ACM（CFG:77 `ADI_FIR_CFG_ACCELERATOR_MODE`，21569 两种皆合法，CFG 第 176-180 行守卫）**[L-src]**。（行号修正：critic C1 核出原 CFG:139 实为 `ADI_FIR_CFG_FIXED_INPUT_FORMAT`，`ADI_FIR_CFG_ACCELERATOR_MODE` 在 CFG:77；实质结论不变。）
- 例程 MCP 用 2 task × 2 channel = 4 通道（MCP.h:24-33）**[L-src]**；PIPE 用 NCH=12 单 task（PIPE.h:17, PIPE.c:104-109）**[L-src]**。**我方 16 通道 < 32（Legacy 即可装下），或走 ACM 无限制**。

### 1.3 系数定点位宽 / 浮点

- **默认 32-bit IEEE 浮点**："The FIR accelerator treats data and coefficients in 32-bit floating-point format as the default functional mode"（HWREF 38-9，hwref.txt:75711）**[L-doc]**；MCP.c 全 `float`（FirInputBuff/CoeffBuff/FirOutputBuff 均 float，MCP.c:24-70）**[L-src]**。
- **支持 32-bit 定点**："Fixed-point and 32-bit IEEE floating-point format"（HWREF 38-1 Features，hwref.txt:75207）**[L-doc]**；定点 MAC 为 **32-bit × 32-bit → 80-bit 结果**（HWREF 38-9，hwref.txt:75713-75716）**[L-doc]**。定点输入格式可为 unsigned integer / unsigned fractional / signed integer（hwref.txt:75715-75716）**[L-doc]**；驱动 API `ADI_FIR_FIXED_INPUT_FORMAT` 仅暴露 UNSIGNED_INTEGER / SIGNED_INTEGER 两枚举（V2:126-131）**[L-src]**。

### 1.4 我方 4 子带总 tap 能否装下

我方结构（tree_filterbank.{c,h}）的 FIR 单元：
- 原型半带核 **63 tap**（`TFB_HB_TAPS 63`，tree_filterbank.h:53）**[L-src]**；3 级（`TFB_NUM_LEVELS 3`，h:54）**[L-src]**。
- 每通道 FIR 实例数：分析侧 3 个 decimating 半带（`ana_dec[3]`）+ 3 个 interpolating 半带（`ana_int[3]`），合成侧 3 个 interpolating 半带（`syn_int[3]`），共 **9 个 63-tap 半带卷积**（tree_filterbank.h:104-107；tree_filterbank.c:149-158, 188+ 调用 hb_decimate2/hb_interp2）**[L-src]**。

**结论（容量）**：
- 单个半带核 63 tap ≪ 1024（定点）/ 4096（浮点已实测），**单次单通道无任何容量问题** **[L-src+L-doc]**。
- 我方注意：Dolph-Chebyshev −20dB 加权在**阵元维度**（broadside DAS，各子带等增益），**不增加 FIR tap**——加权是 16 元的静态幅度权重，不是子带 FIR 的一层（tree_filterbank.h:16 "Dolph 加权在阵元维度"）**[L-src]**。故"含 Dolph 那一层的 tap"在树形滤波器组里**不存在额外 tap**：Dolph 权重落在波束形成求和系数上，与 FIRA 的 FIR 卷积是两件事。
- 即便把每通道 9 个半带核全部 offload，每个均为独立 63-tap channel/TCB，**无需多次拆分**（远低于 1024 硬长度）**[L-doc]**。16 通道 × 9 核 = 144 个 63-tap FIR 操作，**Legacy 32 通道/迭代限制**意味着需多次 queue（144 > 32），或用 ACM 链式无限制（见 §2/§4 算力讨论）。

---

## 2. 结构匹配（抽取/插值是否可 offload）

### 2.1 FIRA 是否硬件支持抽取/插值？→ 是

- **HW 原生支持**："Single rate or multi-rate window processing / Programmable rates with decimation or interpolation mode"（HWREF 38-1 Features，hwref.txt:75210-75211）**[L-doc]**。
- **三种操作模式确认**："It supports single-rate, decimation, and interpolation functions."（HWREF 38-8 Operating Modes，hwref.txt:75621-75623）**[L-doc]**。
  - **Decimation**：每 M 个输入产 1 个输出，输出率 = 输入率/M；通过 `FIR_CTL2.RATIO` + `FIR_CTL2.UPSAMP` 配置；要求 TAPLEN ≥ RATIO（HWREF 38-8/38-9，hwref.txt:75669-75682）**[L-doc]**。**关键优化**："FIR logic skips the computation of output samples, which are discarded"（hwref.txt:75673-75674）**[L-doc]** → 抽取时硬件跳过被丢弃样点的计算，算力按输出率而非输入率收费。
  - **Interpolation**：每输入产 L 个输出；硬件自动在样点间插 L−1 个 0 再卷积（HWREF 38-9，hwref.txt:75684-75688）**[L-doc]**。
- **驱动 API 暴露**：`ADI_FIR_SAMPLING { SINGLE_RATE, DECIMATION, INTERPOLATION }`（V2:70-75）**[L-src]**；`adi_fir_SetChannelSamplingMode(hChannel, eSampling, nRatio)`（V2:237）**[L-src]**；CHANNEL_PARAMS 含 `eSampling` + `nSamplingRatio` 字段（V2:92-93）**[L-src]**。
- **例程现状**：所有例程（MCP.c:133/159/190/216, PIPE.c:172）都设 `ADI_FIR_SAMPLING_SINGLE_RATE`、ratio=1 **[L-src]** —— 即例程**未演示**抽取/插值，但 API + 硬件均支持。我方若用，属于**有 API 支持但无 ADI 示例代码**的路径（迁移风险点，见 §5）。

### 2.2 抽取/插值的硬约束（直接影响我方树形可 offload 性）

- **多速率模式不支持多迭代 → 最大 1024 tap，比率必须整数**："Both upsampling and downsampling do not support multi-iteration mode. Therefore, the filtering operation only happens on up to 1024 TAPs and the ratio of up and downsampling can only be an integer value."（HWREF 38-9，hwref.txt:75697-75698）**[L-doc]**。
  - 我方半带 63 tap ≪ 1024 ✅；抽取/插值比率 = 2（整数）✅ —— **两条约束我方均满足** **[L-src+L-doc]**。
- **插值的 WINDOWSIZE 约束**："WINDOWSIZE = n × SAMPLERATIO"（HWREF 38-9，hwref.txt:75701-75702）**[L-doc]** → 我方帧长须为采样比的整数倍（我方已要求 frame 为 8 的倍数，tree_filterbank.h:124，恰好覆盖 3 级 ×2 的各级整除）**[L-src]**，对齐。

### 2.3 哪些段能 offload、哪些必须核内做

我方差分金字塔（tree_filterbank.c）逐操作拆解：

| 操作 | 出处 | 可 offload 到 FIRA？ |
|------|------|----------------------|
| `hb_decimate2`（dec2(LP(·))，半带 LP + 取偶相位） | tree_filterbank.c:108-117（调用 c:149-153） | ✅ **可** = FIRA DECIMATION 模式 ratio=2（hwref.txt:75669-75682）**[L-doc]** |
| `hb_interp2`（零插值 + 半带 LP + ×2 增益） | tree_filterbank.c:121-132（调用 c:156-158, 188+） | ✅ **可** = FIRA INTERPOLATION 模式 ratio=2（hwref.txt:75684-75688）**[L-doc]**；×2 增益可折进系数或核内乘 |
| detail 残差 `sb = a − interp2(coarse)`（逐点减） | tree_filterbank.c:161-163 | ❌ **必须核内**：FIRA 只做卷积/MAC，无向量减法单元（HWREF Functional Description 仅列 4 MAC + 部分和寄存器，hwref.txt:75289-75296）**[L-doc]** |
| 合成端逐子带相加 `sat_add_i32` | tree_filterbank.c:55-61, 183+ | ❌ **必须核内**：向量加 + 饱和钳位，非 FIR 操作 |
| 子带增益 `q31_mul`（broadside 时 g=1） | tree_filterbank.c:178-181 | ⚠️ broadside 时 g=1 可省；非 broadside 可折进 FIRA 系数或核内乘 |
| 饱和钳位 `sat_i64_to_i32`（PF-4 FIX-01） | tree_filterbank.c:47-52, 104, 127 | ❌ **必须核内**：FIRA 浮点无溢出钳位语义；FIRA 定点是 80-bit 累加（见 §3） |

**结构匹配判定 = ⚠️ 部分适配**：6 个 decimating + interpolating 半带卷积段（每通道分析 3 dec + 3 int，合成 3 int = 9 段）**可 offload**；但**差分金字塔的核心特征——时域残差减法与合成加法（telescoping PR 的关键，tree_filterbank.h:13-14）必须留在核内**。这意味着不是"把整条链甩给 FIRA 核就空闲"，而是 **FIRA 做卷积 + 核做轻量向量加减**的 split/pipeline 模式（对应 EE408 的 Split Task / Data Pipelining 模型，eenote.txt:420-435）**[L-doc]**。

---

## 3. 定点 vs 浮点口径

### 3.1 例程是浮点（已锚定）

- MCP.c 全 `float`：FirInputBuff/CoeffBuff/FirOutputBuff 均 float（MCP.c:24-70）**[L-src]**；rounding `ADI_FIR_FLOAT_ROUNDING_MODE_IEEE_ROUND_TO_NEAREST_EVEN`（MCP.c:139 等）**[L-src]**。
- PIPE.c 同样全 `float`（PIPE.c:5-23）**[L-src]**；THR.c 的 InputBuff/CoeffBuff/OutputBuff 均 `float`（THR.c:25-31）**[L-src]**。
- → **ADI 提供的全部 21569 FIRA 例程走浮点**。例程默认配置 `ADI_FIR_FIXED_POINT_MODE (0u)` = Floating Point（CFG，`#define ADI_FIR_FIXED_POINT_MODE (0u)` 注释 "(0u) - Floating Point Mode / (1u) - Fixed point Mode"）**[L-src]**。

### 3.2 FIRA 硬件本身：浮点 **和** 定点都吃

- **硬件双模式确认**：Features 列 "Fixed-point and 32-bit IEEE floating-point format"（HWREF 38-1，hwref.txt:75207）**[L-doc]**；数据通路 "Four 32-bit floating-point and fixed-point multiplier and adder units"（HWREF 38-2，hwref.txt:75293）**[L-doc]**。
- **浮点是默认模式**：hwref.txt:75711 **[L-doc]**。
- **定点模式细节**（HWREF 38-9，hwref.txt:75713-75724）**[L-doc]**：
  - 32-bit 定点输入/系数 → **80-bit MAC 结果**；
  - 定点结果整 80-bit 回写为 3×32-bit 突发（LSW / MSW / 16-bit overflow + 16-bit 零填充）→ `WINDOWSIZE = WINDOWSIZE × 3`；
  - 若用 signed fractional，输出须 ×2 缩放（MAC 不右移去冗余符号位），并需后处理 decimate 输出缓冲到目标样点；
  - **定点不支持多迭代 → 最大 1024 tap**（hwref.txt:75724）。
- **驱动 API 双模式**：`adi_fir_FixedPointEnable(hConfig, eInputFormat)` 与 `adi_fir_FloatingPointEnable(hConfig, eRoundingMode)`（V2:176, 179）**[L-src]**；21569 在 Legacy 模式有 `ADI_FIR_FIXED_POINT_MODE` 全局开关（CFG）**[L-src]**，在 ACM 模式可逐通道设 `Fixed point enable` + `Fixed Point format`（MCP.c:140-141 通道结构字段）**[L-src]**。

### 3.3 我方定点（Q15 系数 × Q31 状态）offload 到 FIRA 的口径对照

我方 LOCKED 定点（DEC-S3-PROC-01）：**Q15 系数 × Q31 状态 → Q46(int64) 累加 → >>15 回 Q31**（tree_filterbank.c:6, 99, 104；tree_filterbank.h:29）**[L-src]**。

口径对不上的点（**这是 ⚠️ 的关键差异**）：

| 维度 | 我方算法 | FIRA 定点模式 | 口径对照 |
|------|---------|--------------|---------|
| 系数位宽 | Q15（16-bit）（tree_filterbank.c:65 `int16_t *g_hb`）**[L-src]** | 32-bit 定点（hwref.txt:75714）**[L-doc]** | Q15 需零/符号扩展进 32-bit 容器；位宽不同但可表达 |
| 状态位宽 | Q31（32-bit）（tree_filterbank.h:98 `int32_t state[]`）**[L-src]** | 32-bit 定点 ✅ | 对齐 |
| 累加宽度 | Q46 = int64（tree_filterbank.c:89,99）**[L-src]** | 80-bit（hwref.txt:75714）**[L-doc]** | FIRA 精度更高，不丢精度 |
| 输入格式枚举 | 有符号小数（Q 格式）| API 仅 UNSIGNED_INTEGER / SIGNED_INTEGER（V2:128-129）**[L-src]**；HW 文档另提 "unsigned fractional"（hwref.txt:75715）**[L-doc]** | **口径冲突**：我方是 signed fractional(Q)，但驱动枚举无 signed-fractional；HW 文档的 signed-fractional 处理需"输出 ×2 缩放 + decimate 输出缓冲"（hwref.txt:75722-75723）**[L-doc]** → **非平凡映射，需上板验证 bit 对齐** |
| 回量化 >>15 + 饱和钳位 | 核内 `sat_i64_to_i32`（tree_filterbank.c:104）**[L-src]** | FIRA 输出 80-bit 三字回写，缩放/钳位须核内后处理（hwref.txt:75718-75723）**[L-doc]** | 钳位逻辑必须保留在核内（与 §2.3 一致） |

**口径结论**：
1. **不是"必须转浮点"**——FIRA 有定点模式，我方定点路线可保留 **[L-doc]**。
2. **但**直接 1:1 offload 我方 Q15×Q31 定点到 FIRA 定点有两处口径不平凡：(a) 系数从 Q15 升 32-bit 容器；(b) signed-fractional 格式在驱动 API 无直接枚举、HW 层 signed-fractional 需 ×2+decimate 后处理。**这部分 bit-exact 对齐属 [待实测]**，桌面无法坐实。
3. **更稳的工程路径**：若改走 FIRA 浮点（与全部 ADI 例程一致、风险最低），则我方需把定点链改回/并存浮点链——这与 LOCKED 定点基线（DEC-S3-PROC-01）冲突，属决策项，需上报 PM/CTO（见 §5）。

---

## 4. cycle 基准（ADI 报告值，非我方实测）

> 本节全部为 **[L-adi] ADI 报告值，非我方实测**。我方自己的 cycle 须等 EV-21569-EZKIT 上板（tree_filterbank.h:60-72 的 cycle counter / GPIO 钩子）或 CCES SHARC 仿真实跑。

### 4.1 ADI 报告的 FIRA 每 tap 每样本 cycle 成本

- **理论值 ≈ 0.25 cycle / sample / tap**："For the FIRA ... the theoretical number of cycles per sample per tap is close to 0.25 (1/4)"（EE408 第 3 页，eenote.txt:118-119）**[L-adi]**；原因：4 个 MAC 并行（eenote.txt:201, hwref.txt:75208/75293）**[L-doc]**。
- **FIRA 跑在 CCLK = 1 GHz**（ACLK=CCLK，eenote.txt:138；hwref.txt:75223）**[L-doc]**。
- → 理论吞吐上界 ≈ 4 MAC/cycle × 1e9 cycle/s = **4000 MMAC/s**（理想 100% Compute Efficiency 下，eenote.txt:126-132）**[L-adi]**。实测 CE 随 window/tap 变化（小 tap/小 window 时 DMA 开销主导，eenote.txt:203-237）**[L-adi]**，故**实际有效吞吐 < 4000 MMAC/s，且对我方 63-tap 小核可能显著低于理论**（见 4.3 风险）。
- FIRA vs 核：FIRA ≈ **2× SHARC+ 核**执行同 FIR 代码（FIRA 4 MAC vs 核 2 MAC，eenote.txt:200-202）**[L-adi]**；FIRA ≈ 8× SC57x FIRA、4.44× 214xx FIRA（仅时钟差异，eenote.txt:194-199）**[L-adi]**。

### 4.2 ADI 报告的驱动开销（每次 task/channel 的固定成本，core cycles）

来自 EE408 Table 1（21569 EZ-Kit 实测，buffers 全在 L1，eenote.txt:374-390）**[L-adi]**：

| 操作 | FIRA Legacy | FIRA ACM |
|------|------------|----------|
| CreateTask 常量开销 | 76 | 148 |
| CreateTask 每通道开销 | 306 | 320 |
| QueueTask（空队列） | 300 | 371 |
| QueueTask（非空队列） | 195 | 329 |
| 中断往返（单 task） | 429 | 423 |
| 中断往返（多 task） | 503 | 595 |

> **对我方的意义**：CreateTask 是一次性 init（不计入帧预算）；但 **QueueTask（~195-371 cycle）+ 中断往返（~423-595 cycle）每帧每 task 都付**。我方 16 通道 ×（最多 9 半带段）若拆成大量小 task，per-task 固定开销会吃掉 63-tap 小核本就不多的 MAC 收益 —— 这是"小核 offload 不划算"的定量来源（见 4.3）。

### 4.3 换算到我方 4 子带 + 回答 R1（17×/33× 含不含 FIRA offload）

**R1 直接回答**：dsp_8ch_report.md:14 的权威 MCPS **8ch=45.7 / 16ch=88.7 MMAC/s**、裕量 **33×(8ch)/17×(16ch)**，是 **核内纯软件树形** 算力（对照 1500 MMAC/s 保守核预算，dsp_8ch_report.md:14,66；tree_filterbank.h:68 "21569 单核 1GHz ~1-2 定点 MAC/cycle"）**[L-src]** —— **不含任何 FIRA offload**。即：

- **17×/33× 是"完全不用 FIRA、纯核跑"的裕量**。结论方向（远超 CTO ≥10× 目标）已成立，**FIRA 是锦上添花而非必需**。
- 若额外把半带卷积 offload 到 FIRA：理论上把约 88.7 MMAC/s 的 FIR 部分（实际 < 此值，因 detail 减法/合成加法/钳位留核内，§2.3）转移到 FIRA 的 ~4000 MMAC/s 上界 **[L-adi]**，核负载进一步下降；**但**对 63-tap 小核，per-task 驱动开销（4.2）+ 小 tap 低 CE（eenote.txt:203-211）**[L-adi]** 可能使净收益有限。**具体净收益数字 = [待实测]**（须上板比对"核-only" vs "FIRA-offload"两版的帧 cycle）。

> 量级粗算（仅供方向判断，**非结论**）：我方每帧 16ch×9 段若各开 1 channel/TCB → 144 个 FIRA channel/帧。即便走 ACM 无通道上限（eenote.txt:63-68）**[L-doc]**，144×(QueueTask+中断) 量级 ≈ 144×~(300+500) ≈ 1.15e5 core cycle/帧固定开销；@1GHz、64 样本帧（1.333 ms@48k，tree_filterbank.h:71）帧预算 ≈ 1.33e6 cycle → 固定开销约占 ~8.6%。**此为 [待实测] 的上板验证目标，非我方确定值**（实际可合并通道/减少 TCB 数）。

---

## 5. 迁移工作量清单

从 MATLAB/桌面 C（tree_filterbank.{c,h}，host [L2]）迁到 21569 FIRA 框架（PIPE.c 模式）：

### 5.1 保留（无需改）
- 差分金字塔算法路线、半带原型系数、3 级树结构、PR 重建恒等（telescoping）—— FIRA 不改变算法，只换 FIR 卷积的执行单元（HWREF 38-8 公式与标准卷积一致，hwref.txt:75626-75632）**[L-doc]**。
- 16 通道 < 32（Legacy 即可），通道数无需重构（§1.2）。
- frame 为 8 的倍数约束已满足 INTERPOLATION 的 WINDOWSIZE=n×RATIO 约束（§2.2）。

### 5.2 改造（FIRA 框架适配）
1. **采用 PIPE.c 的实时模式**：`adi_fir_Open` → `InitializeFIRTaskChannels`（逐通道填 ADI_FIR_CHANNEL_INFO）→ 每帧 `adi_fir_QueueTask` → 回调里链下一级（PIPE.c:80-127, 159, 215-229）**[L-src]**。我方需把 9 段半带映射到 channel/task 列表。
2. **抽取/插值改用 FIRA 模式位**：把 `hb_decimate2`/`hb_interp2` 的核内实现替换为 channel 配置 `eSampling=ADI_FIR_SAMPLING_DECIMATION/INTERPOLATION` + `nSamplingRatio=2`（V2:92-93, 237）**[L-src]**。⚠️ **ADI 例程无抽取/插值示例代码**（全 SINGLE_RATE，§2.1），此为无参考代码路径。
3. **detail 减法 / 合成加法 / 饱和钳位保留核内**（§2.3）：在 FIRA 回调之间用核做 `sb=a−r`、`sat_add_i32`、`sat_i64_to_i32`（tree_filterbank.c:55-61, 104, 161-163）**[L-src]** —— 即 EE408 的 Split/Pipelined 模型（eenote.txt:420-435）**[L-doc]**。
4. **定点格式口径对齐（高风险，§3.3）**：Q15→32-bit 容器；signed-fractional 在驱动 API 无枚举 → 要么核内做缩放（HW signed-fractional 需 ×2+decimate 输出，hwref.txt:75722-75723 **[L-doc]**），要么改走 FIRA 浮点（与 LOCKED 定点冲突，需决策）。
5. **circular buffer 索引**：FIRA 输入用环形缓冲，`FIRA_INDEX_START=(WP_START−FIR_TAPS+1)`、缓冲长 ≥ BLOCK_SIZE+FIR_TAPS（PIPE.h:14-16, PIPE.c:184）**[L-src]** —— 我方延迟线（tree_filterbank.h:98 `state[]`）须重排为 FIRA 期望的 `x[n−(N−1)]...x[n+W−1]` 布局（HWREF 38-8，hwref.txt:75603-75606）**[L-doc]**。
6. **buffer 放 L1**：所有 ADI cycle 报告均假设 buffer 在 L1（eenote.txt:149-150, 377）**[L-doc]**；THR.c 用 `#pragma section("seg_l1_block1")`（THR.c:24-31）**[L-src]**。我方 16ch×多缓冲须核算 L1（5 Mb L1，ds.txt:295）是否够放，否则 L2/L3 增 cache flush 开销（eenote.txt:394）**[L-doc]**。

### 5.3 风险清单
| 风险 | 级别 | 出处 / 说明 |
|------|------|-----------|
| signed-fractional 定点格式无驱动枚举，需手工缩放/decimate | **HIGH** | V2:128-129 [L-src] vs hwref.txt:75715,75722 [L-doc]；bit-exact = [待实测] |
| 抽取/插值无 ADI 示例代码（仅 API+HW 支持） | MEDIUM | §2.1，全例程 SINGLE_RATE [L-src] |
| 63-tap 小核 + 144 channel/帧的 per-task 开销可能吞掉 offload 收益 | MEDIUM | EE408 Table 1 [L-adi]，净收益 = [待实测] |
| 21569 SHARC 侧驱动头 adi_fir_2156x.h 本机未安装（仅 ARM v2 头） | LOW | adi_fir.h:32-36 [L-src]；上 CCES/EZKIT 工程时随 BSP 提供 |
| FIRA 定点不支持多迭代（>1024 tap）——我方 63 tap 无碍，但限制未来扩展 | LOW | hwref.txt:75724 [L-doc] |
| L1 容量是否够放 16ch 全缓冲 | LOW | ds.txt:295 (5Mb L1)；= [待实测] 排布后核算 |

---

## 三档结论

### 总判定：⚠️ **部分适配**（可用且有益，但非 1:1 即插即用，且非必需）

**✅ 完全适配的方面：**
- **容量**：我方 63-tap 半带 ≪ 1024(定点)/4096(浮点已实测)；16 通道 < 32(Legacy) 或 ACM 无限制 — 无任何容量瓶颈（HWREF 38-1 hwref.txt:75212; 38-8 hwref.txt:75637; MCP.h:18 TAPS2=4096 [L-doc+L-src]）。
- **抽取/插值结构**：FIRA 硬件原生支持 decimation/interpolation，比率=2 整数、tap≪1024 两约束我方均满足（HWREF 38-8/38-9 hwref.txt:75621-75698 [L-doc]）。
- **定点路线可保留**：FIRA 有定点模式，不强制转浮点（HWREF 38-1 hwref.txt:75207, 38-9 hwref.txt:75713 [L-doc]）。
- **单核 + 硬件浮点已坐实**（解 memory.md §2.3 冲突）：**21569 是 SHARC+ 单核**（DS 封面 ds.txt:1, 正文 ds.txt:153 "based on the SHARC+ single core" [L-doc]；CFG `ADI_FIR_CFG_DUAL_CORE_MODE_SUPPORT (0)` + 注释 "For ADSP-21569 processors, Dual Core Mode is not supported" [L-src]）；**有硬件浮点**（IEEE 32/40/64-bit float，ds.txt:9,488-490 [L-doc]）。

**⚠️ 部分适配（明列）：**
- **可 offload**：每通道 9 个半带卷积段（3 dec + 3 int 分析 + 3 int 合成）→ FIRA DECIMATION/INTERPOLATION 模式（§2.3）。
- **必须核内**：差分金字塔的 detail 残差减法（tree_filterbank.c:161-163）、合成端饱和加法（c:55-61,183+）、Q31 饱和钳位（c:47-52,104）—— FIRA 只做卷积无向量加减/钳位（§2.3）。→ 属 EE408 Split Task / Data Pipelining 模型，非 Direct Replacement（eenote.txt:420-435 [L-doc]）。
- **定点口径需手工对齐**：我方 signed-fractional Q15×Q31 ↔ FIRA 定点（驱动仅 unsigned/signed integer 枚举，HW signed-fractional 需 ×2+decimate 后处理）—— bit-exact 映射 = [待实测]（§3.3）。

**❌ 不适配的方面：无硬性不适配项。** 唯一"做不到 Direct Replacement"是结构性的（差分金字塔含核内向量减/加），但有 Split/Pipelined 替代模型，故归 ⚠️ 而非 ❌。

**给 PM/CTO 的工程结论：**
1. FIRA **可用、有益、但非必需**——R1 的 17×/33× 裕量是**纯核 software、不含 FIRA**，已远超 ≥10× 目标（dsp_8ch_report.md:14 [L-src]）。FIRA 是把核负载再降的可选优化，**不是可行性前提**。
2. 若启用 FIRA，推荐 **Split Task / Data Pipelining**，FIRA 做半带卷积、核做残差减/合成加/钳位。
3. **决策点上报**：定点 offload 的 signed-fractional 口径不平凡（HIGH 风险）。可选 (a) 核内缩放适配保 LOCKED 定点，或 (b) FIRA 浮点（与全部 ADI 例程一致、最低风险，但与 DEC-S3-PROC-01 定点基线冲突 → 需 CTO 裁决）。

---

## 仍待上板 / 仿真实测的项

以下项桌面/资料无法坐实，须 EV-21569-EZKIT 上板或 CCES SHARC 周期精确仿真：

1. **我方树形的真实 FIRA-offload cycle / 帧**（核-only vs FIRA-offload 两版对比）—— 资料只给 ADI 报告的 0.25 cycle/tap 理论值与驱动开销表（eenote.txt:118-119, 374-390 [L-adi]），我方实测须用 tree_filterbank.h:60-72 的 cycle counter / GPIO 钩子上板跑。
2. **63-tap 小核在 FIRA 上的实际 Compute Efficiency**（小 tap/小 window DMA 主导，CE 可能远 < 100%，eenote.txt:203-237 [L-adi]）—— 净 offload 收益方向已知、数值待实测。
3. **定点 signed-fractional Q15×Q31 → FIRA 定点的 bit-exact 对齐**（×2 缩放 + 输出 decimate 是否复现我方 >>15+饱和语义，hwref.txt:75718-75724 [L-doc]）—— 须上板逐位回归。
4. **144 channel/帧（或合并后）的实际 per-task 固定开销占比**（§4.3 的 ~8.6% 是粗算上界，非确定值）。
5. **16ch 全缓冲的 L1 排布与容量核算**（5 Mb L1，ds.txt:295 [L-doc]）；放不下则 L2/L3 cache flush 开销（eenote.txt:394 [L-doc]）待量化。
6. **21569 SHARC 侧 adi_fir_2156x.h 的精确结构/枚举**——本机 CCES 2.12.1 仅装 ARM(cortex-a5) v2 头（adi_fir.h:32-36 [L-src]）；SHARC 侧 API 细节须在装了 21569 BSP 的 CCES 工程内核实（API 跨核应一致，但未在本机直接验证）。
