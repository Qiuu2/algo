#!/usr/bin/env bash
# run_s7_preproc_equiv.sh -- WO-S7-B6 DEFAULT-BYTE-EQUIVALENCE PROOF for the M2 TU change package
#   (DEC-S7-RULINGS-01 D3 / DEC-S7-IMPL-01 item 2). Compares `gcc -E -P` of the HEAD version of
#   m1_loopback_tdm.{c,h} against the working-tree version, for the two DEFAULT macro sets:
#     M1  = -DM1_TARGET_BOARD -DTARGET_SHARC
#     M2  = -DM1_TARGET_BOARD -DTARGET_SHARC -DM2_FIRA_INLOOP=1
#   plus the three pre-existing optional single-macro sets (RX_RIGHT_ALIGNED / CHMAP_FIX / STATIC_TXTEST)
#   for information. The ALLOWED residual diff (CTO ruling) is ONLY:
#     - the 6 build-fingerprint globals (both sets)
#     - g_m2_beam_cyc_min + its reset/update statements (M2 set only)
#   Anything else printed by the diff must be explained or removed. Uses the same desktop parse-stubs as
#   sprint6/dsp/audio/run_guard_check.sh so the board-guarded region is what gets preprocessed.
#   Exit 0 iff every set's diff consists only of the allowed lines (checked by an allow-list grep).
set -u
HDIR="$(cd "$(dirname "$0")" && pwd)"                 # sprint7/dsp/host
ROOT="$(cd "$HDIR/../../.." && pwd)"                  # repo root
AUD="$ROOT/sprint6/dsp/audio"
SRC="$AUD/m1_cces_project/src"
STUB="$AUD/guard_stub_inc"
ADAU="$ROOT/knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/src"
# NOTE: -I"$SRC" is needed for the two static-TX table headers (m2_static_txtest*_table.h) in the STATIC_TXTEST
#   sets; it does NOT leak the new m1_loopback_tdm.h into the HEAD copy because a quoted #include is resolved
#   in the including file's own directory ($TMP/ref) FIRST. gcc -E must succeed (rc=0) or the set is INVALID.
INC=( -I"$STUB" -I"$SRC" -I"$ADAU" -I"$ROOT/sprint4/dsp/fira" -I"$ROOT/sprint4/dsp/core_only/src" \
      -I"$ROOT/sprint4/dsp/core_only/include" -I"$ROOT/sprint4/dsp/core_only/bench" )
REF="${S7_REF:-HEAD}"                                 # git rev to compare against (default HEAD)
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/ref" "$TMP/new"
( cd "$ROOT" && git show "$REF:sprint6/dsp/audio/m1_cces_project/src/m1_loopback_tdm.c" > "$TMP/ref/m1_loopback_tdm.c" \
             && git show "$REF:sprint6/dsp/audio/m1_cces_project/src/m1_loopback_tdm.h" > "$TMP/ref/m1_loopback_tdm.h" ) || { echo "git show failed"; exit 2; }
cp "$SRC/m1_loopback_tdm.c" "$SRC/m1_loopback_tdm.h" "$TMP/new/"

# allow-list: every diff line (after the +/- marker) must match one of these
ALLOW='^[-+]volatile int g_m2_(rx_right_aligned|chmap_fix|static_txtest|stxt_localize|selftest)_built = [01];$'
ALLOW="$ALLOW"'|^[-+]volatile int g_m1_u6_addr_override_built = [01];$'
ALLOW="$ALLOW"'|^[-+]extern volatile int g_m2_(rx_right_aligned|chmap_fix|static_txtest|stxt_localize|selftest)_built;$'
ALLOW="$ALLOW"'|^[-+]extern volatile int g_m1_u6_addr_override_built;$'
ALLOW="$ALLOW"'|^[-+]volatile uint32_t g_m2_beam_cyc_min = 0xFFFFFFFFu;$'
ALLOW="$ALLOW"'|^[-+]extern volatile uint32_t g_m2_beam_cyc_min;$'
ALLOW="$ALLOW"'|^[-+] *g_m2_beam_cyc_min = 0xFFFFFFFFu;$'
ALLOW="$ALLOW"'|^[-+] *g_m2_beam_cyc_min = 0u;$'
ALLOW="$ALLOW"'|^[-+] *if \(g_m2_beam_cyc_last < g_m2_beam_cyc_min\) g_m2_beam_cyc_min = g_m2_beam_cyc_last;$'

overall=0
run_set() {   # $1=label $2=defines
    local label="$1" defs="$2" rc
    if ! gcc -E -P -DM1_TARGET_BOARD -DTARGET_SHARC $defs "${INC[@]}" "$TMP/ref/m1_loopback_tdm.c" > "$TMP/ref.raw" 2> "$TMP/ref.err"; then
        echo "=== [$label] INVALID: gcc -E failed on the $REF copy:"; head -3 "$TMP/ref.err"; overall=1; return; fi
    if ! gcc -E -P -DM1_TARGET_BOARD -DTARGET_SHARC $defs "${INC[@]}" "$TMP/new/m1_loopback_tdm.c" > "$TMP/new.raw" 2> "$TMP/new.err"; then
        echo "=== [$label] INVALID: gcc -E failed on the working-tree copy:"; head -3 "$TMP/new.err"; overall=1; return; fi
    sed 's/[[:space:]]\+/ /g; s/^ //; s/ $//' "$TMP/ref.raw" | grep -v '^$' > "$TMP/ref.i"
    sed 's/[[:space:]]\+/ /g; s/^ //; s/ $//' "$TMP/new.raw" | grep -v '^$' > "$TMP/new.i"
    diff "$TMP/ref.i" "$TMP/new.i" | grep '^[<>]' | sed 's/^< /-/; s/^> /+/' > "$TMP/d.txt"
    local n=$(wc -l < "$TMP/d.txt") bad
    bad=$(grep -vE "$ALLOW" "$TMP/d.txt" || true)
    echo "=== [$label] defines: $defs  -> preprocessed diff lines: $n (ref $(wc -l < "$TMP/ref.i") / new $(wc -l < "$TMP/new.i") lines)"
    sed 's/^/    /' "$TMP/d.txt"
    if [ -n "$bad" ]; then echo "    !! NOT ALLOWED:"; echo "$bad" | sed 's/^/    !! /'; overall=1; else echo "    verdict: every diff line is on the allow-list -> PASS"; fi
}
run_set "M1 default"                 ""
run_set "M2 default"                 "-DM2_FIRA_INLOOP=1"
run_set "M2 + RX_RIGHT_ALIGNED"      "-DM2_FIRA_INLOOP=1 -DM2_RX_RIGHT_ALIGNED"
run_set "M2 + CHMAP_FIX"             "-DM2_FIRA_INLOOP=1 -DM2_CHMAP_FIX"
run_set "M2 + STATIC_TXTEST"         "-DM2_FIRA_INLOOP=1 -DM2_STATIC_TXTEST=1"
run_set "M2 + STATIC_TXTEST+LOCALIZE" "-DM2_FIRA_INLOOP=1 -DM2_STATIC_TXTEST=1 -DM2_STXT_LOCALIZE=1"
echo "=== m1_main.c: $(cd "$ROOT" && git diff --stat "$REF" -- sprint6/dsp/audio/m1_cces_project/src/m1_main.c | wc -l) diff lines vs $REF (0 = untouched)"
if [ $overall -eq 0 ]; then echo "=== OVERALL: PASS (residual diff == 6 fingerprints + g_m2_beam_cyc_min only)"; else echo "=== OVERALL: FAIL (unexplained diff present)"; fi
exit $overall
