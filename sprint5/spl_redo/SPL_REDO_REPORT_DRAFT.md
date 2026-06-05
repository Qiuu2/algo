# SPL_REDO_REPORT_DRAFT — 系统正轴向灵敏度 [L2 模型, 绝对电平条件未定] 重做（DEC-S3-DSP-05 解锁）

> 任务：CTO Line-2 指令 — 用已归档 **L1 T/S**（`knowledge_base/hardware_input/KB-DRV-TEST-001_extracted.md`）重做 SPL 模型。
> 范围：**纯软件 / 不上板 / 不动冻结文件**；写盘只在 `sprint5/spl_redo/`。
> 流程闸：POLICY v1.8 三门 —— 本工作流 = **门-1 筛查**；**critic 门 R22 先裁口径，结果才正式**；**CTO 裁定在先**。
> 输出分级：系统灵敏度 = **[L2 模型]**；输入事实 = **[L1]**（SPLo 绝对电平条件 = [L2-条件未定] caveat 承袭）。
>
> 日期：2026-06-05｜门-1 筛查 by critic（独立第三计算 + 两轨比对）｜状态：**DRAFT — R22 未裁 / CTO 未裁 / 对外口径冻结中**。

---

## 0. 表头数字（headline，[L2 模型]，对外冻结中）

| 输出项 | 值 [L2 模型] | 口径 |
|---|---|---|
| ideal_array_gain_dB | **+12.041200 dB** | =10·log10(16)，功率分摊口径（**非** 20log10N） |
| taper_loss_dB | **−0.173055 dB** | Dolph −20dB w8 镜像到 16，=20·log10(Σw/√(N·Σw²)) |
| **system_sens_1W_total_dB**（主） | **94.029145 dB** | @ 整柱合计电输入 1W，@1m 远场外推，on-axis，free-field，coherent |
| **system_sens_283V_per_ch_dB**（次） | **100.334861 dB** | @ 每通道 2.83V，Z_ch=15Ω channel-level 记账 |

> 主口径分解：`94.029145 = SPLo 82.161 + 阵列 12.041200 + taper (−0.173055)`。
> 次口径偏移：`100.334861 = 94.029145 + 6.305716`，其中 `6.305716 = 10·log10(8·2.83²/15)`。
> **以上为模型计算所得 [L2]，并列呈现 unit-level 输入事实 [L1]；CTO 裁定前无对外可引口径，不预判。**

---


## 0.1 对旧值的变化（呈 CTO，非对外）（critic R22 F22-MAJOR-1 补全）

模型系统灵敏度 94.029 dB [L2 模型, @1W total/@1m 远场外推/绝对电平条件未定] 比旧占位 **117 dB [L4] 低约 23 dB**——旧 117 是全相干 +24dB(=20logN) 口径（decisions_log:394-395，critic 当时已判过乐观，功率守恒=+12dB），本重做用功率分摊 +12.04dB(=10logN) 与该早期裁定一致。次口径 100.3 dB @2.83V/8 通道 与铭牌 88 dB/2.83V(单只) **不同口径不可直比**。**这是决策相关的建模数变化（PRD/对外 SPL 故事须据此更新），但仍 [L2 模型]、绝对电平条件未定、CTO 裁定前不对外。** 88/117 源值未改（冻结）。

## 1. Re 口径证据摘要（CTO 硬约束 1 —— 先举证后喂 Re）

全文见 `RE_SCOPE_EVIDENCE.md`。层级钉死如下（仅引仓内源）：

| 层级 | 值 | 分级 | 出处 |
|---|---|---|---|
| **unit-level Re**（喂单只模型） | **7.600 Ω**（LEAP Revc），双轨核 **7.4 Ω**（万用表单只 DC） | [L1/仪器]+[L1 拆机] | `KB-DRV-TEST-001:23,86-90` / `full_teardown_v2.md:47` |
| **channel-level Z**（串联对，**不当单只 Re**） | **15 Ω**（万用表直测串联） | [L1 拆机] | `定向音柱AI数据_含追问回复:12,19` |
| 标称阻抗（背景，不进模型） | 8 Ω | [L4 铭牌] | `full_teardown_v2.md:43` |

- **桥接互证**：2×7.4 = 14.8 ≈ 15（散差 ~1.3%）→ unit(~7.4–7.6) 与 channel(~14.8–15) **两层级不重叠、互不冒充，层级 CLEAN**。
- **LEAP Revc=7.600 = unit-level** 论证坐实：送测对象 = 单只拆机单元（`full_teardown_v2.md:48`）；LEAP 面板 Qts/Fs 自洽（单只 T/S，串联对给不出这组自洽参数）；数值 7.600 ≈ 单只 DC 7.4（若为串联对应 ~15Ω，矛盾）。
- **建模用法**：主/次口径**均不直接用单只 Re**；`7.600Ω` 仅记录（per-unit 口径若 R22 要求才用）。`15Ω` **只用于 2.83V→功率换算**（channel-level）。**串联 +6dB on-axis 不另加**——已含于阵列增益 +10log10(16)（防重复计红线）。

---

## 2. 规格摘要（`SPL_MODEL_SPEC.md`，两轨共吃同一规格）

- **题面**：由单只 SPLo 82.161 dB → 经阵列相干增益(N=16) + Dolph −20dB taper 损失 + 功率/参考换算 → 系统正轴向远场灵敏度。
- **口径锁定**：主=@TOTAL 1W；阵列增益=+10log10(16)=+12.0412 dB（功率分摊，**非** +20log10N=+24.08）；taper=20log10(Σw/√(NΣw²))，w16=w8镜像（pair {c,15−c} 共权 w8[c]）；次=@2.83V/ch，Z_ch=15Ω → P=2.83²/15 < 1W（**2.83V/8Ω=1W 铭牌惯例不成立**）；@1m=**远场外推**（825mm 孔径对 HF 非远场，诚实约定）。
- **显式 OUT OF SCOPE（两轨都不算）**：最大 SPL（需热额定功率 Q-② [L4 vendor-pending] + Xmax [LEAP 截图无] → **Line-3 pending**）、箱体/房间、离轴/指向性/波束频响、逐频（SPLo 为参考单值，非全工作带逐频）。

---

## 3. 两轨独立产出（critic 比对对象）

| 输出项 | Track-1 (numpy) | Track-2 (MATLAB R2026a) |
|---|---|---|
| ideal_array_gain_dB | 12.041199826559248 | 12.041199826559248 |
| taper_loss_dB | −0.17305512070596213 | −0.17305512070596213 |
| system_sens_1W_total_dB | 94.02914470585328 | 94.029144705853284 |
| system_sens_283V_per_ch_dB | 100.3348606957017 | 100.33486069570171 |

- 中间量两轨一致：N=16；Σw=12.885911890870162；Σw²=10.799803268614895；P_283ch=0.533926…W；P_283total=4.271413…W；offset=6.305715989848428 dB；w16 向量逐元一致。
- **独立性**：Track-2 声明仅依规格实现、未读 Track-1 代码（独立性 FULL）。两轨 csv 自核 max_abs_diff=2.34e-12 < 1e-9（PASS）。

---

## 4. 门-1 筛查结果（critic 独立第三计算 + 比对）

> 方法：critic 直接从 csv 重算 w16/Σw/Σw²/4项输出（第三条独立计算路径），并三方比对；live 重跑 Track-1 验证可复现。

| 检查 | 判据 | 结果 |
|---|---|---|
| (1) 四输出两轨一致 | <0.01 dB | **PASS** — maxΔ = **0.00e+00 dB**（track1/track2/critic 三方完全一致；float 尾差均 0） |
| (2) taper 自行从 csv 重导 | 与两轨一致 | **PASS** — critic 重算 −0.173055120705962，maxΔ=0.00 |
| (3) ideal gain = +12.041 dB（10log16） | 精确 | **PASS** — 12.041199826559248，与 10·log10(16) 差 0.00e+00 |
| (4) 约定遵循 | 1W-total 主 / 2.83V 次带 15Ω 记账 | **PASS** — 主=SPLo+10log10(16)+taper；次 offset=10log10(8·2.83²/15)=6.305716；15Ω channel-level；串联+6dB 未重复计 |
| (5) 分级/冻结/不预判语言 | spec + draft 均在 | **PASS** — [L2 模型]/[L1 输入]/[L2-条件未定]/不得改88→82/不预判 在 spec(各 ≥3) 与 evidence 与本 draft 均在 |
| (附) 写盘范围 | 仅 sprint5/spl_redo/ | **PASS** — git 仅 `?? sprint5/spl_redo/`；无冻结文件改动；Track-1 live 复现一致 |
| (附) csv 双轨核 | <1e-9 | **PASS** — 2.34e-12 |

**门-1 筛查总判：PASS（所有 7 项）。** 注：门-1 是内部筛查，**非正式门**；正式裁口径属 critic R22。

---

## 5. 诚实 caveat（承袭，不得弱化）

1. **SPLo 绝对电平 = [L2-条件未定]**：KB-DRV-TEST-001 截图未标测量距离/电压/障板/平滑（`:11-12,37,62-63,139`）→ SPLo 形状 [L1]，**绝对电平 [L2-条件未定]**。本模型原样承袭——**94.029 dB 不是已坐实的绝对值**，其绝对基准随 SPLo 绝对电平条件待定。
2. **@1m = 远场外推**：825mm 孔径，HF 下 2L²/λ ≫ 1m → @1m 对高频**非远场**。报「远场外推等效灵敏度 @1m」（行业约定），**不声称 1m 处即满足远场**；近场波束细节属 R3。
3. **最大 SPL 不在范围（Line-3 pending）**：本模型只算**灵敏度（每单位输入的 dB）**，不算「能开多大声」。max SPL 需热额定功率（Q-② [L4 vendor-pending]）+ Xmax（LEAP 截图无）→ **Line-3**。
4. **SPLo 为参考单值，非逐频**：SPLo 参考频带未在截图标注 → 系统灵敏度同为**参考灵敏度单值口径**，**不代表 500Hz–6k 逐频**；逐频 / breakup(~4.7–5k) / EQ 属 R3 系统级消声室。
5. **w16 序非单调（flag，不影响门-1）**：csv 中 w8[0]=0.8668 > w8[1]=0.5043（边元权重大于次边元），与典型 Dolph 单调锥度不同。本筛查**原样采用 csv 权重**（taper 公式仅依 Σw、Σw²，与排序无关，故不影响一致性结论）；权重物理排序是否符合 Dolph −20dB 设计意图 = **R22/DSP 线复核项**，登记 flag。

---

## 6. 三门状态 + 对外口径冻结

| 门 | 状态 |
|---|---|
| **门-1 筛查**（本工作流） | **DONE / PASS**（7/7；两轨+critic 三方一致 maxΔ=0.00 dB；csv 双轨 2.34e-12；写盘范围 clean） |
| **critic 门 R22**（正式裁口径） | **PENDING** —— 裁定对象见 spec §6 / evidence §5（Re 喂值、+10log1016、taper 公式、串联不重复计、2.83V 用 15Ω、@1m 远场外推约定、SPLo 条件 caveat、OUT OF SCOPE、w16 序 flag） |
| **CTO 裁定** | **PENDING** —— 系统级真值 + CTO 裁定在先 |

**对外口径冻结（CTO 硬约束 2 & 3，本报告遵守）**：
- 输出 = **[L2 模型]**；**任何文档不得改 88→82**（旧值仅作 provenance：铭牌 88dB[L4]、旧占位 117dB[L4]、LEAP SPLo 82.161dB[L1 形状/绝对电平 L2-条件未定]）。
- **不预判**：呈现「计算所得系统灵敏度 [L2]」并列「unit-level 输入事实 [L1]」；**R22 + CTO 裁定前无对外可引灵敏度口径**。
- 不上板、不动冻结文件、写盘仅 `sprint5/spl_redo/`。

---

## 附. 文件（绝对路径）

- `/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint5/spl_redo/SPL_MODEL_SPEC.md`
- `/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint5/spl_redo/RE_SCOPE_EVIDENCE.md`
- `/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint5/spl_redo/spl_model_numpy.py`
- `/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint5/spl_redo/results_track1.json`
- `/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint5/spl_redo/results_track2.json`
- `/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint5/spl_redo/SPL_REDO_REPORT_DRAFT.md`（本文件）

*SPL_REDO_REPORT_DRAFT — 门-1 筛查 DONE/PASS。R22 裁口径 + CTO 裁定在先；对外口径冻结至两裁完成。输出 [L2 模型]，输入 [L1]。不动板 / 不动冻结文件 / 不改 88→82 / 不预判对外口径。*
