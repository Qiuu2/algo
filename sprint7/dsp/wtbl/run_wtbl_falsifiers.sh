#!/usr/bin/env bash
# run_wtbl_falsifiers.sh -- S7-SIDE30: proves that run_wtbl_checks.sh CAN FAIL (critic R3e F1/J1).
# Builds doctored copies in a temp dir and runs the full gate on each via WTBL_HDR / WTBL_RUNBOOK; every case must end
# in "OVERALL FAIL". The default (untouched) inputs must end in "OVERALL PASS". Output: wtbl_falsifiers.log next to it.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
H="$ROOT/sprint6/dsp/audio/m1_cces_project/src/m2_wtbl_q15.h"
RB="$ROOT/sprint7/docs/S7_TESTER_RUNBOOK_WTBL.md"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
LOG="$HERE/wtbl_falsifiers.log"
sed 's/{  5285,  8787,/{  8787,  5285,/' "$H" > "$T/perm_last_row.h"                     # R3e round-1 case: sum unchanged
sed 's/{ 16080, 13167,/{ 13167, 16080,/' "$H" > "$T/perm_first_row.h"
sed 's|^ \* Generator anchor: reproduces| * Generator anchor (\xe9\x94\x9a): reproduces|' "$H" > "$T/utf8.h"
sed 's/| 4（RS-A） | 5（RS-B） |/| 4（RS-B） | 5（RS-A） |/' "$RB" > "$T/rb_labels_swapped.md"
sed 's/| sel | 0（D20） |/| sel | 0（D25） |/' "$RB" > "$T/rb_label_d25.md"
sed 's/| 152407 | 162056 |/| 162056 | 152407 |/' "$RB" > "$T/rb_sums_swapped.md"
fail=0
{
  echo "run_wtbl_falsifiers.sh  $(date -u +%Y-%m-%dT%H:%MZ)  HEAD $(git -C "$ROOT" rev-parse --short HEAD)"
  for cfg in "DEFAULT" "WTBL_HDR=$T/perm_last_row.h" "WTBL_HDR=$T/perm_first_row.h" "WTBL_HDR=$T/utf8.h" \
             "WTBL_HDR=$T/does_not_exist.h" "WTBL_RUNBOOK=$T/rb_labels_swapped.md" "WTBL_RUNBOOK=$T/rb_label_d25.md" \
             "WTBL_RUNBOOK=$T/rb_sums_swapped.md"; do
    if [ "$cfg" = DEFAULT ]; then out="$(bash "$HERE/run_wtbl_checks.sh" 2>&1)"; want="OVERALL PASS"
    else out="$(env "$cfg" bash "$HERE/run_wtbl_checks.sh" 2>&1)"; want="OVERALL FAIL"; fi
    got="$(echo "$out" | grep -o 'OVERALL PASS\|OVERALL FAIL' | tail -1)"
    why="$(echo "$out" | grep -E 'step 1 FAIL|step 1b FAIL|MISMATCH|non-ASCII|missing/unreadable|CHECK FAIL' | head -3 | tr '\n' ';' | sed "s|$T/||g")"
    if [ "$got" = "$want" ]; then res=OK; else res=WRONG; fail=1; fi
    echo "[$res] ${cfg##*/}: expected '$want', got '$got' | ${why}"
  done
  [ $fail -eq 0 ] && echo "FALSIFIERS: ALL OK" || echo "FALSIFIERS: SOME WRONG"
} 2>&1 | tee "$LOG"
exit $fail
