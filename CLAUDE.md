# ITC Enterprise Multi-Agent System
# 定向音柱（Column Speaker）研发项目 — Claude Code Agent Team 入口

## 系统概述

本项目采用四层 + 一横切的企业级多 Agent 协作架构，专为音频硬件研发设计。
**项目背景**：定向音柱产品研发，相控阵算法 + ADI SHARC DSP，目标场景 博物馆讲解 / 车站广播 / 商场分区广播。

> - 完整架构：`SKILL.md` ｜ 治理全文：`sprint2/docs/POLICY-PROV-001_数字来源分级制度.md`
> - **按需参考**（启动 prompt / 文件结构 / 完整状态机 / 历史状态）：`PROJECT_REFERENCE.md`
> - **现状/基线以** `sprint2/docs/decisions_log.md` + 记忆 `MEMORY.md` + `sprint3_status.md` **为准**（本文件不再嵌入会过时的状态快照）。

---

## 🔒 治理铁律（所有 teammate 必吃 — POLICY-PROV-001 核心）

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

### 九铁律（一句话）
1. 数字有来源身份证（L 标）｜2. L3 撑强约束须挂待验｜3. 不可逆决策 L1 或 L2+签字｜4. L1 与 LOCKED 冲突→强制重审、禁并存｜5. 撤回必须全库传播（声明+反扫+加标/删，三步缺一不生效）｜6. 外部输入 24h 入库｜7. 关键数字双轨独立工具核｜**8. R14 关闭前 FIRA/加速器收益一律标 `[L4/待验证]`、不计入任何选型/流片/客户承诺；选型只许引已坐实的纯核口径**（违反=BLOCKER，C9 守门）｜9. 硬件不可逆动作须先有 CTO 确认的操作清单+物理版本确认+安全硬规矩。

> **三道关（POLICY v1.8 §4B，流程闸，非铁律）**：workflow 产出含修正稿须 自动verify→独立critic门→CTO常识审，不得假设"修过即对"（缘起 R8/R9 修正稿自带新错）。

### DSP/FIRA 专项（本线在用 — critic 必查）
- **假绿**：测试必须依赖被测物。`out==in` 代数恒等（PR telescoping）的端到端 CRC 验不了滤波/加速器 → 比对须取依赖滤波的中间值（子带）+ 证明占位版会 FAIL。
- **占位冒充实测**：compute 被 stub（memset 0/#else/未接线）还能 PASS = L4 冒充 L1 → 必跑占位版确认其 FAIL。
- **I/O 缓冲契约**：加速器段输入须 ≥ `ntaps+window-1` 个**已初始化**样本（防过读）；后处理须恰填 `out_count`（防双重抽取半填）；共用 scratch 段间清零；DMA 输出读前 cache 失效。
- **布局敏感=读未初始化/越界**：compute 没改、只改无关全局却输出变 → BLOCKER 直到隔离。

---

## Agent Team 结构

启动时按下表组建；每个 agent 加载 `agents/<role>/{profile,soul,skill,memory}.md`（4 件套）。完整角色定义见 `SKILL.md §6`。

| 角色 | 加载目录 | 核心能力 |
|---|---|---|
| **Team Lead：project-manager** | `agents/project-manager/` | 接 CTO PRD、WBS/DAG、调度、汇总；**唯一对 CTO 汇报节点** |
| teammate-1 acoustic-simulation | `agents/acoustic-simulation/` | 阵列指向性/波束形成/房间声学/COMSOL |
| teammate-2 dsp-algorithm | `agents/dsp-algorithm/` | 波束算法/定点化移植/ADI SHARC/实时性 |
| teammate-3 hardware-design | `agents/hardware-design/` | 原理图/PCB layout/选型/EMC/热设计 |
| **teammate-4 critic（横切）** | `agents/critic/`（profile/soul/memory）；**skill 唯一权威源 = `.claude/skills/critic/SKILL.md`**（旧 `agents/critic/skill.md` 为指针） | 对抗式评审、质量守门；**所有产出必须先过 Critic** |
| （按需）structure / testing / literature-patent / project-document | `agents/<role>/` | 见 `SKILL.md §6` |

> 启动整支团队的标准 prompt 见 `PROJECT_REFERENCE.md §1`。

---

## Agent 通信协议（完整见 `SKILL.md` 第 2 节）

**关键规则**：
1. 所有产出必须经过 Critic Agent 评审后才能提交给 Team Lead。
2. Team Lead 是唯一向人类汇报的节点。
3. Teammates 可以直接互相通信（peer-to-peer），critic 可直接 rebut 任何 teammate。
4. 发现 BLOCKER 级别问题 → 立即停止并上报人类。

> 任务状态机 `PENDING→ASSIGNED→IN_PROGRESS→REVIEW(Critic)→PASSED/FAILED/ESCALATED`，完整见 `SKILL.md §3` / `PROJECT_REFERENCE.md §2`。

---

## 项目约束（所有 Agent 必须遵守）

### 技术约束
- DSP 平台：ADI SHARC 系列（**已 LOCKED ADSP-21569**，见 decisions_log）。
- 开发工具：CrossCore Embedded Studio（CCES，免费）+ SHARC Audio Toolbox。
- 算法语言：C（最终在 ADI 上运行），Python（仿真验证）。
- 声学仿真：Python pyroomacoustics（首选）+ Octave/MATLAB（交叉验证）。

### 法律约束
- 不可直接抄袭竞品 PCB 和外壳设计；算法借鉴需注意专利边界；ADI reference design 可合法使用。

### 质量约束（Critic 执行）
- 声学仿真：仿真 vs 实测偏差 ≤ ±3dB｜DSP：定点化 vs 浮点偏差 ≤ 1e-10（线性算法）｜硬件：通过 ERC/DRC，热设计留 20% 余量｜所有产出：先过 Critic，再交人类 Review。

> 资源约束（Max plan / 设备 / 消声室外租）见 `PROJECT_REFERENCE.md`。

---

## 人类 CTO 介入点

以下情况必须暂停，等待人类（总工）决策：
1. **Gate 1**：首次阵列设计方案审定（PM + Critic 评审通过后提交）。
2. **Gate 2**：ADI 芯片型号最终确认（不可逆采购决策）。
3. **ESCALATED**：任何 BLOCKER 超过 4 小时未解决。
4. **预算超支**：任何单次 Agent Team 任务费用超过 $10。

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

*ITC Enterprise Agent Team — CLAUDE.md v1.1.0（2026-07-19 分层瘦身 DEC-S6-GOVERNANCE-SLIM-02：参考/过时状态移入 `PROJECT_REFERENCE.md`，资源约束移入参考；红线/护栏**文字**零改动，仅去掉 🔒 标题里已过时的版本号「v1.7」——内文本就含 v1.8 三道关/C10）。原 v1.0.0 生成 2026-05。适配 Claude Code v2.1.32+，Agent Teams experimental。*
