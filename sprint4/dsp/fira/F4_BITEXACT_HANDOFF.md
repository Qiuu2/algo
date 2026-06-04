> **状态更新 2026-06-04：R14 已 CLOSED（DEC-S4-R14-RULING-01），>=10x 判据已退役→实时下限+余量（DEC-S4-CRITERION-01），C9 已 RELEASED 附诚实分母（DEC-S4-C9-RELEASE-01）。本文以下为写时口径，存史。**

# F4 Session Handoff — FIRA 单通道子带定点 bit-exact 里程碑（§12 实战记录）

**日期**：2026-06-04 ｜ **作者**：Project Manager Agent（lead, claude-opus-4-8）｜ **状态**：CTO 已确认口径
**挂接**：R14 / DEC-S4-R14-GRANULARITY / DEC-S4-DSP-01 / POLICY-PROV-001 v1.7 / critic skill **§12**（本文是其实战记录）/ `.claude/team_config.md`

---

## 1. 里程碑（CTO 口径，逐字）

> **「R14 关键里程碑：FIRA 单通道子带定点 bit-exact（L1 板上，commit 9d9fbec）」**

- **R14 主门仍 OPEN**；**C9/铁律八维持**；FIRA 收益一律标 `[L4/待验证]`、**不进选型**。
- **本结果不得写成 R14 闭合**。R14 闭合 / C9 松绑的前提 = F5（8ch 全链）+ F7（含开销 cycle 实测、裕量重算）达标后由 CTO 裁定。

## 2. 板上四证（真绿确认，2026-06-04，[L1/EZKIT]）
1. 自检门 `g_f4_crc_core == 0x2E0D8C6E`（核子带 golden，与桌面 `sbgold` 逐位一致）
2. `g_fira_f4_pass=1` / `mismatch_idx=-1` / `mismatch_sb=-1`
3. `g_fira_f4_crc == 0x2E0D8C6E`（FIRA 子带 == 核子带，逐位）
4. `dump_core[0..31]==dump_fira[0..31]` 逐位 0 差、probe 四带全等 —— **32 点 sharp falsifier 干净归零，与桌面 max-diff=0 预测对上**（判据为子带级、依赖滤波；占位版桌面证 FAIL —— 非假绿，FG1/FG2 双防住）

## 3. 六轮独立 critic 拦截（§12 实战记录 —— 每条都在上板前被拦）

| # | 拦截 | §12 门 | 谁先漏 | 后果若漏过 | 轮次/commit |
|---|---|---|---|---|---|
| 1 | **D1b** DECIMATION 输入计数语义错（`ntaps+window-1`→应 `ntaps+ratio*window-1`） | IO1 | PM 诊断只框到 D1 缓冲供给 | 修了 D1 仍垃圾，再追一轮 | R1 / 3a92754 |
| 2 | **M2 哨兵自掩盖**（memset 哨兵抹掉 D2 证据 + 没盖 `in`/`s_seg_out3` + 全局未定义不链接） | 方法论(FG) | PM 提案 | 假 refuted，误导根因 | R1（M2 被否，未上板） |
| 3 | **INT 跨帧历史在错采样域**（raw vs zero-stuffed；桌面 55286 vs 0） | ST1 | dsp 实现 | 板上呈"sb0过/sb1-3帧边失配"→误判 postscale 白追 | R2 / 9d9fbec 前置 |
| 4 | **A5 flush-back 险**（flush+invalidate 会把 memset 零写回盖 DMA 数据→改 invalidate-only/删冗余 memset） | IO1(d) | dsp 初版 | postscale 读全零 | A5-R1/R2 / 53bd875→a2c42e7 |
| 5 | **A5 符号**（`adi_cache_invalidate`=ARM 侧名,SHARC 无 → 仓库 linker-log 实证 `<sys/cache.h>` `flush_data_buffer`） | A5 硬门（板 link 闸按设计拦下；修复以仓库证据定名,critic 过） | PM/dsp 假设了 ARM 名 | 烧不进/或带病绿 | 板link闸+R / a2c42e7 |
| 6 | **DEC 抽取相位**（FIRA 硬件留偶相、核留奇相;桌面 8/8 复现板残差+预测爆炸 0,-10,0,+22…;**并先否了 PM"FIRA MAC 不同/需容差"的过度结论**——PM 模型把核相位 bake 进 FIRA 侧=自证盲区） | FG1+IO | **PM 过度结论** | 走向容差/判据放宽,而真因是可修相位 | R5否+R6过 / 9d9fbec |

> **方法论结论**：六条中 4 条是"桌面可证伪的逻辑错"，全部在桌面清掉；板上只消耗了 3 次烧录（垃圾→LSB残差→PASS），每次读数都有事前预测可对。critic 的独立重算（自写转录/换种子/审 proof 非自证）是抓住 #3/#6 的关键——**自审两次漏掉的类别，独立异见者两次抓住**。

## 4. Commit 链（本程）
`03ccc04`（诊断+锚改正 0x2E0D8C6E）→ `3a92754`（契约修复 D1/D1b/D2/D3/scratch）→ `53bd875`（A5 invalidate-only + 花名册）→ `a2c42e7`（A5 真符号 flush_data_buffer/方案B）→ `1727dcd`（残差排查 INCONCLUSIVE 存证）→ **`9d9fbec`（DEC 相位修复 + 32-dump → 板上 PASS）**

## 5. 桌面证明资产（[L2]，全部在 `sprint4/dsp/fira/`）
`int_history_proof.py`（INT 零插域+DEC 历史 max-diff-0）· `residual_repro.py`（postscale 候选穷举,负结果存证）· `residual_pack80_repro.py`（§38-10 3字打包无损证明,w[2]=符号扩展非零 29/64）· `decphase_fix_repro.py`（相位修复整帧 0 / 未修爆炸 1,734,588）

## 6. [ASSUME] 登记簿结清状态（板上 PASS 一并坐实的假设集）
A2 nWindowSize=输出计数 · A4 写回槽数 · A5 cache（flush_data_buffer 链接+语义正确） · A-orient（coeff palindrome→moot） · INT=SINGLE_RATE+软件零插 · DEC=SINGLE_RATE+软件抽取相位1 · 跨帧历史（DEC raw 域/INT 零插域）—— **以"单通道子带逐位相等"为整体证据 en bloc 坐实**（单一 chirp 激励;F5 换激励/8ch 仍须复验）。仍开放：单线程 scratch（F5 并发须改 per-task）· GAP-SAT（饱和路径未被本激励覆盖,F5 复议）。

## 7. 下一步（CTO 已定向）
- **F5**：8ch 全链规划（8 路 broadside 求和、任务编排/并发与 per-task scratch、R14 完整闭合定义、GAP-SAT 复议、8ch golden 要否）。
- **F7**：含开销 cycle 实测 + 裕量重算 —— **结果仍受 C9 管辖**，在 CTO 裁定 R14 闭合前不得进任何选型/承诺依据。
- 这两项达标前**不谈 R14 闭合 / C9 松绑**。

## 8. Team 运行记录（审计，对齐 C5）
- 花名册/档位：`.claude/team_config.md`（lead/critic/dsp = `claude-opus-4-8`；peer-challenge ON）。
- **本程全部六轮 critic 裁定的 reviewer = critic @ `claude-opus-4-8`**（2026-06-03 ～ 06-04）。自 Step-3 起裁定带模型标记（见 team_config Step-3 节）。
- 运维教训：子 agent 长任务（>~7min）有 socket 死风险 → **派单收窄单问题**；死后 PM 按盘上状态接力（残篇脚本可恢复并复跑）。
