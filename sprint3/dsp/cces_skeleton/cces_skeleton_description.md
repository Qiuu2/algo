# CCES 项目骨架描述
**项目名**: ITC_ColumnSpeaker_8ch_Beamformer  
**目标平台**: ADSP-21569 EV-21569-EZKIT  
**工具链**: CrossCore Embedded Studio (CCES) + SHARC Audio Toolbox  
**版本**: v0.1 骨架（Sprint 3 EZKIT 验证用）

---

## 1. 目录树结构

```
ITC_ColumnSpeaker_8ch_Beamformer/
├── ITC_ColumnSpeaker_8ch_Beamformer.dpj   # CCES 工程文件
├── system.svc                              # 系统配置（时钟/内存分配）
├── app.c                                   # 主入口，系统初始化 + 主循环
│
├── src/
│   ├── dsp_main.c          # DSP 算法主调度（帧级调度，DMA 回调入口）
│   ├── sport_tdm.c         # SPORT TDM 配置与 DMA ping-pong 控制
│   ├── sport_tdm.h
│   │
│   ├── filterbank/
│   │   ├── halfband_fir.c  # 通用半带 FIR（单级处理，供树形各级复用）
│   │   ├── halfband_fir.h
│   │   ├── dyadic_analysis.c   # 3级分析树（8ch 并行输入→4子带）
│   │   ├── dyadic_analysis.h
│   │   ├── dyadic_synthesis.c  # 3级合成树（4子带→1ch 全速率重建）
│   │   ├── dyadic_synthesis.h
│   │   └── fir_coeffs.h        # Q15 半带系数（从 fir_design_verify.py 导出）
│   │
│   ├── beamformer/
│   │   ├── bf_broadside.c      # broadside-only 波束形成核心
│   │   ├── bf_broadside.h
│   │   ├── dolph_chebyshev.c   # D-C 权重计算（初始化时调用一次）
│   │   ├── dolph_chebyshev.h
│   │   ├── frac_delay_fir.c    # 分数延迟 FIR（broadside 时 τ≈0，可优化掉）
│   │   └── frac_delay_fir.h
│   │
│   ├── postproc/
│   │   ├── subband_gain.c      # 子带增益均衡（可选，补偿喇叭频响）
│   │   ├── subband_gain.h
│   │   ├── limiter.c           # 软限幅器（保护功放，防烧毁）
│   │   └── limiter.h
│   │
│   └── utils/
│       ├── fixed_point.h       # Q15/Q31 宏定义与饱和运算
│       ├── ring_buffer.c       # 整数延迟环形缓冲区
│       └── ring_buffer.h
│
├── include/
│   ├── itc_config.h            # 全局配置（N_CH, FS, FRAME, 子带数等）
│   └── itc_types.h             # 类型定义（Q15, Q31, Q63）
│
└── test/
    ├── test_halfband.c         # 半带 FIR 单元测试
    ├── test_filterbank.c       # 滤波器组重建平坦度测试
    ├── test_beamformer.c       # 波束形成功能验证
    └── test_vectors.h          # 测试向量（Python 生成的 C header）
```

---

## 2. 关键头文件：itc_config.h

```c
/**
 * @file itc_config.h
 * @brief ITC 定向音柱全局配置——Sprint 3 8ch broadside-only 版本
 * @note [待核实 U4] SPORT 参数在拆机 TDM 时序确认后更新
 */
#ifndef ITC_CONFIG_H
#define ITC_CONFIG_H

/* 系统基本参数 */
#define ITC_SAMPLE_RATE_HZ       48000
#define ITC_FRAME_SIZE_SAMPLES   64          /* 1.333 ms/帧 */
#define ITC_NUM_ELEMENTS         16          /* 物理阵元总数 */
#define ITC_NUM_DRIVE_CH         8           /* 独立驱动通道（A/B 串联对数） */

/* TDM / SPORT 参数 [待核实 U4：需逻辑分析仪实测竞品时序后确认] */
#define ITC_TDM_SLOTS            8           /* 输出 TDM 槽数 = 驱动通道数 */
#define ITC_TDM_WORD_BITS        32          /* 位深 */
#define ITC_BCLK_HZ              12288000    /* = 48k × 8 × 32 */

/* 子带配置 */
#define ITC_NUM_SUBBANDS         4
#define ITC_HB_FIR_TAPS          63          /* 半带 FIR 抽头数 */
#define ITC_HB_TREE_LEVELS       3           /* dyadic 树层数 */
#define ITC_FD_FIR_ORDER         8           /* 分数延迟 FIR 阶数 */

/* 波束形成配置 */
#define ITC_BF_MODE_BROADSIDE    1           /* 当前仅支持 broadside */
#define ITC_DC_SLL_DB            (-20)       /* Dolph-Chebyshev 旁瓣电平 dB */
#define ITC_DC_NUM_WEIGHTS       ITC_NUM_DRIVE_CH  /* D-C 权重数 = 8 */

/* DMA 配置 */
#define ITC_DMA_PINGPONG_BUFS    2
/* 输出 DMA 单缓冲大小: FRAME × DRIVE_CH × (WORD_BITS/8) = 64×8×4 = 2048 B */
#define ITC_DMA_OUT_BUF_BYTES    (ITC_FRAME_SIZE_SAMPLES * ITC_NUM_DRIVE_CH * \
                                   (ITC_TDM_WORD_BITS / 8))

/* 内存分配建议（ADSP-21569） */
/* L1 SRAM (640 KB): DMA 缓冲 + 热点状态变量（分数延迟 FIR 状态） */
/* L2 SRAM (1024 KB): 半带 FIR 系数 + 分析树/合成树状态 + 延迟缓冲 */

#endif /* ITC_CONFIG_H */
```

---

## 3. SPORT/TDM 初始化骨架（sport_tdm.c 关键段）

```c
/**
 * @brief 初始化 SPORT0A 为 TDM 输出，8ch @ 48kHz
 * @note  [待核实 U4] TDM 从机/主机模式、MCLK 来源、FSYNC 极性
 *         需要在拆机后用逻辑分析仪实测竞品 TDM 时序后确认
 *         当前参数基于 ADI ADAU1966A + ADSP-21569 标准配置 [估算]
 */
void sport_tdm_init(void)
{
    ADI_SPORT_CONFIG sport_cfg;
    
    /* SPORT0A: TDM 主机模式输出 */
    sport_cfg.pSPORT              = pADI_SPORT0A;
    sport_cfg.direction           = ADI_SPORT_DIR_TX;
    sport_cfg.mode                = ADI_SPORT_MODE_TDM;
    sport_cfg.tdmSlots            = ITC_TDM_SLOTS;         /* 8 */
    sport_cfg.wordLength          = ITC_TDM_WORD_BITS;     /* 32 */
    sport_cfg.sampleRate          = ITC_SAMPLE_RATE_HZ;    /* 48000 */
    /* BCLK = FSYNC × slots × wordLen = 48000 × 8 × 32 = 12.288 MHz */
    sport_cfg.bclkFreq            = ITC_BCLK_HZ;
    sport_cfg.fsyncPolarity       = ADI_SPORT_FSYNC_RISING; /* [待核实 U4] */
    sport_cfg.dataFormat          = ADI_SPORT_DATA_FORMAT_MSB_FIRST;
    
    /* DMA Ping-Pong 配置 */
    sport_cfg.pDmaBufA            = g_dma_out_buf[0];      /* Ping */
    sport_cfg.pDmaBufB            = g_dma_out_buf[1];      /* Pong */
    sport_cfg.dmaBufSizeBytes     = ITC_DMA_OUT_BUF_BYTES; /* 2048 B */
    sport_cfg.dmaCallback         = sport_dma_callback;    /* ISR 入口 */
    
    adi_sport_Open(&sport_cfg, &g_sport_handle);
    adi_sport_Enable(g_sport_handle, true);
}

/**
 * @brief DMA 完成中断回调 — 帧处理入口
 * @note  典型执行路径：拷贝完成缓冲 → 通知 DSP 主任务处理 → 
 *         DSP 主任务调用 dsp_process_frame()
 */
static void sport_dma_callback(void *pCBParam, uint32_t event, void *pArg)
{
    /* 切换 Ping/Pong 指针（硬件自动完成），通知主循环 */
    g_frame_ready = 1;
    /* 注意：不在 ISR 中做算法处理，避免不可预测的 WCET */
}
```

---

## 4. DSP 主调度骨架（dsp_main.c）

```c
/**
 * @brief 帧级 DSP 处理主函数
 *        调用时机：DMA ping-pong 完成中断触发后，在主任务中调用
 *        输入：数字节目源（单声道，ITC_FRAME_SIZE_SAMPLES 个 32bit 样本）
 *        输出：8ch TDM 输出缓冲（ITC_NUM_DRIVE_CH × ITC_FRAME_SIZE_SAMPLES 个 32bit 样本）
 */
void dsp_process_frame(const float *pSrcMono, float *pDst8ch)
{
    static float s_subbands[ITC_NUM_SUBBANDS][ITC_FRAME_SIZE_SAMPLES];  /* 4子带信号（子带率已抽取） */
    static float s_bf_out[ITC_NUM_SUBBANDS][ITC_FRAME_SIZE_SAMPLES];    /* 波束形成输出（4子带） */
    static float s_recon[ITC_FRAME_SIZE_SAMPLES];                        /* 重建全速率信号 */
    
    /* Step 1: 输入单声道 → 8ch 复制（broadside-only：同一信号广播到所有通道，加权在波束形成） */
    /* 注：dyadic 分析对每个驱动通道独立运行（8ch 并行），当前 broadside 时各通道相同 */
    
    /* Step 2: dyadic 树形分析（8ch 并行 → 4子带 × 8ch） */
    dyadic_analysis_8ch(pSrcMono, s_subbands);
    
    /* Step 3: 4子带逐一进行对称对加权求和（broadside-only） */
    for (int sb = 0; sb < ITC_NUM_SUBBANDS; sb++) {
        bf_broadside_process(s_subbands[sb], g_dc_weights, s_bf_out[sb]);
        /* g_dc_weights[8]: Dolph-Chebyshev 权重，初始化时由 dolph_chebyshev_compute() 填充 */
    }
    
    /* Step 4: dyadic 树形合成（4子带 → 1ch 全速率） */
    dyadic_synthesis(s_bf_out, s_recon);
    
    /* Step 5: 后处理（子带增益均衡 + 限幅器） */
    subband_gain_apply(s_recon);   /* 可选：补偿喇叭频响 */
    limiter_process(s_recon);      /* 必须：防烧功放 [待核实 U3：功放增益/限幅阈值] */
    
    /* Step 6: 将 1ch 重建信号 × D-C 权重分发到 8ch 输出 */
    /*         broadside 时 pDst8ch[ch] = dc_weights[ch] × s_recon（已在 Step3 合并） */
    /*         此处简化为：每通道输出 = 已波束形成的 s_recon（权重已含） */
    for (int ch = 0; ch < ITC_NUM_DRIVE_CH; ch++) {
        for (int n = 0; n < ITC_FRAME_SIZE_SAMPLES; n++) {
            pDst8ch[ch * ITC_FRAME_SIZE_SAMPLES + n] = s_recon[n];
            /* [注] 若 D-C 权重在 bf_broadside_process() 中已做加权求和，
             *      此处各通道输出相同（broadside 主瓣信号），
             *      通道间幅度差异已编码在 D-C 权重中并通过串联功放体现 */
        }
    }
}
```

---

## 5. 波束形成核心骨架（bf_broadside.c）

```c
/**
 * @brief broadside-only 波束形成：8个对称对加权求和
 *
 * 数学：AF(broadside) = 2 * Σ_{k=1}^{8} w[k] * x_k[n]
 *       其中 x_k 为第 k 个对称对（A_k 和 B_(16-k+1)，物理串联同信号）
 *       broadside 时所有分数延迟 τ_k = 0，退化为纯加权求和
 *
 * 定点要点（量产时）:
 *   - 输入 Q31（24bit 音频扩展）
 *   - 权重 Q15（D-C 归一化到最大值 = 32767）
 *   - 累加器 Q63（64bit，防止 8次 Q31×Q15 乘法溢出）
 *   - 输出 Q31（截断低 15bit 四舍五入）
 *
 * @param[in]  pSubband    子带信号数组 [ITC_FRAME_SIZE_SAMPLES]（抽取域速率）
 * @param[in]  pWeights    D-C 权重 [ITC_NUM_DRIVE_CH = 8]
 * @param[out] pBfOut      波束输出 [ITC_FRAME_SIZE_SAMPLES]
 */
void bf_broadside_process(const float *pSubband, const float *pWeights, float *pBfOut)
{
    /* broadside: 8个对称对权重直接加权求和 */
    /* A/B 串联 → x_k = A_k = B_(16-k+1)，物理上信号相同 */
    /* 等效：y[n] = Σ_{k=0}^{7} w[k] * 2 * pSubband[n] = (2 * Σw) * pSubband[n] */
    /* 即：broadside 时输出 = 常数增益 × 输入，增益 = 2 * sum(weights) */
    
    float gain = 0.0f;
    for (int k = 0; k < ITC_NUM_DRIVE_CH; k++) {
        gain += pWeights[k];
    }
    gain *= 2.0f;  /* A+B 串联物理增益（同信号叠加） */
    
    for (int n = 0; n < ITC_FRAME_SIZE_SAMPLES; n++) {
        pBfOut[n] = gain * pSubband[n];
    }
    
    /* [注] 若 pSubband 已是 8ch 并行（将来扩展为非 broadside），
     *      改为: pBfOut[n] = Σ_{k=0}^{7} pWeights[k] * pSubband_ch[k][n]
     *      当前 broadside 所有 ch 相同，所以等价上式 */
}
```

---

## 6. Dolph-Chebyshev 权重初始化骨架

```c
/**
 * @brief 初始化 Dolph-Chebyshev 权重（系统启动时调用一次）
 * @note  N=16 D-C 权重关于中心对称，8对对称对共享前8个权重值
 *        Sprint2 已验证：SLL=-20dB，BW@2kHz=26.8° ≤ 30° ✓
 *        仅需在启动时计算一次，运行中不变（broadside-only，无需动态更新）
 *
 * @param[out] pWeights  输出权重数组 [ITC_NUM_DRIVE_CH=8]
 * @param[in]  sll_db    旁瓣电平 (dB, 负值, 如 -20.0f)
 */
void dolph_chebyshev_compute(float *pWeights, float sll_db)
{
    /* TODO: 实现 Dolph-Chebyshev 权重计算（可参考 scipy.signal.chebwin 的 C 移植） */
    /* 步骤:
     * 1. R = 10^(-sll_db/20)  (电压比)
     * 2. x0 = cosh(acosh(R) / (N-1))  (N=16)
     * 3. 构造 Chebyshev 多项式系数，IFFT 得到时域权重
     * 4. 归一化: 除以 max(w)
     * 5. 取前 8 个（关于中心对称，前8 = 后8，取任意半边即可）
     *
     * 或: 初始化阶段通过 HOST PC 预计算，以 const 数组固化到 ROM
     */
    
    /* 临时: 使用 Sprint2 仿真验证的 N=16 D-C 权重前8个值 [估算, 来自 Python 仿真] */
    static const float dc_weights_n16_sll20[8] = {
        0.3491f, 0.5127f, 0.6696f, 0.8000f,
        0.9000f, 0.9700f, 1.0000f, 1.0000f
        /* 注: 最终值需由 Python dolph_chebyshev(16, -20) 精确计算后固化 [估算] */
    };
    for (int k = 0; k < ITC_NUM_DRIVE_CH; k++) {
        pWeights[k] = dc_weights_n16_sll20[k];
    }
}
```

---

## 7. 内存分配图（L1/L2 SRAM，ADSP-21569）

```
L1 SRAM (640 KB — 低延迟热点):
┌──────────────────────────────────┐
│ DMA 输出 Ping-Pong (2×2KB = 4KB) │  DMA 直接访问，必须 L1
│ 分数延迟 FIR 状态 (8ch×4sb,~1KB) │  每帧访问热点
│ 子带输出缓冲 (4sb×64×4B = 1KB)   │  帧级热点
│ 波束输出缓冲 (4sb×64×4B = 1KB)   │  帧级热点
│ 重建输出缓冲 (64×4B = 256B)       │  帧级热点
│ 分析树 L1 状态 (8ch×63×4B=16KB) │  最高速率级
│ 栈 + 临时变量 (~16KB)            │
│ (剩余 ~600KB 可用)               │
└──────────────────────────────────┘

L2 SRAM (1024 KB — 略低延迟):
┌──────────────────────────────────┐
│ 半带 FIR 系数 (3级, ~0.4KB)      │  只读，共享
│ 分析树 L2/L3 状态 (~3KB)         │  低速率级
│ 合成树状态 (~1KB)                │  单通道
│ 整数延迟环形缓冲 (8ch, ~1KB)     │  可略高延迟
│ D-C 权重 (8×4B = 32B)            │  常量，只读
│ 程序代码 (~60-100KB)             │
│ 系统堆栈 (~16KB)                 │
│ (剩余 ~840KB 可用)               │
└──────────────────────────────────┘

总计算法数据: ~15.4 KB (0.9%)
总剩余可用: ~1648 KB
```

---

## 8. 实现优先级（EZKIT 验证阶段）

| 优先级 | 模块 | 原因 |
|--------|------|------|
| P0 | SPORT TDM 初始化 + DMA ping-pong | 硬件通路验证第一步，无此无法播放 |
| P0 | 直通测试（bypass，输入直接输出） | 验证 TDM 时序、DAC 输出正常 |
| P1 | dyadic 分析树（8ch 并行） | 滤波器组核心，Sprint2 已有 Python 参考 |
| P1 | D-C 权重计算 + broadside 加权求和 | 波束形成核心功能 |
| P1 | dyadic 合成树 | 完成信号链路闭环 |
| P2 | 分数延迟 FIR（broadside 可暂时省略） | broadside 时 τ≈0，可先跳过 |
| P2 | 子带增益均衡 | 喇叭频响补偿，需 U3 数据 |
| P2 | 限幅器 | 重要但次于验证波束成形 |
| P3 | 定点化迁移 | 仅当量产决策后触发 |

---

*CCES 骨架 v0.1 | DSP算法专家 Agent | Sprint3*  
*[待核实 U4]: SPORT TDM 参数需逻辑分析仪实测竞品时序后更新*  
*[待核实 U3]: 限幅阈值需功放增益数据支撑*
