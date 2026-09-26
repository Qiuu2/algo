# sprint7/sim/side30/s7_tree_subband_response.py -- landed 2026-09-26 (PM). Evidence for DEC-S7-RETRACT-SUBBAND-01: float replica of frozen tree_filterbank.c:108-205 (same op order), per-subband band-only reconstruction gain vs frequency + PR check. [L2 host] No RNG.
import os
# My own independent check of critic F1/F2 (float model of the frozen pyramid, same op order as tree_filterbank.c)
import re, sys, numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
txt = open(REPO + "/sprint4/dsp/core_only/include/fir_coeffs_hb63.h").read()
body = txt[txt.index("g_hb63_q15[FIR_HB63_NTAPS] = {"):]
h = np.array([int(v) for v in re.findall(r"-?\d+", body[body.index("{"):body.index("}")])], float) / 32768.0
assert len(h) == 63, len(h)
def filt(x): return np.convolve(x, h)[:len(x)]            # causal FIR, same as hb_push_filter stream
def dec2(x): return filt(x)[1::2]                          # keep odd index ((i&1)==1)
def interp2(x):
    u = np.zeros(2 * len(x)); u[0::2] = x                   # phase0 = real sample, phase1 = inserted 0
    return 2 * filt(u)
def analyze(x):
    a1 = dec2(x); a2 = dec2(a1); a3 = dec2(a2)
    r3 = interp2(a3); r2 = interp2(a2); r1 = interp2(a1)
    return a3, a2 - r3, a1 - r2, x - r1                     # sb0..sb3 (tree_filterbank.c:161-164)
def synth(sb0, sb1, sb2, sb3, g=(1, 1, 1, 1)):
    a2p = interp2(g[0] * sb0) + g[1] * sb1
    a1p = interp2(a2p) + g[2] * sb2
    return interp2(a1p) + g[3] * sb3
fs = 48000.0; n = 48000
t = np.arange(n) / fs
print("band-only reconstruction gain (dB) of each subband alone, 48 kHz input:")
print("  f(Hz)   SB0    SB1    SB2    SB3   | PR all-ones err")
for f in (500, 1000, 1500, 2000, 2750, 3000, 3500, 5000, 8000):
    x = np.sin(2 * np.pi * f * t)
    sbs = analyze(x)
    row = []
    for k in range(4):
        g = [0, 0, 0, 0]; g[k] = 1
        y = synth(*sbs, g=g)[8000:]
        row.append(20 * np.log10(np.sqrt(np.mean(y ** 2)) / np.sqrt(0.5) + 1e-12))
    pr = np.max(np.abs(synth(*sbs)[8000:] - x[8000:]))
    print(f"  {f:5d} " + " ".join(f"{v:6.1f}" for v in row) + f"   | {pr:.1e}")
