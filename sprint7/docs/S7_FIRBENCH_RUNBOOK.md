# S7 每通道 FIR 算力台架 — 测试员操作单（S7_FIRBENCH_RUNBOOK）

> 日期 2026-09-27 ｜ 作者 dsp-algorithm teammate ｜ 包：`sprint7/dsp/firbench/`（文件清单与 md5 见其 `README.md` §0）
> **目的**：DEC-S7-SIDE30-01 ③"每通道滤波器"路线的算力 go/no-go。设计文档 `S7_SIDE30_PERCH_FIR_DESIGN.md` §5 只有 [L3 MAC × 30–50 cyc/MAC] 的估算（128 抽头放核上从"勉强"到"超预算约 2.5×"），能否落地取决于 FIRA [L4]。本单让测试员在 ADSP-21569 板上**实测**：8 路 FIR、每帧 64 样点、63/127/255 抽头（64/128/256 档），FIRA 三种任务组织 + 核两种写法，每一格都带逐通道 golden 门。
> **状态**：包已过桌面自动检查（[L2]，README §4）。独立 critic R3d（2026-09-27）判 **CONDITIONAL**（0 BLOCKER / 2 MAJOR / 4 MINOR / 1 INFO），A-1…A-7 已整改（README §7），**待 delta 复审**；**CTO_OK 未取得**——两者到位前不上板（§1）。
> **2026-09-29 状态更新**（上一行原文保留）：
> - critic R3d 的 delta 与 mini-delta 两轮对本包均判 **PASS**（`sprint7/critic/CRITIC_L_SIDE30_R3D_20260927.md` A 部分），本包已入库（commit `0ef46c4`）；
> - **CTO_OK 已给**：CTO 2026-09-29 原话「恩，我同意sfirb可以」。
> - §1 第 1 条的两个条件至此都已满足；§1 第 2–4 条（板与版本确认、上电与 JTAG 顺序、只做 JTAG Load）照旧。
> - 加入本段后本单的 md5 已变，新值见 `sprint7/dsp/firbench/README.md` §0（本单不在测试员第 2 步要核的文件之列）。
> **L 级总则**：本单**不写任何板上预期读数**，所有 cycle 格留空。表里给出的"应为"只有代码/数据常量（帧数、版本号、CRC 常量），不是测量预期。板上读回的 cycle = [L1 bench]；由它算出的占帧比/余量 = [L1 推导]；外推 = [L3 on L1]。

---

## 1. 上板前置（缺一不上电）

1. **过门与授权**：独立 critic 对本包 §12 判 PASS（或 PASS_WITH_MINOR 且已修），且 CTO 对本包给出 CTO_OK（DEC-S7-SIDE30-01 ④ 的逐包先例）。PM 确认后才把本单发给测试员。
2. **板与版本确认（C10 / 铁律九）**：AD-EXKIT V2.1 底板 + 21569 SOM（芯片 ADSP-21569KBCZ10），与 F7 / S7 探针那次是同一块板。不是这块板 → 停，报 PM。
3. **上电与 JTAG 顺序**（照 `sprint3/audit/BENCH_OPS_CARD.md` Phase 2 第 8–12 步，不在此重述其余项）：BMODE0/1/2 全拨 0（No boot）；**先插 JTAG（板断电）→ 板上电 → 仿真器接 USB**；**禁止热插拔**；ICE Test 5 步全过再 Load；结束时**先 disconnect → 再断电 → 再拔**。
4. **本次只做 JTAG Load 到 RAM 运行**，不烧 flash、不改 boot、不写任何寄存器（第 5 步的时钟寄存器只读）。

## 2. 准备文件（Windows）

1. 把整个 `sprint7/dsp/firbench/` 拷到台架机（含 `fb_coeffs.h`、`fb_goldens.h` 两个生成件）。
2. 逐个核 md5（`certutil -hashfile <文件> MD5`），与 `README.md` §0 表逐字比对；任一不同 → 停，报 PM（生成件被改过则 golden 失效）。
3. 核补丁基线：工程里的 `bench_main.c` 打补丁前 md5 应为 `25090f2c29d6729443bef5ed1feb5d31`；若工程里已打过 S7 探针补丁（`bench_main_s7.diff`），则在其上叠打本补丁即可（两种顺序结果相同，见第 3 步的 md5）。

## 3. 工程与构建

1. **工程**：CTO Windows 上的 `bench_core_only`（FIRA 例程派生、F4/F5/F7/H1/H2 与 S7 探针都在它上面跑过的那个 FIRA build）。**不新建工程**。
2. **加源文件**：source list 加 `sprint7/dsp/firbench/s7_firbench.c`（与 `fira_regression.c` 同一 build；core-only build 不加）。
3. **include path**：加 `sprint7/dsp/firbench` 的**绝对路径**（`${repo}` 不是 CCES 变量）。
4. **打补丁（不改仓库里的 tracked 文件）**：
   - **推荐做法**：只给 bench 工程**实际编译的那份副本**打补丁（CCES 工作区里该工程自己的 `bench_main.c` / `main.c`，在仓库之外）。git bash 执行 `patch <副本路径> < sprint7/dsp/firbench/bench_main_firbench.diff`（命令里给出文件名时，patch 不看 diff 头里的路径）。打补丁前先核副本 md5 = `25090f2c29d6729443bef5ed1feb5d31`，或已打探针补丁后的值。
   - **仅当该工程直接编译仓库里的 `sprint4/dsp/core_only/bench/bench_main.c` 时**：在仓库根目录执行 `patch -p1 < sprint7/dsp/firbench/bench_main_firbench.diff`；本次会话结束、表格和 `.map` 都抄完之后，执行 `git checkout -- sprint4/dsp/core_only/bench/bench_main.c` 还原，再用 `git status` 确认该文件不再显示为已修改。**不要 commit，不要 reset**。不还原的话，下次 `git pull` 会停在 "local changes would be overwritten"（测试员索引规定遇到这种情况原样发回）。
   - 没有 git bash：按 diff 手工加两处（① `#include "fir_coeffs_q31.h"` 行下面 5 行声明；② H2 那段注释块结束后、`#endif` 之前的调用块），同样只改副本。
   - 打完核 md5：只打本补丁 = `d003d326da30a673dc33d7900aba5a51`；与探针补丁叠打 = `5b3b459894e9d1949fce5b087418549c`（两种做法结果相同）。都不对 → 停，报 PM。
5. **构建配置**：**沿用上次 F7 / 探针那次的配置，不改优化级别**（F0 那次记载为 Debug Configuration + `-O -Ov=100`，`sprint4/dsp/fira/FIRA_IMPL.md:72`；以工程里实际看到的为准）。把 Configuration 名与编译器优化选项原文抄进表 A，并截图 Compiler 优化设置页（命名 `opt_FB.png`）。Defined symbols 里应已有 `TARGET_SHARC`、`FIRA_USE_REAL_ADI_FIR_HEADER`。**不得**定义 `FB_HOST_MAIN`、`FB_HOST_EMU`、`FB_EMU_STUB`、`FB_EXPECT_EMU`、`FB_EXPECT_STUB`（这些是桌面专用）。`FIRBENCH_FLUSH_IN`、`FIRBENCH_P1_FXD_EACH` 默认**不加**，只在第 8 节故障分流时按指示加。
6. **编译**：须 0 error；warning 条数抄进表 A。保存本次 build 的 `.map`（与 S-B 相同的做法，测试员索引要求每次回传都带 `.map`），记下文件名与 md5。链接报 li1040（内存溢出）→ **停，报 PM**，不要删代码、不要自行加 section pragma。

## 4. 运行

1. Load → Run，**全程 FREE-RUN**：`s7_firbench.c` 里**不设任何断点**（FIRA 自旋 + 断点可能死锁）。
2. 运行顺序（由补丁决定）：F2 → F4 → F5 → F7 →（若链接了探针）S7 探针 → H1 → H2 → **FIR 台架** → idle。FIR 台架排最后，H2 已在它之前停掉自己的 ISR 与总线负载。
3. 等程序停在 `main()` 末尾的 `while (1)` idle（可只在这一行设断点，或跑足够久后 Suspend），确认 `g_fb_done` 已不是 −99 再读数。本单不给预期时长；核路径 255 抽头最慢。
4. 读数一律在 idle 时从 Expressions 窗口读，数组展开抄全。

## 5. 核心时钟读回（DEC-S7-RULINGS-03，只读）

仍在 idle 的 Suspend 状态，按 `S7_TESTER_RUNBOOK_SB.md` 第 6b 步的同一方法：Register 视图展开 `CGU0` 读 `CGU0_CTL` / `CGU0_STAT` / `CGU0_DIV`，或 Memory 视图按地址 `0x3108D000` / `0x3108D008` / `0x3108D00C`（宽度 4 字节，Hex）读。三个值原样抄进表 B，截图命名 `cgu_FB.png`。**只读不写**。CLKIN 按 AD-EXKIT V2.1 核心板原理图为 25 MHz；如知实物晶振不同，抄实际值与出处。

## 6. 读数回填（全部留空，测试员填）

### 表 A —— 构建指纹

| 项 | 应为（代码/文件常量） | 回填 |
|---|---|---|
| `s7_firbench.c` / `s7_firbench.h` / `fb_coeffs.h` / `fb_goldens.h` 的 md5 | = `README.md` §0 | ____ / ____ / ____ / ____ |
| 打补丁后 `bench_main.c` md5 | `d003d326…`（单打）或 `5b3b4598…`（叠打） | ____ |
| 是否链接了 S7 探针 TU | — | 是 / 否 |
| Configuration 名 | 同 F7 那次 | ____ |
| 编译器优化选项原文（`-O` 是否启用、`-Ov` 值，其余优化相关项照抄）＋ 截图 `opt_FB.png` | 同 F7 那次（记载为 `-O -Ov=100`，以实际为准） | ____ |
| 本次 build 的 `.map` 文件名 / md5 | — | ____ / ____ |
| Defined symbols（全部抄） | 含 `TARGET_SHARC`、`FIRA_USE_REAL_ADI_FIR_HEADER` | ____ |
| 编译 error / warning 条数 | 0 / 抄值 | ____ / ____ |
| `g_fb_version` | `0x20260927` | ____ |
| `g_fb_build_flags` | 默认 `0x3`；加 `FIRBENCH_FLUSH_IN` 时 `0x7`；加 `FIRBENCH_P1_FXD_EACH` 时 `0xB`；两个都加 `0xF` | ____ |

### 表 A2 —— 关键数据的放置（地址读数 + `.map`）

地址读数在 idle 时从 Expressions 窗口抄（十六进制）；`.map` 一栏填该符号所在的 memory segment / output section 名。静态符号在 `.map` 里可能以局部符号出现，也可能查不到；查不到就只填地址，PM 用同一份 `.map` 的 memory segment 起止地址判归属。

| 关键数据 | 地址读数 | 回填地址 | `.map` 里的 segment / section |
|---|---|---|---|
| 系数表 63 抽头 `FB_COEF_T63` | `g_fb_addr_coef[0]` | `0x________` | ____ |
| 系数表 127 抽头 `FB_COEF_T127` | `g_fb_addr_coef[1]` | `0x________` | ____ |
| 系数表 255 抽头 `FB_COEF_T255` | `g_fb_addr_coef[2]` | `0x________` | ____ |
| 线性输入缓冲 `s_fb_lin`（T8/T1/核） | `g_fb_addr_lin` | `0x________` | ____ |
| 环形输入缓冲 `s_fb_circ`（P1） | `g_fb_addr_circ` | `0x________` | ____ |
| FIRA 输出区 `s_fb_out3` | `g_fb_addr_out3` | `0x________` | ____ |
| Q31 输出 `s_fb_y` | `g_fb_addr_y` | `0x________` | ____ |

### 表 B —— 核心时钟

| 项 | 回填 |
|---|---|
| `CGU0_CTL` @ `0x3108D000` | `0x________` |
| `CGU0_STAT` @ `0x3108D008` | `0x________` |
| `CGU0_DIV` @ `0x3108D00C` | `0x________` |
| CLKIN 及出处 | ____ MHz ／ ____ |
| 读法（register_view / memory_view）＋ 截图 `cgu_FB.png` | ____ |
| `g_fb_cclk_hz` / `g_fb_cclk_rc`（驱动读回，只作交叉核对） | ____ / ____ |

### 表 C —— 环境与总门

| 符号 | 应为 | 回填 |
|---|---|---|
| `g_fb_done` / `g_fb_valid` | 1 / 1 | ____ / ____ |
| `g_fb_open_rc` / `g_fb_close_rc` | 0 / 0 | ____ / ____ |
| `g_fb_chirp_crc` / `g_fb_chirp_ok` | `0x90556BC7` / 1 | ____ / ____ |
| `g_fb_coef_crc[0..2]` / `g_fb_coef_ok[0..2]` | `0x1183DDFB`, `0x8FE38AE2`, `0x1F897D3D` / 1,1,1 | ____ / ____ |
| `g_fb_neg_fail_all`（负控制：占位系数必须**不中**） | **1** | ____ |
| `g_fb_neg_crc[0..7]` | 抄 8 值（只作记录） | ____ |
| `g_fb_ccnt_read_cyc` | 抄值 | ____ |
| 布局哨兵（同一 build 同一次跑）`g_fira_f4_pass` / `g_f5_pass_all` | 1 / 1 | ____ / ____ |
| （若链接探针）`g_s7_fg_pass_all` | 1 | ____ |

### 表 D —— 每帧墙钟 cycle（8 路合计；统计帧 = 第 4–1023 帧）

路径下标：0 `FIRA_T8`、1 `FIRA_T1`、2 `FIRA_P1`、3 `CORE_C`、4 `CORE_SYM`；抽头下标：0 = 63、1 = 127、2 = 255。`g_fb_io1` 在核路径上恒为 −2（不适用）。

| 路径 | 抽头 | `cyc_last` | `cyc_max` | `cyc_min` | `frames`（应 1020） | `rc`（应 0） | `io1`（FIRA 应 1） | `pass_all` | `usable` |
|---|---|---|---|---|---|---|---|---|---|
| FIRA_T8 | 63 | | | | | | | | |
| FIRA_T8 | 127 | | | | | | | | |
| FIRA_T8 | 255 | | | | | | | | |
| FIRA_T1 | 63 | | | | | | | | |
| FIRA_T1 | 127 | | | | | | | | |
| FIRA_T1 | 255 | | | | | | | | |
| FIRA_P1 | 63 | | | | | | | | |
| FIRA_P1 | 127 | | | | | | | | |
| FIRA_P1 | 255 | | | | | | | | |
| CORE_C | 63 | | | | | | −2 | | |
| CORE_C | 127 | | | | | | −2 | | |
| CORE_C | 255 | | | | | | −2 | | |
| CORE_SYM | 63 | | | | | | −2 | | |
| CORE_SYM | 127 | | | | | | −2 | | |
| CORE_SYM | 255 | | | | | | −2 | | |

符号：`g_fb_cyc_last[p][t]`、`g_fb_cyc_max[p][t]`、`g_fb_cyc_min[p][t]`、`g_fb_frames[p][t]`、`g_fb_rc[p][t]`、`g_fb_io1[p][t]`、`g_fb_pass_all[p][t]`、`g_fb_usable[p][t]`。

### 表 E —— 逐通道 golden 旗（`g_fb_pass[p][t][0..7]`，按通道 0→7 抄成 8 位，如全过写 `11111111`）

| 路径 \ 抽头 | 63 | 127 | 255 |
|---|---|---|---|
| FIRA_T8 | ________ | ________ | ________ |
| FIRA_T1 | ________ | ________ | ________ |
| FIRA_P1 | ________ | ________ | ________ |
| CORE_C | ________ | ________ | ________ |
| CORE_SYM | ________ | ________ | ________ |

任一格不是 `11111111` → 把该格对应的 `g_fb_crc[p][t][0..7]` 八个值全部抄下（诊断用）：

| 路径 / 抽头 | `g_fb_crc[p][t][0..7]` |
|---|---|
| ____ / ____ | ________ |

golden 对照（`fb_goldens.h`，[L2 host]，PM 核对用，测试员不必比）：63 抽头 `407C61FA 02648ED2 F638EB38 29B3B51A 3F36D7E3 4BFDD6B4 DB88122B A8F9415F`；127 抽头 `55E4C89C A3736944 8BABD4CE 18EC6E13 4B1E1B22 FAD896E7 D40F6375 0F9DADE0`；255 抽头 `51AA2611 FD21C3CA 736BC676 77310752 80C34462 CD255C36 18FE58DC 295BA20B`。

## 7. 什么算有效

- **某一格（路径 × 抽头）的 cycle 只有在该格全部 8 个 golden 旗都 = 1 时才算数**，同时要求该格 `rc = 0`、`frames = 1020`、（FIRA）`io1 = 1`。`g_fb_usable[p][t] = 1` 就是这几条的合取（外加 chirp 与该档系数表自检通过）。**usable ≠ 1 的格，cycle 一律作废**，不得引用、不得"参考"。
- **全局门**：`g_fb_valid = 1`、`g_fb_chirp_ok = 1`、`g_fb_coef_ok[0..2]` 全 1、布局哨兵 `g_fira_f4_pass = g_f5_pass_all = 1`。任一不满足 → 整次读数作废，报 PM。
- **负控制**：`g_fb_neg_fail_all` 必须 = 1。若 = 0（占位系数居然中了 golden）→ 比对机制本身坏了 → **BLOCKER，全部作废**，立即报 PM。
- **时钟**：表 B 三个寄存器缺任一 → 读数可存档，但 PM 不出帧预算判定（RULINGS-03：实测 CCLK 未回来前条件不满足）。
- **放置（PM 判）**：PM 用表 A2 的地址对照同一 build 的 `.map` memory segment，判定每个关键数据在 L1 块还是 L2（可缓存）。任一关键数据在 L2 → 这次 build 的全部 cycle 标注「[L1 bench，数据在 L2（可缓存）]」，不得与全部在 L1 的读数混用或直接比较；核路径的 cyc/MAC 与 FIRA 的 DMA 时间都受放置一阶影响。FIRA 路径的输入缓冲只有落在可缓存区时，[ASSUME FLUSH-IN] 才真正被检验到；落在 L1 时这条假设没有被检验，须照实写明。缺 `.map` 或缺地址读数 → 读数存档，PM 暂不出判定。

## 8. 故障分流（按顺序排查，每次改 build 都重抄表 A）

| 现象 | 处置 |
|---|---|
| `g_fb_open_rc ≠ 0` | FIRA 驱动未进 build 或设备被占：确认 `adi_fir*.c` 在编译列表（FIRA_IMPL.md F2 第一件必查）；报 PM |
| FIRA 某格 `rc = 3/4/5` | CreateTask / FixedPointEnable / QueueTask 返回错误：抄 rc，报 PM |
| FIRA 某格 `rc = 7` | 自旋超时（DONE 未到）：抄表，报 PM；不要在循环里加断点排查 |
| **只有 P1** 不过（T1、T8 过） | 加 `FIRBENCH_P1_FXD_EACH` 重编重跑一次：过了 → 定点模式不跨次保持（记录）；仍不过 → [ASSUME P1-IDX]（硬件回写索引）被证伪，P1 行作废，用 T1 行。两次都抄全表 |
| T1 与 P1 都不过、T8 过 | 首要怀疑 8 路共用一个输入缓冲（[L4]）：抄全表报 PM（本包暂无每路独立输入的变体） |
| FIRA 三路全不过、核两路全过 | 加 `FIRBENCH_FLUSH_IN` 重编重跑一次（核写入的输入在 DMA 读之前显式写回）；仍不过 → 抄全表 + 失败格的 `g_fb_crc`，报 PM |
| FIRA 某格 `io1 = 0` | 输出没写满或越界写到保护字：该格作废，报 PM |
| 核路径不过 | 算法/编译问题（核路径不依赖加速器）：抄失败格 CRC，报 PM；此时其余格也先不采信 |
| li1040 链接溢出 | 停，报 PM（放置改动须另走门） |
| T8 与 T1 不过、P1 过 | 本包已按 `fira_tree.c` 的做法在每次调用时重建 CHANNEL_INFO（即使驱动回写调用方的 CHANNEL_INFO，也不会带进下一帧），这个组合不在预期内：停，抄全表（含失败格 `g_fb_crc`）原样发回，不自行改 build 重跑 |
| `g_fb_neg_fail_all = 0` | BLOCKER（§7） |
| 本表没有列出的任何其他失败组合或现象 | 停，抄全表（含失败格 `g_fb_crc`）并用原话描述现象，原样发回；不自行改 build、不反复重试 |

## 9. PM 判读（测试员不必做）

1. **时钟**：按 RULINGS-03 从表 B 解码 `fPLL = (CLKIN/(DF+1))×MSEL`、`CCLK = fPLL/CSEL`（MSEL=0→128，CSEL=0→32；PLLEN=0 或 PLLBP=1 → CCLK=CLKIN），过数据手册三道合理性门（SYS_CLKIN0 20–30 MHz、fPLL 1.20–2.00 GHz、fCCLK 400–1000 MHz）。与 `g_fb_cclk_hz` 不一致 → BLOCKER，先按时钟比折算排查。
2. **帧预算**：`budget_cyc = CCLK_CGU × 64 / 48000 = CCLK_CGU / 750`（不假设 1 GHz）。
3. **每个 usable 格**（只用 usable = 1 的格）：
   - FIR 占帧比 `U = cyc_max / budget_cyc`，FIR 单项余量 `1/U` [L1 推导]；
   - 等效 cyc/MAC `= cyc_max / (8 × ntaps × 64)` [L1 推导]。核路径（CORE_C / CORE_SYM）是**本台架构建设置下的可移植 int64 C**，不是核能做到的最好实现（没有测原生 MR/SIMD 写法，也没有测库函数 FIR）：它的 cyc/MAC 只能检验"30–50 cyc/MAC 规则对这种可移植 C 写法是否成立"，**不能单凭它得出"核上不可行"的结论**。FIRA 路径的这个值是"核墙钟（含忙等）/MAC"，不是加速器内部效率；
   - 三档抽头做 `cyc_max ≈ a + b·ntaps` 线性拟合：`a` = 每帧固定开销，`b` = 每抽头成本 [L1 推导，三点拟合]；外推到其他长度（如卷入校准滤波器后）= [L3 on L1]，须注明。
4. **最佳组织**：128 档取 usable 的 FIRA 路径中 `cyc_max` 最小者；同时给出 T8（与 M2 今天每段一任务的写法同构）作为上界对照。
5. **系统口径（有条件；PM 出，CTO 裁）**：每通道 FIR 取代 M2 帧循环里的 w/ana/syn 三段（tx 段不变）。把台架 FIR cycle 与 M2 分段读数相加减（`M2_new ≈ M2_beam − (seg_w + seg_ana + seg_syn) + FIR_cyc_max`），**只在下列条件全部满足时才允许**：
   - (a) **同一优化配置**：台架 build（表 A；F0 那次记载为 `-O -Ov=100`，`FIRA_IMPL.md:72`）与 M2 build（`m1_cces_project` 的 Debug 配置，其 `-O` 实际取值未核实，`S7_B63_WALLCLOCK_GAP.md:38-41`）的优化选项逐项相同，而且两边的优化选项原文与构建指纹（`.map`、源文件 md5、Defined symbols）都已记录在案；
   - (b) **S-B / B6.3 已有结论**：台架与 M2 同口径墙钟的 1.79× 差距（`S7_B63_WALLCLOCK_GAP.md:19`，[L1-derived]）已由对照 build 解释或消除；
   - (c) **M2_SEG_CYC 读数已实际回收**：截至本单，S-B 尚未执行，**这些读数还没有回收**；
   - (d) 两边用同一 CCLK 口径（第 1 步）。

   任一条不满足 → **只报 FIR cycle 对帧预算**（第 3 步的 `U = cyc_max / budget_cyc`），**不与 M2 分段读数拼接**。条件全部满足后：台架没有 SPORT DMA / RX ISR 争用，须注明并按 H2 口径另加；再与 `budget_cyc` 比，按 T2 ≥ 1.5×（DEC-S4-CRITERION-01-FINAL，带闭合条件）判。**任何余量数字都必须与 DEC-S4-C9-RELEASE-01 规定的"§8 未计入清单"（43–379 MCPS，`sprint4/dsp/fira/R14_RULING_PROPAGATION.md:58`；不是本单第 8 节）连体呈现**，不得单独示人。本单不预设 FIR 在帧预算里的分配额度。
6. **口径纪律**：本台架的 cycle 是墙钟口径（含 FIRA 忙等），不得与争用 ledger 或纯核理想 MMAC 口径相互比较、互称"矛盾/达标"（R27/R42）。max 是 1020 个热帧里的最大值，**不是完整 WCET**（真冷 cache 未测）。
7. **本台架的盲区（critic R3d A-7，列为 TODO）**：① 所有系数集都严格对称，所以抽头顺序 / 数据方向看不出来（桌面把抽头反序的变异照样 PASS，[L2 emulated]）；② 只落在累加结果 bit 15 以下、且没有进位越过 `>>15` 截断边界的误差看不出来（桌面让加速器丢掉低 15 位的变异照样 PASS，丢掉 bit 15 则被抓到，[L2 emulated]）；③ 本激励不触发饱和（生成器统计 0 次），饱和路径没有被检验。因此本台架的结果**不得作为非对称系数、或卷入每台校准后的系数集的 [L1] 依据**；抽头方向探针（非对称系数）与饱和激励留作 TODO。

## 10. 回传清单

- [ ] 表 A、A2、B–E 全部填写（空格写"未读"，不留白）
- [ ] 本次 build 的 `.map`（文件名与 md5 同表 A）与编译器优化设置截图 `opt_FB.png`
- [ ] 若按第 3 步第 4 条直接改过仓库里的 `bench_main.c`：已执行 `git checkout --` 还原，附 `git status` 原文
- [ ] `cgu_FB.png`
- [ ] Expressions 窗口截图：`g_fb_cyc_max`、`g_fb_pass_all`、`g_fb_usable` 三个数组展开各一张
- [ ] 若走了第 8 节任何一次重跑：每次重跑各一套表 A、A2、C、D、E 和对应的 `.map`
- [ ] 异常现象的原话描述（何时、哪一步、看到什么）

---
*S7_FIRBENCH_RUNBOOK · dsp-algorithm · 2026-09-27 · 零板上预期读数；桌面结果见 `sprint7/dsp/firbench/README.md` §4 [L2]。*
