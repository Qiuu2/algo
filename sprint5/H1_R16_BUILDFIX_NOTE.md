# H1 R16 build-fix + desktop-blind-spot closure — note for the R16 gate

> DRAFT. NO commit; critic R16 gates (quick: decl reorder + new guard-check). Then lead commits, CTO syncs.
> 缘起：CTO 退回 R15 包——CCES build 3 错（h1_wcet_measure.c :137/:146/:168「s_h1_fa undefined」）。
> 三道关自指：关①已过（本 teammate 修 + 新增 guard-check 机械证伪：broken FAIL / fixed PASS）；关② critic R16（待）；关③ CTO。

---

## 1. 修复（已落 uncommitted edit on `sprint5/dsp/harness/h1_wcet_measure.c`）

### 根因（CTO 诊断确认）
R15 新增的三函数（h1_state_save / h1_state_restore / h1_dcache_inval_workingset）放在了
`static FiraChannelState s_h1_fa[DOLPH_W8_NCH];` 声明**之前**（旧 :216，在 h1_fira_frame 前）→ C 先用后声明。
CCES 报 :137/:146/:168「s_h1_fa undefined」。

### 修法（robust，非最小挪动）
把**所有** file-scope static STATE 声明集中到 guarded 区**顶部、任何函数之前**一个块：
```
(top of #if FIRA && TARGET block)
  static FiraChannelState s_h1_fa[DOLPH_W8_NCH];        // line 116
  static FiraChannelState s_h1_fa_snap[DOLPH_W8_NCH];   // 118
  static int32_t          s_fd_hist[8][4][7];           // 121
  static int32_t          s_fd_hist_snap[8][4][7];      // 123
  static const int16_t    s_fd_coeff[8][8] = {...};     // 129
(then ALL functions: h1_state_save 146 / restore 155 / dcache 171 / focus_subband 187 / crc 211 / fira_frame 229)
```
- 删了旧 :216 的重复 `s_h1_fa` 声明（现唯一，grep 确认 count==1）。
- 现**5 个 state 声明（116-129）全在 6 个函数（146-229）之前** → 任何函数重排都不会再触发 declare-before-use。
  这是比「只把 s_h1_fa 上移一行」更强的硬化：state 块在顶部，新函数无论插哪都在其后。

## 2. 为什么桌面检查漏了（诚实归因）

- 三新函数（及整个 focus/state/frame 块）在
  **`#if defined(FIRA_USE_REAL_ADI_FIR_HEADER) && defined(TARGET_SHARC)`**（h1_wcet_measure.c:105）守内。
- gate-① 与 critic R15 的桌面检查都是 `gcc -fsyntax-only`/`-c` **不带** 这两个宏 → 预处理器**整块剔除**该区，
  gcc **从未编译**过它。故「gcc clean, 0 warnings」对 guarded 区**结构性失明**——declare-before-use 在
  guarded 区里，桌面零覆盖。CCES build（带宏 + 真 BSP）是第一个真正编译它的地方 → 才暴露。
- 教训：**TARGET-guarded 代码对 plain 桌面 gcc 不可见**；声明序/符号用必须在 guarded 区单独验。

## 3. 缺口闭合：guard-stub 语法检查（option (a)，已实现 + 证伪证明）

实现（cheapest honest）：mock 仅 **BSP-only（不在仓）** 符号，让 gcc 带 `-DFIRA_USE_REAL_ADI_FIR_HEADER
-DTARGET_SHARC` 真编译 guarded 区。仓内符号（FiraChannelState/fira_*/tfb_*/g_*/BENCH_*）走真头。
- **新文件**：
  - `sprint5/dsp/harness/guard_stub_inc/services/pwr/adi_pwr.h` — mock `adi_pwr_GetCoreClkFreq`。
  - `sprint5/dsp/harness/guard_stub_inc/sys/cache.h` — mock `flush_data_buffer`（A5 签名）。
  - `sprint5/dsp/harness/guard_stub_inc/drivers/fir/adi_fir.h` — mock（fira_tree.h 在宏下 #include 它；
    给最小 handle/enum/CHANNEL_INFO + ADI_CACHE_LINE_LENGTH，够 fira_tree.h **parse**；raw adi_fir_* 在
    fira_tree.c，本检查不编译那个 .c）。
  - `sprint5/dsp/harness/run_guard_check.sh` — 跑 `gcc -fsyntax-only -Wall -Wextra -D两宏 -I mock + 真头`。
- **诚实边界**：纯 `-fsyntax-only`（不 link/run）；mock 是 parse-time stand-in，非真 BSP 行为。它验
  **声明序 + 符号用 + 类型**——正是漏掉的那类，**不**验真 FIRA 运行/真 cycle（那些仍待板）。

### 证伪证明（falsifier discipline，CTO 要求）
| 版本 | guard-check 结果 |
|---|---|
| **BROKEN**（s_h1_fa 声明移回 helpers 之后 = 复现 R15 bug） | **FAIL，exit 1**：`error: 's_h1_fa' undeclared` @ :149(save)/:158(restore)/:180(dcache) —— **与 CCES 报的 3 错同址同因** |
| **FIXED**（本修复） | **PASS，exit 0**：guarded 区编译干净 |
=> 该检查**机械捕获**正是这次的 error class（若早有它，R15 不会过门）。

## 4. 验证证据（关①，全绿）
- **`run_guard_check.sh`（FIXED）**：`[guard-check] PASS`，exit 0。
- **`run_guard_check.sh`（BROKEN 临时副本）**：`error: 's_h1_fa' undeclared` ×3，exit 1（证伪成立）。
- 桌面路径 `gcc -c -O2 -Wall -Wextra`（无宏）：exit 0，0 警告（无回归）。
- host test（含 R15 的 check4a/4b 有状态契约）：PASS，exit 0。
- ASCII-clean（.c + 三 stub .h + .sh）；frozen 未动；HEAD 未变（R15 包 lead 已 commit 11a701d，本轮 uncommitted）。

## 5. 改了什么 / 为什么漏 / 闭合（R16 gate 摘要）
- **改了什么**：(i) 所有 static state 声明上移到 guarded 区顶部、函数之前（修 declare-before-use，硬化抗重排）；
  (ii) 新增 guard-stub 语法检查（脚本 + 3 mock 头）覆盖 TARGET-guarded 区。
- **为什么漏**：guarded 区对 plain 桌面 gcc 不可见（宏未定义→预处理剔除）；gate-①/R15「gcc clean」对它失明。
- **闭合**：guard-check 带宏 + mock BSP 真编译该区，已证它捕获本 bug（broken FAIL / fixed PASS）。
- **建议入 harness 规则**（team_config，与 R15 硬化 (b) 同处）：**TARGET-guarded 代码必须跑 guard-stub 语法
  检查**（plain 桌面 gcc 对其失明）；任何含 `#if ...TARGET...` 守区的 harness，gate-① 须含此检查。
  （change block 附下，供 R16 一并过门。）

### team_config change block（追加到 R15 的「Harness / probe design」节）
```
- **TARGET-guarded 代码对桌面 gcc 不可见 — 必跑 guard-stub 检查**：任何 `#if defined(...TARGET_SHARC...)`
  守区的 harness，plain `gcc -fsyntax-only`（不带宏）**不编译该区**，声明序/符号用零覆盖（缘起 R15→R16：
  s_h1_fa declare-before-use 在 guarded 区，桌面「gcc clean」失明，CCES build 才暴露）。gate-① 必含
  guard-stub 语法检查（带 -D守宏 + mock 仅 BSP-not-in-repo 符号，例 sprint5/dsp/harness/run_guard_check.sh），
  并以**证伪**自证（对 broken 版 FAIL、fixed 版 PASS）。
```

## 6. 无法从桌面核实
- 真 CCES/SHARC 编译（guard-check 是 host gcc 代理；mock 非真 BSP，真 link/run 待板）。
- 板上 same-state re-run 数（待板 [L1]，R15 内容不变）。
- 行号随提交漂移；team_config change block 以锚字符串定位，lead apply 复核。
