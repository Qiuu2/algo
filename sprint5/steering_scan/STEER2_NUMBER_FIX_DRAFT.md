# STEER-2 bad-number diagnosis + corrected presentation — DRAFT (no commit; critic gates, then lead patches)

> CTO challenge: "49x 纯核余量 [L3]" next to "2.88 MMAC/s 于 30.56 总" — if chip ~1000 MMAC/s-class then
>   2.9/1000=0.3% => ~340x not 49x. Which is wrong?
> ANSWER: **NONE of the three numbers is arithmetically wrong within ITS OWN frame; ALL THREE framings
>   are DESKTOP idealized-MAC accounting (1 cyc/MAC) — the exact accounting the board overturned. The
>   error is presenting ANY of them (49x, the 2.88, the 340x) next to board L1 numbers without the
>   cyc/MAC conversion caveat.** Re-derived honest board-reality presentation below.

---

## Q1 — What EXACTLY is the 49x? (numerator / denominator, quoted)

The 49x is **NOT** a focusing/steering number and **NOT** `1000/2.88`. It is a **whole-path desktop
margin line, quoted verbatim** from the cited source.

Quoted, `sprint3/dsp/dsp_8ch_report.md:64-68` (the box under the budget table):
```
ADSP-21569 保守口径：1500 MMAC/s
波束形成总算力：        30.56 MMAC/s
算力占比：               2.0%
★ 算力裕量倍数：        49×
```
- **49x = numerator 1500 MMAC/s (chip "conservative" budget) / denominator 30.56 MMAC/s (TOTAL beamforming
  path, desktop MMAC accounting).** Confirmed: `1500 / 30.56 = 49.1`.
- It is type **(a) total-path headroom**, NOT a steering-add ratio. The STEER-2 row mislabels it
  "聚焦/分区 ~49x 纯核余量" — it attaches the whole-PATH 49x to the FOCUSING add (2.88), which is a
  **category error**: 49x is the headroom of the entire 30.56 path, not of the 2.88 focus delta.
- NOTE the chip budget used is **1500** MMAC/s (the report's "保守口径"), not 1000. The CTO's "~1000
  MMAC/s-class" is the other common figure (1 GHz x 1 MAC/cyc); both are idealized (see Q3).

## Q2 — What are 30.56 and 2.88? (quoted, with filter assumptions)

Quoted, `sprint3/dsp/dsp_8ch_report.md:57-63`:
```
| 多相分析 FIR × 4 子带 | 3–24 kHz | 8 ch | 22.27 |
| 分数延迟 FIR × 4 子带 | 3–24 kHz | 8 ch | 2.88 |
| 加权求和 × 4 子带     | 3–24 kHz | 8→1 | 0.36 |
| 多相合成 FIR × 4 子带 | 3–24 kHz | 1 ch | 2.78 |
| 系统开销（DMA/中断/控制 8%） | — | — | 2.26 |
| **总计** |  |  | **30.56** |
```
- **30.56 MMAC/s = the FULL 8ch beamforming path desktop MMAC total** (analysis 22.27 + frac-delay 2.88
  + weighted-sum 0.36 + synthesis 2.78 + 8% overhead 2.26). It is the 8ch tree path (incl. analysis +
  synthesis + sum + overhead), DESKTOP idealized-MAC accounting.
- **2.88 MMAC/s = the fractional-delay FIR ADD** (the steering/focusing stage), across **4 subbands x 8
  channels at the per-subband decimated rates** (subband rates 3-24 kHz, table col "子带率"). It is the
  beamforming delay stage that sits OUTSIDE the frozen halfband filterbank core. (Tap count per the
  frac-delay FIR is the report's accounting assumption, same idealized 1 cyc/MAC basis as the rest.)

## Q3 — THE ACCOUNTING TRAP (named honestly)

**All of dsp_8ch_report's MMAC numbers are DESKTOP idealized-MAC accounting = 1 cyc/MAC.** This is the
EXACT accounting the board overturned:
- decisions_log:234 / :509: desktop [L2] projected 33x(8ch)/17x(16ch) margins from MMAC counts; **board
  [L1] measured ~25x higher real cycles** (real ~30-50 cyc/MAC incl. cache/interrupt/orchestration) ->
  desktop 33x/17x collapsed to **board 0.92x(8ch core)/...**. The MMAC count is NOT the cycle cost.
- **So on board reality:**
  - (a) the 8ch CORE path costs **1088.66 MCPS measured [L1/EZKIT]** (F7_R14_RULING_MATERIAL / decisions_log),
    NOT a "30.56-equivalent". The desktop 30.56 MMAC was ~1/35 of the real cycle demand.
  - (b) the focusing ADD of 2.88 MMAC/s, converted at the board's MEASURED ~30-50 cyc/MAC envelope (decisions_log:234/770,
    the project's only board evidence; a theoretical short-FIR floor ~3 cyc/MAC would give ~9 MCPS but has NO project
    board support — optimistic unverified floor only), costs **2.88 x (30..50) = ~86-144 MCPS [L4 range]** — NOT 2.9 MCPS.

**Verdict on the three readings:**
- **49x [L3, desktop]** — arithmetically correct as `1500/30.56` BUT (i) it is the whole-path margin,
  mislabeled onto the focus add; (ii) it is desktop idealized-MAC — **CANNOT stand next to board L1
  numbers without the cyc/MAC conversion caveat.**
- **2.88 MMAC/s** — correct as a desktop MMAC count, but it is NOT a cycle/MCPS cost; quoting it as if
  it were a board compute cost is the trap.
- **CTO's 340x (=1000/2.88)** — also arithmetically fine BUT makes the SAME idealized 1 cyc/MAC
  assumption (treats 2.88 MMAC/s as 2.88 MCPS). On board it would be 1000/(9..86) = **~12x-111x**, not
  340x. So the 340x reading is desktop-framed too.
- **NET: all three framings share the 1 cyc/MAC idealization. None survives next to L1 without the
  ~30-50 cyc/MAC board-measured reality factor (3 cyc/MAC = unverified theoretical floor only).**

### Honest board-reality presentation of STEER-2's compute cost
- **Focusing/zoning ADD (board estimate): ~86-144 MCPS [L4 range]** (= 2.88 MMAC/s x 30-50 cyc/MAC board envelope; the
  cyc/MAC factor is the unmeasured board reality, hence [L4]).
- **Against WHAT residual:**
  - vs the **post-FIRA 8ch ALGORITHM headroom**: budget 1000 - demand 347.45 = **652.5 MCPS headroom**
    [L1-derived]; the focus add 86-144 MCPS = **~13.2%-22.1%** of that headroom. (Margin moves 2.878x ->
    1000/(347.45+86..144) = **~2.04x-2.31x**.) [L4 add on L1 base]
  - vs the **whole-system residual** (DEC-S4-C9-RELEASE-01 honest denominator: §8 unaccounted 43-379
    MCPS -> residual 1.38x-2.56x): the focus add 86-144 MCPS lands INSIDE/on-top-of that unaccounted
    envelope and must be presented WITH it, never standalone.
- **Plain statement:** STEER-2 focusing is **plausibly affordable** on the post-FIRA board (single-digit
  to low-tens of MCPS on a ~650 MCPS algorithm headroom), but the affordability is **[L4 range]**, NOT a
  "49x headroom" claim. The 49x must be retired from this row.

## Q4 — Could the focusing FIRs ride FIRA? [L4 option]

**Yes, plausibly** — the fractional-delay FIRs are the same class of FIR the FIRA accelerator already runs
for the halfband segments; focusing would add more FIRA segments (per subband x channel). If offloaded,
the focus MAC work is largely **off-core**, and the on-core cost reduces to the per-segment ORCHESTRATION
(CreateTask/QueueTask/spin/postscale/cache-invalidate). **Caveat (measured anchor):** orchestration is the
dominant FIRA cost at these small windows — per-segment ~ `56,616/9 ≈ 6,290 cyc` [L1-derived from F7
g_f7_cyc_1ch_fira=56,616 / 9 segments]; adding focusing segments adds ~that-order per added segment, NOT
the tiny MAC count. So FIRA offload of focusing is **[L4 option]**: it moves MAC off-core but pays
orchestration per added segment — net benefit unquantified until measured, and gated by C9/R14 the same
as any FIRA benefit. Do NOT present a FIRA-offloaded focus cost as a selling number (iron-rule-8).

---

## Q5 — Corrected STEER-2 presentation (exact replacement text)

### Replacement for the STEER-2 row benefit cell (STEERING_HEADROOM_SCAN.md:41, the "[L3]:..." benefit)

old:
```
| **[L3]**：对称聚焦=与 STEER-4 同分数延迟 FIR 成本但仅 8 distinct ch，静态区延迟更新率≈0（2.88 MMAC/s 于 30.56 总，~49x headroom，纯核口径） |
```
new:
```
| **聚焦/分区 = 8ch 分数延迟 FIR（STEER-4 同类，8 distinct ch），静态区延迟更新率≈0**。成本口径修正（CTO 挑出 49x 误用）：源 `dsp_8ch_report.md:59-72` 的「2.88 MMAC/s 于 30.56 总、49x」是 **桌面理想 1 cyc/MAC 口径**（49x=1500/30.56=整路径余量，非聚焦 ADD 的余量；同口径已被板上推翻：桌面 33x/17x→板 0.92x，decisions_log:234）。**板上真实 ADD ≈ 2.88 MMAC/s × 30–50 cyc/MAC（板实测包络 decisions_log:234/770）= ~86–144 MCPS [L4 区间]**（理论最优短 FIR 内核或低至 ~3 cyc/MAC≈9 MCPS，但**无项目板测支撑，仅乐观下界**），落在 post-FIRA 8ch 算法 headroom（1000−347.45=**652.5 MCPS [L1-derived]**）的 ~13.2%–22.1%（margin 2.878x→**~2.04x–2.31x**）。**必须与 §8 整系统未计入清单（43–379 MCPS，残余 1.38x–2.56x，DEC-S4-C9-RELEASE-01）连体呈现，不得以 49x 或单独 2.88 示人。** FIRA-offload 聚焦 FIR = [L4 选项]（MAC 移出核但每加一段付 ~6,290 cyc/段 orchestration，F7 g_f7_cyc_1ch_fira/9 [L1-derived]；C9 闸下）。聚焦疗效 [L3/待 acoustic-sim] |
```

### Replacement for §3 Part-A mention (STEERING_HEADROOM_SCAN.md:83)

old:
```
- **broadside 聚焦/分区（STEER-2）：fit，有 ~49x 纯核 headroom**，固件 only（若不碰冻结输入缓冲）。
```
new:
```
- **broadside 聚焦/分区（STEER-2）：fit，固件 only（若不碰冻结输入缓冲）**。算力口径修正：原「~49x 纯核 headroom」是桌面理想 MAC（1 cyc/MAC）口径，**不可与板上 L1 并置**（49x=1500/30.56 整路径，已被板上 0.92x 推翻同源）。板上真实聚焦 ADD ≈ **86–144 MCPS [L4]**（2.88 MMAC/s × 30–50 cyc/MAC 板实测包络；~3 cyc/MAC=9 MCPS 仅理论乐观下界无板证），约 post-FIRA 652.5 MCPS [L1-derived] headroom 的 13.2%–22.1%（margin → ~2.04x–2.31x）；**呈现须连体 §8 未计入清单（残余 1.38x–2.56x）**。结论方向（聚焦在现板可负担）不变，但量级降为 [L4 区间]，非 49x。 |
```

### One-line note for the report's L-grade ledger / §"修正" block
```
〔CTO 2026-06-04 挑出 STEER-2 的 "2.88 MMAC/s 于 30.56 总 ~49x" = 桌面理想 1cyc/MAC 口径误置于板上语境。
 修正：49x 退出本行（它是整路径桌面余量，非聚焦余量，且同口径已被板 0.92x 推翻）；板上聚焦 ADD = 86–144 MCPS [L4]（板实测 30–50 cyc/MAC 包络），
 连体 §8 未计入（DEC-S4-C9-RELEASE-01）。源 dsp_8ch_report.md:59-72 桌面值存史，不删，加 cyc/MAC 转换注。〕
```

---

## Every ratio's numerator/denominator (audit table)

| ratio | num | denom | grade | verdict |
|---|---|---|---|---|
| 49x (source) | 1500 MMAC/s chip budget | 30.56 MMAC/s whole-path desktop MMAC | [L3 desktop] | correct math, WHOLE-PATH not focus, idealized 1cyc/MAC, mislabeled onto STEER-2 |
| CTO 340x | ~1000 MMAC/s chip | 2.88 MMAC/s focus-add (as MCPS) | [L4 desktop] | correct math, same 1cyc/MAC idealization; board => 12x-111x |
| **board focus margin (corrected)** | **652.5 MCPS post-FIRA headroom** | **86-144 MCPS focus add** | **[L4 on L1 base]** | **~4.5x-7.6x of headroom; add = 13.2%-22.1% of headroom; margin 2.878x->~2.04x-2.31x** |
| board 8ch algo margin | 1000 MCPS (CCLK 1e9 [L1]) | 347.45 MCPS demand [L1] | [L1-derived] | 2.878x (must pair §8) |
| board 8ch core margin | 1000 MCPS | 1088.66 MCPS [L1] | [L1-derived] | 0.92x (the path the 30.56 MMAC really cost) |

---

## What desktop CANNOT verify
- The real board cyc/MAC for the focusing FIR specifically (used the 30-50 board-measured envelope per critic R9; 3 cyc/MAC retained only as labeled unverified theoretical floor; prior 3-30 from the project's general
  board-vs-desktop overturn) — hence the focus ADD is [L4 range]; measurable later with a small harness.
- Focusing acoustic efficacy — [L3/待 acoustic-sim], unchanged.
- No SHARC/board here: board anchors (1088.66, 347.45, 56,616, 1e9) taken as CTO/repo [L1]; desktop MMAC
  (30.56, 2.88, 1500) quoted from dsp_8ch_report.md:57-72; arithmetic [L3]/[L4] as labeled.
```
