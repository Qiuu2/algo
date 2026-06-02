# Core-only 嫁接计划（算法 → 已验证 ADI 脚手架）+ 内存向量 harness

**文档 ID**：DOC-S4-GRAFT-01 ｜ 日期：2026-06-02 ｜ PM 直跑（agent socket 死后收尾）
**方法（CTO 修正）**：21569 纯算法需芯片 init → **不新建空工程、不手写 init**，借已验证 EZKIT 例程 board-level 当底座，把我方算法嫁接进处理槽。
**git**：S0-S1 已 commit `4bf0f52`（核 verbatim md5 `1e884793`/`7397ff0e`）；本 bench/ 为后续增量。

---

## 1. 底座选定：`ADSP21569_LED`（PM 决定）
路径 `knowledge_base/ezkit/vendor_docs/cces_examples/code/ADSP21569_LED/`。
**选它的理由**：`main.c` 的 `adi_initComponents()` = 全板 init（时钟/电源/pinmux/sru）；`system/startup_ldf/`（app.ldf / app_startup.s / app_IVT.s / app_heaptab.c）= 已在本板验证的 boot；**零 codec/FIRA/DMA/A2B，只 GPIO**（最干净）。淘汰：Audio_* 带 ADAU codec+SPORT；UART 带外设+.backup；FIR_Multi_Channel 带 FIRA（core-only 不要）。

## 2. 嫁接边界（ADI 底座 vs 我方算法，红线：不混）
| 层 | 来源 | 处置 |
|----|------|------|
| boot / init | **ADI LED** `system/startup_ldf` + `adi_initialize`（`adi_initComponents`）| **保留不改** |
| GPIO LED | ADI LED | 保留（pass/fail 可视指示） |
| **main 处理槽** | **我方** | **`src/main.c` 的 `while(1)` LED 循环（行 58-75）→ 替换为 `bench_main.c`：init 后调 `bench_run()`** |
| 算法核 | **我方** verbatim `tree_filterbank.c/.h`（md5 守）| 加入工程，🚫逐字节不动 |
| 8ch / 系数 | **我方** `tfb_8ch.c/.h` + `fir_coeffs_hb63.h`（hb63）| 🚫禁 float 层 / 🚫禁例程系数·437-tap |

## 3. 内存向量 harness（S2-S5，不接 codec/A2B/DMA）
`bench_harness.c/.h` + 独立 golden `golden_ref.h`（host 冻结）：
- **输入内存生成**：chirp（同 tree_verify/gen_golden，确定性，0.289=-6dBFS+headroom），无文件 I/O。
- **S2 bit-exact**：单通道链输出 → **CRC32(全65536) + 64 spot 逐位 vs golden_ref.h**，容差 0；sat+unsat 双套。
  - ⚠️ **诚实标注**：0.289 单通道**不触发饱和** → **SAT≡UNSAT**（CRC 均 `0x90556BC7`，gen_golden 两 build 实测一致）；故双套比同一 golden=两 build 都复现核路径 bit-exact。饱和原语 bit-exact 不被此输入覆盖（**GAP-SAT 已正式登记**：decisions_log「关联覆盖缺口 GAP-SAT」，挂 R14、暂不阻塞 R1；台架处置见 BENCH_OPS_CARD **13b** 反汇编饱和钳位：无分支→不影响 R1 算力 / 是分支→补满载 WCET）。
- **S3-S5 cycle**：CCNT（host=clock 占位 cyc_valid=0；**target 待回填真 CCNT**=1 [L1/EZKIT]）；量 analyze/synth/8ch 每帧 cycle；换算 `MCPS_8ch=cyc8×750/1e6`、`MCPS_16ch=(cyc8+8×analyze)×750/1e6`（Fs48k/FRAME64/帧周期1.333ms）。
- **R1 判据**（写死，实测待台架）：满负载 16ch WCET<1.333ms 且 裕量×=预算/实测MCPS≥10× 且 满 PF-1。

## 4. host 预验真实结果（[L2 host 预验]，PM 直跑）
- gcc 编译 `bench_harness.c`（-Wall -Wextra，含 M_PI fallback 防 cc21k 严格）：sat/unsat **0 错 0 警告**。
- 跑：**SAT bit-exact PASS**（CRC 0x90556BC7 match + spot match）/ **UNSAT bit-exact PASS**（同）。
- cycle：host clock 占位（cyc_valid=0，数值无意义，仅验 plumbing）。
- 含义：harness plumbing + golden 嵌入 + 比对逻辑 OK；**跨架构 bit-exact[L1/EZKIT] 待 target**（SHARC 输出 CRC vs 此冻结 golden）。

## 5. .ldf 热点增量（在 LED app.ldf 基底上，台架 CCES 配）
按 `CROSS_BUILD_NOTES.md §2.5`：`HbFirState.state[63]×9级×8ch` 延迟线 + 帧中间数组 → **L1**；`g_hb63_q15[63]` → L1/L2；`tree_filterbank.c:144` 大局部数组（r1[512]/r2/r3）→ 静态+section 或确认 L1 STACK 够。本轮只给增量说明，实际 .ldf 编辑在 Windows CCES。

## 6. 待台架回填（Windows CCES，本机无 SHARC 工具链）
- `bench_main.c` 嫁接进 LED 工程 → **真 SHARC `-proc ADSP-21569 -DTARGET_SHARC` 0 错 0 警告** [L1/CCES-target]。
- **`bench_cyc_target()` 回填真 CCNT**（`bench_main.c` TODO，def21569.h / __builtin_emuclk）。
- **int64 MAC 反汇编**确认落 80-bit MR（只影响 cycle）→ 记 S3/S4。
- 接仿真器 → S2 板上 bit-exact（CRC vs 0x90556BC7）→ S3 cycle → S4-S5 MCPS+R1 判定。

## 7. 文件清单（`sprint4/dsp/core_only/bench/`）
`GRAFT_PLAN.md`（本）/ `gen_golden.c`（golden 生成器）/ `golden_ref.h`（冻结 golden）/ `bench_harness.c/.h`（harness，host 验过）/ `bench_main.c`（target 嫁接）。

## 挂接
R1 / DEC-S4-DSP-01 / DOC-S4-CORE-PLAN-01 / DOC-S4-CORE-S0S1-01 / DOC-S4-CROSS-01 / BENCH_OPS_CARD（DOC-BENCH-CARD-01）。R14 闸门维持（无 FIRA）。

---

*DOC-S4-GRAFT-01，PM 直跑 2026-06-02。底座=ADSP21569_LED；harness host 预验 sat/unsat bit-exact PASS [L2]；真 SHARC 0/0 + 真 CCNT + 板上 bit-exact 待台架 [L1/EZKIT]。核 verbatim md5 守，无 FIRA，scaffold=ADI/algorithm=我方 不混。*
