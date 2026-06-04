# 4 子带树形 FIR — 现有 C 资产盘点 + CCES/SHARC 迁移起点

**文档 ID**：DOC-S4-DSP-INV-01
**日期**：2026-06-02 ｜ 产出：PM 直跑 grep 查证（socket-safe）｜ 性质：纯盘点，不写新代码、不跑仿真
**用途**：R1 真闭合需我方 4 子带算法上板实测；迁移前先盘清已有资产，避免重造。每条结论挂 file:line 出处（过 critic C1）。

---

## 项1：4 子带树形结构设计 — ✅ **存在**（独立设计文档 + LOCKED 决策，非仅代码注释）

| 要素 | 内容 | 出处 |
|------|------|------|
| **锁定决策** | dyadic 树形半带 FIR（非全速率直接 FIR），48kHz，4 子带 500-1k/1k-2k/2k-4k/4k-8k | `decisions_log.md:91`（DEC-S2-002）；亦 `:50/:56/:94` |
| **子带划分 + 抽取比 + 半带阶数**（设计表） | SB0 500-1k/16×/31 tap；SB1 1k-2k/8×/63 tap；SB2 2k-4k/4×/63 tap；SB3 4k-8k/2×/63 tap | `dsp_8ch_report.md:40-45`（§2.1 子带划分表）|
| **树形拓扑** | 3 级 dyadic 树（→4 子带）；每级 1 个 decimating 半带 + 1 个 interpolating 半带求 detail；差分金字塔 PR 精确 | `tree_filterbank.h:3-5,54,103`；拓扑图 `dsp_8ch_report.md:220-234` |
| **群延迟构成** | Σ(N-1)/2/fs_level，63-tap/3 级，与通道数无关 | `dsp_8ch_report.md:106,123` |

> 结论：设计**有独立文档**（`dsp_8ch_report.md §2.1` 设计表 + `decisions_log` DEC-S2-002 锁定），不是只散在代码注释。子带划分/抽取比/半带阶数/拓扑四要素齐全。

---

## 项2：现有 C 代码 — ✅ **已成型 + 桌面 bit-exact 验证过**（可作迁移起点）

**规模与函数**（实测 wc/grep）：
| 文件 | 行数 | 内容 | 出处 |
|------|------|------|------|
| `sprint3/dsp/tree_filterbank.c` | **209** | 全功能定点核 | `tfb_set_coeffs:68` / `tfb_channel_init:74` / `hb_push_filter:85` / `hb_decimate2:108` / `hb_interp2:121` / `tfb_analyze:139` / `q31_mul:178` / `tfb_synthesize:183` + 饱和原语 `sat_i64_to_i32:43/47`、`sat_add_i32:44/55` |
| `sprint3/dsp/tree_filterbank.h` | 146 | 接口/常量（TFB_NUM_LEVELS=3 等）| `:54` |
| `sprint3/dsp/tree_verify.c` | 224 | 桌面验证主程序 | — |
| `sprint3/dsp/tree_verify_adversarial.c` | 188 | 对抗验证 | — |

**定点格式**：Q15 系数 × Q31 状态 → Q46(int64) 累加 → `>>15` 回 Q31；含 PF-4 三处饱和钳位（`tree_filterbank.c:43-60,102`）。

**桌面验证实证**（`pf4/PF4_INTEGRATION_SUMMARY.md` + `sub2_fixed_vs_float.md`）：
- 纯 Q31 算术截断 SNR **172.8–175.5 dB**（≫140dB 门禁）— `PF4_INTEGRATION_SUMMARY.md:26` / `sub2_fixed_vs_float.md:24`
- 端到端定点 vs 理想浮点 **74.6–78.7 dB**（Q15 系数字长主导，非算术缺陷）— `sub2_fixed_vs_float.md:25`
- 整树重建 PR **~300dB**（代数 telescoping 保证）— `PF4_INTEGRATION_SUMMARY.md:25`
- 相位漂移 **0**（互相关 1.0000）— `PF4_INTEGRATION_SUMMARY.md:26`
- **bit-exact**：饱和修复前后"重建数值逐位一致，已 bit-exact 验证" — `tree_verify.c:98`
- **三路互验**：独立编译 C（316.4dB, err 3.9e-16）+ numpy（74.6-78.7/172.8-175.5）+ 自写独立整数实现（SB0=74.9）三路吻合 — `PF4_INTEGRATION_SUMMARY.md:46`

> 结论：C **已成型**（非片段），**桌面 bit-exact + 多路 SNR/PR 验证过** → **可作迁移起点（不需从零写）**。
> 诚实边界：以上全为**桌面 [L2]**；SHARC 逐 bit 真值（含流水线/寄存器宽度/cache/中断）属 PF-5/EZKIT 实测范畴（`PF4_INTEGRATION_SUMMARY.md:56`）= R14 待验。

---

## 项3：bit-exact 参考

### 3a — C 自带测试向量：✅ **存在**
- `sprint3/dsp/tree_io_sat.csv`（2.25 MB）+ `tree_io_unsat.csv`（2.25 MB）= 输入 vs 重建逐样本向量，由 `tree_verify.c:148` 写出（源码 `fopen` 写泛名 `tree_io.csv`，**sat/unsat 为饱和钳位开/关两轮运行后重命名落地的变体**，critic C1 核实），供频谱平坦度/混叠分析 — `tree_verify.c:13,148,152`。
- 用途：CCES 迁移后**位真回归基准**（板上输出须逐位匹配此 golden vector）。

### 3b — 独立 MATLAB 定点参考：❌ **不存在**
- grep 全仓 + `~/matlab-agent` 无任何 .m 文件生成树形/半带/子带定点参考输出。
- 现有交叉验证为 **numpy/Python**（`sprint3/dsp/pf4/xcheck_subband.py`）+ 独立 C + 自写整数实现，**非 MATLAB**。
- 影响：若按 POLICY 铁律七（双轨独立工具核，MATLAB 为第二工具）要 MATLAB 轨确认 R14 bit-exact，**需先生成**（列入缺口）。当前 bit-exact 迁移对齐基准 = C golden vector（3a）+ numpy（已有，但同 Python 生态非独立工具）。

---

## 迁移起点定性：**适配已有 C（非从零写）**

`tree_filterbank.c`（209 行）已成型、桌面 bit-exact + SNR 172-175dB/PR 300dB 多路验证 → **迁移 = 把已验证定点核适配到 CCES/SHARC**（工程化层面），**不重写算法**。

---

## 缺口清单（迁移前需补，逐条挂出处）

| # | 缺口 | 依据 | 性质 |
|---|------|------|------|
| G1 | **独立 MATLAB 定点参考不存在** | 项3b（grep 无 .m） | R14 若要 MATLAB 双轨核需先生成；否则用 C golden vector(`tree_io_*.csv`)+numpy 作基准 |
| G2 | **8ch 接口未落地**：现 `tfb_*` 为单通道，8ch 需 ×8 循环（8 份 `TreeChannelState`） | `tree_filterbank.c` 单通道签名（`tfb_analyze:139`）；`PREP-DSP-migration.md §1` | 迁移工程项 |
| G3 | **系数头接线**：`tfb_set_coeffs`(`:68`) 需喂 `fir_coeffs.h`（SB0=31 tap / SB1-3=63 tap Q15） | `tree_filterbank.c:68`；`PREP-DSP-migration.md §1.3` | 迁移工程项 |
| G4 | **CCES 骨架不一致**：`cces_skeleton` 为 float 描述、文件名 `dyadic_analysis.c` 非 `tree_filterbank.c`，需统一改调 `tfb_*` | `PREP-DSP-migration.md §1.2`（`sprint3/dsp/cces_skeleton/`）| 迁移工程项 |
| G5 | **CCES 工程化未落地**：.ldf 内存布局（L1 热点/L2 系数）、cycle 计数器寄存器填实、SIMD/零系数跳过优化 | `PREP-DSP-migration.md §2/§4` | 迁移工程项 |

> 关键判断：**G1 是唯一"资产缺失"类缺口**（需新生成）；G2–G5 均为"已有 C → CCES 工程化"的适配项，非算法重造。

---

## 挂接
R1（命门，待我方算法上板实测）｜ DEC-S1-004 / DEC-S2-002（树形结构锁定）｜ Split-Task 迁移（`DOC-S4-INPUT-01` INPUT-1）｜ `PREP-DSP-migration.md`（上板迁移技术点）｜ R14（FIRA bit-exact 闸门，依赖 3a/G1 的 bit-exact 基准）

---

*DOC-S4-DSP-INV-01，PM 直跑 grep 查证 2026-06-02。三项各给"存在(file:line)/不存在(明写)"；迁移起点 = 适配已有 C；缺口 G1 需生成、G2-G5 为工程适配。纯盘点，无新代码、无仿真。*
