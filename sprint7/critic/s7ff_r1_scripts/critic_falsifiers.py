#!/usr/bin/env python3
"""Critic gap-probe: feed defect classes NOT in the package falsifier list to a COPY of s7ff_check.py."""
import os, sys, tempfile, wave
import numpy as np
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(S, "gate"))          # scratch COPY of the checker under test
import s7ff_check as C

W = os.path.join(S, "gate", "wav")
_, v0, _ = C.read_wav(os.path.join(W, C.name_of(1000, 0)))
_, v40, _ = C.read_wav(os.path.join(W, C.name_of(1000, 40)))
M, N, FULL = C.M, C.N, C.FULL
tmp = tempfile.mkdtemp(prefix="critic_s7ff_")

def wr(path, q):
    q = np.asarray(q, dtype=np.int64)
    raw = q.astype("<i4").view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(3); w.setframerate(48000); w.writeframes(raw)

def run(label, q, fc=1000, k=0):
    p = os.path.join(tmp, C.name_of(fc, k))
    wr(p, q)
    met, fails, v, _ = C.check_signal_file(p, fc, k)
    tags = sorted(set(s.split(":")[0] for s in fails))
    keys = ("E1_far_energy_dB", "P1_far_psd_dB", "P2_adj_psd_dB", "E2_adj_energy_dB", "W_far_energy_dB", "W_far_psd_bin_max_dB", "W_adj_psd_dB")
    print("%-58s -> %-14s %s" % (label, ",".join(tags) or "PASS(!)", " ".join("%s=%.1f" % (k_.split("_")[0] + k_.split("_")[1][:3], met.get(k_, float('nan'))) for k_ in keys)))
    os.remove(p)

run("G0 control (1000 Hz 0 dB unchanged)", v0)
q = v0.copy(); q[M + N // 2] += int(0.25 * FULL); run("G1 one-sample click +0.25 FS mid-steady", q)
q = v0.copy(); q[M + N // 2: M + N // 2 + 5] = 0; run("G2 5-sample dropout mid-steady", q)
q = v0.copy(); q[M + N // 2: M + N // 2 + 48] = 0; run("G3 1 ms dropout mid-steady", q)
q = v0.copy(); q[:960] = 0; q[960:M] = v0[M + N - M + 960: M + N]; run("G4 silent 20 ms then HARD start at full level (no fade)", q)
# G5: fade-in taken from the period HEAD (not tail) -> discontinuity at the fade/steady junction
nn = np.arange(M); fin = 0.5 * (1 - np.cos(np.pi * nn / M))
q = v0.copy(); q[:M] = np.rint(v0[M:2 * M] * fin); run("G5 fade-in from wrong segment (junction step)", q)
# G6: tone at 300 Hz, energy -55 dB re in-band (E1 should pass, P1 should catch)
t = np.arange(len(v0)) / 48000.0
sig_p = np.mean((v0[M:M + N] / FULL) ** 2)
tone = np.sqrt(2 * sig_p * 10 ** (-55 / 10)) * np.sin(2 * np.pi * 300 * t) * FULL
run("G6 300 Hz tone at -55 dB energy (far region)", np.rint(v0 + tone))
# G7: tone at the adjacent centre fc*2^(1/3) at -33 dB energy (E2 passes, P2 should catch)
tone = np.sqrt(2 * sig_p * 10 ** (-33 / 10)) * np.sin(2 * np.pi * 1000 * 2 ** (1 / 3) * t) * FULL
run("G7 tone at fc*2^(1/3) at -33 dB energy", np.rint(v0 + tone))
# G8: DC offset 0.5 % FS
run("G8 DC offset 0.5 % FS", v0 + int(0.005 * FULL))
# G9: same as G1 but in the -40 dB file (click relative to a quiet file)
q = v40.copy(); q[M + N // 2] += int(0.01 * FULL); run("G9 -40 dB file + one-sample click 0.01 FS", q, k=40)
# G10: gain of a level file off by 0.005 dB (should fail R/L)
q = np.rint(v0 * 10 ** (-10.005 / 20)); run("G10 '-10 dB' file at -10.005 dB (alone, no L ref)", q, k=10)
