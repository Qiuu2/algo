/**
 * @file    fira_tree.c
 * @brief   【草案·未编译·真 Legacy API·F2-F7 待台架】
 *          FIRA 版 4 子带树形 FIR — Split-Task 编排（FIRA 卷积 + 留核定点语义）
 *
 * ┌───────────────────────────────────────────────────────────────────────┐
 * │ 🔴 诚实状态（硬约束，禁删）：本机无 SHARC 工具链 + 无 FIRA 硬件 →        │
 * │  本文件 **无法编译 / 板上验证**。adi_fir_* = 真 Legacy 签名（归档头      │
 * │  adi_fir_legacy_2156x.h）；生命周期仿官方 Legacy 实例 MCP.c:243-285。    │
 * │  每个未验证假设标 [ASSUME]/[L1/EZKIT]。                                  │
 * │  🚫 不声称"已编译/已 bit-exact/已实测 cycle" → 全部待台架（F2-F7）。      │
 * └───────────────────────────────────────────────────────────────────────┘
 *
 * 模式 LEGACY；定点 Path B（运行时 adi_fir_FixedPointEnable(SIGNED)，CreateTask 后/QueueTask 前）。
 */

#include "fira_tree.h"
#include "fir_coeffs_q31.h"   /* 冻结 32-bit 半带系数（F3，占位 0 → 台架填实） */
#include <string.h>
#include <stdint.h>

/* ============================================================
 * 留核定点原语（Split-Task 核侧）
 * ------------------------------------------------------------
 * 🔴 这些必须留核：FIRA 只做 MAC，无 Q31 饱和 / 向量减 / 向量加语义。
 *   语义逐位等同 tree_filterbank.c:47-61（sat_i64_to_i32 / sat_add_i32）。
 *   R14 比对验证 FIRA 路径与核路径数值等价（crc==0x90556BC7）。
 * ============================================================ */
#ifdef TFB_DISABLE_SAT
static inline int32_t f_sat_i64_to_i32(int64_t v) { return (int32_t)v; }
static inline int32_t f_sat_add_i32(int32_t a, int32_t b) { return (int32_t)(a + b); }
#else
static inline int32_t f_sat_i64_to_i32(int64_t v)
{
    if (v > (int64_t)INT32_MAX) { return INT32_MAX; }
    if (v < (int64_t)INT32_MIN) { return INT32_MIN; }
    return (int32_t)v;
}
static inline int32_t f_sat_add_i32(int32_t a, int32_t b)
{
    int64_t s = (int64_t)a + (int64_t)b;
    if (s > (int64_t)INT32_MAX) { return INT32_MAX; }
    if (s < (int64_t)INT32_MIN) { return INT32_MIN; }
    return (int32_t)s;
}
#endif

/* ---- 共享 FIRA 32-bit 半带系数（F3 冻结，符号扩展自 Q15，R14-2） ---- */
static const int32_t *g_hb_fira = 0;
static uint16_t        g_hb_fira_n = 0;

void fira_tree_set_coeffs(const int32_t *hb_coef_fira32, uint16_t ntaps)
{
    /* 🔴 R14-2：hb_coef_fira32 须由 fir_coeffs_q31.h 一次性冻结，
     *   = Q15 符号扩展进 32-bit 容器（高位补符号），小数点语义保持。
     *   台架逐位核实：误当无符号 / 左移对齐错位 → 整体增益错 2^k → CRC 必挂。 */
    g_hb_fira   = hb_coef_fira32;
    g_hb_fira_n = ntaps;
}

void fira_channel_init(FiraChannelState *ch, uint16_t frame)
{
    uint16_t f1 = frame/2u, f2 = frame/4u, f3 = frame/8u;
    memset(ch, 0, sizeof(*ch));
    /* 段元数据（顺序 = FIRA_IMPL.md §2 表）：3 dec(↓) + 3 ana_int(↑) + 3 syn_int(↑) */
    ch->kind[0] = FIRA_SEG_DEC; ch->window[0] = f1;   /* ana_dec[0] f0->f1 */
    ch->kind[1] = FIRA_SEG_DEC; ch->window[1] = f2;   /* ana_dec[1] f1->f2 */
    ch->kind[2] = FIRA_SEG_DEC; ch->window[2] = f3;   /* ana_dec[2] f2->f3 */
    ch->kind[3] = FIRA_SEG_INT; ch->window[3] = f2;   /* ana_int[2] f3->f2 */
    ch->kind[4] = FIRA_SEG_INT; ch->window[4] = f1;   /* ana_int[1] f2->f1 */
    ch->kind[5] = FIRA_SEG_INT; ch->window[5] = frame;/* ana_int[0] f1->f0 */
    ch->kind[6] = FIRA_SEG_INT; ch->window[6] = f2;   /* syn_int[2] f3->f2 */
    ch->kind[7] = FIRA_SEG_INT; ch->window[7] = f1;   /* syn_int[1] f2->f1 */
    ch->kind[8] = FIRA_SEG_INT; ch->window[8] = frame;/* syn_int[0] f1->f0 */
    ch->initialized = 1u;
}

/* ============================================================
 * §A. ADI_FIR_CHANNEL_INFO 构造（真 Legacy 字段，仿 MCP.c:128-153 + legacy 头:46-54）
 * ------------------------------------------------------------
 * 🔴 Legacy 模式下 CHANNEL_INFO **无内联定点字段**（bFixedEnable/eFixedFormat 在
 *   例程 #if ACM 内，Legacy 编译掉，MCP.c:135-142；legacy 头:45 注明）。定点经
 *   运行时 adi_fir_FixedPointEnable(SIGNED) 设（CreateTask 后/QueueTask 前，见 §B）。
 * 字段顺序严格按 legacy 头 ADI_FIR_CHANNEL_INFO（:46-54）：
 *   nTapLength, nWindowSize, eSampling, nSamplingRatio,
 *   nCoefficientCount, pCoefficientIndex, nCoefficientModify,
 *   pOutputBuffBase, nOutputBuffCount, nOutputBuffModify, pOutputBuffIndex,
 *   pInputBuffBase,  nInputBuffCount,  nInputBuffModify,  pInputBuffIndex
 * ============================================================ */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
/**
 * 构造一个半带段的 Legacy ADI_FIR_CHANNEL_INFO。
 *  @param kind   DEC→eSampling=DECIMATION；INT→INTERPOLATION（FIRA_IMPL.md §2）
 *  @param window 输出样本数（= frame/2^level）
 *  @param coeff  冻结 32-bit 半带系数基址（fira_tree_set_coeffs 注入）
 *  @param inbuf  输入延迟线基址，**布局须为 nTapLength+nWindowSize-1**（MCP.c:151）
 *  @param outbuf 输出缓冲基址（window 样本）
 *
 * 🔴 R14-3（HIGH）：定点格式不在此设（Legacy 无字段）；由 adi_fir_FixedPointEnable
 *   (hTask, SIGNED_INTEGER) 运行时设。signed-fractional 当 SIGNED_INTEGER 用 → 小数点
 *   语义丢失，须配 ×2 缩放 + decimate 后处理 + 核内 >>15 一致化（见 fira_postscale_*）。
 *   **此映射桌面无法坐实，必上板逐位回归 golden 0x90556BC7**。
 */
static ADI_FIR_CHANNEL_INFO fira_make_channel(FiraSegKind kind, uint16_t window,
                                              const int32_t *coeff,
                                              const int32_t *inbuf, int32_t *outbuf)
{
    ADI_FIR_CHANNEL_INFO ci;
    memset(&ci, 0, sizeof(ci));
    ci.nTapLength      = g_hb_fira_n;                      /* 63（legacy 头:47） */
    ci.nWindowSize     = window;                           /* 输出样本数（:48） */
    /* 抽取/插值模式（per-channel，Legacy 支持，F1 §3）。枚举见 legacy 头:33-35。
     * 🔴 [ASSUME] ADI 例程全 SINGLE_RATE，无 dec/int 示例 → 相位/×2 行为 F4 上板验。 */
    ci.eSampling       = (kind == FIRA_SEG_DEC) ? ADI_FIR_SAMPLING_DECIMATION
                                                : ADI_FIR_SAMPLING_INTERPOLATION;
    ci.nSamplingRatio  = FIRA_RATIO;                       /* 2（整数，legacy 头:50） */
    /* —— 系数（legacy 头:51）—— */
    ci.nCoefficientCount  = g_hb_fira_n;
    ci.pCoefficientIndex  = (void *)coeff;
    ci.nCoefficientModify = 1;
    /* —— 输出（legacy 头:52）—— */
    ci.pOutputBuffBase  = (void *)outbuf;
    ci.nOutputBuffCount = window;
    ci.nOutputBuffModify = 1;
    ci.pOutputBuffIndex = (void *)outbuf;
    /* —— 输入（legacy 头:53）：布局 nTapLength+nWindowSize-1（MCP.c:151）—— */
    ci.pInputBuffBase  = (void *)inbuf;
    ci.nInputBuffCount = (uint32_t)g_hb_fira_n + window - 1u;
    ci.nInputBuffModify = 1;
    ci.pInputBuffIndex = (void *)inbuf;
    return ci;
}
#endif /* FIRA_USE_REAL_ADI_FIR_HEADER */

/* ============================================================
 * §B. 设备 / 任务生命周期（真 Legacy，仿 MCP.c:243-285）
 * ------------------------------------------------------------
 * 链：Open → RegisterCallback → CreateTask → FixedPointEnable(SIGNED) → QueueTask
 *     → 等回调(FIRTaskDoneCount<N_TASKS, ALL_CHANNEL_DONE) → Close。
 * Legacy 完成事件 = ADI_FIR_EVENT_ALL_CHANNEL_DONE（MCP.c:103），主循环等
 *   FIRTaskDoneCount < N_TASKS（MCP.c:282）。
 * ============================================================ */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
static ADI_FIR_DEV_HANDLE  s_hFir = 0;
volatile uint32_t          g_FIRTaskDoneCount = 0;   /* 回调置位（MCP.c:92,105，Legacy 每 task 一次） */

/* 完成回调：Legacy 在一个 task 的所有 channel 完成后触发一次 ALL_CHANNEL_DONE（MCP.c:96-107）。 */
static void fira_done_cb(void *pCBParam, ADI_FIR_EVENT Event, void *pArg)
{
    (void)pCBParam; (void)pArg;
    if (Event == ADI_FIR_EVENT_ALL_CHANNEL_DONE) {   /* Legacy（MCP.c:103） */
        g_FIRTaskDoneCount++;
    }
}
#endif

/* ============================================================
 * §B-template. F2-F4 单通道台架起步模板（可编译起步：台架定义真头后即跑）
 * ------------------------------------------------------------
 * 跑通 1 个 DECIMATION 半带段的**完整 Legacy 生命周期 + Path B 定点**，验证：
 *   (a) 生命周期顺序正确（Open..Close 无 ADI_FIR_RESULT 错）；
 *   (b) Path B 运行时 FixedPointEnable(SIGNED) 在 Legacy 下生效（F1 §4 残留 G2）；
 *   (c) DECIMATION 相位 / ×2（R14-5/-6）—— 对 out 逐位比小例 golden。
 * 缓冲由调用者传入（in 长 in_count = ntaps+out_count-1，out 长 out_count）。
 * 🔴 [L1/EZKIT]：真 adi_fir_* 行为待台架；草案默认构建返回 -1（不接 FIRA，不冒充）。
 * ============================================================ */
int fira_single_channel_template(const int32_t *in, uint16_t in_count,
                                 int32_t *out, uint16_t out_count, uint16_t ntaps)
{
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    /* TaskMemory：真 FIR_MEM_SIZE(N_CH) 宏（legacy 头:18）。1 通道 → FIR_MEM_SIZE(1)。
     * #pragma align 32（MCP.c:82-83；cache line 对齐，否则坏 bit-exact，见 FIRA_IMPL.md §F4）。 */
    #pragma align 32
    static uint8_t s_taskMem[FIR_MEM_SIZE(1)];
    ADI_FIR_TASK_HANDLE hTask = 0;
    ADI_FIR_RESULT r;

    if (g_hb_fira == 0 || in == 0 || out == 0) { return -2; }

    /* 1 个 channel：DECIMATION r=2（台架可切 INTERPOLATION 验 ×2）。 */
    ADI_FIR_CHANNEL_INFO ch = fira_make_channel(FIRA_SEG_DEC, out_count,
                                                g_hb_fira, in, out);
    ch.nTapLength = ntaps; ch.nCoefficientCount = ntaps;
    ch.nInputBuffCount = (uint32_t)ntaps + out_count - 1u;
    (void)in_count;   /* 调用者保证 in_count == ntaps+out_count-1（布局自检留台架） */

    g_FIRTaskDoneCount = 0;

    r = adi_fir_Open(0u, &s_hFir);                          if (r != ADI_FIR_RESULT_SUCCESS) return 1;
    r = adi_fir_RegisterCallback(s_hFir, fira_done_cb, 0);  if (r != ADI_FIR_RESULT_SUCCESS) return 2;
    r = adi_fir_CreateTask(s_hFir, &ch, 1u, (void *)s_taskMem,
                           (uint32_t)FIR_MEM_SIZE(1), &hTask);
                                                            if (r != ADI_FIR_RESULT_SUCCESS) return 3;
    /* 🔴 Path B：CreateTask 后、QueueTask 前设定点 SIGNED（F1 锁定，不改 config 头）。 */
    r = adi_fir_FixedPointEnable(hTask, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER);
                                                            if (r != ADI_FIR_RESULT_SUCCESS) return 4;
    r = adi_fir_QueueTask(hTask);                           if (r != ADI_FIR_RESULT_SUCCESS) return 5;

    /* Legacy：等 N_TASKS=1 个 ALL_CHANNEL_DONE 回调（MCP.c:282）。 */
    while (g_FIRTaskDoneCount < 1u) { /* spin；台架可换 idle/事件等待 */ }

    r = adi_fir_Close(s_hFir);  s_hFir = 0;                 if (r != ADI_FIR_RESULT_SUCCESS) return 6;
    return 0;
#else
    (void)in; (void)in_count; (void)out; (void)out_count; (void)ntaps;
    return -1;   /* 🚫 本机无真头：不可执行，禁误用为"已验证"。台架定义真头后返回 0。 */
#endif
}

int fira_tree_setup(void)
{
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    /* 仿 MCP.c:243-265：Open → RegisterCallback → CreateTask（×段/通道分组）
     *   → FixedPointEnable(SIGNED)（每任务，Path B）。
     * 🔴 [L1/EZKIT] TaskMemory 须 #pragma align 32（MCP.c:82），按真 FIR_MEM_SIZE() 分配。
     *   通道分组（同级多通道并发 / 跨级回调链）+ 每任务 FixedPointEnable = F4/F5 台架定。 */
    ADI_FIR_RESULT r;
    r = adi_fir_Open(0u, &s_hFir);                         if (r != ADI_FIR_RESULT_SUCCESS) return 1;
    r = adi_fir_RegisterCallback(s_hFir, fira_done_cb, 0); if (r != ADI_FIR_RESULT_SUCCESS) return 2;
    /* adi_fir_CreateTask(...) + adi_fir_FixedPointEnable(hTask, SIGNED) 按段分组：
     *   [ASSUME] 见 FIRA_IMPL.md §F2/F4/F5，全任务编排待台架。 */
    return 0;
#else
    /* 🚫 本机无真头：setup 不可执行。返回非 0 表"未在目标平台"，禁误用。 */
    return -1;   /* 台架（F1）启用真头后返回 0 */
#endif
}

void fira_tree_teardown(void)
{
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    if (s_hFir) { adi_fir_Close(s_hFir); s_hFir = 0; }   /* 实时退出调（MCP.c 未显式调） */
#endif
}

/* ============================================================
 * §C. R14 后处理：signed-fractional 对齐（FIRA_IMPL.md §3 R14-3/-5，bit 偏差高发）
 * ------------------------------------------------------------
 * 🔴 FIRA 80-bit MR（SIGNED_INTEGER MAC）回写后，须与我方核 acc>>15 + ×2 一致化。
 *   - DEC 段：核 hb_push_filter = acc>>15 + sat（tree_filterbank.c:104）。
 *   - INT 段：核 = (acc>>15)*2 + sat（:127,130）。
 *   ×2 只做一次（R14-5：FIRA INTERPOLATION 零插值 ×2 与 signed-fractional ×2 可能
 *   复合两次 → 增益错 4×）。
 *   [ASSUME] 缩放因子/移位量 = 待 F6 台架逐位对齐，桌面给的是**语义占位**，非定值。
 * ============================================================ */
static int32_t fira_postscale_dec(int64_t fira_mr)
{
    /* 🔴 [ASSUME] 待台架：SIGNED_INTEGER MAC 的 80-bit MR → Q31，须 >>15（同核截断，
     *   向负无穷），不得用 IEEE round（R14-1：截断 vs 舍入差 ±1 LSB → CRC 挂）。 */
    return f_sat_i64_to_i32(fira_mr >> 15);
}
static int32_t fira_postscale_int(int64_t fira_mr)
{
    /* 🔴 [ASSUME] 待台架：×2 内插增益**只一次**（R14-5）。若 FIRA 硬件已 ×2，则此处不再 ×2。 */
    return f_sat_i64_to_i32((fira_mr >> 15) * 2);
}

/* ============================================================
 * §D. 帧级 Split-Task 编排（草案占位）
 * ------------------------------------------------------------
 * 🔴 与 tfb_analyze/tfb_synthesize 同签名 → fira_regression 可直接替换做 CRC 比对。
 *   本机无 FIRA → 无法真跑。草案给**编排骨架 + 留核段**；FIRA 卷积段以注释标出
 *   "此处 QueueTask + 等 ALL_CHANNEL_DONE"，台架（F4-F6）填真调用。detail 减/合成加/饱和=核内。
 *
 *   ⚠️ 草案策略（避免冒充验证）：未定义 FIRA_USE_REAL_ADI_FIR_HEADER 时，
 *   FIRA 卷积段**不可用**，本两函数仅保留留核部分 + 段标注，不产出有效数值
 *   （不冒充 bit-exact）。台架启用真头后接通 FIRA 段。
 *
 *   🔴 8ch×多段扩展 = F5（标注，不全展开）：本两函数处理单通道；8ch broadside
 *   把 8 路单通道 analyze/synthesize 各自跑后在核内 sat_add 求和（复用 tfb_8ch.c），
 *   每路一组 ADI_FIR_CHANNEL_INFO + 一次 FixedPointEnable，task 分组与并发度台架填。
 * ============================================================ */
void fira_tfb_analyze(FiraChannelState *ch, const int32_t *in, uint16_t frame,
                      int32_t *sb0, int32_t *sb1, int32_t *sb2, int32_t *sb3)
{
    uint16_t f0 = frame, f1 = frame/2u, f2 = frame/4u, f3 = frame/8u;
    uint16_t i;
    /* 各级 coarse / interp 重建缓冲（同 tree_filterbank.c:143-144 布局） */
    int32_t a1[256], a2[128], a3[64];
    int32_t r1[512], r2[256], r3[128];
    (void)ch; (void)fira_postscale_dec; (void)fira_postscale_int;

    /* —— FIRA 段（DECIMATION r=2，取偶相位由硬件 skip 复现，R14-6）——
     * 🔴 [L1/EZKIT] 台架：a1=FIRA_dec(in); a2=FIRA_dec(a1); a3=FIRA_dec(a2);
     *   （QueueTask seg0→ALL_CHANNEL_DONE→seg1→…→seg2；fira_postscale_dec 还原 Q31）。
     *   草案无硬件 → 不产生 a1/a2/a3 真值；下行 memset 仅占位防未初始化读，
     *   🚫 不代表数值正确（R14 由台架 crc 判定）。 */
    memset(a1, 0, sizeof(a1)); memset(a2, 0, sizeof(a2)); memset(a3, 0, sizeof(a3));

    /* —— FIRA 段（INTERPOLATION r=2，求 detail 用 coarse 重建，×2 见 fira_postscale_int）——
     * 🔴 [L1/EZKIT] 台架：r3=FIRA_int(a3); r2=FIRA_int(a2); r1=FIRA_int(a1); */
    memset(r1, 0, sizeof(r1)); memset(r2, 0, sizeof(r2)); memset(r3, 0, sizeof(r3));

    /* —— 留核（FIRA 无向量减）：detail = 本级 − interp2(下级) —— */
    for (i = 0u; i < f2; i++) sb1[i] = a2[i] - r3[i];   /* SB1 detail @f2（逐位同 tree_filterbank.c:161） */
    for (i = 0u; i < f1; i++) sb2[i] = a1[i] - r2[i];   /* SB2 detail @f1（:162） */
    for (i = 0u; i < f0; i++) sb3[i] = in[i] - r1[i];   /* SB3 detail @f0（:163） */
    for (i = 0u; i < f3; i++) sb0[i] = a3[i];           /* SB0 coarse @f3（:164） */
}

void fira_tfb_synthesize(FiraChannelState *ch,
                         const int32_t *sb0, const int32_t *sb1,
                         const int32_t *sb2, const int32_t *sb3,
                         uint16_t frame, int32_t *out)
{
    uint16_t f0 = frame, f1 = frame/2u, f2 = frame/4u;
    uint16_t i;
    int32_t a2p[256], a1p[512];
    int32_t up3[128], up2[256], up1[512];
    (void)ch;

    /* —— FIRA 段（INTERPOLATION）+ 留核合成加（sat_add，FIRA 无向量加）—— */
    /* 🔴 [L1/EZKIT] 台架：up3=FIRA_int(sb0); 草案占位 0。 */
    memset(up3, 0, sizeof(up3));
    for (i = 0u; i < f2; i++) a2p[i] = f_sat_add_i32(up3[i], sb1[i]);   /* 逐位同 tree_filterbank.c:197 */

    /* 🔴 [L1/EZKIT] 台架：up2=FIRA_int(a2p); */
    memset(up2, 0, sizeof(up2));
    for (i = 0u; i < f1; i++) a1p[i] = f_sat_add_i32(up2[i], sb2[i]);   /* :201 */

    /* 🔴 [L1/EZKIT] 台架：up1=FIRA_int(a1p); */
    memset(up1, 0, sizeof(up1));
    for (i = 0u; i < f0; i++) out[i] = f_sat_add_i32(up1[i], sb3[i]);   /* :205 */
}
