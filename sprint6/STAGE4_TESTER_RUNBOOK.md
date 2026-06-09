# STAGE4_TESTER_RUNBOOK — 测试员傻瓜手册（CTO 出门期间代测）

> 给非专家测试员：照步骤烧板、读数字、复制发回。**不需要懂代码，不需要判断对错** ——
> 只要会：CCES 里 git pull / build / load / Run / 在 Debugger 里读全局变量 / 复制数字。
> 任何一步报错或读数异常，原样复制发回，不要自己改。PM(claude) 远程判 + 指定下一步。
> 工程：algo/master git 仓，CCES 原地 build `m1_cces_project`(=M1_Loopback)。
> 关联：sprint6/STAGE4_BATCH_PLAN.md（计划全景）。维护：PM lead，2026-06-09。

---

## 准备（一次）
1. CCES 打开 algo/master 工作区，`git pull`（拉到最新，含诊断镜像）。
2. 确认能：build、Load .dxe 到 EZKIT、Run、Suspend、在 Expressions/Memory 窗口按变量名读全局。
3. **自由运行纪律**：测量循环里**不要下断点**（会死锁）。流程 = Run → 让它跑几秒 → Suspend → 在 idle 读全局。

---

## 第 1 次测试 · 诊断（最重要，一次读全）

### 1A — softcfg 诊断（build M1 透传，不定义 M2_FIRA_INLOOP）
1. **Build**：默认配置（**不要**加 `M2_FIRA_INLOOP`）。Build M1_Loopback (Debug)。
2. **Load + Run**，跑 ~5 秒，**Suspend**。
3. **读这些全局，逐个抄数字发回**（Expressions 窗口输入变量名）：

| 变量 | 抄什么 |
|---|---|
| `g_m1_u6_addr_sweep[0]`..`[7]` | 8 个值（对应地址 0x20..0x27，1=应答/0=没应答）|
| `g_m1_codec_write_rc` | 1 个值 |
| `g_m1_softcfg_hwerr` | 1 个值 |
| `g_m1_softcfg_rc[0]`..`[4]` | 5 个值 |
| `g_m1_softcfg_set_rc[0]`..`[2]` | 3 个值 |
| `g_m1_softcfg_open_rc` / `g_m1_softcfg_addr_rc` | 2 个值 |
| `g_m1_main_softcfg_rc` | 1 个值 |
| `g_m1_valid` / `g_m1_fg_stream_live` | 2 个值 |
| `g_m1_rx_block_count` / `g_m1_tx_block_count` | 2 个值 |
| `g_m1_max_abs_sample` | 1 个值 |
| `g_m1_main_pwrinit_rc` / `g_m1_init_rc` | 2 个值 |

4. **导出 .map 文件**（Build 产物里的 `*.map`）——整个文件发回（PM 验 buffer 放置）。

### 1B — M2 FIRA（build 加 M2_FIRA_INLOOP=1）
> M2 = FIRA 波束。要额外 build 接线，**若嫌麻烦可先只做 1A，M2 等 PM 说**。
1. **Build 接线**（Project Properties → 预处理宏加 `M2_FIRA_INLOOP=1`；加 sprint4 include 目录；link `fira_tree.c` / `tree_filterbank.c` / `tfb_8ch.c`；加 `FIRA_USE_REAL_ADI_FIR_HEADER`）。详见 m1_cces_project/M1_CCES_IMPORT_GUIDE.md 的 M2 接线节。
2. **Load + Run ~5 秒 + Suspend**，读：

| 变量 | 抄什么 |
|---|---|
| `g_m2_setup_rc` | 1 个值（应=0）|
| `g_m2_fg_beam_live` | 1 个值（应=1）|
| `g_m2_out_nonzero` / `g_m2_out_max_abs` | 2 个值 |
| `g_m2_valid` | 1 个值 |
| `g_m1_rx_buf[0]`..`[7]` | 8 个值（对齐 dump，PM 判左/右对齐）|

3. **导出这个 build 的 .map**——发回（PM 验 FIRA 工作集 pin 到 Block1 ≥0x2c0000）。

### 1C — 发回
把 1A + 1B 所有数字 + 两个 .map 文件，一起发给 PM。**到此停，等 PM 回话。** 不要自己改任何东西。

---

## PM 判读（你不用做，PM 远程做）—— 供参考的判读表

| g_m1_u6_addr_sweep | g_m1_codec_write_rc | g_m1_softcfg_hwerr | → 根因 | PM 给的下一步 build |
|---|---|---|---|---|
| 恰一个=1 | 0 | ANAK 位 | U6 地址错 | `-DM1_U6_TWI_ADDR_OVERRIDE=0x2X`(那个地址) rebuild |
| 0x22 位=1 | 0 | DNAK 位 | 寄存器/BANK | PM 出 block B-d build |
| 全=0 | 0 | — | U6 没上电/缺 | PM 出 block B-c build |
| 全=0 | 非0 / LOSTARB | LOSTARB | 总线级硬件 | ⚠ 需电子工程师拿示波器（非按钮工）|

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
- 跑两遍数字应一致（差 <0.1%）；不一致发回 PM。

## 文档/路径
- 诊断原理：sprint6/dsp/audio/M1_SOFTCFG_U6_ADDR_SWEEP.md
- M2 接线：sprint6/dsp/audio/m1_cces_project/M1_CCES_IMPORT_GUIDE.md（M2 节）
- 计划全景：sprint6/STAGE4_BATCH_PLAN.md

---
*生成 2026-06-09，PM lead。诊断件 b3d7f74(critic R50 PASS)。F-SRU-1 修复+rc 全 0 复验前不得宣称换板安全。*
