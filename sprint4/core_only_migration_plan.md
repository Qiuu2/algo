# Core-only CCES/SHARC 适配计划 — 4 子带树形 FIR（G2–G5 工程适配）

**文档 ID**：DOC-S4-CORE-PLAN-01
**作者**：dsp-algorithm teammate ｜ **日期**：2026-06-02 ｜ **性质**：纯计划文档，**本轮不写算法代码、不跑仿真**（开工待 critic 核计划后）
**前序输入**：`sprint4/dsp_migration_inventory.md`（DOC-S4-DSP-INV-01）、`knowledge_base/ezkit/prep/PREP-DSP-migration.md`、`sprint3/dsp/tree_filterbank.{c,h}`、`sprint3/dsp/tree_verify.c`、`sprint3/dsp/dsp_8ch_report.md §2.1`

---

## 0. 范围声明 + G1 结论引用

### 0.1 范围（core-only G2–G5，🚫 禁碰 FIRA）
本计划**仅覆盖滤波器组定点核（core-only）的 G2–G5 工程适配**，把已成型且桌面 bit-exact 验证过的
`sprint3/dsp/tree_filterbank.c`（209 行）适配到 CCES/ADSP-21569（SHARC+ 单核 1GHz 定点路线）：

| 项 | 一句话范围 |
|----|-----------|
| G2 | 8ch 适配：单通道 `tfb_*` → ×8 循环（8 份 `TreeChannelState`） |
| G3 | 系数接线：`tfb_set_coeffs`（`tree_filterbank.c:68`）喂半带原型 Q15 系数头 |
| G4 | CCES 骨架统一：`cces_skeleton`（float 描述、文件名 `dyadic_analysis.c` 不一致）→ 统一改调 `tfb_analyze/tfb_synthesize`（复用已验证定点核） |
| G5 | CCES 工程化：.ldf 内存布局、cycle 计数寄存器填实、SIMD/零系数跳过优化 |

### 0.2 边界（禁区 + 闸门，红线）
- **🚫 FIRA-offload 不在本范围**：core-only 不依赖台架 baseline（`sprint3/audit/ezkit_fira_baseline.md`）。
- **R14 闸门维持**：本计划**不授权**把任何 FIRA offload 收益写进选型依据（铁律八/C9）。
  纯核够用则该约束自然用不上；本计划全程只产出"纯 4 子带定点 C 核"的 R1 数，**不碰 FIRA**
  （`ezkit_fira_baseline.md:19` R14 闸门定义；§227 FIRA 收益写进选型 = BLOCKER）。
- **不写算法代码**：本轮只出计划；`tfb_analyze/tfb_synthesize/hb_*` 频率特性/系数/算法路线**一律不改**，
  仅做 8ch 包裹、系数接线、骨架统一、工程化放置（最小侵入，与 PF-4 FIX-01"只加饱和不改算法"同纪律）。

### 0.3 G1 结论引用（DEC-S4-DSP-01，已拍板【推后不补】，本计划直接采用、不再讨论）
> bit-exact 迁移基准 = **C golden vector `sprint3/dsp/tree_io_sat.csv` + `tree_io_unsat.csv`（sat/unsat 双套）+ numpy `sprint3/dsp/pf4/xcheck_subband.py`**；
> **独立 MATLAB 参考不补**（grep 两否：铁律七泛指独立双轨非字面 MATLAB + 已有三路独立核；JY/T 不强制 MATLAB）。
> — `sprint2/docs/decisions_log.md:575,627`（DEC-S4-DSP-01，LOCKED）；`dsp_migration_inventory.md:70`（G1）

本计划所有 bit-exact 判定**直接引用此基准**（§5），不再评估"是否要 MATLAB"。

---

## 1. G2：8ch 适配

**现状**：核接口为**单通道**。`tfb_analyze(TreeChannelState *ch, ...)`（`tree_filterbank.c:139`）/
`tfb_synthesize(... ch ...)`（`:183`）/ `tfb_channel_init(ch)`（`:74`）每次只处理一条 `TreeChannelState`。
`TreeChannelState`（`tree_filterbank.h:102-109`）持有该通道全部半带状态：`ana_dec[3] / ana_int[3] / syn_int[3]`，
每个 `HbFirState` = `int32_t state[63] + uint16_t widx`（`tree_filterbank.h:96-99`）。半带系数 `g_hb` 为**全局只读共享**
（`tree_filterbank.c:65,70`）→ 8 通道共用同一原型核，无需复制系数。

**要做什么**：在核**外层**加一个 8ch 包裹层（broadside DAS：8 路阵元输入 → 分析 → 子带加权求和 → 合成单路输出），
即 PREP §1.2 推荐的"骨架改成调 `tfb_*`"。**不改核本身**（`tfb_*` 签名/算法/系数零改动）。
- 静态分配 8 份 `TreeChannelState g_ch[8]`，逐通道 `tfb_channel_init`（`tree_filterbank.c:74`）。
- 帧回调里 `for(c=0;c<8;c++) tfb_analyze(&g_ch[c], in[c], FRAME, sb0[c],...)`；
  broadside DAS 各子带等增益求和（`tree_verify.c:204-217` 已给"分析×N_CH + 合成×1"的系统级口径）。
- 合成 `tfb_synthesize` 仅 **×1**（broadside DAS 输出单路），用一份独立 `syn` 状态（参 `tree_verify.c:70` ana/syn 分用独立实例）。

**改哪些文件/函数**：
- 新增包裹（G4 统一后落在 `dsp_main.c` / 替代 `dyadic_analysis_8ch`，见 §3）——**调用** `tfb_channel_init:74` / `tfb_analyze:139` / `tfb_synthesize:183`，不改其实现。
- 内存：`8 × sizeof(TreeChannelState)`，状态热点 `state[63]×(3+3+3)级×8ch`（§4 G5 .ldf 放置 L1）。

**风险**：
- R-G2-1：8 份 state 内存 + 大局部数组（`tfb_analyze` 内 `a1[256]/r1[512]` 等，`tree_filterbank.c:143-144`）×8ch 栈压力 → 见 G5 .ldf（搬静态/section）。
- R-G2-2：通道间状态必须**严格独立**（每通道独立 `TreeChannelState`），误共享会跨通道串扰；包裹层须按 `c` 索引隔离。
- R-G2-3：broadside 求和点是 int32 相加，沿用核内 `sat_add_i32`（`tree_filterbank.c:55`）饱和纪律，避免 8 路叠加溢出（headroom −4.8dB 约定，`tree_filterbank.h:38-41`）。

## 2. G3：系数接线

**现状（关键发现，须 critic 注意）**：核**只用单一 63-tap 半带原型**，由 `tfb_set_coeffs(hb_coef_q15, ntaps)`
（`tree_filterbank.c:68`）注入全局 `g_hb/g_hb_n`（`:65-66,70-71`），**所有级/所有通道共享同一原型核**
（`tree_filterbank.h:53` `TFB_HB_TAPS=63`；`.h:111-115` 注释明示"所有级/通道共享同一原型半带核"）。
桌面验证里该 63-tap Q15 系数由 `tree_verify.c:make_halfband()`（`:40-60`，kaiser β=6, cutoff fs/4）**运行时内生成**，
**不是从 `fir_coeffs.h` 读**。

**口径澄清（避免 critic C1 卡）**：CLAUDE.md / 盘点 G3 写"SB0=31 tap / SB1-3=63 tap"指的是**子带划分设计表**
（`dsp_8ch_report.md:42-45` §2.1：SB0 31 tap / SB1–3 63 tap）的"等效子带阶数"；而**树形差分金字塔实现**
（DEC-S2-002 锁定）是单一 63-tap 半带原型在 3 级 dyadic 树上复用 —— 二者不矛盾：31/63 是"子带视角的等效抽头"，
63 是"实现视角的物理原型核抽头"。**G3 接线对象 = 这一份 63-tap 半带原型 Q15**，非 4 套独立子带系数。

**🚫 不可误接的旧资产**：`sprint2/dsp/fir_coeffs.h` 是**已废的 437-tap 全速率核**
（`SB_NUM_TAPS 437`，4 套独立子带系数 `g_sb0_coef[437]`…），即 `tree_filterbank.h:6` 注释"取代 cces_template 437 抽头全速率参考核（决策不可行）"
要废弃的对象。**G3 严禁把 437-tap `fir_coeffs.h` 接进 `tfb_set_coeffs`**（PREP §1.3 点名"骨架里 fir_coeffs.h 还是空壳/历史 437 抽头核残留"）。

**要做什么**：
1. 生成一份**与桌面 bit-exact 同源**的 63-tap 半带原型 Q15 系数头（如 `fir_hb63_q15.h`）——
   值必须 = `tree_verify.c:make_halfband()` 量化后的 `hb_q15[63]`（同 kaiser β=6 / cutoff fs/4 / DC 归一化 / `lround(·×32768)` 钳位，`tree_verify.c:54-59`），
   否则板上输出无法对 golden vector bit-exact（§5 容差 0）。**生成方式 = 从同一 host harness 导出常量数组**（避免编译器/平台浮点差异再算一遍）。
2. 上电初始化调一次 `tfb_set_coeffs(g_hb63_q15, 63)`（`tree_filterbank.c:68`），G4 统一后落在工程 init 路径。

**改哪些文件/函数**：
- 新增 `fir_hb63_q15.h`（63-tap Q15 常量，源自 `tree_verify.c:40-60`）；
- init 路径调用 `tfb_set_coeffs:68`（一次性，系数全局共享，8ch 无需各自喂）。

**风险**：
- R-G3-1：**系数同源性**是 bit-exact 命门 —— 若板上系数与 golden 生成时不同源（哪怕 1 个 LSB 差），逐位回归必挂。须把 63-tap 数组**冻结为常量头**而非上板重算（消除浮点不确定性）。
- R-G3-2：误接 437-tap 旧 `fir_coeffs.h` = 算法路线倒退（违反 DEC-S2-002）→ BLOCKER 级，须在工程里物理移除/隔离旧头。
- R-G3-3：`ntaps` 必须 = `TFB_HB_TAPS`(63)（`tree_filterbank.h:53`），与状态线 `state[63]`（`.h:97`）一致；传错长度越界。

## 3. G4：CCES 骨架统一

**现状**：`sprint3/dsp/cces_skeleton/` 只有 `cces_skeleton_description.md`（**纯描述文档，无可编译工程**，
盘点 `dsp_migration_inventory.md:73`；PREP §1.2/`PREP-DSP-migration.md:20-21`）。其算法层与已成型核**双重不一致**：
1. **数据类型不一致**：骨架 `dsp_main.c`/`bf_broadside.c` 用 **`float`** 写（描述文档 §4/§5，PREP `:21` "Step1-6 全 float"）；
   已成型核是**定点 Q15/Q31/Q46**（DEC-S3-PROC-01 锁定单核定点路线，`tree_filterbank.h:29`）。
2. **文件名/函数名不一致**：骨架算法文件名 `dyadic_analysis.c`/`dyadic_synthesis.c`、入口 `dyadic_analysis_8ch()`
   （描述文档 §1 树 + §4 `dsp_main.c:180`）≠ 已验证核 `tree_filterbank.c` 的 `tfb_analyze/tfb_synthesize`。

**要做什么**（PREP 推荐方案：骨架改成调 `tfb_*`，复用已验证定点核；**废弃骨架的 float 算法层**）：
- 帧调度入口 `dyadic_analysis_8ch(...)` → 改为 G2 的 8ch 包裹（逐通道调 `tfb_analyze:139`）。
- `dyadic_synthesis` → 改调 `tfb_synthesize:183`（单路输出）。
- 删除/不落地骨架的 `float` 算法文件（`dyadic_analysis.c`/`bf_broadside.c` 的 float Step）—— 平台/外设层（SPORT/DMA/ldf）**保留**，仅替换算法层。
- broadside 增益钩子已在核内留好（`tfb_synthesize` 的 `q31_mul`/`(void)q31_mul`，`tree_filterbank.c:178-181,207-208`）；当前全 1.0 无需接 Dolph 加权（Dolph 在阵元维度，非子带维度，`tree_filterbank.h:16`）。

**改哪些文件/函数**：
- 新建可编译 CCES 工程，算法层只挂 `tree_filterbank.c/h` + G2 包裹 + G3 系数头；
- 平台层（`sport_tdm.c`/.ldf/init）从骨架描述 + BSP 例程落地（属硬件 bring-up，非 core-only 首测依赖，见 §6/§7）。
- 骨架描述文档保留为参考，**不作为代码源**。

**风险**：
- R-G4-1：骨架 float 残留若被误编译进链路 → 双实现冲突 / 浮点污染定点回归。须在工程里**只挂定点核一条算法路径**。
- R-G4-2：骨架的 SPORT/DMA/codec 接线是 **[待核实]**（FSYNC 极性 U4 等，PREP `:34`）；core-only 首测**不依赖 TDM**（§6 用片内测试向量），TDM 偏差不挡首测。
- R-G4-3：函数签名差异（骨架 `_8ch` 一次进 8ch vs 核单通道）→ 包裹层负责适配，不得改核签名。

## 4. G5：CCES 工程化（.ldf / cycle 计数 / SIMD·零系数跳过）

### 4a — .ldf 内存布局
**现状**：核用大局部数组在栈上：`tfb_analyze` 内 `a1[256]/a2[128]/a3[64]/r1[512]/r2[256]/r3[128]`（`tree_filterbank.c:143-144`），
`tfb_synthesize` 内 `a2p[256]/a1p[512]/up3..up1`（`:188-189`）；状态线 `state[63]`×9级×8ch（G2）。桌面无所谓，SHARC+ 需显式放置。
**要做什么**：
- **L1 放热点**：半带延迟线 `state[63]`（每帧每 push 全扫，`tree_filterbank.c:97-100` 内循环）×9级×8ch + 帧内大中间数组 → L1（block0/1，单周期访问，PREP `:31`）。
- **L2 放系数 + 低速率级**：63-tap Q15 原型核（只读、访问率相对低）放 L2（PREP `:31`）。
- 大局部数组**改静态分配 + section 放置**（避免 ×8ch 栈溢出，PREP §2 内存布局行 / `:38-40`）。
- DMA buf（TDM，仅端到端阶段用）`#pragma align` + L1（PREP `:34`），core-only 首测不依赖。
**风险** R-G5-1：L1 容量 vs `state[63]×9×8ch + 中间数组` 是否放得下 = **待 datasheet 核实**（L1 block 大小，PREP §3 抽取项 `:49`）；放不下则部分降 L2，MCPS 受访存惩罚——属优化项，不挡首测裸核基线。

### 4b — cycle 计数寄存器填实（R1 命门）
**现状**：`tree_filterbank.h:74-93` 已预埋 `ENABLE_CPU_LOAD_MEASUREMENT` + `TFB_LOAD_START/STOP` 宏，但 `g_tfb_cyc_reg`/`g_tfb_cyc_start`/`g_tfb_cyc_accum`
（`tree_filterbank.h:80-82`）是**占位 extern 声明**；`tfb_gpio_high/low`（`.h:84`）占位未实现。
**要做什么**：
- `g_tfb_cyc_reg` → 真实周期寄存器 `*pREG_..._CCNT`/CCES `cycles()`/`__builtin_emuclk`（从 `def21569.h` 抽，PREP `:40,58`）。
- `ENABLE_CPU_LOAD_MEASUREMENT=1`，`TFB_LOAD_START/STOP`（`.h:86-89`）包住单通道 `tfb_analyze→(broadside 求和)→tfb_synthesize`（PREP 步骤 2）。
- 可选 GPIO 翻转法（`.h:83-89`）交叉校验：`tfb_gpio_high/low` → `*pREG_PORTx_DATA_SET/_CLR`。
**风险** R-G5-2：CCNT 寄存器名/读取方式 = 待 datasheet/BSP 核实（PREP §3）；中断/cache 开销须含进实测窗口（`TFB_LOAD_START/STOP` 包住完整帧处理）。

### 4c — SIMD / 零系数跳过优化（**后置，先测裸核**）
**现状**：核为朴素标量全长卷积（`hb_push_filter` 内 `for k<N` 全 63 抽头，`tree_filterbank.c:97-100`），注释已点明"半带约半数抽头为 0，SHARC 上可零系数跳过砍半 MAC"（`tree_filterbank.c:8-9`；`tree_filterbank.h:30`）。
**要做什么**（**拿到基线 MCPS 之后**才做，PREP 关键纪律 `:73`"先测裸核，后优化"）：
- 零系数跳过表：半带非零系数 `(63+1)/2=32`（`tree_verify.c:160`），跳零后 MAC 砍半（头号优化，PREP §2 SIMD 行 `:32`）。
- SIMD/PEx-PEy 向量化 + `#pragma loop_unroll`/`#pragma SIMD_for` 给半带卷积循环（PREP `:41`）。
**风险** R-G5-3：优化必须**保持 bit-exact**（跳零仅去乘 0 项，数学等价；舍入模式 `>>15`/`>>31` 须与桌面一致，PREP §2 定点指令行 `:35`），否则破坏 §5 回归。先裸核基线、后优化，免得优化掩盖真实裕量（PREP `:73`）。

## 5. bit-exact 回归方案（vs tree_io_sat/unsat 双套，板上，容差 0）

### 5.1 判定口径（写进二值判据）
**跑对（bit-exact）= core-only 板上输出 vs `sprint3/dsp/tree_io_sat.csv` + `tree_io_unsat.csv` 全向量逐位一致，sat/unsat 两套都过。**
**仅编译运行 ≠ 达标**（"出声即跑通"❌）。容差 = **0**（逐位，非 SNR/RMS 阈值）。

### 5.2 golden vector 来源与两套差异（已核实，DEC-S4-DSP-01 / 盘点 3a）
- `tree_io_*.csv`（各 2.25MB）= 输入 vs 重建逐样本向量，由 `tree_verify.c:148` 写出（源码写泛名 `tree_io.csv`）。
- **sat / unsat = 饱和钳位开/关两轮运行后重命名落地的变体**（`dsp_migration_inventory.md:50`，critic C1 已核）：
  - **unsat** = 定义 `TFB_DISABLE_SAT`（`tree_filterbank.c:42-44`，饱和退化为原始环绕窄化）→ 验证 headroom 内"修复前/后逐位一致"。
  - **sat** = 默认饱和路径（`sat_i64_to_i32`/`sat_add_i32` 激活）→ 验证对抗激励下饱和钳位行为。
  - **两套都过** = 标称路径与饱和兜底路径**双覆盖**（对抗激励已自带，无需另造）。

### 5.3 板上怎么做（可执行）
1. **喂 golden 输入**：把 `tree_io_*.csv` 的 `x` 列（Q31 输入序列，`tree_verify.c:107-108` 的 0.289 chirp，含 −4.8dB headroom）
   转成片内 `const int32_t` 测试向量数组（**不经 TDM/codec**，消除外设变量），逐帧（FRAME=64，`tree_verify.c:24`）喂单通道 `tfb_analyze→tfb_synthesize`（跨帧状态连续，参 `tree_verify.c:112-119`）。
2. **逐位比对**：板上重建 `y`（Q31 整数）vs csv 的 `y` 列（`tree_verify.c:150` 写出的对齐重建）—— **整数逐 sample 严格相等**判定。
   注意 csv 存的是 `%.10e` double（`tree_verify.c:150` `from_q31` 回浮点）；**比对须在 Q31 整数域**做：重新跑一份 host harness 导出**整数 `y` golden**（`y[]` 数组，`tree_verify.c:67,118`），或把 csv `y` 列 `to_q31` 还原后比——以**整数逐位**为准（容差 0），避免浮点字符串往返误差。
3. **两轮**：第一轮 **unsat**（编译定义 `TFB_DISABLE_SAT`）对 `tree_io_unsat.csv`；第二轮 **sat**（默认）对 `tree_io_sat.csv`。两轮逐位全过才算 G2–G4 迁移无功能漂移。
4. **门序**：bit-exact 回归（本节）是 §6 cycle 实测的**前置门**——必须先过，否则测的是错算法的 MCPS（PREP 关键纪律 `:73`）。

### 5.4 对齐桌面三路互验（背书，非板上重做）
桌面已有三路独立核吻合（独立 C 316.4dB / numpy 74.6–78.7dB / 自写整数 SB0=74.9，`dsp_migration_inventory.md:40`）+ numpy `xcheck_subband.py`（DEC-S4-DSP-01 基准之一）。
板上回归**只需对 C golden vector 逐位**即可证迁移正确性；numpy 轨作桌面侧交叉背书，**MATLAB 不补**（DEC-S4-DSP-01 已定）。

> 诚实边界：桌面 golden 为 [L2]；板上逐位通过后，重建正确性升 [L1]（含流水线/寄存器宽度/cache/中断真值，原 R14/PF-5 范畴，`dsp_migration_inventory.md:43`）。**🚫 禁把桌面 [L2] 当板上 [L1]**。

## 6. R1 数口径（CCLK 实测 + MCPS [L1/EZKIT]，区别 baseline）

### 6.1 实测什么（板上真值，非桌面算法学 MCPS）
- **CCLK 实测**：读 SHARC+ 周期寄存器（CCNT/EMUCLK，§4b），`TFB_LOAD_START/STOP` 包住完整帧处理（含 cache/取模/中断开销，`tree_filterbank.h:87` 记最坏 `g_tfb_cyc_accum`）。
- **core-only MCPS/cycle**：`MCPS = cycles_per_frame × FS / FRAME / 1e6`（`tree_filterbank.h:69`；FRAME=64@48k → 帧周期 1.333ms）。
- **measured 对象 = 纯 4 子带定点 C 核**（`tfb_analyze`+broadside 求和+`tfb_synthesize`），**不含 FIRA、不含 TDM 信号链**（片内向量喂入）。

### 6.2 强制标签（红线）
- 所有 core-only 板上数标 **[L1/EZKIT]**；明确区别于：
  - **桌面算法学 MCPS [L2]**：`tree_verify.c:155-219` 的 MAC计数×速率（17×/33× 桌面口径，`decisions_log.md:634`）—— 是推断，非实测。
  - **ADI 例程 FIRA baseline [L1/EZKIT]**：`sprint3/audit/ezkit_fira_baseline.md` 的官方 FIR 例程 cycle/sample/tap —— **非我方算法**，仅校准 FIRA 性能。
- ✅ 正确措辞模板：「4 子带定点 C，core-only，板上 vs `tree_io_*.csv` bit-exact，CCLK=… 实测，core-only MCPS=…，[L1/EZKIT]」
- ❌ 错误：把桌面 [L2] 当板上 / 把 FIRA 收益算进 R1（违反 R14 闸门，`ezkit_fira_baseline.md:227` BLOCKER）/「出声即跑通」当达标。

### 6.3 与 baseline 的解耦声明
core-only R1 数**独立成立**，不依赖、不引用 FIRA baseline 收益（R14 闸门维持，`ezkit_fira_baseline.md:19`）。
**纯核若已满足 WCET < 帧周期 1.333ms 且裕量目标 ≥10×**（`tree_filterbank.h:72`）→ R1 由纯核闭合，R14/FIRA 自然用不上（§0.2）。〔≥10× 退役 DEC-S4-CRITERION-01 2026-06-04〕

### 6.4 R1 闭合判据（core-only 部分）
- 单通道 [L1] MCPS 实测 → 外推；8ch/16ch 实测满负载 cycles/frame；
- 判据：满负载 WCET < 1.333ms 且裕量 ≥10×（`tree_filterbank.h:72`），对照桌面 17×(16ch)/33×(8ch)[L2]（`decisions_log.md:634`）验证桌面外推合理性。〔≥10× 退役 DEC-S4-CRITERION-01 2026-06-04〕
- 实测 [L1] 与桌面 [L2] 偏差是预期的（cache/中断/访存惩罚），以 [L1] 为权威收口 R1。

## 7. 开工步骤序列（编号，可执行 — 从建 CCES 工程到出 core-only MCPS）

> 总纲：**先单通道、纯 C 核、bypass 信号链，bit-exact 先过再测 cycle**（PREP §4 最短路径 `:62-73`）。本计划**到 S7 出 core-only [L1] MCPS 即闭环**；TDM/端到端为后置。

| # | 步骤 | 产出 | 门 / 依据 |
|---|------|------|----------|
| **S0** | CCES 2.12.1 安装 + license（资料已在 `/home/it1234/下载/`）；ADSP-21569 datasheet/HWRM/BSP 入库后精读 §3 待抽取清单（CCNT 寄存器名、L1 block 大小、`def21569.h`） | 环境就绪 + 寄存器/内存事实 | PREP §3/§4 步0 `:46-58,66` |
| **S1** | 建 21569 空 CCES 工程 + 默认 `.ldf`；挂 `tree_filterbank.c/h`（**不改**）+ G3 的 `fir_hb63_q15.h` + G2 8ch 包裹层；init 调 `tfb_set_coeffs(g_hb63_q15,63)`（`:68`）；纯编译过 | 可编译工程 | G2/G3/G4；PREP 步1 `:67` |
| **S2** | **板上 bit-exact 回归（前置门）**：片内喂 `tree_io_*.csv` 的 x 序列，单通道逐帧 `tfb_analyze→tfb_synthesize`，整数域逐位对 golden y。先 **unsat**（`-DTFB_DISABLE_SAT`）对 `tree_io_unsat.csv`，再 **sat**（默认）对 `tree_io_sat.csv`。**两套全过（容差 0）方可继续** | bit-exact PASS（双套） | §5；PREP 关键纪律 `:73` |
| **S3** | 接 cycle 计数：`def21569.h` 抽真实周期寄存器填 `g_tfb_cyc_reg`（§4b），`ENABLE_CPU_LOAD_MEASUREMENT=1`，`TFB_LOAD_START/STOP` 包住单通道处理 | cycle 计数可读 | G5/4b；`tree_filterbank.h:74-93`；PREP 步2 `:68` |
| **S4** | **首测单通道 core-only MCPS [L1]**：片内 64-sample Q31 向量（不依赖 TDM），读 cycles/frame → `MCPS=cycles×FS/FRAME/1e6`（`.h:69`）。**最早能出的 [L1] 数** | 单通道 MCPS [L1/EZKIT] | §6；PREP 步3 `:69` |
| **S5** | **8ch/16ch 实测**：×8/×16 份 `TreeChannelState`（G2），实测满负载 cycles/frame，验 WCET<1.333ms 且裕量≥10×〔≥10× 退役 DEC-S4-CRITERION-01〕，对照桌面 17×/33×[L2] | 满负载 MCPS [L1] + R1 判据 | §6.4；PREP 步4 `:70`；`decisions_log.md:634` |
| **S6** | （**S5 通过后**才做）零系数跳过表 + SIMD 优化，**复测仍须过 S2 bit-exact**；先裸核基线后优化 | 优化后 MCPS [L1]（裸核基线已锁） | G5/4c；PREP 纪律 `:73` |
| **S7** | 收口 core-only R1 数：按 §6.2 模板出「4 子带定点 C / core-only / 板上 bit-exact / CCLK 实测 / MCPS=… / [L1/EZKIT]」，**不掺 FIRA**（R14 维持） | core-only R1 结论（待 critic 核） | §6；R14 闸门 |
| **S8** | （**后置/并行，不挡 S7**）待 hardware-design bring-up TDM+DMA 后接真实 8ch 端到端；limiter/子带均衡 P2 | 端到端（不在 core-only 范围） | PREP 步5 `:71` |

**关键纪律（重申）**：S2 是 S4 的硬前置门；S5 是 S6 的硬前置门；S7 不引用 FIRA baseline 收益。

## 8. 挂接

| 挂接对象 | 关系 | 出处 |
|---------|------|------|
| **R1**（命门，待我方算法上板实测） | 本计划 S4–S7 产出 core-only [L1] MCPS = R1 闭合的核心；CCLK 实测口径见 §6 | `dsp_migration_inventory.md:80`；`tree_filterbank.h:72` |
| **R14**（FIRA bit-exact 闸门） | **维持关闭**：core-only 不依赖 FIRA、不把 FIRA 收益写进 R1/选型（§0.2/§6.3） | `ezkit_fira_baseline.md:19,227` |
| **DEC-S2-002**（树形 FIR 路线 LOCKED） | 适配对象=该路线已成型核；G3 严禁回退 437-tap（§2） | `decisions_log.md:90,598` |
| **DEC-S3-PROC-01**（定点路线 + 采购冻结，待 EZKIT 实测） | 单核定点路线前提；core-only MCPS 实测是解冻该决策的输入 | `decisions_log.md:480,622` |
| **DOC-S4-DSP-INV-01**（迁移盘点，G1–G5） | 本计划是其 G2–G5 的执行方案；迁移=适配非重写 | `dsp_migration_inventory.md:60,71-74` |
| **DOC-S4-INPUT-01**（Sprint4 Split-Task 输入） | 本计划属其 DSP 迁移 INPUT-1 子任务 | `sprint3/audit/sprint4_inputs.md`；`dsp_migration_inventory.md:80` |
| **DEC-S4-DSP-01**（bit-exact 基准；G1 MATLAB 推后不补，LOCKED） | §5 回归基准直接引用；不再讨论 MATLAB | `decisions_log.md:575,627` |

---

## 附：技术结论 file:line 出处索引（过 critic C1）

- 单通道接口 / 状态结构：`tree_filterbank.c:74,139,183`；`tree_filterbank.h:96-109`
- 全局共享半带系数 / 注入：`tree_filterbank.c:65-66,68,70-71`；`tree_filterbank.h:53,111-115`
- 63-tap 原型 host 生成（bit-exact 同源依据）：`tree_verify.c:40-60,54-59`
- golden vector 写出 / sat·unsat 双套：`tree_verify.c:13,148,150,152`；`dsp_migration_inventory.md:50`
- 饱和开关 TFB_DISABLE_SAT：`tree_filterbank.c:42-44`；`sat_*`：`tree_filterbank.c:47,55`
- 大局部数组（.ldf 放置依据）：`tree_filterbank.c:143-144,188-189`
- cycle 计数预埋（占位待填）：`tree_filterbank.h:74-93,80-82`
- MCPS 公式 / WCET 判据：`tree_filterbank.h:69,72`
- 半带零系数跳过依据：`tree_filterbank.c:8-9`；`tree_filterbank.h:30`；`tree_verify.c:160`
- 旧 437-tap 废核（G3 禁接）：`sprint2/dsp/fir_coeffs.h`（`SB_NUM_TAPS 437`）；`tree_filterbank.h:6`
- 子带划分设计表（31/63 等效抽头）：`dsp_8ch_report.md:42-45`
- 桌面 [L2]→[L1] 路径 / 上板技术点：`knowledge_base/ezkit/prep/PREP-DSP-migration.md` 全文
- 桌面 17×/33× [L2] 权威值：`decisions_log.md:634`

---

*DOC-S4-CORE-PLAN-01，dsp-algorithm teammate，2026-06-02。范围=core-only G2–G5，🚫禁碰 FIRA，R14 闸门维持。本轮纯计划，无算法代码、无仿真。待 critic 核后开工。*
