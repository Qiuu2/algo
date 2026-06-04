/**
 * @file    dolph_w8_q15.h
 * @brief   F5-C: frozen 8-channel Dolph-Chebyshev -20dB broadside amplitude weight table.
 *
 * Plan : sprint4/dsp/fira/F5_F7_PLAN.md section 3 (F5-C).  Scope: F5-C only.
 * L-grade: [L2/dual-track] (desktop simulation; on-board L1 closure happens in F5-A
 *          when this table is bit-exactly applied at input-scale).
 *
 * +-----------------------------------------------------------------------------+
 * | WHAT THIS TABLE IS                                                           |
 * |  8 amplitude weights for the 8 broadside channels of the directional column. |
 * |  broadside -> delays = 0 (symmetric array, no phase term); pure amplitude.    |
 * |                                                                              |
 * | ELEMENT<->CHANNEL MAPPING  [L1/hardware]                                      |
 * |  center-symmetric {c, 15-c}: A-zone #n in series with B-zone #(17-n).         |
 * |  Source: knowledge_base/hardware_input/                                       |
 * |          (CJK filename) ..._extracted.md:40 ("A-zone#1 series B-zone#16 ...     |
 * |          16 speakers -> 8 channels via A/B series").                           |
 * |  The 16-element Dolph -20dB taper is center-symmetric (w[c]==w[15-c]); each   |
 * |  channel c drives one symmetric PAIR {element c, element 15-c}, so the 8      |
 * |  channel weights = the 8 DISTINCT half-aperture taper values w[0..7]          |
 * |  (edge c=0 -> center c=7). The mirror half is reproduced PHYSICALLY by the     |
 * |  A/B series pair, NOT in the DSP. 16-indep vs 8-pair equivalence proven:       |
 * |  sprint3/audit/m3_numpy_8pair_equiv.csv (BW/SLL diff 0.000e+00).               |
 * |                                                                              |
 * | DIRECTIVITY TARGET SERVED                                                      |
 * |  JY/T standard table-9 directivity (same baseline as acoustic a1/m1/m3):       |
 * |  Dolph-Chebyshev -20dB, N=16, d=55mm, broadside. Beam gate (quantized table,   |
 * |  N=16 mirrored, 1kHz): SLL = -20.00 dB, BW(-6dB full) = 29.269 deg (<=30 OK).  |
 * +-----------------------------------------------------------------------------+
 *
 * +-----------------------------------------------------------------------------+
 * | GENERATION (iron-rule-7 dual-track; tool calls/versions)                      |
 * |  Track-1 (acoustic main, same source as the acoustic baseline):               |
 * |    scipy.signal.windows.chebwin(16, at=20), normalized max=1.                  |
 * |    scipy 1.15.3 / numpy 2.2.6. IDENTICAL call+normalization to                  |
 * |    sprint3/audit/a1_static_weight_numpy.py  w_dolph(20).                        |
 * |  Track-2 (INDEPENDENT, does NOT call scipy chebwin):                           |
 * |    Barbiere/Stegen closed-form Dolph synthesis (factorial combinatorial sum),  |
 * |    sprint4/dsp/fira/gen_dolph_w8.py:track2_recurrence().                        |
 * |  Track-3 (cross-check): MATLAB chebwin(16,20) via matlab MCP.                   |
 * |  Evidence: float max|w_track1 - w_track2| = 2.340e-12 (8 channels);            |
 * |            Q15 quantized table BIT-IDENTICAL across all three tracks.          |
 * |  Generator script (committed evidence): sprint4/dsp/fira/gen_dolph_w8.py       |
 * |  Evidence CSV: sprint4/dsp/fira/dolph_w8_q15.csv                               |
 * |  Frozen at baseline commit 8b373f3 (F5/F7 plan critic-PASS).                   |
 * |  Same-source discipline (like hb63): values are frozen here, NOT recomputed    |
 * |  on board.                                                                    |
 * +-----------------------------------------------------------------------------+
 *
 * +-----------------------------------------------------------------------------+
 * | Q-FORMAT CHOICE = Q15  (justified vs Q31)                                      |
 * |  Weights apply at INPUT-SCALE (plan 1.2): per-channel input sample is scaled   |
 * |  by w_c BEFORE analyze: x_weighted = (int32_t)(((int64_t)w_q15 * x_q31) >> 15).|
 * |  The existing FIRA chain discipline is: Q15 coeff x Q31 state >> 15            |
 * |  (fir_coeffs_q31.h: g_hb63_fira32 is a Q15 prototype in an int32 container,    |
 * |  the >>15 truncation done core-side in fira_postscale). Choosing Q15 for the   |
 * |  weight makes the weight multiply the SAME arithmetic shape as the coeff       |
 * |  multiply and reuses the SAME >>15 truncation point -- no new truncation point |
 * |  ([ASSUME-A2], plan 1.2/4 / DP-01 discipline). Q31 would add a second, finer   |
 * |  truncation stage with no accuracy benefit at the beam gate (quant shift in    |
 * |  BW/SLL is < 1e-3, already negligible at Q15). So Q15 chosen.                   |
 * |  Container note: values live in int32_t. The center weight w=1.0 -> Q15 32768  |
 * |  = (1<<15) = INT16_MAX+1, which does NOT fit int16 but DOES fit the int32       |
 * |  container; (32768 * x_q31) >> 15 == x_q31 exactly (unity gain, NO growth), so  |
 * |  no overflow. Edge weights are smaller -> attenuation only.                     |
 * +-----------------------------------------------------------------------------+
 *
 * +-----------------------------------------------------------------------------+
 * | <=1.0 VERIFICATION (GAP-SAT closed-by-topology premise -> VERIFIED)            |
 * |  All 8 channel weights <= 1.0 in float (both tracks: max|w| = 1.000000) AND in |
 * |  the fixed-point container (max|w_q15| = 32768 = (1<<15), i.e. == 1.0, none     |
 * |  exceeds the Q15 unity value -> no value > 1.0). Therefore no single-channel    |
 * |  sample is amplified beyond its input magnitude -> no new INT32 saturation      |
 * |  risk is introduced in any per-channel link. This VERIFIES the residual premise |
 * |  of the GAP-SAT closed-by-topology disposition (decisions_log 2026-06-04,       |
 * |  plan 2.3 / 3.4): premise was `pending-on-F5C`, now PREMISE-VERIFIED.           |
 * |                                                                              |
 * | FG1 ALL-DISTINCT property: the 8 weights are pairwise distinct. NOTE the taper   |
 * |  is NOT monotonic: the very edge element c=0 (w=0.8668) is RAISED above its      |
 * |  neighbour c=1 (w=0.5043) -- this raised-edge is the characteristic Dolph-       |
 * |  Chebyshev edge behaviour, not an error. The minimum weight is c=1, the maximum  |
 * |  is the centre c=7. All 8 are distinct (verified). Any two equal channel weights |
 * |  would mean the weight does not differentiate channels -> false-green.           |
 * +-----------------------------------------------------------------------------+
 *
 * ASCII-only. CCES SHARC target (ADSP-21569).
 */
#ifndef ITC_DOLPH_W8_Q15_H
#define ITC_DOLPH_W8_Q15_H
#include <stdint.h>

#define DOLPH_W8_NCH      8
#define DOLPH_W8_QBITS   15          /* Q15: 1.0 -> (1<<15) = 32768 */
#define DOLPH_W8_ONE     (1 << DOLPH_W8_QBITS)   /* 32768 == weight 1.0 */

/* F5-C frozen 8-channel Dolph-Chebyshev -20dB broadside amplitude weights, Q15.
 * Index = channel c (0 = edge pair {0,15} ... 7 = center pair {7,8}).
 * Apply at input-scale: x_weighted_q31 = (int32_t)(((int64_t)g_dolph_w8_q15[c] * x_q31) >> 15).
 * Values are bit-identical across scipy chebwin / Barbiere recurrence / MATLAB chebwin.
 * DO NOT recompute on board (same-source discipline). All values <= 32768 (<= 1.0). */
static const int32_t g_dolph_w8_q15[DOLPH_W8_NCH] = {
    28404,   /* c=0  {0,15} edge    w=0.866829693 (raised-edge, > c=1; Dolph behaviour) */
    16525,   /* c=1  {1,14}         w=0.504310065 */
    20371,   /* c=2  {2,13}         w=0.621670438 */
    24031,   /* c=3  {3,12}         w=0.733379377 */
    27287,   /* c=4  {4,11}         w=0.832733104 */
    29934,   /* c=5  {5,10}         w=0.913514611 */
    31802,   /* c=6  {6,9}          w=0.970518658 */
    32768,   /* c=7  {7,8}  center  w=1.000000000 (== DOLPH_W8_ONE, unity gain) */
};

#endif /* ITC_DOLPH_W8_Q15_H */
