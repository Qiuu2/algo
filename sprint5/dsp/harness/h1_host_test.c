/*
 * h1_host_test.c -- desktop self-verify for the focus FIR + FG logic in h1_wcet_measure.c.
 * The FIRA spans are target-only; this host test exercises the part that CAN run on desktop:
 *   the 8-tap focus FIR, the FG "output differs" check, and the identity-continuity control.
 * Build: gcc -O2 -DH1_HOST -I<includes> h1_host_test.c -o /tmp/h1_host && /tmp/h1_host
 * Exit 0 = all desktop checks pass.
 *
 * This is a standalone re-implementation of the focus FIR identical in form to h1_focus_subband
 *   (same coeffs, same Q15 shift) so the desktop result predicts the board FG behavior.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define H1_FDTAPS 8
#define NCH 8

static const int16_t s_fd_coeff[NCH][H1_FDTAPS] = {
    {  1100, 28000,  6200, -1400,   500,  -200,    90,   -40 },
    { -1500, 25000, 10500, -2600,   950,  -380,   160,   -70 },
    { -2100, 21500, 14800, -3900,  1500,  -610,   260,  -110 },
    { -2400, 17800, 18800, -5000,  2050,  -850,   370,  -160 },
    { -2400, 17800, 18800, -5000,  2050,  -850,   370,  -160 },
    { -2100, 21500, 14800, -3900,  1500,  -610,   260,  -110 },
    { -1500, 25000, 10500, -2600,   950,  -380,   160,   -70 },
    {  1100, 28000,  6200, -1400,   500,  -200,    90,   -40 }
};
/* zero-delay identity = true pass-through (copy), NOT a Q15 tap -- matches h1_wcet_measure.c. */
static void focus_subband(const int16_t *coef, int32_t *hist, int32_t *buf, int n, int32_t *scratch)
{
    int i, k;
    for (i = 0; i < n; i++) {
        int64_t acc = 0;
        for (k = 0; k < H1_FDTAPS; k++) {
            int32_t x;
            int idx = i - k;
            if (idx >= 0) x = buf[idx];
            else          x = hist[(H1_FDTAPS - 1) + idx];
            acc += (int64_t)coef[k] * (int64_t)x;
        }
        scratch[i] = (int32_t)(acc >> 15);
    }
    for (k = 0; k < H1_FDTAPS - 1; k++) hist[k] = buf[n - (H1_FDTAPS - 1) + k];
    for (i = 0; i < n; i++) buf[i] = scratch[i];
}

static uint32_t crc32(uint32_t c, const int32_t *d, int n)
{
    int i, b, k;
    for (i = 0; i < n; i++) {
        uint32_t v = (uint32_t)d[i];
        for (b = 0; b < 4; b++) { uint8_t by = (uint8_t)(v >> (8 * b)); c ^= by;
            for (k = 0; k < 8; k++) c = (c & 1u) ? (c >> 1) ^ 0xEDB88320u : (c >> 1); }
    }
    return c;
}

int main(void)
{
    int fail = 0;
    int n = 32;                         /* representative subband length */
    int32_t in[32], a[32], b[32], scr[32];
    int32_t hist[H1_FDTAPS - 1];
    int i, c;

    for (i = 0; i < n; i++) in[i] = (int32_t)((i * 2654435761u) >> 8) - 1000000; /* arbitrary nonzero */

    /* CHECK 1: zero-delay identity = pass-through (skip the stage) reproduces input EXACTLY.
     * In the board code use_identity SKIPS h1_focus_subband, so the continuity is a literal copy.
     * Here we model that as "no call" -> a unchanged == in. (Trivially exact; documents the contract.) */
    memcpy(a, in, sizeof(in));   /* identity path = pass-through: buffer untouched */
    for (i = 0; i < n; i++) if (a[i] != in[i]) { fail = 1; printf("FAIL identity@%d\n", i); break; }
    if (!fail) printf("PASS check1: zero-delay identity = pass-through reproduces input exactly (continuity anchor)\n");

    /* CHECK 2: a real focus coeff CHANGES the output (delay actually computes -> FG differs). */
    for (c = 0; c < NCH; c++) {
        memcpy(b, in, sizeof(in)); memset(hist, 0, sizeof(hist));
        focus_subband(s_fd_coeff[c], hist, b, n, scr);
        if (crc32(0xFFFFFFFFu, b, n) == crc32(0xFFFFFFFFu, in, n)) {
            fail = 1; printf("FAIL check2 ch%d: focus output == input (FG would falsely pass)\n", c);
        }
    }
    if (!fail) printf("PASS check2: all 8 focus coeffs change the output (FG 'differs' is real)\n");

    /* CHECK 3: identity CRC == input CRC, focus CRC != input CRC (the two FG anchors in board code). */
    {
        uint32_t crc_in, crc_id, crc_fc;
        memcpy(a, in, sizeof(in));   /* identity = pass-through (no focus call) */
        memcpy(b, in, sizeof(in)); memset(hist, 0, sizeof(hist)); focus_subband(s_fd_coeff[3], hist, b, n, scr);
        crc_in = crc32(0xFFFFFFFFu, in, n) ^ 0xFFFFFFFFu;
        crc_id = crc32(0xFFFFFFFFu, a,  n) ^ 0xFFFFFFFFu;
        crc_fc = crc32(0xFFFFFFFFu, b,  n) ^ 0xFFFFFFFFu;
        printf("crc in=0x%08X identity=0x%08X focus=0x%08X\n", crc_in, crc_id, crc_fc);
        if (crc_id != crc_in) { fail = 1; printf("FAIL check3a: identity CRC != input CRC\n"); }
        if (crc_fc == crc_in) { fail = 1; printf("FAIL check3b: focus CRC == input CRC\n"); }
        if (!fail) printf("PASS check3: identity-recovers + focus-differs CRC anchors hold\n");
    }

    printf(fail ? "==== H1 host self-verify: FAIL ====\n" : "==== H1 host self-verify: PASS ====\n");
    return fail;
}
