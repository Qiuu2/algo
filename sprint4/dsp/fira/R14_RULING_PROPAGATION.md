# R14 三裁定 — decisions_log 条目 + 全库口径传播（iron-rule-5）DRAFT

> DRAFT ONLY. 不 commit；critic R7 先门。lead 过门后 apply + commit。
> 缘起：CTO 正式三裁定 2026-06-04（R14 CLOSED / >=10x 复议 / C9 RELEASED 附诚实分母）。
> 原则（CTO 令）：**历史按写时为真，保留逐字；活状态翻转；规则本身（条件于 R14）无须改写**。
> 引用全部 file:line。L 分级随附。

---

# (a) 三条 DEC 条目（供 lead 追加 `sprint2/docs/decisions_log.md`）

## A1. summary-table 追加行（接在 F7 cycle 行之后，C9 banner 之前）

```
| **R14 三裁定** | ✅ **R14 CLOSED + 判据复议 + C9 RELEASED（CTO 正式裁定 2026-06-04）** | 三条：DEC-S4-R14-RULING-01（R14 闭合，证据侧 §5 全绿，FIRA 2.878x 裕量/3.07x 加速 L1 坐实，bit-exact 逐位不变；8ch_core 复读=非阻塞尾巴）｜DEC-S4-CRITERION-01（>=10x 退役→「实时下限+余量政策」，临时下限 >=1.0x，正式阈值待 item-3 EQ链 PRD + WCET 实测）｜DEC-S4-C9-RELEASE-01（C9 松绑附诚实分母：FIRA 收益 [L1] 进选型但必须与 §8 未计入清单 43-379 MCPS 连体呈现；官方加速比锁 3.07x in-build；3.13x 混 build 禁入选型/对外）。详见下「R14 三裁定」节 + `sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md` |
```

## A2. C9 banner 行更新（decisions_log.md:630，LIVE — 翻转）

old:
```
> 🔒 **C9/铁律八维持**：FIRA 算力收益在 **R14 闭合前不进选型/裕量结论**。
```
new:
```
> 🔓 **C9/铁律八 RELEASED（2026-06-04，DEC-S4-C9-RELEASE-01）**：R14 已闭合（DEC-S4-R14-RULING-01），FIRA 算力收益现以 **[L1]** 进选型口径——**但必须与 §8 未计入清单（43-379 MCPS，整系统残余裕量 1.38-2.56x）连体呈现，不得单独以 2.878x 示人**。官方加速比锁 **3.07x（in-build A/B）**；**3.13x（混 build）禁入任何选型/对外材料**。（C9 守门历史：R14 闭合前持续生效，见下里程碑行逐字保留。）
```

## A3. F7 cycle 行状态尾注（decisions_log.md:629，LIVE 状态短语 → 追加，不改历史正文）

在该行开头状态短语 `✅ **板跑完成·R14 数据采集 COMPLETE·裁定待 CTO**（2026-06-04，DEC-S4-F7-CLOSE-01；...` 之后追加：
```
【裁定已下 2026-06-04：R14 CLOSED / 判据复议 / C9 RELEASED，DEC-S4-R14-RULING-01 / -CRITERION-01 / -C9-RELEASE-01】
```
（其余历史正文——判据 margin≥10× 等——逐字保留，因其记录的是 F7 当时口径；判据退役由 A6 注记。）

## A4. 详细节（追加到 decisions_log.md F7 节之后）

```
## R14 三裁定（2026-06-04，CTO 正式裁定；裁定权在 CTO，本节录裁定与依据）

### DEC-S4-R14-RULING-01：R14 主门 CLOSED
- **裁定**：R14 **CLOSED**。
- **依据（逐字 CTO）**：证据侧 §5 SATISFIED 全绿，FIRA offload 收益（2.878x 裕量、3.07x 加速）已坐实 L1，bit-exact 证明算法输出逐位不变。仅 8ch_core 复读为非阻塞尾巴。FIRA 把系统从纯软 0.92x（跑不动）救到能实时——R14 工程目标达成。
- **证据集 [L1/EZKIT 2026-06-04]**：F4 单通道子带 bit-exact（crc 0x2E0D8C6E）+ F5 8ch 逐位（g_f5_pass_all=1，8 锚命中）+ F7 含全开销 cycle（g_f7_cyc_8ch_fira=463,273）+ CCLK 实测（g_f7_cclk_hz=1e9，G6 CLOSED）→ 裕量 2.878x [L1-derived]、加速 3.07x [L1-derived]。
- **非阻塞尾巴**：g_f7_cyc_analyze_fira/synth_fira CCES Expressions 读 ERROR（疑符号名/读侧，数据在板上=1ch_fira 字面和证；不阻塞，待重读升 16ch 为 L1-derived）。
- **状态**：R14 **CLOSED**；下游 F4/F5/F7 里程碑行「R14 主门 OPEN/C9 维持」为写时历史，逐字保留并加「(R14 已闭合 2026-06-04 DEC-S4-R14-RULING-01)」尾注（A5）。

### DEC-S4-CRITERION-01：R1 算力判据 >=10x 退役 → 「实时下限 + 余量政策」
- **裁定**：>=10x **复议**，改「实时下限+余量政策」，**正式阈值暂不拍**。
- **依据（逐字 CTO）**：原 10x 基础（桌面 33×/17×）被板上推翻；但整系统残余 1.38-2.56x、EQ 最坏 ~1.0x，现在拍 >=2x 可能被 EQ 规格打穿。暂挂 **>=1.0x 实时底线为临时下限**；正式阈值等 item-3（EQ 链）PRD 钉死 + WCET 实测收窄后再定。
- **退役口径**：原 >=10x（出处 GRAFT_PLAN.md:28 / CCNT_source.md:47「写死」R1 判据，源自 dsp_8ch_report 桌面 33×/17× [L2] 投影）**退役**，不删，加注「retired-by-DEC-S4-CRITERION-01」。
- **临时下限**：>=1.0x 实时底线。残差范围（§8/ADDENDUM B）最坏 1.38x > 1.0x **在 item-3（EQ/mixing）≤150 MCPS 的 [L4] 包络下成立**；若产品加重型多频段 EQ+限幅链（板上 ~30 cyc/MAC 可达 ~250-290 MCPS，>150），最坏残差被拉向 ~1.0x。故 >=1.0x 系统级达成 **须待 item-3 PRD 钉死后方可无条件断言**（与 CTO 裁定二「EQ 最坏 ~1.0x」一致）。
- **待办（不阻塞）**：item-3 EQ 链 PRD 规格化 + WCET 实测（F7_WARM=0）收窄 → 定正式阈值。

### DEC-S4-C9-RELEASE-01：C9/铁律八 RELEASED（附诚实分母）
- **裁定**：C9 **RELEASED**，附诚实分母。
- **依据（逐字 CTO）**：FIRA 收益以 [L1] 进选型口径，但必须与 §8 未计入清单（43-379 MCPS）连体呈现，不得单独以 2.878x 示人（整系统残余 1.38-2.56x）。加速比官方值锁 3.07x（in-build）；3.13x 混 build 不进任何选型/对外材料。
- **松绑条件（强制连体）**：任何引 FIRA 收益（2.878x / 3.07x）的选型/对外材料，**必须同页并列** §8 未计入五项（codec/IO DMA 5-30、中断 2-15、EQ/mixing 0-150、控制 1-10、WCET +34.7-173.7 MCPS）+ 整系统残余裕量 **1.38-2.56x [L4]**。单独示 2.878x = 违裁定三。
- **加速比锁定**：官方 = **3.07x [L1-derived]**（in-build 1,420,543/463,273，同 build/输入/循环 A/B）。**3.13x（核-only 1,451,030/463,273）= 混 build 伪值，禁入选型/对外材料**（可作历史/异常留痕，见 F7_CLOSING_RECORDS）。
- **C9 守门历史**：R14 闭合前 C9 持续生效（六轮 critic 拦截、F4/F5/F7 全程 [L4/待验证]），该历史逐字保留；C9 现状 = RELEASED-with-denominator。

### 后续待办（不阻塞 R14 闭合）
1. item-3 EQ 链 PRD 规格化 → 定正式阈值（DEC-S4-CRITERION-01 悬项）。
2. WCET 实测（F7_WARM=0 冷 cache 帧 + DMA 并发）收窄 §8 item-5 → [L1]。
3. DMA/中断小 harness（Pipelined ADC→DAC passthrough）量 §8 item-1/2 → [L1]。
4. 非阻塞：重读 g_f7_cyc_analyze_fira/synth_fira（正确符号名）→ 16ch 约定估算升 [L1-derived]。
```

## A5. F4 / F5 里程碑行尾注（HISTORICAL — 加注，不改正文）

- decisions_log.md:626（F4 行）句末 `...全在上板前——详见 ... §12 实战记录）｜` 处的 **R14/C9 短语**「**R14 主门仍 OPEN、C9 维持、FIRA 收益 [L4/待验证] 不进选型；本结果≠R14 闭合**」与正文「**R14 仍 OPEN、C9 不松**」**逐字保留**（写时为真），在该行**末尾**追加尾注：
  ```
  〔R14 已闭合 2026-06-04，DEC-S4-R14-RULING-01；本行为 F4 里程碑写时口径，存史〕
  ```
- decisions_log.md:627（F5 行）同法，句中「**≠R14 闭合，C9 维持**」逐字保留，行末追加：
  ```
  〔R14 已闭合 2026-06-04，DEC-S4-R14-RULING-01；本行为 F5 里程碑写时口径，存史〕
  ```
- decisions_log.md:648（「状态：R14 未闭合... C9/铁律八维持」）= R14 假绿回退节的写时状态，**HISTORICAL，逐字保留**，行末追加同款尾注。

## A6. >=10x 判据写死处（decisions_log 内引）

decisions_log.md:634 等若有「裕量目标 ≥10×」写死引用 → 加注「(>=10x 已退役 2026-06-04 DEC-S4-CRITERION-01，改实时下限+余量政策)」。逐字保留原文。

---

# (b) 全库命中分类 + LIVE change blocks（iron-rule-5 反扫）

> 反扫范围：LIVE 树 `.md`（grep R14-OPEN / C9-维持 / [L4/待验证]-FIRA-收益 / >=10x-判据 / 标准 2.878x）。
> 分类：**HISTORICAL**（里程碑记录 / commit 引文 / 写时口径 — 保留逐字，可选尾注）vs **LIVE**（当前状态陈述 — 必须翻）。

## B1. LIVE — 必须更新（change blocks）

### LIVE-1：`sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md` §5 release-scope（条件句变实然）
本文 §5 通篇以「if the CTO rules R14 CLOSED」条件式写（锚字符串定位：`C9 RELEASE SCOPE if the CTO rules R14 CLOSED`；行号随版本漂移不引）。裁定已下 → 加实然顶注（不删条件正文，因其记录推理逻辑）。
插入 §5 开头：
```
> **STATUS UPDATE 2026-06-04: THE CTO HAS NOW RULED — R14 CLOSED (DEC-S4-R14-RULING-01), >=10x retired
>   -> realtime-floor+headroom, interim >=1.0x (DEC-S4-CRITERION-01), C9 RELEASED with the §8 honest
>   denominator (DEC-S4-C9-RELEASE-01). The conditional "if the CTO rules" language below is now ACTUAL.
>   Official speedup LOCKED 3.07x (in-build); 3.13x banned from selection/external material. Any citation
>   of 2.878x / 3.07x MUST appear paired with the §8 unaccounted list (43-379 MCPS, residual 1.38-2.56x).**
```
§5 :216 行 `**C9 RELEASE SCOPE if the CTO rules R14 CLOSED:**` → 改 `**C9 RELEASE SCOPE (NOW IN EFFECT, DEC-S4-C9-RELEASE-01):**`。

### LIVE-2：`sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md` §1B 2.878x 独立呈现（裁定三连体分母）
:41-42 `Margin: 1000/347.45 = 2.878x ... CONFIRMED` 与 §1C :51 `margin 2.878x is [L1-derived]` 为**算力侧裕量**陈述。裁定三要求任何 2.878x **连体未计入清单**。在 §1B 末追加：
```
> **DEC-S4-C9-RELEASE-01 PAIRING (mandatory): 2.878x is the ALGORITHM-CORE 8ch margin. It MUST NOT be
>   presented standalone. Paired denominator = §8 unaccounted items (43-379 MCPS) -> whole-system residual
>   margin 1.38-2.56x [L4]. Cite 2.878x only alongside that range.**
```
（§3a 已含未计入清单，但 §1B 是首次出现 2.878x 处，须就地挂钩。）

### LIVE-3：`sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md` §1A 加速比 3.07x（确认锁定 + 3.13x 禁令）
:30-33 已写 official 3.07x / 3.13x retired（本 teammate 上轮草案已并入）。追加裁定三禁令明文：
```
> **DEC-S4-C9-RELEASE-01: 3.07x is the LOCKED official speedup. 3.13x is BANNED from any selection /
>   external material (mixed-build artifact); it may appear ONLY in historical / anomaly-trail context.**
```

### LIVE-4：`sprint4/dsp/core_only/bench/GRAFT_PLAN.md:28`（写死 >=10x R1 判据 — LIVE 计划判据）
old:
```
- **R1 判据**（写死，实测待台架）：满负载 16ch WCET<1.333ms 且 裕量×=预算/实测MCPS≥10× 且 满 PF-1。
```
new:
```
- **R1 判据**（写死，实测待台架）：满负载 16ch WCET<1.333ms 且 裕量×=预算/实测MCPS≥10× 且 满 PF-1。
  〔注 2026-06-04：>=10x **已退役**（DEC-S4-CRITERION-01）——板上实测推翻桌面 33×/17×；改「实时下限+余量政策」，临时下限 >=1.0x，正式阈值待 item-3 EQ 链 PRD + WCET 实测。原文存史。〕
```

### LIVE-5：`sprint4/dsp/core_only/bench/CCNT_source.md:47`（写死 >=10x R1 闭合判据 — LIVE）
old:
```
**R1 闭合 ⇔ 16ch WCET<1.333ms 且 裕量×=预算/实测MCPS≥10× 且 满 PF-1**。标 [L1/EZKIT] 纯核。
```
new:
```
**R1 闭合 ⇔ 16ch WCET<1.333ms 且 裕量×=预算/实测MCPS≥10× 且 满 PF-1**。标 [L1/EZKIT] 纯核。
〔注 2026-06-04：>=10x **已退役**（DEC-S4-CRITERION-01），改「实时下限+余量政策」临时下限 >=1.0x；原文存史。R14/FIRA 侧裕量见 F7_R14_RULING_MATERIAL。〕
```

### LIVE-6：`sprint4/dsp/core_only/S0S1_report.md:57`（选型 margin >=10× 线 — LIVE 引用）
`(b) 裕量× ≥ 10×  —— 选型留 margin（参 dsp_8ch_report.md ≥10× 线）` → 行尾加注 `〔≥10× 已退役 2026-06-04 DEC-S4-CRITERION-01，改实时下限+余量〕`。

### LIVE-7：`sprint4/core_only_migration_plan.md:191/195/209`（>=10× R1 闭合判据 — LIVE 计划）
三处「裕量 ≥10×」R1 闭合引用 → 各加尾注 `〔≥10× 退役 DEC-S4-CRITERION-01 2026-06-04〕`。原文存史（这些是 core-only 路径计划，R1 仍可独立于 FIRA 论，但判据阈值已变）。

## B2. HISTORICAL — 保留逐字（可选尾注，不翻状态）

| 站点 | 内容 | 为何 HISTORICAL |
|---|---|---|
| `agents/critic/skill.md:1102` + `.claude/skills/critic/SKILL.md:1126` | §12 实战记录「...commit 9d9fbec，R14 主门仍 OPEN」 | **里程碑实战记录**，记的是 F4 当时（9d9fbec）状态；写时为真。可选行末尾注「(R14 已闭合 2026-06-04 DEC-S4-R14-RULING-01)」。 |
| `sprint4/dsp/fira/F4_BITEXACT_HANDOFF.md:12-13` | 「R14 主门仍 OPEN；C9/铁律八维持；FIRA 收益 [L4/待验证]」 | **F4 handoff 写时口径**。保留逐字 + 顶部加一行状态尾注（见 B3）。 |
| `sprint4/dsp/fira/F5_8CH_HANDOFF.md:11-12` | 「R14 主门仍 OPEN；C9/铁律八维持；... 最后裁定依据=F7」 | **F5 handoff 写时口径**。保留 + 顶部状态尾注（B3）。 |
| `sprint4/dsp/fira/F5_F7_PLAN.md:4` | 挂接「R14 主门 OPEN / C9·铁律八维持」 | **计划文档挂接行**，写时为真。可选尾注。 |
| `sprint4/dsp/fira/FIRA_IMPL.md:94/135` | F8「R14 PASS 后才实测 cycle...gating 于 F7」 | **实现计划写时序**（F8 现已被 F7 实测取代）。保留；可注「F7 已完成此项 2026-06-04」。 |
| `sprint4/dsp/fira/F3_F4_datapath_verified.md:51` | 「C9 维持」文末戳 | F3/F4 数据通路验证写时戳。保留逐字。 |
| `sprint4/core_only_migration_plan.md:211/248` | S7「不掺 FIRA（R14 维持）」+ 文末戳 | core-only 计划写时口径。保留。 |
| `sprint4/dsp/core_only/CROSS_BUILD_NOTES.md:86` | 文末「R14 维持，无 FIRA」 | cross-build 写时戳（core-only 范围声明）。保留逐字。 |
| `sprint3/audit/BENCH_OPS_CARD.md:7` | 红线「FIRA 收益均不混入（R14/铁律八维持）」 | bench ops 卡写时红线。保留；该卡是 R1 纯核操作纪律，FIRA 不混入仍是 core-only 量法的正确做法——**实质仍成立**（R1 纯核数不掺 FIRA），无须翻。 |
| `sprint3/audit/fira_fit_assessment.md:170/224` | 桌面 17×/33× 「远超 ≥10× 目标」 | **桌面 [L2] 评估历史**，已被板上推翻（decisions_log:234）。保留逐字（存史）；判据退役由 DEC-S4-CRITERION-01 全局注记覆盖。 |
| `sprint3/audit/A2_fib_feasibility.md:18` / `critic_a123_rv.md:81` / `A3_decision_recommendation.md:7` | FIB/A2「≥10× 守 19.1×」 | **Sprint3 FIB 可行性审计历史**（不同议题：FIB 而非 R14 cycle）。保留逐字。 |
| `sprint3_status.md:83` / `dsp_8ch_report.md:14/274` / `PREP-DSP-migration.md:70` / `L1_test_window_tasklist.md:28` / `NEXT_SESSION_BOOTSTRAP.md:56` | 桌面 33×/17× / ≥10× 关闭线（写时计划/状态） | **Sprint3 写时计划/状态**。多数是历史快照；其中 sprint3_status.md 若仍作活状态被读，建议 lead 加一行「R14 已闭合、判据已复议 2026-06-04」状态尾注（B3 候选），但正文 33×/17× 桌面值存史。 |
| decisions_log.md:626/627/648（F4/F5 里程碑 + 假绿回退节） | 「R14 OPEN/C9 维持」写时口径 | **里程碑记录**。A5 加尾注，正文逐字。 |
| F2 行 :625 / F3 行 :631 等 | 各阶段写时状态 | 历史。无须翻。 |

## B3. handoff/status 文档顶部状态尾注（HISTORICAL 正文 + 一行活状态指针）

**强制**：F4_BITEXACT_HANDOFF.md / F5_8CH_HANDOFF.md / F5_F7_PLAN.md 三个 handoff/plan 文档**必须**加顶部状态指针（critic R7 裁定：今日读者落到这些文档不得在无指针情况下误读 R14 仍开）。**可选**：sprint3_status.md。在文件**顶部**加一行（正文逐字不动）：
```
> **状态更新 2026-06-04：R14 已 CLOSED（DEC-S4-R14-RULING-01），>=10x 判据已退役→实时下限+余量（DEC-S4-CRITERION-01），C9 已 RELEASED 附诚实分母（DEC-S4-C9-RELEASE-01）。本文以下为写时口径，存史。**
```

## B4. 规则本身（CLAUDE.md / POLICY-PROV-001）— 核查结论：**无须改写**（CTO 假设证实）

- `CLAUDE.md:38`（C9 门）/ `:44`（铁律八）/ `POLICY-PROV-001 §4 铁律八 :106` / `§7 C9 :179` / `:252/:258` 全部是**条件规则**：「**R14 关闭前** FIRA 收益一律 [L4/待验证] 不进选型」。
- 该条件在 R14 **闭合后自动失效**（前件不再成立）——规则文本正确且永久有效（适用于任何未来 R-类不可逆闸门），**无须改一字**。改写反而会损坏规则的一般性。
- **结论：CLAUDE.md / POLICY-PROV-001 的 C9/铁律八 LIVE 规则文本 = 无变更。** 仅本案实例（R14）的状态翻转，在 decisions_log + 材料文档落字（上述 A/B1）。
- 同理 `agents/critic/skill.md` / `.claude/skills/critic/SKILL.md` 的 C9 门规则文本无须改；其 §12 **实战记录**（:1102/:1126）是历史叙述，B2 可选尾注。

## B5. iface_survey.md G6
G6 闭合 change block 已在 `F7_R14_RULING_MATERIAL.md §2` 备好（CCLK=1e9 [L1]，G6 CLOSED）。本传播不重复；提示 lead 同批 apply。

---

# (c) 一致性守卫（裁定三）：2.878x 独立呈现核查

扫 `2.878 / 2.88x` 全库命中：
- `F7_R14_RULING_MATERIAL.md` §1B :41-42 / §1C :51 — **首次独立呈现处**，LIVE-2 已挂连体分母注。
- `F7_R14_RULING_MATERIAL.md` §3a — 已含未计入清单（连体在场）。✓
- `F7_CLOSING_RECORDS.md:45`（"the 8ch margin (2.878x), the speedup..., the 2.23% fixed-share are all L1-derived"）— **非独立销售呈现**（在 Q1 内文列举，非对外裕量结论），且 :162 中文版「8ch 实时裕量=2.878x [L1-derived]」紧随 §8 未计入引用脉络。判定 HISTORICAL/内部分析，**可选**加一行指针「对外引用须连体 §8（DEC-S4-C9-RELEASE-01）」，不强制改正文。
- `F7_MARGIN_MATERIAL.md`（v1 core-only）— 全文是 0.92x core-only，**无 FIRA 2.878x 独立销售**；其 §0 顶注已声明「MATERIAL ONLY，不决 R14」。无需改（历史 v1 记录）。
- 结论：唯一须就地挂分母的 LIVE 销售呈现 = `F7_R14_RULING_MATERIAL.md §1B`（LIVE-2 覆盖）。其余为分析/历史脉络。

---

# 未触历史清单（保留逐字，理由）
- 所有 commit message / git note（e338288 / 593d764 / bbcf1fc 等）— 不可改，是 git 历史。
- decisions_log F2/F3/F4/F5 里程碑行正文、R14 假绿回退节、桌面 33×/17× 评估节 — 写时为真，A5/A6 仅加尾注。
- critic skill §12 实战记录 — 历史叙述。
- sprint3/audit/* FIB 与桌面裕量审计 — 不同议题 / 桌面历史。
- CLAUDE.md / POLICY / critic skill 的 C9/铁律八**规则文本** — 条件规则，R14 闭合后自失效，永久正确，B4 证实无须改。

---

# 我无法从桌面核实
- decisions_log 精确当前行号（文件随提交漂移）；以锚字符串定位，lead apply 时按当前行复核。
- analyze/synth 重读结果（板上全局）— 非阻塞尾巴，16ch 升级待之。
- 无 SHARC 工具链/板：板值取 CTO [L1/EZKIT]；本传播为文档口径作业，引用 file:line + 锚字符串。
