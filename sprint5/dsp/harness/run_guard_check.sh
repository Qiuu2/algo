#!/usr/bin/env bash
# run_guard_check.sh -- R16 desktop syntax check that COVERS the TARGET-guarded region of
#   h1_wcet_measure.c (the region behind #if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && TARGET_SHARC).
#
# WHY: plain `gcc -fsyntax-only` (gate-1 / critic R15) compiled ONLY the desktop path, so the guarded
#   block was NEVER syntax-checked on host -> the R15 declare-before-use bug (s_h1_fa used before its
#   declaration) slipped through "gcc clean" and only failed in the CCES build. This script defines the
#   guard macros AND points the BSP angle-bracket includes at desktop mocks (guard_stub_inc/), so gcc
#   compiles the guarded code and catches that whole error class (declaration order / symbol use).
#   PROVEN: it fails on the broken (decl-after-use) version and passes on the fixed one (falsifier).
#
# This is -fsyntax-only ONLY (no link/run): the mocks are parse-time stand-ins, not real BSP behavior.
# Run from the repo root.  Exit 0 = guarded region syntactically clean.
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"   # repo root (sprint5/dsp/harness -> up 3)
HARNESS="$ROOT/sprint5/dsp/harness/h1_wcet_measure.c"
STUB="$ROOT/sprint5/dsp/harness/guard_stub_inc"
INC=( -I"$STUB"
      -I"$ROOT/sprint4/dsp/core_only/src"
      -I"$ROOT/sprint4/dsp/core_only/include"
      -I"$ROOT/sprint4/dsp/core_only/bench"
      -I"$ROOT/sprint4/dsp/fira" )

echo "[guard-check] compiling TARGET-guarded region of h1_wcet_measure.c on desktop (mock BSP)..."
gcc -fsyntax-only -Wall -Wextra \
    -DFIRA_USE_REAL_ADI_FIR_HEADER -DTARGET_SHARC \
    "${INC[@]}" "$HARNESS"
rc=$?
if [ $rc -eq 0 ]; then
    echo "[guard-check] PASS: guarded region compiles clean (declaration order + symbol use OK)."
else
    echo "[guard-check] FAIL: guarded region has a compile error above (e.g. declare-before-use)."
fi
exit $rc
