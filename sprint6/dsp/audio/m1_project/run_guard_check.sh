#!/usr/bin/env bash
# run_guard_check.sh -- desktop syntax check covering the BOARD-guarded regions of ALL M1-project TUs
#   (m1_main.c / m1_sru.c / m1_softconfig.c / m1_cyc.c + the m1_loopback_tdm.c module).
#
# WHY (R16/R25 lesson): plain gcc compiles only the desktop path; the board-guarded blocks (SRU routing,
#   SoftConfig U6 writes, codec init, SPORT/TWI/SPU/PDMA, fan-out) are NEVER syntax-checked on host. This
#   defines the guard macros AND points the BSP angle-bracket includes at desktop parse-stubs (guard_stub_inc/)
#   + the real ADAU register-name headers (define-only), so gcc compiles the guarded code and catches
#   declaration-order / symbol-typo / arg-mismatch / handle-type errors. -Werror promotions make symbol-typo +
#   pointer/handle-type mistakes hard FAILs. Proven by the falsifier (broken FAILS / good PASSES).
#
# -fsyntax-only ONLY (mocks are parse-time stand-ins). The SRU stub cannot validate ROUTE legality
#   (board-confirm); it only proves the routing TU parses + token names are correct.
set -u
PDIR="$(cd "$(dirname "$0")" && pwd)"                                   # m1_project
ADIR="$(cd "$PDIR/.." && pwd)"                                          # sprint6/dsp/audio
ROOT="$(cd "$ADIR/../../.." && pwd)"                                    # repo root
STUB="$ADIR/guard_stub_inc"
ADAU="$ROOT/knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/src"  # ADAU_19xxCommon.h
INC=( -I"$STUB" -I"$ADIR" -I"$PDIR/src" -I"$ADAU" )

FILES=( "$PDIR/src/m1_main.c" "$PDIR/src/m1_sru.c" "$PDIR/src/m1_softconfig.c"
        "$PDIR/src/m1_cyc.c" "$ADIR/m1_loopback_tdm.c" )
[ "$#" -gt 0 ] && FILES=( "$@" )

overall=0
for f in "${FILES[@]}"; do
    echo "[guard-check] $(basename "$f"): compiling BOARD-guarded region on desktop (mock BSP)..."
    gcc -fsyntax-only -Wall -Wextra -Wno-main \
        -Werror=implicit-function-declaration \
        -Werror=int-conversion -Werror=incompatible-pointer-types \
        -DM1_TARGET_BOARD -DTARGET_SHARC \
        "${INC[@]}" "$f"
    rc=$?
    if [ $rc -eq 0 ]; then
        echo "[guard-check]   PASS ($(basename "$f"))."
    else
        echo "[guard-check]   FAIL ($(basename "$f"): compile error above)."
        overall=1
    fi
done
exit $overall
