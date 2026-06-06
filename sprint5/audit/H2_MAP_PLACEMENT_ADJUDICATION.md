# WO-S5-H2 R24-gate .map placement adjudication (s_bh_src/dst vs s_h2_fa)

> dsp-algorithm teammate, 2026-06-06. Adjudicates the R24 F24-MAJOR-1 measurement-validity gate:
> are the MDMA busload proxy buffers (s_bh_src/dst) in the SAME physical RAM block as the FIRA
> working set (s_h2_fa)? If yes, inc_dma measures a self-conflict artifact, not crossbar contention.
> NOT a board-result prediction. Pending critic gate before it counts. ASCII only. No commit.

## 0. Inputs (all [L1])

Board .map evidence (CTO, bench_core_only.map.xml, CCES 2.12.1 rebuild, 2026-06-06):
```
s_bh_src  @ 0x25fe88  size 0x1000   end 0x260e87
s_bh_dst  @ 0x260e88  size 0x1000   end 0x261e87
s_h2_fa   @ 0x261ee0  size 0x47a0   end 0x26667f   (FIRA working set, FiraChannelState[8])
```
Span under question: 0x25fe88 .. 0x26667f (top = s_h2_fa end). CTO note: dst_end 0x261e87,
fa_start 0x261ee0, gap = 0x58 bytes -> suspiciously adjacent.

## 1. Section / physical-block adjudication (NOT by address contiguity alone)

### 1a. Chip memory-map boundaries -- authoritative source
ADSP-21569 default app.ldf MEMORY{} block, byte-addressed (BW) view, [L1]:
- File: `knowledge_base/ezkit/vendor_docs/cces_examples/code/Power_On_Self_Test/EZ-Board/21569/sharc/system/startup_ldf/app.ldf`
- `:118` comment: "The ADSP-2156x SHARC+ cores have 5 Mbit L1 RAM split over four blocks."
- `:142` comment: "L1-Block 0 RAM (1.5 MBit)"
- `:144` `mem_block0_bw  { TYPE(BW RAM) START(0x002403f0) END(0x0026ffff) WIDTH(8) }`  <- L1 Block 0
- `:146/:151` `mem_block1_bw { ... START(0x002c0000) END(0x002effff) }`               <- L1 Block 1
- `:153/:158` `mem_block2_bw { ... START(0x00300000) END(0x0031ffff) }`               <- L1 Block 2
- `:160/:163` `mem_block3_bw { ... START(0x00380000) END(0x0039ffff) }`               <- L1 Block 3
- `:165/:176` `mem_L2_bw     { ... START(0x20000000) END(0x200f9fff) }`               <- L2 (0x2000_0000)
The FIRA Performance build app.ldf (the build family the bench derives from) has the IDENTICAL
block layout (`.../EE408V02/ADSP_2156x_FIRA_Performance/system/startup_ldf/app.ldf:143-178`),
so the boundaries above govern the bench build too.

Cross-check vs datasheet: `bsp/datasheets/ADSP-2156x-Datasheet-EN.pdf` / the 21569 HW Reference
(`bsp/hw_reference/ADSP-21569 SHARC+ Processor Hardware Reference.pdf`) describe the 5 Mbit L1
as four blocks; the exact byte-window START/END that the linker actually enforces is the .ldf
MEMORY{} above (the .ldf is the binding boundary the .map addresses are placed against). The
.ldf is the authority used for the boundary numbers; datasheet/HWref corroborate the 4-block split.

### 1b. Which MEMORY segment each buffer lands in (numeric, vs the .ldf boundary)
L1 Block 0 window = 0x002403f0 .. 0x0026ffff. L1 Block 1 window = 0x002c0000 .. 0x002effff.
| symbol   | start    | end      | inside Block0 (0x2403f0..0x26ffff)? |
|----------|----------|----------|--------------------------------------|
| s_bh_src | 0x25fe88 | 0x260e87 | YES |
| s_bh_dst | 0x260e88 | 0x261e87 | YES |
| s_h2_fa  | 0x261ee0 | 0x26667f | YES |
All three (and their full spans) are >= 0x2403f0 AND <= 0x26ffff -> all in `mem_block0_bw`.
None reaches 0x2c0000 (Block 1 start). The "address contiguity" the CTO flagged is therefore
NOT a near-boundary coincidence: they are not merely adjacent, they are co-resident well inside
ONE MEMORY segment with ~0x9980 bytes of headroom to the Block-0 end.

## 2. RULING: SAME physical RAM block

s_bh_src, s_bh_dst, and s_h2_fa are ALL in `mem_block0_bw` = **L1 Block 0** (single physical RAM
block). Adjudicated by the dual test the CTO required:
1. .ldf section boundary: one MEMORY segment contains all three spans (sec 1b).
2. chip memory-map block boundary: that segment's [0x2403f0, 0x26ffff] is the L1 Block 0 window
   (app.ldf:142-144, "L1-Block 0 RAM"); next block (Block 1) does not start until 0x2c0000.
Both tests agree -> SAME block, not merely contiguous addresses.

=> **R24 gate = FAIL.** With the MDMA proxy source/dest and the FIRA working set in the same L1
block, `g_h2_inc_dma` would capture intra-Block-0 single-port bank conflict between the MDMA
engine and the core's FIRA accesses -- an artifact the PRODUCT does not have (the product's
SPORT-PDMA codec buffers are a SEPARATE allocation from the FIRA working set) -- instead of, or
contaminating, the true system-crossbar contention the WCET wants. **pragma placement IS required.**

## 3. Fix: source-side #pragma section (the .ldf is FROZEN, read-only -- not edited)

Target section name (must exist in the .ldf, verified): **`seg_l1_block1`** -- the input section
that the .ldf routes into `mem_block1_bw` (L1 Block 1), a DIFFERENT physical block from Block 0:
- app.ldf `:460` `INPUT_SECTIONS( $OBJS_LIBS(seg_l1_block1 seg_int_data) ) } > mem_block1_bw`
  (and :471/:484/:491/:497/:504/:510/:517 -- seg_l1_block1 routes to mem_block1_bw throughout).

Pragma (placed in h2_board_hooks_21569som.c Block 1, immediately before each buffer def; the
pragma applies to the next definition only, so one pragma per buffer -- matches the proven ADI
usage pattern in sec 3b):
```c
#pragma section("seg_l1_block1")
static uint32_t  s_bh_src[H2_BH_BLOCK_WORDS];   /* MDMA proxy source  -> L1 Block 1 (NOT Block 0 = FIRA set) */
#pragma section("seg_l1_block1")
static uint32_t  s_bh_dst[H2_BH_BLOCK_WORDS];   /* MDMA proxy dest    -> L1 Block 1 */
```
s_h2_fa stays unpragma'd -> it remains in Block 0 (its current .map home). Result: MDMA proxy
buffers in Block 1, FIRA working set in Block 0 -> different physical blocks -> no intra-block
self-conflict; inc_dma now reflects cross-block / crossbar arbitration = the product-representative
contention. Bring-up MUST re-check the rebuilt .map to confirm s_bh_src/dst land >= 0x2c0000 and
s_h2_fa stays < 0x270000 (the F24-MAJOR-1 placement-verify obligation persists; this pragma is the
fix, the .map re-read is the proof).

### 3a. Why seg_l1_block1 is on the SAME bus segment as the product SPORT-PDMA path
- Product audio DMA path (DOC-S4-IO-01): ADAU1979 -> **SPORT4 TDM -> 21569** -> SPORT4 -> ADAU1962A.
  The SPORT4 peripheral DMA (PDMA) moves the codec ping-pong buffers across the DM-side system bus
  / crossbar into L1 (or L2) on-chip RAM; the contention mechanism is the DMA engine arbitrating for
  the same crossbar/bank port the SHARC+ core uses (h2_dma_isr_measure.c header, sec 2.1).
- L1 Block 1 is reached by the SAME DM-bus crossbar that serves SPORT-PDMA transfers into on-chip
  L1; it is a peer L1 block to Block 0, not a different bus tier. So an MDMA stream targeting Block 1
  exercises the same arbitration class as the SPORT-PDMA codec path, while NOT sharing Block 0's
  single-port with the FIRA working set. (If a future bring-up wants the proxy on the EXACT product
  buffer block, it pins to whichever block the SPORT RX/TX buffers land in; Block 1 is the correct
  "same-bus-class, different-block-from-FIRA" choice given FIRA set is in Block 0.)

### 3b. #pragma syntax + target-section name are [L1] proven (ADI's own accelerator examples)
The ADI 2156x FIRA/IIRA accelerator benchmark sources place the ACCELERATOR's DMA input/output/coeff
buffers with exactly this pragma + section:
- `bsp/app_notes/fira_accel_code/EE408V02/ADSP_2156x_FIRA_Performance/src/FIR_Throughput_21569.c`
- `bsp/app_notes/fira_accel_code/EE408V02/ADSP_2156x_IIRA_Performance/src/IIR_Throughput_21569_V2.c`
  [R26 F26-MINOR-1 attribution note: the line-by-line quote below is from the IIRA file; the FIR file
   uses the SAME pragma + section name but a different buffer order/line numbers (InputBuff/CoeffBuff/
   OutputBuff) -- no impact on the conclusion.]
  `:23 #pragma section("seg_l1_block1")` / `:24 float OutputBuff[MAX_WINDOW_SIZE];`
  `:26 #pragma section("seg_l1_block1")` / `:27 float InputBuff[MAX_WINDOW_SIZE];`
  `:29 #pragma section("seg_l1_block1")` / `:30 float CoeffBuff[7*MAX_BIQUADS];`
  (`:30 //#pragma section("seg_l2_dmda_bw")` -- a commented L2 alternative, confirming an L2 section
   name `seg_l2_dmda_bw` exists too, available if bring-up prefers L2 placement.)
This is the same buffer CLASS (accelerator-DMA data) as the H2 proxy -> the pragma form and the
`seg_l1_block1` name are board-proven [L1], not invented.

## 4. Comparability check (my own harness): does moving src/dst perturb base/dma/isr A/B?

Moving ONLY s_bh_src/dst to Block 1 does NOT break the A/B subtraction purity:
- The baseline (`g_h2_cyc_frame_base`) and ALL three measured frames (dma / isr / both) run the SAME
  FIRA chain over the SAME s_h2_fa working set, which STAYS in Block 0 in every arm. The FIRA frame's
  own memory layout is therefore identical across baseline and loaded arms -> baseline is unchanged
  by the move.
- The busload buffers (src/dst) are touched ONLY by the MDMA engine, and ONLY in the dma/both arms
  (h2_busload_start..stop). They are not read/written by h2_fira_frame at all. So relocating them
  changes WHERE the proxy load lands (the intended fix), not the FIRA compute path.
- Net: `inc_dma = dma - base` and `inc_isr = isr - base` remain pure single-factor deltas; the only
  thing that changed is that the dma factor now exercises cross-block arbitration (product-like)
  instead of intra-Block-0 self-conflict (artifact). The move IMPROVES validity without disturbing
  the subtraction. Frozen files untouched; only h2_board_hooks_21569som.c Block 1 gains 2 pragmas.

Honest residual: this is a static-placement adjudication from the .ldf + .map; the rebuilt-with-pragma
.map must be re-read on the bench to confirm the new addresses (Block 1 >= 0x2c0000) and that the
linker honored the pragma. No board contention number is predicted here.

## 5. Answers to the CTO's 4 questions (summary)
1. Section/RAM: 0x25fe88..0x26667f all sit in `mem_block0_bw` = L1 Block 0 (app.ldf:144,
   START 0x2403f0 END 0x26ffff; "L1-Block 0 RAM" :142). Not L2 (L2 starts 0x2000_0000).
2. Same physical block? YES -- dual-tested (one .ldf MEMORY segment AND inside the chip L1-Block-0
   window; next block starts 0x2c0000). Not concluded from contiguity alone.
3. Same block -> R24 FAIL -> pragma REQUIRED. Fix: `#pragma section("seg_l1_block1")` before
   s_bh_src and before s_bh_dst (routes to mem_block1_bw = L1 Block 1, app.ldf:460/:471; pragma
   form + section name proven in ADI FIRA/IIRA examples). Same-bus-class as SPORT-PDMA (peer L1 over
   the same DM crossbar), different block from the FIRA set (which stays in Block 0). .map re-read at
   bring-up to confirm.
4. Not applicable (it is the same block, not a cross-boundary split).
```
| WO-S5-H2 R24 .map gate | RULING: s_bh_src/dst + s_h2_fa all in L1 Block 0 (mem_block0_bw
  0x2403f0..0x26ffff, app.ldf:144) -> SAME block -> FAIL -> fix = #pragma section("seg_l1_block1")
  on s_bh_src/dst (-> L1 Block 1, different block, same DM-crossbar class as SPORT-PDMA). Baseline/
  A-B purity preserved (FIRA set stays Block 0). .map re-read pending at bring-up. critic gate pending.
```
