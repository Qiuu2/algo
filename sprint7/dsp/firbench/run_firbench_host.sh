#!/usr/bin/env bash
# run_firbench_host.sh -- desktop (gcc + /usr/bin/python3) checks of the S7 per-channel FIR compute bench. [L2 host]
#   R0  generator --check : fb_coeffs.h / fb_goldens.h regenerate byte-identical (track 1 = numpy) + FG2 report
#   R1  host/fb_ref_host.c : golden track 2 (plain C whole-signal convolution) reproduces all 24 goldens;
#                            every placeholder entry (Dolph-20 x delta, uniform x delta) MISSES (48/48); 0 saturations
#   H1  s7_firbench.c, no FIRA  : core paths PASS 3 tap sets x 2 paths x 8 ch through the bench's OWN frame/history
#                                 code; FIRA paths honestly not built (rc -1, pass_all -99); board negative control MISSES
#   H2  + host FIRA emulator    : all 5 paths PASS, IO1 frame-0 fill check == 1 on the FIRA paths ([L2 emulated
#                                 plumbing]: proves the orchestration matches the ASSUMED Legacy model, not the chip)
#   H3  + emulator STUB mode    : the "accelerator" writes nothing -> every FIRA path FAILS every channel, IO1 == 0 (FG2)
#   H4  + emulator + FIRBENCH_FLUSH_IN + FIRBENCH_P1_FXD_EACH : optional build paths stay green
# Cycle numbers printed on the host are MEANINGLESS (clock()). Exit 0 iff every step meets its expectation.
set -u
HDIR="$(cd "$(dirname "$0")" && pwd)"                      # sprint7/dsp/firbench
ROOT="$(cd "$HDIR/../../.." && pwd)"
OUTDIR="${FB_HOST_OUTDIR:-${TMPDIR:-/tmp}/s7firbench_host_build}"   # binaries stay OUT of the repo
mkdir -p "$OUTDIR"
STUB7="$ROOT/sprint7/dsp/probe/guard_stub_inc"            # Legacy adi_fir.h transcription (prototypes)
STUB5="$ROOT/sprint5/dsp/harness/guard_stub_inc"          # sys/cache.h (no-op flush_data_buffer)
INC=( -I"$ROOT/sprint4/dsp/core_only/bench" -I"$ROOT/sprint4/dsp/fira" -I"$HDIR" )
CFLAGS=( -std=c99 -O2 -Wall -Wextra -Wno-unknown-pragmas )
overall=0

step() { echo; echo "==== [$1] ===="; }
judge() { if [ "$2" -eq 0 ]; then echo "[$1] expectation MET"; else echo "[$1] expectation NOT MET"; overall=1; fi; }

step "R0 generator --check (track 1, numpy)"
/usr/bin/python3 "$HDIR/tools/gen_firbench_tables.py" --check; judge R0 $?

step "R1 fb_ref_host (track 2, C)"
if gcc "${CFLAGS[@]}" "${INC[@]}" "$HDIR/host/fb_ref_host.c" -o "$OUTDIR/fb_ref_host"; then
    "$OUTDIR/fb_ref_host"; judge R1 $?
else echo "[R1] BUILD FAIL"; overall=1; fi

build_run() {   # $1 label, $2 exe, rest = extra args (defines / extra sources)
    local label="$1" exe="$2"; shift 2
    step "$label"
    if gcc "${CFLAGS[@]}" -DFB_HOST_MAIN "$@" "${INC[@]}" "$HDIR/s7_firbench.c" -o "$OUTDIR/$exe"; then
        "$OUTDIR/$exe"; judge "$label" $?
    else echo "[$label] BUILD FAIL"; overall=1; fi
}
build_run "H1 bench, no FIRA (core paths + negative control)" fb_h1
build_run "H2 bench + host FIRA emulator" fb_h2 -DFIRA_USE_REAL_ADI_FIR_HEADER -DFB_HOST_EMU -DFB_EXPECT_EMU \
    -I"$STUB7" -I"$STUB5" "$HDIR/host/fb_fira_emu_host.c"
build_run "H3 bench + emulator STUB (FIRA writes nothing -> must FAIL)" fb_h3 -DFIRA_USE_REAL_ADI_FIR_HEADER \
    -DFB_HOST_EMU -DFB_EMU_STUB -DFB_EXPECT_STUB -I"$STUB7" -I"$STUB5" "$HDIR/host/fb_fira_emu_host.c"
build_run "H4 bench + emulator + FLUSH_IN + P1_FXD_EACH" fb_h4 -DFIRA_USE_REAL_ADI_FIR_HEADER -DFB_HOST_EMU \
    -DFB_EXPECT_EMU -DFIRBENCH_FLUSH_IN -DFIRBENCH_P1_FXD_EACH -I"$STUB7" -I"$STUB5" "$HDIR/host/fb_fira_emu_host.c"

echo; echo "==== host overall: $([ $overall -eq 0 ] && echo PASS || echo FAIL) ===="
exit $overall
