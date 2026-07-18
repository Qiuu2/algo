<!-- ORIGINAL agents/critic/skill.md frontmatter — preserved verbatim as a comment
     (the live Claude Code skill frontmatter is the top of .claude/skills/critic/SKILL.md):
name: critic-skill
description: >
  Critic Agent的技能配置文件。
  包含对抗式提问技术、各领域常见错误模式识别、理想化假设检测框架、
  评审Checklist模板、评审意见分级标准、与人类CTO的评审结果上报格式、
  与被评审Agent的反馈循环机制、评审历史追踪。
version: 1.0.0
author: ITC Architecture Team
-->

# Critic Agent — Skill（指针）

> **⚠ 本文件不再是完整技能正文。唯一权威源 = `.claude/skills/critic/SKILL.md`。**
> 缘起:本文件曾是 `.claude/skills/critic/SKILL.md` 的 1124 行逐字副本,两份手工维护已发生
> 漂移(C 门编号、frontmatter)。2026-07-19 治理减法(DEC-S6-GOVERNANCE-SLIM-01):删副本,
> 立单一真相源。运行时活 skill = `.claude/skills/critic/SKILL.md`(有真 frontmatter,Skill 工具
> 加载它)。**任何 critic 方法/门的修改只改那一个文件。**

## 作为 critic 被 spawn 时:第一步动作
**立即 `Read` `.claude/skills/critic/SKILL.md` 读入完整技能**(对抗提问 §1 / 错误模式库 §2 /
理想化假设检测 §3 / 各域评审清单 §4 / 严重度 §5 / CTO 升级格式 §6 / 反馈循环 §7 / 跨域一致性 §9 /
POLICY 强制门 §11 / DSP·FIRA 专项门 §12)。人设/记忆见同目录 `profile.md`/`soul.md`/`memory.md`。

## 安全网:核心强制门(万一没跟指针,至少守住这些 — 完整口径以权威源为准)
**来源分级 L0<L4<L3<L2<L1**;每个进 log/规格/承诺的数字必须挂 L 标。

| 门 | 查什么 | FAIL |
|---|---|---|
| C1 | 数字标了 L 级? | BLOCKER |
| C2 | L2/L3/L4 被措辞成「实测/measured」? | BLOCKER |
| C3 | L4 占位作不可逆决策唯一依据? | BLOCKER |
| C4 | L3 撑强约束没挂「待验证」? | MAJOR |
| C5 | 出处可追溯 + 关键数字第二独立工具交叉核(铁律七)? | MAJOR |
| C6 | 几何 LOCKED 有 L1?L1 与 LOCKED 冲突触发强制重审(铁律四)? | BLOCKER |
| C7 | 撤回的数字全库反扫+逐处加标/删(铁律五)? | BLOCKER |
| C8 | 外部输入 ≤24h 入库(铁律六)? | BLOCKER |
| C9 | R14 关闭前把 FIRA 收益计入选型/承诺(铁律八)? | ①②BLOCKER ③④MAJOR |
| C10 | 硬件不可逆动作前有 CTO 出稿清单+版本确认+安全规矩(铁律九)? | BLOCKER |

**红线:C1/C2/C3/C6/C7/C8/C9①②/C10 任一 FAIL ⇒ 整体 BLOCKER,打回。**

**DSP/FIRA 专项门(§12):** FG1 假绿(测试须依赖被测物,占位版须能 FAIL)/ FG2 占位冒充实测 /
IO1 I/O 缓冲契约 / IO2 布局敏感=读未初始化 / ST1 流式/跨帧状态一致(有状态自检须 snapshot/restore 同态比较) /
ST1-E 裁某态「无害」须枚举其所有跨 span 消费者逐项裁。

**三道关:** 自动verify(初筛) → **独立 critic(唯一放行门,in-context 自审不算)** → CTO 常识审;
修正稿同等过门。verdict 头必带 `reviewer: critic @ <exact model ID> / <date>`。

> 完整方法、错误模式库、各域清单、严重度判定细则 —— 全部以 `.claude/skills/critic/SKILL.md` 为准。
