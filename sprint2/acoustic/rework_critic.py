"""
⚠️ 历史归档/作废（PF-8，2026-05-29）：本文件含基于 d=30 错误几何（Sprint2 视觉估测值，已被拆机实测真值 d=55 取代，DEC-S3-GEOM-01）的结论/数据，仅作历史留痕，不可作任何决策依据。现行 d=55 基线见 decisions_log DEC-S3-GEOM-01 / PROJECT_HANDOVER.md。

ITC 定向音柱 — 声学仿真专家 Agent
Critic 返工脚本（针对 F-AC-01 / F-AC-02 两个 BLOCKER）
不重跑 48 组扫描，仅补充：
  F-AC-01: 模型隐含 BW + 不确定带 + 拟合优度图（实测点叠加到模型方向图）
  F-AC-02: 前后比 / 旁瓣 / 量纲说明 + 多维对比图 + d=30/35 对比 + 8kHz 栅瓣更正
作者：AcousticSimulationAgent v1.0
日期：2026-05-26
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.signal.windows import hann, chebwin
import csv
import os

OUT = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint2/acoustic"
C = 343.0

# ────────────────────────────────────────────────
# 竞品实测数据（1m, dB SPL）
# ────────────────────────────────────────────────
MEAS_ANGLES_DEG = np.array([0, 30, 60, 90, 150, 180])
MEAS_SPL = np.array([
    [103.2, 101.8, 98.5, 94.0, 95.7, 99.2],   # 250 Hz
    [110.5, 103.0, 95.6, 89.2, 93.4, 100.7],  # 500 Hz
    [110.9,  88.4, 84.0, 78.9, 82.6,  91.6],  # 1kHz
    [106.8,  82.7, 82.5, 82.0, 82.1,  88.5],  # 2kHz
    [106.6,  87.8, 85.9, 81.2, 78.1,  84.1],  # 4kHz
])
MEAS_FREQS = np.array([250, 500, 1000, 2000, 4000])
MEAS_NORM_DB = MEAS_SPL - MEAS_SPL[:, 0:1]

# ────────────────────────────────────────────────
# 核心函数
# ────────────────────────────────────────────────
def get_weights(N, win_type):
    if win_type == 'uniform':
        w = np.ones(N)
    elif win_type == 'hanning':
        w = hann(N)
    elif win_type == 'dolph20':
        w = chebwin(N, 20)
    elif win_type == 'dolph30':
        w = chebwin(N, 30)
    w = w / (np.abs(w).max() + 1e-30)
    return w

def array_factor_db(theta_deg_arr, N, d_m, freq_hz, win_type='uniform'):
    theta_rad = np.radians(theta_deg_arr)
    w = get_weights(N, win_type)
    k = 2 * np.pi * freq_hz / C
    n = np.arange(N)
    phase = k * np.outer(np.sin(theta_rad), n * d_m)
    af = (w * np.exp(1j * phase)).sum(axis=1)
    mag = np.abs(af)
    mag_ref = mag[0] if mag[0] > 1e-10 else mag.max()
    db = 20 * np.log10(mag / (mag_ref + 1e-30) + 1e-10)
    return db

def beamwidth_6db(theta_deg_arr, af_db):
    mask90 = theta_deg_arr <= 90.0
    th = theta_deg_arr[mask90]
    db = af_db[mask90]
    peak = db[0]
    below = np.where(db < peak - 6)[0]
    if len(below) == 0:
        return 180.0
    idx_right = below[0]
    if idx_right > 0:
        t0, t1 = th[idx_right - 1], th[idx_right]
        d0, d1 = db[idx_right - 1], db[idx_right]
        t_6dB = t0 + (peak - 6 - d0) / (d1 - d0) * (t1 - t0) if d1 != d0 else t0
    else:
        t_6dB = th[idx_right]
    return float(2 * t_6dB)

def front_back_ratio_model(N, d_m, freq_hz, win_type):
    """模型前后比：0°(broadside)与端射 90° 的差。
    注：线阵 broadside 阵列，θ=180° 物理上是另一侧端射，AF(180°)=AF(0°)（sin对称）。
    竞品实测"前后比"是 0° 与 180°（声学后方）的差，这取决于阵元/箱体的后向辐射，
    点声源阵因子模型无法预测真实后向辐射，此处给出模型在 90°(端射) 的衰减作为参考。"""
    db0 = 0.0  # broadside 归一化
    db90 = array_factor_db(np.array([0.0, 90.0]), N, d_m, freq_hz, win_type)[1]
    return db0 - db90

# ════════════════════════════════════════════════
# F-AC-01: 竞品 BW 重新评估
# ════════════════════════════════════════════════
print("=" * 60)
print("F-AC-01: 竞品波束宽度重新评估")
print("=" * 60)

# 1. 证明 4 点插值不可靠：0->30° 跌幅
print("\n竞品 0°→30° 跌幅（证明 -6dB 交点落在 0~30° 内）:")
for fi, f in [(2, '1kHz'), (3, '2kHz'), (4, '4kHz')]:
    drop = MEAS_NORM_DB[fi, 1]  # 30° 处归一化
    print(f"  {f}: 30°处={drop:.1f}dB (跌幅{abs(drop):.1f}dB >> 6dB) → -6dB点必在0~30°间")

# 2. 用反推模型（N=20, d=35mm, dolph20）推算模型隐含 BW
FIT_N, FIT_D_MM, FIT_WT = 20, 35, 'dolph20'
FIT_D_M = FIT_D_MM * 1e-3
theta_fine = np.linspace(0, 90, 9001)  # 0.01° 高分辨率

model_bw = {}
for fi, freq in [(2, 1000), (3, 2000), (4, 4000)]:
    db = array_factor_db(theta_fine, FIT_N, FIT_D_M, freq, FIT_WT)
    bw = beamwidth_6db(theta_fine, db)
    model_bw[freq] = bw
    print(f"\n模型隐含 BW @{freq}Hz (N={FIT_N},d={FIT_D_MM}mm,{FIT_WT}): {bw:.1f}°")

# 3. 不确定带：考虑 Top-3 拟合候选的 BW 散布
TOP3 = [(20, 35, 'dolph20'), (32, 28, 'dolph20'), (24, 25, 'dolph20')]
print("\n模型隐含 BW 不确定带（Top-3 反推候选）:")
bw_band = {1000: [], 2000: [], 4000: []}
for N, d_mm, wt in TOP3:
    for freq in [1000, 2000, 4000]:
        db = array_factor_db(theta_fine, N, d_mm * 1e-3, freq, wt)
        bw_band[freq].append(beamwidth_6db(theta_fine, db))
for freq in [1000, 2000, 4000]:
    arr = bw_band[freq]
    print(f"  {freq}Hz: {min(arr):.1f}°~{max(arr):.1f}° (中心 {model_bw[freq]:.1f}°)")

# ────────────────────────────────────────────────
# 拟合优度图：实测点叠加到模型方向图
# ────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 6), subplot_kw={'projection': 'polar'})
fig.suptitle(f'F-AC-01: Competitor Fit Quality — Model (N={FIT_N},d={FIT_D_MM}mm,Dolph-20dB) vs Measured Points',
             fontsize=12)

def make_polar_full(theta_deg_half, af_db_half):
    th_half = np.radians(theta_deg_half)
    th_p1 = th_half
    db_p1 = af_db_half
    th_p2 = np.pi - th_half[::-1]
    db_p2 = af_db_half[::-1]
    th_p3 = np.pi + th_half
    db_p3 = af_db_half
    th_p4 = 2 * np.pi - th_half[::-1]
    db_p4 = af_db_half[::-1]
    th_full = np.concatenate([th_p1, th_p2[1:], th_p3[1:], th_p4[1:]])
    db_full = np.concatenate([db_p1, db_p2[1:], db_p3[1:], db_p4[1:]])
    return th_full, db_full

theta_plot = np.linspace(0, 90, 901)
for ax, (fi, freq, flabel) in zip(axes, [(2, 1000, '1kHz'), (3, 2000, '2kHz'), (4, 4000, '4kHz')]):
    # 模型方向图
    db_model = array_factor_db(theta_plot, FIT_N, FIT_D_M, freq, FIT_WT)
    th_full, db_full = make_polar_full(theta_plot, db_model)
    db_full_clip = np.clip(db_full, -30, 0)
    ax.plot(th_full, db_full_clip + 30, color='navy', lw=1.5, label='Reverse-engineered model')

    # 实测 6 点（散点，全角度）
    meas_db = MEAS_NORM_DB[fi]
    meas_th = np.radians(MEAS_ANGLES_DEG)
    meas_clip = np.clip(meas_db, -30, 0)
    ax.scatter(meas_th, meas_clip + 30, color='red', s=80, zorder=5, marker='o',
               label='Measured (6 pts)', edgecolors='black')
    # 镜像实测点（对称侧）
    ax.scatter(-meas_th, meas_clip + 30, color='red', s=80, zorder=5, marker='o',
               edgecolors='black', alpha=0.6)

    ax.set_title(f'{flabel}  (model BW={model_bw[freq]:.1f}°)', fontsize=10, pad=12)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 32)
    ax.set_yticks([0, 10, 20, 30])
    ax.set_yticklabels(['-30', '-20', '-10', '0dB'], fontsize=7)
    ax.legend(loc='lower right', fontsize=7)

plt.tight_layout()
fit_png = os.path.join(OUT, 'competitor_fit_quality.png')
plt.savefig(fit_png, dpi=150)
plt.close()
print(f"\n拟合优度图已保存: {fit_png}")

# ════════════════════════════════════════════════
# F-AC-02: 前后比 / 旁瓣 / 量纲对比
# ════════════════════════════════════════════════
print("\n" + "=" * 60)
print("F-AC-02: 多维对比（前后比/旁瓣/量纲）")
print("=" * 60)

# 竞品前后比（0° - 180°），实测明确给出
comp_fb = {}
for fi, freq in [(2, 1000), (3, 2000), (4, 4000)]:
    fb = MEAS_NORM_DB[fi, 0] - MEAS_NORM_DB[fi, 5]  # 0° - 180°
    comp_fb[freq] = -fb  # MEAS_NORM_DB[fi,0]=0, 所以 = -(0 - meas[180]) = meas衰减量
    # 修正：前后比 = SPL(0) - SPL(180) = -MEAS_NORM_DB[fi,5]
    comp_fb[freq] = -MEAS_NORM_DB[fi, 5]
print("\n竞品实测前后比（0° vs 180°）:")
for freq in [1000, 2000, 4000]:
    print(f"  {freq}Hz: {comp_fb[freq]:.1f}dB")

# 3 候选方案（从最终报告）
CANDIDATES = [
    ('方案1-经济档', 16, 35, 'uniform'),
    ('方案2-均衡档', 24, 35, 'dolph30'),
    ('方案3-高性能档', 32, 35, 'uniform'),
]

# 重新计算每个候选的 SLL（用之前的 peak_sll 逻辑）
from scipy.signal import argrelmax
def peak_sll(theta_deg_arr, af_db):
    mask90 = theta_deg_arr <= 90.0
    th = theta_deg_arr[mask90]
    db = af_db[mask90]
    peak = db[0]
    null_idx = None
    for i in range(1, len(db)):
        if db[i] < peak - 35:
            null_idx = i
            break
    if null_idx is None:
        return -60.0
    sidelobe_db = db[null_idx:]
    if len(sidelobe_db) < 3:
        return float(sidelobe_db.max() - peak)
    peaks = argrelmax(sidelobe_db, order=3)[0]
    if len(peaks) == 0:
        return float(sidelobe_db.max() - peak)
    return float(sidelobe_db[peaks].max() - peak)

cand_data = {}
for label, N, d_mm, wt in CANDIDATES:
    d_m = d_mm * 1e-3
    fb = {}
    sll = {}
    for freq in [1000, 2000, 4000]:
        db = array_factor_db(theta_fine, N, d_m, freq, wt)
        fb[freq] = front_back_ratio_model(N, d_m, freq, wt)
        sll[freq] = peak_sll(theta_fine, db)
    cand_data[label] = {'N': N, 'd_mm': d_mm, 'wt': wt, 'fb': fb, 'sll': sll}
    print(f"\n{label} (N={N},d={d_mm}mm,{wt}):")
    for freq in [1000, 2000, 4000]:
        print(f"  {freq}Hz: 端射衰减(0vs90°)={fb[freq]:.1f}dB, SLL={sll[freq]:.1f}dB")

# ────────────────────────────────────────────────
# 多维对比图：前后比/旁瓣随频率
# ────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('F-AC-02: Candidates vs Competitor — Front-Back & Sidelobe vs Frequency', fontsize=12)

freqs_x = [1000, 2000, 4000]
colors = ['tab:blue', 'tab:green', 'tab:red']
labels_en = ['Cand1 (N16/d35/uniform)', 'Cand2 (N24/d35/dolph30)', 'Cand3 (N32/d35/uniform)']

# 左图：端射衰减 / 前后比
ax = axes[0]
for (label, _, _, _), color, len_str in zip(CANDIDATES, colors, labels_en):
    fb_vals = [cand_data[label]['fb'][f] for f in freqs_x]
    ax.plot(freqs_x, fb_vals, 'o-', color=color, label=f'{len_str} (model 0vs90°)', lw=2)
comp_fb_vals = [comp_fb[f] for f in freqs_x]
ax.plot(freqs_x, comp_fb_vals, 's--', color='black', label='Competitor F/B (0vs180° measured)', lw=2, ms=8)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Attenuation (dB)')
ax.set_title('Front-Back / Endfire Attenuation\n(model=0vs90°, competitor=0vs180°: NOT directly comparable)')
ax.set_xscale('log')
ax.set_xticks(freqs_x)
ax.set_xticklabels(['1k', '2k', '4k'])
ax.legend(fontsize=7, loc='best')
ax.grid(True, alpha=0.3)

# 右图：旁瓣级
ax = axes[1]
for (label, _, _, _), color, len_str in zip(CANDIDATES, colors, labels_en):
    sll_vals = [abs(cand_data[label]['sll'][f]) for f in freqs_x]
    ax.plot(freqs_x, sll_vals, 'o-', color=color, label=len_str, lw=2)
# 竞品旁瓣：从实测 60°/90° 附近近似（实测无法精确分辨旁瓣，标注为参考下界）
comp_sll_approx = [abs(MEAS_NORM_DB[fi, 2]) for fi in [2, 3, 4]]  # 60°处作为旁瓣区参考
ax.plot(freqs_x, comp_sll_approx, 's--', color='gray',
        label='Competitor @60° (sidelobe region ref, lower bound)', lw=2, ms=8)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('|Sidelobe Level| (dB, higher=better suppression)')
ax.set_title('Peak Sidelobe Level vs Frequency')
ax.set_xscale('log')
ax.set_xticks(freqs_x)
ax.set_xticklabels(['1k', '2k', '4k'])
ax.legend(fontsize=7, loc='best')
ax.grid(True, alpha=0.3)

plt.tight_layout()
multidim_png = os.path.join(OUT, 'candidates_fb_sll_vs_freq.png')
plt.savefig(multidim_png, dpi=150)
plt.close()
print(f"\n多维对比图已保存: {multidim_png}")

# ════════════════════════════════════════════════
# 栅瓣更正：8kHz / SB3 d/λ 检查
# ════════════════════════════════════════════════
print("\n" + "=" * 60)
print("栅瓣更正：d=30mm vs d=35mm 在 4.9k-8kHz")
print("=" * 60)

print("\nd/λ 比值（栅瓣条件 d/λ ≥ 0.5 即出现栅瓣）:")
for d_mm in [30, 35]:
    print(f"\n  d={d_mm}mm:")
    for freq in [4000, 4900, 6000, 8000]:
        lam = C / freq
        ratio = (d_mm * 1e-3) / lam
        d_lam2 = (d_mm * 1e-3) / (lam / 2)
        # 栅瓣可见角度（broadside阵）
        if d_lam2 > 1.0:
            gl_angle = np.degrees(np.arcsin(lam / (d_mm * 1e-3) - 0)) if lam / (d_mm*1e-3) <= 1 else None
            gl_status = f"栅瓣! 出现于±{gl_angle:.0f}°" if gl_angle else "栅瓣"
        elif d_lam2 > 0.9:
            gl_status = "接近栅瓣阈值（旁瓣抬升）"
        else:
            gl_status = "无栅瓣"
        print(f"    {freq}Hz: d/λ={ratio:.3f}, d/(λ/2)={d_lam2:.3f} → {gl_status}")

# d=35mm 在 8kHz 的栅瓣角度
lam8k = C / 8000
d35_lam8 = 0.035 / lam8k
print(f"\n  ★ 更正确认：d=35mm @8kHz, d/λ={d35_lam8:.3f} (>0.5)")
ratio_arg = lam8k / 0.035
if ratio_arg <= 1:
    gl_ang = np.degrees(np.arcsin(ratio_arg))
    print(f"     栅瓣出现于 ±{gl_ang:.1f}° → SB3(4.9-8kHz)确有栅瓣抬升风险")

print("\n所有返工计算完成！")
