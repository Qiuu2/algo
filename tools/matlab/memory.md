---
name: "MATLABAgent"
description: "MATLAB计算引擎Agent的常用脚本库、性能数据与数值问题记录"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# MATLAB Agent — Memory

## 1. 常用脚本库

### 频率响应分析脚本

```matlab
% script: frequency_response_analysis.m
% Purpose: Compute and plot frequency response of audio system

function [H, f, figHandles] = frequency_response_analysis(ir, fs, smoothing)
    % Parameters
    NFFT = 2^nextpow2(length(ir)*4);
    f = (0:NFFT-1)*fs/NFFT;
    
    % Compute FFT
    H_raw = fft(ir, NFFT);
    H_mag = 20*log10(abs(H_raw));
    
    % Apply smoothing (1/6 octave default)
    if nargin < 3, smoothing = 6; end
    H_smooth = smooth_spectrum(H_mag(1:NFFT/2), f(1:NFFT/2), smoothing);
    
    % Find peaks and bandwidth
    [peaks, locs] = findpeaks(H_smooth, f(1:NFFT/2), ...
        'MinPeakHeight', -10, 'MinPeakDistance', 500);
    
    % Generate plots
    figHandles(1) = figure('Name', 'Magnitude Response');
    semilogx(f(1:NFFT/2), H_smooth, 'LineWidth', 1.5);
    hold on;
    plot(locs, peaks, 'ro', 'MarkerSize', 10);
    xlabel('Frequency (Hz)'); ylabel('Magnitude (dB)');
    title(sprintf('Frequency Response (%d Octave Smooth)', smoothing));
    grid on; xlim([20 fs/2]); ylim([-60 10]);
    legend('Response', 'Peaks');
    
    % Output
    H = H_smooth;
    f = f(1:NFFT/2);
end
```

### THD+N分析脚本

```matlab
% script: thd_analysis.m
% Purpose: Total Harmonic Distortion plus Noise measurement

function [thd_pct, thd_db, harmonics] = thd_analysis(signal, fs, f0)
    % Use MATLAB built-in thd function
    [thd_db, ~, harmpow, harmfreq] = thd(signal, fs, 10);
    thd_pct = 100 * 10^(thd_db/20);
    
    % Extract harmonic data
    harmonics = struct('frequency', harmfreq, 'power_dB', harmpow);
    
    % Generate THD report figure
    figure('Name', 'THD Analysis');
    subplot(2,1,1);
    thd(signal, fs, 10);
    title(sprintf('THD = %.3f%% (%.1f dB)', thd_pct, thd_db));
    
    subplot(2,1,2);
    bar(harmfreq/1000, harmpow);
    xlabel('Harmonic Frequency (kHz)');
    ylabel('Power (dB)');
    title('Harmonic Distortion Components');
end
```

### 阻抗曲线测量脚本

```matlab
% script: impedance_analysis.m
% Purpose: Measure loudspeaker impedance curve

function [Z, f, Re, Fs, Qts] = impedance_analysis(V, I, fs)
    % Compute impedance
    Z_mag = abs(V ./ I);
    Z_phase = angle(V ./ I) * 180/pi;
    
    % Frequency vector
    N = length(Z_mag);
    f = (0:N-1)*fs/N;
    
    % Find resonance parameters
    [Z_max, idx_max] = max(Z_mag);
    Fs = f(idx_max);
    Re = min(Z_mag(1:round(N/4)));  % DC resistance
    
    % Estimate Qts from 3dB bandwidth
    Z_3dB = Z_max / sqrt(2);
    idx_low = find(Z_mag(1:idx_max) >= Z_3dB, 1, 'first');
    idx_high = find(Z_mag(idx_max:end) <= Z_3dB, 1, 'first') + idx_max - 1;
    BW = f(idx_high) - f(idx_low);
    Qts = Fs / BW;
    
    % Plot
    figure;
    yyaxis left; semilogx(f, Z_mag); ylabel('|Z| (Ohm)');
    yyaxis right; semilogx(f, Z_phase); ylabel('Phase (deg)');
    xlabel('Frequency (Hz)'); title('Impedance Curve');
    xlim([10 fs/2]); grid on;
end
```

## 2. 计算性能数据

### 常见运算耗时

| 运算 | 数据规模 | 平均耗时 | 内存 | 工具箱 |
|------|----------|----------|------|--------|
| FFT (1M点) | 1M samples | 22ms | 95MB | Signal Processing |
| Welch PSD | 10M samples, 4096窗口 | 180ms | 320MB | Signal Processing |
| Spectrogram | 1min@48kHz | 250ms | 400MB | Signal Processing |
| FIR设计 ( Parks-McClellan, 1000阶 ) | 1000 taps | 45ms | 45MB | DSP System |
| IIR设计 ( Butterworth, 8阶 ) | 8th order | 12ms | 30MB | Signal Processing |
| fmincon优化 | 10 vars, 100 iter | 800ms | 60MB | Optimization |
| 相关分析 (xcorr) | 1M samples | 35ms | 120MB | Signal Processing |
| THD计算 | 65536 samples | 28ms | 40MB | Signal Processing |

### 大矩阵处理建议

| 矩阵规模 | 内存需求 | 处理策略 |
|----------|----------|----------|
| < 1M elements | < 8MB | 直接处理 |
| 1M - 10M | 8 - 80MB | 直接处理 |
| 10M - 100M | 80 - 800MB | 预分配内存 |
| 100M - 1B | 800MB - 8GB | 分块处理 |
| > 1B | > 8GB | 流式处理+单精度 |

## 3. 数值问题记录

### 已知数值问题

| 问题ID | 描述 | 影响 | 解决方案 | 状态 |
|--------|------|------|----------|------|
| NUM-001 | FFT 1M+点精度下降 | 频谱泄漏 | 加窗处理 | Resolved |
| NUM-002 | IIR滤波器高阶不稳定 | 数值溢出 | 拆分为SOS | Resolved |
| NUM-003 | fmincon局部最优 | 参数估计偏差 | 多起点优化 | Mitigated |
| NUM-004 | 除零在THD计算 | Inf结果 | 添加保护值 | Resolved |
| NUM-005 | 大矩阵求秩误差 | 错误自由度 | 使用SVD阈值 | Resolved |

### 精度建议

| 计算类型 | 建议精度 | 原因 |
|----------|----------|------|
| 频谱分析 | double | 动态范围需要 |
| 滤波器系数 | double | 级联稳定性 |
| 矩阵求逆 | double | 条件数敏感 |
| 大规模数据 | single | 内存优化 |
| 蒙特卡洛 | single | 速度优先 |

## 4. 优化记录

### 2024-01-08: FFT缓存优化
- **问题**: 重复计算相同长度FFT
- **方案**: FFT计划缓存
- **效果**: 重复FFT减少60%耗时

### 2024-01-11: 向量化重构
- **问题**: 循环导致MATLAB脚本慢
- **方案**: 全面向量化+预分配
- **效果**: 平均加速15x

### 2024-01-14: 内存映射大文件
- **问题**: 大WAV文件加载内存不足
- **方案**: memmapfile内存映射
- **效果**: 10GB文件处理仅需200MB内存
