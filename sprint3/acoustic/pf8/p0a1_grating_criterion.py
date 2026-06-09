#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-PF8-P0A-1 : 栅瓣判据校准 (Grating-lobe criterion calibration)
声学仿真专家 teammate — P0-A 第一交付物（仅判据校准，不做 5 频点代价量化）

目的：独立推导并用 L2 数值仿真校准两个不同物理阶段的栅瓣判据，
      纠正历史文档把"栅瓣临界 = 3.1kHz"的单点表述（混了两个阶段）。

物理正确性硬规则（对齐 skill.md N.2）：
  - c = 343 m/s（20°C 空气）显式声明，绝不用光速默认。
  - 本任务为 broadside-only（0° 固定波束，无电子偏转）—— 锁定硬决策。
  - 数字带溯源标签：L1=几何解析，L2=数值仿真（array factor）。不得称"实测"。

基线几何（CTO 锁定）：N=16, d=55mm, L=(N-1)d=825mm, broadside, Dolph-Cheby -20dB。
方法：点声源远场阵因子 AF(θ)=Σ w_n exp(j k x_n sinθ)，θ∈[0,90°]（半空间，对称）。
"""
import numpy as np
from scipy.signal import argrelmax

# ── 物理常数与几何（参数区，可复现）──────────────────────────
C    = 343.0          # 声速 m/s（20°C 空气）—— skill.md N.2.1 强制显式
N    = 16             # 阵元数
D_MM = 55.0
D    = D_MM / 1000.0  # 阵元间距 m
L    = (N - 1) * D    # 声学孔径 m

# Dolph-Chebyshev -20dB 加权（与基线一致；栅瓣位置由几何决定，与加权无关，
# 但栅瓣电平相对主瓣会受加权影响，故仍用基线加权以反映真实电平）
def chebwin_taper(n, sll_db):
    """Dolph-Chebyshev 窗，sll_db 为正数表示旁瓣低于主瓣的 dB 数。"""
    from scipy.signal.windows import chebwin
    return chebwin(n, at=sll_db)

W = chebwin_taper(N, 20.0)
W = W / W.sum()

# 阵元位置（中心对称）
X = (np.arange(N) - (N - 1) / 2.0) * D

# ── L1：两个几何解析判据 ────────────────────────────────────
f_half = C / (2 * D)   # d/λ = 1/2  → 栅瓣开始从 ±90° 边缘抬升
f_full = C / D         # d/λ = 1    → 栅瓣主瓣完全进入可视区（等高副主瓣）

print("=" * 70)
print("L1 几何解析判据（独立推导）")
print("=" * 70)
print(f"  c = {C} m/s, d = {D_MM} mm = {D} m, N = {N}, L = {L*1000:.0f} mm")
print(f"  [L1] 半波长准则  d/λ ≥ 0.5 → f_half = c/(2d) = {f_half:.1f} Hz = {f_half/1000:.3f} kHz")
print(f"       物理意义：此频率以下完全无栅瓣；以上栅瓣开始从 ±90° 边缘抬升（过渡阶段）")
print(f"  [L1] 严格准则    d/λ ≥ 1.0 → f_full = c/d   = {f_full:.1f} Hz = {f_full/1000:.3f} kHz")
print(f"       物理意义：栅瓣主瓣完全进入可视区，±90° 内出现与主瓣等高的副主瓣")

# ── L2：数值仿真验证 ────────────────────────────────────────
# 在半空间 θ∈[0,90°] 扫描方向图，量化栅瓣进入可视区的频率/角度/电平。
THETA = np.linspace(0, 90, 9001)   # 0.01° 分辨率
TH = np.radians(THETA)

def array_factor_db(freq):
    k = 2 * np.pi * freq / C
    af = np.zeros_like(TH, dtype=complex)
    for n in range(N):
        af += W[n] * np.exp(1j * k * X[n] * np.sin(TH))
    mag = np.abs(af)
    mag /= mag.max()
    return 20 * np.log10(np.maximum(mag, 1e-12))

def grating_geometry(freq):
    """几何预测的栅瓣角：sin θ_gl = λ/d（仅 λ/d ≤ 1 即 d≥λ 时落在可视区）。"""
    lam = C / freq
    ratio = D / lam
    if ratio >= 1.0:
        return ratio, np.degrees(np.arcsin(min(1.0, lam / D)))
    return ratio, None

def grating_lobe_level(freq):
    """L2：扫描方向图，找出主瓣(0°)以外的最高副瓣（栅瓣/旁瓣），返回(角度,电平dB)。
    区分'近 ±90° 边缘抬升'与'可视区内独立栅瓣峰'。"""
    db = array_factor_db(freq)
    # 主瓣在 0°，找第一个零点/谷之后的所有局部极大
    # 先定位主瓣外区域：从全局最大(0°)向外，找到第一个极小
    peaks = argrelmax(db, order=10)[0]
    # 排除主瓣本身（0°附近）
    peaks = peaks[THETA[peaks] > 3.0]
    if len(peaks) == 0:
        return None, None, None
    # 最高的那个副瓣
    top = peaks[np.argmax(db[peaks])]
    return THETA[top], db[top], db[peaks]  # 角度, 电平(相对主瓣dB), 全部副瓣电平

# 5 个校准频点
FREQS = [3120, 4000, 5000, 6240, 8000]

print()
print("=" * 70)
print("L2 数值仿真验证（array factor, N=16/d=55/Dolph-20, θ∈[0,90°]）")
print("=" * 70)
print(f"{'f(Hz)':>6} {'d/λ':>6} {'几何栅瓣角(°)':>13} {'L2最高副瓣角(°)':>15} {'L2最高副瓣电平(dB)':>18}")
print("-" * 70)

rows = []
for f in FREQS:
    ratio, gl_geo = grating_geometry(f)
    ang, lvl, allpk = grating_lobe_level(f)
    gl_geo_s = f"{gl_geo:.1f}" if gl_geo is not None else "—(可视区外)"
    rows.append((f, ratio, gl_geo, ang, lvl))
    print(f"{f:>6} {ratio:>6.3f} {gl_geo_s:>13} {ang:>15.1f} {lvl:>18.2f}")

# 额外：精确求"最高副瓣首次达到 ~ -20dB(=主瓣电平附近/接近Dolph底)与达到 0dB(等高)"的频率
print()
print("=" * 70)
print("栅瓣电平随频率演化（细扫，定位'真问题起点'）")
print("=" * 70)
print(f"{'f(Hz)':>6} {'d/λ':>6} {'最高副瓣(dB)':>12}  说明")
print("-" * 70)
fine = [2800, 3120, 3500, 4000, 4500, 5000, 5500, 6000, 6240, 7000, 8000]
for f in fine:
    ratio, _ = grating_geometry(f)
    ang, lvl, _ = grating_lobe_level(f)
    note = ""
    if ratio < 0.5:
        note = "无栅瓣区"
    elif ratio < 1.0:
        note = "过渡区(±90°边缘抬升, 受Dolph压制)"
    else:
        note = "可视区内出现独立栅瓣峰"
    print(f"{f:>6} {ratio:>6.3f} {lvl:>12.2f}  {note}")

# ── 导出方向图数据（5 频点）供 Critic 复核 ──────────────────
import csv
import os
outdir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(outdir, "p0a1_pattern_data.csv")
with open(csv_path, "w", newline="") as fh:
    wtr = csv.writer(fh)
    wtr.writerow(["theta_deg"] + [f"AF_dB_{f}Hz" for f in FREQS])
    patterns = {f: array_factor_db(f) for f in FREQS}
    for i, th in enumerate(THETA):
        if abs(th * 100 - round(th * 100)) < 1e-6 and (round(th * 10) % 1 == 0):
            pass
    # 以 0.5° 步导出（够画图、文件不臃肿）
    idx = np.arange(0, len(THETA), 50)
    for i in idx:
        wtr.writerow([f"{THETA[i]:.2f}"] + [f"{patterns[f][i]:.3f}" for f in FREQS])
print(f"\n方向图数据已写盘: {csv_path}")

# ── 画方向图（直角坐标 0~90°，5 频点叠加）──────────────────
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for f in FREQS:
        ax.plot(THETA, array_factor_db(f), label=f"{f/1000:.2f} kHz (d/λ={D*f/C:.2f})")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xlim(0, 90)
    ax.set_ylim(-40, 2)
    ax.set_xlabel("Angle off broadside θ (deg)")
    ax.set_ylabel("Array factor (dB, normalized)")
    ax.set_title("Grating-lobe entry vs frequency  (N=16, d=55mm, Dolph-Cheby -20dB, broadside)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)
    png_path = os.path.join(outdir, "p0a1_grating_pattern.png")
    fig.tight_layout()
    fig.savefig(png_path, dpi=150)
    print(f"方向图已写盘: {png_path}")
except Exception as e:
    print(f"[warn] 绘图跳过: {e}")
