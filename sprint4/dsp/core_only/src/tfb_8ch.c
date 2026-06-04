/**
 * @file    tfb_8ch.c
 * @brief   8ch independent filterbank wrapper -- see tfb_8ch.h
 *
 * F5-B structural change (plan sec.2): the digital-sum node is GONE. There is
 * NO cross-channel int32 summation here (grep-proof: no w_add_i32, no acc*
 * buffers, no sat_add across channels). Each channel runs its own
 * analyze -> synthesize, independently, into its own output row. This matches
 * the CTO-locked product topology (8 DACs, acoustic broadside superposition).
 *
 * Calls only the core tfb_channel_init / tfb_analyze / tfb_synthesize; does NOT
 * change their implementation/signature. Per-channel gain hook = 1.0 (Dolph
 * weights land in F5-C). With gain 1.0, out[c] == single-channel chain output
 * bit-exactly for identical input (plan sec.2 sanity / FG1).
 */
#include "tfb_8ch.h"
#include <string.h>

void tfb8_init(Tfb8State *st)
{
    int c;
    memset(st, 0, sizeof(*st));
    for (c = 0; c < TFB8_NCH; c++) {
        tfb_channel_init(&st->ana[c]);
        tfb_channel_init(&st->syn[c]);
    }
    st->initialized = 1u;
}

void tfb8_process(Tfb8State *st, const int32_t in[TFB8_NCH][TFB8_FRAME],
                  uint16_t frame, int32_t out[TFB8_NCH][TFB8_FRAME])
{
    int c;

    /* Per-channel subband scratch (intra-frame upper bound frame=64). */
    int32_t sb0[TFB8_FRAME/8], sb1[TFB8_FRAME/4], sb2[TFB8_FRAME/2], sb3[TFB8_FRAME];

    /* 8 independent chains: analyze -> synthesize, gain 1.0, NO cross-channel op. */
    for (c = 0; c < TFB8_NCH; c++) {
        tfb_analyze(&st->ana[c], in[c], frame, sb0, sb1, sb2, sb3);
        /* gain hook = 1.0 (subbands pass through unscaled until F5-C weights). */
        tfb_synthesize(&st->syn[c], sb0, sb1, sb2, sb3, frame, out[c]);
    }
}
