---
name: "DSPAlgorithmAgent_Memory"
description: "DSP算法专家Agent的记忆存储 - 算法库、芯片适配经验、定点化陷阱库与听觉测试反馈"
version: "1.0.0"
author: "ITC Enterprise Multi-Agent System"
---

# DSP算法专家Agent - 记忆存储 (Memory)

## 1. 算法库 (Algorithm Library)

### 1.1 经典波束形成算法

#### DSB (Delay-Sum Beamformer)
```yaml
algo_id: "BF_DSB_v2.1"
name: "延迟求和波束形成器"
category: "beamforming"
type: "fixed_beam"

specification:
  input_channels: "M (configurable, 2-32)"
  output_channels: 1
  sample_rate: "8-48kHz"
  
  parameters:
    - name: steering_angle
      range: "-90 to +90 degrees"
      resolution: "1 degree"
      format: "int16, Q15 (normalized to 90deg)"
    - name: element_spacing_mm
      range: "10 to 500 mm"
      format: "uint16"
    - name: speed_of_sound
      default: 343
      unit: "m/s"
      
  complexity:
    mips_per_channel: "~5 MIPS @ 48kHz"
    memory_kb: "~2KB + M × 256B (delay lines)"
    latency_samples: "max_delay + filter_order"
    
  implementation:
    core: "分数延迟滤波器 (Farrow/线性插值)"
    optimization: "查表cos/sin, 延迟线环形缓冲区"
    
  performance:
    snr_improvement: "10*log10(M) dB (理论)"
    typical_snr: "10*log10(M) - 1 dB"
    
  status: "production_ready"
  platforms_verified: ["ADAU1467", "HiFi4", "SHARC21569"]
  last_updated: "2024-01-15"
```

#### MVDR (Minimum Variance Distortionless Response)
```yaml
algo_id: "BF_MVDR_v1.8"
name: "MVDR自适应波束形成器"
category: "beamforming"
type: "adaptive"

specification:
  input_channels: "M (configurable, 4-16)"
  output_channels: 1
  sample_rate: "8-48kHz"
  
  parameters:
    - name: target_direction
      range: "-90 to +90 degrees"
    - name: diagonal_loading
      default: "0.01 × trace(R)"
      range: "0.001 to 0.1"
    - name: covariance_window
      default: "1024 samples"
      range: "256 to 4096"
      
  complexity:
    mips: "~50-200 MIPS (M-dependent, O(M³))"
    memory_kb: "~10KB + M² × 4B (covariance matrix)"
    latency_samples: "covariance_window"
    
  implementation:
    core: "LDL分解 + 权重计算"
    optimization: "增量式协方差更新, 对称矩阵优化"
    
  performance:
    interference_rejection: "20-40dB (取决于场景)"
    snr_improvement: "15-25dB (有干扰时)"
    tracking_speed: "~100ms (典型收敛)"
    
  status: "production_ready"
  platforms_verified: ["SHARC21569", "HiFi4"]
  notes: "ADAU1467上M>8时MIPS紧张, 建议用子带降采样"
```

#### GSC (Generalized Sidelobe Canceller)
```yaml
algo_id: "BF_GSC_v1.3"
name: "广义旁瓣抵消器"
category: "beamforming"
type: "adaptive"

specification:
  input_channels: "M (4-16)"
  adaptive_filter: "NLMS"
  
  parameters:
    - name: nlms_step_size
      default: 0.01
      range: "0.001 to 0.1"
      format: "Q15"
    - name: nlms_filter_length
      default: 64
      range: "16 to 256"
      
  complexity:
    mips: "~30-80 MIPS"
    memory_kb: "~5KB + (M-1) × L_nlms × 2B"
    
  status: "production_ready"
  known_issues:
    - "信号泄漏问题: 阻塞矩阵不完全时目标信号泄漏到噪声支路"
    - "缓解: 使用阻塞矩阵校准 + 泄漏因子<0.1"
```

### 1.2 自适应滤波算法

| 算法 | 收敛速度 | 稳态误差 | MIPS | 内存 | 鲁棒性 | 推荐场景 |
|------|----------|----------|------|------|--------|----------|
| LMS | 慢 | 高 | 低 | 低 | 高 | 平稳环境 |
| NLMS | 中 | 中 | 低 | 低 | 高 | **通用推荐** |
| RLS | 快 | 低 | 高 | 高 | 低 | 快速变化 |
| APA | 快 | 低 | 中 | 中 | 中 | 回声消除 |
| 频域LMS | 中 | 中 | 中 | 中 | 中 | 长滤波器 |

**NLMS定点实现参考：**
```yaml
algo_id: "AF_NLMS_v3.0"
name: "归一化最小均方自适应滤波"

fixed_point_details:
  input: Q15
  weights: Q15
  step_size: Q15 (mu = 0.01 ~ 0.1)
  power_estimate: Q31 (能量归一化)
  error: Q15
  
  critical_path:
    - 误差计算: e = d - w'× (Q31累加→Q15)
    - 功率估计: P = x'× + lambda (Q31)
    - 归一化步长: mu_eff = mu / P (除法→LUT)
    - 权重更新: w = w + mu_eff × e × x (Q31中间)
    
  overflow_risks:
    - "权重累加: 必须饱和"
    - "功率估计: 必须检查零除"
    - "除法: 使用Newton-Raphson或LUT"
```

### 1.3 空间音频算法

#### Ambisonics B-format 编解码
```yaml
algo_id: "SA_AMB_v1.5"
name: "Ambisonics B-format处理"

encoder:
  input: "单声道源 + 方位角θ + 仰角φ"
  output: "W, X, Y, Z 四通道"
  coefficients:
    W: 1/sqrt(2)  (Q15: 23170)
    X: cos(θ)cos(φ)
    Y: sin(θ)cos(φ)
    Z: sin(φ)
  sin/cos: "CORDIC算法或LUT + 线性插值"
  
decoder:
  input: "WXYZ + 扬声器布局"
  output: "N通道扬声器信号"
  method: "伪逆解码矩阵"
  speaker_layouts_supported:
    - "5.1声道标准布局"
    - "7.1声道标准布局"
    - "四声道正方形"
    - "自定义布局 (需提供坐标)"
```

#### VBAP (Vector Base Amplitude Panning)
```yaml
algo_id: "SA_VBAP_v1.2"
name: "矢量基振幅声像"

inputs: "虚拟源方位角 + 扬声器布局三角网格"
outputs: "参与放音的扬声器增益"

process:
  step1: "找到虚拟源所在的三角面"
  step2: "计算2D/3D增益系数 (g1, g2, g3)"
  step3: "归一化: g_norm = g / sqrt(g1²+g2²+g3²)"
  step4: "输出到对应扬声器"
  
fixed_point:
  gain_resolution: "Q15, 1/32768 ≈ 0.003%"
  sqrt: "Newton-Raphson迭代或LUT"
  sin/cos: "LUT 1024点 + 线性插值"
```

---

## 2. 芯片平台适配经验 (Platform Adaptation Knowledge)

### 2.1 ADAU1467 (SigmaDSP)

```yaml
platform: "ADAU1467"
manufacturer: "Analog Devices"
category: "中等复杂度音频DSP"

capabilities:
  core_clock: "294.912 MHz"
  effective_mips: ~600
  data_ram: "320KB"
  program_ram: "128KB"
  max_sample_rate: "192kHz"
  max_channels: "48 in / 48 out"
  word_length: "28bit (5.23 format内部)"
  
dsp_features:
  hardware_multiplier: true
  hardware_divider: false
  hardware_sqrt: false
  fft_accelerator: true
  biquad_accelerator: true
  
algo_constraints:
  max_biquads: "~2000 (实时)"
  max_fft_size: "4096"
  division: "software (slow, avoid)"
  sqrt: "software or LUT"
  
successful_algos:
  - "DSB波束形成 (M<=8)"
  - "8段PEQ"
  - "动态范围控制"
  - "延迟补偿"
  - "Ambisonics B-format"
  
challenging_algos:
  - "MVDR: M>4时MIPS不足"
  - "自适应滤波: 收敛速度受限"
  - "高精度FFT: 28bit精度需特别注意"
  
lessons_learned:
  - "5.23定点格式不同于标准Q格式, 转换需谨慎"
  - "硬件除法缺失: 所有除法用LUT+插值或移位替代"
  - "FFT加速器必须使用指定API, 不能直接访问"
  - "程序内存128KB紧张, 代码复用至关重要"
  - "数据RAM 320KB对多通道波束形成够用但需精打细算"
```

### 2.2 Tensilica HiFi4

```yaml
platform: "Tensilica HiFi4"
manufacturer: "Cadence"
category: "高性能音频DSP"

capabilities:
  core_clock: "up to 600MHz"
  effective_mips: ~1200
  simd: " dual 24x24 MAC per cycle"
  data_cache: "configurable"
  instruction_cache: "configurable"
  
dsp_features:
  hardware_multiplier: true
  hardware_divider: true
  hardware_sqrt: true
  fft_accelerator: true
  simd_support: true
  
successful_algos:
  - "MVDR波束形成 (M<=16)"
  - "NLMS自适应滤波"
  - "3阶Ambisonics"
  - "高阶均衡器(31段)"
  - "复杂DRC多段"
  
optimization_tips:
  - "SIMD双24bit MAC非常适合音频处理"
  - "循环展开配合编译器pragma获得最优性能"
  - "使用HiFi4专用intrinsics: AE_MULF32R_LL等"
  - "Cache友好数据结构: 连续访问优于随机访问"
  - "32x32乘法使用双精度MAC指令"
```

### 2.3 SHARC ADSP-21569

> ✅ **铁律④ 重审已闭环（2026-06-02 datasheet 坐实，PM 更新；critic C1 已验证引用真实）** —— 本条三项**两错一对**，下方 yaml 已逐行更正：
> - ❌ `architecture: dual SHARC+ cores` = **错**。Datasheet 坐实 **ADSP-21569 = SHARC+ 单核**（ds.txt:153 "based on the SHARC+ single core"；驱动 CFG `DUAL_CORE_MODE` 对 21569 "not supported"）。与 DEC-S3-PROC-01 / `dsp-chip-decision.md` 一致，旧 yaml 是离群错值。
> - ✅ `category: 浮点DSP` / `float_support` = **对**。21569 **确有硬件浮点**（IEEE 32/40/64-bit，ds.txt:9）。
> - ⚠️ `定点化非必须` = **路线选择问题，非硬件强制**。芯片虽支持浮点，但项目 **LOCKED 走定点**（DEC-S3-PROC-01，MCPS 效率）；FIRA 硬件**定点+浮点双模式都支持**（见 `sprint3/audit/fira_fit_assessment.md` §3），故定点路线合法可保留。**全部 PF-4 定点闭环工作有效。**
> - 17×(16ch)/33×(8ch) 桌面算力 [L2] 按**单核定点纯软件**算，**不含 FIRA offload**（fira 评估 §4.3 已确认）→ R1 上板实测口径不变。
> 出处：`sprint3/audit/fira_fit_assessment.md` §5（critic PASS_WITH_MINOR→PASS）。下方 yaml 红线项已就地标注。

```yaml
platform: "ADSP-21569"
manufacturer: "Analog Devices"
category: "浮点DSP"

capabilities:
  core_clock: "1GHz"
  architecture: "single SHARC+ core"   # ← 已更正（原写 dual，错；ds:153 单核坐实 2026-06-02）
  float_support: "native 32/40bit float"   # ← 坐实正确（ds:9 IEEE 32/40/64bit）
  internal_ram: "5Mb"
  
dsp_features:
  hardware_floating_point: true
  hardware_multiplier: true
  iir_accelerator: true
  fft_accelerator: true
  
algo_advantages:
  - "浮点原生支持: 算法移植最容易"
  - "大容量RAM: 复杂算法无内存压力"
  # - "双核: 算法可分配到两个核"   ← 已删除（21569 单核，此优势不成立，ds:153）
  - "高主频: 计算密集型算法首选"
  
disadvantages:
  - "功耗较高: 不适合电池供电"
  - "成本较高: 高端产品定位"
  - "定点化非必须: 但量产时可能需考虑成本"
  
use_cases:
  - "专业音响波束形成"
  - "多通道回声消除"
  - "高精度空间音频"
  - "研发阶段浮点验证平台"
```

### 2.4 芯片选型速查表

| 应用场景 | 推荐芯片 | 理由 | 成本等级 |
|----------|----------|------|----------|
| 消费级智能音箱 | ADAU1467 | 成本适中, 功能足够 | 中 |
| 专业会议系统 | HiFi4 / SHARC21569 | 高MIPS, 多通道 | 高 |
| 便携/电池供电 | HiFi3 / 专用低功耗 | 功耗优先 | 中 |
| 车载音响 | ADAU1467 / 车规级 | 可靠性认证 | 中高 |
| 研发验证平台 | SHARC21569 | 浮点易调试 | 高 |
| 助听器 | 专用低功耗DSP | 超低延迟, 超低功耗 | 高 |

---

## 3. 定点化陷阱库 (Fixed-Point Pitfalls)

### 3.1 常见溢出场景

#### Pitfall-001: FIR滤波器累加溢出
```yaml
id: "FP_001"
title: "FIR滤波器MAC累加溢出"
frequency: "高"
severity: "高"

scenario: "N阶FIR滤波器, N×Q15乘法累加至Q31累加器"

root_cause: "累加器位宽不足, N次累加超出Q31范围"

trigger_condition: "输入信号较大 + 滤波器系数有正值增益 + 阶数>64"

example:
  filter_order: 128
  max_input: 0.5 (Q15: 16384)
  max_coef: 0.3 (Q15: 9830)
  max_product: 0.15 (Q31: ~3.2e8)
  max_sum: 128 × 3.2e8 = 4.1e10 > INT32_MAX(2.15e9)
  result: "溢出!"

solutions:
  - method: "累加前缩放"
    detail: "每次累加后右移1bit (精度换范围)"
    tradeoff: "精度损失6dB"
  - method: "分块累加+二次求和"
    detail: "每32个乘积分块, 中间结果缩放"
    tradeoff: "复杂度略增, 精度较好"
  - method: "使用Q63累加器"
    detail: "64bit累加, 结果后缩放"
    tradeoff: "需要64bit支持, 速度略慢"
    
prevention: "所有FIR实现必须做最坏情况累加分析"
```

#### Pitfall-002: IIR滤波器极限环
```yaml
id: "FP_002"
title: "IIR滤波器定点极限环振荡"
frequency: "中"
severity: "中"

scenario: "二阶IIR(SOS)滤波器, Q15系数和状态变量"

root_cause: "量化非线性导致零输入时持续振荡"

trigger_condition: "高Q值极点 + 低输入电平 + 有限字长"

symptoms: "零输入时输出有-40dB至-60dB噪声"

solutions:
  - method: "增加状态变量精度至Q31"
    effectiveness: "显著改善"
  - method: "使用三角型/格型结构替代直接型"
    effectiveness: "结构本身抑制极限环"
  - method: "dither注入"
    effectiveness: "打散极限环, 转为宽带噪声"
  - method: "级联二阶节替代高阶直接型"
    effectiveness: "级联结构更稳定"
    
prevention: "所有IIR必须做零输入测试, 检查极限环"
```

#### Pitfall-003: 除法精度损失
```yaml
id: "FP_003"
title: "定点除法精度损失"
frequency: "高"
severity: "中"

scenario: "归一化运算、功率估计归一化等需要除法"

root_cause: "DSP无硬件除法, 软件实现精度有限"

problems:
  - "Newton-Raphson初始值敏感, 收敛慢"
  - "LUT占用内存大且插值误差"
  - "移位近似仅在除数为2的幂时精确"

best_practices:
  - "避免除法: 用乘法替代 (a/b = a × (1/b))"
  - "预计算倒数LUT: 分段线性插值"
  - "Newton-Raphson: 3次迭代, 初始值用LUT"
  - "归一化: 用CORDIC算法替代除法"
```

#### Pitfall-004: FFT位反转地址计算
```yaml
id: "FP_004"
title: "FFT位反转索引越界"
frequency: "低"
severity: "高"

scenario: "FFT/IFFT实现, 输出重排时的位反转寻址"

root_cause: "位反转函数对非2的幂FFT大小处理错误"

impact: "输出数据顺序错误, 导致后续处理完全错误"

prevention:
  - "FFT大小强制为2的幂"
  - "位反转函数用查表法 (预计算反转索引)"
  - "单元测试中验证输出顺序"
```

### 3.2 精度损失模式

| 损失来源 | 影响程度 | 量化方法 | 缓解策略 |
|----------|----------|----------|----------|
| 系数量化 | 高 | Q15: ~0.003%精度 | 使用Q31或浮点系数 |
| 乘法截断 | 中 | Q31→Q15丢弃低16bit | 四舍五入替代直接截断 |
| 加法舍入 | 低 | 多次加法累积 | 扩大累加器位宽 |
| 除法近似 | 高 | LUT插值误差 | 增加LUT点数或使用迭代 |
| 非线性函数 | 中 | LUT+插值 | 增加LUT分辨率或分段 |
| 反馈量化 | 高 | IIR状态变量量化 | 增加状态精度或改变结构 |

---

## 4. 听觉测试反馈记录 (Listening Test Feedback)

### 4.1 主观评价数据库

#### Test-001: DSB波束形成语音清晰度
```yaml
test_id: "LISTEN_2024_001"
date: "2024-02-15"
testers: 8
method: "MUSHRA (ITU-R BS.1534)"

conditions:
  - name: "Reference"
    description: "近讲麦克风录音"
  - name: "DSB_8ch"
    description: "8通道DSB波束形成"
  - name: "DSB_4ch"  
    description: "4通道DSB波束形成"
  - name: "Hidden_Reference"
  - name: "Anchor_7kHz"

results:
  Reference: 100
  DSB_8ch: 85
  DSB_4ch: 72
  Hidden_Reference: 98
  Anchor: 25
  
conclusions:
  - "8通道DSB语音清晰度良好, 接近参考"
  - "4通道在噪声环境下清晰度下降明显"
  - "建议会议系统使用≥8通道"
  - "低频(<200Hz)有轻微染色, 建议后接HPF"
```

#### Test-002: MVDR vs DSB 干扰抑制主观对比
```yaml
test_id: "LISTEN_2024_005"
date: "2024-03-20"
testers: 6
method: "ABX测试"

conditions:
  - scene: "会议室, 目标说话人前方, 干扰说话人侧方60°"
  - signal: "目标语音 + 干扰语音(同音量)"
  
results:
  DSB:
    interference_audible: "明显可闻"
    target_clarity: "受干扰影响大"
    preference_score: 30
  MVDR:
    interference_audible: "几乎不可闻"
    target_clarity: "清晰"
    preference_score: 85
  
conclusions:
  - "MVDR干扰抑制效果显著优于DSB"
  - "MVDR偶有语音失真(音乐噪声)"
  - "建议在强干扰场景使用MVDR"
  - "可结合: MVDR + 后处理去噪"
```

### 4.2 客观-主观相关性记录

| 算法 | 客观SNR(dB) | 主观MOS | 相关性 | 异常说明 |
|------|-------------|---------|--------|----------|
| DSB 8ch | 12.5 | 4.2 | 强 | 无 |
| MVDR 8ch | 18.3 | 4.5 | 强 | 无 |
| GSC 8ch | 16.8 | 4.0 | 中 | 音乐噪声降低MOS |
| 子带MVDR | 15.2 | 4.3 | 强 | 子带 Artifact 轻微 |
| 频域BF | 14.0 | 3.8 | 中 | 相位不连续问题 |

**关键发现：**
- SNR提升>3dB不一定对应主观改善（音乐噪声问题）
- 相位连续性对主观感受影响大于幅度精度
- 瞬态响应（Attack）比稳态响应更重要

### 4.3 听觉优化经验

```yaml
listening_optimization_tips:
  - "波束形成后加1-2dB低频提升(补偿阵列低频损失)"
  - "自适应算法收敛期间使用DSB输出(避免收敛期失真)"
  - "限制自适应权重更新幅度(防止过度适应)"
  - "双声道输出比单声道更自然(即使单声道信号)"
  - "轻微混响(<50ms)增加自然感"
  - "避免硬削波, 使用软压缩(听感更自然)"
  - "切换算法时交叉淡化(避免咔嗒声)"
```

---

## 5. 项目经验积累

### 5.1 已完成项目清单

| 项目ID | 名称 | 算法内容 | 芯片平台 | 状态 | 关键经验 |
|--------|------|----------|----------|------|----------|
| PRJ-2024-001 | 会议线阵 | DSB+EQ | ADAU1467 | 量产 | 8ch DSB在294MHz下稳定运行 |
| PRJ-2024-003 | 智能音箱 | AEC+NR | HiFi4 | 量产 | NLMS+频域NR组合效果最佳 |
| PRJ-2024-007 | 教堂扩声 | MVDR+EQ | SHARC21569 | 试产 | 大房间MVDR对角加载需增大 |
| PRJ-2024-010 | 车载阵列 | BF+ANC | HiFi4 | 开发中 | 风噪场景需特殊处理 |
| PRJ-2024-012 | 便携音箱 | VBAP | ADAU1467 | 设计 | 两声道VBAP简化版可行 |

### 5.2 设计复用指数

```yaml
design_reuse_statistics:
  dsb_core: 
    original_projects: 5
    reuse_count: 12
    reuse_rate: "71%"
    
  eq_biquad:
    original_projects: 8
    reuse_count: 25
    reuse_rate: "76%"
    
  drc_compressor:
    original_projects: 4
    reuse_count: 10
    reuse_rate: "71%"
    
  nlms_af:
    original_projects: 3
    reuse_count: 6
    reuse_rate: "67%"
    
  mvdr_bf:
    original_projects: 2
    reuse_count: 3
    reuse_rate: "60%"
    
overall_reuse_target: "> 65%"
```

---

## 6. 学习与发展计划

| 时间 | 学习内容 | 应用场景 | 优先级 |
|------|----------|----------|--------|
| 2024 Q3 | 神经网络音频增强(DNS) | 降噪升级 | 高 |
| 2024 Q3 | 自适应波束形成RLS快速算法 | 专业音响 | 中 |
| 2024 Q4 | 多通道AEC联合优化 | 会议系统 | 高 |
| 2024 Q4 | 对象音频渲染引擎 | 沉浸音频 | 中 |
| 2025 Q1 | 边缘AI推理优化 | 智能音频 | 高 |
| 2025 Q1 | 自动增益控制AGC高级算法 | 广播/会议 | 低 |

---

## 7. 阶段 4 bring-up 教训（2026-06-06, R24-R34 — 板上返工换来的）

> 完整清单：`sprint6/STAGE4_BRINGUP_CHECKLIST.md`（开工前过一遍）。本节是 dsp 侧速记。

1. **先查后写（MDMA 9-error 教训）**：BSP 符号先在本地 KB 例程找实调 [L1-example-called]；没实调的 [board-confirm] 占位+TODO。离线推测写板代码 = 一轮返工。
2. **header 后缀非对称**：adi_sport.h（无后缀）/adi_twi_2156x.h/adi_spu_v3.h 三种命名并存，且同名双版并存——逐 driver 在安装版 include 树确认确切头名。
3. **缓冲放置 = 效度命门**：测量缓冲与被测工作集同 L1 block = 自冲突假象。.map 双重裁定（.ldf 段边界+芯片窗口），pragma seg_l1_block1 是 ADI 例程同款修法。
4. **FG 存在性 ≠ 正确性**：count>0 验不了率对（62× 率错 FG 照绿）。周期激励必须率在带判据（FG-B'）+ CCNT wall 时戳实测率（反推 span 误差可 6×）。
5. **软件重武装 ≠ 硬件周期**：过期 one-shot 上 re-Enable，周期由软件延迟决定非编程值。周期 ISR 用 continuous 硬件模式。
6. **聚合数先拆解再标签**：20.59 MCPS = 99.8% ISR + 0.2% DMA，标「DMA 争用」=口径错。relabel 强制随行。
7. **64 vs 120 双口径**：64=I/O 帧（数据流/块率分母）；120=树内 sz[] 之和（MMAC 用）。buffer 重算 8×64×4B×2=4096B 不套例程（COUNT=300 不同源）。
8. **harness build ≠ 产品 build**：harness-only 产物（proxy 缓冲）不进产品 .map——放置决策只认产品 build .map。
