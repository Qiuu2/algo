# critic 第 1 轮（侧面 30 dB）复核脚本（原样落库，2026-09-26）

独立 critic 子代理自写的代码，不 import 被审方脚本。它们引用的都是会话临时目录的绝对路径，仅作留痕。

- **未落库的生成物**：可执行文件 tfb_probe、tfb_paths，以及 25 MB 的 paths.bin。需要时用 gcc 按 tfb_probe.c / tfb_paths.c 重新编译，再对冻结的 sprint4/dsp/core_only/src/tree_filterbank.c 重跑即可。
- **报告**：../CRITIC_G_SIDE30_R1_20260926.md

**注意（critic R3a F9）**：这些脚本里硬编码了会话临时目录和仓库的绝对路径，**不能原样复跑**；要复跑，须先把路径改成本地路径。
