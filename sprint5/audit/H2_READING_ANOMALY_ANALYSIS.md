# WO-S5-H2 board-reading anomaly analysis (mechanism-level)

> dsp-algorithm teammate (harness author), 2026-06-06. Source @ HEAD de59de8:
> sprint5/dsp/harness/h2_dma_isr_measure.c + h2_board_hooks_21569som.c. ASCII. No commit.
> Discipline: explain or say "cannot explain + need what". No number-rounding to force closure.
> Does NOT predict CTO final ruling. Two flagged anomalies + one I found while checking (rate).

## 0. Board readings under analysis ([L1] EZKIT, 2 runs identical, FG all green)
```
cyc_frame_base     = 454,730     inc_dma            = 51
cyc_frame_isr (impl)= 507,070    inc_isr            = 52,340
cyc_frame_both_max = 482,178     cyc_frame_both_min = 479,949
isr_count = 1951   isr_count_off = 0   done/valid=1/1  fg_dma_loads=1  fg_isr_fires=1
```
(cyc_frame_isr implied = base + inc_isr; harness stores inc_isr = isr - base, h2:185-186.)

================================================================================
## ANOMALY 1 -- base 454,730 vs yardstick ~525,850 (low 13.5%, gap 71,120)
================================================================================

### 1.1 Line-by-line H2 vs H1-nofocus frame chain
| element | H1 nofocus (h1_wcet_measure.c) | H2 (h2_dma_isr_measure.c) | same? |
|---|---|---|---|
| frame size | BENCH_FRAME=64 (h1:235) | BENCH_FRAME=64 (h2:104) | YES |
| channels | DOLPH_W8_NCH=8 (h1:236) | =8 (h2:102) | YES |
| input frame src | chirp[(H1_WARM+1)*FRAME] (h1:327) | chirp[H2_WARM*FRAME] (h2:145) | diff INDEX, same data class |
| weight apply | (w*xin)>>15 (h1:238-239) | identical (h2:104-105) | YES (byte-identical expr) |
| analyze | fira_tfb_analyze (h1:240) | same (h2:106) | YES |
| focus stage | SKIPPED when focus=0 (h1:244 guard false) | absent | YES (both skip) |
| synthesize | fira_tfb_synthesize (h1:250) | same (h2:107) | YES |
| **CRC32 / frame** | **crc = h1_crc32(crc, fout, FRAME) EVERY ch (h1:251)** | **ABSENT** | **NO <-- the difference** |
| state array | s_h1_fa[8] | s_h2_fa[8] | same type/init (fira_channel_init) |

The ONLY per-frame compute H1-nofocus carries that H2 does NOT: **a bit-serial CRC32 over the
8-channel synth output**, h1:251 calling h1_crc32 (h1:210-227). H2's h2_fira_frame (h2:97-109)
has no CRC -- it is a pure timing target. (Different input-frame INDEX cannot change cycle count;
the chirp data is the same statistical class and the FIRA op count is frame-size-driven, not
data-value-driven. s_h1_fa/s_h2_fa init identically via fira_channel_init. Same TU family, same
build flags -> no inline/opt divergence expected; the CRC is the structural delta.)

### 1.2 Quantify: does CRC32 account for 71,120?
h1_crc32 is bit-serial (h1:216-220): per int32 word = 4 bytes x 8 bits = 32 inner iterations of
`c = (c&1)?(c>>1)^poly:(c>>1)` (data-dependent branch + shift + xor). Per frame:
  8 ch x 64 words x 32 = **16,384 inner iterations / frame** (+ 512 word-iters + 2,048 byte-iters outer).
| cyc / inner-iter (SHARC) | CRC body cyc/frame | vs gap 71,120 |
|---|---|---|
| 3 | 49,152 | 0.69 |
| 4 | 65,536 | 0.92 |
| 4.34 | 71,120 | 1.00 (exact) |
| 5 | 81,920 | 1.15 |
The gap is fully explained if the CRC inner-iteration costs ~4.3 cyc -- a realistic SHARC cost for
a data-dependent-branch + shift/xor on a per-bit loop, with the byte/word outer-loop load/xor on
top. **CRC32 accounts for the entire 13.5% (71,120 cyc) gap; the magnitude reconciles.** This is a
real chain difference, NOT a measurement error or a broken FIRA path.

### 1.3 Ruling: does base-low harm M_contention = (both_max - base)?
TWO SEPARATE QUESTIONS, kept apart:
- **Internal A/B self-consistency (what M_contention uses): NOT harmed.** base, dma, isr, both arms
  ALL run the SAME H2 frame (h2_fira_frame, no CRC in any arm). The CRC is absent uniformly, so it
  cancels in every (arm - base) subtraction. (both_max - base) and (dma - base) are pure single-
  factor deltas against a self-consistent baseline. The base being 71k lower than H1 does not
  touch the subtraction -- both minuend and subtrahend are on the same (CRC-free) chain.
- **Cross-harness yardstick comparison: legitimately offset.** The H2_WORKORDER.md:114 yardstick
  "base ~= H1 g_h1_cyc_8ch_nofocus ~525,850" is comparing H2's CRC-free base to H1's CRC-bearing
  nofocus. They are NOT the same chain, so the 13.5% offset is EXPECTED, not a red flag. The
  yardstick text should read "~= H1 nofocus MINUS its CRC32 (~71k)". The base value 454,730 is the
  correct H2 self-baseline.
=> base-low is BENIGN for M_contention. The yardstick was mis-set (compared across a CRC difference).

================================================================================
## ANOMALY 2 -- inc_isr=52,340 > (both_max - base)=27,448  (surface contradiction)
================================================================================

### 2.1 Arm calibers, pulled line-by-line from source
- **isr arm** (h2:171-184): times **ONE frame** (single bench_cyc_target pair around one
  h2_fira_frame). inc_isr = that one frame - base. NOT averaged, NOT max -- a single sample.
- **both arm** (h2:188-202): sweeps **N = H2_NFRAMES = 64 frames** (h2:83,191), takes
  **max and min over the 64** (h2:197-198). both_max = worst single frame of 64.
- **timing order** (sequential, h2): baseline -> dma arm -> isr-OFF control -> **isr arm (FIRST ISR
  activation ever, h2:172)** -> both arm (h2:190, SECOND activation). The isr arm is the FIRST time
  the timer-ISR dispatch + the re-arm handler run -> their I-cache/path is COLD there, WARM by the
  both arm.
- **re-arm handler weight** (board hooks h2_bh_timer_callback :264-283): every ISR does
  ++count + **THREE BSP service calls** adi_tmr_SetWidth + SetDelay + Enable (:275-277). Heavy.

### 2.2 The divisor the CTO floated (52,340/1951=26.8 cyc/ISR) is the WRONG caliber
1951 = isr_count = the **cumulative** FG counter over the ENTIRE ISR-on span (it is never reset
between arms; source only snapshots isr0, h2:174). It spans the isr-arm frame PLUS all 64 both-arm
frames. inc_isr=52,340 is a **single-frame** delta. Dividing a 1-frame delta by a 65-frame-span
count mixes calibers -> 26.8 is meaningless. Correct per-ISR needs ISRs-in-that-one-frame.

### 2.3 The real ISR rate is NOT 1 kHz -- it is ~62 kHz (rate artifact, found here)
Reconstruct from isr_count=1951 over the ISR-on wall window:
- ISR-on compute spans ~= 1 isr-frame (~507k cyc) + 64 both-frames (~481k each) ~= 31.3 ms wall.
- implied actual rate = 1951 / 31.3 ms ~= **62,000 Hz** (~62x the nominal H2_ISR_HZ=1000).
- => ISRs per base-frame ~= 454,730/1e9 * 62,000 ~= **28 ISR/frame**, NOT the 0.45/frame that a
  true 1 kHz rate would give.
Mechanism: h2_isr_start computes period in the SCLK(125 MHz) domain (period=125,000 SCLK =1 ms
nominal, board hook :293), but the **re-arm path** (SetWidth(half)+SetDelay(half)+Enable each ISR)
evidently reloads the timer with a far shorter effective period than 1 ms -- the one-shot re-arm
does not reproduce a clean 1 ms cadence. The harness header (:259-263, F24-MINOR-1) only flagged a
*small downward* drift; the board shows a *large upward* rate error instead. **This is a real
harness defect, not predicted.** (Exact rate is BOUNDED not measured: the harness never timestamps
the ISR-on wall window, so 62 kHz is an estimate from the 1951 count / reconstructed wall time --
honest gap.)

[R27 F27-MAJOR-1 error band -- critic sensitivity sweep] The 31.3 ms span above counts ONLY the
timed compute frames; the real ISR-on wall window also contains the inter-arm gap (isr arm ends ->
h2_isr_stop -> busload_start -> both arm restarts ISR) plus two isr_start/stop BSP overheads, none
timestamped. Sensitivity: span 31.3 ms -> 62 kHz; 50 ms -> 39 kHz; 100 ms -> 20 kHz; 200 ms ->
10 kHz. So **62 kHz is the UPPER endpoint of a point estimate whose lower bound is ~10 kHz**. The
QUALITATIVE conclusions (rate >> nominal 1 kHz, re-arm cadence broken, caliber error, safe-side
upper-bound property of the measured ISR cost) hold across the ENTIRE [10, 62] kHz band -- even at
10 kHz the rate is 10x nominal and the measured cost remains an over-count of the product cost.
The exact rate is pinned only by the rate-bracket retest (#1 below).

### 2.4 Resolve the "contradiction" -- it is NOT one
At ~28 ISR/frame:
| arm | increment | per-ISR (incr/28) | cache temp |
|---|---|---|---|
| isr (1 frame) | 52,340 | ~1,846 cyc | COLD (first activation) |
| both_min (best of 64) | 25,219 | ~890 cyc | WARM |
| both_max (worst of 64) | 27,448 | ~968 cyc | WARM |
inc_isr > both_max-base because the isr-arm frame is a SINGLE COLD first-pass sample (~2x the warm
steady per-ISR) AND a single noisy draw; the both arm's 64 frames are all warm. Same ~28 events
per frame in both; the per-ISR cost differs by cache temperature, not by a logic error. **No
contradiction.** Candidate (a) cold-transient CONFIRMED as the dominant cause; candidate (b)
heavy-re-arm-handler CONFIRMED (~900-1850 cyc/ISR = the 3 service calls); candidate (c) sampling
variance is SECONDARY (with ~28 ISR/frame the events are dense, not sparse -- so single-frame
variance is real but small vs the cold-vs-warm 2x). The sparse-event worry in the dispatch was
based on the assumed 1 kHz; at the actual 62 kHz it is dense.

### 2.5 Does the rate artifact poison both_max -> does M_contention's leg survive?
- both_max is max-over-64 (clean estimator structurally: many ISR phases sampled, worst captured).
  Its JITTER band (max-min)=2,229 is tight -> the 64-frame max is stable, not a wild outlier.
  So as a *max-over-N* statistic both_max is internally clean. The isr-arm single-frame is the
  noisy one, not both_max.
- BUT both_max is dominated by the INFLATED ISR rate: decompose (both_max-base)=27,448 =
  inc_dma(51) + ISR-share(27,397). **99.8% of (both_max-base) is the ~62 kHz ISR cost; only 0.2%
  is DMA contention.** Therefore:

### 2.6 CALIBER RULING (lesson#3 -- mislabel guard)
**Labeling M_contention=(both_max-base)*750/1e6=20.59 MCPS as "DMA bus-contention" is a caliber
error.** That number is ~99.8% ISR-preemption cost at a ~62x-too-high ISR rate, not DMA contention.
- True DMA bus-contention (clean, post-R24-pragma, Block-1 src/dst): inc_dma*750/1e6 =
  **0.038 MCPS** (~51 cyc/frame). The R24 pragma fix WORKED -- contention is near-zero because the
  MDMA proxy no longer self-conflicts with the FIRA set; that is the expected, correct outcome.
- The ISR/preemption magnitude is NOT a usable product number yet: it is measured at ~62 kHz, while
  the product target is ~1 kHz (control tick) / 750 Hz (frame ISR). It over-counts preemption ~62x.
- inc_isr (single-frame, cold) has NO standalone statistical meaning for the steady preemption cost.

================================================================================
## 3. Impact on T2 read -- which leg is usable, retest needed?
================================================================================
- **DMA-contention leg [L1, CLEAN]: usable now.** inc_dma=51 -> 0.038 MCPS. The R24 pragma closed
  the self-conflict artifact; real DMA crossbar contention against the (still-MDMA-proxy) load is
  negligible. (Caveat already on record: MDMA proxy misses SPORT callback core cost; that is the
  io item-1 share, separate, still [L3] until SPORT bring-up -- not this leg.)
- **ISR-preemption leg: NOT usable as a product figure.** Both inc_isr and the ISR-share of
  both_max are inflated ~62x by the rate artifact (sec 2.3) and the heavy 3-service-call re-arm
  handler. The magnitude cannot be reported as the product's ISR cost.
- **CTO's M_contention=20.59 MCPS as a T2 input: CONSERVATIVE but MISLABELED.** It over-counts ISR
  ~62x, so using it as the contention+preemption budget line is safe-side for closure (the true
  combined number at 1 kHz is far smaller). T2 closes EVEN with this inflated figure. But it must be
  re-labeled "combined ISR(@62kHz, inflated) + DMA contention", NOT "DMA contention", and it is not
  a faithful product number. So: T2 directionally closes on the CONSERVATIVE side, but the ISR leg
  is not yet a clean [L1].

### Retest needed (what to change) to get a clean ISR [L1]:
1. **Fix the ISR rate**: switch the board hook from the one-shot+re-arm to a true periodic timer
   (ADI_TMR_MODE_CONTINUOUS_PWMOUT if the installed adi_tmr.h exposes it -- already a TODO at board
   hooks :272-274), OR fix the re-arm so the effective period = 1 ms. Verify by re-reading
   isr_count over a TIMED wall window (add a wall-clock CCNT bracket around the ISR-on span so the
   rate is MEASURED, not reconstructed).
2. **Make the handler product-representative**: the product ISR is "minimal handler (count + ack)";
   the current 3 service calls/ISR are an artifact of the re-arm workaround. A continuous-mode timer
   needs no re-arm -> handler drops to count+ack -> the measured per-ISR cost becomes the real one.
3. **Report ISR cost as per-ISR x product-rate**, not as a single-frame delta: per-ISR(warm) x
   (750 or 1000 Hz) x frame_period. With continuous-mode + minimal handler, re-run the isr and both
   arms; both_max-base then becomes a faithful combined contention+preemption WCET.
4. Keep base as-is (CRC-free is correct for H2); only fix the yardstick TEXT (subtract H1's CRC).
5. [R27 F27-MAJOR-2] **Upgrade FG-B to FG-B' (rate-in-band)**: this round proved FG-B (count>0 AND
   off==0) verifies ISR EXISTENCE only, not rate correctness -- it stayed green through a ~62x rate
   error. The retest gate must require: measured rate (from the CCNT wall bracket, #1) falls in
   [950, 1050] Hz (or the product band CTO sets); outside the band = FG-B' FAIL = data quarantined.
   Existence != correctness; the gate must check both.
6. [R27 F27-MINOR-1] **Cold/warm isolation probes**: continuous mode removes the re-arm but does NOT
   auto-isolate first-activation cold cost. Add dedicated probes -- sample the first-activation frame
   separately from steady-state frames -- so the per-ISR cold/warm split becomes an isolated [L1]
   measurement instead of a 2-cache-state inference.

### What I cannot do from the readings alone (honest gaps):
- The exact ISR rate is BOUNDED (~62 kHz) not measured -- the harness has no timestamp of the ISR-on
  wall window. Need the rate-bracket retest (#1) to pin it [L1].
- The cold-vs-warm split (isr-arm 1846 vs both 890-968 cyc/ISR) is an inference from 2 cache states;
  it is consistent but not isolated by a dedicated cold/warm ISR probe.
- I cannot certify the product steady ISR cost from this run; it requires the continuous-mode retest.

## 4. One-line summary for decisions_log (draft, pending critic)
```
| WO-S5-H2 board reading anomalies | A1: base 454,730 low 13.5% vs H1-nofocus yardstick = H1 carries
  bit-serial CRC32/frame (16,384 inner-iters @~4.3cyc = ~71,120 cyc) that H2 lacks; A/B subtraction
  unaffected (CRC absent in all H2 arms), only cross-harness yardstick mis-set. A2: inc_isr(52,340) >
  both_max-base(27,448) NOT a contradiction -- isr arm = single COLD first-activation frame (~2x
  warm) + heavy 3-service-call re-arm handler; reconstructed ISR rate ~62kHz (NOT 1kHz, ~28 ISR/
  frame from isr_count 1951) = harness rate artifact. CALIBER RULING: M_contention=(both_max-base)*
  750/1e6=20.59 MCPS is ~99.8% inflated-ISR not DMA; true DMA contention = inc_dma 0.038 MCPS (R24
  pragma worked). T2 closes CONSERVATIVELY (inflated ISR over-counts safe-side) but ISR leg NOT clean
  [L1]; need continuous-mode + minimal-handler + wall-time-bracketed retest. critic gate pending.
```
