# sprint7/dsp/probe — B6.3 bench 侧墙钟三段拆分探针（WO-S7-B6.3）

> dsp-algorithm teammate，2026-09-02。依据 DEC-S7-IMPL-01 第 (1) 项 b（bench 侧 `fira_tree` 诊断副本 + 三段括号）。
> 设计与判读文档：`sprint7/docs/S7_B63_WALLCLOCK_GAP.md`（§2 = 本探针，§3 = 板上三段括号规格，§4 = 排查表）。
> **诚实声明**：本机无 cc21k、无板，本目录的一切"PASS"都是桌面 gcc 语法/宿主运行 [L2]；真正编译门 = 测试员 CCES build（D14）。
> 所有 cycle 数值只能上板得到，本 README **一个板上数字都不填**（回填模板留空）。

## 0. 文件清单与指纹

| 文件 | 作用 | md5（2026-09-02） |
|---|---|---|
| `s7_wallclock_probe.h` | 读数声明 + 入口原型 | `3f359cd53ed91ece6aaa22cc9d2163d1` |
| `s7_wallclock_probe.c` | 探针本体（新 bench TU，不改 `fira_regression.c`；链式读法、可选 `S7_PROBE_SYN_FG`） | `8f63aa7847f167fcfdb92c78d1645ea8` |
| `fira_tree_probe.c` | **诊断专用副本**：冻结 `sprint4/dsp/fira/fira_tree.c` + 内括号（§4 登记） | `4e94a6ede8e05915449ff2ad45884401` |
| `tools/make_fira_tree_probe.py` | 由冻结件机械生成/校验副本（insert-only，`--check` 验逐字） | — |
| `guard_stub_inc/drivers/fir/adi_fir.h` | 桌面语法检查用的 Legacy 头**转录**（字段序同归档真头，仅解析、不链接） | — |
| `run_s7_probe_guard_check.sh` | 桌面 `gcc -fsyntax-only` 守卫检查 A–H（§5） | — |
| `run_s7_probe_host.sh` | 桌面 gcc 编译 + 运行 H1/H2/H3/H4（§6） | — |
| `bench_main_s7.diff` | bench 接线补丁**文本**（不直接改 `bench_main.c`，由 CTO/测试员应用，§2） | `0b1e7252f0b20344aa65a8a08ef87ef8` |

冻结件指纹（本目录不改动任何冻结件）：`sprint4/dsp/fira/fira_tree.c` md5 `7616c41102946c357e9c70fafcd51da3`（副本复制时的值，守卫检查 (H) 每次核）；`sprint4/dsp/core_only/bench/bench_main.c` md5 `25090f2c29d6729443bef5ed1feb5d31`（补丁基线）。

## 1. 探针量什么（与 F7 同口径，再拆三段）

`s7_wallclock_probe()` 用与 F5/F7/M2 **完全相同的调用序列**（`fira_tree_setup` → `tfb_set_coeffs` → `fira_channel_init`×8；每帧每通道 `(w_q15·x_q31)>>15` 加权 → `fira_tfb_analyze` → `fira_tfb_synthesize`）跑冻结 `CHIRP_INPUT` 的**全部 1024 帧**（帧主序：每帧内通道 0..7，与板上 `m2_fira_beam_frame` 同序），每帧读数：

| 读数 | 括号罩什么（每帧 8 通道之和） | 对应板上符号（s7-base 实现） |
|---|---|---|
| `g_s7_seg_w_cyc_{last,max,min}` | 64 样本加权乘法循环（`f5_apply_w` 语义）+ c>0 的循环增量（链式：从上一路 syn 关括号到本路 w 关括号；板上是从上一路 tx 关括号） | `g_m2_seg_w_cyc_*` |
| `g_s7_seg_ana_cyc_{last,max,min}` | `fira_tfb_analyze` 调用本身 | `g_m2_seg_ana_cyc_*` |
| `g_s7_seg_syn_cyc_{last,max,min}` | `fira_tfb_synthesize` 调用本身 | `g_m2_seg_syn_cyc_*` |
| `g_s7_beam_cyc_{last,max,min}` | 整个 8 通道循环（= `fira_regression.c:611-619` F7 口径） | `g_m2_beam_cyc_*` |
| `g_s7_seg_sum_last` / `g_s7_probe_ovh_last` | 同一帧 w+ana+syn / beam − sum（= 链首 1 次读 + 循环进出，≈1–2 次读量级；24 次内层读分摊在三段内，每段 8 次） | —（板上 = tx 段 + 循环开销） |
| `g_s7_reads_per_frame` | beam 括号内 CCNT 读次数 = 1 + 3×8 = **25**（链式；板上 1 + 4×8 = 33） | 扣除量 = 25 × `g_s7_ccnt_read_cyc` |
| `g_s7_ccnt_read_cyc` | 背靠背两次 `bench_cyc_target()` 之差 = 一次读的成本（扣扰动用） | 建议板上同加 |
| `g_s7_frames` / `g_s7_frames_total` | 进统计的帧数（去掉前 `S7_WARM=4` 热身帧）/ 跑过的帧数（应 1020 / 1024） | — |
| `g_s7_cclk_hz` / `g_s7_cclk_rc` | CCLK 复读（应 1e9 / 0，G6 一致性） | — |

**读法（与板上 `M2_SEG_CYC` 同构，链式）**：`ta` 一次读打开 c=0 的 w；每路 `t1`（w 关/ana 开）、`t2`（ana 关/syn 开）、`t3`（syn 关 = 下一路 w 开）；每帧 beam 括号内 25 次读，外加 beam 自身 2 次。

**热身**：前 4 帧照跑（它们是 CRC 流的一部分、也填跨帧历史），只不进 last/max/min 统计（与 `F7_WARM`/`H1_WARM` 纪律一致）。与 F7 的差别：F7 只量 1 个稳态帧，本探针扫 1020 帧 → max/min 同时给出该口径的抖动带。

**统计外的工作**：子带 CRC 更新、统计更新、内层计数捕获，全部在外层括号**之后**。analyze 直接写进每通道的 staging 缓冲 `s_s7_sb[8][120]`（sb0|sb1|sb2|sb3 连续），synthesize 从同处读，括号内无 memcpy。

## 2. bench 工程接线（测试员/CTO 操作；不直接改 tracked 文件）

1. **source list** 加 `sprint7/dsp/probe/s7_wallclock_probe.c`（与 `fira_regression.c`、`h1_wcet_measure.c` 同一 FIRA build；core-only build 不加）。
2. **include path** 加 `sprint7/dsp/probe`（绝对路径，同 IMPORT_GUIDE R52 教训：`${repo}` 不是 CCES 变量）。
3. **`bench_main.c` 应用补丁** `bench_main_s7.diff`（extern 块 + F7 之后一行调用；补丁基线 md5 见 §0）。补丁文本：

```diff
--- a/sprint4/dsp/core_only/bench/bench_main.c
+++ b/sprint4/dsp/core_only/bench/bench_main.c
@@ -104,6 +104,10 @@
 extern volatile int      g_h2_fg_dma_loads, g_h2_fg_isr_fires, g_h2_valid;
 volatile int g_h2_done = -99;
 volatile int g_fira_f7_done = -99;              /* F7 measure ran: 1=on-board w/ FIRA / 0=desktop no-FIRA / -99 not-run */
+/* S7 B6.3 (WO-S7-B6.3): bench wall-clock split probe (defined in sprint7/dsp/probe/s7_wallclock_probe.c;
+ *   readouts g_s7_* declared in sprint7/dsp/probe/s7_wallclock_probe.h -> add that dir to the include path). */
+#include "s7_wallclock_probe.h"
+volatile int g_s7_done = -99;                   /* S7 probe ran: 1=on-board w/ FIRA / 0=desktop no-FIRA / -99 not-run */
 #endif
 
 /* ---- target CCNT read (true CCLK cycles) ----
@@ -239,6 +243,17 @@
      *   g_f7_cyc_8ch_fira / g_f7_cyc_8ch_core / g_f7_cyc_1ch_fira / g_f7_cyc_analyze_fira / g_f7_cyc_synth_fira
      *   -> off-board: margin vs >=10x + FIRA-vs-core ratio, ALL [L4/to-verify] until CTO rules R14 closed. */
 
+    /* ---- S7 B6.3 (WO-S7-B6.3): wall-clock split probe -- SAME caliber as the F7 span above (8ch weight ->
+     *   fira_tfb_analyze -> fira_tfb_synthesize, main context, FIRA busy-wait inside), but sweeps ALL frames and
+     *   splits each frame into w / ana / syn (sum over 8 ch) with last/max/min. Own setup/state/buffers AFTER F7
+     *   -> does NOT perturb the F4/F5/F7 PASS paths. RAW counters only (C9). FG: g_s7_fg_pass_all MUST read 1
+     *   (all 8 F5 anchors) or the cycle numbers are NOT to be used. FREE-RUN: read g_s7_* at idle only. ---- */
+    g_s7_done = s7_wallclock_probe();
+    /* breakpoint at idle: g_s7_valid(==1) / g_s7_fg_pass_all(==1) / g_s7_core_selfcheck_all(==1) / g_s7_frames /
+     *   g_s7_beam_cyc_last/max/min (compare g_f7_cyc_8ch_fira) / g_s7_seg_w_cyc_* / g_s7_seg_ana_cyc_* /
+     *   g_s7_seg_syn_cyc_* / g_s7_seg_sum_last / g_s7_probe_ovh_last / g_s7_ccnt_read_cyc /
+     *   (S7_PROBE_INNER build only) g_s7_inner_valid + g_s7_in_task|spin|flush|post|mem|core_cyc_last/max/min */
+
     /* ---- H1 (WO-S5-H1): focusing-increment same-build A/B + WCET cold/warm/max. Runs AFTER F7 with
      *   its OWN setup/state/buffers -> does NOT perturb F4/F5/F7 PASS paths. RAW counters only (C9).
      *   FREE-RUN: read g_h1_* at idle only (no mid-loop breakpoints). ---- */
```

   桌面已验：打补丁后的 `bench_main.c` 副本在 guard 配置下 `gcc -fsyntax-only` 通过（仅原有 `void main` 警告）[L2]；该检查的 `-I` 需含 `sprint6/dsp/audio/guard_stub_inc`（提供 `adi_initialize.h`）与 `sprint5/dsp/harness/guard_stub_inc`，再加四个 sprint4 目录与本目录。
4. **可选宏**（Defined symbols）：
   - `S7_PROBE_FA_BLOCK1`：把 `s_s7_fa`（8 个 `FiraChannelState`，~18 KB）钉到 `seg_l1_block1`，镜像板上 `s_m2_fa` 的 pin（`m1_loopback_tdm.c:218-219`）。**默认不加** = 与 F7 的 `f7_fa[]` 同放置类（463,273 锚的放置）。两种各跑一次可 A/B 放置假设（排查表 #3）。
   - `S7_PROBE_INNER`：仅当按 §4 用副本替换冻结件时加。**CTO 2026-09-03 裁定（DEC-S7-RULINGS-02）：本轮不必做、保持默认关；对照 build 后差距仍无法归因时另行申请。**
   - `S7_PROBE_SYN_FG`：合成侧对照旗（§6c；+≈18 KB 静态，括号外每帧 8 次核合成）。**CTO 2026-09-03 裁定：不必做，保持默认关**（DEC-S7-RULINGS-03；仅当板上四段占比与 bench 四段占比在合成段出现不可归因分歧时再申请）。
   - `seg_l1_block1` 这个 section 名在 `m1_app.ldf` 与 ADI EE408 `app.ldf` 里都有，但 bench 工程的 `.ldf` 不在库内 → 它在 bench 里是否存在 [L4]，首编即知；不存在则不要加 `S7_PROBE_FA_BLOCK1`。
   - **绝不**在目标 build 里定义 `S7_PROBE_HOST_FORCE`（那是桌面负控制，会绕过 `fira_tree_setup` 失败门）。
5. **内存**：新增静态 ≈ 18.3 KB（`s_s7_fa`）+ 2.3 KB（`s_s7_ca`）+ 3.8 KB（`s_s7_sb`）+ 2.3 KB（`s_s7_out[8][64]` 等），合计 ≈ 26.4 KB。bench 工程曾因 256 KB chirp 副本 li1040 溢出（`fira_regression.c:60-64`），本探针**不**再 include `chirp_input.h`，走 `bench_chirp_input()` 单副本。若链接仍报 li1040：先加 `S7_PROBE_FA_BLOCK1`（把最大的 18 KB 挪去 Block 1），再报回，**不要缩算法**。
6. 运行顺序：F2/F3 → F4 → F5 → F7 → **S7 probe** → H1 → H2 → idle。探针自带 setup/teardown，不碰 F4/F5/F7 的状态数组。

## 3. 读数清单与回填模板（**全部留空，测试员回填**）

上板前提（同 F7 纪律）：FREE-RUN，只在 idle `while(1)` 读；测量循环内**禁断点**。先读 FG，FG 不绿则 cycle 一律作废。

| 符号 | 期望 | 回填 |
|---|---|---|
| `g_s7_done` / `g_s7_valid` | **1 / 1**（板上真 FIRA） | ______ / ______ |
| `g_s7_setup_rc` | **0** | ______ |
| `g_s7_core_selfcheck_all` | **1**（正控制：核链复现八锚；桌面已 8/8 PASS） | ______ |
| `g_s7_fg_pass_all` | **1**（八锚全中 = **analyze 段**量的是真链；`g_s7_fg_anchor_pass[0..7]` 全 1；**syn 段无锚**，见 §6c） | ______ |
| `g_s7_crc_fira[0..7]` | == `{0x8E807729, 0xB2F1E13F, 0x7B109C71, 0xD7BD23E7, 0xA000D606, 0x2403E085, 0xB88D91B5, 0x2E0D8C6E}` | 抄 8 值 |
| `g_s7_frames_total` / `g_s7_frames` | **1024 / 1020** | ______ / ______ |
| `g_s7_cclk_hz` / `g_s7_cclk_rc` | 1,000,000,000 / 0 | ______ / ______ |
| `g_s7_ccnt_read_cyc` | 抄值（一次读的成本，扣扰动用） | ______ |
| `g_s7_beam_cyc_last / max / min` | 抄值；与同 build 的 `g_f7_cyc_8ch_fira` 对照（同口径，应同量级；本文件不写数） | ______ / ______ / ______ |
| `g_s7_seg_w_cyc_last / max / min` | 抄值 | ______ / ______ / ______ |
| `g_s7_seg_ana_cyc_last / max / min` | 抄值 | ______ / ______ / ______ |
| `g_s7_seg_syn_cyc_last / max / min` | 抄值 | ______ / ______ / ______ |
| `g_s7_seg_sum_last` / `g_s7_probe_ovh_last` | sum + ovh == beam_last（同帧恒等）；ovh 应 ≈ 1–2 × `g_s7_ccnt_read_cyc` + 循环进出（24 次读已在三段内，每段 8 次；ovh 远大于此 = 括号有误） | ______ / ______ |
| `g_s7_reads_per_frame` | **25** | ______ |
| `g_fira_f4_pass` / `g_f5_pass_all`（同 build 同次跑，**每臂都抄**：探针新增 ≈25 KB 静态改变链接布局，这两旗是 IO2 布局 canary） | **1 / 1** | ______ / ______ |
| （`S7_PROBE_SYN_FG` build）`g_s7_syn_fg_built` / `g_s7_syn_fg_all` / `g_s7_syn_fg[0..7]` | 1 / **1** / 全 1（-2 = FG-A 未过不评估；0 = 记录上报，不默认作废 w/ana） | ______ / ______ / ______ |
| `g_s7_fa_block1` | 0（默认）/ 1（加了 `S7_PROBE_FA_BLOCK1`） | ______ |
| `g_f7_cyc_8ch_fira`（同 build 同次跑） | 抄值（对照锚） | ______ |
| （副本 build）`g_s7_inner_valid` | 1 | ______ |
| （副本 build）`g_s7_in_task/spin/flush/post/mem/core_cyc_last` | 抄 6 值；六项之和 + 剩余 ≈ ana_last + syn_last | ______ ×6 |
| （副本 build）`g_s7_in_reads_last` | 抄值（扰动 = 该值 × `g_s7_ccnt_read_cyc`） | ______ |
| （副本 build）`g_fira_f4_pass` / `g_f5_pass_all` | **1 / 1**（副本忠实性 FG，在上面每臂 canary 之外单列） | ______ / ______ |

## 4. 诊断副本 `fira_tree_probe.c` 登记（同源纪律，A 批次松散副本清理后的新增副本须登记）

| 项 | 值 |
|---|---|
| 复制自 | `sprint4/dsp/fira/fira_tree.c`（冻结件；M2 只 call 不 edit，`m1_loopback_tdm.c:62-69`） |
| 复制时冻结件 md5 | `7616c41102946c357e9c70fafcd51da3` |
| 副本 md5 | `4e94a6ede8e05915449ff2ad45884401` |
| 生成方式 | `tools/make_fira_tree_probe.py`：**只插入、不改动**；每条插入行含记号 `S7P`；`grep -v S7P` 去掉插入行后与冻结件**逐字节相同**（守卫检查 (F) 实跑 PASS，见 §5） |
| 性质 | **诊断专用**；**不进产品 build**；**随冻结件变动同步（重跑生成器）或删除**；守卫检查 (H) 在冻结件 md5 漂移时 FAIL |
| 用法 | bench 工程：`fira_tree.c` **Exclude from Build**，source list 加 `fira_tree_probe.c`，Defined symbols 加 `S7_PROBE_INNER`。**二者不可同时链接**（同名符号） |
| 内括号（`S7_PROBE_INNER` 时生效，每段 `fira_run_segment` / `fira_run_segment_stateful`） | `task` = CreateTask + FixedPointEnable + QueueTask（调用返回）；`spin` = QueueTask 返回 → `g_FIRTaskDoneCount` 看到 DONE（`fira_tree.c:481` 忙等，含 FIRA 硬件时间 + FIRI 中断往返 + 驱动 ISR + 回调）；`flush` = `flush_data_buffer`；`post` = `fira_postscale`；`mem` = 历史前置 / 零填充 / 历史更新的 memcpy/memmove；`core` = analyze 的细节相减循环 + synthesize 的 sat_add 循环 |
| 未罩（残余） | `fira_make_channel` 结构体填充、函数调用/返回、`ch.hist` 索引、每次 CCNT 读自身 → 残余 = (ana+syn) − 六项之和 |
| **FG（副本忠实性）** | 用副本链接时：F4 锚 `0x2E0D8C6E`（`g_fira_f4_pass=1`）、F5 八锚（`g_f5_pass_all=1`）、探针 `g_s7_fg_pass_all=1` **必须仍逐位过**。任一不过 = 副本失真或括号扰动了数据路径 → 副本作废 |
| 扰动 | 每通道 9 段 × 9 次读 + core 8 次 = 89 次，每帧 712 次 + 探针自身 27 次（25 链式 + beam 2 次）≈ 739 次 `bench_cyc_target()`/帧；量级 = 739 × `g_s7_ccnt_read_cyc`（板上读到后算，本文件不估数）。**副本 build 的 beam/ana/syn 数含此扰动，不作新基线；新基线只认无副本 build** |

为什么需要副本（而不只三段拆分）：三段只能区分"FIRA 段（ana/syn）"与"纯核段（w）"，不能区分 ana 里的**忙等**（-O 无关、放置/中断相关）与**核侧 postscale/memcpy**（-O 强相关）。排查表 #4/#5/#7 的证实/排除靠副本的 spin/post/mem 三项。

## 5. 守卫检查实跑结果（2026-09-02 首跑、2026-09-03 复跑与 critic-E 修正后第三跑，本机 gcc 11.4.0，[L2 桌面语法]）

`./run_s7_probe_guard_check.sh` → **overall: PASS**（exit 0）：

| 项 | 内容 | 结果 |
|---|---|---|
| (A) | `s7_wallclock_probe.c` guarded（`-DFIRA_USE_REAL_ADI_FIR_HEADER -DTARGET_SHARC`，sprint5 mock BSP） | PASS |
| (B) | 同上 + `-DS7_PROBE_INNER -DS7_PROBE_FA_BLOCK1 -DS7_PROBE_SYN_FG` | PASS（gcc 对 `#pragma section` 报 unknown pragma 提示，属 CCES 真 pragma，未提升） |
| (C) | `fira_tree_probe.c` guarded + `S7_PROBE_INNER`（本目录 Legacy 头转录 stub） | PASS（1 条 unused-parameter 警告来自冻结原文 `fira_make_channel(kind)`，非本次插入） |
| (D) | `fira_tree_probe.c` guarded、`S7_PROBE_INNER` 未定义（记号行惰性） | PASS |
| (E) | `fira_tree_probe.c` 桌面路径 + `S7_PROBE_INNER` | PASS |
| (F) | 逐字校验：去掉 `S7P` 行后 md5 == 冻结件 `7616c411…` | PASS |
| (G) | 新源文件 ASCII-only | PASS |
| (H) | 冻结 `fira_tree.c` md5 未漂移 | PASS |

`-Werror` 提升与 sprint5 一致：implicit-function-declaration / int-conversion / incompatible-pointer-types。

## 6. 桌面 host 编译 + 运行（`./run_s7_probe_host.sh`，[L2 宿主管路；cycle 数无意义]）

四个 run 全部 "host expectation MET"，**overall PASS**（2026-09-02 首跑三 run、2026-09-03 复跑，critic-E 修正后第三跑加 H4，结果一致；副本 md5 `4e94a6ede8e05915449ff2ad45884401`、冻结件 md5 `7616c41102946c357e9c70fafcd51da3` 复核一致）：

| run | 链接 | 结果（摘） |
|---|---|---|
| H1 | 冻结 `fira_tree.c`，不强制 | `setup_rc=-1 valid=0 frames_total=0`；核正控制 **8/8 PASS**；FIRA 锚 `fg_pass_all=0`（门把探针拦住，诚实 0） |
| H2 | 冻结 `fira_tree.c` + `-DS7_PROBE_HOST_FORCE` | `frames_total=1024 frames=1020`；核正控制 **8/8 PASS**（`0x8E807729 … 0x2E0D8C6E` 逐位同）；FIRA 占位链（`fira_tree.c:711-719/754-768` memset 0）→ **八锚 0/8，预期的诚实 FAIL**（FG2 负控制：证明八锚判据不是常数、依赖真链） |
| H3 | 副本 `fira_tree_probe.c` + FORCE + `S7_PROBE_INNER` | 与 H2 逐值相同（副本**桌面路径** == 冻结件；目标路径的忠实性靠板上 F4/F5 锚）；`inner_valid=1`、内层计数全 0（内括号只在目标 FIRA 路径生效） |
| H4 | 冻结 `fira_tree.c` + FORCE + `S7_PROBE_SYN_FG` | `syn_fg_built=1`、`syn_fg_all=-2`（FG-A 未过 → 不评估；占位子带下两条合成路径平凡相等，故桌面**绝不**报 PASS） |

判读：核正控制 8/8 证明探针的 CRC 多项式/字节序、加权截断点、帧序与 `gen_f5_goldens.c` 同源；FIRA 占位 0/8 证明"八锚 PASS"只可能来自真 FIRA **analyze** 链。**synthesize 段无锚**（既有盲区，与 F4/F5/F7 相同）：syn 读数置信低一档，合成对照旗见 §6c。**上板时若 `g_s7_fg_pass_all=0` 而 `g_s7_core_selfcheck_all=1` → FIRA 链在探针调用序列下失真（不是探针 CRC 的问题），cycle 作废、先查链**。

## 6c. syn 侧对照旗（`S7_PROBE_SYN_FG`，F-2；**CTO 2026-09-03 裁定不必做、保持默认关**，DEC-S7-RULINGS-03）

八锚只覆盖 analyze；`fira_tfb_synthesize` 的 3 个 FIRA 段 rc 被冻结件 `(void)` 丢弃，失败/早返回会给偏短的 syn 读数而 FG-A 仍绿。对照旗：每帧括号**外**把同一组 FIRA 子带喂冻结核 `tfb_synthesize`（每通道 `TreeChannelState` 与 FIRA 合成历史锁步），两路合成输出各自流式 CRC → `g_s7_syn_fg[c]`/`g_s7_syn_fg_all`（1 同 / 0 异 / -2 = FG-A 未过不评估 / -99 未编入）。不等 → 记录上报，不默认作废 w/ana。代价 ≈18 KB 静态 + 括号外核合成时间 → 默认关（bench 内存紧，li1040 先例）。它不是锚：只证"FIRA 合成 == 核合成"，不证合成正确。

## 6b. 板上括号实现回执（s7-base，2026-09-02）

板上 `M2_SEG_CYC=1` 已落码：符号 `g_m2_seg_{w,ana,syn,tx}_cyc_last/_max` + 无条件 `g_m2_beam_cyc_min`；链式读法每帧 33 次 CCNT 读（4×8+1），全部落在 `g_m2_beam_cyc_*` 内 → SEG_CYC build 与非 SEG_CYC build 的 beam 数不可直接相减，两个 build 都读、离板比；`M2_SEG_CYC` 无 `M2_FIRA_INLOOP` 时 `#error`。板上 ana/syn 各自**含** FIRA DONE 忙等（冻结件内），compute vs 忙等只能靠本目录的副本内拆分（**CTO 2026-09-03 裁定不必做、保持默认关**，DEC-S7-RULINGS-02；对照 build 后仍无法归因时另行申请）。

## 7. 与板上三段的可比性（一句话版，全文见 `S7_B63_WALLCLOCK_GAP.md §2.3`）

同冻结 API、同帧长 64、同 8 通道、同 Q15×Q31>>15 权重、同跨帧状态结构、同主上下文忙等 → w/ana/syn 三段可逐段对比。**差异（明示）**：输入 = 冻结 chirp vs 活音频（定点 MAC 时间与数据无关，饱和分支在两边都不触发 [L3]）；bench 无 SPORT DMA、无 RX ISR、无 TX 交织段（板上 tx 段无 bench 对应项）；bench 一次跑 1024 帧后 idle，板上连续 750 fps；两工程的 build 配置/放置/驱动库变体可能不同（排查表 #1/#3/#8）。

## 8. 未做 / 限制

- 本机无 cc21k：以上全是 gcc [L2]；CCES 首编可能遇到 A2 头名漂移类问题（`<services/pwr/adi_pwr.h>` 与 F7 同一 include，已在板上过）。
- 探针不做 I-cache/D-cache 失效（21569 L1 不被数据 cache，`m1_loopback_tdm.c:34`；bench 放置见排查表 #3）。
- 探针 4 项 FG 的覆盖面：analyze 有锚（八锚）、synthesize 无锚（对照旗可选）——不把 `g_s7_fg_pass_all=1` 说成"整链已证"。
- 探针的 w 段用恒等通道→权重下标（八锚定义如此）；板上默认 build 同样恒等（`M2_CHMAP_FIX` 默认关）。
