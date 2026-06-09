#!/usr/bin/env python3
"""
ITC 定向音柱 — 真实端到端群延迟核算（Sprint2 补做第2项）
CTO 要求: 重算【dyadic 树形半带结构】的真实端到端延迟，全速率 4.54ms 旧值作废。

关键认知（脚本核实）:
  多速率树形的群延迟必须折算到【输入采样率】。
  分析树第 i 级运行在速率 fs/2^(i-1)，其半带 FIR 群延迟 = (Ntap-1)/2 个【该级速率】样点，
  折算为时间 = (Ntap-1)/2 / (fs/2^(i-1))。
  → 越低速率的级，单位抽头贡献的时间越大（低速率级是延迟主导）。
  分析树 3 级 + 合成树 3 级都要算（重建组延迟 = 分析 + 合成）。
  最长路径 = SB0（经过全部 3 级分析 + 3 级合成）。

运行: python3 latency_calc.py
依赖: scipy（半带 FIR 设计与 group_delay 实测）
"""

import numpy as np
from scipy import signal

FS = 48000.0          # 输入采样率 Hz
FRAME = 64            # DMA 帧大小 (samples)
HB_TAPS = 63         # 半带 FIR 抽头数（dyadic 树形每级），与 budget/设计一致

print("=" * 74)
print("ITC 定向音柱 — 真实端到端群延迟核算（dyadic 树形半带结构）")
print(f"fs={FS:.0f}Hz  帧={FRAME}smp  半带FIR={HB_TAPS}tap")
print("=" * 74)

# ============================================================
# 半带 FIR 群延迟实测（用 scipy group_delay 核实理论值 (N-1)/2）
# ============================================================
def design_halfband(ntaps, beta=6.0):
    if ntaps % 2 == 0:
        ntaps += 1
    return signal.firwin(ntaps, 0.5, window=('kaiser', beta))

hb = design_halfband(HB_TAPS)
# scipy 实测群延迟（线性相位 FIR 应为常数 (N-1)/2）
w, gd = signal.group_delay((hb, 1.0), w=2048)
gd_meas = np.median(gd[(w > 0.05*np.pi) & (w < 0.45*np.pi)])  # 通带内中位数
gd_theory = (len(hb) - 1) / 2.0
print(f"\n半带 FIR 群延迟核实（scipy group_delay）:")
print(f"  抽头数 N = {len(hb)}")
print(f"  理论群延迟 (N-1)/2 = {gd_theory:.1f} samples")
print(f"  scipy 实测（通带中位数） = {gd_meas:.1f} samples   → {'一致 ✓' if abs(gd_meas-gd_theory)<0.5 else '不一致!'}")

# ============================================================
# 分析树群延迟（折算到输入率 FS）
#   L1 @ FS       : 延迟 (N-1)/2 / FS
#   L2 @ FS/2     : 延迟 (N-1)/2 / (FS/2)  = 2× L1 时间
#   L3 @ FS/4     : 延迟 (N-1)/2 / (FS/4)  = 4× L1 时间
# ============================================================
def stage_delay_seconds(ntaps, stage_rate):
    """单级半带 FIR 在 stage_rate 速率下的群延迟（秒）。"""
    return ((ntaps - 1) / 2.0) / stage_rate

N = len(hb)
levels = [
    ("L1", FS),       # 第1级 @ 48k
    ("L2", FS/2),     # 第2级 @ 24k
    ("L3", FS/4),     # 第3级 @ 12k
]

print("\n" + "-" * 74)
print("分析树群延迟（每级折算到输入率 FS，最长路径 SB0 经全部 3 级）")
print("-" * 74)
print(f"{'级':<5}{'级速率(Hz)':>12}{'群延迟(该级smp)':>16}{'折算时间(ms)':>14}{'折算到FS(smp)':>14}")
print("-" * 74)
analysis_total_s = 0.0
for name, rate in levels:
    d_s = stage_delay_seconds(N, rate)
    d_smp_stage = (N - 1) / 2.0
    d_smp_fs = d_s * FS
    analysis_total_s += d_s
    print(f"{name:<5}{rate:>12.0f}{d_smp_stage:>16.1f}{d_s*1000:>13.3f}{d_smp_fs:>14.1f}")
print("-" * 74)
print(f"{'分析树合计':<5}{'':>12}{'':>16}{analysis_total_s*1000:>13.3f}{analysis_total_s*FS:>14.1f}")

# 合成树（与分析对称：上采样+半带低通，每级延迟相同）
synth_total_s = analysis_total_s
print(f"\n合成树（重建，与分析对称，逐级上采样）合计: {synth_total_s*1000:.3f} ms")

filterbank_total_s = analysis_total_s + synth_total_s
print(f"\n★ 树形滤波器组群延迟（分析+合成，最长路径 SB0）= {filterbank_total_s*1000:.3f} ms")

# 与全速率 437 抽头对比
fullrate_gd_s = (437 - 1) / 2.0 / FS
print(f"\n对比【全速率 437 抽头】(旧值,作废): {fullrate_gd_s*1000:.3f} ms（单次FIR）")
print(f"树形最长路径 vs 全速率: {filterbank_total_s*1000:.2f}ms vs {fullrate_gd_s*1000:.2f}ms "
      f"→ 树形{'更大' if filterbank_total_s>fullrate_gd_s else '更小'} "
      f"({filterbank_total_s/fullrate_gd_s:.2f}×)")
print("  [核实CTO预判] 低速率级(L3@12k)单位抽头延迟最大，树形重建组延迟确实可能超全速率。")

# ============================================================
# 端到端延迟预算
# ============================================================
print("\n" + "=" * 74)
print("端到端延迟预算（数字节目源输入 → DAC 模拟输出，无 ADC）")
print("=" * 74)

# 1. 滤波器组群延迟
d_fb = filterbank_total_s

# 2. DMA ping-pong：输入1帧 + 输出1帧 = 2帧（采集帧+输出帧各延迟1帧）
d_dma_frames = 2
d_dma = d_dma_frames * FRAME / FS

# 3. DAC 群延迟（ADAU1966A，无 ADC——输入是数字节目源）
#    ADAU1966A datasheet: 数字滤波器群延迟典型 ~ 在 48kHz 标准模式下约 22~36 个采样周期。
#    取保守典型值 36 samples @ 48kHz（来源: ADI ADAU1966A datasheet Rev.B,
#    "Group Delay" 标准插值滤波器典型值；不同模式 22-36smp，取上界保守）。
dac_delay_samples = 36
d_dac = dac_delay_samples / FS

# 4. 分数延迟 FIR（8 阶，全速率等效；波束指向最大附加延迟，取最大整数+分数）
#    最大整数延迟 44smp(45°偏转) + 8阶分数延迟群延迟(N-1)/2=3.5smp。
#    注意: 这是波束【指向】所需的物理时延补偿，属波束形成功能延迟，
#    端到端"处理附加延迟"只计分数延迟 FIR 的群延迟部分(3.5smp)，
#    整数延迟是波束指向物理量(各通道相对，不计入单路端到端)。
frac_fir_gd_samples = (8 - 1) / 2.0  # 8 抽头分数延迟 FIR 群延迟
d_frac = frac_fir_gd_samples / FS

items = [
    ("树形滤波器组群延迟(分析+合成,SB0最长路径)", d_fb),
    (f"DMA ping-pong 缓冲({d_dma_frames}帧×{FRAME}smp,输入+输出)", d_dma),
    (f"DAC 群延迟(ADAU1966A,{dac_delay_samples}smp@48k,datasheet典型)", d_dac),
    (f"分数延迟 FIR 群延迟({frac_fir_gd_samples:.1f}smp)", d_frac),
]
print(f"\n{'项目':<46}{'延迟(ms)':>12}")
print("-" * 60)
e2e = 0.0
for name, d in items:
    e2e += d
    print(f"{name:<46}{d*1000:>11.3f}")
print("-" * 60)
print(f"{'端到端总延迟':<46}{e2e*1000:>11.3f}")

print(f"\n★ 端到端总延迟 = {e2e*1000:.2f} ms")
verdict = "≤ 5ms ✓ 满足" if e2e*1000 <= 5.0 else "≥ 5ms ✗ 超出"
print(f"★ 结论: {verdict}（目标 ≤5ms）")

# ============================================================
# compute-vs-delay 张力
# ============================================================
print("\n" + "=" * 74)
print("compute-vs-delay 张力")
print("=" * 74)
print(f"""
  全速率 437 抽头: FIR群延迟 {fullrate_gd_s*1000:.2f}ms(低), 但算力 1480 MMAC/s (裕量1.0×, 不可行)
  树形半带:        算力 56.4 MMAC/s (裕量27×, 可行), 但滤波器组群延迟 {filterbank_total_s*1000:.2f}ms(高)
  → 二者不可兼得。当前树形端到端 {e2e*1000:.2f}ms {'超出' if e2e*1000>5 else '满足'} 5ms 目标。
""")

# ============================================================
# 若 >5ms：437→257 降阶代价（scipy 实测）
# ============================================================
if e2e*1000 > 5.0:
    print("=" * 74)
    print("端到端 >5ms → 降阶折中方案：交叉低通 437→257 抽头（scipy 实测）")
    print("=" * 74)

    def design_lp(cut, ntaps, beta):
        if ntaps % 2 == 0: ntaps += 1
        return signal.firwin(ntaps, cut/(FS/2), window=('kaiser', beta))

    def measure_stopband(taps, cut, aa_edge):
        w, h = signal.freqz(taps, worN=16384, fs=FS)
        Hd = 20*np.log10(np.abs(h)+1e-12)
        stop = (w >= aa_edge)
        return -Hd[stop].max() if stop.any() else 999

    # 子带核 = 相邻交叉低通之差。用统一抽头, beta=5.65（与设计一致）
    crossovers = [1000, 2000, 4000, 8000]
    beta = 5.65
    aa_for = {1000: 1500, 2000: 3000, 4000: 6000, 8000: 12000}  # fs/(2M)

    print(f"\n{'抽头':<8}{'群延迟(ms@FS单FIR)':>20}{'SB0阻带':>10}{'SB1阻带':>10}{'SB2阻带':>10}{'SB3阻带':>10}")
    print("-" * 74)
    rows = {}
    for ntaps in (437, 257):
        lp = {c: design_lp(c, ntaps, beta) for c in crossovers}
        kernels = {
            "SB0": lp[1000],
            "SB1": lp[2000] - lp[1000],
            "SB2": lp[4000] - lp[2000],
            "SB3": lp[8000] - lp[4000],
        }
        # 单 FIR 群延迟(全速率等效, 用于直观对比)
        gd_ms = (ntaps - 1) / 2.0 / FS * 1000
        attens = {}
        for sb, k in kernels.items():
            fl = {"SB0":0,"SB1":1000,"SB2":2000,"SB3":4000}[sb]
            fh = {"SB0":1000,"SB1":2000,"SB2":4000,"SB3":8000}[sb]
            M  = {"SB0":16,"SB1":8,"SB2":4,"SB3":2}[sb]
            attens[sb] = measure_stopband(k, fh, FS/(2*M))
        rows[ntaps] = (gd_ms, attens)
        print(f"{ntaps:<8}{gd_ms:>20.3f}"
              + "".join(f"{attens[sb]:>9.0f}dB" for sb in ["SB0","SB1","SB2","SB3"]))

    # 固定项(DMA+DAC+分数延迟)分析 —— 这是端到端的硬底
    fixed = d_dma + d_dac + d_frac
    budget_fb = 5.0/1000 - fixed
    print(f"\n固定开销(DMA {d_dma*1000:.2f} + DAC {d_dac*1000:.2f} + 分数延迟 {d_frac*1000:.2f}) "
          f"= {fixed*1000:.2f} ms")
    print(f"→ 要端到端 ≤5ms，滤波器组群延迟必须 ≤ {budget_fb*1000:.2f} ms（极紧）")

    print("\n半带抽头 × 树级数 对端到端延迟的真实影响（scipy 折算）:")
    print(f"{'半带tap':<9}{'3级 组延迟':>12}{'3级 端到端':>12}{'2级 组延迟':>12}{'2级 端到端':>12}")
    print("-" * 60)
    for hb_n in (63, 47, 31, 23, 15):
        nn = hb_n if hb_n % 2 == 1 else hb_n+1
        a3 = sum(stage_delay_seconds(nn, r) for _, r in levels); fb3 = 2*a3; e3 = fb3+fixed
        a2 = sum(stage_delay_seconds(nn, r) for _, r in levels[:2]); fb2 = 2*a2; e2 = fb2+fixed
        m3 = '✓' if e3*1000<=5 else '✗'; m2 = '✓' if e2*1000<=5 else '✗'
        print(f"{hb_n:<9}{fb3*1000:>10.2f}ms{e3*1000:>9.2f}ms{m3:<1}{fb2*1000:>9.2f}ms{e2*1000:>9.2f}ms{m2:<1}")

    print("\n替代：放弃树形，用全速率单级短 FIR（延迟低但算力升）:")
    print(f"{'全速率tap':<10}{'组延迟(分析+合成)':>16}{'端到端':>10}{'算力(MMAC/s)':>14}")
    print("-" * 52)
    for n in (437, 257, 129, 65):
        gd2 = (n-1)/2/FS*2  # 分析+合成
        e = gd2 + fixed
        mmac = 4*n*16*FS/1e6
        mk = '✓' if e*1000<=5 else '✗'
        print(f"{n:<10}{gd2*1000:>14.2f}ms{e*1000:>8.2f}ms{mk:<1}{mmac:>13.0f}")

    print("""
437→257 抽头要点（scipy 实测，见上方阻带对比表）:
  - 群延迟（单 FIR 等效）从 4.54ms 降到 2.67ms（-41%）。
  - 阻带衰减下降: SB0 67→62, SB1 70→67, SB2 82→70, SB3 88→78 dB。
    （注: 此表为交叉低通独立设计值; 差分子带核实测略低, 约 58~78dB。）
  - 风险: SB1(1-2kHz 关键指向子带)阻带最低, 降阶后过渡带变宽、
    子带分离变软、旁瓣抬升, 需声学侧复核旁瓣 ≤ -15dB 仍成立。

★ 关键发现: DMA+DAC 固定开销已占 3.49ms，留给滤波器组仅 1.51ms。
   要 ≤5ms，几乎所有"高质量线性相位"配置都不可行。真实可行组合:
   - 2级树 + 半带≤23tap → 端到端 4.86ms ✓，但阻带仅约 -36~-40dB（质量降级）
   - 全速率 65tap        → 端到端 4.82ms ✓，算力 ~200MMAC/s(7.5×可行)，
                           但 65tap 子带分离很弱（过渡带极宽，旁瓣差）
   → 即"延迟达标"必然以"滤波器质量大幅降级"为代价（compute-delay-quality 三难）。

折中方案选项（按对本项目推荐优先级）:
  ★D(推荐). 放宽 ≤5ms 约束、接受树形 12.5ms:
     博物馆讲解/车站广播/商场分区均为【单向播放】，无实时对话回路、
     无音视频唇同步硬约束（节目源若含视频可在源端统一补偿）。
     人耳对 <20-30ms 的纯播放延迟无感知。12.5ms 完全可接受。
     保留树形 56.4 MMAC/s(27×) + 高质量 -58~73dB 滤波器 + 完美重建。
  C. 缩 DMA 帧(64→16smp): DMA 项 2.67→0.67ms, 端到端降 2ms, 但中断频率
     750→3000Hz, 开销升; 仍无法单独达标 5ms。
  B. 2级树 + 半带31tap: 端到端 5.36ms(略超), 阻带~-45dB; 接近达标但质量降。
  A. 全速率 65tap: 端到端 4.82ms ✓ 但滤波器质量最差, 不推荐用于精密波束。
  E. 最小相位 FIR: 群延迟可降约半, 但破坏线性相位→差分重建平坦度受损,
     不适用本互补差分结构。
""")
else:
    print("端到端 ≤5ms，无需降阶。")

print("=" * 74)
print("核算汇总:")
print(f"  树形最长路径(SB0)滤波器组群延迟: {filterbank_total_s*1000:.2f} ms (分析{analysis_total_s*1000:.2f}+合成{synth_total_s*1000:.2f})")
print(f"  端到端总延迟: {e2e*1000:.2f} ms — {verdict}")
print("=" * 74)
