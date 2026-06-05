# H1 FINAL RULING MATERIAL (v2 board re-run, all green) — CTO RULES, material does not rule

> Author: dsp-algorithm teammate. Date: 2026-06-05. Build: FIRA (H1 R15/R16 fixed), ADSP-21569, CCES.
> Status: **MATERIAL ONLY.** Does NOT rule the formal threshold; supplies L1 facts + graded options.
> Gate trail: R16 = the build-fix gate (CTO-numbered R16; consumed by the declare-before-use fix +
>   guard-stub check). This ruling material's independent gate = **critic R17** (next round number).
> Discipline: 不偏不倚 (R5/R7/R13) — no optimism bias in EITHER direction; every number [grade/source];
>   arithmetic python-double-checked; C9 paired §8 denominator throughout.

---

## 0. Board data this run [L1/EZKIT, CTO-measured 2026-06-05, free-run, idle read]

| group | symbol | value |
|---|---|---|
| gates | g_h1_done / valid | 1 / 1 |
| FG | g_h1_fg_focus_differs / g_h1_fg_zero_recovers | **1 / 1** (R15 snapshot fix PROVEN on board) |
| continuity | F4 / F5 | 1 / 1 |
| ride-along | g_h1_cclk_hz / g_h1_cclk_rc | 1,000,000,000 / 0 |
| A (focus) | focus / nofocus / **focus_only** | 591,221 / 525,850 / **65,371** cyc/frame |
| B (WCET) | cold / warm / max / min | 591,337 / 591,221 / 591,335 / 591,332 |

Both FG gates pass this time (R14 had zero_recovers=0; R15 same-state snapshot/restore fixed it; R16
fixed the declare-before-use build error). So the A/B numbers are BOOKED [L1] (the R14 run was quarantined).

---

## 1. FOCUS INCREMENT — L1 TRUTH + MAC-2x CHECKLIST CLOSED

### 1.1 The L1 number
`focus_only = 65,371 cyc/frame` -> **49.03 MCPS** [L1-derived] (= 65,371 x 750 / 1e6; fps=BENCH_FS/FRAME=750).
- **Reproducibility**: prior quarantined run 65,410 vs this 65,371 = **39 cyc apart (0.060%)** -> stable,
  reproducible. (The quarantine was for the FG self-check contract, not the cycle counter; the timing
  was always reproducible — now it is BOOKED because the run passed both FG gates.)

### 1.2 cyc/MAC with the TRUE MAC count
True MAC/frame = 8 tap x 120 samp x 8 ch = **7,680 MAC/frame** (120 samp = the real dyadic subbands
8+16+32+64, source fira_regression.c:193（+ harness 自身 sz[]）, NOT the model's 60). So **65,371 / 7,680 = 8.51 cyc/MAC** [L1-derived].

### 1.3 Why the direction is good — honestly (no spin)
- The 173-288 MCPS envelope used **30-50 cyc/MAC**, which is the board reality for the
  **tree-FIR + FIRA-orchestration** path (decisions_log:234: real ~30-50 cyc/MAC incl. per-segment
  CreateTask/QueueTask/spin/postscale/cache-invalidate + cache/interrupt).
- The H1 focus stage is **NOT that path** — it is a **flat short 8-tap core FIR loop with sequential
  access**, no FIRA orchestration, no per-segment task lifecycle. Such a loop legitimately achieves
  ~8.5 cyc/MAC (a few cycles per MAC on a SHARC MAC unit with sequential reads). So the 30-50 envelope
  was the **WRONG REFERENCE CLASS** for this kernel -> the envelope was **conservative, not wrong**, and
  the L1 came in ~3.5-5.9x cheaper. Stated plainly: good direction is REAL and EXPLAINED by kernel class,
  not by luck or by an undercount.

### 1.4 MAC-2x checklist — CLOSED, with the honest limit of what the L1 number proves
- **The 120-samp basis comes from SOURCE (sz[] = BENCH_FRAME/8,/4,/2,/1; fira_regression.c:193（+ harness 自身 sz[]）), NOT from
  the cycle count.** The L1 cycle number alone CANNOT distinguish 120-samp vs 60-samp: 65,371 over 7,680
  MAC = 8.51 cyc/MAC; the same 65,371 over 3,840 MAC (the 60-samp hypothesis) = 17.02 cyc/MAC — **both
  are arithmetically possible** for a flat FIR. So the cycle count does NOT by itself settle the MAC
  count; the MAC count is settled by the SOURCE sz[]. State this explicitly to avoid circular reasoning.
- What IS settled: the harness ran over the real 120-samp subbands (source-confirmed), so the booked
  49.03 MCPS is the cost of the TRUE 120-samp work — the right thing to compare against.
- **Compare-and-retire**: both estimates SUPERSEDED by 49.03 [L1]:
  - 86-144 MCPS — derived from the **wrong 2.88 MMAC/s** basis (assumed 60 samp/45 kHz). RETIRED.
  - 173-288 MCPS — derived from the **correct 5.76 MMAC/s** basis but the **wrong cyc/MAC class**
    (30-50, a FIRA-orchestration figure) for this flat-FIR kernel. Conservative; RETIRED.
  - **49.03 MCPS [L1] is the booked focus increment.** (cyc/MAC 8.51, true 7,680 MAC.)

---

## 2. WCET LANDING — honest, NO silent shrink in either direction

### 2.1 The measured numbers
- cold / warm = 591,337 / 591,221 = **1.000196** (cold-DATA penalty = **+116 cyc = +0.0196%**).
- max / warm = 591,335 / 591,221 = **1.000193**; max - min = **3 cyc** (intra-run jitter band).
- D-cache invalidate was ACTIVE this run (R15 flush_data_buffer over the ~20KB working set, before the
  cold frame), so this cold IS true-cold-DATA, not the R14 partial proxy.

### 2.2 Honest interpretation of the ~0 cold-DATA penalty
The +116 cyc cold-DATA penalty is **negligible relative to the ~591k-cyc frame** because: the ~20KB
working set refills from L2/external on first touch, but that refill cost (order hundreds of cycles
total) is amortized across a frame that already does ~591k cycles of FIRA/core work -> ~0.02%. This is
plausible and consistent: the FIRA path is compute/orchestration-bound, not memory-bandwidth-bound, so
cold-DATA misses are a tiny fraction. **[L1] for the cold-DATA + intra-run-jitter components.**

### 2.3 The scope discipline — what is and is NOT measured (CRITICAL, both directions)
- **MEASURED [L1, ~1.0002x]**: cold-DATA (after invalidate) + intra-run jitter. Both ~negligible.
- **UNMEASURED [L3/L4]**: (i) **I-cache cold** — symbol still C10-pending (no repo SHARC I-cache
  invalidate); the I-cache was warm from F4/F5/F7 this run too, so I-cold is NOT in the 1.0002. (ii)
  **DMA bus contention** — no SPORT/codec DMA runs in the bench. (iii) **ISR preemption** — bare-metal
The original §8 item-5 +10-50% rationale **explicitly led with cold-cache**（cold L1/L2 misses + the
FIRA cache-invalidate）alongside DMA contention + ISR jitter, as a single lumped 1.1-1.5x multiplier
（F7_R14_RULING_MATERIAL:354）。H1 now measures the cold-**DATA** sub-component at ~0 (+0.02%) [L1] —
**partially retiring that named component**。We nonetheless **keep the full +10-50% [L3] as a deliberate
conservative choice**, NOT because the unmeasured three were "always the bulk", but because: (i)
I-cache-cold, DMA contention, and ISR preemption remain genuinely unmeasured; (ii) the original
multiplier was never decomposed by sub-component, so the cold-data portion cannot be cleanly
subtracted; (iii) narrowing the [L3] range without measuring those three would be the optimism error.
The DMA/ISR harness (§4.4 register) and the C10 I-cache symbol can later narrow it with measurement.
系对原始 rationale 的失实概括，已撤。）

### 2.4 Proposed updated WCET envelope (NO collapse to 1.0002)
- **Collapsing the §8 WCET allowance to 1.0002 would be the optimism error in the other direction** —
  the 1.0002 covers only the measured share; the unmeasured share (I-cold/DMA/ISR) is untouched.
- **Honest split (proposed)**:
  - MEASURED WCET component (cold-DATA + jitter): pinned **~0 extra (+0.02%) [L1]**.
  - UNMEASURED WCET component (I-cache cold + DMA contention + ISR preemption): **KEEP a stated
    allowance**. Proposed: **+10% to +50% of the core demand on the UNMEASURED share** (= 34.7-173.7
    MCPS on the 347.45 core), grade **[L3]**, rationale: this is the same engineering envelope as the
    original §8 item-5 (cold cache + DMA contention + ISR jitter on a SHARC with a shared crossbar) —
    purely I-cold + DMA + ISR. We do NOT narrow the [L3] range because none of those three were
    measured; narrowing without measurement = optimism error. (A future DMA/ISR harness — §4 register —
    can pin DMA/ISR; the I-cold needs the C10 I-side symbol.)
- **Net**: measured WCET multiplier 1.0002x [L1]; the BOOKED WCET allowance for the residual envelope
  stays the unmeasured +10-50% [L3] (justified above), NOT collapsed.

---

## 3. DEC-S5 BUDGET CORRECTION PROPOSAL (flag from R15 resolves)

### 3.1 Focus line correction
DEC-S5-V1-SCOPE-01 "focus 86-144 MCPS [L4]" -> **49.03 MCPS [L1/EZKIT]**. The R15 FLAG ("focus likely 2x
understated, true ~173-288") **RESOLVES to: actual L1 is BETTER than BOTH estimates** — 49.03 is below
even the original 86 (because the kernel is flat-FIR ~8.5 cyc/MAC, not FIRA-orchestration 30-50). So the
v1 budget is HELPED, not hurt, by the L1 truth. (The R15 flag was directionally honest — it flagged
uncertainty; the resolution is favorable.)

### 3.2 Whole-system residual recompute (python-double-checked; both ends, formulas shown)
`margin = 1000 [L1 CCLK] / ( 347.45[L1] + focus[L1] + O1[L4] + io[L3] + irq[L3] + ctl[L4] + WCET_unmeas[L3] )`
- focus = **49.03** [L1]; O1 = 29-60 [L4]; io = 5-30 [L3]; irq = 2-15 [L3]; ctl = 1-10 [L4];
  WCET_unmeas = +34.7 to +173.7 [L3] (§2.4); measured-WCET share pinned ~0 [L1].
- **best** = 1000/(347.45+49.03+29+5+2+1+34.7) = 1000/468.2 = **2.14x**
- **worst** = 1000/(347.45+49.03+60+30+15+10+173.7) = 1000/685.2 = **1.46x**
- **New whole-system residual envelope = 1.46x – 2.14x [L4]** (inherits weakest grade = O1/ctl/WCET L4/L3).
  Supersedes R15's 1.28-1.98x (which used focus 86-144) and the proposed-correction 1.08-1.69x (focus
  173-288). The L1 focus (49) lifts both ends.

### 3.3 Distance from the 1.0x floor — plainly
- **Worst case 1.46x = 46% above the 1.0x real-time floor.** Not razor-edge any more (R14-era worst was
  1.28x = 28% above; the L1 focus moved it to 46%). The system fits real time with comfortable margin
  across the entire envelope, even in the conservative worst case (full unmeasured WCET + rich O1 + high
  io/irq/ctl). **[L4]** (the worst case still rides the [L3/L4] unmeasured allowances).

---

## 4. DEC-S4-CRITERION-01 FORMAL THRESHOLD MATERIAL (CTO rules now)

### 4.1 Dependencies — all resolved or pinned
| dependency | status |
|---|---|
| item-3 EQ chain | **RESOLVED** = O1 (DEC-S5-EQ-O1-01), 29-60 MCPS [L4] |
| focus increment | **PINNED L1** = 49.03 MCPS [L1/EZKIT] |
| WCET (measured part) | **PINNED L1** = +0.02% (cold-DATA + jitter), 1.0002x |
| WCET (unmeasured part) | **[L3] allowance** = +10-50% on core (I-cold/DMA/ISR), §2.4 |
| acoustic efficacy / X | still OPEN (R3 anechoic, T/S 2-4 wk) — NOT a compute-threshold dependency |

### 4.2 What the final envelope supports (every grade labeled, §8 paired denominator)
Whole-system residual **1.46x – 2.14x [L4]** (best=low estimates+low WCET; worst=high+full WCET):
- **>=1.0x (real-time floor)**: **MET unconditionally** — best 2.14x AND worst 1.46x both > 1.0x.
  Margin: worst is +46% above floor. [L4-envelope, but the dominant terms core+focus are L1]
- **>=1.5x**: **best MET (2.14x), worst NOT (1.46x < 1.5x)** — borderline-broken at the conservative end.
  Exact: worst 1.459x is 0.041 below 1.5x; tightening the unmeasured WCET or O1 (board-measure) would
  likely clear it, but as-is the worst case misses 1.5x by ~3%. Honest: NOT guaranteed >=1.5x system-wide.
- **>=2x**: **best MET (2.14x), worst NOT (1.46x)** — on-core 2x holds only in the favorable half; HW-1
  IIR-offload (optional per DEC-S5-OPT-ORDER-02) could lift the worst end toward 2x by moving O1 biquads
  off-core. Not guaranteed on-core across the envelope.

### 4.3 Threshold OPTIONS (CTO rules; NO recommendation)
- **Option T1 — >=1.0x realtime floor (CTO's interim)**: **MET unconditionally now**, +46% margin worst
  case. Defensible if the policy is "fit real time + rely on the [L3] WCET allowance as the safety pad."
  Cleanest given all compute dependencies are resolved/pinned.
- **Option T2 — >=1.5x (realtime + ~33% headroom)**: MET best, **NOT met worst (1.46x)**. Adopting it
  requires either (a) board-measuring the unmeasured WCET share (DMA/ISR harness) to narrow worst, or
  (b) O1 board-measure to pin the EQ term, or (c) accepting it as a target met-in-expectation-not-worst.
- **Option T3 — >=2x**: not met on-core worst case; would gate on HW-1 IIR-offload. Defer unless the CTO
  wants the extra pad.
- The CTO sets the formal threshold; this material gives the measured envelope, not a pick.

### 4.4 Residual unmeasured-risk register (carried, not hidden)
| risk | grade | closure path |
|---|---|---|
| I-cache cold WCET | [L3/L4] | C10 board item — SHARC I-cache invalidate symbol (TBD desktop) |
| DMA bus contention | [L3] | small SPORT/codec passthrough harness on EZKIT -> [L1] |
| ISR preemption | [L3] | same harness (ISR cadence x cost) -> [L1] |
| acoustic efficacy / X dB | [L2->L1] | R3 anechoic + in-situ (T/S 2-4 wk); X = PRD OPEN |
| O1 EQ cost | [L4] | board-measure the 2-3 biquad + limiter -> [L1] |

---

## 5. C9 / governance
- FIRA + focus benefit now [L1], but per DEC-S4-C9-RELEASE-01 every cited number travels WITH the §8
  unaccounted denominator (residual 1.46-2.14x [L4]); the 49.03 focus / 2.14x best are NOT shown standalone.
- This material rules nothing; CTO rules the threshold (§4.3) and the DEC-S5 budget adoption (§3).

## 6. Desktop-verified arithmetic (python double-check, all confirmed)
- focus 65,371x750/1e6 = 49.03 MCPS; 65,371/7,680 = 8.51 cyc/MAC; reproduce 65,410-65,371=39 cyc (0.060%).
- cold/warm 1.000196; max/warm 1.000193; cold-warm +116 (0.0196%); max-min 3 cyc.
- residual best 1000/468.2 = 2.136x; worst 1000/685.2 = 1.459x; worst 46% above 1.0x; >=1.5x worst miss by ~3%.

## 7. What desktop CANNOT verify
- The unmeasured WCET share (I-cold/DMA/ISR) — [L3] allowance, not board-measured (register §4.4).
- Acoustic efficacy / X — [L2/sim], R3-pending.
- No SHARC/board here: board values taken as CTO [L1/EZKIT]; MAC/sz[] from source; arithmetic [L1-derived]/[L3]/[L4] as labeled.
