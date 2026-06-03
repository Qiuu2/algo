/**
 * @file    fira_tree.c
 * @brief   [DRAFT, uncompiled, real Legacy API, F2-F7 bench-side]
 *          FIRA 4-subband tree FIR - Split-Task orchestration (FIRA convolution + core-side fixed-point semantics)
 *
 * +-----------------------------------------------------------------------+
 * | HONESTY STATUS (hard constraint, do not delete): no SHARC toolchain   |
 * |  + no FIRA hardware on this host -> this file **cannot be compiled /   |
 * |  board-verified**. adi_fir_* = real Legacy signatures (archived header |
 * |  adi_fir_legacy_2156x.h); lifecycle mirrors official Legacy example    |
 * |  MCP.c:243-285. Each unverified assumption marked [ASSUME]/[L1/EZKIT]. |
 * |  Does NOT claim "compiled/bit-exact/measured cycle" -> all bench-side  |
 * |  (F2-F7).                                                              |
 * +-----------------------------------------------------------------------+
 *
 * Mode LEGACY; fixed-point Path B (runtime adi_fir_FixedPointEnable(SIGNED), after CreateTask / before QueueTask).
 */

#include "fira_tree.h"
#include <string.h>
#include <stdint.h>

/* ============================================================
 * Core-side fixed-point primitives (Split-Task core side)
 * ------------------------------------------------------------
 * These must stay in core: FIRA only does MAC, no Q31 saturation / vector sub / vector add semantics.
 *   Semantics bit-identical to tree_filterbank.c:47-61 (sat_i64_to_i32 / sat_add_i32).
 *   R14 comparison verifies FIRA path numerically equivalent to core path (crc==0x90556BC7).
 * ============================================================ */
#ifdef TFB_DISABLE_SAT
static inline int32_t f_sat_i64_to_i32(int64_t v) { return (int32_t)v; }
static inline int32_t f_sat_add_i32(int32_t a, int32_t b) { return (int32_t)(a + b); }
#else
static inline int32_t f_sat_i64_to_i32(int64_t v)
{
    if (v > (int64_t)INT32_MAX) { return INT32_MAX; }
    if (v < (int64_t)INT32_MIN) { return INT32_MIN; }
    return (int32_t)v;
}
static inline int32_t f_sat_add_i32(int32_t a, int32_t b)
{
    int64_t s = (int64_t)a + (int64_t)b;
    if (s > (int64_t)INT32_MAX) { return INT32_MAX; }
    if (s < (int64_t)INT32_MIN) { return INT32_MIN; }
    return (int32_t)s;
}
#endif

/* ---- Shared FIRA 32-bit halfband coeffs (F3 frozen, sign-extended from Q15, R14-2) ---- */
static const int32_t *g_hb_fira = 0;
static uint16_t        g_hb_fira_n = 0;

void fira_tree_set_coeffs(const int32_t *hb_coef_fira32, uint16_t ntaps)
{
    /* R14-2: hb_coef_fira32 must be frozen once by fir_coeffs_q31.h,
     *   = Q15 sign-extended into 32-bit container (sign-fill high bits), fractional-point semantics preserved.
     *   Bench bit-by-bit verify: mistaking as unsigned / left-shift align misplacement -> overall gain off by 2^k -> CRC fails. */
    g_hb_fira   = hb_coef_fira32;
    g_hb_fira_n = ntaps;
}

void fira_channel_init(FiraChannelState *ch, uint16_t frame)
{
    uint16_t f1 = frame/2u, f2 = frame/4u, f3 = frame/8u;
    memset(ch, 0, sizeof(*ch));
    /* Segment metadata (order = FIRA_IMPL.md S2 table): 3 dec(down) + 3 ana_int(up) + 3 syn_int(up) */
    ch->kind[0] = FIRA_SEG_DEC; ch->window[0] = f1;   /* ana_dec[0] f0->f1 */
    ch->kind[1] = FIRA_SEG_DEC; ch->window[1] = f2;   /* ana_dec[1] f1->f2 */
    ch->kind[2] = FIRA_SEG_DEC; ch->window[2] = f3;   /* ana_dec[2] f2->f3 */
    ch->kind[3] = FIRA_SEG_INT; ch->window[3] = f2;   /* ana_int[2] f3->f2 */
    ch->kind[4] = FIRA_SEG_INT; ch->window[4] = f1;   /* ana_int[1] f2->f1 */
    ch->kind[5] = FIRA_SEG_INT; ch->window[5] = frame;/* ana_int[0] f1->f0 */
    ch->kind[6] = FIRA_SEG_INT; ch->window[6] = f2;   /* syn_int[2] f3->f2 */
    ch->kind[7] = FIRA_SEG_INT; ch->window[7] = f1;   /* syn_int[1] f2->f1 */
    ch->kind[8] = FIRA_SEG_INT; ch->window[8] = frame;/* syn_int[0] f1->f0 */
    ch->initialized = 1u;
}

/* ============================================================
 * SA. ADI_FIR_CHANNEL_INFO construction (real Legacy fields, mirrors MCP.c:128-153 + legacy hdr:46-54)
 * ------------------------------------------------------------
 * In Legacy mode CHANNEL_INFO has **no inline fixed-point fields** (bFixedEnable/eFixedFormat are
 *   inside example's #if ACM, compiled out in Legacy, MCP.c:135-142; legacy hdr:45 notes). Fixed-point set via
 *   runtime adi_fir_FixedPointEnable(SIGNED) (after CreateTask / before QueueTask, see SB).
 * Field order strictly per legacy hdr ADI_FIR_CHANNEL_INFO (:46-54):
 *   nTapLength, nWindowSize, eSampling, nSamplingRatio,
 *   nCoefficientCount, pCoefficientIndex, nCoefficientModify,
 *   pOutputBuffBase, nOutputBuffCount, nOutputBuffModify, pOutputBuffIndex,
 *   pInputBuffBase,  nInputBuffCount,  nInputBuffModify,  pInputBuffIndex
 * ============================================================ */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
/**
 * Construct a Legacy ADI_FIR_CHANNEL_INFO for one halfband segment.
 *  @param kind   DEC->eSampling=DECIMATION; INT->INTERPOLATION (FIRA_IMPL.md S2)
 *  @param window output sample count (= frame/2^level)
 *  @param coeff  frozen 32-bit halfband coeff base (injected by fira_tree_set_coeffs)
 *  @param inbuf  input delay-line base, **layout must be nTapLength+nWindowSize-1** (MCP.c:151)
 *  @param outbuf output buffer base (window samples)
 *
 * R14-3 (HIGH): fixed-point format not set here (no Legacy field); set at runtime by adi_fir_FixedPointEnable
 *   (hTask, SIGNED_INTEGER). signed-fractional used as SIGNED_INTEGER -> fractional-point
 *   semantics lost, needs x2 scaling + decimate post-processing + core-side >>15 unification (see fira_postscale_*).
 *   **This mapping cannot be confirmed on desktop, must do board bit-by-bit regression golden 0x90556BC7**.
 */
static ADI_FIR_CHANNEL_INFO fira_make_channel(FiraSegKind kind, uint16_t window,
                                              const int32_t *coeff,
                                              const int32_t *inbuf, int32_t *outbuf)
{
    ADI_FIR_CHANNEL_INFO ci;
    memset(&ci, 0, sizeof(ci));
    ci.nTapLength      = g_hb_fira_n;                      /* 63 (legacy hdr:47) */
    ci.nWindowSize     = window;                           /* output sample count (:48) */
    /* Decimation/interpolation mode (per-channel, Legacy supported, F1 S3). Enum see legacy hdr:33-35.
     * [ASSUME] ADI examples all SINGLE_RATE, no dec/int example -> phase/x2 behavior F4 board-verify. */
    ci.eSampling       = (kind == FIRA_SEG_DEC) ? ADI_FIR_SAMPLING_DECIMATION
                                                : ADI_FIR_SAMPLING_INTERPOLATION;
    ci.nSamplingRatio  = FIRA_RATIO;                       /* 2 (integer, legacy hdr:50) */
    /* -- coeffs (legacy hdr:51) -- */
    ci.nCoefficientCount  = g_hb_fira_n;
    ci.pCoefficientIndex  = (void *)coeff;
    ci.nCoefficientModify = 1;
    /* -- output (legacy hdr:52) -- */
    ci.pOutputBuffBase  = (void *)outbuf;
    ci.nOutputBuffCount = window;
    ci.nOutputBuffModify = 1;
    ci.pOutputBuffIndex = (void *)outbuf;
    /* -- input (legacy hdr:53): layout nTapLength+nWindowSize-1 (MCP.c:151) -- */
    ci.pInputBuffBase  = (void *)inbuf;
    ci.nInputBuffCount = (uint32_t)g_hb_fira_n + window - 1u;
    ci.nInputBuffModify = 1;
    ci.pInputBuffIndex = (void *)inbuf;
    return ci;
}
#endif /* FIRA_USE_REAL_ADI_FIR_HEADER */

/* ============================================================
 * SB. Device / task lifecycle (real Legacy, mirrors MCP.c:243-285)
 * ------------------------------------------------------------
 * Chain: Open -> RegisterCallback -> CreateTask -> FixedPointEnable(SIGNED) -> QueueTask
 *     -> wait callback (FIRTaskDoneCount<N_TASKS, ALL_CHANNEL_DONE) -> Close.
 * Legacy completion event = ADI_FIR_EVENT_ALL_CHANNEL_DONE (MCP.c:103), main loop waits
 *   FIRTaskDoneCount < N_TASKS (MCP.c:282).
 * ============================================================ */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
static ADI_FIR_DEV_HANDLE  s_hFir = 0;
volatile uint32_t          g_FIRTaskDoneCount = 0;   /* set by callback (MCP.c:92,105, Legacy once per task) */

/* Completion callback: Legacy fires ALL_CHANNEL_DONE once after all channels of one task complete (MCP.c:96-107). */
static void fira_done_cb(void *pCBParam, ADI_FIR_EVENT Event, void *pArg)
{
    (void)pCBParam; (void)pArg;
    if (Event == ADI_FIR_EVENT_ALL_CHANNEL_DONE) {   /* Legacy (MCP.c:103) */
        g_FIRTaskDoneCount++;
    }
}
#endif

/* ============================================================
 * SB-template. F2-F4 single-channel bench starter template (compilable starter: runs once bench defines real header)
 * ------------------------------------------------------------
 * Run **full Legacy lifecycle + Path B fixed-point** of 1 DECIMATION halfband segment, verify:
 *   (a) lifecycle order correct (Open..Close no ADI_FIR_RESULT error);
 *   (b) Path B runtime FixedPointEnable(SIGNED) takes effect under Legacy (F1 S4 residual G2);
 *   (c) DECIMATION phase / x2 (R14-5/-6) -- compare out bit-by-bit to small-example golden.
 * Buffers passed by caller (in length in_count = ntaps+out_count-1, out length out_count).
 * [L1/EZKIT]: real adi_fir_* behavior bench-side; draft default build returns -1 (no FIRA, no faking).
 * ============================================================ */
int fira_single_channel_template(const int32_t *in, uint16_t in_count,
                                 int32_t *out, uint16_t out_count, uint16_t ntaps)
{
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    /* TaskMemory: real FIR_MEM_SIZE(N_CH) macro (legacy hdr:18). 1 channel -> FIR_MEM_SIZE(1).
     * #pragma align 32 (MCP.c:82-83; cache line alignment, else breaks bit-exact, see FIRA_IMPL.md SF4). */
    #pragma align 32
    static uint8_t s_taskMem[FIR_MEM_SIZE(1)];
    ADI_FIR_TASK_HANDLE hTask = 0;
    ADI_FIR_RESULT r;

    if (g_hb_fira == 0 || in == 0 || out == 0) { return -2; }

    /* 1 channel: DECIMATION r=2 (bench can switch INTERPOLATION to verify x2). */
    ADI_FIR_CHANNEL_INFO ch = fira_make_channel(FIRA_SEG_DEC, out_count,
                                                g_hb_fira, in, out);
    ch.nTapLength = ntaps; ch.nCoefficientCount = ntaps;
    ch.nInputBuffCount = (uint32_t)ntaps + out_count - 1u;
    (void)in_count;   /* caller guarantees in_count == ntaps+out_count-1 (layout self-check bench-side) */

    g_FIRTaskDoneCount = 0;

    r = adi_fir_Open(0u, &s_hFir);                          if (r != ADI_FIR_RESULT_SUCCESS) return 1;
    r = adi_fir_RegisterCallback(s_hFir, fira_done_cb, 0);  if (r != ADI_FIR_RESULT_SUCCESS) return 2;
    r = adi_fir_CreateTask(s_hFir, &ch, 1u, (void *)s_taskMem,
                           (uint32_t)FIR_MEM_SIZE(1), &hTask);
                                                            if (r != ADI_FIR_RESULT_SUCCESS) return 3;
    /* Path B: set fixed-point SIGNED after CreateTask / before QueueTask (F1 locked, do not change config header). */
    r = adi_fir_FixedPointEnable(hTask, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER);
                                                            if (r != ADI_FIR_RESULT_SUCCESS) return 4;
    r = adi_fir_QueueTask(hTask);                           if (r != ADI_FIR_RESULT_SUCCESS) return 5;

    /* Legacy: wait N_TASKS=1 ALL_CHANNEL_DONE callbacks (MCP.c:282). */
    while (g_FIRTaskDoneCount < 1u) { /* spin; bench can switch to idle/event wait */ }

    r = adi_fir_Close(s_hFir);  s_hFir = 0;                 if (r != ADI_FIR_RESULT_SUCCESS) return 6;
    return 0;
#else
    (void)in; (void)in_count; (void)out; (void)out_count; (void)ntaps;
    return -1;   /* No real header on this host: not executable, do not misuse as "verified". Returns 0 once bench defines real header. */
#endif
}

int fira_tree_setup(void)
{
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    /* Mirrors MCP.c:243-265: Open -> RegisterCallback -> CreateTask (per segment/channel grouping)
     *   -> FixedPointEnable(SIGNED) (per task, Path B).
     * [L1/EZKIT] TaskMemory must #pragma align 32 (MCP.c:82), allocate per real FIR_MEM_SIZE().
     *   Channel grouping (same-level multi-channel concurrency / cross-level callback chain) + per-task FixedPointEnable = F4/F5 bench-side. */
    ADI_FIR_RESULT r;
    r = adi_fir_Open(0u, &s_hFir);                         if (r != ADI_FIR_RESULT_SUCCESS) return 1;
    r = adi_fir_RegisterCallback(s_hFir, fira_done_cb, 0); if (r != ADI_FIR_RESULT_SUCCESS) return 2;
    /* adi_fir_CreateTask(...) + adi_fir_FixedPointEnable(hTask, SIGNED) grouped per segment:
     *   [ASSUME] see FIRA_IMPL.md SF2/SF4/SF5, full task orchestration bench-side. */
    return 0;
#else
    /* No real header on this host: setup not executable. Non-zero return means "not on target platform", do not misuse. */
    return -1;   /* Returns 0 once bench (F1) enables real header */
#endif
}

void fira_tree_teardown(void)
{
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    if (s_hFir) { adi_fir_Close(s_hFir); s_hFir = 0; }   /* call on real-time exit (MCP.c does not call explicitly) */
#endif
}

/* ============================================================
 * SC. R14 post-processing: signed-fractional alignment (FIRA_IMPL.md S3 R14-3/-5, high bit-deviation risk)
 * ------------------------------------------------------------
 * After FIRA 80-bit MR (SIGNED_INTEGER MAC) writeback, must unify with our core acc>>15 + x2.
 *   - DEC segment: core hb_push_filter = acc>>15 + sat (tree_filterbank.c:104).
 *   - INT segment: core = (acc>>15)*2 + sat (:127,130).
 *   x2 done only once (R14-5: FIRA INTERPOLATION zero-stuff x2 and signed-fractional x2 may
 *   compound twice -> gain off by 4x).
 *   [ASSUME] scaling factor / shift amount = pending F6 bench bit-by-bit alignment, desktop gives **semantic placeholder**, not fixed value.
 * ============================================================ */
static int32_t fira_postscale_dec(int64_t fira_mr)
{
    /* [ASSUME] bench-side: SIGNED_INTEGER MAC 80-bit MR -> Q31, must >>15 (same core truncation,
     *   toward negative infinity), must not use IEEE round (R14-1: truncate vs round differs +/-1 LSB -> CRC fails). */
    return f_sat_i64_to_i32(fira_mr >> 15);
}
static int32_t fira_postscale_int(int64_t fira_mr)
{
    /* [ASSUME] bench-side: x2 interpolation gain **only once** (R14-5). If FIRA hardware already x2, do not x2 here. */
    return f_sat_i64_to_i32((fira_mr >> 15) * 2);
}

/* ============================================================
 * SD. Frame-level Split-Task orchestration (draft placeholder)
 * ------------------------------------------------------------
 * Same signature as tfb_analyze/tfb_synthesize -> fira_regression can directly substitute for CRC comparison.
 *   No FIRA on this host -> cannot truly run. Draft gives **orchestration skeleton + core-side segments**; FIRA convolution segments marked in comments
 *   "QueueTask + wait ALL_CHANNEL_DONE here", bench (F4-F6) fills real calls. detail sub / synthesis add / saturation = in core.
 *
 *   Draft strategy (avoid faking verification): when FIRA_USE_REAL_ADI_FIR_HEADER undefined,
 *   FIRA convolution segments **unavailable**, these two functions keep only core-side part + segment annotation, produce no valid values
 *   (no faking bit-exact). Bench connects FIRA segments once real header enabled.
 *
 *   8ch x multi-segment extension = F5 (annotated, not fully expanded): these two functions handle single channel; 8ch broadside
 *   runs 8 single-channel analyze/synthesize each then sums in core via sat_add (reuse tfb_8ch.c),
 *   each path one set of ADI_FIR_CHANNEL_INFO + one FixedPointEnable, task grouping and concurrency bench-side.
 * ============================================================ */
void fira_tfb_analyze(FiraChannelState *ch, const int32_t *in, uint16_t frame,
                      int32_t *sb0, int32_t *sb1, int32_t *sb2, int32_t *sb3)
{
    uint16_t f0 = frame, f1 = frame/2u, f2 = frame/4u, f3 = frame/8u;
    uint16_t i;
    /* Per-level coarse / interp reconstruction buffers (same layout as tree_filterbank.c:143-144) */
    int32_t a1[256], a2[128], a3[64];
    int32_t r1[512], r2[256], r3[128];
    (void)ch; (void)fira_postscale_dec; (void)fira_postscale_int;

    /* -- FIRA segment (DECIMATION r=2, even phase reproduced by hardware skip, R14-6) --
     * [L1/EZKIT] bench: a1=FIRA_dec(in); a2=FIRA_dec(a1); a3=FIRA_dec(a2);
     *   (QueueTask seg0->ALL_CHANNEL_DONE->seg1->...->seg2; fira_postscale_dec restores Q31).
     *   Draft has no hardware -> produces no real a1/a2/a3 values; memset below is placeholder to prevent uninitialized read,
     *   does NOT mean values correct (R14 judged by bench crc). */
    memset(a1, 0, sizeof(a1)); memset(a2, 0, sizeof(a2)); memset(a3, 0, sizeof(a3));

    /* -- FIRA segment (INTERPOLATION r=2, reconstruct coarse for detail, x2 see fira_postscale_int) --
     * [L1/EZKIT] bench: r3=FIRA_int(a3); r2=FIRA_int(a2); r1=FIRA_int(a1); */
    memset(r1, 0, sizeof(r1)); memset(r2, 0, sizeof(r2)); memset(r3, 0, sizeof(r3));

    /* -- core-side (FIRA has no vector sub): detail = this level - interp2(lower level) -- */
    for (i = 0u; i < f2; i++) sb1[i] = a2[i] - r3[i];   /* SB1 detail @f2 (bit-identical tree_filterbank.c:161) */
    for (i = 0u; i < f1; i++) sb2[i] = a1[i] - r2[i];   /* SB2 detail @f1 (:162) */
    for (i = 0u; i < f0; i++) sb3[i] = in[i] - r1[i];   /* SB3 detail @f0 (:163) */
    for (i = 0u; i < f3; i++) sb0[i] = a3[i];           /* SB0 coarse @f3 (:164) */
}

void fira_tfb_synthesize(FiraChannelState *ch,
                         const int32_t *sb0, const int32_t *sb1,
                         const int32_t *sb2, const int32_t *sb3,
                         uint16_t frame, int32_t *out)
{
    uint16_t f0 = frame, f1 = frame/2u, f2 = frame/4u;
    uint16_t i;
    int32_t a2p[256], a1p[512];
    int32_t up3[128], up2[256], up1[512];
    (void)ch;

    /* -- FIRA segment (INTERPOLATION) + core-side synthesis add (sat_add, FIRA has no vector add) -- */
    /* [L1/EZKIT] bench: up3=FIRA_int(sb0); draft placeholder 0. */
    memset(up3, 0, sizeof(up3));
    for (i = 0u; i < f2; i++) a2p[i] = f_sat_add_i32(up3[i], sb1[i]);   /* bit-identical tree_filterbank.c:197 */

    /* [L1/EZKIT] bench: up2=FIRA_int(a2p); */
    memset(up2, 0, sizeof(up2));
    for (i = 0u; i < f1; i++) a1p[i] = f_sat_add_i32(up2[i], sb2[i]);   /* :201 */

    /* [L1/EZKIT] bench: up1=FIRA_int(a1p); */
    memset(up1, 0, sizeof(up1));
    for (i = 0u; i < f0; i++) out[i] = f_sat_add_i32(up1[i], sb3[i]);   /* :205 */
}
