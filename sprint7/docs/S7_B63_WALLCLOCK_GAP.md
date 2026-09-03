# S7 B6.3 — M2 波束墙钟 830,903 对 bench 463,273 的 1.79× 差距：拆解方案、对照实验与排查表

> **文档 ID**：WO-S7-B6.3（DEC-S7-IMPL-01 第 (1) 项；裁定 D1/D2，`sprint2/docs/decisions_log.md:1036-1052`）
> **作者**：dsp-algorithm teammate，2026-09-02 ｜ **状态**：设计 + 桌面验证完成，**板上数字全部待测试员回填**
> **口径**：全文用**墙钟**口径（D1：解冻条件按墙钟判；三口径互不可比纪律不变，`S7_DSP_ASSESSMENT.md §0.1`）。
> **铁则**：本文**不替测试员补任何板上数字**；所有回填格子留空；本文出现的既有数字均带 L 标与出处。
> **禁区**（本工单）：不改冻结件、不改 `.cproject`/`.project`、不改 `sprint6/dsp/audio/m1_cces_project/`（板上 TU 改动由 s7-base 按 §3 规格实现）。

---

## 0. 问题与本文交付

| 量 | 值 | L 标 / 出处 |
|---|---|---|
| M2 波束墙钟 `g_m2_beam_cyc_max`（06-16） | 830,903 cyc/帧 | [L1 墙钟，run 内最大值] DEC-S6-M2-BOARD-PASS-01（`decisions_log.md:1013`） |
| 同上（06-29 复测） | 829,218 | [L1] `deliverables/algorithm_validation/TEST1_WIRING_FINGERPRINT_FIELDLOG_20260629.md:24` |
| bench F7 8ch FIRA（main 上下文，含忙等，1 个稳态帧） | 463,273 | [L1 bench] `sprint4/dsp/fira/F7_CLOSING_RECORDS.md:154` |
| bench H2 base 8ch | 454,730 | [L1 bench] `S7_DSP_ASSESSMENT.md §0.2` |
| 差距 | 1.794× / 367,630 cyc | [L1-derived] `S7_DSP_ASSESSMENT.md §0.3` |
| 帧预算 / 1.5× 线 | 1,333,333 / 888,889 **（参考值，待实测重算）** | [L1-derived]（由 CCLK 1e9 [L1 F7 G6，bench 读回] 得出；M2 工程同频原为推断 [L3]。**CTO 2026-09-03：改由测试员读 CGU 寄存器实测、intake 脚本重算；实测回来前 B1 条件 0 未满足**，DEC-S7-RULINGS-03） |

两个括号**同口径**：都罩「每帧 8 通道 × (加权 → `fira_tfb_analyze` → `fira_tfb_synthesize`)」，都在 main 上下文，都含 `fira_tree.c:481` 的 FIRA DONE 忙等（板上 `m1_loopback_tdm.c` `m2_beam_poll` 的括号，审计版 :592-596；bench `fira_regression.c:611-619`）。所以 1.79× 不是「忙等没算」能解释的，而是**两个环境的差**。本文把这个差拆成可逐条证实/排除的项：

- §1 零成本假设（a）：`.cproject` 逐行核实 + 两条对照 build 路径 + 测试员操作与回填模板；
- §2 bench 三段拆分（b）：探针 `sprint7/dsp/probe/`（已桌面验证）；
- §3 板上三段括号规格（c）：交 s7-base 实现（符号、罩什么、宏门控、扰动估计）；
- §4 排查表（d）：优化等级之外的候选成因，每条给「用哪个读数证实/排除」；
- §5 runbook 增量（e）+ 回填模板；§6 回填后的判读逻辑（决策树，不预填）；§7 诚实声明。

**口径提醒（critic-C F-15，必须先读）**：CTO 定义的三段（加权乘法 / analyze / synthesize）是按**流水级**切的；FIRA DONE 忙等（`fira_tree.c:481`）在冻结件内、分布在 analyze 与 synthesize 两段各自的 6/3 个 FIRA 段里，所以**三段拆分本身拆不出「compute vs 忙等」**——它只能回答"差距落在哪一级、纯核段（w/tx）与 FIRA 段（ana/syn）是否同比例放大"。要拆 compute vs 忙等，只有 bench 侧的诊断副本内拆分（§2.1 `fira_tree_probe.c`，`S7_PROBE_INNER`）能做；**该内拆分 **CTO 2026-09-03 裁定不必做、保持默认关**（DEC-S7-RULINGS-02），对照 build 后差距仍无法归因时另行申请**（本文只交付设计与桌面验证，不假定它会上板）。

---

## 1. 零成本假设（a）：M2 工程当前 build 优化等级

### 1.1 `.cproject` 逐行核实（`sprint6/dsp/audio/m1_cces_project/.cproject`，只读，[L1 文件]）

| 项 | Debug 配置（当前上板用） | Release 配置 | 对墙钟的影响 |
|---|---|---|---|
| 编译器 `Enable optimization (-O)` | **`:39` 无 `value` 属性** → 取 CDT 工具定义的默认值 | `:153` `value="true"` | **核心变量**：只影响本工程编译的 C（`m1_loopback_tdm.c` 加权/交织循环、冻结 `fira_tree.c` 的 postscale/memcpy/零填充/细节相减、`tree_filterbank.c`），**不影响** FIRA 硬件时间、预编译驱动库 `libdrv`、中断往返 |
| `-Ov`（速度/体积） | 两配置都未出现 → 默认 | 同 | bench 用 `-O -Ov=100`（`sprint4/dsp/fira/FIRA_IMPL.md:72`）；路径 A 只勾 `-O`，`-Ov` 取默认（须在凭证截图里看到实际值） |
| 编译器 `-g` | `:40` 无 value（Debug 默认开） | `:154` `false` | 仅调试信息，不改代码生成 [L3]；**cc21k 下 `-g` 与 `-O` 同开是否限制优化未核 [L4]**——臂 A' 保留 `-g` 可能低估 `-O` 效应，臂 B（无 `-g`）可旁证 |
| 编译器 `-D` | `:44-47` `_DEBUG, CORE0, M1_TARGET_BOARD, TARGET_SHARC` | `:158-161` `NDEBUG, CORE0, M1_TARGET_BOARD, TARGET_SHARC` | `_DEBUG`/`NDEBUG` 只影响 `assert()`；波束路径无 assert [L3]；工程内链接的 ADI 驱动源（sport/twi/pdma/spu）用 `ADI_DEBUG` 而非 `_DEBUG` 门控 [L3]，且不在波束括号内 |
| 汇编器 `-g` / `-D` | `:26` 无 value；`:30-31` `_DEBUG, CORE0` | `:140` false；`:144-145` `NDEBUG, CORE0` | 无影响（无自写汇编） |
| 链接器 `-ip`（逐项映射） | `:57` `false` | `:171` `defaultValue="true"` | 改变放置 → 路径 B 的放置与路径 A 不同（多变量） |
| 链接器 `-e`（剔未用对象） | `:58` 无 value（默认） | `:172` `true` | 只影响体积/放置，不影响热路径时间 [L3] |
| **`Use Debug System libraries (-add-debug-libpaths)`** | `:59` 无 value（Debug 默认**开**） | `:173` `false` | 链接系统库/驱动库的 **debug 变体**。1B PASS map 里 `libdrv.dlb[adi_fir.doj]` 含 `.sASSERT.0..18` 字符串与 `ValidateTaskHandle/ValidateDeviceHandle` 函数（`board_artifacts/M1_Loopback_M2build_1B_PASS_20260616.map.xml`，[L1 map]）→ FIR 驱动很可能是带断言的 debug 变体 [L3 推断]，每帧 72×(CreateTask+FixedPointEnable+QueueTask)+72 次 ISR 都走它。**路径 A 保持此项不变**（单变量），路径 B 同时变它 |
| 链接器 `-MD` | `:63-64` `DEBUG, CORE0` | `:177-178` `RELEASE, CORE0` | LDF 宏；`m1_app.ldf` 里未见依赖 DEBUG/RELEASE 的分支 [L3，未逐行核] |
| 自定义 LDF | `:66` `m1_app.ldf` | `:180` 同 | 同一 LDF |
| 构建产物 | `:20` `.ldr`（targetTool = loader，`:22`） | `:134` `.exe`（dxe；targetTool = linker，`:136`） | Debug 多一步 loader（R52：常在 loader 步报错但 `.dxe` 已生成）；Release 无 loader 步 |
| loader kernel | `:80` `_spi.dxe`（硬编码 2.11.1 路径）、`:81` boot=spimaster | `:194` `_prom.dxe` | 与运行无关（仿真器加载 `.dxe`） |
| 驱动版本宏 | `:7-10` sport 1.0 / twi 2.0 / spu 1.0 / pdma 1.0 | 同 | 同 |

**结论 [L1 文件 + L3 语义]**：两配置的实质差别是四项：`-O`（默认关 vs 开）、`-g`、`_DEBUG/NDEBUG`、Debug 系统库 + `-ip`/`-e`。其中只有 **`-O`** 与 **Debug 系统库（驱动变体）** 可能显著改变波束括号内的时间。`.cproject:39` "无 value = 关" 是按 CDT 语义推断 [L3]，**L1 坐实靠测试员的 GUI 复选框截图 + Console 编译行**（§1.3 凭证）。

bench 侧对照：bench 工程（`bench_core_only`，从 ADI `FIR_Multi_Channel_Processing` 例程派生）**在 Debug Configuration 下带 `-O -Ov=100`**（`FIRA_IMPL.md:72`，[L1 文档记录，非本机可核]）。因此 **463,273 是 `-O` 下的数，830,903 极可能是无 `-O` 的数**——这就是零成本假设的全部依据；它是否成立、成立多少，只能由 §1.2 的对照 build 回答。

### 1.2 两条对照 build 路径（主路径 = A）

| 路径 | 做法 | 变量数 | 用途 |
|---|---|---|---|
| **A（主）** | **保持 Debug 配置**，只在 GUI 里勾上 `Enable optimization (-O)`；其它一律不动（宏、LDF、Debug 系统库、`-g` 都保持） | **1**（优化等级） | 直接证伪/证实"零成本假设"；A 与基线的差 = 纯 `-O` 效应 |
| **B（旁证）** | 切到 **Release** 配置（`-O` + `NDEBUG` + 无 `-g` + 无 Debug 系统库 + `-ip` + `-e`），并把 M2 宏重新加到 Release 的 Defined symbols | 多变量 | B 与 A 的差 = Debug 系统库/驱动变体 + 放置（`-ip`）等的合并效应，只作旁证；**不用 B 定新基线** |

两条路径都**改变二进制** → 每条都必须重跑 M2 板门（§1.5）。

**两条硬规则（critic-C F-15 / CTO 硬约束"不动 `.cproject`"）**：
1. 对照 build **不需要手工编辑 `.cproject`**：Release 配置本来就在（`.cproject:118-153`，`-O` value=true），路径 A 只是 GUI 里勾一个复选框——但 **CDT 在 Apply 时就会把它写回 `.cproject:39`**（切配置同样会重写 `.cproject`/`.project`）。所以每臂 build 后测试员必须 `git status`；只要看到这两个文件有变动，一律
   ```
   git checkout -- sprint6/dsp/audio/m1_cces_project/.cproject sprint6/dsp/audio/m1_cces_project/.project
   ```
   然后 **Refresh / 重开工程**（否则 CDT 内存里的设置会再次写回）；**不入库、不 commit**（源码级改动只允许 s7-base 的 TU；工程文件零改动）。
2. 对照 build 是**另一份二进制**：其 `beam_cyc` 读数必须与 **build 指纹一起回填**（Defined symbols 截图 + Console 编译行含/不含 `-O` + `g_m2_*_built` 指纹值），**不替代** Debug 基线 830,903 [L1]（该基线仍是当前产品配置的墙钟）。若日后 CTO 决定改产品配置，须 M2 板门 + 八锚 + 耳听全套重跑后另立 DEC 行。

### 1.3 测试员 GUI 操作（逐步；S-B 基座部分见 `sprint7/docs/S7_TESTER_RUNBOOK_SB.md`，本节不重复）

**共同前提**：S-B 基座 build 已 PASS（`M2_SELFTEST` 八锚、6 宏指纹、板门全绿），且 s7-base 已把 §3 的括号与 `g_m2_beam_cyc_min` 放进 TU。`M2_SEG_CYC` 的取值按 §5 各臂规定。

**路径 A（Debug + `-O`）**：
1. Project Explorer 右键 `M1_Loopback` → Properties → C/C++ Build → Settings → Tool Settings → **SHARC C/C++ Compiler → General**（或 Optimization 页，随 CCES 版本）→ 勾选 **Enable optimization (-O)**。**只勾这一项**；`Generate debug information (-g)` 保持勾；Preprocessor 的 Defined symbols 保持 S-B 基座的那套（`M2_FIRA_INLOOP=1`、`FIRA_USE_REAL_ADI_FIR_HEADER` 及 §5 规定的 `M2_SEG_CYC`）。
2. 若该页有 **Optimization for speed vs size (-Ov)** 数值框：**不改**（记下它显示的值，抄进回填表）。
3. Apply and Close → **Project → Clean** → **Build Project**（必须 Clean 后全量重编；R52：不 Rebuild 直接 Load = 烧旧程序）。
4. **凭证（三张截图，必交）**：① 该 Tool Settings 页（看得到 `-O` 复选框状态与 `-Ov`）；② Console 里 `m1_loopback_tdm.c` **和** `fira_tree.c` 的编译命令行各一条（命令行里是否出现 `-O`/`-Ov` 就是优化等级的 L1 凭证；两条都要，因为冻结源是链接进来的资源，要证明它也被 `-O` 编了）；③ Defined symbols 页。
5. **Load `Debug/M1_Loopback.dxe`**（不是 `.ldr`；loader 步报错而 `.dxe` 已生成时照 IMPORT_GUIDE F7 忽略）。
6. 功放断电或音量最小 → 放立体声音乐 → **不间断 Run ≥ 10 秒** → Suspend → idle 读 §1.4 全表 → 若板门绿且 `out_max_abs` 未顶满幅 → 功放上电最小音量 → **重新 Load 重跑** → 耳听一行话。
7. **导出 .map** 改名 `map_B63_armA_<日期>`；发回。
8. **复原**：把 `Enable optimization (-O)` **取消勾选**，Apply；下一臂前 Clean。
9. **`git status`**：若 `.cproject`/`.project` 显示已修改 → `git checkout -- sprint6/dsp/audio/m1_cces_project/.cproject sprint6/dsp/audio/m1_cces_project/.project`（§1.2 硬规则 1）。

**路径 B（Release）**：
1. Properties → C/C++ Build → 顶部 **Configuration** 下拉切到 **Release**。
2. 在 Release 的 SHARC C/C++ Compiler → Preprocessor → Defined symbols 里**重新加** S-B 基座的那套宏（Release 的宏列表与 Debug 独立，`.cproject:158-161` 只有四个默认宏）；**Include 目录同样是按配置独立的**（`.cproject:165` Release 只有 `system`）→ 在 Release 的 Includes 里重新加四个绝对路径 `sprint4/dsp/fira`、`sprint4/dsp/core_only/src`、`sprint4/dsp/core_only/include`、`sprint4/dsp/core_only/bench`（s7-base runbook 同表）；链接的三个冻结源（`fira_tree.c`/`tree_filterbank.c`/`tfb_8ch.c`）是工程级 linkedResources，应已在；缺失按 IMPORT_GUIDE M2 步骤 2 补。
3. Build 前先看 **SHARC Linker → General**：`Use Debug System libraries` 应为**未勾**（`.cproject:173`），`Individually map (-ip)` 为勾（`:171`）——**抄状态，不改**。
4. Clean → Build（产物在 `Release/M1_Loopback.dxe`；Release 无 loader 步）。凭证同 A 的三张 + Linker 页一张。
5. Load `Release/M1_Loopback.dxe` → 同 A 的 6–7。导出 .map 改名 `map_B63_armB_<日期>`。
6. **复原**：Configuration 切回 Debug；Release 下加的宏可留（Release 不再 build 即无害），但要在回填表注明。
7. **`git status`**：切配置最容易触发 CDT 重写工程文件 → 若 `.cproject`/`.project` 有变动，一律 `git checkout -- sprint6/dsp/audio/m1_cces_project/.cproject sprint6/dsp/audio/m1_cces_project/.project`，不入库。

### 1.4 每臂读数（板上符号；由 s7-base 实现，含义见 §3）

| 组 | 符号 | 期望 | 说明 |
|---|---|---|---|
| 指纹 | `g_m2_fira_inloop` / `g_m2_selftest_built` / **`g_m2_seg_w_cyc_last` 符号可见性**（`M2_SEG_CYC` 无专用指纹，以该符号存在与否判该臂是否带括号，见 S-B runbook 表 A） | 1 / 按臂 / 按臂 | **每臂第一个读**，证明读数属于哪个 build |
| 板门 | `g_m2_setup_rc` / `g_m2_valid` / `g_m2_fg_beam_live` / `g_m1_fg_stream_live` | 0 / 1 / 1 / 1 | DEC-S6-M2-BOARD-PASS-01 同表 |
| 板门 | `g_m1_rx_block_count` ≈ `g_m2_poll_count`；`g_m2_overrun_count` | 增长、相等；≈0 | rx=poll、无丢帧 |
| 数值门 | `M2_SELFTEST` 八锚 `g_m2_selftest_pass[0..7]`（s7-base 命名为准） | 全 1 | **bit-exact 与优化等级无关**的实证（前提无 UB） |
| 幅度 | `g_m2_out_max_abs` / `g_m1_max_abs_sample` | 未顶 0x7FFFFFFF / 抄 | R57 判别式 |
| **墙钟** | `g_m2_beam_cyc_last` / `g_m2_beam_cyc_max` / **`g_m2_beam_cyc_min`** | 抄三值 | 本工单主读数；min = 稳态下界，max = run 内最大 |
| io | `g_m1_cb_cyc_max` | 抄 | M2 口径 = io+握手（排查表 #9 用） |
| 三段（`M2_SEG_CYC=1` 臂） | `g_m2_seg_w_cyc_last/_max`、`g_m2_seg_ana_cyc_last/_max`、`g_m2_seg_syn_cyc_last/_max`、`g_m2_seg_tx_cyc_last/_max`（+ 若实现了 `_min`） | 抄 | 每帧 8 通道之和 |
| 一致性 | w+ana+syn+tx（同一帧的 `_last`）vs `g_m2_beam_cyc_last` | 和 ≤ beam | 差 = 循环开销 + CCNT 读扰动（§3.5） |
| 凭证 | Tool Settings 截图 / Console 两条编译行 / Defined symbols / `.map` / 听感一行话 | 全交 | 缺一臂作废 |

### 1.5 诚实标注：改优化等级 = 改二进制

- 每条路径都产生**新二进制** → M2 板门（`fira_inloop=1 / setup_rc=0 / valid=1 / fg_beam_live=1 / overrun≈0 / rx≈poll`）**每臂重跑**，不得沿用 06-16 的 PASS。
- **bit-exact**：定点整数算术的结果与优化等级无关**的前提是代码无未定义行为**；这一条**不靠推理**，靠 `M2_SELFTEST` 八锚在每臂逐位 PASS（s7-base 实现；selftest 上板前只有板门 + 耳听两道）。桌面 gcc 的 `-O0`/`-O2` 对照可作旁证（s7-base 的 host harness），但 cc21k 的代码生成只有板上能证。
- `-O` 可能改变**栈用量与放置**（内联/寄存器分配）：每臂 `.map` 必导出；核对 `s_m1_rx_buf`/`s_m1_tx_buf`/`s_m2_fa` 仍在 Block 1（≥0x2c0000）、`s_seg_in`/`s_seg_out3`/`s_taskMem` 仍在 L1（0x24xxxx，非 `mem_L2_bw`）（IMPORT_GUIDE M2 步骤 3 / R57）。
- 若某臂板门不绿或八锚不全过：**该臂的墙钟读数作废**，原样发回，不猜不改（F4 板纪律）。
- 对照臂的读数**带指纹回填、不替代 830,903 [L1] 基线**（§1.2 硬规则 2）；它们只回答"差距里有多少是优化等级"，产品配置改不改是 CTO 的另一个决策。

### 1.6 回填模板（§1；**全部留空**）

| 臂 | 配置 | `-O` 凭证（截图编号） | `-Ov` 显示值 | beam_cyc min / last / max | 板门 6 项 | 八锚 | 听感 | .map 文件名 |
|---|---|---|---|---|---|---|---|---|
| 0 | Debug 现状（S-B 基座 build，`M2_SEG_CYC=0`） | ____ | ____ | ____ / ____ / ____ | ____ | ____ | ____ | ____ |
| A' | Debug + `-O`，`M2_SEG_CYC=0` | ____ | ____ | ____ / ____ / ____ | ____ | ____ | ____ | ____ |
| B | Release（含 `-O`），`M2_SEG_CYC=0` | ____ | ____ | ____ / ____ / ____ | ____ | ____ | ____ | ____ |

---

## 2. bench 三段拆分（b）：探针 `sprint7/dsp/probe/`

### 2.1 交付物（已桌面验证，详见 `sprint7/dsp/probe/README.md`）

| 文件 | 内容 |
|---|---|
| `s7_wallclock_probe.c/.h` | 新 bench TU：与 F5/F7/M2 同调用序列跑冻结 `CHIRP_INPUT` 全部 1024 帧，每帧三段括号（w / ana / syn，各为 8 通道之和）+ 外层 beam 括号（= F7 口径）；last/max/min；前 4 帧热身不进统计；读法与板上同构（链式，每帧 1+3×8 = 25 次读在 beam 括号内）；FG = 同一次跑的每通道 **analyze** 子带 CRC 逐位等于 `dolph_f5_goldens.h` 八锚（`g_s7_fg_anchor_pass[8]`、`g_s7_fg_pass_all`：证 **analyze 段**量的是真链）+ 核链正控制（`g_s7_core_selfcheck_all`）；**synthesize 段无锚**（既有盲区，F4/F5 只比子带、F7 只计时，463,273 同样如此），以 FG2（占位版必 FAIL）与副本 F4/F5 锚为据，读数置信低一档；可选 `S7_PROBE_SYN_FG` 合成对照旗见 §2.5（**CTO 2026-09-03 裁定不必做、保持默认关**，DEC-S7-RULINGS-03） |
| `fira_tree_probe.c`（**CTO 2026-09-03 裁定：不必做，保持默认关；对照 build 后差距仍无法归因时另行申请**，DEC-S7-RULINGS-02） | 冻结 `fira_tree.c`（md5 `7616c41102946c357e9c70fafcd51da3`）的**逐字副本 + 内括号**（`S7_PROBE_INNER` 门控；task / spin / flush / postscale / mem / core 六项），生成器 `tools/make_fira_tree_probe.py`，README §4 登记（复制自、md5、诊断专用、随冻结件变动同步或删除、不进产品 build、FG = 副本链接时 F4 锚 `0x2E0D8C6E` 与 F5 八锚仍逐位过）。这是唯一能把 ana/syn 里的 **FIRA DONE 忙等** 与核侧工作分开的手段（三段拆分做不到，见 §0 口径提醒）；已桌面验证；按 DEC-S7-RULINGS-02 不上 bench |
| `run_s7_probe_guard_check.sh` | 仿 `sprint5/dsp/harness/run_guard_check.sh`：`gcc -fsyntax-only -DFIRA_USE_REAL_ADI_FIR_HEADER -DTARGET_SHARC` + mock BSP，8 项 (A)–(H) **实跑全 PASS**（含副本逐字校验、ASCII、冻结 md5 守卫） |
| `run_s7_probe_host.sh` | 桌面 gcc 编译 + 运行四种链接：核正控制 **8/8 PASS**，FIRA 占位链 **0/8 = 预期的诚实 FAIL**（FG2 负控制），副本链接结果与冻结件逐值相同（**桌面路径**；目标路径的副本忠实性靠板上 F4/F5 锚），`S7_PROBE_SYN_FG` 在桌面报 -2（不评估，非 PASS） |
| `bench_main_s7.diff` | bench 接线补丁**文本**（extern 块 + F7 之后一行调用），不直接改 `bench_main.c`，由 CTO/测试员应用 |

### 2.2 括号定义（bench）

| 读数 | 罩什么 | 不罩什么 |
|---|---|---|
| `g_s7_seg_w_cyc_*` | 64 样本 `(w_q15·x_q31)>>15` 循环（`f5_apply_w` 语义，`fira_regression.c:260-263`）；c>0 时含链式读法带来的循环增量 | 权重表读取以外的一切 |
| `g_s7_seg_ana_cyc_*` | `fira_tfb_analyze(&fa[c], xw, 64, sb0..3)` 一次调用 | — |
| `g_s7_seg_syn_cyc_*` | `fira_tfb_synthesize(&fa[c], sb0..3, 64, out)` 一次调用 | — |
| `g_s7_beam_cyc_*` | 整个 8 通道循环（`fira_regression.c:611-619` 同口径） | CRC 更新、统计更新、内层捕获（全在括号后） |
| `g_s7_probe_ovh_last` | beam − (w+ana+syn) 同帧 | = 链首 1 次读 + 循环进出（≈1–2 次读的量级）；**不是 24 次**——24 次内层读的成本分摊在三段内（每段 8 次） |
| `g_s7_reads_per_frame` | beam 括号内的 CCNT 读次数 = 1 + 3×8 = **25**（链式：段 CLOSE = 下段 OPEN；c 的 syn CLOSE = c+1 的 w OPEN） | 扣除 = 25 × `g_s7_ccnt_read_cyc`；板上同构为 1 + 4×8 = 33 |
| `g_s7_ccnt_read_cyc` | 背靠背两次读之差 = 一次 `bench_cyc_target()` 的成本 | 扣扰动用 |
| 副本内层 `g_s7_in_{task,spin,flush,post,mem,core}_cyc_*` | task = CreateTask+FixedPointEnable+QueueTask；spin = QueueTask 返回 → DONE（`fira_tree.c:481`）；flush = `flush_data_buffer`；post = `fira_postscale`；mem = 历史前置/零填充/历史更新；core = 细节相减 + sat_add 循环 | `fira_make_channel` 填充、调用/返回、CCNT 读自身 = 残余 |

### 2.3 为什么 bench 三段与板上三段可逐段对比

**相同**：① 同一冻结 API 与调用序列（`fira_tree_setup` → `tfb_set_coeffs` → `fira_channel_init`×8；每帧每通道加权 → analyze → synthesize；`m1_loopback_tdm.c:788-811, 401-450` vs 探针）；② 同帧长 64、同 8 通道、同 Q15×Q31>>15 权重与截断点；③ 同 `FiraChannelState` 跨帧状态结构、同 9 段/通道（72 段/帧）；④ 同 main 上下文忙等（板上 `m2_beam_poll` 在 `m1_main.c:78` idle 循环；bench 在 `main` 顺序执行）；⑤ 同 `bench_cyc_target()`（`clock()` = CCLK，`m1_cyc.c` 逐字复制 `bench_main.c:118`）。

**不同（明示，判读时要记着）**：

| 差异 | 方向/量级 | L 标 |
|---|---|---|
| 输入：冻结 chirp vs 活音频 | 定点 MAC 时间与数据无关；`f_sat_*` 饱和分支两边都不触发（板上峰值 `out_max_abs=0x44885300` 未顶满幅 [L1]，chirp 0.289 FS 不饱和 [L2 golden_ref.h]）→ 可忽略 | [L3] |
| bench 无 SPORT DMA、无 RX ISR | 板上每 1.333 ms 一次 RX-done ISR（`m1_sport_rx_callback` = 64 样本 FG 扫描 + 握手），约 62% 概率落在 beam 括号内 [L3]；量级用 `g_m1_cb_cyc_max` 读（排查表 #9） | [L3 + L1 读数] |
| 板上多一个 tx 段（TX 交织写 + FG 累计） | 64×8 次写 + 比较；bench 无对应项；板上 beam = w+ana+syn+tx+循环 | [L3] |
| bench 一次跑 1024 帧后 idle；板上连续 750 fps | bench 的 max/min 是 1020 帧内的抖动带；板上是 run 内（可到 10^5 帧）的 max | — |
| 两工程 build 配置 / 放置 / 驱动库变体可能不同 | 排查表 #1 / #3 / #8 | — |
| bench 权重下标恒等（八锚定义）；板上默认 build 也恒等（`M2_CHMAP_FIX` 默认关） | 一致 | [L1 源码] |

### 2.4 bench 侧读数与回填（**留空**；符号表见 README §3）

| 读数 | 无副本 build（主） | 副本 build（`S7_PROBE_INNER`） |
|---|---|---|
| `g_s7_fg_pass_all` / `g_s7_core_selfcheck_all` | ____ / ____（都须 1） | ____ / ____ |
| `g_f7_cyc_8ch_fira`（同次跑，对照锚） | ____ | ____ |
| `g_s7_beam_cyc` min / last / max | ____ / ____ / ____ | ____ / ____ / ____ |
| `g_s7_seg_w_cyc` min / last / max | ____ / ____ / ____ | ____ / ____ / ____ |
| `g_s7_seg_ana_cyc` min / last / max | ____ / ____ / ____ | ____ / ____ / ____ |
| `g_s7_seg_syn_cyc` min / last / max | ____ / ____ / ____ | ____ / ____ / ____ |
| `g_s7_probe_ovh_last` / `g_s7_ccnt_read_cyc` | ____ / ____ | ____ / ____ |
| `g_s7_in_task/spin/flush/post/mem/core_cyc_last` | — | ____ ×6 |
| `g_s7_in_reads_last` | — | ____ |
| `g_fira_f4_pass` / `g_f5_pass_all`（同 build 同次跑；bench-P = 布局 canary，探针新增 ≈25 KB 静态；bench-I = 副本忠实性） | ____ / ____ | ____ / ____ |
| `g_s7_syn_fg_built` / `g_s7_syn_fg_all`（仅 `S7_PROBE_SYN_FG` build；-2 = FG-A 未过不评估） | ____ / ____ | ____ / ____ |
| `g_s7_reads_per_frame` | ____（应 25） | ____ |
| bench build 的 `-O`/`-Ov` 凭证（Console 编译行截图） | ____ | ____ |

### 2.5 syn 侧对照旗设计（F-2；`S7_PROBE_SYN_FG`，默认关；**CTO 2026-09-03 裁定：不必做，保持默认关；仅当板上四段占比与 bench 四段占比在合成段出现不可归因的分歧时再申请开启**，DEC-S7-RULINGS-03）

- **盲区**：八锚 = analyze 子带 CRC；`fira_tfb_synthesize` 的 3 个 syn_int FIRA 段（`fira_tree.c:756-773`）rc 被 `(void)` 丢弃，bench 侧无任何锚（F4/F5 只比子带、F7 只计时）。某个 syn 段失败/早返回会给出**偏短**的 syn 读数而 FG-A 仍绿 → §12 FG1 对 syn 段不成立。这是项目既有盲区（463,273 同样无 syn FG），本文不再把 FG-A 写成"证明整链"。
- **对照旗**（已实现、默认关）：每帧括号**之外**，把同一组 FIRA 子带喂给冻结核 `tfb_synthesize`（每通道一个 `TreeChannelState`，与 FIRA 路径的合成历史逐帧锁步），FIRA 合成输出与核合成输出各自流式 CRC → `g_s7_syn_fg[c]`（1 同 / 0 异）、`g_s7_syn_fg_all`；`g_s7_syn_crc_fira[8]`/`g_s7_syn_crc_core[8]` 可读。**只在 `g_s7_fg_pass_all==1` 时评估**，否则报 -2（占位子带 0,0,0,in 下两条合成路径平凡相等，桌面不得报 PASS；`run_s7_probe_host.sh` H4 实跑 = -2）。不等 → **记录并上报**，不默认作废 w/ana（由 CTO/critic 判）。
- **代价**：+8 个 `TreeChannelState`（≈18 KB 静态）+ 每帧 8 次核合成（括号外，不进 cycle 数）→ 默认关；bench 内存紧（li1040 先例）是它默认关的原因；重开条件见本节标题（DEC-S7-RULINGS-03）。
- **不是锚**：它证明"FIRA 合成 == 核合成（同子带、同历史）"，不证明合成对不对（合成正确性由 F5-B/F7 的 telescoping 设计与 M2 板门/耳听承担）。

---

## 3. 板上三段括号规格（c）：s7-base 已按此落码（未 commit）；本工单不改板上 TU

> 2026-09-02 s7-base 回执：`M2_SEG_CYC` 括号 + `g_m2_beam_cyc_min` 已在 `m1_loopback_tdm.c` 落码，符号名与本节一致；测试员单 `sprint7/docs/S7_TESTER_RUNBOOK_SB.md` 的 B1 build = `M2_FIRA_INLOOP=1 FIRA_USE_REAL_ADI_FIR_HEADER M2_SELFTEST=1 M2_SEG_CYC=1`（Release/`-O` 对照步骤与括号判读指向本文）。下表"状态"列区分**已落码**与**本文建议、未实现**两类。行号引用的是 2026-09-02 审计版 TU（`fw_code_audit.md`）；s7-base 改动后行号会移动，以函数名为锚。

### 3.1 符号与含义（全部 `volatile uint32_t`，raw cycle，C9：代码内不做任何换算）

| 符号 | 含义（每帧 8 通道之和） | 初值 / 复位 | 状态 |
|---|---|---|---|
| `g_m2_beam_cyc_min` | 现有 beam 括号（`m2_beam_poll`）的 run 内最小值，与 `_last/_max` 同处更新 | `0xFFFFFFFF`；`m2_fira_setup` 复位；desktop honest-0 | **已落码（无条件，两种 build 都有）** |
| `g_m2_seg_w_cyc_last` / `_max` | **w** = 加权乘法循环，含权重下标读（`M2_CHMAP_FIX` 时含 `s_m2_chmap[c]` 查表）+ 64 次乘 + 循环开销 | 0；setup 复位 | **已落码**（`M2_SEG_CYC` 内） |
| `g_m2_seg_ana_cyc_last` / `_max` | **ana** = 恰好 `fira_tfb_analyze(&s_m2_fa[c], ...)` 调用（含冻结 `fira_tree.c` 内 6 个 FIRA 段的 DONE 忙等） | 同上 | **已落码** |
| `g_m2_seg_syn_cyc_last` / `_max` | **syn** = 恰好 `fira_tfb_synthesize(...)` 调用（含 3 个 FIRA 段的忙等） | 同上 | **已落码** |
| `g_m2_seg_tx_cyc_last` / `_max` | **tx** = 8 槽交织写 `tx[i*8+c]=o` + FG nz/peak 扫描的 64 次循环 | 同上 | **已落码** |
| `g_m2_seg_*_cyc_min` | 各段 run 内最小值 | `0xFFFFFFFF` | 建议项，**未实现**（可后补，不阻塞） |
| `g_m2_seg_frames` | 进三段统计的帧数（核对 = `g_m2_poll_count`） | 0 | 建议项，**未实现** |
| `M2_SEG_CYC` 构建指纹 | **无专用指纹**（s7-base 的 `M2_FP_*` 列表不含 SEG_CYC）；以 `g_m2_seg_w_cyc_last` 符号**可见/不可见**判该臂是否带括号（S-B runbook 表 A 同判据） | — | 已核；若要专用指纹 `M2_FP_SEG_CYC` 须走 D3 同类 gate 另派 |

### 3.2 每个括号罩什么 / 不罩什么（R42：括号跨度就是口径；s7-base 的链式读法）

```
m2_fira_beam_frame(rx, tx, &nz, &peak):          /* 全部在 m2_beam_poll 的 beam 括号内 */
  ta = CCNT                                      /* 每帧 1 次：打开 c=0 的 w 括号 */
  for c in 0..7:
    w = g_dolph_w8_q15[ chmap? ]; 64x s_m2_xw[i] = (w*rx[i])>>15
    tb = CCNT;  sw   += tb - ta                  /* w CLOSE  / ana OPEN */
    fira_tfb_analyze(...)
    tc = CCNT;  sana += tc - tb                  /* ana CLOSE / syn OPEN */
    fira_tfb_synthesize(...)
    td = CCNT;  ssyn += td - tc                  /* syn CLOSE / tx OPEN */
    64x { o = s_m2_chout[i]; tx[i*8+c] = o; nz/peak 累计 }
    ta = CCNT;  stx  += ta - td                  /* tx CLOSE = 下一路 w OPEN（链式，c=7 的这次读收尾） */
  *pnz = nz; *ppeak = peak;                      /* 原样 */
  4 个 sum -> g_m2_seg_*_cyc_last / _max         /* 在 m2_fira_beam_frame 末尾（仍在 beam 括号内，4 次比较） */
m2_beam_poll():
  t0 = CCNT; m2_fira_beam_frame(...); t1 = CCNT; /* 现有 beam 括号，原样 */
  beam -> last / max / min                       /* min 新增 */
  claim / FG 累计 / poll_count++ / latch          /* 原样，括号外 */
```

- **不罩**：claim（读 half、清 ready）、`g_m2_out_nonzero`/`g_m2_out_max_abs` 累计、`g_m2_poll_count`、`fg_beam_live` latch。
- **每帧 CCNT 读次数 = 4×8 + 1 = 33**（链式共用：上一路的 tx 关括号 = 下一路的 w 开括号），全部落在 `g_m2_beam_cyc_*` 之内。
- **三段之和 + tx ≤ 同帧 `g_m2_beam_cyc_last`**；差 = 循环控制 + 33 次读 + 4 次 sum 累加与末尾统计更新。
- **口径提醒**：ana 与 syn 各自**含** FIRA DONE 忙等（冻结件内，`fira_tree.c:481`），板上拆不出 compute vs 忙等（§0）。

### 3.3 宏门控（已落码）

- `M2_SEG_CYC` 默认 0 = 字节等同于现产品 build（`-D` 传入，不进 `.cproject`）；`M2_SEG_CYC=1` 且 `M2_FIRA_INLOOP` 未定义时 `#error`（括号在 `m2_fira_beam_frame` 内，无 M2 路径无意义）。
- `M2_SEG_CYC=1` 时才编入 33 次读与 4 个累加；不改数据路径 → **bit-exact 不受影响**，但仍是新二进制，八锚 + 板门重跑。
- guard-check 矩阵加 `-DM2_FIRA_INLOOP=1 -DM2_SEG_CYC=1` 列（s7-base 负责）。

### 3.4 两条判读约束

1. `M2_SEG_CYC=1` build 的 `g_m2_beam_cyc_*` **含 33 次读的扰动**，与 `M2_SEG_CYC=0` build 的 beam 数**不可直接相减**；两个 build 都读、离板比（§5 臂 0 vs 0s、A' vs As）。新基线（若 §1 成立）只认 `M2_SEG_CYC=0` 的臂。**第二个变量**：0s（B1）比 B0 多了 `M2_SELFTEST` 的静态数据（如 `s_m2_st_core`，默认 Block 0）→ Block 0 布局移位，而排查表 #3 正假设 Block 0 放置有影响，所以 0→0s 的差**不能全归** 33 次读；核对两臂 .map 的 `s_m2_sb0..chout` / `s_seg_in` / `s_seg_out3` / `s_taskMem` 地址是否相同，不同则在判读表注明（或请 s7-base 经 gate 提供 SEG_CYC-only 臂）。
2. `_min` 初值 `0xFFFFFFFF` 是"从未更新"哨兵（与 `g_m1_cb_cyc_min` 同约定）；desktop 路径 honest-0。

### 3.5 CCNT 读扰动量级估计 [L3]

`bench_cyc_target()` = 函数调用 + `clock()`（库函数读 EMUCLK）。ADI 例程把它当零成本用（`FIR_Throughput_21569.c:42,86`），但 33 次/帧不再可忽略：按每次读数十 cycle 量级估 [L3]，每帧扰动为 10^3 cycle 量级 [L3]，相对 831k 为千分之一量级 [L3]。**真值由读数定**：bench 探针的 `g_s7_ccnt_read_cyc` 直接量一次读的成本（板上可后补 `g_m2_ccnt_read_cyc`，建议项），扰动 ≈ 33 × 该值，回填后在判读表里扣除。

---

## 4. 排查表（d）：优化等级之外的差距候选成因

约定：**证据方向**只给"哪个读数往哪边动就支持/否定"，不给数值；**可回收量级**只许 [L3]/[L4] 或"未知"。读数符号：板上 `beam_min/last/max`、`w/ana/syn/tx`；bench `S7 beam/w/ana/syn`、副本 `spin/post/mem/task/flush/core`。

| # | 候选成因 | 依据（file:line） | 怎么证实 / 排除（用哪个读数） | 证据方向 | 若成立可回收 |
|---|---|---|---|---|---|
| 1 | **`beam_cyc_max` 是 run 内最大值**，含首帧冷（首次 CreateTask、首触数据）与 ISR 落入帧；稳态可能远低 | `m1_loopback_tdm.c:595-596`（只记 last/max）；`g_m2_beam_cyc_last` 存在但从未记录（`S7_DSP_ASSESSMENT.md §6.3 a`） | 臂 0 读 `beam_min / last / max` | `min ≈ last ≪ max` → 830,903 是离群/冷帧，稳态另算；`min ≈ max` → 系统性差距，与本项无关 | 未知（读数直接给） |
| 2 | **Debug 系统库 / FIR 驱动 debug 变体**（断言、句柄校验）在 72×3 次驱动调用 + 72 次 ISR 里累积 | `.cproject:59`（Debug 默认开）vs `:173`；1B map `libdrv.dlb[adi_fir.doj]` 含 `.sASSERT.*`、`ValidateTaskHandle/ValidateDeviceHandle` [L1 map] | 臂 B（Release）与臂 A' 的差（两臂都有 `-O`）；bench 副本 `task` 项量驱动调用本身 | B < A' 且差集中在 ana/syn（驱动只在 FIRA 段被调）→ 支持；B ≈ A' → 排除 | [L3] 每次调用百 cycle 量级 × 216 次/帧 → 10^4 量级；不超过 ana+syn 中非忙等部分 |
| 3 | **L1 放置 / 单端口争用**：M2 scratch `s_m2_sb0..3/xw/chout` 未 pin，在 Block 0（0x243e98–0x244178）与 FIRA DMA scratch `s_seg_in`(0x2411c0) / `s_seg_out3`(0x242360) / `s_taskMem`(0x243b60)、驱动数据 `gFirQueueInfo`(0x245f60)、**栈**(0x246cf8–0x25b674) 同块；`s_m2_fa` 在 Block 1(0x2c1200) 与 SPORT 缓冲同块 | fw 审计 §9.F；1B map [L1]；`m1_app.ldf:183,190`；`fira_tfb_analyze` 的 a1..r3 局部数组 5.4 KB 在栈（Block 0） | (i) 臂 C：M2 TU 给 6 个 scratch 加 `#pragma section("seg_l1_block1")`（非冻结件，CTO-gated），重读 .map + beam；(ii) bench 探针 `S7_PROBE_FA_BLOCK1` 开/关两跑对照；(iii) 副本 `spin` 项：FIRA DMA 读写 Block 0 时核在自旋读 Block 0 的 `g_FIRTaskDoneCount`(0x243cf8) | 臂 C 的 ana/syn 明显低于臂 0 → 支持；不变 → 排除。bench 两放置的 spin 差 = 放置对忙等的影响 | [L3] 小到中；bench 放置未知（bench .map 不在库内，H2 调整时 FIRA set 在 Block 0，`H2_MAP_PLACEMENT_ADJUDICATION.md:95-101`）|
| 4 | **FIRA DONE 自旋等待 + FIRI 中断往返**（每段一次：QueueTask → 硬件 → FIRI → `FirInterruptHandler` → 回调 → 计数 → 自旋退出） | `fira_tree.c:480-481`；ADI 报告中断往返 423–595 cyc、QueueTask 195–371 cyc（Legacy/ACM 两列）[L4/ADI 文档 EE408 Table 1，`fira_fit_assessment.md §4.2`；非我方实测]；1B map `FirInterruptHandler` 0x1c8f7e | 只有 bench 副本能拆：`spin` 项 vs `ana+syn`；板上不能（冻结件内）→ 用"ana/syn 在 A' 下不随 `-O` 变的部分"间接估 | 若 bench `spin` 占 ana+syn 的大头且板上 ana/syn ≫ bench ana/syn → 差在忙等（板上中断延迟/优先级/SEC 配置，非 `-O`）；若 `spin` 占比小 → 差在核侧 | 忙等本身不可回收（硬件 + 中断）；仅重构可藏（B7，已裁不做） |
| 5 | **核侧 postscale / memcpy / 零填充 / 细节相减 在 -O0 下膨胀**（这才是 `-O` 的作用点） | `fira_tree.c:345-392`（80-bit 重组 + postscale 每样本 3 字）、`:604-656`（memcpy/memmove）、`:722-726`、`:756-773` | bench 副本 `post + mem + core` 之和 vs `spin`；臂 A' vs 臂 0 的 ana/syn 差 | A' 的 ana/syn 明显低于臂 0、w 与 tx 同比例低 → `-O` 成立且量 = 差；ana/syn 不动 → `-O` 不是主因 | ≤ (post+mem+core+w+tx) 在 -O0 下的份额 [L3]；上限 = 臂 0 − 臂 A' 的实测差 |
| 6 | **I/D cache 配置差异** | `system.svc:159` dcache 关+CPLB、`:162` icache 开、`:198-211` 三 cache 各 16 KB；21569 L1 不被数据 cache（`m1_loopback_tdm.c:34`「L1 RAM is NOT data-cached」）；1B map：**代码在 L1 Block 3**（`dxe_block3_sw_code_prio2`：`fira_tree.doj` 0x1c15ee、`m1_loopback_tdm.doj` 0x1c2072、`adi_fir.doj` 0x1c87a8）、数据全在 L1 Block 0/1 [L1 map] | 板上取指与数据都在 L1 → cache 不在路径上；只剩 `flush_data_buffer` 的执行成本（副本 `flush` 项）与 bench 工程的 cache/放置（未知，bench .svc/.map 不在库内） | bench `flush` 项相对 ana+syn 很小 → 排除 cache 操作成本；bench 若代码/数据在 L2（需 bench .map）→ bench 应更慢而非更快，不解释差距 | 板侧"未知/不适用"；bench 侧待 .map |
| 7 | **`flush_data_buffer` 在 L1 区域上的调用成本**（每段一次，范围 = window×3 字） | `fira_tree.c:522-524` | 副本 `flush` 项 | 占比小 → 排除 | [L3] 小 |
| 8 | **驱动 cache 管理配置**：bench 工程内编译的驱动源 `ADI_CACHE_MANAGEMENT`（例程配置 1，`FIR_Multi_Channel_Processing/.../adi_fir_config_2156x.h:64`）vs M2 用预编译 `libdrv` 的默认 | 1B map `libdrv.dlb[adi_fir.doj]` [L1]；bench 驱动源在工程内（`FIRA_IMPL.md:76`） | 副本 `task` 项（bench）；板上无法拆 | 方向：bench 若付 flush 成本会更慢 → 不解释 M2 更慢；只在 M2 的 `libdrv` 是 debug 变体时才反向（并入 #2） | 未知 |
| 9 | **SPORT RX ISR 抢占**（每帧一次 `m1_sport_rx_callback`，64 样本 FG 扫描 + 握手） | `m1_loopback_tdm.c:466-545`；ISR 内无计算（M2FIX） | `g_m1_cb_cyc_max`（M2 口径 = 该 ISR 体）；板上 `beam_max − beam_min` 的抖动带 | 抖动带 ≈ `cb_cyc_max` 量级 → ISR 只贡献抖动；带宽远大于它 → 另有来源（#1/#3） | [L3] 千级 cycle，≤1% 帧 |
| 10 | **SPORT DMA 乒乓块争用**（RX 64 字 + TX 512 字/帧进出 Block 1，与 `s_m2_fa` 同块） | `m1_app.ldf` 横幅 R47 caveat；1B map Block 1 三符号 [L1] | 臂 C 若把 scratch 也 pin 进 Block 1 会加重此项 → 对照"scratch pin 到 Block 2/3"（s7-base 可选臂）；bench 无 DMA 可作零争用对照的 ana/syn | 每帧 576 字 DMA 相对 10^5 级核访存 [L3] → 量级小 | [L3] 小 |
| 11 | **首帧/冷路径**：`fira_channel_init` 后首帧、首次 CreateTask、SEC 首次 FIRI | 与 #1 合并 | `beam_min/last` | 同 #1 | 同 #1 |
| 12 | **tx 段**（bench 无）：64×8 次交织写 + abs/比较 | `m1_loopback_tdm.c:432-446` | 板上 `tx` 项直接读 | tx ≪ beam → 排除为主因 | [L3] 10^3–10^4 级 |
| 13 | **测量结构差异**：F7 = 1 个稳态帧（热身 4 帧后），M2 = 10^5 帧的 max | `fira_regression.c:597-619`；`m1_loopback_tdm.c:596` | 用 bench 探针的 1020 帧 max/min 与板上 min/max 对齐口径后再比 | bench max 与板 min 接近 → 差主要是抖动/离群；bench max ≪ 板 min → 系统性 | — |
| 14 | **`-g` / `_DEBUG` / `-e` / `-ip`** | `.cproject:40,44,57,58` | 臂 A'（只 `-O`）与臂 B 的差已含它们；单独不拆 | — | [L3] 可忽略（除 #2） |
| 15 | **时钟树（CTO 2026-09-03：已给出零改码读法，见 `S7_TESTER_RUNBOOK_SB.md` 第 6b 步与表 D）**：FIRA 忙等 cycle 与 CCLK/SYSCLK/SCLK 比例相关；1e9 是 bench F7 G6 读回的 [L1]，M2 工程从未板上读 `adi_pwr_GetCoreClkFreq`，两工程同板、同 `adi_pwr_Init(0,25 MHz)`（`m1_main.c:44` / `bench_main.c:144`）、`system.svc` 无 CGU 项 → 同频只是推断 [L3] | `m1_main.c:44`；`bench_main.c:144`；`system.svc` | **测试员在 B0 上用 Register/Memory 视图读 `CGU0_CTL/STAT/DIV`（`0x3108D000/0x3108D008/0x3108D00C`）**，`s7_intake.py` 解码成 CCLK 后与 bench `g_s7_cclk_hz` 对照（不加 TU 代码、不改二进制；`g_m2_cclk_hz` 方案作罢） | 两者相等 → 排除；不等 → 忙等段按比例重标，先于一切 `-O` 判读 | 若不等：全部差距先按时钟比例折算后再拆 [L3] |

**判读顺序建议**：#1（零改动，先读 last/min）→ #5（臂 A'，零成本假设）→ #2（臂 B 旁证）→ #3（臂 C，一行 pragma）→ #4/#7/#8（bench 副本）→ #9/#10/#12（读数排除）。

---

## 5. runbook 增量（e）：给测试员的步骤化清单

> 前置：`sprint7/docs/S7_TESTER_RUNBOOK_SB.md`（s7-base）的 S-B 基座会话已完成：`M2_SELFTEST` 八锚 PASS、6 宏指纹、板门全绿、`g_m2_beam_cyc_min` 与 §3 括号已在 TU 中。本节只写 B6.3 增量；准备/安全/自由运行纪律沿 `sprint6/STAGE4_TESTER_RUNBOOK.md` 与 `sprint6/BOARD_TEST_INSTRUCTIONS.md`。**每臂 = Clean → Build → 凭证截图 → Load `.dxe` → 放音乐不间断 Run ≥10 s → Suspend → idle 读表 → 导 .map 改名 → 复原**。任一步不确定：原样发回，停手。

### 5.1 臂序（按优先级；时间不够先做 0 与 A'）

| 臂 | 配置 | 宏（在 S-B 基座宏之上） | 主读数 | 目的 |
|---|---|---|---|---|
| **0** | Debug 现状 | **不需要额外 build**：读数取 S-B 的 **B0**（`M2_FIRA_INLOOP=1 FIRA_USE_REAL_ADI_FIR_HEADER`，无 SEG_CYC、无 SELFTEST = 最纯的无括号 Debug 二进制）；或 **B2**（SELFTEST+NEGCTRL、无 SEG_CYC；NEGCTRL 只改 init 自检权重，不碰活流）的 `beam_min/last/max` | `beam_min/last/max`（无括号扰动的 Debug 稳态基线） | 排查表 #1（稳态 vs max）；与 0s（= B1）的差 = 33 次读的扰动 **+ SELFTEST 静态数据带来的 Block 0 布局差**（§3.4 第 1 条，两臂 .map 核对） |
| **A'** | Debug + GUI 勾 `-O`（§1.3 路径 A） | 同 0 | `beam_min/last/max` + 板门 + 八锚 + 听感 | **零成本假设主判**；若成立即新基线候选（无括号扰动） |
| **0s** | Debug 现状 | `M2_SEG_CYC=1`（**= S-B 基座 B1 build 本身，读数可直接复用**） | 四段 `w/ana/syn/tx` last/max + beam | 板上三段拆分（无 `-O`） |
| **As** | Debug + `-O` | `M2_SEG_CYC=1` | 同上 | 三段在 `-O` 下的变化 → 排查表 #5（若时间只够一臂带 `-O`：做 As，beam 数扣 33 次读扰动后近似 A'） |
| **B** | Release（§1.3 路径 B） | 同 0（Release 侧重加） | `beam_min/last/max` + 板门 + 八锚 | 旁证（#2） |
| **A''**（可选，单变量） | Debug + `-O` + 只取消勾 `Use Debug System libraries (-add-debug-libpaths)` | 同 0 | `beam_min/last/max` + 板门 + 八锚 + .map | 排查表 #2 的**单变量**证据（比 B−A' 干净）；同样按 §1.2 硬规则 1 复原 + checkout |
| **C**（可选；s7-base 本轮**未动** `s_m2_sb*/xw/chout` 放置，若要做须经 lead/CTO 走 D3 同类 gate 另派 TU 改动） | Debug + `-O`（或现状） + scratch pin Block 1 | `M2_SEG_CYC=1` | 四段 + .map | 排查表 #3 |
| **bench-P** | bench 工程 + 探针（§2；无副本） | bench 侧 | `g_s7_*` 全表 + `g_f7_cyc_8ch_fira` | bench 三段 |
| **bench-I** | bench 工程 + 副本（`S7_PROBE_INNER`；`fira_tree.c` Exclude） | bench 侧 | `g_s7_in_*` + F4/F5 锚 | 忙等/核侧拆分（#4/#5/#7） |

### 5.2 每臂固定动作（勾选）

- [ ] 第一个读构建指纹（`g_m2_fira_inloop=1`；`g_m2_seg_w_cyc_last` 的可见/不可见与该臂一致，见 S-B 表 A）
- [ ] 板门 6 项抄值（不绿 → 该臂作废，发回）
- [ ] `M2_SELFTEST` 八锚抄 8 值（任一不过 → 该臂 cycle 作废）
- [ ] `g_m2_beam_cyc_min / last / max` 抄三值；`g_m1_cb_cyc_max` 抄
- [ ] （`M2_SEG_CYC=1` 臂）四段 last/max(/min) 抄；核对 w+ana+syn+tx ≤ beam_last
- [ ] `g_m2_out_max_abs`、`g_m1_max_abs_sample` 抄（R57 判别式）
- [ ] 凭证：Tool Settings 截图、Console 两条编译行（`m1_loopback_tdm.c` + `fira_tree.c`）、Defined symbols、（B 臂）Linker 页
- [ ] `.map` 导出改名 `map_B63_arm<X>_<日期>`；核对 pin 三符号 ≥0x2c0000、`s_seg_*` 在 0x24xxxx
- [ ] 功放上电最小音量重 Load 重跑 → 听感一行话（正常 / 刺耳 / 无声 / 卡顿）
- [ ] 复原本臂改动（`-O` 取消 / Configuration 切回 Debug / 宏删回基座）
- [ ] **`git status`**：`.cproject`/`.project` 若有变动 → `git checkout -- sprint6/dsp/audio/m1_cces_project/.cproject sprint6/dsp/audio/m1_cces_project/.project`，不入库（§1.2 硬规则 1）

### 5.3 回填模板（**全部留空**）

**板上臂：**

| 臂 | 指纹 | 板门 | 八锚 | beam min | beam last | beam max | cb_cyc_max | w last/max | ana last/max | syn last/max | tx last/max | 听感 | .map | 凭证 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | ____ | ____ | ____ | ____ | ____ | ____ | ____ | — | — | — | — | ____ | ____ | ____ |
| A' | ____ | ____ | ____ | ____ | ____ | ____ | ____ | — | — | — | — | ____ | ____ | ____ |
| 0s | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____/____ | ____/____ | ____/____ | ____/____ | ____ | ____ | ____ |
| As | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____/____ | ____/____ | ____/____ | ____/____ | ____ | ____ | ____ |
| B | ____ | ____ | ____ | ____ | ____ | ____ | ____ | — | — | — | — | ____ | ____ | ____ |
| C | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____/____ | ____/____ | ____/____ | ____/____ | ____ | ____ | ____ |

**bench 臂：**（符号表 `sprint7/dsp/probe/README.md §3`）

| 臂 | fg_pass_all / core_selfcheck | f7_cyc_8ch_fira | beam min/last/max | w min/last/max | ana min/last/max | syn min/last/max | ovh_last / read_cyc | in_task/spin/flush/post/mem/core last | in_reads | F4/F5 锚 |
|---|---|---|---|---|---|---|---|---|---|---|
| bench-P | ____/____ | ____ | ____/____/____ | ____/____/____ | ____/____/____ | ____/____/____ | ____/____ | F4 `g_fira_f4_pass`=__ / F5 `g_f5_pass_all`=__（每臂都抄，§2.4） | `g_s7_fg_pass_all`=__ | `g_s7_syn_fg_all`=__（未开=-99） |
| bench-I | ____/____ | ____ | ____/____/____ | ____/____/____ | ____/____/____ | ____/____/____ | ____/____ | ____ ×6 | ____ | ____/____ |

---

## 6. 回填后的判读逻辑（决策树；本节**不预填任何结论**）

记板上 `B0 = 臂0 beam_min`，`BA = 臂A' beam_min`，bench `Bb = bench-P beam_min`（或同 build 的 `g_f7_cyc_8ch_fira`）。三段比：`r_x = 臂0s x / bench-P x`（x ∈ {w, ana, syn}）。

1. **先看 #1**：`臂0 beam_last` 与 `beam_min` 是否接近 `beam_max`？
   - 若 `min ≈ last ≪ max`：830,903 是 run 内离群/冷帧；**稳态基线 = min~last**；后续所有比较用 min/last。
   - 若 `min ≈ max`：系统性差距，进入 2。
2. **零成本假设（#5）**：`BA / B0`。
   - `BA` 落到 bench 同量级 → 假设成立，差距主要是 `-O`；新墙钟基线候选 = `BA`（无括号臂）。**产品配置是否改用 `-O`** 由 CTO 裁（提案 D2 保留项），改则八锚 + 板门 + 耳听 + .map 重过。
   - `BA ≈ B0` → `-O` 不是主因，进入 3。
   - 介于两者 → 部分成立，剩余差按 3 拆。
3. **差在 FIRA 段还是纯核段**（臂 0s vs bench-P）：
   - `r_w`、`r_ana`、`r_syn` 都 ≫1 且大小相近 → 均匀放大 → 指向编译/环境级因素（`-O`、驱动变体 #2）。
   - `r_ana`、`r_syn` ≫ `r_w` → 只有 FIRA 段慢 → 指向忙等/中断/放置（#3、#4），进入 4。
   - `r_w` ≫ `r_ana` → 纯核循环慢（少见）→ `-O` 或放置（`s_m2_xw` 在 Block 0）。
4. **忙等占比**（bench-I）：`spin / (ana+syn)`。
   - spin 占大头，且 `post+mem+core` 小 → 核侧能回收的少；板上 FIRA 段慢 = 中断/放置差异 → 臂 C 与 SEC 配置核对。
   - `post+mem+core` 占大头 → 与 `-O` 一致（这些是 -O0 膨胀点）。
5. **旁证**（臂 B vs A'）：B 低于 A' 的部分 = Debug 系统库/驱动变体/放置（#2）；**不用 B 定基线**。
6. **扰动扣除**（账目与代码逐一对得上）：板上 `M2_SEG_CYC=1` 臂的 beam 含 **33** × `ccnt_read_cyc`（链式 1+4×8，全部落在四段之和 + 链首 1 次内）；bench-P 的 beam 含 **25** × `g_s7_ccnt_read_cyc`（链式 1+3×8，`g_s7_reads_per_frame`），其中 24 次落在 w+ana+syn 内（每段 8 次）、`g_s7_probe_ovh_last` 只含链首 1 次读 + 循环进出；bench-I 的 ana/syn 另含 `in_reads × g_s7_ccnt_read_cyc`。核对 `w+ana+syn(+tx) + ovh == beam_last`（同帧恒等；ovh 应为 1–2 次读的量级），ovh 远大于此 → 括号或读法有误，先修。
7. **新基线登记**（若成立）：写 DEC 行时同时给 min/last/max 三值与 build 凭证，注明"`M2_SEG_CYC=0`、优化等级 X、八锚 PASS、板门绿"；`S7_DSP_ASSESSMENT.md §8` 的组合表按新基线重算（B1/B2 是否触发解冻按 D1 墙钟口径）。

---

## 7. 诚实声明 / L 标 / 未验项

- 本文**没有任何板上新数字**；所有格子留空由测试员回填；PM 不替补。
- `.cproject:39` "无 value = 优化关" 是按 CDT 语义推断 [L3]，L1 凭证 = 测试员的 GUI 复选框截图与 Console 编译行；bench 的 `-O -Ov=100` 来自 `FIRA_IMPL.md:72` 的文字记录 [L1 文档]，bench 工程本身不在库内，**建议 bench-P 臂同样交 Console 编译行截图**。
- 排查表所有"可回收量级"均 [L3]/[L4]/未知；#2 的"debug 变体"由 map 中断言字符串推断 [L3]，不是证实。
- 本机无 cc21k、无板：探针与副本只过了 gcc 语法/宿主运行 [L2]（`sprint7/dsp/probe/README.md §5-§6`），编译门 = 测试员 CCES build（D14）。
- 桌面 FG 负控制已证：占位链下八锚 0/8（预期 FAIL）；核正控制 8/8。**八锚只覆盖 analyze 段**；synthesize 段无锚（既有盲区，与 F4/F5/F7 相同），其读数置信低一档；`S7_PROBE_SYN_FG` 合成对照旗（§2.5）在桌面只能报 -2（不评估），真值上板；按 DEC-S7-RULINGS-03 不必做、保持默认关（重开条件 = 合成段占比出现不可归因分歧）。上板若 `g_s7_fg_pass_all=0` → cycle 一律作废。
- 板上三段括号（§3）由 s7-base 实现（2026-09-02 已落码、未 commit）；本文按其回执的符号命名与链式口径引用；`_min`/`g_m2_seg_frames` 为本文建议项，未实现不阻塞。对 `m1_loopback_tdm.c` 的行号引用是 2026-09-02 审计版（`fw_code_audit.md`）的行号，s7-base 改动后已移动（如 `m2_fira_beam_frame` 已在 :533 起），以函数名为锚。
- 内拆分副本 `fira_tree_probe.c` **CTO 2026-09-03 裁定不上 bench、保持默认关**（DEC-S7-RULINGS-02；对照 build 后仍无法归因时另行申请）；它只是桌面验证过的设计件，不进本轮任何板测臂。
- 臂 0（无括号 Debug 基线）**不需要测试员额外 build**：取 s7-base runbook 的 B0（或 B2）读数即可（s7-base 2026-09-03 核对）；臂 0s = B1。
- 三口径纪律：本文只用墙钟；不与 T2 争用账（95.59≤210.19）或纯核 MCPS 互称达标/矛盾。
- **未做**：真冷 I/D cache 失效测量（21569 L1 不被数据 cache，本项对板上意义有限，见排查表 #6）；bench 工程 .map/.svc 核实（不在库内，待 CTO 提供）。

---

## 8. 引用

`sprint2/docs/decisions_log.md:1013,1036-1052`；`sprint7/docs/S7_ALGO_UPGRADE_PROPOSAL.md §1/§3-B6.3/§4/§6 D2`；`sprint7/docs/S7_DSP_ASSESSMENT.md §0.2/§0.3/§6.3`；`sprint7/docs/S7_VERIFICATION_PLAN.md:46-47,239`；PM 审计 `fw_code_audit.md §1.4/§2.1/§7.1/§9.F`、`algo_code_audit.md §3.5/§4.6`（**会话临时件**，scratchpad，未入库；本文引用的 file:line 结论均已逐条以仓内文件复核，正式出处以本列表其余仓内文件为准）；`sprint4/dsp/fira/fira_regression.c:71-81,260-263,521,597-650`；`sprint4/dsp/fira/fira_tree.c:345-392,424-539,604-656,675-773`；`sprint4/dsp/fira/FIRA_IMPL.md:70-76`；`sprint4/dsp/fira/F7_CLOSING_RECORDS.md:148-160`；`sprint4/dsp/core_only/bench/bench_main.c:104-107,118,237-241`；`sprint4/dsp/core_only/bench/CCNT_source.md`；`sprint5/H1_WCET_WORKORDER.md §3`；`sprint5/audit/H2_MAP_PLACEMENT_ADJUDICATION.md:95-117`；`sprint3/audit/fira_fit_assessment.md §4.1-4.2`；`sprint6/dsp/audio/m1_cces_project/.cproject`（只读）；`.../system.svc:159-162,198-211`；`.../system/startup_ldf/m1_app.ldf:183,190,202,215`；`.../src/m1_loopback_tdm.c:34,203-219,356-361,401-450,466-545,580-607,788-811`（2026-09-02 审计版行号；s7-base 改动后已移动，以函数名为锚）；`.../src/m1_main.c:78`；`.../src/m1_cyc.c`；`sprint6/dsp/audio/board_artifacts/M1_Loopback_M2build_1B_PASS_20260616.map.xml`；`sprint6/dsp/audio/run_guard_check.sh`；`sprint6/BOARD_TEST_INSTRUCTIONS.md`；`sprint6/STAGE4_TESTER_RUNBOOK.md:38-58`；`sprint6/dsp/audio/m1_cces_project/M1_CCES_IMPORT_GUIDE.md`；`sprint7/dsp/probe/README.md`。
