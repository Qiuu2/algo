# ITC Enterprise Multi-Agent System
# 定向音柱（Column Speaker）研发项目 — Claude Code Agent Team 入口

## 系统概述

本项目采用四层 + 一横切的企业级多 Agent 协作架构，专为音频硬件研发设计。
完整架构定义见：`Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/SKILL.md`

**项目背景**：定向音柱产品研发，基于相控阵算法 + ADI SHARC DSP 平台，
目标场景为博物馆讲解 / 车站广播 / 商场分区广播。

---

## 🔒 治理铁律（所有 teammate 必吃 — POLICY-PROV-001 v1.7 核心）

> 全文：`sprint2/docs/POLICY-PROV-001_数字来源分级制度.md` + `.claude/skills/critic/SKILL.md`。
> 此处是每个 teammate 每次都要遵守的红线摘要，不是全文替代。

### L 来源分级（严格度 L0 < L4 < L3 < L2 < L1）
- **L1 实测**（板上/EZKIT/仪器/measured）— 可支撑任何决策，含不可逆。
- **L2 仿真/工具**（numpy/MATLAB/scipy/COMSOL/host 桌面跑）— 强约束可；不可逆须 L2+风险声明+CTO 签字。
- **L3 解析**（闭式/手算）— 方向性可；进强约束须挂「待 L1/L2 验证」。
- **L4 占位**（placeholder/stub/假设/未实测收益）— 仅探索；**绝不作不可逆决策唯一依据**；不得无标进 decisions_log。
- **L0 目测**（拍脑袋/无任何测量）— **仅探索讨论，严禁任何 LOCKED 决策**（比 L4 更严，PF-8 病根）。
- 决策权重红线：不可逆→L1（或 L2+签字）｜强约束→L2 起（L3 须挂待验）｜方向性→L3｜探索→L4（不进 log）。**可逆性不得自我降档**规避等级。

### 强制门 C1–C10（任何产出/评审逐项给 PASS/FAIL + 证据）
| 门 | 查什么 | FAIL |
|---|---|---|
| C1 | 进 log/规格/承诺的数字标了 L 级？ | BLOCKER |
| C2 | 有无 L2/L3/L4 被措辞成「实测/measured」？ | BLOCKER |
| C3 | 有无 L4 占位作不可逆决策唯一依据？ | BLOCKER |
| C4 | L3 撑强约束却没挂「待验证」？ | MAJOR |
| C5 | 出处可追溯？关键数字第二独立工具交叉核（铁律七）？ | MAJOR |
| C6 | 几何尺寸 LOCKED 有 L1？L1 与 LOCKED 冲突触发了强制重审（铁律四）？ | BLOCKER |
| C7 | 撤回的数字全库反扫+逐处加标/删（铁律五）？ | BLOCKER |
| C8 | 外部输入 ≤24h 入库（铁律六）？ | BLOCKER |
| C9 | R14 关闭前没把 FIRA 收益计入选型/承诺（铁律八）？ | ①②BLOCKER ③④MAJOR |
| C10 | 硬件不可逆动作前有 CTO 出稿清单+版本确认+安全规矩（铁律九）？ | BLOCKER |

**红线：C1 / C2 / C3 / C6 / C7 / C8 / C9①② / C10 任一 FAIL ⇒ 整体 BLOCKER，打回，不得进下一阶段。**

### 八铁律（一句话）
1. 数字有来源身份证（L 标）｜2. L3 撑强约束须挂待验｜3. 不可逆决策 L1 或 L2+签字｜4. L1 与 LOCKED 冲突→强制重审、禁并存｜5. 撤回必须全库传播（声明+反扫+加标/删，三步缺一不生效）｜6. 外部输入 24h 入库｜7. 关键数字双轨独立工具核｜**8. R14 关闭前 FIRA/加速器收益一律标 `[L4/待验证]`、不计入任何选型/流片/客户承诺；选型只许引已坐实的纯核口径**（违反=BLOCKER，C9 守门）｜9. 硬件不可逆动作须先有 CTO 确认的操作清单+物理版本确认+安全硬规矩。

> **三道关（POLICY v1.8 §4B，流程闸，非铁律）**：workflow 产出含修正稿须 自动verify→独立critic门→CTO常识审，不得假设"修过即对"（缘起 R8/R9 修正稿自带新错）。

### DSP/FIRA 专项（本线在用 — critic 必查）
- **假绿**：测试必须依赖被测物。`out==in` 代数恒等（PR telescoping）的端到端 CRC 验不了滤波/加速器 → 比对须取依赖滤波的中间值（子带）+ 证明占位版会 FAIL。
- **占位冒充实测**：compute 被 stub（memset 0/#else/未接线）还能 PASS = L4 冒充 L1 → 必跑占位版确认其 FAIL。
- **I/O 缓冲契约**：加速器段输入须 ≥ `ntaps+window-1` 个**已初始化**样本（防过读）；后处理须恰填 `out_count`（防双重抽取半填）；共用 scratch 段间清零；DMA 输出读前 cache 失效。
- **布局敏感=读未初始化/越界**：compute 没改、只改无关全局却输出变 → BLOCKER 直到隔离。

---

## Agent Team 结构

当 Claude Code 启动 Agent Team 时，按以下结构组建团队：

### Team Lead（团队领导）
**角色**：Project Manager Agent（项目总调度）
**加载文件**：
- `Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/agents/project-manager/profile.md`
- `Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/agents/project-manager/soul.md`
- `Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/agents/project-manager/skill.md`
- `Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/agents/project-manager/memory.md`

**职责**：
- 接收来自人类总工（CTO）的 PRD 和任务需求
- 分解为 WBS 任务，构建 DAG 依赖图
- 调度和派发任务给各领域 teammate
- 整合所有 teammate 的产出，汇总给人类

### Teammates（领域专家）

**teammate-1：声学仿真专家**
- Profile：`agents/acoustic-simulation/profile.md`
- Soul：`agents/acoustic-simulation/soul.md`
- Skill：`agents/acoustic-simulation/skill.md`
- Memory：`agents/acoustic-simulation/memory.md`
- 核心能力：阵列指向性仿真、波束形成、房间声学、COMSOL 操作

**teammate-2：DSP 算法专家**
- Profile：`agents/dsp-algorithm/profile.md`
- Soul：`agents/dsp-algorithm/soul.md`
- Skill：`agents/dsp-algorithm/skill.md`
- Memory：`agents/dsp-algorithm/memory.md`
- 核心能力：波束形成算法、定点化移植、ADI SHARC 开发、实时性优化

**teammate-3：硬件设计专家**
- Profile：`agents/hardware-design/profile.md`
- Soul：`agents/hardware-design/soul.md`
- Skill：`agents/hardware-design/skill.md`
- Memory：`agents/hardware-design/memory.md`
- 核心能力：原理图设计、PCB layout、元器件选型、EMC、热设计

**teammate-4：Critic 评审员（横切所有领域）**
- Profile：`agents/critic/profile.md`
- Soul：`agents/critic/soul.md`
- Skill：`agents/critic/skill.md`
- Memory：`agents/critic/memory.md`
- 核心能力：对抗式评审、质量守门、所有产出必须先过 Critic

---

## 启动 Agent Team 的标准 Prompt

将以下 prompt 粘贴进 Claude Code，即可启动完整的 Agent Team：

```
Read the CLAUDE.md and the full system architecture in
Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/SKILL.md.

Create an agent team for the ITC directional column speaker project:

Team lead: Project Manager Agent
  - Load profile/soul/skill/memory from agents/project-manager/
  - Decompose the task, build DAG, coordinate teammates

Teammates (work in parallel):
  1. acoustic-simulation: Array directivity and beam-forming simulation
  2. dsp-algorithm: Algorithm feasibility and SHARC compute budget check
  3. critic: Review all outputs before they reach the team lead

Today's task (illustrative; current locked baseline is d=55mm per DEC-S3-GEOM-01):
Validate the baseline array design for a 16-element linear array:
  - Element spacing d = 55mm (L1 teardown-measured; d=30mm was a Sprint2 visual-estimate, retired by PF-8/DEC-S3-GEOM-01)
  - Working frequency: 500Hz to 8kHz (strong directivity downgraded to ≤6kHz; 6.2-8kHz has grating lobes)
  - Target: -6dB beamwidth ≤ 30° at 2kHz
  - DSP target: ADSP-21569 SHARC+ (check compute feasibility)

Workflow:
1. acoustic-simulation calculates directivity pattern and beamwidth
2. dsp-algorithm checks if DAS beamforming fits SHARC compute budget
3. Both submit outputs to critic for adversarial review
4. Team lead synthesizes findings into a structured report for CTO

Constraints:
  - Each teammate: max 10 minutes, max $3 budget
  - Stop immediately if any teammate exceeds budget
  - All outputs must pass critic before reaching team lead
```

---

## 项目约束（所有 Agent 必须遵守）

### 技术约束
- DSP 平台：ADI SHARC 系列（优先 ADSP-SC589 或 ADSP-21569）
- 开发工具：CrossCore Embedded Studio（CCES，免费）+ SHARC Audio Toolbox
- 算法语言：C（最终在 ADI 上运行），Python（仿真验证）
- 声学仿真：Python pyroomacoustics（首选）+ Octave/MATLAB（交叉验证）

### 资源约束
- AI 工具：2 个 Claude Max plan（非 24×7 运行，人工监督）
- 实验设备：基础测量话筒 + 多通道声卡（初期）
- 消声室：外租（每次约 2000-5000 元）

### 法律约束
- 不可直接抄袭竞品 PCB 和外壳设计
- 算法借鉴需注意专利边界
- ADI reference design 可合法使用

### 质量约束（Critic 执行）
- 声学仿真：仿真 vs 实测偏差 ≤ ±3dB
- DSP：定点化 vs 浮点偏差 ≤ 1e-10（线性算法）
- 硬件：通过 ERC/DRC，热设计留 20% 余量
- 所有产出：先过 Critic，再交人类 Review

---

## Agent 通信协议

参考完整协议：`itc-enterprise-workflow/SKILL.md` 第 2 节

**关键规则**：
1. 所有产出必须经过 Critic Agent 评审后才能提交给 Team Lead
2. Team Lead 是唯一向人类汇报的节点
3. Teammates 可以直接互相通信（Agent Team 的 peer-to-peer 能力）
4. 发现 BLOCKER 级别问题 → 立即停止并上报人类

---

## 任务状态机

```
PENDING → ASSIGNED → IN_PROGRESS → REVIEW (Critic) → PASSED → COMPLETED
                                                    → FAILED → 打回修正
                                                    → ESCALATED → 人类介入
```

---

## 当前项目状态（MEMORY）

**项目阶段**：阶段 ① 需求建模 + 阶段 ③ 算法仿真并行启动

**已确认的技术决策**：
- 技术路线：相控阵线阵（DAS + 子带波束形成）
- DSP 平台：ADI SHARC（待确认具体型号）
- 竞品参考：已拆机分析，主芯片为 ADI 系列（型号待确认）
- 开发策略：参考 ADI reference design，自研核心波束形成算法

**锁定基线一览**（2026-05-29 几何统一修正，DEC-S3-GEOM-01）：
- **自研基线 = 竞品几何**：N = 16 / **d = 55mm**（拆机 L1 实测真值）/ L = 825mm / Dolph-Chebyshev -20dB / 8 路 A/B 对称串联 / broadside-only
- d=30mm 已撤销（PF-8：系 Sprint2 视觉估测错误值，DEC-S2-006 作废）；受 CTO 硬约束 **SC-S3-GEOM-01** 永久边界约束（PRD 不新增 6–8kHz 强指向硬需求为前提，否则触发 d 重议）

**待决策**：
- ADI 具体芯片型号（ADSP-SC589 vs ADSP-21569）
- 阵元数量（16 vs 24）

**当前最高优先级任务**：
- AC-WP01：阵列指向性仿真（声学 agent 执行）
- DSP-WP01：波束形成算法可行性评估（DSP agent 执行）

---

## 人类 CTO 介入点

以下情况必须暂停，等待人类（总工）决策：

1. **Gate 1**：首次阵列设计方案审定（PM + Critic 评审通过后提交）
2. **Gate 2**：ADI 芯片型号最终确认（不可逆采购决策）
3. **ESCALATED**：任何 BLOCKER 超过 4 小时未解决
4. **预算超支**：任何单次 Agent Team 任务费用超过 $10

---

## 文件结构参考

```
/home/it1234/algorithm_speaker/
└── Kimi_Agent_多Agent协作方案/
    └── itc-enterprise-workflow/
        ├── SKILL.md                    ← 系统入口（完整架构定义）
        ├── agents/
        │   ├── project-manager/        ← Team Lead
        │   │   ├── profile.md
        │   │   ├── soul.md
        │   │   ├── skill.md
        │   │   └── memory.md
        │   ├── acoustic-simulation/    ← 声学 Teammate
        │   ├── dsp-algorithm/          ← DSP Teammate
        │   ├── hardware-design/        ← 硬件 Teammate
        │   ├── structure/              ← 结构 Teammate
        │   ├── testing/                ← 测试 Teammate
        │   ├── literature-patent/      ← 专利文献 Teammate
        │   ├── project-document/       ← 文档 Teammate
        │   └── critic/                 ← 横切评审（必须）
        └── tools/
            ├── code-execution/         ← Python 代码执行
            ├── matlab/                 ← MATLAB/Octave 仿真
            ├── cad-interface/          ← CAD 工具接口
            ├── web-search/             ← 网络检索
            └── database/              ← 数据库访问
```

---

## 安全护栏（Agent Team 运行规则）

```
1. 每个 teammate 独立预算上限：$3（超出立即停止）
2. 单次 Agent Team 任务总预算：$10
3. 时间上限：任何单个 teammate 任务最长 15 分钟
4. 禁止 sub-sub-agent 递归：teammate 不得再生成 sub-agent
5. 所有文件写操作：先生成"操作建议"，等人类确认后执行
6. 遇到 BLOCKER：立即停止并以结构化格式向人类报告
7. 三道关（POLICY v1.8 §4B）：任何 workflow 产出（含修正稿）须 自动verify(初筛)→独立critic门→CTO常识审，缺一不可；不得假设"修过即对"（修正稿同样过门）
```

---

*ITC Enterprise Agent Team — CLAUDE.md v1.0.0*
*生成时间：2026-05*
*适配：Claude Code v2.1.32+，Agent Teams experimental*

---

## 最新状态（2026-05-26 晚）

当前节点：Sprint 3 启动准备中

下次启动时执行：
1. 等用户回来汇报硬件团队拆机结果
2. 拿到 6 项未知量数据后评估转接板可行性
3. 决定是否进入完整 Sprint 3 流程

预计算力消耗：0（等待人工输入，零自动推进）

> 详见 `sprint3_status.md`（状态快照）与 `sprint2/docs/sprint3_teardown_workorder.md`（拆机工单 WO-S3-001）。
> 已批准并行：① 自研主线（EZKIT 立即下单 + 喇叭 datasheet 收集）② 快速验证线（先拆机逆向 6 项未知量）。
> 闸门锁定：转接板设计 PO 待《6 项未知量确认报告》签署；Codec/功放/电源采购待 PCB v0.1 冻结。
