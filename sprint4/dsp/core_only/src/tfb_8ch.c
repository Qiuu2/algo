/**
 * @file    tfb_8ch.c
 * @brief   8ch broadside DAS 包裹层实现 — 见 tfb_8ch.h
 *
 * ⚠️ 仅调用核 tfb_channel_init / tfb_analyze / tfb_synthesize，不改其实现/签名。
 *    broadside 求和点用核内 sat_add_i32 同纪律（这里在包裹层重复同一钳位逻辑，
 *    因核的 sat_add_i32 是 static；语义与 tree_filterbank.c:55-61 一致）。
 */
#include "tfb_8ch.h"
#include <string.h>

/* broadside 求和饱和钳位：语义同 tree_filterbank.c:55 sat_add_i32。
 * 注：unsat 构建（-DTFB_DISABLE_SAT）下退化为环绕，与核 unsat 纪律一致。 */
#ifdef TFB_DISABLE_SAT
static inline int32_t w_add_i32(int32_t a, int32_t b) { return (int32_t)(a + b); }
#else
static inline int32_t w_add_i32(int32_t a, int32_t b)
{
    int64_t s = (int64_t)a + (int64_t)b;
    if (s > (int64_t)INT32_MAX) { return INT32_MAX; }
    if (s < (int64_t)INT32_MIN) { return INT32_MIN; }
    return (int32_t)s;
}
#endif

void tfb8_init(Tfb8State *st)
{
    int c;
    memset(st, 0, sizeof(*st));
    for (c = 0; c < TFB8_NCH; c++) {
        tfb_channel_init(&st->ana[c]);
    }
    tfb_channel_init(&st->syn);
    st->initialized = 1u;
}

void tfb8_process(Tfb8State *st, const int32_t in[TFB8_NCH][TFB8_FRAME],
                  uint16_t frame, int32_t *out)
{
    uint16_t f0 = frame, f1 = frame/2u, f2 = frame/4u, f3 = frame/8u;
    uint16_t i;
    int c;

    /* 每通道子带缓冲 + broadside 累加缓冲（帧内静态上限 frame=64） */
    int32_t sb0[TFB8_FRAME/8], sb1[TFB8_FRAME/4], sb2[TFB8_FRAME/2], sb3[TFB8_FRAME];
    int32_t acc0[TFB8_FRAME/8], acc1[TFB8_FRAME/4], acc2[TFB8_FRAME/2], acc3[TFB8_FRAME];

    memset(acc0, 0, sizeof(acc0));
    memset(acc1, 0, sizeof(acc1));
    memset(acc2, 0, sizeof(acc2));
    memset(acc3, 0, sizeof(acc3));

    /* 分析 ×8 + broadside 各子带等增益(1.0)求和（增益钩子=1.0，不接 Dolph） */
    for (c = 0; c < TFB8_NCH; c++) {
        tfb_analyze(&st->ana[c], in[c], frame, sb0, sb1, sb2, sb3);
        for (i = 0u; i < f3; i++) acc0[i] = w_add_i32(acc0[i], sb0[i]);
        for (i = 0u; i < f2; i++) acc1[i] = w_add_i32(acc1[i], sb1[i]);
        for (i = 0u; i < f1; i++) acc2[i] = w_add_i32(acc2[i], sb2[i]);
        for (i = 0u; i < f0; i++) acc3[i] = w_add_i32(acc3[i], sb3[i]);
    }

    /* 合成 ×1（broadside DAS 单路输出），独立 syn 状态 */
    tfb_synthesize(&st->syn, acc0, acc1, acc2, acc3, frame, out);
}
