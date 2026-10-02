# digest_D — sprint5/ + deliverables/ 记录读取摘要（只读，未改仓库）

> ⚠ 公开版说明（2026-10-02）：本摘录按写时原文照录，里面会出现已撤回或已被推翻的数字（如 d=30、17×/33×、1.5k/3k/6k 子带标签、86–144 MCPS、6.4×）。采信任何数字前，以 `sprint2/docs/decisions_log.md` 和 `sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md` 为准。

- 读取日期：2026-10-02；仓库 HEAD = 263e984（2026-10-02）；仓库全库仅 155 个 commit，**首个 commit = 4bf0f52（2026-06-02）**，故 06-02 之前无 git 历史，只能靠文件正文日期。
- 范围：`git ls-files sprint5 deliverables` = 54 个 tracked 文件（30 个 md = 638,972 B；24 个非 md = 522,351 B）。
- 引用约定：`path:line` = 当前工作树行号（HEAD 263e984）；`[F]` = 取自文件正文；`[G:hash]` = 取自 git commit message / 提交时间（非文件正文）；`旁证` = 范围外、明确标注。
- 可信度提醒：本范围多为 workflow 落地包 / 工单 / 材料，**文件头"状态"是写入时点快照**（见 §5-3），现状应以 decisions_log 为准；本摘要不替代 decisions_log。
- 本摘要不推断文本之外的内容；凡"未见"均指本范围 54 个文件中无记录。

---

## 0. 读了什么

### 0.1 md 文件（30 个，全部读完全文）

| # | path | bytes | 行数 | 读完？ | 首次入库 |
|---|---|---|---|---|---|
| 1 | deliverables/Gate1-baseline-array-validation-2026-05-26.md | 6,656 | 112 | 是 | 43aad40 2026-06-09 |
| 2 | deliverables/algorithm_validation/BEAM_POLARITY_CLOSURE_20260708.md | 9,691 | 96 | 是 | 4f87150 2026-07-08 |
| 3 | deliverables/algorithm_validation/EXP_CHMAP_AB.md | 8,028 | 100 | 是 | 99143fd 2026-07-09 |
| 4 | deliverables/algorithm_validation/EXP_COMPET_BEAM_VS_FREQ.md | 12,169 | 90 | 是 | b6bc5fe 2026-09-02 |
| 5 | deliverables/algorithm_validation/EXP_PLAN_20260701_BEAM_DEFECT.md | 14,794 | 185 | 是 | 4f87150 2026-07-08 |
| 6 | deliverables/algorithm_validation/EXP_STATIC_POL375.md | 9,912 | 112 | 是 | 02bc474 2026-07-07 |
| 7 | deliverables/algorithm_validation/EXP_STATIC_TXTEST.md | 7,171 | 89 | 是 | 4bf18b6 2026-07-02 |
| 8 | deliverables/algorithm_validation/OBS_OWNRIG_FRONT_SIDE_L0_REG20260902.md | 5,361 | 57 | 是 | b6bc5fe 2026-09-02 |
| 9 | deliverables/algorithm_validation/TEST1_WIRING_FINGERPRINT_FIELDLOG_20260629.md | 7,814 | 120 | 是 | 4f87150 2026-07-08 |
| 10 | sprint5/COMPUTE_LINE_CLOSURE_LANDING.md | 18,546 | 201 | 是 | d47ed19 2026-06-05 |
| 11 | sprint5/H1_FINAL_RULING_MATERIAL.md | 13,823 | 199 | 是 | 96245ef 2026-06-05 |
| 12 | sprint5/H1_R15_FIX_PACKAGE.md | 14,956 | 173 | 是 | 11a701d 2026-06-05 |
| 13 | sprint5/H1_R16_BUILDFIX_NOTE.md | 6,587 | 89 | 是 | ffb8bf2 2026-06-05 |
| 14 | sprint5/H1_WCET_WORKORDER.md | 15,198 | 165 | 是 | 2a50f51 2026-06-05 |
| 15 | sprint5/H2_PASSLINE_DERIVATION.md | 11,617 | 165 | 是 | 25e9253 2026-06-05（内容有误版，见 §5-7） |
| 16 | sprint5/H2_WORKORDER.md | 15,985 | 176 | 是 | 346b5ee 2026-06-05 |
| 17 | sprint5/NEXT_SESSION_BOOTSTRAP_H1.md | 5,390 | 57 | 是 | 3c86674 2026-06-05 |
| 18 | sprint5/SPL_CALIBER_LANDING.md | 13,507 | 142 | 是 | 6d0a0af 2026-06-05 |
| 19 | sprint5/V1_NARROWING_LANDING.md | 16,966 | 200 | 是 | 4d7e528 2026-06-05 |
| 20 | sprint5/audit/H2_MAP_PLACEMENT_ADJUDICATION.md | 10,977 | 154 | 是 | de59de8 2026-06-06 |
| 21 | sprint5/audit/H2_READING_ANOMALY_ANALYSIS.md | 15,490 | 210 | 是 | e5b26f9 2026-06-06 |
| 22 | sprint5/efficacy_sim/FOCUS_EFFICACY_REPORT.md | 11,778 | 155 | 是 | 1277f0a 2026-06-04 |
| 23 | sprint5/efficacy_sim/SIM_PLAN.md | 15,497 | 251 | 是 | 1277f0a 2026-06-04 |
| 24 | sprint5/eq_prd/EQ_PRD_DECISION_MATERIAL.md | 129,734 | 617 | 是（分 6 段读完 1-617；附录 JSON 在 :616 被截断，见 §5-5） | 97595af 2026-06-04 |
| 25 | sprint5/spl_redo/RE_SCOPE_EVIDENCE.md | 10,161 | 106 | 是 | 9bf2e0d 2026-06-05 |
| 26 | sprint5/spl_redo/SPL_MODEL_SPEC.md | 14,009 | 161 | 是 | 9bf2e0d 2026-06-05 |
| 27 | sprint5/spl_redo/SPL_REDO_REPORT_DRAFT.md | 10,814 | 124 | 是 | 9bf2e0d 2026-06-05 |
| 28 | sprint5/steering_scan/STEER2_NUMBER_FIX_DRAFT.md | 11,558 | 156 | 是 | 5d0e157 2026-06-04 |
| 29 | sprint5/steering_scan/STEERING_HEADROOM_SCAN.md | 179,343 | 910 | 是（分 9 段读完 1-910；附录 JSON 在 :909 被截断，见 §5-5） | 7ad6100 2026-06-04 |
| 30 | sprint5/steering_scan/V1_ROUTING_LANDING.md | 15,440 | 196 | 是 | 8e49cb2 2026-06-04 |

（`git log --follow --diff-filter=AR` 核过：30 个 md 均无改名/移动，首次入库 = 创建入库。）

### 0.2 非 md 文件（24 个，仅列名/类型，不读内容）

| path | 类型 | bytes | 首次入库 |
|---|---|---|---|
| deliverables/algorithm_validation/dispersion_envelope_20260617.png | PNG 图（按文件名对应 [G:8e419f4] message 所列"扩散角可行域"图） | 137,729 | 8e419f4 2026-06-25 |
| deliverables/algorithm_validation/m2_directivity_preview_20260617.png | PNG 图（按文件名对应"指向性预览"图） | 125,543 | 8e419f4 2026-06-25 |
| deliverables/algorithm_validation/test3_2kHz_beam_reference_20260617.png | PNG 图（按文件名对应"测3 2kHz 对账图"） | 65,027 | 8e419f4 2026-06-25 |
| sprint5/dsp/harness/h1_wcet_measure.c | C 源（H1 测量主体） | 24,452 | 2a50f51 2026-06-05 |
| sprint5/dsp/harness/h1_host_test.c | C 源（H1 桌面自验） | 7,240 | 2a50f51 2026-06-05 |
| sprint5/dsp/harness/h2_dma_isr_measure.c | C 源（H2 DMA/ISR 测量主体） | 21,425 | 346b5ee 2026-06-05 |
| sprint5/dsp/harness/h2_host_test.c | C 源（H2 桌面自验） | 7,177 | 346b5ee 2026-06-05 |
| sprint5/dsp/harness/h2_board_hooks_21569som.c | C 源（H2 板侧 4 hook，21569-SOM 板） | 27,879 | ba3dfe7 2026-06-06 |
| sprint5/dsp/harness/run_guard_check.sh | shell（guard-stub 语法检查） | 2,786 | ffb8bf2 2026-06-05 |
| sprint5/dsp/harness/guard_stub_inc/drivers/fir/adi_fir.h | C 头（BSP mock） | 1,592 | ffb8bf2 2026-06-05 |
| sprint5/dsp/harness/guard_stub_inc/services/pwr/adi_pwr.h | C 头（BSP mock） | 546 | ffb8bf2 2026-06-05 |
| sprint5/dsp/harness/guard_stub_inc/sys/cache.h | C 头（BSP mock） | 473 | ffb8bf2 2026-06-05 |
| sprint5/dsp/harness/guard_stub_inc/services/tmr/adi_tmr.h | C 头（BSP mock） | 1,837 | ba3dfe7 2026-06-06 |
| sprint5/dsp/harness/guard_stub_inc/services/dma/adi_mdma_2156x.h | C 头（BSP mock，R25 MDMA 符号修复） | 3,126 | 08ba7db 2026-06-06 |
| sprint5/efficacy_sim/focus_sim.py | Python（numpy 主轨仿真） | 20,711 | 1277f0a 2026-06-04 |
| sprint5/efficacy_sim/focus_sim_matlab.m | MATLAB（独立轨） | 7,343 | 1277f0a 2026-06-04 |
| sprint5/efficacy_sim/dualtrack_compare.py | Python（双轨比对） | 4,841 | 1277f0a 2026-06-04 |
| sprint5/efficacy_sim/dualtrack_compare.csv | CSV（118 行比对） | 8,003 | 1277f0a 2026-06-04 |
| sprint5/efficacy_sim/results_numpy.json | JSON | 18,119 | 1277f0a 2026-06-04 |
| sprint5/efficacy_sim/results_matlab.json | JSON | 7,385 | 1277f0a 2026-06-04 |
| sprint5/efficacy_sim/__pycache__/focus_sim.cpython-310.pyc | Python 字节码（被 tracked，见 §5-16） | 16,242 | 43aad40 2026-06-09 |
| sprint5/spl_redo/spl_model_numpy.py | Python（SPL 模型） | 7,414 | 9bf2e0d 2026-06-05 |
| sprint5/spl_redo/results_track1.json | JSON | 2,086 | 9bf2e0d 2026-06-05 |
| sprint5/spl_redo/results_track2.json | JSON | 3,375 | 9bf2e0d 2026-06-05 |

---

## 1. 文件清单（按首次入库日期排序）

格式：`首次入库日期 | path | 类型 | 一句话内容 | 状态(原文)`。"状态(原文)"摘自文件自身，多为写入时点状态。

| 首次入库 | path | 类型 | 一句话内容 | 状态(原文) |
|---|---|---|---|---|
| 2026-06-04 18:35 | sprint5/steering_scan/STEERING_HEADROOM_SCAN.md | workflow 扫描报告 + JSON 核验附录 | 可控音柱算力余量扫描：两条战略闸 FLAG-A（A/B 串联→角度偏转硬件物理不可达 [L1]，:54-58）与 FLAG-B（转向触发 d 重议 [L3]，:60-63）；优化表 HW-1/FRAME-1/ORCH 等量级全为 [L4/待验证] | :1「DRAFT — 待独立 critic 门，未呈 CTO 正式版」；:4-12 后加 4 条注记（R14 已闭/v1 路线/v1 收窄/算力线收官/R8、R9 修正台账） |
| 2026-06-04 19:58 | sprint5/steering_scan/STEER2_NUMBER_FIX_DRAFT.md | 数字诊断+修正稿 | CTO 质询"49x vs 2.9 MMAC/s"：49x=1500/30.56 为整路径桌面理想 1 cyc/MAC 余量，误挂聚焦增量；修正为 86–144 MCPS [L4]（:12-27，:105-134） | :1「DRAFT (no commit; critic gates, then lead patches)」 |
| 2026-06-04 21:56 | sprint5/steering_scan/V1_ROUTING_LANDING.md | 决策落地包 | DEC-S5-STEER-V1-01（v1=聚焦/分区）/DEC-S5-OPT-ORDER-01/DEC-S5-POLICY-3GATE-01；POLICY v1.8 §4B 三道关全文（:93-116）；CLAUDE.md 护栏 7（:126-143）；team_config Three-gate（:154-168） | :1「落地包 DRAFT（不 commit；critic R10 先门，lead 过门后 apply+commit）」；:3-4 后加算力线收官注 |
| 2026-06-04 22:41 | sprint5/eq_prd/EQ_PRD_DECISION_MATERIAL.md | PRD 决策材料 + JSON 核验附录 | item-3 EQ/限幅链：PRD 对 EQ 真沉默（:26,35）；选项表 O0–O3 不给推荐（:62-77）；保护限幅工程级 REQUIRED（:46-48） | :1「DRAFT — 三道关之第②关待过：独立 critic；第③关待过：CTO 常识审」；:3-5 后加"CTO 已裁 O1"注记 |
| 2026-06-04 22:55 | sprint5/efficacy_sim/FOCUS_EFFICACY_REPORT.md | 声学仿真报告 | v1 在轴聚焦/分区效能（numpy+MATLAB 双轨 118/118 一致）：由近场瑞利极限 R=2L²/λ 门控，有用增益仅高频近距（:14-16,101） | :1「（DRAFT）」；:3 裁定注记（2026-06-05）；:155「DRAFT，供 critic gate + CTO」 |
| 2026-06-04 22:55 | sprint5/efficacy_sim/SIM_PLAN.md | 仿真计划/规格 | 上述仿真的锁定输入、近场球面波模型、可行域门、验收锚 A1-A4、双轨纪律 | :1-5「PREREQUISITE #2 … GATE 1 SCREENING ONLY … NO efficacy verdict」 |
| 2026-06-05 10:44 | sprint5/V1_NARROWING_LANDING.md | 决策落地包 | DEC-S5-V1-SCOPE-01（v1=近场高频展区分区 2–5 m/≥4 kHz，车站 zoning 剔除，:28-45）+ DEC-S5-EQ-O1-01（:47-67）+ 后果重算 + PRD 改写块 | :1「落地包 DRAFT（不 commit；critic R13 …）」；:3-5 后加收官注 |
| 2026-06-05 12:00 | sprint5/H1_WCET_WORKORDER.md | 工单 | WO-S5-H1：聚焦增量同 build A/B + WCET + CCLK 复读 + 假绿门 + bench_main 接线块（:71-101）+ 读出 worksheet（:111-129） | :1「WORK ORDER DRAFT」；:3「〔H1 v2 已板跑：focus_only=49.03 MCPS[L1] …〕」 |
| 2026-06-05 13:17 | sprint5/H1_R15_FIX_PACKAGE.md | 修复包 | R15：ST1 跨态自检假 FAIL 的快照同态修复；MAC-2x 发现（120 samp→5.76 MMAC/s，:48-92）；三硬化（:94-125）；DEC-S5-H1-R15-01 | :3「DRAFT. NO commit; critic R15 gates」 |
| 2026-06-05 13:28 | sprint5/NEXT_SESSION_BOOTSTRAP_H1.md | 现场快照 | compact 前存档：R16 循环、重跑读数单、裁定队列、口径锁、流程法清单、agent 实例号、commit 链 | :1「…现场快照（2026-06-05，compact 前存档）」；:3-5「收官 … 本文以下为板跑前指引，存史」 |
| 2026-06-05 13:32 | sprint5/H1_R16_BUILDFIX_NOTE.md | 修复说明 | R16：CCES build 错（static 声明先后序）+ TARGET 守卫区桌面 gcc 失明 + guard-stub 语法检查及证伪（:40-60） | :3「DRAFT. NO commit; critic R16 gates」 |
| 2026-06-05 14:29 | sprint5/H1_FINAL_RULING_MATERIAL.md | 终裁材料（英文） | H1 v2 板跑全绿：focus_only 65,371 cyc=49.03 MCPS（:31）；WCET 实测部分 1.0002（:69-74）；整系统残余 1.46–2.14x [L4]（:128-130）；阈值 T1/T2/T3 中立呈（:164-173） | :4-5「Status: MATERIAL ONLY. Does NOT rule the formal threshold」 |
| 2026-06-05 14:51 | sprint5/COMPUTE_LINE_CLOSURE_LANDING.md | 收官归档 | 双槌（DEC-S5-BUDGET-L1-01，:25-37；DEC-S4-CRITERION-01-FINAL=T2 ≥1.5x，:38-47）+ 铁律五传播（:59-135）+ F0→H1 全链（:141-147）+ 官方数字表（:160-171）+ 残留登记（:179-188） | :1「DRAFT（不 commit；critic R18 先门）」 |
| 2026-06-05 15:26 | sprint5/H2_WORKORDER.md | 工单 | WO-S5-H2：DMA 争用（MDMA proxy，:28-36）+ ISR 抢占（:38-42）+ 联合 WCET；板侧 4 hook 规约（:64-85）；后增 R27 relabel（:126-130）/H2R（:132-137）/R26 解读边界（:139-143） | :1「WORK ORDER DRAFT」；:5「缘起：CTO 批 WO-S5-H2 = T2 系统侧闭合钥匙」 |
| 2026-06-05 16:16 | sprint5/H2_PASSLINE_DERIVATION.md | 推导链 | 210.19 MCPS=666.67−456.48 溯源（:9-23）+ scope 审计（双计/O1 worst/预留，:36-84）+ 机械 verdict 模板（:93-136） | :3「硬约束：此件不过 critic R21 门，板不开跑」 |
| 2026-06-05 16:28 | sprint5/spl_redo/RE_SCOPE_EVIDENCE.md | 证据包 | Re 层级：7.4/7.600 Ω=单元级，~15 Ω=通道级（:27-30,45-53） | :10「状态：DRAFT，待 critic R22 裁定口径」 |
| 2026-06-05 16:28 | sprint5/spl_redo/SPL_MODEL_SPEC.md | 模型规格 | 系统灵敏度两轨共吃规格：主口径@TOTAL 1W，阵列增益+10log10(16)，taper 公式（:35-76,101-124） | :10「状态：DRAFT，待 critic R22 裁定口径后两轨实现」 |
| 2026-06-05 16:28 | sprint5/spl_redo/SPL_REDO_REPORT_DRAFT.md | 报告 | 94.029145 dB @1W 总输入 [L2]；次口径 100.334861 dB @2.83 V/ch（:20-24）；比旧 117 低 ~23 dB（:32） | :10「状态：DRAFT — R22 未裁 / CTO 未裁 / 对外口径冻结中」；:3 后加 DEC-S5-SPL-CALIBER-01 裁定注 |
| 2026-06-05 16:56 | sprint5/SPL_CALIBER_LANDING.md | 决策落地包 | DEC-S5-SPL-CALIBER-01（内部 94.0 dB [L2 待坐实] 必带标注，对外冻结至 R3 L1，:13,21-38）+ 线③厂家函（:16,40-45）+ 旧 117 库 R7 分类（:97-112） | :1「落地包 DRAFT（不 commit；critic R23 门）」 |
| 2026-06-06 16:03 | sprint5/audit/H2_MAP_PLACEMENT_ADJUDICATION.md | 裁定/审计 | 板上 .map 证据：proxy 缓冲与 FIRA 工作集同居 L1 Block0→R24 FAIL（:53-62）→ #pragma section("seg_l1_block1") 修复（:68-89） | :6「NOT a board-result prediction. Pending critic gate before it counts. … No commit.」 |
| 2026-06-06 16:42 | sprint5/audit/H2_READING_ANOMALY_ANALYSIS.md | 读数异常分析 | H2 板读数两异常：base 低 71,120 cyc=H1 帧链多出 CRC32（:18-68）；inc_isr>(both_max−base) 因 ISR 实际率远高于 1 kHz（:71-150）；DMA 腿 0.038 MCPS [L1 CLEAN]（:146） | :5「Does NOT predict CTO final ruling」；:3「… No commit.」 |
| 2026-06-09 10:34 | deliverables/Gate1-baseline-array-validation-2026-05-26.md | 交付文档（历史归档） | Gate 1 审定（2026-05-26）：16 元/d=30 mm/Dolph−20 dB/4 子带 FAS；候选芯片 SC589 vs 21569；Gate 2 准入三条件（:81-85） | :3「历史归档/作废（PF-8，2026-05-29）… 不可作任何决策依据」；:15「✅ CTO 已批准（2026-05-26）」 |
| 2026-07-02 17:41 | deliverables/algorithm_validation/EXP_STATIC_TXTEST.md | 测试规程 | 静态缓冲差分指向性诊断，分 🅰固件撕裂 vs 🅱板 DAC 极性（2250 Hz 静态表） | :3「【已闭合 2026-07-08 → 见 BEAM_POLARITY_CLOSURE】… 🅰/🅱 均非根因」；:89 编于 2026-07-02 |
| 2026-07-07 18:37 | deliverables/algorithm_validation/EXP_STATIC_POL375.md | 测试规程 | 375 Hz 软件法逐路 solo + 成对相消测喇叭极性；分辨率只到通道级（:12-27）；电池纸盆兜底（:93-99） | :3「【结果 2026-07-08 → 见 BEAM_POLARITY_CLOSURE】… 物理 C2、C4 两对喇叭接反」；:112 编于 2026-07-07 |
| 2026-07-08 21:03 | deliverables/algorithm_validation/TEST1_WIRING_FINGERPRINT_FIELDLOG_20260629.md | 现场实测记录 | 2026-06-29：Test0 DSP 端 PASS；Test1 原法无效→逐路 solo 订正法 PASS；Test2/3 指向性方法订正（DEC-S6-TEST1/TEST3-METHOD-01） | :5「本记录待 critic 独立门 + CTO 常识审后方为权威；在此之前为 PM/测试员现场底稿」；:120 同 |
| 2026-07-08 21:03 | deliverables/algorithm_validation/EXP_PLAN_20260701_BEAM_DEFECT.md | 实验单 | 2026-07-01 台前定位"波束为何形不成"：实验 C（C0/C2/C1 逐对 300 Hz）/A（竞品背靠背）/B/D | :3「【已闭合 2026-07-08】… 本单存史」；:1「critic 过门定稿 v2」；:185 编于 2026-06-30 |
| 2026-07-08 21:03 | deliverables/algorithm_validation/BEAM_POLARITY_CLOSURE_20260708.md | 根因闭合报告 | "波束平"根因=物理 C2/C4 两对喇叭反极性；板/算法平反（限本 rig）；证据链 ①-⑤（:12-16）；仍开放 3 项（:63-74） | :3「状态:草案,待独立 critic + CTO 签」（但 [G:4f87150] 记 CTO 签，见 §5-4） |
| 2026-07-09 16:19 | deliverables/algorithm_validation/EXP_CHMAP_AB.md | 测试规程 | 选项 B 通道→物理位置映射修正的远场 A/B（M2_CHMAP_FIX；s_m2_chmap JTAG 活切，:41-50）；判据 30° 抑制 ≥6 dB（:79） | :5「诊断 build 门控 … CTO-gated」；:6「critic … CONDITIONAL 2MAJOR+2MINOR → 全修 → PASS」 |
| 2026-09-02 18:56 | deliverables/algorithm_validation/EXP_COMPET_BEAM_VS_FREQ.md | 实验设计 | 竞品 vs 我们 波束宽随频率对比（须扣单喇叭对照 E(θ,f)，:24-27）；判定矩阵（:58-66） | :3 入库复核注（4 数未落盘）；:90「v2（过 critic 整改）」；:11 写于 2026-07-15 |
| 2026-09-02 18:56 | deliverables/algorithm_validation/OBS_OWNRIG_FRONT_SIDE_L0_REG20260902.md | 观察值登记 | CTO 口述"自家 rig 正面读数 100/侧面约 80"按 [L0] 登记，不作规格，10 项条件全"未记录"（:26-39） | :3「[L0/条件未记录的读数，CTO 裁定按最低档]… 不作规格」；:57「独立 critic 过门后入库」 |
| 2026-06-25 16:26 | deliverables/algorithm_validation/*_20260617.png（3 张） | PNG | 随整机验证文档 sprint6/STAGE4_ALGORITHM_VALIDATION_TEST.md 入库的 3 张参考图 [G:8e419f4] | （无文本状态） |

### 1b. 文件头部日期 / 作者（按 §0.1 序号；"—"= 头部未标）

| # | 头部日期 | 头部作者/来源 | 出处 |
|---|---|---|---|
| 1 | 2026-05-26（v1.0.0，文档编号 DEL-GATE1-ITC-2026-0526-001，Trace TRACE-ITC-baseline-001） | 编制 Project Manager Agent（pm-itc-001）；评审 critic-itc-001（2 轮）；领域产出 agent-acoustic-sim-v1、agent-dsp-algo-v1 | Gate1-…md:7-16 |
| 2 | 2026-07-08 | PM | BEAM_POLARITY_CLOSURE_20260708.md:96 |
| 3 | 2026-07-09 | PM；critic claude-opus-4-8 过门 | EXP_CHMAP_AB.md:6,97-100 |
| 4 | 2026-07-15（写）/2026-09-02（入库复核注） | PM；独立 critic（claude-opus-4-8）；复核注 PM+独立 critic F-5 | EXP_COMPET_BEAM_VS_FREQ.md:3,11,79,90 |
| 5 | 2026-06-30 编，供 2026-07-01 台前 | PM lead；defect-hunt workflow wf_1ad922f8；critic claude-opus-4-8[1m] | EXP_PLAN_20260701_BEAM_DEFECT.md:7,185 |
| 6 | 2026-07-07 | PM；critic claude-opus-4-8（2026-07-07） | EXP_STATIC_POL375.md:8,108,112 |
| 7 | 2026-07-02 | board-output-defect-hunt workflow + PM；critic claude-opus-4-8 | EXP_STATIC_TXTEST.md:8,89 |
| 8 | 2026-09-02（CTO 口述日；登记日同） | 登记方 PM（lead）；口述人 CTO | OBS_OWNRIG…md:4,13,57 |
| 9 | 2026-06-29 | PM lead（现场底稿）/PM/测试员 | TEST1_WIRING…:5,120 |
| 10 | 缘起 2026-06-05（CTO 双槌裁定） | —（lead 落地包） | COMPUTE_LINE_CLOSURE_LANDING.md:3 |
| 11 | 2026-06-05 | dsp-algorithm teammate | H1_FINAL_RULING_MATERIAL.md:3 |
| 12 | — | —（缘起：CTO 批 fix(a)+R15；文中自称"本 teammate"） | H1_R15_FIX_PACKAGE.md:3-4 |
| 13 | — | —（缘起：CTO 退回 R15 包） | H1_R16_BUILDFIX_NOTE.md:3-4 |
| 14 | 缘起 DEC-S5-OPT-ORDER-02（CTO 2026-06-05） | — | H1_WCET_WORKORDER.md:7 |
| 15 | — | —（"CTO 派单线① 第一步"） | H2_PASSLINE_DERIVATION.md:3-6 |
| 16 | — | —（缘起：CTO 批 WO-S5-H2） | H2_WORKORDER.md:5 |
| 17 | 2026-06-05（compact 前存档） | — | NEXT_SESSION_BOOTSTRAP_H1.md:1 |
| 18 | 2026-06-05 | —（缘起：CTO 线②裁定） | SPL_CALIBER_LANDING.md:3 |
| 19 | 2026-06-05 | —（缘起：CTO 双裁定） | V1_NARROWING_LANDING.md:7 |
| 20 | 2026-06-06 | dsp-algorithm teammate | H2_MAP_PLACEMENT_ADJUDICATION.md:3 |
| 21 | 2026-06-06（Source @ HEAD de59de8） | dsp-algorithm teammate（harness author） | H2_READING_ANOMALY_ANALYSIS.md:3 |
| 22 | 2026-06-04（Sprint5 / efficacy_sim） | —（PREREQUISITE #2，CTO 令） | FOCUS_EFFICACY_REPORT.md:5 |
| 23 | 2026-06-04 | acoustic-simulation teammate | SIM_PLAN.md:8 |
| 24 | 2026-06-04（workflow eq-prd-material，28 agents；文档 ID DOC-S5-EQPRD-DECISION-01） | workflow + 内部 verifier | EQ_PRD_DECISION_MATERIAL.md:7,16 |
| 25 | 2026-06-05 | dsp-algorithm teammate（lead Line-2 派发） | RE_SCOPE_EVIDENCE.md:10 |
| 26 | 2026-06-05 | dsp-algorithm teammate（lead Line-2 派发） | SPL_MODEL_SPEC.md:10 |
| 27 | 2026-06-05 | 门-1 筛查 by critic（第三计算+两轨比对） | SPL_REDO_REPORT_DRAFT.md:10 |
| 28 | —（正文 :131 称 CTO 2026-06-04） | — | STEER2_NUMBER_FIX_DRAFT.md:131 |
| 29 | 2026-06-04（workflow steering-headroom-scan，31 agents） | workflow + critic R8 | STEERING_HEADROOM_SCAN.md:3,18 |
| 30 | 缘起 2026-06-04（CTO v1 路线三裁定） | — | V1_ROUTING_LANDING.md:6 |

---

## 2. 时间线事件（按日期；`[F]` 文件正文 / `[G]` git commit）

### 2.1 仓库建立之前（仅文件正文日期，git 无记录）

| 日期 | path:line | 事件 |
|---|---|---|
| 2026-05-26 | deliverables/Gate1-baseline-array-validation-2026-05-26.md:10,15,22 | [F] CTO 批准 Gate 1，任务状态 PASSED→HUMAN_REVIEW→COMPLETED |
| 2026-05-26 | 同上:24 | [F] 锁定基线：16 元均匀线阵/d=30 mm/孔径 0.45 m/−20 dB Dolph-Chebyshev/4 子带多相抽取 FAS/平台 ADI SHARC+（型号待 Gate 2） |
| 2026-05-26 | 同上:33-35,57 | [F] critic 第 1 轮 FAILED（1 BLOCKER+4 MAJOR+7 MINOR+5 INFO）→修订（含 CTO「指向性仅要求 ≥1 kHz」决策）→第 2 轮 PASSED_WITH_MINOR |
| 2026-05-26 | 同上:12-14,38 | [F] 参与 agent：pm-itc-001 / critic-itc-001 / agent-acoustic-sim-v1 / agent-dsp-algo-v1；资源 ≈$3–4（上限 $10），单任务 <10 min |
| 2026-05-26 | 同上:47-56 | [F] 指标（d=30 几何，已作废）：2 kHz −6 dB 宽 24.9°（均匀）/26.8°（Dolph−20，通过 ≤30°）；DI 2.0/4.8/7.6/10.5 dB（500/1k/2k/4k） |
| 2026-05-26 | 同上:63-71,83 | [F] 算力（解析估算，假设 1.5 MAC/周期）：方案 B 4 子带 FAS 79.9 MMAC/s；SC589 单核 cap 402→19.9%，21569 cap 892→9.0% |
| 2026-05-26 | 同上:81-85 | [F] Gate 2 准入条件：CCES 实机 profiling / ADI 芯片最终选型（SC589 vs 21569，不可逆采购）/ Phase-2 消声室实测（±3 dB） |
| 2026-05-29 | 同上:3 | [F] PF-8：d=30（Sprint2 视觉估测）被拆机实测 d=55 取代（DEC-S3-GEOM-01）；本文件降为历史归档/作废 |
| 2026-05-29/30 | sprint5/eq_prd/EQ_PRD_DECISION_MATERIAL.md:578,591 | [F] JY/T 标准 JPEG（文件 mtime 05-29 17:57；目录 05-30 15:41）；C8 审计 GAP-2：CTO 声明"标准 05-30 入库"与实际对不上，全文 PDF 缺 |

### 2.2 2026-06-04（sprint5 起点；一天 5 个 commit）

| 日期时间 | path:line / commit | 事件 |
|---|---|---|
| 06-04 | sprint5/steering_scan/STEERING_HEADROOM_SCAN.md:3-5 | [F] 扫描生成（31 agents）；启动时 R14 PENDING，现 CTO 已三连裁定（R14 CLOSED/判据复议/C9 松绑附诚实分母） |
| 06-04 18:35 | [G:7ad6100]；STEERING_HEADROOM_SCAN.md:11 | 首个 sprint5 commit（"新线 sprint5，critic R8 过门"）；R8：synthesizer 曾撤销 verifier 对 21.7 MCPS 错下界的纠正 |
| 06-04 | STEERING_HEADROOM_SCAN.md:54-63 | [F] FLAG-A（角度偏转硬件不可达，[L1]；DEC-S3-DSP-03 原文"必须改回 16ch 独立驱动硬件"，:57）；FLAG-B（fc(θ)=c/(d(1+abs(sinθ)))，θ=10°→5314 Hz，θ=30°→4158 Hz，触发 SC-S3-GEOM-01 d 重议） |
| 06-04 19:58 | [G:5d0e157]；sprint5/steering_scan/STEER2_NUMBER_FIX_DRAFT.md:12-27,105-134 | CTO 质询 49x vs 2.9 MMAC/s；49x/340x 退役；聚焦增量改 86–144 MCPS [L4]；R9 抓到修正稿自带 2.55x→应 2.31x（STEERING_HEADROOM_SCAN.md:12） |
| 06-04 21:56 | [G:8e49cb2]；sprint5/steering_scan/V1_ROUTING_LANDING.md:27-66 | CTO 三裁定：DEC-S5-STEER-V1-01（v1=聚焦/分区，角度偏转独立立项）/DEC-S5-OPT-ORDER-01/DEC-S5-POLICY-3GATE-01；R10 PASS |
| 06-04 | V1_ROUTING_LANDING.md:80-86,93-116,121 | [F] POLICY-PROV-001 v1.7→v1.8 新增 §4B 三道关；版本史：v1.6 铁律八/C9、v1.7 铁律九/C10 均 CTO 拍板 2026-06-02 |
| 06-04 | V1_ROUTING_LANDING.md:126-143,154-168 | [F] CLAUDE.md 安全护栏新增 item 7；.claude/team_config.md 新增 Three-gate 团队法 |
| 06-04 22:41 | [G:97595af]；sprint5/eq_prd/EQ_PRD_DECISION_MATERIAL.md:7-8,62-77 | EQ/限幅 PRD 决策材料（28 agents，R11）；O0–O3 无推荐 |
| 06-04 22:55 | [G:1277f0a]；sprint5/efficacy_sim/FOCUS_EFFICACY_REPORT.md:5,14-16,101 | 聚焦/分区声学疗效仿真（R12 PASS-WITH-MINOR）；净聚焦超额最高 ≈3.9 dB（6 kHz，2 m/5 m） |
| 06-04 | 旁证（范围外）[G:3359ff7] | "R14 三裁定落档"commit（R14 CLOSED/判据复议/C9 松绑）；[G:89bed86] CLAUDE.md 与 POLICY-PROV-001 首次入库追踪（commit message 称二者"自仓库建立即 untracked，v1.2–v1.8 修订仅存磁盘"） |

### 2.3 2026-06-05（算力线收官 + SPL 线 + H2 起步；13 个 commit）

| 日期时间 | path:line / commit | 事件 |
|---|---|---|
| 06-05 10:44 | [G:4d7e528]；sprint5/V1_NARROWING_LANDING.md:7,28-45,47-67 | CTO 双裁定：DEC-S5-V1-SCOPE-01（v1=近场高频展区分区，2–5 m/≥4 kHz；车站 zoning 剔除）+ DEC-S5-EQ-O1-01（master-bus 2–3 biquad + per-channel 限幅 T_k=T·w_k，29–60 MCPS [L4]）；R13 |
| 06-05 12:00 | [G:2a50f51]；sprint5/H1_WCET_WORKORDER.md:7,20-26,131-152 | WO-S5-H1（聚焦增量 + WCET harness）；DEC-S5-OPT-ORDER-02（harness+WCET 先，R3 次，HW-1 可选）；R14 |
| 06-05 | sprint5/NEXT_SESSION_BOOTSTRAP_H1.md:26,32 | [F] H1 首次板跑 FG zero_recovers=0（ST1 自检缺陷），数据 quarantined（590,137/524,727/65,410） |
| 06-05 13:17 | [G:11a701d]；sprint5/H1_R15_FIX_PACKAGE.md:9-35,48-92,94-125,127-157 | R15：快照同态修复；MAC-2x 发现（120 samp/帧→5.76 MMAC/s；86–144→173–288）；三硬化；DEC-S5-H1-R15-01 |
| 06-05 13:28 | [G:3c86674]；sprint5/NEXT_SESSION_BOOTSTRAP_H1.md:1-57 | compact 前现场快照（HEAD 11a701d，下一轮 R16，:8） |
| 06-05 13:32 | [G:ffb8bf2]；sprint5/H1_R16_BUILDFIX_NOTE.md:4,10-14,40-60 | R16：CCES 3 个 `s_h1_fa undefined`（声明先后序）；桌面 gcc 对 TARGET 守卫区失明；guard-stub 检查证伪（坏版 FAIL/修复版 PASS）；R16 PASS |
| 06-05（v2 板跑） | sprint5/H1_FINAL_RULING_MATERIAL.md:12-21,31,69-74 | [F] H1 v2 板跑全绿 [L1/EZKIT，CTO 2026-06-05]：focus_only=65,371 cyc=49.03 MCPS；cold/warm=1.000196；CCLK=1e9 |
| 06-05 14:29 | [G:96245ef]；H1_FINAL_RULING_MATERIAL.md:128-130,164-173 | 整系统残余 1.46–2.14x [L4]；T1/T2/T3 阈值选项中立呈 CTO；R17 |
| 06-05 14:51 | [G:d47ed19]；sprint5/COMPUTE_LINE_CLOSURE_LANDING.md:25-47,141-147 | 双槌：DEC-S5-BUDGET-L1-01（focus 86-144[L4]→49.03 MCPS[L1]）+ DEC-S4-CRITERION-01-FINAL（正式阈值=T2 ≥1.5x 带闭合条件）；"算力线正式收官"；R18 |
| 06-05 15:26 | [G:346b5ee]；sprint5/H2_WORKORDER.md:5,28-42,145-157 | WO-S5-H2 harness（MDMA proxy 3.072 MB/s；~1 kHz timer ISR）；阈值灵敏度：(io+irq+争用 WCET+I_cold)≤210.19 MCPS；R19 |
| 06-05 16:16/16:17 | [G:25e9253][G:b860a4d]；sprint5/H2_PASSLINE_DERIVATION.md:9-23,48-54,108 | 210.19 通过线推导；R21 双计裁定（ISR 真双计/DMA 非双计）；首版 25e9253 内容与 message 不符，1 分钟后 b860a4d 修 |
| 06-05 16:28 | [G:9bf2e0d]；sprint5/spl_redo/SPL_REDO_REPORT_DRAFT.md:20-24,32 | SPL 模型重做：94.029 dB @1W 总输入 [L2]，比旧 117 低 ~23 dB；R22 Re 口径裁 CLEAN（RE_SCOPE_EVIDENCE.md:27-30,45-53） |
| 06-05 16:56 | [G:6d0a0af]；sprint5/SPL_CALIBER_LANDING.md:13-16,21-38 | DEC-S5-SPL-CALIBER-01；PRD ≥90 dB 与 94.0 同口径，余量仅 ~4 dB（R23 FLAG）；线③厂家函准发（Xmax/热额定功率/送测条件） |

### 2.4 2026-06-06（H2 板跑审计 → 进入 sprint6/M1）

| 日期时间 | path:line / commit | 事件 |
|---|---|---|
| 06-06 10:02 | [G:ba3dfe7]（sprint5/dsp/harness/h2_board_hooks_21569som.c） | H2 板侧 4 hook 实现；R24 |
| 06-06 15:16 | [G:08ba7db]（sprint5/dsp/harness/guard_stub_inc/services/dma/adi_mdma_2156x.h） | MDMA 符号修复（"板上 9 error 清根"）；R25 |
| 06-06 16:03 | [G:de59de8]；sprint5/audit/H2_MAP_PLACEMENT_ADJUDICATION.md:10-16,53-62,68-89 | CTO 板上 .map.xml（CCES 2.12.1）：s_bh_src/dst/s_h2_fa 同居 L1 Block0（0x2403f0–0x26ffff）→R24 FAIL→pragma 钉 Block1；R26 |
| 06-06 16:42 | [G:e5b26f9]；sprint5/audit/H2_READING_ANOMALY_ANALYSIS.md:8-15,31-54,92-105,142-150 | H2 板读数 base=454,730/inc_dma=51/inc_isr=52,340/both_max=482,178/isr_count=1951；异常1=H1 链多 CRC32（71,120 cyc）；异常2=ISR 率 ~10–62 kHz 非 1 kHz；20.59 MCPS 须 relabel；DMA 腿 0.038 MCPS [L1 CLEAN]；R27 |
| 06-06 17:24 | [G:59ba0e5]；sprint5/H2_WORKORDER.md:132-137 | "三摊并行包"（O1 EQ 模块 sprint6/dsp/eq、H2R 重测、M1 调研 sprint6/dsp/audio/M1_SYMBOL_SURVEY.md）——sprint6 路径首次出现；H2R 读数 worksheet（R30）并入 H2_WORKORDER |
| 06-06 18:58 | [G:7bf2730]；sprint5/H1_WCET_WORKORDER.md:32；sprint5/H1_R15_FIX_PACKAGE.md:51 | M1 架构输入数据表（R33）；铁律五改锚：fira_tree.c:49-52 误引→fira_regression.c:195/h1_wcet_measure.c:235 |

### 2.5 2026-06-09 ～ 06-29（整机验证阶段）

| 日期 | path:line / commit | 事件 |
|---|---|---|
| 06-09 10:34 | [G:43aad40] | 批量入库（≈202 文件；message「M1完整loopback + M2 FIRA入环(12a5920) + softcfg重跑包 + 文档/sprint历史」）；Gate1 文档首次入 git；knowledge_base 与 *.zip 被 ignore（当前 .gitignore:2,5） |
| 06-17 | [G:8e419f4] message「reviewer … 2026-06-17」；3 张 PNG 文件名 *_20260617 | 整机算法有效性验证测试文档 v1（R61）与 3 张参考图；message：「CTO 接好真功放+16元阵列」「AD-EXKIT 跑 M2 broadside→DAC→4功放8路→16元对称对阵列」 |
| 06-25 16:26 | [G:8e419f4] | 上述文档 + 3 PNG 入库 |
| 06-29 | deliverables/algorithm_validation/TEST1_WIRING_FINGERPRINT_FIELDLOG_20260629.md:20-26 | [F] Test0 DSP 端 PASS（fira_inloop=1/setup_rc=0/valid=1/fg_beam_live=1/overrun=0；[L1/EZKIT AD-EXKIT]） |
| 06-29 | 同上:28-51 | [F] Test1 原法（全阵齐放贴近测）数据无效（近场相干干涉，非接线/算法故障） |
| 06-29 | 同上:53-76,78-82 | [F] Test1 订正法（逐路 solo，0.15 V 2 kHz 等幅外部驱动）PASS；DEC-S6-TEST1-METHOD-01 |
| 06-29 | 同上:92-117 | [F] Test2/3：1 m 近场（2 kHz 最后轴向极大值 0.99 m，远场 7.9 m）+纯单音手持→3 样本不可用；DEC-S6-TEST3-METHOD-01：≥3–4 m、粉噪/warble、Leq 10–30 s、三脚架 |

### 2.6 2026-06-30 ～ 07-22（"波束平"缺陷定位 → 根因闭合 → 选项 B）

| 日期 | path:line / commit | 事件 |
|---|---|---|
| 06-30 编/07-01 台前 | deliverables/algorithm_validation/EXP_PLAN_20260701_BEAM_DEFECT.md:185,5 | [F] 编于 2026-06-30，供 2026-07-01 台前：Test3 实测乱、竞品同场景 1 m 出 ~12 dB 对照；最可能根因=串联对极性反接 |
| 07-01 | deliverables/algorithm_validation/BEAM_POLARITY_CLOSURE_20260708.md:12,46-48 | [F] 交换实验：同台架只换 DSP 板→我们板平/竞品整套 rig 的板 16 dB；该"板 vs 板"差异至今未解释 |
| 07-02 | EXP_STATIC_TXTEST.md:89；[G:4bf18b6] | 静态缓冲差分指向性测试落库 |
| 07-07 | EXP_STATIC_POL375.md:8,112；[G:02bc474 18:37][G:5b98b18 19:45] | 375 Hz 极性测试落库；参考路改为 Phase A 实测居中路 c3（0x08）（:45,48） |
| 07-07 | BEAM_POLARITY_CLOSURE_20260708.md:13-14 | [F] 静态仍平 + JTAG 回读数字缓冲为正确同相 Dolph + SNR 64 dB⇒缺陷在数字缓冲之后；DAC 为单端 DAC1P–DAC8P（无 N 脚），翻极性只能在喇叭端 |
| 07-08 | 同上:15-16,24-25 | [F] 375 逐路声学：solo 全 87.5 dB；C7+{C0,C1,C3,C5,C6}=93.5 dB，C7+{C2,C4}=71 dB⇒C2/C4 反极性；翻正后 M2 波束 2 kHz 0°95/90°77（18 dB），1 kHz 95/86（9 dB），[L1，1 m 近场] |
| 07-08 21:03 | [G:4f87150]；同上:90-91 | CTO 签 DEC-S6-BEAM-POLARITY-CLOSURE-01；铁律四/五传播：DEC-S6-TEST1-METHOD-01"极性确认对"降级（solo-SPL 对极性天生瞎） |
| 07-09 16:13/16:19 | [G:c9321bc][G:99143fd]；EXP_CHMAP_AB.md:3,6-7,45-48；BEAM_POLARITY_CLOSURE_20260708.md:65-72 | 选项 B：通道→物理位置映射修正（宏 M2_CHMAP_FIX 默认关；s_m2_chmap B={4,5,6,7,0,1,2,3}）；预测[L2 numpy]：1 kHz 30° 抑制 −10.3→−23.1 dB，−6 dB 主瓣 25.7°→29.3°，峰值旁瓣 −9.67→−20 dB（EXP_CHMAP_AB.md:22-27） |
| 07-09～07-15 | EXP_COMPET_BEAM_VS_FREQ.md:3 | [F] 此期间有测量，但无单独原始记录（CTO D10 裁定 2026-09-02）；4 处带标数字（含"远场实测 [L1]"）"未落盘" |
| 07-15 | 同上:11,90 | [F] 竞品 vs 我们波束宽随频率对比实验设计 v2（critic：2 BLOCKER+5 MAJOR+7 MINOR 整改）；当时未入库 |
| 07-19 | [G:c3dcd50]；sprint5/steering_scan/V1_ROUTING_LANDING.md:145-149 | 治理减法① DEC-S6-GOVERNANCE-SLIM-01（critic 技能去重）；本范围仅涉及"八铁律→九铁律"锚点 |
| 07-20 | EXP_COMPET_BEAM_VS_FREQ.md:3 | [F] 引 testing/SKILL.md:89：选项 B 远场 A/B 至 07-20 仍"待测试员坐实" |
| 07-22 | deliverables/algorithm_validation/OBS_OWNRIG_FRONT_SIDE_L0_REG20260902.md:11 | [F]（CTO 口述）此后没有新的正式测试；停测原因"算法已见效" |

### 2.7 2026-09-02（Sprint 7 入库整理与 CTO 裁定）

| 日期时间 | path:line / commit | 事件 |
|---|---|---|
| 09-02 | OBS_OWNRIG_FRONT_SIDE_L0_REG20260902.md:3-5,11,20 | [F] CTO 口述"自家 rig 正面读数 100/侧面约 80"，按 [L0] 登记（DEC-S7-OBS-OWNRIG-01），不作规格 |
| 09-02 18:56 | [G:b6bc5fe]；EXP_COMPET_BEAM_VS_FREQ.md:3 | S7 A 入库整理：DEC-S7-SCOPE-01/OBS-OWNRIG-01/EXTINPUT-HIT9616-01；EXP_COMPET 首次进 git 并加复核注；critic CONDITIONAL→delta PASS |
| 09-02 22:31 | [G:c9c3f91]；EXP_COMPET_BEAM_VS_FREQ.md:3（末句） | S7 CTO 裁定：DEC-S7-RULINGS-01（14 条）+ DEC-S7-IMPL-01；D10：4 数维持"未落盘"、不升级 |

---

## 3. 前期环节线索

（"前期"= 本范围内能见到的 2026-06-04 之前及背景性记录；"未见"= 54 个文件中无记录。）

### 3.1 需求指标 / PRD — 有记录（均为转录/引用，未见 PRD 原文起草日期）
- 目标场景三类：博物馆讲解/车站广播/商场分区广播（sprint5/eq_prd/EQ_PRD_DECISION_MATERIAL.md:42；sprint5/V1_NARROWING_LANDING.md:138）；距离分档 博物馆 ~2–5 m、商场 ~3–8 m、车站 ~5–15 m（sprint5/efficacy_sim/FOCUS_EFFICACY_REPORT.md:114-118）。
- Gate 1（2026-05-26，d=30 时代，已作废）指标：−6 dB 波束宽 ≤30° @2 kHz（deliverables/Gate1-…md:54）；指向性仅要求 ≥1 kHz（CTO 决策，:34,57）；算力预算规则 可用=总值×0.85、单算法≤可用×0.70（:72）；端到端延迟约 2.0 ms/预算 20 ms（:74）。
- PRD（DOC-PRD-002 v2.4，EQ_PRD_DECISION_MATERIAL.md:26）相关行（均经 EQ_PRD/SPL_CALIBER 二手引用）：灵敏度 ≥90 dB SPL/1W/1m 正轴向（SPL_CALIBER_LANDING.md:15,82；06-04 时在 prd_update.md:172-173，EQ_PRD:553-554；06-05 后称 :183）；平坦度 ±4 dB（1k–8k，EQ_PRD:49,365）；JY/T 表 10：应备声压级 ≤75 dB(A)、不均匀度 ≤10 dB（1k/4k）、STIPA ≥0.50、GB 3096-2008（EQ_PRD:33,546）；端到端延迟 ≤20 ms（STEERING_HEADROOM_SCAN.md:143,372-373）与 DEC-S2-012 <30 ms（:365,369）并存；强指向频段降级 1k–6k（内部）/5k（对外）（EQ_PRD:377）。
- 算力判据演化：≥10x 退役→实时+余量→临时 1.0x→FINAL T2 ≥1.5x（COMPUTE_LINE_CLOSURE_LANDING.md:43-44）。
- v1 范围收窄后的新验收占位："高频近场净隔离 ≥X dB @消声室 L1"，X=OPEN（V1_NARROWING_LANDING.md:43-44,158）；保护限幅 REQUIRED、整形 EQ（V1_NARROWING_LANDING.md:47-67；EQ_PRD:46-48）。
- PRD 对 EQ/限幅/响度"真沉默"（EQ_PRD:26,35-36）。
- 整机指向性验收判据：0° 最大/±90° 落差 ≥12 dB/左右对称，且须远场重测（TEST1_WIRING_…:115；BEAM_POLARITY_CLOSURE_20260708.md:29,58）。
- 未见：客户需求原始文本、PRD 起草/评审日期、需求变更史。

### 3.2 竞品样机拆机 — 有记录（二手引用；拆机报告 full_teardown_v2.md 不在本范围）
- 拆机法律声明排除竞品专有 DSP 固件/算法二进制（EQ_PRD:31,464；引 full_teardown_v2.md:16）；PF-9 红线：禁从竞品 SPL 反推设计参数（EQ_PRD:607）。
- 拆机实测事实：A 区元 n 与 B 区元 (17−n) 串联成 8 路，串联 15 Ω [L1]，d=55 mm（STEERING_HEADROOM_SCAN.md:55；FOCUS_EFFICACY_REPORT.md:8；SIM_PLAN.md:29-31；RE_SCOPE_EVIDENCE.md:28,64）；单只喇叭 DC 7.4 Ω [L1]、铭牌 8 Ω/88 dB [L4]（RE_SCOPE_EVIDENCE.md:27-30；SPL_CALIBER_LANDING.md:109）；功放 ACM3128A（纯 D 类 BTL，无内置 DSP，EQ_PRD:32,486-506）；链路 ADAU1979→SPORT4→21569→ADAU1962A（12ch DAC 用 8ch）→8×ACM3128A→16 喇叭（STEERING_HEADROOM_SCAN.md:706）；竞品 0° SPL 106–111 dB（1–4 kHz，[L1 消声室]，EQ_PRD:602-604）。
- "拆机单元送测中，预计 2–4 周回报"（RE_SCOPE_EVIDENCE.md:38，引 full_teardown_v2.md:48）→ 后续 T/S 到库（SPL_CALIBER_LANDING.md:102）。
- PF-8（2026-05-29）：拆机实测 d=55 取代 d=30（Gate1-…md:3）。
- 竞品整机作对比台：07-01 交换实验（BEAM_POLARITY_CLOSURE_20260708.md:12,46-47）；竞品 1 m front-to-side 12–16 dB（EXP_PLAN_20260701_BEAM_DEFECT.md:5；EXP_STATIC_TXTEST.md:75；OBS_OWNRIG…md:44）；对比实验设计（EXP_COMPET_BEAM_VS_FREQ.md 全文）。
- 竞品固件包（SPON HIT-9616A12）登记仅见 [G:b6bc5fe] commit message，文件正文未提。
- 未见：拆机日期、拆机报告本体、竞品型号/来源。

### 3.3 方案 / 芯片选型 — 有记录（决策本体不在本范围）
- Gate 1 候选 ADSP-SC589 vs ADSP-21569，"型号待 Gate 2 定"（Gate1-…md:24,67-71,84）；SC589 cap 402、21569 cap 892（:67，解析估算）。
- DEC-S1-004 LOCKED 21569 单核，Gate 2 closed=irreversible；SC589 改芯片需独立 Gate-2（STEERING_HEADROOM_SCAN.md:116,128,685）。
- 功放：Plan A ACM3128A（无 DSP）vs Plan B TAS5825M（集成 DSP/EQ，DEC-S2-005），功放选型未锁（EQ_PRD:32,89,503-506；V1_NARROWING_LANDING.md:20,59）。
- 几何：DEC-S2-006 d=30 退役→d=55（DEC-S3-GEOM-01，SC-S3-GEOM-01 永久边界，STEERING_HEADROOM_SCAN.md:62,124）；N=16 LOCKED（:125）；拓扑 broadside-only（DEC-S3-DSP-03，:57）。
- 算法方案：4 子带 dyadic 树 + FIRA 加速器 + Dolph−20 dB 权重（Gate1:63-76；SIM_PLAN.md:35-67；COMPUTE_LINE_CLOSURE_LANDING.md:141-147）；v1=聚焦/分区、EQ=O1（V1_ROUTING_LANDING.md:27-41；V1_NARROWING_LANDING.md:28-67）。
- 未见：选型比较的原始评审、DEC-S1-004/Gate 2 的日期（见 §5-18）。

### 3.4 开发板 / EZKIT 采购与到货 — 采购/到货日期与记录：**未见**
- 仅见存在性旁证：板上 L1 数据 [L1/EZKIT]（STEERING_HEADROOM_SCAN.md:18；H1_FINAL_RULING_MATERIAL.md:12；COMPUTE_LINE_CLOSURE_LANDING.md:14,170）；板型 AD-EXKIT（TEST1_WIRING…:20）；板侧 hook 文件名含 21569som（sprint5/dsp/harness/h2_board_hooks_21569som.c，[G:ba3dfe7]）；CTO 板上 .map（CCES 2.12.1，2026-06-06，H2_MAP_PLACEMENT_ADJUDICATION.md:10）；CCLK 1.0e9 Hz（G6 闭，H2_PASSLINE_DERIVATION.md:14）。
- 整机链：[G:8e419f4] message「CTO 接好真功放+16元阵列…AD-EXKIT 跑 M2 broadside→DAC→4功放8路→16元对称对阵列」（reviewer 日期 2026-06-17）。
- 厂家函：线③（Xmax 大信号页/热额定功率/绝对电平送测条件）2026-06-05 准发（SPL_CALIBER_LANDING.md:16,40-45）；限幅阈值与转接板 PO 签署条件挂钩（EQ_PRD:48,123）。

### 3.5 GitHub / 论文调研、框架选择、资料入库
- GitHub/论文调研：**未见**（本范围无 github/arxiv/论文引用；`knowledge_base/papers/` 为空目录，范围外旁证 mtime 2026-05-26 15:02）。
- 框架/工具选择：仅有使用记录，无选型记录——numpy 主轨 + MATLAB R2026a 独立轨（Phased Array System Toolbox、Signal Processing、DSP System、Audio；FOCUS_EFFICACY_REPORT.md:7,103-108；SIM_PLAN.md:7,203-212）；CCES 2.12.1 + ADI 示例（STEERING_HEADROOM_SCAN.md:168；H2_MAP_PLACEMENT_ADJUDICATION.md:23-37,104-117）。
- 资料入库（有记录）：T/S 厂家/LEAP 测试 KB-DRV-TEST-001 走 iron-rule-7 路径（SPL_CALIBER_LANDING.md:42；RE_SCOPE_EVIDENCE.md:29,101-104）；JY/T 标准仅 1 张 JPEG、标准号占位、C8 审计认定"05-30 入库"声明与实际不符（EQ_PRD:93-98,570-593）；ADI 数据手册/FIRA 示例（EE408V02）/CCES 例程 .ldf 作证据源（H2_MAP_PLACEMENT_ADJUDICATION.md:23-37；STEERING_HEADROOM_SCAN.md:478-509,518-519）；literature-patent 角色被指派补 JY/T 全文与应急广播标准（EQ_PRD:97-98；V1_NARROWING_LANDING.md:190；NEXT_SESSION_BOOTSTRAP_H1.md:54）。
- 旁证（范围外）：当前 `.gitignore:2` 将 knowledge_base/ 整体忽略，故拆机/标准/ADI 资料无 git 入库日期；目录 mtime：measurements/papers 2026-05-26，standards 2026-05-30（JPEG 05-29），ezkit 2026-06-01，hardware_input 2026-06-05。

### 3.6 团队 / 治理搭建 — 有记录
- Gate 1 即有 PM/critic/声学/DSP 四 agent 的编号与 2 轮对抗评审、$10 预算护栏（Gate1-…md:12-16,33-38）。
- POLICY-PROV-001 版本史：v1.6（铁律八/C9）、v1.7（铁律九/C10）均 CTO 拍板 2026-06-02；v1.8（§4B 三道关）2026-06-04（V1_ROUTING_LANDING.md:80-86,93-122）；CLAUDE.md 护栏 7 与 team_config Three-gate（:126-143,154-168）。
- 制度教训入制度：critic §12 ST1-E、harness 探针/态隔离、PM cross-item 派单、TARGET 守卫区必跑 guard-stub（H1_R15_FIX_PACKAGE.md:94-125；H1_R16_BUILDFIX_NOTE.md:73-84；COMPUTE_LINE_CLOSURE_LANDING.md:153-158）；三道关实战诚实记录（:176-177）。
- critic 轮次 R8–R18（COMPUTE_LINE_CLOSURE_LANDING.md:149-151）；agent 实例号与流程法清单（NEXT_SESSION_BOOTSTRAP_H1.md:18,46-51）；角色：dsp-algorithm teammate（H1_FINAL_RULING_MATERIAL.md:3）、acoustic-simulation teammate（SIM_PLAN.md:8）、critic、literature-patent、PM lead、CTO、测试员（EXP_PLAN_20260701_BEAM_DEFECT.md:12；EXP_STATIC_TXTEST.md:85）。
- critic verdict 必带 `reviewer: critic @ <模型> / <日期>`（NEXT_SESSION_BOOTSTRAP_H1.md:50；各落库 commit message）。
- 旁证（范围外）：[G:89bed86] CLAUDE.md/POLICY 首次入库追踪（2026-06-04）；[G:c3dcd50] 2026-07-19 治理减法①（critic 技能去重，称"首次真正生效"见 §5-8）；[G:1656e02] 2026-07-20 治理减法 1+2。
- 未见：团队组建日期、Sprint 1–4 的角色/章程原文。

---

## 4. 阶段边界线索（日期 + 出处）

| 日期 | 边界 | 出处 |
|---|---|---|
| 2026-05-26 | Gate 1 通过：基线设计锁定（d=30 版），进入下一阶段；Gate 2 三条件待关 | deliverables/Gate1-…md:15,22,81-85 |
| 2026-05-29 | PF-8：d=30→d=55，Gate 1 文档作废（"Sprint2 视觉估测"→拆机实测） | deliverables/Gate1-…md:3 |
| 2026-06-02 | 仓库首个 commit（同日已有 FIRA 集成路线图/R14 前置分析 commit）；POLICY v1.6/v1.7 拍板 | [G:4bf0f52][G:9dd9e61]；V1_ROUTING_LANDING.md:80 |
| 2026-06-04 | R14 CLOSED/C9 松绑；新线 sprint5 开始；v1 路线（聚焦/分区）+ POLICY v1.8 三道关 | STEERING_HEADROOM_SCAN.md:3-5；V1_ROUTING_LANDING.md:17-19；[G:7ad6100] |
| 2026-06-05 | v1 收窄（近场高频展区分区）+ EQ=O1；H1 板跑 49.03 MCPS；"算力线正式收官"（F0→H1 链闭合）；SPL 线重做与口径裁定 | V1_NARROWING_LANDING.md:28-67；COMPUTE_LINE_CLOSURE_LANDING.md:25-55,141-147；SPL_CALIBER_LANDING.md:21-38 |
| 2026-06-06 | H2 板跑读数审计（T2 保守闭合，ISR 腿待重测）；"三摊并行包"与 M1 架构输入 → sprint5→sprint6（阶段 4 音频 M1/M2） | H2_READING_ANOMALY_ANALYSIS.md:142-167；[G:59ba0e5][G:7bf2730]；H2_WORKORDER.md:132-137 |
| 2026-06-17～06-29 | 真功放+16 元阵列整机验证（Test0–3）；测试方法订正 | [G:8e419f4]；TEST1_WIRING…:20-117 |
| 2026-07-01～07-08 | "波束平"缺陷定位→根因闭合（DEC-S6-BEAM-POLARITY-CLOSURE-01） | EXP_PLAN_20260701…:3-5；BEAM_POLARITY_CLOSURE_20260708.md:3,12-16 |
| 2026-07-09 | 选项 B（通道映射修正）落库，待远场 A/B | EXP_CHMAP_AB.md:3,6-7 |
| 2026-07-15 | 竞品对比实验设计（判竞品优势类别） | EXP_COMPET_BEAM_VS_FREQ.md:5,11 |
| 2026-07-22 | 最后一次正式测试（CTO 口述） | OBS_OWNRIG…md:11 |
| 2026-09-02 | Sprint 7：DEC-S7-SCOPE-01/OBS-OWNRIG-01/EXTINPUT-HIT9616-01/RULINGS-01/IMPL-01；sprint7/docs 提案被引用 | OBS_OWNRIG…md:4,53；EXP_COMPET…:3；[G:b6bc5fe][G:c9c3f91] |

编号线索：DEC-S1/S2/S3/S4/S5/S6/S7 前缀在本范围内均出现（DEC-S1-004、DEC-S2-005/006/007/008/012、DEC-S3-DSP-03/05、DEC-S3-GEOM-01、DEC-S4-*、DEC-S5-*、DEC-S6-*、DEC-S7-*）；sprint5 目录实际只覆盖 2026-06-04～06-06 三天（git 提交时间）。

---

## 5. 疑点（供手册作者避坑；均给出处）

1. **git 起点晚于早期事件**：全库首个 commit=2026-06-02（4bf0f52），而 Gate 1=05-26、PF-8=05-29；Gate1 文件"首次入库 06-09"是批量入库（43aad40，202 文件），不是产生日期。本范围 2026-05-26～05-30 的事件仅有文件正文日期（Gate1-…md:3,10；EQ_PRD:578,591）。
2. **原始资料不在 git**：当前 `.gitignore:2` 忽略 knowledge_base/（`git ls-files knowledge_base` 仅 8 个文件被强制 add）；拆机报告、T/S、标准 JPEG、ADI 数据手册/例程均无入库日期，本摘要对它们的内容全为二手引用。
3. **文件头状态多为写入时点快照**：COMPUTE_LINE_CLOSURE_LANDING.md:1、SPL_CALIBER_LANDING.md:1、V1_NARROWING_LANDING.md:1、V1_ROUTING_LANDING.md:1、H1_R15_FIX_PACKAGE.md:3、H1_R16_BUILDFIX_NOTE.md:3、H2_WORKORDER.md:1、H2_MAP_…:6、STEERING_HEADROOM_SCAN.md:1、EQ_PRD:1、FOCUS_EFFICACY_REPORT.md:150-151、SPL_REDO_REPORT_DRAFT.md:10 仍写"DRAFT/不 commit/critic 待"，但对应 commit message 均记 critic 已过门；NEXT_SESSION_BOOTSTRAP_H1.md:8（HEAD 11a701d、下一轮 R16）4 分钟后即过期。**引用现状请以 decisions_log 为准。**
4. **BEAM_POLARITY_CLOSURE_20260708.md:3,96 仍标"草案，待独立 critic + CTO 签"**，但 [G:4f87150] 记"CTO 签 + critic CONDITIONAL→PASS"；07-09 又被 c9321bc 改过（§5.1）而状态行未更新。
5. **两个核验 JSON 附录被截断**：EQ_PRD_DECISION_MATERIAL.md:616（CS-6 verdict 的 reasons 断在句中，后接游离 ``` ）——附录仅 17 条（F1-F6/SN-1..5/CS-1..6），而 :8 称 surviving findings 23，正文引用的 CO-1..CO-5（:64,68,102,110）附录中缺；STEERING_HEADROOM_SCAN.md:909 同样断在句中，附录 20 条且 `ORCH-1` 编号出现两次（:179 orchestration 维度，:879 constraints 维度），被驳回的 HW-5 仅见 :103，commit message 称"24 确认/1 驳回"[G:7ad6100]。
6. **H1_FINAL_RULING_MATERIAL.md:86-96 文本拼接损伤**：":86 … (iii) **ISR preemption** — bare-metal" 在句中截断，:87-96 接入另一段"The original §8 item-5 +10-50% rationale…"并以孤立的"系对原始 rationale 的失实概括，已撤。）"收尾（R17 MAJOR 修补痕迹）。
7. **H2_PASSLINE_DERIVATION.md 首版（25e9253）内容有误**：该版不含 F21-MAJOR-1（`git show 25e9253:…|grep -c F21-MAJOR-1`=0），commit message 却称 R21 修正已落；b860a4d（1 分钟后）才真正落地（含 2 处）。引用"首次入库"版本会得到半错的双计裁定（DMA/ISR 皆双计）；HEAD 版 :48-54 为正确口径。
8. **R15 硬化"ST1-E"的落地时点存疑**：H1_R15_FIX_PACKAGE.md:96-105 称已加到 agents/critic/skill.md 与 .claude/skills/critic/SKILL.md；而 [G:c3dcd50]（2026-07-19）message 称 canonical 的 ST1-E 门"卡在非法 YAML frontmatter、§12 正文其实缺失=静默失效→归位 §12（首次真正生效）"。故 06-05～07-19 间 critic 技能是否真的执行 ST1-E 无法从本范围确认；H1_R15_FIX_PACKAGE.md:99,104 的 :1108/:1132 行锚随 c3dcd50 已失效。
9. **退役/被取代数字仍留在正文**（顶注覆盖，正文逐字保留）：focus 86-144[L4]→173-288[L4]→49.03 MCPS[L1]；整系统残余 1.38–2.56→1.28–1.98→1.08–1.69→1.46–2.14x；49x/340x（STEER2_NUMBER_FIX_DRAFT.md:12-27）；2.88→5.76 MMAC/s（H1_R15_FIX_PACKAGE.md:48-92）；117→94.0 dB（SPL_REDO_REPORT_DRAFT.md:32）。**现行官方值**见 COMPUTE_LINE_CLOSURE_LANDING.md:160-171（3.07x 官方、3.13x 混 build 禁入、2.878x、49.03 MCPS、T2 ≥1.5x、1.46–2.14x、必连体 §8 未计入清单）。另：Gate1:67 的芯片 cap 402/892 与 STEER2_NUMBER_FIX_DRAFT.md:19 的"保守口径 1500 MMAC/s"互不对账，二者都是桌面理想口径，已被板上 CCLK 1.0e9/1000 MCPS 取代。
10. **对 prd_update.md 的行号引用漂移**：灵敏度行在 06-04 材料中是 :172-173（EQ_PRD:553-554），06-05 材料中是 :183（SPL_CALIBER_LANDING.md:15,82），而 STEERING_HEADROOM_SCAN.md:372-373 又把 :183 当"处理延迟 ≤20ms"行；各文件自述"行号随提交漂移"（V1_NARROWING_LANDING.md:198；SPL_CALIBER_LANDING.md:141）。手册引用须用锚字符串+commit 固定。
11. **指向性规格的频点锚不一致**：Gate 1 为 2 kHz −6 dB≤30°（Gate1:54，d=30）；d=55 之后的锚是 1 kHz 29.269°（SIM_PLAN.md:191；FOCUS_EFFICACY_REPORT.md:108；EXP_CHMAP_AB.md:23 "≤30 规格"）。手册须声明规格频点与几何版本。
12. **通道下标与宏的记号陷阱**：小写 c/slot（软件通道，mask 位）vs 大写 C（物理对中→边）——EXP_PLAN_20260701_BEAM_DEFECT.md:40 设计命名"c7=中心对、c0=最外对"，EXP_STATIC_POL375.md:45,48 实测"中间=c3（0x08）"，BEAM_POLARITY_CLOSURE:65,80-84 给全映射（sw0–3→物理 C4/C5/C6/C7，sw4–7→C0/C1/C2/C3；C2 反=mask 0x40，C4 反=mask 0x01，:36）。另"默认"有两义：宏 M2_CHMAP_FIX"默认关=字节等同"（BEAM_POLARITY:65；EXP_CHMAP_AB.md:5,37）vs 数组"B（修对，默认值）"（EXP_CHMAP_AB.md:48,74；EXP_COMPET_BEAM_VS_FREQ.md:22"默认 B"）。
13. **"自家 rig"一词含义不一**：BEAM_POLARITY_CLOSURE:74、EXP_COMPET:22 的 rig=我们板+我们功放+**竞品喇叭**，自家 16 元阵列极性"从未验过"；OBS_OWNRIG:20 把 07-08 数据称"自家 rig"，而 :38 又把 rig 组成列为"未记录"；[G:c9c3f91] D7 才裁定"接自家 16 元阵列"。
14. **07-01 交换实验至今无解释**（BEAM_POLARITY_CLOSURE:12,46-48）；竞品 front-to-side 来源不同：~12 dB（EXP_PLAN:5，06-30 前）vs 16 dB（BEAM_POLARITY:12；OBS:44，07-01）vs "12-16 dB"（EXP_STATIC_TXTEST:75）。
15. **无远场 L1 落盘数据**：所有指向性读数为 1 m 近场、方法敏感（BEAM_POLARITY:29,73）；EXP_COMPET:3 列出的 4 处带标数字（2k 我们 30° 抑制 13–16 dB/1k 近全向；1.9 dB 与 WNG −43 dB；1.5 dB 重复性；0.7 dB）"未落盘，出处待补"，CTO D10 维持；OBS_OWNRIG 的 100/80 只是 [L0]；07-09～15 测量无原始记录、07-22 后停测。正式指向性规格仍待 R3 消声室（BEAM_POLARITY:29,58；SPL_CALIBER_LANDING.md:15）。
16. **产出物命名/卫生**：SIM_PLAN.md:176-183 列 efficacy_sim.py/efficacy_sim_matlab.m/results/*.csv/plots/，实际 tracked 为 focus_sim.py/focus_sim_matlab.m/results_numpy.json/results_matlab.json/dualtrack_compare.csv（无 results/、plots/ 目录）；SIM_PLAN.md:249-251 末尾有游离代码围栏；`__pycache__/focus_sim.cpython-310.pyc` 被 tracked（43aad40），与当前 `.gitignore:8` 的 `__pycache__/` 冲突。
17. **H2 数字口径**：20.59 MCPS=(both_max−base)×750/1e6 实为 ~99.8% ISR@~10–62 kHz 膨胀值，"禁裸引"（H2_WORKORDER.md:126-130；H2_READING_ANOMALY_ANALYSIS.md:139-150）；DMA 腿 0.038 MCPS [L1 CLEAN]（:146）；ISR 腿须 H2R 重测，结果不在本范围（仅登记于 H2_WORKORDER.md:132-137）；H2 base 454,730 vs H1 nofocus 525,850 差 71,120=H1 链的 CRC32（H2_READING_ANOMALY_ANALYSIS.md:31-54），跨链不可直比。
18. **芯片锁定时序不清**：STEERING_HEADROOM_SCAN.md:116,685 称 DEC-S1-004 已 LOCKED 21569、Gate 2 closed=irreversible；而 Gate1-…md:24,84（05-26）仍写"型号待 Gate 2 定"、SC589 vs 21569 待选。锁定日期无法从本范围确定，需 decisions_log。
19. **延迟规格并存**：PRD 表 ≤20 ms（STEERING_HEADROOM_SCAN.md:143,372-373）vs DEC-S2-012 <30 ms 草案（:365,369）；FRAME=256 的 e2e≈20.5 ms 会破前者（:393-394）。
20. **SPL 余量与未决项**：94.0 dB 仅比 PRD ≥90 dB 高 ~4 dB 且绝对电平条件未坐实（SPL_CALIBER_LANDING.md:15）；SPL_REDO_REPORT_DRAFT.md:96 仍把 w8[0]>w8[1]（边元>次边）列为开放 flag，而 [G:9bf2e0d] 称已由 MATLAB chebwin(16,20) 复现为真 Dolph 特性——文件内未同步。
21. **PNG 与说明文档分离**：3 张图文件名日期 20260617、入库 06-25（[G:8e419f4]）；其说明文档 sprint6/STAGE4_ALGORITHM_VALIDATION_TEST.md 不在本范围（TEST1_WIRING…:3 引用）；按指令未读图内容。
22. **commit 时间 ≠ 文档时间**：TEST1_WIRING（06-29）、EXP_PLAN（06-30）直到 07-08 才入库（[G:4f87150] message 称"landed 上会话遗留未提交的 06-29 DEC"）；EXP_COMPET（07-15）到 09-02 才入库；Gate1（05-26）到 06-09。做时间线请以文内日期为准，git 日期只是入库日。
