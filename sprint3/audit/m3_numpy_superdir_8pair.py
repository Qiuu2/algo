#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-MATLAB-M3 轨3 [L2-numpy] : 超指向 MVDR d=55 (ε扫描) + 8路A/B串联 broadside 等价性
作者: 声学仿真专家 teammate (agent-acoustic-sim-v1)
日期: 2026-05-29

几何 (LOCKED, SC-S3-GEOM-01): N=16 / d=55mm / L=825mm / Dolph-Cheby-20dB / broadside / isotropic
说明: M0 标注 numpy 现有超指向实现 (diff_1khz_optimization.py) 是 d=30 撤回几何, 不可直接引.
      故本脚本在 d=55 重写 MVDR 超指向 (与 MATLAB 轨1/轨2 同方法), 补三轨第三轨.
方法: 各向同性噪声相干 Gamma_ij = sinc(kd|i-j|); w=(Gamma+eps*I)^-1 a / [a^H (Gamma+eps*I)^-1 a]
      (与 p02_superdirective_d55.m / m3_superdir_8pair_agent.m 完全同一公式, 独立实现)
口径: BW = -6dB 全角 (full-angle); WNG = |w^H a|^2 / (w^H w); 容差同 MATLAB 口径.
措辞红线: 全部为仿真值, 非实测.
"""
import numpy as np
from scipy.signal.windows import chebwin

# ---- 公共参数 ----
c   = 343.0          # 声速 m/s (20°C)
N   = 16             # 阵元数
d   = 0.055          # 间距 m (d=55mm 基线)
f   = 1000.0         # 超指向目标频点 Hz
k   = 2*np.pi*f/c
ang = np.arange(-90, 90+1e-9, 0.01)   # deg, broadside=0
a   = np.ones(N, dtype=complex)        # broadside 导向矢量
np.random.seed(20260529)               # 形式固定(本段确定性)

def bw_neg6(P, ang):
    """-6dB 全角 BW; 主瓣未在[-90,90]收束到-6dB则截断180°"""
    i0 = int(np.argmax(P))
    iR = i0
    while iR < len(P)-1 and P[iR] > -6:
        iR += 1
    iL = i0
    while iL > 0 and P[iL] > -6:
        iL -= 1
    if iR >= len(P)-1 or iL <= 0:
        return 180.0
    aR = np.interp(-6, [P[iR], P[iR-1]], [ang[iR], ang[iR-1]])
    aL = np.interp(-6, [P[iL], P[iL+1]], [ang[iL], ang[iL+1]])
    return aR - aL

def peak_sll(P, ang):
    i0 = int(np.argmax(P))
    iR = i0
    while iR < len(P)-1 and P[iR+1] <= P[iR]:
        iR += 1
    iL = i0
    while iL > 1 and P[iL-1] <= P[iL]:
        iL -= 1
    mask = np.ones(len(P), dtype=bool)
    mask[iL:iR+1] = False
    if not mask.any():
        return -60.0
    return float(np.max(P[mask]))

def superdir(N, d, f, c, eps, a, ang):
    k = 2*np.pi*f/c
    idx = np.arange(N)
    I, J = np.meshgrid(idx, idx, indexing='ij')
    x = k*d*np.abs(I-J)
    with np.errstate(invalid='ignore', divide='ignore'):
        Gamma = np.sinc(x/np.pi)   # numpy sinc(z)=sin(pi z)/(pi z) -> arg x/pi 给 sin(x)/x
    Gamma[x == 0] = 1.0
    Gr = Gamma + eps*np.eye(N)
    Gr_inv_a = np.linalg.solve(Gr, a)
    w = Gr_inv_a / (a.conj() @ Gr_inv_a)
    st = np.sin(np.deg2rad(ang))
    ph = k * (np.arange(N)[:, None] * d) * st[None, :]
    AF = np.abs(w.conj() @ np.exp(1j*ph))
    P = 20*np.log10(AF/AF.max() + 1e-12)
    bw = bw_neg6(P, ang)
    wng = 10*np.log10(np.abs(w.conj() @ a)**2 / np.real(w.conj() @ w))
    err_pow = min(10**((wng-3)/10), 0.9)
    gain_tol = 20*np.log10(1+np.sqrt(err_pow))
    phase_tol = np.rad2deg(np.sqrt(err_pow))
    return bw, float(np.real(wng)), gain_tol, phase_tol

print("="*70)
print("M3-A 轨3 [L2-numpy] : 超指向 MVDR d=55 (N=16, f=1kHz)")
print("="*70)
print(f"{'eps':>7} | {'BW1k°':>8} | {'WNG_dB':>8} | {'gain_tol_dB':>11} | {'phase_tol°':>10}")
print("-"*55)
eps_list = [0.3, 0.1, 0.03, 0.01, 0.003]
rowsA = []
for eps in eps_list:
    bw, wng, gt, pt = superdir(N, d, f, c, eps, a, ang)
    print(f"{eps:>7.3f} | {bw:>8.2f} | {wng:>8.2f} | {gt:>11.2f} | {pt:>10.2f}")
    rowsA.append((eps, 55, bw, wng, gt, pt))

# 参考 d=55 标称 Dolph-20
w0 = chebwin(N, 20); w0 = w0/w0.sum()
st = np.sin(np.deg2rad(ang))
ph0 = k*(np.arange(N)[:, None]*d)*st[None, :]
AF0 = np.abs(w0 @ np.exp(1j*ph0)); P0 = 20*np.log10(AF0/AF0.max()+1e-12)
bw0 = bw_neg6(P0, ang)
wng0 = 10*np.log10(np.abs(w0 @ a)**2/(w0 @ w0))
print(f"\n[参考] d=55 标称 Dolph-20 无超指向: BW@1k={bw0:.2f}° WNG={np.real(wng0):.2f}dB")

# ---- Part B : 8路串联 broadside 等价性 ----
print("\n" + "="*70)
print("M3-B 轨3 [L2-numpy] : 8路串联 vs 16元独立 broadside 等价性 (f=1kHz)")
print("="*70)
fc = 1000.0; kc = 2*np.pi*fc/c
xn = (np.arange(N) - (N-1)/2.0) * d
phB = kc * xn[:, None] * st[None, :]

w16 = chebwin(N, 20); w16 = w16/w16.sum()
AF16 = np.abs(w16 @ np.exp(1j*phB)); P16 = 20*np.log10(AF16/AF16.max()+1e-12)

w_pair = w16[:N//2]
w8p = np.concatenate([w_pair, w_pair[::-1]]); w8p = w8p/w8p.sum()
AF8p = np.abs(w8p @ np.exp(1j*phB)); P8p = 20*np.log10(AF8p/AF8p.max()+1e-12)

bw16, bw8p = bw_neg6(P16, ang), bw_neg6(P8p, ang)
sll16, sll8p = peak_sll(P16, ang), peak_sll(P8p, ang)
max_w_diff = float(np.max(np.abs(w16 - w8p)))
max_p_diff = float(np.max(np.abs(P16 - P8p)))

print(f"{'指标':<16} | {'16-indep':>14} | {'8-pair':>14} | {'偏差':>10}")
print("-"*64)
print(f"{'BW@1k -6dB°':<16} | {bw16:>14.4f} | {bw8p:>14.4f} | {abs(bw16-bw8p):>10.2e}")
print(f"{'峰值SLL dB':<16} | {sll16:>14.4f} | {sll8p:>14.4f} | {abs(sll16-sll8p):>10.2e}")
print(f"权向量逐元最大偏差(linear) = {max_w_diff:.3e}")
print(f"方向图逐点最大偏差(dB)      = {max_p_diff:.3e}")

# CSV 落盘
import csv, os
OUT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(OUT, 'm3_numpy_superdir_d55.csv'), 'w', newline='') as fp:
    w = csv.writer(fp); w.writerow(['eps','d_mm','BW1k_deg','WNG_dB','gain_tol_dB','phase_tol_deg'])
    for r in rowsA: w.writerow([f"{r[0]:.3f}", r[1], f"{r[2]:.2f}", f"{r[3]:.2f}", f"{r[4]:.2f}", f"{r[5]:.2f}"])
with open(os.path.join(OUT, 'm3_numpy_8pair_equiv.csv'), 'w', newline='') as fp:
    w = csv.writer(fp); w.writerow(['metric','16indep_dolph20','8pair_sym','abs_diff'])
    w.writerow(['BW1k_neg6_full_deg', f"{bw16:.4f}", f"{bw8p:.4f}", f"{abs(bw16-bw8p):.3e}"])
    w.writerow(['peak_SLL_dB', f"{sll16:.4f}", f"{sll8p:.4f}", f"{abs(sll16-sll8p):.3e}"])
    w.writerow(['max_weight_diff_linear', '', '', f"{max_w_diff:.3e}"])
    w.writerow(['max_pattern_diff_dB', '', '', f"{max_p_diff:.3e}"])
print("\nCSV: m3_numpy_superdir_d55.csv + m3_numpy_8pair_equiv.csv")
print("="*70)
print("M3 (numpy 轨3) 完成")
