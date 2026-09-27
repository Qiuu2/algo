#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
gen_firbench_tables.py -- S7 per-channel FIR compute bench (DEC-S7-SIDE30-01 (3)): coefficient + golden generator.

Produces (ASCII-only, CCES-safe):
  ../fb_coeffs.h   8-channel V1 FIR tables for the 64/128/256-tap tiers = 63/127/255 real taps (type-I, odd,
                   exactly symmetric after quantisation), Q15-in-int32, equal on-axis gain to today's Dolph-20
                   table (max weight 1.0), plus a CRC32 fingerprint per table and of the frozen chirp.
  ../fb_goldens.h  per-channel golden CRC32 of the Q31 output stream, 1024 frames x 64 samples of the FROZEN chirp
                   (sprint4/dsp/core_only/bench/chirp_input.h, read-only), per tap set.

Coefficient provenance (reproducible, no hand edits):
  * 127 taps = the V1 rows of the frozen design CSV sprint7/sim/side30/fir/s7_fir_coeffs_127tap.csv ("V1-128").
  * 63 / 255 taps = the SAME design code path (s7_fir_robust_design.py: sigma2_gain(seed 20260926) ->
    perbin_design(V1) -> smooth_logf -> fit_fir(L)), imported read-only and run in memory (the design script's
    main() is NOT called, none of its outputs are written). The 127-tap re-derivation is compared against the
    CSV as a reproducibility check (printed; the CSV stays the source of the 127-tap set).
Fixed-point format (identical to the project FIRA fixed-point path, fira_tree.c: SIGNED_INTEGER, int32
  coefficient words, exact integer MAC, core postscale ">>15" + Q31 saturate):
    c[k] = floor(h_eq[k] * 2^15 + 0.5), h_eq = h * G, G = d20_axis_level() = 2*sum(w8)/max(w8)  (equal on-axis
    gain to the Dolph-20 table, S7_SIDE30_PERCH_FIR_DESIGN.md sec 6-4). |c| may exceed 32767 (max ~1.03 * 2^15):
    it is a Q15 VALUE in an int32 container (same as g_dolph_w8_q15[7] = 32768). Quantised on the first half
    (k = 0..M) and mirrored -> exactly symmetric integers (FIRA tap orientation is then moot, cf. fira_tree.c
    [ASSUME A-orient]).
    y[n] = sat32( (sum_k c[k] * x[n-k]) >> 15 ),  x = Q31 chirp, x[n<0] = 0, arithmetic shift (floor).
Golden track 1 = this script (numpy int64 np.convolve over the WHOLE 65536-sample signal, zlib.crc32 over the
  little-endian int32 output bytes == bench_harness.c crc32_buf). Track 2 = host/fb_ref_host.c (plain C loops).
FG2 (placeholder must FAIL): Dolph-20 weight x delta[k-M] and uniform (G/16) x delta[k-M] (both have the same
  sum_c 2c_c as the real set up to rounding -> "sum 2h = delta" can never be a coefficient check) are run through
  the same reference; every channel of every tap set must MISS its golden, including over the 0.7-5.2 kHz
  chirp window alone.

Usage:  /usr/bin/python3 gen_firbench_tables.py            (regenerate both headers + print report)
        /usr/bin/python3 gen_firbench_tables.py --check    (regenerate in memory, byte-compare with disk; exit 1 on diff)
All numbers printed are [L2 host] (numpy); nothing here is a board number.
"""
import os
import re
import sys
import zlib
import argparse

sys.dont_write_bytecode = True          # do not drop __pycache__ into the frozen sim directories
import numpy as np                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FBDIR = os.path.abspath(os.path.join(HERE, ".."))                       # sprint7/dsp/firbench
ROOT = os.path.abspath(os.path.join(FBDIR, "..", "..", ".."))           # repo root
DESIGN_DIR = os.path.join(ROOT, "sprint7", "sim", "side30", "fir")
CSV127 = os.path.join(DESIGN_DIR, "s7_fir_coeffs_127tap.csv")
CHIRP_H = os.path.join(ROOT, "sprint4", "dsp", "core_only", "bench", "chirp_input.h")
DOLPH_H = os.path.join(ROOT, "sprint4", "dsp", "fira", "dolph_w8_q15.h")
OUT_COEF = os.path.join(FBDIR, "fb_coeffs.h")
OUT_GOLD = os.path.join(FBDIR, "fb_goldens.h")

TAPS = (63, 127, 255)          # tiers 64 / 128 / 256 (odd type-I length, the design's own TAPS)
NCH = 8
FRAME = 64
NFR = 1024
NS = FRAME * NFR
FS = 48000.0
QB = 15
I32MIN, I32MAX = -(1 << 31), (1 << 31) - 1


def md5(path):
    import hashlib
    with open(path, "rb") as fp:
        return hashlib.md5(fp.read()).hexdigest()


def crc32_i32(a):
    return zlib.crc32(np.asarray(a, dtype="<i4").tobytes()) & 0xFFFFFFFF


def read_chirp():
    txt = open(CHIRP_H, "r").read()
    body = txt.split("CHIRP_INPUT[CHIRP_INPUT_N] = {", 1)[1].split("};", 1)[0]
    v = np.array([int(s) for s in re.findall(r"-?\d+", body)], dtype=np.int64)
    assert v.size == NS, v.size
    return v


def read_dolph_q15():
    txt = open(DOLPH_H, "r").read()
    body = txt.split("g_dolph_w8_q15[DOLPH_W8_NCH] = {", 1)[1].split("};", 1)[0]
    w = [int(m.group(1)) for m in (re.match(r"\s*(-?\d+)\s*,", ln) for ln in body.splitlines()) if m]
    assert len(w) == NCH, w
    return np.array(w, dtype=np.int64)


def read_csv127_v1():
    h = np.zeros((NCH, 127))
    seen = 0
    for ln in open(CSV127, "r").read().splitlines()[1:]:
        f = ln.split(",")
        if f[0] == "V1" and int(f[1]) == 127:
            h[int(f[2])] = [float(s) for s in f[3:]]
            seen += 1
    assert seen == NCH
    return h


def design_v1(taps):
    """Re-run the frozen design code path in memory (read-only import; main() not called, no file written)."""
    sys.path.insert(0, DESIGN_DIR)
    import s7_fir_robust_design as D  # noqa: E402
    rng = np.random.default_rng(D.SEED)
    sig2g = D.sigma2_gain(rng)
    wraw, qs, brob, ra = D.perbin_design(D.CFG["V1"], sig2g)
    ws = D.smooth_logf(wraw, D.SMOOTH_FWHM_OCT)
    out = {}
    for L in taps:
        _, h = D.fit_fir(ws, qs, brob, L, ra, D.FIT_GAMMA)
        out[L] = h
    return out, float(D.d20_axis_level()), sig2g


def quantize_sym(h, G):
    """Q15-in-int32, round-half-up on the first half, mirrored -> exactly symmetric."""
    L = h.shape[1]
    M = (L - 1) // 2
    c = np.zeros((NCH, L), dtype=np.int64)
    half = np.floor(h[:, :M + 1] * G * (1 << QB) + 0.5).astype(np.int64)
    c[:, :M + 1] = half
    c[:, M + 1:] = half[:, :M][:, ::-1]
    full = np.floor(h * G * (1 << QB) + 0.5).astype(np.int64)
    asym = int(np.count_nonzero(full != c))            # taps where independent rounding would break symmetry
    return c, asym


def fir_q31(x, c):
    """Whole-signal reference: y[n] = sat32((sum_k c[k] x[n-k]) >> 15), x[n<0] = 0. Returns (y int64, nsat)."""
    acc = np.convolve(x, c)[:NS]                       # exact int64 (|acc| < 2^48 here)
    y = np.right_shift(acc, QB)                        # arithmetic shift == floor, same as C >> on int64
    nsat = int(np.count_nonzero((y > I32MAX) | (y < I32MIN)))
    return np.clip(y, I32MIN, I32MAX), nsat, int(np.max(np.abs(acc)))


def band_window():
    """Frame window where the log chirp (20 Hz -> 11 kHz over 65536 samples, gen_chirp_input.c) is in 0.7-5.2 kHz."""
    lr = np.log(11000.0 / 20.0)
    s0 = int(np.ceil(np.log(700.0 / 20.0) / lr * NS))
    s1 = int(np.floor(np.log(5200.0 / 20.0) / lr * NS))
    return s0 // FRAME, s1 // FRAME                   # inclusive frame range


def c_array(name, c):
    L = c.shape[1]
    lines = [f"static const int32_t {name}[FB_NCH * {L}] = {{"]
    for ch in range(NCH):
        lines.append(f"    /* channel {ch} (pair {{{ch},{15 - ch}}}) */")
        row = [str(int(v)) for v in c[ch]]
        for i in range(0, L, 10):
            lines.append("    " + ", ".join(row[i:i + 10]) + ",")
    lines.append("};")
    return "\n".join(lines)


def build(report):
    x = read_chirp()
    wq = read_dolph_q15()
    h127_csv = read_csv127_v1()
    hd, G, sig2g = design_v1(TAPS)

    # reproducibility of the 127 set: re-derived vs frozen CSV
    d127 = float(np.max(np.abs(hd[127] - h127_csv)))
    rel127 = d127 / float(np.max(np.abs(h127_csv)))
    src = {63: hd[63], 127: h127_csv, 255: hd[255]}
    coefs, info = {}, {}
    for L in TAPS:
        c, asym = quantize_sym(src[L], G)
        coefs[L] = c
        info[L] = dict(asym=asym, maxc=int(np.max(np.abs(c))), l1max=int(np.max(np.abs(c).sum(1))))
    c127_re, _ = quantize_sym(hd[127], G)
    q127_diff = int(np.count_nonzero(c127_re != coefs[127]))

    chirp_crc = crc32_i32(x)
    xmax = int(np.max(np.abs(x)))
    gold, gold_nsat, gold_accmax, yreal = {}, {}, {}, {}
    for L in TAPS:
        g, ns, am, yy = [], 0, 0, []
        for ch in range(NCH):
            y, nsat, amax = fir_q31(x, coefs[L][ch])
            g.append(crc32_i32(y)); ns += nsat; am = max(am, amax); yy.append(y)
        gold[L], gold_nsat[L], gold_accmax[L], yreal[L] = g, ns, am, yy

    # FG2 placeholders (same group delay M): Dolph-20 table x delta, uniform G/16 x delta
    f0, f1 = band_window()
    ws0, ws1 = f0 * FRAME, (f1 + 1) * FRAME
    ph = {}
    for L in TAPS:
        M = (L - 1) // 2
        uni = int(np.floor(G / 16.0 * (1 << QB) + 0.5))
        rows = []
        for kind, wv in (("dolph20_x_delta", wq), ("uniform_G16_x_delta", np.full(NCH, uni, dtype=np.int64))):
            for ch in range(NCH):
                cph = np.zeros(L, dtype=np.int64)
                cph[M] = wv[ch]
                y, _, _ = fir_q31(x, cph)
                crc_full = crc32_i32(y)
                yr = yreal[L][ch]
                d = np.abs(yr[ws0:ws1] - y[ws0:ws1])
                band_db = 20.0 * np.log10(max(float(d.max()), 1.0) / float(np.max(np.abs(yr[ws0:ws1]))))
                crc_band_real = crc32_i32(yr[ws0:ws1])
                crc_band_ph = crc32_i32(y[ws0:ws1])
                rows.append((kind, ch, crc_full, crc_full != gold[L][ch], crc_band_ph != crc_band_real, band_db,
                             int(2 * wv.sum())))
        ph[L] = rows
    sum2 = {L: [int(2 * coefs[L][:, (L - 1) // 2].sum()), int(2 * coefs[L].sum())] for L in TAPS}

    # ---------------- headers ----------------
    hdr = []
    hdr.append("/* fb_coeffs.h -- GENERATED by sprint7/dsp/firbench/tools/gen_firbench_tables.py. DO NOT EDIT.")
    hdr.append(" * S7 per-channel FIR compute bench (DEC-S7-SIDE30-01 (3)); ASCII-only (CCES SHARC).")
    hdr.append(" * V1 robust design, 8 channels (channel c drives the series pair {c,15-c}), type-I linear phase,")
    hdr.append(" *   tiers 64/128/256 = 63/127/255 REAL taps (odd, exactly symmetric integers; group delay 31/63/127).")
    hdr.append(" * Format = the project FIRA fixed-point path (fira_tree.c): Q15 value in an int32 word (may exceed")
    hdr.append(" *   32767: max |c| below), SIGNED_INTEGER exact MAC, core postscale y = sat32(acc >> 15).")
    hdr.append(f" * Equal on-axis gain to the Dolph-20 table (max weight 1.0): G = 2*sum(w8)/max(w8) = {G:.12f}.")
    hdr.append(" * Sources: 127 = V1 rows of sprint7/sim/side30/fir/s7_fir_coeffs_127tap.csv (md5 "
               f"{md5(CSV127)});")
    hdr.append(" *   63/255 = the same design code path (s7_fir_robust_design.py V1, seed 20260926) re-run in memory.")
    hdr.append(" * NOT a product coefficient set: bench-only (compute + bit-exact gate), [L2] design, no L1 behind it.")
    hdr.append(" */")
    hdr.append("#ifndef S7_FB_COEFFS_H")
    hdr.append("#define S7_FB_COEFFS_H")
    hdr.append("#include <stdint.h>")
    hdr.append("")
    hdr.append("#define FB_NCH        8")
    hdr.append("#define FB_NTAPSET    3")
    hdr.append("#define FB_TAPS_0     63     /* tier  64 */")
    hdr.append("#define FB_TAPS_1     127    /* tier 128 = the correctness set (V1-128) */")
    hdr.append("#define FB_TAPS_2     255    /* tier 256 */")
    hdr.append("#define FB_MAXTAPS    255")
    hdr.append("#define FB_COEF_QBITS 15")
    for i, L in enumerate(TAPS):
        hdr.append(f"#define FB_COEF_CRC_{i} 0x{crc32_i32(coefs[L].reshape(-1)):08X}u   /* CRC32 of FB_COEF_T{L} bytes (LE int32) */")
    hdr.append(f"#define FB_CHIRP_CRC  0x{chirp_crc:08X}u   /* CRC32 of the frozen CHIRP_INPUT[65536] (LE int32) */")
    for i, L in enumerate(TAPS):
        hdr.append(f"/* T{L}: max|c| = {info[L]['maxc']}, max per-channel sum|c| = {info[L]['l1max']} */")
    hdr.append("")
    for L in TAPS:
        hdr.append(c_array(f"FB_COEF_T{L}", coefs[L]))
        hdr.append("")
    hdr.append("#endif /* S7_FB_COEFFS_H */")
    coef_txt = "\n".join(hdr) + "\n"

    g = []
    g.append("/* fb_goldens.h -- GENERATED by sprint7/dsp/firbench/tools/gen_firbench_tables.py. DO NOT EDIT.")
    g.append(" * Per-channel golden CRC32 (IEEE 802.3, LE int32 bytes == bench_harness.c crc32_buf) of the Q31 output")
    g.append(" *   y_c[n] = sat32((sum_k FB_COEF_T<L>[c][k] * x[n-k]) >> 15) over the WHOLE frozen chirp (65536 samples")
    g.append(" *   = 1024 frames x 64, zero initial state), x = CHIRP_INPUT (sprint4/dsp/core_only/bench/chirp_input.h, md5")
    g.append(f" *   {md5(CHIRP_H)}). Track 1 = numpy int64 (this generator); track 2 = host/fb_ref_host.c (C loops).")
    g.append(" * The bench must reproduce EVERY channel of EVERY path; any miss voids that path's cycle numbers.")
    g.append(" * [L2 host]; placeholder sets (Dolph-20 x delta, uniform x delta) MISS every entry (host FG2 proof).")
    g.append(" */")
    g.append("#ifndef S7_FB_GOLDENS_H")
    g.append("#define S7_FB_GOLDENS_H")
    g.append("#include <stdint.h>")
    g.append("#define FB_GOLDEN_NFR 1024")
    g.append("static const uint32_t FB_GOLDEN_CRC[3][8] = {")
    for L in TAPS:
        g.append("    { " + ", ".join(f"0x{v:08X}u" for v in gold[L]) + " },   /* " + str(L) + " taps */")
    g.append("};")
    g.append("#endif /* S7_FB_GOLDENS_H */")
    gold_txt = "\n".join(g) + "\n"

    if report:
        print("==== gen_firbench_tables.py report [L2 host, numpy] ====")
        print(f"inputs: chirp md5 {md5(CHIRP_H)} | dolph md5 {md5(DOLPH_H)} | csv127 md5 {md5(CSV127)}")
        print(f"design load sigma^2_gain = {sig2g:.5f} (seed 20260926, same as the design log); G = {G:.9f}")
        print(f"127-tap reproducibility: max|h_rederived - h_csv| = {d127:.3e} (rel {rel127:.3e}); "
              f"quantised taps that differ = {q127_diff} (CSV is the source of the 127 set)")
        for L in TAPS:
            print(f"T{L}: asym-rounding taps (independent rounding) = {info[L]['asym']}, max|c| = {info[L]['maxc']}"
                  f" ({info[L]['maxc'] / 32768.0:.4f}), max sum|c| = {info[L]['l1max']};"
                  f" max|acc| = {gold_accmax[L]} (2^{np.log2(gold_accmax[L]):.2f}); saturations = {gold_nsat[L]}")
        print(f"chirp: max|x| = {xmax} ({xmax / 2.0 ** 31:.4f} FS), CRC32 0x{chirp_crc:08X};"
              f" 0.7-5.2 kHz window = frames {f0}..{f1} (samples {ws0}..{ws1 - 1})")
        for L in TAPS:
            print(f"GOLDEN T{L}: " + " ".join(f"{v:08X}" for v in gold[L]))
        print("sum_c 2c_c (centre tap / all taps): " + ", ".join(f"T{L}: {sum2[L][0]}/{sum2[L][1]}" for L in TAPS)
              + f" | Dolph-20 x delta: {int(2 * wq.sum())} | uniform x delta: {16 * int(np.floor(G / 16.0 * 32768 + 0.5))}")
        print("FG2 placeholder proof (must MISS every golden; band = 0.7-5.2 kHz window only):")
        allmiss = True
        for L in TAPS:
            for kind in ("dolph20_x_delta", "uniform_G16_x_delta"):
                rows = [r for r in ph[L] if r[0] == kind]
                miss = sum(1 for r in rows if r[3]); bmiss = sum(1 for r in rows if r[4])
                allmiss = allmiss and miss == NCH and bmiss == NCH
                print(f"  T{L} {kind:20s}: full-CRC miss {miss}/8, band-CRC miss {bmiss}/8, band max|diff|/max|y| "
                      + " ".join(f"{r[5]:+.1f}" for r in rows) + " dB")
        print(f"FG2 verdict: {'ALL placeholders MISS (expected)' if allmiss else 'PLACEHOLDER HIT A GOLDEN -> BLOCKER'}")
    return coef_txt, gold_txt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="byte-compare regenerated headers with the files on disk")
    a = ap.parse_args()
    coef_txt, gold_txt = build(report=True)
    if a.check:
        ok = True
        for path, txt in ((OUT_COEF, coef_txt), (OUT_GOLD, gold_txt)):
            same = os.path.exists(path) and open(path, "r").read() == txt
            print(f"[check] {os.path.basename(path)}: {'IDENTICAL' if same else 'DIFFERS'}")
            ok = ok and same
        sys.exit(0 if ok else 1)
    for path, txt in ((OUT_COEF, coef_txt), (OUT_GOLD, gold_txt)):
        with open(path, "w") as fp:
            fp.write(txt)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
