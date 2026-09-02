# S7 DSP 侧候选评估 — B1–B6 + 补充候选（六段式）

> dsp-algorithm teammate @ claude-fable-5-1，2026-09-02。范围裁定 DEC-S7-SCOPE-01（算法层升级；产品层不做）。
> **状态：DRAFT，待独立 critic（关②）+ CTO 常识审（关③）。未 commit。**
> 纪律自查：未修改任何既有文件；未写任何算法/固件代码；只新建本文与算力核算脚本
> `sprint7/sim/dsp/s7_dsp_compute_ledger.py`（纯 stdlib，`/usr/bin/python3` 3.10.12 实跑，输出即本文 §0.2/§8 各表）。
> 每个数字挂 L 标；不替 CTO 补任何未记录数字；声学收益一律引用 acoustic teammate 报告
> **`sprint7/sim/acoustic/S7_ACOUSTIC_SIM_REPORT.md`**（2026-09-02 已落盘；节号见各候选段）。分工：该报告子带按**理想砖墙**算，
> 其 §1「不能回答」第 4 条明写差分金字塔 detail 带泄漏/交叠纹波须 DSP 侧核——**本项归 DSP，本文 §2.5/§4.3/§5.1 承接**。
> 输入：PM 两份只读审计（fw_code_audit / algo_code_audit，scratchpad）+ decisions_log 2026-06-10 至 09-02 各条 +
> §「引用」所列文件。file:line 相对仓库根 `itc-enterprise-workflow/`。

---

## 0. 口径与共同前提（先读，各候选段不重复）

### 0.1 本文用哪个口径
三口径互不可比（F7_MARGIN_MATERIAL.md:29-56；DEC-S6-M2-BOARD-PASS-01 F60-MAJOR-1）：
① **墙钟/需求 MCPS**（cyc×750/1e6，含加速器忙等）② **争用-ledger**（both_max−base，T2 账 95.59≤210.19）③ **纯核 MMAC**（已退役）。

**本文算力代价全部用口径 ①（墙钟）**，锚 = `g_m2_beam_cyc_max=830,903` [L1，M2 板，run 内最大值]。理由：它是唯一在
**真实 M2 上下文**（SPORT DMA 在跑、ISR 在抢、FIRA 忙等在内）测到的 L1 数，也是 DEC-S6-M2-BOARD-PASS-01 明写
"现实 main 循环余量 37.7%"的口径。T2 账（口径 ②）只在 §8 作参考并列，**不与墙钟相加、不互称达标/矛盾**。

### 0.2 锚点表（脚本 §A 输出，逐位复核）

| 量 | cyc/帧 | MCPS | 占帧 | 墙钟余量 | L 标 / 出处 |
|---|---|---|---|---|---|
| 帧预算（1 GHz × 64/48k） | 1,333,333 | 1000.00 | 100% | 1.000× | [L1-derived] CCLK 1e9 [L1 F7 G6] |
| **T2 1.5× 线（墙钟等价）** | **888,889** | 666.67 | 66.7% | 1.500× | [L1-derived] = 1,333,333/1.5 |
| `g_m2_beam_cyc_max` 06-16 | **830,903** | 623.18 | 62.3% | **1.605×** | [L1 max] DEC-S6-M2-BOARD-PASS-01 |
| `g_m2_beam_cyc_max` 06-29 | 829,218 | 621.91 | 62.2% | 1.608× | [L1 max] TEST1_WIRING…FIELDLOG_20260629.md:24 |
| F7 8ch FIRA（bench，main ctx，含忙等） | 463,273 | 347.45 | 34.7% | 2.878× | [L1 bench] F7_CLOSING_RECORDS.md:154 |
| H2 base 8ch（bench） | 454,730 | 341.05 | 34.1% | 2.932× | [L1 bench] H2_READING_ANOMALY_ANALYSIS.md:9-13 |
| H1 focus_only（bench，同态 A/B） | 65,371 | 49.03 | 4.9% | — | [L1 bench] H1_FINAL_RULING_MATERIAL.md:16-21 |

由此两条硬推论 [L1-derived]：
- **到帧边余量 = 502,430 cyc = 376.8 MCPS = 37.7%**。
- **到 1.5× 线余量 = 57,986 cyc = 43.5 MCPS**。任何墙钟增量 > 57,986 cyc/帧 ⇒ 墙钟余量 < 1.5×。这是本文所有"是否击穿"判断的唯一尺子。

### 0.3 一个先决观察：M2 831k 与 bench 463k 的 1.79× 差距
- M2 墙钟 830,903 / F7 463,273 = **1.794×**；/ H2 base 454,730 = 1.827× [L1-derived]。F7 与 H2 都是 main 上下文、含 FIRA 忙等的
  **同口径墙钟**（fira_regression.c:611-619 括号；h2 同链），所以这个差不是"忙等未计入"能解释的——bench 也含忙等。
- DEC-S6-M2-BOARD-PASS-01 写的 "~130µs [L2 H2 纯核口径] 的 6.4 倍" 已被 F60-MINOR-2 标为"基数不可独立溯源"。**我的读法：
  正确的 bench 尺子是 F7 463k / H2 455k（455-463µs），M2 超出为 1.8×，不是 6.4×。** 本文不改 DEC 原文，只在此登记读法供 PM/critic 核。
- **差距 368k cyc 比本文全部候选增量之和（低端 ~80k，高端 ~218k，§8）都大。** 成因未拆（WO-S6-BEAMCYC-SPLIT 尚无登记行）。
  候选成因见 §6.3；其中"M2 工程 Debug 配置优化关"（`.cproject:39` 无 value [L1 文件] → 按 CDT 默认推断为关 [L3]；bench 计划 `-O1`，BENCH_OPS_CARD.md:19）
  是零成本可证伪的第一假设 [L3]。**因此本文把 B6.3（split）列为一切算力决策的前置。**

### 0.4 冻结件与"重跑 bit-exact 链"的定义
冻结件（M2 只 call 不 edit，m1_loopback_tdm.c:62-69）：`tree_filterbank.c/.h`（md5 1e884793…/7397ff0e…）、`tfb_8ch.c`、`fira_tree.c`、
`dolph_w8_q15.h`、`fir_coeffs_hb63.h`、`fir_coeffs_q31.h`、`golden_ref.h`、`chirp_input.h`、`dolph_f5_goldens.h`、sprint4 `.ldf`。

"重跑链"= 以下按序全过（任一冻结件或 golden 变动即触发）：
1. host `make run` 双套（sat/unsat，`sprint4/dsp/core_only/Makefile:27-29`；[A][B][C][D] 四子项，exit 0）；
2. `gen_golden.c` → 0x90556BC7（仅基建自检，非判据）；`gen_f5_goldens.c` → 八锚 + FG1 DISTINCT + `-DF5_GEN_UNWEIGHTED` 负控制必 FAIL；
3. 板 F4 子带锚 `0x2E0D8C6E`（`g_fira_f4_pass=1`）；4. 板 F5 八锚 `g_f5_pass_all=1`、8 锚互异；
5. F7 cycle（`g_f7_cyc_8ch_fira`）；6. H1（focus_differs=1 / zero_recovers=1）/ H2（FG 全绿）。
M2 板门（与上独立）：`fira_inloop=1 / setup_rc=0 / valid=1 / fg_beam_live=1 / overrun=0 / rx=poll / beam_cyc_max` + CTO 耳听。
桌面 M2 门：M2_Q_BOUNDARY_SURVEY.md §3 的 MODE-IDENT/SHIFT8 子带 CRC 测试（设计已过 critic，实现状态见 §11）。

### 0.5 验证台阶定义
- **桌面 harness**：gcc host（核 `tfb_*` 可跑；FIRA 段桌面故意 memset 0 → 子带 CRC 必 FAIL，FG2）；guard-check（`run_guard_check.sh`）。
- **上板**：AD-EXKIT V2.1 + 21569-SOM，JTAG idle 读全局（FREE-RUN，不在回调/环内断点）。本机无 cc21k，任何"编译过"只能在 CTO 板机。
- **R3**：消声室（无排期）；线③厂家函（无回函）。凡标"须等 R3"者，本轮只能做到结构完成 + 占位默认关。

---

## 1. B1 EQ + 保护限幅（O1）接入固件

### 1.1 预期收益（DSP 侧）
- 完成 O1 **功能件**（算力优化冻结令明列例外：EQ 实现+上板、保护限幅器）。
- 把 O1 成本从 [L4] 29–60 MCPS / [L2-account] 14.4–55.2 MCPS 升到 **[L1]**：`g_m2_beam_cyc_max` 的 EQ-on/EQ-off 差即 O1 板成本；
  该差可对照 T2 账**固定侧** O1 60 [L4] 的墙钟等价；T2 **争用侧**预留 `O1_contention_reserve=15` [L4] 须 H2 型 both_max−base 另测，**B1 不坐实它**。这正是冻结令解冻条件之一（"O1 上板后 margin 意外击穿 1.5×"）的**实测触发器**。
- 限幅器完成"防烧功放"的结构（阈值 t_base 仍 [L4]，见 1.5）。
- 声学/听感收益（EQ 曲线是否需要、几段）：`sprint7/sim/acoustic/S7_ACOUSTIC_SIM_REPORT.md` **无 EQ 章节**（其范围 = B5/B4/B2），仍待 R3 在轴响应；DSP 侧不裁。

### 1.2 算力代价（口径 ①墙钟；对照 §0.2）
**定点还是 float？→ 保持 float32，不迁定点。** 理由（DSP 侧）：
- SHARC+ 原生 32/40-bit float，`FIX/FLOAT` 是单周期指令类；转换只发生在 **mono 输入边界**（64 in + 64 out = 128 次/帧），
  ≈ 256 cyc [L3]，可忽略。限幅在 **Q31 整数域**做（见摆位），**不需要** 8 通道 float 转换。
- 定点 biquad 需 Q30 系数 + 64-bit 累加 + 极限环/量化噪声记账（memory.md Pitfall-002），= 新开一级截断点，违背 [ASSUME-A2]
  "不新开截断级" 的精神，且带来一整套新验证面；float 路径已桌面验 1.51e-7 [L2]（EQ_INTEGRATION_NOTE.md:67）。
- 唯一要 float 的场合是 EQ 本身；它在 mono 母线一次处理（1/8 成本），不在 8 通道循环内。

**数字**（脚本 §B；MAC 逐行取自 `eq_limiter.c:5-13`）：

| 项 | 低端 | 高端 | 出处/口径 |
|---|---|---|---|
| EQ 2–3 biquad × 64 样本 | 640 MAC × 8.51 cyc/MAC = 5,446 | 960 MAC × 50 = 48,000 | 8.51 = H1 核类 [L1-derived]（flat int FIR，**非 float 递归 biquad 同类**，故低端标 [L3]；**低端非下界**，SHARC+ 单周期 float MAC 下可能更低）；50 = 板包络上限 [L4] |
| 限幅 8ch × 64 × 2 比较 | 1,024 × 1 = 1,024 | 1,024 × 4 = 4,096 | [L3]；融进现有 TX 交织循环（c:433-447）几乎无额外遍历 |
| Q31↔float 128 次 | 256 | 256 | [L3] |
| **B1 合计** | **6,728 cyc = 5.05 MCPS** | **52,352 cyc = 39.3 MCPS** | 低 [L3] / 高 [L4] |

- 与 EQ note 的 [L2-account] 14.4–55.2 MCPS 对账：高端 39.3 < 55.2，差在 EQ note 把 8ch 限幅按 1 MAC/样本@50 计 19.2 MCPS，本文按比较指令计；
  两者同向，**不超出在档 [L4] 29–60**。
- **对照 1.5× 线**：高端 52,352 = 到线余量 57,986 的 **90%** → B1 单项高端墙钟余量 **1.510×**，刀刃；低端 1.592×。
- MCPS 口径：5.05–39.3 MCPS（= cyc×750/1e6）。

**摆位（帧内位置，均在 M2 TU，不碰冻结件）**：
```
RX half (64, Q31 identity)
  |-- ISR: FG scan + publish (不变)
main: m2_beam_poll -> m2_fira_beam_frame
  [新] EQ: rx[h] -> float -> 2-3 biquad -> float->Q31 sat -> s_m2_xeq[64]   (mono, 一次; 写新 static, 不就地改 DMA 缓冲)
  for c in 0..7:
      xw = (w_c * s_m2_xeq) >> 15           (原 c:420, 输入改读 s_m2_xeq)
      analyze -> [v2: focus] -> synthesize -> s_m2_chout
      for i: o = chout[i]
             FG nz/peak 取限幅前的 o      (保住"FIRA 逐帧失败 = out_max_abs 顶满幅"的失败特征, 见 6.4 #2)
             [新] o = clamp(o, +/-t_ch_q31[c]); g_m2_lim_clip_count += (clipped)
             tx[i*8+c] = o
```
- EQ 在 mono 输入进入 8 通道循环之前（LTI 可与逐通道延时/权重交换，EQ_PRD §2.2）；限幅在 synthesize 之后、写 TX 之前，
  `t_ch_q31[c] = round(t_base · w_c · 2^31)`，`w_c` 从 **同一张** `g_dolph_w8_q15` 取（/32768），满足 EQ note 单一来源要求，
  且 chmap 开启时用 `s_m2_chmap[c]` 同一下标（限幅阈值也随物理位置走，否则锥度保护错位）。
- float 缩放：`x_f = (float)x_q31 * 2^-31`（2 的幂，精确）；回程 `(int32)(y_f * 2^31)` **必须饱和**（EQ 提升后 |y|>1 会溢出）。

**占位处理（unity 系数 / t_base [L4]）**：
- build 门控宏 `M2_O1_EQ`，**默认关 = 预处理输出逐 token 等同现固件**（同 `M2_CHMAP_FIX` 纪律，EXP_CHMAP_AB.md §1）。
- **负控制（FG，必须）**：宏开 + unity 系数 + t_base=1.0 ⇒ 输出与现固件**逐位相同**。可证明性：板上样本是 24-bit 左对齐（低 8 位硬 0，
  DEC-S6-ALIGN-LEFT-01），float32 尾数 24 位 → Q31→float→Q31 **精确可逆**；unity biquad `y=1.0*x+0` 精确。
  ⚠ 但桌面若用冻结 chirp 做此负控制会**假 FAIL**：chirp 65,282/65,536 个样本低 8 位非零（M2_Q_BOUNDARY_SURVEY.md §3.1），
  > 24 有效位在 float32 里丢精度。桌面负控制须先把输入 `& 0xFFFFFF00`；F4/F5 锚不受影响（它们在 bench，不经 EQ）。
- **t_base 默认取 1.0 FS**（合法 Q31 永不触发钳位）而不是测试用 0.8f（`eq_test.c:84`，[L4]，不得进产品 build）。代价：线③回函前
  限幅器**结构在、保护不在**，如实标注。
- 加构建指纹 `g_m2_o1_built = M2_O1_EQ`（fw 审计 §9H：现有 6 宏 5 个无指纹，R52 stale-state 同类风险）。

**limiter 峰值口径与 EQ 群延迟（EQ_INTEGRATION_NOTE.md:109-114）**：
- 限幅在 EQ 下游，看到的是 EQ 后 + 加权后的真实峰值——摆位本身已满足"峰值口径 = 送 DAC 的值"；FG 峰值另取限幅前值（上图）。
- EQ 群延迟：2–3 biquad 的群延迟取决于系数（低频搁架/峰值滤波在其转折频率附近可达数十样本 [L3，系数待 R3]）；
  它叠加在 12.53 ms（dsp_design.md:615）之上，仍远低于 < 30 ms 判据（dsp_8ch_report.md:130）；总延迟表须在系数定后重画（M2 接口项）。
- **headroom 交互（新增，[L3]）**：冻结链有 −4.8 dB 输入 headroom 契约（tree_filterbank.h:38-41）。EQ 若有正增益（如低频 +6 dB 搁架），
  EQ 后信号会吃掉该 headroom → 节点① 回量化饱和（PF-4 病根）。B1 须把 **EQ 峰值增益 ≤ headroom 或加补偿衰减**写进系数约束；
  `g_m2_lim_clip_count` 与 `g_m1_max_abs_sample`/`0x49A00000`（−4.8 dBFS）一起读作 headroom 健康。

### 1.3 冻结件影响
- **零触碰**任何冻结件；不改任何 golden；F4/F5/F7/H1/H2 链**不需重跑**（它们在 bench 工程，不含 M2 TU）。
- 新阶段需要的新验证（非 golden，是 FG）：①负控制逐位等同（板上真数据 / 桌面 24-bit 掩码数据）；②`eq_test`+`eq_verify.py` 桌面链
  （现存，`eq_out.txt` 需先生成）；③板 FG：`g_m2_o1_built`、`g_m2_lim_clip_count`、`g_m2_beam_cyc_max` 的 on/off 差。
- 反假绿设计：unity 时 `lim_clip_count` 必为 0；给一段满幅测试音时必 > 0（限幅真在工作）；EQ 非 unity 时输出与 EQ-off **必不同**
  （同 H1 `focus_differs` 思路）。

### 1.4 验证方式
- **桌面能到**：guard-check 新增配置 `-DM2_FIRA_INLOOP=1 -DM2_O1_EQ`（并入 fw 审计 §9B 缺失矩阵）；host 编译 M2 TU 的 EQ 路径
  （需把 `m2_fira_beam_frame` 的核心做成 host 可编译、以核 `tfb_*` 代 `fira_tfb_*`——M2 TU 改动，非冻结件）；负控制（掩码 chirp）；eq_verify。
- **必须上板**：O1 [L1] 成本（beam_cyc 差）、overrun=0、`fg_beam_live`、耳听、headroom 读数。
- **必须等 R3/线③**：EQ 段数与系数（R3 在轴响应）、t_base（线③ Xmax/热额定）。本轮只能"结构 + 占位默认关 + unity 负控制"。

### 1.5 风险与前置依赖
1. **墙钟刀刃**：高端估计把余量压到 1.510×；B1 之后再加任何东西（B2）必击穿。→ 先做 §6.3 split 再接 B1，否则 O1 实测数不可解释。
2. **限幅掩盖 FIRA 逐帧失败**（§4B #2 的新交互）：满幅噪声被钳到 t_ch，`out_max_abs` 不再顶 0x7FFFFFFF，失败特征消失。→ FG 峰值取限幅前值（已写入摆位）。
3. t_base [L4] 卡线③；默认 1.0 = 无保护，须明示。
4. 系数 [L4] 卡 R3；unity 上板等于"证明接线不坏"，不是"证明 EQ 有用"。
5. 与 B2 的耦合：B2 的分数延时在 EQ 下游，仍 LTI 可交换，无冲突；但 headroom 由 EQ、权重、聚焦 FIR 三者共同消耗，须一并算。

### 1.6 DSP 侧建议
**本轮做**（冻结令例外的功能完成件），**顺序在 B6.3 之后**；默认宏关、unity 负控制、t_base=1.0、FG 峰值取限幅前。一句话：
B1 是解冻条件的实测触发器，做它就是在测"1.5× 会不会被击穿"，所以先把 831k 的成因拆清，实测数才有解释力。

---

## 2. B2 子带内分数延时 / 聚焦 v2

### 2.1 预期收益（DSP 侧）
- 交付 DEC-S5-V1-SCOPE-01 锁定的 v1 能力"近场高频展区分区（2–5 m，有用带 ≥4 kHz）"所需的 DSP 阶段：analyze 与 synthesize 之间、
  每 (通道, 子带) 一个 8-tap 分数延时 FIR（H1 harness 形状，h1_wcet_measure.c:187-208, 244-249）。
- 声学效能（焦点增益 4.85–8.09 dB @4k/6k、净超额 ≤3.9 dB，**[L2] FOCUS_EFFICACY**）：`sprint7/sim/acoustic/S7_ACOUSTIC_SIM_REPORT.md`
  §6.1 原样引用 S5 结果（未重算）；DSP 侧不引为收益，只引为"值不值 +65k cyc"的依据待定（PRD X dB 仍 OPEN）。
- DSP 侧附带给出一个**更便宜的替代摆位**（§2.2 变体 c）供声学侧评：全速率、analyze 之前的逐通道分数延时（4,096 MAC，比子带级 7,680 少 47%），
  代价是不能只对 ≥4 kHz 带聚焦。

### 2.2 算力代价
**基准 [L1]**：H1 `focus_only = 65,371 cyc/帧 = 49.03 MCPS`，8 tap × **120 samp** × 8 ch = 7,680 MAC，8.51 cyc/MAC。
**120 口径说明**：120 = sb0 8 + sb1 16 + sb2 32 + sb3 **64（未抽取 detail）**，源 `h1_wcet_measure.c:28-36`；早期 60/2.88 MMAC 是 2× 错（R15），
已退役。H1 数是 **bench 上下文**（main、无 SPORT DMA、无 SPORT ISR）。

| 变体 | MAC/帧 | cyc/帧 | MCPS | 墙钟余量（叠 831k） | L 标 |
|---|---|---|---|---|---|
| a. H1 原样（4 子带 × 8 tap） | 7,680 | **65,371** | 49.03 | **1.488×** | [L1 bench] |
| a'. 同上，按 M2/bench 1.794× 缩放 | 7,680 | 117,246 | 87.9 | 1.406× | [L3 scaled，成因未拆] |
| b. 只聚焦 sb2+sb3（≥3 kHz 标称，覆盖 v1 ≥4 kHz） | 6,144 | 52,297 | 39.2 | 1.510× | [L1-derived 线性缩放] |
| c. 全速率 analyze 前（8 tap × 64 × 8） | 4,096 | 34,865 | 26.1 | 1.540× | [L1-derived 线性缩放]；宽带聚焦，不能分带 |
| d. sb3 用 16 tap（见 2.5 精度点）+ 其余 8 tap | 11,776 | 100,236 | 75.2 | 1.432× | [L1-derived 线性缩放] |

**结论：变体 a 单项 65,371 > 到线余量 57,986 → 墙钟余量 1.488× < 1.5×，即使用 [L1] 数也越线**（§8 表）。b/c 勉强在线上，但与 B1 相加均越线。

### 2.3 冻结件影响
- 阶段落在 M2 TU 的本地子带缓冲上（H1 同法，h1:47-48），**不触碰冻结件**；F4/F5 锚仍只门 bench 核/FIRA 一致性，**不需重生成**。
- **但 chmap 权重置换等价性被破坏**：等价证明依赖"各通道滤波相同 ⇒ 输出 = w_c·y（y 共享）"（c:383-387）。加入逐通道延时后
  输出 = w_c·D_τc(y)，不再共享。**重推方案**：延时表按物理位次建（`tau_rank[8]`，边=0…中心=7），与权重**用同一个** `s_m2_chmap[c]` 取下标：
  `w = g_dolph_w8_q15[perm[c]]`，`tau = tau_rank[perm[c]]`。这样"置换 (w,τ) 对"仍位等价于"置换 TX 槽"，等价性恢复。
  acoustic 报告 §6.2 [L2/numpy 单轨] 已把"只换权重下标"的后果量化：焦点损失 **4–13 dB**（4k/2 m −13.36 dB、6k/3 m −13.21 dB），
  焦平面 −6 dB 宽扩 2.3–2.5× 或主瓣裂成等高离轴瓣；τ≡0 时 WPERM==REF（v1 等价成立）。与 c:385-387 边界声明一致。
- 新增阶段需要的**新 golden 与 FG**（非冻结锚）：延时表双轨（python 闭式 vs C 侧生成，逐值同）；`focus_differs=1`（延时真在算）、
  `zero_recovers=1`（零延时 = 跳过阶段，与无聚焦逐位同；注意 H1 教训：Q15 unity tap 32767/32768 ≠ 1，零延时必须**跳过**而非乘 1）、
  同态 snapshot/restore（R15）；产品级 golden = "chirp → analyze → 延时 → synthesize" 的子带 CRC，需扩 `gen_f5_goldens.c` 同型生成器。

### 2.4 验证方式
- **桌面**：h1_host_test 同型 4 项 check；延时表双轨；Σ|h| 与直流增益检查；chmap 置换等价的数值证明（置换 (w,τ) vs 置换槽逐位同）；
  差分金字塔跨带一致性（§2.5 第 5 点）用 tree_verify 型仿真 [L2]。
- **必须上板**：M2 上下文的 [L1] 增量（beam_cyc on/off）、overrun=0、盲带检查（§6.4 #4）、耳听。
- **必须等 R3**：焦点增益/净隔离 X dB（PRD OPEN）——DSP 只能证"延时算对了"，证不了"有用"。

### 2.5 风险与前置依赖
1. **墙钟击穿 1.5×（[L1] 数即越线）→ 触发冻结令解冻条件，须 CTO 裁定后才可实施**（§8）。
2. **前置 = chmap 远场 A/B 坐实**（EXP_CHMAP_AB.md；C1–C6 排序仍是假设，c:388-394）。延时对位置比权重更敏感：脚本 §F，F=2 m 时
   c=3 与 c=7 的延时差 44 µs ≈ 11 kHz 的半周期 [L3]，中间对排错即把高带聚焦打散；权重排错只是"两个近似权重互换"（graceful）。
   延时完全不置换的极端情形已由 acoustic §6.2 量化为 −4…−13 dB [L2]（§2.3）；中间对局部排错介于两者之间，须远场 A/B 坐实排序后才可推。
3. **前置 = 自家 16 元阵列极性 QA**（BEAM_POLARITY_CLOSURE §5.3；solo-SPL 对极性盲）。极性错则聚焦相干叠加失效，比 broadside 更敏感。
4. **需要的物理输入**：焦距 F（PRD/场景，2–5 m）、阵元真实位置（d=55 [L1] 对称对，`|x_c|=(7.5−c)·55 mm`）、声速。延时表（脚本 §F，[L3]）：
   F=2 m 中心对相对边对 122 µs = 5.86 samp@48k / 0.73 samp@6k；F=5 m 为 49 µs。
5. **8-tap 跨度精度**：sb3（48k）在 F=2 m 需 ~5.9 样本延时，落在 8-tap 跨度顶端，带顶（~12 kHz）分数精度差 [L3]；建议 sb3 用整数偏移 + 8-tap
   分数，或 12–16 tap（变体 d 成本）。
6. **差分金字塔跨带一致性**：同一物理 τ 在四个速率下各用一组 FIR 实现，交叠区两支（interp(coarse) 与 detail）相位若不匹配 → 纹波
   （tree_filterbank.h:9-16 的已知代价）。须 [L2] 量化后再定 tap/设计，本文不臆造数值。
7. Q31 饱和面：子带 FIR 在 Q31 上做 MAC，非 bit-exact 门控（M2_BEAM_WEIGHTING_SURVEY §4.3）；核 Σ|h|≤1 设计 + headroom 与 B1 EQ 共同记账。
8. 8 通道延时不同 → 各通道 FIRA 历史状态仍独立（`s_m2_fa[c]`），无跨通道问题；但聚焦 FIR 自己的跨帧尾巴（7 样本 × 4 子带 × 8 ch）要 pin 到 Block 1。

### 2.6 DSP 侧建议
**下轮**（不本轮）。前置四件：B6.3 split（拆清 831k）→ CTO 解冻裁定（墙钟越线）→ chmap 远场 A/B → 自家极性 QA。
本轮可做且不写固件的 DSP 准备：延时表双轨脚本 + 桌面 FG harness 设计稿 + 跨带一致性 [L2] 仿真方案。一句话：算法是现成的（H1），
卡的不是代码而是 58k cyc 的墙钟余量和两个声学前置。

---

## 3. B3 偏转 — 结论：本轮不做（现板不可达）

### 3.1 预期收益
无（现板）。acoustic 报告不含偏转章节（其 §1 范围 = broadside + 对称加权）；偏转 ROI 属独立立项材料。

### 3.2 算力代价（给结论所需的数字）
- **软件不可达**：{c,15−c} 对称串联，配对物理接收同一激励 [L1 拆机]；阵因子 = Σ w_c·2cos(k x_c sinθ) 为**纯实偶函数**，无法施加非对称相位
  → 零偏转权（DEC-S3-DSP-03；DEC-S5-STEER-V1-01 FLAG-A [L1]；m3_superdir_8pair 三轨机器精度等价证明 §结论 B）。**这不是算力问题。**
- **硬件叉**：16 通道独立驱动 = DAC 由 ADAU1962A 12ch（用 8）→ 需 ≥16ch（现片不够，换片或双片）、功放 8→16 路、转接板/接线全改、
  Gate-2 级不可逆（STEERING_HEADROOM_SCAN.md §2 FLAG-A）。
- **算力**：16ch 核路径 core-only 0.55× [L3 外推]；FIRA 16ch 无板测，naive 2× 现 M2 墙钟 = 1.66 M cyc > 帧预算 [L3] → 在拆清 831k 之前
  16ch 连 broadside 实时都不成立；偏转 FIR 16 tap × 64 × 16ch = 16,384 MAC ≈ 139k cyc [L3 @8.51] 还在其上。
- **栅瓣约束 [L3]** `fc(θ)=c/(d(1+|sinθ|))`，c=343，d=55 mm（脚本 §E）：θ=0° 6,236 Hz（复现 decisions_log:455 锚）/ **10° 5,314** / **20° 4,647** /
  **30° 4,158 Hz**。偏转 30° 时干净带上限已压到 v1 有用带（≥4 kHz）的边缘；任何偏轴指向性 PRD 自动触发 SC-S3-GEOM-01 d 重议（无 PM 自治权）。

### 3.3 冻结件影响
若立项：几何变（d 重议）→ Dolph 表、golden、chirp 之外的一切几何相关冻结件全部重做；不在本轮讨论。

### 3.4 验证方式
无可验；立项后先板测 16ch FIRA 真余量（STEERING_HEADROOM_SCAN.md §3 pin-first 清单 #5）。

### 3.5 风险与前置依赖
把"余量 1.6×"读成"偏转是固件功能"= 类别错误（FLAG-A 原话）。前置 = CTO 独立立项 + Gate-2 硬件叉 + d 重议 + Stage 5 硬件（无进展）。

### 3.6 DSP 侧建议
**不做**；维持 DEC-S5-STEER-V1-01"角度偏转 = 独立立项"。一句话：现板上偏转在数学上是零，不是慢。

---

## 4. B4 低频指向性（DSP 侧）

### 4.1 预期收益（DSP 侧）
acoustic 报告已给出子带差异化权重的**真实收益形态**（`S7_ACOUSTIC_SIM_REPORT.md` §3.5 / §4.2 / §5.3，[L2/numpy 单轨]）：
- 它买的是**恒定波束宽 / 覆盖均匀性**：1–6 kHz −6 dB 波束宽平坦度 24.4°→15.0°；**BW(1k) 恒 29.27°，不是低频变窄**。
- 代价：DI@4k −4.35 dB、3–6k 满驱动轴向 SPL −9.9 dB、5.5–6 kHz ±90° 泄漏接近 0 dB（§3.5）。
- 真正的"低频变窄"只能来自超指向权重（§5.3）：在**假设** WNGn ≥ −10 dB 地板下 1k 29.3→22.7°，但 SLL 回到 −13 dB、1k/30° 由一级掉三级；
  子带机制对 <1.5 kHz **无低频变窄收益**。
是否值这个代价由声学/PRD 裁；DSP 能给的是：权重从 input-scale 移到子带级——每 (通道, 子带) 一个 Q15 增益，**4 张 8 权重表**（32 值），落在 analyze 与 synthesize 之间的本地子带缓冲上
（与 B2 同一插入点）。input-scale 权重可置 unity 或直接删除（权重"搬家"，不是叠加）。

**DSP 侧先说清结构上限**：本树的真实交叉点是 **1.5k / 3k / 6k / 12k**（tree_filterbank.h:19-21），不是标称 1k/2k/4k/8k。
"低频"= sb0（0–~1.5k，6 kHz 率）+ sb1（~1.5–3k）。若声学侧要在 1 kHz 处分界，本树给不了；改树 = 改冻结核（不在本轮范围）。

### 4.2 算力代价
- 120 samp × 8 ch = **960 mul/帧** [L3]；@8.51 → 8,171 cyc（6.1 MCPS）[L3]；@50 → 48,000 cyc（36 MCPS）[L4]。替换 input-scale 512 mul（不叠加）。
- 单项墙钟余量 1.517–1.589×；与 B1 高端相加 1.432× 越线（§8）。

### 4.3 冻结件影响
- 不触碰冻结件。**但 F5 八锚的前提是 input-scale 权重**（gen_f5_goldens.c 头注："weight is INSIDE the bit-exact boundary"，权重在 analyze 之前）。
  权重移到子带级后，产品路径不再是 F5 验证过的配置 → 需要**新 golden F5'**：`chirp → analyze → 子带增益 → 子带 CRC`（每通道），
  同型扩 `gen_f5_goldens.c`（新文件，不改原生成器）；FG1 扩为 32 值互异 + 负控制（全 unity 必坍缩到 F4 锚 0x2E0D8C6E）。
- chmap：4 张表都按 `s_m2_chmap[c]` 置换（同 §2.3）。
- **差分金字塔纹波风险（结构性，[L3]）**：tree_filterbank.h:9-16 明写"各子带增益差异大时交叠区出现纹波"，telescoping 恒等只在等增益下成立。
  子带级权重 = 每通道各子带不等增益 → 每通道输出在 1.5k/3k/6k 交叠区带纹波，且 8 通道纹波不同 → 波束在交叠区畸变。**必须先 [L2] 量化
  （tree_verify 型仿真，用 acoustic §3.4 的 `s7_constbw_chosen_weights.csv` 作输入）再谈落地。** 本文不臆造纹波数值。
  acoustic 报告 §1「不能回答」第 4 条明写其按理想砖墙子带算、交叠真实行为须 DSP 侧仿真/上板——**此项归 DSP，是 B4/B5-子带级 的硬前置**。

### 4.4 验证方式
- **桌面能到全部算术**：核 `tfb_*` 可跑 → F5' 生成 + 比对 + FG1 + 负控制 + 纹波 [L2]。
- **上板**：FIRA 路径与本阶段无关（analyze/synthesize 不变），只需 M2 板门 + beam_cyc 增量 + 耳听。
- **R3**：指向性效果。

### 4.5 风险与前置依赖
- **WNG/散差敏感（引 sprint3）**：低带要指向 = 超指向类权重。三轨核实（matlab_verify_m3_superdir_8pair.md 结论 A）：ε=0.1–0.3 时 1 kHz BW
  29.27°→24–25°，WNG 从 Dolph 基线 11.84 dB 降到 +9.5~10.9 dB，ε 更小时 WNG 可到 −2.08 dB [L2]。WNG 越低对喇叭幅相散差越敏感；
  公差 MC（matlab_verify_m2_mc.md，±1 dB/±5°/±0.5 mm，N=3000，三轨收敛）在 **Dolph 基线** 8 对 iso 场景 1 kHz 已有 P(BW>30°)=5.3–6.3%
  [L2]；超指向权重下该概率**未仿真**，方向上只会更差。acoustic §5.3：无约束下限（1k 17°）需 WNGn −59…−74 dB，物理不可实现；
  §7 标明 B4 ε 扫描为单轨 [L2/numpy]（1k ε=0.3/0.01 两行由 m3 三轨锚定）。→ 前置 = 声学侧用候选权重重跑 MC + 双轨。
- 前置 = chmap A/B + 极性 QA（同 B2）；前置 = 纹波 [L2]。
- 与 B2 共享插入点与 headroom：子带增益 ≤1 时不吃 headroom。

### 4.6 DSP 侧建议
**不做本轮**。声学结论已到：收益形态是覆盖均匀性而非低频变窄，代价大（DI@4k −4.35 dB、轴向 −9.9 dB），低频变窄要付 SLL 与 30° 等级；
交叠纹波（归 DSP）未量化。若 CTO 仍要覆盖均匀性，DSP 侧工作量 = "纹波 [L2] 仿真 → 32 值表 + F5' 生成器"，算力小，验证面中。一句话：算力不是问题，纹波和 WNG 才是。

---

## 5. B5 旁瓣 / 波束宽（DSP 侧）

### 5.1 预期收益
声学侧已给（`sprint7/sim/acoustic/S7_ACOUSTIC_SIM_REPORT.md` §2 主表、§4.1/4.2；§7 双轨 numpy+MATLAB，最坏 |ΔBW| 0.0003°）：
- **全频段单一换窗被 [L2/双轨] 否决**：dolph30@1k BW 34.87°、taylor25@1k 32.97°、kaiser_b5@1k 43.87°，均破 ≤30° 红线（Dolph-20 = 29.27°，余 0.73°）。
- 有收益的形式只剩 **子带级换窗（保留 SB0 = Dolph-20）** = §4.2 = 与本文 B4 同一机制、同一代价（DI −1.5…−4.4 dB、轴向 −3.9…−9.9 dB 换平坦度 +9.5°）；
  A2 "第①层轻量点"（SB(2k) Dolph-25、SB(4k) Dolph-30）买的是旁瓣/R10（2k/90° +5.77 dB、DI −0.29 dB），不是均匀覆盖。
DSP 侧只说明：换窗 = 换 `dolph_w8_q15.h` 那张 8 值表，算力 **+0**；子带级换窗 = B4 机制（960 mul）+ 交叠纹波（归 DSP，§4.3）。

### 5.2 算力代价
0 cyc（同一 512 mul/帧循环，只换常数）。每子带不同窗 = B4 机制与代价（960 mul，纹波风险同 §4.3）。

### 5.3 冻结件影响（这是 B5 的全部工作量）
**触碰冻结表 `dolph_w8_q15.h`** → 必须重跑：
1. `gen_dolph_w8.py` **双轨**（scipy chebwin/Taylor + 独立闭式；换 Taylor 则 Track-2 闭式要另写，Barbiere 递推只对 Dolph）→ `dolph_w8_q15.csv` → 手工冻进 `.h`（三轨逐位同）；
2. `gen_f5_goldens.c` 重生成八锚 → 手工汇入 `dolph_f5_goldens.h`；FG1 DISTINCT 必过；`-DF5_GEN_UNWEIGHTED` 负控制必 FAIL；
3. 板 F5 八锚 `g_f5_pass_all=1`（F4 锚 0x2E0D8C6E 不变，c=7 unity 连续性仍成立当且仅当新窗中心权重 =1.0 归一化）；
4. 全库同源副本跟改：`eq_test.c:77-82` 硬编码 w8、`focus_sim.py:19-21` 的 29.27° 锚断言（**按设计会 raise**，须同步更新锚）、
   `spl_model_numpy.py`（taper loss）、限幅阈值 `t_ch=t_base·w_k`、`M2_STXT_TBL`（静态 Dolph 2250 表，python 烘焙）；
5. host `make run` 双套（核不变，应仍过）；F7/H1/H2 不需重跑（cycle 与权重值无关，权重仍 ≤1.0 时 GAP-SAT 残余前提成立——**新窗若有 >1.0 值则
   PREMISE-VERIFIED 失效，须重审饱和**）。
M2 固件 call-only，零改动。

### 5.4 验证方式
桌面：1–2、4、5 全部可做；上板：3 + M2 板门 + 耳听；R3：旁瓣/BW 实测。

### 5.5 风险与前置依赖
- 前置 = chmap 远场 A/B：**现在旁瓣 −9.67 dB / 30° 弱的主因是权重贴错物理位置**（[L2 numpy]，BEAM_POLARITY_CLOSURE §5.1），不是窗不好。
  A/B 没坐实之前换窗 = 在错位的阵上调窗。
- BW 红线 0.73° 余量 + 8 对 MC P(BW>30°) 5–6% [L2]：更低旁瓣的全频段窗**已被 acoustic §7 双轨坐实必破 30°**（上表）。

### 5.6 DSP 侧建议
**不做本轮**；先 B6.1。全频段换窗已被声学 [L2/双轨] 否决，不再有"一张表"的小包可做；子带级换窗并入 B4 路线（前置同 §4.6）。一句话：先把权重放对位置，再谈换窗；而换窗本身已无全频段解。

---

## 6. B6 未闭合项收口（逐项：是否为升级前置）

### 6.1 chmap 选项 B 远场 A/B（EXP_CHMAP_AB.md）
- **是前置**：B2/B4/B5 任一"按物理位置"的阶段都依赖 C1–C6 排序（§2.5 #2）。
- DSP 侧无代码；测试按 EXP_CHMAP_AB §2–6（单 build JTAG 活切 `s_m2_chmap`，2 kHz ≥8 m，30° 主判 ≥6 dB）。
- 坐实后的 DSP 动作：`M2_CHMAP_FIX` 默认由关翻开 = 字节变动 → M2 板门重跑（非冻结链）。
- 验证：上板 + 远场（无消声室可用地面反射门控/最长距离相对法）。建议：**本轮做**（测试侧）。

### 6.2 自家 16 元阵列极性 QA
- **是前置**（所有声学验证的前置；B2 尤甚）。方法 = 电池纸盆逐只 + 成对声学相消（`M2_STXT_LOCALIZE` 375 Hz build 已存在，c:611-641）。
- DSP 侧无代码；注意 §6.5 的 `#error` 守卫先补，否则 `M2_STATIC_TXTEST` 单独定义时诊断前提静默失效。建议：**本轮做**（装配/测试侧）。

### 6.3 WO-S6-BEAMCYC-SPLIT（拆 831 µs 里 compute vs FIRA 忙等）——**一切算力决策的前置**
**为什么决定真实可用余量**：
- FIRA 引擎理想 MAC 时间 [L3]：每通道 9 段窗口 [64,32,16,16,32,64,16,32,64] × 63 tap = 21,168 MAC；8 ch = 169,344 MAC/帧；
  按 4 MAC/cyc @1 GHz、100% CE（fira_fit_assessment.md:148 [L-adi]）= **42,336 cyc/帧 = F7 463k 的 9.1%、M2 831k 的 5.1%**。
- F7 每段 6,291 cyc，其中理想 MAC 平均仅 588 → **≈91%（= 1−588/6,291，上界；引擎 CE<100% 的 DMA 时间含在内）是编排（CreateTask/FixedPointEnable/QueueTask）+ DMA 取放 + 中断/自旋 + 核侧
  postscale/memcpy** [L3]。即 bench 里"忙等 + 编排"已是大头；M2 再多出 368k。
- **B1 能否放进等待期？不能（确定性地）。** 自旋在冻结的 `fira_tree.c:481`（main 上下文），M2 TU 无法在自旋内插工作；SPORT ISR 抢占自旋
  只是随机地藏住 ISR 自身时长（每帧一次），不可作 WCET 依据；确定性重叠 = ORCH-3 型流水线（双缓冲 s_seg_in/out3 + 破 [ASSUME-A1] 单线程
  scratch + 触碰冻结件 + 冻结令内），见 §7。**所以 B1/B2 的墙钟代价与现 831k 是相加的。**

**1.79× 差距的成因假设（按可证伪成本排序，全部 [L3]）**：
| # | 假设 | 零改动证伪方法 | 若成立可回收 |
|---|---|---|---|
| a | `beam_cyc_max` 是 run 内**最大值**，含首帧冷（I-cache/首次 CreateTask）；稳态 `beam_cyc_last` 可能远低 | JTAG 读 `g_m2_beam_cyc_last`（已存在，从未记录）；M2 TU 加 `_min`/第二大值（raw，C9 合规） | 未知；若稳态≈463k 则余量实为 2.9× |
| b | M2 工程 **Debug 配置优化关**（`.cproject:39` 无 value；IMPORT_GUIDE:29 "Build Debug"），冻结 fira_tree/tree_filterbank 的 postscale/memcpy 以 −O0 编译；bench 计划 −O1（BENCH_OPS_CARD:19） | 用 Release 配置（`.cproject:153` −O 开）重建同源，读 beam_cyc；整数算术与优化等级无关，bit-exact 不受影响 [L3，前提无 UB；以 M2_SELFTEST 八锚验证] | 最多 ~368k |
| c | M2 scratch `s_m2_sb*/xw/chout` 未 pin，落 Block 0 与 FIRA DMA scratch `s_seg_in/out3` 同块（fw 审计 §9F，.map 实证） | 加 `#pragma section("seg_l1_block1")`（M2 TU，非冻结）重读 .map + beam_cyc | 小到中 |
| d | SPORT RX ISR 每 1.33 ms 一次，~62% 概率落在 beam 括号内 | 读 `g_m1_cb_cyc_max`（M2 build 下 = 64 样本 FG 扫描 + 握手，[L3] 千级 cyc） | 千级，可忽略 |
| e | 真冷 I-cache（bench H1 的 cold 是 I 热的部分冷代理） | 与 a 合并读 last/min | 未知 |

**仪表化设计（不改冻结件）**：bench 工程内建 `fira_tree_probe.c` = 冻结 `fira_tree.c` 的**副本** + CCNT 括号（QueueTask→DONE 自旋 / postscale /
memcpy 三段，raw 计数），FG = 副本的 F4/F5 子带 CRC 必与八锚逐位同（证副本忠实）。产品 build 不含副本。**同源纪律登记**：副本须在 bench MANIFEST/README 登记为「诊断专用、随冻结件变动同步或删除、不进产品 build」（A 批次刚清理过松散副本，不再新增无登记副本）。
可与 hypotheses a–c 在同一次板上会话做完。**建议：本轮做，最高优先。** 产出 = "M2 稳态墙钟 [L1] + 忙等/编排/核侧三分 [L1]"，
之后 §8 汇总表全部按新基线重算。

### 6.4 §4B defer 清单里与算法相关的项
| # | 项 | 判定 | DSP 侧分析 |
|---|---|---|---|
| 2 | `fg_beam_live` 无逐帧 FIRA 失败 gating | **B1 的前置**（否则限幅掩盖失败特征） | 段 rc 在冻结 `fira_tree.c:697-708` 被 `(void)`，无法不碰冻结件而门控。M2 侧代理：FG 峰值取限幅前 + `g_m2_lim_clip_count` + "`out_max_abs` 顶满幅且 `max_abs_sample` < 0x49A00000" 判别式（IMPORT_GUIDE R57(a)）保留。 |
| 3 | `M1_RX_SLOTS=2` fallback 漏 `rx[f*M1_RX_SLOTS]` 步距 | **非前置**；本板 1B PASS 证 slot0-only 可用 | 关闭为"本板 N/A，文档警告保留"；若换官方载板再议。 |
| 4 | QueueTask 自旋在 SPORT DMA 中断里 | **已被 M2FIX 取代**（beam 在 main，c:580-607） | 关闭。残余 = overrun 盲带（c:573-579）：B1/B2 把占用推到 67–75% 后盲带 (帧周期−beam, 帧周期) 变宽 → B2 期前置：加"claim 时刻 CCNT 戳 + DMA 当前半区核对"raw 读数。 |
| 10 | 栈长度 ≥ ~16 KB | **已闭合 [L1 .map]** | 1B PASS map `ldf_stack_length = 0x1497C = 84,348 B ≈ 82 KB`（与 BATCH_PLAN §2 "栈 82KB" 一致）≫ fira_tfb 栈帧 ~6.7 KB。B1 EQ 状态/表、B2 尾巴均建议 static + pin，不走栈。 |

### 6.5 fw 审计新发现
| 项 | 判定 | 动作（全部 M2 TU/工程，非冻结件；默认字节等同） |
|---|---|---|
| `M2_STATIC_TXTEST` 缺 `#error` 守卫（fw 审计 §9C，实测单独定义可编译、扇出每 1.33 ms 覆写"静态"TX） | **6.2 极性 QA 的前置**（诊断前提静默失效） | 加 `#if M2_STATIC_TXTEST && !M2_FIRA_INLOOP #error` 三行；宏未定义时字节等同。顺带补 guard-check 配置 D/E/F（审计 §9B）。 |
| M2 scratch 未 pin（§9F） | 并入 6.3 假设 c | pragma 一行 ×6，.map 重读。 |
| `g_m1_tx_block_count` 名不副实（§9G，在 RX 回调自增，TX 无回调） | 非前置，诚实性 | 改名/注释或注册 TX 回调计数；随下次 CTO-gated commit 捎带。 |
| 6 宏 5 无指纹（§9H） | B1 前置（`g_m2_o1_built`）+ 通用 | 每宏一个 `volatile int g_m2_<flag>_built`。 |

---

## 7. 补充候选 B7：FIRA 忙等期间的调度重构（ORCH-3 类）

### 7.1 预期收益
若 §6.3 证明 831k 里自旋/DMA 等待占大头，用回调驱动/队列深度>1 让"下一段的输入组装/上一段的 postscale"与 FIRA 引擎并行，
理论上可把 B1/B2 的核侧工作藏进等待。量级 **完全 [L4]**（STEERING_HEADROOM_SCAN.md §1 #5：spin 占 30–50% 时 ~100–200k cyc，乐观上界）。

### 7.2 算力代价
负增量，量级待 6.3 实测；不可与 ORCH-1（72→9 段合并）相加。

### 7.3 冻结件影响
**必触碰 `fira_tree.c`**（自旋、单线程 scratch `s_seg_in/out3/taskMem/s_hFir`，[ASSUME-A1]/[ASSUME] fira_tree.c:598-600）→ 全链重跑 + per-task
scratch + cache 一致性（A5 flush-back 危险重引）+ 并发下 ST1 跨帧态审。最高 bit-exact 回归风险项。

### 7.4 验证方式
桌面不可（无 FIRA）；全在板；须新建并发态 FG。

### 7.5 风险与前置依赖
算力优化冻结令明列 ORCH 全停；解冻条件 = 16ch 立项 或 O1 上板后击穿 1.5×。前置 = 6.3 实测 + CTO 解冻。

### 7.6 DSP 侧建议
**不做**；只有当 6.3 显示自旋 ≥50% **且** B1+B2 必须同时进 **且** CTO 解冻，才重开。一句话：先量再谈藏。

---

## 8. 算力汇总表（口径 ①墙钟；脚本 §B/§C 输出）

### 8.1 各候选增量

| id | 候选 | 低端 cyc | 高端 cyc | 低端 MCPS | 高端 MCPS | L 标 |
|---|---|---|---|---|---|---|
| B1 | EQ 2–3bq + 限幅 + Q31↔float | 6,728 | 52,352 | 5.05 | 39.3 | 低 [L3] / 高 [L4] |
| B2 | 子带分数延时（8tap×120×8ch） | 65,371 | 117,246 | 49.03 | 87.9 | 低 [L1 bench] / 高 [L3 按 1.794× 缩放] |
| B3 | 偏转（现板） | — | — | — | — | 不可达 |
| B4 | 子带级权重（4×8 表） | 8,171 | 48,000 | 6.13 | 36.0 | [L3] / [L4] |
| B5 | 换窗 | 0 | 0 | 0 | 0 | [L1 结构] |
| B6 | 收口项 | 0 | 0 | 0 | 0 | 产品 build 无每帧算力 |
| B7 | 忙等期调度重构 | 负，[L4] | — | — | — | 不做 |

### 8.2 组合后的墙钟余量（基线 830,903 [L1 max]；1.5× 线 888,889）

| 组合 | 增量 低..高 | 合计 低..高 | 占帧 | 墙钟余量（高端..低端） | < 1.5×？ |
|---|---|---|---|---|---|
| 现状 | 0 | 830,903 | 62.3% | 1.605× | 否 |
| B1 | 6,728..52,352 | 837,631..883,255 | 62.8..66.2% | **1.510×**..1.592× | 否（高端刀刃） |
| B2 | 65,371..117,246 | 896,274..948,149 | 67.2..71.1% | 1.406×..**1.488×** | **是（连 [L1] 低端也越线）** |
| B4 | 8,171..48,000 | 839,074..878,903 | 62.9..65.9% | 1.517×..1.589× | 否 |
| B1+B2 | 72,099..169,598 | 903,002..1,000,501 | 67.7..75.0% | 1.333×..1.477× | **是（低端也越线）** |
| B1+B4 | 14,899..100,352 | 845,802..931,255 | 63.4..69.8% | 1.432×..1.576× | 高端是 |
| B2+B4 | 73,542..165,246 | 904,445..996,149 | 67.8..74.7% | 1.338×..1.474× | 是 |
| B1+B2+B4 | 80,270..217,598 | 911,173..1,048,501 | 68.3..78.6% | 1.272×..1.463× | 是 |

### 8.3 与 T2 账（口径 ②）并列，仅参考、不相加
T2 保守闭合：M_contention 20.59 + 三预留 30/15/30 = 95.59 ≤ 210.19（DEC-S5-T2-CLOSURE-01）。该账固定侧 = F7 347.45 + focus 49.03 + O1 60 [L4]
= 456.48 MCPS ≈ 608,640 cyc 等价，**已含 B2 与 B1 的 [L4] 上限**，且以 bench 463k 为核。它和墙钟表的差 = 本文 §0.3 那个未拆的 1.79×。
两表不可互证：T2 账说"B1+B2 装得下"，墙钟表说"装不下"——两口径答案不同、不可互证（F60 纪律：不称矛盾），差异归因于未拆的 831k——再次指向 B6.3。

### 8.4 冻结令解冻条件是否会被触发
- 解冻条件原文："可控音柱（角度偏转 16ch 硬件叉）立项 **或** O1 上板后 margin 意外击穿 1.5x"（decisions_log:725）。
- **B1 单项**：墙钟 1.510–1.592× → 高端估计下**未击穿但刀刃**；实测（[L1]）落在哪一端由 B6.3 与 O1 上板决定。
- **B2 单项**：即使用 [L1] bench 数（65,371）也把墙钟压到 1.488× → **按墙钟口径会触发**"击穿 1.5×"条件。
- **B1+B2**：低端 1.477×，高端 1.333× → **必触发**。
- **CTO 须先裁一件事**：解冻条件里的 "margin" 用哪个口径判。DSP 侧建议**墙钟口径**（唯一含 M2 真实上下文的 L1 数）；若 CTO 取 T2 账口径，
  则 B1+B2 纸面不触发，但那是在 1.79× 差距未解释的前提下。
- 反向可能：若 B6.3 证明 368k 大部分可回收（如假设 b），基线回到 ~463–530k，则 B1+B2+B4 高端 1.78–1.96×、低端 ≥2.45×（脚本 §C 按新基线重算），均不触发解冻条件。
  **这就是 B6.3 必须先做的算术理由。**

---

## 9. DSP 侧排序建议（PM 综合时可改）

1. **B6.3 WO-S6-BEAMCYC-SPLIT**（本轮，最高优先）：读 `beam_cyc_last`、Release 配置对照、scratch pin、probe 副本三分。产出新基线。
2. **B6.5 守卫与指纹**（本轮，一起上板；默认字节等同）：`#error` 守卫、6 个宏指纹、guard-check 矩阵补全。
3. **B1 O1 接入**（本轮，在 1 之后；冻结令例外件）：宏默认关、unity 负控制、t_base=1.0、FG 峰值取限幅前、headroom 约束进系数规格。
4. **B6.1 chmap 远场 A/B + B6.2 自家极性 QA**（本轮，测试/装配侧；DSP 无代码）——它们是 B2/B4/B5 的共同前置。
5. **B2 聚焦 v2**（下轮）：前置 = 1 + 4 + CTO 解冻裁定（墙钟越线）；本轮只做延时表双轨与 FG 设计稿。
6. **B4 / B5**：声学结论已到（§3.5/§4.2/§5.3/§7）——全频段换窗 [L2/双轨] 否决；子带级换窗/恒定波束宽有收益但代价大且单轨；
   两者合并为一条"子带级权重"路线，前置 = 4 + 交叠纹波 [L2]（归 DSP，未做）+ 声学双轨 + MC。不本轮。
7. **B3 不做；B7 不做。**

## 10. 给 CTO 决策清单的 DSP 侧输入
1. 解冻条件 "margin 击穿 1.5×" 的判定口径：墙钟（建议）还是 T2 账？
2. 产品 build 是否改用 Release（−O 开）配置？（若 B6.3 假设 b 成立，这是一条零算法改动的余量来源，但改变二进制 → M2 板门重跑。）
3. B1 限幅 t_base 默认 1.0（无保护、如实标注）还是保留 0.8 占位（[L4] 进产品 build，违 C3 精神）？——DSP 建议 1.0。
4. B2 go/no-go 挂在 B6.3 结果 + 口径裁定之后，而不是现在。
5. chmap 远场 A/B 过门后 `M2_CHMAP_FIX` 默认翻开的授权（字节变动，CTO-gated）。

## 11. 附：验证链与反假绿设计速查
- 冻结链六步见 §0.4；本轮候选中**只有 B5 触碰冻结件**（表）；B1/B2/B4/B6 全在 M2 TU/工程/测试侧。
- M2_Q_BOUNDARY_SURVEY §3 桌面子带 CRC 测试（MODE-IDENT 必复现八锚 / MODE-SHIFT8 必 FAIL）：设计过 critic，**仓内无任何实现**
  （`grep -rl SHIFT8 --include=*.c/*.h/*.py` 零命中，2026-09-02），B1/B2 引入的 host 可编译 M2 帧函数正好是它的载体——建议合并成一个桌面 M2 harness。
- 每个新阶段的 FG 三件套：①默认关字节等同；②开而 unity 时逐位等同（负控制）；③非 unity 时输出必变（differs）+ 板上健康计数器（raw）。
- 24-bit 掩码规则：任何 float 参与的桌面负控制先 `& 0xFFFFFF00`（§1.2）。

## 12. 引用
decisions_log.md:375-381（DEC-S3-DSP-03）/ :723-725（T2 闭合、H2R、冻结令）/ :813-900（STEER-V1、OPT-ORDER、V1-SCOPE、EQ-O1）/ :1013（M2 板 PASS）/ :1028（S7 SCOPE）；
COMPUTE_LINE_CLOSURE_LANDING.md；H2_PASSLINE_DERIVATION.md；F7_CLOSING_RECORDS.md:37-45,114-124,152-168；H1_FINAL_RULING_MATERIAL.md；
h1_wcet_measure.c:25-49,187-208,229-254；EQ_INTEGRATION_NOTE.md；eq_limiter.h/.c；eq_compute_budget.py；M2_BEAM_WEIGHTING_SURVEY.md；
M2_Q_BOUNDARY_SURVEY.md §0/§3；STEERING_HEADROOM_SCAN.md §0-§3；STAGE4_BATCH_PLAN.md §4B；EXP_CHMAP_AB.md；BEAM_POLARITY_CLOSURE_20260708.md §5；
m1_loopback_tdm.c:62-69,240-249,353-450,479-517,556-607,611-659；m1_main.c:55-86；fira_tree.c:424-481,590-660,675-708；tree_filterbank.h:5-41,130-140；
gen_f5_goldens.c:1-40；fira_fit_assessment.md:148；matlab_verify_m2_mc.md；matlab_verify_m3_superdir_8pair.md；.cproject:39,153；BENCH_OPS_CARD.md:19；
board_artifacts/M1_Loopback_M2build_1B_PASS_20260616.map.xml（ldf_stack_length）；PM 审计 fw_code_audit.md §1.4/§2/§9、algo_code_audit.md §1-§8；
sprint7/sim/acoustic/S7_ACOUSTIC_SIM_REPORT.md §1/§3.5/§4.2/§5.3/§6.1/§6.2/§7（acoustic teammate，2026-09-02）。
