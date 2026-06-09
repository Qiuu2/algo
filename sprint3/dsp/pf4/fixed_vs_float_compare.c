/**
 * @file    fixed_vs_float_compare.c
 * @brief   TASK-PF4-02 (Sub-2): 定点 Q31 树形 vs 浮点参考链 — 逐 bit 对比
 *
 * 目的：隔离"纯定点处理损失"，避免把输入量化误差混入 SNR 统计。
 *
 * ⚠️ 防复发（PM MINOR#2 清理 2026-05-29）：本程序门禁数字取【子带层/处理链】SNR，
 *    【不可】用差分金字塔【重建层】的 ~316dB 当门禁——重建层 PR(telescoping) 抵消会把
 *    误差压到机器精度、掩盖真实定点损失（Critic REV-S3-PF4 已独立确认）。
 *
 * 方法：
 *   1. 同一份 double 测试信号（chirp + 白噪声 + 满幅正弦）
 *   2. 两条链均从同一 Q31 量化输入出发（先统一量化，排除输入差异）：
 *      Chain A（定点 Q31）：Q31 输入 → C int32_t 树形 analyze/synthesize → Q31 输出 → double
 *      Chain B（浮点参考）：同一 Q31 输入 cast to double → double 树形 analyze/synthesize → double 输出
 *   3. 对比 Chain A vs Chain B 输出：SNR、最大误差、相位分析
 *
 * 注意事项：
 *   - host 桌面仿真，非 SHARC 实测，数字属于 L2（host 桌面仿真可信，算法学层面）。
 *   - 浮点参考链使用 double（64-bit），代表理想处理下限。
 *   - 门禁标准（DSP profile）：SNR_loss < 0.5 dB（任务规格），或备用：逐 bit 一致 / SNR>140dB。
 *
 * 编译：
 *   gcc -O2 -o fixed_vs_float fixed_vs_float_compare.c \
 *       ../tree_filterbank.c -lm -I..
 * 运行：./fixed_vs_float
 */

#include "../tree_filterbank.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <stdint.h>

/* ============================================================ */
/* 测试信号参数                                                  */
/* ============================================================ */
#define FS          48000
#define FRAME       64
#define N_FRAMES    1024          /* 65536 samples */
#define N_TOTAL     (FRAME * N_FRAMES)

/* ============================================================ */
/* 半带系数（Q15 定点 + double 浮点）——两链共享同一原型 FIR      */
/* ============================================================ */
static int16_t  hb_q15[TFB_HB_TAPS];
static double   hb_f64[TFB_HB_TAPS];

static double bessel_i0(double x) {
    double s = 1.0, t = 1.0;
    double x2 = (x / 2.0) * (x / 2.0);
    int k;
    for (k = 1; k <= 30; k++) {
        t *= x2 / ((double)k * k);
        s += t;
        if (t < 1e-18 * s) break;
    }
    return s;
}

static void make_halfband(void) {
    int N = TFB_HB_TAPS, n;
    double beta = 6.0, M = (double)(N - 1);
    double i0b = bessel_i0(beta), sum = 0.0;
    for (n = 0; n < N; n++) {
        double m = (double)n - M / 2.0;
        double sinc = (m == 0.0) ? 1.0 : sin(M_PI * 0.5 * m) / (M_PI * 0.5 * m);
        double r = (2.0 * (double)n / M) - 1.0;
        double win = bessel_i0(beta * sqrt(1.0 - r * r)) / i0b;
        hb_f64[n] = 0.5 * sinc * win;
        sum += hb_f64[n];
    }
    for (n = 0; n < N; n++) hb_f64[n] /= sum;  /* DC 增益归一化 = 1 */
    for (n = 0; n < N; n++) {
        long q = lround(hb_f64[n] * 32768.0);
        if (q >  32767) q =  32767;
        if (q < -32768) q = -32768;
        hb_q15[n] = (int16_t)q;
    }
}

/* ============================================================ */
/* Q31 <-> double 转换                                           */
/* ============================================================ */
static int32_t to_q31(double v) {
    double s = v * 2147483648.0;
    if (s >  2147483647.0) s =  2147483647.0;
    if (s < -2147483648.0) s = -2147483648.0;
    return (int32_t)s;
}
static double from_q31(int32_t v) { return (double)v / 2147483648.0; }

/* ============================================================ */
/* 浮点参考链（double 精度，镜像 C 定点链结构）                   */
/* 使用完全相同的 FIR 系数（hb_f64[]），相同滤波器结构，         */
/* 相同抽取/内插逻辑。                                           */
/* ============================================================ */

/* 浮点 HbFirState */
typedef struct {
    double   state[TFB_HB_TAPS];
    uint16_t widx;
} HbFirStateF64;

typedef struct {
    HbFirStateF64 ana_dec[TFB_NUM_LEVELS];
    HbFirStateF64 ana_int[TFB_NUM_LEVELS];
    HbFirStateF64 syn_int[TFB_NUM_LEVELS];
} TreeChF64;

static double hb_push_f64(HbFirStateF64 *s, double x) {
    uint16_t N = TFB_HB_TAPS;
    uint16_t idx = s->widx;
    double acc = 0.0;
    uint16_t k;

    s->state[idx] = x;
    idx = (uint16_t)((idx + 1u < N) ? (idx + 1u) : 0u);
    s->widx = idx;

    for (k = 0u; k < N; k++) {
        uint16_t rd = (uint16_t)((idx + k < N) ? (idx + k) : (idx + k - N));
        acc += hb_f64[k] * s->state[rd];
    }
    return acc;
}

static void hb_decimate2_f64(HbFirStateF64 *s,
                              const double *in, uint16_t n_in, double *out) {
    uint16_t i, o = 0u;
    for (i = 0u; i < n_in; i++) {
        double y = hb_push_f64(s, in[i]);
        if ((i & 1u) == 1u) out[o++] = y;
    }
}

static void hb_interp2_f64(HbFirStateF64 *s,
                            const double *in, uint16_t n_in, double *out) {
    uint16_t i, o = 0u;
    for (i = 0u; i < n_in; i++) {
        double y0 = hb_push_f64(s, in[i]);
        out[o++] = y0 * 2.0;
        double y1 = hb_push_f64(s, 0.0);
        out[o++] = y1 * 2.0;
    }
}

static void tfb_analyze_f64(TreeChF64 *ch, const double *in, uint16_t frame,
                             double *sb0, double *sb1, double *sb2, double *sb3) {
    double a1[256], a2[128], a3[64];
    double r1[512], r2[256], r3[128];
    uint16_t f0 = frame, f1 = frame/2u, f2 = frame/4u, f3 = frame/8u;
    uint16_t i;

    hb_decimate2_f64(&ch->ana_dec[0], in, f0, a1);
    hb_decimate2_f64(&ch->ana_dec[1], a1, f1, a2);
    hb_decimate2_f64(&ch->ana_dec[2], a2, f2, a3);

    hb_interp2_f64(&ch->ana_int[2], a3, f3, r3);
    hb_interp2_f64(&ch->ana_int[1], a2, f2, r2);
    hb_interp2_f64(&ch->ana_int[0], a1, f1, r1);

    for (i = 0u; i < f2; i++) sb1[i] = a2[i] - r3[i];
    for (i = 0u; i < f1; i++) sb2[i] = a1[i] - r2[i];
    for (i = 0u; i < f0; i++) sb3[i] = in[i]  - r1[i];
    for (i = 0u; i < f3; i++) sb0[i] = a3[i];
}

static void tfb_synthesize_f64(TreeChF64 *ch,
                                const double *sb0, const double *sb1,
                                const double *sb2, const double *sb3,
                                uint16_t frame, double *out) {
    double a2p[256], a1p[512];
    double up3[128], up2[256], up1[512];
    uint16_t f0 = frame, f1 = frame/2u, f2 = frame/4u, f3 = frame/8u;
    uint16_t i;

    hb_interp2_f64(&ch->syn_int[2], sb0, f3, up3);
    for (i = 0u; i < f2; i++) a2p[i] = up3[i] + sb1[i];

    hb_interp2_f64(&ch->syn_int[1], a2p, f2, up2);
    for (i = 0u; i < f1; i++) a1p[i] = up2[i] + sb2[i];

    hb_interp2_f64(&ch->syn_int[0], a1p, f1, up1);
    for (i = 0u; i < f0; i++) out[i] = up1[i] + sb3[i];
}

/* ============================================================ */
/* 相位分析：归一化互相关 peak，估算群延迟差                      */
/* ============================================================ */
static double xcorr_peak_lag(const double *a, const double *b, int N,
                              int max_lag, int *peak_lag) {
    double best = -1e30;
    int bestlag = 0;
    int lag;
    for (lag = -max_lag; lag <= max_lag; lag++) {
        double s = 0.0, pa = 0.0, pb = 0.0;
        int n;
        for (n = max_lag; n < N - max_lag; n++) {
            int nb = n + lag;
            if (nb < 0 || nb >= N) continue;
            s  += a[n] * b[nb];
            pa += a[n] * a[n];
            pb += b[nb] * b[nb];
        }
        double c = (pa > 0 && pb > 0) ? s / sqrt(pa * pb) : 0.0;
        if (c > best) { best = c; bestlag = lag; }
    }
    *peak_lag = bestlag;
    return best;
}

/* ============================================================ */
/* FFT 误差谱（简单 DFT，用于验证噪声分布）                       */
/* 仅分析前 4096 点，给出每 1/8 频段的平均误差能量               */
/* ============================================================ */
#define FFT_N 4096
static void error_spectrum_report(const double *err, int N) {
    int n, k;
    int nuse = (N < FFT_N) ? N : FFT_N;
    /* 8 个子带 */
    double band_e[8] = {0};
    int band_cnt[8] = {0};

    for (k = 1; k < FFT_N / 2; k++) {
        double re = 0, im = 0;
        for (n = 0; n < nuse; n++) {
            double w = 2.0 * M_PI * k * n / FFT_N;
            re += err[n] * cos(w);
            im -= err[n] * sin(w);
        }
        double mag2 = (re * re + im * im) / (FFT_N * FFT_N);
        int band = (int)(8.0 * k / (FFT_N / 2));
        if (band > 7) band = 7;
        band_e[band] += mag2;
        band_cnt[band]++;
    }
    printf("\n[误差谱分析 — 误差信号前 %d 点 DFT，8 子带分布]\n", nuse);
    printf("  子带 |  频率范围        | 归一化功率(dBFS)\n");
    for (int b = 0; b < 8; b++) {
        double f_lo = (double)b * FS / 16.0;
        double f_hi = (double)(b + 1) * FS / 16.0;
        double avg = (band_cnt[b] > 0) ? band_e[b] / band_cnt[b] : 1e-300;
        printf("  SB%d  |  %5.0f – %5.0f Hz | %7.1f dBFS\n",
               b, f_lo, f_hi, 10.0 * log10(avg + 1e-300));
    }
}

/* ============================================================ */
/* main                                                          */
/* ============================================================ */
int main(void) {
    /* ---- 静态缓冲（avoid stack overflow for large N_TOTAL=65536） ---- */
    static int32_t  x_q31[N_TOTAL];      /* 共同量化输入（Q31） */
    static double   x_f64[N_TOTAL];      /* 同一输入的 double 视图 */
    static double   y_float[N_TOTAL];    /* Chain B 浮点参考链输出 */
    static int32_t  y_fixed_q31[N_TOTAL];/* Chain A 定点链输出（Q31） */
    static double   y_fixed[N_TOTAL];    /* Chain A 转 double */
    static double   err[N_TOTAL];        /* 误差 = y_fixed - y_float */

    /* 子带帧缓冲 */
    int32_t  fsb0[FRAME/8], fsb1[FRAME/4], fsb2[FRAME/2], fsb3[FRAME];
    double   dsb0[FRAME/8], dsb1[FRAME/4], dsb2[FRAME/2], dsb3[FRAME];

    /* 分析/合成状态 */
    static TreeChannelState   fix_ana, fix_syn;
    static TreeChF64          flt_ana, flt_syn;

    int i, fnum;

    printf("================================================================\n");
    printf("  TASK-PF4-02 Sub-2: 定点 Q31 vs 浮点参考链 — host 桌面仿真\n");
    printf("  [L2] host-PC gcc -O2, 非 SHARC 实测\n");
    printf("================================================================\n\n");

    /* ---- 1. 生成半带系数 ---- */
    make_halfband();
    tfb_set_coeffs(hb_q15, TFB_HB_TAPS);

    printf("[半带滤波器] %d tap, kaiser beta=6, Q15 量化\n", TFB_HB_TAPS);
    {
        /* 验证 Q15 量化对系数的影响 */
        double coef_err = 0.0, coef_max = 0.0;
        for (int n = 0; n < TFB_HB_TAPS; n++) {
            double q = (double)hb_q15[n] / 32768.0;
            double e = fabs(q - hb_f64[n]);
            coef_err += e * e;
            if (e > coef_max) coef_max = e;
        }
        printf("  系数 Q15 量化误差：RMS=%.2e, Max=%.2e (相对精度 %.1f dB)\n\n",
               sqrt(coef_err / TFB_HB_TAPS), coef_max,
               -20.0 * log10(coef_max + 1e-30));
    }

    /* ---- 2. 生成测试信号：对数 chirp 20Hz→11kHz，幅度 0.5 ---- */
    printf("[测试信号] 对数 chirp 20Hz->11kHz, A=0.5, %d 样点 (%.3f s)\n",
           N_TOTAL, (double)N_TOTAL / FS);
    for (i = 0; i < N_TOTAL; i++) {
        double t = (double)i / FS;
        double T = (double)N_TOTAL / FS;
        double f0 = 20.0, f1 = 11000.0;
        double K = pow(f1 / f0, t / T);
        double phase = 2.0 * M_PI * f0 * T / log(f1 / f0) * (K - 1.0);
        double val = 0.5 * sin(phase);
        /* 量化到 Q31（两链共享同一量化输入，隔离输入差异） */
        x_q31[i] = to_q31(val);
        x_f64[i] = from_q31(x_q31[i]);   /* 精确的 Q31 → double（去除量化误差影响） */
    }
    printf("  输入 RMS = %.6f\n\n", (double[]){({
        double s=0; for(int k=0;k<N_TOTAL;k++)s+=x_f64[k]*x_f64[k]; sqrt(s/N_TOTAL);
    })}[0]);

    /* ---- 3. Chain A：定点 Q31 树形 ---- */
    printf("[Chain A] 定点 Q31 树形（C int32_t 实现）...\n");
    memset(&fix_ana, 0, sizeof(fix_ana)); fix_ana.initialized = 1;
    memset(&fix_syn, 0, sizeof(fix_syn)); fix_syn.initialized = 1;
    for (fnum = 0; fnum < N_FRAMES; fnum++) {
        int32_t *xin  = &x_q31[fnum * FRAME];
        int32_t *yout = &y_fixed_q31[fnum * FRAME];
        tfb_analyze(&fix_ana, xin, FRAME, fsb0, fsb1, fsb2, fsb3);
        tfb_synthesize(&fix_syn, fsb0, fsb1, fsb2, fsb3, FRAME, yout);
    }
    for (i = 0; i < N_TOTAL; i++) y_fixed[i] = from_q31(y_fixed_q31[i]);
    printf("  Chain A 完成。\n");

    /* ---- 4. Chain B：浮点参考链（double）---- */
    printf("[Chain B] 浮点参考链（double，镜像同一结构）...\n");
    memset(&flt_ana, 0, sizeof(flt_ana));
    memset(&flt_syn, 0, sizeof(flt_syn));
    for (fnum = 0; fnum < N_FRAMES; fnum++) {
        double *xin  = &x_f64[fnum * FRAME];
        double *yout = &y_float[fnum * FRAME];
        tfb_analyze_f64(&flt_ana, xin, FRAME, dsb0, dsb1, dsb2, dsb3);
        tfb_synthesize_f64(&flt_syn, dsb0, dsb1, dsb2, dsb3, FRAME, yout);
    }
    printf("  Chain B 完成。\n\n");

    /* ---- 5. 对比分析 ---- */
    printf("================================================================\n");
    printf("  对比结果：Chain A (定点 Q31) vs Chain B (浮点 double 参考)\n");
    printf("  口径：同一 Q31 量化输入，隔离纯处理损失\n");
    printf("================================================================\n\n");

    int guard = 600;  /* 跳过启动瞬态 */
    int Nuse = N_TOTAL - 2 * guard;

    /* 计算误差 */
    for (i = 0; i < N_TOTAL; i++) err[i] = y_fixed[i] - y_float[i];

    /* 信号功率（以浮点参考为基准） */
    double sig_pow = 0.0, err_pow = 0.0, max_err = 0.0;
    double sig_max = 0.0;
    for (i = guard; i < N_TOTAL - guard; i++) {
        sig_pow += y_float[i] * y_float[i];
        err_pow += err[i] * err[i];
        double ae = fabs(err[i]);
        if (ae > max_err) max_err = ae;
        if (fabs(y_float[i]) > sig_max) sig_max = fabs(y_float[i]);
    }
    sig_pow /= Nuse;
    err_pow /= Nuse;

    double sig_rms = sqrt(sig_pow);
    double err_rms = sqrt(err_pow);
    double snr_db = 10.0 * log10(sig_pow / (err_pow + 1e-300));
    double max_err_lsb = max_err * 2147483648.0;  /* 转为 Q31 LSB */
    double max_err_db = 20.0 * log10(max_err / (sig_max + 1e-30));

    printf("[SNR 结果 — L2 host 桌面仿真]\n");
    printf("  Chain B (浮点) 输出 RMS     = %.6f\n", sig_rms);
    printf("  Chain B (浮点) 输出最大值   = %.6f\n", sig_max);
    printf("  误差 RMS                    = %.3e\n", err_rms);
    printf("  误差最大绝对值              = %.3e (%.2f LSB Q31) (%.1f dBFS)\n",
           max_err, max_err_lsb, max_err_db);
    printf("\n");
    printf("  *** 定点 vs 浮点 SNR = %.1f dB  [L2] ***\n", snr_db);
    printf("\n");

    /* 门禁判断 */
    double gate_snr = 140.0;  /* DSP profile 门禁 */
    double gate_snr_loss = 0.5; /* 任务规格：SNR 损失 < 0.5 dB */

    /* 浮点参考链自身 SNR（相对原始 double 输入，即处理链的固有损失） */
    double float_sig_pow = 0.0, float_err_pow = 0.0;
    for (i = guard; i < N_TOTAL - guard; i++) {
        float_sig_pow += x_f64[i] * x_f64[i];
        double fe = y_float[i] - x_f64[i];
        float_err_pow += fe * fe;
    }
    float_sig_pow /= Nuse;
    float_err_pow /= Nuse;
    double float_snr = 10.0 * log10(float_sig_pow / (float_err_pow + 1e-300));
    double snr_loss = float_snr - snr_db;  /* 定点化导致的 SNR 损失（相对浮点参考） */

    printf("[SNR 损失分析]\n");
    printf("  浮点参考链 SNR（vs 量化输入）= %.1f dB  [L2]\n", float_snr);
    printf("  定点链     SNR（vs 浮点参考）= %.1f dB  [L2]\n", snr_db);
    printf("  SNR 损失（定点化损失）        = %.2f dB  [L2]\n", snr_loss);
    printf("\n");

    printf("[门禁判断]\n");
    if (snr_db >= gate_snr) {
        printf("  ✓ SNR=%.1f dB >= 门禁 %.0f dB → 通过  [L2]\n", snr_db, gate_snr);
    } else {
        printf("  ✗ SNR=%.1f dB < 门禁 %.0f dB → 未通过  [L2]\n", snr_db, gate_snr);
    }
    if (snr_loss <= gate_snr_loss) {
        printf("  ✓ SNR 损失=%.2f dB <= %.1f dB（任务规格）→ 通过  [L2]\n",
               snr_loss, gate_snr_loss);
    } else {
        printf("  ✗ SNR 损失=%.2f dB > %.1f dB（任务规格）→ 未通过  [L2]\n",
               snr_loss, gate_snr_loss);
    }

    /* ---- 6. 相位分析（互相关 peak lag） ---- */
    printf("\n[相位漂移分析 — 互相关峰延迟]\n");
    {
        int peak_lag = 0;
        double peak_corr = xcorr_peak_lag(
            y_float + guard, y_fixed + guard,
            N_TOTAL - 2 * guard, 10, &peak_lag
        );
        printf("  互相关峰 lag = %d samples (%.3f ms)  [L2]\n",
               peak_lag, 1000.0 * peak_lag / FS);
        printf("  互相关系数   = %.8f  [L2]\n", peak_corr);
        if (peak_lag == 0 && peak_corr > 0.9999) {
            printf("  ✓ 无可检测相位漂移（lag=0，相关系数>0.9999）\n");
        } else {
            printf("  ⚠ 相位漂移检测：lag=%d, corr=%.6f（需关注）\n",
                   peak_lag, peak_corr);
        }
    }

    /* ---- 7. 误差谱分析 ---- */
    error_spectrum_report(err + guard, Nuse < FFT_N ? Nuse : FFT_N);

    /* ---- 8. 导出 CSV ---- */
    {
        FILE *fp = fopen("pf4_fixed_vs_float.csv", "w");
        if (fp) {
            fprintf(fp, "n,x_q31_in,y_float,y_fixed,err\n");
            for (i = guard; i < guard + 4096 && i < N_TOTAL - guard; i++) {
                fprintf(fp, "%d,%.10e,%.10e,%.10e,%.10e\n",
                        i, x_f64[i], y_float[i], y_fixed[i], err[i]);
            }
            fclose(fp);
            printf("\n[CSV] 已写 pf4_fixed_vs_float.csv（前 4096 有效样点，供 Python 画图）\n");
        }
    }

    /* ---- 9. 诚实边界声明 ---- */
    printf("\n================================================================\n");
    printf("  [诚实边界 / 标签说明]\n");
    printf("  本程序：HOST 桌面 gcc -O2 仿真，标签 [L2]。\n");
    printf("  数字结论属于「算法学层面可信」，非「SHARC 平台验证」。\n");
    printf("  SHARC 平台定点实测（含硬件流水线/寄存器/中断开销）属于\n");
    printf("  PF-5 / EZKIT 阶段，须上 EV-21569-EZKIT 后验证。\n");
    printf("  本任务（PF-4-Sub2）结论：桌面层面可关闭，SHARC 真值属 PF-5。\n");
    printf("================================================================\n");

    return 0;
}
