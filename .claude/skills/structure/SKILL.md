---
name: structure
description: >-
  Structure / mechanical engineering expert for the ITC column speaker. Use for
  enclosure CAD, box acoustic design, material selection, vibration control, and
  DFM/DFA review. Obeys CLAUDE.md governance (L-grading, geometry LOCKED needs L1
  per C6). NOTE: domain is currently DORMANT (bare eval column, no enclosure work
  ever run) — the A section is intentionally empty pending real runs; do not treat
  B/C as project fact.
---

<!-- CANONICAL source of record for the structure skill (DEC-S6-GOVERNANCE-SLIM-04, 2026-07-20);
     agents/structure/skill.md is a pointer — edit ONLY here. Persona/memory: agents/structure/{profile,soul,memory}.md -->
<!-- 旧内嵌 frontmatter 存史（已删）: name "Structure Engineer Agent Skills" / version 1.0.0 /
     "Kimi/Hermes Agent Skill标准" / 认证级别 L3(专家级) —— 重复且失效，去重。 -->

# 结构/机械工程专家 Agent — 技能（删假留骨版）

> **状态：域休眠。** 本项目至今是**裸评估柱**（无外壳/机械工程真跑）——结构域**没有可蒸馏的真料**，故 A 段空置。
> **本次做的是"删假留骨"**（roadmap#5 蒸馏法只做得了"删假"这一半；"提真"须待真跑）：删掉原 883 行里的**虚构基建 + 假 ID + 错产品假设**（逐条见文末「已移除」，铁律五留痕），留一个诚实薄骨架。
> **别把 B/C 当项目事实**：B 是通用 ME 方法（Claude 已知，非本项目蒸馏），C 是缺口。任何数字进规格/log 先挂 L 标。

---

# A. 项目真本事（蒸馏所得，每条带出处）
- **（空）——结构域无真跑，无可蒸馏真料。** 不编造。
- **唯一真锚 = 阵列几何 N16 / d55mm[L1拆机实测] / L825mm / broadside**，但这是**声学/DSP 域**的 LOCKED 决策，结构域只是未来承接方，本身零产出。`← DEC-S3-GEOM-01`
- 几何 LOCKED 落 C6 门：任何承载/外壳设计若触及阵列间距/长度 → 触发铁律四强制重审，须 L1。`← CLAUDE.md C6/铁律四`

# B. 通用骨架（通用 ME 方法，**非本项目蒸馏**；Claude 已知，要用先按真跑蒸馏）
- **CAD/出图**：自顶向下参数化装配；GD&T + ISO 2768 一般公差 + 第三角投影 —— 标准做法。
- **材料选型**：按刚度质量比 E/ρ、阻尼、成本、工艺多目标权衡；ABS/ABS+PC/PC/PA-GF/铝6061/MDF 物性为教科书值（**进规格须 L1 供应商数据**）。
- **箱体声学**：密闭/倒相/传输线各有闭式（Qtc、fb、¼波长）——**但适用性存疑：本品是定向直线阵列音柱，未必用倒相箱**，箱体形态须先由声学域定型（现无）。
- **振动控制**：加强筋（间距 8-12×壁厚、顶部 ≤0.6×根部防缩痕）、阻尼/去耦、模态避开工作频段 —— 标准 ME。
- **DFM/DFA**：注塑拔模/壁厚均匀、CNC 内 R≥刀具半径、DFA 减件/防错/防呆 —— 标准可制造性门；具体逐项清单 Claude 可按需生成。

# C. 缺口 / 未跑过（保持薄、不编造；要用先补真料）
- 外壳/箱体**从未设计**；无 FEM、无材料选型定型、无 DFM 评分、无跌落/振动/密封测试计划。
- **结构-声学耦合未定**：本品是否需要箱体、还是开放式阵列承载，待声学域定。
- 全部待**外壳工程立项**后从真跑蒸馏进 A。

---

# 已移除（删假留骨砍掉的虚构/错料，存档说明 — 铁律五留痕）
- **虚构 agent 基建（两处，非仅 §6）**：§6 全节 `JSON-RPC over MessageBus`、`agent.acoustic.simulation`(@669)、`IDF/EMN/EMP`、各 `agent_id`；**外加 §2 箱体声学里内嵌的一段协作块** `interface: agent.acoustic.simulation`(@317)、`protocol: 参数双向绑定`、`sync_frequency: 每日同步` —— 本项目**无此消息总线/RPC**，agent 通信按 CLAUDE.md §2 通信协议。（`agent.acoustic.simulation` 在原文 **317 和 669 两处**都出现。）`← 原 SKILL.md:314-335, 664-842`
- **虚构工具接口 + 假输出**：`agent.cad.interface`、`/data/models/*.step`、`quality_score:97`、`item_count:45`、`total_weight:850` —— 凭空捏造。`← 原:189-214`
- **假件号 / 占位数**：`STR-2401-001-A = 结构域-24年01项目`、单重 `125.5g`、`XXX g` —— 编造/占位。`← 原:168-214,398-415`（另 `[x,y,z]` 占位坐标在 §6 @691/743，已含在上面 §6 范围内）
- **错产品假设**：倒相箱/传输线 `internal_volume 2500ml / port_diameter 50mm / port_length 80mm` —— 按倒相书架箱写死，本品是定向直线阵列音柱、箱体形态未定。核心方法移入 B 并标"适用性存疑"。`← 原:254-312,680-720`
- **重复/失效 frontmatter + 假认证**：内嵌第二份 `version 1.0.0` / `Kimi/Hermes 标准` / `认证级别 L3(专家级)` —— 去重存史（见顶部注释）。`← 原:13-37`
- **注**：原 §1-5 的通用 ME 方法**本体**（CAD 规范 / 材料物性 / 振动 / DFM 100 项）**非虚构、是正确通用知识**，已压缩进 B（Claude 已知，不逐条复制）。**例外：§2 内嵌 314-335 那段"协作块"是虚构 agent 基建，不在"非虚构"之列，已在上面第 1 条移除。** 完整原文仍在 git 历史（本次 commit 前版本）可查。
