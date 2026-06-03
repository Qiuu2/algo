# 音频 I/O 拓扑（直进直出）— 文档事实 + gaps

**文档 ID**：DOC-S4-IO-01 ｜ 日期：2026-06-03 ｜ PM 直跑 grep 提取 ｜ 挂接：DEC-S4-DSP-01 / 系统架构
**板**：AD-EXKIT V2.1 + ADSP-21569-SOM + AD2428W-SOM ｜ **拓扑**：直进直出（不用 A2B，音柱单元本地）
**红线**：只录文档有的（带 PDF/源码出处）；文档没有的列 **gap**，不凭印象补。

---

## 1. 芯片清单（带出处）

| 角色 | 型号 | 关键规格 | 出处 |
|------|------|---------|------|
| **音频输入 ADC** | **ADAU1979** | **Quad（4 通道）ADC，24-bit，8k-192kHz；支持 right-just/left-just/I2S/**TDM** | `bsp/datasheets/adau1979.pdf` p1（"Quad Analog-to-Digital Converter"；"Right justified, left justified, I2S, and **TDM** modes"）|
| **音频输出 DAC** | **ADAU1962A** | **12 通道，24-bit，32k-192kHz DAC**，差分/单端输出，SPI/I2C 控制 | `bsp/datasheets/ADAU1962A.pdf` p1（"**12-Channel** … 192 kHz, 24-Bit DAC"）|
| 功放 | **ACM3128A** | 0.246 Vrms / 20kΩ 模拟输入 | `KB-HW-001`（拆机）/ handover L190（U3）|
| 主控 | ADSP-21569 SHARC+ | 单核 1GHz | DEC-S3-PROC-01 |

> EZKIT 板载 codec = ADAU1979(ADC)+ADAU1962A(DAC)，由 ADI 官方例程 `Pipelined`（ADC→处理→DAC）+ `ADAU_1962Common.h`/`ADAU_1979Common.h` 坐实（186×ADAU1962 / 114×ADAU1979 引用）。

---

## 2. I/O 拓扑图（输入 → DSP → 8 路输出）

```
                          [EZKIT 板载，直进直出，AD2428W/A2B 旁路]
  模拟音源 ──→ ADAU1979 ──TDM──→ SPORT4 ──→ ADSP-21569 ──→ SPORT4 ──TDM──→ ADAU1962A ──→ 8×功放 ──→ 16 喇叭
  (1ch讲解/广播)  (4ch ADC,    (SPT4,      (4子带 dyadic     (SPT4,      (12ch DAC,    (ACM3128A)  (8 路 A/B
   [gap:源]      用1ch)      SRU2/DAI1)   beamform 8ch)    SRU2/DAI1)   用8ch)                   对称串联)
```
- **输入**：模拟音源 → ADAU1979（4ch ADC，用 1ch 单声道讲解/广播源）→ 经 SPORT4 TDM 入 21569。
- **DSP**：4 子带 dyadic 树形 + broadside beamform，**8 通道**输出（dsp_8ch_report）。
- **输出**：8ch → ADAU1962A（12ch DAC，**用 8ch**）→ 8 路 ACM3128A 功放 → **8 路 A/B 对称串联 = 16 喇叭**（拆机 KB-HW-001：转接板 16ch 实为 **8 路驱动**）。
- **数字协议 = TDM**（拆机 [L1/硬件实测]，`KB-HW 定向音柱AI数据_extracted.md:51`）。

---

## 3. SPORT / TDM / SRU 配置（带出处）

| 项 | 值 | 出处 / 性质 |
|----|----|-----------|
| **音频 SPORT** | **SPORT4（SPT4）**，A 侧（AD0）+ B 侧（BD0） | `Pipelined/src/Audio_Passthrough_I2S.c:277-296`（SRU2 路由 SPT4_ACLK/BCLK/AFS/BFS/AD0/BD0）|
| **SRU 片上路由** | SPT4 时钟/FS/数据 ↔ **DAI1_PB** 引脚（PB05=BCLK、PB04=FS、PB01=DAC SDATA、PB06=ADC SDATA，PB12/PB20=时钟扇出）| `Audio_Passthrough_I2S.c:275-296`（`SRU2(...)` 赋值）；宏定义 `Pipelined/src/sru21569.h` |
| **TDM slot/位宽（我方锁定）** | **8 slot × 32-bit @ 48kHz** → BCLK = 8×32×48k = **12.288 MHz**（与锁定值数学自洽）| handover L93 "8ch TDM（BCLK 12.288MHz）" + 数学推导；**24-bit 数据置于 32-bit slot**（ADAU 24-bit）= 推导，非寄存器实证 |
| **板上软开关** | SoftConfig 经 TWI/I2C 配 ADC/DAC（U48 Port A/B）| `Pipelined/system/SoftConfig_21569_ADC_DAC.c`（SwitchConfig0/1，TWI 写 ADAU 寄存器）|

> 一路 SPORT4 TDM 带几 ch：ADAU1962A 单片 12ch → **8ch 输出 1 路 SPORT 足够**（1×ADAU1962A）。**16 路驱动**才需 2×SPORT 或 TDM-32 + 多片 DAC（decisions_log:109 旧分析，针对更高通道数；我方 8 路驱动不触发）。

---

## 4. 采样格式
- **采样率**：**48kHz**（项目锁定，handover L93 / dsp_8ch_report；ADAU1962A 32k-192k / ADAU1979 8k-192k **均支持 48k**，datasheet p1）。
- **位宽**：**24-bit**（ADAU1962A/1979 datasheet p1）。
- **TDM**：8 slot（我方 8 路驱动），BCLK 12.288MHz。

---

## 5. Gaps（文档未记录 / 待工程师确认，不编）

| # | gap | 为何是 gap |
|---|-----|-----------|
| G-IO1 | **EZKIT 例程实际采样率寄存器值** | SoftConfig/ADAU PLL 寄存器值未解码确认例程跑的是不是 48k（datasheet 支持，例程实际值待读寄存器/工程师确认）|
| G-IO2 | **模拟音源具体接法** | "1ch 讲解/广播源"是 mic / line-in / 哪个 ADAU1979 输入脚 → 产品设计待定 |
| G-IO3 | **AD2428W-SOM 物理旁路接法** | "直进直出不用 A2B"已定，但 AD2428W-SOM 在板上如何旁路 / 音频不经它的物理走线 → 待工程师确认 |
| G-IO4 | **我方 8ch → ADAU1962A 通道映射 + → 8 路 A/B 物理连线** | 哪个 DAC ch 驱哪路功放/哪对喇叭 = 产品布线设计，文档无 |
| G-IO5 | **TDM slot 精确时序** | BCLK/FSYNC 极性、slot 起始、24-in-32 对齐 = 拆机时序细节未给（`KB-HW:52` 待示波器/逻辑分析仪或 EZKIT 对齐）|
| G-IO6 | **block size 对齐** | 例程 `Pipelined` BLOCK_SIZE=256；我方 harness FRAME=64 → 产品流水线块大小待定（影响延迟/DMA）|
| G-IO7 | **SoftConfig 直进直出开关设置** | U48 等软开关在"直进直出（非 A2B）"下的具体配置值 → 待工程师按产品确认 |

---

## 区分总结
- **板子文档事实（高置信，带出处）**：ADAU1979(4ch ADC)+ADAU1962A(12ch DAC)、SPORT4 经 SRU2/DAI1、TDM、24-bit、48k 支持 —— 全部 datasheet/ADI 例程坐实。
- **我方锁定基线**：8ch TDM / 48k / BCLK 12.288MHz / 8 路 A/B → 16 喇叭（handover + 拆机 [L1]）。
- **数学推导（非寄存器实证）**：8 slot × 32-bit @48k = BCLK 12.288MHz。
- **Gaps（待工程师确认，未编）**：G-IO1~7。

---

*DOC-S4-IO-01，PM 直跑提取 2026-06-03。芯片/SPORT/SRU 全带 PDF/源码出处；采样格式 48k/24bit 文档支持 + 项目锁定；7 项 gap 明列待工程师确认，未凭印象补。*
