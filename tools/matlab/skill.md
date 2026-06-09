---
name: "MATLABAgent"
description: "MATLAB计算引擎Agent的具体功能、API规范与协作接口"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# MATLAB Agent — Skill

## 1. 支持的MATLAB工具箱

### 核心工具箱

| 工具箱 | 版本 | 用途 | 主要函数 |
|--------|------|------|----------|
| Signal Processing | R2023b | 信号分析与处理 | `fft`, `ifft`, `filter`, `freqz`, `spectrogram`, `pwelch`, `xcorr` |
| DSP System | R2023b | 数字信号处理系统 | `dsp.FIRFilter`, `dsp.IIRFilter`, `dsp.SpectrumAnalyzer`, `dsp.AudioFileReader` |
| Optimization | R2023b | 参数优化 | `fmincon`, `lsqnonlin`, `ga`, `patternsearch` |
| Statistics and ML | R2023b | 统计分析 | `mean`, `std`, `corr`, `regress`, `anova` |
| Curve Fitting | R2023b | 曲线拟合 | `fit`, `smooth`, `interp1`, `spline` |

### 工具箱依赖检查

```json
{
  "jsonrpc": "2.0",
  "method": "matlab.check_toolboxes",
  "params": {
    "required": ["Signal Processing", "DSP System"]
  }
}
```

## 2. 常用函数库

### 信号处理函数集

| 函数名 | 用途 | 输入 | 输出 |
|--------|------|------|------|
| `fft_analysis` | FFT频谱分析 | signal, fs | f, magnitude, phase |
| `psd_welch` | Welch功率谱密度 | signal, fs, window | f, psd |
| `spectrogram_stft` | 短时傅里叶变换 | signal, fs, nfft | t, f, Sxx |
| `design_butterworth` | Butterworth滤波器设计 | fc, fs, order, type | b, a, sos |
| `design_chebyshev` | Chebyshev滤波器设计 | fc, fs, order, ripple | b, a |
| `apply_filter` | 零相位滤波 | signal, b, a | filtered_signal |
| `group_delay` | 群延迟计算 | b, a, f, fs | gd |
| `thd_analysis` | 总谐波失真分析 | signal, fs, f0 | thd, harmonics |

### 频谱分析参数模板

```matlab
% Standard FFT parameters
NFFT = 2^nextpow2(length(signal));
f = (0:NFFT-1)*fs/NFFT;
Y = fft(signal, NFFT);
mag_dB = 20*log10(abs(Y/NFFT));

% Welch PSD parameters
window = hann(4096);
noverlap = 2048;
nfft = 8192;
[pxx, f] = pwelch(signal, window, noverlap, nfft, fs);
```

## 3. 执行接口规范（JSON-RPC）

### 主执行接口: `matlab.run`

**请求格式：**

```json
{
  "jsonrpc": "2.0",
  "method": "matlab.run",
  "params": {
    "script": "YmFzZTY0X2VuY29kZWRfbV9maWxlX2NvbnRlbnQ=",
    "script_name": "frequency_response_analysis.m",
    "workspace": {
      "fs": 48000,
      "signal_data": "/input/noisy_signal.mat",
      "filter_order": 8,
      "cutoff_freq": [200, 8000]
    },
    "outputs": ["H", "f", "filtered_signal", "thd_value"],
    "figure_options": {
      "format": "png",
      "dpi": 300,
      "width_px": 1200,
      "height_px": 600,
      "colormap": "parula"
    },
    "timeout": 60
  },
  "id": "ml-req-001"
}
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `script` | string(base64) | 是 | Base64编码的M文件内容 |
| `script_name` | string | 否 | 脚本名称（用于日志） |
| `workspace` | object | 否 | 输入变量/文件路径映射 |
| `outputs` | string[] | 否 | 需要返回的工作空间变量名 |
| `figure_options` | object | 否 | 图形输出选项 |
| `timeout` | int | 否 | 超时秒数，默认60，最大600 |

**成功响应：**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "execution_id": "ml-20240115-001",
    "workspace": {
      "H": {
        "type": "double_matrix",
        "shape": [4096, 1],
        "file_path": "/output/ml_H.mat",
        "summary": {
          "min": -45.2,
          "max": 3.1,
          "mean": -18.5
        }
      },
      "f": {
        "type": "double_vector",
        "shape": [4096],
        "file_path": "/output/ml_f.mat",
        "summary": {
          "min": 0,
          "max": 24000
        }
      },
      "thd_value": 0.0032
    },
    "figures": [
      {
        "figure_id": "fig1",
        "type": "magnitude_response",
        "file_path": "/output/fig1_magnitude.png",
        "resolution": "1200x600",
        "dpi": 300
      },
      {
        "figure_id": "fig2",
        "type": "phase_response",
        "file_path": "/output/fig2_phase.png",
        "resolution": "1200x600",
        "dpi": 300
      }
    ],
    "console_output": "Peak at 1.2kHz: 3.2dB\nTHD: 0.32%\nFilter order: 8",
    "execution_time_ms": 4520,
    "memory_peak_mb": 180,
    "toolboxes_used": ["Signal Processing", "DSP System"]
  },
  "id": "ml-req-001"
}
```

### 快速分析接口: `matlab.analyze_signal`

```json
{
  "jsonrpc": "2.0",
  "method": "matlab.analyze_signal",
  "params": {
    "signal_file": "/input/audio_sample.wav",
    "sample_rate": 48000,
    "analysis_type": "frequency_response",
    "output_format": "full"
  }
}
```

### 滤波器设计接口: `matlab.design_filter`

```json
{
  "jsonrpc": "2.0",
  "method": "matlab.design_filter",
  "params": {
    "filter_type": "butterworth_bandpass",
    "order": 8,
    "cutoff_frequencies_hz": [200, 8000],
    "sample_rate_hz": 48000,
    "output_format": "sos"
  }
}
```

## 4. 协作接口

### 与DSP算法Agent的协作

```json
{
  "interface": "matlab-to-dsp",
  "scenario": "algorithm_prototype_validation",
  "data_flow": {
    "input": {
      "algorithm_spec": "/shared/filter_spec.json",
      "test_signal": "/shared/test_signal.wav"
    },
    "processing": [
      "load_algorithm_parameters",
      "implement_in_matlab",
      "run_frequency_response",
      "run_time_domain_test",
      "compute_metrics"
    ],
    "output": {
      "frequency_response_plot": "/shared/fr_validation.png",
      "metrics_report": "/shared/dsp_metrics.json",
      "coefficients_validated": true,
      "pass": "PASS|FAIL|WARNING"
    }
  }
}
```

### 与声学仿真Agent的协作

```json
{
  "interface": "matlab-to-acoustic-postprocess",
  "scenario": "simulation_data_analysis",
  "data_flow": {
    "input": {
      "simulation_results": "/shared/com3_results.mat",
      "microphone_positions": "/shared/mic_positions.csv"
    },
    "processing": [
      "load_simulation_data",
      "compute_SPL_at_mics",
      "generate_directivity_pattern",
      "calculate_frequency_response"
    ],
    "output": {
      "spl_map": "/shared/spl_map.png",
      "directivity_data": "/shared/directivity.mat",
      "frequency_response": "/shared/fr_com3.png"
    }
  }
}
```

### 与测试Agent的协作

```json
{
  "interface": "matlab-to-test",
  "scenario": "test_data_processing",
  "data_flow": {
    "input": {
      "raw_measurement": "/shared/measurement_data.wav",
      "calibration_data": "/shared/calibration.csv",
      "test_config": "/shared/test_config.yaml"
    },
    "processing": [
      "load_and_calibrate",
      "compute_fr_and_distortion",
      "generate_test_report",
      "pass_fail_judgment"
    ],
    "output": {
      "processed_fr": "/shared/fr_processed.png",
      "distortion_analysis": "/shared/thd_analysis.png",
      "test_report_json": "/shared/test_report.json",
      "pass_fail": "PASS"
    }
  }
}
```

## 5. 图形输出规范

### 分辨率与格式

| 用途 | 分辨率 | 格式 | DPI |
|------|--------|------|-----|
| 文档嵌入 | 800x400 | PNG | 150 |
| 报告用图 | 1200x600 | PNG | 300 |
| 演示文稿 | 1920x1080 | PNG | 150 |
| 印刷用图 | 2400x1200 | PDF/SVG | 300 |
| 海报/展板 | 3600x1800 | PNG | 600 |

### 标注规范

```matlab
% Required annotation elements
figure('Position', [100 100 width height]);
plot(f/1000, mag_dB, 'LineWidth', 1.5);
xlabel('Frequency (kHz)', 'FontSize', 12);
ylabel('Magnitude (dB)', 'FontSize', 12);
title('Frequency Response - Speaker A300', 'FontSize', 14);
legend('Magnitude', 'Location', 'best');
grid on;
xlim([0 24]);  % fs/2 in kHz
ylim([-60 10]);
text(peak_f/1000, peak_mag, sprintf('Peak: %.1fdB@%.1fkHz', peak_mag, peak_f/1000));
```

### 颜色映射

| 图表类型 | 推荐colormap | 说明 |
|----------|-------------|------|
| 频谱图 | `parula` | 默认，色盲友好 |
| 瀑布图 | `jet` | 传统，对比强烈 |
| 极坐标图 | 自定义 | 蓝到红渐变 |
| 二维热力图 | `hot` | 温度/强度感 |

## 6. 错误码体系

| 错误码 | 类别 | 说明 |
|--------|------|------|
| `M1001` | 参数错误 | 输入类型不匹配 |
| `M1002` | 参数错误 | 矩阵维度不一致 |
| `M1003` | 参数错误 | 数值超出有效范围 |
| `M1004` | 参数错误 | 依赖文件不存在 |
| `M2001` | 计算错误 | MATLAB许可证不可用 |
| `M2002` | 计算错误 | 数值溢出/下溢 |
| `M2003` | 计算错误 | 优化/迭代不收敛 |
| `M2004` | 计算错误 | 内存不足 |
| `M3001` | 图形错误 | 图形渲染失败 |
| `M3002` | 图形错误 | 输出文件过大 |
| `M9001` | 系统错误 | MATLAB引擎未启动 |
| `M9002` | 系统错误 | 内部服务错误 |
