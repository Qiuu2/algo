# v1 路线裁定 + 三道关新政 — 落地包 DRAFT（不 commit；critic R10 先门，lead 过门后 apply+commit）

> 算力线收官 2026-06-05：focus 实测 49.03 MCPS [L1]（本文 86-144[L4] 退役）；算法侧 margin 由 2.04-2.31 升
>   实测口径，整系统残余 1.46-2.14x[L4]；正式阈值 T2 ≥1.5x。DEC-S5-BUDGET-L1-01/-CRITERION-01-FINAL。本文以下存史。

> 缘起：CTO v1 路线三裁定 + POLICY 新条（三道关），2026-06-04。裁定substance逐字采纳，不改写。
> 原则：历史按写时为真；活状态/路线落 decisions_log；规则落 POLICY/CLAUDE/team_config。引用 file:line。
> 两线数字零交叉纪律不变（FIRA/算力线 vs 声学/几何线）。

---

# 1. decisions_log 条目（供 lead 追加 `sprint2/docs/decisions_log.md`）

## 1.1 summary-table 追加行

```
| **STEER v1 路线** | ✅ **v1=聚焦/分区（现板固件线）；角度偏转=独立立项（CTO 后评 ROI）**（DEC-S5-STEER-V1-01，2026-06-04）| 转向定义二选一已裁：v1 走 broadside 聚焦/分区（现板可负担，算法侧最坏 margin **2.04x**）；角度偏转拓扑数学不可达 [L1]，须 16ch 硬件叉 + SC-S3-GEOM-01 d 重议，单独立项。聚焦增量 **86–144 MCPS [L4]**（2.88 MMAC/s × 30–50 cyc/MAC 板证包络），聚焦后算法侧 margin **2.04–2.31x**（口径修正见 STEER scan R9 台账：49x/340x 同源 1cyc/MAC 理想记账双双作废）。详见「STEER v1 路线」节 |
| **STEER 优化排序** | ✅ **HW-1(IIR EQ offload) 最高优先 + item-3 EQ PRD 同推**（DEC-S5-OPT-ORDER-01，2026-06-04）| 基于修正后真实余量 2.04–2.31x：(1) HW-1 IIR 加速器 EQ offload 评估 = 最高优先（聚焦后余量紧，EQ=§8 item-3 最大威胁，且为聚焦/分区成立前提钥匙）+ item-3 EQ 链 PRD 规格化（joint）；(2) 聚焦增量上板小 harness（86–144 [L4]→L1）；(3) FRAME/ORCH 按收益排后；ORCH-4 = measure-first likely KEEP（CTO 认可）。依赖：DEC-S4-CRITERION-01 正式阈值与 item-3/WCET 共依赖 |
| **三道关新政** | ✅ **workflow 产出三道关，含修正稿**（DEC-S5-POLICY-3GATE-01，POLICY v1.8，2026-06-04）| 任何 workflow/多 agent 产出（**含修正稿**）须过：自动 verify(初筛) → 独立 critic 门 → CTO 常识合理性审，缺一不可，**不得假设「修过即对」**。缘起 R8（synthesizer 撤销自家 verifier 的纠正）+ R9（修正稿自带两处偏乐观新错）。详见 POLICY-PROV-001 §4B + CLAUDE.md/team_config 同步 |
```

## 1.2 详细节（追加到 decisions_log 末，STEER 段）

```
## STEER v1 路线裁定（2026-06-04，CTO 正式裁定；本节录裁定与依据）

### DEC-S5-STEER-V1-01：v1 = 聚焦/分区（现板固件线）；角度偏转 = 独立立项
- **裁定（substance 逐字）**：转向定义走「聚焦/分区」做 v1（现板可负担，算法侧最坏 margin 2.04x）；
  「角度偏转」（拓扑数学不可达 [L1]，16ch 硬件叉 + d 重议）单独立项，CTO 后续评 ROI。
- **数字依据（口径修正后）**：
  - 聚焦增量 = **86–144 MCPS [L4]**（fractional-delay FIR 2.88 MMAC/s × **30–50 cyc/MAC 板证包络**；
    源 dsp_8ch_report.md:59-72 的 2.88 MMAC/s 桌面 MMAC 记账 × 板上真实 cyc/MAC）。
  - 聚焦后算法侧 margin = **2.04–2.31x**（= 1000 MCPS [L1, CCLK 实测 1e9] / (347.45 [L1] + 86–144 [L4])）。
  - **49x / 340x 双双作废**：49x=1500/30.56 系桌面理想 1cyc/MAC 整路径余量（类别错挂聚焦增量）；
    340x=1000/2.88 同源理想记账；同口径已被板上 0.92x 推翻（decisions_log:234/770）。
    修正台账见 STEERING_HEADROOM_SCAN.md 顶「修正台账 #2（critic R9）」。
  - **FLAG-A [L1] 基础**：角度偏转不可达 = 对称实阵 broadside-only（AF 纯实偶函数，dsp_8ch_report.md:164
    + critic_review_s3.md:106 + {c,15-c} 串联 [L1/硬件实测]）；DEC-S3-DSP-03 broadside-only 一致。
- **隔离**：聚焦疗效 = **[L3/待 acoustic-sim + PRD 确认]**，非 load-bearing 直到声学 teammate 确认。
- **状态**：v1 路线锁定聚焦/分区；角度偏转转独立项（16ch 叉 ROI 待 CTO 后评）。FIRA/算力收益仍 C9 纪律
  （DEC-S4-C9-RELEASE-01 松绑附诚实分母：任何聚焦增量呈现须连体 §8 未计入清单 43–379 MCPS）。

### DEC-S5-OPT-ORDER-01：优化执行排序（基于修正后真实余量 2.04–2.31x）
- **裁定（substance 逐字）**：HW-1（IIR offload EQ）最高优先（聚焦后余量紧，EQ=item-3 最大威胁必须先解，
  也是聚焦/分区成立的前提钥匙）；配套小 harness 上板实测聚焦增量（86–144 [L4]→L1）；其余 FRAME/ORCH 按
  收益排后；ORCH-4 同意 measure-first likely KEEP。item-3 EQ 链 PRD 规格化优先推进，与 HW-1 评估一并做。
- **排序落字**：
  1. **HW-1 IIR 加速器 EQ offload 评估** + **item-3 EQ 链 PRD 规格化**（joint，最高优先）。理由：聚焦后
     算法侧 margin 仅 2.04–2.31x，EQ（§8 item-3，0–150 MCPS [L4]，整系统残余最坏 ~1.0x 的主威胁）必须先解；
     EQ offload 也是聚焦/分区成立的前提钥匙。
  2. **聚焦增量上板 harness**：86–144 MCPS [L4] → [L1]（小 harness，DMA/中断同测，对应 §8 follow-up）。
  3. **FRAME/ORCH 按收益排后**（FRAME-1 区间 86.9–341.6 MCPS [L4]、ORCH-1 ~3.2–3.6x [L4] 等，
     均 R14 bit-exact 重门 gated）。
  4. **ORCH-4 = measure-first likely KEEP**（CTO 认可）。
- **依赖**：DEC-S4-CRITERION-01 的正式阈值（实时下限+余量政策）与 item-3 EQ PRD + WCET 实测共依赖——
  HW-1/item-3 落定后方能拍正式阈值。
- **C9 纪律**：所有 offload/FRAME/ORCH 收益在各自 R14-类闸关闭前 [L4/待验证]，呈现连体未计入清单。

### DEC-S5-POLICY-3GATE-01：workflow 产出三道关（POLICY v1.8）
- **裁定（substance 逐字）**：workflow/agent 输出每一轮都可能引入新错，包括修正错误的那一轮。
  POLICY-PROV-001 增条：任何 workflow 产出（含修正稿）三道关——自动 verify(初筛) → 独立 critic 门 →
  CTO 常识合理性审，缺一不可，不得假设「修过即对」。
- **缘起**：R8（synthesizer 撤销自家内部 verifier 已纠正的算错——21.7 MCPS 错下界）+ R9（STEER-2 修正稿
  自带两处偏乐观新错：2.55x 低端应 2.31x、3 cyc/MAC 下界无板证）。两轮均「修正动作本身引入/遗漏错」。
- **落点**：POLICY-PROV-001 v1.8 §4B（全文，见本包 §2）+ CLAUDE.md 治理摘要同步（§3）+ team_config 团队
  法同步（§4）。critic 评审时显式列三道关状态（与 C1–C10 并列）。
```

---

# 2. POLICY-PROV-001 文档编辑（v1.7 → v1.8）

> 遵其既有 convention：① 头部版本行追加 v1.8 描述；② 正文加 §4B 正式条款；③ 文末 changelog 追加 v1.8 行。
> （v1.6→v1.7 即此式：头部版本行 + §4 铁律九 + 文末 changelog 行 + 关联 critic skill §11。三处。）

## 2.1 头部版本行（change block）

old:
```
**版本**：v1.7（v1.6 增 铁律八/C9 FIRA-offload 不可逆闸门，v1.7 增 铁律九/C10 硬件不可逆动作闸门，均 CTO 拍板 2026-06-02，见文末增补与 §4/§7）｜ 以下为 v1.5 及更早：...
```
new（仅在 v1.7 描述前插入 v1.8 段，其余逐字保留）:
```
**版本**：v1.8（增 **§4B 三道关流程闸**——任何 workflow/多 agent 产出含修正稿须过 自动verify→独立critic门→CTO常识审，缺一不可、不得假设「修过即对」；CTO 拍板 2026-06-04，缘起 R8/R9 修正稿自带新错，见文末增补与 §4B）｜v1.7（v1.6 增 铁律八/C9 FIRA-offload 不可逆闸门，v1.7 增 铁律九/C10 硬件不可逆动作闸门，均 CTO 拍板 2026-06-02，见文末增补与 §4/§7）｜ 以下为 v1.5 及更早：...
```
（"以下为 v1.5 及更早：..." 起的整段 v1.5/v1.4/v1.3/v1.2 描述逐字不动。）

## 2.2 正文新增 §4B（插入到 §4 九条铁律之后、§4A 入库传播义务附近——作为流程闸独立小节）

```
---

## 4B. 三道关：workflow 产出验证闸（v1.8 新增，CTO 拍板 2026-06-04）

> **类型**：强制流程制度（治理 agent-workflow 输出质量，非数字定级）。与铁律一–九（管数字 provenance）
>   正交：铁律管「数字身份证」，本条管「产出经过几道独立检验」。

**核心原则**：**workflow/多 agent 的每一轮输出都可能引入新错——包括「修正错误的那一轮」。**
任何 workflow 产出（设计、诊断、补丁、数字、报告，**含修正稿/二次修正稿**）在被采信或下游引用前，
**必须依次通过三道关，缺一不可**：

1. **自动 verify（初筛，NOT 门）**：workflow 内部的 verifier/自检/自审。仅作初筛过滤，**不构成门禁**——
   它与产出者同上下文，可被同一盲点污染（甚至撤销自己已做对的纠正，见缘起 R8）。
2. **独立 critic 门（THE GATE）**：全新上下文的独立 critic teammate，出具带 `reviewer: critic @
   <exact model ID> / <date>` 的 verdict。这是唯一放行门。in-context 调 critic skill 自审 **不算**
   （team_config Commit-discipline / Fallback 条款一致）。
3. **CTO 常识合理性审（FINAL）**：CTO 对数量级/方向/口径做常识性 sanity check（如「2.9/1000 该是 ~340x
   不是 49x」——本条缘起之一）。前两道关均可能放过量级/口径错，CTO 审是最后兜底。

**红线**：**不得假设「修过即对」。** 修正稿与原稿同等过三道关；修正动作本身是新一轮 workflow 输出，
同样可能引入/遗漏错（缘起 R9：修正稿自带两处偏乐观新错）。critic 评审报告须显式列三道关执行状态。

**缘起**：R8（2026-06-04，synthesizer 撤销其内部 verifier 已纠正的 21.7 MCPS 错下界——「自动 verify」被
同上下文推翻）+ R9（STEER-2 「49x」修正稿自带 2.55x 低端算错应 2.31x、3 cyc/MAC 无板证下界——修正稿新错）。
两案证明：单靠 workflow 自检不足；独立 critic + CTO 常识审是命门。
```

## 2.3 文末 changelog 追加（在 v1.7 行之后）

```
*POLICY-PROV-001 v1.8，2026-06-04（CTO 拍板）：新增 **§4B 三道关 workflow 产出验证闸**——任何 workflow/多 agent 产出（含修正稿）须依次过 自动verify(初筛) → 独立critic门 → CTO常识合理性审，缺一不可，不得假设「修过即对」；缘起 R8（synthesizer 撤销自家 verifier 纠正）+ R9（STEER-2 修正稿自带两处偏乐观新错）。与铁律一–九正交（管流程检验道数，非数字 provenance）。同步落 CLAUDE.md 治理摘要 + .claude/team_config.md 团队法。*
```

---

# 3. CLAUDE.md 治理同步（最小插入）

> 三道关是 agent-workflow 流程规则。最自然落点 = §安全护栏（Agent Team 运行规则）追加一条 item 7
>   （与既有 5「文件写先建议后执行」、6「BLOCKER 立即停」同类流程规则）。另在治理铁律摘要末加一行指针。

## 3.1 安全护栏 block 追加 item 7（change block）

old:
```
5. 所有文件写操作：先生成"操作建议"，等人类确认后执行
6. 遇到 BLOCKER：立即停止并以结构化格式向人类报告
```
new:
```
5. 所有文件写操作：先生成"操作建议"，等人类确认后执行
6. 遇到 BLOCKER：立即停止并以结构化格式向人类报告
7. 三道关（POLICY v1.8 §4B）：任何 workflow 产出（含修正稿）须 自动verify(初筛)→独立critic门→CTO常识审，缺一不可；不得假设"修过即对"（修正稿同样过门）
```

## 3.2 治理铁律摘要末加一行指针（在 C1–C10 表 / 九铁律之后，DSP 专项之前的合适处）

在 `### 九铁律（一句话）` 段末追加一行（不改九铁律本体）：
```
> **三道关（POLICY v1.8 §4B，流程闸，非铁律）**：workflow 产出含修正稿须 自动verify→独立critic门→CTO常识审，不得假设"修过即对"（缘起 R8/R9 修正稿自带新错）。
```

---

# 4. .claude/team_config.md 同步（团队法，紧邻 Commit discipline）

> 三道关与 Commit-discipline/Fallback 同属团队过程法。落点 = Commit discipline 节之后新增小节。

在 `## Commit discipline ...` 节（含 Fallback 条款）**之后**新增：
```

## Three-gate verification (2026-06-04, CTO-mandated — POLICY v1.8 §4B)
- **每一轮 workflow 产出（含修正稿）都可能引入新错——包括修正错误的那一轮。** 三道关缺一不可：
  ① 自动 verify（workflow 内部自检）= **初筛，NOT 门**（同上下文可被同一盲点污染，甚至撤销自己已做对的纠正）；
  ② **独立 critic teammate**（全新上下文，`reviewer: critic @ <model> / <date>`）= **唯一放行门**（in-context critic skill 自审不算，与 Commit-discipline 一致）；
  ③ **CTO 常识合理性审** = 最后兜底（量级/方向/口径 sanity）。
- **不得假设"修过即对"。** 修正稿同等过三道关。lead 在派单 prompt 中对「修正/二次修正」任务**显式重申**此条。
- **缘起**：R8（synthesizer 撤销自家 verifier 已纠正的 21.7 MCPS 错下界）+ R9（STEER-2 「49x」修正稿自带 2.55x/3-cyc-MAC 两处偏乐观新错）。两案证明 workflow 自检不足，独立 critic + CTO 常识审是命门。
```

---

# 5. 一致性：STEERING_HEADROOM_SCAN.md 状态指针 + 两线隔离重申

## 5.1 顶部状态指针（在现有「时点注记」之后追加一行，正文逐字不动）

在文件顶部 `> 时点注记:...` 行之后追加：
```
> v1 路线注记 (2026-06-04): CTO 已裁 v1=聚焦/分区(DEC-S5-STEER-V1-01); 角度偏转转独立项(16ch 叉 ROI 待评). 优化排序 HW-1(IIR EQ)最高优先+item-3 PRD 同推(DEC-S5-OPT-ORDER-01). 口径采纳: 49x/340x 双作废(同源 1cyc/MAC 理想记账); 聚焦增量 86-144 MCPS[L4](30-50 cyc/MAC 板证包络), 聚焦后算法侧 margin 2.04-2.31x. 本报告 [L4/待验证] 估算不进选型基准, 须连体 §8 未计入清单呈现(DEC-S4-C9-RELEASE-01).
```

## 5.2 两线零交叉纪律重申（落 landing 包，不改报告正文）
- **算力/FIRA 线**（本包全部数字：347.45/463,273/86-144 MCPS/2.04-2.31x/cyc 等）与**声学/几何线**
  （d=55mm/栅瓣/聚焦疗效/AF 函数）**数字零交叉**：聚焦疗效 [L3/待 acoustic-sim] 不得用算力线数字背书，
  算力增量 [L4] 不得用声学结论背书。两线各自 provenance、各自门。
- 聚焦/分区 v1 成立 = **双线 AND**：算力侧可负担（本包，2.04x 最坏 [L4→待 harness L1]）AND 声学侧疗效
  确认（acoustic-sim teammate，[L3]→待仿真/实测）。任一未达 = v1 聚焦能力不成立，回 PRD。

---

# 6. 我无法从桌面核实
- decisions_log/POLICY/CLAUDE/team_config 精确当前行号（文件随提交漂移）；以锚字符串定位，lead apply 时复核。
- 聚焦增量 86-144 MCPS 的板上真值（[L4]，待 DEC-S5-OPT-ORDER-01 第 2 项 harness 升 L1）。
- 聚焦疗效（[L3]，待 acoustic-sim）。
- 无 SHARC/板：板锚（347.45/1e9/56,616）取 [L1]；桌面 MMAC（2.88/30.56）引 dsp_8ch_report.md:59-72；
  cyc/MAC 包络 30-50 = CTO 采纳的板证包络；算术 [L3]/[L4] 如标。
```
