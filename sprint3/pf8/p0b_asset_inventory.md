# PF-8 P0-B：d=30 资产盘点表（PM 直跑）

**任务**：TASK-PF8-P0B
**执行**：Project Manager Agent（PM 直跑 grep + 三档分类）
**日期**：2026-05-29
**待复核**：Critic（按 Q2+ 要求，复核**三档分类判定逻辑**，非 grep 准确性）
**关联**：PF-8 几何参数假性完成；DEC-S3-GEOM-01（待 P1-A 立）；ESCALATE#2 near-miss（cces_template 硬编码）

---

## 0. 结论先行
- 全项目 **31 处资产**引用 d=30/30mm（29 文件 + 2 teammate memory + C config）。
- 三档：**重审 14 项**（活文档/决策/C 代码，P1-A 必改）｜**作废 11 项**（历史结论/数据，归档加标不删）｜**不影响 6 项**（巧合"30mm"或已正确标注为历史对照）。
- **C 代码 near-miss #2 确认**：`sprint2/dsp/cces_template/src/config.h:59 ARRAY_ELEMENT_SPACING_MM=30u` + `sprint2/dsp/cces_template/src/beamformer.c:107` 使用 + `config.h:95` 缓冲深度按 d=30 算（=54，d=55 需 ~92）。属**已废弃全速率模板**、**非 LOCKED 树形**、**无产物编译** → 走 P1-A 重生成 + critic 确认"残留已清"（Q1+）。
- P1-A 工作量估算：**重审 14 项**（含 1 项 C 代码重生成）+ **作废 11 项加归档标记** ≈ 一个 project-document teammate 批次（建议拆 2-3 段写盘防 socket 中断）。

## 1. 分类判据（三档定义）
| 档 | 定义 | P1-A 动作 |
|----|------|----------|
| **重审** | d=30 是**当前活跃基线/决策/活文档/可编译代码**的引用 | 改为 d=55 或加作废标记+新决策 |
| **作废** | d=30 是**已被 d=55 取代的历史结论/数据/脚本** | 归档加"基于错误几何 PF-8,不可作决策依据"标记,**不删除** |
| **不影响** | "30mm"系**巧合**(散热/螺钉)或**已正确标注为历史对照** | 无需动(可选措辞微调) |

## 2. 盘点表

### 2.1 重审（14 项，P1-A 必改）
| # | 资产 | 行 | d=30 用法 | P1-A 动作 |
|---|------|----|----------|----------|
| 1 | `sprint2/docs/decisions_log.md` | 46/55/151/166 | **DEC-S2-006 LOCKED d=30** + Gate1 + DEC-S1-002 | DEC-S2-006 作废标记 + **新增 DEC-S3-GEOM-01** |
| 2 | `CLAUDE.md` | 85/165 | 启动 prompt 示例 + "待决策(30mm候选)" | 删候选表述,锁定一览改 d=55 |
| 3 | `sprint2/docs/PROJECT_HANDOVER.md` | 15/71/75/83 | "两条几何并存" + d=30 线 | 删"并存",改 d=55 单一基线 |
| 4 | `sprint2/docs/simulation_coverage_audit.md` | 34/36/57/93 | PF-7 d=30 注 | 新增 PF-8 条目 + P0-1 MC d=30 标作废 + P0-3 升唯一基线 + 引 P0-A 栅瓣 |
| 5 | `sprint2/docs/prd_update.md` | 8/17/21/23 | PRD 活跃基线 d=30/450mm | **P1-B**：改 d=55/825mm |
| 6 | `sprint2/docs/sprint3_kickoff_checklist.md` | 14/31/32/43 | d=30 基线 + R4/G6 重算项 | 改基线 + R4 关闭(d=30 BW@2k moot) |
| 7 | `sprint2/docs/sprint3_procurement_kickoff.md` | 55/93 | 采购规格 + **工装夹具 450mm/d=30 定位** | ⚠️ 工装尺寸→825mm,须通知硬件/结构 |
| 8 | `sprint2/dsp/budget_calc.py` | 17/55 | `D=0.030` 参数 + d/λ 栅瓣注 | 更新 D=0.055(注:不改 MMAC 结论,d 不影响算力) |
| 9 | `sprint2/dsp/dsp_design.md` | 35/562 | 规格表 d=30 + "d不影响算力" | 更新规格表 d=55 |
| 10 | `sprint3/dsp/dsp_8ch_report.md` | 45 | ⚠️ **活跃 S3 报告仍写"d=30mm 全频段 d/λ<1.0 无栅瓣"** | 改 d=55 + 栅瓣结论按 P0-A(6.2kHz 起) |
| 11 | `sprint3_status.md` | 18/26 | d=30 残留注 + 竞品 55mm 表 | 更新状态 |
| 12 | `agents/acoustic-simulation/memory.md` | 474 | 记忆旧 d=30 基线 55.2° | 清理 d=30 记忆,载 d=55 唯一基线 + PF-8 教训 |
| 13 | `sprint2/patent/formulas.md` | 38/120/214/216 | 公式 worked example 用 d=30 | (低优先)更新算例 d=55 |
| 14 | `sprint2/dsp/cces_template/src/config.h` + `…/beamformer.c` | cfg:59/95, bf:107 | **C 硬编码 d=30 + 缓冲深度** | **重生成 d=55 config**(near-miss#2);critic 确认残留已清(Q1+) |

### 2.2 作废（11 项，归档加标，不删）
| # | 资产 | d=30 用法 | 处置 |
|---|------|----------|------|
| 15 | `deliverables/Gate1-baseline-array-validation-2026-05-26.md` | Gate1 锁 d=30/0.45m | 加 PF-8 归档标记 |
| 16 | `sprint2/acoustic/1khz_optimization.md` | d=30 超指向分析(PF-7) | 归档标记(d=55 见 P0-3) |
| 17 | `sprint2/acoustic/array_sweep.py` | Sprint2 d=30 扫描 | 归档(被 sweep_d55.py 取代) |
| 18 | `sprint2/acoustic/diff_1khz_optimization.py` | d=30 差分(PF-7) | 归档(d=55 P0-3 取代) |
| 19 | `sprint2/acoustic/rework_critic.py` | d=30/35 对比 | 归档 |
| 20 | `sprint2/acoustic/sweep_report.md` | d=35 主+d=30 栅瓣阈 | 归档 |
| 21 | `sprint2/critic/critic_review.md` | d=30 vs 35 冲突评审 | 归档(历史评审记录) |
| 22 | `sprint2/docs/memory_update_proposal.md` | d=30 决策提案 | 归档 |
| 23 | `sprint2/docs/sprint3_retrofit_assessment.md` | d=30 算法基线 vs 竞品错配 | 归档("两几何错配"前提已被统一决策取代) |
| 24 | `sprint2/SPRINT2_CTO_REPORT.md` | Sprint2 推荐 N=24/d=30 | 归档(推荐已被取代) |
| — | (P0-1 MC d=30 场景数据) | 在 audit 内,归 #4 处理 | 标作废 |

### 2.3 不影响（6 项，巧合或已正确标注）
| # | 资产 | 原因 |
|---|------|------|
| 25 | `agents/hardware-design/skill.md:494/512/514` | "30mm"=散热片包络/高度范围,**非阵元间距** |
| 26 | `agents/structure/memory.md:507` | "螺钉间距≤30mm",**非阵元间距** |
| 27 | `sprint2/docs/POLICY-PROV-001:116` | d=30 仅作回填表 example,**已正确注 d=55 迁移** |
| 28 | `sprint3/acoustic/sweep_d55.py:383+` | d=30 仅作**历史对照**(bw_1k=55.2),脚本本身是 d=55 |
| 29 | `sprint3/acoustic/sweep_d55_report.md:114/165` | d=30 仅历史对照 |
| 30 | `sprint3/critic/critic_review_s3.md` | 评审记录,正确识别 d=30 残留(对象已单列#14) |

## 3. 给 P1-A 的工作量估算
- **重审 14 项**：12 项纯文档编辑（decisions_log 最重，含新 DEC-S3-GEOM-01）+ 1 项 PRD(P1-B) + **1 项 C 重生成**（config.h d=55 + 缓冲深度重算 + beamformer 重验，须 critic 对抗复核 per §3/Q1+）。
- **作废 11 项**：仅加归档标记，机械工作。
- **不影响 6 项**：不动。
- 建议 P1-A 派 project-document **拆 2-3 段写盘**（文档批改易长跑触发 socket 中断）；C 重生成单独走 dsp + critic。

## 4. 须 CTO 知悉的连带影响
- **#7 工装夹具**：采购工装按 450mm/d=30 定位，d=55 后阵长 825mm（+72%），**夹具须重做** → 通知硬件/结构（连带 PRD 安装可行性 P1-B）。
- **#14 near-miss #2**：C 硬编码已确认在废弃模板，非 LOCKED、无产物；按 CTO Q1 走常规清理。

---

*TASK-PF8-P0B，PM 直跑，2026-05-29。待 Critic 复核三档分类逻辑（Q2+）。grep 准确性确定性、不复核；复核分类判定是否合理（P1-A 工作量依赖此）。*
