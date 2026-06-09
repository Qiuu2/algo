"""
TASK-MATLAB-M2 — 轨3 [L2-numpy] 公差蒙特卡洛 N=3000（d=55 基线）
几何锁定 SC-S3-GEOM-01: N=16 / d=55mm / L=825mm / Dolph-Cheby-20dB / broadside / isotropic

三轨对照之第三轨。复现 CTO p01_tolerance_mc_full.m 的注入口径（幅度±1dB/相位±5°/位置±0.5mm，
均匀分布半宽；8-pair 通道级+单元级叠加，单元级权0.5；SLL/BW/WNG 同定义），
但用【独立随机种子】 rng=20260530（≠ CTO 的 20260528、≠ MATLAB-agent 的 20260529），
以验证三轨在不同种子下统计收敛一致（分布量，非 bit 级）。

诚实边界声明（与 CTO 脚本同）：
  - cosine 阵元仅作障板/单元指向【近似代理】，非真实有限障板边缘衍射（需 BEM/FEM/COMSOL）。
  - 8-pair 串联互耦用幅相扰动增量【粗近似】，非真实互阻抗矩阵求解。
  - 措辞红线：本脚本为【仿真】MC，非实测；阵因子层 MC，cosine 为乐观下界。
作者：声学仿真专家 teammate (agent-acoustic-sim-v1)  日期：2026-05-29
"""
import numpy as np
from scipy.signal.windows import chebwin
from scipy.signal import find_peaks
import csv

# ---- 参数区（与 CTO p01 对齐）----
C = 343.0
N = 16
D = 0.055
FSET = [500, 1000, 2000, 4000]
SLL_DESIGN = 20      # Dolph -20dB
DBDOWN = 6           # -6dB 全角
NMC = 3000
TOL_AMP_DB = 1.0     # ±1 dB
TOL_PHA_DEG = 5.0    # ±5°
TOL_POS_MM = 0.5     # ±0.5 mm
SLL_FAIL_THRESH = -16  # SLL > -16dB 视为超标
SEED = 20260530      # 轨3 独立种子（≠ CTO 20260528, ≠ MATLAB-agent 20260529）

ANG = np.arange(-90, 90 + 0.02, 0.02)  # 方位面网格，与 CTO ang=-90:0.02:90 一致

# ---- 加权 ----
w_full = chebwin(N, SLL_DESIGN)  # 注意：CTO MATLAB 用 chebwin(N,20) 未归一化 max=1
w_full = np.asarray(w_full, dtype=float)
# CTO 脚本 w_full 未做 /max 归一化；BW/SLL 与归一化无关，WNG 比值也无关 → 保持与 CTO 一致不归一化

def af_pattern_db(w_act, dpos, freq, use_cos):
    """阵因子方向图(dB)，含实际复权重 + 位置扰动 + cosine 阵元近似。"""
    k = 2 * np.pi * freq / C
    pos = np.arange(N) * D + dpos          # 实际阵元位置(含位置扰动)
    st = np.sin(np.radians(ANG))           # (A,)
    phase = k * np.outer(pos, st)          # (N, A)
    AF = (w_act[:, None] * np.exp(1j * phase)).sum(axis=0)  # (A,)
    mag = np.abs(AF)
    if use_cos:
        ef = np.maximum(np.cos(np.radians(ANG)), 0.0)
        mag = mag * ef
    P = 20 * np.log10(mag / mag.max() + 1e-12)
    return P

def bw_from_pat(P):
    """-6dB 全角，主瓣在 broadside(0°)，从峰向两侧找 -6dB 交点线性插值。"""
    ipk = int(np.argmax(P))
    target = -DBDOWN
    iR = ipk
    while iR < len(P) - 1 and P[iR] > target:
        iR += 1
    iL = ipk
    while iL > 0 and P[iL] > target:
        iL -= 1
    if iR > ipk and iL < ipk:
        # 右交点
        aR = np.interp(target, [P[iR], P[iR - 1]], [ANG[iR], ANG[iR - 1]]) \
            if P[iR] != P[iR - 1] else ANG[iR]
        # 左交点（P 在 iL..iL+1 递增穿过 target）
        aL = np.interp(target, [P[iL], P[iL + 1]], [ANG[iL], ANG[iL + 1]]) \
            if P[iL] != P[iL + 1] else ANG[iL]
        return float(aR - aL)
    return np.nan

def sll_from_pat(P):
    """峰值旁瓣级：findpeaks 取第2高峰（同 CTO MinPeakHeight=-55, prominence=0.5）。"""
    pk_idx, props = find_peaks(P, height=-55, prominence=0.5)
    if len(pk_idx) == 0:
        return -60.0
    heights = np.sort(P[pk_idx])[::-1]
    if len(heights) >= 2:
        return float(heights[1])
    return -60.0

def wng_db(w_act):
    """WNG = |w^H a|^2 / (w^H w)，a=理想broadside全1（与 CTO wng_db 同口径）。"""
    a = np.ones(N)
    num = np.abs(np.vdot(w_act, a)) ** 2
    den = np.vdot(w_act, w_act).real
    return float(10 * np.log10(num / den + 1e-12))

rng = np.random.default_rng(SEED)

scenarios = ['S1_16indep_iso', 'S2_16indep_cos', 'S3_8pair_iso', 'S4_8pair_cos']
out_rows = []

print(f"========== M2 numpy 公差MC (d=55,N=16,Dolph-20) seed={SEED} Nmc={NMC} ==========")
print(f"容差 ±{TOL_AMP_DB}dB/±{TOL_PHA_DEG}°/±{TOL_POS_MM}mm\n")

for sc in scenarios:
    use_pair = '8pair' in sc
    use_cos = 'cos' in sc
    w_des = w_full
    for f in FSET:
        bw_s = np.empty(NMC); sll_s = np.empty(NMC); wng_s = np.empty(NMC)
        for m in range(NMC):
            da_unit = (rng.random(N) * 2 - 1) * TOL_AMP_DB
            dp_unit = (rng.random(N) * 2 - 1) * TOL_PHA_DEG
            dpos = (rng.random(N) * 2 - 1) * TOL_POS_MM * 1e-3
            if use_pair:
                da_ch = (rng.random(8) * 2 - 1) * TOL_AMP_DB
                dp_ch = (rng.random(8) * 2 - 1) * TOL_PHA_DEG
                da_ch16 = np.concatenate([da_ch, da_ch[::-1]])
                dp_ch16 = np.concatenate([dp_ch, dp_ch[::-1]])
                da = da_ch16 + da_unit * 0.5
                dp = dp_ch16 + dp_unit * 0.5
            else:
                da = da_unit; dp = dp_unit
            amp_err = 10 ** (da / 20)
            w_act = w_des * amp_err * np.exp(1j * np.radians(dp))
            P = af_pattern_db(w_act, dpos, f, use_cos)
            P = P - P.max()
            bw_s[m] = bw_from_pat(P)
            sll_s[m] = sll_from_pat(P)
            wng_s[m] = wng_db(w_act)
        bw_valid = bw_s[~np.isnan(bw_s)]
        sll_p = np.percentile(sll_s, [5, 50, 95])
        bw_p = np.percentile(bw_valid, [5, 50, 95])
        wng_p = np.percentile(wng_s, [5, 50, 95])
        p_sll_fail = np.mean(sll_s > SLL_FAIL_THRESH) * 100
        p_bw_fail = np.mean(bw_valid > 30) * 100
        row = dict(scenario=sc, freq_hz=f,
                   SLL_p5=sll_p[0], SLL_p50=sll_p[1], SLL_p95=sll_p[2], SLL_worst=sll_s.max(),
                   SLL_fail_pct=p_sll_fail,
                   WNG_p5=wng_p[0], WNG_p50=wng_p[1], WNG_p95=wng_p[2], WNG_worst=wng_s.min(),
                   BW_p50=bw_p[1], BW_p95=bw_p[2], BW_max=bw_valid.max(), BW_fail_pct=p_bw_fail)
        out_rows.append(row)
        print(f"{sc:16s} {f:5d}Hz | SLL p50={sll_p[1]:6.2f} p95={sll_p[2]:6.2f} | "
              f"BW p50={bw_p[1]:6.2f} p95={bw_p[2]:6.2f} max={bw_valid.max():6.2f} "
              f"P(BW>30)={p_bw_fail:5.2f}% | WNG p50={wng_p[1]:5.2f}")

out = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint3/audit/m2_numpy_mc_results.csv"
cols = ["scenario", "freq_hz", "SLL_p5", "SLL_p50", "SLL_p95", "SLL_worst", "SLL_fail_pct",
        "WNG_p5", "WNG_p50", "WNG_p95", "WNG_worst", "BW_p50", "BW_p95", "BW_max", "BW_fail_pct"]
with open(out, "w", newline="") as fp:
    wr = csv.writer(fp)
    wr.writerow(cols)
    for r in out_rows:
        wr.writerow([r["scenario"], r["freq_hz"]] + [round(r[c], 2) for c in cols[2:]])
print(f"\n[CSV] {out}")
print("========== M2 numpy MC 完成 ==========")
