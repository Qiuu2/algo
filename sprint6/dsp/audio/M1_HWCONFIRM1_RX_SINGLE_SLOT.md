# M1 Hardware-Confirm 1: RX single-slot feasibility (research-only; HALT at conclusion)

> dsp-algorithm teammate, 2026-06-06. WO-S6-AUDIO M1, CTO architecture v-final (block-rate 750Hz/FRAME64,
> fan-out 1->8, RX window target = 1 slot, TX = TDM8 first-8 = 4096B, M1 no-pin). ASCII. No commit.
> NO implementation this round -- this is the feasibility ruling for the RX buffer size. Every fact carries
> datasheet page/table or example line. "Can't find -> say so", no invention.
>
> SOURCES: adau1979.pdf (ADC), Audio_Loopback_TDM (ALT, real 21569 loopback), M1_FACT_BASE.md (vetted facts).

================================================================================
## VERDICT: (c) local evidence is insufficient to fully decide -- but the two paths split cleanly
================================================================================
- **Path A (force the ADC to emit only 1 slot): RULED OUT by datasheet [datasheet].** The ADAU1979 has
  no 1-slot / TDM1 / mono-serial mode. Smallest frame = Stereo (2 ch) or TDM2.
- **Path B (ADC emits a multi-slot frame; SPORT captures only slot 0 via DMA): FEASIBLE IN PRINCIPLE,
  DEMONSTRATED-IN-KIND by ALT [L1] -- but the exact `SelectChannel(0,0)=1 slot` arg semantics + the
  resulting per-frame DMA word count are [board-confirm]** (reconstructed from call-site, not header body).
- Therefore the RX buffer cannot be hard-locked to 512B from local evidence alone; it is **512B IF Path B
  single-slot capture is confirmed on the install-tree header, ELSE the safe value follows the captured
  slot count.** Both candidate values are pinned below, plus the exact board-confirm checklist.

================================================================================
## PATH A -- ADC side (ADAU1979): can it emit just 1 slot?  ANSWER: NO
================================================================================
SAI_CTRL0 (Reg 0x05), field SAI[5:3] = "Serial Port Mode" -- the ONLY channel-count options are:
| SAI[5:3] | mode | channels on the wire |
|---|---|---|
| 000 | Stereo (I2S/LJ/RJ) | 2 |
| 001 | TDM2 | 2 |
| 010 | TDM4 | 4 |
| 011 | TDM8 | 8 |
| 100 | TDM16 | 16 |
[source: adau1979.pdf Table 20 "Bit Descriptions for SAI_CTRL0", P30 (pdftotext l.4365-4439)]
- There is **NO TDM1 / single-slot / 1-channel mode**. The minimum frame is 2 channels (Stereo or TDM2).
- "Stereo I2S as candidate": stereo is **2 channels**, not 1 -> does not achieve a 1-slot RX. (And the ADC
  is physically a 4-channel part; even stereo emits 2.) So Path A cannot give a 1-slot bus frame.
- CMAP note: channel->slot mapping (SAI_CMAP12 0x07 / CMAP34 0x08) lets you place which ADC channel lands
  in which slot, but does NOT reduce the FRAME to 1 slot -- the frame width is set by SAI mode above.
  [source: adau1979.pdf Table 22 (P32); M1_FACT_BASE sec 2 l.209]
=> The ADC cannot be told "send 1 slot only." Path A is closed. (Honest: this kills any plan that needs the
   physical TDM frame to be 1 slot wide. The product's 1-mono-source still rides a >=2-slot ADC frame.)

================================================================================
## PATH B -- SPORT side: capture only slot 0 of a multi-slot ADC frame?  FEASIBLE IN KIND
================================================================================
### B.1 ALT demonstrates SPORT-capture-window NARROWER than the ADC bus frame [L1]
Decoding ALT's own ADC registers + SPORT calls:
- ALT ADC SAI_CTRL0 = 0x1B -> SAI=011 = **TDM8** (8-slot frame on the wire); the ADAU1979 being a 4-ch part
  fills 4 of those 8 slots. [source: ALT.c:98 value 0x1B; decode vs adau1979.pdf Table 20]
- ALT SPORT RX: `adi_sport_ConfigMC(h, 1u, 7u, 0u, true)` (MC window) + `adi_sport_SelectChannel(h, 0u, 3u)`
  -> the SPORT MC window spans 8 slots but the channel-SELECT captures only slots 0..3 into the DMA buffer.
  [source: ALT.c:317,319; M1_FACT_BASE sec 2.2 l.127-128]
=> ALT is a working [L1] proof that "ADC frame has more slots than the SPORT DMA captures" is a legal,
   shipping configuration: the bus runs the full frame; SelectChannel(start,end) chooses the captured slots.
### B.2 Does SelectChannel(h, 0u, 0u) = capture slot 0 ONLY?  -> plausible but [board-confirm]
- The reconstructed prototype is `adi_sport_SelectChannel(h, uint8_t nStartCh, uint8_t nEndCh)`; ALT uses
  (0u,3u)=4 slots and (0u,11u)=12 slots. By the same start..end semantics, **(0u,0u) would select exactly
  slot 0 = 1 captured slot.** [source: M1_FACT_BASE sec 2.2 l.128 -- but tagged [L1-example-called] for the
  CALL, while the start/end MEANING is reconstructed from call-sites, NOT read from the header body
  (the real adi_sport.h body is not local; install-tree only). See B.4.]
- This is an INFERENCE from two data points ((0,3)->4, (0,11)->12); it is consistent but not header-proven.
  I will not state it as fact: it is "highly plausible, board-confirm."
### B.3 What "bus runs N slots, DMA captures 1" means for the RX buffer
- The TDM frame still clocks all its slots on the wire (unused/uncaptured slots cost BUS time, NOT core/DMA
  buffer space -- the high-Z/unused slots just pass). [source: adau1979.pdf P18 "unused slots ... high-Z";
  M1_FACT_BASE sec 2 l.210]
- The RX DMA buffer is sized by the CAPTURED slot count, NOT the frame width. If SelectChannel captures 1
  slot, the DMA writes 1 int32/frame -> per ping-pong half = FRAME(64) x 1 slot x 4B = 256B, x2 = **512B**.
- If the install-tree header forces capture to follow a minimum (e.g. the SAI minimum 2 for Stereo/TDM2, or
  a driver granularity), the captured count is 2 -> 64 x 2 x 4B x 2 = **1024B**.
### B.4 What is NOT locally decidable (the gap that makes this (c) not (a))
- The real BSP header bodies (adi_sport.h / adi_sport_2156x.h) are NOT in the repo -- only DESKTOP parse-
  stubs that explicitly self-label "NOT the real BSP header" and were NOT used as signature evidence.
  [source: M1_FACT_BASE sec 2 l.112, l.168] So `SelectChannel`'s exact start/end inclusivity and the minimum
  capturable slot count are reconstructed, not header-verified. Until the install-tree header is grepped,
  "(0,0) = 1 slot" is [board-confirm], not [L1].

================================================================================
## RX BUFFER VALUE (candidates -- CTO picks after board-confirm)
================================================================================
| case | captured RX slots | RX buffer (FRAME 64 x slots x 4B x pingpong 2) | when |
|---|---|---|---|
| **B-1slot (target)** | 1 (SelectChannel 0,0) | **512 B** | IF install-tree confirms (0,0)=1 captured slot |
| B-2slot (fallback) | 2 (Stereo/TDM2 min, or driver min) | **1024 B** | IF min capture = 2 |
| (ALT-style 4slot) | 4 (SelectChannel 0,3) | 2048 B | only if neither single nor pair works (deepest fallback) |
- CTO architecture target = 1 slot -> **512B is the value to lock IF Path B single-slot is confirmed.**
- The ADC bus frame width (>=2 slots, Path A) is INDEPENDENT of this buffer -- it does not change the RX
  DMA buffer; it only sets BCLK/bus occupancy. So the product's >=2-slot ADC frame does NOT force a bigger
  RX buffer; only the SPORT-captured slot count does.

================================================================================
## REMAINING board-confirm checklist (exact names, for the CTO bring-up grep)
================================================================================
1. **adi_sport_SelectChannel(h, nStartCh, nEndCh) inclusivity + minimum** -- open install-tree
   `<drivers/sport/adi_sport.h>` (CCES 2.11.1/2.12.1 SHARC/include): confirm (a) start/end are inclusive
   slot INDICES (so (0,0)=1 slot), (b) is a single-slot select legal (no driver minimum of 2). [decides
   B-1slot vs B-2slot] [source for header path: M1_FACT_BASE sec 2 l.168, ALT.d:40-41]
2. **adi_sport_ConfigMC(h, nMFD, nWindowSize, nWindowOffset, bEnable) exact field meaning** -- confirm
   nWindowSize=7u means "8 slots" (last-index vs count) and that the MC window can stay 8 (matching the ADC
   TDM frame) while SelectChannel narrows capture. [source: M1_FACT_BASE sec 2.2 l.127, flagged [inferred]]
3. **ADAU1979 SAI mode to use** -- pick the smallest ADC frame that the board codec + SRU support for a
   1-mono input: Stereo (SAI=000, 2ch) or TDM2 (SAI=001, 2ch). [source: adau1979.pdf Table 20 P30]
   (Either gives a >=2-slot bus frame; SPORT captures slot 0.)
4. **CCES version delta** -- ALT.d shows 2.11.1; brief says 2.12.1; confirm SelectChannel/ConfigMC
   signatures unchanged across the delta. [source: M1_FACT_BASE sec 2 l.112]

================================================================================
## ONE-LINE for decisions_log (draft, pending CTO RX-slot ruling + critic)
================================================================================
```
| M1 HW-confirm-1 RX single slot | Path A (ADC 1-slot emit) RULED OUT: ADAU1979 SAI[5:3] min = Stereo/TDM2,
  no TDM1 (adau1979.pdf Table 20 P30). Path B (SPORT captures slot0 of a multi-slot ADC frame) FEASIBLE
  IN KIND -- ALT [L1] proves SPORT capture-window (SelectChannel 0,3 = 4 of 8) narrower than the ADC TDM8
  bus frame (ALT.c:317,319); SelectChannel(0,0)=1 slot is highly plausible but [board-confirm] (header body
  not local). RX buffer = 512B IF (0,0)=1 captured slot confirmed on install-tree adi_sport.h; else 1024B
  (2-slot min). ADC bus frame width (>=2 slots) does NOT change RX buffer -- only captured slots do.
  HALT for CTO RX-slot ruling. critic gate pending.
```

> HALT: feasibility reported. Awaiting CTO ruling on RX slot count before any M1 implementation (separate WO).
