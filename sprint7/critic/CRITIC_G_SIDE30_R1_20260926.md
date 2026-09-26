# Critic G：侧面抑制 20→30 dB 分析，第 1 轮（2026-09-26）

> 独立 critic 子代理的报告，原文照录。被审对象是 PM 会话内的 C1–C8 结论及 scratchpad 里的 side30_feasibility.py；这份脚本已作为第 1 轮版本落库，见 `sprint7/sim/side30/s7_side30_r1_feasibility.py`。
> 复核脚本：`sprint7/critic/side30_r1_scripts/`。
> **处置**：F1 已复核成立，形成 DEC-S7-RETRACT-SUBBAND-01；F2–F12 已并入 `sprint7/docs/S7_SIDE30_ANALYSIS.md`。

---

**Critic review: the side-attenuation 20→30 dB analysis (C1–C8)**
reviewer: critic @ claude-opus-5-5 / 2026-09-26

**Verdict: FAIL.** One BLOCKER (F1). Do not send C2, C6 or the per-subband recommendation to the CTO in their current form.

My own code (it does not import the lead's script) is in `scratchpad/critic/`: `tfb_probe.c`, `tfb_paths.c`, `crit_model.py`, `check1`–`check9`. My numbers are [L2 host]: the frozen C code run on x86 gcc, plus numpy. An analytic second track agrees to within 1 dB.

**F1 BLOCKER: C2, C6 and the algorithm recommendation assume a subband map that the frozen code contradicts.**
- I compiled `sprint4/dsp/core_only/src/tree_filterbank.c` read-only and ran it. The M2 path is structurally identical (`fira_tree.c:746-773`).
- SB0 passes 2.0–2.75 kHz at 0 dB, is −6 dB at 3 kHz and −71 dB at 3.5 kHz. So the real split points are **3k / 6k / 12k**, not 1.5k / 3k / 6k. The header comment (`tree_filterbank.h:19-27`) is wrong, and the S7 report §0.1 cites it as "[L1 代码]".
- The detail bands are computed as "this level − interp(lower level)" with no delay alignment. So every detail band carries full-band comb content up to +6 dB (SB1 is +6.0 dB at 500 Hz; SB3 is +6.0 dB at 2 kHz). This only cancels when all subband gains are equal.
- The model checks itself: all-D20 and all-D35 reproduce the ideal results to within 0.2 dB.
- Real-tree side attenuation at 500 / 800 / 1k / 2k / 4k (dB):

| Design | Lead's claim | Real tree |
|---|---|---|
| D1 | 23.1 / 24.1 / 22.7 / 37.8 / 37.8 | 12.9 / 19.7 / 20.6 / 19.5 / 20.7 |
| D2 | 20.3 / 35.4 / 31.6 / 37.8 / 37.8 | 14.7 / 26.0 / 21.9 / 20.5 / 20.7 |

- D2 broadband (630 Hz–5 kHz) is 20.7 dB, not the claimed 35.4.
- The on-axis response gets an audible comb: −3.7/+1.3 dB for D2.
- Consequence: on this tree, 1–3 kHz can only be changed through SB0, which covers 0–3 kHz and so includes 1 kHz.
  - The only comb-free option is one deeper table for all bands. All-D35 gives 37.3 dB broadband (630 Hz–5 kHz), costs 0 cycles, but widens the 1 kHz beam to 37.4° and changes the frozen weight table.
  - Keeping SB0 at Dolph-20 and deepening SB1–3 gives 37.8 dB only above 3.5 kHz, drops 500 Hz from 23.1 to 11.9 dB, and adds a −4.0/+2.1 dB comb.

**F2 MAJOR: tolerance labels.** The lead's "±1 dB / 5°" are Gaussian sigmas. The project convention is a uniform half-width (`sprint3/audit/matlab_verify_m2_mc.md:28`). Under that convention (±1 dB / ±5° / ±0.5 mm), all-D35 with no calibration gives median 30.6–30.9 dB and P10 26.9–28.2 dB at 1–4 kHz. That is about 4 dB better than C3's 26–27, which flips the feasibility message.

**F3 MAJOR: the calibration model can't be built as assumed.** The subband-gain mechanism (B4) is one real Q15 gain per channel per subband (`S7_DSP_ASSESSMENT.md:264`), so complex (phase) trims are not possible.
- With amplitude-only calibration (D35, 2 kHz, σ 1 dB/5°): median 28.5 / P10 24.6 dB, against 30.4 / 26.7 for complex calibration. My complex figure matches the lead's 30.2 / 26.7.
- Phase trims need per-channel fractional delays, which is the B2 cost class: 65,371 cycles alone gives 1.488×, below the 1.5× line (`S7_ALGO_UPGRADE_PROPOSAL.md:96`). So C8 is incomplete.
- Trims that differ per subband recreate the F1 comb.

**F4 MAJOR: C1's "consistent with the design ceiling" can't discriminate.** Under plausible but unrecorded conditions an ideal array reads anywhere from about 13 to 24 dB: at 1 m, Dolph-20: 18.7 / 16.0 / 13.5 dB at 1k / 2k / 4k; with the mis-mapped A-arm weights (chmap fix off; build fingerprint not recorded, per OBS doc §3 item 8): 16.1 dB at 1 kHz, 18.1 dB broadband; Z-weighting instead of A: 15.2 dB; including the 6.3 kHz band: about 16 dB. The OBS doc §4 limits this L0 reading to qualitative use and deliberately does not compute the difference. Drop the sentence.

**F5 MAJOR: C6 leaves out everything above 5.6 kHz.** With the 6.3 kHz band included (A-weighted, HPF at 630 Hz), broadband attenuation is 15.9 dB for the current design and 14.6 dB for D2. A broadband 30 dB target therefore also needs a low-pass around 5 kHz, plus (per F1) a table of at least Dolph-30 depth. That breaks the 1 kHz ≤30° beamwidth line (R10 at `decisions_log:243`; the PRD v2.4 downgraded it to an engineering reference, `prd_update.md:159`, so it is a CTO call). It also costs the 500 Hz/30° first-grade rating (R8).

**F6 MAJOR: the competitor comparison in C7 mixes 1 m and far-field data.** The competitor table was measured at 1 m (`KB-SPL-001:6`). At 1 m, an ideal Dolph-20 on our geometry reads 18.5 / 15.8 / 15.4 dB at 90°. The competitor measured 32.0 / 24.8 / 25.4. The competitor's 30° at 1 kHz is 22.5 dB. Every Dolph taper from −20 to −40 gives at most 10.6 dB there in our 1 m model. So this table can't be read with our model. It must not be used as "the competitor only reaches about 25 dB at 2–4 kHz" evidence.

**F7 MAJOR: target context is missing.** JY/T Table 9 first-grade thresholds at 90° are 10 / 20 / 25 / 10 dB at 500 / 1k / 2k / 4k (`sprint3/audit/std_table9_compliance.csv`). The PRD commits to second grade (`prd_update.md:120`). The existing test criterion is ±90° ≥12 dB (DEC-S6-TEST3-METHOD-01). 30 dB is above first grade at every point, so it is a new requirement and needs a decisions-log entry and a PRD change.

**MINOR**
- F8 (C4): wiring faults are modelled wrongly for series pairs. An open voice coil silences the whole pair: median 17.1 dB, worst 16.2 dB, not 20.3. A shorted coil doubles the partner: 19.4 dB. "Regardless of algorithm" is false for a reversed pair: a DSP sign flip fixes it, and the lead's own calibration already gives g = −1.
- F9: the "median" is the worse of ±90°. At +90° only it is 28.7 dB versus 26.7. Lead with P10 or yield instead. Also, "σ ≤ 0.5 dB/3° plus calibration gives a median of at least 30" fails at 1 kHz: the lead's own log shows 29.2.
- F10: the subband-weight mechanism (B5-2) does not exist yet. It is pending with the CTO (`decisions_log:1052`); the firmware applies input-scale weights only (`m1_loopback_tdm.c:545-547`). Splitting SB0 would mean changing the frozen tree.
- F11 (C5): for D35 the grating lobe reaches 90° at about 5.7 kHz, not 5.8–6.2: 20.9 dB at 5.7k, 12.1 dB at 5.8k.
- F12: confirm with the CTO whether "after measurement" means the L0 reading or new data. If it is new data, it must be registered within 24 hours (C8).

**INFO**
- The wrong subband edges also appear in 7 repo files (both `tree_filterbank.h` copies, the S7 report and its script, the S7 DSP assessment, the S7 proposal, and a sprint3 pf4 doc). The S7 B4/B5-2 results are also invalid. A C7 retraction sweep is needed; the headers are frozen, so this is CTO-gated.
- For independent, frequency-flat errors, the mean side power relative to on-axis is at least σ_e²/N for any real weights. That caps mean-power attenuation at ≤28.8 dB (σ 1/5) and ≤34.2 dB (σ 0.5/3). So C3 holds regardless of the weights, and dismissing the LP designs was fair.

**Confirmed claims**：anchors 22.404/23.010/26.029 dB at 1k/2k/4k；C1 ideal 22.06–24.16 dB at 90°（sector worst 20.7）；D35 at 2k/4k 37.83/37.79 dB，on-axis cost −2.47/−1.82 dB，1 kHz beamwidth 34.87°（D30）；single reversed driver at 2 kHz（Dolph-20）median 16.3、worst 13.2；single driver zeroed 20.3；reversed pair 12.3/8.6；MC（D35, 2 kHz, σ 1 dB/5°）26.7/23.3 raw、30.4/26.7 complex calibration；broadband under lead's assumptions 20.2（current）/35.4（D2, HPF 630）；competitor arithmetic 9.2/21.3/32.0/24.8/25.4；compute 57,986 and 8,171–48,000 cycles and F5' goldens match the S7 docs；DEC-S7-EXTINPUT-HIT9616-01 wording；Dolph-30 500 Hz/30° 4.06 dB（second grade）。

**Provenance gates C1–C10**：C1 PASS once the F2 relabel is done｜C2 PASS for the lead's text（the S7 "[L1 代码]" mislabel is a separate issue）｜C3 PASS｜C4 PASS｜C5 FAIL MAJOR（key premise never checked against the code, one tool only, scripts only in scratchpad）｜C6 N/A｜C7 N/A now, retraction sweep is a follow-up｜C8 PENDING（F12）｜C9 N/A（released）｜C10 N/A.

**Required rework**：redo C2 and C6 on the real tree；present the real algorithm choice as "deeper single table for all bands vs 1 kHz beamwidth (CTO decision)" or "change the frozen tree / per-channel FIR"；relabel all tolerances as σ and give the equivalent in project convention；keep the measurement recommendation but specify at least 4 m (≤2 kHz) and 8 m (4 kHz)；keep polarity/mapping QA and driver matching first, and record the build fingerprint.
