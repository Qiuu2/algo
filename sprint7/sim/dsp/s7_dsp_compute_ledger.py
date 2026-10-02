#!/usr/bin/env python3
"""
s7_dsp_compute_ledger.py -- S7 DSP assessment: pure-stdlib compute ledger (no numpy).

Caliber: WALL-CLOCK cycles per 64-sample frame, as bracketed by g_m2_beam_cyc_max on the
board (DEC-S6-M2-BOARD-PASS-01). This is caliber (1) of the three mutually-incomparable
calibers (wall-clock / contention-ledger / pure-core MMAC, F7_MARGIN_MATERIAL.md:29-56).
Every number carries an L grade. Nothing here is measured; the script only ADDS measured
[L1] anchors to derived/estimated increments and reports the wall-clock margin.

Run:  /usr/bin/python3 s7_dsp_compute_ledger.py
"""

# ⚠ 勘误 2026-09-26 · DEC-S7-RETRACT-SUBBAND-01（补标 2026-10-02）：B4 "subband-level weights" 及其组合行
# （B1+B4、B2+B4、B1+B2+B4）作废——[L2 host 复算] 冻结树分界 3k/6k/12k，detail 带是未对齐梳状残差，
# 不能按子带分别加权。数值不改，以便复现旧表。见 sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md

FS_HZ        = 48000
FRAME        = 64
FPS          = FS_HZ / FRAME                      # 750 frames/s
CCLK_HZ      = 1.0e9                              # [L1/EZKIT] F7 g_f7_cclk_hz (G6 CLOSED)
FRAME_CYC    = int(round(CCLK_HZ / FPS))          # 1,333,333 cyc/frame [L1-derived]
T2_RATIO     = 1.5                                # DEC-S4-CRITERION-01-FINAL
T2_LINE_CYC  = FRAME_CYC / T2_RATIO               # 888,889 cyc/frame wall-clock equivalent

# ---- measured anchors [L1] -----------------------------------------------------------
BEAM_CYC_MAX_0616 = 830_903   # [L1 wall-clock, MAX over run] DEC-S6-M2-BOARD-PASS-01
BEAM_CYC_MAX_0629 = 829_218   # [L1 wall-clock, MAX over run] TEST1_WIRING_FINGERPRINT_FIELDLOG_20260629.md:24
F7_8CH_FIRA       = 463_273   # [L1 bench, main ctx, incl. spin] F7_CLOSING_RECORDS.md:154
F7_1CH_FIRA       =  56_616   # [L1 bench] F7_CLOSING_RECORDS.md:156
H2_BASE_8CH       = 454_730   # [L1 bench] H2_READING_ANOMALY_ANALYSIS.md:9-13
H1_FOCUS_ONLY     =  65_371   # [L1 bench, same-state A/B] H1_FINAL_RULING_MATERIAL.md:16-21
H1_FOCUS_MAC      = 8 * 120 * 8                   # 7,680 MAC/frame (h1_wcet_measure.c:28-32)
H1_CYC_PER_MAC    = H1_FOCUS_ONLY / H1_FOCUS_MAC  # 8.51 cyc/MAC [L1-derived, flat-FIR kernel class]
BOARD_ENV_CYC_PER_MAC = (30, 50)                  # mandatory board envelope [decisions_log:234/770], FIRA-orchestration class

def mcps(cyc):
    return cyc * FPS / 1e6

def margin(cyc):
    return FRAME_CYC / cyc

# ---- candidate increments (cyc/frame, wall-clock) -------------------------------------
# Each entry: (id, label, low_cyc, high_cyc, grade, derivation)
cands = []

# B1: EQ 2-3 biquad on the mono input (64 samp) + per-channel limiter clamp (512 samp) + 2x64 Q31<->float
eq_mac_lo, eq_mac_hi = 5 * 2 * FRAME, 5 * 3 * FRAME          # 640 .. 960 MAC/frame (eq_limiter.c:5-13)
lim_ops              = 8 * FRAME * 2                        # 1024 compare-class ops/frame (2 compares/sample)
conv_ops             = 2 * FRAME                            # 128 FIX/FLOAT ops/frame (mono in + mono out)
b1_lo = int(round(eq_mac_lo * H1_CYC_PER_MAC + lim_ops * 1 + conv_ops * 2))          # optimistic: kernel-class
b1_hi = int(round(eq_mac_hi * BOARD_ENV_CYC_PER_MAC[1] + lim_ops * 4 + conv_ops * 2))  # pessimistic: 50 cyc/MAC
cands.append(("B1", "EQ(2-3bq)+limiter+Q31<->float", b1_lo, b1_hi, "[L3 low]/[L4 high]",
              "MAC 640..960 x {8.51 [L1-derived kernel] .. 50 [L4 envelope]} + limiter 1024 cmp x {1..4} + 128 conv x 2"))

# B2: subband frac-delay focus, 8 tap x 120 samp x 8 ch. Low = H1 bench number; high = scaled by the
# M2-vs-bench wall-clock factor (830,903/463,273) because the M2 context ran 1.79x slower than bench.
m2_over_bench = BEAM_CYC_MAX_0616 / F7_8CH_FIRA
b2_lo = H1_FOCUS_ONLY
b2_hi = int(round(H1_FOCUS_ONLY * m2_over_bench))
cands.append(("B2", "subband frac-delay focus v2 (8tap x 120 x 8ch)", b2_lo, b2_hi, "[L1 bench]/[L3 scaled]",
              "H1 65,371 [L1]; high = x%.2f (M2 831k / F7 463k wall-clock ratio, cause unresolved)" % m2_over_bench))

# B4: subband-level weights, 120 samp x 8 ch = 960 mul/frame
b4_mac = 120 * 8
b4_lo = int(round(b4_mac * H1_CYC_PER_MAC))
b4_hi = int(round(b4_mac * BOARD_ENV_CYC_PER_MAC[1]))
cands.append(("B4", "subband-level weights (4 tables x 8)", b4_lo, b4_hi, "[L3]/[L4]",
              "960 mul x {8.51 .. 50} cyc/MAC; replaces (does not add to) the 512-mul input-scale weight"))

# B5: window swap = table replacement, 0 cyc; per-subband tables = B4 cost
cands.append(("B5", "window swap (dolph_w8_q15.h table)", 0, 0, "[L1 structural]",
              "same 512 mul/frame input-scale loop, only the 8 constants change"))

# B3: steering -- not reachable on 8ch hardware; listed as 0 on this board (see doc)
cands.append(("B3", "angle steering on 8ch A/B-series board", 0, 0, "n/a",
              "math-unreachable (DEC-S3-DSP-03); 16ch fork cost is a different board, see doc sec.3"))

# B6: closure items -- 0 product compute
cands.append(("B6", "closure items (chmap A/B, polarity QA, BEAMCYC split, guards)", 0, 0, "[L1 structural]",
              "diagnostic/build-hygiene only; no per-frame compute in product build"))

# ---- print ----------------------------------------------------------------------------
def row(*cols):
    return "| " + " | ".join(str(c) for c in cols) + " |"

print("## A. anchors")
print(row("quantity", "cyc/frame", "MCPS(x750/1e6)", "% of frame", "wall-clock margin", "grade"))
print(row("---", "---", "---", "---", "---", "---"))
for name, cyc, g in [("frame budget", FRAME_CYC, "[L1-derived]"),
                     ("T2 1.5x line (wall-clock equiv)", round(T2_LINE_CYC), "[L1-derived]"),
                     ("g_m2_beam_cyc_max 2026-06-16", BEAM_CYC_MAX_0616, "[L1 max]"),
                     ("g_m2_beam_cyc_max 2026-06-29", BEAM_CYC_MAX_0629, "[L1 max]"),
                     ("F7 8ch FIRA bench", F7_8CH_FIRA, "[L1 bench]"),
                     ("H2 base 8ch bench", H2_BASE_8CH, "[L1 bench]"),
                     ("H1 focus_only", H1_FOCUS_ONLY, "[L1 bench]")]:
    print(row(name, f"{cyc:,}", f"{mcps(cyc):.2f}", f"{100*cyc/FRAME_CYC:.1f}%", f"{margin(cyc):.3f}x", g))
headroom = FRAME_CYC - BEAM_CYC_MAX_0616
to_line  = T2_LINE_CYC - BEAM_CYC_MAX_0616
print()
print(f"headroom to frame edge   = {headroom:,} cyc = {mcps(headroom):.2f} MCPS = {100*headroom/FRAME_CYC:.1f}% [L1-derived]")
print(f"headroom to 1.5x line    = {to_line:,.0f} cyc = {mcps(to_line):.2f} MCPS  <-- any wall-clock adder above this breaks 1.5x [L1-derived]")
print(f"M2 / bench wall-clock    = {m2_over_bench:.3f}x (831k vs F7 463k); vs H2 base {BEAM_CYC_MAX_0616/H2_BASE_8CH:.3f}x  [L1-derived, cause unresolved -> WO-S6-BEAMCYC-SPLIT]")
print(f"H1 kernel cyc/MAC        = {H1_CYC_PER_MAC:.2f} [L1-derived, flat int FIR class; NOT the FIRA-orchestration 30-50 class]")

print()
print("## B. candidate increments (wall-clock cyc/frame)")
print(row("id", "candidate", "low cyc", "high cyc", "low MCPS", "high MCPS", "grade", "derivation"))
print(row("---", "---", "---", "---", "---", "---", "---", "---"))
for cid, lab, lo, hi, g, d in cands:
    print(row(cid, lab, f"{lo:,}", f"{hi:,}", f"{mcps(lo):.2f}", f"{mcps(hi):.2f}", g, d))

print()
print("## C. combinations vs the 1.5x wall-clock line")
print(row("combination", "adder low", "adder high", "total low", "total high", "occupancy low..high", "margin high..low", "<1.5x ?"))
print(row("---", "---", "---", "---", "---", "---", "---", "---"))
byid = {c[0]: c for c in cands}
combos = [("baseline (no change)", []),
          ("B1", ["B1"]), ("B2", ["B2"]), ("B4", ["B4"]),
          ("B1+B2", ["B1", "B2"]), ("B1+B4", ["B1", "B4"]), ("B2+B4", ["B2", "B4"]),
          ("B1+B2+B4", ["B1", "B2", "B4"])]
for lab, ids in combos:
    lo = sum(byid[i][2] for i in ids); hi = sum(byid[i][3] for i in ids)
    tlo, thi = BEAM_CYC_MAX_0616 + lo, BEAM_CYC_MAX_0616 + hi
    flag = "YES (high)" if thi > T2_LINE_CYC else "no"
    if tlo > T2_LINE_CYC: flag = "YES (even low)"
    print(row(lab, f"{lo:,}", f"{hi:,}", f"{tlo:,}", f"{thi:,}",
              f"{100*tlo/FRAME_CYC:.1f}%..{100*thi/FRAME_CYC:.1f}%",
              f"{margin(thi):.3f}x..{margin(tlo):.3f}x", flag))

print()
print("## D. FIRA segment MAC accounting per frame [L3] (windows from fira_tree.c seg table, 63 taps)")
windows = [64, 32, 16, 16, 32, 64, 16, 32, 64]      # DEC full-rate 2*out (32,16,8) ; INT out (16,32,64) x2 trees
mac_ch  = sum(windows) * 63
fira_cyc_ideal = mac_ch / 4.0                        # 4 MAC/cycle at CCLK, 100% CE [L-adi] fira_fit_assessment.md:148
print(f"windows/ch = {windows} -> {sum(windows)} output slots/ch; MAC/ch = {mac_ch:,}; MAC/frame(8ch) = {8*mac_ch:,}")
print(f"FIRA engine time @4 MAC/cyc ideal CE: {fira_cyc_ideal:,.0f} cyc/ch, {8*fira_cyc_ideal:,.0f} cyc/frame = {100*8*fira_cyc_ideal/F7_8CH_FIRA:.1f}% of F7 463k, {100*8*fira_cyc_ideal/BEAM_CYC_MAX_0616:.1f}% of M2 831k [L3]")
print(f"F7 per-channel 56,616 / 9 seg = {F7_1CH_FIRA/9:,.0f} cyc/seg; ideal MAC share per seg (avg) = {fira_cyc_ideal/9:,.0f} cyc -> orchestration+DMA+spin+postscale >= {100*(1-fira_cyc_ideal/F7_1CH_FIRA):.0f}% of the per-channel wall-clock [L3]")

print()
print("## E. grating-lobe clean-band vs steering angle fc(theta) = c/(d(1+|sin theta|)) [L3], c=343 m/s, d=55 mm")
import math
c0, d = 343.0, 0.055
print(row("theta", "fc (Hz)", "note"))
print(row("---", "---", "---"))
for th in (0, 10, 20, 30):
    fc = c0 / (d * (1 + abs(math.sin(math.radians(th)))))
    print(row(f"{th} deg", f"{fc:,.0f}", "broadside anchor = 6236 Hz (decisions_log:455)" if th == 0 else "v1 useful band >=4 kHz (DEC-S5-V1-SCOPE-01) -> " + ("OK" if fc >= 4000 else "below 4 kHz")))

print()
print("## F. on-axis focus delays per pair (relative to the edge pair, edge gets 0) [L3], d=55 mm, pair c = elements {c,15-c}")
print(row("F (m)", "pair c", "|x_c| (mm)", "delay (us)", "samp @48k (sb3)", "samp @24k (sb2)", "samp @12k (sb1)", "samp @6k (sb0)"))
print(row("---", "---", "---", "---", "---", "---", "---", "---"))
for F in (2.0, 3.0, 5.0):
    r_edge = math.hypot(F, 7.5 * d)
    for c in (0, 3, 7):
        x = (7.5 - c) * d
        tau = (r_edge - math.hypot(F, x)) / c0
        print(row(F, c, f"{1000*x:.1f}", f"{1e6*tau:.1f}", f"{tau*48000:.2f}", f"{tau*24000:.2f}", f"{tau*12000:.2f}", f"{tau*6000:.2f}"))
print("max delay (center pair, F=2 m) sets the FIR span: 8-tap FIR covers 0..7 samples at each subband rate;")
print("at sb3/48k the F=2 m center delay (~5.8 samp) sits near the top of an 8-tap span -> fractional accuracy at the band top degrades; 12-16 taps or integer-offset + 8-tap fractional recommended [L3].")
