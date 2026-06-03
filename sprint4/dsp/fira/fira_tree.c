/**
 * @file    fira_tree.c
 * @brief   【草案·未编译·API 仿例程·待台架编译+逐位验证】
 *          FIRA 版 4 子带树形 FIR — Split-Task 编排（FIRA 卷积 + 留核定点语义）
 *
 * ┌───────────────────────────────────────────────────────────────────────┐
 * │ 🔴 诚实状态（硬约束，禁删）：本机无 SHARC 工具链 + 无 FIRA 硬件 →        │
 * │  本文件 **无法编译 / 板上验证**。adi_fir_* 用法仿例程 MCP.c:128-285；    │
 * │  每个未验证假设标 [ASSUME]/[proxy]/[L1/EZKIT]。                          │
 * │  🚫 不声称"已编译/已 bit-exact/已实测 cycle" → 全部待台架（F0-F8）。      │
 * └───────────────────────────────────────────────────────────────────────┘
 */

#include "fira_tree.h"
#include <string.h>
#include <stdint.h>

/* 🔴 [proxy] 台架（F1）启用真头后定义 FIRA_USE_REAL_ADI_FIR_HEADER 并取消下行注释：
 *   #include <drivers/fir/adi_fir.h>
 * 本机无该头（CCES ARM-only），草案用 fira_tree.h 的占位 typedef。 */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
#include <drivers/fir/adi_fir.h>   /* [L1/EZKIT] 真 ACM 字段顺序以此为准（F1 校实） */
#endif

/* ============================================================
 * 留核定点原语（Split-Task 核侧，plan §3.2）
 * ------------------------------------------------------------
 * 🔴 这些必须留核：FIRA 只做 MAC，无 Q31 饱和 / 向量减 / 向量加语义。
 *   语义逐位等同 tree_filterbank.c:47-61（sat_i64_to_i32 / sat_add_i32）+
 *   :180 q31_mul。为保证 R14 bit-exact，这里**复刻同一钳位/截断逻辑**
 *   （核内 sat_* 为 static，FIRA 路径在本编译单元重复同一语义；R14 比对验证等价）。
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

/* ---- 共享 FIRA 32-bit 半带系数（F3 冻结，符号扩展自 Q15，§4.2 R14） ---- */
static const int32_t *g_hb_fira = 0;
static uint16_t        g_hb_fira_n = 0;

void fira_tree_set_coeffs(const int32_t *hb_coef_fira32, uint16_t ntaps)
{
    /* 🔴 R14 §4.2：hb_coef_fira32 须由 fir_coeffs_q31.h 一次性冻结，
     *   = Q15 符号扩展进 32-bit 容器（高位补符号），小数点语义保持。
     *   台架逐位核实：误当无符号 / 左移对齐错位 → 整体增益错 2^k → CRC 必挂。 */
    g_hb_fira   = hb_coef_fira32;
    g_hb_fira_n = ntaps;
}

void fira_channel_init(FiraChannelState *ch, uint16_t frame)
{
    uint16_t f1 = frame/2u, f2 = frame/4u, f3 = frame/8u;
    memset(ch, 0, sizeof(*ch));
    /* 段元数据（顺序 = plan §3.3 表）：3 dec(↓) + 3 ana_int(↑) + 3 syn_int(↑) */
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
 * §A. ACM channel 描述构造（仿 MCP.c:128-160 字段顺序）
 * ------------------------------------------------------------
 * 🔴 [proxy] 字段顺序/类型以台架真 adi_fir_2156x.h 为准（F1）。下方在真头启用时
 *   编译；草案默认 #if 0 屏蔽，避免占位 typedef 下产生误导性"可编译"假象。
 * ============================================================ */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
/**
 * 构造一个半带段的 ACM ADI_FIR_CHANNEL_INFO（字段顺序严格仿 MCP.c:128-160）。
 *  @param kind   DEC→eSampling=DECIMATION；INT→INTERPOLATION（plan §3.3）
 *  @param window 输出样本数（= frame/2^level）
 *  @param coeff  冻结 32-bit 半带系数基址（fira_tree_set_coeffs 注入）
 *  @param inbuf  输入延迟线基址，**布局须为 TapLen+Window-1**（MCP.c:151, §1.2）
 *  @param outbuf 输出缓冲基址（Window 样本）
 *
 * 🔴 R14 §4.3（HIGH）：bFixedEnable=true + 定点格式枚举只有 UNSIGNED/SIGNED_INTEGER
 *   （MCP.c:140-141）。我方 signed-fractional：选 SIGNED_INTEGER 当 Q 用 → 小数点
 *   语义丢失，须配 ×2 缩放 + decimate 后处理 + 核内 >>15 一致化（见 fira_postscale）。
 *   **此映射桌面无法坐实，必上板逐位回归 golden 0x90556BC7**。
 */
static ADI_FIR_CHANNEL_INFO fira_make_channel(FiraSegKind kind, uint16_t window,
                                              const int32_t *coeff,
                                              const int32_t *inbuf, int32_t *outbuf)
{
    ADI_FIR_CHANNEL_INFO ci;
    memset(&ci, 0, sizeof(ci));
    /* 字段顺序仿 MCP.c:131-153（ACM）。命名以真头为准，台架对齐。 */
    ci.TapLength      = g_hb_fira_n;                       /* 63（MCP.c:131） */
    ci.WindowSize     = window;                            /* 输出样本数（MCP.c:132） */
    /* 🔴 [ASSUME] 抽取/插值模式位：ADI 例程全 SINGLE_RATE，无 dec/int 示例（plan §3.3）。
     *   枚举名 ADI_FIR_SAMPLING_DECIMATION/INTERPOLATION 引自 V2:92-93,237 [proxy]。 */
    ci.eSampling      = (kind == FIRA_SEG_DEC) ? ADI_FIR_SAMPLING_DECIMATION
                                               : ADI_FIR_SAMPLING_INTERPOLATION;
    ci.nSamplingRatio = FIRA_RATIO;                        /* 2（整数，hwref:75697-98 满足） */
    /* —— ACM 专属（MCP.c:135-142 的 #if ACM 内）—— */
    ci.bCallbackEnable = 1;                                /* 该 channel 完成回调 → 链下一级 */
    ci.bGenerateTrigger = 0;
    ci.bWaitForTrigger  = 0;
    ci.eRoundingMode    = ADI_FIR_FLOAT_ROUNDING_MODE_IEEE_ROUND_TO_NEAREST_EVEN; /* 浮点用；定点路径不主导（§4.4） */
    ci.bFixedEnable     = 1;                               /* 🔴 定点路线必须 true（例程 false=浮点） */
    /* 🔴 R14 §4.3 命门：signed-fractional 无直接枚举。先选 SIGNED_INTEGER + 核内补缩放。
     *   [ASSUME] 待 F6 台架在 SHARC 仿真器单段打通 bit-exact 才能确认本选择正确。 */
    ci.eFixedFormat     = ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER;
    /* —— 系数 / 输出 / 输入布局（MCP.c:143-153）—— */
    ci.CoeffCount  = g_hb_fira_n;
    ci.CoeffModify = 1;
    ci.pCoeffIndex = (void *)coeff;
    ci.pOutBase    = (void *)outbuf;
    ci.OutCount    = window;
    ci.OutModify   = 1;
    ci.pOutIndex   = (void *)outbuf;
    ci.pInBase     = (void *)inbuf;
    ci.InCount     = (uint32_t)g_hb_fira_n + window - 1u;  /* TapLen+Window-1（MCP.c:151, §1.2） */
    ci.InModify    = 1;
    ci.pInIndex    = (void *)inbuf;
    return ci;
}
#endif /* FIRA_USE_REAL_ADI_FIR_HEADER */

/* ============================================================
 * §B. 设备 / 任务生命周期（仿 MCP.c:243-265，PIPE.c 实时一次性 init）
 * ============================================================ */
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
static ADI_FIR_DEV_HANDLE  s_hFir = 0;
volatile uint32_t          g_FIRChanDoneCount = 0;   /* 回调置位（仿 MCP.c:92,105，ACM 每 channel 一次） */

/* 完成回调：ACM 每 channel 完成一次（MCP.c:96-107）。实时模式在此 queue 下一级。 */
static void fira_done_cb(void *pCBParam, ADI_FIR_EVENT Event, void *pArg)
{
    (void)pCBParam; (void)pArg;
    if (Event == ADI_FIR_EVENT_CHANNEL_DONE) {   /* ACM（MCP.c:101） */
        g_FIRChanDoneCount++;
        /* 🔴 [L1/EZKIT] 级间依赖链：分析 dec[0]→[1]→[2] 串行（下级吃上级输出）。
         *   实时路径在此 adi_fir_QueueTask(下一级)；草案不展开调度细节（待 F4 台架）。 */
    }
}
#endif

int fira_tree_setup(void)
{
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    /* 仿 MCP.c:243-265：Open → RegisterCallback → CreateTask（×段/通道分组）。
     * 🔴 [L1/EZKIT] TaskMemory 须 #pragma align 32（MCP.c:82），按真 FIR_MEM_SIZE() 分配。
     *   通道分组（同级多通道并发 / 跨级回调链）= F4 台架定，草案不锁。 */
    ADI_FIR_RESULT r;
    r = adi_fir_Open(0u, &s_hFir);                 if (r != ADI_FIR_RESULT_SUCCESS) return 1;
    r = adi_fir_RegisterCallback(s_hFir, fira_done_cb, 0); if (r != ADI_FIR_RESULT_SUCCESS) return 2;
    /* adi_fir_CreateTask(...) 按段分组：[ASSUME] 见 FIRA_IMPL.md §F2/F4，待台架。 */
    return 0;
#else
    /* 🚫 本机无真头：setup 不可执行。返回非 0 表"未在目标平台"，禁误用。 */
    return -1;   /* [proxy] 台架（F1）启用真头后返回 0 */
#endif
}

void fira_tree_teardown(void)
{
#ifdef FIRA_USE_REAL_ADI_FIR_HEADER
    if (s_hFir) { adi_fir_Close(s_hFir); s_hFir = 0; }   /* MCP.c 未显式调，实时退出调（plan §1.1） */
#endif
}

/* ============================================================
 * §C. R14 后处理：signed-fractional 对齐（plan §4.3/§4.5，bit 偏差高发）
 * ------------------------------------------------------------
 * 🔴 FIRA 80-bit MR（SIGNED_INTEGER MAC）回写后，须与我方核 acc>>15 + ×2 一致化。
 *   - DEC 段：核 hb_push_filter = acc>>15 + sat（tree_filterbank.c:104）。
 *   - INT 段：核 = (acc>>15)*2 + sat（:127,130）。
 *   ×2 只做一次（§4.5：FIRA INTERPOLATION 零插值 ×2 与 signed-fractional ×2 可能
 *   复合两次 → 增益错 4×）。此函数把 FIRA 整数输出还原到我方 Q31 语义。
 *   [ASSUME] 缩放因子/移位量 = 待 F6 台架逐位对齐，桌面给的是**语义占位**，非定值。
 * ============================================================ */
static int32_t fira_postscale_dec(int64_t fira_mr)
{
    /* 🔴 [ASSUME] 待台架：SIGNED_INTEGER MAC 的 80-bit MR → Q31，须 >>15（同核截断，
     *   向负无穷），不得用 IEEE round（§4.1：截断 vs 舍入差 ±1 LSB → CRC 挂）。 */
    return f_sat_i64_to_i32(fira_mr >> 15);
}
static int32_t fira_postscale_int(int64_t fira_mr)
{
    /* 🔴 [ASSUME] 待台架：×2 内插增益**只一次**（§4.5）。若 FIRA 硬件已 ×2，则此处不再 ×2。 */
    return f_sat_i64_to_i32((fira_mr >> 15) * 2);
}

/* ============================================================
 * §D. 帧级 Split-Task 编排（草案占位）
 * ------------------------------------------------------------
 * 🔴 与 tfb_analyze/tfb_synthesize 同签名 → bench_harness 可直接替换做 CRC 比对。
 *   本机无 FIRA → 无法真跑。草案给**编排骨架 + 留核段**；FIRA 卷积段以注释标出
 *   "此处 QueueTask + 等回调"，台架（F4-F6）填真调用。detail 减/合成加/饱和=核内。
 *
 *   ⚠️ 草案策略（避免冒充验证）：未定义 FIRA_USE_REAL_ADI_FIR_HEADER 时，
 *   FIRA 卷积段**不可用**，故本两函数在草案构建下仅保留留核部分 + 段标注，
 *   不产出数值（不冒充 bit-exact）。台架启用真头后接通 FIRA 段。
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

    /* —— FIRA 段（DECIMATION r=2，留核取偶相位语义由硬件 skip 复现，§4.6）——
     * 🔴 [L1/EZKIT] 台架：a1=FIRA_dec(in); a2=FIRA_dec(a1); a3=FIRA_dec(a2);
     *   （QueueTask seg0→回调→seg1→回调→seg2；fira_postscale_dec 还原 Q31）。
     *   草案无硬件 → 不产生 a1/a2/a3 真值；下行 memset 仅占位防未初始化读，
     *   🚫 不代表数值正确（R14 由台架 crc 判定）。 */
    memset(a1, 0, sizeof(a1)); memset(a2, 0, sizeof(a2)); memset(a3, 0, sizeof(a3));

    /* —— FIRA 段（INTERPOLATION r=2，求 detail 用的 coarse 重建，×2 见 fira_postscale_int）——
     * 🔴 [L1/EZKIT] 台架：r3=FIRA_int(a3); r2=FIRA_int(a2); r1=FIRA_int(a1); */
    memset(r1, 0, sizeof(r1)); memset(r2, 0, sizeof(r2)); memset(r3, 0, sizeof(r3));

    /* —— 留核（plan §3.2，FIRA 无向量减）：detail = 本级 − interp2(下级) —— */
    for (i = 0u; i < f2; i++) sb1[i] = a2[i] - r3[i];   /* SB1 detail @f2（核内，逐位同 tree_filterbank.c:161） */
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

    /* —— FIRA 段（INTERPOLATION）+ 留核合成加（sat_add，FIRA 无向量加，§3.2）—— */
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
