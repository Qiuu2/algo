# FIRA 集成路线图 — 我方 4 子带树形 FIR → ADSP-21569 FIRA 硬件加速器

**文档 ID**：DOC-S4-FIRA-PLAN-01
**任务**：dsp-algorithm teammate（R14 前置 · 分析 + 路线图 · 🚫不写 FIRA 代码）
**日期**：2026-06-02
**性质**：分析 + 路线图。**等 R1 板测完再开发 FIRA 版**；本单只输出"怎么改"的规划。

---

## 0. 范围声明 + 挂接 + 红线

### 0.1 范围
- **做**：① FIRA 文档/接口梳理 ② 参考实现剖析 ③ 我方算法→FIRA 任务映射 ④ R14 风险点（Q 格式映射） ⑤ 集成路线图。
- **🚫 不做**：不写任何 FIRA 代码（adi_fir_* 调用、TCB 配置、回调实现一律推后到 R1 板测之后）。
- **口径继承**：本单大量结论已在 `sprint3/audit/fira_fit_assessment.md`（DOC-S4-FIRA-FIT，C1 PASS）坐实，**直接引用其行号 / hwref 页 / 例程 file:line，不重新查 PDF 容量页**。

### 0.2 挂接（cross-ref）
| 锚点 | 含义 | 出处 |
|------|------|------|
| **R14** | bit-exact 闸门：FIRA 收益在 R14 通过前不得写进选型依据 | `ezkit_fira_baseline.md:19`；`core_only_migration_plan.md:24-26` |
| **DEC-S4-DSP-01** | bit-exact 迁移基准 = C golden vector（sat/unsat 双套）+ numpy xcheck，MATLAB 不补，LOCKED | `decisions_log.md:575,627`；`core_only_migration_plan.md:30-33` |
| **铁律八 / C9** | FIRA 性能数写进选型依据 = BLOCKER | `core_only_migration_plan.md:24,227` |
| **DOC-S4-FIRA-FIT** | FIRA 适配性评估（容量/结构/定点/cycle/迁移工作量），本单上游 | `sprint3/audit/fira_fit_assessment.md` |
| **DOC-S4-CORE-PLAN-01** | core-only G2–G5 适配计划（禁碰 FIRA），本单的"核内基线"对照 | `sprint4/core_only_migration_plan.md` |
| **golden CRC** | R14 回归基准 = `0x90556BC7`（core-only 单通道 65536-sample Q31 CRC32） | `sprint4/dsp/core_only/bench/golden_ref.h:26` |

### 0.3 红线（写进报告，违者 BLOCKER）
1. **FIRA 收益（cycle / MMAC/s / 裕量）在 R14 bit-exact 通过前不得写进任何选型依据**（铁律八 / C9）。本文所有 FIRA 性能数一律标 **"待 R14 后实测、不计入选型"**。
2. 本单 = 分析 + 路线图，**不写 FIRA 代码**。
3. 每条技术结论挂出处（fira_fit_assessment 行 / 例程 file:line / hwref 页）。
4. **R1 的 17×/33× 裕量是纯核 software、不含 FIRA**（DOC-S4-FIRA-FIT §4.3）——FIRA 是可选优化，非可行性前提。

---

## 1. FIRA 文档 / 接口梳理

> 口径说明（继承 DOC-S4-FIRA-FIT §0）：21569 SHARC 侧 `adi_fir_2156x.h` **本机未装**（CCES 2.12.1 仅装 ARM cortex-a5 v2 头 `adi_fir_v2.h`）。下文驱动 API 级流程引自 **ARM v2 头 + EE-408 例程字段注释**作 proxy（API 跨核应一致），21569 硬件能力以 HWREF/DS 为准。**精确 SHARC 结构体待装 21569 BSP 的 CCES 工程内核实**——凡 proxy 项均标 `[proxy]`。

### 1.1 adi_fir Open → CreateTask → QueueTask → (回调) → Close 主流程

例程 `FIR_Multi_Channel_Processing.c`（下称 MCP.c）的标准生命周期 **[L-src]**：

| 步骤 | API | 出处 | 作用 |
|------|-----|------|------|
| ① 打开设备 | `adi_fir_Open(0u, &hFir)` | MCP.c:243 | 获取 FIRA 设备 handle（设备号 0） |
| ② 注册回调 | `adi_fir_RegisterCallback(hFir, cb, 0)` | MCP.c:247 | 任务/通道完成事件回调 |
| ③ 建任务 | `adi_fir_CreateTask(hFir, ChannelList, nCh, &TaskMem, MemSize, &hTask)` | MCP.c:251-265 | 把一组 `ADI_FIR_CHANNEL_INFO[]` 编译成 TCB 链，写进调用者提供的 `TaskMemory[]`（`#pragma align 32`，MCP.c:82-86） |
| ④ 入队 | `adi_fir_QueueTask(hTask)` | MCP.c:268-272 | 把任务挂上加速器队列，启动 DMA + MAC |
| ⑤ 等完成 | 轮询 `FIRTaskDoneCount`（或回调驱动） | MCP.c:281-285 | Legacy：每 task 一次回调；ACM：每 channel 一次回调（见 §2.3） |
| ⑥ 关闭 | `adi_fir_Close(hFir)`（例程未显式调，实时应用退出时调） | — | 释放设备 |

实时音频（PIPE.c 模式，DOC-S4-FIRA-FIT §5.2.1 引）：CreateTask 一次性 init，**每帧只重复 ④ QueueTask + 回调里链下一级**，CreateTask 不进帧预算。

### 1.2 ADI_FIR_CHANNEL_INFO 字段含义（逐字段，来自 MCP.c:128-160 例程注释 [L-src]）

每个 FIR 通道（= 一个 FIR 卷积操作）由一个 `ADI_FIR_CHANNEL_INFO` 结构描述：

| 字段 | 例程值 | 含义 | 我方映射要点 |
|------|--------|------|-------------|
| Tap Length | TAPS1=64 / TAPS2=4096 | FIR 抽头数 | 我方 = 63（共享半带原型，见 §3.1） |
| Window Size | FIR_WINDOW_SIZE=1024 | 一次处理的输出样本数 | 我方 = 各级子带帧长（frame/2^l），见 §3.3 |
| **Sampling** | `ADI_FIR_SAMPLING_SINGLE_RATE` | 单速率 / 抽取 / 插值 | **我方关键**：dec 段填 DECIMATION，int 段填 INTERPOLATION |
| **Sampling Ratio** | 1 | 抽取/插值比 | 我方 = 2（整数，满足 hwref 约束） |
| [ACM:] Callback Enable | true | 该通道完成是否回调 | ACM 才有；用于链下一级 |
| [ACM:] Generate Trigger | false | 完成发触发 | 跨任务同步用 |
| [ACM:] Wait for Trigger | false | 等触发才启动 | 跨任务同步用 |
| **Rounding Mode** | `ADI_FIR_FLOAT_ROUNDING_MODE_IEEE_ROUND_TO_NEAREST_EVEN` | 浮点舍入 | **R14 风险**：浮点路径的舍入模式 ≠ 我方 Q31 截断 `>>15`（§4） |
| **Fixed point enable** | false（=浮点） | 选浮点 or 定点模式 | 我方定点路线须置 true；例程无定点示例 |
| **Fixed Point format** | `ADI_FIR_FIXED_INPUT_FORMAT_UNSIGNED_INTEGER` | 定点输入格式 | **R14 命门**：我方是 signed-fractional Q，与 UNSIGNED_INTEGER 错配（§4） |
| Coefficient Count | TAPS | 系数个数 | = Tap Length |
| Coeff Modify / Index | 1 / `CoeffBuff` | 系数步长 / 基址 | 我方喂冻结的 Q15→32bit 容器系数 |
| Output Base/Count/Modify/Index | `FirOutputBuff` / WINDOW / 1 | 输出缓冲布局 | 我方各级子带输出缓冲 |
| Input Base/Count/Modify/Index | `FirInputBuff` / **TAPS+WINDOW-1** / 1 | 输入缓冲布局 | **Input Count = TapLen+Window-1**（含延迟线尾），我方延迟线须重排为此布局（§5） |

> 关键观察：定点字段 **Fixed point enable / Fixed Point format 只在 ACM 模式编译**（MCP.c:135-142 的 `#if ...ACM` 守卫）。Legacy 模式定点走 `ADI_FIR_FIXED_POINT_MODE` 全局开关（DOC-S4-FIRA-FIT §3.2）。→ **我方若要逐通道定点，须走 ACM**（见 §2.3 / §3.3）。

---

## 2. 参考实现剖析

### 2.1 例程任务结构（MCP.c）

- **任务/通道粒度**：MCP 用 **2 task × 2 channel = 4 通道**（MCP.c:128/185 两个 `ADI_FIR_CHANNEL_INFO[]` 数组）**[L-src]**。每个 channel 一个独立 FIR 卷积，输入/系数/输出各自独立缓冲。
- **任务内存**：每 task 一块 `uint8_t TaskMemory[FIR_MEM_SIZE_TASKn]`（`#pragma align 32`，MCP.c:82-86）**[L-src]**——CreateTask 把 channel list 编译成 TCB 链写进这块内存。我方须按 channel 数算各 task 的 MemSize。
- **缓冲规模**：Input = `TAPS+WINDOW-1`、Coeff = `TAPS`、Output = `WINDOW`（MCP.c:24-70, 151）**[L-src]**。
- **完成判定**：Legacy 等 `FIRTaskDoneCount < FIR_NUMBER_OF_TASKS`（每 task 一回调）；ACM 等 `< FIR_NUMBER_OF_CHANNELS`（每 channel 一回调）（MCP.c:281-285）**[L-src]**。
- **校验法**：`Find_Max_Diff` 算实际 vs 期望的**相对误差**（MCP.c:300-320）**[L-src]**——这是浮点容差比对，**我方 R14 须改为整数逐位/CRC**（§5.3）。

### 2.2 系数格式（例程 = float；定点模式 = unsigned int）

- **例程全 float**：`FirInputBuff/CoeffBuff/FirOutputBuff` 均 `float`（MCP.c:24-70）**[L-src]**；舍入 `IEEE_ROUND_TO_NEAREST_EVEN`（MCP.c:139）**[L-src]**。**ADI 提供的全部 21569 FIRA 例程走浮点**（DOC-S4-FIRA-FIT §3.1）。
- **定点模式系数格式 = UNSIGNED_INTEGER**：例程定点字段填 `ADI_FIR_FIXED_INPUT_FORMAT_UNSIGNED_INTEGER`（MCP.c:141）**[L-src]**；驱动 API 仅暴露 UNSIGNED_INTEGER / SIGNED_INTEGER 两枚举（V2:126-131），HW 文档另提 unsigned-fractional（hwref:75715）**[L-doc]**——**均无 signed-fractional（=我方 Q 格式）的直接枚举**。这是 §4 R14 命门的根。

### 2.3 ACM vs Legacy 差异（决定我方 task 拆分方式）

| 维度 | Legacy 模式 | ACM（Auto-Configuration Mode） |
|------|------------|-------------------------------|
| 通道上限 | **≤ 32 通道（TDM）** | **无理论上限**（TCB 链处理到 CHNPTR=0 为止） |
| 出处 | hwref:75212 [L-doc] | EE408 p2 eenote:63-68；ds:1166-1168 [L-doc] |
| 回调粒度 | 每 **task** 完成一次（`ALL_CHANNEL_DONE`，MCP.c:103） | 每 **channel** 完成一次（`CHANNEL_DONE`，MCP.c:101）[L-src] |
| 定点配置 | 全局 `ADI_FIR_FIXED_POINT_MODE` 开关 | **逐通道** `Fixed point enable`+`Fixed Point format`（MCP.c:140-141）[L-src] |
| 调度 | 静态 TDM | 动态 TCB 链（dynamic queuing of unlimited channels，ds:1166）[L-doc] |
| per-task 开销（core cycle，EE408 Table 1） | QueueTask 195-300 / 中断 429-503 | QueueTask 329-371 / 中断 423-595 [L-adi] |

> **对我方的含义**：我方 16ch（< 32）单看通道数 Legacy 即可装下；但我方需要**逐通道不同的 Sampling 模式（dec vs int）+ 逐级链式回调**，且若走定点须**逐通道定点格式**——这些**强烈倾向 ACM**（Legacy 全局定点开关 + 静态 TDM 不便逐级链）。代价是 ACM per-task 固定开销略高（上表）。**最终 Legacy/ACM 选型 = 待 R1 后实测两版开销再定，不计入选型**（铁律八）。

---

## 3. 我方算法 → FIRA 任务映射

### 3.1 ⚠️ tap 口径澄清（先做，否则映射错）

存在**两套 tap 口径**，必须分清：

| 口径 | SB0 | SB1 | SB2 | SB3 | 出处 |
|------|-----|-----|-----|-----|------|
| **设计表**（dsp_8ch_report §2.1） | 31 tap | 63 tap | 63 tap | 63 tap | `dsp_8ch_report.md:40-45`；`dsp_migration_inventory.md:14` |
| **C 实际**（tree_filterbank） | **单一共享 63-tap 半带原型** | 同 | 同 | 同 | `tree_filterbank.h:53,113-114`；`tree_filterbank.c:65-72` |

**C 实际口径**：`tfb_set_coeffs(hb_coef_q15, ntaps)` 注入**唯一一组** `g_hb`（`tree_filterbank.c:65,68`），头注释明写"**所有级/通道共享同一原型半带核**"（`tree_filterbank.h:113-114`）；`TFB_HB_TAPS=63`（`:53`）。差分金字塔不是按子带配不同阶 FIR，而是**同一 63-tap 半带原型在 dyadic 树各级复用**，子带由 telescoping 残差产生，不由"每子带一条独立阶数 FIR"产生。

> **本路线图一律按 C 实际口径（统一 63-tap 共享原型）做映射**，并标注此差异：**设计表的 SB0=31 tap 是规格层标称，C 实现未采用**（若未来 G3 系数接线决定 SB0 单独用 31-tap，需回头修映射 + golden 重生成）。R14 golden（`0x90556BC7`）就是按 C 实际口径生成的，**映射对齐 C 而非设计表**。

### 3.2 哪些段可 offload 到 FIRA（半带卷积），哪些必须核内（残差减/合成加/钳位）

继承 DOC-S4-FIRA-FIT §2.3 的逐操作判定（不重推）：

| 操作 | 出处 | FIRA？ | FIRA 模式 |
|------|------|--------|----------|
| `hb_decimate2`（dec2(LP)，取偶相位） | `tree_filterbank.c:108-117` | ✅ **可 offload** | DECIMATION，ratio=2（hwref:75669-75682） |
| `hb_interp2`（零插值+半带 LP+×2） | `tree_filterbank.c:121-132` | ✅ **可 offload** | INTERPOLATION，ratio=2（hwref:75684-75688）；×2 折进系数或核内 |
| detail 残差 `sb = a − interp2(coarse)` | `tree_filterbank.c:161-163` | ❌ **核内** | FIRA 只 MAC，无向量减（hwref:75289-75296） |
| 合成端 `sat_add_i32` 逐子带加 | `tree_filterbank.c:55-61,197-205` | ❌ **核内** | 向量加 + 饱和，非 FIR |
| 子带增益 `q31_mul`（broadside g=1） | `tree_filterbank.c:178-181` | ⚠️ broadside 时省；非 broadside 折进系数或核内 | — |
| 饱和钳位 `sat_i64_to_i32` | `tree_filterbank.c:47-52,104,127` | ❌ **核内** | FIRA 80-bit MR 无 Q31 钳位语义（§4） |
| 8ch broadside 求和 `sat_add_i32` | `tfb_8ch.h:12`（包裹层） | ❌ **核内** | 跨通道向量加 |

→ **Split-Task 模型**（EE408，eenote:420-435）：**FIRA 做半带卷积，核做残差减 / 合成加 / 饱和钳位 / broadside 求和**。不是"整条链甩给 FIRA 核就空闲"。

### 3.3 3 级 dyadic 树 × 8（或 16）通道 → FIRA task 队列拆分

每通道的半带卷积实例（`tree_filterbank.h:104-107`，C 实际）：
- 分析侧：`ana_dec[3]`（3 个 decimating 半带）+ `ana_int[3]`（3 个 interpolating 半带，求 detail）；
- 合成侧：`syn_int[3]`（3 个 interpolating 半带）；
- = **每通道 9 个 63-tap 半带段**。

**channel/TCB 映射**（每个半带段 = 1 个 FIRA channel）：

| 段 | 输入率 | 输出率 | FIRA 模式 | Window Size（= 输出样本数） | 备注 |
|----|--------|--------|-----------|------------------------------|------|
| ana_dec[0] | f0=frame | f1=frame/2 | DECIMATION r=2 | frame/2 | dec 跳过被丢样点的计算（hwref:75673-75674） |
| ana_dec[1] | f1 | f2=frame/4 | DECIMATION r=2 | frame/4 | |
| ana_dec[2] | f2 | f3=frame/8 | DECIMATION r=2 | frame/8 | |
| ana_int[2] | f3 | f2 | INTERPOLATION r=2 | f2；WINDOWSIZE=n×RATIO 约束满足（frame=8 倍数，tree_filterbank.h:124） | 求 detail 用 |
| ana_int[1] | f2 | f1 | INTERPOLATION r=2 | f1 | |
| ana_int[0] | f1 | f0 | INTERPOLATION r=2 | f0 | |
| syn_int[2] | f3 | f2 | INTERPOLATION r=2 | f2 | 合成 |
| syn_int[1] | f2 | f1 | INTERPOLATION r=2 | f1 | 合成 |
| syn_int[0] | f1 | f0 | INTERPOLATION r=2 | f0 | 合成 |

**抽取/插值用 Sampling+Ratio 字段（不核内做）**：`eSampling=DECIMATION/INTERPOLATION` + `nSamplingRatio=2`（V2:92-93, 237）。两约束我方都满足：比率=2 整数 ✅、tap=63≪1024 ✅（hwref:75697-75698）。⚠️ **ADI 例程无抽取/插值示例代码**（全 SINGLE_RATE，MCP.c:133 等）——此为有 API/HW 支持但无参考代码的路径（§5 风险）。

**队列拆分方案**：
- **数据依赖链**：分析侧 ana_dec[0]→[1]→[2] 串行（下级吃上级输出），ana_int 各级依赖对应 a；合成侧 syn_int[2]→[1]→[0] 串行。**级间有依赖 → 用 ACM 回调链**（每 channel 完成回调里 queue 下一级，PIPE.c 模式）。
- **通道并行**：8（或 16）个阵元通道之间**互相独立**（`tfb_8ch.h:24` `ana[NCH]` 严格独立），同一级的不同通道可批量放进同一 task 的 channel list 并行。
- **规模**：8ch×9 段 = 72 channel/帧；16ch×9 = 144 channel/帧。Legacy ≤32 → 需多次 queue；**ACM 无上限**（eenote:63-68）更顺，且支持逐通道 dec/int 模式 + 逐通道定点。→ **倾向 ACM**（§2.3）。
- **detail 减法 / 合成加法 / Q31 饱和钳位 = 核内**，穿插在 FIRA 回调之间（Split-Task，§3.2）。

> 性能数（72/144 channel 的 per-task 开销占比、净 offload 收益）= **待 R14 后实测、不计入选型**（铁律八）。DOC-S4-FIRA-FIT §4.3 的 ~8.6% 是粗算上界，非确定值。

---

## 4. R14 风险点（Q 格式映射）— bit 偏差高发区，逐条列

**总命门**：我方核 = **有符号分数 Q15 系数 × Q31 状态 → Q46(int64) 累加 → `>>15` 回 Q31 + 饱和钳位**（`tree_filterbank.c:6,99,104`）。FIRA 定点 = **32-bit × 32-bit → 80-bit MR**，输入格式枚举只有 **UNSIGNED_INTEGER / SIGNED_INTEGER**（无 signed-fractional）。这套"无符号整数 vs 有符号分数"错配 + signed-fractional 后处理 = bit 偏差高发区。R14 = 逐位证 FIRA 版复现 core-only golden `0x90556BC7`。

### 4.1 累加器宽度差（不丢精度，但截断点不同）— 风险 LOW
- 我方 Q46 = int64（`tree_filterbank.c:89,99`）；FIRA = 80-bit MR（hwref:75714）。FIRA 更宽，**中间不丢精度**。
- **但最终回 Q31 的截断/舍入点不同**：我方是 `acc>>15`（算术右移截断，向负无穷取整）；FIRA 80-bit MR 回写须缩放 + 我方核内再 `>>` 对齐。**截断 vs 舍入差 = 可能 ±1 LSB**。须确认 FIRA 输出回写后核内做的移位与我方 `>>15` **逐位等价**。

### 4.2 系数位宽：Q15(16-bit) → FIRA 32-bit 容器 — 风险 LOW-MEDIUM
- 我方系数 Q15 `int16_t`（`tree_filterbank.c:65`）；FIRA 定点系数 32-bit（hwref:75714）。
- 须把 Q15 **符号扩展**进 32-bit 容器（高位补符号），且**保持小数点位置语义**。若误当无符号或左移对齐错位 → 整体增益错 2^k。**转换点 = 系数头生成时一次性冻结为 32-bit 常量数组**（同 G3 同源性纪律，`core_only_migration_plan.md:91`），不上板重算。

### 4.3 ★ signed-fractional vs UNSIGNED_INTEGER 格式错配 — 风险 **HIGH（最高风险）**
- 驱动枚举只有 UNSIGNED_INTEGER / SIGNED_INTEGER（V2:128-131，MCP.c:141 例程用 UNSIGNED_INTEGER）**[L-src]**；我方是 **signed-fractional Q15×Q31**。
- HW 文档：用 signed-fractional 时输出须 **×2 缩放**（MAC 不右移去冗余符号位）+ **decimate 输出缓冲到目标样点**（hwref:75722-75723）**[L-doc]**。
- **bit 偏差高发点**：(a) 选 SIGNED_INTEGER 当 Q 用 → 小数点语义丢失，整体差 2^k 缩放；(b) ×2 缩放若与我方核内 `>>15` 复合错位 → 系统性增益偏差；(c) decimate 输出后处理若与我方"取偶相位"（`tree_filterbank.c:113`）相位不一致 → 整段错位。**这三处任一错 = golden CRC 必挂。bit-exact 映射 = 待上板实测，桌面无法坐实**（DOC-S4-FIRA-FIT §3.3 / 仍待实测项 #3）。

### 4.4 浮点路径的舍入模式差 — 风险 MEDIUM（仅当改走 FIRA 浮点时）
- 若为降风险改走 FIRA 浮点（与全部 ADI 例程一致），舍入 = `IEEE_ROUND_TO_NEAREST_EVEN`（MCP.c:139）**[L-src]**——**与我方 Q31 定点截断 `>>15`（向负无穷）语义不同** → **逐位必不一致**。
- 此路径下 R14 **不可能 bit-exact 复现定点 golden `0x90556BC7`**（浮点 ≠ 定点）。改走浮点 = 与 LOCKED 定点基线 DEC-S3-PROC-01 冲突 + R14 基准失效 → **决策项，须上报 PM/CTO**，不在本路线图擅自切换。

### 4.5 ×2 内插增益 + 饱和钳位的位置 — 风险 MEDIUM
- 我方 `hb_interp2` 输出 `×2` 后 `sat_i64_to_i32` 钳位（`tree_filterbank.c:127,130`）；FIRA INTERPOLATION 的零插值 + ×2 增益（hwref:75684-75688）与 signed-fractional 的 ×2（§4.3）**可能复合两次 ×2** → 增益错 4×。须明确：×2 只做一次，且钳位**必须留核内**（FIRA 无 Q31 饱和语义）。

### 4.6 decimation 相位对齐 — 风险 MEDIUM
- 我方 `hb_decimate2` 取"每对的第 2 个"（`i&1==1`，`tree_filterbank.c:113`）；FIRA DECIMATION "skips computation of discarded samples"（hwref:75673）的**保留相位**须与我方一致（取偶 vs 取奇）。相位差半样 → detail 残差全错 → CRC 挂。

> **R14 风险汇总**：最高风险 = §4.3 signed-fractional 格式错配（HIGH，桌面无法坐实，必须上板逐位回归）。其余为 LOW-MEDIUM 的截断点/相位/×2 对齐。**所有这些只有上板逐位比对 golden `0x90556BC7` 才能证伪**（§5.3）。

---

## 5. FIRA 集成路线图

> **前置闸门**：本路线图的**任何编码动作都在 R1 板测 + core-only R14（DOC-S4-CORE-PLAN-01）通过之后**才启动。FIRA 性能数一律"待 R14 后实测、不计入选型"（铁律八 / C9）。

### 5.1 步骤清单（core-only → FIRA 版怎么改）

| 步 | 动作 | 依赖 | 出处/对照 |
|----|------|------|----------|
| **F0** | **前置**：R1 板测完 + core-only 板上 R14 逐位通过（golden `0x90556BC7`），拿到 core-only 真实 cycle 基准 | 板测 | `core_only_migration_plan.md` G2-G5 |
| **F1** | 装 21569 BSP 的 CCES 工程，拿到 SHARC 侧 `adi_fir_2156x.h` 真结构体（替换本单 [proxy] 字段） | F0 | DOC-S4-FIRA-FIT 仍待实测 #6 |
| **F2** | 选 ACM 模式（逐通道 dec/int + 逐通道定点 + 链式回调，§2.3） | F1 | EE408 / PIPE.c 模式 |
| **F3** | 系数：把 Q15 半带原型符号扩展冻结为 **32-bit 定点常量数组**（同源，不上板重算，§4.2） | F1 | `core_only_migration_plan.md:91` |
| **F4** | 把 `hb_decimate2`/`hb_interp2` 的核内卷积替换为 FIRA channel（DECIMATION/INTERPOLATION + ratio=2），延迟线重排为 FIRA `TapLen+Window-1` 布局（§4.6, §1.2） | F2,F3 | V2:92-93,237 |
| **F5** | 保留核内：detail 减法 / 合成加法 / `sat_*` 钳位 / 8ch broadside 求和（Split-Task，§3.2），穿插在 FIRA 回调之间 | F4 | `tree_filterbank.c:55-61,104,161-163`；`tfb_8ch.h:12` |
| **F6** | 定点 signed-fractional 格式对齐：×2 缩放 + decimate 后处理 + 核内 `>>15` 一致化（§4.3, §4.5）——**bit-exact 攻坚点** | F5 | hwref:75722-723 |
| **F7** | **R14 回归**：FIRA 版输出 vs core-only golden 逐位/CRC 比（§5.3），sat+unsat 双套 | F6 | `golden_ref.h:26` |
| **F8** | 通过 R14 后才实测 FIRA cycle，做 core-only vs FIRA-offload 对比（**此时性能数方可进选型**） | F7 PASS | 解锁铁律八 |

### 5.2 新增 / 改动文件清单（规划，**本单不创建**）

| 文件 | 新增/改动 | 内容 |
|------|----------|------|
| `sprint4/dsp/fira/tfb_fira.c/.h`（新） | 新增 | FIRA 版分析/合成：channel list 构造 + QueueTask + 回调链；调核内 `sat_*`/残差减 |
| `sprint4/dsp/fira/fir_coeffs_q31.h`（新） | 新增 | Q15→32-bit 符号扩展冻结系数（F3，同源） |
| `sprint4/dsp/fira/adi_fir_config_2156x.h`（新，BSP 提供后定制） | 新增 | ACM 模式开关 + 单核守卫 |
| `tree_filterbank.c/.h` | **不改算法核** | 复用核内 `sat_i64_to_i32`/`sat_add_i32`/`q31_mul`（Split-Task 核侧原语）；保持 md5/CRC 不变 |
| `bench/gen_golden.c` + `golden_ref.h` | 复用，不改 | golden `0x90556BC7` 是 FIRA 版的回归真值，**不重生成**（否则失去对照基准） |
| `bench/fira_regression.c`（新） | 新增 | F7 板上 FIRA 输出抓取 + 逐位/CRC 比对 harness |

### 5.3 R14 bit-exact 回归方案（FIRA 输出 vs core-only golden）

继承 DEC-S4-DSP-01 + DOC-S4-CORE-PLAN-01 §5 的判定口径：

1. **基准**：core-only 单通道 65536-sample（FRAME 64 × 1024 帧）Q31 输出，CRC32(IEEE 802.3) = **`0x90556BC7`**（`golden_ref.h:26`）+ `GOLDEN_SPOT[64]`（stride 1024 逐位 spot，`golden_ref.h:28-37`）。
2. **输入**：同一 0.289 chirp（−6dBFS + −4.8dB headroom）Q31 序列（`golden_ref.h:11`；`core_only_migration_plan.md:162`）。
3. **比对域 = Q31 整数逐位，容差 0**（不用例程的浮点 `Find_Max_Diff` 相对误差，MCP.c:300）。FIRA 版每帧输出还原到 Q31 整数后算 CRC32 + 逐 spot 比。
4. **判据（二值）**：FIRA 版 CRC32 == `0x90556BC7` **且** 64 个 spot 全等 → R14 PASS（重建逐位等价）；任一不等 → FAIL，定位到 §4 哪条偏差。
5. **sat+unsat 双套**：core-only 已证 0.289 chirp 单通道**不触发饱和**，故 SAT==UNSAT 两 build CRC 均 `0x90556BC7`（`golden_ref.h:12-13`）。FIRA 版同样跑 sat/unsat 双 build，**两者都须 == `0x90556BC7`** → 证 FIRA MAC/滤波路径 bit-exact（饱和原语本身不被此输入覆盖，属 GAP-SAT，由 8ch ~8× 过载行为校验另补，`golden_ref.h:14-15`）。
6. **诚实边界**：桌面 golden 为 [L2]；**FIRA 版板上逐位通过后**，重建正确性升 [L1]（含 FIRA DMA/80-bit MR/相位/cache 真值）。🚫 禁把桌面 [L2] 当板上 [L1]（`core_only_migration_plan.md:173`）。

### 5.4 已知风险 + 缓解

| 风险 | 级别 | 缓解 |
|------|------|------|
| signed-fractional 格式错配（§4.3） | **HIGH** | F6 专项攻坚；先在 CCES SHARC 仿真器单段（1 个 dec 半带）打通 bit-exact 再扩全链；若打不通 → 上报决策（保定点核内适配 vs 不 offload） |
| 抽取/插值无 ADI 示例代码（§3.3） | MEDIUM | F4 先单 channel DECIMATION 小例验证相位（§4.6）再批量 |
| 浮点路径破坏定点 R14 基准（§4.4） | MEDIUM | **不擅自切浮点**；如要切 = 上报 PM/CTO（冲突 DEC-S3-PROC-01） |
| 63-tap 小核 per-task 开销吞收益（§3.3） | MEDIUM | F8 实测，合并通道/减 TCB 数；**收益不进选型直到 R14**（铁律八） |
| SHARC 侧 adi_fir_2156x.h 本机未装（[proxy] 字段） | LOW | F1 装 21569 BSP 后校实 |
| L1 容量放不下 16ch 全缓冲 | LOW | F4 排布后核算（5Mb L1，ds:295）；放不下走 L2/L3 + cache flush |

### 5.5 路线图首步（明确）
**F0**：等 R1 板测 + core-only 板上 R14 逐位通过（golden `0x90556BC7`），拿到 core-only 真实 cycle 基准——**在此之前不动 FIRA 任何代码**。

---

*DOC-S4-FIRA-PLAN-01 · dsp-algorithm teammate · 2026-06-02 · 分析+路线图，未写 FIRA 代码*

