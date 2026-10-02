# digest_B：sprint2/ + sprint4/ 全部 tracked .md 读后摘要（只读，不推断）

> ⚠ 公开版说明（2026-10-02）：本摘录按写时原文照录，里面会出现已撤回或已被推翻的数字（如 d=30、17×/33×、1.5k/3k/6k 子带标签、86–144 MCPS、6.4×）。采信任何数字前，以 `sprint2/docs/decisions_log.md` 和 `sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md` 为准。

- 仓库：`/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow`（读取日 2026-10-02，`git status` 干净，未改动仓库）
- 行号 = Read 工具 1 起算的文内行号；`[git]` = 来自 git 提交信息/时间（次级证据，低于文内原文）；`[文内]` = 文件正文原文。
- 本摘要跳过 `sprint2/docs/decisions_log.md`、`sprint2/docs/prd_update.md`（另一 agent 负责），其余 41 个 md 全部读完。

---

## 0. 读了什么

**读取方式**：逐文件整读（`dsp_design.md` 分 1-340 + 340-668 两段；`F7_R14_RULING_MATERIAL.md` 分 1-210 + 210-411 两段；其余一次读完），共 **41 个文件 / 599,389 B / 7,666 行**，全部读完，无截断。

**范围命令偏差（重要）**：指定命令 `git ls-files sprint2 sprint4 | grep '\.md$'` 实际返回 41 行（含两个要跳过的），**漏掉 2 个含中文文件名的 md**（git 默认把非 ASCII 路径加引号输出，行尾变成 `.md"`，grep 匹配不到）。用 `git -c core.quotepath=off ls-files` 后真实 tracked md = **43 个**，去掉 2 个跳过项 = 41 个。漏掉的两个已补读：第 5 行 `AC-WP01_1kHz波束宽度决策追溯.md`、第 6 行 `POLICY-PROV-001_数字来源分级制度.md`。

| # | path | bytes | 行数 | 读完? | 首次入库 hash 日期 | 末次 git 修改 |
|---|------|------:|-----:|:-----:|-------------------|--------------|
| 1 | sprint2/SPRINT2_CTO_REPORT.md | 9,206 | 145 | yes | 43aad40 2026-06-09 | 同 |
| 2 | sprint2/acoustic/1khz_optimization.md | 9,529 | 198 | yes | 43aad40 2026-06-09 | 同 |
| 3 | sprint2/acoustic/sweep_report.md | 20,392 | 389 | yes | 43aad40 2026-06-09 | 同 |
| 4 | sprint2/critic/critic_review.md | 30,954 | 236 | yes | 43aad40 2026-06-09 | 同 |
| 5 | sprint2/docs/AC-WP01_1kHz波束宽度决策追溯.md | 10,430 | 167 | yes | 4d7e528 2026-06-05 | 同 |
| 6 | sprint2/docs/POLICY-PROV-001_数字来源分级制度.md | 35,784 | 289 | yes | 89bed86 2026-06-04 | c3dcd50 2026-07-19 |
| 7 | sprint2/docs/PROJECT_HANDOVER.md | 20,408 | 233 | yes | 4d7e528 2026-06-05 | 33b1966 2026-09-26 |
| 8 | sprint2/docs/memory_update_proposal.md | 6,038 | 156 | yes | 4d7e528 2026-06-05 | 同 |
| 9 | sprint2/docs/simulation_coverage_audit.md | 28,251 | 230 | yes | 4d7e528 2026-06-05 | 33b1966 2026-09-26 |
| 10 | sprint2/docs/spec_change_latency.md | 4,447 | 78 | yes | 4d7e528 2026-06-05 | 同 |
| 11 | sprint2/docs/sprint3_kickoff_checklist.md | 8,866 | 119 | yes | 4d7e528 2026-06-05 | 同 |
| 12 | sprint2/docs/sprint3_procurement_kickoff.md | 7,698 | 141 | yes | 4d7e528 2026-06-05 | 同 |
| 13 | sprint2/docs/sprint3_retrofit_assessment.md | 21,541 | 270 | yes | 4d7e528 2026-06-05 | 同 |
| 14 | sprint2/docs/sprint3_teardown_workorder.md | 7,482 | 95 | yes | 4d7e528 2026-06-05 | 同 |
| 15 | sprint2/dsp/cces_template/README.md | 3,926 | 92 | yes | 43aad40 2026-06-09 | 同 |
| 16 | sprint2/dsp/dsp_design.md | 33,032 | 668 | yes | 43aad40 2026-06-09 | 同 |
| 17 | sprint2/hardware/bom_v0.md | 8,268 | 156 | yes | 43aad40 2026-06-09 | 同 |
| 18 | sprint2/hardware/hardware_brief.md | 18,092 | 286 | yes | 43aad40 2026-06-09 | 同 |
| 19 | sprint2/patent/formulas.md | 14,827 | 340 | yes | 43aad40 2026-06-09 | 同 |
| 20 | sprint2/patent/patent_map.md | 24,676 | 339 | yes | 43aad40 2026-06-09 | 同 |
| 21 | sprint4/audio_io_topology.md | 5,941 | 79 | yes | ecaa9d4 2026-06-03 | 同 |
| 22 | sprint4/core_only_migration_plan.md | 24,692 | 248 | yes | 3359ff7 2026-06-04 | 同 |
| 23 | sprint4/dsp/core_only/CROSS_BUILD_NOTES.md | 8,339 | 86 | yes | 4bf0f52 2026-06-02 | 同 |
| 24 | sprint4/dsp/core_only/S0S1_report.md | 6,249 | 77 | yes | 4bf0f52 2026-06-02 | 3359ff7 2026-06-04 |
| 25 | sprint4/dsp/core_only/bench/CCNT_source.md | 4,484 | 52 | yes | 4801575 2026-06-03 | 3359ff7 2026-06-04 |
| 26 | sprint4/dsp/core_only/bench/GRAFT_PLAN.md | 5,265 | 54 | yes | c12cca8 2026-06-02 | 3359ff7 2026-06-04 |
| 27 | sprint4/dsp/core_only/bench/R14_bitexact_rootcause.md | 4,249 | 52 | yes | 03d2172 2026-06-02 | 同 |
| 28 | sprint4/dsp/core_only/src/tree_filterbank.h.ERRATUM.md | 1,357 | 19 | yes | 33b1966 2026-09-26 | 同 |
| 29 | sprint4/dsp/fira/F1_mode_format_decision.md | 5,213 | 64 | yes | 7d24e6e 2026-06-03 | 同 |
| 30 | sprint4/dsp/fira/F3_F4_datapath_verified.md | 4,931 | 51 | yes | f80ee10 2026-06-03 | 同 |
| 31 | sprint4/dsp/fira/F4_BITEXACT_HANDOFF.md | 5,856 | 53 | yes | 46a9899 2026-06-04 | 3359ff7 2026-06-04 |
| 32 | sprint4/dsp/fira/F5_8CH_HANDOFF.md | 4,459 | 39 | yes | 22b4ef9 2026-06-04 | 3359ff7 2026-06-04 |
| 33 | sprint4/dsp/fira/F5_F7_PLAN.md | 23,259 | 218 | yes | 8b373f3 2026-06-04 | 3359ff7 2026-06-04 |
| 34 | sprint4/dsp/fira/F7_CLOSING_RECORDS.md | 18,390 | 248 | yes | 010eb35 2026-06-04 | 同 |
| 35 | sprint4/dsp/fira/F7_MARGIN_MATERIAL.md | 15,566 | 219 | yes | 93de6d9 2026-06-04 | 同 |
| 36 | sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md | 33,780 | 411 | yes | 06e4fc4 2026-06-04 | 3359ff7 2026-06-04 |
| 37 | sprint4/dsp/fira/FIRA_IMPL.md | 22,455 | 190 | yes | 8f24017 2026-06-03 | f80ee10 2026-06-03 |
| 38 | sprint4/dsp/fira/R14_RULING_PROPAGATION.md | 19,259 | 212 | yes | 3359ff7 2026-06-04 | 同 |
| 39 | sprint4/dsp/fira_integration_plan.md | 24,988 | 261 | yes | 9dd9e61 2026-06-02 | 同 |
| 40 | sprint4/dsp_migration_inventory.md | 6,773 | 85 | yes | 3359ff7 2026-06-04 | 同 |
| 41 | sprint4/iface_survey.md | 30,037 | 321 | yes | 493cefc 2026-06-03 | 06e4fc4 2026-06-04 |

**按指令跳过（未读）**：`sprint2/docs/decisions_log.md`（225,187 B / 1,322 行；git 首次入库 13be4b3 2026-06-02，该提交一次性加入 659 行；末次 3a008e8 2026-10-02）；`sprint2/docs/prd_update.md`（35,209 B / 417 行；首次 4d7e528 2026-06-05；末次 33b1966 2026-09-26）。以上 git 信息仅为存证，内容未读。

**非 md 文件（只列名与类型，未读正文；57 个）**
- `sprint2/acoustic/`（首次入库均 43aad40 2026-06-09）：Python 仿真脚本 `array_sweep.py`(34,522 B)、`diff_1khz_optimization.py`(21,953)、`rework_critic.py`(14,732)；数据 `sweep_results.csv`(4,666)；图 `candidate_1/2/3.png`、`candidates_fb_sll_vs_freq.png`、`competitor_fit_quality.png`、`diff_1khz_comparison.png`、`pareto.png`。
- `sprint2/docs/`：无非 md 文件（该目录的两个中文名文件是 md，即上表第 5、6 行）。
- `sprint2/dsp/`（43aad40）：Python `budget_calc.py`、`fir_design_verify.py`、`latency_calc.py`；C 头 `fir_coeffs.h`(14,361 B, 437 抽头旧核)；图 `reconstruction.png`；`cces_template/src/`：`beamformer.c/.h`、`config.h`、`fir.c/.h`、`fir_coeffs.h`、`main.c`。
- `sprint4/dsp/core_only/`（4bf0f52/c12cca8/03d2172，2026-06-02）：`MANIFEST.md5`、`Makefile`、`src/{tree_filterbank.c/.h, tfb_8ch.c/.h}`、`include/fir_coeffs_hb63.h`、`host/{gen_hb63.c, host_bitexact.c}`、`cces/dsp_main_core_only.c`、`bench/{bench_harness.c/.h, bench_main.c, gen_golden.c, golden_ref.h, gen_chirp_input.c, chirp_input.h(684,865 B)}`；二进制 `host_bitexact_sat`、`host_bitexact_unsat`(各 21,216 B)、`core_only_to_windows.tgz`(20,655 B)（这 3 个 3359ff7 2026-06-04 首次入库，同日 0383915 移出跟踪，43aad40 2026-06-09 又加回 [git]）。
- `sprint4/dsp/fira/`（2026-06-03/04）：C `fira_tree.c`(52,013 B)/`fira_tree.h`/`fira_regression.c`(42,522 B)/`gen_f5_goldens.c`；头 `fir_coeffs_q31.h`、`dolph_w8_q15.h`、`dolph_f5_goldens.h`；`dolph_w8_q15.csv`；Python `gen_dolph_w8.py`、`int_history_proof.py`、`residual_repro.py`、`residual_pack80_repro.py`、`decphase_fix_repro.py`；`.gitignore`。

---

## 1. 文件清单

排序按**文内日期**升序（git 首次入库日期是回填日期，不是创建日期，见 §5-2）。行格式：`首次入库日期 | path | 类型 | 一句话内容（含文内日期/作者） | 状态(原文)`。

### 1A. Sprint 2 交付物（文内 2026-05-26）

- 2026-06-09 | sprint2/SPRINT2_CTO_REPORT.md | 报告（Sprint 2 CTO 终汇报） | 文内 2026-05-26，Team Lead=PM Agent。主推荐 N=24/d=30/Dolph-30（经济备选 N=16/d=30），DSP 链 dyadic 树形 56.4 MMAC/s(27×)，BOM 估算，竞品对比，列 Gate 1 决策项(d、N、专利动作、CNIPA 核查)与 3 个技术风险；L3 事后加 PF-8 作废横幅 | 原文：L3「⚠️ 历史归档/作废（PF-8，2026-05-29）…不可作任何决策依据」；L7「四份产出最终『有条件 PASS』」；L111「Gate 1 决策（阻塞 Sprint 3，必须拍板）」
- 2026-06-09 | sprint2/acoustic/sweep_report.md | 报告（声学扫描+Critic 返工） | 文内 2026-05-26，AcousticSimulationAgent v1.0，版本 Sprint2-AC-WP01。竞品阵列反推(N=20/d=35/Dolph-20, RMS 2.84dB)、48 组 N×d×加权扫描、Pareto 17 解、3 候选；§7 返工：撤回 4 点插值竞品 BW(16/14.9/19.1°)，补前后比/旁瓣/量纲，更正栅瓣结论 | 原文：L3 PF-8 作废横幅；L389「返工版本：Sprint2-AC-WP01-rev2（Critic REWORK 修订）」
- 2026-06-09 | sprint2/acoustic/1khz_optimization.md | 报告（声学专题） | 文内 2026-05-26，Sprint 2 补做 #3；锁定基线 N=16/d=30/Dolph-20(L8)；1kHz BW 55.2°→「子带差分+相控混合」ε=0.01 得 35.4°/WNG+2dB；高阶差分 WNG −8~−30dB 不可量产；结论「有条件做」(L168-181) | 原文：L3 PF-8 作废横幅；L197-198「提交对象：Critic Agent → Team Lead；跨 Agent 依赖：延迟/算力增量待 DSP agent 复核；单元一致性/温漂待硬件 agent 评估」
- 2026-06-09 | sprint2/critic/critic_review.md | 评审（Critic 跨域，第一轮） | 文内 2026-05-26，编号 REV-SPRINT2-CROSS-001。声学/DSP 各 2 BLOCKER 打回 REWORK，专利/硬件有条件 PASS；跨域裁决 A-E(d=30 vs 35、N=16 vs 24、Boone 过度告警、BOM DSP 单价偏高、反推置信度)；MUST-FIX MF-1..9(L213-225) | 原文：L3 PF-8 作废横幅；L10「4 份产出无一可直接 PASS。2 份打回 REWORK，2 份有条件 PASS。存在 4 个 BLOCKER」
- 2026-06-09 | sprint2/dsp/dsp_design.md | 设计书（DSP） | 文内 v1.0.0 2026-05-26，作者 DSP 算法专家 Agent(agent-dsp-algo-v1)。FAS 子带波束形成：4 子带、分数延迟、算力/SRAM/TDM/定点；L466 起「Critic 返工修订」(×M 增益补偿、Kaiser 437 抽头、树形 56.4 MMAC/s=27×、N=16 vs 24)；L582 起补算端到端群延迟 12.53ms(footer v1.2.0 2026-05-26)。正文被事后改写为 d=55(L35,L108-117,L566)，无 PF-8 横幅 | 原文：L7「状态: 待 Critic 评审」
- 2026-06-09 | sprint2/dsp/cces_template/README.md | 工具说明（CCES 骨架使用说明） | 无日期/作者。骨架目录、系数(真实 scipy Kaiser Q15)、SPORT/DMA 待办；L65 config 已写 ARRAY_ELEMENT_SPACING_MM=55(L1 拆机/DEC-S3-GEOM-01)，说明经事后更新；L83-92 TODO 清单 | 原文：无状态行；L85-87 勾选「F-DSP-02 修复/F-DSP-01 修复」，L87「[ ] 将参考实现切换为 dyadic 树形半带抽取」未勾
- 2026-06-09 | sprint2/hardware/hardware_brief.md | 报告（硬件设计简报） | 文内 v0.1 2026-05-26，HardwareDesignAgent v1.0。16ch/24ch：ADAU1966A/1962A、TAS5825M(对比 TAS6424/MAX9744/TPA3255)、明纬 MSP-450-24 电源拓扑、24.576MHz TCXO、功耗三工况、DSP 结温 76.2°C>68°C 降额线(D.2) | 原文：L6「状态：初版评估，待 Critic 审核」；L286「状态：初版 | 送 Critic 评审」
- 2026-06-09 | sprint2/hardware/bom_v0.md | 报告（BOM 初版估算） | 文内 v0.1 2026-05-26，HardwareDesignAgent v1.0。16ch ¥1,169–2,065(中值~¥1,600)、24ch ¥1,452–2,631(中值~¥2,050)；DSP 单价 ¥350–500(Critic 后判偏高，见 §5) | 原文：L3「v0.1（估算版，仅用于成本评估，非采购依据）」；L155「状态：初版估算 | 送 Critic 评审」
- 2026-06-09 | sprint2/patent/patent_map.md | 调研（专利地图/技术情报） | 文内生成+检索 2026-05-26，agent.literature.patent，LIT-PAT-MAP-001。3 篇核心论文(Dolph 1946/Boone 2009/Zhang 2024)公式提炼，专利检索(Google Patents/Espacenet/USPTO/Justia，未用商业库 L117)，风险地图，5 个差异化方向，P0 行动(CNIPA 同族检索) | 原文：L9「免责声明：本报告为工程级技术情报参考，不构成法律意见」（无评审通过戳）
- 2026-06-09 | sprint2/patent/formulas.md | 调研（公式速查手册） | 文内 2026-05-26，agent.literature.patent，LIT-FORMULA-001。Dolph/Boone/Zhang 三论文公式+项目用途；d=55 算例为事后更新(L38,L120,L214-216,L327-331)；L140 仍写「本项目定向音柱为端射布局」 | 原文：L340「本文档为论文公式速查，不构成法律意见」（无状态戳）
- 2026-06-05 | sprint2/docs/memory_update_proposal.md | 提案（MEMORY 更新建议） | 文内 DOC-MEM-002 v1.0 2026-05-26，作者项目文档专家 Agent。提议写入 sprint2-baseline.md；PEND-001..004(d、N、专利启动、CNIPA 核查，¥5000-20000 待询价)；全部授权项⏳ | 原文：L9「⚠️ 建议草案，需 Team Lead（项目经理 Agent）+ CTO 确认后方可写入 MEMORY」；L3 PF-8 作废横幅
- 2026-06-05 | sprint2/docs/spec_change_latency.md | 规格变更草稿 | 文内 DOC-SPEC-CHG-001 v0.1 2026-05-26，PM 直接起草(L77)。端到端延迟 <5ms→<30ms(DEC-S2-012)，依据 12.53ms[解析/仿真,非实测]，人因依据，待客户对齐事项 | 原文：L7「状态：⏳ 草稿 — CTO 将据此与市场/客户对齐，对齐通过后正式生效」
- 2026-06-05 | sprint2/docs/sprint3_kickoff_checklist.md | 清单（Sprint 3 启动清单） | 文内 DOC-S3-KICKOFF-001 v1.0 2026-05-26，项目文档专家 Agent。S3-G1..G7 目标/验收、前置物、分 agent 任务、CTO 介入点、R1-R4 闭环路径、DoD；正文含 d=55/DEC-S3-GEOM-01 事后改写(L14,L43,L48,L94,L109)；EZKIT 行「⏳ 采购到货（Gate 2 已批）」(L45) | 原文：L7「前置依据：Gate 1 PASSED / Gate 2 CLOSED（decisions_log.md v1.1）」；L8「状态：待 Team Lead（项目经理 Agent）排期与资源到位确认」
- 2026-06-05 | sprint2/docs/sprint3_procurement_kickoff.md | 清单（采购+供应商模板+消声室预约） | 文内 DOC-S3-PROC-001 v1.0 2026-05-26，Team Lead 直接编制(L9,L140)。立即批准：EV-21569-EZKIT ¥4,000–6,000、CCES、ICE 仿真器；喇叭送样 3 家×16 只；暂缓：Codec/功放/电源；供应商询样邮件模板；消声室按 T−6 周倒推目标 2026-07-07；A1-A4 待评估项；含 d=55 事后改写(L40-42,L59,L98,L105) | 原文：无状态行；L129-136「Definition of Ready」6 项复选框全未勾
- 2026-06-05 | sprint2/docs/sprint3_retrofit_assessment.md | 评审/评估（硬件平台快速验证法） | 文内 DOC-S3-RETROFIT-001 v1.0 2026-05-26，HardwareDesignAgent v1.0。评估 CTO 的「保留竞品喇叭+功放+箱体，仅换 EV-21569-EZKIT+自制转接板」；几何不匹配、EZKIT 板载 12ch DAC 不足(L98-114)、转接板要点、净节省仅 2–4 周(L220-228)；基于 d=30(已作废) | 原文：L10「决策评估报告（仅技术评估，不采购、不下单、不改装）」；L240「评级：🟡 有条件推荐」；L269「送 Critic 评审后交 CTO」；L3 PF-8 作废横幅
- 2026-06-05 | sprint2/docs/sprint3_teardown_workorder.md | 执行单（拆机逆向确认工单 WO-S3-001） | 文内 v1.1，2026-05-26（v1.1 更新 2026-05-29），Team Lead 编制(L95)。6 项未知量 U1-U6 确认清单、法律红线、拆机前置；v1.1 状态升级：KB-HW-001 使 6/6「文档级闭环」(U2 N=16/d=55；U3 7.4Ω/15Ω/ACM3128A；U4 TDM；U5 主芯片含 DSP ADSP-21569KBCZ10) | 原文：L8「本工单是闸门：6 项未知量确认报告签署后，方可发『转接板设计 PO』」；L36-37「闸门技术上可解锁…仍需…正式签署」；L82「EZKIT 采购…✅ 批准」；L84「转接板设计 PO ⏸ 闸门锁定」

### 1B. 2026-05-28 ~ 05-30（分析审计、治理制度、交接）

- 2026-06-05 | sprint2/docs/AC-WP01_1kHz波束宽度决策追溯.md | 决策追溯（复盘纪要） | 文内 DOC-TRACE-AC-WP01 v1.0 2026-05-28，作者 PM Agent。1kHz −6dB 全角 BW=29.28°(d=55/N=16/Dolph-20，压线 0.72°)，4 种独立方法验证；14.63° 为半角误读(MATLAB `max()` 选中 −180° 端瓣)；超指向保留为 fallback，待消声室实测裁定；竞品 16°/36.6° 基准失效 | 原文：L7「状态：CLOSED（结论已三方+四法验证锁定）」
- 2026-06-05 | sprint2/docs/simulation_coverage_audit.md | 审计（Sprint 1-3 仿真完成度） | 文内 DOC-AUDIT-SIM-001，日期 2026-05-28，v2.3(版本链 v2.0 05-28 → v2.1-2.3 05-29)。A-G/①-⑤ 状态表、PF-1..PF-9「假性完成」清单、盲区、P0 优先级、P0 后可信清单 v2、§9 栅瓣判据(d=55: 3118/6236Hz)、§10 P0 场景几何修正 | 原文：L12「Critic 复核结论（REV-S3-SIMAUDIT，PASS_WITH_MINOR / HIGH）…可作 PCB 阶段决策依据」；L155「Critic REV-S3-P0 复核 PASS_WITH_MINOR / HIGH」
- 2026-06-04 | sprint2/docs/POLICY-PROV-001_数字来源分级制度.md | 制度（强制流程制度） | 文内 v1.8；v1.1=2026-05-28、v1.2/v1.3=2026-05-29、v1.5=2026-05-30（CTO 已审批）、v1.6/v1.7=2026-06-02（CTO 拍板）、v1.8=2026-06-04（CTO 拍板）；作者 PM Agent，v1.2/1.3/1.5 由 Critic 主拟。L0-L4 五级来源、九铁律、§4A 入库义务、§4B 三道关、C1-C10 强制检查 | 原文：L5「类型：强制流程制度（非技术决策）」；L8「生效范围：新决策强制执行；历史决策下次修订时回填」；L279「修订：本制度的修改须经 CTO 批准并记入 decisions_log」
- 2026-06-05 | sprint2/docs/PROJECT_HANDOVER.md | 交接总结 | 文内 DOC-HANDOVER-001 v1.2，2026-05-29（PF-8 几何统一）。「5 分钟接手」：阶段=Sprint 3 Phase 1-2 完成、卡在 PCB 前闸门；d=55 单一基线；Agent Team 清单；数据可信度清单；待决策项；Sprint 3 待办；四个教训；文档索引 | 原文：L7「权威来源…冲突时以这四份原始文档为准」；L14「零自动推进、等人工输入（拆机报告 + EZKIT 到货 + T/S 送测回报）」；L232「Critic REV-S3-HANDOVER-001 复核 PASS_WITH_MINOR」

### 1C. Sprint 4（文内 2026-06-02 ~ 06-04）

- 2026-06-04 | sprint4/dsp_migration_inventory.md | 盘点（4 子带树形 FIR 现有 C 资产） | 文内 DOC-S4-DSP-INV-01 2026-06-02，PM 直跑 grep。项1 设计存在、项2 C 核成型+桌面 bit-exact、项3 golden=tree_io_sat/unsat.csv，独立 MATLAB 定点参考不存在；缺口 G1-G5；结论「迁移=适配已有 C，不重写」 | 原文：L4「性质：纯盘点，不写新代码、不跑仿真」
- 2026-06-04 | sprint4/core_only_migration_plan.md | 计划（core-only G2–G5 适配计划） | 文内 DOC-S4-CORE-PLAN-01 2026-06-02，作者 dsp-algorithm teammate。8ch 包裹、63 抽头半带系数接线(禁接 437 抽头旧头)、骨架统一、.ldf/CCNT/SIMD；bit-exact 回归(sat/unsat 容差 0)；S0-S8 步骤(L202-212)；L191/L195/L209 事后加「≥10× 退役」注 | 原文：L4「纯计划文档…开工待 critic 核计划后」；L248「待 critic 核后开工」（S0S1_report.md:5 称「critic 已核可开工」）
- 2026-06-02 | sprint4/dsp/fira_integration_plan.md | 计划（FIRA 集成路线图） | 文内 DOC-S4-FIRA-PLAN-01 2026-06-02，dsp-algorithm teammate。FIRA 接口梳理、9 半带段×通道映射(8ch=72 channel/帧)、R14 风险点(signed-fractional vs UNSIGNED_INTEGER 为 HIGH)、F0-F8 路线、R14 回归方案(golden CRC 0x90556BC7) | 原文：L6「性质：分析 + 路线图。等 R1 板测完再开发 FIRA 版」；L28「FIRA 收益…R14 bit-exact 通过前不得写进任何选型依据」（git 提交信息称 critic PASS）
- 2026-06-02 | sprint4/dsp/core_only/S0S1_report.md | 报告（桌面首增量） | 文内 DOC-S4-CORE-S0S1-01 2026-06-02，dsp-algorithm 实现+PM 直跑收尾(dsp socket 死于报告前 L4)。host 双套(sat/unsat) bit-exact PASS，核 verbatim md5；R1 闭合数值判据(L46-60) | 原文：L7「本轮全部为 [L2 host 预验]…≠ 板上 [L1/EZKIT] bit-exact（待 S2）」；L71「达标判定：本轮=桌面首增量完成」
- 2026-06-02 | sprint4/dsp/core_only/CROSS_BUILD_NOTES.md | 工具说明（SHARC cross-build 预案） | 文内 DOC-S4-CROSS-01 2026-06-02，PM 直跑。本机 CCES 2.12.1 为 ARM-only、无 cc21k(Windows-only)；gcc 严格警告代理 0/0 [L2 代理]；SHARC 专项静态分析；台架零 debug checklist | 原文：L11-15「本机无法跑真·SHARC cross-build，故本文档不声称『已 0 错 0 警告交叉编译过』」；L80「真·SHARC cc21k 0/0…待台架 [L1/CCES-target]」
- 2026-06-02 | sprint4/dsp/core_only/bench/GRAFT_PLAN.md | 计划（嫁接计划+内存向量 harness） | 文内 DOC-S4-GRAFT-01 2026-06-02，PM 直跑。底座选 ADI 例程 ADSP21569_LED(L9-11)；harness host 预验 PASS；L29 事后加「>=10x 已退役」注 | 原文：L54「harness host 预验 sat/unsat bit-exact PASS [L2]；真 SHARC 0/0 + 真 CCNT + 板上 bit-exact 待台架 [L1/EZKIT]」
- 2026-06-02 | sprint4/dsp/core_only/bench/R14_bitexact_rootcause.md | 报告（上板 bit-exact 失败根因+修复） | 文内 DOC-S4-R14-RC-01 2026-06-02，PM 直跑。首次上板 crc32=0x21a3d598≠golden 0x90556BC7(L9)；根因=运行期 chirp 的 double 在 `-double-size-32` 下输入分叉(L21-24)；修=冻结 `CHIRP_INPUT[]` | 原文：L52「target 重跑待台架（二值判据 crc==0x90556BC7）」
- 2026-06-03 | sprint4/dsp/core_only/bench/CCNT_source.md | 工具说明（cycle 计数出处+实现+验证） | 文内 DOC-S4-CCNT-01 2026-06-03。`clock()`=CCLK 周期(ADI 例程 FIR_Throughput_21569.c 出处)；L4 记「S2 板上 bit-exact 已 PASS（crc=0x90556BC7，[L1/EZKIT]）」；L41(2026-06-04)加 FIRA 测量「严禁循环内断点」；L48 加「>=10x 已退役」注 | 原文：L3-4 日期与背景行；无独立状态戳
- 2026-06-03 | sprint4/dsp/fira/FIRA_IMPL.md | 执行单/runbook（FIRA 集成实现说明） | 文内 DOC-S4-FIRA-IMPL-01 2026-06-03，dsp-algorithm teammate。真 Legacy API 草案；F0/F1 已闭；F2-F8 台架 runbook(L84-94)；R14 Q 格式转换点表(L110-117)；F2 载体=CTO Windows 上的 `bench_core_only`(L70-76) | 原文：L11-23「诚实边界（硬约束，禁删，违者 BLOCKER）」草案未编译；L190「草案未编译/未板验·F2-F8 待台架回填」
- 2026-06-03 | sprint4/audio_io_topology.md | 报告（音频 I/O 拓扑，文档事实+gaps） | 文内 DOC-S4-IO-01 2026-06-03，PM 直跑。板=AD-EXKIT V2.1+ADSP-21569-SOM+AD2428W-SOM；ADAU1979(4ch ADC)→SPORT4 TDM→21569→ADAU1962A(12ch DAC，用 8ch)→8 路功放→16 喇叭；8 slot×32bit@48k BCLK 12.288MHz；gaps G-IO1..7 | 原文：L5「红线：只录文档有的…文档没有的列 gap」；L79「7 项 gap 明列待工程师确认，未凭印象补」
- 2026-06-03 | sprint4/iface_survey.md | 调研（系统接口普查 5 段信号链） | 文内 DOC-S4-IFACE-SURVEY-01 2026-06-03，owner dsp-algorithm teammate。SPORT/FIRA/SRU/TWI/PDMA/SPU/pwr 接口表+gaps G1-G9；L225/L229/L297 为 2026-06-04 加的「adi_pwr 由 initComponents 代办」证伪注(铁律五加标)；L308 G6 已闭合(CCLK=1,000,000,000 Hz [L1/EZKIT]) | 原文：L10「诚实声明（ARM-proxy / 必读，置顶）」；L321「本单仅普查，不跑仿真/不写集成代码」
- 2026-06-03 | sprint4/dsp/fira/F1_mode_format_decision.md | 报告（FIRA F1 决策） | 文内 DOC-S4-FIRA-F1-01 2026-06-03，PM 直跑。G1 闭合（CTO 提供 `adi_fir_legacy_2156x.h` 归档，C8/铁律六）；G2 闭合（例程=Legacy，定点格式走运行时 FixedPointEnable）；Legacy 推荐(纠正 IFACE-SURVEY 的 ACM 倾向) | 原文：L64「G1 闭合…G2 闭合…Legacy 推荐…F2-F8 + R14 命门待台架」
- 2026-06-03 | sprint4/dsp/fira/F3_F4_datapath_verified.md | 报告（FIRA 定点数据通路 HW 手册实证） | 文内 DOC-S4-FIRA-DP-01 2026-06-03，PM 直跑。HW Reference §38-10：80-bit 精确整数 MAC、3×32-bit 写回、无内建右移、signed-fractional 需 ×2+decimate；修正「Q15 符号扩展」假设(触发=「顾问针 1」) | 原文：L51「C9 维持」
- 2026-06-04 | sprint4/dsp/fira/F4_BITEXACT_HANDOFF.md | 交接（F4 里程碑 session handoff） | 文内 2026-06-04，PM(lead, claude-opus-4-8)。「R14 关键里程碑：FIRA 单通道子带定点 bit-exact（L1 板上，commit 9d9fbec）」，板上四证(0x2E0D8C6E)，六轮独立 critic 拦截清单，commit 链 | 原文：L1 横幅「状态更新 2026-06-04：R14 已 CLOSED…本文以下为写时口径，存史」；L5「状态：CTO 已确认口径」
- 2026-06-04 | sprint4/dsp/fira/F5_F7_PLAN.md | 计划（F5+F7 规划草案） | 文内 2026-06-04，dsp-algorithm(claude-opus-4-8)。F5-A 链×8、F5-B 删求和 wrapper、F5-C 8 路 Dolph-Cheb −20dB 权重表、F7 含开销 cycle 实测；OPEN-A1(8 路=8 对对称元，L200) | 原文：L1 R14 CLOSED 横幅；L5「状态：DRAFT，待 critic 门禁」（git 提交信息 8b373f3 称「critic 两轮 PASS」）
- 2026-06-04 | sprint4/dsp/fira/F5_8CH_HANDOFF.md | 交接（F5 里程碑） | 文内 2026-06-04，PM。「8ch 子带定点 bit-exact 上板达成（L1，commit 44a99e8）」，8 锚命中，权重表 [28404,16525,20371,24031,27287,29934,31802,32768]，8 通道→16 单元={c,15−c}对称配对[L1/硬件实测]，流程偏差→Commit discipline 硬规 | 原文：L1 R14 CLOSED 横幅；L5「状态：CTO 已确认口径」
- 2026-06-04 | sprint4/dsp/fira/F7_MARGIN_MATERIAL.md | 材料（F7 core-only 板跑裕量，呈 CTO 裁定） | 文内 2026-06-04，dsp-algorithm。core-only：cyc_8ch_frame=1,451,030、1088.66 MCPS、8ch 裕量 0.92×、16ch 0.55×（按 1GHz[L2/datasheet]，CCLK 未测）；四个 R14 选项 | 原文：L4「Status: MATERIAL ONLY. This document does NOT decide R14 closure or relax C9」
- 2026-06-04 | sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md | 材料（F7 R14/C9 终版裁定材料 v2，FIRA build） | 文内 2026-06-04，dsp-algorithm。g_f7_cyc_8ch_fira=463,273、CCLK=1e9 实测(G6 关)、裕量 2.878×[L1-derived]、官方加速比 3.07×(3.13× 退役)；Addendum A 尾读预期、Addendum B 五项未计入(43–379 MCPS，整系统残余 1.38–2.56× [L4]) | 原文：L1「CTO RULES, material does not rule」；L199「STATUS UPDATE 2026-06-04: THE CTO HAS NOW RULED」；L247「critic R5 gated CONDITIONAL 0/1/1…reviewer: critic @ claude-opus-4-8 / 2026-06-04」
- 2026-06-04 | sprint4/dsp/fira/F7_CLOSING_RECORDS.md | 草稿（回答 CTO 三问+收官记录草稿） | 无头部日期（正文各板值标「CTO-measured 2026-06-04」）。Q1 analyze/synth 拆分存在证明、Q2 官方加速比 3.07×、Q3 摊薄估算；DRAFT(a) DEC-S4-F7-CLOSE-01 条文；DRAFT(b) 对 RULING_MATERIAL 的改写块 | 原文：L3「DRAFT ONLY. Not committed; independent critic gates first, then lead commits.」（已被提交 010eb35，状态行未更新）
- 2026-06-04 | sprint4/dsp/fira/R14_RULING_PROPAGATION.md | 执行单（R14 三裁定条目+铁律五全库传播） | 文内「缘起：CTO 正式三裁定 2026-06-04」(L4)。(a) 三条 DEC：DEC-S4-R14-RULING-01(R14 CLOSED)、DEC-S4-CRITERION-01(≥10× 退役，临时下限 ≥1.0×)、DEC-S4-C9-RELEASE-01(C9 松绑附诚实分母)；(b) 全库命中分类 LIVE/HISTORICAL+change blocks；(c) 2.878× 连体呈现守卫 | 原文：L3「DRAFT ONLY. 不 commit；critic R7 先门。lead 过门后 apply + commit。」（已被提交 3359ff7；提交信息称 critic R7 CONDITIONAL 0/1/1 预豁免落地后放行）

### 1D. 后续勘误（2026-09-26）

- 2026-09-26 | sprint4/dsp/core_only/src/tree_filterbank.h.ERRATUM.md | 勘误（冻结件旁注） | 文内 2026-09-26，DEC-S7-RETRACT-SUBBAND-01。冻结头 `tree_filterbank.h` 的「交叉点 12k/6k/3k/1.5k」是错的，[L2 host] 复算实际分界 3k/6k/12k(1kHz 在 SB0 内)；detail 子带=未延时对齐的梳状残差，不可按子带加不同权重；不改冻结头（md5 7397ff0e…） | 原文：L3「⚠【勘误 2026-09-26 · DEC-S7-RETRACT-SUBBAND-01】」；L6「[L2 host]，不是 L1 实测」；全文见 sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md(L19，范围外)

---

## 2. 时间线事件（文内日期，按时间升序）

**无日期但早于 2026-05-26**
- 无日期 | sprint2/docs/simulation_coverage_audit.md:8 | 「无 sprint1 目录（Sprint 1 仅 spec，无仿真脚本）」
- 无日期 | sprint2/docs/PROJECT_HANDOVER.md:62 | Sprint 1 ✅：技术路线锁定、指向性频段需求(DEC-S1-002)、Gate 1 基线验证、芯片选型(DEC-S1-004，见 POLICY-PROV-001:17)
- 无日期 | sprint2/docs/PROJECT_HANDOVER.md:63 | Sprint 2 ✅：6-agent+2 轮 Critic；Gate 1 PASSED/Gate 2 CLOSED；N/d/加权/子带锁定；竞品反推

**2026-05-26（Sprint 2 交付物与 Sprint 3 启动包，同日）**
- 2026-05-26 | sprint2/SPRINT2_CTO_REPORT.md:1,5,7 | Sprint 2 CTO 终汇报（Team Lead=PM Agent）；Critic 两轮，首轮声学/DSP 各 2 BLOCKER 被打回，返工后「四份产出最终有条件 PASS」
- 2026-05-26 | sprint2/SPRINT2_CTO_REPORT.md:111-123 | 向 CTO 提 Gate 1 四项决策（d、N、专利动作、CNIPA 核查）+3 个技术风险（树形 C 未落地、群延迟 4.54ms、绝对 SPL 盲区）
- 2026-05-26 | sprint2/critic/critic_review.md:5-10 | REV-SPRINT2-CROSS-001：4 个 BLOCKER，声学/DSP 打回 REWORK，专利/硬件有条件 PASS；裁决 A(d)、B(N) 须 CTO 在 Gate 1 拍板(L184-195,L232)
- 2026-05-26 | sprint2/acoustic/sweep_report.md:6-8,260-389 | 声学扫描报告 + Critic 返工 rev2（撤回竞品 BW 插值值）
- 2026-05-26 | sprint2/acoustic/1khz_optimization.md:6-8 | 「Sprint 2 补做 #3」1kHz 强指向优化；锁定基线 N=16/d=30/Dolph-20
- 2026-05-26 | sprint2/dsp/dsp_design.md:4-7,667-668 | DSP 设计书 v1.0.0 →（返工）→ v1.2.0；补算树形端到端群延迟 12.53ms(L582-662)，方案 D 建议放宽 ≤5ms
- 2026-05-26 | sprint2/docs/spec_change_latency.md:5-18 | 草拟延迟规格变更 <5ms→<30ms（DEC-S2-012），待市场/客户对齐
- 2026-05-26 | sprint2/hardware/hardware_brief.md:5 与 bom_v0.md:4 | 硬件简报 v0.1、BOM v0.1 估算
- 2026-05-26 | sprint2/patent/patent_map.md:5,8 与 formulas.md:5 | 专利检索与三论文公式提炼（检索时间同日）
- 2026-05-26 | sprint2/docs/memory_update_proposal.md:8-9 | MEMORY 更新提案 DOC-MEM-002（待 TL+CTO 确认）
- 2026-05-26 | sprint2/docs/sprint3_kickoff_checklist.md:6-8 | Sprint 3 启动清单；前置「Gate 1 PASSED / Gate 2 CLOSED」(L7)
- 2026-05-26 | sprint2/docs/sprint3_procurement_kickoff.md:4-9,19,89-101 | 采购清单（DEC-S2-014 分级采购）：P1 EV-21569-EZKIT ¥4,000–6,000、货期 4–8 周；消声室按 T−6 周倒推，目标首测 ≈2026-07-07(L91)
- 2026-05-26 | sprint2/docs/sprint3_retrofit_assessment.md:8-20,240 | 评估 CTO 的「硬件平台快速验证法」→「🟡 有条件推荐（作为低成本探针，不作为主验证路径）」
- 2026-05-26 | sprint2/docs/sprint3_teardown_workorder.md:3,82-84 | 拆机工单 WO-S3-001 v1.0；EZKIT 采购「可立即下单…✅ 批准」，转接板 PO「⏸ 闸门锁定」

**2026-05-28**
- 2026-05-28 | sprint2/docs/AC-WP01_1kHz波束宽度决策追溯.md:152-162 | 同日事件链：AC-WP01 初版报 14.63°(半角误读)→CTO 一度拟撤销超指向→TASK-S3-NUMPY-AUDIT 推翻→主 Claude MATLAB 复算→REV-S3-BWANGLE PASS/HIGH→CTO 重审：超指向保持降级/fallback(DEC-S3-DSP-06 RESOLVED)
- 2026-05-28 | sprint2/docs/simulation_coverage_audit.md:5,12,153 | DOC-AUDIT-SIM-001 v2.0（Critic REV-S3-SIMAUDIT）；P0 三项桌面仿真完成（REV-S3-P0）：树形 C 桌面重建 182.4dB，算力 88.7/45.7 MCPS=17×/33× [L2]
- 2026-05-28 | sprint2/docs/POLICY-PROV-001_数字来源分级制度.md:6,276,288 | POLICY-PROV-001 v1.1（Critic REV-POLICY-PROV-001 PASS_WITH_MINOR/HIGH）；「自 2026-05-28 起强制执行第 1–5、7 部分」
- 2026-05-28 | sprint2/docs/POLICY-PROV-001_数字来源分级制度.md:27,152 | 硬件团队将 `定向音柱AI数据.docx` 发给 CTO（后成 KB-HW-001）

**2026-05-29**
- 2026-05-29 | sprint2/docs/simulation_coverage_audit.md:58 | PF-8 处置：DEC-S3-GEOM-01 撤销 d=30(视觉估测)，自研基线统一为拆机实测 d=55/N=16/L=825mm；SC-S3-GEOM-01 永久边界约束(L207-211)
- 2026-05-29 | sprint2/docs/simulation_coverage_audit.md:169,179 | PF-4 桌面闭环（DEC-S3-PF4-01）：定点化升 [L2]，SHARC [L1] 逐 bit 仍待 EZKIT
- 2026-05-29 | sprint2/docs/simulation_coverage_audit.md:59,225 | PF-9「撤回未传播」+E-NEW-3 全库清扫执行，Critic C7 复核 PASS、残留 0
- 2026-05-29 | sprint2/docs/PROJECT_HANDOVER.md:5,14,190 | 交接 v1.2；阶段=Sprint 3 Phase 1-2 完成，卡 PCB 前闸门；KB-HW-001 提取归档，WO-S3-001 6 项 1/6→6/6 文档级闭环
- 2026-05-29 | sprint2/docs/sprint3_teardown_workorder.md:3,12-18 | WO-S3-001 v1.1 状态升级（U2 N/d=16/55 此前已拆机确认为 1/6）
- 2026-05-29 | sprint2/docs/POLICY-PROV-001_数字来源分级制度.md:6 | v1.2（L0 等级+铁律四 L1↔LOCKED 强制重审+C6 几何门禁）、v1.3（铁律五撤回传播+C7）
- 2026-05-29 | 6 个文件 :3 | 给 SPRINT2_CTO_REPORT、1khz_optimization、sweep_report、critic_review、memory_update_proposal、sprint3_retrofit_assessment 统一加「历史归档/作废（PF-8，2026-05-29）」横幅

**2026-05-30**
- 2026-05-30 | sprint2/docs/POLICY-PROV-001_数字来源分级制度.md:6,27,152,276,283 | v1.5（CTO 已审批）：铁律六(外部输入 24h 入库)、铁律七(关键数字双轨独立工具核)、C8；该 docx 的「入库日」记为 2026-05-30（超 24h，约 2 天；LESSON-013 病例）

**2026-06-02**
- 2026-06-02 | sprint2/docs/POLICY-PROV-001_数字来源分级制度.md:4,106-108,284-285 | v1.6 铁律八/C9（R14 FIRA offload 收益闸门）+ v1.7 铁律九/C10（硬件不可逆动作闸门，缘起「EZKIT 上板厂商三陷阱：boot 抢 JTAG / JTAG 热插拔烧板 / 供电跳线接错」），均「CTO 拍板 2026-06-02」
- 2026-06-02 | sprint4/core_only_migration_plan.md:4 与 sprint4/dsp_migration_inventory.md:4 | Sprint 4 DSP 迁移文档起点：盘点 DOC-S4-DSP-INV-01、适配计划 DOC-S4-CORE-PLAN-01(S0-S8 步骤 L202-212)
- 2026-06-02 | sprint4/dsp/core_only/S0S1_report.md:4,28-36 | S0-S1 桌面首增量完成：host 双套 bit-exact PASS [L2 host 预验]，板上 S2 排队等台架(L6)
- 2026-06-02 | sprint4/dsp/core_only/bench/GRAFT_PLAN.md:3,9-11 | 底座选 ADI 例程 ADSP21569_LED，harness host 预验 PASS
- 2026-06-02 | sprint4/dsp/fira_integration_plan.md:5-6 | FIRA 集成路线图（不写 FIRA 代码，等 R1 板测）
- 2026-06-02 | sprint4/dsp/core_only/bench/R14_bitexact_rootcause.md:3,9,21-24 | **core-only 算法在台架上板的首个文内记录**：crc32=0x21a3d598≠golden 0x90556BC7；根因=运行期 chirp double 在 -double-size-32 下输入分叉；修=冻结 CHIRP_INPUT[]
- 2026-06-02 14:03 [git] | 提交 4bf0f52 | **本仓库第一个提交**「core-only S0-S1 host-verified」；此前内容无 git 历史

**2026-06-03**
- 2026-06-03 | sprint4/dsp/core_only/bench/CCNT_source.md:3-4 | S2 板上 bit-exact PASS（crc=0x90556BC7，[L1/EZKIT]）；填真 CCNT=`clock()`
- 2026-06-03 | sprint4/dsp/fira/FIRA_IMPL.md:5,86,142,175 | F0 闭：R1 cycle 基准 cyc_8ch_frame=1,006,935 [L1/EZKIT] + core-only 板上 bit-exact（该值按 1GHz 裕量 1.32×，见 F7_MARGIN_MATERIAL.md:117-119）；F2 载体=`bench_core_only`
- 2026-06-03 | sprint4/dsp/fira/F7_MARGIN_MATERIAL.md:117,188-193 与 F7_R14_RULING_MATERIAL.md:84,148 | 桌面 17×/33× [L2] 被板上推翻（真实周期约为 MMAC 计数的 ~25×，旧语义 8ch 裕量 1.32×）；R1 判据绑定 8ch(DEC-S4-R1-8CH-01)，16ch 降为参考（日期仅见 [git] 509dfa4 2026-06-03 11:19，文内未标日）
- 2026-06-03 | sprint4/audio_io_topology.md:3-4,13-14 | 音频 I/O 拓扑：AD-EXKIT V2.1+ADSP-21569-SOM+AD2428W-SOM，ADAU1979+ADAU1962A，SPORT4 TDM
- 2026-06-03 | sprint4/iface_survey.md:4,22 | 系统接口普查（SHARC 侧 adi_fir_2156x.h 本机缺失=G1）
- 2026-06-03 | sprint4/dsp/fira/F1_mode_format_decision.md:3,10 | G1 闭合：CTO 提供 `adi_fir_legacy_2156x.h` 并归档（C8/铁律六）；G2 闭合；Legacy 推荐
- 2026-06-03 | sprint4/dsp/fira/F3_F4_datapath_verified.md:3,9-13 | FIRA 数据通路 HW 手册实证（§38-10）
- 2026-06-03 | sprint4/dsp/fira/F4_BITEXACT_HANDOFF.md:52 | 六轮独立 critic 裁定自 2026-06-03 起（至 06-04），reviewer=critic @ claude-opus-4-8

**2026-06-04**
- 2026-06-04 | sprint4/dsp/fira/F4_BITEXACT_HANDOFF.md:5,12-21 | F4 里程碑：FIRA 单通道子带定点 bit-exact（L1 板上，9d9fbec；子带 CRC 0x2E0D8C6E）；当时「R14 主门 OPEN / C9 维持」
- 2026-06-04 | sprint4/dsp/fira/F5_8CH_HANDOFF.md:5,11-20 | F5 里程碑：8ch 子带定点 bit-exact 上板达成（L1，44a99e8；8 锚命中）
- 2026-06-04 | sprint4/iface_survey.md:225,229 | F7 首次板跑崩溃 BadResetDetected/PC=0x1，根因=`adi_pwr` 未初始化（initComponents 仅调 adi_sec_Init），修复 524c7c0
- 2026-06-04 | sprint4/dsp/fira/F7_MARGIN_MATERIAL.md:3,13-25,109-112 | F7 core-only 板跑：1,451,030 cyc/帧→8ch 裕量 0.92×（<1.0× 实时下限）[1GHz 为 L2 假设]
- 2026-06-04 | sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:11-21,41-50 | F7 FIRA build 板跑：g_f7_cyc_8ch_fira=463,273、CCLK=1,000,000,000 Hz [L1]（G6 关）、裕量 2.878×[L1-derived]
- 2026-06-04 | sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:29-39 | 官方加速比裁为 3.07×(1,420,543/463,273)，3.13× 退役（混 build 伪值）
- 2026-06-04 | sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:338-368 | Addendum B：五项未计入(43–379 MCPS)，整系统残余裕量 1.38–2.56× [L4]
- 2026-06-04 | sprint4/dsp/fira/F7_CLOSING_RECORDS.md:143-174 | DEC-S4-F7-CLOSE-01 草稿：R14 数据采集 COMPLETE，裁定 PENDING CTO
- 2026-06-04 | sprint4/dsp/fira/R14_RULING_PROPAGATION.md:4,40-61 | **CTO 三裁定**：DEC-S4-R14-RULING-01（R14 CLOSED）、DEC-S4-CRITERION-01（≥10× 退役，临时下限 ≥1.0×，正式阈值待 EQ PRD+WCET）、DEC-S4-C9-RELEASE-01（C9 RELEASED 附诚实分母，加速比锁 3.07×）
- 2026-06-04 | sprint4/dsp/fira/F4_BITEXACT_HANDOFF.md:1 等 3 文件 :1 | F4/F5 handoff、F5_F7_PLAN 顶部加「状态更新 2026-06-04：R14 已 CLOSED」指针(R14_RULING_PROPAGATION.md:170-175 的 B3 要求)
- 2026-06-04 | sprint2/docs/POLICY-PROV-001_数字来源分级制度.md:4,114-136,286 | v1.8 §4B 三道关（自动 verify→独立 critic 门→CTO 常识审），缘起 R8/R9（CTO 拍板 2026-06-04）
- 2026-06-04 21:56 [git] | 提交 89bed86 | 治理文档（CLAUDE.md、POLICY-PROV-001）首次入库——提交信息称二者「自仓库建立即 untracked，历次 v1.2-v1.8 修订仅存磁盘」

**2026-06-05 及以后**
- 2026-06-05 | sprint2/docs/simulation_coverage_audit.md:53,96 | 事后注：T/S 报告已到库(KB-DRV-TEST-001)，SPL 重做解锁
- 2026-06-05 10:44 [git] | 提交 4d7e528 | sprint2/docs 下 10 个文件首次入库（本摘要第 5,7-14 行共 9 个 + 被跳过的 prd_update.md），并对 decisions_log.md 增补 45 行；同提交落 DEC-S5-V1-SCOPE-01/DEC-S5-EQ-O1-01(范围外)
- 2026-06-09 10:34 [git] | 提交 43aad40 | sprint2 声学/DSP/硬件/专利/critic/CTO 报告等 Sprint 2 原始交付物（本摘要第 1-4,15-20 行）首次入库，提交信息称「文档/sprint历史」
- 2026-07-07 | sprint2/docs/sprint3_procurement_kickoff.md:91 | **仅为 2026-05-26 的计划目标**：消声室首次实测窗口；本范围内无任何「已预约/已实测」记录
- 2026-09-26 | sprint4/dsp/core_only/src/tree_filterbank.h.ERRATUM.md:3-15 | DEC-S7-RETRACT-SUBBAND-01：子带分界撤回更正(3k/6k/12k)；同日给 PROJECT_HANDOVER.md:173、simulation_coverage_audit.md:174 加「⚠勘误 2026-09-26」

---

## 3. 前期环节线索（"有记录+出处" / "未见"）

### 3.1 需求指标 / PRD — **有记录（二手汇编+零散）；原始需求文档未见**
- 有记录：产品定义与指标汇编 — 一句话定义、场景(博物馆讲解/车站广播/商场分区广播，固定前向安装，无电子偏转)、单向播放→延迟 <30ms、**仅 ≥1kHz 要求强指向性(DEC-S1-002)**、核心指标(−6dB BW@2kHz ≤30°、旁瓣 −20dB、栅瓣安全) — `sprint2/docs/PROJECT_HANDOVER.md:24-32`（2026-05-29 汇编，称源自 decisions_log）。
- 有记录：原延迟规格 <5ms 的来源=「沿用通信/会议/监听类音频系统的惯例值」，改 <30ms 草稿待市场/客户对齐 — `sprint2/docs/spec_change_latency.md:17-27,64-73`；正式生效仍卡对齐(`PROJECT_HANDOVER.md:153`)。
- 有记录：CTO 要求 ≥1kHz 强指向 — `sprint2/acoustic/1khz_optimization.md:15-16`；规格「−6dB BW≤30°@2kHz」称 Sprint1 规格 — `sprint2/acoustic/sweep_report.md:231`；CTO 目标「核心波束 <100 MMAC/s」— `sprint2/dsp/dsp_design.md:285-288`；质量约束(仿真 vs 实测 ≤±3dB、定点 vs 浮点 ≤1e-10、对标竞品 0° 106-111dB) — `sprint2/docs/sprint3_kickoff_checklist.md:27-31`。
- 有记录：CTO 硬约束 SC-S3-GEOM-01（PRD 不新增 6-8kHz 强指向硬需求，否则触发 d 重议）— `simulation_coverage_audit.md:207-211`、`PROJECT_HANDOVER.md:15`。
- 有记录（仅目录）：`prd_update.md` 被列为 Sprint 2 交付物 — `SPRINT2_CTO_REPORT.md:139`（内容由另一 agent 读）。EQ 链 PRD(item-3) 作为后续悬项 — `F7_R14_RULING_MATERIAL.md:352,396-397`、`R14_RULING_PROPAGATION.md:54`。
- **未见**：CTO 原始 PRD/客户需求原文、Sprint 1 的 spec 文件(`simulation_coverage_audit.md:8` 称 Sprint 1 仅 spec，不在 sprint2/sprint4 目录)；需求提出日期。

### 3.2 竞品样机拆机 — **有记录（方案+结果摘要）；拆机执行日期/照片/正式签署未见**
- 竞品消声室实测（外部数据，落盘 `knowledge_base/measurements/competitor_anechoic.md`，范围外）：角度数文内写 4 或 6 个（反推只用 0/30/60/90°，见 §5-12）、0° SPL 106–111dB（另一处写 103~110.9）— `SPRINT2_CTO_REPORT.md:92,99,141`；`critic_review.md:36`(2kHz 0°=106.8dB、30°=82.7dB)；`sweep_report.md:273-275`(30° 相对电平 −22.5/−24.1/−18.8dB)。
- 竞品反推：N≈20/d=35mm/Dolph-20/L=665mm，RMS 2.84dB — `sweep_report.md:33-46`；其后被拆机真值取代（`AC-WP01...追溯.md:134`「按错误几何…几何前提已废止」）。
- 拆机方案：CTO 的「硬件平台快速验证法」评估 — `sprint3_retrofit_assessment.md:16-20,240`（2026-05-26，当时「不执行任何采购、下单、拆机、改装」L270）；拆机工单 WO-S3-001 含法律红线 — `sprint3_teardown_workorder.md:41-45`。
- 拆机结果：N=16/d=55mm，A/B 区串联成 8 路、功放 ACM3128A、协议 TDM、主芯片含 DSP(ADSP-21569KBCZ10)、数模分地单点 — `sprint3_teardown_workorder.md:18,27-32`（2026-05-29 v1.1，经 KB-HW-001「文档级闭环」，注明仍有 5 项精度追问 L21）；8 通道→16 单元={c,15−c}对称配对[L1/硬件实测] — `sprint4/dsp/fira/F5_8CH_HANDOFF.md:29`；拆机真值归档 `knowledge_base/competitor/full_teardown_v2.md` — `PROJECT_HANDOVER.md:222`(范围外)。
- **未见**：拆机/测量的实际执行日期、照片与《6 项未知量拆机确认报告》正式签署（2026-05-29 仍「待正式签署」`PROJECT_HANDOVER.md:192`）；竞品样机采购记录。时间窗只能推：2026-05-26 拆机工单仍为计划(`retrofit:270`)，2026-05-28 的 AC-WP01 追溯已引用拆机真值 d=55(DEC-S3-003)(`AC-WP01...追溯.md:134`)。

### 3.3 方案 / 芯片选型 — **有记录（结论与后续验证）；选型比较过程未见**
- 芯片：ADSP-21569（SHARC+ 单核 1GHz）— `dsp_design.md:31`、`PROJECT_HANDOVER.md:92`；芯片 LOCKED(DEC-S1-004，Sprint 1)、算法 LOCKED(DEC-S2-002) 依据曾是纸面算力 27×/49×，被 PF-1 点名 — `POLICY-PROV-001:17`、`simulation_coverage_audit.md:51,92`；量产芯片不可逆采购冻结，21565 vs 21569 重评窗口(DEC-S3-PROC-01) — `PROJECT_HANDOVER.md:92,149`。
- 算法路线：4 子带 dyadic 树形半带 FIR + DAS/Dolph-Chebyshev — `dsp_design.md:466-562`、`SPRINT2_CTO_REPORT.md:32-67`；N/d 扫描与 Pareto — `sweep_report.md:69-152`；Gate 1 后基线 N=16/d=30/Dolph-20（`sprint3_retrofit_assessment.md:23`、`1khz_optimization.md:8`）→ 2026-05-29 统一为 d=55(DEC-S3-GEOM-01)。
- 外围选型：ADAU1966A/1962A、TAS5825M(对比 TAS6424/MAX9744/TPA3255)、明纬 MSP-450-24、TCXO — `hardware_brief.md:14-52,97`；BOM — `bom_v0.md`。
- 板上落地：ADAU1979 → SPORT4 TDM → 21569 → ADAU1962A(用 8ch) → 8 路功放 — `audio_io_topology.md:11-33`；2026-06-04 R14/路线裁定 — `R14_RULING_PROPAGATION.md:40-61`。
- 仅见侧面：Critic 对比 SC589(双核+ARM)价档 — `critic_review.md:175`；**未见**：21565/21569/其它芯片的候选比较表与选型决策日期（DEC-S1-004 原文在 decisions_log，范围外）。

### 3.4 开发板 / EZKIT 采购 — **有记录（计划与批准）；下单/订单/到货日期未见**
- 计划：EV-21569-EZKIT ×1（建议 2）¥4,000–6,000、货期 4–8 周、ADI 代理(世强/科通)下单 — `sprint3_procurement_kickoff.md:19`；ICE 仿真器等调试附件 ¥1,500–3,000 — `:21`；DoR「P1 EZKIT 已下单并确认到货期」未勾 — `:131`。
- 批准：「采购：EZKIT 开发板…（Gate 2 已批）」— `sprint3_kickoff_checklist.md:45,77`；「EZKIT 采购：可立即下单（海外周期长）…✅ 批准」— `sprint3_teardown_workorder.md:82`。
- 官方 EZKIT 板载 I/O 核实(ADAU1962A 12ch DAC+ADAU1979 4ch ADC，引 ADI 官方页) — `sprint3_retrofit_assessment.md:98-114,263-265`。
- 到货状态：2026-05-29 仍「卡…EZKIT 到货」— `PROJECT_HANDOVER.md:14,67,131-133,193`；2026-06-02 已有台架上板记录(`R14_bitexact_rootcause.md:9`)；且 `core_only_migration_plan.md:23,26,185,187,190,221`(2026-06-02)引用了 Sprint 3 的 `sprint3/audit/ezkit_fira_baseline.md`(官方 FIR 例程在 EZKIT 上的 [L1/EZKIT] cycle 基线，R14 闸门定义也出自 `:19`)和 `BENCH_OPS_CARD`(`GRAFT_PLAN.md:50`)——二者均在范围外、未读，只能说明 2026-06-02 前板上已有例程测量。故到货时点只能推在 2026-05-29(handover 仍待到货)与 2026-06-02 之间，**文内无明文日期**。
- 实际板型：S4 文档记「AD-EXKIT V2.1 + ADSP-21569-SOM + AD2428W-SOM」— `audio_io_topology.md:4`（与采购计划写的「EV-21569-EZKIT」措辞不同，见 §5-9）。
- 上板规矩：铁律九/C10（先有 CTO 确认的操作清单+物理版本确认+安全硬规矩）2026-06-02 — `POLICY-PROV-001:108`。
- 工具链：本机 CCES 2.12.1 为 ARM-only，SHARC 工具链在 CTO 的 Windows 台架（`C:\Users\<CTO>\cces\2.12.1\bench_core_only`）— `CROSS_BUILD_NOTES.md:13`、`FIRA_IMPL.md:71`。
- **未见**：采购订单/价格/实际货期/到货日、板子实物(REV 丝印)确认记录。

### 3.5 GitHub / 论文调研、框架选择、资料入库
- **GitHub：未见**（对 41 个文件 grep `github|开源|gitlab` = 0 命中）。
- 论文/专利调研：**有记录** — 三篇核心论文(Dolph 1946、Boone 2009、Zhang 2024 Sensors 24(19)6277 DOI 10.3390/s24196277「已核实」)+Ward 1973 — `patent_map.md:13-100,318-322`；检索来源=Google Patents/Espacenet/USPTO/Justia/CNIPA，**未用商业库** — `:106-117`；公式速查 — `formulas.md`；任务书曾称「疑为 Zhang 2024」、原 PDF 名 `Design_of_Differential_Loudspe.pdf` — `patent_map.md:78`、`formulas.md:224`（提示论文由 CTO 任务书/PDF 给出）。检索日期 2026-05-26 — `patent_map.md:5,8`。
- 框架/工具：numpy/scipy 仿真脚本(`array_sweep.py`、`fir_design_verify.py`、`budget_calc.py`、`latency_calc.py` 见 `SPRINT2_CTO_REPORT.md:130-137`)；MATLAB R2026a 复核 — `AC-WP01...追溯.md:32,51-53`；pyroomacoustics 仅出现在角色描述 — `PROJECT_HANDOVER.md:43`（范围内未见实际使用）；COMSOL 仅为待办 — `simulation_coverage_audit.md:127,139`；CCES+SHARC Audio Toolbox — `sprint3_procurement_kickoff.md:20`、`cces_template/README.md:53`(`ss_tdm_loopback` 示例)；ADI 例程做底座(ADSP21569_LED) — `GRAFT_PLAN.md:9-11`；ADI EE-408 FIRA 例程树/`Split_Task` — `iface_survey.md:317`、`F1_mode_format_decision.md:11`。**未见**：专门的框架/库选型比较文档。
- 资料入库(KB)：`knowledge_base/measurements/competitor_anechoic.md` — `SPRINT2_CTO_REPORT.md:141`；KB-HW-001（硬件团队 docx，2026-05-28 发出→05-29/30 入库）— `POLICY-PROV-001:27,152`、`PROJECT_HANDOVER.md:190`；KB-DRV-TEST-001(T/S 报告，2026-06-05 到库)— `simulation_coverage_audit.md:53,96`；`knowledge_base/ezkit/`（datasheet、BSP、app notes、`adi_fir_legacy_2156x.h` 归档 2026-06-03）— `audio_io_topology.md:13-14`、`CCNT_source.md:10-16`、`F1_mode_format_decision.md:10`；入库纪律=铁律六 24h 规则 — `POLICY-PROV-001:102,138-157`。

### 3.6 团队 / 治理搭建 — **有记录（成员与制度演进）；团队创建日期未见**
- 团队：四层+一横切，成员清单与安全护栏 — `PROJECT_HANDOVER.md:36-52`；Sprint 2 团队=声学/DSP/专利文献/硬件/项目文档+Critic — `SPRINT2_CTO_REPORT.md:6-7`；各 agent 带版本署名(`AcousticSimulationAgent v1.0` 等)；Critic 2026-05-26 已在运作 — `critic_review.md:5-10`。
- 记忆机制：MEMORY 更新需 TL+CTO 授权的流程 — `memory_update_proposal.md:11-14,140-150`。
- 治理制度：POLICY-PROV-001 v1.1(05-28)→v1.8(06-04)，逐版缘起(PF-1/PF-8/PF-9/LESSON-012/013/R14/EZKIT 三陷阱/R8-R9) — `POLICY-PROV-001:4-29,283-288`。
- 运行规则：Commit discipline 硬规入 `.claude/team_config.md`(commit 1ce0819) — `F5_8CH_HANDOFF.md:32`；team 花名册/模型档位 claude-opus-4-8、peer-challenge ON — `F4_BITEXACT_HANDOFF.md:52`；子 agent 长任务 socket 死风险 → 窄派单+PM 接力 — `F4_BITEXACT_HANDOFF.md:53`、`S0S1_report.md:4`。
- **未见**：Agent Team 的组建日期/初始 prompt（`PROJECT_REFERENCE.md`、`SKILL.md`、`CLAUDE.md` 在范围外）。

---

## 4. 阶段边界线索

- **Sprint 1 → Sprint 2**：无日期。仅见 Sprint 1 完成项(技术路线锁定、指向性频段需求、Gate 1 基线验证、芯片选型) `PROJECT_HANDOVER.md:62`；「Sprint 1 仅 spec，无仿真脚本」`simulation_coverage_audit.md:8`。
- **Sprint 2 结束 / Gate 1**：2026-05-26，`SPRINT2_CTO_REPORT.md:1,5`「Sprint 2 CTO 终汇报」，L111「Gate 1 决策（阻塞 Sprint 3，必须拍板）」；同日 Sprint 3 启动清单已写「Gate 1 PASSED / Gate 2 CLOSED」`sprint3_kickoff_checklist.md:7`。Gate 1 拍板的具体日期/决议原文在本范围内未见（见 §5-7）。
- **Sprint 3 开始**：2026-05-26，`sprint3_kickoff_checklist.md:6-8`（启动清单）+`sprint3_procurement_kickoff.md:4-9`（采购）+`sprint3_retrofit_assessment.md:8`（快速验证法评估）+`sprint3_teardown_workorder.md:3`（拆机工单第一动作）。
- **Sprint 3 内部转折（几何重启）**：2026-05-29 DEC-S3-GEOM-01/PF-8，d=30→d=55，旧 d=30 数字作废 — `simulation_coverage_audit.md:58`；`PROJECT_HANDOVER.md:15,71`。治理转折：POLICY v1.1(05-28)→v1.5(05-30)，`POLICY-PROV-001:276`。
- **Sprint 3 暂停点**：2026-05-29「Sprint 3 Phase 1-2 完成，卡 PCB 前闸门，零自动推进、等人工输入」`PROJECT_HANDOVER.md:14,64-67`（Phase 3 ⏸：拆机报告签署+EZKIT 到货+T/S 回报）。
- **硬件上板开始（Sprint 3→4 衔接）**：EZKIT 到货在 2026-05-29 之后、2026-06-02 之前（06-02 前已有板上例程基线，见 §3.4）；2026-06-02 我方算法首次上板失败记录 `R14_bitexact_rootcause.md:9`；铁律九/C10(上板规矩)同日 `POLICY-PROV-001:108`。
- **Sprint 4 开始**：2026-06-02 起 DOC-S4-* 文档集（`core_only_migration_plan.md:4`、`dsp_migration_inventory.md:4`、`fira_integration_plan.md:5`）；git 第一提交同日 14:03 `[git] 4bf0f52`。Sprint 3 清单把「Sprint 4」指为专利申请阶段(`sprint3_kickoff_checklist.md:35`、`PROJECT_HANDOVER.md:155`)，实际 Sprint 4 内容是 DSP 板上迁移/FIRA（见 §5-8）。
- **Sprint 4 内里程碑**：2026-06-03 F0 闭(R1 基准 1,006,935 cyc+板上 bit-exact PASS) `FIRA_IMPL.md:86`；2026-06-04 F4(`F4_BITEXACT_HANDOFF.md:12`)、F5(`F5_8CH_HANDOFF.md:11`)、F7(`F7_R14_RULING_MATERIAL.md:11-21`)。
- **Sprint 4 / R14 线结束**：2026-06-04，CTO 三裁定 `R14_RULING_PROPAGATION.md:4,40-61`（R14 CLOSED、≥10× 退役、C9 RELEASED 附诚实分母）；git 提交信息 3359ff7 称「R14 线正式收官；悬项：EQ PRD/WCET 实测/DMA harness/analyze-synth 重读」`[git]`；文内悬项见 `R14_RULING_PROPAGATION.md:63-68`、`F7_R14_RULING_MATERIAL.md:390-398`。
- **治理闸门演进**：C9 管控期 2026-06-02(设立)→2026-06-04(释放，`R14_RULING_PROPAGATION.md:56-61`)；三道关 2026-06-04 `POLICY-PROV-001:114-136`。
- **向 Sprint 5 过渡（仅 git 侧证）**：2026-06-04 21:56 提交 8e49cb2「v1 路线裁定+三道关新政(DEC-S5-STEER-V1-01)」、2026-06-05 10:44 提交 4d7e528「v1 收窄+EQ=O1(DEC-S5-V1-SCOPE-01/DEC-S5-EQ-O1-01)」`[git]`；范围内文件无 Sprint 5 正文。
- **后期回溯**：2026-09-26 DEC-S7-RETRACT-SUBBAND-01 回改 Sprint 2/4 文档(三处勘误注) — `ERRATUM.md:3`、`PROJECT_HANDOVER.md:173`、`simulation_coverage_audit.md:174`。

---

## 5. 疑点

1. **范围命令漏文件**：`git ls-files … | grep '\.md$'` 漏掉 2 个中文名 md（git 引号转义），已补读；若 CTO 的手册索引用该命令生成，会漏 `POLICY-PROV-001_数字来源分级制度.md` 与 `AC-WP01_1kHz波束宽度决策追溯.md`。
2. **git 首次入库日期≠创建日期（回填）**：仓库第一个提交是 2026-06-02 14:03（4bf0f52 `[git]`），此前内容无 git 历史；Sprint 2 原始交付物（文内 2026-05-26）到 2026-06-09 才首次入库（43aad40，提交信息「文档/sprint历史」）；sprint2/docs 的 10 个文件(文内 05-26~05-29)到 2026-06-05 才首次入库（4d7e528）；POLICY-PROV-001 到 2026-06-04 才首次追踪（89bed86 提交信息自述「自仓库建立即 untracked，历次 v1.2-v1.8 修订仅存磁盘」）；`core_only_migration_plan.md`/`dsp_migration_inventory.md`(文内 06-02)到 06-04 才入库；`decisions_log.md` 首次入库即加入 659 行(13be4b3)。时间线应以文内日期为准，git 日期只能作"最晚已存在"证据。
3. **事后改写但头部日期/版本未更新**：多个文件头仍为 2026-05-26 v1.0，正文却含 2026-05-29 之后的 d=55 改写，不能把头部日期当"内容截至日"：`sprint3_kickoff_checklist.md:14,43,48,94,109`；`sprint3_procurement_kickoff.md:40-42,59,98,105`；`dsp_design.md:35,108-117,566`（还无 PF-8 横幅）；`formulas.md:38,120,214-216,327-331`；`cces_template/README.md:65`（该文件无任何日期）；`simulation_coverage_audit.md` 头部日期 2026-05-28 但版本到 v2.3(05-29)。另 `CCNT_source.md` 头 2026-06-03 却含 06-04 追加(L41,L48)；`iface_survey.md` 头 06-03 含 06-04 证伪注(L225)。
4. **Critic 指出的问题在文件里没改（修订只在 Critic 报告/汇报里声明）**：
   - `formulas.md:140`「本项目定向音柱为端射布局」、`patent_map.md:292`「ITC 采用端射 + 稳定因子最优波束成形的核心方案存在侵权风险」仍在，而 Critic F-PAT-01(`critic_review.md:132`)判定项目为 broadside、`SPRINT2_CTO_REPORT.md:117` 称「Critic 已纠正」。
   - `patent_map.md:226,256-258,278-284` 写「双核 SHARC+」「ADSP-21569 ARM 核（600 MHz Cortex-A5）」，与同文件 L238「单核」、`critic_review.md:203`、`PROJECT_HANDOVER.md:92`、`F7_MARGIN_MATERIAL.md:87`(数据手册标题「SHARC+ Single Core」)矛盾；`hardware_brief.md:141` 框图亦写 "Dual SHARC Core"。
   - `bom_v0.md:16,80,89,141` 仍用 DSP ¥350–500、16ch ¥1,169–2,065；`SPRINT2_CTO_REPORT.md:75,82` 为 DSP ¥120–220、16ch ¥940–1,785「修正后」；`memory_update_proposal.md:58` 写 ¥1169-2065 却注「ADSP-21569 ¥120-220」——三处口径不一致，库内无修正后的 BOM 文件。`hardware_brief.md:70,83` 仍把 TLV62568 标 LDO（Critic F-HW-06 指其为 buck，`critic_review.md:179`）。
   - `SPRINT2_CTO_REPORT.md:64,122`（同为 2026-05-26）仍写群延迟 4.54ms 逼近 <5ms，而 `dsp_design.md:619`、`spec_change_latency.md:17-18` 同日已算出树形端到端 12.53ms 并提议放宽到 <30ms。`sprint3_kickoff_checklist.md:29,92,107` 仍把 R2 目标写 ≤5ms，与 DEC-S2-012 的 <30ms(待市场对齐，`PROJECT_HANDOVER.md:153`)并存。
5. **文内状态行与 git 提交信息不一致（过门证据只在 git 里）**：`F5_F7_PLAN.md:5`「DRAFT，待 critic 门禁」、`F7_CLOSING_RECORDS.md:3`「DRAFT ONLY. Not committed」、`R14_RULING_PROPAGATION.md:3`「DRAFT ONLY. 不 commit」，三者都已提交（8b373f3/010eb35/3359ff7），"critic 两轮 PASS / R6 / R7 CONDITIONAL 0/1/1"只出现在 git 提交信息 `[git]`。`F7_R14_RULING_MATERIAL.md:247` 自带 critic R5 CONDITIONAL 0/1/1 注，是唯一文内过门痕迹。`fira_integration_plan.md`、`FIRA_IMPL.md` 全文无 "critic" 字样，其「critic PASS」同样只见于 git 提交信息(9dd9e61/8f24017)；`core_only_migration_plan.md:4,248` 自称「开工待 critic 核」，「已核可」只在 `S0S1_report.md:5` 一句带过。
6. **KB-HW-001 日期冲突 1 天**：`PROJECT_HANDOVER.md:190` 与 `sprint3_teardown_workorder.md:12` 写「2026-05-29」已提取归档 KB-HW-001、6/6 闭环；`POLICY-PROV-001:27,152` 写该 docx「2026-05-28 发 CTO，2026-05-30 才转交入库」(入库日 05-30，超 24h)。哪个是准的在范围内无法判定。
7. **Gate 1 的结果与时点**：`SPRINT2_CTO_REPORT.md:15`（2026-05-26）主推荐 N=24/d=30/Dolph-30，并请 CTO 在 Gate 1 拍板 N、d(L113-114)；同日的 `sprint3_retrofit_assessment.md:23`、`1khz_optimization.md:8`、`sprint3_kickoff_checklist.md:7` 已把基线写成 N=16/d=30/Dolph-20(「Gate 1 PASSED」)。拍板人/日期/决议原文不在本范围（应在 decisions_log）。另外 `critic_review.md` 是第一轮（REWORK）；CTO 报告说"两轮"，第二轮评审文件未见。
8. **"Sprint 4"含义漂移**：Sprint 2/3 文档里「Sprint 4」=专利申请(DEC-S2-010 推迟至 Sprint 4，`sprint3_kickoff_checklist.md:35`；`PROJECT_HANDOVER.md:155`)/「第四阶段(正式产品)」(`sprint3_retrofit_assessment.md:234`)；DOC-S4-* 文档实际是 DSP 板上迁移与 FIRA。git 提交信息里还有「阶段4」「WO-S6-AUDIO」「DEC-S6-*」[git]，与 Sprint 4/S4 编号并存。手册分章要先定义阶段命名。
9. **板型称呼**：采购/计划写官方「EV-21569-EZKIT」(`sprint3_procurement_kickoff.md:19`、`kickoff_checklist.md:45`、`retrofit_assessment.md:98-114`)；S4 记录板为「AD-EXKIT V2.1 + ADSP-21569-SOM + AD2428W-SOM」(`audio_io_topology.md:4`)，但全体系仍用 `[L1/EZKIT]` 标签。文内无"实际采购板与计划不同"的明文说明，也无订单记录。
10. **R14 一词多义**：(i) FIRA 收益闸门/bit-exact 闸门(`fira_integration_plan.md:20`)；(ii) core-only 上板 bit-exact 失败根因文件也冠以 R14(`R14_bitexact_rootcause.md:1`)；(iii) 最终闭合含"周期含全开销+CCLK 实测"(`F7_R14_RULING_MATERIAL.md:210-212`)。两个 golden 并存：端到端 0x90556BC7 与子带 0x2E0D8C6E，前者被 R14 子带粒度判据取代(`F5_F7_PLAN.md:71`，DEC-S4-R14-GRANULARITY)。
11. **算力数字多版本，不可混引**：纸面 27×/49×(L3，已废) → 桌面 17×/33×[L2] → 板上 cyc_8ch=1,006,935(旧"8 进 1 出求和"语义，1GHz 下 1.32×) → 新"8 路独立无求和"语义 1,451,030(0.92×，不可与 1,006,935 直接比，`F7_MARGIN_MATERIAL.md:116-127`) → FIRA 463,273(2.878×，须与 1.38–2.56×[L4] 连体，`F7_R14_RULING_MATERIAL.md:47-49`)。`FIRA_IMPL.md:86,142`、`F5_F7_PLAN.md:180` 仍写 1,006,935 为"纯核基线"。加速比 3.13× 已禁用，官方 3.07×(`F7_R14_RULING_MATERIAL.md:38-39`)；16ch 的 1.73–1.75× 仍是 [L3] 约定式估算，analyze/synth 拆分读数未恢复(`:325-334`)。
12. **竞品实测数字不一致**：0° SPL `sweep_report.md:310`「103~110.9dB」vs `SPRINT2_CTO_REPORT.md:99`、`kickoff_checklist.md:31`「106–111dB」；实测角度数 `sweep_report.md:63,281,292`、`sprint3_retrofit_assessment.md:50` 写 6 个角度/6 点，而 `SPRINT2_CTO_REPORT.md:97,105`、`critic_review.md:35,206`、`AC-WP01...追溯.md:133` 写 4 角度（0/30/60/90°），`sweep_report.md:22,268` 称「四个实测角度」；源 `competitor_anechoic.md` 在范围外，无法在本范围内裁定。
13. **MEMORY 提案文件名**：`memory_update_proposal.md:26,132` 提议 `sprint2-baseline.md`，而 `SPRINT2_CTO_REPORT.md:143` 称已更新 `memory/sprint2-algorithm-baseline.md`；提案授权表全⏳(L142-150)。文内无法确认哪份落地。
14. **计划但无落地记录**：消声室预约/首次实测目标 2026-07-07(`sprint3_procurement_kickoff.md:91-101`)、供应商 datasheet 回收(DoR L133)、2026-05-29 仍卡消声室档期(`PROJECT_HANDOVER.md:137,186`)——本范围内无任何"已完成"记录。
15. **跨文档引用的行号会漂移**：多处写时引用 `decisions_log.md:234/:575/:627` 等行号，`R14_RULING_PROPAGATION.md:210` 自承"行号随版本漂移，以锚字符串定位"；手册引用 decisions_log 时应以 DEC 编号而非行号。
16. **「顾问」角色**：`FIRA_IMPL.md:70`「CTO 顾问侧更正 2026-06-03」、`F3_F4_datapath_verified.md:5`「顾问针 1」——"顾问"身份与职责文内未定义。
17. **二进制入库反复**：`host_bitexact_sat/unsat`、`core_only_to_windows.tgz` 2026-06-04 先入库(3359ff7)、同日移出(0383915 称误卷入构建产物)、2026-06-09 又加回(43aad40) `[git]`，无来源说明。
