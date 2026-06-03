/**
 * @file    fira_tree.h
 * @brief   [DRAFT, uncompiled, real Legacy API, F2-F7 bench-side]
 *          FIRA hardware-accelerated 4-subband dyadic tree halfband FIR (Split-Task orchestration interface)
 *
 * +-----------------------------------------------------------------------+
 * | HONESTY STATUS ANNOTATION (hard constraint, do not delete)            |
 * |  This file is **draft code**: no SHARC toolchain on this host (CCES   |
 * |  only ARM cortex-a5) + no FIRA hardware -> **cannot compile / board-  |
 * |  verify on this host**.                                               |
 * |  - adi_fir_* API = **real Legacy signatures** (archived header        |
 * |    knowledge_base/ezkit/bsp/fira_headers/adi_fir_legacy_2156x.h,      |
 * |    10 functions + ADI_FIR_CHANNEL_INFO + enums, F1/G1 closed DOC-S4-  |
 * |    FIRA-F1-01)                                                        |
 * |  - lifecycle order mirrors official Legacy example                    |
 * |    .../FIR_Multi_Channel_Processing/src/FIR_Multi_Channel_Processing.c |
 * |    (hereafter MCP.c):243-285.                                         |
 * |  - each unverified assumption explicitly marked [ASSUME] / [L1/EZKIT].|
 * |  - NEVER claims "compiled / bit-exact passed / measured cycle".       |
 * |  - real compile + board R14 bit-exact(crc==0x90556BC7) + measured     |
 * |    cycle = bench backfill.                                            |
 * +-----------------------------------------------------------------------+
 *
 * Mode: **LEGACY** (F1 locked, DOC-S4-FIRA-F1-01 S2).
 * Fixed-point: **Path B runtime** -- after CreateTask, before QueueTask call
 *   adi_fir_FixedPointEnable(hTask, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER);
 *   **do not change config header** (adi_fir_config_2156x.h keeps ADI_FIR_FIXED_POINT_MODE=0,
 *   FixedPointEnable .c writes FIRCTL1 TC+FXD bits directly, self-sufficient; report to CTO per red-line before changing config header).
 * Decimation: ADI_FIR_CHANNEL_INFO.eSampling=ADI_FIR_SAMPLING_DECIMATION + nSamplingRatio (per-channel).
 * Completion: Legacy callback ADI_FIR_EVENT_ALL_CHANNEL_DONE; main waits FIRTaskDoneCount<N_TASKS (MCP.c:282).
 *
 * Implementation notes: DOC-S4-FIRA-IMPL-01 (FIRA_IMPL.md, this directory).
 *
 * Split-Task model (FIRA_IMPL.md S2 / EE408 Split_Task example):
 *   - FIRA (hardware): each-level halfband convolution segment (DECIMATION r=2 / INTERPOLATION r=2) = adi_fir channel.
 *   - core-side (software, reuse tree_filterbank.c primitives): detail residual sub / synthesis add /
 *     Q31 saturation clamp / x2 interpolation gain / 8ch broadside sum.
 *   => not "dump the whole chain to FIRA", core still owns all non-MAC fixed-point semantics.
 *
 * R14 critical point (FIRA_IMPL.md S3, HIGH): ours = signed-fractional Q15xQ31; FIRA fixed-point
 *   input format enum only has UNSIGNED/SIGNED_INTEGER (legacy hdr:42-43). Q format conversion points see
 *   FIRA_IMPL.md S3, **each marked "high bit-deviation risk, must board bit-by-bit"**; cannot confirm on desktop.
 *
 * Red-line (iron rule 8 / C9): before board R14 crc==0x90556BC7 passes, FIRA benefit/margin must not be written into
 *   any selection basis (violation = BLOCKER). This file contains no performance numbers.
 */
#ifndef ITC_FIRA_TREE_H
#define ITC_FIRA_TREE_H

#include <stdint.h>
#include "tree_filterbank.h"   /* reuse HbFirState/TreeChannelState dimensions + subband layout convention */

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================
 * Segment enum: per-channel halfband segments (FIRA_IMPL.md S2, C actual convention).
 *   Analysis side: ana_dec[0..2] (DECIMATION r=2) + ana_int[0..2] (INTERPOLATION r=2, for detail)
 *   Synthesis side: syn_int[0..2] (INTERPOLATION r=2)
 * ============================================================ */
#define FIRA_HB_TAPS            TFB_HB_TAPS   /* 63, shared halfband prototype */
#define FIRA_SEGS_PER_CHAN      9             /* 3 dec + 3 ana_int + 3 syn_int */
#define FIRA_RATIO              2             /* decimation/interpolation ratio, integer */

/* Segment category (determines eSampling field: DECIMATION vs INTERPOLATION) */
typedef enum {
    FIRA_SEG_DEC = 0,   /* hb_decimate2 equivalent: DECIMATION, even phase (R14-6 critical point) */
    FIRA_SEG_INT = 1    /* hb_interp2  equivalent: INTERPOLATION, x2 gain compensated in core (R14-5 critical point) */
} FiraSegKind;

/* ============================================================
 * Real Legacy header hookup (F1 closed)
 * ------------------------------------------------------------
 * [L1/EZKIT]: no 21569 SHARC-side driver header on this host (CCES only ARM v2). Bench, in CCES SHARC
 *   project, #includes real BSP header (i.e. the installed header <drivers/fir/adi_fir.h> corresponding to
 *   archived adi_fir_legacy_2156x.h) and defines FIRA_USE_REAL_ADI_FIR_HEADER.
 *   Archived header already gives real signatures (10 functions + ADI_FIR_CHANNEL_INFO + enums), draft orchestrates from it;
 *   base types like ADI_CALLBACK / ADI_CACHE_LINE_LENGTH provided by BSP platform header (bench-supplied).
 * ============================================================ */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
#include <drivers/fir/adi_fir.h>   /* [L1/EZKIT] real Legacy header (= archived adi_fir_legacy_2156x.h) */
#endif

/* ============================================================
 * FIRA tree channel state (draft): per-channel segment metadata (window/category).
 *   Actual buffers (coeffs/input delay-line/output) + TaskMemory statically allocated by caller (F2 template demo).
 *
 * D3 / ST1 cross-frame history (fix 2026-06-03):
 *   tree_filterbank.c is STATEFUL: hb_decimate2 / hb_interp2 maintain a persistent (ntaps-1) = 62 sample
 *   ring buffer (HbFirState.state[TFB_HB_TAPS]) across ALL 1024 frames.  FIRA operates as a one-shot
 *   block call per frame, with no built-in delay-line persistence between frames.  To produce bit-exact
 *   output the FIRA path must PREPEND the previous frame's tail ((ntaps-1) = 62 samples) to each frame's
 *   input before calling adi_fir_QueueTask.
 *
 *   hist[seg][0 .. FIRA_HIST-1] = the last (ntaps-1) input samples of the PREVIOUS frame for each of the
 *   9 segments.  fira_channel_init() zero-initialises them (correct: filter delay-line starts at 0).
 *   fira_run_segment_stateful() prepends hist to the real input and updates hist after each call.
 *
 *   FIRA_HIST = FIRA_HB_TAPS - 1 = 62.  Hard-coded so the compiler can size the arrays statically.
 *   [ASSUME] ntaps is always 63 (frozen g_hb63_fira32, FIR_HB63_FIRA_NTAPS=63).  If ntaps changes,
 *   FIRA_HIST must be updated AND all callers must be recompiled.  Board must verify the prepend layout
 *   produces bit-exact subbands vs core on the first frame boundary (frame 0 -> frame 1 transition).
 * ============================================================ */
#define FIRA_HIST  62   /* ntaps-1; MUST equal FIR_HB63_FIRA_NTAPS-1 = 62 [ASSUME] */

typedef struct {
    FiraSegKind kind[FIRA_SEGS_PER_CHAN];
    uint16_t    window[FIRA_SEGS_PER_CHAN];   /* output sample count (= frame/2^level) */
    /* D3/ST1 per-segment cross-frame history (ntaps-1 samples each, zero-init by fira_channel_init). */
    int32_t     hist[FIRA_SEGS_PER_CHAN][FIRA_HIST]; /* [seg][0..FIRA_HIST-1] = prev-frame tail */
    uint8_t     initialized;
} FiraChannelState;

/* ============================================================
 * Coefficient injection (F3): sign-extend and freeze the shared 63-tap Q15 halfband prototype into FIRA 32-bit container.
 *   R14-2: Q15->32-bit sign-extend + fractional-point semantics preserved, bench bit-by-bit verify.
 *   coef32 = frozen const array generated by fir_coeffs_q31.h (not recomputed on board, same-source discipline).
 * ============================================================ */
void fira_tree_set_coeffs(const int32_t *hb_coef_fira32, uint16_t ntaps);

/** @brief F3: bind active coeffs to the frozen real prototype g_hb63_fira32 (fir_coeffs_q31.h).
 *   Use to restore real coeffs after an F2 arbitrary-coeff smoke override. */
void fira_tree_use_real_coeffs(void);

/** @brief Initialize one FIRA tree channel (clear state + fill segment metadata). */
void fira_channel_init(FiraChannelState *ch, uint16_t frame);

/* ============================================================
 * F2-F4 single-channel bench starter template: 1 ADI_FIR_CHANNEL_INFO (real Legacy fields) runs full
 *   Open -> RegisterCallback -> CreateTask -> FixedPointEnable(SIGNED) -> QueueTask ->
 *   wait ALL_CHANNEL_DONE -> Close sequence. Bench runs this one first (verify lifecycle + fixed-point + phase).
 *   Returns 0 success; non-zero = adi_fir_* failure step code (bench checks ADI_FIR_RESULT).
 *   [L1/EZKIT]: real adi_fir_* behavior bench-side; draft default build does not connect FIRA (returns -1).
 * ============================================================ */
int fira_single_channel_template(const int32_t *in, uint16_t in_count,
                                 int32_t *out, uint16_t out_count, uint16_t ntaps);

/* ============================================================
 * F4: run ONE halfband segment on the already-open FIRA device (s_hFir, opened by fira_tree_setup):
 *   adi_fir_CreateTask -> FixedPointEnable(SIGNED, Path B) -> QueueTask -> wait ALL_CHANNEL_DONE
 *   -> fira_postscale (80-bit/3-word -> Q31, decimate). Does NOT Open/Close per segment.
 *   kind selects DECIMATION/INTERPOLATION; out_q31 receives out_count Q31 samples.
 *   in_count = ntaps + out_count - 1 (FIRA delay-line layout); phase per DP-01 [ASSUME], F4b board-locked.
 *   Returns 0 on success, non-zero = adi_fir_* failure step. Only defined when real header enabled.
 *   [L1/EZKIT]: bench-side; cannot run on this host (no FIRA).
 * ============================================================ */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
int fira_run_segment(FiraSegKind kind, const int32_t *in, uint16_t in_count,
                     int32_t *out_q31, uint16_t out_count);
#endif

/* ============================================================
 * F2/F4: one-time task setup (Open -> RegisterCallback -> CreateTask -> FixedPointEnable).
 *   Real-time mode: CreateTask + FixedPointEnable called once at init, not in frame budget.
 *   [L1/EZKIT]: real adi_fir_* behavior bench-side.
 * ============================================================ */
int fira_tree_setup(void);

/* ============================================================
 * Frame-level Split-Task orchestration (draft): interface deliberately **same signature** as tfb_analyze/tfb_synthesize,
 *   so bench_harness / fira_regression can directly substitute the convolution segment for CRC comparison (crc==0x90556BC7).
 * ============================================================ */
void fira_tfb_analyze(FiraChannelState *ch, const int32_t *in, uint16_t frame,
                      int32_t *sb0, int32_t *sb1, int32_t *sb2, int32_t *sb3);

void fira_tfb_synthesize(FiraChannelState *ch,
                         const int32_t *sb0, const int32_t *sb1,
                         const int32_t *sb2, const int32_t *sb3,
                         uint16_t frame, int32_t *out);

/** @brief Release FIRA device on exit (adi_fir_Close). Real-time app calls once on exit. */
void fira_tree_teardown(void);

#ifdef __cplusplus
}
#endif
#endif /* ITC_FIRA_TREE_H */
