/**
 * @file    bench_harness.c
 * @brief   内存向量法 S2-S5 harness 实现（纯算法，无 ADI 依赖；可 host 预验）
 *
 * 编译（host 预验，含自带 main）：
 *   sat   : gcc -O2 -DBENCH_HOST_MAIN -I../include -I../src -o /tmp/bh_sat   bench_harness.c ../src/tree_filterbank.c ../src/tfb_8ch.c -lm
 *   unsat : gcc -O2 -DBENCH_HOST_MAIN -DTFB_DISABLE_SAT ... 同上
 * target（嫁接）：由 bench_main.c 在 adi_initComponents() 后调 bench_run()，本文件不带 main。
 *
 * CCNT：host 用 clock() 占位（数值无意义，仅验 plumbing，cyc_valid=0）；
 *       target 待回填真 CCNT（def21569.h，cyc_valid=1，[L1/EZKIT]）。
 */
#include "tree_filterbank.h"
#include "tfb_8ch.h"
#include "fir_coeffs_hb63.h"
#include "bench_harness.h"
#include "golden_ref.h"
#include "chirp_input.h"   /* 冻结 chirp 输入（host 64-bit double 预算，消 -double-size-32 分叉） */
#include <string.h>
#include <stdint.h>
/* ⚠️ 不再 include <math.h>/不再运行期算 chirp：冻结输入后 bit-exact 路径
 *   零 double/pow/sin → host 与 target（-double-size-32）逐位一致（R14 根因修复）。*/

/* ---- 输入 = 冻结 chirp（CHIRP_INPUT[]，算法直接读，无运行期 double） ---- */
typedef char chirp_len_check[(CHIRP_INPUT_N == BENCH_FRAME*BENCH_NFR) ? 1 : -1]; /* 编译期校验长度 */
static int32_t s_y[BENCH_FRAME*BENCH_NFR];
static int32_t s_in8[TFB8_NCH][TFB8_FRAME];

/* Expose this single existing frozen chirp (fira_regression references it to avoid a 2nd 256KB copy
 * -> prevents L1/L2 li1040 overflow). chirp_input.h is `static const` (per-TU copy); this accessor
 * lets other TUs reuse the one copy held here. ASCII-only (CCES). */
const int32_t *bench_chirp_input(void) { return CHIRP_INPUT; }

/* CRC32 IEEE 802.3（与 gen_golden.c 同算法） */
static uint32_t crc32_buf(const int32_t *d,int n){uint32_t c=0xFFFFFFFFu;
    for(int i=0;i<n;i++){uint32_t v=(uint32_t)d[i];for(int b=0;b<4;b++){uint8_t by=(uint8_t)(v>>(8*b));c^=by;
        for(int k=0;k<8;k++)c=(c&1)?(c>>1)^0xEDB88320u:(c>>1);}}return c^0xFFFFFFFFu;}

/* ---- CCNT 抽象 ---- */
#ifdef TARGET_SHARC
/* 【待 CTO 台架回填】#include <def21569.h>; 用 EMUCLK/CCNT 自由运行计数器。
 * 例（伪，依 21569 SHARC+ Core Programming Reference 实际寄存器名）：
 *   static inline uint32_t bench_cyc(void){ return __builtin_emuclk(); } */
extern uint32_t bench_cyc_target(void);
#define BENCH_CYC()  bench_cyc_target()
#define BENCH_CYC_VALID 1
#else
#include <time.h>
#define BENCH_CYC()  ((uint32_t)clock())   /* host 占位：数值无意义 */
#define BENCH_CYC_VALID 0
#endif

int bench_run(BenchResult *r){
    memset(r,0,sizeof(*r));
    r->cyc_valid = BENCH_CYC_VALID;
    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);   /* hb63，禁 437（NTAPS 守） */
    /* 输入已冻结（CHIRP_INPUT[]，host 预算），无运行期生成 → 无 double 分叉 */

    /* ---- S2 bit-exact：单通道链 → 输出 → CRC32 + spot vs golden_ref.h ---- */
    {
        TreeChannelState ana, syn;
        int32_t sb0[BENCH_FRAME/8], sb1[BENCH_FRAME/4], sb2[BENCH_FRAME/2], sb3[BENCH_FRAME];
        tfb_channel_init(&ana); tfb_channel_init(&syn);
        uint32_t c0a=BENCH_CYC(); /* 顺带量首帧 analyze（cycle 用稳态见下） */
        for(int f=0; f<BENCH_NFR; f++){
            tfb_analyze(&ana, &CHIRP_INPUT[f*BENCH_FRAME], BENCH_FRAME, sb0,sb1,sb2,sb3);
            tfb_synthesize(&syn, sb0,sb1,sb2,sb3, BENCH_FRAME, &s_y[f*BENCH_FRAME]);
        }
        (void)c0a;
        r->crc32 = crc32_buf(s_y, BENCH_FRAME*BENCH_NFR);
        r->crc_match = (r->crc32 == GOLDEN_CRC32) ? 1:0;
        int sm=1;
        for(int i=0;i<GOLDEN_NSPOT;i++) if(s_y[i*GOLDEN_SPOT_STRIDE]!=GOLDEN_SPOT[i]){sm=0;break;}
        r->spot_match = sm;
        r->bitexact_pass = r->crc_match && r->spot_match;
    }

    /* ---- S3 cycle：稳态单帧 analyze / synth / 8ch（扣首帧冷 cache，取稳态中位近似） ---- */
    {
        /* F7-FIX2 (board crash PC=0x1 in bench_run): st8 (~37KB Tfb8State) + out8 (~2KB) as STACK
         * locals made bench_run's frame ~43KB. The e338288 F7 block added ~36KB of new .bss statics
         * (f7_fa[8]/f7_ca[8] in fira_regression.c) which shrank the RESERVE_EXPAND L1 stack remainder
         * (proxy app.ldf: initial reserve :241-244, RESERVE_EXPAND stack/heap split :1334-1343 of the
         * leftover L1 Block0) -> bench_run's pre-existing frame now overflows the smaller stack and
         * smashes the return address (vector to 0x1). Moving the two large locals to file-scope static
         * (same discipline e338288 used for f7_fa/f7_ca) keeps the computation unchanged (bench is
         * single-call/non-reentrant; both call sites one-shot, build-exclusive).
         * [L3/PROXY-ldf inference] st8/out8 move from stack to .bss; BOTH reside in L1 Block-0
         * (stack = RESERVE_EXPAND remainder), so net Block-0 demand is ~unchanged -- the gain is
         * converting a silent runtime stack-overflow into a link-time-checked .bss placement. If total
         * L1 Block-0 demand exceeds capacity the LINK fails loudly (caught pre-board). Confirm via
         * .map L1 Block-0 occupancy + on-board SP-vs-ldf_stack symbols. If the link DOES fail, the
         * real fix is moving these statics to L2/L3 via #pragma section (CROSS_BUILD_NOTES.md:61) --
         * escalate, do not shrink the algorithm. Logic/buffers/values: host S2 CRC 0x90556BC7
         * re-verified byte-identical on patched source. */
        static Tfb8State st8;
        TreeChannelState ana, syn;
        int32_t sb0[BENCH_FRAME/8], sb1[BENCH_FRAME/4], sb2[BENCH_FRAME/2], sb3[BENCH_FRAME];
        int32_t out1[BENCH_FRAME];
        tfb_channel_init(&ana); tfb_channel_init(&syn); tfb8_init(&st8);
        /* 热身 4 帧（预热 cache/状态） */
        for(int f=0; f<4; f++){ tfb_analyze(&ana,&CHIRP_INPUT[f*BENCH_FRAME],BENCH_FRAME,sb0,sb1,sb2,sb3);
            tfb_synthesize(&syn,sb0,sb1,sb2,sb3,BENCH_FRAME,out1); }
        /* 单通道 analyze 稳态 */
        uint32_t t0=BENCH_CYC();
        tfb_analyze(&ana,&CHIRP_INPUT[4*BENCH_FRAME],BENCH_FRAME,sb0,sb1,sb2,sb3);
        uint32_t t1=BENCH_CYC();
        tfb_synthesize(&syn,sb0,sb1,sb2,sb3,BENCH_FRAME,out1);
        uint32_t t2=BENCH_CYC();
        /* 8ch 满负载: 8 路同信号, 8 条独立链 analyze->synthesize.
         * F5-B 语义变更: cyc_8ch_frame 现在量的是「8 条独立链」一帧 wall cycle,
         * 不再含跨通道数字求和(求和节点已删, 见 tfb_8ch.c). 旧值含 8x 求和+饱和钳位
         * 的 WCET 路径; 新值 = 纯 8x (analyze+synthesize), 无 acc 累加/无 w_add_i32.
         * 8 路同信号 -> 8 个相同输出(各自独立链), 不触发任何跨通道饱和. out 现 8 行. */
        for(int i=0;i<BENCH_FRAME;i++) for(int c=0;c<TFB8_NCH;c++) s_in8[c][i]=CHIRP_INPUT[4*BENCH_FRAME+i];
        static int32_t out8[TFB8_NCH][BENCH_FRAME];   /* F7-FIX2: static (off stack, see note above) */
        uint32_t t3=BENCH_CYC();
        tfb8_process(&st8, s_in8, BENCH_FRAME, out8);
        uint32_t t4=BENCH_CYC();
        r->cyc_analyze_1ch = t1-t0;
        r->cyc_synth_1ch   = t2-t1;
        r->cyc_8ch_frame   = t4-t3;
        double fpf = (double)BENCH_FS/BENCH_FRAME;          /* 帧/秒 = 750 */
        r->mcps_8ch     = (double)r->cyc_8ch_frame * fpf / 1e6;
        r->mcps_16ch_est= (double)(r->cyc_8ch_frame + 8u*r->cyc_analyze_1ch) * fpf / 1e6;
    }
    return r->bitexact_pass;
}

#ifdef BENCH_HOST_MAIN
#include <stdio.h>
int main(void){
    BenchResult r; bench_run(&r);
#ifdef TFB_DISABLE_SAT
    const char* tag="unsat";
#else
    const char* tag="sat";
#endif
    printf("==== bench_harness host 预验 [build=%s] [L2 host 预验] ====\n", tag);
    printf("[S2 bit-exact] CRC32=0x%08X  golden=0x%08X  crc_match=%d  spot_match=%d -> %s\n",
           r.crc32, (uint32_t)GOLDEN_CRC32, r.crc_match, r.spot_match,
           r.bitexact_pass? "PASS":"FAIL");
    printf("[S3 cycle] cyc_valid=%d (host=0 占位无意义; target 真CCNT=1)\n", r.cyc_valid);
    printf("   analyze_1ch=%u  synth_1ch=%u  8ch_frame=%u (host clock 占位)\n",
           r.cyc_analyze_1ch, r.cyc_synth_1ch, r.cyc_8ch_frame);
    printf("   [换算式 target 用] MCPS_8ch=cyc8*750/1e6 ; MCPS_16ch=(cyc8+8*analyze)*750/1e6\n");
    printf("==== 总结: bit-exact %s（cycle 数值待 target 真 CCNT [L1/EZKIT]）====\n",
           r.bitexact_pass?"PASS":"FAIL");
    return r.bitexact_pass?0:1;
}
#endif
