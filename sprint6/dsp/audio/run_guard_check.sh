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
# Usage: run_guard_check.sh [file.c]   (default = m1_cces_project/src/m1_loopback_tdm.c). -fsyntax-only ONLY (no link/run).
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
BENCH="$ROOT/sprint4/dsp/core_only/bench"                              # chirp_input.h (WO-S7-B6 M2_SELFTEST; frozen, read-only)
CCES_SRC="$HDIR/m1_cces_project/src"                                  # AUTHORITATIVE M1/M2 sources (2026-09-02)
INC_M1=( -I"$STUB" -I"$CCES_SRC" -I"$ADAU" )
INC_M2=( "${INC_M1[@]}" -I"$FIRA" -I"$CORE" -I"$CINC" -I"$BENCH" )

# DEFAULT TARGET = the authoritative CCES-project copy (2026-09-02 housekeeping). The loose copy
#   sprint6/dsp/audio/m1_loopback_tdm.c is a DEPRECATED 2026-06-12 snapshot (81 lines behind) -- do not check it.
SRC="$CCES_SRC/m1_loopback_tdm.c"
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
# (D)(E)(F) 2026-09-02 housekeeping: the three diagnostic build gates added in July (chmap fix / static TX test /
#     375Hz polarity localize) were NOT in this matrix, so their guarded code was never desktop-checked by the
#     default run. Same institutionalization as (C): prove them compile-clean before they are needed on the bench.
#     All six configs must PASS. (Config E prints one -Wsign-compare warning at the static-fill loop; not promoted.)
run_one "M2-FIRA+chmap-fix (M2_CHMAP_FIX)" "-DM2_FIRA_INLOOP=1 -DM2_CHMAP_FIX" "${INC_M2[@]}"
run_one "M2-FIRA+static-txtest (M2_STATIC_TXTEST=1)" "-DM2_FIRA_INLOOP=1 -DM2_STATIC_TXTEST=1" "${INC_M2[@]}"
run_one "M2-FIRA+static-txtest+localize (M2_STXT_LOCALIZE=1)" "-DM2_FIRA_INLOOP=1 -DM2_STATIC_TXTEST=1 -DM2_STXT_LOCALIZE=1" "${INC_M2[@]}"

# (G)(H)(I) WO-S7-B6 (DEC-S7-RULINGS-01 D3 / DEC-S7-IMPL-01 item 2, 2026-09-02): the eight-anchor init self-test
#     (M2_SELFTEST, pulls the frozen 256 KB chirp_input.h from $BENCH + dolph_f5_goldens.h), the three-segment
#     CCNT brackets (M2_SEG_CYC) and the unity-weight negative-control build (M2_SELFTEST_NEGCTRL). Same
#     institutionalization as C..F: compile-clean on desktop BEFORE the tester's CCES build. All must PASS.
run_one "M2-FIRA+selftest (M2_SELFTEST=1)" "-DM2_FIRA_INLOOP=1 -DM2_SELFTEST=1" "${INC_M2[@]}"
run_one "M2-FIRA+selftest+seg-cyc (M2_SEG_CYC=1)" "-DM2_FIRA_INLOOP=1 -DM2_SELFTEST=1 -DM2_SEG_CYC=1" "${INC_M2[@]}"
run_one "M2-FIRA+selftest+negctrl (M2_SELFTEST_NEGCTRL=1)" "-DM2_FIRA_INLOOP=1 -DM2_SELFTEST=1 -DM2_SELFTEST_NEGCTRL=1" "${INC_M2[@]}"
# (J) all diagnostics together with chmap: proves the self-test's "no chmap" weight path coexists with M2_CHMAP_FIX.
run_one "M2-FIRA+chmap+selftest+seg-cyc (all)" "-DM2_FIRA_INLOOP=1 -DM2_CHMAP_FIX -DM2_SELFTEST=1 -DM2_SEG_CYC=1" "${INC_M2[@]}"
# S7-SIDE30 (DEC-S7-SIDE30-01, 2026-09-26): runtime weight-table select M2_WTBL_SEL (#ifdef-style)
run_one "M2-FIRA+wtbl-sel (M2_WTBL_SEL)" "-DM2_FIRA_INLOOP=1 -DM2_WTBL_SEL" "${INC_M2[@]}"
run_one "M2-FIRA+wtbl-sel+chmap (M2_WTBL_SEL+M2_CHMAP_FIX)" "-DM2_FIRA_INLOOP=1 -DM2_WTBL_SEL -DM2_CHMAP_FIX" "${INC_M2[@]}"
run_one "M2-FIRA+wtbl+chmap+selftest+seg-cyc (all)" "-DM2_FIRA_INLOOP=1 -DM2_WTBL_SEL -DM2_CHMAP_FIX -DM2_SELFTEST=1 -DM2_SEG_CYC=1" "${INC_M2[@]}"

# ---- FALSIFIERS (X1..X5): macro combinations that MUST FAIL to compile via the WO-S7-B6 #error guards
#     (fw audit 9.C: -DM2_STATIC_TXTEST=1 alone used to compile clean and silently broke the static-TX premise).
#     Verdict rule: compile FAILURE whose diagnostic contains "#error" = PASS; a clean compile = FAIL (guard
#     missing); a failure WITHOUT "#error" in the output = FAIL too (an unrelated error must not masquerade
#     as the guard). Includes = the full M2 set so the ONLY possible reason to fail is the guard.
run_must_fail() {  # $1=label  $2=defines  shift2=include array
    local label="$1"; shift
    local def="$1";   shift
    local out rc
    echo "[guard-check] ${label}: EXPECT compile FAIL via #error guard..."
    out=$(gcc -fsyntax-only -Wall -Wextra \
        -Werror=implicit-function-declaration \
        -Werror=int-conversion -Werror=incompatible-pointer-types \
        -DM1_TARGET_BOARD -DTARGET_SHARC $def \
        "$@" "$SRC" 2>&1)
    rc=$?
    if [ $rc -ne 0 ] && printf '%s' "$out" | grep -q '#error'; then
        echo "[guard-check]   PASS (${label}: build refused by #error guard as intended):"
        printf '%s\n' "$out" | grep '#error' | head -2 | sed 's/^/[guard-check]     /'
    elif [ $rc -eq 0 ]; then
        echo "[guard-check]   FAIL (${label}: compiled CLEAN -- the #error guard is missing)."
        overall=1
    else
        echo "[guard-check]   FAIL (${label}: failed for a reason OTHER than the #error guard):"
        printf '%s\n' "$out" | head -5 | sed 's/^/[guard-check]     /'
        overall=1
    fi
}
run_must_fail "X1 M2_STATIC_TXTEST=1 alone (no INLOOP)"        "-DM2_STATIC_TXTEST=1"                          "${INC_M2[@]}"
run_must_fail "X2 M2_SELFTEST=1 alone (no INLOOP)"             "-DM2_SELFTEST=1"                               "${INC_M2[@]}"
run_must_fail "X3 M2_STXT_LOCALIZE=1 without STATIC_TXTEST"    "-DM2_FIRA_INLOOP=1 -DM2_STXT_LOCALIZE=1"       "${INC_M2[@]}"
run_must_fail "X4 M2_SELFTEST_NEGCTRL=1 without SELFTEST"      "-DM2_FIRA_INLOOP=1 -DM2_SELFTEST_NEGCTRL=1"    "${INC_M2[@]}"
run_must_fail "X5 M2_SEG_CYC=1 alone (no INLOOP)"              "-DM2_SEG_CYC=1"                                "${INC_M2[@]}"
run_must_fail "X6 M2_WTBL_SEL alone (no INLOOP)"               "-DM2_WTBL_SEL"                                 "${INC_M2[@]}"
run_must_fail "X7 M2_WTBL_SEL with M2_STATIC_TXTEST=1"         "-DM2_FIRA_INLOOP=1 -DM2_WTBL_SEL -DM2_STATIC_TXTEST=1" "${INC_M2[@]}"

if [ $overall -eq 0 ]; then echo "[guard-check] OVERALL PASS (13 compile configs + 7 falsifiers)."; else echo "[guard-check] OVERALL FAIL."; fi
exit $overall
