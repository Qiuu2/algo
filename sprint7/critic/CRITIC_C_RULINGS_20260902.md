reviewer: critic @ claude-fable-5-1 / 2026-09-02

# Critic C verdict — CTO 2026-09-02 裁定落库批次（DEC-S7-RULINGS-01 / DEC-S7-IMPL-01 / D12 注 / KB D9 / SKILL:58 D13 / D11 rm）

**被审对象**：工作树未暂存 `git diff`（3 文件：`sprint2/docs/decisions_log.md` +18/−0、`knowledge_base/competitor/KB-EXT-SPON-HIT9616A12_FIRMWARE_REG.md` +2/−2、`.claude/skills/testing/SKILL.md` +1/−1）+ 未跟踪 `deliverables/algorithm_validation/m2_static_txtest_table.h` 已 rm。
**审法**：只读；逐条对照 team-lead 转来的 CTO 原话；关键出处与算术全部本机实跑复核（命令见 §5）。

---

## 0. 总裁定

**CONDITIONAL（打回修 5 MAJOR 后 delta 复审；未过 delta 不得 commit）**
0 BLOCKER / **5 MAJOR** / 6 MINOR / 5 INFO。红线门 C1/C2/C3/C6/C7/C8/C9/C10 无 FAIL；**C5 FAIL（MAJOR）**。

一句话：CTO 明确裁定的条目（D1/D2/D3/D4/D7/D9/D10/D11/D12、push 许可、实施第一步范围）**无漏项**，D12 注与 D9/D11 处置**实核全对**；问题集中在两处 PM 加工——① **B5「不做」vs 提案「B5-2 挂起」被糅成一句**、未标待确认，且「候选总处置」整行无标签（含 B1/B6.1/B6.2「本轮做」）= CTO 明令禁止的「默认通过」；② **DEC-S7-IMPL-01 把 PM 实施细则整体标成「CTO 裁定」**，其 B6.3 三段括号定义与 CTO 批准的提案 B6.3 ④ 不同且拆不出忙等，另把 D3 未列的 M2 TU 改动（raw 读数/板上括号）挂在「D3 改动包」名下。SKILL:58 一处把 testing 自定的「3dB 工作假设」归到 D10 裁定、出处指错。

---

## 1. Findings

| # | 严重度 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| F-1 | **MAJOR** | `decisions_log.md:1042` D6；`:1051` 候选总处置 | CTO 原话「B5 不做…全部照提案」，而提案 §3 B5（:144）与 §6 D6（:229）/§4（:212）是**拆两半**：全频段换窗**不做**、**B5-2 子带级恒定波束宽挂起**（待 B6.10 竞品对比定）。PM 写成「B5 不做（全频段换窗零收益；子带级恒定波束宽挂起）」= 同一条里既「不做」又「挂起」，自相矛盾；:1051 总处置再写「B3/B5/B7 不做」把「挂起」抹掉。差别有下游后果：B5-2 若「不做」，D7 里「竞品整机可用于对比实验（B6.10）」与 B6.10「决定 B5-2 立项与否」失去目的。这是 CTO「不要有默认通过的条目」直接命中的歧义，PM 无权替 CTO 二选一 | D6 拆成两行：「B5-1 全频段换窗 不做【CTO 裁定，照提案】」/「B5-2 子带级恒定波束宽：CTO 口头「B5 不做」与提案「挂起（待 B6.10）」不一致 → **待 CTO 确认**」；:1051 同步改「B5-1 不做 / B5-2 待确认」 |
| F-2 | **MAJOR** | `decisions_log.md:1051`「候选总处置」 | 整行无「CTO 裁定/拟处置」标签，含三项 CTO 原话没说的：**「B1 本轮做」**（CTO 只裁 D4 t_base + 「不得在 B6.3 出结论前启动」+ 实施第一步「不要开始 B1」，未说「B1 本轮做」）、**「B6.1 本轮做」**（chmap 远场 A/B；D8 翻宏尚待确认，D7 只裁 rig）、**「B6.2 本轮做」**（实施第一步只批「零代码准备」，QA 本身未批）。= 默认通过 | 每项挂标签：B1「D4 隐含、启动待 B6.3 结论、**是否本轮实施待 CTO 明确**」；B6.1「测试按 D7 rig，翻宏按 D8 待确认」；B6.2「本实施步仅零代码准备（IMPL-01 第 3 项）」；B6.3/6.4/6.5「CTO 裁定 D2/D3」；B5 见 F-1 |
| F-3 | **MAJOR**（C5） | `decisions_log.md:1052` DEC-S7-IMPL-01 (1) a–d | 条目头标「CTO 裁定」，但 CTO 原话只有范围一句（三项 + 六条硬约束）；a–d 细则、产出文件名 `S7_B63_WALLCLOCK_GAP.md` 全是 PM 加的。且 **(1)b 三段括号 =「加权乘法 / analyze / synthesize」**，全库仅此一处，与 CTO 通过 D2 批准的提案 B6.3 ④（:152）/ dsp §6.3（:371）**「QueueTask→DONE 自旋 / postscale / memcpy」不同**——后者直接把加速器忙等隔离出来，前者按流水级切、每级仍各含 FIRA 段自旋，**拆不出 WO-S6-BEAMCYC-SPLIT 要的「compute vs 忙等」**（DEC-S6-M2-BOARD-PASS-01 原文点名的目标）。(1)c「板上侧同样三段括号」把提案明写「作为补充非主法」（critic-B F-16 后加）的 M2 侧括号升为主法。(1) 还漏了提案 ①「`g_m2_beam_cyc_last` + `_min`/次大值」与 ③「scratch pin Block1（假设 c）」两条零成本证伪 | 条目拆成「**CTO 范围（逐字）**」+「**PM 实施细则（按提案 B6.3 ①–④，待实施前 critic）**」两段；(1)b 恢复提案三段（自旋/postscale/memcpy）或写明为何改；(1)c 标「补充非主法」；补 ①③；若 CTO 另有口头细则，注明「CTO 口头 2026-09-02」 |
| F-4 | **MAJOR** | `decisions_log.md:1052` IMPL-01 (1)a「新增 raw 读数」、(1)c「走 D3 TU 改动包」 | CTO D3 的 CTO_OK=1 **只列三项**：`M2_SELFTEST` 八锚 / 6 宏指纹 / `M2_STATIC_TXTEST` `#error`。raw 读数（`_min`/次大值全局）与板上三段括号是**另外的 M2 TU 改动**，提案自己标「M2 TU 加 raw 读数 CTO-gated」。IMPL-01 把它们说成「走 D3 TU 改动包」= 用 D3 的 CTO_OK 覆盖 CTO 没点头的字节变动（D3 落库行 :1039 本身忠实，问题在 IMPL-01 的引用） | (1)a/(1)c 改「M2 TU 加 raw 读数 / 括号 = **CTO-gated，D3 未含，需单独 CTO_OK**」；或请 CTO 明示把 D3 扩到含 raw 读数（那也要落一行「D3 扩展」） |
| F-5 | **MAJOR**（C5） | `.claude/skills/testing/SKILL.md:58` | 括号内「2026-09-02 D10 裁定：…；**判据一律用「2× 地板 = 3dB 工作假设 [L4]」**」——CTO D10 原话只有「4 个数字保持未落盘，不升级」，**没有 3dB / 2× / 一律**。3dB 的真实出处 = `sprint7/docs/S7_VERIFICATION_PLAN.md:31`（testing 自定，critic-B F-1 原文「本计划 :31 …自定」），而行尾出处指向「EXP_COMPET 顶注」，顶注里没有 3dB。且「一律」与该计划自己的判据不符（:121/:221 用 1× 地板「> 1.5dB」，:144/:158/:188 才用 2×=3dB）。= 替 CTO 补数字 + 出处指错 | 改为「…不升级）；判据用几倍地板由各实验自定（S7_VERIFICATION_PLAN.md:31 取 2× = 3dB 工作假设 [L4]，testing 自定，非 CTO 裁定）」；出处补 `S7_VERIFICATION_PLAN.md:31` |
| F-6 | MINOR | `decisions_log.md:1046` D10 括号「1.9dB/−43dB 的 [L2] 复算另计，不改该文标注」 | 提案 D10 明问「1.9/−43 已由本轮仿真复算可升 [L2]」，CTO 答「不升级」；PM 在「CTO 裁定」行内加「另计」是自己的调和（sim 报告 §5.4 的 [L2] 值有独立出处，调和本身站得住，但不是 CTO 说的；`S7_VERIFICATION_PLAN.md:180` / 提案 :123 已按 [L2] 口径写） | 移出裁定句，改「PM 注：sim 报告 §5.4 的 +1.95dB/−40.8dB 为独立 [L2] 出处，EXP_COMPET 原标注不动；**是否与「不升级」冲突请 CTO 一并确认**」 |
| F-7 | MINOR | `:1037` D1 尾句「三口径互不可比纪律不变，T2 账继续只并列参考」；`:1043` D7 括号「极性 QA 为硬前置」「B6.10 / 07-01 重做」 | 均非 CTO 原话（D1 尾句是 DEC-S6 既有纪律的复述 + PM 对 T2 的定位；D7 括号来自提案选项描述）。内容无错，但挂在「CTO 裁定」标签下 | 各加「（PM 注）」或移到句尾括号注明出处（DEC-S6-M2-BOARD-PASS-01 / 提案 D7） |
| F-8 | MINOR | `:1041` D5 | CTO「B2 推下轮…全部照提案」已覆盖提案 D5 全句（含「本轮只做不写固件的准备」），PM 却标「拟处置…待 CTO 确认」又写「CTO 已批」，标签打架，会让 CTO 重裁一次 | 改「CTO 裁定（照提案 D5）：B2 推下轮；准备工作本实施步不启动（实施第一步「其他候选一律不动」）」 |
| F-9 | MINOR（铁律五状态位） | `:1045` D9；`:1031` DEC-S7-EXTINPUT-HIT9616-01；KB §3 标题 | D9 未点名 `DEC-S7-EXTINPUT-HIT9616-01`（提案 D9 原文点了）；:1031 仍写「C8 状态 = 偏差留痕、未闭合…ESCALATE」无向前指针；KB §3 标题仍「接收声明基线缺失（ESCALATE 项）」。LESSON-011 案例 B 同型（状态变了、引用处没传播） | D9 加 DEC ID；:1031 后加一行 `*↑ [注 2026-09-02 D9] C8 → 来源已补、授权待确认*`（D12 式，不改原文）；KB §3 标题可加「（2026-09-02 D9 后：部分闭合）」 |
| F-10 | MINOR（铁律五状态位） | `deliverables/algorithm_validation/EXP_COMPET_BEAM_VS_FREQ.md:3` 顶注 | SKILL:58 把顶注引为 D10 状态出处，但顶注写于 D10 之前，仍写「出处待补」「将列入决策清单」；CTO 已裁「有测量但无单独原始记录、不升级」= 「待补」已知补不出 | 顶注末加一句「↑ 2026-09-02 D10：07-09~15 有测量无单独原始记录，4 数维持未落盘、不升级」（不改正文） |
| F-11 | MINOR（六字段） | `:1036` RULINGS-01 头；`:1052` IMPL-01 头 | RULINGS-01 称「不引新数字」但 D2/D6 带标引用数字；两条均缺**验证状态 / 风险声明**，IMPL-01 还缺数据出处。IMPL-01 该写的风险：Release/−O 对照 build 是**另一份二进制**，其 beam_cyc 读数须带 build 指纹、**不替代 Debug 基线 830,903**、若改产品配置须 M2 板门重跑（提案 D2 原句） | 各补一行「验证状态=会话裁定/未板验；风险声明=…」（SCOPE-01 先例可容，故 MINOR） |
| F-12 | INFO | `:1036`「除 D11 外均可逆」 | D11 删的是 tracked `sprint6/dsp/audio/m1_cces_project/src/m2_static_txtest_table.h` 的逐字节副本（本机 md5 `f78b1dcc7551ab432022c209ea5a4af0` 与 critic-A 记录同），随时可恢复 → 可逆 | 改「均可逆（D11 副本可由 src 版恢复）」 |
| F-13 | INFO | KB §1「CTO 2026-09-02 口述」 | log 用「会话内裁定」，KB 用「口述」，同一事实两种说法 | 统一为「会话内裁定」 |
| F-14 | INFO（流程） | 工作树 `sprint7/docs/S7_POLARITY_QA_RUNBOOK.md`（未跟踪，mtime 22:21:21，本审首次 `git status` 之后出现，应为并行实施 agent 产物） | 不在本批范围；但落库 commit 时**不得顺手 `git add` 它**——按 commit discipline 它要有自己的独立 critic verdict（含 C10：电池瞬触/功放断电/JTAG 顺序引 `STAGE4_BRINGUP_CHECKLIST.md`） | commit 用显式路径 `git add <3 文件>`，不用 `git add -A` |
| F-15 | INFO | IMPL-01 (1)a「Release 或手动开 −O」 | `.cproject` **已有** Release 配置（:118–153，`-O` value=true），Debug 配置 :39 `-O` 无 value（默认关）→ 假设 b 成立可能性合理，且对照 build 不需要改 `.cproject`。但 CDT 切配置有时会重写 `.cproject` | runbook 写明：CCES 选 Release 配置即可；build 后 `git status` 若见 `.cproject` 变动**一律 `git checkout -- .cproject`**，不入库（CTO「不动 .cproject」） |
| F-16 | INFO（正向） | `:1014` D12 注 | **全部实核通过**：`m1_loopback_tdm.c:572` 原文「Beam compute ~130us (H2 account, off-board caliber)」✓；`STAGE4_ALGORITHM_VALIDATION_TEST.md:61`「纯核~130µs[L2]」✓；830903/463273=1.7935→1.79 ✓；830903/454730=1.8272→1.83 ✓；454,730 [L1 EZKIT] `decisions_log:722` ✓、CCLK 1e9 [L1] `F7_CLOSING_RECORDS:156` → 455µs ✓；F7 括号 `fira_regression.c:604-618` = main 上下文 8ch weight+analyze+synthesize 含 spin ✓；`BENCH_FRAME=64`（`bench_harness.h:31`）= M2 帧 64 样本/1.333ms → **同口径成立** ✓；原条目 :1013 零字符变动（diff 18+/0−）✓；引用 dsp §0.3 与 critic-B F-13 均存在且内容一致 ✓ | 无 |

---

## 2. CTO 原话逐条对照

| CTO 原话 | 落库 | 判定 |
|---|---|---|
| D1 墙钟口径判 1.5×；理由=帧 deadline 实际约束、比 T2 保守 | :1037 D1 CTO 裁定，理由逐字 | 忠实；尾句 PM 加（F-7） |
| D2 批准 B6.3 对照实验 | :1038 CTO 裁定（附 830,903/463,273 [L1]、1.79×） | 忠实；数字带标、可溯提案 |
| D3 批准 M2 TU 改动包（八锚/6 宏指纹/#error），CTO_OK=1 | :1039 CTO 裁定，三项逐字，CTO_OK=1 | 忠实（IMPL-01 越界引用见 F-4） |
| D4 t_base 1.0 + 标注；B1 不得先于 B6.3 结论启动 | :1040 CTO 裁定 | 忠实 |
| D7 自家 16 元；竞品整机可对比 | :1043 CTO 裁定 | 忠实；括号 PM 加（F-7） |
| D9 来源=同事自 SPON；渠道/授权未确认；授权栏「未确认」；三不变；C8 闭合到可闭合程度 | :1045 + KB §1/§3 | 忠实；KB「授权状态：未确认」✓「不解包、不分析、不参考」§2/§3 ✓；缺 DEC ID 指针（F-9） |
| D10 有测量无单独原始记录；4 数保持未落盘不升级 | :1046 | 忠实；括号 PM 调和（F-6）；SKILL:58 越写（F-5） |
| D11 删未跟踪副本 | :1047 + 已 rm；`git status` 无其它变化 | 忠实 |
| D12 加注不改原文 | :1014 注 + :1048 | 忠实（F-16） |
| B2 推下轮 | D5 | 内容对，标签打架（F-8） |
| B3 不做 / B7 不做 / B4 挂起 | D6 | 忠实 |
| B5 不做 | D6「不做（…挂起）」 | **加工/歧义（F-1）** |
| §6 其余按提案执行、列回确认、不默认通过 | D5/D8/D13/D14 标「待 CTO 确认」✓；:1051 总处置无标签 | **F-2** |
| 实施第一步：三项、其他不动、前后 critic、不动核/编排/Dolph/.cproject/.project、hook 照旧、不开始 B1 | :1052 头部六条硬约束逐条在 | 范围忠实；细则冒名（F-3/F-4） |
| 两个 commit 允许 push | :1052 尾「b6bc5fe / 5adfe91 允许 push」 | 忠实（`git status -sb` 领先 origin/master 2） |
| 漏项 | — | **无** |

---

## 3. C1–C10 逐门 + §12

| 门 | 结论 | 证据 |
|---|---|---|
| C1 L 标 | PASS | 新引数字全带标：830,903/463,273/454,730 [L1]、1.79/1.83 [L1-derived]、1.5dB [L4]、3dB [L4]、「零收益 [L2 双轨]」、33 天 [L1 mtime] |
| C2 不越级称实测 | PASS | 「H2 实测 base 454,730」为 L1（:722 EZKIT）；SKILL:58 假 [L1] 已去；grep `1\.5 *dB *\[L1` 唯一命中 = critic-A 历史记录 |
| C3 L4 撑不可逆 | PASS | 本批无不可逆动作；3dB [L4] 只进可逆测试判据 |
| C4 L3 撑强约束挂待验 | PASS | 「Debug 优化关 [L3]」作待证伪假设，非结论 |
| C5 可追溯/双轨 | **FAIL → MAJOR** | F-5（3dB 出处指错、归 CTO）；F-3（三段括号定义无出处、与批准案不同）。D12 注双轨核通过（F-16） |
| C6 几何/冲突重审 | PASS（N/A） | 无几何；D12 走「加注不改原文」，非并存 |
| C7 撤回传播 | PASS（带 2 MINOR） | 1.5dB [L1] 残留 0；「6.4 倍」除 :1013 原文外仅 sprint7 讨论与 :1014 注；状态位传播缺口 F-9/F-10 |
| C8 外部输入 ≤24h | PASS-偏差留痕 | 本批无新外部输入；HIT9616 逾期 33 天已登记，CTO D9 补来源、授权未确认、接受留痕 |
| C9 FIRA 收益入选型 | PASS（N/A） | 1.79× 差距分析不进选型/承诺 |
| C10 硬件不可逆动作 | PASS（本批无动作） | 板测 hook 照旧；后续 runbook/对照 build 须引 `STAGE4_BRINGUP_CHECKLIST.md`（F-14/F-15 预告） |
| §12 FG/IO/ST | N/A | 本批零代码；D3 实施时必过（log 已写） |

**硬约束核对**：`git diff --name-only` = 恰 3 文件 ✓；`.cproject`/`.project`/`m1_softconfig*`/`fira_tree.c`/`tree_filterbank.c`/`tfb_8ch.c`/`fir_coeffs_hb63.h`/`dolph_w8_q15.h` 零变动 ✓；staged 空 ✓；untracked：审时新增 1 个（F-14，非本批）。

---

## 4. 修后 delta 复审要看的

1. D6 拆 B5-1/B5-2，B5-2 标「待 CTO 确认」；:1051 逐项挂标签（F-1/F-2）。
2. IMPL-01 分「CTO 范围」/「PM 细则」；三段括号回到提案定义或给理由；raw 读数/板上括号标「CTO-gated 待 CTO_OK」（F-3/F-4）。
3. SKILL:58 去「D10 裁定」名下的 3dB，出处改 `S7_VERIFICATION_PLAN.md:31`（F-5）。
4. F-6 移出裁定句并列为待确认；F-9/F-10 两行指针注。
5. commit 只 add 这 3 个文件。

---

## 5. 实跑命令（全部本机，2026-09-02）

```
git status --porcelain=v1 --untracked-files=all ; git diff --name-only ; git diff --stat ; git diff --cached --name-only ; git log --oneline -5 ; git status -sb
git diff -- sprint2/docs/decisions_log.md                      → 18 insertions, 0 deletions（:1013 原行零变动）
git diff -- knowledge_base/competitor/KB-EXT-SPON-HIT9616A12_FIRMWARE_REG.md .claude/skills/testing/SKILL.md
sed -n '570,574p' sprint6/dsp/audio/m1_cces_project/src/m1_loopback_tdm.c   → :572 "~130us (H2 account, off-board caliber)"
sed -n '59,63p'  sprint6/STAGE4_ALGORITHM_VALIDATION_TEST.md                 → :61 "纯核~130µs[L2]"
python3 -c "print(830903/463273, 830903/454730)"                            → 1.7935 / 1.8272
grep -rn "454[,]*730" / "463[,]*273"   → decisions_log:722 [L1]; H2_READING_ANOMALY_ANALYSIS:10; F7_CLOSING_RECORDS:154-156 (CCLK 1e9 [L1])
sed -n '600,625p' sprint4/dsp/fira/fira_regression.c ; grep "define BENCH_FRAME" sprint4/dsp/core_only/bench/bench_harness.h → 64
awk '/^## 6/…/^## 7/' sprint7/docs/S7_ALGO_UPGRADE_PROPOSAL.md ; sed -n '140,160p' 同文件（B5/B6.x 行）
awk '/^### 6\.3/…' sprint7/docs/S7_DSP_ASSESSMENT.md ; awk '/0\.3/…' 同文件
grep -n "F-13" sprint7/critic/CRITIC_B_PROPOSAL_20260902.md
sed -n '1,20p;50,58p' deliverables/algorithm_validation/EXP_COMPET_BEAM_VS_FREQ.md ; grep -rn "工作假设" / "2× 地板\|3dB 工作"
grep -rn "加权乘法" / "Dolph −20 保留" / "零收益" / "4,5,6,7,0,1,2,3" / "S7_B63_WALLCLOCK_GAP"
grep -rn "6\.4 倍\|6\.4×\|6\.4x\|6\.4倍" --include='*.md' . ; grep -rn "1\.5 *dB *\[L1" ; grep -rn "重复性地板"
grep -n "冻结令" / "1\.5×" sprint2/docs/decisions_log.md（:725 解冻条件 = margin 击穿 1.5x）
cat .claude/hooks/cto-gate-softconfig.sh ; grep -n -i "release\|optimization" sprint6/dsp/audio/m1_cces_project/.cproject（:39 无 value / :118-153 Release -O true）
md5sum sprint6/dsp/audio/m1_cces_project/src/m2_static_txtest_table.h → f78b1dcc7551ab432022c209ea5a4af0
git show --stat 5adfe91 / b6bc5fe ; comm -3 <(find sprint7 -type f|sort) <(git ls-files sprint7|sort) → 仅 S7_POLARITY_QA_RUNBOOK.md（mtime 22:21:21）
grep -n -i "commit\|gate" .claude/team_config.md（:45-50 commit discipline）
```

---
---

# Delta 复审（2026-09-02，同 reviewer: critic @ claude-fable-5-1）

**前提纠正**：team-lead 补交了 CTO【实施第一步】完整原话——(1) a–d、三段名「加权乘法 / analyze / synthesize」、「走 D3 批准的 TU 改动包」、「新增的 raw 读数」、产出名 `S7_B63_WALLCLOCK_GAP.md` 均为 CTO 原话。初审 F-3/F-4 中「PM 冒名 CTO」的判定**作废**；F-3 的技术观察（按流水级切拆不出忙等）保留，性质改为「给 CTO 的提醒」，PM 已以 PM 注 1 落库并列待确认。

**范围**：只看四文件 `git diff`：`decisions_log.md`（+26/−0）、KB（+3/−3）、`testing/SKILL.md`（+1/−1）、`EXP_COMPET_BEAM_VS_FREQ.md`（+1/−1，仅顶注行）。工作树里 `m1_loopback_tdm.{c,h}`、`run_guard_check.sh` 与 5 个未跟踪 `sprint7/dsp|docs` 文件属 s7-base/dsp 实施，另派 critic，本 delta 不看。

## 最终裁定：**PASS**（5 MAJOR 全部闭合/作废；剩 1 MINOR + 5 INFO，非阻塞；可 commit 四文件）

## 逐条闭合

| # | 初审 | delta 状态 | 证据 |
|---|---|---|---|
| F-1 | MAJOR | **已修** | D6 拆「B5-1 全频段换窗不做（CTO）」/「B5-2 子带级恒定波束宽：待 CTO 确认」，并写明 CTO「B5 不做」与提案「挂起」不一致、以及与 D7/B6.10 目的冲突；总处置行同步「B5-1 不做 / B5-2 待确认」 |
| F-2 | MAJOR | **已修** | 总处置逐项挂标签：B1「是否本轮实施待 CTO 明确」、B6.1「rig 按 D7（CTO），翻宏按 D8 待确认」、B6.2「本步仅零代码准备（CTO），执行待排」、B6.3/6.4/6.5 = D2/D3 |
| F-3 | MAJOR | **作废 + 技术点已落** | a–d 为 CTO 原话（前提纠正）；IMPL-01 已分「CTO 原话」/「PM 注」；PM 注 1 明写三段拆不出忙等、内拆分（自旋/postscale/memcpy）作可选补充、是否必做待 CTO 确认 |
| F-4 | MAJOR | **作废 + 已列待确认** | 「走 D3 批准的 TU 改动包」「新增的 raw 读数」为 CTO 原话；PM 注 2 按此理解为 D3 扩展、并写「若 CTO 认为须单独 CTO_OK 请明示，届时先不 commit 该两项」；提案 ③ scratch pin 明确本步不做 |
| F-5 | MAJOR | **已修** | SKILL:58 去掉 D10 名下的 3dB；改为「判据用几倍地板由各实验自定（`S7_VERIFICATION_PLAN.md:31` 取 2× = 3dB [L4]，testing 自定，非 CTO 裁定）」；出处栏三项：EXP_COMPET 顶注(D10) / `S7_VERIFICATION_PLAN.md:31`（本机确认该行仍在）/ 原 :54 已废。无循环 |
| F-6 | MINOR | **已修** | D10 的 [L2] 复算移出裁定句，独立标「待 CTO 确认」，EXP_COMPET 原标注不动 |
| F-7 | MINOR | **已修** | D1 尾句、D7 括号均标「PM 注」 |
| F-8 | MINOR | **已修** | D5 = 「CTO 裁定（照提案）」+ PM 注（准备工作本步不启动） |
| F-9 | MINOR | **已修** | D9 点名 `DEC-S7-EXTINPUT-HIT9616-01`；:1031 后加 D12 式「↑ 注」（原行零变动）；KB §3 标题「D9 后：部分闭合，剩余留痕」 |
| F-10 | MINOR | **已修** | EXP_COMPET 顶注末加「↑ 2026-09-02 CTO 裁定 D10：…4 数维持未落盘、不升级」；07-15 正文零变动（diff 只动第 3 行） |
| F-11 | MINOR | **已修** | RULINGS-01：可逆/验证状态/风险声明齐；IMPL-01：可逆/验证状态/数据出处（提案 §1 :40 表、dsp §0.2 锚点表，指针核对正确）/风险声明（Release 对照 build 另一份二进制、不替代 830,903 基线、改产品配置须板门重跑）齐 |
| F-12 | INFO | 已修 | 「可逆（D11 副本可由 src 版恢复）」+ D11 带 md5 |
| F-13 | INFO | 已修 | KB「会话内裁定」 |
| F-16 | INFO(正向) | 不变 | D12 注一字未动，`git diff` 对 decisions_log 删行数 = 0 |

## 剩余（非阻塞）

| # | 严重度 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| F-17 | MINOR（C5 可追溯） | `decisions_log.md` D12 行「critic-C 实核通过」；批次尾无 reviewer 行 | A/B 批次先例 = critic verdict 落 `sprint7/critic/CRITIC_*.md` 同 commit 入库 + log 尾加 `reviewer: critic @ … ` 行；本批四文件清单不含 verdict，「critic-C 实核通过」成无落盘引用 | 本 verdict 复制为 `sprint7/critic/CRITIC_C_RULINGS_20260902.md` 作第 5 个文件一并 add；log 尾按先例加一行「reviewer: critic @ claude-fable-5-1 / 2026-09-02 — 裁定落库批次：初审 CONDITIONAL（0/5/6/5）→ 全修 → delta PASS；全文 sprint7/critic/CRITIC_C_RULINGS_20260902.md」 |
| F-18 | INFO | D6 尾「Dolph −20 保留（CTO 裁定）」 | 非 CTO 原话，是提案 :144 的建议、经「全部照提案」+ B5-1 不做的推论；按 PM 自定标签规则应标「CTO 裁定（照提案，B5-1 推论）」 | 改标签 |
| F-19 | INFO | IMPL-01 (2) PM 注「`#error` 守卫顺带覆盖 `M2_STXT_LOCALIZE` 与 `M2_SELFTEST` 的前置宏」 | 超出 D3 字面（只列 `M2_STATIC_TXTEST` 的 `#error`）；零字节影响、同类扩展，由 D3 包实施 critic 时裁即可 | 可加「（超出 D3 字面，D3 包 critic 时裁）」 |
| F-20 | INFO | D8「testing 提醒：…正确表是恒等表」 | 出处在未跟踪的 `sprint7/docs/S7_POLARITY_QA_RUNBOOK.md:404`，该文件本批不入库 | runbook 过门入库后补指针 |
| F-14 | INFO（延续） | 工作树 | 现有 3 个 out-of-scope 修改 + 5 个未跟踪文件；lead 已确认显式 `git add` 四文件（或加 F-17 的第 5 个） | 勿 `git add -A` |
| F-15 | INFO（延续，转下一审） | `S7_B63_WALLCLOCK_GAP.md` runbook（未审） | `.cproject` 已含 Release 配置（:118–153 `-O` true），对照 build 不必改 `.cproject`；runbook 须写「build 后若 `.cproject` 变动一律 checkout，不入库」 | 由 B6.3 产出的 critic 查 |

## C1–C10（delta 后）

C1 PASS ｜ C2 PASS ｜ C3 PASS ｜ C4 PASS ｜ **C5 PASS**（SKILL:58 出处修正；IMPL-01 归属由 CTO 原话坐实；剩 F-17 verdict 落盘为 MINOR）｜ C6 PASS(N/A) ｜ C7 PASS（状态位传播 F-9/F-10 已补）｜ C8 PASS-偏差留痕 ｜ C9 PASS(N/A) ｜ C10 PASS（本批无硬件动作）｜ §12 N/A。红线门无 FAIL。

## delta 实跑命令

```
git status --porcelain --untracked-files=all
git diff --stat -- sprint2/docs/decisions_log.md knowledge_base/competitor/KB-EXT-SPON-HIT9616A12_FIRMWARE_REG.md .claude/skills/testing/SKILL.md deliverables/algorithm_validation/EXP_COMPET_BEAM_VS_FREQ.md   → 31+/5−
git diff -- <四文件>（逐行读）；git diff -- sprint2/docs/decisions_log.md | grep -c '^-[^-]'   → 0（无删行，:1013/:1031 原文零变动）
grep -n "^## \|^### " sprint7/docs/S7_ALGO_UPGRADE_PROPOSAL.md ; grep -n "^### 0\." sprint7/docs/S7_DSP_ASSESSMENT.md   → 提案 §1 = :34-51（含 :40 bench 表）；dsp §0.2 = 锚点表 :25
sed -n '31p' sprint7/docs/S7_VERIFICATION_PLAN.md   → 「2× 地板 = 3dB 工作假设 [L4]」仍在
grep -rn "恒等表" sprint7/   → S7_POLARITY_QA_RUNBOOK.md:404（未跟踪）
ls sprint7/critic/   → 仅 CRITIC_A / CRITIC_B
```
