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

## Change control (audit)
- Changing any role's model = edit this table + log the change (old->new, date, reason) in decisions_log, per POLICY-PROV-001 change-trail discipline.
- See Step-3 audit integration (critic verdicts carry the reviewer's exact model ID) — to be appended.
