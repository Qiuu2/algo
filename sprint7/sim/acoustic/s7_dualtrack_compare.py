#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S7 dual-track compare (iron rule 7): numpy track (s7_windows_sweep.csv) vs INDEPENDENT MATLAB track
(s7_matlab_crosscheck.csv, produced by s7_matlab_crosscheck.m via the matlab MCP, R2026a).
Rows compared: Dolph-20 @1k/2k/4k (BW6, SLL, DI), uniform @1k, Dolph-30 @1k, Kaiser b5 @1k, Taylor-25 nbar4 @1k.
Tolerance: |dBW| <= 0.02 deg, |dSLL| <= 0.02 dB, |dDI| <= 0.02 dB  -> CONSISTENT ; else FLAG (do not average).
Output: s7_dualtrack_compare.csv
"""
import os
import csv
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NP = os.path.join(HERE, "s7_windows_sweep.csv")
ML = os.path.join(HERE, "s7_matlab_crosscheck.csv")
OUT = os.path.join(HERE, "s7_dualtrack_compare.csv")
NAME_MAP = {"dolph20": "dolph20_frozen", "uniform": "uniform", "dolph30": "dolph30",
            "kaiser_b5": "kaiser_b5", "taylor25_nbar4": "taylor25_nbar4"}
TOL = {"BW6": 0.02, "SLL": 0.02, "DI": 0.02}


def main():
    if not os.path.exists(ML):
        print("MATLAB track CSV missing -> single-track [L2/numpy], dual-track pending")
        sys.exit(2)
    np_rows = {}
    with open(NP) as fp:
        for r in csv.DictReader(fp):
            np_rows[(r["window"], int(r["freq_hz"]))] = r
    out = []
    worst = {"BW6": 0.0, "SLL": 0.0, "DI": 0.0}
    flag = False
    with open(ML) as fp:
        for r in csv.DictReader(fp):
            key = (NAME_MAP[r["window"]], int(r["freq_hz"]))
            n = np_rows[key]
            d_bw = float(n["BW6dB_full_deg"]) - float(r["BW6dB_full_deg"])
            d_sll = float(n["peak_SLL_dB"]) - float(r["peak_SLL_dB"])
            d_di = float(n["DI_dB"]) - float(r["DI_dB"])
            status = "CONSISTENT" if (abs(d_bw) <= TOL["BW6"] and abs(d_sll) <= TOL["SLL"] and abs(d_di) <= TOL["DI"]) else "FLAG"
            flag |= status == "FLAG"
            worst["BW6"] = max(worst["BW6"], abs(d_bw)); worst["SLL"] = max(worst["SLL"], abs(d_sll)); worst["DI"] = max(worst["DI"], abs(d_di))
            out.append([key[0], key[1], n["BW6dB_full_deg"], r["BW6dB_full_deg"], f"{d_bw:+.4f}",
                        n["peak_SLL_dB"], r["peak_SLL_dB"], f"{d_sll:+.4f}", n["DI_dB"], r["DI_dB"], f"{d_di:+.4f}", status])
            print(f"{key[0]:<16}{key[1]:>6}  BW6 np {n['BW6dB_full_deg']:>8} ml {r['BW6dB_full_deg']:>8} d={d_bw:+.4f} | "
                  f"SLL np {n['peak_SLL_dB']:>8} ml {r['peak_SLL_dB']:>8} d={d_sll:+.4f} | DI np {n['DI_dB']:>7} ml {r['DI_dB']:>7} d={d_di:+.4f}  {status}")
    with open(OUT, "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(["window", "freq_hz", "BW6_numpy_deg", "BW6_matlab_deg", "dBW6_deg", "SLL_numpy_dB", "SLL_matlab_dB",
                     "dSLL_dB", "DI_numpy_dB", "DI_matlab_dB", "dDI_dB", "status(tol 0.02)"])
        wr.writerows(out)
        wr.writerow(["WORST_ABS_DIFF", "", "", "", f"{worst['BW6']:.4f}", "", "", f"{worst['SLL']:.4f}", "", "", f"{worst['DI']:.4f}",
                     "FLAG" if flag else "ALL CONSISTENT"])
    print(f"\nworst |dBW6| = {worst['BW6']:.4f} deg, |dSLL| = {worst['SLL']:.4f} dB, |dDI| = {worst['DI']:.4f} dB -> "
          f"{'FLAG (E-MATLAB-1: do not average, escalate)' if flag else 'ALL CONSISTENT'}")
    print(f"[CSV] {OUT}")
    sys.exit(1 if flag else 0)


if __name__ == "__main__":
    main()
