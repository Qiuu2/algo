# F7 R14/C9 Ruling Material (v2, FIRA build) — CTO RULES, material does not rule

> Author: dsp-algorithm teammate. Date: 2026-06-04. Build: **FIRA** (`-DFIRA_USE_REAL_ADI_FIR_HEADER
>   -DTARGET_SHARC`), ADSP-21569, CCES 2.12.1. All gates green.
> Supersedes the denominator/caveat sections of `F7_MARGIN_MATERIAL.md` (core-only, 0.92x, G6-open).
>   That file remains valid as the **core-only baseline record**; this v2 adds the FIRA result + closed G6.
> **Status: MATERIAL ONLY. Does NOT decide R14 closure or relax C9 / iron-rule-8.** Every number L-graded.

---

## 0. Board measurements this run [L1/EZKIT, CTO-measured 2026-06-04, FIRA build, free-run]

| Symbol | Value | Grade / source |
|---|---|---|
| `g_f7_cyc_8ch_fira` | 463,273 cyc/frame | [L1/EZKIT] full 8ch FIRA path (analyze+synth, ALL orchestration overhead: 72+24 segments, CreateTask/FixedPointEnable/QueueTask/spin/postscale/cache-invalidate) |
| `g_f7_cyc_8ch_core` | 1,451,030 cyc/frame | [L1/EZKIT] **but see Section 1E — exact-equal anomaly, must be reconciled** |
| `g_f7_cclk_hz` | 1,000,000,000 Hz | **[L1/EZKIT] — G6 CLOSES.** Was [L2/datasheet-assumed]; now measured. |
| `g_f7_cclk_rc` | 0 | [L1/EZKIT] GetCoreClkFreq SUCCESS -> cclk valid |
| `g_fira_f7_done` | 1 | [L1/EZKIT] F7 ran on board with FIRA |
| `g_f5_pass_all` | 1 | [L1/EZKIT] 8/8 channel subband bit-exact PASS (FIRA datapath valid) |
| `g_fira_f4_crc` | 0x2E0D8C6E | [L1/EZKIT] == F4 self-check anchor (== `g_f4_crc_core`); continuity holds |

Cross-check vs prior: core-only run `cyc_8ch_frame` = 1,451,030 [L1/EZKIT, F7_MARGIN_MATERIAL §0].

---

## 1. Arithmetic verification + L-grades (NO rubber-stamp)

### 1A. Net speedup — CONFIRMED
`1,451,030 / 463,273 = 3.1321x`. **CTO's 3.132x CONFIRMED.** This is the net per-frame speedup of the
full 8ch FIRA path (incl. ALL orchestration overhead) vs the core 8ch path, at FRAME=64.
Grade: **[L1-derived, provisional pending the §1E re-read of `g_f7_cyc_8ch_core`]** — ratio of two
[L1/EZKIT] board cycle counts, but the denominator's build-identity is in question (see 1E).

### 1B. FIRA 8ch demand + margin — CONFIRMED
- Demand: `463,273 x 750 / 1e6 = 347.45 MCPS` (fpf = BENCH_FS/BENCH_FRAME = 48000/64 = 750,
  `bench_harness.c:123`). **CONFIRMED 347.45.**
- Margin: `1000 / 347.45 = 2.878x`. Equivalently `cclk / (cyc x fpf) = 1e9 / (463273 x 750) = 2.878x`.
  **CTO's 2.878x CONFIRMED.**

### 1C. L-GRADE OF THE MARGIN — now an arithmetic on TWO L1 values. 1 GHz ASSUMPTION RETIRED.
Per POLICY-PROV-001: the margin = available_cycles/s / demanded_cycles/s.
- **Available** = `g_f7_cclk_hz` = 1.0e9 Hz = **[L1/EZKIT board-measured]** (G6 closed). The earlier
  presentation used the datasheet "Up to 1 GHz" [L2/vendor doc] as an *assumed* denominator with a
  caveat; **that assumption is now RETIRED and replaced by an L1 measurement that happens to equal it**
  (the board CGU is configured to the 1 GHz part maximum). The datasheet number is no longer load-bearing.
- **Demand** = `g_f7_cyc_8ch_fira x fpf` = **[L1/EZKIT board-measured]**.
- Therefore **margin 2.878x is [L1-derived]** (arithmetic on two L1 measurements), NOT
  [L3-on-assumed-denominator] as in v1. This is a real grade upgrade. The FIRA cycle count is also the
  honest "all-overhead-included" number (no flattering exclusions), so 2.878x is a defensible per-frame
  steady-state realtime margin for the 8ch path. (Caveat scope below: what is NOT in the demand — 3a.)

### 1D. 16ch margin — CTO's "~1.74x (est)" **IS reproducible** (critic R4 corrected this section's earlier "not reproducible" finding)
- **We do NOT have the FIRA 16ch number** (no `g_f7_*` 16ch FIRA measurement exists; the only 16ch
  figure in the codebase is the CORE-side `mcps_16ch_est` = `(cyc_8ch + 8*cyc_analyze_1ch)*fpf/1e6`,
  `bench_harness.c:125` — a core extrapolation, not a FIRA one).
- **Defensible FIRA 16ch estimates, with explicit assumptions [L3 extrapolation on L1 base]:**
  - **(A) Naive linear 2x** (16ch = 2 x 8ch FIRA demand): `2 x 347.45 = 694.9 MCPS` ->
    margin `1000/694.9 = ` **1.44x**. Assumption: 16ch is two independent 8ch FIRA passes, full
    orchestration repeated. This is the CONSERVATIVE estimate (orchestration not amortized).
  - **(B) Orchestration-amortized** (16ch reuses some per-frame setup): margin between 1.44x and 2.88x
    depending on how much of the 463,273 is fixed orchestration vs per-channel MAC. **We CANNOT split
    this without `g_f7_cyc_1ch_fira / analyze / synth`** (the per-channel splits the F7 code DOES
    compute, fira_regression.c:619-647, but which the CTO did not read out this session). See 3d.
- **The CTO's ~1.74x IS reproducible as the FIRA analog of the codebase's core 16ch convention**
  `mcps_16ch_est = (cyc_8ch + 8*cyc_analyze)*fpf/1e6` (bench_harness.c:125): with
  cyc_analyze_fira ~ 38,220 cyc (analyze ~ 66% of a per-channel chain, by the core 119116:60766
  ratio; per-channel 463,273/8 ~ 57,909, incremental analyze-only cost ~37,876 cyc **per channel**),
  16ch_est_fira ~ 463,273 + 8*38,220 = 769,033 cyc => 576.8 MCPS => **1.73x ~ CTO's 1.74x**.
  [L3 extrapolation on L1 base; UNCONFIRMED until `g_f7_cyc_analyze_fira` is read out.]
  **Defensible 16ch range: ~1.44x** (naive 2x, no orchestration amortization) **to ~1.73x**
  (analyze-only +8ch, the established convention) **to <2.88x** (full orchestration amortization).
  No single value recommended.
- NOTE all 16ch figures: R1 is bound to **8ch** (DEC-S4-R1-8CH-01, decisions_log:606-610); 16ch is
  "降为参考 / reference only" (hardware drives 16 elements via 8 A/B pairs, DOC-S4-IO-01). So the 16ch
  margin is informational, not the R1 gate.

### 1E. **EXACT-EQUAL CORE BASELINE — ANOMALY, MY EARLIER PREDICTION WAS WRONG, CRITIC WILL PROBE THIS**
`g_f7_cyc_8ch_core` (FIRA build) = 1,451,030 **EXACTLY** == core-only run `cyc_8ch_frame` = 1,451,030.
I previously predicted a small +delta. **From source, the two are NOT the same code path:**
- core-only `cyc_8ch_frame` (`bench_harness.c:115-118`): **unweighted** same-signal input
  (`s_in8[c][i]=CHIRP_INPUT[...]`, no weight), ONE call to `tfb8_process(&st8, s_in8, ...)` via the
  `Tfb8State` wrapper.
- FIRA-build `g_f7_cyc_8ch_core` (`fira_regression.c:621-630`): a **manual 8-channel loop** that
  applies `f5_apply_w(w, xin[i])` per channel (8x64 extra 64-bit mult+shift, fira_regression.c:262)
  then calls `tfb_analyze`/`tfb_synthesize` on `f7_ca[c]` directly (NOT through `tfb8_process`).
- These differ by (i) the weighting multiply and (ii) wrapper-vs-manual-loop. **Two different code
  paths landing on the SAME cycle count to the exact cycle is statistically implausible** for a free-
  running CCNT. My "exactly equal is suspicious-good" read stands.
- **Most likely explanation [L3, must be confirmed by CTO]:** the value 1,451,030 reported for
  `g_f7_cyc_8ch_core` was **carried over / substituted from the known core-only run** (it is labeled
  "in-build baseline") rather than read from the FIRA build's own `g_f7_cyc_8ch_core` global. OR a
  transcription reused the familiar number.
- **IMPACT ON THE RULING: NONE for the headline 2.878x.** That margin uses `g_f7_cyc_8ch_fira`
  (463,273, the FIRA path) and `g_f7_cclk_hz` (1e9) — both unambiguous, both directly measured. The
  3.132x SPEEDUP RATIO is the only number that depends on the core denominator; if the true in-build
  `g_f7_cyc_8ch_core` differs slightly (e.g. +the ~weighting overhead), the speedup shifts marginally
  (a few %), not the realtime margin.
- **DISCRIMINATOR (cheap, one read):** ask the CTO to re-read the FIRA build's actual
  `g_f7_cyc_8ch_core` global at idle (and `g_f7_cyc_1ch_fira/analyze/synth`). If it reads 1,451,030
  exactly, that itself is the anomaly to investigate (shared-buffer/measurement aliasing); if it reads
  slightly higher (~1.46M), the headline figures are unaffected and the speedup is ~3.13x->~3.15x.
- **I am NOT rubber-stamping `g_f7_cyc_8ch_core`. The 2.878x realtime margin does not depend on it.**

---

## 2. G6 CLOSURE — change block for the lead to apply on commit

`g_f7_cclk_hz = 1,000,000,000 Hz` [L1/EZKIT, F7 FIRA board run 2026-06-04], `g_f7_cclk_rc = 0`,
via startup `adi_pwr_Init(0u, 25u*1000000u)` (bench_main.c:130) + `adi_pwr_GetCoreClkFreq(0u,&cclk)`
(fira_regression.c:560). The CGU runs the core at the 1 GHz part maximum.

**CHANGE BLOCK — `sprint4/iface_survey.md`, G6 row (line 308, verbatim-current per critic R4):**

old (3rd cell "缺真值" + 4th cell "待板跑读"):
```
| G6 | **adi_pwr 实际调用点/CLKIN 值** | ~~example 主程序不显式调 adi_pwr，交给 `adi_initComponents()`(c:154)+ system.svc 配置~~ **【「交给 initComponents」部分已证伪 2026-06-04：其函数体仅 adi_sec_Init，见 §5c 顶注；调用点现已落定 = bench_main 启动处 `adi_pwr_Init(0, 25MHz)` + F7 `GetCoreClkFreq`，commit 524c7c0】** | 核频(目标 1GHz)/SCLK 数值未在源码暴露→算力核算缺真值 | ~~读 system/ 下 .svc 或~~ 台架 `adi_pwr_GetCoreClkFreq`（F7 测量块就绪，待板跑读 `g_f7_cclk_hz`） |
```
new:
```
| G6 ✅闭合 | **adi_pwr 实际调用点/CLKIN 值 + 核频实测** | 调用点落定 = bench_main 启动处 `adi_pwr_Init(0, 25MHz)`(bench_main.c:130) + F7 `GetCoreClkFreq`(fira_regression.c:560)，commit 524c7c0 | ~~核频未暴露~~ **【已实测 2026-06-04】CCLK = 1,000,000,000 Hz [L1/EZKIT，F7 FIRA 板跑，`g_f7_cclk_hz`，`g_f7_cclk_rc`=0]；CGU 配在 21569 的 1GHz 上限** | **G6 CLOSED**：核频不再假设，实测 1GHz；裕量从 [L3/假设分母] 升 [L1-derived]（材料 F7_R14_RULING_MATERIAL §1C） |
```

(Lead applies; this material does not edit iface_survey itself — change block only.)

---

## 3. Four options (updated, FACTS only, no recommendation; C9 still binds — see Section 5)

### (a) FIRA 2.878x realtime-capable — engineering sufficiency FACTS, with an HONEST denominator
**What 2.878x IS:** at the measured 1 GHz CCLK, the 8ch FIRA path (analyze+synth, ALL FIRA
orchestration included) consumes 1/2.878 = **34.7% of one core's per-frame budget**, leaving ~65.3%
(~652 MCPS-equiv) headroom on this core. [L1-derived]

**What is NOT yet in the 463,273-cycle demand number (honest 未计入项 — so "够用" has a denominator):**
1. **Codec / audio I/O** — SPORT/TDM DMA servicing, DAC streaming (8 channels out). Not in the
   memory-vector bench (bench is片内 vector method, no codec/A2B/DMA — bench_main.c:10). [未计入]
2. **System interrupts** — DMA-done, timer, any RTOS/scheduler ticks. Bench free-runs, no ISR load. [未计入]
3. **Input-scale / mixing / any pre/post beamforming math** beyond the 9 halfband segments + weight.
   The F7 span includes `f5_apply_w` weighting but NOT a final mix/limiter/EQ if the product adds one. [未计入]
4. **Control / UI / comms** (the headroom consumers the CTO named) — not measured; would draw from the
   ~65% remaining. [未计入]
5. **Cache contention / worst-case (non-steady) frames** — F7 measured ONE warmed steady frame
   (F7_WARM=4, fira_regression.c:593). True WCET (cold cache, interrupt storms) is >= this. [L1 steady, not WCET]
**Plain statement:** 2.878x is the **algorithm-core** realtime margin on a quiet core. Whether it is
"够用" for the product depends on how much of items 1-5 land on the SAME core. With 65% headroom it is
plausibly sufficient for a DSP-only audio core, but that is a SYSTEM-INTEGRATION judgment the CTO owns,
not a fact this bench establishes. The number is honest about its scope: it is per-frame, steady-state,
algorithm-only, single-core, 8ch, FRAME=64.

### (c) >=10x criterion review — basis overturned, measured 2.878x; options (NOT a recommendation)
- **Origin of >=10x:** written-in R1 target, `GRAFT_PLAN.md:28`, `CCNT_source.md:46`, set when desktop
  [L2] MMAC projections gave 33x(8ch)/17x(16ch) (decisions_log:509). Those [L2] projections were
  **overturned on board** (decisions_log:234, DEC-S4-R1-8CH-01): real ~25x higher cycles than MMAC count.
- **What is measured now:** core 8ch = 0.92x (fails realtime); FIRA 8ch = **2.878x** [L1-derived].
- **A revised criterion would have to argue one of:**
  - **Option C1 — keep >=10x:** then FIRA 2.878x does NOT meet it; R1 stays open; pursue (d) larger
    FRAME and/or (a) re-scope what the criterion protects. Honest: 10x was a desktop-era comfort margin
    with no stated physical basis; the board reality may make it unreachable without algorithm change.
  - **Option C2 — tie to realtime floor + explicit headroom policy** (e.g. >=2x = "core uses <=50% so
    half remains for I/O+control+WCET"): FIRA 8ch 2.878x MEETS >=2x. CTO must state what headroom % the
    policy reserves and why (cover items 3a.1-5). This requires naming the safety factor's purpose.
  - **Option C3 — WCET-based** (>=1.0x against a measured worst-case frame incl. interrupts/cold cache):
    requires measuring WCET (not the steady frame we have). Most defensible but needs more board data.
- **No recommendation. These are CTO criterion-policy calls; this material supplies the measured facts.**

### (d) Larger-FRAME amortization — [L3] scaling, + the cheap follow-up read we're missing
- **Orchestration-vs-MAC split:** the F7 code computes `g_f7_cyc_1ch_fira`, `g_f7_cyc_analyze_fira`,
  `g_f7_cyc_synth_fira` (fira_regression.c:632-646, c=7 unity channel) precisely to expose this split —
  **but the CTO did not read them out this session.** Cheap follow-up: read those 3 globals at idle
  (no re-run needed if the session is still loaded). With them: orchestration_per_segment is roughly
  constant (CreateTask/QueueTask/spin/callback are fixed cost), MAC scales with window size.
- **[L3] scaling argument:** each FIRA segment pays ~constant orchestration C + MAC proportional to its
  output window (8/16/32/64 samples at FRAME=64). At FRAME=128/256 the windows double/quadruple, MAC
  scales linearly, but the per-segment orchestration C and the 72+24 segment COUNT stay the same ->
  **orchestration is amortized over more samples -> FIRA cycles/sample DROP -> the FIRA win grows**
  (and the 2.878x margin improves) as FRAME increases. The core path also benefits but less (it has no
  per-segment QueueTask overhead to amortize), so the FIRA-vs-core speedup widens too. Magnitude is
  [L3/unquantified] until the split globals are read.
- **PRD-side tradeoff (flag only):** larger FRAME = larger group delay = `FRAME/fs`. FRAME=64 -> 1.33 ms;
  128 -> 2.67 ms; 256 -> 5.33 ms. Latency is a PRD/acoustic spec decision (announce/PA use may tolerate
  several ms; not mine to set). Also affects FIRA InputCount/WindowSize (G4, iface_survey.md:G4 row).

---

## 4. ENGINEERING LESSON (CTO-supplied, recorded)

**FIRA on-board cycle measurement MUST free-run with NO mid-loop breakpoints.** Setting a breakpoint
inside the SLOWLOOP / measured loop deadlocks the cycle-counter loop (the spin-on-ALL_CHANNEL_DONE and
the free-running CCNT do not advance correctly under a halt), corrupting the cycle counts. **Read the
`g_*` globals ONLY at the idle `while(1)` after the run completes** (bench_main.c:233 idle). This run
followed that discipline (free-run, idle read) -> clean L1 numbers.

**CHANGE BLOCK — `sprint4/dsp/core_only/bench/CCNT_source.md`** (append to the §3 measurement-discipline
section, the natural home for cycle-measurement ops; after the existing 自检 bullets ~line 40):
```
- **自由运行纪律（F7 FIRA 实测教训 2026-06-04）**：FIRA cycle 测量循环（含 spin-on-ALL_CHANNEL_DONE + 自由运行 CCNT）**严禁在测量循环内设断点**——SLOWLOOP+断点会死锁计数循环、污染 cycle 数。只在 run 跑完后的 idle `while(1)`（bench_main.c:233）读 `g_*` 全局。本次 F7 FIRA 板跑遵此 -> 干净 [L1]。
```
(Lead applies on commit; cited home = CCNT_source.md is DOC-S4-CCNT-01, the cycle-measurement ops doc.)

---

## 5. C9 / R14 framing — closure-ready package (CTO RULES)

**C9 / iron-rule-8 still BINDS:** the FIRA benefit (2.878x, 3.132x speedup) now has **L1 evidence**, but
it **does NOT enter any selection /流片 / customer commitment until the CTO explicitly rules R14 CLOSED.**
This material asserts the facts; it does not relax C9.

**R14 closure criterion (restated, from F4/F5 handoffs + DEC-S4):**
R14 closes when, on board [L1/EZKIT]: (i) FIRA bit-exact vs golden, AND (ii) FIRA cycle measured with
all overhead + true CCLK, so the margin is real not assumed.

**What is SATISFIED now [L1/EZKIT, this + prior runs]:**
- (i) bit-exact: F4 single-channel subband `g_fira_f4_crc==0x2E0D8C6E` (== core golden); F5 8-channel
  `g_f5_pass_all==1` (8/8 per-channel subband bit-exact). [L1/EZKIT] -- the FIRA datapath is proven equal
  to the verified core, per-channel, on board.
- (ii) cycle + CCLK: `g_f7_cyc_8ch_fira=463,273` [L1] (all orchestration incl.) + `g_f7_cclk_hz=1e9`
  [L1] (G6 closed) -> margin 2.878x [L1-derived], 8ch, steady-state.

**What remains OPEN / to-note:**
- The `g_f7_cyc_8ch_core` exact-equal anomaly (§1E) — does NOT block closure (headline margin independent
  of it) but should be reconciled by a re-read for the record.
- The realtime criterion itself (>=10x vs revised) is a CTO policy decision (§3c) — closure on the
  EVIDENCE is ready; whether 2.878x MEETS the bar depends on the bar the CTO sets.
- 未计入项 (§3a.1-5: codec/IO, interrupts, mixing, control, WCET) — scope caveat on "够用", not a closure blocker.
- 16ch is reference-only (R1 bound to 8ch); the ~1.44x conservative est is not the gate.

**C9 RELEASE SCOPE if the CTO rules R14 CLOSED:** upon closure, the FIRA cycle/margin numbers
(`g_f7_cyc_8ch_fira`, 2.878x, 3.132x speedup) may be cited in selection/承诺 basis as [L1/EZKIT]
(no longer frozen as [L4/待验证]); the per-frame steady-state, single-core, algorithm-only, FRAME=64,
8ch SCOPE caveat travels with them. Until that ruling, they stay [L4/待验证] for selection purposes
per iron-rule-8 (even though their provenance is L1) — C9 gates USE, not provenance.

---

## 6. What desktop CANNOT verify (explicit)
1. The `g_f7_cyc_8ch_core` exact-equal value (§1E) — cannot read the board global; flagged for re-read.
2. The orchestration-vs-MAC split (§3d) — needs `g_f7_cyc_1ch_fira/analyze/synth` read at idle.
3. WCET / system-integrated load (§3a) — bench is steady-state, algorithm-only; not measured.
4. No SHARC toolchain/board here: board values taken as CTO-supplied [L1/EZKIT]; formulas/constants
   verified from source (§1A-1E cite file:line); arithmetic is [L1-derived] or [L3] as labeled.
