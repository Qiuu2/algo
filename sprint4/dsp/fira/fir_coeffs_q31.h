/**
 * @file    fir_coeffs_q31.h
 * @brief   F3: shared 63-tap halfband prototype loaded into the FIRA 32-bit fixed-point container.
 *
 * +-----------------------------------------------------------------------------+
 * | R14 conversion point (must be verified bit-by-bit on board): FIRA fixed-point|
 * |  coeff = Q15 halfband prototype sign-extended into a 32-bit container (high   |
 * |  bits = sign fill), fractional point semantics preserved. Mistaking it as     |
 * |  unsigned, or a misplaced left-shift alignment, makes overall gain off by 2^k |
 * |  -> golden CRC fails.                                                         |
 * |  Same-source discipline: values are copied from the frozen Q15 prototype       |
 * |  g_hb63_q15[] in core_only/include/fir_coeffs_hb63.h (NOT recomputed on board).|
 * +-----------------------------------------------------------------------------+
 *
 * Load rule (matches bench/fir_coeffs_hb63.h Q15 source):
 *   for k in 0..62:  hb_fira32[k] = (int32_t)hb_q15[k]   // sign-extend, point still at bit15
 *   DP-01 ASSUMPTION (F4 verifies, not desktop-decided): if F4 bit-by-bit shows FIRA SIGNED_INTEGER
 *   needs a different alignment (e.g. shift to bit31 = Q31-aligned coeff), switch to
 *     hb_fira32[k] = (int32_t)hb_q15[k] << 16  and adjust fira_postscale shift accordingly
 *   (paired; one of the composite-misalignment points, bench bit-by-bit locked).
 */
#ifndef ITC_FIR_COEFFS_Q31_H
#define ITC_FIR_COEFFS_Q31_H
#include <stdint.h>

#define FIR_HB63_FIRA_NTAPS   63

/* F3 (DP-01): 63-tap halfband prototype loaded into FIRA 32-bit coeff container.
 * Format = Q15 sign-extended into int32 (high bits = sign fill, fractional point still at bit15).
 * Values are bit-identical to the same-source Q15 prototype g_hb63_q15[] in
 *   core_only/include/fir_coeffs_hb63.h (center tap 16385). DO NOT recompute on board.
 *
 * DP-01 ASSUMPTION (F4 verifies, not desktop-decided): SIGNED_INTEGER MAC treats each coeff as
 *   an exact integer; the >>15 fractional truncation is done core-side in fira_postscale, not by FIRA.
 *   If F4 bit-by-bit shows scale is off by 2^k (gain mismatch -> golden CRC fails), switch the load
 *   alignment to  (int32_t)hb_q15[k] << 16  (Q31-aligned coeff) and adjust fira_postscale shift
 *   accordingly. Alignment vs postscale shift = bench-locked, paired (DP-01 sec.6). */
static const int32_t g_hb63_fira32[FIR_HB63_FIRA_NTAPS] = {
        -5,      0,     13,      0,    -27,      0,     48,      0,
       -78,      0,    120,      0,   -177,      0,    252,      0,
      -353,      0,    486,      0,   -665,      0,    916,      0,
     -1294,      0,   1942,      0,  -3389,      0,  10401,  16385,
     10401,      0,  -3389,      0,   1942,      0,  -1294,      0,
       916,      0,   -665,      0,    486,      0,   -353,      0,
       252,      0,   -177,      0,    120,      0,    -78,      0,
        48,      0,    -27,      0,     13,      0,     -5,
};

#endif /* ITC_FIR_COEFFS_Q31_H */
