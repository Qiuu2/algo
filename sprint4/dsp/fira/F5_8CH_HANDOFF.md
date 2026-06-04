# F5 Session Handoff — 8ch 子带定点 bit-exact 上板达成（L1）

**日期**：2026-06-04 ｜ **作者**：Project Manager Agent（lead, claude-opus-4-8）｜ **状态**：CTO 已确认口径
**挂接**：R14 / DEC-S4-R14-GRANULARITY / F4_BITEXACT_HANDOFF.md（前序）/ F5_F7_PLAN.md（critic 两轮 PASS 基线）/ POLICY-PROV-001 v1.7 / critic §12

---

## 1. 里程碑（CTO 口径，逐字）
> **「8ch 子带定点 bit-exact 上板达成（L1，commit 44a99e8）」**

- **R14 主门仍 OPEN**；**C9/铁律八维持**；FIRA 收益一律 `[L4/待验证]`、不进选型。**本结果不写成 R14 闭合。**
- R14 闭合 / C9 松绑的最后裁定依据 = **F7**（含开销 cycle 实测 + 裕量 vs ≥10× + CCLK/G6 实测）。

## 2. 板上证据（2026-06-04，[L1/EZKIT]，PM 复核十进制↔锚表 8/8 命中）
- **F4 连续性**：`g_fira_f4_pass=1`、32 点 dump 核/fira 全等 —— 单通道基线未被 F5 碰坏（回归连续性设计生效）。
- `g_f5_pass_all=1`、`g_f5_pass[0..7]` 全 1。
- **8 锚逐条命中**（读数十进制 → 锚）：2390783785→`8E807729`｜3002196287→`B2F1E13F`｜2064686193→`7B109C71`｜3619496935→`D7BD23E7`｜2684409350→`A000D606`｜604233861→`2403E085`｜3096285621→`B88D91B5`｜772639854→**`2E0D8C6E`（c=7 unity = F4 基线总锚 ✓ 超集交叉验证）**。
- `g_f5_crc_fira[0..7]` 逐条 == `g_f5_crc_core[0..7]` = **8 路全 bit-exact**；8 条 golden 全相异（非单常量、真 8 路独立，FG1 成立）。

## 3. F5 三件构成（全部独立 critic PASS，verdict 带 `reviewer: critic @ claude-opus-4-8 / 2026-06-04`）
| 件 | commit | 要点 | critic 独立性亮点 |
|---|---|---|---|
| F5-C 权重表 | `ae4a837` | Dolph-Cheby -20dB 8 路 Q15 表冻结 `[28404,16525,20371,24031,27287,29934,31802,32768]`；三轨（scipy/Barbiere 闭式/MATLAB）float diff 2.3e-12、量化表逐位同；**全权重 ≤1.0 双域验证 → GAP-SAT premise-VERIFIED**；波束门 SLL −20.00dB / BW@1k 29.269°≤30° | 铁律七真抓一只：dsp 首版独立轨（DFT 法）有 bug → 双轨不一致定位弃用 |
| F5-B 删求和 | `360ba7e` | 8进1出 `w_add_i32` 求和 wrapper → 8进8出独立（对齐 CTO 锁定拓扑：8 通道独立出 8 DAC 驱 {c,15−c} 对称串联对、声场叠加）；GAP-SAT **closed-by-topology（premise 已验）**；冻结核未动 S2 仍 0x90556BC7 | critic **注 stub 进 ch7** 对抗证实检查抓坏路（[C] 首坏路定位 / [D] 串扰检出） |
| F5-A 链×8 | `44a99e8` | `FiraChannelState[8]` + 权重入链（输入侧 `(w_q15·x_q31)>>15`，golden 含权重=bit-exact 边界）+ 8 条 per-channel golden + 72 次串行 QueueTask 单 handle + C7 banner 清理（全树 grep 表干净） | critic **第三套自写 CRC + 自算 chebwin 逐位复现全部 8 golden** + unweighted 对照塌缩证 FG1 + 桌面 FG2 link 测 |

前置事实勘查：8 通道→16 单元物理映射 = **{c,15−c} 对称配对 [L1/硬件实测]**（拆机原文 `定向音柱AI数据_extracted.md:40`；m3 等价证明 diff=0.000e+00）——CTO「查实再生成」令执行，PM 逐条亲验。

## 4. 流程记录
- **流程偏差（已处置+落字）**：F5-A dsp 在自审后、独立 verdict 前 commit。独立 verdict 事后 PASS、无损；CTO 接受处置并令落字 → **Commit discipline 硬规**入 `.claude/team_config.md`（commit `1ce0819`）：不得在独立 critic verdict 前 commit；先 commit 后 verdict = 流程偏差须原样上报 CTO。
- 团队：lead/critic/dsp = `claude-opus-4-8`；peer-challenge ON；verdict 全程带模型标记（Step-3 审计）。

## 5. 下一步（CTO 已定向）：F7 —— R14 闭合/C9 松绑的最后裁定依据
- 同一工程加测量块（critic 过、按 Commit discipline 硬规），再一次板跑拿数。
- 测：8ch×9 段串行 FIRA 全帧 wall cycle（含 CreateTask/FixedPointEnable/QueueTask/spin/postscale/cache-invalidate 全开销）+ **CCLK 实测关 G6**（现 1.32× 裕量按 1GHz 假设）。
- 判据：margin = (CCLK_实测 × 1.333ms 帧周期) / wall_cycle ≥ **10×**。
- **C9 纪律**：所有结果 `[L4/待验证]`、不进任何选型/承诺依据，仅供 CTO 裁定 R14/C9。
