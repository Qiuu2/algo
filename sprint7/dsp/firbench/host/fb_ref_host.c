/*
 * fb_ref_host.c -- golden track 2 (plain C, independent of the numpy track and of s7_firbench.c).
 *
 * Recomputes every per-channel golden of fb_goldens.h from fb_coeffs.h + the frozen chirp as ONE whole-signal
 * convolution per channel (no framing, no history buffer -> it also cross-checks the bench's frame/ST1 logic):
 *     y_c[n] = sat32( (sum_{k<=n} c[k] * x[n-k]) >> 15 ),  n = 0..65535, int64 accumulate, arithmetic shift.
 * Then the FG2 proof in C: the placeholder sets (Dolph-20 table x delta[k-M]; uniform round(G/16*2^15) x delta[k-M],
 * M = (ntaps-1)/2) must MISS every golden. Also counts saturations (expect 0) and checks the tables' symmetry
 * (required by the folded core path and making the FIRA tap orientation moot).
 * Exit 0 iff: all 24 goldens reproduced, all 48 placeholder entries miss, 0 saturations, all tables symmetric.
 * [L2 host]. ASCII-only. Build: see run_firbench_host.sh.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "chirp_input.h"
#include "dolph_w8_q15.h"
#include "fb_coeffs.h"
#include "fb_goldens.h"

#define NS (64 * 1024)

static uint32_t crc32_buf(const int32_t *d, int n)          /* == bench_harness.c crc32_buf */
{
    uint32_t c = 0xFFFFFFFFu;
    int i, b, k;
    for (i = 0; i < n; i++) {
        uint32_t v = (uint32_t)d[i];
        for (b = 0; b < 4; b++) {
            c ^= (uint8_t)(v >> (8 * b));
            for (k = 0; k < 8; k++) c = (c & 1u) ? (c >> 1) ^ 0xEDB88320u : (c >> 1);
        }
    }
    return c ^ 0xFFFFFFFFu;
}

static int32_t y_buf[NS];
static long    n_sat;

static uint32_t run(const int32_t *c, int n)
{
    int i, k;
    for (i = 0; i < NS; i++) {
        int64_t acc = 0, v;
        int kmax = (i < n - 1) ? i : n - 1;
        for (k = 0; k <= kmax; k++) acc += (int64_t)c[k] * (int64_t)CHIRP_INPUT[i - k];
        v = acc >> 15;
        if (v > INT32_MAX) { v = INT32_MAX; n_sat++; }
        if (v < INT32_MIN) { v = INT32_MIN; n_sat++; }
        y_buf[i] = (int32_t)v;
    }
    return crc32_buf(y_buf, NS);
}

int main(void)
{
    static const int32_t *const tab[3] = { FB_COEF_T63, FB_COEF_T127, FB_COEF_T255 };
    static const int taps[3] = { FB_TAPS_0, FB_TAPS_1, FB_TAPS_2 };
    static int32_t ph[FB_MAXTAPS];
    int t, c, k, ok_gold = 0, miss = 0, asym = 0, uni;
    const double G = 12.885911890870;       /* printed in fb_coeffs.h; only used to rebuild the uniform placeholder */

    uni = (int)(G / 16.0 * 32768.0 + 0.5);
    printf("==== fb_ref_host: golden track 2 (C whole-signal convolution) + FG2 placeholder proof [L2 host] ====\n");
    printf("chirp CRC32 = 0x%08X (fb_coeffs.h FB_CHIRP_CRC 0x%08X)\n", (unsigned)crc32_buf(CHIRP_INPUT, NS),
           (unsigned)FB_CHIRP_CRC);
    for (t = 0; t < 3; t++) {
        const int n = taps[t], m = (n - 1) / 2;
        for (c = 0; c < 8; c++)
            for (k = 0; k < n; k++) if (tab[t][c * n + k] != tab[t][c * n + (n - 1 - k)]) asym++;
        printf("T%-3d golden:", n);
        for (c = 0; c < 8; c++) {
            uint32_t g = run(&tab[t][c * n], n);
            int hit = (g == FB_GOLDEN_CRC[t][c]);
            ok_gold += hit;
            printf(" %08X%s", (unsigned)g, hit ? "" : "(!)");
        }
        printf("\n");
        for (int kind = 0; kind < 2; kind++) {
            printf("T%-3d placeholder %-16s:", n, kind == 0 ? "dolph20_x_delta" : "uniform_x_delta");
            for (c = 0; c < 8; c++) {
                uint32_t g;
                memset(ph, 0, sizeof(ph));
                ph[m] = (kind == 0) ? g_dolph_w8_q15[c] : uni;
                g = run(ph, n);
                if (g != FB_GOLDEN_CRC[t][c]) miss++;
                printf(" %08X%s", (unsigned)g, g != FB_GOLDEN_CRC[t][c] ? "" : "(HIT!)");
            }
            printf("\n");
        }
    }
    printf("goldens reproduced %d/24 | placeholder entries missing their golden %d/48 | saturations %ld | "
           "asymmetric taps %d\n", ok_gold, miss, n_sat, asym);
    {
        int ok = (ok_gold == 24) && (miss == 48) && (n_sat == 0) && (asym == 0);
        printf("==== fb_ref_host verdict: %s ====\n", ok ? "PASS (track 2 == track 1; every placeholder FAILS)" : "FAIL");
        return ok ? 0 : 1;
    }
}
