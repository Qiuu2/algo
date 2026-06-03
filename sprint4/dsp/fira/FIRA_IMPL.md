# FIRA 集成实现说明 — 草案代码 + R14 转换 + bit-exact 协议 + cycle 方案

**文档 ID**：DOC-S4-FIRA-IMPL-01
**任务**：dsp-algorithm teammate（R1/R14 解锁后，按 DOC-S4-FIRA-PLAN-01 F0–F8 实现 FIRA 集成）
**日期**：2026-06-03
**性质**：**草案代码 + 实现文档 + 验证协议**。本机无 SHARC 工具链（CCES ARM-only）+ 无 FIRA 硬件 → FIRA 代码无法本机编译/板上验证。
**上游**：DOC-S4-FIRA-PLAN-01（`sprint4/dsp/fira_integration_plan.md`，F0-F8 蓝图）；DOC-S4-FIRA-FIT（`sprint3/audit/fira_fit_assessment.md`）。

---

## 0. 🔴 诚实边界（硬约束，禁删，违者 BLOCKER）

| 项 | 状态 | 证据级别 |
|----|------|---------|
| 草案代码 `fira_tree.{c,h}` / `fira_regression.c` / `fir_coeffs_q31.h` | 已写，**未编译** | 草案 |
| adi_fir_* API 用法 | 严格仿例程 MCP.c:128-285 | [proxy]（ARM v2 头 + 例程注释，21569 SHARC 头本机未装） |
| 板上 R14 bit-exact（crc==0x90556BC7） | **未验证** | [L1/EZKIT] 台架回填 |
| FIRA 版 cyc_8ch_frame 实测 | **未测** | [L1/EZKIT] 台架回填 |
| profile 优化建议（硬件循环等） | 分析，**未反汇编确认** | 待台架反汇编 |

- 🚫 本文件/代码**绝不声称**"已编译 / 已 bit-exact 通过 / 已实测 cycle"。
- F0 三闸门**已满足**（任务前提）：R1 cycle 基准 `cyc_8ch_frame=1,006,935`；core-only 板上 bit-exact `crc=0x90556BC7 PASS`。本任务在此之上做 FIRA 版草案 + 验证协议。
- 🔴 **铁律八 / C9**：R14 板上 crc==0x90556BC7 通过前，FIRA 收益/裕量**不得写进任何选型依据**（违者 BLOCKER）。R1 现纯核不足 → FIRA 必需，但 **R1 闭合 gating 于 R14 板上通过**。本文所有性能位一律标"待 R14 后实测、不计入选型"。

---

## 1. 文件清单（本任务产出）

| 文件 | 角色 | 状态 |
|------|------|------|
| `sprint4/dsp/fira/fira_tree.h` | FIRA 树通道接口 + 段枚举 + [proxy] 占位类型 | 草案 |
| `sprint4/dsp/fira/fira_tree.c` | Split-Task 编排（ACM channel 构造 + 生命周期 + 留核段 + R14 后处理） | 草案·未编译 |
| `sprint4/dsp/fira/fira_regression.c` | F7 R14 回归 harness（FIRA 输出 → CRC32+spot vs golden） | 草案·未编译 |
| `sprint4/dsp/fira/fir_coeffs_q31.h` | F3 Q15→32-bit 冻结系数（占位，台架填实） | 占位 |
| `sprint4/dsp/fira/FIRA_IMPL.md` | 本文档（DOC-S4-FIRA-IMPL-01） | — |

不改：`tree_filterbank.{c,h}`（算法核，复用 sat_*/q31_mul 语义）、`bench/golden_ref.h`（R14 真值，0x90556BC7，不重生成）、`bench/chirp_input.h`（冻结输入）。

---

## 2. F0–F8 实现说明

> Split-Task 总则（plan §3.2）：**FIRA 做 9 个 63-tap 半带卷积段（dec×3 / ana_int×3 / syn_int×3）；核内做 detail 残差减 / 合成加 / Q31 饱和钳位 / ×2 内插增益 / 8ch broadside 求和**。代码落点：`fira_tree.c` §C(后处理)/§D(编排) + 复用 `tree_filterbank.c:47-61` 的 sat_*。

| 步 | 动作 | 代码落点 | 状态 |
|----|------|---------|------|
| **F0** | 前置三闸门：R1 cycle 基准 1,006,935 + core-only 板上 crc=0x90556BC7 PASS | — | ✅ 已满足（任务前提） |
| **F1** | 装 21569 BSP，拿真 `adi_fir_2156x.h`，替换 `fira_tree.h` 的 [proxy] 占位 typedef + 定义 `FIRA_USE_REAL_ADI_FIR_HEADER` | `fira_tree.h` §[proxy]；`fira_tree.c` 顶部 `#include` | 🔴 待台架 |
| **F2** | 选 **ACM 模式**（逐通道 dec/int + 逐通道定点 + 链式回调，plan §2.3） | `fira_tree.c` `fira_make_channel`（ACM 字段 bFixedEnable/eFixedFormat 在 `#if ACM` 内，仿 MCP.c:135-142） | 🔴 待台架 |
| **F3** | 系数：Q15 半带原型符号扩展冻结为 32-bit 常量数组（同源不重算） | `fir_coeffs_q31.h`（占位 0，台架填实） + `fira_tree_set_coeffs()` | 🔴 占位待填 |
| **F4** | `hb_decimate2`/`hb_interp2` → FIRA channel（DECIMATION/INTERPOLATION + ratio=2）；延迟线重排为 `TapLen+Window-1` 布局 | `fira_make_channel`：`eSampling`/`nSamplingRatio=2`/`InCount=TapLen+Window-1`（MCP.c:151） | 🔴 待台架 |
| **F5** | 留核：detail 减 / 合成加 / sat 钳位 / broadside 求和，穿插 FIRA 回调之间 | `fira_tfb_analyze`(detail 减) / `fira_tfb_synthesize`(sat_add)；8ch 求和复用 `tfb_8ch.c` | 草案已写留核段 |
| **F6** | signed-fractional 对齐：×2 缩放 + decimate 后处理 + 核内 >>15 一致化（**bit-exact 攻坚**） | `fira_postscale_dec/int`（§C，[ASSUME] 移位量待台架逐位定） | 🔴 待台架攻坚 |
| **F7** | R14 回归：FIRA 版输出 vs golden 逐位/CRC，sat+unsat 双套 | `fira_regression.c` `fira_r14_regression()` | 🔴 待台架（桌面 plumbing 无效） |
| **F8** | R14 PASS 后才实测 FIRA cycle，做 core-only vs FIRA 对比（性能数此时方可进选型） | `fira_regression.c` 末注（用 `bench_cyc_target` CCNT） | 🔴 待台架，gating 于 F7 |

**抽取/插值实现选择**（plan §3.3 问题点）：用 FIRA **Sampling+Ratio 字段**（`eSampling=DECIMATION/INTERPOLATION`,`nSamplingRatio=2`），不核内做——两约束满足（比率=2 整数 ✅、tap=63≪1024 ✅，hwref:75697-98）。⚠️ **[ASSUME]**：ADI 例程全 SINGLE_RATE（MCP.c:133），**无 dec/int 示例代码** → 此路径有 API/HW 支持但无参考代码，**相位/×2 行为必上板验**（§4.6/§4.5）。**备选**（若台架 dec/int 模式行为与核取偶相位对不齐）：核内做抽取/插值、FIRA 只做 SINGLE_RATE 全速率卷积——但失去 dec "跳过丢弃样点" 的算力优势。最终选择 = 台架 F4 单 channel 小例验相位后定。

## 3. R14 Q 格式转换点（逐条，bit 偏差高发，必上板逐位）

**总命门**（plan §4）：我方核 = **有符号分数 Q15 系数 × Q31 状态 → Q46(int64) 累加 → `>>15` 回 Q31 + 饱和钳位**（`tree_filterbank.c:6,99,104`）。FIRA 定点 = 32×32→80-bit MR，输入格式枚举只有 **UNSIGNED_INTEGER / SIGNED_INTEGER**（MCP.c:141，无 signed-fractional）。下表每条标偏差级别 + "必上板逐位"。

| # | 转换点 | 我方核 | FIRA 侧 | 偏差级别 | 代码落点 | 必上板逐位 |
|---|--------|--------|---------|---------|---------|-----------|
| R14-1 | 累加器宽度 + 回 Q31 截断点 | int64 Q46，`acc>>15` 截断（向负无穷） | 80-bit MR，回写须缩放 | **LOW**（更宽不丢精度，但截断 vs 舍入差 ±1 LSB） | `fira_postscale_dec`：`>>15` 不用 IEEE round | ✅ 截断 vs 舍入 ±1 LSB → CRC 挂 |
| R14-2 | 系数 Q15→32-bit 容器 | Q15 int16（`tree_filterbank.c:65`） | 32-bit，符号扩展，小数点保持 | **LOW-MED** | `fir_coeffs_q31.h`（占位待填，符号扩展或 `<<16` 二选一） | ✅ 误当无符号/对齐错位 → 增益错 2^k |
| **R14-3 ★** | **signed-fractional vs UNSIGNED/SIGNED_INTEGER 格式错配** | signed-fractional Q15×Q31 | 仅 UNSIGNED/SIGNED_INTEGER 枚举；signed-fractional 输出须 **×2 缩放 + decimate 后处理**（hwref:75722-723） | 🔴 **HIGH（最高）** | `fira_make_channel` `eFixedFormat=SIGNED_INTEGER` + `fira_postscale_*` | ✅ **桌面无法坐实**，必上板逐位 |
| R14-4 | 浮点舍入模式（仅若改走 FIRA 浮点） | Q31 定点截断 `>>15` | `IEEE_ROUND_TO_NEAREST_EVEN`（MCP.c:139） | MED | 不走（保定点）；如要切=**上报 PM/CTO** | 浮点≠定点 → R14 必不 bit-exact |
| R14-5 | ×2 内插增益位置 | `hb_interp2` 输出 ×2 后 sat（`tree_filterbank.c:127,130`） | INTERPOLATION 零插值自带 ×2（hwref:75684-88）+ signed-fractional ×2 → 可能复合 4× | MED | `fira_postscale_int`：**×2 只一次** + sat 留核 | ✅ 复合两次 ×2 → 增益错 4× |
| R14-6 | decimation 相位对齐 | 取偶相位 `i&1==1`（`tree_filterbank.c:113`） | DECIMATION "skip discarded samples"（hwref:75673），保留相位须一致 | MED | `fira_make_channel` DEC 段；F4 单 channel 验相位 | ✅ 相位差半样 → detail 全错 → CRC 挂 |

> **最高风险 R14-3**（HIGH）：signed-fractional 格式错配三处复合（(a) SIGNED_INTEGER 当 Q 用丢小数点 → 增益差 2^k；(b) ×2 缩放与核内 >>15 复合错位 → 系统性增益偏差；(c) decimate 后处理与取偶相位不一致 → 整段错位）。**这三处任一错 = golden CRC 必挂**。**桌面无法坐实**（DOC-S4-FIRA-FIT §3.3 仍待实测 #3）；F6 攻坚先在 CCES SHARC 仿真器单段（1 个 dec 半带）打通 bit-exact 再扩全链；打不通 → 上报决策（保定点核内适配 vs 不 offload）。

## 4. bit-exact 验证协议（crc==0x90556BC7）

**一句话**：FIRA 版单通道链跑同一冻结 chirp 65536 样本 → 还原 Q31 整数 → CRC32(IEEE 802.3) **必须 == `0x90556BC7`** 且 64 个 stride-1024 spot 全等（容差 0），sat+unsat 双 build 均须等，才算 R14 PASS（证 FIRA 版数值等价 core-only 核）。

**接入方式**（复用现成 harness，任务要点 3 / plan §5.2-5.3）：
1. **基准不变**：core-only golden `0x90556BC7` + `GOLDEN_SPOT[64]`（`bench/golden_ref.h:28,30-39`）。**FIRA 版是被验方，golden 不重生成**（否则失去对照）。
2. **替换卷积段**：`fira_regression.c` 把 `tfb_analyze/tfb_synthesize` 换成 `fira_tfb_analyze/fira_tfb_synthesize`，输出仍走与 `bench_harness.c:30` **逐位同算法**的 `crc32_buf` + `GOLDEN_CRC32`/`GOLDEN_SPOT` 比对。输入 = 同一冻结 `CHIRP_INPUT[]`（`bench/chirp_input.h`，−6dBFS + −4.8dB headroom），无运行期 double（消架构分叉）。
3. **比对域** = Q31 整数逐位，**容差 0**（不用例程浮点 `Find_Max_Diff` 相对误差，MCP.c:300）。
4. **判据（二值）**：`fira_r14_regression()` 返回 `crc_match && spot_match`。CRC==`0x90556BC7` 且 64 spot 全等 → R14 PASS；任一不等 → FAIL，定位到 §3 哪条（R14-1..6）。
5. **sat+unsat 双套**：0.289 chirp 单通道不触发饱和 → SAT==UNSAT，两 build CRC 均须 `0x90556BC7`（`golden_ref.h:27`）。FIRA 版同跑两 build 都须等 → 证 FIRA MAC/滤波路径 bit-exact（饱和原语本身未被此输入覆盖 = GAP-SAT，由 8ch ~8× 过载行为另校，`golden_ref.h:15-17`）。
6. **诚实边界**：桌面 golden = [L2]；**FIRA 版桌面跑无意义**（`fira_tree_setup()` 桌面返回 -1，`fira_r14_regression` 直接返回 0，不冒充）。**板上逐位通过后** R14 升 [L1]（含真 FIRA DMA / 80-bit MR / 相位 / cache）。🚫 禁把桌面 [L2] 当板上 [L1]（`core_only_migration_plan.md:173`）。

## 5. cycle 方案

- **量法**：FIRA 版 `cyc_8ch_frame` 用现成 CCNT 抽象 `bench_cyc_target()`（`bench_harness.c:39`，`TARGET_SHARC` 下 `BENCH_CYC()`），与纯核同口径（free-run cycle counter，`CCNT_source.md` 待回填真寄存器名）。稳态单帧测法沿用 `bench_harness.c:73-100`（热身 4 帧扣冷 cache）。
- **对比**：FIRA 版 `cyc_8ch_frame` vs 纯核基准 **1,006,935**（F0，[L1] 已实测）。新裕量 = 帧周期 / `cyc_8ch_frame`；帧周期 = FRAME/FS = 64/48000 = 1.333 ms。16ch deadline：`cyc_16ch_est = cyc_8ch_frame + 8*cyc_analyze_1ch`（`bench_harness.c:99` 同换算），须 < 帧周期 cycle 数（1 GHz × 1.333ms = 1,333,333 cycle）。
- **🔴 红线（铁律八/C9）**：FIRA `cyc_8ch_frame` / 新裕量 / 16ch deadline **全部标 [L1/EZKIT] 待台架**，且 **R14 板上 crc==0x90556BC7 通过前不得写进任何选型依据**（gating 于 F7 PASS，违者 BLOCKER）。本任务不报任何 FIRA 收益数值。
- **预期方向**（仅定性，非选型数）：63-tap 小核 → FIRA per-task 固定开销（ACM QueueTask 329-371 / 中断 423-595 core cycle，EE408 Table 1）可能吞掉部分 offload 收益；72/144 channel 的开销占比待 F8 实测。**不写具体倍数**。

## 6. profile 留核部分分析 + 优化建议（并行，标"待反汇编确认"，本机无法编译验证）

留核段（Split-Task 核侧，FIRA 不接管）= `tree_filterbank.c` 的 detail 减 / 合成加 / Q31 钳位 / ×2 / 8ch broadside 求和。本节为静态源码分析，**所有效率结论待台架 SHARC 反汇编/profile 确认**。

| 留核段 | 源码 | 静态观察 | 优化建议（待反汇编确认） |
|--------|------|---------|------------------------|
| Q31 饱和钳位 `sat_i64_to_i32` | `tree_filterbank.c:47-52` | 两个分支比较 + 窄化 | SHARC 有饱和 ALU 模式（MR→R 带 sat）；建议用内建饱和位/`__builtin_sat`，省双分支。**待反汇编确认编译器是否已用饱和指令**。 |
| 合成加 `sat_add_i32` | `:55-61` | int64 加 + 双比较 | 同上，SHARC 定点加可带饱和标志；建议 saturating add 内建。**待反汇编**。 |
| detail 残差减 | `:161-163` | 三段循环（f2/f1/f0），逐样 int32 减 | 向量化（SIMD/双 MAC 数据通路）；循环边界编译期常量（frame 8 的倍数）利于展开。**待反汇编确认是否生成硬件循环**。 |
| 8ch broadside 求和 `w_add_i32` | `tfb_8ch.c:54-60` | 8×4 段嵌套加 | 累加树 + 饱和；候选放 FIRA 外的核 SIMD。**待反汇编**。 |
| **FIR 内循环**（若部分段仍核内卷积，或 FIRA 不接管时的回退） | `tree_filterbank.c:97-100` | `for k<N` 环形读 + int64 MAC，**N=63 编译期已知** | 🔴 **SHARC 零开销硬件循环**：内循环 trip count 编译期常量 → 用 `#pragma SIMD_for` / `#pragma loop_count(min=63,max=63)` 触发硬件 loop（LCNTR/DO-UNTIL），消循环开销；半带核**约半数抽头为 0**（`tree_filterbank.c:8-9`）→ 零系数跳过表可砍半 MAC。**两者均待反汇编确认是否落硬件循环 + 是否真跳零乘**。 |

> ⚠️ 全部 [待反汇编]：本机 CCES ARM-only，无法编 SHARC 目标，更无法看 SHARC 反汇编。以上为源码层建议，**真实指令选择 / 硬件循环 / 零乘跳过 = 台架反汇编 + profile 确认**。不声称任何加速倍数。

## 7. 待台架清单（[L1/EZKIT]，本机无法做）

1. **F1**：装 21569 BSP（CCES 工程），拿真 `adi_fir_2156x.h`，替换 `fira_tree.h` [proxy] 占位 typedef，定义 `FIRA_USE_REAL_ADI_FIR_HEADER`，校实 `ADI_FIR_CHANNEL_INFO` 字段名/顺序（草案仿 MCP.c:128-160，真名以 BSP 头为准）+ `FIR_MEM_SIZE()` 宏 + ACM 枚举（`ADI_FIR_SAMPLING_DECIMATION/INTERPOLATION`、`ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER`、`ADI_FIR_EVENT_CHANNEL_DONE`）。
2. **F3**：`fir_coeffs_q31.h` 占位 0 → 用 `fir_design_verify.py` 导出真 63-tap Q15，按 R14-2 确定对齐（符号扩展 or `<<16`）冻结。
3. **F4**：单 channel DECIMATION 小例验**相位**（取偶 vs 取奇，R14-6）；INTERPOLATION 小例验 ×2（R14-5）。
4. **F6**：signed-fractional 格式 bit-exact 攻坚（R14-3 HIGH）——CCES SHARC 仿真器单段（1 dec 半带）打通逐位再扩全链；定 `fira_postscale_*` 真移位/缩放量。
5. **F7**：板上跑 `fira_r14_regression()`，sat+unsat 双 build，crc 均须 == `0x90556BC7` + 64 spot 全等。
6. **F8（gating F7）**：实测 FIRA `cyc_8ch_frame`（真 CCNT）vs 纯核 1,006,935，算新裕量 + 16ch deadline。
7. **profile**：SHARC 反汇编确认留核段饱和指令 / 硬件循环（LCNTR）/ 半带零乘跳过（§6 全部 [待反汇编]）。
8. **L1 容量**：F4 排布后核 16ch 全缓冲是否进 5Mb L1（ds:295），放不下走 L2/L3 + cache flush。

## 8. 挂接 / 红线落实

**挂接（cross-ref）**：
| 锚点 | 落实 |
|------|------|
| **DOC-S4-FIRA-PLAN-01** | 本实现按其 F0-F8 + §3 映射 + §4 R14 + §5 路线图逐条落代码/文档 |
| **R14** | bit-exact 闸门：§4 协议（crc==0x90556BC7），`fira_regression.c` 实现，板上 [L1] 通过前收益冻结 |
| **R1** | F0 已闭（cyc_8ch_frame=1,006,935）；R1 纯核不足→FIRA 必需，但 **R1 闭合 gating 于 R14 板上通过** |
| **DEC-S4-DSP-01** | bit-exact 基准 = C golden（sat/unsat 双套）+ 容差 0，§4 沿用，MATLAB 不补 |
| **铁律八 / C9** | FIRA 性能数写进选型 = BLOCKER；§5 全标"待 R14 后实测、不计入选型"，本文档零收益数 |
| **DEC-S3-PROC-01** | LOCKED 定点基线；不擅自切 FIRA 浮点（R14-4），如切=上报 PM/CTO |
| **golden CRC** | `bench/golden_ref.h:28` = `0x90556BC7`，FIRA 版回归真值，**不重生成** |

**红线落实自查**：
- ✅ 草案代码 + 文档 + 协议，**未编译/未板验**，文件头均标"草案·未编译·API 仿例程·台架编译+逐位验证"。
- ✅ 每个未验证假设标 [ASSUME]/[proxy]/[L1/EZKIT]；API 仿例程 MCP.c:128-285。
- ✅ 🚫 全文/全代码无"已编译/已 bit-exact/已实测 cycle"声称。
- ✅ R14 转换点逐条挂出处（plan §/MCP.c file:line/hwref 页/tree_filterbank file:line）。
- ✅ R14 板上 crc==0x90556BC7 通过前，FIRA 收益/裕量**不写进任何选型依据**（铁律八/C9），本文档零性能数值。
- ✅ 草案构建下 `fira_tree_setup()` 返回 -1、`fira_r14_regression()` 返回 0，**不冒充桌面验证**。

---

*DOC-S4-FIRA-IMPL-01 · dsp-algorithm teammate · 2026-06-03 · 草案代码+实现文档+验证协议，未编译/未板验，全部待台架回填*
