reviewer: critic @ claude-fable-5-1 / 2026-09-02

# Critic Verdict — Sprint 7 B 批次「算法层升级提案」全包（4 份文档 + dsp 台账脚本 + acoustic 4 py / 1 m / 8 csv / 3 log；均未 commit）

**总裁定：FAIL（BLOCKER ×1 / MAJOR ×2 / MINOR ×9 / INFO ×5）。**
唯一 BLOCKER 是红线门 C7/C2 的撤回传播残留（A 批次 F-5/F-21 已把「1.5 dB 重复性」降为 [未落盘/工作假设 L4]，`S7_VERIFICATION_PLAN.md:119,310` 仍标 `[L1]`，且落在 pass/fail 判据行）。修法两行改标 + 五行补注 + 提案 :243 改口；修完连同 2 条 MAJOR 做 delta 复审，预期转 PASS（带 MINOR）。**算术、声学数字、逻辑链、L 级纪律、红线（冻结件/.cproject/.project/竞品固件）全部实核通过**——这份包的骨架是对的，被卡在一个 A 批次预告过「届时会查」的传播项上。

仓库根：`/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/`。本审只读：未改仓库/暂存区/记忆；未重跑 `sprint7/sim` 任何脚本（dsp 台账脚本以副本在 scratchpad 跑，不写文件）。独立复算脚本与输出：
- `/tmp/claude-1000/-home-it1234-algorithm-speaker/e1279b17-6caf-456c-8270-fe1809f7f500/scratchpad/critic_B_recompute.py`（全新实现，不 import `s7_common`）
- `/tmp/claude-1000/-home-it1234-algorithm-speaker/e1279b17-6caf-456c-8270-fe1809f7f500/scratchpad/critic_B_recompute.log`
- `/tmp/claude-1000/-home-it1234-algorithm-speaker/e1279b17-6caf-456c-8270-fe1809f7f500/scratchpad/ledger_copy.py`（dsp 台账脚本副本，只打印）

---

## 0. 作者声明 vs 实核（先给结论）

| 作者声明 | 实核 |
|---|---|
| 帧预算 1,333,333 / 1.5× 线 888,889 / 到线余量 57,986 = 43.5 MCPS / 余量 1.605× | **全部成立**：1e9/750 = 1,333,333.3；/1.5 = 888,888.9；−830,903 = 57,985.9 → 43.49 MCPS；1,333,333/830,903 = 1.6047 |
| B1 6,728..52,352 / B2 65,371..117,246 / B4 8,171..48,000；组合表 §4（提案）= §8.2（dsp） | **逐格一致**（我的独立算术 = 脚本副本输出 = 两文表）。B1 低端 640×8.5118+1024+256 = 6,728；高端 960×50+4,096+256 = 52,352；B2 高端 65,371×1.7935 = 117,246；B1+B2 1.333..1.477×；B1+B4 1.432..1.576× |
| 8.51 cyc/MAC（H1 flat-FIR）用于 B1 低端 | 已如实标 [L3] 并注「非 float 递归 biquad 同类」——**未越级**（低端本就不是地板，见 F-17 INFO） |
| 三口径互不可比，T2 账只并列不相加 | **未相加**；但提案 :185 / dsp :448 用「矛盾」一词互称两口径，恰是 F60-MAJOR-1 禁的措辞（F-4 MINOR）；另 dsp :74 / 提案 :67 把 EQ-on/off 墙钟差说成能「坐实 T2 账 O1_contention_reserve=15」= 固定侧 vs 争用侧混口径（**F-3 MAJOR**） |
| dsp §0.3 质疑 DEC「6.4 倍」 | **成立**。F7 463,273 与 M2 830,903 同为含忙等的 main 上下文墙钟（`fira_regression.c:611-619` 括号内调 `fira_tfb_analyze/synthesize`），同口径比 = 1.794×；「~130µs」基数的文字出处我找到了：`m1_loopback_tdm.c:572`「Beam compute ~130us (H2 account, off-board caliber)」与 `STAGE4_ALGORITHM_VALIDATION_TEST.md:61`「纯核~130µs[L2]」——是上板前离板账，不是 H2 实测 base（454,730 cyc = 455 µs），6.4× 是跨口径比。D12「加注不改原文」处置正确，注里应带这两处出处（F-13 INFO） |
| Dolph-20 BW@1k 29.27 / dolph25 32.18 / MVDR ε=0.3 24.96 | **独立复算逐位吻合**：29.269 / 32.184 / 24.955（WNGa 10.944）；ε=0.01 22.869/4.568；DI 天花板 +1.947 dB（报告 +1.95），+1.9 dB 处 WNGa −40.8，−43 dB 处 +1.93；WNGn≥−10 地板 BW 22.66；Σw(kaiser_b22.5) 4.138 → −9.87 dB；栅瓣 6236/5314/4647/4158 Hz |
| B2 §6.2「只置换权重不置换延时 → 焦点损失 4–13 dB」 | **机制与符号量级独立坐实**：自写球面波求和 4k/2m REF +4.85 → WPERM −8.51（−13.36）、6k/3m −13.21、2k/2m −3.98，与报告逐位同。机制：perm 把外 4 对与内 4 对延时互换，边对拿 26 µs 代替 122 µs，中心对拿 44 µs 代替 0 → 4 kHz 处相位错最大 138°，主瓣被打散；τ≡0 控制臂等价成立 |
| §5.4 把 EXP_COMPET [L3]「1.9 dB / −43 dB」升 [L2] | **理由成立但须换引用源**：升级依据是本轮 [L2] 仿真给出的 +1.95 dB / WNGa −40.8..−47.3 与旧表述一致，新引用须指向 `s7_lowfreq_superdir.log:78-81`（验证计划 :179 已这么做，但把 −43(WNGa) 与 −59(WNGn 天花板) 错配成一对，F-5 MINOR） |
| 「恒定波束宽 ≠ 低频变窄」 | 提案 :28/:124/:138/:144、dsp §4.1/§5.1、计划 :179 **无一处违反**；BW(1k) 恒 29.27° 在所有子带设计里成立（`s7_constbw_fixedwindow_flatness.csv` 三设计行 BW_1k 均 29.269） |
| 推荐组合 B6.3→B6 基座→P0/P2/P1→B1；B2 下轮；B3/B7 不做；B4/B5 挂起 | **每条可从三份输入推出**（见 §2）；「本轮做」与「只出方案」不冲突但缺一句显式界定（F-6 MINOR） |
| 未改冻结件/.cproject/.project；脚本只在 sprint7/sim；不引竞品固件内容 | **成立**：`git status` 仅 `?? sprint7/docs/ sprint7/sim/` + 既有 `.h`；`git diff`/`--cached` 空；12 个冻结件 + 2 个 `.cproject/.project` 均无变动；sprint7 内对 HIT-9616 的引用仅限登记/裁定/D9，零内容引用 |
| 三份输入互引数字逐处一致（65,371 / 830,903 / 463,273 / 4.85 / 8.09 / 29.27 / 14.5） | **一致**（计数表见 §4）；仅计划 :179 用 29.28°/0.72°（R5 旧舍入）与全包 29.27/0.73 不同（并入 F-5） |
| dsp 对声学报告引用路径 | `sprint7/sim/acoustic/S7_ACOUSTIC_SIM_REPORT.md` 共 5 处 + 节号，**正确**；引用的 §3.5/§4.2/§5.3/§6.1/§6.2/§7 节号均存在 |
| 计划 :31/:179 已按 F-21 改口 | :31、:179 **已改**；但同一数字在 :119、:310 仍 `[L1]`，:120/:195/:220/:306/:394 无标 → **F-1 BLOCKER**；提案 :243「已改口」为部分事实 |

---

## 1. Findings

| ID | 严重度 | file:line | 问题 | 修法 |
|---|---|---|---|---|
| **F-1** | **BLOCKER**（C7 撤回传播 + C2 越级标注） | `sprint7/docs/S7_VERIFICATION_PLAN.md:119`「≤ 重复性地板 1.5dB **[L1]**」、`:310`「> 重复性地板 1.5dB **[L1]**」；同数无标：`:120,:195,:220,:306,:394`；`sprint7/docs/S7_ALGO_UPGRADE_PROPOSAL.md:243`「已按 F-21 改口」 | A 批次 F-5 裁定「1.5 dB 重复性」全库无落盘出处，降为 [未落盘，出处待补]、**补出前不得引用为 L1**；本计划 :31 已照办并自定「判据里写为 2× 地板 = 3dB 工作假设 [L4]」，但 :119/:310 两条**判据行**仍以 [L1] 引用同一数字 = 铁律五「逐处加标」未做完（LESSON-010 同型：源头降标、派生处残留实测标签）。A 批次 delta 已预告「B 入库前必改、届时会查」。提案 :243 把部分改口写成已改口 | :119/:310 改「1.5dB [L4 工作假设，未落盘，见 §0.2]」；:120/:195/:220/:306/:394 各加「(工作假设 [L4])」或「见 §0.2」；提案 :243 改「:31/:179 已改口，其余 7 处于 B 批次 delta 补标」。修后 grep `1.5 *dB` 全文零裸 [L1] |
| **F-2** | **MAJOR**（跨域不一致 SKILL §9） | dsp `S7_DSP_ASSESSMENT.md:120,127,111`：`M2_O1_EQ` / `g_m2_o1_built` / `g_m2_lim_clip_count`；testing `S7_VERIFICATION_PLAN.md:96,100,104,110,112`：`M2_EQ_INLOOP` / `g_m2_eq_built` / `g_m2_lim_clamp_count`；提案 :77-78 随 dsp | 同一 B1 阶段的宏名/指纹/计数器在设计稿与测试程序里是两套名字；测试员照计划 Expressions 读 `g_m2_eq_built` 会读不到（R52 stale-state 同类），提案 :244「命名沿用现有全局」对新增符号不成立 | 统一为一套（建议 dsp 版 `M2_O1_EQ` / `g_m2_o1_built` / `g_m2_lim_clip_count`，与 DEC-S5-EQ-O1-01 的 O1 命名对齐），计划 §1.2/§1.3/§9.2 同步；提案 :244 改口「新增符号以 dsp §1.2 命名为准」 |
| **F-3** | **MAJOR**（三口径混用，F60 纪律） | `S7_DSP_ASSESSMENT.md:73-74`「EQ-on/off 的 beam_cyc 差…**同时坐实 T2 账里 O1_contention_reserve=15 [L4]**」；提案 `:67` 同句 | T2 账（`H2_PASSLINE_DERIVATION.md` 步 5-9）把 O1 放在**固定侧 60 [L4]**，15 是**争用侧**预留（O1 对 DMA/ISR 的争用）。beam_cyc on/off 差 = O1 墙钟成本（含括号内一切），对应的是固定侧 60 的墙钟等价，**坐实不了争用预留 15**——测争用要 H2 型 both_max−base。这句话喂给 D1（解冻口径裁定），是 load-bearing 的口径错 | 改「EQ-on/off beam_cyc 差 = O1 墙钟成本 [L1]，可对照 T2 固定侧 O1 60 [L4]；争用预留 15 [L4] 须 H2 型 both_max−base 另测，B1 不坐实它」。提案 :67 同步 |
| F-4 | MINOR | `S7_ALGO_UPGRADE_PROPOSAL.md:185`；`S7_DSP_ASSESSMENT.md:448` | 「T2 账说装得下，墙钟表说装不下——**矛盾**的根子…」：DEC-S6-M2-BOARD-PASS-01 F60-MAJOR-1 原文「三口径互不可比…不得相互称矛盾/达标」；本包 §1 表还自引了这条。未相加、随即写「不可互证」，属措辞违规 | 改「两口径答案不同、不可互证；差异归因于未拆的 1.79×」 |
| F-5 | MINOR（口径） | `S7_VERIFICATION_PLAN.md:179` | ①「需 WNG 约 −43dB（绝对）/ −59dB（相对均匀）」错配：WNGa−WNGn 恒差 12.04 dB，−43 WNGa ↔ −55.0 WNGn；−59.3 WNGn 是 ε→0 天花板（WNGa −47.3），不是 −43 的对应值（LESSON-012 那类 12 dB 口径坑）；②「BW@1k = 29.28°…0.72°」与全包 29.27/0.73 不同（R5 旧舍入） | ①改「+1.9 dB 需 WNGa −40.8 / WNGn −52.8；天花板 +1.95 dB @WNGa −47.3 / WNGn −59.3 [L2 s7_lowfreq_superdir.log:78-81]」；②统一 29.27/0.73 或注「R5 原文 29.28」 |
| F-6 | MINOR | `S7_ALGO_UPGRADE_PROPOSAL.md:17,24,193-200` | 「本轮做（按顺序，不可换）」的 1/2/4 项都含 M2 TU 或 EQ 适配代码，而本轮硬约束是「只出方案不写算法代码」。§5.1 门列有「dsp 实现 → 独立 critic → CTO 批」，实质不冲突，但没有一句显式界定 | §5 开头加一句：「'本轮做' = 建议 CTO 批准后的实施顺序；**本提案本身零代码**；每项实施前另过独立 critic §12 + CTO 批（D2/D3/D4），未批不动」 |
| F-7 | MINOR | `S7_DSP_ASSESSMENT.md:356-357` | 「F7 每段 6,291 cyc，理想 MAC 仅 588 → **≥91%** 是编排+DMA+自旋+postscale」：按其自己的分类（非理想-MAC 全归此项），份额恰 = 1−588/6291 = **90.7%**，是等号不是 ≥；若把引擎低 CE 的 DMA 时间从「编排」里剔出，则该份额只会更小（≤）。方向写反 | 改「≈91%（=1−588/6,291，上界；引擎 CE<100% 的部分含在内）[L3]」 |
| F-8 | MINOR | `S7_ALGO_UPGRADE_PROPOSAL.md:185`；`S7_DSP_ASSESSMENT.md:457` | 「若 B6.3 回收…基线回到 ~463–530k，则 B1+B2+B4 全部落在 2× 以内」：高端增量 217,598 下，基线 530k → 1.78×、463k → 1.96×；只有低端 80,270 才 ≥2.45×。**承重结论（仍 ≥1.5×，747.6k < 888.9k）成立**，「2×」是溢写 | 改「B1+B2+B4 高端 1.78–1.96×、低端 ≥2.45×，均不触发解冻条件」 |
| F-9 | MINOR | `S7_ALGO_UPGRADE_PROPOSAL.md:23` | §0 ③「chmap 与极性是 B2/B4/B5 共同前置；错位映射会让聚焦增益损失 4–13 dB」：4–13 dB 是 §6.2 **仅对 B2（逐通道延时）**的结果；B4/B5 是标量权重，权重下标置换仍等价（τ≡0 控制臂），其前置理由是「权重贴错位置上调窗无意义」 | 拆成两句：B2 前置理由 = 4–13 dB [L2]；B4/B5 前置理由 = 现旁瓣 −9.67 dB 主因是错位 [L2] |
| F-10 | MINOR（措辞） | `S7_ACOUSTIC_SIM_REPORT.md:150` | 「设计 A 实得 14.96° 与解析下限 14.63° 相差 0.33°…**证实下限成立**」：有限候选族搜索没跌破一个近似（小角 BW∝λ；Dolph BW@2k 14.515 < 29.27/2 说明它是近似）下限，不构成「证实」 | 改「与解析（小角近似）下限一致，差 0.33°」 |
| F-11 | MINOR（L 标） | `S7_DSP_ASSESSMENT.md:47,366` | 「`.cproject:39` 无 value = 默认关 [L1 文件]」：「无 value」是 L1 文件事实，「= 默认关」是 CDT 默认值推断 [L3]；「整数算术与优化等级无关，bit-exact 不受影响」是无标 [L3] 断言（前提 = 无 UB），D2 已挂板门重跑，但句子本身该带标与验证钩子 | 改「无 value [L1 文件] → 按 CDT 默认推断为关 [L3]」；「bit-exact 不受影响 [L3，前提无 UB；以 M2_SELFTEST 八锚验证]」 |
| F-12 | MINOR（同源纪律） | `S7_DSP_ASSESSMENT.md:371-372`；提案 :152 | bench 内建 `fira_tree_probe.c` = 冻结 `fira_tree.c` 的**第二份副本**——A 批次刚清理过松散副本。已有 FG（副本 F4/F5 锚逐位同）和「产品 build 不含」，缺登记 | 加一条：副本在 bench `MANIFEST`/README 登记「诊断专用、随冻结件变动同步或删除、不进产品 build」 |
| F-13 | INFO | `S7_ALGO_UPGRADE_PROPOSAL.md:187,233`（D12） | 「~130µs 基数不可独立溯源」——文字出处存在：`sprint6/dsp/audio/m1_cces_project/src/m1_loopback_tdm.c:572`「~130us (H2 account, off-board caliber)」、`sprint6/STAGE4_ALGORITHM_VALIDATION_TEST.md:61`「纯核~130µs[L2]」；它是离板账，与 H2 实测 base 455 µs 不是一回事 | D12 的加注写明这两处出处 + 「跨口径比，同口径 = 1.79×（F7）/1.83×（H2 base）」 |
| F-14 | INFO | `sprint7/sim/dsp/s7_dsp_compute_ledger.py:87`；dsp :6,:30 | 脚本 `int(T2_LINE_CYC)` 打印 888,888，文表写 888,889；dsp 自称「输出即本文各表逐位」 | 脚本改 `round()` 或文注「线取整」 |
| F-15 | INFO（C10） | `S7_VERIFICATION_PLAN.md:50-56,316-320,355` | P2 含拆喇叭端子、1.5V/9V 瞬触、改线；§0.5 有功放断电/最小音量/Load→Run 纪律，但没指向 `sprint6/STAGE4_BRINGUP_CHECKLIST.md` 的 JTAG 顺序/禁热插拔硬规矩。板已 bring-up、版本已确认（DEC-S6-M2-BOARD-PASS-01），C10 判 PASS | §0.5 加一行「板侧上电/JTAG 顺序按 STAGE4_BRINGUP_CHECKLIST.md，不重述」 |
| F-16 | INFO | `S7_VERIFICATION_PLAN.md:238`（B6-7） vs `S7_DSP_ASSESSMENT.md:371`（B6.3 ④） | 计划写「只能在 M2 侧对 analyze/synthesize 各加括号，真拆需 CTO 批触碰冻结文件」；dsp 走 bench 副本 + CCNT 三段。提案采 dsp 法，未说明计划的 B6-7 已被取代 | 提案 B6.3 行加「计划 §6 B6-7 的 M2 侧分段括号作为补充，不作主法」 |
| F-17 | INFO | `S7_DSP_ASSESSMENT.md:90` | B1 低端按 8.51 cyc/MAC（int flat-FIR）估 float DF1 biquad：SHARC+ 单周期 float MAC 下 2 个 biquad×64 样本可能只需 ~1–2k cyc，低端 6,728 不是地板；已标 [L3] 且区间宽，无决策影响 | 可注「低端非下界」 |

**红线门（C1/C2/C3/C6/C7/C8/C9①②/C10）**：C7 FAIL（F-1，兼触 C2）→ 整体 BLOCKER。其余红线无 FAIL。

---

## 2. 逻辑链核（推荐组合每条是否由证据推出）

| 推荐 | 证据链 | 判 |
|---|---|---|
| B6.3 第一 | 830,903 vs 463,273 同口径差 367,630 [L1-derived] > 全部候选高端和 217,598；B2 单项用 [L1] 低端即越线（896,274 > 888,889）；假设 b（Debug −O0）零成本可证伪 | **推得出**。补：理由应写成「配置假设会同时改变 B1 增量与基线」而非「O1 实测数不可解释」（增量本身可解释，不可解释的是余量是否越线）——措辞级，并入 F-6 |
| B6.4/B6.5 基座 | DEC-S6-M2-BOARD-PASS-01「功能 PASS ≠ bit-exact 已验」；fw 审计 6 宏 5 无指纹；`M2_STATIC_TXTEST` 无 `#error` | 推得出 |
| P0→P2→P1 零代码 | L0 隔离登记（DEC-S7-OBS-OWNRIG-01）升 L1 路径；自家极性从未验（CLOSURE §5.3）；chmap 远场 A/B 是 lock 硬门（`m1_loopback_tdm.c:388-394`） | 推得出 |
| B1 本轮做（排 B6.3 后） | 冻结令例外件（decisions_log:725）；高端 1.510× 刀刃；零触碰冻结件；FG 三件套设计过 §12 形态 | 推得出（F-6 加界定句） |
| B2 下轮 | [L1] 低端越线 → 按墙钟口径触发解冻条件 → 须 CTO 裁 D1；两个声学前置未闭 | 推得出 |
| B3 不做 | 阵因子纯实偶 [L1 拓扑]；硬件叉 Gate-2；栅瓣 30° 时 4,158 Hz 压到 v1 有用带边缘 [L3 复算一致] | 推得出 |
| B7 不做 | 须触碰冻结 `fira_tree.c:481` 自旋；量级 [L4]；冻结令 ORCH 全停 | 推得出 |
| B4 挂起 | 假设地板下 1k 29.27→22.66 但 att30 13.2–13.5 → 一级掉三级 [L2 复算一致]；纹波未量化（归 DSP）；MC 未做 | 推得出 |
| B5 不换全频段窗 / 子带级挂起 | 双约束可行集只剩 Dolph −20…−21 [L2 双轨]；子带级 = DI@4k −4.35、3–6k 轴向 −9.87 换平坦度 9.5° [L2 单轨]；产品要不要均匀性待 B6.10 | 推得出 |

过度声明扫描（证明/一定/完美/排除/最实/证实）：dsp :121「可证明性」（24-bit 左对齐→float32 精确可逆，数学成立）、:190/:200/:234「等价证明」（指代码注释推导/m3 三轨结论/测试设计）、:397/:457「若 B6.3 证明」（条件句）——**均非过度声明**；仅 acoustic :150「证实」（F-10）。「一定/完美/排除/最实」零命中。

---

## 3. C1–C10 + §12 逐门

| 门 | 结论 | 证据 |
|---|---|---|
| C1 标 L 级 | **PASS（带保留）** | 提案/dsp/计划/声学四文承重数字均带 L 标；声学表格行继承节标 [L2/numpy]（中间量不强制）。保留：F-1 的 5 处 1.5 dB 无标、F-11 两处推断无标 |
| C2 不越级称实测 | **FAIL → BLOCKER（与 C7 同源，F-1）** | `S7_VERIFICATION_PLAN.md:119,310` 把 A 批次已裁「未落盘 → 工作假设 [L4]」的 1.5 dB 标 `[L1]`。其余：grep「实测」在四文 23 处命中，全部是「须等 R3 实测/实测触发器/不得写成实测/R3 实测」类用法，无仿真值冒充实测；声学报告首页自禁「实测」定语且全文遵守 |
| C3 L4 不撑不可逆 | **PASS** | 包内无不可逆决策（提案可逆、D2 对照实验、M2 TU 改动 CTO-gated）；t_base 默认 1.0 明标「结构在保护不在」以避 0.8f [L4] 进产品 |
| C4 L3 撑强约束挂待验 | **PASS** | 无强约束决策；B2「越线」用 [L1] 低端；B6.3 假设 a–e 全标 [L3] 且以实验为出口 |
| C5 可追溯 / 双轨 | **PASS** | 承重数字第二独立工具核（本 critic numpy 全新实现）逐位吻合：ledger 全表、29.269/32.184/24.955/22.869/22.66/+1.947/−13.36/−13.21/−3.98/Σw −9.87/栅瓣四点/延时 122.2 µs·43.9 µs；声学 §7 MATLAB 轨确为独立实现（`s7_matlab_crosscheck.m` 自写 AF/BW/SLL/DI，chebwin 来自 MATLAB 非 CSV）；抽查行号 `fira_tree.c:481` 自旋 / `:697-708 (void)` / `m1_loopback_tdm.c:380-398,418-448,571-582` / `eq_test.c:77-84` / `focus_sim.py:17-21` / `h2_board_hooks:364 TODO` / `gen_f5_goldens.c:20 INSIDE` / `TEST1_FIELDLOG:24,74` / `EXP_STATIC_POL375:3` / `EXP_CHMAP_AB:22-31,79-80` **全部对得上**。缺口：F-2 跨域命名漂移（MAJOR，SKILL §9）、F-13 130µs 出处可补 |
| C6 几何门 / 冲突重审 | **PASS（N/A）** | 无几何 LOCKED；d=55 [L1] 消费未重推；dsp 对 DEC「6.4×」的异议走 D12 加注上 CTO，非「并存」 |
| C7 撤回传播 | **FAIL → BLOCKER（F-1）** | A 批次降标的 1.5 dB 在计划 :119/:310 残留 [L1]，5 处无标；铁律五「逐处加标」未完成；A 批次 delta 明文预告本项。撤回值（d=30/14.9/19.1/19.2/16.0）未作输入（声学 §10 自检 + 本 critic grep 零命中）；18 dB 归属正确（提案 :44） |
| C8 外部输入入库 | **PASS（ESCALATE 已正确挂出）** | B 批次无新外部输入；D9 把「CTO 接收声明 + 持有合法性」列入决策清单 = A 批次 F-4 的 ESCALATE 形式 |
| C9 FIRA 收益闸 | **PASS（N/A）** | B7 [L4] 100–200k 未计入任何选型/承诺；B2 高端用 1.794× 缩放标 [L3]；无选型/流片/承诺 |
| C10 硬件不可逆动作 | **PASS** | 板已 bring-up + 版本已确认；计划 §0.5 有功放断电/最小音量/Load→Run/限幅门先过纪律，P2 改线前功放断电、9V 瞬触。F-15 INFO 建议指向 STAGE4_BRINGUP_CHECKLIST |
| §12 FG1/FG2/IO1/IO2/ST1 | **N/A（无 bit-exact PASS 主张）；FG 设计合规** | B1：默认关字节等同 / unity 逐位等同（24-bit 掩码规则正确：低 8 位硬 0 的 Q31 在 float32 24 位尾数内精确）/ stub 必 FAIL；B2：focus_differs / zero_recovers（零延时跳过非乘 1）/ ST1-E 全消费者 / 尾巴 pin Block1；B6.4：子带 CRC 对八锚（非端到端）+ 桌面 stub 必全 0；FG 存在性→率/值在带升级已写入计划 §0.3 |

---

## 4. 跨文件数字一致性（计数：提案 / dsp / 计划 / 声学）

65,371 = 4/7/2/0 ｜ 830,903 = 6/5/1/0 ｜ 463,273 = 2/2/0/0 ｜ 888,889 = 2/2/0/0 ｜ 57,986 = 2/4/0/0 ｜ 1.794 = 2/3/0/0 ｜ 4.85 = 2/1/1/3 ｜ 8.09 = 1/1/1/4 ｜ 29.27 = 3/4/0/14（计划用 29.28 ×1，F-5）｜ 14.5 = 0/0/1/5 ｜ 24.96 = 0/0/0/3 ｜ 32.18 = 1/0/0/3 ｜ 22.66/22.7 = 提案 2、dsp 1、声学 3 ｜ 1.510 = 4/5/0/0 ｜ 1.488 = 3/4/0/0 ｜ −4.35 = 2/2/0/2 ｜ −9.87/−9.9 = 提案 2、dsp 3、声学 3 ｜ 15.0°/14.96 = 一致。**除 29.28 与 F-2 命名外无冲突**。§6 决策清单对照三份输入：dsp §10 五项 → D1/D2/D4/D5/D8；计划「rig 组成不猜」「竞品 rig 可用性不猜」→ D7；A 批次 F-4/F-5/F-16/F-21 → D9/D10/D11/D13；**无遗漏**。

---

## 5. 实跑命令与结果（全部只读）

```
git status --short                       → ?? deliverables/…/m2_static_txtest_table.h  ?? sprint7/docs/  ?? sprint7/sim/（无其它）
git diff --stat ; git diff --cached --stat → 均空
git status/log -- 12 冻结件 + m1_cces_project/.cproject .project → 无工作区变动；最后 commit ae4a837/44a99e8/9139de3/43aad40/4bf0f52/360ba7e/03d2172/cf0c34d/2e505b6
grep -rn -i "HIT9616|固件包|解包|firmware|反编译" sprint7/ → 仅 critic A 文件 + 提案 :6 自查 / :230 D9（零内容引用）
/usr/bin/python3 scratchpad/critic_B_recompute.py → 见 critic_B_recompute.log（ledger 全表 / 29.269 / 32.184 / 24.955 / 22.869 / 22.66 / +1.947 / −13.36 / −13.21 / −3.98 / 122.2µs / 43.9µs / 6236-5314-4647-4158 / Σw −9.87）
/usr/bin/python3 scratchpad/ledger_copy.py（dsp 脚本副本，只打印） → §A/§B/§C 与 dsp §0.2/§8 逐格同（唯 1.5× 线打印 888,888，F-14）
sed/grep 源锚：F7_CLOSING_RECORDS:154-156 (463,273 / 56,616 / CCLK 1e9) ; H2_READING_ANOMALY:9-13 (454,730) ; H1_FINAL_RULING:16-21 (65,371) ; TEST1_FIELDLOG:24 (829,218) :74 (span 3.2dB) ;
        m3_numpy_superdir_d55.csv (0.3→24.96/10.94, 0.01→22.87/4.57) ; sweep_d55_results.csv 1000/dolph20 29.269 ; dolph_w8_q15.csv 8 行 ; H2_PASSLINE_DERIVATION:16-23 (666.67/456.48/210.19) ;
        decisions_log:721 (O1 29–60 [L4]) :723 (T2 95.6≤210.19) :725 (冻结令/解冻条件) :1013 (DEC-S6-M2-BOARD-PASS-01 6.4×/F60) :1028-1031 (DEC-S7 三条 + housekeeping) ;
        EXP_COMPET:3 (顶注降标) ; FOCUS_EFFICACY:66-73,86-101,116 ; EQ_INTEGRATION_NOTE:60-70,105-116 ; eq_limiter.c:5-13 (5 MAC/biquad) ; F7_MARGIN_MATERIAL:29-56 ; .cproject:39,153 ;
        fira_fit_assessment:148 (4 MAC/cyc) ; h1_wcet_measure.c:25-49 (120 samp) ; tree_filterbank.h:5-41 ; m1_loopback_tdm.c:378-400,418-448,571-582 ; fira_tree.c:478-484,695-710 ;
        STAGE4_ALGORITHM_VALIDATION_TEST:61 + m1_loopback_tdm.c:572 (~130µs 出处) ; STEERING_HEADROOM_SCAN:38-42 ; BENCH_OPS_CARD:19 (-O1) ; M2_Q_BOUNDARY_SURVEY:197 (65282/65536)
grep 1.5dB/1.9dB/−43/0.7dB/13–16 in sprint7/docs → 计划 :31(已降标) :119[L1] :120 :179(已改) :195 :220 :306 :310[L1] :394 ；提案 :123 :231 :243
grep "实测" 四文 → 23 处，全为「须等 R3 实测/实测触发器/不得写成实测」类；grep 证明|一定|完美|排除|最实|证实 → 见 §2
awk s7_lowfreq_superdir.csv quasi rows → pair8_vs_16 max 3.02e-08 @250Hz（报告「3e-8」= 跨频最大值，成立）
ls -la --time-style sprint7/sim/acoustic → .m 18:50 → matlab_crosscheck.csv 18:54 → dualtrack_compare.csv 18:54（MATLAB 轨确实跑过；本 critic 未重跑）
```

---

## 6. 认可项（如实记）

- 算力台账把「墙钟 / 争用 ledger / 纯核」三口径分开、只用墙钟并列 T2 不相加，且用 [L1] 低端就得出「B2 单项越线」——这是本包最硬的一条结论，我独立算术逐格复现。
- 声学报告的锚点先断言后出数（A1–A8 + m3 三轨 + S5 六格 + 8 对≡16 元）与 §6.2 的 τ≡0 控制臂，是 LESSON-008/012 纪律的正确形态；我的全新实现与之逐位吻合。
- 对 DEC「6.4 倍」的异议走「登记读法、不改原文、上 CTO 加注」，是铁律四的正确用法。
- 验证计划 §10「现 rig 诚实做不到的事」13 条与 §0.1「③ 相对证据永不写成规格」把 L1-相对 与 L1-规格 分开，防了 PF-1 类越级。

---
*reviewer: critic @ claude-fable-5-1 / 2026-09-02 — FAIL（BLOCKER ×1 F-1 / MAJOR ×2 F-2·F-3 / MINOR ×9 / INFO ×5）。修 F-1（改标 2 行 + 补注 5 行 + 提案 :243 改口）与 F-2/F-3 后 delta 复审；其余 MINOR 建议同批一句话修。只读审计，未改仓库/暂存区/记忆。*

---

# Delta 复审（2026-09-02，reviewer: critic @ claude-fable-5-1；只读，未改仓库/暂存区/记忆；未重跑 sprint7/sim 脚本，台账脚本以副本 `scratchpad/ledger_copy2.py` 跑）

**最终裁定：PASS（带 INFO ×2）。** 初审 1 BLOCKER + 2 MAJOR + 9 MINOR + 5 INFO 全部核实已修；红线门 C1/C2/C3/C6/C7/C8/C9/C10 无 FAIL；C7/C2 的 F-1 残留清零。可 commit。

## D1. 初审 findings 逐条核销

| ID | 状态 | 核实证据 |
|---|---|---|
| **F-1** | **已修** | 计划里 `1.5 *dB` 命中 8 行（:31/:120/:121/:196/:221/:307/:311/:395），逐行判：**全部带 [L4]/未落盘**（awk 判定 8/8）；:120/:311 判据行改「[L4 工作假设，未落盘，见 §0.2]」；其余 5 行加「（工作假设 [L4]，见 §0.2）」。`grep -rE "1\.5 ?dB *\[L1" sprint7/` 唯一命中 = `critic/CRITIC_A_HOUSEKEEPING_20260902.md:28`（A 批次裁定原文引述改前状态，历史记录，非活引用）。提案 :245 改口为「共 8 处：:31/:179 A 批次先改，其余 7 处 B 批次补标」——与实况一致 |
| **F-2** | **已修** | 旧名 `M2_EQ_INLOOP` / `g_m2_eq_built` / `g_m2_lim_clamp_count` 三文 grep = 0/0/0；计划改用 `M2_O1_EQ`(1) / `g_m2_o1_built`(2) / `g_m2_lim_clip_count`(3)，与 dsp(3/3/4)、提案(2/2/2) 一致；提案 :246 加「新增符号…以 dsp §1.2 命名为准，验证计划已同步」 |
| **F-3** | **已修** | dsp :73-74、提案 :67 均改为「beam_cyc 差 = O1 墙钟成本，对照 T2 **固定侧** O1 60 [L4] 的墙钟等价；**争用侧** 15 须 H2 型 both_max−base 另测，B1 不坐实它」，固定侧/争用侧口径分清 |
| F-4 | 已修 | 提案 :185、dsp :448 改「两口径答案不同、不可互证（F60 纪律：不称矛盾）」；剩余「矛盾」各 2 处均为引述规则本身（提案 :46 表、dsp :23） |
| F-5 | 已修 | 计划 :180「+1.9dB 需 WNGa −40.8 / WNGn −52.8；天花板 +1.95dB @WNGa −47.3 / WNGn −59.3 [L2 …log:78-81]」——与本 critic 复算逐位同；29.27/0.73 + 注「R5 原文 29.28/0.72 为旧舍入」 |
| F-6 | 已修 | 提案 :195 界定句「'本轮做' = 建议 CTO 批准后的实施顺序；本提案本身零代码；每项实施前另过独立 critic §12 + CTO 批（D2/D3/D4），未批不动」 |
| F-7 | 已修 | dsp :356「≈91%（= 1−588/6,291，上界；引擎 CE<100% 的 DMA 时间含在内）」 |
| F-8 | 已修 | 提案 :185 ②、dsp :457 改「高端 1.78–1.96×、低端 ≥2.45×，均不触发解冻条件」——与复算 1.783/1.958/2.453 一致 |
| F-9 | 已修 | 提案 :23 拆为 B2 理由（4–13 dB [L2]）与 B4/B5 理由（−9.67 dB 错位 [L2]） |
| F-10 | 已修 | 声学 :150 改「与解析（小角近似）下限一致」；该行现「相差 0.33°…差 0.33°」重复一次（措辞，INFO-2） |
| F-11 | 已修（dsp） | dsp :47「无 value [L1 文件] → 按 CDT 默认推断为关 [L3]」；:366「[L3，前提无 UB；以 M2_SELFTEST 八锚验证]」。提案 :152 B6.3 行仍保留无标的「整数算术与优化等级无关，bit-exact 不受影响」（初审只点了 dsp；提案是摘要，dsp 已带标与验证钩子）→ INFO-1 |
| F-12 | 已修 | dsp :372「同源纪律登记：副本须在 bench MANIFEST/README 登记为诊断专用、随冻结件变动同步或删除、不进产品 build」；提案 :152 同句 |
| F-13 | 已修 | 提案 :187 与 D12(:235) 写明 `m1_loopback_tdm.c:572` / `STAGE4_ALGORITHM_VALIDATION_TEST.md:61` 两处出处 + 同口径比 1.79×(F7)/1.83×(H2 base) |
| F-14 | 已修 | `s7_dsp_compute_ledger.py:87` `round(T2_LINE_CYC)`；副本实跑打印 888,889 / 57,986 / 表 §C 与初审逐格同 |
| F-15 | 已修 | 计划 §0.5 第 6 条「板侧上电 / JTAG 连接与断开顺序、禁热插拔、BMODE 全 0，按 `sprint6/STAGE4_BRINGUP_CHECKLIST.md` 执行」 |
| F-16 | 已修 | 提案 :152「验证计划 §6 B6-7 的 M2 侧 analyze/synthesize 分段括号作为补充非主法」 |
| F-17 | 已修 | dsp :90「低端非下界，SHARC+ 单周期 float MAC 下可能更低」 |

## D2. Delta 复跑（只读）

```
git status --short                         → 仍仅 ?? deliverables/…/m2_static_txtest_table.h  ?? sprint7/docs/  ?? sprint7/sim/；git diff --stat 空（冻结件/.cproject/.project 零变动）
ls --time-style sprint7/sim/acoustic/*.csv → 全部 18:46 / 18:54 未变（脚本未重跑）；S7_ACOUSTIC_SIM_REPORT.md 19:21 仍 369 行、关键数字行计数不变
grep -n "1\.5 *dB" S7_VERIFICATION_PLAN.md | awk tag-judge → 8/8 行 L4/未落盘；grep -rE "1\.5 ?dB *\[L1" sprint7/ → 仅 critic A 历史引述 1 处
grep 旧名 M2_EQ_INLOOP|g_m2_eq_built|g_m2_lim_clamp_count 三文 → 0
grep 矛盾 → 提案 2 / dsp 2，均为规则引述
python3 scratchpad/ledger_copy2.py → 1.5x line 888,889；to-line 57,986；§C 表与初审同
sed 全文核对：计划 :120,:121,:180,:221；提案 :23,:67,:152,:185,:195,:235,:245,:246；dsp :47,:74,:90,:356,:366,:371-372,:448,:457；声学 :150
```

## D3. 剩余（均不阻 commit）

| ID | 严重度 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| INFO-1 | INFO | `S7_ALGO_UPGRADE_PROPOSAL.md:152` | B6.3 行「整数算术与优化等级无关，bit-exact 不受影响」无标（dsp :366 已带 [L3，前提无 UB；以 M2_SELFTEST 验证]） | 同句补「[L3，见 dsp §6.3 b]」 |
| INFO-2 | INFO | `S7_ACOUSTIC_SIM_REPORT.md:150` | 「相差 0.33°…差 0.33°」重复 | 删一处 |

## D4. C1–C10 + §12 delta 结论

C1 PASS ｜ **C2 PASS**（1.5 dB 8 处全为 [L4]/未落盘，无越级）｜ C3 PASS ｜ C4 N/A ｜ C5 PASS（跨域命名统一；130µs 出处补齐；副本登记句在）｜ C6 N/A ｜ **C7 PASS**（降标传播 8/8 完成，唯一 [L1] 残留是 critic A 文件的历史引述）｜ C8 留痕 PASS + ESCALATE 已挂 D9 ｜ C9 N/A ｜ C10 PASS（§0.5 第 6 条指向 bring-up 清单）｜ §12 N/A（FG 设计合规，未变）。

**最终：PASS（带 INFO-1/INFO-2）。可 commit。** 提交时建议同 commit 落本裁定文件（含本 delta 节，首行 reviewer 标保留）并在 decisions_log 追加 `reviewer: critic @ claude-fable-5-1 / 2026-09-02 FAIL(1 BLOCKER)→全修→delta PASS` 行。

---
*reviewer: critic @ claude-fable-5-1 / 2026-09-02 — delta 复审 PASS（带 INFO ×2）。只读审计，未改仓库/暂存区/记忆。*
