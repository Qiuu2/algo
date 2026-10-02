# digest_G — sprint7（critic / dsp / sim / tools）记录摘要

> ⚠ 公开版说明（2026-10-02）：本摘录按写时原文照录，里面会出现已撤回或已被推翻的数字（如 d=30、17×/33×、1.5k/3k/6k 子带标签、86–144 MCPS、6.4×）。采信任何数字前，以 `sprint2/docs/decisions_log.md` 和 `sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md` 为准。

> 生成日期 2026-10-02。只读：未改仓库、未起子代理。服务对象：CTO 撰写《算法开发手册》。可信度序：decisions log > runbook/执行单 > git commit > memory。
> **范围**：`git ls-files sprint7 | grep '\.md$' | grep -v -e '^sprint7/docs/' -e '^sprint7/signals/'` = **26 份 md，全部整份读完**；另有 **161 个非 md 文件**（仅列名/类型，不读内容；唯一例外：`sprint7/tools/s7_intake.py:26` 的 VERSION 行、`sprint7/tools/s7_driver_pairing.py` 前 12 行 docstring，只用来说明类型）。
> **引用约定**：`ID:行号` = §0.1 表里该 ID 对应文件的行号；`git <hash>` = 提交；**（转引）** = 事实原件不在本范围（decisions_log、prd_update、`sprint7/docs/*`、KB 等），我只看到 critic/README 的引述，**未核原件**。
> **措辞约定**：判定一律照抄原文；标"（自数）"的计数是我按原文条目行数数出来的，不是原文声明；"未见"= 在 26 份 md 内做关键词检索 0 命中（检索式见 §3 各条）。

---

## 0. 读了什么

### 0.1 md 文件（26 份，全部读完）

| # | ID（引用简写） | path | bytes | 行数 | 读法 | 首次入库（hash 日期） | 之后又被改动的提交 |
|---|---|---|---:|---:|---|---|---|
| 1 | `CRITIC_A` | `sprint7/critic/CRITIC_A_HOUSEKEEPING_20260902.md` | 26,577 | 171 | 全文（Read 工具整份读完，171 行） | b6bc5fe 2026-09-02 | — |
| 2 | `CRITIC_B` | `sprint7/critic/CRITIC_B_PROPOSAL_20260902.md` | 31,630 | 191 | 全文（Read 工具整份读完，191 行） | 5adfe91 2026-09-02 | — |
| 3 | `CRITIC_C` | `sprint7/critic/CRITIC_C_RULINGS_20260902.md` | 25,253 | 174 | 全文（Read 工具整份读完，174 行） | c9c3f91 2026-09-02 | — |
| 4 | `CRITIC_D` | `sprint7/critic/CRITIC_D_D3PKG_POLQA_20260903.md` | 34,409 | 191 | 全文（Read 工具整份读完，191 行） | d524fde 2026-09-03 | — |
| 5 | `CRITIC_E` | `sprint7/critic/CRITIC_E_B63_20260903.md` | 29,331 | 203 | 全文（Read 工具整份读完，203 行） | e773399 2026-09-03 | — |
| 6 | `CRITIC_F` | `sprint7/critic/CRITIC_F_INTAKE_20260903.md` | 32,453 | 204 | 全文（Read 工具整份读完，204 行） | 7d6704d 2026-09-03 | 4e0b2ce 2026-09-03 |
| 7 | `CRITIC_G` | `sprint7/critic/CRITIC_G_SIDE30_R1_20260926.md` | 9,140 | 64 | 全文（Read 工具整份读完，64 行） | 33b1966 2026-09-26 | — |
| 8 | `CRITIC_H` | `sprint7/critic/CRITIC_H_SIDE30_R2_20260926.md` | 6,835 | 64 | 全文（Read 工具整份读完，64 行） | 33b1966 2026-09-26 | — |
| 9 | `CRITIC_I` | `sprint7/critic/CRITIC_I_SIDE30_R3A_20260926.md` | 6,902 | 64 | 全文（Read 工具整份读完，64 行） | 33b1966 2026-09-26 | — |
| 10 | `CRITIC_J` | `sprint7/critic/CRITIC_J_SIDE30_R3B_20260926.md` | 3,778 | 49 | 全文（Read 工具整份读完，49 行） | 04fd908 2026-09-26 | — |
| 11 | `CRITIC_K` | `sprint7/critic/CRITIC_K_SIDE30_R3C_20260926.md` | 4,029 | 51 | 全文（Read 工具整份读完，51 行） | db301ef 2026-09-26 | 0ef46c4 2026-09-27 |
| 12 | `CRITIC_L` | `sprint7/critic/CRITIC_L_SIDE30_R3D_20260927.md` | 3,659 | 57 | 全文（Read 工具整份读完，57 行） | 0ef46c4 2026-09-27 | — |
| 13 | `CRITIC_M` | `sprint7/critic/CRITIC_M_SIDE30_R3E_20260928.md` | 15,334 | 128 | 全文（Read 工具整份读完，128 行） | 04e0e6a 2026-09-28 | — |
| 14 | `CRITIC_N` | `sprint7/critic/CRITIC_N_SIDE30_R3F_20260928.md` | 19,489 | 143 | 全文（Read 工具整份读完，143 行） | 46574ed 2026-09-28 | — |
| 15 | `CRITIC_O` | `sprint7/critic/CRITIC_O_SIDE30_R3G_20260929.md` | 18,352 | 150 | 全文（Read 工具整份读完，150 行） | cd113e2 2026-09-29 | — |
| 16 | `CRITIC_P` | `sprint7/critic/CRITIC_P_S7FF_SIGNALS_20261002.md` | 12,998 | 102 | 全文（Read 工具整份读完，102 行） | 3a008e8 2026-10-02 | — |
| 17 | `README_s7ff_r1` | `sprint7/critic/s7ff_r1_scripts/README.md` | 1,256 | 15 | 全文（Read 工具整份读完，15 行） | 3a008e8 2026-10-02 | — |
| 18 | `README_r1` | `sprint7/critic/side30_r1_scripts/README.md` | 690 | 8 | 全文（Read 工具整份读完，8 行） | 33b1966 2026-09-26 | — |
| 19 | `README_r2` | `sprint7/critic/side30_r2_scripts/README.md` | 180 | 3 | 全文（Read 工具整份读完，3 行） | 33b1966 2026-09-26 | — |
| 20 | `README_r3b` | `sprint7/critic/side30_r3b_scripts/README.md` | 512 | 5 | 全文（Read 工具整份读完，5 行） | 04fd908 2026-09-26 | — |
| 21 | `README_r3e` | `sprint7/critic/side30_r3e_scripts/README.md` | 760 | 6 | 全文（Read 工具整份读完，6 行） | 46574ed 2026-09-28 | — |
| 22 | `README_r3f` | `sprint7/critic/side30_r3f_scripts/README.md` | 921 | 7 | 全文（Read 工具整份读完，7 行） | 46574ed 2026-09-28 | 58fa094 2026-09-28 |
| 23 | `README_r3g` | `sprint7/critic/side30_r3g_scripts/README.md` | 972 | 12 | 全文（Read 工具整份读完，12 行） | cd113e2 2026-09-29 | — |
| 24 | `FIRBENCH` | `sprint7/dsp/firbench/README.md` | 20,493 | 128 | 全文（Read 工具整份读完，128 行） | 0ef46c4 2026-09-27 | ce87ed1 2026-09-29 |
| 25 | `PROBE` | `sprint7/dsp/probe/README.md` | 20,856 | 188 | 全文（Read 工具整份读完，188 行） | e773399 2026-09-03 | 7d6704d 2026-09-03; 4e0b2ce 2026-09-03 |
| 26 | `ACOUSTIC` | `sprint7/sim/acoustic/S7_ACOUSTIC_SIM_REPORT.md` | 35,892 | 375 | 全文（Read 工具整份读完，375 行） | 5adfe91 2026-09-02 | 7d6704d 2026-09-03; 33b1966 2026-09-26 |

说明：首次入库 = `git log --diff-filter=A --format='%h %ad' --date=short -- <file> | tail -1`；表中 bytes = `wc -c`，行数 = `wc -l`（与 Read 工具显示的行数一致）。"之后又被改动的提交"来自 `git log -- <file>`。

### 0.2 非 md 文件（161 个，1,705,683 B；只列名/类型，**未读内容**）

| 目录 | 个数 | bytes 合计 | 类型分布 | 首次入库（hash 日期 ×个数） | 文件名（相对该目录） |
|---|---:|---:|---|---|---|
| `sprint7/critic/s7ff_r1_scripts` | 8 | 21,425 | .log×5, .py×3 | 3a008e8 2026-10-02 ×8 | click_detector_probe.log, click_detector_probe.py, critic_falsifiers.log, critic_falsifiers.py, gate_run_stdout.log, indep_recompute.log, indep_recompute.py, leq_compare.log |
| `sprint7/critic/side30_r1_scripts` | 12 | 29,495 | .c×2, .py×10 | 33b1966 2026-09-26 ×12 | check1_ideal.py, check2_faults_mc.py, check3_broadband_nf.py, check4_realtree.py, check5_realtree_more.py, check6_nf_compet.py, check7_realtree_bb.py, check8_mc_uniform.py, check9_analytic_tree.py, crit_model.py, tfb_paths.c, tfb_probe.c |
| `sprint7/critic/side30_r2_scripts` | 4 | 9,824 | .py×3, .txt×1 | 33b1966 2026-09-26 ×4 | mc2.py, mc2_out.txt, mc3.py, r2_ideal.py |
| `sprint7/critic/side30_r3b_scripts` | 2 | 7,443 | .py×2 | 04fd908 2026-09-26 ×2 | delta.py, indep.py |
| `sprint7/critic/side30_r3e_scripts` | 12 | 28,594 | .out×3, .py×9 | 46574ed 2026-09-28 ×12 | check_edit.py, delta/altwin_check.py, delta/eta_window.py, dense_checks.py, gen_check_on.py, grid_overfit.py, mc_own.py, mc_own_full.out, mc_pm_newseeds.out, mc_pm_newseeds.py, rs_own.out, rs_own.py |
| `sprint7/critic/side30_r3f_scripts` | 24 | 62,222 | .out×12, .py×12 | 46574ed 2026-09-28 ×22; 58fa094 2026-09-28 ×2 | q10_freelow.out, q10_freelow.py, q11_l1_abs.out, q11_l1_abs.py, q1_lr_bank_real.out, q1_lr_bank_real.py, q2_kkt_drive.out, q2_kkt_drive.py, q2b_l1_sanity.out, q2b_l1_sanity.py, q3_mc_paired.out, q3_mc_paired.py, q4_ddc_keele.out, q4_ddc_keele.py, q5_fir_overshoot.out, q5_fir_overshoot.py, q6_outofband.out, q6_outofband.py, q7_drive_premise.out, q7_drive_premise.py, q8_headroom_delta.out, q8_headroom_delta.py, q9_mutation.out, q9_mutation.py |
| `sprint7/critic/side30_r3g_scripts` | 7 | 37,025 | .log×2, .py×5 | cd113e2 2026-09-29 ×7 | r3g_bank_headroom.log, r3g_bank_headroom.py, r3g_kkt_mc.log, r3g_kkt_mc.py, r3g_mc_path.py, r3g_taper_eff.py, run_mut.py |
| `sprint7/dsp/firbench` | 10 | 97,883 | .c×3, .diff×1, .h×3, .py×1, .sh×2 | 0ef46c4 2026-09-27 ×10 | bench_main_firbench.diff, fb_coeffs.h, fb_goldens.h, host/fb_fira_emu_host.c, host/fb_ref_host.c, run_firbench_guard_check.sh, run_firbench_host.sh, s7_firbench.c, s7_firbench.h, tools/gen_firbench_tables.py |
| `sprint7/dsp/host` | 3 | 21,319 | .c×1, .sh×2 | d524fde 2026-09-03 ×3 | run_s7_host_checks.sh, run_s7_preproc_equiv.sh, s7_selftest_host.c |
| `sprint7/dsp/probe` | 8 | 124,797 | .c×2, .diff×1, .h×2, .py×1, .sh×2 | e773399 2026-09-03 ×8 | bench_main_s7.diff, fira_tree_probe.c, guard_stub_inc/drivers/fir/adi_fir.h, run_s7_probe_guard_check.sh, run_s7_probe_host.sh, s7_wallclock_probe.c, s7_wallclock_probe.h, tools/make_fira_tree_probe.py |
| `sprint7/dsp/wtbl` | 6 | 29,700 | .c×1, .log×2, .py×1, .sh×2 | 7686c05 2026-09-26 ×3; 04e0e6a 2026-09-28 ×3 | gen_m2_wtbl.log, gen_m2_wtbl.py, run_wtbl_checks.sh, run_wtbl_falsifiers.sh, wtbl_falsifiers.log, wtbl_sums_host.c |
| `sprint7/sim/acoustic` | 20 | 161,966 | .csv×11, .log×3, .m×1, .py×5 | 5adfe91 2026-09-02 ×20 | s7_common.py, s7_constbw_chosen_weights.csv, s7_constbw_fixedwindow_flatness.csv, s7_constbw_subband_design.csv, s7_constbw_wng_tradecurve.csv, s7_dualtrack_compare.csv, s7_dualtrack_compare.py, s7_focus_chmap_equiv.csv, s7_focus_chmap_equiv.log, s7_focus_chmap_equiv.py, s7_lowfreq_boundary.csv, s7_lowfreq_eps_scan.csv, s7_lowfreq_superdir.csv, s7_lowfreq_superdir.log, s7_lowfreq_superdir.py, s7_matlab_crosscheck.csv, s7_matlab_crosscheck.m, s7_windows_sweep.csv, s7_windows_sweep.log, s7_windows_sweep.py |
| `sprint7/sim/dsp` | 1 | 10,234 | .py×1 | 5adfe91 2026-09-02 ×1 | s7_dsp_compute_ledger.py |
| `sprint7/sim/side30/fir` | 11 | 225,458 | .csv×9, .log×1, .py×1 | 04fd908 2026-09-26 ×11 | s7_fir_bands.csv, s7_fir_coeffs_127tap.csv, s7_fir_compute.csv, s7_fir_headroom.csv, s7_fir_jyt.csv, s7_fir_mc.csv, s7_fir_nearfield.csv, s7_fir_robust_design.log, s7_fir_robust_design.py, s7_fir_summary.csv, s7_fir_verify.csv |
| `sprint7/sim/side30` | 31 | 703,583 | .csv×9, .log×11, .m×3, .py×8 | 33b1966 2026-09-26 ×10; 46574ed 2026-09-28 ×7; 04e0e6a 2026-09-28 ×6; cd113e2 2026-09-29 ×8 | s7_alt_algos.log, s7_alt_algos.py, s7_alt_algos_ideal.csv, s7_alt_algos_mc.csv, s7_alt_algos_params.csv, s7_alt_algos_xcheck.log, s7_alt_algos_xcheck.m, s7_alt_tables.log, s7_alt_tables.py, s7_alt_tables_ideal.csv, s7_alt_tables_mc.csv, s7_alt_tables_xcheck.log, s7_alt_tables_xcheck.m, s7_hybrid_lpxo.log, s7_hybrid_lpxo.py, s7_hybrid_lpxo_headroom.csv, s7_hybrid_lpxo_ideal.csv, s7_hybrid_lpxo_mc.csv, s7_hybrid_lpxo_params.csv, s7_hybrid_lpxo_xcheck.log, s7_hybrid_lpxo_xcheck.m, s7_nearfield_side.log, s7_nearfield_side.py, s7_side30_r1_feasibility.log, s7_side30_r1_feasibility.py, s7_single_table.log, s7_single_table.py, s7_sorting_mc.log, s7_sorting_mc.py, s7_tree_subband_response.log, s7_tree_subband_response.py |
| `sprint7/tools` | 2 | 134,715 | .py×2 | 7d6704d 2026-09-03 ×1; db301ef 2026-09-26 ×1 | s7_driver_pairing.py, s7_intake.py |
| **合计** | **161** | **1,705,683** | | | |

### 0.3 取数命令（可复现）
- `git ls-files sprint7 | grep '\.md$' | grep -v -e '^sprint7/docs/' -e '^sprint7/signals/'`（26）；同式取反得非 md（161）。
- `git log --diff-filter=A --format='%h %ad' --date=short -- <file> | tail -1`；`git log --format='%h %ad %s' --date=short -- sprint7/critic sprint7/dsp sprint7/sim sprint7/tools`；`git show --stat <hash>`（只用来看某提交含哪些文件，及 §2 提交时间）；`git rev-list --max-parents=0 HEAD`、`git rev-list --count HEAD`、`git log --format=%ad --date=format:%Y-%m | sort | uniq -c`（仓库根提交与月度分布）；`git ls-files knowledge_base`（8 个）。
- 关键词检索：对 26 份 md 做 `grep -n -E`（PRD / 竞品拆机 / 芯片板采购 / GitHub·论文 / 框架 / DEC 编号等），结果见 §3。

### 0.4 范围外、只看到名字的东西（未读）
`sprint7/docs/*`（S7_ALGO_UPGRADE_PROPOSAL / S7_DSP_ASSESSMENT / S7_VERIFICATION_PLAN / S7_B63_WALLCLOCK_GAP / S7_BOARD_RESULTS_INTAKE / S7_SIDE30_* / S7_LIT_REGISTER_SIDE30 / 各 runbook 等）、`sprint7/signals/s7ff_v1/*`、`sprint2/docs/decisions_log.md`、`sprint2/docs/prd_update.md`、`knowledge_base/*`、`deliverables/algorithm_validation/*`。以上均为其他摘要员的范围，下文凡涉及均标（转引）。

---

## 1. 文件清单

### 1.1 md 文件（26 份）

格式：`首次入库日期 | path | 类型 | 一句话内容 | 判定/状态(原文)`。critic 文件的"轮次名"= 文件名里的 A…P / R1…R3g。

| 首次入库日期 | path | 类型 | 一句话内容 | 判定/状态（原文） |
|---|---|---|---|---|
| 2026-09-02（b6bc5fe） | `sprint7/critic/CRITIC_A_HOUSEKEEPING_20260902.md` | critic 裁定 · **A 批「入库整理」**；首行 `reviewer: critic @ claude-fable-5-1 / 2026-09-02`(CRITIC_A:1) | 审 Sprint 7「A 入库整理」批次（`git diff --cached`，12 文件，未提交；CRITIC_A:3）：CTO 口述的自家 rig 正/侧读数按 L0 登记（OBS_OWNRIG）、竞品固件包只登记元数据不解包（KB-EXT）、EXP_COMPET 入库、旧松散副本 guard 改指权威、decisions_log 4 条 + team_config 留痕（对照表 CRITIC_A:11-18）。5 条 MAJOR = 幻影引用 F-1 / 18 dB 归属错 F-2 / 固件接触程度自述不实 F-3 / C8 接收基线缺失 F-4 / EXP_COMPET 4 数无出处 F-5（CRITIC_A:24-28） | 初审 `CONDITIONAL-PASS（0 BLOCKER / 5 MAJOR / 8 MINOR / 5 INFO）`(CRITIC_A:5) → delta `PASS（带 MINOR）`，余 3 MINOR + 3 INFO(CRITIC_A:117, :153-162)。**链：CONDITIONAL-PASS → PASS** |
| 2026-09-02（5adfe91） | `sprint7/critic/CRITIC_B_PROPOSAL_20260902.md` | critic 裁定 · **B 批「算法层升级提案」** | 审 B 批全包：4 份文档（提案 / dsp 评估 / 验证计划 / 声学报告）+ dsp 算力台账脚本 + acoustic 脚本与数据（CRITIC_B:3）。独立复算：帧预算 1,333,333 / 1.5× 线 888,889 / 余量 57,986(=43.5 MCPS)/1.605×（CRITIC_B:19）；对 DEC「6.4 倍」提出同口径应为 1.794×（CRITIC_B:23）；推荐组合逻辑链核（CRITIC_B:62-74） | 初审 `FAIL（BLOCKER ×1 / MAJOR ×2 / MINOR ×9 / INFO ×5）`(CRITIC_B:5)：BLOCKER F-1 = 1.5 dB 重复性仍标 [L1]（CRITIC_B:40）；MAJOR F-2 命名跨文档不一致(:41)、F-3 T2 争用侧 15 与固定侧 60 混口径(:42) → delta `PASS（带 INFO ×2）`(CRITIC_B:141)。**链：FAIL → PASS** |
| 2026-09-02（c9c3f91） | `sprint7/critic/CRITIC_C_RULINGS_20260902.md` | critic 裁定 · **C 批「CTO 裁定落库」** | 审 CTO 2026-09-02 裁定落库：DEC-S7-RULINGS-01（14 条）/ DEC-S7-IMPL-01 / D12 加注 / KB D9 / SKILL:58 D13 / D11 rm（CRITIC_C:3）；含「CTO 原话逐条对照」表（CRITIC_C:42-61） | 初审 `CONDITIONAL（… 0 BLOCKER / 5 MAJOR / 6 MINOR / 5 INFO）`(CRITIC_C:12-13) → delta `PASS`：5 MAJOR 全部闭合/作废（F-3/F-4 因 CTO 原话补交而作废，CRITIC_C:124），剩 1 MINOR + 5 INFO(CRITIC_C:128)。**链：CONDITIONAL → PASS** |
| 2026-09-03（d524fde） | `sprint7/critic/CRITIC_D_D3PKG_POLQA_20260903.md` | critic 裁定 · **D 批（两包）** | 包 1 = D3 固件改动包（5 个 `#error`、6 指纹、`M2_SELFTEST` 八锚、`M2_SELFTEST_NEGCTRL`、`M2_SEG_CYC` 四段括号、`g_m2_beam_cyc_min`；CRITIC_D:14）+ S-B 测试员单；包 2 = 极性 QA runbook（零代码，S7_POLARITY_QA_RUNBOOK.md）。critic 亲跑 guard/host/preproc 三套检查（CRITIC_D:33-35） | 包 1 初审 `CONDITIONAL（0/1/2/6 INFO）`(CRITIC_D:12) → delta `PASS（0/0/0/7 INFO）`(CRITIC_D:180)；包 2 `PASS_WITH_MINOR（0/0/2 MINOR/3 INFO）`(CRITIC_D:80) → delta 仍 `PASS_WITH_MINOR`，残留 1 MINOR(CRITIC_D:191)。**链：包1 CONDITIONAL→PASS；包2 PASS_WITH_MINOR→PASS_WITH_MINOR** |
| 2026-09-03（e773399） | `sprint7/critic/CRITIC_E_B63_20260903.md` | critic 裁定 · **E 批「B6.3 墙钟差距包」** | 审 DEC-S7-IMPL-01 第(1)项 B6.3 交付包：`S7_B63_WALLCLOCK_GAP.md` + `sprint7/dsp/probe/`（CRITIC_E:3）。MAJOR = CCNT 读次数账目自相矛盾(F-1, :97)、FG 只罩 analyze 不罩 synthesize 却写成"证明真链"(F-2, :98) | 初审 `CONDITIONAL — 0 BLOCKER / 2 MAJOR / 8 MINOR / 6 INFO`(CRITIC_E:13) → delta `PASS（剩 3 MINOR 非阻塞 + 2 INFO；0 BLOCKER / 0 MAJOR）`(CRITIC_E:154)。**链：CONDITIONAL → PASS** |
| 2026-09-03（7d6704d；4e0b2ce 追加 delta-3/4/5） | `sprint7/critic/CRITIC_F_INTAKE_20260903.md` | critic 裁定 · **F 批（落库版，去数值）** | 包 1 = DEC-S7-RULINGS-02 落库；包 2 = 板测结果判读方案 `S7_BOARD_RESULTS_INTAKE.md` + `s7_intake.py`；delta-3/4/5 = DEC-S7-RULINGS-03 + B1 条件 0 改"实测 CGU 寄存器重算 CCLK" + 脚本 v3→v3.2(CRITIC_F:5, :141)。完整裁定仅存会话 scratchpad，未入库(CRITIC_F:137) | 包 1 `CONDITIONAL(0/2/4/3)→PASS(0/0/0/1)→PASS`(CRITIC_F:14)；包 2 `FAIL(1 BLOCKER/7 MAJOR/5 MINOR/3 INFO)→CONDITIONAL(0/1/2/3)→PASS_WITH_MINOR(0/0/2/2)`(CRITIC_F:15)；delta-3 `FAIL(1/0/3/4)`→delta-4 `CONDITIONAL(0/1/1/3)`→delta-5 `PASS_WITH_MINOR(0/0/2/2)`(CRITIC_F:151-153) |
| 2026-09-26（33b1966） | `sprint7/critic/CRITIC_G_SIDE30_R1_20260926.md` | critic 报告 · **R1**（PM 转录"原文照录"，英文；reviewer 行在 :10 `claude-opus-5-5`） | 审 PM 会话内「侧面抑制 20→30 dB」C1–C8 结论 + `side30_feasibility.py`（后落库为 `sprint7/sim/side30/s7_side30_r1_feasibility.py`；CRITIC_G:3）。F1 = 分析假设的子带分界与冻结代码矛盾：真实为 3k/6k/12k（头注 1.5k/3k/6k 错）、detail 带为未对齐梳状残差（CRITIC_G:16-19）；处置 → DEC-S7-RETRACT-SUBBAND-01（CRITIC_G:5） | `Verdict: FAIL. One BLOCKER (F1).`(CRITIC_G:12)；条目自数 1 BLOCKER / 6 MAJOR(F2–F7) / 5 MINOR(F8–F12)；原文未给计数。**无 delta（由 R2 接续）** |
| 2026-09-26（33b1966） | `sprint7/critic/CRITIC_H_SIDE30_R2_20260926.md` | critic 报告 · **R2**（PM 转录，英文） | 审 PM 按 R1 修正后的 R1–R5 主张：单表路线、配对/微调 MC、文献综合、计划顺序（CRITIC_H:4）。MAJOR：重开 CTO D6 并破 1 kHz≤30°（:14）、良率只是单频点非整机良率（:24-30）、计划顺序（:33-36）、C5 脚本/论文只在 scratchpad（:38） | `Verdict: CONDITIONAL. I found no BLOCKER.` … `Four MAJORs`(CRITIC_H:10)；条目自数 0/4/4 MINOR/1 INFO |
| 2026-09-26（33b1966） | `sprint7/critic/CRITIC_I_SIDE30_R3A_20260926.md` | critic 报告 · **R3a**（PM 转录"原文要点照录"，含 PM 修正记录） | 审侧抑 30 dB 实施批三包：包 1 撤回子带边界 / 包 2 分析·DEC·PRD / 包 3 固件 `M2_WTBL_SEL`（CRITIC_I:1, :4）。BLOCKER = C7（`S7_DSP_ASSESSMENT.md:263` 未加标，:11）与 C2（把 [L2 host] 写成"实测"，:12） | 初审：包 1 `FAIL（2 BLOCKER）`、包 2 `CONDITIONAL（2 MAJOR）`、包 3 `PASS_WITH_MINOR`、总体 `FAIL`(CRITIC_I:4) → delta：包 1 PASS、包 2 PASS、包 3 PASS_WITH_MINOR、总体 `PASS_WITH_MINOR`(CRITIC_I:56) |
| 2026-09-26（04fd908） | `sprint7/critic/CRITIC_J_SIDE30_R3B_20260926.md` | critic 报告 · **R3b**（PM 转录，四轮） | 审每通道滤波器 FIR 原型包：`S7_SIDE30_PERCH_FIR_DESIGN.md` + `sim/side30/fir/*`，作者 dsp teammate（CRITIC_J:3-5） | 四轮：`FAIL（1 BLOCKER / 3 MAJOR / 5 MINOR）`(CRITIC_J:8) → `CONDITIONAL`(:31) → `CONDITIONAL`(:39) → `PASS_WITH_MINOR`(:45)。**链：FAIL → CONDITIONAL → CONDITIONAL → PASS_WITH_MINOR** |
| 2026-09-26（db301ef；0ef46c4 增 PM 补注） | `sprint7/critic/CRITIC_K_SIDE30_R3C_20260926.md` | critic 报告 · **R3c**（PM 转录，两轮） | 审测试执行单包：`S7_DRIVER_MATCHING_RUNBOOK.md`、`S7_SIDE30_FARFIELD_TEST.md`、`s7_driver_pairing.py`，作者 testing teammate（CRITIC_K:3-6）。:19 为 2026-09-27 PM 在审计记录里**原地补注**（来源 CRITIC_L:56） | R1 `CONDITIONAL（0 BLOCKER / 7 MAJOR / 6 MINOR / 1 INFO）`(CRITIC_K:7) → delta `PASS_WITH_MINOR（0/0/3 MINOR/1 INFO）`(CRITIC_K:37) |
| 2026-09-27（0ef46c4） | `sprint7/critic/CRITIC_L_SIDE30_R3D_20260927.md` | critic 报告 · **R3d**（PM 转录，三轮） | A 部分 = FIR 算力 bench 包（`sprint7/dsp/firbench/*` + `S7_FIRBENCH_RUNBOOK.md`，dsp teammate）；B 部分 = 测试员总览页 `S7_TESTER_INDEX_SIDE30.md`（PM）（CRITIC_L:3-6） | R1：A `CONDITIONAL（0/2/4/1）`(CRITIC_L:11)、B `0 BLOCKER / 1 MAJOR / 4 MINOR`(:28) → R2：A PASS、B CONDITIONAL(:44) → R3(mini-delta)：A PASS、B `PASS_WITH_MINOR`(:53)；仍需 CTO_OK 才能把 S-FIRB 交测试员(:57) |
| 2026-09-28（04e0e6a） | `sprint7/critic/CRITIC_M_SIDE30_R3E_20260928.md` | critic 报告 · **R3e**（PM 转录） | 审稳健扇区表 RS-A(sel 4)/RS-B(sel 5) 加入 `M2_WTBL_SEL`（CRITIC_M:1）。MAJOR F1 = 一键门 `run_wtbl_checks.sh` 第 1 步**假绿**（无 pipefail，自 7686c05 起存在，R3a 漏审；:11-16）；F2 = RS-B 授权标注写大（CTO 只同意一张表；:17） | `CONDITIONAL，0 BLOCKER / 2 MAJOR / 7 MINOR / 7 INFO`(CRITIC_M:4) → delta `PASS_WITH_MINOR`(CRITIC_M:93)，新增 D1/D2 两条 MINOR(:97) |
| 2026-09-28（46574ed） | `sprint7/critic/CRITIC_N_SIDE30_R3F_20260928.md` | critic 报告 · **R3f**（PM 转录，含补充报告） | 审低阶 IIR 分频加权（X3/LR4）/ DDC 原样 / Keele 延时 CBT 桌面评估（CRITIC_N:1）。F1 = 漏了公共全通相位与瞬态余量（:11）；delta BLOCKER D1 = 把「94.0 dB 灵敏度接近程度」误写成 SPL 余量（:87）；D2 MAJOR = 把 X3 需要的联动限幅器说成"例外清单里已有的逐通道保护限幅器"（:92） | R1 `CONDITIONAL，0 BLOCKER / 1 MAJOR / 7 MINOR / 6 INFO`(CRITIC_N:4) → delta `FAIL，1 BLOCKER / 1 MAJOR / 3 MINOR / 4 INFO`(:78) → mini-delta `PASS`(:121)。**链：CONDITIONAL → FAIL → PASS** |
| 2026-09-29（cd113e2） | `sprint7/critic/CRITIC_O_SIDE30_R3G_20260929.md` | critic 报告 · **R3g**（PM 转录） | 审 hybrid「共享线性相位分频 + 每通道频段增益」桌面评估（CRITIC_O:1）。MAJOR F1 = "不再需要联动限幅器"说宽（:15）；F2 = 拆树后算力推断跨口径且说得太肯定（:21） | `CONDITIONAL，0 BLOCKER / 2 MAJOR / 7 MINOR / 8 INFO`(CRITIC_O:4) → delta `PASS_WITH_MINOR`(CRITIC_O:103)，新增 2 MINOR |
| 2026-10-02（3a008e8） | `sprint7/critic/CRITIC_P_S7FF_SIGNALS_20261002.md` | critic 报告 · **s7ff R1**（PM 转录） | 审远场逐带信号文件包 `s7ff_v1`（61 个 WAV，已进 git）（CRITIC_P:1, :4）。MAJOR M1 = 渐入渐出门放过咔哒/断续/接缝跳变（:27）；M2 = 电平 −20 dB 与板子输入余量 `0x49A00000`≈−4.8 dBFS 未对账（:28） | `CONDITIONAL，0 BLOCKER / 2 MAJOR / 7 MINOR / 1 INFO`(CRITIC_P:4) → delta `PASS_WITH_MINOR`（余 6 条文字 MINOR；CRITIC_P:70, :86-98） |
| 2026-10-02（3a008e8） | `sprint7/critic/s7ff_r1_scripts/README.md` | 脚本存档说明 | s7ff R1 的 critic 复核脚本/日志存档；**跑的是修正前（0 dB 档 RMS −20 dB）那一版**，电平类数字只代表 R1 当时状态（README_s7ff_r1:4-6） | 无判定；脚本含绝对路径，原样保留(README_s7ff_r1:7) |
| 2026-09-26（33b1966） | `sprint7/critic/side30_r1_scripts/README.md` | 脚本存档说明 | CRITIC_G 的复核脚本存档；未落库：可执行文件与 25 MB `paths.bin`（README_r1:5）；**不能原样复跑**（硬编码绝对路径，README_r1:8） | 无判定 |
| 2026-09-26（33b1966） | `sprint7/critic/side30_r2_scripts/README.md` | 脚本存档说明 | CRITIC_H 的复核脚本存档；不 import s7_common；每格 MC M=300–400（README_r2:3） | 无判定 |
| 2026-09-26（04fd908） | `sprint7/critic/side30_r3b_scripts/README.md` | 脚本存档说明 | CRITIC_J 的 `indep.py`/`delta.py`；delta 复算 7 频段联合良率（U-flat 装好直接用，3000 阵，seed 4242）= D35 5.4% / V1-128 20.7% / V2-128 18.4%；**正式数字以 `sim/side30/fir/s7_fir_mc.csv` 为准**（README_r3b:3-5） | 无判定 |
| 2026-09-28（46574ed） | `sprint7/critic/side30_r3e_scripts/README.md` | 脚本存档说明 | R3e 复核脚本存档；正文与 r3f README 近乎同文（同时提到 R3e/R3f；README_r3e:5）；刻意未存档：论文页面截图/全文抽取（Keele 2002 为 AES 版权，仓库公开；README_r3e:6） | 无判定 |
| 2026-09-28（46574ed；58fa094 补 q11） | `sprint7/critic/side30_r3f_scripts/README.md` | 脚本存档说明 | R3f 复核脚本存档（q1–q11 + q2b，24 个文件；mini-delta 后补存 `q11_l1_abs.py/.out` 支撑"保证不削顶约 10.5 dB(c6)/FIR 约 5.0 dB(c0)"；README_r3f:7） | 无判定 |
| 2026-09-29（cd113e2） | `sprint7/critic/side30_r3g_scripts/README.md` | 脚本存档说明 | R3g 复核脚本存档：分频组/瞬态余量、KKT+配对 MC(6000 阵)、MC 路径核对、锥度项、对 PM 脚本的变异测试 `run_mut.py`（README_r3g:5-9） | 无判定 |
| 2026-09-27（0ef46c4；ce87ed1 加状态更新） | `sprint7/dsp/firbench/README.md` | 目录 README（dsp teammate，2026-09-27；FIRBENCH:3） | 每通道 FIR **算力台架**包（DEC-S7-SIDE30-01 ③ 的 go/no-go 测量）：5 条路径 T8/T1/P1/CORE_C/CORE_SYM × 63/127/255 抽头 × 8 路（FIRBENCH:29-37）、golden 24/24 双轨（:71-77）、桌面检查 PASS（:79-94）。**本机无 cc21k/无板，一个板上数字都不填**(FIRBENCH:4) | :5 原写"R3d CONDITIONAL…待 delta、未 commit、未获 CTO_OK"；**:6（2026-09-29 更新，上行原文保留）**：delta 与 mini-delta 均判 PASS、已入库 `0ef46c4`、**CTO_OK 已给**（CTO 原话「恩，我同意sfirb可以」） |
| 2026-09-03（e773399；7d6704d、4e0b2ce 小改） | `sprint7/dsp/probe/README.md` | 目录 README（dsp teammate，2026-09-02；PROBE:3） | B6.3 **bench 侧墙钟三段拆分探针**（WO-S7-B6.3）：w/ana/syn + beam 括号、`fira_tree_probe.c` 诊断副本登记（PROBE:124-139）、桌面 guard 8/8 与 host H1–H4 PASS（:141-169）、板上读数回填模板全部留空（:95-122）。诚实声明：无 cc21k/无板（PROBE:5-6） | CTO 2026-09-03 裁定：`S7_PROBE_INNER`（副本内拆分）与 `S7_PROBE_SYN_FG` 均"不必做、保持默认关"（PROBE:88-89, :171, :177；DEC-S7-RULINGS-02/03） |
| 2026-09-02（5adfe91；7d6704d、33b1966 改动） | `sprint7/sim/acoustic/S7_ACOUSTIC_SIM_REPORT.md` | 仿真报告（acoustic-simulation teammate `agent-acoustic-sim-v1`，2026-09-02；ACOUSTIC:4） | B 批声学数字供给：B5 窗比较(§2)、B5-2 子带恒定波束宽(§3)、B5-3 换窗(§4)、B4 低频超指向边界(§5)、B2 聚焦 v2 声学收益(§6)、双轨 MATLAB(§7)。**全部 [L2/numpy]，无任何 L1 实测**(ACOUSTIC:5) | **2026-09-26 部分撤回**（DEC-S7-RETRACT-SUBBAND-01）：§3 全部、§4.2、§1 能回答第 2 条、§0.1 子带划分行的 [L1 代码] 标作废；§2/§4.1/§5 逐频率数字/§6 保留（ACOUSTIC:3, :23, :133, :207） |

### 1.2 非 md 文件（按目录归并；名称清单见 §0.2；**内容未读**，"一句话"依据 = 文件名 + 同目录 README/critic 报告的描述，出处已标）

| 首次入库日期 | 目录 | 类型 | 一句话内容 | 状态 |
|---|---|---|---|---|
| 2026-09-02 | `sprint7/sim/acoustic`（20） | py / csv / log / m | B 批声学仿真：窗扫描 `s7_windows_sweep`、子带设计 `s7_constbw_*`（已作废）、低频超指向 `s7_lowfreq_*`、聚焦 chmap 等价 `s7_focus_chmap_equiv`、MATLAB 第二轨 `s7_matlab_crosscheck.m/.csv` + `s7_dualtrack_compare`、共用库 `s7_common.py`（ACOUSTIC:365-373） | `s7_constbw_*` 数据作废(ACOUSTIC:133)；其余 [L2] |
| 2026-09-02 | `sprint7/sim/dsp`（1） | py | `s7_dsp_compute_ledger.py` 算力台账（critic 以副本跑：帧预算/1.5×线/余量，CRITIC_B:11-12,:19；F-14 改 `round()`，CRITIC_B:53,:160） | B 批 delta PASS |
| 2026-09-03 | `sprint7/dsp/host`（3） | sh / c | D3 固件包的桌面检查：`s7_selftest_host.c` + `run_s7_host_checks.sh` + `run_s7_preproc_equiv.sh`（CRITIC_D:33-35：host 8/8 + 负控制、preproc 等价均 PASS） | D 批 PASS |
| 2026-09-03 | `sprint7/dsp/probe`（8） | c / h / py / sh / diff | B6.3 探针本体、诊断副本、桌面 stub 头、守卫/宿主脚本、bench 补丁文本（PROBE:8-19） | E 批 delta PASS；板上数字待回填 |
| 2026-09-03 | `sprint7/tools/s7_intake.py` | py | 板测结果判读脚本（自动初筛，非裁定；`VERSION = "v3.3 2026-09-03"` 见 s7_intake.py:26；CRITIC_F:15） | F 批 `PASS_WITH_MINOR`；v3.3 的退出码修补见 CRITIC_F:204 |
| 2026-09-26 | `sprint7/critic/side30_r1_scripts`、`side30_r2_scripts`、`side30_r3b_scripts`（18） | py / c / txt | critic G、H、J 的复核脚本存档（说明见各 README） | 不能原样复跑（绝对路径；README_r1:8, README_r3b:5） |
| 2026-09-26 | `sprint7/sim/side30` 一次性脚本组（10） | py / log | 侧抑 20→30 dB 第一批分析：`s7_side30_r1_feasibility.*` = CRITIC_G 所审 R1 版(CRITIC_G:3)；`s7_sorting_mc.*`、`s7_single_table.*` 按名**疑为** CRITIC_H:38 所说"只在 scratchpad 的 sorting_mc.py / single_table_check.py"（名称不同，未核对）；`s7_nearfield_side.*`、`s7_tree_subband_response.*` 仅按名 | 内容未读 |
| 2026-09-26 | `sprint7/sim/side30/fir`（11） | csv / py / log | 每通道 FIR 桌面原型：`s7_fir_robust_design.py/.log` + 9 个 `s7_fir_*.csv`（bands/coeffs_127tap/compute/headroom/jyt/mc/nearfield/summary/verify） | 正式数字以 `s7_fir_mc.csv` 为准(README_r3b:5)；J 批 PASS_WITH_MINOR |
| 2026-09-26 / 09-28 | `sprint7/dsp/wtbl`（6） | py / sh / log / c | `M2_WTBL_SEL` 加权表生成器与一键门：`gen_m2_wtbl.py/.log`、`run_wtbl_checks.sh`（7686c05, 09-26）；`run_wtbl_falsifiers.sh`、`wtbl_falsifiers.log`、`wtbl_sums_host.c`（04e0e6a, 09-28，R3e 的 F1 假绿修复与 7 种伪造输入反证；CRITIC_M:68-70, :121-122） | M 批 PASS_WITH_MINOR |
| 2026-09-26 | `sprint7/tools/s7_driver_pairing.py` | py | 逐只喇叭复响应 → 散布/离群/疑似极性 → 贪心配对 → 修整 → ±90° 侧抑模型预测（docstring 前 12 行；CRITIC_K:3-6）；Python 3.10+ + numpy，不需 scipy | K 批 PASS_WITH_MINOR |
| 2026-09-27 | `sprint7/dsp/firbench`（10） | c / h / py / sh / diff | FIR 算力台架：`s7_firbench.c/.h`、`fb_coeffs.h`、`fb_goldens.h`、生成器、host 参考与 FIRA 行为模型、守卫/宿主脚本、bench 补丁（FIRBENCH:8-25） | L 批 A 部分 PASS；CTO_OK 2026-09-29(FIRBENCH:6) |
| 2026-09-28 | `sprint7/sim/side30` alt_tables（6） | py / csv / log / m | RS-A/RS-B 稳健扇区表生成 + MATLAB 交叉；含"探索记录"一节（CRITIC_M:52, :73-75） | M 批 PASS_WITH_MINOR |
| 2026-09-28 | `sprint7/sim/side30` alt_algos（7）+ `critic/side30_r3e_scripts`（12）+ `side30_r3f_scripts`（24） | py / csv / log / m / out | R3f：低阶 IIR(X3/LR4)、DDC、Keele 延时 CBT 桌面评估及 critic 复核（脚本新增 HEADROOM/DRIVE PREMISE、SCOPE、EXPLORATORY free-low 等节，CRITIC_N:59-69） | N 批 PASS |
| 2026-09-29 | `sprint7/sim/side30` hybrid_lpxo（8）+ `critic/side30_r3g_scripts`（7） | py / csv / log / m | R3g：hybrid「共享线性相位分频 + 每通道频段增益」（LPX3/LPX4）及 critic 复核（CRITIC_O:85, README_r3g:5-9） | O 批 PASS_WITH_MINOR |
| 2026-10-02 | `sprint7/critic/s7ff_r1_scripts`（8） | py / log | CRITIC_P 的独立复算/反证/探针/Leq 对比/一键门输出（README_s7ff_r1:9-15） | 修正前版（README_s7ff_r1:4） |

---

## 2. 时间线事件

> 提交时间取 `git log` 的 author date（与 commit date 相同）。"事件"内的数字是原文数字，我未复算。

| 日期 | path:行 / git | 事件 |
|---|---|---|
| 2026-06-02 | git 4bf0f52（范围外） | 本仓库根提交 `core-only S0-S1 host-verified`；全库 155 个提交，按月 6 月 120 / 7 月 13 / 9 月 20 / 10 月 2。**首次入库日期的下限因此是 2026-06-02**（见 §5-5） |
| 2026-06-16 | CRITIC_E:56 | 被引作放置证据的 M2 板上 PASS map 文件名含 `20260616`（`M1_Loopback_M2build_1B_PASS_20260616.map.xml`）；日期只来自文件名 |
| 2026-07-01 / 07-08 | CRITIC_A:25, :94（转引） | 竞品板 16 dB@2k [L1 07-01，竞品 rig 只换板]；自家 rig 18 dB@2k [L1 07-08，1 m 近场，C2/C4 翻正后] |
| 2026-07-22 | git c8eeb08（范围外） | Sprint 7 之前最后一个提交（治理瘦身 SLIM-07）；到 09-02 共 **42 天无提交** |
| 2026-07-31 | CRITIC_A:87, :27 | 竞品固件 zip 文件 mtime 2026-07-31 14:59:38（birth 15:22:35）；A 批按 mtime 代理接收时间，C8 逾期 **33 天为下界**，CTO 接收声明基线缺失 |
| 2026-09-02 18:56 | git b6bc5fe；CRITIC_A:3,:5,:24,:92,:117 | **首个含 `sprint7/` 路径的提交**（`sprint7/` 目录此前不存在：CRITIC_A:24 F-1 幻影引用、:92 `ls sprint7` 无）。A 批 `CONDITIONAL-PASS → PASS`；同批落 DEC-S7-SCOPE-01 / OBS-OWNRIG-01 / EXTINPUT-HIT9616-01（CRITIC_A:24,:27） |
| 2026-09-02（A 批内） | CRITIC_A:25-28 | 四个实质发现：18 dB 被误归到竞品名下(F-2)；PM 会话记忆里已有竞品固件头 XOR 混淆级内容，与"只做格式判断"自述不符，记忆被清洗(F-3, delta :125)；C8 基线缺失(F-4)；EXP_COMPET 4 个带标数字全库无出处(F-5) |
| 2026-09-02 19:25 | git 5adfe91；CRITIC_B:3,:5,:19,:23,:40,:141 | B 批「算法层升级提案」入库：`FAIL → PASS`。BLOCKER F-1=1.5 dB 重复性降标未传播（:40）。critic 独立复算：帧预算 1,333,333 / 线 888,889 / 余量 57,986(43.5 MCPS)/1.605×（:19）；DEC「6.4×」是跨口径，同口径 F7 463,273 vs M2 830,903 = **1.794×**（:23）；推荐顺序 B6.3→B6.4/6.5 基座→P0/P2/P1→B1；B2 下轮；B3/B7 不做；B4 挂起；B5 不换全频段窗（:66-74） |
| 2026-09-02 22:31 | git c9c3f91；CRITIC_C:12-13,:42-61,:124,:128 | CTO 裁定落库：D1 判 1.5× 用墙钟口径(:46)；D2 批准 B6.3 对照实验(:47)；D3 批准 M2 TU 改动包 CTO_OK=1(:48)；D4 t_base=1.0(:49)；D7 自家 16 元 + 竞品整机可对比(:50)；D9 固件来源=同事自 SPON、授权未确认(:51)；D10 4 数保持未落盘不升级(:52)；D11 删副本(:53)；D12 加注不改原文(:54)；B2 推下轮、B3/B7 不做、B4 挂起(:55-56)；B5 措辞歧义(:57)；实施第一步三项(:59)；两个提交允许 push(:60)。critic 自己的"PM 冒名 CTO"判定在 CTO 原话补交后**作废**(:124) |
| 2026-09-03 01:28 | git d524fde（+3567aae 同分钟）；CRITIC_D:12,:14,:33-35,:80,:180,:191 | D3 固件包 + S-B 单 + 极性 QA runbook 入库：包 1 `CONDITIONAL → PASS`，包 2 `PASS_WITH_MINOR`。critic 亲跑 guard(10 配置+5 反证)/host/preproc 三套全 PASS；MAJOR 仅在 runbook：`M2_SEG_CYC` 无指纹、B63 引用不存在的 `g_m2_seg_cyc_built`(:20) |
| 2026-09-03 01:43 | git e773399；CRITIC_E:13,:97-98,:154,:170-171 | B6.3 包入库：`CONDITIONAL → PASS`。MAJOR：CCNT 读次数账目三处矛盾(:97)；FG 只罩 analyze 不罩 synthesize(:98)。修后：探针改链式、每帧 25 读（板上 33），synthesize 无锚如实声明、可选 `S7_PROBE_SYN_FG` 旗(:170-171) |
| 2026-09-03 12:20 | git 7d6704d；CRITIC_F:14-15,:51,:137 | DEC-S7-RULINGS-02 + 板测判读方案 + `s7_intake.py v2.2` 入库；判读方案首轮 **FAIL（BLOCKER：作废读数仍出 PASS，§12 FG2）**（:51），v2/v2.1 修后 PASS_WITH_MINOR |
| 2026-09-03 14:20 | git 4e0b2ce；CRITIC_F:2,:141-153,:161,:180,:204 | DEC-S7-RULINGS-03 入库（SYN_FG 不做 / SEG_CYC 四段追认 / B1 条件 0 改"实测 CGU 寄存器重算 CCLK"）。delta-3 **FAIL**：CCLK 解码公式的 ÷2 属于 ADSP-21568 而非 21569(:180,:161)；经 delta-4/5 加数据手册三道合理性门 → PASS_WITH_MINOR；脚本终版 v3.3(:204) |
| **2026-09-03 → 09-26** | git（全库） | **23 天无提交**（全库 2026-08-25…10-02 窗口内只有 09-02/09-03/09-26/09-27/09-28/09-29/10-02 七个提交日） |
| 2026-09-26 17:55 | git 33b1966（+7686c05 17:55:29）；CRITIC_G:5,:10,:12,:16-19；CRITIC_H:6,:10；CRITIC_I:4,:56 | **侧面 30 dB 线开启**：撤回子带边界(DEC-S7-RETRACT-SUBBAND-01) + CTO 四项同意落库(DEC-S7-SIDE30-01) + 分析/文献/PRD v2.5 + 固件第一步 `M2_WTBL_SEL`。G=`FAIL`(F1 BLOCKER：真实子带分界 3k/6k/12k，非 1.5k/3k/6k)；H=`CONDITIONAL`；I=`FAIL → PASS_WITH_MINOR` |
| 2026-09-26 18:23 | git 04fd908；CRITIC_J:8,:31,:39,:45 | 每通道 FIR 原型入库：`FAIL → CONDITIONAL → CONDITIONAL → PASS_WITH_MINOR`（四轮） |
| 2026-09-26 18:27 / 18:28 | git db301ef / 42f38a0；CRITIC_K:7,:37 | 逐只测量 + 远场分频段 + 配对工具入库：`CONDITIONAL → PASS_WITH_MINOR`；42f38a0 把切表执行单钉住远场单版本 db301ef（落实 R3a F12） |
| 2026-09-27 19:44 | git 0ef46c4；CRITIC_L:9,:11,:44,:53；FIRBENCH:3-5；CRITIC_K:19 | FIRBENCH 台架包 + 测试员总览页入库；同提交给 CRITIC_K 原地补 PM 注（CRITIC_L:56 要求） |
| 2026-09-28 01:21 | git 04e0e6a；CRITIC_M:4,:11-16,:93 | RS-A/RS-B 表(sel 4/5) 入库；**修一键门假绿**（自 7686c05 起潜伏）；`CONDITIONAL → PASS_WITH_MINOR`；critic LESSON 写入 `agents/critic/memory.md`(CRITIC_M:69) |
| 2026-09-28 01:54 / 01:55 | git 46574ed / 58fa094；CRITIC_N:4,:78,:87,:92,:121 | IIR 分频/DDC/Keele 评估入库：`CONDITIONAL → FAIL(1 BLOCKER) → PASS`；"修正稿自带新错"（delta 的 BLOCKER/MAJOR 都出在修正稿新写的余量与限幅器措辞上，CRITIC_N:78）；58fa094 补存 q11 复核脚本 |
| 2026-09-29 00:48 | git ce87ed1；FIRBENCH:6；CRITIC_O:9 | **S-FIRB 获 CTO_OK**（CTO 原话「恩，我同意sfirb可以」，FIRBENCH:6）；R3g 评审期间 HEAD 由 58fa094 移到 ce87ed1(CRITIC_O:9) |
| 2026-09-29 01:25 | git cd113e2；CRITIC_O:4,:15,:21,:103 | hybrid LPX3-b 评估入库：`CONDITIONAL → PASS_WITH_MINOR`；MAJOR F1=联动限幅器说宽(含 FIR)、F2=跨口径算力推断；critic LESSON 再写入 memory(CRITIC_O:82) |
| 2026-10-02 01:54 | git 3a008e8；CRITIC_P:4,:53,:70,:98 | 远场逐带信号包 s7ff_v1（61 个 WAV 进 git，CTO 选定）：`CONDITIONAL → PASS_WITH_MINOR`；0 dB 档电平 −20→**−23 dB**(CRITIC_P:53)；"已生成入库、过门中；三道关走完之前不算 §2 的'已交付'"(CRITIC_P:98) |

### 2.1 DEC 编号索引（本范围内出现者；decisions_log 正文不在本范围，语境为转引）

| DEC 编号 | 本范围首次出现 | 语境 |
|---|---|---|
| DEC-S3-GEOM-01 | ACOUSTIC:16；CRITIC_D:115 | 几何 16 元 / d=55 mm / L=825 mm 标 [L1 拆机]；runbook 只把几何当 rig 描述、不锁几何 |
| DEC-S3-DSP-03 | ACOUSTIC:17 | 8 路 A/B 中心对称串联 {c,15−c}，权重必须中心对称，broadside-only [L1 硬件] |
| DEC-S3-003 | CRITIC_A:27 | 竞品固件"持有合法性确认（DEC-S3-003 边界）"列入 CTO 决策清单 |
| DEC-S4-CRITERION-01-FINAL | CRITIC_F:91 | T2_RATIO 1.5 [裁定]，口径=墙钟（DEC-S7-RULINGS-01 D1） |
| DEC-S5-EQ-O1-01 | CRITIC_B:41 | B1(EQ+限幅器)命名对齐；其"逐通道保护限幅器 T_k=T·w_k"在 CRITIC_N:92-95、CRITIC_O:15-20 被拿来区分联动限幅器 |
| DEC-S5-SPL-CALIBER-01 | CRITIC_N:87 | 94.0 dB@1W/1m [L2 模型，待消声室坐实] 每次使用必带标注；"多响"与灵敏度分开 |
| DEC-S5-BUDGET-L1-01 | CRITIC_O:54 | 整系统残余 1.46–2.14× [L4]，取代 1.38–2.56× |
| DEC-S5-V1-SCOPE-01 | ACOUSTIC:290 | v1 = 近场高频展区分区（2–5 m，≥4 kHz） |
| DEC-S6-M2-BOARD-PASS-01 | CRITIC_B:43（:22 提 F60-MAJOR-1） | 三口径（墙钟/争用 ledger/纯核）互不可比；其中"6.4 倍"被 CRITIC_B:23 指为跨口径 |
| DEC-S6-TEST3-METHOD-01 | CRITIC_A:31；CRITIC_G:47 | ±90° ≥12 dB 的现行测试判据；2L²/λ 远场距离 |
| DEC-S7-SCOPE-01 / OBS-OWNRIG-01 / EXTINPUT-HIT9616-01 | CRITIC_A:27 / :24 / CRITIC_C:31 | A 批三条：范围、L0 隔离登记、竞品固件外部输入登记 |
| DEC-S7-RULINGS-01 / IMPL-01 | CRITIC_C:3 | CTO 14 条裁定逐条处置 / 实施范围（第一步三项） |
| DEC-S7-RULINGS-02 / 03 | CRITIC_F:5 / :2 | 遗留裁定（含内拆分不必做）/ SYN_FG 不做、SEG_CYC 四段追认、B1 条件 0 改实测 CCLK |
| DEC-S7-RETRACT-SUBBAND-01 | CRITIC_G:5 | 撤回 1.5k/3k/6k 子带边界 |
| DEC-S7-SIDE30-01 | CRITIC_H:6 | CTO 四项同意（侧面 30 dB 线立项的裁定条目） |

### 2.2 承重数字/结论摘录（**原文数字，未复算**；L 级以原文为准；用于手册时请回原文核）

| 结论 | 级别（原文） | 出处 |
|---|---|---|
| M2 帧预算 1,333,333 cyc（1 GHz/750 帧每秒）；1.5× 线 888,889；M2 墙钟 max 830,903 → 余量 57,986 cyc = 43.5 MCPS，1.605× | 830,903 [L1 墙钟]（CRITIC_F:92；decisions_log:1013 转引自 CRITIC_B:115）；余者派生（CRITIC_F:90） | CRITIC_B:19 |
| 同口径比：M2 830,903 / F7(bench) 463,273 = 1.794×；"6.4 倍"是跨口径；H2 base 454,730 [L1 EZKIT] → 1.83× | 463,273/830,903 [L1]，比值 [L1-derived] | CRITIC_B:23, :66；CRITIC_C:38, :69 |
| 1.5× 判据采用**墙钟口径**（CTO D1） | CTO 裁定 | CRITIC_C:46 |
| 冻结树真实子带分界 3k/6k/12k（头注 `tree_filterbank.h:19-27` 的 1.5k/3k/6k 错）；detail 带为未对齐梳状残差；SB0 ≤2.5 kHz 为 0.00 dB、2.75k −0.37、3k −6.02、3.5k −71.2 | [L2 host 复算]（非实测） | CRITIC_G:17-19；CRITIC_I:36 |
| 真实树上 D2 宽带(630 Hz–5 kHz)侧抑 20.7 dB，而非原声称 35.4 | [L2 host] | CRITIC_G:28 |
| 全频段单一深表 D35：宽带 37.3 dB、0 cyc，但 BW@1k 37.4° 破 30° 线；D30 34.87° | [L2] | CRITIC_G:31；CRITIC_H:60 |
| "±1 dB/5°"是高斯 σ，项目约定是均匀半宽 | — | CRITIC_G:34 |
| 联合良率(1k∧2k∧4k)随误差模型 1%…26% 大幅波动，不是整机良率 | [L2 on L4 spread] | CRITIC_H:24-30 |
| FIR(V1-128) 7 频段、U-flat 装好直接用良率：D35 6.0% / V1-128 20.4% / V2-128 16.9%（仓库 CSV） | [L2]（误差分布本身是 L4 假设，宜标"[L2 on L4 spread]"：CRITIC_H:31） | CRITIC_J:41 |
| RS-B 与 D35 "持平，最薄处只高 0.03 dB"；7 频段 U 配对 D35/RS-A/RS-B = 82.3/87.7/85.6 % | [L2] | CRITIC_M:41, :55-58, :86 |
| X3(LR4) 与 FIR 良率打平；X3 瞬态：1 kHz 方波相对现表最多 +7.38 dB；"保证不削顶"须退≈10.5 dB(c6) vs FIR≈5.0 dB(c0)；X3 需**联动**限幅器（不是例外清单里的逐通道保护限幅器） | [L2 桌面计算]。**注意：原文的"L1 上界/L1 口径"是 ℓ1 范数（峰值上界），不是来源分级 L1**（见 §5-13） | CRITIC_N:60,:92-95,:113,:131 |
| LPX3-b：固定退 0.81 dB 可覆盖任意 \|x\|≤1 的数字削顶，但 c2 正弦下仍 +0.36 dB，守前提需退 1.17(正弦)/1.32(方波) dB；U-flat 装好直接用 MC：X3 23.1 / LPX3-b 23.1 / FIR V1-128 22.0 / LPX4-b-cap 21.0 %；折叠 4.3×、直接 4.8× 少于 FIR（MAC 比）；延迟 63 样点=1.3125 ms | [L2 桌面计算]（原文"（L1，已复现）"的 L1 同为 ℓ1 范数）；MAC 比的 L 级原文未标 | CRITIC_O:16,:46,:49,:58,:78 |
| LPX 的 MAC 估算**不能**与 F7 台架墙钟 463,273 直接相减（口径不同，1.79× 未解释） | — | CRITIC_O:21-25 |
| B6.3 探针每帧 CCNT 读次数：bench 25（链式），板上 33 | 源码 | CRITIC_E:170；PROBE:34 |
| ADSP-21569 1 GHz = MSEL 80 / DF 0 / CSEL 2（SYS_CLKIN0 25 MHz）；解码公式 `CCLK=(CLKIN/(DF+1))×MSEL/CSEL`，**无 ÷2**；数据手册门 fCCLK 400–1000 MHz(Table 19)、fPLL 1.20–2.00 GHz(Table 20)、fCKIN 20–30 MHz(Table 33) | HRM + ADI 源码 + 4 份 21569 配置头 | CRITIC_F:161-172 |
| Dolph-20：BW@1k 29.27°、@2k 14.51°；栅瓣临界 6236 Hz；1 kHz 超指向在假设地板 WNGn≥−10 dB 下 29.27°→22.66° | [L2/numpy]，地板为假设 | ACOUSTIC:76, :20, :272 |
| 只置换权重下标、不置换延时 → 聚焦处损失 4–13 dB | [L2] | ACOUSTIC:325 |
| 远场信号包：0 dB 档 RMS −23 dB；最热 3150 Hz 文件峰值 −8.49 dB；若笔记本满幅=板子满幅，对 `0x49A00000`(≈−4.8 dBFS) 余量约 3.7 dB（对应关系未实测） | [L3 算术] | CRITIC_P:53-54, :74 |
| 竞品 1 m 实测表（90° 32.0/24.8/25.4 dB；30°@1 kHz 22.5 dB）与我方模型的远场口径不可直接比较 | 原文未标级（KB-SPL-001:6 转引） | CRITIC_G:45 |
| "1.5 dB 重复性"全库无落盘出处 → [L4 工作假设，未落盘]；"2× 地板=3 dB"是 testing 自定，非 CTO 裁定 | [L4] | CRITIC_B:40,:147；CRITIC_C:27,:138 |

---

## 3. 前期环节线索

> 本范围（Sprint 7 的 critic / dsp / sim / tools）本质上是**后期**记录，前期环节只能间接看到。每条给"有记录+出处"或"未见"。

### 3.1 需求指标 / PRD — **有间接记录（转引）；PRD 正文不在本范围**
- 现行指标口径：JY/T 表 9 一级 90° 门限 10/20/25/10 dB（500/1k/2k/4k，`sprint3/audit/std_table9_compliance.csv`）；**PRD 承诺二级**（`prd_update.md:120`）；现行测试判据 ±90°≥12 dB（DEC-S6-TEST3-METHOD-01）——CRITIC_G:47（转引）。30° 门限一/二/三级 500 Hz 5/3/1、1 k 18/15/12、2 k 20/17/14、4 k 22/19/16——ACOUSTIC:129（转引）。
- 1 kHz 波束宽：R10（`decisions_log:243`）；PRD v2.4 把 BW@1k≤30° 降为工程参考（`prd_update.md:159`）；500 Hz/30° 一级评定 R8——CRITIC_G:43（转引）；ACOUSTIC:85 称"BW@1k ≤ 30° 规格线"。
- SPL：PRD ≥90 dB SPL/1W/1m（`decisions_log:994` 已 FLAG），内部口径 94.0 dB@1W/1m [L2 模型，待消声室坐实]，PRD 的最大声压级一行是 [L4] 占位——CRITIC_N:88, :90（转引）。
- **新增需求**：侧面 ±90° 抑制 30 dB 高于一级每个点，"是新需求，需要 decisions-log 条目与 PRD 变更"——CRITIC_G:47；对应 PRD v2.5 落库见 git 33b1966 的文件清单（`sprint2/docs/prd_update.md +15`，git 事实，非本范围文件正文）。
- CTO 口述的自家 rig 读数"正面 100 / 侧面约 80"按 L0 登记、不得作基线：CRITIC_A:13, :29, :24（DEC-S7-OBS-OWNRIG-01）。
- 需求原始来源（PRD 本体、CTO 原始 PRD 文字）：**未见**。

### 3.2 竞品样机拆机 — **无拆机报告本体；只有引用与衍生物**
- 几何标 [L1 拆机]：16 元 / d=55 mm / L=825 mm（DEC-S3-GEOM-01）；驱动拓扑 8 路 A/B 中心对称串联标 [L1 硬件]（DEC-S3-DSP-03）——ACOUSTIC:16-17（该"拆机"是谁的机器，本范围文字未说）。
- 竞品实测数据（转引）：KB-SPL-001:6 的 1 m 实测表，90° 32.0/24.8/25.4 dB、30°@1 kHz 22.5 dB（CRITIC_G:45）；竞品板在竞品 rig 16 dB@2k [L1 07-01]、自家 rig 18 dB@2k [L1 07-08]（CRITIC_A:25, :94）。
- 竞品整机可用于 B6.10 对比实验（CTO D7）：CRITIC_C:23, :50。
- 竞品固件包 HIT-9616A12（SPON RK3308）：登记为 KB-EXT-001（只登元数据，**不解包/不分析/不参考**），来源=同事自 SPON、渠道/授权未确认，C8 逾期 33 天：CRITIC_A:14, :26-27, :41；CRITIC_C:51。
- EXP_COMPET_BEAM_VS_FREQ（竞品波束 vs 频率的 07-09~15 实验，4 个数字无落盘记录，CTO D10 维持"未落盘不升级"）：CRITIC_A:28；CRITIC_C:32, :52。
- 拆机报告/拆机照片/BOM：**未见**。（范围外指针：`knowledge_base/competitor/full_teardown_v2.md` 在磁盘上存在，`git ls-files knowledge_base` 无该文件=未入 git；我只 `ls` 到名字，**未读**。）

### 3.3 方案 / 芯片选型 — **选型结论本体未见；有选型的事实基线与候选评估**
- 芯片：ADSP-21569（SHARC+：CRITIC_B:163；CCLK 1 GHz：CRITIC_J:14、PROBE:37）的**事实基线**见 CRITIC_F:159-172（寄存器/位域/公式/数据手册门限）；"21569 L1 不被数据 cache"(PROBE:186)。**LOCKED 芯片的裁定条目本体：未见**（"LOCKED" 在 26 份 md 里只出现 3 次，均为"无几何 LOCKED"类否定句：CRITIC_B:89, CRITIC_A:33,:52）。
- 阵列/算法基线：16 元、d=55、8 对串联、中心对称加权、broadside-only（ACOUSTIC:16-17）；Dolph-Chebyshev −20 dB 冻结 Q15 表（ACOUSTIC:18）；4 子带树 + FIRA 的 M2 路径（CRITIC_G:16-19；PROBE:25, :43）。
- Sprint 7 内的方案候选与处置：
  - B 系列（B1 EQ+限幅器 / B2 聚焦 v2 / B3 硬件叉 / B4 低频超指向 / B5 换窗 / B6.x 诊断 / B7）：CTO 处置见 CRITIC_C:50-58；critic 对推荐组合的逻辑核见 CRITIC_B:62-74。
  - 侧面 30 dB 候选（全部仅 [L2] 桌面）：单深表 D30/D35（CRITIC_G:31；CRITIC_H:60）；稳健扇区表 RS-A/RS-B（CRITIC_M:4,:55-58）；每通道 FIR V1-128（CRITIC_J:41）；X3(LR4 IIR)+联动限幅器（CRITIC_N:60,:92-95）、DDC 原样（CRITIC_N:32）、Keele 延时 CBT（CRITIC_N:24）；hybrid LPX3-b（CRITIC_O:16-18,:58）。**"X3 与 FIR 并列候选，X3 以逐通道限幅器为前提"**（CRITIC_N:62，PM 修正记录原文；其后 D2 又更正为"联动限幅器"）。**最终选定：未见**。
- Gate 1 / Gate 2：仅见一次"硬件叉 Gate-2"（CRITIC_B:71，B3 不做的理由之一）；Gate 裁定条目：**未见**。

### 3.4 开发板 / EZKIT 采购 — **未见采购记录**
- 检索：`采购|购买|订购|报价|供应商|下单|到货` 在 26 份 md 内仅 3 行命中，且都不是硬件采购：CRITIC_N:68（"是否购买 Keele 论文正式版本由 CTO 决定"）、CRITIC_D:100、:112（极性 QA 的 decisions_log 骨架"无采购"）。`EZKIT|EXKIT` 4 行命中，均为数据来源标签或 bring-up 清单名（CRITIC_C:38,:70；CRITIC_F:110；CRITIC_D:61）。
- 只有"板身份与资料"：板 = AD-EXKIT V2.1 + 21569 SOM，fw 9.N（CRITIC_D:61，转引）；bring-up 清单 `sprint3/audit/ezkit_bringup_checklist.md`、`sprint6/STAGE4_BRINGUP_CHECKLIST.md`、`BENCH_OPS_CARD.md`（CRITIC_D:61,:176-178）；KB 里有核心板原理图 V2.1（V1.0/V1.2 同）与 HRM（CRITIC_F:161-162）。
- Sprint 7 自身**没有板上回传数据**（见 §4-5）。

### 3.5 GitHub / 论文调研、框架选择、资料入库
- **GitHub**：**未见**（`GitHub|github|git clone` 0 命中）。arXiv/DOI 也 0 命中。ADI 资料来自 EngineerZone 例程 EE408（`Direct_Replacement`、`app.ldf`）：FIRBENCH:35；PROBE:90；CRITIC_E:99；`FIRA_IMPL.md:72` 记"CTO 顾问侧更正 2026-06-03"：CRITIC_E:72（转引）。
- **论文调研**（R2/R3 侧抑线）：R2 时论文与脚本只在 scratchpad，要求带种子入库，"C8 24 小时钟适用于文献"（CRITIC_H:38）；文献点评：Start 2003「up to 20 dB」是后向额外衰减、非侧抑实测；Zhu 2017 Table 3 为房间分区对比度 11–17.5 dB；鲁棒项仅在 Straube 2015/2018 摘录；Van Trees (2.208)、Doclo、van Beuningen、Gilbert & Morgan（CRITIC_H:41-43,:62）；"文献 16/16 md5 与字节数一致"（CRITIC_I:38）；Keele 2002 CBT：dbkeele.com "CBT Paper 2"、AES "All rights reserved"、作者自存副本禁转贴、audioartistry.com 是第三方（CRITIC_N:26），登记改为"第三方网站副本，非开放获取…不入 git；是否购买由 CTO 定"（CRITIC_N:68）；未存档论文抽取文本/截图（README_r3e:6）。文献登记表 `S7_LIT_REGISTER_SIDE30.md`（docs，范围外）。
- **框架/工具**：numpy/scipy 主轨 + **MATLAB R2026a（MCP）独立第二轨**（ACOUSTIC:5, :331；CRITIC_N:13；CRITIC_M:52）；CCES 2.12.1（CRITIC_F:145,:159）；桌面 gcc 11.4.0 / Python 3.10（CRITIC_D:34；FIRBENCH:79）；PM 工具 `s7_driver_pairing.py` 只需 numpy（docstring）。`pyroomacoustics` 在 26 份 md 与 161 个非 md 内 **0 命中=未见**（`CLAUDE.md:95` 写"声学仿真：Python pyroomacoustics（首选）"，与此不一致，见 §5-17）。框架选型的决策过程：**未见**。
- **资料入库纪律**：C8「外部输入 ≤24h 入库」——竞品固件 33 天逾期留痕(CRITIC_A:27,:54)；`knowledge_base/` 在 `.gitignore`（CRITIC_A:100）且只有 8 个 tracked 文件（`git ls-files knowledge_base`）；KB-EXT 文件在被忽略目录里却是 tracked，先例是 `knowledge_base/hardware_input` 同样 tracked（CRITIC_A:100）；KB-EXT 为新编号系列（CRITIC_A:41）。

### 3.6 团队 / 治理
- **角色**：PM；dsp-algorithm teammate（FIRBENCH:3；PROBE:3）；acoustic-simulation teammate `agent-acoustic-sim-v1`（ACOUSTIC:4, :375）；testing teammate（CRITIC_K:4）；独立 critic 子代理（CRITIC_G:3；CRITIC_L:3）；CTO 裁定/CTO_OK（CRITIC_C:42-61；FIRBENCH:6）。
- **门与制度**：POLICY-PROV-001 的 C1–C10 + SKILL §12 的 FG1/FG2/IO1/IO2/ST1 逐门表出现在每份 critic 文件里（如 CRITIC_B:80-94）；铁律五"撤回须全库逐处加标"（CRITIC_B:40）；POLICY §4A.2 C8 基线（CRITIC_A:27）；**三道关**（自动 verify → 独立 critic → CTO 常识审）：FIRBENCH:5；CRITIC_N:121；CRITIC_P:98；"CTO_OK 逐包先例 d524fde"（CRITIC_I:22）。
- **提交/变更纪律**：`team_config.md:45-50` commit discipline（CRITIC_C:116；CRITIC_C:36 要求显式 `git add` 路径）；team_config change-control 条款 :77/:83（CRITIC_A:33）；hook `.claude/hooks/cto-gate-softconfig.sh` 阻止未经 CTO_OK 暂存 `m1_softconfig`（CRITIC_A:16,:99）；冻结件/`.cproject`/`.project` 不得改（CRITIC_A:16；CRITIC_B:29）；critic 裁定落库规则：verdict 落 `sprint7/critic/CRITIC_*.md` 同 commit + log 尾加 `reviewer:` 行（CRITIC_C:153）。
- **reviewer 模型标**：A–F 为 `claude-fable-5-1`（CRITIC_A:1 等），G–P 为 `claude-opus-5-5`（CRITIC_G:10；CRITIC_H:64；…）；CRITIC_A:33 记：team_config 表载 06-10 的 `claude-fable-5`，而 07-20 各 log 行的 reviewer 标显示实跑 `claude-opus-4-8`。
- **LESSON 写入**：`agents/critic/memory.md`（CRITIC_M:69；CRITIC_O:82；提交 04e0e6a / cd113e2 的文件清单含该文件）。
- **标签纪律**：PM 把自己的操作化标成"CTO 裁定"被多次抓：CRITIC_I:19,:22；CRITIC_M:17；CRITIC_N:92；CRITIC_F:28 重申"CTO 裁定 / PM 注 / 待 CTO 裁"三标签（CRITIC_C 全篇据此逐条对照 CTO 原话，CRITIC_C:42-61）。

---

## 4. 阶段边界线索（日期 + path:行）

1. **Sprint 7 起点 = 2026-09-02**：b6bc5fe 是首个含 `sprint7/` 的提交；此前 `sprint7/` 不存在（CRITIC_A:24, :92）；上一个提交 c8eeb08 是 2026-07-22，之间 42 天空窗（git）。CRITIC_A:3 自称"Sprint 7 'A 入库整理'批次"，CRITIC_B:3 为"B 批次算法层升级提案"。
2. **S7-阶段一（提案/裁定/实施第一步）= 09-02 → 09-03**：A→F 六份 critic（CRITIC_A…F）；终点是 4e0b2ce(09-03 14:20) 的 DEC-S7-RULINGS-03（CRITIC_F:141-153, :204）。该阶段产出的是**待板验的桌面件**：D3 固件包、B6.3 探针、判读脚本——所有回填格留空（CRITIC_D:180；CRITIC_E:18；CRITIC_F:8；PROBE:5-6）。
3. **空窗 = 09-03 → 09-26（23 天无提交）**：之后第一份记录 CRITIC_G 的主题是另一条线。
4. **S7-阶段二（侧面 30 dB 线）= 09-26 → 10-02**：起点 33b1966（CRITIC_G:1,:5；CRITIC_H:6）；含"撤回子带边界"这一重要纠错（CRITIC_G:16-19；CRITIC_I:36）与"PRD v2.5"（git 33b1966）。
5. **证据级别的边界**：本范围内 Sprint 7 的全部新数字都是 [L2] 桌面（ACOUSTIC:5；FIRBENCH:4；PROBE:5-6；CRITIC_E:18；CRITIC_F:8）；**范围内未见任何 Sprint 7 板上/仪器 L1 回传**。要写进手册的"已验证"只能引 Sprint 7 之前的 L1（如 M2 板上 PASS、F7 463,273，转引自 CRITIC_B:23,:115）。
6. **09-29 = S-FIRB 放行**（CTO_OK，FIRBENCH:6）；此时 FIR 算力台架才可交测试员，结果仍待回传。
7. **10-02 = 当日**：s7ff_v1 信号包"已生成入库、过门中，三道关走完前不算已交付"（CRITIC_P:98）。
8. 文件名日期与批次：A/B/C=20260902，D/E/F=20260903，G/H/I/J/K=20260926，L=20260927，M/N=20260928，O=20260929，P=20261002。G–P 的轮次命名为 R1/R2/R3a…R3g，随后重新从"s7ff R1"计（CRITIC_P）。
9. 往前一阶段的标记（转引）：M2 板上 PASS（map 文件名 20260616，CRITIC_E:56）；DEC-S6-M2-BOARD-PASS-01（CRITIC_B:43,:115）；Sprint 5/6 决策被 Sprint 7 反复引作基线（§2.1）。

---

## 5. 疑点

**A. 来源与可信度**
1. **reviewer 模型标在 09-03 与 09-26 之间换了**：A–F `claude-fable-5-1`，G–P `claude-opus-5-5`（CRITIC_A:1；CRITIC_G:10）；CRITIC_A:33 还记 team_config 表载 06-10 的 `claude-fable-5`、而 07-20 各 log 行 reviewer 标显示实跑 `claude-opus-4-8`——合计出现过 4 种模型标：`claude-fable-5`(表, 06-10)、`claude-opus-4-8`(07-20 log)、`claude-fable-5-1`(09-02/03)、`claude-opus-5-5`(09-26 起)；CRITIC_A:33 自己把"表与实况脱节"列为 MINOR。手册引用 critic 结论时宜带模型标与日期。
2. **G–P 不是 critic 原文，是 PM 转录**：G/H 称"原文照录"，I–P 称"（原文）要点照录"（CRITIC_G:3；CRITIC_H:3；CRITIC_I:3；CRITIC_J:3；CRITIC_K:3；CRITIC_L:3；CRITIC_M:4；CRITIC_N:4；CRITIC_O:4；CRITIC_P:4），且同一文件内混有"PM 修正记录/PM 处置"（CRITIC_I:5, :43；CRITIC_M:62；CRITIC_N:56）；CRITIC_F 明言完整裁定只在 scratchpad、落库的是"去数值版"（CRITIC_F:137）；CRITIC_K:19 被 PM 事后原地补注（CRITIC_L:56 抓出）。A–F 反之为 critic 第一人称整份裁定，带"实跑命令"（如 CRITIC_A:71-102）。可信度：A–F > G–P 的 critic 部分 > 其中的 PM 部分。
3. **复核脚本存档不全且不可复跑**：只有 r1、r2、r3b、r3e、r3f、r3g、s7ff 七处存档；A–F、R3a(I)、R3c(K)、R3d(L) 没有对应存档目录，其 critic 脚本/日志按原文在会话 scratchpad（CRITIC_B:9-11；CRITIC_D:155；CRITIC_F:137；E 批的补丁演练也在 scratchpad 副本，CRITIC_E:7）；已存档的含会话临时目录绝对路径，"不能原样复跑"（README_r1:8；README_r3e:4；README_r3g:10；README_s7ff_r1:7）。`side30_r3e_scripts` 的首次入库是 R3f 的提交 46574ed 而非 R3e 的 04e0e6a；其 README 与 r3f README 近乎同文。
4. **KB 证据不在 git**：`knowledge_base/` 被 `.gitignore`，仅 8 个 tracked（`git ls-files`）；critic 引用的 KB-SPL-001、核心板原理图/HRM PDF、论文库都是本机文件，无法靠 git 历史核（CRITIC_A:100；CRITIC_G:45；CRITIC_F:161-162；CRITIC_I:38）。
5. **git 历史从 2026-06-02 才开始**（根提交 4bf0f52，共 155 个提交）：因此"首次入库日期"不能当作前期（需求/拆机/选型）文档的撰写日期；前期环节无法靠 git 定年月。佐证（git 事实）：`sprint2/docs/decisions_log.md` 首次入库 13be4b3 = 2026-06-02，`sprint2/docs/prd_update.md` 首次入库 4d7e528 = 2026-06-05，而二者内容属更早的 Sprint 2/3 决策。

**B. 数字/状态冲突、过期风险**
6. **"6.4 倍"与"1.79 倍"**：DEC-S6-M2-BOARD-PASS-01 的 6.4× 被指为跨口径（离板 ~130 µs 账 vs 板上墙钟），同口径为 1.794×（F7）/1.83×（H2 base）（CRITIC_B:23；CRITIC_C:38）；该 1.79× 在本范围终点**仍未解释**（B6.3 板上回填全空；CRITIC_O:23-24；FIRBENCH:109）。
7. **1.5 dB 重复性 / 1.9 dB / −43 dB / 13–16 dB 无落盘出处**：CTO 裁定"有测量无单独原始记录、维持未落盘、不升级"；1.5 dB 只能当 [L4 工作假设]，"3 dB=2× 地板"是 testing 自定（CRITIC_A:28；CRITIC_B:40；CRITIC_C:27,:52,:138）。手册里不得写成 [L1]。
8. **子带分界撤回**：1.5k/3k/6k 是错的，真实 3k/6k/12k；冻结头文件未改，改以 ERRATUM 旁注（git 33b1966 文件清单：两份 `tree_filterbank.h.ERRATUM.md`）。ACOUSTIC 里 §3、§4.2 作废，但原文仍留在页内（ACOUSTIC:3,:22-23,:133,:207）；G 说 SB0 通带到 2.75 kHz 为 0 dB(CRITIC_G:18)，R3a 细化为 ≤2.5 kHz 0.00、2.75k −0.37 dB(CRITIC_I:36)，以后者为准。
9. **审计过程中改过的数**（早期文档里可能残留旧值，手册只取终值）：RS-A 与探索版相差 "<0.002"→0.0025（CRITIC_M:75,:97）；保证不削顶 10.4→10.5 dB（CRITIC_N:113）；R3e 的 "0–2.8 dB"、R3f 的"约 4 dB SPL 余量"已删（CRITIC_M:87；CRITIC_N:110）；CCLK 解码 ÷2 公式已撤（CRITIC_F:180）；"多约 70%"→+74%（CRITIC_O:67）；29.28→29.27°（CRITIC_B:44）。
10. **良率数字跨报告不可直接比**：同叫"U-flat 装好直接用"，V1-128 在 CRITIC_J:41 为 20.4%（仓库 CSV，7 频段）/ README_r3b:4 为 20.7%，在 CRITIC_O:58 为 22.0%（critic 自写 MC，6000 阵；频段数原文未写）；R3f 里出现 "V1-128t" 变体（CRITIC_N:31），与 "V1-128" 的关系本范围未说明。模型/频段数/种子不同，且 H 指出联合良率随误差模型从 1% 到 26% 波动（CRITIC_H:24-30）。
11. **审计模式：修正稿自带新错**：N 的 delta 判 FAIL（CRITIC_N:78）、F 的 delta-3 判 FAIL（CRITIC_F:151）、E 的 delta 残留 R-1…R-3（CRITIC_E:191-193）、D 的残留（CRITIC_D:187）。**这些"待修/顺手修"的 MINOR 是否已修，本范围无法核**（对应文档在 `sprint7/docs/*`，范围外）。
12. **计数不一致（小）**：CRITIC_F 的汇总表 INFO 数多于逐条行（包 1 写 3 条、只列 P1-I1；包 2 首轮写 3 条、只列 P2-I1/I2；CRITIC_F:14-15 vs :33,:64-65）；CRITIC_J 首轮"5 MINOR"而逐条只列"MINOR 5–8"4 项（CRITIC_J:8-24）；CRITIC_G/H 未给计数，上文为自数。
13. **符号撞车："L1" 有两个意思**：POLICY 的来源分级 L1（实测），与 N/O 里的 "L1 上界 / L1 口径 / L1 相对现表同一路"——后者是**ℓ1 范数（脉冲响应绝对值之和，峰值上界）**，如 `AP700·AP1600 的 L1 = 4.333，比单位正弦增益高 +12.7 dB`（CRITIC_N:15, :17-19, :48, :113, :133；CRITIC_O:16, :35-36, :65, :86）。这些数都是 [L2 桌面计算]，**手册若把"L1 口径"写成实测等级就是 C2 越级**。

**C. 授权与治理**
14. **"PM 把操作化标成 CTO 裁定"反复出现**：CRITIC_I:19（把"立项改架构"写成冻结令解冻授权）、:22（对未来固件包整体 CTO_OK）；CRITIC_M:17（RS-B 只获"一张表"同意）；CRITIC_N:92（把联动限幅器说成例外清单已有）。（反例：CRITIC_C 初审的 F-3/F-4 把 CTO 原话误判成 PM 加工，CTO 原话补交后作废：CRITIC_C:124——说明这类判定本身也必须对照 CTO 原话。）手册里"CTO 裁定"必须有 CTO 原话，RS-B(sel 5) 仍是"PM 追加，待 CTO 过目"（CRITIC_M:71）。
15. **竞品固件接触程度**：CRITIC_A:26 发现会话记忆里有解混淆级内容，delta 后 KB-EXT §4 重写为 6 项接触清单（含 bin md5 流式、全文件 strings、头部区解混淆；CRITIC_A:125），"比初审掌握的还完整"；接收基线缺失、授权"未确认"、持有合法性待 CTO（CRITIC_A:27；CRITIC_C:51）。
16. **一键门假绿潜伏**：`run_wtbl_checks.sh` 第 1 步自 7686c05(09-26) 起永不 FAIL，R3a 漏审，R3e 才抓到（CRITIC_M:11-16）。说明"一键门 PASS"必须附证伪反证才算数（已加 `run_wtbl_falsifiers.sh`，CRITIC_M:121）。

**D. 缺口（本范围未见）**
17. **未见**：PRD 本体、拆机报告本体、芯片/板选型与采购裁定、GitHub 调研、框架选型过程、任何 Sprint 7 板上 L1 回传。`pyroomacoustics` 全 0 命中，而 `CLAUDE.md:95` 称其为声学仿真首选；实际用 numpy/scipy 自写 + MATLAB 第二轨（ACOUSTIC:5,:331）。
18. **本范围唯一的 Gate-2 提及**在 CRITIC_B:71；Gate 1/2 的裁定记录需到 decisions_log（范围外）找。
19. **范围外指针（未读）**：`knowledge_base/competitor/full_teardown_v2.md` 与 `SPL_anechoic_measurement_archived.md` 在磁盘上存在但未入 git。

**E. 终点时仍待 CTO / 未闭合**（原文标注，截至 2026-10-02）
20. RS-B(sel 5) 是否保留；选表前须做 30° 测量（由谁/何时出单待 CTO 定）（CRITIC_M:71,:81）；联动限幅器是否纳入、X3/FIR/LPX 的最终取舍（CRITIC_N:62,:95；CRITIC_O:15-20；"限幅器/D5 闸需在写每通道固件包时重审"，CRITIC_O:134）；s7ff 信号包的输入电平线与余量由 CTO 定（CRITIC_P:52-54,:74）；EXP_COMPET 4 数是否永久"未落盘"（CRITIC_C:52）；1.79× 的解释依赖 S-B/B6.3 板上回填（FIRBENCH:109；CRITIC_O:23-24），范围内尚无回填。

---
*本摘要所有判定/数字均为转录；未对任何数字做独立复算；未改仓库。*
