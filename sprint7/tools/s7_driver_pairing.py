#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s7_driver_pairing.py -- S7 侧抑 20->30 dB 线：逐只喇叭复响应 -> 散布-频率 / 离群 / 疑似极性 -> 贪心配对
                        -> 按权重上位 -> 每路实增益修整 -> ±90° 1/3 倍频程带平均侧抑模型预测
                        （无误差参考 / 随机装配 / 现装配(T0) / 配对装配；修整与否；路线 B 理想化）

配套手册: sprint7/docs/S7_DRIVER_MATCHING_RUNBOOK.md（采集协议、CSV 格式、L 级规则、入库模板）
解释器:   Python 3.10+ 与 numpy（不需要 scipy）。
  Linux:   /usr/bin/python3 sprint7/tools/s7_driver_pairing.py ...
  Windows: 装 python.org 的 Python 3.10+（勾 "Add to PATH"）→ py -m pip install numpy
           → py sprint7\\tools\\s7_driver_pairing.py ...   （跑不了就把数据发回 PM 跑，手册 §4.6）

用法:
  s7_driver_pairing.py DATA.csv [DATA2.csv ...] [选项]            分析实测 CSV（可多文件合并）
  s7_driver_pairing.py DATA.csv --as-built T0.csv                  另外预测现装配（T0：pos,driver_id）
  s7_driver_pairing.py --schema                                    打印 CSV 模板（头块 + 列，占位符，无数值）
  s7_driver_pairing.py --import-rew DIR --header H.txt -o OUT.csv  把 REW 逐条导出文本(<id>_r<rep>.txt)合并成本工具 CSV
  s7_driver_pairing.py --selftest                                  合成数据自检（只在系统临时目录生成，绝不写库）

CSV（手册 §5）:
  头块 = 以 '#' 开头的 'key: value' 行（R10 风格条件，键见 --schema）；数据列:
  driver_id,rep,freq_Hz,mag_dB,phase_deg     (rep 可省=1；phase_deg 全空 = 幅度-only 退路)
  同一喇叭的多次测量用不同 rep；参考喇叭（头块 ref_driver_id）的周期复测也写成它的 rep 递增。
  所有测量必须同一频率网格（REW 同设置导出）且覆盖分析区间。
  T0（--as-built）: 列 pos,driver_id，16 行，pos 0..15（极性 QA 手册 §1.2 的位置约定）。

模型（[L2 模型 on L1 输入]）:
  16 元各向同性点源, x_n=(n-7.5)*0.055 m, c=343 m/s, 远场自由场（与 sprint7/sim/acoustic/s7_common.py 同约定）;
  物理位置 n 与 15-n 为一串联对 P_c (c=n, n<8)，权重 w8[c]；元件 n 的实际响应 = w * g_n(f)，
  g_n = 该只实测复响应 / 批参考（逐频中位 dB + 圆中位相位）。相位在复数域插值/平均（无卷绕伪影）。
  侧抑 R90 = 10log10(ΣP(0°)/max(ΣP(+θ),ΣP(-θ)))，和取 1/3 倍频程带内对数均匀网格（= 粉噪等能量加权）
  = DEC-S7-SIDE30-01 ① 的 R90 形式；默认 7 带 1000..4000 Hz（口径 1k-4k 各 1/3 oct 带）。
  "无误差参考"是各向同性模型值，**不是物理上界**：喇叭/障板自身指向性可能使实测 R90 更高。
  不含: 喇叭自身指向性与其离轴(掠射)离散、箱体绕射、反射/混响、功放 8 路通道增益差、串联对内阻抗分压、温度。
  → 预测值只用于"随机 vs 配对 vs 现装配、修整与否、权重表 A/B"的相对比较与选择，不是现场读数期望值。

纪律:
  * 本脚本不含任何实测数字、不含任何期望读数。唯一内置数表 = 冻结 Dolph-20 权重（运行时读
    sprint4/dsp/fira/dolph_w8_q15.csv 的 w_float_track1_scipy 列，不重算）。
  * 阈值（离群 k、漂移比、噪声比）都是工作假设 [L4]，可改；--target-db 默认 30 = DEC-S7-SIDE30-01 ① 口径值（参数待 CTO 过目）。
  * 配对值不值得做以本批"随机 vs 配对"的逐批比较为准（[5] 的百分位行）；合成数据上配对平均更好但单批可输。
  * 贪心配对不是最优匹配；上位规则 d（按对内距离）/ resid（按修整后残差）两种都打印，供比较。
  * 输出的修整后权重只是提案：改权重表 = 冻结表改动，须 dsp 重跑 F4/F5 子带 bit-exact 链 + 独立 critic + CTO。
  * 退出码: 0 = 完成且无 WARN；1 = 完成但有 WARN（必读）；2 = 输入不可用（格式/网格/覆盖/数量）。
"""
import sys
import os
import re
import csv
import math
import argparse
import tempfile

import numpy as np

VERSION = "v1.2 2026-09-26 (critic R3c + delta fixes)"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
W8_CSV = os.path.join(ROOT, "sprint4", "dsp", "fira", "dolph_w8_q15.csv")
W8_COL = "w_float_track1_scipy"

C_SOUND = 343.0                      # m/s @20 C, same as s7_common.py
N_EL = 16
D_EL = 0.055                         # m [L1 teardown] DEC-S3-GEOM-01
X_EL = (np.arange(N_EL) - (N_EL - 1) / 2.0) * D_EL
DB_EQ = 20.0 / math.log(10.0)        # 8.686: 1 neper (or 1 rad of phase) = 8.686 dB-eq
DEFAULT_BANDS = (1000.0, 1250.0, 1600.0, 2000.0, 2500.0, 3150.0, 4000.0)   # DEC-S7-SIDE30-01 ①: 1k-4k 各 1/3 oct
NOMINAL_THIRD = (500.0, 630.0, 800.0, 1000.0, 1250.0, 1600.0, 2000.0, 2500.0, 3150.0, 4000.0, 5000.0, 6300.0)
THIRD = 2.0 ** (1.0 / 6.0)           # 1/3-oct half-width factor

HEADER_KEYS = [
    ("date", "测量日期 YYYY-MM-DD"),
    ("operator", "测量人"),
    ("location", "地点/房间"),
    ("jig_id", "治具编号/版本（障板或测试箱，手册 §3）"),
    ("mic_model", "测量麦型号+序列号"),
    ("mic_cal_file", "麦校准文件名（无则写 none）"),
    ("interface", "声卡/接口型号"),
    ("software", "软件+版本（如 REW 版本号）"),
    ("timing_reference", "loopback / acoustic / none（none=相位不可用于延时散布）"),
    ("mic_distance_m", "麦到振膜中心距离 m（卷尺实测）"),
    ("mic_position", "麦相对喇叭轴线位置（如 on-axis）"),
    ("drive_level_Vrms", "喇叭端子处激励 Vrms（万用表 AC 档实测）+ 功放档位"),
    ("sweep", "扫频范围/长度/电平/平均次数/IR 窗口"),
    ("temperature_C", "开始/结束室温 C"),
    ("background", "本底（麦位，扫频关闭时）"),
    ("driver_batch", "喇叭批次/来源/数量"),
    ("ref_driver_id", "参考喇叭 ID（漂移追踪）"),
    ("polarity_method", "逐只极性确认方法（电池法 S7_POLARITY_QA_RUNBOOK §1，离线做）"),
]


class InputError(Exception):
    """Input unusable -> exit 2."""


def _console_safe():
    """Windows consoles (GBK) cannot encode some symbols; never crash on print."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


# ---------------------------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------------------------
def wrap_rad(x):
    return (np.asarray(x) + np.pi) % (2.0 * np.pi) - np.pi


def circ_mean(ph, axis=0):
    return np.angle(np.mean(np.exp(1j * ph), axis=axis))


def circ_median(ph, axis=0):
    """Robust circular median: centre on the circular mean, take the linear median of wrapped residuals."""
    c0 = circ_mean(ph, axis=axis)
    r = wrap_rad(ph - np.expand_dims(c0, axis))
    return wrap_rad(c0 + np.median(r, axis=axis))


def zlog(Z):
    """Complex log ln|Z| + j*phase with the phase UNWRAPPED along frequency (last axis) and centred so the
    mid-band value lies in [-pi, pi]. Used only after complex-domain averaging (no wrap artefacts)."""
    mag = np.log(np.maximum(np.abs(Z), 1e-12))
    ph = np.unwrap(np.angle(Z), axis=-1)
    mid = ph[..., ph.shape[-1] // 2]
    ph = ph - 2.0 * np.pi * np.round(mid / (2.0 * np.pi))[..., None]
    return mag + 1j * ph


def expand16(w8):
    w8 = np.asarray(w8, float)
    return np.concatenate([w8, w8[::-1]])


def log_grid(fmin, fmax, ppo):
    n = int(math.ceil(math.log2(fmax / fmin) * ppo))
    return fmin * 2.0 ** (np.arange(n + 1) / float(ppo))


def band_mask(fgrid, fc):
    return (fgrid >= fc / THIRD * (1 - 1e-9)) & (fgrid <= fc * THIRD * (1 + 1e-9))


def steer(fgrid, theta_deg):
    k = 2.0 * np.pi * np.asarray(fgrid, float) / C_SOUND
    return np.exp(1j * np.outer(X_EL, k) * math.sin(math.radians(theta_deg)))   # (16, F)


def db(x):
    return 10.0 * np.log10(np.maximum(x, 1e-300))


def chebwin_np(M, at):
    """Dolph-Chebyshev window, numpy port of scipy.signal.windows.chebwin (sym=True), normalised max 1.
    Selftest T3 checks chebwin_np(16, 20) against the frozen table (and against scipy when installed)."""
    order = M - 1.0
    beta = np.cosh(1.0 / order * np.arccosh(10 ** (abs(at) / 20.0)))
    x = beta * np.cos(np.pi * np.arange(M) / M)
    p = np.zeros(M)
    p[x > 1] = np.cosh(order * np.arccosh(x[x > 1]))
    p[x < -1] = (2 * (M % 2) - 1) * np.cosh(order * np.arccosh(-x[x < -1]))
    m = np.abs(x) <= 1
    p[m] = np.cos(order * np.arccos(x[m]))
    if M % 2:
        w = np.real(np.fft.fft(p))
        n = (M + 1) // 2
        w = w[:n]
        w = np.concatenate((w[n - 1:0:-1], w))
    else:
        p = p * np.exp(1j * np.pi / M * np.arange(M))
        w = np.real(np.fft.fft(p))
        n = M // 2 + 1
        w = np.concatenate((w[n - 1:0:-1], w[1:n]))
    return w / w.max()


# ---------------------------------------------------------------------------------------------
# weights
# ---------------------------------------------------------------------------------------------
def load_w8(path=None, col=W8_COL):
    path = path or W8_CSV
    if not os.path.exists(path):
        raise InputError("找不到权重表 %s（在仓库外运行时用 --weights 指定，或 --w8 / --chebwin）" % path)
    w = [None] * 8
    with open(path, "r", encoding="utf-8-sig") as fp:
        for row in csv.DictReader(fp):
            w[int(row["ch"])] = float(row[col])
    if any(v is None for v in w):
        raise InputError("权重表 %s 缺通道行（需要 ch=0..7）" % path)
    return np.array(w, float)


def resolve_weights(args):
    if args.w8:
        w8 = np.array([float(v) for v in args.w8.split(",")], float)
        label = "--w8 手给（候选，非冻结）"
    elif args.chebwin is not None:
        w8 = chebwin_np(N_EL, args.chebwin)[:8]
        label = "chebwin(16, %.1f dB) 归一（候选，非冻结 [L2]）" % args.chebwin
    else:
        path = args.weights or W8_CSV
        w8 = load_w8(path, args.weight_col)
        label = ("冻结 Dolph-20 %s:%s" % (os.path.relpath(path, ROOT), args.weight_col)
                 if not args.weights else "%s:%s" % (path, args.weight_col))
    if w8.shape != (8,) or np.any(w8 <= 0):
        raise InputError("权重需 8 个正数（通道 c=0 最外 … c=7 最中心）")
    return w8, label


# ---------------------------------------------------------------------------------------------
# input
# ---------------------------------------------------------------------------------------------
def schema_text():
    out = ["# S7_DRIVER_MATCHING v1   (s7_driver_pairing.py %s; 手册 sprint7/docs/S7_DRIVER_MATCHING_RUNBOOK.md §5)" % VERSION]
    for k, desc in HEADER_KEYS:
        out.append("# %s: <%s>" % (k, desc))
    out.append("driver_id,rep,freq_Hz,mag_dB,phase_deg")
    out.append("<ID>,<1..n>,<Hz>,<dB>,<deg; 幅度-only 退路时整列留空>")
    out.append("")
    out.append("# --as-built T0.csv 格式:")
    out.append("pos,driver_id")
    out.append("<0..15>,<ID>")
    return "\n".join(out)


def read_dataset_csv(path):
    header, body = {}, []
    with open(path, "r", encoding="utf-8-sig") as fp:
        for ln in fp.read().splitlines():
            s = ln.strip()
            if not s:
                continue
            if s.startswith("#"):
                m = re.match(r"#\s*([A-Za-z0-9_]+)\s*[:=]\s*(.*)$", s)
                if m:
                    header[m.group(1)] = m.group(2).strip()
                continue
            body.append(ln)
    if not body:
        raise InputError("%s: 没有数据行" % path)
    rdr = csv.DictReader(body)
    cols = [c.strip() for c in (rdr.fieldnames or [])]
    for need in ("driver_id", "freq_Hz", "mag_dB", "phase_deg"):
        if need not in cols:
            raise InputError("%s: 缺列 %s（需要 driver_id,rep,freq_Hz,mag_dB,phase_deg）" % (path, need))
    rows = []
    for i, r in enumerate(rdr, start=2):
        r = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in r.items() if k}
        try:
            did = r["driver_id"]
            rep = int(r.get("rep") or 1)
            f = float(r["freq_Hz"])
            m = float(r["mag_dB"])
            p = r.get("phase_deg")
            p = float(p) if p not in (None, "") else float("nan")
        except (ValueError, TypeError):
            raise InputError("%s: 第 %d 行数值格式错: %r" % (path, i, r))
        if not did:
            raise InputError("%s: 第 %d 行 driver_id 为空" % (path, i))
        rows.append((did, rep, f, m, p))
    return header, rows


def build_measurements(files):
    """Return (headers, meas, has_phase); meas = list of dict(driver, key, f, mag, ph)."""
    headers, groups = [], {}
    for fi, path in enumerate(files):
        h, rows = read_dataset_csv(path)
        headers.append((path, h))
        for did, rep, f, m, p in rows:
            groups.setdefault((did, fi, rep), []).append((f, m, p))
    meas = []
    for (did, fi, rep), lst in sorted(groups.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
        a = np.array(lst, float)
        a = a[np.argsort(a[:, 0])]
        if np.any(np.diff(a[:, 0]) <= 0):
            raise InputError("driver %s rep %d (文件 %d): 频点重复或非递增" % (did, rep, fi))
        meas.append({"driver": did, "key": (fi, rep), "f": a[:, 0], "mag": a[:, 1], "ph": a[:, 2]})
    if not meas:
        raise InputError("没有测量")
    f0 = meas[0]["f"]
    for m in meas:
        if m["f"].shape != f0.shape or not np.allclose(m["f"], f0, rtol=1e-6, atol=0):
            raise InputError("频率网格不一致（driver %s rep %s）：所有测量须用同一 REW 设置导出" % (m["driver"], m["key"][1]))
    nan_counts = [int(np.isnan(m["ph"]).sum()) for m in meas]
    has_phase = all(c == 0 for c in nan_counts)
    if not has_phase and not all(c == len(f0) for c in nan_counts):
        raise InputError("phase_deg 部分有部分空：要么全部有相位，要么整列留空（幅度-only 退路）")
    return headers, meas, has_phase


def read_asbuilt(path, drivers):
    """T0 as-built assignment: CSV pos,driver_id (16 rows, pos 0..15). Returns list of 16 driver ids by position."""
    with open(path, "r", encoding="utf-8-sig") as fp:
        lines = [ln for ln in fp.read().splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    rdr = csv.DictReader(lines)
    cols = [c.strip() for c in (rdr.fieldnames or [])]
    if "pos" not in cols or "driver_id" not in cols:
        raise InputError("%s: T0 需要列 pos,driver_id" % path)
    m = {}
    for r in rdr:
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        try:
            pos = int(r["pos"])
        except ValueError:
            raise InputError("%s: pos 不是整数: %r" % (path, r))
        if pos in m:
            raise InputError("%s: pos %d 重复" % (path, pos))
        m[pos] = r["driver_id"]
    if sorted(m) != list(range(N_EL)):
        raise InputError("%s: 需要 pos 0..15 各一行（现有 %s）" % (path, sorted(m)))
    ids = [m[p] for p in range(N_EL)]
    if len(set(ids)) != N_EL:
        raise InputError("%s: 同一只喇叭出现在两个位置" % path)
    miss = [d for d in ids if d not in drivers]
    if miss:
        raise InputError("%s: 这些 ID 没有测量数据: %s" % (path, ",".join(miss)))
    return ids


def import_rew(dirpath, header_path, out_path):
    """Merge REW text exports named <driver_id>_r<rep>.txt into one tool CSV."""
    pat = re.compile(r"^(.+)_r(\d+)\.(txt|csv)$", re.IGNORECASE)
    files = sorted(os.listdir(dirpath))
    hdr_lines = []
    if header_path:
        with open(header_path, "r", encoding="utf-8-sig") as fp:
            for ln in fp.read().splitlines():
                if ln.strip():
                    hdr_lines.append(ln if ln.lstrip().startswith("#") else "# " + ln)
    n_files, out_rows = 0, []
    for name in files:
        m = pat.match(name)
        if not m:
            continue
        did, rep = m.group(1), int(m.group(2))
        n_files += 1
        with open(os.path.join(dirpath, name), "r", encoding="utf-8-sig", errors="replace") as fp:
            for ln in fp:
                s = ln.strip()
                if not s or s.startswith("*") or s.startswith("#"):
                    continue
                toks = [t for t in re.split(r"[,\s;]+", s) if t]
                try:
                    nums = [float(t) for t in toks[:3]]
                except ValueError:
                    continue
                if len(nums) < 2:
                    continue
                ph = "%.6g" % nums[2] if len(nums) >= 3 else ""
                out_rows.append("%s,%d,%.6f,%.6f,%s" % (did, rep, nums[0], nums[1], ph))
    if n_files == 0:
        raise InputError("%s 下没有 <driver_id>_r<rep>.txt 文件" % dirpath)
    with open(out_path, "w", encoding="utf-8") as fp:
        for ln in hdr_lines:
            fp.write(ln + "\n")
        fp.write("driver_id,rep,freq_Hz,mag_dB,phase_deg\n")
        for r in out_rows:
            fp.write(r + "\n")
    return n_files, len(out_rows)


# ---------------------------------------------------------------------------------------------
# core analysis
# ---------------------------------------------------------------------------------------------
def deviations(meas, has_phase, fgrid):
    """Complex ratio z = H/R per measurement, R = batch reference (per-frequency median dB over drivers,
    circular median phase). Interpolated onto fgrid in the COMPLEX domain (real/imag, linear in log f) ->
    no phase-wrap artefacts (critic R3c MAJOR-5)."""
    f0 = meas[0]["f"]
    drivers = sorted(set(m["driver"] for m in meas))
    MAG = np.array([m["mag"] for m in meas])
    PH = np.deg2rad(np.array([m["ph"] for m in meas])) if has_phase else np.zeros_like(MAG)
    idx = {d: [i for i, m in enumerate(meas) if m["driver"] == d] for d in drivers}
    rep_mag = np.array([MAG[idx[d]].mean(axis=0) for d in drivers])
    rep_ph = np.array([circ_mean(PH[idx[d]], axis=0) for d in drivers])
    ref_mag = np.median(rep_mag, axis=0)
    ref_ph = circ_median(rep_ph, axis=0)
    Z0 = 10.0 ** ((MAG - ref_mag) / 20.0) * np.exp(1j * (PH - ref_ph))
    lf, lg = np.log(f0), np.log(fgrid)
    Z = np.array([np.interp(lg, lf, Z0[i].real) + 1j * np.interp(lg, lf, Z0[i].imag) for i in range(len(meas))])
    return drivers, idx, Z


def per_driver(drivers, idx, Zm):
    """Complex mean over reps (wrap-safe), then unwrapped complex log. Repeatability = RMS |log(z_rep/z_mean)|."""
    Zd = np.array([Zm[idx[d]].mean(axis=0) for d in drivers])
    Ld = zlog(Zd)
    nrep = np.array([len(idx[d]) for d in drivers])
    srep = np.array([np.sqrt(np.mean(np.abs(zlog(Zm[idx[d]] / Zd[k])) ** 2)) if nrep[k] >= 2 else np.nan
                     for k, d in enumerate(drivers)])
    return Zd, Ld, nrep, srep


def fit_gain_delay(L, fgrid, has_phase):
    """Per driver: constant gain (dB), linear-phase delay (us), intercept (rad, phase extrapolated to 0 Hz),
    residual RMS (dB-eq) after removing gain + linear phase."""
    g_db = np.real(L).mean(axis=1) * DB_EQ
    if has_phase:
        A = np.vstack([np.ones_like(fgrid), fgrid]).T
        coef, *_ = np.linalg.lstsq(A, np.imag(L).T, rcond=None)      # (2, n)
        tau_us = -coef[1] / (2.0 * np.pi) * 1e6
        icpt = wrap_rad(coef[0])            # zlog centring shifts phase by 2*pi*k -> intercept only meaningful mod 2*pi
        fit_i = (A @ coef).T
    else:
        tau_us = np.full(L.shape[0], np.nan)
        icpt = np.zeros(L.shape[0])
        fit_i = np.zeros_like(np.imag(L))
    res = (np.real(L) - np.real(L).mean(axis=1, keepdims=True)) + 1j * (np.imag(L) - fit_i)
    resid = np.sqrt(np.mean(np.abs(res) ** 2, axis=1)) * DB_EQ
    return g_db, tau_us, icpt, resid


def outliers(L, icpt, has_phase, k):
    """OUTLIER: score = RMS|l| > median + k*1.4826*MAD. POLARITY?: |wrap(phase intercept at 0 Hz)| > 90 deg
    (a reversed driver is a constant ~180 deg offset; a pure delay extrapolates to ~0 deg mod 360 -- the wrap matters
    because a gross delay makes the unwrapped/centred phase pick up 2*pi*k, critic delta MINOR-1)."""
    score = np.sqrt(np.mean(np.abs(L) ** 2, axis=1))
    med = np.median(score)
    mad = np.median(np.abs(score - med)) * 1.4826
    thr = med + k * mad if mad > 0 else med + 1e-9
    pol = (np.abs(wrap_rad(icpt)) > np.pi / 2) if has_phase else np.zeros(len(score), bool)   # critic delta MINOR-1
    return score, thr, (score > thr) | pol, pol


def pair_distance(La, Lb):
    return float(np.sqrt(np.mean(np.abs(La - Lb) ** 2)))


def greedy_pairs(L, ids):
    """Greedy (NOT optimal) matching: repeatedly take the globally closest unused pair, 8 times."""
    n = len(ids)
    cand = []
    for i in range(n):
        for j in range(i + 1, n):
            cand.append((pair_distance(L[i], L[j]), ids[i], ids[j], i, j))
    cand.sort(key=lambda t: (t[0], t[1], t[2]))
    used, pairs = set(), []
    for dist, _, _, i, j in cand:
        if i in used or j in used:
            continue
        used.update((i, j))
        pairs.append((dist, i, j))
        if len(pairs) == 8:
            break
    spares = [i for i in range(n) if i not in used]
    return pairs, spares


def pair_resid(La, Lb):
    """Uncorrectable residual of a pair after its per-channel real trim: RMS over f and both elements of |g*t-1|."""
    Gp = np.exp(np.array([La, Lb]))
    p = 0.5 * (Gp[0] + Gp[1])
    tr = np.exp(-np.mean(np.log(np.maximum(np.abs(p), 1e-12))))
    return float(np.sqrt(np.mean(np.abs(Gp * tr - 1.0) ** 2)))


def assign(pairs, w8, ids, L=None, rule="d"):
    """Pairs -> channels, best first to the highest weight. rule d: by within-pair distance D (spec default);
    rule resid: by the pair's residual after the real trim (includes its common-mode phase/delay; critic R3c INFO-14)."""
    order_ch = sorted(range(8), key=lambda c: (-w8[c], -c))
    if rule == "resid":
        key = lambda p: (pair_resid(L[p[1]], L[p[2]]), ids[min(p[1], p[2])])
    else:
        key = lambda p: (p[0], ids[min(p[1], p[2])])
    table = [None] * 8
    for c, (dist, i, j) in zip(order_ch, sorted(pairs, key=key)):
        a, b = (i, j) if ids[i] <= ids[j] else (j, i)
        table[c] = (a, b, dist)
    return table


def build_G(table, L, nf):
    G = np.zeros((N_EL, nf), complex)
    for c in range(8):
        a, b, _ = table[c]
        G[c] = np.exp(L[a])
        G[15 - c] = np.exp(L[b])
    return G


def ls_trims(G):
    """G: (..., 16, F) element gains. Per-channel real, frequency-independent trim t_c that removes the pair's
    band-mean log-magnitude offset: 20log10 t_c = -mean_f 20log10|p_c(f)|, p_c = (g_c + g_15-c)/2 (on-axis pair sum).
    (Not the complex LS fit: with phase errors LS shrinks gains and bends the taper; a real gain can only fix magnitude.
    With phase-dominated spread the on-axis pair sum partly cancels, so this trim can be slightly counter-productive.)"""
    p = 0.5 * (G[..., :8, :] + G[..., ::-1, :][..., :8, :])
    return np.exp(-np.mean(np.log(np.maximum(np.abs(p), 1e-12)), axis=-1))


def fir_correct(G):
    """Route-B idealisation: per-channel complex, per-frequency correction that makes each pair's common mode exactly 1
    (divides both elements of pair c by p_c(f)); weights unchanged. Only the within-pair difference survives. [L2]
    Not an upper bound of route B (route B may also change weights per frequency)."""
    p = 0.5 * (G[..., :8, :] + G[..., ::-1, :][..., :8, :])
    return G / np.concatenate([p, p[..., ::-1, :]], axis=-2)


def rejection(G, w16, fgrid, bands, angles):
    """G (T,16,F), w16 (T,16) -> dict[(fc, ang)] = (rej_plus, rej_minus, worse, P0band, Psband) arrays (T,), dB."""
    front = np.einsum("te,tef->tf", w16, G)
    P0 = np.abs(front) ** 2
    out = {}
    for ang in angles:
        Pp = np.abs(np.einsum("te,tef,ef->tf", w16, G, steer(fgrid, ang))) ** 2
        Pm = np.abs(np.einsum("te,tef,ef->tf", w16, G, steer(fgrid, -ang))) ** 2
        for fc in bands:
            m = band_mask(fgrid, fc)
            rp = db(P0[:, m].mean(axis=1) / Pp[:, m].mean(axis=1))
            rm = db(P0[:, m].mean(axis=1) / Pm[:, m].mean(axis=1))
            out[(fc, ang)] = (rp, rm, np.minimum(rp, rm), P0[:, m].mean(axis=1), np.maximum(Pp, Pm)[:, m].mean(axis=1))
    return out


def predict_all(G, w8, fgrid, bands, angles):
    """(raw, +real trim, +route-B idealisation) for one assembly G (16,F)."""
    t = ls_trims(G[None])[0]
    return (rejection(G[None], expand16(w8)[None], fgrid, bands, angles),
            rejection(G[None], expand16(w8 * t)[None], fgrid, bands, angles),
            rejection(fir_correct(G[None]), expand16(w8)[None], fgrid, bands, angles), t)


def ideal_rejection(w8, fgrid, bands, angles):
    G = np.ones((1, N_EL, len(fgrid)), complex)
    return rejection(G, expand16(w8)[None, :], fgrid, bands, angles)


def monte_carlo(Lpool, w8, fgrid, bands, angles, n, rng, chunk=500):
    """Random assembly: each trial draws 16 distinct drivers from the pool into random positions."""
    M = Lpool.shape[0]
    w16 = expand16(w8)
    res = {"raw": {}, "trim": {}, "fir": {}}
    powers = {"P0": [], "Ps": {}}
    for start in range(0, n, chunk):
        T = min(chunk, n - start)
        perms = np.array([rng.permutation(M)[:N_EL] for _ in range(T)])
        G = np.exp(Lpool[perms])                                   # (T,16,F)
        W = np.broadcast_to(w16, (T, N_EL))
        r0 = rejection(G, W, fgrid, bands, angles)
        t = ls_trims(G)
        r1 = rejection(G, W * np.concatenate([t, t[:, ::-1]], axis=1), fgrid, bands, angles)
        r2 = rejection(fir_correct(G), W, fgrid, bands, angles)
        for key in r0:
            res["raw"].setdefault(key, []).append(r0[key][2])
            res["trim"].setdefault(key, []).append(r1[key][2])
            res["fir"].setdefault(key, []).append(r2[key][2])
        front = np.einsum("te,tef->tf", W, G)
        powers["P0"].append(np.abs(front) ** 2)
        for ang in angles:
            for sgn in (1, -1):
                Ps = np.abs(np.einsum("te,tef,ef->tf", W, G, steer(fgrid, sgn * ang))) ** 2
                powers["Ps"].setdefault(sgn * ang, []).append(Ps)
    for mode in res:
        for key in res[mode]:
            res[mode][key] = np.concatenate(res[mode][key])
    P0 = np.concatenate(powers["P0"]).mean(axis=0)
    Ps = {a: np.concatenate(v).mean(axis=0) for a, v in powers["Ps"].items()}
    return res, P0, Ps


def analytic_random(Lpool, w8, fgrid, angle):
    """Expected band powers for random assembly without trims (Van Trees 2.208 form + finite-population
    correction): E|sum a_n g_n|^2 = |mu|^2 |A|^2 + s2 [sum|a|^2 - (|A|^2 - sum|a|^2)/(M-1)]."""
    G = np.exp(Lpool)                                    # (M,F)
    M = G.shape[0]
    mu = G.mean(axis=0)
    s2 = np.mean(np.abs(G - mu) ** 2, axis=0)            # population variance over the pool
    w16 = expand16(w8)
    sa2 = np.sum(w16 ** 2)

    def ep(theta):
        A = w16 @ steer(fgrid, theta)
        return np.abs(mu) ** 2 * np.abs(A) ** 2 + s2 * (sa2 - (np.abs(A) ** 2 - sa2) / (M - 1))
    return ep(0.0), ep(angle), s2, mu


def spread_table(L, fgrid, fmin, fmax):
    """Per nominal 1/3-oct band fully inside [fmin,fmax]: spread across drivers."""
    rows = []
    gconst = np.real(L).mean(axis=1, keepdims=True)
    for fc in NOMINAL_THIRD:
        if fc / THIRD < fmin * (1 - 1e-6) or fc * THIRD > fmax * (1 + 1e-6):
            continue
        m = band_mask(fgrid, fc)
        Lb = L[:, m]
        mag_sd = np.std(np.real(Lb).mean(axis=1)) * DB_EQ
        ph_sd = np.degrees(np.std(np.imag(Lb).mean(axis=1)))
        tot = np.sqrt(np.mean(np.abs(Lb) ** 2)) * DB_EQ
        aft = np.sqrt(np.mean(np.abs(Lb - gconst) ** 2)) * DB_EQ
        rows.append((fc, mag_sd, ph_sd, tot, aft))
    return rows


def pctl(dist, v):
    return 100.0 * float(np.mean(np.asarray(dist) <= v))


# ---------------------------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------------------------
def analyse(files, args, out=print):
    warns = []
    headers, meas, has_phase = build_measurements(files)
    bands = tuple(float(b) for b in args.bands.split(","))
    angles = tuple(float(a) for a in args.angles.split(","))
    fmin, fmax = min(bands) / THIRD, max(bands) * THIRD
    f0 = meas[0]["f"]
    if f0[0] > fmin * (1 + 1e-6) or f0[-1] < fmax * (1 - 1e-6):
        raise InputError("数据频率覆盖 %.0f-%.0f Hz 不含分析区间 %.0f-%.0f Hz" % (f0[0], f0[-1], fmin, fmax))
    fgrid = log_grid(fmin, fmax, args.ppo)
    w8, wlabel = resolve_weights(args)

    # header completeness (R10 style)
    for path, h in headers:
        miss = [k for k, _ in HEADER_KEYS if not h.get(k)]
        if miss:
            warns.append("头块缺 %s（%s）→ 按手册 §8 结果只能记'条件未记录'，不得定 [L1]" % (",".join(miss), os.path.basename(path)))
    if len(headers) > 1:
        for key in ("jig_id", "mic_distance_m", "drive_level_Vrms", "timing_reference", "mic_position"):
            vals = set(h.get(key, "") for _, h in headers)
            if len(vals) > 1:
                warns.append("多文件条件不一致: %s = %s → 跨会话混合比较无效，除非 CTO 认可" % (key, sorted(vals)))
    tref = (headers[0][1].get("timing_reference", "") or "").lower()
    if has_phase and tref.startswith("none"):
        warns.append("timing_reference=none 但有相位列：延时散布不可信，建议加 --remove-delay 并在结论里写明")
    if set(bands) != set(DEFAULT_BANDS):
        warns.append("频带 %s ≠ 口径 7 带（DEC-S7-SIDE30-01 ① 1k-4k 各 1/3 oct）：联合良率不可与口径直接对照"
                     % "/".join("%g" % b for b in bands))

    drivers, idx, Zm = deviations(meas, has_phase, fgrid)
    Zd, Ld, nrep, srep = per_driver(drivers, idx, Zm)
    if args.remove_delay and has_phase:
        A = np.vstack([np.ones_like(fgrid), fgrid]).T
        coef, *_ = np.linalg.lstsq(A, np.imag(Ld).T, rcond=None)
        slope_only = (A[:, 1:] @ coef[1:]).T                    # remove the delay slope, keep the intercept
        Ld = np.real(Ld) + 1j * (np.imag(Ld) - slope_only)
    g_db, tau_us, icpt, resid = fit_gain_delay(Ld, fgrid, has_phase)
    score, thr, flag, pol = outliers(Ld, icpt, has_phase, args.k_mad)

    out("=" * 100)
    out("s7_driver_pairing %s | 模式: %s | 权重: %s | 上位规则: %s" % (
        VERSION, "复响应(幅度+相位)" if has_phase else "幅度-only 退路", wlabel, args.assign))
    out("文件: %s" % ", ".join(os.path.basename(p) for p, _ in headers))
    out("喇叭 %d 只, 测量 %d 条, 原网格 %d 点 %.0f-%.0f Hz; 分析区间 %.0f-%.0f Hz (1/%d oct), 频带 %s, 角度 ±%s"
        % (len(drivers), len(meas), len(f0), f0[0], f0[-1], fmin, fmax, args.ppo,
           "/".join("%g" % b for b in bands), "/±".join("%g" % a for a in angles)))
    if not has_phase:
        warns.append("幅度-only：相位误差按 0 处理 → 预测在期望意义上偏乐观（不是上下界）；极性反接/延时差在此数据里不可见，"
                     "逐只极性必须以电池法确认；本结果不能回答'散布是否随频率变'中相位那一半")
    out("单位: dB-eq = 8.686 x |复对数偏差|（1 dB-eq ≈ 0.115 Np 幅度 ≈ 6.6° 相位）")

    # --- data quality -----------------------------------------------------------------------
    out("\n[1] 数据质量")
    typ_rep = np.nanmedian(srep) if np.any(~np.isnan(srep)) else float("nan")
    all_d = [pair_distance(Ld[i], Ld[j]) for i in range(len(drivers)) for j in range(i + 1, len(drivers))]
    med_d = float(np.median(all_d)) if all_d else float("nan")
    nr = int(np.median(nrep))
    if not np.isnan(typ_rep):
        noise_d = math.sqrt(2.0) * typ_rep / math.sqrt(max(nr, 1))
        out("  重复性(每只各 rep 相对其均值, RMS) 中位 %.3f dB-eq; 配对距离噪声底 ≈ %.3f dB-eq; 全体两两距离中位 %.3f dB-eq"
            % (typ_rep * DB_EQ, noise_d * DB_EQ, med_d * DB_EQ))
        if med_d < args.noise_ratio * noise_d:
            warns.append("两两距离中位 < %.1f x 噪声底：测量分辨不出喇叭差异，配对=在噪声上配（先改善治具/重复性）[L4 阈值]" % args.noise_ratio)
    else:
        warns.append("每只只有 1 次测量：无重复性，不能判断配对是否在噪声上（手册要求每只 3 次）")
    ref = headers[0][1].get("ref_driver_id", "")
    if ref and ref in drivers:
        k = drivers.index(ref)
        ii = idx[ref]
        dev = [np.sqrt(np.mean(np.abs(zlog(Zm[i] / Zd[k])) ** 2)) for i in ii]
        drift = np.sqrt(np.mean(np.abs(zlog(Zm[ii[-1]] / Zm[ii[0]])) ** 2)) if len(ii) >= 2 else float("nan")
        out("  参考喇叭 %s: %d 次测量, 相对其均值最大 %.3f dB-eq, 首→末 %.3f dB-eq"
            % (ref, len(ii), max(dev) * DB_EQ, drift * DB_EQ))
        if len(ii) < 2:
            warns.append("参考喇叭只测了 1 次：漂移未追踪（手册 §4.3 要求每 N 只复测）")
        elif max(dev) > args.drift_ratio * np.median(score):
            warns.append("参考喇叭漂移 %.3f dB-eq > %.2f x 批散布中位 %.3f：本批数据不可用于配对，查温度/麦/治具后重测 [L4 阈值]"
                         % (max(dev) * DB_EQ, args.drift_ratio, np.median(score) * DB_EQ))
    else:
        warns.append("头块无 ref_driver_id 或该 ID 无数据：漂移未追踪")

    # --- per driver ---------------------------------------------------------------------------
    out("\n[2] 逐只偏差（相对批参考；分析区间内）  score=RMS|l|；离群阈 = 中位 + %.1f x 1.4826 MAD = %.3f dB-eq"
        % (args.k_mad, thr * DB_EQ))
    out("  %-10s %4s %9s %10s %9s %12s %10s %9s  %s" % ("driver", "rep", "gain dB", "delay us", "截距 deg",
                                                      "残差 dB-eq", "score", "rep RMS", "flag"))
    for k, d in enumerate(drivers):
        fl = []
        if pol[k]:
            fl.append("POLARITY?(相位截距 >90°: 查治具接线/该只极性，别当坏品换)")
        elif flag[k]:
            fl.append("OUTLIER")
        out("  %-10s %4d %+9.3f %10s %9s %12.3f %10.3f %9s  %s" % (
            d, nrep[k], g_db[k], ("%+.1f" % tau_us[k]) if has_phase else "n/a",
            ("%+.0f" % math.degrees(icpt[k])) if has_phase else "n/a", resid[k], score[k] * DB_EQ,
            ("%.3f" % (srep[k] * DB_EQ)) if not np.isnan(srep[k]) else "n/a", " ".join(fl)))
    out("  注: gain = 常数增益偏差；delay = 线性相位拟合斜率；截距 = 拟合相位外推到 0 Hz（反接 ≈ ±180°）；"
        "残差 = 去掉常数增益与线性相位后剩下的随频率变部分")

    # --- spread vs frequency --------------------------------------------------------------------
    keep = ~flag if not args.keep_outliers else np.ones(len(drivers), bool)
    pool_ids = [d for k, d in enumerate(drivers) if keep[k]]
    Lpool = Ld[keep]
    out("\n[3] 散布 vs 频率（池内 %d 只；1/3 oct 带）" % len(pool_ids))
    out("  %8s %12s %12s %14s %22s" % ("fc Hz", "幅度SD dB", "相位SD deg", "总RMS dB-eq", "去每只常数增益后 dB-eq"))
    for fc, msd, psd, tot, aft in spread_table(Lpool, fgrid, fmin, fmax):
        out("  %8.0f %12.3f %12s %14.3f %22.3f" % (fc, msd, ("%.2f" % psd) if has_phase else "n/a", tot, aft))
    tot_all = np.mean(np.abs(Lpool) ** 2)
    aft_all = np.mean(np.abs(Lpool - np.real(Lpool).mean(axis=1, keepdims=True)) ** 2)
    frac = 1.0 - aft_all / tot_all if tot_all > 0 else float("nan")
    out("  每只一个常数增益能解释的散布方差比例 = %.1f%%（低 = 散布随频率变/相位主导 → 实数增益修整本身帮助小；"
        "配对是否值得仍看 [5] 的逐批比较）" % (100 * frac))

    if flag.any():
        warns.append("离群/疑似极性: %s → %s" % (", ".join(d for k, d in enumerate(drivers) if flag[k]),
                                                  "已排除出配对池" if not args.keep_outliers else "--keep-outliers: 仍在池内"))
    if len(pool_ids) < N_EL:
        raise InputError("可用喇叭 %d < 16（离群已排除）；补测/补货，或 --keep-outliers 仅看预测" % len(pool_ids))

    # --- pairing + assignment + trims ------------------------------------------------------------
    pairs, spares = greedy_pairs(Lpool, pool_ids)
    other = "resid" if args.assign == "d" else "d"
    table = assign(pairs, w8, pool_ids, Lpool, args.assign)
    table_o = assign(pairs, w8, pool_ids, Lpool, other)
    G = build_G(table, Lpool, len(fgrid))
    pr_raw, pr_trim, pr_fir, t = predict_all(G, w8, fgrid, bands, angles)
    _, pr_trim_o, _, _ = predict_all(build_G(table_o, Lpool, len(fgrid)), w8, fgrid, bands, angles)
    w_trim = w8 * t
    w_new = w_trim / w_trim.max()
    out("\n[4] 配对表（贪心匹配 = 全局最小复偏差向量距离优先，非最优匹配；上位规则 %s：%s → 最高权重位置）"
        % (args.assign, "对内距离 D 最小的一对" if args.assign == "d" else "修整后残差最小的一对"))
    out("  %3s %10s %8s %10s %10s %10s %11s %9s %10s" % ("c", "位置对", "w8[c]", "pos c", "pos 15-c", "D dB-eq",
                                                       "残差 dB-eq", "修整 dB", "新权重"))
    for c in sorted(range(8), key=lambda c: -w8[c]):
        a, b, dist = table[c]
        out("  %3d %10s %8.4f %10s %10s %10.3f %11.3f %+9.3f %10.6f" % (
            c, "{%d,%d}" % (c, 15 - c), w8[c], pool_ids[a], pool_ids[b], dist * DB_EQ,
            pair_resid(Lpool[a], Lpool[b]) * DB_EQ, 20 * math.log10(t[c]), w_new[c]))
    score_pool = score[keep]
    spares = sorted(spares, key=lambda i: (score_pool[i], pool_ids[i]))
    out("  备用(未上位，按 score 升序 = 优先替补顺序): %s" % (", ".join(pool_ids[i] for i in spares) if spares else "无"))
    out("  新权重 = w8[c] x 修整 / max(...)（最大 = 1.0）。修整 = 去掉该对在轴和的带均 dB 偏差（实数、与频率无关）；只修对内平均幅度，"
        "对内两只之差、相位/延时、随频率变部分都修不了。位置对 {c,15-c} 是物理位置；功放通道→位置对的映射以极性 QA Phase A 实测为准"
        "（非 {c,15-c} 拓扑 = 停，本模型不适用）。改权重表 = 冻结表改动（F4/F5 bit-exact 重跑 + critic + CTO），本表只是提案")

    # --- as-built (T0) --------------------------------------------------------------------------
    ab = None
    if args.as_built:
        ab_ids = read_asbuilt(args.as_built, drivers)
        Gab = np.exp(np.array([Ld[drivers.index(d)] for d in ab_ids]))
        ab = predict_all(Gab, w8, fgrid, bands, angles)
        inst_out = [d for d in ab_ids if flag[drivers.index(d)]]
        out("\n[4b] 现装配（T0 %s）：pos0..15 = %s" % (os.path.basename(args.as_built), ",".join(ab_ids)))
        if inst_out:
            warns.append("现装配里装着离群/疑似极性喇叭: %s（现装配预测照算，含它们）" % ",".join(inst_out))

    # --- predictions ------------------------------------------------------------------------------
    rng = np.random.default_rng(args.seed)
    ide = ideal_rejection(w8, fgrid, bands, angles)
    mc, P0mc, Psmc = monte_carlo(Lpool, w8, fgrid, bands, angles, args.mc, rng)

    out("\n[5] ±θ 侧抑 R90 预测 [L2 模型 on %s 输入]：1/3 oct 带平均，较差一侧，dB（越大越好）；目标线 %.1f dB（口径值，非期望）"
        % ("L1" if has_phase else "L1 幅度-only", args.target_db))
    for ang in angles:
        out("  --- ±%g° ---" % ang)
        out("  %-36s" % "装配方式" + "".join("%16s" % ("%g Hz" % b) for b in bands) + "%12s" % "全带≥目标")
        out("  %-36s" % "无误差参考(各向同性模型，非上界)" + "".join("%16.2f" % ide[(b, ang)][2][0] for b in bands) + "%12s" % "-")
        for mode, name in (("raw", "随机装配 中位[P10,P90]"), ("trim", "随机+每路修整 中位[P10,P90]"),
                           ("fir", "随机+路线B理想化 中位[P10,P90]")):
            cells, ok = [], np.ones(args.mc, bool)
            for b in bands:
                v = mc[mode][(b, ang)]
                ok &= v >= args.target_db
                cells.append("%.1f[%.1f,%.1f]" % (np.median(v), np.percentile(v, 10), np.percentile(v, 90)))
            out("  %-36s" % name + "".join("%16s" % c for c in cells) + "%11.1f%%" % (100 * ok.mean()))
        rows = []
        if ab is not None:
            rows += [(ab[0], "现装配 T0"), (ab[1], "现装配+每路修整"), (ab[2], "现装配+路线B理想化")]
        rows += [(pr_raw, "配对装配(规则 %s)" % args.assign), (pr_trim, "配对+每路修整(规则 %s)" % args.assign),
                 (pr_fir, "配对+路线B理想化(规则 %s)" % args.assign), (pr_trim_o, "配对+每路修整(另一规则 %s)" % other)]
        for arr, name in rows:
            v = [arr[(b, ang)][2][0] for b in bands]
            out("  %-36s" % name + "".join("%16.2f" % x for x in v) + "%12s" % ("是" if min(v) >= args.target_db else "否"))
        # per-batch decision aid: where do the single assemblies sit in the random distributions?
        cells = ["P%.0f" % pctl(mc["trim"][(b, ang)], pr_trim[(b, ang)][2][0]) for b in bands]
        out("  %-36s" % "本批判读: 配对+修整 在 随机+修整 中的百分位" + "".join("%16s" % c for c in cells))
        if ab is not None:
            cells = ["P%.0f" % pctl(mc["raw"][(b, ang)], ab[0][(b, ang)][2][0]) for b in bands]
            out("  %-36s" % "本批判读: 现装配 在 随机装配 中的百分位" + "".join("%16s" % c for c in cells))
        # analytic cross-check (second track): random, no trims, expected power ratio per side
        cells = []
        for b in bands:
            m = band_mask(fgrid, b)
            e0, ep, s2, mu = analytic_random(Lpool, w8, fgrid, ang)
            _, em, _, _ = analytic_random(Lpool, w8, fgrid, -ang)
            ra = min(db(e0[m].mean() / ep[m].mean()), db(e0[m].mean() / em[m].mean()))
            rm = min(db(P0mc[m].mean() / Psmc[ang][m].mean()), db(P0mc[m].mean() / Psmc[-ang][m].mean()))
            cells.append("%.2f/%.2f" % (ra, rm))
        out("  %-36s" % "核: 随机期望功率比 解析/MC" + "".join("%16s" % c for c in cells) + "%12s" % "-")
        low = [b for b in bands if ide[(b, ang)][2][0] < args.target_db]
        if low:
            warns.append("无误差各向同性模型值 @%s Hz ±%g° < 目标 %.1f dB：本模型下配对/修整无法达标（模型值不是物理上界，"
                         "喇叭/箱体自身指向性可能使实测更高，但不能据此预期达标）→ 权重表选择是另一个决定（CTO；候选用 --chebwin/--weights 比）"
                         % ("/".join("%g" % b for b in low), ang, args.target_db))
        for arr, name in ((pr_raw, "配对"), (pr_trim, "配对+修整")):
            hi = [b for b in bands if arr[(b, ang)][2][0] > ide[(b, ang)][2][0]]
            if hi:
                out("  注: %s 在 %s Hz 高于无误差参考 = 误差恰好与理想旁瓣相消的单次巧合，不可当可实现值（模型外误差会抹掉）"
                    % (name, "/".join("%g" % b for b in hi)))
    wng = expand16(w8).sum() ** 2 / np.sum(expand16(w8) ** 2)
    s2m = np.mean(np.abs(np.exp(Lpool) - np.exp(Lpool).mean(axis=0)) ** 2)
    out("  WNG_abs = %.2f dB；池内误差方差 σ² = %.3e → 随机误差侧向平均地板 ≈ σ²/WNG = %.1f dB re 正前 (Van Trees 2.208)"
        % (10 * math.log10(wng), s2m, db(s2m / wng)))
    out("  随机行 = %d 次 Monte Carlo（seed %d；池 %d 只中随机抽 16 随机上位）；配对/现装配行 = 单一确定装配；配对含选择偏差"
        "（按含噪实测挑最像的），噪声/散布比越大越乐观。配对值不值得做 = 看本批百分位行，不看一般结论" % (args.mc, args.seed, len(pool_ids)))
    out("  路线B理想化 = 每路把该对共模逐频幅相完全修平、权重不变，只剩对内差（DEC-S7-SIDE30-01 ③）；不是路线B上界"
        "（路线B还可逐频改权重），实际受滤波器长度/鲁棒设计限制，见 S7_SIDE30_PERCH_FIR_DESIGN.md")
    out("  模型不含：喇叭自身指向性及其离轴(掠射)离散/箱体绕射/反射/功放通道增益差/串联对阻抗分压 → 只作相对比较，不是现场读数期望值")

    if args.out_dir:
        write_outputs(args.out_dir, drivers, nrep, g_db, tau_us, icpt, resid, score, flag, pol, table, pool_ids, w8, t,
                      w_new, Lpool, spread_table(Lpool, fgrid, fmin, fmax))
        out("\n输出 CSV → %s" % args.out_dir)

    out("\n[WARN] %d 条" % len(warns))
    for wmsg in warns:
        out("  WARN: " + wmsg)
    return {"warns": warns, "drivers": drivers, "flag": flag, "pol": pol, "icpt": icpt, "table": table,
            "table_other": table_o, "pool_ids": pool_ids, "trims": t, "w_new": w_new, "ideal": ide,
            "paired_raw": pr_raw, "paired_trim": pr_trim, "paired_fir": pr_fir, "paired_trim_other": pr_trim_o,
            "asbuilt": ab, "mc": mc, "P0mc": P0mc, "Psmc": Psmc, "Lpool": Lpool, "Ld": Ld, "fgrid": fgrid, "w8": w8,
            "bands": bands, "angles": angles, "has_phase": has_phase, "frac_gain": frac}


def write_outputs(d, drivers, nrep, g_db, tau_us, icpt, resid, score, flag, pol, table, pool_ids, w8, t, w_new,
                  Lpool, spread):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "per_driver.csv"), "w", newline="", encoding="utf-8") as fp:
        wr = csv.writer(fp)
        wr.writerow(["driver_id", "n_rep", "gain_dB", "delay_us", "intercept_deg", "resid_dBeq", "score_dBeq",
                     "outlier", "polarity_suspect"])
        for k, dd in enumerate(drivers):
            wr.writerow([dd, nrep[k], "%.4f" % g_db[k], "%.2f" % tau_us[k], "%.1f" % math.degrees(icpt[k]),
                         "%.4f" % resid[k], "%.4f" % (score[k] * DB_EQ), int(flag[k]), int(pol[k])])
    with open(os.path.join(d, "pairing.csv"), "w", newline="", encoding="utf-8") as fp:
        wr = csv.writer(fp)
        wr.writerow(["c", "pos_pair", "w8_frozen", "driver_pos_c", "driver_pos_15mc", "D_dBeq", "resid_dBeq",
                     "trim_dB", "w_new_proposal"])
        for c in range(8):
            a, b, dist = table[c]
            wr.writerow([c, "{%d,%d}" % (c, 15 - c), "%.10f" % w8[c], pool_ids[a], pool_ids[b], "%.4f" % (dist * DB_EQ),
                         "%.4f" % (pair_resid(Lpool[a], Lpool[b]) * DB_EQ), "%.4f" % (20 * math.log10(t[c])),
                         "%.10f" % w_new[c]])
    with open(os.path.join(d, "spread_vs_freq.csv"), "w", newline="", encoding="utf-8") as fp:
        wr = csv.writer(fp)
        wr.writerow(["fc_Hz", "mag_sd_dB", "phase_sd_deg", "total_rms_dBeq", "after_const_gain_dBeq"])
        for row in spread:
            wr.writerow(["%.1f" % row[0]] + ["%.4f" % v for v in row[1:]])


# ---------------------------------------------------------------------------------------------
# selftest (synthetic data in a system temp dir only)
# ---------------------------------------------------------------------------------------------
def _synth(rng, n, gain_sd=0.5, delay_sd_us=8.0, ripple_sd=0.3, rep_noise_db=0.02, reps=3, ph_noise_deg=0.2):
    """Synthetic drivers on a REW-like 1/48-oct grid 300-8000 Hz with a common bulk delay. Returns grid, dict id->list of (mag,ph)."""
    f = log_grid(300.0, 8000.0, 48)
    common_mag = 85.0 + 3.0 * np.sin(np.log(f))
    common_ph = -360.0 * f * 1.5e-3                       # 1.5 ms bulk delay (mic distance + latency), wrapped later
    drv = {}
    for i in range(n):
        g = rng.normal(0, gain_sd)
        tau = rng.normal(0, delay_sd_us) * 1e-6
        rip = ripple_sd * np.sin(np.log(f) * rng.uniform(1, 3) + rng.uniform(0, 6.28))
        lst = []
        for _ in range(reps):
            mag = common_mag + g + rip + rng.normal(0, rep_noise_db, f.size)
            ph = common_ph - 360.0 * f * tau + np.degrees(rip / DB_EQ) + rng.normal(0, ph_noise_deg, f.size)
            lst.append((mag, ph))
        drv["D%02d" % i] = lst
    return f, drv


def _write_csv(path, f, drv, header=None, phase=True):
    with open(path, "w", encoding="utf-8") as fp:
        h = header if header is not None else {k: "synthetic-selftest" for k, _ in HEADER_KEYS}
        for k, v in h.items():
            fp.write("# %s: %s\n" % (k, v))
        fp.write("driver_id,rep,freq_Hz,mag_dB,phase_deg\n")
        for did, lst in drv.items():
            for r, (mag, ph) in enumerate(lst, start=1):
                phw = (np.asarray(ph) + 180.0) % 360.0 - 180.0
                for k in range(f.size):
                    fp.write("%s,%d,%.6f,%.6f,%s\n" % (did, r, f[k], mag[k], ("%.6f" % phw[k]) if phase else ""))


def _args(**kw):
    ns = argparse.Namespace(bands=",".join("%g" % b for b in DEFAULT_BANDS), angles="90", ppo=48, w8=None, chebwin=None,
                            weights=None, weight_col=W8_COL, k_mad=3.5, keep_outliers=False, remove_delay=False, mc=400,
                            seed=12345, target_db=30.0, noise_ratio=3.0, drift_ratio=0.5, out_dir=None, as_built=None,
                            assign="d")
    for k, v in kw.items():
        setattr(ns, k, v)
    return ns


def selftest():
    sys.dont_write_bytecode = True
    _console_safe()
    results = []
    quiet = lambda *a, **k: None

    def check(name, cond, detail=""):
        results.append((name, bool(cond), detail))
        print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

    rng = np.random.default_rng(20260926)
    w8 = load_w8()
    with tempfile.TemporaryDirectory(prefix="s7_pairing_selftest_") as td:
        print("selftest 临时目录（退出即删）: %s" % td)
        hdr = {k: "synthetic-selftest" for k, _ in HEADER_KEYS}
        hdr["ref_driver_id"] = "D00"

        # T1 parse round trip + header completeness
        f, drv = _synth(rng, 18)
        p1 = os.path.join(td, "t1.csv")
        _write_csv(p1, f, drv, hdr)
        headers, meas, has_phase = build_measurements([p1])
        check("T1 解析回读: 18 只 x 3 rep, 有相位", len(meas) == 54 and has_phase and len(set(m["driver"] for m in meas)) == 18)
        h2 = dict(hdr)
        del h2["mic_distance_m"]
        p1b = os.path.join(td, "t1b.csv")
        _write_csv(p1b, f, drv, h2)
        r = analyse([p1b], _args(), out=quiet)
        check("T1 头块缺键必 WARN", any("mic_distance_m" in w for w in r["warns"]))
        check("T1 默认 = 口径 7 带", tuple(r["bands"]) == DEFAULT_BANDS)

        # T2 zero-error batch: all identical drivers -> paired == random == ideal, trims == 1
        drv0 = {"Z%02d" % i: [(85.0 + 0 * f, -360.0 * f * 1.5e-3)] * 3 for i in range(16)}
        p2 = os.path.join(td, "t2.csv")
        _write_csv(p2, f, drv0, hdr)
        r = analyse([p2], _args(), out=quiet)
        dmax = max(abs(r["paired_trim"][(b, 90.0)][2][0] - r["ideal"][(b, 90.0)][2][0]) for b in r["bands"])
        mmax = max(float(np.max(np.abs(r["mc"]["raw"][(b, 90.0)] - r["ideal"][(b, 90.0)][2][0]))) for b in r["bands"])
        check("T2 零误差批: 配对/随机预测 == 无误差参考", dmax < 1e-6 and mmax < 1e-6, "(max diff %.1e / %.1e dB)" % (dmax, mmax))
        check("T2 零误差批: 修整 == 1, 新权重 == 冻结表", np.allclose(r["trims"], 1, atol=1e-9) and np.allclose(r["w_new"], w8, atol=1e-9))
        fmax_ = max(float(np.max(np.abs(r["mc"]["fir"][(b, 90.0)] - r["ideal"][(b, 90.0)][2][0]))) for b in r["bands"])
        check("T2 零误差批: 路线B行 == 无误差参考", fmax_ < 1e-6, "(max diff %.1e dB)" % fmax_)

        # T3 model vs independent formulas; numpy chebwin vs frozen table (and scipy if present)
        fg = log_grid(1000 / THIRD, 4000 * THIRD, 48)
        ide = ideal_rejection(w8, fg, DEFAULT_BANDS, (90.0,))
        errs = []
        for b in DEFAULT_BANDS:
            m = band_mask(fg, b)
            k = 2 * np.pi * fg[m] / C_SOUND
            af0 = 2 * w8.sum()
            af90 = 2 * (w8[None, :] * np.cos(np.outer(k, X_EL[:8]))).sum(axis=1)
            errs.append(abs(db(af0 ** 2 / np.mean(af90 ** 2)) - ide[(b, 90.0)][2][0]))
        check("T3 模型 vs 对称闭式 2Σw cos(kx)", max(errs) < 1e-9, "(max %.1e dB)" % max(errs))
        check("T3 chebwin_np(16,20) == 冻结 Dolph-20 表", np.allclose(chebwin_np(16, 20.0)[:8], w8, atol=1e-9),
              "(max %.1e)" % float(np.max(np.abs(chebwin_np(16, 20.0)[:8] - w8))))
        try:
            from scipy.signal.windows import chebwin as _sc_cheb
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")      # scipy's ENBW note on chebwin < 45 dB is irrelevant here
                ok = all(np.allclose(chebwin_np(16, a), _sc_cheb(16, a) / _sc_cheb(16, a).max(), atol=1e-12)
                         for a in (20, 35, 40))
            check("T3 chebwin_np == scipy chebwin（第二实现）", ok)
        except ImportError:
            check("T3 scipy 交叉核（可选）", True, "跳过: 无 scipy")
        try:
            sys.path.insert(0, os.path.join(ROOT, "sprint7", "sim", "acoustic"))
            import s7_common as sc
            ff = np.array([1000.0, 2000.0, 4000.0])
            a_mine = np.abs(expand16(w8) @ steer(ff, 90.0))
            a_sc = np.array([abs(sc.af_complex([90.0], x, sc.expand16(w8))[0]) for x in ff])
            check("T3 模型 vs s7_common.af_complex（第二实现）", np.allclose(a_mine, a_sc, rtol=1e-9, atol=1e-12))
        except Exception as e:                                    # pragma: no cover
            check("T3 s7_common 交叉核（可选）", True, "跳过: %s" % e)

        # T4 planted twins, GAIN-dominated spread: greedy recovers twins; best twin -> highest weight;
        #    data dependence + negative control
        def twins(seed, g_sd, t_sd_us, rip_db):
            rng4 = np.random.default_rng(seed)
            dd4 = {}
            for p in range(8):
                base_g = rng4.normal(0, g_sd)
                base_t = rng4.normal(0, t_sd_us) * 1e-6
                rip = rip_db * np.sin(np.log(f) * rng4.uniform(1, 3) + rng4.uniform(0, 6.28))
                for s_ in (0, 1):
                    dlt = (0.01 * (p + 1)) * (1 if s_ else -1) / 2
                    dd4["P%d%s" % (p, "ab"[s_])] = [(85.0 + base_g + rip + dlt, -360.0 * f * (1.5e-3 + base_t))] * 3
            return dd4

        def improvement(r_):
            return np.array([r_["paired_trim"][(bb, 90.0)][2][0] - np.median(r_["mc"]["trim"][(bb, 90.0)]) for bb in r_["bands"]])

        p4 = os.path.join(td, "t4.csv")
        _write_csv(p4, f, twins(7, 1.0, 0.0, 0.05), hdr)
        r = analyse([p4], _args(chebwin=35.0, keep_outliers=True), out=quiet)   # outlier logic is T6
        got = sorted(tuple(sorted((r["pool_ids"][a], r["pool_ids"][b]))) for a, b, _ in r["table"])
        want = sorted(("P%da" % p, "P%db" % p) for p in range(8))
        check("T4 贪心配对恢复 8 对孪生", got == want)
        best_ch = max(range(8), key=lambda c: r["w8"][c])
        a, b, _ = r["table"][best_ch]
        check("T4 最像的一对 → 最高权重位置 c%d" % best_ch, {r["pool_ids"][a], r["pool_ids"][b]} == {"P0a", "P0b"})
        imp_gain = improvement(r)
        check("T4 增益主导孪生批: 配对+修整 > 随机+修整中位（预测依赖数据）", np.all(imp_gain > 0), "(Δ %s dB)" % np.round(imp_gain, 1))
        G = np.zeros((N_EL, len(r["fgrid"])), complex)
        for c in range(8):
            a, b, _ = r["table"][c]
            a2, b2, _ = r["table"][(c + 1) % 8]
            G[c] = np.exp(r["Lpool"][a])
            G[15 - c] = np.exp(r["Lpool"][b2])
        tt = ls_trims(G[None])[0]
        bad = rejection(G[None], expand16(r["w8"] * tt)[None], r["fgrid"], r["bands"], (90.0,))
        dneg = np.array([bad[(bb, 90.0)][2][0] - r["paired_trim"][(bb, 90.0)][2][0] for bb in r["bands"]])
        check("T4 负控制: 错配(交叉换伴) 带均更差且多数带更差", dneg.mean() < 0 and np.sum(dneg < 0) > len(dneg) / 2,
              "(带均 %+.2f dB, 更差 %d/%d 带)" % (dneg.mean(), int(np.sum(dneg < 0)), len(dneg)))
        # T4b CONSTRUCTION-SPECIFIC (8 exact twins, pure delay, one seed) -- NOT a general rule (critic R3c MAJOR-1):
        #     real gain trims cannot touch a common-mode delay, so the pairing gain is smaller than in the gain-twin case.
        p4b = os.path.join(td, "t4b.csv")
        _write_csv(p4b, f, twins(7, 0.0, 20.0, 0.0), hdr)
        rb = analyse([p4b], _args(chebwin=35.0, keep_outliers=True), out=quiet)
        trim_db = 20 * np.log10(rb["trims"])
        dtr = max(abs(rb["paired_trim"][(bb, 90.0)][2][0] - rb["paired_raw"][(bb, 90.0)][2][0]) for bb in rb["bands"])
        check("T4b 孪生+纯延时构造: 实数增益修整对共模延时无作用（修整≈0 dB，配对+修整==配对）",
              np.max(np.abs(trim_db)) < 1e-3 and dtr < 1e-3, "(max|trim| %.1e dB, Δ %.1e dB)" % (np.max(np.abs(trim_db)), dtr))
        check("T4b 同上: 常数增益可解释方差比例 < 增益孪生批", rb["frac_gain"] < r["frac_gain"],
              "(%.0f%% vs %.0f%%)" % (100 * rb["frac_gain"], 100 * r["frac_gain"]))
        # T13 route B idealisation leaves only within-pair differences
        dfir = [abs(rb["paired_fir"][(bb, 90.0)][2][0] - rb["ideal"][(bb, 90.0)][2][0]) for bb in rb["bands"]]
        check("T13 路线B: 孪生+纯延时批 配对+逐频复修正 ≈ 无误差参考(<0.5 dB)", max(dfir) < 0.5, "(max %.2f dB)" % max(dfir))
        imp_fir = np.array([rb["paired_fir"][(bb, 90.0)][2][0] - np.median(rb["mc"]["fir"][(bb, 90.0)]) for bb in rb["bands"]])
        check("T13 路线B: 配对 > 随机中位（路线B下配对的价值 = 缩小对内差）", np.all(imp_fir > 0), "(Δ %s dB)" % np.round(imp_fir, 1))

        # T16 statistics on CONTINUOUS delay-only spread (critic R3c MAJOR-1 / delta INFO-4; the runbook cites only this):
        #     a) 16-driver pool: averaged over seeds, paired+trim beats random+trim median in every band, yet single
        #        batches can lose -> decision is per batch;
        #     b) 16-driver pool: most of that gain comes from the assignment rule (same pairs, random channel order = rule off);
        #     c) 24-driver pool: most of the gain comes from choosing 16 of 24 (total minus assignment share);
        #     d) real gain trims do ~nothing to a pure-delay spread (paired+trim minus paired raw).
        w35 = chebwin_np(16, 35.0)[:8]
        fg7 = log_grid(1000 / THIRD, 4000 * THIRD, 48)
        acc = {16: {"tot": [], "share": [], "trim": []}, 24: {"tot": [], "share": [], "trim": []}}
        for sd in range(12):
            for npool, base in ((16, 3000), (24, 4000)):
                rs = np.random.default_rng(base + sd)
                Lb = np.array([1j * (-2 * np.pi * fg7 * rs.normal(0, 20.0) * 1e-6) for _ in range(npool)])
                ids = ["S%02d" % i for i in range(npool)]
                prs, _ = greedy_pairs(Lb, ids)
                praw, ptrim, _, _ = predict_all(build_G(assign(prs, w35, ids, Lb, "d"), Lb, len(fg7)), w35, fg7,
                                                DEFAULT_BANDS, (90.0,))
                perm = np.random.default_rng(sd + 7).permutation(8)
                tab_r = [None] * 8
                for c, (dd, i, j) in zip(perm, prs):
                    tab_r[c] = (i, j, dd)
                _, ptrim_r, _, _ = predict_all(build_G(tab_r, Lb, len(fg7)), w35, fg7, DEFAULT_BANDS, (90.0,))
                mcs, _, _ = monte_carlo(Lb, w35, fg7, DEFAULT_BANDS, (90.0,), 150, np.random.default_rng(sd))
                acc[npool]["tot"].append([ptrim[(bb, 90.0)][2][0] - np.median(mcs["trim"][(bb, 90.0)]) for bb in DEFAULT_BANDS])
                acc[npool]["share"].append([ptrim[(bb, 90.0)][2][0] - ptrim_r[(bb, 90.0)][2][0] for bb in DEFAULT_BANDS])
                acc[npool]["trim"].append([ptrim[(bb, 90.0)][2][0] - praw[(bb, 90.0)][2][0] for bb in DEFAULT_BANDS])
        a16 = {k: np.array(v) for k, v in acc[16].items()}
        a24 = {k: np.array(v) for k, v in acc[24].items()}
        check("T16a 连续纯延时散布 16 只池 12 种子: 配对+修整 平均 > 随机+修整中位（每带）", np.all(a16["tot"].mean(axis=0) > 0),
              "(均值 %s dB; 单批输的比例 %s)" % (np.round(a16["tot"].mean(axis=0), 1), np.round((a16["tot"] < 0).mean(axis=0), 2)))
        check("T16b 同上 16 只池: 收益主要来自上位规则（上位规则份额 > 总收益的一半，带均）",
              a16["share"].mean() > 0.5 * a16["tot"].mean(),
              "(总 %.2f dB, 上位规则份额 %.2f dB)" % (a16["tot"].mean(), a16["share"].mean()))
        check("T16c 24 只池: 收益主要来自从 24 只里挑 16 只（总收益 − 上位规则份额 > 上位规则份额，带均）",
              a24["tot"].mean() - a24["share"].mean() > a24["share"].mean(),
              "(总 %.2f dB, 上位规则份额 %.2f dB)" % (a24["tot"].mean(), a24["share"].mean()))
        check("T16d 16 只池: 实数修整对纯延时散布几乎无作用（|配对+修整 − 配对| 均值 < 0.5 dB，每带）",
              np.all(np.abs(a16["trim"].mean(axis=0)) < 0.5), "(均值 %s dB)" % np.round(a16["trim"].mean(axis=0), 2))

        # T5 trims: one pair +2 dB -> its trim ~ -2 dB relative; renormalised max == 1, all <= 1
        drv5 = {"Q%02d" % i: [(85.0 + 0 * f, -360.0 * f * 1.5e-3)] * 3 for i in range(16)}
        for nm in ("Q14", "Q15"):
            drv5[nm] = [(87.0 + 0 * f, -360.0 * f * 1.5e-3)] * 3
        p5 = os.path.join(td, "t5.csv")
        _write_csv(p5, f, drv5, hdr)
        r = analyse([p5], _args(keep_outliers=True), out=quiet)
        chq = [c for c in range(8) if {r["pool_ids"][r["table"][c][0]], r["pool_ids"][r["table"][c][1]]} == {"Q14", "Q15"}]
        ok5 = len(chq) == 1
        if ok5:
            c = chq[0]
            rel = 20 * math.log10(r["trims"][c]) - np.median([20 * math.log10(r["trims"][k]) for k in range(8) if k != c])
            ok5 = abs(rel + 2.0) < 1e-6
        check("T5 +2 dB 对的修整 = -2 dB（相对）", ok5)
        check("T5 新权重 max == 1.0 且全部 <= 1", abs(r["w_new"].max() - 1.0) < 1e-12 and np.all(r["w_new"] <= 1 + 1e-12))

        # T6 outlier + polarity flags (with phase)
        rng6 = np.random.default_rng(11)
        f6, drv6 = _synth(rng6, 18)
        drv6["BAD_GAIN"] = [(m + 6.0, p) for m, p in drv6["D03"]]
        drv6["BAD_POL"] = [(m, p + 180.0) for m, p in drv6["D04"]]
        p6 = os.path.join(td, "t6.csv")
        _write_csv(p6, f6, drv6, hdr)
        r = analyse([p6], _args(), out=quiet)
        fl = {d for k, d in enumerate(r["drivers"]) if r["flag"][k]}
        pl = {d for k, d in enumerate(r["drivers"]) if r["pol"][k]}
        check("T6 离群: +6 dB 与反极性两只被标，正常 18 只不标", fl == {"BAD_GAIN", "BAD_POL"}, "(flagged %s)" % sorted(fl))
        check("T6 反极性只标在 BAD_POL", pl == {"BAD_POL"})
        check("T6 离群排除出配对池", "BAD_GAIN" not in r["pool_ids"] and "BAD_POL" not in r["pool_ids"])

        # T14 phase-wrap regression (critic R3c MAJOR-5): reversed copy of a near-median driver in a TIGHT batch
        #     (gain SD 0.05 dB, delay SD 1 us, phase noise 0.5 deg). Old code (wrapped-phase interpolation +
        #     arithmetic rep averaging) flagged POLARITY? in only 4/20 here. Must be 20/20, with 0 false polarity flags.
        npol, nfalse = 0, 0
        for sd in range(20):
            rt = np.random.default_rng(700 + sd)
            cm = 85.0 + 3.0 * np.sin(np.log(f))
            cp = -360.0 * f * 1.5e-3
            dt = {}
            for i in range(18):
                g = rt.normal(0, 0.05)
                tau = rt.normal(0, 1.0) * 1e-6
                dt["D%02d" % i] = [(cm + g + rt.normal(0, 0.02, f.size), cp - 360.0 * f * tau + rt.normal(0, 0.5, f.size))
                                   for _ in range(3)]
            dt["REV"] = [(cm + rt.normal(0, 0.02, f.size), cp + 180.0 + rt.normal(0, 0.5, f.size)) for _ in range(3)]
            pt = os.path.join(td, "t14_%d.csv" % sd)
            _write_csv(pt, f, dt, hdr)
            rr = analyse([pt], _args(mc=20, keep_outliers=True), out=quiet)
            kk = rr["drivers"].index("REV")
            npol += bool(rr["pol"][kk])
            nfalse += sum(bool(rr["pol"][j]) for j, d in enumerate(rr["drivers"]) if d != "REV")
        check("T14 相位卷绕回归: 紧批中反接副本 POLARITY? 20/20，正常只 0 误标", npol == 20 and nfalse == 0,
              "(%d/20, 误标 %d)" % (npol, nfalse))
        # T14b gross-delay regression (critic delta MINOR-1): normal polarity + gross delay offset must NOT be POLARITY?
        #      (may be OUTLIER); reversed + gross delay must still be POLARITY?. Pre-fix code flagged +400/-300 us.
        rg = np.random.default_rng(11)
        fg_, dg = _synth(rg, 18)
        gross = {"DLY+260": ("D05", 260e-6, 0.0), "DLY-300": ("D07", -300e-6, 0.0), "DLY+400": ("D08", 400e-6, 0.0),
                 "DLY-400": ("D09", -400e-6, 0.0), "DLY+600": ("D10", 600e-6, 0.0), "REV+300": ("D06", 300e-6, 180.0),
                 "REV-400": ("D11", -400e-6, 180.0)}
        for nm, (src, dly, flip) in gross.items():
            dg[nm] = [(m, p - 360.0 * fg_ * dly + flip) for m, p in dg[src]]
        pg = os.path.join(td, "t14b.csv")
        _write_csv(pg, fg_, dg, hdr)
        rgx = analyse([pg], _args(mc=20, keep_outliers=True), out=quiet)
        polset = {d for k, d in enumerate(rgx["drivers"]) if rgx["pol"][k]}
        check("T14b 粗延时回归: 正常极性 +260/-300/±400/+600 us 不标 POLARITY?，反接+粗延时仍标",
              polset == {"REV+300", "REV-400"}, "(POLARITY? = %s)" % sorted(polset))

        # T7 Van Trees analytic vs Monte Carlo (random assembly, no trims): expected power ratio agreement
        rng7 = np.random.default_rng(3)
        f7, drv7 = _synth(rng7, 24, gain_sd=0.6, delay_sd_us=10.0)
        p7 = os.path.join(td, "t7.csv")
        _write_csv(p7, f7, drv7, hdr)
        r = analyse([p7], _args(mc=4000), out=quiet)
        diffs = []
        for bb in r["bands"]:
            m = band_mask(r["fgrid"], bb)
            e0, ep, _, _ = analytic_random(r["Lpool"], r["w8"], r["fgrid"], 90.0)
            ra = db(e0[m].mean() / ep[m].mean())
            rm = db(r["P0mc"][m].mean() / r["Psmc"][90.0][m].mean())
            diffs.append(abs(ra - rm))
        check("T7 解析(Van Trees+有限总体) vs MC 期望功率比 < 0.5 dB", max(diffs) < 0.5, "(max %.3f dB)" % max(diffs))

        # T15 as-built mode: T0 equal to the paired table reproduces the paired prediction; errors are rejected
        r = analyse([p7], _args(mc=100), out=quiet)
        t0 = os.path.join(td, "t0.csv")
        with open(t0, "w", encoding="utf-8") as fp:
            fp.write("pos,driver_id\n")
            for c in range(8):
                a, b, _ = r["table"][c]
                fp.write("%d,%s\n%d,%s\n" % (c, r["pool_ids"][a], 15 - c, r["pool_ids"][b]))
        r2 = analyse([p7], _args(mc=100, as_built=t0), out=quiet)
        dab = max(abs(r2["asbuilt"][1][(bb, 90.0)][2][0] - r2["paired_trim"][(bb, 90.0)][2][0]) for bb in r2["bands"])
        check("T15 现装配=配对表 → 现装配+修整预测 == 配对+修整", dab < 1e-9, "(max %.1e dB)" % dab)
        bad_t0 = os.path.join(td, "t0bad.csv")
        with open(bad_t0, "w", encoding="utf-8") as fp:
            fp.write("pos,driver_id\n" + "".join("%d,D%02d\n" % (p, p) for p in range(15)) + "15,NOPE\n")
        try:
            analyse([p7], _args(mc=50, as_built=bad_t0), out=quiet)
            ok = False
        except InputError:
            ok = True
        check("T15 T0 含无数据 ID → 输入不可用", ok)

        # T17 alternative assignment rule: same 8 pairs, only the channel order may differ
        ra_ = analyse([p7], _args(mc=50, assign="resid"), out=quiet)
        s1 = sorted(tuple(sorted((ra_["pool_ids"][a], ra_["pool_ids"][b]))) for a, b, _ in ra_["table"])
        s2 = sorted(tuple(sorted((ra_["pool_ids"][a], ra_["pool_ids"][b]))) for a, b, _ in ra_["table_other"])
        check("T17 上位规则 resid 与 d: 同一组 8 对，只换位置", s1 == s2)

        # T8 determinism
        ra_ = analyse([p7], _args(mc=300, seed=5), out=quiet)["mc"]["trim"][(2000.0, 90.0)]
        rb_ = analyse([p7], _args(mc=300, seed=5), out=quiet)["mc"]["trim"][(2000.0, 90.0)]
        rc_ = analyse([p7], _args(mc=300, seed=6), out=quiet)["mc"]["trim"][(2000.0, 90.0)]
        check("T8 同 seed 结果逐位相同 / 异 seed 不同", np.array_equal(ra_, rb_) and not np.array_equal(ra_, rc_))

        # T9 magnitude-only fallback: runs, flagged, and is BLIND to the reversed driver (documents the limit)
        p9 = os.path.join(td, "t9.csv")
        _write_csv(p9, f6, drv6, hdr, phase=False)
        r = analyse([p9], _args(), out=quiet)
        check("T9 幅度-only: 可跑且 WARN 标明", (not r["has_phase"]) and any("幅度-only" in w for w in r["warns"]))
        check("T9 幅度-only 对反极性盲（BAD_POL 不被标 = 退路的已知盲区）",
              "BAD_POL" not in {d for k, d in enumerate(r["drivers"]) if r["flag"][k]})

        # T10 REW import
        rd = os.path.join(td, "rew")
        os.makedirs(rd)
        for did in ("A1", "A2"):
            for rep in (1, 2):
                with open(os.path.join(rd, "%s_r%d.txt" % (did, rep)), "w", encoding="utf-8") as fp:
                    fp.write("* Measurement data measured by REW (synthetic)\n* Freq(Hz), SPL(dB), Phase(degrees)\n")
                    for k in range(f.size):
                        fp.write("%.6f %.3f %.3f\n" % (f[k], 85.0, -10.0))
        hp = os.path.join(td, "hdr.txt")
        with open(hp, "w", encoding="utf-8") as fp:
            fp.write("date: synthetic\n# jig_id: J0\n")
        oc = os.path.join(td, "imported.csv")
        nf, nr = import_rew(rd, hp, oc)
        h, rows = read_dataset_csv(oc)
        check("T10 REW 导入: 4 文件、行数、头块", nf == 4 and nr == 4 * f.size and len(rows) == nr and h.get("jig_id") == "J0")

        # T11 input errors -> InputError (exit 2)
        drvx = dict(list(drv.items())[:16])
        px = os.path.join(td, "tx.csv")
        _write_csv(px, f, drvx, hdr)
        with open(px, "a", encoding="utf-8") as fp:
            fp.write("EXTRA,1,1000.5,85,0\n")                       # different grid for one measurement
        try:
            analyse([px], _args(), out=quiet)
            ok = False
        except InputError:
            ok = True
        check("T11 网格不一致 → 输入不可用", ok)
        sel = (f > 1200) & (f < 3000)
        drvs = {k: [(m[sel], p[sel]) for m, p in v] for k, v in drvx.items()}
        ps = os.path.join(td, "ts.csv")
        _write_csv(ps, f[sel], drvs, hdr)
        try:
            analyse([ps], _args(), out=quiet)
            ok = False
        except InputError:
            ok = True
        check("T11 频率覆盖不足 → 输入不可用", ok)
        drv15 = dict(list(drv.items())[:15])
        p15 = os.path.join(td, "t15.csv")
        _write_csv(p15, f, drv15, hdr)
        try:
            analyse([p15], _args(), out=quiet)
            ok = False
        except InputError:
            ok = True
        check("T11 可用喇叭 < 16 → 输入不可用", ok)

        # T12 reference-below-target warning logic (no number asserted)
        r = analyse([p1], _args(), out=quiet)
        need = any(r["ideal"][(bb, 90.0)][2][0] < 30.0 for bb in r["bands"])
        has = any("无误差各向同性模型值" in w for w in r["warns"])
        check("T12 无误差参考<目标 ⇔ 出 WARN", need == has)
        r2 = analyse([p1], _args(chebwin=40.0), out=quiet)
        need2 = any(r2["ideal"][(bb, 90.0)][2][0] < 30.0 for bb in r2["bands"])
        has2 = any("无误差各向同性模型值" in w for w in r2["warns"])
        check("T12 候选表(chebwin 40)同一逻辑", need2 == has2)

    n_fail = sum(1 for _, ok, _ in results if not ok)
    print("selftest: %d/%d PASS%s" % (len(results) - n_fail, len(results), "" if n_fail == 0 else "  <-- %d FAIL" % n_fail))
    return 0 if n_fail == 0 else 1


# ---------------------------------------------------------------------------------------------
def main(argv=None):
    _console_safe()
    ap = argparse.ArgumentParser(
        prog="s7_driver_pairing.py",
        description="S7 侧抑线：逐只喇叭复响应 → 配对/上位/修整 + ±90° R90 模型预测（随机 vs 现装配 vs 配对）。"
                    "手册 sprint7/docs/S7_DRIVER_MATCHING_RUNBOOK.md。预测 = [L2 模型 on L1 输入]，只作相对比较。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码: 0 无 WARN / 1 有 WARN / 2 输入不可用。selftest: 0 PASS / 1 FAIL。\n"
               "Windows: py -m pip install numpy 之后 py s7_driver_pairing.py ...（不需要 scipy）。")
    ap.add_argument("csv", nargs="*", help="实测 CSV（手册 §5 格式；可多文件）")
    ap.add_argument("--schema", action="store_true", help="打印 CSV 模板（占位符，无数值）")
    ap.add_argument("--selftest", action="store_true", help="合成数据自检（系统临时目录，退出即删）")
    ap.add_argument("--import-rew", metavar="DIR", help="合并 DIR 下 REW 导出 <driver_id>_r<rep>.txt → -o CSV")
    ap.add_argument("--header", metavar="TXT", help="--import-rew 用：头块文本（key: value 每行一条）")
    ap.add_argument("-o", "--output", metavar="CSV", help="--import-rew 输出路径")
    ap.add_argument("--as-built", metavar="T0.csv", help="现装配（pos,driver_id 16 行）：另外预测现装配的 R90（恢复 vs 重配决策用）")
    ap.add_argument("--assign", choices=("d", "resid"), default="d",
                    help="上位规则：d = 对内距离最小的对 → 最高权重（默认）；resid = 修整后残差最小的对 → 最高权重。另一规则也会打印一行")
    ap.add_argument("--bands", default=",".join("%g" % b for b in DEFAULT_BANDS),
                    help="1/3 oct 带中心 Hz（默认口径 7 带 1000..4000；分析区间 = 带边并集）")
    ap.add_argument("--angles", default="90", help="侧向角 deg，逗号分隔（默认 90 → ±90°）")
    ap.add_argument("--ppo", type=int, default=48, help="分析网格每倍频程点数（默认 48）")
    ap.add_argument("--weights", help="权重 CSV（需 ch 列 + --weight-col 列；默认冻结 Dolph-20）")
    ap.add_argument("--weight-col", default=W8_COL, help="权重列名（默认 %s）" % W8_COL)
    ap.add_argument("--w8", help="手给 8 个权重 c0..c7，逗号分隔（候选，非冻结）")
    ap.add_argument("--chebwin", type=float, help="用 chebwin(16, AT dB) 归一作候选表（numpy 实现；候选，非冻结）")
    ap.add_argument("--k-mad", type=float, default=3.5, help="离群阈 k：score > 中位 + k·1.4826·MAD（默认 3.5 [L4]）")
    ap.add_argument("--keep-outliers", action="store_true", help="离群不排除（仅看预测用）")
    ap.add_argument("--remove-delay", action="store_true", help="去掉每只线性相位斜率（无可信时间参考时用；延时散布随之不可见）")
    ap.add_argument("--mc", type=int, default=2000, help="随机装配 Monte Carlo 次数（默认 2000）")
    ap.add_argument("--seed", type=int, default=20260926, help="RNG seed（默认 20260926）")
    ap.add_argument("--target-db", type=float, default=30.0, help="目标线 dB（默认 30 = DEC-S7-SIDE30-01 ① 口径值，非期望值）")
    ap.add_argument("--noise-ratio", type=float, default=3.0, help="两两距离中位 < 此倍噪声底 → WARN（默认 3 [L4]）")
    ap.add_argument("--drift-ratio", type=float, default=0.5, help="参考喇叭漂移 > 此倍批散布中位 → WARN（默认 0.5 [L4]）")
    ap.add_argument("--out-dir", help="把 per_driver/pairing/spread_vs_freq 写成 CSV 到此目录（不给则只打印）")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.schema:
        print(schema_text())
        return 0
    try:
        if args.import_rew:
            if not args.output:
                raise InputError("--import-rew 需要 -o OUT.csv")
            nf, nr = import_rew(args.import_rew, args.header, args.output)
            print("导入 %d 个文件, %d 行 → %s" % (nf, nr, args.output))
            return 0
        if not args.csv:
            ap.print_help()
            return 2
        r = analyse(args.csv, args)
        return 1 if r["warns"] else 0
    except InputError as e:
        print("输入不可用: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
