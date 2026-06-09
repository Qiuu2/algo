# Sprint 4 输入清单（Sprint 4 Input Register）

**文档 ID**：DOC-S4-INPUT-01
**建立日期**：2026-06-02（CTO 拍板：FIRA 适配评估 Split-Task 迁移复杂度入 Sprint 4 输入）
**用途**：聚合所有需在 Sprint 4 处理的输入项（迁移/COMSOL/硬件追问等），防 HIGH 级预警/复杂度只活在单份评估文档、Sprint 切换时丢失（PF-9 同类陷阱）。
**可检查性**：本清单是 Sprint 4 启动的 checklist；每条挂出处，状态随实测/实施回填。

---

## INPUT-1：FIRA Split-Task 迁移复杂度 🔴 HIGH（CTO 拍板 2026-06-02）

**确认结论**：我方 4 子带 dyadic 树形为 **Split-Task 模型**（FIR 卷积段 offload 到 FIRA + 加减/合成/Q31 钳位 留核内），**非 1:1 FIRA 替换**。
**迁移复杂度**：🔴 **HIGH（需手动切分 + bit-exact 回归）**
**出处**：`sprint3/audit/fira_fit_assessment.md` 第2项（结构匹配）+ 第5项（迁移清单）
**挂接**：DEC-S3-DSP 迁移系列；R14（FIRA 定点 bit-exact 风险，`decisions_log.md`）；DEC-S3-PROC-01（定点路线 LOCKED）

### dsp-algorithm 三项 migration 待办（Sprint 4 交付）
| # | 待办 | 出处 | 状态 |
|---|------|------|------|
| **①** | **明确哪些段下 FIRA**（树形中可 offload 的 FIR 卷积段：各级半带卷积段，6–9 段） | fira 第2/5项 | ⏳ 待 Sprint 4 |
| **②** | **明确哪些留核内**（detail 残差减法 / 合成加法 / Q31 饱和钳位 —— FIRA 只做 MAC，无向量加减/钳位） | fira 第2项（hwref:75718-723）| ⏳ 待 Sprint 4 |
| **③** | **bit-exact 回归怎么验**（FIRA 版 vs 桌面 MATLAB/`tree_verify.c` 定点基准逐位对齐；signed-fractional Q15×Q31 ↔ 驱动枚举口径映射 + HW ×2/decimate 后处理） | fira 第3项（hwref:75713/75722）；回归基准 `sprint3/dsp/tree_verify.c`/`tree_verify_adversarial.c` | ⏳ 待 Sprint 4 |

> **不可逆闸门联动**：上述 migration 在 R14（bit-exact L1 实测）关闭前为**可行性待验证**项；其算力收益**不得**计入任何选型/流片/客户承诺依据（critic `skill.md §11 C9` 守门）。

---

## INPUT-2：COMSOL 立项几何/边界输入（既有，Sprint 4 承接）
**出处**：`sprint3/audit/comsol_geometry_input.md`
**含**：盆口 Sd（Q-③）、箱体宽深（Q-④，待实测）、后腔无吸音边界（R13）、有限障板衍射几何。
**关联风险**：R9（180° 后向不可评）、R13（后腔无吸音乐观 5–10dB）、R11（高频前向 PF-6 乐观）。
**状态**：⏳ 待硬件追问 Q-③/④/⑤ 回填（`hardware_followup_queries.md`）+ Sprint 4 启动建模。

## INPUT-3：硬件精度追问残留（既有，Sprint 4 承接）
**出处**：`sprint3/audit/hardware_followup_queries.md` + `KB-HW-002`
**残留**：Q-②/③（额定功率/阻抗待厂家 T/S）、Q-④（箱体宽深待实测）、Q-0（3W 口径 CTO 直跟）。

## INPUT-4：测试阶段驱动绝对 SPL（R3a，跨 Sprint 承接）
**出处**：`DOC-DRV-META-01`（SPL 曲线 6 metadata 待测试团队回填）+ `KB-DRV-TEST-001_raw/`
**状态**：⏳ X2 三轨重算阻塞于 M1 测距/M2 电压回填 + 同一性确认。

---

*DOC-S4-INPUT-01，PM 建册 2026-06-02（CTO 拍板 FIRA Split-Task 入 Sprint 4 输入）。INPUT-1 为本次新增正式条目；INPUT-2~4 为既有 Sprint-4-bound 输入聚合，防散落丢失。*
