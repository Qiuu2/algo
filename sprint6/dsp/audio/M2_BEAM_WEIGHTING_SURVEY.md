# M2 BEAM-WEIGHTING SURVEY -- where does the beam weighting land (3-option compare for CTO)

> dsp-algorithm teammate (M2 beam-weighting survey), 2026-06-08. CTO survey-order 1.
> SCOPE: survey-only -- HALT at the data. Compare 3 options (input-level / subband-level frac-delay
>   / both) on a) compute cost, b) beam shape & pointing, c) implementation complexity + risk.
>   dsp RECOMMENDATION + reasoning included; this is NOT a ruling. CTO decides where weighting lands.
> Numbers carry archive sources (file:line / archived figure) + L-grade; inferences marked [inferred];
>   acoustic conclusions CITED from archive, not invented. FROZEN code zero-touch (read-only compare).
>   ASCII only. No commit.

M2 three openings already LOCKED (per dispatch): whole-frame reconstruction / pin Block 1 /
O1 not in M2. THIS survey settles ONLY the remaining open: "which level does the beam weighting
land at" -- and even that is a RECOMMENDATION, the CTO rules after data.

---

## 0. The three options (exact, from archive)

| # | Option | What it is | Where in the frame chain | Archive anchor |
|---|--------|-----------|--------------------------|----------------|
| (1) | **Input-level w*xin** | 8 channels each multiplied by its static Dolph weight (broadside, no delay) | BEFORE analyze, per (ch,sample) | h2_dma_isr_measure.c:115-118 `xw[i]=(w*xin[i])>>15`; == f5_apply_w (fira_regression.c:260) |
| (2) | **Subband-level frac-delay** | Per-channel 8-tap fractional-delay FIR for near-field focusing | BETWEEN analyze and synthesize, per (ch,subband) | h1_wcet_measure.c:243-249 `h1_focus_subband(...)` x4 subbands |
| (3) | **both** | input-level static weight + subband-level frac-delay | both insertion points | (1)+(2) |

Geometry baseline for (b): N=16 / d=55mm / L=825mm / Dolph-Chebyshev -20dB / 8x A/B symmetric
series / broadside-only (CLAUDE.md DEC-S3-GEOM-01).

---

## 1. THREE-ROW COMPARE TABLE (option x {a compute / b shape / c complexity})

| Option | a) Compute cost (MCPS, L-grade) | b) Beam shape / pointing accuracy (geometry d55) | c) Implementation complexity + risk |
|--------|----------------------------------|--------------------------------------------------|--------------------------------------|
| **(1) Input-level w*xin** | **+0 net adder [L1].** The Dolph weight is ALREADY inside the 347.45 MCPS core (F7 bracket `g_f7_cyc_8ch_fira` brackets the f5_apply_w loop, fira_regression.c:611-619). Stand-alone arithmetic cost = 512 mul/frame -> ~3.27 MCPS **[L3-inferred, ILLUSTRATIVE ONLY -- NOT additive, NOT in any margin]** (kernel @8.51 cyc/MAC); core was MEASURED with the weight in, so the load-bearing number is +0. | Fixed broadside main-lobe + Dolph -20dB sidelobe suppression. NO focusing, NO steering. Matches the locked baseline directivity (BW@1k=29.28deg / 2k=14.52deg / 4k=7.26deg [L2-numpy+MATLAB, sweep_d55_results.csv]). 1k is the R5 line-ball point (0.72deg margin, tolerance-sensitive). | **Lowest.** One mul+shift loop, already coded & R14/F5 bit-exact verified (8 per-ch goldens dolph_f5_goldens.h). Q15xQ31>>15 truncation is the FROZEN, board-PASS path. R14 bit-exact boundary: TOUCHED but already CLOSED for this op. |
| **(2) Subband-level frac-delay** | **+49.03 MCPS [L1/EZKIT]** (H1 g_h1_cyc_focus_only=65,371 cyc x750/1e6, H2_PASSLINE:18; 8tap x 120 samp/frame x 8ch). | Near-field FOCUSING reachable (4k/6k @2-3m focal gain 4.85-8.09dB, net excess <=3.9dB [L2/sim, FOCUS_EFFICACY_REPORT.md]). STEERING (angle deflection) is MATH-UNREACHABLE under {c,15-c} A/B-series topology [L1, DEC-S3-DSP-03 broadside-only] -- focusing ONLY. Speech band 0.3-3kHz focusing near-empty (band-mismatch). | **Medium.** Per-(ch,subband) frac-delay FIR coeffs (8 distinct Q15 sets, mirror-symmetric {c,15-c} pair-locked) + cross-frame history (8 tap-1 tail per ch/subband, h1:120). NOT bit-exact-gated (operates in-place on local subband buffers, does NOT touch frozen filterbank/F5 CRC path, h1:47-48). Q31 risk: frac-delay FIR MAC in Q31, saturation at subband level. |
| **(3) both** | **+49.03 MCPS net [L1/EZKIT]** (input-level already in core's 347.45; only the frac-delay 49.03 is the marginal adder). Same as (2). | Dolph -20dB sidelobe suppression AND near-field focusing combined. Best beam quality for the v1 near-field zoning route. Still NO steering (topology bar, DEC-S3-DSP-03). | **Highest.** Two stages (input weight + subband frac-delay), two Q boundaries to align, two state sets. R14 bit-exact: input-weight side CLOSED; frac-delay side not-gated but adds its own Q31 saturation surface. Most insertion/format-conversion points. |

> KEY FINDING (a): options (1) and (3) cost the SAME marginal MCPS as (2) -- because the input-level
> weight is NOT a separate adder. F7 measured g_f7_cyc_8ch_fira=347.45 MCPS WITH f5_apply_w inside
> the t0..t1 bracket (fira_regression.c:611-619; confirmed bench_main.c:209 "weight applied at
> INPUT-SCALE on BOTH FIRA and core"). So the compute decision between (1)/(2)/(3) is really
> "do we pay the +49.03 focus increment or not" -- the input weight is free either way.

---

## 2. dsp RECOMMENDATION (recommendation != ruling)

**dsp recommends (3) both -- input-level Dolph weight + subband-level frac-delay -- for the v1
product target; with (1)-only as the safe fallback if focusing efficacy fails the R3 anechoic gate.**

Reasoning:
1. **The locked product baseline already IS option (1).** The Dolph -20dB input weight is the frozen,
   R14/F5 bit-exact, board-PASS path (8 per-ch goldens). It is non-negotiable for sidelobe
   suppression and costs +0 marginal MCPS. So (1) is the FLOOR -- every option includes it.
2. **v1 scope (DEC-S5-V1-SCOPE-01) IS focusing.** The locked v1 capability = near-field high-freq
   zoning (2-5m, useful band >=4kHz), which is physically the subband frac-delay focus (focal gain
   4.85-8.09dB @4k/6k [L2/sim]). Delivering v1 zoning REQUIRES option (2)'s frac-delay. Therefore
   the product that meets the locked v1 scope = (1)+(2) = **(3)**.
3. **Cost fits with wide margin.** (3)'s marginal cost over the core is the SAME +49.03 MCPS as (2)
   alone (input weight already in core). Demand = 347.45+49.03+30(io-cb core(a) worst)+60(O1)=
   486.48 MCPS -> 0.65ms wall << 1.333ms deadline -> 2.06x at 1.0x (M2_SURVEY:264, R43). Fits.
4. **Steering is OFF the table regardless** -- {c,15-c} A/B-series topology makes electronic
   deflection math-unreachable [L1, DEC-S3-DSP-03]. So no option buys steering; the choice is
   purely "static-broadside-only" (1) vs "broadside + near-field focus" (3). Since v1 scope
   demands focus, (3) wins on scope-fit.
5. **Fallback to (1)-only is cheap and reversible**: if the R3 anechoic gate finds focusing efficacy
   insufficient (the PRD net-isolation X-dB OPEN ITEM, DEC-S5-V1-SCOPE-01), drop the frac-delay
   stage and you are back at (1) = pure broadside Dolph, -49.03 MCPS, no rework of the frozen core.

NOT recommended as primary: **(2) without saying (1)** -- meaningless, because (2) is defined as the
stage BETWEEN analyze/synthesize and the input weight is upstream of analyze; you cannot have the
frac-delay "instead of" the Dolph weight. In practice the real choice is (1) vs (3).

---

## 3. deadline margin check -- do ALL three fit? (vs 2.06-2.34x [L2-cross-checked])

Frame period = 1/750 = 1.3333 ms = 1,333,333 cyc @1GHz CCLK (M2_SURVEY:226, [L1-derived]).
Marginal-adder accounting (input weight is +0, already in core 347.45):

| Option | demand MCPS (core 347.45 + adder + io-cb core(a) 30 + O1 60) | single-frame wall | 1.0x margin | fits deadline? |
|--------|--------------------------------------------------------------|-------------------|-------------|----------------|
| (1) input-level only | 347.45 + 0 + 30 + 60 = **437.45** | 0.583 ms | **2.29x** | YES (<<1.333ms) |
| (2) frac-delay only* | 347.45 + 49.03 + 30 + 60 = **486.48** | 0.649 ms | **2.06x** | YES |
| (3) both | 347.45 + 49.03 + 30 + 60 = **486.48** | 0.649 ms | **2.06x** | YES |

*(2)-alone is notional -- it still carries the input weight inside core 347.45; listed for symmetry.
So (2) and (3) have IDENTICAL demand. Compute: 347.45+49.03+30+60=486.48; wall=486.48e6/750/1e9
=0.6486e-3 s = 0.649 ms. Margin 1000/486.48=2.056x. (1): 437.45 -> 1000/437.45=2.286x.

**All three fit the deadline** -- worst case (2)/(3) = 0.649ms wall vs 1.333ms period, 2.06x at 1.0x.
Consistent with the M2_SURVEY 2.06-2.34x envelope ([L2-cross-checked]). io-cb core(a) uses worst
reserve 30 (R42); O1 uses worst 60 [L4-pinned]. The (1)-vs-(3) delta is exactly the +49.03 focus
increment (37% of the core+focus headroom is unused either way).

> CAVEAT (carried from M2_SURVEY §4, NOT re-litigated here): this is the REAL-TIME base demand. Full
> T2 1.5x system closure still needs M_contention (H2 board run) + io_callback core(a) [L3 reserve]
> + O1_contention [L4] + I_cold [L4]; pass-line = 210.19 MCPS (H2_PASSLINE:21), mechanical criterion
> M_contention + three-reserves <= 210.19. base 486.48 leaves ~180 MCPS to the pass-line. This
> survey does NOT predict board-run results (R5 discipline).

---

## 4. openings / missing data (survey scope)

### 4.1 compute (a)
- **Input-level stand-alone cost ~3.27 MCPS is [L3-inferred]** (512 mul/frame x 8.51 cyc/MAC kernel
  ratio x 750 fps). It is NOT used in any margin number -- margin uses the MEASURED core 347.45
  which already contains it. Listed only to show the op is sub-1% of core. The LOAD-BEARING fact is:
  input-level weight = +0 marginal [L1, F7 bracket fira_regression.c:611-619].
- **frac-delay 49.03 MCPS [L1/EZKIT]** is the H1 v2 board-booked focus_only (65,371 cyc). This is a
  REPRESENTATIVE 8-tap frac-delay envelope; per-(ch,subband) true product delays settle at zone-set
  time (~0 per-frame update, h1:43-45). Product focus on the SAME 120 samp/frame -> same ~5.76
  MMAC/s class (the old 86-144 MCPS budget was ~2x understated; superseded by board 49.03, R15/R16).

### 4.2 beam shape (b)
- Focusing acoustic EFFICACY (focal gain / net isolation) is [L2/sim] (FOCUS_EFFICACY_REPORT.md);
  the PRD net-isolation acceptance "X dB @ anechoic L1" is an OPEN ITEM (X TBD by CTO/PRD,
  DEC-S5-V1-SCOPE-01). Whether (3)'s focus is WORTH the +49.03 depends on this gate -- not settled.
- d55 BW@1k=29.28deg is line-ball (R5, 0.72deg margin, tolerance-sensitive, 8-pair P(BW>30)=5.33%
  [L2-MC]). This is a BASELINE-DIRECTIVITY risk independent of which weighting option -- all options
  inherit it (the static Dolph weight sets it; frac-delay focus does not change far-field BW).
- Steering math-unreachable under A/B series is [L1, DEC-S3-DSP-03] -- no option buys steering;
  angle deflection would need a 16ch hardware fork + d re-litigation (separate line, not M2).

### 4.3 complexity / risk (c)
- (3)'s frac-delay Q31 saturation surface is NOT bit-exact-gated (operates on local subband buffers,
  off the frozen F5 CRC path, h1:47-48) -- so it carries audio-quality risk (limit-cycle / overflow
  on focus FIR) that must be caught by listening/measurement, NOT by the bit-exact harness. [inferred]
- Q31 <-> FIRA INTEGER enum + headroom -4.8dB hold (tree_filterbank.h:38) apply to ALL options at
  the M1 int32 <-> FIRA Q31 boundary (R37/R38, M2_SURVEY §2.4) -- option-independent, board-confirm.
- Whole-frame reconstruction granularity + TX [8ch][64]->[64frame][8slot] deinterleave already
  LOCKED open (per dispatch) -- not re-opened here.

### 4.4 what is CTO's to rule (NOT this survey)
- [CTO rule] (1) input-level only (broadside Dolph, no focus) vs (3) both (broadside + near-field
  focus). dsp recommends (3) with (1)-fallback; CTO rules after R3 efficacy gate + budget call.
- [CTO rule] whether to pay the +49.03 focus increment NOW (in M2) or defer focus to a later
  milestone and ship M2 as (1)-only first.

---

## 5. for critic -- what to verify

1. **(a) load-bearing claim**: input-level weight = +0 marginal MCPS. Verify F7 bracket
   fira_regression.c:611-619 (t0..t1) DOES contain the f5_apply_w loop :614, and bench_main.c:209
   confirms "weight applied at INPUT-SCALE on BOTH FIRA and core". If true, (1)/(3) compute equality
   stands; if the bracket excludes the weight, the +3.27 MCPS would be additive and the table changes.
2. **(a) frac-delay 49.03**: H2_PASSLINE:18 = H1 g_h1_cyc_focus_only=65,371 x750/1e6=49.03 [L1/EZKIT].
   Verify the (2)/(3) demand 486.48 and margin 2.06x arithmetic.
3. **(b) acoustic citations**: focal gain 4.85-8.09dB [L2/sim FOCUS_EFFICACY], BW@1k=29.28deg
   [L2-numpy+MATLAB], steering-unreachable [L1, DEC-S3-DSP-03] -- all CITED, none invented. Verify
   no L2/L3 dressed as L1, and the R5 line-ball 0.72deg margin is attributed (not the survey's claim).
4. **(c) bit-exact boundary**: (1) input-weight is R14/F5-gated CLOSED; (2)/(3) frac-delay is NOT
   bit-exact-gated (h1:47-48). Verify this is stated as a RISK (audio-quality, off-CRC-path), not
   hidden, and Q31/headroom risks are option-attributed.
5. **recommendation discipline**: confirm the dsp recommendation is framed as recommendation != ruling,
   does NOT pre-empt CTO, and the (1)-fallback reversibility (-49.03, no frozen-core rework) is honest.
6. **deadline closure honesty**: confirm §3 states base-demand fits but full T2 1.5x closure stays
   CONDITIONAL on H2 board run + three reserves (pass-line 210.19), no board-result prediction (R5).

---

## HALT -- M2 beam-weighting survey output, awaiting CTO ruling on weighting level.

Do NOT pre-judge CTO's M2 weighting ruling. Frozen code zero-touch (this survey is read-only compare).
No commit. Recommendation != ruling.
reviewer pending: critic gate (three-gate POLICY v1.8 section 4B).
dsp-algorithm @ claude-opus-4-8 / 2026-06-08.
