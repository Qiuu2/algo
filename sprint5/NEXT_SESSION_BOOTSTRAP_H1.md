# NEXT SESSION BOOTSTRAP — H1 线现场快照（2026-06-05，compact 前存档）

> 用途：会话压缩/重启后恢复现场。配合 memory/（r14-closed-fira-ruling / steering-v1-focusing / workflow-three-gate-rule / h1-line-state）使用。
> 当前 HEAD：`11a701d`。critic 轮次计数：**R1–R15 已用，下一轮 = R16**。

## 一、正在进行（最高优先）

**H1 R16 修正循环**（dsp 在修，回包后送 critic R16）：
- **缘起**：R15 修复包 CCES build 失败——3 个 error（h1_wcet_measure.c:137/146/168 `s_h1_fa undefined`）。根因 = R15 新增的三个函数（h1_state_save/restore/dcache_inval）放在 `static FiraChannelState s_h1_fa[]` 声明之前（C 先声明后使用）。
- **为何桌面没抓到**：三函数在 TARGET 守卫区（`#if FIRA_USE_REAL_ADI_FIR_HEADER && TARGET_SHARC`），桌面 gcc -fsyntax-only 根本不编译守卫区——dsp 关① 和 critic R15 的"gcc clean"对守卫区结构性失明（验证缺口 #2；#1 是 host test 无状态盲区）。
- **派单要求**：① 全部 static 状态声明上移文件顶部统一块（结构修非最小挪动）；② 诚实交代缺口；③ 实现 guard-stub 桌面检查（gcc -DTARGET_SHARC + stub 头模拟 ADI 符号），**证伪验证**（先对坏版证明能抓、再对修复版证明通过）。
- **流程**：dsp 回包 → critic R16 → PM 落预豁免+commit → CTO sync 重跑（C10 checklist）。

**Agent 实例**（SendMessage 续用）：dsp = `a7fdac0e6b92a1093`；critic = `ad4fc53d1461316e8`。

## 二、H1 重跑读数单（R16 过门后给 CTO）

Sync：仅 `sprint5/dsp/harness/h1_wcet_measure.c`（bench_main.c 接线已在板上）。FIRA build。

| 组 | 变量 | 期望 | 解读规则 |
|---|---|---|---|
| FG | `g_h1_fg_zero_recovers` | **1**（上次 0 = ST1 自检缺陷，R15 快照修复目标）| 不为 1 = BLOCKER 再诊 |
| FG | `g_h1_fg_focus_differs` | 1 | |
| A | `g_h1_cyc_focus_only`（=focus−nofocus，同态 A/B）| ×750/1e6 对照 **173–288 MCPS**（MAC-2× 校正后尺度；原 86–144 作废）| **此 L1 直接 settle DEC-S5 聚焦预算修正** |
| B | `cold/warm/max/min` | cold 应明显 > warm（D-cache 已真失效；上次 1.0002=全热）| 口径=真冷-DATA/I-cache 仍热/系统下界 |
| C | `cclk_hz/cclk_rc`、F4/F5 连续性 | 1e9/0、1/1 | |

被隔离不入账的首跑数（参考勿引用）：focus=590,137/nofocus=524,727/focus_only=65,410(~49 MCPS)/WCET≈无差。

## 三、重跑读数回来后的裁定队列（一次解锁三件）
1. 聚焦增量 [L1] 入账 → **DEC-S5 预算修正案**（86–144 vs ~173–288 vs 实测更优，L1 说了算；当前 FLAG 未静默改）
2. WCET 乘子 [L1 下界] → **DEC-S4-CRITERION-01 正式阈值材料**（最后依赖到齐，CTO 落槌）
3. 整系统残余终算 → **1.0× 临时下限是否守**（当前刀刃口径：worst 1.08×，距底线 0.08×，focus[L4]/WCET[L3] 未实测前不作断言——R15 修正措辞已入档，R5/R7/R13/R15 四次教训）

## 四、关键口径（不得漂移）
- **R14 线（已闭）**：官方加速比 **3.07×**[L1-derived]（3.13× 混 build 禁用）；8ch margin **2.878×** 必须连体 §8 未计入清单（DEC-S4-C9-RELEASE-01）；CCLK=1GHz 实测。
- **v1**：近场高频展区分区（2–5m/≥4kHz），车站 zoning 剔除（broadside 保留）；EQ=O1（master-bus 2-3 biquad + 保护限幅 REQUIRED per-channel T_k=T·w_k 护 −20dB 锥度）；执行序 = H1 优先 / R3 第二 / HW-1 可选（DEC-S5-OPT-ORDER-02）。
- **验收 X**（净隔离 ≥X dB @消声室）= OPEN 至 R3。
- 板上 cyc/MAC 现实 30–50（理想 1cyc/MAC 记账禁用）；聚焦真实成本基准 = 120 samp/frame（5.76 MMAC/s 级）。
- 两线隔离：R14/C9 基线数与 v1/[L4] 估算零交叉。

## 五、流程法（全部在档生效）
- POLICY v1.8 §4B 三道关（workflow 内 verify=初筛 / 独立 critic=命门 / CTO 常识审；修正稿同等过门）
- Commit discipline + Fallback（不得 verdict 前 commit；in-context critic 不算门）
- critic §12 ST1-E（裁"无害"须枚举 ALL 消费者）；harness 探针/态隔离；PM stateful cross-item 派单纪律
- verdict 必带 `reviewer: critic @ <exact model> / <date>`；硬件动作 C10 checklist；自由运行纪律（循环内禁断点，idle 读）
- CTO 角色：裁定/板跑/sync；PM 不替裁、verify-before-relay；dsp 出码；critic 独立门。

## 六、后续登记（不阻塞）
R3 消声室（待 T/S 2–4 周：EQ band 数 + 疗效 L2→L1 + 定 X）｜限幅绝对阈值待 U3/T-S｜JY/T 标准全文缺口（literature-patent）｜I-cache 失效符号板侧查（C10）｜HW-1 在 WCET 后若争 ≥2× 再启｜角度偏转 16ch 叉 ROI 待 CTO。

## 七、关键 commit 链（近）
`3359ff7` R14 三裁定落档｜`8e49cb2` v1 路线+POLICY v1.8｜`89bed86` 治理文档入库｜`4d7e528` v1 收窄+O1｜`2a50f51` H1 包｜`11a701d` R15 修复包（现 HEAD；R16 修 build 错进行中）
