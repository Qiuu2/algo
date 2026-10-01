#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_s7ff_signals.py -- S7 far-field per-band test signals, package s7ff_v1.

Spec source: sprint7/docs/S7_SIDE30_FARFIELD_TEST.md
  §4.1  per-band 1/3-octave pink noise, centres 500 ... 5000 Hz + 6300 Hz (grating check);
        all files the SAME digital RMS; each file >= Leq + 5 s; out-of-band attenuation
        >= 50 dB beyond one octave from the band edge, >= 30 dB at the adjacent 1/3-oct centres
        ([L4 provisional] spec, CTO/dsp may change); files delivered with list + md5 + spectra.
  §4.3  per band, -10/-20/-30/-40 dB digitally attenuated versions.
  §4.4  background is measured with the source muted ("player stopped / silence file").
  §5-6  Leq 10-30 s, one duration for the whole session.

What this script writes (into --outdir, default ./wav next to this script):
  12 bands x 5 levels (0, -10, -20, -30, -40 dB) + 1 silence file = 61 WAV files,
  mono, PCM 24-bit little-endian, 48 kHz, 1,728,000 samples (36.000 s) each:
  0.5 s raised-cosine fade-in + 35.000 s steady + 0.5 s raised-cosine fade-out.
  Also writes MANIFEST.md5 (md5sum format) into --outdir and a log on stdout.

Signal construction (choices are PM proposals, documented in README.md):
  * Band b = [fc * 2^(-1/6), fc * 2^(+1/6)] with NOMINAL fc -- the same band convention as
    sprint7/sim/side30/fir/s7_fir_robust_design.py:297 and the 891-4490 Hz union used by
    S7_DRIVER_MATCHING_RUNBOOK.md.
  * One DFT period N = 35 s * 48 kHz = 1,680,000 samples. Every DFT bin inside the band gets
    amplitude f^(-1/2) (power ~ 1/f = pink) and a uniform random phase (seeded per band); every
    bin outside the band is exactly zero. x = irfft(X) is therefore periodic with period N and
    contains no out-of-band energy except the 24-bit rounding error.
  * The 35 s steady part of the file is exactly one period; the 0.5 s fade-in uses the last 0.5 s
    of the period and the fade-out uses the first 0.5 s, so the file is one continuous piece of
    the periodic signal with smooth ends (no click at start/stop).
  * Steady-part RMS of every 0 dB file = -23.00 dB re digital full scale (amplitude 1.0), so the
    hottest peak stays about 8.5 dB below full scale (board input headroom contract 0x49A00000 = -4.8 dBFS,
    S7_VERIFICATION_PLAN.md:53; critic s7ff R1 M2).
    The -k dB files are the SAME float waveform multiplied by 10^(-k/20), then rounded to 24 bit
    (each level rounded once from float; no double rounding).
  * Rounding: round-half-to-even, no dither. Full scale is never reached (asserted, never clipped).

Determinism: same numpy build -> byte-identical files (checked by run_s7ff_checks.sh).
No scipy needed. Python 3.8+, numpy.
"""
import argparse
import hashlib
import os
import platform
import sys
import wave

import numpy as np

PACKAGE = "s7ff_v1"
FS = 48000                      # Hz, board audio rate
STEADY_S = 35                   # s, one DFT period
FADE_S = 0.5                    # s, raised-cosine fade at each end
N = STEADY_S * FS               # 1,680,000 samples per period
M = int(FADE_S * FS)            # 24,000 samples per fade
NTOT = N + 2 * M                # 1,728,000 samples per file (36.000 s)
BITS = 24
FULL = 2 ** (BITS - 1)          # 8,388,608 -> digital full scale 1.0
RMS_DB = -23.0                  # steady RMS of the 0 dB files, dB re full scale (1.0)
BANDS_HZ = [500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300]  # nominal fc
LEVELS_DB = [0, 10, 20, 30, 40]  # digital attenuation
SEED_BASE = 20261002


def level_tag(k):
    return "0dB" if k == 0 else "m%ddB" % k


def file_name(fc, k):
    return "%s_%04dHz_%s.wav" % (PACKAGE, fc, level_tag(k))


SILENCE_NAME = "%s_silence.wav" % PACKAGE


def band_edges(fc):
    return fc * 2.0 ** (-1.0 / 6.0), fc * 2.0 ** (1.0 / 6.0)


def make_period(fc):
    """One period (N samples, float64) of the band-limited pink multisine, RMS = 1.0."""
    f = np.arange(N // 2 + 1) * (FS / N)
    lo, hi = band_edges(fc)
    inband = (f >= lo) & (f <= hi)
    rng = np.random.default_rng([SEED_BASE, fc])
    phase = rng.uniform(0.0, 2.0 * np.pi, size=int(inband.sum()))
    spec = np.zeros(N // 2 + 1, dtype=np.complex128)
    spec[inband] = f[inband] ** -0.5 * np.exp(1j * phase)
    x = np.fft.irfft(spec, n=N)
    x /= np.sqrt(np.mean(x * x))
    return x, int(inband.sum())


def fades():
    n = np.arange(M)
    fin = 0.5 * (1.0 - np.cos(np.pi * n / M))   # fin[0] = 0, rises to ~1
    fout = fin[::-1].copy()                      # falls from ~1, fout[-1] = 0
    return fin, fout


def to_file_float(x):
    """Period -> full file (fade-in from the period's tail, steady period, fade-out from its head)."""
    fin, fout = fades()
    return np.concatenate([x[N - M:] * fin, x, x[:M] * fout])


def quantize(y):
    q = np.rint(y * FULL).astype(np.int64)
    if q.max() > FULL - 1 or q.min() < -FULL:
        raise SystemExit("FATAL: full scale reached (max %d min %d) -- refusing to clip" % (q.max(), q.min()))
    return q


def write_wav(path, q):
    raw = q.astype("<i4").view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(BITS // 8)
        w.setframerate(FS)
        w.writeframes(raw)


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def db(v):
    return 20.0 * np.log10(v) if v > 0 else float("-inf")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "wav"))
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    print("%s generator | python %s | numpy %s | %s" % (PACKAGE, platform.python_version(), np.__version__, platform.platform()))
    print("FS %d Hz | %d-bit mono PCM | period N=%d (%.3f s) | fades %d samples (%.3f s) | total %d samples (%.3f s)"
          % (FS, BITS, N, N / FS, M, M / FS, NTOT, NTOT / FS))
    print("steady RMS (0 dB files) = %.2f dB re full scale 1.0 | levels %s dB | seed base %d" % (RMS_DB, LEVELS_DB, SEED_BASE))
    print()
    print("%-34s %8s %10s %10s %8s %10s %10s  %s" % ("file", "fc_Hz", "f_lo_Hz", "f_hi_Hz", "bins", "rms_dB", "peak_dB", "md5"))

    manifest = []
    g0 = 10.0 ** (RMS_DB / 20.0)
    for fc in BANDS_HZ:
        x, nbins = make_period(fc)
        y = to_file_float(x) * g0
        lo, hi = band_edges(fc)
        for k in LEVELS_DB:
            q = quantize(y * 10.0 ** (-k / 20.0))
            name = file_name(fc, k)
            path = os.path.join(args.outdir, name)
            write_wav(path, q)
            steady = q[M:M + N] / FULL
            rms = np.sqrt(np.mean(steady * steady))
            peak = np.abs(q).max() / FULL
            md5 = md5_of(path)
            manifest.append((md5, name))
            print("%-34s %8d %10.2f %10.2f %8d %10.3f %10.3f  %s" % (name, fc, lo, hi, nbins, db(rms), db(peak), md5))

    q = np.zeros(NTOT, dtype=np.int64)
    path = os.path.join(args.outdir, SILENCE_NAME)
    write_wav(path, q)
    md5 = md5_of(path)
    manifest.append((md5, SILENCE_NAME))
    print("%-34s %8s %10s %10s %8s %10s %10s  %s" % (SILENCE_NAME, "-", "-", "-", "-", "-inf", "-inf", md5))

    manifest.sort(key=lambda t: t[1])
    man_path = os.path.join(args.outdir, "MANIFEST.md5")
    with open(man_path, "w", newline="\n") as fh:
        for md5, name in manifest:
            fh.write("%s *%s\n" % (md5, name))
    print()
    print("files: %d | MANIFEST.md5 md5 = %s" % (len(manifest), md5_of(man_path)))


if __name__ == "__main__":
    main()
