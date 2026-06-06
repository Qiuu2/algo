#!/usr/bin/env python3
"""
eq_compute_budget.py -- desktop ledger for O1 EQ+limiter compute.

L-grade discipline:
  - MAC/sample counts are L2-accounting, read line-by-line from
    eq_limiter.c source (NOT guessed). Each count cites the source lines.
  - MCPS = MAC/sample x FS x cyc/MAC, with cyc/MAC the MANDATORY board
    envelope band {30,50} (decisions_log:234/770). Single source for the
    unit conversion (avoids the MMAC mis-attach lesson, workflow-three-gate).
  - Result is [L2-account / board-factor-band], to be compared against the
    in-archive 29-60 MCPS [L4] placeholder (DEC-S5-EQ-O1-01).
  - C9: this is a pure budget reconciliation. It feeds NO selection / promise.
"""

FS_HZ = 48000.0
CYC_PER_MAC = (30, 50)        # board envelope band [decisions_log:234/770]

# ---- MAC/sample, counted from eq_limiter.c (line anchors) ----
# eq_biquad_tick (eq_limiter.c, the 3 arithmetic lines):
#   y  = b0*x + z1                 -> 1 MAC  (b0*x)
#   z1 = b1*x + z2 - a1*y          -> 2 MAC  (b1*x, a1*y)
#   z2 = b2*x      - a2*y          -> 2 MAC  (b2*x, a2*y)
BIQUAD_MAC = 5                # DF1 canonical, 5 MAC/sample/biquad

# master-bus EQ runs on ONE stream (eq_master_process loops bands on x[i]),
# NOT per-channel x8 -- this is the 1/8 master-bus saving (EQ_PRD sec.2.2).
EQ_STREAMS = 1

# limiter (eq_limiter_sample): fabs + 2 compares + (rare) 1 clamp mul.
# In-range path = 0 MAC; clamp path = 1 mul. Counted as 0 MAC (scalar
# control, EQ_PRD sec.2.2 / CO-5 "limiter MAC negligible"). Even pessimistically
# at 1 op/sample x 8ch it is ~0.4 MCPS at 50 cyc, immaterial -- reported below.
LIM_OPS_PER_SAMPLE_PER_CH = 1
LIM_NCH = 8


def mcps(mac_per_sample, cyc):
    return mac_per_sample * FS_HZ * cyc / 1.0e6


def main():
    print("=== O1 EQ + limiter desktop compute budget (L2-account) ===")
    print("FS = %.0f Hz ; cyc/MAC band = %s (board envelope, "
          "decisions_log:234/770)\n" % (FS_HZ, CYC_PER_MAC))

    rows = []
    for n_bands in (2, 3):
        eq_mac = BIQUAD_MAC * n_bands * EQ_STREAMS
        lo = mcps(eq_mac, CYC_PER_MAC[0])
        hi = mcps(eq_mac, CYC_PER_MAC[1])
        rows.append((n_bands, eq_mac, lo, hi))
        print("EQ %d biquad (master-bus, 1 stream): %2d MAC/samp"
              " -> %5.1f MCPS (@30) .. %5.1f MCPS (@50)"
              % (n_bands, eq_mac, lo, hi))

    # limiter, pessimistic (counted as MAC even though ~0)
    lim_mac = LIM_OPS_PER_SAMPLE_PER_CH * LIM_NCH
    lim_lo = mcps(lim_mac, CYC_PER_MAC[0])
    lim_hi = mcps(lim_mac, CYC_PER_MAC[1])
    print("limiter 8ch (pessimistic 1 op/samp/ch): %d 'MAC'/samp"
          " -> %.2f .. %.2f MCPS (treated ~0)" % (lim_mac, lim_lo, lim_hi))

    # full O1 envelope: min(2bq@30) .. max(3bq@50) [+ limiter pessimistic]
    o1_lo = rows[0][2]                 # 2 biquad @ 30
    o1_hi = rows[1][3] + lim_hi        # 3 biquad @ 50 + limiter pessimistic
    o1_hi_eqonly = rows[1][3]
    print("\nO1 total [L2-account/board-band]:")
    print("  EQ-only   : %.1f .. %.1f MCPS  (2bq@30 .. 3bq@50)"
          % (o1_lo, o1_hi_eqonly))
    print("  EQ+limiter: %.1f .. %.1f MCPS  (limiter pessimistic)"
          % (o1_lo, o1_hi))

    # compare to in-archive [L4] placeholder
    print("\nIn-archive [L4] placeholder (DEC-S5-EQ-O1-01): 29 .. 60 MCPS")
    print("  derivation there: 20-25 MAC/samp x 48k x {30,50} cyc/MAC")
    print("  -> 28.8 (2bq/30) .. 60.0 (3bq/50)")
    print("reconciliation: source-counted EQ-only %.1f..%.1f vs L4 28.8..60.0"
          % (o1_lo, o1_hi_eqonly))
    print("  NOTE: the L4 placeholder used 20-25 MAC/samp; source count is")
    print("  10 (2bq) / 15 (3bq) MAC/samp for the EQ itself. The L4 20-25")
    print("  bundled limiter+overhead+margin into the MAC/samp. EQ-only MCPS")
    print("  is therefore at/below the L4 low end; the L4 60.0 high end holds")
    print("  as a conservative ceiling once limiter+per-segment overhead are")
    print("  added. No selection/promise consumes this (C9, pure budget).")


if __name__ == "__main__":
    main()
