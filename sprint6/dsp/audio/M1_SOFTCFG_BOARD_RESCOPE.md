# M1 softcfg 终局：板身份揭晓 → F-SRU-1 re-scope 关闭（CTO 裁决 2026-06-11）

> PM lead，2026-06-11。板测 1A 读数 [L1] + 厂商原理图亲读 [L1/vendor-schematic] 双轨互证。
> 独立 critic R54 CONDITIONAL PASS（修正 4 MAJOR 后成稿，本文即修正稿）→ R55 增量过门 → CTO 采纳。
> reviewer: critic @ claude-fable-5[1m] / 2026-06-11。（该 critic 报告自题 R52 = 团队序号 R54，发现 ID F52-* 同轮。）
> **判据撤回（C7 传播源头）**：「F-SRU-1 修复 + 板上 rc 全 0 复验前不得宣称换板安全」自本裁决起退役，
> 新口径见 §4。全库传播位置见 §6。

## 1. 板身份（终于坐实）
物理板 = **第三方 AD-EXKIT V2.1 底板 + ADSP-21569-SOM REV 1.1**（OpenADSP 生态；丝印照片 + BENCH_OPS_CARD:5
肉眼记录一致），**不是** ADI 官方 EV-SOMCRR-EZKIT。m1_softconfig 的 U6@0x22 使能序列是按官方 SOMCRR 载板例程
写的——**写给了一块不存在的芯片**。5×rc=11 (NACK) 是这块板的永久正确行为。

## 2. 原理图亲读事实（critic R54 300dpi+文本层双轨核，修正后）
### TWI2 总线全员枚举（三板）
| 器件 | 位置 | 7-bit 地址 | 0x20-0x27? |
|---|---|---|---|
| **U13 MCP23017**（注意：U13 非 U15）| SOM Mux_Ports 页 | **0x21**（strap 亲核 A0↑R54/A1↓R55/A2↓R58）| **是（唯一）** |
| U6(SOM) Si5356A 时钟 | SOM | 0x70/0x71 | 否 |
| U2 ADAU1962 DAC | 底板 | 0x04 | 否 |
| U8 ADAU1979 ADC | 底板 | 0x11 | 否 |
| AD2428（插入式 A2B 子卡上，底板只有 CON10X2 插座）| 子卡 | 0x68/0x6C | 否 |
| AT24C256（子卡）| 子卡 | 0x50-0x57 | 否 |
| 24AA01T（SOM，且根本不在 TWI2 上）| SOM | 0x50 段 | 否 |

### U13 引脚映射（修正版：LED 在 GPA0-2，GPB 全悬空）
GPA0/1/2=LED×3｜GPA3=SP2IFLASH_CS_EN#｜GPA4=SPI2D2_D3_EN#｜GPA5=UART0_EN#｜GPA6=UART0_FLOW_EN｜GPA7=NC｜GPB0-7=悬空。
RESET#←SYS_HWRST#。**零 codec 使能位。**

### codec 使能/复位 = 硬连线（F-SRU-1 前提不存在的根据）
ADAU1962 PU/RST_N 与 ADAU1979 PD_N/RST_N ← **#CPU_RESET = SYS_HWRST#**（SOM 复位监督器 ADM6315 统一释放）
→ **DSP 能跑代码 ⇒ codec 必已出复位，无条件成立，不经任何 I2C 扩展器**。地址 strap 亲核 = 0x04/0x11，
与 m1_loopback_tdm.c 写的地址一致、板上 codec_write_rc=0 [L1] 互证（铁律七双轨）。

## 3. override build 取消（机理修正版）
对 0x21(U13) 重放 SOMCRR 序列（IODIRA=0x18/IODIRB=0x00/GPIOB=0xFD/GPIOA=0x25→0x05）的真实后果：
- IODIRA=0x18 恰把 GPA3/GPA4（两个 flash 使能脚）设**输入不驱动**→板上默认下拉=使能，boot flash **不**受影响
  （我初稿说「扰动 flash CS」是错的，critic 纠正）；
- **真被驱动**：GPA5/GPA6（UART0_EN#/UART0_FLOW_EN 被 0x25→0x05 来回翻 = 调试串口开关被拨）+ GPA0-2 LED；
  GPIOB=0xFD 写进悬空脚无害。
- 取消理由：①本载板**无 codec 使能扩展器**，override 对 F-SRU-1 零收益；②盲写他人系统管理扩展器=无谓系统态
  扰动；③若日后 IODIRA 值改动，flash 使能脚就会被真驱动——危险一步之遥。

## 4. CTO 裁决（DEC-S6-FSRU1-RESCOPE-01，2026-06-11 采纳）
1. **F-SRU-1 对 AD-EXKIT 载板不适用**（使能硬连线，原理图 L1）——softcfg 命脉线就此收口，不再消耗板时间。
2. **0x22 使能代码保留**作官方 SOMCRR 载板兼容；加载板 flag 跳过 = CTO-gated 代码改，defer（§4B 清单追加）。
3. **判据替换**：~~「F-SRU-1 修复+rc 全 0 复验前不得宣称换板安全」~~ → **「换同款 AD-EXKIT 载板=安全（使能硬
   连线）；换官方 SOMCRR 载板才需 U6@0x22 使能代码生效（届时 rc 全 0 判据复活）」**。本板上 softcfg_rc=11×5
   = 预期值，**永远不可能全 0，也不需要**。
4. **codec 寄存器级软配置（0x04/0x11 的 PLL/时钟/解 mute 写）仍然必做**——硬连线只覆盖复位脚（critic 口子①，
   防后人误删）。
5. R51 探测安全 gate **闭合**：0x20-0x27 唯一器件=真 MCP23017（寄存器指针型），sweep 0x00 探测无害坐实。
6. 版本前提注记：图纸 Revision 栏空白，「V2.1」系文件名/目录级关联（critic 口子③）；换板时按 BENCH_OPS_CARD
   三特征（电源开关/转接卡/双 A2B）肉眼比对。

## 5. 命名撞名警告（critic F52-MINOR-1）
本项目文档凡称 codec 使能扩展器为「U6」均指 **SOMCRR-U6（官方载板的）**；实物 SOM 上真正的 U6 = Si5356A
时钟芯片（在 TWI2 0x70）。上板排障勿找错芯片。

## 6. C7 传播位置（撤回判据「rc 全 0/换板安全」+ R1a 表行）
- STAGE4_TESTER_RUNBOOK.md：交付前 gate 关闭标注；判读表+第 2 次测试节 R55 横幅（override 取消、剩余任务改向）；页脚判据替换。
- STAGE4_BATCH_PLAN.md：§0 状态、§2 表 R55 戳、§5 纪律判据替换、§4B 追加载板 flag defer 项。
- M1_SOFTCFG_U6_ADDR_SWEEP.md / M1_SOFTCFG_U6_NACK_ROOTCAUSE.md：R55 终局横幅（R1a「地址错」被「载板架构不匹配」取代；block-B 各分支对本载板 moot）。
- memory/MEMORY.md + 新 memory 文件：板身份+判据替换。
- decisions_log：DEC-S6-FSRU1-RESCOPE-01 新行（R48/R44 行存史不动）。

## 7. 板上剩余（下次同事上板做什么）
**第 2 次 softcfg 验证 = 取消。** 剩余 = ①1A 还欠的对齐 dump（s_m1_rx_buf[0][0..7]，立体声源）+ .map；
②1B M2 FIRA（按 runbook，功放断电/音量最小）。可选顺手：读 U13 IODIRA/GPIOA 当前值（只读）作 L1 佐证。
