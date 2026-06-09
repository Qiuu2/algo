"""
TASK-MATLAB-M1 — 轨3 [L2-numpy] d=55 补算：SLL + WNG + DI 频率扫描
几何锁定 SC-S3-GEOM-01: N=16 / d=55mm / L=825mm / Dolph-Cheby-20dB / broadside / isotropic
作者：声学仿真专家 teammate (agent-acoustic-sim-v1)  日期：2026-05-29

说明：M0 发现 numpy 侧 d=55 缺 SLL/WNG/DI 标称值。本脚本用与 sweep_d55.py 完全相同假设
（点声源远场阵因子 + chebwin(16,20) 归一化 max=1 + C=343）独立补算，作为三轨对照的第三轨。
DI 沿用 sprint2/array_sweep.py 的 2D 线阵半球近似口径，以与 MATLAB 自写 2D-DI 直接对齐。
"""
import numpy as np
from scipy.signal.windows import chebwin
from scipy.signal import argrelmax

C = 343.0
N = 16
D_M = 0.055
FREQS = [100, 250, 500, 1000, 2000, 4000, 6000, 10000]

# 角度网格：0.01° 精细，覆盖 0~90°（前半球，broadside 对称）
THETA = np.linspace(0, 90, 9001)

def weights_dolph20():
    w = chebwin(N, 20)
    return w / w.max()

def af_db(theta_deg, freq, w):
    th = np.radians(theta_deg)
    k = 2 * np.pi * freq / C
    n = np.arange(N)
    phase = k * np.outer(np.sin(th), n * D_M)
    af = (w * np.exp(1j * phase)).sum(axis=1)
    mag = np.abs(af)
    ref = mag[0] if mag[0] > 1e-10 else mag.max()
    return 20 * np.log10(mag / (ref + 1e-30) + 1e-12)

def peak_sll(theta_deg, db):
    """峰值旁瓣级 dB（相对主瓣）。从主瓣外第一个零点之后找最高旁瓣峰。"""
    peak = db[0]
    null_idx = None
    for i in range(1, len(db)):
        if db[i] < peak - 35:
            null_idx = i
            break
    if null_idx is None:
        return -60.0
    sl = db[null_idx:]
    if len(sl) < 3:
        return float(sl.max() - peak)
    pk = argrelmax(sl, order=3)[0]
    if len(pk) == 0:
        return float(sl.max() - peak)
    return float(sl[pk].max() - peak)

def wng_db(w, freq):
    """白噪声增益(阵增益) WNG = |w^H a|^2 / (w^H w)，a=理想broadside导向(全1)。
    与 CTO p01 wng_db() 同口径（不除以 |a|^2）。标称(isotropic无误差)下与频率无关，
    等于 (Σw)^2 / Σw^2 → uniform 时 = N，上限 10log10(N)=12.04dB。"""
    a = np.ones(N)  # broadside steering vector (isotropic), 各阵元同相
    num = np.abs(np.vdot(w, a))**2
    den = np.vdot(w, w).real
    return float(10 * np.log10(num / den))

def di_2d(theta_deg, db):
    """2D 线阵半球 DI 近似（与 sprint2/array_sweep.py 同口径）。
    DI = 10log10(2 / ∫[0,π/2]|D|^2 sinθ dθ * 2)。"""
    th = np.radians(theta_deg)
    af_lin = 10 ** (db / 20)
    integrand = af_lin**2 * np.sin(th)
    int_half = np.trapezoid(integrand, th)
    integral = 2 * int_half
    if integral < 1e-12:
        return 0.0
    return float(10 * np.log10(2.0 / integral))

w = weights_dolph20()
# 标称 WNG 与频率无关（isotropic 无误差），但逐频点打印以示稳定
print(f"{'freq_Hz':>8} {'SLL_dB':>10} {'WNG_dB':>10} {'DI_2D_dB':>10}")
rows = []
for f in FREQS:
    db = af_db(THETA, f, w)
    sll = peak_sll(THETA, db)
    wng = wng_db(w, f)
    di = di_2d(THETA, db)
    rows.append((f, sll, wng, di))
    print(f"{f:>8} {sll:>10.3f} {wng:>10.3f} {di:>10.3f}")

# 落盘 CSV
import csv
out = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint3/audit/m1_numpy_d55_sll_wng_di.csv"
with open(out, "w", newline="") as fp:
    wr = csv.writer(fp)
    wr.writerow(["freq_hz", "SLL_dB", "WNG_dB", "DI_2D_dB"])
    for r in rows:
        wr.writerow([r[0], round(r[1], 3), round(r[2], 3), round(r[3], 3)])
print(f"\n[CSV] {out}")
print(f"WNG 理论上限 10log10(N)=10log10(16)={10*np.log10(16):.3f} dB (uniform)")
