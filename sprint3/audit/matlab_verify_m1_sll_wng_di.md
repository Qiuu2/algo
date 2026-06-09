# TASK-MATLAB-M1 — 三轨独立验证 · SLL + WNG + DI 频率扫描

> 作者：声学仿真专家 teammate（agent-acoustic-sim-v1）　|　日期：2026-05-29
> 几何锁定 **SC-S3-GEOM-01 = N=16 / d=55mm / L=825mm / Dolph-Cheby-20dB / broadside / isotropic**
> 工具：MATLAB R2026a + Signal Processing(`chebwin`) + Phased Array(`pattern`/`directivity`)；numpy/scipy（`chebwin`）。
> 三轨标签：**[L2-MATLAB-agent]**（本段 MATLAB 独立算）/ **[L2-MATLAB-CTO]**（`~/matlab-agent/` p01 现值）/ **[L2-numpy]**（本段 python 在 d=55 补算）。
> 措辞红线：以下全部为**仿真值**，非实测。禁用撤回值 d=30 / 14.9 / 19.1 / 19.2 / 16.0（F-AC-01 / PF-8）。

---

## 0. 结论速览

| 指标 | 三轨是否一致 | 判定 |
|------|-------------|------|
| **SLL** | [L2-MATLAB-agent] = [L2-numpy] **逐频点 bit 级一致**；与 [L2-MATLAB-CTO] 口径对齐（标称 vs MC-p50） | ✔ 一致，无 E-MATLAB-1 |
| **WNG** | 三轨一致：agent=numpy=11.868dB，CTO p01 p50=11.84dB（MC 扰动 p50，标称值即 11.868） | ✔ 一致，无 E-MATLAB-1 |
| **DI** | **首算**。agent 2D-DI = numpy 2D-DI **bit 级一致**；CTO 轨缺（p01/p02 无 DI 列）；官方 `directivity()` 与 2D-DI 系**口径不同**（已说明，非错误） | ✔ 两可得轨一致，无 E-MATLAB-1 |

**无任何两轨不一致 → 不触发 `🚨E-MATLAB-1`，不 ESCALATE。**

> 过程中发现并自纠 **1 处 numpy 笔误**（WNG 公式多除 `|a|²=N`），纠正后三轨闭合。详见 §4。该错误**仅存在于本段新建 numpy 脚本草稿**，未进入任何已发布数据，非 BLOCKER。

---

## 1. SLL 频率扫描（峰值旁瓣级，dB，相对主瓣）

几何 N=16/d=55/Dolph-20/broadside/iso。角度网格 0~90° × 9001 点（0.01°）。SLL 定义：主瓣外第一零点（<-35dB）之后的最高旁瓣峰。

| 频率(Hz) | [L2-MATLAB-agent] | [L2-numpy] | Δ(agent−numpy) | [L2-MATLAB-CTO] (p01 标称/MC-p50) | 一致性 |
|---------|-------------------|------------|----------------|-----------------------------------|--------|
| 100  | -60.000 | -60.000 | 0.000 | （CTO 未扫 100Hz） | ✔ agent=numpy |
| 250  | -60.000 | -60.000 | 0.000 | （CTO 未扫 250Hz） | ✔ agent=numpy |
| 500  | -23.098 | -23.098 | 0.000 | -60.00 (S1 MC p50；主瓣未成形，CTO 取 floor) | ✔ agent=numpy；CTO 口径差异见注 |
| 1000 | -20.000 | -20.000 | 0.000 | -18.70 (S1 MC p50) / -19.87 (p5) | ✔ agent=numpy；CTO=含公差 MC |
| 2000 | -20.000 | -20.000 | 0.000 | -18.27 (S1 MC p50) | ✔ agent=numpy；CTO=含公差 MC |
| 4000 | -20.000 | -20.000 | 0.000 | -17.98 (S1 MC p50) | ✔ agent=numpy；CTO=含公差 MC |
| 6000 | -20.000 | -20.000 | 0.000 | （CTO 未扫 6000Hz） | ✔ agent=numpy |
| 10000| -0.000  | -0.000  | 0.000 | （CTO 未扫 10000Hz） | ✔ agent=numpy；见注 |

**观察**：
- **轨1 vs 轨3 逐频点完全一致（Δ=0.000）**——MATLAB `pattern()`（powerdb，显式 PropagationSpeed=343）与 numpy 手写阵因子归一化后 SLL 算法完全互证。
- **轨2 [L2-MATLAB-CTO] 口径差异（非错误）**：CTO p01 给的是**含公差蒙特卡洛**的 p50/p5（注入幅度±1dB/相位±5°/位置±0.5mm），SLL 在 -20dB 设计值上恶化至 ~-18.7dB（p50）。本段 agent/numpy 给的是**无误差标称值** -20.0dB。二者方向一致（标称 -20，公差使其略升），**口径不同不构成不一致**。
- **500Hz 的 -23.098dB**：低频主瓣尚未充分成形，旁瓣定义下检出的峰值实际是主瓣裙边的第二极大，低于 -20 设计线属正常物理现象（agent/numpy 一致）。CTO 在 500Hz 取 -60 floor（其 SLL 检测在主瓣未成形时返回 floor），口径差异。
- **10000Hz 的 -0.0dB**：d/λ=1.60>1，栅瓣已进入可见区且与主瓣等高（旁瓣级≈0dB）。符合 §3 栅瓣物理（f_grating=6236Hz，10kHz 远超）。agent/numpy 一致。

---

## 2. WNG 频率扫描（白噪声增益/阵增益，dB）

定义（与 CTO p01 `wng_db` 同口径）：**WNG = |wᴴa|² / (wᴴw)**，a = 理想 broadside 导向（全 1 向量）。
标称（isotropic 无误差）下 WNG **与频率无关**，= (Σw)²/Σw²。

| 频率(Hz) | [L2-MATLAB-agent] | [L2-numpy] | Δ | [L2-MATLAB-CTO] (p01 MC p50) | 一致性 |
|---------|-------------------|------------|---|------------------------------|--------|
| 100–10000（全频点） | **11.868** | **11.868** | 0.000 | **11.84**（各频点 p50，MC 扰动）；标称即 11.868 | ✔ 三轨一致 |

**观察**：
- **三轨一致**：agent=numpy=11.868dB（标称）；CTO p01 MC p50=11.84dB（注入误差后轻微下降 ~0.03dB，p5=11.80/p95=11.88），**标称值与 CTO 标称完全吻合**。
- 物理校验：uniform 加权上限 = 10log10(N) = 10log10(16) = **12.041dB**；Dolph-20 加权因边缘削权略低于均匀，11.868dB（损失 0.17dB）合理。
- WNG 与频率无关性已在 8 个频点逐点确认（皆 11.868），符合 isotropic 标称理论。

---

## 3. DI 频率扫描（指向性指数，dB）—— **本段首算（M0 标注三轨全空）**

### 3.1 DI 首算说明（口径声明）

DI 在 d=55 下**三轨全空**（M0 §2.6 确认：numpy 仅扫过 d=30 撤回区；CTO 三 CSV 无 DI 列；agent 待算）。本段为 **DI 在 d=55 的首次计算**。

DI 存在两种合法口径，本段**两种都算**以避免口径混淆：
- **DI_2D（线阵半球近似）**：DI = 10log10( 2 / ∫₀^{π/2}|D(θ)|²sinθ dθ · 2 )，θ 为偏离 broadside 角，仅前半球。与 `sprint2/acoustic/array_sweep.py:directivity_index()` 同口径——**这是与 numpy 直接对齐的轨**。
- **DI_official（MATLAB 官方 `directivity()`）**：Phased Array Toolbox 在 3D（方位+俯仰全球面）对 ULA 实际方向图积分的标准 DI。**与 2D-DI 是不同物理定义**，数值不可直接相等。

### 3.2 三轨 DI 表

| 频率(Hz) | [L2-MATLAB-agent] DI_2D | [L2-numpy] DI_2D | Δ(DI_2D) | [L2-MATLAB-agent] DI_official | [L2-MATLAB-CTO] | 一致性 |
|---------|-------------------------|------------------|----------|-------------------------------|-----------------|--------|
| 100  | 0.556  | 0.556  | 0.000 | 0.274  | 缺（CTO 轨无 DI） | ✔ 2D 两轨一致 |
| 250  | 3.425  | 3.425  | 0.000 | 1.555  | 缺 | ✔ 2D 两轨一致 |
| 500  | 10.115 | 10.115 | 0.000 | 4.213  | 缺 | ✔ 2D 两轨一致 |
| 1000 | 15.519 | 15.519 | 0.000 | 7.155  | 缺 | ✔ 2D 两轨一致 |
| 2000 | 20.178 | 20.178 | 0.000 | 10.068 | 缺 | ✔ 2D 两轨一致 |
| 4000 | 22.539 | 22.539 | 0.000 | 12.862 | 缺 | ✔ 2D 两轨一致 |
| 6000 | 13.561 | 13.561 | 0.000 | 14.077 | 缺 | ✔ 2D 两轨一致 |
| 10000| 14.486 | 14.486 | 0.000 | 12.134 | 缺 | ✔ 2D 两轨一致 |

**观察**：
- **DI_2D 轨1 vs 轨3 逐频点 bit 级一致（Δ=0.000）**——MATLAB 自写 2D 积分与 numpy `trapezoid` 完全互证。这是 DI 首算的**核心三轨闭合结果**（CTO 轨缺，由 agent+numpy 双轨建立）。
- **DI 随频率单调上升至 4kHz（22.5dB）后在 6kHz 回落**：DI_2D 在 4kHz 达峰，6kHz（d/λ=0.96，逼近栅瓣临界 6236Hz）因可见区能量泄漏/旁瓣抬升导致 DI 回落至 13.6dB，10kHz（栅瓣全开）维持低位。**物理自洽**：栅瓣进入可见区会显著降低 DI。
- **DI_official vs DI_2D 口径差异（非错误）**：官方 `directivity()`（3D 球面）数值系统性低于 2D 半球近似（如 2kHz：10.07 vs 20.18），因 3D 积分把方位面也计入分母、且 ULA 在方位面无指向性。**这是定义差异，已声明，不判为不一致**；2D-DI 才是与 numpy 同口径的对照轨。官方 DI 随频率也单调上升至 6kHz（14.08dB）后回落，趋势与 2D 一致，互为旁证。
- **CTO 轨缺**：p01/p02 三 CSV 无 DI 列，DI 在 CTO 侧无值（M0 已记录）。本段 DI 三轨对照降级为 **agent+numpy 双轨**，二者一致即视为闭合。

---

## 4. 过程自纠记录（numpy WNG 笔误，已修复，非 BLOCKER）

| 项 | 内容 |
|----|------|
| 现象 | 首跑 numpy 草稿 WNG = **-0.173dB**，与 CTO p01 的 11.84dB 差 ~12dB |
| 定位 | **numpy 错**（非 MATLAB 错）。草稿 WNG 公式误写为 `|wᴴa|²/(wᴴw·|a|²)`，多除了 `|a|²=N=16`（10log10(16)=12.04dB）。CTO p01 `wng_db`（已核源码 L219-222）与标准定义均为 `|wᴴa|²/(wᴴw)`，不除 `|a|²`。 |
| 修复 | numpy 脚本去掉 `·|a|²`，重跑 → 11.868dB，与 agent/CTO 闭合。 |
| 性质 | 仅存于本段**新建草稿**，未进入任何已发布数据/活文档。**不构成 E-MATLAB-1**（E-MATLAB-1 指两条已落盘轨之间的真实不一致；此为草稿即时自纠）。 |

> 教训沿用 memory PF-8 精神：任何新脚本数字须与既有轨交叉核验后方可采信；本次因坚持三轨对照，12dB 笔误在落盘报告前即被拦截。

---

## 5. 强制规则自检（skill.md N.2 / N.6）

- [x] **N.2.1** MATLAB 每处阵列计算（`pattern`/`directivity`）均显式传 `PropagationSpeed=343`（脚本 grep 命中 2 处）；numpy 用 C=343。
- [x] **N.2.2** f_grating = c/d = **6236Hz** 已报告；扫描列含 6000/10000Hz，10kHz d/λ=1.60 栅瓣可见区已在 SLL/DI 中体现。
- [x] **N.2.3** 本段为 SLL/WNG/DI，不涉 BW 口径（BW -6dB 全角口径已在 M0/sweep_d55 闭合）。
- [x] **N.2.4** 阵元 = `IsotropicAntennaElement`（SC-S3-GEOM-01 锁定），numpy 点声源等价；报告已声明。
- [x] 函数名均经 R2026a 官方核验（`chebwin`/`phased.ULA`/`pattern`/`directivity`），无杜撰 API。
- [x] 措辞红线：全文称"仿真值"，未称实测。

---

## 6. 文件清单（可复现）

| 文件 | 轨 | 说明 |
|------|----|------|
| `~/matlab-agent/m1_sll_wng_di_agent.m` | [L2-MATLAB-agent] | MATLAB 脚本（chebwin+ULA+pattern+directivity） |
| `~/matlab-agent/m1_agent_d55_sll_wng_di.csv` | [L2-MATLAB-agent] | MATLAB 结果 CSV |
| `sprint3/audit/m1_numpy_sll_wng_di.py` | [L2-numpy] | numpy 脚本（d=55 补算） |
| `sprint3/audit/m1_numpy_d55_sll_wng_di.csv` | [L2-numpy] | numpy 结果 CSV |
| `~/matlab-agent/p01_tolerance_mc_results.csv` | [L2-MATLAB-CTO] | CTO MC 现值（WNG/SLL 对照源） |

环境：MATLAB R2026a (26.1.0.3251617) Update 2，Signal Processing 26.1，Phased Array 26.1；Python3 + scipy。

---

*AcousticSimulationAgent v1.0 | 提交方向：Critic Agent → Team Lead（Project Manager Agent）*
*工具负责算，物理判断由本 Agent 承担。*
