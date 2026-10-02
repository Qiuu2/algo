# digest_F — `sprint7/docs/*.md` + `sprint7/signals/s7ff_v1/README.md` 摘读

> ⚠ 公开版说明（2026-10-02）：本摘录按写时原文照录，里面会出现已撤回或已被推翻的数字（如 d=30、17×/33×、1.5k/3k/6k 子带标签、86–144 MCPS、6.4×）。采信任何数字前，以 `sprint2/docs/decisions_log.md` 和 `sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md` 为准。

> 范围：18 份 `sprint7/docs/*.md`（515,334 B）+ `sprint7/signals/s7ff_v1/README.md`（17,599 B）= 19 份，合计 532,933 B，**全部读完**（长文件分段读，无跳读）。只读，未改仓库，未派 sub-agent。
> 引用约定：无目录前缀的 `S7_*.md` = `sprint7/docs/S7_*.md`；冒号后为文件内行号（已用脚本抽核 266 处引用的行内容，5 处偏差已改；并核过全部 437 个行号均落在文件长度内）。标 `(git)` 的事实来自 `git log`（提交时间/提交信息），不是文件正文。正文里为省字用的简称（均在 `sprint7/docs/` 下，SIG 除外）：
> PROP=S7_ALGO_UPGRADE_PROPOSAL.md；DSPA=S7_DSP_ASSESSMENT.md；VPLAN=S7_VERIFICATION_PLAN.md；B63=S7_B63_WALLCLOCK_GAP.md；INTAKE=S7_BOARD_RESULTS_INTAKE.md；SB=S7_TESTER_RUNBOOK_SB.md；POLQA=S7_POLARITY_QA_RUNBOOK.md；RETR=S7_RETRACTION_SUBBAND_EDGES.md；LIT=S7_LIT_REGISTER_SIDE30.md；WTBL=S7_TESTER_RUNBOOK_WTBL.md；ANA=S7_SIDE30_ANALYSIS.md；FIR=S7_SIDE30_PERCH_FIR_DESIGN.md；DRV=S7_DRIVER_MATCHING_RUNBOOK.md；FF=S7_SIDE30_FARFIELD_TEST.md；FIRB=S7_FIRBENCH_RUNBOOK.md；ALT=S7_SIDE30_ALT_ALGOS.md；HYB=S7_SIDE30_HYBRID.md；IDX=S7_TESTER_INDEX_SIDE30.md；SIG=`sprint7/signals/s7ff_v1/README.md`。
> 采信提醒（CTO 序：decisions_log > runbook > git > memory）：本组文件**不含 decisions_log 正文**，其中的 DEC 内容都是转述；要在手册里写成定论的，请回 decisions_log 核对。本组文件**没有任何板上/现场 [L1] 回填数据**（见 §5-3），所有数字都是桌面 [L2]/[L3]/[L4] 或"历史 [L1]（06-16/06-29/07-08）"的转引。

---

## 0. 读了什么

| # | path（均在 sprint7/docs/，另注者除外） | 字节 | 行数 | 读全？ | 首次入库（git，`--diff-filter=A`） | 最后提交（git） | 提交数 |
|---|---|---|---|---|---|---|---|
| 1 | S7_ALGO_UPGRADE_PROPOSAL.md | 36946 | 258 | 全文 | 5adfe91 2026-09-02 19:25 | 33b1966 2026-09-26 17:55 | 3 |
| 2 | S7_B63_WALLCLOCK_GAP.md | 52601 | 381 | 全文 | e773399 2026-09-03 01:43 | 4e0b2ce 2026-09-03 14:20 | 3 |
| 3 | S7_BOARD_RESULTS_INTAKE.md | 40634 | 592 | 全文（INI 模板段 :54-453 为重复字段，已逐行读） | 7d6704d 2026-09-03 12:20 | 4e0b2ce 2026-09-03 14:20 | 2 |
| 4 | S7_DRIVER_MATCHING_RUNBOOK.md | 37157 | 387 | 全文 | db301ef 2026-09-26 18:27 | 0ef46c4 2026-09-27 19:44 | 2 |
| 5 | S7_DSP_ASSESSMENT.md | 47633 | 499 | 全文 | 5adfe91 2026-09-02 19:25 | 33b1966 2026-09-26 17:55 | 2 |
| 6 | S7_FIRBENCH_RUNBOOK.md | 21140 | 205 | 全文 | 0ef46c4 2026-09-27 19:44 | ce87ed1 2026-09-29 00:48 | 2 |
| 7 | S7_LIT_REGISTER_SIDE30.md | 7226 | 47 | 全文 | 33b1966 2026-09-26 17:55 | 46574ed 2026-09-28 01:54 | 2 |
| 8 | S7_POLARITY_QA_RUNBOOK.md | 42308 | 427 | 全文 | 3567aae 2026-09-03 01:28 | 0ef46c4 2026-09-27 19:44 | 3 |
| 9 | S7_RETRACTION_SUBBAND_EDGES.md | 9915 | 112 | 全文 | 33b1966 2026-09-26 17:55 | 33b1966 2026-09-26 17:55 | 1 |
| 10 | S7_SIDE30_ALT_ALGOS.md | 25584 | 239 | 全文 | 46574ed 2026-09-28 01:54 | cd113e2 2026-09-29 01:25 | 2 |
| 11 | S7_SIDE30_ANALYSIS.md | 22004 | 194 | 全文 | 33b1966 2026-09-26 17:55 | cd113e2 2026-09-29 01:25 | 6 |
| 12 | S7_SIDE30_FARFIELD_TEST.md | 34057 | 339 | 全文 | db301ef 2026-09-26 18:27 | 3a008e8 2026-10-02 01:54 | 3 |
| 13 | S7_SIDE30_HYBRID.md | 19809 | 196 | 全文 | cd113e2 2026-09-29 01:25 | cd113e2 2026-09-29 01:25 | 1 |
| 14 | S7_SIDE30_PERCH_FIR_DESIGN.md | 32036 | 309 | 全文 | 04fd908 2026-09-26 18:23 | 0ef46c4 2026-09-27 19:44 | 2 |
| 15 | S7_TESTER_INDEX_SIDE30.md | 7772 | 65 | 全文 | 0ef46c4 2026-09-27 19:44 | 263e984 2026-10-02 01:54 | 6 |
| 16 | S7_TESTER_RUNBOOK_SB.md | 24486 | 248 | 全文 | d524fde 2026-09-03 01:28 | 4e0b2ce 2026-09-03 14:20 | 2 |
| 17 | S7_TESTER_RUNBOOK_WTBL.md | 7750 | 89 | 全文 | 7686c05 2026-09-26 17:55 | 04e0e6a 2026-09-28 01:21 | 4 |
| 18 | S7_VERIFICATION_PLAN.md | 46276 | 418 | 全文 | 5adfe91 2026-09-02 19:25 | 7d6704d 2026-09-03 12:20 | 2 |
| 19 | `sprint7/signals/s7ff_v1/README.md` | 17599 | 158 | 全文 | 3a008e8 2026-10-02 01:54 | 3a008e8 2026-10-02 01:54 | 1 |

补充（git，非本组文件）：本仓库首个提交 4bf0f52 为 2026-06-02，全仓 155 个提交；与本组文件相关的提交只在 2026-09-02 ~ 2026-10-02。`sprint7/docs/` 下无非 .md 文件（`ls` 18 项均为 .md）；`signals/s7ff_v1/wav/` 有 61 个 WAV + `MANIFEST.md5`（`ls` 62 项，与 SIG:25 相符）。

---

## 1. 文件清单

按首次入库时间排序。"过门与 CTO 状态"栏是**文件内原文**（引号内），必要时附 git 提交信息作对照；"状态行"可能滞后于后来的提交，见 §5-1。

| 首次入库日期 | path | 类型 | 一句话内容 | 过门与 CTO 状态（原文） |
|---|---|---|---|---|
| 2026-09-02 | S7_ALGO_UPGRADE_PROPOSAL.md | 提案（供 CTO 裁定） | PM 综合 dsp/acoustic/testing 三份输入：评估 B1 EQ+限幅、B2 聚焦 v2、B3 偏转、B4 低频、B5 换窗、B6 未闭合项、B7 忙等重构；建议本轮做 ①B6.3 拆 831k 墙钟 ②B6.4/6.5 数值门基座 ③测试战役 P0→P2→P1 ④B1，下轮 B2，不做 B3/B7/全频段换窗，挂起 B4/B5；附 D1–D14 待裁（:16-31, :227-246） | :5「状态：DRAFT → 独立 critic（全包…）→ CTO 常识审（三道关）。**未 commit。**」；:3 2026-09-26 部分撤回横幅；:229「裁定结果见 decisions_log DEC-S7-RULINGS-01（2026-09-02）与 DEC-S7-RULINGS-02（2026-09-03）；本表保留为提案原貌」。git 5adfe91：「独立 critic FAIL→1BLOCKER+2MAJOR+9MINOR 全修→delta PASS」 |
| 2026-09-02 | S7_DSP_ASSESSMENT.md | 分析（dsp 六段式评估+算力台账） | 每个候选按 收益/算力/冻结件影响/验证/风险/建议 六段评估；算力一律用**墙钟口径**：锚 `g_m2_beam_cyc_max`=830,903 cyc/帧（62.3%，余量 1.605×）[L1]，到 1.5× 线余量 57,986 cyc；M2 对 bench 463,273 差 1.79×（成因未拆）；B1 5.05–39.3 MCPS，B2 单项即越线（1.488×），B3 现板不可达，B7 不做（:27-50, :422-462） | :6「状态：DRAFT，待独立 critic（关②）+ CTO 常识审（关③）。未 commit。」；:2 2026-09-26 部分撤回横幅 |
| 2026-09-02 | S7_VERIFICATION_PLAN.md | 验证计划 | 四级证据阶梯（桌面[L2]/上板[L1]/台前相对[L1相对]/R3 消声室无排期）；B1–B6 逐项验证与负控制；板测会话 S-A/S-B/S-C 打包；三份程序 P0（基线正规化）/P1（chmap 远场 A/B）/P2（自家阵列极性 QA）；现 rig 做不到的 13 条（:11-22, :250-258, :262-361, :391-405） | :3「状态：草案，待独立 critic 门 + CTO 常识审（三道关）」；:418「草案，未 commit；待独立 critic 门 + CTO 常识审」 |
| 2026-09-03 | S7_TESTER_RUNBOOK_SB.md | 测试员执行单（板测 S-B） | 4 个 build：B0 M2 基线 / B1 +`M2_SELFTEST`+`M2_SEG_CYC` / B2 +`M2_SELFTEST_NEGCTRL` / B3 无宏；固定 10 步流程；指纹表 A、板门表 B、时钟表 D（读 CGU0 三寄存器实测 CCLK）、自检表 C（八锚 CRC）；所有 cyc 格留空（:40-47, :55-81, :87-163） | :4「依据 DEC-S7-RULINGS-01 D3（CTO_OK=1）+ DEC-S7-IMPL-01 第 2 项/第 1 项 c」；:248「未 commit；待独立 critic §12（FG1/FG2/IO1/IO2/ST1-E）过门与 CTO-gated commit」；总览 IDX:35「critic 已过（CRITIC_D/E/F）；CTO 已在 RULINGS-02/03 中据此裁定」。git d524fde：「CTO_OK=1; 独立 critic CONDITIONAL→1MAJOR 文档修→delta PASS」 |
| 2026-09-03 | S7_POLARITY_QA_RUNBOOK.md | 测试员执行单（S-POL / P2 正式版） | 自家 16 元阵列极性 QA：Step A 电池纸盆逐只（1.5 V 首选/9 V 瞬触）+ Step B 375 Hz 成对声学相消（`M2_STATIC_TXTEST`+`M2_STXT_LOCALIZE`，`g_stxt_ch_mask`）；产出通道→物理位置映射；判据全为同会话相对比较，不写期望 dB（:1-8, :82-175, :175-312） | :8「状态：草案…待独立 critic 门 + CTO 常识审；未过门前不作权威」；:9「↑状态更新 2026-09-27，PM：已过独立 critic（CRITIC_D_D3PKG_POLQA_20260903.md：PASS_WITH_MINOR → delta…commit 3567aae）…**CTO 常识审：没有单独记录，开工前请 CTO 过目**」；D7/D8 CTO 裁定见 :4、:326 |
| 2026-09-03 | S7_B63_WALLCLOCK_GAP.md | 工单/设计（WO-S7-B6.3） | M2 墙钟 830,903 对 bench 463,273（1.79×，差 367,630 cyc）的拆解：假设 a「Debug 无 -O」（`.cproject:39` 无 value，推断 [L3]）的路径 A/B 对照 build；bench 三段探针 `sprint7/dsp/probe/`；板上 `M2_SEG_CYC` 四段括号（w/ana/syn/tx，每帧 33 次 CCNT 读）；15 项排查表（:264-280）；回填模板全部留空 | :4「状态：设计 + 桌面验证完成，**板上数字全部待测试员回填**」；:20「CTO 2026-09-03：改由测试员读 CGU 寄存器实测…实测回来前 B1 条件 0 未满足，DEC-S7-RULINGS-03」；:30「CTO 2026-09-03 裁定不必做、保持默认关（DEC-S7-RULINGS-02）」。git e773399：「critic CONDITIONAL→2MAJOR+8MINOR 全修→delta PASS」 |
| 2026-09-03 | S7_BOARD_RESULTS_INTAKE.md | 判读方案（预写，等数据） | 4 批回填 INI（S-B 四 build / B63 对照臂 / bench 探针 / 极性 QA）+`[CLK]` 节；判读决策树 §2.0–2.6；B1 启动 5 条件（条件 0＝实测 CCLK）；宿主脚本 `sprint7/tools/s7_intake.py` v3.3；全文无板上数字（:3-9, :457-552） | :9「状态：critic-F 三轮（首轮 FAIL → delta CONDITIONAL → delta-2 PASS_WITH_MINOR…）；verdict 见 `sprint7/critic/CRITIC_F_INTAKE_20260903.md`。**落库后 PM 停止，等测试员数据**」；:3「CTO 2026-09-03 指令，DEC-S7-RULINGS-02『准备工作』」；:5 DEC-S7-RULINGS-03 |
| 2026-09-26 | S7_RETRACTION_SUBBAND_EDGES.md | 撤回登记（铁律五） | DEC-S7-RETRACT-SUBBAND-01：冻结子带树实际分界 **3k/6k/12k**（非 1.5k/3k/6k），SB0≈0–3k，1 kHz 在 SB0 内；detail 带是未对齐梳状残差，只有 4 子带增益全等时 telescoping 才精确重建→树上不能子带加权；影响分级（作废/标签错/待核）；15 文件反扫+加标表；冻结头文件本体不改（旁注 ERRATUM）（:13-25, :50-64, :68-96, :100-104） | :3「CTO 授权：会话内『根据目前的信息先开干』（2026-09-26…）」；:4 缘起 critic R1 F1 BLOCKER；:108-112「仍待 CTO 裁定」3 项 |
| 2026-09-26 | S7_SIDE30_ANALYSIS.md | 分析（侧面抑制 20→30 dB） | 口径（1/3 oct 1k–4k 各带 R90≥30 dB，r≥8 m 自由场）；现表 Dolph-20 理想 att90 22–24 dB 封顶；D35 理想 36.9–39.0 dB 但 7 频段良率仅 6.0% [L2 on L4]；路线 A 固定表（D30/D35/RS-A/RS-B）；路线 B 每通道滤波器（FIR/IIR/hybrid）；配对是最大杠杆；执行顺序 §6；全文无 L1（:11-69, :71-131, :133-154, :164-174） | :4 critic R1 FAIL→R2 CONDITIONAL→R3a FAIL→delta PASS_WITH_MINOR；:5「CTO 裁定：DEC-S7-SIDE30-01…四项同意」；:75 R3e；:142/:149 R3f/R3g「CTO 常识审待」 |
| 2026-09-26 | S7_LIT_REGISTER_SIDE30.md | 登记（外部文献入库，铁律六/C8） | 17 篇文献（A 声区 4/B 音柱工程 8/C 稳健校准 4/D CBT 1）的 md5/DOI/字节；存仓库外 `knowledge_base/papers/2026-09_side30/`；2026-09-28 增补 Keele 2002 与 PM 通读 van Beuningen & Start 2000；措辞约束（:9-27, :29-38, :44-47） | 无 gate 行；:3「登记日期 2026-09-26，与下载同日，不超过 24h」；:31 Keele 副本来自第三方站点、版权受限、「是否改为向 AES 购买正式版本，由 CTO 决定」 |
| 2026-09-26 | S7_TESTER_RUNBOOK_WTBL.md | 测试员执行单（S-WTBL） | `M2_WTBL_SEL` 运行时切表：同一二进制 6 张表（sel0 D20 冻结/1 D25/2 D30/3 D35/4 RS-A/5 RS-B），JTAG 改 `g_m2_wtbl_sel`，读 applied/oob_count/applied_sum（权重和 211122/187690/171198/158784/152407/162056，:63-65）；远场 A/B 顺序 0→3→4→5→0→2→0，只能下 [L1 相对] 结论 | :9「过门状态（2026-09-27）：critic R3a 固件包 PASS_WITH_MINOR → delta 已修（commit 7686c05/42f38a0）；**CTO 常识审待**」；:14 sel4/5 增补过 R3e，「CTO 过目：待」；:12 sel 5「PM 追加…待 CTO 过目」 |
| 2026-09-26 | S7_SIDE30_PERCH_FIR_DESIGN.md | 分析（每通道 FIR 桌面原型） | V1「守 1 kHz 窄束」/V1n/V2「最大侧向」× 64/128/256 抽头：理想 ≥40 dB；7 频段未校准良率（U-flat 误差模型）V1-128 20.4%（D35 6.0%）；夹具配对+增益修正（U-flat）V1-128 92.1%（D35 82.8%；G 模型下分别 79.5%/56.8%）；128 抽头核上 0.98–3.28 M cyc/帧 [L3×30–50 cyc/MAC]，可行性取决于 FIRA [L4]；落地需 CTO 架构裁定（§6）（:10-37, :161-181, :206-221） | :3「DRAFT 修订 2（critic R3b 判 FAIL → 9 项整改 → delta 复审 CONDITIONAL → N1/N2/N3 整改，**待复审**；三道关…未走完）」——文内无后续状态更新 |
| 2026-09-26 | S7_DRIVER_MATCHING_RUNBOOK.md | 测试员执行单（S-DRV） | 逐只喇叭复响应（1–4 kHz 灵敏度+相位）治具测量与配对：REW 采集、`s7_driver_pairing.py` 做离群/配对/修整/现装配预测；拆喇叭属 C10（铁律九）须 CTO 签；`V_JIG_MAX` 等 Q1–Q12 空栏（:3, :64-91, :369-384） | :6「R3c + delta 修订稿…待 delta critic + CTO 常识审」+「↑状态更新 2026-09-27，PM：critic R3c delta 判 PASS_WITH_MINOR…已入库（commit db301ef）；**CTO 常识审待**，开工前请 CTO 过目，并填好 `V_JIG_MAX`、签字 C10」；:91 CTO 确认栏空白 |
| 2026-09-26 | S7_SIDE30_FARFIELD_TEST.md | 测试员执行单（S-FF） | 侧抑远场测试：室外自由场 r=8 m，1/3 oct 逐带粉噪 500–5k+6.3k，0/±60°/±90° Leq×3 遍，R=L(0°)−L(θ) 逐带判读；动态范围自检/距离不变性/「地面反射未隔离」永久标注；取代 VERIFICATION_PLAN §8.1 的侧抑部分；`V_FF_MAX` 空栏（:3, :12-31, :92, :320-336） | :7「R3c + delta 修订稿…」+「↑2026-09-27：critic R3c delta 判 PASS_WITH_MINOR…已入库（commit db301ef）；**CTO 常识审待**…填好 `V_FF_MAX`」；:8「↑2026-10-02」信号文件已入库，「CTO 过目：待」 |
| 2026-09-27 | S7_FIRBENCH_RUNBOOK.md | 测试员执行单（S-FIRB） | 每通道 FIR 算力台架（`bench_core_only` 工程）：8 路×63/127/255 抽头×（FIRA T8/T1/P1 + 核 C/SYM）逐通道 golden 门，读 CGU 时钟；全部 cycle 格留空；DEC-S7-SIDE30-01 ③ 路线的算力 go/no-go（:4, :108-148） | :5（原）「critic R3d…CONDITIONAL…**CTO_OK 未取得**」；:6-10「2026-09-29 状态更新」：R3d delta/mini-delta 判 PASS（commit 0ef46c4）；「CTO_OK 已给：CTO 2026-09-29 原话『恩，我同意sfirb可以』」 |
| 2026-09-27 | S7_TESTER_INDEX_SIDE30.md | 总览/索引（测试员） | 6 个会话 ①S-B ②S-POL ③S-FF ④S-WTBL ⑤S-DRV ⑥S-FIRB 的顺序/前提/过门状态/发回项；三条不许碰的线（驱动上限/拆喇叭/接线拓扑）；数据交付规则；待 CTO 定 3 项（:31-40, :42-48, :50-54, :61-65） | :9「过门规矩（三道关）…凡写着『CTO 过目：待』的，开工前先请 CTO 看一眼」；表 :35-40：① critic 已过且 CTO 已裁；②③④⑤「CTO 过目：待」；⑥「CTO_OK 已给（2026-09-29），可以执行」 |
| 2026-09-28 | S7_SIDE30_ALT_ALGOS.md | 分析（FIR 以外两条路线） | 低阶 IIR 分频加权 X3-LR4（7 频段良率与 FIR V1-128 打平、MAC 约 1/7–1/15，但方波冲高最多 +7.4 dB 需联动限幅器）；Duran DDC 原样（4 kHz R90 掉到 8.5 dB，不适合）；Keele 直阵延时 CBT（比不加延时更差）；2026-09-29 补注：X3 被 LPX3-b 取代，逐通道保护限幅器对 FIR 同样须改联动（:15-47, :7-9） | :6「critic R3f 第 1 轮 CONDITIONAL…delta FAIL…mini-delta PASS（CRITIC_N…）。**CTO 常识审：待。**」；:4「CTO 2026-09-27 回复『我同意，你依次干吧』」 |
| 2026-09-29 | S7_SIDE30_HYBRID.md | 分析（hybrid 桌面评估） | 共享线性相位分频（h1=700 Hz, h2=1600 Hz；low/mid/high = h1, h2−h1, δ−h2）+ 每通道频段增益：LPX3-b 良率与 X3/FIR 打平，方波最多 +1.3 dB，保证不削顶仅退 0.81 dB，MAC 7,680（折叠）/13,696（直接）每帧，比 FIR-128×8 少 4.3/4.8 倍 [L3]，延迟 1.31 ms，5 kHz 观察带弱（21 dB）；联动保护限幅器为路线共同待定项（:12-38, :40-57, :94-117, :127-145） | :6「critic R3g 第 1 轮 CONDITIONAL（2 MAJOR…）→ 修正 → delta PASS_WITH_MINOR…**CTO 常识审：待。**」；:4「CTO 2026-09-29 回复『好』」 |
| 2026-10-02 | `signals/s7ff_v1/README.md`（SIG） | 数据包说明 | 远场逐带测试信号包 s7ff_v1：61 个 WAV（12 个 1/3 oct 带×{0,−10,−20,−30,−40 dB}+静音；24-bit/48 kHz/单声道/36 s；稳态 RMS −23 dB 相对满幅），带外衰减谱与指标 CSV，一键门 6 步+23 个反证+MATLAB 第二轨；PM 拟的现场做法清单待 CTO 同意；WAV 进 git（≈302 MiB）（:3-8, :68-94, :135-159） | :11-15「自动检查 PASS；独立 critic 第 1 轮 CONDITIONAL（2 MAJOR）→ delta PASS_WITH_MINOR（CRITIC_P…）；**CTO 过目：待**；三道关走完之前，不交给测试员」；:9「授权：CTO 2026-10-02『好，你先做信号文件』…同日 CTO 选定交付方式为『WAV 进 git』」 |

**文件间"取代/修正"关系（手册采信时按此取最新）**：
- PROP（09-02）的子带级 B4/B5-2/B5-3 部分、DSPA 的子带权重机制 → 被 RETR（09-26）撤回（PROP:3；DSPA:2；RETR:50-54）。
- VPLAN §8.1 的侧抑判据（±90°≥12 dB、2 kHz warble）→ 侧抑部分被 FF 取代（FF:23-31）；VPLAN 的 P1（chmap 远场 A/B）、§5.3 的 30° 主判角、S-C（B1 板测）在 IDX 的 6 个会话里**没有对应执行单**（IDX:63；ANA:129-130）。
- ALT 的"X3 为省算力首选"→ 被 HYB 的 LPX3-b 取代；"FIR 不受限幅器问题影响"一句被 critic R3g F1 否定（ALT:7-9；HYB:21-23；ANA:147）。
- PROP §6 的 PM 建议（如 D8「预授权」，PROP:240）≠ CTO 最终裁定（POLQA:326「不预授权 chmap 翻宏」）；PROP:229 已声明"本表保留为提案原貌"。

---

## 2. 时间线事件

`[文内]` = 文件正文有该日期/事件；`(git)` = 来自提交时间/提交信息。

| 日期 | path:line | 事件 |
|---|---|---|
| 2026-05-26 | S7_LIT_REGISTER_SIDE30.md:40-42 | 「已在本地库、本次被引用的两份（2026-05-26 入库）」：Van Trees 2002 §2.6.3、Boone/Cho/Ih 2009（更早的文献入库） |
| 2026-05-29 | S7_RETRACTION_SUBBAND_EDGES.md:37 | PF-4 桌面仿真 [L2] 已测到「detail 子带带外抑制≈0 dB，是互补重建残差」，但沿用了错误的子带边界标签（后来被撤回的先兆） |
| 2026-06-02 | (git) 4bf0f52 | 本仓库首个提交（core-only S0-S1 host-verified）；此前事件只能在 decisions_log/被引文件里找 |
| 2026-06-04 | S7_SIDE30_HYBRID.md:136 | 「CTO 2026-06-04 裁定」：2.878× 不得单独使用，须与未计入清单连体呈现（同一规则另见 S7_FIRBENCH_RUNBOOK.md:190：DEC-S4-C9-RELEASE-01 要求余量数字与「§8 未计入清单 43–379 MCPS」连体呈现） |
| 2026-06-16 | S7_ALGO_UPGRADE_PROPOSAL.md:39-40；S7_DSP_ASSESSMENT.md:33；S7_VERIFICATION_PLAN.md:46 | M2 FIRA broadside 波束上板 PASS（DEC-S6-M2-BOARD-PASS-01）：`g_m2_beam_cyc_max`=830,903 cyc/帧=62.3% 帧周期 [L1 墙钟，含 FIRA 忙等]，CTO 耳听正常 |
| 2026-06-29 | S7_ALGO_UPGRADE_PROPOSAL.md:40；S7_POLARITY_QA_RUNBOOK.md:19,23；S7_DSP_ASSESSMENT.md:34 | 整机验证：beam_cyc_max 复测 829,218；接线/左右对称/无死路确认（极性除外）；「逐路 solo 等幅 SPL 法对极性天生盲」 |
| 2026-07-01 | S7_VERIFICATION_PLAN.md:241；S7_ALGO_UPGRADE_PROPOSAL.md:165 | 竞品整套 rig「交换实验」：结果**至今未解释**，无法重构，竞品 rig 不在手则永久 OPEN |
| 2026-07-08 | S7_ALGO_UPGRADE_PROPOSAL.md:45；S7_VERIFICATION_PLAN.md:345；S7_POLARITY_QA_RUNBOOK.md:20 | 极性根因闭合（DEC-S6-BEAM-POLARITY-CLOSURE-01）：竞品喇叭 rig 因 C2/C4 两对喇叭 +/− 接反把波束打散；自家 rig 2 kHz 0°95/90°77=18 dB（1 m 近场，非规格）；竞品喇叭 rig 375 Hz 成对读数 solo 87.5/同极性 93.5/反极性 71/本底 40 dB [L1] |
| 2026-07-09~07-15 | S7_ALGO_UPGRADE_PROPOSAL.md:242 | D10：EXP_COMPET 顶注 4 个无落盘出处的数字（远场 2k/30° 抑制 13–16 dB、1.5 dB 重复性、1.9 dB/−43 dB、0.7 dB），问这期间有无远场测量记录 |
| 2026-07-22 | S7_VERIFICATION_PLAN.md:4, :266-268；S7_ALGO_UPGRADE_PROPOSAL.md:6, :46 | 「7-22 后无正式测试」（VPLAN:4；PROP:6）；P0 要在「CTO 7-22 后所用那套」rig 上重测，把 CTO 口述观察值（自家 rig 正面 100/侧面≈80，10 项条件均未记录，[L0]，DEC-S7-OBS-OWNRIG-01，PROP:46）升为 L1（VPLAN:266-268）。观察值本身的日期文内未写 |
| 2026-09-02 18:56 | (git) b6bc5fe；S7_ALGO_UPGRADE_PROPOSAL.md:12 | S7 A 批次入库整理：DEC-S7-SCOPE-01 / OBS-OWNRIG-01 / EXTINPUT-HIT9616-01（critic CONDITIONAL→delta PASS）。DEC-S7-SCOPE-01 内容见 PROPOSAL:6 |
| 2026-09-02 | S7_ALGO_UPGRADE_PROPOSAL.md:4；S7_DSP_ASSESSMENT.md:5；S7_VERIFICATION_PLAN.md:3 | PM(lead) 综合 dsp/acoustic/testing 三位 teammate 的输入写成提案；三份文件头日期均为 2026-09-02 |
| 2026-09-02 19:25 | (git) 5adfe91 | 提案/DSP 评估/验证计划三件入库（critic FAIL→1 BLOCKER+2 MAJOR+9 MINOR 全修→delta PASS） |
| 2026-09-02 22:31 | (git) c9c3f91；S7_ALGO_UPGRADE_PROPOSAL.md:229 | CTO 裁定落库：DEC-S7-RULINGS-01 十四条逐条处置 + DEC-S7-IMPL-01 实施范围（提交信息；本组文件只转述） |
| 2026-09-02 | S7_POLARITY_QA_RUNBOOK.md:4；S7_TESTER_RUNBOOK_SB.md:4 | CTO D7（本轮声学测试接自家 16 元阵列，极性 QA 为硬前置）、D8（自家阵列映射以 Phase A 实测为准）；D3（M2 TU 改动包 CTO_OK=1） |
| 2026-09-03 01:28 | (git) d524fde；3567aae | D3 固件包（`M2_SELFTEST` 八锚/6 宏指纹/`#error` 守卫/`M2_SEG_CYC`/`g_m2_beam_cyc_min`）与极性 QA runbook 入库 |
| 2026-09-03 01:43 | (git) e773399 | B6.3 工单入库（板上数字全留空） |
| 2026-09-03 | S7_B63_WALLCLOCK_GAP.md:30,139,372；S7_ALGO_UPGRADE_PROPOSAL.md:128；S7_POLARITY_QA_RUNBOOK.md:326 | CTO DEC-S7-RULINGS-02：bench 内拆分副本 `fira_tree_probe.c` 不必做；D10 补（1.9 dB/−43 dB 以本轮仿真 [L2] 复算，不为未落盘实测背书）；D8「不预授权 chmap 翻宏」 |
| 2026-09-03 12:20 | (git) 7d6704d；S7_BOARD_RESULTS_INTAKE.md:3 | RULINGS-02 落库 + 板测结果判读方案（`s7_intake.py` v2.2） |
| 2026-09-03 | S7_B63_WALLCLOCK_GAP.md:20,190；S7_BOARD_RESULTS_INTAKE.md:5 | CTO DEC-S7-RULINGS-03：B1 条件 0 改为**测试员读 CGU 寄存器实测 CCLK**（不设旗位放行）；`S7_PROBE_SYN_FG` 不做；`M2_SEG_CYC` 四段追认（git 4e0b2ce 14:20） |
| 2026-09-03 | S7_BOARD_RESULTS_INTAKE.md:9,589 | 判读方案落库后「PM 停止，等测试员数据」；此后 git 无任何提交至 2026-09-26（见 §5-3） |
| 2026-09-26 | S7_RETRACTION_SUBBAND_EDGES.md:3-4 | DEC-S7-RETRACT-SUBBAND-01：撤回「1.5k/3k/6k 子带可分别加权」；缘起 critic R1 F1（BLOCKER），PM 用独立模型复核成立；CTO 授权「根据目前的信息先开干」 |
| 2026-09-26 | S7_SIDE30_ANALYSIS.md:3-5 | 侧面抑制 20→30 dB 分析；CTO DEC-S7-SIDE30-01 四项同意（正式化 30 dB 口径、重开 D6、立项改架构、改板上固件） |
| 2026-09-26 | S7_LIT_REGISTER_SIDE30.md:3-4 | PM 派出 3 路文献检索子代理（A 声区/B 音柱工程/C 稳健校准），16 篇与下载同日登记 |
| 2026-09-26 17:55 | (git) 33b1966；7686c05 | 撤回+SIDE30 分析/文献/PRD v2.5 落库；`M2_WTBL_SEL` 固件第一步 + 切表执行单 |
| 2026-09-26 | S7_SIDE30_ANALYSIS.md:4；S7_SIDE30_PERCH_FIR_DESIGN.md:3；S7_SIDE30_FARFIELD_TEST.md:7 | 同日多轮 critic：G R1 FAIL、H R2 CONDITIONAL、I R3a FAIL→delta PASS_WITH_MINOR、J R3b FAIL→整改→delta CONDITIONAL、K R3c→delta PASS_WITH_MINOR |
| 2026-09-26 18:23~18:28 | (git) 04fd908；db301ef；42f38a0 | 每通道 FIR 原型；喇叭逐只测量单+远场测试单+配对工具；切表单钉住远场单版本（critic R3a F12） |
| 2026-09-27 | S7_SIDE30_ALT_ALGOS.md:4；S7_TESTER_RUNBOOK_WTBL.md:11 | CTO 对「除了 Dolph 还有别的算法吗」的回复「我同意，你依次干吧」→ 稳健扇区表 RS-A、IIR、延时 CBT 的桌面评估 |
| 2026-09-27 | S7_SIDE30_ANALYSIS.md:164；S7_TESTER_INDEX_SIDE30.md:4 | 执行顺序调整：「现装配远场基线」提到拆喇叭之前（critic R3c F6、R3d B-2） |
| 2026-09-27 19:44 | (git) 0ef46c4；S7_FIRBENCH_RUNBOOK.md:3,5 | FIR 算力 bench 包 + 测试员总览页入库；critic R3d CONDITIONAL，CTO_OK 未取得 |
| 2026-09-28 | S7_TESTER_RUNBOOK_WTBL.md:10-14；S7_SIDE30_ANALYSIS.md:6,73 | 稳健扇区表加入切表包：RS-A（sel 4，CTO 同意的「一张」）、RS-B（sel 5，PM 追加，待 CTO 过目）；critic R3e（git 04e0e6a 01:21） |
| 2026-09-28 | S7_LIT_REGISTER_SIDE30.md:27-38；S7_SIDE30_ALT_ALGOS.md:49-62 | 下载入库 Keele 2002（#17，第三方站点副本）；PM 通读 van Beuningen & Start 2000 第 17–28 页（#12 复核） |
| 2026-09-28 01:54 | (git) 46574ed；S7_SIDE30_ALT_ALGOS.md:3,6 | IIR/DDC/Keele CBT 桌面评估落库；critic R3f（CONDITIONAL→delta FAIL→mini-delta PASS） |
| 2026-09-29 | S7_FIRBENCH_RUNBOOK.md:6-10；S7_TESTER_INDEX_SIDE30.md:40 | critic R3d delta/mini-delta PASS；CTO「恩，我同意sfirb可以」→ S-FIRB 可执行（git ce87ed1 00:48） |
| 2026-09-29 | S7_SIDE30_HYBRID.md:3-6 | CTO「好」→ hybrid 共享线性相位分频桌面评估；critic R3g CONDITIONAL→delta PASS_WITH_MINOR（git cd113e2 01:25）；HYB:4 称"等台架期间" |
| 2026-10-02 | SIG:9, :11-15；S7_SIDE30_FARFIELD_TEST.md:8；S7_TESTER_INDEX_SIDE30.md:37, :65 | CTO「好，你先做信号文件」；同日选定「WAV 进 git」；信号包过 critic P（CONDITIONAL→PASS_WITH_MINOR），CTO 过目待；总览页新鲜度锚点移到 3a008e8（git 3a008e8、263e984，01:54） |

---

## 3. 前期环节线索

### 3.1 需求指标 / PRD
**有记录（均为转述；PRD 本体不在本组文件，只引 `prd_update.md` 行号）：**
- 30 dB 侧抑内部目标口径（DEC-S7-SIDE30-01 ①）：「1/3 倍频程 1k–4k 各频段 R90 = L(0°) − max[L(±90°)] ≥ 30 dB；远场自由场 r ≥ 8 m，3 次重复取中值，背景噪声比侧面读数低 ≥10 dB」；「高于 JY/T 表9 在 90° 各点的一级门限（1k 20 / 2k 25 / 4k 10 dB），属内部产品目标」— S7_SIDE30_ANALYSIS.md:15-18；S7_SIDE30_FARFIELD_TEST.md:19。参数「PM 拟、CTO 同意正式化、参数待 CTO 过目」— ANA:15；FF:19, :333(Q10)。
- JY/T 表 9 的 12 点口径（30°/90°/180°×500/1k/2k/4k）与一/二/三级门限：出处 `sprint3/audit/std_table9_compliance.csv` = PRD v2.4 §3.1（`prd_update.md:108-111`）— S7_SIDE30_PERCH_FIR_DESIGN.md:77-79；「JY/T 1 档是冲刺点，2 档是锁定的保底承诺（`prd_update.md:120`）」— FIR:139；二级门限 500/30°=3 dB — ANA:48；180° 各向同性线阵前后辐射相同，不可评 — FIR:79。
- PRD 旁瓣 ≤ −18 dB — ANA:103；PRD v2.5 变更块 — ANA:169；7 频带口径出自 `prd_update.md` v2.5 — FIR:101, :114。
- 旧内部线「BW(−6 dB 全角)@1k ≤ 30°」从 PRD v2.4 起降为工程参考 — FIR:71, :269；1k 波束宽 D20=29.27°，距 30° 仅 0.73° 余量 [L2] — S7_VERIFICATION_PLAN.md:180。
- v1 能力范围 DEC-S5-V1-SCOPE-01：「近场高频展区分区（2–5 m，有用带 ≥4 kHz）」— S7_ALGO_UPGRADE_PROPOSAL.md:95；S7_DSP_ASSESSMENT.md:168；「PRD 验收指标 X 仍 OPEN」— PROP:96, DSPA:171,205。
- 对外 ≥90 dB 承诺 vs 内部口径 94.0 dB [L2 待消声室]，余量约 4 dB — FIR:261；「94.0 [L2] 冻结至 R3」— VPLAN:128。
- 延迟「<30 ms 判据」— DSPA:134（引 `dsp_8ch_report.md:130`）；「任何偏轴指向性 PRD 自动触发 SC-S3-GEOM-01 d 重议」— DSPA:242。

**未见：** 应用场景（博物馆/车站/商场）——本组文件 grep 无命中，仅有"展区分区"字样（PROP:95）；PRD 原文与需求来源日期；"≥1 kHz 才要求指向性"的原话（本组只见 1k–4k 考核口径和 500 Hz 的 JY/T 点）。

### 3.2 竞品样机拆机
**有记录：**
- 「[L1 拆机]」标注：d=55 mm（FIR:53）、配对物理接收同一激励（DSPA:235）——文内**没写拆的是哪台、何时、谁拆**，出处不在本组文件。
- 竞品整套 rig（板+喇叭）：07-01 交换实验（VPLAN:241；PROP:165）；07-08 竞品喇叭 rig 375 Hz 读数 [L1]（VPLAN:345）；竞品 rig 假设映射 {4,5,6,7,0,1,2,3}（VPLAN:274；POLQA:406）；C2/C4 反接（POLQA:20）。
- 竞品 1 m 消声室表：90° 32.0/24.8/25.4 dB（1k/2k/4k），1k/30° 22.5 dB — ANA:159-160；**来源/日期文内未写**（转引自 critic R1 F6）。
- 竞品固件包：「未解包竞品固件」（PROP:7）；D9「C8 接收声明：竞品固件包的接收时间/渠道/授权 + 持有合法性确认（DEC-S3-003 边界），补后 DEC-S7-EXTINPUT-HIT9616-01 的 C8 才闭合」（PROP:241）——是否已补文内未见（git c9c3f91 提交信息列有「D9 KB 更新」）。
- 竞品对比实验 EXP_COMPET（beam-vs-freq、丙单喇叭对照）未跑（VPLAN:242；PROP:166）；"竞品是否分频段处理"只能做远场黑盒对比（ANA:161）。
- Duran Intellivox 作为同构参照：16 单元/8 通道（ANA:139）；文献 LIT #5–#8, #12。

**未见：** 拆机日期、拆机原始记录、竞品型号。

### 3.3 方案 / 芯片选型
**有记录（只有结果，没有选型过程）：**
- 芯片 ADSP-21569（KBCZ10）— FIRB:18；板 AD-EXKIT V2.1 + 21569-SOM — PROP:6；VPLAN:4,29。CCLK=1 GHz 来自 bench F7 G6 读回 [L1]，M2 工程同频原为推断 [L3]，须实测 — DSPA:31；B63:20；INTAKE:5（含数据手册 Rev.C 三道合理性门）。
- 硬件拓扑：8 路单端 DAC1P–DAC8P（无 N 脚）[L1 硬件]、功放 4 片×2 路 — VPLAN:171；DAC ADAU1962A 12ch（用 8）— DSPA:237；16 元线阵 d=55 mm、L=825 mm，通道 c 驱动镜像串联对 {c,15−c} — POLQA:29-30；PROP:114。
- 算法架构：输入端 Dolph-Chebyshev −20 dB Q15 权重（冻结 `dolph_w8_q15.h`）→ 冻结 4 子带半带金字塔（FIRA 实现）→ 恒等重建 — PROP:56,223；FIR:46-48；FIRA = FIR 加速器（VPLAN:46）。
- 选型相关约束：偏转 = 独立立项（DEC-S5-STEER-V1-01）；16ch 硬件叉 = Gate-2 级不可逆 — DSPA:237-238；PROP:114,117。

**未见：** 芯片/方案比选过程（备选、评分、决策日期）——本组只引 DEC-S3/S4/S5 编号，过程在 decisions_log。

### 3.4 开发板 / EZKIT 采购与到货
**未见：** 采购、下单、到货、验收日期，本组文件均无。
**使用线索：** AD-EXKIT V2.1 + 21569 SOM、ICE-1000 识别（POLQA:32）；核心板原理图 V2.1 路径 `knowledge_base/ezkit/vendor_docs/schematics/V2.1/ADSP21569核心板原理图.pdf`（SB:126；INTAKE:51）；「R55 后本板不需要 override」（SB:97）；`softcfg_rc=11×5` 为本板永久预期值（DEC-S6-FSRU1-RESCOPE-01，VPLAN:29；POLQA:213）；上电/JTAG 顺序引 `sprint3/audit/BENCH_OPS_CARD.md`、`ezkit_bringup_checklist.md`（SB:19；POLQA:40）；F7/S7 探针/H1/H2 在同一块板（FIRB:18）；M2 上板 PASS 2026-06-16（PROP:39-40）。工具链：CCES 2.12.1（INTAKE:5）；编译门=测试员的 CCES build（SB:7），在 Windows 机上（FIRB:22,30）；PM 机 cc21k 已装但无 license（SB:7；PROP:246 D14）。

### 3.5 GitHub / 论文调研、框架选择、资料入库
- **论文：有记录** — S7_LIT_REGISTER_SIDE30.md 全文：2026-09-26 三路子代理 16 篇 + 2026-09-28 #17；存仓库外 `knowledge_base/papers/2026-09_side30/` 与 `README_论文索引.md`（含 12 篇付费墙 DOI）（LIT:4-7）；更早 2026-05-26 入库两篇（LIT:40-42）；引用规范「文献 X 报告…，不得写成我方实测」（LIT:6, :44-47）；PM 直接读原文核实（ALT:49-62）。版权风险：Keele 副本来自第三方站点（LIT:31）。
- **GitHub：未见**（grep 无命中）。仅 SIG:154 称「公开仓库」；`git remote -v` 为 github.com/Qiuu2/algo（文件外）。
- **框架/工具选择：未见专门选型决策**，只有使用事实：Python numpy/scipy + MATLAB 双轨交叉核（PROP:55；ALT:234-237；SIG:128-129）、gcc host harness（SB:225-236）、REW 测量（DRV:48）、CCES（INTAKE:5）、ffprobe（SIG:130）。pyroomacoustics 在本组文件无提及。
- **资料入库规则：** 铁律六/C8 外部输入 ≤24h 入库（LIT:1,3）；论文数字是外部证据，非我方 L1/L2（LIT:6）。

### 3.6 团队 / 治理
- **角色：** PM(lead)（PROP:4）；teammates：dsp-algorithm（DSPA:5）、acoustic-simulation（FIR:4）、testing（VPLAN:3）、critic 多轮；PROP:252 列「critic-A、dsp、acoustic、testing，以及 critic-B」；测试员为非 DSP 专家（IDX:3；SB:3），CCES 编译在 CTO/测试员的 Windows 机上（FIRB:22,30）。模型标签：09-02 文件 claude-fable-5-1（PROP:4,258；DSPA:5；SB:248；POLQA:427；VPLAN:3 写「Fable 5.1」），09-26 testing teammate claude-opus-5-5（DRV:387；FF:339）。
- **三道关：** 「自动 verify → 独立 critic → CTO 常识审」（IDX:9；FIR:3；PROP:5）。文内引用的 critic 判决：CRITIC_A（PROP:12）、D（POLQA:9）、F（INTAKE:9）、G/H/I（ANA:4）、K（FF:7）、L（FIRB:7）、M（ANA:75）、N（ALT:6）、O（HYB:6）、P（SIG:13）；`sprint7/critic/` 目录另有 B/C/E/J 及各 `*_scripts/`（`ls`，未读内容）。
- **治理条款被引用：** L 级/POLICY-PROV-001（PROP:55）、C8（LIT:1）、C10/铁律九（SB:19；DRV:64；FIRB:18）、铁律三（DRV:349）、铁律四（POLQA:398；FF:281）、铁律五（RETR:1）、FG1/FG2/IO1/IO2/ST1（VPLAN:413；SB:248）、「CTO_OK 逐包规则（DEC-S7-SIDE30-01 ④）」（ALT:221；HYB:185）、冻结件清单与重跑链（PROP:56；DSPA:52-62）。
- **护栏：**「CLAUDE.md 的 $3/15 min 护栏 PM 无法精确计量，如实报告」「无 sub-agent 递归」（PROP:252）；LIT:4 为 PM 派 3 路文献子代理。
- **CTO 原话（文内转述）：** 「根据目前的信息先开干」（RETR:3）；「我同意，你依次干吧」（ALT:4；WTBL:11）；「好」（HYB:4）；「恩，我同意sfirb可以」（FIRB:8）；「好，你先做信号文件」（SIG:9）；D8 裁定原话（POLQA:326）；D1 墙钟口径、RULINGS-03 实测 CCLK（B63:20；INTAKE:5-6）。
- **撤回自述：**「我方 2026-09-26 会话中『每子带加深、稳健设计多挣 1–4 dB』的数字：从未落库，已在会话中口头撤回」（RETR:55）。

---

## 4. 阶段边界线索

| # | 日期 | path:line | 边界 |
|---|---|---|---|
| B1 | 2026-07-22 → 2026-09-02 | S7_VERIFICATION_PLAN.md:4；S7_ALGO_UPGRADE_PROPOSAL.md:6；(git) | 上一阶段尾：「7-22 后无正式测试」；git 07-22 为 S6 治理瘦身提交，之后到 09-02 无提交（`git log` 提交日分布） |
| B2 | 2026-09-02 | S7_ALGO_UPGRADE_PROPOSAL.md:6,12；(git) b6bc5fe | **S7 立项**：DEC-S7-SCOPE-01「本轮=算法层；产品层不做；治理照旧；硬件仍 AD-EXKIT V2.1 + 21569-SOM；Stage 5 无进展、厂家函无回函、R3 无排期」 |
| B3 | 2026-09-02/03 | S7_ALGO_UPGRADE_PROPOSAL.md:229；S7_B63_WALLCLOCK_GAP.md:3 | S7 第一轮（候选 B1–B7 评估→CTO 裁定 D1–D14→DEC-S7-IMPL-01 三个实施包：B6.3 拆 831k、D3 固件包、极性 QA runbook） |
| B4 | 2026-09-03 14:20 | S7_BOARD_RESULTS_INTAKE.md:9,589；(git) 4e0b2ce | 第一轮收束：判读方案落库，「PM 停止，等测试员数据」；此后 23 天无提交 |
| B5 | 2026-09-26 | S7_RETRACTION_SUBBAND_EDGES.md:3；S7_SIDE30_ANALYSIS.md:5 | **主线切换**：撤回子带边界 + DEC-S7-SIDE30-01 四项同意 → 开启「侧面抑制 20→30 dB」线（口径正式化、重开 D6、改架构立项、改板上固件） |
| B6 | 2026-09-26~09-29 | S7_TESTER_INDEX_SIDE30.md:31-40；S7_SIDE30_HYBRID.md:4 | 侧面 30 dB 线的"桌面评估 + 测试员包"阶段：6 个测试会话成型，候选路线收敛为 固定表 / FIR / LPX3-b；HYB:4「等台架期间」说明桌面评估在等 S-B/S-FIRB 数据 |
| B7 | 2026-09-29 | S7_FIRBENCH_RUNBOOK.md:8；S7_TESTER_INDEX_SIDE30.md:40 | S-FIRB 获 CTO_OK，成为总览页里**第二个可执行会话**（另一个是 S-B） |
| B8 | 2026-10-02 | SIG:9, :14-15；S7_TESTER_INDEX_SIDE30.md:65 | 信号包入库，但「CTO 过目：待；三道关走完之前，不交给测试员」——**当前停在等 CTO 过目** |
| B9 | 持续 | S7_VERIFICATION_PLAN.md:20,33,393；S7_DSP_ASSESSMENT.md:67；S7_SIDE30_FARFIELD_TEST.md:254 | 硬边界：R3 消声室无排期 → 所有绝对规格/对外承诺/EQ 产品系数/聚焦效能 L1 不可闭合；现 rig 只能 [L1 相对] |
| B10 | 持续 | S7_ALGO_UPGRADE_PROPOSAL.md:114,117；S7_DSP_ASSESSMENT.md:229-251 | 硬件边界：现板 8 路对称串联拓扑无法偏转；16ch 硬件叉=Gate-2 级不可逆，须 CTO 独立立项 + d 重议 |
| B11 | 持续 | S7_ALGO_UPGRADE_PROPOSAL.md:44,56；S7_DSP_ASSESSMENT.md:455；S7_SIDE30_HYBRID.md:135 | 工程边界：算力优化冻结令（例外=O1 EQ/保护限幅/SPORT bring-up）；解冻=16ch 立项 或 O1 上板后余量击穿 1.5×，CTO D1 裁定按**墙钟口径**判；冻结件清单 PROP:56 |
| B12 | 前期被引用 | S7_B63_WALLCLOCK_GAP.md:381；S7_VERIFICATION_PLAN.md:6；S7_RETRACTION_SUBBAND_EDGES.md:78-79,91-92 | 前期阶段命名：路径引用显示 sprint3（audit/、dsp/pf4）、sprint4（dsp/fira、dsp/core_only）、sprint5（H1_WCET_WORKORDER、audit/）、sprint6（dsp/audio、BOARD_TEST_INSTRUCTIONS、STAGE4_*）、sprint7（本组）；DEC 前缀 S3–S7（见 §7） |
| B13 | 下一步（文内预告） | S7_ALGO_UPGRADE_PROPOSAL.md:218；S7_SIDE30_ANALYSIS.md:174；S7_SIDE30_ALT_ALGOS.md:221；S7_SIDE30_PERCH_FIR_DESIGN.md:265 | 下轮 B2 聚焦 v2；每通道滤波器固件路径（桌面原型过门→新 golden/自检锚→板门，每个新固件包须单独 CTO_OK）；是否外租消声室由 CTO 定 |

---

## 5. 疑点

**A. 状态与采信**
1. **状态行滞后于提交。** 多份文件头仍写"DRAFT/草案/未 commit/待 critic"，但 git 提交信息已记 critic 通过：S7_VERIFICATION_PLAN.md:3,418、S7_DSP_ASSESSMENT.md:6、S7_ALGO_UPGRADE_PROPOSAL.md:5、S7_TESTER_RUNBOOK_SB.md:248（对 d524fde「critic…delta PASS」）、S7_B63_WALLCLOCK_GAP.md:4（对 e773399）。S7_SIDE30_PERCH_FIR_DESIGN.md:3 写「待复审」，文内**没有后续终审记录**。过门状态请以 `sprint7/critic/CRITIC_*.md` 与提交信息为准。
2. **CTO 常识审（第三关）大面积"待"。** 截至 2026-10-02：S-POL（IDX:36；POLQA:9「没有单独记录」）、S-FF（IDX:37；FF:7）、S-WTBL（IDX:38；WTBL:9,14）、S-DRV（IDX:39；DRV:6）、s7ff_v1（SIG:14）、X3/LPX3-b/FIR 候选路线（ALT:6；HYB:6；ANA:149-153「PM 拟…待 CTO 过目」）均"待"。只有 S-B（IDX:35）与 S-FIRB（IDX:40）已有 CTO 裁定/CTO_OK。手册里这些路线只能写成"候选，待 CTO 定"，不能写成采用。
3. **没有任何板上/现场 [L1] 回填。** 所有回填表均为空白（B63:4,366；INTAKE:4；SB:6；FIRB:11；FF:160-218；SIG:17）；FIRB:187「截至本单，S-B 尚未执行」，HYB:38,143、IDX:48 仍在等 S-B；INTAKE:9,589 后 git 无提交到 09-26，09-26 起的提交主题均为新文档/新测试包，按提交信息未见板测或现场数据回填。**1.79× 差距成因、CCLK 实测值、自家阵列极性/映射、现装配远场基线、逐只喇叭散布都没有结果**。B1 条件 0 明文「未满足」（B63:20；INTAKE:541）→ B1（EQ+限幅）按规则仍挂起。
4. **撤回传播有缺口（铁律五"反扫+加标"）。** (a) S7_VERIFICATION_PLAN.md 没有撤回横幅，且不在 RETR:76-92 的反扫表里，但 §2 B2「子带内分数延时」（:132-164）、§4 B4「低频子带差异化权重」（:178-202，含 `g_m2_sbw_sel`）、§5 B5「每子带旁瓣电平」（:206-225）、:180「子带处理交付的是波束宽跨频率恒定」都建立在被撤回/待核的"子带可分别加权/延时"前提上。(b) S7_ALGO_UPGRADE_PROPOSAL.md:29（§0 摘要）仍写「每子带换窗可把 1–6k 波束宽跨度从 24.4° 压到 15.0°，代价 4k 指向性指数 −4.35 dB…」，撤回横幅 :3 列了 B4/B5-2/B5-3/§4/§5.2/§6，未点名 §0 摘要。(c) B2 在 RETR:64 仍是"待核"，尚无真实树上的验证结论。手册引用 B2/B4/B5 时请回 RETR。
5. **「6.4×」与「1.79×」口径冲突。** DEC-S6-M2-BOARD-PASS-01 写「~130 µs [L2 H2 纯核口径] 的 6.4 倍」，S7 文件认为该基数「不可独立溯源」（F60-MINOR-2），正确同口径尺子是 bench F7 463,273 / H2 base 454,730，M2 超出约 1.8×（PROP:194；DSPA:46-47）；D12 PM 建议加注（PROP:244），git c9c3f91 称 D12 已加注，但文内看不到加注结果。手册请勿使用"6.4×"。且 830,903 是 run 内**最大值**，含首帧冷（DSPA:369 假设 a），稳态值未知。
6. **帧预算/1.5× 线仍是"参考值"。** 1,333,333 / 888,889 依赖 CCLK=1 GHz，CTO RULINGS-03 要求用测试员读到的 CGU 实测值重算（B63:20；INTAKE:5）；HYB:131、FIR:218、ALT:161 都带"待 S-B 读回"。在读回前，凡写"余量 x×"都应带这条限定。
7. **两套 cyc/MAC 换算并存。** DSPA:92 用 H1 的 8.51 cyc/MAC（"低端非下界"，[L3]），FIR:216-217 与 ALT:5、HYB:5 用项目规则 30–50 cyc/MAC 并明说 8.51「是另一类核，只作 [L3] 参考，本文不用它算周期」。两者对应不同核类型，换算时必须同时写明因子与 L 级。
8. **良率/裕量指标口径多套。** D35 的"联合良率"：3 频带口径 23–26% vs DEC 正式口径 7 频带 6.0%（ANA:57-59；FIR:168）；JY/T 点同时有单频值/频带值/带内最小值，差异可极大（V1-128 的 1k/30° 单频 42.29 dB vs 带内最小 17.44 dB，FIR:147；X3-LR4 带内最小 14.29 低于二级线 15，ALT:124）。手册引用须固定口径（建议用 7 频带、频带值/带内最小值）。
9. **旧结论被后续修正。** ALT:44-47「X3 为首选（若接受联动限幅器）」被 HYB（LPX3-b 取代 X3）与 critic R3g F1（"FIR 也须联动限幅器"，ALT:8-9；HYB:21-23）修正；联动保护限幅器是整条"改架构"路线的共同待定项（HYB:149）。

**B. 授权与治理**
10. **RS-B（sel 5）超出 CTO 明确授权。** CTO 只同意加「一张」稳健扇区表（WTBL:11；ANA:73），RS-B 是 PM 追加、「待 CTO 过目」，可能被删（WTBL:12；IDX:64）；其选取规则「是 PM 看过探索扫描之后定的，不是事先定的」（ANA:81），属事后选择。RS-A 同时被标「只作测量用，不是产品候选」（ANA:101），却在 sel 4 里（WTBL:29）。
11. **"20 dB" 起点来源仍未确认。** 是否就是 [L0] 口述观察（DEC-S7-OBS-OWNRIG-01，条件未记录）「待 CTO 确认」；若是新数据须 C8 24h 入库（ANA:13；FF:18, :334 Q11）。
12. **版权与仓库体量。** Keele 论文副本来自第三方站点、版权受限，「不转发、不入 git；是否购买正式版由 CTO 决定」（LIT:31）。信号包 WAV ≈302 MiB 入 git，SIG:154 称"仓库会从 24 MB 涨到约 0.28 GB，而且公开仓库的历史会永久保留"；重生成一次再加 ≈0.26 GB（SIG:155）。"是否公开"文内断言，未在本组核验。
13. **护栏无法计量。** PROP:252「$3/15 min 护栏 PM 无法精确计量」——预算/时间护栏事实上无审计证据。
14. **CTO 空栏（会话启动前必填/必签，当前全空）：** `V_FF_MAX`（FF:107, :326 Q3）、`V_JIG_MAX`（DRV:79, :376 Q4）、C10 拆装签字（DRV:91）、D8 映射裁定（IDX:36）、30° 测量谁出单/何时做（IDX:63；ANA:129-130）、是否保留 sel 5（IDX:64）、信号包 PM 拟做法 8 项（IDX:65；SIG:23-66）、FF Q1-Q13 / DRV Q1-Q12 全部默认值待确认、RETR:108-112 三项。

**C. 数字出处与来源**
15. **未落盘数字。** 「1.5 dB 重复性地板」[未落盘，出处待补]，只能作 [L4] 工作假设（VPLAN:31；PROP:254）；D10 的 1.9 dB/−43 dB 已由本轮仿真 [L2] 复算，但**不为 EXP_COMPET 未落盘实测背书**（VPLAN:180；PROP:128）。
16. **竞品数据出处缺失**：ANA:159-160 的竞品 1 m 消声室表未写来源/日期；EXP_COMPET 顶注数字来源不明（PROP:242）。
17. **"[L1 拆机]" 只有标签没有出处**（FIR:53；DSPA:235）；"d=55 [L1]"的 L1 依据请回 decisions_log/DEC-S3-GEOM-01。
18. **日期细节：** WTBL:9「过门状态（2026-09-27）」引用的提交 7686c05/42f38a0 实为 2026-09-26（git）；LIT:3「登记日期 2026-09-26」表内含 09-28 才入库的 #17（已在 :27-29 增补说明）；INTAKE 内脚本版本标签 v3.3（:3）/v3（:556）/「脚本 v2」（:567）/提交信息 v2.2 并存；B63、POLQA、SB 头日期 09-02、首提交 09-03（git）。
19. **git 历史起点 2026-06-02**，而本组文件引用 2026-05-26/05-29 的事件（LIT:40；RETR:37），说明 6 月前的记录不在此 git 历史中，只能靠 decisions_log/被引文件。
20. **测试流程覆盖缺口：** VERIFICATION_PLAN §9 的最小测试战役（P0→P2→P1→S-B→P0 基线 v2）在总览页被改写：P0 侧抑部分并入 S-FF，P1（chmap 远场 A/B）、30° 主判角、B1 板测 S-C 无执行单（IDX:63；ANA:129-130）。若手册要写"验证流程"，需明确哪些已被取代、哪些悬空。
21. **模型适用边界反复强调：** 各向同性点源、无障板/互耦，±90° 掠射方向最不可信，RS 表恰按 ±90° 优化（ANA:131, :191-194；FIR:88-91）；本组所有侧抑结论均为 [L2]，良率为 [L2 on L4 spread]，无 L1 支撑，不可写成规格。

---

## 6. 附 A：承重事实速查（均为文内转述，保留 L 级；采信前回 decisions_log）

- 阵列：16 元线阵 d=55 mm [L1 拆机]、L=825 mm；8 路单端 DAC 各驱一个镜像串联对 {c,15−c}→阵因子纯实偶函数→现板无法偏转（FIR:53；POLQA:29-30；VPLAN:170-171；PROP:114）。
- 帧与链路：48 kHz、64 样点/帧（1.333 ms）；M2 = 单声道输入→Q15 Dolph-20 权重（c7=1.0 最大）→FIRA 4 子带分析→综合（恒等重建）→TX 交织→8 路；帧预算 1,333,333 cyc（CCLK 1 GHz，待实测）（DSPA:31, :102-115；PROP:223；B63:218-236）。
- 算力基线（墙钟口径，含 FIRA 忙等）：M2 `beam_cyc_max` 830,903（62.3%，1.605×）[L1] vs bench F7 463,273 [L1 bench] → 1.794×，成因未拆；1.5× 线余量 57,986 cyc=43.5 MCPS（DSPA:27-50；PROP:49）。三口径（墙钟/争用 ledger/纯核）互不可比（DSPA:20；PROP:47）。
- 冻结子带树真实分界 3k/6k/12k，detail 带为梳状残差，仅四子带增益全等才 PR（RETR:13-25）。
- 侧抑 [L2 理想]：D20 att90 22–24 dB；D35 36.9–39.0 dB；随机误差底≈32–33 dB（σ²‖w‖²/|Σw|²，ANA:30；FIR:16）；D35 500/30° 二级裕量仅 +0.54 dB，带内最小 2.78 dB 低于二级线（ANA:48）。
- 良率 [L2 on L4]（7 频段，装好直接用，均为 U-flat 误差模型；G 模型数字略高/略低，见原表）：D35 6.0%；RS-B 10.4%；RS-A 13.6%；FIR V1-128 20.4%；X3 21.3%；LPX3-b 21.2%（ANA:114-119；ALT:113-116；HYB:79）；配对+增益修正（U-flat）D35 82.8%、FIR V1-128 92.1%（FIR:168-170）。**配对是最大杠杆**（ANA:126）。
- 候选实现成本：B1 EQ+限幅 6,728 [L3]–52,352 [L4] cyc/帧（DSPA:95）；B2 聚焦 65,371 cyc [L1 bench H1]→单项 1.488× 越线（DSPA:182,188）；LPX3-b 7,680/13,696 MAC/帧 [L3]（HYB:25）；FIR-128×8 32,768/65,536 MAC/帧→核上 0.98–3.28 M cyc [L3×30–50]（FIR:213）；X3 4,416 MAC/帧（ALT:154-157）。
- 板测门：`M2_SELFTEST` 八锚 CRC（B1 期望 rc=0，B2 NEGCTRL 期望 rc=7；期望来自桌面 golden [L2]，SB:134-148, :6）；6 个宏指纹 + `#error` 守卫（SB:87-101）；B1 启动 5 条件（INTAKE:537-545）。
- 极性/映射：竞品 rig 假设映射 {4,5,6,7,0,1,2,3} 不得沿用；自家映射以 Phase A 实测为准；恒等则 `M2_CHMAP_FIX` 保持关（POLQA:326, :406）。
- 测法口径：远场 r≥8 m、1/3 oct 粉噪、3 遍取中值、本底门≥10 dB；所有 ±60°/±90° 读数永久带「地面反射未隔离」；手机分贝计只支撑 [L1 相对]（FF:19, :92, :115-117；VPLAN:19）。

## 7. 附 B：本组文件引用的 DEC 编号（含义仅取自文件措辞）

| DEC | 文内含义 | 一处引用 |
|---|---|---|
| DEC-S7-SCOPE-01 | 本轮=算法层；产品层不做；硬件不变 | S7_ALGO_UPGRADE_PROPOSAL.md:6 |
| DEC-S7-OBS-OWNRIG-01 | CTO 口述观察值 [L0]（正面100/侧面≈80，条件未记录） | S7_ALGO_UPGRADE_PROPOSAL.md:46 |
| DEC-S7-EXTINPUT-HIT9616-01 | 竞品固件包外部输入；C8 接收声明待补 | S7_ALGO_UPGRADE_PROPOSAL.md:241 |
| DEC-S7-RULINGS-01/02/03 | CTO 对 D1–D14 的裁定（09-02/09-03/09-03）；03=实测 CCLK | S7_ALGO_UPGRADE_PROPOSAL.md:229；S7_B63_WALLCLOCK_GAP.md:20 |
| DEC-S7-IMPL-01 | S7 实施范围（B6.3/D3 包/极性 QA 三项） | S7_B63_WALLCLOCK_GAP.md:3 |
| DEC-S7-RETRACT-SUBBAND-01 | 撤回冻结树子带边界（2026-09-26） | S7_RETRACTION_SUBBAND_EDGES.md:3 |
| DEC-S7-SIDE30-01 | CTO 四项同意：①口径 ②重开 D6 ③立项改架构 ④改板上固件（逐包 CTO_OK） | S7_SIDE30_ANALYSIS.md:5；ALT:221 |
| DEC-S7-POLQA-OWNARRAY-01 / DRVMATCH-01 / SIDE30-BASE-01 / SIDE30-AB-01 | **拟定 ID**，入库时由 PM 定（入库骨架） | POLQA:374；DRV:346；FF:295 |
| DEC-S3-003 / S3-DSP-03 / S3-GEOM-01 | 竞品固件持有边界 / 对称串联无法偏转 / 几何 | PROP:241；PROP:114；POLQA:29 |
| DEC-S4-C9-RELEASE-01 / S4-CRITERION-01-FINAL / S4-F7-CLOSE-01 | FIRA 收益连体呈现 / T2 判据 / F7 闭合 | FIRB:190；PROP:43；HYB:133 |
| DEC-S5-BUDGET-L1-01 / EQ-O1-01 / SPL-CALIBER-01 / STEER-V1-01 / T2-CLOSURE-01 / V1-SCOPE-01 | 预算 / EQ+限幅 / SPL 口径 / 偏转独立立项 / T2 保守闭合 / v1 范围 | HYB:136；PROP:68；HYB:115；PROP:114；PROP:43；PROP:95 |
| DEC-S6-ALIGN-LEFT-01 / BEAM-POLARITY-CLOSURE-01 / FSRU1-RESCOPE-01 / M2-BOARD-PASS-01 / TEST1-METHOD-01 / TEST3-METHOD-01 | 左对齐 / 极性根因闭合 / F-SRU-1 再定范围 / M2 上板 PASS / Test1 方法 / Test3 方法 | DSPA:124；VPLAN:315；POLQA:213；PROP:39；INTAKE:515；FF:4 |
