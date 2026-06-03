/**
 * @file    fir_coeffs_q31.h
 * @brief   【草案·占位·待台架冻结】F3：共享 63-tap 半带原型 → FIRA 32-bit 定点容器
 *
 * ┌───────────────────────────────────────────────────────────────────────┐
 * │ 🔴 R14 §4.2 转换点（必上板逐位）：FIRA 定点系数 = Q15 半带原型符号扩展     │
 * │  进 32-bit 容器（高位补符号），**小数点语义保持**。误当无符号/左移对齐错位 │
 * │  → 整体增益错 2^k → golden CRC 必挂。                                     │
 * │  本文件**不是真值**：真系数须由 fir_design_verify.py 导出、同源冻结（不上  │
 * │  板重算，core_only_migration_plan.md:91 同纪律）。下方为占位 0，台架填实。  │
 * │  🚫 禁用占位 0 跑回归并声称通过。                                          │
 * └───────────────────────────────────────────────────────────────────────┘
 *
 * 生成口径（待台架脚本，对齐 bench/fir_coeffs_hb63.h 的 Q15 源）：
 *   for k in 0..62:  hb_fira32[k] = (int32_t)hb_q15[k]   // 符号扩展，小数点仍在 bit15
 *   ⚠️ 若台架 F6 确定 FIRA SIGNED_INTEGER 需不同对齐（如左移到 bit31 = Q31 系数），
 *      则改 hb_fira32[k] = (int32_t)hb_q15[k] << 16，并相应调 fira_postscale 移位量
 *      （§4.3 三处复合错位之一，逐位回归定）。**对齐方式 = 台架逐位确认，非桌面拍板**。
 */
#ifndef ITC_FIR_COEFFS_Q31_H
#define ITC_FIR_COEFFS_Q31_H
#include <stdint.h>

#define FIR_HB63_FIRA_NTAPS   63

/* 🔴 占位（全 0）——台架用 fir_design_verify.py 导出真值替换。禁用占位跑 R14。 */
static const int32_t g_hb63_fira32[FIR_HB63_FIRA_NTAPS] = { 0 };

#endif /* ITC_FIR_COEFFS_Q31_H */
