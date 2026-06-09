# MATLAB 三轨独立验证 — 完整指标体系（EZKIT 前工具链可信度核）

**文档 ID**：DOC-MATLAB-VERIFY-01
**日期**：2026-05-29
**缘起**：CTO 级硬要求——EZKIT 到货前，numpy 工具链（SLL/WNG/DI/MC/超指向/8路）**零独立工具交叉核**；`sim_d55_beamwidth.m` 的 `max()` 选端瓣 bug 已证明 numpy 风格 bug 会潜伏，EZKIT 后才发现=软件链路返工。本任务用 **三轨独立**（numpy + MATLAB-agent + MATLAB-CTO）在 EZKIT 前把完整指标体系核一遍。
**执行**：acoustic-simulation（M0-M3，mcp__matlab__）+ Critic（RV，独立复算）+ PM（整合）
**几何**：N=16 / d=55mm / L=825mm / Dolph-Cheby-20dB / broadside / isotropic（SC-S3-GEOM-01）。**全为仿真值[L2]，非实测**；真实喇叭离轴/障板待 T/S + 消声室。
**独立性深度**：(b) 三轨——轨1 [L2-MATLAB-agent]（不同随机种子）/ 轨2 [L2-MATLAB-CTO]（p01/p02）/ 轨3 [L2-numpy]。

---

## 0. 结论先行
- **6 指标三轨全对照通过，零 BLOCKER，零 E-MATLAB-1（无两轨发散）。** Critic RV 独立复算 4 关键值全吻合。
- **三轨价值即时兑现**：M1 一个 **12dB 量级 WNG 公式 bug（草稿多除 |a|²）被三轨交叉核当场抓出**、定位"numpy 错"（Critic 独立数学验证 10log₁₀16=12.041dB 确认）、落盘前修正——证明 EZKIT 前三轨核是真有效，不是形式主义。
- **C7 第三次主动评审通过**；连续三次零 BLOCKER（panorama / 竞品对比 / 本任务）→ **支撑 POLICY 升 v1.4（数字身份证 + 双轨/三轨独立工具复核）**。
- 工具箱齐（MATLAB R2026a + Signal Proc `chebwin` + Phased Array `directivity()`），E-MATLAB-2 不触发。

## 1. 六指标三轨对照汇总（详见各段报告）

| 指标 | CTO 项 | 三轨结果 | 一致性 | 段 |
|------|--------|---------|--------|----|
| **SLL 频率扫描** | 1 | 标称 1k/2k/4k 均 −20.00dB（agent=numpy bit 级；CTO p01 系含公差 MC p50≈−18.5dB，口径不同非不一致）| ✅ | M1 |
| **WNG 频率扫描** | 2 | agent=numpy=**11.868dB**；CTO p01 MC p50=11.84dB（uniform 上限 12.04dB 削 0.17 合理）| ✅ | M1 |
| **DI 频率扫描** | 3 | **三轨此前全空，首算**：DI_2D 1k=15.52/2k=20.18/4k=22.54dB（agent=numpy bit 级；CTO 轨缺→诚实降双轨；官方 directivity() 旁证趋势一致）| ✅（双轨）| M1 |
| **公差 MC 3000 次** | 4 | 三轨**不同种子**收敛一致（BW p50/p95 差<0.05°，极差<0.25°）；**8-pair@1k fail 率 6.27/5.33/5.80%（≈5.8%，2σ 内）** | ✅ | M2 |
| **超指向 d=55**（ε=0.1/0.2/0.3）| 5 | 三轨 **bit 级一致**：ε=0.3→BW24.96°/WNG10.94dB；ε=0.1→24.02°/9.51dB。P0-3 结论（24-25°/+9.5~10.9dB）核实成立 | ✅ | M3 |
| **8路 A/B 串联 broadside 等价性** | 6 | **首验**：broadside+Dolph 对称权下 **8 路串联 ≡ 16 元独立**（机器精度，逐点差≤5.6e-12dB）；不等价维度=电子偏转丧失（DEC-S3-DSP-03）| ✅ | M3 |

> 详细三轨数表见：`matlab_verify_m1_sll_wng_di.md`、`m2_mc.md`、`m3_superdir_8pair.md`；侦察/工具箱见 `matlab_verify_m0_plan.md`；Critic 复核见 `critic_matlab_rv.md`。

## 2. 关键发现
1. **WNG 草稿 bug 被抓（三轨价值证据）**：agent 首跑 numpy WNG 误多除 |a|²=N → −0.173dB（差 12dB）；与 CTO p01 源码对照即暴露，定位"numpy 错"，落盘前修正。**这正是单轨自证发现不了、三轨交叉核当场抓出的那类 bug。**
2. **DI 是三轨首算**（此前 numpy/CTO 均无 d=55 DI）：agent+numpy 双轨闭合，CTO 轨缺已诚实降级标注，非缺标。
3. **8-pair@1k 工程风险（真实，非数值错）**：三轨一致复现 ~5.8% 超 30° 概率（p95≈30.0° 压线），源于 8-pair 自由度减半 + 1k 标称 29.3° 贴线。**建议进风险登记**（呼应 R5 / DEC-S3-DSP-04 超指向降级）。
4. **8 路串联严格等价**：依赖 Dolph 权中心对称（人为非对称权偏差达 71.6dB，证等价非巧合）；"8 路"=电气驱动/独立加权自由度，物理相位中心仍 16；电子偏转能力丧失（DEC-S3-DSP-03 已接受）。

## 3. Critic RV 裁决（C7 第三次主动评审）
**PASS，零 BLOCKER / 零 MAJOR（2 INFO）**（`critic_matlab_rv.md`）：
- C1（三轨 L 标签）/ C2（无冒充实测）/ C7（无撤回值裸引，M3 numpy 确在 d=55 重写非引 d=30 旧轨）**全 PASS**。
- Critic **独立复算** WNG 11.868dB / bug −0.173dB（=10log₁₀16 验证）/ BW 29.269° / MVDR ε 扫描 / 8-pair 对称性 / 第4种子 MC 4.60%——全吻合，三轨一致非编造。
- E-MATLAB-1 未触发（独立确认无漏报发散）。
- **LESSON-012 已记**（critic memory）：三轨独立工具验证价值 + WNG bug 抓取案例。

## 4. CTO 决策辅助小结
1. **numpy 工具链可信度**：经三轨独立核，6 指标（SLL/WNG/DI/MC/超指向/8路）**EZKIT 前已确立可信**——抓出并修掉 1 个 12dB 量级 WNG 草稿 bug，其余 bit 级/统计收敛一致。**桌面仿真基准在 EZKIT 实测前已去除"潜伏 numpy bug"风险**。
2. **唯一需登记的工程风险**：8-pair@1k 公差敏感（~5.8% 超 30°，三轨一致复现的真实结论，非 bug）→ 建议进风险登记，与 R5/超指向降级联动。
3. **制度依据**：连续三次 C7 主动评审零 BLOCKER → **POLICY v1.4（双轨/三轨独立工具复核）依据确立**，待 CTO 批准立项。

---

*DOC-MATLAB-VERIFY-01，2026-05-29。acoustic（M0-M3 三轨真跑）+ Critic（独立复算 RV，PASS 零 BLOCKER）+ PM 整合。全为 [L2] 仿真三轨；零撤回值裸引；CTO 第四轨 T1-T10 独立验证并行（互为佐证）。第四轨高精度 MC 后台冗余佐证中。*
