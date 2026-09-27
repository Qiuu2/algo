import csv, os, sys
import numpy as np
from scipy import signal
REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
for p in ("sprint7/sim/side30", "sprint7/sim/side30/fir", "sprint7/sim/acoustic", "sprint7/dsp/wtbl"):
    sys.path.insert(0, os.path.join(REPO, p))
import s7_alt_algos as A
F = A.F
FS = 48000.0
q20 = A.G.frozen_d20().astype(float); d20r = q20 / q20.max()
with open(os.path.join(REPO, "sprint7/sim/side30/s7_alt_algos_params.csv")) as fp:
    rows = [r for r in csv.DictReader(fp) if r["design"] == "X3-LR4-700/1600-e0.1m35"]
wk = np.array([[float(r[f"c{i}"]) for i in range(8)] for r in sorted(rows, key=lambda r: int(r["band_or_param"]))])
def lr(fc, kind):
    s = signal.butter(2, fc, btype=kind, fs=FS, output="sos"); return np.vstack([s, s])
def ap(fc):   # ONE mirror-numerator biquad (independent of the PM's tf2sos(LP+HP) realisation)
    s = signal.butter(2, fc, btype="low", fs=FS, output="sos")[0]; return np.array([[s[5], s[4], s[3], s[3], s[4], s[5]]])
bank = [np.vstack([lr(700, "low"), lr(1600, "low")]), np.vstack([lr(700, "high"), lr(1600, "low")]), np.vstack([ap(700), lr(1600, "high")])]
f = np.linspace(1.0, 23999.0, 1 << 16)
amax_x = np.abs(np.stack([signal.sosfreqz(s, worN=f, fs=FS)[1] for s in bank], 1) @ wk).max()
# my own rebuilt FIR V1-128 (not the CSV taps)
sig2g = F.sigma2_gain(np.random.default_rng(F.SEED))
Wraw, Qs, brob, Ra = F.perbin_design(F.CFG["V1"], sig2g)
P, h = F.fit_fir(F.smooth_logf(Wraw, F.SMOOTH_FWHM_OCT), Qs, brob, 127, Ra, F.FIT_GAMMA)
amax_f = np.abs(np.stack([signal.freqz(h[c], worN=f, fs=FS)[1] for c in range(8)], 1)).max()
def x3(x):
    B = np.stack([signal.sosfilt(s, x) for s in bank]); return (wk.T @ B) / amax_x
def fir(x):
    return np.stack([signal.lfilter(h[c], 1.0, x) for c in range(8)]) / amax_f
n = 2 * int(FS); k = np.arange(n); t = k / FS
print("per-channel peak vs today's same channel (dB), c0..c7 ; [max over channels; peak re digital FS]")
for f0 in (100, 1000, 3000):
    per = int(round(FS / f0))
    clean = np.where((k % per) < per // 2, 1.0, -1.0)          # PM's generator
    jit = np.sign(np.sin(2 * np.pi * f0 * t))                    # my R3f generator
    nz = int(np.sum(np.abs(np.sin(2 * np.pi * f0 * t)) < 1e-9))
    for nm, x, skip in (("clean, onset incl.", clean, 0), ("clean, steady only", clean, int(FS) // 2),
                        (f"sign(sin) [{nz} zero-crossing samples, sign from rounding]", jit, int(FS) // 2)):
        for lab, y in (("X3 ", x3(x)), ("FIR", fir(x))):
            pk = np.abs(y[:, skip:]).max(1)
            rel = 20 * np.log10(pk / d20r)
            print(f"  {f0:5d} Hz {nm:52s} {lab}: {' '.join(f'{v:+6.2f}' for v in rel)}  [max {rel.max():+5.2f} c{rel.argmax()}; FS {20*np.log10(pk.max()):+5.2f}]")
# worst-case full-scale TWO-LEVEL input for c7 and c2: x = sign(reversed impulse response) -> reaches the L1 bound
imp = np.zeros(1 << 15); imp[0] = 1
hx = x3(imp)
for c in (7, 2):
    xw = np.sign(hx[c][::-1]); xw[xw == 0] = 1.0
    y = x3(np.concatenate([xw, np.zeros(10)]))
    print(f"  worst two-level (+/-1) input for c{c}: c{c} peak {20*np.log10(np.abs(y[c]).max()/d20r[c]):+6.2f} dB vs today"
          f" ({20*np.log10(np.abs(y[c]).max()):+6.2f} dB re FS); L1 bound {20*np.log10(np.abs(hx[c]).sum()/d20r[c]):+6.2f} dB")
