# sprint7/dsp/firbench — 每通道 FIR 算力台架包（DEC-S7-SIDE30-01 ③ 的 go/no-go 测量）

> dsp-algorithm teammate，2026-09-27。上游：`sprint7/docs/S7_SIDE30_PERCH_FIR_DESIGN.md` §5/§6-3/§7-6（算力开放问题）；DEC-S7-SIDE30-01 ③④（`sprint2/docs/decisions_log.md` 末尾）。测试员操作单：`sprint7/docs/S7_FIRBENCH_RUNBOOK.md`。
> **诚实声明**：本机无 cc21k、无板。本目录的一切 "PASS" 都是桌面 gcc / numpy **[L2]**；FIRA 路径在桌面上只跑在自写的**行为模型**上（`host/fb_fira_emu_host.c`）= **[L2 emulated plumbing]**，证明的是"编排代码与所假设的 Legacy 行为自洽"，**不是芯片证据**。真正的编译门 = 测试员 CCES build；cycle 只能上板得到，**本目录一个板上数字都不填**。
> **状态**：独立 critic R3d（2026-09-27）判 **CONDITIONAL**（0 BLOCKER / 2 MAJOR / 4 MINOR / 1 INFO；§12 各门 FG1/FG2/IO1/IO2/ST1 判 PASS，golden 24/24 由 critic 独立复现）→ A-1…A-7 已整改（§7），**待 delta 复审**；未 commit、未获 CTO_OK（DEC-S7-SIDE30-01 ④ 逐包先例）。三道关（自动 verify → 独立 critic → CTO 常识审）第二道未闭合。
> **2026-09-29 状态更新**（上一行原文保留）：R3d 的 delta 与 mini-delta 两轮对本包均判 PASS，已入库（`0ef46c4`）；CTO_OK 已给（CTO 2026-09-29 原话「恩，我同意sfirb可以」）。

## 0. 文件清单与指纹

| 文件 | 作用 | md5（2026-09-27，R3d 整改后） |
|---|---|---|
| `s7_firbench.c` | 台架 TU（新文件；直接调 Legacy `adi_fir_*`，不调冻结 `fira_tree.c`） | `20eb427285d33dfb5c536c08cec9838f` |
| `s7_firbench.h` | 读数声明 + 入口 `s7_firbench_run()` | `1d7abbb979f1dc5540f478ff69abe123` |
| `fb_coeffs.h` | **生成件**：8 路 V1 系数 63/127/255 抽头（Q15 值存 int32）+ 系数表/chirp CRC 指纹 | `cf8b7aa8b7f959965856f6d5c02d6ceb` |
| `fb_goldens.h` | **生成件**：3 套 × 8 路 golden CRC32 | `f4f457814cce9881ae342ae2eb8f57e1` |
| `tools/gen_firbench_tables.py` | 系数 + golden 生成器（golden 第一轨 numpy；`--check` 逐字节核对两份头文件） | `6da92398b058e2458a4f2eb715326ae6` |
| `host/fb_ref_host.c` | golden 第二轨（纯 C 整段卷积）+ 占位版 FAIL 证明（C 轨） | `3178905f5566d5598df42a5ca86800c6` |
| `host/fb_fira_emu_host.c` | 桌面 Legacy FIRA 行为模型（只用于桌面检编排；`-DFB_EMU_STUB` = "加速器不写"占位版） | `64a5358ac3572bb1053944cbe48fc90f` |
| `run_firbench_host.sh` | 桌面构建 + 运行 R0/R1/H1–H4（§4） | `9a78bec66386240f8005688ba1c95700` |
| `run_firbench_guard_check.sh` | 桌面守卫检查 (A)–(G)（§4） | `17f0e7ac546cb493781219f19d88057e` |
| `bench_main_firbench.diff` | bench 接线补丁**文本**（不直接改 `bench_main.c`，由测试员应用） | `f7ad667bba47533685b930bfc44535b0` |
| `sprint7/docs/S7_FIRBENCH_RUNBOOK.md` | 测试员操作单（中文） | `adc1a9e09b3ee20940e15c1614494a7b`（2026-09-29 页头加状态更新后；R3d 审定版为 `19e2e702a29565860ff144509d689d07`） |

只读输入指纹（本包未改动任何既有文件；守卫检查 (G) 每次核）：`chirp_input.h` `f38270f3b963265129bdf45c34ad2b6f`｜`dolph_w8_q15.h` `ef2b75235a15b69b63b445ecffd8cf7f`｜`bench_main.c`（补丁基线）`25090f2c29d6729443bef5ed1feb5d31`｜`fira_tree.c` `7616c41102946c357e9c70fafcd51da3`（未调用，仅证未动）｜`s7_fir_coeffs_127tap.csv` `93792b2473b01eb959afb50d0b644e19`｜`s7_fir_robust_design.py` `e2938a9eb0e8872e23fe493fc759d119`｜`s7_common.py` `f68a834fd08ba184fc8aad6aeed7e24e`｜探针补丁 `bench_main_s7.diff` `0b1e7252f0b20344aa65a8a08ef87ef8`。
打补丁后 `bench_main.c` 的 md5（桌面 `patch -p1` 实得）：只打本补丁 `d003d326da30a673dc33d7900aba5a51`；本补丁与探针补丁叠加（两种顺序结果逐字节相同）`5b3b459894e9d1949fce5b087418549c`。

## 1. 量什么

每帧 64 样点（48 kHz，750 帧/s）、8 路、单声道输入（8 路滤同一个输入：每通道 FIR 取代今天的"Dolph 权 + 恒等树"，权重折进系数），三档抽头 **63 / 127 / 255 真实抽头**（= 设计文档的 64/128/256 档，设计脚本自己的 `TAPS=(63,127,255)`，奇数长 → 整数群延迟 31/63/127，末位补零不装载），五条路径：

| 下标 | 路径 | 每帧做什么 | 为什么要量 |
|---|---|---|---|
| 0 | `FIRA_T8` | 8 个任务，每路一个：CreateTask(1 路) → FixedPointEnable → QueueTask → 自旋等 DONE → invalidate → postscale | 与冻结 `fira_tree.c` 每段一任务的写法同构（M2 今天每帧 72 个任务）；给出"每任务固定开销 × 8"的上界 |
| 1 | `FIRA_T1` | 1 个任务装 8 路：CreateTask(8 路) → FixedPointEnable → Queue → 一次 DONE → 一次 invalidate → 8 路 postscale | 每帧重建 TCB（线性输入，与硬件索引回写无关），是 P1 失败时的稳妥退路 |
| 2 | `FIRA_P1` | 8 路任务**只在初始化建一次**、设一次定点；每帧只写 64 个新样点进环形缓冲 → QueueTask → DONE → invalidate → postscale | 每帧核侧开销最小。布局照 ADI EE408 `Direct_Replacement`（`Processing.h:13-16`、`Processing.c:182` 每块重排同一任务）。**[ASSUME P1-IDX]**：Legacy 在每次运行后把输入索引 +64、输出索引 +192 回写 TCB（归档 legacy 头对 `ADI_FIR_CHANNEL_BUFFER_INFO`/`UpdateTask` 的注释）；该例程是浮点、每路各自输入缓冲，本包是定点、8 路共用一个输入缓冲 → **[L4]，以板上 golden 为准** |
| 3 | `CORE_C` | 纯核可移植 C，直接型，int64 MAC | 给出**本台架构建设置下可移植 int64 C 写法**的板上账（设计文档 §5 只有 [L3×30–50 cyc/MAC]）。**不是核能做到的最好实现**：没有测原生 MR/SIMD 写法，也没有测库函数 FIR，所以**不能单凭它得出"核上不可行"的结论** |
| 4 | `CORE_SYM` | 纯核可移植 C，对称折叠（乘法减半，整数运算精确 → 与直接型逐位相同） | 可选优化变体 |

**括号**（每帧）= 输入入缓冲 + 8 路计算 +（FIRA）DONE 自旋 + cache invalidate + postscale 到 Q31 +（线性路径）历史 memmove。T8 / T1 每次调用都新建 CHANNEL_INFO（栈上局部变量，与 `fira_tree.c:468` 板上已验证的写法相同，重建开销在括号内）；P1 的通道表是静态数组，每次运行只建一次，任务存活期间不改动（ADI Direct_Replacement 的全局 `FirTaskChannels[]` 同理）。CRC、统计、IO1 检查全在括号**外**。统计 = last / max / min，取第 4–1023 帧（前 4 帧热身照跑、照进 CRC，不进统计，同 F7/H1/S7 探针纪律）。每条路径 × 每档抽头都从零状态跑完整 1024 帧冻结 chirp。

**未量**（TODO，§6）：8 个单路任务一次性建好后成批排队；ACM 模式；FIRA 浮点模式；与 SPORT DMA / RX ISR 并发时的争用（台架无音频 I/O，同 S7 探针 §7 的已知差异）。

## 2. 定点格式与系数

| 项 | 取值 | 出处 |
|---|---|---|
| FIRA 模式 | Legacy，`SINGLE_RATE`，`nWindowSize=64`（输出数），`adi_fir_FixedPointEnable(SIGNED_INTEGER)` 在 CreateTask 之后、QueueTask 之前 | 与 `fira_tree.c:177-206,472-477` 相同 |
| 系数字 | Q15 的**值**放在 int32 字里：`c = floor(h·G·2^15 + 0.5)`；可超过 32767（同 `g_dolph_w8_q15[7]=32768` 的做法） | 生成器 |
| 增益归一 | 与今天 Dolph-20 表（最大权 1.0）等轴向增益：`G = 2·Σw8/max(w8) = 12.885911891` | `s7_fir_robust_design.py d20_axis_level()`；设计文档 §6-4 |
| 数据 | Q31 int32（冻结 chirp，0.289 FS） | `chirp_input.h` |
| 累加 / 回写 | 精确整数 MAC；FIRA 每个输出写 3 个 32 位字（LSW/MSW/溢出），核侧取低 64 位 | DP-01；`fira_tree.c:345-358` |
| postscale | `y = sat32(acc >> 15)`（算术右移 = 向下取整）——与树路径唯一收敛口径同一截断点，不新开截断级 | skill A1；`fira_tree.c:362-366` |
| 对称 | 只量化前半（k=0..M）再镜像 → 整数系数严格对称 → FIRA 抽头方向无关（同 `fira_tree.c` [ASSUME A-orient] 的论证），折叠核路径成立 | 生成器 + `fb_ref_host.c` 复核 0 处不对称 |

系数来源（可复现、无手改）：127 抽头 = 冻结 CSV `s7_fir_coeffs_127tap.csv` 的 V1 八行（任务书指定的"V1-128"正确性集）；63 / 255 抽头 = 同一设计代码路径（`sigma2_gain(seed 20260926) → perbin_design(V1) → smooth_logf → fit_fir(L)`，只读 import、内存中运行，不调用其 `main()`、不写其任何输出）。

生成器报告 [L2 host, numpy]：127 抽头重算 vs CSV 最大差 4.6e-13（相对 5.7e-12），量化后 0 个抽头不同；三档独立四舍五入会破坏对称的抽头数 0；max|c| = 34007 / 33779 / 33792（1.0378 / 1.0309 / 1.0312，与设计文档 `s7_fir_headroom.csv` 的 1.038/1.031/1.031 一致）；每路 Σ|c| 最大 69123 / 71378 / 68784；max|acc| = 2^44.64 / 2^44.50 / 2^44.48（远低于 64 位，低 64 位重组无损）；**饱和 0 次**（该激励下 golden 与饱和行为无关）。

## 3. 正确性门（critic §12）

| 门 | 本包怎么做 | 证据 [L2] |
|---|---|---|
| **FG1** | 逐通道比对每路 Q31 输出流（1024 帧整流）的 CRC32 与 golden；**从不比通道和**（Σ_c 2h_c = δ 是代数恒等，同树的 telescoping） | 顺带核对：chirp 本身的 CRC32 = `0x90556BC7` = 已退役的端到端 golden，正是 telescoping "out==in" 的直接体现，也独立证明本包 CRC 与 `bench_harness.c crc32_buf` 同算法 |
| **FG2** | 桌面：占位版 Dolph-20×δ[k−M] 与均匀 (G/16)×δ[k−M] 两套过同一参考，**每档每路都必须不中 golden**，且只看 0.7–5.2 kHz 窗口（第 576–902 帧）也不中；模型 stub 模式（"加速器不写"）下三条 FIRA 路径全 FAIL。板上：同一次运行里把 Dolph-20×δ 过 `CORE_C`（127 抽头）→ `g_fb_neg_fail_all` 必须 = 1 | 生成器：6 组 × 8 路全不中、窗口内也全不中，窗口内 max\|差\|/max\|y\| 在 +0.6 … −17.6 dB；`fb_ref_host`：48/48 不中；H3：FIRA 3 路 × 3 档 × 8 路全 0、IO1 全 0；H1/H2：`neg_fail_all=1` |
| **Σ2h=δ** | 从不作系数检查：三套占位与真系数的 Σ_c 2c_c 在取整误差内相同（422240–422266），但 golden 全不中；系数表逐值核 = 表 CRC（`g_fb_coef_ok[t]`） | 生成器报告 |
| **IO1** | 输入 = [ntaps−1 历史 \| 64 新]，每次运行先清零再入缓冲 → 全部已初始化；线性计数恰为 ntaps+63（126/190/318），环形长度 L = 128/192/320 ≥ ntaps+64；输出每路恰 64×3 字，第 0 帧用哨兵 `0x5A5A5A5A` 查"全写满、背后 8 个保护字未被写" → `g_fb_io1`；各路输出区各自独立（无共用 scratch），每次运行前重置哨兵并 flush；DONE 后、postscale 读前 `flush_data_buffer(..,1)` 失效，中间无核写 | H2：FIRA 3 路 × 3 档 `io1=1`；H3：`io1=0` |
| **ST1** | ntaps−1 个输入历史跨帧携带（单声道输入 → 8 路共用一份；各路的"态"= 各自系数）；线性路径 memmove 尾部，P1 靠硬件回写索引 | 变异测试（scratch，不入库；R3d 整改后的代码上重跑，结果不变）：去掉历史 memmove → T8/T1/CORE_C/CORE_SYM 全 FAIL、P1 仍 PASS；模型不回写输入索引 → 只有 P1 FAIL。两道 golden 对 ST1 敏感且各自定位到对应路径 |
| **盲区（A-7）** | 所有系数集严格对称 → 抽头顺序/数据方向不可见；只落在累加结果 bit 15 以下、且不进位越过 >>15 截断边界的误差不可见；本激励不触发饱和（0 次），饱和路径未被检验 | 变异测试 [L2 emulated]：模型抽头反序 → 5 路 × 3 档全 PASS（不可见）；模型丢掉累加结果低 15 位 → 全 PASS（不可见）；只丢 bit 15 → FIRA 3 路 × 3 档全 FAIL（可见）。故本台架结果**不得作为非对称系数或每台校准系数集的 [L1] 依据**（§6 TODO） |
| **IO2** | 每条路径 × 每档都从重新清零的缓冲开始；读到陈旧/未初始化数据必改 CRC；板上同时抄 `g_fira_f4_pass`/`g_f5_pass_all`（本 TU 新增约 32 KB 静态改变链接布局）作布局哨兵 | — |

**golden（[L2 host]，双轨一致）**：第一轨 = 生成器（numpy int64 `np.convolve` 整段 65536 样点 + `zlib.crc32`）；第二轨 = `host/fb_ref_host.c`（纯 C 整段卷积，不分帧、不用历史缓冲 → 同时交叉检查台架的分帧/ST1 逻辑）：24/24 相同。

| 抽头 | c0 | c1 | c2 | c3 | c4 | c5 | c6 | c7 |
|---|---|---|---|---|---|---|---|---|
| 63 | `407C61FA` | `02648ED2` | `F638EB38` | `29B3B51A` | `3F36D7E3` | `4BFDD6B4` | `DB88122B` | `A8F9415F` |
| 127 | `55E4C89C` | `A3736944` | `8BABD4CE` | `18EC6E13` | `4B1E1B22` | `FAD896E7` | `D40F6375` | `0F9DADE0` |
| 255 | `51AA2611` | `FD21C3CA` | `736BC676` | `77310752` | `80C34462` | `CD255C36` | `18FE58DC` | `295BA20B` |

## 4. 桌面检查实跑（2026-09-27，gcc 11.4.0 / Python 3.10，[L2]）

`./run_firbench_guard_check.sh` → **overall PASS**：(A) 目标守卫区语法；(B) 加 `FIRBENCH_FLUSH_IN`+`FIRBENCH_P1_FXD_EACH`；(C) 桌面路径；(D) 补丁单打、与探针补丁两种顺序叠打均无冲突且结果相同；(E1/E2) 打补丁后的 `bench_main.c`（单打 / 叠打）守卫配置语法；(F) 新 .c/.h/.diff 全 ASCII；(G) 只读输入 md5 未漂移。无告警。

`./run_firbench_host.sh` → **overall PASS**：

| 步 | 内容 | 结果 |
|---|---|---|
| R0 | 生成器 `--check`：两份头文件重生成逐字节相同 + FG2 报告 | IDENTICAL ×2；占位全不中 |
| R1 | `fb_ref_host`（第二轨） | golden 24/24；占位 48/48 不中；饱和 0；不对称 0 |
| H1 | 台架 TU，无 FIRA | 核两路 × 3 档 × 8 路全 PASS（走台架自己的分帧/历史代码）；FIRA 三路诚实"未构建"（rc −1、pass_all −99）；`neg_fail_all=1`；`valid=0` |
| H2 | + 桌面 FIRA 模型 | 5 路 × 3 档全 PASS，FIRA 路 `io1=1`（**[L2 emulated]，不是芯片证据**） |
| H3 | + 模型 stub（不写输出） | FIRA 3 路 × 3 档 × 8 路全 FAIL、`io1=0`；核路仍 PASS |
| H4 | + 模型 + 两个可选宏 | 同 H2 |

桌面 cycle 数（`clock()`）无意义，不引用。

## 5. 板上接线（摘要；逐步操作见 runbook）

1. source list 加 `sprint7/dsp/firbench/s7_firbench.c`（与 `fira_regression.c` 同一 FIRA build）；include path 加 `sprint7/dsp/firbench` 的**绝对路径**（`${repo}` 不是 CCES 变量，IMPORT_GUIDE R52 教训）。
2. 对 `sprint4/dsp/core_only/bench/bench_main.c` 应用 `bench_main_firbench.diff`（基线 md5 见 §0；可与探针补丁叠打）。调用位于 H2 之后、最后运行。
3. 不改 build 配置（同 F7/探针那次）；Defined symbols 已有 `TARGET_SHARC`、`FIRA_USE_REAL_ADI_FIR_HEADER`。`FIRBENCH_FLUSH_IN` / `FIRBENCH_P1_FXD_EACH` 只在 runbook 故障分流里按需加。
4. 静态内存（桌面 x86 目标文件统计 [L2]；SHARC 上的实际占用与放置以本次 build 的 `.map` 为准）：`.bss` ≈ 18.0 KB + `.rodata`（系数）≈ 14.4 KB ≈ 32 KB；不 include `chirp_input.h`（目标上走 `bench_chirp_input()` 单副本）。若链接报 li1040：**报回，不要缩算法、不要自行加 section pragma**（放置改动另走门）。

## 6. 假设、风险与 TODO

- **[ASSUME P1-IDX]**（§1）——若只有 P1 不过：先加 `FIRBENCH_P1_FXD_EACH` 重跑（区分"定点模式不跨次保持"与"索引不回写"），仍不过 → 该假设被板上证伪，P1 行作废，用 T1 行。
- **[ASSUME FLUSH-IN]**：同 `fira_tree.c`，核写的输入不显式 flush（F4/F5 [L1] 先例：驱动 cache 管理或 L1 不缓存）。若 FIRA 全不过而核全过 → 加 `FIRBENCH_FLUSH_IN` 重跑。
- 8 路共用一个输入缓冲是 [L4]（ADI 例程每路各自缓冲）。若 T1 与 P1 都不过而 T8 过 → 记录上报，这是首要怀疑项（本包暂不提供每路独立输入的变体，TODO）。
- 台架无 SPORT DMA / RX ISR → 量到的是"无 I/O 争用"的墙钟；进 M2 后的争用另算（H2 口径）。
- **跨 build 拼接（A-1）**：台架 build（F0 记载 `-O -Ov=100`，`FIRA_IMPL.md:72`）与 M2 build（`m1_cces_project` Debug，`-O` 实际值未核实，`S7_B63_WALLCLOCK_GAP.md:38-41`）的优化配置未必相同，台架与 M2 同口径墙钟本就有 1.79× 未解释差距（`S7_B63_WALLCLOCK_GAP.md:19`，[L1-derived]）。在两边优化配置逐项相同且都有记录、S-B / B6.3 出结论、M2_SEG_CYC 实际回收之前，FIR cycle **只对帧预算（CCLK/750）报告**，不与 M2 分段读数相加减（runbook §9 第 5 步）。
- **放置（A-2）**：系数表与 `s_fb_lin/circ/out3/y` 落在 L1 还是可缓存 L2，会一阶影响核路径 cyc/MAC 与 FIRA DMA 时间，也决定 [ASSUME FLUSH-IN] 是否真被检验。TU 提供运行时地址读数 `g_fb_addr_*`，测试员同时回传 `.map`；数据在 L2 时读数须标「[L1 bench，数据在 L2（可缓存）]」（runbook §7、表 A2）。
- **盲区（A-7）**：见 §3 表"盲区"行。
- 真冷 cache WCET 未测（与 H1 同一局限）：max 是 1020 个热帧里的最大值，不是完整 WCET。
- 系数是 bench 用的 [L2] 设计，不是产品系数；每台复数校准会使系数不再对称（抽头方向届时必须上板锁定，TODO）且可能变长（可用三档数据外推）。
- TODO（按价值排序）：⓪ 抽头方向探针（非对称系数）与饱和激励——补上 A-7 盲区，是把本台架结果用于校准系数集之前的前提；① **P1 的线性缓冲孪生变体**（持久任务 + 每帧 memmove 历史，假设驱动/硬件**不**回写索引）——与现 P1（假设回写）互补，两者恰有一个应过 golden，既保住"持久任务"这一最低开销组织的测量，又顺带在板上 [L1] 定下 Legacy 索引语义（超时未做）；② 8 个单路任务一次建好成批排队的变体；每路独立输入缓冲的变体；ACM 模式；与 M2 帧循环（含 SPORT/ISR）同 build 的在环测量；抽头方向探针（非对称系数）。

## 7. critic R3d 整改记录（2026-09-27；R3d 判 CONDITIONAL，待 delta 复审）

| 项 | 级别 | 整改 |
|---|---|---|
| A-1 | MAJOR | runbook §9 第 5 步改为有条件：跨 build 相加减须同一优化配置（两边优化选项原文与构建指纹都记录）、S-B/B6.3 已出结论、M2_SEG_CYC 实际回收、同一 CCLK；删去"已回收"的错误说法；条件不满足时只报 FIR 对帧预算。表 A 增"编译器优化选项原文 + 截图"一行 |
| A-2 | MAJOR | TU 新增运行时地址读数 `g_fb_addr_coef[3]`、`g_fb_addr_lin/circ/out3/y`；runbook 新增表 A2（地址 + `.map` 段）、表 A 增 `.map` 文件名/md5 一行、回传清单加 `.map` 与优化设置截图；§7 加放置判读规则（L2 → 标注；缺 `.map`/地址 → 暂不出判定） |
| A-3 | MINOR | README §1 与 runbook §9 第 3 步：CORE_C/CORE_SYM 标为"本台架构建设置下的可移植 int64 C，不是最好实现（未测 MR/SIMD/库函数）"，并写明不能单凭它得出核上不可行 |
| A-4 | MINOR | 采用首选方案：T8/T1 每次调用新建 CHANNEL_INFO（栈局部，同 `fira_tree.c:468`）；P1 用只建一次的静态通道表；runbook §8 加"T8 与 T1 不过、P1 过 → 停，发回"与"其他任何失败组合 → 停，发回"两行 |
| A-5 | MINOR | §5 第 4 条原先对 [L2] 桌面数字用了 L1 专用的测量用词，已改为"统计"，并注明 SHARC 实际占用以 `.map` 为准 |
| A-6 | MINOR | runbook §3 第 4 步：推荐只给工程实际编译的副本打补丁（`patch <副本> < diff`，桌面验证 md5 同为 `d003d326…`）；若只能改仓库文件，会话结束后 `git checkout --` 还原并以 `git status` 确认，不 commit、不 reset |
| A-7 | INFO | README §3/§6 与 runbook §9 第 7 条写明三处盲区（对称 → 方向不可见；bit 15 以下且不越界的累加误差不可见；无饱和），附桌面变异证据 [L2 emulated]；不得作非对称/校准系数集的 [L1] 依据；列入 TODO |

整改后重跑：`run_firbench_host.sh` PASS（R0 生成器 `--check` 两份头文件 IDENTICAL、R1、H1–H4）、`run_firbench_guard_check.sh` PASS（A–G）[L2]；`fb_coeffs.h`、`fb_goldens.h`、`bench_main_firbench.diff` 均未变（md5 同前），打补丁后 `bench_main.c` 的两个 md5 不变。
