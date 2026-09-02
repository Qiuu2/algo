/*
 * s7_wallclock_probe.h -- WO-S7-B6.3 bench-side wall-clock split probe (raw readouts + entry point).
 *
 * ASCII-only (CCES SHARC). NEW bench TU (sprint7/dsp/probe). Frozen files untouched:
 *   tree_filterbank.c/.h, tfb_8ch.c, fira_tree.c, dolph_w8_q15.h, fir_coeffs_hb63.h, fir_coeffs_q31.h,
 *   golden_ref.h, chirp_input.h, dolph_f5_goldens.h, sprint4 .ldf. fira_regression.c NOT edited.
 *
 * PURPOSE (DEC-S7-IMPL-01 item (1)b): split the bench F7 same-caliber wall-clock (fira_regression.c:611-619,
 *   8ch weight -> fira_tfb_analyze -> fira_tfb_synthesize, main context, FIRA busy-wait INSIDE) into THREE
 *   per-frame segments, each = the SUM over the 8 channels of ONE frame:
 *     w   = the input-scale Dolph weight multiply loop (f5_apply_w semantics, 64 samples) + loop increment
 *     ana = the fira_tfb_analyze call ONLY (3 DEC + 3 ana_int FIRA segments + core-side detail subtract)
 *     syn = the fira_tfb_synthesize call ONLY (3 syn_int FIRA segments + core-side sat_add)
 *   plus the OUTER per-frame bracket (beam = the whole 8-channel loop, == the F7 span caliber).
 *   Reads are CHAINED exactly like the board's M2_SEG_CYC brackets (m1_loopback_tdm.c m2_fira_beam_frame):
 *   one read opens w of c=0, then each segment's CLOSE read is the next segment's OPEN read, and the syn
 *   close of channel c is the w open of channel c+1. Per frame: 1 + 3 x 8 = 25 reads inside the beam bracket
 *   (+2 for the beam bracket itself = 27); the board has 1 + 4 x 8 = 33 (it has a 4th "tx" segment).
 *   All readouts are RAW cycle counts (bench_cyc_target() == clock() == CCLK cycles, CCNT_source.md).
 *   NO derived margin / MCPS / ratio is computed in code (C9 discipline): off-board only.
 *
 * ANTI-FALSE-GREEN (FG) -- what is and is NOT covered:
 *   FG-A (analyze): in the SAME run, the per-channel FIRA subband CRC (sb0|sb1|sb2|sb3 per frame, streaming
 *     over ALL BENCH_NFR frames from a zero-initialized state) MUST equal the frozen F5-A eight anchors
 *     g_f5_golden_crc[c] (dolph_f5_goldens.h). g_s7_fg_pass_all == 1 proves that the ANALYZE segment (the 6
 *     FIRA segments per channel that produce the subbands) timed the REAL FIRA chain; a stubbed / memset-0 /
 *     wrong-weight analyze fails every anchor. The CRC is updated OUTSIDE every timed bracket.
 *   FG-B (positive control, host + board): the CORE chain (tfb_analyze) over the same weighted chirp, through
 *     the SAME crc/weight/sequence code, must ALSO hit the 8 anchors (g_s7_core_selfcheck_all) -> the probe's
 *     FG machinery is same-source with gen_f5_goldens.c.
 *   SYNTHESIZE HAS NO ANCHOR (pre-existing project blind spot, shared with F7's 463,273: F4/F5 compare
 *     subbands only, F7 only times). The syn segment's evidence is FG2 (the desktop placeholder version FAILS
 *     the analyze anchors and can therefore not masquerade as a full run) and, with the diagnostic copy, the
 *     F4/F5 anchors still passing; a syn FIRA segment that fails/returns early would give a SHORT syn reading
 *     while FG-A stays green -> syn readings are one confidence grade below w/ana.
 *   FG-E (OPTIONAL syn-side control flag, build -DS7_PROBE_SYN_FG; whether it is mandatory = CTO ruling):
 *     outside every bracket, the SAME per-frame FIRA subbands are fed to the frozen CORE tfb_synthesize
 *     (per-channel TreeChannelState, lockstep history) and the two synth outputs are CRC-compared over all
 *     frames -> g_s7_syn_fg[c] / g_s7_syn_fg_all. Evaluated ONLY when g_s7_fg_pass_all == 1 (with placeholder
 *     subbands 0,0,0,in both synths trivially agree, so the flag would be meaningless -> -2). A mismatch is
 *     RECORDED and reported; it does not by itself invalidate w/ana (CTO/critic judge). Costs ~18 KB static
 *     (8 TreeChannelState) + core synth time OUTSIDE the brackets -> default OFF.
 *
 * Readout discipline: FREE-RUN, read g_s7_* at idle only (no breakpoint inside the measured loops --
 *   CCNT_source.md lesson: a breakpoint inside the FIRA spin loop deadlocks / pollutes the count).
 */
#ifndef ITC_S7_WALLCLOCK_PROBE_H
#define ITC_S7_WALLCLOCK_PROBE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---- run status ---- */
extern volatile int      g_s7_valid;            /* 1 = ran on board with real FIRA (cycles meaningful); 0 = desktop/no-FIRA */
extern volatile int      g_s7_host_forced;      /* 1 = desktop negative control (S7_PROBE_HOST_FORCE: setup gate bypassed) */
extern volatile int      g_s7_setup_rc;         /* fira_tree_setup() rc (0 = ok); -99 not-run; -1 = desktop no-FIRA */
extern volatile int      g_s7_fa_block1;        /* 1 = s_s7_fa pinned to seg_l1_block1 (S7_PROBE_FA_BLOCK1 build); 0 = default placement (F7-like) */
extern volatile uint32_t g_s7_frames;           /* frames that entered the last/max/min statistics (after warm-up) */
extern volatile uint32_t g_s7_frames_total;     /* frames run through the chain (== BENCH_NFR when complete) */
extern volatile uint32_t g_s7_cclk_hz;          /* [L1-to-be] adi_pwr_GetCoreClkFreq (Hz); 0 = not read / desktop */
extern volatile int      g_s7_cclk_rc;          /* rc of that read (0 = SUCCESS); -99 not-run/desktop */
extern volatile uint32_t g_s7_ccnt_read_cyc;    /* cost of ONE bench_cyc_target() read pair back-to-back (bracket perturbation unit) */
extern volatile uint32_t g_s7_reads_per_frame;  /* CCNT reads issued per frame INSIDE the beam bracket (25 chained) -- for the deduction */

/* ---- per-frame wall-clock: sum over 8 channels of one frame; last / max / min over measured frames ----
 *      chained reads: each segment reading carries the cost of ONE read (its close); w of c>0 also carries the
 *      loop increment (same as the board's w, which starts at the previous channel's tx close). */
extern volatile uint32_t g_s7_seg_w_cyc_last,   g_s7_seg_w_cyc_max,   g_s7_seg_w_cyc_min;    /* weight loop (+loop increment) */
extern volatile uint32_t g_s7_seg_ana_cyc_last, g_s7_seg_ana_cyc_max, g_s7_seg_ana_cyc_min;  /* fira_tfb_analyze */
extern volatile uint32_t g_s7_seg_syn_cyc_last, g_s7_seg_syn_cyc_max, g_s7_seg_syn_cyc_min;  /* fira_tfb_synthesize */
extern volatile uint32_t g_s7_beam_cyc_last,    g_s7_beam_cyc_max,    g_s7_beam_cyc_min;     /* outer 8ch loop (F7 caliber) */
extern volatile uint32_t g_s7_seg_sum_last;     /* w+ana+syn of the LAST measured frame (same frame as g_s7_beam_cyc_last) */
extern volatile uint32_t g_s7_probe_ovh_last;   /* beam - sum of the LAST frame = the first (chain-open) read + loop entry/exit ~ 1-2 reads */

/* ---- FG-A: FIRA-path per-channel ANALYZE subband CRC vs the 8 frozen anchors (dolph_f5_goldens.h) ---- */
extern volatile uint32_t g_s7_crc_fira[8];      /* live FIRA subband CRC per channel (all frames, sb0|sb1|sb2|sb3) */
extern volatile int      g_s7_fg_anchor_pass[8];/* 1 = g_s7_crc_fira[c] == g_f5_golden_crc[c]; 0 = FAIL */
extern volatile int      g_s7_fg_pass_all;      /* AND over 8 channels; -99 not-run; 0 = FAIL (cycles NOT trustworthy) */
/* FG-B positive control: the CORE chain (tfb_analyze) over the same weighted chirp must ALSO hit the anchors */
extern volatile uint32_t g_s7_crc_core[8];
extern volatile int      g_s7_core_anchor_pass[8];
extern volatile int      g_s7_core_selfcheck_all; /* 1 = CRC/weight/sequence machinery same-source with gen_f5_goldens.c */

/* ---- FG-E: OPTIONAL syn-side control (S7_PROBE_SYN_FG build). Not an anchor: a lockstep core-vs-FIRA compare. ---- */
extern volatile int      g_s7_syn_fg_built;     /* 1 = compiled with S7_PROBE_SYN_FG; 0 = not built (syn_fg fields stay -99) */
extern volatile uint32_t g_s7_syn_crc_fira[8];  /* CRC over all frames of the FIRA synthesize output, per channel */
extern volatile uint32_t g_s7_syn_crc_core[8];  /* CRC over all frames of the CORE tfb_synthesize output on the SAME subbands */
extern volatile int      g_s7_syn_fg[8];        /* 1 = equal; 0 = differ (record + report); -99 not built/not run; -2 not evaluated (FG-A failed) */
extern volatile int      g_s7_syn_fg_all;       /* AND over channels with the same coding */

/* ---- OPTIONAL inner split (only when the diagnostic copy fira_tree_probe.c is linked with -DS7_PROBE_INNER
 *      INSTEAD OF the frozen fira_tree.c; see README). Per frame = sum over 8 ch x 9 segments. ---- */
extern volatile int      g_s7_inner_valid;      /* 1 = inner counters came from the S7_PROBE_INNER copy; 0 = not linked (all 0) */
extern volatile uint32_t g_s7_in_task_cyc_last,  g_s7_in_task_cyc_max,  g_s7_in_task_cyc_min;  /* CreateTask+FixedPointEnable+QueueTask */
extern volatile uint32_t g_s7_in_spin_cyc_last,  g_s7_in_spin_cyc_max,  g_s7_in_spin_cyc_min;  /* QueueTask return -> DONE seen (busy-wait) */
extern volatile uint32_t g_s7_in_flush_cyc_last, g_s7_in_flush_cyc_max, g_s7_in_flush_cyc_min; /* flush_data_buffer (cache invalidate) */
extern volatile uint32_t g_s7_in_post_cyc_last,  g_s7_in_post_cyc_max,  g_s7_in_post_cyc_min;  /* fira_postscale (80-bit -> Q31, sw decimate) */
extern volatile uint32_t g_s7_in_mem_cyc_last,   g_s7_in_mem_cyc_max,   g_s7_in_mem_cyc_min;   /* history prepend / zero-stuff / hist update */
extern volatile uint32_t g_s7_in_core_cyc_last,  g_s7_in_core_cyc_max,  g_s7_in_core_cyc_min;  /* core-side detail subtract / sat_add loops */
extern volatile uint32_t g_s7_in_reads_last;    /* inner CCNT reads per frame (perturbation = reads x g_s7_ccnt_read_cyc) */

/* ---- inner counters as DEFINED by the S7_PROBE_INNER copy (accumulators; the probe resets them per frame) ---- */
#ifdef S7_PROBE_INNER
extern volatile uint32_t g_s7_in_task_cyc, g_s7_in_spin_cyc, g_s7_in_flush_cyc, g_s7_in_post_cyc,
                         g_s7_in_mem_cyc, g_s7_in_core_cyc, g_s7_in_reads;
#endif

/**
 * Run the probe. Sequence (== F5/F7/M2 call sequence): fira_tree_setup -> tfb_set_coeffs -> fira_channel_init x8,
 *   then for EVERY frame f of the frozen chirp, for each channel c: weight (f5_apply_w semantics) ->
 *   fira_tfb_analyze -> fira_tfb_synthesize, with the three chained segment brackets + the outer beam bracket.
 *   The first S7_WARM frames are RUN (they are part of the CRC stream) but EXCLUDED from last/max/min.
 * @return 1 = ran on board with FIRA (g_s7_valid=1); 0 = desktop / no FIRA (cycles stay 0, FG stays FAIL: FG2 honest 0).
 */
int s7_wallclock_probe(void);

#ifdef __cplusplus
}
#endif
#endif /* ITC_S7_WALLCLOCK_PROBE_H */
