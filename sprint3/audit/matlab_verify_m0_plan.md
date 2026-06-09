# TASK-MATLAB-M0 — MATLAB 三轨独立验证 · 预探段（侦察 + 规划）

> 作者：声学仿真专家 teammate（agent-acoustic-sim-v1）
> 日期：2026-05-29　|　几何锁定：SC-S3-GEOM-01 = **N=16 / d=55mm / L=825mm / Dolph-Cheby-20dB / broadside / isotropic**
> 本段只做工具箱探针 + 现有脚本侦察 + M1/M2/M3 规划，**不跑大计算**（MC/扫描/超指向留 M1-M3）。
> 三轨标记：**[L2-numpy]**（我方 scipy 第三轨基准）/ **[L2-MATLAB-CTO]**（CTO 第二轨 p01/p02/sim 现值）/ **[L2-MATLAB-agent]**（本任务 M1-M3 待算的本 agent 第一轨）。
> 禁用撤回值：d=30 / 14.9 / 19.1 / 19.2 / 16.0（F-AC-01 / PF-8）——下表对竞品锚点仅作"现状记录"，不作物理基线。

---

## 1. 工具箱清单与关键依赖判定

MATLAB **R2026a (26.1.0.3251617) Update 2**，Linux glnxa64，许可证 40821746。

| 工具箱 | 版本 | M0 判定 |
|--------|------|---------|
| MATLAB（base） | 26.1 (R2026a) | ✔ |
| **Signal Processing Toolbox** | 26.1 | ✔ **关键依赖满足**——`chebwin` 可用（Dolph-Cheby-20 加权，SLL/WNG/DI/MC/超指向全部依赖） |
| **Phased Array System Toolbox** | 26.1 | ✔ 可用（`phased.ULA` / `beamwidth` / `pattern` / `directivity`），M2 DI 可用官方 `directivity()` 而非自写 |
| DSP System Toolbox | 26.1 | ✔（备用，非本任务关键路径） |
| Audio Toolbox | 26.1 | ✔（备用） |

**关键依赖结论**：`chebwin` 在（Signal Processing Toolbox），Phased Array 在。
**`🚨E-MATLAB-2` 不触发**——无工具箱缺失，无需买/换工具，三条轨全部可执行。

---

## 2. 三轨现有值基线表（M1/M2/M3 对照基准）

几何统一 N=16/d=55/Dolph-20/broadside/iso（除非另注）。CTO-MATLAB 值取自 `~/matlab-agent/` 三个 CSV；numpy 值取自 `sprint3/acoustic/sweep_d55_results.csv` 与 `sprint2/acoustic/diff_1khz_optimization.py`。

### 2.1 BW（-6dB 全角，主指标）— 已可三轨对照

| 频率 | [L2-numpy] (iso/Dolph20) | [L2-MATLAB-CTO] BW_iso | [L2-MATLAB-CTO] BW_cos | 解析 0.886λ/Nd |
|------|--------------------------|------------------------|------------------------|----------------|
| 250Hz | 180.0 | 360 (绕回) | 81.9 | 79.1 |
| 500Hz | 60.703 | 60.72 | 53.06 | 39.57 |
| **1000Hz** | **29.269** | **29.28** | 28.38 | 19.79 |
| 2000Hz | 14.515 | 14.52 | 14.42 | 9.89 |
| 4000Hz | 7.243 | 7.26 | 7.24 | 4.95 |

> 出处：[L2-numpy] `sprint3/acoustic/sweep_d55_results.csv`（16-indep/dolph20 行）；[L2-MATLAB-CTO] `~/matlab-agent/sim_d55_matlab_results.csv` + `sim_d55_beamwidth.m`。
> **观察**：iso 两轨 500–4000Hz 偏差 <0.1%，**numpy 与 CTO-MATLAB 已高度互证**。250Hz CTO=360°（broadside 绕回伪值，与 numpy 封顶 180° 口径差异，M1 须统一截断口径）。

### 2.2 SLL（峰值旁瓣，dB）— 已可两轨对照（缺 MATLAB 第一轨独立值）

| 频率 | [L2-numpy] SLL (Dolph20) | [L2-MATLAB-CTO] | 备注 |
|------|--------------------------|-----------------|------|
| 500Hz | -23.1 | (p01 MC: SLL_p50 区间) | 低频主瓣未成形，SLL 偏离 -20 设计值 |
| 1000Hz | -20.0 | p01 S1 p50 = -18.70 / worst -16.09 | numpy 标称 vs CTO MC 分布 |
| 2000Hz | -20.0 | p01 S1 p50 = -18.27 | |
| 4000Hz | -20.0 | p01 S1 p50 = -17.98 | |

> 出处：[L2-numpy] `sweep_d55_results.csv`；[L2-MATLAB-CTO] `~/matlab-agent/p01_tolerance_mc_results.csv`（S1_16indep_iso，MC 分布，非标称）。
> **观察**：numpy 给标称无误差 SLL=-20.0；CTO p01 给的是含公差 MC 的 p50/worst，二者口径不同（标称 vs 统计）。M1 须补 MATLAB 无误差标称 SLL 以与 numpy -20.0 直接对齐。

### 2.3 WNG（白噪声增益，dB）— 仅 MATLAB 有 d=55 值；numpy 仅 d=30 差分轨

| 工况 | [L2-numpy] | [L2-MATLAB-CTO] | 备注 |
|------|-----------|-----------------|------|
| Dolph-20 标称 (1kHz) | （未在 d=55 直接算；理论 ≈10log10(N)=12.04dB 上限） | p01 MC: WNG_p50 ≈ 11.84dB（各频点稳定）| numpy 侧 WNG 只在 `diff_1khz_optimization.py` 算了**差分超指向**轨，非 Dolph 标称 |
| 超指向 ε 扫描 (1kHz) | diff 轨 1-3 阶 WNG（d=30，**撤回几何**）| p02: ε=0.3→10.94 / 0.01→4.57 / 0.003→-2.08dB（d=55）| 见 2.4 |

> 出处：[L2-MATLAB-CTO] `p01_tolerance_mc_results.csv`（WNG_p50≈11.84）+ `p02_superdir_d55_results.csv`；[L2-numpy] `sprint2/acoustic/diff_1khz_optimization.py`（差分轨，d=30）。
> **缺口**：numpy 侧**无 d=55 Dolph-20 标称 WNG**。M1/M2 须补 numpy d=55 Dolph WNG 以三轨对齐（CTO 已有 11.84dB）。

### 2.4 超指向（MVDR 对角加载 ε 扫描，1kHz，d=55）— 仅 MATLAB-CTO 有 d=55

| ε | [L2-MATLAB-CTO] BW1k° | WNG_dB | gain_tol_dB | phase_tol_deg |
|---|----------------------|--------|-------------|---------------|
| 0.300 | 24.96 | 10.94 | 5.79 | 54.36 |
| 0.100 | 24.02 | 9.51 | 5.79 | 54.36 |
| 0.030 | 23.33 | 7.82 | 5.79 | 54.36 |
| 0.010 | 22.87 | 4.57 | 5.79 | 54.36 |
| 0.003 | 22.19 | -2.08 | 3.85 | 31.92 |

> 出处：[L2-MATLAB-CTO] `~/matlab-agent/p02_superdir_d55_results.csv` + `p02_superdirective_d55.m`（MVDR Γ_ij=sinc(kd|i-j|)，对角加载）。
> **缺口**：[L2-numpy] 侧超指向只有 `diff_1khz_optimization.py` 的**差分波束**实现且为 **d=30 撤回几何**，与 CTO 的 MVDR/d=55 既不同方法也不同几何。M3 须用 numpy 在 d=55 重写 MVDR ε 扫描以建对照。CTO 自验 d=30/ε=0.01=35.39°/+2.01dB 与旧报告吻合，d=55 同 ε=0.01=22.87° 收窄属合理。

### 2.5 公差蒙特卡洛（MC）— 仅 MATLAB-CTO 有完整 d=55

| 场景 (1kHz) | [L2-MATLAB-CTO] SLL_p50 | BW_p50 | BW_p95 | BW_fail% | WNG_p50 |
|-------------|-------------------------|--------|--------|----------|---------|
| S1_16indep_iso | -18.70 | 29.27 | 29.77 | 0.97 | 11.84 |
| S3_8pair_iso | -18.70 | 29.29 | 30.03 | 5.33 | 11.84 |
| S2_16indep_cos | -21.00 | 28.67 | 29.14 | 0.00 | 11.84 |
| S4_8pair_cos | -21.18 | 28.66 | 29.36 | 0.03 | 11.84 |

> 出处：[L2-MATLAB-CTO] `~/matlab-agent/p01_tolerance_mc_results.csv`（4 场景 × 4 频点；注入幅度±/相位±/位置±，p5/p50/p95/worst + fail%）。
> **关键观察**：8-pair 拓扑 BW_fail% (5.33%) 远高于 16-indep (0.97%)，1kHz 压线达标（30°）对公差敏感——M1 MC 须复核此风险点。
> **缺口**：[L2-numpy] 侧**无公差 MC**（numpy 只算无误差标称）。M1 须用 numpy 实现同口径 MC（同种子/同注入幅度）对照 CTO p50/fail%。

### 2.6 DI（指向性指数）— 三轨皆无 d=55 值（重大缺口）

| 来源 | DI@d=55 状态 |
|------|-------------|
| [L2-numpy] | **无**——`sprint2/acoustic/array_sweep.py` 有 `directivity_index()` 但只扫 d∈{25,28,30,32,35,40}mm（全为 d=30 撤回区），`sweep_results.csv` 无 d=55 行；`sweep_d55.py` 注释写"BW/SLL/DI"但**实际未实现 DI** |
| [L2-MATLAB-CTO] | **无**——三个 CSV 均无 DI 列 |
| [L2-MATLAB-agent] | **无**（待 M2 算） |

> **结论**：DI 是三轨全空的指标，**无任何 d=55 基线**。M2 须新建：numpy 用 `array_sweep.py:directivity_index()` 移植到 d=55 + MATLAB 用官方 `directivity(phased.ULA,...)`，二者互证。这是 M2 的核心新增工作，非"复核"而是"首算"。

---

## 3. M1 / M2 / M3 执行规划

### M1 — BW + SLL + 公差MC 三轨闭合
- **算什么**：① d=55 Dolph-20 标称 BW(-6dB全角)/SLL 全频点（与 2.1/2.2 对齐，统一 250Hz 截断口径）；② 公差 MC（4 场景，幅度±1dB/相位±5°/位置±0.5mm，rng 固定）复核 CTO p01 的 p50/p95/fail%，重点核 8-pair@1kHz fail=5.33% 风险。
- **MATLAB 实现**：`chebwin(16,20)` + `phased.ULA` + `beamwidth(...,'dBDown',6,'PropagationSpeed',343)`；MC 用 `Taper` 扰动注入 + `rng` 固定。
- **对照**：BW↔[L2-numpy]`sweep_d55_results.csv` & [L2-MATLAB-CTO]`sim_d55_matlab_results.csv`；MC↔[L2-MATLAB-CTO]`p01_tolerance_mc_results.csv`（须补 numpy MC 第三轨）。

### M2 — DI + WNG 标称 三轨首建
- **算什么**：① DI（线阵 2D 近似，IEC 口径，全频点）——三轨全空，**首算非复核**；② Dolph-20 标称 WNG（numpy 侧补 d=55，对齐 CTO MC 的 11.84dB）。
- **MATLAB 实现**：DI 优先用官方 `directivity(phased.ULA,f,[0;0],'PropagationSpeed',343)`（避免自写积分误差），与 numpy `directivity_index()` 移植版互证；WNG = |wᴴa|²/(wᴴw)。
- **对照**：DI↔numpy 移植`array_sweep.py:directivity_index()`到 d=55（[L2-MATLAB-CTO] 无值，本段建双轨）；WNG↔[L2-MATLAB-CTO] p01 WNG_p50=11.84。

### M3 — 超指向 MVDR ε 扫描 三轨闭合
- **算什么**：1kHz d=55 MVDR 对角加载 ε∈{0.3,0.1,0.03,0.01,0.003} 的 BW/WNG/容差，复核 CTO p02；并以 numpy 在 d=55 重写同方法 MVDR（替换现有 d=30 差分轨）。
- **MATLAB 实现**：Γ_ij=sinc(kd|i-j|)，w=(Γ+εI)⁻¹a/[aᴴ(Γ+εI)⁻¹a]，`beamwidth` 取 -6dB 全角；本 agent 独立重跑而非读 CTO 脚本输出。
- **对照**：↔[L2-MATLAB-CTO]`p02_superdir_d55_results.csv`（须补 numpy d=55 MVDR 第三轨）；CTO d=30/ε=0.01=35.39° 自验锚点可顺带交叉。

---

## 4. 强制规则自检（skill.md N.2）— 适用 M1-M3 全部脚本
- [N.2.1] 所有阵列计算显式 `PropagationSpeed=343`（CTO 现有脚本已满足，本 agent 脚本须 grep 验证）。
- [N.2.2] 报告 d/λ 与栅瓣临界 f_grating=c/d=6236Hz；4kHz 工作上限安全（栅瓣留 M0 既有 pf8 结论，不重算）。
- [N.2.3] BW 统一 -6dB 全角（已与 numpy/CTO 同口径）。
- [N.2.4] 阵元模型：基准 isotropic（SC-S3-GEOM-01 锁定）；cos 仅作 CTO 已有对标参考，不进基线。
- [N.7] 与竞品实测冲突时实测为权威——本任务为三轨仿真自洽核验，不裁决实测。
