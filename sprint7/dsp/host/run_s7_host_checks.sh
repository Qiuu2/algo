#!/usr/bin/env bash
# run_s7_host_checks.sh -- WO-S7-B6 host checks for the M2_SELFTEST kernel (DEC-S7-IMPL-01 item 2).
#   1. builds s7_selftest_host.c against the FROZEN core (sprint4/dsp/core_only/src/tree_filterbank.c, read-only)
#      with -O2 and runs all modes (pos + 5 negative controls) -> exit code = 0 iff every mode meets its expectation;
#   2. rebuilds at -O0 with UBSan and re-runs `pos`; the 8 CRC lines must be IDENTICAL to the -O2 run
#      (integer arithmetic is optimization-level independent given no UB -- the premise behind the B6.3
#      Release/-O contrast build, S7_DSP_ASSESSMENT 6.3 hypothesis b; [L2 host gcc], not a cc21k proof).
#   Usage: run_s7_host_checks.sh          (from anywhere; paths resolved relative to this script)
set -u
HDIR="$(cd "$(dirname "$0")" && pwd)"                   # sprint7/dsp/host
ROOT="$(cd "$HDIR/../../.." && pwd)"                    # repo root
CORE="$ROOT/sprint4/dsp/core_only/src"
BENCH="$ROOT/sprint4/dsp/core_only/bench"
CINC="$ROOT/sprint4/dsp/core_only/include"
FIRA="$ROOT/sprint4/dsp/fira"
OUT="${S7_OUT:-$(mktemp -d)}"
INC=( -I"$CORE" -I"$BENCH" -I"$CINC" -I"$FIRA" )
overall=0

echo "[s7-host] gcc: $(gcc --version | head -1)"
echo "[s7-host] frozen core md5: $(md5sum "$CORE/tree_filterbank.c" | cut -c1-32)  chirp: $(md5sum "$BENCH/chirp_input.h" | cut -c1-32)  goldens: $(md5sum "$FIRA/dolph_f5_goldens.h" | cut -c1-32)"

echo "[s7-host] build -O2 ..."
gcc -std=c99 -O2 -Wall -Wextra "${INC[@]}" "$HDIR/s7_selftest_host.c" "$CORE/tree_filterbank.c" -o "$OUT/s7_selftest_host_O2" || { echo "[s7-host] BUILD FAIL"; exit 2; }
echo "[s7-host] run all modes (-O2):"
"$OUT/s7_selftest_host_O2" all | tee "$OUT/run_O2.txt"; rc=${PIPESTATUS[0]}
[ $rc -eq 0 ] || overall=1

echo "[s7-host] build -O0 -fsanitize=undefined ..."
if gcc -std=c99 -O0 -g -fsanitize=undefined -fno-sanitize-recover=all -Wall -Wextra "${INC[@]}" "$HDIR/s7_selftest_host.c" "$CORE/tree_filterbank.c" -o "$OUT/s7_selftest_host_O0ub" 2>"$OUT/build_O0.err"; then
    "$OUT/s7_selftest_host_O0ub" pos > "$OUT/run_O0.txt" 2>&1; rc0=$?
    grep -E '^  [0-7]  ' "$OUT/run_O2.txt" | head -8 > "$OUT/crc_O2.txt"
    grep -E '^  [0-7]  ' "$OUT/run_O0.txt" | head -8 > "$OUT/crc_O0.txt"
    if [ $rc0 -eq 0 ] && cmp -s "$OUT/crc_O2.txt" "$OUT/crc_O0.txt"; then
        echo "[s7-host] -O0+UBSan pos run: rc=0, no UB reported, 8 CRC lines IDENTICAL to -O2 -> optimization-invariance PASS [L2 host]"
    else
        echo "[s7-host] -O0+UBSan pos run: rc=$rc0 or CRC lines differ -> FAIL"; diff "$OUT/crc_O2.txt" "$OUT/crc_O0.txt"; tail -5 "$OUT/run_O0.txt"; overall=1
    fi
else
    echo "[s7-host] (UBSan build unavailable on this host: $(head -1 "$OUT/build_O0.err")) -- optimization-invariance check SKIPPED (not a FAIL)"
fi
[ $overall -eq 0 ] && echo "[s7-host] OVERALL PASS" || echo "[s7-host] OVERALL FAIL"
exit $overall
