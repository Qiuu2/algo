reviewer: critic @ claude-fable-5-1 / 2026-09-03

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
