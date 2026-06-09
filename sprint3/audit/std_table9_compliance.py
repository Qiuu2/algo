"""
ITC 定向音柱 — 声学仿真专家 Agent  (TASK-STD-A)
任务：按国产标准 JY/T 表9 的 12 点口径，补算 d=55/N=16 阵列在
      500/1k/2k/4k × {30°,90°,180°} 的 SPL 差值（衰减量），并对照一/二/三级分级。

【SPL 差值定义（标准口径）】
  SPL差值(θ) = −20·log10|AF(θ)/AF(0)|  = θ 处相对主瓣(0°)的衰减量（dB，正值）
  与"BW(波束宽度)"是不同口径：BW 是 −6dB 全角宽度；
  本任务直接给固定角度的衰减 dB。两者均来自同一已三轨验证的 d=55 阵因子。

【前置陷阱（必须先解，已在报告中裁定）】
  陷阱1（平面口径）：线阵只在阵列轴平面有指向性 → 本脚本算的是"阵列波束平面"的衰减，
                    默认对应表9"水平测量平面"（前提：音柱水平安装，阵列轴=水平）。
  陷阱2（180°对称）：isotropic 线阵阵因子前后对称 → AF(180°)=AF(0°) → 180°衰减≈0dB(artifact)。
                    本脚本会数值验证该 artifact，但 180° 标"现模型不可评"，禁报误导性达标数字。

【几何】N=16 / d=55mm / L=825mm / Dolph-Cheby-20dB / broadside / isotropic
        (SC-S3-GEOM-01；与已三轨验证的 sweep_d55.py 同一阵因子)
作者：AcousticSimulationAgent v1.0 | 日期：2026-05-29 | 三轨：numpy 主算
"""

import numpy as np
from scipy.signal.windows import chebwin

# ─── 物理常数 & 几何（与 sweep_d55.py 严格一致）───
C = 343.0                      # m/s 声速 (20°C)  —— N.2.1
N_ELEM = 16
D_M = 55.0e-3                  # 55mm  —— [L1拆机实测]
L_APERTURE_MM = (N_ELEM - 1) * 55.0   # 825mm 声学孔径

# Dolph-Cheby -20dB，归一化（与 sweep_d55.get_weights_16('dolph20') 完全相同）
W = chebwin(N_ELEM, 20)
W = W / W.max()

def af_linear(theta_deg, N, d_m, freq_hz, weights):
    """线阵远场阵因子复幅值（未归一化）。theta=0 为 broadside。"""
    th = np.radians(np.atleast_1d(theta_deg).astype(float))
    k = 2 * np.pi * freq_hz / C
    n = np.arange(N)
    phase = k * np.outer(np.sin(th), n * d_m)         # (len, N)
    af = (weights * np.exp(1j * phase)).sum(axis=1)
    return af

def spl_diff_db(theta_deg, freq_hz):
    """SPL 差值(衰减量) = -20log10|AF(theta)/AF(0)|，正值=衰减。"""
    af = af_linear(theta_deg, N_ELEM, D_M, freq_hz, W)
    af0 = af_linear(0.0, N_ELEM, D_M, freq_hz, W)[0]
    ratio = np.abs(af) / np.abs(af0)
    return -20.0 * np.log10(ratio + 1e-30)

# ─── 标准表9（水平面 SPL 差值要求，dB）───
# 行=频率，列=角度，值=(一级,二级,三级) 门限
STD = {
    (500, 30):  (5, 3, 1),   (500, 90):  (10, 8, 6),   (500, 180): (12, 10, 8),
    (1000, 30): (18, 15, 12),(1000, 90): (20, 17, 14), (1000, 180):(20, 17, 14),
    (2000, 30): (20, 17, 14),(2000, 90): (25, 22, 19), (2000, 180):(20, 17, 14),
    (4000, 30): (22, 19, 16),(4000, 90): (10, 8, 6),   (4000, 180):(20, 17, 14),
}

FREQS = [500, 1000, 2000, 4000]
ANGLES = [30, 90, 180]

def grade_of(value, thresholds):
    """thresholds=(L1,L2,L3 门限)。返回 (达到的级别字符串, 到下一更高级的裕量dB)。"""
    l1, l2, l3 = thresholds
    if value >= l1:
        return "一级", value - l1            # 已最高级，裕量=超一级量
    elif value >= l2:
        return "二级", l1 - value            # 距一级缺口（负=还差多少）
    elif value >= l3:
        return "三级", l2 - value            # 距二级缺口
    else:
        return "不达标", l3 - value          # 距三级缺口

print("=" * 78)
print("TASK-STD-A：JY/T 表9 12点 SPL差值补算 + 分级  (N=16/d=55/L=825/Dolph-20)")
print("=" * 78)
print(f"声速 c={C} m/s | 孔径 L={L_APERTURE_MM:.0f}mm | 阵元=isotropic | broadside")
print()

# ─── 前置陷阱2 数值验证：180° 前后对称 artifact ───
print("【前置陷阱2 验证】isotropic 线阵前后对称性：AF(180°) 应 = AF(0°)")
for f in FREQS:
    d180 = spl_diff_db(180.0, f)[0]
    print(f"  {f:>5}Hz : SPL差(180°) = {d180:+.4f} dB  "
          f"→ {'≈0 (前后对称artifact，不可评)' if abs(d180) < 0.01 else '⚠非零，需检查'}")
print()

# ─── 12 点主表（30/90 实算；180 标不可评）───
print("【12点 SPL差值表】值=θ处相对0°的衰减量(dB)，正=衰减")
print(f"{'频率':>6} {'角度':>5} {'SPL差[L2-numpy]':>16} {'门限(1/2/3级)':>16} {'达级':>6} {'裕量到上级(dB)':>16}")
print("-" * 78)

results = {}
for f in FREQS:
    for a in ANGLES:
        if a == 180:
            d180 = spl_diff_db(180.0, f)[0]
            results[(f, a)] = ("不可评", d180)
            l1, l2, l3 = STD[(f, a)]
            print(f"{f:>6} {a:>4}° {('≈%.2f' % d180):>16} {f'{l1}/{l2}/{l3}':>16} "
                  f"{'不可评':>6} {'前后对称artifact':>16}")
        else:
            v = spl_diff_db(float(a), f)[0]
            g, margin = grade_of(v, STD[(f, a)])
            results[(f, a)] = (g, v, margin)
            l1, l2, l3 = STD[(f, a)]
            if g == "一级":
                mtxt = f"超一级+{margin:.2f}"
            elif g == "不达标":
                mtxt = f"距三级{margin:+.2f}"
            else:
                mtxt = f"距上级{margin:+.2f}"
            print(f"{f:>6} {a:>4}° {v:>16.2f} {f'{l1}/{l2}/{l3}':>16} {g:>6} {mtxt:>16}")
    print()

# ─── R8 重点核：500Hz/30° 一级裕量是否 +0.86dB ───
print("=" * 78)
print("【R8 重点核验】500Hz/30° 一级裕量是否 ≈ +0.86dB")
v_500_30 = spl_diff_db(30.0, 500)[0]
l1_500_30 = STD[(500, 30)][0]   # 一级门限 = 5dB
margin_500_30 = v_500_30 - l1_500_30
print(f"  500Hz/30° SPL差[L2-numpy] = {v_500_30:.4f} dB")
print(f"  一级门限 = {l1_500_30} dB")
print(f"  一级裕量 = {v_500_30:.4f} - {l1_500_30} = {margin_500_30:+.4f} dB")
print(f"  R8 校验：≈+0.86dB ? → {'✓ 命中 (一级值≈5.86dB)' if abs(margin_500_30 - 0.86) < 0.15 else '✗ 不符，需复核'}")
print()

# ─── 垂直面 1kHz/30° ≥12dB（=阵列主控平面，与上 1kHz/30° 同一数）───
print("=" * 78)
print("【垂直面 1kHz/30° ≥12dB】(本线阵 主控平面=阵列轴平面)")
v_vert_1k_30 = spl_diff_db(30.0, 1000)[0]
print(f"  1kHz/30° SPL差[L2-numpy] = {v_vert_1k_30:.2f} dB ; 门限 ≥12dB")
print(f"  → {'达标 ✓' if v_vert_1k_30 >= 12 else '不达标 ✗'} (裕量 {v_vert_1k_30-12:+.2f}dB)")
print("  注：线阵指向性平面唯一(阵列轴平面)；'水平/垂直'取决于安装朝向，")
print("      此值即阵列主控平面 30° 衰减，与上表 1kHz/30° 同源同值。")
print()

# ─── CSV 落盘 ───
import csv
OUT_CSV = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint3/audit/std_table9_compliance.csv"
with open(OUT_CSV, "w", newline="", encoding="utf-8") as fp:
    w = csv.writer(fp)
    w.writerow(["freq_hz", "angle_deg", "SPL_diff_dB_numpy", "L1_thr", "L2_thr", "L3_thr",
                "grade", "margin_to_next_dB", "note"])
    for f in FREQS:
        for a in ANGLES:
            l1, l2, l3 = STD[(f, a)]
            if a == 180:
                d180 = results[(f, a)][1]
                w.writerow([f, a, round(d180, 4), l1, l2, l3, "不可评", "",
                            "isotropic前后对称artifact；真实后向抑制待COMSOL障板+消声室实测"])
            else:
                g, v, m = results[(f, a)]
                w.writerow([f, a, round(v, 3), l1, l2, l3, g, round(m, 3),
                            "仿真推算非实测"])
print(f"[CSV] 已导出: {OUT_CSV}")
print("=" * 78)
print("完成。所有数字标 [L2-numpy]，可复现（同 sweep_d55.py 阵因子 + Dolph-20）。")
print("=" * 78)
