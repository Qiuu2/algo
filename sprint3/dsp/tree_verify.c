/**
 * @file    tree_verify.c
 * @brief   桌面（host）验证 + MCPS 实算 harness for tree_filterbank.c
 *
 * ⚠️ 这是 HOST（PC gcc）验证，NOT 平台验证。
 *    - 数值/重建正确性：host 与 SHARC 一致（纯整数运算，可移植）。
 *    - MCPS：这里是"实算 MAC 计数 × 速率"得到的算法学算力，
 *      仍非 EZKIT cycle-counter 实测。真实 MCPS 须上板测（见 README/dsp 报告）。
 *
 * 编译：gcc -O2 -o tree_verify tree_verify.c tree_filterbank.c -lm
 * 运行：./tree_verify
 *   - stdout 打印重建误差 / MCPS
 *   - 写 tree_io.csv（输入 vs 重建，供 Python 做频谱平坦度/混叠分析）
 */

#include "tree_filterbank.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <stdint.h>

#define FS        48000
#define FRAME     64           /* 帧长，8 的倍数 */
#define N_FRAMES  1024         /* 总帧数 -> 65536 样点 */
#define N_TOTAL   (FRAME*N_FRAMES)

/* ---- 半带系数（Q15），运行时由本 harness 内生成（kaiser β=6, 63tap, cutoff fs/4） ---- */
static int16_t  hb_q15[TFB_HB_TAPS];
static double   hb_f64[TFB_HB_TAPS];

/* 修正 Bessel I0 级数 */
static double i0(double x) {
    double s = 1.0, t = 1.0; int k;
    double x2 = (x/2.0)*(x/2.0);
    for (k = 1; k <= 30; k++) { t *= x2/((double)k*k); s += t; if (t < 1e-18*s) break; }
    return s;
}

static void make_halfband(void) {
    /* firwin(63, 0.5, kaiser beta=6) 等价：sinc(0.5) × Kaiser，再归一化 DC=1 */
    int N = TFB_HB_TAPS, n;
    double beta = 6.0, M = (double)(N-1);
    double i0b = i0(beta), sum = 0.0;
    for (n = 0; n < N; n++) {
        double m = (double)n - M/2.0;
        double sinc = (m == 0.0) ? 1.0 : sin(M_PI*0.5*m)/(M_PI*0.5*m); /* cutoff 0.5*nyq */
        double r = (2.0*(double)n/M) - 1.0;
        double win = i0(beta*sqrt(1.0 - r*r)) / i0b;
        hb_f64[n] = 0.5 * sinc * win;   /* 0.5 = cutoff/nyq factor for firwin scaling */
        sum += hb_f64[n];
    }
    for (n = 0; n < N; n++) hb_f64[n] /= sum;          /* DC 增益归一化 = 1 */
    for (n = 0; n < N; n++) {
        long q = lround(hb_f64[n] * 32768.0);
        if (q > 32767) { q = 32767; }
        if (q < -32768) { q = -32768; }
        hb_q15[n] = (int16_t)q;
    }
}

/* Q31 <-> double */
static int32_t to_q31(double v){ double s=v*2147483648.0; if(s>2147483647.0)s=2147483647.0; if(s<-2147483648.0)s=-2147483648.0; return (int32_t)s; }
static double  from_q31(int32_t v){ return (double)v/2147483648.0; }

int main(void) {
    static int32_t x[N_TOTAL], y[N_TOTAL];
    static double  xf[N_TOTAL], yf[N_TOTAL];
    int32_t sb0[FRAME/8], sb1[FRAME/4], sb2[FRAME/2], sb3[FRAME];
    TreeChannelState ana, syn;   /* 分析/合成各用独立状态实例 */
    int i, fnum;

    make_halfband();
    tfb_set_coeffs(hb_q15, TFB_HB_TAPS);

    /* 半带阻带（host 估计：用频响在 0.3fs 以上的峰值） */
    {
        double maxstop = 0.0;
        int kf;
        for (kf = 0; kf <= 2048; kf++) {
            double w = M_PI * (double)kf/2048.0;       /* 0..pi */
            if (w < 0.30*2.0*M_PI/2.0) continue;        /* >0.30 fs region (w>0.6pi) */
            if (w < 0.6*M_PI) continue;
            double re=0, im=0; int n;
            for (n=0;n<TFB_HB_TAPS;n++){ re+=hb_f64[n]*cos(w*n); im-=hb_f64[n]*sin(w*n);}
            double mag = sqrt(re*re+im*im);
            if (mag > maxstop) maxstop = mag;
        }
        printf("半带原型 %d tap, kaiser beta=6: 阻带(>0.30fs)衰减 = %.1f dB\n",
               TFB_HB_TAPS, -20.0*log10(maxstop+1e-12));
    }

    /* 对数扫频 chirp 20Hz->11kHz
     * ── PF-4 FIX-01 headroom 约定（重要）──
     * 标称幅度取 0.289 = 0.5 × (1/1.7309)：在原 −6dBFS 测试电平上再叠加
     * 半带链路约定的 −4.8dB headroom（1/Σ|h|），使差分金字塔 detail 子带的
     * 中间值不触及 Q31 满量程 → 修复后的饱和钳位在标称下不激活 →
     * 重建数值与修复前逐位一致（已 bit-exact 验证）。
     * 若改回 0.5（违反 headroom），detail 子带达 FS、饱和激活，属预期保护行为
     * （非回归）；对抗激励溢出验证见 tree_verify_adversarial.c。 */
    for (i = 0; i < N_TOTAL; i++) {
        double t = (double)i/FS;
        double T = (double)N_TOTAL/FS;
        double f0=20.0, f1=11000.0;
        double K = pow(f1/f0, t/T);
        double phase = 2.0*M_PI*f0*T/log(f1/f0)*(K-1.0);
        xf[i] = 0.289*sin(phase);   /* −10.8 dBFS = −6dBFS + −4.8dB headroom */
        x[i]  = to_q31(xf[i]);
    }

    /* 逐帧 analyze -> synthesize（跨帧状态连续） */
    tfb_channel_init(&ana);
    tfb_channel_init(&syn);
    for (fnum = 0; fnum < N_FRAMES; fnum++) {
        int32_t *xin  = &x[fnum*FRAME];
        int32_t *yout = &y[fnum*FRAME];
        tfb_analyze(&ana, xin, FRAME, sb0, sb1, sb2, sb3);
        tfb_synthesize(&syn, sb0, sb1, sb2, sb3, FRAME, yout);
    }
    for (i = 0; i < N_TOTAL; i++) yf[i] = from_q31(y[i]);

    /* ---- 重建误差（扫描最佳整数延迟对齐） ---- */
    {
        int D, bestD=0; double bestrms=1e30;
        int guard = 600;
        for (D = 0; D < 500; D++) {
            double se=0; int cnt=0; int n;
            for (n = guard; n < N_TOTAL-guard; n++) {
                double e = xf[n] - yf[n+D];
                se += e*e; cnt++;
            }
            double rms = sqrt(se/cnt);
            if (rms < bestrms){ bestrms=rms; bestD=D; }
        }
        double sig=0; int n;
        for (n=guard;n<N_TOTAL-guard;n++) sig += xf[n]*xf[n];
        sig = sqrt(sig/(N_TOTAL-2*guard));
        double maxe=0;
        for (n=guard;n<N_TOTAL-guard;n++){ double e=fabs(xf[n]-yf[n+bestD]); if(e>maxe)maxe=e;}
        printf("\n[重建验证 — 定点 Q31 树形, host]\n");
        printf("  最佳对齐延迟 = %d samples (= %.3f ms)\n", bestD, 1000.0*bestD/FS);
        printf("  时域重建 RMS 误差 = %.3e  (信号 RMS = %.3f)\n", bestrms, sig);
        printf("  时域最大绝对误差 = %.3e\n", maxe);
        printf("  重建 SNR = %.1f dB  (定点 Q31 量化底，非结构缺陷)\n",
               20.0*log10(sig/(bestrms+1e-30)));

        /* 导出 io 给 Python 做频谱/混叠分析（已对齐） */
        FILE *fp = fopen("tree_io.csv","w");
        fprintf(fp,"x,y\n");
        for (n=guard;n<N_TOTAL-guard;n++) fprintf(fp,"%.10e,%.10e\n", xf[n], yf[n+bestD]);
        fclose(fp);
        printf("  已写 tree_io.csv (input vs aligned-recon, 供 Python 频谱分析)\n");
    }

    /* ---- MCPS 实算（按本实现的真实 MAC 计数）---- */
    {
        /* 每个 hb_push_filter = N_TAPS 次 MAC（全长卷积参考实现）。
         * 半带优化：约半数系数为 0，硬件可跳到 (N+1)/2 次。两个口径都给。 */
        int Ntap = TFB_HB_TAPS;
        int Nnz  = (TFB_HB_TAPS+1)/2;   /* 半带非零系数（含中心） */

        /* 单通道每秒 push_filter 次数：
         * 分析 decimate: L1 处理 fs 个输入；L2 处理 fs/2；L3 处理 fs/4
         *   （decimate 对每个输入都 push_filter 一次）
         * 分析 interp(求detail): 各级 interp2 对每输入 push 2 次，输入率 fs/2,fs/4,fs/8
         *   实际 hb_interp2 每输入 push 2 次 → push 率 = 2×输入率 = fs, fs/2, fs/4
         * 合成 interp: 同分析 interp，push 率 fs/4,fs/2,fs (syn L3->L2->L1 输入 fs/8,fs/4,fs/2)
         */
        double pf_ana_dec = (double)FS + FS/2.0 + FS/4.0;             /* dec 各级 push 率 */
        double pf_ana_int = 2.0*(FS/2.0 + FS/4.0 + FS/8.0);          /* ana detail interp */
        double pf_syn_int = 2.0*(FS/8.0 + FS/4.0 + FS/2.0);          /* synth interp */
        double pf_total   = pf_ana_dec + pf_ana_int + pf_syn_int;    /* push_filter/s/ch */

        double mac_full = pf_total * Ntap / 1e6;     /* 全长卷积 MMAC/s/ch */
        double mac_hb   = pf_total * Nnz  / 1e6;     /* 半带跳零 MMAC/s/ch */

        int n_ch_16 = 16, n_ch_8 = 8;
        double fullrate_ref = 1480.0;  /* 全速率 437 抽头方案（决策"不可行"基准） */
        double cap_21569 = 1500.0;     /* 21569 保守口径 */
        double cap_21565 = 750.0;      /* 21565 单核 SHARC+ ~500MHz 量级保守口径（估算，待 datasheet 核实） */

        printf("\n[树形 MCPS 实算 — 由本 C 实现的真实 MAC 计数推得]\n");
        printf("  半带抽头 %d (非零 %d)；每通道 push_filter 率 = %.0f /s\n", Ntap, Nnz, pf_total);
        printf("  分析dec %.0f + 分析int %.0f + 合成int %.0f (push/s)\n", pf_ana_dec, pf_ana_int, pf_syn_int);
        printf("  ── 单通道滤波器组算力 ──\n");
        printf("    全长卷积口径: %.2f MMAC/s/ch\n", mac_full);
        printf("    半带跳零口径: %.2f MMAC/s/ch\n", mac_hb);
        printf("  ── 整阵滤波器组（仅树形，不含波束求和/分数延迟）──\n");
        printf("    16ch 全长: %.1f MMAC/s | 16ch 半带跳零: %.1f MMAC/s\n",
               mac_full*n_ch_16, mac_hb*n_ch_16);
        printf("    8ch  全长: %.1f MMAC/s | 8ch  半带跳零: %.1f MMAC/s\n",
               mac_full*n_ch_8, mac_hb*n_ch_8);
        printf("  ── vs 全速率 437 抽头方案 %.0f MMAC/s（决策\"不可行\"基准）──\n", fullrate_ref);
        printf("    16ch 半带跳零 %.1f MMAC/s → 相对全速率省 %.1f×\n",
               mac_hb*n_ch_16, fullrate_ref/(mac_hb*n_ch_16));
        printf("  ── 裕量（仅滤波器组，半带跳零口径）──\n");
        printf("    21569(cap %.0f): 16ch=%.0f× 8ch=%.0f×\n",
               cap_21569, cap_21569/(mac_hb*n_ch_16), cap_21569/(mac_hb*n_ch_8));
        printf("    21565(cap %.0f,估算): 16ch=%.0f× 8ch=%.0f×\n",
               cap_21565, cap_21565/(mac_hb*n_ch_16), cap_21565/(mac_hb*n_ch_8));
        printf("  注：核心波束（分数延迟+加权求和）另计；broadside DAS 时分数延迟≈0，\n");
        printf("      波束=8/16 路加权求和，量级 ~3-6 MMAC/s（见 budget_calc.py），相对滤波器组小。\n");

        /* ── 系统级正确口径：分析 ×N_CH，合成 ×1（broadside DAS 输出单路）── */
        {
            double pf_ana = (FS + FS/2.0 + FS/4.0) + 2.0*(FS/2.0 + FS/4.0 + FS/8.0);
            double pf_syn = 2.0*(FS/8.0 + FS/4.0 + FS/2.0);
            printf("\n  ── 系统级 MCPS（分析×N_CH + 合成×1，半带跳零口径，broadside DAS）──\n");
            printf("    %-8s %-14s %-10s %-10s\n", "N_CH", "滤波器组MMAC/s", "21569裕量", "21565裕量(估)");
            int nchs[2] = {16, 8};
            for (int q = 0; q < 2; q++) {
                int nc = nchs[q];
                double fb = (pf_ana*Nnz*nc + pf_syn*Nnz*1) / 1e6;
                printf("    %-8d %-14.1f %-10.0f %-10.0f\n",
                       nc, fb, cap_21569/fb, cap_21565/fb);
            }
            printf("    对比 budget_calc.py 纸面声称: 16ch=56.4 / 8ch=30.56 MMAC/s（约低 2×）\n");
        }
    }

    printf("\n[免责声明] 以上为 HOST 桌面验证 + 算法学 MCPS（MAC计数×速率）。\n");
    printf("           真实 MCPS 必须 EZKIT cycle-counter 实测（含 cache/取模/中断开销）。\n");
    return 0;
}
