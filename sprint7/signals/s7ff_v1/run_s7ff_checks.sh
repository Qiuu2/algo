#!/usr/bin/env bash
# run_s7ff_checks.sh -- one-key gate for the s7ff_v1 far-field signal package.
# Exit 0 only if EVERY step passes. Each step's own exit code is checked (no pipes swallow it).
#
#   1 determinism : regenerate all 61 files into a temp dir; byte-compare with wav/ (cmp) + manifest
#   2 md5         : md5sum -c wav/MANIFEST.md5
#   3 checker     : s7ff_check.py wav  (independent of the generator; writes s7ff_check.log + CSVs)
#   4 ffprobe     : third tool reads every header: pcm_s24le, 48000 Hz, 1 ch, 24 bit, 1,728,000 samples
#   5 falsifiers  : s7ff_falsifiers.py -- 23 broken inputs must each FAIL as targeted, control must PASS
#   6 gate self-test: steps 2-4 run on a copy with ONE flipped byte must FAIL (proves this script can fail)
#
# Usage: ./run_s7ff_checks.sh        (from anywhere; works on the package directory of this script)
set -u
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
TMP=$(mktemp -d /tmp/s7ff_gate_XXXXXX)
trap 'rm -rf "$TMP"' EXIT
overall=0
report() { if [ "$2" -eq 0 ]; then echo "[PASS] $1"; else echo "[FAIL] $1 (exit $2)"; overall=1; fi; }

core_checks() {   # $1 = wav dir, $2 = output dir for logs/CSVs; returns non-zero if any core step fails
  local d="$1" out="$2" rc=0 r
  ( cd "$d" && md5sum --quiet -c MANIFEST.md5 ) > "$TMP/md5.log" 2>&1; r=$?
  report "2 md5sum -c MANIFEST.md5 ($d)" $r; [ $r -eq 0 ] || { rc=1; sed 's/^/  /' "$TMP/md5.log"; }
  "$PY" s7ff_check.py "$d" --metrics "$out/S7FF_V1_METRICS.csv" --spectra "$out/S7FF_V1_SPECTRA.csv" > "$out/s7ff_check.log" 2>&1; r=$?
  report "3 s7ff_check.py ($d): $(tail -1 "$out/s7ff_check.log")" $r; [ $r -eq 0 ] || rc=1
  local bad=0 n=0 f got
  for f in "$d"/*.wav; do
    n=$((n+1))
    got=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,bits_per_sample,duration_ts -of csv=p=0 "$f" 2>&1)
    if [ "$got" != "pcm_s24le,48000,1,24,1728000" ]; then echo "  ffprobe $f -> $got"; bad=$((bad+1)); fi
  done
  [ "$n" -eq 61 ] || { echo "  ffprobe saw $n wav files, want 61"; bad=$((bad+1)); }
  report "4 ffprobe headers: $n files, $bad mismatches" $bad; [ $bad -eq 0 ] || rc=1
  return $rc
}

echo "== s7ff_v1 gate | $(date -Iseconds) | $($PY -c 'import numpy,platform;print("python",platform.python_version(),"numpy",numpy.__version__)')"

# 1 determinism
"$PY" gen_s7ff_signals.py --outdir "$TMP/regen" > "$TMP/regen.log" 2>&1; r=$?
if [ $r -eq 0 ]; then
  diffs=0
  for f in wav/*.wav wav/MANIFEST.md5; do cmp -s "$f" "$TMP/regen/$(basename "$f")" || { echo "  differs: $f"; diffs=$((diffs+1)); }; done
  [ "$(ls "$TMP/regen" | wc -l)" -eq "$(ls wav | wc -l)" ] || { echo "  file count differs"; diffs=$((diffs+1)); }
  r=$diffs
fi
report "1 determinism: regenerated files byte-identical to wav/" $r
rm -rf "$TMP/regen"

# 2-4 core checks on the delivered files; logs/CSVs land in the package directory
core_checks wav . ; r=$?

# 5 falsifiers
"$PY" s7ff_falsifiers.py wav > s7ff_falsifiers.log 2>&1; r=$?
report "5 falsifiers: $(tail -1 s7ff_falsifiers.log)" $r

# 6 gate self-test: symlink farm with one flipped byte -> core checks must FAIL
mkdir -p "$TMP/farm" "$TMP/out"
for f in wav/*; do ln -s "$(readlink -f "$f")" "$TMP/farm/$(basename "$f")"; done
victim="$TMP/farm/s7ff_v1_3150Hz_m30dB.wav"
rm "$victim"; cp "wav/s7ff_v1_3150Hz_m30dB.wav" "$victim"
printf '\x55' | dd of="$victim" bs=1 seek=$((44 + 3 * 900000)) conv=notrunc status=none
( core_checks "$TMP/farm" "$TMP/out" ) > "$TMP/selftest.log" 2>&1; r=$?   # subshell: its FAILs must not touch $overall
if [ $r -ne 0 ]; then report "6 gate self-test: one flipped byte -> core checks FAIL as required" 0
else report "6 gate self-test: corrupted copy PASSED (gate cannot fail!)" 1; fi
sed 's/^/    selftest> /' "$TMP/selftest.log"
grep '^FAIL ' "$TMP/out/s7ff_check.log" | sed 's/^/    selftest> /'

echo "== OVERALL $([ $overall -eq 0 ] && echo PASS || echo FAIL)"
exit $overall
