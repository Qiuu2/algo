#!/usr/bin/env bash
# run_guard_check.sh -- desktop syntax check that COVERS the TARGET-guarded region(s) of the harness
#   files (the regions behind #if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && TARGET_SHARC).
#
# WHY (R16): plain `gcc -fsyntax-only` (gate-1) compiles ONLY the desktop path, so guarded blocks are
#   NEVER syntax-checked on host -> the R15 declare-before-use bug (s_h1_fa used before its declaration)
#   slipped through "gcc clean" and only failed in the CCES build. This script defines the guard macros
#   AND points the BSP angle-bracket includes at desktop mocks (guard_stub_inc/), so gcc compiles the
#   guarded code and catches that whole error class (declaration order / symbol use). PROVEN by falsifier
#   (broken decl-after-use version FAILS; fixed version PASSES).
#
# Usage: run_guard_check.sh [file.c ...]   (default: all harness files with a TARGET guard).
# -fsyntax-only ONLY (no link/run): mocks are parse-time stand-ins, not real BSP behavior.
# Run from anywhere. Exit 0 = all checked guarded regions syntactically clean.
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"   # repo root (sprint5/dsp/harness -> up 3)
HDIR="$ROOT/sprint5/dsp/harness"
STUB="$HDIR/guard_stub_inc"
INC=( -I"$STUB"
      -I"$ROOT/sprint4/dsp/core_only/src"
      -I"$ROOT/sprint4/dsp/core_only/include"
      -I"$ROOT/sprint4/dsp/core_only/bench"
      -I"$ROOT/sprint4/dsp/fira" )

# default file set = harness sources that contain a TARGET guard
if [ "$#" -gt 0 ]; then
    FILES=( "$@" )
else
    FILES=( "$HDIR/h1_wcet_measure.c" "$HDIR/h2_dma_isr_measure.c" )
fi

overall=0
for f in "${FILES[@]}"; do
    echo "[guard-check] $(basename "$f"): compiling TARGET-guarded region on desktop (mock BSP)..."
    gcc -fsyntax-only -Wall -Wextra \
        -DFIRA_USE_REAL_ADI_FIR_HEADER -DTARGET_SHARC \
        "${INC[@]}" "$f"
    rc=$?
    if [ $rc -eq 0 ]; then
        echo "[guard-check]   PASS ($(basename "$f"): declaration order + symbol use OK)."
    else
        echo "[guard-check]   FAIL ($(basename "$f"): compile error above, e.g. declare-before-use)."
        overall=1
    fi
done
exit $overall
