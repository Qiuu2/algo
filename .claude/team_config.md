# ITC Agent Team — Roster & Model Tiering (LOCKED)

> Authoritative team configuration. Every teammate spawn MUST follow this table.
> Mechanism: model is set at spawn via the `Agent` tool `model` arg (alias resolves to the exact ID below);
> no live re-tier — changing a teammate's model = respawn (fresh context). No persistent per-skill model
> field exists, so this file is the source of truth; spawns are checked against it.
> Environment: Claude Code CLI 2.1.161, Agent Teams experimental (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1).

## Model resolution map (alias the Agent tool accepts -> exact model ID, this env)
| alias | exact model ID | gen |
|---|---|---|
| `opus`   | `claude-opus-4-8`            | Opus 4.8 (latest) |
| `sonnet` | `claude-sonnet-4-6`          | Sonnet 4.6 |
| `haiku`  | `claude-haiku-4-5-20251001`  | Haiku 4.5 |

## Locked roster (role -> exact model -> effective date)
| role | exact model | effective | status | notes |
|---|---|---|---|---|
| project-manager (lead) | `claude-opus-4-8` | 2026-06-03 | ONLINE | session lead; reports to CTO |
| critic | `claude-opus-4-8` | 2026-06-03 | ONLINE (agentId ab86…) | command line; not downgraded — depth matters |
| dsp-algorithm | `claude-opus-4-8` | 2026-06-03 | RE-TIER PENDING SPAWN | Sonnet instance a9ba… RETIRED; next spawn = Opus; context on disk (commit 3a92754 + decisions_log + int_history_proof.py) |
| testing | `claude-sonnet-4-6` | 2026-06-03 | not yet started | CTO will temporarily raise to `claude-opus-4-8` for board-verification phase |
| structure | `claude-sonnet-4-6` | 2026-06-03 | on demand | low activity on FIRA line |
| hardware-design | `claude-sonnet-4-6` | 2026-06-03 | on demand | — |
| literature-patent | `claude-sonnet-4-6` | 2026-06-03 | on demand | — |
| project-document | `claude-sonnet-4-6` | 2026-06-03 | on demand | — |
| acoustic-simulation | (deferred) | — | not started | raise to `claude-opus-4-8` when real COMSOL evidence phase starts |

**Current FIRA line = lead + critic + dsp-algorithm, all `claude-opus-4-8`.** Others spawned on demand per table.

## Peer-challenge protocol (ON — 2026-06-03)
- Teammates may `SendMessage` each other **directly**; the critic MAY rebut dsp-algorithm (or any teammate) in the mailbox **without routing through the lead**.
- Lead (PM) arbitrates only: (a) a BLOCKER deadlock between teammates, or (b) anything hitting a CTO gate (Gate 1/2, ESCALATED, budget). A critic BLOCKER halts the artifact regardless of author.
- Lead remains the ONLY node reporting to the CTO (synthesis), but no longer the mandatory relay between dsp <-> critic.
- Previously (rounds 1-3 of the FIRA contract fix) the lead manually relayed dsp<->critic; from now the two converse directly and the lead receives the converged result + any escalation.

## Commit discipline (2026-06-04, CTO-mandated after the F5-A deviation — HARD RULE)
- **不得在独立 critic verdict 前 commit。** Teammate 自己的对抗式自审**不满足门禁**——只有独立 critic teammate 出具的、带 `reviewer: critic @ <exact model ID> / <date>` 标记的 verdict 才能放行 commit。
- **硬顺序**：实现 → 桌面自验 → SendMessage critic → **收到独立 verdict** → PASS 才 commit ／ BLOCKER/MAJOR 则修复后重新 challenge。lead 在**每份派单 prompt** 中显式写入此顺序；任何先 commit 后 verdict 的行为 = 流程偏差，必须**原样上报 CTO**（不得自行消化）。
- **理由**：先 commit 的代码若随后被裁 BLOCKER 而已被下游引用，回退成本非零。缘起：2026-06-04 F5-A——dsp 在自审后、独立 verdict 前提交（verdict 事后 PASS、未致损，但口子是真的）。
- 适用范围：所有 teammate、所有代码/文档交付物；唯一豁免 = critic 明文预先豁免的纯笔误级修正（critic 自己指定措辞的 Fix 落地）。

## Change control (audit)
- Changing any role's model = edit this table + log the change (old->new, date, reason) in decisions_log, per POLICY-PROV-001 change-trail discipline.

## Step-3 audit integration (2026-06-04, CTO-mandated — IN EFFECT)
- **Every critic verdict MUST carry**: `reviewer: critic @ <exact model ID> / <date>` in its report header (audit chain, aligns C5 traceability). The lead enforces this in every critic dispatch; a verdict without the tag is returned for re-issue.
- **Retroactive record**: all six F4-line critic verdicts (2026-06-03~04: D1b+M2 / INT-domain / pack80+phase-reject / A5 flush-back / A5 symbol-fix gate / DEC-phase-fix) = `reviewer: critic @ claude-opus-4-8`. Recorded in `sprint4/dsp/fira/F4_BITEXACT_HANDOFF.md` §3/§8.
- **Model-change trail**: any roster change = edit the table above + a decisions_log line (old -> new, effective date, reason, who approved). No silent re-tiering.
- dsp re-tier executed this session: `claude-sonnet-4-6` (instance a9ba…, retired 2026-06-03) -> `claude-opus-4-8` (effective 2026-06-03, CTO Step-2 confirmation).
