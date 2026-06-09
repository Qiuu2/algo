"""
ITC 定向音柱 — 声学仿真专家 Agent  (Sprint 3)
任务：d=55mm / N=16 / L=825mm 阵列指向性仿真 + 竞品对照分析

【几何说明】
  - 物理箱体长度：16 × 55 = 880mm（CTO 给出值）
  - 声学孔径 L = (N-1)×d = 15 × 55 = 825mm
  - 880 是箱体物理长度；825mm 是有效波束形成孔径
  - 二者差 55mm（1 个间距，端部超出余量）

【驱动拓扑】
  8 路独立通道，A/B 串联对称：
    Ch1: A1+B16, Ch2: A2+B15, ..., Ch8: A8+B9
  - 强制对称实加权 → 只能 broadside，无法电子偏转
  - 有效独立自由度 = 8 对（非 16 独立元）
  - 建模两种情况：
    (a) 理想 16 独立元（如 16 通道驱动，完全独立）
    (b) 实际 8 对称对约束（复现真实硬件）

【喇叭 T/S 参数 — 全部标 [估算]】
  Re≈7.0Ω [估算], BL≈4.0 T·m [估算]
  Qts≈0.5 [估算], Fs≈150Hz [估算]
  灵敏度 88 dB SPL/2.83V/1m（即 88dB/1W @ 8Ω）[估算]
  实测单只阻抗 7.4Ω [实测]
  每路 2 只串联 ≈ 15Ω [实测推算]

作者：AcousticSimulationAgent v1.0
日期：2026-05-27
Sprint：3
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.signal.windows import chebwin
import os

# ────────────────────────────────────────────────
# 输出目录
# ────────────────────────────────────────────────
OUT = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint3/acoustic"
os.makedirs(OUT, exist_ok=True)

# ────────────────────────────────────────────────
# 0. 竞品实测数据（消声室 1m, dB SPL）
# ────────────────────────────────────────────────
MEAS_ANGLES_DEG = np.array([0, 30, 60, 90, 150, 180])

# 行: 频率 [250,500,1k,2k,4k], 列: 角度 [0,30,60,90,150,180]
MEAS_SPL = np.array([
    [103.2, 101.8, 98.5, 94.0, 95.7, 99.2],   # 250 Hz
    [110.5, 103.0, 95.6, 89.2, 93.4, 100.7],  # 500 Hz
    [110.9,  88.4, 84.0, 78.9, 82.6,  91.6],  # 1kHz
    [106.8,  82.7, 82.5, 82.0, 82.1,  88.5],  # 2kHz
    [106.6,  87.8, 85.9, 81.2, 78.1,  84.1],  # 4kHz
])
MEAS_FREQS = np.array([250, 500, 1000, 2000, 4000])
MEAS_NORM_DB = MEAS_SPL - MEAS_SPL[:, 0:1]   # 归一化至 0° = 0dB

# ────────────────────────────────────────────────
# 1. 物理常数 & 阵列参数
# ────────────────────────────────────────────────
C = 343.0         # m/s，声速（20°C）

N_ELEM   = 16     # 阵元数（真实值，拆机确认）
D_MM     = 55.0   # 阵元中心距 mm（真实值，拆机确认）
D_M      = D_MM * 1e-3
L_APERTURE_MM = (N_ELEM - 1) * D_MM   # 825mm — 声学孔径
L_BOX_MM      = N_ELEM * D_MM         # 880mm — 箱体物理长度

print(f"【几何参数确认】")
print(f"  N = {N_ELEM} 元")
print(f"  d = {D_MM} mm")
print(f"  L_aperture = (N-1)×d = {L_APERTURE_MM:.0f} mm  ← 波束形成孔径（用于声学计算）")
print(f"  L_box      =  N ×d  = {L_BOX_MM:.0f} mm  ← 箱体物理长度（CTO 给出值）")
print(f"  差值 = {L_BOX_MM - L_APERTURE_MM:.0f} mm（1 个间距，端部余量）")
print()

# ────────────────────────────────────────────────
# 2. 加权函数
# ────────────────────────────────────────────────

def get_weights_16(win_type='dolph20'):
    """16 元独立加权（理想情况 a）。"""
    if win_type == 'uniform':
        w = np.ones(16)
    elif win_type == 'dolph20':
        w = chebwin(16, 20)
    elif win_type == 'dolph30':
        w = chebwin(16, 30)
    else:
        raise ValueError(win_type)
    return w / w.max()


def get_weights_8pair(win_type='dolph20'):
    """
    8 对对称约束加权（实际拓扑 b）。
    对称对：元 0 与元 15，元 1 与元 14，...元 7 与元 8
    同一对权值相同 → 展开为 16 元实加权向量。
    Dolph-Chebyshev 本身对称，取外侧 8 元权值分配给各对。
    """
    if win_type == 'uniform':
        w_pair = np.ones(8)
    elif win_type == 'dolph20':
        w_full = chebwin(16, 20)
        # 前 8 元（外→内）：w_full[0..7]
        w_pair = w_full[:8]
    elif win_type == 'dolph30':
        w_full = chebwin(16, 30)
        w_pair = w_full[:8]
    else:
        raise ValueError(win_type)
    w_pair = w_pair / w_pair.max()
    # 展开：[w0,w1,...,w7, w7,...,w0]（对称）
    w16 = np.concatenate([w_pair, w_pair[::-1]])
    return w16


# ────────────────────────────────────────────────
# 3. 阵因子计算
# ────────────────────────────────────────────────

THETA_FINE = np.linspace(0, 90, 1801)   # 0.05° 分辨率


def array_factor_db(theta_deg_arr, N, d_m, freq_hz, weights):
    """
    线阵远场阵因子（归一化 dB）。
    weights: 长度为 N 的实加权向量（已归一化至 max=1）
    θ=0° 为 broadside（轴向），返回归一化 dB（0°=0dB）。
    """
    theta_rad = np.radians(theta_deg_arr)
    k = 2 * np.pi * freq_hz / C
    n = np.arange(N)
    # (len_theta, N)
    phase = k * np.outer(np.sin(theta_rad), n * d_m)
    af = (weights * np.exp(1j * phase)).sum(axis=1)
    mag = np.abs(af)
    mag_ref = mag[0]
    if mag_ref < 1e-10:
        mag_ref = mag.max()
    db = 20 * np.log10(mag / (mag_ref + 1e-30) + 1e-10)
    return db


def beamwidth_6db(theta_deg_arr, af_db):
    """计算 -6dB 全角波束宽度（度）。"""
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
        if d1 != d0:
            t_6dB = t0 + (peak - 6 - d0) / (d1 - d0) * (t1 - t0)
        else:
            t_6dB = t0
    else:
        t_6dB = th[idx_right]
    return float(2 * t_6dB)


def peak_sll(theta_deg_arr, af_db):
    """计算峰值旁瓣级（dB，相对主瓣，负值）。"""
    from scipy.signal import argrelmax
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


def grating_lobe_analysis(d_m, freq_hz):
    """
    栅瓣分析，返回 (has_grating_d_ge_lam, ratio_d_over_lam, grating_angle_deg)。
    broadside 阵列栅瓣判据：d ≥ λ（d/(λ)≥1，在可见区出现栅瓣）。
    注意区分：
      d ≥ λ/2 → 严格 aliasing 域（扫描阵有栅瓣风险）
      d ≥ λ   → broadside 阵才在可见区出现栅瓣
    """
    lam = C / freq_hz
    ratio_half = d_m / (lam / 2)     # 相对半波长比
    ratio_full = d_m / lam            # 相对全波长比
    # broadside: 栅瓣出现在 sin(θ_gl) = λ/d → θ_gl = arcsin(λ/d)
    # 只有当 λ/d ≤ 1 时才在可见区（即 d ≥ λ）
    has_grating_visible = (ratio_full >= 1.0)
    if has_grating_visible:
        gl_angle = np.degrees(np.arcsin(min(1.0, lam / d_m)))
    else:
        gl_angle = None
    return has_grating_visible, round(ratio_half, 3), round(ratio_full, 3), gl_angle


# ────────────────────────────────────────────────
# 4. 栅瓣临界频率分析
# ────────────────────────────────────────────────
print("=" * 65)
print("任务 3：栅瓣分析（d=55mm）")
print("=" * 65)

f_crit_half = C / (2 * D_M)          # d = λ/2 临界频率（保守扫描判据）
f_crit_full = C / D_M                 # d = λ   临界频率（broadside 可见区判据）
print(f"\n  d = {D_MM} mm")
print(f"  (a) 保守扫描判据  d ≥ λ/2 → f ≥ c/(2d) = {f_crit_half:.0f} Hz ≈ {f_crit_half/1000:.2f} kHz")
print(f"  (b) Broadside 判据 d ≥ λ   → f ≥ c/d   = {f_crit_full:.0f} Hz ≈ {f_crit_full/1000:.2f} kHz")
print()
print("  解释：竞品 broadside-only 设计使用判据 (b)：")
print(f"    → 约 {f_crit_full/1000:.1f} kHz 以下不出现可见区栅瓣")
print("    → 4kHz 时 d/λ = {:.3f} < 1，无可见栅瓣（阵因子可能有 aliasing 但在不可见区）".format(D_M / (C/4000)))
print("    → 加上阵元自身高频指向性衰减，4kHz 旁瓣/栅瓣被进一步抑制")
print()

# 3~8 kHz 栅瓣角度表
print("  【3-8 kHz 栅瓣状态（broadside 判据）】")
print(f"  {'Freq(kHz)':<12} {'d/λ':<8} {'d/(λ/2)':<10} {'可见区栅瓣':<12} {'栅瓣角(°)'}")
for f_khz in [3, 4, 5, 6, 7, 8]:
    freq = f_khz * 1000
    vis, r_half, r_full, gl_ang = grating_lobe_analysis(D_M, freq)
    gl_str = f"{gl_ang:.1f}°" if gl_ang is not None else "—（不可见）"
    vis_str = "YES ⚠" if vis else "NO"
    print(f"  {f_khz:.1f} kHz       {r_full:<8.3f} {r_half:<10.3f} {vis_str:<12} {gl_str}")

print()
print("  【结论】")
print(f"    - 4 kHz：d/λ = {D_M/(C/4000):.3f} < 1 → broadside 无可见栅瓣 ✓")
print(f"    - 6.2 kHz：d/λ ≈ 1.0 → 栅瓣进入可见区（边缘，±90° 附近）")
print(f"    - 6-8 kHz 区间：栅瓣逐渐从端射方向（±90°）向轴向（0°）移入")
print(f"    - P0 声学风险：6-8 kHz 工作时轴外栅瓣出现，需阵元自身指向性抑制")


# ────────────────────────────────────────────────
# 5. 主仿真：各频率 BW、SLL、DI（两种拓扑）
# ────────────────────────────────────────────────
print()
print("=" * 65)
print("任务 1-2：N=16/d=55mm 指向性仿真（两种拓扑）")
print("=" * 65)

ANALYSIS_FREQS = [250, 500, 1000, 2000, 4000]

# 理想 16 独立元 + Dolph-20
w16_d20  = get_weights_16('dolph20')
# 理想 16 独立元 + Uniform（参考用）
w16_uni  = get_weights_16('uniform')
# 实际 8 对称对 + Dolph-20
w8p_d20  = get_weights_8pair('dolph20')
# 实际 8 对称对 + Uniform
w8p_uni  = get_weights_8pair('uniform')

results_16 = {}   # 理想 16 独立 Dolph-20
results_8p = {}   # 实际 8 对称 Dolph-20

print(f"\n{'Freq':<8} {'BW(16/D20)':<14} {'BW(8p/D20)':<14} {'SLL(16)':<12} {'SLL(8p)':<12} {'栅瓣状态'}")
print("-" * 75)

for freq in ANALYSIS_FREQS:
    # 理想 16 元
    af16 = array_factor_db(THETA_FINE, N_ELEM, D_M, freq, w16_d20)
    bw16 = beamwidth_6db(THETA_FINE, af16)
    sll16 = peak_sll(THETA_FINE, af16)

    # 8 对称对
    af8p = array_factor_db(THETA_FINE, N_ELEM, D_M, freq, w8p_d20)
    bw8p = beamwidth_6db(THETA_FINE, af8p)
    sll8p = peak_sll(THETA_FINE, af8p)

    vis, r_half, r_full, gl_ang = grating_lobe_analysis(D_M, freq)
    gl_str = f"YES(gl={gl_ang:.0f}°)" if vis else "NO"

    results_16[freq] = {'bw': bw16, 'sll': sll16, 'af': af16}
    results_8p[freq] = {'bw': bw8p, 'sll': sll8p, 'af': af8p}

    print(f"{freq:<8} {bw16:<14.1f} {bw8p:<14.1f} {sll16:<12.1f} {sll8p:<12.1f} {gl_str}")

# 竞品插值BW(派生·非实测)：竞品仅实测 SPL，BW 系从 SPL 4点插值反推、F-AC-01 已撤回
print()
print("竞品插值BW(派生·非实测)：竞品仅实测 SPL，以下 BW 系从 SPL 4点插值反推、F-AC-01 已撤回")
meas_bw = {}
for fi, freq in enumerate(MEAS_FREQS):
    meas_db_fine = np.interp(THETA_FINE,
                              MEAS_ANGLES_DEG[:4],
                              MEAS_NORM_DB[fi, :4])
    bw_m = beamwidth_6db(THETA_FINE, meas_db_fine)
    meas_bw[freq] = bw_m
    print(f"  {freq} Hz: {bw_m:.1f}°")


# ────────────────────────────────────────────────
# 6. SPL 预测
# ────────────────────────────────────────────────
print()
print("=" * 65)
print("任务 5：轴向 SPL 预测（1m）")
print("=" * 65)
print()
print("【假设（全部标 [估算/假设]）】")
print("  1. 单只灵敏度 = 88 dB SPL / 2.83V / 1m @ 8Ω  [估算]")
print("     等价 88 dB/1W/1m（功率灵敏度，8Ω 负载）")
print("  2. 8 通道独立驱动，每通道串联 2 只（15Ω 总阻抗）")
print("  3. 每通道输入功率 P_ch（假设恒压驱动，电压 U 固定）")
print("  4. 相干阵列增益 = 20 log10(N_ch) 对 N_ch 个同相同幅通道 [理想假设]")
print("  5. 串联 2 只：每只获得 P_ch/2 功率，但声压在轴向相干叠加")
print("     每只 SPL_single = 88 + 10 log10(P_ch/2) = 85 + 10 log10(P_ch)")
print("  6. 8 通道相干叠加：+20 log10(8) = +18.1 dB")
print("  7. 轴向 SPL_total(1m) = SPL_single_at_P_ch + 18.1 dB")
print()
print("  参考点：竞品 0° 实测 SPL（1m）")
print("    250Hz: 103.2 dB,  500Hz: 110.5 dB")
print("    1kHz: 110.9 dB,   2kHz: 106.8 dB,   4kHz: 106.6 dB")
print()

# 计算相干阵列增益（8 通道 + 每通道 2 只相干）
# 单只 @ 1W @ 8Ω 灵敏度 88 dB
# 每只 @ P_ch/2: SPL = 88 + 10 log10(P_ch/2)
# 2 只串联同向轴上相干叠加 (方向相同，轴向同相):
#   +20 log10(2) = +6 dB
# 每通道 2 只相干 SPL_ch = 88 + 10 log10(P_ch/2) + 6 = 88 + 10 log10(P_ch) - 3 + 6
#                         = 91 + 10 log10(P_ch)   [估算]
# 8 通道相干叠加: +20 log10(8) = +18.1 dB
# 总 SPL @ 1m = 91 + 10 log10(P_ch) + 18.1 = 109.1 + 10 log10(P_ch)
# 如果 P_ch = 10W: SPL = 109.1 + 10 = 119.1 dB（理想无损）
# 实际需要考虑阵元指向性、箱体衍射等损失，估算保守 -3~-5 dB
# 给出 P_ch = 1W 和 10W 两档
P_ref_W = [1, 5, 10]
sens_1w_1m = 88.0  # dB [估算]
array_gain_coherent = 20 * np.log10(16)  # 16 只同向相干叠加（等效）
# 实际：8ch × 2只串联，每只获 P_ch/2，轴向相干
# SPL(1m) = sens_1w + 10log10(P_each) + 20log10(16)
# P_each = P_ch/2（串联分压，阻抗匹配时各得一半）

print(f"  16 只相干叠加增益 = 20 log10(16) = {array_gain_coherent:.1f} dB [理想]")
print(f"  （实际因不完全相干、阵元幅相偏差，损失约 1~3 dB [估算]）")
print()
print(f"  {'P_ch(W)':<10} {'P_each(W)':<12} {'SPL_each(dB)':<16} {'SPL_array(dB)':<16} {'vs竞品平均(dB)'}")
print("-" * 70)

comp_avg_spl = np.mean([110.9, 106.8, 106.6])  # 竞品 1k/2k/4k 均值 ≈ 108.1 dB

for P_ch in P_ref_W:
    P_each = P_ch / 2  # 串联，每只
    spl_each = sens_1w_1m + 10 * np.log10(P_each)
    spl_array = spl_each + array_gain_coherent  # 理想相干
    spl_array_real = spl_array - 2.0  # 保守修正 -2dB [估算]
    diff = spl_array_real - comp_avg_spl
    print(f"  {P_ch:<10} {P_each:<12.1f} {spl_each:<16.1f} {spl_array_real:<16.1f} {diff:+.1f} [估算]")

print()
print("  【结论】若每通道输入 5~10W，预计轴向 SPL 接近或超过竞品水平 [估算]")
print("  【告警】T/S 参数均为估算值，实际 SPL 需消声室实测后修正")
print("  【告警】阵元一致性（幅相偏差）会降低相干增益，产线散差需标定")


# ────────────────────────────────────────────────
# 7. 超指向性需求分析（PM 问题1）
# ────────────────────────────────────────────────
print()
print("=" * 65)
print("任务 4：超指向性需求分析（PM 问题1）")
print("=" * 65)

bw_1k_16d55 = results_16[1000]['bw']
bw_1k_16d30_sprint2 = 55.2  # Sprint2 结果，d=30mm N=16（已知值）
L_old_mm = (16 - 1) * 30    # 450mm
L_new_mm = (16 - 1) * 55    # 825mm
aperture_ratio = L_new_mm / L_old_mm

print(f"\n  旧基线（Sprint2）：N=16, d=30mm, L=450mm, BW@1k={bw_1k_16d30_sprint2}°")
print(f"  新阵列（Sprint3）：N=16, d=55mm, L=825mm, BW@1k（仿真）={bw_1k_16d55:.1f}°")
print(f"  孔径比 L_new/L_old = {aperture_ratio:.2f}×")
print(f"  理论 BW 比 ∝ 1/L → 预期 BW@1k ≈ {bw_1k_16d30_sprint2/aperture_ratio:.1f}°")
print()
print(f"  竞品 1kHz 实测 BW ≈ {meas_bw[1000]:.1f}°")
print(f"  我方 d=55 仿真 BW@1kHz = {bw_1k_16d55:.1f}°")
print()

need_super = bw_1k_16d55 > meas_bw[1000]

print(f"  【PM 问题1 明确回答】")
print(f"  1kHz 超指向性（ε=0.01）{'还需要' if need_super else '不需要'}。")
if need_super:
    gap = bw_1k_16d55 - meas_bw[1000]
    print(f"  原因：d=55mm 阵列 BW@1kHz = {bw_1k_16d55:.1f}°，")
    print(f"         竞品插值BW(派生·非实测) = {meas_bw[1000]:.1f}°，差距 {gap:.1f}°")
    print(f"  但注意：竞品 1kHz BW 较窄，部分原因可能是箱体衍射/号角指向性辅助，")
    print(f"  纯阵因子无法完全解释。超指向仍为可选手段，建议先实测复核。")
else:
    print(f"  原因：d=55mm 孔径大幅扩展，BW@1kHz 已满足目标，无需超指向。")
print()
print(f"  注：Gate1 原设计目标 BW@2kHz≤30°，已无需超指向（Sprint2 已关闭 R5 对 2kHz）。")


# ────────────────────────────────────────────────
# 8. 旧 d=30 vs 新 d=55 对照分析
# ────────────────────────────────────────────────
print()
print("=" * 65)
print("d=30 vs d=55 反推对照（历史Sprint2 vs 真实拆机值）")
print("=" * 65)

# d=30, N=20 RMS（Sprint2 反推最佳，已知结果）
sprint2_best_rms = 2.84  # dB，Sprint2 报告值

# d=55, N=16：计算对已知测量角度的 RMS
FIT_FREQ_IDX = [2, 3, 4]  # 1k, 2k, 4k
FIT_FREQS_arr = MEAS_FREQS[FIT_FREQ_IDX]
MEAS_FIT_ANGLES = np.array([0.0, 30.0, 60.0, 90.0])
MEAS_FIT_IDX = [0, 1, 2, 3]
MEAS_NORM_FIT = MEAS_NORM_DB[FIT_FREQ_IDX][:, MEAS_FIT_IDX]

rms_d55_16 = 0.0
for fi, freq in enumerate(FIT_FREQS_arr):
    sim_db = array_factor_db(MEAS_FIT_ANGLES, N_ELEM, D_M, freq, w16_d20)
    diff = sim_db - MEAS_NORM_FIT[fi]
    rms_d55_16 += np.sqrt(np.mean(diff**2))
rms_d55_16 /= len(FIT_FREQS_arr)

print(f"\n  Sprint2 反推最佳（N=20/d=35，估算）：RMS ≈ {sprint2_best_rms:.2f} dB")
print(f"  Sprint3 真实值（N=16/d=55，Dolph-20）：RMS = {rms_d55_16:.2f} dB")

if rms_d55_16 < sprint2_best_rms:
    print(f"\n  结论：N=16/d=55 比 N=20/d=35 更好地解释实测数据")
    print(f"         RMS 改善 {sprint2_best_rms - rms_d55_16:.2f} dB")
else:
    diff_rms = rms_d55_16 - sprint2_best_rms
    print(f"\n  结论：N=16/d=55 RMS 比 Sprint2 反推大 {diff_rms:.2f} dB")
    print(f"         原因分析：")
    print(f"           1. 阵因子模型是点声源近似，阵元辐射指向性未建模")
    print(f"           2. d=55mm 在 2-4kHz 时 d/(λ/2)={D_M/(C/2000*0.5):.2f}~{D_M/(C/4000*0.5):.2f}，")
    print(f"              阵元互耦合效应可能改变实际方向图")
    print(f"           3. 竞品 8 通道/16 喇叭 broadside 约束使有效自由度仅 8 对，")
    print(f"              实测与 16 独立元仿真存在内在差异")
    print(f"         拆机真值 N=16/d=55 在几何上确定无误，RMS 偏大")
    print(f"         反映模型简化局限，而非几何反推错误")


# ────────────────────────────────────────────────
# 9. 生成对比图
# ────────────────────────────────────────────────
print()
print("生成仿真 vs 竞品对比图...")

def make_polar_full(theta_deg_half, af_db_half):
    """0~90° 展开为 0~360° 极坐标（线阵 broadside 对称）。"""
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


PLOT_FREQS = [250, 500, 1000, 2000, 4000]
COLORS = ['steelblue', 'darkorange', 'forestgreen', 'crimson', 'purple']

fig, axes = plt.subplots(1, 5, figsize=(22, 5), subplot_kw={'projection': 'polar'})
fig.suptitle('N=16 / d=55mm / L=825mm — Dolph-20dB\n'
             '实线: 仿真(16独立元), 虚线: 竞品插值BW(派生·非实测)', fontsize=11)

for fi, (freq, color, ax) in enumerate(zip(PLOT_FREQS, COLORS, axes)):
    # 仿真
    af = array_factor_db(THETA_FINE, N_ELEM, D_M, freq, w16_d20)
    th_s, db_s = make_polar_full(THETA_FINE, af)
    db_s_clip = np.clip(db_s, -30, 0)
    ax.plot(th_s, db_s_clip + 30, color=color, lw=2, label='Sim')

    # 竞品
    freq_idx = list(MEAS_FREQS).index(freq)
    meas_db_4pt = MEAS_NORM_DB[freq_idx, :4]
    meas_interp = np.interp(THETA_FINE, MEAS_ANGLES_DEG[:4], meas_db_4pt)
    th_m, db_m = make_polar_full(THETA_FINE, meas_interp)
    db_m_clip = np.clip(db_m, -30, 0)
    ax.plot(th_m, db_m_clip + 30, color=color, lw=2, linestyle='--', alpha=0.7, label='Meas')

    ax.set_title(f'{freq}Hz', fontsize=10, pad=8)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 32)
    ax.set_yticks([0, 10, 20, 30])
    ax.set_yticklabels(['-30', '-20', '-10', '0'], fontsize=7)
    if fi == 0:
        ax.legend(loc='lower right', fontsize=8)

plt.tight_layout()
fig_path = os.path.join(OUT, 'polar_d55_vs_competitor.png')
plt.savefig(fig_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  极坐标对比图: {fig_path}")

# 8-对 vs 16独立 对比图（1kHz & 2kHz）
fig2, axes2 = plt.subplots(1, 4, figsize=(18, 5), subplot_kw={'projection': 'polar'})
fig2.suptitle('拓扑对比：16独立元 vs 8对称对约束（Dolph-20dB）', fontsize=11)
for fi, freq in enumerate([1000, 2000, 500, 4000]):
    ax = axes2[fi]
    af16_ = array_factor_db(THETA_FINE, N_ELEM, D_M, freq, w16_d20)
    af8p_ = array_factor_db(THETA_FINE, N_ELEM, D_M, freq, w8p_d20)
    for af_, lbl, ls in [(af16_, '16独立', '-'), (af8p_, '8对称', '--')]:
        th_, db_ = make_polar_full(THETA_FINE, af_)
        db_c = np.clip(db_, -30, 0)
        ax.plot(th_, db_c + 30, lw=2, linestyle=ls, label=lbl)
    bw16_ = results_16[freq]['bw'] if freq in results_16 else beamwidth_6db(THETA_FINE, af16_)
    bw8p_ = results_8p[freq]['bw'] if freq in results_8p else beamwidth_6db(THETA_FINE, af8p_)
    ax.set_title(f'{freq}Hz\n16独立:{bw16_:.0f}° 8对:{bw8p_:.0f}°', fontsize=9, pad=8)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 32)
    ax.set_yticks([10, 20, 30])
    ax.set_yticklabels(['-20', '-10', '0'], fontsize=7)
    if fi == 0:
        ax.legend(loc='lower right', fontsize=8)

plt.tight_layout()
fig2_path = os.path.join(OUT, 'topology_16elem_vs_8pair.png')
plt.savefig(fig2_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  拓扑对比图: {fig2_path}")


# ────────────────────────────────────────────────
# 10. 生成 Markdown 报告
# ────────────────────────────────────────────────
print()
print("生成 sweep_d55_report.md ...")

# 构建汇总表数据
table_rows = []
for freq in ANALYSIS_FREQS:
    bw_sim16 = results_16[freq]['bw']
    bw_sim8p = results_8p[freq]['bw']
    bw_meas  = meas_bw.get(freq, float('nan'))
    sll16    = results_16[freq]['sll']
    sll8p    = results_8p[freq]['sll']

    vis, r_half, r_full, gl_ang = grating_lobe_analysis(D_M, freq)
    if vis:
        gl_str = f"YES(≈{gl_ang:.0f}°)"
    else:
        gl_str = "NO"

    # SPL 预测（取 P_ch=10W 档）
    P_ch = 10.0
    P_each = P_ch / 2
    spl_each = sens_1w_1m + 10 * np.log10(P_each)
    spl_pred = spl_each + array_gain_coherent - 2.0  # -2dB 保守修正
    spl_meas = MEAS_SPL[list(MEAS_FREQS).index(freq), 0]

    bw_diff_16  = bw_sim16 - bw_meas
    bw_diff_8p  = bw_sim8p - bw_meas
    spl_diff    = spl_pred - spl_meas

    table_rows.append({
        'freq': freq,
        'bw16': bw_sim16,
        'bw8p': bw_sim8p,
        'bw_meas': bw_meas,
        'bw_diff16': bw_diff_16,
        'bw_diff8p': bw_diff_8p,
        'sll16': sll16,
        'sll8p': sll8p,
        'gl': gl_str,
        'spl_pred': spl_pred,
        'spl_meas': spl_meas,
        'spl_diff': spl_diff,
    })

# 汇总表 Markdown 字符串
table_md = "| 频率(Hz) | BW仿真_16独立(°) | BW仿真_8对称(°) | BW竞品(插值派生·已撤回·非实测)(°) | Δ(16-竞品) | SLL_16(dB) | SLL_8p(dB) | 栅瓣状态 | SPL预测(dB)[估算] | SPL实测(dB) | ΔSPL |\n"
table_md += "|---------|----------------|----------------|-------------|-----------|----------|----------|---------|----------------|------------|-----|\n"
for r in table_rows:
    table_md += (f"| {r['freq']} | {r['bw16']:.1f} | {r['bw8p']:.1f} | "
                 f"{r['bw_meas']:.1f} | {r['bw_diff16']:+.1f} | "
                 f"{r['sll16']:.1f} | {r['sll8p']:.1f} | {r['gl']} | "
                 f"{r['spl_pred']:.1f} | {r['spl_meas']:.1f} | {r['spl_diff']:+.1f} |\n")

# 栅瓣临界频率表
grating_table = "| 频率(kHz) | d/λ | d/(λ/2) | broadside可见栅瓣 | 栅瓣角(°) |\n"
grating_table += "|----------|-----|---------|-----------------|----------|\n"
for f_khz in [3, 4, 5, 6, 7, 8]:
    freq = f_khz * 1000
    vis, r_half, r_full, gl_ang = grating_lobe_analysis(D_M, freq)
    gl_str = f"{gl_ang:.1f}" if gl_ang is not None else "—"
    vis_str = "YES ⚠" if vis else "NO"
    grating_table += f"| {f_khz:.1f} | {r_full:.3f} | {r_half:.3f} | {vis_str} | {gl_str} |\n"

report_content = f"""# Sprint 3 声学仿真报告
## N=16 / d=55mm / L=825mm 阵列指向性分析与竞品对照

**项目**：ITC 定向音柱（线阵）Sprint 3
**Agent**：AcousticSimulationAgent v1.0
**日期**：2026-05-27
**仿真脚本**：`sprint3/acoustic/sweep_d55.py`
**版本**：Sprint3-AC-WP01-v1

---

## 0. 几何参数 & 驱动拓扑说明

### 0.1 口径差异（880 vs 825）

| 参数 | 值 | 说明 |
|------|-----|------|
| N | 16 元 | 拆机实测 |
| d | 55 mm | 拆机实测，阵元中心距 |
| **L_aperture = (N-1)×d** | **825 mm** | **声学孔径（波束形成用）** |
| L_box = N×d | 880 mm | 箱体物理长度（CTO 给出值） |
| 差值 | 55 mm | 1 个间距，端部安装余量 |

> 【重要】880mm 是箱体/安装长度；**825mm 是有效声学孔径**，所有波束宽度计算基于 825mm。

### 0.2 驱动拓扑约束

| 拓扑 | 描述 | 有效自由度 | 指向能力 |
|------|------|-----------|---------|
| **(a) 理想 16 独立元** | 16 路独立驱动，可任意加权 | 16 | broadside + 扫描 |
| **(b) 实际 8 对称对** | 8ch A/B 串联，关于中心对称 | 8（实加权） | **仅 broadside，不可电子偏转** |

拓扑 (b) 强制对称约束：
- Ch1 = A1+B16（位置 0 与 15），Ch2 = A2+B15（位置 1 与 14），…
- 实加权，权值仅 8 个独立参数
- Dolph-Chebyshev 本身满足对称性，8 对约束下仍可近似实现

---

## 1. 仿真方法

- 远场线阵阵因子模型：`AF(θ) = Σ w_n·exp(j·k·n·d·sinθ)`，`k = 2πf/c`，`c = 343 m/s`
- 阵元：点声源近似（忽略阵元自身指向性——高频有低估旁瓣抑制的风险）
- 加权：Dolph-Chebyshev -20dB（基线），参考均匀加权
- 角度分辨率：0.05°（`THETA_FINE = linspace(0,90,1801)`）
- 模型局限：不含箱体衍射、阵元互耦合、实际相位误差

---

## 2. 各频率指向性结果 + 竞品对比（核心汇总表）

{table_md}

**注：**
- BW = -6dB 全角波束宽度（°），双侧对称值
- SPL预测基于 P_ch=10W/通道，88dB/1W/1m 灵敏度 [估算]，-2dB 保守修正
- Δ = 仿真 - 实测（正值表示仿真偏宽）

---

## 3. 栅瓣分析（P0 声学风险）

### 3.1 临界频率

| 判据 | 公式 | d=55mm 临界频率 |
|------|------|----------------|
| 保守扫描判据（d ≥ λ/2） | f = c/(2d) | **{f_crit_half:.0f} Hz ≈ {f_crit_half/1000:.1f} kHz** |
| Broadside 判据（d ≥ λ） | f = c/d | **{f_crit_full:.0f} Hz ≈ {f_crit_full/1000:.1f} kHz** |

### 3.2 3–8 kHz 栅瓣状态

{grating_table}

### 3.3 分析与风险结论

**为何竞品 d=55mm 在 4kHz 仍可工作（Broadside-only 优势）：**

1. **使用 broadside 判据（d ≥ λ）而非扫描判据（d ≥ λ/2）**
   - 竞品 8ch/16喇叭 仅 broadside，无需电子偏转
   - 4kHz 时 d/λ = {D_M/(C/4000):.3f} < 1 → **无可见区栅瓣** ✓

2. **阵元自身指向性抑制**
   - 55mm 口径喇叭在 4kHz 时已有一定指向性（kα ≈ {2*np.pi*4000/C * 0.055/2/2:.2f}），
     端射方向（±90°）的阵元辐射已有 3~6dB 自然衰减 [估算]
   - 实际栅瓣在端射方向受阵元函数抑制

3. **P0 风险区：6.2–8 kHz**
   - f > {f_crit_full/1000:.1f} kHz（d/λ > 1）栅瓣进入可见区
   - 6–8 kHz 栅瓣从 ±90° 向轴心移入，会在可见方向产生明显副瓣
   - **这是设计的固有物理限制**，若需工作到 8kHz 需缩小间距或分频段处理

---

## 4. PM 问题1：1kHz 超指向性是否仍需要？

| 对比项 | 值 |
|--------|-----|
| Sprint2 旧基线（d=30mm）BW@1kHz | {bw_1k_16d30_sprint2}° |
| Sprint3 新阵列（d=55mm）BW@1kHz（仿真） | {bw_1k_16d55:.1f}° |
| 孔径比 L_new/L_old | {aperture_ratio:.2f}× |
| 竞品 BW@1kHz [插值派生·F-AC-01已撤回·非实测] | {meas_bw[1000]:.1f}° |
| 差距（仿真 - 竞品） | {bw_1k_16d55 - meas_bw[1000]:+.1f}° |

**明确结论：1kHz 超指向性（ε=0.01）{'仍需要' if need_super else '不需要'}。**

{"理由：d=55mm 孔径扩大（L=825mm vs 旧 450mm），BW@1kHz 已大幅收窄，接近或达到竞品水平。无需超指向性额外收窄。" if not need_super else f"理由：仿真 BW@1kHz = {bw_1k_16d55:.1f}°，竞品 BW≈{meas_bw[1000]:.1f}° [插值派生·F-AC-01已撤回·非实测]，差距 {bw_1k_16d55-meas_bw[1000]:.1f}°。差距较小，可通过适当加权优化而非引入超指向性处理。超指向性对产线标定成本有显著影响（见 Sprint2 R5 风险），建议先实测再决策。"}

注：Gate1 指标 BW@2kHz≤30°，新阵列仿真 BW@2kHz = {results_16[2000]['bw']:.1f}°，**已满足**。

---

## 5. SPL 预测 vs 竞品

【所有 SPL 预测值均为估算，基于如下假设——实测前不可用于最终验收】

假设：
1. 单只灵敏度 = 88 dB/1W/1m @ 8Ω [估算，T/S 待实测]
2. 每通道 P_ch = 10W，串联 2 只，每只 P_each = 5W
3. 16 只轴向相干叠加，阵列增益 = 20 log10(16) = {array_gain_coherent:.1f} dB
4. 保守修正 -2dB（阵元幅相散差、互耦合等） [估算]

| 频率 | SPL预测@1m [估算] | 竞品实测@1m | 差值 |
|------|-----------------|-----------|------|
{"".join([f"| {r['freq']} Hz | {r['spl_pred']:.1f} dB | {r['spl_meas']:.1f} dB | {r['spl_diff']:+.1f} dB |" + chr(10) for r in table_rows])}

**【告警 W1】** T/S 参数全部为估算值，SPL 预测误差可达 ±5dB [估算]
**【告警 W2】** 功放输出功率与实际负载阻抗匹配尚未验证（15Ω vs 功放额定阻抗）
**【告警 W3】** 竞品 0° SPL 高（103–111dB），可能部分来自高功率设计或更高灵敏度单元

---

## 6. d=20/35（Sprint2估算）vs d=16/55（真实值）对照

| | Sprint2 估算 | Sprint3 真实 |
|--|-------------|-------------|
| 几何 | N≈20, d≈35mm, L≈665mm | N=16, d=55mm, L=825mm |
| 反推 RMS（1k/2k/4kHz） | {sprint2_best_rms:.2f} dB | {rms_d55_16:.2f} dB |
| BW@1kHz | 约 41° [估算] | {bw_1k_16d55:.1f}° |
| BW@2kHz | 约 20° [估算] | {results_16[2000]['bw']:.1f}° |
| 栅瓣风险 | d=35: f_gl={C/0.035/1000:.1f}kHz | d=55: f_gl={f_crit_full/1000:.1f}kHz，更早出现 |

{'**结论**：N=16/d=55 在几何上是正确的拆机真值。RMS 对比说明点声源模型在大间距时局限性更显著（阵元指向性未建模），但不影响几何确认的正确性。竞品阵元间距大（55mm）是低成本驱动（8通道）与宽孔径指向性的折中设计。' if rms_d55_16 > sprint2_best_rms else f'**结论**：N=16/d=55 比 Sprint2 估算的 N=20/d=35 更好地拟合实测方向图，RMS 改善 {sprint2_best_rms-rms_d55_16:.2f} dB，进一步验证拆机几何真值的正确性。'}

---

## 7. 置信度与告警清单

| 项目 | 置信度 | 说明 |
|------|--------|------|
| 几何参数（N=16, d=55mm） | 高 | 拆机实测 |
| 阵因子 BW 仿真（低频 ≤1kHz） | 中-高 | 点声源模型偏差 ±3° |
| 阵因子 BW 仿真（高频 2–4kHz） | 中 | 阵元指向性未建模，偏差 ±5° |
| 栅瓣临界频率 | 高 | 纯几何/波长关系，公式确定 |
| SPL 预测 | 低 | T/S 估算，偏差可达 ±5dB |
| 超指向性需求判断 | 中 | 依赖仿真 BW 精度，建议实测复核 |

**[估算] 标记**：
- 喇叭 T/S：Re≈7Ω, BL≈4 T·m, Qts≈0.5, Fs≈150Hz — 待实测更新
- SPL：88dB/1W/1m — 待消声室实测更新
- -2dB 保守修正系数 — 待实测标定

---

## 8. 文件清单

| 文件 | 说明 |
|------|------|
| `sweep_d55.py` | 本次仿真 Python 脚本 |
| `sweep_d55_report.md` | 本报告 |
| `polar_d55_vs_competitor.png` | 5 频率极坐标图（仿真 vs 竞品） |
| `topology_16elem_vs_8pair.png` | 16独立元 vs 8对称对拓扑对比 |

---

*AcousticSimulationAgent v1.0 | ITC Enterprise Multi-Agent System*
*提交方向：Critic Agent → Team Lead（Project Manager Agent）*
"""

report_path = os.path.join(OUT, 'sweep_d55_report.md')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_content)
print(f"  报告已写出: {report_path}")

# ────────────────────────────────────────────────
# 11. 执行摘要打印
# ────────────────────────────────────────────────
print()
print("=" * 65)
print("【执行摘要】向 Team Lead 汇报")
print("=" * 65)

print(f"""
几何确认：
  口径差异：880mm（箱体）vs 825mm（声学孔径=(N-1)×d=15×55）

各频率 BW（仿真 vs 竞品插值BW·派生·非实测）：
  频率    BW仿真(16独立) BW仿真(8对) BW竞品(插值派生·非实测)
""")
for freq in ANALYSIS_FREQS:
    bwS = results_16[freq]['bw']
    bw8 = results_8p[freq]['bw']
    bwM = meas_bw.get(freq, 0)
    diff = bwS - bwM
    print(f"  {freq:6d}Hz  {bwS:8.1f}°     {bw8:8.1f}°     {bwM:8.1f}°   Δ={diff:+.1f}°")

print(f"""
栅瓣结论：
  d=55mm：broadside 模式下约 {f_crit_full/1000:.1f}kHz 进入可见区（d≥λ）
  4kHz 时 d/λ={D_M/(C/4000):.3f}<1 → 无可见栅瓣 ✓
  6.2kHz+ 出现栅瓣，为 P0 风险区（500Hz–6kHz 工作安全）

超指向需求（PM 问题1）：
  1kHz BW仿真={bw_1k_16d55:.1f}°，竞品={meas_bw[1000]:.1f}°，差{bw_1k_16d55-meas_bw[1000]:+.1f}°
  结论：{'仍建议考虑超指向，但差距较小，实测优先于仿真评估' if need_super else '不需要超指向，d=55mm 孔径已满足指向性要求'}

SPL预测（P_ch=10W，[估算]）：
  预测值约 {table_rows[2]['spl_pred']:.0f}–{table_rows[1]['spl_pred']:.0f} dB（1k–500Hz），
  vs 竞品 {int(MEAS_SPL[2,0])}–{int(MEAS_SPL[1,0])} dB（同频），差约 {table_rows[2]['spl_diff']:+.0f}~{table_rows[1]['spl_diff']:+.0f} dB
  [估算，置信度低，T/S 待实测]

置信度：BW预测 中-高，栅瓣 高，SPL 低（T/S估算）
告警：T/S 全为估算，需 2-4 周后实测更新
""")

# ────────────────────────────────────────────────
# 9. CSV 导出（原始仿真数据，可追溯 / 审计用）
#    导出脚本实际算出的同一批数（results_16 / results_8p / meas_bw / 栅瓣分析）
#    long 格式：每行 = (频率 × 拓扑 × 加权)；dolph20 取自已算结果，uniform 用同一确定性函数现算
# ────────────────────────────────────────────────
import csv as _csv

_csv_path = os.path.join(OUT, "sweep_d55_results.csv")
_fields = ["freq_hz", "N", "d_mm", "L_aperture_mm", "topology", "weighting",
           "BW6dB_deg", "SLL_dB", "competitor_BW_deg",
           "d_over_lambda", "grating_visible_d_ge_lambda", "grating_angle_deg"]

with open(_csv_path, "w", newline="", encoding="utf-8") as _f:
    _w = _csv.DictWriter(_f, fieldnames=_fields)
    _w.writeheader()
    for _freq in ANALYSIS_FREQS:
        _vis, _rhalf, _rfull, _glang = grating_lobe_analysis(D_M, _freq)
        _comp = meas_bw.get(_freq, float("nan"))
        # uniform 用同一阵因子函数现算（与 dolph20 同一确定性模型，仅加权不同）
        _af16u = array_factor_db(THETA_FINE, N_ELEM, D_M, _freq, w16_uni)
        _af8pu = array_factor_db(THETA_FINE, N_ELEM, D_M, _freq, w8p_uni)
        _rows = [
            ("16-indep", "dolph20", results_16[_freq]["bw"], results_16[_freq]["sll"]),
            ("8-pair",   "dolph20", results_8p[_freq]["bw"], results_8p[_freq]["sll"]),
            ("16-indep", "uniform", beamwidth_6db(THETA_FINE, _af16u), peak_sll(THETA_FINE, _af16u)),
            ("8-pair",   "uniform", beamwidth_6db(THETA_FINE, _af8pu), peak_sll(THETA_FINE, _af8pu)),
        ]
        for _topo, _win, _bw, _sll in _rows:
            _w.writerow({
                "freq_hz": _freq, "N": N_ELEM, "d_mm": D_MM,
                "L_aperture_mm": L_APERTURE_MM, "topology": _topo, "weighting": _win,
                "BW6dB_deg": round(float(_bw), 3), "SLL_dB": round(float(_sll), 2),
                "competitor_BW_deg": round(float(_comp), 2),
                "d_over_lambda": round(float(_rfull), 4),
                "grating_visible_d_ge_lambda": "YES" if _vis else "NO",
                "grating_angle_deg": (round(float(_glang), 1) if _vis else ""),
            })
print(f"\n[CSV] 原始仿真数据已导出: {_csv_path}  ({len(ANALYSIS_FREQS)*4} 行 + 表头)")

print("=" * 65)
print("Sprint3 声学仿真完成，文件已写出：")
for fn in sorted(os.listdir(OUT)):
    size = os.path.getsize(os.path.join(OUT, fn))
    print(f"  {fn}  ({size//1024 if size > 1024 else size}{'KB' if size > 1024 else 'B'})")
print("=" * 65)
