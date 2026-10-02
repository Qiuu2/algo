# 《算法开发手册》原始摘录与提示词索引

> **性质**：阅读笔记，不是结论。由 2026-10-02 的 PM 会话派子代理分头通读仓库、git 历史、记忆文件和本机会话记录后写成。**未逐条过 critic**；引用任何数字或结论前，回原文核对。
> **入库依据**：CTO 2026-10-02 指示"摘录和提示词索引存进仓库，放在 knowledge_base/manual_sources/ 下，单独提交一次"。
> **可信度顺序**（CTO 指定）：决策日志 > 执行单 / runbook > git 提交记录 > 记忆文件。摘录里的引用按这个顺序取证。

## 文件清单

| 文件 | 读了什么 | 备注 |
|---|---|---|
| `digest_A_decisions.md` | `sprint2/docs/decisions_log.md`、`sprint2/docs/prd_update.md`、状态快照 | 最高可信层；含 173 行时间线、阶段边界线索、23 条疑点（§5） |
| `digest_B_sprint2_4.md` | `sprint2/`、`sprint4/` 其余 tracked .md | 跳过 A 已读的两份 |
| `digest_C_sprint3.md` | `sprint3/` 全部 tracked .md（64 份） | 疑点 D1–D21（D8 = 子带撤回漏标，已于 10-02 补） |
| `digest_D_sprint5_deliv.md` | `sprint5/`、`deliverables/` | |
| `digest_E_sprint6_kb_tools.md` | `sprint6/`、`knowledge_base/`、`tools/`、`references/` | |
| `digest_F_sprint7_docs.md` | `sprint7/docs/*.md` + 信号包 README | |
| `digest_G_sprint7_critic_code.md` | `sprint7/` 其余 .md（critic / dsp / sim / tools） | |
| `digest_H_agents_memory.md` | `agents/`、团队与治理配置、自动记忆 | §6 列了过时记忆 |
| `digest_I_prompts.md` | CTO 提示词索引：`~/.claude/history.jsonl`（349 块）+ 3 份幸存完整会话记录（107 块） | 28 个主题、59 处丢失的粘贴、前期环节线索 |
| `prompts_crosscheck_other_project.md` | `history.jsonl` 里记在本机另一个项目目录下、但关键词疑似相关的 19 条 | 3 条相关（都是本项目提示词先误贴到别的窗口），16 条无关、只列日期和会话 |

## 使用须知

1. **行号**：摘录里的 `路径:行号` 对应读取时的 HEAD `263e984`（2026-10-02）。之后的提交（例如同日的勘误补标）会让少数文件行号位移几行，按内容搜即可。
2. **`all:NNNN` / `trans:NNNN`**：digest_I 里的这类指针是本机临时抽取文件的行号（`prompts_all.md` 3798 行、`prompts_transcripts.md` 1473 行）。这两份原始抽取**没有入库**（仓库是公开的，原文里有与本项目无关的内容），需要原话时回本机 `~/.claude/history.jsonl` 和 `~/.claude/projects/<项目目录>/<session>.jsonl`。
3. **疑点不是结论**：各摘录的"疑点 / 矛盾"段是读者发现的问题。其中一部分已在 2026-10-02 的修正提交里处理（子带撤回补标见 `sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md` §6；决策日志与 PRD 表头已更正），其余仍待核。
4. **会话记录不完整**：`history.jsonl` 只存键入和粘贴的文字，59 处粘贴已丢失；完整会话记录只剩 3 份（09-02、09-26、10-01 起）。06-02 之前没有 git 历史（首个 commit `4bf0f52`）。5 月写的文档是分批入库的：决策日志 06-02（`13be4b3`），PRD、交接文档、仿真完成度审计等 sprint2/docs 若干份 06-05（`4d7e528`），其余多数 06-09（`43aad40`）。所以 5 月的日期以文内日期和提示词时间为准。
5. **每份摘录开头都有一行公开版说明**：摘录按写时原文照录，会出现已撤回或已推翻的数字，采信前以决策日志和撤回登记为准。

## 公开仓库处理（与本机原稿的差异）

- 删去了一个个人邮箱地址和一个 Windows 用户目录名（两者在仓库其他文件里已存在，这里不再复写），以及一个可能属于另一项目的本机压缩包文件名。
- digest_I 的 T24（厂家服务器 / 后台 / 终端同屏）一线按 CTO 2026-10-02 裁定不进手册：时间线只留日期、会话和指针，§2 主题段改为一句话。
- 产品参数分类分支（`origin/claude/product-parameter-taxonomy-lbflde`）同样不进手册，摘录里没有涉及。
- `prompts_crosscheck_other_project.md` 里 16 条无关提示词只列日期和会话，不写内容，也不写那个项目的名称和目录。
