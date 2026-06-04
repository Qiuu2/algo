# item-3 EQ/限幅链 PRD 决策材料（DRAFT — 三道关之第②关待过：独立 critic；第③关待过：CTO 常识审）

> 生成: 2026-06-04, workflow eq-prd-material (28 agents, 4 维证据扫描 + 逐发现对抗证伪 = 三道关第①关已过).
> 状态: surviving findings 23 / refuted 0. 本材料不给推荐项, O0-O3 供 CTO 裁 PRD.

All arithmetic confirms the critic's corrected values. I have verified the load-bearing source lines and re-derived every margin. Producing the synthesis.

---

# item-3（EQ/限幅链）PRD 决策材料 — 是否需要、何种规格

文档ID: DOC-S5-EQPRD-DECISION-01 | 状态: 待独立 critic 评审 → CTO 裁定 | 来源分级: 见各条 | 口径: v1=broadside 聚焦/分区（DEC-S5-STEER-V1-01）；MCPS 换算一律用板上 30-50 cyc/MAC 包络（decisions_log:234/770），禁用理想 1 cyc/MAC

> 本材料**不给推荐项**。O0-O3 选项表供 CTO 裁定 item-3 PRD 规格；该裁定决定 (a) HW-1 IIR-offload 的真伪、(b) §8「EQ 把余量拉向 1.0x」威胁的存在性、(c) DEC-S4-CRITERION-01 正式实时余量阈值。

---

## 1. 现有 PRD / 标准 / 竞品证据总结（KNOWN / SILENT / GAP）

| 维度 | 状态 | 证据（file:line）| 分级 |
|---|---|---|---|
| 产品 PRD（DOC-PRD-002 v2.4）对 EQ/限幅/响度 | **SILENT（沉默，非 EQ=0）** | prd_update.md 全文 grep：唯一「均衡」命中=line 226「均衡档」(N=24/d=35mm 几何方案档名，非信号 EQ)；§3.3 DSP 指标(175-185)=子带/采样/算力裕量/SRAM/延迟/定点精度/阻带衰减，**无输出级 EQ/限幅/响度行**；§3.2 频响(170-173)=平坦度±4dB+灵敏度 | **L1**（文档事实，grep 可复核；「沉默」为确定性观察） |
| 系统 I/O 拓扑（DOC-S4-IO-01）DSP 块 | **KNOWN：仅画波束形成** | audio_io_topology.md:26-28 链路 ADAU1979→SPORT4→21569→SPORT4→ADAU1962A→功放→喇叭，DSP 块注=「(4子带 dyadic beamform 8ch)」；G-IO1~7 gap 无一项涉及 EQ | **L1**（文档事实）；"作者未把 EQ 列为待补项"=**L3**（意图推断）。注：「直进直出」语义边界=A2B 旁路（line 4/25），**不可**引为「PRD 承诺无 EQ」 |
| EQ/限幅作为「处理链一级」的全库出处 | **KNOWN：至少 2 处，均「可选/未锁」** | (a) dsp_design.md:80-82「后处理 (可选: per-ch DRC/EQ/电平/限幅)」[L4 设计草图]；(b) cces_skeleton_description.md:191-193「Step5 后处理（子带增益均衡+限幅器）」其中 EQ=「可选:补偿喇叭频响」、**限幅=「必须:防烧功放 [待核实 U3]」** | **L4**（EQ 探索语）；**限幅必须性=工程级（见 §2）** |
| 官方裁定记录对 item-3 | **KNOWN：明确登记为 PENDING 头号前置** | decisions_log:769-774(DEC-S4-CRITERION-01)「正式阈值等 item-3(EQ链)PRD 钉死」；:808-822(DEC-S5-OPT-ORDER-01)排序#1「HW-1 IIR offload + item-3 EQ PRD 规格化（joint，最高优先）」 | **L1**（CTO 裁定原文，逐字录） |
| 实现路线 FIR vs FIR+IIR | **GAP：UNDECIDED（iface_survey G8）** | iface_survey.md:310「FIR vs FIR+IIR / 浮点 vs 定点路线未定」；ADI 参考例程 Pipelined 确含 5-band IIR EQ 但走**浮点**+全通占位系数(G9)，是例程非我方承诺。我方架构(dsp_8ch_report:238-240)含**可选、类型未指定**的 EQ/限幅级 | **L1**（G8/G9 文档+源码事实）；我方是否采 IIR=**L4/待定** |
| 竞品固件是否含 EQ/限幅 | **GAP：拆机明确排除 → 无法逆推** | full_teardown_v2.md:16 法律声明排除竞品专有 DSP 固件/算法二进制；§7 SPL(0° 106-111dB@1-4kHz)是全链声学量，**不能区分 EQ 整形 vs 喇叭/箱体本征**，且 PF-9 红线禁从竞品 SPL 反推任何设计参数 | **L1**（拆机文本+排除范围）；"无法证实/证伪 EQ"=**L3 推断** |
| 功放 ACM3128A 是否含硬件 EQ/限幅 | **KNOWN（Plan A）：纯 D 类 BTL，无内置 DSP** | full_teardown_v2.md:80-88 仅模拟参数；U5(定向音柱AI数据_extracted.md:54-58)「主芯片含 DSP(ADSP-21569)，功放板不含独立 DSP」 | **L1**（拆机+U5 实测）/ 参数 L4 datasheet。**注：Plan A(ACM3128A)未锁；备选 TAS5825M(selfdev_bom.md:99/101) 含集成 DSP/可软配 EQ** — EQ-on-main-chip 前提是**功放选型相关，非绝对** |
| 适用 JY/T 标准 | **KNOWN（间接）+ GAP（标准号缺）** | JYT_directional_speaker.jpeg 表10 空场: 应备声压级≤75dB(A) / 不均匀度≤10dB(1k/4k) / STIPA≥0.50 / GB3096-2008（prd_update.md:159-162 逐字转录，均「待实测」）；**GAP**：标准号显示为占位「JY/T XXXX—XXXX」，全文 PDF 缺(仅 1 JPEG)，C8 审计已记原件缺失(critic_c8_first_run.md:38-58) | 表10 条文文本=**L1**；标准号/全文缺=**L4 证据缺口（CS-5）** |
| 车站/应急广播 PA 标准是否强制限幅 | **GAP：仓内无任何 EN54/GB 应急广播/声压上限标准文本** | grep GB17565/GB25506/EN54/应急广播 = 0 命中 | **L4 证据缺口**，需 literature-patent 跟进 |

**总结**：产品 PRD 对 item-3 **真实沉默**——既不能默认 EQ=0（会假装 §8 威胁不存在），也不能默认重型 EQ 存在（无 PRD 依据）。官方记录与 CTO 此次指令闭合：item-3 PRD 是公认 PENDING 头号前置项。

---

## 2. 场景功能需求分析（per scenario + 摆位约束）

**三场景（prd_update.md:72）**：博物馆讲解 / 车站广播 / 商场分区广播。

### 2.1 后处理需求分级（按功能，非按场景拍死）

| 功能 | 必要性 | 依据 | 分级 |
|---|---|---|---|
| **保护级限幅器（防烧功放/喇叭）** | **工程级 REQUIRED（建议 PRD 强制）— 三场景皆需** | 实测单只喇叭 7.4Ω/3W[L1]、A/B 串联 15Ω[L1]；铭牌 10W 额定/15W 峰值[L4]；ACM3128A 0.246Vrms=满输出[L4 datasheet]。3W 实测低功率喇叭+低满输出点 D 类功放=任何 DSP 增益/D-C 权重误标或热源都会把削波功率灌进音圈。cces_skeleton:193「必须:防烧功放」；限幅阈值=转接板 PO 签署条件(含追问回复_extracted.md:19,34) | **L3**（工程推理，基于 L1/L4 硬件事实）。**诚实标注：PRD 当前未强制（DOC-S4-IO-01 未命名限幅）；这是工程"建议入 PRD"，非"PRD 已要求"**。阈值待 U3，Q-2/Q-3 额定功率/阻抗仍[L4/待 T/S]（followup:20-21） |
| **语音段校正 EQ（平坦/可懂度）** | **RECOMMENDED（质量级，非保护级）** | PRD 有 STIPA≥0.50(161,待实测)+频响平坦度±4dB(172)；铭牌 120Hz-18kHz 疑-10dB 边界,真实可用 LF 更高(含追问回复:22)[L4]；dsp_8ch_report:239 子带增益均衡明标「可选」 | **L3 — RECOMMENDED**。**诚实警示**：是否真需 EQ、几频段，取决于**实测正轴向响应（R3 消声室，待 T/S 2-4 周）**，当前不可从[L4]铭牌锁定 |
| **响度/AGC** | **场景相关（建议作可配置/分固件档，不进基线常开成本）** | 三场景声环境不同（p1b_prd_alignment.md:54-56）；75dB(A)上限+STIPA+不均匀度均待实测(159-161) | **L4 — 工程判断（无文档讨论动态处理，属未来源观点）**。**诚实修正**：博物馆/车站/商场的 OPTIONAL/RECOMMENDED 分档是**提议默认值，非可证依据**；车站「最需动态处理」与 §3.1.4 待实测指标**不构成 AGC 需求的证据**。**开放项**：商场分区是否含背景音乐？（影响 v1 是否纳 loudness）→ 须 CTO 确认 |

### 2.2 摆位：master-bus vs per-channel（含限幅×波束权重交互约束）

**关键架构事实**（critic R11 修正 F11-MAJOR-1 后口径）：broadside 时 8 通道同信号仅幅度差（dsp_8ch_report.md:229,249）；**v1 聚焦下各通道另加 per-channel 分数延迟（STEER-2），不再逐样本相同**。但整形 EQ 与 per-channel 延迟均为 LTI，二者可交换（master-bus EQ→fan-out→per-ch 延迟 在频谱整形上等价于 per-ch EQ→延迟）——故 **master-bus 整形 EQ 在 broadside 与聚焦下都成立且约 1/8 成本**（broadside 靠同信号、聚焦靠 LTI 可交换性，两条独立成立）。

- **整形 EQ → master-bus（fan-out 前一次处理）**：依上述（同信号 / LTI 可交换双重基础），per-channel EQ 与单次 master-bus EQ 声学等价，per-channel **买不到任何东西** → master-bus 是正确且约 1/8 成本的选择。per-channel EQ 仅当喇叭单元单体差异/位置相关响应才有理（当前驱动单元一致性=[L4]未知，待 T/S）。
- **保护限幅器 → 应 per-driver/per-channel（D-C 权重 fan-out 之后）**【critic 修正 SN-5】：每路携带不同 D-C 幅度权重（chebwin(16,20) 中心 w=1.0、次边 w≈0.50，约 6dB 跨度），各驱动峰值电平不同，**单一 master 限幅器无法单独保护最高权重通道**。但限幅器是标量/近零 MAC，8 个 per-channel 限幅器 MCPS 可忽略。
- **限幅×波束交互约束（D14，PF9:56 开放风险）**：**共阈值** per-channel 限幅会先削高权重通道、把实现锥度推向均匀加权 → 旁瓣抬升、-20dB SLL 在大声驱动下劣化。若用 per-channel 限幅，阈值须**按权重缩放**（T_k = T·w[k]）以保锥度，或保护级限幅放 master-bus 参考最高权重通道。整形 EQ 放 master-bus 不触此问题。

---

## 3. 选项表 O0-O3（无推荐，CTO 裁定）

**共用成本基（CO-1，全部核验）**：
- 预算 = 1000 MCPS [L1，CCLK 实测 1e9，G6 CLOSED]；8ch FIRA 需求 = 347.45 MCPS [L1/EZKIT]
- **v1=聚焦/分区**，EQ 选项骑在**聚焦后基**之上：focusing 增量 = 86-144 MCPS [L4]（2.88 MMAC/s × 30-50 cyc/MAC）→ **聚焦后基（无 EQ）margin = 2.04-2.31x [L4]**
- 余量公式：`margin = 1000 / (347.45[L1] + focus[86-144,L4] + option[L4])`
- 板上 cyc/MAC = **30-50（禁用 1 cyc/MAC）**；biquad = 5 MAC/sample；限幅器包络+增益 ≈ 10 op/sample/ch（abs+一极点检测+平滑增益乘）— **限幅器 MAC 为 CO-5 注入的工程假设，非仓内来源数字**

| 选项 | 规格 | item-3 MCPS [L4, 30-50 cyc/MAC] | 聚焦后基 margin [L4] | IIR-accel offload 资格 | 支持的正式阈值 | 风险 |
|---|---|---|---|---|---|---|
| **O0** | 无 EQ/限幅（现架构 DOC-S4-IO-01，纯直进直出波束） | **0**（精确，L1） | **2.04-2.31x** | 无（无 EQ 可 offload） | 唯一无条件清 **≥2x**（best/mid 系统场景） | **非算力风险=产品声学**：(a)无限幅→瞬态峰值削波/过冲(驱动单元未定 R3 开放)；(b)无整形 EQ→16 阵元线阵+真实喇叭可能粗糙/不平；(c)PA 场景常规需保护限幅+语音整形。**选 O0=显式声学/产品签字"无需保护与整形"，不可静默默认进入** |
| **O1** | LEAN master-bus：2-3 biquad 整形 EQ + 1 限幅器，**单通道 fan-out 前** | **29-60**（=20-25 MAC/samp×48000×{30,50}/1e6；28.8@2bq/30cyc → 60.0@3bq/50cyc） | **1.81x-2.16x**（worst=1000/(347.45+144+60)；best=1000/(347.45+86+29)）【critic 修正：原"1.92-2.30"误配，2.30 实为无 EQ 值】 | biquad EQ 部分 **IIR-accel 原生可 offload**[L2 datasheet]；限幅器**非 biquad，留 core** | 守 **≥1.0x 底线有余量**（1.81x worst）；**不保证 ≥2x**（worst 1.81<2x） | 最低成本非零项（单通道）；offload biquad 后 core 仅余限幅+编排，恢复向无 EQ 2.04-2.31x |
| **O2** | MODERATE：master 5-band EQ(5bq)+限幅 + per-ch trim 1-2 biquad×8 | **108-276**（30cyc:108-166；50cyc:180-276）；典型 1-trim/30cyc 倾向 ~108-180 | **典型 1.49x-1.85x**（best=1000/(347.45+86+108)；worst=1000/(347.45+144+180)）；**满 276 上界 1.30x**【critic 修正：原"1.55-1.91/~1.4"偏乐观】 | per-ch biquad **IIR-offload 可** | **支持 ≥1.5x；≥2x 须靠 HW-1 offload** | 刀刃区：下界 108<150 名义包络（清），上界 180-276>150（破）→ 阈值敏感。**若 O2 入 PRD，HW-1 由"可选"变"承重"** |
| **O3** | RICH per-channel 5-band+限幅 ×8（§8 worst case） | **R5 乐观端 250-290**（9.6 MMAC/s EQ×30cyc=288，限幅折瘦）；**满 30-50+限幅诚实端 ~400-672**（EQ-only 288-480；EQ+lim 403-672）| **R5 端 1.28x-1.46x**；**满堆叠上界 0.86x（→可破 ≥1.0x）** | EQ 部分 **必须 offload** 才可行 | **on-core 不支持任何 ≥1.5x** | O3 = §8 威胁具象化。on-core+聚焦**不可行**，**强制 HW-1 IIR offload**（把 9.6 MMAC/s EQ 移出 core，仅余限幅+编排）。**注：R5 的 250-290 是 30cyc/EQ-only 乐观端，非天花板** |

**诚实分母（DEC-S4-C9-RELEASE-01 强制连体）**：以上 margin 仅含 focus+EQ。整系统残余须并列 §8 未计入清单：codec/IO 5-30、中断 2-15、控制 1-10、WCET +34.7~173.7 MCPS；**整系统残余（无 EQ）= 1.38-2.56x [L4]**，每选项在此基础上进一步退化。任何引 FIRA/offload 收益的呈现须同页并列此清单（不得单独示 2.878x）。

---

## 4. HW-1（IIR-accelerator-offload）的条件性结论

- **HW-1 是"真优化"当且仅当 item-3 PRD 真要 IIR EQ（或可 offload 到 IIR 加速器的滤波）**。ADSP-21569 含 FIR+IIR 加速器（均"up to 1 GHz"[L2 datasheet]）≠ 产品需要它。
- **O0**：HW-1 **moot**——§8「EQ→1.0x」威胁消失，HW-1 收益=0（STEERING_HEADROOM_SCAN.md:33,534：PRD 无 EQ → offload 不需要）。
- **O1**：HW-1 **有价值但非承重**——offload 2-3 biquad 后 core 仅余限幅+编排；不 offload 也守 ≥1.0x。
- **O2**：HW-1 **承重（load-bearing）**——per-ch biquad 移到 IIR accel 才能从 ~1.49-1.85x 拉回 O1 量级、争取 ≥2x。
- **O3**：HW-1 **强制（mandatory）**——on-core 聚焦后 1.28-1.46x（乐观端）已破任何 ≥1.5x；HW-1 是 O3 唯一可行路径。**O3 同时证明 HW-1 真实 + §8 威胁真实**。
- **HW-1 收益上界与缺口**：offload 后 core 成本塌缩为 per-segment 编排，上界 ~6,290 cyc/segment（=g_f7_cyc_1ch_fira 56,616/9 段）。**诚实标注**：6,290 是 FIR 加速器**每段总成本(编排+MAC)**，非编排-only（F7_CLOSING_RECORDS:120-123 明示 56,616 内编排/MAC 不可分），作**保守上界**用；本机**无 adi_iir SHARC cycle 测量**（驱动头 adi_iir_2156x.h 缺，iface_survey:318）→ IIR-accel 编排=[L4/无测量]，须上板 bring-up。**限幅器非线性，即使 HW-1 也留 core**。
- **功放选型耦合**：上述假设 EQ-on-main-chip（Plan A/ACM3128A，无硬件 DSP）。若选 Plan B/TAS5825M（集成 DSP/可软配 EQ），部分 EQ 可卸到功放 DSP，改变 §8/HW-1 威胁模型。当前 CTO 治理（decisions_log:771-784）假设 EQ-on-core，与 Plan A 一致但**功放选型相关，未锁**。

---

## 5. 证据缺口清单（须文献/标准跟进或上板测量）

1. **实测正轴向频响/阵列着色**：无消声室/EZKIT 数据（R3 开放，T/S 待 2-4 周 prd_update:331）→ EQ 频段数/曲线现为[L4]铭牌+[L3]推理。**SN-3 的 RECOMMENDED 不能升 REQUIRED，直到实测显示无 EQ 则失 STIPA/平坦度**。
2. **限幅阈值（保护级数值）**：待 U3（喇叭阻抗/功放增益）；Q-2 额定 10W/峰值 15W、Q-3 8Ω/10W 仍[L4/待 T/S 厂家实测]（followup:20-21）。**保护需求已立，保护阈值未定**。
3. **JY/T 标准编号 + 全文**：仅 1 JPEG（标准号占位 JY/T XXXX—XXXX），全文 PDF 缺 → literature-patent 取编号原件；核表10 之外是否有条款强制限幅/EQ。
4. **车站/应急广播 PA 标准**：仓内无 EN54/GB17565/GB25506/应急广播文本 → literature-patent 核是否强制限幅/SPL 控制（关乎车站场景是否硬性需限幅）。
5. **商场分区是否含背景音乐**：开放 PRD 问题，决定 v1 是否纳 loudness/AGC → 须 CTO 确认。
6. **item-3 精确 MCPS（点值）**：取决于 PRD 钉死频段数 + 板上 cyc/MAC + WCET 实测（DEC-S4-CRITERION-01 / F7_WARM=0 待）→ 本材料只给架构级范围（master-bus ~1/8 of per-ch×8）。
7. **IIR-accel 编排 cycle + 并发 FIR+IIR 总线仲裁**：本机无测量，须 adi_iir bring-up 上板（HW-1/HW-2）。
8. **限幅器算法**：无仓内文件指定（look-ahead/RMS/multiband 会抬升 MAC）；CO-5 的 10 MAC/sample 为注入假设。

**给 CTO 的 item-3 PRD 裁定应至少分别钉死**：(i) **保护限幅器**——是否强制、阈值口径（系 15Ω DC Re[L1]+U3 功放增益，待核实）；(ii) **整形 EQ**——是否需多频段、频段数、master-bus 还是 per-channel；(iii) **响度/AGC**——是否需、是否分固件档/场景可选。**两类（保护限幅 vs 产品级多频段 EQ 链）必要性不同，不得混为一谈**：保护限幅算力可忽略（§8 威胁可忽略）；只有重型多频段 EQ+限幅链（板上 ~250-290+ MCPS）才是 §8「余量拉向 1.0x」来源与 HW-1 触发器。

---

## 6. 三道关状态（POLICY-PROV-001 v1.8 §4B）

- **关①（workflow auto-verify）**：已做（本 synthesizer 重跑全部 grep、重读 decisions_log:765-823 与 F7_R14_RULING_MATERIAL:348-387 逐字核验、Python 重算所有 O0-O3 margin 与 MCPS 包络——全部命中 critic 修正值；已吸收 critic 对 F3/F5/SN-1/SN-3/SN-4/SN-5/CS-2/CS-6/CO-3/CO-4/CO-5 的 weakened 修正进正文）。
- **关②（独立 critic teammate）**：**PENDING** — 本材料须经独立 critic（fresh-context，verdict 带 reviewer@model/date）评审 C1-C10 + L-grade 完整性后方可上 CTO。
- **关③（CTO sanity review）**：**PENDING** — 由 CTO 就 item-3 PRD 是否需要、何种规格作正式裁定（DEC-S4-CRITERION-01 正式阈值依此落定）。

相关文件（绝对路径）：
- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint2/docs/prd_update.md
- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint2/docs/decisions_log.md（:769-822 裁定原文）
- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md（:348-387 §8 残余裕量）
- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint4/audio_io_topology.md（DOC-S4-IO-01）
- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint3/dsp/cces_skeleton/cces_skeleton_description.md（:191-193 限幅必须）
- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint3/dsp/dsp_8ch_report.md（:229,238-249 同信号 fan-out + EQ/限幅级）
- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/knowledge_base/standards/JYT_directional_speaker.jpeg（表10，标准号占位）
- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/knowledge_base/competitor/full_teardown_v2.md（:16 固件排除；:80-88 ACM3128A）
- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md（:19,34 限幅阈值 PO 条件）

---

## APPENDIX: verified findings (machine record)

```json
{
 "findings": [
  {
   "id": "F1",
   "title": "产品 PRD（DOC-PRD-002 v2.4）对 EQ/限幅/响度 = 完全沉默（不是 EQ=0，而是规格缺口真实存在）",
   "claim": "现行 PRD 全文无任何一条把 EQ / 限幅 / 压限 / loudness / DRC 列为产品后波束处理需求；唯一命中的「均衡」是候选方案档名「均衡档」(N=24 配置名)，与信号均衡无关。这是 item-3 规格缺口为真的直接证据——PRD 沉默意味着 CTO 必须裁定，而非默认 EQ=0。",
   "evidence": [
    {
     "source": "sprint2/docs/prd_update.md (整文件 grep)",
     "detail": "对 限幅|限制器|压限|EQ|均衡|loudness|响度|过载|clip|limiter|compressor|DRC|AGC|增益管理|保护 全文搜索：唯一命中为 line 226 「**均衡档** | N=24 / d=35mm / Dolph-30dB」——即 §4 候选方案对比的方案档名，非后处理需求。其余 0 命中。"
    },
    {
     "source": "prd_update.md:98-214 (§3 目标技术指标)",
     "detail": "§3.1 指向性、§3.1.4 表10(SPL/不均匀度/STIPA/GB3096)、§3.2 频响(平坦度 ±4dB/灵敏度)、§3.3 DSP指标(子带4/采样48k/算力裕量/SRAM/延迟/定点精度/阻带衰减)、§3.4 功耗、§3.5 BOM、§3.6 可靠性——逐节列举可量化指标，无一条提及输出级 EQ/限幅/压限/响度均衡。§3.3 DSP 指标项里也没有 EQ/limiter。"
    }
   ],
   "grade": "L1 — 直接文档事实(grep 全命中可复核)；「沉默」本身是确定性观察，非估计。",
   "implications": "item-3 EQ 链的产品规格在 PRD 中不存在 → 规格缺口为真，DEC-S4-CRITERION-01 正式阈值无法在 PRD 沉默下拍定。HW-1 IIR-offload 的「真伪」与 §8「EQ 把余量拉向 1.0x」威胁的存在性，都取决于 CTO 先把 item-3 规格化；当前不能默认 EQ=0(那会假装威胁不存在)，也不能默认重型 EQ 存在(无 PRD 依据)。",
   "dimension": "prd-repo",
   "verdict": {
    "finding_id": "F1",
    "verdict": "confirmed",
    "reasons": "I independently re-ran the grep over sprint2/docs/prd_update.md (377 lines) with a term set BROADER than the finding's (added 保护/protect/过流/过压/热保护/soft-clip/clip/compress/loudness/削波/削顶/peak/过冲/DRC/AGC, case-insensitive). Result: the ONLY EQ-related hit is prd_update.md:226 \"**均衡档** | N=24 / d=35mm / Dolph-30dB\" — a §4 candidate-config name (a retired N=24 geometry option), NOT a signal-processing EQ/limiter requirement. (A line-71 match on \"相控阵型\" is a CJK-substring false positive, irrelevant.) Protection/over-current/over-voltage/thermal/soft-clip terms returned ZERO matches (grep exit 1). \n\nEvidence item 2 verified by reading §3.3 DSP指标 (prd_update.md:175-185): the rows are 子带数量/采样率/算力裕量(≥10×)/SRAM/延迟/定点精度/滤波器阻带衰减 — no output-stage EQ/limiter/loudness/DRC line, exactly as claimed. §3.2 频响 (170-173) = 频响平坦度±4dB + 灵敏度 only (response flatness, not a DSP EQ requirement). §3.1/§3.1.4 (100-163) are directivity/SPL-difference/表10 acoustic specs — no post-beam EQ. §5 未覆盖需求 (235-245) does NOT list EQ/limiter as future work; line 243 \"用户控制接口（DSP参数调整）\" is a control-UI item, not an EQ/limiter spec.\n\nL-grade honest: the finding self-grades L1 and explicitly states \"「沉默」本身是确定性观察，非估计\" — correct, a grep over a committed file is a deterministic documentary fact, appropriately L1. No arithmetic / no MMAC->MCPS conversion / no idealized-MAC numbers involved, so the cyc/MAC envelope discipline is not engaged and cannot be violated.\n\nPRD-silence trap handled correctly (the exact discipline I am to enforce): the finding does NOT spin silence into a PRD decision. Title says \"不是 EQ=0，而是规格缺口真实存在\"; implications say it must NOT default to EQ=0 (would fake the §8 threat away) NOR assume heavy EQ exists (no PRD basis), and that DEC-S4-CRITERION-01 cannot be pinned under PRD silence — CTO must rule. This is the honest reading. My broader sweep only strengthens the finding (more terms, still zero genuine hits).",
    "grade_ok": true
   }
  },
  {
   "id": "F2",
   "title": "「直进直出」拓扑(DOC-S4-IO-01)的 DSP 块只画了波束形成，无 EQ/限幅级",
   "claim": "系统 I/O 拓扑文档把 DSP 处理块明确写为「4 子带 dyadic beamform 8ch」，输入→DSP→8 路输出全链中没有任何 EQ/限幅/后处理级。文档自陈红线「只录文档有的…文档没有的列 gap，不凭印象补」，且 7 项 gap(G-IO1~7)中无一项涉及 EQ——即文档作者未把 EQ 视为待补的已知项。",
   "evidence": [
    {
     "source": "sprint4/audio_io_topology.md:1-4, 22-35",
     "detail": "标题「音频 I/O 拓扑（直进直出）」；拓扑图 line 26-28：『模拟音源 → ADAU1979 →TDM→ SPORT4 → ADSP-21569 → SPORT4 →TDM→ ADAU1962A → 8×功放 → 16 喇叭』，DSP 块注释(line 27)= 『(4子带 dyadic beamform 8ch)』。line 31 『**DSP**：4 子带 dyadic 树形 + broadside beamform，**8 通道**输出』。无 EQ/limiter 字样。"
    },
    {
     "source": "audio_io_topology.md:4 (拓扑定义) + 57-67 (Gaps)",
     "detail": "『**拓扑**：直进直出（不用 A2B，音柱单元本地）』——「直进直出」原文范围 = 指音频不经 A2B/AD2428W 旁路网络(板级路由)，line 25 『AD2428W/A2B 旁路』、G-IO3 『直进直出不用 A2B…如何旁路』。其语义是「不走 A2B 总线」，并非「DSP 内不做任何处理」的承诺。整文件 EQ/限幅/后处理 grep = 0 命中；G-IO1~7 gaps 无一项关于 EQ。"
    }
   ],
   "grade": "L1 — 文档原文(带 PDF/源码出处的事实文档)。注意「直进直出」语义边界已逐字界定，避免误读为 EQ 承诺。",
   "implications": "系统级拓扑文档确认当前架构图中无 EQ 级；但「直进直出」一词的 scope 是 A2B 旁路，不能被引用为「PRD 承诺无 EQ」。EQ 若加入，是 DSP 块内新增级，不与「直进直出」(A2B 旁路)矛盾。",
   "dimension": "prd-repo",
   "verdict": {
    "finding_id": "F2",
    "verdict": "confirmed",
    "reasons": "Every cited claim verified verbatim against /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint4/audio_io_topology.md (DOC-S4-IO-01):\n\n1. Topology diagram (lines 26-28) reads exactly: 模拟音源 → ADAU1979 →TDM→ SPORT4 → ADSP-21569 → SPORT4 →TDM→ ADAU1962A → 8×功放 → 16 喇叭; the DSP-block annotation (line 28) = \"(4子带 dyadic beamform 8ch)\". Line 31 = \"DSP：4 子带 dyadic 树形 + broadside beamform，8 通道输出\". No EQ/limiter/post-process token anywhere in the chain. CONFIRMED.\n\n2. Independent grep for EQ|equaliz|限幅|limiter|压限|后处理|滤波|compress|drc|均衡 over the whole file = 0 hits (exit 1). CONFIRMED.\n\n3. Gaps section (lines 57-67) has exactly 7 distinct gaps G-IO1..G-IO7 (verified via grep -oE | sort -u; the count-of-8 is G-IO1 recurring in the summary line 75, not an 8th gap). None of the 7 concerns EQ/limiter — they cover sample-rate register value, analog-source connection, A2B physical bypass, DAC→amp channel mapping, TDM timing, block size, SoftConfig switches. CONFIRMED.\n\n4. Self-stated red line (line 5) = \"只录文档有的（带 PDF/源码出处）；文档没有的列 gap，不凭印象补\" — verbatim. So EQ being absent AND not listed as a gap genuinely means the doc author did not flag EQ as a known to-be-filled item. CONFIRMED.\n\n5. The \"直进直出\" semantic-scope guard is correct: line 4 defines it as \"(不用 A2B，音柱单元本地)\", line 25 = \"AD2428W/A2B 旁路\", G-IO3 (line 63) = \"直进直出不用 A2B…如何旁路\". So scope = A2B/AD2428W bypass (board routing), NOT \"DSP does no processing\". CONFIRMED.\n\nAdversarial checks all pass: (a) No compute/MAC arithmetic in this finding — no MMAC→MCPS conversion, no idealized 1-cyc/MAC number, cyc/MAC envelope discipline not triggered. (b) No PRD-silence-spun-as-PRD-decision: the finding's implications section explicitly states \"直进直出\" cannot be cited as \"PRD 承诺无 EQ\" and that EQ would be a new DSP-block stage not contradicting the A2B-bypass topology — this is exactly the anti-spin discipline required. (c) The finding does NOT claim the PRD decided against EQ; it correctly scopes itself to the architecture/topology document.",
    "grade_ok": false,
    "grade_fix": "The blanket \"L1\" is slightly imprecise and should be split. The text-presence/absence claims (diagram says X, grep finds 0 EQ hits, 7 gaps with no EQ) are directly-observable documentary facts — fairly treated as L1-equivalent (directly verified, not simulated/inferred), and I independently reproduced all of them. BUT the interpretive sub-claim \"文档作者未把 EQ 视为待补的已知项\" (author did not consider EQ a known item) is an inference about author intent derived from the gap list + red-line, not a measured fact — that specific sub-claim is L3 (analytic/sound reading), not L1. Recommend grading: documentary facts = L1; the author-intent inference = L3. This does not change the verdict (the L3 inference is well-supported and the finding never over-reads it), but the single \"L1\" label over-states the intent inference by one notch. Separately, the dimension tag \"prd-repo\" is a mild mismatch: the evidence is a topology/I/O document (DOC-S4-IO-01), not the PRD (sprint2/docs/prd_update.md, sprint3/pf8/p1b_prd_alignment.md exist separately) — the finding is honest about this in its implications, but a reader scanning by dimension label should not treat F2 as PRD evidence. Net: finding is sound and confirmed; only the L-grade granularity needs the L1/L3 split noted above."
   }
  },
  {
   "id": "F3",
   "title": "EQ/限幅 在全库唯一作为「处理链一级」出现的地方=DSP 设计书，且明确标注「(可选)」——设计探索语，非 PRD 需求",
   "claim": "dsp_design.md 的处理流程框图把后处理画成一个独立框，文字为『后处理 (可选: per-ch DRC / EQ / 电平 / 限幅)』。这是算法设计书的设计草图层(L4 探索)，明确「可选」，不是 PRD 锁定需求；它恰恰说明 EQ 是「可加可不加」的待定项，而非已承诺规格。",
   "evidence": [
    {
     "source": "sprint2/dsp/dsp_design.md:80-82",
     "detail": "处理流程框图倒数第二框原文：『后处理 (可选: per-ch DRC / EQ / 电平 / 限幅)』。前序框为分析滤波器组→通道扇出加权延迟→合成滤波器组(line 59-77)，后处理框置于 16 通道全带输出(line 78)与 DMA/TDM 输出(line 83-87)之间。「可选」二字为措辞红线，标明非强制。"
    },
    {
     "source": "sprint3/dsp/dsp_8ch_report.md:70",
     "detail": "算力台账旁注：『剩余可用算力：1469 MMAC/s（可用于 EQ/DRC/AEC 等后处理）』——把 EQ 列为「可用于」的潜在用途(桌面 L2 投影口径，且该 33×/17× 桌面口径已被 DEC-S5/decisions_log:234/770 板上 0.92x 推翻，不可作余量依据)，非已实现/已承诺级。"
    }
   ],
   "grade": "L4(设计书「可选」探索语) — 框图为设计阶段占位，非 PRD 承诺；引用须标「可选/未锁」。",
   "implications": "全库 EQ/限幅作为「处理链一级」的唯一出处是「可选」设计草图。这强化 F1：产品侧无承诺。若 CTO 要把 item-3 规格化，dsp_design.md 的「per-ch DRC/EQ/电平/限幅」可作为待规格化的功能候选清单起点，但其算力/规格全部未定，不可作为 §8『EQ 把余量拉向 1.0x』威胁存在性的依据(那需要 PRD 钉死频段数/限幅复杂度)。",
   "dimension": "prd-repo",
   "verdict": {
    "finding_id": "F3",
    "verdict": "weakened",
    "reasons": "CORE HOLDS, but two load-bearing framing claims are factually wrong.\n\nVERIFIED ACCURATE (core thesis sound):\n- sprint2/dsp/dsp_design.md:80-82 quote is verbatim: the post-process box reads \"后处理 (可选: per-ch DRC / EQ / 电平 / 限幅)\", positioned between the 16ch fullband output (line 78) and DMA/TDM output (line 83-87), preceded by analysis/fanout/synthesis (line 59-77). \"可选\" qualifier is real. Confirmed.\n- sprint3/dsp/dsp_8ch_report.md:70 quote is verbatim: \"剩余可用算力：1469 MMAC/s（可用于 EQ/DRC/AEC 等后处理）\". F3 correctly flags this as the overturned 33×/17× desktop accounting (decisions_log:234 \"高估约 25×\"; 49×/340× voided as same-source idealized 1cyc/MAC, decisions_log:799-800) and correctly says it cannot serve as margin evidence. Good provenance discipline.\n- L-grade L4 honest; NO idealized-MAC number cited as live; no MMAC->MCPS conversion attempted (cyc/MAC envelope respected by abstention). Clean.\n- Central thesis (EQ/limiter is a design-exploration item, NOT a locked PRD spec; §8 threat existence requires PRD to pin band-count/limiter complexity) is corroborated by F7_R14_RULING_MATERIAL.md:352,396,411 (item-3 NOT spec'd, \"the DOMINANT uncertainty\", undefined until product DSP chain spec'd) and decisions_log:773 (>=1.0x assertion conditional on item-3 PRD pinning).\n\nREFUTED / OVERCLAIMED (why weakened):\n1. The \"全库唯一出处\" (library-unique source) claim is FALSE. EQ/limiter appears as a labeled processing-chain step in a SECOND place: sprint3/dsp/cces_skeleton/cces_skeleton_description.md:191 -> \"/* Step 5: 后处理（子带增益均衡 + 限幅器） */\", inside dsp_process_frame() between Step4 synthesis and Step6 8ch fanout — i.e. a genuine chain stage, not just a sketch box. F3 explicitly states \"全库 EQ/限幅作为「处理链一级」的唯一出处是「可选」设计草图\" — directly contradicted.\n2. The blanket \"可选 / 可加可不加\" framing is partly contradicted by that same second source. At cces_skeleton:192-193 only the EQ (subband_gain_apply) is \"可选：补偿喇叭频响\", but the LIMITER (limiter_process) is annotated \"必须：防烧功放 [待核实 U3]\" — MANDATORY for amplifier protection, NOT optional. This is corroborated product-side: knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md:19,34 treats the limiter threshold (限幅阈值) as a transition-board PO-signing condition (防烧功放). So a basic protection limiter has a mandatory face; F3 conflates the discretionary EQ with the protection limiter by lumping both as one \"可选\" item.\n\nIMPACT ON CTO DECISION: F3's implication (\"产品侧无承诺\", supports F1) is overstated for the limiter. Evidence indicates a basic protection limiter is effectively required (防烧功放), while a rich multi-band EQ is discretionary. That distinction is exactly what the §8 threat hinges on — it gives the threat a non-zero floor (some limiter compute is unavoidable) even though the rich-5-band worst case (~250-290 MCPS) remains conditional on PRD. F3 as written would mislead the CTO into believing item-3 has zero product-side commitment.\n\nRelevant files (absolute):\n- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint2/dsp/dsp_design.md (lines 80-82, verified)\n- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint3/dsp/dsp_8ch_report.md (line 70, verified)\n- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint3/dsp/cces_skeleton/cces_skeleton_description.md (lines 191-193, COUNTEREXAMPLE: second chain-stage source; limiter marked 必须)\n- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md (lines 19,34: limiter threshold = PO-signing condition, 防烧功放)\n- /home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md (lines 352,396,411: item-3 NOT spec'd)",
    "grade_ok": true,
    "grade_fix": "L4 grade is correct and honest for the two cited evidence items (dsp_design.md design-sketch \"可选\" exploration text; dsp_8ch_report.md overturned desktop projection). No change to the L4 grade needed. The correction is to the CLAIM scope, not the grade: (1) drop \"全库唯一\" — there is a second chain-stage source at cces_skeleton_description.md:191; (2) split \"可选\" — EQ is discretionary [L4 design-sketch], but a protection limiter is annotated 必须/防烧功放 in cces_skeleton:193 and tied to a PO condition in KB-HW-002:19,34, so the limiter side carries a hardware-protection necessity that should itself be L-graded (limiter threshold provenance: 15Ω DC Re is [L1], the threshold value 待核实 U3).",
    "corrected": "EQ/限幅 appears as a labeled post-beamform processing-chain stage in at least TWO repo locations, not one: (a) sprint2/dsp/dsp_design.md:80-82 — design-flow box \"后处理 (可选: per-ch DRC / EQ / 电平 / 限幅)\" [L4 design sketch, \"可选\"]; and (b) sprint3/dsp/cces_skeleton/cces_skeleton_description.md:191-193 — \"Step 5: 后处理（子带增益均衡 + 限幅器）\" inside dsp_process_frame(), where the EQ (subband_gain_apply) is \"可选：补偿喇叭频响\" but the limiter (limiter_process) is \"必须：防烧功放 [待核实 U3]\". Neither is a locked PRD spec (item-3 remains [L4] and unpinned per F7_R14_RULING_MATERIAL.md:352,396,411), so F3's core conclusion stands: item-3 must be PRD-pinned before the §8 \"~1.0x\" rich-5-band worst case can be asserted as a real threat. HOWEVER the framing must be corrected: a basic protection limiter is NOT discretionary — it is treated as mandatory for amplifier protection in both the CCES skeleton (line 193) and the hardware input (KB-HW-002:19,34, where the limiter threshold is a transition-board PO-signing condition). Therefore: the rich multi-band EQ is genuinely optional/待定 [L4], but item-3 has a non-zero compute floor from a required protection limiter; the §8 threat's UPPER envelope (rich 5-band+limiter ≈250-290 MCPS at 30 cyc/MAC) is conditional on PRD, but its existence is not purely hypothetical. CTO action: PRD spec for item-3 should separately pin (i) the mandatory protection limiter (threshold ties to 15Ω DC Re [L1] + U3 amp gain, 待核实) and (ii) any discretionary multi-band EQ band-count — these have different necessity levels and must not be lumped as one \"可选\" item."
   }
  },
  {
   "id": "F4",
   "title": "decisions_log 已把「item-3 EQ 链 PRD 规格化」明确登记为悬而未决的前置待办(DEC-S4-CRITERION-01 / DEC-S5-OPT-ORDER-01)",
   "claim": "项目正式裁定文档反复记载：实时余量正式阈值「待 item-3(EQ 链)PRD 钉死」，且 EQ 链 PRD 规格化被列为头号待办。这与 CTO 当前「先决定 PRD 是否需要 item-3」的指令一致——即官方记录确认 EQ 规格在 PRD 中尚未存在、需专门裁定。",
   "evidence": [
    {
     "source": "sprint2/docs/decisions_log.md:769-774 (DEC-S4-CRITERION-01)",
     "detail": "逐字：『>=10x 复议…正式阈值暂不拍』；『正式阈值等 item-3（EQ 链）PRD 钉死 + WCET 实测收窄后再定』；line 774 待办：『item-3 EQ 链 PRD 规格化 + WCET 实测…收窄 → 定正式阈值』。"
    },
    {
     "source": "decisions_log.md:773 (临时下限依据)",
     "detail": "逐字：残差最坏 1.38x>1.0x 『在 item-3（EQ/mixing）≤150 MCPS 的 [L4] 包络下成立；若产品加重型多频段 EQ+限幅链（板上 ~30 cyc/MAC 可达 ~250-290 MCPS，>150），最坏残差被拉向 ~1.0x』——明示 §8 威胁的成立完全条件化于 item-3 PRD 规格(频段/限幅复杂度)，当前 [L4] 包络。"
    },
    {
     "source": "decisions_log.md:808-822 (DEC-S5-OPT-ORDER-01)",
     "detail": "逐字：『HW-1（IIR offload EQ）最高优先…EQ=item-3 最大威胁必须先解』；排序 #1『HW-1 IIR 加速器 EQ offload 评估 + item-3 EQ 链 PRD 规格化（joint，最高优先）』；line 820-822 依赖：『正式阈值与 item-3 EQ PRD + WCET 实测共依赖——HW-1/item-3 落定后方能拍正式阈值』。"
    }
   ],
   "grade": "L1 — CTO 正式裁定原文(decisions_log v2.0，逐字录)。EQ 算力数字 0-150/250-290 MCPS 本身为 [L4] 包络，已在原文标注。",
   "implications": "官方记录与 CTO 此次指令闭合：item-3 EQ 链 PRD 是公认的 PENDING 前置项。(a) HW-1 IIR-offload 的「真伪」= 取决于 item-3 是否真需要重型 IIR EQ；(b) §8『EQ 拉余量向 1.0x』威胁存在性 = 条件化于 item-3 复杂度([L4] 包络 0-150 vs 250-290 MCPS)，PRD 沉默使其既不可证实也不可证伪；(c) DEC-S4-CRITERION-01 正式阈值依赖 item-3 落定——三项均指向「先做 item-3 PRD 裁定」。",
   "dimension": "prd-repo",
   "verdict": {
    "finding_id": "F4",
    "verdict": "confirmed",
    "reasons": "All three cited evidence blocks match the source files verbatim and the L-grade discipline is honest.\n\n1) decisions_log.md:769-774 (DEC-S4-CRITERION-01) — verified verbatim. Line 770 \"正式阈值暂不拍\"; line 771 \"正式阈值等 item-3（EQ 链）PRD 钉死 + WCET 实测收窄后再定\"; line 774 todo \"item-3 EQ 链 PRD 规格化 + WCET 实测...→ 定正式阈值\". Confirms formal realtime-margin threshold (DEC-S4-CRITERION-01) is explicitly NOT yet set and is blocked on item-3 EQ PRD.\n\n2) decisions_log.md:773 — verified verbatim. The §8 \"EQ pulls margin toward 1.0x\" threat is explicitly CONDITIONAL on item-3 PRD: \"残差最坏 1.38x>1.0x 在 item-3（EQ/mixing）≤150 MCPS 的 [L4] 包络下成立；若产品加重型多频段 EQ+限幅链（板上 ~30 cyc/MAC 可达 ~250-290 MCPS，>150），最坏残差被拉向 ~1.0x\". This matches the finding's implication (b) exactly.\n\n3) decisions_log.md:808-822 (DEC-S5-OPT-ORDER-01) — verified verbatim. Ranking #1 (line 813): \"HW-1 IIR 加速器 EQ offload 评估 + item-3 EQ 链 PRD 规格化（joint，最高优先）\"; line 809 \"HW-1（IIR offload EQ）最高优先...EQ=item-3 最大威胁必须先解\"; lines 820-821 \"正式阈值与 item-3 EQ PRD + WCET 实测共依赖——HW-1/item-3 落定后方能拍正式阈值\". Confirms item-3 PRD is the #1 pending prerequisite and the threshold co-depends on it.\n\nADVERSARIAL CHECKS (default-refute) ALL CLEARED:\n- cyc/MAC envelope discipline HONORED: line 773's 250-290 MCPS is explicitly derived at board \"~30 cyc/MAC\" (decisions_log:234 board reality 30-50). I re-derived: 5 biquads x 5 MAC x 8ch x 48000 = 9.6 MMAC/s; x30 cyc/MAC = 288 MCPS — lands inside 250-290. NO banned idealized 1-cyc/MAC numbers; the idealized 49x/340x are explicitly RETIRED in the same log (lines 799-800) as \"桌面理想 1cyc/MAC...被板上 0.92x 推翻\". Matches task envelope mandate exactly.\n- L-grades HONEST: finding grades itself L1 for the DOCUMENTARY FACT that the record registers item-3 as pending (genuinely L1-verifiable and verified), while explicitly flagging the embedded EQ MCPS numbers (0-150 / 250-290) as [L4]. Independently corroborated: F7_R14_RULING_MATERIAL.md:338-344 grades item-3 as [L4] \"the DOMINANT uncertainty\" and the residual-margin result \"inherits the WEAKEST grade...= [L4]\". No L4-dressed-as-L1.\n- PRD-silence NOT spun as PRD-decision: the architecture doc DOC-S4-IO-01 (sprint4/audio_io_topology.md) is genuinely silent on any EQ/limiter chain — it describes only I/O topology (SPORT/SRU/TDM/48k/24bit) plus 7 gaps (G-IO1..7), none of which is an EQ decision. F7_R14_RULING_MATERIAL.md:339 states item-3 has \"NO evidence either way\" and may legitimately be 0 (pure pass-through). The finding correctly frames item-3 EQ PRD as PENDING/undecided, NOT as a decided spec — which is the truthful reading and aligns with the CTO's current instruction to first decide whether the PRD needs item-3.\n- Document version v2.0 confirmed (decisions_log.md:4 and :835).\n\nThe finding accurately reflects that the official decision record closes the loop with the CTO's instruction: item-3 EQ PRD is the recognized #1 PENDING prerequisite, and (a) HW-1 IIR-offload reality, (b) the §8 threat's existence, and (c) the DEC-S4-CRITERION-01 formal threshold all condition on it. No overclaim found.",
    "grade_ok": true
   }
  },
  {
   "id": "F5",
   "title": "FIR-vs-FIR+IIR / 是否需要 IIR EQ 的实现路线，工程上仍 UNDECIDED(iface_survey G8)；ADI 例程含 5-band IIR EQ 但走浮点、且为参考非我方锁定",
   "claim": "接口普查把「FIR vs FIR+IIR / 浮点 vs 定点路线未定」列为 gap G8，明示我方波束形成是否需 IIR 驱动(adi_iir)尚未锁；ADI 参考例程 Pipelined 确实含 5-band IIR EQ，但那是例程(走浮点、FIR 系数为占位全通)，不是我方产品承诺。这是 HW-1 IIR-offload 评估真伪的工程侧依据：IIR EQ 既未在我方架构中存在，也未被排除。",
   "evidence": [
    {
     "source": "sprint4/iface_survey.md:310 (G8)",
     "detail": "逐字：『**FIR vs FIR+IIR / 浮点 vs 定点路线未定**：example(Pipelined)是 FIR(512tap)+5band IIR 且**走浮点**(Fixed↔Float 转换 c:535-557)；我方波束形成是否纯 FIR / 纯定点未锁』；影响『决定…是否需 IIR 驱动(adi_iir)』；闸门『由 DEC-S4-DSP-01 算法定型后定』。"
    },
    {
     "source": "sprint4/iface_survey.md (G9) + dsp_8ch_report.md:159-175",
     "detail": "G9：example FIR 系数=全通(b0=1)占位，非真实波束系数——例程的 EQ/滤波链是占位参考，不代表我方算法。我方实现侧(dsp_8ch_report)处理链 = 4 子带分析/分数延迟/加权求和/合成，无 IIR EQ 级。"
    }
   ],
   "grade": "L1(G8/G9 为文档事实，源码行号坐实) — 例程含 5-band IIR EQ 是 ADI 例程事实；我方是否采用 = 未锁(L4 待定)。",
   "implications": "HW-1(IIR-accelerator-offload)优化的「真实性」前提 = 产品确需 IIR EQ 链。当前我方架构无 IIR EQ(纯 FIR 子带波束)，IIR EQ 仅存在于 ADI 参考例程。因此 HW-1 是否为「真优化」严格取决于 item-3 PRD 是否把 IIR EQ(或可 offload 到 IIR 加速器的滤波)列为需求；ADSP-21569 IIR 加速器存在[L2 datasheet]不等于产品需要它。",
   "dimension": "prd-repo",
   "verdict": {
    "finding_id": "F5",
    "verdict": "weakened",
    "reasons": "Core thesis SOUND and well-sourced, but two wording/citation defects weaken it.\n\nVERIFIED TRUE:\n1. G8 verbatim at sprint4/iface_survey.md:310 — \"FIR vs FIR+IIR / 浮点 vs 定点路线未定\", example(Pipelined)=FIR(512tap)+5band IIR 走浮点, impact \"是否需 IIR 驱动(adi_iir)\", gate \"由 DEC-S4-DSP-01 算法定型后定\". Faithful.\n2. ADI example IS 5-band IIR + float (verified in source, not just doc): Pipelined/src/Processing.h:18-20 = FIR_TAPS 512 / IIR_BANDS 5 / NSECTIONS 4 biquad; Processing.c uses `float` Input/IIROutput/IIRCoeffs/FIRCoeffs and `IIRGains[5]={1.0,1.0,1.0,1.0,1.0}`.\n3. G9 all-pass placeholder confirmed: fir_coeffs.dat = 511 zeros + single 1.0 at tap 512 (pure delay, |H|=1, placeholder). \"全通占位非真实波束系数\" correct. (Loose: impulse is at last tap, not literally b0; iface_survey itself says \"b0=1\" loosely — substance holds.)\n4. Thesis (\"IIR EQ exists only in ADI ref example, not an ITC commitment; HW-1 reality hinges on whether item-3 PRD requires IIR EQ\") corroborated by sprint5/steering_scan/STEERING_HEADROOM_SCAN.md:89,143 and HW-1 risk(1) at :534 (\"if PRD defines NO EQ/limiter... the threat is 0 and the offload is unneeded\"). Consistent with C9/iron-rule-8.\n5. L-grades honest: G8/G9 documentary facts = L1, our-adoption = L4-待定. F5 makes NO MMAC->MCPS conversion so no idealized-1-cyc/MAC violation. PRD-silence is preserved as undecided, NOT spun into a decision.\n\nDEFECT 1 (overclaim): F5 says \"我方实现侧处理链...无 IIR EQ 级\" and \"当前我方架构无 IIR EQ(纯 FIR 子带波束)\". But sprint3/dsp/dsp_8ch_report.md:238-240 — the architecture chain diagram — DOES contain a post-beamform \"子带增益均衡(可选,各子带×G_sb)\" + \"DRC/限幅器(保护功放)\" stage. Accurate statement: our architecture carries an optional EQ/limiter stage that is type-UNSPECIFIED (not declared IIR-vs-FIR), marked optional, and not PRD-locked. \"无 IIR EQ\" is defensible only in the narrow \"no stage declared IIR\" reading; \"无 EQ 级\"/\"纯 FIR 子带波束\" overstates absence and actually undersells HW-1's relevance (an EQ/limiter slot already exists in-architecture, just unspecified — strengthening, not refuting, the \"未排除\" half of F5's own claim).\n\nDEFECT 2 (wrong citation): F5's evidence cites dsp_8ch_report.md:159-175 for the processing chain, but :159-175 is the symmetry-constraint section (4.2/4.3). The actual chain with the EQ/limiter is at :215-247 (diagram :238-240; \"无 IIR\" note at :266). Cited range shows neither the chain nor the EQ stage.\n\nNet: the load-bearing conclusion (IIR EQ undecided/unspecified for our product; HW-1 reality is PRD-conditional) survives intact and is well-supported; the defects are scope-of-wording + a misdirected line pointer, not a thesis collapse. Hence WEAKENED, not refuted.",
    "grade_ok": true,
    "grade_fix": "L-grade is honest and adequate. G8/G9 as L1 documentary facts is correct (verified at file:line incl. source code). Our-adoption-of-IIR-EQ as L4/待定 is correct. One refinement for precision: the sub-claim \"our architecture has no EQ stage\" should itself be downgraded/corrected — dsp_8ch_report.md:238-240 shows an OPTIONAL, type-unspecified EQ/limiter stage already in-architecture, so the honest grade of \"EQ-stage existence in our chain\" = present-but-optional [doc L1] with type/PRD-status = [L4/待定]. No idealized-MAC numbers present; no MCPS arithmetic to envelope-check (F5 introduces none).",
    "corrected": "F5 (corrected): The interface survey lists \"FIR vs FIR+IIR / float vs fixed route\" as gap G8 (iface_survey.md:310), explicitly leaving UNDECIDED whether our beamforming needs an IIR driver (adi_iir), gated on DEC-S4-DSP-01 algorithm freeze. The ADI reference example (Pipelined) genuinely contains a 5-band IIR EQ (Processing.h:18-20: FIR 512-tap + IIR_BANDS=5, 4 biquad sections) running in FLOATING-POINT with all-pass placeholder FIR coefficients (fir_coeffs.dat = 511 zeros + 1.0, G9) — it is reference example code, NOT an ITC product commitment. Our own architecture (dsp_8ch_report.md:215-247) is a pure-FIR subband beamformer (analysis / fractional-delay / weighted-sum / synthesis) that ALREADY INCLUDES a post-beamform \"subband gain EQ (optional)\" + \"DRC/limiter (amp protection)\" stage at :238-240 — but that stage is OPTIONAL, type-UNSPECIFIED (not declared IIR vs FIR), and not PRD-locked. So an IIR EQ is neither present-as-committed nor excluded in our architecture; the EQ/limiter slot exists but its realization is open [L4/待定]. This is the engineering basis for the truth-value of HW-1 (IIR-accelerator-offload): HW-1 is a \"real optimization\" only if item-3 PRD actually requires an IIR EQ / IIR-offloadable filtering. ADSP-21569 having an IIR accelerator [L2 datasheet] does not imply the product needs it; if the PRD specifies no EQ/limiter, the §8 \"EQ pulls margin toward 1.0x\" threat = 0 and HW-1 benefit = 0 (STEERING_HEADROOM_SCAN.md:89,534). [Evidence line fix: the processing chain is at dsp_8ch_report.md:215-247, not :159-175 as originally cited.]"
   }
  },
  {
   "id": "F6",
   "title": "全库唯一坐实的「限幅」需求是过驱动/喇叭保护阈值(硬件级)，与多频段 EQ 链是不同的东西——不要混为一谈",
   "claim": "检索到的「限幅」实需均指向「过驱动保护/防烧功放输入级」这一硬件保护阈值(由灵敏度/阻抗推算)，挂在转接板/采购闸门，而非产品级多频段 EQ+limiter 信号处理链。这区分对 §8 威胁评估关键：一个单通道保护性 limiter 的算力远小于 PRD 待定的『重型多频段 EQ+限幅链 250-290 MCPS』。",
   "evidence": [
    {
     "source": "sprint2/docs/sprint3_retrofit_assessment.md:171, 188-192",
     "detail": "line 171『过驱动保护 | 转接板加限幅 | 过压烧输入级风险 | 必须限幅 | ✅ 由灵敏度推限幅阈值』；line 189『过驱动可能烧毁竞品功放输入级…必须…限幅保护』。语境为硬件保护，非信号美化 EQ。"
    },
    {
     "source": "sprint2/docs/PROJECT_HANDOVER.md:192, 196",
     "detail": "line 192：建议把『Q-①（15Ω 是 Re 还是 1kHz 模值，影响限幅阈值）』列为转接板 PO 签署条件；line 196『影响阻抗匹配/限幅』。限幅在此 = 由阻抗/灵敏度定的保护阈值(单参数)，挂采购闸门，非 DSP EQ 链规格。"
    },
    {
     "source": "prd_update.md:243",
     "detail": "§5 未覆盖需求表：『用户控制接口（DSP 参数调整）| Sprint 4 | DSP/软件』——DSP 可调参数(可能含 EQ/电平)被推迟到 Sprint 4，确认产品级 DSP 调参/EQ 至今未规格化。"
    }
   ],
   "grade": "L1(限幅=保护阈值的文档事实) — 但「保护限幅算力 vs 多频段 EQ 链算力」的量级差为推断，须 item-3 PRD 才能定。",
   "implications": "item-3 规格化时必须区分两类：(1) 单通道过驱动/喇叭保护 limiter(已有硬件需求依据，算力极小，对余量威胁可忽略)；(2) 产品级多频段 EQ+loudness+limiter 信号链(PRD 当前无依据，若加入才是 §8『余量拉向 1.0x』的来源，250-290 MCPS @板上 30 cyc/MAC)。CTO 的 item-3 裁定应分别就这两类给出明确 spec，否则 §8 威胁与 HW-1 真伪都无法判定。建议 item-3 PRD 至少明确：是否需多频段 EQ、频段数、是否需 loudness、limiter 是保护级还是动态级。",
   "dimension": "prd-repo",
   "verdict": {
    "finding_id": "F6",
    "verdict": "confirmed",
    "reasons": "I opened every cited file and re-derived the arithmetic. CORE CLAIM CONFIRMED: every established/坐实 \"限幅\" need in the repo is a hardware-level overdrive/amp-protection threshold (derived from sensitivity/impedance, hung on the transition-board procurement gate), NOT a product-level multi-band EQ+limiter signal-processing chain.\n\nEVIDENCE #1 (sprint2/docs/sprint3_retrofit_assessment.md): line 171 verbatim \"过驱动保护 | 转接板加限幅 | 过压烧输入级风险 | 必须限幅 | ✅ 由灵敏度推限幅阈值\"; line 189 \"（模拟）竞品功放输入灵敏度、阻抗、耦合方式（决定匹配/限幅，防烧机）\". Context is §3.1 analog-interface compatibility — unambiguously hardware protection, not signal-beautifying EQ. The finding cites range 188-192 for a quote that lands at line 189 (in-range, exact text). CONFIRMED.\n\nEVIDENCE #2 (sprint2/docs/PROJECT_HANDOVER.md): line 192 recommends Q-① (15Ω = Re vs 1kHz modulus, \"影响限幅阈值\") as a transition-board PO signing condition; line 196 \"影响阻抗匹配/限幅\". A single impedance/sensitivity-derived protection-threshold parameter on the procurement gate. CONFIRMED verbatim.\n\nEVIDENCE #3 (prd_update.md:243): content exact (\"用户控制接口（DSP 参数调整）| Sprint 4 | DSP/软件\"). DSP-tunable params (possibly incl. EQ/level) deferred to Sprint 4 = product DSP tuning still unspec'd. CONFIRMED content.\n\nUNCITED CORROBORATION (strengthens the finding): cces_skeleton_description.md:191-193 splits post-processing into \"subband_gain_apply (可选: 补偿喇叭频响)\" and \"limiter_process (必须: 防烧功放 [待核实 U3])\" — the ONLY mandatory limiter in the DSP chain is itself a protection limiter (finding's class-1). F7_R14_RULING_MATERIAL.md:352 + audio_io_topology.md (DOC-S4-IO-01) confirm the documented architecture is \"直进直出\" with NO product-level multi-band EQ named, so class-2 genuinely has \"PRD 当前无依据\".\n\nARITHMETIC re-derived WITH cyc/MAC envelope discipline: 5-band(5 biquad) x 5 MAC x 8ch x 48000 x 30 cyc/MAC = 288 MCPS — squarely in the cited 250-290 band; uses board-reality 30 cyc/MAC, NOT banned idealized 1 cyc/MAC. (At 50 cyc/MAC = 480, so 250-290 = low end of board envelope, consistent with established context.) The \"保护 limiter 算力 << 多频段 EQ 链算力\" magnitude gap is correctly self-graded by the finding as an INFERENCE pending item-3 PRD, not as an L1 fact.\n\nL-GRADE HONEST: \"L1 (限幅=保护阈值的文档事实)\" is appropriate for the documented decisions; the finding explicitly cabins the magnitude-difference as needing item-3, and explicitly states the product-EQ chain has \"PRD 当前无依据\". PRD-SILENCE NOT SPUN AS PRD-DECISION: the finding characterizes the product-level multi-band EQ as undecided/unspec'd (Sprint-4 deferred, no basis), NOT as \"decided no\" — correct discipline.\n\nWEAKNESSES (minor, do not break core): (a) Citation file-path imprecise — finding writes \"prd_update.md:243\" but actual path is \"sprint2/docs/prd_update.md:243\" (three-gate hygiene defect, content correct). (b) Finding slightly understates that an OPTIONAL loudspeaker-FR compensation stage (subband_gain_apply, 可选) already sits in the skeleton chain, so the class-1/class-2 boundary is not perfectly clean; but it is optional, unspec'd, and does not change the §8 threat / HW-1 truth-test conclusion or the actionable implications. IMPLICATIONS SOUND: item-3 PRD must separately spec (1) per-ch overdrive/speaker protection limiter (has HW basis, compute negligible, §8-threat ignorable) vs (2) product-level multi-band EQ+loudness+limiter chain (no PRD basis; if added = the §8 \"margin toward 1.0x\" driver and the HW-1 offload trigger). Verdict: confirmed.",
    "grade_ok": true,
    "grade_fix": "L-grade is honest as written. Optional sharpening (not required): fix the citation path \"prd_update.md:243\" -> \"sprint2/docs/prd_update.md:243\" for three-gate traceability, and add one clause noting that an OPTIONAL per-ch loudspeaker-FR compensation (subband_gain_apply, cces_skeleton_description.md:192) already exists as an unspec'd optional stage, so the class-1/class-2 boundary should be stated as \"the only MANDATORY/established limiter is protection-grade\" rather than implying the chain is entirely empty of any EQ-like stage.",
    "corrected": "No correction to the verdict needed. Recommended precision edits only: (1) cite \"sprint2/docs/prd_update.md:243\" (full path); (2) note the optional subband_gain_apply (cces_skeleton:192, \"可选: 补偿喇叭频响\") already present as an unspec'd loudspeaker-FR-compensation stage — so phrase class-1 as \"the only MANDATORY/established limiter is protection-grade (cces_skeleton:193 '必须: 防烧功放')\". Core distinction, §8/HW-1 dependency on item-3, and the recommendation that item-3 PRD separately spec protection-limiter vs product-EQ-chain all stand."
   }
  },
  {
   "id": "SN-1",
   "title": "Driver/amp PROTECTION limiter is REQUIRED in all three scenarios, not optional",
   "claim": "A protection limiter is mandatory (not nice-to-have) for the as-built hardware: 4x ACM3128A class-D amps drive 8 BTL channels into ~15 ohm series pairs of low-power 2-inch drivers (single-driver rated 10W nominal / 15W peak nameplate, real measured Re 7.4 ohm, real measured single-driver power 3W). The drivers are the weak link and the limiter is the only thing standing between full-scale digital signal and burned voice coils.",
   "evidence": [
    {
     "source": "knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md:11-12,19",
     "detail": "Driver real-measured 7.4 ohm/3W [L1]; series A/B pair real impedance 15 ohm [L1]; Q-1 explicitly: '15 ohm DC Re true value -> 转接板限幅阈值可定 -> PO 签署条件满足' (limiter threshold is itself a gating precondition for the transition-board PO)"
    },
    {
     "source": "knowledge_base/competitor/full_teardown_v2.md:44-45,81-88",
     "detail": "Driver 10W rated / 15W peak, 88 dB/2.83V/1m -> ~98 dB at 10W [L4 nameplate]; ACM3128A class-D, 0.246 Vrms input sensitivity = full output, 4 chips/8 channels BTL [L4 datasheet]"
    },
    {
     "source": "knowledge_base/hardware_input/定向音柱AI数据_extracted.md:34",
     "detail": "Project's own stated meaning: 'Q-1 直流 Re 真值 -> 转接板 PO 签署条件满足 (限幅阈值防烧功放可定)' — limiter is framed as the burn-protection mechanism, a precondition not an enhancement"
    },
    {
     "source": "sprint3/dsp/cces_skeleton/cces_skeleton_description.md:193",
     "detail": "Existing skeleton already marks limiter_process as '必须：防烧功放' (REQUIRED: prevent amp/driver burnout), pending U3 threshold data — engineering already treats it as required"
    }
   ],
   "grade": "L3 (engineering reasoning over L1/L4 hardware facts) — REQUIRED in all 3 scenarios. Justification: low-power 3W-real drivers + class-D amp with a low 0.246Vrms full-output point means any DSP gain/D-C weight miscalibration or hot source feeds clipping power into voice coils; protection is the floor, not a feature. Honest caveat: exact threshold awaits U3 (Q-2/Q-3 rated power/impedance still [L4/待 T/S], decisions_log:286).",
   "implications": "item-3 is NOT optional at the PRD level — at minimum a single protection limiter MUST exist, so the §8 'EQ pulls margin toward 1.0x' threat is real to the extent the limiter (+ any EQ) consumes compute. The HW-1 IIR-offload value proposition stands because at least one mandatory dynamics/EQ stage exists. The minimal-spec floor is a one-band brickwall/soft-knee limiter; this alone is cheap (see SN-5).",
   "dimension": "scenario-needs",
   "verdict": {
    "finding_id": "SN-1",
    "verdict": "weakened",
    "reasons": "SUBSTANCE SOUND, HEADLINE OVERSHOOTS, TWO WRONG LINE-POINTERS.\n\nHARDWARE FACTS — all verified accurately against the cited files:\n- Driver real-measured 7.4 ohm / 3W [L1]: confirmed at 定向音柱AI数据_含追问回复_extracted.md:11 and 定向音柱AI数据_extracted.md:45 (\"真实测量单只喇叭 7.4Ω/3W [L1/硬件实测]\").\n- Series A/B pair 15 ohm [L1]: confirmed followup:12,19 and full_teardown_v2.md:70.\n- 10W rated / 15W peak nameplate [L4]: full_teardown_v2.md:44; followup:20 (\"额定 10W 预计参数，峰值 15W，待厂家实测 [L4 预估]\").\n- 88 dB/2.83V/1m -> ~98 dB @10W [L4 nameplate]: verbatim full_teardown_v2.md:45.\n- ACM3128A class-D, 0.246 Vrms full-output, 4 chips/8 BTL ch [L4 datasheet]: full_teardown_v2.md:81-88.\n- Q-1 \"15Ω 直流 Re 真值 -> 限幅阈值可定 -> PO 签署条件满足\": verbatim followup:19,34.\n- Skeleton already marks limiter_process as \"必须：防烧功放\": verbatim cces_skeleton_description.md:193.\nNo idealized-1-cyc/MAC numbers used; the only MCPS figure invoked (rich 5-band+limiter x8 ~250-290 MCPS) inherits the board 30 cyc/MAC envelope (decisions_log:234) per F7_R14_RULING_MATERIAL.md:352 — discipline respected.\n\nWHY WEAKENED, NOT CONFIRMED:\n1) PRD-SILENCE vs PRD-DECISION. The headline says the limiter is \"REQUIRED ... at the PRD level\" / \"NOT optional at the PRD level.\" The authoritative item-3 record (F7_R14_RULING_MATERIAL.md:352) and the current architecture doc DOC-S4-IO-01 (audio_io_topology.md:1-33) both state the PRD currently names NO EQ/limiter — the documented DSP block is \"4子带 dyadic beamform 8ch\" only, and item-3 is \"the DOMINANT uncertainty,\" range 0-150 MCPS where 0 = pure beamform pass-through is a LIVE possibility, graded [L4]. So the PRD does NOT presently mandate a limiter; the requirement is an engineering inference, not a PRD fact. The finding is NOT refuted because it does not actually assert the PRD-as-written mandates one — it self-grades L3 (\"engineering reasoning over L1/L4 hardware facts\"), says \"at minimum a single protection limiter MUST exist\" as a floor, and honestly caveats threshold awaits U3 with Q-2/Q-3 still [L4/待T/S]. The engineering core is correct: a 3W-real-measured driver behind a class-D amp with a 0.246 Vrms full-output point is a genuine voice-coil burn risk, and the project's own skeleton + PO-gating language already treat protection limiting as required engineering. But the headline wording risks being read by the critic/CTO as \"PRD already requires it\" — that spin is exactly the PRD-silence-as-decision trap and must be tightened.\n2) TWO WRONG LINE-POINTERS (true facts, mis-cited):\n (a) Evidence #3 cites 定向音柱AI数据_extracted.md:34 for the \"限幅阈值防烧功放\" framing. At line 34 of THAT file is U1 interface content; the exact phrase lives at line 34 of the *followup* file (...含追问回复_extracted.md). The substance is present in the plain extracted file at lines 45-48 (\"限幅阈值依据齐备... 防烧\"), so it is a cross-file mislabel, not fabrication.\n (b) The grade caveat cites decisions_log:286 for \"Q-2/Q-3 still [L4/待T/S]\"; line 286 is latency (DEC-S2-012), not U3 power. The fact is true and sourced at followup:20-21 and extracted:46-47 — wrong pointer, real fact.\n\nIMPLICATIONS CHECK: The conditional framing is correct and matches the established record. STEERING_HEADROOM_SCAN.md:33 and R14_RULING_PROPAGATION.md:53 explicitly make HW-1 value and the §8 \"EQ pulls margin toward 1.0x\" threat CONDITIONAL on item-3 actually existing. The finding's own implications preserve this conditionality (HW-1 stands \"because at least one mandatory dynamics/EQ stage exists\"). Given the hardware burn-risk argument, a one-band protection limiter as a floor is a defensible L3 engineering position, and even a minimal one-band limiter is cheap (small MCPS), so the §8 threat magnitude from a protection-only floor is modest — the large 250-290 MCPS threat only materializes with a RICH multiband EQ that the PRD has not specified. The finding does not over-inflate this.",
    "grade_ok": false,
    "grade_fix": "Keep the body grade L3 (engineering reasoning over L1/L4 hardware facts) — that is honest. But the TITLE/CLAIM wording \"REQUIRED ... at the PRD level\" must be corrected to reflect PRD-silence: the PRD as written (DOC-S4-IO-01) names no EQ/limiter and item-3 is [L4] 0-150 MCPS with 0 (pure pass-through) a live option. Reword to an L3 engineering RECOMMENDATION that the PRD SHOULD mandate a protection limiter, not a statement that it already does. Also fix the two line-pointers: (a) cite the followup file ...含追问回复_extracted.md:34 (or the plain file lines 45-48) for the 防烧功放 framing, not 定向音柱AI数据_extracted.md:34; (b) drop decisions_log:286 and cite followup:20-21 / extracted:46-47 for the Q-2/Q-3 [L4/待T/S] caveat.",
    "corrected": "SN-1 (corrected): A driver/amp PROTECTION limiter SHOULD be a PRD-mandated stage (engineering recommendation, L3), based on as-built hardware: 4x ACM3128A class-D amps drive 8 BTL channels into ~15 ohm A/B series pairs of 2-inch drivers (single-driver real-measured Re 7.4 ohm [L1] and real-measured power 3W [L1]; nameplate 10W nom/15W peak [L4]; amp 0.246 Vrms input = full output [L4 datasheet]). The drivers are the weak link; a protection limiter is the only thing between full-scale digital and burned voice coils. NOTE the PRD as currently written does NOT yet mandate this: DOC-S4-IO-01 (audio_io_topology.md:26-33) describes ADC->beamform->DAC->amp with NO EQ/limiter named, and item-3 (post-beamform mixing/EQ/limiter) is the DOMINANT [L4] uncertainty at 0-150 MCPS (F7_R14_RULING_MATERIAL.md:352), where 0 (pure pass-through) is a live option. The project already treats protection limiting as engineering-required (cces_skeleton_description.md:193 \"必须：防烧功放\") and ties a definable limiter threshold to the transition-board PO precondition (定向音柱AI数据_含追问回复_extracted.md:19,34). IMPLICATION: if the CTO accepts this engineering recommendation into the PRD, item-3 is non-zero, so the HW-1 IIR-offload value proposition and the §8 \"EQ pulls margin toward 1.0x\" threat both become real — but their MAGNITUDE depends on scope: a minimal one-band protection limiter is cheap (small MCPS, modest threat), whereas a RICH 5-band+limiter x8ch reaches ~250-290 MCPS at board ~30 cyc/MAC [L4 envelope, decisions_log:234] and is the dominant margin threat. Exact limiter threshold awaits U3; Q-2/Q-3 rated power/impedance remain [L4/待T/S] (followup:20-21). HW-1 benefit and §8 threat stay [L4/待验证] per C9/iron-rule-8 until board-measured."
   }
  },
  {
   "id": "SN-2",
   "title": "Limiter MUST sit on the master bus BEFORE the D-C weight fan-out; per-channel limiters would break the beam pattern",
   "claim": "This is a real, load-bearing design constraint, not a preference. In the broadside-only architecture all 8 output channels carry the SAME signal, differing only by a fixed Dolph-Chebyshev amplitude weight applied at the weighted-sum/fan-out (y = Sigma w[k]*(A_k+B_k); all 8 outputs identical except amplitude). A single master limiter placed BEFORE the weight fan-out scales every channel by the same factor and preserves the D-C weight ratios -> beam pattern (SLL -20dB taper) intact. Per-channel limiters with a common threshold would clip high-weight channels before low-weight ones, dynamically flattening the taper toward uniform weighting -> sidelobes rise and -20dB SLL degrades exactly under loud drive.",
   "evidence": [
    {
     "source": "sprint3/dsp/dsp_8ch_report.md:229,245-249",
     "detail": "Signal chain: 'y_sb = Sigma w[k]*(A_k+B_k)' and note 1: 'broadside-only 时,所有 8 个通道输出信号相同 (仅幅度因 D-C 权重不同),可视为对同一处理结果的幅度加权分发' — fan-out is pure per-channel amplitude scaling of one common signal"
    },
    {
     "source": "computed (scipy.signal.windows.chebwin(16,20), normalized max=1)",
     "detail": "8 symmetric-pair weights span ~0.50 to 1.00 (edge pair 0.87, 2nd-from-edge 0.50, center 1.00) — ~6 dB spread. Under a common per-channel threshold the center (w=1.0) channels clip ~6 dB earlier than the lightest (w=0.50), progressively driving the realized taper toward uniform = sidelobe degradation"
    },
    {
     "source": "sprint3/dsp/dsp_8ch_report.md:163,265",
     "detail": "SLL -20dB is the stated retained beamforming target; D-C weight precision treated as load-bearing (Q15, ~60dB dynamic range) — confirms the taper ratios are what produce the spec'd pattern"
    },
    {
     "source": "sprint3/audit/PF9_post_simulation_panorama.md:56",
     "detail": "Existing open risk D14 '限幅器/DRC 对波束影响' (limiter/DRC effect on beam), P2, desktop-doable now — the interaction is already flagged as an unverified risk, corroborating it is real"
    }
   ],
   "grade": "L3 (analytic, geometry/weight facts are L1/L2) — placement is a CONSTRAINT. Justification: the math is deterministic given identical-signal fan-out + fixed weights; a master pre-fan-out limiter is the only placement that protects all drivers without distorting the pattern. Caveat: the worst driver sees the highest absolute level (center pair, w=1.0), so the master limiter's threshold must be referenced to the highest-weight channel to guarantee protection of every channel.",
   "implications": "Resolves the per-channel-x8 vs one-master-bus cost question decisively: ONE master limiter (before fan-out) is both ~8x cheaper AND the acoustically correct choice. Per-channel limiting is contraindicated, not merely costlier. This shrinks the item-3 compute envelope (favorable for the §8/margin threat) and means the HW-1 IIR offload only needs to carry a master-bus chain, not 8 independent chains, for the limiter portion.",
   "dimension": "scenario-needs",
   "verdict": {
    "finding_id": "SN-2",
    "verdict": "confirmed",
    "reasons": "Independently verified every cited line and re-derived the arithmetic. (1) Identical-signal fan-out fact CONFIRMED: dsp_8ch_report.md:229 (\"y_sb = Σ w[k]×(A_k+B_k)\") and note 1 at :249 (\"broadside-only 时,所有 8 个通道输出信号相同,仅幅度因 D-C 权重不同...幅度加权分发\") — fan-out is pure per-channel amplitude scaling of one common signal [L1/L2 as graded]. (2) Weight-spread arithmetic CONFIRMED by independent scipy run: chebwin(16,20) normalized gives center w=1.0, edge pair 0.8668 (~0.87 ✓), 2nd-from-edge 0.5043 (~0.50 ✓), min-to-max span 0.50–1.00 ✓. The \"~6 dB spread / center clips ~6 dB earlier than the w=0.50 channel\" claim is exact: 20·log10(1.0/0.5043)=5.95 dB ✓. (3) The taper-flattening logic is deterministic and sound: under a COMMON-threshold per-channel limiter the w=1.0 center clips ~6 dB before the lightest channel, compressing realized weight ratios toward uniform → SLL rises. (4) D14 corroboration CONFIRMED: PF9_post_simulation_panorama.md:56 lists \"限幅器/DRC 对波束影响 (D14), P2, 现在(desktop-doable)\" as an OPEN, unverified risk — independently flags the interaction as real and not-yet-quantified, consistent with the honest L3 grade (degradation magnitude is NOT measured/asserted). (5) STRENGTHENING fact the finding under-cites: the report's own block diagram (dsp_8ch_report.md:238-245) ALREADY places DRC/限幅器 on the single reconstructed mono channel (line 240, \"1 通道 @ 48kHz\") BEFORE the 8ch TDM broadcast (line 245) — i.e., the existing architecture already implements the master-bus-before-fan-out placement the finding recommends. L-grade honesty: graded L3 analytic with geometry/weight facts L1/L2; NOT spun as measured; no idealized-MAC numbers; no MMAC→MCPS conversion (envelope discipline N/A); scope is architecture-internal (does NOT spin PRD-silence into a PRD limiter decision — it scopes \"IF a limiter exists, WHERE it goes\"). Load-bearing conclusion (one master limiter before fan-out is both ~8x cheaper AND acoustically correct; shrinks item-3/HW-1 envelope) stands.",
    "grade_ok": false,
    "grade_fix": "L-grade itself (L3 analytic, geometry/weight facts L1/L2) is correct and honest — leave as-is. The one defect is a TITLE-level overclaim, not a grade error: the title \"per-channel limiters would break the beam pattern\" drops the qualifier that the body correctly carries. The taper-breaking mechanism requires a COMMON threshold across channels; weight-scaled per-channel thresholds (T_k = T·w[k]) would preserve the static taper. The body is careful (\"Per-channel limiters with a common threshold would clip high-weight channels before low-weight ones\"), so this is precision-loss in the headline only. Recommended title edit: \"...per-channel limiters with a common threshold would break the beam pattern.\" Note for completeness: even weight-scaled per-channel limiters can momentarily diverge under independent attack/release dynamics, and master-bus placement remains unambiguously simpler + ~8x cheaper, so the load-bearing conclusion is unaffected by this nuance."
   }
  },
  {
   "id": "SN-3",
   "title": "Speech-band corrective EQ is RECOMMENDED (not required) and belongs on the master bus, not per-channel",
   "claim": "Some response-shaping EQ is warranted for intelligibility — the column has known response issues (driver low-end roll-off, nameplate 120Hz-18kHz likely a -10dB edge so true usable LF is higher, plus array coloration) and the PRD carries a STIPA >= 0.50 intelligibility requirement and a +-4dB flatness target. But corrective EQ is a quality/recommended item, not a protection-grade must. Crucially it should be MASTER-BUS, not per-channel: per-channel correction is only justified if drivers differ unit-to-unit or there is position-dependent response; for a single common broadside signal the correction is identical for all 8 channels, so master-bus shaping is sufficient.",
   "evidence": [
    {
     "source": "sprint2/docs/prd_update.md:161,172",
     "detail": "PRD targets: STIPA >= 0.50 (待实测), frequency-response flatness +-4dB over 1k-8kHz on-axis — both motivate response correction"
    },
    {
     "source": "knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md:22",
     "detail": "Q-4: frequency response 120Hz-18kHz is nameplate, '疑 -10dB 边界,真实可用 -3dB 下限待' [L4] -> real usable LF higher than 120Hz; a corrective/shaping HPF+presence-EQ is the natural fix"
    },
    {
     "source": "sprint3/dsp/dsp_8ch_report.md:239",
     "detail": "Chain already reserves '子带增益均衡(可选,各子带 xG_sb) 补偿喇叭频响偏差' — labeled 可选 (OPTIONAL/recommended), confirms it is not protection-grade"
    },
    {
     "source": "sprint2/docs/prd_update.md:145,171",
     "detail": "Strong-directivity band downgraded to 1k-6kHz(internal)/5kHz(external); speech energy <= 5kHz dominant — so EQ need only shape the speech band, a modest band count"
    }
   ],
   "grade": "L3 — RECOMMENDED, master-bus placement. Justification: intelligibility/flatness targets exist and the driver/array has real coloration, but EQ improves quality rather than preventing damage; identical fan-out signal means per-channel EQ buys nothing acoustically (drivers are nominally identical; any unit-matching is a [L4] unknown awaiting T/S). Honest caveat: whether EQ is truly needed and how many bands depends on measured on-axis response (R3, anechoic, pending) — cannot be locked from current [L4] nameplate data.",
   "implications": "For the EQ-spec decision: a master-bus parametric/shaping EQ of a FEW bands (speech-shaping HPF + presence + de-mud) is the realistic spec, NOT a per-channel rich EQ. This keeps item-3 modest and keeps the §8 margin threat bounded. The 'rich 5-band+limiter x8ch ~250-290 MCPS' worst case is an over-spec for this product's actual need — see SN-5.",
   "dimension": "scenario-needs",
   "verdict": {
    "finding_id": "SN-3",
    "verdict": "confirmed",
    "reasons": "All load-bearing claims verified against cited sources. (1) PRD targets are real and pending, not met: STIPA >= 0.50 待实测 (prd_update.md:161), flatness +-4dB over 1k-8kHz on-axis (prd_update.md:172). These motivate response correction. (2) Nameplate 120Hz-18kHz with suspected -10dB edge is [L4/datasheet 标称] (定向音柱AI数据_含追问回复_extracted.md:22) — real usable LF higher, a shaping HPF is the natural fix. (3) dsp_8ch_report.md:239 gain-EQ is explicitly labeled 可选 (OPTIONAL), confirming non-protection-grade. (4) \"Recommended not required\" holds: no PRD line mandates EQ as a hard requirement (grep for 必须/required across prd_update.md + dsp report returned nothing). (5) Master-bus-sufficient argument is strongly supported: dsp_8ch_report.md:153 \"同一驱动通道的两个单元接收完全相同的信号\" and :249 \"所有 8 个通道输出信号相同（仅幅度因 D-C 权重不同）\" — common broadside mono fan-out, so identical per-channel EQ buys nothing over one master-bus EQ. (6) Per-channel caveat is honest: driver unit-to-unit consistency is an OPEN [L4] unknown awaiting T/S + supplier 一致性 indices (decisions_log:312, sprint3_teardown_workorder:83, sprint3_procurement_kickoff:48); transition_board_design:43 states the electrical chain is \"无失配\". No doc establishes known mismatch that would force per-channel. L-grades are honest throughout (L3 recommendation; [L4] nameplate/unit-matching; R3 anechoic on-axis response explicitly flagged as pending and as the gate to lock band count). The finding makes NO MMAC->MCPS conversion of its own — it cites the critic R5 250-290 MCPS figure only as an over-spec to argue against — so the cyc/MAC envelope discipline is respected, no idealized 1-cyc/MAC numbers introduced. The finding also correctly bounds the §8 threat: under master-bus placement the EQ cost is ~1/8 of per-channel x8, far below the 0-150 MCPS [L4] item-3 envelope (decisions_log:773), so the \"rich 5-band+limiter x8ch ~250-290 MCPS pulls margin toward 1.0x\" worst case is indeed an over-spec for this product's actual need.\n\nADVERSARIAL CHECKS THAT FAILED TO REFUTE (i.e., finding survives): I tested whether the protection-grade limiter belongs in item-3 EQ (which would make item-3 a must, not recommended). It does NOT: the amp-protection limiting (防烧功放) is HARDWARE-domain — RC+TVS clamp on the transition board (transition_board_design:33,151,262; extracted:19,34 \"转接板限幅阈值防烧功放\"). The dsp_8ch_report:240 \"DRC/限幅器(保护功放)\" sits in the SAME optional post-process box as the 可选 gain-EQ and is redundant with the hardware clamp. This STRENGTHENS the finding's \"quality not protection\" thesis rather than refuting it. I also searched for any documented driver mismatch requiring per-channel correction — none exists; only an open consistency unknown.\n\nMINOR NON-MATERIAL ISSUES (do not change verdict): (a) The evidence detail attributed to prd_update.md:145,171 reads \"speech energy <= 5kHz dominant\"; those lines actually establish the strong-directivity band upper limit (6kHz internal / 5kHz external) due to grating lobes (f=c/d≈6236Hz), not a speech-energy statement — the <=5kHz speech-energy point is the finding's own (reasonable) acoustic inference, not a verbatim PRD claim. The downstream conclusion (modest, speech-band band count) still holds via the directivity-band ceiling. (b) The finding slightly under-states its own case (master-bus is ~1/8 cost, and protection is doubly covered in hardware).",
    "grade_ok": true,
    "grade_fix": "Grade L3 (RECOMMENDED, master-bus) is appropriate and the L-grade discipline is sound. Optional precision tweak: in evidence item citing prd_update.md:145,171, relabel the detail as \"strong-directivity band ceiling 6kHz(internal)/5kHz(external) due to grating lobes (f=c/d≈6236Hz) -> EQ need only shape up to the directivity band; speech energy concentrated <=5kHz is an acoustics inference, not a verbatim PRD line.\" Also recommend adding the hardware-domain TVS amp-protection citation (transition_board_design.md:151,262) as positive support that the DSP-chain limiter is non-protection-grade, strengthening the L3 (quality not protection) grade. Neither change alters the L-level or the conclusion."
   }
  },
  {
   "id": "SN-4",
   "title": "Loudness/AGC is scenario-dependent: OPTIONAL for museum, RECOMMENDED for station, OPTIONAL-to-RECOMMENDED for mall",
   "claim": "Auto-loudness/AGC need varies by scenario acoustics. 博物馆讲解 (speech, quiet, close zones): OPTIONAL — operator-set fixed level suffices, AGC risks pumping on intentional pauses. 车站广播 (speech, loud reverberant, high-SPL): RECOMMENDED — variable ambient noise and the need for consistent intelligibility over distance favor slow leveling / a measured loudness target, and the high-SPL demand stresses the protection limiter most here. 商场分区 (speech + possibly background music, medium): OPTIONAL-to-RECOMMENDED — if music is in scope, a gentle AGC/loudness helps level mixed program, otherwise not needed.",
   "evidence": [
    {
     "source": "sprint2/docs/prd_update.md:72",
     "detail": "Target scenarios: 博物馆讲解、车站广播、商场分区广播 (PRD) — distinct acoustic environments"
    },
    {
     "source": "sprint3/pf8/p1b_prd_alignment.md:54-56",
     "detail": "Per-scenario character: museum = single-exhibit close directional speech; station = large space, longer aperture for distance/zoning; mall = ceiling/wall zoning with cross-talk isolation — supports differing loudness needs"
    },
    {
     "source": "sprint2/docs/prd_update.md:159-161",
     "detail": "PRD §3.1.4 SPL <=75dB(A) open-field cap + STIPA >=0.50 + uniformity <=10dB are all '待实测' — loudness control is an unproven应备 item, not a locked requirement, consistent with OPTIONAL/RECOMMENDED grading"
    },
    {
     "source": "sprint2/docs/prd_update.md:62",
     "detail": "Station vertical-mount case (table-9 invalidation) deferred to Sprint 4 — station is the most demanding/uncertain scenario, reinforcing it as the one where dynamics processing matters most"
    }
   ],
   "grade": "L3 — scenario-dependent (museum OPTIONAL / station RECOMMENDED / mall OPTIONAL-RECOMMENDED). Justification: AGC value tracks ambient-noise variability and program type, which differ by scenario; none of the three needs it to function. Caveat: 'music?' in mall is an open PRD question — if confirmed speech-only across all three, AGC drops to OPTIONAL everywhere and item-3 simplifies further.",
   "implications": "AGC/loudness should be a configurable, scenario-selectable master-bus block, not a baseline always-on cost. For compute budgeting it should be costed as a conditional/per-firmware-profile feature, not added to the worst-case baseline that threatens margin. Confirm 'music in mall scope?' with CTO — it materially changes whether loudness is in the v1 spec.",
   "dimension": "scenario-needs",
   "verdict": {
    "finding_id": "SN-4",
    "verdict": "weakened",
    "reasons": "CITATIONS VERIFIED (all exist, quoted text accurate): prd_update.md:72 (target scenarios 博物馆/车站/商场, L1/PRD fact), :159-161 (75dB(A) cap / STIPA>=0.50 / uniformity<=10dB all 待实测), :62 (车站竖装 table-9 invalidation deferred to Sprint 4), p1b_prd_alignment.md:54-56 (per-scenario install character). PRD-SILENCE CONFIRMED & is the crux: grep across BOTH cited PRD files for AGC/自动增益/响度/loudness/leveling/limiter/限幅/EQ/均衡/DRC/compressor returns ZERO substantive hits (only \"均衡档\" at :226, a geometry config-tier name, unrelated). Authoritative arch doc DOC-S4-IO-01 = \"direct-in-direct-out beamform ONLY, no EQ/limiter named\" (F7_R14_RULING_MATERIAL.md:352); item-3 is \"[L4]... NO evidence either way... NOT measurable until product DSP chain is SPEC'D\" (F7_R14_RULING_MATERIAL.md:352,396). So the finding's PRACTICAL conclusion is policy-aligned and SURVIVES: AGC/loudness must be costed as conditional/per-firmware-profile, NOT added to the worst-case baseline; this matches STEERING_HEADROOM_SCAN.md:33 (\"if PRD has no EQ -> HW-1 benefit=0\") and the established conditional posture. The finding does NOT inflate the baseline, does NOT spin silence into a locked decision, introduces NO idealized-1-cyc/MAC arithmetic (no MMAC->MCPS conversion of its own), and correctly flags the open \"music-in-mall?\" question for CTO. WHY WEAKENED (two defects): (1) L-GRADE OVERSTATED. Finding self-grades \"L3 — scenario-dependent.\" In POLICY-PROV-001 L3 = analytic/closed-form derivation. The per-scenario AGC-need verdict (museum OPTIONAL / station RECOMMENDED / mall OPT-REC) is NOT an analytic derivation — it is qualitative engineering judgment with NO cited source that discusses dynamics processing at all. It is L4 (engineering opinion, no source), not L3. The grade conflates \"scenario names are L1/PRD facts\" with \"per-scenario AGC need is L3\", but the latter has no evidentiary basis in any cited line. (2) TWO NON-SEQUITUR INFERENCES that spin silence/unrelated facts toward the conclusion: (a) evidence[3] uses :62 (vertical-mount table-9 DIRECTIVITY invalidation) to argue station is \"the one where dynamics processing matters most\" — vertical-mount directivity failure is unrelated to loudness/dynamics need; this is a leap the source does not support. (b) evidence[2] claims the §3.1.4 待实测 acoustic-compliance targets (75dB cap, STIPA, uniformity) are \"consistent with OPTIONAL/RECOMMENDED grading\" — an unmeasured SPL cap / intelligibility target says nothing about whether an AGC/limiter BLOCK is required; this is silence reframed as support. Both should be struck or explicitly demoted to \"author opinion, no source.\"",
    "grade_ok": false,
    "grade_fix": "Downgrade the per-scenario AGC-need verdict from \"L3 — scenario-dependent\" to \"L4 — engineering judgment, no source\": no cited document discusses dynamics processing, so the museum-OPTIONAL/station-RECOMMENDED/mall-OPT-REC grading is unsourced opinion, not analytic derivation. Keep L1 only for the bare scenario LIST (prd_update.md:72). Explicitly demote/strike two inferences: (a) evidence[3] (:62 vertical-mount table-9 invalidation) does NOT support \"station needs dynamics most\" — vertical-mount is a directivity-plane issue, orthogonal to loudness; relabel as irrelevant or remove. (b) evidence[2] (§3.1.4 待实测 SPL/STIPA/uniformity) does NOT evidence AGC need — an unmeasured compliance target is silent on whether a dynamics block is required; reframe as \"no PRD evidence either way\" rather than \"consistent with OPTIONAL/RECOMMENDED.\" Add the dominant fact up front: the PRD is SILENT on EQ/AGC/limiter entirely (zero hits across cited files) and DOC-S4-IO-01 specifies direct-in/direct-out beamform only — so item-3 (incl. AGC) is [L4] across ALL scenarios pending PRD spec, and the scenario-tiering is a PROPOSED default, not a graded requirement. The conditional-costing implication and CTO music-scope question are correct and should be retained verbatim."
   }
  },
  {
   "id": "SN-5",
   "title": "Minimal honest item-3 spec for this product: ONE master-bus chain (shaping EQ few-band + 1 limiter), ~8x cheaper than per-channel and well under the 250-290 MCPS worst case",
   "claim": "Synthesizing SN-1..SN-4: the spec the signal chain actually needs is a single master-bus post-processing chain placed before the D-C weight fan-out, comprising (a) a few-band speech-shaping EQ [RECOMMENDED] + (b) one protection limiter [REQUIRED], with optional scenario-selectable loudness. This is ~8x cheaper than per-channel x8 because it processes ONE signal before fan-out, and per-channel placement is acoustically contraindicated (SN-2). The frequently-cited 'rich 5-band + limiter x8ch ~250-290 MCPS' (critic R5) is an over-spec: x8 channel multiplier is wrong for this architecture and rich 5-band exceeds the speech-shaping need.",
   "evidence": [
    {
     "source": "sprint2/docs/decisions_log.md:773",
     "detail": "§8/ADDENDUM B: worst-case residual margin pulled toward ~1.0x assumes 'heavy multi-band EQ+limiter chain' at board ~30 cyc/MAC reaching ~250-290 MCPS (>150) — i.e. the threat is conditioned on a heavy x-channel chain that SN-2 shows is unnecessary"
    },
    {
     "source": "sprint2/docs/decisions_log.md:779",
     "detail": "§8 uncalculated item EQ/mixing listed as 0-150 MCPS [L4] envelope — a master-bus few-band chain sits at the LOW end of this envelope, not the heavy end"
    },
    {
     "source": "sprint3/dsp/dsp_8ch_report.md:239-249,285",
     "detail": "Chain shows post-processing as the LAST stage on the single reconstructed mono signal BEFORE the 8ch fan-out; line 285 notes ample residual compute for post-processing — master-bus placement is the natural fit"
    },
    {
     "source": "sprint2/docs/decisions_log.md:771,773",
     "detail": "Board reality 30-50 cyc/MAC envelope is mandatory for MCPS conversion; a master-bus chain runs at 1ch (not 8ch) input rate, so its MCPS is ~1/8 of the per-channel figure for the same band count"
    }
   ],
   "grade": "L3/L4 — minimal-spec recommendation (architecture L3, exact MCPS L4 pending WCET). Justification: derived deterministically from the identical-signal fan-out (SN-2); precise compute is L4 until item-3 PRD bands are fixed and WCET measured per DEC-S4-CRITERION-01. I deliberately give a RANGE-of-architecture not a point MCPS, per governance. Caveat: if CTO later requires per-channel driver-mismatch correction (needs measured unit-to-unit variance, currently [L4] unknown) the x8 multiplier returns for the EQ portion only — but the limiter must stay master-bus regardless.",
   "implications": "For DEC-S4-CRITERION-01 and the HW-1 offload decision: spec item-3 as a single master-bus chain (few-band shaping EQ + one limiter, optional loudness profile). This bounds the §8 threat far below the 250-290 MCPS worst case, likely keeping it within the 0-150 [L4] low end, so >=1.0x is more defensible than the pessimistic framing suggests. HW-1 IIR-offload remains worthwhile (a mandatory limiter + EQ exists) but its required capacity is 1-channel master-bus scale, which should be the sizing basis — recommend the workflow re-run the §8 worst case with a master-bus (not x8) item-3 assumption before locking the formal margin threshold.",
   "dimension": "scenario-needs",
   "verdict": {
    "finding_id": "SN-5",
    "verdict": "confirmed",
    "reasons": "Opened every cited source and re-derived the arithmetic. CITED LINES VERBATIM-CORRECT: decisions_log.md:773 (临时下限 >=1.0x; 250-290 MCPS conditioned on 重型多频段 EQ+限幅链 at ~30 cyc/MAC), :779 (§8 五项含 EQ/mixing 0-150 MCPS [L4]), :771 (CTO 裁定二), dsp_8ch_report.md:239-249 (post-processing as LAST stage on the single reconstructed mono signal before 8ch fan-out), :285 (\"可支持大量后处理\"). CORE CLAIM SUPPORTED: (1) the §8 worst case (250-290 MCPS) is EXPLICITLY conditioned on a per-channel x8 chain — F7_R14_RULING_MATERIAL.md:352 and :381-382 say verbatim \"rich 5-band+limiter x8 can reach ~250-290 MCPS\" / \"per-channel multiband EQ + limiter x8ch ... ~250-290 MCPS.\" So the finding's claim that the x8 multiplier drives the threat is directly textual, not inferred. (2) Identical-signal fan-out is firmly established (dsp_8ch_report.md:153 \"同一驱动通道...完全相同的信号\", :229 \"[A_k、B_k 同信号]\", :249 [注1] \"所有 8 个通道输出信号相同（仅幅度因 D-C 权重不同）\"), so a master-bus shaping EQ before fan-out is acoustically equivalent to per-channel EQ — the x8 EQ is genuinely redundant. (3) ARITHMETIC INTERNALLY CONSISTENT and envelope-disciplined: 250-290 MCPS for 5-band x8 implies ~31-36 MCPS for the same 5-band at 1ch; a FEWER-band master-bus chain is lower still (~15-30 MCPS) — squarely in the LOW end of the 0-150 [L4] envelope, far under 250-290. No idealized 1-cyc/MAC number is used; the ~30 cyc/MAC board envelope (decisions_log:234) is carried throughout, satisfying the MMAC->MCPS discipline. (4) PRD-SILENCE NOT SPUN AS DECISION: F7_R14_RULING_MATERIAL.md:352 confirms DOC-S4-IO-01 is direct-in-direct-out with NO EQ/limiter named; the finding correctly treats item-3 as PRD-pending, grades the recommendation L3/L4, gives a range-of-architecture not a point MCPS, and flags the legitimate per-channel exception (driver-mismatch correction, currently [L4] unknown). L-grades are honest (architecture L3, exact MCPS L4 pending DEC-S4-CRITERION-01 WCET). Two prior independent critic verdicts (STEERING_HEADROOM_SCAN.md:541, :356) already re-derived these same numbers (288=5x5x8x48000x30; 1.569x/2.010x recovery; item-3=0-150 [L4]; DOC-S4-IO-01 EQ-silent) and found them sound. WEAKNESS NOT BREAKING CORE: the finding's assertion \"the limiter must stay master-bus regardless\" is technically WRONG for the PROTECTION function — each of the 8 channels carries a DIFFERENT D-C amplitude weight (dsp_8ch_report.md:249 \"仅幅度因 D-C 权重不同\"), so per-driver peak levels differ and a single master-bus limiter cannot individually protect the highest-weight channel; a protection limiter ideally sits per-driver. This does NOT change the compute/sizing or §8-threat conclusion (limiters are scalar/near-zero MAC; 8 per-channel limiters add negligible MCPS — the MAC-heavy part is the EQ, which the master-bus argument handles correctly). So the headline (master-bus few-band EQ + limiter is the honest minimal spec, ~8x cheaper than rich per-channel x8, sitting at the low end of 0-150 and well under the 250-290 worst case, so the §8 threat is far below worst-case and >=1.0x is more defensible) stands as confirmed.",
    "grade_ok": true,
    "grade_fix": "Grade L3/L4 is correct and honest: architecture/placement is L3 (deterministic from the identical-signal fan-out, dsp_8ch_report.md:153/229/249), exact MCPS is L4 pending item-3 PRD fix + WCET per DEC-S4-CRITERION-01. The finding correctly inherits item-3's [L4] for the precise compute figure and gives a range-of-architecture rather than a point, per governance. No idealized-MAC numbers; ~30 cyc/MAC board envelope used throughout. No L4-dressed-as-L1/L2. No frozen-core or LOCKED-decision violation (this is a spec-time architecture recommendation; no core code touched).",
    "corrected": "Adopt the finding's recommendation with ONE correction: do NOT assert \"the limiter must stay master-bus regardless.\" Split item-3 into (a) shaping EQ = MASTER-BUS, placed once before the D-C weight fan-out (acoustically equivalent because all 8 channels carry the identical signal differing only by D-C amplitude weight — dsp_8ch_report.md:153/229/249 [L1/L2]); this is where the ~8x EQ saving comes from. (b) Protection limiter = should be PER-DRIVER/PER-CHANNEL (8 scalar limiters AFTER the D-C weight fan-out), because each channel sees a different D-C amplitude weight so per-driver peak levels differ and a master-bus limiter cannot individually protect the highest-weight driver. This correction does NOT raise the compute estimate materially: scalar limiters are near-zero MAC, so 8 of them add negligible MCPS; the §8-threat downgrade and HW-1 IIR-offload sizing conclusion (master-bus EQ scale, low end of 0-150 [L4], well under 250-290) are unchanged. RECOMMENDED ACTION for DEC-S4-CRITERION-01 / HW-1: re-run the §8 worst case with a master-bus-EQ (1ch, few-band) + per-channel-limiter (8x scalar, ~0 MAC) item-3 assumption BEFORE locking the formal margin threshold; this keeps item-3 at the low end of the 0-150 [L4] envelope (≈15-40 MCPS estimated, [L4] until WCET), so the §8 pull-toward-1.0x threat is substantially weaker than the rich-x8 framing implies and a >=1.5x or even >=2x floor becomes more defensible — but the figure stays [L4/待验证] until item-3 PRD is fixed and WCET is board-measured (C9/iron-rule-8 still binds any FIRA/offload benefit framing)."
   }
  },
  {
   "id": "CS-1",
   "title": "Teardown hardware CANNOT prove an EQ/limiter DSP stage is used — by explicit scope exclusion",
   "claim": "The competitor teardown gives zero hardware evidence either way on whether a DSP-domain EQ/limiter (item-3) post-processing stage is in the product, because the teardown deliberately excludes competitor firmware/DSP chain. The §8 item-3 estimator already records this exact gap.",
   "evidence": [
    {
     "source": "knowledge_base/competitor/full_teardown_v2.md:16",
     "detail": "Legal-status declaration: teardown explicitly does NOT include 竞品专有 DSP 固件/算法二进制 (competitor proprietary DSP firmware/algorithm binary). Hardware teardown can read pin-out/parts, not what the firmware computes."
    },
    {
     "source": "sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:352",
     "detail": "item-3 (Mixing/limiter/EQ) = 0-150 MCPS, grade [L4], basis: 'NO evidence either way. Teardown explicitly EXCLUDES competitor firmware/DSP chain (full_teardown_v2.md:16). PRD/architecture docs (DOC-S4-IO-01) describe direct-in-direct-out beamform ONLY — no EQ/limiter named.' Labeled 'the DOMINANT uncertainty.'"
    }
   ],
   "grade": "L1 (the teardown text + scope exclusion are L1 documentary facts); the downstream 'cannot prove' conclusion is L3 logical inference from those facts",
   "implications": "Competitor teardown does NOT settle the PREREQUISITE-#1 question. The EQ/limiter need cannot be reverse-engineered from competitor hardware — it must be decided from the product PRD/standards/scenario requirements, not from the teardown. This is exactly why DEC-S4-CRITERION-01 left the realtime-margin threshold pending on item-3 PRD.",
   "dimension": "competitor-standards",
   "verdict": {
    "finding_id": "CS-1",
    "verdict": "confirmed",
    "grade_ok": true,
    "reasons": "I opened both cited sources and the surrounding evidence; the core claim holds. (1) full_teardown_v2.md:16 VERBATIM CONFIRMED: the legal-status declaration line excludes 竞品专有 DSP 固件/算法二进制 (competitor proprietary DSP firmware/algorithm binary); a physical teardown reads pin-out/parts, not what firmware computes. (2) F7_R14_RULING_MATERIAL.md:352 VERBATIM CONFIRMED: item-3 (Mixing/limiter/EQ) = 0-150 MCPS [L4], basis text matches exactly including \"NO evidence either way\", the full_teardown_v2.md:16 citation, the DOC-S4-IO-01 direct-in-direct-out reference, and the \"the DOMINANT uncertainty\" label; its NB uses the board-reality 30 cyc/MAC envelope (decisions_log:234) for ~250-290 MCPS, no banned 1-cyc/MAC number. (3) DOC-S4-IO-01 (audio_io_topology.md) independently verified: topology is ADC(ADAU1979)->21569 beamform->DAC(ADAU1962A)->amps, NO row names any EQ/limiter, and gaps G-IO1~7 don't mention EQ — genuine architecture SILENCE, not a documented decision to exclude EQ; the finding correctly says the need must be DECIDED from PRD/standards/scenario, NOT spinning silence into a decision. (4) grep for EQ/limiter/biquad/DRC/均衡/限幅/后处理 across knowledge_base/competitor/ returns ZERO hits; only 固件/binary mentions are the exclusion lines 16/18 — no positive hardware evidence of a DSP EQ stage. (5) DEC-S4-CRITERION-01 linkage CONFIRMED (decisions_log.md:769/784): >=10x retired to temporary >=1.0x floor with \"正式阈值待 item-3 EQ链 PRD + WCET 实测\"; steering scan STEERING_HEADROOM_SCAN.md:33 confirms HW-1 IIR-offload benefit is conditional, =0 if PRD has no EQ. L-grades honest: teardown text/scope-exclusion graded L1 documentary (correct), \"cannot prove\" graded L3 inference (correct); no L4-as-L1/L2, no idealized-MAC arithmetic.</reasons>\n<parameter name=\"grade_fix\">L-grades are honest, no correction needed. One precision note (does NOT change verdict/grade/conclusion): \"zero hardware evidence either way\" is very slightly over-stated because teardown section 7 (full_teardown_v2.md:117-159) DOES contain 消声室 SPL-vs-frequency measurements (0deg axial 250Hz=103.2 dB, 1-4kHz 106-111 dB), a full-chain acoustic observable that includes any firmware EQ. But it cannot distinguish EQ-shaping from native 2-inch-driver/box response, so it proves neither presence nor absence of a DSP EQ stage and says nothing about OUR PRD's need. Recommend citing section 7 and adding the caveat: \"no usable hardware evidence on whether a DSP EQ/limiter stage exists, and none on our PRD's need.\"",
    "corrected": "Confirmed as written; add a one-line precision addendum: teardown section 7 SPL/frequency data is a full-chain acoustic observable but cannot distinguish DSP-EQ shaping from native driver/enclosure response and reveals nothing about our PRD's EQ need — operative claim is \"no usable evidence on whether a DSP EQ/limiter stage is used, and none on whether OUR PRD needs one; PREREQUISITE-#1 must be settled from product PRD/standards/scenario, not the teardown.\""
   }
  },
  {
   "id": "CS-2",
   "title": "ACM3128A is a plain Class-D BTL amp with NO built-in DSP/limiter in any repo evidence; DSP sits in the main ADSP-21569",
   "claim": "All in-repo evidence describes ACM3128A as a 2-channel Class-D BTL power amp characterized only by voltage/sensitivity/impedance — no datasheet field for built-in DSP, EQ, or limiter is recorded. The U5 hardware answer explicitly states the amp board has NO DSP; DSP is in the main chip. So if EQ/limiter exists it is a main-chip (ADSP-21569) DSP function, not amp hardware.",
   "evidence": [
    {
     "source": "knowledge_base/competitor/full_teardown_v2.md:80-88",
     "detail": "ACM3128A = D类立体声(双通道BTL); 4 chips/8 channels; 4.5-26V BTL; input sensitivity 0.246 Vrms; input impedance 20kOhm; efficiency >85% [估算]. No DSP/limiter/EQ feature listed (all fields are analog amp params)."
    },
    {
     "source": "knowledge_base/hardware_input/定向音柱AI数据_extracted.md:54-58",
     "detail": "U5: '否,我们开发的主芯片含 DSP(ADSP-21569)' — amp board does NOT contain DSP; DSP processing is on the main chip side. So an EQ/limiter would be an ADSP-21569 firmware stage, which a teardown of amp hardware cannot reveal."
    }
   ],
   "grade": "L1 (teardown IC silkscreen + datasheet fields + U5 hardware answer are L1/L4-datasheet documentary)",
   "implications": "There is NO hardware-offloaded EQ/limiter in the amp chain to lean on. Any EQ/limiter must run on the ADSP-21569 core or its IIR accelerator — which is precisely what the HW-1 IIR-offload optimization targets. Confirms HW-1 is a real lever ONLY IF the PRD actually mandates a DSP EQ/limiter stage; the amp hardware neither requires nor provides it.",
   "dimension": "competitor-standards",
   "verdict": {
    "finding_id": "CS-2",
    "verdict": "weakened",
    "reasons": "CORE CLAIM CONFIRMED, all cited sources opened and verbatim-verified. (1) knowledge_base/competitor/full_teardown_v2.md:80-88 describes ACM3128A solely by analog amp fields (D类立体声 BTL / 4片8通道 / 4.5-26V / 灵敏度0.246Vrms / 输入阻抗20kOhm / 效率>85%[估算]) — no DSP/EQ/limiter field, exactly as claimed. (2) knowledge_base/hardware_input/定向音柱AI数据_extracted.md:54-58 = U5 \"否,主芯片含DSP(ADSP-21569)...功放板不含独立DSP\" verbatim. (3) CORROBORATION the finding did not cite but strengthens it: sprint2/docs/sprint3_teardown_workorder.md:66 shows the U5 teardown task explicitly asked \"判断功放板是否做分频/EQ/限幅\" and read ALL board IC silkscreens — so the EQ/limiter question was specifically investigated and answered negative, not merely unmentioned. So if EQ/limiter exists it is an ADSP-21569 firmware/IIR-accelerator stage, confirming HW-1 targets a real (non-hardware-offloaded) lever under the current amp plan.\n\nL-GRADE DISCIPLINE HONEST. The load-bearing claim is the NEGATIVE (\"no DSP IC on amp board\"), resting on L1 physical teardown (all silkscreens read) + U5 L1/硬件实测 answer (repo grades it [L1/硬件实测+L4/datasheet混合], extracted.md:55; decisions_log:578 \"[L1]+[L4]\"). The positive parameter values (sensitivity/impedance) are repeatedly graded L4/datasheet in-repo (extracted.md:47; decisions_log:576). The finding's grade string \"L1 (... L1/L4-datasheet documentary)\" explicitly discloses the L4 component rather than laundering it up to L1 — no overclaim. No MMAC->MCPS arithmetic in this finding, so cyc/MAC-envelope and idealized-MAC checks N/A. No PRD-silence spun as PRD-decision.\n\nWHY WEAKENED (not confirmed): the IMPLICATION over-generalizes. \"There is NO hardware-offloaded EQ/limiter in the amp chain to lean on\" is true only for Plan A (ACM3128A), which is NOT locked — it is conditional 首选 with a live fallback. The candidate alternate TAS5825M (Plan B, DEC-S2-005 original BOM) is documented at sprint3/hardware/selfdev_bom.md:99 + :101 as \"集成 DSP ... 可软件配置增益/EQ\" and decisions_log:135 lists it as the prior Sprint-2 amp pick. So a hardware EQ path is NOT categorically absent from the amp design space; it exists conditionally if Plan B is selected. This also conditions the finding's \"EQ/limiter must run on ADSP-21569 core/IIR accelerator\" conclusion: that holds under Plan A; under Plan B part of EQ could live on the amp's integrated DSP, altering the §8 EQ-on-core / HW-1 threat model. CTO governance (decisions_log:771-784) currently assumes EQ-on-core (§8 EQ/mixing 0-150 MCPS, HW-1 offload) consistent with Plan A, but that assumption is amp-selection-dependent and not yet locked. Finding scopes its title/claim correctly to ACM3128A but its implication should say \"no hardware EQ in the ACM3128A (Plan A) amp chain; the TAS5825M alternate (Plan B) does offer integrated DSP/EQ — so the EQ-on-main-chip premise is amp-selection-dependent, not absolute.\" Finding drives no irreversible decision by itself; C9/HW-1/item-3 framing otherwise sound.",
    "grade_ok": true,
    "grade_fix": "Grade L1 is acceptable for the load-bearing NEGATIVE claim (no amp-board DSP IC = L1 teardown silkscreen + U5 L1/硬件实测), and the finding already discloses the positive parameter values are L4/datasheet. No change needed to the grade itself. Optional precision: label the negative-existence claim \"[L1 teardown/U5]\" and the amp parameters \"[L4 datasheet]\" as two distinct grades rather than a single blended \"L1\" string, to mirror repo practice (decisions_log:576/578 \"[L1]+[L4]\").",
    "corrected": "Title/claim are accurate as scoped to ACM3128A. Recommended implication rewrite: \"There is no hardware-offloaded EQ/limiter in the ACM3128A (Plan A) amp chain [L1 teardown]; the ACM3128A is a plain analog Class-D BTL amp [L4 datasheet fields]. HOWEVER the amp selection is not locked — the live alternate TAS5825M (Plan B, DEC-S2-005, selfdev_bom.md:99/101) does carry an integrated DSP with software-configurable gain/EQ. Therefore: (a) under Plan A, any EQ/limiter must run on the ADSP-21569 core or its IIR accelerator, making HW-1 (IIR-offload) the real lever and the §8 EQ-on-core threat real; (b) under Plan B, part of the EQ/limiter could be offloaded to the amp's integrated DSP, which would change the §8/HW-1 threat model. The current CTO governance (decisions_log:771-784, §8 EQ/mixing 0-150 MCPS, HW-1 offload) assumes EQ-on-main-chip, consistent with Plan A but amp-selection-dependent. Net: confirms HW-1 is a real lever IF Plan A is chosen AND the PRD mandates a DSP EQ/limiter (item-3, still pending) — both contingencies should be stated, not assumed.\""
   }
  },
  {
   "id": "CS-3",
   "title": "A board-level limiter IS required for amp protection (anti-burn) — but that is analog/protection, NOT the §8 item-3 DSP EQ/limiter compute load",
   "claim": "The hardware-input docs DO establish a genuine need for a limiting (clipping) threshold to protect the amp/drivers (防烧功放), tied to the 15Ohm DC-Re measurement (Q-①). This is a real product requirement, but it is a transition-board/clip-threshold protection function — it must not be conflated with the DSP-domain multiband EQ+limiter chain whose 0-290 MCPS load drives the §8 margin threat.",
   "evidence": [
    {
     "source": "knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md:19",
     "detail": "Q-① 15Ohm = DC Re (measured) → '转接板限幅阈值可定 → PO 签署条件满足' — limiting threshold is a transition-board protection parameter, made definable by the L1 DC-Re value."
    },
    {
     "source": "sprint3/dsp/dsp_8ch_report.md:240",
     "detail": "Signal-chain diagram lists 'DRC/限幅器(保护功放)' as an OPTIONAL post-filterbank stage whose purpose is amp protection; and 子带增益均衡(可选) to compensate driver frequency-response deviation — both flagged 可选/optional, not yet PRD-mandated."
    },
    {
     "source": "sprint3/dsp/dsp_8ch_report.md:286",
     "detail": "DSP open item: U3 (speaker impedance/amp gain) confirmation needed to re-check whether D-C weight amplitude normalization triggers amp limiting — i.e. limiting is framed as a gain-staging/protection concern."
    }
   ],
   "grade": "L1 (the protection-limiter need is from L1 hardware answers); whether it must be implemented in the DSP domain (compute-bearing) vs analog/clip is undetermined [L4]",
   "implications": "PRD item-3 must distinguish (a) a cheap protection clip/limiter (near-zero MCPS, possibly analog) from (b) a rich per-channel multiband EQ + limiter DSP chain (0-290 MCPS at board reality). Only (b) creates the §8 margin-toward-1.0x threat and justifies HW-1 IIR offload. The need for SOME limiting is real; the need for a HEAVY DSP EQ/limiter is what the PRD must actually decide.",
   "dimension": "competitor-standards",
   "verdict": {
    "finding_id": "CS-3",
    "verdict": "confirmed",
    "reasons": "All four evidence anchors verified against source and the core distinction holds.\n\n(1) knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md:19 — CONFIRMED verbatim: \"Q-① 15Ω... 直流 Re... = 真值 [L1 实测] | ✅ 转接板限幅阈值可定 → PO 签署条件满足\". Corroborated at :34 (\"限幅阈值防烧功放可定\") and in the companion doc 定向音柱AI数据_extracted.md:48 (\"转接板输出电平/阻抗匹配 + 限幅阈值依据齐备(每路负载15Ω、功放灵敏度0.246Vrms)\") and :86. The limiting threshold is consistently framed as a transition-board / gain-staging protection parameter anchored on the L1 15Ω DC-Re + ACM3128A amp sensitivity (0.246Vrms). Accurate.\n\n(2) sprint3/dsp/dsp_8ch_report.md:240 — CONFIRMED: \"DRC/限幅器(保护功放)\" is an OPTIONAL (可选) post-filterbank stage for amp protection; line 239 \"子带增益均衡(可选)...补偿喇叭频响偏差\" also flagged 可选. Neither is PRD-mandated. Accurate.\n\n(3) sprint3/dsp/dsp_8ch_report.md:286 — CONFIRMED: this is §8 待CTO决策项 item #3, U3 (喇叭阻抗/功放增益), framing limiting as a gain-staging concern (\"校核 D-C 权重幅度归一化是否触发功放限幅\"). Accurate. (Note §8 item #2 separately lists \"EQ、DRC...后处理模块扩展\" as undecided — the heavy-DSP-chain candidate. The finding correctly keeps these two apart.)\n\nL-GRADE HONEST: the protection-limiter NEED is L1-anchored (15Ω DC-Re measured); whether it must live in the compute-bearing DSP domain is correctly graded undetermined [L4]. Conservative and correct — this is the load-bearing distinction.\n\nNO ARITHMETIC/MAC VIOLATION: finding does no MMAC->MCPS conversion itself; it cites the established board-reality envelope (0-290 MCPS for the rich 5-band+limiter x8ch) correctly. No idealized 1-cyc/MAC numbers.\n\nPRD-SILENCE NOT SPUN AS DECISION: CONFIRMED clean. prd_update.md (DOC-PRD-002 v2.4) contains NO DSP EQ/limiter mandate — the only \"均衡\" hit (line 226 \"均衡档\" N=24/d=35) is an array directivity-WEIGHTING option, not a DSP EQ chain. The finding explicitly states \"the need for a HEAVY DSP EQ/limiter is what the PRD must actually decide\" — it asserts an open decision, not a fabricated PRD ruling. Correct framing, directly serving the CTO PREREQUISITE #1.\n\nIMPLICATIONS sound: the (a) cheap near-zero-MCPS protection clip vs (b) rich per-channel multiband EQ+limiter (0-290 MCPS board-reality) split is the right product-decision axis, and only (b) creates the §8 margin-toward-1.0x threat and justifies HW-1 IIR offload.",
    "grade_ok": false,
    "grade_fix": "The L-grade tagging is honest and conservative, but the CLAIM/TITLE prose overstates the evidence on ONE point: it asserts the board limiter \"is analog/protection, NOT the §8 item-3 DSP EQ/limiter\" and \"must not be conflated with the DSP-domain... chain.\" The sources do NOT establish the protection limiter is ANALOG — on the contrary, dsp_8ch_report.md:240 places \"DRC/限幅器(保护功放)\" INSIDE the DSP signal chain (as an optional stage). So the protection limiter could itself be a (trivial) DSP block. This is internally inconsistent with the finding's own L4 grade (\"whether it must be implemented in the DSP domain (compute-bearing) vs analog/clip is undetermined [L4]\"). Recommend softening the title/claim wording from \"analog/protection\" to \"a near-zero-MCPS protection clip (analog OR a trivial DSP block), NOT a heavy multiband EQ chain\". The substantive conclusion (protection-clip != heavy 5-band EQ+limiter; only the latter drives the §8 margin threat / HW-1 offload) is unaffected and stands.",
    "corrected": "CORRECTED CLAIM: The hardware-input docs (含追问回复_extracted.md:19,34; AI数据_extracted.md:48,86) establish a genuine, L1-anchored need for a clip/limiting threshold to protect amp/drivers (防烧功放), made definable by the L1 15Ω DC-Re measurement + ACM3128A amp sensitivity (0.246Vrms). This is a transition-board gain-staging/protection function (near-zero MCPS — implementable as analog OR a trivial single DSP clip). It must NOT be conflated with the §8 item-2 candidate: a rich per-channel multiband EQ + limiter DSP chain (0-290 MCPS at board reality per critic R5), which is the only variant that creates the §8 margin-toward-1.0x threat and justifies HW-1 IIR offload. Per dsp_8ch_report.md:239-240 BOTH 子带增益均衡 and DRC/限幅器 are marked 可选 (optional), and prd_update.md (DOC-PRD-002 v2.4) mandates NEITHER — so PRD item-3 must explicitly DECIDE which variant is required. The need for SOME limiting is real and L1; the need for a HEAVY DSP EQ/limiter is undecided [L4] and is the actual open PRD question."
   }
  },
  {
   "id": "CS-4",
   "title": "Applicable JY/T standard imposes a max-SPL CAP (≤75 dB(A)), uniformity ≤10 dB, and STIPA ≥0.50 — implying SPL control + FR shaping, but does NOT literally name an EQ/limiter",
   "claim": "The in-repo standard (JY/T, Table 9 directivity + Table 10 acoustic indicators) sets a ≤75 dB(A) empty-room max-SPL cap, ≤10 dB steady-SPL non-uniformity over 1k/4k coverage, STIPA ≥0.50, and GB 3096-2008 noise limits. These functionally REQUIRE output SPL control and frequency-response uniformity (which EQ/limiter deliver) but the standard text does not literally mandate a DSP limiter/EQ block.",
   "evidence": [
    {
     "source": "knowledge_base/standards/JYT_directional_speaker.jpeg",
     "detail": "Table 10 (定向扩声系统声学指标要求, 空场): 应备声压级 ≤75 dB(A); 稳态声场不均匀度 1000Hz/4000Hz 覆盖目标区域 ≤10 dB; 扩声系统语音传输指数 STIPA ≥0.50; 噪声敏感建筑物噪声限值 应符合 GB 3096-2008 第5.1条. Table 9 = horizontal directivity SPL-difference 3 grades."
    },
    {
     "source": "sprint2/docs/prd_update.md:159-162",
     "detail": "PRD §3.1.4 transcribes Table 10 verbatim: 空场最大声压级 ≤75dB(A); 不均匀度 ≤10dB; STIPA ≥0.50; GB 3096-2008. All marked '待实测/待数据 [L4]', '禁占位当达标' — none currently met, and a 117.1dB [L4] theoretical-ceiling figure vastly exceeds the 75 dB(A) cap."
    },
    {
     "source": "sprint2/docs/prd_update.md:172-173",
     "detail": "PRD §3.2 frequency-response targets: 平坦度 ±4dB (1k-8k); 灵敏度 ≥90dB SPL/1W/1m. Flatness target is the kind of spec an EQ stage is used to meet."
    }
   ],
   "grade": "L1 (the standard JPEG + PRD transcription are L1 documentary evidence of the clause text)",
   "implications": "The standard gives an INDIRECT but real basis for an EQ/limiter: a ≤75 dB(A) cap means output SPL must be bounded (limiter territory) and ±4dB flatness + ≤10dB uniformity + STIPA≥0.50 favor an EQ stage to flatten driver/room response. This supports specifying SOME item-3 stage in the PRD — but the standard does NOT prescribe it as a DSP block, so it cannot by itself force a HEAVY (250-290 MCPS) chain. The 75 dB(A) cap vs the 117 dB ceiling also flags that the protection-limiter is genuinely load-relevant.",
   "dimension": "competitor-standards",
   "verdict": {
    "finding_id": "CS-4",
    "verdict": "confirmed",
    "reasons": "All three evidence citations independently verified against the live sources:\n\n(1) knowledge_base/standards/JYT_directional_speaker.jpeg — read directly. Table 10 (表10 定向扩声系统声学指标要求, 场景=空场) shows exactly: 应备声压级 ≤75 dB(A); 稳态声场不均匀度 1000Hz/4000Hz 覆盖目标区域 ≤10 dB; 扩声系统语音传输指数 STIPA ≥0.50; 噪声敏感建筑物噪声限值 应符合 GB 3096—2008 第5.1条. Table 9 (表9) shows 3-grade (一级/二级/三级) horizontal-directivity SPL-difference at 500/1000/2000/4000 Hz × 30°/90°/180°. Exact match to the finding's transcription.\n\n(2) sprint2/docs/prd_update.md:159-162 — verbatim, marked 应备指标占位 [L4] / 待实测/待数据 / \"禁占位当达标\"; line 159 carries the 117.1dB [L4] 理论上限低置信占位 (also at :164 and :320, all explicitly marked unusable). Match.\n\n(3) prd_update.md:172-173 — 频率响应平坦度 ±4dB (1kHz-8kHz, 正轴向 1m); 灵敏度 ≥90dB SPL/1W/1m. Match.\n\nCentral claim discipline is sound and on-point for the task: I grep'd the entire PRD for EQ/limiter/限幅/均衡/biquad/DRC/parametric. The ONLY \"均衡\" hit (line 226) is \"均衡档\" = a geometry option tier (N=24/d=35mm) in a design-options table, NOT a DSP EQ/limiter block. So there is genuinely NO item-3 EQ/limiter DSP block specified in the PRD, and there is NO clause in the standard text literally naming one — the finding states this correctly and does NOT spin PRD/standard silence into a decision. It explicitly limits itself: the standard \"cannot by itself force a HEAVY (250-290 MCPS) chain.\" That conservatism is exactly right.\n\nIndependent corroboration I located that strengthens (not weakens) the finding: sprint2/docs/PROJECT_HANDOVER.md:192 records that the 限幅阈值 (limiter threshold) depends on Q-① (whether 15Ω is Re or 1kHz modulus), confirming the finding's implication that a protection-limiter is genuinely load-relevant. Also prd_update.md:270 (R12) independently lists all four Table 10 indicators as unevaluated/unmet, corroborating the 待实测 status.\n\nL-grade is honest: graded L1 only for \"documentary evidence of the clause text\" (the JPEG is a primary standard doc; the PRD transcription is faithful). It does NOT claim the product meets these specs (those are correctly L4/待实测 in-PRD). No MMAC->MCPS conversion is performed in this finding, so the cyc/MAC envelope discipline is not triggered; the 250-290 MCPS figure is referenced only as external context (critic R5), not re-derived. No idealized-1-cyc/MAC numbers appear.\n\nNo refuting evidence found. The finding is accurate, properly cited to file:line, conservative on the silence-vs-decision boundary, and correct on L-grades.",
    "grade_ok": true
   }
  },
  {
   "id": "CS-5",
   "title": "EVIDENCE GAP: the full JY/T standard text is NOT in the repo — only a single screenshot + analysis; the standard NUMBER is unknown (redacted JY/T XXXX—XXXX)",
   "claim": "The repo cannot authoritatively cite JY/T clause numbers for an EQ/limiter/SPL-control requirement: the only standard artifact is one JPEG page-pair, the standard number is shown as placeholder 'JY/T XXXX—XXXX', and a prior C8 audit already flagged the standard original was declared-ingested-but-actually-missing. Any PA/broadcast standard requiring limiting/EQ beyond this JPEG would have to be confirmed by the literature-patent teammate.",
   "evidence": [
    {
     "source": "knowledge_base/standards/JYT_directional_speaker.jpeg",
     "detail": "Table header literally reads 'JY/T XXXX—XXXX' — standard number is a placeholder/redacted; this is a draft or unidentified-version screenshot, not a citable published standard with a number."
    },
    {
     "source": "sprint3/audit/critic_c8_first_run.md:38-58",
     "detail": "C8 GAP-2: 'JY/T 标准原文档未归档入 KB. CTO 声明「标准 05-30 入库」与实际对不上.' standard_compliance_check.md is an analysis artifact and '不得充当标准原件入库'. The standards/ dir holding only the JPEG confirms full text still absent."
    },
    {
     "source": "knowledge_base/standards/",
     "detail": "Directory contains exactly one file: JYT_directional_speaker.jpeg. No PDF/docx of the full JY/T standard, no 应急广播 / EN54 / GB emergency-broadcast standard text exists anywhere in repo (grep for GB 17565/25506/EN54/应急广播 returned nothing)."
    }
   ],
   "grade": "L4 (this is an evidence-absence finding — flagging what the repo does NOT contain; needs literature-patent teammate follow-up to obtain the numbered standard + any 车站/应急广播 PA standard)",
   "implications": "Do NOT invent JY/T clause numbers or assert a hard standards mandate for a DSP EQ/limiter. The PRD EQ-spec decision can lean on the Table-10 SPL-cap/uniformity/STIPA intent (CS-4) but must mark the standard-traceability as incomplete. ACTION: route to literature-patent teammate to (a) obtain the numbered JY/T standard original, (b) check whether 车站广播/应急广播 invokes EN54/GB应急广播 standards that DO mandate limiting — currently NO such standard text is in-repo.",
   "dimension": "competitor-standards",
   "verdict": {
    "finding_id": "CS-5",
    "verdict": "confirmed",
    "reasons": "All three evidence items independently verified against repo sources; finding holds exactly as stated.\n\n(1) JPEG placeholder — CONFIRMED visually. knowledge_base/standards/JYT_directional_speaker.jpeg table header literally reads \"JY/T XXXX—XXXX\". The standard number is redacted/placeholder; this is a draft or unidentified-version screenshot, not a numbered published standard. The page shows 表9 (directivity SPL-difference) and 表10 (声学指标: SPL-cap ≤75 dB(A), 1k-4kHz coverage-zone uniformity ≤10dB, STIPA ≥0.50) but no clause number.\n\n(2) C8 GAP-2 — CONFIRMED at sprint3/audit/critic_c8_first_run.md:38-58. Text states \"JY/T 标准原文档未归档入 KB. CTO 声明「标准 05-30 入库」与实际对不上\" and \"standard_compliance_check.md 仅为分析物... 不得充当标准原件入库\". Cited line range is accurate.\n\n(3) Directory contents + no emergency-broadcast standard — CONFIRMED. knowledge_base/standards/ contains exactly 1 file (the JPEG, 341KB). Repo-wide grep for EN54 / 应急广播 / GB17565 / GB25506 / emergency-broadcast returned 0 hits. No PDF/DOCX JY/T full text exists anywhere.\n\nSTRENGTHENING CHECK (beyond finding): grep \"JY/T XXXX\" across all text files returned 0 — the placeholder number lives ONLY inside the JPEG, so no agent artifact has falsely asserted a real JY/T number. standard_compliance_check.md covers only 表9 directivity, self-labels every value as \"仿真推算，非实测\" / \"标准差值非合规认证\", and does NOT cover 表10 (the EQ/limiter-relevant SPL-cap/uniformity/STIPA intent). So the repo genuinely cannot authoritatively cite JY/T clause numbers for any EQ/limiter/SPL-control requirement.\n\nNUANCE (not a contradiction): the c8 audit text says \"无 standards 目录\" because at audit time (05-30) the dir did not yet exist; the JPEG was added afterward (file mtime 05-29 17:57, dir mtime 05-30 15:41 — JPEG present but full text still absent). This is consistent with the finding (full numbered standard still missing), not refuting it.\n\nImplication is sound and conservative: do NOT invent JY/T clause numbers or assert a hard standards mandate for a DSP EQ/limiter; route to literature-patent teammate to obtain the numbered original and check whether 车站/应急广播 invokes EN54/GB应急广播 (none in-repo currently).",
    "grade_ok": true,
    "grade_fix": "L4 grade is correct and honest for an evidence-ABSENCE finding. An absence claim (\"repo does NOT contain X\") cannot be L1/L2/L3 — there is no measurement, simulation, or closed-form derivation underlying it; it is by nature a gap-flag requiring external (literature-patent) follow-up to resolve, which is exactly how it is framed. No idealized-MAC numbers, no MMAC->MCPS conversions, no PRD-silence spun as a PRD-decision (the finding explicitly warns against spinning the standard into a hard mandate). No grade change needed. Optional precision: could note the placeholder number appears ONLY in the JPEG (0 text-file occurrences), reinforcing that no artifact has yet fabricated a clause number — but this strengthens rather than alters the L4 absence finding."
   }
  },
  {
   "id": "CS-6",
   "title": "Competitor 0° SPL data is consistent with SPL bounding being a real product concern, but NO competitor EQ/limiter can be inferred from SPL alone (PF-9 red line)",
   "claim": "The competitor's measured 0° axial SPL (106-111 dB @ 1-4kHz, far above the 75 dB(A) standard cap) shows max-SPL is a live concern for this product class, lending circumstantial support to needing output limiting/level control — but it is forbidden and impossible to infer the competitor's EQ/limiter firmware from SPL measurements.",
   "evidence": [
    {
     "source": "knowledge_base/competitor/full_teardown_v2.md:131-132",
     "detail": "Competitor 0° axial SPL: 250Hz=103.2dB; voice band 1-4kHz steady 106-111 dB [L1 anechoic, per SPL_anechoic_measurement_archived.md]. These exceed the JY/T Table-10 空场 ≤75 dB(A) cap by ~30+ dB, so SPL/level management is non-trivial for the category."
    },
    {
     "source": "knowledge_base/competitor/SPL_anechoic_measurement_archived.md:14",
     "detail": "'禁从此竞品 SPL 反推 BW (PF-9 红线, C7)' — measurement attribution = competitor (CTO confirmed); the SPL data is the ONLY competitor performance evidence and may not be reverse-engineered into design parameters (extends to: cannot infer EQ/limiter presence from SPL)."
    }
   ],
   "grade": "L1 (competitor SPL is L1 anechoic measurement); the 'EQ cannot be inferred from SPL' is L3 inference reinforced by the PF-9 governance red line",
   "implications": "Competitor SPL evidence reinforces that output-SPL control is a genuine category concern (supports a limiter in PRD item-3) but provides ZERO evidence on the EQ/limiter compute footprint. The EQ-spec decision must be grounded in the PRD's own scenario/standard requirements, not in any competitor-firmware inference. Net: hardware+SPL evidence makes a LIMITER plausibly required; an EQ FLATTENING stage is supported by Table-10 uniformity/flatness intent; neither pins the MCPS scale that drives the §8 threat.",
   "dimension": "competitor-standards",
   "verdict": {
    "finding_id": "CS-6",
    "verdict": "weakened",
    "reasons": "Two halves; only one survives.\n\nSOLID HALF (confirmed): The headline \"no competitor EQ
```
