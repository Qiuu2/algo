---
name: "HardwareDesignAgent_Skill"
description: "硬件设计专家Agent的专业技能定义、工具使用规范、工作流与输入输出标准"
version: "1.0.0"
author: "ITC Enterprise Multi-Agent System"
---

# 硬件设计专家Agent - 技能定义 (Skill)

## 1. 原理图设计流程

### 1.1 完整设计链

```
系统架构 → 电源树 → 信号链 → 保护电路 → 接口设计 → 检查验证
```

### 1.2 系统架构设计

**架构设计模板：**
```
[音频输入] → [ADC] → [DSP/MCU] → [DAC] → [功放] → [扬声器]
                ↑         ↑
           [控制接口] [数字接口]
                ↑         ↑
           [用户交互] [网络/USB]
```

**架构设计Checklist：**
- [ ] 信号链路完整，从输入到输出无断点
- [ ] 处理链路满足延迟预算
- [ ] 各模块接口电平兼容
- [ ] 时钟架构定义（主时钟分配）
- [ ] 电源架构初步规划
- [ ] 关键器件选型初筛完成

### 1.3 电源树设计

**电源设计流程：**
```
Step 1: 功耗预算
  └── 列出所有器件及其供电需求（电压/电流/纹波）
  └── 计算各电压轨总电流
  └── 计算总功耗
  └── 输出：功耗预算表

Step 2: 电源架构选择
  └── 输入电源类型：AC适配器/POE/电池
  └── 拓扑选择：LDO/Buck/Boost/Buck-Boost
  └── 效率要求：≥85%（Buck）、≥90%（同步整流）
  └── 输出：电源架构框图

Step 3: 器件选型
  └── 根据电流/纹波/效率要求选择IC
  └── 外围器件计算（电感/电容/电阻）
  └── 环路稳定性初步评估
  └── 输出：电源设计计算书

Step 4: 时序设计
  └── 上电时序：Core → I/O → 模拟
  └── 下电时序：模拟 → I/O → Core
  └── 复位时序：POR延迟、手动复位
  └── 输出：电源时序图

Step 5: 保护设计
  └── 过压保护 (OVP)：阈值=额定×110%
  └── 过流保护 (OCP)：阈值=额定×120%
  └── 欠压锁定 (UVLO)
  └── 热关断 (Thermal Shutdown)
```

**电源树模板（专业音频设备）：**
```
外部DC输入 (12V-24V)
    ├── Buck 1: 12V → 5V @ 3A (系统电源)
    │       ├── LDO 1: 5V → 3.3V @ 500mA (数字I/O)
    │       ├── LDO 2: 5V → 1.8V @ 200mA (DSP Core)
    │       └── LDO 3: 5V → 1.0V @ 300mA (DSP Core)
    │
    ├── Buck 2: 12V → 5V @ 1A (模拟电源, 低噪声)
    │       └── LDO 4: 5V → 3.3V @ 200mA (ADC/DAC模拟)
    │
    └── Buck 3: 12V → ±35V @ 2A (Class-D功放电源)
```

### 1.4 音频信号链设计

#### 麦克风输入链路
```
麦克风 → 耦合电容 → 前置放大器 → 抗混叠滤波 → ADC
```

| 器件 | 推荐型号 | 关键参数 | 设计要点 |
|------|----------|----------|----------|
| 前置放大器 | INA217/SSM2019 | EIN<1nV/√Hz | 增益20-60dB可编程 |
| ADC | PCM4204/CS5368 | 24bit/192kHz | 模拟电源隔离 |
| 耦合电容 | 钽电容/固态电容 | 低ESR | 防反相保护 |

#### 线路输出链路
```
DAC → I/V转换 → 低通滤波 → 线路驱动 → 输出连接器
```

| 器件 | 推荐型号 | 关键参数 | 设计要点 |
|------|----------|----------|----------|
| DAC | PCM1794/AK4499 | SNR>120dB | 差分输出优 |
| I/V转换 | OPA1612/OPA2134 | THD<0.0001% | 精密电阻 |
| 低通滤波 | 二阶有源 | fc=100kHz | Butterworth |
| 线路驱动 | DRV134/SSM2142 | 驱动600Ω | 短路保护 |

#### Class-D功放链路
```
音频输入 → PWM调制器 → 栅极驱动 → MOSFET全桥 → LC低通 → 扬声器
```

| 器件 | 推荐型号 | 关键参数 | 设计要点 |
|------|----------|----------|----------|
| PWM调制器 | TAS5754/MA12070 | 效率>90% | EMI优化 |
| 栅极驱动 | UCC27201 | 4A驱动能力 | 死区时间设置 |
| MOSFET | CSD17570 | Rds_on<10mΩ | 热设计 |
| LC滤波 | 定制 | fc=30-50kHz | Zobel网络 |

### 1.5 数字接口设计

| 接口 | 用途 | 关键信号 | 设计要点 |
|------|------|----------|----------|
| **I2S** | 音频数据 | BCLK, LRCK, DATA | 匹配阻抗、等长走线 |
| **TDM** | 多通道音频 | TDM_CLK, TDM_FS, TDM_Dx | 时钟质量、信号完整性 |
| **I2C** | 控制 | SCL, SDA | 上拉电阻、总线电容 |
| **SPI** | 高速控制 | SCK, MOSI, MISO, CS | 速率匹配、CS时序 |
| **UART** | 调试/通信 | TX, RX | 波特率配置 |
| **USB** | 连接/供电 | D+, D-, VBUS | 阻抗90Ω、ESD保护 |
| **Ethernet** | 网络音频 | TX+, TX-, RX+, RX- | 差分阻抗、变压器 |

---

## 2. BOM管理规范

### 2.1 选型标准

**选型决策矩阵：**

| 评估维度 | 权重 | 评分标准 | 最低要求 |
|----------|------|----------|----------|
| 技术参数满足度 | 30% | 1-5分 | ≥4分 |
| 供应商质量评级 | 20% | A/B/C/D | ≥B级 |
| 交期稳定性 | 15% | 现货/4周/8周/12周+ | ≤8周 |
| 单价竞争力 | 15% | 与竞品对比 | ≤市场均价 |
| 替代料可用性 | 10% | pin-to-pin/功能替代/无 | 至少功能替代 |
| RoHS/REACH | 10% | 合规/有条件合规/不合规 | 必须合规 |

**分级管理：**
```yaml
component_classification:
  critical:
    definition: "影响核心功能、无直接替代料、长交期"
    examples: ["主DSP", "专用ADC/DAC", "定制变压器"]
    management: "安全库存≥3个月, 必须确定替代方案"
    approval_level: "技术总监+采购总监"
    
  important:
    definition: "影响功能性能、有替代料但需验证"
    examples: ["音频运放", "电源IC", "连接器"]
    management: "安全库存≥1个月, 替代料AVL内"
    approval_level: "硬件主管+采购经理"
    
  general:
    definition: "通用元器件、市场供应充足"
    examples: ["电阻", "电容", "二极管", "LED"]
    management: "标准库存管理"
    approval_level: "工程师自主"
```

### 2.2 替代料管理

```yaml
alternative_part_management:
  pin_to_pin:
    criteria: "封装相同、引脚兼容、功能兼容、寄存器兼容"
    verification: "读数据手册对比 + 样品测试"
    timeline: "2-4周"
    
  function_equivalent:
    criteria: "功能等效、性能满足需求、封装可兼容"
    verification: "原理图修改 + PCB适配 + 全功能测试"
    timeline: "4-8周"
    
  redesign_required:
    criteria: "功能等效但需要重新设计"
    verification: "完整设计变更流程 + 全项测试"
    timeline: "8-16周"
```

### 2.3 RoHS合规管理

| 物质 | 限值(ppm) | 管控级别 | 检测方法 |
|------|-----------|----------|----------|
| 铅 (Pb) | 1000 | A级 | XRF + 化学分析 |
| 汞 (Hg) | 1000 | A级 | 必须合规 |
| 镉 (Cd) | 100 | A级 | 必须合规 |
| 六价铬 | 1000 | A级 | 必须合规 |
| PBB | 1000 | B级 | 供应商声明 |
| PBDE | 1000 | B级 | 供应商声明 |
| 4种邻苯二甲酸酯 | 1000 each | B级 | 供应商声明 |

### 2.4 成本分级目标

| 产品等级 | BOM成本目标 | 关键件占比 | 目标毛利率 |
|----------|-------------|------------|------------|
| 入门级 | <$30 | 40% | 35% |
| 中端 | $30-80 | 45% | 40% |
| 高端专业 | $80-200 | 50% | 45% |
| 旗舰 | >$200 | 55% | 50% |

---

## 3. EMC设计规范

### 3.1 接地策略

**接地策略选择矩阵：**

| 系统类型 | 频率范围 | 推荐接地 | 理由 |
|----------|----------|----------|------|
| 纯模拟音频 | <100kHz | 单点接地 | 避免地环路噪声 |
| 混合模拟/数字 | <10MHz | 混合接地 | 分区单点+高频多点 |
| 数字为主 | >10MHz | 多点接地 | 最小化接地阻抗 |
| 含Class-D功放 | DC-100MHz | 分区接地+屏蔽 | 开关噪声隔离 |

**分区接地设计：**
```
┌─────────────────────────────────┐
│         机壳地 (Chassis)         │
│    ┌─────────┐  ┌─────────┐     │
│    │ 数字地  │  │ 模拟地  │     │
│    │ (DGND)  │  │ (AGND)  │     │
│    └────┬────┘  └────┬────┘     │
│         │ 单点连接    │          │
│         └──────┬─────┘          │
│              星型点              │
│         (靠近电源入口)           │
└─────────────────────────────────┘
```

### 3.2 屏蔽设计

| 屏蔽对象 | 屏蔽方式 | 材料 | 设计要求 |
|----------|----------|------|----------|
| Class-D功放 | 金属屏蔽罩 | 镀锡钢/铝 | 接地良好、缝隙<3mm |
| 开关电源 | 金属屏蔽罩 | 镀锡钢 | 输入/输出滤波在罩内 |
| 变压器 | 铜箔屏蔽 | 铜箔 | 单端接地、匝间屏蔽 |
| 敏感信号线 | 包地线 | 铜走线 | 两侧地线、过孔缝合 |
| 连接器 | 金属外壳 | 镀镍铜 | 360°接触机壳 |

### 3.3 滤波设计

**电源输入滤波：**
```
AC输入 → 保险丝 → 共模扼流圈 → X电容 → 共模电容 → 整流桥
              ↑_________________|
                    Y电容
```

| 滤波器类型 | 器件 | 参数 | 作用 |
|------------|------|------|------|
| 共模滤波 | 共模扼流圈 | 10mH-50mH | 抑制共模噪声 |
| 差模滤波 | X电容 | 0.1-0.47μF | 抑制差模噪声 |
| 共模滤波 | Y电容 | 1000-4700pF | 共模噪声到地 |
| π型滤波 | 电感+电容 | 10μH+100μF | DC电源纹波 |

### 3.4 EMC设计Checklist

**电源EMC：**
- [ ] 电源输入共模滤波器设计完成
- [ ] Y电容总和≤4700pF（漏电流限制）
- [ ] 整流二极管并联RC缓冲
- [ ] MOSFET/二极管有RC/Snubber
- [ ] 开关环路面积最小化
- [ ] 屏蔽罩多点接地

**信号EMC：**
- [ ] 高速信号线有端接电阻
- [ ] 时钟线有串联阻尼电阻
- [ ] 敏感模拟信号远离数字信号
- [ ] 所有信号线有完整回流路径
- [ ] I/O端口有TVS/ESD保护
- [ ] 连接器外壳接地

**结构EMC：**
- [ ] 机壳接缝导电连续性
- [ ] 通风孔尺寸<λ/20（最高频率）
- [ ] 显示屏有导电边框接地
- [ ] 按键/LED有ESD泄放路径

---

## 4. 热设计流程

### 4.1 功耗估算

**功耗估算模板：**
```yaml
power_budget:
  device: "Professional_Line_Array_Controller"
  total_input_power: "120W (24V/5A)"
  
  breakdown:
    - module: "DSP_Core"
      device: "ADSP-21569"
      voltage: "1.0V / 1.8V / 3.3V"
      current: "2.5A / 0.5A / 0.3A"
      power: "4.9W"
      thermal_design_power: "5.5W"
      
    - module: "Audio_ADC"
      device: "CS5368"
      voltage: "3.3VA / 3.3VD"
      current: "0.05A / 0.03A"
      power: "0.26W"
      
    - module: "Audio_DAC"
      device: "PCM5242"
      voltage: "3.3V"
      current: "0.05A"
      power: "0.17W"
      
    - module: "Class_D_Amplifier"
      device: "TAS5754M"
      voltage: "12V / 3.3V"
      current: "3A / 0.1A"
      power: "36.3W (含音频输出)"
      efficiency: "90%"
      dissipated_power: "3.6W"
      
    - module: "Power_Supply"
      device: "Buck converters + LDOs"
      efficiency: "85%"
      input_power: "120W"
      output_power: "100W"
      dissipated_power: "20W"
      
  total_dissipated_power: "~30W"
  max_ambient_temperature: "45°C"
```

### 4.2 散热方案

**散热方式选择：**

| 功耗范围 | 散热方式 | 热阻范围 | 适用场景 |
|----------|----------|----------|----------|
| <1W | 自然对流 | 50-100°C/W | 小信号器件 |
| 1-5W | 小型散热器 | 10-50°C/W | LDO、小功放 |
| 5-20W | 散热器+导热垫 | 3-10°C/W | 中大功放 |
| 20-50W | 强制风冷 | 1-3°C/W | 大功率设备 |
| >50W | 热管/液冷 | 0.5-1°C/W | 专业功放 |

**热设计计算：**
```
Tj = Ta + Pd × (Rjc + Rcs + Rsa)

其中:
  Tj: 结温 (°C)
  Ta: 环境温度 (°C)
  Pd: 功耗 (W)
  Rjc: 结到壳热阻 (°C/W) - 数据手册
  Rcs: 壳到散热器热阻 (°C/W) - 导热垫
  Rsa: 散热器到环境热阻 (°C/W) - 散热器规格

降额要求: Tj ≤ Tj_max × 0.8
```

### 4.3 热仿真设置

```yaml
thermal_simulation_setup:
  tool: "FloTHERM / Icepak"
  
  inputs:
    - pcb_geometry: "导入PCB文件"
    - component_power: "功耗预算表"
    - material_properties: "FR-4导热系数, 铜层厚度"
    - boundary_conditions: "环境温度, 风速(如强制风冷)"
    
  analysis_type:
    - steady_state: "稳态温度分布"
    - transient: "上电瞬态温升"
    
  outputs:
    - temperature_map: "PCB温度云图"
    - hot_spot_list: "热点列表(Tj排序)"
    - airflow_pattern: "气流分布（风冷时）"
```

---

## 5. 跨Agent协作接口

### 5.1 与DSP算法Agent协作

**接口名称**: `collab_dsp_agent`
**协作模式**: 双向协商

```yaml
# DSP算法Agent → 硬件设计Agent
dsp_constraints:
  trigger: "算法定点化规格确定"
  content:
    dsp_chip:
      model: "ADAU1467WBCPZ300"
      core_clock: "294.912MHz"
      required_voltage:
        - rail: "VDDIO"
          voltage: "3.3V ±5%"
          current_max: "300mA"
        - rail: "VDDCORE"
          voltage: "1.2V ±3%"
          current_max: "800mA"
      memory_requirement:
        data_ram: "320KB (internal)"
        external_ram: "optional 8MB SPI Flash"
      audio_interface:
        i2s_channels: 8
        sample_rate: "48kHz"
        word_length: 24
      peripheral:
        i2c: 2
        spi: 1
        uart: 1
    
    performance_budget:
      max_latency_ms: 5
      allocated_mips: 400
      
    timing_constraints:
      clock_jitter: "< 50ps RMS"
      power_up_sequence: "VDDIO first, then VDDCORE"

# 硬件设计Agent → DSP算法Agent
hw_feedback:
  trigger: "硬件设计反馈DSP约束"
  content:
    actual_implementation:
      power_supply:
        - rail: "3.3V"
          regulator: "TPS7A4700 (LDO)"
          noise: "4.7μVrms"
          headroom: "50%"
        - rail: "1.2V"
          regulator: "TPS54331 (Buck+LDO post)"
          noise: "10μVrms"
          headroom: "30%"
          
      clock_source:
        crystal: "12.288MHz"
        pll_multiplier: "24"
        actual_mclk: "294.912MHz"
        jitter_measured: "35ps RMS"
        
    constraints_on_dsp:
      available_mips: "380 (因电源裕量限制未超频)"
      memory_limitation: "external SPI Flash read speed 50MB/s"
      thermal_limit: "DSP Tj must < 100°C (ambient 45°C)"
```

### 5.2 与结构Agent协作

**接口名称**: `collab_mechanical_agent`
**协作模式**: 约束交换

```yaml
# 结构Agent → 硬件设计Agent
mechanical_constraints:
  trigger: "产品结构设计初步完成"
  content:
    pcb_envelope:
      max_size: "200mm × 150mm × 1.6mm"
      layer_count: "4层 (推荐) 或 6层"
      mounting_holes: "4 × M3, 角部"
      keepout_areas: ["USB端口区域", "散热孔区域"]
      
    connector_positions:
      - connector: "XLR输入 × 4"
        position: "后面板, 距左边缘20mm起"
        height_constraint: "距PCB底面<25mm"
      - connector: "XLR输出 × 4"
        position: "后面板, 距右边缘20mm起"
      - connector: "EtherCON"
        position: "后面板居中"
      - connector: "AC电源"
        position: "后面板, 带保险丝座"
        
    thermal:
      heat_sink_envelope: "80mm × 60mm × 30mm max"
      airflow_direction: "底部进, 顶部出"
      ambient_max: "45°C"
      
    material:
      enclosure: "铝合金型材 + 钣金"
      finish: "阳极氧化黑色"
      ip_rating: "IP20 (室内)"

# 硬件设计Agent → 结构Agent
hw_mounting_requirements:
  trigger: "原理图设计完成, 输出结构需求"
  content:
    component_height_profile:
      - height_range: "0-5mm"
        components: "SMD电阻电容"
      - height_range: "5-15mm"
        components: "电解电容, 变压器"
      - height_range: "15-30mm"
        components: "散热器, 连接器"
      - height_range: ">30mm"
        components: "大型电容, 继电器 (需确认)"
        
    keepout_requirements:
      - zone: "WiFi/BT天线区域"
        clearance: "≥10mm 净空"
        material: "非金属"
      - zone: "散热孔区域"
        size: "≥50cm² 有效通风面积"
        
    connector_access:
      - all_connectors: "从后面板接入"
      - led_indicators: "前面板可见"
      - user_controls: "顶部面板可触及"
      
    grounding:
      - chassis_ground_points: "至少4处, 靠近角部"
      - ground_impedance: "< 10mΩ"
```

### 5.3 与PCB Layout Agent协作

**接口名称**: `send_to_layout`
**协作模式**: 设计交付+约束输出

```yaml
schematic_delivery:
  trigger: "原理图冻结, 准备Layout"
  deliverables:
    netlist: "netlist.xml (Altium格式)"
    schematic_pdf: "schematic_v1.0.pdf"
    bom: "bom_v1.0.xlsx"
    
  layout_constraints:
    layer_stackup:
      layers: 4
      stack: "Top(Signal) - GND - PWR - Bottom(Signal)"
      copper_weight: "1oz outer, 0.5oz inner"
      
    placement_constraints:
      critical_components:
        - component: "U1_DSP"
          constraint: "居中放置, 靠近散热器"
          priority: 1
        - component: "U2_ClassD"
          constraint: "靠近输出连接器, 远离ADC"
          priority: 1
        - component: "Y1_Crystal"
          constraint: "靠近DSP时钟引脚, <10mm"
          priority: 2
          
    routing_constraints:
      critical_nets:
        - net: "I2S_*"
          constraint: "差分走线, 等长<2mm, 远离开关电源"
          width: "0.15mm"
        - net: "ANALOG_*"
          constraint: "包地, 最短路径, 远离数字信号"
          width: "0.2mm"
        - net: "VDD_CORE"
          constraint: "最短路径, 足够铜宽, 去耦电容<5mm"
          width: "0.5mm"
          
    impedance_control:
      - net_class: "USB"
        impedance: "90Ω ±10% differential"
      - net_class: "Ethernet"
        impedance: "100Ω ±10% differential"
        
    manufacturing:
      min_trace_width: "0.1mm"
      min_via_size: "0.2mm drill"
      component_clearance: "0.3mm"
```

### 5.4 与评审Agent协作

**接口名称**: `submit_for_review`
**协作模式**: 正式设计评审

```yaml
review_package:
  trigger: "设计完成, 自检通过"
  contents:
    system_architecture: "system_arch_v1.0.md"
    schematics: "schematic_v1.0.pdf + .SchDoc"
    simulation_reports:
      - "power_simulation.pdf"
      - "thermal_simulation.pdf"
      - "signal_integrity.pdf"
    bom: "bom_v1.0.xlsx"
    design_calculations: "calculations_v1.0.pdf"
    test_point_definition: "test_points_v1.0.xlsx"
    drc_erc_report: "checks_v1.0.pdf"
    emc_checklist: "emc_checklist_v1.0.md"
    derating_analysis: "derating_v1.0.xlsx"
    
  review_criteria:
    electrical:
      - 原理正确性
      - 参数计算准确性
      - 器件选型合理性
      - 信号完整性
      
    reliability:
      - 降额设计合规性
      - 热设计充分性
      - 保护电路完整性
      - MTBF预测
      
    manufacturability:
      - DFM合规性
      - 可测试性
      - 装配可行性
      - 成本控制
      
    compliance:
      - EMC预评估
      - 安全规范(CE/UL)
      - 环保合规(RoHS)
      - 文档完整性
```

---

## 6. 设计审查Checklist

### 6.1 电气安全审查

- [ ] 绝缘距离：初级-次级 ≥ 6mm (电气间隙)
- [ ] 爬电距离：≥ 8mm (污染等级2)
- [ ] 保险丝规格：额定电流 ≤ 电路最大承载电流的80%
- [ ] X/Y电容：Y电容总和漏电流 < 0.25mA
- [ ] 接地连续性：保护接地阻抗 < 0.1Ω
- [ ] 高压标识：>50V电路有明确警示
- [ ] 温升限制：可触及表面 < 60°C (持续接触)

### 6.2 信号完整性审查

- [ ] 所有高速信号有端接/阻尼
- [ ] 时钟信号最短路径, 有串联电阻
- [ ] 敏感模拟信号远离数字/开关信号
- [ ] 差分信号等长(长度差<2mm)
- [ ] 信号回流路径完整, 无跨分割
- [ ] 去耦电容靠近电源引脚(<5mm)
- [ ] 关键信号有测试点

### 6.3 电源完整性审查

- [ ] 电源网络铜宽满足电流要求
- [ ] 去耦电容数量满足芯片要求
- [ ] 多种电压间上电时序正确
- [ ] 电源纹波满足负载要求
- [ ] LDO压降(Vdropout)有裕量
- [ ] 热插拔保护(如适用)
- [ ] 欠压锁定(UVLO)设置合理

### 6.4 可靠性审查

- [ ] 所有器件满足降额规范
- [ ] 电解电容寿命满足产品寿命
- [ ] 连接器插拔寿命满足使用频率
- [ ] 机械应力考虑（振动、冲击）
- [ ] 环境适应性（温度、湿度、海拔）
- [ ] ESD保护所有用户可触及接口
- [ ] 浪涌保护电源输入和信号端口