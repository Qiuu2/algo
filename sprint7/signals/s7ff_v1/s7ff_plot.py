#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s7ff_plot.py -- overview figure of the out-of-band spectra (reads S7FF_V1_SPECTRA.csv only).

12 small multiples, one per band: the 0 dB file and the -40 dB file (worst case: the 24-bit rounding
floor sits 40 dB closer to the signal), each as 1/24-octave band-averaged PSD in dB re that file's own
mean in-band PSD. Dashed grey = the [L4 provisional] spec ceilings of S7_SIDE30_FARFIELD_TEST.md §4.1:
-50 dB beyond one octave from the band edges, -30 dB at the adjacent 1/3-oct centres.
Output: s7ff_spectra_overview.png. Table view of the same numbers = the CSV.
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS = [500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
S1, S2 = "#2a78d6", "#eb6834"          # validated pair (dataviz reference palette slots 1-2)

rows = [r for r in csv.reader(open(os.path.join(HERE, "S7FF_V1_SPECTRA.csv"))) if r and not r[0].startswith("#")]
head, data = rows[0], rows[1:]
freq = [float(r[0]) for r in data]
col = {name: i for i, name in enumerate(head)}

plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})
fig, axes = plt.subplots(3, 4, figsize=(13, 8.2), sharex=True, sharey=True, facecolor=SURFACE)
for ax, fc in zip(axes.flat, BANDS):
    ax.set_facecolor(SURFACE)
    lo, hi = fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6)
    for name, color, label in (("s7ff_v1_%04dHz_0dB.wav" % fc, S1, "0 dB file"),
                               ("s7ff_v1_%04dHz_m40dB.wav" % fc, S2, "-40 dB file")):
        ax.plot(freq, [float(r[col[name]]) for r in data], color=color, lw=1.4, label=label, zorder=3)
    ax.axvspan(lo, hi, color=S1, alpha=0.08, lw=0, zorder=1)
    for seg in ((15, lo / 2), (2 * hi, 24000)):
        ax.plot(seg, (-50, -50), color=INK2, lw=1.0, ls=(0, (4, 3)), zorder=2)
    for c in (fc * 2 ** (-1 / 3), fc * 2 ** (1 / 3)):
        ax.plot((c, c), (-30, -30), marker="v", ms=4.5, color=INK2, ls="none", zorder=2)
    ax.set_xscale("log")
    ax.set_xlim(20, 24000)
    ax.set_ylim(-175, 15)
    ax.grid(True, which="major", color=GRID, lw=0.6)
    ax.set_title("%d Hz band (%.0f-%.0f Hz)" % (fc, lo, hi), color=INK, fontsize=8.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
for ax in axes[-1]:
    ax.set_xlabel("frequency (Hz)")
for ax in axes[:, 0]:
    ax.set_ylabel("dB re mean in-band PSD")
h, l = axes.flat[0].get_legend_handles_labels()
h += [plt.Line2D([], [], color=INK2, lw=1.0, ls=(0, (4, 3))),
      plt.Line2D([], [], color=INK2, marker="v", ms=4.5, ls="none")]
l += ["spec ceiling -50 dB beyond one octave [L4]", "spec ceiling -30 dB at adjacent 1/3-oct centres [L4]"]
fig.legend(h, l, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.985))
fig.suptitle("s7ff_v1: out-of-band spectra of the delivered files (1/24-oct averages of the 35 s steady part, "
             "computed from the file bytes) [L2 tool]", y=0.945, fontsize=9.5, color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(os.path.join(HERE, "s7ff_spectra_overview.png"), dpi=110, facecolor=SURFACE)
print("wrote s7ff_spectra_overview.png")
