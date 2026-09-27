import os, sys
import numpy as np
from scipy import signal
REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
for p in ("sprint7/sim/side30", "sprint7/sim/side30/fir", "sprint7/sim/acoustic", "sprint7/dsp/wtbl"):
    sys.path.insert(0, os.path.join(REPO, p))
import s7_alt_algos as A
F = A.F
sig2g = F.sigma2_gain(np.random.default_rng(F.SEED))
Wraw, Qs, brob, Ra = F.perbin_design(F.CFG["V1"], sig2g)
Ws = F.smooth_logf(Wraw, F.SMOOTH_FWHM_OCT)
P, h = F.fit_fir(Ws, Qs, brob, 127, Ra, F.FIT_GAMMA)
fd = np.geomspace(20, 20000, 4000)
sine = np.abs(F.cos_basis(fd, P.shape[1] - 1) @ P.T).max(0)
l1 = np.abs(h).sum(1)
print("FIR V1-128t per-channel L1/sine (dB):", np.array2string(20*np.log10(l1/sine), precision=2))
print(f"FIR V1-128t on-axis full drive vs D20: sine {20*np.log10(1/np.abs(F.cos_basis(fd, P.shape[1]-1) @ P.T).max()/F.d20_axis_level()):+.2f} dB, L1 {20*np.log10(1/l1.max()/F.d20_axis_level()):+.2f} dB")
rng = np.random.default_rng(3); n = 1 << 18
white = rng.standard_normal(n); Xf = np.fft.rfft(white); fr = np.fft.rfftfreq(n, 1/48000); Xf[1:] /= np.sqrt(fr[1:]); Xf[0] = 0
pink = np.fft.irfft(Xf, n); pink /= np.abs(pink).max()
t = np.arange(n) / 48000
for nm, x in (("pink noise", pink), ("100 Hz square", np.sign(np.sin(2*np.pi*100*t))), ("1 kHz square", np.sign(np.sin(2*np.pi*1000*t)))):
    Y = np.stack([signal.lfilter(h[c], 1, x) for c in range(8)])
    pk = np.abs(Y[:, 20000:]).max(1) / sine
    print(f"  FIR {nm:14s}: peak/(sine-max gain) per channel (dB) {np.array2string(20*np.log10(pk), precision=2)}   max {20*np.log10(pk.max()):+.2f}")
