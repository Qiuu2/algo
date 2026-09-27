/*
 * s7_firbench.c -- S7 per-channel FIR compute bench (DEC-S7-SIDE30-01 (3); S7_SIDE30_PERCH_FIR_DESIGN.md sec 5/7-6).
 *
 * ASCII-only (CCES SHARC chokes on UTF-8). NEW self-contained bench TU. It edits NO existing file and does NOT
 *   call fira_tree.c (frozen, CALL-ONLY for M2): it drives the Legacy adi_fir_* API directly, in the SAME
 *   fixed-point mode as fira_tree.c (SINGLE_RATE, adi_fir_FixedPointEnable(SIGNED_INTEGER) after CreateTask /
 *   before QueueTask, int32 coefficient words, exact MAC, 3x32-bit writeback per output (DP-01), core postscale
 *   (80-bit low-64 reassembly, >>15, Q31 saturate), flush_data_buffer(..,1) invalidate before the core reads).
 *   Read-only includes: bench_harness.h, dolph_w8_q15.h (negative control only), chirp_input.h (host build only).
 *
 * WHAT IT MEASURES: wall-clock CCLK cycles per 64-sample frame (48 kHz, 750 fps) for 8 channels of FIR, mono
 *   input (every channel filters the SAME input -- the per-channel filters replace today's Dolph weight + identity
 *   tree), at 63/127/255 taps (tiers 64/128/256), for 5 paths (s7_firbench.h). Bracket per frame = input staging +
 *   all 8 channels + (FIRA) cache invalidate + postscale to Q31 + history update. CRC / stats / IO1 check run
 *   OUTSIDE the bracket. Stats last/max/min over frames 4..1023 (first 4 = warm-up, still in the CRC stream).
 *
 * CORRECTNESS GATES (critic sec 12; a path's cycles count only if all hold -> g_fb_usable[p][t]):
 *   FG1  per-CHANNEL output CRC over the whole 1024-frame stream vs FB_GOLDEN_CRC[t][c] (fb_goldens.h). No
 *        channel sum is ever compared (sum_c 2h_c = delta is an algebraic identity -> telescoping-blind).
 *   FG2  host: placeholder coefficient sets (Dolph-20 x delta, uniform x delta) MISS every golden (generator +
 *        host/fb_ref_host.c); host emulator in stub mode (no FIRA write) FAILS every FIRA path.
 *        board: negative control = Dolph-20 x delta[k-63] through CORE_C in the same run -> g_fb_neg_fail_all==1.
 *   IO1  input = [ntaps-1 history | 64 new] fully initialised (buffers zeroed per run, then staged), count exactly
 *        ntaps+63 (linear) or L >= ntaps+64 (circular); output exactly 64x3 words per channel (frame-0 sentinel
 *        0x5A5A5A5A must be fully overwritten and the 8 guard words behind each channel must survive); each channel
 *        has its OWN output region (no shared scratch); regions re-sentinelled + flushed between runs;
 *        flush_data_buffer(..,1) (invalidate) after DONE and before the postscale read (no core write in between).
 *   ST1  streaming state: ntaps-1 samples of input history carried across frames (shared by the 8 channels
 *        because the input is mono; the per-channel state is the channel's coefficient set). Linear paths
 *        memmove the tail; P1 relies on the hardware index write-back of the circular buffer [ASSUME P1-IDX].
 *   IO2  every run starts from re-zeroed buffers; any read of stale/uninitialised data changes the CRC.
 *   Never uses sum_c 2h_c = delta as a coefficient check; coefficient tables are checked value-for-value by CRC.
 *
 * BLIND SPOTS (critic R3d A-7; keep as TODO): (1) every coefficient set is exactly symmetric, so tap order / data
 *   direction is invisible (a reversed-tap mutation passes); (2) accumulator errors confined below bit 15 that do
 *   not carry across the >>15 truncation are invisible (e.g. a MAC that drops low bits); (3) no saturation occurs
 *   with this stimulus (generator: 0 events), so the saturating paths are not exercised. Results from this bench
 *   must NOT be cited as [L1] for asymmetric or calibrated coefficient sets.
 * CHANNEL_INFO lifetime: T8 / T1 rebuild a fresh stack CHANNEL_INFO on every call (fira_tree.c:468 pattern, cost
 *   inside the bracket); P1 keeps one static list for the lifetime of its persistent task.
 *
 * [ASSUME P1-IDX] (FB_P_FIRA_P1 only): Legacy writes the advanced input/output indices back into the task's TCBs
 *   after each run (archived legacy header note on ADI_FIR_CHANNEL_BUFFER_INFO / adi_fir_UpdateTask), so a re-queued
 *   task continues where it stopped: input index +64 mod L, output index +192 mod 192. Layout copied from ADI EE408
 *   Direct_Replacement (Processing.h:13-16: circular length multiple of the block and >= block+taps, write pointer
 *   starts at L-block, FIRA index at L-block-taps+1; Processing.c:182 re-queues ONE task per block). That example
 *   is floating point with one input buffer per channel; here the mode is fixed point and the 8 channels share one
 *   input buffer -> [L4] until the goldens pass on the board. If only P1 fails: rebuild with -DFIRBENCH_P1_FXD_EACH
 *   (re-issue FixedPointEnable before every QueueTask) to separate a mode-persistence problem from an index problem.
 * [ASSUME FLUSH-IN]: like fira_tree.c, the core-written input is NOT explicitly flushed before QueueTask (driver
 *   cache management / non-cached L1 placement, the F4/F5 [L1] precedent). -DFIRBENCH_FLUSH_IN adds the flush.
 *
 * C9: RAW counters only. FREE-RUN: no breakpoint inside the frame loops (a FIRA spin + breakpoint can deadlock).
 * Build (target): add to the FIRA bench build next to fira_regression.c (-proc ADSP-21569 -DTARGET_SHARC
 *   -DFIRA_USE_REAL_ADI_FIR_HEADER), include path += sprint7/dsp/firbench, call site = bench_main_firbench.diff.
 * Build (desktop): run_firbench_host.sh (-DFB_HOST_MAIN, optional host FIRA emulator host/fb_fira_emu_host.c).
 */
#include <stdint.h>
#include <string.h>
#include "bench_harness.h"      /* BENCH_FRAME / BENCH_NFR (read-only) */
#include "dolph_w8_q15.h"       /* g_dolph_w8_q15[8] -- negative control only (frozen, read-only) */
#include "fb_coeffs.h"          /* generated: FB_COEF_T63/T127/T255, FB_COEF_CRC_t, FB_CHIRP_CRC */
#include "fb_goldens.h"         /* generated: FB_GOLDEN_CRC[3][8] */
#include "s7_firbench.h"

#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
#include <drivers/fir/adi_fir.h>    /* real Legacy header on the board (== archived adi_fir_legacy_2156x.h) */
#include <sys/cache.h>              /* flush_data_buffer (CCES SHARC builtin, same as fira_tree.c A5) */
#endif
#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)
#include <services/pwr/adi_pwr.h>   /* adi_pwr_GetCoreClkFreq (pwr service inited at startup by bench_main.c) */
#endif

#ifdef FB_HOST_MAIN
#include <stdio.h>
#include <time.h>
#include "chirp_input.h"            /* host only: the frozen chirp (on target: the ONE copy in bench_harness.c) */
const int32_t *bench_chirp_input(void) { return CHIRP_INPUT; }
uint32_t bench_cyc_target(void) { return (uint32_t)clock(); }   /* plumbing only: host cycles are MEANINGLESS */
#else
extern const int32_t *bench_chirp_input(void);    /* bench_harness.c:32 */
extern uint32_t bench_cyc_target(void);           /* bench_main.c:118 (TARGET_SHARC) = clock() = CCLK cycles */
#endif

#define FB_VERSION   0x20260927u
#define FB_FRAME     BENCH_FRAME                   /* 64 */
#define FB_NFR       BENCH_NFR                     /* 1024 */
#define FB_WARM      4u                            /* warm-up frames: run + CRC'd, not in the stats */
#define FB_OUT3      (FB_FRAME * 3)                /* 192 words: 3 x 32-bit writeback per output (DP-01) */
#define FB_GUARD     8                             /* one 32-byte line of guard words behind each channel */
#define FB_OSTRIDE   (FB_OUT3 + FB_GUARD)          /* 200 words = 25 cache lines per channel */
#define FB_LINLEN    320                           /* >= FB_MAXTAPS-1+FB_FRAME = 318, padded to whole lines */
#define FB_CIRCMAX   320                           /* FB_CIRCLEN(255) */
#define FB_CIRCLEN(n) ((uint32_t)FB_FRAME * (((uint32_t)(n) + 2u * FB_FRAME - 1u) / FB_FRAME))  /* >= n+64, k*64 */
#define FB_SENT      0x5A5A5A5A
#define FB_SPIN_LIMIT 20000000u                    /* spin-iteration cap -> rc 7 instead of a silent hang */

typedef char fb_chk_lin[(FB_LINLEN >= FB_MAXTAPS - 1 + FB_FRAME) ? 1 : -1];
typedef char fb_chk_circ[(FB_CIRCMAX >= FB_CIRCLEN(FB_MAXTAPS)) ? 1 : -1];
typedef char fb_chk_nch[(FB_NCH == FB_NCHAN && FB_NCH == DOLPH_W8_NCH && FB_NTAPSET == FB_NTS) ? 1 : -1];

/* ---------------- readouts (definitions; honest not-run sentinels) ---------------- */
volatile uint32_t g_fb_version     = FB_VERSION;
volatile uint32_t g_fb_build_flags = 0u;
volatile int      g_fb_valid       = 0;
volatile int      g_fb_open_rc     = -99;
volatile int      g_fb_close_rc    = -99;
volatile uint32_t g_fb_cclk_hz     = 0u;
volatile int      g_fb_cclk_rc     = -99;
volatile uint32_t g_fb_ccnt_read_cyc = 0u;
volatile uint32_t g_fb_chirp_crc   = 0u;
volatile int      g_fb_chirp_ok    = -99;
volatile uint32_t g_fb_coef_crc[FB_NTS];
volatile int      g_fb_coef_ok[FB_NTS];
volatile uint32_t g_fb_addr_coef[FB_NTS];
volatile uint32_t g_fb_addr_lin  = 0u;
volatile uint32_t g_fb_addr_circ = 0u;
volatile uint32_t g_fb_addr_out3 = 0u;
volatile uint32_t g_fb_addr_y    = 0u;
volatile int      g_fb_rc[FB_NPATH][FB_NTS];
volatile int      g_fb_io1[FB_NPATH][FB_NTS];
volatile uint32_t g_fb_frames[FB_NPATH][FB_NTS];
volatile uint32_t g_fb_cyc_last[FB_NPATH][FB_NTS];
volatile uint32_t g_fb_cyc_max[FB_NPATH][FB_NTS];
volatile uint32_t g_fb_cyc_min[FB_NPATH][FB_NTS];
volatile uint32_t g_fb_crc[FB_NPATH][FB_NTS][FB_NCHAN];
volatile int      g_fb_pass[FB_NPATH][FB_NTS][FB_NCHAN];
volatile int      g_fb_pass_all[FB_NPATH][FB_NTS];
volatile int      g_fb_usable[FB_NPATH][FB_NTS];
volatile uint32_t g_fb_neg_crc[FB_NCHAN];
volatile int      g_fb_neg_fail_all = -99;

/* ---------------- tables ---------------- */
static const int32_t *const s_fb_coef[FB_NTAPSET] = { FB_COEF_T63, FB_COEF_T127, FB_COEF_T255 };
static const uint16_t       s_fb_taps[FB_NTAPSET] = { FB_TAPS_0, FB_TAPS_1, FB_TAPS_2 };
static const uint32_t       s_fb_ccrc[FB_NTAPSET] = { FB_COEF_CRC_0, FB_COEF_CRC_1, FB_COEF_CRC_2 };

/* ---------------- working set (static, off-stack; ~15 KB coefficients are const) ----------------
 * s_fb_lin : linear input [history(ntaps-1) | frame(64)] for T8 / T1 / CORE (shared by the 8 channels: mono input).
 * s_fb_circ: circular input for P1 (length FB_CIRCLEN(ntaps)).
 * s_fb_out3: per-channel FIRA writeback regions (64 x 3 words) + 8 guard words each; written ONLY by FIRA DMA
 *            (plus the per-run sentinel fill that is flushed before any task is queued).
 * s_fb_y   : per-channel Q31 output of the frame (postscale / core writes, CRC reads after the bracket). */
#pragma align 32
static int32_t  s_fb_lin[FB_LINLEN];
#pragma align 32
static int32_t  s_fb_circ[FB_CIRCMAX];
#pragma align 32
static int32_t  s_fb_out3[FB_NCH * FB_OSTRIDE];
static int32_t  s_fb_y[FB_NCH][FB_FRAME];
static int32_t  s_fb_ph[FB_NCH * FB_TAPS_1];      /* negative-control placeholder coefficients */
static uint32_t s_fb_crcs[FB_NCH];

#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
#pragma align 32
static uint8_t  s_fb_tm1[FIR_MEM_SIZE(1)];        /* T8: one task memory re-used serially (fira_tree.c pattern) */
#pragma align 32
static uint8_t  s_fb_tm8[FIR_MEM_SIZE(FB_NCH)];   /* T1 / P1 */
/* P1 only: the persistent task's channel list. Built ONCE per P1 run and never touched while that task lives:
 * static lifetime because the driver may keep the list pointer of a task that outlives the creating call (ADI
 * Direct_Replacement keeps its FirTaskChannels[] global for the same reason). T8 / T1 do NOT use it: they rebuild
 * a fresh CHANNEL_INFO on every call, exactly like fira_tree.c:468 (board-proven F4/F5 pattern), so nothing the
 * driver might write back into a caller's CHANNEL_INFO can leak into the next frame. */
static ADI_FIR_CHANNEL_INFO s_fb_ci_p1[FB_NCH];
static ADI_FIR_DEV_HANDLE   s_fb_hdev = 0;
static ADI_FIR_TASK_HANDLE  s_fb_hp1  = 0;
static volatile uint32_t    s_fb_done = 0u;

/* Legacy completion: ALL_CHANNEL_DONE once per task (MCP.c:103; same signature as fira_tree.c fira_done_cb) */
static void fb_done_cb(void *pCBParam, ADI_FIR_EVENT Event, void *pArg)
{
    (void)pCBParam; (void)pArg;
    if (Event == ADI_FIR_EVENT_ALL_CHANNEL_DONE) { s_fb_done++; }
}
#endif

/* ---------------- helpers ---------------- */
static void fb_crc32_update(uint32_t *c, const int32_t *d, int n)   /* == bench_harness.c crc32_buf, streaming */
{
    int i, b, k;
    for (i = 0; i < n; i++) {
        uint32_t v = (uint32_t)d[i];
        for (b = 0; b < 4; b++) {
            *c ^= (uint8_t)(v >> (8 * b));
            for (k = 0; k < 8; k++) *c = (*c & 1u) ? (*c >> 1) ^ 0xEDB88320u : (*c >> 1);
        }
    }
}

static inline int32_t fb_sat32(int64_t v)
{
    if (v > (int64_t)INT32_MAX) return INT32_MAX;
    if (v < (int64_t)INT32_MIN) return INT32_MIN;
    return (int32_t)v;
}

/* core, direct form: y[j] = sat(sum_k c[k] * x[j-k] >> 15); b = [hist(n-1) | frame], newest of output j = b[j+n-1] */
static void fb_core_direct(const int32_t *c, int n, const int32_t *b, int32_t *y)
{
    int j, k;
    for (j = 0; j < FB_FRAME; j++) {
        const int32_t *xp = &b[j + n - 1];
        int64_t acc = 0;
        for (k = 0; k < n; k++) acc += (int64_t)c[k] * (int64_t)xp[-k];
        y[j] = fb_sat32(acc >> 15);
    }
}

/* core, symmetric-folded (c[k] == c[n-1-k], odd n, guaranteed by the generator): exact int64 -> bit-identical */
static void fb_core_sym(const int32_t *c, int n, const int32_t *b, int32_t *y)
{
    int j, k;
    const int m = (n - 1) / 2;
    for (j = 0; j < FB_FRAME; j++) {
        const int32_t *lo = &b[j];
        const int32_t *hi = &b[j + n - 1];
        int64_t acc = (int64_t)c[m] * (int64_t)lo[m];
        for (k = 0; k < m; k++) acc += (int64_t)c[k] * ((int64_t)hi[-k] + (int64_t)lo[k]);
        y[j] = fb_sat32(acc >> 15);
    }
}

#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
/* FIRA 3-word output -> Q31: low 64 bits of the 80-bit exact MAC (|acc| < 2^45 here, generator report),
 * arithmetic >>15 (floor, == golden), saturate. Same arithmetic as fira_tree.c fira_postscale_dec (ratio 1). */
static void fb_postscale(const int32_t *w3, int32_t *y)
{
    int j;
    for (j = 0; j < FB_FRAME; j++) {
        uint64_t lo = (uint32_t)w3[3 * j];
        uint64_t hi = (uint32_t)w3[3 * j + 1];
        y[j] = fb_sat32(((int64_t)((hi << 32) | lo)) >> 15);
    }
}

/* one Legacy CHANNEL_INFO, field order per legacy hdr :46-54, SINGLE_RATE, window = 64 OUTPUTS (fira_make_channel) */
static void fb_ci_fill(ADI_FIR_CHANNEL_INFO *ci, uint16_t n, const int32_t *coef,
                       int32_t *in_base, uint32_t in_count, int32_t *in_index, int32_t *out3)
{
    memset(ci, 0, sizeof(*ci));
    ci->nTapLength         = n;
    ci->nWindowSize        = (uint32_t)FB_FRAME;
    ci->eSampling          = ADI_FIR_SAMPLING_SINGLE_RATE;
    ci->nSamplingRatio     = 1u;
    ci->nCoefficientCount  = n;
    ci->pCoefficientIndex  = (void *)coef;
    ci->nCoefficientModify = 1;
    ci->pOutputBuffBase    = (void *)out3;
    ci->nOutputBuffCount   = (uint32_t)FB_OUT3;          /* 64 x 3 words (DP-01) -> exactly out_count filled */
    ci->nOutputBuffModify  = 1;
    ci->pOutputBuffIndex   = (void *)out3;
    ci->pInputBuffBase     = (void *)in_base;
    ci->nInputBuffCount    = in_count;                   /* linear: n+63 ; circular: L >= n+64 */
    ci->nInputBuffModify   = 1;
    ci->pInputBuffIndex    = (void *)in_index;
}

static int fb_spin(void)
{
    uint32_t k = 0u;
    while (s_fb_done < 1u) { if (++k > FB_SPIN_LIMIT) return 7; }
    return 0;
}

/* channel c on the LINEAR input [hist(n-1) | 64 new] (T8 / T1): count n+63, index = base */
static void fb_ci_lin(ADI_FIR_CHANNEL_INFO *ci, int c, uint16_t n, const int32_t *coef)
{
    fb_ci_fill(ci, n, coef + c * (int)n, s_fb_lin, (uint32_t)n + (uint32_t)FB_FRAME - 1u, s_fb_lin,
               &s_fb_out3[c * FB_OSTRIDE]);
}

/* T8: per channel a FRESH CHANNEL_INFO (stack local, like fira_tree.c:468) + CreateTask(1) + FixedPointEnable +
 * Queue + spin + invalidate + postscale (fira_run_segment shape; the rebuild cost is inside the bracket there too) */
static int fb_fira_t8_frame(uint16_t n, const int32_t *coef)
{
    int c;
    for (c = 0; c < FB_NCH; c++) {
        ADI_FIR_CHANNEL_INFO ci;
        ADI_FIR_TASK_HANDLE h = 0;
        int32_t *o3 = &s_fb_out3[c * FB_OSTRIDE];
        fb_ci_lin(&ci, c, n, coef);
        if (adi_fir_CreateTask(s_fb_hdev, &ci, 1u, (void *)s_fb_tm1, (uint32_t)FIR_MEM_SIZE(1), &h)
            != ADI_FIR_RESULT_SUCCESS) return 3;
        if (adi_fir_FixedPointEnable(h, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER) != ADI_FIR_RESULT_SUCCESS) return 4;
        s_fb_done = 0u;
        if (adi_fir_QueueTask(h) != ADI_FIR_RESULT_SUCCESS) return 5;
        if (fb_spin() != 0) return 7;
        flush_data_buffer((void *)o3, (void *)(o3 + FB_OUT3), 1);   /* IO1d: invalidate before the core reads */
        fb_postscale(o3, s_fb_y[c]);
    }
    return 0;
}

/* common tail of the 8-channel task (T1 / P1): queue, one DONE, one invalidate over the 8 regions, 8 postscales */
static int fb_fira_8ch_finish(ADI_FIR_TASK_HANDLE h)
{
    int c;
    s_fb_done = 0u;
    if (adi_fir_QueueTask(h) != ADI_FIR_RESULT_SUCCESS) return 5;
    if (fb_spin() != 0) return 7;
    flush_data_buffer((void *)s_fb_out3, (void *)(s_fb_out3 + (FB_NCH - 1) * FB_OSTRIDE + FB_OUT3), 1);
    for (c = 0; c < FB_NCH; c++) fb_postscale(&s_fb_out3[c * FB_OSTRIDE], s_fb_y[c]);
    return 0;
}

/* T1: 8 FRESH CHANNEL_INFOs every frame (stack locals, alive until the task is done) + CreateTask(8) + FXD + tail */
static int fb_fira_t1_frame(uint16_t n, const int32_t *coef)
{
    int c;
    ADI_FIR_CHANNEL_INFO ci[FB_NCH];
    ADI_FIR_TASK_HANDLE h = 0;
    for (c = 0; c < FB_NCH; c++) fb_ci_lin(&ci[c], c, n, coef);
    if (adi_fir_CreateTask(s_fb_hdev, ci, (uint32_t)FB_NCH, (void *)s_fb_tm8, (uint32_t)FIR_MEM_SIZE(FB_NCH), &h)
        != ADI_FIR_RESULT_SUCCESS) return 3;
    if (adi_fir_FixedPointEnable(h, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER) != ADI_FIR_RESULT_SUCCESS) return 4;
    return fb_fira_8ch_finish(h);
}

/* P1: the persistent task only (created once per run from s_fb_ci_p1); optional per-frame FXD re-issue */
static int fb_fira_p1_frame(void)
{
#ifdef FIRBENCH_P1_FXD_EACH
    if (adi_fir_FixedPointEnable(s_fb_hp1, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER) != ADI_FIR_RESULT_SUCCESS) return 4;
#endif
    return fb_fira_8ch_finish(s_fb_hp1);
}
#endif /* FIRA_USE_REAL_ADI_FIR_HEADER */

#define FB_STAT(p, t, v) do { g_fb_cyc_last[p][t] = (v); \
                              if ((v) > g_fb_cyc_max[p][t]) g_fb_cyc_max[p][t] = (v); \
                              if ((v) < g_fb_cyc_min[p][t]) g_fb_cyc_min[p][t] = (v); } while (0)

/* IO1 frame-0 check: every one of the 64x3 words per channel overwritten, every guard word untouched */
static int fb_io1_check(void)
{
    int c, i;
    for (c = 0; c < FB_NCH; c++) {
        const int32_t *o3 = &s_fb_out3[c * FB_OSTRIDE];
        for (i = 0; i < FB_OUT3; i++) if (o3[i] == (int32_t)FB_SENT) return 0;
        for (i = FB_OUT3; i < FB_OSTRIDE; i++) if (o3[i] != (int32_t)FB_SENT) return 0;
    }
    return 1;
}

/* One run = one path x one tap set over all FB_NFR frames from zero state.
 * coef = 8 x n table; t = tap-set index (selects the golden row); neg != 0 -> negative control (no stats). */
static void fb_run(int p, int t, const int32_t *coef, int neg)
{
    const int32_t *chirp = bench_chirp_input();
    const int n = (int)s_fb_taps[t];
    const int fira = (p <= FB_P_FIRA_P1);
    uint32_t f;
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    uint32_t L = FB_CIRCLEN(n), wp = 0u;       /* P1 circular length / write pointer */
#endif
    int c, rc = 0, all = 1;

    if (!neg) {
        g_fb_rc[p][t] = -99; g_fb_io1[p][t] = fira ? -99 : -2; g_fb_frames[p][t] = 0u;
        g_fb_cyc_last[p][t] = 0u; g_fb_cyc_max[p][t] = 0u; g_fb_cyc_min[p][t] = 0xFFFFFFFFu;
    }
#ifndef FIRA_USE_REAL_ADI_FIR_HEADER
    if (fira) { g_fb_rc[p][t] = -1; return; }       /* honest: FIRA path not built -> not run, pass_all stays -99 */
#endif

    /* ---- per-run init (OUTSIDE any bracket): zero history (ST1 start), sentinel outputs (IO1), CRC seeds ---- */
    memset(s_fb_lin, 0, sizeof(s_fb_lin));
    memset(s_fb_circ, 0, sizeof(s_fb_circ));
    memset(s_fb_y, 0, sizeof(s_fb_y));
    for (c = 0; c < FB_NCH * FB_OSTRIDE; c++) s_fb_out3[c] = (int32_t)FB_SENT;
    for (c = 0; c < FB_NCH; c++) s_fb_crcs[c] = 0xFFFFFFFFu;
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    if (fira) {
        /* push the sentinel to memory and drop the lines, so FIRA DMA output can never be overwritten by a later
         * write-back of core-dirtied lines (fira_tree.c A5 flush-back hazard) */
        flush_data_buffer((void *)s_fb_out3, (void *)(s_fb_out3 + FB_NCH * FB_OSTRIDE), 1);
        if (g_fb_open_rc != 0) { rc = (g_fb_open_rc > 0) ? g_fb_open_rc : 1; goto done; }
        s_fb_hp1 = 0;
        if (p == FB_P_FIRA_P1) {
            /* persistent task: channel list built ONCE (static, untouched while the task lives), task created and
             * set to fixed point ONCE, all outside the frame budget. Circular input: L = FB_CIRCLEN(n) >= n+64,
             * FIRA index starts at L-64-n+1 (Direct_Replacement FIRA_INDEX_START) */
            for (c = 0; c < FB_NCH; c++)
                fb_ci_fill(&s_fb_ci_p1[c], (uint16_t)n, coef + c * n, s_fb_circ, L,
                           &s_fb_circ[L - (uint32_t)FB_FRAME - (uint32_t)n + 1u], &s_fb_out3[c * FB_OSTRIDE]);
            if (adi_fir_CreateTask(s_fb_hdev, s_fb_ci_p1, (uint32_t)FB_NCH, (void *)s_fb_tm8,
                                   (uint32_t)FIR_MEM_SIZE(FB_NCH), &s_fb_hp1) != ADI_FIR_RESULT_SUCCESS) { rc = 3; goto done; }
            if (adi_fir_FixedPointEnable(s_fb_hp1, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER)
                != ADI_FIR_RESULT_SUCCESS) { rc = 4; goto done; }
            wp = L - (uint32_t)FB_FRAME;              /* write pointer start (Direct_Replacement WP_START) */
        }
    }
#endif

    for (f = 0u; f < (uint32_t)FB_NFR; f++) {
        const int32_t *x = &chirp[f * (uint32_t)FB_FRAME];
        uint32_t t0, t1;

        t0 = bench_cyc_target();                                        /* ======== frame bracket OPEN ======== */
        if (p == FB_P_FIRA_P1) {
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
            memcpy(&s_fb_circ[wp], x, (size_t)FB_FRAME * sizeof(int32_t));
#ifdef FIRBENCH_FLUSH_IN
            flush_data_buffer((void *)&s_fb_circ[wp], (void *)&s_fb_circ[wp + FB_FRAME], 0);
#endif
            wp += (uint32_t)FB_FRAME; if (wp >= L) wp = 0u;
            rc = fb_fira_p1_frame();
#endif
        } else {
            memcpy(&s_fb_lin[n - 1], x, (size_t)FB_FRAME * sizeof(int32_t));   /* [hist(n-1) | new 64] */
#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(FIRBENCH_FLUSH_IN)
            if (fira) flush_data_buffer((void *)s_fb_lin, (void *)&s_fb_lin[n - 1 + FB_FRAME], 0);
#endif
            if (p == FB_P_CORE_C) {
                for (c = 0; c < FB_NCH; c++) fb_core_direct(coef + c * n, n, s_fb_lin, s_fb_y[c]);
            } else if (p == FB_P_CORE_SYM) {
                for (c = 0; c < FB_NCH; c++) fb_core_sym(coef + c * n, n, s_fb_lin, s_fb_y[c]);
            }
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
            else if (p == FB_P_FIRA_T8) { rc = fb_fira_t8_frame((uint16_t)n, coef); }
            else                        { rc = fb_fira_t1_frame((uint16_t)n, coef); }
#endif
            memmove(s_fb_lin, &s_fb_lin[FB_FRAME], (size_t)(n - 1) * sizeof(int32_t));   /* ST1: keep last n-1 */
        }
        t1 = bench_cyc_target();                                        /* ======== frame bracket CLOSE ======= */

        /* ---- outside the bracket ---- */
        if (rc != 0) break;
        if (fira && f == 0u && !neg) g_fb_io1[p][t] = fb_io1_check();
        for (c = 0; c < FB_NCH; c++) fb_crc32_update(&s_fb_crcs[c], s_fb_y[c], FB_FRAME);
        if (!neg && f >= FB_WARM) { uint32_t d = t1 - t0; FB_STAT(p, t, d); g_fb_frames[p][t]++; }
    }

#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
done:
#endif
    if (neg) {
        int miss = 1;
        for (c = 0; c < FB_NCH; c++) {
            g_fb_neg_crc[c] = s_fb_crcs[c] ^ 0xFFFFFFFFu;
            if (rc != 0 || g_fb_neg_crc[c] == FB_GOLDEN_CRC[t][c]) miss = 0;
        }
        g_fb_neg_fail_all = miss;
        return;
    }
    g_fb_rc[p][t] = rc;
    for (c = 0; c < FB_NCH; c++) {
        g_fb_crc[p][t][c]  = s_fb_crcs[c] ^ 0xFFFFFFFFu;
        g_fb_pass[p][t][c] = (rc == 0 && g_fb_crc[p][t][c] == FB_GOLDEN_CRC[t][c]) ? 1 : 0;
        if (!g_fb_pass[p][t][c]) all = 0;
    }
    g_fb_pass_all[p][t] = all;
    g_fb_usable[p][t] = (all == 1 && rc == 0 && (g_fb_io1[p][t] == 1 || g_fb_io1[p][t] == -2)
                         && g_fb_chirp_ok == 1 && g_fb_coef_ok[t] == 1 && g_fb_frames[p][t] == FB_NFR - FB_WARM) ? 1 : 0;
}

static void fb_reset_readouts(void)
{
    int p, t, c;
    g_fb_version = FB_VERSION;
    g_fb_build_flags = 0u
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
        | 1u
#endif
#ifdef TARGET_SHARC
        | 2u
#endif
#ifdef FIRBENCH_FLUSH_IN
        | 4u
#endif
#ifdef FIRBENCH_P1_FXD_EACH
        | 8u
#endif
#ifdef FB_HOST_EMU
        | 16u
#endif
        ;
    g_fb_valid = 0; g_fb_open_rc = -99; g_fb_close_rc = -99; g_fb_cclk_hz = 0u; g_fb_cclk_rc = -99;
    g_fb_ccnt_read_cyc = 0u; g_fb_chirp_crc = 0u; g_fb_chirp_ok = -99; g_fb_neg_fail_all = -99;
    for (t = 0; t < FB_NTS; t++) { g_fb_coef_crc[t] = 0u; g_fb_coef_ok[t] = -99; g_fb_addr_coef[t] = 0u; }
    g_fb_addr_lin = 0u; g_fb_addr_circ = 0u; g_fb_addr_out3 = 0u; g_fb_addr_y = 0u;
    for (p = 0; p < FB_NPATH; p++)
        for (t = 0; t < FB_NTS; t++) {
            g_fb_rc[p][t] = -99; g_fb_io1[p][t] = -99; g_fb_frames[p][t] = 0u; g_fb_pass_all[p][t] = -99;
            g_fb_usable[p][t] = 0;
            g_fb_cyc_last[p][t] = 0u; g_fb_cyc_max[p][t] = 0u; g_fb_cyc_min[p][t] = 0xFFFFFFFFu;
            for (c = 0; c < FB_NCH; c++) { g_fb_crc[p][t][c] = 0u; g_fb_pass[p][t][c] = -99; }
        }
    for (c = 0; c < FB_NCH; c++) g_fb_neg_crc[c] = 0u;
}

int s7_firbench_run(void)
{
    int p, t, c, k;
    uint32_t crc;

    fb_reset_readouts();
    { uint32_t a = bench_cyc_target(); uint32_t b = bench_cyc_target(); g_fb_ccnt_read_cyc = b - a; }
    /* placement readouts (addresses as the core sees them; decoded off-board against the build's .map) */
    for (t = 0; t < FB_NTS; t++) g_fb_addr_coef[t] = (uint32_t)(uintptr_t)s_fb_coef[t];
    g_fb_addr_lin  = (uint32_t)(uintptr_t)s_fb_lin;
    g_fb_addr_circ = (uint32_t)(uintptr_t)s_fb_circ;
    g_fb_addr_out3 = (uint32_t)(uintptr_t)s_fb_out3;
    g_fb_addr_y    = (uint32_t)(uintptr_t)&s_fb_y[0][0];
#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)
    { uint32_t cclk = 0u; g_fb_cclk_rc = (int)adi_pwr_GetCoreClkFreq(0u, &cclk); g_fb_cclk_hz = cclk; }
#endif

    /* data self-checks (value-for-value via CRC; NOT sum_c 2h_c = delta) */
    crc = 0xFFFFFFFFu; fb_crc32_update(&crc, bench_chirp_input(), FB_FRAME * FB_NFR);
    g_fb_chirp_crc = crc ^ 0xFFFFFFFFu; g_fb_chirp_ok = (g_fb_chirp_crc == FB_CHIRP_CRC) ? 1 : 0;
    for (t = 0; t < FB_NTS; t++) {
        crc = 0xFFFFFFFFu; fb_crc32_update(&crc, s_fb_coef[t], FB_NCH * (int)s_fb_taps[t]);
        g_fb_coef_crc[t] = crc ^ 0xFFFFFFFFu; g_fb_coef_ok[t] = (g_fb_coef_crc[t] == s_fb_ccrc[t]) ? 1 : 0;
    }

    /* FIRA paths first (the primary measurement), then the core paths */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    g_fb_open_rc = 0;
    if (adi_fir_Open(0u, &s_fb_hdev) != ADI_FIR_RESULT_SUCCESS) g_fb_open_rc = 1;
    else if (adi_fir_RegisterCallback(s_fb_hdev, fb_done_cb, 0) != ADI_FIR_RESULT_SUCCESS) g_fb_open_rc = 2;
#else
    g_fb_open_rc = -1; g_fb_close_rc = -1;
#endif
    for (t = 0; t < FB_NTS; t++)
        for (p = FB_P_FIRA_T8; p <= FB_P_FIRA_P1; p++) fb_run(p, t, s_fb_coef[t], 0);
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    g_fb_close_rc = (g_fb_open_rc == 0 && adi_fir_Close(s_fb_hdev) == ADI_FIR_RESULT_SUCCESS) ? 0 : 1;
    s_fb_hdev = 0;
#endif
    for (t = 0; t < FB_NTS; t++)
        for (p = FB_P_CORE_C; p <= FB_P_CORE_SYM; p++) fb_run(p, t, s_fb_coef[t], 0);

    /* negative control (FG2 on the board): Dolph-20 weight x delta[k-63], 127 taps, CORE_C -> must MISS all 8 */
    memset(s_fb_ph, 0, sizeof(s_fb_ph));
    k = (FB_TAPS_1 - 1) / 2;
    for (c = 0; c < FB_NCH; c++) s_fb_ph[c * FB_TAPS_1 + k] = g_dolph_w8_q15[c];
    fb_run(FB_P_CORE_C, 1, s_fb_ph, 1);

#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)
    g_fb_valid = 1;          /* cycles meaningful ONLY here, and per path x tap set only where g_fb_usable == 1 */
#endif
    return g_fb_valid;
}

#ifdef FB_HOST_MAIN
/* Desktop harness [L2 host plumbing; cycles MEANINGLESS]. Expectation depends on the build:
 *   default          : core paths PASS 3x2x8, FIRA paths not built (rc -1, pass_all -99), negative control MISSES
 *   -DFB_EXPECT_EMU  : + host FIRA emulator (host/fb_fira_emu_host.c): all 5 paths PASS, io1 == 1 on FIRA paths
 *   -DFB_EXPECT_STUB : + emulator in stub mode (FIRA writes nothing): every FIRA path FAILS (pass_all 0, io1 0) */
static const char *const s_pname[FB_NPATH] = { "FIRA_T8", "FIRA_T1", "FIRA_P1", "CORE_C", "CORE_SYM" };
int main(void)
{
    int p, t, c, ok = 1;
    (void)s7_firbench_run();
    printf("==== s7_firbench host run [L2 host; cycles MEANINGLESS off-board] ====\n");
    printf("version=0x%08X build_flags=0x%X valid=%d open_rc=%d close_rc=%d chirp_ok=%d coef_ok=%d/%d/%d neg_fail_all=%d\n",
           (unsigned)g_fb_version, (unsigned)g_fb_build_flags, g_fb_valid, g_fb_open_rc, g_fb_close_rc, g_fb_chirp_ok,
           g_fb_coef_ok[0], g_fb_coef_ok[1], g_fb_coef_ok[2], g_fb_neg_fail_all);
    for (t = 0; t < FB_NTS; t++)
        for (p = 0; p < FB_NPATH; p++) {
            printf("  T%-3d %-8s rc=%3d io1=%3d pass_all=%3d usable=%d frames=%4u pass[c]=", (int)s_fb_taps[t], s_pname[p],
                   g_fb_rc[p][t], g_fb_io1[p][t], g_fb_pass_all[p][t], g_fb_usable[p][t], (unsigned)g_fb_frames[p][t]);
            for (c = 0; c < FB_NCH; c++) printf("%d", g_fb_pass[p][t][c] < 0 ? 9 : g_fb_pass[p][t][c]);
            printf("  crc0=0x%08X\n", (unsigned)g_fb_crc[p][t][0]);
        }
    ok = ok && g_fb_valid == 0 && g_fb_chirp_ok == 1 && g_fb_coef_ok[0] == 1 && g_fb_coef_ok[1] == 1
            && g_fb_coef_ok[2] == 1 && g_fb_neg_fail_all == 1;
    for (t = 0; t < FB_NTS; t++) {
        for (p = FB_P_CORE_C; p <= FB_P_CORE_SYM; p++) ok = ok && g_fb_pass_all[p][t] == 1 && g_fb_rc[p][t] == 0;
        for (p = FB_P_FIRA_T8; p <= FB_P_FIRA_P1; p++) {
#if defined(FB_EXPECT_EMU)
            ok = ok && g_fb_pass_all[p][t] == 1 && g_fb_rc[p][t] == 0 && g_fb_io1[p][t] == 1;
#elif defined(FB_EXPECT_STUB)
            ok = ok && g_fb_pass_all[p][t] == 0 && g_fb_io1[p][t] == 0;
            for (c = 0; c < FB_NCH; c++) ok = ok && g_fb_pass[p][t][c] == 0;
#else
            ok = ok && g_fb_pass_all[p][t] == -99 && g_fb_rc[p][t] == -1;
#endif
        }
    }
    printf("==== host expectation: %s ====\n", ok ? "MET" : "NOT MET");
    return ok ? 0 : 1;
}
#endif
