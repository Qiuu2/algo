#!/usr/bin/env python3
"""
residual_repro.py  [DESKTOP host model, [L2], NOT board]

GOAL (Critic round-4 mandate, 2026-06-03/06-04): the BOARD shows a STRUCTURED
residual between the FIRA path and the core-golden subbands -- sb3 dump
(8 consecutive from its first substantial sample, frame 0):
    core: 0x0018CB1E 0x003196D1 0x004A6305 0x00632FB7 0x007BFCD8 0x0094CA60 0x00AD983E 0x00C6666A
    fira: residual (fira-core) = 0, -2, 0, +2, 0, -2, 0, +6
    -> EVEN dump-index exact, ODD dump-index +-2, tail accumulates to +6.
The earlier int_history_proof.py showed max-diff 0 vs core -> that model's FIRA
side does NOT match the real hardware.  RECONCILE: find the ONE mechanism that
reproduces the EXACT board sb3 residual AND the sb0-worst accumulation.

Method: mirror the core C (tree_filterbank.c) bit-exactly using the REAL frozen
coeffs (fir_coeffs_hb63.h) and the REAL frozen chirp (chirp_input.h), then run
several candidate FIRA-side models and diff against core.  The candidate that
reproduces the board residual identifies the mechanism.

Candidates (FIXABLE hypotheses FIRST per mandate):
  (i)   postscale shift-order:  (acc>>15)*2  vs  (acc*2)>>15  vs  acc>>14
  (ii)  round-to-nearest vs truncation at >>15  (and the *2 path)
  (iii) 80-bit reassembly width/sign handling
  (iv)  signed-fractional FIRA applying an extra scale

ASCII-only. No board claim. No FIRA benefit numbers (C9).
"""

import re
import os

NTAPS = 63
HIST = NTAPS - 1
FRAME = 64

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(HERE, "..", "core_only")

# ---- parse the REAL frozen Q15 coeffs ----
def load_coeffs():
    p = os.path.join(CORE, "include", "fir_coeffs_hb63.h")
    txt = open(p).read()
    body = txt.split("g_hb63_q15", 1)[1].split("{", 1)[1].split("}", 1)[0]
    nums = [int(x) for x in re.findall(r"-?\d+", body)]
    assert len(nums) == NTAPS, "got %d coeffs" % len(nums)
    return nums

# ---- parse the REAL frozen chirp (we only need the first few frames) ----
def load_chirp(nmax):
    p = os.path.join(CORE, "bench", "chirp_input.h")
    txt = open(p).read()
    body = txt.split("CHIRP_INPUT[CHIRP_INPUT_N] = {", 1)[1].split("};", 1)[0]
    nums = []
    for tok in re.findall(r"-?\d+", body):
        nums.append(int(tok))
        if len(nums) >= nmax:
            break
    return nums

H = load_coeffs()
assert H[31] == 16385


def sat32(v):
    v = int(v)
    if v > 2147483647:
        return 2147483647
    if v < -2147483648:
        return -2147483648
    return v


class Ring:
    """bit-exact mirror of hb_push_filter (tree_filterbank.c:85-105)."""
    def __init__(self):
        self.state = [0] * NTAPS
        self.widx = 0

    def push_raw_acc(self, x):
        """push x, return the FULL int64 acc BEFORE >>15 (for FIRA mechanism modeling)."""
        idx = self.widx
        self.state[idx] = int(x)
        idx = idx + 1 if idx + 1 < NTAPS else 0
        self.widx = idx
        acc = 0
        for k in range(NTAPS):
            rd = idx + k if idx + k < NTAPS else idx + k - NTAPS
            acc += H[k] * self.state[rd]
        return acc

    def push_filter(self, x):
        return sat32(self.push_raw_acc(x) >> 15)


# ==========================================================================
# CORE ground truth (exact mirror of tfb_analyze, the part that makes sb3).
#   sb3[i] = in[i] - r1[i],  r1 = hb_interp2(ana_int[0], a1, f1)
#   a1     = hb_decimate2(ana_dec[0], in, f0)
# Core interp2 out:  out[2o]=sat(sat(acc(x)>>15)*2), out[2o+1]=sat(sat(acc(0)>>15)*2)
# ==========================================================================
def core_decimate2(ring, x_in):
    out = []
    for i, x in enumerate(x_in):
        y = ring.push_filter(int(x))
        if (i & 1) == 1:
            out.append(y)
    return out


def core_interp2(ring, x_in):
    out = []
    for x in x_in:
        y0 = ring.push_filter(int(x))
        out.append(sat32(y0 * 2))
        y1 = ring.push_filter(0)
        out.append(sat32(y1 * 2))
    return out


# ==========================================================================
# FIRA-side INTERP models.  All run a SINGLE_RATE FIR over the SOFTWARE
# zero-stuffed stream [hist_zs(62) ++ zero_stuff(frame)] exactly like
# fira_run_segment_stateful INT path, but vary the POSTSCALE math to model
# what the hardware 80-bit MAC + core postscale really compute.
#   The acc here == the same int64 MAC as the core (FIRA does exact integer MAC).
#   The ONLY thing that can differ is how acc -> Q31 is done.
# ==========================================================================
def fira_interp(prime_zs, frame_raw, mode):
    ring = Ring()
    for p in prime_zs:
        ring.push_raw_acc(int(p))      # warm the delay line (no output kept)
    out = []
    stream = []
    for x in frame_raw:
        stream.append(int(x)); stream.append(0)
    for x in stream:
        acc = ring.push_raw_acc(int(x))
        if mode == "shift15_then_x2":          # == core order  (acc>>15)*2
            q = (acc >> 15) * 2
        elif mode == "x2_then_shift15":         # (i) wrong order (acc*2)>>15
            q = (acc * 2) >> 15
        elif mode == "shift14":                 # (i) acc>>14
            q = acc >> 14
        elif mode == "round_shift15_x2":        # (ii) round-half-up at >>15, then x2
            q = ((acc + (1 << 14)) >> 15) * 2
        elif mode == "shift15_x2_round16":      # (ii) >>16 round on the *2-domain
            q = ((acc * 2) + (1 << 15)) >> 16 << 1
        else:
            raise ValueError(mode)
        out.append(sat32(q))
    return out


def zero_stuff(raw):
    out = []
    for x in raw:
        out.append(int(x)); out.append(0)
    return out


def run_frame0(mode):
    """Reproduce frame-0 sb3 for a given FIRA interp mode; return (core_sb3, fira_sb3)."""
    chirp = load_chirp(FRAME * 2)          # frame 0 only needs FRAME samples; load 2 to be safe
    x = chirp[:FRAME]
    f0, f1 = FRAME, FRAME // 2

    # ---- core ----
    cdec = Ring(); cint = Ring()
    a1_core = core_decimate2(cdec, x)               # f1 samples
    r1_core = core_interp2(cint, a1_core)           # f0 samples
    sb3_core = [x[i] - r1_core[i] for i in range(f0)]

    # ---- FIRA path (frame 0: history = zeros, same as channel_init) ----
    # a1 for FIRA: use the SAME decimation result as core for the INT-stage input
    # (we are isolating the INTERP postscale; DEC is separately bit-exact-confirmed).
    # But to be faithful, recompute a1 via a FIRA DEC model too (exact MAC, >>15, keep odd).
    a1_fira = fira_decimate(x)
    prime_zs = [0] * HIST                            # frame 0: zero history
    r1_fira = fira_interp(prime_zs, a1_fira, mode)   # f0 samples
    sb3_fira = [x[i] - r1_fira[i] for i in range(f0)]
    return sb3_core, sb3_fira, a1_core, a1_fira


def fira_decimate(x):
    """FIRA DEC model frame0: exact MAC, >>15 trunc, keep odd (== core decimate2)."""
    ring = Ring()
    out = []
    for i, xi in enumerate(x):
        y = ring.push_filter(int(xi))   # >>15 trunc + sat, same as core
        if (i & 1) == 1:
            out.append(y)
    return out


def first_substantial_dump(core, fira, thresh=256, n=8):
    """mimic the C harness probe: first |core|>=thresh, then n consecutive."""
    for i in range(len(core)):
        if abs(core[i]) >= thresh:
            cc = [core[i + d] if i + d < len(core) else 0 for d in range(n)]
            ff = [fira[i + d] if i + d < len(fira) else 0 for d in range(n)]
            res = [ff[d] - cc[d] for d in range(n)]
            return i, cc, ff, res
    return -1, [], [], []


BOARD_CORE = [0x0018CB1E, 0x003196D1, 0x004A6305, 0x00632FB7,
              0x007BFCD8, 0x0094CA60, 0x00AD983E, 0x00C6666A]
BOARD_RES = [0, -2, 0, 2, 0, -2, 0, 6]


if __name__ == "__main__":
    print("=== FIRA residual reproduction (desktop [L2], real coeffs+chirp, frame0) ===")
    print("BOARD sb3 core dump :", [hex(v) for v in BOARD_CORE])
    print("BOARD sb3 residual  :", BOARD_RES, "(fira-core)\n")

    modes = ["shift15_then_x2", "x2_then_shift15", "shift14",
             "round_shift15_x2", "shift15_x2_round16"]
    for mode in modes:
        sb3_c, sb3_f, a1c, a1f = run_frame0(mode)
        # sanity: does our core sb3 dump match the BOARD core dump? (proves model fidelity)
        i0, cc, ff, res = first_substantial_dump(sb3_c, sb3_f)
        core_match = (cc == BOARD_CORE)
        res_match = (res == BOARD_RES)
        print("MODE %-20s  core_dump_match_board=%s  residual=%s%s"
              % (mode, core_match, res,
                 "  <== REPRODUCES BOARD" if (core_match and res_match) else ""))
        if mode == modes[0]:
            print("   (our core sb3 dump : %s)" % [hex(v & 0xffffffff) for v in cc])
            print("   a1 dec match core  : %s" % (a1c == a1f))
