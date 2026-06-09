---
name: "CodeExecutionAgent"
description: "代码执行Agent的调用历史、性能数据与优化记录"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# Code Execution Agent — Memory

## 1. 执行历史记录

### 记录格式

```json
{
  "execution_id": "ce-20240115-001",
  "code_fingerprint": "a3f7e2b1c8d4e5f6",
  "language": "python",
  "caller_agent": "dsp-algorithm-agent",
  "timestamp_start": "2024-01-15T09:30:00Z",
  "timestamp_end": "2024-01-15T09:30:02Z",
  "execution_time_ms": 1523,
  "resource_usage": {
    "memory_peak_mb": 245,
    "memory_limit_mb": 512,
    "cpu_time_ms": 890,
    "cpu_limit_percent": 80
  },
  "exit_code": 0,
  "error_code": null,
  "tags": ["signal_processing", "batch_001"],
  "cache_hit": false,
  "output_size_kb": 12.3
}
```

### 历史查询索引

| 索引字段 | 类型 | 用途 |
|----------|------|------|
| `execution_id` | PK | 唯一执行标识 |
| `code_fingerprint` | HASH | 缓存命中检测 |
| `language` | TAG | 按语言筛选 |
| `caller_agent` | TAG | 按调用者筛选 |
| `timestamp_start` | ZSET | 时间范围查询 |
| `exit_code` | TAG | 成功率统计 |
| `tags` | SET | 标签分类查询 |

## 2. 常用代码片段库

### 信号处理模板

```python
# snippet: fft_analysis
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

def analyze_signal(signal, sample_rate):
    N = len(signal)
    yf = fft(signal)
    xf = fftfreq(N, 1/sample_rate)
    return xf[:N//2], 2.0/N * np.abs(yf[:N//2])
```

### 滤波器设计模板

```python
# snippet: filter_design
from scipy.signal import butter, filtfilt, freqz

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
```

### 频谱图生成模板

```python
# snippet: spectrogram
import librosa
import librosa.display
import matplotlib.pyplot as plt

def generate_spectrogram(audio_path, sr=48000, n_fft=2048, hop_length=512):
    y, _ = librosa.load(audio_path, sr=sr)
    D = librosa.amplitude_to_db(
        np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length)),
        ref=np.max
    )
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(D, sr=sr, hop_length=hop_length,
                            x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.tight_layout()
    return plt
```

## 3. 性能基准数据

### Python环境基准

| 测试项 | 平均耗时 | 内存峰值 | 备注 |
|--------|----------|----------|------|
| 空执行启动 | 350ms | 42MB | 容器冷启动 |
| warmed启动 | 120ms | 42MB | 容器预加载 |
| NumPy 1M数组FFT | 15ms | 85MB | 复数双精度 |
| Pandas 10万行处理 | 45ms | 156MB | CSV读+聚合 |
| Librosa频谱图 | 120ms | 210MB | 1分钟音频 |
| Matplotlib图表 | 200ms | 180MB | 含数据点10万 |

### MATLAB环境基准

| 测试项 | 平均耗时 | 内存峰值 | 备注 |
|--------|----------|----------|------|
| Engine启动 | 2800ms | 320MB | Runtime冷启动 |
| FFT 1M点 | 22ms | 95MB | 双精度复数 |
| 滤波器设计 | 35ms | 78MB | 8阶Butterworth |
| 频谱分析 | 150ms | 245MB | Welch方法 |

### 资源配额建议

| 任务类型 | 建议内存 | 建议CPU | 建议超时 |
|----------|----------|---------|----------|
| 轻量计算 | 256MB | 50% | 15s |
| 数据分析 | 512MB | 80% | 30s |
| 信号处理 | 1GB | 100% | 60s |
| 批量处理 | 2GB | 100% | 300s |
| 可视化 | 512MB | 80% | 30s |

## 4. 错误模式库

### 高频错误模式

| 错误模式 | 频率 | 根因 | 解决方案 |
|----------|------|------|----------|
| 内存溢出(E2002) | 23% | 大数据集未分块 | 添加分块处理模板 |
| 超时(E2001) | 18% | 算法复杂度高 | 添加进度检测+增量输出 |
| 依赖缺失(E1002) | 15% | 新库未审批 | 简化审批流程 |
| 序列化失败(E3002) | 8% | numpy数组未转换 | 自动类型转换中间件 |

### 错误趋势

```
Week 1: E2002 [UP]   - 批量信号处理任务增加
Week 2: E1002 [UP]   - 新增深度学习依赖请求
Week 3: E2001 [DOWN] - 优化超时预估算法
Week 4: (stable)     - 整体错误率 < 5%
```

## 5. 优化记录

### 2024-01-10: 容器预加载优化
- **问题**: 冷启动350ms影响交互体验
- **方案**: 保持2个 warmed 容器池
- **效果**: 平均启动时间降至120ms

### 2024-01-12: Librosa缓存优化
- **问题**: 重复音频文件多次加载
- **方案**: 输入文件层加LRU缓存
- **效果**: 频谱图任务减少30%执行时间

### 2024-01-14: 内存预估算法
- **问题**: E2002错误率偏高
- **方案**: 基于AST分析的内存预估
- **效果**: 预估准确率78%，超限任务前置拦截
