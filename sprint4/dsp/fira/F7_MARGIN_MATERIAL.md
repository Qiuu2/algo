# F7 Margin Ruling Material (core-only board run) — MATERIAL ONLY, CTO RULES R14/C9

> Author: dsp-algorithm teammate. Date: 2026-06-04. Build: core-only (NO FIRA), ADSP-21569, CCES 2.12.1.
> Status: **MATERIAL ONLY.** This document does **NOT** decide R14 closure or relax C9 / iron-rule-8.
> Every number carries an `[L-grade/source]`. Every margin formula is shown with its source pointer.
> **G6 CAVEAT (PROMINENT): the actual board CCLK is UNMEASURED in this build (`g_f7_cclk_hz`=0,
>   sentinel "not read" — see Section 1B). All margins below are computed against the datasheet
>   *maximum* 1 GHz [L2/vendor], NOT a measured CCLK. If the real CCLK < 1 GHz, every margin is
>   WORSE than stated here.** The CCLK read closes only on the pending FIRA-build F7 run.

---

## 0. Board measurements (this build) [L1/EZKIT, CTO-measured 2026-06-04]

| Symbol | Value | Grade / source |
|---|---|---|
| `bitexact_pass` | 1 | [L1/EZKIT] core-only board run |
| `crc32` | 0x90556BC7 | [L1/EZKIT] == frozen golden (GOLDEN_CRC32), `crc_match=1`, `spot_match=1` |
| `cyc_valid` | 1 | [L1/EZKIT] true CCNT (clock()/REGF_EMUCLK), not host placeholder |
| `cyc_analyze_1ch` | 119,116 cyc | [L1/EZKIT] one-channel analyze, steady frame |
| `cyc_synth_1ch` | 60,766 cyc | [L1/EZKIT] one-channel synthesize, steady frame |
| `cyc_8ch_frame` | 1,451,030 cyc | [L1/EZKIT] **8 independent chains (analyze+synth), NO cross-channel sum — F5-B semantic** |
| `mcps_8ch` | 1088.66 | [L1/EZKIT] derived on board, see Section 1A (units = **Mcycle/s of DEMAND**, not MMAC) |
| `mcps_16ch_est` | 1803.35 | [L1/EZKIT] derived on board (8ch + 8x one-ch analyze extrapolation) |
| `g_f7_cclk_hz` | 0 | **[sentinel "not read", NOT a failed read]** — compiled out in core-only build, Section 1B |

---

## 1A. What is `mcps_8ch` computed against? — CCLK-INDEPENDENT cycle DEMAND. CONFIRMED from source.

The CTO cross-check is **CONFIRMED**. The bench MCPS is a *demand* number, independent of CCLK.

Source (`sprint4/dsp/core_only/bench/bench_harness.c:124-126`):
```c
double fpf = (double)BENCH_FS/BENCH_FRAME;          /* frames/sec */
r->mcps_8ch     = (double)r->cyc_8ch_frame * fpf / 1e6;
r->mcps_16ch_est= (double)(r->cyc_8ch_frame + 8u*r->cyc_analyze_1ch) * fpf / 1e6;
```
Constants (`bench_harness.h:30-32`): `BENCH_FS=48000`, `BENCH_FRAME=64` -> `fpf = 48000/64 = 750` frames/s [L1/source].

**Formula (in words):** `mcps_8ch = cyc_8ch_frame [cycles/frame] x 750 [frames/s] / 1e6`
= **cycles DEMANDED per second** (in millions). There is NO CCLK term. CCLK enters only on the
*available* side (Section 2). So `mcps_8ch` answers "how many Mcycle/s of core work does the 8ch
core path demand to keep up with a 48 kHz / 64-sample frame stream", which is CCLK-independent.

**Arithmetic check (mine, [L3]):** `1,451,030 x 750 / 1e6 = 1088.27`. Board reports **1088.66**.
- Delta = +0.39 (+0.036%). The CTO's hand-calc `1451030*750/1e6 = 1088.27` matches mine exactly.
- Source of the delta: the formula and constants are fixed (fpf=750 exactly), so the ~0.036%
  discrepancy is **NOT a formula difference**. Back-solving, 1088.66 implies an effective
  fpf=750.27 (fs~48017) — i.e. the on-board MCPS was computed from a cycle reading marginally
  different from the snapshot quoted to me (cycle-counter jitter between the `cyc_8ch_frame` latch
  and the MCPS computation), or display rounding. **Sub-0.04%, immaterial to any margin ruling.**
  [L3 reasoning; the exact cause is not verifiable from desktop — see Section 6.]
- Same check for 16ch: `(1,451,030 + 8*119,116) x 750/1e6 = 1802.97` vs board 1803.35 (+0.02%). Consistent.

**Verdict 1A: CONFIRMED.** `mcps_8ch` is a CCLK-independent cycle-DEMAND figure (Mcycle/s), exactly
per `bench_harness.c:124-126`. Board value matches the source formula to within +0.036% (jitter/rounding).

## 1B. Why is `g_f7_cclk_hz` = 0? — guard compiled out in core-only build. CONFIRMED, NOT a failed read.

Guard chain (`sprint4/dsp/fira/fira_regression.c`, fira_f7_measure):
- The CCLK read `adi_pwr_GetCoreClkFreq(0u, &cclk)` (and its rc capture) sits inside
  `#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)` (the block around the
  `g_f7_cclk_rc = (int)adi_pwr_GetCoreClkFreq(...)` line).
- `adi_pwr_Init` at startup is likewise guarded `#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)` (`bench_main.c`).
- The **core-only build does NOT define `FIRA_USE_REAL_ADI_FIR_HEADER`** (the whole F2-F7 FIRA
  block in `bench_main.c` is under `#ifdef FIRA_USE_REAL_ADI_FIR_HEADER`, and `fira_f7_measure()`
  is never called in core-only). Therefore the CCLK read is **compiled out**, `g_f7_cclk_hz` keeps
  its initializer `0u` = the documented sentinel "0 = not read / desktop" (`fira_regression.c`
  decl comment, `bench_main.c:85` comment).

**Verdict 1B: CONFIRMED.** `g_f7_cclk_hz=0` is the **"not read" sentinel**, NOT a failed/garbage read.
**G6 remains OPEN.** The build that DOES fill it = the **FIRA build** (`-DFIRA_USE_REAL_ADI_FIR_HEADER
-DTARGET_SHARC`), whose F7 run (`fira_f7_measure`) is **still pending** — that run also produces
`g_f7_cyc_8ch_fira`, `g_f7_pwrinit_rc`, `g_f7_cclk_rc`. Until then the actual CCLK is unmeasured.

---

## 2. Margin DENOMINATOR (available cycle budget)

**Available = CCLK in cycles/second.** For the cycle-budget margin, "available MCPS" = the core clock
expressed as Mcycle/s (the SHARC+ retires up to one instruction/cycle; the bench's `cyc_*` are
*cycles*, not MACs, so the apples-to-apples available figure is the clock rate in Mcycle/s).

**CCLK source [L2/vendor doc]:** `knowledge_base/ezkit/bsp/datasheets/ADSP-2156x-Datasheet-EN.pdf`,
**page 1 (cover / SYSTEM FEATURES)**, Rev. C, (c)2022 Analog Devices. Verbatim:
- Title: "**SHARC+ Single Core High Performance DSP (Up to 1 GHz)**" (covers ADSP-21562/63/65/66/67/**21569**).
- SYSTEM FEATURES: "Enhanced SHARC+ high performance floating-point core / **Up to 1 GHz**".
- Block diagram: core block labeled "**UP TO 1 GHz** FLOATING-POINT DSP".
- ALSO: "Enhanced FIR and IIR accelerators running **up to 1 GHz**" (relevant to the future FIRA margin).

=> **Available = 1 GHz = 1000 Mcycle/s. Grade [L2/vendor doc].**

**CAVEAT (G6, repeated):** "Up to 1 GHz" is the datasheet **maximum**. The ACTUAL CCLK on our board
is set by the CGU config and is **UNMEASURED in this build** (`g_f7_cclk_hz=0`, Section 1B). Margins
below assume the 1 GHz ceiling; if the board CGU runs the core below 1 GHz, **every margin is worse**.

---

## 3. TRUE margin = available / demand (HONEST, no softening)

```
margin = available_Mcycle_per_s / demanded_Mcycle_per_s = 1000 / mcps
```
Formula source: criterion `margin = budget / demand` per `GRAFT_PLAN.md:28`, `CCNT_source.md:46`,
`F5_F7_PLAN.md:179` (`margin = cycle_budget_per_frame / wall_cycle`, budget = CCLK x frame_period).
Note `(CCLK x frame_period)/cyc_frame == CCLK/(cyc_frame x fps) == 1000/mcps`, identical algebra.

| Path | Demand [L1/EZKIT] | Available [L2, 1 GHz] | Margin | vs realtime floor 1.0x | vs criterion >=10x |
|---|---|---|---|---|---|
| **8ch core (F5-B, no-sum)** | 1088.66 Mcyc/s | 1000 Mcyc/s | **0.92x** | **FAILS (below 1.0x)** | **FAILS (0.92 << 10)** |
| **16ch est** | 1803.35 Mcyc/s | 1000 Mcyc/s | **0.55x** | **FAILS** | **FAILS** |

(`1000/1088.66 = 0.919x`; `1000/1803.35 = 0.555x`. [L3 arithmetic on [L1] demand + [L2] available.])

### 3.1 Semantic note (MANDATORY — old baseline is NOT directly comparable) [L1/source-cited]
- The **OLD** baseline `cyc_8ch_frame = 1,006,935 cyc [L1/EZKIT, decisions_log DEC-S4-R1-8CH-01]`
  used the **OLD S3 semantic = 8-in-1-out** (8 analyze + 8 synthesize + cross-channel digital sum
  `w_add_i32`/`acc` + Q31 saturating clamp), giving margin 1.32x at assumed 1 GHz.
- The **NEW** `cyc_8ch_frame = 1,451,030 cyc` uses the **F5-B semantic = 8 INDEPENDENT chains, NO sum**
  (the 8->1 sum wrapper was deleted; product topology = 8 channels each -> its own DAC stream).
  Source of the semantic change: `bench_harness.c:120-124` (verbatim: "F5-B 语义变更: cyc_8ch_frame
  现在量的是「8 条独立链」一帧 wall cycle, 不再含跨通道数字求和...新值 = 纯 8x (analyze+synthesize)")
  and decisions_log line 270 (F5-B topology closure, CTO-locked 8-independent-DAC topology).
- **Therefore the new 1,451,030 must NOT be ratioed directly against the old 1,006,935.** The new
  number is larger because it runs 8 full independent synthesize chains instead of one summed
  synthesize. Both are [L1/EZKIT]; they measure different topologies.

### 3.2 Internal cross-check (consistency) [L3]
`8 x (cyc_analyze_1ch + cyc_synth_1ch) = 8 x (119,116 + 60,766) = 1,439,056` vs `cyc_8ch_frame =
1,451,030`. Delta = **11,974 cyc (+0.83%)** = per-channel-loop / call overhead in the 8ch loop body
(the `f5_apply_w`-free core loop at `bench_harness.c:118` plus loop control). Consistent and small ->
the 8ch number is internally coherent with the per-channel splits.

### 3.3 PLAIN-LANGUAGE STATEMENT (no softening, as ordered)
**At the datasheet-maximum 1 GHz CCLK, the 8-channel core-only path (F5-B 8-independent-chain,
analyze+synthesize, the product topology) does NOT fit real time: it demands 1088.66 Mcycle/s
against a 1000 Mcycle/s ceiling = 0.92x, which is BELOW the 1.0x real-time floor and far below the
>=10x criterion.** This is true **before FIRA enters the picture** and is the worst case only if the
board CCLK is actually 1 GHz; a lower measured CCLK makes it worse. The 16ch estimate (0.55x) is
further out. (For contrast, the OLD summed-semantic 8ch was 1.32x — above the floor but still <10x;
the F5-B product topology has pushed even the real-time floor into failure.)

---

## 4. R14 decision OPTIONS for CTO (feasibility facts only — NO recommendation, NO benefit claimed)

> C9 / iron-rule-8 DISCIPLINE (active): every FIRA benefit number stays **[L4/待验证]** until the
> FIRA-build F7 run lands `g_f7_cyc_8ch_fira` as [L1/EZKIT]. This section names targets and bounds;
> it asserts NO FIRA benefit and makes NO selection/commitment.

### (a) FIRA offload — concrete target now exists
- The core 8ch demand is **1088.66 Mcycle/s [L1/EZKIT]**. To reach the 1.0x real-time floor at 1 GHz,
  the path must shed demand to <=1000 Mcycle/s (>= ~8% reduction); to reach >=10x it must shed to
  <=100 Mcycle/s (a ~10.9x reduction). [L3 arithmetic on [L1] demand.]
- **What fraction is FIRA-offloadable:** the entire 8ch path is `f5_apply_w` (input scale) + 9
  halfband-FIR segments/channel (3 dec + 3 ana_int + 3 syn_int, per `fira_tree.h:65 FIRA_SEGS_PER_CHAN=9`)
  -> the analyze+synthesize work is **almost entirely halfband-FIR MAC work**, which is exactly what
  the FIR accelerator offloads. So the FIRA-addressable WORK (the FIR-MAC structure) is the large
  majority of the core path; HOWEVER the FIRA-path cycle cost is NOT this minus 0.8% -- the FIRA
  path replaces core MAC cycles with accelerator latency PLUS its own orchestration overhead
  (CreateTask/QueueTask/spin/postscale/cache-invalidate, 72+24 invocations, see next bullet), which
  is unmeasured. The net offloaded cycle fraction is therefore [L4/待验证] pending
  `g_f7_cyc_8ch_fira` -- NOT inferable from the 0.8% core-loop figure (that 0.8% is the CORE loop
  overhead from Section 3.2, not the FIRA-path overhead). No benefit asserted (C9). [L3 structure /
  [L4] net fraction]
- **The pending FIRA-build F7 run measures this directly** as `g_f7_cyc_8ch_fira` (full 8ch FIRA
  path INCLUDING all orchestration overhead: CreateTask/FixedPointEnable/QueueTask/spin/postscale/
  cache-invalidate, 72+24 segment invocations). **That number is [L4/待验证] until measured on board;
  no FIRA benefit is asserted here (C9).** The FIRA accelerator clock is also "up to 1 GHz" [L2,
  datasheet p.1], so the same CCLK caveat applies to the FIRA side.

### (b) Core-side optimization headroom (honest effort/uncertainty grades)
- "Task grouping / fewer Open-Close" (CTO's mention) is **FIRA-side** orchestration, not core-side.
- Core-side levers (all **[L4/未量化]**, would each need its own [L1] bench re-run to grade):
  - L1/L2 placement of hot state (`HbFirState.state[63]` delay lines, coeffs) via .ldf section
    pragmas — current build uses default placement (no section pragmas, verified). Potential cache
    effect unknown; **[L4, uncertain], effort: medium (ldf + re-measure).**
  - Inner-MAC scheduling of `tree_filterbank.c` halfband loops — but `tree_filterbank.c` is a
    **FROZEN file**; any change reopens R14 bit-exact. **Effort: high + reopens frozen baseline.**
  - **Honest bound:** core-side optimization is unlikely to find a ~10.9x reduction (that is an
    algorithmic/accelerator-class gap, not a constant-factor tuning gap). Closing even the ~8% to
    reach 1.0x by core tuning alone is **uncertain [L4]** and would need measurement.

### (c) Criterion review — where >=10x came from
- Origin: **`GRAFT_PLAN.md:28`** and **`CCNT_source.md:46`** — "R1 判据（写死）: 16ch WCET<1.333ms 且
  裕量x = 预算/实测MCPS >= 10x 且 满 PF-1"; reaffirmed `F5_F7_PLAN.md:170,179`.
- It was a **written-in design target** ("写死"), set when desktop [L2] MAC-counting projected
  17x(16ch)/33x(8ch) margins (decisions_log line 509, P0-2). Those [L2] projections were **overturned
  on board** (decisions_log line 234, DEC-S4-R1-8CH-01): real cycles ran ~25x higher than the MMAC
  count (real ~30-50 cycle/MAC + cache/interrupt), collapsing 33x to 1.32x (old semantic).
- A revised criterion would have to argue: (i) what real-world headroom (thermal, future feature
  load, 16ch growth) >=10x was protecting against, vs (ii) accepting a lower margin (e.g. >=2x, or
  even just >=1.0x real-time + a stated safety factor) now that the [L1] board truth is known.
  **This is a CTO criterion-policy call, not a dsp fact.** Stated as material only.

### (d) Structurally cheaper levers — NAMED ONLY (PRD / algorithm-change territory, NOT mine to propose)
- Block size `BENCH_FRAME` (64) — larger frames amortize per-frame overhead but change latency/PRD.
- Subband count / tree depth `TFB_NUM_LEVELS` (3 -> 4 subbands) — fewer levels = less FIR work but
  changes the acoustic/beamforming spec.
- Channel count topology (8 independent vs shared) — locked by DEC-S4 / DOC-S4-IO-01 hardware.
- **These are PRD/algorithm/hardware changes. Flagged for awareness only; outside this material's scope.**

---

## 5. Explicit non-decision statements (governance)
- **R14 is NOT decided here.** R14 closure remains gated on the FIRA-build bit-exact (FIRA crc ==
  0x90556BC7) + the FIRA F7 cycle result, per F4/F5 handoffs. CTO rules.
- **C9 / iron-rule-8 is NOT relaxed.** No FIRA benefit/margin is asserted; all FIRA numbers are
  [L4/待验证] pending the [L1] FIRA F7 run.
- **G6 is OPEN.** CCLK is unmeasured this build; all margins use the datasheet 1 GHz maximum [L2].

## 6. What desktop CANNOT verify (stated explicitly)
1. The exact cause of the +0.036% `mcps_8ch` delta (cycle-latch jitter vs display rounding) — I cannot
   re-read the board's exact `cyc_8ch_frame` at the instant MCPS was computed. Immaterial to the ruling.
2. The actual board CCLK (G6) — unmeasured this build; the FIRA-build F7 run closes it.
3. The FIRA offload benefit (Section 4a) — [L4] until the FIRA-build F7 run lands `g_f7_cyc_8ch_fira` [L1].
4. No SHARC toolchain/board here: all board values are taken as the CTO-supplied [L1/EZKIT] facts;
   formulas/constants are verified from source (Sections 1A/1B), arithmetic is [L3].
