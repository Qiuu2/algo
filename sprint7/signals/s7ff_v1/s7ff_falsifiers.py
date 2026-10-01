#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s7ff_falsifiers.py -- prove that s7ff_check.py can FAIL (no false green).

Builds deliberately broken copies of good package files in a temporary directory and runs the
checker on each. Every falsifier must FAIL with the gate tag it targets; the untouched file (positive
control) must PASS. Exit 0 only if all of that holds.

Usage: python3 s7ff_falsifiers.py WAVDIR
"""
import os
import shutil
import struct
import sys
import tempfile
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7ff_check as C   # the checker under test (NOT the generator)


def write_wav(path, q, ch=1, rate=C.FS):
    q = np.asarray(q, dtype=np.int64)
    if ch == 2:
        q = np.repeat(q, 2)
    raw = q.astype("<i4").view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(3)
        w.setframerate(rate)
        w.writeframes(raw)


def quant(y):
    return np.clip(np.rint(y), -C.FULL, C.FULL - 1).astype(np.int64)


def fades():
    n = np.arange(C.M)
    fin = 0.5 * (1.0 - np.cos(np.pi * n / C.M))
    return fin, fin[::-1].copy()


def tags(fails):
    return sorted(set(s.split(":")[0] for s in fails))


def main():
    good = sys.argv[1]
    _, v1000, _ = C.read_wav(os.path.join(good, C.name_of(1000, 0)))
    _, v1250, _ = C.read_wav(os.path.join(good, C.name_of(1250, 0)))
    _, v1000_40, _ = C.read_wav(os.path.join(good, C.name_of(1000, 40)))
    rng = np.random.default_rng(7)
    tmp = tempfile.mkdtemp(prefix="s7ff_falsify_")
    results = []

    def file_case(label, expect, q=None, fc=1000, k=0, writer=None, ref=None):
        path = os.path.join(tmp, C.name_of(fc, k))
        if writer is not None:
            writer(path)
        else:
            write_wav(path, q)
        met, fails, v, _ = C.check_signal_file(path, fc, k)
        if ref is not None and v is not None:
            _, sf = C.check_step(v, ref, k)
            fails = fails + sf
        got = tags(fails)
        ok = (expect in got) if expect else (not fails)
        results.append((label, expect or "(none)", got, ok, fails[:3]))
        os.remove(path)

    # positive control: the delivered file, re-written unchanged, must PASS
    file_case("P0 untouched 1000 Hz 0 dB (positive control)", None, q=v1000)
    # F1 broadband white noise 45 dB below the in-band power (fails the far-energy spec)
    sig_p = np.mean((v1000[C.M:C.M + C.N] / C.FULL) ** 2)
    noise = rng.standard_normal(C.NTOT) * np.sqrt(sig_p * 10 ** (-45 / 10)) * C.FULL
    file_case("F1 + white noise at -45 dB re in-band", "E1", q=quant(v1000 + noise))
    # F2 level +0.5 dB
    file_case("F2 level +0.5 dB", "R", q=quant(v1000 * 10 ** (0.5 / 20)))
    # F3 wrong band: 1250 Hz content under the 1000 Hz name
    file_case("F3 1250 Hz content named 1000 Hz", "B", q=v1250)
    # F4 boosted 15 dB and hard clipped
    file_case("F4 +15 dB, clipped at full scale", "P", q=quant(v1000 * 10 ** (15 / 20)))
    # F5 fades removed (periodic continuation at full level -> click at start/stop)
    st = v1000[C.M:C.M + C.N]
    file_case("F5 no fade-in/fade-out", "F", q=np.concatenate([st[C.N - C.M:], st, st[:C.M]]))
    # F6 the -40 dB file re-quantised to 16 bit (rounding floor ~ -41 dB re in-band)
    file_case("F6 -40 dB file re-quantised to 16 bit", "E1", q=np.rint(v1000_40 / 256.0).astype(np.int64) * 256, k=40)
    # F7 header says 44100 Hz
    def w44(path):
        write_wav(path, v1000)
        with open(path, "r+b") as fh:
            fh.seek(24)
            fh.write(struct.pack("<II", 44100, 3 * 44100))
    file_case("F7 header sample rate 44100", "H", writer=w44)
    # F8 truncated to 30 s
    file_case("F8 truncated to 30 s", "H", q=v1000[:30 * C.FS])
    # F9 white (flat) inside the band instead of pink
    X = np.fft.rfft(st / C.FULL)
    lo, hi = C.edges(1000)
    f = np.arange(len(X)) * (C.FS / C.N)
    inb = (f >= lo) & (f <= hi)
    X[inb] = np.exp(1j * np.angle(X[inb]))
    X[~inb] = 0
    x = np.fft.irfft(X, n=C.N)
    x *= 10 ** (C.RMS0_DB / 20) / np.sqrt(np.mean(x * x))
    fin, fout = fades()
    file_case("F9 flat (white) in band, not pink", "S",
              q=quant(np.concatenate([x[C.N - C.M:] * fin, x, x[:C.M] * fout]) * C.FULL))
    # F11 -10 dB file that is really -9.5 dB
    file_case("F11 '-10 dB' file at -9.5 dB", "L", q=quant(v1000 * 10 ** (-9.5 / 20)), k=10, ref=v1000)
    # F13 stereo file
    file_case("F13 stereo (2 channels)", "H", writer=lambda p: write_wav(p, v1000, ch=2))

    # ---- time-domain defects that gates F/R/P cannot see (critic s7ff R1 M1) -> gate C
    fin, fout = fades()
    # F16 20 ms of silence, then full level with no fade (first sample 0, first 10 ms silent -> F passes)
    q = np.concatenate([np.zeros(960, dtype=np.int64), st[C.N - C.M + 960:], st, np.rint(st[:C.M] * fout).astype(np.int64)])
    file_case("F16 20 ms silence then abrupt full-level start", "C", q=q)
    # F17 5 ms dropout in the middle of the steady part
    q = v1000.copy(); q[864000:864240] = 0
    file_case("F17 5 ms dropout mid-file", "C", q=q)
    # F18 one-sample click of 64 LSB (-102 dB re full scale) mid-file
    q = v1000.copy(); q[500000] += 64
    file_case("F18 single 64-LSB click mid-file", "C", q=q)
    # F19 fade-in taken from the wrong place -> step at the fade/steady junction (0.5 s)
    q = np.concatenate([np.rint(st[1000:1000 + C.M] * fin).astype(np.int64), st, np.rint(st[:C.M] * fout).astype(np.int64)])
    file_case("F19 step at the fade-in / steady junction", "C", q=q)

    # ---- targeted spectral gates (each designed so that its own gate fails)
    t = np.arange(C.NTOT) / C.FS
    rms_in = np.sqrt(np.mean((st / C.FULL) ** 2)) * C.FULL       # LSB
    def tone(freq, rel_db):                                       # sine with power rel_db re in-band power
        return np.sqrt(2.0) * rms_in * 10 ** (rel_db / 20) * np.sin(2 * np.pi * freq * t)
    # F20 far-region tone at 3 kHz, 52 dB below the in-band power: E1 still passes (-52 < -50) but the
    #     1/24-oct PSD average around 3 kHz is ~4.3 dB higher than E1 -> P1 fails
    file_case("F20 3 kHz tone at -52 dB (P1 targeted, E1 passes)", "P1", q=quant(v1000 + tone(3000.0, -52.0)))
    # F21 tone at the adjacent centre 1000*2^(1/3) Hz, 35 dB below in-band power: E2 passes (-35 < -30)
    #     but the +/-1/48-oct PSD there is ~8 dB higher -> P2 fails
    file_case("F21 adjacent-centre tone at -35 dB (P2 targeted, E2 passes)", "P2",
              q=quant(v1000 + tone(1000.0 * 2 ** (1 / 3), -35.0)))
    # F22 noise confined to 1125-1175 Hz (just above the band edge, away from the adjacent centre), -25 dB
    nz = rng.standard_normal(C.NTOT)
    Z = np.fft.rfft(nz); fz = np.arange(len(Z)) * (C.FS / C.NTOT)
    Z[(fz < 1125.0) | (fz > 1175.0)] = 0
    nz = np.fft.irfft(Z, n=C.NTOT); nz *= rms_in * 10 ** (-25 / 20) / np.sqrt(np.mean(nz ** 2))
    file_case("F22 noise just above the band edge at -25 dB (E2 targeted)", "E2", q=quant(v1000 + nz))
    # F23 broadband noise only inside the fade-in (10 ms ... 490 ms): the steady-part gates cannot see it,
    #     the whole-file Welch must
    q = v1000.astype(np.float64)
    seg = slice(480, C.M - 480)
    q[seg] += rng.standard_normal(seg.stop - seg.start) * rms_in * 10 ** (-20 / 20)
    file_case("F23 broadband noise only inside the fade-in (W targeted)", "W", q=quant(q))

    # directory-level cases: symlink farm of the good package with one change
    def dir_case(label, expect, mutate):
        d = tempfile.mkdtemp(prefix="s7ff_dir_", dir=tmp)
        for n in os.listdir(good):
            src = os.path.join(good, n)
            if n == "MANIFEST.md5":
                shutil.copy(src, os.path.join(d, n))
            else:
                os.symlink(os.path.abspath(src), os.path.join(d, n))
        mutate(d)
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok_dir = C.check_dir(d, verbose=True)
        got = sorted(set(line.split(": ", 1)[1].split(":")[0] for line in buf.getvalue().splitlines()
                         if line.startswith("FAIL ")))
        ok = (not ok_dir) and (expect in got)
        results.append((label, expect, got, ok, [l for l in buf.getvalue().splitlines() if l.startswith("FAIL ")][:3]))
        shutil.rmtree(d)

    def flip_byte(d):
        p = os.path.join(d, C.name_of(2000, 20))
        os.remove(p)
        shutil.copy(os.path.join(good, C.name_of(2000, 20)), p)
        with open(p, "r+b") as fh:
            fh.seek(44 + 3 * 800000)
            b = fh.read(1)
            fh.seek(44 + 3 * 800000)
            fh.write(bytes([b[0] ^ 0x01]))
    dir_case("F10 one LSB flipped in a file (md5)", "M", flip_byte)
    dir_case("F12 one file missing", "N", lambda d: os.remove(os.path.join(d, C.name_of(4000, 30))))

    def bad_silence(d):
        p = os.path.join(d, C.SILENCE)
        os.remove(p)
        z = np.zeros(C.NTOT, dtype=np.int64)
        z[C.NTOT // 2] = 1
        write_wav(p, z)
    dir_case("F14 silence file with one non-zero sample", "Z", bad_silence)

    def short_manifest(d):
        p = os.path.join(d, "MANIFEST.md5")
        lines = open(p).read().splitlines()
        with open(p, "w") as fh:
            fh.write("\n".join(lines[1:]) + "\n")
    dir_case("F15 manifest missing one entry", "M", short_manifest)

    shutil.rmtree(tmp)
    allok = True
    for label, expect, got, ok, fl in results:
        allok &= ok
        print("%-48s expect %-6s got %-22s %s" % (label, expect, ",".join(got) or "-", "OK" if ok else "<<< WRONG"))
        if not ok or expect != "(none)":
            for s in fl:
                print("      %s" % s)
    print("falsifiers: %d cases | OVERALL %s" % (len(results), "PASS (every falsifier failed as targeted; control passed)" if allok else "FAIL"))
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
