#!/usr/bin/env bash
# run_guard_check.sh -- desktop syntax check that COVERS the BOARD-guarded region of m1_loopback_tdm.c
#   (the region behind #if defined(M1_TARGET_BOARD) && defined(TARGET_SHARC)).
#
# WHY (R16 lesson, mirrors sprint5): plain `gcc -fsyntax-only` compiles ONLY the desktop path, so the
#   board-guarded block (codec init, SPORT/TWI/SPU/PDMA calls, fan-out, register tables) is NEVER syntax-
#   checked on host. This script defines the guard macros AND points the BSP angle-bracket includes at the
#   desktop parse-stubs (guard_stub_inc/) + the real ADAU register-name headers (define-only), so gcc
#   compiles the guarded code and catches declaration-order / symbol-typo / arg-mismatch errors. The
#   warning-class -Werror promotions (R25/R26 lesson) make symbol-typo + handle-type mistakes hard FAILs.
#   PROVEN by the falsifier (a broken version FAILS; the good version PASSES).
#
# Usage: run_guard_check.sh   (checks m1_loopback_tdm.c). -fsyntax-only ONLY (no link/run).
set -u
HDIR="$(cd "$(dirname "$0")" && pwd)"                                   # sprint6/dsp/audio
ROOT="$(cd "$HDIR/../../.." && pwd)"                                    # repo root
STUB="$HDIR/guard_stub_inc"
ADAU="$ROOT/knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/src"  # ADAU_19xxCommon.h (define-only)
INC=( -I"$STUB" -I"$HDIR" -I"$ADAU" )

FILES=( "$HDIR/m1_loopback_tdm.c" )
[ "$#" -gt 0 ] && FILES=( "$@" )

overall=0
for f in "${FILES[@]}"; do
    echo "[guard-check] $(basename "$f"): compiling BOARD-guarded region on desktop (mock BSP + real ADAU regs)..."
    gcc -fsyntax-only -Wall -Wextra \
        -Werror=implicit-function-declaration \
        -Werror=int-conversion -Werror=incompatible-pointer-types \
        -DM1_TARGET_BOARD -DTARGET_SHARC \
        "${INC[@]}" "$f"
    rc=$?
    if [ $rc -eq 0 ]; then
        echo "[guard-check]   PASS ($(basename "$f"): declaration order + symbol use OK)."
    else
        echo "[guard-check]   FAIL ($(basename "$f"): compile error above)."
        overall=1
    fi
done
exit $overall
