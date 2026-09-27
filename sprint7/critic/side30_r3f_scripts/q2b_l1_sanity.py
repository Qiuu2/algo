import csv, os, sys
import numpy as np
from scipy import signal
REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
FS = 48000.0
def lr(fc, kind):
    s = signal.butter(2, fc, btype=kind, fs=FS, output="sos"); return np.vstack([s, s])
def ap(fc):
    s = signal.butter(2, fc, btype="low", fs=FS, output="sos")[0]; return np.array([[s[5], s[4], s[3], s[3], s[4], s[5]]])
def cascade(*ss): return np.vstack(ss)
imp = np.zeros(1 << 15); imp[0] = 1
comp = {"LP700.LP1600 (band1)": cascade(lr(700,"low"), lr(1600,"low")), "HP700.LP1600 (band2)": cascade(lr(700,"high"), lr(1600,"low")),
        "AP700.HP1600 (band3)": cascade(ap(700), lr(1600,"high")), "AP700.AP1600 (sum)": cascade(ap(700), ap(1600))}
for k, s in comp.items():
    h = signal.sosfilt(s, imp); w, H = signal.sosfreqz(s, worN=np.geomspace(5, 23000, 20000), fs=FS)
    print(f"  {k:22s} L1 = {np.abs(h).sum():6.3f}  max|H| = {np.abs(H).max():.3f}  L1/max = {20*np.log10(np.abs(h).sum()/np.abs(H).max()):5.2f} dB   step overshoot {signal.sosfilt(s, np.ones(4000)).max():.3f}")
with open(os.path.join(REPO, "sprint7/sim/side30/s7_alt_algos_params.csv")) as fp:
    rows = [r for r in csv.DictReader(fp) if r["design"] == "X3-LR4-700/1600-e0.1m35"]
wk = np.array([[float(r[f"c{i}"]) for i in range(8)] for r in sorted(rows, key=lambda r: int(r["band_or_param"]))])
B = np.stack([signal.sosfilt(s, imp) for s in list(comp.values())[:3]])
h = wk.T @ B
fd = np.geomspace(20, 20000, 4000)
Bf = np.stack([np.abs(signal.sosfreqz(s, worN=fd, fs=FS)[1]) for s in list(comp.values())[:3]], 1)
sine = (Bf @ wk).max(0)
# zero-phase counterpart (same magnitude, no all-pass phase): L1 of irfft of the real magnitude
nf = 1 << 15; ff = np.fft.rfftfreq(nf, 1/FS)
Bz = np.stack([np.abs(signal.sosfreqz(s, worN=ff, fs=FS)[1]) for s in list(comp.values())[:3]], 1)
hz = np.fft.irfft(Bz @ wk, n=nf, axis=0)
print("  per-channel L1/sine (dB), real IIR   :", np.array2string(20*np.log10(np.abs(h).sum(1)/sine), precision=2))
print("  per-channel L1/sine (dB), zero-phase :", np.array2string(20*np.log10(np.abs(hz).sum(0)/sine), precision=2))
# realistic signals: peak |y_c| / (w_max-normalised) vs a pure table with the same sine-max gain, pink noise and a full-scale 100 Hz square
rng = np.random.default_rng(3); n = 1 << 18
white = rng.standard_normal(n); Xf = np.fft.rfft(white); fr = np.fft.rfftfreq(n, 1/FS); Xf[1:] /= np.sqrt(fr[1:]); Xf[0] = 0
pink = np.fft.irfft(Xf, n); pink /= np.abs(pink).max()
t = np.arange(n) / FS
for nm, x in (("pink noise", pink), ("100 Hz square", np.sign(np.sin(2*np.pi*100*t))), ("1 kHz square", np.sign(np.sin(2*np.pi*1000*t)))):
    Y = wk.T @ np.stack([signal.sosfilt(s, x) for s in list(comp.values())[:3]])
    pk = np.abs(Y[:, 20000:]).max(1) / sine   # peak relative to (sine-max gain x input peak 1)
    print(f"  {nm:14s}: peak(y_c)/(sine-max gain) per channel (dB) {np.array2string(20*np.log10(pk), precision=2)}")
