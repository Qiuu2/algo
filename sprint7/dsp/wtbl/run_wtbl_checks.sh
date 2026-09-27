#!/usr/bin/env bash
# run_wtbl_checks.sh -- S7-SIDE30 M2_WTBL_SEL desktop gate (DEC-S7-SIDE30-01 (2)(4)).
#   1.  gen_m2_wtbl.py --check : header == fresh dual-track generation (anchor: reproduces frozen D20)
#   1b. built-in falsifier     : the same check on a temp copy whose last row has two weights swapped (row sum
#                                unchanged) MUST FAIL -- proves step 1 can fail (critic R3e F1)
#   2.  run_guard_check.sh     : 13 compile configs (incl. 3 WTBL) + 7 #error falsifiers (incl. X6/X7 WTBL)
#   3.  run_s7_preproc_equiv.sh: every NON-WTBL macro set is gcc -E identical to HEAD (0 diff lines)
#   4.  runbook sec 2 tables   : (a) Q15 row sums printed by gcc from the SAME headers the firmware includes
#                                (wtbl_sums_host.c) == the sums row; (b) generator sel:label list == the sel/label row
#   5.  ASCII-only             : the CCES target files of this feature contain no non-ASCII byte (dsp-algorithm skill A6)
# Overrides for falsifier runs: WTBL_HDR=<header copy> (steps 1, 4, 5), WTBL_RUNBOOK=<runbook copy> (step 4).
# No `set -o pipefail` on purpose: step 3 uses `grep | grep -q` inside `if`, where pipefail would turn grep -q's early
# exit (SIGPIPE upstream) into a false "no diff". Exit codes of piped commands are read from PIPESTATUS instead.
# Board behaviour (sel switching, OOB fallback) is NOT provable on the desktop: it is checked by the tester
# per sprint7/docs/S7_TESTER_RUNBOOK_WTBL.md (g_m2_wtbl_sel_applied / g_m2_wtbl_oob_count readbacks).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
PY=/usr/bin/python3
SRC="$ROOT/sprint6/dsp/audio/m1_cces_project/src"
HDR="${WTBL_HDR:-$SRC/m2_wtbl_q15.h}"
RB="${WTBL_RUNBOOK:-$ROOT/sprint7/docs/S7_TESTER_RUNBOOK_WTBL.md}"
rc=0
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "[wtbl] 1/5 table same-source check ($HDR)"
WTBL_HDR="$HDR" $PY "$HERE/gen_m2_wtbl.py" --check 2>&1 | grep -v 'UserWarning\|chebwin('
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "[wtbl]   step 1 FAIL"; rc=1; }

echo "[wtbl] 1b    falsifier: a copy with two weights of the last row swapped must FAIL step 1"
$PY - "$HDR" "$TMP/perm.h" <<'EOF'
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
m = list(re.finditer(r"\{\s*(\d+),\s*(\d+),", t))[-1]      # last table row; swap its first two weights (sum unchanged)
t = t[:m.start(1)] + m.group(2) + t[m.end(1):m.start(2)] + m.group(1) + t[m.end(2):]
open(sys.argv[2], "w", encoding="utf-8").write(t)
EOF
if [ $rc -ne 0 ]; then
    echo "    skipped: step 1 already failed (1b only proves that a PASSING check can fail)"
elif cmp -s "$HDR" "$TMP/perm.h"; then
    echo "[wtbl]   step 1b FAIL: could not build a permuted copy"; rc=1
else
    WTBL_HDR="$TMP/perm.h" $PY "$HERE/gen_m2_wtbl.py" --check > "$TMP/perm.out" 2>&1; pr=$?
    if [ $pr -ne 0 ] && grep -q 'CHECK FAIL' "$TMP/perm.out"; then    # a content rejection, not a crash (R3e J3)
        echo "    permuted copy rejected as it must be: $(grep -m1 'CHECK FAIL' "$TMP/perm.out")"
    else
        echo "[wtbl]   step 1b FAIL: the checker did not reject the permuted table with CHECK FAIL (exit $pr)"; rc=1
    fi
fi

echo "[wtbl] 2/5 guard matrix"
bash "$ROOT/sprint6/dsp/audio/run_guard_check.sh" > "$TMP/guard.out" 2>&1; g=$?
grep -E 'OVERALL' "$TMP/guard.out"; [ $g -eq 0 ] || rc=1

echo "[wtbl] 3/5 default-preprocessor-equivalence vs ${S7_REF:-HEAD}"
bash "$ROOT/sprint7/dsp/host/run_s7_preproc_equiv.sh" > "$TMP/eq.out" 2>&1; e=$?
grep -E '^=== \[|OVERALL' "$TMP/eq.out" | sed 's/^/    /'
if grep -E '^=== \[' "$TMP/eq.out" | grep -qv 'diff lines: 0 '; then
    echo "[wtbl]   NOTE: a non-zero diff set above -- expected ZERO for this change (all WTBL code is #ifdef M2_WTBL_SEL)"; rc=1; fi
[ $e -eq 0 ] || rc=1

echo "[wtbl] 4/5 runbook sec 2: applied_sum row == gcc sums of the headers; sel/label row == generator labels"
mkdir -p "$TMP/inc"; cp "$HDR" "$TMP/inc/m2_wtbl_q15.h"
csums=""
if gcc -std=c99 -Wall -Wextra -Werror -I"$ROOT/sprint4/dsp/fira" -I"$TMP/inc" \
       "$HERE/wtbl_sums_host.c" -o "$TMP/sums" 2> "$TMP/cc.err"; then csums="$("$TMP/sums")"; else cat "$TMP/cc.err"; fi
rsums="$(grep -E '^\| 8 个 Q15 权重之和' "$RB" | tr -d ' ' | awk -F'|' '{for (i = 3; i < NF; i++) printf "%s%s", (i > 3 ? " " : ""), $i; print ""}')"
glabels="$(WTBL_HDR="$HDR" $PY "$HERE/gen_m2_wtbl.py" --labels 2>/dev/null)"
rlabels="$(awk '/^\| 8 个 Q15 权重之和/ {print prev2} {prev2 = prev1; prev1 = $0}' "$RB" | tr -d ' ' \
           | awk -F'|' '{for (i = 3; i < NF; i++) printf "%s%s", (i > 3 ? " " : ""), $i; print ""}' | sed 's/（/:/g; s/）//g')"
echo "    gcc header sums  : ${csums:-<none>}"
echo "    runbook sums row : ${rsums:-<none>}"
echo "    generator labels : ${glabels:-<none>}"
echo "    runbook sel row  : ${rlabels:-<none>}"
if [ -z "$csums" ] || [ "$csums" != "$rsums" ]; then
    echo "[wtbl]   MISMATCH (or missing) sums -- the tester would check applied_sum against wrong numbers"; rc=1; fi
if [ -z "$glabels" ] || [ "$glabels" != "$rlabels" ]; then
    echo "[wtbl]   MISMATCH (or missing) sel/label row -- the tester would read the wrong table name"; rc=1; fi

echo "[wtbl] 5/5 ASCII-only CCES target files"
bad=0
for f in "$HDR" "$SRC/m1_loopback_tdm.c" "$SRC/m1_loopback_tdm.h" "$HERE/wtbl_sums_host.c"; do
    if [ ! -r "$f" ]; then echo "    missing/unreadable: $f"; bad=1; continue; fi     # R3e J2
    if LC_ALL=C grep -qP '[^\x00-\x7F]' "$f"; then
        echo "    non-ASCII in $f:"; LC_ALL=C grep -nP '[^\x00-\x7F]' "$f" | head -3 | cut -c1-120; bad=1; fi
done
if [ $bad -eq 0 ]; then echo "    all ASCII"; else rc=1; fi

if [ $rc -eq 0 ]; then echo "[wtbl] OVERALL PASS"; else echo "[wtbl] OVERALL FAIL"; fi
exit $rc
