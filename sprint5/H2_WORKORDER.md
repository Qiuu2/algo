# WO-S5-H2: DMA bus-contention + ISR-preemption measurement harness — WORK ORDER DRAFT

> 三道关自指：关①已过（本 teammate 自验 + gcc 桌面路径 + guard-stub 检查 h1+h2 + host test + 证伪）；
>   关② = critic R19（独立门，待）；关③ = CTO 同步 + C10 bringup checklist（板跑前，待）。
> 缘起：CTO 批 WO-S5-H2 = T2（>=1.5x）系统侧闭合钥匙（DEC-S4-CRITERION-01-FINAL）。
> NO commit before independent critic verdict（H1/F7 同纪律）。frozen 未动；ASCII；RAW counters only（C9）；free-run。

---

## 0. 交付物
- **新文件**（blast radius 最小，不动 h1/fira_regression 的 PASS 路径）：
  - `sprint5/dsp/harness/h2_dma_isr_measure.c` — H2 测量主体（DMA 争用 + ISR 抢占 + 联合 WCET + FG）。
  - `sprint5/dsp/harness/h2_host_test.c` — 桌面自验（A/B + FG 逻辑）。
- **板侧 hook TU（不在仓，CTO/bring-up 写）**：`h2_board_hooks_<board>.c` — 实现 4 个 extern hook（见 §3）。
- **change block**（bench_main.c 接线，§4）+ guard-check 已泛化覆盖 h2（run_guard_check.sh）。
- 读出 worksheet（§5）+ 阈值灵敏度（§6）+ DEC 行（§7）。

## 1. 测什么（对应 CTO A/B/C/D）
| 块 | 目标 | 升级 |
|---|---|---|
| **A DMA 争用** | 8ch FIRA 帧 cycle WITH 总线负载流 vs WITHOUT（同 build A/B）= 争用增量 | io 5-30 [L3] → 争用份额 [L1] |
| **B ISR 抢占** | 8ch FIRA 帧 cycle WITH 周期 ISR vs WITHOUT = ISR 增量 | irq 2-15 [L3] → [L1] |
| **C 联合 WCET** | A+B 同时, max-over-N 帧 = 争用 WCET 乘子（仍排除 I-cache cold） | WCET +10-50% [L3] → 争用部分 [L1] |
| **D FG** | DMA-off 控制零增量 + ISR 计数交叉核 + 占位失败 | 防假绿 |

## 2. 设计要点（与 critic 必查项对齐）

### 2.1 DMA = MDMA 内存-内存 PROXY（CTO 预批，诚实标注 + 总线类等价 justify）
- 产品 DMA = SPORT4 TDM 乒乓（ADAU1979 in / ADAU1962A out，8 slot×32bit@48k=BCLK 12.288MHz，DOC-S4-IO-01）。
- **争用机制 = 同一系统 crossbar 的总线仲裁**，与哪条 DMA 通道（SPORT-PDMA 或 MDMA）无关。MDMA 流按
  **同聚合字节率**（8slot×4B×48k×2 dir = 3,072,000 B/s，H2_DMA_BYTES_PER_S）压 crossbar = 同类总线负载
  → MDMA proxy 诚实捕获**争用增量**。
- **proxy 漏什么（明说不藏）**：真 SPORT 路径还有每块 RX/TX 回调的 **core 成本**（descriptor 服务 + cache-inval），
  MDMA 自动重填**不产生**该 core 成本。该回调 core 成本 = sec-8 item-1「codec/IO DMA」份额，**非争用份额**。
  故本 harness 测**争用 [L1]**（proxy）；**回调 core 成本须真 SPORT bring-up**（更重 harness/future）= 留 [L3] flag。
  → io 包络 5-30 拆 = 争用（此处测）+ 回调（SPORT bring-up 前仍 [L3]）。

### 2.2 ISR = 周期 timer ISR，product-representative 率（justify）
- v1 bare-metal 产品中断源：(i) 音频**帧 ISR @ FS/FRAME = 48000/64 = 750 Hz**（SPORT block-done 乒乓，DOC-S4-IO-01）；
  (ii) 低率控制/UI tick（~1 kHz 典型 bare-metal 控制环；芯片决定无 ARM/net/display=**无 RTOS=无调度器 tick**）。
- H2 建模**主导抢占源 = ~1 kHz timer ISR**（最小 handler：计数 + ack）。H2_ISR_HZ 旋钮，默认 1000。
  （帧 ISR 750Hz 若 A 的 SPORT bring-up 带来则一并，但本 proxy 用 MDMA 无 SPORT block ISR → ISR 由 timer 建模。）

### 2.3 同 build A/B + ST1-E（每个 A/B 仅一因子不同）
- 三个 A/B（DMA / ISR / both）**都减同一个 baseline** `g_h2_cyc_frame_base`（无 dma 无 isr），同输入帧、同 s_h2_fa
  状态推进序、同循环。每次只切**一个**负载开关 → 增量纯。（ST1-E：跨 span 共享态 s_h2_fa 逐项核——baseline/dma/isr
  各跑一帧推进态，但**增量是 cycle 不是 CRC**，cycle 对状态推进不敏感；且 dma/isr 用与 baseline **同一输入帧**，
  对比的是同位置帧的 cycle，状态偏移仅一帧 << 争用/ISR 增量量级。已在注释落字。）

- **ST1-E 第二跨 span 态 = g_h2_isr_count**（off-control 段 + ISR 段读）：off-control 在 ISR 装载前跑（count 恒 0），ISR 段与之互斥，故 off==0 ∧ growth>0 是干净交叉核——已逐项核（critic R19 F19-MINOR-1 补全枚举）。

### 2.4 假绿纪律（FG）
- **FG-A DMA 真压**：`g_h2_fg_dma_loads==1` 要求 dma 帧 > base（总线真争用）。dead hook（不压）→ 增量 0 → FG=0。
  host check1/check3 已证（check3 = no-op busload 抓 inc=0/FG=0）。
- **FG-B ISR 真触**：`g_h2_fg_isr_fires==1` 要求 ISR 计数在计时帧内增长 **AND** ISR-off 控制段计数恒 0
  （`g_h2_isr_count_off==0`）。占位/未真装 ISR → 计数不长 → FG=0。host check2 已证。
- **FG-C 桌面诚实 0**：无 FIRA + 无板 hook → 返 0，全 g_h2_*=0/sentinel（FG2，同 F7/H1）。

### 2.5 C9 / free-run / frozen / 栈
- 零 derived margin（无 io/irq/WCET 计算）；只存 raw counters + FG flag；margin off-board。
- free-run，idle 读 g_h2_*（无 mid-loop 断点）。frozen 未动（只 #include 非冻结 header + extern 现成 entry）。
- 大态 s_h2_fa[8] static off-stack；帧内栈局部 fsb/fout/xw（~1KB）——无 L1 Block-0 栈溢出（FIX2 教训）。

## 3. 板侧 hook 规约（C10 bring-up 写 `h2_board_hooks_<board>.c`，不在仓）
4 个 extern（h2_dma_isr_measure.c 声明），真 BSP 实现：
```c
int  h2_busload_start(uint32_t bytes_per_s);  /* 启 MDMA 内存-内存流压 ~bytes_per_s; 返 0=ok。BSP adi_mdma_*/PDMA descriptor */
void h2_busload_stop(void);                   /* 停 MDMA 流 */
int  h2_isr_start(uint32_t hz);               /* 装周期 timer ISR @hz; handler 必须 ++g_h2_isr_count 并 ack timer; 返 0=ok */
void h2_isr_stop(void);                       /* 卸 ISR */
```
- **ISR install 符号 = C10 板项**（iface_survey G7：adi_int.h 是 ARM/GIC，SHARC 侧中断控制器不同 → install 符号
  须板侧确认，**与 I-cache invalidate 符号同类未知**）。timer = adi_tmr_*（adi_tmr 存在性见 BSP）。
- handler 极简（计数 + ack），其自身 core 成本是被测 ISR 成本的一部分（诚实：测的是「该最小 handler」的抢占成本，
  产品真 handler 若更重则更高——off-board 标注）。
- **【R24 F24-MAJOR-1 board-confirm】proxy 缓冲总线段放置 = 测量效度命门**：`s_bh_src/dst` 无 section pragma，
  板上落位由 linker 决定。bring-up **必须**显式定到与产品 SPORT-PDMA 同总线段、且**不得**与 FIRA 工作集
  （s_h2_fa）同 L1 block——否则 inc_dma 测的是自冲突假象（产品不存在）而非 crossbar 争用。**读数解释前先核
  .map 放置**。
- **【R24 F24-MINOR-2】bring-up 须确认 `ADI_MDMA_MEMORY`/`ADI_TMR_MEMORY` 来自真 header 而非 hook TU 的
  parse fallback**（板 build 对 `H2_BH_USED_FALLBACK_MDMA_MEMORY` 标记 #error 守卫，或查预处理输出）——fallback
  被采用 = 服务内存可能 undersized（open 越界写）。
- **【R24 F24-MINOR-1】重武装漂移方向**：one-shot 重武装含 callback 软件延迟 δ，实际 ISR 率略低于标称 hz →
  inc_isr 为该（略低）率下的抢占成本，方向上偏低估（二阶：δ~数十 cyc vs 周期 ~125k cyc，<<1%）；bring-up 若
  确认 `ADI_TMR_MODE_CONTINUOUS_PWMOUT` 存在则切换消除。

## 4. bench_main.c 接线 change block（在 H1 hook 之后）
**(i) extern**（加在 H1 extern 块后）：
```c
/* H2 (WO-S5-H2): DMA/ISR contention measure (defined in sprint5/dsp/harness/h2_dma_isr_measure.c) */
extern int      h2_dma_isr_measure(void);
extern volatile uint32_t g_h2_cyc_frame_base, g_h2_cyc_frame_dma, g_h2_cyc_frame_isr;
extern volatile uint32_t g_h2_cyc_frame_both_max, g_h2_cyc_frame_both_min, g_h2_inc_dma, g_h2_inc_isr;
extern volatile uint32_t g_h2_isr_count, g_h2_isr_count_off;
extern volatile int      g_h2_fg_dma_loads, g_h2_fg_isr_fires, g_h2_valid;
volatile int g_h2_done = -99;
```
**(ii) 调用点**（在 H1 hook 之后，FIRA `#endif` 之前）：
```c
    /* ---- H2 (WO-S5-H2): DMA contention + ISR preemption. Own state/buffers; does NOT perturb F4/F5/F7/H1.
     *   RAW counters only (C9). FREE-RUN: read g_h2_* at idle only. Needs board hooks (h2_board_hooks_*.c). ---- */
    g_h2_done = h2_dma_isr_measure();
    /* breakpoint here (idle): g_h2_valid / g_h2_fg_dma_loads(==1) / g_h2_fg_isr_fires(==1) /
     *   g_h2_inc_dma / g_h2_inc_isr / g_h2_cyc_frame_both_max / g_h2_cyc_frame_base / g_h2_isr_count(_off==0)
     *   off-board: io MCPS = inc_dma*750/1e6 ; irq MCPS = inc_isr*750/1e6 ; WCET mult = both_max/base ; sec-8 paired. */
```
project: 把 `h2_dma_isr_measure.c` + `h2_board_hooks_<board>.c` 加进 FIRA build source list。

## 5. 读出 worksheet（idle 读；期望区间 = 当前 [L3] 包络作 yardstick）

| 全局 | 期望 / yardstick | 偏差含义 |
|---|---|---|
| `g_h2_done`/`g_h2_valid` | 1 / 1 | 0=fira_setup 失败/桌面/无 hook（全数无意义）；-99=未跑 |
| `g_h2_cyc_frame_base` | ≈ H1 g_h1_cyc_8ch_nofocus（~525,850 量级，同 8ch 无 focus 链） | 偏离大→链与 H1 不一致，先查 |
| **`g_h2_inc_dma`** | **io MCPS = inc×750/1e6，yardstick 5-30 MCPS [L3]** | 远超 30→proxy 压过头（查 bytes_per_s）**或 proxy 缓冲落 FIRA 同 L1 段=自冲突假象（R24，先核 .map 放置）**；=0→FG-A 应=0（dead hook） |
| **`g_h2_inc_isr`** | **irq MCPS = inc×750/1e6，yardstick 2-15 MCPS [L3]** | 远超 15→ISR 率/handler 过重；=0→FG-B 应=0 |
| **`g_h2_cyc_frame_both_max`** | WCET 乘子 = both_max/base，yardstick ≤ +10-50% [L3] | both_max/base 远超 1.5→争用极端，记录；< base 反常→测序错 |
| `g_h2_cyc_frame_both_min` | ≥ base；(max-min)/base = jitter 带 | — |
| `g_h2_fg_dma_loads` | **1** | **0 = BLOCKER**：总线没真压（dead/弱 hook），io 数无效 |
| `g_h2_fg_isr_fires` | **1** | **0 = BLOCKER**：ISR 没真触或 off-count≠0，irq 数无效 |
| `g_h2_isr_count`/`_off` | count>0（ISR 段）/ off==0 | off≠0→ISR 在不该跑时跑（装/卸序错） |

**off-board 算（C9，连体 sec-8 呈现）**：io = inc_dma×750/1e6；irq = inc_isr×750/1e6；
WCET 争用乘子 = both_max/base。三者 [L1] 替换 sec-8 [L3] 估值；I-cache cold 仍 [L3/L4] 待 C10。

## 6. 阈值灵敏度（CTO 要：板上要显示什么才把 worst 抬过 1.5x）— python 双核

公式：`margin_worst = 1000 / (347.45[L1核] + 49.03[L1 focus] + O1 + io + irq + WCET_contention + I_cold)`
- 现状 worst（全 [L3/L4] 估值高端）= 1000/(347.45+49.03+60+30+15+173.7) = **1.459x**（差 1.5x 之 2.7%）。
- **>=1.5x 要求**：总需求 ≤ 1000/1.5 = **666.67 MCPS**。
- 固定 [L1]+O1worst（核+focus+O1=60）= 456.48 MCPS → **(io + irq + WCET_contention + I_cold) 之和须 ≤ 210.19 MCPS**。
- 对照现高端估 (io30 + irq15 + WCET+50%=173.7) = 218.7 → **仅超 8.5 MCPS**。
  **=> 板上需把 (io+irq+争用WCET+I_cold) 的 L1 实测之和压到 ≤ 210.19 MCPS（O1=60 worst）/ ≤ 241.19（O1=29 best）才使 worst ≥ 1.5x；现高端估 218.7 超 8.51 MCPS。实测高于或低于此线由板决定——本节只给阈值灵敏度，不预判板上结果（R5/R7/R13 板决定纪律，critic R19 F19-MAJOR-1 修正）。**
- 若 O1 取 best=29：room 放宽到 ≤ 241.19 MCPS（更易过）。
- **样例**（python）：io=15/irq=8/WCET_cont=50/O1=60 → demand 529.5 → **1.889x**（过）；
  io=20/irq=10/WCET_cont=80/I_cold=0*/O1=60 → 566.5 → **1.765x**。
  **示例（非预测）**：IF io/irq/WCET/I_cold 实测落如上值 THEN margin 如上——用于读 worksheet，不预判板上结果。
  （*示例中 I_cold=0 系示例假设非实测；I_cold 仍 C10-pending，实际读数须计入。）
- **诚实**：I_cache cold 仍未测（C10），若它单独很大可吃掉余地——但 H1 已测 cold-DATA ~0，I-cold 是指令侧、
  对 FIRA 编排循环（指令局部性高、F4/F5/F7 已暖）预计小；待 C10 符号实测才能 [L1] 关死。

## 7. DEC 行草案（WO-S5-H2 登记 → 实现待门）
```
| **WO-S5-H2 实现** | 🟡 **DMA/ISR harness 代码就绪·待 critic R19 + 板 hook + 板跑**（2026-06-05）| H2 测 DMA 争用增量(MDMA proxy, 同聚合字节率 3.072MB/s, 诚实标 proxy 漏回调 core 成本)+ISR 抢占增量(~1kHz timer, 帧 ISR 750Hz 口径)+联合 WCET max/N, 同 build A/B 减同一 baseline(ST1-E)。FG 双门(DMA 真压/ISR 真触+off-count 0)+占位失败。板 hook 4 个 extern(busload/isr start-stop, ISR install 符号=C10 板项 同 I-cache 类)待 bring-up 写。桌面验:desktop 路径+guard-stub(h1+h2 证伪)+host test 全 PASS;ASCII;frozen 未动;RAW only。阈值灵敏度:worst 1.459x 距 1.5x 仅 2.7%;(io+irq+争用WCET+I_cold) L1 之和需 ≤ allowance 210.19 MCPS——板决定,不预判。是 DEC-S4-CRITERION-01-FINAL T2 系统侧闭合钥匙。详见 sprint5/H2_WORKORDER.md |
```

## 8. Honest scoping — 测不到的（明说）
- **I-cache cold WCET**：仍待 C10（SHARC I-cache invalidate 符号未知，桌面不知）。H2 测的是「I-cache 暖」下的
  争用+ISR；I-cold 是独立残余项。
- **真 codec 模拟路径 / SPORT 回调 core 成本**：MDMA proxy 不含每块 RX/TX 回调的 core 成本（descriptor 服务 +
  cache-inval）= io item-1 的一部分，须真 SPORT bring-up（更重 harness）才 [L1]。本 harness 测**争用**份额。
- **生产固件 ISR 混合**：建模单一 ~1kHz timer 最小 handler；真产品若多中断源/更重 handler → 实际更高，off-board 标注。
- 无 SHARC/板：桌面验 = A/B+FG 逻辑 + 编译 + guard-stub；真 DMA/ISR 行为待板 [L1]。

## 9. 三道关
- 关①过（桌面 gcc 双路径 + guard-stub h1+h2 证伪 broken FAIL/fixed PASS + host test PASS + ASCII + frozen）。
- 关② critic R19（独立门，待）。关③ CTO 同步 + C10 bringup checklist（板 hook 写 + 上电 JTAG 安全，待）。
