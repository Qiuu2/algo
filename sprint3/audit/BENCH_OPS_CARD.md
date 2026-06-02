# 台架 CCES 操作卡（cross-build + bringup + baseline 合并）— 一页流程

**文档 ID**：DOC-BENCH-CARD-01 ｜ 日期：2026-06-02 ｜ PM 整合
**用途**：台架当天照此一页走完 core-only 上板到 R1 闭合 + FIRA baseline。细节见各源文档（每段标注）。
**板**：AD-EXKIT V2.1 / SOM REV 1.1 / 芯片 ADSP-21569KBCZ10（CTO 已肉眼坐实）。

> 🔴 **三条贯穿红线**：① 版本确认前禁上电/接 ICE（C10）；② 禁热插拔 JTAG（烧板）；③ R1 数=纯核 [L1/EZKIT]，host[L2]/桌面[L2]/FIRA 收益**均不混入**（R14/铁律八维持）。

---

## Phase 0 — 传输 + verbatim 核对（Windows）
1. 传 `sprint4/dsp/core_only_to_windows.tgz`（20KB，源文件）到 Windows，解包。
2. **md5 核对**：对 `MANIFEST.md5` 逐行验；**★ `src/tree_filterbank.c`(`1e884793…e840a`) + `.h`(`7397ff0e…2912`) 必须逐字节一致**（= host 验过的核，改一字节即作废）。

## Phase 1 — 真 SHARC cross-build（Windows CCES，不接板）
*源：`sprint4/dsp/core_only/CROSS_BUILD_NOTES.md`（DOC-S4-CROSS-01）*
3. CCES 新建 ADSP-21569 工程，加入 `tree_filterbank.c/.h` + `tfb_8ch.c/.h` + `fir_coeffs_hb63.h` + `dsp_main_core_only.c`（**🚫 不挂 float 骨架 / 🚫 不接 437-tap `sprint2/dsp/fir_coeffs.h`**）。
4. `.ldf` 按预案放置：热点 `state[63]×9×8ch`→L1；系数→L1/L2；大局部数组（`tree_filterbank.c:144` r1[512]/r2/r3）改静态+section 或确认 L1 STACK 够。
5. 编译 `-proc ADSP-21569 -O1`。预期通用 C 层 0 警告（gcc 代理已佐证 0/0）；若报 int8/16_t → 查 `stdint.h`，极端缺失把 `uint8_t`(`tree_filterbank.h:108`+`tfb_8ch.h` 标志)→`uint32_t`。
6. **目标：0 错 0 警告 [L1/CCES-target]**（区别于桌面 gcc 代理 [L2]）。
7. **反汇编抽查 int64 MAC 映射**（唯一 target 风险，只影响 cycle 不影响 bit-exact）：`(int64_t)h*state` 是否落 MR 硬件累加器（非 `__mulli3` 库）；`>>` 是否 ASHIFT。**记入 S3/S4**。

## Phase 2 — Bringup 上电（接板，按版本 V2.1）
*源：`sprint3/audit/ezkit_bringup_checklist.md`（DOC-BENCH-CARD 顺序简版，专属接线以 V2.1 回填位为准）*
8. **供电**：5V2A/MINI USB；JP1 按供电方式（0=核心板独立/1=底板）；V2.1 电源开关默认 OFF→拨 ON。**先目视无短接、确认电压再上电**。
9. **Boot**：BMODE0/1/2 **全拨 0**（No boot，防 flash boot 抢 JTAG）。
10. **接仿真器硬规矩**：**先插 JTAG（断电）→ 板上电 → AD-HP530ICE 接 USB**；**🚫 禁热插拔**。
11. **上电 LED 判据**：核心板 LED5 亮 + 仿真器 Power 亮（正确链接）；异常按 checklist §5 分流。
12. **CCES Session**：SHARC→ADSP-21569→Emulator→`ADSP-21569 via ICE-1000`；**ICE Test 5 步**全过（1-3 步=软件/4-5 步=链路）。结束先 disconnect 再拔（断电后）。

## Phase 3 — core-only R1 闭合（接仿真器后）
*源：`sprint4/dsp/core_only/S0S1_report.md` §5 R1 判据*
13. **S2 板上 bit-exact**：片内喂 `tree_io_*.csv` 的 x 序列，单通道逐帧 `tfb_analyze→tfb_synthesize`，**整数 Q31 域逐位对 golden y[]**；**sat（默认）对 `tree_io_sat.csv` + unsat（`-DTFB_DISABLE_SAT`）对 `tree_io_unsat.csv`，两套全过、容差 0**。golden 权威=host 重跑导出整数 y[]（csv 仅参考）。**仅编译运行≠达标**。
13b. **S3 前·反汇编饱和钳位（GAP-SAT 处置，决定 WCET 口径）**：S3 cycle 前先反汇编 `sat_i64_to_i32`/`sat_add_i32`（`tree_filterbank.c:43-60`）的钳位实现，二分叉：
    - **无分支**（min/max/条件传送/饱和指令 → cycle 与是否饱和无关）→ **GAP-SAT 不影响 R1 关闭**；R1 数标「**WCET@非饱和激励 + 钳位无分支确认**」即可（0.289 非饱和路径 cycle = 真 WCET）。
    - **是分支**（数据相关分支 → 饱和路 cycle 可能更高）→ **必须补 8ch 满载激励（~8× 过载触饱和）量真 WCET 再标 [L1]**；**不可用非饱和 WCET 充 worst-case**（PF-4 教训：worst-case 须对抗激励，DC/非饱和会漏最坏路径）。
14. **S3 cycle**：`g_tfb_cyc_reg`(`tree_filterbank.h:80-82`) 换 `def21569.h` 的 CCNT/EMUCLK；空测扣偏置；setup 与稳态分开。
15. **S4-S5 MCPS + R1 判据**：满负载 8ch/16ch 实测 cycles/帧 → `MCPS=cycles×Fs/FRAME/1e6`（Fs=48k/FRAME=64/帧周期1.333ms）；**实测 CCLK 不假设 1GHz**；标 **[L1/EZKIT] 纯核**，并按 13b 结果标 WCET 口径（「@非饱和+钳位无分支确认」或「@8ch 满载饱和激励」）。
    **★ R1 闭合 ⇔ (a) 16ch WCET < 1.333ms 且 (b) 裕量×=预算/实测MCPS ≥ 10× 且 (c) 满 PF-1 七判据。** 桌面 17×/33×[L2] 仅外推参照、非闭合依据。**GAP-SAT（饱和路 bit-exact 未测）= 正确性覆盖缺口，挂 R14，暂不阻塞 R1**（登记见 decisions_log R14 块）。

## Phase 4（并行/独立）— ADI FIRA baseline
*源：`sprint3/audit/ezkit_fira_baseline.md`（DOC-…BASELINE-001）*
16. 跑 ADI 官方 `FIR_Multi_Channel_Processing`（64-tap/4096-tap 两档，4ch，**浮点**），插桩 `adi_fir_QueueTask`→`FIRTaskDoneCount`，扣偏置，≥3×100 次 → cycle/sample/tap [L1/EZKIT] vs ADI 标称 0.25。
17. **🚩 红线**：baseline = **ADI 例程，非我方算法，baseline≠R1 闭合**；**FIRA 收益不进选型**（R14/C9，未关 R14 违者 BLOCKER）。

---

## 待回填（台架产出后）
- Phase 1：真 SHARC 0/0 结果 + int64 MAC 反汇编结论。
- Phase 3：**13b 饱和钳位反汇编结论（无分支/是分支）+ 据此 WCET 口径** + S2 双套 bit-exact PASS/FAIL（diff 数）+ S4-S5 实测 CCLK/MCPS/裕量× + R1 判定 + GAP-SAT 处置回填。
- Phase 4：FIRA cycle/sample/tap + vs 0.25 + PF-1 七判据。

**挂接**：R1 / R14 / DEC-S2-002 / DEC-S3-PROC-01 / DEC-S4-DSP-01 / DOC-S4-CORE-PLAN-01 / DOC-S4-CORE-S0S1-01 / DOC-S4-CROSS-01 / DOC-S4-DSP-INV-01。

---

*DOC-BENCH-CARD-01，PM 整合 2026-06-02。三源文档（cross-build/bringup/baseline）合并为一页台架流程；红线（C10 上电闸门/禁热插拔/R14 FIRA 不进选型/host[L2]≠板[L1]）贯穿。细节见各源文档。*
