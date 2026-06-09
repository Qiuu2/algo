---
name: "MATLABAgent"
description: "MATLAB计算引擎Agent，提供信号处理、数值计算、仿真与可视化能力"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# MATLAB Agent — Profile

## 身份定义

- **Agent ID**: `matlab-agent`
- **类型**: 工具层Agent
- **身份**: MATLAB计算引擎Agent
- **所属系统**: ITC企业级多Agent协作系统

## 功能范围

| 功能域 | 说明 | 优先级 |
|--------|------|--------|
| 信号处理 | FFT、频谱分析、时频分析、滤波 | P0 |
| 数值计算 | 矩阵运算、插值、积分、微分方程 | P0 |
| 滤波器设计 | FIR/IIR设计、参数优化 | P0 |
| 系统辨识 | 传递函数估计、状态空间模型 | P1 |
| 优化计算 | 参数优化、约束优化 | P1 |
| 可视化 | 2D/3D绘图、频谱图、瀑布图 | P0 |
| 仿真验证 | 算法原型验证、蒙特卡洛仿真 | P1 |

## 调用接口

### 入口方法 (JSON-RPC)

```json
{
  "jsonrpc": "2.0",
  "method": "matlab.run",
  "params": {
    "script": "<base64_encoded_mfile>",
    "workspace": {
      "fs": 48000,
      "signal_data": "/input/signal.mat"
    },
    "outputs": ["H", "f", "fig1"],
    "timeout": 60
  },
  "id": 1
}
```

### 返回值格式

```json
{
  "jsonrpc": "2.0",
  "result": {
    "execution_id": "ml-20240115-001",
    "workspace": {
      "H": "/output/ml_H.mat",
      "f": "/output/ml_f.mat"
    },
    "figures": [
      "/output/fig1_magnitude.png",
      "/output/fig1_phase.png"
    ],
    "console": "Frequency response computed.\nPeak at 1.2kHz: 3.2dB",
    "execution_time_ms": 4520
  },
  "id": 1
}
```

## 支持的MATLAB工具箱

| 工具箱 | 版本 | 主要函数 | 状态 |
|--------|------|----------|------|
| Signal Processing | R2023b | fft, filter, spectrogram | Licensed |
| DSP System | R2023b | dsp.FIRFilter, dsp.IIRFilter | Licensed |
| Optimization | R2023b | fmincon, lsqnonlin | Licensed |
| Statistics | R2023b | mean, std, corr, regress | Licensed |
| Curve Fitting | R2023b | fit, smooth | Licensed |

## 依赖服务

| 服务 | 用途 | 健康检查 |
|------|------|----------|
| MATLAB Runtime | MATLAB引擎执行 | `/health/matlab` |
| License Server | 浮动许可证管理 | `/health/license` |
| Figure Renderer | 图形渲染服务 | `/health/renderer` |
