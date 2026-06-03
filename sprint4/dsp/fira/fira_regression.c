/**
 * @file    fira_regression.c
 * @brief   【草案·未编译·真 Legacy API·待台架】F7 R14 回归 harness：FIRA 路径输出
 *          → CRC32 + spot vs core-only golden（0x90556BC7）。复用 bench/golden_ref.h 同基准。
 *
 * ┌───────────────────────────────────────────────────────────────────────┐
 * │ 🔴 诚实状态：本机无 FIRA 硬件 → 本文件**无法产生有效 FIRA 输出**。       │
 * │  它定义"台架上怎么比"——把 fira_tfb_analyze/synthesize 的输出喂进与       │
 * │  bench_harness.c 完全相同的 CRC32 + GOLDEN_SPOT 比对。判据二值：          │
 * │  crc==0x90556BC7 且 64 spot 全等 → R14 PASS（FIRA 版数值等价核版）。      │
 * │  🚫 桌面跑不出真值；R14 [L1] 由台架板上回填（plan §5.3 step6）。          │
 * └───────────────────────────────────────────────────────────────────────┘
 *
 * 接入方式（FIRA_IMPL.md §4 + 任务要点 2）：FIRA 版**替换 bench_harness 的卷积段**——
 *   即把 tfb_analyze/tfb_synthesize 换成 fira_tfb_analyze/fira_tfb_synthesize，
 *   输出仍走同一 crc32_buf + GOLDEN_CRC32/GOLDEN_SPOT 比对。其余（输入冻结 chirp、
 *   sat/unsat 双 build）完全沿用 bench_harness.c，不改 golden（否则失对照基准）。
 *
 * 台架先决：F2 先跑 fira_single_channel_template()（单段完整 Legacy 生命周期 +
 *   Path B 运行时 FixedPointEnable(SIGNED)）验通，再扩到本全链回归（F4→F7）。
 *
 * 🔴 桌面构建安全：fira_tree_setup()/fira_single_channel_template() 桌面返回 -1，
 *   本函数据此**直接返回 0**（FAIL，提示"非台架，结果无效"），**绝不冒充** R14 通过。
 */

#include "fira_tree.h"
/* ⚠️ 台架 CCES 工程须配 -I.../sprint4/dsp/core_only/bench（下三头实体在 core_only/bench/，
 *    裸文件名靠 -I 解析；critic MINOR，否则 F2 编译报 not found） */
#include "golden_ref.h"     /* 复用 core-only golden（0x90556BC7），勿改 */
#include "bench_harness.h"  /* BENCH_FRAME/NFR/FS 同口径 */
#include "chirp_input.h"    /* 冻结 chirp 输入（同 R14 输入，§5.3 step2） */
#include <string.h>
#include <stdint.h>

/* CRC32 IEEE 802.3 —— 与 bench_harness.c:30 / gen_golden.c 逐位同算法（勿改） */
static uint32_t crc32_buf(const int32_t *d, int n)
{
    uint32_t c = 0xFFFFFFFFu;
    for (int i = 0; i < n; i++) {
        uint32_t v = (uint32_t)d[i];
        for (int b = 0; b < 4; b++) {
            uint8_t by = (uint8_t)(v >> (8 * b));
            c ^= by;
            for (int k = 0; k < 8; k++) c = (c & 1) ? (c >> 1) ^ 0xEDB88320u : (c >> 1);
        }
    }
    return c ^ 0xFFFFFFFFu;
}

static int32_t s_y_fira[BENCH_FRAME * BENCH_NFR];

/**
 * F7 回归：单通道 FIRA 链 65536 样本 → CRC32 + spot vs golden。
 *  @param[out] out_crc  FIRA 版 CRC32（台架抓取）
 *  @return 1 = R14 PASS（crc==0x90556BC7 且 64 spot 全等）；0 = FAIL（定位 plan §4）
 *
 * 🔴 [L1/EZKIT] 必须在板上跑（含真 FIRA DMA / 80-bit MR / 相位 / cache）。
 *   桌面无 FIRA → fira_tfb_* 在草案构建下为占位（不接 FIRA 段）→ 故本函数
 *   **桌面调用结果无意义**，仅 plumbing。禁把桌面结果当 R14 通过。
 */
int fira_r14_regression(uint32_t *out_crc)
{
    FiraChannelState ana, syn;
    int32_t sb0[BENCH_FRAME/8], sb1[BENCH_FRAME/4], sb2[BENCH_FRAME/2], sb3[BENCH_FRAME];

    /* 🔴 [L1/EZKIT] 台架：先 fira_tree_setup()（Open/CreateTask）。桌面返回 -1（禁用）。 */
    if (fira_tree_setup() != 0) {
        /* 桌面/非目标平台：不冒充验证，直接返回 0（FAIL→提示"非台架，结果无效"）。 */
        if (out_crc) *out_crc = 0u;
        return 0;
    }

    fira_channel_init(&ana, BENCH_FRAME);
    fira_channel_init(&syn, BENCH_FRAME);

    for (int f = 0; f < BENCH_NFR; f++) {
        fira_tfb_analyze(&ana, &CHIRP_INPUT[f * BENCH_FRAME], BENCH_FRAME,
                         sb0, sb1, sb2, sb3);
        fira_tfb_synthesize(&syn, sb0, sb1, sb2, sb3, BENCH_FRAME,
                            &s_y_fira[f * BENCH_FRAME]);
    }

    uint32_t crc = crc32_buf(s_y_fira, BENCH_FRAME * BENCH_NFR);
    if (out_crc) *out_crc = crc;

    int crc_match = (crc == GOLDEN_CRC32) ? 1 : 0;
    int spot_match = 1;
    for (int i = 0; i < GOLDEN_NSPOT; i++) {
        if (s_y_fira[i * GOLDEN_SPOT_STRIDE] != GOLDEN_SPOT[i]) { spot_match = 0; break; }
    }

    fira_tree_teardown();
    return crc_match && spot_match;   /* 1 = R14 PASS（FIRA 版逐位等价 core golden） */
}

/* ============================================================
 * cycle 方案（plan §5.1 F8）：FIRA 版 cyc_8ch_frame 用现成 CCNT（bench_cyc_target）
 *   量 → 对比纯核 1,006,935 → 算新裕量 + 16ch deadline。
 * 🔴 [L1/EZKIT] 待台架；🔴 铁律八/C9：R14（fira_r14_regression==1，板上）通过前，
 *   cycle/裕量收益**不得写进任何选型依据**（违者 BLOCKER）。本文件不含任何收益数。
 * ============================================================ */
