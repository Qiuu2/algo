#!/usr/bin/env python3
"""Proposed gate 'C' (continuity): whole-file FFT, zero everything within [fc*2^-1/2*... ] i.e. band +- one 1/3-oct,
inverse -> residual r(t); max|r| in LSB must stay at the rounding floor. Run on ALL 60 delivered files + G1..G5 probes."""
import os, numpy as np
R = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint7/signals/s7ff_v1/wav"
FS, NTOT, M = 48000, 1728000, 24000
N = NTOT - 2 * M
BANDS = [500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300]

def load(nm):
    raw = open(os.path.join(R, nm), "rb").read()[44:]
    a = np.frombuffer(raw, np.uint8).reshape(-1, 3); w = np.zeros((len(a), 4), np.uint8); w[:, 1:] = a
    return (w.view("<i4").reshape(-1) >> 8).astype(np.float64)

def resid_max(v, fc):
    X = np.fft.rfft(v)
    f = np.arange(len(X)) * FS / len(v)
    keep_out = (f < fc * 2 ** (-0.5)) | (f > fc * 2 ** 0.5)      # outside band +- one adjacent third
    X[~keep_out] = 0
    r = np.fft.irfft(X, n=len(v))
    return np.abs(r).max()

worst = 0.0
for fc in BANDS:
    for k in (0, 10, 20, 30, 40):
        nm = "s7ff_v1_%04dHz_%s.wav" % (fc, "0dB" if k == 0 else "m%ddB" % k)
        m = resid_max(load(nm), fc); worst = max(worst, m)
print("delivered 60 files: worst max|residual| = %.2f LSB" % worst)

v0 = load("s7ff_v1_1000Hz_0dB.wav"); FULL = 2 ** 23
nn = np.arange(M); fin = 0.5 * (1 - np.cos(np.pi * nn / M))
probes = {}
q = v0.copy(); q[M + N // 2] += 0.25 * FULL; probes["G1 click +0.25FS"] = q
q = v0.copy(); q[M + N // 2:M + N // 2 + 5] = 0; probes["G2 5-sample dropout"] = q
q = v0.copy(); q[M + N // 2:M + N // 2 + 48] = 0; probes["G3 1 ms dropout"] = q
q = v0.copy(); q[:960] = 0; q[960:M] = v0[M + N - M + 960:M + N]; probes["G4 hard start @20ms"] = q
q = v0.copy(); q[:M] = np.rint(v0[M:2 * M] * fin); probes["G5 junction step"] = q
q = v0.copy(); q[M + N // 3] += 64; probes["G1b click of only 64 LSB (-102 dBFS)"] = q
for lab, q in probes.items():
    print("%-40s max|residual| = %12.1f LSB" % (lab, resid_max(q, 1000)))
