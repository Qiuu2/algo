#!/usr/bin/env python3
"""Critic R3e: independent recomputation of the RS rows (own code, own constants, no project imports).
Track X1: pair domain, composite Simpson in theta (20001 pts per sector).
Track X2: ELEMENT domain (16 complex steering vectors, pair map T), scipy quad_vec, error variance from its own
          Monte-Carlo-free closed form written from scratch (E|g|^2 - |E g|^2 AND E|g-1|^2 variants).
Also: (a) the 'fully expected' variant where the mid sector is error-loaded too ((1+eta) x load) and the position
term uses sin^2(theta) inside each sector -> how far the PM's rows are from 'minimum EXPECTED (side + eta mid)'.
"""
import numpy as np
from scipy.integrate import quad_vec, simpson

C, D, N = 343.0, 0.055, 16
xe = (np.arange(N) - 7.5) * D               # element positions
xc = xe[:8]                                 # pair c = {c, 15-c}, edge -> centre
T = np.zeros((N, 8))
for c in range(8):
    T[c, c] = 1.0
    T[15 - c, c] = 1.0
bands = [1000, 1250, 1600, 2000, 2500, 3150, 4000]
F7 = np.concatenate([fc * 2.0 ** np.linspace(-1 / 6, 1 / 6, 31) for fc in bands])   # own log grid
FROZEN_D20 = np.array([28404, 16525, 20371, 24031, 27287, 29934, 31802, 32768])
HDR = {"RS-A": [3470, 6948, 11598, 16960, 22469, 27318, 30876, 32768],
       "RS-B": [5285, 8787, 13546, 18697, 23762, 28068, 31143, 32768]}

# error statistics, from scratch: a ~ U(-1,1) dB (amplitude), phi ~ U(-5,5) deg, dx ~ U(-0.5,0.5) mm
b = np.log(10) / 20.0
E_amp = np.sinh(b) / b                       # E 10^(a/20)
E_amp2 = np.sinh(2 * b) / (2 * b)            # E 10^(a/10)
p0 = np.deg2rad(5.0)
E_cos = np.sin(p0) / p0
mu = E_amp * E_cos                           # E g (real)
var_g = E_amp2 - mu ** 2                     # E|g - Eg|^2
e_g1 = E_amp2 - 2 * mu + 1                   # E|g - 1|^2   (the PM's sigma_g^2)
sx2 = (0.5e-3) ** 2 / 3.0
print(f"E|g-1|^2 = {e_g1:.12f}   Var(g) = {var_g:.12f}   |Eg|^2 = {mu**2:.9f}")


def R_pair_simpson(t1, t2, k, n=20001):
    th = np.linspace(np.deg2rad(t1), np.deg2rad(t2), n)
    a = 2 * np.cos(k * np.outer(np.sin(th), xc))                 # (n, 8)
    integrand = a[:, :, None] * a[:, None, :]
    return simpson(integrand, x=th, axis=0) / (th[-1] - th[0])


def R_elem_quad(t1, t2, k, loadfun=None):
    """(1/(t2-t1)) int T^T Re(v v^H) T dth ; optional theta-dependent diagonal load (element domain)."""
    t1r, t2r = np.deg2rad(t1), np.deg2rad(t2)

    def f(th):
        v = np.exp(1j * k * xe * np.sin(th))                      # (16,)
        Rv = np.real(np.outer(v, v.conj()))
        if loadfun is not None:
            Rv = Rv + loadfun(th) * np.eye(N)
        return T.T @ Rv @ T
    val, err = quad_vec(f, t1r, t2r, epsabs=1e-13, epsrel=1e-12)
    return val / (t2r - t1r)


def solve(Q):
    W = np.linalg.solve(Q, np.ones(8))
    return W / W.max()


def build(ths, thm, eta, method, sig2g=e_g1, full=False):
    Q = np.zeros((8, 8))
    for f in F7:
        k = 2 * np.pi * f / C
        if method == "simpson":
            Rs, Rm = R_pair_simpson(ths, 90, k), R_pair_simpson(thm, ths, k)
            Q += Rs + eta * Rm + 2 * (sig2g + k * k * sx2) * np.eye(8)
        elif method == "elem":
            if not full:
                Rs, Rm = R_elem_quad(ths, 90, k), R_elem_quad(thm, ths, k)
                Q += Rs + eta * Rm + (sig2g + k * k * sx2) * (T.T @ T)      # T^T T = 2 I
            else:
                # fully expected power: E|sum w g e^{jk(x+dx)s}|^2 ~ |mu_s|^2 |AF0|^2 + Var_s sum|w|^2,
                # Var_s = E|g e^{jk dx s}|^2 - |E g e^{jk dx s}|^2 ; E e^{jk dx s} = sinc, computed exactly
                def mus(th):
                    q = k * 0.5e-3 * np.sin(th)
                    return mu * (np.sinc(q / np.pi))                 # E e^{j k dx s} = sin(q)/q
                def load(th):
                    return E_amp2 - mus(th) ** 2
                def fR(th):
                    v = np.exp(1j * k * xe * np.sin(th))
                    Rv = (mus(th) ** 2) * np.real(np.outer(v, v.conj())) + load(th) * np.eye(N)
                    return T.T @ Rv @ T
                def Rsec(t1, t2):
                    t1r, t2r = np.deg2rad(t1), np.deg2rad(t2)
                    return quad_vec(fR, t1r, t2r, epsabs=1e-13, epsrel=1e-12)[0] / (t2r - t1r)
                Q += Rsec(ths, 90) + eta * Rsec(thm, ths)
    return solve(Q / len(F7))


def q15(w):
    return np.round(w * 32768).astype(int)


for lab, ths, thm, eta in (("RS-A", 60.0, 35.0, 0.1), ("RS-B", 60.0, 30.0, 1.0)):
    w1 = build(ths, thm, eta, "simpson")
    w2 = build(ths, thm, eta, "elem")
    tie1 = np.min(np.abs(w1 * 32768 - np.floor(w1 * 32768) - 0.5))
    print(f"{lab}: X1 simpson Q15 {q15(w1).tolist()} == header {q15(w1).tolist() == HDR[lab]}   tie {tie1:.4f} LSB")
    print(f"{lab}: X2 element Q15 {q15(w2).tolist()} == header {q15(w2).tolist() == HDR[lab]}   max|X1-X2| {np.abs(w1-w2).max():.2e}")
    print(f"      all <= frozen D20 same channel: {bool(np.all(q15(w1) <= FROZEN_D20))}   sum {int(q15(w1).sum())}")
    w3 = build(ths, thm, eta, "elem", sig2g=var_g)
    print(f"      variant Var(g) instead of E|g-1|^2: Q15 {q15(w3).tolist()}  max|dQ15| {np.abs(q15(w3)-np.array(HDR[lab])).max()}")
    w4 = build(ths, thm, eta, "elem", full=True)
    print(f"      variant FULLY-EXPECTED (mid sector loaded too, (1+eta)x; sin^2 position; |Eg|^2 scaling): "
          f"Q15 {q15(w4).tolist()}  max|dQ15| {np.abs(q15(w4)-np.array(HDR[lab])).max()}")
    np.save(f"/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic_r3e/{lab}_full.npy", w4)
