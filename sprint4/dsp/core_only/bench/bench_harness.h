/**
 * @file    bench_harness.h
 * @brief   内存向量法 S2-S5 harness 接口（嫁接进 ADI LED 脚手架处理槽）
 *
 * 设计：不接 codec/A2B/DMA；输入在内存生成（chirp 确定性）→ 跑算法 →
 *       输出落已知内存 → S2 bit-exact(CRC32+spot vs 独立 golden_ref.h) +
 *       S3 cycle(CCNT, sat 激励 WCET)。纯算法、无 ADI 依赖 → 可 host 预验。
 */
#ifndef ITC_BENCH_HARNESS_H
#define ITC_BENCH_HARNESS_H
#include <stdint.h>

typedef struct {
    /* S2 bit-exact（CRC 在 host 与 target 均有意义；数值跨架构一致即 bit-exact） */
    uint32_t crc32;            /* 本次运行 65536 样本输出的 CRC32 */
    int      crc_match;        /* == GOLDEN_CRC32 ? 1:0 */
    int      spot_match;       /* 64 spot 逐位一致 ? 1:0 */
    int      bitexact_pass;    /* crc_match && spot_match */
    /* S3-S5 cycle（host=占位无意义[L2]；target=真 CCNT[L1/EZKIT]） */
    uint32_t cyc_analyze_1ch;  /* 单通道 tfb_analyze 每帧 cycle */
    uint32_t cyc_synth_1ch;    /* 单通道 tfb_synthesize 每帧 cycle */
    uint32_t cyc_8ch_frame;    /* tfb8_process 每帧 cycle（8 条独立链, 无跨通道求和; F5-B 后语义=8x analyze+synth） */
    /* 派生（换算式见 bench_harness.c；CCLK 实测填入 cclk_hz 后算） */
    double   mcps_8ch;         /* = cyc_8ch_frame * (FS/FRAME) / 1e6 */
    double   mcps_16ch_est;    /* = (cyc_8ch_frame + 8*cyc_analyze_1ch)*(FS/FRAME)/1e6 */
    int      cyc_valid;        /* 1=target 真 CCNT；0=host 占位 */
} BenchResult;

/* FS/FRAME 与 golden 同口径 */
#define BENCH_FS     48000
#define BENCH_FRAME  64
#define BENCH_NFR    1024

/* 跑全套 harness，填 BenchResult。返回 bitexact_pass。 */
int bench_run(BenchResult *r);

#endif /* ITC_BENCH_HARNESS_H */
