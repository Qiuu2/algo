# F5 + F7 规划草案（PLANNING DRAFT — 无代码改动）

**日期**：2026-06-04 ｜ **作者**：dsp-algorithm（claude-opus-4-8）｜ **状态**：DRAFT，待 critic 门禁
**挂接**：F4 里程碑（commit 9d9fbec，FIRA 单通道子带 bit-exact L1）/ R14 主门 OPEN / C9·铁律八维持 / POLICY-PROV-001 v1.7 / critic skill §12 / `sprint4/dsp/fira/F4_BITEXACT_HANDOFF.md`
**性质**：本文是规划文档，**仅定义 WHAT/WHERE/HOW 与验收判据，不含任何实现代码改动**。所有判据均按 §12 设计为「依赖滤波系数、不可假绿」。

---

## 0. 范围与不变量（贯穿 F5/F7）

- **C9/铁律八不动**：FIRA 收益（cycle 裕量、是否值得用）一律标 `[L4/待验证]`，**在 CTO 裁定 R14 闭合前不进任何选型/承诺依据**。本文 F7 只规划「如何测」，不预设测出来的结果。
- **8ch 事实基线（dsp 自查、CTO 接受）**：8 通道同构且完全独立；当前 `tfb_8ch.c:54-63` 把 8→1 数字求和（WCET 时代的包裹层，**非产品拓扑**）；CTO 最终拓扑 = 8 路独立输出到 8 个 DAC、声学叠加、**无数字求和**；Dolph-Chebyshev -20dB 的「每路权重表」作为 DSP 代码**尚不存在**（只有共享 hb63 原型 ×2 份）；`fira_tree.c` 零跨通道代码；4 个共享 static（`s_seg_in`/`s_seg_out3`/`s_taskMem`(1)/`s_hFir`）在严格串行纪律下安全。
- **F4 既证不变量（en bloc 坐实，单 chirp 单通道）**：A2/A4/A5/INT/DEC 相位/跨帧历史。F5 换激励、上 8ch 后**须复验**（见各部 [ASSUME]）。
- **顺序与依赖总览**：**F5-C 先**（生成并冻结权重表）→ **F5-A** 的 golden 生成需要权重表 → **F5-A** 上板 PASS 后 → **F7**（含开销 cycle 实测）。**F5-B 与 C/A 解耦可并行**（删求和节点不依赖权重数值，但其新接口定义需与 A 的链路实例化对齐）。

```
          F5-C (权重表生成+冻结+≤1.0验证+L定级)
            │ 权重数值
            ▼
F5-B ──── F5-A (链×8 实例化 + 8 golden + 板上读数)
(独立)      │ 板上 PASS
            ▼
          F7 (含开销 cycle 实测 + 裕量重算)  ← 结果受 C9 管辖
```

---

## 1. F5-A：链 ×8（单通道已验链路的 8 倍实例化）

### 1.1 范围
把 F4 已逐位验证的单通道 fira 链实例化为 8 份：`FiraChannelState[8]`。**无新结构** —— 数据通路、生命周期、postscale、相位修复全部复用 F4 既证逻辑；唯一变化 = 「golden 从 1 条变 8 条，每路系数不同」（每路套用 F5-C 冻结的该通道 Dolph 权重）。

**共享 static 串行纪律（correctness 依据）**：8ch × 9 seg = **72 个串行 QueueTask** 全部跑在同一个 `s_hFir` 上；4 个共享 static 在「单线程严格串行」纪律下复用，**无需任务分组即可保证正确性**（每个 seg 跑完读走结果再发下一个；不存在并发覆盖窗口）。该纪律为 F5-A 的**前置不变量**，必须在 harness 注释中逐字记录，并作为 [ASSUME-A1] 登记（见 1.5）。

### 1.2 权重施加位置（必须二选一并论证 + 标 bit-exact 边界）
**决策：权重施加在「输入级 input-scale」**（每路 analyze 之前对该路输入乘以标量权重 w_c），**不**在输出级。

理由：
1. 与声学模型一致 —— a1_static_weight_numpy.py 的阵因子是 `(weights * exp(jφ)).sum()`，权重乘在每元复幅值（即每路输入端），输入级施加与声学 golden 同源同位，避免「DSP 把权重放输出、声学放输入」造成的语义错位。
2. 线性滤波下 input-scale 与 output-scale 数学等价，但定点截断点不同；input-scale 把权重并入「进 FIRA 前的核侧整数乘」，落在已被 F4 锁定的 `fira_postscale` 截断纪律内，**不新增截断点**。
3. broadside 无延时（delays=0，对称），权重是纯幅值标量；input-scale 让「每路只差一个标量」最清晰，8 golden 之间的差异可追溯到单一标量。

**bit-exact 边界（关键，§12 FG1）**：权重一旦进链路，**golden 必须包含该权重**。即第 c 路的桌面 golden = 「该路输入 × w_c → analyze/synthesize（含 postscale）」的逐位结果。判据是「FIRA 子带 == 核子带（含权重）」逐位相等，**不是**「不含权重的 hb63 golden」。权重的定点表示（Q 格式、乘法对齐、截断 shift）必须与桌面 golden 生成端**同源同算**，否则 off-by-2^k → CRC 失配（这是判据依赖滤波系数的体现，非假绿）。

> [ASSUME-A2]：input-scale 的权重定点乘对齐沿用 F4 既证的 `fira_postscale` 截断纪律，不新增第二截断点。F5-A 上板逐位验证；若 bit-by-bit 显示需要独立的权重 shift，配对调整 postscale（同 DP-01 纪律，桌面不裁、板上裁）。

### 1.3 8 路桌面 golden 生成（扩展 sbgold/gen_golden 方法）
- 复用 F4 已证的桌面 golden 生成路径（`sbgold` 子带核算法，与板上自检门 `g_f4_crc_core==0x2E0D8C6E` 同源）。
- **逐路生成**：对 c=0..7，取 F5-C 冻结表的 w_c，喂同一冻结 chirp 激励 × w_c，跑核子带算法 → 得该路子带 golden（CRC + 32 点 dump + 四带 probe 首样本）。
- 产出 8 组 golden 常量（建议 `g_f5_golden_crc[8]` / `g_f5_golden_dump[8][32]` / `g_f5_golden_probe[8][4]`），provenance 注释块标注：源激励、源权重表版本（F5-C 冻结 commit）、生成脚本、算法 = sbgold 子带。
- **去重检查（按默认映射 = 全相异断言）**：在本规划默认映射「8 路 = 8 对对称元」下，每路驱动一对对称元 {元 c, 元 15-c}，该路权重 = 该对的单一 Dolph 幅值；16 元 Dolph 表关于中心对称（w_元c == w_元(15-c)），故 8 路取到的是**半孔径的 8 个互不相同的 Dolph 值**（从边缘最小到中心最大单调，无重复）。因此正确断言 = **「8 条 golden 两两互不相同（全相异）」**；任何两条相等 ⇒ 权重未真正区分通道 / 权重表退化 / 权重没接进链路 → FG1 假绿，FAIL。
  - 注意：这里**不是**「镜像对相等」—— 镜像相等发生在 16 元层面（元 c 与元 15-c），而 8 路每路已把一对对称元合并为单一路权重，故 8 路层面无镜像重复。先前草稿「8 条可能有合法重复」的表述在默认映射下不成立，已更正为全相异。
  - 若 OPEN-A1 最终改判为「8 路 = 8 单元（只用 8 元，非对称对）」，则映射与维度变更，去重断言须按新映射重新推导（仍以「权重真正区分通道」为 FG1 不变内核）。该断言的具体形式锚定 OPEN-A1 决议（见 §5）。

### 1.4 板上读数方案（per-channel 全局）
逐通道独立 pass/crc/mismatch 全局，禁止「任一路绿即整体绿」的聚合掩盖：
- `g_f5_pass[8]`（每路 0/1）
- `g_f5_crc[8]`（每路 FIRA 子带 CRC，板上比 `g_f5_golden_crc[c]`）
- `g_f5_mismatch_idx[8]` / `g_f5_mismatch_sb[8]`（每路首失配点 + 子带，默认 -1）
- `g_f5_dump_fira[8][32]` / 复用 golden 侧 dump 做逐位 0 差核对（sharp falsifier ×8）
- 整体门 = `AND(g_f5_pass[0..7])`，但**任一路 FAIL 必须能从 per-channel 全局定位到「哪一路、哪子带、哪点」**（§12 IO/FG：失败必须可定位，不可只给一个聚合 bool）。

### 1.5 [ASSUME] 登记
- [ASSUME-A1] 72 串行 QueueTask 单线程纪律成立、4 共享 static 无并发覆盖窗口 —— F5-A 上板由「8 路逐位相等」整体坐实；若引入任务分组/并发则失效，须改 per-task scratch（F4 handoff §6 已挂「单线程 scratch」为 F5 开放项）。
- [ASSUME-A2] 见 1.2（权重定点对齐沿用 postscale 纪律）。
- [ASSUME-A3] 换 ×8 后仍用单一冻结 chirp；F5 后续若换激励须复验（同 F4 §6）。

### 1.6 C7 顺手清理（CTO：顺手清掉）
`fira_regression.c` 的过期 header banner —— 第 ~12 行与第 ~33 行写的判据是「crc==0x90556BC7（端到端 e2e golden）→ R14 PASS」，该 e2e 判据**已被 R14 子带粒度判据取代**（DEC-S4-R14-GRANULARITY；真判据 = 子带 `0x2E0D8C6E`，见 F4 §2）。在 F5-A 编辑 harness 时**顺手改正**这两处 banner 为子带判据，并指明「e2e telescoping 恒等盲区已由子带级判据替代」。**注意**：0x2E0D8C6E 是 F4 单通道单一权重（实为 hb63 等增益）的子带 golden CRC；F5 是**每路不同权重的 8 条 golden**，banner 改正应表述为「判据 = per-channel 子带 CRC 逐位（不再是单一 e2e 常量）」，不要把 0x2E0D8C6E 误写成 8ch 的统一判据。
- **C7 传播完备性 AC（critic Fix-2，随 F5-A harness 编辑落地）**：banner 改正时**全树 grep `0x90556BC7`**，逐处确认残留要么是合法 e2e 自检（`fira_harness_selfcheck` / `g_bench_result.crc32` 端到端检查），要么带「已退役 R14 判据」注记——不留半改正引用（铁律五/C7）。

### 1.7 验收判据（依赖滤波、按设计不可假绿）
- AC-A1：板上 `AND(g_f5_pass[0..7])==1` 且每路 `g_f5_crc[c]==g_f5_golden_crc[c]` 逐位、`g_f5_dump_fira[c]==golden_dump[c]` 32 点 0 差。
- AC-A2（FG1 防假绿）：8 条 golden 满足去重断言（默认映射 = **8 条全相异**，见 1.3；若 OPEN-A1 改判则按新映射重导）；占位/未接权重版本桌面必须 FAIL（沿用 F4「占位版桌面证 FAIL」的双防 FG1/FG2）。
- AC-A3（FG2 防占位）：harness 在桌面（无 FIRA 硬件）`return 0`=FAIL、绝不假绿（沿用 fira_regression.c 桌面安全纪律）。
- L 定级：板上结果 = `[L1/EZKIT]`；桌面 golden 与去重证明 = `[L2]`。

---

## 2. F5-B：删求和 wrapper（按新结构审，非清理）

### 2.1 范围与性质
移除 `tfb_8ch.c` 的 8-in-1-out 求和节点（`w_add_i32` 累加到 `acc0..3` 再单路 synthesize，行 44-63）。**这改变模块接口与 golden 定义** —— 不是删几行，是**结构变更**：原拓扑 = broadside DAS 数字求和单输出；新拓扑 = 8 路独立、各自 synthesize、8 路独立输出。**critic 须按结构变更审（接口契约 + golden 重定义 + 拓扑风险），不按行删除审。**

### 2.2 新接口（二选一并论证）
**决策：以「8× 单通道调用」替换 `tfb8_process` 的求和体**，新接口 = 8-in-8-out 独立：

```
旧： tfb8_process(st, in[8][FRAME], frame, int32_t *out)        // 1 路 out
新： tfb8_process(st, in[8][FRAME], frame, int32_t out[8][FRAME]) // 8 路 out, 每路独立 synthesize
     // 内部 = for c in 0..7: analyze(in[c]) → (无 acc 求和) → synthesize(&st->syn[c], out[c])
     // st->syn 由单实例扩为 syn[8]（每路独立合成状态）
```

理由：
1. 保「单通道链」为最小已验单元 —— 直接 8× 复用 F4 既证链，不引入新的求和/钳位语义；删掉的恰好是「非产品拓扑」的求和。
2. 8-in-8-out 与 CTO 最终拓扑（8 DAC、声学叠加）**一一对应**，接口即拓扑，无需后续再改。
3. 删 `w_add_i32` 与 `acc*` 缓冲后，**无数字求和路径** → GAP-SAT 不再有触发点（见 2.3）。

**与 F5-A 的对齐**：F5-A 的 `FiraChannelState[8]` 与 F5-B 的 8-in-8-out 是同一拓扑的两面（A 管 FIRA 链实例化与 golden，B 管核侧包裹层接口）。两者接口签名须一致；建议 F5-B 的新签名作为 F5-A 链实例化的核侧对照基准。

### 2.3 GAP-SAT 闭合登记（closed-by-topology）
求和节点删除后，正式记入风险登记簿：

> **GAP-SAT 闭合（closed-by-topology）**：本拓扑无数字求和路径，饱和加（`sat_add_i32`/`w_add_i32`）不存在 → GAP-SAT（求和饱和路径未被 F4 单 chirp 激励覆盖）**不触发**。
> **证据链**：① 8ch 事实自查（CTO 接受）—— 8 路完全独立、无跨通道求和；② F5-B 删除 `tfb_8ch.c:14-24`（`w_add_i32`）+ 行 44-63 的 `acc*` 累加；③ 新接口 8-in-8-out 无任何 int32 相加节点。
> **残留前提（必须验证、非假设）**：闭合成立的前提 = 单路链路内部不产生溢出，即**所有权重 ≤ 1.0**（权重 >1.0 会放大单路样本逼近 INT32 边界，重新引入单路饱和风险）。该前提**由 F5-C 显式验证**（见 §3.4），**F5-B 不得假设、只登记依赖**。若 F5-C 验出任一权重 >1.0 → GAP-SAT 闭合作废，回到「需覆盖饱和路径」。

### 2.4 golden 重定义
旧 golden = 单路求和输出的 CRC；新 golden = 8 路独立输出，**每路独立 CRC**（与 F5-A 的 8 golden 一致 —— 实为同一套）。F5-B 的核侧验证复用 F5-A 的 per-channel golden，不再有「求和后单路 golden」。

### 2.5 [ASSUME] 与验收
- [ASSUME-B1] CTO 最终拓扑 = 8 DAC 声学叠加、无数字求和（CTO 已确认，记此处供 critic 复核拓扑前提）。
- [ASSUME-B2] `st->syn` 扩为 `syn[8]` 后每路合成状态独立、无共享跨帧历史串扰（8 路同构独立，复用 F4 单路 synthesize 既证逻辑；上板由 per-channel 逐位坐实）。
- AC-B1：新接口编译通过（核侧 desktop 可编），8-in-8-out 签名落地，`w_add_i32`/`acc*` 完全移除（grep 证无 int32 求和节点残留）。
- AC-B2：GAP-SAT 闭合登记入风险簿，残留前提显式指向 F5-C，**不标 closed 直到 F5-C 验证 ≤1.0 通过**（在此之前标 `pending-on-F5C`）。
- AC-B3（结构审）：critic 确认这是接口+golden 重定义，按结构变更复核（拓扑前提、契约、无求和证据）。
- L 定级：接口/拓扑变更 = `[L0→L1]`（桌面编译 L0，板上 F5-A 逐位 L1 一并坐实）。

---

## 3. F5-C：生成并冻结 8 路 Dolph-Chebyshev -20dB 权重表（F5 真命门）

### 3.1 范围
生成 broadside 的 8 路幅值权重表并冻结为 DSP 代码常量。**broadside → delays = 0（对称阵，无相位项），只有幅值权重**。这是 F5 的独立验证项 —— 与 bit-exact 是**两个维度**（见 3.5）。

### 3.2 双轨生成（铁律七）
- **声学侧生成（主算）**：`scipy.signal.windows.chebwin(N, sll_db)` 归一化 max=1，sll=20（-20dB）。与已三轨验证的 `sprint3/audit/a1_static_weight_numpy.py`（`w_dolph(20)`）**同源同算**，复用其阵因子定义。这是权重数值的来源。
- **DSP 侧独立验证（第二工具）**：用**独立工具**（建议 numpy 直接实现 Dolph-Chebyshev 递推，或 Octave/MATLAB `chebwin`，**不复用 scipy 的同一调用**）独立算一遍 16 元 -20dB 系数，与声学侧逐元比对（容差 = 浮点 eps 级，定点化前）。两轨一致才进冻结。
  - MATLAB 通道可用（本环境有 matlab MCP）：`chebwin(16,20)` 作第二工具。
- **元↔路映射**：16 元 Dolph 表如何映射到 8 路，取决于 F5-A/B 的「8 路 = 8 元 还是 8 路 = 8 对(16 元)」拓扑 —— 见 §5 OPEN-A1（命门，须先定）。**默认映射（8 路 = 8 对对称元）下，权重表 = 半孔径 8 个相异 Dolph 值**（16 元表关于中心对称，每对取单值，路 c → 对 {元 c, 元 15-c}）；冻结表维度 = 8 项（`g_dolph_w_q31[8]`）。若改判 8 单元则维度/取值随之变（见 OPEN-A1）。

### 3.3 冻结格式（C header，仿 fir_coeffs）
仿 `fir_coeffs_q31.h` 的格式冻结：
- 文件建议 `sprint4/dsp/.../dolph_weights_q31.h`（或并入核侧），`static const int32_t g_dolph_w_q31[8]`（或 `[16]`，按映射定）。
- **provenance 注释块**（强制）：源 = chebwin(N,20) 归一 max=1；定点格式（Q 格式 + 截断纪律，与 F5-A input-scale 对齐）；双轨工具名 + 逐元一致证明；冻结 commit；服务的指向性目标 = JY/T 标准表 9 指向性（与 a1/m1 同基线）。
- **Same-source 纪律**（仿 hb63）：值从冻结浮点表定点化而来，板上**不重算**。

### 3.4 全权重 ≤ 1.0 显式验证（GAP-SAT 前提，VERIFY 不 ASSUME）
- chebwin 归一化 max=1 → **理论上**所有权重 ∈ (0, 1]。但这是 GAP-SAT 闭合的前提，**必须显式验证、落证、不得假设**：
  - 验证 = 双轨浮点表的 `max(abs(w)) <= 1.0` 断言（两轨都查）+ 定点化后 `max(abs(w_q31)) <= (1<<Q)` 断言（定点容器不溢出 + 不达 1.0 边界放大）。
  - 产出明确记录：「全 8（或16）权重 ≤1.0，max=1.0（中心元），定点后 max=0x____」，作为 §2.3 GAP-SAT 残留前提的闭合证据。
- 若任一 >1.0（理论不应发生，但归一化方式错/定点 round-up 可能触发）→ **报 critic，GAP-SAT 闭合作废**。

### 3.5 验证框架：「算的目标对不对」（独立维度 + 独立门）
F5-C 验的是「**算的目标对不对**」（指向性目标是否正确）—— 与 bit-exact「**算得对不对**」（F5-A 逐位）是**两个维度**，各自独立验收：
- **bit-exact（F5-A）**：定点 == 桌面 golden 逐位。
- **目标正确性（F5-C 本门）**：用冻结权重算出的**波束图** vs 声学基线对得上。
  - 验证 = 桌面 beam-pattern 检查：用冻结的 8 路权重重算阵因子（同 a1_static_weight_numpy.py 的 `af_complex`），核对关键指标对上 `sprint3/audit` 的 m1/m3 numpy 资产（`m1_numpy_d55_sll_wng_di.csv` 的 SLL/WNG/DI、`m3_numpy_8pair_equiv.csv` 的 8 对等效）—— 特别是 SLL ≈ -20dB、BW@1k ≤30°（红线）、与 a1 基线 Dolph-20 行一致。
  - 这是**仿真维度**（[L2-numpy]），非实测；标 PF-6（isotropic 高频宽角偏乐观）。

### 3.6 L 定级目标
- 权重数值（双轨浮点）= `[L2-numpy]`（声学主算 + 第二工具交叉验证）。
- 定点冻结表 = `[L2]`（桌面定点化 + ≤1.0 验证 + same-source 纪律）。
- 波束图目标核对 = `[L2-numpy]`（vs m1/m3 基线，仿真非实测）。
- 上板生效 = 经 F5-A 的 input-scale `[L1/EZKIT]` 一并坐实「这张表被逐位正确施加」。

### 3.7 [ASSUME] 与验收
- [ASSUME-C1] sll=20 即产品锁定的 Dolph-20 基线（DEC-S3-GEOM-01 / a1 基线）；若 PRD 后续改 SLL 则表重生成。
- AC-C1（双轨）：声学侧 chebwin 与 DSP 侧第二工具逐元一致（浮点 eps 级），落证。
- AC-C2（≤1.0）：全权重显式 ≤1.0 验证通过、落证（喂给 §2.3 GAP-SAT 闭合）。
- AC-C3（目标）：冻结表波束图 vs m1/m3 基线关键指标对上（SLL≈-20dB、BW@1k≤30°），独立于 bit-exact 的单独门。
- AC-C4（冻结）：C header + provenance 块 + same-source 纪律完整，板上不重算。

---

## 4. F7：含开销 cycle 实测 + 裕量重算（与 A/B 并行，但板测在 F5-A 之后）

### 4.1 范围
测量**真实 8ch × 9seg 串行 FIRA 路径**的含开销 cycle，重算裕量。**当前纯核裕量 ~1.3×，判据 ≥10×**。F7 **只规划如何测**，不预设 FIRA 能不能达标（C9）。

### 4.2 测什么（含开销，非纯核）
- **每 seg QueueTask 开销**：包含 CreateTask / FixedPointEnable(SIGNED) / spin-wait 的完整 per-segment 编排开销（这是 FIRA 相对纯核多出来的部分，纯核 MAC 之外）。
- **整帧 8ch wall cycles**：用既有 `bench_cyc_target` 的 CCNT（cycle count）量 8 通道 × 9 段全链一帧的墙钟 cycle（含 72 次 QueueTask 编排）。
- 分解上报：纯 FIRA-MAC cycle / 编排开销 cycle / 总 wall cycle，避免「只报总数」掩盖开销占比。

### 4.3 对比基线与裕量公式
- **对比基线 = 纯核 1,006,935 cyc** `[L1/EZKIT，出处 decisions_log DEC-S4-R1-8CH-01（cyc_8ch_frame 板上实测，F0 基线）]`（critic Fix-3：C1 来源标注落在使用点）。注：该值按 1GHz 计裕量 1.32×，CCLK 真值待实测——F7 实测时一并确认 CCLK（G6），裕量按实测 CCLK 计。
- **裕量公式**：`margin = cycle_budget_per_frame / wall_cycle_8ch_fira`，其中 cycle_budget = SHARC 时钟 × 帧周期（按 fs/frame 算可用预算）。判据 `margin >= 10×`。
- 同时报 FIRA-vs-核比值（`wall_cycle_8ch_fira / 1006935`）供 C9 决策参考，**但该比值标 [L4/待验证]、不进选型**。

### 4.4 C9 纪律（强制）
- F7 测出的数字是 **R14-gated**：它们回答的是「**值不值得用**」（FIRA offload 是否带来足够裕量），服务 CTO 的 C9 裁定。
- **在 CTO 裁定 R14 闭合前，这些数字不得进任何选型/承诺依据**（铁律八）。本规划只定义测量方法与公式，**不预设结果、不主张任何 FIRA 收益数字**。
- 标注：F7 结果一律 `[L4/待验证]` 直到 R14 闭合 + CTO 裁定。

### 4.5 [ASSUME] 与验收
- [ASSUME-F1] 72 串行 QueueTask 编排是 F5-A 实际跑的拓扑（与 A 一致），F7 测的就是该真实路径（非简化模型）。
- [ASSUME-F2] CCNT 测量点位与 bench_cyc_target 既有约定一致（量的是同一段 wall）。
- AC-F1：报含开销分解（MAC / 编排 / 总 wall）+ 裕量值 + 公式 + 预算来源，全部 `[L1/EZKIT]` 板测（cycle）/ `[L4/待验证]` 结论（值不值得）。
- AC-F2（C9）：所有 FIRA 收益结论标 [L4]、显式声明「不进选型直到 R14 闭合」。
- **依赖**：F7 板测须在 F5-A 上板 PASS 后（要测的就是 8ch 链路本身）。

---

## 5. 待定项（OPEN，须在对应部开工前定）

- **OPEN-A1（命门，跨 A/B/C）：8 路 ↔ 16 元映射**。16 元阵 + Dolph-16 权重，但「8ch」—— 是 8 路各驱 1 元（只用 8 元？）还是 8 路各驱一对对称元（8 路 ×2 = 16 元，A/B 对称串联，对应 CLAUDE.md「8 路 A/B 对称串联」）？这决定：F5-C 权重表是 8 还是 16 项、F5-A 的 8 golden 去重断言、F5-B 的 out[8] 语义。**CLAUDE.md 基线写「8 路 A/B 对称串联」→ 倾向 8 路各对应一对对称元**，但须 CTO/声学确认后才能定权重表维度。**本规划默认走「8 路 = 8 对对称元」，待确认。**
- OPEN-A2：input-scale 权重的 Q 格式与 postscale 配对的最终 shift —— 桌面不裁，F5-A 板上 bit-by-bit 定（[ASSUME-A2]）。
- OPEN-B1：`st->syn[8]` 内存增量是否触发 scratch/缓冲上限 —— F5-B 编译期核对。

---

## 6. §12 / C1-C10 自检小结（供 critic 对照）

- **FG1（假绿）**：A 的去重断言 + 占位桌面 FAIL；C 的双轨 + ≤1.0 显式验证 + 波束图目标门 —— 判据均依赖滤波系数/权重，不接权重则 FAIL。
- **FG2（占位）**：harness 桌面无 FIRA `return 0`=FAIL，绝不假绿（沿用 F4）。
- **IO1/IO2**：per-channel 失配可定位（哪路/哪子带/哪点），不只给聚合 bool。
- **ST1**：8 路 synthesize 跨帧历史独立性（[ASSUME-B2]），板上逐位坐实。
- **C9/铁律八**：F7 收益 [L4]、不进选型，贯穿全文。
- **C6（几何 LOCKED 需 L1）**：F5-C 权重服务 d=55 锁定基线，目标核对 vs m1/m3 [L2]，上板 [L1]。
- **铁律七（双轨）**：F5-C 声学 + DSP 第二工具独立验证。

---

*F5+F7 PLANNING DRAFT — dsp-algorithm @ claude-opus-4-8 / 2026-06-04 — 待 critic 门禁，无代码改动*
