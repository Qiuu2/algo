# FIRA 定点数据通路 — HW 手册实证（F3 系数格式 + F4 后处理有据）

**文档 ID**：DOC-S4-FIRA-DP-01 ｜ 日期：2026-06-03 ｜ PM 直跑（HW Reference 实证）
**挂接**：R14 / DEC-S4-DSP-01 / DOC-S4-FIRA-IMPL-01 §3
**触发**：顾问针 1（"真系数=Q15 符号扩展 32-bit"是假设，待 HW 手册验）。**结论：假设不完整，已用证据修正。**

---

## 1. 出处（权威）
`ADSP-21569 SHARC+ Processor Hardware Reference` **§38-10「Fixed-Point Data Format」**（pdftotext line 75713-75724）逐字：
> "In fixed-point mode, the 32-bit input data or coefficient is treated as fixed-point. **A 32-bit fixed-point MAC operation generates an 80-bit result.** Fixed-point data or coefficients can be **unsigned integer, unsigned fractional and signed integer**."
> NOTE："the entire **80-bit result register is always written back in bursts of 3 × 32 bits**. The first word is the LSW, the second word is the MSW, and the third word is a 16-bit overflow… Therefore … **WINDOWSIZE = WINDOWSIZE × 3**.
> **If the signed fractional format is used, the output must be scaled by 2. The MAC does not right shift to remove the redundant sign bit. A final routine must decimate the output buffer to the desired samples.**"
> "Multi-iteration mode is not supported in this format. Therefore, the maximum TAP length is 1024."

ACM 下 `FIR_SGCTL` 可逐通道改 rounding/fixed-point 模式（line 75759-762）。

---

## 2. 对"Q15 符号扩展"假设的修正（证据驱动）
| 顾问假设 | HW 实证 | 修正 |
|---|---|---|
| 真系数 = Q15 符号扩展 32-bit | FIRA 做**精确整数 MAC**（coeff_int × data_int），**无内建分数右移**（"MAC does not right shift") | 符号扩展只是**系数装载**一环；**>>15 不在 FIRA 内** |
| FIRA 自带分数 shift/rounding？ | **否**——整数 MAC，精确 80-bit，无 rounding（截位由核内 >>做） | 我方 Q15×Q31→Q46 的 **>>15 必须核内自己做**（与 golden 同口径 = 算术右移截断）|
| 输出格式 | **80-bit 结果，3×32-bit 写回（LSW/MSW/overflow），WINDOWSIZE×3** | 输出 buf 须 **3×**；核内**从 3 字提取 80-bit → 取需要的位** |
| signed fractional | "must be scaled by 2 … decimate the output" | signed-fractional 需 **×2（补冗余符号位）+ decimate** |

**🎯 R14 利好（证据带来的信心）**：FIRA 的 MAC 是**精确整数**（非有损 rounding）→ 只要核内"80-bit 提取 + >>15 + ×2 + decimate"做对，与 golden(`Σh·state>>15` 整数)**bit-exact 可达**。失配只会来自后处理对齐，**不是 FIRA 算错**。

---

## 3. F3 系数格式（据 §38-10 定，不再猜）
- **格式选 signed**（我方有符号 PCM）：driver 枚举 `ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER`（写 FIRCTL1 TC=1+FXD）。注：HW 列「unsigned int / unsigned fractional / signed int」三格式，**无独立"signed fractional"**——signed-fractional 语义靠 signed + ×2/decimate 后处理实现（NOTE）。
- **系数装载**：63-tap Q15 → 32-bit 容器。符号扩展 `(int32_t)hb_q15[k]`（小数点仍 bit15）**或** `<<16`（移到高位）——**哪种由 F4 单段逐位定**（取决于 FIRA 把 coeff 当多少位整数 × data；80-bit MAC 不关心小数点，小数点是核内 >> 量的事）。`fir_coeffs_q31.h` 占位 0，F4 定对齐后填。

## 4. F4 后处理（核内 Split-Task，据 §38-10）
FIRA 段输出 → 核内 `fira_postscale`：① 从 3×32-bit 提取 80-bit（LSW+MSW，overflow 检查）→ ② `>>15`（Q46→Q31，同 golden，算术右移）→ ③ signed-fractional **×2**（补冗余符号位）→ ④ **decimate**（WINDOWSIZE×3 → 目标样本）→ ⑤ Q31 饱和钳位（复用 `tree_filterbank.c` sat_*）。

## 5. 针 2 回应（调参 vs 架构）
上述 ×2 / >>15 / 80-bit 提取 / decimate **是后处理对齐 = gate 内正常 R14 迭代**（核内 `fira_postscale` 调，不碰滤波器结构/算法）→ **我在 F4 gate 内迭代,不每次失配都停**。**仅当**"不改核心算法/结构就够不到 bit-exact"（如发现 FIRA 整数 MAC 与我方某语义结构性不可调和）才停下问 CTO——以实测为准，早停也对。

## 6. 待台架（F4 定死）
- 系数对齐方式（符号扩展 vs `<<16`）+ 对应 `>>` 量；
- 80-bit 3 字提取的确切位选 + overflow 处理；
- ×2 与核内 `>>15` 复合的最终移位量；
- decimate 取偶/取奇相位（R14-6）。
**全部 F4 单段逐位定**（FIRA MAC 精确 → 可达 bit-exact，crc==0x90556BC7）。

---

*DOC-S4-FIRA-DP-01，PM 直跑 2026-06-03。HW Reference §38-10 实证：FIRA 精确整数 MAC→80-bit/3字写回/WINDOWSIZE×3/无内建右移/signed-fractional 需 ×2+decimate。修正"Q15 符号扩展"假设；F3 格式有据、F4 后处理有据。MAC 精确 → bit-exact 可达，失配在后处理对齐（gate 内调参）。C9 维持。*
