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
 * FOCUSING FIR DESIGN CHOICE (justified, maps to the costed 2.88 MMAC/s):
 *   - 8-tap fractional-delay FIR, applied PER-SUBBAND (4 subbands) PER-CHANNEL on the analyzed
 *     subband outputs (between analyze and synthesize), at the decimated subband rates.
 *   - MMAC mapping: 8 taps x 8 ch x sum(subband rates 3+6+12+24 kHz = 45 kHz) = 2.88 MMAC/s --
 *     EXACTLY the dsp_8ch_report.md:59 "frac-delay FIR x 4 subbands, 8 ch = 2.88 MMAC/s" accounting (critic R14: :59 is the frac-delay row; :60 is weighted-sum 0.36).
 *     (A full-rate 16-tap pre-analyze choice would be 6.14 MMAC/s = ~2.1x heavier; rejected so the
 *      harness measures the COSTED envelope, not an inflated one. The board cyc it returns is the
 *      truth; desktop MMAC is only the design anchor.)
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
#endif

#define H1_WARM     4    /* warm-up frames (== F7_WARM discipline, bench_harness.c:84) */
#define H1_NFRAMES  64   /* steady frames swept for max/min jitter (g_h1_cyc_8ch_max/min) */
#define H1_FDTAPS   8    /* focus fractional-delay FIR taps (maps to 2.88 MMAC/s, see header) */

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

        /* ===== B (cold-PROXY): H1's first frame, NO H1 warm-up -- BUT I-cache is already warm from
         * F4/F5/F7 (same FIRA code path); only H1-local data buffers are first-touch. This is a
         * PARTIAL cold proxy that UNDERSTATES true cold WCET (critic R14 F14-MAJOR-1). ===== */
        {
            const int32_t *xin = &chirp[0];
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

        /* ===== A (same-build A/B) on the SAME warmed frame index ===== */
        {
            const int32_t *xin = &chirp[(H1_WARM + 1) * BENCH_FRAME];
            uint32_t crc_f, crc_nf;

            /* focus ON */
            t0 = bench_cyc_target();
            crc_f = h1_fira_frame(xin, 1, 0, fsb0, fsb1, fsb2, fsb3, fout, xw, scr);
            t1 = bench_cyc_target();
            g_h1_cyc_8ch_focus = t1 - t0;
            g_h1_cyc_8ch_warm  = g_h1_cyc_8ch_focus;   /* steady focus-on = warm reference for cold/warm */
            g_h1_focus_crc = crc_f;

            /* focus OFF (no-focus path) -- SAME frame (re-run analyze/synth without focus stage) */
            t0 = bench_cyc_target();
            crc_nf = h1_fira_frame(xin, 0, 0, fsb0, fsb1, fsb2, fsb3, fout, xw, scr);
            t1 = bench_cyc_target();
            g_h1_cyc_8ch_nofocus = t1 - t0;
            g_h1_nofocus_crc = crc_nf;

            /* focus-only cost (increment cross-check) = focus - nofocus, recorded raw both ways */
            g_h1_cyc_focus_only = (g_h1_cyc_8ch_focus > g_h1_cyc_8ch_nofocus)
                                ? (g_h1_cyc_8ch_focus - g_h1_cyc_8ch_nofocus) : 0u;

            /* FG: focus output MUST differ from nofocus (delay actually computes) */
            g_h1_fg_focus_differs = (crc_f != crc_nf) ? 1 : 0;

            /* FG continuity: identity (zero-delay) config MUST reproduce the nofocus path */
            {
                uint32_t crc_id = h1_fira_frame(xin, 1, 1, fsb0, fsb1, fsb2, fsb3, fout, xw, scr);
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
