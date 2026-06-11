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
#
# WO-S6-M2 EXTENSION (2026-06-08): now syntax-checks BOTH callback datapaths in one run --
#   (A) M1 transparent  (M2_FIRA_INLOOP undefined -> default 0) = the fan-out 1->8 passthrough.
#   (B) M2 FIRA in-loop  (M2_FIRA_INLOOP=1)                      = the 8ch FIRA broadside beam.
#   Build (B) additionally pulls the FROZEN FIRA call surface (fira_tree.h / tree_filterbank.h /
#   fir_coeffs_hb63.h / dolph_w8_q15.h from sprint4) -- read-only headers, CALL-only (zero-touch).
#   The #pragma section("seg_l1_block1") is a SHARC linker directive; gcc emits an "unknown pragma"
#   note (NOT promoted to error here -- it is a real CCES pragma, board-only). Both builds must PASS.
set -u
HDIR="$(cd "$(dirname "$0")" && pwd)"                                   # sprint6/dsp/audio
ROOT="$(cd "$HDIR/../../.." && pwd)"                                    # repo root
STUB="$HDIR/guard_stub_inc"
ADAU="$ROOT/knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/src"  # ADAU_19xxCommon.h (define-only)
# FROZEN FIRA call-surface header dirs (build B only; read-only -- M2 calls, never edits):
FIRA="$ROOT/sprint4/dsp/fira"                                          # fira_tree.h, dolph_w8_q15.h
CORE="$ROOT/sprint4/dsp/core_only/src"                                 # tree_filterbank.h
CINC="$ROOT/sprint4/dsp/core_only/include"                             # fir_coeffs_hb63.h
INC_M1=( -I"$STUB" -I"$HDIR" -I"$ADAU" )
INC_M2=( "${INC_M1[@]}" -I"$FIRA" -I"$CORE" -I"$CINC" )

SRC="$HDIR/m1_loopback_tdm.c"
[ "$#" -gt 0 ] && SRC="$1"

overall=0

run_one() {  # $1=label  $2=extra-define(or empty)  shift2=include array name
    local label="$1"; shift
    local def="$1";   shift
    echo "[guard-check] ${label}: compiling BOARD-guarded region on desktop (mock BSP + frozen FIRA hdrs)..."
    gcc -fsyntax-only -Wall -Wextra \
        -Werror=implicit-function-declaration \
        -Werror=int-conversion -Werror=incompatible-pointer-types \
        -DM1_TARGET_BOARD -DTARGET_SHARC $def \
        "$@" "$SRC"
    local rc=$?
    if [ $rc -eq 0 ]; then
        echo "[guard-check]   PASS (${label}: declaration order + symbol use OK)."
    else
        echo "[guard-check]   FAIL (${label}: compile error above)."
        overall=1
    fi
}

# (A) M1 transparent passthrough (default; M2 path NOT compiled -- board-PASS path preserved)
run_one "M1-transparent (M2_FIRA_INLOOP=0)" "" "${INC_M1[@]}"
# (B) M2 FIRA beam in-loop (the new datapath + the frozen FIRA call surface)
run_one "M2-FIRA-inloop (M2_FIRA_INLOOP=1)" "-DM2_FIRA_INLOOP=1" "${INC_M2[@]}"
# (C) R57 contingency config: M2 + RIGHT-aligned Q-boundary fallback (-DM2_RX_RIGHT_ALIGNED, default-OFF
#     macro, CTO-gated rebuild -- see the Q-BOUNDARY NOTE in m1_loopback_tdm.c). Institutionalized here
#     (same pattern as the WO-S6-M2 extension) so the contingency shift paths (RX<<8 / TX>>8) are proven
#     compile-clean BEFORE they are ever needed on the bench. All three configs must PASS.
run_one "M2-FIRA+RX-right-aligned (M2_RX_RIGHT_ALIGNED)" "-DM2_FIRA_INLOOP=1 -DM2_RX_RIGHT_ALIGNED" "${INC_M2[@]}"

exit $overall
