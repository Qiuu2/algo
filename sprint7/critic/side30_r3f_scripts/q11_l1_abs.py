import csv, os, sys
import numpy as np
from scipy import signal
REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
for p in ("sprint7/sim/side30", "sprint7/sim/side30/fir", "sprint7/sim/acoustic", "sprint7/dsp/wtbl"):
    sys.path.insert(0, os.path.join(REPO, p))
import s7_alt_algos as A
F = A.F; FS = 48000.0
q20 = A.G.frozen_d20().astype(float); d20r = q20 / q20.max()
with open(os.path.join(REPO, "sprint7/sim/side30/s7_alt_algos_params.csv")) as fp:
    rows = [r for r in csv.DictReader(fp) if r["design"] == "X3-LR4-700/1600-e0.1m35"]
wk = np.array([[float(r[f"c{i}"]) for i in range(8)] for r in sorted(rows, key=lambda r: int(r["band_or_param"]))])
def lr(fc, kind):
    s = signal.butter(2, fc, btype=kind, fs=FS, output="sos"); return np.vstack([s, s])
def ap(fc):
    s = signal.butter(2, fc, btype="low", fs=FS, output="sos")[0]; return np.array([[s[5], s[4], s[3], s[3], s[4], s[5]]])
bank = [np.vstack([lr(700, "low"), lr(1600, "low")]), np.vstack([lr(700, "high"), lr(1600, "low")]), np.vstack([ap(700), lr(1600, "high")])]
f = np.linspace(1.0, 23999.0, 1 << 16)
amax = np.abs(np.stack([signal.sosfreqz(s, worN=f, fs=FS)[1] for s in bank], 1) @ wk).max()
imp = np.zeros(1 << 16); imp[0] = 1
h = wk.T @ np.stack([signal.sosfilt(s, imp) for s in bank]) / amax
l1 = np.abs(h).sum(1)
print("X3 L1 per channel re digital FS (dB):", np.array2string(20*np.log10(l1), precision=2), "-> max", f"{20*np.log10(l1.max()):.2f} dB at c{l1.argmax()}")
print("X3 L1 per channel vs today      (dB):", np.array2string(20*np.log10(l1/d20r), precision=2))
sig2g = F.sigma2_gain(np.random.default_rng(F.SEED))
Wraw, Qs, brob, Ra = F.perbin_design(F.CFG["V1"], sig2g)
P, hf = F.fit_fir(F.smooth_logf(Wraw, F.SMOOTH_FWHM_OCT), Qs, brob, 127, Ra, F.FIT_GAMMA)
amf = np.abs(np.stack([signal.freqz(hf[c], worN=f, fs=FS)[1] for c in range(8)], 1)).max()
l1f = np.abs(hf).sum(1) / amf
print("FIR L1 per channel vs today     (dB):", np.array2string(20*np.log10(l1f/d20r), precision=2), f"-> max {20*np.log10((l1f/d20r).max()):+.2f}")
print("FIR L1 per channel re digital FS(dB):", np.array2string(20*np.log10(l1f), precision=2))
