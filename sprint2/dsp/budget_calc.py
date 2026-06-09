#!/usr/bin/env python3
"""
ITC 定向音柱 — Filter-and-Sum 子带波束形成 算力/内存核算脚本
ADSP-21569 SHARC+ | 16通道线阵 | 48kHz | 多相抽取

运行: python3 budget_calc.py
输出: 算力预算表、SRAM估算、TDM参数
"""

import numpy as np

# ============================================================
# 基本参数
# ============================================================
FS     = 48000   # 采样率 Hz
N_CH   = 16      # 阵元数
D      = 0.055   # 阵元间距 m（d=55mm[L1拆机实测]，DEC-S3-GEOM-01；旧 0.030 系视觉估测错误，已作废）
# 注意：改 D 仅影响整数/分数延迟系数与 d/λ 栅瓣判据，【不改变 MMAC/s 算力结论】——
#       算力由子带率×抽头×通道数决定，与阵元间距 d 无关。
C      = 343.0   # 声速 m/s
FRAME  = 64      # 帧大小 samples (1.33 ms @ 48kHz)

print("=" * 70)
print("ITC 定向音柱 — Filter-and-Sum 子带波束形成 算力核算（多相抽取方案）")
print(f"平台: ADSP-21569 SHARC+  fs={FS}Hz  N_ch={N_CH}  d={D*1000}mm  帧={FRAME}samples")
print("=" * 70)

# ============================================================
# 子带参数 (多相FIR + 抽取)
# SB0: 500-1kHz   抽取16x → 3kHz子带率  原型63阶(低频宽波束可放宽到31阶)
# SB1: 1k-2kHz    抽取 8x → 6kHz子带率  原型63阶
# SB2: 2k-4kHz    抽取 4x → 12kHz子带率 原型63阶
# SB3: 4k-8kHz    抽取 2x → 24kHz子带率 原型63阶
# ============================================================
subbands = [
    {"name": "SB0", "fl": 500,  "fh": 1000, "M": 16, "N": 31},   # SB0 可用31阶（低频宽波束）
    {"name": "SB1", "fl": 1000, "fh": 2000, "M": 8,  "N": 63},
    {"name": "SB2", "fl": 2000, "fh": 4000, "M": 4,  "N": 63},
    {"name": "SB3", "fl": 4000, "fh": 8000, "M": 2,  "N": 63},
]

FD_ORDER = 8   # 分数延迟FIR阶数 (sinc-windowed Kaiser)

print("\n【子带划分与 d/λ 分析】")
print(f"{'子带':<6} {'频率范围':>14} {'M':>4} {'子带率':>8} {'N_proto':>8} {'d/λ_low':>8} {'d/λ_high':>9} {'栅瓣?':>6}")
print("-" * 70)
for sb in subbands:
    fl, fh, M, N = sb["fl"], sb["fh"], sb["M"], sb["N"]
    fs_sub = FS / M
    dl_lo  = D * fl / C
    dl_hi  = D * fh / C
    grating = "无" if dl_hi < 1.0 else f"{np.degrees(np.arcsin(1-C/(fh*D))):.0f}°"
    sb["fs_sub"] = fs_sub
    print(f"{sb['name']:<6} {fl:>5}-{fh:<5}Hz  {M:>3}x {fs_sub:>7.0f}Hz {N:>8}  {dl_lo:>8.3f}  {dl_hi:>9.3f} {grating:>6}")

print("""
d/λ 结论（d=55mm[L1拆机实测]，DEC-S3-GEOM-01）:
  500Hz–5kHz: d/λ<1.0 → 无栅瓣，安全。
  6.2–8kHz:   d/λ>1.0（8kHz 时 d/λ=1.282）→ broadside 出现栅瓣[L1/几何]。
              半波长判据 d=λ/2 → 3118Hz；严格判据(broadside,d=λ) → 6236Hz；
              6.24kHz 起栅瓣峰达 0dB（与主瓣等高），带外泄漏 78–89%[L2 仿真]。
  应对: 强指向规格上限由 8kHz 降级为 6kHz(对内)/5kHz(对外保守)（方向1，CTO 采纳）。
子带划分策略:
  SB0(500-1kHz):  d/λ<0.16，自然宽波束，无指向性需求，抽取16x降低算力
  SB1(1k-2kHz):   声学≥1kHz强指向 关键子带，8阶抽取后6kHz速率下精确处理
  SB2(2k-4kHz):   d/λ=0.32-0.64，良好指向，4x抽取，仍 <1.0 无栅瓣
  SB3(4k-8kHz):   d/λ=0.64-1.28，上半段(6.2-8k)有栅瓣，落在降级规格之外，2x抽取
抽取后每子带 FIR 在低速率下运行 → 与全速率相比算力下降 M 倍。
（再次提醒：上述 d/λ 与栅瓣变化【不影响 MMAC/s 算力】，算力与 d 无关。）
""")

# ============================================================
# 算力预算表
# ============================================================
print("【完整算力预算表 (MMAC/s)】")
print(f"\n{'组件':<34} {'子带率':>8} {'通道':>6} {'MMAC/s':>10}")
print("-" * 63)

total = 0.0

# 1. 多相分析滤波器（每通道）
for sb in subbands:
    M, N, fs_sub = sb["M"], sb["N"], sb["fs_sub"]
    # 多相实现：(N+1)个系数在 fs/M 速率下运行，每通道
    macs = (N + 1) * fs_sub * N_CH / 1e6
    sb["analysis_mmac"] = macs
    label = f"多相分析FIR({sb['name']} {sb['fl']//1000}k-{sb['fh']//1000}kHz, N={N})"
    print(f"{label:<34} {fs_sub:>7.0f}Hz {N_CH:>5}ch {macs:>10.3f}")
    total += macs

print()

# 2. 分数延迟FIR（每子带，每通道，在子带速率下）
for sb in subbands:
    macs = FD_ORDER * sb["fs_sub"] * N_CH / 1e6
    sb["fd_mmac"] = macs
    label = f"分数延迟FIR({sb['name']}, N={FD_ORDER})"
    print(f"{label:<34} {sb['fs_sub']:>7.0f}Hz {N_CH:>5}ch {macs:>10.3f}")
    total += macs

print()

# 3. 加权求和（每子带，N_CH MAC/output）
for sb in subbands:
    macs = N_CH * sb["fs_sub"] / 1e6
    sb["sum_mmac"] = macs
    label = f"加权求和({sb['name']})"
    print(f"{label:<34} {sb['fs_sub']:>7.0f}Hz {'16→1':>6} {macs:>10.3f}")
    total += macs

print()

# 4. 多相合成滤波器（1通道输出插值）
for sb in subbands:
    macs = (sb["N"] + 1) * sb["fs_sub"] / 1e6  # 1通道
    sb["synth_mmac"] = macs
    label = f"多相合成FIR({sb['name']})"
    print(f"{label:<34} {sb['fs_sub']:>7.0f}Hz {'1ch':>6} {macs:>10.3f}")
    total += macs

# 5. 系统开销
overhead = total * 0.08
print(f"\n{'系统开销 (DMA/中断/控制 8%)':<34} {'':>8} {'':>6} {overhead:>10.3f}")
total += overhead

print("-" * 63)
print(f"{'总计 MMAC/s':<34} {'':>8} {'':>6} {total:>10.2f}")

available = 1500.0
cto_budget = 100.0
core_bf_mmac = sum(sb["fd_mmac"] + sb["sum_mmac"] for sb in subbands)

print(f"\nADSP-21569 保守口径:      {available:.0f} MMAC/s (实际峰值 ~2000 MMAC/s)")
print(f"波束形成系统总算力:        {total:.1f} MMAC/s")
print(f"  其中核心波束形成（分数延迟+求和）: {core_bf_mmac:.2f} MMAC/s")
print(f"  其中分析+合成滤波器:              {total - overhead - core_bf_mmac:.2f} MMAC/s")
print(f"算力占比:                  {total/available*100:.1f}%")
print(f"裕量倍数:                  {available/total:.0f}×")
print(f"剩余算力（可用于后处理）:  {available - total:.0f} MMAC/s")
print(f"\nCTO目标 <{cto_budget} MMAC/s 验证:")
if core_bf_mmac <= cto_budget:
    print(f"  核心波束形成 {core_bf_mmac:.2f} MMAC/s — 满足（裕量 {cto_budget/core_bf_mmac:.0f}×）")
if total <= cto_budget:
    print(f"  全系统 {total:.1f} MMAC/s — 也满足")
else:
    print(f"  全系统 {total:.1f} MMAC/s — 含滤波器组开销，仍在 21569 可用算力范围内（{available/total:.0f}×裕量）")

# ============================================================
# SRAM 估算（定点 Q15/Q31 实现）
# ============================================================
print("\n\n【SRAM 占用估算（Q15系数 / Q31状态，bytes）】")
COEF_B  = 2   # Q15 系数 2字节
STATE_B = 4   # Q31 状态 4字节

mem_items = []

# 分析FIR系数（共享，1套）+ 状态（每通道独立）
for sb in subbands:
    N = sb["N"]
    coef  = (N + 1) * COEF_B              # 共享1套系数
    state = (N + 1) * STATE_B * N_CH      # 每通道独立状态
    mem_items.append((f"多相分析FIR({sb['name']})", coef, state))

# 分数延迟 FIR（4子带，每通道独立系数+状态）
fd_coef  = FD_ORDER * COEF_B * 4 * N_CH   # 每通道每子带独立（不同延迟量）
fd_state = FD_ORDER * STATE_B * 4 * N_CH  # 状态
mem_items.append(("分数延迟FIR(4子带×16ch)", fd_coef, fd_state))

# 整数延迟环形缓冲区（Q31，最大44采样 + 边界）
theta_max = 45
tau_max_samp = int((N_CH - 1) * D * np.sin(np.radians(theta_max)) / C * FS) + FD_ORDER + 2
delay_buf = tau_max_samp * STATE_B * N_CH
mem_items.append(("整数延迟环形缓冲区", 0, delay_buf))

# DMA Ping-Pong (I/O)
dma_in  = FRAME * N_CH * STATE_B * 2   # 16ch输入 ping+pong
dma_out = FRAME * 1   * STATE_B * 2    # 1ch输出 ping+pong
mem_items.append(("I/O DMA Ping-Pong缓冲区", 0, dma_in + dma_out))

# 波束权重（每子带16通道，复数Q15）
weights = 4 * N_CH * COEF_B * 2  # complex
mem_items.append(("波束权重(4子带×16ch×complex)", weights, 0))

# 合成FIR（与分析共享系数；状态1通道）
for sb in subbands:
    N = sb["N"]
    state = (N + 1) * STATE_B * 1
    mem_items.append((f"合成FIR状态({sb['name']})", 0, state))

print(f"\n{'组件':<34} {'系数(B)':>10} {'状态/缓冲(B)':>14} {'小计(B)':>10}")
print("-" * 72)
total_coef  = 0
total_state = 0
for name, c, s in mem_items:
    total_coef  += c
    total_state += s
    print(f"{name:<34} {c:>10,} {s:>14,} {c+s:>10,}")

total_mem = total_coef + total_state
print("-" * 72)
print(f"{'合计':<34} {total_coef:>10,} {total_state:>14,} {total_mem:>10,}")
print(f"\n总计: {total_mem:,} 字节 = {total_mem/1024:.1f} KB")

l1_kb = 640
l2_kb = 1024
print(f"\nADSP-21569 SRAM 规格:")
print(f"  L1 SRAM: {l1_kb} KB  →  热点状态变量、I/O缓冲（低延迟）")
print(f"  L2 SRAM: {l2_kb} KB  →  FIR系数表、延迟缓冲（可接受延迟）")
print(f"  合计:    {l1_kb+l2_kb} KB")
print(f"  算法占用: {total_mem/1024:.1f} KB ({total_mem/1024/(l1_kb+l2_kb)*100:.1f}%)")
print(f"  剩余:    {l1_kb+l2_kb - total_mem/1024:.0f} KB → 程序代码约60KB + 系统堆栈16KB + 富余")

# ============================================================
# TDM / SPORT 参数
# ============================================================
print("\n\n【TDM / SPORT 接口参数】")
tdm_slots = 16
bit_depth  = 32
bclk = FS * tdm_slots * bit_depth
pp_bytes = FRAME * tdm_slots * (bit_depth // 8)
print(f"""
FSYNC (fs):        {FS} Hz = {FS/1000:.0f} kHz
TDM slots:         {tdm_slots}  (对应 16 阵元)
位深 (bit/slot):   {bit_depth} bit
BCLK:              {bclk:,} Hz = {bclk/1e6:.3f} MHz
帧大小:            {FRAME} samples = {FRAME/FS*1000:.3f} ms
DMA中断频率:       {FS/FRAME:.0f} Hz
Ping-pong单缓冲:   {FRAME} × {tdm_slots} × {bit_depth//8}B = {pp_bytes:,} B = {pp_bytes/1024:.1f} KB
双缓冲合计:        {pp_bytes*2/1024:.1f} KB
系统延迟估算:      < {FRAME/FS*1000*2 + 1/FS*1000:.2f} ms（双缓冲）
""")

print("核算完毕。")
