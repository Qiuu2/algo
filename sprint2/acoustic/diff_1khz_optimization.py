"""
⚠️ 历史归档/作废（PF-8，2026-05-29）：本文件含基于 d=30 错误几何（Sprint2 视觉估测值，已被拆机实测真值 d=55 取代，DEC-S3-GEOM-01）的结论/数据，仅作历史留痕，不可作任何决策依据。现行 d=55 基线见 decisions_log DEC-S3-GEOM-01 / PROJECT_HANDOVER.md。

ITC 定向音柱 — 声学仿真专家 Agent
Sprint 2 补做 #3：1kHz 指向性优化方案 D-2「子带差分 + 相控混合」
CTO 要求：≥1kHz 强指向；现状 N=16/d=30/Dolph-20dB 在 1kHz 的 -6dB BW=55.2° 偏宽（竞品反推 36.6°）

本脚本用 numpy 真实仿真：
  1. N=16/d=30 阵的 1/2/3 阶差分波束形成方向图（500Hz/1kHz/1.5kHz）
  2. 各阶 -6dB BW、旁瓣、前后比
  3. 白噪声增益 WNG（核心成本）+ 阵元幅相一致性容差
  4. 差分+相控混合方案的优化后 BW@1k
  5. 算力/延迟/复杂度增量估算
作者：AcousticSimulationAgent v1.0  日期：2026-05-26
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal.windows import chebwin
import os

OUT = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint2/acoustic"
C = 343.0
D_M = 0.030      # 阵元间距 30mm
N_ELEM = 16      # 阵元数

# ════════════════════════════════════════════════
# 1. 差分波束形成核心模型
# ════════════════════════════════════════════════
# 说明：差分波束形成（Differential Beamforming, 对偶于差分传声器阵 DMA）
#   - N 阶差分使用 (N+1) 个相邻阵元，通过差分组合产生 cos^N 型方向图。
#   - 方向角 θ 定义：θ=0 指向阵轴方向（端射 endfire）。
#   - 1阶 cardioid:  D(θ)=(1+cosθ)/2 ；hypercardioid:(1+3cosθ)/4 ；supercardioid
#   - 2阶: D(θ)=[(1+cosθ)/2]^2 类（cos^2）；3阶 cos^3
#   - 这是端射差分阵的理想（频率无关）方向图，主瓣指向阵轴。
#
# 关键物理：差分阵实现"频率无关方向图"的代价是 WNG 随频率下降而急剧恶化：
#   WNG(f) ∝ (kd)^(2N)  （小孔径近似），N=阶数。
#   小 kd（低频/小间距）→ WNG 极低 → 对阵元幅相误差/自噪声极度敏感。

def diff_pattern_ideal(theta_rad, order, beta=None):
    """
    理想 N 阶差分方向图（端射，主瓣 θ=0）。
    采用 (a0 + a1 cosθ)^... 形式的标准差分波束。
    order=1: cardioid (a0=a1=0.5)
    order=2: cos^2 型
    order=3: cos^3 型
    返回归一化幅度（线性，0~1）。
    """
    base = (1 + np.cos(theta_rad)) / 2.0  # cardioid 基元 (1+cosθ)/2
    patt = base ** order
    return patt  # 已归一化到 θ=0 时=1

def diff_wng_db(order, freq_hz, d_m):
    """
    N 阶差分波束形成的白噪声增益 WNG (dB)。
    标准 DMA 理论：对 (N+1) 元均匀线阵端射 N 阶差分，
    WNG ≈ [Π_{n=1}^{N} (k d)^2 / (相关系数)]，小孔径近似下
    WNG_dB ≈ 10*log10( (1/(N+1)) ) - 20*N*log10( 1/(2 sin(kd/2)) )  的量级。

    采用闭式（Elko 经典结果，端射 N 阶差分小孔径）：
       WNG ≈ ( (kd)^(2N) ) / ( c_N )   （线性，<1 表示恶化）
    其中 c_N 为阶数相关常数。这里用更标准的形式：
       WNG = |h^H d|^2 / (h^H h)，h 为差分权向量，d 为期望响应导向矢量。
    我们直接数值计算（最稳妥）。
    """
    M = order + 1  # 使用 M 个相邻阵元
    k = 2 * np.pi * freq_hz / C
    # 端射导向矢量（θ=0，主瓣方向）：相位 = k*m*d*cos(0)=k*m*d
    n = np.arange(M)
    # 差分波束的权向量 h：求解使 (N+1) 元阵在 θ=0 产生 N 阶差分响应。
    # 用约束最小范数：在 0/null 角度满足方向图约束。
    # 标准做法：h 满足 V^H h = c，V 为多个角度的导向矢量，c 为期望响应。
    # cos^N 型 cardioid 的零点在 θ=π。
    # 简化稳健实现：用二项式差分系数（典型差分阵权）
    # 1阶: [1,-1] 经 cardioid 延迟；高阶为其卷积。
    # 这里用频域差分阵权：h_m = binom(N,m)*(-1)^m 的延迟差分（端射 cardioid）
    from math import comb
    # cardioid N 阶 = (前向延迟差分)^N，端射设计延迟 τ = d/c（指向 θ=0）
    # 频域权：h(f) 使阵列在 θ=0 主瓣、θ=π 零点
    # 导向矢量 a(θ) = exp(-j k m d cosθ)
    def steer(theta):
        return np.exp(-1j * k * n * d_m * np.cos(theta))
    a0 = steer(0.0)        # 主瓣
    api = steer(np.pi)     # 后向零点
    # 期望：h^H a0 = 1（主瓣），h^H api = 0（cardioid 后向零点）
    # 对高阶，在 θ=π 处要求 N 重零点（导数也为0）——用多约束
    # 构造约束矩阵：在 θ=π 的 0~(N-1) 阶导数为0，θ=0 响应=1
    # 简化：用 (M) 个约束点的最小范数解
    angles_constr = [0.0]  # 主瓣=1
    resp = [1.0]
    # 在 π 附近放 N 个零点约束（cos^N 后向多重零）
    for j in range(order):
        ang = np.pi - 0.0 if order == 1 else np.pi * (1 - 0.0)
        angles_constr.append(np.pi)
        resp.append(0.0)
    # 为避免奇异，把后向零点稍微散开
    if order >= 2:
        angles_constr = [0.0] + list(np.linspace(np.pi*0.75, np.pi, order))
        resp = [1.0] + [0.0]*order
    V = np.array([steer(t) for t in angles_constr]).T  # (M, n_constr)
    c = np.array(resp, dtype=complex)
    # 最小范数解 h = V (V^H V)^-1 c
    VhV = V.conj().T @ V
    try:
        h = V @ np.linalg.solve(VhV, c)
    except np.linalg.LinAlgError:
        h = V @ np.linalg.pinv(VhV) @ c
    # WNG = |h^H a0|^2 / (h^H h)
    num = np.abs(h.conj() @ a0) ** 2
    den = np.real(h.conj() @ h)
    wng = num / (den + 1e-30)
    return 10 * np.log10(wng + 1e-30), h

# ════════════════════════════════════════════════
# 2. 现状 Dolph 相控方向图（broadside, 对照基线）
# ════════════════════════════════════════════════
def dolph_phased_db(theta_deg_arr, N, d_m, freq_hz, sll_db=20):
    """现状方案：N 元 Dolph-Cheby 相控阵 broadside 方向图（θ=0 为 broadside）。"""
    theta_rad = np.radians(theta_deg_arr)
    w = chebwin(N, sll_db); w /= w.max()
    k = 2 * np.pi * freq_hz / C
    n = np.arange(N)
    phase = k * np.outer(np.sin(theta_rad), n * d_m)
    af = (w * np.exp(1j * phase)).sum(axis=1)
    mag = np.abs(af); mag /= mag[0] if mag[0] > 1e-10 else mag.max()
    return 20 * np.log10(mag + 1e-10)

def bw6_endfire(theta_deg, patt_db):
    """端射差分主瓣 -6dB 全宽（主瓣在 θ=0，对称）。"""
    peak = patt_db[0]
    below = np.where(patt_db < peak - 6)[0]
    if len(below) == 0:
        return 360.0
    i = below[0]
    if i > 0:
        t0, t1 = theta_deg[i-1], theta_deg[i]
        d0, d1 = patt_db[i-1], patt_db[i]
        t6 = t0 + (peak-6-d0)/(d1-d0)*(t1-t0) if d1 != d0 else t0
    else:
        t6 = theta_deg[i]
    return float(2 * t6)

def bw6_broadside(theta_deg, patt_db):
    """broadside 主瓣 -6dB 全宽（主瓣在 θ=0）。"""
    return bw6_endfire(theta_deg, patt_db)

def front_back(theta_deg, patt_db):
    """前后比：0° vs 180°。理想 cardioid 后向为零(数学上 -inf)，实际受 WNG/误差限制，封顶到 30dB。"""
    i180 = np.argmin(np.abs(theta_deg - 180))
    fb = patt_db[0] - patt_db[i180]
    return float(min(fb, 30.0))  # 理想后向零点不可实现，实际受阵元误差限到~25-30dB

def peak_sidelobe(theta_deg, patt_db):
    """主瓣外峰值旁瓣（dB，相对主瓣）。"""
    from scipy.signal import argrelmax
    peak = patt_db[0]
    # 找第一零点
    null_i = None
    for i in range(1, len(patt_db)):
        if patt_db[i] < peak - 25:
            null_i = i; break
    if null_i is None:
        # cos^N 型无明显旁瓣
        return -60.0
    sl = patt_db[null_i:]
    pk = argrelmax(sl, order=3)[0]
    if len(pk) == 0:
        return float(sl.max() - peak)
    return float(sl[pk].max() - peak)

# ════════════════════════════════════════════════
# 3. 仿真：各阶差分 @500/1000/1500 Hz
# ════════════════════════════════════════════════
print("=" * 60)
print("D-2 差分波束形成仿真（N=16/d=30mm 阵的相邻子阵差分）")
print("=" * 60)

theta_deg = np.linspace(0, 180, 1801)
theta_rad = np.radians(theta_deg)
FREQS = [500, 1000, 1500]

results = {}  # results[(order,freq)] = dict
for order in [1, 2, 3]:
    for freq in FREQS:
        patt_lin = diff_pattern_ideal(theta_rad, order)
        patt_db = 20 * np.log10(patt_lin + 1e-10)
        bw = bw6_endfire(theta_deg, patt_db)
        fb = front_back(theta_deg, patt_db)
        sll = peak_sidelobe(theta_deg, patt_db)
        wng_db, h = diff_wng_db(order, freq, D_M)
        results[(order, freq)] = dict(bw=bw, fb=fb, sll=sll, wng=wng_db)

print("\n各阶差分方向图指标（理想 cos^N 端射型，方向图本身频率无关）:")
print(f"{'阶数':<6}{'BW@-6dB':<12}{'前后比':<10}{'旁瓣':<10}")
for order in [1, 2, 3]:
    r = results[(order, 1000)]
    print(f"{order}阶    {r['bw']:.1f}°       {r['fb']:.1f}dB    {r['sll']:.1f}dB")

print("\n★ 核心成本：白噪声增益 WNG (dB)（越负越差，对阵元误差越敏感）:")
print(f"{'阶数':<6}{'WNG@500Hz':<14}{'WNG@1kHz':<14}{'WNG@1.5kHz':<14}")
for order in [1, 2, 3]:
    w5 = results[(order, 500)]['wng']
    w1 = results[(order, 1000)]['wng']
    w15 = results[(order, 1500)]['wng']
    print(f"{order}阶    {w5:.1f}          {w1:.1f}          {w15:.1f}")

# ════════════════════════════════════════════════
# 4. WNG → 阵元幅相一致性容差
# ════════════════════════════════════════════════
# WNG 决定对阵元增益/相位误差的放大。容差准则（工程经验）：
#   若希望误差导致的方向图劣化 < 3dB，需要阵元误差功率 σ² 满足
#   σ²_总 < WNG_linear（即 误差不能淹没有用信号）。
#   增益误差 σ_g (dB) 与相位误差 σ_φ (deg) 的等效：
#   σ²_err ≈ (σ_g·ln10/20)² + (σ_φ·π/180)²
#   要求 10*log10(σ²_err) < WNG_db - 3
print("\n阵元幅相一致性容差需求（保证差分波束有效，误差劣化<3dB）:")
print(f"{'阶数':<6}{'WNG@1kHz':<12}{'允许误差功率':<16}{'对应增益/相位容差(@1kHz)'}")
tol_table = {}
for order in [1, 2, 3]:
    wng1k = results[(order, 1000)]['wng']
    # 允许总误差功率 (dB) = WNG - 3 (留 3dB 余量)，再转线性
    allow_err_db = wng1k - 3
    allow_err_lin = 10 ** (allow_err_db / 10)
    # 假设增益相位误差各占一半功率
    sigma_each = np.sqrt(allow_err_lin / 2)
    sigma_g_db = sigma_each * 20 / np.log(10)   # 增益误差 (dB)
    sigma_phi_deg = sigma_each * 180 / np.pi    # 相位误差 (deg)
    tol_table[order] = (sigma_g_db, sigma_phi_deg, allow_err_db)
    print(f"{order}阶    {wng1k:.1f}dB     {allow_err_db:.1f}dB         ±{sigma_g_db:.3f}dB / ±{sigma_phi_deg:.2f}°")

# ════════════════════════════════════════════════
# 5. 现状基线 + 混合方案 BW@1k
# ════════════════════════════════════════════════
print("\n" + "=" * 60)
print("现状基线 vs 混合方案 @1kHz")
print("=" * 60)
base_db = dolph_phased_db(theta_deg, N_ELEM, D_M, 1000, 20)
base_bw1k = bw6_broadside(theta_deg, base_db)
print(f"\n现状 N=16/d=30/Dolph-20dB @1kHz BW = {base_bw1k:.1f}° (CSV 标称 55.2°)")
print(f"竞品反推模型隐含 BW @1kHz = 36.6°")

# 物理说明：N=16/d=30 阵在 1kHz 孔径 L=450mm，L/λ=1.31。
#   常规相控（含 Dolph）-6dB BW 下限受瑞利衍射极限约束（≈0.886λ/L≈38.7°单侧→全宽更大），
#   Dolph-20dB 加权进一步展宽主瓣，故得 55.2°。
#   要在 broadside 突破孔径限制收窄主瓣，必须使用【超指向(superdirectivity)】——
#   这正是"差分波束形成"在 broadside 阵的本质：用相邻阵元的幅度反相组合，
#   等效于各向同性噪声场下的 MVDR(最小方差无失真响应)加权。
#   超指向程度由正则化 ε 控制：ε↓ → BW↓但 WNG↓(鲁棒性崩)；ε↑ → 退回常规相控。
#
# 超指向 MVDR 加权：w = (Γ+εI)^-1 a / [a^H (Γ+εI)^-1 a]
#   Γ_ij = sinc(k d |i-j|) 为各向同性噪声相干矩阵；a 为 broadside 导向矢量(=1)。
def superdirective_weights(N, d_m, freq_hz, eps):
    k = 2 * np.pi * freq_hz / C
    n = np.arange(N)
    idx = np.abs(np.subtract.outer(n, n))
    Gamma = np.sinc(k * d_m * idx / np.pi)   # np.sinc(x)=sin(πx)/(πx)
    a = np.ones(N, dtype=complex)            # broadside steering, sin(0)=0
    Gr = Gamma + eps * np.eye(N)
    w = np.linalg.solve(Gr, a)
    w = w / (a.conj() @ w)
    return w

def superdir_pattern_db(N, d_m, freq_hz, eps):
    w = superdirective_weights(N, d_m, freq_hz, eps)
    k = 2 * np.pi * freq_hz / C
    n = np.arange(N)
    phase = k * np.outer(np.sin(theta_rad), n * d_m)
    af = (w.conj() * np.exp(1j * phase)).sum(axis=1)
    mag = np.abs(af); mag /= mag.max()
    return 20 * np.log10(mag + 1e-12)

def superdir_wng_db(N, d_m, freq_hz, eps):
    w = superdirective_weights(N, d_m, freq_hz, eps)
    a = np.ones(N, dtype=complex)
    return 10 * np.log10(np.abs(w.conj() @ a) ** 2 / np.real(w.conj() @ w) + 1e-30)

# 混合方案：在 1kHz 用超指向加权（等效低阶差分），扫不同 ε 给出 BW-WNG 权衡
print("\n混合方案(Dolph 相控 → 1kHz 超指向/差分)：ε 控制 BW vs WNG 权衡")
print(f"{'正则ε':<10}{'BW@1k':<12}{'WNG@1k':<12}{'增益容差':<14}{'相位容差'}")
hybrid_sweep = []
for eps in [0.3, 0.1, 0.03, 0.01, 0.003]:
    hdb = superdir_pattern_db(N_ELEM, D_M, 1000, eps)
    hbw = bw6_broadside(theta_deg, hdb)
    hwng = superdir_wng_db(N_ELEM, D_M, 1000, eps)
    allow_err_db = hwng - 3
    allow_lin = 10 ** (allow_err_db / 10)
    sg = np.sqrt(max(allow_lin,1e-9)/2) * 20/np.log(10)
    sp = np.sqrt(max(allow_lin,1e-9)/2) * 180/np.pi
    hybrid_sweep.append((eps, hbw, hwng, sg, sp))
    print(f"{eps:<10}{hbw:.1f}°       {hwng:.1f}dB      ±{sg:.3f}dB     ±{sp:.2f}°")

# 选两个代表点：保守(WNG≥0) 与 激进(BW≈竞品36.6°)
# 保守：ε使 WNG≈+2dB；激进：BW≈36°
hyb_conservative = min(hybrid_sweep, key=lambda r: abs(r[2]-2.0))   # WNG≈2dB
hyb_aggressive = min(hybrid_sweep, key=lambda r: abs(r[1]-36.6))    # BW≈竞品
hyb1_bw = hyb_conservative[1]   # 保守混合 BW
hyb2_bw = hyb_aggressive[1]     # 激进混合 BW
hyb1_db = superdir_pattern_db(N_ELEM, D_M, 1000, hyb_conservative[0])
hyb2_db = superdir_pattern_db(N_ELEM, D_M, 1000, hyb_aggressive[0])
print(f"\n保守混合(ε={hyb_conservative[0]}): BW@1k={hyb1_bw:.1f}°, WNG={hyb_conservative[2]:.1f}dB (鲁棒)")
print(f"激进混合(ε={hyb_aggressive[0]}): BW@1k={hyb2_bw:.1f}°, WNG={hyb_aggressive[2]:.1f}dB (接近竞品但脆弱)")

# ════════════════════════════════════════════════
# 6. 增量估算（算力/延迟/复杂度）
# ════════════════════════════════════════════════
print("\n" + "=" * 60)
print("增量估算")
print("=" * 60)
# 子带速率：SB0(500-1k) 抽取后 ~3kHz, SB1低端 ~6kHz
# 差分 FIR：每阶约需 1 个延迟差分；标定补偿 FIR 取 T_fir 抽头
# 16 通道
T_fir = 32  # 每通道补偿/差分 FIR 抽头（标定+差分）
ch = 16
for sb, rate in [('SB0(500-1k)', 3000), ('SB1低端', 6000)]:
    # MMAC/s = ch * T_fir * rate
    mmac = ch * T_fir * rate / 1e6
    print(f"  {sb} @ {rate}Hz: {ch}ch × {T_fir}tap × {rate}Hz = {mmac:.2f} MMAC/s")
total_mmac = ch * T_fir * (3000 + 6000) / 1e6
print(f"  差分补偿算力增量合计 ≈ {total_mmac:.2f} MMAC/s（需 DSP agent 复核）")

# 延迟：差分 FIR 群延迟 ~ T_fir/2 / rate
for sb, rate in [('SB0', 3000), ('SB1低端', 6000)]:
    grp_delay_ms = (T_fir/2) / rate * 1000
    print(f"  {sb} 差分FIR群延迟 ≈ {grp_delay_ms:.2f} ms (需 DSP agent 复核子带重建总延迟)")

# ════════════════════════════════════════════════
# 7. 出图
# ════════════════════════════════════════════════
fig = plt.figure(figsize=(18, 10))

# (a) 极坐标：各阶差分方向图 @1kHz vs 现状 vs 混合
ax1 = fig.add_subplot(2, 3, 1, projection='polar')
def to_full_polar(theta_deg_180, patt_db):
    th = np.radians(theta_deg_180)
    th_full = np.concatenate([th, 2*np.pi - th[::-1]])
    db_full = np.concatenate([patt_db, patt_db[::-1]])
    return th_full, db_full
for order, col in zip([1,2,3], ['tab:blue','tab:orange','tab:green']):
    patt_db = 20*np.log10(diff_pattern_ideal(theta_rad, order)+1e-10)
    th_f, db_f = to_full_polar(theta_deg, patt_db)
    ax1.plot(th_f, np.clip(db_f,-30,0)+30, color=col, lw=1.8, label=f'{order}阶差分(端射)')
ax1.set_title('Differential beams (endfire, cos^N)', fontsize=9, pad=10)
ax1.set_theta_zero_location('N'); ax1.set_theta_direction(-1)
ax1.set_ylim(0,32); ax1.set_yticks([0,10,20,30]); ax1.set_yticklabels(['-30','-20','-10','0dB'],fontsize=6)
ax1.legend(fontsize=6, loc='lower right')

# (b) 极坐标：现状 vs 混合 @1kHz (broadside)
ax2 = fig.add_subplot(2, 3, 2, projection='polar')
for db_arr, lab, col in [(base_db,f'现状Dolph ({base_bw1k:.0f}°)','tab:red'),
                          (hyb1_db,f'混合-保守 ({hyb1_bw:.0f}°)','tab:blue'),
                          (hyb2_db,f'混合-激进 ({hyb2_bw:.0f}°)','tab:green')]:
    th_f, db_f = to_full_polar(theta_deg, db_arr)
    ax2.plot(th_f, np.clip(db_f,-30,0)+30, color=col, lw=1.8, label=lab)
ax2.set_title('@1kHz: Baseline vs Hybrid (broadside)', fontsize=9, pad=10)
ax2.set_theta_zero_location('N'); ax2.set_theta_direction(-1)
ax2.set_ylim(0,32); ax2.set_yticks([0,10,20,30]); ax2.set_yticklabels(['-30','-20','-10','0dB'],fontsize=6)
ax2.legend(fontsize=6, loc='lower right')

# (c) WNG vs 频率
ax3 = fig.add_subplot(2, 3, 3)
ff = np.linspace(300, 2500, 60)
for order, col in zip([1,2,3], ['tab:blue','tab:orange','tab:green']):
    wngs = [diff_wng_db(order, f, D_M)[0] for f in ff]
    ax3.plot(ff, wngs, color=col, lw=2, label=f'{order}阶差分')
ax3.axhline(0, color='k', ls=':', lw=1, label='全和阵基准(0dB)')
ax3.axvline(1000, color='gray', ls='--', alpha=0.6)
ax3.set_xlabel('Frequency (Hz)'); ax3.set_ylabel('WNG (dB)')
ax3.set_title('White Noise Gain vs Freq (核心成本)', fontsize=9)
ax3.legend(fontsize=7); ax3.grid(alpha=0.3)

# (d) BW 对比柱状
ax4 = fig.add_subplot(2, 3, 4)
names = ['现状\nDolph', '竞品\n反推', '混合\n保守', '混合\n激进']
vals = [base_bw1k, 36.6, hyb1_bw, hyb2_bw]
cols = ['tab:red','gray','tab:blue','tab:green']
ax4.bar(names, vals, color=cols)
for i,v in enumerate(vals):
    ax4.text(i, v+1, f'{v:.0f}°', ha='center', fontsize=9)
ax4.axhline(36.6, color='gray', ls='--', alpha=0.6)
ax4.set_ylabel('-6dB BW @1kHz (°)')
ax4.set_title('BW@1kHz Comparison', fontsize=9)

# (e) 容差需求柱状
ax5 = fig.add_subplot(2, 3, 5)
orders = [1,2,3]
gtol = [tol_table[o][0] for o in orders]
ptol = [tol_table[o][1] for o in orders]
x = np.arange(3)
ax5.bar(x-0.2, gtol, 0.4, label='增益容差(dB)', color='tab:purple')
ax5b = ax5.twinx()
ax5b.bar(x+0.2, ptol, 0.4, label='相位容差(°)', color='tab:cyan')
ax5.set_xticks(x); ax5.set_xticklabels([f'{o}阶' for o in orders])
ax5.set_ylabel('增益容差 ±dB'); ax5b.set_ylabel('相位容差 ±°')
ax5.set_title('Element matching tolerance @1kHz', fontsize=9)
ax5.legend(fontsize=7, loc='upper right'); ax5b.legend(fontsize=7, loc='upper center')

# (f) WNG@1k 柱
ax6 = fig.add_subplot(2, 3, 6)
wng1k = [results[(o,1000)]['wng'] for o in orders]
ax6.bar([f'{o}阶' for o in orders], wng1k, color='tab:brown')
for i,v in enumerate(wng1k):
    ax6.text(i, v-1, f'{v:.1f}dB', ha='center', fontsize=9, color='white')
ax6.axhline(0, color='k', ls=':', lw=1)
ax6.set_ylabel('WNG @1kHz (dB)')
ax6.set_title('WNG penalty @1kHz (越负越差)', fontsize=9)

plt.tight_layout()
png = os.path.join(OUT, 'diff_1khz_comparison.png')
plt.savefig(png, dpi=140)
plt.close()
print(f"\n对比图已保存: {png}")

# 导出关键数字供报告
print("\n" + "=" * 60)
print("关键数字汇总（供报告）")
print("=" * 60)
print(f"现状BW@1k={base_bw1k:.1f}°, 竞品36.6°, 混合保守={hyb1_bw:.1f}°(WNG={hyb_conservative[2]:.1f}dB), 混合激进={hyb2_bw:.1f}°(WNG={hyb_aggressive[2]:.1f}dB)")
for o in [1,2,3]:
    r=results[(o,1000)]
    print(f"{o}阶: BW={r['bw']:.1f}° FB={r['fb']:.1f}dB SLL={r['sll']:.1f}dB WNG@1k={r['wng']:.1f}dB "
          f"容差±{tol_table[o][0]:.3f}dB/±{tol_table[o][1]:.2f}°")
print(f"算力增量≈{total_mmac:.2f}MMAC/s")

# 存盘供 md 使用
np.savez(os.path.join(OUT,'_diff_cache.npz'),
         base_bw1k=base_bw1k, hyb1_bw=hyb1_bw, hyb2_bw=hyb2_bw,
         hyb1_wng=hyb_conservative[2], hyb2_wng=hyb_aggressive[2],
         hyb1_eps=hyb_conservative[0], hyb2_eps=hyb_aggressive[0],
         total_mmac=total_mmac)
print("\n完成。")
