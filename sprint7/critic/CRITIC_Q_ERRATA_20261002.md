> **公开版（2026-10-02）**：本文件收录独立 critic 对 2026-10-02 修正包与手册摘录包的评审报告（第 1 轮 + 第 2、3 轮 delta）。按手册摘录包同一规则脱敏：另一项目的名称、性质和本机压缩包文件名改为中性措辞，其余逐字。原件只保存在 PM 会话的临时目录。

<!-- 第 1 轮：CRITIC_Q_R1.md -->

# CRITIC_Q_R1 — 2026-10-02 修正包（包 1）+ 手册摘录包（包 2）独立评审

reviewer: critic @ claude-opus-5-5 / 2026-10-02

> 性质：只读对抗式评审。未改仓库、未改记忆目录、未做任何改状态的 git 操作、未派子代理、未联网。
> 依据：`.claude/skills/critic/SKILL.md` §11（C1–C10）/§12、`CLAUDE.md` 铁律 1–9（重点铁律五：声明 + 全库反扫 + 就地加标，原文不改）。

---

## 0. 结论速览

| 包 | 裁定 | BLOCKER | MAJOR | MINOR | INFO |
|---|---|---|---|---|---|
| 包 1 修正包（15 个仓库文件 + 自动记忆目录；含 lead 晚到的 PRD §7.3 注与 decisions_log:739 注，见 §7） | **FAIL** | 2（C7、C1） | 9 | 14 | 6 |
| 包 2 手册摘录（`knowledge_base/manual_sources/`，11 个文件） | **CONDITIONAL** | 0 | 1 | 4 | 5 |

包 1 被打回的原因有两条，修起来都只是追加标注和改记忆文字，不需要返工：

1. **C7 撤回传播仍有残留（BLOCKER）**。本包的目的是补齐 DEC-S7-RETRACT-SUBBAND-01 的反扫，但按机制关键词复扫后，仍有至少 9 组依赖"子带可分别加权/延时"或依赖已撤回边界标签的位置没有加标。其中两处（`NEXT_SESSION_BOOTSTRAP.md:66`、`critic_a123_rv.md:122`）就在 PM 自己的命中清单 `premise_hits.txt` 里，既没加标，也没列入"不需加标"。另有一处派生数会让结论翻转：变体 b"只聚焦 sb2+sb3 覆盖 ≥4 kHz → 1.510×"是按被撤回标签算的，按真实分界约为 1.495× [L3]，从"勉强在线上"变成"越线"。
2. **C1 标签缺失（BLOCKER）**。14 处新加勘误标重述了冻结树的 [L2 host] 事实（3k/6k/12k、≤2.5k 0 dB、SB0 通带），其中 12 处漏了登记 §3 统一标签要求的 `[L2 host 复算]`，包括规格文件 `prd_update.md:135`。这和登记 §6"按 §3 的统一标签补标"的自述不符。

主要的 MAJOR（写进记忆的问题，每个会话都会读到）：

- `dsp-chip-decision.md:21` 把"板上实际约 30–50 cycle/MAC"当通用事实写。DEC-S5-BUDGET-L1-01 对 FIR 核的实测是 8.51 cyc/MAC，并已把 173–288 作为"错 cyc/MAC 类"退役。
- `sprint3-d55-baseline.md:18` 写"SPLo 82.161 dB [L1 单只]……两者口径不同、勿直比"。这与 KB-DRV-TEST-001 §3a（约 5.8 dB 冲突，铁律四类）和 SPL_REDO（绝对电平为 L2、条件未定）不一致。
- `directivity-band-requirement.md` 写"S7 红线 BW@1k ≤30°"和"500 Hz 不要求"，与 PRD v2.5、D6 重开以及 JY/T 二级保底中的 500 Hz 两点相冲突。
- `S7_VERIFICATION_PLAN.md:219` 的"BW@1k ≤30° 是红线"没有标出，而本包刚在 §5 横幅（:213）里声明"全频段单表流程保留"，两者自相矛盾。
- 评审期间文件仍在变（diff 从 +87 变成 +92），所以门必须落在冻结快照上。

包 2 的公开仓库安全面基本干净：邮箱和 Windows 用户名已去掉，T24 的 8 行时间线和主题块已抹掉内容，没有 IP 片段、凭据，也没有产品参数分类分支的内容。问题在于 `prompts_crosscheck_〈旧文件名，含另一项目名，已更名为 other_project〉.md` 超出了"只列日期和会话"：写了另一项目的性质、本机目录名，还引用了一条无关提示词原话。这与 README:34 的自述和 CTO 要求不符，提交到公开仓库前必须改掉。

---

## 1. 评审对象与快照

- 快照时间：2026-10-02 20:03。`git diff --stat`：15 files, +92 / −11。`git diff | md5sum` = `2b158f5c77bd0eea2374f8f78c98937a`。
- **评审期间包 1 仍在被修改**。按 mtime，`prd_update.md` 在 19:41:55、`decisions_log.md` 在 19:42:19、`S7_RETRACTION_SUBBAND_EDGES.md` 在 19:42:30 改过，都晚于本评审开始的约 19:37。diff 由任务书写的 +87 变成 +92，新增了 `decisions_log.md:739-740` 的 ↑注、`prd_update.md:359` 的 §7.3 注、表头修改和登记 #28。本报告以上述快照为准，快照之后的任何改动都需要 delta 复审。
- 记忆文件 md5 前 8 位：MEMORY 54a88755｜dsp-chip 87fcd636｜gate1 df707bee｜sprint2 0dc8bac9｜sprint3-d55 02441eed｜steering 16dac478｜m2 4d1ed386｜agent-team-ops 857ab89c｜directivity 0e354292。
- 包 2 文件 md5 前 8 位：README aff06ec7｜crosscheck d0e89f1b｜digest_A 0ad56eec｜B ad064058｜C 655acef4｜D b9917a48｜E 4f6ca928｜F 38d20de6｜G f2f91a59｜H c51fa0b6｜I 14f7b351。

---

## 2. 包 1 门表（C1–C10）

| 门 | 结论 | 证据（一行） |
|---|---|---|
| C1 | **FAIL（BLOCKER）** | 14 处重述冻结树 [L2 host] 数字的新标里，12 处没有 `[L2 host 复算]`，其中包括规格 `prd_update.md:135`（"实际分界 3k/6k/12k…≤2.5k 为 0 dB"）和日志 `decisions_log.md:739` 第②条。另外 :739 和 `prd_update.md:359` 里的 0.92×/2.878× 只靠上下文"板上 [L1] 推翻"带出标签（MINOR，见 P1-m2） |
| C2 | PASS | 没有 L2/L3/L4 被写成"实测/measured"。记忆里有措辞过度的地方（P1-M3/M4），但不触红线词 |
| C3 | PASS | 本包不涉及任何不可逆决策 |
| C4 | PASS | 没有用 L3 支撑新的强约束 |
| C5 | **FAIL（MAJOR）** | `sprint3-d55-baseline.md:18`"两者口径不同、勿直比"没有出处，且与 KB-DRV-TEST-001_extracted.md:79-85 相反；`dsp-chip-decision.md:15`"06-01 到货"仓内无出处，只见于提示词史 digest_I:589；`dsp-chip-decision.md:21` 的 30–50 cyc/MAC 把适用范围外推了 |
| C6 | PASS | 没有改几何。d=55 [L1]、d=30 [L0] 的表述正确 |
| C7 | **FAIL（BLOCKER）** | 见 §3.2：残留 R-1…R-9，包括对外交付物目录 `deliverables/…/EXP_COMPET_BEAM_VS_FREQ.md` 和一个会让结论翻转的派生数（R-6）。记忆里"撤回传播已做"的表述依然存在（P1-M6） |
| C8 | N/A | 没有外部输入入库 |
| C9 | PASS | RELEASED 体制：官方锁 3.07×，3.13× 只以"已退役"出现。log/PRD 的注里连体了分母（43–379 MCPS）；有几处没连体，属 MINOR（P1-m3） |
| C10 | N/A | 不涉及硬件动作 |

红线：C1、C7 FAIL ⇒ **包 1 整体 BLOCKER，打回**。

---

## 3. 包 1 逐项核查

### 3.1 数字保真（任务 1）— 转录全部正确，问题出在外推和标签

| 数字 | 源（当前工作树行号） | 结果 |
|---|---|---|
| 1,006,935 cyc → 1.32×（按 1 GHz） | decisions_log:608 DEC-S4-R1-8CH-01（2026-06-03）；:234 R1 行 | 一致 |
| 1,451,030 → 0.92×（产品核路径） | :754-755, :765 DEC-S4-F7-CLOSE-01（2026-06-04） | 一致 |
| 463,273 → 2.878× [L1-derived]；3.07×（1,420,543/463,273）；3.13× 退役 | :756, :761-764 | 一致 |
| CCLK 1e9 [L1]（G6 CLOSED） | :759 | 一致 |
| 43–379 MCPS 未计入清单 | :631, :800-801 DEC-S4-C9-RELEASE-01 | 一致 |
| 49.03 MCPS = 65,371 cyc ×750/1e6；残余 1.46–2.14× [L4] | :717 DEC-S5-BUDGET-L1-01（2026-06-05） | 一致（本 critic 复算 49.028） |
| 830,903 = 帧 62.3%（余量 1.60×）；1.79×/1.83× | D12 注 :1018（2026-09-02） | 一致（复算 1.6047 / 1.7935 / 1.8272） |
| 高估约 25×；30–50 cycle/MAC | :234 R1 行 | 一致。但 :234 指的是**树形核整路径**的折合值，记忆把它写成了通用值（P1-M3） |
| L/λ 0.60/1.20/1.80/2.41；fc(10°)=5314 Hz；1.488× | 提案 :127、:101、:188 | 一致（复算 0.60/1.20/1.80/2.41、5313.7 Hz、1.4876） |
| DEC ID 与日期 | S1-004、S3-PROC-01（05-28）、S3-GEOM-01（05-29）、S4-*（06-03/04）、S5-*（06-05/06）、S6-GOVERNANCE-SLIM-01/04（07-19/07-20）、S7-IMPL-01（09-02；第 1 项 09-03 落库 e773399）、S7-SIDE30-01、S7-RETRACT-SUBBAND-01（09-26） | 全部存在，日期一致 |

### 3.2 撤回加标（任务 2）

**分级是否正确，有没有过度作废（越权）**：没有发现越权。B4 的逐频率物理边界数字（1k 29.3°→22.7°、30° 衰减到 13 dB、L/λ、WNG）在提案 :31 和验证计划 :183 都被正确**保留**。critic_a123_rv:111 保留了 29.27°/28.78 dB/15.93° 这几个单频阵因子数字；dsp_8ch_report:47 保留了 6.2–8 kHz 栅瓣结论；PRD 的二级保底承诺被声明不受影响。这些都与登记 §2 一致。原文未改：全 diff 的删除行只出现在两份文件的表头和页脚。冻结件未动：没有 .c/.h 改动。critic memory 的 9 个 yaml 块改前改后都能用 `yaml.safe_load` 解析。

**D6 表述**：总体正确。CTO 同意重开 D6、允许换更深的全频段单表；"接受 1k >30°/BW 线降为工程参考"是 PM 拟、待 CTO 过目。但有三处瑕疵：
(a) 提案 :31 把"因此接受 1k 波束 >30°"加了引号当原话，而日志 ② 的 PM 拟原文是"重开 D6 即接受更深的表带来 1k 波束 >30°，因此'BW@1k ≤ 30°'内部线降为工程参考"（P1-m5）；
(b) PRD 新表头 :4 把"'BW@1k ≤30°'内部线降为工程参考"列为 v2.5 内容，没有"PM 拟、待 CTO 过目"限定（P1-m5）；
(c) 验证计划 §5.1 :219"BW@1k ≤30° 是红线"没有加标（P1-M1）。

**本 critic 的独立复扫**：按机制关键词扫全部 tracked 文本，不限 *.md，关键词包括 `每子带|逐子带|子带级|子带内|子带权重|子带加权|子带延时|子带独立|独立加权|子带标量|SB2 单独|恒定波束宽|per-subband|subband 值得|FIB|超指向+SB0/SB1|500-1k/1k-2k…`，另外核对了派生数。下表是**残留且必须处理**的位置：

| # | 文件:行（当前工作树） | 依赖什么 | 建议级别 |
|---|---|---|---|
| R-1 | `sprint3/audit/NEXT_SESSION_BOOTSTRAP.md:66` | 触发 E 的任务④"否则启用子带标量加深 A3 选项1.5 零成本"，是**可执行指令**；同行②"R5 裁超指向去留"见 R-7。本行在 PM 的 premise_hits.txt 中命中，但既没加标也没列入排除 | 作废 |
| R-2 | `sprint3/audit/critic_a123_rv.md:122`（及 :124） | §5"选项 1.5 … ✓ 成立：1.5 零成本达标"，:124"FIB 价值定位 … ✓"。:111 的标只覆盖其上方的 §4.2；本行同样在 premise_hits.txt 里 | 作废 |
| R-3 | `sprint3/audit/A2_fib_feasibility.md:21`（§0"可作为 Sprint 4 候选"）、:60-75（§2.2/§2.3 FIB 结果）、:85-89（§3"2k 子带 90° 28.78dB ✓"）、:106-128（§4 FIR 长度、算力、延迟，含 :123"SB0 是 0.5-1k 宽波束"）、:147（§5 结论） | :44 的标写的是"本节两层方案"，只覆盖 §1.2。建议改成文首横幅并列出受影响各节 | 作废（§4 子带率另属标签错） |
| R-4 | `sprint3/audit/SPRINT3_DESKTOP_CLOSURE.md:57` | "Sprint 4 战略储备：FIB（A2 桌面预研就绪）" | 作废 |
| R-5 | `deliverables/algorithm_validation/EXP_COMPET_BEAM_VS_FREQ.md:5`、:62、:68③、:82 | "可用 subband 匹配"、"subband **值得做**（交付的是均匀性）"，即 B5-2 的前提。位于 C7 点名的**对外交付物**目录。本包在验证计划 :183 的新标里自己引用了这句话（"子带处理交付的是覆盖均匀…同样做不到"），却没去源头加标 | 作废（前提） |
| R-6 ★ | `sprint7/docs/S7_DSP_ASSESSMENT.md:184`；`sprint7/docs/S7_ALGO_UPGRADE_PROPOSAL.md:101` | 变体 b"只聚焦 sb2+sb3（**≥3 kHz 标称**，覆盖 v1 ≥4 kHz）6,144 MAC / 52,297 cyc / 1.510×"。"sb2 ≥3 kHz"正是被撤回的 1.5k/3k/6k 标签的派生。真实树中 4–6 kHz 落在 SB1（3–6k），要覆盖 ≥4k 需要 SB1+SB2+SB3 = 112 samp/帧，即 7,168 MAC → 约 61,013 cyc → 墙钟余量约 **1.495×** [L3，本 critic 按 8.51 cyc/MAC 线性缩放，与原行同法，待第二工具核]。结论因此由"勉强在线上"变成"越线"。而且 detail 带是梳状残差，"只聚焦高频子带"这个概念本身也待核。另外，`S7_DSP_ASSESSMENT.md:2` 的横幅写着"其余（算力台账、B1/B2/B6 等）不受此影响"，这句话对变体 b 是错的 | 作废/待核 |
| R-7 | `sprint2/docs/decisions_log.md:238`（R5 行）、:294-306（DEC-S2-013：增量延迟"SB0≈5.3/SB1≈2.7ms"，即按子带实现）、:404-425（DEC-S3-DSP-06"实测超 30° → 启用超指向"）；`sprint2/acoustic/1khz_optimization.md:122`（SB0 16ch×32tap）；`NEXT_SESSION_BOOTSTRAP.md:66`②；记忆 `sprint3-d55-baseline.md:24`"留兜底" | 1 kHz 超指向兜底的实现路径是子带级（SB0/SB1），与已作废的 S7 B4"低频子带差异化权重/超指向"是同一机制。冻结树上没有现成实现路径，只能走 DEC-S7-SIDE30-01 ③ 的每通道滤波器 | 待核 |
| R-8 | 设计标签"500-1k/1k-2k/2k-4k/4k-8k"：`prd_update.md:23`（§0"锁定值（当前生效）"表）、:200（§3.3 规格"…｜CCES 代码实现确认"）；`sprint4/dsp_migration_inventory.md:13-14`（迁移基线把设计表当成冻结树；同表 :15 写"3 级 dyadic 树"，但又列 SB0 16× 抽取，3 级树最多 8×，自相矛盾）；`sprint2/docs/PROJECT_HANDOVER.md:93`；`decisions_log.md:91`（DEC-S2-002）、:196（DEC-S2-009，LOCKED） | 本包在 #24/#25/#28 已把**同一标签**定为"标签错（设计意图 ≠ 冻结树实际行为）"，却只标了 3 处。冻结树实际子带率是 6/12/24/48 kHz（sz[]=8/16/32/64），设计表是 3/6/12/24 kHz | 标签错（并见 P1-M2 升级） |
| R-9 | `prd_update.md:421` | 新补注写"正文虽没有直接写边界数字"，与 :23、:200 不符 | 改正补注 |

**可以不加标、但应写进登记 §6 排除清单并注明理由**（理由：属于 Sprint 2 设计史或成本替身，按 06-04 CTO 令"历史按写时为真"处理）：`sprint2/SPRINT2_CTO_REPORT.md:39,44-46`、`sprint2/dsp/dsp_design.md:61,121`、`sprint2/dsp/budget_calc.py:30,64`、`sprint2/dsp/cces_template/src/beamformer.h:41`、`sprint2/docs/sprint3_kickoff_checklist.md:15`、`decisions_log.md:50`、`sprint2/patent/patent_map.md:58,230-238`、`sprint2/patent/formulas.md:306`、`sprint3/audit/A2_fib_feasibility.py:165,193`、`sprint5/H1_WCET_WORKORDER.md:30` 与 `sprint5/dsp/harness/h1_wcet_measure.c:11,99`（H1 成本替身，B2 待核已覆盖）、`sprint6/dsp/audio/M2_SURVEY.md:125-126,158,317`（只是选项清单）。

**过程问题**：登记 §6 说"逐条人工判定"，并只列了 3 处"不需加标"。但 premise_hits.txt 中 `NEXT_SESSION_BOOTSTRAP.md:66`、`critic_a123_rv.md:122` 这两条命中既没加标也没排除，A2:60 只被"本节"标间接覆盖。所以"逐条判定"的自述不准确。

### 3.3 表头（任务 3）

- 正确的部分：v2.0 = 2026-05-29、是最后一个编号版本；"以上 7 行"（:1006-1012）数目正确；最新条目 2026-10-02 存在；4d7e528/d47ed19/6d0a0af 都是 ITC-PM 在 2026-06-05 提交，分别对应 V1-SCOPE+EQ-O1、BUDGET-L1（PRD §3.4 直翻）、SPL-CALIBER；33b1966（09-26）对应 v2.5。
- 有问题的部分：
  - decisions_log :4 写"（2026-10-02 表头更正，正文未改）"，但本包在正文追加了 :739-740 ↑注和 :1013 文末注，表头没有跟着更新（P1-M8）。
  - :7"首版 2026-05-26"、:8"写于 2026-05-26"是推断。原"日期"字段没写含义，06-02 之前也没有 git 记录（P1-m6）。
  - :8"现状以文末最新条目为准"有误导性，因为按 :1013 注，条目也会插在中间各节。
  - PRD :6"（见上列 commit）"覆盖不到 v2.5，因为 33b1966 没列出；另外 4d7e528 是 PRD 第一次入 git（整文件新增），"06-05 增补"相对 v2.4 的差异在 git 里看不出来（P1-m7）。
  - PRD :4 缺 PM 拟限定（P1-m5）。

### 3.4 记忆（任务 4）

- 链接：本次改动涉及的 `[[…]]` 全部指向存在的文件。目录里唯一悬空的是 `r14-closed-fira-ruling.md:22` 的 `[[steering-line-constraints]]`（旧文件，未改）。MEMORY.md 的索引行与被改文件内容一致，所有文件都已入索引。
- 新写入的问题：P1-M3（30–50 cyc/MAC 外推）、P1-M4（SPLo）、P1-M5（指向频段）、P1-m10（"06-01 到货"出处）、P1-m11（team_config 自身滞后）、P1-m1（本包让 :102→:103、:1015→:1018 的行号指针失效）。
- 三份全文重写文件删掉了仍有效的事实（P1-m12）：竞品前后比 1k 19.3 / 2k 18.3 / 4k 22.5 dB（竞品实测，`SPRINT2_CTO_REPORT.md:96`）；指向仓外 `competitor_anechoic.md` 的路径；"4 角度采样测不了竞品 −6 dB 波束宽，插值 BW 已撤回"这条 PF-9 防线；DEC-S2-013"禁止 ≥2 阶纯差分"；gate1 中仍未关闭的消声室验证项（互耦、障板衍射、单元散差）。
- 仍未标的过时内容（P1-M6/M7）：
  - `tree-filterbank-real-subbands.md:15` 和 `MEMORY.md:13` 写"撤回（全库）传播已做 / 15 个文件逐处加标"。本包和本评审都证明这不成立，按 C7 不得再这样宣称。
  - `r14-closed-fira-ruling.md:13-14` 与 `MEMORY.md:21` 写"正式阈值 PENDING"、"残余 1.38–2.56×"，已被 T2 ≥1.5×（06-05）、06-06 保守闭合、1.46–2.14× 取代。
  - `workflow-three-gate-rule.md:15` 与 `MEMORY.md:22` 写"板实测 30–50 cyc/MAC"，是不分类别的通用说法。
  - `steering-v1-focusing.md:18` 写"可控线（全 [L4]）"，但聚焦增量已有 49.03 [L1]。
  - `h1-line-state.md:14-21` 的"现场快照"（进行中 R16；173–288 MCPS；1.08–1.69×）没有标"已被上方终态取代"。
  - `MEMORY.md:6` 的 CBT"直阵死路?待核"已在 09-28 更正（digest_H D12）。
  - `MEMORY.md:24`"下一步 WO-S6-AUDIO…待CTO拍"已过时，M1/M2 已过。
  - `MEMORY.md:26`"PRD:183"行指针失效。
  - `sprint3-d55-baseline.md:24`"超指向…留兜底"（R-7）。
- 用户点名的那几类已清理干净：d=30、17×/33×、27×、6.4×、86–144、2.04–2.31、"板 = EV-21569-EZKIT"、opus-4-8 名册、re-cat 规则，在记忆目录中都已标为历史或已改正。

### 3.5 范围（任务 6）

- sprint3、PRD、agents 记忆里的子带补标：**有依据，不算越权**。PM 一旦发现 09-26 的反扫漏了前提型依赖，铁律五/C7 就要求补完；CTO 点名的两份文件只是症状。但扩展之后就必须做完整，所以本轮判 C7 FAIL。
- 仓库文档里的 17×/33× 加标（BOOTSTRAP:15②、decisions_log:739①、PRD:359）：**超出了字面要求**（CTO 说的是"记忆文件"），也超出了 06-04 传播政策（"历史按写时为真；活状态翻转"）。这些标是追加的、内容正确，可以接受。但应当：(a) 在 commit message 里说明；(b) 活规格要处理一致，例如 PRD §3.3:202"DSP 算力裕量 ≥10×"仍未标，而 :359 却写了"≥10× 判据已退役"（P1-m13）。agents/*/memory.md 是 teammate 的记忆，属于"记忆文件"，在要求范围内。
- decisions_log 改标题、给状态行加限定：略超"改版本号"的字面要求，可以接受，但表头随后变得不准（P1-M8）。

---

## 4. 包 2 — 手册摘录

### 4.1 门表

| 门 | 结论 | 证据 |
|---|---|---|
| C1 | N/A | 阅读笔记，不进 log、规格或承诺；README:3 声明"不是结论，未逐条过 critic" |
| C2 | PASS（抽查） | digest 中涉及 L2 的行都明写"非实测"，例如 digest_G:191 |
| C3/C4/C6/C8/C9/C10 | N/A | — |
| C5 | PASS（附 MINOR） | 指针 all:1203/1253/1320/1726 都精确落在对应块头；README 里的计数（173 行、23 条疑点、64 份、349+107 块、28 个主题、59 处丢失、3798/1473 行、HEAD 263e984、155 个 commit）逐项核对一致。例外见 P2-m1 |
| C7 | PASS（附 MINOR） | digest 的时间线按写时引用了已撤回数字（d=30 ×58、17×/33× ×12、1.5k/3k/6k ×12、86–144 ×11、6.4× ×8），大多带日期、L 标和"已推翻"语境，README 做了目录级提示。为稳妥起见，建议每份 digest 文首加一行横幅（P2-m3；PF-9 先例：异地免责不抵） |

### 4.2 公开仓库安全（任务 5）

- 脱敏前后 diff 只有预期的改动：digest_B:243（Windows 用户目录改成 `<CTO>`）、digest_E:363（邮箱改成不复写地址）、digest_I 的 8 行 T24 时间线和 :676-679 主题块。build 脚本对每处替换都做了命中次数校验，并对邮箱正则做了后置检查。
- 9 份 digest、README 和 crosscheck 中：没有点分 IP（只有 `6.3.1.1` 这样的节号）；没有 T24 的 IP 片段、终端编号或同屏内容残留；没有密码、token、密钥（"密码"只出现在 digest_I:413，是一句关于 public 仓库的疑问，不含凭据）；"taxonomy"只出现在 README:33 的排除说明里，分支名本身在 origin 上已公开；"服务器/后台"只出现在 T24 的占位符中。
- T24 提示词数是 9 条，其中 8 条已抹，剩下 1 条是 :377"忽略,发错了"，无害。
- crosscheck 与 `records/ai19.md` 和 `prompts_all.md` 逐条核对：#12/#14/#17 判为相关正确；时间差为 1 分钟和 1–2 分钟；会话计数 16/1/2 正确。
- **超出"只列日期和会话"的内容**（P2-M1）：crosscheck :3 写了本机另一项目的目录名，:5 写了该项目的性质，:23 引用了一条无关提示词的原话。
- 已有问题（不属于本包，P2-i1）：公开仓库里已经有个人邮箱（`sprint6/BOARD_TEST_INSTRUCTIONS.md:83`、`sprint6/STAGE4_TESTER_RUNBOOK.md:157`）和 Windows 用户目录名（`sprint4/dsp/fira/FIRA_IMPL.md:71`），README:31 的说法属实。是否清理要由 CTO 决定：需要改写历史并 force push，不可逆且对外。

### 4.3 README 与 crosscheck 的准确性

- README:27"5 月的文档是 06-09 `43aad40` 一次性入库的"**不准确**。decisions_log 在 06-02（13be4b3）首次入库，prd_update、PROJECT_HANDOVER、simulation_coverage_audit 等 sprint2/docs 在 06-05（4d7e528）首次入库（P2-m1）。
- README:13"D8 = 子带撤回漏标，已于 10-02 补"和 :26 依赖包 1 已提交。包 1 被打回，所以提交顺序必须是包 1 修好过门后先提交（P2-m2）。D8 列出的 6 个位置本包都已加标，这一点属实。
- README:18"§6 列了过时记忆"属实，但其中的 D12（`MEMORY.md:6` CBT、悬空链接）包 1 还没处理。

---

## 5. Findings 清单

### 包 1

| ID | 级别 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| P1-B1 | **BLOCKER（C7）** | §3.2 中 R-1…R-9 | 撤回传播仍有残留：可执行指令、对外交付物、会让结论翻转的派生数、LOCKED DEC 与 PRD 规格行都没加标；premise_hits 中的命中有漏判 | 逐处用统一标签（含 `[L2 host 复算]`）加标，R-6 写明约 1.495× [L3] 并修改 DSP 横幅里"算力台账/B2 不受影响"那句；把 §3.2 排除清单写进登记 §6；premise_hits 每条都要有"加标"或"排除+理由"；修正 PRD:421 |
| P1-B2 | **BLOCKER（C1）** | `prd_update.md:135`、`decisions_log.md:739`②、`A1…:83`、`A2…:44`、`A3…:9`、`NEXT_SESSION_BOOTSTRAP.md:15,141`、`critic_a123_rv.md:111`、`critic_bootstrap_rv.md:35`、`PF8_retrospective.md:168`、`S7_ALGO_UPGRADE_PROPOSAL.md:31`、`agents/critic/memory.md:624` | 12/14 处重述冻结树 [L2 host] 数字的新标缺 `[L2 host 复算]`；与登记 §3 统一标签和 §6"按 §3 统一标签补标"的自述不符。规格和日志属于 C1 硬门 | 每处插入 `[L2 host 复算]`（只有 dsp_8ch_report:47 和验证计划:3 已带） |
| P1-M1 | MAJOR | `S7_VERIFICATION_PLAN.md:219`（以及 :213 横幅） | §5 横幅说"全频段单一换表流程保留"，但 §5.1 仍写"BW@1k ≤30° 是红线"，而更深的表按 [L2] 都会破这条线，指令自相矛盾。PRD v2.5（:120、:419）和 DEC-S7-SIDE30-01 ② 已把它降级（PM 拟、待 CTO 过目），D6 已重开 | 在 §5 横幅加一句："§5.1'BW@1k ≤30° 是红线'写于 09-02、早于 D6 重开；现为工程参考（PM 拟、待 CTO 过目）；换表须写明 500/30° 二级裕量（D35 +0.54 dB / D30 +1.06 dB [L2 理想]）" |
| P1-M2 | MAJOR（升级 CTO） | `decisions_log.md:196`（DEC-S2-009 LOCKED）、`prd_update.md:23,200`、`dsp_migration_inventory.md:13-15` | LOCKED 的设计子带（500-1k…，SB0 ÷16）与冻结实现（3 级树，SB0 ÷8，0–3k + 梳状 detail）不一致；PRD 规格写的验证方法"CCES 代码实现确认"在冻结代码上不成立。这是铁律四精神下的规格与实现冲突，只加"标签错"不够 | 在登记 §5 增加第 4 条待 CTO 裁定：修订 DEC-S2-009/PRD §3.3（承认冻结树结构），还是挂到 DEC-S7-SIDE30-01 ③ 改架构 |
| P1-M3 | MAJOR | 记忆 `dsp-chip-decision.md:21` | 把"板上实际约 30–50 cycle/MAC"写成通用事实，与 DEC-S5-BUDGET-L1-01 的 FIR 核 8.51 cyc/MAC（120/60 MAC 基准分不开时为 8.51–17.02）相反；173–288 正是因为"错 cyc/MAC 类"退役的。容易诱发同类错 | 改成："cyc/MAC 分类别：树形核整路径折合约 30–50（decisions_log R1 行）；H1 聚焦 FIR 核 8.51 [L1-derived]（DEC-S5-BUDGET-L1-01）；规划按 30–50 取保守（DEC-S7-SIDE30-01 风险其四）" |
| P1-M4 | MAJOR | 记忆 `sprint3-d55-baseline.md:18` | "SPLo 82.161 dB [L1 单只]…两者口径不同、勿直比"：KB-DRV-TEST-001_extracted.md:79-85 记的是与铭牌 88 dB/2.83V [L4] 差约 5.8 dB 的铁律四类冲突；SPL_REDO_REPORT_DRAFT.md:109 / RE_SCOPE_EVIDENCE.md:95 定为"[L1 形状 / 绝对电平 L2-条件未定]"、"不下 88→82 结论"。"口径不同"没有出处，又是 SPL 承诺敏感项（PRD ≥90 dB 只有约 4 dB 模型余量） | 改成："SPLo 82.161 dB [L1 形状 / 绝对电平条件未定]；与铭牌 88 [L4] 差约 5.8 dB，记为铁律四类冲突；按 SPL_REDO 不下'88→82'结论，等线③送测条件" |
| P1-M5 | MAJOR | 记忆 `directivity-band-requirement.md:11-15` | 写"S7 红线 BW@1k ≤30°"已过时（见 P1-M1）；写"500 Hz 不要求 / specs from 1 kHz up"与 PRD v2.4 §3.1.1 二级保底（锁定承诺，8 点含 500/30°、500/90°）冲突，而 500/30° 二级裕量正是 D6 选表的硬约束（DEC-S7-SIDE30-01 ②） | 补充：二级保底含 500 Hz 两点；500/30° 裕量是换表约束；BW@1k ≤30° 已非承诺，v2.5 拟降为参考（待 CTO）；DEC-S1-002（不做低频指向）与 JY/T 500 Hz 承诺的张力写明，交 PRD 统一 |
| P1-M6 | MAJOR | 记忆 `tree-filterbank-real-subbands.md:15`、`MEMORY.md:13`、`sprint3-d55-baseline.md:24` | 写"撤回（全库）传播已做/15 个文件逐处加标"，但本包 #16–#28 和本评审 R-1…R-9 证明不成立，按 C7 不得宣称"已撤回"；"超指向…留兜底"未注明子带级兜底在冻结树上不可用（R-7） | 改成"09-26 首轮 + 10-02 补标；仍有残留（CRITIC_Q_R1），清完前不称已做"；:24 加一句"兜底若走子带级在冻结树上不可实现（同 B4），待核" |
| P1-M7 | MAJOR | 记忆 `r14-closed-fira-ruling.md:13-14,22`、`MEMORY.md:21,22,6,24,26`、`workflow-three-gate-rule.md:15`、`steering-v1-focusing.md:18`、`h1-line-state.md:14-21` | CTO 要求"记忆文件里的过时数字先修掉"，但同类过时内容仍未标（正式阈值 PENDING、残余 1.38–2.56、通用 30–50、"可控线全 [L4]"、未标的 H1 快照、CBT 待核、下一步 WO-S6-AUDIO、PRD:183、悬空链接） | 逐条加"〔2026-10-02 注：已被 X 取代〕"或直接改正（T2 ≥1.5× 06-05 / 06-06 保守闭合；49.03 [L1]；fib-cbt 09-28；`[[steering-v1-focusing]]`） |
| P1-M8 | MAJOR（过程） | 全包；`decisions_log.md:4` | 评审期间文件仍在改（+87→+92）；decisions_log 表头"正文未改"没有反映 :739 和 :1013 的追加 | 先冻结快照，改表头为"表头更正 + 锁定基线一览 ↑注 + 文末注；原文未改"，然后按冻结 md5 做 delta 复审 |
| P1-M9 | MAJOR | `decisions_log.md:513-514`（DEC-S3-P0-01 正文："以本条 88.7/45.7、17×/33× 为准…引用以本条为权威"）、:699（汇总表 DEC-S3-P0-01 行"MCPS 纠正 88.7/45.7（17×/33×）"） | 最高可信层仍把已被板上推翻的 17×/33× 写成"权威引用"，且没有注。lead 给 :739 加注的理由在这里同样成立；06-04 传播（R14_RULING_PROPAGATION:202"仅加尾注"）也没有给这一节加尾注 | 在 :514 后、:699 行内各加"↑注 2026-10-02：已被板上 [L1] 推翻（DEC-S4-R1-8CH-01 / DEC-S4-F7-CLOSE-01），不得再作权威引用" |
| P1-m1 | MINOR | 记忆 `gate1…:21`（BOOTSTRAP:102 → 现 :103）、`m2…:18`（decisions_log:1015 → 现 :1018）、`MEMORY.md:26`（PRD:183） | 本包自身的插行让行号指针失效 | 改用锚点（DEC ID / 行名 / 节名） |
| P1-m2 | MINOR | dsp memory:305、critic memory:514/670、BOOTSTRAP:15、decisions_log:739、PRD:359、sprint3-d55:17 | 1.32×（旧"8 进 1 出求和"语义的 core-only build）与 0.92×（产品核路径）并列，都叫"纯核"，却没说两者口径不同（decisions_log:630"旧求和语义不可直比"）；"06-03 推翻"后面跟的是 06-04 的数；0.92×/2.878× 没有就地标 [L1-derived] | 加"（口径不同、不可直比，DEC-S4-F7-CLOSE-01）"，并分开写日期，补就地 L 标 |
| P1-m3 | MINOR | dsp memory:305、BOOTSTRAP:15、sprint3-d55:17、dsp-chip 描述 :3、MEMORY.md:16；PRD:359 | 2.878× 没连体分母（虽然不是选型或对外材料）；PRD 里写的"§8 未计入清单"会和 PRD 自己的 §8 混淆 | 补"（须连体 43–379 MCPS）"；写成"F7_R14_RULING_MATERIAL.md §8" |
| P1-m4 | MINOR | `S7_ALGO_UPGRADE_PROPOSAL.md:194` | "B2 行的周期数是 H1 bench 实测 [L1]"，但该行高端 117,246 是 [L3] | 改成"低端 65,371 [L1 bench]，高端 117,246 [L3 缩放]" |
| P1-m5 | MINOR | 提案 :31；PRD :4 | 引号里的话不是日志原文；PRD 表头缺"PM 拟、待 CTO 过目" | 按日志 ② 原文引用；表头补限定 |
| P1-m6 | MINOR | `decisions_log.md:7-8` | "首版 2026-05-26"、"写于 2026-05-26"是推断；"现状以文末最新条目为准"有误导性 | 改成"原表头日期 2026-05-26（含义未注）"；"现状按各主题最新条目" |
| P1-m7 | MINOR | `prd_update.md:6` | v2.5 的 33b1966 没列出；4d7e528 是 PRD 第一次入 git | 补 33b1966，并注明"06-05 前无 git 版本" |
| P1-m8 | MINOR | `A3_decision_recommendation.md:9` | 文首横幅的"受影响处"漏了 :39（路线表一级冲刺行）和 :43（A3 推荐①） | 补列 |
| P1-m9 | MINOR | `dsp_8ch_report.md:47` | 只说"频率范围、d/λ 列"是设计意图；"抽取比、子带率"两列同样是设计值（冻结树为 6/12/24/48 kHz） | 补一句 |
| P1-m10 | MINOR | 记忆 `dsp-chip-decision.md:15` | "06-01 到货"仓内没有出处 | 注"（CTO 提示词 06-01 17:44，digest_I_prompts.md:589）" |
| P1-m11 | MINOR | 记忆 `agent-team-ops-lessons.md:14` | 让读者去 team_config 查当前模型，但 team_config 最新名册行是 09-02 claude-fable-5-1，而 09-26 起 critic 裁定是 claude-opus-5-5 | 改成"以会话自身 model ID 为准；team_config 可能滞后" |
| P1-m12 | MINOR | 重写的 3 个记忆文件 | 删掉了仍有效的事实（竞品前后比、competitor_anechoic 路径、插值 BW 撤回防线、禁 ≥2 阶差分、消声室待验项） | 用一两行补回或给出指针 |
| P1-m13 | MINOR | `prd_update.md:202` | 活规格"DSP 算力裕量 ≥10×"没标，而 :359 已写"≥10× 已退役"，部分加标前后不一致 | 加标（T2 ≥1.5×，DEC-S4-CRITERION-01-FINAL），或在 commit message 里说明政策 |
| P1-m14 | MINOR | `S7_VERIFICATION_PLAN.md:3` | 横幅紧贴"> **作者**"引用块，渲染时会并成一段 | 中间加一个空行 |
| P1-i1 | INFO | — | 范围判断见 §3.5 | — |
| P1-i2 | INFO | — | 已核实：全部数字转录正确；yaml 能解析；链接有效；冻结件未动；删除行只在表头和页脚；没有越权作废 | — |
| P1-i3 | INFO | `prd_update.md:209,222` | 有两个"§3.4"标题（06-05 留下） | 下次修订时重新编号 |
| P1-i4 | INFO | decisions_log DEC-S5-V1-SCOPE-01 / DEC-S5-STEER-V1-01 | v1"现板可做聚焦"的实现前提（子带分数延时）与 B2 同样待核 | 加 ↑注，指向登记 §2.3 |
| P1-i5 | INFO | `prd_update.md:15` | 把 d=30 标成"[L3/目测]"，按 POLICY v1.2 目测应为 L0（decisions_log:167 写的是 [L0]），属既有错标 | 顺手改标，或登记 |
| P1-i6 | INFO | — | 本 critic 给出的约 1.495× 是 [L3] 线性缩放，按铁律七须由 PM/dsp 用第二工具复核后才能落盘 | — |

### 包 2

| ID | 级别 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| P2-M1 | MAJOR | `prompts_crosscheck_〈旧文件名，含另一项目名，已更名为 other_project〉.md:3,5,23`（以及文件名） | 超出"只列日期和会话"：写了另一项目的性质（〈另一项目的性质，公开版略〉）、本机目录名，并引用无关提示词原话（#15）。与 README:34 的自述和 CTO 要求不符，且仓库公开 | 删掉性质描述和 #15 引语；目录名改为"另一本机项目"；文件名可以中性化 |
| P2-m1 | MINOR | `README.md:27` | "5 月的文档是 06-09 43aad40 一次性入库"不准确 | 改成"多数 5 月文档在 06-09 入库；decisions_log 06-02（13be4b3）、sprint2/docs 若干份 06-05（4d7e528）先入库" |
| P2-m2 | MINOR | `README.md:13,26` | 依赖包 1 已提交 | 包 1 过门后先提交，再提交包 2；或先改成"待修正提交" |
| P2-m3 | MINOR | 9 份 digest 的文首 | 没有就地提示"按写时原文照录，含已撤回或已推翻的数字" | 每份加一行横幅，指向 decisions_log 和撤回登记 |
| P2-m4 | MINOR | `digest_E_sprint6_kb_tools.md:209,317` | 〈一个可能属于另一项目的本机压缩包，公开版不写文件名〉 可能属于另一项目 | 核实；如果是另一项目的东西就删掉文件名 |
| P2-i1 | INFO | 仓库既有文件 | 公开仓库里已有个人邮箱和 Windows 用户目录名（见 §4.2） | 交 CTO 决定（改写历史属不可逆、对外动作） |
| P2-i2 | INFO | digest_F:157、digest_I:412,776 | 出现 GitHub 用户名，但 remote URL 本身就是公开的 | 无需处理 |
| P2-i3 | INFO | 提交方式 | `knowledge_base/` 被 gitignore（其中 ezkit 有 1280 个文件） | 用 `git add -f` 按 11 个显式路径添加，再核对 `git status --short` 没有带进别的文件 |
| P2-i4 | INFO | — | 已核实：脱敏差异只有预期项；T24 9 条 = 8 条已抹 + 1 条无害；没有 IP、凭据或分类分支内容 | — |
| P2-i5 | INFO | — | 已核实：crosscheck #12/#14/#17 及 all: 指针准确 | — |

**计数**：包 1 为 BLOCKER 2 / MAJOR 9 / MINOR 14 / INFO 6；包 2 为 BLOCKER 0 / MAJOR 1 / MINOR 4 / INFO 5。

---

## 6. 过 delta 门的最小修复路径

1. 先冻结包 1，后面所有改动在同一个快照上做。
2. P1-B2：12 处补 `[L2 host 复算]`。
3. P1-B1：R-1…R-9 加标，R-6 改 DSP 横幅，登记 §6 增加补充行和完整的排除清单（premise_hits 每条都要有结论），修正 PRD:421。
4. P1-M1：给验证计划 §5 横幅补上 §5.1 红线的说明。P1-M2：登记 §5 增加第 4 条待 CTO 项。
5. P1-M3 至 P1-M7：改记忆文字（上表已给出建议文本），同步 MEMORY.md 的索引行。
6. P1-M8：改 decisions_log 表头。
7. 送 delta 复审；包 1 提交后，再修 P2-M1、P2-m1 并提交包 2。
8. MINOR 项可以同批改，也可以登记后续处理；不阻塞 delta 门，但 P1-m1（行号失效）建议同批修。
9. P1-M9：给 decisions_log:514 和 :699 加 ↑注。

---

## 7. lead 晚到两项的复核

**(a) `prd_update.md:359`（§7.3 表后注）**
- 数字和 DEC 编号都正确：1,006,935 → 1.32×（DEC-S4-R1-8CH-01）；0.92× 和 2.878×（DEC-S4-F7-CLOSE-01）；43–379 MCPS（DEC-S4-C9-RELEASE-01）；≥10× 已退役、T2 ≥1.5×（DEC-S4-CRITERION-01-FINAL，decisions_log:913-920）。
- **符合 DEC-S5-SPL-CALIBER-01**：:938 和 :949 写"旧 117/88 源值全库不改；本裁定不撤旧值，只立内部新口径 + 对外冻结"。这条注没有改 117.1 那一行，只指向 §3.2 的 94.0 dB 内部口径行（PRD:194 自带 [L2 待坐实] 标），而且注里没有裸写 94.0。:944 写明 117 与 94.0 是同一量在 20logN 和 10logN 两种口径下的值，所以"现行内部口径见 §3.2"的指向是对的。
- 遗留问题：0.92× 和 2.878× 没有就地标 L（P1-m2）；PRD 里写"§8 未计入清单"会和 PRD 自己的 §8 混淆（P1-m3）；同一份 PRD 的 §3.3:202"≥10×"活规格仍未标（P1-m13）；PRD 表头 :4 已提到 §7.3 注，这一点属实。

**(b) `decisions_log.md:739`（锁定基线一览 ↑注）**
- 数字和 DEC 编号正确；C9 连体要求的写法是"引用须连体 §8 未计入清单"，没有写出 43–379 这个数，可以接受。
- 第②条里的"500-1k/…是设计标签"与 #24/#25 的分级一致。但"冻结树实际分界 3k/6k/12k"没有标 `[L2 host 复算]`（归入 P1-B2）。
- 表头 :4"正文未改"没有反映这条注（P1-M8）。

**(c) lead 的追问：decisions_log 里还有没有把这些值当现行陈述而又没有注的地方**（逐行 grep `33×|17×` 和 `1.5k|500-1k|1k-2k|2k-4k|4k-8k`，再逐条判读）：

| 行 | 内容 | 判定 |
|---|---|---|
| :513-514、:699 | DEC-S3-P0-01：17×/33×"为准…引用以本条为权威"，汇总行无注 | **未注，残留**（P1-M9） |
| :50 | 低频子带影响段里的"4 个子带（500-1k/…）" | 设计史，未注（可列入排除，见 §3.2） |
| :91 | DEC-S2-002 决策内容"4 子带（500-1k/…）" | **未注**（R-8） |
| :196 | DEC-S2-009 LOCKED"锁定 4 子带（500-1k/…）" | **未注**（R-8，并见 P1-M2 升级） |
| :234、:794、:795、:920 | 17×/33× | 已写明被推翻或退役，没问题 |
| :517 | F-2"12k/6k/3k/1.5k" | 已有 :518 勘误注 |
| :737 | 17×/33×、500-1k/… | 已有本包 :739 注 |
| :1040 | 1.5k/3k/6k 相关 | 已有 09-26 注 |
| :14、:64 | "17×17mm"是封装尺寸 | 误命中 |

1.5k/3k/6k 这组边界标签在 decisions_log 里已经没有未注的残留。

---

## 8. 未核清单（如实报告覆盖面）

按 lead 的收口要求，以下检查**没有做或只做了抽查**：

1. 9 份 digest（约 600 KB）没有逐行核对事实，只做了抽查：README 的计数、all: 指针、PII/IP/T24/分类分支扫描、正则方式的 C2 抽查、已撤回数字的出现次数和语境抽样。digest 的时间线和疑点条目没有逐条回源核对。
2. 本 critic 算出的约 1.495×（R-6）是 [L3] 线性缩放，**没有做铁律七要求的第二工具复核**。
3. 非 md 的代码、脚本、csv、log 没有全量扫前提依赖，只看了关键词命中到的文件。09-26 登记 #1–#15 的那些位置（S7_ACOUSTIC_SIM_REPORT 的逐处加标、s7_* 脚本注释、两份 ERRATUM 旁注、pf4 脚本头注）没有重新核实，只复看了 S7_DSP_ASSESSMENT 的横幅和 :184。
4. 17×/33× 在 39 份 md 中共出现 95 次。除 decisions_log、PRD、BOOTSTRAP 和记忆外，没有逐行判读，只按 06-04 传播政策（R14_RULING_PROPAGATION:164-202）的分类视为"写时为真"。
5. 定点修改的 5 个记忆文件（sprint3-d55、steering、m2、agent-team-ops、directivity）**没有改前文本**，只能拿改后文本对照仓库来源，无法判断是否误删了什么。全文重写的 3 个文件则对照了 BEFORE 文件。
6. crosscheck 中 #18/#19（03cb2e29）判为"无关"，只读了两条原文，判断合理但没有逐条证实；digest_E 里的 〈一个可能属于另一项目的本机压缩包，公开版不写文件名〉 是否属于另一项目，没有核实（P2-m4）。
7. `deliverables/Gate1-baseline-array-validation-2026-05-26.md` 只确认了存在，没读内容。
8. PRD 和 decisions_log 中其他可能过时的活状态（除本报告点名的行以外）没有做语义级扫描；decisions_log 只做了 17×/33× 和子带标签两类正则扫描。
9. markdown 渲染只检查了验证计划 :3 的空行问题，其他新增标注的渲染效果没有逐一看。
10. 快照之后（20:03 以后）的任何改动都没有看到，需要 delta 复审。

reviewer: critic @ claude-opus-5-5 / 2026-10-02

---

<!-- 第 2 轮（delta）：CRITIC_Q_R2_DELTA.md -->

# CRITIC_Q_R2_DELTA — 2026-10-02 修正包 / 手册摘录包 delta 复审

reviewer: critic @ claude-opus-5-5 / 2026-10-02

> 范围：只复审 CRITIC_Q_R1 各 finding 的修复，以及新增文字里有没有新错；不重做 R1 全审。只读，未改任何文件。

## 0. 结论

> **最终裁定以 §6 为准**（lead 更新后的快照：仓库 diff md5 `07c30576…`，20:30:53 核验一致）：包 1 **CONDITIONAL**（P1-M9 已关闭；只剩 R2-M1：ERRATA 副本未脱敏）；包 2 **PASS**。下表是对前一个快照 `a3523461` 的裁定，保留作留痕。

| 包 | 裁定（以 20:25:29 校验通过的冻结快照为准） | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|
| 包 1 修正包 | **CONDITIONAL** | 0（R1 的两个 BLOCKER 已关闭） | 2（R2-M1 新增；R2-M2 = P1-M9 在快照中未修） | 6 |
| 包 2 手册摘录 | **PASS** | 0 | 0 | 0（提交顺序见 P2-m2） |

包 1 要转为 PASS_WITH_MINOR，需满足两个条件：
1. 不要把 `CRITIC_Q_ERRATA_20261002.md` 原样提交，改交脱敏版（R2-M1）；
2. P1-M9 的修改要在冻结后的快照上补核（R2-M2）。

**过程问题**：冻结声明之后，文件**又被修改了**（见 §3）。本裁定只对下面列出的快照哈希有效。

## 1. 快照核验

- 20:25:29 核验：仓库 `git diff | md5sum` = `a3523461ce22fc6f823036976c8389a7`（22 个文件，+169/−11），与 lead 给的一致。记忆目录 13 个文件、包 2 的 11 个文件，md5 前 8 位也全部一致。
- 20:28:57 复查：仓库 diff 变成 `07c30576e6d29e21471b4ddd6128d280`，冻结后改过的文件是 `sprint2/docs/decisions_log.md` 和 `agents/dsp-algorithm/memory.md`。记忆目录里 `MEMORY.md`（现 2aaabcbd）、`dsp-chip-decision.md`（现 c7486f6a）、`workflow-three-gate-rule.md`（现 4f8186c3）、`working-style-lessons.md` 也在 20:28 改过。详见 §3。

## 2. R1 各 finding 的复核（冻结快照）

| R1 ID | 状态 | 证据 |
|---|---|---|
| P1-B2（C1） | **关闭** | 22 个文件的新增行中，凡重述 3k/6k/12k、≤2.5k、SB0 通带、0–3k 的共 30 行，30 行都带 `[L2 host 复算]`，缺 0 行 |
| P1-B1（C7） | **关闭** | R-1 `NEXT_SESSION_BOOTSTRAP.md:70`；R-2 `critic_a123_rv.md:130`；R-3 `A2…:9` 文首横幅覆盖 §0–§5 并注明子带率 6/12/24/48；R-4 `SPRINT3_DESKTOP_CLOSURE.md:58`；R-5 `EXP_COMPET…:5,:72`；R-6 `S7_DSP_ASSESSMENT.md:4,:192` 加提案 :102；R-7 decisions_log :251/:311/:435、`1khz_optimization.md:128`；R-8 decisions_log :102/:202、PRD :30/:210、`dsp_migration_inventory.md:20`、`PROJECT_HANDOVER.md:94`；R-9 PRD :425。登记 §6.2 已逐条处置 premise_hits 的 30 条，并承认第一轮"逐条人工判定"说法不准。**我自己的复扫**（同组关键词，另加 FIB、选项 1.5、sb2+sb3、1.5k/3k/6k、SB0<1.5k；排除 knowledge_base）：命中的文件要么带撤回标，要么在 §6.2 排除清单里，只剩两处——`.claude/skills/dsp-algorithm/SKILL.md:97,107`（写的是"子带-FIB 未建"，本身正确）和 `s7_windows_sweep.log`（已由 §3 第 6 行覆盖）。子带撤回这一条，C7 通过 |
| R-6 数值 | 正确 | 1,333,333 / (830,903 + 61,013) = 1.4949，标 [L3]；PM 用 Python 与 MATLAB 两轨核过（我只核了算术，没看 MATLAB 运行记录）；子带样本数出处 h1_wcet_measure.c:28-31 |
| P1-M1 | 关闭 | 验证计划 :214 补了"§5.1 红线写于 09-02、早于 D6 重开；PM 拟、待 CTO 过目；D35 +0.54 / D30 +1.06 dB [L2 理想]" |
| P1-M2 | 关闭 | 登记 §5 第 4 条；DEC-S2-009 下 :202 注明"待 CTO 裁定" |
| P1-M3 至 P1-M7 | 关闭（以快照版本为准） | cyc/MAC 按类别写；SPLo 写成"[L1 形状 / 绝对电平 L2、条件未定]"，并引 KB §3a 与 SPL_REDO；directivity 写明二级保底含 500 Hz 两点、BW 线降级为 PM 拟；tree-filterbank 写"别再说已全部传播"；r14、workflow、steering、h1 快照横幅、MEMORY 的 :6/:21/:22/:24/:26 都已改 |
| P1-M8 / m6 | 关闭 | decisions_log :4/:7/:8 的表头已列出追加的注，日期写"含义未注" |
| P1-M9 | **快照中未修**（→ R2-M2） | 快照里 decisions_log:520（DEC-S3-P0-01"以本条 17×/33× 为准…引用以本条为权威"）和 :705 都没有注，lead 的修复清单也没把它列为未做。冻结后已改，见 §3 |
| P1-m1 至 m14、i4、i5 | 关闭 | 行号指针改成锚点；口径和日期分开写；补了 [L1-derived]；改用"F7_R14_RULING_MATERIAL.md §8"；B2 行写清 L1/L3；按日志原文引用；33b1966 与首次入 git 的说明；A3 清单补全；dsp_8ch 抽取率和子带率两列；"06-01"写了出处；team_config 会滞后；补回竞品前后比等；PRD §3.3 的 ≥10×；空行；V1-SCOPE 的 ↑注；PRD §0 的 [L0] |
| P1-i3 | 未做，已声明 | PRD 有两个 §3.4，留待下次修订 |
| 包 2：P2-M1、m1、m3、m4 | 关闭 | `prompts_crosscheck_other_project.md` 里没有项目名、目录或引语（#15 只是中性转述）；README 改正了入库历史；9 份 digest 都有公开版横幅；压缩包名在 3 处删掉（digest_E 和 README）。复扫没有发现邮箱、IP、T24 内容、分类分支内容或另一项目的名称。digest 相对 records 的差异只有横幅、脱敏和 T24 |

## 3. 冻结后的改动（20:28）——只粗看，没有正式复审

- decisions_log：在 DEC-S3-P0-01 详节下和汇总表后加了两条 ↑注，内容看起来正确（1.32× [L1] 旧求和语义，0.92×/2.878× [L1-derived]，标明口径不同，连体 F7_R14 §8）。**应该能关掉 P1-M9**，但要在新快照上确认。
- 记忆 `dsp-chip-decision.md:21` 与 `workflow-three-gate-rule.md:16` 改写了 cyc/MAC 的说法："25× 高估折合每个桌面 MAC 约 16.5 cycle [L3 推算]"，算术对得上（1,006,935×750/1e6 = 755.2 MCPS ÷ 45.7 MMAC/s ≈ 16.5；25 ≈ 16.5 × 1500/1000）。"30–50 是 FIRA 编排类的保守包络"有出处（`sprint5/H1_FINAL_RULING_MATERIAL.md:42`、`H1_R15_FIX_PACKAGE.md:76`）。**副作用**：decisions_log:234 写的"真实 ~30-50 cycle/MAC"现在和记忆里的 16.5 [L3] 推算对不上了。建议在 :234 加一条 ↑注，或者登记到撤回登记，否则日志和记忆会各说各的（INFO-1）。
- `dsp-chip-decision.md:23` 新增"选型的教训（PF-1）"一段，其中"…不是冻结的功劳"和 decisions_log:234"制度 gating 生效…25× 高估未污染不可逆决策"的说法有张力，建议两边对齐，或者写明各自指的是什么（R2-m6）。
- `working-style-lessons.md` 和 `MEMORY.md` 也改了，**没有看**。

## 4. Findings（R2）

| ID | 级别 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| R2-M1 | **MAJOR（公开仓库）** | `sprint7/critic/CRITIC_Q_ERRATA_20261002.md`（未入库，准备随包 1 提交，登记 §6.2 引用它）:212、:216、:280 | 这是 CRITIC_Q_R1.md 的逐字副本（cmp 完全一致），里面有包 2 刚删掉的另一项目信息：旧文件名里的项目名、项目性质、压缩包文件名（本报告不复写原文）。一旦提交，等于在公开仓库里重新发布这些内容，与 README:37 的自述和 CTO 要求相矛盾 | 提交脱敏版：这三处改成中性措辞，文首注明"公开版，按 P2-M1 同规则脱敏，其余逐字"。原件只留在 scratchpad |
| R2-M2 | MAJOR | 快照中的 `decisions_log.md:520,:705` | P1-M9 在冻结快照里没有修，lead 的修复清单也没把它列为未做（完整性说法过头） | 冻结后已加注（§3），需在新快照上确认；以后修复清单要把未做项写全 |
| R2-m1 | MINOR | decisions_log:745、PRD:363、BOOTSTRAP:15、critic memory:514/670、dsp memory:305、dsp-chip:18 | 1.32× 标的是 [L1]，严格说应为 [L1-derived]（周期数是 L1，比值是按当时假设 1 GHz 推出来的；CCLK 06-04 才实测确认），和 0.92× 的标法也不一致 | 统一改成 [L1-derived] |
| R2-m2 | MINOR | `prd_update.md:429` 页脚 | 页脚仍写"'BW@1k ≤30°'降为工程参考"，没有"PM 拟、待 CTO 过目"（表头 :4 已经有了） | 页脚补上限定 |
| R2-m3 | MINOR | 记忆 `dsp-chip-decision.md:15` | "06-01 17:44 到货"：17:44 是 CTO 通报"板已到手"的时间，不是到货时间 | 改成"06-01（17:44 前）已到手" |
| R2-m4 | MINOR | 记忆 `sprint3-d55-baseline.md:18` | "94.0 dB @1W [L2]"：DEC-S5-SPL-CALIBER-01 规定必带完整标注"@1W 总输入 [L2 模型，待消声室坐实]" | 用完整写法 |
| R2-m5 | MINOR | 记忆 `sprint2-algorithm-baseline.md:27` | 引了"3 阶 WNG −13.4 dB"，这是 Sprint 2 旧几何下的数（`1khz_optimization.md:60,75`） | 注明"旧几何，仅示量级"，或者删掉数字只留规则 |
| R2-m6 | MINOR | 记忆 `dsp-chip-decision.md:23`（冻结后新增） | "不是冻结的功劳"与 decisions_log:234 的"制度 gating 生效"说法有张力 | 两边对齐，或写明各自所指 |
| INFO-1 | INFO | decisions_log:234 | 见 §3：日志里的"真实 ~30-50 cycle/MAC"与记忆里的 16.5 [L3] 推算不一致 | 加 ↑注或登记 |
| INFO-2 | INFO | — | 我的复扫对子带撤回是干净的；17×/33× 的其余历史位置仍按 06-04 政策视为"写时为真" | — |

## 5. 未核

1. 冻结后的改动（§3）只粗看过：`working-style-lessons.md`、`MEMORY.md` 的新内容没看；decisions_log 和 dsp memory 只看了 P1-M9 相关的注。需要在新快照（仓库 diff md5 `07c30576…` 加上新的记忆哈希）上再做一次 delta。
2. 登记 §6.2 第 #29–#43 行写的"补标位置"，只抽查了 #29–#35、#38–#43 对应的实际位置，没有逐行核对。
3. PM 说的 MATLAB 两轨复核没看运行记录，只复核了算术。
4. §6.2 排除清单里 40 个不带标记的文件，只核了清单是否覆盖我的命中，没有逐文件复读排除理由。
5. 22 个文件的 169 行新增文字已通读，但对 S7_RETRACTION_SUBBAND_EDGES.md §6.2 的长段落只读了表格、数值段、排除清单和处置段的要点。

---

## 6. 快照 `07c30576` 复核（lead 更新后的快照，最终）

**哈希核验（20:30:53）**：仓库 `git diff | md5sum` = `07c30576e6d29e21471b4ddd6128d280`（22 个文件，+172/−11）。记忆目录 MEMORY 2aaabcbd、dsp-chip c7486f6a、workflow 4f8186c3、working-style 1df30402，其余 10 个与前一快照相同。包 2 的 11 个文件哈希未变。全部与 lead 给出的一致。

| 项 | 结论 | 证据 |
|---|---|---|
| P1-M9（= R2-M2） | **关闭** | decisions_log:523（DEC-S3-P0-01 第 2 条下加注，"引用算力以后者为权威"）、:739（汇总表后加注），表头 :4 的注清单也写进了"DEC-S3-P0-01 详节与汇总表"。数字和 DEC 编号正确 |
| 30–50 cyc/MAC 的改写（dsp memory、dsp-chip:21、workflow:16、MEMORY:16/:22） | 算术正确，措辞小改（N-1、N-2） | 1,006,935 × 750 / 1e6 = 755.2 Mcyc/s，除以 45.7 MMAC/s ≈ 16.5 cycle/桌面 MAC [L3] |
| R2-M1 ERRATA 副本 | **仍未关闭（MAJOR）** | `sprint7/critic/CRITIC_Q_ERRATA_20261002.md` 仍有 4 处另一项目的名称或性质（按 P2-M1 所列字样 grep，命中 4 次；本报告不复写字样） |
| dsp-chip PF-1 段 | 有出处 | decisions_log:207"Gate 2 关闭，ADSP-21569 最终确认（不可逆采购决策）"原话属实；"不是冻结的功劳"是 critic-r F-07 的判断，见 R2-m6 措辞建议 |
| MEMORY.md:25"SRU 路由配反"的更正 | 部分核实 | 3bf91af 的提交信息写的是"SRU 信号路由表 8 路由 + 6 引脚使能逐条…时钟方向链核一致"，支持"查过、无误"；但 787a7a1 写的"两静默无声类封死"指哪两类，没有对照 R39/R40 原文（见未核） |
| working-style-lessons:15 的注 | 正确 | 与 test3-diagnosis 记忆一致：07-08 闭合，根因是物理极性 C2/C4 接反；07-01 那次差异仍未解释 |
| 用词残留 | 已清 | 我 R1 建议的"树形核整路径折合约 30–50"在记忆和仓库 diff 里出现 0 次 |

**本 critic 自我更正**：R1 的 P1-M3 修法里，我建议写"树形核整路径折合约 30–50（decisions_log R1 行，L1 周期 ÷ 桌面 MMAC）"。这句**是错的**：用 L1 周期除以桌面 MAC 算出来约 16.5，不是 30–50。我照抄了 decisions_log:234 的数字，没有自己复算，这正是我该替别人拦下的那种错。critic-r F-06 抓到了它；lead 按 16.5 [L3] 改写是对的。

**新 findings（只针对本快照的新文字）**

| ID | 级别 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| R2-M1 | **MAJOR（延续）** | `sprint7/critic/CRITIC_Q_ERRATA_20261002.md` | 未脱敏（见 §4） | 提交脱敏版 |
| N-1 | MINOR | `agents/dsp-algorithm/memory.md` 新注；记忆 dsp-chip:21、workflow:16 | "R1 行的 ~30–50 后来**被定为** FIRA 编排类的保守预算包络，不是直接测量"：记录里没有这样一条定义。`sprint5/H1_FINAL_RULING_MATERIAL.md:41-42` 称它是"board reality for the tree-FIR + FIRA-orchestration path"，DEC-S5-STEER-V1-01 称"板证包络"，DEC-S7-SIDE30-01 称"项目规则"。"不是直接测量"是 critic-r F-06 用 16.5 [L3] 推出来的结论，不是记录中的定义 | 改成："R1 行的'~30–50'与 R1 自己的周期对不上（R1 周期 ÷ 桌面 MAC ≈ 16.5 [L3]）；记录中 30–50 作为 FIRA 编排类的项目预算规则使用（DEC-S7-SIDE30-01 风险声明其四），没有找到直接测量出处" |
| N-2 | MINOR | 同上 | "高估约 25×"紧挨着"每个桌面 MAC 约 16.5 cycle"，读者会以为两数矛盾。实际 25 ≈ 16.5 × 1.5，因为 33× 的分母用的是 1500 MCPS 峰值 | 补一句"（33× 以 1500 MCPS 为分母，另含 1.5 倍）" |
| N-3 | MINOR | `decisions_log.md:234` R1 行 | 本包让仓库内出现了新的不一致：agents/dsp-algorithm/memory.md 说 R1 行的 30–50 不是测量值，而最高可信层 :234 仍写"真实 ~30-50 cycle/MAC"，没有注。DEC-S7-SIDE30-01 ③ 的风险声明（每通道 FIR"超预算 2.5 倍"）也建在这个规则上 | 在 :234 加 ↑注（16.5 [L3] 推算 + 30–50 无直接测量出处 + 以 S-FIRB 实测为准），与 agents memory 一致 |
| R2-m1 至 m5 | MINOR（延续） | 见 §4 | 本快照未处理（1.32× [L1] 仍出现在 :523 的新注里；PRD 页脚；"06-01 17:44 到货"；94.0 dB 的标注；−13.4 dB） | 同 §4 |

**最终裁定（快照 07c30576 + 上列记忆哈希）**：
- 包 1：**CONDITIONAL**，0 BLOCKER / 1 MAJOR（R2-M1）/ 若干 MINOR。只要提交脱敏版 ERRATA，即可转 PASS_WITH_MINOR，不需要再审，lead 自行 grep，确认另一项目的名称、性质和压缩包名为 0 即可（**注意**：如果把本 delta 报告附到 ERRATA 文件里，本报告也要按同一规则检查；我已把本报告里的原字样去掉）。N-3 建议同批加注。
- 包 2：**PASS**；提交顺序必须包 1 在前（P2-m2）。

**未核（本节）**：787a7a1"两静默无声类"所指，以及 R39/R40 原文；working-style-lessons 除 :15 以外的内容；MEMORY.md 除 :16/:22/:25 以外的改动没有逐行比对，因为没有前一版文本，只核了哈希和这三处。

reviewer: critic @ claude-opus-5-5 / 2026-10-02

---

<!-- 第 3 轮（delta）：CRITIC_Q_R3_DELTA.md -->

# CRITIC_Q_R3_DELTA — 冻结快照 9b44a908 的小 delta

reviewer: critic @ claude-opus-5-5 / 2026-10-02

> 范围：只看 lead 列的 5 项。只读，未改任何文件。本报告不复写任何需脱敏的原字样。

## 0. 结论

| 包 | 裁定 | BLOCKER | MAJOR | MINOR / INFO |
|---|---|---|---|---|
| 包 1 修正包 | **CONDITIONAL** | 0 | 1（R3-M1，源头是我自己 R1 报告的措辞） | 0 / 1 |
| 包 2 手册摘录 | **PASS**（哈希未变；仍须包 1 先提交） | 0 | 0 | 0 |

R3-M1 不需要再审：lead 改完后自己 grep 确认为 0，包 1 即为 **PASS_WITH_MINOR**。

## 1. 快照核验（20:34:41）

仓库 `git diff | md5sum` = `9b44a90806877430c5ff34036969d72e`（22 个文件，+174/−11）。ERRATA 的 md5 为 `fd519b67…`。记忆目录：MEMORY 2aaabcbd、dsp-chip 7c6e79f1、workflow 4f8186c3、working-style 1df30402、sprint3-d55 e5a120d8、sprint2 9459f18f，其余 8 个不变。包 2 的 11 个文件哈希不变。全部与 lead 给出的一致。

## 2. 逐项

| # | 项 | 结论 | 证据 |
|---|---|---|---|
| 1 | P1-M9（= R2-M2） | **关闭** | decisions_log:523（DEC-S3-P0-01 第 2 条下："…引用算力以后者为权威"）、:739（汇总表后）；表头 :4 的注清单已列入"DEC-S3-P0-01 详节与汇总表"。数字和 DEC 编号正确 |
| 2 | 20:28 的改动 | **通过** | 30–50 的改写：**我在 R2 提的 N-1 有一半说错了**。DEC-S5-BUDGET-L1-01 的详节原话是"30-50 cyc/MAC 是 FIRA-编排类、非本 flat-FIR 核类=保守"，所以"FIRA 编排类的保守包络"有出处。"不是直接测量"是由 16.5 [L3] 推出来的，注里写明了依据，可以接受。PF-1 段对 decisions_log:207（"不可逆采购决策"）、:234 的自评、DEC-S3-PROC-01（"芯片此前 LOCKED…建立在未实测数字上"）的引用都核对属实，现在把两种说法并列，不再下定论。MEMORY:16/:22/:25 与 working-style:15 和上一快照相同，已核 |
| 3 | R2 的 MINOR | **全部关闭** | 今天新增的仓库注里，1.32× 共出现 7 次，记忆里 2 次，全部标为 `[L1-derived]`，没有残留的 `[L1]`。PRD 页脚已加"（PM 拟、待 CTO 过目）"。dsp-chip 写"06-01 17:44 之前已到 CTO 手上"。sprint3-d55 写的是完整标注"94.0 dB @1W 总输入 @1m（远场外推）[L2 模型，待消声室坐实]"。sprint2 注明 −13.4 dB 按 d=30 算、d=55 没有复算 |
| 4 | INFO（N-3） | **关闭** | decisions_log:253 的 ↑注：25× 折合约 16.5 [L3 推算]；30–50 为 FIRA 编排类保守包络（DEC-S5-BUDGET-L1-01）；8.51 [L1-derived]。和 agents/dsp-algorithm 记忆一致，仓库内不再自相矛盾 |
| 5 | R2-M1 的 ERRATA 脱敏 | **部分关闭，见 R3-M1** | 另一项目的名称、性质、压缩包名、旧文件名都已替换，grep 结果为 0；文首写明"公开版、按同一规则脱敏"；没有邮箱或 Windows 用户名 |

## 3. Findings

| ID | 级别 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| R3-M1 | **MAJOR（公开仓库）** | `sprint7/critic/CRITIC_Q_ERRATA_20261002.md:160` | 这一行逐字保留了 T24 那条线的服务器 IP 片段和三台终端的编号。T24 按 CTO 2026-10-02 裁定不进公开内容，build 脚本的后置检查也专门拦这几个字样。**错在我**：R1 §4.2 本来是在说明"已确认这些字样不存在"，却把字样本身写了出来，ERRATA 照抄了下来 | 把 :160 改成"没有 T24 的 IP 片段、终端编号或同屏内容残留"。附 R3 时同样检查。自查方法：用 `build_manual_sources.py` 后置检查里的那组字样对 ERRATA 全文 grep，结果为 0 即可 |
| R3-i1 | INFO（可选） | decisions_log:253、agents/dsp-algorithm/memory 注 | 25× 和 16.5 写在一起，没有说明 33× 的分母是 1500 MCPS 峰值（所以 25 ≈ 16.5 × 1.5），读者可能以为两个数矛盾 | 可补半句，不阻塞 |

## 4. 本轮的自我更正

1. R1 §4.2 在说明"没有 X"时把 X 本身写了出来（T24 的 IP 片段和终端编号），导致公开版副本带出了敏感字样（R3-M1）。以后描述脱敏结果时，只写类别，不写字样。
2. R2 的 N-1 说"记录里没有这样的定义"，这句不对：DEC-S5-BUDGET-L1-01 明确把 30–50 归为"FIRA-编排类…保守"。真正缺出处的只是"不是直接测量"这一点，而这一点现在已经由 16.5 [L3] 推算给出了依据。

## 5. 未核

ERRATA 只按敏感字样做了全文 grep（另一项目、邮箱、Windows 用户名、T24 字样），以及文首和 :159-:160、:216、:220 几行的目视检查；没有逐行比对它与 R1/R2 原件的其余差异。

reviewer: critic @ claude-opus-5-5 / 2026-10-02
