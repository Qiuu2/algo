#!/usr/bin/env bash
# run_wtbl_checks.sh -- S7-SIDE30 M2_WTBL_SEL desktop gate (DEC-S7-SIDE30-01 (2)(4)).
#   1. gen_m2_wtbl.py --check : m2_wtbl_q15.h == fresh dual-track generation (anchor: reproduces frozen D20)
#   2. run_guard_check.sh     : 13 compile configs (incl. 3 WTBL) + 7 #error falsifiers (incl. X6/X7 WTBL)
#   3. run_s7_preproc_equiv.sh: every NON-WTBL macro set is gcc -E identical to HEAD (0 diff lines)
# Board behaviour (sel switching, OOB fallback) is NOT provable on the desktop: it is checked by the tester
# per sprint7/docs/S7_TESTER_RUNBOOK_WTBL.md (g_m2_wtbl_sel_applied / g_m2_wtbl_oob_count readbacks).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
PY=/usr/bin/python3
rc=0
echo "[wtbl] 1/3 table same-source check"
$PY "$HERE/gen_m2_wtbl.py" --check 2>&1 | grep -v 'UserWarning\|chebwin(' || rc=1
echo "[wtbl] 2/3 guard matrix"
bash "$ROOT/sprint6/dsp/audio/run_guard_check.sh" > "$HERE/.guard.out" 2>&1; g=$?
grep -E 'OVERALL' "$HERE/.guard.out"; [ $g -eq 0 ] || rc=1; rm -f "$HERE/.guard.out"
echo "[wtbl] 3/3 default-byte-equivalence vs ${S7_REF:-HEAD}"
bash "$ROOT/sprint7/dsp/host/run_s7_preproc_equiv.sh" > "$HERE/.eq.out" 2>&1; e=$?
grep -E '^=== \[|OVERALL' "$HERE/.eq.out" | sed 's/^/    /'
if grep -E '^=== \[' "$HERE/.eq.out" | grep -qv 'diff lines: 0 '; then
    echo "[wtbl]   NOTE: a non-zero diff set above -- expected ZERO for this change (all WTBL code is #ifdef M2_WTBL_SEL)"; rc=1; fi
[ $e -eq 0 ] || rc=1; rm -f "$HERE/.eq.out"
if [ $rc -eq 0 ]; then echo "[wtbl] OVERALL PASS"; else echo "[wtbl] OVERALL FAIL"; fi
exit $rc
