# 下一 Session 启动指南（NEXT SESSION BOOTSTRAP）

**文档 ID**：DOC-BOOTSTRAP-01
**日期**：2026-05-30
**用途**：**self-contained** —— 下一对话只需读本文件即可接手 ITC 定向音柱项目。CTO 据"启动条件"复制对应 prompt 即可启动。
**当前状态**：Sprint 3 桌面阶段 **~96% 完成**；剩余卡外部数据（T/S / 3W 口径 / 箱体实测 / EZKIT / 消声室 / COMSOL）。Agent Team 待命，零自动推进。
**权威文件根**：`/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/`（下文路径均相对此根）。

---

## Part 0 — 项目一句话 + 几何/系统基线（先读这个）
- **产品**：相控阵线阵定向音柱（DAS + 4 子带波束形成），跑在 ADI **ADSP-21569**（SHARC+ 单核 1GHz）。场景：博物馆/车站/商场分区广播，**水平安装**（SC-S3-GEOM-02）。
- **几何基线（单一，LOCKED）**：**N=16 / d=55mm[L1 拆机实测] / L=825mm / Dolph-Cheby −20dB / broadside-only**（DEC-S3-GEOM-01）。8 路 A/B 对称串联驱 16 喇叭（每路 2 只串联 15Ω[L1]，单只 7.4Ω/3W[L1]）。
- **DSP**：4 子带（500-1k/1k-2k/2k-4k/4k-8k）/ dyadic 树形半带 FIR / 48kHz / 8ch TDM（BCLK 12.288MHz）；算力裕量桌面实算 **17×(16ch)/33×(8ch)[L2]**（待 EZKIT cycle 实测[L1]）；端到端延迟 **12.53ms[L3 仿真]**（规格 <30ms，待 EZKIT）。
- **标准目标**：JY/T 表9 **二级保底（锁定承诺）+ 一级冲刺（待实测，非承诺）**；强指向上限 **6kHz(对内)/5kHz(对外)**（栅瓣 6.2-8k 降级）。

---

## Part 1 — 启动条件 → 可直接复制的 prompt 模板

> 每段 prompt CTO 可直接粘贴启动新对话。所有任务**强制 POLICY-PROV-001 v1.5**（七条铁律 + C1–C8 双向门禁 + L 标签 + 双轨/三轨独立工具核 + 撤回值禁用）。

### 触发 A：T/S 真值回报（BL/Re/Fs/Qts）→ X2 全套 SPL 三轨重算
```
@project-manager T/S 真值已回（BL/Re/Fs/Qts 见附）。启动 X2 SPL 重算：
- 读：knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md（KB-HW-002，喇叭 7.4Ω/3W[L1]、频响 120Hz-18kHz 厂家标称[L4]、后腔无吸音 R13）；
     sprint3/acoustic/sweep_d55.py（现 117dB 占位 L317-371）；decisions_log DEC-S3-DSP-05（SPL 降级）/ R3 / R13。
- 任务：用真实 BL/Re/Fs/Qts 建电声模型，重算绝对 SPL（替换 117dB[L4 占位]）；含 R13 后腔无吸音对后向修正；含频响 −10dB/−3dB 口径（Q-④）。
- teammate：acoustic-simulation 主跑 + critic 复核；POLICY v1.5 三轨核（numpy + MATLAB-agent + MATLAB-CTO ~/matlab-agent/）。
- 归档：sprint3/audit/X2_spl_recompute.md。
- 严格限定：d=55/broadside/isotropic（SC-S3-GEOM-01/02）；SPL 标 [L2-半解析]，BL/Re 标 [L1]；禁撤回值（d=30/14.9/19.1/19.2/16.0）；禁从竞品 SPL 反推 BW（PF-9/C7）；铁律六核 T/S 文档 24h 入库。
```

### 触发 B：3W 口径回报（Q-0：连续 RMS / 峰值 / 失真前）→ X2 SPL 单/双口径
```
@project-manager 3W 口径已回 = [RMS/峰值/失真前]。启动 X2 SPL（路径3）：
- 若单口径明确 → 单口径精算 SPL；若仍含糊 → 双口径并行版（输出 SPL 108-119dB 区间，口径待定）。
- 读：KB-HW-002（Q-① 15Ω 直流 Re[L1]、Q-② 额定 10W 预估[L4]）；hardware_followup_queries.md（Q-0 去向）。
- teammate：acoustic-simulation + critic 三轨；归档 sprint3/audit/X2_spl_recompute.md；标 [L2-半解析]。
- 限定同触发 A。注：3W 口径仅影响功率项，完整 SPL 仍需 T/S（触发 A）。
```

### 触发 C：5 追问其余回报（Q-④箱体宽深 / Q-②③ 额定功率阻抗 / Q-⑦）→ PRD v2.5 + COMSOL 输入补
```
@project-manager 硬件追问 [Q-④箱体宽深 / Q-② / Q-③ / 频响-3dB口径] 已回。
- 读：sprint3/audit/hardware_followup_queries.md（追问去向）；comsol_geometry_input.md（COMSOL 待补输入）；KB-HW-002。
- 任务：① 箱体宽深 → 补 comsol_geometry_input.md（COMSOL 立项硬前置）；② 频响 -3dB 口径明确 → PRD 低频规格增补（prd_update.md v2.4 → v2.5）；③ 额定功率/阻抗 → BOM/限幅更新。
- teammate：project-document + critic（C8 核入库）；归档对应文件。
- 限定：L 标签（实测[L1]/datasheet[L4]）；铁律六 24h 入库；撤回值禁用。
```

### 触发 D：EZKIT 到货 → R1 MCPS 实测（命门）+ L1 窗口任务
```
@project-manager EZKIT 到货。启动 L1 实测窗口（命门 R1 优先）：
- 读：sprint3/pf8/L1_test_window_tasklist.md（T1 触发器 DAG）；sprint3/dsp/tree_filterbank.{c,h} + tree_verify.c + tree_verify_adversarial.c（树形 C 已落地+饱和修复）；decisions_log DEC-S3-PROC-01（芯片采购冻结，21565 vs 21569 待此实测）。
- 任务（优先序）：① R1 树形 C 移植 EZKIT + CCES cycle-counter 实测真实 MCPS（含 cache/中断，判 ≥10× + 定 21565/21569，关闭 PF-1）；② SHARC 定点 SNR 逐 bit（PF-4 L1）；③ 端到端延迟硬件确认（PF-2）；④ 节点① 溢出真实触发率 + headroom 标定；⑤ WCET/DMA/SPORT（需 U4 拆机 TDM）。
- 前置：转接板 PO（6 项已闭环，Q-① 已满足签署条件——若仍未发 PO 需先解）。
- teammate：dsp-algorithm 主跑 + critic；归档 sprint3/audit/ezkit_*.md；MCPS 标 [L1-EZKIT]；铁律二回填 DEC-S1-004/DEC-S3-PROC-01。
```

### 触发 E：消声室档期定 → 后向/BW/栅瓣/balloon/SPL 实测
```
@project-manager 消声室档期 = [日期]，样机 = [竞品壳验证线/自研]。启动消声室实测：
- 读：sprint3/audit/standard_compliance_check.md（标准 12 点，180° R9 不可评待实测）；decisions_log R5/R6/R9/R10/R11/R13；sprint3/acoustic/pf8/p0a1_grating_criterion.md（栅瓣 6.2-8k）。
- 任务（按 R 优先）：① **R9 180° 后向实测**（标准达标决定性，含 R13 后腔无吸音真实后向）；② R5 BW@1k 裁超指向去留（DEC-S3-DSP-06）；③ R6 栅瓣 6.2-8k 对标；④ R10 2k/90°（PF-6 可能自然达一级 ≥25dB → 关 R10；否则启用子带标量加深 A3 选项1.5 零成本）；⑤ R11 4k/30° 高频；⑥ 垂直/俯仰 balloon；⑦ 绝对 SPL 校准（对标竞品 0° 106-111dB）；⑧ 不均匀度/STIPA（表10）。
- teammate：testing + acoustic-simulation + critic；归档 sprint3/audit/anechoic_*.md；实测标 [L1-消声室]；**禁从 SPL 反推 BW（PF-9/C7）**。
```

### 触发 F：COMSOL 立项（Q-④箱体宽深到位后）→ 有限障板/箱体衍射
```
@project-manager COMSOL 流程就绪（箱体宽深 Q-④ 已回）。启动 COMSOL 建模：
- 读：sprint3/audit/comsol_geometry_input.md（几何输入 + Q-③盆口非Sd/Q-④箱体/Q-⑤后腔无吸音）；audit §3 盲区2（有限障板衍射）；R9/R11/R13。
- 任务：① 825mm 有限障板 + 边缘衍射建模（疑似竞品 4kHz 反常主因 PF-6）；② 180° 后向辐射（R9，含 R13 后腔无吸音边界）；③ 公差 MC 真实障板版（替 cosine 乐观下界）。
- teammate：acoustic-simulation 主跑 + critic；归档 sprint3/audit/comsol_*.md；标 [L2-COMSOL]；盆口≠Sd（Q-⑤）须按物理盆口估辐射面。
```

---

## Part 2 — Agent Team 工作记忆（权威，勿凭印象）

### 2.1 已 LOCKED / 已定决策（`sprint2/docs/decisions_log.md`）
| 决策 ID | 内容 | 状态 |
|---------|------|------|
| DEC-S1-001 | 技术路线 = 相控阵线阵 DAS + 子带 | ✅ LOCKED |
| DEC-S1-002 | 指向性仅 ≥1kHz 要求 | ✅ LOCKED |
| DEC-S1-004 | DSP 芯片 = ADSP-21569（量产 21565 vs 21569 待 EZKIT，冻结 DEC-S3-PROC-01）| ✅ LOCKED（不可逆，依据待 L1 回填）|
| DEC-S2-002 | DSP = dyadic 树形半带 FIR | ✅ LOCKED |
| ~~DEC-S2-006~~ | ~~d=30mm~~ | ⚠️ **作废（PF-8）**，由 DEC-S3-GEOM-01 取代 |
| DEC-S2-007/008/009 | N=16 / Dolph-20 / 4 子带 | ✅ LOCKED |
| DEC-S2-012 | 延迟 <5ms→<30ms | ✅ LOCKED-IN-PRINCIPLE（待市场对齐）|
| DEC-S2-013 | 1kHz 超指向 ε=0.01 | 📋 降级/fallback（待消声室）|
| **DEC-S3-GEOM-01** | **撤销 d=30 → 统一 d=55/N=16/L=825mm** | ✅ LOCKED（强约束）|
| **SC-S3-GEOM-01** | 硬约束：PRD 不新增 6-8kHz 强指向（否则触发 d 重议）| ✅ 永久边界 |
| **SC-S3-GEOM-02** | 硬约束：音柱**水平安装**（竖装→表9 失效）| ✅ LOCKED |
| DEC-S3-DSP-03 | broadside-only 接受（无电子偏转）| ✅ APPROVED |
| DEC-S3-DSP-05 | SPL 117dB 降级"低置信/不可对外"| ✅（待 T/S）|
| DEC-S3-DSP-06 | 1kHz 超指向去留待消声室；半角误读已纠正（BW=全角=2×半角）| ✅ RESOLVED |
| DEC-S3-PROC-01 | 量产芯片采购冻结，待 EZKIT MCPS | ✅ 闸门 |
| DEC-S3-P0-01 | P0 桌面：树形 C 落地 + MCPS 17×/33× + 超指向 d=55 | ✅ 归档 |
| DEC-S3-PF4-01 | PF-4 定点桌面闭环（正面案例）| ✅ |
| DEC-S3-GEOM-01 配套 / DEC-S3-HWDOC-01 | WO-S3-001 6/6 文档闭环（KB-HW-002）| ✅ |
| Gate 1 / Gate 2 | 阵列方案 PASSED / ADSP-21569 CLOSED | ✅ |

### 2.2 已撤回 / 作废数字（**禁裸引，引用须带"已撤回/作废"警示，C7**）
- **竞品 BW 14.9° / 19.1° / 16.0°** = SPL 4 点插值反推、**F-AC-01 已撤回**（PF-9）；竞品只实测 SPL 无 BW（`knowledge_base/competitor/SPL_anechoic_measurement_archived.md` KB-SPL-001 = 竞品 SPL 原件，CTO 已确认）。
- **19.2°** = ITC 自仿 N16/d25 行**张冠李戴**（非竞品非实测）。
- **d=30mm / L=450mm / 超指向 d=30 全套 / BW@2k=26.8° / 栅瓣临界 5.7kHz** = **PF-8 作废**（视觉估测 L0），归档不删，不可作依据。
- **算力纸面 27×/49×** = 已被 17×/33× 取代（PF-1）。

### 2.3 假性完成 PF-1~9（全闭环，`simulation_coverage_audit.md §2`）
PF-1 算力纸面 / PF-2 延迟标实测 / PF-3 SPL 占位 / PF-4 定点声明（桌面闭环）/ PF-5 CCES 夸大 / PF-6 高频 isotropic / PF-7 超指向 d=30 / **PF-8 估测当实测+冲突未重审** / **PF-9 撤回未传播**。

### 2.4 LESSON 库（`agents/critic/memory.md`）
LESSON-006 反推让位实测 / 007 分级制度 / 008 半角误读 / **009 PF-8 估测当实测** / **010 PF-9 撤回未传播** / **011 制度内化（C7 零 BLOCKER + 抓 BLOCKER）** / **012 三轨独立工具核（WNG 12dB bug 抓出）** / **013 信息透明义务（入手未入库）**。

### 2.5 POLICY-PROV-001 谱系（v1.5，`sprint2/docs/POLICY-PROV-001_数字来源分级制度.md`）
- **五级来源**：L0 目测 / L1 实测 / L2 仿真 / L3 解析 / L4 占位。
- **七条铁律**：①L4/L0 不作不可逆/LOCKED ②L3 强约束挂待验证 ③措辞红线（实测仅 L1）④L1↔LOCKED 冲突强制重审禁并存 ⑤撤回全库传播（出站）⑥信息透明义务/外部输入 24h 入库（入站）⑦关键数字双轨独立工具核。
- **Critic C1–C8**：C1 标签 / C2 冒充实测 / C3 L4 独撑不可逆 / C4 L3 强约束待验证 / C5 可追溯（扩双轨核）/ C6 几何门禁 / **C7 撤回传播（出站）** / **C8 入库传播（入站）**。
- **数字生命周期两端闭环**：入站 C8/铁律六 ⇄ 出站 C7/铁律五 + 入口 C6 + 冲突铁律四 + 双轨核铁律七。
- **CTO 外部接收声明义务**：Sprint 收尾 CTO 声明近 1 周外部接收清单（C8 唯一基线，无声明→ESCALATE）。

### 2.6 R-list（R1–R13，`decisions_log.md` carry-forward 表）
| R | 等级 | 状态 |
|---|------|------|
| R1 | P0（命门）| 算力裕量桌面 17×/33×，待 EZKIT cycle 实测[L1] |
| ~~R2~~ | 关闭 | 延迟规格放宽 |
| R3 | 中 | 绝对 SPL 占位 117dB[L4]，待 T/S+电声模型 |
| ~~R4~~ | 关闭（PF-8）| d=30 BW moot |
| R5 | 主路线唯一 BW | BW@1k=29.28°[L2] 压线 0.72°，超指向去留待消声室 |
| R6 | 中 | 栅瓣 6.2-8kHz，规格降级 6k/5k |
| R7 | watch | PRD 6-8k 强指向→触发 d 重议（SC-S3-GEOM-01）|
| R8 | 中 | 标准 500/30° 一级裕量仅 +0.86dB[L2] |
| R9 | **高（标准 gating）** | 180° 后向 isotropic 不可评，待 COMSOL+消声室 |
| R10 | 中 | 2k/90° 仅二级（缺 1.99dB）；子带标量加深零成本兜底（A3 选项1.5）或 PF-6 实测自然关 |
| R11 | 中 | 4k/30° 一级 +1.01dB 且 isotropic 乐观 |
| R12 | 待评估 | 表10 应备SPL/不均匀度/STIPA/GB3096 未评估 |
| **R13** | 中（加剧 R9）| 后腔无吸音棉 → 后向辐射乐观 5-10dB |

---

## Part 3 — 严格守门规则（C1–C8 双向门禁 + 双轨核 + L 标签）

| 门禁 | 触发判级 |
|------|---------|
| **C1** 标签 | 进决策/结论/规格数字未标 L 等级 → BLOCKER |
| **C2** 冒充 | L2/L3/L4/L0 称"实测/measured" → BLOCKER |
| **C3** L4 独撑 | L4/L0 作不可逆决策唯一依据 → BLOCKER |
| **C4** L3 待验证 | L3 撑强约束未挂"待 L1/L2" → MAJOR |
| **C5** 可追溯（含双轨核）| 出处不可追溯 / 关键决策数字未第二独立工具核 → MAJOR |
| **C6** 几何门禁 | 几何/尺寸 LOCKED 前无 L1（用 L0 目测）→ BLOCKER |
| **C7** 撤回传播（出站）| 撤回值残留未带警示 / 撤回未全库反扫 → BLOCKER |
| **C8** 入库传播（入站）| 外部输入超 24h 未入库 / CTO 无外部接收声明 → BLOCKER/ESCALATE |
| **双轨/三轨核（铁律七）** | 关键几何/算力/统计/标准数字须 numpy + MATLAB 交叉核，不一致 BLOCKER |
| **L 标签** | 所有进决策数字带 [L0-L4 + 出处] |

> **每次评审报告须显式列 C1–C8 结论**；C1/C2/C3/C6/C7/C8 任一 FAIL = BLOCKER 打回。
> **铁律四**：L1 实测与 LOCKED 冲突 → 强制重审、禁并存。**铁律五/六**：出站撤回 / 入站入库均须传播。

### 关键路径与方法约定（防复发）
- **BW = 全角 −6dB = 2×单边半角**（半角误读教训 LESSON-008；用 `beamwidth()` 第一返回值）。
- **禁从竞品 SPL 反推 BW**（= PF-9 同款病，BLOCKER）；竞品只有 SPL[L1] 无 BW。
- **datasheet ≠ 实测**：8Ω/10W/频响标称 = [L4]，不解锁 SPL 重做。
- **三轨工具**：numpy/scipy + MATLAB-agent（mcp__matlab__，R2026a + chebwin + Phased Array）+ MATLAB-CTO（`~/matlab-agent/p01/p02/sim_d55`）。
- **socket 防护**：teammate 长跑（>200s）易断 → 拆小段派单 / 验证类 PM 直跑 Bash。

### 关键文件索引（self-contained 补充，需深入时读）
- 决策：`sprint2/docs/decisions_log.md`（v2.0+）｜审计：`sprint2/docs/simulation_coverage_audit.md`（v2.3）｜交接：`sprint2/docs/PROJECT_HANDOVER.md`（v1.2）｜制度：`sprint2/docs/POLICY-PROV-001_数字来源分级制度.md`（v1.5）｜critic：`agents/critic/skill.md §11`(C1-C8) + `memory.md`(LESSON-006~013)
- Sprint 3 收尾包：`sprint3/audit/SPRINT3_DESKTOP_CLOSURE.md`（总索引）+ panorama / standard_compliance_check / matlab_independent_verification / A1·A2·A3 / comsol_geometry_input / hardware_followup_queries
- 制度复盘：`sprint3/pf8/PF8_retrospective.md`（§7 持久记忆治理 + §8 实战检验附录 A/B/C）｜L1 任务：`sprint3/pf8/L1_test_window_tasklist.md`
- 硬件：`knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md`(KB-HW-002) ｜竞品：`knowledge_base/competitor/full_teardown_v2.md` + `SPL_anechoic_measurement_archived.md`(KB-SPL-001)｜标准：`knowledge_base/standards/JYT_directional_speaker.jpeg`
- 树形 C：`sprint3/dsp/tree_filterbank.{c,h}` + `tree_verify.c` + `tree_verify_adversarial.c` + `sprint3/dsp/pf4/`

### 待 CTO 动作（跨 session 挂起）
- 转接板 PO 正式签署（6 项闭环、Q-① 满足，待 CTO 拍板，建议挂 Q-① 直流 Re 为限幅条件）。
- 5 追问余项（Q-④箱体宽深 / Q-②③额定功率阻抗 / Q-0 3W 口径）— CTO 微信硬件团队跟进。

---

## Part 4 — CTO 视角补充段（CTO 手写，启动时元层级注入）

> *（以下留白，由 CTO 在 clear 本对话前手写："CTO 视角的关键洞察 + 本轮对话过程教训"，作为下次启动的元层级输入。）*

```
[CTO 手写区]



```

---

*DOC-BOOTSTRAP-01，PM 生成 2026-05-30，待 Critic 复核。self-contained：下次启动只读本文件即可接手。所有路径/决策 ID/POLICY 条款精确，无 TBD。SPL PDF attribution = 竞品（CTO 确认）。*
