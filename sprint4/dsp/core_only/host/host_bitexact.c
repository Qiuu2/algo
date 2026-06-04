/**
 * @file    host_bitexact.c
 * @brief   core-only S0-S1 host bit-exact 预验 harness  [L2 host 预验]
 *
 * ⚠️ host 预验 ≠ 板上 bit-exact。本 harness 在 PC gcc 上跑，证明：
 *   (A) 同源系数：冻结 fir_coeffs_hb63.h 与 host live 重算 make_halfband 逐值一致；
 *       且断言 ntaps==63（CTO 盯点①，防 437-tap 误接）。
 *   (B) golden 权威 = host 重跑参考单通道链导出整数 y[]（走 tree_verify 同一路径），
 *       tree_io_*.csv 仅作参考（其 %.10e 字符串不作权威）（CTO 盯点②）。
 *   (C) 8ch 独立 bit-exact（F5-B）：8 路同信号、增益 1.0、8 条独立链 →
 *       每路 out[c] 与参考单通道链整数域逐位一致（容差 0, 8/8 路）。
 *       验删求和节点后核数值不变、每路独立链 == 单通道 golden（FG1 依赖滤波）。
 *   (D) 8ch 互等性（F5-B）：8 路同输入 → 8 个输出两两逐位一致（无跨通道串扰、
 *       等增益钩子=1.0）。删求和后不再有「8x 饱和」smoke, 改为独立性核对。
 *
 * 两套构建：
 *   sat   : gcc 默认（sat_i64_to_i32 / sat_add_i32 激活）
 *   unsat : gcc -DTFB_DISABLE_SAT（饱和退化为环绕窄化）
 *   两套都须 (A)(B)(C) PASS。
 *
 * 编译（sat）  : gcc -O2 -I include -I src -o host_bitexact_sat   host/host_bitexact.c src/tree_filterbank.c src/tfb_8ch.c -lm
 * 编译（unsat）: gcc -O2 -DTFB_DISABLE_SAT -I include -I src -o host_bitexact_unsat host/host_bitexact.c src/tree_filterbank.c src/tfb_8ch.c -lm
 */
#include "tree_filterbank.h"
#include "tfb_8ch.h"
#include "fir_coeffs_hb63.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define FS        48000
#define FRAME     64
#define N_FRAMES  1024
#define N_TOTAL   (FRAME*N_FRAMES)

#ifdef TFB_DISABLE_SAT
#define BUILD_TAG "unsat"
#define GOLDEN_CSV "../../../sprint3/dsp/tree_io_unsat.csv"
#else
#define BUILD_TAG "sat"
#define GOLDEN_CSV "../../../sprint3/dsp/tree_io_sat.csv"
#endif

/* ---- live make_halfband：与 tree_verify.c:40-60 逐字符同源（CTO 盯点①核对源） ---- */
static int16_t hb_q15_live[TFB_HB_TAPS];
static double  hb_f64_live[TFB_HB_TAPS];
static double i0_(double x) {
    double s = 1.0, t = 1.0; int k;
    double x2 = (x/2.0)*(x/2.0);
    for (k = 1; k <= 30; k++) { t *= x2/((double)k*k); s += t; if (t < 1e-18*s) break; }
    return s;
}
static void make_halfband_live(void) {
    int N = TFB_HB_TAPS, n;
    double beta = 6.0, M = (double)(N-1);
    double i0b = i0_(beta), sum = 0.0;
    for (n = 0; n < N; n++) {
        double m = (double)n - M/2.0;
        double sinc = (m == 0.0) ? 1.0 : sin(M_PI*0.5*m)/(M_PI*0.5*m);
        double r = (2.0*(double)n/M) - 1.0;
        double win = i0_(beta*sqrt(1.0 - r*r)) / i0b;
        hb_f64_live[n] = 0.5 * sinc * win;
        sum += hb_f64_live[n];
    }
    for (n = 0; n < N; n++) hb_f64_live[n] /= sum;
    for (n = 0; n < N; n++) {
        long q = lround(hb_f64_live[n] * 32768.0);
        if (q > 32767) q = 32767;
        if (q < -32768) q = -32768;
        hb_q15_live[n] = (int16_t)q;
    }
}

static int32_t to_q31(double v){ double s=v*2147483648.0; if(s>2147483647.0)s=2147483647.0; if(s<-2147483648.0)s=-2147483648.0; return (int32_t)s; }

/* chirp 激励：与 tree_verify.c:101-109 同口径（0.289 = -6dBFS + -4.8dB headroom） */
static void gen_chirp(int32_t *x, double *xf) {
    for (int i = 0; i < N_TOTAL; i++) {
        double t = (double)i/FS, T = (double)N_TOTAL/FS;
        double f0=20.0, f1=11000.0;
        double K = pow(f1/f0, t/T);
        double phase = 2.0*M_PI*f0*T/log(f1/f0)*(K-1.0);
        xf[i] = 0.289*sin(phase);
        x[i]  = to_q31(xf[i]);
    }
}

/* 静态大数组（避免栈溢出） */
static int32_t x[N_TOTAL];
static double  xf[N_TOTAL];
static int32_t y_ref[N_TOTAL];     /* 参考单通道链 golden（整数 Q31，权威） */
static int32_t in8[TFB8_NCH][TFB8_FRAME];
static int32_t out8[TFB8_NCH][TFB8_FRAME];   /* 8 路独立输出（F5-B 8-in-8-out） */

int main(void) {
    int rc_total = 0;   /* 累计失败计数；0 = 全 PASS */
    printf("==================================================================\n");
    printf(" host_bitexact harness  [build=%s]  [L2 host 预验]\n", BUILD_TAG);
    printf("==================================================================\n");

    /* ---------- (A) 同源系数核对 + ntaps==63 断言（CTO 盯点①） ---------- */
    printf("\n[A] 同源系数核对 (CTO 盯点①: 防 437-tap 误接)\n");
    int fail_A = 0;
    if (FIR_HB63_NTAPS != 63) { printf("  FAIL: FIR_HB63_NTAPS=%d != 63\n", FIR_HB63_NTAPS); fail_A++; }
    if (TFB_HB_TAPS != 63)    { printf("  FAIL: TFB_HB_TAPS=%d != 63\n", TFB_HB_TAPS); fail_A++; }
    make_halfband_live();
    int diffA = 0;
    for (int n = 0; n < TFB_HB_TAPS; n++) {
        if (g_hb63_q15[n] != hb_q15_live[n]) {
            if (diffA < 8) printf("  MISMATCH tap[%d]: frozen=%d live=%d\n", n, g_hb63_q15[n], hb_q15_live[n]);
            diffA++;
        }
    }
    if (diffA) { printf("  FAIL: 冻结头 vs live make_halfband 有 %d 个值不一致\n", diffA); fail_A++; }
    else       { printf("  PASS: 冻结 g_hb63_q15[63] 与 live make_halfband 逐值一致 (63/63)\n"); }
    printf("  断言: ntaps==63 -> %s ; 中心抽头 g_hb63_q15[31]=%d (期望 16385)\n",
           (FIR_HB63_NTAPS==63 && TFB_HB_TAPS==63) ? "OK" : "VIOLATED", g_hb63_q15[31]);
    /* 显式防 437：若误接 437-tap 核，ntaps 必不为 63 */
    printf("  [%s] (A) 同源系数\n", fail_A ? "FAIL" : "PASS");
    rc_total += fail_A;

    /* 喂冻结系数（核全局共享，8ch 无需各自喂） */
    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);

    /* ---------- 生成激励 ---------- */
    gen_chirp(x, xf);

    /* ---------- (B) golden = 参考单通道链重跑导出整数 y[]（CTO 盯点②） ---------- */
    printf("\n[B] golden 权威 = host 重跑参考单通道链导出整数 y[] (走 tree_verify 同一路径)\n");
    {
        TreeChannelState ana, syn;
        int32_t sb0[FRAME/8], sb1[FRAME/4], sb2[FRAME/2], sb3[FRAME];
        tfb_channel_init(&ana);
        tfb_channel_init(&syn);
        for (int f = 0; f < N_FRAMES; f++) {
            int32_t *xin = &x[f*FRAME];
            int32_t *yo  = &y_ref[f*FRAME];
            tfb_analyze(&ana, xin, FRAME, sb0, sb1, sb2, sb3);
            tfb_synthesize(&syn, sb0, sb1, sb2, sb3, FRAME, yo);
        }
        printf("  PASS: 参考链跑完 %d 帧 -> 整数 golden y_ref[%d] (Q31)\n", N_FRAMES, N_TOTAL);
        printf("  注: tree_io_%s.csv 仅作参考 (其 %%.10e 字符串非权威; 整数域比对)\n", BUILD_TAG);
    }

    /* ---------- (C) 8ch 独立 bit-exact vs 单通道 golden（容差 0, 8/8 路）---------- */
    printf("\n[C] 8ch 独立 bit-exact 预验 (F5-B: 8 路同信号, 增益 1.0, 8 条独立链)\n");
    {
        Tfb8State st;
        tfb8_init(&st);
        long diffC[TFB8_NCH]; int firstC[TFB8_NCH];
        for (int c = 0; c < TFB8_NCH; c++) { diffC[c] = 0; firstC[c] = -1; }
        for (int f = 0; f < N_FRAMES; f++) {
            /* 8 路同信号; 每路独立链 -> 每路应 == 参考单通道 golden */
            for (int i = 0; i < FRAME; i++)
                for (int c = 0; c < TFB8_NCH; c++) in8[c][i] = x[f*FRAME + i];
            tfb8_process(&st, in8, FRAME, out8);
            for (int c = 0; c < TFB8_NCH; c++)
                for (int i = 0; i < FRAME; i++) {
                    int gi = f*FRAME + i;
                    if (out8[c][i] != y_ref[gi]) { if (firstC[c] < 0) firstC[c] = gi; diffC[c]++; }
                }
        }
        long totC = 0; int firstBadCh = -1;
        for (int c = 0; c < TFB8_NCH; c++) { totC += diffC[c]; if (diffC[c] && firstBadCh < 0) firstBadCh = c; }
        if (totC == 0) {
            printf("  PASS: 8/8 路 out[c] == 参考单通道 golden, 逐位一致 (diff=0, 每路 %d samples)\n", N_TOTAL);
        } else {
            printf("  FAIL: 跨路总 diff=%ld; 首坏路 ch%d diffC=%ld first@%d out=%d ref=%d\n",
                   totC, firstBadCh, diffC[firstBadCh], firstC[firstBadCh],
                   out8[firstBadCh][firstC[firstBadCh]%FRAME], y_ref[firstC[firstBadCh]]);
            rc_total++;
        }
    }

    /* ---------- (D) 8ch 互等性（8 路同输入 -> 8 输出两两逐位一致）---------- */
    printf("\n[D] 8ch 互等性 (F5-B: 8 路同输入 -> 8 输出无串扰, 增益 1.0 全等)\n");
    {
        Tfb8State st;
        tfb8_init(&st);
        long diffD = 0; int firstD = -1; int firstCh = -1;
        for (int f = 0; f < N_FRAMES; f++) {
            for (int i = 0; i < FRAME; i++)
                for (int c = 0; c < TFB8_NCH; c++) in8[c][i] = x[f*FRAME + i];
            tfb8_process(&st, in8, FRAME, out8);
            /* 每帧: 路 1..7 应逐位 == 路 0（同输入+同增益+独立链, 零跨通道串扰） */
            for (int c = 1; c < TFB8_NCH; c++)
                for (int i = 0; i < FRAME; i++)
                    if (out8[c][i] != out8[0][i]) {
                        if (firstD < 0) { firstD = f*FRAME + i; firstCh = c; }
                        diffD++;
                    }
        }
        if (diffD == 0) {
            printf("  PASS: 8 路同输入 -> 8 输出两两逐位一致 (diff=0; 证独立链无串扰、等增益)\n");
        } else {
            printf("  FAIL: 互等 diff=%ld; first@ch%d sample%d (out[%d]!=out[0])\n",
                   diffD, firstCh, firstD, firstCh);
            rc_total++;
        }
    }

    /* ---------- 参考: tree_io_*.csv 对照（非权威, 仅信息） ---------- */
    printf("\n[ref] tree_io_%s.csv 对照 (仅参考, 非权威; 因 csv 经 guard 裁剪+延迟对齐)\n", BUILD_TAG);
    {
        FILE *fp = fopen(GOLDEN_CSV, "r");
        if (!fp) {
            printf("  (skip: 打不开 %s)\n", GOLDEN_CSV);
        } else {
            char line[256];
            long nrows = 0;
            if (fgets(line, sizeof(line), fp)) { /* header x,y */ }
            while (fgets(line, sizeof(line), fp)) nrows++;
            fclose(fp);
            printf("  csv 行数(数据)=%ld (供 Python 频谱/对照; 整数权威见 [B][C])\n", nrows);
        }
    }

    /* ---------- 总结 ---------- */
    printf("\n==================================================================\n");
    printf(" [%s] 总结: %s  (失败子项=%d)\n", BUILD_TAG, rc_total ? "FAIL" : "PASS", rc_total);
    printf("==================================================================\n");
    return rc_total ? 1 : 0;
}
