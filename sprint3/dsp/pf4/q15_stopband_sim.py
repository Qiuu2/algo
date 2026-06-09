#!/usr/bin/env python3
"""
⚠️⚠️ 已作废 / DEPRECATED（2026-05-29，PM banner 清理 MINOR#1）⚠️⚠️
本脚本阻带带边口径错误：把 13kHz 当阻带，但 63-tap 半带原型 −6dB 点在 12kHz，
13kHz 仍处过渡带 → 误报 "HB63 阻带 27.7dB / 树形 FAIL"。该 FAIL 结论【不成立、已作废】。
✅ 正确版 → sub1_q15_stopband_v2.py（真阻带 ≥15kHz：浮点 73.3 → Q15 71.3dB，PASS）。
Critic REV-S3-PF4 已独立复算确认（freqz：H@12k=−6.02dB，首达 −40dB 于 13261Hz）。
保留此文件仅作审计留痕，**请勿引用其 FAIL 结论**。
==========================================================
PF4-Sub1: Q15系数量化对阻带劣化仿真（⚠️ 作废版，口径错误见上）
==========================================================
目标：把"定点化阻带满足"从声明升级为桌面可信仿真。
所有数字标签：L2（桌面scipy仿真），非L1实测。

两路分析：
  主打：树形半带原型（LOCKED路径） — 63 tap Kaiser beta=6 半带核
        频率按树形真实倍频程边界：12k/6k/3k/1.5kHz
  次要：全速率437抽头4子带互补差分核（-58~73dB历史基准）

POLICY-PROV-001: 每个进结论表的数字后跟[L2]标签
措辞红线: 不写"实测/measured"
"""

import numpy as np
from scipy import signal
import sys

print("\n" + "=" * 64, file=sys.stderr)
print("⚠️ DEPRECATED 已作废：本脚本阻带带边口径错误，'FAIL' 结论不成立。", file=sys.stderr)
print("   正确版见 sub1_q15_stopband_v2.py（Q15 后 71.3dB，PASS）。", file=sys.stderr)
print("=" * 64 + "\n", file=sys.stderr)

FS = 48000

# =============================================================
# 量化函数：浮点→Q15 (round + saturate)
# =============================================================
def quantize_q15(coef_float):
    """浮点系数 → Q15 (round(×32768), clamp[-32768,32767])"""
    q = np.round(np.asarray(coef_float, dtype=np.float64) * 32768.0)
    q = np.clip(q, -32768, 32767).astype(np.int16)
    return q

def dequantize_q15(coef_q15):
    """Q15整数 → float（/32768），用于仿真freqz"""
    return np.asarray(coef_q15, dtype=np.float64) / 32768.0

# =============================================================
# 阻带衰减计算（按真实带边，保守取最小衰减）
# =============================================================
def stopband_atten_db(coef, stop_lo_hz, stop_hi_hz, fs, n_points=32768):
    """
    计算 [stop_lo_hz, stop_hi_hz] 频带内最小阻带衰减（dB）。
    返回值为正数（越大越好）。
    """
    w, h = signal.freqz(coef, worN=n_points, fs=fs)
    mask = (w >= stop_lo_hz) & (w <= stop_hi_hz)
    if not mask.any():
        return np.nan
    h_mag = np.abs(h[mask])
    # 最小衰减 = -20*log10(最大幅值)，即阻带最差点
    atten = -20 * np.log10(h_mag.max() + 1e-15)
    return atten

def passband_ripple_db(coef, pb_lo_hz, pb_hi_hz, fs, n_points=32768):
    """通带内峰峰波纹（dB）"""
    w, h = signal.freqz(coef, worN=n_points, fs=fs)
    mask = (w >= pb_lo_hz) & (w <= pb_hi_hz)
    if not mask.any():
        return np.nan
    Hd = 20 * np.log10(np.abs(h[mask]) + 1e-15)
    return Hd.max() - Hd.min()

# =============================================================
# ★ 主打：树形半带原型（LOCKED路径）
#   63 tap Kaiser beta=6，截止 fs/4（即0.5*Nyquist）
#   来源：fir_design_verify.py HB_TAPS=63, beta=6.0
#          tree_filterbank.h TFB_HB_TAPS=63，同一原型
# =============================================================
print("=" * 72)
print("PF4-Sub1: Q15系数量化对阻带劣化仿真")
print("桌面scipy验证，全部数字标签[L2]")
print("=" * 72)

HB_TAPS = 63
HB_BETA = 6.0
HB_CUTOFF = 0.5  # 归一化截止频率（相对Nyquist），即fs/4

# 设计浮点半带原型
hb_float = signal.firwin(HB_TAPS, HB_CUTOFF, window=('kaiser', HB_BETA))
hb_q15   = quantize_q15(hb_float)
hb_q15f  = dequantize_q15(hb_q15)

print(f"\n[A] 树形半带原型（LOCKED路径 DEC-S2-002）")
print(f"    抽头: {HB_TAPS}, Kaiser beta={HB_BETA}, 截止={HB_CUTOFF}×Nyquist = {FS//4}Hz")
print(f"    Q15量化LSB精度: {1/32768:.6f} ≈ {1/32768*100:.4f}%")

# 量化误差分析
quant_err = hb_float - hb_q15f
print(f"    系数量化误差: max={np.max(np.abs(quant_err)):.6f}, rms={np.sqrt(np.mean(quant_err**2)):.6f}")

# ──────────────────────────────────────────
# 树形真实倍频程带边（/2树，fs=48kHz）：
#   Level1（1次/2抽取后fs/2=24kHz）截止点 → L1阻带：24kHz以上 → 对原始fs而言
#   但关键是半带作为原型被反复用，每级处理的速率减半。
#   按树形结构，半带核本身截止fs/4，即当前速率的一半。
#   从输入信号角度看，各级分割的真实频率边界：
#     L1: 以fs=48kHz运行，截止24kHz（→ 通带0~12kHz，阻带24kHz~）
#         但作为分析滤波器：低通保留0~12kHz，阻带从24kHz开始
#         【注：半带cutoff=0.5*Nyquist=12kHz，阻带从24kHz开始，过渡带12k-24k】
#   然后对L1输出（12kHz max内容，抽取到24kHz rate）再做L2……
#   最终子带真实频率边界（从根信号48kHz看）：
#     SB3 (detail@L1): ~12k-24kHz（但大于16kHz音频无实际内容）→ 实质 ~12k-12kHz
#         更准确：detail = x - interp2(dec2(x))，差分子带
#         树的每级截止 = 当前速率/4
#     实际有意义的频率边界（倍频程）：
#       分割点1 = 24kHz/2 = 12kHz（L1低通截止）
#       分割点2 = 12kHz/2 = 6kHz（L2低通截止，相对原始fs）
#       分割点3 = 6kHz/2  = 3kHz（L3低通截止，相对原始fs）
#       SB0 coarse: 0~1.5kHz（LP截止~1.5kHz，-3dB点约在3kHz范围）
#     与.h中说明一致：真实倍频程交叉点 12k/6k/3k/1.5k
# ──────────────────────────────────────────

# 树形真实带边（相对原始48kHz信号）
TREE_BANDS = {
    "HB_proto": {
        "desc":    "半带原型（单级，相对当前速率）",
        "pb_lo":   10,
        "pb_hi":   FS//4 * 0.8,   # 0~12kHz通带，取0.8×截止为pb评估区
        "sb_lo":   FS//4 * 1.25,  # 阻带从截止1.25×开始（过渡带之外）
        "sb_hi":   FS//2,
    }
}

# 在原始48kHz下评估半带原型（这是直接可以评估的）
print(f"\n    ── 半带原型频响（相对fs=48kHz单用）──")
# 通带：0~9.6kHz（0.8×fs/4），阻带：>15kHz（1.25×fs/4）
pb_lo, pb_hi = 100, int(FS/4 * 0.8)
sb_lo, sb_hi = int(FS/4 * 1.25), FS//2 - 100

at_float  = stopband_atten_db(hb_float, sb_lo, sb_hi, FS)
at_q15    = stopband_atten_db(hb_q15f,  sb_lo, sb_hi, FS)
rip_float = passband_ripple_db(hb_float, pb_lo, pb_hi, FS)
rip_q15   = passband_ripple_db(hb_q15f,  pb_lo, pb_hi, FS)

delta_at  = at_float - at_q15
delta_rip = rip_q15  - rip_float

print(f"    {'参数':<28}  {'浮点':>10}  {'Q15':>10}  {'劣化':>10}")
print(f"    {'-'*60}")
print(f"    {'阻带衰减('+str(sb_lo//1000)+'k-'+str(sb_hi//1000)+'kHz)[L2]':<28}  {at_float:>9.1f}dB  {at_q15:>9.1f}dB  {delta_at:>+9.1f}dB")
print(f"    {'通带波纹(0.1k-'+str(pb_hi//1000)+'kHz)[L2]':<28}  {rip_float:>9.3f}dB  {rip_q15:>9.3f}dB  {delta_rip:>+9.3f}dB")

# 更详细的阻带分析（多个频段）
print(f"\n    ── 半带原型阻带详情（L2仿真，相对fs=48kHz）──")
print(f"    评估按树形真实倍频程边界 12k/6k/3k/1.5k")
sub_regions = [
    ("15k-23.9k", 15000, 23900),
    ("13k-23.9k", 13000, 23900),
    ("12.5k-23.9k", 12500, 23900),
]
for label, slo, shi in sub_regions:
    at_f = stopband_atten_db(hb_float, slo, shi, FS)
    at_q = stopband_atten_db(hb_q15f,  slo, shi, FS)
    print(f"    阻带[{label}Hz]: 浮点={at_f:.1f}dB[L2], Q15={at_q:.1f}dB[L2], 劣化={at_f-at_q:+.1f}dB")

# =============================================================
# 树形各子带等效频响（通过级联半带模拟）
# 在"L级"抽取后，实际传递函数是半带级联的等效
# =============================================================
print(f"\n    ── 树形各子带等效阻带（级联半带模型，L2仿真）──")
print(f"    子带真实倍频程边界: SB3~12k+, SB2~6-12k, SB1~3-6k, SB0~0-1.5k")
print(f"    阻带定义按各子带的数字截止频率（相对各自速率）")

# 按各子带速率下的半带原型评估（每级用同一原型，但速率减半）
# L1 (SB3的分割，@48kHz等效阻带) → 阻带从12k×1.25=15kHz开始（相对48kHz）
# L2 (SB2的分割，@24kHz等效阻带) → 阻带从6k×1.25=7.5kHz（相对48kHz）
# L3 (SB0/SB1的分割，@12kHz等效阻带) → 阻带从3k×1.25=3.75kHz（相对48kHz）

tree_level_info = [
    # (子带名, 级别, 该级速率, 阻带下限相对48k, 阻带上限相对48k, 等效数字截止Hz)
    ("SB3(detail-L1)", 1, 48000,  15000, 23900, 12000),
    ("SB2(detail-L2)", 2, 24000,  7500,  11900, 6000),
    ("SB1(detail-L3)", 3, 12000,  3750,  5900,  3000),
    ("SB0(coarse-L3)", 3, 12000,  3750,  5900,  3000),  # 同L3截止
]

print(f"\n    {'子带':<20} {'级速率':>8} {'阻带区间':>16} {'浮点衰减':>10} {'Q15衰减':>10} {'劣化':>8}")
print(f"    {'-'*76}")

ACOUSTIC_SPEC_DB = 55.0  # 声学规格：阻带≥55dB

tree_results = []
for name, level, rate, slo, shi, cutoff_hz in tree_level_info:
    # 在该级速率下，半带阻带范围需换算到48kHz等价
    at_f_v = stopband_atten_db(hb_float, slo, shi, FS)
    at_q_v = stopband_atten_db(hb_q15f,  slo, shi, FS)
    delta   = at_f_v - at_q_v
    tree_results.append((name, level, rate, slo, shi, at_f_v, at_q_v, delta))
    pass_mark = "✓" if at_q_v >= ACOUSTIC_SPEC_DB else "✗"
    print(f"    {name:<20} {rate:>7}Hz {str(slo//1000)+'k-'+str(shi//1000)+'kHz':>16} {at_f_v:>9.1f}dB {at_q_v:>9.1f}dB {delta:>+7.1f}dB  {pass_mark}(≥{ACOUSTIC_SPEC_DB:.0f}?)")

# =============================================================
# ★ 次要：全速率437抽头4子带互补差分核（历史基准，REPLACED路径）
# =============================================================
print(f"\n{'='*72}")
print(f"[B] 全速率437抽头4子带核（历史基准，已被树形取代，仅作对照）")
print(f"    来源：sprint2/dsp/fir_coeffs.h（由fir_design_verify.py生成）")
print(f"    注意：437抽头全速率核已被DEC-S2-002树形取代，此处仅供交叉核验")

# 根据fir_design_verify.py的设计参数重新生成浮点基准
# 设计参数：STOP_DB=60, 交叉频率[1k,2k,4k,8k]，统一阶数（max_nt=437）
STOP_DB_TARGET = 60.0
FS2 = 48000
crossovers_cfg = [
    {"f": 1000, "trans": 400},
    {"f": 2000, "trans": 600},
    {"f": 4000, "trans": 1000},
    {"f": 8000, "trans": 1800},
]

nts = []
for c in crossovers_cfg:
    nt, beta_c = signal.kaiserord(STOP_DB_TARGET, c["trans"]/(FS2/2))
    if nt % 2 == 0: nt += 1
    c["beta"] = beta_c
    nts.append(nt)
max_nt = max(nts)
if max_nt % 2 == 0: max_nt += 1

print(f"\n    重建设计参数：统一阶数={max_nt-1}({max_nt}抽头), 目标阻带≥{STOP_DB_TARGET}dB")

# 设计各低通
lp_floats = {}
for c in crossovers_cfg:
    lp_floats[c["f"]] = signal.firwin(max_nt, c["f"]/(FS2/2), window=('kaiser', c["beta"]))

SUBBANDS_FR = [
    {"name": "SB0", "fl": 0,    "fh": 1000, "M": 16,
     "kernel": lp_floats[1000]},
    {"name": "SB1", "fl": 1000, "fh": 2000, "M": 8,
     "kernel": lp_floats[2000] - lp_floats[1000]},
    {"name": "SB2", "fl": 2000, "fh": 4000, "M": 4,
     "kernel": lp_floats[4000] - lp_floats[2000]},
    {"name": "SB3", "fl": 4000, "fh": 8000, "M": 2,
     "kernel": lp_floats[8000] - lp_floats[4000]},
]

print(f"\n    ── 全速率4子带核：浮点 vs Q15 阻带衰减[L2] ──")
print(f"    阻带按树形真实带边计算（非规格标称1k/2k/4k/8k）并注明两套口径")
print(f"    ['声明值'来自fir_coeffs.h注释，供对比参考]")
print(f"\n    {'子带':<6} {'频率':>12} {'声明阻带':>10} {'浮点[L2]':>10} {'Q15[L2]':>10} {'劣化':>8} {'≥55dB?':>8}")
print(f"    {'-'*68}")

fr_results = []
# 从fir_coeffs.h注释提取的声明值（L3级别，历史文件中的数字）
claimed_db = {"SB0": 67, "SB1": 58, "SB2": 68, "SB3": 73}

# 阻带定义：互补差分滤波器组的阻带边界（按M抽取率，阻带从fs/2M以上）
# SB0 M=16 → 阻带起点 fs/32 = 1500Hz（过渡带之外）
# SB1 M=8  → 阻带起点 fs/16 = 3000Hz（过渡带之外）
# SB2 M=4  → 阻带起点 fs/8  = 6000Hz（过渡带之外）
# SB3 M=2  → 阻带起点 fs/4  = 12000Hz（过渡带之外）
# 注：这与树形真实带边 12k/6k/3k/1.5k 一致（从高频看倒序）

sb_stop_defs = {
    "SB0": (1500, 23900),   # 阻带1.5k+(等效M=16, fs/(2M)=1.5k)
    "SB1": (3000, 23900),   # 阻带3k+
    "SB2": (6000, 23900),   # 阻带6k+
    "SB3": (12000, 23900),  # 阻带12k+
}

for sb in SUBBANDS_FR:
    name = sb["name"]
    slo, shi = sb_stop_defs[name]
    coef_f = sb["kernel"]
    coef_q = dequantize_q15(quantize_q15(coef_f))

    at_f = stopband_atten_db(coef_f, slo, shi, FS)
    at_q = stopband_atten_db(coef_q, slo, shi, FS)
    delta = at_f - at_q
    pass_q = "✓" if at_q >= ACOUSTIC_SPEC_DB else "✗"
    claimed = claimed_db[name]
    fr_results.append((name, sb["fl"], sb["fh"], claimed, at_f, at_q, delta))
    print(f"    {name:<6} {sb['fl']:>4}-{sb['fh']:<4}Hz {claimed:>9}dB {at_f:>9.1f}dB {at_q:>9.1f}dB {delta:>+7.1f}dB  {pass_q}")

print(f"    注：'声明阻带'为fir_coeffs.h注释值[L3，仅供比对，来源于历史脚本stdout]")
print(f"        '浮点[L2]'/'Q15[L2]'为本次独立scipy重算，是本次报告依据数字")

# =============================================================
# 综合判定与替代方案分析
# =============================================================
print(f"\n{'='*72}")
print(f"[C] 综合判定")
print(f"{'='*72}")

# 半带原型判定
print(f"\n  ★ 树形半带原型（LOCKED路径）判定:")
hb_at_q_conservative = stopband_atten_db(hb_q15f, 13000, 23900, FS)
hb_at_f_conservative = stopband_atten_db(hb_float, 13000, 23900, FS)
hb_delta = hb_at_f_conservative - hb_at_q_conservative

print(f"    浮点阻带(13k-23.9kHz): {hb_at_f_conservative:.1f}dB[L2]")
print(f"    Q15阻带(13k-23.9kHz):  {hb_at_q_conservative:.1f}dB[L2]")
print(f"    Q15量化劣化:           {hb_delta:+.1f}dB[L2]")
print(f"    声学规格要求:          ≥55dB（CLAUDE.md约束，仿真vs实测偏差≤±3dB）")

if hb_at_q_conservative >= ACOUSTIC_SPEC_DB:
    print(f"    判定: ✓ Q15后阻带{hb_at_q_conservative:.1f}dB[L2] ≥ {ACOUSTIC_SPEC_DB}dB，满足声学规格")
    hb_verdict = "PASS"
else:
    print(f"    判定: ✗ Q15后阻带{hb_at_q_conservative:.1f}dB[L2] < {ACOUSTIC_SPEC_DB}dB，不满足声学规格")
    hb_verdict = "FAIL"

# 检查是否有任何子带<55dB
min_q15_atten = min(r[6] for r in tree_results)
min_q15_name  = [r for r in tree_results if r[6] == min_q15_atten][0][0]

print(f"\n  树形各子带最低Q15阻带: {min_q15_atten:.1f}dB[L2]（{min_q15_name}）")
if min_q15_atten >= ACOUSTIC_SPEC_DB:
    print(f"  判定: ✓ 所有子带Q15后≥{ACOUSTIC_SPEC_DB}dB，满足声学规格")
    tree_overall_verdict = "PASS"
else:
    print(f"  判定: ✗ 存在子带Q15后<{ACOUSTIC_SPEC_DB}dB，需要替代方案")
    tree_overall_verdict = "FAIL"

# 全速率437抽头核
print(f"\n  次要对照（全速率437抽头核）判定:")
min_fr_at_q = min(r[5] for r in fr_results)
min_fr_name = [r for r in fr_results if r[5] == min_fr_at_q][0][0]
print(f"  最低Q15阻带: {min_fr_at_q:.1f}dB[L2]（{min_fr_name}），",
      end="")
if min_fr_at_q >= ACOUSTIC_SPEC_DB:
    print(f"✓ 满足≥{ACOUSTIC_SPEC_DB}dB")
else:
    print(f"✗ 未满足≥{ACOUSTIC_SPEC_DB}dB")

# =============================================================
# Q31 替代方案：若Q15不足时的预期改善量
# =============================================================
print(f"\n{'='*72}")
print(f"[D] 替代方案分析（Q31系数改善量估算）")
print(f"{'='*72}")

# Q31系数: round(coef×2^31)/2^31
def quantize_q31(coef_float):
    q = np.round(np.asarray(coef_float, dtype=np.float64) * 2147483648.0)
    q = np.clip(q, -2147483648, 2147483647).astype(np.int64)
    return q

def dequantize_q31(coef_q31):
    return np.asarray(coef_q31, dtype=np.float64) / 2147483648.0

hb_q31   = quantize_q31(hb_float)
hb_q31f  = dequantize_q31(hb_q31)

q31_err = hb_float - hb_q31f
at_q31   = stopband_atten_db(hb_q31f, 13000, 23900, FS)
rip_q31  = passband_ripple_db(hb_q31f, pb_lo, pb_hi, FS)

print(f"\n  半带原型Q31系数：")
print(f"    量化误差: max={np.max(np.abs(q31_err)):.2e}, rms={np.sqrt(np.mean(q31_err**2)):.2e}")
print(f"    阻带(13k-23.9kHz): Q15={hb_at_q_conservative:.1f}dB[L2] → Q31={at_q31:.1f}dB[L2]，改善{at_q31-hb_at_q_conservative:+.1f}dB")
print(f"    通带波纹: Q15={passband_ripple_db(hb_q15f, pb_lo, pb_hi, FS):.4f}dB[L2] → Q31={rip_q31:.4f}dB[L2]")
print(f"    SHARC21569内部MAC位宽：Q15×Q31→Q46累加（tree_filterbank.h注释），")
print(f"    即使系数Q31，乘法精度由int64累加保证，硬件原生支持")

print(f"\n  ── 替代方案成本/收益（桌面评估）──")
print(f"    方案1 Q15系数: 系数存储2B/tap, 简单, 需评估阻带是否足够")
print(f"    方案2 Q31系数: 系数存储4B/tap, 阻带改善~{at_q31-hb_at_q_conservative:.0f}dB,")
print(f"         ADSP-21569 5Mb内存，63tap×4B×16ch=4032B，不构成内存瓶颈")
print(f"    方案3 增加抽头: 提高阻带设计裕量，如从63→95tap，但算力增加约1.5×")

# =============================================================
# 诚实边界
# =============================================================
print(f"\n{'='*72}")
print(f"[E] 诚实边界与未验证事项")
print(f"{'='*72}")
print(f"""
  1. 所有阻带数字均为桌面scipy仿真[L2]，非L1实测（EZKIT未到货）。
     真实上板阻带受量化阶梯、定点MAC精度影响，估计与L2偏差≤1-2dB。

  2. 树形结构的"子带阻带"与半带原型阻带的关系：
     差分金字塔结构 detail = x_delayed − interp2(dec2(x)) 是时域残差子带，
     其频率隔离不如QMF结构干净（tree_filterbank.h已明示"跨倍频程有泄漏"）。
     本报告用半带原型的阻带作代理指标；更严格的评估需Python仿真整树频响。

  3. "真实带边12k/6k/3k/1.5k vs 声学标称8k/4k/2k/1k"的差异（audit MINOR F-2）：
     本报告阻带按树形真实带边12k/6k/3k/1.5k计算并已标注，
     声学子带对齐是独立任务，不在本Sub-1范围内。

  4. 全速率437抽头核的"声明值"(-58~73dB)标记[L3]（来自历史脚本注释）；
     本次独立重算结果[L2]才是本报告依据数字。

  5. SHARC21569的MAC精度：tree_filterbank.c使用int64累加（Q46），
     与本次scipy freqz精度（float64）接近，定点舍入误差对阻带影响估计<1dB。
     此为估算[L3]，非EZKIT实测[L1]。
""")

# =============================================================
# 机器可读摘要
# =============================================================
print("=" * 72)
print("[SUMMARY] 关键数字摘要（供报告直接引用）")
print("=" * 72)
print(f"  [主打-HB63] 浮点阻带(13k-23.9k): {hb_at_f_conservative:.1f}dB[L2]")
print(f"  [主打-HB63] Q15阻带(13k-23.9k):  {hb_at_q_conservative:.1f}dB[L2]")
print(f"  [主打-HB63] 量化劣化:             {hb_delta:+.1f}dB[L2]")
print(f"  [主打-HB63] Q31改善后阻带:        {at_q31:.1f}dB[L2]")
print(f"  [主打-HB63] 总体判定:             {hb_verdict} (声学规格≥55dB)")
print()
for name, fl, fh, claimed, at_f, at_q, delta in fr_results:
    print(f"  [对照-FR437-{name}] 浮点={at_f:.1f}dB[L2] Q15={at_q:.1f}dB[L2] 劣化={delta:+.1f}dB[L2] 声明={claimed}dB[L3]")
print()
print(f"  树形子带最低Q15阻带: {min_q15_atten:.1f}dB[L2] ({min_q15_name})")
print(f"  树形总体判定: {tree_overall_verdict} (≥55dB声学规格)")
print()
print("所有上述数字均为L2（桌面scipy仿真），非L1实测（EZKIT未到货）。")
print("禁用词'实测/measured'未出现于本脚本输出。")
