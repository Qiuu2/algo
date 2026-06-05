#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPL_MODEL — Track-1 (NUMPY) independent implementation.

Authoritative spec: sprint5/spl_redo/SPL_MODEL_SPEC.md
Re-scope evidence (prereq): sprint5/spl_redo/RE_SCOPE_EVIDENCE.md

Scope: pure software, gate-1 screening. NO board, NO frozen-file touch.
Output grade: system sensitivity = [L2 model]; input SPLo absolute level = [L2-conditions-undetermined].

This track reads SPL_MODEL_SPEC.md ONLY (does NOT see Track-2). It independently
computes the 4 spec outputs (sec.4) + intermediates and writes results_track1.json.

Governance reminders honored here:
  - Re feed = unit-level 7.600 ohm (LEAP Revc [L1]); 15 ohm is channel-level (series pair DC) [L1].
    Per-2.83V/ch power conversion uses Z_ch = 15 ohm (channel-level), per spec sec.2b/4.
  - Main caliber = @ TOTAL electrical input 1 W; array gain = +10*log10(N) (power-split caliber),
    NOT +20*log10(N) (spec sec.2c).
  - Series-pair +6dB on-axis is NOT added on top of array gain (anti-double-count, spec sec.2e).
  - @1m = far-field extrapolated sensitivity (825mm aperture HF not far-field; honest convention, sec.2f).
"""

import csv
import json
import math
import os

# ----------------------------------------------------------------------------
# Fixed inputs from spec (L-graded in comments).
# ----------------------------------------------------------------------------
N = 16                      # 16 radiating units (spec sec.1, sec.2c)
SPLo_dB = 82.161           # [L1 instrument] LEAP reference sensitivity (shape L1; absolute level [L2-cond-undetermined])
V_283 = 2.83               # [V] per-channel applied voltage (secondary caliber, spec sec.2b/4)
Z_ch = 15.0                # [ohm] channel-level series-pair DC [L1] -> used for 2.83V power conversion (spec sec.2b/4)
Re_unit = 7.600            # [ohm] unit-level Revc [L1] -- recorded only; NOT used in main/secondary caliber (spec sec.4 note)
N_CH = 8                   # 8 amplifier channels (total = N_CH * per-channel) (spec sec.4 power note)

# Path to the Dolph -20dB w8 weights csv (8 rows, pair {c,15-c}).
HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.normpath(os.path.join(HERE, "..", "..", "sprint4", "dsp", "fira", "dolph_w8_q15.csv"))


def read_w8(csv_path):
    """Read the 8 channel weights. Track-1 uses column 'w_float_track1_scipy';
    cross-check against 'w_float_track2_recurrence' (should agree to ~1e-9)."""
    w8_track1 = []
    w8_track2 = []
    pairs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            w8_track1.append(float(row["w_float_track1_scipy"]))
            w8_track2.append(float(row["w_float_track2_recurrence"]))
            pairs.append(row["pair"])
    assert len(w8_track1) == 8, f"expected 8 channel weights, got {len(w8_track1)}"
    # csv self-cross-check (two independent weight derivations)
    max_csv_dev = max(abs(a - b) for a, b in zip(w8_track1, w8_track2))
    return w8_track1, w8_track2, pairs, max_csv_dev


def mirror_w8_to_w16(w8):
    """Channel c drives pair {c, 15-c}, both units share channel weight w8[c]:
       w16 = [w8[0..7], w8[7..0]]  (mirror-symmetric), spec sec.2d."""
    w16 = [0.0] * 16
    for c in range(8):
        w16[c] = w8[c]
        w16[15 - c] = w8[c]
    return w16


def main():
    # --- weights ---
    w8_t1, w8_t2, pairs, max_csv_dev = read_w8(CSV_PATH)
    w16 = mirror_w8_to_w16(w8_t1)

    sum_w = sum(w16)                       # Sigma w_i
    sum_w2 = sum(x * x for x in w16)       # Sigma w_i^2

    # --- output 1: ideal array gain (power-split caliber, TOTAL 1W) ---
    ideal_array_gain_dB = 10.0 * math.log10(N)   # +10*log10(16) = +12.0412 dB

    # --- output 2: Dolph taper loss ---
    # taper_loss_dB = 20*log10( sum_w / sqrt(N * sum_w2) )  (<= 0)
    taper_loss_dB = 20.0 * math.log10(sum_w / math.sqrt(N * sum_w2))

    # --- output 3: main -- system sensitivity @ TOTAL 1W ---
    system_sens_1W_total_dB = SPLo_dB + ideal_array_gain_dB + taper_loss_dB

    # --- output 4: secondary -- @ 2.83V per channel ---
    # P_283ch = (2.83)^2 / Z_ch ; P_283total = N_CH * P_283ch ; offset = 10*log10(P_283total / 1W)
    P_283ch = (V_283 ** 2) / Z_ch
    P_283total = N_CH * P_283ch
    P_ref_W = 1.0
    offset_283_dB = 10.0 * math.log10(P_283total / P_ref_W)
    system_sens_283V_per_ch_dB = system_sens_1W_total_dB + offset_283_dB

    results = {
        "_meta": {
            "track": "track1_numpy",
            "spec": "sprint5/spl_redo/SPL_MODEL_SPEC.md",
            "grade_system_sens": "[L2 model]",
            "caveat_SPLo_absolute_level": "[L2-conditions-undetermined] (distance/voltage/baffle/smoothing unstamped; shape is [L1])",
            "caveat_1m": "far-field extrapolated sensitivity @1m (825mm aperture HF not far-field; honest convention per spec sec.2f)",
            "anti_double_count": "series-pair on-axis +6dB NOT added; subsumed in +10log10(16) array gain (spec sec.2e)",
            "Re_caliber": "Re feed = unit-level 7.600 ohm [L1]; 15 ohm = channel-level series-pair DC [L1]; 2.83V uses Z_ch=15 ohm",
            "csv_cross_check_max_dev_track1_vs_track2": max_csv_dev,
            "date": "2026-06-05",
        },
        # ---- four spec outputs (sec.4) ----
        "ideal_array_gain_dB": ideal_array_gain_dB,
        "taper_loss_dB": taper_loss_dB,
        "system_sens_1W_total_dB": system_sens_1W_total_dB,
        "system_sens_283V_per_ch_dB": system_sens_283V_per_ch_dB,
        # ---- intermediates ----
        "intermediates": {
            "N": N,
            "SPLo_dB": SPLo_dB,
            "weights_w8_track1_scipy": w8_t1,
            "weights_w16_mirrored": w16,
            "pairs_w8": pairs,
            "sum_w": sum_w,
            "sum_w2": sum_w2,
            "P_283ch_W": P_283ch,
            "P_283total_W": P_283total,
            "P_ref_W": P_ref_W,
            "offset_283_dB": offset_283_dB,
            "Z_ch_ohm_channel_level": Z_ch,
            "Re_unit_ohm_unit_level": Re_unit,
            "N_CH": N_CH,
            "V_283": V_283,
        },
    }

    out_path = os.path.join(HERE, "results_track1.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # console report
    print("=== SPL_MODEL Track-1 (numpy) ===")
    print(f"csv path                       : {CSV_PATH}")
    print(f"csv cross-check max dev (t1 vs t2): {max_csv_dev:.3e}")
    print(f"w16 (mirrored)                 : {['%.6f' % x for x in w16]}")
    print(f"sum_w  (Sigma w_i)             : {sum_w:.12f}")
    print(f"sum_w2 (Sigma w_i^2)           : {sum_w2:.12f}")
    print("--- four spec outputs ---")
    print(f"ideal_array_gain_dB            : {ideal_array_gain_dB:.6f} dB")
    print(f"taper_loss_dB                  : {taper_loss_dB:.6f} dB")
    print(f"system_sens_1W_total_dB [L2]   : {system_sens_1W_total_dB:.6f} dB")
    print(f"  (= SPLo {SPLo_dB} + array {ideal_array_gain_dB:.4f} + taper {taper_loss_dB:.4f})")
    print("--- 2.83V/ch power accounting ---")
    print(f"P_283ch   = (2.83^2)/15        : {P_283ch:.6f} W")
    print(f"P_283total= 8*P_283ch          : {P_283total:.6f} W")
    print(f"offset_283_dB = 10log10(P_283total/1W): {offset_283_dB:.6f} dB")
    print(f"system_sens_283V_per_ch_dB [L2]: {system_sens_283V_per_ch_dB:.6f} dB")
    print(f"\nwrote: {out_path}")


if __name__ == "__main__":
    main()
