# SPL_MODEL_SPEC — 系统正轴向灵敏度模型 共享规格（双轨独立实现的同一规格）

> 任务：CTO Line-2 指令 — SPL 模型重做（DEC-S3-DSP-05 解锁），用已归档 L1 T/S（KB-DRV-TEST-001）。
> 范围：**纯软件 / 不上板 / 不动冻结文件**。本文件 = **两条独立实现轨共吃的同一规格**（题面 + 约定 + 输出项 + 公式），
> 不含数值结果（结果由各轨独立算，再交 critic 比对）。
> 前置：`sprint5/spl_redo/RE_SCOPE_EVIDENCE.md`（Re 口径分级证据包，已钉死 unit/channel 层级）。
> 流程闸：POLICY v1.8 三门，本工作流 = **门-1 筛查**；**critic 门（R22）先裁定口径范围，结果才正式**。
> 输出分级：系统灵敏度 = **[L2 模型]**；输入事实 = **[L1]**（SPLo 绝对电平条件 caveat = [L2-条件未定]）。
>
> 日期：2026-06-05｜作者：dsp-algorithm teammate（lead Line-2 派发）｜状态：DRAFT，待 critic R22 裁定口径后两轨实现。

---

## 0. 治理前提（喂模型前必读，不预判对外口径）

- **CTO 硬约束 (1)**：Re 口径**已先举证**（RE_SCOPE_EVIDENCE.md）。**喂 Re = unit-level 7.600 Ω**（LEAP Revc [L1/仪器]，
  双轨核万用表单只 DC 7.4 Ω [L1 拆机]）；**15 Ω 是 channel-level（串联对 DC），严禁当单只 Re 喂单只模型**。
- **CTO 硬约束 (2) 对外口径冻结**：输出 = **[L2 模型]**；**任何文档不得改 88→82**；系统级真值 + CTO 裁定在先。
- **CTO 硬约束 (3) 不预判**：呈现「计算所得系统灵敏度 [L2]」+「unit-level 输入事实 [L1]」并列；**CTO 裁定前无对外可引口径**。
- 本规格只定**算什么、怎么算、出哪些数、带哪些 caveat**；不下「灵敏度 = X dB 对外」结论。

---

## 1. QUESTION（题面 — 两轨共答的同一问题）

求：**16 单元 / 8 通道音柱的系统正轴向远场灵敏度（dB SPL @ 1m，带明确的输入参考基准）**，
由单只 SPLo **82.161 dB**（[L1 仪器]，绝对电平条件 caveat = [L2-条件未定]）出发，
经 **阵列相干增益（N=16）** + **Dolph −20dB taper 效率损失（实际 w8 镜像到 16）** + **功率/参考基准换算** 推得。

- 单只 SPLo 形状 = [L1]；绝对电平（距离/电压/障板/平滑未标）= **[L2-条件未定]**，模型原样承袭此 caveat。
- 系统灵敏度结果 = **[L2 模型]**（建立在 [L1] 单只 SPLo + [L2 条件] + 解析阵列增益之上）。

---

## 2. CONVENTIONS（口径锁定 — 两轨必须用同一套约定）

### (a) 主输出 = 系统灵敏度 @ **TOTAL 电输入 1 W**（全通道合计）
- 参考基准：**整柱 8 通道合计电输入功率 = 1 W**，远场正轴向，自由场（free-field），相干叠加（coherent summation）。
- 这是主口径，因为它是「整柱作为一个系统、单位总输入功率」的物理灵敏度，避免 per-unit / per-channel 的基准歧义。
- **单只参考点对齐**：SPLo 82.161 dB 是「单只 @ 其 LEAP 参考输入（1W/1m 等效）」。系统 @ total 1W 与
  「单只 @ 1W」同处 **1W 总功率**基准 → 阵列增益按下文 (c)「同总功率下 N 元相干 vs 单元」的净增益 +10log10(N) 计。

### (b) 次输出 = @ **2.83 V per channel**
- 报「每通道施加 2.83 V」的系统灵敏度。**通道阻抗 ~15 Ω（channel-level，串联对 DC [L1]）**
  → per-channel 功率 = (2.83)²/15 W（< 1W，因 15Ω ≠ 8Ω 标称）。
- 必须显式写出 per-channel 功率与对 1W 的 dB 偏移，再叠加到总功率口径上（见 §4）。**2.83V/8Ω=1W 的铭牌惯例在此不成立**，
  须按实测通道 15 Ω 重算实际功率。

### (c) 阵列增益分解（显式写明）
- **理想均匀 N=16 相干**：同总功率下，N 元相干阵列正轴向**声压** = 单元的 N 倍中、按「功率分摊」口径展开：
  - 若把同一总功率 P 分给 N 个单元（每个 P/N），各元声压 ∝ √(P/N)，N 元正轴向相干相加 → 总声压 ∝ N·√(P/N) = √(N·P)。
  - 相对「单元独享同一总功率 P」（声压 ∝ √P）：增益 = 20log10(√(N·P)/√P) = 20log10(√N) = **+10·log10(N)**。
  - N=16 → **ideal_array_gain_dB = +10·log10(16) = +12.0412 dB**（vs 单元 @ 同一总功率）。
  - 备注：若误用「每元各 1W、共 N W」口径则为 +20log10(N)=+24.08 dB —— **本规格不用该口径**（基准是 TOTAL 1W，功率分摊，故 +10log10N）。
- **Dolph −20dB taper 效率（见 (d)）** 从理想 +12.0412 dB 中扣除 taper_loss（≤0）。

### (d) Dolph −20dB taper 效率（taper loss）
- 公式（aperture/array taper efficiency，定向阵标准）：
  **taper_loss_dB = 20·log10( Σwᵢ / sqrt( N · Σwᵢ² ) )**，i=1..N，N=16。
- **权重来源 = 实际 w8 镜像到 16**：读 `sprint4/dsp/fira/dolph_w8_q15.csv`（8 行，`w_float_track1_scipy` 列）。
  通道 c 驱动对 {c,15−c}，**两元共享通道权重 w8[c]** → 16 元幅度向量：
  `w16[c]=w8[c]`，`w16[15−c]=w8[c]`，c=0..7。
  即 w16 = [w8[0],w8[1],...,w8[7], w8[7],...,w8[1],w8[0]]（镜像对称）。
- taper_loss ≤ 0 dB（均匀时 =0，加权时为损失）。**它从理想 +12.0412 dB 中扣**：net = 12.0412 + taper_loss。
- **两轨核**：csv 含 `w_float_track1_scipy` 与 `w_float_track2_recurrence` 两列（应一致到 ~1e-9）→ taper 计算的输入本身已双轨。

### (e) 串联对接线（同电流，相干声学叠加 —— 证明不改 1W-total 灵敏度数学，只改阻抗记账）
- 通道 c 串联驱动 {c,15−c}：**两元同一电流 i**；通道端电压在两元间**大致各分一半**（两元 Re≈相等 ~7.4Ω each）。
- **关键证明（为何 1W-total 数学不变）**：
  - 灵敏度主口径以 **TOTAL 电输入功率** 为基准。串联对的「两元 vs 一元」之分，在 (c) 的 N=16 元相干分解里**已经计入**
    （16 元每个都是独立辐射体，相干增益 +10log10(16) 已含全部 16 个辐射元）。
  - 串联只是**电学接线方式**（决定通道阻抗 = 2×单元 ≈15Ω、决定「给定通道电压 → 通道电流/功率」），
    **不额外新增声学 +6dB**：那「同电流两元 on-axis 相干 +6dB」已是 16 元相干总和 +10log10(16) 的一部分，**不可重复计**。
  - 因此：**主口径（@ total 1W）的灵敏度数学 = SPLo + 10log10(16) + taper_loss，与接线串/并无关**；接线只影响
    §(b) 的「电压↔功率」记账（per-channel 功率用 15Ω，per-unit 用 7.6Ω）。
  - **防重复计红线**：串联「+6dB on-axis」**不得**与阵列增益 +10log10(16) 叠加；二者描述同一组辐射元的相干，取阵列增益口径为唯一计。

### (f) 1m 参考 in 远场 caveat（825mm 孔径 → @1m 对 HF 非远场，诚实声明约定）
- 远场边界（Fraunhofer）≈ 2·L²/λ，L=825mm 孔径。HF（λ 小）下 2L²/λ 远超 1m → **@1m 对高频不是远场**。
- **本规格采用约定**：报「**远场外推灵敏度（far-field extrapolated sensitivity）@1m**」——即按远场 1/r 球面扩散律
  外推到 1m 的等效灵敏度（行业标准做法），**而非声称 1m 处即满足远场**。
- 此约定**诚实标注**：@1m 数字 = 远场外推等效，不代表近场实测；近场指向/波束细节属 R3 消声室（OUT OF SCOPE §3）。
- SPLo 单只 @1m 同样是参考灵敏度口径（小驱动近场边界小，单只 @1m 远场近似成立）；系统外推保持同一 1/r 口径以对齐。

---

## 3. EXPLICITLY OUT OF SCOPE（显式排除 — 两轨都不得算）

1. **最大 SPL（max SPL）**：需热额定功率（thermal rated power，Q-② vendor-pending [L4]）+ Xmax（LEAP 截图无）
   → **Line-3 pending**，本规格不算。本规格只算**灵敏度**（每单位输入的 dB），不算「能开多大声」。
2. **房间 / 箱体（enclosure）效应**：箱体谐振、房间反射、增益 —— 不算（R3 消声室/系统级）。
3. **离轴（off-axis）/ 指向性 / 波束频响**：本规格只算**正轴向 on-axis**；离轴、−6dB 波束宽、栅瓣属声学线/R3。
4. **频率依赖（超出灵敏度参考带）**：SPLo 82.161 是**参考灵敏度单值**口径。
   - SPLo 参考带可见性：KB-DRV-TEST-001 未显式标注 SPLo 的参考频带（LEAP No=0.103% 推参考效率，对应 SPLo 单值）；
     SPL-vs-freq 曲线（LMS）绝对电平条件未标（[L2-条件未定]）→ **本规格不引曲线绝对值**，只用面板 SPLo 单值。
   - **caveat（承袭）**：SPLo 参考频带未在截图显式标注 → 系统灵敏度同为「参考灵敏度单值口径」，
     **不代表全工作带（500Hz–6k）逐频灵敏度**；逐频 / breakup（~4.7–5k）/ EQ 整形属 R3，不在本规格。

---

## 4. 数值输出项（两轨各自独立产出，再交 critic 比对）

> 两轨**独立实现**、独立算出下列 4 项 + 中间量；critic 比对两轨是否一致（且与本规格公式一致）。
> 所有结果带 **[L2 模型]** 标 + SPLo 绝对电平 **[L2-条件未定]** caveat。

| 输出项 | 公式 | 说明 |
|---|---|---|
| **ideal_array_gain_dB** | `+10·log10(N)`，N=16 | 同 TOTAL 功率下 N 元相干 vs 单元的净增益（功率分摊口径，§2c）。**不是 20log10(N)**。 |
| **taper_loss_dB** | `20·log10( Σwᵢ / sqrt(N·Σwᵢ²) )`，i=1..16 | w16 = w8 镜像（§2d，读 csv `w_float_track1_scipy`，对 `track2_recurrence` 双轨核）。≤0。 |
| **system_sens_1W_total_dB** | `SPLo + ideal_array_gain_dB + taper_loss_dB` | **主输出**：系统灵敏度 @ TOTAL 电输入 1W，@1m 远场外推，on-axis，free-field，coherent。SPLo=82.161。 |
| **system_sens_283V_per_ch_dB** | `system_sens_1W_total_dB + 10·log10(P_283/P_ref)` | **次输出**：@ 2.83V per channel。P_283 = (2.83)²/Z_ch，Z_ch≈15Ω（channel-level [L1]）。须显式声明 P_ref 与“total vs per-ch”功率口径换算（见下注）。 |

**system_sens_283V_per_ch_dB 的功率口径注（两轨须显式写清，防基准混淆）**：
- 主口径 system_sens_1W_total_dB 的基准 = **整柱合计 1W**。
- 「2.83V per channel」= 8 通道**各**施加 2.83V → 每通道功率 P_283ch=(2.83)²/15 W，**整柱合计** P_283total = 8 × P_283ch。
- 故 @2.83V/ch 相对 @total-1W 的偏移 = `10·log10( P_283total / 1W ) = 10·log10( 8·(2.83)²/15 )`（dB）。
  两轨须各自独立算此偏移并与主口径相加；**显式写出 P_283ch、P_283total、偏移 dB 三个中间量**，不得只给终值。
- **可选第二次口径（若 critic 要求）**：@2.83V**单通道**驱动该通道串联对（其余通道静默）的 per-channel-pair 灵敏度——
  此为另一参考基准，须单独标注，**不得与全柱口径混报**。本规格主次两口径如上；其余口径列为 critic R22 裁定项。

**中间量（两轨都要落，便于 critic 逐项核）**：
- `N=16`；`w16` 向量（16 元，镜像）；`Σwᵢ`；`Σwᵢ²`；
- `P_283ch=(2.83)²/Z_ch`，`Z_ch=15Ω`（注明 channel-level 来源）；`P_283total=8·P_283ch`；
- `Re_unit=7.600Ω`（注明 unit-level，仅用于 per-unit 口径若被要求，主/次口径不直接用单只 Re，用 channel 15Ω 做 2.83V 换算）。

---

## 5. 实现约束（两轨独立性 + 可核性）

1. **双轨独立**：轨 A 与轨 B 各自从本规格独立实现（不共享中间代码），各自读 csv、各自算 4 项 + 中间量。
2. **csv 双列自核**：taper 用 `w_float_track1_scipy`，对 `w_float_track2_recurrence` 核（应一致到 ~1e-9）。
3. **单位/前缀**：本规格的灵敏度数学**只用** SPLo(dB)/N/w/Z(Ω)/V —— 不涉及 Mms/Cms/Vas 等存疑前缀量（§KB §1.1），
   故单位前缀歧义**不影响**本灵敏度计算（位移/excursion 模型属 Line-3，不在此）。
4. **结果呈现**：每个数字带 L 标；system_sens_* 带 [L2 模型] + SPLo 绝对电平 [L2-条件未定] caveat；@1m=远场外推（§2f）。
5. **不对外**：两轨结果交 critic（R22 裁口径 + 比对两轨），CTO 裁定前**无对外可引灵敏度口径**；**不改 88→82 任何文档**。

---

## 6. critic R22 裁定对象（口径线，结果正式前必裁）

1. Re 喂值 = unit 7.600Ω；15Ω=channel-level 不当单只 Re（承 RE_SCOPE_EVIDENCE）。 ☐ R22
2. 主口径 = @ TOTAL 1W；阵列增益 = **+10log10(16)**（功率分摊，非 +20log10）。 ☐ R22
3. taper_loss = 20log10(Σw/√(NΣw²))，w16=w8 镜像（{c,15−c} 共权）。 ☐ R22
4. 串联 +6dB **不另加**于阵列增益（防重复计）；串联只改阻抗记账。 ☐ R22
5. @2.83V/ch 用 Z_ch=15Ω 算实际功率（铭牌 2.83V/8Ω=1W 不成立）；total/per-ch 功率口径显式。 ☐ R22
6. @1m = 远场外推灵敏度（825mm 孔径 HF 非远场，诚实约定）。 ☐ R22
7. SPLo 绝对电平 [L2-条件未定]（条件 caveat 承袭）；SPLo 参考频带未标 → 系统灵敏度=参考单值口径，非逐频。 ☐ R22
8. 输出 [L2 模型]；OUT OF SCOPE（max SPL/箱体/房间/离轴/逐频）不算。 ☐ R22

---

## 附. 引用源（file:line）

- `sprint5/spl_redo/RE_SCOPE_EVIDENCE.md`（Re 口径分级证据包，前置）
- `knowledge_base/hardware_input/KB-DRV-TEST-001_extracted.md:23,33-37,62-63,86-90`（Revc 7.600 / SPLo 82.161 / 条件 caveat / Re 双轨）
- `knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md:12,19`（串联拓扑 + 15Ω channel-level [L1]）
- `knowledge_base/competitor/full_teardown_v2.md:43,45,47-48`（标称 8Ω/88dB [L4] / 单只 DC 7.4Ω [L1] / 送测语境）
- `sprint4/dsp/fira/dolph_w8_q15.csv`（pair {c,15−c} + Dolph −20dB w8，8 行，双列双轨核）

*SPL_MODEL_SPEC — gate-1 筛查共享规格。两轨依此独立实现 → critic R22 裁口径 + 比对 → CTO 裁定。
不动板 / 不动冻结文件 / 不改 88→82 / 不预判对外口径。系统灵敏度 = [L2 模型]，输入事实 = [L1]。*
