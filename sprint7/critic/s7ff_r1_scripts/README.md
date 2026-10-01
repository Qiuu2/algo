# critic s7ff R1 的复核脚本与日志（2026-10-02）

- **来源**：独立 critic 子代理在会话 scratchpad 里写的复核脚本与日志，原样存档。
- **跑的是哪版文件**：都是修正**前**那一版（0 dB 档 RMS −20 dB）。
  - 修正后文件已重新生成，0 dB 档 RMS 改为 −23 dB，所以日志里的电平类数字只代表 R1 当时的状态。
  - 新文件的数字以 `sprint7/signals/s7ff_v1/` 下的日志与 CSV 为准。
- **脚本里的绝对路径**：照原样保留。

| 文件 | 内容 |
|---|---|
| `indep_recompute.py` / `.log` | critic 不导入包内任何模块，自己解析 RIFF、自己解 24-bit 样点、自己算指标，抽查 10 个文件，并与 `S7FF_V1_METRICS.csv` 比对 |
| `critic_falsifiers.py` / `.log` | critic 自造坏文件，结果发现：渐变不平滑、咔哒、断续这几类坏文件能通过 R1 版检查器（即 R1 的 M1） |
| `click_detector_probe.py` / `.log` | 探针，验证"去掉带内 ±1/3 倍频程后看残差"能否检出上述坏文件（即 PM 加的 C 门） |
| `leq_compare.log` | 本包的多正弦信号与高斯带噪在 Leq 窗口起伏上的对比 |
| `gate_run_stdout.log` | critic 在 scratch 副本上跑 R1 版一键门的输出 |
