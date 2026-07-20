# ITC 项目参考（按需加载 — 非每轮热路径）

> 本文件收纳**不需要每轮读**的参考内容,从 `CLAUDE.md` 分出来以减轻每轮认知负荷
> （DEC-S6-GOVERNANCE-SLIM-02,2026-07-19）。**每轮必读的红线/护栏仍在 `CLAUDE.md`。**
> 完整架构见 `SKILL.md`;治理全文见 `sprint2/docs/POLICY-PROV-001_数字来源分级制度.md`。
> **一条规则、一行审计都没删——只是搬到按需加载。**

---

## 1. 启动 Agent Team 的标准 Prompt

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

## 2. 任务状态机（完整见 SKILL.md 第 3 节）

```
PENDING → ASSIGNED → IN_PROGRESS → REVIEW (Critic) → PASSED → COMPLETED
                                                    → FAILED → 打回修正
                                                    → ESCALATED → 人类介入
```

---

> **技术/法律/质量约束留在 `CLAUDE.md` 热路径**（护栏材料，critic 每次评审用），本文件不复制以免 SSOT 漂移。
> **资源约束（非每轮，收纳于此）**：AI 工具 = 2 个 Claude Max plan（非 24×7 运行，人工监督）；实验设备 = 基础测量话筒 + 多通道声卡（初期）；消声室 = 外租（每次约 2000–5000 元）。
> DSP 平台锁型（21569）等现状**以 `decisions_log` 为准**（本文件不复述状态）。

---

## 3. 文件结构参考

```
/home/it1234/algorithm_speaker/
└── Kimi_Agent_多Agent协作方案/
    └── itc-enterprise-workflow/
        ├── CLAUDE.md                   ← 每轮热路径（红线/护栏/名册）
        ├── PROJECT_REFERENCE.md        ← 本文件（按需加载参考）
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
        │   └── critic/                 ← 横切评审（skill 权威源在 .claude/skills/critic/SKILL.md）
        └── tools/
            ├── code-execution/         ← Python 代码执行
            ├── matlab/                 ← MATLAB/Octave 仿真
            ├── cad-interface/          ← CAD 工具接口
            ├── web-search/             ← 网络检索
            └── database/              ← 数据库访问
```

---

## 4. ⚠ 历史状态快照（可能过时 — 现状以 `sprint2/docs/decisions_log.md` + 记忆 `MEMORY.md` + `sprint3_status.md` 为准）

> 以下两块是从 CLAUDE.md 搬来的旧状态快照,**写于 2026-05,早已被后续 Sprint 超越**（现已 Sprint 6，
> 芯片 LOCKED 21569，波束已上板）。保留仅作历史,**不得作现状依据**。
> **⚠ 例外**：其中「**锁定基线 N16 / d55 / L825 + SC-S3-GEOM-01 永久边界**」本身**仍现行**（权威在
> `decisions_log` DEC-S3-GEOM-01 / 记忆 `sprint3-d55-baseline`）；过时的只是「阶段 / 待决策 / Sprint 节点」措辞。

### 当前项目状态（MEMORY，2026-05 写，已过时）
**项目阶段**：阶段 ① 需求建模 + 阶段 ③ 算法仿真并行启动
**已确认的技术决策**：相控阵线阵（DAS + 子带波束形成）/ DSP 平台 ADI SHARC / 竞品已拆机（ADI 系）/ 参考 ADI reference design 自研核心波束
**锁定基线一览**（2026-05-29 DEC-S3-GEOM-01）：**自研基线 = 竞品几何** N=16 / **d=55mm**（拆机 L1 真值）/ L=825mm / Dolph-Chebyshev -20dB / 8 路 A/B 对称串联 / broadside-only；d=30mm 已撤销（PF-8 视觉估测错误，DEC-S2-006 作废）；受 **SC-S3-GEOM-01** 永久边界约束（PRD 不新增 6–8kHz 强指向硬需求为前提，否则触发 d 重议）
**待决策**（已过时）：ADI 型号（**现已 LOCKED 21569**）/ 阵元数量（16 vs 24）
**当前最高优先级**（已过时）：AC-WP01 阵列指向性仿真 / DSP-WP01 波束可行性

### 最新状态（2026-05-26 晚，已过时）
当前节点：Sprint 3 启动准备中。下次启动：等硬件拆机结果 → 拿 6 项未知量评估转接板 → 决定是否进完整 Sprint 3。
> 详见 `sprint3_status.md` 与 `sprint2/docs/sprint3_teardown_workorder.md`（拆机工单 WO-S3-001）。已批准并行：①自研主线（EZKIT 下单 + 喇叭 datasheet）②快速验证线（拆机逆向 6 项未知量）。闸门：转接板 PO 待《6 项未知量确认报告》；Codec/功放/电源采购待 PCB v0.1 冻结。

---
*ITC PROJECT_REFERENCE — 从 CLAUDE.md v1.0.0 分出,2026-07-19（DEC-S6-GOVERNANCE-SLIM-02）。适配 Claude Code v2.1.32+，Agent Teams experimental。*
