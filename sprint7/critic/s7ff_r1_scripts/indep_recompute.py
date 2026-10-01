#!/usr/bin/env python3
"""Critic independent recomputation for s7ff_v1 (does NOT import any package module).
Own RIFF walker, own 24-bit decode, own band edges, own metrics. Compares to S7FF_V1_METRICS.csv."""
import os, sys, struct, csv, hashlib
import numpy as np

R = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint7/signals/s7ff_v1"
W = os.path.join(R, "wav")
FS = 48000

def parse(path):
    raw = open(path, "rb").read()
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WAVE", "not riff"
    chunks = []
    p = 12
    while p + 8 <= len(raw):
        cid = raw[p:p+4]; sz = int.from_bytes(raw[p+4:p+8], "little")
        chunks.append((cid.decode("latin1"), p, sz))
        p += 8 + sz + (sz & 1)
    hdr = {"riff_size": int.from_bytes(raw[4:8], "little"), "file_len": len(raw), "chunks": chunks, "end_pos": p}
    fmt = [c for c in chunks if c[0] == "fmt "][0]
    fb = raw[fmt[1]+8: fmt[1]+8+fmt[2]]
    hdr.update(dict(zip(("tag","ch","rate","brate","balign","bits"), struct.unpack("<HHIIHH", fb[:16]))))
    hdr["fmt_size"] = fmt[2]
    dat = [c for c in chunks if c[0] == "data"][0]
    db = raw[dat[1]+8: dat[1]+8+dat[2]]
    hdr["data_off"] = dat[1]+8
    a = np.frombuffer(db, dtype=np.uint8).reshape(-1, 3)
    # own decode: build int via int32 from 3 bytes placed in the TOP of a 32-bit word then arithmetic shift
    w = np.zeros((a.shape[0], 4), dtype=np.uint8)
    w[:, 1:] = a
    v = w.view("<i4").reshape(-1) >> 8
    return hdr, v.astype(np.int64)

def edges(fc):          # nominal centre +/- 1/6 octave, independent re-derivation
    return fc / 2 ** (1/6), fc * 2 ** (1/6)

def db10(x): return 10*np.log10(x) if x > 0 else -np.inf

files = [(500,0),(630,0),(1000,40),(1600,10),(2000,20),(3150,0),(6300,0),(6300,40),(5000,40),(500,40)]
met = {}
with open(os.path.join(R, "S7FF_V1_METRICS.csv")) as fh:
    for row in csv.DictReader(fh):
        met[row["file"]] = row

FULL = 2**23
res = {}
print("%-26s %5s %4s %6s %4s %5s %9s | %9s %9s %9s %9s %9s %9s %9s" % (
    "file","tag","ch","rate","bits","balgn","nsamp","rms_dB","peak_dB","E1_dB","P2adj_dB","E2_dB","mean_lsb","Lres_lsb"))
zero = {}
for fc, k in files:
    nm = "s7ff_v1_%04dHz_%s.wav" % (fc, "0dB" if k == 0 else "m%ddB" % k)
    h, v = parse(os.path.join(W, nm))
    n = len(v)
    # locate steady part independently: find where the envelope is flat. Use the documented 24000 offset
    # but verify that samples [24000, 1704000) are exactly one period of what the fades contain.
    M = 24000; N = n - 2*M
    st = v[M:M+N].astype(np.float64) / FULL
    rms = np.sqrt(np.mean(st**2))
    peak = np.abs(v).max() / FULL
    X = np.fft.rfft(st)
    P = np.abs(X)**2; P[1:-1] *= 2
    f = np.arange(len(P)) * FS / N
    lo, hi = edges(fc)
    inb = (f >= lo) & (f <= hi)
    Ein = P[inb].sum()
    far = (f < lo/2) | (f > 2*hi)
    E1 = db10(P[far].sum()/Ein)
    psd_in = P[inb].mean()
    # adjacent centres: fc*2^(+-1/3); mean PSD over +-1/48 oct
    adj = []
    for c in (fc*2**(-1/3), fc*2**(1/3)):
        m = (f >= c*2**(-1/48)) & (f < c*2**(1/48))
        adj.append(db10(P[m].mean()/psd_in))
    E2 = db10(max(P[(f >= fc*2**-0.5) & (f < lo)].sum(), P[(f > hi) & (f <= fc*2**0.5)].sum())/Ein)
    lres = float("nan")
    if k == 0:
        zero[fc] = v
    else:
        if fc not in zero:
            _, zero[fc] = parse(os.path.join(W, "s7ff_v1_%04dHz_0dB.wav" % fc))
        lres = np.sqrt(np.mean((v - zero[fc] * 10**(-k/20))**2))
    res[nm] = dict(rms=20*np.log10(rms), peak=20*np.log10(peak), E1=E1, P2=max(adj), E2=E2, L=lres)
    print("%-26s %5d %4d %6d %4d %5d %9d | %9.4f %9.4f %9.2f %9.2f %9.2f %9.4f %9.3f" % (
        nm.replace("s7ff_v1_",""), h["tag"], h["ch"], h["rate"], h["bits"], h["balign"], n,
        res[nm]["rms"], res[nm]["peak"], E1, max(adj), E2, v.mean(), lres))
    print("     header: riff_size+8=%d file_len=%d fmt_size=%d chunks=%s data_off=%d end=%d brate=%d" % (
        h["riff_size"]+8, h["file_len"], h["fmt_size"], [(c[0], c[2]) for c in h["chunks"]], h["data_off"], h["end_pos"], h["brate"]))
    m = met[nm]
    print("     CSV   : rms %s peak %s E1 %s P2 %s E2 %s L %s | diffs rms %.1e peak %.1e E1 %.1e P2 %.1e E2 %.1e" % (
        m["R_rms_dB"], m["P_peak_dB"], m["E1_far_energy_dB"], m["P2_adj_psd_dB"], m["E2_adj_energy_dB"], m.get("L_resid_lsb",""),
        abs(res[nm]["rms"]-float(m["R_rms_dB"])), abs(res[nm]["peak"]-float(m["P_peak_dB"])),
        abs(E1-float(m["E1_far_energy_dB"])), abs(max(adj)-float(m["P2_adj_psd_dB"])), abs(E2-float(m["E2_adj_energy_dB"]))))
    # junction continuity: max |diff| near the steady boundaries vs typical in steady
    x = v.astype(np.float64)
    d = np.abs(np.diff(x))
    dmax_st = d[M:M+N-1].max()
    j1 = d[M-5:M+5].max(); j2 = d[M+N-6:M+N+4].max()
    # periodic-continuation check of the fades (fade-in region / raised cosine == tail of the period)
    nn = np.arange(M); fin = 0.5*(1-np.cos(np.pi*nn/M))
    tail = v[M+N-M:M+N].astype(np.float64)        # last 0.5 s of the steady period
    head = v[M:2*M].astype(np.float64)            # first 0.5 s
    fi_err = np.max(np.abs(v[:M] - np.rint(tail*fin)))   # approx (double-rounding effect <= ~1 LSB)
    fo_err = np.max(np.abs(v[M+N:] - np.rint(head*fin[::-1])))
    print("     junction max|dx| %.0f / %.0f LSB vs steady max|dx| %.0f | fade==periodic-continuation max err in/out %.0f/%.0f LSB | first/last %d/%d" % (
        j1, j2, dmax_st, fi_err, fo_err, v[0], v[-1]))
print()
# silence
h, v = parse(os.path.join(W, "s7ff_v1_silence.wav"))
print("silence: tag %d ch %d rate %d bits %d n %d nonzero %d" % (h["tag"], h["ch"], h["rate"], h["bits"], len(v), np.count_nonzero(v)))
# manifest
man = {}
for line in open(os.path.join(W, "MANIFEST.md5"), "rb").read().decode().splitlines():
    hh, nm = line.split(" ", 1); man[nm.lstrip("*")] = hh
bad = 0
for nm in sorted(os.listdir(W)):
    if nm.endswith(".wav"):
        if hashlib.md5(open(os.path.join(W, nm), "rb").read()).hexdigest() != man.get(nm):
            bad += 1
print("manifest entries %d, wav files %d, md5 mismatches %d, manifest md5 %s, CRLF in manifest: %s" % (
    len(man), len([n for n in os.listdir(W) if n.endswith('.wav')]), bad,
    hashlib.md5(open(os.path.join(W, "MANIFEST.md5"), "rb").read()).hexdigest(),
    b"\r" in open(os.path.join(W, "MANIFEST.md5"), "rb").read()))
