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
#include "fir_coeffs_q31.h"   /* F3: real 63-tap Q15-sign-extended FIRA coeffs g_hb63_fira32 (DP-01) */
#include <string.h>
#include <stdint.h>
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
#include <sys/cache.h>        /* A5: CCES SHARC cache builtins (flush_data_buffer). CCES path
                               * SHARC/include/sys/cache.h, evidenced in 21569 .d files
                               * (knowledge_base/ezkit/vendor_docs/cces_examples dotd files).
                               * Guarded: desktop/#else host has no such header -> NOT pulled. */
#endif

/* ============================================================
 * Core-side fixed-point primitives (Split-Task core side)
 * ------------------------------------------------------------
 * These must stay in core: FIRA only does MAC, no Q31 saturation / vector sub / vector add semantics.
 *   Semantics bit-identical to tree_filterbank.c:47-61 (sat_i64_to_i32 / sat_add_i32).
 *   R14 comparison verifies the FIRA path is numerically equivalent to the core path.
 *   (RETIRED criterion: the old e2e crc==0x90556BC7 is telescoping-blind -> replaced by the
 *    per-SUBBAND criterion, DEC-S4-R14-GRANULARITY: F4 single-channel sb0..3==core (anchor
 *    0x2E0D8C6E) and F5-A per-channel sb0..3==core over chirp*w[c] (dolph_f5_goldens.h).)
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

/* ---- Shared FIRA 32-bit halfband coeffs (F3 frozen, sign-extended from Q15, R14-2) ----
 * Default to the real F3 coeffs (g_hb63_fira32, fir_coeffs_q31.h). Bench may override via
 *   fira_tree_set_coeffs (e.g. F2 arbitrary-coeff smoke). */
static const int32_t *g_hb_fira   = g_hb63_fira32;
static uint16_t        g_hb_fira_n = FIR_HB63_FIRA_NTAPS;

void fira_tree_set_coeffs(const int32_t *hb_coef_fira32, uint16_t ntaps)
{
    /* R14-2: hb_coef_fira32 must be frozen once by fir_coeffs_q31.h,
     *   = Q15 sign-extended into 32-bit container (sign-fill high bits), fractional-point semantics preserved.
     *   Bench bit-by-bit verify: mistaking as unsigned / left-shift align misplacement -> overall gain off by 2^k -> CRC fails. */
    g_hb_fira   = hb_coef_fira32;
    g_hb_fira_n = ntaps;
}

/* F3: explicitly (re)bind to the real frozen coeffs (call after any F2 smoke override). */
void fira_tree_use_real_coeffs(void)
{
    g_hb_fira   = g_hb63_fira32;
    g_hb_fira_n = FIR_HB63_FIRA_NTAPS;
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
 *   **This mapping cannot be confirmed on desktop, must do board bit-by-bit subband regression**
 *   (per-SUBBAND golden, DEC-S4-R14-GRANULARITY; the e2e 0x90556BC7 is RETIRED as the pass
 *    criterion -- telescoping-blind -- and survives only as fira_harness_selfcheck infra check).
 */
static ADI_FIR_CHANNEL_INFO fira_make_channel(FiraSegKind kind, uint16_t window,
                                              const int32_t *coeff,
                                              const int32_t *inbuf, int32_t *outbuf)
{
    ADI_FIR_CHANNEL_INFO ci;
    memset(&ci, 0, sizeof(ci));
    ci.nTapLength      = g_hb_fira_n;                      /* 63 (legacy hdr:47) */
    ci.nWindowSize     = window;                           /* OUTPUT sample count (:48) */
    /* [ASSUME A-orient] (board-locked, 2026-06-03): bit-exact requires FIRA's convolution tap
     *   orientation to MATCH the core hb_push_filter readout: y = sum_k h[k]*state[oldest..newest]
     *   (h[0] pairs with the OLDEST sample in the delay line, h[ntaps-1] with the NEWEST).  If FIRA
     *   pairs h[k] with the opposite end (reversed), the result diverges (DESKTOP-shown: max|core-fira|
     *   = 314204 with reversed taps, int_history_proof.py).  CORRECTION (critic round-3, verified):
     *   the FROZEN g_hb63_fira32 IS bit-exactly symmetric (palindrome, all 31 nonzero pairs equal;
     *   verified by independent parse of fir_coeffs_q31.h) -> for THESE coeffs reversed taps give an
     *   IDENTICAL result, so A-orient is MOOT for the current frozen set (board-locking it is harmlessly
     *   conservative).  RE-VERIFY only if g_hb63_fira32 is ever changed to a non-symmetric set; if a
     *   future set is asymmetric AND FIRA reverses, pre-reverse once at fira_tree_set_coeffs, NOT per-call. [L1/EZKIT] */
    /* D1b / nWindowSize ASSUME (fix 2026-06-03):
     *   [ASSUME] nWindowSize = OUTPUT count for DECIMATION (i.e. the HW produces `window` decimated
     *   outputs).  The field name is ambiguous -- it could mean INPUT window.  Evidence for OUTPUT
     *   interpretation: (a) MCP.c:151 sets nInputBuffCount = ntaps+nWindowSize-1 for SINGLE_RATE, which
     *   is the classic FIR overlap-save layout where nWindowSize = number of NEW outputs per block; if
     *   nWindowSize were INPUT the formula would double-count; (b) the ADI hw-ref table lists nWindowSize
     *   alongside nTapLength as filter-descriptor fields (not input-buffer descriptors).
     *   IF nWindowSize is actually INPUT count the board will DMA-read the wrong number of samples; flip
     *   the assignment to `window * FIRA_RATIO` with a one-line change here and re-run R14. [L1/EZKIT] */
    /* Decimation/interpolation mode (per-channel, Legacy supported, F1 S3). Enum see legacy hdr:33-35.
     * [ASSUME] ADI examples all SINGLE_RATE, no dec/int example -> phase/x2 behavior F4 board-verify. */
    /* ===== DEC-PHASE FIX (2026-06-04, root cause CONFIRMED by PM + critic) =====
     * BOTH DEC and INT now run SINGLE_RATE (full-rate FIR); the decimation phase is done in
     * SOFTWARE by fira_postscale (ratio=2, phase=1).  WHY:
     *   The board FIRA hardware DECIMATION mode keeps the EVEN input-stream sample (i&1==0), while
     *   core hb_decimate2 (tree_filterbank.c:113) keeps the ODD one (i&1==1).  Because the DEC
     *   stream is [hist(62=even) ++ frame], the HW even-phase keep lands on FRAME-EVEN indices but
     *   core keeps FRAME-ODD -> off-by-one decimation phase.  This reproduced the board sb3 residual
     *   [0,-2,0,+2,0,-2,0,+6] EXACTLY and then exploded (DESKTOP-PROVEN, decphase_fix_repro.py:
     *   un-fixed HW-even max|core-fira| = 1734588; fixed = 0 over the WHOLE frame).
     *   The HW decimation start-phase is NOT controllable through any confirmed Legacy field, and is
     *   exactly the kind of unverifiable hardware phase we already removed for INT by doing the
     *   zero-stuff in software.  SAME REMEDY HERE: run SINGLE_RATE (full-rate, ntaps+full-1 inputs ->
     *   `window` = full-rate outputs = ratio*out_count), then fira_postscale decimates ratio=2 phase=1.
     *   This makes the decimation phase a SOFTWARE knob (bit-exact-capable, board-independent), and
     *   the (ntaps-1) RAW cross-frame history (critic-confirmed bit-exact) is UNCHANGED.
     * INT keeps its SOFTWARE zero-stuff + SINGLE_RATE convolution (INT history-domain fix 2026-06-03):
     *   doing the zero-stuff in software made the (ntaps-1) cross-frame history bit-exactly the tail
     *   of the 2x stream (DESKTOP-PROVEN max|core-fira|=0, int_history_proof.py); x2 gain in
     *   fira_postscale_int.
     * [ASSUME dec-sw-phase] FIRA HW DECIMATION keeps EVEN phase -> we sidestep it via SINGLE_RATE +
     *   sw phase=1.  Board R14 g_f4_dump confirms: residual all-zero if fixed; or the predicted
     *   even-phase explosion 0,-10,0,+22,... if SINGLE_RATE itself somehow still decimates. [L1/EZKIT] */
    ci.eSampling       = ADI_FIR_SAMPLING_SINGLE_RATE;   /* DEC + INT both full-rate; sw decimate in postscale */
    ci.nSamplingRatio  = 1u;                             /* full-rate; software decimation downstream */
    /* -- coeffs (legacy hdr:51) -- */
    ci.nCoefficientCount  = g_hb_fira_n;
    ci.pCoefficientIndex  = (void *)coeff;
    ci.nCoefficientModify = 1;
    /* -- output (legacy hdr:52) --
     * DP-01 (HW sec.38-10): 80-bit MAC result is written back in bursts of 3x32-bit (LSW/MSW/overflow),
     *   so the output buffer must hold WINDOWSIZE x 3 int32 words and nOutputBuffCount = window*3.
     *   The caller's outbuf MUST be sized window*3 (else FIRA DMA overruns). Core fira_postscale()
     *   then reassembles 80-bit, >>15 (+x2 for INT), no further decimation (ratio=1) -> `window` Q31. */
    ci.pOutputBuffBase  = (void *)outbuf;
    ci.nOutputBuffCount = (uint32_t)window * 3u;   /* WINDOWSIZE x 3 (3x32-bit per sample) */
    ci.nOutputBuffModify = 1;
    ci.pOutputBuffIndex = (void *)outbuf;
    /* -- input (legacy hdr:53): DEC-PHASE FIX uniform SINGLE_RATE (2026-06-04) --
     * BOTH DEC and INT are now SINGLE_RATE, so the input-count formula is uniform:
     *   nInputBuffCount = ntaps + window - 1   (ntaps-1 priming history + `window` full-rate outputs).
     * Here `window` is the FULL-RATE output count the FIRA engine produces (one output per input):
     *   DEC: caller passes window = FIRA_RATIO*out_count (full frame-rate); postscale decimates ->out_count.
     *   INT: caller passes window = out_count (= 2x the raw input, over the sw zero-stuffed stream).
     * This matches the buffer fira_run_segment_stateful builds (FIRA_HIST + window).
     * (Supersedes the D1b ntaps+ratio*window-1 DEC formula, which assumed HW DECIMATION; the HW
     *  decimation phase was the confirmed root-cause bug, so DEC no longer uses HW decimation.) */
    ci.pInputBuffBase  = (void *)inbuf;
    ci.nInputBuffCount = (uint32_t)g_hb_fira_n + window - 1u;   /* SINGLE_RATE: ntaps-1 prime + window outputs */
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
 * Buffers passed by caller: in length in_count = ntaps+out_count-1; **out length out_count*3**
 *   (DP-01: FIRA writes 3x32-bit per sample = LSW/MSW/overflow). Caller must size out as out_count*3.
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

    /* 1 channel: DECIMATION r=2 (bench can switch INTERPOLATION to verify x2).
     * D1b fix (2026-06-03): nInputBuffCount for DECIMATION = ntaps + ratio*out_count - 1.
     * fira_make_channel already applies this formula for FIRA_SEG_DEC.  Override ntaps/ntaps only. */
    ADI_FIR_CHANNEL_INFO ch = fira_make_channel(FIRA_SEG_DEC, out_count,
                                                g_hb_fira, in, out);
    ch.nTapLength = ntaps; ch.nCoefficientCount = ntaps;
    /* nInputBuffCount inherited from fira_make_channel: ntaps + FIRA_RATIO*out_count - 1
     * (D1b fix; old override `ntaps + out_count - 1` removed). Caller must size in[] accordingly. */
    (void)in_count;   /* caller guarantees in_count == ntaps+FIRA_RATIO*out_count-1 (layout self-check bench-side) */

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
    fira_tree_use_real_coeffs();   /* F3: ensure real frozen coeffs active before CreateTask */
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
 * SC. R14 post-processing: FIRA 80-bit writeback -> Q31 (DP-01 5-step, FIRA_IMPL.md S3 R14-3/-5)
 * ------------------------------------------------------------
 * Per HW Reference sec.38-10 (DOC-S4-FIRA-DP-01): a 32-bit fixed-point MAC produces an 80-bit result,
 *   and the result register is always written back in bursts of 3 x 32-bit words:
 *     word0 = LSW (low 32 bits), word1 = MSW (next 32 bits), word2 = 16-bit overflow (high bits).
 *   => the FIRA output buffer holds WINDOWSIZE x 3 int32 words, not WINDOWSIZE.
 *   FIRA does an EXACT integer MAC with NO built-in right shift; the fractional >>15 (our Q15xQ31->Q46)
 *   must be done here, core-side, matching the golden (arithmetic truncate toward -inf, NOT IEEE round).
 *
 * DP-01 5 steps (applied per output sample):
 *   (a) reassemble the 80-bit signed result from the 3x32-bit words (LSW/MSW/overflow);
 *   (b) >>15 arithmetic right shift (Q46 -> Q31, same truncation as golden Sigma h*state >>15);
 *   (c) x2 for signed-fractional compensation (INTERPOLATION segments only; redundant-sign-bit / zero-stuff
 *       gain, applied ONCE -- R14-5: must not compound twice or gain is off by 4x);
 *   (d) decimate the buffer to the desired sample stride (per-segment ratio; HW NOTE: "final routine must
 *       decimate the output buffer to the desired samples");
 *   (e) Q31 saturate (f_sat_*; FIRA has no Q31 saturation).
 *
 * [ASSUME] The exact bit-window of (a), the paired (>>15)/x2 composite of (b)/(c), and the decimate phase
 *   of (d) are F4 bench-locked (DOC-S4-FIRA-DP-01 sec.6); desktop gives the documented semantics, NOT a
 *   board-confirmed shift/phase. These are core-side post-processing knobs (gate-internal R14 iteration),
 *   they do NOT touch the filter structure/algorithm.
 * ============================================================ */

/* (a) Reassemble the signed 80-bit MAC result from the 3x32-bit FIRA writeback words.
 *   Layout (HW sec.38-10): w[0]=LSW, w[1]=MSW, w[2]=16-bit overflow (sign-extended high bits).
 *   We need only the low 48..64 bits for a 63-tap halfband (no realistic 80-bit overflow at our levels),
 *   so we fold MSW into an int64; overflow word is range-checked only.
 *   [ASSUME] exact bit selection F4-locked; if real data exercises >48 effective bits this must widen. */
static int64_t fira_reassemble80(const int32_t w[3])
{
    uint64_t lsw = (uint32_t)w[0];
    uint64_t msw = (uint32_t)w[1];
    int64_t  acc = (int64_t)((msw << 32) | lsw);   /* low 64 bits as signed */
    /* (a-overflow) w[2] is the 16-bit overflow/sign word. Dropping it is LOSSLESS for our data NOT
     *   because w[2]==0 (for negative acc it is 0xFFFF sign-extension, not 0) but because every acc in
     *   this 63-tap halfband Q15xQ31 filter fits in signed 64 bits, so reinterpreting the low 64 bits as
     *   int64 already carries the correct sign+magnitude; w[2] is then pure redundant sign extension and
     *   reconstructs no information (desktop-proven over the +-2^47 range that occurs,
     *   residual_pack80_repro.py pack/unpack self-check). Bench asserts the no->64-bit-overflow on board. */
    (void)w;   /* w[2] consistency = F4 board check (R14); keep low-64 path bit-exact-capable */
    return acc;
}

/* DEC segment post-process: (a)->(b)->(e). Decimation phase done in SOFTWARE by fira_postscale
 * (ratio=2, phase=1 == core (i&1)==1; DEC-PHASE FIX 2026-06-04, was FIRA hardware skip/even-phase). */
static int32_t fira_postscale_dec(const int32_t w[3])
{
    int64_t acc = fira_reassemble80(w);            /* (a) 80-bit reassemble */
    return f_sat_i64_to_i32(acc >> 15);            /* (b) >>15 truncate, (e) saturate */
}

/* INT segment post-process: (a)->(b)->(c)->(e). x2 applied exactly once (R14-5). */
static int32_t fira_postscale_int(const int32_t w[3])
{
    int64_t acc = fira_reassemble80(w);            /* (a) 80-bit reassemble */
    int64_t q31 = (acc >> 15) * 2;                 /* (b) >>15 truncate, (c) x2 signed-fractional */
    return f_sat_i64_to_i32(q31);                  /* (e) saturate */
}

/* (d) Decimate a 3-word-per-sample FIRA output buffer into a packed Q31 sample buffer.
 *   src holds n_src logical samples, each as 3 consecutive int32 (LSW,MSW,overflow).
 *   ratio = decimation factor (DEC: pick every ratio-th sample; INT/SINGLE: ratio=1).
 *   phase = which sub-sample to keep (R14-6 even/odd; F4-locked). kind selects dec vs int postscale.
 *   Returns number of Q31 samples written to dst. */
static uint16_t fira_postscale(const int32_t *src3, uint16_t n_src,
                               int32_t *dst, uint16_t ratio, uint16_t phase,
                               FiraSegKind kind)
{
    uint16_t o = 0u, s;
    if (ratio == 0u) { ratio = 1u; }
    for (s = phase; s < n_src; s += ratio) {
        const int32_t *w = &src3[(uint32_t)s * 3u];   /* 3x32-bit per logical sample */
        dst[o++] = (kind == FIRA_SEG_DEC) ? fira_postscale_dec(w)
                                          : fira_postscale_int(w);
    }
    return o;   /* decimated Q31 sample count */
}

/* ============================================================
 * SC2. fira_run_segment: one halfband segment = adi_fir lifecycle (Path B) + fira_postscale
 * ------------------------------------------------------------
 * Reuse F2/F3 single-channel lifecycle template (SB-template), but on the *already-open* s_hFir
 *   (opened once by fira_tree_setup; do NOT Open/Close per segment -> real-time per-frame cost).
 * Per segment:
 *   (1) build ADI_FIR_CHANNEL_INFO via fira_make_channel(kind, out_count, g_hb_fira, in, s_seg_out3)
 *       (eSampling=DECIMATION/INTERPOLATION chosen inside fira_make_channel by kind; nSamplingRatio=FIRA_RATIO);
 *   (2) adi_fir_CreateTask (TaskMemory #pragma align 32, FIR_MEM_SIZE(1));
 *   (3) adi_fir_FixedPointEnable(hTask, SIGNED_INTEGER) (Path B, after CreateTask / before QueueTask);
 *   (4) g_FIRTaskDoneCount=0; adi_fir_QueueTask; spin until ALL_CHANNEL_DONE (FIRTaskDoneCount<1);
 *   (5) fira_postscale(s_seg_out3, fira_window, out_q31, post_ratio, post_phase, kind) -> Q31 samples.
 *
 * out3 scratch: FIRA writes fira_window x 3 int32 (LSW/MSW/overflow, DP-01). Static [MAXWINDOW*3],
 *   #pragma align 32 (cache-line, MCP.c:82, else breaks bit-exact). MAXWINDOW=512 (largest fira_window =
 *   FIRA_RATIO*f1 = f0 = 512 for the DEC seg0 full-rate run).
 *   DEC-PHASE FIX (2026-06-04): BOTH DEC and INT run SINGLE_RATE -> in_count = ntaps + fira_window - 1.
 *     DEC: fira_window = FIRA_RATIO*out_count (full frame-rate); postscale decimates ratio=2 phase=1.
 *     INT: fira_window = out_count (sw zero-stuffed 2x stream); postscale ratio=1.
 *   Caller (fira_run_segment_stateful) passes prepended temp_in with the correct total count.
 *
 * phase: DEC sw-decimate phase=1 (== core (i&1)==1); INT phase=0 (x2 in fira_postscale_int).
 *   DEC-PHASE FIX 2026-06-04; F4b board bit-by-bit confirms the all-zero residual.
 * Returns 0 on success; non-zero = adi_fir_* failure step code (simplified error flag, draft).
 * [L1/EZKIT]: real adi_fir_* behavior bench-side; cannot run on this host.
 * ============================================================ */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
#define FIRA_MAXWINDOW 512u   /* largest segment output window = frame (f0); INT up to f0 too */

int fira_run_segment(FiraSegKind kind, const int32_t *in, uint16_t in_count,
                     int32_t *out_q31, uint16_t out_count)
{
    /* out3 scratch: WINDOWSIZE x 3 int32 (80-bit/3-word writeback, DP-01). align 32 (MCP.c:82).
     * D-scratch (A5 fix 2026-06-03, approach B): shared static across all 9 segments x 1024 frames.
     * The earlier per-call memset(s_seg_out3,0,fira_window*3) was BELT-AND-SUSPENDERS only: fira_postscale
     * reads only WITHIN the FIRA write span (DEC-PHASE FIX 2026-06-04: FIRA writes fira_window full-rate
     * slots; postscale reads slots s=post_phase..fira_window-1 stride post_ratio, 3 words each = the FIRA
     * write span), so no unwritten slot is ever read -> no stale residue can leak.
     * The memset is now REMOVED so that no core write dirties these cache lines; this makes the
     * post-DMA flush_data_buffer(...,1) below effectively invalidate-only (no dirty line to write
     * back over the FIRA DMA data) -> the flush-back hazard is eliminated at the source, not papered
     * over by ordering.  s_seg_out3 is only ever written by FIRA DMA and only ever read by postscale. */
    #pragma align 32
    static int32_t s_seg_out3[FIRA_MAXWINDOW * 3u];
    #pragma align 32
    static uint8_t s_taskMem[FIR_MEM_SIZE(1)];
    ADI_FIR_TASK_HANDLE hTask = 0;
    ADI_FIR_RESULT r;

    /* DEC-PHASE FIX (2026-06-04): FIRA runs SINGLE_RATE (full-rate) for BOTH kinds; the FIRA window
     * (= number of 3-word slots FIRA writes) is the FULL-RATE output count:
     *   DEC: fira_window = FIRA_RATIO * out_count (full frame-rate); postscale decimates ratio=2 phase=1
     *        -> out_count Q31 samples (== core hb_decimate2 keeping (i&1)==1).
     *   INT: fira_window = out_count (already the 2x zero-stuffed output count); postscale ratio=1.
     * post_ratio/post_phase drive the SOFTWARE decimation in fira_postscale. */
    uint16_t fira_window = (kind == FIRA_SEG_DEC) ? (uint16_t)(FIRA_RATIO * out_count) : out_count;
    uint16_t post_ratio  = (kind == FIRA_SEG_DEC) ? (uint16_t)FIRA_RATIO : 1u;
    uint16_t post_phase  = (kind == FIRA_SEG_DEC) ? 1u : 0u;   /* DEC: keep odd phase == core (i&1)==1 */

    if (s_hFir == 0 || g_hb_fira == 0 || in == 0 || out_q31 == 0) { return -2; }
    if (fira_window > FIRA_MAXWINDOW) { return -3; }   /* scratch overrun guard (full-rate window) */

    /* (A5 approach B) NO memset here: see the s_seg_out3 declaration note above. Clearing would
     * dirty the cache lines and reintroduce the post-DMA flush-back hazard; postscale reads exactly
     * the FIRA write span (out_count*3 words) under ratio=1, so there is nothing to pre-clear. */

    /* (1) channel info on already-open device (fira_tree_setup did Open + RegisterCallback).
     * in_count: caller (fira_tfb_analyze/synthesize) passes the assembled prepended count.  Under the
     * DEC-PHASE FIX (SINGLE_RATE for both kinds) the engine consumes ntaps + fira_window - 1 inputs:
     *   DEC: hist(62) + FIRA_RATIO*out_count raw frame samples = 62 + fira_window (one trailing raw
     *        sample unused; engine reads ntaps+fira_window-1 = 62+fira_window... i.e. 63+fira_window-1).
     *   INT: hist(62) + out_count zero-stuffed samples = 62 + fira_window.
     * Passed via `in` which ALREADY points to the prepended temp buffer (see fira_run_segment_stateful). */
    ADI_FIR_CHANNEL_INFO ch = fira_make_channel(kind, fira_window, g_hb_fira, in, s_seg_out3);
    (void)in_count;   /* in_count double-documented in ch.nInputBuffCount via fira_make_channel; kept for caller contract */

    /* (2) CreateTask */
    r = adi_fir_CreateTask(s_hFir, &ch, 1u, (void *)s_taskMem,
                           (uint32_t)FIR_MEM_SIZE(1), &hTask);
                                                            if (r != ADI_FIR_RESULT_SUCCESS) return 3;
    /* (3) Path B fixed-point SIGNED (after CreateTask / before QueueTask) */
    r = adi_fir_FixedPointEnable(hTask, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER);
                                                            if (r != ADI_FIR_RESULT_SUCCESS) return 4;
    /* (4) queue + wait ALL_CHANNEL_DONE (Legacy, MCP.c:282) */
    g_FIRTaskDoneCount = 0;
    r = adi_fir_QueueTask(hTask);                           if (r != ADI_FIR_RESULT_SUCCESS) return 5;
    while (g_FIRTaskDoneCount < 1u) { /* spin; bench can switch to idle/event wait */ }

    /* IO1d cache coherence (A5 HARD GATE, REAL symbol wired 2026-06-03): s_seg_out3 is written by FIRA
     * DMA (not by the core).  The core L1 data cache may still hold lines for that region, so the core
     * MUST invalidate them AFTER the FIRA task completes (g_FIRTaskDoneCount spin above) and BEFORE
     * fira_postscale() reads s_seg_out3 (next statement).  Range = exactly the bytes FIRA wrote =
     * out_count*3 int32 words (DP-01 3-word/sample writeback) = the exact span postscale reads (ratio=1).
     *
     * REAL SYMBOL (A5, repo-evidenced): the prior draft used adi_cache_invalidate(), an SC5xx-ARM
     * service name that does NOT exist in the SHARC BSP -> li1021 unresolved + cc0223 implicit decl.
     * The documented CCES SHARC builtin (header <sys/cache.h>, linked as flush_data_buffer_ba in 21569
     * SHARC linker logs: knowledge_base/ezkit/vendor_docs/cces_examples/.../21569/sharc/.../linker_log.xml)
     * is:  void flush_data_buffer(void *start, void *end, int enInv);
     * It writes back dirty lines covering [start,end) and, when enInv!=0, also invalidates them.
     *
     * HAZARD-FREE because of approach B (no memset): flush_data_buffer is flush-AND-(optionally-)invalidate;
     * there is no pure-invalidate builtin.  Since we removed the memset, the core NEVER dirties s_seg_out3
     * (only FIRA DMA writes it, only postscale reads it).  So at this point any core-cached lines are
     * CLEAN (read-fills from a prior frame at most) -> the flush part writes back nothing, and enInv=1
     * invalidates them so the following postscale read misses and fetches the fresh FIRA DMA data.
     * There is thus no path where stale core data overwrites the FIRA output. s_seg_out3 is #pragma
     * align 32 (whole cache lines) so the op never touches an unrelated dirty line.
     *
     * Between this call and the postscale read only the g_FIRTaskDoneCount spin (already completed) and
     * local control flow run -- nothing writes s_seg_out3 -- so no line is re-dirtied before the read.
     *
     * NOTE on driver auto-invalidate (FIRA_IMPL.md L35/L155, DOC-S4-FIRA-IMPL-01): when the FIR config
     * header has ADI_CACHE_MANAGEMENT=1 AND the output buffer is ADI_CACHE_ALIGN'd, the Legacy driver
     * may already invalidate the output region at QueueTask completion.  This explicit call is then
     * idempotent (invalidating an already-clean region is harmless), kept as defense for the
     * cache-management-off / region-not-driver-tracked case.
     *
     * END-POINTER CONVENTION (ADI-documented, now prototype-checked by <sys/cache.h>): `end` points
     * one past the last byte of the region (half-open [start,end)), matching the ADI cache primitive
     * convention.  end = s_seg_out3 + out_count*3 (int32* arithmetic = one past last written word).
     *
     * [ASSUME A5: still board-link-locked -- MUST compile+link on the board (CCES 2.12.1, -proc
     *   ADSP-21569) before flashing. flush_data_buffer is now a real SHARC-BSP symbol so it SHOULD
     *   resolve; the included header prototype-checks the arg type/count (wrong call now compile-caught,
     *   not silent). Board R14 g_f4 dump still shows zeros/stale if any A5 assumption is wrong.
     *   NOT verifiable on this host. [L1/EZKIT] */
    flush_data_buffer((void *)s_seg_out3,
                      (void *)(s_seg_out3 + (uint32_t)fira_window * 3u),
                      1 /*enInv: also invalidate after (no dirty lines under approach B)*/);

    /* (5) postscale: 80-bit 3-word -> Q31 + SOFTWARE decimation (DEC-PHASE FIX 2026-06-04).
     * FIRA now runs SINGLE_RATE and wrote `fira_window` full-rate 3-word slots.  Postscale:
     *   DEC: ratio=2, phase=1 -> keeps slots 1,3,5,... == core hb_decimate2 (i&1)==1 -> out_count samples.
     *        (DESKTOP-PROVEN max|core-fira|=0 over the whole frame, decphase_fix_repro.py; the OLD
     *         HW-decimation even-phase path reproduced the board residual [0,-2,0,+2,0,-2,0,+6] then
     *         exploded to ~1.7e6.)
     *   INT: ratio=1, phase=0 -> reads all out_count slots (x2 gain applied inside fira_postscale_int).
     * fira_postscale returns the decimated Q31 sample count (== out_count for DEC, out_count for INT).
     * [ASSUME dec-sw-phase] FIRA SINGLE_RATE writes exactly `fira_window` full-rate 3-word slots in DMA
     *   order (one per input-after-priming).  Board R14 g_f4_dump confirms (all-zero if fixed; predicted
     *   even-phase explosion 0,-10,0,+22,... if SINGLE_RATE itself still decimates). [L1/EZKIT] */
    (void)fira_postscale(s_seg_out3, fira_window, out_q31, post_ratio, post_phase, kind);
    return 0;
}
/* ============================================================
 * SC3. fira_run_segment_stateful: D3/ST1 cross-frame history wrapper
 *      (fix 2026-06-03; INT history-domain re-fix per Critic round-2)
 * ------------------------------------------------------------
 * tree_filterbank.c is a STATEFUL streaming filter: hb_decimate2 / hb_interp2 maintain a
 * persistent (ntaps-1)-sample ring buffer (HbFirState.state[63]) across ALL 1024 frames.
 * FIRA runs as a one-shot block call with no persistence.  To match core bit-exact, each
 * FIRA segment must prepend the previous frame's (ntaps-1)-sample delay-line tail.
 *
 * CRITICAL DOMAIN DISTINCTION (Critic round-2, DESKTOP-PROVEN by int_history_proof.py):
 *   The two core primitives advance their ring DIFFERENTLY:
 *     - hb_decimate2 (DEC): pushes RAW inputs only (push(in[i])).  Its persistent ring tail =
 *       the last (ntaps-1) RAW inputs.  -> DEC history is RAW-domain.
 *     - hb_interp2 (INT):  per raw input pushes TWO samples (push(x); push(0)).  Its persistent
 *       ring tail = the last (ntaps-1) samples of the ZERO-STUFFED 2x stream (31 real + 31
 *       interleaved zeros, most-recent slot = the trailing 0).  -> INT history is ZERO-STUFFED-domain.
 *   Carrying RAW history for INT (the round-1 bug) primes the FIRA delay line with 62 consecutive
 *   real samples instead of 31 real + 31 zeros -> WRONG (proof: max|core-fira| = 396830, frame>=1).
 *   Carrying ZERO-STUFFED history for INT -> max|core-fira| = 0 (proof).
 *
 * IMPLEMENTATION:
 *   DEC: build temp_in = [hist_raw(62) ++ frame_raw(2*out_count)], run FIRA as a SINGLE_RATE FIR over
 *        that stream (DEC-PHASE FIX 2026-06-04: was FIRA DECIMATION mode, whose EVEN keep-phase mismatched
 *        the core ODD phase -- the confirmed root-cause bug; now full-rate + SOFTWARE decimate ratio=2
 *        phase=1 in fira_postscale == core (i&1)==1, DESKTOP-PROVEN max|core-fira|=0 decphase_fix_repro.py).
 *        The RAW cross-frame history is UNCHANGED (Critic + int_history_proof.py confirmed bit-exact).
 *   INT: build temp_zs = [hist_zs(62) ++ zero_stuff(frame_raw)] in the 2x domain, run FIRA as a
 *        SINGLE_RATE FIR over that explicit 2x stream (eSampling set in fira_make_channel; x2 gain in
 *        fira_postscale_int), keep out_count = 2*in_count outputs, then update hist_zs from the last 62
 *        samples of the zero-stuffed frame.  Software zero-stuff removes any dependence on the FIRA
 *        INTERPOLATION mode's internal zero-stuff phase (unverifiable on desktop) and makes the
 *        cross-frame history bit-exactly the tail of the convolution stream.
 *
 * [ASSUME prepend-len] prepend = FIRA_HIST = ntaps-1 = 62 (frozen ntaps=63).  If ntaps changes,
 *   update FIRA_HIST and recompile.  Board R14 verifies frame-boundary subbands (frame>=1). [L1/EZKIT]
 * [ASSUME A-orient]  bit-exactness also requires FIRA tap orientation == core (see fira_make_channel
 *   [ASSUME A-orient]).  Board-locked. [L1/EZKIT]
 *
 * Stack: temp buffer max = FIRA_HIST + 2*FIRA_MAXWINDOW int32.  See stack DECISION below.
 *
 * Parameters:
 *   seg_idx   segment index [0..8] -> ch->hist[seg_idx].
 *   kind      FIRA_SEG_DEC (raw-domain) or FIRA_SEG_INT (zero-stuffed-domain).
 *   frame_in  CURRENT frame's input slice (RAW samples, no history prefix, NOT pre-stuffed).
 *   n_frame   count of RAW current-frame samples:
 *               DEC: n_frame = ratio * out_count (= 2*out_count, the raw stream the decimator eats).
 *               INT: n_frame = in_count = out_count/ratio (the RAW samples; this fn zero-stuffs them).
 *   out_q31   output Q31 samples (out_count words written).
 *   out_count output sample count (INT: = 2 * n_frame).
 *   ch        FiraChannelState* carrying per-segment history (DEC: raw; INT: zero-stuffed).
 * Returns 0 on success, non-zero = fira_run_segment failure code.
 * ============================================================ */

/* Stack DECISION (Critic round-2, item 4): the assembled FIRA input buffer is sized for the
 * largest frame (FIRA_MAXWINDOW=512 -> INT stream up to 62 + 2*512 = 1086 int32 = ~4.3 KB).  4.3 KB
 * on a SHARC+ stack is risky alongside the analyze/synthesize frame buffers (a1/a2/r1.. ~ several KB),
 * and this fn is on the per-frame real-time path.  DECISION: make the assembly buffer STATIC (file
 * scope, single-threaded FIRA path -> no reentrancy), explicitly distinct from s_seg_out3 (no alias).
 * [ASSUME] FIRA orchestration is single-threaded / non-reentrant per frame (one segment at a time on
 *   the already-open s_hFir).  If F5 8ch concurrency runs segments in parallel, this must become
 *   per-task scratch. [L1/EZKIT] */
#pragma align 32
static int32_t s_seg_in[FIRA_HIST + 2u * FIRA_MAXWINDOW];   /* assembly scratch; NOT aliased to s_seg_out3 */

static int fira_run_segment_stateful(uint8_t seg_idx, FiraSegKind kind,
                                     const int32_t *frame_in, uint16_t n_frame,
                                     int32_t *out_q31, uint16_t out_count,
                                     FiraChannelState *ch)
{
    uint16_t total_in;
    int rc;

    if (kind == FIRA_SEG_DEC) {
        /* ---- DEC: RAW-domain history (UNCHANGED, bit-exact-confirmed) ---- */
        total_in = (uint16_t)(FIRA_HIST + n_frame);                 /* 62 + 2*out_count raw */
        memcpy(s_seg_in, ch->hist[seg_idx], FIRA_HIST * sizeof(int32_t));      /* prepend raw history */
        memcpy(s_seg_in + FIRA_HIST, frame_in, n_frame * sizeof(int32_t));     /* append raw frame */

        rc = fira_run_segment(kind, s_seg_in, total_in, out_q31, out_count);

        /* update raw history: last FIRA_HIST raw frame samples */
        if (n_frame >= FIRA_HIST) {
            memcpy(ch->hist[seg_idx], frame_in + n_frame - FIRA_HIST, FIRA_HIST * sizeof(int32_t));
        } else {
            uint16_t keep = (uint16_t)(FIRA_HIST - n_frame);
            memmove(ch->hist[seg_idx], ch->hist[seg_idx] + n_frame, keep * sizeof(int32_t));
            memcpy(ch->hist[seg_idx] + keep, frame_in, n_frame * sizeof(int32_t));
        }
    } else {
        /* ---- INT: ZERO-STUFFED-domain history (Critic round-2 fix) ---- */
        uint16_t i, zlen = (uint16_t)(FIRA_RATIO * n_frame);        /* zero-stuffed frame length = 2*in_count = out_count */
        total_in = (uint16_t)(FIRA_HIST + zlen);                    /* 62 + out_count */

        /* prepend zero-stuffed-domain history */
        memcpy(s_seg_in, ch->hist[seg_idx], FIRA_HIST * sizeof(int32_t));
        /* append zero_stuff(frame_in): for each raw x -> {x, 0} (matches hb_interp2 push(x);push(0)) */
        for (i = 0u; i < n_frame; i++) {
            s_seg_in[FIRA_HIST + (uint32_t)i * 2u]      = frame_in[i];
            s_seg_in[FIRA_HIST + (uint32_t)i * 2u + 1u] = 0;
        }

        /* SINGLE_RATE FIR over the explicit 2x stream (eSampling/ratio set in fira_make_channel for INT). */
        rc = fira_run_segment(kind, s_seg_in, total_in, out_q31, out_count);

        /* update zero-stuffed history: last FIRA_HIST samples of [history ++ zero_stuffed_frame].
         * total assembled (excluding old prefix) zero-stuffed length = zlen; if zlen >= FIRA_HIST take
         * its tail, else slide the old zs history.  Mirrors how the core ring holds the last 62 of the
         * zero-stuffed stream after this frame. */
        if (zlen >= FIRA_HIST) {
            memcpy(ch->hist[seg_idx], &s_seg_in[FIRA_HIST + zlen - FIRA_HIST], FIRA_HIST * sizeof(int32_t));
        } else {
            uint16_t keep = (uint16_t)(FIRA_HIST - zlen);
            memmove(ch->hist[seg_idx], ch->hist[seg_idx] + zlen, keep * sizeof(int32_t));
            memcpy(ch->hist[seg_idx] + keep, &s_seg_in[FIRA_HIST], zlen * sizeof(int32_t));
        }
    }
    return rc;
}
#endif /* FIRA_USE_REAL_ADI_FIR_HEADER */

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
    uint16_t ntaps = g_hb_fira_n;
    (void)ntaps;   /* ntaps consumed indirectly via g_hb_fira_n inside fira_make_channel; not used directly here */
    /* ch is used by fira_run_segment_stateful in the FIRA path; (void)ch removed from the #else path below */

#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    /* -- FIRA DEC segments (DEC-PHASE FIX 2026-06-04: SINGLE_RATE full-rate FIR + SOFTWARE decimate
     *      ratio=2 phase=1 in fira_postscale == core (i&1)==1; was HW DECIMATION even-phase = the bug) --
     *   D3/ST1 fix (2026-06-03): use fira_run_segment_stateful, which prepends history and updates it.
     *   n_frame for DEC = ratio * out_count (the raw sample count consumed by the decimator this frame).
     *   Segment index mapping (fira_channel_init): seg 0=ana_dec[0], 1=ana_dec[1], 2=ana_dec[2].
     *   a1=dec(in)@f1; a2=dec(a1)@f2; a3=dec(a2)@f3.
     *   [ASSUME] n_frame = FIRA_RATIO * out_count is the input slice size for each DEC step.
     *     frame 0..2 are DEC; the in[] and a1[]/a2[] buffers already hold exactly that many samples
     *     for this frame.  Verify at frame boundary (frame 0->1) on board. [L1/EZKIT] */
    (void)fira_run_segment_stateful(0u, FIRA_SEG_DEC, in, (uint16_t)(FIRA_RATIO * f1), a1, f1, ch);
    (void)fira_run_segment_stateful(1u, FIRA_SEG_DEC, a1, (uint16_t)(FIRA_RATIO * f2), a2, f2, ch);
    (void)fira_run_segment_stateful(2u, FIRA_SEG_DEC, a2, (uint16_t)(FIRA_RATIO * f3), a3, f3, ch);

    /* -- FIRA INTERPOLATION segments (SOFTWARE zero-stuff + SINGLE_RATE FIR; x2 gain in fira_postscale_int) --
     *   Critic round-2 fix (2026-06-03): fira_run_segment_stateful zero-stuffs frame_in in SOFTWARE and
     *     carries ZERO-STUFFED-domain cross-frame history (DESKTOP-PROVEN bit-exact, int_history_proof.py).
     *   n_frame for INT = RAW input count to the interpolator (the helper builds the 2x stream).
     *     hb_interp2: n_in raw -> 2*n_in out.  So n_frame = f3/f2/f1; out_count = f2/f1/f0 (= 2*n_frame).
     *   Segment index mapping: seg 3=ana_int[2], 4=ana_int[1], 5=ana_int[0].
     *   r3=int(a3)@f2; r2=int(a2)@f1; r1=int(a1)@f0. */
    (void)fira_run_segment_stateful(3u, FIRA_SEG_INT, a3, f3, r3, f2, ch);
    (void)fira_run_segment_stateful(4u, FIRA_SEG_INT, a2, f2, r2, f1, ch);
    (void)fira_run_segment_stateful(5u, FIRA_SEG_INT, a1, f1, r1, f0, ch);
#else
    /* No real header on this host: FIRA convolution segments unavailable -> placeholder 0.
     *   This intentionally produces WRONG a1/a2/a3 + r1/r2/r3 so the subband CRC check FAILS
     *   correctly (no faking bit-exact). Bench connects real segments once FIRA_USE_REAL_ADI_FIR_HEADER is defined.
     *   (void)fira_postscale* keeps the desktop-only postscale primitives referenced. */
    (void)ch;   /* ch only used in FIRA path above; suppress warning in placeholder path */
    (void)fira_postscale_dec; (void)fira_postscale_int; (void)fira_postscale;
    memset(a1, 0, sizeof(a1)); memset(a2, 0, sizeof(a2)); memset(a3, 0, sizeof(a3));
    memset(r1, 0, sizeof(r1)); memset(r2, 0, sizeof(r2)); memset(r3, 0, sizeof(r3));
#endif

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
    uint16_t f0 = frame, f1 = frame/2u, f2 = frame/4u, f3 = frame/8u;
    uint16_t i;
    int32_t a2p[256], a1p[512];
    int32_t up3[128], up2[256], up1[512];
    uint16_t ntaps = g_hb_fira_n;
    (void)ntaps;   /* ntaps consumed indirectly via g_hb_fira_n inside fira_make_channel */
    /* ch used by fira_run_segment_stateful in the FIRA path below */
#ifndef FIRA_USE_REAL_ADI_FIR_HEADER
    (void)ch; (void)f3; (void)sb0;   /* desktop placeholder: ch/sb0/f3 only consumed by the real FIRA interp path */
#endif

    /* -- FIRA INTERPOLATION segments + core-side synthesis add (sat_add, FIRA has no vector add) --
     *   Telescoping reconstruct: up3=int(sb0)@f2; a2p=up3+sb1; up2=int(a2p)@f1; a1p=up2+sb2;
     *   up1=int(a1p)@f0; out=up1+sb3. FIRA does the interp MAC; core does the saturating add.
     *   Critic round-2 fix (2026-06-03): fira_run_segment_stateful zero-stuffs in SOFTWARE and carries
     *   ZERO-STUFFED-domain history (seg 6=syn_int[2], 7=syn_int[1], 8=syn_int[0]).
     *   n_frame for INT = RAW input count (sb0 has f3 samples -> up3 at f2 = 2*f3; etc.). */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    (void)fira_run_segment_stateful(6u, FIRA_SEG_INT, sb0, f3, up3, f2, ch);
#else
    memset(up3, 0, sizeof(up3));   /* desktop placeholder: wrong on purpose -> subband CRC fails correctly */
#endif
    for (i = 0u; i < f2; i++) a2p[i] = f_sat_add_i32(up3[i], sb1[i]);   /* bit-identical tree_filterbank.c:197 */

#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    (void)fira_run_segment_stateful(7u, FIRA_SEG_INT, a2p, f2, up2, f1, ch);
#else
    memset(up2, 0, sizeof(up2));
#endif
    for (i = 0u; i < f1; i++) a1p[i] = f_sat_add_i32(up2[i], sb2[i]);   /* :201 */

#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    (void)fira_run_segment_stateful(8u, FIRA_SEG_INT, a1p, f1, up1, f0, ch);
#else
    memset(up1, 0, sizeof(up1));
    /* Desktop placeholder: a2p/a1p are computed above but their results feed the FIRA interp path
     * (segments 7/8), which is absent here.  Suppress unused-but-set warning. */
    (void)a2p; (void)a1p;
#endif
    for (i = 0u; i < f0; i++) out[i] = f_sat_add_i32(up1[i], sb3[i]);   /* :205 */
}
