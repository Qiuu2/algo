# bench_cyc_target() — ADSP-21569 CCLK 周期计数：文档出处 + 实现 + 验证

**文档 ID**：DOC-S4-CCNT-01 ｜ 日期：2026-06-03 ｜ 挂接：R1 / DEC-S4-DSP-01
**背景**：S2 板上 bit-exact 已 PASS（crc=0x90556BC7，[L1/EZKIT]）；填 `bench_cyc_target()` 读真周期 → S3 cycle → R1。

---

## 1. 源头确认（文档出处，非凭印象）

**底层寄存器 — REGF_EMUCLK（32-bit 核周期计数器，用户空间可读）**
> 出处：`bsp/sw_reference/SHARC+ Core Programming Reference` §29（pdftotext line 14929-14935 / 29379-29383）：
> "The emulation clock counter consists of a **32-bit count register (REGF_EMUCLK)** and a 32-bit scaling register (REGF_EMUCLK2). The REGF_EMUCLK **counts core clock cycles** while the user has control of the processor and stops counting when the emulator gains control. … **Reads of REGF_EMUCLK … can be performed in user space.** This allows simple benchmarking of code." REGF_EMUCLK2 在 EMUCLK 回绕时自增 → 合成 **64-bit**，"can count accurately for thousands of hours"。

**C 层 API（ADI 自己的 21569 例程，最具体出处）— 标准 `clock()`**
> 出处：`bsp/app_notes/fira_accel_code/EE408V02/ADSP_2156x_FIRA_Performance/src/FIR_Throughput_21569.c`：
> `:4` 注释 "measure the number of **CCLK cycles** … **on ADSP-21569**"；`:18-20` `volatile clock_t clock_start,clock_stop,cycles;`；`:42` `clock_start=clock();`；`:86` `clock_stop=clock();`；`:87` `cycles=clock_stop-clock_start;`；`:89` `printf("… CCLK cycles = %d", …, cycles)`。
> `Pipelined/` 与 `*_Driver_Benchmark/` 例程一致用 `clock_start/stop=clock()`（START/STOP_CYCLE_COUNT 宏）。

**裁定**：
- **用 `clock()`（`<time.h>`），返回 `clock_t` = CCLK 周期**——这是 ADI 官方 21569 例程的口径，非猜测。
- 位宽：`clock_t` **32-bit**（例程以 `%d` 打印）；底层即 REGF_EMUCLK 32-bit。
- ❌ 不用 `__builtin_emuclk()`（候选之一，但 ADI 例程未用、本可用文档未确认其名 → 避免凭印象）。clock() 是文档坐实路径。

---

## 2. 实现（`bench_main.c`）
```c
#include <time.h>
uint32_t bench_cyc_target(void) { return (uint32_t)clock(); }   /* CCLK 周期，同 ADI 21569 例程 */
```
**回绕处理**：32-bit @1GHz 约 **4.29s** 回绕。per-frame 测量（1.333ms ≈ 1.3M cycles）远不回绕；`bench_harness` 用**无符号差** `end-start`，单次回绕自动正确。长累计测量才需 EMUCLK2（64-bit 合成）或逐帧累加——本 harness 逐帧小区间，无需。

---

## 3. 验证方法（task 3）
**已加 CCNT 自检（`bench_main.c`，bench_run 前）**：已知 1,000,000 次 `volatile` 空循环，`g_ccnt_selftest = clock()差`。
- **判据**：emulator 查 `g_ccnt_selftest` 应 **>0** 且 **≈ 1e6 × 每迭代周期**（空 volatile 循环每迭代约 2-6 cycle → 数 **M cycles** 量级）。=0 → clock() 没读到真周期；乱跳/极小 → 排查。
- **线性性**：再测 10× 循环 → `g_ccnt_selftest` 应 ≈10× → 证明线性计数。
- **量级合理性（cyc_8ch_frame）**：8ch×4 子带×63-tap/64 样本帧 → 预期**几万 cycle**（1.333ms@1GHz 预算=1.333M，桌面外推 17-33× 裕量 → ~40K-80K）。落此区间=合理；0/百万级=异常。
- **二值判据（本任务）**：板上 `cyc_8ch_frame > 0` 且数值合理（非 0、非乱跳）。
- **自由运行纪律（F7 FIRA 实测教训 2026-06-04）**：FIRA cycle 测量循环（含 spin-on-ALL_CHANNEL_DONE + 自由运行 CCNT）**严禁在测量循环内设断点**——SLOWLOOP+断点会死锁计数循环、污染 cycle 数。只在 run 跑完后的 idle `while(1)`（bench_main.c:233）读 `g_*` 全局。本次 F7 FIRA 板跑遵此 -> 干净 [L1]。

---

## 4. S3 → R1 路径
`cyc_8ch_frame`（真 CCLK）→ `MCPS = cyc×Fs/FRAME/1e6`（Fs=48k/FRAME=64，即 ×750/1e6）；实测 CCLK 不假设 1GHz。
**R1 闭合 ⇔ 16ch WCET<1.333ms 且 裕量×=预算/实测MCPS≥10× 且 满 PF-1**。标 [L1/EZKIT] 纯核。

---

*DOC-S4-CCNT-01，PM 直跑 2026-06-03。clock()=CCLK 周期（ADI 21569 例程 FIR_Throughput:4/18-20/42/86-89 坐实）；底层 REGF_EMUCLK 32-bit 用户可读（Core Programming Ref §29）。回绕：per-frame 安全。自检：已知 1M 循环对照。*
