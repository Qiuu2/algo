# STAGE4_TESTER_RUNBOOK — 测试员傻瓜手册（CTO 出门期间代测）

> 给非专家测试员：照步骤烧板、读数字、复制发回。**不需要懂代码，不需要判断对错** ——
> 只要会：CCES 里 git pull / build / load / Run / 在 Debugger 里读全局变量 / 复制数字。
> 任何一步报错或读数异常，原样复制发回，不要自己改。判读由 PM 远程做（见交接节）。
> 工程：algo/master git 仓，CCES 原地 build `m1_cces_project`(=M1_Loopback)。
> 关联：sprint6/STAGE4_BATCH_PLAN.md（计划全景）。维护：PM lead。
> **修订（critic 放行前审计 R51）**：修正符号名 / hwerr 序数判读 / -99 哨兵 / 总线挂死 / 判读表补全 /
> .map 启用 / M2 接线展开 / 对齐 dump 注入已知输入并移到 1A / 跑两遍口径 / 交接渠道。

---

## ⚠ CTO/PM 交付前必须先确认（不是测试员做，是交付前 gate）
- **原理图确认 0x20–0x27 范围内只有 MCP23017 类器件**：地址自探测会对每个应答地址发一个 1 字节 `0x00`
  （对 MCP23017 是「选寄存器」无害；但对该范围内的 PCF857x 类器件，`0x00` 会直接驱动输出脚）。
  确认前不得让非专家跑此 build。若不能确认，先把 sweep 移出 boot 路径（CTO-gated 代码改，本轮未做）。
- 确认 codec_write_rc 在 M1 透传 build 里有效（已核：m1_twi_w8 在 #if M2_FIRA_INLOOP 外，init step 5 跑）。

---

## 准备（一次）
1. CCES 打开 algo/master 工作区，`git pull`（拉到最新，含诊断镜像）。
2. **若工作区里还没有 M1_Loopback 工程**：File → Import 按 `m1_cces_project/M1_CCES_IMPORT_GUIDE.md` 导入，
   含首次构建修正 **F1–F6**（尤其 F3 路径变量 / F6 头文件名漂移）。
3. **启用符号表 .map**（默认没开，不开就没有 .map 可发）：Project Properties → C/C++ Build → Settings →
   Tool Settings → **SHARC Linker** → 勾选 **Generate symbol map**（或加 `-map`）→ 应用 → Rebuild。
   生成后 .map 在 `Debug/` 文件夹里。
3b. **加载哪个文件**：build 产物里 **`Debug/M1_Loopback.dxe`** 是给仿真器/JTAG 调试加载的；
    `.ldr` 是引导镜像，**不要加载 .ldr**。Load `Debug/M1_Loopback.dxe`。
    （若 `Debug/` 下没有 `.dxe`、产物名不同，原样发回，不要猜。）
4. **若 build 报错**：先对照 `M1_CCES_IMPORT_GUIDE.md` 的 **F1–F6** 自查（多半是路径变量/头名），
   还不行就原样复制错误发回，不要猜改。
5. **自由运行纪律**：测量循环里**不要下断点**（会死锁）。流程 = Run → 让它跑几秒 → Suspend → idle 读全局。
   「在 idle」= core 停在 main 的 while(1) 空转循环里，**这是正常的**。

---

## 第 1 次测试 · 诊断（最重要，一次读全）

### 1A — softcfg 诊断 + 对齐 dump（build M1 透传，**不**定义 M2_FIRA_INLOOP）
1. **Build**：默认配置（**不要**加 `M2_FIRA_INLOOP`）。Build M1_Loopback (Debug)。
2. **Load `Debug/M1_Loopback.dxe`** → **Run，跑 ~5 秒，Suspend**。
   - **先确认到了 idle**：Suspend 后看 PC 是否停在 main 的 while(1)；若 `g_m1_main_init_rc` 仍是 **-99**
     且 `g_m1_rx_block_count` 仍是 **0** → 程序没跑到读数点（多半阻塞式 TWI 写把总线挂死了）。
     **此时：记录 PC/调用栈 + 当前所有全局，原样发回，不要反复重烧。**（见下「总线挂死」）
3. **读这些全局，逐个抄数字发回**（Expressions 窗口输入变量名）：
   - **数组怎么读**：输入数组名后展开前面的三角号读 `[0]..[7]`，或逐个输入 `名字[0]`…；**抄元素的值，不要抄数组地址**。

| 变量 | 抄什么 |
|---|---|
| `g_m1_u6_addr_sweep[0]`..`[7]` | 8 个值（index [k] 对应地址 0x20+k；1=应答/0=没应答/**-99=没跑**）|
| `g_m1_codec_write_rc` | 1 个值（注：是**最后一次** codec 写的 rc，见交接节注意）|
| `g_m1_softcfg_hwerr` | 1 个值（**抄原始整数**，PM 按序数解，不要自己解）|
| `g_m1_softcfg_rc[0]`..`[4]` | 5 个值 |
| `g_m1_softcfg_set_rc[0]`..`[2]` | 3 个值 |
| `g_m1_softcfg_open_rc` / `g_m1_softcfg_addr_rc` | 2 个值 |
| `g_m1_main_softcfg_rc` | 1 个值 |
| `g_m1_valid` / `g_m1_fg_stream_live` | 2 个值 |
| `g_m1_rx_block_count` / `g_m1_tx_block_count` | 2 个值 |
| `g_m1_max_abs_sample` | 1 个值 |
| `g_m1_main_pwrinit_rc` / `g_m1_main_init_rc` | 2 个值（**注意是 `g_m1_main_init_rc`，不是 g_m1_init_rc**）|

4. **对齐 dump（在 1A 这里做，不放 1B）**：SPORT 对齐是 M1/M2 build 相同的属性，在容易的 M1 build 就能取。
   - **先给一个已知的、稳定的中等幅度音频输入**（不能静音，否则 dump 全 0 没法判）。
   - 读 `s_m1_rx_buf[0][0]`..`s_m1_rx_buf[0][7]`（**注意是 `s_m1_rx_buf`，2 维 file-static**；
     在 Expressions 里按文件作用域输入，若调试器看不到此 file-static 符号，**原样记「符号不可见」发回**）。
   - 抄这 8 个值发回（PM 判左/右对齐）。**若全是 0 → 注明「无实时输入/未注入」一并发回。**
5. **导出 .map**（准备步骤 3 启用后，在 `Debug/*.map`）——整个文件发回。

### 1B — M2 FIRA（build 加 M2_FIRA_INLOOP=1）—— **不确定就跳过，只做 1A**
> M2 = FIRA 波束。要改 build 接线，**非专家做不了就明确只做 1A，M2 等 CTO 回来或 PM 指导**。
1. **Build 接线**（这几步对没配过 CCES build 的人有坑——逐条按 `M1_CCES_IMPORT_GUIDE.md` 第 121–141 行的点击路径做）：
   - 预处理宏加 `M2_FIRA_INLOOP=1`（Properties → C/C++ Build → Settings → Preprocessor → Defined symbols）；
   - 加 3 个 include 目录：`sprint4/dsp/fira`、`sprint4/dsp/core_only/src`、`sprint4/dsp/core_only/include`；
   - link 3 个源文件（linked resource）：`fira_tree.c` / `tree_filterbank.c` / `tfb_8ch.c`；
   - 编译宏再加 `FIRA_USE_REAL_ADI_FIR_HEADER`。
   - **任一步不确定 → 停，只交 1A，把卡在哪发回。**
2. **Load + Run ~5 秒 + Suspend**，读：

| 变量 | 抄什么 |
|---|---|
| `g_m2_setup_rc` | 1 个值（应=0；**=-99 表示 FIRA setup/link 没跑成**）|
| `g_m2_fg_beam_live` | 1 个值（应=1）|
| `g_m2_out_nonzero` / `g_m2_out_max_abs` | 2 个值（setup_rc=0 但 out_nonzero=0 = 波束静默，记录别盲重跑）|
| `g_m2_valid` | 1 个值 |

3. **导出这个 build 的 .map**——发回（PM 验 FIRA 工作集 pin 到 Block1 ≥0x2c0000）。

### 1C — 交接（发回，到此停）
把 1A（+ 可选 1B）所有数字 + .map 文件，按下面「交接」节发出。**到此停，等回话。** 不要自己改任何东西。

---

## 交接（CTO 出门期间：测试员 → CTO 中转 → PM）
- **PM 是一个 Claude agent，没人调它就不跑**——所以测试员**不直接联系 PM**。
- 测试员把：① 上面所有读数（直接粘文本）② .map 文件（作为附件）**发给 CTO**：
  邮箱 `taricqiu@gmail.com`（或约定的 IM）。
- **CTO 收到后转给 PM 判读**，PM 出下一步 build，CTO 再转回测试员。
- **若 N 小时没回话**：停着等，**不要重烧、不要猜、不要自行改 build**。

---

## PM 判读（**测试员不做这节**，PM 远程做）—— 判读表

> **hwerr 是枚举序数，不是位掩码**（核：ADI_TWI_EVENT 顺序枚举）：
> `g_m1_softcfg_hwerr == 0`→无错 ｜ `==3`→**DNAK**(数据相 NAK) ｜ `==4`→**ANAK**(地址相 NAK) ｜ `==5`→**LOSTARB**(总线仲裁丢失)。
> （`0xFFFFFFFF`/-99 = 那步没跑，见哨兵节。）**用相等判，不要按位解。**
> 注：hwerr 只在第一次写(IODIRA)之后读一次；若 `softcfg_rc[1..4]` 非 0 而 hwerr=0，失败的是后面的写，**以 softcfg_rc 为准**。

**主判据 = (sweep 模式, codec_write_rc)；hwerr 是佐证。hwerr 与主判据矛盾 → ANOMALY，发 PM。**

| sweep 模式 | codec_write_rc | hwerr(序数) | → 根因 | 下一步 build |
|---|---|---|---|---|
| 恰一个=1 **且不是 0x22(=sweep[2])** | 0 | 4=ANAK | **R1a 地址错** | `-DM1_U6_TWI_ADDR_OVERRIDE=0x2X`(那个地址) rebuild |
| 0x22(=sweep[2])=1 其余 0 | 0 | 3=DNAK | R1d 寄存器/BANK | PM 出 block B-d build |
| **全=0** | 0 | 4=ANAK | R1c U6 没上电/缺/复位中 | PM 出 block B-c build |
| 全=0 | **非0** | 5=LOSTARB | **R0 总线级硬件** | ⚠ 需电子工程师拿示波器（非按钮工）|
| **≥2 个=1**（多地址应答）| 任意 | 任意 | **ANOMALY 外来器件** | **不自动 override**，PM re-scope |
| 任一=1 **且 codec_write_rc 非0 / LOSTARB** | 非0 | 5=LOSTARB | **ANOMALY**（应答但总线也坏）| 不自动结论，PM re-scope |

判读注意（PM 侧）：① `codec_write_rc` 是**最后一次** codec 写的 rc——中途瞬时 NACK 可能读回 0；若有 LOSTARB 或 sweep 全 0 等总线征兆，别过信 cwrc=0。② 若 sweep 全 0，下「U6 缺」结论前先看 `g_m1_softcfg_open_rc`==0（sweep 与 enable 共用 TWI 内存；INSUFFICIENT_MEMORY 也会让 sweep 全 0=软件 bug 非板况）。

### 哨兵值（-99 / 0xFFFFFFFF）= 那步没跑（测试员也要懂这条）
- 任何读数 = **-99**（或 hwerr = **0xFFFFFFFF**）= 该步**根本没执行**——**原样记录，不要当成 0**。
- 看 `g_m1_main_softcfg_rc` / `g_m1_main_init_rc` 判哪步中止了，一并发回。

### 总线挂死 / 没跑到 idle
- Suspend 后 PC 不在 main/while(1)，或 `g_m1_main_init_rc` 一直 -99 且 `rx_block_count` 一直 0
  → 多半阻塞式 TWI 写把总线挂住了。**记录 PC/调用栈 + 所有全局发回，不要反复重烧。**

---

## 第 2 次测试 · 验证（PM 指定 build 后）

1. PM 会告诉你**具体 build 配置**（比如「加 `-DM1_U6_TWI_ADDR_OVERRIDE=0x21u` rebuild」）。
2. **Build + Load + Run ~5 秒 + Suspend**，读：
   - `g_m1_softcfg_rc[0]`..`[4]` —— **目标：全 = 0**（5 个写全成功 = F-SRU-1 真生效）
   - `g_m1_u6_addr_sweep` —— 复确认
   - `g_m1_valid` / `g_m1_fg_stream_live` —— 应 1/1
3. 抄数字发回。**rc 全 0 = softcfg 命脉修好。** 否则发回 PM 再判。

---

## 红线（务必遵守）
- **不要自己改代码 / 改寄存器值**——只按 PM 指定的 build 宏 rebuild。
- 测量循环里**不下断点**，只 Run→Suspend→idle 读。
- 读数异常/build 报错：**原样复制发回**，不要猜不要改。
- **跑两遍一致的口径**（别误报）：
  - `rc` / `sweep` / `hwerr` / `set_rc` 这些**快照值**——两次**各自重新 Load/重启后**应一致；
  - `rx_block_count` / `tx_block_count` / `g_m2_out_nonzero` 这些是**累加计数器**，会一直增长——
    **只看它在增长**，**不要要求两次相等**（不重启会越来越大，重启会归零再长，都正常）。

## 文档/路径
- 诊断原理：sprint6/dsp/audio/M1_SOFTCFG_U6_ADDR_SWEEP.md
- 导入 + M2 接线 + F1–F6：sprint6/dsp/audio/m1_cces_project/M1_CCES_IMPORT_GUIDE.md
- 计划全景：sprint6/STAGE4_BATCH_PLAN.md

---
*PM lead。诊断件 b3d7f74(critic R50)。放行前审计 R51 修订（符号名/hwerr 序数/哨兵/总线挂死/判读表/​交接 等）。*
*F-SRU-1 修复 + 板上 rc 全 0 复验前不得宣称换板安全。*
