# Critic H：侧面抑制 30 dB 路线与数字，第 2 轮（2026-09-26）

> 独立 critic 子代理的报告，原文照录。
> 被审对象是 PM 按第 1 轮意见修正后的主张 R1–R5：单表路线、配对/微调蒙特卡洛、文献综合、计划顺序。
> 复核脚本：`sprint7/critic/side30_r2_scripts/`。
> **处置**：4 条 MAJOR 与 5 条 MINOR 已并入 `sprint7/docs/S7_SIDE30_ANALYSIS.md` 和 DEC-S7-SIDE30-01 的 PM 注。

---

**Verdict: CONDITIONAL.** I found no BLOCKER. The numbers reproduce. Four MAJORs are about framing and plan order, and they must be fixed before this goes to the CTO.

Scratch scripts: `scratchpad/critic2/{r2_ideal.py,mc2.py,mc3.py,mc2_out.txt}`. They do not import s7_common; M=300–400 per MC cell.

1. **MAJOR – R1 reopens a CTO ruling and breaks a spec line.**
   - The CTO's D6 ruling says "B5-1 全频段换窗不做" (decisions_log.md:1043/1068). D30 (34.9°) and D35 (37.4°) both break the BW@1k ≤30° line (S7_ACOUSTIC_SIM_REPORT.md:83,201).
   - It has to be presented as a request to reopen D6 and change the 1k spec line. The new reason is the 90° objective.
   - "Zero cycles" is true: the multiply runs whatever the value (m1_loopback_tdm.c:543-551). "Implementable today" is not:
     - The table is `static const` in the frozen `sprint4/dsp/fira/dolph_w8_q15.h:102`, so the full B5 chain applies (proposal :141: dual-track gen, F5 goldens, 5 copies, and the focus_sim 29.27° assert will raise).
     - The M2_SELFTEST eight anchors (d524fde) are derived from D20.
     - `g_m2_wtbl_sel` does not exist yet, so the JTAG switch needs new M2 code (CTO-gated).
     - Unit-specific trims need per-unit anchors or a calibration-load path, and neither exists.
     - Positive trims push the centre weights above 1.0, which breaks the GAP-SAT premise (header :69-77). Renormalising fixes it at small cost: median 0.04 dB, P90 0.55 dB.

2. **MAJOR – R3's yields are for one band (2 kHz), frequency-flat errors and a noise-free jig. They are not a unit yield.** Joint yield below means ≥30 dB at 1k AND 2k AND 4k. Each row lists as-built / +trim / pair16 / buy24 / complex.
   - Lead's flat uniform model: joint **26 / 47 / 91 / 96 / 100%**. At 2k only: 64 / 81 / 96 / 99 / 100%.
   - Gaussian σ 1 dB / 5°: joint **1 / 8 / 51 / 72 / 100%**.
   - Same variance, 50% frequency-dependent (1-octave correlation), jig noise 0.25 dB / 1.5°, pairing on a 1–4k average: 2k 56 / 72 / 90 / 95 / 99%, joint **24 / 40 / 65 / 74 / 93%**.
   - 75% frequency-dependent (0.5-octave correlation): joint **20 / 25 / 48 / 56 / 91%**. Pair+trim medians are 31.7–32.2 dB, not 34.6.
   - Jig noise alone, with flat errors, drops complex trim from 36.6 to 34.5 dB median.
   - So gain trim and buy-24 gain little once errors vary with frequency. Only per-channel filters stay robust, which supports step 5.
   - The tolerance spread is itself an L4 assumption. Label R3 "[L2 on L4 spread]" and quote joint ranges.

3. **MAJOR – plan order.**
   - (a) Step 6 must come first. Round 1 invalidates per-subband numbers the CTO is still holding (proposal :28, :138-139; B5-2 "挂起待 B6.10", decisions_log :1068). Declare the retraction and tag them now under iron rule 5. If the CTO pack goes out with them untagged, this becomes a C7 BLOCKER.
   - (b) Step 4 must be gated explicitly on step 1's measured channel-to-position map and the CTO D8 ruling (:1069). A deeper table on a mis-mapped array tells you nothing (proposal :143).
   - (c) No buy-24 purchase or table choice before step 2 has measured the real spread.

4. **MAJOR – C5.** sorting_mc.py, single_table_check.py and the papers exist only in the session scratchpad. Commit them with seeds before citing them to the CTO. The C8 24-hour clock applies to the literature.

5. **MINOR – literature wording.**
   - Start 2003's "up to 20 dB" is an extra rear (cardioid) reduction below 630 Hz compared with a single column. The paper says the LF rear values "couldn't be verified" by measurement, so it is not a measured side-rejection data point.
   - Zhu 2017 Table 3 measured contrast runs about 11–17.5 dB (about 11 at 200 Hz, 17.1–17.5 at 1 kHz). It is room zone contrast, a different metric.
   - "Robustness terms" appear only in the Straube 2015/2018 extracts, not in Duran or Thompson.
   - Say "no comparable measured evidence ≥30 dB found" rather than implying a ceiling.

6. **MINOR – step 3.**
   - 4 m at 2k and 8 m at 4k are L²/λ, half of 2L²/λ (7.9 m and 15.9 m). They also conflict with S7's own 2k at ≥8 m (proposal :150).
   - For the 90° endfire reading the near-field bias is small. Exact 1/R sums for D35 give −0.3 dB at 2k/4 m and −0.9 dB at 4k/4 m. The distances are not OK for 30° or beamwidth readings.
   - "Indoors reverberation caps the side reading" is fair but incomplete. Outdoors, the ground reflection of the main lobe caps a −35 dB side reading the same way unless the measurement is time-gated. The column should be rotated so ±90° is horizontal, and on-axis SNR needs to be about 50 dB or more.

7. **MINOR – unlisted cost and model validity.**
   - D35 is worse at 500 Hz/90°: 23.1 → 16.4 dB (D30 gives 20.3).
   - ±90° is grazing along the enclosure. The point-source, identical-element model is least valid there, and on-axis jig trims do not correct per-driver off-axis spread.

8. **MINOR – C10.** Doing step 2 on the built column (removing drivers, re-pairing, rewiring) is a hardware action and needs the C10 checklist.

9. **INFO – MC script details.** In sorting_mc.py the Gaussian branch sets dx=0, and dx follows the driver rather than the slot; that is statistically harmless here. Modelling amplitude trim as one real scalar per series pair is correct.

**Confirmed claims**
- R2, all numbers reproduced: D35 att90 31.2 dB at 630 Hz and 36.9–39.0 dB over 0.8–5k; A-weighted broadband 37.1 dB (15.8 with 6.3k); BW@1k 37.36°, 1k/30° 17.1 dB, 500/30° 3.54 dB, on-axis −2.47 dB. D30: att90 31.6–35.4 dB, BW@1k 34.87°, 1k/30° 21.8 dB, 500/30° 4.06 dB, on-axis −1.82 dB.
- R3 under the lead's own assumptions (2 kHz, median / yield): uniform 30.8/64, 32.0/81, 34.5/96, 34.9/99, 36.6/100; Gaussian 26.8/15, 29.2/40 (lead had 28.6/31), 32.5/79, 33.7/89, 35.5/100. D20 stays at 21.9–23.0 dB in every mode, so it is design-limited.
- Literature and code: zero-cycle claim holds; Van Trees (2.208) T_n·(σ_g²+σ_φ²+σ_p²), i.e. error floor = error variance × 1/WNG, matches my MC floor; Doclo mean-performance holds; van Beuningen: Bessel IIR, eight 4th-order filters at 48 kHz (:288-302), 64-point FIR, outdoor measurement at 32 m (:494-506), measured 8-channel/16-element array (:778). I could not verify the Gilbert & Morgan equation numbers from the extract.

reviewer: critic @ claude-opus-5-5 / 2026-09-26
