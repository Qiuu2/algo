# H2 PASS-LINE DERIVATION — the 210.19 MCPS line, fully sourced + scope-audited

> 硬约束：此件不过 critic R21 门，板不开跑（CTO 派单线① 第一步）。
> 目的：把 210.19 MCPS 通过线**每一步溯源 + 逐项 scope 审**，防 49x 同类口径错挂（一个数跨 scope 复用/错挂分母）。
> 纪律：不偏不倚（R5 系列）——**不预测板跑结果**；只定 pass/fail 的机械判据。RAW/[L] 全程标。

---

## 1. CHAIN（每步溯源 + 分级）

| 步 | 量 | 值 | 出处 | 分级 |
|---|---|---|---|---|
| 1 | T2 正式阈值 | **>=1.5x** | DEC-S4-CRITERION-01-FINAL（CTO 2026-06-05） | 裁定 |
| 2 | CCLK | **1.0e9 Hz** | F7 板跑 g_f7_cclk_hz（G6 闭） | [L1/EZKIT] |
| 3 | 预算（1 帧周期内可用 Mcycle/s） | **1000 MCPS** | = CCLK/1e6 = 1e9/1e6 | [L1-derived] |
| 4 | 最大可容需求（达 T2） | **666.67 MCPS** | = 1000 / 1.5（步3/步1） | [L1-derived] |
| 5 | 核 8ch FIRA 需求 | **347.45 MCPS** | F7 g_f7_cyc_8ch_fira=463,273 cyc × 750 /1e6 | [L1/EZKIT] |
| 6 | 聚焦增量 | **49.03 MCPS** | H1 v2 g_h1_cyc_focus_only=65,371 cyc × 750 /1e6 | [L1/EZKIT] |
| 7 | O1 EQ（worst 端） | **60 MCPS** | DEC-S5-EQ-O1-01（O1 LEAN 29-60 [L4]，取 worst=60） | [L4-pinned] |
| 8 | 固定侧合计 | **456.48 MCPS** | = 347.45 + 49.03 + 60（步5+6+7） | 混 [L1]+[L4] |
| 9 | **余量 = 通过线** | **210.19 MCPS** | = 666.67 − 456.48（步4 − 步8） | [L4]（继承 O1 [L4]） |

**步 9 = PASS LINE 210.19 MCPS**：固定侧之外的 on-board overhead 合计须 ≤ 此值，worst-case 才达 T2 1.5x。

---

## 2. SCOPE AUDITS（本件核心——逐条工作，防错挂）

### 2a. O1 worst(60) vs best(29)：通过线必须用 worst — 否则虚增余量
- @O1=60（worst）：余量 = 666.67 − (347.45+49.03+60) = **210.19 MCPS**。
- @O1=29（best）：余量 = 666.67 − (347.45+49.03+29) = **241.19 MCPS**。
- **pass/fail 判据必须用 210.19（O1=60 worst）**。理由：O1 是 [L4] 区间 29-60，板上 EQ 未接线、真值未测；
  **worst-case 达标 = 对最坏 EQ 也守 T2**。用 241.19（O1=29）= 假设 EQ 取最省 = **虚增余量 31 MCPS** = 把
  pass 线放宽到一个未证的乐观前提上 = 49x 同类错（用乐观分母粉饰）。**verdict 用 210.19，best 241.19 仅作参考上界。**

### 2b. WCET 基底问题（49x-class trap candidate）——逐条裁，发现两处 scope 问题，给出诚实修正

**问题陈述**：原 §8 item-5 WCET +10-50% 是按**核 347.45 ONLY**算（34.7-173.7 MCPS），当时 focus/O1 还没进需求。
现在 (i) H1 的 WCET 量（cold/warm/max ~591,221-class）是在 **focus-ON 路径（core+focus）**上测的；(ii) O1 EQ 还没上板。
问：余量里的「未测 WCET 乘子」该挂哪个基底？210.19 这个 framing 有没有 double-count 或 under-count？

**裁定（逐条，不为 210.19 辩护惯性）**：

- **(P1) H1 的 WCET 测量基底 = core+focus（不是 core-only）。** H1 cold/warm/max 帧 = 591,221-class =
  8ch FIRA + focus-ON（H1 v2）。即**已测的 cold-DATA+jitter 部分（~+0.02% [L1]）已覆盖 core+focus**。
  → 余量里**剩下的 WCET 是「未测争用部分」**，不是「整段 WCET」。

- **(P2) 发现 DOUBLE-COUNT（原 §8 worst 口径，保守方向）。** H1_FINAL §2.4 明文：WCET_unmeas(+10-50%) 覆盖
  **{I-cold + DMA 争用 + ISR 抢占}**。但 §8 worst 残差里 **io(30)=codec/IO DMA、irq(15)=中断 是独立 line items**。
  → **DMA 争用与 ISR 在原 worst 口径里被计了两次**（一次作 io/irq，一次在 WCET_unmeas 内）= **保守 double-count**。
  这正是要防的「一个 overhead 跨两个 scope 名目重复进分母」。**诚实说：原 §8 worst 1.46x 偏保守（高估了需求）。**

- **(P3) 修正 framing：H2 把 DMA+ISR 争用作 ONE combined 量测，消 double-count。** H2 的
  `g_h2_cyc_frame_both_max − g_h2_cyc_frame_base` = **DMA + ISR 争用合计**（一次量，both 同时开）。
  `g_h2_inc_dma / g_h2_inc_isr` 是**归因拆分**（各自单开）。**通过判据用 combined `(both_max − base)`**——
  它是「core+focus 帧之上、DMA+ISR 同时在跑时的真实 overhead」一个数，**不再 io+irq+WCET 三项相加（那会重复）**。

- **(P4) O1 争用 + I_cold 仍未测 → 必须在 210.19 内显式预留 sub-budget，不可静默并入。**
  - O1 EQ **未上板**（EQ 未接线）→ H2 的 both_max-base **不含 O1 的争用**（O1 60 MCPS 稳态成本已在固定侧步7，
    但其**争用 adder** 未测）。
  - I_cache cold **C10 待**（符号未知）→ H2 测不到。
  → 210.19 余量须覆盖 = **(DMA+ISR 争用)[H2 测] + (O1 争用)[未测] + (I_cold)[未测]**。
    后两项不可当 0 静默——否则又是「未测项当达标」乐观错。

- **(P5) 净结论（诚实，改了 framing 不改 210.19 数本身）**：
  - **210.19 这个数 = 余量本身，溯源正确**（步4−步8，纯算术，O1=60 worst）。**不变。**
  - **变的是「210.19 须覆盖什么」的口径**：不是 io+irq+WCET 三项相加（double-count），而是
    **combined 争用[H2 测] + O1 争用[预留] + I_cold[预留]**。
  - **原 §8 worst 1.46x 偏保守**（double-count + WCET 挂 core-only 基底）；本通过线 framing 更干净，但**保守方向**
    （worst 端），**不放宽 pass 难度**——故采纳，不破坏 T2 守门严格性。

### 2c. I_cold 的安置：余量内、但 H2 测不到 → 必须显式预留或条件化
- I_cache cold 在余量内（R19 口径），但 **H2 readouts 测不到**（SHARC I-cache invalidate 符号 C10 待，桌面未知；
  H1 已测 cold-DATA~0，I-cold 是指令侧、独立项）。
- **两种诚实呈现，二选一（裁定取 A）**：
  - **(A) 条件化 verdict（采纳）**：pass 判据 = 「H2 测得 combined 争用 ≤ (210.19 − I_cold_reserve − O1_contention_reserve)」，
    且 verdict 明文标 **"T2 系统侧闭合 conditional on I_cold ≤ I_cold_reserve（C10 未关前）"**。即**不假装 I_cold=0**，
    而是把它做成显式 reserve + 条件标注。
  - (B) 把 I_cold 当 0 并标「EXCLUDING I_cold」：较弱（容易被读成已闭合）。**不取。**
- **I_cold_reserve / O1_contention_reserve 的值**：本件**不臆造**（无板测）。建议 CTO 在 verdict 时设一个保守
  reserve（如各 ~10-30 MCPS 工程界），或在 H2 板跑后据 combined 实测余地反推可容 reserve。**本件只定结构，reserve 数 CTO 设。**

### 2d. 单位/换算（一次性给全，零 MMAC/理想数）
- **唯一换算**：`MCPS = cyc × (BENCH_FS/BENCH_FRAME) / 1e6 = cyc × 750 / 1e6`（fps=48000/64=750，bench_harness.c:123）。
- 全链每个 MCPS 都由此式从 cyc 来：核 463,273→347.45；focus 65,371→49.03；H2 (both_max−base) cyc→×750/1e6。
- **零 MMAC、零理想 1cyc/MAC**：本件无任何 MAC×cyc/MAC 估算（那些已在 49x/86-144 退役链里）；通过线纯 cyc→MCPS。

---

## 3. VERDICT TEMPLATE（板跑后机械判，无再解释）

> H2 板跑后，把 idle 读出的 raw counter 代入下式。先验 FG，再算 sum，再比 210.19。

**前置 FG 门（任一 FAIL ⇒ verdict 作废，数无效）**：
- `g_h2_valid == 1` 且 `g_h2_fg_dma_loads == 1` 且 `g_h2_fg_isr_fires == 1` 且 `g_h2_isr_count_off == 0`。

**measured combined 争用（消 double-count，用 both_max）**：
```
M_contention_MCPS = (g_h2_cyc_frame_both_max - g_h2_cyc_frame_base) * 750 / 1e6
```
（归因参考，不进 sum：io = g_h2_inc_dma×750/1e6；irq = g_h2_inc_isr×750/1e6；M_contention 应 ≈ 或 ≥ io+irq 合理。）

**未测预留（H2 covers NOT，CTO 设 reserve 值）**：
```
R_reserve_MCPS = O1_contention_reserve + I_cold_reserve     (both [unmeasured]; CTO sets, conservative)
```

**PASS/FAIL 句（机械）**：
```
IF  (M_contention_MCPS + R_reserve_MCPS)  <=  210.19  MCPS
THEN  T2 系统侧 PASS — conditional on:
        (i) I_cold <= I_cold_reserve  (C10 I-cache symbol 未关前为 conditional)
        (ii) O1 EQ 上板后争用 <= O1_contention_reserve  (EQ 未接线前为 conditional)
ELSE  T2 系统侧 FAIL — 需 HW-1 EQ offload 或进一步收窄（CTO 裁）
```

**全系统 worst margin（呈递，连体 §8）**：
```
demand_worst_MCPS = 347.45 + 49.03 + 60 + M_contention_MCPS + R_reserve_MCPS
margin_worst = 1000 / demand_worst_MCPS        (>=1.5x ⇔ demand_worst <= 666.67 ⇔ 上式 sum <= 210.19)
```

**readout → allowance 映射表（哪个 H2 全局管哪块；标 H2 覆盖与否）**：
| 余量组分 | H2 全局 | 覆盖？ |
|---|---|---|
| DMA+ISR 争用（combined） | `g_h2_cyc_frame_both_max − g_h2_cyc_frame_base` | ✅ H2 测 [L1] |
| ├ DMA 争用归因 | `g_h2_inc_dma`（=dma−base） | ✅ 归因参考 |
| ├ ISR 抢占归因 | `g_h2_inc_isr`（=isr−base） | ✅ 归因参考 |
| O1 EQ 争用 adder | （无——EQ 未上板） | ❌ 预留 reserve（CTO 设） |
| I_cache cold | （无——C10 符号待） | ❌ 预留 reserve（CTO 设） + 条件标注 |
| base 自检 | `g_h2_cyc_frame_base` ≈ H1 nofocus ~525,850-class | （核对链一致性，非余量项） |

**FLAG（readouts 不覆盖的组分，verdict 必带）**：O1 争用 + I_cold = H2 测不到 → verdict 必须**条件化**（§2c-A），
不得读成「无条件闭合」。

---

## 4. 不偏不倚声明
- 本件**不预测** M_contention 会落多少、不预测 PASS/FAIL（板决定，R5 系列纪律）。
- 只定：210.19 的溯源（§1）、它须覆盖什么的诚实口径（§2，含发现的 double-count 与 O1/I_cold 预留）、
  机械 verdict 模板（§3）。reserve 具体值 CTO 设；板跑后代数即判。

## 5. 桌面验证（算术 python 双核）
- 666.67=1000/1.5；固定侧 347.45+49.03+60=456.48；余量 666.67−456.48=**210.19**；@O1=29 → 241.19。
- 换算 750=48000/64；核 463,273×750/1e6=347.45；focus 65,371×750/1e6=49.03。
- double-count 审：原 worst denom io(30)+irq(15) 与 WCET_unmeas(覆盖 DMA/ISR) 重叠 → combined both_max 消重。

## 6. 无法核实（待板/待 CTO）
- M_contention 真值（待 H2 板跑 [L1]）；O1 争用（EQ 上板后）；I_cold（C10 符号）。
- reserve 具体值（CTO 设）。本件结构性，不臆造任何板上数。
