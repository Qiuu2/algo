# M2 Q-BOUNDARY SURVEY -- M1 int32 (24-in-32) <-> FIRA Q31 conversion point + alignment + bit-exact verification plan

> dsp-algorithm teammate (M2 Q-boundary survey specialist), 2026-06-08. CTO survey-order 2.
> SCOPE: define WHERE the M1 int32 (24-bit-in-32, left-justified) <-> FIRA Q31 conversion lives, the
>   exact alignment (left vs right), and a DESKTOP-RUNNABLE bit-exact test that critic can run against the
>   R14 golden CRC anchors (CTO hard requirement: critic MUST verify by bit-exact reproduction, NOT by
>   "should line up"). Survey + test DESIGN only -- no implementation code committed, no architecture ruling.
>   Frozen code read-only (tree_filterbank.c/tfb_8ch.c/.h / golden_ref.h / chirp_input.h / fira_tree.h /
>   dolph_f5_goldens.h). ASCII only. No commit. HALT at the end.
> NOT a board-result prediction. NOT a critic bit-exact verdict (that is critic's gate to run).

---

## 0. R14 GOLDEN CRC ANCHORS -- repo provenance (CTO transcript vs repo, native-checked)

CTO hard requirement: use the REPO ground-truth anchors, not the CTO-transcribed value. I greped the repo
myself. Result: **the CTO transcript MATCHES the repo exactly -- no discrepancy.**

### 0.1 F4 anchor (single-channel subband bit-exact)
- **CTO transcript: 0x2E0D8C6E.  Repo: 0x2E0D8C6E.  -> MATCH (no discrepancy).**
- Native source-of-truth (where the constant actually LIVES, not just where it is quoted):
  - `sprint4/dsp/core_only/bench/bench_main.c:47` `g_f4_crc_core ... self-check anchor 0x2E0D8C6E`
  - `sprint4/dsp/core_only/bench/bench_main.c:191-202` PASS gate: `g_fira_f4_crc == g_f4_crc_core (== 0x2E0D8C6E)`,
    explicitly "filter-level criterion -- a placeholder FIRA (segs=0) FAILS it (unlike the retired e2e
    0x90556BC7 test it could fool)".
  - `sprint4/dsp/fira/fira_regression.c:92` `g_f4_crc_core ... F4b self-check anchor = 0x2E0D8C6E`.
  - `sprint4/dsp/fira/dolph_f5_goldens.h:65` c=7 (center pair, w=1.0 unity) golden = `0x2E0D8C6Eu` (== F4 baseline, continuity).
  - `sprint2/docs/decisions_log.md:643-645` (in-archive ruling, DEC-S4-R14): "core subband golden = 0x2E0D8C6E
    (desktop sbgold.c reproduces FIRA core path); on-board g_f4_crc_core reads bit-identical."
- Meaning [L1/EZKIT 2026-06-04]: this is the **subband-level, filter-dependent** anchor over the frozen chirp,
  single channel, unity weight. It is NOT the retired end-to-end 0x90556BC7 (telescoping-blind, see 0.3).

### 0.2 F5 8-channel anchors (8 per-channel subband goldens, NOT one constant)
- **CTO transcript: "F5 8ch 8-anchor CRC".  Repo: the 8 anchors are a TABLE, not a single value:**
  - Native source-of-truth = `sprint4/dsp/fira/dolph_f5_goldens.h:58-65`:
    | c | pair | weight w_q15 | golden CRC |
    |---|---|---|---|
    | 0 | {0,15} edge   | 28404 (0.866829693) | 0x8E807729 |
    | 1 | {1,14}        | 16525 (0.504310065, min) | 0xB2F1E13F |
    | 2 | {2,13}        | 20371 (0.621670438) | 0x7B109C71 |
    | 3 | {3,12}        | 24031 (0.733379377) | 0xD7BD23E7 |
    | 4 | {4,11}        | 27287 (0.832733104) | 0xA000D606 |
    | 5 | {5,10}        | 29934 (0.913514611) | 0x2403E085 |
    | 6 | {6,9}         | 31802 (0.970518658) | 0xB88D91B5 |
    | 7 | {7,8} center  | 32768 (1.0, unity)  | 0x2E0D8C6E  (== F4 baseline, continuity) |
  - Corroborated verbatim: `bench_main.c:216-218` (the per-channel PASS gate lists the same 8), and the
    F5 board read-out `sprint4/dsp/fira/F5_8CH_HANDOFF.md:19` (8 decimal readings -> the same 8 anchors).
- **Pitfall flagged in the source itself** (`dolph_f5_goldens.h:24,42,56`): an UNWEIGHTED/degenerate weight
  table collapses ALL 8 channels to 0x2E0D8C6E (28 collisions) and FAILS the per-channel pairwise-distinct
  gate (FG1). So the F5 anchor is "8 DISTINCT per-channel CRCs", and 0x2E0D8C6E is correct ONLY for c=7
  (unity). Do NOT treat 0x2E0D8C6E as an 8ch single criterion (F5_F7_PLAN.md:71 explicit warning).

### 0.3 The OTHER constant (0x90556BC7) is NOT the bit-exact filter anchor -- do not use it
- `golden_ref.h:28` `GOLDEN_CRC32 0x90556BC7u` = end-to-end full-65536 output CRC. Per
  `bench_main.c:193`, `decisions_log.md:644`, `F5_F7_PLAN.md:71`: this e2e CRC is **telescoping-blind**
  (a placeholder FIRA that does out==in can still PASS it). It was RETIRED as the R14 criterion in favor of
  the subband anchors (DEC-S4-R14-GRANULARITY). **The M2 bit-exact test MUST gate on the subband anchors
  (0.1/0.2), not on 0x90556BC7.** (0x90556BC7 is still a useful SECONDARY full-chain sanity CRC -- it
  catches gross corruption -- but it is NOT the falsifying anchor; see test plan 3.4.)

> ANCHOR RULING: CTO transcript == repo for F4 (0x2E0D8C6E). The F5 "8-anchor" is the 8-row table in
> dolph_f5_goldens.h:58-65 (native), not a single constant. The retired e2e 0x90556BC7 is NOT the bit-exact
> criterion. All three facts are [L1/EZKIT 2026-06-04, in decisions_log].

---

## 1. THE TWO BOUNDARY FACTS (read, frozen, only restated)

### 1.1 FIRA core = Q31 fixed-point (signed-fractional)
- `tree_filterbank.h:31`: coeffs Q15, state/intermediate Q31, MAC accum Q46 (int64). Subbands + output = int32 = Q31.
- `fira_tree.h` `fira_tfb_analyze/synthesize` take/return `int32_t` interpreted as **Q31 signed fraction**.
- A Q31 value v_q31 represents the real fraction  x = v_q31 / 2^31, with x in [-1, +1).  [L1, frozen header]

### 1.2 M1 audio = int32 container, 24-bit ADC/DAC data, SPORT DTYPE_SIGN_FILL to bit 31 (left-justified)
Exact register/config evidence (m1_loopback_tdm.c, frozen-adjacent board TU -- the conversion lives HERE,
not in frozen core):
- **Container = 32-bit slot word**: `m1_loopback_tdm.h:24` `M1_WORD_BYTES = 4` (32-bit slot). RX/TX bufs int32.
- **ADC data width = 24-bit**: `m1_loopback_tdm.c:155` ADAU1979 `SAI_CTRL1 = 0x08` decode:
  `SLOT_WIDTH=00 (32 BCLK/slot)  DATA_WIDTH=0 (24-bit)`. So 24 valid data bits inside a 32-BCLK slot.
- **DAC data**: `m1:132/146` ADAU1962A `DAC_CTRL0`, I2S/TDM8, 32 BCLK/slot (`DAC_CTRL2 BCLK_TDMC=0`); 24-bit DAC class.
- **SPORT word-length / sign-extension = SIGN_FILL to bit 31** (THE alignment-determining call):
  - `m1:314` TX: `adi_sport_ConfigData(..., ADI_SPORT_DTYPE_SIGN_FILL, 31, false, false, false)`
  - `m1:322` RX: `adi_sport_ConfigData(..., ADI_SPORT_DTYPE_SIGN_FILL, 31, false, false, false)`
  - the "31" word-length-select arg = serial word length 32 (bits 0..31 => MSB at bit 31); DTYPE_SIGN_FILL =
    sign-extend the received word into the SPORT FIFO. `ConfigClock(...,32,...)` (m1:315/323) = 32 BCLK/word.
- **NET (board-aligned data path, [L1] on the .c, alignment-semantics [board-confirm] -- see 2.3)**: the
  24-bit codec sample is carried MSB-first in a 32-BCLK slot. With SIGN_FILL/word-length 31, the SPORT
  presents a **32-bit left-justified word**: the 24 valid bits occupy the HIGH 24 bits (bit31..bit8), the
  low 8 bits are 0 (or undefined-but-masked), and the sign is at bit 31. This is the standard ADI
  TDM/I2S MSB-first left-justified convention. [board-confirm the exact low-8 contents -- see 2.3]

---

## 2. CONVERSION-POINT RULING (RX + TX, bit-by-bit)

### 2.0 The core claim to be PROVEN bit-exact (not asserted)
> A 24-bit sample left-justified into bit31 IS ALREADY A LEGAL Q31 VALUE of 24-bit precision: its high 24
> bits are the Q31 high bits, its low 8 bits are 0. Therefore the RX->FIRA conversion is **arithmetically
> the IDENTITY (zero shift, zero mask)** -- IF and ONLY IF the SPORT word is truly left-justified-to-bit31.
> This is the "zero-conversion" hypothesis. It is plausible but MUST NOT be assumed -- it is exactly what
> the bit-exact test in section 3 falsifies. (If the SPORT delivered RIGHT-justified, the conversion would
> need `<< 8`, and a missing shift would put every sample 256x too small -> the FIRA output would be wrong
> by a fixed scale -> CRC mismatch. The test catches this.)

### 2.1 RX side: M1 rx[f] (int32, 24-in-32) -> FIRA analyze input (Q31)  -- bit-by-bit
LEFT-JUSTIFIED case (the hypothesis, DTYPE_SIGN_FILL-31 => MSB at bit31):
```
  rx word bit layout (left-justified, what SIGN_FILL-31 should give):
    bit31              bit8 bit7        bit0
    [ s  d22 ... d0 (24 valid MSB-first) ][ 0 0 0 0 0 0 0 0 ]
  Q31 interpretation: x = rx / 2^31.  The 24 codec bits already sit at Q31 positions 31..8.
  => CONVERSION = IDENTITY:   q31_in = rx;        // NO shift, NO mask, NO scale
  Precision: 24-bit (LSB step = 2^-23 in fractional terms = 2^8 = 256 in raw int32 units). Legal Q31.
```
RIGHT-JUSTIFIED case (the falsifiable alternative, if the wrapper delivers data in low 24 bits):
```
    bit31      bit23                    bit0
    [ s s s s s s s s (sign-extend) ][ d22 ... d0 (24 valid) ]
  => CONVERSION = LEFT SHIFT 8:   q31_in = (int32_t)((uint32_t)rx << 8);   // align 24-bit MSB to bit31
  (sign already carried; <<8 is well-defined on the magnitude, saturate not needed since 24<31 bits of data)
```
- **The choice between IDENTITY and `<<8` is THE alignment ruling.** It cannot be settled on desktop from
  the .c alone (the SIGN_FILL-31 semantics are a driver/HRM property). DTYPE_SIGN_FILL + length-31 STRONGLY
  implies left-justified (sign filled UP TO bit31 => MSB at bit31) [inferred], so IDENTITY is the leading
  hypothesis -- but it is [board-confirm] via HRM/SPORT (see 2.3) AND mechanically falsifiable (section 3).
- **Where it lives**: the M2 insertion region, RX-frame -> FIRA, i.e. the `xw[]` load in the H1/H2 frame
  template (`h2_dma_isr_measure.c:117-118`). H2 today loads `xw[i] = (w_q15 * xin[i]) >> 15` where `xin` is
  ALREADY Q31 (frozen chirp). For M2 the line becomes: `q31 = align(rx[f])` (IDENTITY or <<8) THEN the beam
  weight. The conversion is ONE op per sample, fused into the existing xw load. No frozen code touched.

### 2.2 TX side: FIRA synthesize output fout (Q31) -> M1 tx slot (int32, codec takes high 24)  -- bit-by-bit
LEFT-JUSTIFIED case (mirror of 2.1, the hypothesis):
```
  fout is Q31 (full 32-bit fraction). DAC takes the HIGH 24 bits (bit31..bit8), drops low 8.
  => CONVERSION = IDENTITY:   tx_slot = fout;     // NO shift; codec truncates low 8 on the wire
  Caveat: this DROPS the low 8 bits of FIRA precision (24-bit DAC). That is a PHYSICAL truncation at the
  DAC, NOT a conversion bug -- it is identical to what M1 passthrough already does, and is OUT of the
  bit-exact boundary (the bit-exact test compares the FULL 32-bit fout, see 3.2; the 8-bit DAC drop is a
  separate, expected, analog-domain loss). Optional: round-to-nearest on bit7 before truncation to reduce
  DC bias (+0.5 LSB-24) -- a quality choice, NOT required for correctness; flag to CTO.
```
RIGHT-JUSTIFIED case (if DAC slot expects data in low 24):
```
  => CONVERSION = ARITHMETIC RIGHT SHIFT 8 (sign-preserving):  tx_slot = fout >> 8;   // Q31 -> 24-bit right
  (>>8 of a signed Q31 = round-toward-neg-inf truncation; add (1<<7) before >>8 for round-to-nearest).
```
- Same alignment ruling as RX governs TX (the same SPORT/codec convention applies to both directions).
  If RX is IDENTITY then TX is IDENTITY (symmetric); if RX needs <<8 then TX needs >>8.
- **Where it lives**: after `fira_tfb_synthesize` returns `fout[64]`, in the deinterleave-to-TX-slot write
  (M2_SURVEY.md item 1.3: `[8ch][64] -> [64frame][8slot]`). One op per output sample. No frozen code touched.

### 2.3 ALIGNMENT RULING (left vs right) -- leading verdict + the board check that closes it
- **LEADING VERDICT [inferred, HIGH confidence]: LEFT-JUSTIFIED => RX/TX conversion = IDENTITY (zero shift).**
  Basis: (a) `ConfigData(..., ADI_SPORT_DTYPE_SIGN_FILL, 31, ...)` -- SIGN_FILL extends the sign through to
  bit 31, which is the left-justified MSB-at-bit31 convention; (b) ADI TDM/I2S codecs (ADAU1979/1962A) are
  MSB-first, data left-aligned in the slot (`SLOT_WIDTH=32, DATA_WIDTH=24`); (c) this is the same data path
  M1 passthrough already runs bit-for-bit, so any 24<->32 placement is already exercised by the live M1 PASS.
- **WHY IT IS NOT YET CLOSED [board-confirm]**: the precise bit position the SPORT driver/HRM places the
  24 valid bits at (and what the low 8 bits actually hold: hard 0, or sign/garbage that must be masked) is a
  driver+HRM property, not derivable from the .c alone. M2_SURVEY.md:139-142 already left this open.
- **HRM/driver grep to close it [board-confirm]** (CTO Windows CCES 2.12.1 tree):
  - `grep -n -A20 "DTYPE_SIGN_FILL\|adi_sport_ConfigData" "<CCES>/SHARC/include/drivers/sport/adi_sport.h"`
    -- read whether the word-length arg (31) + SIGN_FILL documents MSB-justified (bit31) or LSB-justified.
  - HRM "Serial Word Length (SLEN)" + "Data Type / sign-fill" sections: confirm received word is
    left-justified in the 32-bit memory word with sign at the configured MSB.
  - Cross-check on the LIVE board: dump a few `s_m1_rx_buf[0][...]` (R52: real 2D file-static symbol; the old name g_m1_rx_buf does not exist) words while feeding a known small DC/tone; if the
    24 valid bits sit at bit31..bit8 (low byte ~0) => LEFT-justified => IDENTITY confirmed; if at bit23..bit0
    (high byte = sign extension) => RIGHT-justified => need <<8 / >>8.
- **The board check is BACKED UP by the desktop bit-exact test (section 3)**: even before HRM is read, the
  test in section 3 mechanically PROVES which conversion is correct -- a wrong-justification conversion
  produces a DIFFERENT CRC. So alignment is settled either by HRM read OR by the failing/passing CRC.

---

## 3. BIT-EXACT VERIFICATION PLAN (CTO hard requirement -- critic can run this on desktop)

GOAL: a desktop-runnable test that PROVES the RX/TX conversion is correct by reproducing an R14 golden CRC
bit-for-bit, and FALSIFIES a wrong conversion (wrong shift/justification -> different CRC). NOT "should match".

### 3.1 KEY INSIGHT that makes the test sound (the golden input is FULL Q31, not 24-bit)
I parsed the frozen `chirp_input.h` (65536 int32):
- peak |value| = 620,622,774 = 0.289 x 2^31 (matches golden_ref.h header "0.289 chirp").
- **65282 of 65536 samples have NON-ZERO low-8-bits** -- i.e. the golden chirp is a FULL-32-bit-precision
  Q31 vector, NOT a 24-bit-left-justified one. The F4/F5 goldens were computed over this full-precision input.
- CONSEQUENCE (critical, prevents a false test): if you naively low-mask the chirp to 24-bit before feeding
  the conversion, you change the input vector and the CRC will mismatch FOR A REASON UNRELATED to the
  conversion. So the test must distinguish "conversion identity over the EXACT golden input" (which must
  reproduce the anchor) from "24-bit physical precision loss" (a separate, expected effect). The test below
  is structured to keep these separate: the bit-exact gate runs the conversion over the UNMODIFIED golden
  input so that a CORRECT (identity) conversion reproduces the anchor EXACTLY.

### 3.2 TEST CHAIN (desktop, links the conversion into the existing R14 harness)
Reuse the EXACT frozen R14 path so the anchor is meaningful. Build the bench (bench_main.c / fira_regression.c
core+FIRA path, or the desktop sbgold core path) with a thin conversion wrapper inserted at the two boundaries:
```
  [golden chirp int32]  --(RX align: q31 = align(rx))-->  [FIRA analyze/synthesize per-channel]
                                                          --(TX align: tx = unalign(fout))-->  [CRC]
  where align()/unalign() are the M2 conversion under test.
```
Two test modes:
- **MODE-IDENT (the hypothesis = LEFT-justified, zero shift)**: `align = identity`, `unalign = identity`.
  The chain is byte-for-byte the existing R14 chain -> subband CRCs MUST reproduce the anchors EXACTLY:
  - F4: `g_f4_crc_core == 0x2E0D8C6E` AND `g_fira_f4_crc == 0x2E0D8C6E`  (single channel, unity).
  - F5: `g_f5_crc_core[c] == g_f5_golden_crc[c]` for c=0..7 = {8E807729, B2F1E13F, 7B109C71, D7BD23E7,
    A000D606, 2403E085, B88D91B5, 2E0D8C6E}, all 8 DISTINCT, AND `g_f5_crc_fira[c] == g_f5_crc_core[c]`.
  PASS here = the IDENTITY conversion is bit-exact (the zero-conversion hypothesis is PROVEN over the golden).
- **MODE-SHIFT8 (the wrong alternative = RIGHT-justified mis-assumption)**: `align = (rx << 8)`,
  `unalign = (fout >> 8)`. This MUST CHANGE the subband CRCs (the analyze input is now 256x the golden) ->
  the anchors will NOT reproduce. **MODE-SHIFT8 is the negative control / falsifier**: it proves the test
  is sensitive to a one-shift conversion error (i.e. the test is NOT a telescoping/identity tautology).
  (Note: because TX `>>8` partially un-does RX `<<8` at the FULL-chain output, the END-TO-END 0x90556BC7
  could be MISLEADINGLY close -- which is exactly why the gate is the SUBBAND anchor, where the `<<8` is
  visible and uncancelled. This is the same telescoping-blindness that retired 0x90556BC7; see 3.4.)

### 3.3 INPUT VECTOR + WHICH ANCHOR
- INPUT VECTOR: the frozen `chirp_input.h` `CHIRP_INPUT[65536]` (the ONLY R14 golden input; do NOT regenerate
  -- it is frozen, FIRA_IMPL.md red-line). It is full-Q31; it IS the int32 RX vector for the test (treated as
  if it arrived left-justified from the codec). No separate "golden input" file is needed.
- ANCHOR TO COMPARE: the SUBBAND anchors (0.1 F4 + 0.2 F5 table), via the existing
  `fira_r14_regression()` / `fira_r14_regression_8ch()` self-check gates (`bench_main.c:202/216`). These are
  filter-dependent and placeholder-FAILing (bench_main.c:191), so they are real falsifiers, not tautologies.
- EXPECTED VALUES IF CONVERSION IS CORRECT (IDENTITY): F4 = 0x2E0D8C6E; F5 = the 8-row table above, exactly.
  If the conversion is wrong (e.g. <<8 mis-applied), at least one subband CRC differs -> FAIL -> the test
  has FALSIFIED the wrong conversion. **This is the bit-exact proof, runnable by critic, not "should match".**

### 3.4 SECONDARY (non-gating) full-chain sanity
- Also read `g_bench_result.crc32` (e2e 0x90556BC7) as a GROSS-corruption catch only. It is telescoping-blind
  (bench_main.c:193) so it does NOT gate the conversion ruling; it is a cheap extra signal. Gate = subband.

### 3.5 WHAT THE TEST DOES NOT CLOSE (honest scope)
- The desktop test proves the **arithmetic** conversion (shift/justification) is bit-exact against the golden.
  It does NOT prove the **board** SPORT actually delivers left-justified data (that is the 2.3 HRM/board read)
  -- it proves WHICH conversion is arithmetically correct FOR a given justification. The two together
  (HRM says "left-justified" + desktop says "identity reproduces anchor") close the ruling. If HRM says
  "right-justified", re-run MODE-SHIFT8 as the candidate and confirm IT reproduces the anchor with the codec
  re-modeled accordingly -- but per current evidence (SIGN_FILL-31) left/identity is the leading, testable case.
- The FIRA fixed-point INPUT FORMAT enum mismatch (`fira_tree.h:42-43`: ours = signed-fractional Q15xQ31 vs
  FIRA enum only UNSIGNED/SIGNED_INTEGER, Path-B runtime `FixedPointEnable(SIGNED_INTEGER)`, fira_tree.h:27-29)
  is a SEPARATE R14 board bit-by-bit item ("high bit-deviation risk, must board bit-by-bit", cannot confirm
  on desktop). The Q-boundary conversion (this survey) is the M1<->Q31 container alignment; the INTEGER-enum
  semantics is the FIRA-internal fixed-point mode. Both must hold for end-to-end correctness; this survey
  owns the former and flags the latter as already-tracked board work. [L1/EZKIT, R14]

---

## 4. HEADROOM / SATURATION (the conversion must not break the frozen headroom contract)
- `tree_filterbank.h:38-41`: half-band chain reserves -4.8 dB input headroom (=1/1.7309) so Sum|h_q15|=1.7309
  does not push Q31 requantization past full-scale; saturation clamp is the adversarial-peak backstop (PF-4).
- IMPLICATION for the RX->Q31 conversion: the IDENTITY conversion does NOT add gain, so it does not by itself
  break headroom. BUT the M2 beam weight (Dolph w[c] <= 1.0 at input-scale, h2:118) and any fan-out MUST keep
  the post-weight Q31 input within the -4.8 dB headroom (do not let Sum or peak exceed the 1.7309 full-scale
  budget). Final headroom calibration (real trigger rate at node (1)) is EZKIT [L1], not desktop.
- The frozen chirp peak is 0.289 x FS (-10.78 dBFS vs 2^31 by my parse; header says "-6dBFS + -4.8dB headroom"
  -- minor label nuance, the -10.78 = the COMBINED post-headroom level, both consistent at ~0.289 FS). The
  IDENTITY conversion preserves this exactly -> single-channel does not saturate (golden_ref.h header: SAT==
  UNSAT for single channel), consistent with the F4/F5 goldens being saturation-free at unity/per-weight.

---

## 5. OPEN ITEMS / board-confirm (collected)
- [board-confirm] SPORT justification (left vs right): HRM "SLEN"/sign-fill + adi_sport.h ConfigData doc +
  live `s_m1_rx_buf[0][...]` dump (2.3). Leading verdict LEFT => IDENTITY conversion; SHIFT8 is the falsifiable
  alternative. The desktop bit-exact test (section 3) settles WHICH conversion reproduces the anchor.
- [board-confirm] low-8-bits of the RX word (hard 0 vs sign/garbage to mask): if non-zero garbage, IDENTITY
  must add `& 0xFFFFFF00` mask; the bit-exact test (over the clean golden) does not exercise this -- it is a
  board-data hygiene item, separate from the arithmetic ruling.
- [board-confirm, already-tracked R14] FIRA fixed-point INTEGER-enum vs signed-fractional Q15xQ31
  (fira_tree.h:42-43) -- board bit-by-bit, not this survey's scope (3.5).
- [CTO] TX rounding policy (truncate vs round-to-nearest on bit7 before the 24-bit DAC drop) -- quality, not
  correctness (2.2).
- [CTO] where the beam weight/frac-delay lands (input-scale vs subband-level) -- M2 architecture, governs
  whether the conversion is fused into the weight load or stands alone (orthogonal to the alignment ruling).

---

## 6. SUMMARY (for report)
1. **CONVERSION POINT**: RX = at the `xw[]` load before `fira_tfb_analyze` (h2:117-118 region); TX = at the
   deinterleave write after `fira_tfb_synthesize` (fout -> tx slot). One op per sample each, fused into M2's
   board TU; frozen core untouched.
2. **ZERO-CONVERSION RULING [inferred, HIGH, board+test-confirmable]**: a 24-bit value left-justified to
   bit31 IS ALREADY a legal Q31 (high 24 bits = Q31 high bits, low 8 = 0). With DTYPE_SIGN_FILL-31
   (left-justified), **RX and TX conversion = IDENTITY (zero shift, zero mask)**. The falsifiable alternative
   (right-justified) needs RX `<<8` / TX `>>8`. Which one is correct is settled by (a) HRM/board read of
   justification AND (b) the desktop bit-exact test below -- NOT by assumption.
3. **BIT-EXACT TEST (critic-runnable, CTO hard requirement met)**: feed the frozen full-Q31 `chirp_input.h`
   through `[align -> FIRA analyze/synthesize -> unalign]` in the existing R14 harness, gate on the SUBBAND
   anchors. MODE-IDENT (identity conversion) MUST reproduce F4=0x2E0D8C6E and the F5 8-row table EXACTLY ->
   PASS proves zero-conversion is bit-exact. MODE-SHIFT8 (wrong `<<8`/`>>8`) MUST change at least one subband
   CRC -> FAIL proves the test is sensitive to a one-shift error (not a tautology). Gate = subband anchors
   (filter-dependent, placeholder-FAILing); the e2e 0x90556BC7 is a secondary sanity only (telescoping-blind).
4. **R14 CRC ANCHOR PROVENANCE**: F4 0x2E0D8C6E -- CTO transcript == repo (native: bench_main.c:47/191,
   fira_regression.c:92, dolph_f5_goldens.h:65, decisions_log.md:643). F5 = the 8-row per-channel table
   (dolph_f5_goldens.h:58-65, native), NOT a single constant (unweighted collapses all to 0x2E0D8C6E = FAIL).
   0x90556BC7 = retired telescoping-blind e2e, NOT the bit-exact criterion. No CTO/repo discrepancy found.

---

## HALT -- M2 Q-boundary survey + bit-exact test DESIGN. Awaiting critic bit-exact gate + CTO alignment ruling.

Do not predict the critic bit-exact verdict (critic runs the test in section 3). Frozen code zero-touch
(read-only here). Alignment justification + FIRA INTEGER-enum = board-confirm, not closed on desktop.
No commit. reviewer pending: critic gate (three-gate, POLICY v1.8 §4B).
dsp-algorithm @ claude-opus-4-8 / 2026-06-08.
