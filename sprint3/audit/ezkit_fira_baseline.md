# EV-21569-EZKIT 首板 ADI 官方 FIR 例程（FIRA）cycle baseline 实测协议 + 文档骨架 + PF-1 核对表

> 文档：TST-EZKIT-FIRA-BASELINE-001 ｜ 产出方：testing teammate ｜ 任务等级：P0 ｜ 日期：2026-06-02
> 状态：**协议 + 骨架 + 核对表已出稿；cycle 实测值待 CTO 台架回填**
> 激活：`knowledge_base/ezkit/prep/PREP-TST-cyclecount.md`（cycle 方法学）

---

## 0. 顶部定性声明（措辞红线，贯穿全文）

> 🔴 **以下声明是本文档的措辞红线，任何引用本 baseline 的下游文档必须同步携带，违反即 BLOCKER（见 §8 / critic C9）。**

1. **跑的是 ADI 官方例程，不是我方算法**：本 baseline 实测对象 = ADI 官方 `FIR_Multi_Channel_Processing`（EE-408 例程，全 float / `ADI_FIR_SAMPLING_SINGLE_RATE` / TAPS1=64 / TAPS2=4096 / 4 通道）。**不是**我方 4 子带 dyadic 树形半带滤波器组（`sprint3/dsp/tree_filterbank.c`，Q15×Q31 定点 / 抽取插值 / 差分金字塔）。

2. **产出用途 = FIRA 性能 baseline + 链路验证**，用于**校准 FIRA 性能、为算力外推提供真板锚点**。

3. **baseline ≠ R1 闭合**：R1（算力命门）的**完整闭合仍需我方 4 子带算法迁移到 21569 后真板实测**（Split-Task 路径，Sprint 4 输入 `DOC-S4-INPUT-01`）。本 baseline 只坐实"ADI 官方 FIR 在本板的 FIRA 性能数量级"，**不坐实我方算法的板上 MCPS**。

4. **R14 闸门维持**：本 baseline **不授权**把"FIRA offload 收益"写进任何选型依据（DEC-S1-004 等）。FIRA offload 净收益须我方算法迁移后实测，在此之前 R14 闸门保持关闭。任何把本 baseline 当作"FIRA offload 已坐实"的引用 = **BLOCKER**。

**❌ 禁止的措辞**："FIR 上板实测 X cycle，R1 算力裕量坐实" / "FIRA offload 收益 = …，选型据此" 。
**✅ 正确的措辞**："ADI 官方 FIR 例程 FIRA baseline = X cycle/sample/tap [L1/EZKIT]；非我方算法；用于校准 FIRA 性能；R1 闭合待我方 4 子带迁移后实测；R14 闸门维持。"

---

## 1. 被测对象与已确认硬件

### 1.1 被测例程

- **例程**：`FIR_Multi_Channel_Processing`（ADI EE-408 例程框架）
- **源码**：`knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/FIR_Multi_Channel_Processing/src/FIR_Multi_Channel_Processing.{c,h}`
- **算法类型**：标准多通道 FIR 卷积（**非我方树形/抽取/插值/差分金字塔**）
- **数值格式**：32-bit IEEE 浮点（全 `float`；rounding `ADI_FIR_FLOAT_ROUNDING_MODE_IEEE_ROUND_TO_NEAREST_EVEN`）[L-src: MCP.c:24-70,139]
- **采样模式**：`ADI_FIR_SAMPLING_SINGLE_RATE`，ratio=1（4 个通道全单速率）[L-src: MCP.c:133/159/190/216]

### 1.2 已确认硬件（CTO 回填前的已知锚点）

| 项 | 值 | 来源 |
|----|----|----|
| 底板 | AD-EXKIT V2.1（双 A2B 改版） | CTO 肉眼确认丝印 |
| 核心板（SOM） | ADSP-21569-SOM REV 1.1 | CTO 确认 |
| 芯片 | **ADSP-21569KBCZ10**（标称 1GHz） | 丝印 |
| CCLK | **【待 CTO 台架回填 — 实测确认，不假设标称 1GHz】** | PF-1 真时钟判据 |
| boot mode | BMODE0/1/2 全 0（No boot，调试态） | `ezkit_bringup_checklist.md` 项③ |
| FIR 例程编译 | 0 错 0 警告 | CTO 确认 |
| 仿真器 | AD-HP530ICE（CCES 识别为 ICE-1000） | `ezkit_bringup_checklist.md` 项② |
| CCES | 2.11.1（bringup）/ cycle 宏头以本机 21569 def 为准 | 见 §3.2 |

> ⚠️ **CCLK 不可假设**：FIRA 跑在 CCLK=ACLK（EE408 标称 1GHz），但 PF-1 红线要求 CCLK **上板实测确认**，换算一律用实测 CCLK。本文档凡涉及"@1GHz"的 ADI 标称值均标 [L-adi]，不当作本板实测。

---

## 2. 配置表（已填确切值，从源码核）

> 全部从例程源码核出，**确切值**，CTO 不需重新推导，照此核对即可。

| 参数 | 值 | 出处 [L-src] |
|------|----|----|
| TAPS1（第一档 tap 数） | **64** | MCP.h:15 |
| TAPS2（第二档 tap 数） | **4096** | MCP.h:18 |
| FIR_WINDOW_SIZE | **1024** | MCP.h:21 |
| 任务数 FIR_NUMBER_OF_TASKS | **2** | MCP.h:24 |
| Task1 通道数 | 2 | MCP.h:27 |
| Task2 通道数 | 2 | MCP.h:30 |
| 总通道数 FIR_NUMBER_OF_CHANNELS | **4**（2 task × 2 ch） | MCP.h:33 |
| 采样模式 | `ADI_FIR_SAMPLING_SINGLE_RATE`，ratio=1 | MCP.c:133/159/190/216 |
| 定点 / 浮点 | **浮点（32-bit IEEE float）** ⚠️须显式标 | MCP.c:24-70（全 `float`） |
| 完成判定 | `FIRTaskDoneCount`，回调 `FIRTaskDoneCallback` 在 `ADI_FIR_EVENT_ALL_CHANNEL_DONE` 自增 | MCP.c:92-105 |
| 输出比对阈值 | `MAX_DIFF_LIMIT 0.001`（实测输出 vs 期望，<0.001 判通过） | MCP.h:52,55-58 |

### 2.1 采样率（Fs）口径 ⚠️ 关键

- **例程未设置音频 Fs**：`FIR_Multi_Channel_Processing` 是**纯吞吐 / 每-window 块处理测试**——一次性把输入 buffer 喂给 FIRA、queue task、等 `FIRTaskDoneCount` 到齐，**不挂实时音频 codec / TDM 时钟**，源码内无 Fs 设定。[L-src: MCP.c 全文无 Fs/codec 配置；完成判定为 `while(FIRTaskDoneCount<...)` 轮询，MCP.c:282-284]
- **换算口径因此按"每 window 处理量"**，不按"每秒采样数"。即 cycle/sample/tap 的 "sample" = window 内处理的样点数（= FIR_WINDOW_SIZE = 1024），不引入 Fs。详见 §3.3 公式。
- **对比意义**：本例程口径 = FIRA 计算吞吐 baseline；与我方算法的 per-block(B=64 sample/通道 @ Fs=48k) 实时口径**不同**，外推时须显式换算，不可直接相减（见 §5 归因 + §9 挂接 dsp_8ch_report §4.3 纯核口径）。

### 2.2 定点/浮点对可比性的影响 ⚠️

本例程为**浮点** FIR。ADI 标称 0.25 cycle/sample/tap [L-adi] 也是浮点 4-MAC 并行口径。我方 LOCKED 基线是**定点**（Q15×Q31，DEC-S3-PROC-01）。**浮点 baseline 不能直接当作我方定点链的 cycle**——FIRA 定点模式有不同的回写/缩放开销（80-bit→3×32-bit 突发，见 `fira_fit_assessment.md` §3.2）。本 baseline 的 cycle/sample/tap **仅对浮点 FIR 口径成立**，须在所有引用处显式标"浮点"。

---

## 3. 测量协议（CTO 可照跑 runbook）

> 本节激活 `PREP-TST-cyclecount.md` §1-§2 的 cycle 方法学到 FIRA 例程语境。CTO 在台架照此跑，testing teammate 数据回流后核 §6。

### 3.1 配置记录（开测前冻结，进 run log）

CTO 跑前把下列确切值记入 run log（多数已在 §2 填好，CTO 只需核对 + 补回填项）：
- tap 数：**TAPS1=64 与 TAPS2=4096 分别测**（两档独立）
- 通道数：4（2 task × 2 ch）
- window：1024
- 采样率：**无 Fs**，按"每 window 处理量"换算（§2.1）
- 数值格式：**浮点**（显式记，影响可比性）
- 编译选项（优化级 `-O?` / SIMD / 内存放置 L1/L2）、中断状态、buffer 段（建议 L1，对齐 ADI 报告假设 EE408 buffers in L1）
- CCLK 实测值（§1.2 回填位）

### 3.2 cycle 测量手段（真硬件周期计数器）

- **用真硬件 cycle 计数器**，不用 statistical profiler（PF-1 红线）。候选宏/内建（**具体宏名以 CCES + ADSP-21569 def 头实际为准**）：
  - SHARC+ 自由运行 cycle counter（疑 `__builtin_emuclk()` / `cycles()` / `CCNT`，名称**待 CTO 在 CCES 头文件确认**）。
  - **CTO 在哪查**：CCES 安装目录下 21569 处理器定义头（`<install>/SHARC/include/` 内的 `cycle_count.h` / `cycles.h` / 处理器 `def` 头）；或 CCES 编译器手册搜 `emuclk`。这是 `PREP-TST-cyclecount.md` §4「待抽取清单」里"cycle 计数寄存器/宏"项的落地动作。
- **64-bit 计数防回绕**：读高低两半。
- **空测扣偏置**：背靠背读计数器测固定偏置 `c_overhead`，从每次测量值扣除。

### 3.3 插桩位置（关键）

> 目标：只测 **FIRA 任务执行**的 cycle，排除一次性 setup。

- **起点**：包住 FIR 任务从 `adi_fir_QueueTask` 提交开始（MCP.c:270 的 queue 循环）。
- **终点**：到 `ALL_CHANNEL_DONE` 全部完成——回调在 `ADI_FIR_EVENT_ALL_CHANNEL_DONE` 自增 `FIRTaskDoneCount`（MCP.c:103-105）。⚠️ **完成阈值随加速器模式不同**（MCP.c:281-284）：Legacy 模式轮询 `while(FIRTaskDoneCount < FIR_NUMBER_OF_TASKS)`(=2)；ACM 模式轮询 `while(FIRTaskDoneCount < FIR_NUMBER_OF_CHANNELS)`(=4)。**CTO 须先确认本次编译用的 `ADI_FIR_CFG_ACCELERATOR_MODE`，按对应阈值定终点，并在 run log 记录模式**（Legacy/ACM 的固定开销不同，EE408 Table1 [L-adi]）。
- **排除（单独记为 setup，不计入稳态）**：一次性 `adi_fir_Open` / 配置 / 系数注入（`CoeffBuff` 填充）/ `adi_fir_RegisterCallback`（MCP.c:247）/ 首次冷 cache 块。
- 用 `volatile` / 内存屏障围栏防编译器重排打点。
- ⚠️ **例程本身无 cycle 打点代码**：CTO 须自行在上述起/终点插入计数器读取（参 `FIR_Throughput_21569` 例程 THR.c 的计时围栏写法，`PREP-TST-cyclecount.md` §4 已列其为可复用范例）。

### 3.4 换算 cycle/sample/tap

按"每 window 处理量"口径（无 Fs，§2.1），公式：

```
cycle_per_sample_per_tap = (测得稳态 cycle − c_overhead) / (FIR_WINDOW_SIZE × tap数 × 通道数)
```

- **64-tap 档**：分母 = 1024 × 64 × 4 = 262,144
- **4096-tap 档**：分母 = 1024 × 4096 × 4 = 16,777,216

> 注：通道数计入分母是因为 4 通道串行/并行执行的总 MAC 量 = window×tap×ch；若 CTO 的插桩只包单通道，则分母去掉 ×4 并在表中注明口径。两档分别算、分别填表。

### 3.5 复现要求（呼应 PF-1 §6）

- 每档 **≥100 迭代**（连喂 block，丢弃前若干热身）
- **≥3 次独立运行**，报 median + max + run-to-run 偏差
- worst-case 说明见 §6 判据 d。

---

## 4. cycle 实测表（待 CTO 台架回填）

> 🚫 **本轮无 cycle 数字**（CTO 未在台架跑）。下列一律 `【待 CTO 台架回填】`。**严禁编造任何 cycle 数字，严禁用仿真器值充数**（仿真器 ≠ 真板，违反 PF-1 真板判据 → 本表保持空占位直到 [L1] 真板数据回流）。

### 4.1 cycle 实测表（每档 ≥3 次独立运行，每次 ≥100 迭代）

| tap 档 | 通道 | window | 数值格式 | 原始 cycle（median） | 扣偏置后 cycle | cycle/sample/tap | N 次 max | run-to-run 偏差 | 离群处理 | CCLK（实测） | 板号+日期+配置hash |
|--------|------|--------|---------|---------------------|----------------|------------------|----------|----------------|----------|-------------|---------------------|
| 64 | 4 | 1024 | float | 【待 CTO 台架回填】 | 【待回填】 | 【待回填】 | 【待回填】 | 【待回填】 | 【待回填】 | 【待回填】 | 【待回填】 |
| 4096 | 4 | 1024 | float | 【待 CTO 台架回填】 | 【待回填】 | 【待回填】 | 【待回填】 | 【待回填】 | 【待回填】 | 【待回填】 | 【待回填】 |

### 4.2 setup（一次性，单独记，不计入稳态）

| 项 | cycle | 备注 |
|----|-------|------|
| `c_overhead`（空测计数器偏置） | 【待回填】 | 背靠背读差值 |
| `adi_fir_Open` + 配置 + 系数注入 setup | 【待回填】 | 隔离，不进 cycle/sample/tap |
| 首次冷 cache 块 | 【待回填】 | 丢弃，不进 median |

---

## 5. vs ADI 标称 0.25 cycle/sample/tap 对比（待回填）

**ADI 标称值**：≈ **0.25 cycle/sample/tap @1GHz**（4 MAC 并行，理想 CE=100%）[L-adi: EE408 p3, eenote:118-119]。⚠️ ADI 报告值，**非本板实测**。

| tap 档 | 实测 cycle/sample/tap（本板） | ADI 标称 | 实测/标称 比值 | 归因（CE / setup 占比 / cache / DMA 主导） |
|--------|------------------------------|----------|----------------|---------------------------------------------|
| 64 | 【待回填】 | 0.25 | 【待回填】 | 【待回填】小 tap → DMA/驱动开销主导，CE 可能 ≪100%（eenote:203-237 [L-adi]） |
| 4096 | 【待回填】 | 0.25 | 【待回填】 | 【待回填】大 tap → 更接近理论 CE |

**归因栏填写要求（呼应 PF-1 红线⑤）**：实测 vs 0.25 偏差须根因分析（FIRA 利用率/Compute Efficiency、QueueTask+中断往返固定开销占比 EE408 Table1 [L-adi]、cache 冷热、DMA 主导），**不得无解释吞掉偏差**。预期：64-tap 偏离 0.25 较大（小核 DMA 主导），4096-tap 较接近。

---

## 6. PF-1 七判据逐条核对表（待 CTO 回填证据）

> 来自 `PREP-TST-cyclecount.md` §3。**全部满足才可标 [L1]，缺一即降级为 [L2]**（见 §8）。每条给"满足条件 + CTO 需回填的证据"。

| # | 判据 | 满足条件 | CTO 需回填的证据 | 状态 |
|---|------|---------|------------------|------|
| a | **真板** | 物理 EV-21569-EZKIT（AD-EXKIT V2.1 + SOM REV1.1 + 21569KBCZ10）运行，非 simulator/桌面 host | 板号 + 运行截图/log（证明非 simulator） | 【待回填】 |
| b | **真时钟** | CCLK 实测确认，**不假设标称 1GHz**；换算用实测 CCLK | 实测 CCLK 值 + 测量方式（PLL 寄存器读 / 时钟树核对） | 【待回填】 |
| c | **真数据** | 例程自带代表性输入 buffer + 期望输出（非 DC=1 占位）；本例为固定输入，记录输入数据来源 | 输入数据描述 + `MAX_DIFF<0.001` 通过证据 | 【待回填】 |
| d | **worst-case** | ⚠️ **本例为定长 float FIR，cycle 基本与数据无关**（无溢出分支、无数据相关跳转，浮点 MAC 等周期）→ **worst-case ≈ average 成立，理由：单速率定长卷积无数据依赖控制流**。**但仍要求 N≥100 迭代 + ≥3 次独立运行**复现，以暴露 cache/中断引入的 run-to-run 抖动（max 仍须报）。<br>（区别于我方算法：我方定点链有饱和钳位分支，worst-case 须对抗满量程激励触发——本 FIR 例程无此问题，须诚实说明此差异，**不可把"本例 worst≈avg"外推到我方算法**） | median + max + 离群，证明 max 与 median 接近 | 【待回填】 |
| e | **真硬件计数器** | 用硬件 cycle counter / `cycles()` / 内建，**非 statistical profiler 估值** | 所用宏/寄存器名 + 头文件出处（§3.2） | 【待回填】 |
| f | **可复现 N 次** | **≥3 次独立运行 + 每次 ≥100 迭代**，报 median+max+run-to-run 偏差 | 3 次 run log + 偏差数值 | 【待回填】 |
| g | **偏置已扣 + setup 隔离** | `c_overhead` 空测扣除；`adi_fir_*` 配置/系数注入 setup 单独记不计入稳态（§3.3/§4.2） | `c_overhead` 值 + setup cycle 值 | 【待回填】 |
| h | **配置可追溯** | 编译选项/SIMD/内存布局/中断状态/数值格式/CCLK/激励/N 全进 run log；每个 cycle 值挂"板号+日期+配置hash+N" | 完整 run log + 配置 hash | 【待回填】 |

> 注：判据计 a-h 共 8 行，对应 PREP-TST §3 的 7 条核心判据（worst-case 单列为 d 以承载"本例 worst≈avg"的诚实说明）。语义等价于"PF-1 七判据"，d 为其展开。

---

## 7. 链路验证模板（ICE Test 5 步 + 例程跑通，待回填）

> 参 `ezkit_bringup_checklist.md` 项⑥（ICE Test 5 步）。前置：bringup checklist 安全闸门已解除（CTO 已确认 V2.1 + 回填专属接线）。

### 7.1 ICE Test 五步（链路自检，CCES Run→Debug Configurations→Session Wizard→Target Configurator→Test）

配置：Type=**ICE-1000**，Device ID=**0**，JTAG TCLK=**5**，点 Start。

| 步 | 项 | 期望 | 实测 |
|----|----|----|----|
| 1 | Opening Emulator Interface | OK | 【待回填】 |
| 2 | Resetting ICEPAC module | OK | 【待回填】 |
| 3 | Testing ICEPAC memory | OK | 【待回填】 |
| 4 | **1 JTAG device(s) detected** | 1 device | 【待回填】 |
| 5 | Performing scan test | 通过（如 ~358 KB/s） | 【待回填】 |

> 1-3 步出错≈软件问题；4-5 步出错≈PC/仿真器/板链路（`ezkit_bringup_checklist.md` 项⑥）。Session platform 字符串：`ADSP-21569 via ICE-1000`。

### 7.2 例程运行跑通

| 项 | 期望 | 实测 |
|----|----|----|
| 编译 | 0 错 0 警告 | ✅ 已达（CTO 确认，§1.2） |
| 运行完成 | Legacy: `FIRTaskDoneCount==FIR_NUMBER_OF_TASKS`(=2) / ACM: `==FIR_NUMBER_OF_CHANNELS`(=4)（MCP.c:281-284，记录所用模式） | 【待回填】 |
| 输出比对 | 实测输出 vs 期望 `MAX_DIFF < 0.001`（MCP.h:52） | 【待回填】 |
| 结束 | CCES 内先 disconnect 再断电；拔 JTAG 前先断电 | 【执行确认】 |

---

## 8. 二值验收判据

> 二值判据，数据回流后 testing teammate 据此判级，无中间态。

1. **标 [L1] 的唯一条件**：§6 PF-1 七判据（a-h）**全部满足**。缺一即**降级为 [L2]**，cycle 值不得进 decisions_log，不得作任何外推锚点。
2. **配置缺项 = MAJOR**：§2 / §3.1 任一配置项（tap档/通道/window/格式/编译选项/CCLK/中断状态/N）未记录 → MAJOR，须补齐方可判 [L1]。
3. **未标"ADI 官方例程非我方算法" = BLOCKER**：§0 定性声明缺失、或下游引用未携带"baseline≠R1闭合 / R14维持"措辞 → **BLOCKER**（critic C9）。
4. **仿真器值充数 = BLOCKER**：任何 cycle 数字若来自 simulator 而标 [L1] → BLOCKER（PF-1 真板红线）。
5. **FIRA offload 收益写进选型 = BLOCKER**：违反 R14 闸门（§0.4）。

> 当前状态：cycle 全占位，judgement = **未判级（待 CTO 台架回填后由 testing teammate 核 §6 判 L1/L2）**。

---

## 9. 挂接 ID 与待回填项清单

### 9.1 挂接 ID

| 挂接 | 关系 |
|------|------|
| **R1**（算力命门） | 本 baseline 校准 FIRA 性能，**不闭合 R1**；R1 闭合待我方 4 子带迁移后真板实测（DOC-S4-INPUT-01） |
| **PF-1**（纸面误判 L1）| §6 七判据防复发；cycle 满判据才 [L1] |
| **DEC-S1-004**（选型）| 本 baseline **不授权**写入选型依据（R14 闸门） |
| **R14**（FIRA bit-exact / offload 闸门）| 维持关闭；FIRA offload 收益须我方算法迁移后实测 |
| `PREP-TST-cyclecount.md` | 本任务激活的 cycle 方法学（§1-§4） |
| `dsp_8ch_report.md` §4.3 / :14（纯核口径）| 我方纯核 MCPS 8ch=45.7/16ch=88.7、裕量 33×/17× = **纯核 software，不含 FIRA**；本 baseline 是 FIRA 浮点口径，两者**不可直接相减**，外推须显式换算 |
| `fira_fit_assessment.md` | §3 例程=浮点/SINGLE_RATE；§4 ADI 标称 0.25 [L-adi] |
| `ezkit_bringup_checklist.md` | §7 ICE Test 5 步来源 |

### 9.2 仍待回填项清单（CTO 台架）

1. **CCLK 实测值**（§1.2 / §6-b）——不假设 1GHz。
2. **64-tap 档 cycle 表**（§4.1）：原始/扣偏置/cycle-per-sample-per-tap/max/偏差/板号+日期+hash。
3. **4096-tap 档 cycle 表**（§4.1）：同上。
4. **setup cycle + `c_overhead`**（§4.2）。
5. **vs 0.25 对比 + 归因栏**（§5）：两档比值 + 偏差根因。
6. **PF-1 七判据 a-h 证据列**（§6）：板号/CCLK/计数器宏名/run log×3/配置 hash。
7. **cycle 计数器宏名确认**（§3.2）：CCES 21569 头文件实际宏（`emuclk`/`cycles()`/`CCNT`）。
8. **ICE Test 5 步实测**（§7.1）。
9. **例程运行 + MAX_DIFF<0.001 通过**（§7.2）。

### 9.3 回流后 testing teammate 动作

数据回流 → 核 §6 七判据 → 全满判 [L1] 标级、否则降 [L2] → 按 §8 二值判据出结论 → 提交 critic（C9 校 R14/措辞）→ 经 Team Lead 汇 CTO。**本文档当前无 cycle 数字，testing teammate 不自行上板、不跑仿真器充数。**

---

*TST-EZKIT-FIRA-BASELINE-001 ｜ testing teammate ｜ 本轮无 cycle 数字（CTO 未跑），实测值一律占位*
