/*
 * s7_firbench.h -- S7 per-channel FIR compute bench (DEC-S7-SIDE30-01 (3)): readout declarations + entry point.
 * ASCII-only (CCES SHARC). Definitions live in s7_firbench.c. See README.md and
 * sprint7/docs/S7_FIRBENCH_RUNBOOK.md. RAW counters only: no margin / MCPS / ratio is computed on board (C9).
 *
 * Index conventions used by every [path][tapset][channel] readout:
 *   path   0 = FB_P_FIRA_T8  FIRA, 8 tasks per frame (1 channel each, CreateTask+FixedPointEnable+Queue+spin
 *                            per channel -- the fira_tree.c per-segment pattern)
 *          1 = FB_P_FIRA_T1  FIRA, 1 task per frame carrying all 8 channels (CreateTask+FixedPointEnable per frame)
 *          2 = FB_P_FIRA_P1  FIRA, 1 persistent 8-channel task created ONCE; per frame only QueueTask, circular
 *                            input buffer advanced by the hardware (ADI EE408 Direct_Replacement pattern)
 *          3 = FB_P_CORE_C   core, portable C direct form (int64 MAC)
 *          4 = FB_P_CORE_SYM core, portable C symmetric-folded form (bit-identical results, half the multiplies)
 *   tapset 0/1/2 = 63/127/255 real taps (tiers 64/128/256); tapset 1 = the V1-128 correctness set.
 */
#ifndef S7_FIRBENCH_H
#define S7_FIRBENCH_H
#include <stdint.h>

#define FB_NPATH       5
#define FB_P_FIRA_T8   0
#define FB_P_FIRA_T1   1
#define FB_P_FIRA_P1   2
#define FB_P_CORE_C    3
#define FB_P_CORE_SYM  4
#define FB_NTS         3          /* tap sets (== FB_NTAPSET in fb_coeffs.h) */
#define FB_NCHAN       8

#ifdef __cplusplus
extern "C" {
#endif

/* Run every path x tap set over the full frozen chirp (1024 frames), then the negative control.
 * Returns g_fb_valid (1 only on the board with the real FIRA header). FREE-RUN; read g_fb_* at idle only. */
int s7_firbench_run(void);

/* ---- identity / environment ---- */
extern volatile uint32_t g_fb_version;          /* source tag, README sec 0 */
extern volatile uint32_t g_fb_build_flags;      /* bit0 FIRA built, bit1 TARGET_SHARC, bit2 FIRBENCH_FLUSH_IN,
                                                   bit3 FIRBENCH_P1_FXD_EACH, bit4 host emulator */
extern volatile int      g_fb_valid;            /* 1 = board + real FIRA header (cycles meaningful) */
extern volatile int      g_fb_open_rc;          /* adi_fir_Open/RegisterCallback: 0 ok, 1/2 step code, -1 not built */
extern volatile int      g_fb_close_rc;         /* adi_fir_Close rc (0 ok), -1 not built */
extern volatile uint32_t g_fb_cclk_hz;          /* adi_pwr_GetCoreClkFreq readback (cross-check ONLY; the budget
                                                   uses the CGU register readback, DEC-S7-RULINGS-03) */
extern volatile int      g_fb_cclk_rc;
extern volatile uint32_t g_fb_ccnt_read_cyc;    /* cost of one back-to-back CCNT read pair */
extern volatile uint32_t g_fb_chirp_crc;        /* CRC32 of the chirp copy actually used */
extern volatile int      g_fb_chirp_ok;         /* == FB_CHIRP_CRC */
extern volatile uint32_t g_fb_coef_crc[FB_NTS]; /* CRC32 of the coefficient tables actually linked */
extern volatile int      g_fb_coef_ok[FB_NTS];  /* == FB_COEF_CRC_t */

/* ---- placement (runtime addresses of the key data; the PM decodes them against the memory segments of the
 *      same build's .map -> L1 block vs cacheable L2 decides how the cycles are labelled, runbook sec 7) ---- */
extern volatile uint32_t g_fb_addr_coef[FB_NTS];  /* FB_COEF_T63 / FB_COEF_T127 / FB_COEF_T255 */
extern volatile uint32_t g_fb_addr_lin;           /* s_fb_lin  : linear input  (T8 / T1 / CORE) */
extern volatile uint32_t g_fb_addr_circ;          /* s_fb_circ : circular input (P1) */
extern volatile uint32_t g_fb_addr_out3;          /* s_fb_out3 : FIRA 3-word output regions (8 x 200 words) */
extern volatile uint32_t g_fb_addr_y;             /* s_fb_y    : Q31 outputs (8 x 64 words) */

/* ---- per path x tap set ---- */
extern volatile int      g_fb_rc[FB_NPATH][FB_NTS];        /* 0 ok | 3 CreateTask 4 FixedPointEnable 5 QueueTask
                                                               7 spin timeout | -1 FIRA not built | -99 not run */
extern volatile int      g_fb_io1[FB_NPATH][FB_NTS];       /* FIRA: 1 = frame-0 output exactly filled (no sentinel
                                                               left in 64x3 words/ch) AND guard words intact; 0 = FAIL;
                                                               -2 = n/a (core paths) ; -99 not run */
extern volatile uint32_t g_fb_frames[FB_NPATH][FB_NTS];    /* frames in the stats (expect 1020 = 1024 - 4 warm-up) */
extern volatile uint32_t g_fb_cyc_last[FB_NPATH][FB_NTS];  /* per-frame wall cycles, 8 channels, last measured frame */
extern volatile uint32_t g_fb_cyc_max[FB_NPATH][FB_NTS];
extern volatile uint32_t g_fb_cyc_min[FB_NPATH][FB_NTS];
extern volatile uint32_t g_fb_crc[FB_NPATH][FB_NTS][FB_NCHAN];   /* per-channel output-stream CRC32 */
extern volatile int      g_fb_pass[FB_NPATH][FB_NTS][FB_NCHAN];  /* 1 = == FB_GOLDEN_CRC[t][c] */
extern volatile int      g_fb_pass_all[FB_NPATH][FB_NTS];        /* AND over 8 channels; -99 not run */
extern volatile int      g_fb_usable[FB_NPATH][FB_NTS];          /* 1 = cycles may be used: pass_all==1, rc==0,
                                                                     io1 in {1,-2}, chirp_ok, coef_ok[t] */

/* ---- negative control (placeholder Dolph-20 x delta[k-63], 127 taps, CORE_C path, same run) ---- */
extern volatile uint32_t g_fb_neg_crc[FB_NCHAN];
extern volatile int      g_fb_neg_fail_all;     /* 1 = placeholder MISSED all 8 goldens (expected); 0 = a hit (BLOCKER) */

#ifdef __cplusplus
}
#endif
#endif /* S7_FIRBENCH_H */
