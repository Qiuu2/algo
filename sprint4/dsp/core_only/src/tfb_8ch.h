/**
 * @file    tfb_8ch.h
 * @brief   8ch broadside DAS 包裹层（core-only G2 适配）— 核外层包裹
 *
 * ⚠️ 不碰算法核签名/算法：只在 tree_filterbank.c 的 tfb_* 之上做 8ch 循环 +
 *    broadside 等增益求和（增益钩子=1.0）+ 合成×1。核 verbatim 复制（md5 一致）。
 *
 * 结构（计划 §1 G2）：
 *   8 份 TreeChannelState（分析）+ 1 份独立 syn 状态（合成×1，参 tree_verify.c:70）。
 *   帧回调：for c in 0..7  tfb_analyze(&g_ana[c], in[c], ...);
 *           broadside 各子带 sat_add_i32 求和（沿用核饱和纪律，避免 8 路叠加溢出）;
 *           tfb_synthesize(&g_syn, sb_sum..., out)  ×1。
 */
#ifndef ITC_TFB_8CH_H
#define ITC_TFB_8CH_H

#include <stdint.h>
#include "tree_filterbank.h"

#define TFB8_NCH    8
#define TFB8_FRAME  64   /* 8 的倍数；与 tree_verify FRAME 一致 */

/* 8ch broadside 包裹状态（核外层；不修改 TreeChannelState 定义） */
typedef struct {
    TreeChannelState ana[TFB8_NCH];   /* 8 路阵元分析状态，严格独立（R-G2-2） */
    TreeChannelState syn;             /* 合成单路（broadside DAS 输出 ×1） */
    uint8_t          initialized;
} Tfb8State;

/** @brief 初始化 8ch 包裹（清零全部子状态）。 */
void tfb8_init(Tfb8State *st);

/**
 * @brief 一帧 8ch broadside DAS：分析×8 → 各子带等增益(1.0)求和 → 合成×1。
 * @param[in]  st     8ch 包裹状态
 * @param[in]  in     8 路输入 [TFB8_NCH][frame] @48kHz Q31
 * @param[in]  frame  帧长（8 的倍数）
 * @param[out] out    重建单路 [frame] @48kHz Q31
 */
void tfb8_process(Tfb8State *st, const int32_t in[TFB8_NCH][TFB8_FRAME],
                  uint16_t frame, int32_t *out);

#endif /* ITC_TFB_8CH_H */
