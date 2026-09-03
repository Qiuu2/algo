reviewer: critic @ claude-fable-5-1 / 2026-09-03
*↑注 2026-09-03：本裁定 D2-F1 中的 `--cclk-inference-accepted` 旗已按 **DEC-S7-RULINGS-03** 删除——CTO 裁定条件 0 不设旗位放行，改由测试员实测 CGU 寄存器、脚本解码重算帧预算（`s7_intake.py` v3、runbook 第 6b 步）。本文其余部分为 v2.2 当时的复审记录，保留原貌。*


# CRITIC-F 裁定（落库版）：DEC-S7-RULINGS-02 落库 + S7 板测判读方案（`S7_BOARD_RESULTS_INTAKE.md` / `s7_intake.py`）

> 独立 critic，全新上下文，只读审计（仓库零改动、零暂存、零 spawn）。三轮：首轮 → delta（v2）→ delta-2（v2.1）。
> 本文不含任何板上实测数字，也不含脚本逻辑验证所用的假回填值；场景只用文字描述。仓库自身已登记的数字（830,903 / 463,273 / 1,333,333 / 888,889 / 0x49A00000 / ldf 地址 / 8192 / 1024·1020 / 25 / 33 / 6,728·52,352）按其原出处引用。

## 0. 三轮总裁定

| 包 | 首轮 | delta（v2） | delta-2（v2.1） | 落库状态 |
|---|---|---|---|---|
| 包 1：CTO 2026-09-03 遗留裁定落库（`decisions_log.md` DEC-S7-RULINGS-02 + 6 处文档同步） | CONDITIONAL（0 BLOCKER / 2 MAJOR / 4 MINOR / 3 INFO） | **PASS**（0 / 0 / 0 / 1 INFO） | 维持 PASS | 可入库 |
| 包 2：判读方案 `sprint7/docs/S7_BOARD_RESULTS_INTAKE.md` + 宿主脚本 `sprint7/tools/s7_intake.py` | **FAIL**（1 BLOCKER / 7 MAJOR / 5 MINOR / 3 INFO） | CONDITIONAL（0 / 1 MAJOR / 2 MINOR / 3 INFO） | **PASS_WITH_MINOR**（0 / 0 / 2 MINOR / 2 INFO） | 可入库；2 MINOR 已在同一提交修：① 条件 0 的 CCLK 硬门不再受 bench FG 无效豁免；② 文档 §2.3 标题与状态行残留改正；另 bench 参考改取 `beam_cyc_min` 与板上稳态对称（delta-2 INFO） |

红线门（C1/C2/C3/C6/C7/C8/C9①②/C10、§12 FG1/FG2/IO1/IO2）终态：全部 PASS 或 N/A。首轮的 §12 FG2 BLOCKER 已在 v2 修复、v2.1 加固，delta-2 用 47 个假回填场景（PM 7 + critic 首轮 22 + delta 15 + delta-2 3）复核无一泄漏。

---

## 1. 包 1：DEC-S7-RULINGS-02 落库

CTO 原话 10 项（D6 补 / D8 / D10 补 / D13 / D14 / B1 / M2_SEG_CYC 追认 / fira_tree 内拆分 / push / 准备工作）逐条对照：全部有落点，无漏项，无替补数字（本条自述"不引新数字"属实；D10 所引 1.9dB 为既有 [L2] 出处）。

| # | 严重度 | file:line | 问题 | 修法 | 状态 |
|---|---|---|---|---|---|
| P1-F1 | MAJOR（铁律五 / LESSON-011 状态位传播） | `sprint7/docs/S7_B63_WALLCLOCK_GAP.md:30`、`:139` 行尾、`:372`；`sprint7/dsp/probe/README.md:177` | CTO 已裁"内拆分副本不必做、保持默认关"，四处仍写"待 CTO 确认 / 由 CTO 裁 / 未确认前" | 四处改为「CTO 2026-09-03 裁定不必做、保持默认关（DEC-S7-RULINGS-02）；对照 build 后仍无法归因时另行申请」 | ✓ 已修；复核 grep 只剩 `S7_PROBE_SYN_FG` 真悬置（已在 RULINGS-02 末尾登记）与 B63 §6「产品配置是否改 -O 由 CTO 裁」（本就是 CTO 事项） |
| P1-F2 | MAJOR（标签纪律，同 critic-C 先例） | `sprint2/docs/decisions_log.md` RULINGS-02 D8 / D10 / fira_tree 三行括号；`sprint7/docs/S7_POLARITY_QA_RUNBOOK.md:325`（6b） | PM 操作化与状态注混在「CTO 裁定」标签下无标；runbook 6b 整行挂 CTO D8 头却含三句 PM 处置 | 头部重申「CTO 裁定 / PM 注 / 待 CTO 裁」三标签；括号内容改「PM 注：…」；6b 拆成「CTO D8 裁定（原话）」+「PM 处置（非裁定）」 | ✓ 已修 |
| P1-F3 | MINOR | `decisions_log.md` M2_SEG_CYC 追认行 | CTO 原话"三段括号"，已入库实现为四段（含 tx） | 加 PM 注说明按 D3 扩展理解覆盖 tx，若 CTO 另有意见请明示 | ✓ 已修 |
| P1-F4 | MINOR（C5 表单 + LESSON-014 预警丢失） | `decisions_log.md` RULINGS-02 头/尾 | 缺「数据出处 / 风险声明」字段；裁完后仍悬置的 `S7_PROBE_SYN_FG` 无人接手 | 补两字段；末尾加「本条后仍待 CTO 裁：S7_PROBE_SYN_FG」 | ✓ 已修 |
| P1-F5 | MINOR（D10「引用处一律标」未全覆盖） | `sprint7/sim/acoustic/S7_ACOUSTIC_SIM_REPORT.md` §5.4 | [L2] 复算源头的结论句未加"仿真 L2，不为未落盘实测数字背书" | 结论句后加标 + DEC-S7-RULINGS-02 指针 | ✓ 已修 |
| P1-F6 | MINOR | `sprint7/tools/__pycache__/`；`.gitignore` | 多出未忽略的 pycache，工作树不是"6 改 + 2 新" | 删目录；`.gitignore` 加 `__pycache__/` | ✓ 已修；终态 `git status` = 8 改（含 `.gitignore`、acoustic report）+ 2 新 |
| P1-I1 | INFO | RULINGS-02 D8 PM 注 | 「仍不翻宏」被列为 PM 处置，其实与 CTO「不预授权翻宏」同义 | 无害，不必改 | — |

包 1 C1–C10 / §12：C1 PASS（无新数字）；C2 PASS；C3 PASS；C4 N/A；C5 PASS（字段补齐）；C6 N/A；C7 PASS（状态位传播终态干净）；C8/C9/C10 N/A；§12 N/A。

---

## 2. 包 2：判读方案 + 宿主脚本

### 2.1 CTO 四点要求落实（终态）
- §1 四批回填表统一收在一处，`--schema` 输出与 §1 逐字同源（三轮 md5 均一致）；每个空位标期望值来源（[锚] 冻结 golden 运行时解析 / [表 A] / [门] / [派生] / [凭证] / [记录]）。
- §2 决策树覆盖 CTO 点名五类：对照 build 后差距消失 / 部分缩小 / 不变（另加"未复现"与"反常"两支）；八锚任一不等（`crc_core≠锚` 链前段漂 与 `crc_core==锚 但 crc≠锚` FIRA 不 bit-exact 分开）；负控制 rc≠7（rc=0 假绿 / rc=8 比较路径坏 / 其它，且先看 NEGCTRL 指纹判 build 错）；极性接反（OPPOSITE 未改线未复测 → 一切声学测试停；恒等映射 → `M2_CHMAP_FIX` 保持关闭，D8）；三段占比不一致归因（等比 / 单段独大 = 比值最大且占比 Δ 最大同一段 / 不等比无独大）。
- §3 B1 启动条件五条（条件 0 CCLK 推断 / §2.3 有结论 / 数值门 / S-B 无 BLOCKER / 余量 ≥ 1.5×）与脚本 `b1_gate` 逐条对应；口径写死墙钟 WCET，T2 账只并列不相加。
- §4 脚本纯标准库、只读（唯一 `open()` 读 `dolph_f5_goldens.h`），退出码 0/1/2；假数据只在 scratchpad。

### 2.2 Findings（三轮合并；状态列为终态）

| # | 严重度 | file:line（首轮行号） | 问题（场景只用文字） | 修法 | 状态 |
|---|---|---|---|---|---|
| P2-F1 | **BLOCKER**（§12 FG2：作废读数仍出 PASS；文档 §2.0 自违） | `s7_intake.py` 主流程 B63.* 循环 / bench 参考 / `check_selftest` / `b1_gate`；doc §2.0 | 对照臂与 bench-P 的指纹、板门、FG 判定不回灌：A' 指纹残留或板门不绿时仍用其读数判"差距消失"并给"B1 可启动"；bench FG 不绿仍作参考；CHIRP 不在 L2 或自检帧数不满时仍报八锚 PASS | 每节维护 valid（指纹 ∧ 板门 ∧ 凭证）；差距分类、三段归因、B1 门只用 valid 节；bench 只在全绿时作参考否则明标回退历史 463,273；自检前置不过一律 `return False` | ✓ v2 修，delta 用 A' 指纹残留 / A' 板门不绿 / 缺 -O 凭证 / bench FG 不绿 / CHIRP 不在 L2 / 帧数不满 / As 指纹错 / B0 指纹误填 / scratch 落 L2 / 自检数组长度错 / B1 误带 NEGCTRL 指纹 十一类场景复核，无一泄漏 |
| P2-F2 | MAJOR | doc §2.3；`classify_gap` | "消失"只查 A'/bench，不查 A' 相对臂 0 是否真降、也不查差距是否先复现；臂 0 已与 bench 同量级且 -O 零变化时仍判"主因=优化等级" | 步骤 0 先判复现（臂 0/bench > 1+t），否则"未复现"单独成支；消失 := A'/臂 0 < 1−t ∧ A'/bench ≤ 1+t | ✓ v2 修 |
| P2-F3 | MAJOR | `classify_gap` 反常支；`b1_gate` | "反常"（-O 后更慢）被当作有结论，B1 仍可启动；doc §3 明写反常不算结论 | 反常 → `gap_class=None, anomalous=True` → B1 挂起 | ✓ v2 修 |
| P2-F4 | MAJOR（表 A 逐项不同） | INI 模板 / `FP_EXPECT` | 表 A 八行指纹漏 `selftest_negctrl_built`；B2 漏加 NEGCTRL 宏会被误判"自检假绿" | 加字段与期望（B1=0 / B2=1 / 其余 na）；rc=0 先看指纹，指纹为 0 判 build 错 | ✓ v2 修 |
| P2-F5 | MAJOR（文档称"脚本逐条实现"，实未实现） | doc §2.0.2/§2.0.3/§2.4；`check_board_gate`、bench 检查 | 未实现：三 pin 在 Block 1（0x2C0000–0x2EBFFF）、R57 判别式（`m1_max_abs_sample` 对 0x49A00000）、bench done/valid/setup_rc/frames 1024·1020/cclk/reads 25、臂 B `cproject_checked_out`、`syn_fg` 三态 | 逐项实现；§1 表补齐期望；模板加 A'' 节、`selftest_cyc_ch`、`map_seg_*`、`fa_block1` | ✓ v2 修 |
| P2-F6 | MAJOR（与已入库 B63 §6 口径不一致） | doc §2.3；`classify_gap` | B63 §6 以 `beam_min` 为稳态并先做步骤 1（min≈last≪max → max 为离群/冷帧）；方案全用 `beam_cyc_max` 且未实现步骤 1、未声明改口 | 加 `steady()`：差距分类用稳态、B1 余量用 WCET max，两口径分开写 | ✓ v2 修（稳态先取 last）→ delta 残留 D2-F2 → v2.1 改为 `beam_min` |
| P2-F7 | MAJOR（D8 唯一依据被截断） | `_clean()`；`mapping` 模板 | 值内分号被当注释截断，八路映射在报告里只剩第一路 | 模板改逗号；`_clean` 只 strip；路数 ≠ 8 → MAJOR | ✓ v2 修 |
| P2-F8 | MAJOR（C4：L3 撑强约束未挂待验） | doc 头注；`REFS`；报告头 | 帧预算的 CCLK 裸标 [L1]，丢了 B63 排查表 #15 的"M2 工程从未读 CCLK，同频为推断 [L3]" | 标签改「[L1 bench F7 读回]；M2 同频为推断 [L3]，待 `g_m2_cclk_hz` 对照」；§3 加条件 0 | ✓ v2 标签修 → 执行见 D2-F1 |
| P2-F9 | MINOR | doc §2.4；`segment_shares` | ovh 恒等式的 cyc 下限阈值无 L 标、不可调 | `--ovh-tol-frac / --ovh-tol-cyc` 标 [L4]；bench 有 `ccnt_read_cyc` 时打印 1–2 次读参考 | ✓ v2 修 |
| P2-F10 | MINOR | `attribute_segments` | 所有超容差的段都打"独大"；恒等式失败后仍归因 | 独大 = 比值最大 ∧ 占比 Δ 最大同一段；恒等式失败即返回 | ✓ v2 修 |
| P2-F11 | MINOR | scratchpad 存档 | PM 假文件输出与脚本版本不同步 | 重跑归档；§5 标脚本版本/日期 | ✓ v2 修 |
| P2-F12 | MINOR | INI 模板 | 漏收 runbook 模板字段（`selftest_cyc_ch`、`s_seg_*` 地址、第 2 遍快照、A'' 臂） | 补字段；第 2 遍写在原件（模板头注） | ✓ v2 修 |
| P2-F13 | MINOR | `b1_gate`；`polqa` | `--use-optimized-baseline` 报告行无"须 CTO 明示"；改线未复测但无 OPPOSITE 时不告警 | 报告行加提醒；`lines_changed ∧ ¬reverified` 独立 MAJOR | ✓ v2 修 |
| P2-I1 | INFO | `b1_gate` | 1.5× 线取整使"恰在线上"的基线被判可启动 | 直接比 `FRAME_BUDGET/(base+hi) ≥ 1.5` | ✓ v2 修（该场景现判刀刃） |
| P2-I2 | INFO | doc §2.3 | bench 括号内含 25 次 CCNT 读扰动而 A' 无括号，比值略偏向"消失"；量级千分位，容差覆盖 | 可打印扣除后旁注 | — |
| D2-F1 | MAJOR（§3 条件 0 未执行） | `b1_gate`；bench 检查 | bench-P 读回 CCLK 与 1e9 不符时只打 MAJOR，B1 headline 仍"可启动"且余量仍按 1e9 派生 | bench 有效且 cclk ≠ 1e9 → BLOCKER「条件 0 被 [L1] 读数否定」+ 按 bench cclk 重算一行参考 → 挂起；加 `--cclk-inference-accepted` 旗，未指定时 headline 带「待 CTO」 | ✓ v2.1 修；带旗仍 BLOCKER（旗压不过 L1 否定） |
| D2-F2 | MINOR（F6 残留） | `steady()` | 稳态取 `beam_cyc_last` 单帧样本；A' 的 last 单帧偏离 min 时分类在消失/部分缩小间翻转 | 稳态 = `beam_cyc_min`（B63 §6 定义），要求 min ≤ last ≤ max 且 last 与 min 一致 ±t，否则"稳态不可判" | ✓ v2.1 修 |
| D2-F3 | MINOR | `check_fingerprints` | 不带 SELFTEST 的 build 把 `selftest_negctrl_built` 填 0（符号实际不存在）→ 整节作废 | `selftest_built=0` 时降 MAJOR「填写不一致，按 na 处理」 | ✓ v2.1 修 |
| D2-I1 | INFO | `b1_gate` | "不变"+`--use-optimized-baseline` 仍取 A' | 仅消失/部分缩小时生效 | ✓ v2.1 修 |
| D2-I2 | INFO | `b1_gate` | 未复现或臂 0 与历史 830,903 差未解释时 headline 裸"可启动" | headline 带「待 CTO」 | ✓ v2.1 修 |
| D2-I3 | INFO | doc §2.0.3 | 三 pin 漂出 Block 1 文档措辞比脚本软 | 统一为"BLOCKER 隔离，先解释再入账" | ✓ v2.1 修 |
| D3-F1 | MINOR | 主流程 bench_cclk 传递 | 条件 0 硬门只在 bench-P 有效时取 cclk；bench FG 不绿且 CCLK 异常并存时硬门不触发（CCLK 是时钟查询，与探针 FG 无关） | 只要 `cclk_rc==0` 且已填即传入 `b1_gate`；doc §3 条件 0 加"bench FG 无效不豁免" | ✓ 同一提交修 |
| D3-F2 | MINOR（文档残留） | doc §2.3 标题；状态行 | 标题仍写稳态 `beam_cyc_last`；状态行仍"（v2）待 delta" | 改 `beam_cyc_min`；状态行改 v2.1 落库 | ✓ 同一提交修 |
| D3-I1 | INFO | doc §2.3；`classify_gap` | 板上稳态 min 与 bench 参考 last 不对称 | bench 参考改取 `beam_cyc_min` | ✓ 同一提交修 |
| D3-I2 | INFO | scratchpad 回归集 | 首轮两个边界文件因数据自相矛盾在 v2.1 被一致性检查拦住，不再测其原意 | 用数据自洽的替代文件接替，原文件改作一致性负例 | — |

### 2.3 口径与一致性核（终态）
- §2.3 划分：步骤 0 未复现（臂 0/bench ≤ 1+t）；复现后按 A'/臂 0 三分——> 1+t 反常｜|·−1| ≤ t 不变｜< 1−t → A'/bench ≤ 1+t 消失 / 否则部分缩小。三区间覆盖实数轴、互斥；边界落"不变"，doc 与脚本一致；用数据自洽的场景验证消失 / 部分缩小 / 不变 / 反常 / 未复现各落一支，无双成立、无空档。
- §3 五条件 ↔ `b1_gate`：条件 0（旗 + bench CCLK 硬门）、1（反常/无结论 → 挂起）、2（自检 ∧ 负控制）、3（S-B 三 build 无 BLOCKER）、4（直接比 ≥ 1.5）逐条对应。
- 与既有裁定：D1 墙钟 ✓；D4 B1 卡 B6.3 ✓；D8 不预授权 / 恒等保持关闭 ✓；RULINGS-02 内拆分不做（§0 与 INI 无 bench-I 节）✓；S-B 表 A ↔ `FP_EXPECT` 八行 + 可见性逐项同 ✓；表 C 八锚 ↔ 运行时解析同 ✓（c=7 == F4 锚）；极性 runbook 6b ↔ `polqa` 同 ✓；B63 §6 ↔ §2.3 口径对齐（稳态 min + 步骤 1）✓。
- 三口径：全文与脚本只用墙钟；T2 争用账只在 REFS 标签与 §3 末尾并列。
- 硬约束：冻结件 / `.cproject` / `.project` / `m1_softconfig` / `sprint4` / `sprint5` 零触碰（`git status` 对这些路径为空）；脚本只读；仓库对 scratchpad 假文件零引用；正文与脚本 grep `fake` 为 0。

### 2.4 REFS 溯源（脚本参考量，只作对照不作期望）

| 项 | 值 | L 标 | 出处 | 结论 |
|---|---|---|---|---|
| CCLK_HZ | 1e9 | [L1 bench F7 读回]；M2 同频为推断 [L3] | `sprint4/dsp/fira/F7_CLOSING_RECORDS.md`（G6 CLOSED）；`S7_B63_WALLCLOCK_GAP.md` 排查表 #15 | ✓（首轮 P2-F8 补限定） |
| FRAME / FS | 64 / 48000 | [L1 源码] | `m1_loopback_tdm.h` | ✓ |
| 帧预算 / 1.5× 线 | 1,333,333 / 888,889 | [派生] | 1e9×64/48000；÷1.5；与 B63:20、`S7_DSP_ASSESSMENT.md` §8.2 同 | ✓ |
| T2_RATIO | 1.5 | [裁定] | DEC-S4-CRITERION-01-FINAL；口径 = 墙钟（DEC-S7-RULINGS-01 D1） | ✓ |
| BEAM_HIST_MAX | 830,903 | [L1 墙钟] | DEC-S6-M2-BOARD-PASS-01 `g_m2_beam_cyc_max` | ✓ |
| F7_HIST | 463,273 | [L1 bench] | `F7_CLOSING_RECORDS.md` `g_f7_cyc_8ch_fira` | ✓ |
| B1_LO / B1_HI | 6,728 / 52,352 | [L3] / [L4] | `S7_DSP_ASSESSMENT.md` §8.1 | ✓ |
| SEG_READS_BOARD / BENCH | 33 / 25 | [L1 源码] | `m1_loopback_tdm.c` M2_SEG_CYC（4×8+1）；probe README §3 `g_s7_reads_per_frame` | ✓ |
| SELFTEST_FRAMES | 8192 | [派生] | `m1_loopback_tdm.c`（8×1024）；S-B runbook 表 C | ✓ |
| BENCH_FRAMES | 1024 / 1020 | [L1 源码] | probe README §3 | ✓ |
| HEADROOM_Q31 | 0x49A00000（−4.8 dBFS） | [L1 契约] | `tree_filterbank.h` 经 `S7_DSP_ASSESSMENT.md` §3 | ✓ |
| L2 范围 | 0x20000000–0x200F9FFF | [L1 文件] | `m1_cces_project/system/startup_ldf/m1_app.ldf` `mem_L2_bw` | ✓ |
| Block 1 范围 | 0x002C0000–0x002EBFFF | [L1 文件] | 同上 `mem_block1_bw` | ✓ |
| L1 范围 | 0x00240000–0x0039BFFF | [L1 文件] | 同上 | ✓ |
| 八锚 / F4 锚 | 运行时解析 | [L2 桌面 golden，板上比对 → L1] | `sprint4/dsp/fira/dolph_f5_goldens.h`（不复写） | ✓ |
| 默认 chmap 表 | {4,5,6,7,0,1,2,3} | [L1 源码] | `m1_loopback_tdm.c` `s_m2_chmap` | ✓ |

### 2.5 C1–C10 / §12（包 2 终态）

| 门 | 结论 | 证据 |
|---|---|---|
| C1 | PASS | 正文/脚本进入判据的数字全部带 L 标；容差类参数标 [L4] |
| C2 | PASS | 无 L2/L3/L4 被写成"实测"；报告把回填值标 [L1/EZKIT] 属实 |
| C3 | PASS | 不产生不可逆决策；脚本自述"初筛，裁定权在 CTO" |
| C4 | PASS（首轮 FAIL → v2.1 修） | M2 CCLK 同频 [L3] 推断挂待验；被 bench [L1] 否定时阻断 B1 |
| C5 | PASS | REFS 逐项溯源通过（§2.4） |
| C6 | N/A | — |
| C7 | PASS | 无撤回数字 |
| C8 | N/A | — |
| C9 | PASS | 未把任何未实测收益计入 |
| C10 | N/A | 不指导硬件动作 |
| §12 FG1 | PASS | 判据依赖被测物（八锚 / 负控制 / 指纹） |
| §12 FG2 | PASS（首轮 BLOCKER → v2 修 → v2.1 加固） | 空模板零 PASS、退出码 2；任何节指纹/板门/FG 不符即作废且不进入结论；47 场景无泄漏 |
| §12 IO1 / IO2 / ST1 | N/A | 无固件改动 |

### 2.6 实跑清单（场景名 → 分类；数值一律不列）

- `--schema` 与文档 §1：三轮均逐字同源（首轮、v2、v2.1 各一次 md5 比对）。
- PM 假文件 7 个：全绿+消失+极性恒等 → 0 BLOCKER、B1 可启动（待 CTO）；不变+ana 独大 → 不变、B1 按臂 0；自检 `crc_core≠锚` → BLOCKER 链前段漂、B1 挂起；负控制 rc=0（指纹在）→ BLOCKER 假绿、B1 挂起；极性 OPPOSITE 未改线 → BLOCKER 声学停、不影响 B1；B0 指纹残留 → BLOCKER 作废、差距不可判、B1 挂起；空模板 → 零 PASS、退出码 2。
- critic 首轮边界 22 个（含 lead 补的 NEGCTRL 指纹=0 变体）：差距未复现 → 未复现（待 CTO 裁新基线）；-O 后更慢 → 反常、B1 挂起；负控制 rc=8 / rc=其它 → BLOCKER 自检不可信；自检帧数不满 / CHIRP 不在 L2 → 自检作废、B1 挂起；A' 缺 -O 凭证 / A' 指纹残留 / A' 板门不绿 → A' 无效、差距不可判、B1 挂起；部分缩小 → 部分缩小；两条件同时成立 → 消失；A'/臂 0 落在不变带内 → 不变；基线恰在线上 → 刀刃；bench FG 不绿 → bench 无效、参考明标回退历史 F7；B2 漏 NEGCTRL 宏（指纹=0）→ 指纹不符 build 错、零次假绿；rc≠0 但 crc 全等锚 → 判据逻辑异常；FIRA 不 bit-exact（`crc_core==锚`）→ BLOCKER 定位通道与首失配子带；恒等式不成立 → 占比不入账不归因；rx≉poll / overrun 涨 → 板门 BLOCKER；改线未复测 → MAJOR。
- delta 边界 15 个：A' last 单帧偏离 min → 稳态不可判、B1 挂起；As 指纹错且三段填满 → As 作废、归因回退 SB.B1；As 有效 → 归因取 As；B0 负控制指纹误填 → MAJOR 填写不一致、不作废；A' 只填凭证 → 不可判；bench 读回 CCLK 与 1e9 不符 → BLOCKER 条件 0、B1 挂起（带 `--cclk-inference-accepted` 旗仍同）；臂 B 缺 checkout → MAJOR 不入账；映射非八路 → MAJOR；bench 帧数不符 → bench 无效回退；自检数组长度错 → 不可判；B0 max 为冷帧且稳态与 bench 同量级 → 未复现 + 步骤 1 离群提示；scratch 落 L2 → 板门 BLOCKER；B1 误带 NEGCTRL 指纹 → 作废；不变 + `--use-optimized-baseline` → 退回臂 0。
- delta-2 边界 3 个：数据自洽的"两条件同时成立" → 消失；数据自洽的"不变带内" → 不变；bench FG 不绿且 CCLK 异常并存 → 硬门未触发（D3-F1，已修）。
- 旗组合：`--cclk-inference-accepted` → headline 去掉「待 CTO」；`--use-optimized-baseline` 在消失/部分缩小取 A' 并注明须 CTO 采纳，在不变/未复现退回臂 0。
- 回归：44 个场景在 v2.1 上与 lead 存档逐字同；无 fake 引用进仓库；冻结件零触碰。

---

## 3. 声明

完整裁定（含每个假回填场景的具体数值、脚本运行日志、逐条 diff）仅存本会话 scratchpad（`critic_F_verdict.md`、`critic_F/`、`critic_F_v2/`、`intake_fake/`、`reg_*.md`），**未入库**；本文为去数值的落库版。三轮 reviewer 标：critic @ claude-fable-5-1 / 2026-09-03。

---

## Delta-3 / Delta-4 / Delta-5 复审（DEC-S7-RULINGS-03 落库 + B1 条件 0 实测 CCLK 读法 + `s7_intake.py` v3 → v3.1 → v3.2）

reviewer: critic @ claude-fable-5-1 / 2026-09-03（delta-3 → delta-5）

> 只读审计；仓库零改动、零 spawn。本段不含任何板上实测数字，也不含脚本验证所用的假回填值；出现的数值全部是 CCES 2.12.1 头文件/电源服务源码、ADI 配置头、HRM、数据手册、核心板原理图的原值。

### 轨迹

| 轮 | 对象 | 裁定 | 要点 |
|---|---|---|---|
| delta-3 | RULINGS-03 落库 + runbook 第 6b 步/表 D + 脚本 v3 | **FAIL**（1 BLOCKER / 0 MAJOR / 3 MINOR / 4 INFO） | 落库、传播、零改码读法、寄存器地址与位域、回灌门全对；**解码公式的 ÷2 不属于 ADSP-21569**（C2/C5） |
| delta-4 | 脚本 v3.1 + 文档/runbook/log 同步 | **CONDITIONAL**（0 BLOCKER / 1 MAJOR / 1 MINOR / 3 INFO） | BLOCKER 与三条 MINOR 全部确认修复；剩一个 MAJOR：解码值无物理合理性门（CSEL 抄错一位即放行 B1） |
| delta-5 | 脚本 v3.2（三道数据手册门）+ 文档/log 同步 | **PASS_WITH_MINOR**（0 BLOCKER / 0 MAJOR / 2 MINOR / 2 INFO） | 三门值全对、边界含等号、合法配置无假阴；MINOR = 两处数据手册表号引错 + 一句残留措辞，同一提交顺手修，可落库 |

### 出处核（PM 点名的六项，终态）

| # | 项 | 核到的出处 | 结论 |
|---|---|---|---|
| 1 | 寄存器地址 | `CCES 2.12.1 SHARC/include/sys/ADSP_2156x_HPC.h:13186/13188/13189`：`REG_CGU0_CTL 0x3108D000`、`REG_CGU0_STAT 0x3108D008`、`REG_CGU0_DIV 0x3108D00C`；`SHARC/include/def21569.h:26` `#include <sys/ADSP_2156x_HPC.h>`（def21565.h 才是 LPC）；LPC 头三地址相同 | ✓（delta-3 指出路径应为 `include/def21569.h:26`，delta-4 已改） |
| 2 | 位域 | 同头文件 `:13213/:13223` MSEL bit8..14（0x7F00）、`:13214/:13224` DF bit0、`:13293/:13311` CSEL bit0..4（0x1F）、`:13257/:13258` PLLBP bit1 / PLLEN bit0（另有 `:13278` PLOCK bit2） | ✓ |
| 3 | 公式 | **HRM**（`knowledge_base/ezkit/bsp/hw_reference/ADSP-21569 … Hardware Reference.pdf`，CGU_CTL.MSEL / CGU_DIV.CSEL 描述）：`PLLCLK = (SYS_CLKIN/(DF+1)) × MSEL`；`CCLK = PLLCLK / CSEL`；MSEL 字段 0 = 128；CSEL 字段 0 = 32；DF=1 = CLKIN/2 进 PLL。**ADI 电源服务源码** `CCES 2.12.1 SHARC/lib/src/services/Source/pwr/adi_pwr_2156x.c:741-800`（`adi_pwr_GetCoreClkFreq`，即 bench F7 读回 1e9 的函数）：PLLEN=0 或 PLLBP=1 → CCLK = CLKIN；msel 0→128、csel 0→32；**`#if defined(__ADSP21568_FAMILY__)` 才 `clkin*msel/2`，`#else`（含 `__ADSP21569_FAMILY__`）`(clkin/(df+1))*msel`，再 `/csel`**。`adi_pwr_v2.c:375-378` 同，无 ÷2。**ADSP-21569 家族四份 ADI 配置头**（`SHARC/ldr/init_code/2156x_Init/21569_init/src/adi_pwr_21569_family_1GHz_config.h` 等）：SYS_CLKIN0 25 MHz；1 GHz = MSEL 80 / DF 0 / CSEL 2；800 MHz = 64 / 2；600 MHz = 72 / 3；400 MHz = 48 / 3，与无 ÷2 公式逐一精确相等。PM delta-3 初稿交叉验证所用 `adi_pwr_2156x_800MHz/933MHz_config_BGA.h` 文件头写明 "BGA **ADSP-21568** family parts"（24.576 MHz），只对 21568 分支成立；初稿"第三组 MSEL 80、CSEL 1"不是任何 ADI 配置 | delta-3 ✗ → delta-4 ✓：v3.1 起采用 `fPLL = (CLKIN/(DF+1)) × MSEL`、`CCLK = fPLL / CSEL`，整数除法次序与源码同；字段 0 取 128/32；DF 项按源码解码 |
| 4 | CLKIN 出处 | `m1_main.c:44 adi_pwr_Init(0, 25*1000000)` 是软件实参，单独不够 L1（PM 的疑虑成立）。KB 内**核心板原理图** `knowledge_base/ezkit/vendor_docs/schematics/V2.1/ADSP21569核心板原理图.pdf`（V1.0/V1.2 同）：25 MHz 振荡器直连 SYS_CLKIN0；21569 家族 ADI 配置头 SYS_CLKIN0 = 25 MHz；bench F7 读回值与之自洽 | delta-4 ✓：REFS、doc §1、runbook 表 D、INI 注释均改标「[L1 文件：核心板原理图 V2.1]」并给 KB 路径 |
| 5 | 零改码 | runbook 第 6b 步：Suspend 下 Register/Memory 视图只读，"只读不写；不要改任何寄存器值"，不加代码、不 build；§6 红线不变；表 D 只抄原值 | ✓ |
| 6 | 回灌与门 | `[CLK]` 缺项/格式错 → 不可判 → B1 挂起（退出码 2）；PLLEN=0 或 PLLBP=1 → MAJOR 且条件 0 不放行；字段 0 → info 代入最大值；CLKIN / fPLL / CCLK 任一越出数据手册范围 → 不可判、不标 [L1]；解码值 ≠ bench 读回 → BLOCKER 挂起；bench 时钟读数不受 FG 有效性豁免；条件 0 未满足时无任何路径输出"可启动" | delta-5 ✓ |

### 三道合理性门（delta-5 核）

| 门 | 值 | 数据手册出处（`ADSP-2156x-Datasheet-EN.pdf` Rev.C 2022-11） | 边界核（数据自洽的合法配置） |
|---|---|---|---|
| fCCLK | 400–1000 MHz | **Table 19** Clock Operating Conditions（1000 MHz 为 1 GHz 档上限） | 400 MHz 配置（MSEL 48 / CSEL 3，恰在下限）通过；1 GHz 配置（恰在上限）通过；CSEL 抄成 1（解出 2 GHz）与 CSEL 8（250 MHz）均拦 |
| fPLLCLK | 1.20–2.00 GHz | **Table 20** Phase-Locked Loop (PLL) Operating Conditions（p.45）——PM 引为 Table 19，表号错（MINOR） | 1 GHz 配置 fPLL 恰 2.0 GHz 通过；400 MHz 配置与 DF=1/MSEL 96 配置 fPLL 恰 1.2 GHz 通过；DF=1 且 MSEL 0→128、CSEL 2（fPLL 1.6 GHz、CCLK 800 MHz）通过；DF=1/MSEL 80/CSEL 1（fPLL 1.0 GHz）拦——该配置本身不合规 |
| fCKIN（SYS_CLKIN0） | 20–30 MHz | **Table 33** Clock and Reset Timing（晶振/外部）——PM 引为 Table 19，表号错（MINOR） | 恰 20 MHz、恰 30 MHz 通过；低于 20 MHz 一赫兹即拦；DF=1 时门查分频前的 CLKIN（正确） |

结论：边界含等号，合法但少见的配置（DF=1 大 MSEL）不被误拦；无假阴。

### Findings（三轮合并；状态为终态）

| # | 严重度 | file:line | 问题（场景只用文字） | 修法 | 状态 |
|---|---|---|---|---|---|
| D4-F1 | **BLOCKER**（C5 交叉核对象是另一家族；C2 把只对 21568 成立的公式写成"[L1 工具链] 两组交叉验证"；条件 0 唯一依据错） | `s7_intake.py` 公式注释与解码行；doc 头注、§2.6；log RULINGS-03 PM 注；runbook 表 D 注 | 以 21569 1 GHz 配置头的真实寄存器值（MSEL 80、DF 0、CSEL 2）代入 v3 公式解出真值的一半：有 bench → 假告警「两工程不同频」；无 bench → 按减半预算假告警「触发冻结令解冻条件」 | 去 ÷2；字段 0 → 128/32；PLLEN=0 视同旁路；DF 按源码；出处改 HRM + `adi_pwr_2156x.c` 家族条件编译原文 + 21569 四份配置头；log/doc/runbook/脚本按铁律五同步 | ✓ delta-4 已修：四锚代入逐一相等；真 1 GHz 寄存器值有/无 bench 均解出 1e9、条件 0 满足、B1 按 1,333,333 / 888,889 判；21568 两份头按新公式不吻合（证明没再混锚）；log 内嵌「PM 注更正」（声明 + 反扫 + 删旧公式三步齐，铁律五满足）；sprint7 与 log 内 ÷2/21568 锚 grep 清零 |
| D4-F2 | MINOR | `decode_cclk` | PLLEN 只打印不判；ADI 源码把 PLLEN=0 与旁路同等处理 | 与 PLLBP 同支 | ✓ delta-4 已修（MAJOR 正确） |
| D4-F3 | MINOR（L 标） | REFS CLKIN；runbook 表 D；doc §1 | CLKIN 标「[L1 源码] 实参」；原理图在 KB 却未引 | 改标原理图 | ✓ delta-4 已修 |
| D4-F4 | MINOR（出处路径） | log PM 注；doc 头注 | `sys/def21569.h:26` 应为 `include/def21569.h:26` | 改路径 | ✓ delta-4 已修 |
| D5-F1 | **MAJOR**（由 delta-3 INFO 升级；§12 FG 升级义务：存在性绿、率不在带） | `decode_cclk`；doc §2.6 | 公式改正后，CSEL 抄错一位即解出真值两倍，脚本仍标 [L1] 并放行条件 0；无 bench 时帧预算翻倍、B1「可启动」——错误方向宽松 | 按数据手册 fCKIN / fPLLCLK / fCCLK 三道门：越界 → 不可判、不标 [L1]、条件 0 未满足 | ✓ delta-5 已修（边界核见上表） |
| D5-F2 | MINOR | doc §2.6 第 1 行 | 与同表 PLLEN 行、字段 0 行矛盾 | 改「PLLEN=1 且 PLLBP=0、三门全过」 | ✓ delta-5 已修 |
| D6-F1 | MINOR（C5 出处表号） | `s7_intake.py` REFS `FPLL_*`/`CLKIN_*`；doc 头注/§2.6；log PM 注 | fPLLCLK 门引为 Table 19，实为 Table 20；fCKIN 门引为 Table 19，实为 Table 33；值全对 | 三处改表号 | 待修（同一提交顺手） |
| D6-F2 | MINOR（残留措辞） | doc §3 条件 0 行 | 「PLL 旁路与字段 0 照常解码」与 §2.6（旁路 → MAJOR 且不放行）矛盾 | 改「字段 0 照常解码；PLL 未使能/旁路 → MAJOR 且不放行」 | 待修（同一提交顺手） |
| D4-I1 / D5-I2 | INFO | `decode_cclk` / `check_bench` / `b1_gate` | 解码 ≠ bench 一个根因打三条 | 旁路提前返回后已自然合并 | ✓ |
| D4-I2 | INFO | `b1_gate` | 无 bench 时条件 0 由解码单独满足（CTO 原话允许）；加三道门后可接受 | — | — |
| D6-I1 | INFO | log PM 注；doc §2.6 | "PLL 旁路 → 条件 0 未满足"是 PM 操作化（CTO 原话只说未实测），已标 PM 注并给理由，方向保守，不越权 | 措辞区分「CTO：未实测 → 未满足」与「PM 处置：实测显示超规 → 亦不放行」 | — |
| D5-I1 / D5-I3 / D6-I2 | INFO | INI 注释；`sprint7/critic/CRITIC_F_INTAKE_20260903.md` ↑注；scratchpad 归档 | INI 注释已改引原理图（D5-I1 ✓）；↑注"v2.2/v3"用词；旧场景归档未随 v3.2 重跑 | 顺手统一；重跑归档（仅 scratchpad） | — |

### 其余核对（三轮全过）
- DEC-S7-RULINGS-03 三条 CTO 原话逐字落库；PM 注全部带标签；对 IMPL-01 PM 注 2、RULINGS-02 SEG_CYC 行与悬置项的三处 ↑注有日期、有依据、原文保留。
- 铁律五：sprint7 内旧的待裁措辞与旗位名清零；B63 §2.5/§7/排查表 #15、probe README §1/§6c 已按"裁定不必做 + 重开条件（合成段占比不可归因分歧）"改写；delta-3 错公式的更正声明 + 反扫 + 删旧三步齐。
- `--schema` 与文档 §1 逐字同源（含 `[CLK]` 节；v3.2 因 INI 注释改引原理图 md5 变一次，两边仍同）；lead 的时钟场景（delta-3 七个、delta-4 六个、delta-5 五个）我逐轮重跑与存档逐字同（v3.2 下早期归档为旧版输出，行为正确但需重跑归档）；既有 45 个回归场景在 v3/v3.1/v3.2 下一律"条件 0 未满足 → B1 挂起"，是 CTO 裁定的预期后果而非回归；我另造 15 个条件 0 边界（delta-3）+ 10 个门限边界（delta-5）各落对应支。
- 硬约束：冻结件零触碰；脚本只读；正文/脚本无假数据；工作树 7 改（含落库版裁定文件的 ↑注）。

### C1–C10 / §12（delta-5 终态）
C1 PASS；C2 PASS（delta-3 FAIL → 出处主张改为源码 + 21569 四锚，属实）；C3 PASS；C4 PASS（条件 0 改实测，L3 推断退出）；C5 PASS_WITH_MINOR（delta-3 FAIL → 交叉核对象正确；三门值对，两处表号错）；C6/C8/C9/C10 N/A；C7 PASS（更正三步齐）；§12 FG1 PASS、FG2 PASS（缺失/作废读数零 PASS 泄漏）、FG 率在带 PASS（delta-4 MAJOR → delta-5 三门已修）；IO1/IO2/ST1 N/A。

完整裁定（含每个场景的具体数值与运行日志）仅存会话 scratchpad，未入库。

*PM 注 2026-09-03（delta-5 后）：delta-5 的两条 MINOR 已在同一提交修完 —— ① 三个门限的表号改正为 Table 19（fCCLK）/ Table 20（fPLLCLK）/ Table 33（fCKIN）；② §3 条件 0 措辞与 §2.6 对齐（PLL 未使能/旁路、解出值越门 → 同样不放行）。另修一处退出码一致性：旁路分支原先只打 MAJOR，报告说“条件 0 未满足、B1 挂起”而退出码为 0，现已计入“不可判”（脚本 v3.3）。*
