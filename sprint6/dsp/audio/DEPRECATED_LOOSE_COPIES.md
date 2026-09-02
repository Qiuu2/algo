# 已过期副本标注（2026-09-02 housekeeping，只加注不删除）

| 路径 | 性质 | 权威替代 |
|---|---|---|
| `sprint6/dsp/audio/m1_loopback_tdm.c` | 2026-06-12 松散快照，816 行；权威版 897 行（+81 行：`M2_CHMAP_FIX` / `M2_STATIC_TXTEST` / `M2_STXT_LOCALIZE`，2026-07-07） | `m1_cces_project/src/m1_loopback_tdm.c` |
| `sprint6/dsp/audio/m1_loopback_tdm.h` | 同上，76 行 vs 权威 89 行 | `m1_cces_project/src/m1_loopback_tdm.h` |
| `sprint6/dsp/audio/m1_project/`（整个目录） | 2026-06-08 route-B 骨架：无 `.cproject/.project`；`src/m1_main.c` 78 行 vs 权威 95 行；`src/m1_cyc.c` / `m1_sru.c` / `m1_softconfig.c` 与权威逐字节相同（重复文件）；`system/startup_ldf/m1_app.ldf` 与权威逐字节相同 | `m1_cces_project/` |

**规则**：导入 CCES、构建、guard-check、阅读源码、写文档引用，一律以 `m1_cces_project/` 为准。两个 `run_guard_check.sh` 的默认检查对象已于 2026-09-02 改指权威工程；旧副本仅可通过显式传参检查（历史对照用）。

**为什么不删**：CTO 2026-09-02 裁定"只加标注不删除"；且 `m1_project/src/m1_softconfig.c` 受 CTO-gate hook 保护（任何 commit 暂存该路径须 `CTO_OK=1`），本次不触碰它，靠本文件与 `m1_project/DEPRECATED.md` 目录级覆盖。

**行数口径**：表中 816/76 为加注前（HEAD）行数；加 7 行注释块后为 823/83，正文字节不变（critic 09-02 `cmp` 复核）。

**残留引用（存史，不改）**：`sprint6/dsp/audio/M2_SURVEY.md:16-18` 仍把松散 `m1_loopback_tdm.{c,h}` 与 `m1_project/…/m1_app.ldf` 当接入点——那是 06-08 的历史勘察文档，路径已过期，一律以 `m1_cces_project/` 为准。

**发现来源**：2026-09-02 只读代码审计（`diff` 证明 CCES 版是松散版的严格超集，0 行删除）。
