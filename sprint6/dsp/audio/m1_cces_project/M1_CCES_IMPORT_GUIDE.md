# M1 CCES project -- dummy-proof import guide (WO-S6-AUDIO-M1-PROJ, scheme X)

> dsp-algorithm teammate, 2026-06-08. A one-click-importable CCES project for the M1 passthrough loopback.
> ASCII. No commit (PM lands after critic R41).
>
> *** HONESTY (read first): this machine has NO CCES -- the project was assembled + DESKTOP SYNTAX-SMOKED
> only (gcc -fsyntax-only on the M1 source TUs with mock BSP). The FIRST real cc21k compile / link /
> system.svc-consistency check happens ON THE BOARD MACHINE. This guide does NOT claim "guaranteed one-click
> build"; it claims "assembled to import cleanly; first true build is board-side." Board-side gaps listed at
> the end. ***

## What this project is
A THIN standalone CCES SHARC project (ADSP-21569, EV-SOMCRR-EZKIT) that builds ONLY the M1 audio loopback.
It contains NO FIRA / compute-line code -> M1 bring-up cannot perturb the frozen compute golden environment.
Project name: **M1_Loopback** (renamed from ALT to avoid an import name-clash with the KB Audio_Loopback_TDM).

## Import steps (File -> Import, click by click)
1. CCES menu: **File -> Import...**
2. **General -> Existing Projects into Workspace** -> Next.
3. **Select root directory -> Browse...** -> choose:
   `.../sprint6/dsp/audio/m1_cces_project`
4. The Projects list should show **M1_Loopback** (checked).
5. **Copy projects into workspace**: CHECK it (recommended) -- copies the project into your CCES workspace
   so the original repo folder stays clean. (Unchecked = build in-place in the repo; also fine.)
6. **Finish**.
7. Build: right-click **M1_Loopback -> Build Project** (Debug config).
8. Connect EZKIT + emulator -> **Run / Debug** -> read g_m1_* at idle (see CTO action list below).

## What is already configured in the project (you should NOT need to touch)
- **LDF** = `system/startup_ldf/m1_app.ldf` (the M1 .ldf; ALT's app.ldf was REMOVED so there is no
  ambiguity). The `.cproject` Custom-LDF (-T) points at m1_app.ldf for BOTH Debug and Release.
- **Preprocessor macros** `M1_TARGET_BOARD` + `TARGET_SHARC` are in the `.cproject` compiler defs for BOTH
  Debug and Release (the board-guarded code is `#if M1_TARGET_BOARD && TARGET_SHARC`). Plus the ALT defaults
  `_DEBUG`/`CORE0` (Debug) and `NDEBUG`/`CORE0` (Release).
- **Sources auto-discovered** (`.cproject` sourcePath: root + system/): everything in `src/` and `system/`
  compiles automatically. `src/` holds the M1 sources; ALT's main file is NOT present (no duplicate main()).
- **adi_initComponents** (system/adi_initialize.c, GUI-generated -- reused verbatim, cannot regenerate
  without CCES) runs adi_sec_Init + adi_initpinmux + adi_SRU_Init. NOTE: adi_SRU_Init is fully guarded by
  `#if defined(SRU_FULL_INIT)` -- WITHOUT that macro it does NO routing (only DAI input-enable), which is
  why m1_main.c calls m1_sru_init() to do the actual R39 routing. Do NOT define SRU_FULL_INIT (its
  GUI-default routing differs from R39 and would fight m1_sru_init).
- **Driver-source links** (`.project` linkedResources): adi_sport.c / adi_twi.c / adi_pdma_2156x.c /
  adi_spu.c are linked from the CCES install tree (`CCES/SHARC/lib/src/...`). On import CCES resolves the
  `CCES` path variable to your install. If a link shows broken (red), see fallback F3 below.

## Project file tree (what is what)
```
m1_cces_project/
  .project                       <- ALT skeleton, RENAMED to M1_Loopback; ALT src-file links REMOVED;
                                    only CCES driver-source links kept. [ALT base, edited]
  .cproject                      <- ALT skeleton; LDF -> m1_app.ldf; +M1_TARGET_BOARD +TARGET_SHARC. [ALT base, edited]
  system.svc                     <- ALT GUI system config (codec/SPORT/pinmux/SRU). [ALT base, reused verbatim]
  src/                           <- REAL folder (ALT's was a virtual link to a sibling ../src/)
    m1_main.c                    <- M1 thin main (init -> SRU -> codec-enable -> loopback -> idle). [M1, R40-passed]
    m1_sru.c                     <- SRU routing glue (R39 table). [M1]
    m1_softconfig.c              <- F-SRU-1 explicit codec enable (U6 @ TWI2 0x22). [M1]
    m1_cyc.c                     <- bench_cyc_target() CCNT shim. [M1]
    m1_loopback_tdm.c / .h       <- codec + SPORT TDM ping-pong module. [M1, R37/R38-passed]
    ADAU_1962Common.h / 1979Common.h  <- codec register-name macros. [ALT, define-only, reused verbatim]
  system/
    adi_initialize.c / .h        <- adi_initComponents (GUI-gen, REUSED verbatim -- cannot regen w/o CCES)
    sru/sru_config.c             <- GUI SRU (no-op without SRU_FULL_INIT). [ALT verbatim]
    SoftConfig_*_ADC_DAC.c       <- ALT carrier soft-switch. DEAD CODE (not called; m1_softconfig replaces it).
    SoftConfig_*_ADAU_Reset.c    <- ditto, dead code. [ALT verbatim, harmless -- see ruling below]
    pinmux/GeneratedSources/pinmux_config.c  <- GUI pinmux. [ALT verbatim]
    drivers/.../*_config_2156x.h <- SPORT/TWI/PDMA static config (MCPDE=1 etc). [ALT verbatim]
    services/pdma/adi_pdma_config_2156x.h
    startup_ldf/m1_app.ldf       <- M1 LDF (NEW; ALT app.ldf removed)
    startup_ldf/app_startup.s / app_IVT.s / app_heaptab.c  <- GUI startup. [ALT verbatim]
```
Build artifacts (Debug/, *.doj, *.dxe, *.d) were NOT copied -- CCES regenerates them on first build.

## RULING: ALT's system/SoftConfig_*.c -- kept as DEAD CODE (not excluded)
ALT's `ConfigSoftSwitches_ADC_DAC` / `_ADAU_Reset` symbol names do NOT collide with my
`m1_softconfig_enable_codecs` (verified: src and system symbol sets are disjoint). They are never called
(ALT's main, which called them via the also-commented-out Switch_Configurator, is gone). So they compile as
harmless dead code. This is the lowest-change choice (per the WO preference).
[R41 F41-MINOR-1 PRECISION] These two .c files are actually LINK-REFERENCED, not pure dead code:
m1_loopback_tdm.c:372-373 takes their address (`(void)ConfigSoftSwitches_ADC_DAC;`) to anchor the symbols.
=> Do NOT simply DELETE the SoftConfig_*.c files (that gives an unresolved-symbol LINK error). If you must
remove them, also remove the `(void)ConfigSoftSwitches_*;` anchor lines first. Excluding-from-build below
is fine only if you also drop those anchor lines; otherwise leave the files in (the recommended default).
If you ever want them gone (after removing the anchor lines):
Project Explorer -> right-click each SoftConfig_*.c -> Resource Configurations -> Exclude from Build.
(M1's codec enable is m1_softconfig.c, F-SRU-1, called explicitly from m1_main.c.)

## Fallback if something sticks (CCES GUI, a few clicks each)
- **F1 -- M1 sources not compiled (auto-discover missed them)**: Project Properties -> C/C++ General ->
  Paths and Symbols -> Source Location -> ensure the project root (and `system`) are source folders; or just
  confirm src/*.c show a build icon. (sourcePath name="" + name="system" already covers this.)
- **F2 -- duplicate main() link error**: means an ALT main slipped in. Project Explorer -> find any
  Audio_Loopback_TDM.c -> right-click -> Exclude from Build (or Delete the link). This project ships WITHOUT
  it, so this should not happen -- but that is the one-click fix if it does.
- **F3 -- broken driver-source links (red, "CCES" unresolved)**: Window -> Preferences -> C/C++ -> Build ->
  Build Variables (or Linked Resources path var) -> set `CCES` to your CrossCore install root
  (e.g. C:\Analog Devices\CrossCore Embedded Studio 2.12.1). Re-import or refresh. Alternatively add the
  drivers via the System Configuration (system.svc) "Add driver" UI so CCES links them itself.
- **F4 -- LDF still ALT's**: Project Properties -> C/C++ Build -> Settings -> SHARC Linker -> LDF
  Preprocessing -> Custom LDF (-T) -> confirm it is `${ProjDirPath}/system/startup_ldf/m1_app.ldf`.
- **F5 -- macro not applied**: Project Properties -> C/C++ Build -> Settings -> SHARC C/C++ Compiler ->
  Preprocessor -> Preprocessor definitions -> confirm `M1_TARGET_BOARD` and `TARGET_SHARC` are present (they
  are in .cproject; this is the manual re-add if a CCES version drops them on import).
- **F6 -- header name drift (2.11.1 ALT vs 2.12.1 install)**: if a `<drivers/sport/adi_sport.h>` or
  `<services/...>` include is not found, the installed header name differs -> Project Properties -> Paths
  and Symbols -> Includes, or fix the #include in the M1 source to the 2.12.1 name (board-confirm A2).

## Honest gaps -- what the BOARD machine will first reveal (not predicted here)
- **First true cc21k compile/link**: desktop gcc syntax-smoke != CCES build. Real header names (2.12.1),
  intrinsics, LDF section fit, and the system.svc<->code double-config (SPORT4 A/B, TWI2, SPU) are
  board-first. The system.svc was reused from ALT (same chip/board/codecs) so it SHOULD match, but
  svc-vs-code consistency is a board-machine check.
  [R41 F41-MINOR-2] RECOMMENDED first step after import: Build Debug immediately -- if CCES regenerates
  from system.svc or flags a svc mismatch, you see it at once (before chasing other issues). The svc is
  the highest board-first-reveal risk in this assembly; surface it first.
- **A2 header-name drift** (adi_sport.h vs adi_sport_2156x.h etc) -- the #1 cc21k-error risk (R25 lesson).
- **system.svc driver versions** vs the M1 source calls (sport 1.0 / twi 2.0 / spu 1.0 / pdma 1.0 per the
  .cproject macros) -- confirm the install has these.
- **SelectChannel single-slot driver minimum** (grep G1-G2) -> M1_RX_SLOTS 1 (512B) or 2 (1024B).
- DAI1-pin->codec physical traces (carrier schematic); MCLK 12.288 MHz source; SRU effect latency.

## WO-S6-M2 -- building the FIRA beam in-loop (M2_FIRA_INLOOP=1)
This same project builds EITHER M1 (transparent passthrough) OR M2 (FIRA broadside beam), selected by ONE
compiler macro. M1 is the default (no macro) -> the board-PASS passthrough is never lost.

To build **M2** (FIRA beam in-loop), do BOTH of these in the CCES project (these are project-wiring steps,
NOT code edits -- the source already has the M2 path behind `#if M2_FIRA_INLOOP`):
1. **Define the macro**: Project Properties -> C/C++ Build -> Settings -> SHARC C/C++ Compiler ->
   Preprocessor -> add `M2_FIRA_INLOOP=1` (Debug and Release). (M1 build = simply omit it.)
2. **Add the FROZEN FIRA call surface** (read-only; M2 CALLs, never edits -- iron-rule zero-touch):
   - **Include dirs** (Paths and Symbols -> Includes -> add):
     `${repo}/sprint4/dsp/fira`, `${repo}/sprint4/dsp/core_only/src`, `${repo}/sprint4/dsp/core_only/include`
     (these resolve fira_tree.h, dolph_w8_q15.h, tree_filterbank.h, fir_coeffs_hb63.h).
   - **Link the frozen sources** (add as linked-resource source files, do NOT copy/edit):
     `sprint4/dsp/fira/fira_tree.c`, `sprint4/dsp/core_only/src/tree_filterbank.c`,
     `sprint4/dsp/core_only/src/tfb_8ch.c`. fira_tree.c needs `FIRA_USE_REAL_ADI_FIR_HEADER` defined for the
     real adi_fir.h path -- add it to the compiler defs FOR THE M2 BUILD (board-confirm the installed
     `<drivers/fir/adi_fir.h>` exists, A2 header-drift class).
   NOTE: the M1 transparent build needs NONE of step 2 -- those dirs/sources are pulled only under the macro.
3. **Pin proof**: the M2 build pins s_m1_rx_buf / s_m1_tx_buf / s_m2_fa to L1 Block 1 via
   `#pragma section("seg_l1_block1")` (already in the .c). After the M2 build, **re-read the .map** and
   confirm all three land at >= 0x2c0000 (Block 1) -- see the m1_app.ldf banner + the honest gap below.

## CTO on-board action list
1. Import per the steps above; **Build Project (Debug)**. Expect possible first-build fixes from F3 (CCES
   path var) / F6 (header drift) -- those are normal for a hand-assembled cross-machine project.
   For M2: add the macro + FIRA include/link wiring above first.
2. **grep G1-G2** in the install `adi_sport.h`: single-slot SelectChannel accepted? -> keep M1_RX_SLOTS=1
   (512B) or set =2 (1024B) in m1_loopback_tdm.h.
3. **Run/Debug + read at idle (M1 build)** (free-run, NO callback breakpoints): g_m1_main_pwrinit_rc /
   softcfg_rc / init_rc all 0; g_m1_valid=1; g_m1_fg_stream_live=1 (green ONLY if blocks grew AND non-zero
   audio); g_m1_rx_block_count / tx growing; g_m1_cb_cyc_last/max/min (io-callback [L1] cost);
   g_m1_max_abs_sample (>0 = live input). Run twice, main numbers <0.1% (F3 board discipline). Any FG not
   green -> isolate, do not rescue (F4 board discipline).
4. **M2 build extra on-board steps** (after step 3 proves M1 passthrough works):
   a. **.map re-read (pin proof)**: confirm s_m1_rx_buf, s_m1_tx_buf, s_m2_fa all in L1 Block 1
      (>=0x2c0000, <=0x2ebfff). Product .map not yet captured -- this is the F24-MAJOR-1 placement-verify.
   b. **Q alignment dump (OPENING-5 discriminant)**: with a known mid-scale input, dump g_m1_rx_buf. Low 8
      bits ~0 + magnitude in high 24 -> LEFT-aligned -> zero-transform identity correct (code as-is). Else
      magnitude in low 24 -> RIGHT-aligned -> apply RX `<<8` / TX `>>8` (the m1_loopback_tdm.c M2 Q-BOUNDARY
      NOTE has the exact lines). This is the R46 mechanical discriminant; HRM grep corroborates.
   c. **read M2 readouts at idle**: g_m2_fira_inloop=1; g_m2_setup_rc=0 (fira_tree_setup ok);
      g_m2_valid=1; g_m2_fg_beam_live=1 (green ONLY if blocks grew AND FIRA output non-zero -- a dead/stub
      FIRA keeps it 0); g_m2_out_nonzero / g_m2_out_max_abs > 0 (beam produced audio); g_m1_cb_cyc_* now =
      core+beam+io (NOT io-callback alone -- caliber = app load, R42; separate off-board).
   d. **R14 bit-exact (INTEGER-enum)**: the FIRA fixed-point INTEGER enum vs the Q15xQ31 signed-fractional
      semantics is a board bit-exact check (fira_tree.h:42-43, per-subband criterion) -- do NOT read M2
      audio as correct until this passes; broadside audio sounding "present" is not bit-exact proof.
   Do NOT predict listening quality or specific cycle numbers off-board (R5 discipline).
