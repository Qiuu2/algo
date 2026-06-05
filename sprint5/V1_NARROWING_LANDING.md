# v1 收窄 + EQ=O1 双裁定 — 落地包 DRAFT（不 commit；critic R13 = 三道关之②，过后 CTO 三道关之③确认）

> **状态更新 2026-06-05（DEC-S5-BUDGET-L1-01 / -CRITERION-01-FINAL）**：focus 增量已实测 **49.03 MCPS [L1]**
>   （本文 86-144[L4]/173-288 估值均退役，实测更优）；整系统残余 **1.46-2.14x [L4]**（取代本文 1.28-1.98）；
>   正式阈值 = **T2 ≥1.5x**（算法侧达标[L1]/系统侧待 WO-S5-H2 闭合[L4]）；本文以下为写时口径，存史。

> 缘起：CTO 双裁定 2026-06-05「走(a) v1 收窄为近场高频展区分区, EQ 取 O1; 请落档」。
> 裁定 substance 逐字采纳。原则：历史按写时为真；活路线/规格落 decisions_log + PRD；引用 file:line。
> 两线数字零交叉纪律不变（算力/FIRA 线 vs 声学/几何线）。
> **三道关自指**：本落地包自身是修正/裁定落地的 workflow 产出 → 走 critic R13（关②）+ CTO 确认（关③）；不假设「写了即对」。

---

# 1. decisions_log 条目

## 1.1 summary-table 追加行

```
| **v1 范围收窄** | ✅ **v1=近场高频展区分区（2–5m, 有用带 ≥4kHz）；车站 zoning 剔除（broadside 定向保留）；PRD 重写**（DEC-S5-V1-SCOPE-01，2026-06-05）| 走 FOCUS_EFFICACY 选项(a)：聚焦效能仅在高频近距物理真实（4k/6k@2–3m 焦点增益 4.85–8.09dB、聚焦超额最高 3.9dB；语音主带 0.3–3kHz 近乎为空；车站 12–15m 宽带物理为空，efficacy_sim §3 [L2/仿真]）。双线 AND **对收窄范围 SATISFIED**（算力 [L4] AND 声学 CTO 裁为「足够-for-收窄范围」）。验收指标 = **PRD OPEN ITEM**：「高频近场净隔离 ≥ X dB @ 消声室 L1」，X 待 CTO/PRD 定（不臆造）。详见「v1 收窄」节 |
| **item-3 = O1** | ✅ **EQ 取 O1（LEAN master-bus 2–3 biquad 整形 EQ + 保护限幅器 REQUIRED）**（DEC-S5-EQ-O1-01，2026-06-05）| O1 成本 **29–60 MCPS [L4]**（20–25 MAC/samp×48k×{30,50}cyc/MAC）；整形 EQ→master-bus（broadside 同信号 + LTI 可交换双基础，约 1/8 成本）；**保护限幅器 REQUIRED 入 PRD**（per-channel，阈值按权重缩放 T_k=T·w_k，D14 防锥度劣化）；band 数终调待 R3 消声室正轴向响应；功放选型 caveat（TAS5825M 会把 EQ 账外置）。详见「item-3 O1」节 |
```

## 1.2 详细节（追加到 decisions_log 末）

```
## v1 收窄 + EQ=O1 双裁定（2026-06-05，CTO 正式裁定；本节录裁定与依据）

### DEC-S5-V1-SCOPE-01：v1 = 近场高频展区分区；车站 zoning 剔除；PRD 重写
- **裁定（substance 逐字）**：走 (a)，v1 收窄为近场高频展区分区。
- **范围定义**：v1 zoning 能力 = **近场高频展区分区，工作距离 2–5m，有用频段 ≥4kHz**（博物馆/商场近端展区）。
  **车站广播场景的 zoning 能力剔除**——车站保留 broadside 定向音柱产品角色（指向性产品不变），**不承诺深度分区**。
- **物理依据 [L2/仿真，efficacy_sim FOCUS_EFFICACY_REPORT.md]**：
  - 聚焦效能由近场瑞利极限 R=2L²/λ 严格门控；可观焦点增益（4.85–8.09dB）+ 净聚焦超额（最高 3.9dB）
    仅在 **高频(4k/6k)+近距(2–3m)**（efficacy §2/§3）。
  - 语音主能量带 0.3–3kHz：全距离焦点增益/聚焦超额都很小（频带错配，efficacy:118）。
  - 车站 5–15m 宽带：12–15m 远超绝大多数频段瑞利极限，深度分区**物理为空**（efficacy:116/139）→ 剔除正确。
- **双线 AND（收窄范围）= SATISFIED**：
  - 算力侧：聚焦增量 86–144 MCPS [L4]，聚焦后算法侧 margin 2.04–2.31x [L4]（DEC-S5-STEER-V1-01）。
  - 声学侧：CTO 裁「足够-for-收窄范围」（高频近距 efficacy 真实，剔除物理不达标的车站宽带 zoning）。
  - **注**：efficacy 全为 [L2/仿真]，无 L1；点声源各向同性、自由场（无混响）= 高估隔离（efficacy:124/125）。
    **L2→L1 缺口**：任何进选型/承诺/PRD 的聚焦效能数字须消声室+现场实测升 L1（efficacy:129）。
- **PRD 重写 mandated**：v1 能力定义、场景表（车站 zoning 剔除）、新增验收指标占位（见 §3 PRD change blocks）。
- **验收指标 = PRD OPEN ITEM（不臆造 X）**：建议口径「**高频近场净隔离 ≥ X dB @ 消声室 L1**」（扣除 1/r 几何扩散后
  只认聚焦净贡献，efficacy:140 归因纪律）。**X 由 CTO/PRD 定**；efficacy 自由场上界参考 ~3.9dB@6k 近距（混响后更低）。
- **状态**：v1=近场高频展区分区锁定；车站 zoning 剔除；角度偏转仍独立项（DEC-S5-STEER-V1-01）。

### DEC-S5-EQ-O1-01：item-3 = O1（LEAN master-bus EQ + 保护限幅 REQUIRED）
- **裁定（substance 逐字）**：EQ 取 O1。
- **O1 规格（EQ_PRD_DECISION_MATERIAL.md:69 + §2.2 结构规则）**：
  - **整形 EQ**：2–3 biquad，**master-bus（fan-out 前一次处理）**。基础 = broadside 同信号 + 整形 EQ/per-ch 延迟
    均 LTI 可交换（master-bus EQ→fan-out→per-ch 延迟 ≡ per-ch EQ→延迟，频谱整形等价），broadside 与聚焦下
    均成立、约 1/8 成本（EQ_PRD §2.2:50/52）。
  - **保护限幅器 = REQUIRED 入 PRD**（三场景皆需；3W 实测低功率喇叭[L1]+D 类功放，削波灌音圈风险，EQ_PRD §2:44）。
    **摆位 = per-channel（D-C 权重 fan-out 之后）**：各通道 D-C 权重不同（中心 w=1.0、次边 w≈0.50，~6dB 跨度），
    单一 master 限幅器保护不了最高权重通道（SN-5）。**阈值按权重缩放 T_k=T·w[k]**（D14）以保锥度——
    共阈值 per-channel 限幅会先削高权重通道、把锥度推向均匀加权 → 旁瓣抬升、-20dB SLL 劣化（EQ_PRD §2.2:54）。
    限幅器标量/近零 MAC，8 个 per-channel 可忽略。
  - **band 数 = 终调待 R3**：是否真需 EQ、几频段取决于实测正轴向响应（R3 消声室，待 T/S 2–4 周，EQ_PRD:45）。
  - **功放选型 caveat**：Plan A=ACM3128A（无内置 DSP，EQ 在主芯片）；备选 **TAS5825M 含集成 DSP/可软配 EQ**
    → 会把 EQ 账外置（EQ_PRD:28）。功放未锁；选型变更须重算 item-3 算力账。
- **成本 [L4]**：29–60 MCPS（=20–25 MAC/samp×48000×{30,50}cyc/MAC；28.8@2bq/30cyc → 60.0@3bq/50cyc）。
- **O1 系统 margin（EQ_PRD 口径 = 聚焦+O1 项，critic R11 修正）= 1.81x–2.16x**
  （best=1000/(347.45+86+29)=2.16x；worst=1000/(347.45+144+60)=1.81x）。**注：2.04–2.31x 是无-EQ 基线值，
  非 O1 值——勿混（EQ_PRD:69 critic 修正记录）。**
- **HW-1 条件性（O1）= 有价值但非承重**（EQ_PRD:81）：offload 2–3 biquad 后 core 仅余限幅+编排；
  **不 offload 也守 ≥1.0x**。详见 §2 CONSEQUENCE。
- **状态**：item-3 PRD 规格 = O1 锁定；限幅 REQUIRED 入 PRD；EQ band 数待 R3 实测。
```

---

# 2. CONSEQUENCE RECOMPUTATION（承重数学，公式 + L 分级）

> 预算 = 1000 MCPS（CCLK 实测 1e9 [L1/EZKIT]）；核需求 = 347.45 MCPS [L1]（8ch FIRA algo demand）。
> margin = 1000 / (核需求 + Σ项)。混 L1+L4 → 结果**继承最弱级 [L4]**。

## 2.1 §8 item-3 包络坍缩
- 旧（裁定前）：item-3 = **0–150 MCPS [L4]**（EQ 链未定，0=无 EQ 到 150=rich）。
- 新（O1 锁定）：item-3 = **29–60 MCPS [L4-pinned-by-PRD-ruling]**（O1 LEAN，EQ_PRD:69）。
  → §8 最大不确定项（EQ）从 0–150 坍缩到 29–60，残余包络显著收窄。

## 2.2 整系统残余 margin 重算（v1 收窄 = 含聚焦 + O1）
公式：`margin = 1000 / (347.45[L1] + focus[L4] + O1[L4] + io[L3] + irq[L3] + ctl[L4] + WCET[L3])`
代入区间（best=各项低端 / worst=各项高端）：
- focus 86–144 [L4]（2.88 MMAC/s × 30–50 cyc/MAC）｜O1 29–60 [L4]｜io 5–30 [L3]｜irq 2–15 [L3]｜
  ctl 1–10 [L4]｜WCET +34.7–173.7 [L3]（核 347.45 的 +10%–50%）
- **best**：1000/(347.45+86.4+29+5+2+1+34.7)=1000/505.6 = **1.98x**
- **worst**：1000/(347.45+144+60+30+15+10+173.7)=1000/780.1 = **1.28x**
- **独立复核（我方 python 双算）确认 best 1.98x / worst 1.28x**，与 CTO quick-check 一致。

**新整系统残余包络 = 1.28x–1.98x [L4]**，**取代**旧 1.38x–2.56x（旧假设 no-focus + EQ 0–150）。
- 收窄两面：上端降（now 含 focus 86–144 + WCET）；下端升（EQ 从最坏 150 收到 60）。

**两个口径并存（须分清，勿混）**：
| 口径 | 分母项 | best–worst | 出处 |
|---|---|---|---|
| **O1 算法侧**（EQ 材料口径） | 仅 focus + O1 | **2.16x–1.81x** | EQ_PRD:69（critic 修正） |
| **整系统残余**（§8 全清单） | focus+O1+io+irq+ctl+WCET | **1.98x–1.28x** | 本节 2.2（独立复核） |
两者非矛盾：算法侧只数算法+EQ；整系统再叠加 IO/中断/控制/WCET。对外呈现裁定三连体分母 → 用整系统口径。

## 2.3 DEC-S4-CRITERION-01 状态更新
- **item-3 依赖 = RESOLVED**（O1 已裁，DEC-S5-EQ-O1-01）→ §8 EQ 项 pinned 29–60。
- **WCET 实测 = 仍 OPEN，现为正式阈值的最后依赖**（F7_WARM=0 冷 cache + DMA 并发，§5 follow-up）。
- **新包络支持哪些阈值（陈述，NO 推荐）**：
  - **≥1.0x：在本 [L4] 包络内守**（worst 1.28x > 1.0x，已含 WCET+50%/focus 144/cyc-MAC 50 的最坏端）。
    item-3 pin 到 O1 消除了 EQ 这一条 1.0x-威胁路径；**但此守线仍条件于包络端点为 [L3/L4] 估计——若实测
    WCET>+50% 或聚焦增量>144 或 cyc/MAC>50，1.0x 仍可能被破**。故 1.0x「守」= 本包络内成立，
    WCET 实测前不可作无条件断言（与 R7 教训一致，critic R13 F13-MAJOR-1 修正）。
  - **≥1.5x**：**worst 1.28x < 1.5x = 临界偏破**（整系统口径）；算法侧口径 worst 1.81x 则守。明说：整系统最坏不达 1.5x。
  - **≥2x**：**on-core 死**（best 整系统 1.98x 差一点，O1 算法侧 best 2.16x 勉强）；须 HW-1 offload 拉升。
  - WCET 实测收窄后（若实测 <+50%），worst 上移，可能改变 ≥1.5x 判读 → 正式阈值待 WCET。

## 2.4 HW-1 条件性更新（FLAG 给 CTO，不替裁）
- **O1 下 HW-1 = 有价值但非承重**（EQ_PRD:81）：offload 2–3 biquad 后 core 仅余限幅+编排；不 offload 也守 ≥1.0x。
- **DEC-S5-OPT-ORDER-01「HW-1 最高优先」的原 rationale（EQ 威胁未解、item-3 最大威胁必须先解）现被裁定 overtaken**：
  item-3 已裁 O1（威胁从 0–150 坍缩到 29–60，非承重）。
- **排序更新问题 = FLAG 给 CTO（不替裁）**：O1 下，承重项不再是 HW-1，而是 **(1) 聚焦增量 harness（86–144→L1）+
  (2) WCET 实测（正式阈值最后依赖）**——二者现可论先于 HW-1；HW-1 降为**可选**（O1 守 ≥1.0x 不依赖它，仅
  争 ≥2x 时才需）。**本包不改 DEC-S5-OPT-ORDER-01；呈递推算数字供 CTO 决定是否重排序。**

---

# 3. PRD change blocks（`sprint2/docs/prd_update.md`，锚字符串已对 live 文件核）

## 3.1 v1 能力定义 + 场景表（车站 zoning 剔除）
prd_update.md:62（车站竖装留 Sprint4 行）后**新增** v1 zoning 能力小节：
```
> **v1 zoning 能力定义（DEC-S5-V1-SCOPE-01，2026-06-05）**：v1 提供**近场高频展区分区**能力——
>   工作距离 **2–5m**、有用频段 **≥4kHz**（博物馆/商场近端展区）。物理依据：近场瑞利极限 R=2L²/λ 门控，
>   可观聚焦效能仅在高频近距（FOCUS_EFFICACY_REPORT.md [L2/仿真]，焦点增益 4.85–8.09dB@4k/6k 2–3m、
>   净聚焦超额最高 3.9dB；语音主带 0.3–3kHz 聚焦近乎为空 = 频带错配）。
>   **车站广播场景 zoning 能力剔除**：车站 5–15m 宽带远超瑞利极限，深度分区物理为空——车站保留
>   **broadside 定向音柱**产品角色（指向性不变），**不承诺深度分区**。
>   验收指标见 §3.1.4 OPEN ITEM「高频近场净隔离」。聚焦效能 [L2/仿真]，进承诺前须消声室+现场实测升 L1。
```
场景表 prd_update.md:72（`目标场景 | 博物馆讲解、车站广播、商场分区广播`）→ 行尾加注：
```
〔v1 zoning 仅博物馆/商场近端展区（2–5m,≥4kHz）；车站=broadside 定向，不承诺 zoning，DEC-S5-V1-SCOPE-01〕
```

## 3.2 新增 EQ/限幅章节（§3.3 DSP 指标后，新小节 §3.4）
```
### 3.4 输出级 EQ / 限幅链（DEC-S5-EQ-O1-01，2026-06-05）

| 项 | 规格 | 说明 |
|----|------|------|
| **整形 EQ** | 2–3 biquad，**master-bus**（fan-out 前一次处理） | 喇叭频响校正/可懂度；band 数终调待 R3 消声室正轴向响应。master-bus 基础=broadside 同信号 + LTI 可交换（聚焦下仍成立）。成本 29–60 MCPS [L4] |
| **保护限幅器** | **REQUIRED**，per-channel，阈值按 D-C 权重缩放 **T_k=T·w[k]** | 防烧功放/喇叭（3W 实测低功率喇叭[L1]+D 类功放）；per-channel 因各路权重不同；权重缩放阈值保 -20dB 锥度（D14，否则旁瓣抬升）。限幅阈值待 U3/T-S 实测 |
| **实现路线** | EQ=IIR 可 offload 到 IIR 加速器（可选，非承重）；限幅器非线性留 core | HW-1 IIR-offload 在 O1 下=有价值非承重；功放若选 TAS5825M（含 DSP）则 EQ 账外置 |

> 算力账：item-3=O1 锁定 29–60 MCPS [L4]；聚焦后整系统残余 margin **1.28x–1.98x [L4]**（连体 §8 未计入清单
>   呈现，DEC-S4-C9-RELEASE-01）；守 ≥1.0x 实时底线，正式阈值待 WCET 实测（DEC-S4-CRITERION-01）。
```

## 3.3 验收指标占位（§3.1.4 表10 其他声学指标，新增行 + OPEN 标注）
prd_update.md:159–161（表10 SPL/不均匀度/STIPA 待实测行）区域**新增行**：
```
| **高频近场净隔离（v1 zoning）** | **≥ X dB**（X 待 CTO/PRD 定）@ 消声室 L1，扣 1/r 几何扩散后净聚焦贡献 | **OPEN ITEM**（DEC-S5-V1-SCOPE-01）；自由场仿真上界 ~3.9dB@6k 近距 [L2]，混响后更低；待消声室+现场实测 |
```

---

# 4. 状态指针（三材料顶 + scan 报告，沿前例）

## 4.1 `sprint5/efficacy_sim/FOCUS_EFFICACY_REPORT.md` 顶（关一注记后追加）
```
> 裁定注记 (2026-06-05)：CTO 已裁 v1=近场高频展区分区（2–5m,≥4kHz），走本报告选项(a)；车站 zoning 剔除（车站=broadside 定向）。DEC-S5-V1-SCOPE-01。本报告 [L2/仿真] 效能进 PRD/承诺前须消声室+现场实测升 L1（§129 缺口）。验收 X dB = PRD OPEN ITEM。
```

## 4.2 `sprint5/eq_prd/EQ_PRD_DECISION_MATERIAL.md` 顶
```
> 裁定注记 (2026-06-05)：CTO 已裁 item-3=O1（LEAN master-bus 2–3 biquad EQ + 保护限幅 REQUIRED per-ch T_k=T·w_k）。DEC-S5-EQ-O1-01。O1 系统 margin 1.81x–2.16x（算法侧）/ 整系统残余 1.28x–1.98x [L4]。HW-1=有价值非承重。band 数待 R3。
```

## 4.3 `sprint5/steering_scan/STEERING_HEADROOM_SCAN.md` 顶（v1 路线注记后追加）
```
> v1 收窄注记 (2026-06-05)：v1 进一步收窄=近场高频展区分区（2–5m,≥4kHz），车站 zoning 剔除（DEC-S5-V1-SCOPE-01）；item-3=O1（29–60 MCPS [L4]，DEC-S5-EQ-O1-01）。整系统残余 margin 重算 1.28x–1.98x（取代旧 1.38x–2.56x）。HW-1 在 O1 下=可选非承重；排序重评 FLAG 给 CTO（harness+WCET 可论先于 HW-1）。
```

---

# 5. Follow-up register（待办，不阻塞落档）

| # | 待办 | 状态/依赖 | 升级目标 |
|---|------|----------|----------|
| 1 | **聚焦增量上板 harness** | ON（收窄 v1 仍用聚焦）；DMA/中断同测 | 86–144 MCPS [L4] → [L1] |
| 2 | **WCET 实测**（F7_WARM=0 冷 cache + DMA 并发） | ON，**现为 DEC-S4-CRITERION-01 正式阈值最后依赖** | WCET 乘子 [L3] → [L1]；定 ≥1.5x 判读 |
| 3 | **R3 消声室正轴向驱动响应** | 待 T/S 2–4 周 | EQ band 数定 + 聚焦 efficacy [L2]→[L1] |
| 4 | **限幅阈值** | 待 U3/T-S 参数（额定功率/阻抗 [L4/待 T/S]） | T_k=T·w_k 绝对阈值定 [L4]→[L1] |
| 5 | **JY/T 标准文本 gap** | 仓内无 EN54/GB 应急广播/声压上限标准文本（EQ_PRD:30）；literature-patent 跟进 | 限幅/声压上限合规依据 [L4 缺口]→标准引 |

---

# 6. 三道关自指 + 无法核实
- **三道关**：本落地包 = workflow 产出（裁定落地稿）→ 关①已过（本 teammate 自验 + python 双算 margin）；
  **关② = critic R13（独立门，待）**；**关③ = CTO 常识审确认（待）**。不假设「写了即对」（POLICY v1.8 §4B）。
- **无法从桌面核实**：聚焦增量/O1/WCET 板上真值（[L4]，待 harness/实测）；聚焦 efficacy（[L2/仿真]，待消声室）；
  decisions_log/PRD 精确行号（随提交漂移，锚字符串定位，lead apply 复核）。验收 X dB = CTO/PRD 定，未臆造。
- 无 SHARC/板：板锚（347.45/1e9 [L1]）取实测；桌面 MMAC（2.88/EQ MAC）引材料；cyc/MAC 30–50=CTO 采纳板证包络；算术 [L3]/[L4] 如标。
```
