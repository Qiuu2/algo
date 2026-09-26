# tree_filterbank.h 勘误旁注（本体为冻结件，字节不改）

> ⚠【勘误 2026-09-26 · DEC-S7-RETRACT-SUBBAND-01】
> 同目录 `tree_filterbank.h` 第 19 行"交叉点为 12k / 6k / 3k / 1.5k"和第 24 行"SB0 …（0 – ~1.5k …）"**是错的**。

**复算结果**（[L2 host]，不是 L1 实测；两条独立证据：critic 编译本冻结 C 源实跑；PM 用 numpy float 按 `tree_filterbank.c:108-205` 复刻）：

- 48 kHz 输入、3 级半带抽取，实际分界为 **3k / 6k / 12k**：
  - SB0 ≈ 0–3 kHz：≤2.5k 为 0 dB，3k 为 −6 dB，3.5k 为 −71 dB。
  - SB1 ≈ 3–6k，SB2 ≈ 6–12k，SB3 ≈ 12–24k。
  - 1 kHz 在 SB0 内部。
- detail 子带 = 本级 − interp2(下一级)（`tree_filterbank.c:161-163`），**没有延时对齐**。
  - 结果是全频段梳状残差，不是带通：SB1 在 500 Hz 为 +5.9 dB、1 kHz 为 −5.7 dB。
  - 只有 4 个子带增益全相等时，才能精确重建（telescoping）。
- **不能**在本树上按子带施加不同的加权、校准或延时，否则会出梳状失真。

**为什么不直接改头文件**：本文件的 md5 `7397ff0e02b9f9bd917c3093bc2b2912` 是上板前逐字节核对的身份码（`sprint3/audit/BENCH_OPS_CARD.md:13`、`sprint4/dsp/core_only/MANIFEST.md5`）。

**全文**：`sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md`
