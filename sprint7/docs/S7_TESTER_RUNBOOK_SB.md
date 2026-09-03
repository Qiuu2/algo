# S7 板测会话 S-B 测试员执行单 —— B6 数值门基座（`M2_SELFTEST` 八锚自检 / 6 宏指纹 / `#error` 守卫 / 三段括号）

> **给谁**：板测测试员（非 DSP 专家）。照本单顺序做完 4 个 build，把读数表原样回填、发回，**不判读、不猜、不改代码**。
> **依据**：DEC-S7-RULINGS-01 D3（CTO_OK=1）+ DEC-S7-IMPL-01 第 2 项 / 第 1 项 c（`sprint2/docs/decisions_log.md` 末尾）；`sprint7/docs/S7_VERIFICATION_PLAN.md` §6 B6-4/5/6/7、§7 S-B、§0.3/§0.4/§0.5。
> **配套**：`sprint7/docs/S7_B63_WALLCLOCK_GAP.md`（B6.3 墙钟差距；**Release / −O 对照 build 的步骤在那边**，本单只管下面 4 个 build；两单可同一次上板会话做完，读数表互相引用）。
> **状态**：本单所有"期望值"来自桌面 golden 与 host harness（**[L2]**），板上读数回填后才是 **[L1]**。凡"留空"的格子，**PM/DSP 不替补数字**（DEC-S7-IMPL-01 硬约束）。
> **编译门 = 你的 CCES build**（本机 cc21k 无 license，DEC-S7-RULINGS-01 D14）：任何编译报错原样截图发回。

---

## 0. 本次要交付什么（一句话）

4 个 build（M2 基线 / +自检+括号 / +自检负控制 / 无宏 M1）各一份：**Defined symbols 截图 + Console 编译行截图 + 改名 `.map` + 读数表 A/B/C 原值 + 听感一行话**。任一 FG 不绿 = 隔离发回，不抢救。

---

## 1. 准备（一次性）

0. **板与 JTAG 顺序、BMODE（C10）**：BMODE0/1/2 全拨 0（No boot）；**先插 JTAG（板断电）→ 板上电 → 仿真器接 USB**，禁热插拔；结束**先 disconnect 再断电再拔**；ICE Test 5 步全过再 Load。全文按 `sprint3/audit/BENCH_OPS_CARD.md:26-29` 与 `sprint3/audit/ezkit_bringup_checklist.md:100-104,134`（`sprint6/STAGE4_BRINGUP_CHECKLIST.md` 为教训清单，不含上电顺序原文），本文不重述其余项。
1. **`git pull`**（若报 `local changes would be overwritten` → **原样发回**，等 stash 指令，**不要 reset**），然后在仓库根执行并把两行输出抄进回填模板 §5 顶部：
   ```
   git log -1 --oneline
   git status --short sprint6/dsp/audio/m1_cces_project/src
   ```
   第二条应为空（源码干净）。不为空 → 停，发回。
2. **确认工程是"就地导入"**（不是 Copy projects into workspace，R52 stale-build 陷阱）：右键 M1_Loopback → Properties → Resource → Location 应指向你 checkout 里的 `.../sprint6/dsp/audio/m1_cces_project`。不是 → 按 `M1_CCES_IMPORT_GUIDE.md` §导入 步骤 5 重新就地导入。
3. **加 1 个 include 目录（本轮新增，一次加好永久留着，无害）**：
   Properties → C/C++ Build → Settings → SHARC C/C++ Compiler → Preprocessor → Additional include directories（或 C/C++ General → Paths and Symbols → Includes，同一处）→ Add → 填**你自己 checkout 的绝对路径**（`${repo}`、相对路径都不解析，R52）：
   ```
   <你的checkout绝对路径>/sprint4/dsp/core_only/bench
   ```
   （给 `M2_SELFTEST` 解析冻结的 `chirp_input.h`，256 KB 只读表。）**Debug 与 Release 配置各加一次**（两份配置的 include/宏是独立的，fw 审计 §7.5）。
   上周已加的三个 include 目录（`sprint4/dsp/fira`、`sprint4/dsp/core_only/src`、`sprint4/dsp/core_only/include`）和三个 linked source（`fira_tree.c` / `tree_filterbank.c` / `tfb_8ch.c`）**保留不动**；若提示 `resource already exists` 跳过即可。
4. **宏在哪里加/删**：Properties → C/C++ Build → Settings → SHARC C/C++ Compiler → Preprocessor → Defined symbols（**Debug 配置**；若做 B63 单的 Release 对照，Release 那份要单独加）。`M1_TARGET_BOARD` / `TARGET_SHARC` 两个是工程自带的，**永远不要动**。
5. **功放断电**（或音量最小）。每个新 build 首跑都断电（§0.5 功放安全）。
6. 准备好 1B 用过的立体声音乐源，整个会话都放着。

---

## 2. Build 矩阵（按 B0 → B1 → B2 → B3 顺序做；B3 同时就是"恢复到无宏"）

| build | Defined symbols（除工程自带两个外，**只能**是这些） | 目的 | 预计 Run 时长 |
|---|---|---|---|
| **B0** M2 基线 | `M2_FIRA_INLOOP=1` `FIRA_USE_REAL_ADI_FIR_HEADER` | 重现 1B 全表 + 新增 `g_m2_beam_cyc_min` + 指纹基线 | ≥10 s |
| **B1** 自检 + 括号 | B0 的两个 + `M2_SELFTEST=1` `M2_SEG_CYC=1` | 八锚自检正控制 + 三段括号读数 | ≥20 s（自检占开头几秒） |
| **B2** 自检负控制 | B0 的两个 + `M2_SELFTEST=1` `M2_SELFTEST_NEGCTRL=1`（**不要** `M2_SEG_CYC`） | 证明自检真依赖权重（必须 rc=7） | ≥20 s |
| **B3** 无宏 M1 | **一个都不加**（把 B0/B1/B2 加的全部删掉） | 指纹负控制（全 0）+ 恢复工程状态 | ≥10 s |

**与 `S7_B63_WALLCLOCK_GAP.md` §5.1 臂序的对应（不需要额外 build）**：臂 **0**（Debug 现状、无括号）= **B0** 的 `beam_cyc_min/last/max`（B0 就是"没有 `M2_SEG_CYC`"的 build；若那边要的是"带自检、无括号"的版本，**B2** 的活流读数同样满足——`M2_SELFTEST_NEGCTRL` 只改 init 自检的权重，不碰活流）；臂 **0s** = **B1** 本身（读数直接复用）；臂 **A'/As/B**（勾 `-O` / Release）的宏组合在那边 §5.1，操作在那边 §1.3——做 Release（路径 B）时 **Release 配置要单独加宏和 include 目录**（§1 第 3/4 步）。

**守卫提示**：如果 build 在 Console 里报 `#error "M2_... requires ..."`，那不是代码坏了，是**宏组合填错**（例如只加了 `M2_SELFTEST=1` 没加 `M2_FIRA_INLOOP=1`）。对照上表改宏重 build；把那条 `#error` 截图一并发回（它本身就是 B6-6 守卫生效的证据）。

---

## 3. 每个 build 的固定流程（10 步，四个 build 完全一样）

1. **核对 Defined symbols** 与 §2 该行一字不差 → **截图**（命名 `sym_SB_B<n>.png`）。
2. **Project → Clean… 然后 Build Project**（必须显式 rebuild；不 rebuild 直接 Load = 烧的还是上一个 build）。Console 找到 `m1_loopback_tdm.c` 的编译行，确认里面有本行该有的 `-D...` → **截图**（`console_SB_B<n>.png`）。loader 步报 `FAILED` 但 `Debug/M1_Loopback.dxe` 存在 → 忽略（IMPORT_GUIDE F7）。
3. **`.map` 检查**（`Debug/M1_Loopback.map`，用文本编辑器 Ctrl+F 搜符号名，抄地址进表 M；地址不在下述范围**不要停**，照抄、在备注写 `MAP-异常` 继续跑）：

   | 搜什么 | 哪些 build 有 | 应落在 | 判 |
   |---|---|---|---|
   | `CHIRP_INPUT` | B1、B2 | **L2**：`0x20000000` – `0x200F9FFF`（`mem_L2_bw`） | 在 `0x24xxxx`–`0x2Fxxxx`（L1）= 挤进 Block 了，记 `MAP-异常` |
   | `s_m1_rx_buf` / `s_m1_tx_buf` / `s_m2_fa` | B0、B1、B2 | **L1 Block 1**：`≥ 0x2C0000` 且 `≤ 0x2EBFFF` | 否则记 `MAP-异常`（pin 失效） |
   | `s_seg_in` / `s_seg_out3` / `s_taskMem` | B0、B1、B2 | **L1**（`0x24xxxx`–`0x2Fxxxx`），**不得**在 `0x2000xxxx` | 在 L2 = 记 `MAP-异常`（R57 追加项） |
   | `s_m2_st_core` | B1、B2 | 任意 L1 地址（默认 Block 0），只抄 | — |
   | 链接是否成功 | 全部 | build 成功即栈/堆无溢出（溢出会直接 link 报错） | 报错截图 |

   把 `.map` 复制改名 **`map_SB_B<n>.map`**（保留 .map 后缀）。
4. **Load `.dxe`**（功放断电）。
5. 放音乐 → **一次不间断 Run** 到 §2 的时长 → **Suspend**。
   - B1/B2 的开头几秒在跑自检（SPORT 还没启），`g_m1_rx_block_count` 会晚几秒才开始涨，属正常。
   - Suspend 后若 `g_m1_valid = 0` 且 `g_m2_selftest_rc = -99` 且 `g_m2_selftest_frames` 在涨 → 自检还没跑完，**Resume 再等 15 s 再 Suspend**（计数器可信，只有听感不可信）。
   - PC 停在 fira 自旋里属正常，判死活只看计数器涨不涨（BOARD_TEST_INSTRUCTIONS 红线）。
6. **读表 A（指纹）→ 表 B（既有 M2 门）→ 表 C（新增）**，全部**原值照抄**（Expressions 视图；数组变量输入名字会展开 8 个元素；**右键 → Number Format → Hex** 抄十六进制，抄不到 hex 就抄十进制并注明）。
6b. **读核心时钟寄存器（只在 B0 这一个 build 做一次；CTO 2026-09-03 裁定）**：仍在 Suspend 状态，打开 **Register 视图**（`Window → Show View → Registers`，展开 `CGU0`，读 `CGU0_CTL` / `CGU0_STAT` / `CGU0_DIV` 三个），**或**用 **Memory 视图**（`Window → Show View → Memory`，`New Renderings…` 选 Hex，地址逐个输入下表三个地址，宽度 4 字节）。三个值**原样抄十六进制**进表 D 并**截图**（命名 `cgu_SB_B0.png`）。只读不写；这三个是只读观察，**不要改任何寄存器值**。若 Register 视图里没有 CGU0 分组，就用 Memory 视图按地址读，并在表 D 的 `读法` 里写 `memory_view`。

7. **当场只判两件事**：① 表 A 指纹与该 build 的期望列不符 → **停**，回第 1 步（build 不对，其它读数作废）；② `g_m2_fg_beam_live ≠ 1` 或 `g_m2_overrun_count` 在明显增长 → 隔离，标 `FG-不绿`，照抄发回。其它一律不判。
8. **跑两遍口径**（STAGE4 runbook 红线）：重新 Load → Run → Suspend 再读一遍。快照值（`rc`、指纹、`selftest_*`、`crc`、`pass`）两次要一致；`*_block_count` / `poll_count` / `out_nonzero` / `selftest_frames` 是计数器只看在涨；`*_cyc_last` 每帧变、`*_cyc_max`/`_min` 只看量级。两次都抄进模板（第二遍可只抄快照值 + max/min）。
9. **听感一行话**：功放上电、音量最小 → **重新 Load → 一次不间断 Run → 听** → 写 正常 / 刺耳 / 无声 / 循环卡顿。B1/B2 也要听：自检跑完后活流应与 B0 一样。
10. **恢复**：删掉本 build 加的宏（做 B3 时 = 全部删干净）。include 目录和 linked source 留着无害。

---

## 4. 读数表（期望值列 = 你当场只对表 A 判；其余 PM 判）

### 表 A —— build 指纹（7 个；**每个 build 第一件事就是读它们**）

| 变量 | B0 | B1 | B2 | B3 | 说明 |
|---|---|---|---|---|---|
| `g_m2_fira_inloop` | 1 | 1 | 1 | 0 | 既有指纹 |
| `g_m2_selftest_built` | 0 | 1 | 1 | 0 | 新增 |
| `g_m2_static_txtest_built` | 0 | 0 | 0 | 0 | 新增；读到 1 = 上次会话残留了 `M2_STATIC_TXTEST` |
| `g_m2_stxt_localize_built` | 0 | 0 | 0 | 0 | 新增 |
| `g_m2_chmap_fix_built` | 0 | 0 | 0 | 0 | 新增；读到 1 = 残留了 `M2_CHMAP_FIX`（本轮 S-B 不开它） |
| `g_m2_rx_right_aligned_built` | 0 | 0 | 0 | 0 | 新增 |
| `g_m1_u6_addr_override_built` | 0 | 0 | 0 | 0 | 新增（R55 后本板不需要 override，应恒 0） |
| `g_m2_selftest_negctrl_built` | 符号不存在 | 0 | 1 | 符号不存在 | 仅自检 build 有此符号 |
| `g_m2_seg_w_cyc_last`（**符号可见性**） | 符号不存在 | **可见** | 符号不存在 | 符号不存在 | `M2_SEG_CYC` 无专用指纹（critic-D F-MAJOR-1）：用这个符号存在与否判该臂是否带括号；B0/B2 若可见 = 残留了 `M2_SEG_CYC`，该 build 的 `beam_cyc` 读数作废（33 次 CCNT 读扰动） |

**符号存在性规则**（不是错）：B0/B3 里 `g_m2_selftest_*` 全部找不到；B0/B2/B3 里 `g_m2_seg_*` 找不到；B3 里 `g_m2_overrun_count` / `g_m2_poll_count` / `g_m2_beam_cyc_*` 找不到。"找不到"本身就是该宏没编进去的证据，在表里写 `符号不可见`。

### 表 B —— 既有 M2 板门（B0/B1/B2 都读；B3 读前 4 行 + `g_m1_*`）

| 变量 | 期望（B0/B1/B2） | 期望（B3） | 抄什么 |
|---|---|---|---|
| `g_m1_main_init_rc` | 0 | 0 | 原值 |
| `g_m1_valid` / `g_m2_valid` | 1 / 1 | 1 / 0 | 原值 |
| `g_m2_setup_rc` | 0 | −99 | 原值（≠0 时 B1/B2 的 `g_m2_selftest_rc` 应 = −1） |
| `g_m1_fg_stream_live` / `g_m2_fg_beam_live` | 1 / 1 | 1 / −99 | 原值 |
| `g_m1_rx_block_count` | 持续增长（~750/s） | 同 | 两遍原值 |
| `g_m2_poll_count` | ≈ `rx_block_count` | 符号不可见 | 原值 |
| `g_m2_overrun_count` | ≈ 0 | 符号不可见 | 原值 |
| `g_m2_out_nonzero` / `g_m2_out_max_abs` | > 0 / 不顶在 0x7FFFFFFF | 符号可见但 0 | 原值（hex） |
| `g_m1_nonzero_samples` / `g_m1_max_abs_sample` | > 0 | > 0 | 原值 |
| `g_m2_beam_cyc_last` / `g_m2_beam_cyc_max` | **留空回填**（max 远小于 1,333,333 即可） | 符号不可见 | 两遍原值 |
| **`g_m2_beam_cyc_min`**（新增） | **留空回填**（应 ≤ `_last` ≤ `_max`；仍是 `0xFFFFFFFF` = 一帧波束都没算过） | 符号不可见 | 两遍原值 |

### 表 D —— 核心时钟（**只做一次**，在 B0；PM 判，你只抄）

| 读什么 | 地址 | 抄成什么 | 期望值/判据 |
|---|---|---|---|
| `CGU0_CTL` | `0x3108D000` | `0x________` | 无期望值，只记录（PM 解码出 MSEL/DF） |
| `CGU0_STAT` | `0x3108D008` | `0x________` | 无期望值，只记录（PM 看 PLL 是否旁路） |
| `CGU0_DIV` | `0x3108D00C` | `0x________` | 无期望值，只记录（PM 解码出 CSEL） |
| CLKIN | 不用读寄存器 | 抄 `25000000` | **核心板原理图 V2.1**：25 MHz 振荡器直连 `SYS_CLKIN0`（`knowledge_base/ezkit/vendor_docs/schematics/V2.1/ADSP21569核心板原理图.pdf`）；与工程启动实参 `m1_main.c:44` 一致。**若板上实物晶振不是 25 MHz，抄实际值并写明从哪看到的** |

三个地址出处：CCES 2.12.1 头文件 `SHARC/include/sys/ADSP_2156x_HPC.h`（`REG_CGU0_CTL/STAT/DIV`；`SHARC/include/def21569.h:26` 引的就是这份）。PM 侧用 ADI 电源服务源码 `adi_pwr_2156x.c` 的同款算法解码成 CCLK。这一步**不改二进制、不加代码、不写任何寄存器**，所以不影响任何 build 的读数。

### 表 C —— 本轮新增（B1 / B2）

**C-1 八锚自检**（B1 与 B2 都读；期望值来源 `sprint4/dsp/fira/dolph_f5_goldens.h`，**[L2 桌面 golden]**；host harness 实跑同值，见 §8）

| 变量 | B1 期望（正控制） | B2 期望（负控制，unity 权重） |
|---|---|---|
| `g_m2_selftest_rc` | **0** | **7** |
| `g_m2_selftest_frames` | 8192 | 8192 |
| `g_m2_selftest_pass[0..7]` | 全 1 | `0 0 0 0 0 0 0 1`（只有 [7]=1） |
| `g_m2_selftest_crc[0]` | `0x8E807729` | `0x2E0D8C6E` |
| `g_m2_selftest_crc[1]` | `0xB2F1E13F` | `0x2E0D8C6E` |
| `g_m2_selftest_crc[2]` | `0x7B109C71` | `0x2E0D8C6E` |
| `g_m2_selftest_crc[3]` | `0xD7BD23E7` | `0x2E0D8C6E` |
| `g_m2_selftest_crc[4]` | `0xA000D606` | `0x2E0D8C6E` |
| `g_m2_selftest_crc[5]` | `0x2403E085` | `0x2E0D8C6E` |
| `g_m2_selftest_crc[6]` | `0xB88D91B5` | `0x2E0D8C6E` |
| `g_m2_selftest_crc[7]` | `0x2E0D8C6E` | `0x2E0D8C6E` |
| `g_m2_selftest_crc_core[0..7]` | 与 `crc[]` 同列逐个相等 | 全 `0x2E0D8C6E` |
| `g_m2_selftest_mismatch_sb[0..7]` | 全 −1 | 全 −1 |
| `g_m2_selftest_mismatch_idx[0..7]` | 全 −1 | 全 −1 |
| `g_m2_selftest_cyc` | **留空回填**（原值） | **留空回填** |
| `g_m2_selftest_cyc_ch[0..7]` | **留空回填**（8 个原值） | **留空回填** |

读到别的值 → **不判**，把 `rc` / `pass[]` / `crc[]` / `crc_core[]` / `mismatch_sb[]` / `mismatch_idx[]` 全部原值抄回，PM 据此定位（`crc_core ≠ 锚` 是链前段漂了，`crc ≠ crc_core` 是 FIRA 侧不一致，`mismatch_sb/idx` 给出第一个错的子带和位置）。`rc = −1` = FIRA 没起来（对照 `g_m2_setup_rc`）。`rc = −99` = 没跑（看 §3 第 5 步）。

**C-2 三段括号**（只有 B1；全部**留空回填**，两遍各抄一次；不给任何期望数，量级由 `S7_B63_WALLCLOCK_GAP.md` 判读）

| 变量 | 第 1 遍 | 第 2 遍 | 含义（只为让你知道抄的是什么） |
|---|---|---|---|
| `g_m2_seg_w_cyc_last` / `_max` | | | 8 路加权乘法（含权重下标读取） |
| `g_m2_seg_ana_cyc_last` / `_max` | | | 8 路 `fira_tfb_analyze`（含等加速器） |
| `g_m2_seg_syn_cyc_last` / `_max` | | | 8 路 `fira_tfb_synthesize`（含等加速器） |
| `g_m2_seg_tx_cyc_last` / `_max` | | | 8 路 TX 交织写 + FG 扫描 |
| `g_m2_beam_cyc_last` / `_max` / `_min`（B1 的） | | | 与 B0 的同名读数**不可直接相减**——B1 括号本身每帧多 33 次 CCNT 读 |

---

## 5. 回填模板（复制到回执里逐格填；一个 build 一份）

```
[S-B 回填]  日期____  测试员____  commit(git log -1)____________  git status 干净? __
build: B_   Defined symbols 截图文件名 ______  Console 截图 ______  map 文件名 ______
MAP: CHIRP_INPUT=0x________  s_m1_rx_buf=0x________  s_m1_tx_buf=0x________  s_m2_fa=0x________
     s_seg_in=0x________  s_seg_out3=0x________  s_taskMem=0x________  s_m2_st_core=0x________  备注(MAP-异常?)____
表A: fira_inloop=_ selftest_built=_ static_txtest_built=_ stxt_localize_built=_ chmap_fix_built=_
     rx_right_aligned_built=_ u6_addr_override_built=_ selftest_negctrl_built=_/不可见   seg_w_cyc_last 可见?(是/否)=_   与期望列一致? __
表B(第1遍/第2遍): main_init_rc=_/_ m1_valid=_/_ m2_valid=_/_ setup_rc=_/_ fg_stream_live=_/_ fg_beam_live=_/_
     rx_block=______/______ poll=______/______ overrun=____/____ out_nonzero=______/______ out_max_abs=0x______/0x______
     m1_nonzero=______ m1_max_abs=0x______ beam_cyc_last=______/______ beam_cyc_max=______/______ beam_cyc_min=______/______
表C-1(B1/B2): rc=__ frames=____ pass=[_ _ _ _ _ _ _ _]
     crc     =[0x________ 0x________ 0x________ 0x________ 0x________ 0x________ 0x________ 0x________]
     crc_core=[0x________ 0x________ 0x________ 0x________ 0x________ 0x________ 0x________ 0x________]
     mismatch_sb=[_ _ _ _ _ _ _ _]  mismatch_idx=[____ ____ ____ ____ ____ ____ ____ ____]
     selftest_cyc=__________  cyc_ch=[________ x8]
表C-2(B1, 第1遍/第2遍): seg_w last/max=______/______ | ______/______   seg_ana=______/______ | ______/______
     seg_syn=______/______ | ______/______   seg_tx=______/______ | ______/______
表D(只在 B0 填一次): CGU0_CTL=0x________  CGU0_STAT=0x________  CGU0_DIV=0x________
     CLKIN=__________ Hz（默认 25000000；不同则写出处：______）  读法: register_view / memory_view  截图: cgu_SB_B0.png
听感（重新 Load 后一次不间断 Run）：正常 / 刺耳 / 无声 / 循环卡顿 ：______
异常/卡住/报错（原样贴）：______
```

---

## 6. 红线（务必遵守）

- **不改代码、不改寄存器、不改 `.cproject`**——只按 §2 表加/删宏；wrong 了就改宏重 build。
- **不 commit、不 push、不 reset**。GUI 加宏/加 include 会让本地 `.cproject`/`.project` 变脏，这是**设计如此、永不提交**；若你被要求提交别的东西，先 `git checkout -- sprint6/dsp/audio/m1_cces_project/.cproject sprint6/dsp/audio/m1_cces_project/.project` 再说；`git pull` 冲突 → 原样发回，不自行处理。
- **不下断点**；只 Run → Suspend → idle 读；PC 停在 fira 自旋里正常。
- **Suspend 后的音频不可信**：要听必须重新 Load、一次不间断 Run。
- **任一 FG 不绿（`g_m1_fg_stream_live` / `g_m2_fg_beam_live` ≠ 1、`overrun` 涨）= 隔离**：照抄发回、标记、**不抢救不重试**（可以做下一个 build）。
- **指纹不符期望 = 那个 build 的所有读数作废**，回 §3 第 1 步；不要"顺手"抄下去。
- **数字只抄不算**：所有 `*_cyc_*` 原值回填，换算/判读是 PM 的事（C9，raw only）。
- 功放：每个新 build 首跑断电；表 B `g_m2_out_max_abs` 不顶在 `0x7FFFFFFF` 附近才上电听。
- 读数怪 / build 报错 / 卡住 → **原样发回停手等回话**。
- 会话结束前把工程恢复到 **B3 状态（无宏）**——宏会跨会话残留（R52）。

---

## 7. 发回清单（发 CTO 中转 PM）

- [ ] §1 的两行 git 输出
- [ ] 4 个 build 各：`sym_SB_B<n>.png`、`console_SB_B<n>.png`、`map_SB_B<n>.map`
- [ ] 4 份 §5 回填（B1/B2 含表 C）
- [ ] 若出现过 `#error`：那条 Console 截图 + 当时的 Defined symbols 截图（守卫证据）
- [ ] 表 D（三个 CGU 原值 + CLKIN）与 `cgu_SB_B0.png`
- [ ] 听感 4 行
- [ ] 若同会话做了 `S7_B63_WALLCLOCK_GAP.md` 的对照 build：那边的回填单一起发，并注明它用的 Defined symbols（应与 B1 相同）

---

## 8. 附：期望值从哪来、L 级怎么定（PM/critic 看；测试员可跳过）

- **八锚**：`sprint4/dsp/fira/dolph_f5_goldens.h:57-66`，由 `gen_f5_goldens.c` 用冻结核 `tree_filterbank.c` 在桌面生成，**[L2]**；F5 上板 commit `44a99e8` 已证 FIRA 八路逐位同 **[L1]**。`M2_SELFTEST` 的定义与 F5 完全一致（同权重表达式、同 `fira_channel_init(…,64)`、同 CRC32 多项式/初值/终值/字节序、同 sb0|sb1|sb2|sb3 流式顺序、同三项 PASS 判据），**权重下标 = 通道下标，不经 chmap**（自检验的是链不是映射）。
- **负控制 B2 的期望 rc=7 / 全 `0x2E0D8C6E`**：与 `gen_f5_goldens.c -DF5_GEN_UNWEIGHTED` 的 FG1 双保险同源（unity 权重下 8 锚坍缩到 F4 单通道锚），host harness 实跑复现（下）。
- **host harness**（`sprint7/dsp/host/s7_selftest_host.c` + `run_s7_host_checks.sh`，gcc 11.4，**[L2 host]**）2026-09-02 实跑摘要：
  ```
  MODE pos          rc=0  crc[0..7] = 8E807729 B2F1E13F 7B109C71 D7BD23E7 A000D606 2403E085 B88D91B5 2E0D8C6E  8/8 PASS
  MODE neg-unity    rc=7  crc[0..7] 全 = 2E0D8C6E, 只有 c=7 PASS                                            (== B2 期望)
  MODE neg-reverse  rc=8  crc[c] == golden[7-c]（判据对权重下标敏感）
  MODE neg-chmap    rc=8  crc[c] == golden[perm[c]]（自检若套 chmap 会因映射而非链失败）
  MODE neg-stub     rc=8  零填充占位器件全 FAIL，mismatch_sb=0 idx=1，crc_core 仍 == 锚 (FG2)
  MODE neg-sb2flip  rc=8  第 100 帧 sb2[0] 翻 1 bit -> mismatch_sb=2 idx=3200（定位链路有效）
  -O0+UBSan 的 pos 与 -O2 的 8 行 CRC 逐字节同（整数链与优化等级无关 [L2 host]；这是 B63 单里 Release 对照 build 不改 bit-exact 的前提）
  ```
- **guard-check 矩阵**（`sprint6/dsp/audio/run_guard_check.sh`，gcc `-fsyntax-only`，**[L2 gcc 代理，仅编译通过]**）：10 个编译配置 PASS（含 G `+SELFTEST`、H `+SELFTEST+SEG_CYC`、I `+SELFTEST+NEGCTRL`、J 全开+chmap）+ 5 个证伪配置按预期被 `#error` 拒绝（X1 只定义 `M2_STATIC_TXTEST=1`、X2 只定义 `M2_SELFTEST=1`、X3 `STXT_LOCALIZE` 无 `STATIC_TXTEST`、X4 `NEGCTRL` 无 `SELFTEST`、X5 只定义 `M2_SEG_CYC=1`）。
- **默认字节等同**（`sprint7/dsp/host/run_s7_preproc_equiv.sh`，`gcc -E -P` 对 HEAD 比对）：M1 宏集差异 = 6 个指纹（12 行：6 extern + 6 定义）；默认 M2 宏集差异 = 6 指纹 + `g_m2_beam_cyc_min`（定义、extern、setup 里复位、poll 里更新，共 16 行）；其它 4 个既有可选宏集同样只有这 16 行。`m1_main.c` 未改。
- **板上 [L1] 结论只由本单回填产生**；本单不含任何板上数字。
- **cyc 类读数一律留空**（`selftest_cyc`、`cyc_ch`、`seg_*`、`beam_cyc_min/last/max`），口径见 `m1_loopback_tdm.c` 各符号定义处注释与 `S7_VERIFICATION_PLAN.md` §0.4；`g_m2_selftest_cyc` 是 32 位，若小于 `cyc_ch[0..7]` 之和说明回绕过 2^32（4.29 s@1 GHz），以 `cyc_ch` 求和为准（PM 算）。
- **`CHIRP_INPUT` 落 L2**：源码 `#pragma section("seg_l2_dmda_bw")` 紧接 `#include "chirp_input.h"`（ADI POST 例程同名段 [L1 例程]，`m1_app.ldf` `dxe_l2_data_bw > mem_L2_bw`）；这是**源码侧假设、`.map` 是证明**——若表 M 显示不在 L2，PM 改用 `#pragma default_section` 包裹后再发一次 build（不需要测试员改代码）。

## 9. 关联文件

- 改动包：`sprint6/dsp/audio/m1_cces_project/src/m1_loopback_tdm.c` / `.h`（`m1_main.c` 未改）；`sprint6/dsp/audio/run_guard_check.sh`
- host 侧：`sprint7/dsp/host/s7_selftest_host.c`、`run_s7_host_checks.sh`、`run_s7_preproc_equiv.sh`
- 上板流程与既有表：`sprint6/BOARD_TEST_INSTRUCTIONS.md`（1A/1B）、`sprint6/STAGE4_TESTER_RUNBOOK.md`（红线/哨兵）、`sprint6/dsp/audio/m1_cces_project/M1_CCES_IMPORT_GUIDE.md`（导入、M2 接线、F1–F7）、`sprint6/STAGE4_BRINGUP_CHECKLIST.md`（上电/JTAG 顺序）
- 配套：`sprint7/docs/S7_B63_WALLCLOCK_GAP.md`（Release/−O 对照 build + 括号读数判读）、`sprint7/docs/S7_VERIFICATION_PLAN.md` §6/§7

*dsp-algorithm teammate @ claude-fable-5-1，2026-09-02。未 commit；待独立 critic §12（FG1/FG2/IO1/IO2/ST1-E）过门与 CTO-gated commit。*
