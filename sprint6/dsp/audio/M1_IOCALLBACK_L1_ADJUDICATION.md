# M1 io-callback [L1] adjudication + bench-pollution check (HALT)

> dsp-algorithm teammate, 2026-06-08. M1 passthrough is board-PASS (5 readouts [L1]). The io-callback CCNT
> probe measured g_m1_cb_cyc_last = 12839 cyc. Task: convert -> MCPS, ADJUDICATE the caliber (today's H2
> lesson: a raw aggregate must be mechanism-decomposed before labeling), update the H2 T2 reserve, and
> verify the compute line is un-polluted. ASCII. No commit. HALT for CTO. Does NOT predict CTO ledger ruling.
>
> SOURCES: m1_loopback_tdm.c/.h @ the R40-passed file; H2 T2 ledger = H2_PASSLINE_DERIVATION / DEC-S5-H2;
> bench state = git (this repo).

================================================================================
## TASK A.1 -- rate re-derivation (independent) + MCPS
================================================================================
Callback rate, re-derived from the SOURCE STRUCTURE (not taking PM's value on trust):
- RX is packed 1 word/frame (M1_RX_SLOTS=1); M1_RX_HALF_WORDS = M1_FRAME x 1 = 64 words/ping-pong half.
- The RX-done callback fires once per half completed; it processes M1_FRAME=64 frames (the `for f<M1_FRAME`
  loop, m1_loopback_tdm.c:197). So 64 audio frames per callback.
- callback rate = FS / frames_per_cb = 48000 / 64 = **750 Hz**.  [m1_loopback_tdm.h M1_FS_HZ/M1_FRAME]
  => INDEPENDENTLY CONFIRMS PM's 750 Hz (same as the H2 block-rate; opening 1).
- io-callback MCPS (whole bracket) = 12839 cyc x 750 Hz / 1e6 = **9.629 MCPS**.

================================================================================
## TASK A.2 -- CALIBER ADJUDICATION (the command of this WO)
================================================================================
### What the CCNT bracket actually encloses (read from the code, not assumed)
The bracket is `t0 = bench_cyc_target()` at m1_loopback_tdm.c:187 (FIRST line of the callback BODY, AFTER
function entry + the event-type check at :185) and `t1` at :212 (BEFORE the function returns). Therefore:

| cost component | runs where vs the t0..t1 bracket | in the 12839? |
|---|---|---|
| (a) SPORT ISR dispatch + callback INVOCATION + descriptor service + event-check (:185) | BEFORE t0 (entry) and AFTER t1 (return) | **NO** |
| (b) M1 app-load: fan-out 1->8 copy (64 frames x 8 stores) + FG non-zero scan + counters | INSIDE t0..t1 | **YES** |
| (c) the 2 bench_cyc_target() calls themselves (bracket self-overhead) | at t0 and t1 edges | partially (small) |

### RULING (corrects the WO's (a)+(b) framing -- stated honestly)
The WO framed 12839 as "(a) pure io-callback core + (b) M1 app load" and asked whether (a) can be split
out. **The code shows the opposite: 12839 = (b) app-load ONLY; (a) the io-callback CORE/dispatch cost is
NOT inside the bracket at all** (it is the SPORT driver's entry/exit, outside t0..t1). So:
- 12839 cyc / 9.629 MCPS = the **M1 application body** (fan-out + FG), NOT the io-callback core that H2's
  30-MCPS reserve was defined to cover.
- The pure io-callback CORE (a) -- SPORT dispatch + descriptor service = the H2 "codec/IO DMA" item-1 share
  -- is STILL UNMEASURED by this probe (it is outside the bracket). I will NOT hard-split it from 12839,
  because 12839 does not contain it. (To get (a) [L1], a SEPARATE probe is needed: bracket the WHOLE ISR
  including dispatch, or an empty-callback baseline. The harness has NO dispatch-only probe -- grep
  confirmed -- so (a) cannot be extracted from THIS run. Honest: not hard-splitting, not inventing.)

### Consequence for the H2 io-callback reserve (30 MCPS [L3])
The H2 30-MCPS io-callback reserve covers the per-block CALLBACK CORE cost = (a) dispatch + descriptor
service. The M1 probe measured (b) app-load = 9.629 MCPS, which is a DIFFERENT thing. Two honest readings:
- **Conservative (recommended) reading**: the 30-MCPS reserve covers (a) [still unmeasured]. The M1 probe
  does NOT directly retire it -- it measures (b). BUT it bounds the TOTAL callback differently: the full M1
  callback (a)+(b) at 750 Hz, IF (a) were comparable to (b), would still be well under 30 (9.63 is the
  measured (b) part; a minimal dispatch (a) is typically small vs a 64x8-store app body). So 30 still HOLDS
  as the (a) reserve, and the M1 run is INDIRECT EVIDENCE the whole callback is modest, not direct retirement.
- **Optimistic (NOT recommended) reading**: treat 9.629 as the whole-callback upper bound and replace the
  30 reserve. REJECTED here because 9.629 demonstrably EXCLUDES (a) -- using it to replace an (a)-reserve
  would UNDER-count (the caliber error H2/R27 warned against: label (b) as (a)). Do not do this.

### Three-state conclusion (per the WO's required format)
- measured <= reserve -> reserve HOLDS, lift confidence: **YES, but with the corrected caliber** -- the
  measured 9.629 MCPS is the M1 APP-LOAD (b), not the io-callback core (a). It is < 30 and is consistent
  with the whole callback being well under the 30 reserve, so the reserve HOLDS and the run RAISES confidence.
  It does NOT by itself promote the (a) reserve to [L1] (the bracket excludes (a)).
- measured > reserve -> FLAG T2 re-review: NOT triggered (9.629 << 30).
- This case = the first state (reserve holds), with the honest caveat that what was measured [L1] is (b),
  and (a) the pure io-callback core remains [L3] until a dispatch-inclusive probe runs.

### Note for M2 (honesty the WO asked for)
9.629 MCPS contains M1's fan-out 1->8 + FG -- M1-SPECIFIC app load. At M2 the callback body becomes the
FIRA beamformer (already counted elsewhere in core 347.45), and the M1 fan-out does NOT carry into M2. So
9.629 is an OVER-estimate of any per-callback APP cost that M2 inherits (M2 inherits ~0 of M1's fan-out).
Only the io-callback CORE (a) carries into M2 -- and (a) is exactly what this probe did NOT measure. So for
M2 the relevant number (a) is still pending a dispatch-inclusive probe.

================================================================================
## TASK A.3 -- T2 ledger, BOTH calibers (CTO picks)
================================================================================
H2 T2 worst-end allowance = (io-callback + O1 + I_cold) reserves on top of M_contention, must be
<= 210.19 MCPS (DEC-S4-CRITERION T2 worst). Current ledger sum 95.59 (all reserves [L3]).

| caliber | io-callback term | T2 reserve sum | vs 210.19 | note |
|---|---|---|---|---|
| **(I) conservative -- keep 30 reserve, M1 as side-evidence (RECOMMENDED)** | 30 [L3] (a) unmeasured | 20.59 + 30 + 15 + 30 = **95.59** | <= 210.19 | unchanged ledger; M1 9.629[L1] is SIDE EVIDENCE the callback is modest, raising confidence WITHOUT retiring the (a) reserve. Most robust: T2 stays conservatively closed. |
| (II) replace -- io reserve := measured | 9.629 [L1, but = app-load (b) NOT core (a)] | 20.59 + 9.63 + 15 + 30 = **75.22** | <= 210.19 | WIDER margin BUT MIS-CALIBERED: 9.629 is (b) app-load, the 30 reserve is (a) core. Replacing (a) with (b) under-counts (a). NOT recommended -- repeats the H2/R27 label error. |

LEAN: **(I) conservative** -- the WO's own preference and the caliber-correct choice. The M1 [L1] probe
proves the M1 app body is 9.629 MCPS and (by the 64x8-store structure) the full callback is plausibly modest,
which RAISES confidence that the 30-MCPS (a) reserve has ample headroom -- but does NOT retire it (the
bracket excluded dispatch). Keep 30, T2 stays conservatively closed at 95.59 <= 210.19. CTO rules the caliber.

(If CTO wants (a) [L1] retired too: spec a dispatch-inclusive probe -- bracket the whole ISR or add an
empty-callback baseline -- as a small M1 follow-up; do NOT hard-split 12839.)

================================================================================
## TASK B -- bench / compute-line pollution check
================================================================================
Repo compute line = CLEAN golden standard (git-verified):
- `git status --short sprint4/dsp/` -> EMPTY (zero changes to compute-line tracked files).
- The 5 TRACKED frozen files (under sprint4/dsp/core_only/) all have EMPTY `git diff` = unmodified:
  src/tree_filterbank.c, src/tfb_8ch.c, bench/golden_ref.h, bench/chirp_input.h, include/fir_coeffs_hb63.h.
- bench_main.c + bench_harness.c: TRACKED, empty diff = clean.
- ZERO modified/deleted tracked files anywhere this session (pure additions, all under sprint6/dsp/audio/).
- (`sprint3/dsp/tree_filterbank.c` shows untracked `??` -- it is a PRE-EXISTING untracked artifact, present
  in the session-start git status, NOT the tracked frozen file and NOT touched by me. The tracked frozen
  copy is sprint4/dsp/core_only/src/tree_filterbank.c, which is clean.)

### CTO recovery guidance (the repo is the golden master)
- The pollution is ONLY in the CTO's board-machine LOCAL workspace (the imported/copied bench project), NOT
  in the repo. The repo compute line is untouched.
- To recover on the board machine: DELETE the local polluted bench workspace project and re-checkout from
  git (`git checkout -- sprint4/dsp/` or re-clone / re-import the clean repo tree). Do NOT edit the repo --
  it is already the clean standard.
- The M1 work is a SEPARATE independent project (sprint6/dsp/audio/m1_cces_project/) and shares NO files
  with the bench compute line -- so M1 bring-up cannot have caused (and cannot fix) bench pollution. The
  two are isolated by design (route B value).

================================================================================
## SUMMARY (HALT)
================================================================================
- Rate 750 Hz (independently re-derived: FS 48000 / FRAME 64). io-callback = 12839 x 750 / 1e6 = 9.629 MCPS.
- CALIBER (corrected): 12839 = M1 APP-LOAD (b: fan-out 1->8 + FG), measured INSIDE the t0..t1 bracket. The
  io-callback CORE (a: SPORT dispatch + descriptor service = what H2's 30 reserve covers) is OUTSIDE the
  bracket -> NOT in 12839, cannot be hard-split from it (no dispatch-only probe -- honest, not invented).
- THREE-STATE: measured (9.629) <= reserve (30) -> reserve HOLDS, confidence RAISED -- with the caveat that
  the [L1] number is the app-load (b), and the (a) core reserve stays [L3] pending a dispatch-inclusive probe.
- T2 ledger: (I) conservative keep-30 = 95.59 (recommended; M1 as side-evidence); (II) replace-with-9.63 =
  75.22 (wider but mis-calibered, NOT recommended). Both <= 210.19. CTO rules the caliber.
- BENCH POLLUTION: repo compute line CLEAN (git: sprint4/dsp empty, all 5 frozen files unmodified, zero
  tracked edits). Recovery = delete local polluted workspace + re-checkout from git; repo needs no change.
- HALT: awaiting CTO ledger-caliber ruling. No CTO ruling predicted.
