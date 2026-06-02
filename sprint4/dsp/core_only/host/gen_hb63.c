/**
 * @file    gen_hb63.c
 * @brief   冻结 63-tap 同源 Q15 半带系数头生成器（一次性）
 *
 * CTO 盯点①（同源防 437-tap 误接）：本生成器的 make_halfband() 与
 * sprint3/dsp/tree_verify.c:40-60 逐字符同源（kaiser β=6 / cutoff fs/4 /
 * DC 归一 / lround(h*32768) 钳位）。运行本程序导出 fir_coeffs_hb63.h。
 * harness 上电再 live 重算并逐值核对（不一致即 FAIL），杜绝 fir_coeffs.h(437) 误接。
 *
 * 编译：gcc -O2 -o gen_hb63 host/gen_hb63.c -lm
 * 运行：./gen_hb63 > include/fir_coeffs_hb63.h
 */
#include <stdio.h>
#include <math.h>
#include <stdint.h>

#define TFB_HB_TAPS 63

static double i0(double x) {
    double s = 1.0, t = 1.0; int k;
    double x2 = (x/2.0)*(x/2.0);
    for (k = 1; k <= 30; k++) { t *= x2/((double)k*k); s += t; if (t < 1e-18*s) break; }
    return s;
}

/* 与 tree_verify.c:40-60 逐字符同源 */
static int16_t hb_q15[TFB_HB_TAPS];
static double  hb_f64[TFB_HB_TAPS];
static void make_halfband(void) {
    int N = TFB_HB_TAPS, n;
    double beta = 6.0, M = (double)(N-1);
    double i0b = i0(beta), sum = 0.0;
    for (n = 0; n < N; n++) {
        double m = (double)n - M/2.0;
        double sinc = (m == 0.0) ? 1.0 : sin(M_PI*0.5*m)/(M_PI*0.5*m);
        double r = (2.0*(double)n/M) - 1.0;
        double win = i0(beta*sqrt(1.0 - r*r)) / i0b;
        hb_f64[n] = 0.5 * sinc * win;
        sum += hb_f64[n];
    }
    for (n = 0; n < N; n++) hb_f64[n] /= sum;
    for (n = 0; n < N; n++) {
        long q = lround(hb_f64[n] * 32768.0);
        if (q > 32767) { q = 32767; }
        if (q < -32768) { q = -32768; }
        hb_q15[n] = (int16_t)q;
    }
}

int main(void) {
    int n, nz = 0;
    make_halfband();
    for (n = 0; n < TFB_HB_TAPS; n++) if (hb_q15[n] != 0) nz++;
    printf("/**\n");
    printf(" * @file    fir_coeffs_hb63.h\n");
    printf(" * @brief   冻结 63-tap 同源 Q15 半带原型系数（自动生成，勿手改）\n");
    printf(" *\n");
    printf(" * 来源：tree_verify.c:40-60 make_halfband()（kaiser beta=6, cutoff fs/4,\n");
    printf(" *       DC 归一, lround(h*32768) 钳位）— 与桌面 golden 同源。\n");
    printf(" * 生成器：sprint4/dsp/core_only/host/gen_hb63.c（make_halfband 逐字符同源）\n");
    printf(" * 用法：tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);\n");
    printf(" *\n");
    printf(" * CTO 盯点①：严禁用 sprint2/dsp/fir_coeffs.h(437-tap 废核)。harness 上电\n");
    printf(" *            live 重算 make_halfband 并逐值核对本表，不一致即 FAIL。\n");
    printf(" */\n");
    printf("#ifndef ITC_FIR_COEFFS_HB63_H\n");
    printf("#define ITC_FIR_COEFFS_HB63_H\n\n");
    printf("#include <stdint.h>\n\n");
    printf("#define FIR_HB63_NTAPS 63   /* 必须 == TFB_HB_TAPS；harness 断言 */\n");
    printf("#define FIR_HB63_NNZ   %d   /* 非零系数（含中心），半带跳零优化用 */\n\n", nz);
    printf("static const int16_t g_hb63_q15[FIR_HB63_NTAPS] = {\n");
    for (n = 0; n < TFB_HB_TAPS; n++) {
        if (n % 8 == 0) printf("   ");
        printf(" %6d,", hb_q15[n]);
        if (n % 8 == 7) printf("\n");
    }
    if (TFB_HB_TAPS % 8 != 0) printf("\n");
    printf("};\n\n");
    printf("#endif /* ITC_FIR_COEFFS_HB63_H */\n");
    return 0;
}
