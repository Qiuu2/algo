# digest_H — agents / 团队与治理搭建 / memory 阅读摘要

> ⚠ 公开版说明（2026-10-02）：本摘录按写时原文照录，里面会出现已撤回或已被推翻的数字（如 d=30、17×/33×、1.5k/3k/6k 子带标签、86–144 MCPS、6.4×）。采信任何数字前，以 `sprint2/docs/decisions_log.md` 和 `sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md` 为准。

> 生成：2026-10-02（只读摘录，未改动任何仓库或记忆文件）。
> 仓库根 `R` = `/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow`；记忆目录 `M` = `/home/it1234/.claude/projects/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/memory/`。
> 引用格式 `路径:行`。**可信度顺序**：decisions_log > 执行单/runbook > git commit > memory（最低）。凡与 decisions_log / git 交叉核过的，在文中标「✓核」；没核的标「未核」；我自己的推断标「〔推断〕」。
> **先看一眼最要紧的 3 条**（细节在 §6）：
> 1. `agents/*/{profile,soul,skill,memory}.md` 绝大部分是 2026-05-24 的 Kimi 通用模板（含 2023–2024 假日期、假项目号、假设备序列号），真料只占少数行段；§3.0 给了「真/假行号表」，**别把模板段当项目事实引用**。
> 2. 「POLICY v1.8」有两个含义：POLICY 文件的 v1.8=§4B 三道关（2026-06-04）；critic skill 页脚的 v1.8=§12 DSP/FIRA 门（2026-06-03）。写手册时必须分开说。
> 3. git 历史只从 2026-06-02 开始；05-24→06-01 的一切日期只能靠文件 mtime / decisions_log 文字 / memory，不是 git 证据。

---

## 0. 读了什么

### 0.1 范围与读法
- 范围内文件**全部读完**：根 3 个 + `.claude/` 8 个 + `agents/` 37 个（36 个 .md + 1 个 `skill.md.backup_20260528_113013`）+ 记忆目录 22 个（含 `MEMORY.md`）= **70 个文件**。
- 大文件分段读完（`.claude/skills/critic/SKILL.md` 1157 行分 4 段；`agents/critic/memory.md` 793 行分 3 段；其余同理），无遗漏行段。
- 日期规则：git 已跟踪的给「首次入库」(`git log --diff-filter=A`) 与「末次提交」；未跟踪的标「untracked」；磁盘 mtime 另列（`agents/*/soul.md` 等 mtime=2026-05-24 是 Kimi 原包时间，见 §1.1）。记忆文件按 `stat` 的 birth/mtime + frontmatter `originSessionId` / `modified` 列。
- 本机有**两个** `knowledge_base/`：仓库内（gitignore，`R/knowledge_base/`，含 ezkit 1280 个文件）和仓库外（`/home/it1234/algorithm_speaker/knowledge_base/`，含 papers 23 个文件）。memory 里写的 `knowledge_base/papers/...`、`knowledge_base/measurements/...` 指的是**仓库外那个**（见 §6-D7）。

### 0.2 表 A：仓库内文件（路径相对 `R`）
| 路径（相对 R） | bytes | 行 | 读 | 首次入库(git) | 末次提交(git) | 磁盘 mtime | 性质 / 可引用性 |
|---|---|---|---|---|---|---|---|
| `CLAUDE.md` | 9350 | 131 | 全文 | 89bed86 2026-06-04 | bdc9126 2026-07-20 | 2026-07-20 | 真（治理红线/名册/护栏） |
| `SKILL.md` | 23643 | 502 | 全文 | 43aad40 2026-06-09 | 1656e02 2026-07-20 | 2026-07-20 | 混合：Kimi 骨架(2026-05-24)+2026 改动（§6 L326、§10 L477-489、§11 L493-498） |
| `PROJECT_REFERENCE.md` | 6790 | 118 | 全文 | ed83668 2026-07-20 | ed83668 2026-07-20 | 2026-07-19 | 真（参考；§4 为已标过时的 2026-05 快照） |
| `.claude/hooks/cto-gate-softconfig.sh` | 2938 | 66 | 全文 | b3ea58e 2026-06-10 | b3ea58e 2026-06-10 | 2026-06-10 | 真（唯一 hook） |
| `.claude/settings.json` | 285 | 16 | 全文 | b3ea58e 2026-06-10 | b3ea58e 2026-06-10 | 2026-06-10 | 真（hook 注册） |
| `.claude/settings.local.json` | 1005 | 22 | 全文 | 未入库(untracked) | - | 2026-06-06 | 真（本机权限白名单，untracked） |
| `.claude/skills/critic/SKILL.md` | 51500 | 1157 | 全文 | 46a9899 2026-06-04 | 1656e02 2026-07-20 | 2026-07-20 | 混合：L40-1038 通用方法(模板)；L1042-1139 真 |
| `.claude/skills/dsp-algorithm/SKILL.md` | 13708 | 115 | 全文 | 46a9899 2026-06-04 | ade79e1 2026-07-20 | 2026-07-20 | 真（A 段逐条出处，07-20 项目化） |
| `.claude/skills/structure/SKILL.md` | 5284 | 50 | 全文 | 46a9899 2026-06-04 | c8eeb08 2026-07-22 | 2026-07-22 | 删假留骨（A 空置，域休眠） |
| `.claude/skills/testing/SKILL.md` | 12026 | 99 | 全文 | 46a9899 2026-06-04 | c9c3f91 2026-09-02 | 2026-09-02 | 真（A 段逐条出处，07-22 项目化） |
| `.claude/team_config.md` | 10492 | 85 | 全文 | 53bd875 2026-06-03 | b6bc5fe 2026-09-02 | 2026-09-02 | 真（名册/纪律/变更留痕） |
| `agents/acoustic-simulation/memory.md` | 20666 | 498 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-29 | 混合：L10-464 模板；L466-499 真 |
| `agents/acoustic-simulation/profile.md` | 5147 | 126 | 全文 | 43aad40 2026-06-09 | 1656e02 2026-07-20 | 2026-07-20 | 模板（+07-20 §7 降级注） |
| `agents/acoustic-simulation/skill.md` | 29173 | 830 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-28 | 混合：L1-628 模板；L630-829 真(MATLAB,2026-05) |
| `agents/acoustic-simulation/skill.md.backup_20260528_113013` | 19227 | 627 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-28 | Kimi 原版快照（2026-05-28 备份） |
| `agents/acoustic-simulation/soul.md` | 6828 | 160 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/critic/memory.md` | 41817 | 793 | 全文 | 218ead7 2026-06-06 | cd113e2 2026-09-29 | 2026-09-29 | 混合：见 §3.0（真=L350-358/492-691/775-793） |
| `agents/critic/profile.md` | 9355 | 285 | 全文 | 43aad40 2026-06-09 | 1656e02 2026-07-20 | 2026-07-22 | 模板（+07-20 §5/§6 注） |
| `agents/critic/skill.md` | 3227 | 51 | 全文 | 46a9899 2026-06-04 | c3dcd50 2026-07-19 | 2026-07-19 | 指针（07-19）+C 门安全网 |
| `agents/critic/soul.md` | 9816 | 300 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-07-22 | 模板 |
| `agents/dsp-algorithm/memory.md` | 20017 | 640 | 全文 | 218ead7 2026-06-06 | 218ead7 2026-06-06 | 2026-06-06 | 混合：真=L298-340(部分)、L629-640 |
| `agents/dsp-algorithm/profile.md` | 5921 | 140 | 全文 | 43aad40 2026-06-09 | 1656e02 2026-07-20 | 2026-07-20 | 模板（+07-20 §7 注） |
| `agents/dsp-algorithm/skill.md` | 1130 | 13 | 全文 | 43aad40 2026-06-09 | bdc9126 2026-07-20 | 2026-07-20 | 指针（07-20） |
| `agents/dsp-algorithm/soul.md` | 7711 | 190 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/hardware-design/memory.md` | 16985 | 475 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/hardware-design/profile.md` | 6815 | 152 | 全文 | 43aad40 2026-06-09 | 1656e02 2026-07-20 | 2026-07-20 | 模板（+07-20 §7 注） |
| `agents/hardware-design/skill.md` | 20654 | 678 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/hardware-design/soul.md` | 7711 | 197 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/literature-patent/memory.md` | 22700 | 666 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/literature-patent/profile.md` | 7161 | 142 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/literature-patent/skill.md` | 27841 | 969 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/literature-patent/soul.md` | 8601 | 197 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/project-document/memory.md` | 19801 | 692 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/project-document/profile.md` | 7028 | 147 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/project-document/skill.md` | 27505 | 924 | 全文 | 43aad40 2026-06-09 | ade79e1 2026-07-20 | 2026-07-20 | 混合：§0 L29-55 真(07-20)；其余模板 |
| `agents/project-document/soul.md` | 7333 | 194 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/project-manager/memory.md` | 22411 | 624 | 全文 | 218ead7 2026-06-06 | 218ead7 2026-06-06 | 2026-06-06 | 混合：L38-587 模板；L591-624 真 |
| `agents/project-manager/profile.md` | 6817 | 188 | 全文 | 43aad40 2026-06-09 | 1656e02 2026-07-20 | 2026-07-20 | 模板（+07-20 §6 注） |
| `agents/project-manager/skill.md` | 28093 | 898 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/project-manager/soul.md` | 7886 | 254 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/structure/memory.md` | 16457 | 540 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/structure/profile.md` | 6188 | 136 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/structure/skill.md` | 1093 | 13 | 全文 | 43aad40 2026-06-09 | bdc9126 2026-07-20 | 2026-07-20 | 指针（07-20） |
| `agents/structure/soul.md` | 6881 | 157 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/testing/memory.md` | 14761 | 579 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板（含假实验室设备） |
| `agents/testing/profile.md` | 6992 | 142 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |
| `agents/testing/skill.md` | 1106 | 13 | 全文 | 43aad40 2026-06-09 | bdc9126 2026-07-20 | 2026-07-20 | 指针（07-20） |
| `agents/testing/soul.md` | 7657 | 193 | 全文 | 43aad40 2026-06-09 | 43aad40 2026-06-09 | 2026-05-24 | 模板 |

> 「性质」列含义：**真**=项目真实内容；**模板**=Kimi 通用模板（2023–24 假数据）；**混合**=给出真/模板行段；**指针**=只含指向权威源的几行。真/模板行号细表见 §3.0。
> mtime 注：`agents/critic/profile.md`、`agents/critic/soul.md` 的 mtime=2026-07-22 10:41:36（与 structure skill 重写同一秒）；〔推断〕是 SLIM-07 同批 `git checkout` 复原「critic 装饰试点」所致（`decisions_log.md:1029`）。内容与 git 一致（开工时 `git status` 干净）。

### 0.3 表 B：记忆目录文件（`M` 下，全文已读）
| 路径（相对 M） | bytes | 行 | 读 | birth | mtime | originSessionId | fm.modified(UTC) |
|---|---|---|---|---|---|---|---|
| `memory/MEMORY.md` | 8284 | 26 | 全文 | 2026-10-02 01:55:05 | 2026-10-02 01:55:05 | - | - |
| `memory/agent-team-ops-lessons.md` | 1965 | 17 | 全文 | 2026-06-04 10:23:48 | 2026-06-04 10:23:48 | d706e3ea | - |
| `memory/board-identity-fsru1-rescope.md` | 2324 | 25 | 全文 | 2026-06-11 17:17:46 | 2026-06-11 17:17:46 | d706e3ea | - |
| `memory/directivity-band-requirement.md` | 1073 | 14 | 全文 | 2026-05-26 13:04:33 | 2026-05-26 13:04:33 | cbe3df46 | - |
| `memory/dsp-chip-decision.md` | 916 | 17 | 全文 | 2026-05-26 15:01:10 | 2026-05-26 15:01:10 | cbe3df46 | - |
| `memory/fib-cbt-literature.md` | 3893 | 24 | 全文 | 2026-09-26 16:36:05 | 2026-09-28 01:33:54 | d706e3ea | 2026-09-26T08:36:05.865Z |
| `memory/gate1-baseline-array-validation.md` | 1735 | 19 | 全文 | 2026-05-26 13:14:29 | 2026-05-26 13:14:29 | cbe3df46 | - |
| `memory/h1-line-state.md` | 4094 | 23 | 全文 | 2026-06-06 16:53:23 | 2026-06-06 16:53:23 | d706e3ea | - |
| `memory/m2-board-pass-stage4.md` | 2417 | 24 | 全文 | 2026-06-16 17:53:12 | 2026-06-16 17:53:12 | d706e3ea | - |
| `memory/preflight-audit-before-nonexpert-handoff.md` | 2511 | 24 | 全文 | 2026-06-10 22:13:58 | 2026-06-10 22:13:58 | d706e3ea | - |
| `memory/r14-closed-fira-ruling.md` | 1893 | 22 | 全文 | 2026-06-04 18:19:04 | 2026-06-04 18:19:04 | d706e3ea | - |
| `memory/self-critique-before-conclusions.md` | 1962 | 23 | 全文 | 2026-07-02 00:02:53 | 2026-07-02 00:02:53 | d706e3ea | - |
| `memory/side-rejection-30db.md` | 10116 | 58 | 全文 | 2026-10-02 01:55:03 | 2026-10-02 01:55:03 | 7580d6ba | 2026-10-01T17:55:03.010Z |
| `memory/sprint2-algorithm-baseline.md` | 5126 | 30 | 全文 | 2026-05-26 18:10:32 | 2026-05-26 18:10:32 | dc2c2904 | - |
| `memory/sprint3-d55-baseline.md` | 5101 | 36 | 全文 | 2026-05-29 14:43:10 | 2026-05-29 14:43:10 | 869ba718 | - |
| `memory/steering-v1-focusing.md` | 2318 | 21 | 全文 | 2026-06-05 10:36:09 | 2026-06-05 10:36:09 | d706e3ea | - |
| `memory/test1-method-fix-test3-next.md` | 3524 | 28 | 全文 | 2026-06-30 07:31:41 | 2026-06-30 07:31:41 | de198ad9 | - |
| `memory/test3-diagnosis-state.md` | 15621 | 39 | 全文 | 2026-07-09 16:19:44 | 2026-07-09 16:19:44 | d706e3ea | - |
| `memory/tree-filterbank-real-subbands.md` | 2027 | 17 | 全文 | 2026-09-26 17:50:50 | 2026-09-26 17:50:59 | 7580d6ba | 2026-09-26T08:35:51.622Z |
| `memory/verify-teammate-numbers-before-acting.md` | 2028 | 14 | 全文 | 2026-05-28 15:25:53 | 2026-05-28 15:25:53 | 86af57a0 | - |
| `memory/workflow-three-gate-rule.md` | 1978 | 24 | 全文 | 2026-06-04 20:03:18 | 2026-06-04 20:03:18 | d706e3ea | - |
| `memory/working-style-lessons.md` | 5784 | 43 | 全文 | 2026-10-02 00:14:56 | 2026-10-02 00:14:56 | d706e3ea | 2026-10-01T16:14:56.619Z |

- `originSessionId` 共 7 个：`cbe3df46`（05-26 首会话）、`dc2c2904`（05-26 傍晚）、`86af57a0`（05-28）、`869ba718`（05-29）、`d706e3ea`（06-04→10-01，最长，也被 `R/.claude/settings.local.json:17-18` 的路径引用，属 R34 那轮 06-06）、`de198ad9`（06-29）、`7580d6ba`（09-26→10-02）。〔推断〕项目由 ≥7 个 Claude Code 会话接力，靠记忆文件传状态。
- `modified:` frontmatter 只出现在 4 个文件（fib-cbt / side-rejection / tree-filterbank / working-style），时间为 UTC（+8h 才是本地）。其中 `fib-cbt-literature.md`（fm=09-26T08:36Z=本地 16:36，但 mtime=09-28 01:33）与 `tree-filterbank-real-subbands.md`（fm=本地 16:35，mtime=17:50）的 fm 落后于 mtime，**以 `stat` mtime 为准**。
- `MEMORY.md` 索引 26 行：21 个带链接的条目 + 2 个**无独立文件**的内嵌条目（`MEMORY.md:25` 阶段4 M1 透传 06-08；`MEMORY.md:26` 三线 WO-S5 06-05）。

### 0.4 表 C：范围外的补充材料（仅为定年/佐证，**不是**全文读）
| 材料 | 读法 | 用途 |
|---|---|---|
| `/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/plan.md`（1694 B） | 全文 | Kimi 生成这套多 Agent 包的 6 阶段计划（`plan.md:1-50`） |
| `…/itc-enterprise-workflow.skill`（zip，287309 B） | 仅 `unzip -l` | 59 个条目时间戳 2026-05-24 12:25–12:46，证明原包生成时间 |
| `R/tools/`（5 个工具层 agent×4 件=20 文件）、`R/references/`（2 文件） | 仅列名+mtime | 均为 Kimi 原包遗留，mtime 2026-05-24，2026-06-09 才入 git（43aad40）；**未读内容** |
| `/home/it1234/algorithm_speaker/ee-agent-team-starter/README.md` | 全文（41 行） | 2026-07 从本项目提炼的「EE agent team 启动包」，`README.md:41` |
| `R/sprint2/docs/POLICY-PROV-001_数字来源分级制度.md`（35784 B） | 读 L1-30 + 章节目录 + 版本行 grep | 核对 POLICY 各版本日期 |
| `R/sprint2/docs/decisions_log.md`（225187 B） | 仅 grep/节选（L1-30、63-75、310-322、495-520、698-737、783-798、814-857、933、1011-1030、1089-1091…） | 交叉核 memory 里的 DEC 日期/内容 |
| `/home/it1234/algorithm_speaker/knowledge_base/`（仓库外 KB） | `ls` + `README_论文索引.md` L1-40 + `competitor_anechoic.md` | §4 资料入库线索 |
| `R/knowledge_base/`（仓库内 KB） | `ls`/mtime 汇总 | §4 资料入库线索 |
| git log / reflog / `git merge-base` | 只读命令 | 核对 memory 里 commit 哈希与 push 状态 |

---

## 1. 团队与治理搭建

### 1.0 结论（5 条）
1. **来源**：整套 PM/声学/DSP/硬件/结构/测试/专利/文档/critic 九角色 + 工具层，是 **2026-05-24 12:25–12:46 一次性生成的 Kimi 包**（`itc-enterprise-workflow.skill`，59 个文件），2026-05-26 11:33 落到本机工作区；两天内（05-26）就被 Claude Code 实际启用（Sprint 2 六 agent 团队）。
2. **真正长出来的部分**：critic 的 POLICY/门禁（v1.1→v1.8，2026-05-28→06-04）、`.claude/team_config.md`（2026-06-03 起）、`CLAUDE.md` 红线、独立 critic 的 commit 纪律与三道关（06-04）、CTO-gate hook（06-10）、4 个 slash-invocable skill（`.claude/skills/*`，06-04 起）。
3. **2026-07-19→07-22「治理减法」SLIM-01~07**：去重（skill 副本→指针）、删伪造指标层、skill 项目化（dsp/testing/structure/project-document）。之后 `agents/{critic,dsp-algorithm,testing,structure}/skill.md` 只是指针，权威源在 `.claude/skills/<role>/SKILL.md`。
4. **团队机制**：「团队」= 具名 agent + `SendMessage` 续上下文，不是 TeamCreate 正式 team（commit 47356dd 说明，`R/.claude/team_config.md:7` 有 Agent Teams 实验开关）。
5. 九个角色里**在 persona 层留下真料的只有** PM、critic、dsp-algorithm、acoustic-simulation（`memory.md` 真段，见 §3.0）；testing 是 S7 才 spawn（`team_config.md:35`），其 skill 真料取自整机验证 `EXP_*` 文档（`.claude/skills/testing/SKILL.md:17`）；hardware / literature-patent 只见 Sprint 2/3 的产出痕迹（`M/sprint2-algorithm-baseline.md:10,18,20`），自己的 `memory.md` 无真料；project-document 是 decisions_log 的署名作者（`decisions_log.md:6`）、skill 只有 §0 是真的；structure 休眠（`.claude/skills/structure/SKILL.md:19`）。

### 1.1 成型前后（2026-05-24 → 06-03，**无 git**，靠文件时间/文字）
| 日期 | 事件 | 出处 |
|---|---|---|
| 2026-05-24 12:25–12:46 | Kimi 生成「ITC 企业级多Agent协作系统」：计划分 6 阶段（Skill 标准→架构设计→入口 skill+PM+critic→7 个领域 agent→5 个工具层 agent→打包 .skill）；依据「用户提供的工作流架构图」 | `plan.md:3-12,14-50`；`unzip -l` 59 条目均 2026-05-24；`R/agents/*/soul.md` 等 mtime 2026-05-24 12:26–12:44 |
| 同上（文本佐证） | 文件里自称「Kimi/Hermes Agent Skill 标准」「认证级别 L3（专家级）」；`SKILL.md` author=「ITC Architecture Team」 | `R/agents/literature-patent/skill.md:5,23-24`；`R/agents/project-document/skill.md:24`；`R/.claude/skills/structure/SKILL.md:13-14`（旧 frontmatter 存史注释）；`R/SKILL.md:9-13` |
| 2026-05-26 11:33 | 包落到本机工作区（`R/agents/*` 的 birth=2026-05-26 11:33:42；父目录 `Kimi_Agent_多Agent协作方案/` mtime 同）〔推断：拷贝/解压时刻〕 | `stat` |
| 2026-05-26 13:04 | 第一条记忆文件诞生（CTO 决定 ≥1 kHz 定向）；同日 Sprint 2 完成、Gate 1 PASSED / Gate 2 CLOSED（Sprint 1 本身无日期记载） | `M/directivity-band-requirement.md:10`；`M/sprint2-algorithm-baseline.md:10,22` |
| 2026-05-26 | Sprint 2 = **6 agent 团队（PM+声学+DSP+专利+硬件+critic）**，全部产出过 critic 两轮（首轮声学/DSP 各 2 BLOCKER 被打回）；`decisions_log.md` 作者栏=「项目文档专家 Agent」 | `M/sprint2-algorithm-baseline.md:10`；`R/sprint2/docs/decisions_log.md:6` |
| 2026-05-27 | `SKILL.md` v1.0.1「文档对齐磁盘实际：领域 Agent 目录改名、补登 literature-patent 与 project-document、Domain Agents 5→7」；v1.0.0 行的 `2024-01-15` 是 Kimi 模板日期 | `R/SKILL.md:493-498` |
| 2026-05-28 11:30–11:33 | `agents/acoustic-simulation/skill.md` 先备份（=原包 19227 B，与 zip 内同大小）再追加 §N「MATLAB 仿真执行能力」（MATLAB R2026a + MathWorks MATLAB MCP Core Server，工作目录 `~/matlab-agent/`） | `R/agents/acoustic-simulation/skill.md.backup_20260528_113013`（19227 B）；`R/agents/acoustic-simulation/skill.md:630-656`；mtime 11:32:55 |
| 2026-05-26 18:47 / 05-29 18:21 | 真实项目记忆写入人设文件：PM `memory.md §7`（文件 birth 05-26 18:47）、acoustic `memory.md §7`（文件 birth=mtime 05-29 18:21，文内写明 PF-8 重审 05-29）〔推断：birth 近似「整文件重写时刻」，PM 文件 06-06 又在原 inode 上追加过〕 | `R/agents/project-manager/memory.md:591-609`；`R/agents/acoustic-simulation/memory.md:466-499`；`stat` birth |

### 1.2 团队名册 / 模型分档（`R/.claude/team_config.md`）
| 日期 | 事件 | 出处 |
|---|---|---|
| 2026-06-03 23:30 | 首次入 git（53bd875「团队花名册锁档」）：lead/critic/dsp = claude-opus-4-8，其余 sonnet-4-6；**peer-challenge 协议 ON**（teammate 可直接 SendMessage，critic 可不经 lead 直接反驳 dsp；lead 只仲裁 BLOCKER 死锁/CTO 门） | `team_config.md:39-43`；git 53bd875 |
| 2026-06-03 | dsp 由 sonnet-4-6（实例 a9ba…，06-03 退役）→ opus-4-8，CTO Step-2 确认 | `team_config.md:28,85` |
| 2026-06-10 22:39 | **Fable 5 re-tier**（47356dd）：lead → `claude-fable-5[1m]`；critic/dsp 自 NEXT SPAWN 起 `claude-fable-5`，既有 Opus 实例（ac22…/a3f8…/a9e2…）可续用；默认省略 `model` 继承会话；Fable 免费窗口至 06-22 后 CTO 复议；decisions_log 同步记录 | `team_config.md:9-21,26-28`；`decisions_log.md:1011`（✓核，DEC 文字同） |
| 2026-07-20（实际）| critic verdict 仍带 `claude-opus-4-8` 标签（SLIM-01~07 全部如此），roster 表里的 fable-5 是 06-10 的「历史分档」 | `decisions_log.md:1021-1029`；`team_config.md:35` 自述「07-20 actual claude-opus-4-8, per reviewer tags」 |
| 2026-09-02 | Sprint 7：会话模型 `claude-fable-5-1`；新 spawn（critic/dsp/acoustic/testing）省略 model 继承；roster 表加「current session」行并保留 06-10 旧行 | `team_config.md:35,79`；git b6bc5fe |
| 机制 | 具名 agent + SendMessage 续上下文；**非** TeamCreate 正式 team；`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 开关在；Claude Code CLI 2.1.161 | git 47356dd 提交说明；`team_config.md:7` |
| 角色真实使用度 | PM/lead（全程）、critic（R 编号轮次 R1…R60+，`M/m2-board-pass-stage4.md:18` 提 R60；`agents/critic/memory.md:788` 提 R3e/R3g）、dsp（F4/F5/F7/H1/H2/M1/M2，实例 a9e2…）、acoustic（Sprint 2–3、S7）、testing（06-03 标「not yet started」，S7 才 spawn）、hardware/literature-patent「on demand」、structure 休眠 | `team_config.md:26-35`；`.claude/skills/structure/SKILL.md:19` |

### 1.3 POLICY-PROV-001 版本（文件 `R/sprint2/docs/POLICY-PROV-001_数字来源分级制度.md`）
> **git 只在 2026-06-04 才首次跟踪它和 CLAUDE.md**（89bed86 提交说明承认：「自仓库建立即 untracked，历次 v1.2–v1.8 修订仅存磁盘」）。所以 v1.1–v1.7 的日期只能取自政策文件自述 + critic skill 页脚 + critic LESSON 日期。

| 版本 | 日期 | 内容 | 出处 |
|---|---|---|---|
| v1.1 | 2026-05-28 | L1–L4 来源分级 + C1–C5（缘起 PF-1：纸面算力 27×/49× 锁芯片） | POLICY 头 `:6`（「v1.1 = 2026-05-28」）；`.claude/skills/critic/SKILL.md:1144`；`R/agents/critic/memory.md:506-523`（LESSON-007） |
| v1.2 | 2026-05-29 | 增 **L0 目测** + **铁律四**（L1 与 LOCKED 冲突强制重审）+ **C6 几何门**（缘起 PF-8 d=30 目测被锁） | POLICY `:4-6`；`critic/SKILL.md:1047`；`agents/critic/memory.md:540-555`（LESSON-009） |
| v1.3 | 2026-05-29 | **铁律五**（撤回全库传播三步）+ **C7**（缘起 PF-9） | POLICY `:6`；`critic/SKILL.md:1145`；`agents/critic/memory.md:556-571` |
| v1.4 | （无独立日期，并入 v1.5） | 双轨/三轨独立工具复核（缘起 LESSON-012：M1 WNG 草稿 bug 多除 \|a\|²=N→12.04 dB） | POLICY `:4`；`agents/critic/memory.md:592-621` |
| v1.5 | 2026-05-30（CTO 已审批） | **铁律六**（外部输入 24h 入库）+ **铁律七**（关键数字双轨核）+ **C8** + C5 扩 + CTO 外部接收声明义务（缘起 LESSON-013：docx 05-28 入手 05-30 才入库） | POLICY `:4-6`；`critic/SKILL.md:1146`；`agents/critic/memory.md:623-647` |
| v1.6 | 2026-06-02（CTO 拍板） | **铁律八 + C9**：R14 关闭前 FIRA 收益 `[L4/待验证]` 不进选型（缘起 R14） | POLICY `:106,284`；`critic/SKILL.md:1147`；`agents/critic/memory.md:649-669`（LESSON-014） |
| v1.7 | 2026-06-02（CTO 拍板） | **铁律九 + C10**：硬件不可逆动作须先有 CTO 出稿清单 + 物理版本确认 + 安全规矩（缘起 EZKIT 上板三陷阱） | POLICY `:108,285`；`critic/SKILL.md:1148` |
| v1.8（POLICY） | 2026-06-04（CTO 拍板） | **§4B 三道关**：workflow 产出（含修正稿）须 自动 verify→独立 critic→CTO 常识审 | POLICY `:4,114,286`；`CLAUDE.md:49,126`；`decisions_log.md:710,852` |
| v1.8（**critic skill 页脚**，另一含义） | 2026-06-03 | **§12 DSP/FIRA 验证专项门** FG1/FG2/IO1/IO2/ST1（+LESSON-015）；**POLICY 文件里没有 §12/FG1**（grep 0 命中） | `critic/SKILL.md:1126-1139,1149`；`agents/critic/memory.md:671-691` |
| 状态翻转 | 2026-06-04 | R14 CLOSED、C9/铁律八 RELEASED（附诚实分母：连体 §8 未计入清单 43–379 MCPS + 官方 3.07×，3.13× 混 build 禁入）；2026-07-20 SLIM-03 把「状态旗」补进规则本 | `CLAUDE.md:47`；`critic/SKILL.md:1083-1086,1120`；`decisions_log.md:1023` |

### 1.4 流程纪律（团队法）
| 日期 | 规则 | 出处 |
|---|---|---|
| 2026-06-03 | peer-challenge 协议 ON | `team_config.md:39-43` |
| 2026-06-04 10:23 | **Step-3 审计**：每份 critic verdict 头必带 `reviewer: critic @ <精确 model ID> / <日期>`；F4 线 6 份 verdict 追认 =`claude-opus-4-8`；改档须「改表 + decisions_log 一行」 | `team_config.md:77-85`；`critic/SKILL.md:1113`；git 46a9899 |
| 2026-06-04 11:54 | **Commit discipline**：独立 critic verdict 之前不得 commit；自审不算门；缘起 F5-A 偏差 | `team_config.md:45-50`；git 1ce0819 |
| 2026-06-04 12:26 | **Fallback 条款**：critic 实例续不上时，teammate 不得用「在自己上下文调 critic skill」充当门——停在未 commit、回报 lead 由其 spawn 全新 critic（缘起 F7 偏差 #2，e338288） | `team_config.md:50`；git 81c4e27 |
| 2026-06-04 21:56 | **三道关**入 POLICY v1.8 §4B / CLAUDE.md 护栏 7 / team_config 团队法（缘起 R8 synthesizer 撤销自家 verifier 的纠正 + R9 修正稿自带两处偏乐观新错） | `team_config.md:52-58`；`CLAUDE.md:49,126`；git 8e49cb2；`M/workflow-three-gate-rule.md:10-22`（✓核 DEC-S5-POLICY-3GATE-01 `decisions_log.md:710`） |
| 2026-06-05 13:17/13:32 | **harness/probe 设计纪律**（自检 probe 与测量 span 不得共享可变态；省内存须落字；stateful-chain 派单强制 cross-item 枚举 ST1-E）+ **TARGET 守卫代码必跑 guard-stub 检查并证伪**（缘起 R14/R15 H1、R15→R16 CCES build 才暴露） | `team_config.md:60-75`；git 11a701d、ffb8bf2；`critic/SKILL.md:1137`（ST1-E） |
| 2026-06-06 19:48 | `STAGE4_BRINGUP_CHECKLIST`（R24–R34 教训 32 条）+ 分角色速记节写入 `agents/{dsp-algorithm,critic,project-manager}/memory.md` | git 218ead7；`agents/critic/memory.md:775-786`；`agents/dsp-algorithm/memory.md:629-640`；`agents/project-manager/memory.md:616-624` |
| CLAUDE.md 护栏（首版即有） | 每 teammate 预算 $3、总 $10、单任务 ≤15 分钟、禁 sub-sub-agent 递归、文件写操作先出「操作建议」等人类确认、BLOCKER 立即停并上报；CTO 介入点：Gate 1（首次阵列方案审定）/Gate 2（ADI 芯片型号最终确认）/BLOCKER>4h/预算超 $10 | `CLAUDE.md:107-127`（首版 89bed86 已含） |

### 1.5 Hooks（`.claude/` 里**只有 1 个 hook**）
- 配置：`R/.claude/settings.json:3-15`——`PreToolUse` / matcher `Bash` → `${CLAUDE_PROJECT_DIR}/.claude/hooks/cto-gate-softconfig.sh`（timeout 10）。
- 行为：只拦截含 `git commit` 的 Bash 命令；若暂存区含 `m1_softconfig`（codec 使能/softcfg 命脉文件，两处：`sprint6/dsp/audio/m1_cces_project/src/m1_softconfig.c`、`…/m1_project/src/m1_softconfig.c`）且环境变量 `CTO_OK` 为空→`exit 2` 阻断；`export CTO_OK=1` 一行放行（`cto-gate-softconfig.sh:35-65`）。缘起：CTO 06 月出门期间 codec 使能逻辑改动不得无签字落库（`:5-12`）。
- 日期：2026-06-10（b3ea58e 22:13；文件 mtime 20:18）；提交说明称端到端测 4/4 过、hook 在会话启动时加载。
- CTO_OK 的后续使用：`decisions_log.md:1042`（D3 CTO_OK=1）、`:1227`（S-FIRB CTO_OK 2026-09-29）、`:1086/:1096`。
- 本机 `R/.claude/settings.local.json`（**untracked**，mtime 06-06 19:39）：只是权限白名单（python3/pip/matlab MCP/读 KB/`/tmp`），含 R34 轮的一条会话专用 `cp`（`:17-18`），无 hook。
- 其他 `.claude/` 内容：没有 plugins / 其他 hooks（`find .claude -type f` 共 8 文件）。

### 1.6 Skills（`.claude/skills/*/SKILL.md`，Claude Code 可 slash 调用）
| 日期 | 事件 | 出处 |
|---|---|---|
| 2026-06-04 10:23 | 4 个 skill（critic / dsp-algorithm / structure / testing）首次入 git（46a9899「critic skill 重搬 .claude/skills」）；当时是 `agents/<role>/skill.md` 的逐字副本 | git 46a9899；`M/agent-team-ops-lessons.md:13`（memory 称「verbatim cat-moves」） |
| 2026-06-05 | critic §12 增 ST1-E（11a701d）。2026-07-19 SLIM-01 查出该条被误塞进 YAML frontmatter（非法）→归位 §12 | git 11a701d；`decisions_log.md:1021`；`critic/SKILL.md:1137` |
| 2026-07-19 | SLIM-01：`agents/critic/skill.md` 1124 行→指针（现 51 行），权威源改为 `.claude/skills/critic/SKILL.md` | `agents/critic/skill.md:15-19`；`decisions_log.md:1021` |
| 2026-07-20 | SLIM-04：dsp/testing/structure 三份 agents 副本（660/1132/871 行，diff 实证「独有内容行=0」）→各 ~13 行指针；`CLAUDE.md:73` 加脚注 | `agents/dsp-algorithm/skill.md:5-13`；`decisions_log.md:1024`；git bdc9126 |
| 2026-07-20 | SLIM-05：dsp skill 678→115 行项目化（砍错平台 ADAU1467/MVDR/GSC/HRTF；加 A 项目真本事 43 处出处、B 通用骨架、C 缺口）；project-document skill 加 **§0 溯源纪律绑定**（L 标/DEC 六字段/铁律五/C7·C8/三道关） | `.claude/skills/dsp-algorithm/SKILL.md:22-115`；`agents/project-document/skill.md:29-55`；git ade79e1 |
| 2026-07-22（DEC 记 07-20） | SLIM-06：testing skill 1145→99 行（立体声 QA 模板+虚构实验室→单声道广侧柱真测法；A4 假绿纪律首次落地）；SLIM-07：structure skill 883→50（删假留骨，A 段诚实空置，域休眠） | `.claude/skills/testing/SKILL.md:17-18,64-71`；`.claude/skills/structure/SKILL.md:19-21`；git 29a8539 / c8eeb08；`decisions_log.md:1027,1029` |
| 2026-09-02 | testing skill `:58` 重复性地板改标 `[L4 工作假设，未落盘]`（DEC-S7-RULINGS-01 D13） | git c9c3f91；`testing/SKILL.md:58` |

### 1.7 治理减法 SLIM-01~07 一览
| DEC | DEC 日期 | git 提交（作者日期） | 做了什么 | 出处 |
|---|---|---|---|---|
| SLIM-01 | 07-19 | c3dcd50（07-19 02:08）✓一致 | critic skill 去重+修活 bug（CLAUDE.md「八铁律」→「九铁律」） | `decisions_log.md:1021` |
| SLIM-02 | 07-19 | ed83668（**07-20 10:40**）⚠DEC 写「已 commit ed83668 + push（2026-07-19）」与 git 差一天 | CLAUDE.md 294→128 行；新建 `PROJECT_REFERENCE.md`（按需加载）；规则 0 条删 | `decisions_log.md:1022`；`PROJECT_REFERENCE.md:1-6` |
| SLIM-03 | 07-20 | 1656e02（07-20 11:02） | 4 个并行 agent 审配置（bloat/depth/drift/metrics）→删 critic memory §3/§4 的 182 行伪造指标、`SKILL.md §10` 假仪表盘；5 个 profile KPI 降「设计意图·未跟踪」；R14/C9 状态旗；team_config:36 矛盾修 | `decisions_log.md:1023`；`agents/critic/memory.md:350-358`；`SKILL.md:477-489` |
| SLIM-04 | 07-20 | bdc9126（07-20 11:18） | 三个 skill 副本→指针，净 −2185 行 | `decisions_log.md:1024` |
| SLIM-05 | 07-20 | ade79e1（07-20 15:31） | project-document + dsp 两个「焊接样板」 | `decisions_log.md:1025` |
| SLIM-06 | 07-20 | 29a8539（**07-22 10:42**） | testing skill 项目化 | `decisions_log.md:1027` |
| SLIM-07 | 07-20 | c8eeb08（**07-22 10:42**） | structure 删假留骨；同批 revert 了 critic「装饰试点」 | `decisions_log.md:1029` |
- 07-17：`ee-agent-team-starter/` 从本项目提炼成「EE agent team 启动包」（框架+治理精华，**不带 memory**，防跨项目污染），`README.md:2-3,32-33,41`；目录 mtime 7 月 17 日。〔推断〕SLIM 系列是这次提炼之后的瘦身。

### 1.8 Sprint 7（2026-09-02 起）治理姿态
- `DEC-S7-SCOPE-01`：本轮升级=算法层；治理照旧（agent team、PM lead、独立 critic 前不得 commit、CTO_OK hook、三道关、预算护栏）——`decisions_log.md:1030`。
- critic memory 增 2 条新教训（09-28、09-29 提交）——见 §3。

---

## 2. 记忆文件时间线

> 列：事实日期 | memory 文件（`stat` mtime / 会话） | 事实（一句话） | 关联 DEC / commit | 校核
> 「✓核」= 已与 `decisions_log.md` / `git log` 对过。memory 仍是最低可信度来源。

| 事实日期 | memory 文件（mtime；会话） | 事实 | 关联 DEC / commit | 校核 |
|---|---|---|---|---|
| 2026-05-26 | `directivity-band-requirement.md:10`（05-26 13:04；cbe3df46） | CTO 决定：只要求 ≥1 kHz 起定向，500 Hz 不要求（理由用 L=0.45 m / 16 元） | — | 理由里的 0.45 m 属已撤销的 d=30 几何，正文未标（§6-D3） |
| 2026-05-26 | `gate1-baseline-array-validation.md:10-19`（05-26 13:14） | 16 元 / d=30 / L=0.45 基线过 Critic cycle-2 PASSED_WITH_MINOR 并交 CTO Gate 1；−20 dB Dolph；4 子带 FAS ≈80 MMAC/s；Gate-2 入口=CCES 实测 + SC589 vs 21569 | `R/deliverables/Gate1-baseline-array-validation-2026-05-26.md`（存在） | d=30 已被 PF-8 撤销；索引 `MEMORY.md:15` 有 ⚠，正文无 |
| 2026-05-26 | `dsp-chip-decision.md:10-17`（05-26 15:01） | 锁定 ADSP-21569（SHARC+ 单核 1 GHz；640 KB L1+1024 KB L2；400-ball 17×17）；无 ARM/网络/显示 | DEC-S1-004（`decisions_log.md:63-75`，「决策时间: Sprint 1」）✓核 | `:14` 「裕量 ~20–40×」、`:17`「Compute was never the constraint」已被后续 L1 推翻（`decisions_log.md:234`）；正文未标（§6-D3） |
| 2026-05-26 | `sprint2-algorithm-baseline.md:10-30`（05-26 18:10；dc2c2904） | Sprint 2 六 agent 完成；竞品反推 ≈20 元/35 mm；3 候选阵列；4 子带树形 FAS（裕量 27×，纸面）；锁定基线 N=16/d=30/Dolph-20，Gate1 PASSED/Gate2 CLOSED；DEC-S2-012 延迟<30 ms；DEC-S2-013 超指向；DEC-S2-014 分级采购；Sprint 3「硬件平台快速验证法」DEC-S3-001/002，第一动作拆机 WO-S3-001；法律红线 | `decisions_log.md:310`（DEC-S2-014 2026-05-26 ✓核）、`:322`（DEC-S3-001） | d=30 / 27× 均被后续取代；索引 `MEMORY.md:17` 有 d=30 ⚠，**无**算力 ⚠ |
| 2026-05-27→29 | `sprint3-d55-baseline.md:10-36`（05-29 14:43；869ba718） | 05-27 CTO 拍 Sprint 3 主路线「竞品硬件基线+自研主板+我方算法」；拆机真值 N=16/d=55/L=825、8 路 A/B 对称串联 broadside-only；05-28 P0 桌面仿真三项+DEC-S3-PROC-01 芯片不可逆采购冻结；05-29 PF-8→DEC-S3-GEOM-01 撤 d=30，POLICY v1.2 | `decisions_log.md:442`（DEC-S3-GEOM-01）、`:167`（DEC-S2-006 作废标记）、`:495-520`（PROC-01/P0-01，2026-05-28）均 ✓核 | `:15` 与索引 `MEMORY.md:18` 的「17×/33×」已被 06-03 板上 L1（8ch 裕量 1.32×，`decisions_log.md:234`）推翻 |
| 2026-05-28 | `verify-teammate-numbers-before-acting.md:10-14`（05-28 15:25；86af57a0） | AC-WP01 把 1 kHz BW 报成 14.63°（实为单边半角，全角 29.28°），差点让 CTO 撤销超指向；规则=转报前独立核验，「−6 dB 全角必>−3 dB 全角」 | critic LESSON-008（`agents/critic/memory.md:525-539`）；`R/sprint2/docs/AC-WP01_1kHz波束宽度决策追溯.md`（存在） | 与 critic memory 内容一致 |
| 2026-06-03→04 | `agent-team-ops-lessons.md:10-17`（06-04 10:23；d706e3ea） | Agent Team 自 06-03 起跑；子 agent 长任务 ~7 min socket 死→每次只派一个紧问题、PM 从磁盘现场接手；独立 critic 在 F4 线拦下 6 个结构问题 | git 53bd875（06-03）、46a9899（06-04） | `:13` 的「lead/critic/dsp=opus-4-8」「skills 是 agents 的 verbatim cat-moves、编辑后需 re-cat」**已过时/有危险**（§6-D6） |
| 2026-06-04 | `r14-closed-fira-ruling.md:10-20`（06-04 18:19） | CTO 三连裁定：R14 CLOSED；≥10× 判据退役改「实时+余量」；C9 松绑附诚实分母；官方 3.07× / 2.878× [L1] | DEC-S4-R14-RULING-01（`decisions_log.md:783`）、-C9-RELEASE-01（`:798`）✓核；-CRITERION-01（`:718` 是 06-05 的 FINAL 版 ≥1.5×(T2)，memory 记的是 06-04 的临时 ≥1.0×/正式阈值 PENDING 阶段）✓核 | `:22` 有悬空链接 `[[steering-line-constraints]]`（无此文件） |
| 2026-06-04 | `workflow-three-gate-rule.md:10-22`（06-04 20:03） | CTO 铁规：三道关；缘起 R8/R9 | DEC-S5-POLICY-3GATE-01（`decisions_log.md:710,852`）、git 8e49cb2 ✓核 | — |
| 2026-06-04→05 | `steering-v1-focusing.md:10-17`（06-05 10:36） | v1=聚焦/分区（现板固件）；角度偏转=16ch 硬件叉+d 重议，单独立项；06-05 再收窄为「近场高频展区分区」；EQ 取 O1 | DEC-S5-STEER-V1-01（`decisions_log.md:708,814`，06-04 ✓核）、DEC-S5-OPT-ORDER-01（`:709`，06-04 ✓核）、DEC-S5-V1-SCOPE-01（`:857`，DEC 存在且内容吻合 ✓；块首无日期，06-05 取自 memory 未核） | — |
| 2026-06-05 | `MEMORY.md:26`（无独立文件） | 三线 WO-S5：①H2 及格线 210.19 ②SPL 内部口径 94.0 dB@1W[L2 待消声室]、对外冻结至 R3 L1 ③厂家函准发；⚠「PRD:183 对外承诺 ≥90 dB」与 94.0 仅 ~4 dB 模型余量 | commit b860a4d、6d0a0af（06-05 ✓核）；DEC-S5-SPL-CALIBER-01（`decisions_log.md:933`）✓核 | PRD 行号未核 |
| 2026-06-06 | `h1-line-state.md:10-12`（06-06 16:53） | 算力线 T2 保守闭合；DMA 腿 0.038 MCPS[L1]；ISR 腿隔离待 H2R；「保守≠clean」；**算力优化冻结令**；下一阶段 WO-S6-AUDIO | commit 603c326（06-06 ✓核）、DEC-S5-T2-CLOSURE-01（`decisions_log.md:724` ✓核） | — |
| 2026-06-08 | `MEMORY.md:25`（无独立文件） | 阶段 4 M1 透传 loopback；四开口 DEC-S6-M1-ARCH-01；走 B 路独立工程零扰动算力黄金环境；门禁板前抓 4 个静默无声坑 | DEC-S6-M1-ARCH-01（`decisions_log.md:727`，06-08 ✓核）；commits 0346442/dc87606/3bf91af/fb597f6/787a7a1（均 06-08 ✓核） | — |
| 2026-06-10 | `preflight-audit-before-nonexpert-handoff.md:10-24`（06-10 22:13） | 单 critic R50 过门却漏 4 BLOCKER+8 MAJOR（符号名、hwerr 序数非位掩码、探测写 0x00、「发给 PM」没人接）；交非专家/远程/不可逆前须多视角 fan-out 审计 | 提交 b3d7f74（06-09 U6 自探测包） | 未核 R50 细节 |
| 2026-06-11 | `board-identity-fsru1-rescope.md:10-26`（06-11 17:17） | 台架板=第三方 AD-EXKIT V2.1 + ADSP-21569-SOM REV1.1（非官方 EV-SOMCRR-EZKIT）；F-SRU-1 re-scope 关闭，「rc 全 0」判据退役；0x21=SOM 自带 U13 勿写 | DEC-S6-FSRU1-RESCOPE-01（`decisions_log.md:1012`，06-11 ✓核） | `dsp-chip-decision.md:13` 仍写「Dev board: EV-21569-EZKIT」（§6-D16） |
| 2026-06-16 | `m2-board-pass-stage4.md:10-24`（06-16 17:53） | M2 FIRA 波束上板 PASS（死锁/对齐/波束三清零，CTO 耳听正常）；beam_cyc 墙钟 62.3%=纯核预期 6.4×，三口径互不可比；阶段④软件实质收口，M3 卡阵列硬件（阶段⑤） | DEC-S6-M2-BOARD-PASS-01（`decisions_log.md:1014`）、DEC-S6-ALIGN-LEFT-01（`:1013`）均 06-16 ✓核 | — |
| 2026-06-29 | `test1-method-fix-test3-next.md:10-28`（06-30 07:31；de198ad9） | Test0 PASS；Test1 接线确认对（方法订正：近场相干干涉→改逐路 solo）；Test2 PASS；Test3「1m+纯单音+手持」退役，改远场+warble/粉噪+Leq | DEC-S6-TEST1-METHOD-01（`decisions_log.md:1016`）、-TEST3-METHOD-01（`:1018`）均 06-29 ✓核 | — |
| 2026-07-01 | `self-critique-before-conclusions.md:10-20`（07-02 00:02） | CTO 当面指出反复过度声明；两层规则：每结论内建 4 查 + 承重结论主动过独立 critic | — | — |
| 2026-07-01→09 | `test3-diagnosis-state.md`（07-09 16:19）`:10` 闭合；`:16` 07-01 交换实验；`:26` 07-01 JTAG dump；`:30` 07-02；`:32` 07-07；`:33` 07-07/08 | 波束「平」诊断链：07-01 交换实验（只换板）→JTAG dump 数字侧完美→07-02 `M2_STATIC_TXTEST`（4bf18b6）→07-07 静态差分锁死「数字缓冲之后」→07-07 375 Hz 逐对测（02bc474/5b98b18）→**07-08 根因=物理 C2/C4 两对喇叭接反极性**→07-09 选项 B 通道映射修（c9321bc/99143fd，`M2_CHMAP_FIX`）。**07-01「板 vs 板」差异至今未解释**（极性根因不外推） | DEC-S6-BEAM-POLARITY-CLOSURE-01（`decisions_log.md:1020`，07-08 ✓核）；commits 4bf18b6（07-02）、02bc474/5b98b18（07-07）、c9321bc/99143fd（07-09）均 ✓核且在 origin/master | 文件含「存史」旧结论（`:12` 分隔线之后），以 `:10` 为准 |
| 2026-07-09→09-28 | `fib-cbt-literature.md:11-24`（birth 09-26 16:36；mtime 09-28 01:33；fm.modified=09-26T08:36Z） | 07-09 CTO 追问 FIB；联网核实：FIB=频率不变波束（差分+Jacobi-Anger）；09-28 读 Keele 2002 原文+仿真：直阵延时 CBT 可行且兼容对称对，但 60° 外变宽、不适合 ±90° 抑制；Duran DDC 原样 4 kHz R90 仅 8.5 dB | `R/sprint7/docs/S7_SIDE30_ALT_ALGOS.md §4`（memory 自述） | 索引 `MEMORY.md:6` 仍写「直阵死路?⚠09-26 待核」，已被本文件 `:15-17` 更正（§6-D12） |
| 2026-09-26 | `tree-filterbank-real-subbands.md:11-17`（09-26 17:50；7580d6ba；fm=08:35Z） | 冻结子带树真实分界 3k/6k/12k（头文件注释 1.5k/3k/6k 错）；detail 带=未对齐梳状残差；每子带不同加权不可用；撤回已全库传播 | DEC-S7-RETRACT-SUBBAND-01（`decisions_log.md:1089`，09-26 ✓核）；commit 33b1966 ✓核 | — |
| 2026-09-26→10-02 | `side-rejection-30db.md`（10-02 01:55；7580d6ba；fm=10-01T17:55Z）`:11` 缘起；`:13-26` 提交链；`:47-56` 10-02 现状 | 侧面 ±90° 30 dB 目标：CTO 同意口径/重开 D6/改架构/改固件（DEC-S7-SIDE30-01）；RS-A/RS-B 稳健扇区表；hybrid LPX3-b；S-FIRB 获 CTO_OK（09-29）；远场信号包 s7ff_v1（10-02）；配对是最大杠杆；本地 master 领先 origin 9 提交 | DEC-S7-SIDE30-01（`decisions_log.md:1091`，09-26 ✓核）；commits 7686c05/04fd908/db301ef/42f38a0（09-26）、0ef46c4（09-27）、04e0e6a/7ad4df6/46574ed（09-28）、ce87ed1/cd113e2（09-29）、3a008e8/263e984（10-02）全 ✓核 | `git status -sb`=「领先 9」，且 0ef46c4…263e984 不在 origin/master，✓与 memory 一致（按本地跟踪引用） |
| 2026-10-01/02 | `working-style-lessons.md:11-41`（10-02 00:14；fm=10-01T16:14Z） | 协作复盘：核心病=过度声明且不自查；硬规则 R1–R9（校准标/强制 critic/假绿词/先找决定性实验/每轮自检/记忆防污染/先跑代码不信注释/汇报数字从过门文档逐字取/说「别人多久没做」前先查对方拿得到什么） | — | — |
| 2026-10-02 | `MEMORY.md:1-26`（10-02 01:55） | 索引本体（与会话启动快照略有差异：`:4` 多了 R9，`:12` 多了 s7ff_v1 摘要） | — | — |

---

## 3. agents/*/memory.md（及 skill）里的经验/教训时间线

### 3.0 先分真假（**引用前必看**）
| 文件 | 模板/假（勿引） | 真料（可引，仍需交叉核） |
|---|---|---|
| `agents/critic/memory.md` | L11-348（§1 架构、§2.1-2.3 占位评审记录 `total_reviews:156`、2024 假日期；`:42` 自己标了「占位」）、L360-406（§5 误判分析：REV-AC-004 等）、L408-450（通用标准库）、L457-490（**LESSON-001~005：2023-11~2024-01 假日期**）、L694-766（§6.3/§7 通用） | L350-358（2026-07-20 删假指标层说明）、**L492-691（LESSON-006~015，2026-05-27→06-03）**、L775-786（2026-06-06 R24–R34）、L788-793（2026-09-28 R3e/R3g） |
| `agents/project-manager/memory.md` | L11-587（假项目 ITC-Pro-2024-Q1/Q2、假团队指标、假风险库） | **L591-609（§7，实战记忆）**、L616-624（§7.5，2026-06-06） |
| `agents/dsp-algorithm/memory.md` | L10-296、L342-627（BF_DSB/MVDR/GSC 算法库、ADAU1467/HiFi4 平台、2024 听音测试、假项目 PRJ-2024-xxx、2024Q3 学习计划） | L298-305,314,327（**2026-06-02 SHARC 21569 单核更正**）、**L629-640（2026-06-06 阶段 4 bring-up 8 条）** |
| `agents/acoustic-simulation/memory.md` | L10-464（材料库、CASE-2024-xxx、FAIL-2023-xxx、假偏差统计） | **L466-499（§7 d=55 基线、§7.5 JY/T 表 9）** |
| `agents/{hardware-design,literature-patent,structure,testing,project-document}/memory.md` | **全文模板**（hardware 唯一提到 21569 的 `:48` 也是模板行；testing 的 APx515/B&K/ESPEC 带假序列号） | 无 |
| `agents/*/profile.md`、`soul.md` | 全文通用模板；5 个 profile 的「性能指标/Success Criteria」节 2026-07-20 已降级为「设计意图·未跟踪」 | 无 |
| `agents/acoustic-simulation/skill.md` | L1-628（=Kimi 原版） | L630-829（§N MATLAB，2026-05；含 d=55 栅瓣 `:700-702` 等） |
| `agents/project-document/skill.md` | L58-925（通用文档技能；其中 L789-796 把虚构 REST 服务改写成「repo markdown」） | **L29-55（§0 溯源纪律，2026-07-20）** |
| `agents/project-manager/skill.md`、`agents/{hardware-design,literature-patent}/skill.md` | 全文模板（任务 ID 样式 `TASK-{project}-{seq}` 等） | 无 |
| `agents/{critic,dsp-algorithm,testing,structure}/skill.md` | 指针 | 指向 `.claude/skills/<role>/SKILL.md`（真） |
| `.claude/skills/dsp-algorithm/SKILL.md`、`testing/SKILL.md` | B 段「通用骨架」自标非项目蒸馏 | **A 段（逐条带出处）**；C 段缺口 |
| `.claude/skills/structure/SKILL.md` | B/C | A 段**诚实空置**（域休眠，`:19,26`） |
| `.claude/skills/critic/SKILL.md` | L40-1038（§1-§10：Kimi 通用方法/错误模式库/各域清单，其中的 `frequency: 8` 等计数是模板） | **L1042-1139（§11 POLICY 门禁 C1–C10 + 铁律、§12 DSP/FIRA 门）** |

### 3.1 时间线（date | 文件:行 | 教训/事实 | 触发）
| 日期 | 文件:行 | 教训/事实 | 触发/关联 |
|---|---|---|---|
| 2026-05-26（birth 18:47） | PM `memory.md:591-609` | ①ADSP-21569 真实参数已核（单核 1 GHz；640 KB L1+1024 KB L2；400-ball CSP_BGA 17×17）；推荐采购型号 ADSP-21569KBCZ10（CTO 指定），**订货后缀发 PO 前须 web 核实**（Sprint 2 BOM 曾写 KBCZ-1A）`:596`；②早期把主频误标 500 MHz（实 1 GHz）→任何器件参数落档前必须核实 `:599`；③CTO 偏好：所有技术参数 web 核实、不确定标「待核实」、算力/预算受控 `:601-604`；④当前节点 Sprint 3 有条件 GO，首动作拆机 WO-S3-001 `:606-607` | Sprint 2 收口 |
| 2026-05-27 | critic `:492-504`（LESSON-006） | 竞品参数**反推**（Sprint 2 ≈20 元/35 mm，RMS 2.84 dB）多解欠定；Sprint 3 拆机实测 16 元/55 mm 才是真值——反推仅作对标，有实测必须修旧反推 | 拆机 |
| 2026-05-28 | critic `:506-523`（LESSON-007） | PF-1：算力裕量 27×/49× 是纸面 L3，却 LOCKED 芯片并触发不可逆采购；真实树形 C 17×/33× → POLICY-PROV-001、C1–C5 | DOC-AUDIT-SIM-001 |
| 2026-05-28 | critic `:525-539`（LESSON-008） | 半角/全角误读（14.63° vs 29.28°）；「−6 dB 全角必>−3 dB 全角」；会推翻决策的数字转报前必须独立复算 | AC-WP01 |
| 2026-05-29 | critic `:540-555`（LESSON-009） | PF-8：d=30 是目测 [L0] 却 LOCKED；与实测 d=55 冲突未重审，被「两条几何并存」掩盖近一个 Sprint → L0 / 铁律四 / C6；自省：制度缺位处 critic 应主动补门 | PF-8 → DEC-S3-GEOM-01 |
| 2026-05-29 | critic `:556-571`（LESSON-010） | PF-9：竞品 BW 14.9°/19.1°/16.0° 是 SPL 4 点插值反推（竞品只实测 SPL）；撤回只发生在源头，`full_teardown_v2.md` 等仍标「实测」→外部 AI 引为 L1 → 铁律五 / C7 | F-AC-01 |
| 2026-05-29 | critic `:572-591`（LESSON-011） | 正向案例：teammate 在派单阶段自行拦下 3 个 PF-9 诱惑点；反噬自身：「已完成」状态位也要全库传播 | C7 首次主动评审 |
| 2026-05-29 | critic `:592-621`（LESSON-012） | 三轨独立工具（numpy / MATLAB-agent / MATLAB-CTO）当场抓出 M1 WNG 草稿 bug（多除 \|a\|²=N，偏差 =10log10(16)=12.041 dB）→ 铁律七；critic 终审必须自己复算 1–2 个承重值；C7 第五次评审抓到 A2 的 PF-9 复发（撤回的竞品 19.1° 被称「实测」） | TASK-MATLAB-RV / STD-A-RV |
| 2026-05-29 | acoustic `:491-499`（§7.5） | JY/T 表 9 合规检查（TASK-STD-A）三轨一致到 0.001 dB：可评 8 点中 7 点一级，唯 2 kHz/90°=23.01 dB 仅二级；500 Hz/30°=5.857 dB 一级裕量 +0.857 dB（全表最薄）；180° 点因 isotropic 阵因子对称=artifact 禁报；平面口径假设=音柱须水平安装 | TASK-STD-A |
| 2026-05-27/29 | acoustic `:466-489`（§7.1-7.3） | d=55 基线：BW@1 kHz=29.3°、@2 kHz=14.5°（点声源阵因子）；栅瓣 d=λ→6236 Hz，6.24 kHz 起栅瓣与主瓣等高；强指向上限 8k→6k（对内）/5k（对外）；点声源模型 ≥2 kHz 置信度低；SPL 预测 ~117 dB 为理论上限低置信 | DEC-S3-GEOM-01 / DSP-05 |
| 2026-05-30 | critic `:623-647`（LESSON-013） | `定向音柱AI数据.docx` 硬件团队 05-28 发 CTO、05-30 才入库（>24h），期间 Sprint 3 产出全未用上（R3 SPL 仍占位）→ 铁律六 / C8（入站，对偶铁律五出站）；CTO 外部接收声明义务 | v1.5 |
| 2026-06-02 | critic `:649-669`（LESSON-014） | FIRA 评估的两个 HIGH 风险（定点 bit-exact / Split-Task）只活在一份文档→强制登记 R14、Sprint 4 输入清单、C9；措辞红线正反示例（纯核裕量可引 / FIRA 收益须标 [L4/待验证]） | v1.6 |
| 2026-06-02 | DSP `:300-305,314,327` | 21569 是**单核**（旧 yaml 写 dual 是错，datasheet `ds.txt:153` 坐实）；浮点原生，**定点是项目路线选择非硬件强制**（DEC-S3-PROC-01，FIRA 定点浮点双模）；17×/33× 是单核定点纯软件口径，不含 FIRA | 铁律四重审闭环 |
| 2026-06-03 | critic `:671-691`（LESSON-015） | R14 端到端假绿（占位 FIRA 仍 PASS，`out==in` telescoping 恒等）+ FIRA D1/D2 I/O 契约垃圾，**两次都由 CTO 兜住而非 critic**→ §12 FG1/FG2/IO1/IO2/ST1 | v1.8(critic skill) |
| 2026-06-06 | critic `:775-786` | R24–R34：同源自证盲区（guard-stub 与实现同一份情报）；FG 须含「率在带」（存在性≠正确性，62× 率错照绿）；点估须带误差带；聚合数先拆解再 relabel；「保守闭合≠clean 闭合」；harness build≠产品 build；审查型角色三态判定 | STAGE4 bring-up |
| 2026-06-06 | DSP `:629-640` | 先查后写（MDMA 9-error）；header 后缀非对称；缓冲放置=效度命门（.map 双重裁定，`pragma seg_l1_block1`）；FG 存在性≠正确性；软件重武装≠硬件周期；聚合数先拆解（20.59 MCPS=99.8% ISR+0.2% DMA）；64 vs 120 双口径；harness≠产品 build | R24–R34 |
| 2026-06-06 | PM `:616-624` | 排队消息会被合并吞（逐单核收 verdict）；流超时先查磁盘现场；机械落位 assert 守卫；长调研勿强制结构化输出；范围变更竞态（改令晚于 agent 已动工） | R29/R30、M1 draft |
| 2026-09-28 | critic `:788-793` | 管道吞退出码的假绿（`cmd \| grep -v … \|\| rc=1` 永不 FAIL，R3a 漏审）→用 `${PIPESTATUS[0]}`/pipefail+内置反证输入；机制性结论要问「还有谁同样适用」（R3g F1：限幅器联动结论没用到对照组 FIR） | S7 R3e/R3g |
| （skill 层）2026-07-20/22 | `.claude/skills/dsp-algorithm/SKILL.md:51-60`（A3 坑+触发器库）；`.claude/skills/testing/SKILL.md:42-52`（A2 坑+触发器库） | 把上面 memory/handoff 的事故蒸馏成「症状→先查这里」表，逐条带出处 | SLIM-05/06 |

---

## 4. 前期环节线索（"有记录+出处" / "未见"）

| 环节 | 结论 | 出处与说明 |
|---|---|---|
| **需求指标 / PRD** | **有记录（零散）；原始 PRD 全文未见** | ①应用场景：博物馆讲解/车站广播/商场分区广播 `CLAUDE.md:7`。②Sprint 1 规格：−6 dB 波束宽度 ≤30° @2 kHz、工作带 500 Hz–8 kHz（`PROJECT_REFERENCE.md:31-34`；`M/gate1-baseline-array-validation.md:13`）。③2026-05-26 CTO：仅 ≥1 kHz 要求定向 `M/directivity-band-requirement.md:10`。④延迟规格 <5 ms→<30 ms（DEC-S2-012，`M/sprint2-algorithm-baseline.md:24`）。⑤强指向规格上限 8k→6k/5k `M/sprint3-d55-baseline.md:32`。⑥SPL：对外承诺 ≥90 dB（`MEMORY.md:26` 写 `PRD:183`）；94.0 dB@1W 内部口径 [L2]。⑦PRD 更新稿存在：`R/sprint2/docs/prd_update.md`（git 首入库 06-05，4d7e528）、`R/sprint3/pf8/p1b_prd_alignment.md`、`R/sprint5/eq_prd/EQ_PRD_DECISION_MATERIAL.md`；PRD v2.5（`M/side-rejection-30db.md:14`，commit 33b1966 09-26）；DEC-S5-V1-SCOPE-01「PRD 重写」`decisions_log.md:857`。**未见**：`SKILL.md:299-301` 约定的 `prd_document.md`/`constraints.yaml`/`milestones.json`/`project_plan.yaml`（全盘 find 无）；Sprint 1 产物（仓库无 `sprint1/`，仅 `decisions_log.md:63-75` 的 DEC-S1-004「决策时间: Sprint 1」）。 |
| **竞品样机拆机** | **有记录；拆机执行日期未见明确记载** | ①Sprint 2：CTO 提供「竞品拆机+消声室实测」SPL 数据（5 频点×6 角度），记录日 2026-05-26，`/home/it1234/algorithm_speaker/knowledge_base/measurements/competitor_anechoic.md:3-5`（仓库外 KB，无 git）。②Sprint 2 反推 ≈20 元/35 mm（RMS 2.84 dB）后被实测推翻 `agents/critic/memory.md:492-504`。③拆机工单 WO-S3-001（6 项未知量 U1–U6，零采购，闸门=转接板 PO 须等《6 项未知量确认报告》）2026-05-26 `M/sprint2-algorithm-baseline.md:28`；`PROJECT_REFERENCE.md:113-115`；文件 `R/sprint2/docs/sprint3_teardown_workorder.md`（git 首入库 06-05）。④拆机真值 N=16/d=55/L=825、8 路 A/B 对称串联、DAC ADAU1962A 8 路、功放 ACM3128A、喇叭 8Ω/10W 2 寸 88 dB：LESSON-006 日期 2026-05-27（`agents/critic/memory.md:492-494`）→ 拆机最迟 05-27 完成〔推断〕；`M/sprint3-d55-baseline.md:13-17`。⑤竞品画像 `R/knowledge_base/competitor/full_teardown_v2.md`（mtime 05-29 15:43，gitignore）。⑥竞品固件：DEC-S7-EXTINPUT-HIT9616-01（2026-09-02，`decisions_log.md:1032`）——SPON HIT-9616A12 RK3308 整机固件包**「不解包、不分析、不参考」（CTO 裁定）**；来源=同事从竞品原厂获得，渠道/授权**未确认**（D9，`:1048`）；落盘时间以 zip 文件 mtime 2026-07-31 代理，C8 偏差留痕未闭合（`:1032`）；登记文件 `R/knowledge_base/competitor/KB-EXT-SPON-HIT9616A12_FIRMWARE_REG.md`（09-02）；zip 在仓库外 `/home/it1234/algorithm_speaker/HIT-9616A12_Firmware_…zip`；`M/side-rejection-30db.md:13` 提「竞品固件登记」随公开仓库公开。⑦法律红线（竞品壳改装机禁止对外/拆机仅内部/改装留档）`M/sprint2-algorithm-baseline.md:28`；DEC-S3-003（`M/sprint3-d55-baseline.md:24`）。 |
| **方案 / 芯片选型** | **有记录** | ①DEC-S1-004 芯片锁定 ADSP-21569（`decisions_log.md:63-75`；`M/dsp-chip-decision.md:10`）；候选 SC589 vs 21569 `M/gate1-baseline-array-validation.md:19`。②Sprint 2 三候选阵列（经济 N16/d35、均衡 N24/Dolph-30、高性能 N32）+ 4 子带 dyadic 树形 FAS `M/sprint2-algorithm-baseline.md:14-16`；BOM 估算 `:20`；专利：Dolph-Chebyshev(1946) 公有领域、Boone EP1986464A1 告警被 critic 纠正 `:18`。③05-28 DEC-S3-PROC-01：量产芯片不可逆采购冻结，待 EZKIT cycle 实测、**21565 vs 21569 重评窗口开启**（`decisions_log.md:495-501,698`）——**未见显式关闭记录**（§6-D4）。④06-03 板上 L1：纯核 8ch=0.92×（实时 FAIL）→FIRA 转必需；官方 3.07× / 裕量 2.878×（`CLAUDE.md:47`；`M/r14-closed-fira-ruling.md:16`）。⑤阵列几何路线：d=30→d=55（PF-8，05-29，DEC-S3-GEOM-01 `decisions_log.md:442`；DEC-S2-006 作废标记 `:167`）。⑥PM 记忆里的订货号待办 `agents/project-manager/memory.md:595-596`（台架板丝印实为 ADSP-21569KBCZ10，`R/sprint3/audit/BENCH_OPS_CARD.md:5`）。 |
| **开发板 / EZKIT 采购与到货** | **采购批准有记录；到货日期未见** | ①DEC-S2-014（2026-05-26）：立即批准 EV-21569-EZKIT（下单索货期）+CCES+SHARC Audio Toolbox+消声室档期；喇叭单元供应商并行联络；Codec/功放/电源暂缓（`decisions_log.md:310-317`；`M/sprint2-algorithm-baseline.md:24`；`PROJECT_REFERENCE.md:115`）。②DEC-S3-PROC-01 明示 EZKIT 采购「不受影响（验证用途）」`decisions_log.md:498`。③**到货日期未见**。侧面证据：EZKIT 厂商资料入库不晚于 2026-06-01（仓库内 `knowledge_base/ezkit/` 目录 mtime 06-01 17:46）；C10/铁律九（06-02）缘起「EZKIT 上板厂商三陷阱」（`.claude/skills/critic/SKILL.md:1096`，说明 06-02 前后已在准备上电）；最早板上 L1 读数=06-03「R1 状态: L1 翻盘 cyc_8ch=1006935」（git 7563b3f，`decisions_log.md:234`）；06-02 首批提交已含「core-only graft: ADSP21569_LED 脚手架」（软件脚手架，非到货证据）。④**实际台架板身份**：第三方 AD-EXKIT V2.1 + ADSP-21569-SOM REV1.1，非官方 EV-SOMCRR-EZKIT，2026-06-11 坐实（`M/board-identity-fsru1-rescope.md:10`；`decisions_log.md:1012`）——**DEC-S2-014 采购的是哪块、何时到的，范围内无记录**（§6-D16）。 |
| **GitHub / 论文调研** | **论文有记录；外部 GitHub 开源调研未见** | ①论文入库（仓库外 KB `papers/`）：05-26 14:19–14:29（mtime）的 5 份 PDF——Dolph 1946、Properties of Dolph-Chebyshev Weighting Functions、Van Trees《Optimum Array Processing》2002、Boone 2009、Sensors 2024《Design of Differential Loudspeaker Line Array for Steerable FIB》（首页文本核过）。②2026-09-26 侧面 30 dB 文献检索：3 路检索 agent（A 声区 / B 音柱工程 / C 稳健校准），15 篇 PDF+1 XML+付费墙待取清单，`…/papers/2026-09_side30/README_论文索引.md:1-9`；`M/side-rejection-30db.md:14`。③09-28 D_cbt：Keele 2002（AES 5653，第三方副本，仓库登记 #17）+ Duran DDC `M/fib-cbt-literature.md:17-18`。④07-09 FIB 联网核实（WebSearch+WebFetch）`M/fib-cbt-literature.md:11`。⑤国标：`R/knowledge_base/standards/JYT_directional_speaker.jpeg`（05-29）→TASK-STD-A `agents/acoustic-simulation/memory.md:491-499`。⑥项目自己的 GitHub：`origin=https://github.com/Qiuu2/algo.git`，**公开**仓库，09-27 CTO 亲自 push（`M/side-rejection-30db.md:13,49`）。⑦**外部 GitHub/开源参考代码调研：未见**（仅 `M/board-identity-fsru1-rescope.md:10` 提「OpenADSP 生态」、`CLAUDE.md:98`「ADI reference design 可合法使用」、06-02 提交「ADSP21569_LED 脚手架嫁接」）。 |
| **框架 / 工具链选择** | **有记录，但「为何选」的决策记录未见** | ①多 Agent 框架=Kimi 生成包 + Claude Code Agent Teams（experimental）`CLAUDE.md:131`、`team_config.md:7`、`plan.md`。②算法/工具：CCES+SHARC Audio Toolbox；C（上板）+Python（仿真）；pyroomacoustics（首选）+Octave/MATLAB（交叉）`CLAUDE.md:92-95`；MATLAB MCP Core Server R2026a `agents/acoustic-simulation/skill.md:651-656`。③算法骨架：4 子带 dyadic 半带树 + FIRA 加速 + Dolph-Chebyshev −20 dB 8 路 Q15 表 `.claude/skills/dsp-algorithm/SKILL.md:36-47`。④「为什么选 Kimi 包 / Claude Code」「DSP 为什么 21569 而非别的」：除 DEC-S1-004 的 5 条依据外**未见**框架层 DEC。 |
| **资料入库** | **有记录** | ①仓库内 KB（gitignore，`.gitignore:1-2`）：ezkit 1280 文件（最老 2018，最新 06-03）、competitor 3 文件（05-29/05-30/09-02）、hardware_input 6 文件（05-29→06-05：`定向音柱AI数据_extracted.md` 05-29 19:16、`…含追问回复…` 05-30 15:53、`KB-DRV-TEST-001_*` 06-01 raw→06-05 extracted）、standards 1 文件（05-29）；`measurements/`、`papers/` 为**空目录**。②仓库外 KB：measurements 1 文件（05-26 15:14）、papers 23 文件（05-26→09-28）。③制度：铁律六/C8「外部输入 24h 入库」、CTO 外部接收声明清单（LESSON-013，`agents/critic/memory.md:623-647`；`.claude/skills/critic/SKILL.md:1081,1118`）。④外部 AI 输入：LESSON-010 提「外部 AI」把撤回值引为 L1（`agents/critic/memory.md:564-565`）；M1 架构「基于 claude.ai 总工设计」（`decisions_log.md:727`）；CTO 的「FIB+CBT 分析报告」不在库（`M/fib-cbt-literature.md:22`）。 |

---

## 5. 阶段边界线索（日期 + 来源）

> Sprint 编号取自 DEC 前缀首现与 `sprintN/` 目录首次入 git 日期〔推断〕；「阶段 ①–⑤」编号取自 `PROJECT_REFERENCE.md:107`（阶段①需求建模、阶段③算法仿真）、`R/sprint6/STAGE4_BRINGUP_CHECKLIST.md:1`（阶段 4=实时音频通路）、`R/sprint6/STAGE4_ALGORITHM_VALIDATION_TEST.md:5`（阶段⑤=自研 PCB）；**阶段②及⑥无定义**。

| 日期 | 边界 | 来源 |
|---|---|---|
| 2026-05-24 | 多 Agent 包生成 | `unzip -l`、`plan.md` |
| 2026-05-26 | Sprint 2 收口：Gate 1 PASSED / Gate 2 CLOSED（Sprint 1 无独立日期，只见 DEC-S1-004「决策时间: Sprint 1」）；同日 Sprint 3 立项（DEC-S3-001/002「硬件平台快速验证法」，并行自研主线） | `decisions_log.md:1-8,63-75,310,322`；`M/sprint2-algorithm-baseline.md:22,28`；`PROJECT_REFERENCE.md:113-115` |
| 2026-05-27 | CTO 拍 Sprint 3 主路线；`SKILL.md` v1.0.1 | `M/sprint3-d55-baseline.md:10`；`SKILL.md:498` |
| 2026-05-28 | P0 桌面仿真三项完成（DEC-S3-P0-01）；芯片不可逆采购冻结（DEC-S3-PROC-01） | `decisions_log.md:495-520` |
| 2026-05-29 | PF-8：几何统一 d=30→55（DEC-S3-GEOM-01）；POLICY v1.2/v1.3 | `decisions_log.md:442`（及 `:1004` 文档 v2.0 页脚）；POLICY 头 |
| 2026-06-02 | git 建库（首提交 4bf0f52）；**Sprint 4（FIRA/R14 线）**：`sprint4/` 与 sprint2/3 同日首入 git；C9/C10 立 | `git log`；`agents/critic/memory.md:649-669` |
| 2026-06-03 | EZKIT 板上 L1：8ch 裕量 1.32× 翻盘（DEC-S4-R1-8CH-01）；roster 锁档 | git 7563b3f/509dfa4（06-03）；`decisions_log.md:234`；`team_config.md:26-33` |
| 2026-06-04 | **R14 CLOSED / C9 RELEASED / ≥10× 判据退役**（Sprint 4 收口）；v1 路线裁定、三道关（Sprint 5 开始：`sprint5/` 06-04 首入 git，DEC-S5-* 首现 06-04） | `CLAUDE.md:47`；`M/r14-closed-fira-ruling.md:10`；`decisions_log.md:708-710,783,798,814` |
| 2026-06-05→06 | Sprint 5：H1/H2、SPL 口径、EQ O1；**06-06 T2 保守闭合 + 算力优化冻结令**；「下一阶段=WO-S6-AUDIO（M1→M2→M3）」 | `M/h1-line-state.md:10`；`decisions_log.md:724` |
| 2026-06-06→08 | **阶段 4（实时音频通路）/ Sprint 6 开始**：`sprint6/` 06-06 首入 git；STAGE4_BRINGUP_CHECKLIST；06-08 M1 架构定稿 | git 218ead7；`decisions_log.md:727` |
| 2026-06-11 | 台架板身份坐实（AD-EXKIT）+ F-SRU-1 re-scope | `decisions_log.md:1012` |
| 2026-06-16 | **阶段④软件部分实质收口**（M2 FIRA 波束上板 PASS）；M3 可听 demo 卡阵列硬件（阶段⑤） | `M/m2-board-pass-stage4.md:10,24`；`decisions_log.md:1014` |
| 2026-06-29→07-09 | 整机算法验证（阶段④软件收口后、阶段⑤自研 PCB 前）：Test0–3；07-08 极性闭合；07-09 通道映射修 | `R/sprint6/STAGE4_ALGORITHM_VALIDATION_TEST.md:5`；`decisions_log.md:1016-1020` |
| 2026-07-17→22 | 非产品阶段：提炼 starter kit；治理减法 SLIM-01~07 | `ee-agent-team-starter/README.md:41`；`decisions_log.md:1021-1029` |
| 07-22→09-02 | 「7-22 后无正式测试」；硬件仍 AD-EXKIT，Stage 5 无进展，R3 消声室无排期 | `decisions_log.md:1030` |
| 2026-09-02 | **Sprint 7 开始**：本轮升级=算法层；产品层（网络/控制/OTA）不做；`sprint7/` 首入 git | `decisions_log.md:1030`；`team_config.md:35` |
| 2026-09-26 | S7 侧面 ±90° 30 dB 子项目启动（DEC-S7-SIDE30-01） | `decisions_log.md:1091`；`M/side-rejection-30db.md:11` |
| 2026-10-02 | 最近一次落库：s7ff_v1 远场信号包（3a008e8/263e984）；本地 master 领先 origin 9 提交 | `git log`；`git status -sb` |

---

## 6. 疑点（按重要度分组；D 编号按发现顺序，非重要度）

### 高
- **D1 「v1.8」双义**：POLICY 文件 v1.8=§4B 三道关（2026-06-04，`POLICY:4,114,286`）；critic skill 页脚 v1.8=§12 DSP/FIRA 门（2026-06-03，`.claude/skills/critic/SKILL.md:1149`，LESSON-015 `agents/critic/memory.md:671`）；POLICY 里无 §12/FG1（grep 0 命中）。`critic/SKILL.md:7` 与 `CLAUDE.md:49` 的「POLICY v1.8」指前者。手册引用时应写「POLICY v1.8 §4B」「critic skill §12」。
- **D2 模板/假数据混在 persona 文件里**（见 §3.0）：`agents/critic/memory.md` 的 L11-348（含 `:42` 自标占位的 §2.1 与未标的 §2.2/§2.3）、LESSON-001~005（2023-11~2024-01 假日期，`:457-490`）、5 个角色 memory 全文、PM `:38-587`、DSP `:10-296,342-627`、acoustic `:10-464`。SLIM-03 有意延后清理 §2.1（`agents/critic/memory.md:42`）。**手册不得引用这些段落**；真 critic 教训从 LESSON-006 起。
- **D3 memory 正文里的过期数字没有撤回标签（C7 类残留）**：`dsp-chip-decision.md:14,17`（算力裕量 20–40×、「Compute was never the constraint」）与 `decisions_log.md:234`（06-03 板上 L1 推翻：8ch 1.32×，纯核 0.92× FAIL）矛盾；`sprint3-d55-baseline.md:15` 及索引 `MEMORY.md:18` 仍写「算力 17×/33×」；`gate1-baseline-array-validation.md:12`、`sprint2-algorithm-baseline.md:22-23`、`directivity-band-requirement.md:12` 以 d=30/L=0.45 为前提且正文无撤回标（索引 `MEMORY.md:15,17` 只对前两条加了 ⚠，没有对 `directivity-band-requirement` 加）。

### 中
- **D4 芯片「LOCKED」与采购冻结/重评并存**：`CLAUDE.md:92`、`M/dsp-chip-decision.md:10` 说 LOCKED；`decisions_log.md:495-501,698`（DEC-S3-PROC-01，2026-05-28）说量产芯片不可逆采购冻结、**21565 vs 21569 重评窗口开启**，待 EZKIT 实测。grep `21565` 只命中 05-28 前后条目（`:497,498,501,509,511,698,737`），**未见显式关闭记录**（板上 L1 06-03 后实际按 21569 做）。建议由 decisions_log 摘录那一路确认是否有关闭 DEC。
- **D5 Gate 编号两套**：`SKILL.md:371-391` Gate 1=项目计划审批、Gate 2=架构评审、Gate 3=原型 Go/No-Go、Gate 4=终审；`CLAUDE.md:107-113` Gate 1=首次阵列设计方案审定、Gate 2=ADI 芯片型号最终确认；decisions_log 头「Gate 1 PASSED / Gate 2 CLOSED」（`:8`）与 `M/dsp-chip-decision.md:17`（「closes the Gate-2 chip-selection」）按 CLAUDE.md 口径。SKILL.md 的是 Kimi 通用定义。
- **D6 `agent-team-ops-lessons.md:13` 过时且有危险**：写「lead/critic/dsp=opus-4-8」（06-10 起 Fable，`team_config.md:17-35`）；写「`.claude/skills` 是 `agents/<role>/skill.md` 的逐字副本，编辑 canonical 后需 re-cat」——**07-19/20 SLIM-01/04 后权威源反了**（`.claude/skills` 为权威，`agents/*/skill.md` 是指针）。若照旧 memory 去 re-cat，会把指针覆盖掉权威 skill。
- **D7 两个 `knowledge_base/`**：memory 的 `knowledge_base/measurements/competitor_anechoic.md`、`knowledge_base/papers/2026-09_side30/`（`M/sprint2-algorithm-baseline.md:30`、`M/side-rejection-30db.md:14`）在**仓库外** `/home/it1234/algorithm_speaker/knowledge_base/`；仓库内同名目录 `R/knowledge_base/measurements`、`papers` 是空目录；反过来仓库外 `competitor/` 是空的、仓库内 `competitor/` 有 3 个文件；两处都不受 git 管（仓库内的被 `.gitignore:1-2` 忽略），无法用 git 审计。
- **D8 日期来源不一致**：①git 历史自 2026-06-02 起，此前所有日期依赖 mtime/文字/memory。②`decisions_log.md:1022`（SLIM-02）写「已 commit ed83668 + push（2026-07-19）」，git 作者/提交日期=2026-07-20 10:40:05（reflog 同）；SLIM-06/07 的 DEC 日期 07-20，commit 07-22 10:42。手册建议「决策日期」取 DEC，「仓库状态日期」取 git。③POLICY/CLAUDE.md 在 06-04 前从未入 git（89bed86 说明）。
- **D9 护栏与实际做法对不上**：`CLAUDE.md:119-127`（$3/teammate、≤15 分钟、禁 sub-sub-agent）vs `PROJECT_REFERENCE.md:43-45`（启动 prompt 里写 10 分钟）——这两个数在同一份 CLAUDE.md 的**原版里就并存**（`git show 89bed86:CLAUDE.md` 第 139 行 10 分钟、第 265 行 15 分钟）；实际（`M/working-style-lessons.md:25`「一轮 ~36 min/63 万 token」；`PROJECT_REFERENCE.md:61` 为 Max plan）；范围内没有任何「预算/时限被执行」的记录。
- **D16 采购名与实物不符**：DEC-S2-014 批的是 EV-21569-EZKIT（`decisions_log.md:310-312`），`M/dsp-chip-decision.md:13` 也写 EV-21569-EZKIT；实际台架板是第三方 AD-EXKIT V2.1 + 21569-SOM（`M/board-identity-fsru1-rescope.md:10`，BENCH_OPS_CARD「CTO 已肉眼坐实」）。采购/到货记录范围内未见，需去采购/决策那一路核。

### 低
- **D10 疑似撤回值残留**：`agents/acoustic-simulation/skill.md:816` 写「d=55 仿真 1kHz=29.3° vs 竞品实测 16°」；LESSON-010（`agents/critic/memory.md:561`）列出的被撤回派生值就含 16.0°（竞品只实测 SPL，无 BW）。`decisions_log.md:582` 的「撤回值红线」也把 `d=30 / 14.9° / 19.1° / 19.2° / 16.0°` 列为「禁裸引」。该处无撤回标，很可能是 C7 残留（未核该 16° 的原始出处；〔推断〕该 MATLAB 节写于 05-28，早于 05-29 的撤回，故未被清扫）。
- **D11 hook 提示文字过期**：`cto-gate-softconfig.sh:59-60` 仍写「F-SRU-1 not-in-effect；板上 rc 全 0 复验前不得宣称 swap-safe」，该判据次日（06-11）已退役（`M/board-identity-fsru1-rescope.md:13-14`；`decisions_log.md:1012`）。不影响 hook 行为。
- **D12 索引/元数据落后**：`MEMORY.md:6` 仍说 CBT「直阵死路?⚠09-26 待核」，而 `fib-cbt-literature.md:15-17` 已在 09-28 更正；两个 memory 的 `modified:` 落后于 mtime（见 §0.3）；`r14-closed-fira-ruling.md:22` 悬空链接 `[[steering-line-constraints]]`。
- **D13 模板日期**：`SKILL.md:497` v1.0.0「2024-01-15」及 agents 里一切 2022–2024 日期都是 Kimi 模板，**不是项目日期**（项目最早日期 2026-05-24）；`SKILL.md:4`「ITC (In-The-Can)」全称仅此一处，其余文件无解释，来源未知。
- **D14 CLAUDE.md 页脚未随改动更新**：页脚写「v1.1.0（2026-07-19 …SLIM-02）」，但文件之后又被 SLIM-03（`:47` 状态旗，1656e02）与 SLIM-04（`:73` 脚注，bdc9126）改过，git 末次提交 07-20 11:18。
- **D15 〔推断〕KB 论文与 agent 工作流脱节**：仓库外 KB 的 `Design_of_Differential_Loudspe.pdf`（mtime 2026-05-26 14:19，首页即 Sensors 2024 差分扬声器线阵 FIB 论文）在 05-26 就在库里，而 `M/fib-cbt-literature.md:11` 记 07-09 才联网核实「FIB 到底是什么」并承认早先讲错——说明库里论文没被当作检索入口〔推断，未核该 PDF 是否 05-26 才入库还是仅 mtime〕。
- **D17 时效状态**：memory 里「N 个提交未推」类陈述随时失效；本次按本地跟踪引用核到 master 领先 origin/master 9 提交（`git status -sb`），与 `M/side-rejection-30db.md:48` 及 `MEMORY.md:12` 一致，但远端真实状态未联网核。

### 给手册作者的取用建议（来自上面的核查）
- 治理/团队章节：以 `CLAUDE.md`、`.claude/team_config.md`、`.claude/skills/critic/SKILL.md §11-§12`、POLICY、`decisions_log.md:1021-1029` 为准；memory 只作索引。
- 「项目经验教训」章节：critic LESSON-006~015、`agents/critic/memory.md:775-793`、`agents/dsp-algorithm/memory.md:629-640`、`agents/project-manager/memory.md:591-624`、`agents/acoustic-simulation/memory.md:466-499` 是 persona 层仅有的真料；其余 persona 文件不要引。
- 日期：05-24→06-01 只能写「据文件时间/文字」；06-02 起可用 git。
