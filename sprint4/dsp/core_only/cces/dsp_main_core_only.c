/**
 * @file    dsp_main_core_only.c
 * @brief   CCES/ADSP-21569 core-only 入口骨架（S1 结构占位; 板上 build 待 IDE 配置）
 *
 * ⚠️ 本文件是 S1 工程结构骨架。算法层只挂已验证定点核 tree_filterbank.c
 *    (md5 verbatim) + tfb_8ch.c 包裹 + fir_coeffs_hb63.h 冻结系数。
 *    🚫 不挂 sprint3 骨架的 float dyadic_analysis.c / bf_broadside.c (计划 §3 G4)。
 *    🚫 不接 sprint2/dsp/fir_coeffs.h (437-tap 废核, 计划 §2 G3)。
 *
 * S1 板上 build 还需 IDE/工程配置的项 (本轮只搭结构, 不真跑 CCES)，见
 *    S0S1_report.md「S1 板上 build 待 IDE 项」一节:
 *      - .ldf 内存布局 (热点 state[63] -> L1; 系数 -> L2; 大局部数组 -> section)
 *      - system.svc / startup / clock (CCLK=1GHz) 配置
 *      - def21569.h 抽 CCNT/EMUCLK 寄存器名 (S3 cycle 计数填实)
 *      - SPORT/DMA/codec (端到端 S8, core-only 首测不依赖)
 *
 * core-only 首测路径 (S2 板上 bit-exact): 片内喂 tree_io_*.csv 的 x 序列,
 *    单通道逐帧 tfb_analyze->tfb_synthesize, 整数域逐位对 golden y[]。
 *    host 侧已预验 (本轮 host_bitexact.c, [L2 host 预验])。
 */
#include "tree_filterbank.h"
#include "tfb_8ch.h"
#include "fir_coeffs_hb63.h"

/* 8ch broadside 包裹状态 (静态分配, 见计划 §1/§4 G5 .ldf -> L1/section) */
static Tfb8State g_tfb8;

/* 上电初始化: 注入冻结 63-tap Q15 系数 (全局共享; 8ch 无需各自喂) */
void core_only_init(void)
{
    tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);   /* tree_filterbank.c:68 */
    tfb8_init(&g_tfb8);
}

/* 帧回调 (S4-S5 cycle 计数时用 TFB_LOAD_START/STOP 包住; 见 tree_filterbank.h:74-93)
 * F5-B: 8-in-8-out (8 路独立链, 无数字求和); out 现为 8 行 -> 8 DAC (声学叠加). */
void core_only_frame(const int32_t in[TFB8_NCH][TFB8_FRAME], int32_t out[TFB8_NCH][TFB8_FRAME])
{
    TFB_LOAD_START();
    tfb8_process(&g_tfb8, in, TFB8_FRAME, out);
    TFB_LOAD_STOP();
}

/* S1 仅验证编译/链接; 真正 main 由 CCES BSP 模板提供 (system.svc 生成)。 */
