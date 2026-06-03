# FIRA 集成实现说明（合并工作文档）— 真 Legacy API · F0/F1 已闭 · F2-F8 台架 runbook

**文档 ID**：DOC-S4-FIRA-IMPL-01（合并 FIRA 工作单正文 + 草案代码说明 + F2-F8 板上 runbook + 验收）
**任务**：dsp-algorithm teammate（DOC-S4-FIRA-IMPL-01 工作单，F0/F1 已完成；本次用**真 Legacy API**把草案更新为台架可直接编译起步版 + 合并工作文档）
**日期**：2026-06-03
**性质**：**草案代码 + 实现文档 + 板上 runbook + 验证协议**。本机无 SHARC 工具链（CCES ARM-only）+ 无 FIRA 硬件 → FIRA 代码无法本机编译/板上验证。台架拿**这一份**可从 F2 开跑。
**上游**：DOC-S4-FIRA-F1-01（F1 模式/格式决策，本目录）；DOC-S4-FIRA-PLAN-01（F0-F8 蓝图）；DOC-S4-IFACE-SURVEY-01。

---

## 0. 🔴 诚实边界（硬约束，禁删，违者 BLOCKER）

| 项 | 状态 | 证据级别 |
|----|------|---------|
| 草案代码 `fira_tree.{c,h}` / `fira_regression.c` / `fir_coeffs_q31.h` | 已写（真 Legacy API），**未编译** | 草案 |
| adi_fir_* API 签名 | **真 Legacy**（归档头 `adi_fir_legacy_2156x.h`，10 函数 + ADI_FIR_CHANNEL_INFO + 枚举，G1 闭合） | [L1 归档头]，行为 [L1/EZKIT] 待台架 |
| 生命周期顺序 | 仿官方 Legacy 实例 MCP.c:243-285 | [L1 例程] |
| Path B 运行时定点（FixedPointEnable SIGNED 在 Legacy 下独立生效） | F1 分析推荐，**Legacy 下是否需配全局宏未明说** | [L1/EZKIT] F2/F3 待台架 |
| 板上 R14 bit-exact（crc==0x90556BC7） | **未验证** | [L1/EZKIT] 台架回填 |
| FIRA 版 cyc_8ch_frame 实测 | **未测** | [L1/EZKIT] 台架回填 |

- 🚫 本文件/代码**绝不声称**"已编译 / 已 bit-exact 通过 / 已实测 cycle"。所有板上数标 [L1/EZKIT]。
- 🔴 **铁律八 / C9**：R14 板上 crc==0x90556BC7 通过前，FIRA 收益/裕量**不得写进任何选型依据**（违者 BLOCKER）。本文所有性能位一律标"待 R14 后实测、不计入选型"，本文档零收益数值。

---

## 1. 已钉死的事实（F1 锁定，直接用）

| 项 | 结论 | 出处 |
|----|------|------|
| **模式** | **LEGACY** | F1 §2 / DOC-S4-FIRA-F1-01；MCP.c:281 `while(FIRTaskDoneCount<N_TASKS)` |
| **定点格式** | **Path B 运行时**：`adi_fir_FixedPointEnable(hTask, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER)`，**CreateTask 后、QueueTask 前**调；**config 头一行不动**（FixedPointEnable 直写 FIRCTL1 TC 位=有符号二补码 + FXD 位=定点，无宏门控，自足） | F1 §1/§3；legacy 头:73,42-43 |
| **接口链** | Open → RegisterCallback → CreateTask → **FixedPointEnable(SIGNED)** → QueueTask → 回调(等 FIRTaskDoneCount<N_TASKS, ALL_CHANNEL_DONE) → Close | legacy 头:64-79；MCP.c:243-285 |
| **抽取** | `ADI_FIR_CHANNEL_INFO.eSampling=ADI_FIR_SAMPLING_DECIMATION` + `nSamplingRatio`（per-channel） | F1 §3；legacy 头:33-35,49-50 |
| **内存** | `FIR_MEM_SIZE(N_CH)` 宏（legacy 头:18）；Cache 驱动自管（ADI_CACHE_MANAGEMENT=1，QueueTask flush 输入/系数、invalidate 输出）；**缓冲放置/对齐不当会坏 bit-exact，F4 不过先查这条** | legacy 头:16-18；MCP.c:82-83 #pragma align 32 |

**Legacy CHANNEL_INFO 无内联定点字段**：例程里 `bFixedEnable`/`eFixedFormat`/`Rounding` 字段都在 `#if ACM` 内（MCP.c:135-142），Legacy 编译掉；legacy 头 ADI_FIR_CHANNEL_INFO（:46-54）本就无这些字段 → 定点只能走运行时 FixedPointEnable（Path B）。**草案据此从 ACM 假设改写为真 Legacy。**

---

## 2. 文件清单（本任务产出 / 更新）

| 文件 | 角色 | 状态 |
|------|------|------|
| `sprint4/dsp/fira/fira_tree.h` | FIRA 树接口 + 段枚举 + **真 Legacy 头接入** + 单通道模板声明 | 草案·真 Legacy API |
| `sprint4/dsp/fira/fira_tree.c` | **真 Legacy** CHANNEL_INFO 构造 + 生命周期 + **F2-F4 单通道模板** + Path B FixedPointEnable + 留核段 + R14 后处理 | 草案·未编译·真 Legacy API |
| `sprint4/dsp/fira/fira_regression.c` | F7 R14 回归（FIRA 输出 → CRC32+spot vs golden，桌面返回 -1/0 不冒充） | 草案·未编译 |
| `sprint4/dsp/fira/fir_coeffs_q31.h` | F3 Q15→32-bit 冻结系数（占位 0，台架填实） | 占位 |
| `sprint4/dsp/fira/FIRA_IMPL.md` | 本文档（合并工作单 + runbook + 验收） | — |

**不改（红线）**：`tree_filterbank.{c,h}`（算法核，复用 sat_*/q31_mul 语义）、`bench/golden_ref.h`（R14 真值 0x90556BC7，不重生成）、`bench/chirp_input.h`（冻结输入）、`adi_fir_config_2156x.h`（Path B 自足，config 头不动）、LED 脚手架。

---

## 3. F2-F4 单通道模板（台架起步，可编译起步）

`fira_single_channel_template()`（`fira_tree.c` §B-template）= **台架第一步**：跑通 1 个 DECIMATION 半带段的完整 Legacy 生命周期，验证三件事：
1. **生命周期正确**：Open → RegisterCallback → CreateTask → FixedPointEnable(SIGNED) → QueueTask → 等 1 个 ALL_CHANNEL_DONE → Close，全程无 ADI_FIR_RESULT 错（每步返回独立步骤码 1-6，便于定位）。
2. **Path B 定点生效**（F1 §4 残留 G2）：Legacy 下运行时 `adi_fir_FixedPointEnable(hTask, SIGNED_INTEGER)` 是否独立把任务设为有符号定点（不靠全局 config 宏）。若失效（输出仍按浮点/无符号）→ 回退 Path A（改 config 头，**改前按红线报 CTO**）。
3. **DECIMATION 相位 / ×2**（R14-5/-6）：对单段 out 逐位比小例 golden，定 `fira_postscale_*` 真移位量。

模板要点（真 Legacy）：
- TaskMemory：`#pragma align 32` + `FIR_MEM_SIZE(1)`（真宏，legacy 头:18）。
- CHANNEL_INFO：`fira_make_channel()` 按 legacy 头字段顺序（:46-54）填 nTapLength/nWindowSize/eSampling/nSamplingRatio/系数/输入(=ntaps+window-1)/输出。
- **定点不在 CHANNEL_INFO**（Legacy 无字段）；CreateTask 后立即 FixedPointEnable(SIGNED)，再 QueueTask。
- 草案默认构建（无真头）返回 -1，**不接 FIRA、不冒充**。

**就绪度**：模板序列完整、字段名/顺序按真 Legacy 头、定点走 Path B 正确时点 → **台架定义 `FIRA_USE_REAL_ADI_FIR_HEADER` + 链接 BSP 即可编译起步**。F2 拿它开跑。

---

## 4. F0-F8 板上 runbook（每阶段判据 / 证据要求）

> Split-Task 总则：**FIRA 做 9 个 63-tap 半带卷积段（dec×3 / ana_int×3 / syn_int×3）；核内做 detail 残差减 / 合成加 / Q31 饱和钳位 / ×2 内插增益 / 8ch broadside 求和**。代码落点：`fira_tree.c` §C(后处理)/§D(编排) + 复用 `tree_filterbank.c:47-61` 的 sat_*。

| 阶段 | 动作 | 代码落点 | 判据 / 证据要求 | 状态 |
|----|------|---------|----------------|------|
| **F0** | 前置三闸门：R1 cycle 基准 1,006,935 + core-only 板上 bit-exact crc=0x90556BC7 PASS | — | 证据=R1 报告 + 板上 crc | ✅ 已闭（任务前提） |
| **F1** | 模式/格式决策 + G1/G2 闭合（Legacy + Path B SIGNED + DECIMATION + ALL_CHANNEL_DONE） | F1 文档 + `fira_tree.{c,h}` 头注 | 证据=DOC-S4-FIRA-F1-01 + 归档 legacy 头 | ✅ 已闭 |
| **F2** | CCES SHARC 工程 + 装 21569 BSP；定义 `FIRA_USE_REAL_ADI_FIR_HEADER` `#include <drivers/fir/adi_fir.h>`；跑 `fira_single_channel_template()` | `fira_tree.h` 头接入；`fira_tree.c` §B-template | **判据**：生命周期返回 0（无 ADI_FIR_RESULT 错）；**Path B FixedPointEnable(SIGNED) 不报错** | 🔴 待台架 |
| **F3** | 系数：Q15 半带原型符号扩展冻结为 32-bit 常量数组（同源不重算，`fir_design_verify.py` 导出） | `fir_coeffs_q31.h`（占位 0→真值）+ `fira_tree_set_coeffs()` | **判据**：对齐方式（符号扩展 vs `<<16`）由 F4 单段逐位定；占位 0 禁跑回归 | 🔴 占位待填 |
| **F4** | 单 channel DECIMATION 小例验**相位**（取偶 vs 取奇，R14-6）+ Path B 定点是否生效（G2 残）；INTERPOLATION 小例验 ×2（R14-5）；查缓冲对齐/cache flush（坏 bit-exact 首查项） | `fira_make_channel` + §C `fira_postscale_*` | **判据**：单段 out 逐位 == 小例 golden（容差 0）；定 postscale 真移位量 | 🔴 待台架攻坚 |
| **F5** | 8ch×多段扩展：每路 9 段 CHANNEL_INFO + 每任务 FixedPointEnable(SIGNED)；task 分组/并发度/回调链；留核 detail 减/合成加/sat/broadside 求和穿插 | `fira_tfb_analyze/synthesize`（§D 留核）；8ch 求和复用 `tfb_8ch.c`；§D 已标 F5 扩展 | **判据**：全链 analyze→synthesize 单通道逐位等价核（接 F7） | 🔴 待台架（§D 留 F5 骨架） |
| **F6** | signed-fractional 对齐 bit-exact 攻坚（R14-3 HIGH）：CCES SHARC 仿真器单段打通逐位再扩全链；定 ×2 缩放 + decimate 后处理 + 核内 >>15 一致化 | `fira_postscale_dec/int`（§C，[ASSUME] 待定） | **判据**：单段 → 全链逐位等价；打不通 → 上报决策（保定点核内适配 vs 不 offload） | 🔴 待台架攻坚 |
| **F7** | R14 回归：FIRA 版全链 65536 样本 → CRC32+spot vs golden，sat+unsat 双 build | `fira_regression.c` `fira_r14_regression()` | **判据**：crc==`0x90556BC7` **且** 64 spot 全等（容差 0），sat+unsat 双 build 均等 → R14 PASS | 🔴 待台架（桌面 plumbing 无效） |
| **F8** | R14 PASS 后才实测 FIRA cycle（真 CCNT），core-only vs FIRA 对比（性能数此时方可进选型） | `fira_regression.c` 末注（用 `bench_cyc_target` CCNT） | **判据**：含 FIRA 开销（setup/queue/callback/DMA）的真 cyc_8ch_frame；gating 于 F7 PASS | 🔴 待台架，gating 于 F7 |

**抽取/插值实现**：用 FIRA **eSampling+nSamplingRatio 字段**（`DECIMATION/INTERPOLATION`,`ratio=2`），不核内做——比率=2 整数 ✅、tap=63≪window ✅。⚠️ **[ASSUME]**：ADI 例程全 SINGLE_RATE（MCP.c:133），**无 dec/int 示例代码** → 此路径有 API 支持但无参考代码，**相位/×2 行为必上板验**（F4）。备选（若台架 dec/int 与核取偶相位对不齐）：核内做抽取/插值、FIRA 只 SINGLE_RATE 全速率卷积（失 dec 算力优势）。最终选择 = F4 单 channel 验相位后定。

---

## 5. R14 Q 格式转换点（逐条，bit 偏差高发，必上板逐位）

**总命门**：我方核 = **有符号分数 Q15 系数 × Q31 状态 → Q46(int64) 累加 → `>>15` 回 Q31 + 饱和钳位**（`tree_filterbank.c:6,99,104`）。FIRA 定点 = 32×32→80-bit MR，输入格式枚举只有 **UNSIGNED_INTEGER / SIGNED_INTEGER**（legacy 头:42-43，无 signed-fractional）。

| # | 转换点 | 我方核 | FIRA 侧 | 偏差级别 | 代码落点 | 必上板逐位 |
|---|--------|--------|---------|---------|---------|-----------|
| R14-1 | 累加器宽度 + 回 Q31 截断点 | int64 Q46，`acc>>15` 截断（向负无穷） | 80-bit MR，回写须缩放 | **LOW**（更宽不丢精度，截断 vs 舍入差 ±1 LSB） | `fira_postscale_dec`：`>>15` 不用 IEEE round | ✅ 截断 vs 舍入 ±1 LSB → CRC 挂 |
| R14-2 | 系数 Q15→32-bit 容器 | Q15 int16（`tree_filterbank.c:65`） | 32-bit，符号扩展，小数点保持 | **LOW-MED** | `fir_coeffs_q31.h`（占位待填，符号扩展或 `<<16` 二选一） | ✅ 误当无符号/对齐错位 → 增益错 2^k |
| **R14-3 ★** | **signed-fractional vs SIGNED_INTEGER 格式映射** | signed-fractional Q15×Q31 | 仅 UNSIGNED/SIGNED_INTEGER 枚举；signed-fractional 输出须 **×2 缩放 + decimate 后处理** | 🔴 **HIGH（最高）** | Path B `FixedPointEnable(SIGNED)` + `fira_postscale_*` | ✅ **桌面无法坐实**，必上板逐位 |
| R14-4 | 浮点舍入模式（仅若改走 FIRA 浮点） | Q31 定点截断 `>>15` | `IEEE_ROUND_TO_NEAREST_EVEN`（legacy 头:38） | MED | 不走（保定点）；如要切=**上报 PM/CTO** | 浮点≠定点 → R14 必不 bit-exact |
| R14-5 | ×2 内插增益位置 | `hb_interp2` 输出 ×2 后 sat（`tree_filterbank.c:127,130`） | INTERPOLATION 零插值自带 ×2 + signed-fractional ×2 → 可能复合 4× | MED | `fira_postscale_int`：**×2 只一次** + sat 留核 | ✅ 复合两次 ×2 → 增益错 4× |
| R14-6 | decimation 相位对齐 | 取偶相位 `i&1==1`（`tree_filterbank.c:113`） | DECIMATION "skip discarded samples"，保留相位须一致 | MED | `fira_make_channel` DEC 段；F4 单 channel 验相位 | ✅ 相位差半样 → detail 全错 → CRC 挂 |

> **最高风险 R14-3（HIGH，first-of-kind）**：Legacy + 定点（FixedPointEnable）**无官方先例**（例程 = Legacy + 浮点，FixedPointEnable grep 0 命中，F1 §1）；signed-fractional 当 SIGNED_INTEGER 用三处复合错位（小数点丢失 2^k / ×2 复合 / decimate 相位）→ 任一错 = golden CRC 必挂。**桌面无法坐实**；F6 攻坚先在 SHARC 仿真器单段打通再扩全链；打不通 → 上报决策。

---

## 6. bit-exact 验证协议 + 验收（crc==0x90556BC7）

**一句话**：FIRA 版单通道链跑同一冻结 chirp 65536 样本 → 还原 Q31 整数 → CRC32(IEEE 802.3) **必须 == `0x90556BC7`** 且 64 个 stride-1024 spot 全等（容差 0），sat+unsat 双 build 均须等 → R14 PASS（证 FIRA 版数值等价 core-only 核）。

**接入方式**（复用现成 harness，任务要点 2）：
1. **基准不变**：core-only golden `0x90556BC7` + `GOLDEN_SPOT[64]`（`bench/golden_ref.h:28,30-39`）。**FIRA 版是被验方，golden 不重生成**。
2. **替换卷积段**：`fira_regression.c` 把 `tfb_analyze/tfb_synthesize` 换成 `fira_tfb_analyze/fira_tfb_synthesize`，输出仍走与 `bench_harness.c:30` **逐位同算法**的 `crc32_buf` + `GOLDEN_CRC32`/`GOLDEN_SPOT` 比对。输入 = 同一冻结 `CHIRP_INPUT[]`（`bench/chirp_input.h`），无运行期 double。
3. **比对域** = Q31 整数逐位，**容差 0**（不用例程浮点 `Find_Max_Diff` 相对误差）。
4. **判据（二值）**：`fira_r14_regression()` 返回 `crc_match && spot_match`。
5. **sat+unsat 双套**：0.289 chirp 单通道不触发饱和 → SAT==UNSAT，两 build CRC 均须 `0x90556BC7`（`golden_ref.h:27`）。
6. **诚实边界**：桌面 golden=[L2]；**FIRA 版桌面跑无意义**（`fira_tree_setup()`/`fira_single_channel_template()` 桌面返回 -1，`fira_r14_regression()` 据此返回 0，不冒充）。**板上逐位通过后** R14 升 [L1]。🚫 禁把桌面 [L2] 当板上 [L1]。

**验收（总）**：① **R14 PASS** = crc==`0x90556BC7` + 64 spot 全等，sat+unsat 双 build（F7）；② **cycle 含开销** = 真 cyc_8ch_frame 含 FIRA setup/queue/callback/DMA 开销（F8，gating 于 ①）。两者全 [L1/EZKIT]。

---

## 7. cycle 方案

- **量法**：FIRA 版 `cyc_8ch_frame` 用现成 CCNT 抽象 `bench_cyc_target()`（`bench_harness.c:39`），与纯核同口径。稳态单帧测法沿用 `bench_harness.c:73-100`（热身 4 帧扣冷 cache）。
- **对比**：FIRA 版 `cyc_8ch_frame` vs 纯核基准 **1,006,935**（F0，[L1] 已实测）。帧周期 = 64/48000 = 1.333 ms = 1 GHz × 1.333 ms = 1,333,333 cycle。16ch deadline：`cyc_16ch_est = cyc_8ch_frame + 8*cyc_analyze_1ch` 须 < 1,333,333。
- **🔴 红线（铁律八/C9）**：FIRA `cyc_8ch_frame` / 新裕量 / 16ch deadline **全部标 [L1/EZKIT] 待台架**，且 **R14 板上 crc==0x90556BC7 通过前不得写进任何选型依据**（gating 于 F7 PASS，违者 BLOCKER）。本任务不报任何 FIRA 收益数值。
- **预期方向**（仅定性，非选型数）：63-tap 小核 → FIRA per-task 固定开销（QueueTask / 中断 core cycle）可能吞掉部分 offload 收益；开销占比待 F8 实测。**不写具体倍数。**

---

## 8. 风险

| 风险 | 说明 | 暴露阶段 |
|------|------|---------|
| **Q15×Q31 → signed-INTEGER 映射**（R14-3 HIGH） | signed-fractional 无直接枚举，×2 缩放/decimate 相位/小数点对齐三处复合，桌面无法坐实 | **F4 暴露**，F6 攻坚 |
| **Legacy + 定点 first-of-kind** | 例程 = Legacy + 浮点（FixedPointEnable grep 0），Legacy 下运行时 FixedPointEnable 是否独立生效（不配全局宏）头未明说 | F2/F3 |
| **FIRA 自身开销** | setup/queue/callback/DMA 非零，不假设零成本 | F7/F8 实测 |
| **cache 对齐 / 缓冲放置** | ADI_CACHE_MANAGEMENT=1，QueueTask flush 输入/系数、invalidate 输出；TaskMemory `#pragma align 32`；放置/对齐不当坏 bit-exact | **F4 不过先查这条** |

---

## 9. 来源分级 + 挂接 + 红线落实

**来源分级**：
| 级 | 内容 |
|----|------|
| [L1 归档头] | adi_fir_* 真 Legacy 签名（`adi_fir_legacy_2156x.h`，10 函数 + CHANNEL_INFO + 枚举） |
| [L1 例程] | 生命周期顺序（MCP.c:243-285）、Legacy 完成事件 ALL_CHANNEL_DONE（:103,281） |
| [L1 文档] | F1 模式/格式决策（DOC-S4-FIRA-F1-01）、核侧语义（tree_filterbank.c file:line）、golden（golden_ref.h:28） |
| [ASSUME] | dec/int 相位/×2 行为（例程无示例）、postscale 真移位量、Path B 是否需配全局宏 |
| [L1/EZKIT] | 所有板上数：编译/bit-exact/cycle/反汇编（F2-F8 待台架回填） |

**挂接（cross-ref）**：
| 锚点 | 落实 |
|------|------|
| **DOC-S4-FIRA-F1-01** | 模式 LEGACY + Path B SIGNED + DECIMATION + ALL_CHANNEL_DONE 逐条落代码 |
| **R14** | bit-exact 闸门：§6 协议（crc==0x90556BC7），`fira_regression.c` 实现，板上 [L1] 通过前收益冻结 |
| **R1** | F0 已闭（cyc_8ch_frame=1,006,935）；R1 纯核不足→FIRA 必需，但 R1 闭合 gating 于 R14 板上通过 |
| **铁律八 / C9** | FIRA 性能数写进选型 = BLOCKER；§7 全标"待 R14 后实测、不计入选型"，本文档零收益数 |
| **DEC-S3-PROC-01** | LOCKED 定点基线；不擅自切 FIRA 浮点（R14-4），如切=上报 PM/CTO |
| **golden CRC** | `bench/golden_ref.h:28` = `0x90556BC7`，FIRA 版回归真值，**不重生成** |

**红线落实自查**：
- ✅ 草案代码用**真 Legacy API**（归档头签名）+ 文档 + runbook + 协议，**未编译/未板验**，文件头均标"草案·未编译·真 Legacy API·F2-F7 待台架"。
- ✅ config 头不改（Path B 自足）；不动 chirp_input.h/golden_ref.h/脚手架/tree_filterbank。
- ✅ 每个未验证假设标 [ASSUME]/[L1/EZKIT]；每结论挂出处（legacy 头/例程 file:line/tree_filterbank file:line/F1 文档）。
- ✅ 🚫 全文/全代码无"已编译/已 bit-exact/已实测 cycle"声称。
- ✅ R14 板上 crc==0x90556BC7 通过前，FIRA 收益/裕量**不写进任何选型依据**（铁律八/C9），本文档零性能数值。
- ✅ 草案构建下 `fira_single_channel_template()`/`fira_tree_setup()` 返回 -1、`fira_r14_regression()` 返回 0，**不冒充桌面验证**。

---

*DOC-S4-FIRA-IMPL-01 · dsp-algorithm teammate · 2026-06-03 · 合并工作文档（工作单 + F0/F1 已闭 + F2-F8 runbook + 验收）·真 Legacy API·草案未编译/未板验·F2-F8 待台架回填*
