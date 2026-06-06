# FACTS S4_topology

> Bring-up 前期事实采集（调研型，不下裁决）。源文件已独立打开核实。
> 主参考: DOC-S4-IO-01 = sprint4/audio_io_topology.md。
> M1_SYMBOL_SURVEY.md 处转引均独立核到原始例程/datasheet 行号后才标 [L1-example-called]；
> 仅由 survey 转述、未亲核原始口径的，标 [inferred] 并注「survey 转引」。
> 例程绝对路径根 = knowledge_base/ezkit/vendor_docs/cces_examples/code/Audio_Loopback_TDM/
> （下文简称 ALT；ALT.c = src/Audio_Loopback_TDM.c，ALT.h = src/Audio_Loopback_TDM.h）。

## F-1 SPORT4 实例号 / 半端口分工 / 板上物理连线证据

- FACT: 音频 SPORT 实例 = SPORT4（device 4），软宏 SPORT_DEVICE_4A=4u / SPORT_DEVICE_4B=4u 同一物理 SPORT 的 A/B 两半。
  SRC: ALT.h:26-27（#define SPORT_DEVICE_4A 4u / SPORT_DEVICE_4B 4u）
  GRADE: [L1-example-called]
- FACT: 4A 半端口 = Tx（发往 DAC）；adi_sport_Open(SPORT_DEVICE_4A, ADI_HALF_SPORT_A, ADI_SPORT_DIR_TX, ADI_SPORT_MC_MODE, ...)。
  SRC: ALT.c:292
  GRADE: [L1-example-called]
- FACT: 4B 半端口 = Rx（自 ADC 收）；adi_sport_Open(SPORT_DEVICE_4B, ADI_HALF_SPORT_B, ADI_SPORT_DIR_RX, ADI_SPORT_MC_MODE, ...)。
  SRC: ALT.c:295
  GRADE: [L1-example-called]
- FACT: 两半端口均跑 ADI_SPORT_MC_MODE（多通道 = TDM 模式）。
  SRC: ALT.c:292,295
  GRADE: [L1-example-called]
- FACT: SPU 外设号: SPORT_4A_SPU=57 / SPORT_4B_SPU=58（外设安全单元映射，bring-up SPU 配置用）。
  SRC: ALT.h:39-40
  GRADE: [L1-example-called]
- FACT: 板上 SRU 片上路由（DAI1_PB 引脚 ↔ SPT4），例程 SRU_Init() 逐行: DAC 时钟 DAI1_PB05_O→SPT4_ACLK_I 与 →SPT4_BCLK_I；DAC FS DAI1_PB04_O→SPT4_AFS_I 与 →SPT4_BFS_I。
  SRC: ALT.c:422-426（SRU2(...) 赋值，注释「DAC clock to SPORT 4A/4B」「DAC FS to SPORT 4A/4B」）
  GRADE: [L1-example-called]
- FACT: SPORT4A 数据出 → DAC: SRU2(SPT4_AD0_O, DAI1_PB02_I)（注释「SPORT 4A to DAC」），PB02 输出使能 SRU2(HIGH, DAI1_PBEN02_I)。
  SRC: ALT.c:429-430
  GRADE: [L1-example-called]
- FACT: ADC 数据入 → SPORT4B: SRU2(DAI1_PB06_O, SPT4_BD0_I)，PB06 设输入 SRU2(LOW, DAI1_PBEN06_I)。
  SRC: ALT.c:438-439
  GRADE: [L1-example-called]
- FACT: DAI1 引脚组上电使能 *pREG_PADS0_DAI1_IE=0x1ffffe（DAI0 同设 :417）。
  SRC: ALT.c:418
  GRADE: [L1-example-called]
- FACT: SPORT4 ↔ codec 在 carrier/SOM 上的最终物理网名级走线（哪个连接器脚、AD2428W-SOM 旁路实体走线）= 板级原理图 PDF（schematics/V2.1/*.pdf）未在本轮渲染核名；例程 SRU 行证明的是片上 DAI 路由，非外部网名。
  SRC: knowledge_base/ezkit/vendor_docs/schematics/V2.1/AD-EXKIT-双A2B底板（2026最新改版）.pdf + ADSP21569核心板原理图.pdf（PDF，未渲染）；DOC-S4-IO-01 G-IO3
  GRADE: [board-confirm]

## F-2 8 通道 TDM slot 映射: 例程口径 vs 产品口径

- FACT: 产品锁定口径 = 8 slot × 32-bit @ 48kHz → BCLK = 8×32×48k = 12.288 MHz（= 256×fS）。
  SRC: DOC-S4-IO-01 = sprint4/audio_io_topology.md:43,53
  GRADE: [inferred]（数学自洽推导，DOC-S4-IO-01 自标「非寄存器实证」；非 datasheet 直读、非例程实跑值）
- FACT: 该 256×fS / 12.288MHz @48k 与 codec 原生 TDM8 模式一致——datasheet 实证: adau1979 Table 10「TDM8, 32 bit/slot = 256 × fS」；ADAU1962A「256 × fS @48k = 12.288 MHz」。
  SRC: adau1979.pdf Table 10（survey 转引 l.2449-2474）；ADAU1962A.pdf（survey 转引 l.294, l.2474-2481）
  GRADE: [datasheet]（表/节锚来自 survey 转引；行号随 pdftotext 版本漂移，未本轮重抽 PDF 原文）
- FACT: 例程 SPORT slot 窗口 = 8 slots: adi_sport_ConfigMC(h, 1u, 7u, 0u, true)，window-size 形参 7u ⇒ 8 slots（4A/4B 同配）。
  SRC: ALT.c:305（4A）, ALT.c:317（4B）
  GRADE: [L1-example-called]
- FACT: 例程 slot 位宽 = 32-bit: adi_sport_ConfigData(h, ..., 31, ...)（word=31 ⇒ 32-bit）+ adi_sport_ConfigClock(h, 32, ...)（32 BCLK/slot）。
  SRC: ALT.c（survey §3 转引 :298-301；本轮核到 ConfigMC :305/:317 同段）
  GRADE: [inferred]（ConfigData/ConfigClock 具体行 survey 转引，未逐行亲核原文行号；ConfigMC 已亲核）
- FACT: 例程激活 slot 范围 = adi_sport_SelectChannel(4A, 0u, 11u)（Tx 用 0..11 = 12 ch DAC）/ SelectChannel(4B, 0u, 3u)（Rx 用 0..3 = 4 ch ADC）。
  SRC: ALT.c:307（4A Tx 0..11）, ALT.c:319（4B Rx 0..3）
  GRADE: [L1-example-called]
- FACT: 差异点①(slot 计数/宽/fS/BCLK)：产品 8 slot/32bit/48k/12.288MHz 与例程一致（survey 判 SAME）。
  SRC: M1_SYMBOL_SURVEY.md:77-82（对比表 slots/slot width/fS/BCLK 行）
  GRADE: [inferred]（survey 转引判定；底层例程 slot 数已本轮亲核 :305/:317）
- FACT: 差异点②(通道映射)：例程 = 4 ADC ch（CMAP12=0x01/CMAP34=0x23）映入；产品 = 1 路源 fan-out 到 8 路 TX slot（M2 beamformer 输出），SelectChannel 须改 0..7。属架构待定，survey 标 G-M1-2。
  SRC: M1_SYMBOL_SURVEY.md:84,101,152；例程 SelectChannel 0..11/0..3 见 ALT.c:307,319
  GRADE: [inferred]（差异由 survey 转引；产品 1-in/8-out 映射本身是架构决策，未实现）
- FACT: 差异点③(codec SAI 字段命名)：例程 ADC SAI_CTRL0=0x1B 注释为「I2S 48kHz」，但 SPORT 跑 MC(TDM) 成帧——loopback 能工作，产品 8-amp 映射需确认 codec SAI 字段 = TDM8(SAI=011)。survey 标 G-M1-1。
  SRC: M1_SYMBOL_SURVEY.md:83；ADC SAI_CTRL0=0x1B 见 survey §1 转引 ALT.c:98
  GRADE: [inferred]（survey 转引；SAI=011 确认须 datasheet adau1979 Register 0x05-0x08，待 bring-up）
- FACT: DAC 单片 ADAU1962A 12ch，产品仅用 8ch → 1 路 SPORT4 TDM 足够驱 8 路（不触发多片 DAC / 2×SPORT）。
  SRC: DOC-S4-IO-01 = sprint4/audio_io_topology.md:46
  GRADE: [inferred]（DOC-S4-IO-01 工程推理，非寄存器实证）

## F-3 主从时钟: MCLK/BCLK/FS 出处 + PLL 路径 + 产品拓扑约束

- FACT: 例程时钟主控 = DAC(ADAU1962A)：BCLK 与 FS 由 DAI1_PB05(时钟)/DAI1_PB04(FS) 输出，扇出到 SPORT4(4A+4B) 与转发给 ADC。即 DAC 出时钟，SPORT 与 ADC 均为从。
  SRC: ALT.c:422-426（注释明写「DAC clock to SPORT」「DAC FS to SPORT」）
  GRADE: [L1-example-called]
- FACT: DAC 时钟/FS 再转发给 ADC: SRU2(DAI1_PB05_O, DAI1_PB12_I)「DAC clock to ADC」+ SRU2(DAI1_PB04_O, DAI1_PB20_I)「DAC FS to ADC」，PB12/PB20 设输出使能(HIGH)。
  SRC: ALT.c:432-436
  GRADE: [L1-example-called]
- FACT: DAC(ADAU1962A) PLL bring-up 序: PLL_CTL_CTRL0=0x01→0x05, PLL_CTL_CTRL1=0x22, 轮询 PLL_CTL_CTRL1 bit2 锁定；datasheet 口径 256×fS @48k = 12.288MHz 主时钟。
  SRC: ALT.c:590,596,604,610-613（PLL 写/轮询）；256×fS 出处 ADAU1962A.pdf（survey 转引 l.2464-2481）
  GRADE: [L1-example-called]（PLL 写序例程实跑；256×fS 数值为 [datasheet]，survey 转引行号）
- FACT: ADC(ADAU1979) PLL bring-up: REG_PLL(0x01)=0x03, 轮询 REG_PLL bit7 锁定；datasheet: PLL 接受帧时钟为参考。
  SRC: ALT.c:655-663；datasheet adau1979.pdf（survey 转引 l.1821）
  GRADE: [L1-example-called]（PLL 写序例程实跑；「帧时钟为参考」为 [datasheet] survey 转引）
- FACT: 产品拓扑约束(时钟)：产品保留例程「DAC 出时钟、ADC+SPORT 从同步」单时钟域口径属架构沿用；外部 MCLK 晶振源/具体频率、AD2428W-SOM 旁路下的时钟物理走线 = 板级未核名。
  SRC: DOC-S4-IO-01 = sprint4/audio_io_topology.md:63（G-IO3 A2B 旁路）, :61（G-IO1 例程实际采样率寄存器值未解码）
  GRADE: [board-confirm]

## F-4 M2 FIRA 接口预留（事实层）

- FACT: FIRA 链帧口径 = FRAME 64 / 48000 Hz / 8 通道（BENCH_FS=48000, BENCH_FRAME=64; TFB8_FRAME=64, TFB8_NCH=8）。
  SRC: sprint4/dsp/core_only/bench/bench_harness.h:30-31；sprint4/dsp/core_only/src/tfb_8ch.h:32-33
  GRADE: [L1-example-called]（在档冻结源码常量；非板上测量）
- FACT: EQ 模块自带帧口径 EQ_FRAME=64 / EQ_FS_HZ=48000 / EQ_NCH=8，M2 须 _Static_assert 对齐 BENCH_FRAME / FS / DOLPH_W8_NCH（编译期断言，非静默假设）。
  SRC: sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:38-42
  GRADE: [L1-example-called]（在档集成说明 + 源码常量）
- FACT: Q31↔float 边界: FIRA 核路径 = 定点 Q31(bit-exact)；EQ 模块 = float32。M2 adapter 持有边界转换（前 EQ: int32 Q31→float；后 limiter 每通道: float→int32 Q31 给 DAC）。转换缩放为 M2 决策，未预判、未实现。
  SRC: sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:43-47, :129（gap 4「Q31<->float boundary -- not implemented」）
  GRADE: [declared-only]（接口已声明，转换代码未实现）
- FACT: EQ 在链中位置: master mono 流 → eq_master_process(2-3 biquad shaping, fan-out 前一次) → fan-out×8 + 每通道聚焦分数延迟(FIRA 核) → eq_limiter_process_ch×8(每通道保护, 阈值 T_k=T×w[k]) → 8 路功放。
  SRC: sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:12-35（链图 §1）
  GRADE: [declared-only]（集成意图链，未接入冻结流水线）
- FACT: io-callback 探针需求(H2 留的 [L3] 项): SPORT RX-buffer-processed 回调 core 成本 = H2 MDMA proxy 测不到的 io item-1 份额；预留口径 5-30 MCPS [L3, item-1 包络]，板上 CCNT bracket 升 [L1]。
  SRC: sprint5/H2_PASSLINE_DERIVATION.md:104,108,110；探针提案 M1_SYMBOL_SURVEY.md:157-171
  GRADE: [declared-only]（H2 在档为 [L3] 预留 + survey 提案，未实现/未板测）
- FACT: io-callback 探针挂点 = SPORT RX-buffer-processed handler（ALT.c:167 SPORTCallback, event ADI_SPORT_EVENT_RX_BUFFER_PROCESSED）；off-board MCPS = cb_cyc × block-rate / 1e6。
  SRC: M1_SYMBOL_SURVEY.md:159-166
  GRADE: [inferred]（survey 提案转引；挂点符号见 §3 ALT.c 回调；具体探针未实现）
- FACT: 探针 block-rate 口径不一致点(只列差异)：survey 探针示例用 block-rate=FS/256=187.5Hz（对齐例程 256-sample 块）；而 DOC-S4-IO-01 产品帧 ISR 口径 = FS/FRAME = 48000/64 = 750Hz。两口径源不同(例程块 256 vs 产品 FRAME 64)，最终 block-rate 随产品块大小定，待架构。
  SRC: M1_SYMBOL_SURVEY.md:166（48000/256=187.5）；sprint5/H2_WORKORDER.md:39（48000/64=750Hz）；块差异 DOC-S4-IO-01 G-IO6（audio_io_topology.md:66）
  GRADE: [inferred]（两数均在档；口径选择待架构，本轮不裁）
- FACT: buffer 放置约束(R24/R26 教训): MDMA proxy 缓冲(s_bh_src/dst)与 FIRA 工作集(s_h2_fa)同处 L1 Block 0(mem_block0_bw 0x2403f0..0x26ffff)→ 同物理块 → R24 gate FAIL → 须 #pragma section("seg_l1_block1") 移 proxy 缓冲到 L1 Block 1(不同物理块)。
  SRC: sprint5/audit/H2_MAP_PLACEMENT_ADJUDICATION.md:43-67, :139-148
  GRADE: [L1-example-called]（裁定输入为板 .map [L1] + .ldf [L1]; .map 重读待 bring-up）
- FACT: buffer 放置对 M1/M2: 例程 SPORT ping-pong 缓冲默认落 L1 Block 0(uncached→无须 flush)；若 M2 beamformer 工作集与 SPORT 缓冲同居 Block 0(H2/R24 自冲突型), bring-up 应将 SPORT 缓冲 pin 到 seg_l1_block1(L1 Block 1, R24 已证 fix)并重读 .map。
  SRC: M1_SYMBOL_SURVEY.md:107-118（§3 ping-pong 放置 + R26 note）；H2_MAP_PLACEMENT_ADJUDICATION.md:68-89（pragma fix）
  GRADE: [inferred]（survey 转引 + H2 裁定；产品 M2/SPORT 共置与否未定，pragma 形式已 [L1] 证于 ADI FIRA/IIRA 例程）
- FACT: #pragma section("seg_l1_block1") 形式 + 段名 = ADI FIRA/IIRA accelerator 例程实证([L1])，路由到 mem_block1_bw(app.ldf:460)。
  SRC: H2_MAP_PLACEMENT_ADJUDICATION.md:103-117（引 bsp/app_notes/fira_accel_code/.../IIR_Throughput_21569_V2.c:23-30）
  GRADE: [inferred]（H2 裁定转引 ADI 例程；本轮未亲开 IIRA 例程原文）
- FACT: limiter 阈值 t_base = 占位 [L4]（桌面 0.8 满量程），最终值待线③厂家函(Xmax/热额定)+U3 功放增益；结构完整、唯一开口标量。
  SRC: sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:56-58, :125-128（gap 3）
  GRADE: [declared-only]（占位声明，真值待 L1 外部输入）
- FACT: EQ 系数 = 当前 flat/unity 占位 + 2 个测试 biquad；产品频带系数待 R3 消声室在轴响应(EQ_PRD:45)；M2 加载实测系数，接口 eq_biquad_set 已定。
  SRC: sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md:53-55, :122-124（gap 2）
  GRADE: [declared-only]（接口已声明；产品系数待 R3 L1）

## F-5 已知 board-confirm 项汇总（survey 转引 + 核）

- FACT: CCES 2.11→2.12 头文件名漂移: ALT 为 2.11.1，bench 为 2.12.1；须 grep 安装版 2.12.1 SHARC/include 核 adi_sport.h / adi_pdma_2156x.h / adi_twi_2156x.h / adi_spu.h。
  SRC: M1_SYMBOL_SURVEY.md:143
  GRADE: [board-confirm]
- FACT: 头文件后缀不对称(R25 adi_mdma 9-error 类陷阱): ALT 含 adi_sport.h/adi_spu.h(无后缀) 但 adi_twi_2156x.h/adi_pdma_2156x.h(有后缀)；且 adi_sport_2156x.h 与 adi_sport.h 并存——bring-up 须逐驱动核安装版 2.12.1 确切头名,不得假设 2.11.1 名通用。
  SRC: M1_SYMBOL_SURVEY.md:144
  GRADE: [board-confirm]
- FACT: ADI_SPORT_MEMORY_SIZE / ADI_TWI_MEMORY_SIZE / ADI_SPU_MEMORY_SIZE 数值须在安装版头解析确认(用作数组尺寸)。
  SRC: M1_SYMBOL_SURVEY.md:145
  GRADE: [board-confirm]
- FACT: adi_sport_ConfigMC / ConfigFrameSync 对「8-slot」的形参语义须开安装版 adi_sport.h 核(ALT 用 7u 表 8 slots, 须验 count-vs-index 约定)。
  SRC: M1_SYMBOL_SURVEY.md:146
  GRADE: [board-confirm]
- FACT: codec SAI 字段 = TDM8(SAI=011) 用于 8ch + DAC slot/CMAP 8-of-12 映射,须 datasheet adau1979 Register 0x05-0x08 + ADAU1962A DAC_CTRL/slot 在 bring-up 核(G-M1-1/G-M1-3)。
  SRC: M1_SYMBOL_SURVEY.md:147,151-153
  GRADE: [board-confirm]
- FACT: DMA 缓冲 cache 操作(仅当缓冲移出 L1 时): flush_data_buffer in <sys/cache.h>(H1 A5 符号),仅在 cached L2/external 放置时需要。
  SRC: M1_SYMBOL_SURVEY.md:148
  GRADE: [board-confirm]
- FACT: 8ch → ADAU1962A 通道映射 + → 8 路 A/B 物理连线(哪 DAC ch 驱哪路功放/哪对喇叭) = 产品布线设计,文档无。
  SRC: DOC-S4-IO-01 = sprint4/audio_io_topology.md:64（G-IO4）；M1_SYMBOL_SURVEY.md:153（G-M1-3）
  GRADE: [board-confirm]
- FACT: TDM slot 精确时序(BCLK/FSYNC 极性、slot 起始、24-in-32 对齐)未给,待示波器/逻辑分析仪或 EZKIT 对齐。
  SRC: DOC-S4-IO-01 = sprint4/audio_io_topology.md:65（G-IO5）
  GRADE: [board-confirm]
- FACT: 产品流水线块大小待定(例程 BLOCK 口径 = COUNT=300/ALT 256-ch 缓冲；我方 FRAME=64)——影响延迟/DMA。
  SRC: DOC-S4-IO-01 = sprint4/audio_io_topology.md:66（G-IO6）；ALT.h:24（#define COUNT 300）；ALT.c:26-38（256 长 float 通道缓冲）
  GRADE: [board-confirm]
- FACT: SoftConfig 直进直出软开关(U48 Port A/B)在非 A2B 拓扑下具体配置值待工程师确认；例程用 ConfigSoftSwitches_ADC_DAC(extern, SoftConfig_*.c)。
  SRC: DOC-S4-IO-01 = sprint4/audio_io_topology.md:67（G-IO7）；M1_SYMBOL_SURVEY.md:136（extern board SoftConfig）
  GRADE: [board-confirm]
- FACT: 重建带 pragma 的 .map 须在板上重读确认 s_bh_src/dst 落 ≥0x2c0000(Block 1) 且 s_h2_fa 仍 <0x270000(Block 0)——F24-MAJOR-1 放置验证义务持续。
  SRC: sprint5/audit/H2_MAP_PLACEMENT_ADJUDICATION.md:87-89, :134-136
  GRADE: [board-confirm]

## NOT_FOUND
- 板级原理图 PDF(schematics/V2.1, V1.2, V1.0)内 SPORT4↔codec 外部网名级连线 / AD2428W-SOM 物理旁路走线: PDF 未在本轮渲染核名(例程 SRU 仅证片上 DAI 路由)。
- 外部 MCLK 晶振源具体器件/频率(片外主时钟来源): 例程仅写 codec PLL 内部生成 256×fS,片外参考晶振未在例程/DOC-S4-IO-01 出现。
- 例程实际采样率寄存器解码值(确认例程真跑 48k 而非 datasheet 仅支持): DOC-S4-IO-01 G-IO1 自列为 gap,本地无寄存器 dump。
- adau1979.pdf / ADAU1962A.pdf 内 TDM/PLL 行号本轮未重抽 PDF 原文(沿用 survey 转引行号 + 表/节锚;行号随 pdftotext 版本漂移)。

## VERIFIER_REPORT
- CHECKED: 全部 49 条 fact 独立开源核 (adversarial citation verify, 引用对抗核验员 @ claude-opus-4-8 / 2026-06-06)
  - [L1-example-called] 全核 (命门级,不抽样): F-1 行12-38(SPORT4/4A-Tx/4B-Rx/MC_MODE/SPU57-58/SRU PB05-PB04-PB02-PB06/DAI1_IE), F-2 行51-53+57-59(ConfigMC 7u/SelectChannel 0..11/0..3), F-3 行75-86(SRU 时钟主从/PLL 写序), F-4 行93-98+114-116 — 逐条亲开 ALT.c/ALT.h/bench_harness.h/tfb_8ch.h/EQ_NOTE/H2_MAP 核行号+API 名+实参,全部精确命中 (无一需 +-2 修正)。
  - [datasheet] 核 4/4 = 100% (>=60% 达标): adau1979 Table 10「TDM8/32 Bit Clocks Per Slot/256×fS」(pdftotext l.2449 区真实存在,内容符), ADAU1962A「12.288MHz @48k/256×fS」(l.294+l.2474-2476 精确), adau1979 PLL 帧时钟参考 (l.1821 区「PLL can accept the audio frame clock as reference」), Register 0x05-0x08 SAI_CTRL0/1+CMAP12/34 (l.2226+寄存器图真实)。
  - [declared-only]/[board-confirm] 核判定: F-4 行99-104/123-128(Q31<->float/limiter t_base[L4]/EQ 系数/链位置=真接口已声明未实现), F-5 行132-164(CCES 2.11→2.12 头名/后缀漂移/MEMORY_SIZE/ConfigMC 8-slot/SAI/布线/时序/SoftConfig/.map 重读=真须安装版或板上确认) — 判定均正确,无「本地有头却标 board-confirm」「例程实调过却被降级」误判 (ALT.c:16-18 include 名确为 2.11.1 例程口径,非 2.12.1 安装版)。
  - [inferred] 核: F-2 行45-47/54-56/60-71, F-3 行87-89, F-4 行108-113/117-122 — 均诚实标注为推导/survey 转引/架构待定,无伪装成事实者;ConfigData=31@ALT.c:299/ConfigClock=32@:301 经独立核实际精确,fact 保守降 [inferred] 可辩护。
  - 源文件存在性: schematics/V2.1 PDF (双A2B底板/21569核心板) + adau1979.pdf/ADAU1962A.pdf 均在档;NOT_FOUND 四项(PDF 网名/片外晶振/寄存器 dump/PDF 原文行号)诚实,未编。
- VERDICT: CLEAN
- MISMATCH: (none)
  注(非 mismatch,记录供 CTO 知悉): F-3 行84 写法「REG_PLL(0x01)=0x03」将 ALT.c:654 REG_POWER=0x01 与 :655 REG_PLL=0x03 两写并排表述略含混,但实质主张 (REG_PLL=0x03 + 轮询 bit7) 与行范围 :655-663 均准确,非 FABRICATION,不删不改。

## SUMMARY
本盘点确认产品 SPORT4 拓扑骨架已有完整 [L1] 例程坐实(ALT = Audio_Loopback_TDM, 真 21569 ADAU1979→SPORT4 TDM→ADAU1962A): SPORT device 4, 4A=Tx(发 DAC)/4B=Rx(收 ADC), 均 MC(TDM)模式; 片上 SRU 路由(DAI1_PB05 时钟/PB04 FS/PB02 DAC 数据出/PB06 ADC 数据入)逐行可引。主从时钟口径明确——例程 DAC(ADAU1962A)为时钟主, BCLK/FS 经 SRU 扇出到 SPORT4 与转发 ADC, 单时钟域; DAC/ADC PLL bring-up 写序均例程实跑, 256×fS@48k=12.288MHz 为 datasheet 口径。8-slot TDM 在 slot 数/位宽/fS/BCLK 四项产品与例程一致(例程 ConfigMC 7u⇒8 slots 已亲核), 三处差异均为 codec 寄存器/映射选择(非阻塞): ①SAI 字段 TDM8-vs-I2S 命名(G-M1-1)②1-in/8-out slot/CMAP 映射(G-M1-2, SelectChannel 须 0..7)③8-of-12 DAC→8 amp 路由(G-M1-3)。M2 FIRA 接口预留事实齐备: 链帧口径 FRAME64/48k/8ch[L1 源码常量], Q31↔float 边界与 EQ 链位置/limiter 阈值/EQ 系数均为已声明未实现(declared-only, 真值待 R3 消声室与线③厂家函的 L1), io-callback 探针为 H2 [L3] 预留(挂 SPORT RX-done 回调升 L1; 注一处 block-rate 口径差: survey 187.5Hz 对齐例程块 256 vs 产品帧 ISR 750Hz=FS/64, 待架构选), buffer 放置带 R24/R26 硬教训(proxy 与 FIRA 同 L1 Block 0 → R24 FAIL → #pragma seg_l1_block1 移 Block 1, pragma 形式 ADI 例程已证)。board-confirm 项集中在 CCES 2.11→2.12 头名/后缀漂移(R25 9-error 类)、MEMORY_SIZE 宏、ConfigMC 8-slot 形参语义、codec SAI/CMAP 寄存器、8ch→功放物理布线、TDM 精确时序、流水线块大小、SoftConfig 直进直出开关值、.map 重读——均 grep/示波器可钉, 无 MDMA 式意外预期。NOT_FOUND 四项主要是板级 PDF 网名/片外晶振源/寄存器 dump/PDF 原文行号, 本地不可闭, 不编。
