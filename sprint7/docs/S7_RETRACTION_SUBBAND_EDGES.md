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
