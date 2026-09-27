#!/usr/bin/env python3
"""
gen_m2_wtbl.py -- S7-SIDE30 (DEC-S7-SIDE30-01 (2)(4)): generate the NON-frozen runtime-selectable
weight tables for M2_WTBL_SEL  ->  sprint6/dsp/audio/m1_cces_project/src/m2_wtbl_q15.h

Rows (sel = row + 1; sel 0 is ALWAYS the frozen g_dolph_w8_q15 = Dolph -20, not duplicated here):
    sel 1 = Dolph-Chebyshev -25 dB, sel 2 = -30 dB, sel 3 = -35 dB   (N=16, 8 centre-symmetric pairs)
    sel 4 = robust-sector RS-A, sel 5 = robust-sector RS-B            (added 2026-09-28, definition at RS_SPECS)
    Rows are APPEND-ONLY: sel 1..3 keep their numbers so earlier runbook readings stay comparable.

Iron rule 7 (dual track), same discipline as the frozen table's generator sprint4/dsp/fira/gen_dolph_w8.py:
  Dolph rows:
    track 1 = scipy.signal.windows.chebwin(16, sll) / max
    track 2 = Barbiere/Stegen closed-form Dolph synthesis (factorials only; re-implemented here with the SLL
              as a parameter, same formula as gen_dolph_w8.py:track2_recurrence(), which is hard-wired to 20 dB)
  Robust-sector rows (the table IS the definition in the RS block below; both tracks evaluate it exactly):
    track 1 = Gauss-Legendre quadrature of the sector integrals (numpy) + LU solve; sigma_g^2 in closed form
    track 2 = Jacobi-Anger Bessel series of the same integrals (scipy.special.jv) + Cholesky solve;
              sigma_g^2 by numerical quadrature (scipy.integrate.quad)
  Q15 = round(w * 32768) (1.0 -> 32768, same scale/container as DOLPH_W8_ONE). Tracks must agree bit-exactly;
  RS rows additionally: |w1 - w2| < 1e-10 and every value >= 1e-6 LSB away from a rounding tie.
ANCHOR (runs first, SystemExit on failure): this generator reproduces the FROZEN D20 Q15 table bit-exactly.
GAP-SAT premise: every value <= 32768 (<= 1.0), max = 32768 at the centre channel.
Drive premise (all rows): every weight <= the frozen D20 weight of the SAME channel, so no channel is driven
harder than today's firmware drives it (SystemExit otherwise).
L-grade: tables [L2/dual-track desktop]; metrics [L2 ideal far-field isotropic model] (s7_common.py).
Usage:  /usr/bin/python3 gen_m2_wtbl.py [--check | --labels]   (--check = regenerate in memory and diff against
        the header, or against $WTBL_HDR if set; --labels = print sel:label pairs for the runbook check)
"""
import os
import re
import sys
from math import factorial

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "sprint7", "sim", "acoustic"))
import s7_common as S  # noqa: E402

FROZEN_H = os.path.join(REPO, "sprint4", "dsp", "fira", "dolph_w8_q15.h")
OUT_H = os.path.join(REPO, "sprint6", "dsp", "audio", "m1_cces_project", "src", "m2_wtbl_q15.h")
SLLS = [25.0, 30.0, 35.0]
N = 16
M = N // 2

# ---- robust-sector (RS) rows (S7-SIDE30).
# RS-A (sel 4): approved by the CTO 2026-09-27 ("我同意，你依次干吧", reply to the PM proposal to add ONE robust-sector
#   table as an extra M2_WTBL_SEL row through the critic gate).
# RS-B (sel 5): a SECOND row ADDED BY THE PM, pending CTO review (PM 拟，待 CTO 过目); its selection rule was set by the
#   PM AFTER an exploratory scan (logged in s7_alt_tables.log). Removal path: sprint2/docs/decisions_log.md 2026-09-28.
# Design study and selection rule: sprint7/sim/side30/s7_alt_tables.py / S7_SIDE30_ANALYSIS.md sec 3.1.
# Canonical definition (pair space c = 0..7 edge->centre, x_c = (c - 7.5) d, a_c(th,f) = 2 cos(k x_c sin th)):
#   F7 = the 7 DEC-S7-SIDE30-01 bands 1k..4k, 31 log-spaced points per 1/3 octave
#   R(t1,t2,f) = 1/(t2-t1) * integral_t1^t2 a a^T dth          (uniform in angle, EXACT integral)
#   Q = mean_{f in F7} [ R(ths,90,f) + eta * R(thm,ths,f) + 2 (sigma_g^2 + k^2 sigma_x^2) I ]
#   W = Q^-1 1,  w = W / max(W),  Q15 = round(32768 w)
# = error-loaded side sector + eta x IDEAL mid sector (the mid-sector term carries no error load), over 1-4 kHz at
# fixed on-axis gain: the side term is the expected side power for i.i.d. driver errors (mean-performance robust
# design, Van Trees 2002 eq. 2.208 / Gilbert-Morgan 1955) with the position load taken at sin^2(th) = 1; load = the
# project U-flat tolerance (+/-1 dB, +/-5 deg, +/-0.5 mm), same load as s7_fir_robust_design.py q_matrix().
RS_SPECS = (  # (label, ths, thm, eta, note)
    ("RS-A", 60.0, 35.0, 0.1, "side-first; = the robust-sector table proposed to the CTO, formal exact-integral form"),
    ("RS-B", 60.0, 30.0, 1.0, "PM addition pending CTO review; 8 JY/T points >= Dolph-35 [L2 ideal], i.e. on par"),
)
RS_BANDS = (1000.0, 1250.0, 1600.0, 2000.0, 2500.0, 3150.0, 4000.0)
RS_F7 = np.concatenate([np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 31) for fc in RS_BANDS])
RS_SIG_X2 = (0.5e-3) ** 2 / 3.0


def track1(sll):
    from scipy.signal.windows import chebwin
    w = chebwin(N, sll)
    return (w / w.max())[:M]                       # edge (c=0) .. centre (c=7)


def track2(sll):
    R = 10.0 ** (sll / 20.0)
    x0 = np.cosh(np.arccosh(R) / (N - 1))
    a = np.zeros(M)
    for n in range(1, M + 1):
        s = 0.0
        for q in range(n, M + 1):
            s += ((-1) ** (M - q)) * factorial(q + M - 2) * (x0 ** (2 * q - 1)) / (
                factorial(q - n) * factorial(q + n - 1) * factorial(M - q))
        a[n - 1] = s
    w8 = np.abs(a[::-1])
    return w8 / w8.max()


def _rs_xc():
    return (np.arange(M) - (N - 1) / 2.0) * S.D                  # x_c, c = 0..7 (pair {c, 15-c})


def rs_sig2g_closed():
    b, p0 = np.log(10.0) / 10.0, np.deg2rad(5.0)                 # a ~ U(+/-1 dB), phi ~ U(+/-5 deg)
    return float(np.sinh(b) / b - 2.0 * (np.sinh(b / 2) / (b / 2)) * (np.sin(p0) / p0) + 1.0)


def rs_sig2g_quad():
    from scipy.integrate import quad
    e_p = quad(lambda a: 10 ** (a / 10), -1, 1)[0] / 2           # E|g|^2
    e_a = quad(lambda a: 10 ** (a / 20), -1, 1)[0] / 2           # E 10^(a/20)
    p0 = np.deg2rad(5.0)
    e_c = quad(np.cos, -p0, p0)[0] / (2 * p0)                   # E cos(phi)
    return float(e_p - 2 * e_a * e_c + 1)


def rs_track1(ths, thm, eta):
    """Gauss-Legendre (64 nodes per sector) + numpy LU."""
    xc, sg = _rs_xc(), rs_sig2g_closed()
    xg, wg = np.polynomial.legendre.leggauss(64)

    def rmean(t1, t2, k):
        t1, t2 = np.deg2rad(t1), np.deg2rad(t2)
        th = 0.5 * (t2 - t1) * xg + 0.5 * (t2 + t1)
        a = 2.0 * np.cos(k * np.outer(np.sin(th), xc))           # (64, 8)
        return (a.T * (0.5 * wg)) @ a                            # (1/(t2-t1)) * integral
    Q = np.zeros((M, M))
    for f in RS_F7:
        k = 2 * np.pi * f / S.C
        Q += rmean(ths, 90.0, k) + eta * rmean(thm, ths, k) + 2.0 * (sg + k * k * RS_SIG_X2) * np.eye(M)
    W = np.linalg.solve(Q / len(RS_F7), np.ones(M))
    return W / W.max()


def rs_track2(ths, thm, eta):
    """Jacobi-Anger: cos(Z sin th) = J0(Z) + 2 sum_m J_2m(Z) cos(2m th), integrated term by term + scipy Cholesky.
    a_i a_j = 2 cos((z_i - z_j) sin th) + 2 cos((z_i + z_j) sin th),  z = k x."""
    from scipy.special import jv
    from scipy.linalg import cho_factor, cho_solve
    xc, sg = _rs_xc(), rs_sig2g_quad()
    m = np.arange(1, 121)

    def meancos(Z, t1, t2):
        t1, t2 = np.deg2rad(t1), np.deg2rad(t2)
        s = (np.sin(2 * m * t2) - np.sin(2 * m * t1)) / (2 * m)
        return jv(0, Z) + 2.0 * (jv(2 * m[None, None, :], Z[..., None]) * s).sum(-1) / (t2 - t1)

    def rmean(t1, t2, k):
        z = k * xc
        return 2.0 * meancos(z[:, None] - z[None, :], t1, t2) + 2.0 * meancos(z[:, None] + z[None, :], t1, t2)
    Q = np.zeros((M, M))
    for f in RS_F7:
        k = 2 * np.pi * f / S.C
        Q += rmean(ths, 90.0, k) + eta * rmean(thm, ths, k) + 2.0 * (sg + k * k * RS_SIG_X2) * np.eye(M)
    W = cho_solve(cho_factor(Q / len(RS_F7)), np.ones(M))
    return W / W.max()


def q15(w):
    q = np.round(np.asarray(w) * 32768.0).astype(np.int64)
    assert q.max() <= 32768 and q.min() >= 0
    return q


def frozen_d20():
    t = open(FROZEN_H, encoding="utf-8").read()
    body = t[t.index("g_dolph_w8_q15[DOLPH_W8_NCH] = {"):]
    body = body[body.index("{") + 1: body.index("};")]
    vals = [int(m) for m in re.findall(r"^\s*(\d+),", body, flags=re.M)]
    assert len(vals) == 8, vals
    return np.array(vals, dtype=np.int64)


def metrics(q8):
    w16 = S.expand16(np.asarray(q8, float) / 32768.0)
    ref = S.expand16(frozen_d20().astype(float) / 32768.0)

    def band_att90(fc):
        fs = np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 41)
        p0 = np.mean([abs(S.af_complex([0.0], f, w16)[0]) ** 2 for f in fs])
        p9 = np.mean([abs(S.af_complex([90.0], f, w16)[0]) ** 2 for f in fs])
        return 10 * np.log10(p0 / p9)
    P1k = S.pattern_db(1000.0, w16)
    return {
        "BW1k": S.bw_full(P1k), "SLL": S.peak_sll_interior(P1k),
        "att30_500": S.att_db(30.0, 500.0, w16), "att30_1k": S.att_db(30.0, 1000.0, w16),
        "att90b_1k": band_att90(1000.0), "att90b_2k": band_att90(2000.0), "att90b_4k": band_att90(4000.0),
        "onaxis_vs_d20_dB": 20 * np.log10(w16.sum() / ref.sum()), "WNGn": S.wng_norm_db(w16),
    }


def build():
    """rows = [(label, q15 int64[8], metrics, row_comment)], in sel order 1..M2_WTBL_NEXTRA."""
    S.assert_anchors(verbose=False)
    fz = frozen_d20()
    g20_1, g20_2 = q15(track1(20.0)), q15(track2(20.0))
    if not (np.array_equal(g20_1, fz) and np.array_equal(g20_2, fz)):
        raise SystemExit(f"ANCHOR FAIL: generator D20 {g20_1.tolist()} / {g20_2.tolist()} != frozen {fz.tolist()}")
    rows = []
    for sll in SLLS:
        a, b = q15(track1(sll)), q15(track2(sll))
        if not np.array_equal(a, b):
            raise SystemExit(f"DUAL-TRACK FAIL at {sll} dB: scipy {a.tolist()} vs closed-form {b.tolist()}")
        if a[-1] != 32768:
            raise SystemExit(f"centre weight != 32768 at {sll} dB")
        rows.append((f"D{int(sll)}", a, metrics(a), f"Dolph-Chebyshev -{int(sll)} dB"))
    s1, s2 = rs_sig2g_closed(), rs_sig2g_quad()
    if abs(s1 - s2) > 1e-12:
        raise SystemExit(f"DUAL-TRACK FAIL sigma_g^2: closed {s1!r} vs quad {s2!r}")
    for lab, ths, thm, eta, note in RS_SPECS:
        w1, w2 = rs_track1(ths, thm, eta), rs_track2(ths, thm, eta)
        dmax = float(np.abs(w1 - w2).max())
        a, b = q15(w1), q15(w2)
        tie = float(np.min(np.abs(w1 * 32768.0 - np.floor(w1 * 32768.0) - 0.5)))
        if dmax > 1e-10 or not np.array_equal(a, b):
            raise SystemExit(f"DUAL-TRACK FAIL {lab}: max|w1-w2|={dmax:.3e}, {a.tolist()} vs {b.tolist()}")
        if tie < 1e-6:
            raise SystemExit(f"{lab}: a value sits {tie:.2e} LSB from a rounding tie -- Q15 not robust")
        if a[-1] != 32768:
            raise SystemExit(f"{lab}: max weight is not at the centre channel ({a.tolist()})")
        rows.append((lab, a, metrics(a),
                     f"robust-sector {lab}: {ths:.0f}-90 deg + {eta:g} x {thm:.0f}-{ths:.0f} deg, 1-4 kHz, error-loaded; {note}"))
        RS_TRACE.append((lab, dmax, tie))
    jyt = [(30.0, 500.0), (90.0, 500.0), (30.0, 1000.0), (90.0, 1000.0), (30.0, 2000.0), (90.0, 2000.0),
           (30.0, 4000.0), (90.0, 4000.0)]                        # the 8 evaluable JY/T table-9 points
    qd = {lab: q for lab, q, _m, _c in rows}
    jd = [S.att_db(th, f, S.expand16(qd["D35"] / 32768.0)) for th, f in jyt]
    jb = [S.att_db(th, f, S.expand16(qd["RS-B"] / 32768.0)) for th, f in jyt]
    if any(b < a for a, b in zip(jd, jb)):
        raise SystemExit(f"RS-B CLAIM FAIL: some JY/T point below Dolph-35: {jb} vs {jd}")
    for lab, q, _m, _c in rows:
        if np.any(q > fz):
            raise SystemExit(f"DRIVE PREMISE FAIL {lab}: some weight exceeds the frozen D20 weight of that channel "
                             f"({q.tolist()} vs {fz.tolist()})")
    return fz, rows


RS_TRACE = []


def render(fz, rows):
    fm = metrics(fz)
    L = []
    L.append("/**")
    L.append(" * @file    m2_wtbl_q15.h")
    L.append(" * @brief   S7-SIDE30: runtime-selectable broadside weight tables for M2_WTBL_SEL (NOT frozen).")
    L.append(" *")
    L.append(" * GENERATED by sprint7/dsp/wtbl/gen_m2_wtbl.py -- DO NOT EDIT BY HAND (same-source discipline;")
    L.append(" * `gen_m2_wtbl.py --check` diffs this file against a fresh generation).")
    L.append(" * Basis: DEC-S7-SIDE30-01 (2)(4) (CTO 2026-09-26 agreed to reopen D6 and to firmware changes; that THIS")
    L.append(" *        package falls under it is a PM reading pending CTO review, DEC (4)) and")
    L.append(" *        sprint7/docs/S7_SIDE30_ANALYSIS.md sec 3. Used ONLY under #ifdef M2_WTBL_SEL.")
    L.append(" *        Row sel 4 (robust-sector RS-A): approved by the CTO 2026-09-27 (reply quoted verbatim in")
    L.append(" *        sprint2/docs/decisions_log.md, S7 entry 2026-09-28). Row sel 5 (RS-B): ADDED BY THE PM, pending")
    L.append(" *        CTO review; its selection rule was set after an exploratory scan. ANALYSIS sec 3.1.")
    L.append(" *")
    L.append(" * sel 0 = the FROZEN g_dolph_w8_q15 (Dolph -20, sprint4/dsp/fira/dolph_w8_q15.h) -- NOT duplicated here.")
    L.append(" * sel k (k=1..M2_WTBL_NEXTRA) = g_m2_wtbl_q15[k-1]. Index c = channel = pair {c,15-c}, edge(0)->centre(7),")
    L.append(" * exactly like the frozen table. Q15 scale 1.0 = 32768 (== DOLPH_W8_ONE); all values <= 32768 (GAP-SAT ok)")
    L.append(" * and every value <= the frozen D20 value of the same channel (no channel driven harder than sel 0).")
    L.append(" * Dual track (iron rule 7), bit-identical Q15: Dolph rows = scipy chebwin vs Barbiere closed form;")
    L.append(" * robust-sector rows = Gauss-Legendre quadrature + LU vs Jacobi-Anger Bessel series + Cholesky.")
    L.append(" * Generator anchor: reproduces the frozen D20 table bit-exactly. [L2/dual-track desktop]")
    L.append(" *")
    L.append(" * Ideal far-field metrics [L2, isotropic point-source model s7_common.py; NOT board/acoustic readings]:")
    L.append(" *   table  BW(-6)@1k  SLL    att30@500  att30@1k  att90 band-avg 1k/2k/4k   on-axis vs D20  WNGn")

    def row(name, m):
        return (f" *   {name:5s}  {m['BW1k']:6.2f} deg {m['SLL']:6.2f}  {m['att30_500']:6.2f}   {m['att30_1k']:6.2f}   "
                f"{m['att90b_1k']:5.1f}/{m['att90b_2k']:5.1f}/{m['att90b_4k']:5.1f}   {m['onaxis_vs_d20_dB']:+6.2f} dB  "
                f"{m['WNGn']:+5.2f}")
    L.append(row("D20*", fm))
    for lab, _q, m, _c in rows:
        L.append(row(lab, m))
    L.append(" *   (* D20 = frozen sel 0, listed for reference only)")
    ma = [m for lab, _q, m, _c in rows if lab == "RS-A"][0]
    L.append(f" * JY/T grade-2 (locked PRD floor) is 3 dB at 500/30 deg and 15 dB at 1k/30 deg; RS-A clears them by only"
             f" {ma['att30_500'] - 3:+.2f} /")
    L.append(f" * {ma['att30_1k'] - 15:+.2f} dB [L2 ideal] -> RS-A is a MEASUREMENT row (how far a side-first fixed table"
             f" goes on the real")
    L.append(" * array), not a product candidate. RS-B: each of the 8 evaluable JY/T points >= Dolph-35 [L2 ideal,")
    L.append(" * single frequency, asserted by the generator; thinnest +0.03 dB at 500/30 deg, i.e. on par with D35].")
    L.append(" * GATING (critic R2 MAJOR-3b): on-board A/B only AFTER polarity QA has measured the channel->position")
    L.append(" * map and the CTO D8 ruling; a deeper table on a mis-mapped array tells you nothing. Table choice waits")
    L.append(" * for the per-driver spread measurement (critic R2 MAJOR-3c).")
    L.append(" */")
    L.append("#ifndef ITC_M2_WTBL_Q15_H")
    L.append("#define ITC_M2_WTBL_Q15_H")
    L.append("")
    L.append("#include <stdint.h>")
    L.append("")
    L.append(f"#define M2_WTBL_NEXTRA  {len(rows)}   /* extra tables beyond the frozen sel-0 table */")
    L.append("")
    L.append("static const int32_t g_m2_wtbl_q15[M2_WTBL_NEXTRA][8] = {")
    for k, (lab, q, _m, cmt) in enumerate(rows):
        L.append(f"    {{ {', '.join(f'{v:5d}' for v in q)} }},   /* sel {k + 1}: {cmt} */")
    L.append("};")
    L.append("")
    L.append("#endif /* ITC_M2_WTBL_Q15_H */")
    return "\n".join(L) + "\n"


def main():
    fz, rows = build()
    if "--labels" in sys.argv:                     # sel:label list, compared by run_wtbl_checks.sh with the runbook
        print(" ".join([f"0:D20"] + [f"{k + 1}:{lab}" for k, (lab, _q, _m, _c) in enumerate(rows)]))
        return
    txt = render(fz, rows)
    if not txt.isascii():
        raise SystemExit("ASCII FAIL: the generated header must be ASCII-only (CCES target, dsp-algorithm skill A6)")
    if "--check" in sys.argv:
        target = os.environ.get("WTBL_HDR", OUT_H)   # falsifier runs point this at a doctored copy
        cur = open(target, encoding="utf-8").read()
        if cur != txt:
            raise SystemExit(f"CHECK FAIL: {os.path.basename(target)} differs from a fresh generation")
        print("CHECK PASS: m2_wtbl_q15.h == fresh generation")
    else:
        open(OUT_H, "w", encoding="utf-8").write(txt)
        print("wrote", os.path.relpath(OUT_H, REPO))
    print("anchor: generator D20 == frozen", fz.tolist(), " sum", int(fz.sum()))
    print(f"sigma_g^2 closed {rs_sig2g_closed():.12f} / quad {rs_sig2g_quad():.12f}")
    for lab, dmax, tie in RS_TRACE:
        print(f"{lab}: max|w_track1 - w_track2| = {dmax:.2e}, nearest rounding tie {tie:.4f} LSB")
    for k, (lab, q, m, _c) in enumerate(rows):
        print(f"sel {k + 1} {lab:5s} Q15 {q.tolist()}  sum {int(q.sum())}  "
              + "  ".join(f"{kk}={v:.3f}" for kk, v in m.items()))


if __name__ == "__main__":
    main()
