/**
 * @file    fira_tree.h
 * @brief   【草案·未编译·API 仿例程·待台架编译+逐位验证】
 *          FIRA 硬件加速版 4 子带 dyadic 树形半带 FIR（Split-Task 编排接口）
 *
 * ┌───────────────────────────────────────────────────────────────────────┐
 * │ 🔴 诚实状态标注（硬约束，禁删）                                          │
 * │  本文件为 **草案代码**：本机无 SHARC 工具链（CCES 仅 ARM cortex-a5）+   │
 * │  无 FIRA 硬件 → **无法在本机编译 / 板上验证**。                          │
 * │  - adi_fir_* API 用法严格仿例程                                         │
 * │    knowledge_base/.../FIR_Multi_Channel_Processing.c（下称 MCP.c）。     │
 * │  - 每个未验证假设以 [ASSUME] / [proxy] / [L1/EZKIT] 显式标注。           │
 * │  - 🚫 绝不声称"已编译 / 已 bit-exact 通过 / 已实测 cycle"。              │
 * │  - 真编译 + 板上 R14 bit-exact(crc==0x90556BC7) + cycle 实测 = 台架回填。│
 * └───────────────────────────────────────────────────────────────────────┘
 *
 * 蓝图：DOC-S4-FIRA-PLAN-01（sprint4/dsp/fira_integration_plan.md），F0–F8。
 * 实现说明：DOC-S4-FIRA-IMPL-01（FIRA_IMPL.md，本目录）。
 *
 * Split-Task 模型（plan §3.2 / EE408 eenote:420-435）：
 *   - FIRA（硬件）：各级半带卷积段（dec2 / interp2）= adi_fir channel（ACM）。
 *   - 留核（software，复用 tree_filterbank.c 原语）：detail 残差减 / 合成加 /
 *     Q31 饱和钳位 / ×2 内插增益 / 8ch broadside 求和。
 *   ⇒ 不是"整条链甩给 FIRA"，核仍负责所有非 MAC 的定点语义。
 *
 * 🔴 R14 命门（plan §4.3，HIGH）：我方 = signed-fractional Q15×Q31；FIRA 定点
 *   格式枚举只有 UNSIGNED/SIGNED_INTEGER（MCP.c:141）。Q 格式转换点见 FIRA_IMPL.md
 *   §R14，**逐条标"bit 偏差高发、必上板逐位"**；桌面无法坐实。
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
 * 段枚举：每通道 9 个 63-tap 半带段（plan §3.3，C 实际口径）。
 *   分析侧：ana_dec[0..2]（DECIMATION r=2）+ ana_int[0..2]（INTERPOLATION r=2，求 detail）
 *   合成侧：syn_int[0..2]（INTERPOLATION r=2）
 * ============================================================ */
#define FIRA_HB_TAPS            TFB_HB_TAPS   /* 63，共享半带原型（plan §3.1） */
#define FIRA_SEGS_PER_CHAN      9             /* 3 dec + 3 ana_int + 3 syn_int */
#define FIRA_RATIO              2             /* 抽取/插值比，整数（hwref:75697-98 约束满足） */

/* 段类别（决定 eSampling 字段：DECIMATION vs INTERPOLATION） */
typedef enum {
    FIRA_SEG_DEC = 0,   /* hb_decimate2 等价：DECIMATION，取偶相位（§4.6 命门） */
    FIRA_SEG_INT = 1    /* hb_interp2  等价：INTERPOLATION，×2 增益核内补（§4.5 命门） */
} FiraSegKind;

/* ============================================================
 * [proxy] 平台占位类型 / 常量
 * ------------------------------------------------------------
 * 🔴 [proxy][L1/EZKIT]：本机无 21569 SHARC 侧 adi_fir_2156x.h（CCES 仅 ARM v2 头）。
 *   下列类型在台架（F1：装 21569 BSP）用真 <drivers/fir/adi_fir.h> 的定义替换。
 *   草案编译期用占位 typedef 仅为表达结构，**不代表真签名已验证**。
 * ============================================================ */
#ifndef FIRA_USE_REAL_ADI_FIR_HEADER
/* —— 占位：台架替换为 #include <drivers/fir/adi_fir.h> —— */
typedef void*   ADI_FIR_DEV_HANDLE;    /* [proxy] 真值见 BSP 头 */
typedef void*   ADI_FIR_TASK_HANDLE;   /* [proxy] */
/* TaskMemory 字节数：MCP.c 用宏 FIR_MEM_SIZE(nCh)（BSP 头提供）。台架替换。 */
#define FIRA_TASKMEM_BYTES(nCh)  (4096u * (nCh))   /* [ASSUME] 占位上界，台架按真 FIR_MEM_SIZE() 核实 */
#endif

/* ============================================================
 * FIRA 树通道状态（草案）：每通道 9 段的缓冲布局描述 + TCB 内存。
 *   实际缓冲（系数/输入延迟线/输出）由调用者静态分配并经 fira_tree_setup 绑定。
 * ============================================================ */
typedef struct {
    /* 每段一个 ADI_FIR_CHANNEL_INFO（在 .c 内构造；此处仅记录段元数据）。 */
    FiraSegKind kind[FIRA_SEGS_PER_CHAN];
    uint16_t    window[FIRA_SEGS_PER_CHAN];   /* 输出样本数（= frame/2^level，plan §3.3 表） */
    uint8_t     initialized;
} FiraChannelState;

/* ============================================================
 * 系数注入（F3）：把共享 63-tap Q15 半带原型符号扩展冻结为 FIRA 32-bit 容器。
 *   🔴 R14 §4.2：Q15→32-bit 符号扩展 + 小数点语义保持，台架逐位核实。
 *   coef32 = fir_coeffs_q31.h 生成的冻结常量数组（不上板重算，同源纪律）。
 * ============================================================ */
void fira_tree_set_coeffs(const int32_t *hb_coef_fira32, uint16_t ntaps);

/** @brief 初始化一个 FIRA 树通道（清状态 + 填段元数据）。 */
void fira_channel_init(FiraChannelState *ch, uint16_t frame);

/* ============================================================
 * F2/F4：一次性设置 ACM 任务（Open → RegisterCallback → CreateTask）。
 *   实时模式：CreateTask 只在 init 调一次，不进帧预算（plan §1.1 PIPE.c 模式）。
 *   返回 0 成功；非 0 = adi_fir_* 失败（台架检查 ADI_FIR_RESULT）。
 *   🔴 [L1/EZKIT]：真 adi_fir_Open/CreateTask 行为待台架。
 * ============================================================ */
int fira_tree_setup(void);

/* ============================================================
 * 帧级 Split-Task 编排（草案）：
 *   FIRA 做 9 段半带卷积（QueueTask + 回调链）；核内穿插 detail 减 / 合成加 /
 *   饱和钳位 / ×2。**与 tree_filterbank.c 的 tfb_analyze/tfb_synthesize 数值等价**
 *   是 R14 的判定目标（crc==0x90556BC7）。
 *
 *   接口刻意与 tfb_analyze/tfb_synthesize **同签名**，便于 bench_harness 直接替换
 *   卷积段做 CRC 比对（FIRA_IMPL.md §bit-exact）。
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
