# H1 R15 fix package — state-snapshot fix + D-cache cold + MAC-2x resolution + 3 hardening + DEC row

> DRAFT. NO commit; critic R15 gates. Frozen files untouched; ASCII-only target; desktop self-verify done.
> 缘起：CTO 批 fix(a)+R15+re-run，NO salvage。FG BLOCKER 根因 = ST1 跨态 CRC 自检设计缺陷（已诊断确认）。
> 三道关自指：关①已过（本 teammate 自验 + gcc + host test 扩展覆盖有状态契约）；关② critic R15（待）；关③ CTO。

---

## 1. STATE SNAPSHOT/RESTORE FIX (applied to `sprint5/dsp/harness/h1_wcet_measure.c` — uncommitted edits)

实现要点（CTO 四项逐条）：
- **(i) identity 现 == nofocus 逐位**：三帧（focus-ON/focus-OFF/identity）各自 `h1_state_restore()` 回到同一
  快照态再跑同一输入 → identity 与 nofocus 从**同态同输入**出发，零延迟 pass-through 必逐位复现 nofocus
  (true continuity gate)。host check4b 已证（见 §6）。
- **(ii) cycle A/B 现 same-state**：focus/nofocus 两 span 各自 restore 到同一快照态 → 增量 = 纯 focus 阶段
  代价，无跨态分量。**方法学 delta 落字**：re-run 数（same-state）**取代** R14 quarantined 数（cross-state）。
- **(iii) restore 在计时 span 外**：`h1_state_restore()` 在 `bench_cyc_target()` t0 **之前**调用（代码 :320/:329/
  :348 restore 后才 t0=...）→ 8×~2.3KB struct memcpy **不进** cycle 计数。
- **(iv) s_fd_hist 同处理**：快照/恢复**同时**含 `s_h1_fa`（FIRA 链态）与 `s_fd_hist`（focus FIR 历史）——
  focus FIR 历史也须同态起步，否则 focus-ON span 的 focus 阶段会带上一帧残留 → 增量不纯。`h1_state_save/
  restore` 两者一并存/恢。（identity 路径跳过 focus 阶段，s_fd_hist 不前进，但快照含它保证 focus-ON span 干净。）

**change block 形状**（已落 uncommitted；供 critic diff）：
```c
/* new statics (inside FIRA guard, next to s_fd_hist) */
static FiraChannelState s_h1_fa_snap[DOLPH_W8_NCH];
static int32_t s_fd_hist_snap[DOLPH_W8_NCH][4][H1_FDTAPS - 1];
static void h1_state_save(void){ ... s_h1_fa_snap[c]=s_h1_fa[c]; s_fd_hist_snap=...; }
static void h1_state_restore(void){ ... s_h1_fa[c]=s_h1_fa_snap[c]; s_fd_hist=...; }

/* after warm-up, before compared frames: */
h1_state_save();                 /* snapshot clean steady state ONCE */
/* each compared frame: */
h1_state_restore(); t0=bench_cyc_target(); crc=h1_fira_frame(...); t1=...;  /* restore OUTSIDE span */
```

## 2. D-CACHE INVALIDATE for true-cold-DATA WCET (applied)

- `#include <sys/cache.h>` (TARGET-guarded). `h1_dcache_inval_workingset(...)` calls
  `flush_data_buffer(start,end,1)` (flush-and-invalidate, A5 symbol, fira_tree.c:489-500) over H1's
  **mutable working set**: fsb0-3 / fout / xw / scr + the persistent `s_h1_fa` + `s_fd_hist`. Called
  **OUTSIDE the timed span**, before the cold frame.
- **Relabel (honest)**: cold = **TRUE-cold-DATA / I-cache STILL WARM**. There is **NO repo-known SHARC
  I-cache invalidate symbol** (desktop) — full I+D cold is a **C10 board item (I-side symbol TBD)**.
  Even I+D cold stays a **LOWER BOUND on system WCET** (no SPORT/codec DMA contention, no ISR preemption
  in this bare-metal free-run bench). Scoping unchanged in code header + worksheet.

## 3. MAC 2x DISCREPANCY — RESOLVED (CTO priority, BEFORE re-run interpretation)

### (a) TRUE subband sample counts + true MAC/MMAC of the harness focus stage
Source (fira_regression.c:195 sz[] entity / h1_wcet_measure.c:235 [R33 anchor fix: fira_tree.c:49-52 was a saturating-arith helper, mis-cited], F4/F5 sizing fira_regression.c:193): the dyadic tree's 4 subbands per
64-sample frame are
```
sb0 (coarse @f3) = frame/8 = 8     sb1 (detail @f2) = frame/4 = 16
sb2 (detail @f1) = frame/2 = 32     sb3 (detail @f0) = frame   = 64   (UNDECIMATED: sb3[i]=in[i]-r1[i])
```
**Sum = 120 samples/frame/channel** (NOT 60). Subband rates sum = 120 × 750 fps = **90 kHz** (NOT 45 kHz).
- Harness focus stage MAC/frame = 8 taps × 120 samp × 8 ch = **7,680 MAC/frame**.
- **TRUE harness MMAC/s = 7,680 × 750 = 5.76 MMAC/s.**

### (b) The "EXACTLY 2.88" claim was WRONG by 2x — corrected with trail note
- The cost-model 2.88 MMAC/s (dsp_8ch_report:59) assumed **60 samp/frame/ch (45 kHz)**; the REAL tree has
  **120 samp/frame/ch (90 kHz)** because sb3 is undecimated. So the harness implements **5.76 MMAC/s = 2x**
  the model. **R14 verified the FORMULA (8tap×N×8ch×fps) but NOT the sz[] sample counts → the 2x slipped.**
- **Corrected in code header** (h1_wcet_measure.c FOCUSING-FIR block, uncommitted edit) — the "EXACTLY 2.88"
  line replaced with the 120-sample / 5.76 MMAC/s derivation + the explicit 2x-correction trail.
- **Trail note (落 WO-S5-H1 §2.1 + this doc)**: 86-144 envelope was 2.88-based; harness is 5.76-based.

### (c) Envelope recalibration — the RIGHT yardstick for the re-run
- **Recalibrated envelope (5.76 MMAC/s × 30-50 cyc/MAC) = 173-288 MCPS.** (vs old 86-144 = 2.88-based.)
- **Correct framing (pick): compare g_h1_cyc_focus_only (board) ←→ 173-288 MCPS [L4-recalibrated].**
  Equivalently `g_h1_cyc_focus_only/2 ←→ 86-144`. I pick the FORMER (compare real cyc of real 120-sample
  work against the 5.76-based envelope) — it avoids a /2 fudge and measures the true stage. Worksheet updated.
- Note: R14 quarantined `focus_only=65,410 cyc` → 49.1 MCPS, cyc/MAC=8.5 over 7,680 MAC. That 8.5 cyc/MAC
  is **plausible for a plain flat short-FIR core loop** (NOT a FIRA segment — no orchestration), i.e. it can
  legitimately sit BELOW the 30-50 cyc/MAC FIRA-segment envelope. But it's quarantined (cross-state run) and
  superseded by the same-state re-run; do not interpret it.

### (d) PRODUCT-cost flag (do NOT silently change DEC-S5 — flag for CTO)
- The product focusing applies frac-delay to these **same 120-samp/frame subbands** → true product focus
  cost is **~5.76 MMAC/s class**, so **DEC-S5-V1-SCOPE-01's "focus 86-144 MCPS [L4]" is likely ~2x
  UNDERSTATED** (true ~173-288 MCPS [L4] at 30-50 cyc/MAC).
- **CONSEQUENCE for the v1 whole-system envelope** (do NOT change silently — FLAG):
  if focus 86-144 → 173-288, the §8 best/worst recompute:
  - best = 1000/(347.45 + 173 + 29 + 5 + 2 + 1 + 34.7) = 1000/592.2 = **~1.69x** (was 1.98x)
  - worst = 1000/(347.45 + 288 + 60 + 30 + 15 + 10 + 173.7) = 1000/924.2 = **~1.08x** (was 1.28x)
  - 整系统残余收紧到 ~1.08x–1.69x。**worst 1.08x 仅高于 1.0x 临时下限 0.08x——MAC-2x 校正已把最坏情形逼到 1.0x 底线的刀刃上**；且 focus(288, MAC-2x [L4]) 与 WCET(+50% [L3]) 两个主导项均未实测，任一进一步恶化即可破 1.0x。≥1.5x 现明显不达（worst 1.08<1.5），≥2x 死。**故 1.0x 临时下限在新口径下不再有舒适余量——板上 focus_only [L1] + WCET [L1] 实测前不可断言 1.0x 守得住（R5/R7/R13 教训）。** CTO 据板 L1 裁是否仍守 1.0x / 是否需 HW-1。
    **This is a flagged proposed correction to DEC-S5-V1-SCOPE-01 / the §8 envelope — CTO rules whether to
    adopt (pending the board focus_only [L1] which settles cyc/MAC).**（critic R15 F15-MAJOR-1 修正措辞）
  - The board re-run focus_only [L1] will give the REAL focus MCPS directly (no MMAC×cyc/MAC estimate),
    superseding both 86-144 and 173-288. So the cleanest path: re-run, book the L1 number, then CTO updates
    DEC-S5 from L1. The flag stands until then.

## 4. THREE HARDENING ITEMS (change blocks)

### (a) critic skill §12 — "harmless-for-X" reviewer rule (canonical + recat)
`agents/critic/skill.md`, after the ST1 line (:1108), insert a new bullet:
```
- **ST1-E 跨态/跨消费者枚举 — MAJOR**：当 reviewer 裁某状态/异常「对 X 无害」时，**必须枚举该状态/异常的
  ALL 消费者**（所有跨 span 共享的可变态 × 所有读它的 probe/计数器/CRC），**逐项裁**，不得只裁 X 一处。
  缘起 R14→R15：H1 的 s_h1_fa 跨帧态被三个 probe（focus/nofocus/identity）以**不同推进态**消费，
  原审只看 focus_differs(对) 未枚举 zero_recovers(被同态不对称坑) → 假 FG FAIL。漏枚举=MAJOR。
```
**Recat**：同字符串加到 `.claude/skills/critic/SKILL.md` 对应 ST1 行（:1132）之后（verbatim-copy 约定，
两份保持一致）。两处 §12 红线行不动。

### (b) harness 设计规则 — 落 team_config（与三道关同处，团队过程法；不另建 doc）
`.claude/team_config.md`，Three-gate verification 节之后新增小节：
```
## Harness / probe design (2026-06-05, CTO-mandated — 缘起 R14/R15 H1 ST1 自检缺陷)
- **自检 probe 与测量 span 不得共享可变态**；若必须共享，**须 snapshot/restore 到同一态再比较**
  （比较两帧必须同 state + 同 input，否则有状态滤波的 CRC 必假失配 = ST1 类自检缺陷）。
- **省内存不是充分理由**：把大态设 static 省栈是对的（FIX2），但若该 static 被多 probe 跨态消费，
  必须记录 trade-off 并加 snapshot/restore。**省内存/省拷贝 vs 自检正确性的取舍必须在代码注释落字。**
- 缘起：R14 H1 zero_recovers 假 FAIL（identity 在被 focus/nofocus 推进后的态上比 nofocus 态 → 必失配）；
  R15 修法 = h1_state_save/restore 同态比较。host test 须扩展覆盖**有状态比较契约**（非仅无状态 kernel）。
```

### (c) PM dispatch discipline — 落 team_config（三道关旁）
`.claude/team_config.md`，Three-gate verification 节内（或紧邻）新增一条 bullet：
```
- **有状态链 package 的 critic checklist 强制 cross-item**：派 stateful-chain（FIRA/逐帧延迟线/任何跨帧
  态）测量或自检 package 时，lead 在派单 prompt 显式要求 critic **枚举所有跨 span 共享态 × 所有读它的
  probe/计数器，逐格裁**（ST1-E）。不得只裁主路径。缘起 R14/R15 H1。
```

## 5. decisions_log row draft（FG-BLOCKER episode）

### summary-table 行
```
| **H1 FG-BLOCKER→R15** | ✅ **ST1 自检缺陷诊断确认·数据 quarantined 不 salvage·fix+re-run·MAC-2x 发现**（2026-06-05）| R14 H1 板跑 g_h1_fg_zero_recovers=0：根因=**ST1 跨态 CRC 自检设计缺陷**（identity probe 在被 focus/nofocus 推进后的 FIRA 态上比 nofocus 态→有状态链必假失配；非聚焦机制 bug——focus_differs=1 证 focus 真算）。host test 当初漏=只测无状态 kernel。CTO 批 fix(a) snapshot/restore 同态比较 + 不 salvage quarantined（focus=590,137/nofocus=524,727/focus_only=65,410）。**MAC-2x 发现**：harness sz[]=8+16+32+64=120 samp/frame（sb3 未抽取）=真值；cost-model 2.88 MMAC/s 误设 60 samp→真 5.76 MMAC/s（2x），envelope 重标 86-144→**173-288 MCPS**[L4]；DEC-S5-V1-SCOPE-01 focus 预算疑 2x 低估（FLAG CTO，待板 focus_only[L1] settle）。三硬化入档（critic ST1-E 枚举消费者/harness probe-态隔离/PM cross-item checklist）。fix→critic R15→re-run（C10）。详见 sprint5/H1_R15_FIX_PACKAGE.md |
```

### 详细节
```
### DEC-S5-H1-R15-01：H1 FG-BLOCKER 诊断 + R15 修复 + MAC-2x 校正（2026-06-05）
- **FG-BLOCKER 根因**：g_h1_fg_zero_recovers=0 = **ST1 自检设计缺陷**（非聚焦 bug）。FIRA 链 s_h1_fa 跨帧
  有状态；R14 probe 三帧（focus/nofocus/identity）顺序推进同一态，identity 在 S2 态 vs nofocus S1 态比 CRC
  →有状态链必失配。focus_differs=1（聚焦机制真算）独立证 mechanism 无 bug。host test 漏=只测无状态 kernel
  （memset hist 每次），未覆盖有状态全链比较契约。
- **裁定（CTO）**：fix(a) state snapshot/restore 同态比较；NO salvage quarantined（focus/nofocus/focus_only
  全弃，cross-state run）；R15 re-gate + 板 re-run。
- **R15 修法**：h1_state_save/restore（s_h1_fa + s_fd_hist 一并）；三帧各 restore 到同一快照态再跑同输入
  （restore 在计时 span 外）；identity 现 == nofocus 逐位（true continuity）；A/B 现 same-state（方法学 delta：
  re-run 数取代 quarantined）。+ D-cache invalidate（flush_data_buffer，A5 符号）→ true-cold-DATA WCET
  （I-cache 仍暖=C10 板项，I 侧符号 TBD；仍系统 WCET 下界）。
- **MAC-2x 发现/校正**：harness 真 sz[]=120 samp/frame/ch（sb3 未抽取，fira_regression.c:195 / h1_wcet_measure.c:235 [R33 改锚]）=真 5.76 MMAC/s；
  cost-model 2.88 误设 60 samp=2x 低。「EXACTLY 2.88」claim 撤（R14 验公式未验 sz[]）。envelope 重标
  86-144→**173-288 MCPS [L4]**（5.76×30-50 cyc/MAC）。yardstick：board cyc ←→ 173-288。
- **产品成本 FLAG（不静默改 DEC-S5）**：产品聚焦同作用 120-samp 子带→真成本 ~5.76 MMAC 级→DEC-S5-V1-SCOPE-01
  「focus 86-144」疑 2x 低估（真 ~173-288）；§8 残余若采新值收紧 ~1.08x–1.69x——**worst 1.08x 距 1.0x 临时下限仅 0.08x（刀刃），且 focus[L4]/WCET[L3] 两主导项未实测，任一恶化即破线；板 L1 实测前不可断言 1.0x 守得住**（critic R15 修正）。≥1.5x 明显不达，≥2x 死。
  **待板 focus_only [L1] 直接 settle，CTO 据 L1 更新 DEC-S5。** 不静默改。
- **三硬化**：critic §12 ST1-E（裁「无害」须枚举所有消费者逐项裁）+ harness probe/态隔离规则 + PM stateful-chain
  cross-item checklist（均 team_config / critic skill，§4 change blocks）。
- **状态**：R15 fix 待 critic→板 re-run（C10）。quarantined 数作废。MAC envelope 173-288 [L4]。DEC-S5 focus
  预算 FLAG 待 L1。
```

## 6. Desktop verification evidence (关①)
- `gcc -c -O2 -Wall -Wextra`（FIRA off，编 .o）：**EXIT 0，0 警告**（snapshot/cache helpers TARGET-guarded）。
- **host test EXTENDED**（h1_host_test.c +check4，覆盖有状态比较契约——这次能覆盖 R14 漏的）：**PASS**
  - check4a：WITHOUT restore，identity != nofocus（**复现 R14 false-FAIL** 的有状态根因）。
  - check4b：WITH snapshot/restore，identity == nofocus（**证 R15 fix 恢复 continuity**）。
  - check1-3（无状态 kernel）仍 PASS。
- **诚实**：host 仍**不能**测 FIRA 链真态/真 cyc/真 cache——check4 用 1-pole 累加器 stand-in 模拟「跨帧推进态」
  以覆盖**比较契约逻辑**（snapshot/restore 是否恢复同态比较）；FIRA 链真 bit-exact + 真 cycle + cache 行为
  **待板**。板 FG 将证：g_h1_fg_zero_recovers=1（同态 continuity 真成立）。
- ASCII-only clean；frozen 未动；只改两 H1 文件（已 tracked，lead 2a50f51 提交；本轮 uncommitted 修改）。

## 7. 无法从桌面核实
- 板上 same-state re-run 的 focus_only/WCET/FG 真值（待板 [L1]）；I-cache invalidate 符号（C10 板项，desktop 不知）。
- 真 DMA 争用/ISR（harness 测不到，WCET 仍下界）。
- decisions_log/critic-skill/team_config 精确行号（随提交漂移；锚字符串定位，lead apply 复核）。
