#!/usr/bin/env bash
# cto-gate-softconfig.sh — PreToolUse(Bash) hook.
# CTO-gate (POLICY-PROV-001 / team_config commit-discipline): mechanically BLOCK any
# `git commit` that stages the codec-enable / softcfg命脉 file m1_softconfig.c, UNLESS the
# CTO explicitly approved this commit by exporting CTO_OK=1 in the session shell.
#
# WHY: while the CTO is out (2026-06), no codec-enable LOGIC change (block-B / enable
# sequence / address-override source edit) may land without sign-off. Obs/probe-only edits
# also pass through this file, so the gate is at the COMMIT (the irreversible-ish "land"
# step), not at working-tree edits. The block is overridable in one line (CTO_OK=1) so a
# remotely-approved commit is never stuck.
#
# Block mechanism: exit code 2 (stderr is shown to the agent). Doc: hooks.md PreToolUse.
# JSON arrives on stdin; tool_input.command + cwd parsed via python3 (no jq dependency).
set -u

INPUT="$(cat)"

# Parse the bash command string and cwd from the PreToolUse stdin JSON.
read -r -d '' PYEXTRACT <<'PY' || true
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    print("\t"); sys.exit(0)
ti = d.get("tool_input", {}) or {}
print((ti.get("command","") or "").replace("\n"," ") + "\t" + (d.get("cwd","") or ""))
PY

PARSED="$(printf '%s' "$INPUT" | python3 -c "$PYEXTRACT" 2>/dev/null || printf '\t')"
CMD="${PARSED%%$'\t'*}"
CWD="${PARSED#*$'\t'}"

# Only intercept git commit; everything else passes untouched.
case "$CMD" in
  *"git commit"*) : ;;
  *) exit 0 ;;
esac

# Inspect the staged set in the repo where the commit will run.
[ -n "$CWD" ] && cd "$CWD" 2>/dev/null || true
STAGED="$(git diff --cached --name-only 2>/dev/null || true)"

if printf '%s\n' "$STAGED" | grep -q "m1_softconfig"; then
  if [ -z "${CTO_OK:-}" ]; then
    cat >&2 <<EOF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⛔ CTO-GATE blocked this commit — it stages m1_softconfig.c
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
m1_softconfig.c carries the codec-enable / softcfg命脉 logic.
POLICY-PROV-001 + team_config commit-discipline: no codec-enable
change lands without CTO sign-off (esp. while CTO is out).

Staged paths matching the gate:
$(printf '%s\n' "$STAGED" | grep "m1_softconfig" | sed 's/^/  - /')

If the CTO has explicitly approved THIS commit, set and retry:
  export CTO_OK=1
Otherwise: pause, report to CTO, do not commit (F-SRU-1 not-in-effect;
no swap-safe claim before板上 rc 全 0 复验).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
    exit 2
  fi
fi
exit 0
