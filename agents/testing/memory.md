---
name: Testing & Validation Agent Memory
description: |
  测试验证专家Agent的可积累专业知识记忆、项目经验库、偏好设置。
  包含测试用例库、历史测试数据、缺陷模式库和测试设备清单。
version: 1.0.0
author: ITC Enterprise Agent System
---

# Memory: 测试验证专家 Agent

## 记忆架构

```yaml
memory_system:
  长期记忆 (Persistent):
    - 测试用例库 (Test Case Library)
    - 历史测试数据 (Historical Data)
    - 缺陷模式库 (Defect Pattern Library)
    - 测试设备清单 (Equipment Inventory)
    - 个人偏好设置 (Preferences)
    
  短期记忆 (Session):
    - 当前测试批次信息
    - 活跃测试任务
    - 待处理缺陷
    
  工作记忆 (Working):
    - 当前测量数据
    - 实时分析结果
    - 临时判定记录
```

---

## 记忆1: 测试用例库 `MEM-TST-001`

### 按产品类型分类

#### 有源音箱 (Active Speaker) 测试集

```yaml
product_type: "有源监听音箱"
test_suite_id: "TS-ACT-001"
total_cases: 156

category_breakdown:
  audio_performance: 32
  acoustic_measurement: 24
  electrical_safety: 18
  environmental: 28
  mechanical: 16
  functionality: 22
  user_interface: 16

key_test_cases:
  - case_id: "TC-ACT-001"
    title: "频率响应 - 全频带平坦度"
    priority: P1
    method: "APx对数扫频，1W@4Ω等效"
    spec: "20Hz-20kHz ±3dB (ref 1kHz)"
    automation: true
    last_updated: "2024-03-01"
    
  - case_id: "TC-ACT-015"
    title: "最大SPL - 长期功率"
    priority: P1
    method: "粉红噪声IEC标准谱，1m测量"
    spec: "≥95dB SPL continuous, THD<3%"
    automation: false  # 需人工监控
    last_updated: "2024-02-15"
    
  - case_id: "TC-ACT-032"
    title: "功放保护功能 - 过热保护"
    priority: P1
    method: "温箱+持续额定功率驱动"
    spec: "保护触发温度≤85°C，恢复后功能正常"
    automation: true
    notes: "需在温箱内放置热电偶监控"
    last_updated: "2024-01-20"
```

#### 蓝牙音箱 (Bluetooth Speaker) 测试集

```yaml
product_type: "便携式蓝牙音箱"
test_suite_id: "TS-BT-001"
total_cases: 198

special_tests:
  - case_id: "TC-BT-045"
    title: "蓝牙连接稳定性 - 距离测试"
    priority: P1
    method: "开阔场地，距离递增10m至50m"
    spec: "10m内无断连，音质无劣化"
    automation: false
    
  - case_id: "TC-BT-067"
    title: "电池续航 - 50%音量"
    priority: P1
    method: "粉红噪声@50%音量，持续播放至关机"
    spec: "≥12小时 (标称值)"
    automation: true
    notes: "需满充起始，环境温度25°C"
    
  - case_id: "TC-BT-089"
    title: "防水测试 - IPX7浸泡"
    priority: P1
    method: "1m水深，30分钟浸泡"
    spec: "功能正常，内部无水侵入"
    automation: false
    notes: "仅最终验证执行，非每轮"
```

#### Soundbar 测试集

```yaml
product_type: "Soundbar"
test_suite_id: "TS-SB-001"
total_cases: 142

special_tests:
  - case_id: "TC-SB-023"
    title: "HDMI ARC/eARC 音频回传"
    priority: P1
    method: "连接TV HDMI ARC口，验证音频回传"
    spec: "PCM/Dolby Digital/DTS支持"
    automation: false
    
  - case_id: "TC-SB-031"
    title: "虚拟环绕声效果"
    priority: P2
    method: "主观+MUSHRA客观评估"
    spec: "环绕感评分≥60分 (MUSHRA)"
    automation: false
    notes: "需训练听音员参与"
    
  - case_id: "TC-SB-042"
    title: "壁挂结构强度"
    priority: P1
    method: "壁挂架安装，施加3倍产品重量载荷"
    spec: "无变形/松动，24h持续"
    automation: true
```

### 按测试类型分类

| 测试类型 | 用例数 | 自动化率 | 平均执行时间 |
|----------|--------|----------|-------------|
| 音频性能 | 85 | 92% | 30min/样品 |
| 声学测量 | 62 | 75% | 2h/样品 (含消声室) |
| 环境可靠性 | 48 | 40% |  varies (1h~10days) |
| 电气安全 | 35 | 85% | 15min/样品 |
| 机械结构 | 28 | 60% | varies |
| 功能/接口 | 52 | 80% | 20min/样品 |
| 用户体验 | 24 | 20% | 30min/样品 |

---

## 记忆2: 历史测试数据 `MEM-TST-002`

### 基准性能数据库

```yaml
baseline_database:
  description: "各产品类型的性能基准，用于新项目目标设定和对比"
  
  active_speaker_5inch:
    product_reference: "5寸二分频有源监听"
    sample_size: 50
    measurement_date: "2023-Q4"
    
    frequency_response:
      mean_20hz_20khz_deviation: 2.1  # dB, RMS
      std_dev: 0.4
      worst_case: 2.9
      best_case: 1.2
      
    thd_n_1w_1khz:
      mean: 0.065  # %
      std_dev: 0.015
      worst_case: 0.098
      best_case: 0.038
      
    dynamic_range:
      mean: 98.5  # dB A-weighted
      std_dev: 1.2
      worst_case: 95.8
      best_case: 101.2
      
    snr_a_weighted:
      mean: 96.2  # dB
      std_dev: 1.5
      worst_case: 93.0
      best_case: 99.5
      
    max_spl_1m:
      mean: 102.0  # dB SPL
      std_dev: 1.8
      worst_case: 98.5
      best_case: 105.3

  bluetooth_portable:
    product_reference: "便携蓝牙音箱 (中端)"
    sample_size: 80
    measurement_date: "2023-Q4"
    
    frequency_response:
      mean_100hz_10khz_deviation: 3.5
      std_dev: 0.6
      
    thd_n_1w_1khz:
      mean: 0.12
      std_dev: 0.03
      
    battery_life_50pct:
      mean: 14.2  # hours
      std_dev: 0.8
      worst_case: 12.5
      
    bluetooth_range:
      mean: 18.5  # meters (开阔)
      std_dev: 3.2
```

### 常见问题分布

```yaml
common_issues_distribution:
  source: "2022-2024年所有项目缺陷统计"
  total_defects_analyzed: 347
  
  by_module:
    - module: "音频通路"
      count: 98
      percentage: 28.2%
      top_issues:
        - "底噪偏高: 32例"
        - "频响高频跌落: 24例"
        - "左右平衡超差: 18例"
        - "THD低频超标: 15例"
        - "其他: 9例"
        
    - module: "结构/装配"
      count: 76
      percentage: 21.9%
      top_issues:
        - "密封不良导致声学性能漂移: 28例"
        - "装配应力导致PCB变形: 19例"
        - "螺钉松动: 15例"
        - "外观缺陷: 14例"
        
    - module: "电子硬件"
      count: 65
      percentage: 18.7%
      top_issues:
        - "电源纹波超标: 22例"
        - "功放芯片过热保护: 18例"
        - "元件参数漂移: 15例"
        - "接地噪声: 10例"
        
    - module: "软件/固件"
      count: 58
      percentage: 16.7%
      top_issues:
        - "DSP滤波器系数错误: 20例"
        - "蓝牙连接稳定性: 17例"
        - "音量控制非线性: 12例"
        - "其他: 9例"
        
    - module: "环境可靠性"
      count: 32
      percentage: 9.2%
      top_issues:
        - "高温后频响漂移: 12例"
        - "湿热后绝缘下降: 11例"
        - "振动后松动: 9例"
        
    - module: "其他"
      count: 18
      percentage: 5.2%

  by_severity:
    Critical: 12.4%
    High: 31.1%
    Medium: 38.9%
    Low: 17.6%
    
  lesson: "音频通路问题占比最高(28%)，建议新项目加强前期音频设计评审和仿真验证。密封问题值得特别关注，占结构问题的37%。"
```

---

## 记忆3: 缺陷模式库 `MEM-TST-003`

### 按模块分类

#### 音频通路缺陷模式

```yaml
defect_pattern: "DP-AUD-001"
name: "底噪偏高 — 接地回路问题"
frequency: "常见 (12例/3年)"
severity: "High"

symptoms:
  - "静音时耳机可闻嗡嗡声"
  - "SNR比规格低5-15dB"
  - "噪声频谱有50/100Hz峰值"
  
root_causes:
  - "数字地与模拟地分割不当 (40%)"
  - "电源地线太长/太细 (30%)"
  - "变压器漏磁耦合 (20%)"
  - "PCB布局接地环路 (10%)"
  
detection_methods:
  - "SNR测试 (AUD-004)"
  - "噪声频谱分析 (50/100/150Hz检查)"
  - "近场探头扫描"
  
prevention:
  - "硬件Agent: 星型接地设计规则检查"
  - "PCB布局评审: 地平面完整性验证"
  
fix_verification:
  - "SNR改善>10dB"
  - "50Hz成分<-80dB (相对满幅)"
  
tags: ["底噪", "接地", "SNR", "音频通路"]
```

```yaml
defect_pattern: "DP-AUD-002"
name: "频响高频跌落 — 分频器/扬声器问题"
frequency: "常见 (10例/3年)"
severity: "High"

symptoms:
  - ">10kHz频响较设计目标低3-6dB"
  - "听感偏暗、细节不足"
  
root_causes:
  - "分频器电容值偏差 (35%)"
  - "高音扬声器灵敏度低于规格 (25%)"
  - "箱体内部吸音过多 (20%)"
  - "测量条件不一致 (15%)"
  - "DSP EQ未正确补偿 (5%)"
  
detection: "频响测试 (AUD-001) — >10kHz区域"
prevention: "声学Agent: 分频器容差分析; 来料检验: 高音单元灵敏度100%检测"
fix_verification: "15kHz点频响恢复到规格范围内"
```

#### 结构缺陷模式

```yaml
defect_pattern: "DP-STR-001"
name: "密封不良 — 倒相管调谐偏移"
frequency: "非常常见 (18例/3年)"
severity: "Critical"

symptoms:
  - "低频下潜与规格偏差±5-10Hz"
  - "批次间低频一致性差"
  - "气密性测试泄漏率超标"
  
root_causes:
  - "密封垫压缩率不一致 (35%)"
  - "螺钉扭矩不均 (25%)"
  - "密封沟槽尺寸超差 (20%)"
  - "材料老化/变形 (15%)"
  - "装配工艺未标准化 (5%)"
  
detection:
  - "气密性测试 (±200Pa)"
  - "阻抗曲线对比 (fs偏移检测)"
  - "批次频响一致性检查"
  
prevention: "结构Agent: 卡扣设计替代螺钉; 气密性100%测试; 密封圈来料检验"
```

### 缺陷严重度定义

| 级别 | 定义 | 示例 | 响应时间 |
|------|------|------|----------|
| Critical | 安全/法规风险，或核心功能完全失效 | 绝缘击穿、过热起火、完全无声 | 24小时 |
| High | 主要性能超标，用户体验显著下降 | THD超标3倍、频响超差>6dB、密封失效 | 3天 |
| Medium | 次要性能偏离，特定条件下触发 | 串扰略超规格、外观轻微缺陷 | 7天 |
| Low | 不影响功能的微小偏差 | 标签歪斜、非操作面轻微划痕 | 下版本 |

---

## 记忆4: 测试设备清单 `MEM-TST-004`

### 音频测试设备

```yaml
equipment_id: "EQ-APX-001"
name: "Audio Precision APx515"
model: "APx515"
serial_number: "AP515-2023-0847"
location: "音频测试室-A"
status: "可用"

capabilities:
  - "2通道模拟输入/输出"
  - "24bit/192kHz"
  - "THD+N residual: <-105dB"
  - "幅度精度: ±0.03dB"
  - "频率精度: ±2ppm"

calibration:
  last_calibrated: "2024-01-15"
  cal_interval_months: 12
  next_due: "2025-01-15"
  cal_certificate: "CAL-2024-0156"
  cal_lab: "计量中心"
  
maintenance:
  last_maintenance: "2024-02-20"
  maintenance_interval_months: 6
  issues: []
  
usage_stats:
  total_test_runs: 2347
  uptime_percentage: 98.5
  average_daily_usage_hours: 6.2
  
access_control: "测试Agent + 授权操作员"
```

```yaml
equipment_id: "EQ-MIC-001"
name: "B&K 测量传声器"
model: "4190"
serial_number: "3198765"
location: "消声室"
status: "可用"

calibration:
  last_calibrated: "2024-02-01"
  cal_interval_months: 12
  next_due: "2025-02-01"
  
notes: "配对使用4190型，左右位置固定"
```

### 环境测试设备

```yaml
equipment_id: "EQ-ENV-001"
name: "恒温恒湿箱"
model: "ESPEC SH-642"
serial_number: "ESH-2022-0042"
location: "环境实验室"
status: "可用"

capabilities:
  temperature_range: "-40°C ~ +150°C"
  humidity_range: "20% ~ 98%RH"
  internal_size: "600×600×700mm"
  
calibration:
  last_calibrated: "2024-03-01"
  cal_interval_months: 12
  next_due: "2025-03-01"
```

```yaml
equipment_id: "EQ-VIB-001"
name: "振动试验台"
model: "LDS V875"
serial_number: "LDS-2021-0089"
location: "振动实验室"
status: "维修中 (预计2024-04-01恢复)"

capabilities:
  force_rating: "55kN"
  frequency_range: "5-3000Hz"
  max_displacement: "76mm"
  
maintenance:
  current_issue: "功率放大器故障，待更换部件"
  expected_recovery: "2024-04-01"
  backup_plan: "外协至SUP-TEST-001进行振动测试"
```

### 设备可用性矩阵

| 设备ID | 名称 | 状态 | 下次校准 | 日均可用 | 备注 |
|--------|------|------|----------|----------|------|
| EQ-APX-001 | APx515 | 可用 | 2025-01 | 6h | — |
| EQ-APX-002 | APx525 | 可用 | 2024-09 | 4h | 备用 |
| EQ-MIC-001 | B&K 4190 | 可用 | 2025-02 | 8h | 消声室 |
| EQ-ENV-001 | 恒温恒湿箱 | 可用 | 2025-03 | 16h | 24h连续 |
| EQ-VIB-001 | 振动台 | 维修中 | 2024-08 | 0h | 4月恢复 |
| EQ-DROP-001 | 跌落机 | 可用 | 2024-12 | 4h | — |

---

## 记忆5: 个人偏好设置 `MEM-PREF-001`

```yaml
preferences:
  test_philosophy: "数据说话，规格为准"
  
  default_test_conditions:
    temperature: 23  # °C
    humidity: 50     # %RH
    warm_up_time: 30  # minutes
    settling_time: 5  # seconds between measurements
    
  measurement_practices:
    repeat_count: 3  # 关键测量重复3次
    outlier_handling: "Grubbs检验，α=0.05"
    averaging_method: "median (比mean更鲁棒)"
    uncertainty_reporting: "k=2 (95%置信)"
    
  automation_preferences:
    language: "Python 3.11+"
    test_framework: "pytest"
    code_style: "PEP 8 + black格式化"
    doc_style: "Google docstring"
    
  reporting:
    default_format: "Markdown + PDF"
    chart_style: "白色背景, 无网格线, 清晰标注"
    color_scheme: "Pass=绿色, Fail=红色, Marginal=橙色"
    
  risk_tolerance:
    spec_margin: "目标值在规格限的70%范围内 (Cpk>1.33)"
    new_product: "保守策略，全量测试"
    mature_product: "优化策略，风险导向抽样"
    
  shortcuts:
    - "快速SNR检查: 1kHz 1W → A-weighted noise floor → 计算"
    - "THD快速趋势: 只看1kHz@1W和100Hz@rated_power"
    - "频响一眼判断: 1kHz归一化后看20Hz/20kHz两点"
    - "密封快速检查: 阻抗曲线fs偏移<2Hz = OK"
```

---

## 记忆更新机制

```yaml
update_rules:
  测试用例库:
    trigger: "新产品类型/新测试需求/用例优化"
    frequency: "每项目更新"
    review: "项目经理Agent月度评审"
    
  历史测试数据:
    trigger: "每批次测试完成"
    frequency: "实时追加"
    responsible: "自动写入数据库Agent"
    retention: "7年 (产品生命周期+法规)"
    
  缺陷模式库:
    trigger: "新缺陷根因分析完成"
    frequency: "每缺陷更新"
    validation: "8D报告完成后确认"
    
  设备清单:
    trigger: "设备新增/维修/校准/报废"
    frequency: "实时更新"
    responsible: "设备管理Agent协作"
    
archival:
  test_data_compression: "1年后原始数据归档 (低频访问)"
  defect_data_retention: "永久保留"
  equipment_history: "设备全生命周期"
  
  backup:
    frequency: "每日增量"
    retention: "30天增量 + 12月全量"
    location: "本地 + 云端"
```
