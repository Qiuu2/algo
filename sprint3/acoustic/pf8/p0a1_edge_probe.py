#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L2 补充探针：表征'过渡区'(0.5<d/λ<1) 内 ±90° 边缘的栅瓣肩部抬升。
区分 Dolph 设计旁瓣底(-20dB) 与 接近 90° 的栅瓣肩部电平。"""
import numpy as np
from scipy.signal.windows import chebwin

C, N, D = 343.0, 16, 0.055
W = chebwin(N, at=20.0); W /= W.sum()
X = (np.arange(N) - (N - 1) / 2.0) * D
TH = np.radians(np.linspace(0, 90, 18001))
THETA = np.degrees(TH)

def af_db(freq):
    k = 2 * np.pi * freq / C
    af = sum(W[n] * np.exp(1j * k * X[n] * np.sin(TH)) for n in range(N))
    m = np.abs(af); m /= m.max()
    return 20 * np.log10(np.maximum(m, 1e-12))

print(f"{'f(Hz)':>6} {'d/λ':>6} {'电平@90°(dB)':>12} {'电平@85°(dB)':>12}  栅瓣肩部状态")
print("-" * 70)
for f in [3120, 3500, 4000, 4500, 5000, 5500, 6000, 6236, 6500, 7000, 8000]:
    db = af_db(f)
    e90 = db[-1]
    i85 = np.argmin(np.abs(THETA - 85))
    e85 = db[i85]
    ratio = D * f / C
    if ratio < 1.0:
        # 栅瓣中心在虚区 (sinθ>1)，可视区只看到其逼近90°的肩部
        state = "肩部在90°边缘，未成峰"
    else:
        gl = np.degrees(np.arcsin(C / (f * D)))
        state = f"完整栅瓣峰已入区 @ {gl:.1f}°"
    print(f"{f:>6} {ratio:>6.3f} {e90:>12.2f} {e85:>12.2f}  {state}")
