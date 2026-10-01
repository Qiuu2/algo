#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s7ff_check.py -- independent checker for the s7ff_v1 far-field signal package.

Independence: does NOT import gen_s7ff_signals.py. WAV bytes are parsed with struct; band edges,
file set and gates are re-derived from S7_SIDE30_FARFIELD_TEST.md §4.1/§4.3 and README.md.

Gates (every file; FAIL if any gate fails):
  H   header: RIFF/WAVE, fmt tag 1 (PCM), 1 ch, 48000 Hz, 24 bit, block align 3, byte rate 144000,
      exactly 1,728,000 samples (36.000 s), nothing after the data chunk
  R   steady RMS (samples 24,000 ... 1,703,999 = the 35 s middle) = -23 - k dB re full scale, +/-0.01 dB
  P   peak <= -3.0 dB re full scale and no sample on either rail
  F   ends quiet: |first|, |last| <= 1 LSB and RMS of the first / last 10 ms <= steady RMS - 40 dB
      (this alone does NOT prove the fades are smooth -- gate C does)
  C   continuity over the WHOLE file: remove everything within [f_lo*2^-1/3, f_hi*2^+1/3] (whole-file FFT),
      the residual must stay <= 8 LSB at every sample -- catches clicks, dropouts, abrupt starts and steps
      at the fade/steady junction anywhere in the file (critic s7ff R1 M1)
  S   in-band pink slope: -10 dB/decade +/- 0.5 (1/24-oct averages fully inside the band, exact DFT)
  B   in-band energy fraction >= 0.999 (exact DFT of the steady part)
  E1  energy beyond one octave from the band edges (f < f_lo/2 or f > 2 f_hi) <= -50 dB re in-band energy
  P1  PSD beyond one octave, 1/24-oct averages, max <= -50 dB re mean in-band PSD
  P2  PSD at the adjacent 1/3-oct centres (fc*2^(+/-1/3) and the neighbouring nominal centres),
      +/-1/48 oct average, max <= -30 dB re mean in-band PSD
  E2  energy in the adjacent 1/3-oct regions [fc*2^-1/2, f_lo) and (f_hi, fc*2^1/2], each <= -30 dB re in-band
  W   whole-file Welch (Blackman-Harris 4-term, 65536 pts, 50 % overlap, plus a final segment ending at
      the last sample so both fades are inside): far-region energy and per-bin PSD max <= -50 dB, adjacent
      centres <= -30 dB (re the Welch in-band level)
  L   level steps: the -k dB file equals the 0 dB file x 10^(-k/20) sample by sample
      (residual RMS <= 1 LSB) and the steady RMS step is -k +/- 0.01 dB
  Z   silence file: every sample is 0
  M   md5 of every file equals WAVDIR/MANIFEST.md5, and the manifest lists exactly the 61 expected files
  N   the directory holds exactly the 61 expected WAV files (no missing, no extra)

Usage:  python3 s7ff_check.py WAVDIR [--metrics OUT.csv] [--spectra OUT.csv]
Exit 0 = all PASS, 1 = any FAIL. Spectra/metrics are computed from the delivered bytes: [L2 tool].
"""
import argparse
import hashlib
import os
import struct
import sys

import numpy as np

PACKAGE = "s7ff_v1"
FS = 48000
NTOT = 1728000
M = 24000                       # fade length, samples (0.5 s)
N = NTOT - 2 * M                # steady part, samples (35 s)
FULL = 2 ** 23
BANDS = [500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300]
NOMINAL_SERIES = [315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]
LEVELS = [0, 10, 20, 30, 40]
RMS0_DB = -23.0
TOL_RMS_DB = 0.01
PEAK_MAX_DB = -3.0
FADE_DROP_DB = 40.0
SLOPE_EXPECT, SLOPE_TOL = -10.0, 0.5
INBAND_MIN = 0.999
FAR_MAX_DB = -50.0
ADJ_MAX_DB = -30.0
WELCH_N = 65536
CONT_MAX_LSB = 8.0


def name_of(fc, k):
    return "%s_%04dHz_%s.wav" % (PACKAGE, fc, "0dB" if k == 0 else "m%ddB" % k)


SILENCE = "%s_silence.wav" % PACKAGE
EXPECTED = sorted([name_of(fc, k) for fc in BANDS for k in LEVELS] + [SILENCE])


def edges(fc):
    return fc * 2.0 ** (-1 / 6), fc * 2.0 ** (1 / 6)


def db10(v):
    return 10.0 * np.log10(v) if v > 0 else -400.0


def db20(v):
    return 20.0 * np.log10(v) if v > 0 else -400.0


# ---------------------------------------------------------------- WAV parsing (struct only)
def read_wav(path):
    """Return (info dict, int samples or None, list of header problems)."""
    bad = []
    with open(path, "rb") as fh:
        blob = fh.read()
    if len(blob) < 12 or blob[0:4] != b"RIFF" or blob[8:12] != b"WAVE":
        return {}, None, ["not RIFF/WAVE"]
    riff_size = struct.unpack("<I", blob[4:8])[0]
    if riff_size + 8 != len(blob):
        bad.append("RIFF size %d+8 != file size %d" % (riff_size, len(blob)))
    pos, fmt, data, data_end = 12, None, None, None
    while pos + 8 <= len(blob):
        cid = blob[pos:pos + 4]
        csz = struct.unpack("<I", blob[pos + 4:pos + 8])[0]
        body = blob[pos + 8:pos + 8 + csz]
        if cid == b"fmt ":
            fmt = body
        elif cid == b"data":
            data, data_end = body, pos + 8 + csz
        pos += 8 + csz + (csz & 1)
    if fmt is None or data is None:
        return {}, None, bad + ["missing fmt or data chunk"]
    tag, ch, rate, brate, balign, bits = struct.unpack("<HHIIHH", fmt[:16])
    info = dict(tag=tag, ch=ch, rate=rate, brate=brate, balign=balign, bits=bits, nbytes=len(data))
    if (tag, ch, rate, bits) != (1, 1, FS, 24):
        bad.append("fmt tag/ch/rate/bits = %d/%d/%d/%d, want 1/1/%d/24" % (tag, ch, rate, bits, FS))
    if balign != 3 or brate != 3 * FS:
        bad.append("block align %d / byte rate %d, want 3 / %d" % (balign, brate, 3 * FS))
    if data_end != len(blob):
        bad.append("%d bytes after the data chunk" % (len(blob) - data_end))
    if len(data) != 3 * NTOT:
        bad.append("data %d bytes = %.4f s, want %d bytes = 36.000 s" % (len(data), len(data) / 3 / FS, 3 * NTOT))
    if bits != 24 or ch != 1 or len(data) % 3:
        return info, None, bad
    b = np.frombuffer(data, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
    v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
    v = np.where(v >= FULL, v - 2 * FULL, v)
    return info, v.astype(np.int64), bad


# ---------------------------------------------------------------- spectral helpers
def onesided_power(x):
    X = np.fft.rfft(x)
    p = np.abs(X) ** 2
    p[1:-1] *= 2.0              # even length: bins 1 .. n/2-1 carry both signs
    f = np.arange(len(p)) * (FS / len(x))
    return f, p


def bh4(n):
    a = (0.35875, 0.48829, 0.14128, 0.01168)
    k = np.arange(n) * (2 * np.pi / n)
    return a[0] - a[1] * np.cos(k) + a[2] * np.cos(2 * k) - a[3] * np.cos(3 * k)


def welch(x, n=WELCH_N):
    w = bh4(n)
    hop = n // 2
    starts = list(range(0, len(x) - n + 1, hop))
    if starts[-1] != len(x) - n:
        starts.append(len(x) - n)        # last segment ends at the last sample -> fade-out included
    acc = np.zeros(n // 2 + 1)
    for s in starts:
        acc += np.abs(np.fft.rfft(x[s:s + n] * w)) ** 2
    acc[1:-1] *= 2.0
    return np.arange(n // 2 + 1) * (FS / n), acc / len(starts)


def continuity_residual_lsb(x, fc):
    """Max |x - (its content within [f_lo*2^-1/3, f_hi*2^+1/3])| over the whole file, in LSB."""
    lo, hi = edges(fc)
    X = np.fft.rfft(x)
    f = np.arange(len(X)) * (FS / len(x))
    X[(f >= lo * 2.0 ** (-1 / 3)) & (f <= hi * 2.0 ** (1 / 3))] = 0.0
    return float(np.abs(np.fft.irfft(X, n=len(x))).max() * FULL)


def mean_in(f, p, lo, hi):
    """Mean of p over lo <= f < hi (f ascending)."""
    i, j = np.searchsorted(f, [lo, hi], side="left")
    return p[i:j].mean() if j > i else 0.0


def adj_centres(fc):
    i = NOMINAL_SERIES.index(fc)
    return [fc * 2.0 ** (-1 / 3), fc * 2.0 ** (1 / 3), NOMINAL_SERIES[i - 1], NOMINAL_SERIES[i + 1]]


def spectral_metrics(fc, steady, whole):
    lo, hi = edges(fc)
    f, p = onesided_power(steady)
    inb = (f >= lo) & (f <= hi)
    e_in, e_tot = p[inb].sum(), p.sum()
    psd_in = p[inb].mean()
    far = (f < lo / 2) | (f > 2 * hi)
    out = {}
    out["B_inband_frac"] = e_in / e_tot
    out["E1_far_energy_dB"] = db10(p[far].sum() / e_in)
    out["near_energy_dB_info"] = db10(p[((f >= lo / 2) & (f < lo)) | ((f > hi) & (f <= 2 * hi))].sum() / e_in)
    # P1: 1/24-oct averages over the far region
    worst = -400.0
    for n24 in range(-150, 116):
        fcen = 1000.0 * 2.0 ** (n24 / 24.0)
        a, b = fcen * 2.0 ** (-1 / 48), fcen * 2.0 ** (1 / 48)
        if b > FS / 2:
            break
        if not (b < lo / 2 or a > 2 * hi):
            continue
        worst = max(worst, db10(mean_in(f, p, a, b) / psd_in))
    out["P1_far_psd_dB"] = worst
    out["P1_far_psd_bin_max_dB_info"] = db10(p[far].max() / psd_in)
    out["P2_adj_psd_dB"] = max(db10(mean_in(f, p, c * 2.0 ** (-1 / 48), c * 2.0 ** (1 / 48)) / psd_in) for c in adj_centres(fc))
    e2lo = p[(f >= fc * 2.0 ** -0.5) & (f < lo)].sum() / e_in
    e2hi = p[(f > hi) & (f <= fc * 2.0 ** 0.5)].sum() / e_in
    out["E2_adj_energy_dB"] = db10(max(e2lo, e2hi))
    # S: pink slope from 1/24-oct averages fully inside the band
    xs, ys = [], []
    for n24 in range(-150, 116):
        fcen = 1000.0 * 2.0 ** (n24 / 24.0)
        a, b = fcen * 2.0 ** (-1 / 48), fcen * 2.0 ** (1 / 48)
        if a >= lo and b <= hi:
            xs.append(np.log10(fcen))
            ys.append(db10(mean_in(f, p, a, b)))
    out["S_slope_dB_per_decade"] = float(np.polyfit(xs, ys, 1)[0]) if len(xs) >= 3 else float("nan")
    out["S_points"] = len(xs)
    # W: whole-file Welch
    fw, pw = welch(whole)
    inw = (fw >= lo) & (fw <= hi)
    psd_w = pw[inw].mean()
    farw = (fw < lo / 2) | (fw > 2 * hi)
    out["W_far_energy_dB"] = db10(pw[farw].sum() / pw[inw].sum())
    out["W_far_psd_bin_max_dB"] = db10(pw[farw].max() / psd_w)
    out["W_adj_psd_dB"] = max(db10(mean_in(fw, pw, c * 2.0 ** (-1 / 48), c * 2.0 ** (1 / 48)) / psd_w) for c in adj_centres(fc))
    return out, (f, p, psd_in)


def spectrum_24(f, p, psd_in):
    rows = []
    for n24 in range(-135, 110):
        fcen = 1000.0 * 2.0 ** (n24 / 24.0)
        a, b = fcen * 2.0 ** (-1 / 48), fcen * 2.0 ** (1 / 48)
        rows.append((fcen, db10(mean_in(f, p, a, b) / psd_in)))
    return rows


# ---------------------------------------------------------------- per-file checks
def check_signal_file(path, fc, k):
    """Return (metrics dict, list of failures, int samples, spectra rows)."""
    info, v, bad = read_wav(path)
    fails = ["H: " + s for s in bad]
    met = {"file": os.path.basename(path), "band_hz": fc, "level_db": -k}
    if v is None or len(v) != NTOT:
        return met, fails or ["H: unreadable"], None, None
    x = v / FULL
    steady = x[M:M + N]
    rms = np.sqrt(np.mean(steady * steady))
    met["R_rms_dB"] = db20(rms)
    if abs(met["R_rms_dB"] - (RMS0_DB - k)) > TOL_RMS_DB:
        fails.append("R: steady RMS %.4f dB, want %.2f +/- %.2f" % (met["R_rms_dB"], RMS0_DB - k, TOL_RMS_DB))
    met["P_peak_dB"] = db20(np.abs(x).max())
    if met["P_peak_dB"] > PEAK_MAX_DB:
        fails.append("P: peak %.3f dB re FS > %.1f" % (met["P_peak_dB"], PEAK_MAX_DB))
    if (v >= FULL - 1).any() or (v <= -FULL).any():
        fails.append("P: sample on a rail")
    met["F_first_lsb"], met["F_last_lsb"] = int(v[0]), int(v[-1])
    e10 = int(0.010 * FS)
    met["F_head10ms_dB"] = db20(np.sqrt(np.mean(x[:e10] ** 2))) - met["R_rms_dB"]
    met["F_tail10ms_dB"] = db20(np.sqrt(np.mean(x[-e10:] ** 2))) - met["R_rms_dB"]
    if abs(v[0]) > 1 or abs(v[-1]) > 1:
        fails.append("F: first/last sample %d/%d LSB (click at start/stop)" % (v[0], v[-1]))
    if met["F_head10ms_dB"] > -FADE_DROP_DB or met["F_tail10ms_dB"] > -FADE_DROP_DB:
        fails.append("F: first/last 10 ms only %.1f/%.1f dB below steady (no fade)" % (met["F_head10ms_dB"], met["F_tail10ms_dB"]))
    # info only (no gate): Leq-window level spread when the window is not a whole period;
    # window start 1.0 s ... (35.5 s - T), step 0.25 s, level = 10 log10(mean x^2)
    cs = np.concatenate([[0.0], np.cumsum(x * x)])
    for T in (10, 30):
        n = T * FS
        st = np.arange(FS, int(35.5 * FS) - n + 1, FS // 4)
        lv = 10.0 * np.log10((cs[st + n] - cs[st]) / n)
        met["Leq%ds_range_dB_info" % T] = float(lv.max() - lv.min())
    met["C_resid_max_lsb"] = continuity_residual_lsb(x, fc)
    if met["C_resid_max_lsb"] > CONT_MAX_LSB:
        fails.append("C: out-of-band residual peaks at %.1f LSB > %.0f (click / dropout / abrupt start / step)"
                     % (met["C_resid_max_lsb"], CONT_MAX_LSB))
    sm, (f, p, psd_in) = spectral_metrics(fc, steady, x)
    met.update(sm)
    if not (abs(sm["S_slope_dB_per_decade"] - SLOPE_EXPECT) <= SLOPE_TOL):
        fails.append("S: in-band slope %.2f dB/decade, want %.1f +/- %.1f (pink)" % (sm["S_slope_dB_per_decade"], SLOPE_EXPECT, SLOPE_TOL))
    if sm["B_inband_frac"] < INBAND_MIN:
        fails.append("B: in-band energy fraction %.6f < %.3f" % (sm["B_inband_frac"], INBAND_MIN))
    for key, lim, tag in (("E1_far_energy_dB", FAR_MAX_DB, "E1"), ("P1_far_psd_dB", FAR_MAX_DB, "P1"),
                          ("P2_adj_psd_dB", ADJ_MAX_DB, "P2"), ("E2_adj_energy_dB", ADJ_MAX_DB, "E2"),
                          ("W_far_energy_dB", FAR_MAX_DB, "W"), ("W_far_psd_bin_max_dB", FAR_MAX_DB, "W"),
                          ("W_adj_psd_dB", ADJ_MAX_DB, "W")):
        if sm[key] > lim:
            fails.append("%s: %s = %.1f dB > %.0f dB" % (tag, key, sm[key], lim))
    return met, fails, v, spectrum_24(f, p, psd_in)


def check_step(v_k, v_0, k):
    """Level step: -k dB file vs 0 dB file. Returns (metrics, failures)."""
    g = 10.0 ** (-k / 20.0)
    resid = v_k - v_0 * g                      # in LSB
    r_lsb = float(np.sqrt(np.mean(resid ** 2)))
    s0, sk = v_0[M:M + N] / FULL, v_k[M:M + N] / FULL
    step = db20(np.sqrt(np.mean(sk ** 2))) - db20(np.sqrt(np.mean(s0 ** 2)))
    fails = []
    if r_lsb > 1.0:
        fails.append("L: residual vs 0 dB file x 10^(-%d/20) = %.2f LSB RMS > 1 (not the same waveform)" % (k, r_lsb))
    if abs(step + k) > TOL_RMS_DB:
        fails.append("L: steady RMS step %.4f dB, want %d +/- %.2f" % (step, -k, TOL_RMS_DB))
    return {"L_resid_lsb": r_lsb, "L_step_dB": step}, fails


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_dir(wavdir, metrics_csv=None, spectra_csv=None, verbose=True):
    fails_all = {}
    present = sorted(n for n in os.listdir(wavdir) if n.lower().endswith(".wav"))
    missing = [n for n in EXPECTED if n not in present]
    extra = [n for n in present if n not in EXPECTED]
    if missing or extra:
        fails_all["(directory)"] = ["N: missing %s extra %s" % (missing, extra)]
    man = os.path.join(wavdir, "MANIFEST.md5")
    if not os.path.isfile(man):
        fails_all.setdefault("(manifest)", []).append("M: MANIFEST.md5 missing")
        listed = {}
    else:
        listed = {}
        with open(man) as fh:
            for line in fh:
                if line.strip():
                    h, nm = line.split(None, 1)
                    listed[nm.strip().lstrip("*")] = h.lower()
        if sorted(listed) != EXPECTED:
            fails_all.setdefault("(manifest)", []).append("M: manifest does not list exactly the 61 expected files")
    rows, spectra = [], {}
    for fc in BANDS:
        v0 = None
        for k in LEVELS:
            nm = name_of(fc, k)
            path = os.path.join(wavdir, nm)
            if not os.path.isfile(path):
                continue
            met, fails, v, spec = check_signal_file(path, fc, k)
            if k == 0:
                v0 = v
            elif v is not None and v0 is not None:
                sm, sf = check_step(v, v0, k)
                met.update(sm)
                fails += sf
            if nm in listed and md5_of(path) != listed[nm]:
                fails.append("M: md5 differs from MANIFEST.md5")
            met["verdict"] = "PASS" if not fails else "FAIL"
            rows.append(met)
            if spec is not None:
                spectra[nm] = spec
            if fails:
                fails_all[nm] = fails
    sp = os.path.join(wavdir, SILENCE)
    if os.path.isfile(sp):
        info, v, bad = read_wav(sp)
        fails = ["H: " + s for s in bad]
        if v is None or (v != 0).any():
            fails.append("Z: silence file has non-zero samples")
        if SILENCE in listed and md5_of(sp) != listed[SILENCE]:
            fails.append("M: md5 differs from MANIFEST.md5")
        rows.append({"file": SILENCE, "band_hz": "-", "level_db": "-", "verdict": "PASS" if not fails else "FAIL"})
        if fails:
            fails_all[SILENCE] = fails

    if verbose:
        hdr = ("file", "rms_dB", "peak_dB", "inband", "E1", "P1", "P2", "E2", "W_E", "W_P", "W_adj", "slope", "C_lsb", "L_lsb", "verdict")
        print("%-28s %8s %8s %9s %7s %7s %7s %7s %7s %7s %7s %7s %6s %6s %s" % hdr)
        for r in rows:
            if "R_rms_dB" not in r:
                print("%-28s %s" % (r["file"], r["verdict"]))
                continue
            print("%-28s %8.3f %8.3f %9.6f %7.1f %7.1f %7.1f %7.1f %7.1f %7.1f %7.1f %7.2f %6.2f %6s %s" % (
                r["file"].replace(PACKAGE + "_", ""), r["R_rms_dB"], r["P_peak_dB"], r["B_inband_frac"],
                r["E1_far_energy_dB"], r["P1_far_psd_dB"], r["P2_adj_psd_dB"], r["E2_adj_energy_dB"],
                r["W_far_energy_dB"], r["W_far_psd_bin_max_dB"], r["W_adj_psd_dB"], r["S_slope_dB_per_decade"],
                r["C_resid_max_lsb"], ("%.2f" % r["L_resid_lsb"]) if "L_resid_lsb" in r else "-", r["verdict"]))
        print()
        for nm, fl in fails_all.items():
            for s in fl:
                print("FAIL %s: %s" % (nm, s))
        print("files checked: %d | FAIL items: %d | OVERALL %s" % (len(rows), sum(len(v) for v in fails_all.values()),
                                                                  "PASS" if not fails_all else "FAIL"))
    if metrics_csv:
        keys = []
        for r in rows:
            for kk in r:
                if kk not in keys:
                    keys.append(kk)
        with open(metrics_csv, "w", newline="\n") as fh:
            fh.write(",".join(keys) + "\n")
            for r in rows:
                fh.write(",".join(("%.6g" % r[kk]) if isinstance(r.get(kk), float) else str(r.get(kk, "")) for kk in keys) + "\n")
    if spectra_csv and spectra:
        names = [n for n in EXPECTED if n in spectra]
        freqs = [fr for fr, _ in spectra[names[0]]]
        with open(spectra_csv, "w", newline="\n") as fh:
            fh.write("# 1/24-octave band-averaged PSD of each file's 35 s steady part (exact DFT of the delivered bytes),"
                     " dB re that file's mean in-band PSD. [L2 tool]\n")
            fh.write("f_centre_Hz," + ",".join(names) + "\n")
            for i, fr in enumerate(freqs):
                fh.write("%.2f," % fr + ",".join("%.2f" % spectra[n][i][1] for n in names) + "\n")
    return not fails_all


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wavdir")
    ap.add_argument("--metrics")
    ap.add_argument("--spectra")
    a = ap.parse_args()
    ok = check_dir(a.wavdir, a.metrics, a.spectra)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
