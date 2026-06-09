---
name: Structure Engineer Agent Memory
description: |
  结构设计与机械工程专家Agent的可积累专业知识记忆、项目经验库、偏好设置。
  包含材料数据库、设计案例、供应商信息和公差分析经验。
version: 1.0.0
author: ITC Enterprise Agent System
---

# Memory: 结构设计与机械工程专家 Agent

## 记忆架构

```yaml
memory_system:
  长期记忆 (Persistent):
    - 材料数据库 (Materials DB)
    - 设计案例库 (Case Library)
    - 供应商数据库 (Supplier DB)
    - 公差经验库 (Tolerance DB)
    - 个人偏好设置 (Preferences)
    
  短期记忆 (Session):
    - 当前项目上下文
    - 活跃协作状态
    - 待处理事项
    
  工作记忆 (Working):
    - 当前设计参数
    - 最近的计算结果
    - 临时决策记录
```

---

## 记忆1: 材料数据库 `MEM-MAT-001`

### 概述
结构Agent的核心知识资产，记录所有使用过和评估过的材料性能数据，支持快速选型决策。

### 数据库结构

```yaml
material_record:
  material_id: "MAT-ABS-001"
  commercial_name: "ABS TOYOLAC 100"
  manufacturer: "Toray"
  category: "热塑性塑料"
  
  mechanical_properties:
    density_g_cm3: 1.04
    tensile_strength_mpa: 47
    flexural_strength_mpa: 72
    flexural_modulus_mpa: 2300
    izod_impact_j_m: 200
    hardness_rockwell_r: 110
    
  thermal_properties:
    heat_deflection_temp_c: 88
    vicat_softening_temp_c: 100
    mold_temp_range_c: [50, 80]
    melt_temp_range_c: [220, 260]
    linear_expansion_coefficient: 9.5e-5
    
  acoustic_properties:
    damping_factor: 0.018
    sound_transmission_loss_db: 22  # 2mm厚度@1kHz
    internal_loss_factor: 0.02
    
  processability:
    primary_process: "注塑"
    mold_shrinkage_pct: 0.5
    min_wall_thickness_mm: 1.0
    max_wall_thickness_mm: 4.0
    draft_angle_min_deg: 0.5
    surface_finish_options: ["镜面", "细纹", "粗纹", "喷漆"]
    secondary_operations: ["超声波焊接", "粘接", "喷漆", "电镀"]
    
  cost_data:
    price_per_kg_usd: 2.8
    relative_cost_index: 1.0  # 基准
    MOQ_kg: 500
    lead_time_days: 14
    
  supplier_info:
    primary_supplier: "SUP-PLAS-001"
    alternative_suppliers: ["SUP-PLAS-003", "SUP-PLAS-008"]
    
  usage_history:
    projects: ["PRJ-2201", "PRJ-2305", "PRJ-2312"]
    total_usage_kg: 2500
    performance_rating: 4.2  # 5分制
    issues: 
      - "PRJ-2305: 批次间色差>ΔE1.5，需加强来料检验"
      
  tags: ["通用级", "注塑", "中低成本", "良好加工性"]
  last_updated: "2024-03-15"
```

### 常用材料速查表

| 材料ID | 名称 | 类型 | 密度 | E模量 | 阻尼 | 成本指数 | 最佳应用 |
|--------|------|------|------|-------|------|----------|----------|
| MAT-ABS-001 | ABS 100 | 注塑塑料 | 1.04 | 2.3GPa | 0.018 | 1.0 | 通用外壳 |
| MAT-ABP-001 | ABS+PC T85XF | 注塑塑料 | 1.12 | 2.5GPa | 0.025 | 1.4 | 高强度外壳 |
| MAT-PC-001 | PC 2405 | 注塑塑料 | 1.20 | 2.4GPa | 0.015 | 1.6 | 透明件/耐冲击 |
| MAT-PA6G-001 | PA6+GF30 | 注塑塑料 | 1.35 | 7.5GPa | 0.030 | 2.0 | 高刚度结构件 |
| MAT-AL6-001 | 6061-T6 | 铝合金 | 2.70 | 69GPa | 0.001 | 3.5 | 金属外壳/散热器 |
| MAT-AL5-001 | 5052-H32 | 铝合金 | 2.68 | 70GPa | 0.001 | 2.8 | 钣金件 |
| MAT-MDF-001 | MDF 18mm | 木质板材 | 0.75 | 3.0GPa | 0.050 | 0.6 | 原型/木质箱体 |
| MAT-HDF-001 | HDF 12mm | 木质板材 | 0.90 | 4.0GPa | 0.040 | 0.8 | 高端箱体 |
| MAT-CFRP-001 | T300/环氧树脂 | 碳纤维复材 | 1.60 | 70GPa | 0.020 | 15.0 | 旗舰级/特殊应用 |
| MAT-TPE-001 | TPE 60A | 弹性体 | 0.95 | 0.005GPa | 0.080 | 3.0 | 密封件/减震垫 |
| MAT-EPDM-001 | EPDM 65 | 橡胶 | 1.15 | 0.003GPa | 0.100 | 2.5 | 密封圈/垫片 |

### 材料选型历史记录

```yaml
selection_history:
  - project: "PRJ-2401-旗舰监听音箱"
    decision: "主体用ABS+PC(T85XF)，内部支架用PA6+GF30"
    reasoning: "外壳需要良好表面质量+足够刚度，内部支架需要高刚度支撑扬声器"
    alternatives_considered: ["全铝合金", "PC+玻纤"]
    outcome: "满足性能，成本在预算内"
    
  - project: "PRJ-2403-便携蓝牙音箱"
    decision: "全ABS+硅胶包胶"
    reasoning: "轻量化、防跌落、低成本量产"
    alternatives_considered: ["PP+TPU", "铝合金+硅胶"]
    outcome: "跌落测试通过，成本优于预算15%"
    
  - project: "PRJ-2405-专业低音炮"
    decision: "MDF箱体+内部铝合金加强框"
    reasoning: "大箱体需要MDF的高阻尼特性，铝合金框提供安装刚度"
    alternatives_considered: ["全HDF", "桦木多层板"]
    outcome: "箱体共振控制优秀，一阶模态185Hz(略低但可接受)"
```

---

## 记忆2: 典型结构设计案例库 `MEM-CASE-001`

### 成功案例

#### Case-S-001: 密闭式监听音箱箱体设计

```yaml
case_id: "Case-S-001"
project: "PRJ-2305-近场监听音箱"
product_type: "5寸二分频有源监听音箱"
status: "success"

requirements:
  - 内部容积: 8.5L (中低音腔)
  - 一阶模态: > 250Hz
  - 质量: < 4.5kg (单体)
  - 成本目标: 结构件 < $25/台
  
design_solution:
  material: "ABS+PC T85XF, 壁厚3mm"
  structure: "前后面板+中框三段式，内部放射加强筋"
  speaker_mount: "一体化安装面，厚5mm，6个M4螺孔"
  sealing: "前后面板超声波焊接 + 密封垫"
  
key_parameters:
  wall_thickness: 3.0mm
  rib_height: 8mm (主筋) / 5mm (辅筋)
  rib_thickness_top: 1.2mm
  rib_thickness_root: 2.0mm
  internal_volume_actual: 8.42L (-0.9%)
  first_mode: 268Hz
  total_weight: 4.2kg
  structure_cost: $22/台

lessons_learned:
  - "放射加强筋对扬声器安装面刚度提升显著，面内变形<0.05mm@50W"
  - "中框设计简化模具，前后对称可共用一套模具(不同镶件)"
  - "超声波焊接参数: 频率20kHz, 时间0.8s, 压力0.4MPa — 需DOE优化"
  - "教训: 初版筋位过密导致缩水痕，V2将筋间距从15mm增加到22mm解决"

rating:
  overall: 4.5/5
  would_reuse: true
  tags: ["密闭式", "监听音箱", "ABS+PC", "超声波焊接"]
```

#### Case-S-002: 倒相式蓝牙音箱设计

```yaml
case_id: "Case-S-002"
project: "PRJ-2312-户外蓝牙音箱"
product_type: "便携防水蓝牙音箱"
status: "success"

requirements:
  - 内部容积: 0.8L
  - 调谐频率: 85Hz
  - 防护等级: IP67
  - 质量: < 600g
  - 跌落: 1.5m水泥地
  
design_solution:
  material: "主体ABS+TPE二次注塑(包胶)"
  structure: "上下壳体+密封圈，倒相管一体成型"
  port_design: "圆形倒相管D18mm×L35mm，管口圆角R3"
  waterproof: "双密封圈(外圈IP67+内圈声学密封)，螺钉防锈处理"
  shockproof: "四角TPE加厚(3mm)，内部橡胶减震柱"
  
key_parameters:
  port_diameter: 18mm
  port_length: 35mm
  tuning_frequency_actual: 83Hz (-2.4%)
  weight: 580g
  ip_test: "IP67通过"
  drop_test: "1.5m通过"

lessons_learned:
  - "倒相管一体成型避免后装密封问题，但模具复杂度增加"
  - "TPE包胶厚度需≥1.5mm才有有效缓冲，四角增至3mm"
  - "双密封圈设计: 外圈硅胶(耐UV)+内圈EPDM( acoustic seal)"
  - "教训: 初版倒相管出口在底部，桌面放置时阻塞 → 改到背面"

rating:
  overall: 4.3/5
  would_reuse: true
  tags: ["倒相式", "蓝牙音箱", "防水", "TPE包胶", "跌落防护"]
```

### 失败案例分析

#### Case-F-001: 薄壁金属箱体共振问题

```yaml
case_id: "Case-F-001"
project: "PRJ-2210-超薄 soundbar"
product_type: "壁挂式soundbar"
status: "failure_analyzed"

failure_description: "铝合金箱体(1.2mm)一阶模态仅128Hz，与低音单元(3寸)工作频率重叠，导致129Hz处异常峰值(+4.5dB)"

root_cause:
  - "壁厚过薄，为追求外观纤薄牺牲刚度"
  - "内部缺少加强结构，大片平板区域"
  - "FEM分析时边界条件设置过于理想，未考虑实际安装"
  
corrective_action:
  - "壁厚增至1.8mm，内部增加2条纵向加强筋(高6mm)"
  - "扬声器安装区局部增厚至3mm+放射筋"
  - "重新FEM: 一阶模态提升至198Hz(仍偏低但可用)"
  - "最终方案改为铝合金+内部塑料支架复合结构"

lesson: "金属箱体不能仅靠材料刚度，必须设计内部加强结构。大面积平板是共振隐患。FEM边界条件应模拟实际安装状态。"

tags: ["soundbar", "铝合金", "共振", "教训", "薄壁"]
```

#### Case-F-002: 密封不良导致倒相管失谐

```yaml
case_id: "Case-F-002"
project: "PRJ-2301-桌面音箱"
product_type: "4寸倒相式桌面音箱"
status: "failure_analyzed"

failure_description: "量产批次间低频下潜不一致(±8Hz)，部分产品倒相管调谐频率偏移"

root_cause:
  - "前后面板螺丝连接，扭矩不一致导致密封压力不均匀"
  - "密封垫压缩率批次差异(10%-30%)"
  - "无气密性测试，泄漏未被发现"
  
corrective_action:
  - "改为卡扣+密封圈设计，消除扭矩变量"
  - "密封圈规格标准化，来料100%压缩率检验"
  - "增加气密性测试工序(±200Pa, 泄漏率<0.5Pa/s)"
  - "产线增加扭力扳手校准(每周)"

lesson: "声学密封不能依赖螺钉紧固的一致性。卡扣或焊接提供更稳定的密封。必须增加气密性测试。"

tags: ["密封", "倒相式", "量产一致性", "教训", "气密性"]
```

---

## 记忆3: 供应商/加工商数据库 `MEM-SUP-001`

### 注塑供应商

```yaml
supplier_id: "SUP-PLAS-001"
name: "精密塑料科技"
category: "注塑加工"
location: "东莞"
capabilities:
  machine_range: "80T-650T"
  precision_grade: "±0.05mm (精密级)"
  max_part_size: "600×400×300mm"
  special_processes: ["双色注塑", "埋入成型", "气辅注塑"]
  materials_experienced: ["ABS", "PC", "ABS+PC", "PA", "PBT", "TPE"]
  
certifications: ["ISO 9001", "IATF 16949"]
quality_rating: 4.3/5  # 基于历史交货质量
delivery_rating: 4.0/5
price_rating: 3.8/5  # 5=最便宜

contact_info:
  primary_contact: "张工程师"
  quote_response_time: "3个工作日"
  typical_lead_time: "T1: 25天, 量产: 15天"

history:
  projects: ["PRJ-2201", "PRJ-2305", "PRJ-2312", "PRJ-2401"]
  issues: 
    - "2023-Q2: 交期延迟10天(模具修改沟通不足)"
  strengths:
    - "复杂模具经验丰富"
    - "尺寸稳定性好"
    
tags: ["注塑", "精密", "华南", "复杂模具"]
status: "approved"
last_evaluation: "2024-01-15"
```

### CNC加工供应商

```yaml
supplier_id: "SUP-CNC-001"
name: "铝合金精密加工"
category: "CNC加工"
location: "深圳"
capabilities:
  machine_type: "3轴/4轴/5轴 CNC"
  materials: ["铝合金", "不锈钢", "铜", "工程塑料"]
  tolerance: "±0.02mm"
  max_workpiece: "1000×600×400mm"
  surface_finish: ["阳极氧化", "喷砂", "拉丝", "PVD"]
  
certifications: ["ISO 9001"]
quality_rating: 4.5/5
delivery_rating: 4.2/5
price_rating: 3.5/5

history:
  projects: ["PRJ-2208", "PRJ-2210", "PRJ-2405"]
  
tags: ["CNC", "铝合金", "精密", "表面处理"]
status: "approved"
last_evaluation: "2024-02-20"
```

### 快速原型供应商

```yaml
supplier_id: "SUP-RP-001"
name: "3D打印服务中心"
category: "快速原型"
location: "本地"
capabilities:
  processes: ["SLA", "SLS", "FDM", "SLM(金属)"]
  materials: ["光敏树脂", "尼龙", "ABS", "铝合金"]
  tolerance: "±0.1mm (SLA), ±0.2mm (SLS)"
  lead_time: "2-5天"
  
pricing:
  sla_resin: "¥3-5/cm³"
  sls_nylon: "¥4-6/cm³"
  slm_aluminum: "¥15-25/cm³"

history:
  projects: ["PRJ-2305-V1原型", "PRJ-2312-V1/V2原型"]
  
tags: ["3D打印", "快速原型", "本地"]
status: "approved"
```

### 供应商评级矩阵

| 供应商ID | 质量 | 交期 | 价格 | 服务 | 综合 | 状态 |
|----------|------|------|------|------|------|------|
| SUP-PLAS-001 | 4.3 | 4.0 | 3.8 | 4.2 | 4.08 |  Approved |
| SUP-PLAS-002 | 4.0 | 3.5 | 4.2 | 3.8 | 3.88 |  Approved |
| SUP-PLAS-003 | 4.5 | 4.3 | 3.2 | 4.5 | 4.13 |  Preferred |
| SUP-CNC-001 | 4.5 | 4.2 | 3.5 | 4.0 | 4.05 |  Approved |
| SUP-CNC-002 | 3.8 | 4.5 | 4.0 | 3.5 | 3.95 |  Approved |
| SUP-RP-001 | 4.2 | 4.8 | 3.5 | 4.3 | 4.20 |  Preferred |

---

## 记忆4: 公差分析经验库 `MEM-TOL-001`

### 公差设计规则

```yaml
tolerance_design_rules:
  general_tolerance:
    plastic_injection: "ISO 2768-m 或 GB/T 14486 MT3"
    metal_cnc: "ISO 2768-f 或 ±0.05mm"
    metal_sheet: "ISO 2768-m 或 ±0.1mm"
    die_casting: "GB/T 6414 CT5-CT6"
    
  critical_dimensions:
    speaker_mounting:
      hole_position: "±0.1mm (影响扬声器对中)"
      hole_diameter: "+0.05/-0.0mm (螺钉间隙)"
      mounting_surface_flatness: "0.05mm"
      
    sealing:
      groove_width: "±0.1mm"
      groove_depth: "±0.1mm"
      sealing_surface_flatness: "0.1mm"
      
    acoustic:
      internal_volume: "±3% (影响调谐)"
      port_diameter: "±0.2mm"
      port_length: "±0.5mm"
      
    assembly:
      shell_gap: "0.15±0.1mm (外观间隙)"
      shell_flush: "0±0.1mm (外观段差)"
      screw_hole_alignment: "±0.2mm"
```

### 公差累积分析案例

```yaml
case_id: "TOL-001"
description: "soundbar上下壳体装配间隙累积"
dimensions_chain:
  - element: "上壳体高度"
    nominal: 45.0
    tolerance: "±0.2"
    contribution: "±0.2"
    
  - element: "密封垫厚度"
    nominal: 1.5
    tolerance: "±0.15"
    contribution: "±0.15"
    
  - element: "PCB+扬声器堆高"
    nominal: 28.0
    tolerance: "±0.3"
    contribution: "±0.3"
    
  - element: "下壳体深度"
    nominal: 16.0
    tolerance: "±0.2"
    contribution: "±0.2"

analysis:
  method: "RSS (Root Sum Square)"
  total_tolerance: "±0.47mm"
  worst_case: "±0.85mm"
  design_gap: "0.5±0.3mm"
  
result: "RSS分析通过，最坏情况间隙可能为0(下公差)或1.35(上公差)，需调整设计间隙至0.8±0.3"

lesson: "多塑料件+软质密封垫的公差累积需用RSS方法，最坏情况往往不可接受。设计间隙应≥总公差RSS值。"
```

### 常用配合标准

| 配合类型 | 塑料-塑料 | 塑料-金属 | 金属-金属 | 应用场景 |
|----------|-----------|-----------|-----------|----------|
| 间隙配合 | H7/g6 → 0.1-0.3mm | H7/f7 → 0.1-0.2mm | H7/g6 | 滑动/定位 |
| 过渡配合 | H7/k6 → 0-0.15mm | H7/k6 → 0-0.1mm | H7/k6 | 定位/轻压入 |
| 过盈配合 | H7/p6 → 0.1-0.3mm | H7/p6 → 0.05-0.15mm | H7/p6 | 紧固/密封 |
| 螺钉间隙 | M3: 3.2±0.1 | M3: 3.2±0.05 | M3: 3.2±0.05 | 紧固安装 |
| 定位销 | 3±0.015 | 3±0.01 | 3±0.008 | 精确定位 |

---

## 记忆5: 个人偏好设置 `MEM-PREF-001`

```yaml
preferences:
  cad_software: "SolidWorks"  # 首选
  cad_alternative: "Creo"
  
  default_material:
    housing: "ABS+PC T85XF"
    internal_bracket: "PA6+GF30"
    sealing: "EPDM 65"
    grommet: "TPE 60A"
    
  design_defaults:
    wall_thickness_plastic: 2.5  # mm
    wall_thickness_metal: 1.5    # mm
    min_draft_angle: 1.0         # degree
    default_rib_height: 3.0      # × wall thickness
    default_screw_size: "M3"     # 标准螺钉
    
  quality_thresholds:
    min_dfm_score: 85
    min_fem_quality_score: 95
    max_first_mode_freq: 200     # Hz minimum
    max_weight_deviation: 10     # % from target
    
  communication:
    preferred_language: "中文技术文档，英文术语保留"
    report_format: "Markdown + PDF"
    update_frequency: "每日进度+里程碑详细报告"
    
  shortcuts:
    - "快速估算壁厚: 扬声器直径/50 (塑料), /80 (金属)"
    - "加强筋高度: 壁厚的3倍"
    - "密封沟槽宽度: O型圈线径+0.2mm"
    - "螺钉间距: 密封区域≤30mm，结构区域≤60mm"
```

---

## 记忆更新机制

```yaml
update_rules:
  材料数据库:
    trigger: "新材料使用/材料测试数据更新"
    frequency: "每项目更新"
    responsible: "本Agent + 测试Agent数据输入"
    
  案例库:
    trigger: "项目完成(成功或失败)"
    frequency: "每项目更新"
    review: "项目经理Agent季度评审"
    
  供应商数据库:
    trigger: "新供应商评估/供应商绩效变化"
    frequency: "季度更新"
    responsible: "采购Agent协作"
    
  公差库:
    trigger: "新公差问题发现/测量数据积累"
    frequency: "持续更新"
    validation: "测量Agent数据验证"
    
archival:
  retention_period: "7年 (符合行业法规)"
  compression: "2年以上项目归档为只读"
  backup: "每日增量备份，每周全量备份"
```
