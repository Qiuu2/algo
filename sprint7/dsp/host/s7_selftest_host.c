/*
 * s7_selftest_host.c -- WO-S7-B6 host harness for the M2_SELFTEST eight-anchor self-test kernel
 *   (DEC-S7-RULINGS-01 D3 / DEC-S7-IMPL-01 item 2; S7_VERIFICATION_PLAN.md sec 6 B6-4; fw audit 9.C/9.H).
 *
 * WHAT IT PROVES ON THE HOST [L2 desktop] -- before the tester's CCES build ever runs the board twin:
 *   The self-test kernel (input-scale Q15 weight -> analyze -> streaming subband CRC32 sb0|sb1|sb2|sb3 ->
 *   compare with the frozen F5 eight anchors) is CORRECT and SENSITIVE:
 *     pos          Dolph weights, device = frozen core tfb_analyze        -> 8/8 PASS, crc[c] == g_f5_golden_crc[c]
 *     neg-unity    unity weight on every channel (FG1 double-guard)      -> all 8 crc collapse to 0x2E0D8C6E, ONLY c=7
 *                                                                          passes, rc = 7   (== board -DM2_SELFTEST_NEGCTRL=1)
 *     neg-reverse  weight order reversed (w[7-c] on channel c)            -> 0/8 PASS, and crc[c] == golden[7-c] (index-sensitive)
 *     neg-chmap    weights permuted by the rig chmap {4,5,6,7,0,1,2,3}     -> 0/8 PASS (why the board self-test must NOT apply chmap)
 *     neg-stub     device = zero-fill placeholder (FG2)                   -> 0/8 PASS, mismatch_sb != -1 on every channel
 *     neg-sb2flip  device = core with sb2[0] ^= 1 at frame 100            -> 0/8 PASS, mismatch_sb == 2, mismatch_idx == 3200
 *   (the last two prove the mismatch localizer plumbing, not just the CRC).
 *
 * SAME-SOURCE DISCIPLINE: the kernel below is the TWIN of m2_selftest_run() in
 *   sprint6/dsp/audio/m1_cces_project/src/m1_loopback_tdm.c -- same weight expression
 *   ((int64_t)w * x) >> DOLPH_W8_QBITS, same analyze call shape, same CRC (fira_regression.c:71-81 ==
 *   gen_f5_goldens.c:54-64 verbatim), same sb0|sb1|sb2|sb3 streaming order, same F5 three-term PASS
 *   (fira_regression.c:369-371). The board substitutes fira_tfb_analyze(&s_m2_fa[c], ...) for the
 *   device function pointer; nothing else differs. If either side is edited, edit both.
 *
 * Build/run: sprint7/dsp/host/run_s7_host_checks.sh (gcc; links the FROZEN tree_filterbank.c read-only).
 * Frozen inputs (read-only, never regenerated here): chirp_input.h, dolph_w8_q15.h, dolph_f5_goldens.h,
 *   fir_coeffs_hb63.h, tree_filterbank.{c,h}.
 * ASCII-only. C99 (host only; the board twin is C89-style per R16).
 */
#include "tree_filterbank.h"
#include "fir_coeffs_hb63.h"     /* g_hb63_q15 / FIR_HB63_NTAPS */
#include "chirp_input.h"         /* CHIRP_INPUT[CHIRP_INPUT_N] (frozen R14 excitation, full-Q31) */
#include "dolph_w8_q15.h"        /* g_dolph_w8_q15[8] / DOLPH_W8_NCH / DOLPH_W8_QBITS / DOLPH_W8_ONE */
#include "dolph_f5_goldens.h"    /* g_f5_golden_crc[8] (the eight anchors) */
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define S7_FRAME  64u
#define S7_NFR    ((uint32_t)CHIRP_INPUT_N / S7_FRAME)   /* 1024 */

/* ---- device abstraction: the "thing under test" (FIRA on board, core or a corrupted core here) ---- */
typedef void (*s7_dev_init_fn)(void *st, uint16_t frame);
typedef void (*s7_dev_analyze_fn)(void *st, const int32_t *in, uint16_t frame,
                                  int32_t *sb0, int32_t *sb1, int32_t *sb2, int32_t *sb3);

typedef struct {
    int      rc;                        /* 0 all PASS; n = failing channels (board: -99 not run / -1 FIRA not ready) */
    int      pass[DOLPH_W8_NCH];
    uint32_t crc[DOLPH_W8_NCH];         /* device-path subband CRC */
    uint32_t crc_core[DOLPH_W8_NCH];    /* frozen-core subband CRC over the same weighted chirp */
    int      mismatch_sb[DOLPH_W8_NCH];
    int      mismatch_idx[DOLPH_W8_NCH];
    uint32_t frames;
} S7SelftestResult;

/* Incremental CRC32 (IEEE 802.3, poly 0xEDB88320 reflected, init 0xFFFFFFFF, final ^0xFFFFFFFF), int32 as 4 LE bytes.
 * VERBATIM: fira_regression.c:71-81 == gen_f5_goldens.c:54-64 == m1_loopback_tdm.c m2_st_crc32_update. */
static void s7_crc32_update(uint32_t *c, const int32_t *d, int n)
{
    for (int i = 0; i < n; i++) {
        uint32_t v = (uint32_t)d[i];
        for (int b = 0; b < 4; b++) {
            uint8_t by = (uint8_t)(v >> (8 * b));
            *c ^= by;
            for (int k = 0; k < 8; k++) *c = (*c & 1u) ? (*c >> 1) ^ 0xEDB88320u : (*c >> 1);
        }
    }
}

/* ---- THE KERNEL (twin of m2_selftest_run) ---- */
static int s7_selftest_kernel(const int32_t *w_q15, void *dev_states, size_t dev_stride,
                              s7_dev_init_fn dinit, s7_dev_analyze_fn dana, S7SelftestResult *r)
{
    static int32_t xw[S7_FRAME];
    static int32_t fsb0[S7_FRAME / 8], fsb1[S7_FRAME / 4], fsb2[S7_FRAME / 2], fsb3[S7_FRAME];
    static int32_t csb0[S7_FRAME / 8], csb1[S7_FRAME / 4], csb2[S7_FRAME / 2], csb3[S7_FRAME];
    static TreeChannelState core;
    const int sz[4] = { S7_FRAME / 8, S7_FRAME / 4, S7_FRAME / 2, S7_FRAME };
    const int32_t *fb[4] = { fsb0, fsb1, fsb2, fsb3 };
    const int32_t *cb[4] = { csb0, csb1, csb2, csb3 };
    int nfail = 0;

    memset(r, 0, sizeof(*r));
    r->frames = 0u;
    for (uint32_t c = 0u; c < (uint32_t)DOLPH_W8_NCH; c++) {
        const int32_t w = w_q15[c];                 /* weight index == channel index (NO chmap) -- anchor definition */
        uint32_t cf = 0xFFFFFFFFu, cc = 0xFFFFFFFFu;
        int mis = -1;
        void *dst = (char *)dev_states + c * dev_stride;
        r->mismatch_sb[c] = -1; r->mismatch_idx[c] = -1;

        dinit(dst, (uint16_t)S7_FRAME);
        tfb_channel_init(&core);
        for (uint32_t f = 0u; f < S7_NFR; f++) {
            const int32_t *xin = &CHIRP_INPUT[f * S7_FRAME];
            for (uint32_t i = 0u; i < S7_FRAME; i++)
                xw[i] = (int32_t)(((int64_t)w * (int64_t)xin[i]) >> DOLPH_W8_QBITS);   /* F5 apply_w, bit-exact */
            dana(dst, xw, (uint16_t)S7_FRAME, fsb0, fsb1, fsb2, fsb3);                 /* device under test */
            tfb_analyze(&core, xw, (uint16_t)S7_FRAME, csb0, csb1, csb2, csb3);        /* frozen-core reference */
            for (int b = 0; b < 4; b++) {
                if (mis < 0) {
                    for (int j = 0; j < sz[b]; j++) {
                        if (fb[b][j] != cb[b][j]) {
                            r->mismatch_sb[c] = b; r->mismatch_idx[c] = (int)(f * (uint32_t)sz[b]) + j;
                            mis = r->mismatch_idx[c]; break;
                        }
                    }
                }
                s7_crc32_update(&cf, fb[b], sz[b]);   /* sb0|sb1|sb2|sb3, every frame */
                s7_crc32_update(&cc, cb[b], sz[b]);
            }
            r->frames++;
        }
        r->crc[c] = cf ^ 0xFFFFFFFFu;
        r->crc_core[c] = cc ^ 0xFFFFFFFFu;
        r->pass[c] = ((mis < 0) && (r->crc[c] == r->crc_core[c]) && (r->crc_core[c] == g_f5_golden_crc[c])) ? 1 : 0;
        if (!r->pass[c]) nfail++;
    }
    r->rc = nfail;
    return nfail;
}

/* ---- host devices ---- */
static void dev_core_init(void *st, uint16_t frame) { (void)frame; tfb_channel_init((TreeChannelState *)st); }
static void dev_core_analyze(void *st, const int32_t *in, uint16_t frame, int32_t *s0, int32_t *s1, int32_t *s2, int32_t *s3)
{ tfb_analyze((TreeChannelState *)st, in, frame, s0, s1, s2, s3); }

/* FG2 placeholder: what a linked-but-stubbed accelerator produces (fira_tree.c #else path zero-fills) */
static void dev_stub_init(void *st, uint16_t frame) { (void)st; (void)frame; }
static void dev_stub_analyze(void *st, const int32_t *in, uint16_t frame, int32_t *s0, int32_t *s1, int32_t *s2, int32_t *s3)
{ (void)st; (void)in; memset(s0, 0, (frame / 8) * sizeof(int32_t)); memset(s1, 0, (frame / 4) * sizeof(int32_t));
  memset(s2, 0, (frame / 2) * sizeof(int32_t)); memset(s3, 0, frame * sizeof(int32_t)); }

/* localizer probe: core, but one LSB flipped in sb2[0] at frame 100 -> mismatch_sb must read 2, idx 100*32+0 */
typedef struct { TreeChannelState st; uint32_t f; } DevFlip;
static void dev_flip_init(void *st, uint16_t frame) { (void)frame; DevFlip *d = (DevFlip *)st; tfb_channel_init(&d->st); d->f = 0u; }
static void dev_flip_analyze(void *st, const int32_t *in, uint16_t frame, int32_t *s0, int32_t *s1, int32_t *s2, int32_t *s3)
{ DevFlip *d = (DevFlip *)st; tfb_analyze(&d->st, in, frame, s0, s1, s2, s3); if (d->f == 100u) s2[0] ^= 1; d->f++; }

static TreeChannelState s_dev_core[DOLPH_W8_NCH];
static DevFlip          s_dev_flip[DOLPH_W8_NCH];

static void print_result(const char *mode, const int32_t *w, const S7SelftestResult *r)
{
    printf("MODE %-12s frames=%u rc=%d\n", mode, r->frames, r->rc);
    printf("  c  w_q15  crc_dev    crc_core   golden     pass mis_sb mis_idx\n");
    for (int c = 0; c < DOLPH_W8_NCH; c++)
        printf("  %d  %5d  0x%08X 0x%08X 0x%08X  %d    %2d   %d\n", c, w[c], r->crc[c], r->crc_core[c],
               g_f5_golden_crc[c], r->pass[c], r->mismatch_sb[c], r->mismatch_idx[c]);
}

static int verdict(const char *mode, int ok, const char *expect)
{
    printf("  EXPECT: %s\n  VERDICT %s: %s\n\n", expect, mode, ok ? "PASS" : "FAIL");
    return ok ? 0 : 1;
}

int main(int argc, char **argv)
{
    const char *mode = (argc > 1) ? argv[1] : "all";
    int fails = 0;
    S7SelftestResult r;
    int32_t w[DOLPH_W8_NCH];
    int run_all = (strcmp(mode, "all") == 0);

    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);    /* core golden Q15 halfband coeffs, same as m2_fira_setup */

    if (run_all || !strcmp(mode, "pos")) {
        for (int c = 0; c < DOLPH_W8_NCH; c++) w[c] = g_dolph_w8_q15[c];
        s7_selftest_kernel(w, s_dev_core, sizeof(s_dev_core[0]), dev_core_init, dev_core_analyze, &r);
        print_result("pos", w, &r);
        int ok = (r.rc == 0) && (r.frames == 8u * S7_NFR);
        for (int c = 0; c < DOLPH_W8_NCH; c++) ok = ok && r.pass[c] && (r.crc[c] == g_f5_golden_crc[c]) && (r.mismatch_sb[c] == -1);
        fails += verdict("pos", ok, "rc=0, 8/8 PASS, crc_dev[c] == g_f5_golden_crc[c], frames=8192, no mismatch");
    }
    if (run_all || !strcmp(mode, "neg-unity")) {
        for (int c = 0; c < DOLPH_W8_NCH; c++) w[c] = DOLPH_W8_ONE;
        s7_selftest_kernel(w, s_dev_core, sizeof(s_dev_core[0]), dev_core_init, dev_core_analyze, &r);
        print_result("neg-unity", w, &r);
        int ok = (r.rc == 7);
        for (int c = 0; c < DOLPH_W8_NCH; c++) ok = ok && (r.crc[c] == 0x2E0D8C6Eu) && (r.pass[c] == (c == 7));
        fails += verdict("neg-unity", ok, "rc=7, all crc == 0x2E0D8C6E (F4 unity anchor), ONLY c=7 PASS (== board M2_SELFTEST_NEGCTRL expectation)");
    }
    if (run_all || !strcmp(mode, "neg-reverse")) {
        for (int c = 0; c < DOLPH_W8_NCH; c++) w[c] = g_dolph_w8_q15[DOLPH_W8_NCH - 1 - c];
        s7_selftest_kernel(w, s_dev_core, sizeof(s_dev_core[0]), dev_core_init, dev_core_analyze, &r);
        print_result("neg-reverse", w, &r);
        int ok = (r.rc == 8);
        for (int c = 0; c < DOLPH_W8_NCH; c++) ok = ok && !r.pass[c] && (r.crc[c] == g_f5_golden_crc[DOLPH_W8_NCH - 1 - c]);
        fails += verdict("neg-reverse", ok, "rc=8 (0/8 PASS) and crc_dev[c] == golden[7-c] (the check is weight-INDEX sensitive)");
    }
    if (run_all || !strcmp(mode, "neg-chmap")) {
        static const int perm[DOLPH_W8_NCH] = { 4, 5, 6, 7, 0, 1, 2, 3 };   /* s_m2_chmap default (rig-specific) */
        for (int c = 0; c < DOLPH_W8_NCH; c++) w[c] = g_dolph_w8_q15[perm[c]];
        s7_selftest_kernel(w, s_dev_core, sizeof(s_dev_core[0]), dev_core_init, dev_core_analyze, &r);
        print_result("neg-chmap", w, &r);
        int ok = (r.rc == 8);
        for (int c = 0; c < DOLPH_W8_NCH; c++) ok = ok && !r.pass[c] && (r.crc[c] == g_f5_golden_crc[perm[c]]);
        fails += verdict("neg-chmap", ok, "rc=8 (0/8 PASS): applying the chmap permutation inside the self-test would FAIL for a mapping reason, not a chain reason");
    }
    if (run_all || !strcmp(mode, "neg-stub")) {
        for (int c = 0; c < DOLPH_W8_NCH; c++) w[c] = g_dolph_w8_q15[c];
        s7_selftest_kernel(w, s_dev_core, sizeof(s_dev_core[0]), dev_stub_init, dev_stub_analyze, &r);
        print_result("neg-stub", w, &r);
        int ok = (r.rc == 8);
        for (int c = 0; c < DOLPH_W8_NCH; c++) ok = ok && !r.pass[c] && (r.mismatch_sb[c] != -1) && (r.crc[c] != g_f5_golden_crc[c]) && (r.crc_core[c] == g_f5_golden_crc[c]);
        fails += verdict("neg-stub", ok, "rc=8, zero-fill placeholder device FAILS every channel with a localized mismatch while crc_core still == golden (FG2)");
    }
    if (run_all || !strcmp(mode, "neg-sb2flip")) {
        for (int c = 0; c < DOLPH_W8_NCH; c++) w[c] = g_dolph_w8_q15[c];
        s7_selftest_kernel(w, s_dev_flip, sizeof(s_dev_flip[0]), dev_flip_init, dev_flip_analyze, &r);
        print_result("neg-sb2flip", w, &r);
        int ok = (r.rc == 8);
        for (int c = 0; c < DOLPH_W8_NCH; c++) ok = ok && !r.pass[c] && (r.mismatch_sb[c] == 2) && (r.mismatch_idx[c] == 100 * 32) && (r.crc[c] != r.crc_core[c]) && (r.crc_core[c] == g_f5_golden_crc[c]);
        fails += verdict("neg-sb2flip", ok, "rc=8, one LSB flipped in sb2[0] of frame 100 -> mismatch_sb=2, mismatch_idx=3200 on every channel (localizer plumbing)");
    }
    printf("S7_SELFTEST_HOST %s: %s (%d mode(s) failed)\n", mode, fails ? "FAIL" : "PASS", fails);
    return fails ? 1 : 0;
}
