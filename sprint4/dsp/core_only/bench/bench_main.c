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

/* harness 结果落已知内存，供 emulator / 后续部署读取（volatile 防优化掉） */
volatile BenchResult g_bench_result;

/* ---- target CCNT 读取（【待 CTO 台架回填】） ----
 * 21569 SHARC+ 自由运行 cycle 计数器。依 SHARC+ Core Programming Reference 实际寄存器/内建：
 *   候选：__builtin_emuclk()  或  读 EMUCLK/CCNT 寄存器（def21569.h）。
 * 回填前返回 0 → bench_harness 标 cyc_valid=1 但数值待确认；台架确认寄存器名后实现此函数。 */
#ifdef TARGET_SHARC
uint32_t bench_cyc_target(void)
{
    /* TODO[台架回填]: return (uint32_t)__builtin_emuclk();  // 或读 *pREG_..._CCNT */
    return 0u;   /* 占位：回填真 CCNT 前 cycle 数无效 */
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

    /* ---- 我方算法嫁接：跑 core-only S2-S5 harness ---- */
    bench_run((BenchResult *)&g_bench_result);

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
