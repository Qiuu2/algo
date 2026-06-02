# Core-only 迁移 S0-S1 桌面首增量 — 执行报告

**文档 ID**：DOC-S4-CORE-S0S1-01
**日期**：2026-06-02 ｜ 实现：dsp-algorithm teammate（socket 死于报告前，**代码+编译已完成**）｜ **收尾验证：PM 直跑**（跑可执行 + md5 + 核三盯点）
**计划**：`sprint4/core_only_migration_plan.md`（DOC-S4-CORE-PLAN-01，critic 已核可开工）
**范围**：S0-S1 桌面首增量（不依赖台架）。板上 S2 / S4-S5 排队等台架，本轮不做。
**措辞红线**：本轮全部为 **[L2 host 预验]**（gcc/host 跑），**≠ 板上 [L1/EZKIT] bit-exact**（待 S2）。不混。

---

## 1. 文件清单（`sprint4/dsp/core_only/`）

| 文件 | 行/字节 | 说明 |
|------|--------|------|
| `src/tree_filterbank.c` | 209 行 | **算法核，verbatim 复制（md5 `1e884793…e840a` = 原件，逐字节一致，未改）** |
| `src/tree_filterbank.h` | 146 行 | 核头，verbatim（md5 `7397ff0e…2912` = 原件） |
| `include/fir_coeffs_hb63.h` | 32 行 | **冻结 63-tap 同源 Q15 半带原型**（`FIR_HB63_NTAPS=63`/`NNZ=33`；注释显式禁 437-tap） |
| `src/tfb_8ch.c` / `.h` | 64 / 43 行 | **8ch 包裹层**（8 份 `TreeChannelState`、分析×8、broadside 求和、合成×1；核签名零改动） |
| `host/gen_hb63.c` | 81 行 | 系数生成器（`make_halfband` 同源，产出 `fir_coeffs_hb63.h`） |
| `host/host_bitexact.c` | 212 行 | host bit-exact harness（[A]同源/[B]golden/[C]8ch逐位/[D]smoke） |
| `cces/dsp_main_core_only.c` | 43 行 | CCES/21569 入口骨架（S1 结构占位；显式禁 float 骨架 + 禁 437-tap） |
| `Makefile` | — | `make all` 出 sat/unsat 两套；`-O2 -Wall -lm` |

## 2. gcc 编译结果 — ✅ 两套均过

`make all`（`gcc -O2 -Wall -Iinclude -Isrc … -lm`，sat 默认 / unsat `-DTFB_DISABLE_SAT`）→ 生成 `host_bitexact_sat` + `host_bitexact_unsat`（各 21216 B），**0 错**。

## 3. host 双套 bit-exact 真实结果 — ✅ **SAT PASS / UNSAT PASS**（PM 直跑）

| 子项 | SAT | UNSAT |
|------|-----|-------|
| [A] 同源系数核对（盯点①）| **PASS** 冻结 63 值 == live make_halfband（63/63）；ntaps==63 断言 OK；中心抽头 16385 | **PASS**（同） |
| [B] golden = host 重跑参考链导出整数 y[]（盯点②）| **PASS** 1024 帧 → 整数 golden `y_ref[65536]`（Q31）；csv 仅参考 | **PASS**（同） |
| [C] 8ch 包裹 bit-exact（1 路有效+7 路零）| **PASS 逐位一致 diff=0 / 65536** | **PASS diff=0 / 65536** |
| [D] 8ch broadside smoke（8 路同信号）| PASS(smoke) 峰值 1.0FS / 钳位 21261 样本（~8× 触饱和，预期）| PASS(smoke) 峰值 1.0FS / 钳位 0（环绕，预期）|
| **总结** | **PASS（失败子项=0）** | **PASS（失败子项=0）** |

> 注：`tree_io_*.csv` 数据行 64336 < 整数 golden 65536（csv 经 guard 裁剪+延迟对齐）→ **csv 非权威，整数重跑为唯一权威**（盯点②落实）。

## 4. CTO 三盯点逐条落实

- **① 同源防 437-tap 误接** — ✅：冻结系数由 `host/gen_hb63.c` 的 `make_halfband`（同 `tree_verify.c:40-60`）生成；harness [A] 子项**逐值核对冻结 vs live + 断言 ntaps==63**，不一致即 FAIL；`fir_coeffs_hb63.h:10` + `cces/dsp_main_core_only.c` 头注释**显式禁 `sprint2/dsp/fir_coeffs.h`（437-tap 废核）**。两套 [A] 均 PASS。
- **② tolerance-0 golden = 重跑 host 导出整数 y[]** — ✅：harness [B] 由 host 现跑参考单通道链导出整数 `y_ref[]`（走 tree_verify 同一路径），逐位整数域比对；csv 明标"仅参考、非权威"。[C] diff=0 即据此整数 golden。
- **③ R1 闭合数值判据** — ✅ 判据式写死（见 §5；实测填实待板上 S4-S5）。

## 5. R1 闭合数值判据（盯点③，本轮写死式；板上 S4-S5 填实测）

```
MCPS_measured = cycles_per_frame × Fs / FRAME / 1e6        （/ MAC-per-cycle，若 SIMD）
  @ Fs = 48 kHz, FRAME = 64 samples → frames/s = 750, 帧周期 = 1.333 ms
预算 budget_MCPS = CCLK(MHz)        （ADSP-21569 标称 1GHz=1000 MCPS；CCLK 须板上实测，不假设）
占空比 = 处理时间 / 帧周期（1.333ms@64smp）；WCET = 占空比 × 帧周期
裕量× = budget_MCPS / MCPS_measured

★ R1 P0 闭合 ⇔ 同时满足：
   (a) 满负载 16ch WCET < 帧周期（1.333 ms）         —— 实时性硬约束
   (b) 裕量× ≥ 10×                                   —— 选型留 margin（参 dsp_8ch_report.md ≥10× 线）
   (c) 测量满 PF-1 七判据，标 [L1/EZKIT]，纯核（不含 FIRA、不含 TDM）
```
> 桌面外推参照（非闭合依据）：17×(16ch)/33×(8ch) **[L2 推断]**；R1 闭合以板上 [L1/EZKIT] 为权威。R14 闸门维持——FIRA 收益不进此判据（铁律八/C9）。

## 6. S1 板上 build 待 IDE 项（本轮只搭结构，未真跑 CCES）

- `.ldf` 内存布局：热点 `state[63]×9级×8ch` → L1；系数 → L2；大局部数组（`tree_filterbank.c:144` r1[512]/r2/r3）→ 指定 section。
- `system.svc` / startup / clock（CCLK=1GHz）配置。
- `def21569.h` 抽 **CCNT/EMUCLK** 寄存器名 → 填 `tree_filterbank.h:80-82` 的 `g_tfb_cyc_reg` 占位（S3 cycle 计数）。
- SPORT/DMA/codec → 端到端 S8（core-only 首测 S2 不依赖）。

## 7. 状态与挂接

- **达标判定**：本轮 = **桌面首增量完成**（编译过 + host 双套 bit-exact PASS + 三盯点落实 + 核 verbatim）。**注意**：host 预验 [L2] **≠ 板上 bit-exact [L1/EZKIT]**——计划二值判据的"跑对"以 **S2 板上 vs tree_io_*.csv 双套逐位** 为准，本轮是其桌面前置。
- **下一步**：S2（板上 bit-exact，待台架）→ S3（cycle 计数填实）→ S4-S5（core-only MCPS [L1/EZKIT] + R1 §5 判据判定）。
- **挂接**：R1 / R14（FIRA 闸门维持）/ DEC-S2-002（树形锁定）/ DEC-S3-PROC-01（定点）/ DEC-S4-DSP-01（bit-exact 基准）/ DOC-S4-CORE-PLAN-01 / DOC-S4-DSP-INV-01。

---

*DOC-S4-CORE-S0S1-01，dsp-algorithm 实现 + PM 直跑收尾验证 2026-06-02。host 双套 bit-exact PASS [L2 host 预验]；核 md5 verbatim；三盯点落实。板上 [L1/EZKIT] 待台架。R14 闸门维持，无 FIRA。*
