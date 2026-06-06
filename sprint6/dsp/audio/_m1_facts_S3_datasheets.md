# FACTS S3_datasheets (ADAU1979 ADC / ADAU1962A DAC register-order facts)

> 源 PDF: knowledge_base/ezkit/bsp/datasheets/adau1979.pdf (Rev. A, 42 页) +
>         knowledge_base/ezkit/bsp/datasheets/ADAU1962A.pdf (Rev. A, 48 页)
> 锚定纪律(R31): 表号优先; 页号为 pdftotext -layout 提取的 PDF 物理页, 与页脚 "Rev. A | Page N of M" 一致核对过.
> 标签: [datasheet]=datasheet 正文/表; [inferred]=推测明标; [board-confirm]=本地查无须板上确认.

## F-ADC-I2C-地址（ADAU1979）
- FACT: ADAU1979 控制口默认上电即 I2C 模式; 拉 CLATCH 引脚连续 3 次低电平可切到 SPI 模式; I2C 下为纯从机, 需系统主机驱动.
  SRC: adau1979.pdf P21 (节 "I2C MODE" / "By default ... operates in I2C mode")
  GRADE: [datasheet]
- FACT: ADAU1979 的 7-bit I2C 器件地址固定形态为 xx10001, 其中 Bit7=ADDR1 引脚电平、Bit6=ADDR0 引脚电平; 第一字节 Bit0 为 R/W (1=读, 0=写).
  SRC: adau1979.pdf Table 11 "I2C First Byte Format" (P21)
  GRADE: [datasheet]
- FACT: 由 ADDR1/ADDR0 引脚选出的四个可选 7-bit 器件地址为: 0010001(0x11)、0110001(0x31)、1010001(0x51)、1110001(0x71); 0x11 = ADDR1/ADDR0 均接低.
  SRC: adau1979.pdf P21 (节 "I2C MODE" 四项 bullet)
  GRADE: [datasheet]
- FACT: 控制口寄存器全 8-bit 宽, 地址区间 0x00..0x1A.
  SRC: adau1979.pdf P21 ("registers ... eight bits wide ... start at Address 0x00 and end at Address 0x1A")
  GRADE: [datasheet]

## F-ADC-上电与复位序（ADAU1979）
- FACT: ADAU1979 单 3.3V 供电(AVDDx), 内部 LDO 生成 1.8V DVDD; POR 电路监视 DVDD, 在 DVDD 达 1.2V 时释放内部复位.
  SRC: adau1979.pdf P12 (节 "POWER-ON RESET SEQUENCE" + Figure 13)
  GRADE: [datasheet]
- FACT: PD/RST(Pin6) 拉高后内部稳压器开始给 DVDD 上的 CEXT 充电, 充电时间常数 tC = ROUT×CEXT (ROUT≈20Ω typ); CEXT=10µF 时 tC≈200µs; 建议至少等待 tC 后再发 I2C/SPI 控制信号.
  SRC: adau1979.pdf P12 ("tC = ROUT × CEXT ... recommended to wait for at least the tC period")
  GRADE: [datasheet]
- FACT: 硬复位时 PD/RST 拉低须保持整段 tD 时间(tD = 1.32×RINT×CEXT, RINT≈64kΩ typ; CEXT=10µF 时 tD≈0.845s); 可并联 REXT(典型 3kΩ)把 tD 缩短到 ≈37.8ms.
  SRC: adau1979.pdf P12-P13 ("tD = 1.32 × RINT × CEXT ... tD = 1.32 × REQ × CEXT = 37.8 ms")
  GRADE: [datasheet]
- FACT: 软复位位 S_RST = Register 0x00 (M_POWER) Bit7 (1=软复位, 复位全部内部电路与控制寄存器到默认; AVDDx 掉电时软复位可能不保证正确初始化); 上下电循环不强制需要软复位.
  SRC: adau1979.pdf Table 17 "Bit Descriptions for M_POWER" (P27) + P13
  GRADE: [datasheet]
- FACT: 主上电位 PWUP = Register 0x00 (M_POWER) Bit0, 必须置 1 才能上电整片; M_POWER 复位值 0x00.
  SRC: adau1979.pdf Table 17 (P27) + Table 16 Register Summary (P26)
  GRADE: [datasheet]

## F-ADC-PLL配置与锁判据（ADAU1979）
- FACT: PLL 由 Register 0x01 (PLL_CONTROL) 配置, 复位值 0x41.
  SRC: adau1979.pdf Table 18 "Bit Descriptions for PLL_CONTROL" (P28) + Table 16 (P26)
  GRADE: [datasheet]
- FACT: 锁判据 = PLL_LOCK = Register 0x01 Bit7 (只读, 1=已锁); 建议上电后读此位确认 PLL 输出频率正确后再解除音频静音.
  SRC: adau1979.pdf Table 18 (P28) + P13 ("PLL_LOCK bit (Bit 7) of Register 0x01 indicates the lock status")
  GRADE: [datasheet]
- FACT: PLL_MUTE = Register 0x01 Bit6 (复位 1=PLL 失锁自动静音 ADC 输出); CLK_S = Bit4 (0=MCLK 作 PLL 输入, 1=LRCLK 作 PLL 输入, LRCLK 模式仅支持 32k..192k fS).
  SRC: adau1979.pdf Table 18 (P28)
  GRADE: [datasheet]
- FACT: MCS = Register 0x01 Bits[2:0] 设 PLL 倍频比 (复位 001=256×fS); 编码 000=128×fS / 001=256×fS / 010=384×fS / 011=512×fS / 100=768×fS; 101/110/111=Reserved.
  SRC: adau1979.pdf Table 18 (P28)
  GRADE: [datasheet]
- FACT: PLL 在 LRCLK 模式时, 串口须配为从机且帧时钟由主器件喂入; 改 PLL 设置时强烈建议先禁用 PLL、改设置、再使能.
  SRC: adau1979.pdf P13 (节 "PLL AND CLOCK")
  GRADE: [datasheet]

## F-ADC-时钟要求MCLK与256xfS（ADAU1979）
- FACT: 默认电气表条件锚点 = 主时钟 12.288 MHz (48 kHz fS, 256×fS 模式); PLL 锁定时间最大 10 ms; MCLKIN 占空比 40-60%, 适用 256×/384×/512×/768×fS.
  SRC: adau1979.pdf P3 (Specifications 表头) + P5 (PLL Lock Time / INPUT MASTER CLOCK 表)
  GRADE: [datasheet]
- FACT: 48 kHz fS 下所需 MCLKIN 频率 vs MCS: 000=128×fS=6.144MHz / 001=256×fS=12.288MHz / 010=384×fS=18.432MHz / 011=512×fS=24.576MHz / 100=768×fS=36.864MHz.
  SRC: adau1979.pdf Table 9 "Required Master Clock Input Frequency for Common Sample Rates" (P13)
  GRADE: [datasheet]

## F-ADC-TDM8与SAI字段（ADAU1979）
- FACT: TDM 编程寄存器组 = Register 0x05..0x08; 可编程 TDM slot 宽度、数据宽度、通道分配及输出引脚.
  SRC: adau1979.pdf P18 (节 "TDM Mode") + Table 16 (P26)
  GRADE: [datasheet]
- FACT: SAI(串口模式)字段 = Register 0x05 (SAI_CTRL0) Bits[5:3]; 取值 000=Stereo / 001=TDM2 / 010=TDM4 / 011=TDM8 / 100=TDM16. 即 TDM8 = SAI=011.
  SRC: adau1979.pdf Table 20 "Bit Descriptions for SAI_CTRL0" (P30)
  GRADE: [datasheet]
- FACT: SAI_CTRL0(0x05) 其余字段: SDATA_FMT=Bits[7:6] (00=I2S(LRCLK 后 1 BCLK 延迟)/01=LJ/10=RJ 24-bit/11=RJ 16-bit); FS=Bits[2:0] (000=8-12k/001=16-24k/010=32-48k/011=64-96k/100=128-192k); 复位值 0x02.
  SRC: adau1979.pdf Table 20 (P30) + Table 16 (P26)
  GRADE: [datasheet]
- FACT: SAI_CTRL1(0x06) 字段(复位 0x00): SDATA_SEL=Bit7(0=SDATAOUT1/1=SDATAOUT2 输出, 仅 TDM4+); SLOT_WIDTH=Bits[6:5](00=32 BCLK/slot, 01=24, 10=16, 11=Reserved); DATA_WIDTH=Bit4(0=24-bit/1=16-bit); LR_MODE=Bit3(0=50%占空/1=脉冲 1 BCLK 宽); SAI_MSB=Bit2(0=MSB first/1=LSB first); BCLKRATE=Bit1(0=32 BCLK/ch, 1=16, 仅主模式); SAI_MS=Bit0(0=从机/1=主机).
  SRC: adau1979.pdf Table 21 "Bit Descriptions for SAI_CTRL1" (P31)
  GRADE: [datasheet]
- FACT: 一致性自洽: TDM8 + SLOT_WIDTH=00(32 BCLK/slot) @48kHz => BCLK = 8slot×32×48k = 12.288 MHz = 256×fS, 即 codec 原生 TDM8/256×fS 模式 (与 DOC-S4-IO-01 锁定 8×32@48k 同口径).
  SRC: adau1979.pdf Table 20+Table 21 (P30-P31) 字段推算; 数值与 Table 9 (P13) 256×fS=12.288MHz 一致
  GRADE: [inferred]

## F-ADC-slot线序与通道映射（ADAU1979）
- FACT: 默认串行数据从 SDATAOUT1 引脚输出; SDATA_SEL(0x06 Bit7) 可改为从 SDATAOUT2 输出; 未用 slot 期间输出引脚为高阻(可与总线上其他器件共享数据线).
  SRC: adau1979.pdf P18 (节 "TDM Mode")
  GRADE: [datasheet]
- FACT: 通道->slot 映射 = SAI_CMAP12(0x07) CMAP_C1=Bits[3:0]/CMAP_C2=Bits[7:4] (复位 0x10); SAI_CMAP34(0x08) CMAP_C3/CMAP_C4 (复位 0x32). 每 4-bit 编码 0000=Slot1 ... 1111=Slot16 (TDM8+ 才可用 Slot5-8, TDM16 才可用 Slot9-16).
  SRC: adau1979.pdf Table 22 "Bit Descriptions for SAI_CMAP12" (P32) + Table 16 (P26)
  GRADE: [datasheet]

## F-ADC-关键默认值（ADAU1979 Table 16 Register Summary, P26）
- FACT: 复位默认值: 0x00 M_POWER=0x00 | 0x01 PLL_CONTROL=0x41 | 0x04 BLOCK_POWER_SAI=0x3F | 0x05 SAI_CTRL0=0x02 | 0x06 SAI_CTRL1=0x00 | 0x07 SAI_CMAP12=0x10 | 0x08 SAI_CMAP34=0x32 | 0x0E MISC_CONTROL=0x02.
  SRC: adau1979.pdf Table 16 "REGMAP_ADAU1979 Register Summary" (P26)
  GRADE: [datasheet]
- FACT: BLOCK_POWER_SAI(0x04, 复位 0x3F): Bit7=LR_POL, Bit6=BCLKEDGE, Bit5=LDO_EN, Bit4=VREF_EN, Bits[3:0]=ADC_EN4..ADC_EN1 (各 1=该 ADC 通道使能, 复位均 1).
  SRC: adau1979.pdf Table 16 (P26) + Table 19 "Bit Descriptions for BLOCK_POWER_SAI" (P29)
  GRADE: [datasheet]
- FACT: ADAU1979 为 4 通道 Σ-Δ ADC (两组立体声对), SDATAOUT1=ADC L1/R1, SDATAOUT2=ADC L2/R2; SUM_MODE(0x0E Bits[7:6]) 可两路求和(+3dB)或四路求和(+6dB).
  SRC: adau1979.pdf P8 (Pin 13/14 功能) + P16 (节 "ADC SUMMING MODES")
  GRADE: [datasheet]

## F-DAC-I2C-地址（ADAU1962A）
- FACT: ADAU1962A I2C 器件地址 = 内建地址 0x04 + 两个引脚位 ADDR1/ADDR0; 可寻址四片. 7-bit 从地址表: AD1/AD0=00->0x04, 01->0x24, 10->0x44, 11->0x64.
  SRC: ADAU1962A.pdf Table 15 "I2C Addresses" (P16) + P16 正文 ("internal built-in address (0x04)")
  GRADE: [datasheet]
- FACT: SDA 为开漏, 需 2 kΩ 上拉; SCL 高且 SDA 拉低=start; 数据字前 8 bit = 器件地址+R/W.
  SRC: ADAU1962A.pdf P16 (节 "I2C CONTROL PORT")
  GRADE: [datasheet]

## F-DAC-上电与复位序（ADAU1962A）
- FACT: 供电次序须先 AVDDx 与 IOVDD, 再 DVDD; AVDDx 须稳定且 IOVDD 在调压 10% 内才可加 DVDD (用内部稳压器时默认满足).
  SRC: ADAU1962A.pdf P16 (节 "POWER-UP AND RESET")
  GRADE: [datasheet]
- FACT: PU/RST 先经外部电阻拉低、供电稳定后再驱高(或 RC 网络); 拉低时进 <3µA 低功耗、全功能禁用; 拉高后需 300 ms 稳定; 之后 DAC_CTRL0 的 MMUTE 位须翻转才工作.
  SRC: ADAU1962A.pdf P16 (节 "POWER-UP AND RESET")
  GRADE: [datasheet]
- FACT: 厂家给出的标准启动步骤(5 步): 1)按上电节加电; 2)供电稳后 PU/RST 驱高; 3)置 PUP=1; 4)编程所有目标寄存器; 5)置 MMUTE=0 解除全通道静音.
  SRC: ADAU1962A.pdf P16 (节 "For proper startup ... follow these steps")
  GRADE: [datasheet]
- FACT: PUP(主上电控制) = PLL_CLK_CTRL0(0x00) Bit0, 必须作为第一条寄存器写置 1 上电; 置 0 进 idle 但保留寄存器设置.
  SRC: ADAU1962A.pdf Table 25 "Bit Descriptions for PLL_CLK_CTRL0" (P25) + P16
  GRADE: [datasheet]
- FACT: SOFT_RST = PLL_CLK_CTRL0(0x00) Bit3 (1=复位, 复位除 I2C/SPI 通信与 Reg0x00/0x01 外全部寄存器到默认; 不会在差分模拟输出产生爆音).
  SRC: ADAU1962A.pdf Table 25 (P25) + P16
  GRADE: [datasheet]

## F-DAC-PLL与时钟控制+锁判据（ADAU1962A）
- FACT: PLL/时钟控制 = PLL_CLK_CTRL0(0x00, 复位 0x00) 与 PLL_CLK_CTRL1(0x01, 复位 0x2A); PU/RST 驱高后这两个寄存器即可编程.
  SRC: ADAU1962A.pdf Table 24 Register Summary (P24) + Table 25/Table 26 (P25-P26) + P15
  GRADE: [datasheet]
- FACT: PLL_CLK_CTRL0(0x00) 字段: PLLIN=Bits[7:6](00=MCLKI/XTALI, 01=DLRCLK 作 PLL 输入, 10/11=Reserved); XTAL_SET=Bits[5:4](00=晶振使能, 11=XTALO 关); MCS=Bits[2:0..实为[2:1]](00=256×fS/01=384×fS/10=512×fS/11=768×fS @44.1/48k).
  SRC: ADAU1962A.pdf Table 25 (P25)
  GRADE: [datasheet]
- FACT: 锁判据 = PLL_LOCK = PLL_CLK_CTRL1(0x01) Bit2 (只读, 0=未锁/1=已锁); PLL 须先供电稳定再用作音频源.
  SRC: ADAU1962A.pdf Table 26 "Bit Descriptions for PLL_CLK_CTRL1" (P26) + P15
  GRADE: [datasheet]
- FACT: PLL_CLK_CTRL1(0x01, 复位 0x2A) 其余: LOPWR_MODE=Bits[7:6]; MCLKO_SEL=Bits[5:4](复位 10); PLL_MUTE=Bit3(复位 1, PLL 失锁自动静音); VREF_EN=Bit1(复位 1=内部基准使能); CLK_SEL=Bit0(0=MCLK 取自 PLL, 1=MCLK 直取 MCLKI/XTALI).
  SRC: ADAU1962A.pdf Table 26 (P26)
  GRADE: [datasheet]
- FACT: 直接主时钟模式(CLK_SEL=1)须在 MCLKI 喂 512×fS(参 48k 模式)并在 PDN_THRMSENS_CTRL_1 关 PLL; PLL 模式 fMCLK 范围 6.9-40.5 MHz, PLL 锁定时间最大 10 ms.
  SRC: ADAU1962A.pdf P15 + P6 (INPUT MASTER CLOCK 表 + PLL Lock Time)
  GRADE: [datasheet]

## F-DAC-DAC_CTRL寄存器与TDM8（ADAU1962A）
- FACT: DAC_CTRL0(0x06, 复位 0x01): SDATA_FMT=Bits[7:6](仅 SAI=000 用); SAI=Bits[5:3](000=Stereo/001=TDM2 八线/010=TDM4 四线/011=TDM8 双线/100=TDM16 单线 48k); FS=Bits[2:1](00=32/44.1/48k...); MMUTE=Bit0(复位 1=全通道静音, 0=正常). 即 TDM8 = SAI=011.
  SRC: ADAU1962A.pdf Table 31 "Bit Descriptions for DAC_CTRL0" (P30) + Table 24 (P24)
  GRADE: [datasheet]
- FACT: DAC_CTRL1(0x07, 复位 0x00): BCLK_GEN=Bit7(1=内部生成 DBCLK, PLL 锁 DLRCLK 时可无外部 DBCLK); LRCLK_MODE=Bit6(0=50%占空/1=脉冲, 仅 TDM); LRCLK_POL=Bit5; SAI_MSB=Bit4(0=MSB first); BCLK_RATE=Bit2(0=32/帧,1=16, 仅主模式); BCLK_EDGE=Bit1; SAI_MS=Bit0(0=从机/1=主机).
  SRC: ADAU1962A.pdf Table 32 "Bit Descriptions for DAC_CTRL1" (P31)
  GRADE: [datasheet]
- FACT: DAC_CTRL2(0x08, 复位 0x06): BCLK_TDMC=Bit4(0=32 BCLK/slot,1=16); DAC_POL=Bit3; AUTO_MUTE_EN=Bit2(复位 1=收到 1024 连续零样本自动静音, 逐通道独立); DAC_OSR=Bit1(0=256×fS,1=128×fS 过采样); DE_EMP_EN=Bit0(去加重).
  SRC: ADAU1962A.pdf Table 33 "Bit Descriptions for DAC_CTRL2" (P32)
  GRADE: [datasheet]

## F-DAC-CMAP-slot映射机制8of12（ADAU1962A）
- FACT: ADAU1962A 共 12 路 DAC 输出; 寄存器图(Table 24)无独立 per-channel CMAP 路由寄存器 — slot->通道为按 TDM 模式固定顺序分配(非可编程映射), 由 Table 23 规定.
  SRC: ADAU1962A.pdf Table 24 Register Summary (P24, 无 CMAP 项) + Table 23 (P22)
  GRADE: [datasheet]
- FACT: TDM8 模式(SAI=011)的固定 slot 线序(Table 23): DSDATA1 承载 Channel 1..8, DSDATA2 承载 Channel 9..12, DSDATA3-6 不用; TDM8 模式最大采样率 96 kHz.
  SRC: ADAU1962A.pdf Table 23 (P22, "TDM8 Mode (SAI = 3)" 列)
  GRADE: [datasheet]
- FACT: 即"8-of-12 路由"在单条 TDM8 数据线上=取 DSDATA1 的前 8 个 slot(Channel 1..8)喂 8 路功放; 哪 8 路上板=由数据线选择(SDATA 线)+slot 顺序决定, 非寄存器重映射. 具体上板 8/12 选哪几路属架构/接线决策, 本调研不裁.
  SRC: ADAU1962A.pdf Table 23 (P22) 机制; 取值留架构(任务要求)
  GRADE: [inferred]
- FACT: 12 路各有独立软静音位: DAC_MUTE1(0x09) DAC01..08_MUTE, DAC_MUTE2(0x0A) DAC09..12_MUTE (各 "Soft Mute", 复位 0); 各路独立音量 DACxx_VOL(0x0C..0x17)+主音量 DACMSTR_VOL(0x0B); 各路上下电 DAC_POWERx(0x1D-0x1F, 复位 0xAA).
  SRC: ADAU1962A.pdf Table 24 (P24) + Table 33/34 (P33-P34)
  GRADE: [datasheet]

## F-DAC-去爆音与mute序（ADAU1962A）
- FACT: 去爆音/静音序要点: (a)PU/RST 驱高后必须等 300 ms 稳定; (b)启动序第 5 步置 MMUTE(DAC_CTRL0 Bit0)=0 解除全静音, 即先编程后解静音; (c)SOFT_RST 翻转不会在差分模拟输出产生爆音; (d)逐通道为"Soft Mute"(软静音, 非硬切); (e)支持 autoramp(log 音量自动斜坡)与 clickless mute 特性.
  SRC: ADAU1962A.pdf P16 (300ms/MMUTE/SOFT_RST 无爆音) + P1 Features ("Log volume control with autoramp", "Software-controllable clickless mute") + Table 33/34 (Soft Mute)
  GRADE: [datasheet]
- FACT: AUTO_MUTE_EN(DAC_CTRL2 Bit2, 复位 1) 在 1024 连续零样本时逐通道自动静音 — bring-up 时若送测零数据会自动静音, 是去爆音相关默认行为需注意.
  SRC: ADAU1962A.pdf Table 33 (P32)
  GRADE: [datasheet]

## F-两片时钟拓扑约束（ADC+DAC）
- FACT: 两片各自的 SAI_MS/SAI_MS 位决定本片串口主从: ADAU1979 SAI_CTRL1(0x06) Bit0 SAI_MS(0=从/1=主); ADAU1962A DAC_CTRL1(0x07) Bit0 SAI_MS(0=从/1=主). 同一 TDM 总线上只能一个主器件出 BCLK/LRCLK, 其余(含 SHARC SPORT)须互补配从——具体哪片当主属板级接线决策, datasheet 只给约束不给本板取值.
  SRC: adau1979.pdf Table 21 (P31) + ADAU1962A.pdf Table 32 (P31)
  GRADE: [datasheet]
- FACT: 12.288 MHz 来源选项(数据手册侧): (1)外部主时钟直喂 MCLKIN(ADC)/MCLKI(DAC), 配 PLL MCS=256×fS@48k; (2)ADAU1962A 可用 MCLKI/XTALI 接晶振由内部晶振反相器起振(XTAL_SET=00), 并经 MCLKO 引脚输出缓冲后的主时钟可供 ADC; (3)PLL 从 LRCLK/DLRCLK 反推主时钟(ADC CLK_S=1 / DAC PLLIN=01), 无需独立高频主时钟.
  SRC: ADAU1962A.pdf P15 (节 "CLOCK SIGNALS"/MCLKO) + P16 (SA_MODE MCLKO 缓冲) + adau1979.pdf P13 (CLK_S LRCLK 模式) + Table 9 (P13)
  GRADE: [datasheet]
- FACT: 本 EZKIT 物理时钟拓扑(哪片做 TDM 主、12.288 MHz 实际由 SHARC SPORT 出还是 codec 出还是板载晶振出)须板上/原理图确认; datasheet 仅约束"总线单主". (survey 线索: M1_SYMBOL_SURVEY.md:36/72-75 提 ALT 例程 SPORT 跑 MC/TDM、8×32@48k=256×fS, 但主从具体配置标 "DIFF to verify" G-M1-1, 本调研不据其下结论.)
  SRC: ADAU1962A.pdf P16/P22 + adau1979.pdf P31 约束; 本板取值无 datasheet 记载
  GRADE: [board-confirm]

## NOT_FOUND
- ADAU1962A 无独立 per-channel CMAP/slot 重映射寄存器(slot->通道为 Table 23 固定顺序, 非可编程); 故无"CMAP 寄存器取值"可列(机制已在 F-DAC-CMAP 小节说清).
- 两片在本 ADI EZKIT 上的实际主/从角色与 12.288 MHz 的实际物理来源(SPORT vs codec vs 板载晶振)——datasheet 无本板记载, 须原理图/板上确认(已入 F-两片时钟拓扑 [board-confirm]).
- ADAU1979 PLL 锁定后到可解静音的"建议额外等待时间"无具体数值(仅给 "Lock Time 最大 10 ms" 与 "读 PLL_LOCK 位后再解静音"的定性建议).
- ADAU1962A DAC_CTRL0 FS 字段在 datasheet 文本中标注 Bits[2:1](与 Table 24 位图一致), 但启动 MMUTE 占 Bit0; 未见 Bit?? 多余位的独立默认说明(已按 Table 31 录入, 无缺值)。

## VERIFIER_REPORT
- CHECKED: 43 (全部事实条逐条独立开 PDF 核对; ADC 25 条 / DAC 18 条; [datasheet] 抽核率 100%>60% 门槛; 0 条 [L1-example-called] 本文件不含例程引用; 1 条 [inferred] TDM8 自洽算术 + 1 条 [inferred] 8-of-12 + 1 条 [board-confirm] 时钟拓扑均核判定对)
- 核验法: pdftotext -layout 逐页提取(adau1979 42 页 / ADAU1962A 48 页), 物理页与页脚 "Rev. A | Page N of M" 逐页对齐确认一致; 逐条核 页号/表号/位域/复位值/取值编码/实测取值.
- 页号锚定: 全部抽核页(ADC P3/5/8/12/13/16/18/21/26-32, DAC P1/6/15/16/22/24/25/26/30/31/32/33/34)物理页=印刷页, 无页号造假.
- 表号锚定: ADC Table 9/11/16/17/18/19/20/21/22 全部真实在位且内容相符; DAC Table 15/23/24/25/26/31/32/33 全部真实在位且内容相符.
- 关键数值复核 CLEAN: ADC 0x11/0x31/0x51/0x71 四地址(Table 11); 复位值 0x00/0x41/0x3F/0x02/0x00/0x10/0x32/0x02(Table 16); tC≈200µs/tD≈0.845s/37.8ms(P12-13); 256×fS@48k=12.288MHz(Table 9 P13); SUM +3dB/+6dB(P16 实有"SNR improves by 3/6 dB"). DAC 0x04/0x24/0x44/0x64(Table 15); 复位 0x00/0x2A/0x01/0x00/0x06(Table 24); 300ms+MMUTE(P16); TDM8 DSDATA1=Ch1..8/DSDATA2=Ch9..12 max 96k(Table 23); PLL_LOCK=0x01.b2 只读(Table 26 Access R); AUTO_MUTE 1024 零样本(Table 33); CLK_SEL/512×fS/fMCLK 6.9-40.5MHz(P15/P6).
- 等级判定核: 无 [datasheet]/[inferred] 被措辞成 measured; [board-confirm](时钟拓扑实际主从/12.288MHz 物理源)判定对——datasheet 确无本板记载, 本地无头; 两条 [inferred](TDM8 自洽算术 8×32×48k=12.288MHz; 8-of-12=取 DSDATA1 前 8 slot)均明标推测未伪装成事实, 留架构决策不裁, 判定对; NOT_FOUND 第 1 项(DAC 无 per-channel CMAP)经 Table 24 反查确认无 CMAP 寄存器, 真实.
- VERDICT: ISSUES (仅 1 类表号标注偏移, 内容与页号全对, 非 FABRICATION; 余全 CLEAN)
- MISMATCH: F-DAC-CMAP slot映射(:164) + F-DAC-去爆音(:169) SoftMute SRC 标 "Table 33/34 (P33-P34)" | 页 P33-P34 正确且确含逐通道 Soft Mute, 但该两页实为 Table 34(DAC_MUTE1)+Table 35(DAC_MUTE2); Table 33 实为 DAC_CTRL2(P32) | 修正: 表号 "Table 33/34" -> "Table 34/35"(内容/页号正确, 非造假, 仅标号顺移一位)
- MISMATCH: (除上述表号顺移外, 全部 43 条页号/表号/API无/位域/复位值/取值逐位相符) | (none-additional)

## SUMMARY
两片 codec 寄存器序事实已按表号优先锚定齐全。ADAU1979(ADC): I2C 默认从机, 7-bit 地址 xx10001 由 ADDR1/ADDR0 引脚选四选一(0x11/0x31/0x51/0x71, 双低=0x11, Table 11); 上电须等 tC≈200µs(CEXT=10µF)后发控制字、PWUP(0x00.b0)=1 上电; PLL 由 0x01 配置, MCS[2:0]=001 选 256×fS@48k=12.288MHz(Table 9), 锁判据=PLL_LOCK(0x01.b7 只读)、读到 1 再解静音; TDM8=SAI(0x05.b[5:3])=011、SLOT_WIDTH(0x06.b[6:5])=00(32BCLK/slot)、8×32×48k=256×fS=12.288MHz 自洽; 通道->slot 经 SAI_CMAP12/34(0x07/0x08)。ADAU1962A(DAC): 内建地址 0x04+ADDR 引脚(0x04/0x24/0x44/0x64, Table 15); 标准 5 步启动(供电->PU/RST 高->PUP=1->编程->MMUTE=0), PU/RST 高后须 300ms 稳定; PLL/CLK 由 0x00/0x01 配, MCS@256×fS、锁判据=PLL_LOCK(0x01.b2 只读)、CLK_SEL(0x01.b0)选 PLL/直 MCLK; TDM8=SAI(0x06.b[5:3])=011; 关键发现——DAC 12 路无独立 CMAP 路由寄存器, slot->通道是按 Table 23 的固定顺序(TDM8 下 DSDATA1=Ch1..8/DSDATA2=Ch9..12), "8-of-12" = 取 DSDATA1 前 8 slot, 上板选哪 8 路属接线/架构决策(本调研不裁); 去爆音序=300ms 稳定+先编程后置 MMUTE=0+逐路 Soft Mute+autoramp/clickless 特性+AUTO_MUTE_EN(1024 零样本自动静音)默认开。两片时钟拓扑 datasheet 只约束"TDM 总线单主"(各片 SAI_MS 位选主从)、12.288MHz 三种来源(外部直喂/晶振经 MCLKO 缓冲/PLL 反推 LRCLK), 但本 EZKIT 实际主从角色与 12.288MHz 物理来源 datasheet 无记载, 标 [board-confirm]。survey 的 ADC 地址 0x11 与本调研一致(=ADDR 双低项), DAC 0x04 一致。
