#!/usr/bin/env bash
# run_s7_probe_guard_check.sh -- desktop checks for the WO-S7-B6.3 bench probe (sprint7/dsp/probe).
#   Modelled on sprint5/dsp/harness/run_guard_check.sh (R16 lesson: plain gcc compiles ONLY the desktop path,
#   so the TARGET-guarded regions must be syntax-checked with the guard macros defined + BSP mock headers).
#
# Checks (all must PASS; exit 0 = all PASS):
#   (A) s7_wallclock_probe.c  guarded (-DFIRA_USE_REAL_ADI_FIR_HEADER -DTARGET_SHARC), sprint5 mock BSP
#   (B) s7_wallclock_probe.c  guarded + -DS7_PROBE_INNER + -DS7_PROBE_FA_BLOCK1 + -DS7_PROBE_SYN_FG (all optional paths)
#   (C) fira_tree_probe.c     guarded + -DS7_PROBE_INNER (the diagnostic copy WITH its inner brackets)
#   (D) fira_tree_probe.c     guarded, WITHOUT S7_PROBE_INNER (tag lines inert -> same as the frozen original)
#   (E) fira_tree_probe.c     desktop path (no guard) -- the placeholder chain must still parse
#   (F) VERBATIM: stripping every S7P-tagged line from fira_tree_probe.c must reproduce the frozen fira_tree.c
#       byte-for-byte (md5 7616c41102946c357e9c70fafcd51da3 at copy time; tools/make_fira_tree_probe.py --check)
#   (G) ASCII-only on every new .c/.h in this directory (CCES SHARC chokes on UTF-8)
#   (H) frozen-file guard: sprint4/dsp/fira/fira_tree.c md5 unchanged vs the value recorded at copy time
#
# -fsyntax-only ONLY (no link/run): mocks are parse-time stand-ins, not BSP behaviour. The desktop host
#   build+run lives in run_s7_probe_host.sh. Run from anywhere.
set -u
HDIR="$(cd "$(dirname "$0")" && pwd)"                       # sprint7/dsp/probe
ROOT="$(cd "$HDIR/../../.." && pwd)"                         # repo root
STUB5="$ROOT/sprint5/dsp/harness/guard_stub_inc"            # sys/cache.h, services/pwr/adi_pwr.h, thin adi_fir.h
STUB7="$HDIR/guard_stub_inc"                                 # full Legacy adi_fir.h transcription (for the copy)
INC=( -I"$ROOT/sprint4/dsp/core_only/src"
      -I"$ROOT/sprint4/dsp/core_only/include"
      -I"$ROOT/sprint4/dsp/core_only/bench"
      -I"$ROOT/sprint4/dsp/fira"
      -I"$HDIR" )
WERR=( -Wall -Wextra -Werror=implicit-function-declaration -Werror=int-conversion -Werror=incompatible-pointer-types )
GUARD=( -DFIRA_USE_REAL_ADI_FIR_HEADER -DTARGET_SHARC )
FROZEN_MD5_AT_COPY="7616c41102946c357e9c70fafcd51da3"

overall=0
run_one() {   # $1=label ; rest = gcc args
    local label="$1"; shift
    echo "[s7-guard] $label"
    if gcc -fsyntax-only "$@"; then echo "[s7-guard]   PASS ($label)"; else echo "[s7-guard]   FAIL ($label)"; overall=1; fi
}

run_one "(A) s7_wallclock_probe.c guarded, sprint5 mock BSP" \
    "${WERR[@]}" "${GUARD[@]}" -I"$STUB5" "${INC[@]}" "$HDIR/s7_wallclock_probe.c"
run_one "(B) s7_wallclock_probe.c guarded + S7_PROBE_INNER + S7_PROBE_FA_BLOCK1 + S7_PROBE_SYN_FG" \
    "${WERR[@]}" "${GUARD[@]}" -DS7_PROBE_INNER -DS7_PROBE_FA_BLOCK1 -DS7_PROBE_SYN_FG -I"$STUB5" "${INC[@]}" "$HDIR/s7_wallclock_probe.c"
# The copy uses '#pragma align 32' (CCES) -> gcc prints 'unknown pragma' under -Wall; that is a real SHARC
# pragma (also in the frozen original), so -Wno-unknown-pragmas keeps the check readable; nothing is promoted.
run_one "(C) fira_tree_probe.c guarded + S7_PROBE_INNER (full Legacy mock)" \
    "${WERR[@]}" -Wno-unknown-pragmas "${GUARD[@]}" -DS7_PROBE_INNER -I"$STUB7" -I"$STUB5" "${INC[@]}" "$HDIR/fira_tree_probe.c"
run_one "(D) fira_tree_probe.c guarded, S7_PROBE_INNER undefined (tags inert)" \
    "${WERR[@]}" -Wno-unknown-pragmas "${GUARD[@]}" -I"$STUB7" -I"$STUB5" "${INC[@]}" "$HDIR/fira_tree_probe.c"
run_one "(E) fira_tree_probe.c desktop path (no guard) + S7_PROBE_INNER" \
    "${WERR[@]}" -Wno-unknown-pragmas -DS7_PROBE_INNER "${INC[@]}" "$HDIR/fira_tree_probe.c"

echo "[s7-guard] (F) verbatim check: strip S7P lines == frozen fira_tree.c"
if /usr/bin/python3 "$HDIR/tools/make_fira_tree_probe.py" --check; then echo "[s7-guard]   PASS (F)"; else echo "[s7-guard]   FAIL (F)"; overall=1; fi

echo "[s7-guard] (G) ASCII-only on new sources"
nonascii=0
for f in "$HDIR"/*.c "$HDIR"/*.h "$HDIR"/guard_stub_inc/drivers/fir/adi_fir.h; do
    if LC_ALL=C grep -nP '[^\x00-\x7F]' "$f" >/dev/null; then echo "[s7-guard]   non-ASCII in $(basename "$f")"; nonascii=1; fi
done
if [ $nonascii -eq 0 ]; then echo "[s7-guard]   PASS (G)"; else echo "[s7-guard]   FAIL (G)"; overall=1; fi

echo "[s7-guard] (H) frozen fira_tree.c md5 unchanged since the copy was made"
cur="$(md5sum "$ROOT/sprint4/dsp/fira/fira_tree.c" | awk '{print $1}')"
if [ "$cur" = "$FROZEN_MD5_AT_COPY" ]; then echo "[s7-guard]   PASS (H) $cur"; else echo "[s7-guard]   FAIL (H) frozen md5 $cur != $FROZEN_MD5_AT_COPY -> re-run tools/make_fira_tree_probe.py or delete the copy"; overall=1; fi

echo "[s7-guard] overall: $([ $overall -eq 0 ] && echo PASS || echo FAIL)"
exit $overall
