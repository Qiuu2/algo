# M2 SURVEY -- FIRA beam chain insertion into M1 real-time frame callback

> dsp-algorithm teammate (M2 调研专员), 2026-06-08. CTO 派单 M2 调研.
> SCOPE: 调研型 -- 只出事实 + 来源 (文件:行 / 在档数) + L 级. 不写实现代码, 不裁 M2 架构,
>   不下选型. 冻结代码零触碰 (tree_filterbank.c/tfb_8ch.c/.h/golden_ref.h/chirp_input.h/
>   fir_coeffs_hb63.h/.ldf 只读对照). ASCII only. 不 commit.
> NOT a board-result prediction. M2 = 把 FIRA 波束链插进 M1 实时帧回调, 冻结代码零触碰只接线.
> M1 透传 loopback 已上板 PASS (声进->原样出); M2 = 算法入环.

---

## 0. 现场基线 (已读, 全在档)

| 件 | 路径 | 用途 |
|---|---|---|
| M1 回调实现 | sprint6/dsp/audio/m1_loopback_tdm.c | 接入点 (item 1) |
| M1 头/几何 | sprint6/dsp/audio/m1_loopback_tdm.h | FRAME/slot/buffer 口径 |
| M1 工程 .ldf | sprint6/dsp/audio/m1_project/system/startup_ldf/m1_app.ldf | pin 落地 (item 3) |
| 冻结 8ch 入口 (只读) | sprint4/dsp/core_only/src/tfb_8ch.h | 产品 8ch 拓扑参照 |
| 冻结核入口 (只读) | sprint4/dsp/core_only/src/tree_filterbank.h | 子带/Q 口径 |
| FIRA 编排接口 (只读) | sprint4/dsp/fira/fira_tree.h | M2 真正要 call 的入口 |
| H1 harness | sprint5/dsp/harness/h1_wcet_measure.c | FIRA 帧调用序参照 |
| H2 harness | sprint5/dsp/harness/h2_dma_isr_measure.c | FIRA 帧调用序参照 |
| H2 .map 放置裁定 | sprint5/audit/H2_MAP_PLACEMENT_ADJUDICATION.md | pin pragma/段名 [L1] |
| 通过线溯源 | sprint5/H2_PASSLINE_DERIVATION.md | deadline 核数据源 |
| M1 架构审 (R34) | sprint6/dsp/audio/M1_ARCH_REVIEW_R34.md | 余量/缺数据交叉 |

---

## 1. 接入点 (M1 回调里 FIRA 插哪几行)

### 1.1 回调精确结构 (m1_loopback_tdm.c)
`m1_sport_rx_callback()` @ :180-221. 现在做的就是 1 个 RX 样本 -> 8 个 TX slot 复制:

```
:185   if (nEvent != ADI_SPORT_EVENT_RX_BUFFER_PROCESSED) return;   // 只服务 RX-done
:187   t0 = bench_cyc_target();                                     // CCNT bracket OPEN (io-callback 探针)
:189   const uint32_t half = s_m1_pp_index & 1u;
:190   const int32_t *rx = s_m1_rx_buf[half];   // 64 words = 1 slot x 64 frames (packed, mono)
:191   int32_t *tx = s_m1_tx_buf[half];         // 512 words = 8 slot x 64 frames
:197-204  FAN-OUT 1->8 LOOP:
          for (f=0; f<M1_FRAME(=64); f++) {
:198        int32_t sample = rx[f];                  // 1 个 mono RX 样本 (帧 f)
:200        int32_t *txf = &tx[f * M1_TX_SLOTS(=8)]; // 该帧的 8 TX slot 基址
:201        for (s8=0; s8<8; s8++) txf[s8] = sample; // <<== 现复制 (8 slot 同值)
            ...nz/peak FG 统计...
          }
:208-210  block_count++ / pp_index++
:212   t1 = bench_cyc_target();                                     // CCNT bracket CLOSE
:214   g_m1_cb_cyc_last = t1 - t0;                                  // io-callback core 成本 raw
```

### 1.2 M2 精确插入点 (事实, 不裁架构)
- **替换的精确范围 = 复制内层循环 :201** (`for s8: txf[s8] = sample;`). M1 现在把同一 mono
  样本写进 8 个 slot; M2 要换成「1 mono RX 帧 -> FIRA 8ch 波束链 -> 8 个不同加权/延迟的 TX slot」.
- **更可能的真实粒度 = 整帧级, 不是逐样本级** [inferred]: FIRA/树形分频是块处理 (一帧 64 样本一次
  analyze/synthesize, 见 item 2.3), 不是 per-sample. 所以 M2 的接法更像「在 :197 的 per-frame
  循环之外, 对整个 64 样本的 RX 帧调一次 8ch FIRA, 产出 8 行 x 64 样本, 再 deinterleave 写进 TX 的
  8-slot 交织布局 (txf[s8])」. M1 现行 per-sample 复制循环 (:197-204) 是 M2 要重构成
  「整帧喂 FIRA -> 8ch 输出 -> 按 slot 交织回写」的区间. [inferred -- M2 架构由 CTO 裁]
- **冻结代码零触碰**: tree_filterbank.c / tfb_8ch.c 不改; M2 只在 M1 回调里 (sprint6 board TU)
  `call` FIRA 入口 (item 2 的 fira_*). 冻结令例外项已排 SPORT bring-up 顺带坐实 io-callback
  (M1_ARCH_REVIEW_R34:缺数据#4 / H2_WORKORDER:170).
- **CCNT bracket 复用**: :187/:212 的 t0/t1 探针包住回调体 -> M2 后这就是「core+focus+io-callback
  单帧 wall」的现成 io-callback [L1-to-be] 量测点 (g_m1_cb_cyc_last/max). M2 不必新造探针. [L1-example-called: bench_cyc_target = bench_main.c:118 CCNT]

### 1.3 接入点开口 (M2 架构待裁, 不在本调研收口)
- ⚠ **粒度 (逐样本 vs 整帧)**: FIRA 是块处理 -> 整帧接法; 但 M1 现行 fan-out 是 per-sample. M2 接法
  = per-frame FIRA + deinterleave, 是重构不是「替一行」. **[inferred, CTO 裁 M2 数据流]**
- ⚠ **TX slot 交织布局**: M1 的 TX 是 unpacked 8 words/frame (txf[0..7] = 帧 f 的 8 slot). FIRA
  输出是 8 行 (每行 64 样本/帧, 见 tfb_8ch.h:53). M2 须把 [8ch][64] -> [64frame][8slot] 交织.
  这是格式转换点之一 (与 item 2 的 Q 边界正交). [inferred]

---

## 2. 冻结代码接口 (FIRA 工作集在 M2 帧回调中怎么调)

### 2.1 M2 真正要 call 的是 fira_tree.h, 不是 tfb_8ch.h (重要事实)
- H1/H2 harness 调的是 **fira_tree.h** 的 `fira_*` 入口 (sprint4/dsp/fira/fira_tree.h), 工作集类型
  = **FiraChannelState** (fira_tree.h:115), 即 memory.md / 派单说的 `s_h2_fa` 那类
  (h2_dma_isr_measure.c:107 `static FiraChannelState s_h2_fa[DOLPH_W8_NCH(=8)]`).
- **tfb_8ch.h 的 Tfb8State / tfb8_process (tfb_8ch.h:40/53) 是 core-only (纯软件, 无 FIRA 加速)
  路径**; 它是 R14 bit-exact 的金标参照 (tfb_8ch.h:18 S2 CRC 0x90556BC7), **不是** H1/H2 板上测
  算力的那条 FIRA 链. M2 要插的是 FIRA 加速链 (fira_tree.h), tfb_8ch.h 仅作拓扑/bit-exact 对照只读.
  [L1, 两件头互证]
- fira_tree.h 复用 tree_filterbank.h 的 HbFirState/子带布局口径 (fira_tree.h:53 include).

### 2.2 入口函数签名 (sprint4/dsp/fira/fira_tree.h, 只读不改)
M2 帧回调要按 H1/H2 同款序调这几个 (签名逐一在档):

| 阶段 | 函数 (fira_tree.h:行) | 签名 | 时机 |
|---|---|---|---|
| 一次性 setup | `fira_tree_setup(void)` :160 | `int fira_tree_setup(void)` 返回 0=ok | init 时调一次 (Open->RegisterCallback->CreateTask->FixedPointEnable), **不在帧预算内** (:157-159) |
| 系数注入 | `fira_tree_set_coeffs` :122 / `fira_tree_use_real_coeffs` :126 | `void(const int32_t *hb_coef_fira32, uint16_t ntaps)` | init, 绑定冻结 g_hb63_fira32 (fir_coeffs_q31.h) |
| 通道 init | `fira_channel_init` :129 | `void(FiraChannelState *ch, uint16_t frame)` | init, **每 ch 一次** (8 ch 各一次), 清状态+填段元数据 |
| 帧分析 | `fira_tfb_analyze` :167 | `void(FiraChannelState *ch, const int32_t *in, uint16_t frame, int32_t *sb0,*sb1,*sb2,*sb3)` | 每帧每 ch |
| 帧合成 | `fira_tfb_synthesize` :170 | `void(FiraChannelState *ch, const int32_t *sb0..*sb3, uint16_t frame, int32_t *out)` | 每帧每 ch |
| teardown | `fira_tree_teardown(void)` :176 | `void(void)` | exit 调一次 (adi_fir_Close) |

> **重要**: `fira_tfb_analyze/synthesize` 的签名**与冻结核 tfb_analyze/tfb_synthesize 故意逐字一致**
> (fira_tree.h:163-165 注: 为让 bench 直接替换做 per-subband CRC). 所以 M2 接法 = 对每个 ch 调
> analyze -> (波束加权/延迟) -> synthesize, 与 tfb_8ch.h:18 描述的 per-channel 独立链同构.

### 2.3 H1/H2 实际调用序 (8ch 帧, 板证, 可照搬接线)
H2 `h2_fira_frame()` (h2_dma_isr_measure.c:110-122) 是最干净的 8ch 帧模板:
```
:115 for (c = 0; c < DOLPH_W8_NCH(=8); c++) {
:116   const int32_t w = g_dolph_w8_q15[c];                 // Dolph-Cheb -20dB 每通道权 (Q15)
:117   for (i=0;i<BENCH_FRAME(=64);i++)
:118     xw[i] = ((int64_t)w * (int64_t)xin[i]) >> 15;      // 输入级加权 (== f5_apply_w), Q15 x Q31 >> 15
:119   fira_tfb_analyze(&s_h2_fa[c], xw, 64, fsb0,fsb1,fsb2,fsb3);   // 1ch -> 4 子带
:120   fira_tfb_synthesize(&s_h2_fa[c], fsb0..fsb3, 64, fout);       // 4 子带 -> 1ch 全速率
   }                                                        // 8 ch 各独立, 无跨通道 sum (产品=8 DAC 声学叠加)
```
init 序 (h2:138-150 / h1:277-289):
```
fira_tree_setup() != 0 -> return 0 (无 FIRA honest-0)
tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS)          // core golden Q15 系数
for c in 0..7: fira_channel_init(&s_h2_fa[c], 64)   // 8 ch 各 init
```
- **每帧 64 样本怎么喂**: 一帧 = 64 样本 (M1_FRAME=BENCH_FRAME=64, 同源). 每 ch 把 64 样本 xw[64]
  喂 analyze, 得 4 子带 (sb0=8 / sb1=16 / sb2=32 / sb3=64 样本, h1:29-31 + tree_filterbank.h:127-131),
  synthesize 回 64 样本 fout. 8 ch 循环 -> 8 行输出. [L1, harness 在档]
- **波束加权位置**: H1/H2 的 Dolph 权是**输入级** (xw = w*xin, h2:118). 真聚焦/延迟 (focus frac-delay)
  在 H1 是**子带级** (analyze 与 synthesize 之间, h1:244-249). M2 的「8 slot 不同加权/延迟」落哪级
  (输入级权 vs 子带级 frac-delay vs 两者) = **M2 架构待 CTO 裁**, 本调研不收口. [inferred]

### 2.4 数据格式 + Q 边界 (R37/R38 标的 Q31-float/int 边界, M2 owns)
**这是 M2 的格式命门 -- 逐点列事实**:
- **FIRA 核 = Q31 定点** (tree_filterbank.h:31 「系数 Q15, 状态/中间 Q31, MAC 累加 Q46(int64)」;
  fira_tfb_analyze/synthesize 全 int32 = Q31 语义). 子带/输出全 int32 Q31. [L1, 冻结头]
- **M1 音频 = int32 (32-bit slot word)** (m1_loopback_tdm.h:24 M1_WORD_BYTES=4; SPORT
  ConfigData DTYPE_SIGN_FILL 31-bit, m1_loopback_tdm.c:314/322 -> 32-bit 容器, 24-bit 有效数据
  ADC SAI_CTRL1 DATA_WIDTH=0=24-bit, m1:155). 即 M1 的 RX/TX 是 **24-bit-in-32-bit 左对齐
  int32** (codec 数据宽 24, SPORT 槽 32). [L1, M1 .c 在档]
- **格式边界 = M1 int32 音频 <-> FIRA Q31 的转换点** (R37/R38 标):
  - RX 侧: M1 rx[f] (int32, 24-bit-in-32 左对齐) -> FIRA xw (Q31). 24-bit 左对齐进 32-bit 即
    Q31 高 24 位有效, 低 8 位 0 -> **可能直接当 Q31 用** (左对齐=幅度对齐), 但**须 board-confirm
    SPORT 是左对齐还是右对齐** (DTYPE_SIGN_FILL 31 暗示符号填充到 bit31 = 左对齐 [inferred],
    须核 HRM). [board-confirm]
  - TX 侧: FIRA fout (Q31) -> M1 tx slot (int32, codec 取高 24 位). Q31 直接写 int32 slot,
    codec DAC 取高 24 位 -> **幅度对齐自洽** [inferred], 同须核左/右对齐.
  - **转换点精确位置**: 就在 item 1.2 的接入区间 -- RX 帧喂 FIRA 前 (item 2.3 的 xw 装填,
    现 h2:117-118 是 Q15 权 x Q31, M2 的 RX int32 在此处对齐成 Q31), 与 FIRA 输出回写 TX 后
    (fout -> txf[s8] 交织, item 1.3). **M2 owns 这两个边界的对齐 + 饱和.** [R37/R38]
- ⚠ **FIRA 定点输入格式 enum 只有 UNSIGNED/SIGNED_INTEGER** (fira_tree.h:42-43 R14 临界点):
  「ours = signed-fractional Q15xQ31; FIRA enum 只有 INTEGER」-> Q 格式转换点 fira_tree.h:43 标
  「each marked high bit-deviation risk, must board bit-by-bit」. Path B runtime
  FixedPointEnable(SIGNED_INTEGER) (fira_tree.h:27-29). **M2 的 Q31 <-> FIRA INTEGER 语义对齐
  是 R14 bit-exact 板核范围, 桌面不能确认.** [L1/EZKIT, 待板]
- ⚠ **headroom 约定**: 半带链输入预留 -4.8dB (tree_filterbank.h:38-41, =1/1.7309) 防软削波 +
  Q31 回量化饱和钳位 (PF-4). M2 的 RX->Q31 装填须守这个 headroom (节目素材不进软削波), 真值标定
  属 EZKIT [L1]. M2 的输入级加权/fan-out 不得突破 Sum|h|=1.7309 的满量程上界. [L2 host / 板标定]

### 2.5 接口开口
- M2 的工作集类型 = FiraChannelState[8] (~18KB, item 3), 每 ch 跨帧 history 62 样本/段 x 9 段
  (fira_tree.h:107/113 D3/ST1 cross-frame). M2 须持有这 8 个 state 跨帧 (不能每帧重置).
- 波束加权/延迟落哪级 (输入级/子带级/both) = CTO 裁.
- Q31 <-> FIRA INTEGER + 左/右对齐 = R14 bit-exact 板核 + HRM 对齐核 [board-confirm].

---

## 3. ④开口落地 (pin Block 1)

### 3.1 为什么 M2 要 pin (R24/R26 自冲突教训)
- **M1 现状 = 不 pin, buffer 落 Block 0** (m1_app.ldf:10 「opening 4: M1 NO pin; FIRA working
  set is absent from THIS build」; m1_loopback_tdm.c:97 「default L1 Block 0」). M1 阶段安全 ==
  M1 build **无 FIRA 工作集** (M1_ARCH_REVIEW_R34 ④-1: grep 零 FiraChannelState), 故 SPORT
  buffer (~4.6KB) 落 Block 0 无自冲突对象. [L1]
- **M2 接 FIRA 那一刻**, FiraChannelState[8] (s_h2_fa 那类) 进 build. 若 SPORT buffer 与 FIRA
  工作集**同落 Block 0**, 就是 R24 裁定的自冲突 (H2_MAP_PLACEMENT_ADJUDICATION:62
  「same L1 block -> intra-Block-0 single-port bank conflict ... artifact」). **这就是 M2 必须
  pin 的根因.** [L1, R24 门 FAIL 已裁]
- ⚠ **pin 时机 = M2 接 FIRA 那一刻, 不是笼统「M2 前」** (M1_ARCH_REVIEW_R34 ④ 漏点: 若 M1/M2
  同 build 渐进集成, FIRA 一进 Block 0 即恢复自冲突风险). [inferred, R34 已标]

### 3.2 怎么 pin (pragma 段名 + .ldf 段, 全 [L1] 板证)
- **方式 = source-side #pragma section, .ldf 冻结只读不改** (H2_MAP_PLACEMENT_ADJUDICATION:68-83):
```
#pragma section("seg_l1_block1")
static FiraChannelState s_m2_fa[8];      // FIRA 工作集 -> L1 Block 1 (离 SPORT buffer)
```
  (或反过来 pin SPORT buffer 到 Block 1, 把 FIRA 留 Block 0 -- 哪个 pin 由 CTO 裁; R24 是
  pin proxy buffer 离 FIRA, M2 对称地隔离两者即可).
- **段名 `seg_l1_block1` 在 M1 .ldf 中存在且路由到 mem_block1_bw** (m1_app.ldf:473/484/497/504
  `INPUT_SECTIONS( $OBJS_LIBS(seg_l1_block1 ...) ) ... > mem_block1_bw`). 与 H2 base .ldf 同名同路由. [L1]
- **pragma 形式 + 段名是 ADI 自家加速器例程板证 [L1]** (H2_MAP_PLACEMENT_ADJUDICATION:103-117):
  bsp/app_notes/fira_accel_code/.../FIR_Throughput_21569.c + IIR_Throughput_21569_V2.c:23-30
  用同款 `#pragma section("seg_l1_block1")` 放加速器 DMA buffer. 同 buffer 类 (加速器-DMA 数据).
  **非自造.** [L1]
- pragma 只作用于紧跟的下一个定义 -> 每个 buffer 一条 pragma (H2:76).

### 3.3 Block 边界 (M1 .ldf 实数, 关键差异)
| Block | 窗口 (m1_app.ldf) | 大小 |
|---|---|---|
| L1 Block 0 | 0x2403f0 - 0x26ffff (:158) | ~191KB (DM data home, M1 buffer 落此) |
| L1 Block 1 | **0x2c0000 - 0x2ebfff** (:165) | **~176KB** (末 16KB = DM cache) |
- ⚠⚠ **M1 .ldf 的 Block 1 END = 0x2ebfff, 不是 H2 base 的 0x2effff** (m1_app.ldf:7-9 R40
  MINOR-3 明标: 「Audio_Loopback base sets Block1 END=0x2ebfff (last 16KB = DM cache); the H2
  bench base had END=0x2effff. M1 uses Block0 only so harmless here, **but if M2 later reuses
  THIS .ldf, Block1 usable space is 16KB smaller than the H2 base assumed**」).
  => **M2 若沿用 M1 .ldf, Block 1 可用空间比 H2/R34 假设的 192KB 小 16KB (实 ~176KB)**.
  M2 需求 ~24KB (FIRA 18KB + SPORT 4.6KB) << 176KB, **仍放得下, 但 CTO 须知此 16KB 差**. [L1, M1 .ldf 在档]
- M2 需求总量 (M1_ARCH_REVIEW_R34 ④-2): SPORT buffer ~4.6-6KB + FiraChannelState[8]
  ~17.9KB (0x47a0=18336B, H2_MAP:14) = **~24KB**. Block 1 ~176KB 余量充足.

### 3.4 pin 落地开口
- ⚠ **产品 .map 待补** (M1_ARCH_REVIEW_R34 缺数据#5; R34 审查列的缺数据): pin 决策须基于**产品
  build 的 .map** (M1/M2 实际分配), **非 H2 harness .map** (proxy s_bh_src/dst 只活 harness
  build, 产品不含). H2_MAP 的 0x25fe88 等地址是 harness .map, M2 产品 .map 须 bring-up 重读确认
  s_m2_fa/SPORT buffer 实落块. [board-confirm]
- ⚠ **identical-segment vs same-arbitration-class** (R26 F26-MAJOR-1 残留, H2_MAP:99-101):
  pin Block 1 是 same-bus-class proxy, **非产品 SPORT 缓冲实落 L1 还是 L2 的实证**. M2 pin 是否
  真隔离争用, 须 bring-up 核产品 SPORT 缓冲实际落块 (F24-MAJOR-1 .map 重读义务持续). [board-confirm]
- ⚠ **哪个 pin 离哪个** (FIRA 工作集 pin Block 1, 还是 SPORT buffer pin Block 1) = CTO 裁;
  目标 = 两者不同物理块即可. [inferred]

---

## 4. deadline 核 (750Hz=1.333ms 帧内吃得下吗)

### 4.1 deadline 形式 (单帧回调 wall time < 1.333ms)
- 帧率 fps = M1_FS_HZ/M1_FRAME = 48000/64 = **750 Hz** (m1_loopback_tdm.h:21). [L1]
- 帧周期 = 1/750 = **1.3333 ms**. [L1-derived]
- CCLK = **1.0e9 Hz** (F7 板跑 g_f7_cclk_hz, H2_PASSLINE:14 [L1/EZKIT]).
- deadline (单帧可用 cycle) = 1e9 x 1.3333e-3 = **1,333,333 cyc/帧** (= 1.0x, 无余量). [L1-derived]
- T2 正式阈值 **>=1.5x** (DEC-S4-CRITERION-01-FINAL, H2_PASSLINE:13) -> demand 须
  <=666.67 MCPS <=> 单帧 wall <= **888,889 cyc = 0.8889 ms**. [裁定 + L1-derived]

### 4.2 单帧成分账 (每个 MCPS 带在档出处, 换算 cyc = MCPS x 1e6 / 750)
| 成分 | MCPS | 单帧 cyc | 出处 | L 级 |
|---|---|---|---|---|
| 核 8ch FIRA | 347.45 | 463,267 | F7 g_f7_cyc_8ch_fira=463,273 x750/1e6 (H2_PASSLINE:17) | [L1/EZKIT] |
| 聚焦增量 | 49.03 | 65,373 | H1 g_h1_cyc_focus_only=65,371 x750/1e6 (H2_PASSLINE:18) | [L1/EZKIT] |
| io-callback (M1 回调体 b) | ~~9.63~~ | 12,839 | M1 g_m1_cb_cyc_*=12839 **板已实测 [L1]** (m1:187/212/214) -- **R42 裁: 此=app 负载(b, fan-out+FG), 非 M2 io-callback 核(a); M2 不带** | [L1] 但=app(b) |
| io-callback 核(a) for M2 | **<=30** | -- | dispatch+descriptor, **本探针未测**, M2 须 spec dispatch 探针 (R42); deadline 用预留 worst 30 | [L3 预留] |
| O1 EQ (worst) | 60 | 80,000 | DEC-S5-EQ-O1-01 (O1 LEAN 29-60 [L4] 取 worst) (H2_PASSLINE:19) | [L4-pinned] |

> ⚠ **[R42 reconcile]** 12839 cyc 现已板上实测 [L1] (M1 PASS), 算术 12839x750/1e6=9.629 MCPS 自洽.
> **但 R42 裁定: 9.629 = M1 回调体的 app 负载(b)=fan-out 1->8+FG 扫描, bracket(:187/212) 没罩到
> io-callback 核(a)=SPORT dispatch+descriptor (在函数进入前).** M2 回调体换成 FIRA (已计 core 347.45),
> M1 的 fan-out(b) 不带入 M2; M2 真正的 io-callback 是核(a), 本探针未测 -> deadline 用核(a)预留
> worst 30 (上方表). 核(a)[L1] 坐实须 M2 spec dispatch-inclusive 探针 (R42 登记). 详见
> M1_IOCALLBACK_L1_ADJUDICATION.md.

### 4.3 deadline 余量计算 (两情形)
> ⚠⚠ **[R43 F43-MAJOR-1 口径修正 -- 见 M1_IOCALLBACK_L1_ADJUDICATION.md / R42]**：本节原把 9.63 当 M2
> io-callback 是口径错（本调研先于 R42 io-callback 裁定）。R42 已裁：**9.63 MCPS = M1 fan-out app 负载
> (b)，M2 不带**（M2 回调体换成 FIRA 波束，已计入 core 347.45；M1 的 fan-out 复制不进 M2）。M2 真正的
> io-callback = **核 (a)**（SPORT dispatch+descriptor），本 M1 探针 bracket(:187/212) 没测到它。故 M2
> deadline 应用 **io-callback 核 (a) 预留 ≤30 MCPS(worst)** 代替 9.63。**下表已按 R42 修正用核(a) worst=30**
> （原 9.63 行作废，仅留作 M1 app 负载旁证）。结论 PASS 不变（30 vs 9.63 是 396 core+focus 的零头）。

**情形 A: M2 = core + focus + io-callback核(a) (O1 EQ 是后续独立 stage, 未上板)**
```
demand = 347.45 + 49.03 + 30[io-cb核(a) worst, R42] = 426.48 MCPS
单帧 wall = 568,640 cyc = 0.5686 ms
1.0x deadline 余量 = 1000/426.48 = 2.34x   (wall 0.5686ms < 1.3333ms deadline)
```
**情形 B: + O1 EQ worst(60)**
```
demand = 347.45 + 49.03 + 30[io-cb核(a)] + 60 = 486.48 MCPS
单帧 wall = 648,640 cyc = 0.6486 ms
1.0x deadline 余量 = 1000/486.48 = 2.06x   (wall 0.6486ms < 1.3333ms deadline)
对 T2 666.67 线: 666.67/486.48 = 1.37x  (<1.5x, 但这是 demand 未含争用/其余预留的 base)
```
> [口径无关性, critic R43 独立复算]：用 R42 正确的核(a) worst=30 后，情形 B 仍 **2.06x 吃得下**
> （0.6486ms ≪ 1.333ms）。9.63→30 的 delta(20.37 MCPS)是 396 core+focus 的零头 → **「单帧 wall
> ≪ deadline」结论与 io-callback 口径无关，稳**。io-callback 核(a)[L1] 坐实须 M2 spec dispatch-inclusive
> 探针（罩整 ISR 或 empty-callback baseline，R42 登记），M1 的 9.63 不能替（拿 app 负载 b 替核 a = 欠计）。

### 4.4 结论: 吃得下 (但 io-callback 真值待板, 且 T2 系统侧闭合仍条件化)
- **单帧 wall 吃得下 deadline**: 情形 A 0.57ms / 情形 B 0.65ms (R43 用核(a) worst=30 修正后), 均 << 1.333ms 帧周期.
  1.0x deadline 下 **2.06-2.34x** 余量充足. **M2 单帧回调 wall < 1.333ms 成立 (base demand, [L1]
  核+focus + [io-callback 核(a) 预留 ≤30, R42] + [L4] O1).** -> M2 可行性硬门 **PASS (base, 口径无关)**.
- **但这是 T2 的实时版 base demand, 未含争用/未测预留**. 完整 T2 1.5x 闭合须再扣 (H2_PASSLINE:108):
  - M_contention (DMA+ISR 争用, H2 both_max-base [L1]) -- 待 H2 板跑;
  - io_callback_reserve 5-30 [L3] (=核(a) dispatch+descriptor; **M1 的 9.63 是 app 负载(b) 不落此带不能替, R42**; 核(a) 待 M2 dispatch-inclusive 探针坐实);
  - O1_contention_reserve 5-15 [L4] (EQ 上板后);
  - I_cold_reserve 10-30 [L4] (C10 I-cache 符号待).
  通过线 = **210.19 MCPS** (666.67 - 固定侧 456.48, H2_PASSLINE:21). 机械判据:
  `M_contention + 三预留 <= 210.19 <=> worst >= 1.5x`. base demand 486.48 距 666.67 还有
  **180.19 MCPS** 给争用+其余预留 (io_cb 核(a) worst 30 已计入, R43). **base 吃得下, 争用余地宽; 全系统 worst T2
  闭合条件于 H2 板跑 + 三预留 (CTO 设值)**, 本调研不预判板跑结果 (R5 纪律).
- M1_ARCH_REVIEW_R34 ①-1 已独立交叉: 750Hz 额外固定开销 ~0.55 MCPS << 余量 114.59, 750 vs 187.5
  帧率不破预算 (copy work per-sample 率无关, 仅 per-callback 固定开销随率涨). [L3, R34 算]

---

## 5. 开口 / 缺数据 (集中小节)

### 5.1 产品 .map (item 3 pin)
- **产品 build .map 待补** (R34 缺数据#5). pin 决策须基于产品 .map (非 H2 harness .map; proxy
  buffer 是 harness-only). bring-up 须重读确认 s_m2_fa/SPORT buffer 实落块 (Block 1 >=0x2c0000,
  FIRA 离 SPORT). [board-confirm]
- ⚠ **M1 .ldf Block 1 END=0x2ebfff (~176KB), 比 H2/R34 假设的 192KB 小 16KB** (m1_app.ldf:7-9
  R40 MINOR-3). M2 沿用 M1 .ldf 须知此差; 需求 ~24KB 仍放得下. [L1, 已落 §3.3]
- identical-segment vs same-arbitration-class (R26 残留): pin 真隔离争用须 bring-up 核产品 SPORT
  缓冲实落块. [board-confirm]
- 哪个 pin 离哪个 (FIRA vs SPORT buffer) = CTO 裁.

### 5.2 Q31 转换细节 (item 2)
- **M1 int32 (24-in-32) <-> FIRA Q31 左/右对齐**: SPORT DTYPE_SIGN_FILL 31 暗示左对齐 [inferred],
  须核 HRM 确认左/右对齐 + 24-bit 有效位位置. [board-confirm]
- **FIRA INTEGER enum vs ours Q15xQ31 signed-fractional** (fira_tree.h:42-43 R14 临界点):
  Q 格式转换点高 bit-deviation 风险, 须 board bit-by-bit (R14 per-subband 准则). [L1/EZKIT 待板]
- **headroom -4.8dB** (tree_filterbank.h:38) M2 RX->Q31 装填须守, 真值标定 EZKIT [L1].
- TX 侧 [8ch][64] -> [64frame][8slot] 交织布局 (item 1.3). [inferred, M2 实现]

### 5.3 io-callback 真值 (item 4)
- **cb_cyc 9.63 MCPS / 12839 cyc = [board-confirm], 非在档** (派单假设值). 真 cb_cyc 仍 [L3] 待
  SPORT bring-up; M1 g_m1_cb_cyc_last (m1:214) 上板后即 [L1-to-be]. [board-confirm]
- M_contention / O1 争用 / I_cold = H2 板跑 + EQ 上板 + C10 符号待 (H2_PASSLINE §6). [board-confirm]

### 5.4 接入点 / 架构粒度 (item 1, CTO 裁不在本调研收口)
- 逐样本 vs 整帧接法 (FIRA 块处理 -> 整帧 + deinterleave, 重构非替一行). [inferred]
- 波束加权/延迟落哪级 (输入级权 / 子带级 frac-delay / both). [inferred]
- 1ch 落哪物理 ADC 输入脚 (R34 缺数据#2, G-IO2). [board-confirm]
- RX SPORT 窗口 slot 数 (1/4/8, R34 缺数据#1, ②③耦合) -- M1 现锁 1 slot (512B) 带 fallback 2
  (m1:31 M1_RX_SLOTS, board-confirm-CRITICAL G1-G2 驱动 floor). [board-confirm]

---

## 6. 四项摘要 (回报)

1. **接入点**: M1 回调 `m1_sport_rx_callback` :180-221; 精确替换点 = fan-out 复制内层
   (:201 `txf[s8]=sample`), M2 换成「RX 帧 -> FIRA 8ch -> 8 slot 不同加权/延迟」. CCNT bracket
   (:187/:212) 现成做 io-callback 量测点. 冻结 .c 零触碰, 只在 M1 board TU call FIRA. 粒度
   (逐样本 vs 整帧) = CTO 裁.
2. **冻结接口**: M2 call **fira_tree.h** (FiraChannelState, 非 tfb_8ch.h core-only 金标). 序 =
   setup/set_coeffs/channel_init(x8) [init] -> 每帧每 ch analyze->synthesize (H1/H2 同款,
   h2:115-122). 64 样本/帧, 8 ch 独立无跨通道 sum. **格式边界 = M1 int32(24-in-32) <-> FIRA Q31,
   R37/R38 标, M2 owns**; FIRA INTEGER enum vs Q15xQ31 = R14 bit-exact 板核.
3. **pin 落地**: M2 接 FIRA 刻须 pin (FIRA 工作集 vs SPORT buffer 同 Block 0 = R24 自冲突). 方式
   = `#pragma section("seg_l1_block1")` (ADI 例程板证, .ldf 冻结只读). M1 .ldf Block 1 =
   0x2c0000-**0x2ebfff (~176KB, 比 H2 base 小 16KB**, R40 MINOR-3). 需求 ~24KB 放得下. 产品 .map
   待补 (board-confirm).
4. **deadline 核 -- 余量结论 = 吃得下 (base)**: 帧周期 1.3333ms = 1,333,333 cyc @1GHz. M2 单帧
   demand = core 347.45 + focus 49.03 + io-cb 核(a) worst 30 (+O1 60) = 426-486 MCPS = 0.57-0.65ms
   wall, **<< 1.333ms deadline, 1.0x 余量 2.06-2.34x, 吃得下** (R43: 9.63 是 M1 app 负载(b) 非 M2
   io-callback, 已换核(a)预留 30; 结论口径无关稳). base 距 T2 666.67 线还有 ~180 MCPS 给争用+其余
   预留. **全系统 worst T2 1.5x 闭合仍条件于 H2 板跑 + 三预留** (通过线 210.19, 机械判据
   M_contention+三预留<=210.19). io-callback 核(a)[L1] 待 M2 dispatch 探针 (R42).

### board-confirm / 开口清单
- [board-confirm] 产品 build .map (pin 实落块); M1 .ldf Block1 -16KB 差已知.
- [board-confirm] M1 int32 <-> FIRA Q31 左/右对齐 (HRM) + FIRA INTEGER vs Q15xQ31 R14 bit-exact.
- [board-confirm] io-callback 真 cb_cyc (g_m1_cb_cyc_last 上板; 9.63/12839 是假设).
- [board-confirm] M_contention (H2 板跑) / O1 争用 (EQ 上板) / I_cold (C10 符号).
- [board-confirm] RX SPORT 窗口 slot 数 (1/4/8) + 1ch 物理 ADC 脚 (G-IO2).
- [CTO 裁] 接入粒度 (逐样本/整帧)、波束加权落级、哪个 buffer pin 离哪个、O1 EQ 是否进 M2.

---

## HALT -- M2 调研产出, 等 CTO 拍架构, 不写实现.

不预判 CTO M2 架构裁定. 冻结代码零触碰 (本调研只读对照). 不 commit.
reviewer pending: critic gate (三道关 POLICY v1.8 §4B).
dsp-algorithm @ claude-opus-4-8 / 2026-06-08.
