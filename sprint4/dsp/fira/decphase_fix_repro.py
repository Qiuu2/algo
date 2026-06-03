#!/usr/bin/env python3
"""
decphase_fix_repro.py  [DESKTOP host model, [L2], NOT board]

DISCRIMINATOR for the DECIMATE-PHASE root cause + fix (2026-06-04).

Root cause (confirmed independently by PM + critic): the FIRA hardware
DECIMATION mode keeps the EVEN input-stream sample (i&1==0) while the core
hb_decimate2 (tree_filterbank.c:108-117) keeps the ODD one (i&1==1).  Because
the FIRA DEC stream is [hist(62=even) ++ frame(...)], FIRA's even-phase keep
lands on FRAME-EVEN indices, core keeps FRAME-ODD indices -> off-by-one-phase.

This script models the REAL hardware (FIRA even-phase) two ways and diffs the
WHOLE frame against the core golden sb3 (and sb0, the pure-DEC cascade):

  UN-FIXED  : FIRA DEC = HW DECIMATION keeping EVEN phase   -> must EXPLODE
              (reproduce board sb3 residual [0,-2,0,+2,0,-2,0,+6] then grow).
  FIXED     : FIRA DEC = SINGLE_RATE full-rate FIR over the SAME stream, then
              SOFTWARE-decimate in postscale with phase=1 (== core (i&1)==1).
              This puts the decimation phase fully under software control
              (mirrors the INT software-zero-stuff rationale) and removes any
              dependence on the unverifiable HW decimation phase.
              -> must give max|core-fira| = 0 over the WHOLE frame.

The FIXED model still INDEPENDENTLY models FIRA (full-rate MAC + its own
software decimate), it does NOT copy the core's kept samples -- it computes
all 512 filter outputs from the FIRA stream and selects phase=1.  The reason
it equals core is structural (same MAC, same selected phase), not a bake-in.

ASCII-only. No board claim. No FIRA benefit numbers (C9).
"""
import importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rr", os.path.join(HERE, "residual_repro.py"))
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)

FRAME = rr.FRAME
HIST = rr.HIST


# --------------------------------------------------------------------------
# FIRA DEC models.  Both build the SAME stream the C builds:
#   temp = [hist_raw(62) ++ frame_raw]   (fira_run_segment_stateful DEC path)
# and run an EXACT int64 MAC (FIRA does exact MAC; postscale does >>15+sat).
# They differ ONLY in which output phase is kept.
# --------------------------------------------------------------------------
def fira_dec_hw_even(hist62, frame_raw):
    """UN-FIXED: HW DECIMATION keeps EVEN stream index (the real hardware)."""
    ring = rr.Ring()
    stream = list(hist62) + list(frame_raw)
    out = []
    for i, x in enumerate(stream):
        y = ring.push_filter(int(x))           # >>15 trunc + sat (postscale_dec)
        if i >= HIST and ((i - HIST) & 1) == 0: # frame-relative EVEN kept (HW even-phase)
            out.append(y)
    return out


def fira_dec_singlerate_swphase1(hist62, frame_raw):
    """FIXED: SINGLE_RATE full-rate FIR over the SAME stream, then software
    decimate with phase=1 (== core (i&1)==1).  Phase is a postscale knob."""
    ring = rr.Ring()
    stream = list(hist62) + list(frame_raw)
    full = []
    for i, x in enumerate(stream):
        y = ring.push_filter(int(x))           # full-rate output, one per input
        if i >= HIST:
            full.append(y)                     # all frame-rate outputs (no HW decimate)
    # software decimate: ratio=2, phase=1  (fira_postscale phase param)
    return [full[k] for k in range(1, len(full), 2)]


def core_dec(hist62, frame_raw):
    """core hb_decimate2: ring primed with hist, keep (i&1)==1 of the frame."""
    ring = rr.Ring()
    for h in hist62:
        ring.push_filter(int(h))               # prime ring (history)
    out = []
    for i, x in enumerate(frame_raw):
        y = ring.push_filter(int(x))
        if (i & 1) == 1:
            out.append(y)
    return out


def maxdiff(a, b):
    n = min(len(a), len(b))
    return max((abs(a[k] - b[k]) for k in range(n)), default=0)


if __name__ == "__main__":
    print("=== DEC-phase fix discriminator (desktop [L2], real coeffs+chirp) ===")
    print("BOARD sb3 residual (fira-core, first 8): ", rr.BOARD_RES, "\n")

    chirp = rr.load_chirp(FRAME * 2)
    x = chirp[:FRAME]
    hist62 = [0] * HIST                         # frame 0: zero history (channel_init)

    # ---------------------------------------------------------------
    # Stage 1: the a1 = dec2(x) cascade itself (this is where the phase
    # bug lives; sb0 = dec(dec(dec(x))) is pure DEC -> the cleanest probe).
    # ---------------------------------------------------------------
    a1_core = core_dec(hist62, x)
    a1_unfixed = fira_dec_hw_even(hist62, x)
    a1_fixed = fira_dec_singlerate_swphase1(hist62, x)
    print("a1 (level-1 dec) full-frame max|core-fira|:")
    print("  UN-FIXED (HW even-phase) :", maxdiff(a1_core, a1_unfixed))
    print("  FIXED    (SR + sw phase1):", maxdiff(a1_core, a1_fixed))

    # ---------------------------------------------------------------
    # Stage 2: full sb3 = in - interp2(decimate2(in)).  Re-run the core
    # interp2 on each a1, then form sb3 and diff the WHOLE frame.
    # (interp2 is INT, already bit-exact under the software zero-stuff
    #  path; here we reuse the core interp2 to isolate the DEC fix.)
    # ---------------------------------------------------------------
    def sb3_from_a1(a1):
        cint = rr.Ring()
        r1 = rr.core_interp2(cint, a1)
        return [x[i] - r1[i] for i in range(FRAME)]

    sb3_core = sb3_from_a1(a1_core)
    sb3_unfixed = sb3_from_a1(a1_unfixed)
    sb3_fixed = sb3_from_a1(a1_fixed)

    # first-8 dump (matches the C harness probe) for the un-fixed model
    i0, cc, ff, res = rr.first_substantial_dump(sb3_core, sb3_unfixed)
    print("\nsb3 UN-FIXED first-8 residual (fira-core):", res,
          " reproduces_board=", res == rr.BOARD_RES)
    md_un = maxdiff(sb3_core, sb3_unfixed)
    md_fx = maxdiff(sb3_core, sb3_fixed)
    print("sb3 WHOLE-FRAME max|core-fira|:")
    print("  UN-FIXED :", md_un, "(must be large -> explosion)")
    print("  FIXED    :", md_fx, "(must be 0)")

    print("\nDISCRIMINATOR:")
    print("  un-fixed explodes (max-diff > 100) :", md_un > 100)
    print("  fixed   max-diff-0  (sb3 & a1)     :",
          (md_fx == 0 and maxdiff(a1_core, a1_fixed) == 0))
    ok = (md_un > 100) and (md_fx == 0) and (maxdiff(a1_core, a1_fixed) == 0) \
        and (res == rr.BOARD_RES)
    print("\nRESULT:", "PASS (fix zeroes the explosion, un-fixed reproduces board)"
          if ok else "FAIL")
