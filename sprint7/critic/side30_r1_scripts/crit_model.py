#!/usr/bin/env python3
"""Critic's independent re-implementation (does NOT import the lead's script or s7_common).
Isotropic point sources, N=16, d=55 mm, c=343, broadside, centre-symmetric 8 pairs {c,15-c}."""
import csv, numpy as np
from scipy.signal.windows import chebwin
REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
C, D, N = 343.0, 0.055, 16
X = (np.arange(N) - 7.5) * D                    # element positions, n=0 edge .. n=15 other edge

def read_w8():
    with open(f"{REPO}/sprint4/dsp/fira/dolph_w8_q15.csv") as fh:
        r = list(csv.DictReader(fh))
    return np.array([float(x["w_float_track1_scipy"]) for x in r])   # ch0 = edge pair .. ch7 = centre

def w16(w8):
    w8 = np.asarray(w8, float)
    return np.array([w8[min(n, N - 1 - n)] for n in range(N)])

def cheb16(sll):
    w = chebwin(N, sll); return w / w.max()

W20 = w16(read_w8())

def af(theta_deg, f, w):
    th = np.deg2rad(np.atleast_1d(theta_deg).astype(float))
    k = 2 * np.pi * np.atleast_1d(f)[:, None, None] / C       # (F,1,1)
    ph = np.exp(1j * k * np.sin(th)[None, :, None] * X[None, None, :])  # (F,T,N)
    return (ph * np.asarray(w)[None, None, :]).sum(-1)          # (F,T)

def att_point(theta, f, w):
    a = af([0.0, theta], f, w)[0]
    return 20 * np.log10(abs(a[0]) / abs(a[1]))

def band_f(fc, n=201):
    return np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), n)

def band_att(fc, w_of_f, thetas=(90.0,), n=201, worst_pm=False):
    """w_of_f: callable f -> 16 weights (complex ok) or fixed array. Power-average over band (log-spaced = pink)."""
    fs = band_f(fc, n)
    th = np.array([0.0] + list(thetas) + ([-t for t in thetas] if worst_pm else []))
    P = np.zeros(len(th))
    for f in fs:
        w = w_of_f(f) if callable(w_of_f) else w_of_f
        P += np.abs(af(th, f, w)[0]) ** 2
    P /= len(fs)
    return 10 * np.log10(P[0] / P[1:].max())

def bw6(f, w):
    th = np.linspace(0, 90, 90001)
    p = 20 * np.log10(np.abs(af(th, f, w)[0]) / abs(af([0.0], f, w)[0, 0]))
    i = np.argmax(p < -6.0)
    t = th[i - 1] + (th[i] - th[i - 1]) * (-6.0 - p[i - 1]) / (p[i] - p[i - 1])
    return 2 * t
