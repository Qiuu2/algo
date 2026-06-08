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

# [WO-S6-M2] frozen FIRA call-surface header dirs -- ONLY for the M2 variant of the loopback module
#   (read-only; M2 calls fira_tree.h, never edits). The other TUs do not use FIRA.
FIRA="$ROOT/sprint4/dsp/fira"; CORE="$ROOT/sprint4/dsp/core_only/src"; CINC="$ROOT/sprint4/dsp/core_only/include"
INC_M2=( "${INC[@]}" -I"$FIRA" -I"$CORE" -I"$CINC" )

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

# [WO-S6-M2] additionally compile the loopback module in the M2 FIRA build (M2_FIRA_INLOOP=1) so the
#   project-wide harness covers BOTH datapaths. Frozen FIRA headers added read-only; both must PASS.
echo "[guard-check] m1_loopback_tdm.c (M2_FIRA_INLOOP=1): FIRA beam datapath..."
gcc -fsyntax-only -Wall -Wextra -Wno-main \
    -Werror=implicit-function-declaration \
    -Werror=int-conversion -Werror=incompatible-pointer-types \
    -DM1_TARGET_BOARD -DTARGET_SHARC -DM2_FIRA_INLOOP=1 \
    "${INC_M2[@]}" "$ADIR/m1_loopback_tdm.c"
rc=$?
if [ $rc -eq 0 ]; then
    echo "[guard-check]   PASS (m1_loopback_tdm.c M2-FIRA)."
else
    echo "[guard-check]   FAIL (m1_loopback_tdm.c M2-FIRA: compile error above)."
    overall=1
fi
exit $overall
