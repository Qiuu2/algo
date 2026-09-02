reviewer: critic @ claude-fable-5-1 / 2026-09-03

# CRITIC-D verdict — 包 1（D3 M2 TU 改动包 + S-B runbook）/ 包 2（S7_POLARITY_QA_RUNBOOK.md）

> 只读审计；未改/未暂存/未提交仓库任何文件；未 spawn 子 agent。复算脚本与日志全部在 scratchpad（§3）。
> 审计对象 = 工作树未暂存改动 + 未跟踪新文件（`git status` 见 §1.2 第 10 条）。HEAD = `c9c3f91`。

---

## 1. 包 1 —— D3 固件改动包（CTO_OK=1）+ `S7_TESTER_RUNBOOK_SB.md`

### 1.0 总裁定：**CONDITIONAL**（0 BLOCKER / 1 MAJOR / 2 MINOR / 6 INFO）

一句话：代码本体（5 个 `#error`、6 指纹、`M2_SELFTEST` 八锚、`M2_SELFTEST_NEGCTRL`、`M2_SEG_CYC` 四段括号、`g_m2_beam_cyc_min`）经我亲自实跑三套检查 + 逐项对 F5 定义，**未发现代码级缺陷**；§12 五门全过；默认字节等同实证成立。唯一 MAJOR 在 runbook 侧：新宏 `M2_SEG_CYC` 没有指纹、表 A 没有它的行，而配套的 B63 文档引用一个**不存在**的符号 `g_m2_seg_cyc_built`——上板会话会因此卡住或让某臂读数无据可判。修完 MAJOR（纯文档改动即可，不扩 D3 范围）→ delta 复审可 PASS，进入 CTO-gated commit。

### 1.1 Findings 表（包 1）

| ID | 严重度 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| F1-MAJOR-1 | **MAJOR** | `S7_TESTER_RUNBOOK_SB.md` §4 表 A（:82-95）、§5 模板（:153-171）；`m1_loopback_tdm.c:245-265`；`S7_B63_WALLCLOCK_GAP.md:103,204,294` | `M2_SEG_CYC` 是本包新增的可选宏，**没有运行时指纹**（6 指纹 = RX_RIGHT_ALIGNED/CHMAP_FIX/STATIC_TXTEST/STXT_LOCALIZE/SELFTEST/U6，NEGCTRL 只在 SELFTEST 下），表 A 无其行，§5 模板无其槽；只在表 A 下方一段散文里说「B0/B2/B3 里 g_m2_seg_* 找不到…在表里写符号不可见」，但测试员「当场只判表 A」。同时 B63 文档 §4 表与 §5.2 勾选项要求「第一个读 `g_m2_seg_cyc_built` 与该臂一致」——该符号在本包里**不存在**，B63 又写「名称以 s7-base 定稿为准」，s7-base 却没定稿。后果：(a) 跨会话残留 `M2_SEG_CYC=1` 进 B0/B2 时无强制记录，B0 的 `beam_cyc` 基线被 33 次 CCNT 读扰动却当纯基线用（B63 臂 0 直接复用 S-B B0）；(b) 测试员按 B63 找不到符号 → 按「指纹不符=读数作废」处理，整臂丢失。这正是 fw 审计 9.H / B6-5 要堵的 R52 类洞。 | **不扩 D3 范围的最小修（推荐）**：表 A 加一行「`g_m2_seg_w_cyc_last` 符号可见性：B0 不可见 / B1 可见 / B2 不可见 / B3 不可见」并纳入「当场必判」；§5 模板加 `seg_sym=可见/不可见`；请 lead 让 B63 把 `g_m2_seg_cyc_built` 改成同一存在性判据。**备选（须 CTO 明示扩 1 个指纹）**：M2 侧加 `volatile int g_m2_seg_cyc_built = M2_FP_SEG_CYC;`（`#if M2_FIRA_INLOOP` 内），同步更新 `run_s7_preproc_equiv.sh` 的 allow-list、表 A、B63。 |
| F1-MINOR-1 | MINOR | `S7_TESTER_RUNBOOK_SB.md` §1.1（:19-24）、§1.3-1.4、§6（:177-185） | 缺「不 commit / 不 push / 不 reset git」红线（包 2 有，本单没有）。§1.3 让测试员在 GUI 加 include 目录、§1.4 在 GUI 加 Defined symbols——CCES/Eclipse 把这两项**写进本地 `.cproject`**，与 §6「不改 `.cproject`」字面冲突，测试员会困惑；§1.1 的干净检查只查 `src/`，看不到 `.cproject` 漂移；`git pull` 若报 `local changes would be overwritten` 无处置。 | §6 加：「不 commit、不 push、不 reset；本地 `.cproject`/`.project` 因 GUI 加宏/加 include 而显示 M 属预期、**永不 commit**；若要提交任何东西先 `git checkout -- sprint6/dsp/audio/m1_cces_project/.cproject .project`」；§1.1 加「`git pull` 报 local changes → 原样发回、不 reset」（照抄包 2 §2.1-1）。 |
| F1-MINOR-2 | MINOR | `S7_TESTER_RUNBOOK_SB.md` §1（:17-35）、§9（:224） | C10③ 安全硬规矩（断电插 JTAG → 板上电 → 仿真器 USB；禁热插拔；BMODE 全 0）没有写进本单的准备/红线，只在 §9「关联文件」列了 `STAGE4_BRINGUP_CHECKLIST.md`。包 2 §0.3/§7.4 的写法是正确范例。 | §1 准备加一条「上电/JTAG 顺序按 `sprint6/STAGE4_BRINGUP_CHECKLIST.md`（先插 JTAG→板上电→仿真器 USB；严禁带电插拔；BMODE 全 0）」，§6 红线加同一句。 |
| F1-INFO-1 | INFO | `m1_loopback_tdm.c:1023-1024`；runbook §3.3 M 表、§8 末条 | `#pragma section("seg_l2_dmda_bw")` 紧接 `#include "chirp_input.h"`：ADI 例程（`a2b_slave_test.c:33-44`）是 pragma 紧接**定义**；本包依赖「`<stdint.h>` 已被 include guard 吞掉、`#define` 非声明 → 编译器看到 pragma 后第一条声明就是 `CHIRP_INPUT`」。作者已标 BOARD-CONFIRM、runbook M 表要求 `.map` 落 `0x20000000–0x200F9FFF`、备案 `#pragma default_section`。我核 LDF：`seg_l2_dmda_bw` → `dxe_l2_data_bw BW` → `MY_L2_CACHED_MEM`=`mem_L2_bw`（`m1_app.ldf:215,220,1255-1260`），段名存在、映射到 L2、1000 KB 容 256 KB 无挤占问题。 | 无需动作（[ASSUME] 已诚实标注 + 板证路径齐）。 |
| F1-INFO-2 | INFO | `run_guard_check.sh` 配置矩阵 | `M2_STATIC_TXTEST=1 + M2_SELFTEST=1` 组合未入矩阵。读码无冲突（自检在 `m1_loopback_init` 内、静态填充在其后；`m1_main.c:55-64,77-83`），但「应急路径先证编译干净」纪律（R57）下可顺手补一列 K。 | 可选。 |
| F1-INFO-3 | INFO | `m1_loopback_tdm.c:809` | `-Wsign-compare`（`int i` vs `M1_TX_HALF_WORDS`）为既有噪声（fw 审计 9.B 已记，STATIC_TXTEST 填充循环），非本包引入；10 个配置里只有 E/F 出现。 | 随下次 CTO-gated commit 捎带 `uint32_t i`，本包不动。 |
| F1-INFO-4 | INFO | `m1_loopback_tdm.c:246-256`（口径注）、runbook §4 C-2、B63 §3/§4 | tx 括号包含 FG nz/peak 扫描——**已在三处一致声明**（不是「只罩调用本身」，但 tx 段本来不是调用；外层 beam 括号 B0 时本就含该扫描，口径连续）。33 次 CCNT 读扰动 / 「SEG_CYC 版 beam_cyc 不可与 B0 直减」三处一致（.c:255-256 / runbook:146 / B63:241）。 | 无需动作。 |
| F1-INFO-5 | INFO | runbook §3.5、§8 | 自检耗时无板上数字，作者用「开头几秒」措辞。我按 M2 基线 830,903 cyc/帧（8ch analyze+synth [L1]）粗估 analyze 约半 → 8192 次 ≈ 3.4e8 cyc ≈ 0.34 s @1 GHz，加核侧 analyze 与 CRC ≈ 0.5 s 量级 **[L3 估算，仅供判「卡住 vs 没跑完」]**；`g_m2_selftest_cyc` 不会回绕，但保留 `_cyc_ch` 交叉核是对的。 | 无需动作；板上以 `_cyc_ch` 求和为准。 |
| F1-INFO-6 | INFO | runbook §4 表 B（:105,110） | `~750/s`、`1,333,333` 两个口径数未带 L 标/出处（= 48000/64、1 GHz×1.333 ms，均为既定推导值，PLAN §0.4 已用）。 | 加「[推导，PLAN §0.4]」即可。 |

### 1.2 任务书 11 项逐条核实

1. **实跑**（命令与原始日志见 §3）：
   - `run_guard_check.sh`：**OVERALL PASS (10 compile configs + 5 falsifiers)**，exit 0；15 条 PASS 行逐条在（A–F 既有 + G/H/I/J 新增 + X1–X5 被 `#error` 拒绝且诊断含 `#error`）。唯一非 pragma 警告 = :809 既有 sign-compare。
   - `run_s7_host_checks.sh`（gcc 11.4.0）：**OVERALL PASS**，exit 0。pos 8/8、neg-unity rc=7 全 `0x2E0D8C6E` 仅 c=7 PASS、neg-reverse rc=8 且 crc[c]==golden[7−c]、neg-chmap rc=8 且 crc[c]==golden[perm[c]]、neg-stub rc=8 mismatch_sb=0 idx=1 且 crc_core==golden、neg-sb2flip rc=8 sb=2 idx=3200；−O0+UBSan 的 8 行 CRC 与 −O2 逐字节同。冻结件 md5：core `1e88479385c8de7d3107b8c3a34e840a` / chirp `f38270f3b963265129bdf45c34ad2b6f` / goldens `bcb22c89a8f0306c2813164818733463`。
   - `run_s7_preproc_equiv.sh`：**OVERALL PASS**，exit 0。M1 集差异 12 行（6 extern + 6 定义，值全 0）；默认 M2 集 16 行（+`g_m2_beam_cyc_min` extern/定义/setup 复位/poll 更新）；RX_RIGHT_ALIGNED / CHMAP_FIX / STATIC_TXTEST / +LOCALIZE 四集同样 16 行且对应指纹正确为 1；`m1_main.c` 0 diff。
   - **防呆核实**：我把脚本复制到 scratchpad、硬编码 ROOT、**删掉 `-I"$SRC"`** 再跑：STATIC_TXTEST 两集立即 `INVALID: gcc -E failed on the HEAD copy: fatal error: m2_static_txtest_table.h`，**OVERALL FAIL, exit 1**——rc≠0 判 INVALID 的防呆真的在，不会再假 PASS。
2. **F5 同定义**（逐项对 `gen_f5_goldens.c:54-98` / `fira_regression.c:71-81,260-263,328-371` / `dolph_f5_goldens.h`）：加权 `(int32_t)(((int64_t)w*(int64_t)x)>>DOLPH_W8_QBITS)` ✓ 同 `f5_apply_w`；`fira_channel_init(&s_m2_fa[c],(uint16_t)M1_FRAME)`，`M1_FRAME=64u` ✓；每帧 `fira_tfb_analyze` + 冻结核 `tfb_analyze` 并跑 ✓；CRC 多项式 `0xEDB88320` 反射、初值 `0xFFFFFFFF`、终值 `^0xFFFFFFFF`、每 int32 按 LE 4 字节喂 ✓ 与两处逐字符同；拼接顺序 sb0|sb1|sb2|sb3、每帧流式 ✓；权重下标 = `g_dolph_w8_q15[c]` **不经 chmap**（即使 `M2_CHMAP_FIX` 也不套，host neg-chmap 证明套了会因映射 FAIL）✓；chirp = 冻结 `CHIRP_INPUT`（`sprint4/dsp/core_only/bench/chirp_input.h`，同 F5 生成器）✓；`M2_SELFTEST_NFR = 65536/64 = 1024` ✓；判据三项 `(mis<0) && crc==crc_core && crc_core==golden` ✓ 同 :369-371；首错定位 `f*sz[b]+j` ✓ 同 :351。八个期望 CRC 与 `dolph_f5_goldens.h:58-65` 逐位一致，与我 host 实跑一致。`[L1]` 引用 commit `44a99e8`（2026-06-04 F5-A）存在，归档 commit `22b4ef9` 写明「8ch 子带 bit-exact 上板达成 (L1, commit 44a99e8)」，可追溯。
3. **§12**：见 §1.4。补充关键点：selftest 定义在 `#if defined(M1_TARGET_BOARD)&&defined(TARGET_SHARC)` 区内（:1023-1128），桌面分支 `m1_loopback_init` 只置 `g_m2_selftest_rc=-99` 并返回 1（:1211-1215）——桌面**不跑、不假绿**；板上无真 FIRA 头时 `fira_tree_setup` 走 `#else` 返 −1 → `rc=-1` 并 `return 1`（:1167），`g_m1_valid` 保持 0，与无自检 build 的失败路径同语义。插入点：`m2_fira_setup()` 成功后、`m1_sport_init()`（内含 `adi_sport_Enable` :939-940）之前 ✓；`g_m1_valid=1` 仍只在 sport init 之后 ✓。
4. **括号口径（R42）**：四段链式读，`ta` 在循环前一次、每通道 4 次（:540,560,568,574,595）= 33 次/帧，与注释、runbook C-2、B63 §4 三处一致；w 段含 chmap 下标读 + 64 乘 + 循环开销（已声明）；ana/syn 恰好只罩调用；tx 罩交织写 + FG 扫描（已声明，见 F1-INFO-4）；claim / `g_m2_out_*` 累加 / `poll_count` / latch 全在 `m2_beam_poll` 括号外 ✓（:740-762）。`g_m2_beam_cyc_min`：定义 `0xFFFFFFFFu`（:243）、`m2_fira_setup` 复位 `0xFFFFFFFFu`（:956）、`m2_beam_poll` 在 `_last` 之后更新（:752）、桌面 honest-0（:1210）；runbook 表 B 写明「仍是 0xFFFFFFFF = 一帧都没算过」✓。
5. **指纹派生**：`#ifdef` 类（`M2_RX_RIGHT_ALIGNED` :c 两处 `#ifdef`、`M2_CHMAP_FIX` `#ifdef` :507、`M1_U6_TWI_ADDR_OVERRIDE` `#ifdef` `m1_softconfig.c:33`）用 `defined()`；`#if` 值类（`M2_STATIC_TXTEST` :766 与 `m1_main.c:55,77`、`M2_STXT_LOCALIZE` :767 与 `m1_main.c:79`、`M2_SELFTEST`）用 `#if X` ✓——`-DM2_STATIC_TXTEST=0` 会正确读 0。派生只 `#define M2_FP_*`，不 `#define` 被测宏本身 → 既有 `#ifdef` 语义零改变 ✓。6 个指纹定义在两个 build 都有（:220-225，不在 `#if M2_FIRA_INLOOP` 内），M1 build 可读 ✓（preproc M1 集 12 行为证）。
6. **`#error` 守卫**：5 条（:107-121）逻辑各自成立：STATIC_TXTEST→INLOOP、STXT_LOCALIZE→STATIC_TXTEST、SELFTEST→INLOOP、NEGCTRL→SELFTEST、SEG_CYC→INLOOP；X1–X5 实跑各被对应 `#error` 拒绝；无宏默认 build 不受影响（preproc M1 集只有 12 行指纹差异）。
7. **`seg_l2_dmda_bw`**：见 F1-INFO-1。段名在 `m1_app.ldf:1259` 的 `dxe_l2_data_bw` INPUT_SECTIONS 内，输出到 `MY_L2_CACHED_MEM`=`mem_L2_bw`（:220）= `0x20000000–0x200f9fff`（:215）✓；runbook M 表范围一致 ✓；核读 L2 走 cache、只读 const、loader 初始化、无 DMA 触碰 → 无一致性问题 ✓；`#pragma default_section` 备案 ✓（runbook :218）。
8. **默认字节等同**：亲自跑 = 第 1 条；差异只剩声明的行，allow-list 匹配。
9. **runbook S-B**：宏组合表 B0–B3 与 guard 配置 G/H/I 对应 ✓（B1=H、B2=I）；include 目录 = `sprint4/dsp/core_only/bench` ✓ 与脚本 `$BENCH` 同，Debug/Release 各加 ✓；.map 表：CHIRP_INPUT L2 范围 ✓、Block 1 `0x2C0000–0x2EBFFF` ✓（`m1_app.ldf:190`）、`s_seg_*`/`s_taskMem` 须 L1（R57）✓；读数表：指纹 1/0 逐 build ✓（B3 `g_m2_selftest_built` 可见=0、`negctrl_built` 不存在 ✓），`selftest_rc=0`/`frames=8192`/`pass[8]` 全 1 ✓，8 锚十六进制**逐位**同 `dolph_f5_goldens.h` ✓，NEGCTRL rc=7 全 `0x2E0D8C6E` 仅 pass[7]=1、crc_core 全 `0x2E0D8C6E`、mismatch 全 −1 ✓（= host neg-unity）；cyc 类（`selftest_cyc`、`cyc_ch`、`seg_*`、`beam_cyc_last/max/min`）**全部留空** ✓；功放断电顺序 ✓（§1.5/§3.4/§3.9/§6）；FG 不绿即隔离 ✓（§3.7/§6）；`.cproject` 变动处置 ✗ → F1-MINOR-1；B63 引用：现已落盘为未跟踪文件 `sprint7/docs/S7_B63_WALLCLOCK_GAP.md`（与本包同批 commit 即闭合），但两文对 SEG_CYC 指纹名不一致 → F1-MAJOR-1。B3 期望列（`g_m2_setup_rc=-99`、`fg_beam_live=-99`、`out_*` 可见但 0、`poll/overrun/beam_cyc` 不可见）与代码一致 ✓。
10. **硬约束**：`git status --porcelain` = ` M m1_loopback_tdm.c`、` M m1_loopback_tdm.h`、` M run_guard_check.sh`、`?? sprint7/docs/S7_B63_WALLCLOCK_GAP.md`、`?? sprint7/docs/S7_POLARITY_QA_RUNBOOK.md`、`?? sprint7/docs/S7_TESTER_RUNBOOK_SB.md`、`?? sprint7/dsp/`（host/ 3 文件 = 本审；probe/ 9 文件 = 另一 teammate，不在本审）。**冻结件 / `.cproject` / `.project` / `m1_softconfig*` / `m1_main.c` 零变动** ✓（`git diff --name-only` 仅上述 3 文件；脚本亦报 `m1_main.c: 0 diff lines`）。staged 为空。
11. **新增全局入表**：`g_m2_*_built` ×6 + `negctrl_built`（表 A，期望 1/0/不存在）✓；`g_m2_beam_cyc_min`（表 B，留空 + 哨兵语义）✓；`g_m2_selftest_rc/frames/pass/crc/crc_core/mismatch_sb/mismatch_idx`（表 C-1，期望值）✓；`g_m2_selftest_cyc/_cyc_ch`（留空）✓；`g_m2_seg_{w,ana,syn,tx}_cyc_{last,max}`（表 C-2，留空）✓。L 标：期望值 [L2 桌面 golden] / [L2 host] / [L2 gcc 代理]、板上回填才 [L1] ✓；**未替测试员补任何板上数字** ✓。缺：SEG_CYC 存在性行（F1-MAJOR-1）。

### 1.3 C1–C10（包 1）

| 门 | 结论 | 证据 |
|---|---|---|
| C1 | PASS（1 INFO） | 期望值列全带 L 标；`~750/s`、`1,333,333` 未标（F1-INFO-6，推导值） |
| C2 | PASS | 「[L1]」只用于 commit 44a99e8/22b4ef9 已归档的板证；本包所有桌面结果标 [L2]；runbook :6 明写「板上读数回填后才是 [L1]」 |
| C3 | PASS | 无不可逆决策；commit 仍 CTO-gated |
| C4 | N/A | 无 L3 撑强约束（F1-INFO-5 的耗时估算只用于判「卡住」，已标 [L3 估算]） |
| C5 | PASS | 出处逐行可追（gen_f5_goldens.c/fira_regression.c/dolph_f5_goldens.h 行号均核对无误）；八锚由冻结头 + host 独立复跑 + F5 板证三源一致 |
| C6 | N/A | 无几何 |
| C7 | N/A | 无撤回 |
| C8 | N/A | 无外部输入 |
| C9 | PASS | 未把任何加速器收益计入决策；括号读数只作口径说明 |
| C10 | PASS（1 MINOR） | 上电/JTAG 清单存在且经 CTO（`sprint3/audit/ezkit_bringup_checklist.md`、`sprint6/STAGE4_BRINGUP_CHECKLIST.md`），板身份已确认（AD-EXKIT V2.1 + 21569 SOM，fw 9.N）；S-B 单只在 §9 引用未把安全硬规矩写进准备/红线 → F1-MINOR-2 |

### 1.4 §12 逐门（包 1）

| 门 | 结论 | 证据 |
|---|---|---|
| FG1 假绿 | **PASS** | 比对物 = 逐路 4 子带（依赖 FIRA），非端到端；负控制三层：unity 权重坍缩到 F4 锚 `0x2E0D8C6E` 且 rc=7（host 实跑 + 板上 B2 build）、权重倒序/套 chmap 全 FAIL 且 crc 落到对应锚（下标敏感）、sb2 翻 1 bit 定位到 (2,3200) |
| FG2 占位冒充 | **PASS** | 零填充占位器件 host 实跑 8/8 FAIL（mismatch_sb=0 idx=1，crc_core 仍==锚）；桌面路径不跑（rc=−99）；板上 FIRA 未起 rc=−1 且不 arm 流；`fira_tree.c:711-720,753-772` 的 `#else` 占位是「故意错」的 memset 0，不可能 PASS |
| IO1 缓冲契约 | **PASS** | 自检自身：`CHIRP_INPUT` 最大下标 1023·64+63=65535 < 65536 ✓；`s_m2_sb0..3[8/16/32/64]`、`s_m2_xw[64]`、`s_m2_st_csb*[8/16/32/64]` 与 `sz[]` 及清零循环逐一匹配（:488-493,1029-1032,1122-1126）✓；`mismatch_idx` 最大 65535 入 int ✓。FIRA 段级契约（输入 ≥ ntaps+window−1 已初始化 / 恰填 out_count / scratch / cache）在冻结 `fira_tree.c` 内未动：`s_seg_in` 每次调用由 `ch->hist(62)+frame` **完整重组**（:612-655），`s_seg_out3` 只读 FIRA 写入跨度（:429-436）→ 自检留下的残留不会被活流读到 |
| IO2 布局敏感 | **PASS/N.A.** | 本包新增 256 KB L2 常量 + ~2.8 KB Block 0 静态，改变布局；若链对布局敏感，自检本身就是探测器（会 FAIL 并定位），runbook M 表要求 `.map` 证 CHIRP_INPUT 在 L2、`s_seg_*` 在 L1；B0（无自检）布局与 HEAD 同 |
| ST1 流式状态 | **PASS** | 自检把 8 路 `s_m2_fa` 推进 1024 帧后 `fira_channel_init` ×8 复零（:1120-1121，= `m2_fira_setup` 的同一初始化）+ `s_m2_xw/chout/sb0..3` 清零 → 活流首帧从零延迟线起，与无自检 build 等价 |
| ST1-E 消费者枚举 | **PASS** | 自检触碰的可变态及其消费者逐项：① `s_m2_fa[8]`（消费者 `m2_fira_beam_frame`）→ 已复零；② `s_m2_xw/sb*/chout`（每帧被完整重写前才被读）→ 已清零且无残留依赖；③ `s_m2_st_core/s_m2_st_csb*`（仅自检消费）→ 无跨 span 消费者；④ FIRA 设备级 `s_seg_in/s_seg_out3/s_taskMem/g_FIRTaskDoneCount`（消费者 = 每次段调用）→ 每次调用完整重组/按跨度读/置 0 后排队（:405,612-655）→ 状态等价于「活流跑了 N 帧之后」，活流本就容忍；⑤ `g_m2_selftest_*`（只写自己的读数）；⑥ `g_m1_*`/`g_m2_out_*`/`poll/overrun/beam_cyc_*`/`s_m1_pp_index`/DMA 缓冲 → 自检不触碰 ✓；⑦ `g_m1_valid`/`g_m2_valid` 语义不变（仍在 sport init 后置 1） |

**§12 红线**：FG1/FG2/IO1/IO2 无一 FAIL → 「板上 bit-exact 自检」主张成立（待板证 [L1]）。

---

## 2. 包 2 —— `sprint7/docs/S7_POLARITY_QA_RUNBOOK.md`（testing，零代码）

### 2.0 总裁定：**PASS_WITH_MINOR**（0 BLOCKER / 0 MAJOR / 2 MINOR / 3 INFO）

一句话：可执行、电池逐只（A1/A2 表、1.5 V 首选 / 9 V 极短瞬触例外、最多两次、串联对必须电气孤立）+ 375 Hz 成对复验（三项读数各 3 次取中值、SAME/OPPOSITE/WEAK/分不清全为同会话相对判据、相邻链式法交叉核）+ 失败处理 8 行 + 入库模板（POLQA 文件骨架 + decisions_log 条目骨架含 reviewer pending）+ L 级规则表 + 与 P1/D8 衔接（恒等表提醒在 §6.2）；全文 **零 dB 期望数值、零「应约」**，07-08 竞品数值未引；C10 四项齐。两个 MINOR 都是判据定义的边角：一处经引用绑定了外部 ≥15 dB 门与自身「不用任何绝对 dB 数」矛盾，一处「明显」定义在仪表量化下退化。

### 2.1 Findings 表（包 2）

| ID | 严重度 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| P2-MINOR-1 | MINOR | §2.6 第 16 条（:239） | 「满足 `EXP_STATIC_POL375.md §4` 的信噪比门（门值以该文为准，本文不复写）」——该文 §4 的门是「solo 高出本底 ≥~15 dB」。本文字面没写数字，但判据被一个绝对 dB 门约束，与 §0.4 开头「不用任何绝对 dB 数」和 §0.4 第 5 条（读数 vs 本底也用相对规则）自相矛盾；小喇叭 375 Hz 效率未知（§0.4 末注自己承认）时 15 dB 可能达不到而被误判 FAIL。 | 改为：「solo 明显高于本底（§0.4 第 5 条）即可进入 Phase A；`EXP_STATIC_POL375 §4` 的信噪比门只作电平设定的**参考**，达不到不构成 FAIL，走 §3 第 3 行（挪麦/换参考路）并在 R10 第 6 项记本底与 solo 原值」。 |
| P2-MINOR-2 | MINOR | §0.4 第 1–3 条（:48-51） | 「明显」= 中值差 > 两者散布较大者。手机分贝计量化到 0.1 dB、三次同值时散布 = 0，则 1 个显示步长的差即「明显」（SAME/OPPOSITE 可被 0.1 dB 触发）。Phase A「大致齐」前置削弱了风险，但定义本身退化。 | 散布取 `max(三值极差, 仪器显示分辨率 1 步)`（仪器属性，非声学期望，不违反「不写期望数值」），并在 R10 第 1 项记显示分辨率。 |
| P2-INFO-1 | INFO | §2.1 第 3 条（:186）、§2.3 指纹行（:202） | 「s7-base 正在加 `#error` 守卫与两个运行时指纹…在它们入库之前」在包 1 commit 后即过时；指纹期望「由 s7-base 在入库文档给出；本文不代填」可直接填 `g_m2_static_txtest_built=1 / g_m2_stxt_localize_built=1`（build 事实，非测量期望；IMPL-01(2) 本就要求指纹给期望值）。符号名与包 1 `m1_loopback_tdm.h:67-68` **一致** ✓；`g_stxt_ch_mask` 在 HEAD 存在（`.h:119`）✓。 | 包 1 commit 后同批改两句。 |
| P2-INFO-2 | INFO | §2.4（:218-221） | 格式门回读 `s_m1_tx_buf`（file-static）24 值，已预备「符号不可见 → 记录、等替代法、期间只做 Step A」的处置 ✓；24 个预期值不复写、指向 `EXP_STATIC_POL375 §3`（数字域表，非声学期望）✓。 | 无需动作。 |
| P2-INFO-3 | INFO | §0.1 第 3 行（:20） | 「8 路输出单端 DAC1P–DAC8P（无 N 脚）[L1 硬件]」继承 `BEAM_POLARITY_CLOSURE_20260708.md §1 ③`（已过 critic）；本审未重核该引脚事实，只核引用存在。 | 无需动作。 |

### 2.2 任务书逐项核实（包 2）

- **dB / 应约 / 期望值 grep**：`dB` 命中 5 处全是「不用/不写 dB 门」的否定句（:7,46,55,372,425）；「期望」命中只在 gate 表头与指纹行（:199,202，指纹非声学数值）；「约」只在「Run 约 5 秒」与「λ≈915 mm [L3 背景]」；数字出现的单位只有 Hz/V/mm（375 Hz、2250 Hz、1.5/9 V、d=55 mm、L=825 mm、λ≈915 mm），均为 rig/激励/程序参数且带出处或 L 标，**无一是通过阈值** ✓。07-08 竞品 rig 的 87.5/93.5/104 dB 等数值未出现 ✓。
- **判据全相对**：§0.4 六条操作定义；§2.7 Phase A（大致齐/明显高于本底/明显低于其余）、§2.8 表（SAME/OPPOSITE/WEAK/分不清）、§2.8-26 一致性自检、§2.8-27 链式法（两 OPPOSITE 相乘 = SAME，逻辑正确）——全部是同会话读数间比较 ✓（例外见 P2-MINOR-1）。
- **C10**：电池 1.5 V 首选 / 9 V 只准极短瞬触、同一只最多两次、禁 >9 V、禁按住、禁对仍连功放或仍串联的喇叭做（§1.3）✓；改线前功放断电（§1.1、§2.9、§3 第 2/4 行、§7.1）✓；首跑功放断电 + 掩码 0x00 后再上功放（§2.2-6/9、§7.3）✓；JTAG 顺序引用 `sprint3/audit/ezkit_bringup_checklist.md` 项②③ + 禁热插拔 + BMODE 全 0（§0.3、§2.2-5、§7.4）✓；375 Hz 短促、测完回 0x00、相消零点不加增益（§2.6-17、§7.2）✓；板身份/版本记录（§0.2「板」行 + R10 第 8 项）✓。→ **C10 PASS**。
- **宏组合与指纹**：§2.1 四宏 `M2_FIRA_INLOOP=1`/`FIRA_USE_REAL_ADI_FIR_HEADER`/`M2_STATIC_TXTEST=1`/`M2_STXT_LOCALIZE=1`，与 `m1_main.c:55-83` 静态分支、包 1 `#error` 守卫（X1/X3 证伪）一致 ✓；「不要加 `M2_CHMAP_FIX`/`M2_RX_RIGHT_ALIGNED`」✓；§2.3 诚实死项（`fg_beam_live=−99`、`out_*=0`、`overrun` 涨、`poll/beam_cyc` 不增长）与代码一致 ✓（静态分支跳过 `m2_beam_poll`，ISR 仍发布半区 → overrun 累加）。指纹名一致（P2-INFO-1）。
- **入库模板与 L 级**：§4.1 骨架含 R10 原文、A1/A2/B1/B2 原值、映射表、每条结论带 L 标、铁律四冲突节；§4.2 decisions_log 骨架含可逆性/无采购/判据性质/边界/`reviewer: pending` ✓；§5 定级表：电池逐只 [L1 逐只 机械位移法]、成对 [L1 通道级]、映射 [L1]、理论关系 [L3 背景 不得作阈值]、SPL 原值 [L1 仅相对]、未做写「未记录」、禁 solo-SPL 推极性、禁作方向图规格、映射≠约定触发铁律四 ✓。
- **映射与 P1/D8 衔接**：§6.1 物理秩 = min(p,15−p)、`s_m2_chmap[c]` 由 dsp 从映射表推出并双轨核、测试员不改 ✓；§6.2 不沿用 {4,5,6,7,0,1,2,3} + **恒等表提醒**（与约定一致时开 `M2_CHMAP_FIX` 不改默认表反而贴错）✓；§6.3-6.4 P1/P0 顺序 ✓。
- **有无越级把相对判定写成规格**：无。§2.9 可选 2250 Hz 项明写「不作方向图规格、不作 PASS 条件」；§5 末两行禁令 ✓。
- **串联对接法物理正确性**（我核）：§1.7「pos c 的 − 接 pos(15−c) 的 +，对总 + = pos c 的 +，对总 − = pos(15−c) 的 −」= 同相串联 ✓；§1.4「电池 + 碰到且纸盆外弹 → 标 +」为通行约定 ✓；§1.1 要求被测喇叭电气孤立（否则电流同时过两只）✓。
- **引用文件存在性**：`BOARD_TEST_INSTRUCTIONS.md`、`STAGE4_TESTER_RUNBOOK.md`、`STAGE4_BRINGUP_CHECKLIST.md`、`ezkit_bringup_checklist.md`、`EXP_STATIC_POL375.md`、`EXP_CHMAP_AB.md`、`BEAM_POLARITY_CLOSURE_20260708.md`、`TEST1_WIRING_FINGERPRINT_FIELDLOG_20260629.md`、`OBS_OWNRIG_FRONT_SIDE_L0_REG20260902.md` 全部存在 ✓。

### 2.3 C1–C10 / §12（包 2）

| 门 | 结论 | 证据 |
|---|---|---|
| C1 | PASS | 所有进入结论/规格的数字带 L 标（§0.1 表、§0.2 表、λ [L3]、§5 定级表） |
| C2 | PASS | 无 L2/L3 被写成实测；[L1] 只用于已归档板证/现场事实 |
| C3 | PASS | 无不可逆决策（改线可逆、无采购） |
| C4 | PASS | [L3] 只作背景，明写「不得作阈值」 |
| C5 | PASS | 出处逐条可追；映射表将由 dsp 双轨核（§6.1） |
| C6 | N/A | 几何只作 rig 描述（DEC-S3-GEOM-01），本手册不锁几何；映射≠约定时触发铁律四（§5 末）✓ |
| C7 / C8 / C9 | N/A | 无撤回 / 无外部输入 / 无加速器收益 |
| C10 | PASS | 见 §2.2 C10 条 |
| §12 | N/A（零代码） | 但格式门（24 值逐字节）+ 指纹 + 诚实死项 = 「build 是否是我以为的那个」的反假绿门，设计正确 |

---

## 3. 实跑命令与结果（全部只读；日志在 scratchpad）

```
$ cd <repo>; git status --porcelain; git diff --name-only; git diff --cached --name-only; git log -1 --oneline
   M sprint6/dsp/audio/m1_cces_project/src/m1_loopback_tdm.c   (+328)
   M sprint6/dsp/audio/m1_cces_project/src/m1_loopback_tdm.h   (+35)
   M sprint6/dsp/audio/run_guard_check.sh                       (+48/-1)
   ?? sprint7/docs/S7_B63_WALLCLOCK_GAP.md  ?? sprint7/docs/S7_POLARITY_QA_RUNBOOK.md  ?? sprint7/docs/S7_TESTER_RUNBOOK_SB.md  ?? sprint7/dsp/
   staged: (空)   HEAD: c9c3f91

$ bash sprint6/dsp/audio/run_guard_check.sh            -> critD_guard.log
   [guard-check] OVERALL PASS (10 compile configs + 5 falsifiers).   EXIT=0   (15 条 PASS 行；X1..X5 各含对应 #error 文本)

$ S7_OUT=<scratch>/critD_s7host bash sprint7/dsp/host/run_s7_host_checks.sh   -> critD_s7host.log
   pos PASS / neg-unity PASS / neg-reverse PASS / neg-chmap PASS / neg-stub PASS / neg-sb2flip PASS
   S7_SELFTEST_HOST all: PASS (0 mode(s) failed); -O0+UBSan pos 8 CRC 行与 -O2 IDENTICAL; OVERALL PASS   EXIT=0
   pos crc[0..7] = 8E807729 B2F1E13F 7B109C71 D7BD23E7 A000D606 2403E085 B88D91B5 2E0D8C6E  (== dolph_f5_goldens.h:58-65 == runbook C-1)

$ bash sprint7/dsp/host/run_s7_preproc_equiv.sh        -> critD_preproc.log
   M1 default 12 行 / M2 default 16 行 / +RX_RIGHT_ALIGNED 16 / +CHMAP_FIX 16 / +STATIC_TXTEST 16 / +LOCALIZE 16 — 全在 allow-list
   m1_main.c: 0 diff lines vs HEAD;  OVERALL: PASS   EXIT=0

$ sed(复制到 scratch, 硬编码 ROOT, 删 -I"$SRC") > critD_preproc_noSRC.sh; bash critD_preproc_noSRC.sh
   [M2 + STATIC_TXTEST] INVALID: gcc -E failed on the HEAD copy: fatal error: m2_static_txtest_table.h
   [M2 + STATIC_TXTEST+LOCALIZE] INVALID: ... m2_static_txtest375_table.h
   OVERALL: FAIL   EXIT=1        <- 防呆有效（rc≠0 不再假 PASS）

$ grep -n "seg_l2_dmda_bw\|mem_L2_bw\|MY_L2_CACHED_MEM" system/startup_ldf/m1_app.ldf
   :215 mem_L2_bw START(0x20000000) END(0x200f9fff); :220 MY_L2_CACHED_MEM mem_L2_bw; :1255-1260 dxe_l2_data_bw{seg_l2_dmda_bw...} > MY_L2_CACHED_MEM
$ grep mem_block1_bw m1_app.ldf -> :190 START(0x002c0000) END(0x002ebfff)   (runbook Block 1 范围一致)
$ git log --oneline | grep 44a99e8 -> 44a99e8 2026-06-04 F5-A: FIRA chain x8 instancing + 8 per-channel Dolph goldens + harness
```

Scratchpad 文件：`critD_guard.log`、`critD_s7host.log`、`critD_s7host/`、`critD_preproc.log`、`critD_preproc_noSRC.sh`、本文件。

---

## 4. 交 lead 的两行

- **包 1（D3 固件改动包 + S-B runbook）：CONDITIONAL** —— 0 BLOCKER / 1 MAJOR / 2 MINOR / 6 INFO。代码与 §12 五门全过、三套检查我亲跑全 PASS、防呆实证有效；MAJOR 只在文档：`M2_SEG_CYC` 无指纹且表 A 无行，B63 引用不存在的 `g_m2_seg_cyc_built`。修 runbook 表 A/模板 + 对齐 B63 命名（不扩 D3 范围）→ delta 复审即可 PASS 进 CTO-gated commit。
- **包 2（极性 QA runbook）：PASS_WITH_MINOR** —— 0 BLOCKER / 0 MAJOR / 2 MINOR / 3 INFO。零期望数值、判据全相对、C10 四项齐、模板与 L 级规则齐、恒等表提醒在；MINOR 为 §2.6 经引用绑定外部 15 dB 门（自相矛盾）与 §0.4「明显」在散布=0 时退化。可随包 1 同批修后入库。

---

## 5. Delta 复审（2026-09-03，reviewer: critic @ claude-fable-5-1；只读；文档修正稿）

**前提核实**：代码本体未动——`git diff --stat` 仍为 `.c +328 / .h +35 / run_guard_check.sh +48 −1`，三个 diff 的 md5 与初审一致，`.c/.h/.sh` 与 `sprint7/dsp/host/*` 的 mtime 均为 2026-09-02 22:25–22:30（早于初审）；仅 `S7_TESTER_RUNBOOK_SB.md` / `S7_POLARITY_QA_RUNBOOK.md` / `S7_B63_WALLCLOCK_GAP.md` 三份文档在 01:24:53 更新。`git status` 集合与初审相同，staged 仍为空。初审的三套实跑结论（guard / host / preproc）因代码未变继续有效。

### 5.1 包 1 delta

| 初审 ID | 修正核实 | 结论 |
|---|---|---|
| F1-MAJOR-1 | S-B 表 A 新增行（:97）：`g_m2_seg_w_cyc_last` 符号可见性 = B0 不存在 / B1 可见 / B2 不存在 / B3 不存在，并写明「B0/B2 若可见 = 残留 `M2_SEG_CYC`，该 build 的 `beam_cyc` 读数作废（33 次 CCNT 读扰动）」；§5 模板加 `seg_w_cyc_last 可见?(是/否)=_`（:162）。B63 :103 与 :294 改为同一可见性判据并指向 S-B 表 A；`grep -rn g_m2_seg_cyc_built sprint7/ src/` = **0 命中**。 | **CLOSED** |
| F1-MINOR-1 | §1.1（:20）加 `git pull` 冲突处置（原样发回、不 reset）；§6（:182）加「不 commit、不 push、不 reset；GUI 加宏/加 include 使本地 `.cproject`/`.project` 变脏属设计如此、永不提交；提交别的东西前先 `git checkout -- …/.cproject …/.project`」。 | **CLOSED** |
| F1-MINOR-2 | §1 新增第 0 条（:19）：BMODE0/1/2 全 0、先插 JTAG（断电）→ 板上电 → 仿真器 USB、禁热插拔、结束先 disconnect 再断电再拔、ICE Test 5 步全过再 Load，指向 `STAGE4_BRINGUP_CHECKLIST.md` 与 `BENCH_OPS_CARD.md`。我对照源头：`sprint3/audit/BENCH_OPS_CARD.md:26-29`（BMODE 全 0 / 连接顺序 / ICE Test 5 步 / 先 disconnect 再拔）与 `sprint3/audit/ezkit_bringup_checklist.md:100-104,134`（连接顺序 / 禁热插拔 / BMODE 全 0）逐句有据，**无自创步骤**。 | **CLOSED** |
| F1-INFO-1…6 | 未改（均为「无需动作/可选」项） | 维持 INFO |
| 新 INFO（F1-INFO-7） | §1 第 0 条把出处写为 `STAGE4_BRINGUP_CHECKLIST.md` 与 `BENCH_OPS_CARD.md`；JTAG/BMODE/ICE Test 的原文其实在 `BENCH_OPS_CARD.md` 与 `sprint3/audit/ezkit_bringup_checklist.md` 项②③（`STAGE4_BRINGUP_CHECKLIST.md` 本身无这些关键词）。出处精度问题，不影响执行。 | INFO，可选补一个文件名 |

**包 1 最终裁定：PASS**（0 BLOCKER / 0 MAJOR / 0 MINOR / 7 INFO）。C1–C10 与 §12 结论不变（C10 由「1 MINOR」转 PASS）。可进 CTO-gated commit；板上 [L1] 结论仍只由 S-B 回填产生。

### 5.2 包 2 delta

| 初审 ID | 修正核实 | 结论 |
|---|---|---|
| P2-MINOR-1 | §2.6-16（:239）改为「solo 明显高于本底（§0.4 规则）即可进入 Phase A；`EXP_STATIC_POL375 §4` 信噪比门只作电平设定参考，达不到不构成 FAIL，走 §3 记录并继续」。与 §0.4「不用任何绝对 dB 数」不再矛盾；全文 `dB` 命中仍只有否定句（:7,46,55,372,425）。 | **CLOSED** |
| P2-MINOR-2 | §0.4 第 1 条（:48）：散布取 `max(三值极差, 仪器显示分辨率 1 步)`，并注明「分辨率是仪器属性，记入 R10 第 1 项，不是声学期望」。定义退化已消除。**残留**：R10 记录卡第 1 项（:61）仍是「分贝计 App/型号 / 计权 / 快慢 / 固定方式」，**没有「显示分辨率」格**——§0.4 让测试员记到一个不存在的格子。 | 部分 CLOSED → 残留 **MINOR（非阻塞）**：R10 第 1 项加「显示分辨率(最小步)____」 |
| P2-INFO-1 | §2.1-3（:186）改为「已随 D3 包实现（同批入库）」，§2.3（:202）指纹期望填「均 = 1（build 事实，非测量期望；D3 包 `m1_loopback_tdm.h` 定义）」并给出不符处置。符号名与 `m1_loopback_tdm.h:67-68` 一致。:186 后半句「在它们入库之前，测试员须自行确认三个宏都在」在同批入库后成为恒真的冗余要求（截图仍是交付物），无害。 | CLOSED（措辞冗余记 INFO） |
| P2-INFO-2/3 | 未改（无需动作） | 维持 INFO |

**包 2 最终裁定：PASS_WITH_MINOR**（0 BLOCKER / 0 MAJOR / 1 MINOR 残留 / 3 INFO）。残留 MINOR = R10 卡第 1 项补「显示分辨率」一格，可随入库前顺手改，不阻塞。零期望数值、判据全相对、C10 四项齐的结论不变。
