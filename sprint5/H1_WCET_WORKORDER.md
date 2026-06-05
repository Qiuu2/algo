# WO-S5-H1: Focusing-increment + WCET combined measurement (H1) — WORK ORDER DRAFT

> 〔H1 v2 已板跑：focus_only=49.03 MCPS[L1]，173-288 yardstick settle，实测 8.51 cyc/MAC<30-50 类；DEC-S5-BUDGET-L1-01〕

> 三道关自指：本工单 = workflow 产出 → 关①已过（本 teammate 自验 + 桌面 gcc + host run）；
>   **关② = critic R14（独立门，待）**；**关③ = CTO 常识审 + C10 bringup checklist（板跑前，待）**。
> 缘起：DEC-S5-OPT-ORDER-02（CTO 2026-06-05）执行顺序第 1 项「focusing-harness + WCET 同板跑」。
> NO commit before independent critic verdict（F7 line 同纪律）。frozen files untouched。ASCII-only target。
> RAW counters only（C9 analog：代码零 derived margin，全 off-board 算）。FREE-RUN（无 mid-loop 断点，idle 读）。

---

## 0. 交付物清单
- **新文件**（首选，blast radius 最小——F7 PASS 路径 byte-identical 不动）：
  - `sprint5/dsp/harness/h1_wcet_measure.c` — H1 测量主体（focus 增量 A/B + WCET cold/warm/max + ride-along）。
  - `sprint5/dsp/harness/h1_host_test.c` — 桌面自验（focus FIR + FG 逻辑，host 可跑）。
- **change block**（bench_main.c 接线，§3）——唯一对 tracked 文件的改动，6 行，在 F7 hook 之后。
- 桌面验证证据（§4）｜读出 worksheet（§5）｜DEC 行草案（§6）。

## 1. 测什么（对应 CTO 三项）
| 块 | 目标 | 升级 |
|---|---|---|
| **A 聚焦增量** | 同 build A/B：8ch FIRA 链 (analyze + per-sb focus FIR + synth) 一帧 focus-ON vs OFF | 173–288 MCPS [L4-recalibrated，R15 MAC-2x 校正；原 86–144 系 2.88 误设] → [L1] |
| **B WCET** | cold-**代理**（H1 首帧；**I-cache 已被 F4/F5/F7 同路径焐热，仅 H1 自有数据缓冲首触——部分冷代理，低估真冷 WCET**，critic R14）vs warm（稳态）+ max/min over 64 帧 jitter | WCET 乘子 [L3] → [L1]（可测部分，**下界**） |
| **C ride-along** | per-run CCLK 复读（应==1e9）+ FG（focus 输出≠nofocus、零延迟==nofocus） | sanity + 假绿防护 |

## 2. 设计要点（与 critic 必查项对齐）

### 2.1 聚焦 FIR 选择 + MAC 校正（critic R15，CTO-flagged 2x）
- 实现 = **8-tap 分数延迟 FIR，per-subband（4 子带）per-channel**，作用在 analyze 输出的 4 子带（analyze 与
  synthesize 之间）。
- **真 MMAC（R15 校正）**：真子带 sample 数/帧（源 fira_tree.c:49-52）= sb0/8 + sb1/16 + sb2/32 + sb3/64 =
  **120 samp/帧/ch**（sb3 未抽取，sb3[i]=in[i]-r1[i]）→ 子带率和 = 120×750 = **90 kHz**（非 45kHz）。
  8 tap × 120 samp × 8 ch × 750 fps = **5.76 MMAC/s**（非 2.88）。
- **校正留痕**：原「EXACTLY 2.88 MMAC/s」**错 2x**——cost-model 2.88 误设 60 samp/帧（45kHz）；真树 120 samp
  （90kHz）。R14 验了公式未验 sz[]。harness 实现 = **5.76 MMAC/s（真树结构）**=真值，非夸大。
- **yardstick（重标）**：board cyc ←→ **5.76 MMAC/s × 30-50 cyc/MAC = 173-288 MCPS [L4-recalibrated]**
  （非旧 86-144=2.88-based）。等价 g_h1_cyc_focus_only/2 ←→ 86-144；取前者（真 120-samp 工作对真 envelope）。
- **产品成本 FLAG**：产品聚焦同作用 120-samp 子带→真成本 ~5.76 MMAC 级→DEC-S5「focus 86-144」疑 2x 低估
  （真 ~173-288），FLAG CTO，待板 focus_only [L1] 直接 settle，不静默改 DEC-S5。详见 H1_R15_FIX_PACKAGE §3。
- 拒绝的替代：full-rate 16-tap pre-analyze = 6.14 MMAC/s（~2.1x 重）→ 会测出虚高增量。已 justify 在代码头注。
- 8 distinct 延迟（mirror-symmetric，{c,15-c} pair phase-locked，STEER-2 物理）；静态 set 一次（区延迟更新率~0）。
- **非产品聚焦算法、非 bit-exact-gated**：focus 阶段 **in-place 作用于 H1 自有的本地子带缓冲（fsb0-3）**，喂 H1 自己的 synthesize；**F4/F5 的缓冲与 CRC 路径完全分离、未触碰**（critic R14 措辞修正），**不碰冻结 filterbank**——故不需重 R14。它是**代价 stand-in**，测的是 board cyc（真值），桌面 MMAC 只是设计锚。

### 2.2 F7 mixed-build 陷阱规避（同 build A/B）
- 官方增量 = **run 内 delta**：`g_h1_cyc_8ch_focus - g_h1_cyc_8ch_nofocus`，两 span 同 run、同帧、同循环结构，
  仅 focus 阶段开关不同。**非跨 build**（F7 教训：3.07x 用 in-build A/B 正是避此）。
- 注（critic R14）：focus-ON span 先跑，使 s_h1_fa FIRA 状态前进一帧后 focus-OFF span 再 analyze——两 span 滤波状态不同；对 **cycle 计数**可忽略（两路径逐样本操作数相同），增量有效。

### 2.3 假绿纪律（FG）
- **FG-1 focus 真算**：`g_h1_fg_focus_differs==1` 要求 focus-ON 输出 CRC ≠ focus-OFF（延迟确实改变输出）。
  桌面已证：8 套 coeff 全改变输出（check2 PASS）。占位/零增量会 FAIL 此门。
- **FG-2 连续性**：`g_h1_fg_zero_recovers==1` 要求零延迟（pass-through）配置复现 no-focus 路径**逐位**。
  实现 = use_identity 时**跳过 focus 阶段**（真 pass-through，非 32767/32768 近似）→ 桌面 check1/check3 PASS。
- **FG-3 桌面诚实 0**：`fira_tree_setup()<0`（desktop）→ 返 0，全 g_h1_*=0/sentinel，绝不假造 cycle（同 F7 FG2）。

### 2.4 WCET 诚实 scoping（HARD —— 必须明说，不得 overclaim）
- **CAN 测**：cold-**代理**（H1 首帧 vs 稳态；I-cache 已热，部分冷，**低估真冷**）+ intra-run jitter（max/min over 64 帧）。**真冷测量需在该帧前做 I+D cache 失效（板侧，见 C10 TODO）**。
- **CANNOT 测**：真实 SPORT/codec DMA 总线争用（bench 无 DMA 在跑）+ ISR 抢占（bare-metal free-run 无中断）。
- **结论口径**：测得 WCET = **系统 WCET 的下界**；未测的争用/抢占分量留 [L3/L4]，与 §8 io/irq 包络并存。
  **禁止**把 g_h1_cyc_8ch_max 当 full-system WCET。代码头注 + 本工单双处落字。

### 2.5 C9 analog / free-run / frozen
- 代码**零 derived margin**（无 86-144、无 2.04x 等计算）；只存 raw counters + Hz + FG flag。margin off-board 算。
- **free-run**：无 mid-loop 断点（CCNT_source.md 教训：SLOWLOOP+断点死锁计数循环）；只在 idle while(1) 读 g_h1_*。
- frozen 文件（tree_filterbank.c/tfb_8ch.c/golden_ref.h/chirp_input.h/fir_coeffs_hb63.h/.ldf）**未动**；
  harness 只 #include 非冻结 header（tree_filterbank.h/fir_coeffs_hb63.h 只读用）+ extern 现成 entry。
- **栈纪律**（F7-FIX2 教训）：大 state（s_h1_fa[8]、s_fd_hist、s_fd_coeff）全 static off-stack；
  帧内栈局部仅 fsb/fout/xw/scr（BENCH_FRAME=64 量级，~1.5KB）——无 L1 Block-0 栈溢出风险。

## 3. bench_main.c 接线 change block（唯一 tracked 改动）

> 在 F7 hook（`g_fira_f7_done = fira_f7_measure();` + 其 breakpoint 注释，bench_main.c:223-226）**之后**、
>   `#endif`（:227）**之前**插入。需在文件 extern 区（F7 externs 附近，:79-92）加 H1 externs。

**(i) extern 声明**（加在 bench_main.c 的 F7 extern 块内，`extern volatile int g_f7_cclk_rc;` 之后）：
```c
/* H1 (WO-S5-H1): focusing-increment + WCET combined measure (defined in sprint5/dsp/harness/h1_wcet_measure.c) */
extern int      h1_wcet_measure(void);
extern volatile uint32_t g_h1_cyc_8ch_focus, g_h1_cyc_8ch_nofocus, g_h1_cyc_focus_only;
extern volatile uint32_t g_h1_cyc_8ch_cold, g_h1_cyc_8ch_warm, g_h1_cyc_8ch_max, g_h1_cyc_8ch_min;
extern volatile uint32_t g_h1_cclk_hz, g_h1_focus_crc, g_h1_nofocus_crc;
extern volatile int      g_h1_cclk_rc, g_h1_fg_focus_differs, g_h1_fg_zero_recovers, g_h1_valid;
volatile int g_h1_done = -99;   /* 1=on-board w/ FIRA / 0=desktop no-FIRA / -99 not-run */
```

**(ii) 调用点**（在 bench_main.c:226 的 F7 breakpoint 注释之后，:227 `#endif` 之前）：
```c
    /* ---- H1 (WO-S5-H1): focusing-increment same-build A/B + WCET cold/warm/max. Runs AFTER F7 with
     *   its OWN setup/state/buffers -> does NOT perturb F4/F5/F7 PASS paths. RAW counters only (C9).
     *   FREE-RUN: read g_h1_* at idle only (no mid-loop breakpoints). ---- */
    g_h1_done = h1_wcet_measure();
    /* breakpoint here (idle, after the run): read
     *   A focus increment: g_h1_cyc_8ch_focus - g_h1_cyc_8ch_nofocus (= g_h1_cyc_focus_only) [L1 cyc]
     *   B WCET (LOWER BOUND): g_h1_cyc_8ch_cold / g_h1_cyc_8ch_warm (cold/warm) + g_h1_cyc_8ch_max/min (jitter)
     *   C sanity: g_h1_cclk_hz(==1e9?)/g_h1_cclk_rc(==0?) + FG g_h1_fg_focus_differs(==1)/g_h1_fg_zero_recovers(==1)
     *   off-board: focus MCPS = increment*750/1e6; WCET multiplier = max/warm; ALL paired with section-8 denom (C9). */
```

**Project 设置**：把 `sprint5/dsp/harness/h1_wcet_measure.c` 加进 FIRA build 的 source list（同 fira_regression.c）；
include path 加 `sprint5/dsp/harness`（或就近）。core-only build 不含此文件（H1 是 FIRA-build-only）。

## 4. 桌面验证证据（关①）
- `gcc -fsyntax-only -Wall -Wextra`（FIRA 路径 off）：**EXIT 0**，无警告。
- `gcc -c -O2 -Wall -Wextra`（编 .o）：**EXIT 0**，**0 警告**（focus helpers TARGET-guarded，desktop 无 unused）。
- `h1_host_test.c` build + run：**PASS**（check1 零延迟 pass-through==输入；check2 8 套 coeff 全改输出；
  check3 identity CRC==输入 CRC 0xEB9BD3C6 且 focus CRC 0x40D1B3AF≠输入）→ FG 逻辑桌面坐实。
- ASCII-only：**clean**（grep 非 ASCII = 空）。
- frozen 文件：**未动**（git status 仅新文件，无 tracked 改；bench_main change block 待 lead apply）。

## 5. 读出 worksheet（idle 读；期望区间 + 偏差含义）

| 全局 | 期望 | 偏差含义 |
|---|---|---|
| `g_h1_done` / `g_h1_valid` | **1**（板上 FIRA 跑） | 0=fira_tree_setup 失败/桌面（全数无意义）；-99=未跑 |
| **A. `g_h1_cyc_8ch_focus`** | > nofocus，多出 ~focus 增量 | [L1 cyc] |
| **A. `g_h1_cyc_8ch_nofocus`** | ≈ F7 g_f7_cyc_8ch_fira（463,273 量级，同 8ch analyze+synth 无 focus） | 偏离大→harness 链与 F7 不一致，先查 |
| **A. `g_h1_cyc_focus_only`** | = focus − nofocus（**same-state A/B，R15**）；**focus MCPS = 值×750/1e6 应落 173–288 [L4-recalibrated, 5.76 MMAC]** | 远超 288→实现比 5.76 重（查 tap/sz[]）；≈0→focus 没真算（查 FG）；落 86-144→疑仍按旧 2.88 解读，用 173-288 yardstick |
| **B. `g_h1_cyc_8ch_cold`** | > warm（数据侧首触惩罚）；cold/warm 比 = WCET **下界**乘子（**部分冷代理：I-cache 已热，低估真冷**；off-board 计算必须带此 caveat）| < warm 反常→测序/warm-up 逻辑错 |
| **B. `g_h1_cyc_8ch_warm`** | 稳态值（== g_h1_cyc_8ch_focus，同稳态帧） | — |
| **B. `g_h1_cyc_8ch_max` / `_min`** | max≥warm≥min；(max−min)/warm = jitter 带宽 | max 离群极大→单帧异常（cache/对齐），记录但勿当系统 WCET |
| **C. `g_h1_cclk_hz`** | **1,000,000,000**（G6 一致） | ≠1e9→CGU 变/读失败（查 g_h1_cclk_rc） |
| **C. `g_h1_cclk_rc`** | **0** | ≠0→GetCoreClkFreq 失败，cclk 无效 |
| **C. `g_h1_fg_focus_differs`** | **1**（focus 输出≠nofocus=延迟真算） | **0=假绿 BLOCKER**：focus 阶段没改变输出，增量无意义 |
| **C. `g_h1_fg_zero_recovers`** | **1**（零延迟复现 nofocus） | 0=连续性破，focus 路径污染了 nofocus 基线，增量不可信 |
| `g_h1_focus_crc` / `g_h1_nofocus_crc` | 二者**相异**（focus≠nofocus 的 CRC 证据） | 相等→同 g_h1_fg_focus_differs==0 |

**off-board 算（C9，连体 §8 呈现）**：focus MCPS = g_h1_cyc_focus_only×750/1e6（验 **173–288 [L4-recalibrated]**→[L1]；旧 86-144=2.88 错值已撤，R15）；
WCET 下界乘子 = g_h1_cyc_8ch_max / g_h1_cyc_8ch_warm（喂 DEC-S4-CRITERION-01 正式阈值，标「下界，未含 DMA/ISR」）。

## 6. DEC 行草案（供 lead 追加 decisions_log）

### summary-table 行
```
| **执行顺序 v2** | ✅ **harness+WCET 同板跑优先 / R3 次 / HW-1 可选**（DEC-S5-OPT-ORDER-02，2026-06-05，CTO 确认逐字）| (1) focusing-harness + WCET 实测**同一板跑**——WCET 是正式阈值最后一块，先测；(2) R3 消声室（band 数+efficacy，待 T/S 2–4 周）；(3) HW-1 降级**可选**（仅当 WCET 后追 ≥2x 才重启）。理由：EQ 威胁坍缩 0–150→29–60 非承重；WCET 是阈值 blocker。验收 X 保持 OPEN 直到 R3 给真实可达值。工单 WO-S5-H1（harness 代码→三道关→CTO 同步+板跑，F7 流程）|
```

### 详细节
```
### DEC-S5-OPT-ORDER-02：执行顺序 v2（CTO 确认逐字，2026-06-05）
- **裁定（substance 逐字）**：(1st) focusing-harness + WCET measurement SAME board run——WCET 是正式阈值
  的最后一块，measure first；(2nd) R3 anechoic（band count + efficacy，待 T/S 2–4 weeks）；HW-1 降级 optional
  （仅当 WCET 后 chasing >=2x 才 revisit）。Rationale：EQ threat 坍缩 0–150→29–60 non-load-bearing；
  WCET 是 threshold blocker。验收 X 保持 OPEN 直到 R3 给 real achievable values。
- **取代** DEC-S5-OPT-ORDER-01 排序（HW-1 最高优先 rationale 被 item-3=O1 裁定 overtaken，DEC-S5-EQ-O1-01）。
- **harness=WO-S5-H1**：sprint5/dsp/harness/h1_wcet_measure.c（focus 增量同 build A/B + WCET cold/warm/max
  + ride-along），dsp code → 三道关（关①桌面自验过；关② critic R14 待；关③ CTO+C10 bringup 待）→ 板跑。
  raw counters only（C9）；free-run（无 mid-loop 断点）；frozen 未动；F4/F5/F7 PASS 路径 byte-identical。
- **依赖链**：WCET [L1]（本工单）→ DEC-S4-CRITERION-01 正式实时余量阈值最后依赖解除 → CTO 拍阈值。
  focus 增量 [L1]（本工单）→ DEC-S5-V1-SCOPE-01 算力侧 86–144 [L4]→[L1]。R3 → EQ band 数 + efficacy [L2]→[L1]。
- **状态**：顺序 v2 锁定；WO-S5-H1 待板跑；X 保持 OPEN（DEC-S5-V1-SCOPE-01）。
```

## 7. Follow-up / 板跑前 checklist（C10，CTO-gated）
- 关② critic R14 PASS（独立门）→ 关③ CTO 常识审 + C10 bringup checklist（上电/JTAG 安全，同 F7）。
- 板跑后读 §5 worksheet（idle，free-run）；off-board 算 focus MCPS + WCET 下界乘子，连体 §8 呈现。
- 若 g_h1_fg_focus_differs==0 或 g_h1_fg_zero_recovers==0 → BLOCKER，增量数作废，先修 FG。

## 8. 无法从桌面核实（explicit）
- 板上 focus 增量/WCET cold/jitter 真值（[L4]→待板跑 [L1]）；CCLK 复读（应 1e9，待板）。

## C10 板跑清单补充（critic R14 F14-MAJOR-1）
- **真冷 WCET（可选增强）**：若要把 cold 从"部分冷代理"升为真冷，板侧在 cold 帧前执行 I+D cache 失效（BSP `flush_data_buffer` + I-cache invalidate；ADI 符号以 CCES 文档为准，桌面无法盲写）。不做则 cold 读数一律按"部分冷代理/低估真冷"口径引用。
- 真实 DMA 争用 / ISR 抢占（本 harness 测不到，WCET 仅下界，留 [L3/L4]）。
- 无 SHARC/板：桌面验 = focus FIR 逻辑 + FG + 编译；FIRA span 行为待板。bench_main change block 待 lead apply+复核行号。
