# digest_C_sprint3 — sprint3/ 记录摘录（只读）

> ⚠ 公开版说明（2026-10-02）：本摘录按写时原文照录，里面会出现已撤回或已被推翻的数字（如 d=30、17×/33×、1.5k/3k/6k 子带标签、86–144 MCPS、6.4×）。采信任何数字前，以 `sprint2/docs/decisions_log.md` 和 `sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md` 为准。

> 摘录对象：`/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint3/` 下全部 git 跟踪的 `.md`(64 个)；非 md 38 个仅列名。
> 方法：每个 md 用 Read 工具整文件读完(最长 351 行，无需分段)；字节/行数用 `wc`；首次提交用 `git log --diff-filter=A`。
> 铁则：只摘文本，不外推；每条结论带 `path:line`；凡我自己做的核算(md5、numpy 复刻)均明确标『摘录者临时核』，不是记录内容。
> 摘录日 2026-10-02。

## 0. 读了什么

**先读这条（影响全文时间判断）**：
- git 历史的根提交是 2026-06-02 14:03(`4bf0f52`)。sprint3 的 64 个 md 里 **62 个首次提交都是 `43aad40`(2026-06-09 10:34)** 的批量入库(提交说明：「ITC DSP 入库: M1完整loopback + M2 FIRA入环(12a5920) + softcfg重跑包 + 文档/sprint历史 (knowledge_base/zip 已 ignore)」)；仅 `BENCH_OPS_CARD.md` 是 `13be4b3`(2026-06-02) 当时入库，`tree_filterbank.h.ERRATUM.md` 是 `33b1966`(2026-09-26)。
- 所以 **首次提交日期 ≠ 撰写日期**；真实撰写日期只能取文内自报日期(§1 内容栏 〔文内:…〕)，且这些文内日期没有 git 佐证。
- `knowledge_base/` 被 `.gitignore` 排除(仅个别文件被强制跟踪)，sprint3 文档反复引用的 `knowledge_base/competitor/full_teardown_v2.md`(拆机报告本体)、`定向音柱AI数据*.docx` 的提取件等不在 git 里，本摘录只能看到二手引用。

**文内日期分布(64 md)**：2026-05-27×5；2026-05-29×45；2026-05-30×5；2026-06-01×1；2026-06-02×4；2026-09-26×1；无日期×3。
无任何日期的 3 个：`ezkit_bringup_checklist.md`、`cces_skeleton_description.md`、`critic_ai_citation_audit.md`；日期只在文末的 3 个：`critic_bootstrap_rv.md`(L67)、`PF9_C7_drafts.md`(L78)、`sub2_fixed_vs_float.md`(L199)。

### 0.1 md 文件清单(64)

| # | path | bytes | 行数(wc -l) | 读完? | 首次提交(hash 日期) |
|---|------|------:|-----------:|-------|--------------------|
| 1 | sprint3/acoustic/pf8/critic_p0a2_review.md | 5556 | 95 | 是(整文件 1 次 Read，末行 L95) | 43aad40 2026-06-09 |
| 2 | sprint3/acoustic/pf8/p0a1_grating_criterion.md | 8877 | 121 | 是(整文件 1 次 Read，末行 L121) | 43aad40 2026-06-09 |
| 3 | sprint3/acoustic/pf8/p0a2_grating_cost.md | 14744 | 183 | 是(整文件 1 次 Read，末行 L183) | 43aad40 2026-06-09 |
| 4 | sprint3/acoustic/sweep_d55_report.md | 8937 | 200 | 是(整文件 1 次 Read，末行 L200) | 43aad40 2026-06-09 |
| 5 | sprint3/audit/A1_static_weight_tuning.md | 6704 | 108 | 是(整文件 1 次 Read，末行 L108) | 43aad40 2026-06-09 |
| 6 | sprint3/audit/A2_fib_feasibility.md | 9833 | 174 | 是(整文件 1 次 Read，末行 L174) | 43aad40 2026-06-09 |
| 7 | sprint3/audit/A3_decision_recommendation.md | 4607 | 45 | 是(整文件 1 次 Read，末行 L45) | 43aad40 2026-06-09 |
| 8 | sprint3/audit/BENCH_OPS_CARD.md | 6194 | 57 | 是(整文件 1 次 Read，末行 L57) | 13be4b3 2026-06-02 |
| 9 | sprint3/audit/NEXT_SESSION_BOOTSTRAP.md | 16297 | 193 | 是(整文件 1 次 Read，末行 L193) | 43aad40 2026-06-09 |
| 10 | sprint3/audit/PF9_post_simulation_panorama.md | 21348 | 170 | 是(整文件 1 次 Read，末行 L170) | 43aad40 2026-06-09 |
| 11 | sprint3/audit/POLICY_v15_draft.md | 9506 | 113 | 是(整文件 1 次 Read，末行 L113) | 43aad40 2026-06-09 |
| 12 | sprint3/audit/SPRINT3_DESKTOP_CLOSURE.md | 5664 | 62 | 是(整文件 1 次 Read，末行 L62) | 43aad40 2026-06-09 |
| 13 | sprint3/audit/competitor_directivity_qualitative.md | 9101 | 107 | 是(整文件 1 次 Read，末行 L107) | 43aad40 2026-06-09 |
| 14 | sprint3/audit/comsol_geometry_input.md | 6120 | 94 | 是(整文件 1 次 Read，末行 L94) | 43aad40 2026-06-09 |
| 15 | sprint3/audit/critic_a123_rv.md | 11887 | 154 | 是(整文件 1 次 Read，末行 L154) | 43aad40 2026-06-09 |
| 16 | sprint3/audit/critic_bootstrap_rv.md | 6573 | 67 | 是(整文件 1 次 Read，末行 L67) | 43aad40 2026-06-09 |
| 17 | sprint3/audit/critic_c8_first_run.md | 10123 | 115 | 是(整文件 1 次 Read，末行 L115) | 43aad40 2026-06-09 |
| 18 | sprint3/audit/critic_compqual_gate.md | 3672 | 64 | 是(整文件 1 次 Read，末行 L64) | 43aad40 2026-06-09 |
| 19 | sprint3/audit/critic_matlab_rv.md | 8057 | 113 | 是(整文件 1 次 Read，末行 L113) | 43aad40 2026-06-09 |
| 20 | sprint3/audit/critic_panorama_gate.md | 5700 | 64 | 是(整文件 1 次 Read，末行 L64) | 43aad40 2026-06-09 |
| 21 | sprint3/audit/critic_std_a_rv.md | 5686 | 99 | 是(整文件 1 次 Read，末行 L99) | 43aad40 2026-06-09 |
| 22 | sprint3/audit/critic_x5_x1_review.md | 8190 | 91 | 是(整文件 1 次 Read，末行 L91) | 43aad40 2026-06-09 |
| 23 | sprint3/audit/doc_v15_review.md | 6266 | 70 | 是(整文件 1 次 Read，末行 L70) | 43aad40 2026-06-09 |
| 24 | sprint3/audit/drv_test_metadata_query.md | 4101 | 46 | 是(整文件 1 次 Read，末行 L46) | 43aad40 2026-06-09 |
| 25 | sprint3/audit/ezkit_bringup_checklist.md | 20238 | 284 | 是(整文件 1 次 Read，末行 L284) | 43aad40 2026-06-09 |
| 26 | sprint3/audit/ezkit_fira_baseline.md | 19660 | 266 | 是(整文件 1 次 Read，末行 L266) | 43aad40 2026-06-09 |
| 27 | sprint3/audit/fira_fit_assessment.md | 27190 | 239 | 是(整文件 1 次 Read，末行 L239) | 43aad40 2026-06-09 |
| 28 | sprint3/audit/hardware_followup_queries.md | 3696 | 43 | 是(整文件 1 次 Read，末行 L43) | 43aad40 2026-06-09 |
| 29 | sprint3/audit/matlab_independent_verification.md | 5753 | 51 | 是(整文件 1 次 Read，末行 L51) | 43aad40 2026-06-09 |
| 30 | sprint3/audit/matlab_verify_m0_plan.md | 9789 | 129 | 是(整文件 1 次 Read，末行 L129) | 43aad40 2026-06-09 |
| 31 | sprint3/audit/matlab_verify_m1_sll_wng_di.md | 10484 | 134 | 是(整文件 1 次 Read，末行 L134) | 43aad40 2026-06-09 |
| 32 | sprint3/audit/matlab_verify_m2_mc.md | 10360 | 140 | 是(整文件 1 次 Read，末行 L140) | 43aad40 2026-06-09 |
| 33 | sprint3/audit/matlab_verify_m3_superdir_8pair.md | 10082 | 129 | 是(整文件 1 次 Read，末行 L129) | 43aad40 2026-06-09 |
| 34 | sprint3/audit/sprint4_inputs.md | 3404 | 44 | 是(整文件 1 次 Read，末行 L44) | 43aad40 2026-06-09 |
| 35 | sprint3/audit/standard_compliance_check.md | 10416 | 154 | 是(整文件 1 次 Read，末行 L154) | 43aad40 2026-06-09 |
| 36 | sprint3/critic/critic_review_s3.md | 20322 | 258 | 是(整文件 1 次 Read，末行 L258) | 43aad40 2026-06-09 |
| 37 | sprint3/dsp/cces_skeleton/cces_skeleton_description.md | 15105 | 346 | 是(整文件 1 次 Read，末行 L346) | 43aad40 2026-06-09 |
| 38 | sprint3/dsp/dsp_8ch_report.md | 15971 | 308 | 是(整文件 1 次 Read，末行 L308) | 43aad40 2026-06-09 |
| 39 | sprint3/dsp/pf4/PF4_INTEGRATION_SUMMARY.md | 7153 | 95 | 是(整文件 1 次 Read，末行 L95) | 43aad40 2026-06-09 |
| 40 | sprint3/dsp/pf4/WO_node1_saturation_fix.md | 5823 | 90 | 是(整文件 1 次 Read，末行 L90) | 43aad40 2026-06-09 |
| 41 | sprint3/dsp/pf4/critic_fix_verify.md | 9451 | 146 | 是(整文件 1 次 Read，末行 L146) | 43aad40 2026-06-09 |
| 42 | sprint3/dsp/pf4/critic_review_pf4.md | 20381 | 324 | 是(整文件 1 次 Read，末行 L324) | 43aad40 2026-06-09 |
| 43 | sprint3/dsp/pf4/sub1_q15_stopband.md | 10394 | 156 | 是(整文件 1 次 Read，末行 L156) | 43aad40 2026-06-09 |
| 44 | sprint3/dsp/pf4/sub2_fixed_vs_float.md | 11396 | 200 | 是(整文件 1 次 Read，末行 L200) | 43aad40 2026-06-09 |
| 45 | sprint3/dsp/pf4/sub3_q46_overflow.md | 10201 | 179 | 是(整文件 1 次 Read，末行 L179) | 43aad40 2026-06-09 |
| 46 | sprint3/dsp/tree_filterbank.h.ERRATUM.md | 1357 | 19 | 是(整文件 1 次 Read，末行 L19) | 33b1966 2026-09-26 |
| 47 | sprint3/hardware/selfdev_bom.md | 21851 | 351 | 是(整文件 1 次 Read，末行 L351) | 43aad40 2026-06-09 |
| 48 | sprint3/hardware/transition_board_design.md | 17749 | 299 | 是(整文件 1 次 Read，末行 L299) | 43aad40 2026-06-09 |
| 49 | sprint3/pf8/L1_test_window_tasklist.md | 4108 | 74 | 是(整文件 1 次 Read，末行 L74) | 43aad40 2026-06-09 |
| 50 | sprint3/pf8/PF8_retrospective.md | 21915 | 172 | 是(整文件 1 次 Read，末行 L172) | 43aad40 2026-06-09 |
| 51 | sprint3/pf8/PF9_C7_drafts.md | 7787 | 78 | 是(整文件 1 次 Read，末行 L78) | 43aad40 2026-06-09 |
| 52 | sprint3/pf8/PF_atlas.md | 5492 | 63 | 是(整文件 1 次 Read，末行 L63) | 43aad40 2026-06-09 |
| 53 | sprint3/pf8/blindspot_triage.md | 4136 | 51 | 是(整文件 1 次 Read，末行 L51) | 43aad40 2026-06-09 |
| 54 | sprint3/pf8/critic_ai_citation_audit.md | 7814 | 83 | 是(整文件 1 次 Read，末行 L83) | 43aad40 2026-06-09 |
| 55 | sprint3/pf8/critic_c7_enew3_review.md | 6418 | 79 | 是(整文件 1 次 Read，末行 L79) | 43aad40 2026-06-09 |
| 56 | sprint3/pf8/critic_ctier_eval.md | 5695 | 73 | 是(整文件 1 次 Read，末行 L73) | 43aad40 2026-06-09 |
| 57 | sprint3/pf8/critic_enew3_final_confirm.md | 4874 | 70 | 是(整文件 1 次 Read，末行 L70) | 43aad40 2026-06-09 |
| 58 | sprint3/pf8/critic_final_s1.md | 5917 | 68 | 是(整文件 1 次 Read，末行 L68) | 43aad40 2026-06-09 |
| 59 | sprint3/pf8/critic_final_s2.md | 4141 | 67 | 是(整文件 1 次 Read，末行 L67) | 43aad40 2026-06-09 |
| 60 | sprint3/pf8/critic_final_verdict.md | 6354 | 71 | 是(整文件 1 次 Read，末行 L71) | 43aad40 2026-06-09 |
| 61 | sprint3/pf8/critic_land_review.md | 4704 | 65 | 是(整文件 1 次 Read，末行 L65) | 43aad40 2026-06-09 |
| 62 | sprint3/pf8/critic_p0b_review.md | 3935 | 48 | 是(整文件 1 次 Read，末行 L48) | 43aad40 2026-06-09 |
| 63 | sprint3/pf8/p0b_asset_inventory.md | 6852 | 81 | 是(整文件 1 次 Read，末行 L81) | 43aad40 2026-06-09 |
| 64 | sprint3/pf8/p1b_prd_alignment.md | 13503 | 162 | 是(整文件 1 次 Read，末行 L162) | 43aad40 2026-06-09 |

合计 615614 bytes(约 601 KB)。

### 0.2 非 md 文件(38，仅列名/类型，未读内容；全部首次提交 `43aad40` 2026-06-09)

| path | bytes | 类型 |
|------|------:|------|
| sprint3/acoustic/pf8/p0a1_edge_probe.py | 1304 | Python 脚本 |
| sprint3/acoustic/pf8/p0a1_grating_criterion.py | 7578 | Python 脚本 |
| sprint3/acoustic/pf8/p0a1_grating_pattern.png | 315063 | PNG 图 |
| sprint3/acoustic/pf8/p0a1_pattern_data.csv | 8467 | CSV 数据 |
| sprint3/acoustic/polar_d55_vs_competitor.png | 347606 | PNG 图 |
| sprint3/acoustic/sweep_d55.py | 39926 | Python 脚本 |
| sprint3/acoustic/sweep_d55_results.csv | 1424 | CSV 数据 |
| sprint3/acoustic/topology_16elem_vs_8pair.png | 380657 | PNG 图 |
| sprint3/audit/A2_fib_feasibility.csv | 392 | CSV 数据 |
| sprint3/audit/A2_fib_feasibility.py | 11534 | Python 脚本 |
| sprint3/audit/a1_static_weight_numpy.csv | 316 | CSV 数据 |
| sprint3/audit/a1_static_weight_numpy.py | 8838 | Python 脚本 |
| sprint3/audit/m1_numpy_d55_sll_wng_di.csv | 237 | CSV 数据 |
| sprint3/audit/m1_numpy_sll_wng_di.py | 3645 | Python 脚本 |
| sprint3/audit/m2_numpy_mc.py | 6819 | Python 脚本 |
| sprint3/audit/m2_numpy_mc_results.csv | 1662 | CSV 数据 |
| sprint3/audit/m3_numpy_8pair_equiv.csv | 199 | CSV 数据 |
| sprint3/audit/m3_numpy_superdir_8pair.py | 6043 | Python 脚本 |
| sprint3/audit/m3_numpy_superdir_d55.csv | 214 | CSV 数据 |
| sprint3/audit/std_table9_compliance.csv | 1021 | CSV 数据 |
| sprint3/audit/std_table9_compliance.py | 7776 | Python 脚本 |
| sprint3/dsp/pf4/fixed_vs_float | 29672 | ELF 64 位可执行文件(已编译二进制，被 git 跟踪) |
| sprint3/dsp/pf4/fixed_vs_float_compare.c | 19155 | C 源码 |
| sprint3/dsp/pf4/pf4_fixed_vs_float.csv | 304629 | CSV 数据 |
| sprint3/dsp/pf4/q15_stopband_sim.py | 21084 | Python 脚本 |
| sprint3/dsp/pf4/sub1_q15_stopband_v2.py | 16375 | Python 脚本 |
| sprint3/dsp/pf4/xcheck_subband.py | 7822 | Python 脚本 |
| sprint3/dsp/tree_filterbank.c | 9792 | C 源码 |
| sprint3/dsp/tree_filterbank.h | 7452 | C 头文件(冻结件 tree_filterbank.h) |
| sprint3/dsp/tree_io_sat.csv | 2251786 | CSV 数据 |
| sprint3/dsp/tree_io_unsat.csv | 2251786 | CSV 数据 |
| sprint3/dsp/tree_verify | 21128 | ELF 64 位可执行文件(已编译二进制，被 git 跟踪) |
| sprint3/dsp/tree_verify.c | 11297 | C 源码 |
| sprint3/dsp/tree_verify_adversarial.c | 10254 | C 源码 |
| sprint3/dsp/tree_verify_sat | 21128 | ELF 64 位可执行文件(已编译二进制，被 git 跟踪) |
| sprint3/dsp/tree_verify_unsat | 21128 | ELF 64 位可执行文件(已编译二进制，被 git 跟踪) |
| sprint3/dsp/tva_sat | 20784 | ELF 64 位可执行文件(已编译二进制，被 git 跟踪) |
| sprint3/dsp/tva_unsat | 20784 | ELF 64 位可执行文件(已编译二进制，被 git 跟踪) |

补充(摘录者临时核，非记录内容)：`md5sum sprint3/dsp/tree_filterbank.c` = `1e88479385c8de7d3107b8c3a34e840a`、`tree_filterbank.h` = `7397ff0e02b9f9bd917c3093bc2b2912`，与 `sprint3/audit/BENCH_OPS_CARD.md:13`、`sprint3/dsp/tree_filterbank.h.ERRATUM.md:17` 所写身份码一致。

## 1. 文件清单

格式：`首次入库日期 | path | 类型 | 一句话内容(〔文内日期·署名〕开头) | 状态(原文，括号内为行号)`。排序：按首次入库日期，同日按 path。

| 首次入库日期 | path | 类型 | 一句话内容 | 状态(原文) |
|------------|------|------|-----------|-----------|
| 2026-06-02 | sprint3/audit/BENCH_OPS_CARD.md | 操作卡/runbook | 〔文内:2026-06-02·PM 整合〕台架 CCES 一页流程：Phase0 传输+md5 核对→Phase1 真 SHARC cross-build→Phase2 bringup 上电→Phase3 core-only R1 闭合(含 13b 饱和钳位反汇编)→Phase4 ADI FIRA baseline | 无状态行；「三条贯穿红线」(L7)；「待回填（台架产出后）」(L48) |
| 2026-06-09 | sprint3/acoustic/pf8/critic_p0a2_review.md | Critic 评审 | 〔文内:2026-05-29·critic-itc-001〕复核 P0-A-2：独立 numpy 复现栅瓣 0dB、认同降规格与 ESCALATE#1=NO | 「裁决 PASSED（confidence: HIGH）」(L9) |
| 2026-06-09 | sprint3/acoustic/pf8/p0a1_grating_criterion.md | 仿真/判据校准 | 〔文内:2026-05-29·声学仿真专家 teammate〕栅瓣判据校准：半波长 3.12kHz[L1] vs 严格 6.24kHz[L1]；broadside 真问题带 6.2–8kHz | 无状态行；基线几何『CTO 锁定硬决策，不在讨论范围』(L9) |
| 2026-06-09 | sprint3/acoustic/pf8/p0a2_grating_cost.md | 仿真/代价分析 | 〔文内:2026-05-29·声学仿真专家 teammate〕栅瓣代价：方向 1 规格降级到 6kHz(对内)/5kHz(对外)可行；方向 2 纯加权消栅瓣物理证伪；ESCALATE#1=NO | 「ESCALATE#1：不升级（NO ESCALATE）」(L163) |
| 2026-06-09 | sprint3/acoustic/sweep_d55_report.md | 声学仿真报告 | 〔文内:2026-05-27·AcousticSimulationAgent v1.0〕Sprint3 N=16/d=55/L=825 阵因子(16 独立 vs 8 对称对)各频 BW/SLL/栅瓣+竞品 SPL 对照；SPL 预测 117.1dB 占位 | 「版本：Sprint3-AC-WP01-v1」(L8)；「SPL预测列为占位/低置信度估算，不可对外引用（DEC-S3-DSP-05 已降级）」(L64) |
| 2026-06-09 | sprint3/audit/A1_static_weight_tuning.md | 声学分析(三轨) | 〔文内:2026-05-29·AcousticSimulationAgent v1.0〕静态加权(Dolph-20/22/25、Taylor-25)能否不破 BW@1k≤30° 而把 2k/90° 衰减由 23.01dB 拉到≥25dB(JY/T 表9 一级，即 R10)；numpy+MATLAB 三轨 | 「NO —— 静态加权无法在不破 BW@1k ≤30° 规格的前提下把 2kHz/90° SPL差值拉到 ≥25dB（一级）」(L69) |
| 2026-06-09 | sprint3/audit/A2_fib_feasibility.md | 声学预研(桌面) | 〔文内:2026-05-29·AcousticSimulationAgent v1.0〕FIB(频率不变波束)桌面预研：第①层子带标量加深(声称零成本)+第②层短FIR(+22.3MMAC/s、裕量19.1×、延迟17.70ms)；E-NEW-5 未触发 | 「Sprint 4 战略储备预研（≤9 调用桌面预研，非设计冻结）」(L3)；「E-NEW-5：未触发…可作为 Sprint 4 候选」(L21)；末行「待 Critic 评审 → Team Lead」(L174) |
| 2026-06-09 | sprint3/audit/A3_decision_recommendation.md | 决策建议 | 〔文内:2026-05-29·PM 综合〕R10(2k/90° 缺 1.99dB)四选项对比(1 全局加权不可行/1.5 子带标量加深/2 FIB/3 二级保底)+给 CTO 的三档建议 | 「PM 综合…待 Critic 复核」(L5)；「待 Critic 复核 A1+A2+A3 一致性…」(L45) |
| 2026-06-09 | sprint3/audit/NEXT_SESSION_BOOTSTRAP.md | 交接/启动指南 | 〔文内:2026-05-30·PM〕self-contained 启动指南：项目基线、触发 A–F 可复制 prompt、LOCKED 决策表、R1–R13、POLICY v1.5、待 CTO 动作 | 「Sprint 3 桌面阶段 ~96% 完成；剩余卡外部数据…Agent Team 待命，零自动推进」(L6)；末行「待 Critic 复核」(L193) |
| 2026-06-09 | sprint3/audit/PF9_post_simulation_panorama.md | 全景/缺口评估 | 〔文内:2026-05-29·PM(块A/B)+acoustic(块C.1/C.3)+Critic(块C.2)〕Sprint3 仿真全景(已完成清单+撤回项)、未做项缺口分类(唯一 P0=R1 EZKIT MCPS)、与竞品 PDF 对比可行性(仅 3 项定性) | 「Critic（PASS_WITH_MINOR，零 BLOCKER）」(L170)；L53 含 2026-09-26 勘误(经 33b1966 追加) |
| 2026-06-09 | sprint3/audit/POLICY_v15_draft.md | 制度草案 | 〔文内:2026-05-30·Critic(critic-itc-001)〕POLICY-PROV-001 v1.3→v1.5：v1.4 双轨/三轨独立工具复核(LESSON-012)+v1.5 外部输入 24h 入库/铁律六/C8(缘起 docx 入手未入库) | 「状态：DRAFT 待 CTO 审批」(L3) |
| 2026-06-09 | sprint3/audit/SPRINT3_DESKTOP_CLOSURE.md | 总结/索引 | 〔文内:2026-05-29·PM〕Sprint3 桌面阶段最终交付包：交付物索引、锁定基线+硬约束、gating 清单、R1–R12、制度成熟度、→Sprint 4/EZKIT 移交 | 「Sprint 3 桌面阶段彻底收尾的权威索引 + 最终状态综述」(L5)；「Agent Team 待命，零自动推进」(L58) |
| 2026-06-09 | sprint3/audit/competitor_directivity_qualitative.md | 声学分析(定性) | 〔文内:2026-05-29·acoustic-simulation teammate〕竞品(消声室 SPL[L1])与我方阵因子[L2]的归一化衰减趋势定性对比+4kHz 反常 SPL 域背书+后向单边登记；零 BW、零绝对 SPL | 「[非 Gate 级验证 / 仅作 COMSOL·消声室立项动机]」(L12)；「Critic C1/C2/C7 门禁复核 PASSED，零 BLOCKER」(L107) |
| 2026-06-09 | sprint3/audit/comsol_geometry_input.md | 输入登记表 | 〔文内:2026-05-29·acoustic-simulation teammate〕COMSOL 障板/箱体衍射立项前的几何/边界输入登记(N=16/d=55/L=825[L1]；Q-③盆口、Q-④箱体宽深、Q-⑤后腔吸音 pending) | 「纯几何/边界输入登记。本表不建模、不跑仿真、不出任何声学结论」(L7) |
| 2026-06-09 | sprint3/audit/critic_a123_rv.md | Critic 评审 | 〔文内:2026-05-29·Critic〕A1/A2/A3 合并复核：A1 PASS(独立 scipy 复算)；A2 line91『竞品实测≈19.1°』触发 C2+C7 BLOCKER；A3 PASS(子带标量加深零成本经独立复算) | 「整体裁决：FAILED。A2 触发 C2 + C7 双 BLOCKER」(L20) |
| 2026-06-09 | sprint3/audit/critic_bootstrap_rv.md | Critic 评审 | 〔文内:2026-05-30(仅文末 L67)·critic-agent〕复核 NEXT_SESSION_BOOTSTRAP：完整性/准确性/self-contained/无 TBD/红线/路径 12 of 12 实存 | 「裁决：PASS_WITH_MINOR（无 BLOCKER；2 项 MINOR）」(L6) |
| 2026-06-09 | sprint3/audit/critic_c8_first_run.md | Critic 评审 | 〔文内:2026-05-30·critic-agent〕C8 入库门禁首次实战(CTO 首次外部接收声明 3 份：抓 GAP-1 docx② 与 GAP-2 JY/T 原件『声明入库、实际未真入库』)+PRD v2.4 专职复核 | 「抓到 2 gap（GAP-1 docx② / GAP-2 JY/T 原件）；均 MAJOR」(L108)；「PRD v2.4 = PASS，可进入下一阶段」(L112) |
| 2026-06-09 | sprint3/audit/critic_compqual_gate.md | Critic 评审 | 〔文内:2026-05-29·Critic(critic-itc-001)〕对 DOC-COMP-QUAL-01 做 C1/C2/C7+PF-9 复发四问专查；抽查竞品衰减值确取自 §7 一手 SPL | 「VERDICT：PASSED（零 BLOCKER，零 MAJOR）」(L52) |
| 2026-06-09 | sprint3/audit/critic_matlab_rv.md | Critic 评审 | 〔文内:2026-05-29·Critic Agent(critic-itc-001)〕MATLAB 三轨验证全段门禁+独立复算 4 关键值(WNG 11.868、草稿 bug −0.173dB=误差 12.041dB 等) | 「整体裁决 PASS — 零 BLOCKER」(L15) |
| 2026-06-09 | sprint3/audit/critic_panorama_gate.md | Critic 评审 | 〔文内:2026-05-29·critic-itc-001〕PF9 仿真全景 C1/C2/C7 门禁；C.3 三项安全推荐复核；新 PF-9 隐患扫描 | 「PASS_WITH_MINOR」(L13) |
| 2026-06-09 | sprint3/audit/critic_std_a_rv.md | Critic 评审 | 〔文内:2026-05-29·Critic〕标准 12 点合规补算复核：两个前置陷阱(平面口径/180° 对称)+R8 独立复算 5.8574dB | 「裁决：PASS（零 BLOCKER）」(L3) |
| 2026-06-09 | sprint3/audit/critic_x5_x1_review.md | Critic 评审 | 〔文内:2026-05-29·critic-agent〕X1：KB-HW-001 归档复核(C1–C7、6/6=文档级闭环、PO 未越权)；X5：POLICY v1.5『入手未入库』候选评估 | 「X1：PASSED / X5：POLICY v1.5 候选 — 倾向成立…待 CTO 确认正式接收时间后定」(L86-87) |
| 2026-06-09 | sprint3/audit/doc_v15_review.md | 文档复核 | 〔文内:2026-05-30·Project Document Agent〕复核 POLICY v1.5 草案：完整性/一致性/落地性 PASS；指出 C8 执行盲点(需『CTO 外部接收声明义务』) | 「可提交，但建议附带缺口②一并请 CTO 决策」(L65) |
| 2026-06-09 | sprint3/audit/drv_test_metadata_query.md | 询问单 | 〔文内:2026-06-01·PM 直跑〕测试阶段驱动 T/S(LEAP-4)+SPL(LMS) 两图的 6 项 metadata 询问+SPLo 82.16dB vs 通带~90dB 的 8dB 差归因；旧 117 占位退役 | 「X2 三轨阻塞于本单回填」(L46) |
| 2026-06-09 | sprint3/audit/ezkit_bringup_checklist.md | 检查清单/runbook(文档提取) | 〔文内:无日期·hardware-design teammate〕EV-21569-EZKIT 物理上板 bring-up：安全闸门(版本确认前禁上电/接 ICE)+三版差异表 V1.0/V1.2/V2.1+6 项信息(JTAG 顺序/BOOT/JP1 供电/LED 判据/CCES session)+可打勾上电流程 | 「纯文档提取，未跑仿真」(L6)；「【待 CTO 确认 REV 后回填专属接线】」(L272) |
| 2026-06-09 | sprint3/audit/ezkit_fira_baseline.md | 测试协议/runbook | 〔文内:2026-06-02·testing teammate〕ADI 官方 FIR_Multi_Channel_Processing(浮点,4ch,64/4096-tap)的 FIRA cycle baseline 测量协议+PF-1 七判据核对表；cycle 全为占位 | 「协议 + 骨架 + 核对表已出稿；cycle 实测值待 CTO 台架回填」(L4) |
| 2026-06-09 | sprint3/audit/fira_fit_assessment.md | 技术评估 | 〔文内:2026-06-02·dsp-algorithm teammate〕ADI FIRA 加速器/EE-408 例程 vs 我方 4 子带树形滤波器组：容量/结构匹配/定点 vs 浮点/cycle 基准(ADI 标称 0.25)/迁移清单 | 「总判定：⚠️ 部分适配（可用且有益，但非 1:1 即插即用，且非必需）」(L208) |
| 2026-06-09 | sprint3/audit/hardware_followup_queries.md | 追问跟踪表 | 〔文内:2026-05-29(05-30 更新块 L8)·PM〕KB-HW-001 使 WO-S3-001 六项未知量文档级闭环后的 5 项精度追问(Q-①~⑤)+Q-0(3W 口径)；05-30 KB-HW-002 回 4/5 | 「硬件团队已回 4/5…Q-④ ⏳ pending；Q-0 ⏳ pending」(L8-14) |
| 2026-06-09 | sprint3/audit/matlab_independent_verification.md | 验证汇总 | 〔文内:2026-05-29·acoustic-simulation+Critic+PM〕MATLAB 三轨独立验证完整指标体系(SLL/WNG/DI/MC/超指向/8 路等价)汇总 | 「6 指标三轨全对照通过，零 BLOCKER，零 E-MATLAB-1」(L13) |
| 2026-06-09 | sprint3/audit/matlab_verify_m0_plan.md | 验证(规划) | 〔文内:2026-05-29·声学仿真专家 teammate(agent-acoustic-sim-v1)〕M0 预探：MATLAB R2026a+Signal Processing+Phased Array 工具箱探针、三轨现有值基线表、M1–M3 规划 | 「E-MATLAB-2 不触发」(L24) |
| 2026-06-09 | sprint3/audit/matlab_verify_m1_sll_wng_di.md | 验证 | 〔文内:2026-05-29·声学仿真专家 teammate(agent-acoustic-sim-v1)〕M1：SLL/WNG/DI 频率扫描三轨(DI 为首算)；numpy 草稿 WNG 笔误 −0.173dB 被三轨交叉核抓出 | 「无任何两轨不一致 → 不触发 E-MATLAB-1，不 ESCALATE」(L19) |
| 2026-06-09 | sprint3/audit/matlab_verify_m2_mc.md | 验证 | 〔文内:2026-05-29·声学仿真专家 teammate(agent-acoustic-sim-v1)〕M2：公差蒙特卡洛 N=3000 三轨(三个不同种子)；8 对称对@1kHz P(BW>30°)≈5.8%(真实工程风险) | 「三轨收敛一致，PASS，无 E-MATLAB-1，无 BLOCKER，不 ESCALATE」(L140) |
| 2026-06-09 | sprint3/audit/matlab_verify_m3_superdir_8pair.md | 验证 | 〔文内:2026-05-29·声学仿真专家 teammate(agent-acoustic-sim-v1)〕M3：超指向 MVDR d=55(ε 扫描)三轨 bit 级一致+8 路 A/B 串联 broadside 与 16 元独立等价性(依赖权中心对称) | 「无任意两轨不一致 → E-MATLAB-1 不触发。无 BLOCKER，无需 ESCALATE」(L113) |
| 2026-06-09 | sprint3/audit/sprint4_inputs.md | 输入登记表 | 〔文内:2026-06-02·PM〕Sprint 4 输入清单：INPUT-1 FIRA Split-Task 迁移复杂度 HIGH(CTO 拍板)；INPUT-2 COMSOL 输入；INPUT-3 硬件追问残留；INPUT-4 驱动绝对 SPL | 「INPUT-1：FIRA Split-Task 迁移复杂度 🔴 HIGH（CTO 拍板 2026-06-02）」(L10) |
| 2026-06-09 | sprint3/audit/standard_compliance_check.md | 声学分析(标准) | 〔文内:2026-05-29·AcousticSimulationAgent v1.0〕JY/T 表9 国产标准 12 点 SPL 差值仿真合规检查：7/8 可评点一级、2k/90° 二级、4 个 180° 点不可评；两个口径陷阱裁定 | 「不 ESCALATE（…前提是音柱水平安装）」(L3) |
| 2026-06-09 | sprint3/critic/critic_review_s3.md | Critic 评审 | 〔文内:2026-05-27·Critic Agent〕REV-S3-CRITIC-001 三领域评审：声学/DSP PASSED_WITH_MINOR，硬件 FAILED(F-X01：TDM 槽数/BCLK/DAC 通道失配)；含竞品合法性边界(供 DEC-S3-003) | 「整体放行状态：有条件 FAIL」(L24) |
| 2026-06-09 | sprint3/dsp/cces_skeleton/cces_skeleton_description.md | 工程骨架描述 | 〔文内:无日期·DSP算法专家 Agent〕CCES 工程骨架 v0.1(目录树/itc_config.h/SPORT-TDM 骨架/D-C 权重占位) | 「版本: v0.1 骨架（Sprint 3 EZKIT 验证用）」(L5) |
| 2026-06-09 | sprint3/dsp/dsp_8ch_report.md | 技术报告(DSP) | 〔文内:2026-05-27·DSPAlgorithmAgent v1.0〕Sprint3 DSP 8 通道算法链重设计：算力 30.56MMAC/s(纸面)→2026-05-28 纠正为 45.7/88.7；延迟 12.53ms；8 驱 16 对称约束；CCES/SPORT 配置 | 「状态：REVIEW-READY（送 Critic 评审前）」(L4) |
| 2026-06-09 | sprint3/dsp/pf4/PF4_INTEGRATION_SUMMARY.md | 整合汇总 | 〔文内:2026-05-29·PM〕PF-4 定点化三件套整合：Sub-1/2/3 全 PASS_WITH_MINOR；揪出节点①半带 MAC 无饱和缺陷(1.73×) | 「三个子任务全部 PASS_WITH_MINOR」(L13)；「PF-4 桌面层面可关闭」(L14) |
| 2026-06-09 | sprint3/dsp/pf4/WO_node1_saturation_fix.md | 代码修复工单 | 〔文内:2026-05-29·DSP 算法专家 teammate 提出；PM 直跑验证〕WO-PF4-NODE1-SAT：节点①半带 MAC 回量化无饱和→加饱和钳位；PM 直跑验证 SNR 177.6dB、SAT/UNSAT bit-exact | 「批准：CTO（总工）批立即桌面修复」(L10)；「桌面闭环」(L85) |
| 2026-06-09 | sprint3/dsp/pf4/critic_fix_verify.md | Critic 评审 | 〔文内:2026-05-29·Critic〕独立重编译/复算复核节点①饱和修复(Σ绝对值(h_q15)/32768=1.73087、1.7309×FS、SAT ON/OFF) | 「PASS_WITH_MINOR — 置信度 HIGH」(L14) |
| 2026-06-09 | sprint3/dsp/pf4/critic_review_pf4.md | Critic 评审 | 〔文内:2026-05-29·Critic〕PF-4 三件套合并评审：D3+(现行 LOCKED=63 抽头半带原型)、D4+(Q 格式一致)、三发现独立复算 | 「总裁决：三 Sub 全部 PASS_WITH_MINOR，无 BLOCKER、无 MAJOR」(L271) |
| 2026-06-09 | sprint3/dsp/pf4/sub1_q15_stopband.md | 仿真报告(DSP) | 〔文内:2026-05-29·DSP 算法专家 teammate〕Sub-1：Q15 系数对阻带劣化(真实阻带 15k+ 浮点 73.3→Q15 71.3dB；旧脚本 13k 口径『假 FAIL』)；L53-68 含 2026-09-26 勘误 | 无状态行；全部 [L2] 桌面仿真「无 L1 实测（EZKIT 未到货）」(L4) |
| 2026-06-09 | sprint3/dsp/pf4/sub2_fixed_vs_float.md | 仿真报告(DSP) | 〔文内:2026-05-29(仅文末 L199)·DSP 算法专家 teammate〕Sub-2：定点 Q31 vs 浮点 SNR：重建层 316dB=PR 抵消假象；纯算术 172.8–175.5dB；端到端 74.6–78.7dB(Q15 系数底)；L85 含 2026-09-26 勘误 | 「是否 ESCALATE：无 ESCALATE」(L189-191) |
| 2026-06-09 | sprint3/dsp/pf4/sub3_q46_overflow.md | 分析报告(DSP) | 〔文内:2026-05-29·DSP 算法专家 teammate〕Sub-3：Q46 累加器最坏溢出：节点①回量化 1.73× 溢出、节点② 0.9998× 安全 | 「不触发 ESCALATE」(L23,L163) |
| 2026-06-09 | sprint3/hardware/selfdev_bom.md | 设计文档(硬件) | 〔文内:2026-05-27·HardwareDesignAgent v1.0〕自研主板 BOM v2(长期方案)：ADSP-21569+DDR3+SPI Flash+ADAU1962A(8ch)+ACM3128A×4(或 TAS5825M)+电源树+热设计；整机 ¥345–683[估算] | 「状态：设计建议（仅供参考，不含任何采购/PO 动作）」(L8) |
| 2026-06-09 | sprint3/hardware/transition_board_design.md | 设计文档(硬件) | 〔文内:2026-05-27·HardwareDesignAgent v1.0〕过渡转接板 v2：EZKIT SPORT0 TDM-8→ADAU1962A 8ch DAC→电平匹配→竞品 ACM3128A(情形① 模拟/情形② 数字 TDM)；U1–U6 阻塞项 | 「状态：设计建议（仅供技术评估，不含任何采购/PO 动作）」(L8)；「条件方案 v2，待《6 项未知量拆机确认报告》签署后升 v3」(L292) |
| 2026-06-09 | sprint3/pf8/L1_test_window_tasklist.md | 任务清单/DAG | 〔文内:2026-05-29·PM 直跑〕四个触发器(T1 EZKIT 到货/T2 T-S/T3 消声室/T4 COMSOL)驱动的 L1 实测窗口任务 DAG；T1 行写『海外周期（已下单）』 | 「外部数据到位即激活」(L74) |
| 2026-06-09 | sprint3/pf8/PF8_retrospective.md | 复盘/教训库 | 〔文内:2026-05-29·Critic 主笔(§7、§8 由 PM 据 CTO 钦定补入)〕PF-8(d=30 目测当 LOCKED+L1 冲突未重审)时间线/失误点/制度补丁映射/持久记忆治理/制度实战检验附录 A-B-C | 「性质：项目长期资产 / 永久教训库条目」(L7)；「ESCALATE：无」(L23) |
| 2026-06-09 | sprint3/pf8/PF9_C7_drafts.md | 制度草案 | 〔文内:2026-05-29(仅文末 L78)·Critic〕PF-9(撤回未传播)定义+Critic C7 撤回传播门禁+POLICY v1.2→v1.3 变更清单(铁律五) | 「状态：DRAFT — 待 CTO 审，未落地」(L3) |
| 2026-06-09 | sprint3/pf8/PF_atlas.md | 复盘/图谱 | 〔文内:2026-05-29·PM 直跑〕PF-1~PF-8 假性完成按根因/病型/处置状态关联成图；同根=数字无来源身份证 | 「DOC-PF-ATLAS-001，PM 直跑」(L63) |
| 2026-06-09 | sprint3/pf8/blindspot_triage.md | 分类清单 | 〔文内:2026-05-29·PM 直跑〕audit §3 盲区清单三档分类(✅已闭环/🟢桌面可做/🔴卡数据) | 「DOC-BLINDSPOT-TRIAGE-001，PM 直跑」(L51) |
| 2026-06-09 | sprint3/pf8/critic_ai_citation_audit.md | Critic 评审 | 〔文内:无日期·Critic〕外部 AI 引用『竞品 BW@2k=14.9°/@4k=19.2°』合规判定：C1+C2 双 FAIL；PF-6 同款；建议新立 PF-9；内部 4 处残留为喂养源 | 「C1+C2 双 FAIL → 引用整体 BLOCKER（不合规）」(L47) |
| 2026-06-09 | sprint3/pf8/critic_c7_enew3_review.md | Critic 评审 | 〔文内:2026-05-29·Critic〕E-NEW-3 竞品 BW 残留清扫的 C7 首次实战复核：7 组已清(警示加、数值留)，残留 0 | 「C7 = PASS（残留 0 处）…整体裁决：PASS」(L74-76) |
| 2026-06-09 | sprint3/pf8/critic_ctier_eval.md | Critic 评估 | 〔文内:2026-05-29·Critic〕PF-9 处置是否由 B 档升 C 档：项目无客户/合同/生效对外 PRD→停在 B，列 4 个重启触发条件 | 「建议：停在 B 档（设触发条件重启 C 评估），不 ESCALATE」(L6) |
| 2026-06-09 | sprint3/pf8/critic_enew3_final_confirm.md | Critic 评审 | 〔文内:2026-05-29·Critic(critic-itc-001)〕E-NEW-3 全库 C7 最终确认(认证关闭) | 「verdict: PASSED / confidence HIGH」(L70) |
| 2026-06-09 | sprint3/pf8/critic_final_s1.md | Critic 评审 | 〔文内:2026-05-29·Critic Agent〕PF-8 终审段 1/3：POLICY v1.2(L0/铁律四/C6)完整性+DEC-S3-GEOM-01 六字段+L0 标签一致 | 「裁决：PASS（HIGH 置信）；无 BLOCKER，无 MINOR」(L7) |
| 2026-06-09 | sprint3/pf8/critic_final_s2.md | Critic 评审 | 〔文内:2026-05-29·Critic(critic-itc-001)〕PF-8 终审段 2/3：cces_template d=30 残留(现 55u/92u)已清+活文档无 d=30 现行基线+作废 banner | 「PASSED（三件全部 PASS）」(L59) |
| 2026-06-09 | sprint3/pf8/critic_final_verdict.md | Critic 评审 | 〔文内:2026-05-29·Critic Agent〕PF-8 终审总裁决(段 3/3)：handover v1.2/audit v2.2/C1–C6/收尾同步；遗留 MINOR=critic skill.md §11 未同步 C6 | 「全域终审总裁决：PASS_WITH_MINOR」(L13) |
| 2026-06-09 | sprint3/pf8/critic_land_review.md | Critic 评审 | 〔文内:2026-05-29·Critic〕PF-9/C7/POLICY v1.3 三文件落地复核 | 「裁决：PASS_WITH_MINOR（置信度 HIGH）」(L7) |
| 2026-06-09 | sprint3/pf8/critic_p0b_review.md | Critic 评审 | 〔文内:2026-05-29·Critic〕复核 d=30 资产盘点三档分类逻辑(含 #14 cces 走重审不走 ESCALATE#2) | 「裁决：PASS_WITH_MINOR ｜ Confidence: HIGH」(L9) |
| 2026-06-09 | sprint3/pf8/p0b_asset_inventory.md | 资产盘点表 | 〔文内:2026-05-29·PM 直跑〕d=30 资产盘点 31 处：重审 14/作废 11/不影响 6；cces_template 硬编码 d=30(near-miss#2)；工装夹具须重做 | 「待复核：Critic（…复核三档分类判定逻辑…）」(L6) |
| 2026-06-09 | sprint3/pf8/p1b_prd_alignment.md | PRD 对齐/评估 | 〔文内:2026-05-29·Project Document Agent〕PRD v2.3 对齐 d=55/825mm；安装可行性[L3]；夹具重做时间表；PCB 节奏不受影响；对内口径说明 | 「ESCALATE：无」(L20) |
| 2026-09-26 | sprint3/dsp/tree_filterbank.h.ERRATUM.md | 勘误旁注 | 〔文内:2026-09-26·ITC-PM(DEC-S7-RETRACT-SUBBAND-01)〕冻结头文件 tree_filterbank.h 的子带边界注释勘误：真实分界 3k/6k/12k，detail 带=未对齐梳状残差，不能按子带加权 | 「tree_filterbank.h 勘误旁注（本体为冻结件，字节不改）」(L1) |

## 2. 时间线事件

约定：本节及以后 path 缺省相对 `sprint3/`(`acoustic/pf8/…` 与 `pf8/…` 是两个不同目录)；以 `knowledge_base/` 或 git 提交号开头的是 sprint3 之外的旁证，已逐条标注。日期均为文内自报，除非写明 git。

| 日期 | path:line | 事件 |
|------|-----------|------|
| Sprint 2 期间(日期未见) | pf8/PF8_retrospective.md:44-45 | d=30mm 视觉估测[L0]进入设计，被 DEC-S2-006 LOCKED；此时 POLICY-PROV-001 尚未建立 |
| Sprint 2 期间(日期未见) | acoustic/sweep_d55_report.md:156-160；pf8/critic_enew3_final_confirm.md:45 | Sprint 2 对竞品几何的反推估算 N≈20/d≈35mm/L≈665mm(后被拆机实测取代，prd_update §2 对应处加『已被拆机真值取代』) |
| Sprint 2 期间(日期未见) | hardware/selfdev_bom.md:9,175-177 | Sprint 2 BOM v0(DEC-S2-005)：16 路独立驱动假设，¥1169–2065 |
| 2026-05-26 | pf8/p0b_asset_inventory.md:47；pf8/critic_final_s2.md:49 | Gate 1 基线文件 `deliverables/Gate1-baseline-array-validation-2026-05-26.md`(「Gate1 锁 d=30/0.45m」，后加 PF-8 作废 banner) |
| 2026-05-26 | acoustic/pf8/p0a2_grating_cost.md:29 | CTO 确认「本产品仅需 ≥1kHz 指向」[directivity-band-requirement，2026-05-26] |
| 2026-05-26 | pf8/p1b_prd_alignment.md:75,79,85 | 采购/工装/消声室倒推表基准日(T−6=2026-05-26)；首次消声室实测窗口目标 ~2026-07-07(T) |
| 2026-05-26 15:54 / 05-28 17:09 | dsp/pf4/critic_review_pf4.md:23-25 | 两份 437 抽头全速率 fir_coeffs.h 的时间戳(历史核，已被 63 抽头树形取代) |
| 2026-05-27 | acoustic/sweep_d55_report.md:6,8；dsp/dsp_8ch_report.md:2；hardware/selfdev_bom.md:7；hardware/transition_board_design.md:7；critic/critic_review_s3.md:6 | Sprint 3 首批五份产出同日(声学/DSP/自研 BOM/转接板/Critic 评审)；文本已称「竞品拆机确认」(dsp/dsp_8ch_report.md:10)、「拆机实测」N=16/d=55(acoustic/sweep_d55_report.md:18-19) |
| 2026-05-27 | critic/critic_review_s3.md:18-24,122-153 | REV-S3-CRITIC-001：声学/DSP PASSED_WITH_MINOR，硬件 FAILED(F-X01：TDM 槽数/BCLK/DAC 通道失配)；并给竞品合法性边界(L51-69,L201-203) |
| 2026-05-27(同日) | hardware/selfdev_bom.md:5,11；hardware/transition_board_design.md:5,11-14 | 硬件文档升 v2 闭环 F-X01：DAC 由 ADAU1966A 16ch 改 ADAU1962A 8ch，TDM 统一 8 slot/BCLK 12.288MHz |
| 2026-05-27 19:56 | audit/critic_x5_x1_review.md:59；audit/critic_c8_first_run.md:27 | `定向音柱AI数据.docx` 磁盘 mtime |
| 2026-05-28 | pf8/PF8_retrospective.md:62 | POLICY-PROV-001「2026-05-28 才生效」(缘起 PF-1 算力审计) |
| 2026-05-28 | dsp/dsp_8ch_report.md:14 | P0-2 树形 C 实算纠正：MCPS 8ch=45.7/16ch=88.7 MMAC/s，裕量 33×/17×[L2]，取代纸面 49× |
| 2026-05-28 | audit/POLICY_v15_draft.md:11；audit/critic_c8_first_run.md:17 | 硬件团队把 `定向音柱AI数据.docx` 发给 CTO(两处所述) |
| 2026-05-28 17:38 | dsp/pf4/critic_review_pf4.md:241 | `tree_filterbank.h` 时间戳(三个 PF-4 子任务同引此版本的 Q 锁) |
| 2026-05-29 | pf8/PF8_retrospective.md:49-51 | PF-8 审计暴露「假性并存」；CTO 拍板 DEC-S3-GEOM-01(撤 d=30、统一 d=55)+SC-S3-GEOM-01；POLICY v1.2(L0/铁律四/C6)落盘 |
| 2026-05-29 | pf8/p0b_asset_inventory.md:12-14；pf8/critic_p0b_review.md:9 | d=30 资产盘点 31 处(重审 14/作废 11/不影响 6)及 Critic 复核 |
| 2026-05-29 | acoustic/pf8/p0a1_grating_criterion.md:78-88；acoustic/pf8/p0a2_grating_cost.md:16-20,143-144 | 栅瓣判据校准(broadside 真问题起点 6.24kHz)；规格降级 6kHz(对内)/5kHz(对外) |
| 2026-05-29 | pf8/p1b_prd_alignment.md:16-20,24-39 | PRD v2.3 对齐 d=55/825mm；安装可行性[L3]；PCB 节奏不受影响、无 ESCALATE |
| 2026-05-29 | pf8/critic_final_s1.md:7；pf8/critic_final_s2.md:59；pf8/critic_final_verdict.md:13 | PF-8 终审三段：PASS / PASSED / PASS_WITH_MINOR |
| 2026-05-29 | dsp/pf4/PF4_INTEGRATION_SUMMARY.md:13-15；dsp/pf4/WO_node1_saturation_fix.md:9-10,59-86；dsp/pf4/critic_fix_verify.md:14 | PF-4 定点化三件套 PASS_WITH_MINOR；节点①半带 MAC 回量化无饱和(1.73×)→CTO 批准立即桌面修复→PM 直跑验证 SNR 177.6dB→Critic 复核 PASS_WITH_MINOR |
| 2026-05-29 | pf8/critic_ai_citation_audit.md:1,43-47,68-70；pf8/PF9_C7_drafts.md:7 | 外部 AI 把竞品 BW 14.9°/19.2° 称「竞品 L1 实测」→Critic 判 C1+C2 双 FAIL(BLOCKER)，提议新立 PF-9(撤回未传播) |
| 2026-05-29 | pf8/critic_land_review.md:6-7,11-22；pf8/critic_c7_enew3_review.md:76；pf8/critic_enew3_final_confirm.md:62-70；pf8/critic_ctier_eval.md:6 | POLICY v1.3(铁律五/C7)落地；E-NEW-3 全库清扫+C7 终扫 PASSED；C 档评估「停在 B 档」 |
| 2026-05-29 | audit/matlab_independent_verification.md:4,13-16；audit/critic_matlab_rv.md:15 | MATLAB 三轨独立验证 6 指标；M1 numpy WNG 12dB 笔误被抓出；Critic RV PASS |
| 2026-05-29 | audit/standard_compliance_check.md:3,73-75；audit/critic_std_a_rv.md:3 | JY/T 表9 12 点：8 个可评点中 7 点一级、2k/90° 仅二级；4 个 180° 点不可评 |
| 2026-05-29 | audit/A1_static_weight_tuning.md:69；audit/critic_a123_rv.md:16-20；pf8/PF8_retrospective.md:165 | A1 结论 NO；A2 line91 触发 C2+C7 BLOCKER(整体 FAILED)，修复后 delta 转 PASS |
| 2026-05-29 | audit/PF9_post_simulation_panorama.md:4,63,94；audit/competitor_directivity_qualitative.md:4；audit/critic_panorama_gate.md:13；audit/critic_compqual_gate.md:52 | 仿真全景/缺口(唯一 P0=R1 EZKIT MCPS)与竞品定性对比；Critic 门禁 PASS |
| 2026-05-29 | audit/critic_x5_x1_review.md:59,86-87；audit/hardware_followup_queries.md:5,21-28；audit/comsol_geometry_input.md:3-8 | KB-HW-001 提取归档；WO-S3-001 六项未知量「文档级闭环」；5 项精度追问；COMSOL 几何登记(KB-HW-001 date 2026-05-29 另见 audit/critic_c8_first_run.md:26) |
| 2026-05-29 | pf8/L1_test_window_tasklist.md:15；pf8/PF_atlas.md:5；pf8/blindspot_triage.md:5 | EZKIT「海外周期（已下单）」；PF-1~8 图谱；盲区三档分类(待命期元任务) |
| 2026-05-29 | audit/SPRINT3_DESKTOP_CLOSURE.md:4,11,55-58 | Sprint 3 桌面阶段收尾；「EZKIT 到货即启动」；Agent Team 待命零自动推进 |
| 2026-05-30 | audit/hardware_followup_queries.md:8-15 | KB-HW-002(含追问回复版)到位：Q-①(15Ω=直流 Re[L1])/②/③/⑤已回；Q-④箱体宽深、Q-0(3W 口径)pending |
| 2026-05-30 | audit/NEXT_SESSION_BOOTSTRAP.md:4-6；audit/critic_bootstrap_rv.md:6,67 | 下一 Session 启动指南(桌面阶段~96%)；Critic PASS_WITH_MINOR |
| 2026-05-30 | audit/POLICY_v15_draft.md:3-11；audit/doc_v15_review.md:3,63-67；audit/critic_bootstrap_rv.md:30 | POLICY v1.4+v1.5 草案(双轨核/外部输入 24h/铁律六/C8)→文档复核→「POLICY-PROV-001 v1.5（CTO 审批 2026-05-30）」 |
| 2026-05-30 | audit/critic_c8_first_run.md:5,31-43,108-112 | C8 首次实战：声明入库≠真入库，抓 GAP-1(docx②)/GAP-2(JY/T 原件)；PRD v2.4 专职复核 PASS |
| 2026-05-30 | audit/NEXT_SESSION_BOOTSTRAP.md:105,193 | 竞品 SPL 原件 KB-SPL-001「CTO 已确认」归属=竞品 |
| 2026-06-01 | audit/drv_test_metadata_query.md:4-5,34 | 测试阶段驱动 T/S(LEAP-4)+SPL(LMS) 两图(KB-DRV-TEST-001)；6 项 metadata 询问；旧 117dB 占位「整体推翻」 |
| 2026-06-01 | knowledge_base/ezkit/INDEX.md:4-5,15-16,25(旁证，sprint3 外) | KB-HW-EZKIT-001 建库；vendor_docs/bsp「待 CTO 拷入」；CCES 2.12.1 安装包已在手 |
| 2026-06-02 | audit/fira_fit_assessment.md:4,206-226 | FIRA 适配性评估：⚠️部分适配(Split-Task；定点 signed-fractional 口径为 HIGH 风险) |
| 2026-06-02 | audit/sprint4_inputs.md:4,10-14 | Sprint 4 输入清单建立；CTO 拍板 FIRA Split-Task 迁移入 Sprint 4(🔴HIGH) |
| 2026-06-02 | audit/ezkit_fira_baseline.md:3-4,40-46,139 | ADI 官方 FIR 例程 FIRA baseline 测量协议；板=AD-EXKIT V2.1+SOM REV1.1+21569KBCZ10(CTO 肉眼确认丝印)；「本轮无 cycle 数字」 |
| 2026-06-02 | audit/BENCH_OPS_CARD.md:3-7,11-44；git `13be4b3` | 台架 CCES 操作卡(Phase0–4)；该文件 git 入库于 2026-06-02(sprint3 里唯一当时入库的 md)；git 根提交 `4bf0f52` 同日 14:03 |
| 日期未见(≤2026-06-02) | audit/ezkit_bringup_checklist.md:10-28,272-279 | EZKIT 物理上板 bring-up 检查清单(三版差异表；「CTO 确认后回填专属接线」栏空白)；被 audit/BENCH_OPS_CARD.md:24、audit/ezkit_fira_baseline.md:44,46 引为源文档 |
| 2026-06-09 | git `43aad40` | 批量入库：62/64 个 sprint3 md 的首次提交 |
| 2026-09-26 | dsp/tree_filterbank.h.ERRATUM.md:3-15；git `33b1966` | 子带边界撤回(DEC-S7-RETRACT-SUBBAND-01)：真实分界 3k/6k/12k；sprint3 内另 4 个文件(PF9 panorama L53、sub1 md L68、sub2 md L85 及 2 个 py 头注)被加勘误标 |

## 3. 前期环节线索

### 3.0 一眼结论(各条细节与出处见 3.1–3.6)
- 需求/PRD：只有 PRD 修订记录(v2.3→v2.5)和指标散见，PRD 初版与来源未见。
- 竞品拆机：有结论(N=16/d=55/L=825、8 路 A/B 对称串联、架构要素)和 6 项未知量清单，**无日期/执行人/竞品型号，拆机报告本体不在 sprint3**。
- 选型：DEC-S1-001/002/004、Gate 1/2、DEC-S2-0xx、DEC-S3-PROC-01 只有『状态表』，**无决议日期与候选对比**；自研 BOM(无采购/PO)、DAC/功放取舍有 2026-05-27 记录。
- EZKIT：2026-05-29 写「已下单(海外周期)」；2026-06-02 文本中实物板(AD-EXKIT V2.1/SOM REV1.1)已在手，**到货日与采购细节未见**，且板型口径有出入(D5)。
- 调研/入库：**未见 GitHub、论文调研**；资料入库有 KB-HW-001/002、KB-SPL-001、KB-DRV-TEST-001、JY/T 图的时序记录(2026-05-29～06-01)，并由此催生铁律六/C8。
- 治理：POLICY-PROV-001 2026-05-28 生效，05-29 升 v1.2/v1.3，05-30 批准 v1.5；角色与流程见 3.6，团队创建日期未见。

### 3.1 需求指标 / PRD — 有部分记录(PRD 本体不在 sprint3)
- 【有记录】产品定位：相控阵线阵定向音柱(DAS+4 子带)，ADSP-21569，场景「博物馆/车站/商场分区广播」，水平安装(SC-S3-GEOM-02)——audit/NEXT_SESSION_BOOTSTRAP.md:12,94。
- 【有记录】CTO 指向频段要求：仅需 ≥1kHz 指向、语音可懂度驱动(2026-05-26)——acoustic/pf8/p0a2_grating_cost.md:29-30；决策号 DEC-S1-002——audit/NEXT_SESSION_BOOTSTRAP.md:85；p0a2:28 记其原规格「≥1kHz 强指向到 8kHz」。
- 【有记录】指标：BW@1k≤30°(全角 −6dB，实算 29.28° 压线 0.72°)——audit/NEXT_SESSION_BOOTSTRAP.md:130；强指向上限 6kHz(对内)/5kHz(对外)——pf8/p1b_prd_alignment.md:33、audit/NEXT_SESSION_BOOTSTRAP.md:15；延迟 <30ms(DEC-S2-012，LOCKED-IN-PRINCIPLE，待市场对齐)——audit/NEXT_SESSION_BOOTSTRAP.md:90、dsp/dsp_8ch_report.md:130；CTO 算力目标裕量 ≥10×——audit/fira_fit_assessment.md:170、pf8/L1_test_window_tasklist.md:28；Dolph-20/N=16/4 子带(DEC-S2-007/008/009)——audit/NEXT_SESSION_BOOTSTRAP.md:89。
- 【有记录】标准：JY/T 表9 国产标准 12 点；二级保底=锁定承诺，一级=冲刺(非承诺)——audit/SPRINT3_DESKTOP_CLOSURE.md:30、audit/standard_compliance_check.md:73-75；表10(SPL≤75dB(A)/不均匀度/STIPA/GB3096)全部待实测——audit/critic_c8_first_run.md:94-95。
- 【有记录】PRD 版本链：v2.3(2026-05-29，d=55/825mm)——pf8/p1b_prd_alignment.md:16,24；v2.4(标准对齐重写，Gate PASS)——audit/SPRINT3_DESKTOP_CLOSURE.md:22、audit/critic_c8_first_run.md:64-112；v2.5(待 Q-② 频响口径)——audit/NEXT_SESSION_BOOTSTRAP.md:47。PRD 本体 `sprint2/docs/prd_update.md` 不在 sprint3。
- 【有记录】对外承诺尚未生效：无客户/合同/生效对外 PRD/对外样机(2026-05-29)——pf8/critic_ctier_eval.md:14-19。
- 【未见】PRD 初版的起草日期、来源(CTO PRD 原文)、需求访谈/客户输入：sprint3 内无。

### 3.2 竞品样机拆机 — 有记录，但只有二手引用，拆机本体不在 sprint3
- 【有记录】拆机结论：「拆机用游标卡尺实测 d=55mm/L=825mm | Sprint 3 | DEC-S3-003（拆机）/ WO-S3-001」——pf8/PF8_retrospective.md:46；N=16、d=55mm「拆机实测」，L_box=880mm「CTO 给出值」——acoustic/sweep_d55_report.md:18-22；8 路 A/B 对称串联(A1↔B16…)、全密闭箱、后腔连通、箱体宽深未给——audit/comsol_geometry_input.md:24-28,43-47。
- 【有记录】WO-S3-001「6 项未知量」U1(接口模拟/数字)、U2(N/d)、U3(功放最大输入)、U4(TDM 时序)、U5(功放板是否含 DSP)、U6(供电/地)——hardware/transition_board_design.md:274-281、hardware/selfdev_bom.md:338；拆机隶属「快速验证线」，目标「拿到 6 项未知量真值」——pf8/PF8_retrospective.md:73。
- 【有记录】竞品架构(拆机/硬件团队资料)：ADSP-21569+DDR3+SPI Flash boot；ACM3128A×4(8ch)驱 16 喇叭(A/B 串联 8 路 15Ω)；TDM；25MHz 晶振——hardware/selfdev_bom.md:19-24；「ADSP-21569KBCZ10…竞品同款」——hardware/selfdev_bom.md:67；拆机读取 IC 丝印属合法范围——critic/critic_review_s3.md:62。
- 【有记录】硬件团队资料 `定向音柱AI数据.docx`(KB-HW-001)使 6 项未知量「文档级闭环」(非测量级签署)——audit/hardware_followup_queries.md:5、audit/critic_x5_x1_review.md:39-41；含 [L1] 万用表单只 7.4Ω/3W、串联 15Ω(精度口径追问 Q-①)与 [L4] datasheet 项——audit/critic_x5_x1_review.md:33-34、audit/hardware_followup_queries.md:9-12。
- 【有记录】竞品消声室 SPL(5 频×6 角，@1m)在 `knowledge_base/competitor/full_teardown_v2.md §7`——pf8/critic_ai_citation_audit.md:22、audit/critic_panorama_gate.md:25,28；引用值 103.2/110.5/110.9/106.8/106.6dB——acoustic/sweep_d55_report.md:54-58；该 SPL 为「启用算法」口径——audit/drv_test_metadata_query.md:19；PDF 归属「CTO 已确认=竞品」——audit/NEXT_SESSION_BOOTSTRAP.md:105,193。
- 【有记录】两条线：快速验证线(竞品壳+转接板+EZKIT 跑自研算法)与自研主线(自研 PCB)——hardware/transition_board_design.md:20-45、pf8/L1_test_window_tasklist.md:17、pf8/PF8_retrospective.md:73。法律边界：购买竞品整机/台架测量/拆机读参数/借鉴架构拓扑合法；复制 PCB 与外壳 CAD、复用专有固件、对外展示改装样机为红线——critic/critic_review_s3.md:57-69,201-203；对外禁用改装样机——pf8/critic_ctier_eval.md:18。
- 【有记录】Sprint 2 对竞品几何的错误估算：视觉 d=30mm(L0)与 N≈20/d≈35mm/L≈665mm 反推——pf8/PF8_retrospective.md:44-45、acoustic/sweep_d55_report.md:156-160。
- 【未见】竞品品牌/型号、购入时间、拆机日期与执行人、拆机照片/BOM；`DEC-S3-003` 与 `WO-S3-001` 全文；拆机报告 `full_teardown_v2.md` 本体(在被 gitignore 的 knowledge_base/，旁证：该文件存在，fs mtime 2026-05-29 15:43)。

### 3.3 方案 / 芯片选型 — 有记录(决议号+状态)，选型过程本身不在 sprint3
- 【有记录】决议状态表：DEC-S1-001 技术路线=线阵 DAS+子带 LOCKED；DEC-S1-002 指向仅 ≥1kHz；DEC-S1-004 DSP=ADSP-21569「LOCKED（不可逆，依据待 L1 回填）」；DEC-S2-002 dyadic 树形半带 FIR；DEC-S2-007/008/009 N=16/Dolph-20/4 子带；DEC-S3-PROC-01 量产芯片采购冻结(21565 vs 21569 待 EZKIT)；「Gate 1 阵列方案 PASSED / Gate 2 ADSP-21569 CLOSED」——audit/NEXT_SESSION_BOOTSTRAP.md:84-102。
- 【有记录】选型依据的等级问题：PF-1「算力裕量 27×/49× 纸面当已验证 [L3]→DEC-S1-004 芯片 LOCKED+采购」——pf8/PF_atlas.md:18。
- 【有记录】自研 BOM(无采购/PO 动作)：DSP ADSP-21569KBCZ10「已 LOCKED（DEC-S1-004/Gate2）；竞品同款」(hardware/selfdev_bom.md:67)；DAC ADAU1962A 8ch(CTO 任务书指定，hardware/selfdev_bom.md:80)而非 ADAU1966A 16ch(critic/critic_review_s3.md:137-144)；功放 ACM3128A(首选)vs TAS5825M(备选)(hardware/selfdev_bom.md:86-106)；25MHz vs 24.576MHz 时钟待核(hardware/selfdev_bom.md:112-114)。
- 【有记录】算法方案选型：437 抽头全速率核(裕量 1.0×，不可行)被 63 抽头 dyadic 树形半带取代；现行 LOCKED=63 抽头半带原型——dsp/pf4/critic_review_pf4.md:27-33；8 驱 16 对称约束→仅 broadside、不可电子偏转(DEC-S3-DSP-03)——dsp/dsp_8ch_report.md:134-179、audit/matlab_verify_m3_superdir_8pair.md:93-101；DSP 6 个 DEC-S3-DSP-0x 在 audit/NEXT_SESSION_BOOTSTRAP.md:95-97。
- 【有记录】Sprint 2 的候选/推荐：N=24/d=30 推荐(pf8/p0b_asset_inventory.md:56)、「★N=16/d=30 锁定方案」(pf8/p1b_prd_alignment.md:36)，均已作废。
- 【未见】DEC-S1-004/Gate 1/Gate 2 的决议日期、候选芯片对比、选 21569 的理由(是否与竞品同款有关)、DEC-S3-PROC-01 的日期：sprint3 内无。

### 3.4 开发板 / EZKIT 采购与到货 — 只有零散侧面记录
- 【有记录】下单：2026-05-29 文本写 T1「EZKIT 到货 | … | 海外周期（已下单）」——pf8/L1_test_window_tasklist.md:15。下单日期/供应商/型号/订单号：【未见】。
- 【有记录】尚未到货的证据：2026-05-29「EZKIT 未到、无 PCB」(pf8/critic_ctier_eval.md:18)、「无 L1 实测（EZKIT 未到货）」(dsp/pf4/sub1_q15_stopband.md:4,142)；2026-05-30 启动指南仍以「触发 D：EZKIT 到货」待命(audit/NEXT_SESSION_BOOTSTRAP.md:52-57)。
- 【有记录】转接板 PO：6 项文档级闭环、Q-① 满足签署条件，「待 CTO 拍板」(audit/NEXT_SESSION_BOOTSTRAP.md:57,175)；两份硬件设计文档自称不含采购/PO 动作(hardware/selfdev_bom.md:8、hardware/transition_board_design.md:8)；PO 实际是否发出：【未见】。
- 【有记录】实物板在手(2026-06-02 文本)：AD-EXKIT V2.1(双 A2B)+ADSP-21569-SOM REV 1.1+ADSP-21569KBCZ10，CTO 肉眼确认丝印——audit/ezkit_fira_baseline.md:40-42、audit/BENCH_OPS_CARD.md:5；仿真器 AD-HP530ICE(CCES 识别为 ICE-1000)——audit/ezkit_bringup_checklist.md:92、audit/ezkit_fira_baseline.md:46；厂商资料三版 V1.0/V1.2/V2.1 差异表、安全闸门(版本确认前严禁接 ICE/上电；禁热插拔 JTAG)——audit/ezkit_bringup_checklist.md:10-30,54-64。到货日期：【未见】。
- 【有记录】到货后的执行文件：台架 Phase0–4(md5 核对→cross-build→上电→core-only R1 闭合→ADI FIRA baseline)与 R1 闭合判据——audit/BENCH_OPS_CARD.md:11-44；FIRA baseline 协议(cycle 全占位)——audit/ezkit_fira_baseline.md:139-167。
- 旁证(sprint3 外)：`knowledge_base/ezkit/INDEX.md:4`「建立日期：2026-06-01」，vendor_docs/bsp「待 CTO 拷入」(L15-16)；fs 上 `ezkit/` 目录建于 2026-06-01 17:46。

### 3.5 GitHub / 论文调研、框架选择、资料入库
- GitHub/开源框架调研：【未见】。
- 论文/文献调研：【未见】(sprint3 md 无 arXiv/论文引用；FIB 预研 audit/A2_fib_feasibility.md 全文无参考文献；仅 audit/critic_c8_first_run.md:39 提到 `knowledge_base/` 下有 `papers/` 目录名；旁证：该目录在磁盘上是空目录，建于 2026-05-26 15:02)。
- 专利：【有少量记录】差异化专利「DEFERRED」(audit/SPRINT3_DESKTOP_CLOSURE.md:57)；专利边界提醒及 Sprint 2 过度告警被 CTO 纠正(critic/critic_review_s3.md:68,75)；`sprint2/patent/formulas.md` 在盘点表(pf8/p0b_asset_inventory.md:41)。
- 【有记录】工具链/框架：numpy+scipy 主算；MATLAB R2026a+Signal Processing+Phased Array(audit/matlab_verify_m0_plan.md:13-24)；CTO 自有 MATLAB 脚本目录 `~/matlab-agent/`(p01/p02/sim_d55，audit/matlab_verify_m0_plan.md:30、audit/NEXT_SESSION_BOOTSTRAP.md:164)；pyroomacoustics 仅作未做项的候选工具(pf8/blindspot_triage.md:22)；CCES 2.11.1(清单 audit/ezkit_bringup_checklist.md:221)/2.12.1(audit/fira_fit_assessment.md:24,29)；ADI EE-408 FIRA 手册/例程(audit/fira_fit_assessment.md:18-27)。
- 【有记录】资料入库链：KB-HW-001(2026-05-29 归档，audit/critic_c8_first_run.md:26)；KB-HW-002(2026-05-30，audit/hardware_followup_queries.md:8,15)；KB-SPL-001(竞品 SPL，2026-05-30 归属确认，audit/NEXT_SESSION_BOOTSTRAP.md:105)；KB-DRV-TEST-001(测试阶段驱动图，2026-06-01，audit/drv_test_metadata_query.md:5)；JY/T 标准图 `knowledge_base/standards/JYT_directional_speaker.jpeg`(audit/NEXT_SESSION_BOOTSTRAP.md:171)。
- 【有记录】入库纪律事件：docx 入手后未及时入库(LESSON-013)→铁律六/C8——audit/POLICY_v15_draft.md:9-18,46-55；C8 首战——audit/critic_c8_first_run.md:53-60；「CTO 外部接收声明义务」——audit/doc_v15_review.md:46-53、audit/NEXT_SESSION_BOOTSTRAP.md:121。
- 【有记录】外部 AI 研讨(无内容记录)：CTO 与外部 AI 的讨论曾误引竞品 BW——pf8/PF9_C7_drafts.md:7、pf8/critic_ctier_eval.md:19,30。具体哪家 AI/日期/对话：【未见】。

### 3.6 团队 / 治理搭建 — 有记录(角色、制度、流程)，搭建日期未见
- 【有记录】角色(文内署名)：PM(Project Manager Agent)、acoustic-simulation、dsp-algorithm、hardware-design、testing、project-document、critic(critic-itc-001/critic-agent)——例：acoustic/sweep_d55_report.md:5、dsp/dsp_8ch_report.md:3、hardware/selfdev_bom.md:6、audit/ezkit_fira_baseline.md:3、audit/doc_v15_review.md:3、audit/critic_matlab_rv.md:3；CTO=「总工」，拍板点见 pf8/PF8_retrospective.md:50、dsp/pf4/WO_node1_saturation_fix.md:10、audit/sprint4_inputs.md:4。
- 【有记录】制度谱系 POLICY-PROV-001：生效 2026-05-28(pf8/PF8_retrospective.md:62)→v1.2 L0/铁律四/C6(2026-05-29，pf8/PF8_retrospective.md:51,89-92)→v1.3 PF-9/铁律五/C7(2026-05-29，pf8/critic_land_review.md:11-25)→v1.4 双轨/三轨核+v1.5 铁律六/C8(草案 2026-05-30 audit/POLICY_v15_draft.md；批准 audit/critic_bootstrap_rv.md:30)。sprint3 之后(CLAUDE.md)为九铁律/C1–C10，见疑点 D14。
- 【有记录】运行机制：ESCALATE/E-NEW-x/E-MATLAB-x 编号(pf8/critic_ai_citation_audit.md:59-62、audit/matlab_verify_m0_plan.md:24)；三轨独立工具核(含 CTO 第四轨 T1–T10，audit/SPRINT3_DESKTOP_CLOSURE.md:62)；PM 直跑接力(teammate socket 中断)——dsp/pf4/WO_node1_saturation_fix.md:63、pf8/p0b_asset_inventory.md:73、pf8/critic_final_s1.md:4、audit/critic_c8_first_run.md:66、audit/NEXT_SESSION_BOOTSTRAP.md:165；「待命期元任务」——pf8/PF_atlas.md:4；持久记忆治理(记忆随撤销同步)——pf8/PF8_retrospective.md:131-143；LESSON-006~013——audit/NEXT_SESSION_BOOTSTRAP.md:114。
- 【有记录】制度的实战检验叙事(案例 A/B/C)——pf8/PF8_retrospective.md:147-168。
- 【未见】团队创建日期、模型/档位分配(sprint3 文本仅有 audit/critic_x5_x1_review.md:4 的「reviewer: critic-agent」，无模型标记)、CLAUDE.md/SKILL.md 的起草记录。本仓库根目录名含「Kimi_Agent_多Agent协作方案」(audit/NEXT_SESSION_BOOTSTRAP.md:7 的路径亦含此名)，但 sprint3 文本没有说明该架构来源。

### 3.7 (附)给算法手册的 sprint3 材料速查(只列文中已标的状态)
- 冻结核 `dsp/tree_filterbank.c/.h`：现行 LOCKED=63 抽头半带原型的 3 级 dyadic 差分金字塔(dsp/pf4/critic_review_pf4.md:27-33)；头注释子带边界错，见 dsp/tree_filterbank.h.ERRATUM.md:3-15 与疑点 D8。
- 定点化(PF-4，host [L2]，未上板)：Q15 半带真阻带 71.3dB；纯 Q31 算术 172.8–175.5dB、端到端 74.6–78.7dB(Q15 系数底)；节点①回量化 1.73× 溢出已加饱和，SNR 177.6dB 且 SAT/UNSAT bit-exact——dsp/pf4/PF4_INTEGRATION_SUMMARY.md:25-27、dsp/pf4/WO_node1_saturation_fix.md:65-72。
- 阵因子指标 [L2 三轨]：BW@1k/2k/4k=29.27°/14.5°/7.24°、SLL −20dB、WNG 11.868dB、DI_2D；公差 MC 8 对称对@1k P(BW>30°)≈5.8%；MVDR ε=0.1–0.3→BW 24–25°；8 路串联与 16 元独立在 broadside+Dolph 下等价——audit/matlab_independent_verification.md:20-27；栅瓣临界 3118Hz(半波长)/6236Hz(严格)，规格降级 6k/5k——acoustic/pf8/p0a1_grating_criterion.md:78-88。
- 标准 JY/T 表9：仿真推算、非合规认证；180° 现模型不可评——audit/standard_compliance_check.md:13-16,46-49。
- FIRA 适配：⚠️部分适配、非必需；ADI 标称 0.25cycle/sample/tap 为 [L-adi] 非本板实测——audit/fira_fit_assessment.md:146,208。sprint3 内没有任何 FIRA/EZKIT 板上数字(audit/ezkit_fira_baseline.md:139)。

## 4. 阶段边界线索

| 日期 | path:line | 线索 |
|------|-----------|------|
| ≤2026-05-26 | pf8/p0b_asset_inventory.md:47；pf8/critic_final_s2.md:49 | Sprint 2/Gate 1 终点：Gate 1 文件日期 2026-05-26，当时锁 d=30/0.45m |
| 2026-05-26/27 | pf8/p1b_prd_alignment.md:75,79；acoustic/sweep_d55_report.md:6,8；dsp/dsp_8ch_report.md:10 | Sprint 3 起点附近：采购倒推表基准日 2026-05-26(T−6)；本目录最早的文内日期是 2026-05-27(Sprint3-AC-WP01-v1、DSP-WP01 v1.0 等)，此时拆机真值已入文。Sprint 3 的正式起始日：【未见】 |
| 2026-05-28 | pf8/PF8_retrospective.md:62；dsp/dsp_8ch_report.md:14 | 治理纪元：POLICY-PROV-001 生效；树形 C 实算(P0-2)纠正算力 |
| 2026-05-29 | pf8/PF8_retrospective.md:49-51 | 几何统一(DEC-S3-GEOM-01)+制度补丁 v1.2/v1.3 同日完成 |
| 2026-05-29 | audit/SPRINT3_DESKTOP_CLOSURE.md:4,5,11,55-58 | 「Sprint 3 桌面阶段彻底收尾」；转入「等外部数据」(T1 EZKIT/T2 T-S/T3 消声室/T4 COMSOL，pf8/L1_test_window_tasklist.md:11-18) |
| 2026-05-30 | audit/NEXT_SESSION_BOOTSTRAP.md:6,21 | 「桌面阶段 ~96% 完成」；制度升 v1.5(七铁律+C1–C8) |
| 2026-06-01 | audit/drv_test_metadata_query.md:4-5；knowledge_base/ezkit/INDEX.md:4(旁证) | 外部数据开始到位：测试阶段驱动曲线、EZKIT 资料库 |
| 2026-06-02 | audit/sprint4_inputs.md:4-6；audit/BENCH_OPS_CARD.md:3-7,53；audit/ezkit_fira_baseline.md:17 | Sprint 3→Sprint 4/上板线切换：S4 输入清单建立；台架操作卡；`DOC-S4-*` 编号出现；R1/R14 门禁与「FIRA 收益不进选型」红线。注意这几个文件物理上在 sprint3/audit/，内容属 Sprint 4 |
| 2026-06-02 | git `4bf0f52`(14:03) | git 根提交(此前历史无 git 记录) |
| 2026-06-09 | git `43aad40` | sprint3/sprint2/治理文档与 M1/M2 代码批量入库 |
| 2026-09-26 | dsp/tree_filterbank.h.ERRATUM.md:3-15；git `33b1966` | S7 阶段对 sprint3 冻结件做撤回旁注(DEC-S7-RETRACT-SUBBAND-01) |

## 5. 疑点

(逐条给出文本冲突/缺失，并说明手册引用时的建议；不做裁决。)

**D1 入库日期≠撰写日期，文内日期无 git 佐证。** 62/64 md 首次提交为 `43aad40`(2026-06-09)，git 根提交 2026-06-02(§0)。2026-05-26～06-02 间的所有文内日期只能互相印证。(旁证，fs 观察、可被改写：`knowledge_base/competitor/full_teardown_v2.md` mtime 2026-05-29 15:43，与 E-NEW-3 清扫同日；`SPL_anechoic_measurement_archived.md` mtime 2026-05-30 16:04，与 audit/NEXT_SESSION_BOOTSTRAP.md:105 的归属确认同日。)

**D2 6 个文件日期缺失或只在文末。** 全无日期：audit/ezkit_bringup_checklist.md、dsp/cces_skeleton/cces_skeleton_description.md、pf8/critic_ai_citation_audit.md；仅文末有日期：audit/critic_bootstrap_rv.md:67、pf8/PF9_C7_drafts.md:78、dsp/pf4/sub2_fixed_vs_float.md:199。其中 bring-up 清单可由被引关系定为 ≤2026-06-02(audit/BENCH_OPS_CARD.md:24)，cces 骨架可由 critic/critic_review_s3.md(2026-05-27)评审它推定 ≤05-27。

**D3 `定向音柱AI数据.docx` 的时间链自相矛盾。** 磁盘 mtime 2026-05-27 19:56(audit/critic_x5_x1_review.md:59)；硬件团队 05-28 发 CTO、CTO「2026-05-30 才转交 PM…超 24h」(audit/POLICY_v15_draft.md:11)；C8 基线表写「05-28 | 硬件 | … | 声明入库日 05-30 | 超 24h(48h)」(audit/critic_c8_first_run.md:17)；但 KB-HW-001 的 date 是 2026-05-29(audit/critic_c8_first_run.md:26)，且 05-29 的 audit/critic_x5_x1_review.md:59 已称「今日 2026-05-29 才提取归档」并审了该归档；同文 L60 又把「项目正式收到时间」记为 [pending]。「入手后滞留 48h」这一缘起事实(LESSON-013)的口径并不一致。

**D4 JY/T 标准的获得/入库时序。** 05-29 的 audit/standard_compliance_check.md 已按表9 12 点计算；CTO 接收声明写标准 05-30 入库(audit/critic_c8_first_run.md:19)；同文 L39 称 knowledge_base 当时只有 competitor/hardware_input/measurements/papers 四目录、无 standards；而同为 05-30 的 audit/NEXT_SESSION_BOOTSTRAP.md:171 与 audit/critic_bootstrap_rv.md:49 已把 `knowledge_base/standards/JYT_directional_speaker.jpeg` 列为实存(12/12)。(旁证 fs：该 jpeg mtime 2026-05-29 17:57，standards 目录 mtime 05-30 15:41。)先后顺序文本未交代。

**D5 EZKIT 无采购/到货直接记录，板型口径不一。** 仅一处「海外周期（已下单）」(pf8/L1_test_window_tasklist.md:15)。06-02 的实物是 AD-EXKIT V2.1+SOM REV 1.1(audit/ezkit_fira_baseline.md:40-42)，厂商资料是中文「ADSP-21569EVB 开发板」系列(audit/ezkit_bringup_checklist.md:44-46)，而 sprint3 他处称「EV-21569-EZKIT」(hardware/transition_board_design.md:23；audit/ezkit_fira_baseline.md:177 把二者划等号)——它是否就是当初海外下单的那块，文本没说。SOM 版本：厂商资料 REV 1.0(audit/ezkit_bringup_checklist.md:63)，实物 REV 1.1。bring-up 清单「待 CTO 确认 REV 后回填专属接线」栏始终空白(L272-279)，而 audit/BENCH_OPS_CARD.md:24 写「专属接线以 V2.1 回填位为准」。CCES 版本 2.11.1(清单 L221,254)与 2.12.1(audit/fira_fit_assessment.md:24,29)并存。

**D6 pf8/L1_test_window_tasklist.md 自相矛盾。** L25「转接板 PO 是 T1 真正启动前的闸门」，L26「EZKIT 本体即可启动，不依赖转接板」，L35「关键路径：转接板 PO 解锁→EZKIT 上电→R1」。06-02 的台架文件(audit/BENCH_OPS_CARD.md 全文)也完全没提转接板；转接板 PO 在 05-30 仍「待 CTO 拍板」(audit/NEXT_SESSION_BOOTSTRAP.md:175)。

**D7 算力裕量数字多版本，且被后续 L1 推翻(git，非 sprint3 文本)。** 纸面：26×→49×(30.56 vs 58.11 MMAC/s，dsp/dsp_8ch_report.md:13,79)，A2 另引树形 56.4MMAC/s(audit/A2_fib_feasibility.md:102,109)——16ch 纸面值 58.11 与 56.4 并存。05-28 实算 45.7/88.7、33×/17×[L2](dsp/dsp_8ch_report.md:14)，被 bootstrap/FIRA 评估沿用(audit/NEXT_SESSION_BOOTSTRAP.md:14,126；audit/fira_fit_assessment.md:170,224)，并据此写「电气/算法链路可进 PCB」(audit/SPRINT3_DESKTOP_CLOSURE.md:11,36)。git 提交 `7563b3f`(2026-06-03)的说明写「R1 状态: L1 翻盘 (cyc_8ch=1006935, 8ch裕量1.32x/16ch超1.46x, 桌面[L2]33x高估~25x)」。手册不应把 17×/33× 当作板上结论。

**D8 子带边界撤回的波及面大于被加标的文件。** ERRATUM 称真实分界 3k/6k/12k、detail 带为未对齐梳状残差、「不能在本树上按子带施加不同的加权、校准或延时」(dsp/tree_filterbank.h.ERRATUM.md:7-15)；提交 `33b1966` 说明「15 个文件逐处加标」，sprint3 内只有 PF9 panorama、sub1/sub2 md 与 2 个 py 被加标。未加标但依赖「4 子带 500–1k/1k–2k/2k–4k/4k–8k」或「按子带独立加权」的文件：dsp/dsp_8ch_report.md:40-45、audit/NEXT_SESSION_BOOTSTRAP.md:14、audit/A1_static_weight_tuning.md:81、audit/A2_fib_feasibility.md:34-42、audit/A3_decision_recommendation.md:12,21、audit/critic_a123_rv.md:93-109(把「子带标量加深零成本」经独立复算判为「证真」)。其中「SB2 单独 Dolph-25 关 R10」与 ERRATUM:15 在文本层面直接冲突。引用 A1–A3 的结论时需先对照 ERRATUM 与 `sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md`(sprint3 外)。

**D9 cces_skeleton_description.md 残留撤回值与占位权重。** L262「Sprint2 已验证：SLL=-20dB，BW@2kHz=26.8° ≤ 30° ✓」是 d=30 撤回值(audit/NEXT_SESSION_BOOTSTRAP.md:107 列为作废)，此处无警示；critic/critic_review_s3.md:153,197(F-DSP06)曾要求清 d=30 文案，终审 pf8/critic_final_s2.md:39 只核了 dsp_8ch_report.md。L281-285 的 Dolph 前 8 个权重(0.3491/0.5127/0.6696/0.8/0.9/0.97/1.0/1.0)自标「[估算]…最终值需…精确计算后固化」。摘录者临时核(非记录内容；numpy 复刻 scipy `chebwin` 算法，验证它能复现文档所报 BW@1k/2k/4k=29.27°/14.52°/7.24°、SLL −20.00dB)：chebwin(16,20) 归一化为 [0.8668, 0.5043, 0.6217, 0.7334, 0.8327, 0.9135, 0.9705, 1.0, …镜像]；把骨架权重代入得 BW@1k=32.28°、SLL −18.96dB。结论：该骨架权重不是 Dolph-20，勿引用。

**D10 DAC 型号未随 F-X01 在 DSP 文档中更新。** BOM/转接板 v2 已改 ADAU1962A(hardware/selfdev_bom.md:11,80)，但 dsp/dsp_8ch_report.md:112,125,277 与 dsp/cces_skeleton/cces_skeleton_description.md:118 仍写 ADAU1966A；延迟预算 12.53ms 中 DAC 0.75ms 项的器件出处因此与 v2 BOM 不一致。

**D11 Gate 1「PASSED」的依据已被撤销。** 盘点表称 Gate 1 当时锁 d=30/0.45m(pf8/p0b_asset_inventory.md:47)，acoustic/sweep_d55_report.md:125 仍以「Gate1 指标 BW@2kHz≤30°」判定，audit/NEXT_SESSION_BOOTSTRAP.md:102 仍列「Gate 1 阵列方案 PASSED」，没说明是否在 d=55 基线上重新确认。

**D12 DEC-S1-004(ADSP-21569，不可逆)的依据与日期。** 文本只有「LOCKED（不可逆，依据待 L1 回填）」(audit/NEXT_SESSION_BOOTSTRAP.md:86)、PF-1「纸面 27×/49×[L3]→芯片 LOCKED+采购」(pf8/PF_atlas.md:18)、BOM「竞品同款」(hardware/selfdev_bom.md:67)；选型日期、候选、理由、DEC-S3-PROC-01 日期均不在 sprint3。

**D13 SPL 数字多口径，不可混引。** 117.1dB[L4 占位](acoustic/sweep_d55_report.md:56-58,139)；单只灵敏度 88dB[L4 datasheet](audit/critic_x5_x1_review.md:33)；测试阶段驱动曲线 SPLo 82.16dB/通带~90dB，并称旧 117 占位「整体推翻」(audit/drv_test_metadata_query.md:30-34)；竞品 0° 106–111dB[L1，消声室，启用算法](acoustic/sweep_d55_report.md:54-58、audit/drv_test_metadata_query.md:19)。M1 测距/M2 电压未回填(audit/drv_test_metadata_query.md:15-16,46)；「15Ω=直流 Re、3W 口径」另见 audit/hardware_followup_queries.md:9-14。

**D14 铁律/C 门编号随版本变化。** sprint3 文本里铁律三=措辞红线「实测仅 L1」(pf8/PF8_retrospective.md:10；audit/POLICY_v15_draft.md:90)，v1.5 草案共六条(audit/POLICY_v15_draft.md:87-93)，批准后为七条+C1–C8(audit/NEXT_SESSION_BOOTSTRAP.md:21,118)。本仓库当前 CLAUDE.md(「九铁律（一句话）」节)为九铁律+C1–C10，且其第 3 条=不可逆决策须 L1(或 L2+签字)，与上述「铁律三」不是同一条。手册引「铁律 N」必须带版本。

**D15 C7 评审计数口径不一。** pf8/PF8_retrospective.md:163「第五次…首次抓到 BLOCKER」；audit/critic_a123_rv.md:21「连续五次主动评审零 BLOCKER 的纪录在此中断（前四次零，本次…）」(自相矛盾)；audit/critic_std_a_rv.md:3「第四次、连续四次零」；audit/SPRINT3_DESKTOP_CLOSURE.md:11,51「6 次(5 次零+1 次抓)」。

**D16 DEC-S3-003/WO-S3-001 全文不在 sprint3，且 DEC-S3-003 有两种用法，d=55 的 L1 出处也有两种叙事。** DEC-S3-003 既被当作「拆机」(pf8/PF8_retrospective.md:46；pf8/critic_final_s1.md:37)，又被当作「竞品硬件+自研算法」合法性边界(critic/critic_review_s3.md:51,57,201；pf8/critic_ctier_eval.md:18)。d=55 的出处一说「游标卡尺拆机实测」(pf8/PF8_retrospective.md:46)，一说硬件团队文档的「6/6 文档级闭环、非测量级签署完成」(audit/critic_x5_x1_review.md:40)；谁测、哪天测，文本不清。

**D17 竞品 SPL 的来源与归属。** 数据在 `full_teardown_v2.md §7`，同时另有一份「竞品 SPL PDF」(KB-SPL-001)，需 CTO 确认归属(audit/NEXT_SESSION_BOOTSTRAP.md:105,193)，说明曾有归属不明；测量方/日期/设备/是否 CTO 自测：未见。

**D18 外部 AI 对话只留下后果。** pf8/PF9_C7_drafts.md:7、pf8/critic_ctier_eval.md:19,30 记录了外部 AI 误引，但哪家 AI、何时、对话内容均无记录。

**D19 git 里跟踪了已编译 ELF 与大数据。** `sprint3/dsp/tree_verify`、`tree_verify_sat/unsat`、`tva_sat/unsat`、`pf4/fixed_vs_float` 为 x86-64 ELF；`tree_io_sat.csv`/`tree_io_unsat.csv` 各 2.25MB。手册引用时以 `.c` 源与 md 记录为准，勿以二进制为据。

**D20 sprint3 里没有的权威文件(需到别处核)。** `sprint2/docs/decisions_log.md`、`simulation_coverage_audit.md`(v2.3)、`PROJECT_HANDOVER.md`、`prd_update.md`(v2.3–2.5)、`POLICY-PROV-001_数字来源分级制度.md`、`sprint3_kickoff_checklist.md`、`sprint3_procurement_kickoff.md`、仓库根 `sprint3_status.md`、`knowledge_base/competitor/full_teardown_v2.md`、`knowledge_base/hardware_input/*`。sprint3 内对它们的引用均为二手转述，其中许多行号引用(如 decisions_log L546/L553)随文件演进可能已失效。

**D21 『三道关』的先后。** audit/SPRINT3_DESKTOP_CLOSURE.md:22 在 05-29 已把 PRD v2.4 记为「Gate PASS（C1/C2/C7）」，但专职 critic 复核到 05-30 才补(audit/critic_c8_first_run.md:66：「上轮 critic socket 断、PM 直跑门禁，现补专职复核」)；类似地 PF-8 终审段 1 也是「此前因环境中断由 PM 代验」(pf8/critic_final_s1.md:4)。引用『已过 critic 门』时要区分 PM 直跑门禁与专职 critic 复核两个时间点。

