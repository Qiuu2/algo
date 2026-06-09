"""
ITC 定向音柱 — 声学仿真专家 Agent  (TASK-STD-A2)
任务：FIB（频率不变波束 / 每频段独立优化）FIR 混合架构纸面预研。
几何固定：N=16 / d=55mm / L=825mm / broadside / isotropic（SC-S3-GEOM-01，不动）。

【核心思想】
  Dolph 单频最优 → 全频段同一加权，无法兼顾各频段（R10：2k/90°仅二级=23.01dB）。
  FIB = 每子带用【不同加权】，对该子带独立优化方向图。
  本脚本桌面验证：
    1kHz 子带：保 Dolph-20（BW@1k=29.28°，不破≤30°规格）；
    2kHz 子带：加深 Dolph 至 -25dB（让 2k/90° 衰减 ≥25dB）；
    4kHz 子带：加深 Dolph 至 -30dB（同时优化，但 isotropic 高频偏乐观[PF-6]，
              且 6.2kHz 栅瓣几何限制救不了高频后向，诚实标注）。

【口径声明】
  - SPL差值(θ) = -20log10|AF(θ)/AF(0)| = θ处相对主瓣衰减量(dB，正值)（同 std_table9 口径）。
  - BW = -6dB 全角宽度（同 sweep_d55 / 项目口径，N.2.3）。
  - PropagationSpeed c=343 m/s（N.2.1）；阵元 isotropic（N.2.4，高频乐观 PF-6 标注）。
  - 所有数字标 [L2-numpy]；与 MATLAB 对照标 [L2-MATLAB]（若运行）。

作者：AcousticSimulationAgent v1.0 | 日期：2026-05-29
"""

import numpy as np
from scipy.signal.windows import chebwin

# ─── 物理常数 & 几何（与 sweep_d55.py / std_table9 严格一致）───
C = 343.0
N_ELEM = 16
D_M = 55.0e-3
L_APERTURE_MM = (N_ELEM - 1) * 55.0

def get_dolph(sll_db):
    """Dolph-Chebyshev 加权，归一化到峰值1。sll_db=旁瓣电平(正数,如20表示-20dB)。"""
    w = chebwin(N_ELEM, sll_db)
    return w / w.max()

def af_linear(theta_deg, freq_hz, weights):
    th = np.radians(np.atleast_1d(theta_deg).astype(float))
    k = 2 * np.pi * freq_hz / C
    n = np.arange(N_ELEM)
    phase = k * np.outer(np.sin(th), n * D_M)
    af = (weights * np.exp(1j * phase)).sum(axis=1)
    return af

def spl_diff_db(theta_deg, freq_hz, weights):
    af = af_linear(theta_deg, freq_hz, weights)
    af0 = af_linear(0.0, freq_hz, weights)[0]
    return -20.0 * np.log10(np.abs(af) / np.abs(af0) + 1e-30)

def beamwidth_6db(freq_hz, weights):
    """-6dB 全角波束宽度(度)。细扫一侧找 -6dB 点，×2。"""
    th = np.linspace(0, 90, 90001)
    att = spl_diff_db(th, freq_hz, weights)  # 衰减量(正)
    # 找首次 >=6dB 的角
    idx = np.where(att >= 6.0)[0]
    if len(idx) == 0:
        return np.nan
    # 线性插值精确化
    i = idx[0]
    if i == 0:
        return 0.0
    a0, a1 = att[i-1], att[i]
    t0, t1 = th[i-1], th[i]
    half = t0 + (6.0 - a0) * (t1 - t0) / (a1 - a0)
    return 2.0 * half

def max_sll_db(freq_hz, weights):
    """峰值旁瓣电平(dB, 负值)。扫 0-90，主瓣后第一个局部极大之后的最大旁瓣。"""
    th = np.linspace(0, 90, 90001)
    resp = -spl_diff_db(th, freq_hz, weights)  # 归一化响应(0=主瓣,负=衰减)
    # 主瓣到第一个零点后的最大值
    # 找主瓣第一零点(最深谷)
    # 简化：取从主瓣下降到首个局部最小后的全局最大旁瓣
    d = np.diff(resp)
    # 第一个上升点(谷底)之后
    rising = np.where(d > 0)[0]
    if len(rising) == 0:
        return -99.0
    start = rising[0]
    return resp[start:].max()

# ════════════════════════════════════════════════════════════════════
print("=" * 80)
print("TASK-STD-A2: FIB 频率不变波束 FIR混合架构 桌面预研")
print(f"几何 N={N_ELEM}/d={D_M*1000:.0f}mm/L={L_APERTURE_MM:.0f}mm | broadside | isotropic | c={C}m/s")
print("=" * 80)

# ─── FIB 子带加权方案 ───
SUBBANDS = [
    {"name": "SB(1k)", "freq": 1000, "sll": 20, "label": "保Dolph-20(基线,不破≤30°)"},
    {"name": "SB(2k)", "freq": 2000, "sll": 25, "label": "加深Dolph-25(目标2k/90°≥25dB)"},
    {"name": "SB(4k)", "freq": 4000, "sll": 30, "label": "加深Dolph-30(同时优化;高频PF-6乐观)"},
]
# 基线（全频段单一 Dolph-20，对照组）
W_BASE = get_dolph(20)

print("\n【对照：基线 = 全频段单一 Dolph-20（R10 短板来源）】")
print(f"{'频率':>6} {'BW@-6dB(°)':>12} {'SLL(dB)':>9} {'30°衰减':>9} {'90°衰减':>9}")
print("-" * 60)
base_rows = {}
for f in [1000, 2000, 4000]:
    bw = beamwidth_6db(f, W_BASE)
    sll = max_sll_db(f, W_BASE)
    a30 = spl_diff_db(30.0, f, W_BASE)[0]
    a90 = spl_diff_db(90.0, f, W_BASE)[0]
    base_rows[f] = (bw, sll, a30, a90)
    print(f"{f:>6} {bw:>12.2f} {sll:>9.2f} {a30:>9.2f} {a90:>9.2f}")

print("\n【FIB：每子带独立加权后】值=[L2-numpy]")
print(f"{'子带':>8} {'加权':>10} {'BW@-6dB(°)':>12} {'SLL(dB)':>9} {'30°衰减':>9} {'90°衰减':>9}")
print("-" * 78)
fib_rows = {}
for sb in SUBBANDS:
    f = sb["freq"]
    w = get_dolph(sb["sll"])
    bw = beamwidth_6db(f, w)
    sll = max_sll_db(f, w)
    a30 = spl_diff_db(30.0, f, w)[0]
    a90 = spl_diff_db(90.0, f, w)[0]
    fib_rows[f] = (bw, sll, a30, a90)
    print(f"{sb['name']:>8} {('Dolph-'+str(sb['sll'])):>10} {bw:>12.2f} {sll:>9.2f} {a30:>9.2f} {a90:>9.2f}")

print("\n【方向图改善（FIB vs 基线 Dolph-20）】")
print(f"{'频率':>6} {'BW变化(°)':>11} {'SLL改善(dB)':>12} {'90°衰减改善(dB)':>16}")
print("-" * 52)
for f in [1000, 2000, 4000]:
    b = base_rows[f]; r = fib_rows[f]
    print(f"{f:>6} {r[0]-b[0]:>+11.2f} {r[1]-b[1]:>+12.2f} {r[3]-b[3]:>+16.2f}")

# ─── 规格守门判定 ───
print("\n" + "=" * 80)
print("【规格守门判定】")
bw_1k_fib = fib_rows[1000][0]
a90_2k_fib = fib_rows[2000][3]
print(f"  1k 子带 BW@-6dB = {bw_1k_fib:.2f}°  | 规格 ≤30°  → {'守 ✓' if bw_1k_fib<=30 else '破 ✗'}")
print(f"  2k 子带 90°衰减 = {a90_2k_fib:.2f}dB | 目标 ≥25dB → {'达 ✓' if a90_2k_fib>=25 else '未达 ✗'}")
a30_4k_fib = fib_rows[4000][2]
print(f"  4k 子带 30°衰减 = {a30_4k_fib:.2f}dB（高频，isotropic偏乐观[PF-6]，实测须复核）")
print(f"  4k 后向(>6.2kHz栅瓣)：几何限制，FIB加权救不了，须缩间距/分频段（诚实标）")

# ─── FIR 长度 / 算力增量 / 延迟增量 估算（声学侧初估，待DSP复核）───
print("\n" + "=" * 80)
print("【FIR长度 / 算力增量 / 延迟增量 初估（声学侧，待 DSP teammate 正式复核）】")
print("=" * 80)

# FIB 实现方式：现有 FAS 架构已是"每子带独立加权求和"。
# Dolph 加权本身只是 16 个标量增益(放在加权求和环节)，加深 SLL 仅改系数值，
# 【不增加抽头、不增加算力】——这是关键发现。
# 真正的"频率不变波束 FIB"若要在【子带内】进一步频率细调，
# 需把每阵元的标量增益升级为短 FIR（频率相关加权）。
# 桌面保守估：每阵元 FIR 长度 16–32 tap（覆盖子带内频率变化）。

print("""
关键认知：现有 FAS 架构的"加权求和"环节，Dolph 加权=16个标量增益。
  → 仅【加深 SLL】(改 chebwin 参数) 不增加任何抽头/算力/延迟，零成本。
  → 但"标量加权"在子带内是单频最优，子带带宽内仍有残余频变。

真正的 FIB（子带内频率不变）需把【标量增益→短FIR(频率相关加权)】：
  每阵元每子带一条 FIR，长度 L_fir（桌面估 16–32 tap）。
""")

FS = 48000.0
SUBBAND_RATES = {  # 与 budget_calc.py 树形子带率一致
    "SB0(0.5-1k)": 3000, "SB1(1-2k)": 6000, "SB2(2-4k)": 12000, "SB3(4-8k)": 24000,
}

print("FIB FIR 算力增量（替换标量增益为 L_fir 抽头 FIR，每阵元每子带，子带率下运行）:")
print(f"{'L_fir':>6} {'算力增量(MMAC/s)':>18} {'相对树形56.4基线':>18}")
print("-" * 46)
BASE_TREE_MMAC = 56.4  # latency_calc.py 报告值
for L_fir in [16, 24, 32]:
    # 原标量加权求和已计入基线(16 MAC/output/子带)。FIB 增量 = (L_fir-1)倍 该环节。
    # 每子带: L_fir tap × N_ch × 子带率；原标量是 1×N_ch×子带率(已在基线)。
    # 增量 = (L_fir - 1) × N_ch × Σ子带率
    inc = sum((L_fir - 1) * N_ELEM * r for r in SUBBAND_RATES.values()) / 1e6
    print(f"{L_fir:>6} {inc:>18.3f} {('+'+format(inc/BASE_TREE_MMAC*100,'.1f')+'%'):>18}")

# 取 L_fir=32 最坏情形做守线判定
L_FIR_WORST = 32
inc_worst = sum((L_FIR_WORST - 1) * N_ELEM * r for r in SUBBAND_RATES.values()) / 1e6
total_fib_mmac = BASE_TREE_MMAC + inc_worst
CAP = 1500.0  # 21569 保守口径(同 budget_calc)
margin = CAP / total_fib_mmac
print(f"\n最坏情形 L_fir={L_FIR_WORST}: 算力增量 = {inc_worst:.1f} MMAC/s")
print(f"  FIB 总算力 ≈ {total_fib_mmac:.1f} MMAC/s (树形基线{BASE_TREE_MMAC}+增量{inc_worst:.1f})")
print(f"  21569 保守cap = {CAP:.0f} MMAC/s → 裕量 {margin:.1f}×")
print(f"  安全线 ≥10× → {'守 ✓' if margin >= 10 else '破 ✗ 触发 E-NEW-5'}")

# ─── 延迟增量 ───
print("\n【延迟增量初估（声学侧，待 DSP 复核）】")
# FIB FIR 群延迟 = (L_fir-1)/2 个子带率样点，折算到输入率。
# 最坏路径在最低子带率 SB0(3kHz)，但 SB0 是 0.5-1k 宽波束无需 FIB；
# FIB 主要用于 SB1/SB2/SB3。取 SB1(6kHz子带率)作关键路径。
print(f"{'子带(率)':>14} {'L_fir':>6} {'FIR群延迟(子带smp)':>18} {'折算输入率(ms)':>16}")
print("-" * 58)
for sbname, rate in SUBBAND_RATES.items():
    L_fir = L_FIR_WORST
    gd_sub = (L_fir - 1) / 2.0
    gd_ms = gd_sub / rate * 1000
    print(f"{sbname:>14} {L_fir:>6} {gd_sub:>18.1f} {gd_ms:>16.3f}")

# 最大延迟增量 = 最低子带率(SB0 3kHz)；但实际 FIB 用于 SB1-3。
# 保守取 SB1(6kHz)关键路径增量，且 FIB FIR 是子带内附加，叠加在现有树形延迟上。
gd_sb1_ms = (L_FIR_WORST - 1) / 2.0 / 6000 * 1000
gd_sb0_ms = (L_FIR_WORST - 1) / 2.0 / 3000 * 1000
E2E_TREE = 12.53  # latency_calc.py 报告值(树形端到端)
e2e_fib = E2E_TREE + gd_sb0_ms  # 最坏叠加最低子带率
print(f"\n延迟增量(最坏 SB0 3kHz率, L_fir=32) = {gd_sb0_ms:.3f} ms")
print(f"延迟增量(关键 SB1 6kHz率, L_fir=32) = {gd_sb1_ms:.3f} ms")
print(f"FIB 端到端 ≈ 树形{E2E_TREE}ms + {gd_sb0_ms:.2f}ms = {e2e_fib:.2f} ms")
print(f"  延迟安全线 <30ms → {'守 ✓' if e2e_fib < 30 else '破 ✗ 触发 E-NEW-5'}")

# ─── E-NEW-5 判定 ───
print("\n" + "=" * 80)
print("【E-NEW-5 判定】")
trig_margin = margin < 10
trig_lat = e2e_fib >= 30
print(f"  算力裕量 {margin:.1f}× {'< 10× → 命中' if trig_margin else '≥ 10× → 不命中'}")
print(f"  端到端延迟 {e2e_fib:.2f}ms {'≥ 30ms → 命中' if trig_lat else '< 30ms → 不命中'}")
print(f"  E-NEW-5 = {'🚨 触发' if (trig_margin or trig_lat) else '未触发（FIB 守安全线）'}")

# ─── CSV 落盘 ───
import csv
OUT = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint3/audit/A2_fib_feasibility.csv"
with open(OUT, "w", newline="", encoding="utf-8") as fp:
    w = csv.writer(fp)
    w.writerow(["freq_hz","scheme","BW_6dB_deg","SLL_dB","att30_dB","att90_dB","track"])
    for f in [1000,2000,4000]:
        b = base_rows[f]
        w.writerow([f,"baseline_Dolph20",round(b[0],3),round(b[1],3),round(b[2],3),round(b[3],3),"L2-numpy"])
    for sb in SUBBANDS:
        f=sb["freq"]; r=fib_rows[f]
        w.writerow([f,f"FIB_Dolph{sb['sll']}",round(r[0],3),round(r[1],3),round(r[2],3),round(r[3],3),"L2-numpy"])
print(f"\n[CSV] 已导出: {OUT}")
print("=" * 80)
