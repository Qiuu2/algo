# DEPRECATED（2026-09-02 标注，只加注不删除）

本目录 `m1_project/` 已被 `../m1_cces_project/` 取代（唯一权威、板上 PASS 的 CCES 工程）。

- `src/m1_main.c`：78 行旧版（权威 95 行，多 `m2_static_txtest_fill()` 与 idle 循环三分支）。
- `src/m1_cyc.c` / `src/m1_sru.c` / `src/m1_softconfig.c`：与权威逐字节相同的重复文件；`m1_softconfig.c` 受 CTO-gate hook 保护，本次未加文件内标注。
- `system/startup_ldf/m1_app.ldf`：与权威逐字节相同的重复文件。
- `run_guard_check.sh`：已于 2026-09-02 改为检查 `../m1_cces_project/src/` 的 5 个 TU，本目录 `src/` 不再被检查。

一切以 `../m1_cces_project/` 为准。详见 `../DEPRECATED_LOOSE_COPIES.md`。
