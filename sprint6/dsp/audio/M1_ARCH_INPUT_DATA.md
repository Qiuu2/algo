# M1_ARCH_INPUT_DATA — 数据调取型产出（CTO 派单 14 条目逐条）

> **类型**：数据调取型产出（只读取 + 列清单，不写实现、不做架构决策、不裁开口）。
> **格式**：按 CTO 派单 14 条目编号逐条，每条 = 数据 + [来源]。
> **纪律**：所有数字带来源（文件:行号 / datasheet 页-表号 / M1_FACT_BASE 行号）。两口径并存处双列不裁。
> **边界三类**集中在文末：`NOT_FOUND`（未找到）/ `待硬件确认`（board-confirm）/ `在档未裁=架构开口`。
> 调取员 / 2026-06-06。源文件均亲开核验，未凭记忆/训练知识填。

路径简写：
- `ALT` = `knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/src/Audio_Loopback_TDM.c`
- `ALT.h` = 同目录 `Audio_Loopback_TDM.h`
- `FB` = `sprint6/dsp/audio/M1_FACT_BASE.md`
- `IOTOPO` = `sprint4/audio_io_topology.md`（= DOC-S4-IO-01）

---

## 一、block-rate（第一优先）

### 条目 1 — FIRA 链帧大小：确切样本数/帧 + 两口径（64 输入帧 vs 树内 120）

**输入帧大小 = 64 样本/帧/通道（冻结源码常量）**
- `BENCH_FRAME = 64`、`BENCH_FS = 48000`、`BENCH_NFR = 1024`。 [来源: `sprint4/dsp/core_only/bench/bench_harness.h:30-32`]
- `TFB8_FRAME = 64`（注释「multiple of 8; same as tree_verify FRAME」）、`TFB8_NCH = 8`。 [来源: `sprint4/dsp/core_only/src/tfb_8ch.h:32-33`]
- M2 EQ 模块同口径 `EQ_FRAME=64 / EQ_FS_HZ=48000 / EQ_NCH=8`（须 `_Static_assert` 对齐 BENCH）。 [来源: `sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:38-42`；FB:296]
- `bench_main.c` 用 `BENCH_FRAME`/`BENCH_FS`（无独立 `FRAME`/`BENCH_FRAME` 重定义宏；引用 bench_harness.h 口径）。 [来源: `sprint4/dsp/core_only/bench/bench_main.c:230`（`BENCH_FRAME/BENCH_FS`）]

**两口径关系（双列不裁）：**

口径 A —「64 样本输入帧」：每帧从输入流取 `BENCH_FRAME=64` 个样本喂 `tfb_analyze`/`fira_tfb_analyze`。 [来源: `fira_regression.c:204-206`（`xin = &chirp[f*BENCH_FRAME]`，`...analyze(...,BENCH_FRAME,...)`）]

口径 B —「树内多级 120 样本/帧/ch」：4 子带 dyadic 树 analyze 输出的逐子带样本数之和。
- `sz[4] = { BENCH_FRAME/8, BENCH_FRAME/4, BENCH_FRAME/2, BENCH_FRAME }` = `{8, 16, 32, 64}`，**求和 = 120**。 [来源: `sprint4/dsp/fira/fira_regression.c:195`]
- 同形 4 子带缓冲声明 `b0[FRAME/8],b1[FRAME/4],b2[FRAME/2],b3[FRAME]`。 [来源: `fira_regression.c:148`、`:193-194`]

**两口径解释（双列，不裁）：**
- 「64」= 输入帧粒度（每帧进 64 input 样本）。
- 「120」= sz[] 多级和（sb0=8 + sb1=16 + sb2=32 + sb3=64 = 120 子带样本/帧/ch；sb3 未抽取故 = 满 64）。两者非同物：120 是一帧 64 输入样本经 dyadic 分解后落到 4 个子带的样本总数（sb3 undecimated）。 [来源: sz[] 定义 `fira_regression.c:195`；语义 `sprint5/H1_WCET_WORKORDER.md:33`「sb0/8+sb1/16+sb2/32+sb3/64 = 120 samp/帧/ch（sb3 未抽取，sb3[i]=in[i]-r1[i]）」]
- ⚠ 「120 samp/frame」**字面字符串在 `fira_regression.c` 中不存在**（grep 零命中）；它是 sz[] 四元素之和，最早被显式写成「120」并落档的位置是 H1 线，非 fira_regression。CTO 派单称「:193 附近有 120 samp/frame 记载」——实际 :193-195 是 4 子带缓冲声明 + sz[4] 定义（其和 = 120），非字面「120」。 [来源: grep `120` over `fira_regression.c` = 零命中；sz[] @ `fira_regression.c:195`；字面「120 samp/frame」首落档 = `sprint5/H1_WCET_WORKORDER.md:33`、`sprint5/H1_R15_FIX_PACKAGE.md:57`]
- sz[] 数学来源标注 = `fira_tree.c:49-52`（H1 线转引；本调取员亲开 `fira_tree.c:48-56` 为饱和算术 helper，未见显式 49-52 数字行——sz[] 实体定义在 `fira_regression.c:195` 与 `h1_wcet_measure.c:235`，`fira_tree.c:49-52` 系 H1 文档对「子带 sample 数源」的转引锚，原文行号与本调取所见不完全对齐，列入 NOT_FOUND-A）。 [来源转引: `sprint5/H1_WCET_WORKORDER.md:33`、`sprint5/H1_R15_FIX_PACKAGE.md:147`（标 `fira_tree.c:49-52`）]

### 条目 2 — fS = 48kHz 确认

- `BENCH_FS = 48000`。 [来源: `sprint4/dsp/core_only/bench/bench_harness.h:30`]
- `EQ_FS_HZ = 48000`。 [来源: `sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:38-42`]
- harness ISR 率推导 `FS/FRAME = 48000/64 = 750 Hz`。 [来源: `sprint5/dsp/harness/h2_dma_isr_measure.c:38`]
- 产品锁定采样率 = 48kHz。 [来源: `IOTOPO:51`（「48kHz 项目锁定」）、`:53`]
- codec datasheet 锚点 fS = 48kHz（电气表条件 = 12.288MHz @256×fS）。 [来源: `adau1979.pdf P3+P5`，转引 FB:201；ADC SAI_CTRL0=0x1B 注释「I2S 48kHz」`ALT:98`，转引 FB:68]

### 条目 3 — M1_FACT_BASE 「187.5 vs 750Hz」block-rate 调研原文逐字 + 行号

**原文逐字抄（FB §4.5）：**
> **block-rate 口径不一致点**（仅列差异）：survey 探针示例用 block-rate=FS/256=187.5Hz（对齐例程 256-sample 块）；DOC-S4-IO-01 产品帧 ISR 口径=FS/FRAME=48000/64=750Hz。两口径源不同（例程块 256 vs 产品 FRAME 64），最终随产品块大小定，**待架构**。
- [来源: `FB:305`；该行带源 `M1_SYMBOL_SURVEY.md:166`（187.5）；`sprint5/H2_WORKORDER.md:39`（750Hz）；`DOC-S4-IO-01:66 G-IO6`] [标签: inferred，两数均在档，口径选择待架构，本轮不裁]

**两候选各对应多少样本/块（核原文）：**
- 候选 187.5 Hz = `FS/256` → **块 = 256 样本**（对齐例程 `Pipelined` BLOCK_SIZE=256 / ALT 256-长 float 通道缓冲口径）。 [来源: `FB:305`「对齐例程 256-sample 块」；`IOTOPO:66 G-IO6`「例程 Pipelined BLOCK_SIZE=256」；`FB:360`（board-confirm 15）]
- 候选 750 Hz = `FS/FRAME = 48000/64` → **块 = 64 样本**（产品 FRAME=64 = SPORT block-done 率）。 [来源: `FB:305`；`h2_dma_isr_measure.c:38`「FS/FRAME=48000/64=750Hz the SPORT block-done rate, DOC-S4-IO-01」]

**背后约束原文（为何只列这两个）：**
- 两口径源不同（例程块 256 vs 产品 FRAME 64），「最终随产品块大小定，待架构」；产品流水线块大小本身是开口 G-IO6。 [来源: `FB:305`；`IOTOPO:66 G-IO6`「例程 Pipelined BLOCK_SIZE=256；我方 harness FRAME=64 → 产品流水线块大小待定（影响延迟/DMA）」]

### 条目 4 — H1/H2 帧 cycle 与样本数对应 + ×750/1e6 换算因子

**两 harness 帧均为 BENCH_FRAME=64 样本/帧、8 通道（逐行核同口径）：**
- H1 nofocus 帧 = `BENCH_FRAME=64`（`h1:235`）、`DOLPH_W8_NCH=8`（`h1:236`）。 [来源: `sprint5/audit/H2_READING_ANOMALY_ANALYSIS.md:24-25`]
- H2 base 帧 = `BENCH_FRAME=64`（`h2:104`）、8 ch（`h2:102`）。 [来源: `H2_READING_ANOMALY_ANALYSIS.md:24-25`；`h2_dma_isr_measure.c:117,143-144`（`for i<BENCH_FRAME` / `fout[BENCH_FRAME]`）]

**各 cyc/frame 对应样本数：**
- **525,850 cyc/frame = H1 nofocus（含逐帧 CRC32），一帧 = 64 样本 × 8 ch。** [来源: `sprint5/H1_FINAL_RULING_MATERIAL.md:20`（focus/nofocus/focus_only = 591,221 / **525,850** / 65,371 cyc/frame）；帧 = 64 见 `H2_READING_ANOMALY_ANALYSIS.md:24`]
- **454,730 cyc/frame = H2 base（无 CRC），一帧 = 64 样本 × 8 ch。** [来源: `sprint5/audit/H2_READING_ANOMALY_ANALYSIS.md:10`（`cyc_frame_base=454,730`）；`sprint2/docs/decisions_log.md:722`（base=454,730 [L1] EZKIT 实测）]

**CRC 差异 71,120：**
- 525,850（H1 nofocus）与 454,730（H2 base）之差 = **71,120 cyc**，= H1 链每帧多跑的逐 bit CRC32（H2 链无）。 [来源: `H2_READING_ANOMALY_ANALYSIS.md:18`（标题「base 454,730 vs yardstick ~525,850（low 13.5%, gap 71,120）」）]
- 机理：H1 `crc=h1_crc32(crc,fout,FRAME)` 每 ch（`h1:251`）；H2 `h2_fira_frame` 无 CRC（纯 timing target）。CRC 量化：8 ch × 64 words × 32 bit = 16,384 inner-iter/frame × ~4.34 cyc/iter = 71,120（exact）。 [来源: `H2_READING_ANOMALY_ANALYSIS.md:31-53`；`H2_WORKORDER.md:114`（R27 修正：原 yardstick「≈525,850」系跨链误比，应「H1 nofocus 减其 CRC32 ~71k」）]
- ⚠ yardstick relabel（R27）：`H2_WORKORDER.md:146` 仍有「base ≈ H1 nofocus ~525,850-class」旧措辞，已被 `:114` R27 修正为「减 CRC ~71k ≈ 454,730」。两处并存，**不裁**。 [来源: `H2_WORKORDER.md:114` vs `:146`]

**×750/1e6 换算因子含义出处：**
- `750 = FS/FRAME = 48000/64` Hz = 帧率（= SPORT block-done 率 / 产品帧 ISR 率）。 [来源: `h2_dma_isr_measure.c:38`；`h1_wcet_measure.c:31-32`（「subband RATES sum = 120 × 750 fps」）]
- `MCPS = cyc/frame × (FS/FRAME) / 1e6`（cyc/frame × 帧率 → cyc/s，再 /1e6 → MCPS）。 [来源: `bench_harness.h:24`（`mcps_8ch = cyc_8ch_frame*(FS/FRAME)/1e6`）；`tree_filterbank.h:67`（`MCPS = cycles × FS / FRAME / 1e6 / (MAC/cycle)`）；off-board 公式 `bench_main.c:250,257`（`MCPS = increment*750/1e6`）]

---

## 二、1-in/8-out fan-out

### 条目 5 — SelectChannel 0..7 / fan-out 映射事实 + 例程扇出逻辑

**SelectChannel 事实（例程口径）：**
- 例程 `SelectChannel(4A,0u,11u)` = TX 选 slot 0..11（DAC 最多 12 输出 slot）；`SelectChannel(4B,0u,3u)` = RX 选 0..3（ADC 4 输入 slot）。 [来源: `ALT:307,319`；FB:75,128,277]
- 产品口径 = 1 路源 fan-out 到 8 路 TX slot（M2 beamformer 输出），`SelectChannel 须改 0..7`——**属架构待定（survey G-M1-2）**。 [来源: `FB:283`、FB:378；`M1_SYMBOL_SURVEY.md:100-101,152`]

**例程输入扇出逻辑（以源码为准，4-in / 8-out，不是 12-out）：**
- 回调拷贝为手动循环 `for(i=0,j=0;i<COUNT;i+=4,j+=8)`：每 RX 4-sample 组复制进 8 TX slot，每个 ADC sample 写两相邻 DAC slot（`buf1[j]=buf1[j+4]=buf4[i]`、`[j+1]=[j+5]=buf4[i+1]`…）。即 **4-ch ADC fan-out 到 8-ch TDM DAC**（每 ADC ch 复制到 2 个相邻 DAC slot）。 [来源: `ALT:187-205`（CallbackCount==1，buf4→buf1）、`:210-228`（CallbackCount==2，buf5→buf2）；FB:88]
- 注：例程虽 SelectChannel(TX,0..11)，但实际回调只填 8 个 slot（4 ADC × 2 = 8），fan-out 口径 = **4-in/8-out**（CTO 派单问「4-in/12-out 还是什么」→ 答 = 4-in/8-out）。 [来源: `ALT:187-205`（j+=8，写 [j..j+7]）]

**M1 透传「最简映射」在档有无：**
- **在档无「M1 透传最简映射」定义**——产品 1-in/8-out 的 slot/CMAP 映射在档全部标为架构决策（G-M1-2/G-IO4），未给定值。 [来源: `M1_SYMBOL_SURVEY.md:84,152`（「1 src ch fanned to 8 TX slots … = architecture decision. G-M1-2」）；`FB:283`、FB:378] → **属架构开口（见文末「在档未裁=架构开口」节）。**

### 条目 6 — M2 FIRA 接口关系（EQ_INTEGRATION_NOTE M2 节 + FB §4 M2 预留节）

**EQ_INTEGRATION_NOTE M2 接口节逐条（M2 adapter checklist，标「NOT done here — M2 only」）：**
- ① 帧口径调和：模块声明 `EQ_FRAME=64 / EQ_FS_HZ=48000 / EQ_NCH=8`；M2 须编译期 `_Static_assert(EQ_FRAME==BENCH_FRAME, EQ_NCH==DOLPH_W8_NCH, EQ_FS_HZ==FS)`，非静默假设。 [来源: `EQ_INTEGRATION_NOTE.md:38-42`]
- ② 数据类型：模块 = float32；FIRA 核 = 定点 Q31（bit-exact）；M2 adapter 持 Q31↔float 边界转换（前 EQ：int32 Q31→float；后 limiter 每 ch：float→int32 Q31 给 DAC）。转换缩放为 M2 决策，未实现/未预判。 [来源: `EQ_INTEGRATION_NOTE.md:43-47`；FB:297]
- ③ 权重源：limiter `w[8]` 须与 beamformer 同一单源 `sprint4/dsp/fira/dolph_w8_q15.csv` 列 `w_float_track1_scipy`。 [来源: `EQ_INTEGRATION_NOTE.md:48-51`]
- ④ EQ 系数：当前 flat/unity 占位 + 2 测试 biquad；产品系数待 R3 消声室在轴响应（EQ_PRD:45）；接口 `eq_biquad_set` 已定。 [来源: `EQ_INTEGRATION_NOTE.md:52-55`；FB:300]
- ⑤ limiter 阈值 `t_base`：占位 [L4]（0.8 满量程），最终值待线③厂家函（Xmax/热额定）。 [来源: `EQ_INTEGRATION_NOTE.md:56-58`；FB:299]
- 链中位置：`master mono → eq_master_process(2-3 biquad, fan-out 前一次) → fan-out×8 + 每通道聚焦分数延迟(STEER-2, FIRA 核) → eq_limiter_process_ch×8(T_k=T×w[k]) → 8 路功放`。 [来源: `EQ_INTEGRATION_NOTE.md:14-35`（链图 :14-28）；FB:298]

**FB §4 M2 / FIRA 接口预留节逐条（均标未实现）：**
- FIRA 链帧口径 = FRAME 64 / 48000Hz / 8 ch。 [来源: `FB:295`]
- EQ 帧口径对齐断言。 [来源: `FB:296`]
- Q31↔float 边界（declared-only）。 [来源: `FB:297`]
- EQ 在链中位置（declared-only，集成意图链未接入冻结流水线）。 [来源: `FB:298`]
- limiter 阈值占位 [L4]。 [来源: `FB:299`]
- EQ 系数占位。 [来源: `FB:300`]

**「M1 fan-out 与 M2 波束 fan-out 同一机制吗」——在档有无答案：**
- **在档无此裁定。** FB:283 / survey:84,152 仅把产品「1 路源 fan-out 到 8 路 TX slot（M2 beamformer 输出）」标为「属架构待定 G-M1-2」，**未裁定** M1 透传 fan-out 与 M2 波束 fan-out 是否同一机制。 [来源: `FB:283`；`M1_SYMBOL_SURVEY.md:84,152`] → **属架构开口（见文末）。** 不自行裁。

---

## 三、8-of-12 DAC slot

### 条目 7 — ADAU1962A 12 通道 slot 映射约定

**FB §3 CMAP/slot 机制事实：**
- ADAU1962A 共 12 路 DAC；寄存器图（Table 24）**无独立 per-channel CMAP 路由寄存器**——slot→通道为按 TDM 模式固定顺序分配（非可编程映射），由 Table 23 规定。 [来源: `FB:242`（`ADAU1962A.pdf Table 24 (P24) + Table 23 (P22)`）] [datasheet]
- TDM8 模式（SAI=011）固定 slot 线序（Table 23）：DSDATA1 承载 Channel 1..8，DSDATA2 承载 Ch 9..12，DSDATA3-6 不用；TDM8 最大采样率 96kHz。 [来源: `FB:243`（`ADAU1962A.pdf Table 23 (P22)`）] [datasheet]
- 12 路各独立软静音 `DAC_MUTE1(0x09) DAC01..08` / `DAC_MUTE2(0x0A) DAC09..12`；独立音量 `DACxx_VOL(0x0C..0x17)` + 主音量 `DACMSTR_VOL(0x0B)`。 [来源: `FB:244`（`ADAU1962A.pdf Table 24 (P24) + Table 34/35 (P33-P34)`，表号经 S3 VERIFIER 修正）] [datasheet]
- DAC_CTRL0(0x06) SAI=Bits[5:3]：011=TDM8。 [来源: `FB:239`（`ADAU1962A.pdf Table 31 (P30) + Table 24 (P24)`）] [datasheet]

**例程 SelectChannel 0..11 源码行：**
- `adi_sport_SelectChannel(hSPORTDev4ATx, 0u, 11u)`（TX 选 DAC slot 0..11）。 [来源: `ALT:307`；FB:73,128]

**datasheet 转引（FACT_BASE 已覆盖，转引即可）：**
- ADAU1962A 12-Channel 24-Bit DAC。 [来源: `ADAU1962A.pdf p1`，转引 `IOTOPO:14`]

### 条目 8 — ⚠ 物理通道约束：8 通道阵列接 DAC 哪 8 路

**DOC-S4-IO-01 落点相关节：**
- 输出链：8ch → ADAU1962A（12ch DAC，**用 8ch**）→ 8 路 ACM3128A 功放 → **8 路 A/B 对称串联 = 16 喇叭**（拆机 KB-HW-001：转接板 16ch 实为 8 路驱动）。 [来源: `IOTOPO:26-32`]
- 1 路 SPORT4 TDM 驱 8 路足够（1×ADAU1962A，不触发多片 DAC/2×SPORT）。 [来源: `IOTOPO:46`；FB:285] [inferred]

**G-IO4 类开口（在档最接近的约束原文，逐字）：**
> G-IO4 | **我方 8ch → ADAU1962A 通道映射 + → 8 路 A/B 物理连线** | 哪个 DAC ch 驱哪路功放/哪对喇叭 = 产品布线设计，文档无
- [来源: `IOTOPO:64`（G-IO4）；同义 FB:348（board-confirm B.7「8ch→ADAU1962A 通道映射 + →8 路 A/B 物理连线 = 产品布线设计，文档无」，源 `M1_SYMBOL_SURVEY.md:153 G-M1-3`）]

**硬件线文档 grep（转接板/功放接线）：**
- 转接板 16ch 实为 8 路驱动（拆机 KB-HW-001）；功放 = ACM3128A（0.246 Vrms / 20kΩ 模拟输入，U3）。 [来源: `IOTOPO:15,32`（KB-HW-001 / handover L190）]
- ⚠ **「接 DAC 哪 8 路」= 硬件未定义，在档无映射值** → **待硬件确认（见文末「待硬件确认」节，G-IO4 / G-M1-3）。** 不替 CTO 假设。

---

## 四、M2 缓冲共置

### 条目 9 — 例程 SPORT buffer 放置（FB §1 buffer 节逐条）

- SPORT 数据缓冲为普通全局 int 数组：`int_SP0ABuffer1/2[COUNT*2]`(TX,=600)、`int_SP0ABuffer4/5[COUNT]`(RX,=300)；`COUNT=300`。 [来源: `FB:97`（`ALT:40-43`；`ALT.h:24`）] [L1-example-called]
- SPORT 缓冲**无 `#pragma section`/放置指令**，为普通全局（默认 app.ldf 链接放置）。 [来源: `FB:98`（`ALT:39-43` 缺失）] [L1-example-called]
- 回调/DMA 路径**无 cache flush/invalidate**（文件内无 `adi_cache_*`）；回调仅直接数组拷贝。 [来源: `FB:89`（`ALT:167-235,326-334`）] [board-confirm]
- TX 缓冲字节尺寸 = `COUNT*2*sizeof(int)=600*4=2400 B`；RX = `COUNT*4=1200 B`（sizeof(int)=4 SHARC 假设，算术推导）。 [来源: `FB:101`（`ALT:40-43,256,272`）] [inferred]
- 默认放置 = L1 Block 0 uncached（R32 INFO 补：.ldf 实证，L1 RAM 不被 core data-cache，故 example no-flush 正确-by-placement）。 [来源: `FB:358`（board-confirm 13）] [L1]

### 条目 10 — FIRA 工作集放哪个 block + 共置裁定边界

**H2_MAP_PLACEMENT_ADJUDICATION 逐数字（带行号）：**
- `s_h2_fa @ 0x261ee0  size 0x47a0  end 0x26667f`（FIRA 工作集，FiraChannelState[8]）。 [来源: `sprint5/audit/H2_MAP_PLACEMENT_ADJUDICATION.md:14`]
- `s_bh_src @ 0x25fe88 … end 0x260e87`；`s_bh_dst @ 0x260e88 … end 0x261e87`（MDMA proxy 缓冲）。 [来源: `H2_MAP_PLACEMENT_ADJUDICATION.md:12-13`]
- `mem_block0_bw { START(0x002403f0) END(0x0026ffff) }` = L1 Block 0。 [来源: `H2_MAP_PLACEMENT_ADJUDICATION.md:26,42`（app.ldf:142-144）]
- `mem_block1_bw { START(0x002c0000) END(0x002effff) }` = L1 Block 1。 [来源: `H2_MAP_PLACEMENT_ADJUDICATION.md:27,42`（app.ldf:146/151）]
- 裁定：s_bh_src/dst/s_h2_fa **三者全在 Block 0**（均 ≥0x2403f0 且 ≤0x26ffff，均未达 0x2c0000）→ proxy 与 FIRA 同物理块 = R24 gate FAIL → 须 `#pragma section("seg_l1_block1")` 把 proxy 移 L1 Block 1。 [来源: `H2_MAP_PLACEMENT_ADJUDICATION.md:43-101`（裁定表 :43-48；pragma :79-84）；FB:306]
- proxy pin 后落 `seg_l1_block1`（route 到 mem_block1_bw，Block 1 START 0x2c0000）；s_h2_fa 保持 unpragma'd → 留 Block 0。bring-up 须重读 .map 确认 s_bh_src/dst ≥0x2c0000 且 s_h2_fa <0x270000（F24-MAJOR-1 放置验证义务持续）。 [来源: `H2_MAP_PLACEMENT_ADJUDICATION.md:75-88`；FB:361（board-confirm 16）]

**「SPORT buffer 在 Block 0 与 FIRA 自冲突吗」——在档有无直接裁定：**
- **在档无对「产品 SPORT RX/TX 缓冲 vs FIRA」的直接裁定。** 同类教训（MDMA proxy 同 Block 0 与 FIRA 自冲突）已裁，但 proxy ≠ 产品 SPORT 缓冲。 [来源: `H2_MAP_PLACEMENT_ADJUDICATION.md`（proxy 案）]
- F26-MAJOR-1 解读边界逐字：proxy 钉 Block 1 = **same-arbitration-class proxy（同 DM crossbar peer L1 block），非 identical-segment 实证**——「产品 SPORT RX/TX 缓冲落 L1 还是 L2 本地无证据」，声明 inc_dma 为「产品-representative 争用」前须 bring-up 核 SPORT 缓冲 .map 落块。 [来源: `sprint5/H2_WORKORDER.md:139-143`（F26-MAJOR-1）]
- R26 note 同义：proxy 缓冲与 FIRA 工作集同处 L1 Block 0 → R24 gate FAIL → 须 pin seg_l1_block1。 [来源: `FB:306`（R24/R26 教训）]
- 对 M2：「若 M2 beamformer 工作集与 SPORT 缓冲同居 Block 0，bring-up 应将 SPORT 缓冲 pin 到 seg_l1_block1 并重读 .map」——但「M2/SPORT 共置与否未定」。 [来源: `FB:307`、FB:383（inferred，产品共置与否未定）] → **属架构开口（产品 SPORT/FIRA/M2 共置未定，在档未裁，同类教训如上）。**

### 条目 11 — FB buffer 放置/pin 调研建议原文 + 行号 + 标签

逐字：
> buffer 放置对 M1/M2：例程 SPORT ping-pong 缓冲默认落 L1 Block 0(uncached→无须 flush)；若 M2 beamformer 工作集与 SPORT 缓冲同居 Block 0，bring-up 应将 SPORT 缓冲 pin 到 seg_l1_block1 并重读 .map。
- [来源: `FB:307`] [标签: inferred（M2/SPORT 共置与否未定）；源 `M1_SYMBOL_SURVEY.md:107-118`；`H2_MAP_PLACEMENT_ADJUDICATION.md:68-89`]

> `#pragma section("seg_l1_block1")` 形式 + 段名 = ADI FIRA/IIRA accelerator 例程实证([L1])，路由到 mem_block1_bw(app.ldf:460)。
- [来源: `FB:308`] [标签: inferred（H2 裁定转引 ADI 例程 IIR_Throughput_21569_V2.c:23-30，本轮未亲开 IIRA 例程原文）]

---

## 五、补充

### 条目 12 — M1_FACT_BASE §6 板上确认清单 17 条全文逐字抄

> 源：`FB:335-362`（§6「[board-confirm] 汇总（CTO 板上须确认清单）」）。每条带原编号 + 来源标注，逐字。

**A. install-tree 头（CCES 版本与头名）**
1. CCES 版本核：.d 全部显示 **2.11.1**，brief 称 **2.12.1** —— version delta 未核，须 grep 安装版 2.12.1 SHARC/include 确认头名是否漂移。 [来源: ALT.d 各 install 路径；M1_SYMBOL_SURVEY.md:143] [FB:340]
2. 头文件后缀非对称（R25 adi_mdma 9-error 类陷阱）：逐驱动核 2.12.1 确切头名 —— SPORT(adi_sport.h+adi_sport_2156x.h 并存)/SPU(adi_spu.h+adi_spu_v3.h，注 _v3 非 _2156x)/TWI(adi_twi.h+adi_twi_2156x.h 并存，源 #include 逐例程不同)/PDMA(仅 adi_pdma_2156x.h)，不得假设 2.11.1 名通用。 [来源: M1_SYMBOL_SURVEY.md:144；S2 §2.1] [FB:341]
3. ADI_SPORT_MEMORY_SIZE / ADI_TWI_MEMORY_SIZE / ADI_SPU_MEMORY_SIZE **数值** —— 安装版头解析。 [来源: M1_SYMBOL_SURVEY.md:145] [FB:342]
4. adi_sport_ConfigMC / ConfigFrameSync 对「8-slot」**形参语义**（ALT 用 7u 表 8 slots，验 count-vs-index 约定）。 [来源: M1_SYMBOL_SURVEY.md:146] [FB:343]
5. 全部 adi_* 函数**精确参数 TYPE/return-enum** + 各枚举 token **数值** + ADI_PDMA_DESC_LIST struct 字段类型 —— install-tree 头确认。 [来源: S2 NOT_FOUND] [FB:344]

**B. codec 寄存器/映射（datasheet 已给约束，本板取值待定）**
6. codec SAI 字段 = TDM8(SAI=011) 用于 8ch + DAC slot/CMAP 8-of-12 映射 —— datasheet adau1979 Reg 0x05-0x08 + ADAU1962A DAC_CTRL/slot 在 bring-up 核（G-M1-1/G-M1-3）。 [来源: M1_SYMBOL_SURVEY.md:147,151-153] [FB:347]
7. 8ch→ADAU1962A 通道映射 + →8 路 A/B 物理连线（哪 DAC ch 驱哪路功放/哪对喇叭）= 产品布线设计，文档无。 [来源: DOC-S4-IO-01:64 G-IO4；M1_SYMBOL_SURVEY.md:153 G-M1-3] [FB:348]

**C. 板级时钟/连线/时序（原理图/示波器）**
8. 两片实际主/从角色 + 12.288 MHz 物理来源（SPORT vs codec vs 板载晶振）—— datasheet 无本板记载，须原理图/板上确认。 [来源: S3 F-两片时钟拓扑；DOC-S4-IO-01:63 G-IO3] [FB:351]
9. SPORT4↔codec carrier/SOM 外部网名级走线 + AD2428W-SOM 旁路实体走线 —— schematics PDF 未渲染核名（例程 SRU 仅证片上 DAI 路由）。 [来源: schematics/V2.1/*.pdf；DOC-S4-IO-01 G-IO3] [FB:352]
10. 外部 MCLK 晶振源具体频率/器件 + 例程实际采样率寄存器解码（真跑 48k 验证）。 [来源: DOC-S4-IO-01:61 G-IO1] [FB:353]
11. TDM slot 精确时序（BCLK/FSYNC 极性、slot 起始、24-in-32 对齐）—— 示波器/逻辑分析仪或 EZKIT 对齐。 [来源: DOC-S4-IO-01:65 G-IO5] [FB:354]
12. SoftConfig 直进直出软开关(U48 Port A/B) 在非 A2B 拓扑下具体配置值 —— 工程师确认（例程用 ConfigSoftSwitches_ADC_DAC extern，且 main 中 Switch_Configurator 调用被注释，运行时未执行）。 [来源: DOC-S4-IO-01:67 G-IO7；M1_SYMBOL_SURVEY.md:136；S1 §1.10] [FB:355]

**D. cache / 放置（板 .map 重读）**
13. DMA 回调/提交路径无 cache flush/invalidate —— 本地已知前提（R32 INFO 补）：loopback 当前放置 = L1 Block 0 uncached（.ldf 实证，L1 RAM 不被 core data-cache，cache 仅服务 external/L2 访问）→ 例程 no-flush 正确-by-placement [L1]。board-confirm 仅针对：M1/M2 最终放置若移出 uncached L1（L2/external），则 flush/invalidate 必须补。 [来源: S1 F-frame-callback-logic + loopback app.ldf cache 注释] [FB:358]
14. DMA 缓冲 cache 操作 flush_data_buffer in <sys/cache.h> —— 仅当缓冲移出 L1 到 cached L2/external 时需要。 [来源: M1_SYMBOL_SURVEY.md:148] [FB:359]
15. 产品流水线块大小待定（例程 COUNT=300 / ALT 256-长 float 通道缓冲；我方 FRAME=64）—— 影响延迟/DMA/io-callback block-rate。 [来源: DOC-S4-IO-01:66 G-IO6；ALT.h:24；ALT.c:26-38] [FB:360]
16. 重建带 #pragma 的 .map 须板上重读确认 s_bh_src/dst 落 ≥0x2c0000(Block 1) 且 s_h2_fa 仍 <0x270000(Block 0)（F24-MAJOR-1 放置验证义务持续）。 [来源: H2_MAP_PLACEMENT_ADJUDICATION.md:87-89, :134-136] [FB:361]
17. sizeof(int) 板上确认（SHARC ABI）—— 缓冲字节尺寸 2400/1200 B 依 sizeof(int)=4 假设（§1.9 [inferred]），DMA 尺寸作架构输入前板上 sizeof 一行确认。 [来源: R32 F32-MINOR-1] [FB:362]

### 条目 13 — 启动序骨架完整步骤（每步带 ALT.c 行号）

> 源：FB §1（S1 例程解剖）。main() 顶层调用序 [来源: `ALT:688-804`，FB:32]。

1. **adi_initComponents()**（自动生成）→ 顺序 `adi_sec_Init() → adi_initpinmux() → adi_SRU_Init()`，每步前一步 result==0 为门。 [来源: `EZKIT/system/adi_initialize.c:19-33`，FB:34]
2. **SPU_init()** [SPORT DMA 前置总线安全]：`adi_spu_Init(0, SpuMemory, NULL, NULL, &ghSpu) → adi_spu_EnableMasterSecure(ghSpu, SPORT_4A_SPU, true) → ...(SPORT_4B_SPU, true)`；`SPORT_4A_SPU=57 / 4B_SPU=58`。 [来源: `ALT:453-476`；`ALT.h:39-40`，FB:38-39]
3. **[Switch_Configurator() 被注释掉]** —— SoftConfig SoftSwitch 序列运行时不执行（codec 上电/复位依赖板默认态）。 [来源: `ALT:701` 注释；定义 `ALT:378-401`，FB:33]
4. **SRU_Init()**（片上路由）：先写 pads enable `*pREG_PADS0_DAI0_IE=0x1ffffe / DAI1_IE=0x1ffffe`（`ALT:417-418`）；时钟/FS/数据路由 + PBEN 引脚使能。 [来源: `ALT:417-439`，FB:44-48]
5. **Init_TWI()**（codec 控制总线）：`adi_twi_Open(TWIDEVNUM, ADI_TWI_MASTER, &TwideviceMemory[0], ADI_TWI_MEMORY_SIZE, &hTwiDevice) → SetPrescale(12u) → SetBitRate(100u) → SetDutyCycle(50u) → SetHardwareAddress(0x38u)`。 [来源: `ALT:508-546`，FB:51-52]
6. **ADAU_1962_init()(DAC)** = **ADAU_1962_Pllinit()** [设 hw addr 0x04 → 写 `PLL_CTL_CTRL0=0x01,(delay),=0x05,(delay)` → `PLL_CTL_CTRL1=0x22,(delay)` → **轮询 PLL_CTL_CTRL1 bit2 ((status&0x4)>>2) = PLL lock**] + 循环 i=0..27 写 Config_array_DAC[i]（写后回读比对）。 [来源: `ALT:560-617`（Pllinit :578-617，轮询 :610-613），FB:58-59]
7. **ADAU_1979_init()(ADC)** = **ADAU_1979_Pllinit()** [设 hw addr 0x11 → 写 `REG_POWER=0x01`、`REG_PLL=0x03` → 读 REG_PLL → **轮询 REG_PLL bit7 ((status&0x80)>>7) = PLL lock**] + 循环 i=0..15 写 Config_array_ADC[i]。 [来源: `ALT:622-669`（Pllinit :641-669，轮询 bit7），FB:65-66]
8. **Sport_Init()** 使能序：`RegisterCallback(RX, SPORTCallback, NULL)(ALT:323) → PrepareDescriptors → DMATransfer(RX)(ALT:330) → DMATransfer(TX)(ALT:333) → Enable(RX,true)(ALT:337) → Enable(TX,true)(ALT:340)`。**RX 先于 TX 使能。** [来源: `ALT:323-341`，FB:85]
   - SPORT4A(TX) open：`adi_sport_Open(SPORT_DEVICE_4A, ADI_HALF_SPORT_A, ADI_SPORT_DIR_TX, ADI_SPORT_MC_MODE, ...)`（`ALT:292`）；配置 ConfigData/Clock/FrameSync/MC/SelectChannel(0..11)（`ALT:299-308`）。 [来源: FB:71,73]
   - SPORT4B(RX) open：`...4B, ADI_HALF_SPORT_B, ADI_SPORT_DIR_RX, MC_MODE`（`ALT:295`）；SelectChannel(0..3)（`ALT:311-319`）。 [来源: FB:72,74]
   - DMA 描述符：每方向 2 节点环形 ping-pong（`ALT:259,267,275,283`）；回调仅注册在 RX（`ALT:323`），TX 无回调。 [来源: FB:81,84]
9. **Stop_TWI()**（进音频环前关 TWI，流式期不用 TWI）。 [来源: `ALT:548-556,730-734`，FB:55]
10. 随后 GPIO LED 设置 → 进无限音频环。 [来源: `ALT:688-804`，FB:32]

### 条目 14 — 时钟拓扑数字

**256×fS = 12.288 MHz 来源：**
- ADC datasheet：48kHz fS / 256×fS / 主时钟 12.288 MHz（MCS Bits[2:0] 复位 001=256×fS）；48kHz MCLKIN vs MCS 表：256×=12.288 MHz。 [来源: `adau1979.pdf Table 18 (P28)` + `Table 9 (P13)`，转引 FB:197,201-202] [datasheet]
- DAC datasheet：PLL_CLK_CTRL0(0x00) MCS Bits[2:1]（00=256× @44.1/48k）；256×fS@48k=12.288MHz。 [来源: `ADAU1962A.pdf Table 25 (P25)`，转引 FB:233；FB:290] [datasheet]
- 例程行号：DAC PLL 写序 `ALT:590,596,604`，256×fS 为 datasheet 口径（转引）。 [来源: FB:290（`ALT:590,596,604,610-613`）] [转引]
- 产品锁定推导：8 slot×32-bit@48kHz → BCLK=8×32×48k=12.288MHz（=256×fS，数学自洽，DOC 自标非寄存器实证）。 [来源: `IOTOPO:43`；`FB:278`] [inferred]

**DAC=主 / ADC+SPORT=从（SRU 扇出事实）：**
- 例程时钟主控 = DAC(ADAU1962A)：BCLK/FS 由 DAI1_PB05/PB04 输出，扇出到 SPORT4(4A+4B) 与转发 ADC → DAC 出时钟，SPORT 与 ADC 均从。 [来源: `ALT:422-426`，FB:288] [L1-example-called]
- DAC 时钟/FS 转发 ADC：`SRU2(DAI1_PB05_O, DAI1_PB12_I)`「DAC clock to ADC」+ `SRU2(DAI1_PB04_O, DAI1_PB20_I)`「DAC FS to ADC」，PB12/PB20 输出使能 HIGH。 [来源: `ALT:432-436`，FB:289] [L1-example-called]
- ⚠ datasheet 侧约束：同一 TDM 总线只能一个主器件出 BCLK/LRCLK，其余（含 SHARC SPORT）须配从；「哪片当主属板级接线决策，datasheet 只给约束」。 [来源: FB:254（`adau1979.pdf Table 21 (P31)` + `ADAU1962A.pdf Table 32 (P31)`）] [datasheet]

**PLL 锁判据出处：**
- **ADC PLL 锁 = Reg 0x01(PLL_CONTROL) bit7**（PLL_LOCK，只读，1=已锁）。 [来源: `adau1979.pdf Table 18 (P28) + P13`，FB:195] [datasheet]；例程轮询 `REG_PLL bit7 ((status&0x80)>>7)`。 [来源: `ALT:655-663`，FB:66,291] [L1]
- **DAC PLL 锁 = Reg 0x01(PLL_CLK_CTRL1) bit2**（PLL_LOCK，只读，0=未锁/1=已锁）。 [来源: `ADAU1962A.pdf Table 26 (P26) + P15`，FB:234] [datasheet]；例程轮询 `PLL_CTL_CTRL1 bit2 ((status&0x4)>>2)`。 [来源: `ALT:610-613`，FB:59,290] [L1]
- 注：例程宏命名 `PLL_CTL_CTRL1=0x01`（DAC）= datasheet 的 PLL_CLK_CTRL1(0x01)；ADC `REG_PLL=0x01` = datasheet PLL_CONTROL(0x01)。 [来源: `ALT ADAU_1962Common.h`，FB:60；`ADAU_1979Common.h`，FB:67]

---

## ★ 边界汇总 1：NOT_FOUND（未找到 — 本地不可闭，未编）

> 源：FB §5（FB:312-331）合并 + 本调取新增。

- **【条目 1 新增】字面「120 samp/frame」字符串在 `fira_regression.c` 中不存在**（grep 零命中）；120 = sz[]={8,16,32,64} 之和，字面「120」首落档在 H1 线（`H1_WCET_WORKORDER.md:33` / `H1_R15_FIX_PACKAGE.md:57`），非 fira_regression。
- **【条目 1 新增】`fira_tree.c:49-52`（H1 文档标的 sz[] 数学来源行号）** 与本调取所见不符：本调取亲开 `fira_tree.c:48-56` = 饱和算术 helper（`f_sat_add_i32` 等），未见显式子带 sample 数行；sz[4] 实体仅在 `fira_regression.c:195` 与 `h1_wcet_measure.c:235`。H1 文档转引锚行号存疑，未编。
- adi_sport_ConfigMC/ConfigData/ConfigFrameSync/ConfigClock/SelectChannel **精确原型与各形参语义** —— adi_sport.h 在 install tree，本地无。 [FB:316]
- ADI_SPORT_MEMORY_SIZE / ADI_TWI_MEMORY_SIZE / ADI_SPU_MEMORY_SIZE **数值** —— install-tree 头，本地无。 [FB:317]
- 各枚举 token **数值定义**（ADI_HALF_SPORT_A/B 等）—— 仅作 token，数值在 install-tree/cdef21569.h。 [FB:318]
- 真 BSP 头 BODY（adi_sport*.h / adi_twi*.h / adi_spu*.h / adi_pdma_2156x.h）—— 本地仅 guard_stub_inc/* 桌面 stub。 [FB:319]
- ADI_PDMA_DESC_LIST 各字段**声明类型** —— 由赋值 RHS 推断，struct 定义本地无非-stub 处。 [FB:320]
- adi_spu_v3.h 内容 / adi_spu.h 是否仅 forward —— 本地无。 [FB:321]
- 任何无后缀 adi_pdma.h —— 确认 ABSENT（零 .d 命中）。 [FB:322]
- adi_gpio init/Open —— 例程调 SetDirection 但无可见 adi_gpio_Init。 [FB:323]
- ADAU1962/1979 datasheet 页/表号背书具体寄存器值（为何 PLL_CTL_CTRL1=0x22、SAI_CTRL0=0x1B 选 48kHz I2S）—— S1 子任务未交叉引（S3 已独立覆盖大部分）。 [FB:324]
- ADAU1962A 无独立 per-channel CMAP/slot 重映射寄存器（机制已说清，非缺失）。 [FB:325]
- ADAU1979 PLL 锁后到可解静音「建议额外等待时间」无具体数值（仅「Lock Time 最大 10ms」+「读 PLL_LOCK 后再解静音」定性）。 [FB:326]
- 两片在本 EZKIT 实际主/从角色 与 12.288MHz 实际物理来源 —— datasheet 无本板记载（亦入 board-confirm）。 [FB:327]
- 板级原理图 PDF 内 SPORT4↔codec 外部网名级连线 / AD2428W-SOM 物理旁路走线 —— PDF 未渲染核名。 [FB:328]
- 外部 MCLK 晶振源具体器件/频率 —— 例程仅写 codec PLL 内部生成 256×fS，片外参考晶振未现身。 [FB:329]
- 例程实际采样率寄存器解码值（确认真跑 48k）—— G-IO1，本地无寄存器 dump。 [FB:330]
- adau1979.pdf/ADAU1962A.pdf 内 TDM/PLL 原文行号本轮未重抽（沿用 survey 转引行号 + 表/节锚）。 [FB:331]

---

## ★ 边界汇总 2：待硬件确认（board-confirm — 板上/原理图/示波器才能闭）

> 源：FB §6 全 17 条（已于条目 12 逐字抄）。物理通道相关重点：

- **【条目 8 重点】8ch → ADAU1962A 通道映射 + → 8 路 A/B 物理连线（哪 DAC ch 驱哪路功放/哪对喇叭）= 产品布线设计，文档无 → 待硬件确认。** [来源: `IOTOPO:64 G-IO4`；FB:348（board-confirm 7）；`M1_SYMBOL_SURVEY.md:153 G-M1-3`]
- 两片实际主/从角色 + 12.288MHz 物理来源（SPORT vs codec vs 板载晶振）。 [FB:351（8）]
- SPORT4↔codec carrier/SOM 外部网名级走线 + AD2428W-SOM 旁路实体走线。 [FB:352（9）]
- 外部 MCLK 晶振源频率/器件 + 例程实跑 48k 寄存器解码。 [FB:353（10）]
- TDM slot 精确时序（BCLK/FSYNC 极性、slot 起始、24-in-32 对齐）。 [FB:354（11）]
- SoftConfig 直进直出软开关(U48) 具体配置值。 [FB:355（12）]
- CCES 版本 2.11.1 vs 2.12.1 头名漂移 + 头后缀非对称核 + MEMORY_SIZE 数值 + ConfigMC 形参语义 + adi_* 精确 TYPE/enum。 [FB:340-344（1-5）]
- codec SAI=TDM8(011) 确认。 [FB:347（6）]
- M1/M2 最终放置若移出 uncached L1 则须补 flush/invalidate；flush_data_buffer in <sys/cache.h>。 [FB:358-359（13-14）]
- 产品流水线块大小待定（影响 block-rate 187.5 vs 750）。 [FB:360（15）]
- 重建 .map 须重读确认 s_bh_src/dst ≥0x2c0000 且 s_h2_fa <0x270000。 [FB:361（16）]
- sizeof(int) 板上确认（缓冲字节尺寸 2400/1200B 依此）。 [FB:362（17）]

---

## ★ 边界汇总 3：在档未裁 = 架构开口（CTO 须裁，本调取不裁）

- **【条目 5】M1 透传「最简映射」在档无定义** —— 产品 1-in/8-out slot/CMAP 映射全标架构决策（G-M1-2），未给定值。 [来源: `M1_SYMBOL_SURVEY.md:84,152`；FB:283,378]
- **【条目 6】「M1 fan-out 与 M2 波束 fan-out 同一机制吗」在档无此裁定** —— FB:283 / survey:84,152 仅标「属架构待定 G-M1-2」，未裁是否同机制。 [来源: `FB:283`；`M1_SYMBOL_SURVEY.md:84,152`]
- **【条目 8】8 通道阵列接 DAC 哪 8 路 = 架构/接线决策**（亦入待硬件确认 G-IO4）；datasheet 仅给机制（TDM8 取 DSDATA1 前 8 slot=Ch1..8），「上板选哪 8/12 路属架构/接线决策，本调研不裁」。 [来源: `FB:247,374`；`IOTOPO:64 G-IO4`]
- **【条目 10】产品 SPORT RX/TX 缓冲 vs FIRA 工作集 vs M2 共置 = 在档未裁** —— 同类教训（MDMA proxy 与 FIRA 同 Block 0 自冲突已裁 → pin seg_l1_block1），但 proxy ≠ 产品 SPORT 缓冲（F26-MAJOR-1：「产品 SPORT RX/TX 缓冲落 L1 还是 L2 本地无证据」）；M2/SPORT 共置与否未定。 [来源: `H2_WORKORDER.md:139-143`；`FB:307,383`]
- **【条目 3 / block-rate】187.5Hz(FS/256, 块256) vs 750Hz(FS/64, 块64) 口径选择 = 待架构**（随产品块大小 G-IO6 定，两数均在档，本轮不裁）。 [来源: `FB:305,382`；`IOTOPO:66 G-IO6`]
- **【条目 1 / FIRA 帧】64 输入帧 vs 120 树内子带和** —— 两口径均为源码实证常量（非冲突，非待裁），双列已解释关系（120 = sz[]={8,16,32,64} 之和，sb3 未抽取）；列此仅为防口径混用，非架构开口。 [来源: `fira_regression.c:195`；`H1_WCET_WORKORDER.md:33`]

---

数据齐, HALT——不进架构/实现（按派单）。
