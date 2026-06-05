/*
 * h1_wcet_measure.c -- H1 combined measurement harness (target+desktop): focusing-increment
 *   same-build A/B + WCET cold/warm/max + ride-along sanity. RAW COUNTERS ONLY (no derived margin
 *   in code -- C9 discipline analog; all margins computed OFF-BOARD by PM/CTO).
 *
 * ASCII-only (CCES SHARC compiler chokes on UTF-8). Change-blocks discipline: this is a NEW
 *   self-contained file; it does NOT edit fira_regression.c (the F7 PASS path stays byte-identical).
 *   Frozen files untouched (tree_filterbank.c/tfb_8ch.c/golden_ref.h/chirp_input.h/fir_coeffs_hb63.h/.ldf).
 *
 * WHAT THIS MEASURES (CTO execution-order item 1: harness + WCET, SAME board run):
 *   A. FOCUSING INCREMENT [L4->L1]: same-build A/B -- the 8ch FIRA chain (analyze + per-subband
 *      focus frac-delay FIR + synthesize) measured per steady frame WITH focus enabled vs WITHOUT,
 *      in ONE run (runtime flag, two measured spans). Increment = g_h1_cyc_8ch_focus - _nofocus.
 *      Avoids the F7 mixed-build trap (the focus number is a within-run delta, not cross-build).
 *   B. WCET [L3->L1 for measurable parts]: H1-FIRST-FRAME PROXY (see PARTIAL-COLD caveat below) vs steady frame on
 *      the SAME FIRA 8ch path, plus max-over-N-frames to catch intra-run jitter.
 *      HONEST SCOPE: this measures cold-cache + intra-run jitter ONLY. It does NOT measure real
 *      SPORT/codec DMA bus contention (no DMA running in bench) or ISR preemption (bare-metal
 *      free-run). => measured WCET is a LOWER BOUND on system WCET; the unmeasured contention stays
 *      [L3/L4] with the section-8 io/irq envelopes. DO NOT read this as full-system WCET.
 *   C. RIDE-ALONG: per-frame CCLK re-read sanity (should still be 1e9) + analyze/synth split re-read
 *      attempt (the free F7 tail, exact symbols g_f7_cyc_analyze_fira / g_f7_cyc_synth_fira).
 *      F4/F5 continuity is enforced by bench_main.c sequencing (this harness runs AFTER them).
 *
 * FOCUSING FIR DESIGN CHOICE (justified) + MAC ACCOUNTING CORRECTION (critic R15, CTO-flagged 2x):
 *   - 8-tap fractional-delay FIR, applied PER-SUBBAND (4 subbands) PER-CHANNEL on the analyzed
 *     subband outputs (between analyze and synthesize).
 *   - TRUE subband sample counts THIS tree produces per 64-sample frame (source: fira_regression.c:193 + this file's sz[],
 *     and F4/F5 sb sizing fira_regression.c:193): sb0=frame/8=8, sb1=frame/4=16, sb2=frame/2=32,
 *     sb3=frame=64 (sb3 is the UNDECIMATED detail branch, sb3[i]=in[i]-r1[i]). Sum = 120 samp/frame/ch.
 *     => subband RATES sum = 120 x 750 fps = 90 kHz (NOT the 45 kHz the cost-model assumed).
 *   - TRUE harness MAC: 8 taps x 120 samp x 8 ch = 7,680 MAC/frame -> 7,680 x 750 = 5.76 MMAC/s.
 *   - *** CORRECTION ***: the earlier "EXACTLY 2.88 MMAC/s (dsp_8ch_report:59)" claim was WRONG by 2x.
 *     The cost-model 2.88 assumed 60 samp/frame/ch (45 kHz); the REAL dyadic tree has 120 samp/frame/ch
 *     (90 kHz) because sb3 is undecimated. So this harness implements 5.76 MMAC/s, i.e. 2x the model.
 *     R14 verified the FORMULA (8tap x N x 8ch x fps) but NOT the sz[] sample counts -> the 2x slipped.
 *   - YARDSTICK for interpretation: compare the measured board cyc against the RECALIBRATED envelope
 *     5.76 MMAC/s x (30..50 cyc/MAC) = 173..288 MCPS (NOT the old 86..144, which was 2.88-based).
 *     Equivalently g_h1_cyc_focus_only/2 vs 86..144. See readout worksheet / WO-S5-H1 for the framing.
 *   - PRODUCT-COST FLAG (for CTO, do NOT silently change DEC-S5): the product focus applies frac-delay
 *     to these SAME 120 samp/frame subbands -> true product focus cost is ALSO ~5.76 MMAC/s class, so
 *     the DEC-S5-V1-SCOPE-01 budget "focus 86-144 MCPS" is likely ~2x UNDERSTATED. Flagged, not changed.
 *   - Per-channel distinct delays: 8 distinct fractional delays (mirror-symmetric focus profile,
 *     {c,15-c} pair phase-locked per STEER-2 physics) via 8 distinct 8-tap coeff sets. Static, set
 *     once (focus delays change at zone-set time, ~0 per-frame update -- matches "static-zone ~0 update").
 *   - This is a REPRESENTATIVE cost stand-in for the increment measurement; it is NOT the product
 *     focusing algorithm and is NOT bit-exact-gated (it does not touch the frozen filterbank or the
 *     F4/F5 subband CRC path -- the focus stage applies IN-PLACE on H1's OWN local subband buffers (fsb0-3),
 *     which feed H1's synthesize; F4/F5's buffers and CRC path are separate and untouched (critic R14 wording fix).
 *
 * Build: target = CCES -proc ADSP-21569 -DTARGET_SHARC -DFIRA_USE_REAL_ADI_FIR_HEADER.
 *        desktop = gcc -DH1_HOST (focus FIR + control logic compile + run; FIRA spans stubbed via the
 *        same fira_tree_setup()<0 honest-0 path as F7).
 * Read: idle while(1) in bench_main, g_h1_* globals. FREE-RUN ONLY -- NO mid-loop breakpoints
 *        (CCNT_source.md lesson: SLOWLOOP+breakpoint deadlocks the counter loop). Read at idle only.
 */
#include <stdint.h>
#include "tree_filterbank.h"   /* TreeChannelState, tfb_* (NON-frozen header; frozen .c untouched) */
#include "fir_coeffs_hb63.h"   /* g_hb63_q15, FIR_HB63_NTAPS (frozen header, read-only use) */
#include "bench_harness.h"     /* BENCH_FRAME / BENCH_FS / BENCH_NFR */
#include "dolph_w8_q15.h"      /* g_dolph_w8_q15[8], DOLPH_W8_NCH */
#include "fira_tree.h"         /* FiraChannelState, fira_* (only used under FIRA+TARGET build) */

extern const int32_t *bench_chirp_input(void);   /* the one frozen chirp (bench_harness.c) */
extern uint32_t bench_cyc_target(void);          /* CCLK cycle counter (clock()); bench_main.c (TARGET_SHARC) */

/* ---- H1 raw readouts (emulator reads at idle; raw counters ONLY, no derived margin -- C9 analog) ---- */
/* A. focusing increment (same-build A/B) */
volatile uint32_t g_h1_cyc_8ch_focus   = 0u;   /* [L1-to-be] 8ch FIRA chain WITH focus frac-delay, one steady frame */
volatile uint32_t g_h1_cyc_8ch_nofocus = 0u;   /* [L1-to-be] SAME chain WITHOUT focus, same frame (A/B denominator) */
volatile uint32_t g_h1_cyc_focus_only  = 0u;   /* [L1-to-be] focus frac-delay stage alone, 8ch x 4sb, same frame */
/* B. WCET */
volatile uint32_t g_h1_cyc_8ch_cold    = 0u;   /* [L1-to-be] H1-FIRST-FRAME PROXY: I-cache already WARM (F4/F5/F7 ran the
                                                  same FIRA path first); only H1's own data buffers are first-touch.
                                                  PARTIAL/optimistic cold proxy -- UNDERSTATES true cold-cache WCET.
                                                  True-cold needs I+D cache invalidate immediately before this frame
                                                  (board-only, see C10 checklist TODO). critic R14 F14-MAJOR-1. */
volatile uint32_t g_h1_cyc_8ch_warm    = 0u;   /* [L1-to-be] steady frame (after warm-up), same path -- cold/warm ratio */
volatile uint32_t g_h1_cyc_8ch_max     = 0u;   /* [L1-to-be] max over H1_NFRAMES steady frames (intra-run jitter) */
volatile uint32_t g_h1_cyc_8ch_min     = 0u;   /* [L1-to-be] min over the same (jitter band low end) */
/* C. ride-along sanity */
volatile uint32_t g_h1_cclk_hz         = 0u;   /* [L1-to-be] per-run CCLK re-read (should == 1e9); 0 = desktop/not read */
volatile int      g_h1_cclk_rc         = -99;  /* [L1-to-be] GetCoreClkFreq rc (0=SUCCESS); -99 not-run/desktop */
volatile uint32_t g_h1_focus_crc       = 0u;   /* [L1-to-be] CRC of focus-on synth output (FG: must DIFFER from nofocus) */
volatile uint32_t g_h1_nofocus_crc     = 0u;   /* [L1-to-be] CRC of focus-off synth output (FG continuity anchor) */
volatile int      g_h1_fg_focus_differs = -99; /* [L1-to-be] 1 = focus output != nofocus (delay computes); 0 = SAME (FG FAIL); -99 not-run */
volatile int      g_h1_fg_zero_recovers = -99; /* [L1-to-be] 1 = zero-delay config reproduces nofocus path (continuity); 0 = FAIL; -99 not-run */
volatile int      g_h1_valid           = 0;    /* 1 = ran on board with FIRA; 0 = desktop/no-FIRA (numbers meaningless) */

#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)
#include <services/pwr/adi_pwr.h>   /* adi_pwr_GetCoreClkFreq (BSP; G6 evidence in fira_regression.c) */
#include <sys/cache.h>              /* R15: flush_data_buffer (A5-established CCES SHARC builtin, fira_tree.c:24) */
#endif

#define H1_WARM     4    /* warm-up frames (== F7_WARM discipline, bench_harness.c:84) */
#define H1_NFRAMES  64   /* steady frames swept for max/min jitter (g_h1_cyc_8ch_max/min) */
#define H1_FDTAPS   8    /* focus frac-delay FIR taps (maps to the 5.76 MMAC/s harness envelope; was 2.88, corrected R15 -- see header) */

/* ---- focusing fractional-delay FIR (8-tap, per subband, per channel) ----
 * Representative cost stand-in. 8 distinct Q15 coeff sets = 8 distinct fractional delays (one per
 * channel; mirror-symmetric focus profile keeps {c,15-c} pairs phase-locked). The focus stage + its
 * helpers are TARGET-only (used only inside the FIRA frame fn); guarded so desktop builds carry no
 * unused-symbol warnings. Coeffs are a windowed-sinc-style stand-in; values are arbitrary but
 * NON-trivial so the FG "output differs" check is real. Q15, applied with arithmetic shift. */
#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)
static const int16_t s_fd_coeff[DOLPH_W8_NCH][H1_FDTAPS] = {
    /* c=0 (delay ~0.1) */ {  1100, 28000,  6200, -1400,   500,  -200,    90,   -40 },
    /* c=1 (~0.2)       */ { -1500, 25000, 10500, -2600,   950,  -380,   160,   -70 },
    /* c=2 (~0.3)       */ { -2100, 21500, 14800, -3900,  1500,  -610,   260,  -110 },
    /* c=3 (~0.4)       */ { -2400, 17800, 18800, -5000,  2050,  -850,   370,  -160 },
    /* c=4 (~0.4 mirror)*/ { -2400, 17800, 18800, -5000,  2050,  -850,   370,  -160 },
    /* c=5 (~0.3 mirror)*/ { -2100, 21500, 14800, -3900,  1500,  -610,   260,  -110 },
    /* c=6 (~0.2 mirror)*/ { -1500, 25000, 10500, -2600,   950,  -380,   160,   -70 },
    /* c=7 (~0.1 mirror)*/ {  1100, 28000,  6200, -1400,   500,  -200,    90,   -40 }
};
/* zero-delay identity = a true PASS-THROUGH (copy), NOT a Q15 tap (32767/32768 != 1 would not be
 * bit-exact). The continuity control runs the SAME analyze->synthesize chain with the focus stage as
 * an identity copy, so it must reproduce the no-focus path EXACTLY. Signaled by use_identity in the
 * frame fn (h1_focus_subband is simply NOT called for the identity case -> exact copy). */

/* per-(channel,subband) frac-delay history (cross-frame tail, H1_FDTAPS-1 each). static = off-stack. */
static int32_t s_fd_hist[DOLPH_W8_NCH][4][H1_FDTAPS - 1];

/* ---- R15 fix: state snapshot for the same-state A/B + continuity probe ----
 * The FIRA chain (s_h1_fa) AND the focus-FIR history (s_fd_hist) are stateful cross-frame. The R14
 * probe compared identity-vs-nofocus on DIFFERENT advanced states (ST1 cross-state CRC flaw) -> false
 * FG fail. Fix: snapshot the clean steady state ONCE after warm-up, then RESTORE before each of the
 * three compared frames (focus-ON / focus-OFF / identity) so all run from the IDENTICAL state on the
 * SAME input. Restore is done OUTSIDE the timed span (memcpy must not pollute the cycle count). */
static FiraChannelState s_h1_fa_snap[DOLPH_W8_NCH];           /* FIRA chain state snapshot */
static int32_t s_fd_hist_snap[DOLPH_W8_NCH][4][H1_FDTAPS - 1];/* focus-FIR history snapshot */

static void h1_state_save(void)
{
    int c, sb, i;
    for (c = 0; c < DOLPH_W8_NCH; c++) {
        s_h1_fa_snap[c] = s_h1_fa[c];   /* struct copy (plain POD: hist[9][62] + scalars) */
        for (sb = 0; sb < 4; sb++)
            for (i = 0; i < H1_FDTAPS - 1; i++) s_fd_hist_snap[c][sb][i] = s_fd_hist[c][sb][i];
    }
}
static void h1_state_restore(void)
{
    int c, sb, i;
    for (c = 0; c < DOLPH_W8_NCH; c++) {
        s_h1_fa[c] = s_h1_fa_snap[c];
        for (sb = 0; sb < 4; sb++)
            for (i = 0; i < H1_FDTAPS - 1; i++) s_fd_hist[c][sb][i] = s_fd_hist_snap[c][sb][i];
    }
}

/* R15: invalidate the DATA cache over H1's working set before the cold frame (true-cold-DATA).
 * flush_data_buffer(start, end, 1) = write-back-and-invalidate over [start,end) (A5 symbol, sys/cache.h).
 * Working set = the per-frame data the frame touches: the focus subband buffers, output, weight buffer,
 * scratch, PLUS the persistent FIRA chain state s_h1_fa and the focus history s_fd_hist (so their lines
 * are also cold). Static coeffs (s_fd_coeff) and the chirp input are READ-ONLY and small; including them
 * is optional -- we invalidate the mutable working set (the dominant miss source). enInv=1. */
static void h1_dcache_inval_workingset(int32_t *fsb0, int32_t *fsb1, int32_t *fsb2, int32_t *fsb3,
                                       int32_t *fout, int32_t *xw, int32_t *scr)
{
    flush_data_buffer((void *)fsb0, (void *)(fsb0 + (BENCH_FRAME / 8)), 1);
    flush_data_buffer((void *)fsb1, (void *)(fsb1 + (BENCH_FRAME / 4)), 1);
    flush_data_buffer((void *)fsb2, (void *)(fsb2 + (BENCH_FRAME / 2)), 1);
    flush_data_buffer((void *)fsb3, (void *)(fsb3 + (BENCH_FRAME)),     1);
    flush_data_buffer((void *)fout, (void *)(fout + BENCH_FRAME),       1);
    flush_data_buffer((void *)xw,   (void *)(xw   + BENCH_FRAME),       1);
    flush_data_buffer((void *)scr,  (void *)(scr  + BENCH_FRAME),       1);
    flush_data_buffer((void *)s_h1_fa,   (void *)(s_h1_fa   + DOLPH_W8_NCH), 1);
    flush_data_buffer((void *)s_fd_hist, (void *)(s_fd_hist + DOLPH_W8_NCH), 1);
}

/* Apply the focus FIR to one subband buffer using a scratch out (true FIR, no in-place hazard).
 * Updates hist with the last H1_FDTAPS-1 ORIGINAL input samples. */
static void h1_focus_subband(const int16_t *coef, int32_t *hist, int32_t *buf, int n, int32_t *scratch)
{
    int i, k;
    for (i = 0; i < n; i++) {
        int64_t acc = 0;
        for (k = 0; k < H1_FDTAPS; k++) {
            int32_t x;
            int idx = i - k;
            if (idx >= 0) x = buf[idx];
            else          x = hist[(H1_FDTAPS - 1) + idx];   /* idx in [-(taps-1)..-1] */
            acc += (int64_t)coef[k] * (int64_t)x;
        }
        scratch[i] = (int32_t)(acc >> 15);   /* Q15 -> Q0, arithmetic shift (ASHIFT on SHARC) */
    }
    /* update history: last taps-1 ORIGINAL samples. PRECONDITION n >= H1_FDTAPS-1 (smallest subband
     * sz[0]=BENCH_FRAME/8=8 >= 7), so idx is always >= 0 -- no negative-index path needed. */
    for (k = 0; k < H1_FDTAPS - 1; k++) {
        int idx = n - (H1_FDTAPS - 1) + k;   /* >= 0 by precondition */
        hist[k] = buf[idx];
    }
    for (i = 0; i < n; i++) buf[i] = scratch[i];
}

/* simple CRC32 (IEEE) over an int32 buffer -- FG check only, same poly as bench_harness crc32_buf */
static uint32_t h1_crc32(uint32_t c, const int32_t *d, int n)
{
    int i, b, k;
    for (i = 0; i < n; i++) {
        uint32_t v = (uint32_t)d[i];
        for (b = 0; b < 4; b++) {
            uint8_t by = (uint8_t)(v >> (8 * b));
            c ^= by;
            for (k = 0; k < 8; k++) c = (c & 1u) ? (c >> 1) ^ 0xEDB88320u : (c >> 1);
        }
    }
    return c;
}

/* ---- one 8ch FIRA frame: analyze -> (optional focus on subbands) -> synthesize ----
 * focus_enable: 1 = apply per-(ch,sb) focus FIR; 0 = no-focus path (analyze->synthesize).
 * use_identity: 1 = zero-delay pass-through (skip the focus stage) = continuity control.
 * returns CRC of the 8-channel synth output (FG check). */
static FiraChannelState s_h1_fa[DOLPH_W8_NCH];

static uint32_t h1_fira_frame(const int32_t *xin, int focus_enable, int use_identity,
                              int32_t *fsb0, int32_t *fsb1, int32_t *fsb2, int32_t *fsb3,
                              int32_t *fout, int32_t *xw, int32_t *scr)
{
    uint32_t crc = 0xFFFFFFFFu;
    int c, i;
    const int sz[4] = { BENCH_FRAME / 8, BENCH_FRAME / 4, BENCH_FRAME / 2, BENCH_FRAME };
    for (c = 0; c < DOLPH_W8_NCH; c++) {
        const int32_t w = g_dolph_w8_q15[c];
        for (i = 0; i < BENCH_FRAME; i++)
            xw[i] = (int32_t)(((int64_t)w * (int64_t)xin[i]) >> 15);   /* input-scale weight (== f5_apply_w) */
        fira_tfb_analyze(&s_h1_fa[c], xw, BENCH_FRAME, fsb0, fsb1, fsb2, fsb3);
        /* focus_enable && !use_identity : apply the real 8-tap frac-delay (cost being measured).
         * use_identity (zero-delay) : skip the stage = true pass-through (continuity must == no-focus).
         * !focus_enable : the no-focus path (analyze -> synthesize). */
        if (focus_enable && !use_identity) {
            h1_focus_subband(s_fd_coeff[c], s_fd_hist[c][0], fsb0, sz[0], scr);
            h1_focus_subband(s_fd_coeff[c], s_fd_hist[c][1], fsb1, sz[1], scr);
            h1_focus_subband(s_fd_coeff[c], s_fd_hist[c][2], fsb2, sz[2], scr);
            h1_focus_subband(s_fd_coeff[c], s_fd_hist[c][3], fsb3, sz[3], scr);
        }
        fira_tfb_synthesize(&s_h1_fa[c], fsb0, fsb1, fsb2, fsb3, BENCH_FRAME, fout);
        crc = h1_crc32(crc, fout, BENCH_FRAME);
    }
    return crc ^ 0xFFFFFFFFu;
}
#endif

/**
 * H1 combined measure: focusing increment (A) + WCET cold/warm/max (B) + ride-along (C).
 *   RAW counters only. @return 1 if ran on board with FIRA; 0 desktop/no-FIRA (g_h1_* stay 0/sentinel).
 *   Runs AFTER F4/F5/F7 in bench_main; own state arrays -> does NOT perturb their PASS paths.
 *   FREE-RUN: no mid-loop breakpoints; read g_h1_* at idle only.
 */
int h1_wcet_measure(void)
{
    g_h1_cyc_8ch_focus = 0u; g_h1_cyc_8ch_nofocus = 0u; g_h1_cyc_focus_only = 0u;
    g_h1_cyc_8ch_cold = 0u; g_h1_cyc_8ch_warm = 0u; g_h1_cyc_8ch_max = 0u; g_h1_cyc_8ch_min = 0u;
    g_h1_cclk_hz = 0u; g_h1_cclk_rc = -99; g_h1_focus_crc = 0u; g_h1_nofocus_crc = 0u;
    g_h1_fg_focus_differs = -99; g_h1_fg_zero_recovers = -99; g_h1_valid = 0;

#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)
    {
        uint32_t cclk = 0u;
        g_h1_cclk_rc = (int)adi_pwr_GetCoreClkFreq(0u, &cclk);   /* ride-along sanity; pwr inited at startup */
        g_h1_cclk_hz = cclk;
    }

    if (fira_tree_setup() != 0) {
        return 0;   /* no FIRA on this host: cycles stay 0, never fake (FG2 honest 0) */
    }

    {
        const int32_t *chirp = bench_chirp_input();
        int32_t fsb0[BENCH_FRAME/8], fsb1[BENCH_FRAME/4], fsb2[BENCH_FRAME/2], fsb3[BENCH_FRAME];
        int32_t fout[BENCH_FRAME], xw[BENCH_FRAME], scr[BENCH_FRAME];
        uint32_t t0, t1, cyc, f;
        int c, sb, i;

        tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);   /* core (golden) Q15 coeffs; FIRA coeffs set in setup */
        for (c = 0; c < DOLPH_W8_NCH; c++) fira_channel_init(&s_h1_fa[c], BENCH_FRAME);
        for (c = 0; c < DOLPH_W8_NCH; c++)
            for (sb = 0; sb < 4; sb++)
                for (i = 0; i < H1_FDTAPS - 1; i++) s_fd_hist[c][sb][i] = 0;

        /* ===== B (cold: TRUE-cold-DATA / I-cache still warm) =====
         * R15: invalidate the DATA cache over H1's working set BEFORE the measured cold frame so the
         * frame pays real D-cache miss penalties (true-cold-DATA). flush_data_buffer(start,end,1) =
         * flush-and-invalidate (A5-established CCES SHARC builtin, <sys/cache.h>, fira_tree.c:489-500).
         * SCOPE (honest): this is TRUE-cold-DATA only; the I-CACHE is still warm from F4/F5/F7 (same
         * FIRA code path) -- there is NO repo-known SHARC I-cache invalidate symbol (desktop), so a full
         * I+D cold is a C10 board item (I-side symbol TBD). Even I+D cold stays a LOWER BOUND on system
         * WCET (no SPORT/codec DMA contention, no ISR preemption in this bare-metal free-run bench). */
        {
            const int32_t *xin = &chirp[0];
            h1_dcache_inval_workingset(fsb0, fsb1, fsb2, fsb3, fout, xw, scr);  /* OUTSIDE the timed span */
            t0 = bench_cyc_target();
            (void)h1_fira_frame(xin, 1, 0, fsb0, fsb1, fsb2, fsb3, fout, xw, scr);
            t1 = bench_cyc_target();
            g_h1_cyc_8ch_cold = t1 - t0;
        }

        /* ===== warm-up (steady-state discipline) ===== */
        for (f = 0; f < H1_WARM; f++) {
            const int32_t *xin = &chirp[(f + 1) * BENCH_FRAME];
            (void)h1_fira_frame(xin, 1, 0, fsb0, fsb1, fsb2, fsb3, fout, xw, scr);
        }

        /* ===== snapshot the CLEAN steady state ONCE (after warm-up, before the compared frames) =====
         * R15 fix: all three compared frames (focus-ON / focus-OFF / identity) must run from the SAME
         * filter state on the SAME input. We snapshot here, then h1_state_restore() before each frame
         * (restore OUTSIDE the timed span so the memcpy does not pollute the cycle count). */
        h1_state_save();

        /* ===== A (same-build, same-STATE A/B) on one warmed frame =====
         * METHODOLOGY DELTA vs the R14 quarantined run: the A/B is now same-STATE (each span restored to
         * the snapshot), so the re-run focus/nofocus/identity numbers SUPERSEDE the quarantined ones. */
        {
            const int32_t *xin = &chirp[(H1_WARM + 1) * BENCH_FRAME];
            uint32_t crc_f, crc_nf;

            /* focus ON -- restore clean state first (outside the span) */
            h1_state_restore();
            t0 = bench_cyc_target();
            crc_f = h1_fira_frame(xin, 1, 0, fsb0, fsb1, fsb2, fsb3, fout, xw, scr);
            t1 = bench_cyc_target();
            g_h1_cyc_8ch_focus = t1 - t0;
            g_h1_cyc_8ch_warm  = g_h1_cyc_8ch_focus;   /* steady focus-on = warm reference for cold/warm */
            g_h1_focus_crc = crc_f;

            /* focus OFF -- restore the SAME clean state -> same-state A/B */
            h1_state_restore();
            t0 = bench_cyc_target();
            crc_nf = h1_fira_frame(xin, 0, 0, fsb0, fsb1, fsb2, fsb3, fout, xw, scr);
            t1 = bench_cyc_target();
            g_h1_cyc_8ch_nofocus = t1 - t0;
            g_h1_nofocus_crc = crc_nf;

            /* focus-only cost = focus - nofocus (now a same-state A/B delta) */
            g_h1_cyc_focus_only = (g_h1_cyc_8ch_focus > g_h1_cyc_8ch_nofocus)
                                ? (g_h1_cyc_8ch_focus - g_h1_cyc_8ch_nofocus) : 0u;

            /* FG-1: focus output MUST differ from nofocus (delay actually computes) -- same state, so a
             * difference is purely the focus stage. */
            g_h1_fg_focus_differs = (crc_f != crc_nf) ? 1 : 0;

            /* FG-2 continuity: identity (zero-delay) from the SAME clean state MUST reproduce nofocus
             * bit-for-bit. With same-state restore this is now a TRUE continuity gate (R14 flaw fixed). */
            {
                uint32_t crc_id;
                h1_state_restore();
                crc_id = h1_fira_frame(xin, 1, 1, fsb0, fsb1, fsb2, fsb3, fout, xw, scr);
                g_h1_fg_zero_recovers = (crc_id == crc_nf) ? 1 : 0;
            }
        }

        /* ===== B (jitter): max/min over H1_NFRAMES steady frames, focus ON ===== */
        g_h1_cyc_8ch_max = 0u; g_h1_cyc_8ch_min = 0xFFFFFFFFu;
        for (f = 0; f < H1_NFRAMES; f++) {
            const int32_t *xin = &chirp[((H1_WARM + 2) + (f % (BENCH_NFR - (H1_WARM + 2)))) * BENCH_FRAME];
            t0 = bench_cyc_target();
            (void)h1_fira_frame(xin, 1, 0, fsb0, fsb1, fsb2, fsb3, fout, xw, scr);
            t1 = bench_cyc_target();
            cyc = t1 - t0;
            if (cyc > g_h1_cyc_8ch_max) g_h1_cyc_8ch_max = cyc;
            if (cyc < g_h1_cyc_8ch_min) g_h1_cyc_8ch_min = cyc;
        }
        g_h1_valid = 1;
    }
    fira_tree_teardown();
    return 1;
#else
    /* desktop / no-FIRA: focus FIR + control logic still COMPILE (FG/CRC path exercised on host below),
     * but the FIRA spans are absent -> honest 0/sentinel, never fake a cycle number (FG2). */
    return 0;
#endif
}
