"""
ITC 定向音柱 — 声学仿真专家 Agent  (TASK-STD-A1)
任务：静态加权微调可行性 —— 能否在不破 BW@1k ≤30° 规格前提下，
      把 2kHz/90° SPL差值 从 Dolph-20 的 23.01dB 拉到 ≥25dB（一级）？

【几何】N=16 / d=55mm / L=825mm / Dolph/Taylor 加权 / broadside / isotropic
        (SC-S3-GEOM-01；与已三轨验证的 sweep_d55.py / std_table9_compliance.py 同一阵因子)

【两个口径，同一阵因子，勿混淆】
  (A) SPL差值(θ) = −20·log10|AF(θ)/AF(0)|  = θ处相对主瓣衰减量(dB,正)。本任务核心指标=2kHz/90°。
  (B) BW(波束宽度) = −6dB 全角宽度(度) = 2 × (单侧 −6dB 半角)。规格红线=BW@1k ≤30°。

【加权方案】Dolph-Cheby -20dB(现基线) / -22dB / -25dB / Taylor -25dB(nbar=5)
【阵元假设】isotropic —— 高频(≥2kHz)对宽角度性能偏乐观(PF-6)，已标注。

作者：AcousticSimulationAgent v1.0 | 日期：2026-05-29 | 三轨：numpy 主算
约束：所有数字标 [L2-numpy]；与 sweep_d55.py 阵因子严格一致，可复现。
"""

import numpy as np
from scipy.signal.windows import chebwin, taylor

# ─── 物理常数 & 几何（与 sweep_d55.py / std_table9_compliance.py 严格一致）───
C = 343.0                      # m/s 声速 (20°C)  —— N.2.1
N_ELEM = 16
D_M = 55.0e-3                  # 55mm  —— [L1拆机实测]
L_APERTURE_MM = (N_ELEM - 1) * 55.0   # 825mm 声学孔径

THETA_FINE = np.linspace(0, 90, 1801)   # 0.05° 分辨率（与基线一致）

# ─── 加权方案定义（全部归一化 max=1）───
def w_dolph(sll_db):
    w = chebwin(N_ELEM, sll_db)
    return w / w.max()

def w_taylor(sll_db, nbar=5):
    # taylorwin: sll 以正 dB 给出
    w = taylor(N_ELEM, nbar=nbar, sll=sll_db)
    return w / w.max()

WEIGHTS = {
    "Dolph-20 (基线)": w_dolph(20),
    "Dolph-22":        w_dolph(22),
    "Dolph-25":        w_dolph(25),
    "Taylor-25(nbar5)":w_taylor(25, 5),
}

# ─── 阵因子（复幅值，未归一化）───
def af_complex(theta_deg, freq_hz, weights):
    th = np.radians(np.atleast_1d(theta_deg).astype(float))
    k = 2 * np.pi * freq_hz / C
    n = np.arange(N_ELEM)
    phase = k * np.outer(np.sin(th), n * D_M)
    return (weights * np.exp(1j * phase)).sum(axis=1)

# ─── 口径(A) SPL差值 = θ处衰减量(dB) ───
def spl_diff_db(theta_deg, freq_hz, weights):
    af = af_complex(theta_deg, freq_hz, weights)
    af0 = af_complex(0.0, freq_hz, weights)[0]
    ratio = np.abs(af) / np.abs(af0)
    return -20.0 * np.log10(ratio + 1e-30)

# ─── 口径(B) -6dB 全角 BW（与 sweep_d55.beamwidth_6db 完全相同算法）───
def af_db_norm(theta_deg_arr, freq_hz, weights):
    af = af_complex(theta_deg_arr, freq_hz, weights)
    mag = np.abs(af)
    mag_ref = mag[0] if mag[0] > 1e-10 else mag.max()
    return 20 * np.log10(mag / (mag_ref + 1e-30) + 1e-10)

def beamwidth_6db(freq_hz, weights, theta_arr=THETA_FINE):
    db = af_db_norm(theta_arr, freq_hz, weights)
    th = theta_arr
    peak = db[0]
    below = np.where(db < peak - 6)[0]
    if len(below) == 0:
        return 180.0
    idx = below[0]
    if idx > 0:
        t0, t1 = th[idx-1], th[idx]
        d0, d1 = db[idx-1], db[idx]
        t6 = t0 + (peak-6-d0)/(d1-d0)*(t1-t0) if d1 != d0 else t0
    else:
        t6 = th[idx]
    return float(2 * t6)   # 全角

# ─── 旁瓣级（峰值SLL，dB，负值）—— 用于解释 trade-off ───
from scipy.signal import argrelmax
def peak_sll(freq_hz, weights, theta_arr=THETA_FINE):
    db = af_db_norm(theta_arr, freq_hz, weights)
    peak = db[0]
    null_idx = None
    for i in range(1, len(db)):
        if db[i] < peak - 35:
            null_idx = i; break
    if null_idx is None:
        return -60.0
    sl = db[null_idx:]
    pk = argrelmax(sl, order=3)[0]
    if len(pk) == 0:
        return float(sl.max() - peak)
    return float(sl[pk].max() - peak)

# ═══════════════════════════════════════════════════════════════════════
print("=" * 84)
print("TASK-STD-A1：静态加权微调可行性  (N=16/d=55/L=825/broadside/isotropic)")
print("=" * 84)
print(f"声速 c={C} m/s | 孔径 L={L_APERTURE_MM:.0f}mm | 阵元=isotropic(高频宽角偏乐观 PF-6)")
print(f"目标：2kHz/90° SPL差 ≥25dB(一级) ；红线：BW@1k ≤30°(全角-6dB)")
print()

# 主表：各加权 × {2k/90° SPL差, BW@1k/2k/4k, SLL@2k}
print(f"{'加权方案':<18} {'2k/90°SPL差':>12} {'达一级?':>8} {'BW@1k':>8} {'BW@2k':>8} {'BW@4k':>8} {'SLL@2k':>9} {'BW@1k≤30?':>10}")
print("-" * 84)

rows = {}
for name, w in WEIGHTS.items():
    spl90_2k = spl_diff_db(90.0, 2000, w)[0]
    bw1k = beamwidth_6db(1000, w)
    bw2k = beamwidth_6db(2000, w)
    bw4k = beamwidth_6db(4000, w)
    sll2k = peak_sll(2000, w)
    pass_spl = "✓一级" if spl90_2k >= 25 else f"✗缺{25-spl90_2k:.2f}"
    pass_bw1 = "✓≤30" if bw1k <= 30 else f"✗破{bw1k-30:.1f}"
    rows[name] = dict(spl90_2k=spl90_2k, bw1k=bw1k, bw2k=bw2k, bw4k=bw4k, sll2k=sll2k)
    print(f"{name:<18} {spl90_2k:>10.2f}dB {pass_spl:>8} {bw1k:>7.1f}° {bw2k:>7.1f}° {bw4k:>7.1f}° {sll2k:>7.1f}dB {pass_bw1:>10}")

print()
print("=" * 84)
print("【关键 trade-off 量化】Dolph SLL 加深 → 主瓣展宽 → BW@1k 逼近/突破 30°")
print("=" * 84)
base = rows["Dolph-20 (基线)"]
for name in ["Dolph-22", "Dolph-25", "Taylor-25(nbar5)"]:
    r = rows[name]
    print(f"  {name:<18}: 2k/90°SPL差 {base['spl90_2k']:.2f}→{r['spl90_2k']:.2f}dB "
          f"(Δ{r['spl90_2k']-base['spl90_2k']:+.2f}) | "
          f"BW@1k {base['bw1k']:.1f}→{r['bw1k']:.1f}° (Δ{r['bw1k']-base['bw1k']:+.1f}°)")
print()

# 可行性判定：是否存在某加权 同时 (2k/90°≥25) 且 (BW@1k≤30)
print("=" * 84)
print("【可行性结论】是否存在加权 同时满足 2k/90°SPL差≥25dB 且 BW@1k≤30°？")
print("=" * 84)
feasible = []
for name, r in rows.items():
    if r['spl90_2k'] >= 25 and r['bw1k'] <= 30:
        feasible.append(name)
if feasible:
    print(f"  YES —— 可行方案：{feasible}")
else:
    print("  NO —— 无任何加权能同时满足两约束。")
    # 给出最接近的：能达25dB的最小BW@1k代价
    reach25 = [(n, r) for n, r in rows.items() if r['spl90_2k'] >= 25]
    if reach25:
        for n, r in reach25:
            print(f"    · {n} 能达 2k/90°={r['spl90_2k']:.2f}dB，但 BW@1k={r['bw1k']:.1f}° "
                  f"({'破规格' if r['bw1k']>30 else '未破'})")
    else:
        best = max(rows.items(), key=lambda kv: kv[1]['spl90_2k'])
        print(f"    · 即使最深加权 {best[0]} 也仅 2k/90°={best[1]['spl90_2k']:.2f}dB "
              f"(<25dB，且 BW@1k={best[1]['bw1k']:.1f}°)")
print()

# 边界探针：找出"刚好 BW@1k=30°"对应的 Dolph SLL，看此时 2k/90° 能到多少
print("=" * 84)
print("【边界探针】沿 Dolph SLL 连续扫描，定位 BW@1k=30° 临界点的 2k/90°SPL差")
print("=" * 84)
print(f"{'Dolph-SLL':>10} {'BW@1k':>9} {'2k/90°SPL差':>13}")
crit = None
for sll in np.arange(20, 40.5, 1.0):
    w = w_dolph(sll)
    bw1 = beamwidth_6db(1000, w)
    s = spl_diff_db(90.0, 2000, w)[0]
    flag = ""
    if bw1 > 30 and crit is None:
        crit = sll
        flag = "  ← BW@1k 首次破30°"
    print(f"  -{sll:>5.0f}dB {bw1:>8.1f}° {s:>11.2f}dB{flag}")
print()
if crit is not None:
    w_at = w_dolph(crit - 1.0)
    print(f"  → BW@1k 在 Dolph≈-{crit:.0f}dB 处突破30°；")
    print(f"     在仍≤30°的最深加权(-{crit-1:.0f}dB)下，2k/90°SPL差≈{spl_diff_db(90.0,2000,w_at)[0]:.2f}dB")
else:
    # BW@1k 全程未破30
    w_deep = w_dolph(40)
    print(f"  → 扫至 Dolph-40dB，BW@1k 全程 ≤30°（最深处={beamwidth_6db(1000,w_deep):.1f}°）；")
    print(f"     Dolph-40dB 下 2k/90°SPL差={spl_diff_db(90.0,2000,w_deep)[0]:.2f}dB")
print()

# ─── CSV 落盘 ───
import csv
OUT = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint3/audit/a1_static_weight_numpy.csv"
with open(OUT, "w", newline="", encoding="utf-8") as fp:
    wr = csv.writer(fp)
    wr.writerow(["weighting", "spl_diff_2k_90deg_dB", "reach_L1_25dB",
                 "BW_1k_deg", "BW_2k_deg", "BW_4k_deg", "SLL_2k_dB", "BW1k_le30"])
    for name, r in rows.items():
        wr.writerow([name, round(r['spl90_2k'],3), r['spl90_2k']>=25,
                     round(r['bw1k'],2), round(r['bw2k'],2), round(r['bw4k'],2),
                     round(r['sll2k'],2), r['bw1k']<=30])
print(f"[CSV] {OUT}")
print("=" * 84)
print("完成。所有数字 [L2-numpy]，可复现。isotropic 高频宽角偏乐观(PF-6)。仿真非实测。")
print("=" * 84)
