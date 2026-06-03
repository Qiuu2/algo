/**
 * @file    bench_main.c
 * @brief   嫁接 main（target-only）：ADI LED 脚手架 boot + 我方 harness 处理槽
 *
 * 嫁接边界（红线）：
 *   - ADI 底座（保留，不改）：adi_initComponents()（时钟/电源/pinmux/sru，来自
 *     ADSP21569_LED 例程 system/startup_ldf + adi_initialize）；GPIO LED（pass/fail 可视）。
 *   - 我方算法（嫁接）：bench_run() 跑 core-only（verbatim tree_filterbank.c + tfb_8ch + hb63）。
 *   - 🚫 不挂 float 层 / 🚫 不接例程系数/437-tap / 🚫 不接 codec/A2B/DMA（内存向量法）。
 *
 * 用法：在 ADSP21569_LED 工程基础上，把本文件替换原 src/main.c（保留 system/ 全板 init），
 *       加入 ../src/tree_filterbank.c, ../src/tfb_8ch.c, bench_harness.c；include 路径加
 *       ../src ../include 与本目录；app.ldf 按 GRAFT_PLAN §.ldf 增量放置热点。
 * 编译：CCES -proc ADSP-21569 -DTARGET_SHARC（目标 0 错 0 警告 = [L1/CCES-target] 待台架）。
 *
 * 结果读取：g_bench_result 落已知内存，CCES emulator 暂停后查看（Expressions 窗口）；
 *           LED：bit-exact PASS → LED 常亮；FAIL → 快闪。
 */
#include "main.h"                 /* ADI LED 例程头（adi_gpio / adi_initComponents 声明） */
#include "bench_harness.h"
#include <stdint.h>
#include <time.h>                 /* clock() —— CCES SHARC 上返回 CCLK 周期数 */

/* harness 结果落已知内存，供 emulator / 后续部署读取（volatile 防优化掉） */
volatile BenchResult g_bench_result;
volatile uint32_t    g_ccnt_selftest;   /* CCNT 自检结果（已知循环 cycle，emulator 查） */

#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
#include "fira_tree.h"                       /* F2 FIRA 冒烟（仅 FIRA 接入时编入） */
extern volatile uint32_t g_FIRTaskDoneCount; /* fira_tree.c 定义（ALL_CHANNEL_DONE 回调置位） */
volatile int g_fira_f2_rc = -99;             /* F2 单通道模板返回码（emulator 查；0=PASS） */
#endif

/* ---- target CCNT 读取（真 CCLK 周期） ----
 * 出处：ADI 官方 ADSP-21569 例程 FIR_Throughput_21569.c:18-20,42,86-89 用标准 C `clock()`
 *   量 CCLK cycles（注释 line 4 "measure the number of CCLK cycles ... on ADSP-21569"）；
 *   Pipelined / *_Driver_Benchmark 例程一致用 clock()。底层 = REGF_EMUCLK 32-bit 核周期
 *   计数器（SHARC+ Core Programming Reference §29，用户空间只读，计核时钟周期）。
 * 位宽/回绕：clock_t 32-bit（例程以 %d 打印）；@1GHz 约 4.29s 回绕。per-frame 测量(<2ms,
 *   ~1.3M cycles) 远不回绕；bench_harness 用无符号差 end-start，单次回绕自动正确。长累计测量
 *   需 EMUCLK2（与 EMUCLK 合成 64-bit）或逐帧累加——本 harness 逐帧小区间，无需。 */
#ifdef TARGET_SHARC
uint32_t bench_cyc_target(void)
{
    return (uint32_t)clock();   /* CCES SHARC：clock() = CCLK 周期（同 ADI 21569 例程口径） */
}
#endif

void main(void)
{
    /* ---- ADI 底座：全板 init（时钟/电源/pinmux/sru），保留不改 ---- */
    adi_initComponents();

    /* LED 方向（pass/fail 可视指示，沿用 LED 例程 PC_01..03） */
    adi_gpio_SetDirection(ADI_GPIO_PORT_C, ADI_GPIO_PIN_1, ADI_GPIO_DIRECTION_OUTPUT);
    adi_gpio_SetDirection(ADI_GPIO_PORT_C, ADI_GPIO_PIN_2, ADI_GPIO_DIRECTION_OUTPUT);
    adi_gpio_SetDirection(ADI_GPIO_PORT_C, ADI_GPIO_PIN_3, ADI_GPIO_DIRECTION_OUTPUT);

    /* ---- CCNT 自检（验证 clock() 读真周期；已知 1,000,000 次 volatile 循环对照） ----
     * emulator 查 g_ccnt_selftest：应 >0 且 ≈ 1e6 × 每迭代周期（量级数 M cycles）；
     * =0 或乱跳 → clock() 未读到真 CCNT，先排查再信 cyc_8ch_frame。 */
    {
        volatile uint32_t k; uint32_t a, b;
        a = bench_cyc_target();
        for (k = 0u; k < 1000000u; k++) { }
        b = bench_cyc_target();
        g_ccnt_selftest = b - a;   /* 已知循环 cycle 对照 */
    }

    /* ---- 我方算法嫁接：跑 core-only S2-S5 harness（F0 基准，保留） ---- */
    bench_run((BenchResult *)&g_bench_result);

#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    /* ---- F2 FIRA 冒烟：单通道完整 Legacy 生命周期 + Path B 定点（任意系数）----
     * F2 判据 = 管路 PASS：g_fira_f2_rc==0（6 步全 SUCCESS）+ g_FIRTaskDoneCount==1（回调进）。
     * ⚠️ rc==0 不证 SIGNED 真生效（adi_fir_legacy_2156x.c：FixedPointEnable 非 RUNNING 必返
     *    SUCCESS、与 config 无关）→ G2 真闭合在 F4 逐位比 golden，非 F2。
     * 失败码：1=Open 2=RegisterCallback 3=CreateTask
     *         4=FixedPointEnable（仅 task==RUNNING 才非 SUCCESS = 调用顺序 bug，查顺序，**勿动 config**）
     *         5=QueueTask 6=Close / -1=未定义真头 / -2=系数或 buf 空。 */
    {
        static int32_t s_f2_coef[63];            /* F2 任意系数（仅冒烟，非真系数；F3 换真） */
        static int32_t s_f2_in[63 + 64 - 1];     /* in_count = ntaps+out_count-1 = 126 */
        static int32_t s_f2_out[64];             /* out_count = 64（window） */
        unsigned i;
        for (i = 0u; i < 63u; i++) s_f2_coef[i] = 0;
        s_f2_coef[31] = (int32_t)0x40000000;     /* 中心抽头（任意非零） */
        for (i = 0u; i < (63u + 64u - 1u); i++) s_f2_in[i] = (int32_t)((uint32_t)i << 20);
        fira_tree_set_coeffs(s_f2_coef, 63u);
        g_fira_f2_rc = fira_single_channel_template(s_f2_in, 63u + 64u - 1u,
                                                    s_f2_out, 64u, 63u);
        /* ↑ 在此设断点查 g_fira_f2_rc / g_FIRTaskDoneCount（F2 判据见 DOC-S4-FIRA-IMPL-01） */
    }
#endif

    /* ---- 在此设断点，emulator 查 g_bench_result：
     *   .bitexact_pass / .crc32(应=0x90556BC7) / .cyc_8ch_frame / .mcps_8ch / .mcps_16ch_est
     *   → S2 bit-exact [L1/EZKIT] + S3-S5 cycle/MCPS + R1 判据（WCET<1.333ms 且 裕量≥10×） ---- */

    /* LED 指示：PASS 常亮 / FAIL 快闪 */
    if (g_bench_result.bitexact_pass) {
        adi_gpio_Set(ADI_GPIO_PORT_C, ADI_GPIO_PIN_1);   /* 常亮 */
        while (1) { /* idle，保持指示 */ }
    } else {
        volatile unsigned i;
        while (1) {
            adi_gpio_Toggle(ADI_GPIO_PORT_C, ADI_GPIO_PIN_1);
            for (i = 0; i < 0x400000u; i++) { }          /* 快闪 = FAIL */
        }
    }
}
