#!/usr/bin/env python3
"""
int_history_proof.py  [DESKTOP host model, [L2], NOT board]

Critic round-2 mandate (2026-06-03): PROVE on desktop that the INT-segment
cross-frame history must be carried in the ZERO-STUFFED domain (consistent with
core hb_interp2 ring continuation); that the round-1 RAW-domain history is WRONG;
and that the round-2 fix gives max|core-fira| == 0 across multiple frames.

This version TRANSCRIBES THE ACTUAL C of fira_run_segment_stateful (round-2),
including the history-update slide branch, and the actual frame sizes the tree uses
(f3=8, f2=16, f1=32 for BENCH_FRAME=64).  It also re-confirms DEC stays bit-exact.

Mirrors of tree_filterbank.c:
  - hb_push_filter (L85-105): ring push + reversed-tap readout h[0]*oldest..h[62]*newest
  - hb_interp2     (L121-132): per raw input x: push(x); push(0); both *2 gain
  - hb_decimate2   (L108-117): per raw input push(x); keep odd-indexed outputs (no x2)

FIRA models (one-shot, fresh delay line warmed by the prepended history prefix):
  - DEC: SAMPLING_DECIMATION over [hist_raw(62) ++ frame_raw], keep odd outputs.
  - INT: SINGLE_RATE over [hist_zs(62) ++ zero_stuff(frame_raw)] (SOFTWARE zero-stuff),
         x2 gain, keep all out_count outputs.

ASCII-only. No board claim.
"""

import numpy as np

NTAPS = 63
HIST = NTAPS - 1   # 62
RATIO = 2

rng_h = np.random.default_rng(12345)
h = rng_h.integers(-3000, 3000, size=NTAPS).astype(np.int64)
h[NTAPS // 2] = 16384


def sat32(v):
    v = int(v)
    if v > 2147483647:
        return 2147483647
    if v < -2147483648:
        return -2147483648
    return v


class Ring:
    def __init__(self):
        self.state = [0] * NTAPS
        self.widx = 0

    def push_filter(self, x, reverse_taps=False):
        idx = self.widx
        self.state[idx] = int(x)
        idx = idx + 1 if idx + 1 < NTAPS else 0
        self.widx = idx
        acc = 0
        for k in range(NTAPS):
            rd = idx + k if idx + k < NTAPS else idx + k - NTAPS
            hk = h[NTAPS - 1 - k] if reverse_taps else h[k]
            acc += hk * self.state[rd]
        return sat32(acc >> 15)


# ---- CORE (ground truth, persistent ring) ----
def core_interp2(ring, x_in):
    out = []
    for x in x_in:
        out.append(sat32(ring.push_filter(int(x)) * 2))
        out.append(sat32(ring.push_filter(0) * 2))
    return out


def core_decimate2(ring, x_in):
    out = []
    for i, x in enumerate(x_in):
        y = ring.push_filter(int(x))
        if (i & 1) == 1:
            out.append(y)
    return out


def zero_stuff(raw):
    out = []
    for x in raw:
        out.append(int(x)); out.append(0)
    return out


# ---- FIRA one-shot: prime with EXACTLY the last (NTAPS-1) buffer samples, then stream ----
def fira_singlerate(prime62, stream, reverse_taps=False, gain2=False):
    ring = Ring()
    for p in prime62:
        ring.push_filter(int(p), reverse_taps)
    out = []
    for x in stream:
        y = ring.push_filter(int(x), reverse_taps)
        out.append(sat32(y * 2) if gain2 else y)
    return out


def fira_decimation(prime62, stream, reverse_taps=False):
    """DEC: prime, then stream raw frame, keep odd-indexed outputs (decimation phase)."""
    ring = Ring()
    for p in prime62:
        ring.push_filter(int(p), reverse_taps)
    out = []
    for i, x in enumerate(stream):
        y = ring.push_filter(int(x), reverse_taps)
        if (i & 1) == 1:
            out.append(y)
    return out


# ---- transcription of fira_run_segment_stateful (round-2) history update ----
def hist_update_raw(hist, frame_raw):
    n = len(frame_raw)
    if n >= HIST:
        return frame_raw[n - HIST:]
    keep = HIST - n
    return hist[n:n + keep] + frame_raw  # slide old left, append new


def hist_update_zs(hist, frame_zs):
    zlen = len(frame_zs)
    if zlen >= HIST:
        return frame_zs[zlen - HIST:]
    keep = HIST - zlen
    return hist[zlen:zlen + keep] + frame_zs


def run_int(policy, in_per_frame, n_frames=8, reverse_taps=False):
    core_ring = Ring()
    hist_raw = [0] * HIST
    hist_zs = [0] * HIST
    rng = np.random.default_rng(777 + in_per_frame)
    per_frame = []
    for f in range(n_frames):
        x = rng.integers(-200000, 200000, size=in_per_frame).astype(np.int64).tolist()
        core_out = core_interp2(core_ring, x)
        frame_zs = zero_stuff(x)
        if policy == 'raw':
            prime = hist_raw[:]                    # round-1 BUG: raw-domain priming
        else:
            prime = hist_zs[:]                     # round-2 FIX: zero-stuffed-domain priming
        fira_out = fira_singlerate(prime, frame_zs, reverse_taps, gain2=True)
        d = max(abs(c - fi) for c, fi in zip(core_out, fira_out))
        per_frame.append(d)
        hist_raw = hist_update_raw(hist_raw, x)
        hist_zs = hist_update_zs(hist_zs, frame_zs)
    return max(per_frame), per_frame


def run_dec(out_per_frame, n_frames=8, reverse_taps=False):
    core_ring = Ring()
    hist_raw = [0] * HIST
    rng = np.random.default_rng(555 + out_per_frame)
    per_frame = []
    for f in range(n_frames):
        nin = RATIO * out_per_frame
        x = rng.integers(-200000, 200000, size=nin).astype(np.int64).tolist()
        core_out = core_decimate2(core_ring, x)
        fira_out = fira_decimation(hist_raw[:], x, reverse_taps)
        d = max(abs(c - fi) for c, fi in zip(core_out, fira_out))
        per_frame.append(d)
        hist_raw = hist_update_raw(hist_raw, x)
    return max(per_frame), per_frame


if __name__ == "__main__":
    print("=== INT/DEC cross-frame history proof (desktop [L2]) ===")
    print("ntaps=%d HIST=%d, BENCH_FRAME=64 -> INT in_counts f3=8,f2=16,f1=32\n" % (NTAPS, HIST))

    print("--- INT segments (the BLOCKED path) ---")
    bug_overall = 0
    fix_overall = 0
    for inpf in (8, 16, 32):
        mr, _ = run_int('raw', inpf)
        mz, _ = run_int('zs', inpf)
        bug_overall = max(bug_overall, mr)
        fix_overall = max(fix_overall, mz)
        print("  in_count=%2d  P_raw(round1 BUG) max=%8d   P_zs(round2 FIX) max=%d"
              % (inpf, mr, mz))
    print("  INT OVERALL:  round-1 bug max=%d (nonzero=BUG)   round-2 fix max=%d (0=FIXED)\n"
          % (bug_overall, fix_overall))

    print("--- DEC segments (must stay bit-exact, untouched) ---")
    dec_overall = 0
    for outpf in (32, 16, 8):
        md, _ = run_dec(outpf)
        dec_overall = max(dec_overall, md)
        print("  out_count=%2d  DEC max|core-fira| = %d" % (outpf, md))
    print("  DEC OVERALL max=%d (0=still bit-exact)\n" % dec_overall)

    print("--- [ASSUME A-orient] sensitivity (reversed FIRA taps) ---")
    mo, _ = run_int('zs', 32, reverse_taps=True)
    print("  INT P_zs with reversed taps: max=%d (nonzero shows orientation MUST be board-locked)\n" % mo)

    ok = (bug_overall != 0) and (fix_overall == 0) and (dec_overall == 0) and (mo != 0)
    print("VERDICT  bug(!=0)=%s  fix(==0)=%s  DEC(==0)=%s  A-orient(!=0)=%s   ALL_OK=%s"
          % (bug_overall != 0, fix_overall == 0, dec_overall == 0, mo != 0, ok))
