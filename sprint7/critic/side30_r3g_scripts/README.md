# critic R3G 复核脚本（侧面 30 dB hybrid 包，2026-09-29）

- 独立 critic 子代理在会话 scratch 里写的复核脚本及其输出，原样存档，供追溯。未经 PM 修改。
- 各文件作用：
  - `r3g_bank_headroom.py`（附 `.log`）：自写 DTFT / 卷积复核分频组性质与瞬态余量；
  - `r3g_kkt_mc.py`（附 `.log`）：自写零空间 KKT 与配对 MC（6000 阵列）；
  - `r3g_mc_path.py`：核对复数与实数两条 MC 路径；
  - `r3g_taper_eff.py`：锥度项（每瓦轴向声压）；
  - `run_mut.py`：对 PM 脚本副本做变异测试（delta 轮 F4）。
- 脚本里多是会话 scratch 与本机的**绝对路径**，不能原样复跑；要复跑须改成本仓库的相对路径（同 side30_r1_scripts 的做法）。
- 刻意没有存档：MATLAB 镜像目录、变异后的 PM 脚本副本及其输出（可由 `run_mut.py` 重新生成）。
- 审查结论以 `../CRITIC_O_SIDE30_R3G_20260929.md` 为准。
