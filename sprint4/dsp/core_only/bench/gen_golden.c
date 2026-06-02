/**
 * @file    gen_golden.c
 * @brief   生成内存向量法的独立 golden（host 计算 → 冻结进 golden_ref.h）
 *
 * 内存向量法 S2 bit-exact 的 golden 必须独立于 on-target 运行：
 *   host 跑参考单通道链（走 tree_verify 同一路径）→ 整数 Q31 y_ref[] →
 *   CRC32(全 65536 样本) + 64 样本 spot 子集。on-target harness 跑出 SHARC 输出后
 *   重算 CRC32 + spot 比对此冻结 golden → 匹配即跨架构 bit-exact[L1/EZKIT]。
 *
 * 编译：gcc -O2 -I../include -I../src -o /tmp/gg gen_golden.c ../src/tree_filterbank.c ../src/tfb_8ch.c -lm
 *   sat   : 默认
 *   unsat : 加 -DTFB_DISABLE_SAT
 * 运行打印该 build 的 GOLDEN_CRC32 + spot；PM 据 sat/unsat 两次运行汇成 golden_ref.h。
 */
#include "tree_filterbank.h"
#include "fir_coeffs_hb63.h"
#include "chirp_input.h"   /* 冻结 chirp 输入（与 bench_harness 同一份）→ golden 基于冻结输入 */
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#ifndef M_PI   /* -std=c99 严格 / SHARC cc21k 可能未定义（与 bench_harness.c 一致） */
#define M_PI 3.14159265358979323846
#endif

#define FS 48000
#define FRAME 64
#define N_FRAMES 1024
#define N_TOTAL (FRAME*N_FRAMES)
#define N_SPOT 64

#ifdef TFB_DISABLE_SAT
#define BUILD_TAG "UNSAT"
#else
#define BUILD_TAG "SAT"
#endif

/* make_halfband live —— 与 tree_verify.c:40-60 / host_bitexact.c 同源 */
static int16_t hb_q15[TFB_HB_TAPS];
static double i0_(double x){double s=1,t=1;int k;double x2=(x/2)*(x/2);for(k=1;k<=30;k++){t*=x2/((double)k*k);s+=t;if(t<1e-18*s)break;}return s;}
static void make_hb(void){int N=TFB_HB_TAPS,n;double beta=6,M=(double)(N-1),i0b=i0_(beta),sum=0,f[256];
    for(n=0;n<N;n++){double m=(double)n-M/2;double sc=(m==0)?1:sin(M_PI*0.5*m)/(M_PI*0.5*m);double r=2.0*n/M-1;double w=i0_(beta*sqrt(1-r*r))/i0b;f[n]=0.5*sc*w;sum+=f[n];}
    for(n=0;n<N;n++)f[n]/=sum;
    for(n=0;n<N;n++){long q=lround(f[n]*32768.0);if(q>32767)q=32767;if(q<-32768)q=-32768;hb_q15[n]=(int16_t)q;}}

static int32_t to_q31(double v){double s=v*2147483648.0;if(s>2147483647.0)s=2147483647.0;if(s<-2147483648.0)s=-2147483648.0;return (int32_t)s;}

static int32_t x[N_TOTAL], y_ref[N_TOTAL];

/* CRC32 (IEEE 802.3, 反射, 0xEDB88320) over int32 little-endian 字节流 */
static uint32_t crc32_buf(const int32_t *d, int n){
    uint32_t c=0xFFFFFFFFu;
    for(int i=0;i<n;i++){
        uint32_t v=(uint32_t)d[i];
        for(int b=0;b<4;b++){
            uint8_t byte=(uint8_t)(v>>(8*b));
            c^=byte;
            for(int k=0;k<8;k++) c=(c&1)?(c>>1)^0xEDB88320u:(c>>1);
        }
    }
    return c^0xFFFFFFFFu;
}

int main(void){
    if(FIR_HB63_NTAPS!=63||TFB_HB_TAPS!=63){fprintf(stderr,"NTAPS!=63\n");return 2;}
    make_hb(); tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);
    /* 输入 = 冻结 chirp（CHIRP_INPUT[]）→ golden 证明基于冻结输入算（与 bench_harness 同源） */
    if(CHIRP_INPUT_N != N_TOTAL){fprintf(stderr,"CHIRP_INPUT_N!=N_TOTAL\n");return 2;}
    for(int i=0;i<N_TOTAL;i++) x[i]=CHIRP_INPUT[i];
    TreeChannelState ana,syn; int32_t sb0[FRAME/8],sb1[FRAME/4],sb2[FRAME/2],sb3[FRAME];
    tfb_channel_init(&ana); tfb_channel_init(&syn);
    for(int f=0;f<N_FRAMES;f++){tfb_analyze(&ana,&x[f*FRAME],FRAME,sb0,sb1,sb2,sb3);
        tfb_synthesize(&syn,sb0,sb1,sb2,sb3,FRAME,&y_ref[f*FRAME]);}
    uint32_t crc=crc32_buf(y_ref,N_TOTAL);
    printf("/* build=%s */\n",BUILD_TAG);
    printf("GOLDEN_CRC32_%s = 0x%08X\n",BUILD_TAG,crc);
    printf("SPOT_%s[%d] @ stride %d:\n",BUILD_TAG,N_SPOT,N_TOTAL/N_SPOT);
    for(int i=0;i<N_SPOT;i++){int idx=i*(N_TOTAL/N_SPOT);printf("%d,",y_ref[idx]);}
    printf("\n");
    return 0;
}
