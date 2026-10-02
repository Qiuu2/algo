# 撤回登记：冻结子带树的"1.5k/3k/6k"子带边界（铁律五：声明 + 反扫 + 加标）

> **DEC**：DEC-S7-RETRACT-SUBBAND-01（decisions_log 末尾）｜**日期**：2026-09-26｜**执笔**：PM（lead）｜**CTO 授权**：会话内"根据目前的信息先开干"（2026-09-26，对 PM 所列"批准撤回全库传播"一项的答复）
> **缘起**：侧面 30 dB 分析的独立 critic 第 1 轮（`sprint7/critic/CRITIC_G_SIDE30_R1_20260926.md` F1，BLOCKER）；PM 用独立模型复核成立。
> **本文性质**：勘误与影响登记，不改任何冻结件字节；冻结头文件用旁注文件加标（理由见 §4）。

---

## 1. 撤回声明

以下说法**撤回**：

> 冻结树 `tree_filterbank.{c,h}` 的 4 个子带为 SB0 <1.5k / SB1 1.5–3k / SB2 3–6k / SB3 6–12k，交叉点 12k/6k/3k/1.5k；子带可视为带通，可按子带施加不同增益或延时。

**更正**（[L2 host]，两条独立证据链）：

- **输入与分界**：M2 以 48 kHz 喂树，3 级半带抽取。实际分界为 **3k / 6k / 12k**：
  - **SB0 ≈ 0–3 kHz**：≤2.5k 为 0 dB，2.75k 为 −0.4 dB，3k 为 −6.0 dB（PM 早先复算的 −9.0 dB 是 SB0 奈奎斯特处的采样假象，critic R3a 指出），3.5k 为 −71 dB。
  - **SB1 ≈ 3–6k，SB2 ≈ 6–12k，SB3 ≈ 12–24k**。
  - **1 kHz 在 SB0 内部**，不在任何交叠区。
- **detail 子带不是带通**，而是未做延时对齐的梳状残差：
  - 算法为 detail = 本级 − interp2(下一级)（`tree_filterbank.c:161-163`），没有延时对齐。
  - 示例：SB1 在 500 Hz 为 +5.9 dB、1 kHz 为 −5.7 dB、1.5 kHz 为 +5.3 dB；SB3 在 2 kHz 为 +5.9 dB。
  - **只有 4 个子带增益全相等时**，telescoping 才精确重建（PR 误差 1e-16）。
- **推论**：在这棵树上按子带施加不同加权或校准，会产生梳状失真。critic 用真实树 [L2 host] 复算，分频段加深方案的侧面衰减只有 12–21 dB，不是理想砖墙模型给出的 32–38 dB。

**证据**：

| 轨 | 方法 | 出处 |
|---|---|---|
| A | critic 编译冻结 C 源（只读）实跑 + 解析 | `sprint7/critic/CRITIC_G_SIDE30_R1_20260926.md` F1；critic 脚本在该文件附录列出 |
| B | PM 用 numpy float 按 `tree_filterbank.c:108-205` 同运算顺序复刻 | `sprint7/sim/side30/s7_tree_subband_response.py` + `.log` |

**根因**：

1. 头文件注释把 a3（6 kHz 率）的内容误写成"0–~1.5k"。实际上最后一级半带在 12 kHz 率下截止于 3 kHz。
2. 2026-05-29 PF-4 已在桌面仿真 [L2] 中测到"detail 子带带外抑制 ≈0 dB，是互补重建残差而非隔离带通"（`sprint3/dsp/pf4/sub1_q15_stopband.md` §2.2），但沿用了错误的边界标签。
3. S7 声学报告 §0.1 把注释标成 **[L1 代码]**：读注释当成了实测（C2 型错标）。

---

## 2. 影响分级

| 级别 | 含义 |
|---|---|
| **作废** | 结论依赖错误边界或"子带可分别加权"的前提，数字不再成立 |
| **标签错·数值不受影响** | 数值结论与边界无关，只是频段标签写错 |
| **待核** | 前提可能同病，尚未验证，不下结论 |

### 2.1 作废

- **S7 B5-2（子带级恒定波束宽，设计 A/B/C）与 B5-3 §4.2（子带级换窗）**：`S7_ACOUSTIC_SIM_REPORT.md` §3、§4.2 以及 `s7_constbw_*.csv`、`s7_windows_sweep.py` PART 2。这些都按理想砖墙 1.5k/3k/6k 计算，真实树上实现不了。
- **S7 B4 的"子带级权重"实现路径与算力估计**（`S7_DSP_ASSESSMENT.md` §5 子带权重段；提案 B4 算力行"8,171–48,000 cyc"）：机制在这棵树上不成立。**B4 §5 的逐频率物理边界数字**（MVDR/WNG，与子带无关）**保留**。
- **提案里依赖上面两项的推荐与挂起理由**：`S7_ALGO_UPGRADE_PROPOSAL.md` 的 B4/B5 小节、§4 算力表中的 B4 和 B1+B4 两行、§5.2 挂起项、§6 D6 决策材料；以及 DEC-S7-RULINGS-01/02 D6 中"B5-2 挂起、待 B6.10 回答"的前提。**需要 CTO 重新裁定。**
- **我方 2026-09-26 会话中"每子带加深、稳健设计多挣 1–4 dB"的数字**：从未落库，已在会话中口头撤回，这里一并登记。

### 2.2 标签错·数值不受影响

- **PF-4 定点化的头条数值**（子带 SNR 74.6–78.7 dB、SB0 抗混叠 77.7 dB（>4.5 kHz）、重建 SNR ~300 dB，以及"detail 带 ≈0 dB、不是隔离带通"的定性结论）：不依赖边界标签，结论不变。**例外**：`sub1_q15_stopband.md` §2.2 表中各子带"带外抑制"的具体数值（SB0 11.4 dB、SB1–SB3 −0.1…−0.0 dB）是按错误的通带/阻带定义（`sub1_q15_stopband_v2.py` SB_DEF）算的，**作废**（critic R3a F3）。
- **F-2 MINOR 条目**（"子带边界 vs 规格 8k/4k/2k/1k 对齐；1 kHz 落 SB0/SB1 交叠区"）：后半句错，1 kHz 在 SB0 内部。条目本身（边界与规格不对齐）仍成立，只是实际边界是 3k/6k/12k。

### 2.3 待核

- **B2 聚焦 v2（子带内分数延时）**：它的声学收益（S5 focus_sim）假设各子带是带通、可以分别延时。detail 带是梳状残差，逐通道逐子带施加不同延时很可能同样出梳状失真。**没有验证，不下结论**；B2 重启前必须先在真实树上核。H1 bench 的 FG（focus_differs / zero_recovers）只证实"改变了输出"，证不了"声学上正确"。

---

## 3. 反扫结果与加标

**反扫方法**：

- `git grep -n -I -E` 匹配 `1.5k/3k/6k`、`SB0 <1.5k`、`0–~1.5k`、`1.5–3k`、`12k/6k/3k/1.5k`、`交叉点.*1.5k` 等写法；
- 加宽匹配"子带/SB0/SB1/coarse/交叠/crossover"前后 40 字符内的 `1.5k`、`1500`、`1.5 kHz`；
- 共命中 **15 个 tracked 文件**（CSV/log 单列）。

| # | 文件:行 | 内容 | 级别 | 处置 |
|---|---|---|---|---|
| 1 | `sprint4/dsp/core_only/src/tree_filterbank.h:19,24` | 交叉点 12k/6k/3k/1.5k；SB0 "0–~1.5k" | 根源注释 | **冻结件，本体不动**，旁注 `tree_filterbank.h.ERRATUM.md`（§4） |
| 2 | `sprint3/dsp/tree_filterbank.h:19,24` | 同上（原始副本，md5 同 #1） | 根源注释 | **本体不动**，旁注 `sprint3/dsp/tree_filterbank.h.ERRATUM.md` |
| 3 | `sprint7/sim/acoustic/S7_ACOUSTIC_SIM_REPORT.md:21,51,135,137,182-184` | 边界 [L1 代码] 标；B5-2 结论 | 作废 | 文首撤回横幅 + §0.1/§1/§3/§3.5/§4.2 逐处加标 |
| 4 | `sprint7/sim/acoustic/s7_common.py:66-67` | `SUBBANDS` 字典 | 作废（仅供复现旧数） | 加注释，**不改值**（改了会让旧数不可复现） |
| 5 | `sprint7/sim/acoustic/s7_windows_sweep.py:21,126,130` | PART 2 按 1.5k/3k/6k | 作废 | 加注释 |
| 6 | `sprint7/sim/acoustic/s7_windows_sweep.log:108`、`s7_constbw_*.csv`、`sprint7/sim/side30/s7_side30_r1_feasibility.log`（"LP-SB0 800-1.5k"及 D1–D3 分频段行） | 生成物 | 作废 | **不改**（生成物），由本表覆盖；r1 脚本头部已注明其分频段结果作废 |
| 7 | `sprint7/docs/S7_DSP_ASSESSMENT.md:263,267-268,280` | "<1.5 kHz"、"真实交叉点 1.5k/3k/6k/12k"；子带权重机制 | 作废 | 文首部分撤回横幅，并在 263、267–268、280 三处逐处加标（R3a F1 补上 263） |
| 8 | `sprint7/docs/S7_ALGO_UPGRADE_PROPOSAL.md:125,130,138`、B4/B5 小节、§4、§5.2 | 同上 | 作废 | 文首横幅 + 逐处加标 |
| 9 | `sprint2/docs/decisions_log.md:517` | F-2 待做项 | 标签错 | 加 ↑注（不改原文） |
| 10 | `sprint2/docs/decisions_log.md` 中 DEC-S7-RULINGS-01 D6、RULINGS-02 D6 补、S7 B 提案落库条 | B5-2 挂起前提 | 前提撤回 | 各加 ↑注（不改原文） |
| 11 | `sprint2/docs/PROJECT_HANDOVER.md:173` | F-2 行 | 标签错 | 行内加标 |
| 12 | `sprint2/docs/simulation_coverage_audit.md:174` | F-2 | 标签错 | 行内加标 |
| 13 | `sprint3/audit/PF9_post_simulation_panorama.md:53` | F-2 行 | 标签错 | 行内加标 |
| 14 | `sprint3/dsp/pf4/sub1_q15_stopband.md:66,70-73`（§2.2 表）、`sub2_fixed_vs_float.md:80-81` | 频段标签；§2.2 带外抑制数值 | sub1 §2.2 数值**作废**（定性结论保留）；sub2 只是标签错，数值不受影响 | 加标（措辞已按 R3a F3 更正） |
| 15 | `sprint3/dsp/pf4/q15_stopband_sim.py`（加注前第 17、120、121、156、172、264、389、390 行）、`sub1_q15_stopband_v2.py`（加注前第 96、141、143–146、200 行） | 频段标签/注释；v2 的 SB_DEF 定义 | q15：标签错，半带阻带数值不受影响；v2：SB_DEF 错，由它算出的带外抑制数值作废 | 文件头加勘误注释并逐行列出；注明第 239–270 / 255–261 行是 437 抽头参考核自己的频段，不是树 |

统一标签写法：

> ⚠【勘误 2026-09-26 · DEC-S7-RETRACT-SUBBAND-01】[L2 host 复算] 分界 3k/6k/12k（SB0≈0–3k，1 kHz 在 SB0 内），detail 带是未对齐梳状残差；见 `sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md`

---

## 4. 为什么冻结头文件本体不改

- `tree_filterbank.h` 的 md5 `7397ff0e…2912` 是上板前逐字节核对的身份码（`sprint3/audit/BENCH_OPS_CARD.md:13`、`sprint4/dsp/core_only/MANIFEST.md5` ★核-verbatim）。改一个注释字节，就会让测试员的核对步骤失败，并牵动 R14 证据链的身份核对。
- 所以采用"本体不动 + 同目录旁注文件 + 本登记 + decisions_log"的方式加标。
- 如果 CTO 希望直接在头文件内加注，需要单独给 CTO_OK，并同步更新 MANIFEST.md5、BENCH_OPS_CARD 的身份码和所有引用该 md5 的文档。

---

## 5. 仍待 CTO 裁定（本撤回引出）

1. **B5-2 / B4 在 S7 里的处置**：原来的"挂起、待竞品对比"前提已不成立，应改为"在现有树上不可实现"。频率相关加权只剩两条路：全频段单表（重开 D6），或每通道滤波器（改架构）。
2. **B2 重启前是否先在真实树上核验子带延时**（§2.3）。
3. （可选）是否批准在冻结头文件本体内加注（§4）。
4. **设计子带与冻结实现不一致**（2026-10-02 补，CRITIC_Q_R1 P1-M2）：DEC-S2-009（LOCKED）和 PRD §0 / §3.3 写的是 4 子带"500-1k/1k-2k/2k-4k/4k-8k，SB0 ÷16"；冻结实现是 3 级半带差分金字塔（[L2 host 复算] 分界 3k/6k/12k，SB0 ÷8，sb3 未抽取，detail 带是梳状残差）。PRD §3.3 的验证方法"CCES 代码实现确认"在冻结代码上不成立。请 CTO 定：修订 DEC-S2-009 与 PRD §3.3、承认冻结树结构，还是挂到 DEC-S7-SIDE30-01 ③ 改架构一并处理。
5. **1 kHz 超指向兜底没有实现路径**（2026-10-02 补，CRITIC_Q_R1 R-7）：R5 的兜底按 DEC-S2-013 是子带级超指向（SB0/SB1），与 S7 B4 同机制，在冻结树上做不了。待核后请 CTO 定：是否改挂每通道滤波器路径（DEC-S7-SIDE30-01 ③），以及 DEC-S3-DSP-06"实测超 30° 即启用"的触发条件在 BW@1k 线降级（PM 拟）后如何改写。

---

## 6. 补标记录（2026-10-02，PM）

**缘起**：2026-10-02 为整理《算法开发手册》通读仓库时发现两类遗漏：

- §3 的反扫只按边界写法（`1.5k/3k/6k` 等）匹配，漏掉了**不写边界数字、但建在"子带可分别加权或延时"前提上**的文字；
- §3 第 8 行写的是"文首横幅 + 逐处加标"，但提案的 §0、§4 算力表、§5.2、§6 实际只有文首横幅。

本次按 §3 的统一标签补标，**只加标、不改原文**，冻结件不动：

| # | 文件 | 补标位置 | 级别 |
|---|---|---|---|
| 16 | `sprint7/docs/S7_VERIFICATION_PLAN.md` | 文首横幅；§2、§4、§5 节首；§9.2 表后 | §4 与 §5 的每子带部分作废；§2 待核；§5 全频段单表流程保留 |
| 17 | `sprint7/docs/S7_ALGO_UPGRADE_PROPOSAL.md` | §0 摘要后；§4 算力表后；§5.2 后；§6 决策表后 | 补齐第 8 行的"逐处加标" |
| 18 | `sprint2/docs/prd_update.md` | §3.1.1 诚实标注后；§3.1.2 汇总后；§6 风险表后；§11 v2.5 记录补注 | "选项 1.5 子带标量加深"不可实现；二级保底承诺不受影响 |
| 19 | `sprint3/audit/A1_static_weight_tuning.md` | §5 第 1 条下 | 不可实现 |
| 20 | `sprint3/audit/A2_fib_feasibility.md` | §1.2 表后 | 两层方案的前提不成立 |
| 21 | `sprint3/audit/A3_decision_recommendation.md` | 文首（表头后） | 选项 1.5 不可实现 |
| 22 | `sprint3/audit/critic_a123_rv.md` | §4.2 裁定后 | 当时的"证真"只验了单频阵因子，没验架构前提 |
| 23 | `sprint3/audit/critic_bootstrap_rv.md` | §2 一致性表后 | R10 行前提撤回 |
| 24 | `sprint3/audit/NEXT_SESSION_BOOTSTRAP.md` | 第 14 行下（顺带标注同行 17×/33× 已被板上推翻）；R 表后 | 标签错 + 前提撤回 |
| 25 | `sprint3/dsp/dsp_8ch_report.md` | §2.1 子带表后 | 标签错（设计意图 ≠ 冻结树实际行为） |
| 26 | `sprint3/pf8/PF8_retrospective.md` | "CTO 元层级承认"条下 | 当时被"漏看"的方案本身不成立 |
| 27 | `agents/critic/memory.md` | LESSON-012 的 followup_note | 同 #22 |
| 28 | `sprint2/docs/decisions_log.md` | "锁定基线一览"DSP 行下 ↑注 | 标签错（同条顺带注明 33×/17× 已被板上推翻） |

**补充反扫方法**：`git grep -n -E '子带标量加深|选项 ?1\.5|每子带独立|子带独立加权|子带隔离|子带级标量|SB2 ?单独|SB2\(2kHz' -- '*.md'`，逐条人工判定。以下命中判为不需加标：`sprint2/docs/decisions_log.md:97`（Sprint 1/2 Kaiser FIR 设计描述"满足子带隔离需求"，不涉及本树）；`sprint3/dsp/pf4/sub1_q15_stopband.md:79,115`（本身就是"detail 带不是隔离带通"的正确结论）。

**教训**：撤回一个**机制前提**时，只按数字写法反扫会漏掉"前提型"依赖。要再按机制关键词（这里是"子带可分别加权 / 延时"）扫一遍，并逐条核对登记表里声称"已逐处加标"的文件是否真的逐处加了。

### 6.2 第二轮补标（2026-10-02，按独立 critic `sprint7/critic/CRITIC_Q_ERRATA_20261002.md`）

**缘起**：上面第一轮补标送独立 critic，判 FAIL：① 按机制关键词复扫仍有 R-1…R-9 九组残留；② 第一轮 14 处重述冻结树数字的新标里有 12 处漏了统一标签 `[L2 host 复算]`。② 已全部补上（现在本登记 §6 涉及的所有新标都带该标签）。另外更正一处自述：第一轮写的"逐条人工判定"不准确——第一轮命中里 `NEXT_SESSION_BOOTSTRAP.md:66` 与 `critic_a123_rv.md:122` 既没加标、也没列入排除，本轮补上（#29、#30）。

| # | 文件 | 补标位置 | 级别 |
|---|---|---|---|
| 29 | `sprint3/audit/NEXT_SESSION_BOOTSTRAP.md` | 消声室启动 prompt 代码块后 | 任务④"否则启用选项1.5"作废；任务②超指向兜底待核 |
| 30 | `sprint3/audit/critic_a123_rv.md` | §5 自洽性表后 | 作废 |
| 31 | `sprint3/audit/A2_fib_feasibility.md` | 文首横幅（覆盖 §0–§5；#20 只覆盖 §1.2） | 作废（§4 子带率另属标签错） |
| 32 | `sprint3/audit/SPRINT3_DESKTOP_CLOSURE.md` | §7"Sprint 4 战略储备"条下 | 作废 |
| 33 | `deliverables/algorithm_validation/EXP_COMPET_BEAM_VS_FREQ.md` | 文首；§6 判定矩阵"关键澄清"后 | 前提作废（对比实验本身保留） |
| 34 | `sprint7/docs/S7_DSP_ASSESSMENT.md` | 文首横幅后；§2.2 结论后 | 变体 b 作废：按真实分界约 1.495× [L3]，越线；原横幅"算力台账不受影响"一句对变体 b 不成立 |
| 35 | `sprint7/docs/S7_ALGO_UPGRADE_PROPOSAL.md` | B2"单项即越线"条下 | 同 #34 |
| 36 | `sprint2/docs/decisions_log.md` | R 表后；DEC-S2-013、DEC-S3-DSP-06 下 ↑注 | 1 kHz 超指向兜底（子带级）待核；见 §5 第 5 条 |
| 37 | `sprint2/acoustic/1khz_optimization.md` | §3.1 算力增量后 | 待核 |
| 38 | `sprint2/docs/decisions_log.md` | DEC-S2-002、DEC-S2-009 下 ↑注 | 标签错；设计与实现不一致待 CTO（§5 第 4 条） |
| 39 | `sprint2/docs/prd_update.md` | §0 表后（顺带注 d=30 应为 [L0]）；§3.3 表后（顺带注 ≥10× 判据已退役）；§11 补注改正 | 标签错；待 CTO（§5 第 4 条） |
| 40 | `sprint4/dsp_migration_inventory.md` | 项 1 结论后 | 标签错（表内"SB0 16×"与"3 级树"本身矛盾） |
| 41 | `sprint2/docs/PROJECT_HANDOVER.md` | §3.3 子带行下 | 标签错 |
| 42 | `sprint2/docs/decisions_log.md` | DEC-S5-V1-SCOPE-01 下 ↑注 | v1 聚焦的逐子带延时前提待核（同 §2.3） |
| 43 | `sprint7/sim/dsp/s7_dsp_compute_ledger.py` | 文件头注释 | B4 及其组合行作废，数值不改（便于复现旧表） |

**#34/#35 的数**：变体 b 原为"只聚焦 sb2+sb3（≥3 kHz 标称）"= 96 样本/帧 → 6,144 MAC → 52,297 cyc → 1.510×。按真实分界，要覆盖 v1 有用带 ≥4 kHz 须含 SB1（3–6k）：sb1+sb2+sb3 = 16+32+64 = 112 样本/帧 → 7,168 MAC → 61,013 cyc → 1,333,333 / (830,903 + 61,013) = **1.4949×** [L3，按 H1 的 65,371 cyc / 7,680 MAC 线性缩放]。Python 与 MATLAB 两轨独立复算一致（2026-10-02）。子带样本数出处：`sprint5/dsp/harness/h1_wcet_measure.c:28-31`。

**第二轮反扫方法**：`git grep -l -I -E '每子带|逐子带|子带级|子带内|子带权重|子带加权|子带延时|子带独立|独立加权|子带标量|SB2 ?单独|恒定波束宽|per-subband|subband 值得|500-1k ?/ ?1k-2k|500–1k|SB0 ?\(500'`（全部 tracked 文本，不含 `knowledge_base/`），命中 69 个文件。其中带撤回标记的 29 个，逐行结论以 critic 的复扫为准（R-1…R-9 已全部处理）；不带标记的 40 个由 PM 逐个判定，均列入下面的排除清单。

**排除清单（不加标，理由）**：

- **Sprint 2 设计史及其脚本 / 模板**（按 06-04 CTO 令"历史按写时为真"；结论已由加标文档承载）：`sprint2/SPRINT2_CTO_REPORT.md`、`sprint2/dsp/dsp_design.md`、`sprint2/dsp/budget_calc.py`、`sprint2/dsp/cces_template/src/beamformer.{c,h}`、`sprint2/docs/sprint3_kickoff_checklist.md`、`sprint2/patent/patent_map.md`、`sprint2/patent/formulas.md`、`sprint2/critic/critic_review.md`（模板代码的结构评审）、`sprint2/acoustic/diff_1khz_optimization.py`（#37 的计算脚本）、`sprint3/audit/A2_fib_feasibility.py`（#31 的计算脚本）、`sprint2/docs/decisions_log.md:50`。
- **本身就是正确结论或正确的结构描述**（子带相加、逐子带 CRC 门、每帧 120 样本）：`sprint2/dsp/fir_design_verify.py`（注释指出"每子带独立抽取会破坏差分恒等式"）、`sprint3/dsp/pf4/sub1_q15_stopband.md:79,115`、冻结件 `sprint3/dsp/tree_filterbank.c` 与 `sprint4/dsp/core_only/src/tree_filterbank.c`（不动）、`sprint4/dsp/core_only/src/tfb_8ch.h`、`sprint4/core_only_migration_plan.md`（8ch 包裹层对各子带用同一组通道权重，等增益下精确重建）、`sprint3/audit/fira_fit_assessment.md`、`sprint4/dsp/fira_integration_plan.md`、`sprint4/dsp/fira/{F4_BITEXACT_HANDOFF.md,F5_F7_PLAN.md,fira_regression.c}`、`sprint5/steering_scan/STEERING_HEADROOM_SCAN.md`（逐子带 bit-exact 回归）、`sprint6/STAGE4_ALGORITHM_VALIDATION_TEST.md`、`sprint6/dsp/audio/{M1_ARCH_INPUT_DATA.md,M2_Q_BOUNDARY_SURVEY.md,m1_cces_project/M1_CCES_IMPORT_GUIDE.md}`。
- **"独立加权"指按通道、不是按子带**：`sprint3/acoustic/sweep_d55.py`、`sprint3/audit/matlab_independent_verification.md`、`sprint3/audit/matlab_verify_m3_superdir_8pair.md`。
- **成本替身与选项清单**：`sprint5/H1_WCET_WORKORDER.md`、`sprint5/dsp/harness/h1_wcet_measure.c`（H1 成本替身，B2 待核已覆盖）、`sprint6/dsp/audio/M2_SURVEY.md`（只列选项）、`sprint5/steering_scan/STEER2_NUMBER_FIX_DRAFT.md:47`（"子带率 3–24 kHz"沿用设计表；样本数已由 H1 MAC-2× 更正，见 `h1_wcet_measure.c:28-40`）。
- **评审记录与撤回本身的材料**：`sprint7/critic/CRITIC_B_PROPOSAL_20260902.md`、`sprint7/critic/CRITIC_C_RULINGS_20260902.md`（当时对提案的评审，提案本体已加标）、`sprint7/critic/CRITIC_H_SIDE30_R2_20260926.md`、`sprint7/critic/side30_r1_scripts/*`（撤回的复核脚本）。
- **文献**：`sprint7/docs/S7_LIT_REGISTER_SIDE30.md`（文献里的恒定波束宽，不涉及本树）。
- 第一轮排除的 `sprint2/docs/decisions_log.md:97`（"满足子带隔离需求"）现由 DEC-S2-002 下的 ↑注（#38）覆盖。

**第一轮命中逐条处置**（第一轮 `git grep` 命中 30 条；行号为第一轮扫描时的行号）：
`agents/critic/memory.md:623` → #27｜`sprint2/docs/decisions_log.md:97` → 第一轮排除，现由 #38 覆盖｜`sprint2/docs/prd_update.md:127,148,299` → #18｜`sprint3/audit/A2_fib_feasibility.md:34,36,60` → #20/#31，`:44` 是本轮新标本身｜`sprint3/audit/A3_decision_recommendation.md:14,16,23,27,30,39,43` → #21（:39、:43 第二轮补进横幅清单），`:9` 是新标本身｜`sprint3/audit/NEXT_SESSION_BOOTSTRAP.md:66` → **第一轮漏判**，第二轮 #29；`:136` → #24｜`sprint3/audit/critic_a123_rv.md:91,101,106,109` → #22；`:114`（两套子带编号的澄清）→ #31 的横幅已注明子带率；`:122` → **第一轮漏判**，第二轮 #30；`:111` 是新标本身｜`sprint3/audit/critic_bootstrap_rv.md:29` → #23｜`sprint3/dsp/pf4/sub1_q15_stopband.md:79,115` → 排除（正确结论）｜`sprint3/pf8/PF8_retrospective.md:167` → #26。
