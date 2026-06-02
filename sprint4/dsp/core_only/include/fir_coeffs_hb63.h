/**
 * @file    fir_coeffs_hb63.h
 * @brief   冻结 63-tap 同源 Q15 半带原型系数（自动生成，勿手改）
 *
 * 来源：tree_verify.c:40-60 make_halfband()（kaiser beta=6, cutoff fs/4,
 *       DC 归一, lround(h*32768) 钳位）— 与桌面 golden 同源。
 * 生成器：sprint4/dsp/core_only/host/gen_hb63.c（make_halfband 逐字符同源）
 * 用法：tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);
 *
 * CTO 盯点①：严禁用 sprint2/dsp/fir_coeffs.h(437-tap 废核)。harness 上电
 *            live 重算 make_halfband 并逐值核对本表，不一致即 FAIL。
 */
#ifndef ITC_FIR_COEFFS_HB63_H
#define ITC_FIR_COEFFS_HB63_H

#include <stdint.h>

#define FIR_HB63_NTAPS 63   /* 必须 == TFB_HB_TAPS；harness 断言 */
#define FIR_HB63_NNZ   33   /* 非零系数（含中心），半带跳零优化用 */

static const int16_t g_hb63_q15[FIR_HB63_NTAPS] = {
        -5,      0,     13,      0,    -27,      0,     48,      0,
       -78,      0,    120,      0,   -177,      0,    252,      0,
      -353,      0,    486,      0,   -665,      0,    916,      0,
     -1294,      0,   1942,      0,  -3389,      0,  10401,  16385,
     10401,      0,  -3389,      0,   1942,      0,  -1294,      0,
       916,      0,   -665,      0,    486,      0,   -353,      0,
       252,      0,   -177,      0,    120,      0,    -78,      0,
        48,      0,    -27,      0,     13,      0,     -5,
};

#endif /* ITC_FIR_COEFFS_HB63_H */
