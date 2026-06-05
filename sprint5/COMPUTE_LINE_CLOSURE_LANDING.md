# 算力线收官 — 双槌落地 + 铁律五全库传播 DRAFT（不 commit；critic R18 先门）

> 缘起：CTO 双槌裁定 2026-06-05（槌一 DEC-S5 预算修正确认；槌二 DEC-S4-CRITERION-01 正式阈值=T2 带闭合条件）。
> 裁定 substance 逐字采纳。原则：历史按写时为真（保留逐字+加注）；活状态翻转；引用 file:line + 锚字符串。
> 算术 python 双核（§此处全绿）。三道关自指：关①已过；关② critic R18（待）；关③ CTO。

---

# 1. decisions_log 条目

## 1.1 summary-table 追加行

```
| **DEC-S5 预算修正 [L1]** | ✅ **focus 86-144[L4] → 49.03 MCPS [L1/EZKIT]；整系统残余 1.46-2.14x**（DEC-S5-BUDGET-L1-01，2026-06-05）| H1 v2 板跑（FG 双门过 focus_differs=1/zero_recovers=1，R15 snapshot 板证）focus_only=65,371 cyc → 49.03 MCPS [L1-derived]（×750/1e6）；cyc/MAC=8.51（@7,680 MAC=8tap×120samp×8ch，源 sz[]）；可复现（prior 65,410 差 39 cyc=0.060%）。残差超越链闭合：1.38-2.56→1.28-1.98→1.08-1.69→**1.46-2.14x [L4]**（L1 focus 抬两端）。MAC-2x 收口：cycle 分不出 120 vs 60 MAC 基准（8.51 vs 17.02 cyc/MAC 均可能），120 由源码 sz[] 定非 cycle 反推=诚实极限入档；86-144(误 2.88)/173-288(对 5.76 但错 cyc/MAC 类)双退役，实测优于双估。详见「DEC-S5 预算修正」节 + sprint5/H1_FINAL_RULING_MATERIAL.md |
| **正式阈值 = T2** | ✅ **DEC-S4-CRITERION-01 FINAL = >=1.5x（T2）带闭合条件**（DEC-S4-CRITERION-01-FINAL，2026-06-05）| 现状 best 2.14x 达标 / worst 1.46x 差 2.7% 未达系统级 → 状态标「**算法-best 侧 ≥1.5x 达标（产品级锚=整系统 best 2.14x，纯算法 2.52x[L1] 为 L1 锚非产品级）/ 系统-worst 侧 1.46x 待 harness 闭合 [L4]**」。闭合路径=派 DMA/ISR small harness 实测收窄 WCET +10-50% 保守项，目标 worst 端抬过 1.5x（WO-S5-H2）。不选 T1（1.0x 边际过薄，对未含 EQ/DMA/ISR/未来功能无成长空间）；不选 T3（>=2x 纯核不达需押 HW-1，HW-1 暂可选不为达阈强行上，T2 闭合后再评 2x）。CLOSES 判据项（>=10x 退役→实时+余量→临时 1.0x→今 FINAL T2）。残余风险册认可。详见「正式阈值 T2」节 |
| **WO-S5-H2 登记** | 🟡 **DMA/ISR small harness（T2 闭合路径，待 CTO 排期）**（2026-06-05）| 测 §8 item-1（codec/IO DMA 5-30）+ item-2（中断 2-15）+ 收窄 WCET 未测保守项（I-cold 仍 C10 待）。EZKIT passthrough + ISR-load harness（scope sketch only，未实现）。CTO 排期。是 DEC-S4-CRITERION-01-FINAL 的系统侧闭合钥匙 |
| **H1 FG-BLOCKER** | ✅ **CLOSED（R15 板证 + R16 build 修 + v2 全绿）**（2026-06-05）| 〔状态更新〕R14 zero_recovers=0（ST1 自检缺陷）→ R15 snapshot/restore 修 → R16 declare-before-use build 修 + guard-stub 检查 → v2 板跑 FG 双门过（1/1）数据 BOOKED [L1]。episode 闭环 |
```

## 1.2 详细节（追加到 decisions_log 末）

```
## 算力线收官双槌（2026-06-05，CTO 正式裁定）

### DEC-S5-BUDGET-L1-01：DEC-S5 聚焦预算 86-144[L4] → 49.03 MCPS [L1/EZKIT]（槌一）
- **裁定（substance 逐字）**：focus 86-144[L4] → 49.03 MCPS [L1/EZKIT]；整系统残余更新 1.46-2.14x。
  MAC-2x 收口认可（cycle 分不出两种 MAC 基准，120 样本源码定，86-144/173-288 双退役，实测优于双估，诚实极限入档）。
- **L1 数据**：H1 v2 板跑 [L1/EZKIT 2026-06-05]，focus_only=65,371 cyc/frame → **49.03 MCPS**（×750/1e6）；
  cyc/MAC=**8.51**（@真 7,680 MAC/frame=8tap×120samp×8ch）；可复现（prior quarantined 65,410，差 39 cyc=0.060%）。
- **MAC-2x 收口（诚实极限）**：真 MAC=120 samp/frame（sb0/8+sb1/16+sb2/32+sb3/64，sb3 未抽取，源 fira_regression.c:193（+ harness sz[]））。
  **cycle 数本身分不出 120 vs 60**（65,371/7,680=8.51 或 /3,840=17.02 cyc/MAC 均算术可能）→ 120 由**源码 sz[]**
  定，非 cycle 反推；此诚实极限入档（避循环论证）。86-144（误设 2.88 基准）/173-288（对 5.76 基准但 30-50 cyc/MAC
  是 FIRA-编排类、非本 flat-FIR 核类=保守）**双退役**；49.03 [L1] 为账面值（kernel 类对=8.51 cyc/MAC 解释好方向）。
- **残差超越链闭合**：1.38-2.56（no-focus,EQ0-150）→1.28-1.98（focus86-144）→1.08-1.69（focus173-288）→
  **1.46-2.14x [L4]**（best=1000/(347.45+49.03+29+5+2+1+34.7)=2.14x；worst=1000/(347.45+49.03+60+30+15+10+173.7)=1.46x）。
- **状态**：聚焦预算 [L1] 入账；残余 1.46-2.14x（连体 §8，DEC-S4-C9-RELEASE-01）。

### DEC-S4-CRITERION-01-FINAL：正式阈值 = T2（>=1.5x）带闭合条件（槌二）
- **裁定（substance 逐字）**：正式阈值=T2（>=1.5x）。现状 best 2.14x 达标 / worst 1.46x 差 2.7% 未达系统级；
  闭合路径=派 DMA/ISR small harness 实测收窄 WCET +10-50% 保守项，目标把 worst 端抬过 1.5x；实测闭合前阈值状态
  标「算法-best 侧 ≥1.5x 达标（产品级锚=整系统 best 2.14x；纯算法 2.52x[L1] 锚非产品级）/ 系统-worst 侧待 harness 闭合 [L4]」。不选 T1（1.0x 边际过薄，对未含 EQ/DMA/ISR/未来功能无成长空间）；
  不选 T3（>=2x 纯核不达需押 HW-1，HW-1 暂可选不为达阈强行上，T2 闭合后仍要争 2x 再评）。残余风险册认可。算力线收官归档。
- **CLOSES 判据项**：>=10x（DEC-S4-CRITERION-01，桌面 33×/17× 推翻）退役 → 实时下限+余量政策 → 临时下限 >=1.0x
  → **FINAL = T2 >=1.5x（本条）**。判据演进链闭合。
- **达标账（python 双核，critic R18 F18-MAJOR-1 口径修正）**：CTO 裁定依据 = **整系统 best 2.14x ≥ 1.5x 达标**（含 O1-low/io/irq/ctl/WCET-low [L4]）/ worst 1.46x 差 2.7% 未达系统级。另记 **纯算法侧（核+focus=347.45+49.03=396.5 MCPS，不含 O1 EQ）= 2.52x [L1]** 作 L1-grade 锚——注：**2.52x 排除了 v1 必需的 O1 EQ，非产品级口径；产品级达标看 best 2.14x**；
  系统侧（含 §8 全项）= **1.46-2.14x [L4]**，worst 1.46x 距 1.5x 差 0.041=2.7%（未达系统级）。
- **状态**：T2 FORMAL；状态标「**算法-best 侧 ≥1.5x 达标**[含 best 2.14x[L4-含L1主项] + 纯算法 2.52x[L1]，产品级达标锚=2.14x] / **系统-worst 侧** 1.46x 待 WO-S5-H2 闭合[L4]」。

### WO-S5-H2（登记，未实现）：DMA/ISR small harness = T2 系统侧闭合路径
- **目标**：实测 §8 item-1（codec/IO DMA，5-30 MCPS [L3]）+ item-2（中断，2-15 [L3]）→ 收窄 WCET 未测保守项
  （I-cache cold 仍 C10 待，符号未知）。把 worst 端从 1.46x 抬过 1.5x（T2 系统侧闭合）。
- **scope sketch（only）**：EZKIT 上跑 Pipelined ADC→DAC passthrough（量 DMA 回调+缓冲服务 core cyc）+ ISR-load
  （量帧 ISR cadence×cost）。F7/H1 同流程（dsp code→三道关→CTO+C10→板跑）。**未实现，CTO 排期。**
- **状态**：登记；CTO 排期；DEC-S4-CRITERION-01-FINAL 系统侧闭合钥匙。
```

---

# 2. 铁律五全库传播（活状态翻转 + 历史逐字保留+加注）

## 2.1 LIVE — 必须翻（change blocks）

### LIVE-1：`sprint2/docs/prd_update.md` §3.4 算力账（residual 1.28-1.98 + 1.0x 底线 + 待 WCET → 翻 T2）
old（:206 算力账 blockquote）:
```
> 算力账：item-3=O1 锁定 29–60 MCPS [L4]；聚焦后整系统残余 margin **1.28x–1.98x [L4]**（连体 §8 未计入清单
>   呈现，DEC-S4-C9-RELEASE-01）；守 ≥1.0x 实时底线，正式阈值待 WCET 实测（DEC-S4-CRITERION-01）。
```
new:
```
> 算力账（DEC-S5-BUDGET-L1-01 / DEC-S4-CRITERION-01-FINAL 2026-06-05 更新）：focus 增量实测 **49.03 MCPS
>   [L1/EZKIT]**（H1 v2 板跑，超越旧 86-144 估）；item-3=O1 29–60 MCPS [L4]；聚焦后整系统残余 margin
>   **1.46x–2.14x [L4]**（连体 §8 未计入清单，DEC-S4-C9-RELEASE-01）。**正式阈值 = T2（≥1.5x）**：算法侧
>   达标锚 = 整系统 best 2.14x（产品级，含 O1）；纯算法侧 2.52x [L1]（不含 O1 EQ，非产品级口径）；系统侧 worst 1.46x 待 DMA/ISR harness（WO-S5-H2）收窄 WCET 闭合 [L4]。
```

### LIVE-2：`sprint5/V1_NARROWING_LANDING.md`（多处 86-144 / 1.28-1.98 / 2.04-2.31 / 正式阈值待 WCET）
该文是 v1 收窄落地稿（已 commit）。**正文写时为真逐字保留**，在文件**顶部**加一行活状态指针：
```
> **状态更新 2026-06-05（DEC-S5-BUDGET-L1-01 / -CRITERION-01-FINAL）**：focus 增量已实测 **49.03 MCPS [L1]**
>   （本文 86-144[L4]/173-288 估值均退役，实测更优）；整系统残余 **1.46-2.14x [L4]**（取代本文 1.28-1.98）；
>   正式阈值 = **T2 ≥1.5x**（算法侧达标[L1]/系统侧待 WO-S5-H2 闭合[L4]）；本文以下为写时口径，存史。
```
（§2.3/§4.2 内 1.28-1.98 / >=1.0x 临时下限 / 正式阈值待 WCET 等行**不改正文**，由顶注覆盖活状态。）

### LIVE-3：`sprint5/eq_prd/EQ_PRD_DECISION_MATERIAL.md` 顶（1.28-1.98 裁定注 → 加 L1 更新）
现 :3 裁定注记含「整系统残余 1.28x–1.98x [L4]」。在其后追加一行：
```
> 更新 2026-06-05（DEC-S5-BUDGET-L1-01）：focus 实测 49.03 MCPS [L1]→整系统残余 **1.46-2.14x [L4]**（取代 1.28-1.98）；
>   正式阈值 T2 ≥1.5x（DEC-S4-CRITERION-01-FINAL；算法侧达标[L1]/系统侧待 WO-S5-H2[L4]）。O1 系统 margin 口径同步。
```
（§2/§4 选项表的 1.28-1.98 历史推导**保留**，顶注覆盖。）

### LIVE-4：`sprint5/steering_scan/STEERING_HEADROOM_SCAN.md` 顶（v1 收窄注 1.28-1.98 → 加闭合注）
现顶有「v1 收窄注记…整系统残余 1.28x–1.98x」。追加一行：
```
> 算力线收官注 2026-06-05：focus 实测 49.03 MCPS [L1]→残余 **1.46-2.14x [L4]**；正式阈值 **T2 ≥1.5x**（算法侧
>   达标[L1]/系统侧待 WO-S5-H2 DMA/ISR harness 闭合[L4]）。86-144/173-288/1.28-1.98 均退役。DEC-S5-BUDGET-L1-01/-CRITERION-01-FINAL。
```

### LIVE-5：`sprint5/steering_scan/V1_ROUTING_LANDING.md` 顶（86-144 / 2.04-2.31 散布 → 顶注覆盖）
正文写时为真逐字保留，顶部（现 v1 路线注记 :175 处）后加一行：
```
> 算力线收官 2026-06-05：focus 实测 49.03 MCPS [L1]（本文 86-144[L4] 退役）；算法侧 margin 由 2.04-2.31 升
>   实测口径，整系统残余 1.46-2.14x[L4]；正式阈值 T2 ≥1.5x。DEC-S5-BUDGET-L1-01/-CRITERION-01-FINAL。本文以下存史。
```

### LIVE-6：`sprint5/NEXT_SESSION_BOOTSTRAP_H1.md`（H1 待跑指引 → 已跑闭合）
该文是 H1 板跑前指引（173-288 yardstick / 1.0× 临时下限刀刃口径 = 写时待跑态）。顶部加：
```
> 收官 2026-06-05：H1 v2 已板跑全绿 [L1]，focus_only=49.03 MCPS（本文 173-288 yardstick 已 settle，实测更优）；
>   残余 1.46-2.14x[L4]；正式阈值 T2 ≥1.5x（算法侧达标[L1]/系统侧待 WO-S5-H2[L4]）；1.0× 刀刃口径作废（实测非刀刃）。
>   本文以下为板跑前指引，存史。DEC-S5-BUDGET-L1-01/-CRITERION-01-FINAL。
```

## 2.2 HISTORICAL — 逐字保留 + 加注（不翻状态）

| 站点 | 内容 | 处理 |
|---|---|---|
| decisions_log:706（R14 三裁定行，含「临时下限 >=1.0x，正式阈值待 item-3+WCET」） | R14 写时口径 | 逐字保留；行末加注 `〔正式阈值已定 T2 ≥1.5x，2026-06-05 DEC-S4-CRITERION-01-FINAL；临时下限 1.0x 被 T2 取代〕` |
| decisions_log:773-777（DEC-S4-CRITERION-01 详节，「正式阈值暂不拍/临时下限 >=1.0x」） | 判据复议写时态 | 逐字保留；节末加注 `〔FINAL 2026-06-05：正式阈值 = T2 ≥1.5x 带闭合条件，DEC-S4-CRITERION-01-FINAL；本节为复议阶段口径，存史〕` |
| decisions_log:710（DEC-S5-OPT-ORDER-02，86-144→L1） | 执行序写时（86-144 待 L1） | 逐字保留；加注 `〔focus 已实测 49.03 MCPS[L1]，DEC-S5-BUDGET-L1-01；86-144 退役〕` |
| decisions_log:711（H1 FG-BLOCKER→R15 行，173-288/quarantined 65,410） | R15 写时态 | 逐字保留；加注 `〔R16 build 修 + v2 板跑全绿，FG 双门过，focus_only=65,371 BOOKED[L1]=49.03 MCPS；173-288 退役（kernel 类对=8.51 cyc/MAC）；FG-BLOCKER CLOSED 2026-06-05〕` |
| `sprint5/H1_WCET_WORKORDER.md`（173-288 yardstick，写时校正态） | WO 写时（待板） | 逐字保留；加注顶部 `〔H1 v2 已板跑：focus_only=49.03 MCPS[L1]，173-288 yardstick settle，实测 8.51 cyc/MAC<30-50 类；DEC-S5-BUDGET-L1-01〕` |
| `sprint5/H1_R15_FIX_PACKAGE.md` / `H1_R16_BUILDFIX_NOTE.md` / `H1_FINAL_RULING_MATERIAL.md` | R15/R16/最终材料 | **逐字保留**（过程留痕，本就是收官链证据）；无需翻（H1_FINAL 已是 L1 口径） |
| `sprint4/dsp/fira/F7_*` / `F4/F5 handoff` | F0-F7 写时里程碑 | 逐字保留（R14 三裁定时已加状态尾注，本轮无新动作） |
| CLAUDE.md / POLICY-PROV-001 C9/铁律八 **规则文本** | 条件规则 | **无须改**（条件规则 R14 闭合后自失效，永久正确；本双槌不涉规则文本，仅实例状态） |

## 2.3 grep 分类总表（R7 传播纪律）
- LIVE「86-144」：V1_NARROWING(顶注覆盖)/V1_ROUTING(顶注)/EQ_PRD(顶注)/NEXT_SESSION(顶注)/prd_update §3.4(LIVE-1 直翻)/
  H1_WCET_WORKORDER(已 173-288，HISTORICAL 加注)。**正文逐字保留，顶注/LIVE-1 翻活状态。**
- LIVE「1.28-1.98」：V1_NARROWING/EQ_PRD/STEERING/prd_update — 同上（prd_update LIVE-1 直翻；余顶注）。
- LIVE「临时下限/正式阈值待 WCET」：decisions_log:706/773-777（HISTORICAL 加注 T2-FINAL）/V1_NARROWING(顶注)/
  prd_update(LIVE-1 直翻)。R15/NEXT_SESSION 的「1.0x 刀刃」=写时待板态，顶注作废刀刃口径。
- 原则：**任何「当前状态」陈述翻 T2/49.03/1.46-2.14；任何「写时记录/里程碑/推导」逐字保留+加注。**

---

# 3. 算力线收官 summary（归档）

## 3.1 全链 F0 → 收官
```
F0 (core-only bit-exact crc 0x90556BC7 [L1]) → F2/F3 (FIRA 管路+真系数) → F4 (单通道子带 bit-exact 0x2E0D8C6E)
→ F5 (8ch 逐位 8/8) → F7 (含开销 cycle 463,273 + CCLK 1e9 实测/G6 闭) → R14 三裁定 (CLOSED / 判据复议 / C9 松绑)
→ v1 (聚焦/分区收窄 2-5m≥4kHz, 车站 zoning 剔除 / EQ=O1) → H1 (focus 49.03 + WCET, R14→R15→R16→v2 全绿)
→ 收官双槌 (DEC-S5 预算 L1 / 正式阈值 T2)
```

## 3.2 critic 轮次（17 轮 + R18 本轮）
R8(synth 撤 verifier)/R9(STEER-2 49x 修正稿带新错)/R10(v1 路线)/R11(EQ master-bus 修正)/R13(双裁定落地)/
R14(H1 包)/R15(H1 ST1 修)/R16(H1 build 修+guard-stub)/R17(H1 最终材料)/**R18(本收官包，待)**。+ R14 前 F4/F5/F7 多轮。

## 3.3 固化的教训（制度）
- **POLICY v1.8 §4B 三道关**（auto-verify→独立 critic→CTO 常识审，不假设修过即对；缘起 R8/R9）。
- **critic §12 ST1-E**（裁「无害」须枚举所有消费者逐项裁；缘起 R14/R15 H1 跨态自检）。
- **guard-stub 检查**（TARGET-guarded 代码桌面 gcc 失明，必带宏+mock 真编译；缘起 R16 declare-before-use）。
- **harness probe/态隔离**（自检 probe 与测量 span 不共享可变态或须 snapshot/restore；省内存非充分理由）。
- **不偏不倚 R5/R7/R13**（修正稿自带新错；数字两方向都不偏，WCET 不向下塌也不向上夸）。

## 3.4 官方数字表（连体 §8 分母，DEC-S4-C9-RELEASE-01）
| 量 | 值 | grade | 出处 |
|---|---|---|---|
| 官方加速比 | **3.07x**（in-build A/B；3.13x 混 build 禁） | [L1-derived] | DEC-S4-C9-RELEASE-01 |
| 8ch 算法侧 margin（无 focus/EQ） | 2.878x | [L1-derived] | F7_R14_RULING_MATERIAL |
| focus 增量 | **49.03 MCPS**（65,371 cyc, 8.51 cyc/MAC） | [L1/EZKIT] | DEC-S5-BUDGET-L1-01 |
| 纯算法侧 margin（核+focus，**不含 v1 必需 O1 EQ，非产品级口径**；产品级达标锚=整系统 best 2.14x） | 2.52x | [L1-derived] | 本包 §1.2 |
| 正式阈值 | **T2 ≥1.5x**（带闭合条件） | 裁定 | DEC-S4-CRITERION-01-FINAL |
| 整系统残余 margin | **1.46-2.14x**（连体 §8 未计入 43-379 MCPS） | [L4] | 本包 §3 |
| WCET（实测部分） | +0.02x（cold-DATA+jitter） | [L1] | H1_FINAL_RULING §2 |
| CCLK | 1.0e9 Hz（G6 闭） | [L1/EZKIT] | F7 |
> **C9 纪律**：以上 [L1] 数进选型/对外**须连体 §8 未计入清单**（残余 1.46-2.14x），不单独示 49.03/2.52x/2.878x。

---


### 3.3b 门禁实战记录（critic R18 F18-MINOR-1 补全，诚实记录）
本线两次缺陷逃逸了独立 critic 门、由下游门兜住——R14 的 ST1 跨态自检缺陷被**板跑**捕获（critic R14 PASS 了它）；R15 的 declare-before-use build 错被**CTO 的 CCES 编译**捕获（critic R15 + dsp gate-① 均 PASS，桌面 gcc 对 guarded 区失明）。三道关有效**正因为**下游门（板/CTO）兜住了 critic 门漏的——这才是 R14/R15 的真教训，不是「critic 零漏」。

# 4. 收官后 remaining-open register

| # | 项 | grade | 闭合路径 |
|---|---|---|---|
| 1 | **WO-S5-H2 DMA/ISR harness**（T2 系统侧闭合） | [L3]→[L1] | EZKIT passthrough+ISR-load；worst 抬过 1.5x；CTO 排期 |
| 2 | **I-cache cold WCET** | [L3/L4] | C10 板项，SHARC I-cache invalidate 符号 TBD（桌面未知） |
| 3 | **O1 EQ 板成本** | [L4] | 板测 2-3 biquad+限幅 → [L1] |
| 4 | **R3 消声室**（X dB 验收 + EQ band 数 + efficacy） | [L2]→[L1] | T/S 2-4 周 + 消声室+现场实测；X=PRD OPEN |
| 5 | **HW-1 IIR offload** | 可选 [L4] | T2 闭合后若争 ≥2x 再评（不为达阈强上） |
| 6 | **角度偏转 ROI** | 独立项 | 16ch 硬件叉 + SC-S3-GEOM-01 d 重议，CTO 后评 |

---

# 5. 桌面验证（算术 python 双核，全绿）
- focus 65,371×750/1e6=**49.03 MCPS**；65,371/7,680=**8.51 cyc/MAC**；复现 65,410-65,371=39 cyc（0.060%）。
- 残差链 best=1000/468.2=**2.136x**；worst=1000/685.2=**1.459x**；worst 距 1.5x 差 0.041=**2.7%**。
- 算法侧（核+focus）1000/(347.45+49.03)=1000/396.48=**2.52x**。
- MAC 歧义：65,371/7,680=8.51 vs 65,371/3,840=17.02（均可能，cycle 分不出，源 sz[] 定 120）。

# 6. 无法从桌面核实
- WO-S5-H2 的 DMA/ISR 实测（待板 [L1]）；I-cache cold 符号（C10）；O1 板成本（[L4]）；R3 efficacy（[L2]→板）。
- decisions_log/PRD/sprint5 精确行号（随提交漂移；锚字符串定位，lead apply 复核）。
- 无 SHARC/板：板锚（49.03/1e9/347.45 [L1]）取 CTO 实测；MAC/sz[] 源码；算术 [L1-derived]/[L3]/[L4] 如标。
