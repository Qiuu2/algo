"""critic R3f addendum: independent recompute of the 'no channel driven harder than today' premise for X3-LR4-700/1600.
Route differs from the PM's (closed-form |A| on geomspace 20-20k, float D20): here REAL biquads (scipy sosfreqz) on a dense
LINEAR grid 1 Hz..24 kHz, the FROZEN Q15 D20 table parsed from the firmware header (G.frozen_d20), plus a transient check."""
import csv, os, sys
import numpy as np
from scipy import signal
REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
for p in ("sprint7/sim/side30", "sprint7/sim/side30/fir", "sprint7/sim/acoustic", "sprint7/dsp/wtbl"):
    sys.path.insert(0, os.path.join(REPO, p))
import gen_m2_wtbl as G
import s7_common as S
FS = 48000.0
q20 = G.frozen_d20().astype(float)                    # frozen board table, Q15 ints
print("frozen D20 Q15 (c0..c7):", q20.astype(int).tolist())
d20r = q20 / q20.max()                                 # today's per-channel gain at full drive (c7 = 1)
with open(os.path.join(REPO, "sprint7/sim/side30/s7_alt_algos_params.csv")) as fp:
    rows = [r for r in csv.DictReader(fp) if r["design"] == "X3-LR4-700/1600-e0.1m35"]
wk = np.array([[float(r[f"c{i}"]) for i in range(8)] for r in sorted(rows, key=lambda r: int(r["band_or_param"]))])
def lr(fc, kind):
    s = signal.butter(2, fc, btype=kind, fs=FS, output="sos"); return np.vstack([s, s])
def ap(fc):
    s = signal.butter(2, fc, btype="low", fs=FS, output="sos")[0]; return np.array([[s[5], s[4], s[3], s[3], s[4], s[5]]])
bank = [np.vstack([lr(700, "low"), lr(1600, "low")]), np.vstack([lr(700, "high"), lr(1600, "low")]), np.vstack([ap(700), lr(1600, "high")])]
f = np.linspace(1.0, 23999.0, 1 << 16)
Bf = np.stack([signal.sosfreqz(s, worN=f, fs=FS)[1] for s in bank], 1)          # complex (F,3)
W = np.abs(Bf @ wk)                                                              # (F,8) channel sine gains
amax = W.max()
g = W / amax
d20_axis = 2 * q20.sum() / q20.max()
ax_sine = 20 * np.log10(1 / amax / d20_axis)
for lab, m in (("all f (1 Hz-24 kHz)", np.ones_like(f, bool)), (">= 1.6 kHz", f >= 1600), ("< 1.6 kHz", f < 1600)):
    rel = 20 * np.log10(g[m].max(0) / d20r)
    print(f"  per-channel peak vs frozen D20 same channel, {lab:20s}: {np.array2string(rel, precision=3)} dB")
rel = 20 * np.log10(g.max(0) / d20r)
over = max(rel.max(), 0.0)
print(f"  full-drive normalisation amax = {amax:.6f} at c{np.unravel_index(W.argmax(), W.shape)[1]}, {f[np.unravel_index(W.argmax(), W.shape)[0]]:.0f} Hz")
print(f"  on-axis vs D20 (Q15 table): sine {ax_sine:+.3f} dB ; keep every channel <= today: extra {over:.3f} dB -> {ax_sine - over:+.3f} dB")
# Q15 realisation of the X3 band gains after normalisation (as firmware would store them): does rounding move the answer?
wq = np.round(wk / amax * 32767) / 32767 * amax
Wq = np.abs(Bf @ wq); relq = 20 * np.log10((Wq / Wq.max()).max(0) / d20r)
print(f"  with Q15-rounded band gains: c2 {relq[2]:+.3f} dB, c3 {relq[3]:+.3f} dB, worst {relq.max():+.3f} dB")
# transient content: same premise judged on output peaks (today = pure gain d20r_c, so today's peak = d20r_c x input peak)
imp = np.zeros(1 << 15); imp[0] = 1
h = wk.T @ np.stack([signal.sosfilt(s, imp) for s in bank]) / amax               # normalised channel impulse responses
print(f"  worst-case (L1) per-channel peak vs today (dB): {np.array2string(20 * np.log10(np.abs(h).sum(1) / d20r), precision=2)}", flush=True)
n = 1 << 17; t = np.arange(n) / FS
for nm, x in (("100 Hz square", np.sign(np.sin(2 * np.pi * 100 * t))), ("1 kHz square", np.sign(np.sin(2 * np.pi * 1000 * t))),
              ("3 kHz square", np.sign(np.sin(2 * np.pi * 3000 * t)))):
    Bt = np.stack([signal.sosfilt(s, x) for s in bank])                          # IIR bank, then 8x3 mix (fast)
    Y = (wk.T @ Bt / amax)[:, 20000:]
    print(f"  {nm:14s}: per-channel output peak vs today's same channel (dB) {np.array2string(20 * np.log10(np.abs(Y).max(1) / d20r), precision=2)}", flush=True)
