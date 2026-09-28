#!/usr/bin/env python3
"""critic R3g -- independent checks of the LPX hybrid (own code; reads only the STORED taps/gains CSVs and the
frozen D20 / FIR V1 coefficient CSVs; imports nothing from the PM's modules).
Sections: (1) bank: PR / symmetry / zero-phase / LR4 fit / topology vs X3; (2) headroom; (3) drive premise;
(4) LPX4 diagnosis; (5) compute arithmetic."""
import csv
import os
import numpy as np

REPO = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
SIDE = os.path.join(REPO, "sprint7/sim/side30")
FS = 48000.0

# ---------------- data ----------------
def load_params():
    P = {}
    with open(os.path.join(SIDE, "s7_hybrid_lpxo_params.csv")) as fp:
        rd = csv.reader(fp)
        next(rd)
        for r in rd:
            P.setdefault(r[0], {})[r[1]] = (r[2], int(r[3]), np.array([float(v) for v in r[4:]]))
    return P


def d20_w8():
    w = np.zeros(8)
    with open(os.path.join(REPO, "sprint4/dsp/fira/dolph_w8_q15.csv")) as fp:
        for r in csv.DictReader(fp):
            w[int(r["ch"])] = float(r["w_float_track1_scipy"])
    return w


def fir_v1():
    h = np.zeros((8, 127))
    with open(os.path.join(SIDE, "fir/s7_fir_coeffs_127tap.csv")) as fp:
        for r in csv.DictReader(fp):
            if r["variant"] == "V1" and int(r["taps"]) == 127:
                h[int(r["channel"])] = [float(r[f"h{i}"]) for i in range(127)]
    return h


def x3_gains():
    wk = np.zeros((3, 8))
    with open(os.path.join(SIDE, "s7_alt_algos_params.csv")) as fp:
        for r in csv.DictReader(fp):
            if r["design"] == "X3-LR4-700/1600-e0.1m35":
                wk[int(r["band_or_param"]) - 1] = [float(r[f"c{c}"]) for c in range(8)]
    return wk


W8 = d20_w8()
D20R = W8 / W8.max()
AXIS_D20 = 2 * W8.sum() / W8.max()
P = load_params()


def bank_of(name):
    p = P[name]
    lps = [p[k][2] for k in sorted(k for k in p if k.startswith("lowpass_"))]
    wk = np.array([p[k][2] for k in sorted(k for k in p if k.startswith("band_gain_"))])
    xo = [float(p[k][0]) for k in sorted(k for k in p if k.startswith("lowpass_"))]
    N = max(len(h) for h in lps)
    D = (N - 1) // 2
    pads = []
    for h in lps:
        q = (N - len(h)) // 2
        pads.append(np.concatenate([np.zeros(q), h, np.zeros(q)]))
    dl = np.zeros(N)
    dl[D] = 1.0
    bands = [pads[0]] + [pads[i] - pads[i - 1] for i in range(1, len(pads))] + [dl - pads[-1]]
    return dict(lps=lps, wk=wk, xo=xo, N=N, D=D, bands=np.array(bands), dl=dl)


def zamp(h, f, D):
    """zero-phase amplitude about index D, own DTFT: sum h[n] exp(-j w (n - D))."""
    n = np.arange(len(h)) - D
    w = 2 * np.pi * np.atleast_1d(f) / FS
    E = np.exp(-1j * np.outer(w, n))
    return E @ h


def lr4_lp(f, fc):
    f = np.minimum(np.asarray(f, float), FS / 2 - 1.0)
    t = (np.tan(np.pi * f / FS) / np.tan(np.pi * fc / FS)) ** 4
    return 1.0 / (1.0 + t)


def dense_max(h8, nfft=1 << 18):
    H = np.abs(np.fft.rfft(h8, nfft, axis=1))
    f = np.fft.rfftfreq(nfft, 1 / FS)
    i = np.unravel_index(np.argmax(H), H.shape)
    return H, f, float(H.max()), i


out = []
def log(s=""):
    print(s)
    out.append(s)


# ---------------- (1) bank ----------------
fgrid = np.linspace(0.0, FS / 2, 24001)
log("(1) BANK CHECKS (own code, stored taps)")
for name in ["LPX3-a", "LPX3-b", "LPX4-a", "LPX4-b", "LPX4-a-cap", "LPX4-b-cap"]:
    B = bank_of(name)
    pr = np.abs(B["bands"].sum(0) - B["dl"]).max()
    sym_b = max(np.abs(b - b[::-1]).max() for b in B["bands"])
    h8 = B["wk"].T @ B["bands"]
    sym_c = np.abs(h8 - h8[:, ::-1]).max()
    axis = 2 * h8.sum(0)
    ax_err = np.abs(axis - B["dl"]).max()
    wsum = np.abs(2 * B["wk"].sum(1) - 1).max()
    im = max(np.abs(zamp(b, fgrid, B["D"]).imag).max() for b in B["bands"])
    fit = [np.abs(zamp(h, fgrid, (len(h) - 1) // 2).real - lr4_lp(fgrid, fc)).max() for h, fc in zip(B["lps"], B["xo"])]
    log(f"  {name:11s} N={B['N']} D={B['D']} | PR {pr:.1e} | band sym {sym_b:.1e} | chan sym {sym_c:.1e} | "
        f"sum_c 2h_c - delta {ax_err:.1e} (|2 sum w - 1| {wsum:.1e}) | zero-phase imag {im:.1e} | LR4 fit "
        + " / ".join(f"{v:.4f}" for v in fit))
# the PR "check" is a telescoping identity: garbage low-passes still give PR ~ 0
rng = np.random.default_rng(1)
g1, g2 = rng.normal(size=127), rng.normal(size=127)
dl = np.zeros(127); dl[63] = 1
gb = [g1, g2 - g1, dl - g2]
log(f"  identity demo: random (asymmetric, non-lowpass) taps -> PR err {np.abs(sum(gb) - dl).max():.1e} (cannot fail)")

# topology: LPX bands [A1, A2-A1, 1-A2] vs X3 bands [A1*A2, (1-A1)*A2, 1-A2]
f = np.linspace(1.0, 24000.0, 47999)
A1, A2 = lr4_lp(f, 700.0), lr4_lp(f, 1600.0)
x3b = np.stack([A1 * A2, (1 - A1) * A2, 1 - A2])
lpxi = np.stack([A1, A2 - A1, 1 - A2])
d_top = np.abs(lpxi - x3b).max(1)
i_top = np.argmax(np.abs(lpxi[0] - x3b[0]))
log(f"  TOPOLOGY: ideal LPX bands minus X3 bands, max |diff| low/mid/high = "
    + " / ".join(f"{v:.4f}" for v in d_top) + f" (= A1(1-A2), max at {f[i_top]:.0f} Hz)")
for name in ["LPX3-a", "LPX3-b"]:
    B = bank_of(name)
    Ab = np.stack([zamp(b, f, B["D"]).real for b in B["bands"]])
    log(f"  {name}: real bands minus X3 bands, max |diff| low/mid/high = " + " / ".join(f"{v:.4f}" for v in np.abs(Ab - x3b).max(1))
        + " ; real bands minus ideal-LPX bands = " + " / ".join(f"{v:.4f}" for v in np.abs(Ab - lpxi).max(1)))
    # per-channel response difference vs X3 (both re-solved designs)
    wx = x3_gains()
    Wx = wx.T @ x3b
    Wl = B["wk"].T @ Ab
    fm = (f >= 891) & (f <= 4490)
    log(f"    per-channel |W_LPX - W_X3| max over all f {np.abs(Wl - Wx).max():.5f}, over 0.89-4.49 kHz {np.abs(Wl - Wx)[:, fm].max():.5f}"
        f" (|W| max {np.abs(Wx).max():.4f}); band gains max |w_LPX - w_X3| {np.abs(B['wk'] - wx).max():.5f}")

# ---------------- (2) headroom ----------------
log("\n(2) HEADROOM (own conv; squares from silence, sign(sin) squares, own pink noise; dB vs today's same channel)")


def squares():
    n = int(FS)
    s = {}
    for f0 in (100, 1000, 3000):
        per = int(round(FS / f0))
        s[f"sq{f0}"] = np.where((np.arange(2 * n) % per) < per // 2, 1.0, -1.0)
        s[f"sgn{f0}"] = np.sign(np.sin(2 * np.pi * f0 * np.arange(2 * n) / FS + 1e-9))
    rng = np.random.default_rng(20260929)
    X = np.fft.rfft(rng.normal(size=10 * n))
    fr = np.fft.rfftfreq(10 * n, 1 / FS)
    X[0] = 0
    X[1:] /= np.sqrt(fr[1:])
    pn = np.fft.irfft(X, 10 * n)
    s["pink"] = pn / np.abs(pn).max()
    return s


SIG = squares()
cases = {}
for name in ["LPX3-a", "LPX3-b", "LPX4-b", "LPX4-b-cap"]:
    B = bank_of(name)
    cases[name] = B["wk"].T @ B["bands"]
cases["FIR V1-128"] = fir_v1()
summ = {}
for name, h8 in cases.items():
    H, fd, amax, (ci, fi) = dense_max(h8)
    rows = {}
    for sn, x in SIG.items():
        pk = np.array([np.abs(np.convolve(x, h8[c])[:len(x)]).max() for c in range(8)])
        rows[sn] = 20 * np.log10(pk / amax / D20R)
    l1 = np.abs(h8).sum(1)
    rows["L1_vs_today"] = 20 * np.log10(l1 / amax / D20R)
    rows["L1_vs_FS"] = 20 * np.log10(l1 / amax)
    sine_ax = 20 * np.log10(1 / amax / AXIS_D20)
    l1_ax = 20 * np.log10(1 / l1.max() / AXIS_D20)
    # drive premise (sine): per-channel peak gain vs today's same channel, and above/below 1.6 kHz
    dp = 20 * np.log10(H.max(1) / amax / D20R)
    hf = fd >= 1600
    dp_hf = 20 * np.log10(H[:, hf].max(1) / amax / D20R)
    dp_lf = 20 * np.log10(H[:, ~hf].max(1) / amax / D20R)
    log(f"  {name}: amax {amax:.5f} at c{ci} {fd[fi]:.1f} Hz | on-axis sine {sine_ax:+.2f} dB, L1-conv {l1_ax:+.2f} dB")
    for k in ["sq100", "sq1000", "sq3000", "sgn100", "sgn1000", "sgn3000", "pink", "L1_vs_today", "L1_vs_FS"]:
        v = rows[k]
        log(f"     {k:12s} " + " ".join(f"{u:+6.2f}" for u in v) + f"   max {v.max():+6.2f} (c{int(np.argmax(v))})")
    log(f"     drive(sine) all f " + " ".join(f"{u:+5.2f}" for u in dp) + " | f>=1.6k " + " ".join(f"{u:+5.2f}" for u in dp_hf)
        + " | f<1.6k " + " ".join(f"{u:+5.2f}" for u in dp_lf))
    # absolute square peaks vs FS (clip check at sine normalisation, no back-off)
    absq = max((20 * np.log10(np.array([np.abs(np.convolve(SIG[k], h8[c])[:len(SIG[k])]).max() for c in range(8)]) / amax)).max()
               for k in ("sq100", "sq1000", "sq3000"))
    log(f"     worst clean-square peak vs digital FS (no back-off): {absq:+.2f} dB")
    summ[name] = (max(rows[k].max() for k in ("sq100", "sq1000", "sq3000")), rows["pink"].max(), rows["L1_vs_FS"].max(), l1_ax,
                  rows["L1_vs_today"].max(), dp.max())
log("  summary: design | worst clean square vs today | pink | no-clip back-off (L1 vs FS) | on-axis L1-conv | L1 vs today (max) | sine drive premise")
for k, v in summ.items():
    log(f"     {k:11s} {v[0]:+6.2f} | {v[1]:+6.2f} | {v[2]:+6.2f} | {v[3]:+6.2f} | {v[4]:+6.2f} | {v[5]:+6.2f}")

# compare with the PM headroom CSV
pm = {}
with open(os.path.join(SIDE, "s7_hybrid_lpxo_headroom.csv")) as fp:
    rd = csv.reader(fp)
    next(rd)
    for r in rd:
        pm[(r[0], r[1])] = r[2:]
mx = 0.0
for name, key in [("LPX3-b", "LPX3-b"), ("LPX3-a", "LPX3-a"), ("LPX4-b", "LPX4-b"), ("LPX4-b-cap", "LPX4-b-cap"), ("FIR V1-128", "FIR V1-128 (taps)")]:
    h8 = cases[name]
    _H, _f, amax, _i = dense_max(h8)
    for sn, pmk in [("sq100", "square 100 Hz"), ("sq1000", "square 1000 Hz"), ("sq3000", "square 3000 Hz")]:
        x = SIG[sn]
        v = 20 * np.log10(np.array([np.abs(np.convolve(x, h8[c])[:len(x)]).max() for c in range(8)]) / amax / D20R)
        mx = max(mx, np.abs(v - np.array([float(u) for u in pm[(key, pmk)]])).max())
    l1 = np.abs(h8).sum(1)
    for pmk, v in [("L1 bound", 20 * np.log10(l1 / amax / D20R)), ("L1 abs vs FS", 20 * np.log10(l1 / amax))]:
        mx = max(mx, np.abs(v - np.array([float(u) for u in pm[(key, pmk)]])).max())
log(f"  max |critic - PM headroom CSV| over squares + L1 rows, 5 designs: {mx:.1e} dB")

# ---------------- (4) LPX4 diagnosis ----------------
log("\n(4) LPX4 DIAGNOSIS: global max |W_c(f)| over 0..24 kHz (own FFT grid), band max weights")
for name in ["LPX3-b", "LPX4-a", "LPX4-b", "LPX4-a-cap", "LPX4-b-cap"]:
    B = bank_of(name)
    h8 = B["wk"].T @ B["bands"]
    H, fd, amax, (ci, fi) = dense_max(h8)
    top = H[:, fd <= 20000].max()
    log(f"  {name:11s} max {amax:.5f} at c{ci} {fd[fi]:8.1f} Hz (max over <=20 kHz {top:.5f}); band max weights "
        + " ".join(f"{w.max():.5f}" for w in B["wk"]) + f"; sine on-axis {20 * np.log10(1 / amax / AXIS_D20):+.2f} dB")
    # where does each channel peak, and what is the max below 4.47 kHz
    lo = fd < 4470
    log(f"     max over f<4.47 kHz {H[:, lo].max():.5f} ; top-band contribution at 20 kHz c7: {h8[7] @ np.cos(0) if False else 0:.0f}")

# ---------------- (5) compute ----------------
log("\n(5) COMPUTE arithmetic")
for name, lens, K in [("LPX3-a", (255, 127), 3), ("LPX3-b", (127, 63), 3), ("LPX4-a", (255, 127, 63), 4), ("LPX4-b", (127, 63, 31), 4)]:
    fold = sum((n + 1) // 2 for n in lens) + 8 * K
    direct = sum(lens) + 8 * K
    log(f"  {name}: folded {fold} MAC/sample = {fold * 64} /frame ; direct {direct} MAC/sample = {direct * 64} /frame ;"
        f" ratios vs FIR-128x8 folded 32768: {32768 / (fold * 64):.2f}x ; direct/direct 65536: {65536 / (direct * 64):.2f}x ;"
        f" folded-LPX vs direct-FIR {65536 / (fold * 64):.2f}x ; latency {(max(lens) - 1) // 2} samples = {(max(lens) - 1) / 2 / FS * 1e3:.3f} ms")
log(f"  X3 4416 -> LPX3-b 7680 = +{(7680 / 4416 - 1) * 100:.0f}% ; M2 830903/1333333 = {830903 / 1333333:.4f} ; 830903/463273 = {830903 / 463273:.4f}")
log(f"  cycles L4: LPX3-b 7680 x 30..50 = {7680 * 30} .. {7680 * 50} ; X3 4416 x 30..50 = {4416 * 30} .. {4416 * 50} ;"
    f" FIR 32768x30 = {32768 * 30}, 65536x50 = {65536 * 50}")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "r3g_bank_headroom.log"), "w") as fp:
    fp.write("\n".join(out) + "\n")
