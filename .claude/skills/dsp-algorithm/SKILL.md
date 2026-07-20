---
name: dsp-algorithm
description: >-
  DSP algorithm expert for the ITC directional column speaker (ADSP-21569 SHARC+).
  Use for beamforming (DAS / subband / Dolph-Chebyshev) design, fixed-point (Qxx)
  porting and bit-exact verification, FIRA hardware-accelerator integration and
  postscale/Q-alignment, SHARC compute-budget / cycle / MCPS analysis, and the R14
  bit-exact closure work. Produces code as ASCII-only for the CCES SHARC target,
  change-blocks not full-file rewrites, and obeys CLAUDE.md governance (L-grading,
  C9/iron-rule-8 now RELEASED — R14 closed 2026-06-04; FIRA benefit enters selection
  under DEC-S4-C9-RELEASE-01's honest-denominator terms: pair with the §8 uncounted list
  (43-379 MCPS) and quote the official 3.07x, not 3.13x mixed-build).
---

<!-- CANONICAL source of record for the dsp-algorithm skill (DEC-S6-GOVERNANCE-SLIM-04,
     2026-07-20): the former 660-line copy at agents/dsp-algorithm/skill.md was reduced to a
     pointer — edit skill content ONLY here. Persona/memory: agents/dsp-algorithm/{profile,soul,memory}.md -->

---
name: "DSPAlgorithmAgent_Skill"
description: "DSP算法专家Agent的专业技能定义、工具使用规范、工作流与输入输出标准"
version: "1.0.0"
author: "ITC Enterprise Multi-Agent System"
---

# DSP算法专家Agent - 技能定义 (Skill)

## 1. 波束形成算法设计流程

### 1.1 算法设计完整流程

```
需求分析 → 算法选型 → 浮点原型 → 性能评估 → 定点化设计 → 定点实现 → 验证交付
```

### 1.2 算法选型决策矩阵

| 算法 | 干扰抑制 | 计算复杂度 | 鲁棒性 | 适用场景 | 推荐平台 |
|------|----------|------------|--------|----------|----------|
| **DSB (延迟求和)** | 无 | O(M) | 高 | 无干扰环境、固定波束 | 任何平台 |
| **MVDR** | 强 | O(M³) | 中 | 已知干扰方向、高SNR | 高性能DSP |
| **GSC** | 强 | O(M²) | 低-中 | 时变干扰、语音增强 | 高性能DSP |
| **子带MVDR** | 中-强 | O(K×M³/K_sub) | 中 | 宽带处理、降低复杂度 | 中等DSP |
| ** Frost** | 强 | O(M³) | 中 | 宽带阵列、线性约束 | 高性能DSP |
| **PCA/ICA** | 中 | O(M²×N) | 中 | 盲源分离、多说话人 | 高性能DSP |

> M = 阵元数, K = 子带数, N = 采样数, K_sub = 子带降采样因子

### 1.3 DSB (Delay-Sum Beamformer) 实现规范

```matlab
%% DSB 浮点MATLAB原型
function y = dsb_beamformer(x, d, c, fs, theta_steering)
% 输入:
%   x: M x N 输入信号矩阵 (M: 阵元数, N: 采样数)
%   d: 阵元间距 (m)
%   c: 声速 (m/s)
%   fs: 采样率 (Hz)
%   theta_steering: 波束指向角 (度)
% 输出:
%   y: 1 x N 波束形成输出

    M = size(x, 1);
    theta_rad = theta_steering * pi / 180;
    
    % 计算各阵元时延
    tau = (0:M-1)' * d * sin(theta_rad) / c;  % M x 1
    
    % 时延补偿 (频域实现)
    N_fft = 2^nextpow2(N);
    X = fft(x, N_fft, 2);  % M x N_fft
    
    omega = 2 * pi * (0:N_fft-1) * fs / N_fft;  % 1 x N_fft
    delay_phase = exp(-1j * omega .* tau);  % M x N_fft
    
    % 求和
    Y = sum(X .* delay_phase, 1) / M;  % 1 x N_fft
    y = real(ifft(Y, N_fft));
    y = y(1:N);  % 截取有效部分
end
```

**定点化要点：**
- 时延补偿通过分数延迟滤波器(Farrow/线性插值)实现
- 相位旋转使用CORDIC算法（避免直接计算exp()）
- 求和后的归一化通过右移实现（M为2的幂时）

### 1.4 MVDR 实现规范

```matlab
%% MVDR 浮点MATLAB原型
function y = mvdr_beamformer(x, d, c, fs, theta_target)
% MVDR最小方差无失真响应波束形成器

    M = size(x, 1);
    N = size(x, 2);
    
    % 导向矢量
    a = steering_vector(d, c, fs, M, theta_target);
    
    % 样本协方差矩阵估计
    R = x * x' / N;  % M x M
    
    % 对角加载保证可逆性
    R = R + 0.01 * trace(R) / M * eye(M);
    
    % MVDR权重
    R_inv = inv(R);
    w = R_inv * a / (a' * R_inv * a);  % M x 1
    
    % 波束形成
    y = w' * x;  % 1 x N
end
```

**定点化难点与策略：**
| 难点 | 定点化策略 | Q格式建议 |
|------|------------|-----------|
| 矩阵求逆 | LDL分解替代直接求逆 | Q31中间结果 |
| 数值稳定性 | 对角加载 + 条件数检查 | 动态调整加载量 |
| 大动态范围 | 块浮点或归一化中间结果 | 块指数跟踪 |
| 复数运算 | 分离实部/虚部分开计算 | Q15实部 + Q15虚部 |

### 1.5 GSC (Generalized Sidelobe Canceller) 实现规范

```
GSC架构:
┌─────────────┐     ┌──────────────────┐     ┌──────────┐
│  麦克风阵列  │────→│  阻塞矩阵 B (上)  │────→│ 自适应   │
│    信号 x   │     │  (消除目标信号)   │     │ 滤波器 w │
└─────────────┘     └──────────────────┘     └────┬─────┘
       │                                          │
       │         ┌──────────────┐                │
       └────────→│  约束权重 wq  │←───────────────┘
                 │ (固定波束)    │
                 └──────┬───────┘
                        │ y = wq'x - w'Bx
                        ↓
                     输出信号
```

**定点化要点：**
- 阻塞矩阵B通常为固定矩阵（可用简单的延迟差分实现）
- 自适应滤波器使用NLMS算法（定点友好）
- 步长μ选择：满足收敛条件的最大稳定值

---

## 2. 定点化实现流程

### 2.1 Q格式选择流程

```
Step 1: 信号动态范围分析
  └── 浮点仿真记录每个节点的最大绝对值
  └── 统计峰值和RMS值
  └── 考虑余量(Headroom): 峰值 × 1.25-2.0

Step 2: Q格式映射
  └── 根据动态范围和目标精度选择Q格式
  └── 常用选择:
      - 系数: Q15 (16bit) 或 Q31 (32bit)
      - 状态变量: Q15 或 Q31
      - 中间结果: Q31 或 Q63 (乘法后)
      - 数据样点: Q15 (16bit音频) 或 Q23 (24bit音频)

Step 3: 溢出分析
  └── 识别所有可能溢出的节点
  └── 设计饱和或缩放机制
  └── 最坏情况(WCET)路径重点检查

Step 4: 精度验证
  └── 与浮点参考对比
  └── 验收标准: SNR_loss < 1dB, 频响偏差 < 0.1dB
```

### 2.2 Q格式定义表模板

| 变量名 | 类型 | Q格式 | 范围 | 精度 | 溢出策略 | 备注 |
|--------|------|-------|------|------|----------|------|
| audio_in | int16 | Q15 | [-1, 0.99997] | 3.05e-5 | 饱和 | 音频输入 |
| audio_out | int16 | Q15 | [-1, 0.99997] | 3.05e-5 | 饱和 | 音频输出 |
| filter_coef | int16 | Q15 | [-1, 0.99997] | 3.05e-5 | N/A | FIR系数 |
| accumulator | int32 | Q31 | [-1, 0.9999999995] | 4.66e-10 | 饱和 | MAC累加器 |
| fft_twiddle | int16 | Q15 | [-1, 1] | 3.05e-5 | N/A | FFT旋转因子 |
| beam_weight | int32 | Q28 | [-8, 7.999] | 3.73e-9 | 饱和 | 波束权重 |

### 2.3 溢出分析流程

```c
// 溢出检测与饱和宏定义
typedef int16_t Q15;
typedef int32_t Q31;
typedef int64_t Q63;

// Q15乘法: Q15 × Q15 → Q31
#define Q15_MUL(a, b) ((Q31)(a) * (Q31)(b))

// Q31加法带饱和
static inline Q31 Q31_ADD_SAT(Q31 a, Q31 b) {
    Q63 sum = (Q63)a + (Q63)b;
    if (sum > INT32_MAX) return INT32_MAX;
    if (sum < INT32_MIN) return INT32_MIN;
    return (Q31)sum;
}

// Q15 → Q31 扩展
#define Q15_TO_Q31(x) ((Q31)(x) << 15)

// Q31 → Q15 截断（四舍五入）
#define Q31_TO_Q15_RND(x) ((Q15)(((x) + (1 << 14)) >> 15))
```

**溢出风险等级评估：**

| 风险等级 | 条件 | 处理方式 |
|----------|------|----------|
| **高** | 累加器(>16次累加)、反馈回路 | 必须饱和处理 + 缩放 |
| **中** | 乘法链(>2级)、系数较大 | 建议饱和处理 |
| **低** | 单次操作、系数<0.5 | 可选检查 |

### 2.4 精度验证规范

**逐bit对比流程：**
```
1. 准备相同输入测试向量（含边界条件）
2. 运行浮点MATLAB → 得到参考输出 ref[n]
3. 运行定点C代码 → 得到测试输出 test[n]
4. 计算误差: err[n] = ref[n] - test[n]
5. 统计指标:
   - 最大绝对误差: max|err[n]|
   - RMS误差: sqrt(mean(err²))
   - 信噪比: SNR = 10*log10(mean(ref²)/mean(err²))
6. 验收:
   - SNR ≥ 60dB (16bit系统) 或 ≥ 80dB (24bit系统)
   - 最大偏差 < 1 LSB (Q15) 或 < 2 LSB (放宽)
```

---

## 3. 心理声学算法

### 3.1 HRTF处理

**HRTF应用流程：**
```
输入: 单声道信号 + 方位角(θ) + 仰角(φ)
  ↓
HRTF选择/插值:
  ├── 数据库查询最近的测量方位
  ├── 双线性插值(4个最近方位)
  └── 或球谐函数分解(连续)
  ↓
双耳滤波:
  ├── 左耳: input * HRTF_L(θ,φ)
  └── 右耳: input * HRTF_R(θ,φ)
  ↓
输出: 立体声信号 (左, 右)
```

**定点化策略：**
- HRTF数据量缩减：PCA降维（保留99%能量，通常16-32个基函数）
- 时域FIR实现：256-512点（48kHz采样）
- 频域FFT重叠相加法：更低复杂度

### 3.2 空间音频 (Ambisonics)

| 阶数 | 通道数 | 声场分辨率 | 适用场景 | MIPS需求 |
|------|--------|------------|----------|----------|
| 1阶 (B-format) | 4 (W,X,Y,Z) | 低 | 简单沉浸 | 低 |
| 2阶 | 9 | 中 | 一般沉浸 | 中 |
| 3阶 | 16 | 高 | 高精度沉浸 | 高 |
| 4阶+ | 25+ | 很高 | 专业制作 | 很高 |

### 3.3 响度补偿算法

```c
// A-weighting 滤波器 (定点实现)
// 用于响度计权和声级计
// 双二阶级联实现

#define A_WEIGHT_NUM_STAGES 4

// 每个双二阶段的系数 (Q14格式, 范围[-2, 2))
typedef struct {
    Q15 b0, b1, b2;  // 分子系数
    Q15 a1, a2;      // 分母系数 (a0=1)
    Q31 s1, s2;      // 状态变量
} Biquad_State;

// A-weighting处理
Q15 a_weighting_process(Q15 input, Biquad_State stages[]) {
    Q31 acc;
    Q15 x = input;
    for (int i = 0; i < A_WEIGHT_NUM_STAGES; i++) {
        // 直接II型实现
        // y[n] = b0*x[n] + s1[n]
        // s1[n] = b1*x[n] + s2[n] - a1*y[n]
        // s2[n] = b2*x[n] - a2*y[n]
        acc = Q15_MUL(stages[i].b0, x) + stages[i].s1;
        stages[i].s2 = Q15_MUL(stages[i].b2, x) - Q15_MUL(stages[i].a2, (Q15)(acc >> 15));
        stages[i].s1 = Q15_MUL(stages[i].b1, x) + stages[i].s2 - Q15_MUL(stages[i].a1, (Q15)(acc >> 15));
        x = (Q15)(acc >> 15);  // Q31 → Q15
    }
    return x;
}
```

### 3.4 动态范围控制 (DRC)

**DRC参数规范：**

| 参数 | 说明 | 典型范围 | 定点Q格式 |
|------|------|----------|-----------|
| Threshold | 阈值 | -60dB ~ 0dB | Q15 (线性) |
| Ratio | 压缩比 | 1:1 ~ 20:1 | Q8 (比值) |
| Attack Time | 启动时间 | 0.1ms ~ 100ms | Q15 (ms) |
| Release Time | 释放时间 | 10ms ~ 5s | Q15 (ms) |
| Knee Width | 膝宽 | 0dB ~ 20dB | Q15 (dB) |
| Makeup Gain | 补偿增益 | 0dB ~ 30dB | Q15 (线性) |

**DRC定点实现架构：**
```
输入 → 电平检测(峰值/RMS) → 增益计算 → 平滑(Attack/Release) → 增益应用 → 输出
       (dB转换: LUT法)       (静态曲线)    (一阶IIR平滑)
```

---

## 4. 算法原型开发规范

### 4.1 MATLAB → C 代码生成流程

```
Step 1: MATLAB浮点原型
  └── 模块化函数设计
  └── 输入/输出接口标准化
  └── 完整的测试向量
  └── Git commit: "[ALGO-v1.0] Float prototype complete"

Step 2: Fixed-Point转换
  └── 使用 fi() 对象定义定点类型
  └── 逐步替换浮点运算为定点运算
  └── 每步验证与浮点一致
  └── Git commit: "[ALGO-v1.1] Fixed-point conversion"

Step 3: MATLAB Coder配置
  └── 代码生成目标: ANSI C
  └── 优化级别: 平衡速度与可读性
  └── 定点类型映射: int16_t/int32_t/int64_t
  └── 生成代码风格: MISRA-C兼容

Step 4: C代码生成与验证
  └── 生成C源代码
  └── 编译为目标平台
  └── 运行相同测试向量
  └── 逐bit对比输出
  └── Git commit: "[ALGO-v1.2] C code generated and verified"

Step 5: 手工优化
  └── 关键路径内联汇编（如需要）
  └── 循环展开
  └── SIMD优化（如平台支持）
  └── 重新验证
  └── Git commit: "[ALGO-v1.3] Hand-optimized for [platform]"
```

### 4.2 代码规范

**命名规范：**
```c
// 函数: Module_ActionDetail
dsp_bf_mvdr_process();      // 波束形成-MVDR-处理
dsp_eq_biquad_process();    // 均衡器-双二阶-处理
dsp_drc_compress();         // DRC-压缩

// 变量: module_varName
dsp_bf_numElements;         // 波束形成-阵元数
dsp_fp_format;              // 定点-格式

// 宏: MODULE_ACTION_DETAIL
#define DSP_BF_MAX_ELEMENTS 16
#define DSP_Q15_ONE 32767
#define DSP_Q31_ONE 2147483647
```

**注释规范：**
```c
/**
 * @brief MVDR波束形成处理函数
 * @param[in] pIn 输入信号缓冲区 (M通道 x N采样)
 * @param[out] pOut 输出信号缓冲区 (N采样)
 * @param[in] pConfig 波束形成配置参数
 * @return 处理采样数, 负值表示错误
 * 
 * @note 定点格式: 输入Q15, 权重Q28, 输出Q15
 * @note MIPS: ~2.3ms/frame @ 48kHz, 8阵元
 * @warning 必须保证pIn已对齐到8字节边界
 */
int32_t dsp_bf_mvdr_process(const Q15 *pIn, Q15 *pOut, 
                            const BfMvdrConfig_t *pConfig);
```

---

## 5. 性能指标定义

### 5.1 MIPS (Million Instructions Per Second)

```
MIPS_calculation:
  方法: 代码插桩 / 芯片Profiler
  指标: 
    - 平均MIPS: 典型输入下的平均负载
    - 峰值MIPS: 最坏情况输入下的峰值负载
    - WCET: 最坏执行时间 (必须 ≤ 时间槽)
  
  预算管理:
    可用MIPS = 芯片总MIPS × 0.85 (留15%裕量)
    算法MIPS ≤ 可用MIPS × 0.70 (单算法不超过70%)
    系统总MIPS ≤ 可用MIPS × 0.85 (所有算法合计)
```

### 5.2 Memory (内存)

| 内存类型 | 用途 | 典型大小 | 优化策略 |
|----------|------|----------|----------|
| **代码空间 (ROM)** | 程序指令 | 依算法复杂度 | 函数复用、共享库 |
| **常量数据 (ROM)** | 系数表、LUT | 10-100KB | LUT压缩、插值 |
| **静态RAM** | 状态变量、缓冲区 | 5-50KB | 缓冲区复用 |
| **栈空间** | 函数调用、局部变量 | 1-10KB | 避免大数组局部声明 |
| **堆空间** | 动态分配 | 尽量避免 | 预分配固定大小 |

### 5.3 Latency (延迟)

**延迟组成分析：**
```
Total_Latency = T_adc + T_buffer + T_process + T_dac + T_link

其中:
  T_adc: ADC转换延迟 (通常 < 1 sample)
  T_buffer: 帧缓冲区延迟 (frame_size / fs)
  T_process: 算法处理延迟 (通常 < 1 frame)
  T_dac: DAC转换延迟 (通常 < 1 sample)
  T_link: 数字链路延迟 (I2S/TDM等)
```

**延迟预算模板：**
| 系统类型 | 总延迟预算 | 算法延迟分配 | 帧大小 |
|----------|------------|-------------|--------|
| 专业音响 | < 5ms | < 2ms | 32-64 samples |
| 会议系统 | < 20ms | < 5ms | 128-256 samples |
| 消费电子 | < 40ms | < 10ms | 256-512 samples |
| 助听器 | < 10ms | < 3ms | 64-128 samples |

### 5.4 SNR (信噪比)

```
SNR_metrics:
  浮点SNR: 浮点算法处理的理论SNR
  定点SNR: 定点实现的实际SNR
  SNR_loss: 定点化导致的SNR损失 = SNR_float - SNR_fixed
  
  验收标准:
    - SNR_loss ≤ 1dB: 优秀
    - 1dB < SNR_loss ≤ 3dB: 可接受
    - SNR_loss > 3dB: 需优化
    
  测量方法:
    输入: 标准测试信号（如-1dBFS正弦波扫频）
    输出: 与理想输出比较
    计算: SNR = 10*log10(signal_power / noise_power)
```

---

## 6. 跨Agent协作接口

### 6.1 与声学仿真Agent协作

**接口名称**: `collab_acoustic_agent`
**协作模式**: 闭环优化

```yaml
# 声学仿真Agent → DSP算法Agent
receive_acoustic_constraints:
  trigger: "声学仿真完成，约束条件可用"
  data_format:
    constraints_id: "AC-2024-001"
    array_config:
      type: "linear"
      n_elements: 8
      spacing_mm: 100
      element_frequency_range: [100, 15000]
    
    directivity_requirements:
      coverage_1kHz: "±30deg"
      coverage_4kHz: "±15deg"
      max_sidelobe: "-12dB"
      beam_steering_range: "±30deg"
      
    acoustic_transfer_function:
      file: "array_tf_8x100mm.csv"
      description: "阵列频率响应(未加权)"
      
    dsp_implications:
      eq_required: true           # 需要EQ补偿
      beamformer_required: true    # 需要波束形成
      max_delay_us: 2900          # 最大阵内时延 (us)
      min_process_frequency: 800  # 波束控制有效频率下限(Hz)

# DSP算法Agent → 声学仿真Agent
request_acoustic_feedback:
  trigger: "需要验证算法声学效果"
  request:
    simulation_type: "array_with_dsp_weights"
    weights_file: "dsp_weights_8ch.csv"
    frequencies: [250, 500, 1000, 2000, 4000, 8000]
    output_requests:
      - "directivity_polar_plot"
      - "frequency_response"
      - "beamwidth_vs_frequency"
      
  expected_response:
    turnaround_time: "24 hours"
    format: "simulation_report + csv data"
```

### 6.2 与硬件设计Agent协作

**接口名称**: `collab_hardware_agent`
**协作模式**: 协同定点化

```yaml
# 硬件设计Agent → DSP算法Agent
receive_dsp_chip_spec:
  trigger: "DSP芯片选型确定"
  spec_format:
    chip_model: "ADAU1467 / CS49xxx / Tensilica HiFi4"
    core_clock_mhz: 294.912
    total_mips: 600
    
    memory:
      data_ram_kb: 320
      program_ram_kb: 128
      rom_kb: 0
      external_ram_mb: 8
      
    processing_features:
      hardware_multiplier: true      # 单周期乘法
      hardware_divider: false        # 软件除法
      simd_support: true             # 双16bit SIMD
      fft_accelerator: true          # FFT硬件加速
      
    audio_interface:
      max_sample_rate_khz: 48
      max_channels: 32
      word_length: 24
      
    algorithm_budget:
      allocated_mips: 400           # 分配给算法的MIPS
      allocated_ram_kb: 200         # 分配给算法的RAM
      max_latency_ms: 5             # 最大允许延迟
      frame_size_samples: 128       # 帧大小

# DSP算法Agent → 硬件设计Agent
send_fixed_point_spec:
  trigger: "定点化规格确定"
  spec_content:
    memory_map:
      code_size_bytes: 45000
      data_ram_usage_bytes: 180000
      stack_usage_bytes: 4096
      heap_usage_bytes: 0           # 无动态分配
      
    cpu_requirements:
      estimated_mips: 380
      peak_mips_scenario: "MVDR_update @ 8 channels"
      wcet_us: 2200
      
    peripheral_requirements:
      dma_channels: 4
      interrupt_priority: 2
      timer_required: true
      
    power_estimate:
      dynamic_mw: 150
      static_mw: 50
      
    clock_requirements:
      core_clock_min_mhz: 250
      pll_configuration: "PLL1: 294.912MHz"
```

### 6.3 与评审Agent协作

**接口名称**: `submit_for_review`
**协作模式**: 正式交付

```yaml
review_package:
  trigger: "算法开发完成，自检通过"
  contents:
    design_document: "algorithm_design_doc.md"
    matlab_float: "algo_float_v1_0.m"
    matlab_fixed: "algo_fixed_v1_0.m"
    c_source: 
      - "dsp_algo.c"
      - "dsp_algo.h"
    c_test: 
      - "test_algo.c"
      - "test_vectors.h"
    fixed_point_spec: "fixed_point_spec.md"
    performance_report: "perf_report.md"
    verification_report: "verification_report.md"
    
  review_checklist:
    algorithm:
      - 数学正确性
      - 参数选择合理性
      - 边界条件处理
      - 稳定性分析
      
    fixed_point:
      - Q格式选择合理性
      - 溢出防护完整性
      - 精度损失可接受
      - 与浮点对比通过
      
    code_quality:
      - 代码规范合规
      - 注释完整性
      - 可维护性
      - 可测试性
      
    performance:
      - MIPS预算满足
      - 内存预算满足
      - 延迟预算满足
      - 资源利用率合理
```

---

## 7. 算法验证流程

### 7.1 仿真数据验证

```
Step 1: 单元测试
  └── 每个函数独立测试
  └── 边界条件: min, max, zero, NaN, Inf
  └── 白噪声输入测试
  └── 正弦扫频测试
  └── 输出: 单元测试报告

Step 2: 集成测试
  └── 完整信号链路测试
  └── 典型场景测试向量
  └── 极端场景测试向量
  └── 长时间稳定性测试 (>1小时)
  └── 输出: 集成测试报告

Step 3: 声学验证
  └── 与声学仿真数据闭环验证
  └── 定向精度验证（如波束形成）
  └── 频率响应验证
  └── 输出: 声学验证报告
```

### 7.2 实时原型验证

| 验证项 | 方法 | 通过标准 | 工具 |
|--------|------|----------|------|
| 实时性 | 帧处理时间测量 | WCET < 帧周期 | Profiler/Oscilloscope |
| 音频质量 | 正弦/噪声/音乐测试 | THD+N < 目标 | APx555/音频分析仪 |
| 功能正确 | 对比参考实现 | bit-exact 或 SNR>60dB | 示波器+MATLAB |
| 稳定性 | 长时间运行 | 无崩溃、无异常输出 | 自动化测试 |
| 资源使用 | 内存/CPU监控 | 在预算内 | IDE Profiler |