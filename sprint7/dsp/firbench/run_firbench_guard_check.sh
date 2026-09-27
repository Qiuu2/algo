#!/usr/bin/env bash
# run_firbench_guard_check.sh -- desktop guard / syntax checks of the S7 per-channel FIR compute bench.
#   Plain gcc only compiles the desktop path, so the TARGET-guarded regions are parsed with the guard macros defined
#   and the stub headers (R16 lesson; same scheme as sprint7/dsp/probe/run_s7_probe_guard_check.sh).
# Checks (exit 0 = all PASS), all [L2 desktop syntax] -- the real compile gate is the tester's CCES build:
#   (A) s7_firbench.c guarded: -DFIRA_USE_REAL_ADI_FIR_HEADER -DTARGET_SHARC (probe Legacy adi_fir.h transcription +
#       sprint5 sys/cache.h + services/pwr/adi_pwr.h mocks)
#   (B) as (A) + -DFIRBENCH_FLUSH_IN -DFIRBENCH_P1_FXD_EACH (optional build paths)
#   (C) s7_firbench.c desktop path (no guard macros)
#   (D) bench_main_firbench.diff applies to the repo bench_main.c (patch base md5 25090f2c...) standalone AND stacked
#       with sprint7/dsp/probe/bench_main_s7.diff in both orders (identical result); patched copies live in a temp dir
#   (E) the patched bench_main.c (standalone and stacked) parses in the guard configuration
#   (F) ASCII-only on every new .c / .h / .diff in this directory
#   (G) read-only inputs unchanged (md5): chirp_input.h, dolph_w8_q15.h, bench_main.c, fira_tree.c,
#       s7_fir_coeffs_127tap.csv, s7_fir_robust_design.py, s7_common.py, probe bench_main_s7.diff
set -u
HDIR="$(cd "$(dirname "$0")" && pwd)"                      # sprint7/dsp/firbench
ROOT="$(cd "$HDIR/../../.." && pwd)"
STUB7="$ROOT/sprint7/dsp/probe/guard_stub_inc"
STUB5="$ROOT/sprint5/dsp/harness/guard_stub_inc"
STUB6="$ROOT/sprint6/dsp/audio/guard_stub_inc"            # adi_initialize.h for bench_main.c
INC=( -I"$ROOT/sprint4/dsp/core_only/src" -I"$ROOT/sprint4/dsp/core_only/include"
      -I"$ROOT/sprint4/dsp/core_only/bench" -I"$ROOT/sprint4/dsp/fira" -I"$HDIR" )
WERR=( -std=c99 -Wall -Wextra -Wno-unknown-pragmas -Werror=implicit-function-declaration -Werror=int-conversion
       -Werror=incompatible-pointer-types )
GUARD=( -DFIRA_USE_REAL_ADI_FIR_HEADER -DTARGET_SHARC )
TMP="$(mktemp -d "${TMPDIR:-/tmp}/fbguard.XXXXXX")"; trap 'rm -rf "$TMP"' EXIT
overall=0
pass() { echo "[fb-guard]   PASS ($1)"; }
fail() { echo "[fb-guard]   FAIL ($1)"; overall=1; }
run_one() { local label="$1"; shift; echo "[fb-guard] $label"; if gcc -fsyntax-only "$@"; then pass "$label"; else fail "$label"; fi; }

run_one "(A) s7_firbench.c guarded" "${WERR[@]}" "${GUARD[@]}" -I"$STUB7" -I"$STUB5" "${INC[@]}" "$HDIR/s7_firbench.c"
run_one "(B) s7_firbench.c guarded + FLUSH_IN + P1_FXD_EACH" "${WERR[@]}" "${GUARD[@]}" -DFIRBENCH_FLUSH_IN \
        -DFIRBENCH_P1_FXD_EACH -I"$STUB7" -I"$STUB5" "${INC[@]}" "$HDIR/s7_firbench.c"
run_one "(C) s7_firbench.c desktop path" "${WERR[@]}" "${INC[@]}" "$HDIR/s7_firbench.c"

echo "[fb-guard] (D) patch application"
mk() { mkdir -p "$TMP/$1/sprint4/dsp/core_only/bench"; cp "$ROOT/sprint4/dsp/core_only/bench/bench_main.c" "$TMP/$1/sprint4/dsp/core_only/bench/"; }
ap() { (cd "$TMP/$1" && patch -p1 --no-backup-if-mismatch -s < "$2"); }
mk solo; mk pf; mk fp; dok=1
ap solo "$HDIR/bench_main_firbench.diff" || dok=0
{ ap pf "$ROOT/sprint7/dsp/probe/bench_main_s7.diff" && ap pf "$HDIR/bench_main_firbench.diff"; } || dok=0
{ ap fp "$HDIR/bench_main_firbench.diff" && ap fp "$ROOT/sprint7/dsp/probe/bench_main_s7.diff"; } || dok=0
cmp -s "$TMP/pf/sprint4/dsp/core_only/bench/bench_main.c" "$TMP/fp/sprint4/dsp/core_only/bench/bench_main.c" || dok=0
if [ $dok -eq 1 ]; then pass "(D) standalone + stacked both orders, identical"; else fail "(D)"; fi

run_one "(E1) patched bench_main.c (standalone) guarded" "${WERR[@]}" -Wno-main "${GUARD[@]}" -I"$STUB7" -I"$STUB6" \
        -I"$STUB5" "${INC[@]}" -I"$ROOT/sprint7/dsp/probe" "$TMP/solo/sprint4/dsp/core_only/bench/bench_main.c"
run_one "(E2) patched bench_main.c (probe + firbench) guarded" "${WERR[@]}" -Wno-main "${GUARD[@]}" -I"$STUB7" -I"$STUB6" \
        -I"$STUB5" "${INC[@]}" -I"$ROOT/sprint7/dsp/probe" "$TMP/pf/sprint4/dsp/core_only/bench/bench_main.c"

echo "[fb-guard] (F) ASCII-only"
na=0
for f in "$HDIR"/*.c "$HDIR"/*.h "$HDIR"/host/*.c "$HDIR"/*.diff; do
    if LC_ALL=C grep -nP '[^\x00-\x7F]' "$f" >/dev/null; then echo "[fb-guard]   non-ASCII in ${f#$ROOT/}"; na=1; fi
done
if [ $na -eq 0 ]; then pass "(F)"; else fail "(F)"; fi

echo "[fb-guard] (G) read-only inputs unchanged"
gok=1
chk() { local cur; cur="$(md5sum "$ROOT/$1" | awk '{print $1}')"; if [ "$cur" != "$2" ]; then echo "[fb-guard]   md5 drift $1: $cur != $2"; gok=0; fi; }
chk sprint4/dsp/core_only/bench/chirp_input.h      f38270f3b963265129bdf45c34ad2b6f
chk sprint4/dsp/fira/dolph_w8_q15.h                 ef2b75235a15b69b63b445ecffd8cf7f
chk sprint4/dsp/core_only/bench/bench_main.c        25090f2c29d6729443bef5ed1feb5d31
chk sprint4/dsp/fira/fira_tree.c                    7616c41102946c357e9c70fafcd51da3
chk sprint7/sim/side30/fir/s7_fir_coeffs_127tap.csv 93792b2473b01eb959afb50d0b644e19
chk sprint7/sim/side30/fir/s7_fir_robust_design.py  e2938a9eb0e8872e23fe493fc759d119
chk sprint7/sim/acoustic/s7_common.py               f68a834fd08ba184fc8aad6aeed7e24e
chk sprint7/dsp/probe/bench_main_s7.diff            0b1e7252f0b20344aa65a8a08ef87ef8
if [ $gok -eq 1 ]; then pass "(G)"; else fail "(G) -> regenerate tables / re-derive the patch before use"; fi

echo "[fb-guard] overall: $([ $overall -eq 0 ] && echo PASS || echo FAIL)"
exit $overall
