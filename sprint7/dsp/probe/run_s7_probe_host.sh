#!/usr/bin/env bash
# run_s7_probe_host.sh -- desktop (gcc) build + run of the WO-S7-B6.3 bench probe. [L2 host plumbing]
#   No FIRA on this host: fira_tree.c's desktop path returns -1 from fira_tree_setup() and its fira_tfb_*
#   placeholders memset the FIRA segments to 0 (fira_tree.c:711-719, 754-768). Therefore:
#     H1  probe + frozen fira_tree.c, no force        -> FG-D: setup gate stops the probe, valid=0, fg_pass_all=0
#     H2  probe + frozen fira_tree.c + HOST_FORCE     -> FG-C: placeholder chain runs, ALL 8 anchors FAIL (expected,
#                                                        honest negative control) ; FG-B core positive control 8/8 PASS
#     H3  probe + diagnostic COPY (fira_tree_probe.c) + HOST_FORCE + S7_PROBE_INNER
#                                                     -> same verdicts as H2 (copy == frozen on the desktop path),
#                                                        inner_valid=1 with all-zero inner counters (inner brackets are
#                                                        TARGET-only) -- proves the copy links in place of the frozen file
#     H4  probe + frozen fira_tree.c + HOST_FORCE + S7_PROBE_SYN_FG
#                                                     -> FG-E compiled in; syn_fg_all == -2 (not evaluated: FG-A failed on host;
#                                                        placeholder subbands make both synths agree trivially -> never a host PASS)
#   Cycle numbers printed by these runs are MEANINGLESS (host clock()); only the FG verdicts matter.
#   Exit 0 iff every run meets its host expectation (each binary returns 0 when its expectation is met).
set -u
HDIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HDIR/../../.." && pwd)"
OUTDIR="${S7_HOST_OUTDIR:-${TMPDIR:-/tmp}/s7probe_host_build}"   # keep binaries OUT of the repo
mkdir -p "$OUTDIR"
INC=( -I"$ROOT/sprint4/dsp/core_only/src" -I"$ROOT/sprint4/dsp/core_only/include"
      -I"$ROOT/sprint4/dsp/core_only/bench" -I"$ROOT/sprint4/dsp/fira" -I"$HDIR" )
COMMON=( "$ROOT/sprint4/dsp/core_only/bench/bench_harness.c"
         "$ROOT/sprint4/dsp/core_only/src/tree_filterbank.c"
         "$ROOT/sprint4/dsp/core_only/src/tfb_8ch.c" )
CFLAGS=( -std=c99 -O2 -Wall -Wextra -Wno-unknown-pragmas -DS7_HOST_MAIN )
overall=0

build_run() {   # $1=label $2=exe $3=fira-source ; rest = extra defines
    local label="$1" exe="$2" fira="$3"; shift 3
    echo "==== [$label] build ===="
    if ! gcc "${CFLAGS[@]}" "$@" "${INC[@]}" "$HDIR/s7_wallclock_probe.c" "$fira" "${COMMON[@]}" -o "$OUTDIR/$exe"; then
        echo "[$label] BUILD FAIL"; overall=1; return
    fi
    echo "==== [$label] run ===="
    if "$OUTDIR/$exe"; then echo "[$label] host expectation MET"; else echo "[$label] host expectation NOT MET"; overall=1; fi
}

# H1: no force -> the desktop setup gate must stop the probe honestly (valid 0, fg 0, nothing ran)
build_run "H1 frozen, no-force (FG-D)" s7probe_h1 "$ROOT/sprint4/dsp/fira/fira_tree.c"
# H2: force -> placeholder chain, all anchors FAIL (FG-C), core positive control PASS (FG-B)
build_run "H2 frozen + HOST_FORCE (FG-C/FG-B)" s7probe_h2 "$ROOT/sprint4/dsp/fira/fira_tree.c" -DS7_PROBE_HOST_FORCE
# H3: the diagnostic copy in place of the frozen file (+ inner flag) -> identical desktop verdicts
build_run "H3 COPY + HOST_FORCE + S7_PROBE_INNER" s7probe_h3 "$HDIR/fira_tree_probe.c" -DS7_PROBE_HOST_FORCE -DS7_PROBE_INNER
# H4: FG-E syn-side control compiled in; on the desktop FG-A fails, so syn_fg_all must report -2 (not evaluated), never PASS
build_run "H4 frozen + HOST_FORCE + S7_PROBE_SYN_FG (FG-E gating)" s7probe_h4 "$ROOT/sprint4/dsp/fira/fira_tree.c" -DS7_PROBE_HOST_FORCE -DS7_PROBE_SYN_FG

echo "==== host overall: $([ $overall -eq 0 ] && echo PASS || echo FAIL) ===="
exit $overall
