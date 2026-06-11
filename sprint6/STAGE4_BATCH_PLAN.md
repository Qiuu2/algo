# STAGE4_BATCH_PLAN — 第 4 阶段批量收尾计划（CTO 出门期间，非专家远程测）

> 缘起 2026-06-09：CTO 出门，无法频繁测板，由他人代测。目标：把「跑一次测一个指标」的
> 迭代，压成「攒好批量包 → 别人按手册跑 ~2 次 → 数据发回 → 远程判+指定 build」。
> 本文 = 共享参考（CTO + 测试员 + dsp/critic）。维护：PM lead。

---

## 0. 现在精确位置
```
阶段4 实时音频通路
  ├ M1 透传      board PASS；softcfg 线 R55 收口（板=AD-EXKIT 硬连线使能，F-SRU-1 不适用，DEC-S6-FSRU1-RESCOPE-01）
  ├ M2 FIRA 入环 实现过门(12a5920, broadside v1)，未上板
  └ M3 可听 demo  待 M2 + 阵列硬件(Stage 5)
```

## 1. 剩余工作 × 整合可行性（客观分类）

| # | 工作 | 阶段 | 能否进「批量包+远程测」 | 理由 |
|---|---|---|---|---|
| A | softcfg F-SRU-1 根因+修+验 | 4 | ⚠ 部分（~2 次机械测）| 修法须先读 1 次判别式；R0 总线级需硬件人 |
| B | M2 FIRA 上板（.map pin/对齐/g_m2_*/bit-exact）| 4 | ✅ 可整合（读数=数字）| 对齐两版可预建 |
| C | O1 EQ 上板 MCPS | 4 | ✅ 可整合（独立 build，另跑）| 桌面已过门；band 待 R3 |
| D | H2R ISR 重测 | 3尾 | ✅ 可整合（bench 工程，另跑）| T2 已保守闭合，非阻塞 |
| E | M3 可听 demo | 4 | ❌ 不可 | 需阵列硬件+人耳 |
| F | 线③ 厂家数据 | — | ❌ 不可 | 外部回函 |
| G | 限幅器绝对阈值 | 4/5 | ❌ 不可 | 卡线③ Xmax/热额定 |
| H | Stage 5 硬件（转接板/功放/电源/装配）| 5 | ❌ 不可 | 采购+物理装配，外部串行 |
| I | R3 消声室 | 6 | ❌ 不可 | 外租+需 Stage5 硬件；背疗效/验收/≥90dB |
| J | Stage 7 产品化 | 7 | ❌ 不可 | 远期外部串行 |

**本批量包覆盖 = A+B（同一 m1_cces_project 音频工程，一次 campaign）。**
C/D 是独立工程（O1 待集成、H2R 在 bench 工程）→ 可作**附加独立跑**，不混进 A+B 主 campaign。
E 往后全部卡硬件/外部，整合不进远程软件测试模型。

## 2. 批量包内容（A+B，m1_cces_project）

### 诊断镜像（一次烧、一次读全 → 一次定 root-cause 方向）
- **softcfg（A）**：
  - `g_m1_codec_write_rc`（R1 U6-specific vs R0 总线级 判别式）
  - `g_m1_softcfg_hwerr`（ANAK 地址相 / DNAK 数据相 / LOSTARB 总线级）
  - `g_m1_softcfg_set_rc[3]`（三个 Set 时钟配置成功否）
  - **`g_m1_u6_addr_sweep[8]`（NEW · U6 地址自探测 0x20-0x27 哪个 ACK）** ← 若地址错，这一跑直接找到对的；全不 ACK→U6 缺/上电/总线级
- **M2（B）**：`g_m2_setup_rc/fg_beam_live/out_nonzero` + .map（pin ≥0x2c0000 验）
- **对齐 dump（R51：移到 1A 做，注入已知中等幅度输入）**：`s_m1_rx_buf[0][0..7]`（2D file-static，非 g_m1_rx_buf）；SPORT 对齐 M1/M2 build 相同，在易测的 M1 build 取即可

### 自探测判读【R55 存史：1A 实测=恰一 ACK@0x21+cwrc0+hwerr4，但真因=载板架构不匹配（0x21 是 SOM 系统扩展器 U13），R1a 行已被推翻——见 M1_SOFTCFG_BOARD_RESCOPE.md】
> **hwerr=枚举序数非位掩码**（R51 audit）：0=none/3=DNAK/4=ANAK/5=LOSTARB，**相等判**。主判据=(sweep,codec_write_rc)，hwerr 佐证；矛盾→ANOMALY。完整判读表见 M1_SOFTCFG_U6_ADDR_SWEEP.md §3 / runbook PM 节。

| u6_addr_sweep | codec_write_rc | hwerr | → 结论 |
|---|---|---|---|
| 恰一个 ACK **且非 0x22** | 0（codec 好）| 4=ANAK | **R1a 地址错** → M1_U6_TWI_ADDR 设成那个地址（改一宏，CTO-gated）|
| 0x22 ACK 其余 0 | 0 | 3=DNAK | **R1d BANK/寄存器** → block B-d（CTO-gated）|
| 全不 ACK | 0（codec 好）| 4=ANAK | **R1c U6 缺/未上电/复位中** → block B-c 上电时序（先确认 open_rc==0 排除软件 buf bug）|
| 全不 ACK | 也 NACK | 5=LOSTARB | **R0 总线级**（pull-up/SCL/物理）→ ⚠ 需示波器+电子工程师 |
| **≥2 个 ACK** | 任意 | 任意 | **ANOMALY 外来器件** → 不自动 override，re-scope |
| 任一 ACK 且 codec NACK/LOSTARB | 非0 | 5=LOSTARB | **ANOMALY**（应答但总线坏）→ 不自动结论 |

### 预建修法（决策树，按上表选；除 R0 全是改代码）
- R1a：M1_U6_TWI_ADDR ← sweep 命中地址（一宏，预建可配）
- R1c：写 U6 前加 U6 ready 等待
- R1d：BANK 模式修
- R0：硬件诊断（非代码，安排人）

## 3. 测试节奏（非专家按 runbook）
| 次 | 做什么 | 产出 |
|---|---|---|
| 1 诊断 | 烧诊断镜像，读 ~20 全局 + dump rx_buf + 导出 .map，发 PM | root-cause 方向定 + M2 状态曝光 |
| （PM 远程判 + 从预建指定修 build）| | |
| 2 验证 | ~~套指定 build，读 softcfg_rc 全 0~~〔R55 已取消：本板 rc=11×5 永久预期，判据已替换，见 DEC-S6-FSRU1-RESCOPE-01〕；剩余=对齐 dump/.map + 1B M2 绿 | A 已收口；B 待 1B |

## 4. 诚实风险（攒不进去的硬钉子）
1. **softcfg 若 R0 总线级** → 需示波器+电子工程师（按钮工搞不定）；但诊断第 1 次会明确告诉是这种，好安排人。
2. **M3 可听 / R3 / Stage5-7** → 卡阵列硬件实物+外部，根本进不了远程软件测试，是另一条线（CTO 回来 + 硬件团队 + 外部排期）。

## 4B. CTO-gated 代码 defer 清单（R52 上板前审计发现，本轮只做文档兜底，待 CTO 代码窗口逐项拍）
| # | 项 | 风险 | 文档兜底（已做）|
|---|---|---|---|
| 1 | **CMAP12=0x01 实把 ADC ch2 送进唯一捕获 slot**（注释写反；改 0x10/0x00 需重验）| 单声道插头→全 0 误判 | runbook 1A 要求立体声源 |
| 2 | fg_beam_live 无逐帧 FIRA 失败 gating（fira_tree 9 段 rc 全 (void)）| 逐帧失败→满幅噪声灌功放仍显绿 | runbook 1B 功放断电/音量最小+假绿征兆 |
| 3 | M1_RX_SLOTS=2 fallback 文档称「只改一处」实漏 rx[] 步距（rx[f*M1_RX_SLOTS]）| fallback 即乱序假绿 | IMPORT_GUIDE R52 WARNING×2：勿自行翻宏，发回 grep 等 PM build |
| 4 | FIRA QueueTask 自旋在 SPORT DMA 中断里（FIR DONE 优先级须高于 SPORT DMA+嵌套开）| M2 首帧可能挂死 | runbook 1B 征兆（rx_block_count 卡 1+setup_rc=0）|
| 5 | m1_loopback_init ~9 腿折叠 rc=1（无逐段 rc）| 失败腿不明多跑一轮 | PM 判读注意③（cwrc=-99 vs 0 拆）|
| 6 | g_m1_softcfg_hwerr volatile 强转去 volatile（C11 UB，实际理论级）| 理论 | defer |
| 7 | m1_softconfig.c:67 注释「bits」措辞 + m1_loopback_tdm.c 注释残留 g_m1_rx_buf | 文档已正源码注释未改 | 随下次 CTO-gated commit 捎带 |
| 8 | .cproject loader 2.11.1 硬路径 + device-programmer 路径 | build 尾步报错 | IMPORT_GUIDE F7 |
| 9 | 暴露 `g_m1_u6_addr_used = M1_U6_TWI_ADDR`（override 生效的直接观测）| 现靠 build console 凭证 | runbook 第 2 次步骤 3 |
| 10 | M2 .map 须核 ldf_stack_length ≥ ~16KB（fira_tfb 栈帧 ~6.7KB 进回调）| 栈溢出 | runbook 1B .map 检查项 |
（前轮已 defer：sweep 移出 boot 路径/hwerr 逐写/.cproject 预启用 map/sweep open_rc/cwrc OR 聚合。R55 追加：11=载板 flag 跳过 U6@0x22 使能序列（本板上 vestigial，保留作官方 SOMCRR 兼容）。）

## 5. 纪律
- **R55 判据替换**：换同款 AD-EXKIT 载板=安全（使能硬连线，原理图 L1）；换官方 SOMCRR 载板才需 U6@0x22 代码（届时 rc 全 0 判据复活）。本板 rc=11×5 是永久预期值。
- 任何 logic 修（block B 各分支）CTO-gated；本批量诊断/自探测是 obs/probe-only。
- cycle 读数引用前确认 bracket 口径（R42）；冻结/M2 段零触碰。

---
*生成 2026-06-09，PM lead。批量包实现待 dsp+critic 门。*
