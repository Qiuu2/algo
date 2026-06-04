/**
 * @file    tfb_8ch.h
 * @brief   8ch independent filterbank wrapper (core-only G2) -- 8-in-8-out
 *
 * F5-B structural change (plan sprint4/dsp/fira/F5_F7_PLAN.md sec.2): the
 * former 8-in-1-out digital-sum wrapper (per-subband w_add_i32 across channels
 * + single synthesize) was a WCET-era verification wrapper, NOT product
 * datapath. CTO-locked product topology = 8 channels each output to its own
 * DAC (each driving an A/B series element pair); broadside = ACOUSTIC
 * superposition, NO digital sum in the DSP. This wrapper now mirrors that:
 *   for c in 0..7: tfb_analyze(&ana[c], in[c]) -> tfb_synthesize(&syn[c], out[c])
 * Per-channel, fully independent, zero cross-channel ops (NO int32 sum node).
 *
 * Does NOT touch the algorithm core (tree_filterbank.c tfb_* signatures /
 * implementation; core stays verbatim, md5 identical). The single-channel
 * tfb_analyze/tfb_synthesize chain is the frozen golden (S2 CRC 0x90556BC7);
 * with gain 1.0, out[c] for channel c MUST equal that single-channel chain
 * bit-exactly for identical input (the F5-B sanity, plan sec.2 / FG1).
 *
 * Per-channel gain hook: held at 1.0 here; Dolph-Chebyshev -20dB per-channel
 * weights land in F5-C (not present in DSP code yet). Removing the sum node
 * means broadside summation no longer exists in the DSP -> GAP-SAT closed by
 * topology (residual premise "all weights <= 1.0" pending-on-F5C, see
 * decisions_log.md).
 */
#ifndef ITC_TFB_8CH_H
#define ITC_TFB_8CH_H

#include <stdint.h>
#include "tree_filterbank.h"

#define TFB8_NCH    8
#define TFB8_FRAME  64   /* multiple of 8; same as tree_verify FRAME */

/* 8ch independent wrapper state (does NOT modify TreeChannelState). */
typedef struct {
    TreeChannelState ana[TFB8_NCH];   /* 8 per-element analyze states, strictly independent */
    TreeChannelState syn[TFB8_NCH];   /* 8 per-channel synthesize states, strictly independent */
    uint8_t          initialized;
} Tfb8State;

/** @brief Init 8ch wrapper (zero all sub-states). */
void tfb8_init(Tfb8State *st);

/**
 * @brief One frame, 8 independent channels: per-channel analyze -> synthesize.
 *        NO cross-channel sum (product topology = 8 DACs, acoustic superposition).
 * @param[in]  st     8ch wrapper state
 * @param[in]  in     8 input rows [TFB8_NCH][frame] @48kHz Q31
 * @param[in]  frame  frame length (multiple of 8)
 * @param[out] out    8 output rows [TFB8_NCH][frame] @48kHz Q31 (one per channel)
 */
void tfb8_process(Tfb8State *st, const int32_t in[TFB8_NCH][TFB8_FRAME],
                  uint16_t frame, int32_t out[TFB8_NCH][TFB8_FRAME]);

#endif /* ITC_TFB_8CH_H */
