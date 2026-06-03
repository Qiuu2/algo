/**
 * @file    fira_tree.h
 * @brief   【草案·未编译·真 Legacy API·F2-F7 待台架】
 *          FIRA 硬件加速版 4 子带 dyadic 树形半带 FIR（Split-Task 编排接口）
 *
 * ┌───────────────────────────────────────────────────────────────────────┐
 * │ 🔴 诚实状态标注（硬约束，禁删）                                          │
 * │  本文件为 **草案代码**：本机无 SHARC 工具链（CCES 仅 ARM cortex-a5）+   │
 * │  无 FIRA 硬件 → **无法在本机编译 / 板上验证**。                          │
 * │  - adi_fir_* API = **真 Legacy 签名**（归档头                           │
 * │    knowledge_base/ezkit/bsp/fira_headers/adi_fir_legacy_2156x.h，       │
 * │    10 函数 + ADI_FIR_CHANNEL_INFO + 枚举，F1/G1 闭合 DOC-S4-FIRA-F1-01）│
 * │  - 生命周期顺序仿官方 Legacy 实例                                       │
 * │    .../FIR_Multi_Channel_Processing/src/FIR_Multi_Channel_Processing.c  │
 * │    （下称 MCP.c）:243-285。                                             │
 * │  - 每个未验证假设以 [ASSUME] / [L1/EZKIT] 显式标注。                     │
 * │  - 🚫 绝不声称"已编译 / 已 bit-exact 通过 / 已实测 cycle"。              │
 * │  - 真编译 + 板上 R14 bit-exact(crc==0x90556BC7) + cycle 实测 = 台架回填。│
 * └───────────────────────────────────────────────────────────────────────┘
 *
 * 模式：**LEGACY**（F1 锁定，DOC-S4-FIRA-F1-01 §2）。
 * 定点：**Path B 运行时**——CreateTask 后、QueueTask 前调
 *   adi_fir_FixedPointEnable(hTask, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER)；
 *   **不改 config 头**（adi_fir_config_2156x.h 保持 ADI_FIR_FIXED_POINT_MODE=0，
 *   FixedPointEnable .c 直写 FIRCTL1 TC+FXD 位，自足；改 config 头前按红线报 CTO）。
 * 抽取：ADI_FIR_CHANNEL_INFO.eSampling=ADI_FIR_SAMPLING_DECIMATION + nSamplingRatio（per-channel）。
 * 完成：Legacy 回调 ADI_FIR_EVENT_ALL_CHANNEL_DONE；主等 FIRTaskDoneCount<N_TASKS（MCP.c:282）。
 *
 * 实现说明：DOC-S4-FIRA-IMPL-01（FIRA_IMPL.md，本目录）。
 *
 * Split-Task 模型（FIRA_IMPL.md §2 / EE408 Split_Task 例程）：
 *   - FIRA（硬件）：各级半带卷积段（DECIMATION r=2 / INTERPOLATION r=2）= adi_fir channel。
 *   - 留核（software，复用 tree_filterbank.c 原语）：detail 残差减 / 合成加 /
 *     Q31 饱和钳位 / ×2 内插增益 / 8ch broadside 求和。
 *   ⇒ 不是"整条链甩给 FIRA"，核仍负责所有非 MAC 的定点语义。
 *
 * 🔴 R14 命门（FIRA_IMPL.md §3，HIGH）：我方 = signed-fractional Q15×Q31；FIRA 定点
 *   输入格式枚举只有 UNSIGNED/SIGNED_INTEGER（legacy 头:42-43）。Q 格式转换点见
 *   FIRA_IMPL.md §3，**逐条标"bit 偏差高发、必上板逐位"**；桌面无法坐实。
 *
 * 红线（铁律八 / C9）：R14 板上 crc==0x90556BC7 通过前，FIRA 收益/裕量不得写进
 *   任何选型依据（违者 BLOCKER）。本文件不含任何性能数。
 */
#ifndef ITC_FIRA_TREE_H
#define ITC_FIRA_TREE_H

#include <stdint.h>
#include "tree_filterbank.h"   /* 复用 HbFirState/TreeChannelState 维度 + 子带布局口径 */

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================
 * 段枚举：每通道半带段（FIRA_IMPL.md §2，C 实际口径）。
 *   分析侧：ana_dec[0..2]（DECIMATION r=2）+ ana_int[0..2]（INTERPOLATION r=2，求 detail）
 *   合成侧：syn_int[0..2]（INTERPOLATION r=2）
 * ============================================================ */
#define FIRA_HB_TAPS            TFB_HB_TAPS   /* 63，共享半带原型 */
#define FIRA_SEGS_PER_CHAN      9             /* 3 dec + 3 ana_int + 3 syn_int */
#define FIRA_RATIO              2             /* 抽取/插值比，整数 */

/* 段类别（决定 eSampling 字段：DECIMATION vs INTERPOLATION） */
typedef enum {
    FIRA_SEG_DEC = 0,   /* hb_decimate2 等价：DECIMATION，取偶相位（R14-6 命门） */
    FIRA_SEG_INT = 1    /* hb_interp2  等价：INTERPOLATION，×2 增益核内补（R14-5 命门） */
} FiraSegKind;

/* ============================================================
 * 真 Legacy 头接入（F1 闭合）
 * ------------------------------------------------------------
 * 🔴 [L1/EZKIT]：本机无 21569 SHARC 侧驱动头（CCES 仅 ARM v2）。台架在 CCES SHARC
 *   工程里 #include 真 BSP 头（即归档件 adi_fir_legacy_2156x.h 对应的安装头
 *   <drivers/fir/adi_fir.h>）并定义 FIRA_USE_REAL_ADI_FIR_HEADER。
 *   归档头已给出真签名（10 函数 + ADI_FIR_CHANNEL_INFO + 枚举），草案据此编排；
 *   ADI_CALLBACK / ADI_CACHE_LINE_LENGTH 等基础类型由 BSP 平台头提供（台架自带）。
 * ============================================================ */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
#include <drivers/fir/adi_fir.h>   /* [L1/EZKIT] 真 Legacy 头（= 归档 adi_fir_legacy_2156x.h） */
#endif

/* ============================================================
 * FIRA 树通道状态（草案）：每通道段的元数据（窗口/类别）。
 *   实际缓冲（系数/输入延迟线/输出）+ TaskMemory 由调用者静态分配（F2 模板示范）。
 * ============================================================ */
typedef struct {
    FiraSegKind kind[FIRA_SEGS_PER_CHAN];
    uint16_t    window[FIRA_SEGS_PER_CHAN];   /* 输出样本数（= frame/2^level） */
    uint8_t     initialized;
} FiraChannelState;

/* ============================================================
 * 系数注入（F3）：把共享 63-tap Q15 半带原型符号扩展冻结为 FIRA 32-bit 容器。
 *   🔴 R14-2：Q15→32-bit 符号扩展 + 小数点语义保持，台架逐位核实。
 *   coef32 = fir_coeffs_q31.h 生成的冻结常量数组（不上板重算，同源纪律）。
 * ============================================================ */
void fira_tree_set_coeffs(const int32_t *hb_coef_fira32, uint16_t ntaps);

/** @brief 初始化一个 FIRA 树通道（清状态 + 填段元数据）。 */
void fira_channel_init(FiraChannelState *ch, uint16_t frame);

/* ============================================================
 * F2-F4 单通道台架起步模板：1 个 ADI_FIR_CHANNEL_INFO（真 Legacy 字段）走完整
 *   Open → RegisterCallback → CreateTask → FixedPointEnable(SIGNED) → QueueTask →
 *   等 ALL_CHANNEL_DONE → Close 序列。台架第一步就跑这一个（验生命周期 + 定点 + 相位）。
 *   返回 0 成功；非 0 = adi_fir_* 失败步骤码（台架检查 ADI_FIR_RESULT）。
 *   🔴 [L1/EZKIT]：真 adi_fir_* 行为待台架；草案默认构建不接 FIRA（返回 -1）。
 * ============================================================ */
int fira_single_channel_template(const int32_t *in, uint16_t in_count,
                                 int32_t *out, uint16_t out_count, uint16_t ntaps);

/* ============================================================
 * F2/F4：一次性设置任务（Open → RegisterCallback → CreateTask → FixedPointEnable）。
 *   实时模式：CreateTask + FixedPointEnable 只在 init 调一次，不进帧预算。
 *   🔴 [L1/EZKIT]：真 adi_fir_* 行为待台架。
 * ============================================================ */
int fira_tree_setup(void);

/* ============================================================
 * 帧级 Split-Task 编排（草案）：接口刻意与 tfb_analyze/tfb_synthesize **同签名**，
 *   便于 bench_harness / fira_regression 直接替换卷积段做 CRC 比对（crc==0x90556BC7）。
 * ============================================================ */
void fira_tfb_analyze(FiraChannelState *ch, const int32_t *in, uint16_t frame,
                      int32_t *sb0, int32_t *sb1, int32_t *sb2, int32_t *sb3);

void fira_tfb_synthesize(FiraChannelState *ch,
                         const int32_t *sb0, const int32_t *sb1,
                         const int32_t *sb2, const int32_t *sb3,
                         uint16_t frame, int32_t *out);

/** @brief 退出时释放 FIRA 设备（adi_fir_Close）。实时应用退出调一次。 */
void fira_tree_teardown(void);

#ifdef __cplusplus
}
#endif
#endif /* ITC_FIRA_TREE_H */
