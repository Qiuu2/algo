---
name: "AcousticSimulationAgent_Skill"
description: "声学仿真专家Agent的专业技能定义、工具使用规范、工作流与输入输出标准"
version: "1.0.0"
author: "ITC Enterprise Multi-Agent System"
---

# 声学仿真专家Agent - 技能定义 (Skill)

## 1. COMSOL Multiphysics 操作流程

### 1.1 完整操作链

```
几何建模 → 材料参数 → 边界条件 → 网格划分 → 求解 → 后处理 → 验证
```

### 1.2 步骤详解

#### Step 1: 几何建模 (Geometry)

| 子步骤 | 操作规范 | 检查点 |
|--------|----------|--------|
| 1.1 导入/创建 | 优先使用参数化CAD导入（STEP格式），本地创建仅用于概念验证 | 单位统一为mm |
| 1.2 简化清理 | 移除小圆角(<λ/20)、小孔、不影响声场的结构细节 | 记录所有简化操作 |
| 1.3 装配体设置 | 使用"形成装配"处理多体接触，定义接触对或一致对 | 检查接触面完整性 |
| 1.4 参数定义 | 所有关键尺寸参数化：频率f、单元间距d、箱体尺寸L/W/H | 参数表导出备份 |

**关键参数模板：**
```python
# COMSOL参数定义模板
f_min = 100[Hz]      # 最低分析频率
f_max = 10000[Hz]    # 最高分析频率
f_step = 100[Hz]     # 频率步进（低频密集）
c_air = 343[m/s]     # 声速
rho_air = 1.21[kg/m^3]  # 空气密度
d_elem = 0.1[m]      # 单元间距
N_elem = 8           # 单元数量
```

#### Step 2: 材料参数 (Materials)

| 材料类别 | 必需参数 | 数据来源 | 精度要求 |
|----------|----------|----------|----------|
| 空气 | ρ, c, μ, Cp, k | 内置材料+实测温度 | 温度补偿 |
| 扬声器振膜 | ρ, E, ν, η | 供应商数据+实测 | ±5% |
| 箱体材料（MDF） | ρ, E, ν, η | 实测或标准值 | ±10% |
| 吸音材料 | 流阻率σ, 孔隙率Φ, 曲折度α∞ | 阻抗管实测 | ±15% |
| 金属部件 | ρ, E, ν | 标准材料库 | ±3% |

**材料设置Checklist：**
- [ ] 所有域都分配了材料
- [ ] 材料参数单位正确
- [ ] 温度依赖性已考虑（如适用）
- [ ] 吸声材料使用多孔声学模型（Delany-Bazley/JCA）
- [ ] 材料参数来源已标注

#### Step 3: 边界条件 (Boundary Conditions)

| 边界类型 | 物理含义 | 适用位置 | 设置要点 |
|----------|----------|----------|----------|
| 平面波辐射 | 无反射出射 | 外边界 | 距离声源>λ/3 |
| 球面波辐射 | 无反射出射（球形边界） | 外边界（球形） | 圆心在声源区 |
| 硬声场边界 | 刚性壁，法向速度=0 | 地面、刚性壁面 | 默认边界 |
| 阻抗边界 | 有限阻抗表面 | 吸声处理表面 | Z = R + jX |
| 周期性边界 | 无限阵列近似 | 阵列单元边界 | 相位匹配条件 |
| 端口激励 | 指定入射波 | 波导入口 | 模式选择 |

**边界条件设置流程：**
```
1. 识别所有边界 → 2. 分类物理类型 → 3. 分配边界条件 → 4. 检查冲突 → 5. 参数化设置
```

#### Step 4: 网格划分 (Meshing)

**网格策略决策树：**
```
最高频率 f_max?
├── f_max ≤ 500Hz → 粗网格（λ/4），FEM/BEM均可
├── 500Hz < f_max ≤ 5000Hz → 中网格（λ/6-λ/8），FEM推荐
└── f_max > 5000Hz → 精细网格（λ/8-λ/12），或混合方法

几何复杂度?
├── 简单（规则体） → 结构化网格或扫掠网格
├── 中等 → 非结构化四面体 + 边界层
└── 复杂（细小特征） → 自适应网格 + 局部细化
```

**网格参数规范：**
| 参数 | 设置规则 | 验证方法 |
|------|----------|----------|
| 最大单元尺寸 | ≤ c / (f_max × 6) | 波长/单元数检查 |
| 边界层 | 3-5层，增长比1.2-1.3 | 边界层可视化检查 |
| 曲率因子 | 0.3-0.5 | 曲面网格质量 |
| 狭窄区域分辨率 | 1-2 | 狭缝/薄板区域 |

**网格质量检查标准：**
- 单元质量（COMSOL Skewness）> 0.1
- 长宽比 < 1000（边界层区域允许放宽）
- 网格-几何一致性检查无错误

#### Step 5: 求解 (Solver)

**求解器配置模板：**

```python
# 频域求解器设置
Study: Frequency Domain
Solver: MUMPS (直接求解器，推荐<100万DOF) / GMRES (迭代求解器)
  - 频率范围: range(f_min, f_step, f_max)
  - 参数化扫描: 角度θ（指向性分析）
  
# 求解器参数
Relative tolerance: 1e-6
Linearization method: Automatic
Adaptive mesh refinement: 关闭（手动控制网格）
```

**求解策略：**
| 问题规模 | 求解器 | 内存需求 | 预计时间 |
|----------|--------|----------|----------|
| < 50万 DOF | MUMPS直接求解 | 16-64GB | 分钟级 |
| 50-200万 DOF | MUMPS + 并行 | 64-256GB | 小时级 |
| > 200万 DOF | GMRES迭代 + 预处理器 | 64-512GB | 小时-天级 |

#### Step 6: 后处理 (Post-processing)

**标准输出列表：**
1. 声压级分布云图（SPL, dB ref 20μPa）
2. 声压频率响应曲线（特定点位）
3. 指向性图案（极坐标图）
4. 质点速度矢量图
5. 声强流线图
6. 频谱分析（FFT，时域仿真时）

**后处理参数：**
- 参考声压：20 μPa
- SPL计算公式：20×log10(|p|/p_ref)
- 频率轴：对数坐标
- 平滑：1/3倍频程或1/12倍频程

#### Step 7: 验证 (Verification)

**三级验证体系：**
1. **数值验证**: 网格无关性检查（3级网格对比，差异<3%）
2. **物理验证**: 与理论解析解对比（基准case，差异<5%）
3. **实验验证**: 与实测数据对比（如有，差异目标<±3dB）

---

## 2. 阵列指向性仿真流程

### 2.1 线性阵列仿真

```
输入: 单元数量N, 间距d, 单元类型, 频率范围, 目标覆盖角
  ↓
Step 1: 建立阵列几何模型（参数化）
  ↓
Step 2: 设置单元激励（幅值+相位）
  ↓
Step 3: 远场计算设置（边界/域）
  ↓
Step 4: 参数化扫描（频率+角度）
  ↓
Step 5: 计算指向性因子DI、Q值
  ↓
Step 6: 波束控制仿真（加权+相位延迟）
  ↓
输出: 指向性图案、DI频率曲线、波束宽度曲线、加权效果对比
```

**线性阵列参数模板：**
```
N_elements = [4, 8, 16]        # 单元数扫描
spacing_d = [0.05, 0.10, 0.15] # 间距扫描（m）
steering_angle = [-30, -15, 0, 15, 30] # 波束指向角（度）
window_types = ['Uniform', 'Hanning', 'Hamming', 'Dolph-Chebyshev']
```

**关键计算公式：**
- 阵列因子：AF(θ) = Σ w_n × exp[-jknd(sinθ - sinθ_0)]
- 指向性指数：DI = 10×log10(Q)，Q = 2 / ∫|D(θ)|²sinθ dθ
- -6dB波束宽度：BW_6dB ≈ 0.89 × λ/(Nd) × 180/π（均匀加权）

### 2.2 环形阵列仿真

| 参数 | 说明 | 典型范围 |
|------|------|----------|
| 环半径R | 阵列环半径 | 0.1-0.5m |
| N | 单元数量（均布） | 4-16 |
| 单元指向 | 径向向外/切向/倾斜 | 依设计 |
| 激励模式 | 同相/相位递进/模式合成 | 依应用 |

**环形阵列输出：**
- 水平面全向性评估（全向偏差[dB]）
- 垂直面指向性
- 模式合成效果（定向/全向切换）

### 2.3 波束控制仿真

**波束控制参数扫描矩阵：**
```
频率: 100Hz, 250Hz, 500Hz, 1kHz, 2kHz, 4kHz, 8kHz
波束角: -60°, -45°, -30°, -15°, 0°, 15°, 30°, 45°, 60°
加权函数: 均匀, Hanning, Hamming, Blackman, Dolph-Chebyshev(SLL=-20dB/-30dB)
```

**输出指标：**
- 主瓣宽度 (-3dB, -6dB)
- 最大旁瓣电平 (SLL)
- 波束指向精度偏差
- 阵列增益（ vs 单单元）
- 波束控制频率上限（栅瓣出现频率）

---

## 3. 房间声学仿真流程

### 3.1 完整流程

```
Step 1: 几何导入
  └── 接收CAD建筑模型（Revit/Rhino/SketchUp导出）
  └── 简化：保留房间轮廓、座椅区、主要反射面
  └── 声学化处理：将装饰面映射为吸声/反射/扩散边界

Step 2: 材料吸声系数赋值
  └── 查阅材料吸声系数数据库
  └── 按频率赋值：125/250/500/1k/2k/4k Hz
  └── 处理缺失数据：插值或默认值+灵敏度分析

Step 3: 射线追踪设置
  └── 设置射线数量：≥10,000条（统计收敛）
  └── 设置反射次数：≥100次（直达声能量<1%停止）
  └── 设置接收面：听音区域网格化
  └── 设置时间分辨率：1ms或更细

Step 4: RIR计算
  └── 运行射线追踪
  └── 能量时间曲线 (ETC) 生成
  └── 房间脉冲响应 (RIR) 合成
  └── 考虑空气吸收（温度+湿度）

Step 5: 声学参数提取
  └── T20/T30混响时间
  └── EDT早期衰减时间
  └── C50/C80清晰度指数
  └── D50清晰度百分比
  └── STI语言传输指数
  └── LF侧向能量因子
  └── SPL分布均匀度

Step 6: 结果评估与优化建议
  └── 与目标标准对比（IEC/ANSI/客户规范）
  └── 问题区域识别
  └── 声学处理优化建议
```

### 3.2 材料吸声系数参考表

| 材料 | 125Hz | 250Hz | 500Hz | 1kHz | 2kHz | 4kHz |
|------|-------|-------|-------|------|------|------|
| 混凝土（裸露） | 0.01 | 0.01 | 0.02 | 0.02 | 0.03 | 0.03 |
| 石膏板（轻钢龙骨） | 0.15 | 0.10 | 0.06 | 0.05 | 0.04 | 0.04 |
| 矿棉板（25mm） | 0.20 | 0.40 | 0.70 | 0.80 | 0.85 | 0.80 |
| 玻璃纤维（50mm，背后空腔） | 0.30 | 0.60 | 0.85 | 0.95 | 0.95 | 0.90 |
| 地毯（厚绒） | 0.05 | 0.10 | 0.30 | 0.50 | 0.60 | 0.70 |
| 软包座椅（空置） | 0.20 | 0.25 | 0.35 | 0.40 | 0.40 | 0.40 |
| 软包座椅（ occupied） | 0.30 | 0.35 | 0.45 | 0.55 | 0.55 | 0.55 |
| 穿孔金属板（背后吸声） | 0.20 | 0.50 | 0.80 | 0.50 | 0.30 | 0.20 |

---

## 4. 输入参数规范

### 4.1 几何文件格式

| 格式 | 适用场景 | 版本要求 | 注意事项 |
|------|----------|----------|----------|
| STEP (.step/.stp) | 通用3D CAD交换 | AP214/AP242 | 推荐首选格式 |
| IGES (.iges/.igs) |  legacy系统兼容 | 5.3 | 曲面质量检查 |
| COMSOL (.mphbin) | 原生格式 | 5.6+ | 保留参数化信息 |
| STL (.stl) | 仅用于可视/参考 | - | 不包含参数信息，仅辅助 |

### 4.2 材料数据格式

```json
{
  "material_id": "mineral_wool_50mm",
  "name": "矿棉板 50mm",
  "type": "porous_absorber",
  "parameters": {
    "flow_resistivity": 15000,
    "porosity": 0.95,
    "tortuosity": 1.1,
    "viscous_length": 50e-6,
    "thermal_length": 100e-6,
    "thickness": 0.05
  },
  "absorption_coefficients": {
    "125Hz": 0.35,
    "250Hz": 0.70,
    "500Hz": 0.90,
    "1000Hz": 0.95,
    "2000Hz": 0.95,
    "4000Hz": 0.90
  },
  "source": "ITC_material_db_v3.2",
  "uncertainty": "±15%"
}
```

### 4.3 边界条件模板

```json
{
  "boundary_condition_id": "bc_radiation_outer",
  "type": "plane_wave_radiation",
  "boundaries": ["outer_sphere"],
  "parameters": {
    "wave_number_expression": "2*pi*f/acda.c",
    "spherical": false
  },
  "applicable_frequency_range": [50, 20000],
  "notes": "外边界辐射条件，距离声源>λ/3"
}
```

---

## 5. 输出报告模板

### 5.1 仿真报告标准结构

```markdown
# 声学仿真报告

## 1. 项目信息
- 项目名称、任务编号、版本、日期
- 仿真工程师（Agent标识）
- 软件版本（COMSOL x.x.x）

## 2. 仿真目标
- 任务书要求概述
- 关键性能指标 (KPIs)

## 3. 模型描述
- 3.1 几何描述（尺寸、关键特征）
- 3.2 材料参数（表格+来源）
- 3.3 边界条件（图示+说明）
- 3.4 网格信息（类型、数量、质量统计）
- 3.5 求解器设置

## 4. 验证结果
- 4.1 网格无关性验证
- 4.2 基准case验证（如有）
- 4.3 与实测数据对比（如有）

## 5. 仿真结果
- 5.1 频响曲线
- 5.2 指向性图案
- 5.3 SPL分布图
- 5.4 THD/非线性分析（如适用）
- 5.5 关键发现

## 6. 不确定度分析
- 6.1 不确定度来源识别
- 6.2 不确定度预算表
- 6.3 灵敏度分析结果

## 7. 结论与建议
- 7.1 主要结论
- 7.2 设计优化建议
- 7.3 风险提示

## 8. 附录
- 8.1 完整参数表
- 8.2 补充图表
- 8.3 原始数据文件索引
```

### 5.2 关键图表规范

**频响曲线图：**
- X轴: 频率 (Hz)，对数刻度，20Hz-20kHz
- Y轴: SPL (dB)，线性刻度，范围自适应
- 标注: 目标曲线、容差带(±3dB)、关键频率点
- 分辨率: 1/12倍频程或更细

**指向性图案：**
- 极坐标图，0°在前，顺时针
- 多频率叠加 (250/500/1k/2k/4k/8k Hz)
- 标注 -6dB覆盖角
- 标准化至轴向 (0dB)

**SPL分布图：**
- 2D/3D彩色云图
- 标注 max/min/average 值
- 均匀度指标 ΔSPL = max - min

---

## 6. 跨Agent协作接口

### 6.1 与CAD接口Agent协作

**接口名称**: `collab_cad_agent`
**协作模式**: 请求-响应

```yaml
request_geometry:
  trigger: "仿真任务启动，需要几何模型"
  request_format:
    task_id: "T-2024-001"
    required_geometry:
      type: "speaker_array_assembly"
      level_of_detail: "acoustic_sim"  # 声学仿真级简化
      critical_dimensions: ["diaphragm_d", "box_L", "box_W", "box_H", "port_d", "port_L"]
      format: "STEP"
      version_control: true
    deadline: "2024-01-15T10:00:00Z"
  
  response_format:
    geometry_file: "path/to/model.step"
    simplification_log: "path/to/simp_log.md"
    parameters_table: "path/to/params.csv"
    version: "v1.2"
    checksum: "sha256:abc123..."

validation_rules:
  - 检查几何完整性（无破面、无干涉）
  - 检查单位（必须为mm或m）
  - 检查关键尺寸与任务书一致
  - 检查简化不影响声学关键特征
```

### 6.2 与MATLAB Agent协作

**接口名称**: `collab_matlab_agent`
**协作模式**: 数据推送+结果拉取

```yaml
# 声学仿真Agent → MATLAB Agent（后处理请求）
send_postprocess_request:
  trigger: "COMSOL求解完成，需要高级数据分析"
  data_package:
    raw_data_file: "simulation_result.mph"
    export_points: "measurement_points.csv"
    analysis_requirements:
      - type: "frequency_response_smoothing"
        method: "1/3_octave"
      - type: "directivity_index_calculation"
        method: "IEC_60268-16"
      - type: "statistical_analysis"
        confidence_level: 0.95
      - type: "waterfall_plot"
        time_window: "T20"
  
  expected_delivery:
    processed_curves: "processed_fr.csv"
    di_values: "di_results.json"
    statistical_report: "stat_report.md"
    plots: ["smoothed_fr.png", "waterfall.png"]

# MATLAB Agent → 声学仿真Agent（反馈）
receive_analysis_feedback:
  trigger: "MATLAB分析完成"
  validation:
    - 检查数据处理一致性
    - 检查统计方法正确性
    - 整合至仿真报告
```

### 6.3 与DSP算法Agent协作

**接口名称**: `send_acoustic_constraints`
**协作模式**: 主动推送

```yaml
acoustic_constraints_package:
  trigger: "阵列指向性仿真完成，输出声学约束"
  content:
    array_config:
      type: "linear"
      n_elements: 8
      spacing_mm: 100
      element_type: "4inch_fullrange"
    
    directivity_constraints:
      frequency_range: [100, 10000]
      coverage_angle_6dB:
        "1000Hz": 60  # ±30°
        "4000Hz": 30  # ±15°
      max_sll_dB: -12  # 最大旁瓣电平
      beam_steering_range: [-30, 30]  # 可波束控制范围
      min_beamwidth_hz: 2000  # 波束控制有效频率下限
    
    spl_constraints:
      max_spl_1m_dB: 110  # 最大输出声压级
      sensitivity_dB: 92   # 灵敏度 (1W/1m)
      
    transfer_function:
      file: "array_transfer_function.csv"  # 频率响应数据
      notes: "用于DSP EQ补偿的目标曲线"
  
  update_frequency: "设计变更时主动推送，常规任务完成后推送"
```

### 6.4 与评审Agent协作

**接口名称**: `submit_for_review`
**协作模式**: 正式交付

```yaml
review_package:
  trigger: "仿真完成，自检通过"
  contents:
    report: "simulation_report.md"
    raw_data: 
      - "frequency_response.csv"
      - "directivity_data.csv"
      - "spl_distribution.csv"
    plots:
      - "fr_curve.png"
      - "polar_plots.png"
      - "spl_map.png"
    model_files:
      - "simulation_model.mph"
    verification:
      - "mesh_convergence_check.md"
      - "benchmark_validation.md"
    metadata:
      task_id: "T-2024-001"
      agent_version: "1.0.0"
      simulation_date: "2024-01-15"
      compute_time_hours: 4.5
  
  review_criteria:
    - 物理合理性检查
    - 方法论正确性检查
    - 结果完整性检查
    - 不确定度评估充分性
    - 报告规范性检查
```

---

## 7. 仿真验证流程

### 7.1 与实测数据对比流程

```
Step 1: 实测数据采集条件记录
  └── 消声室/现场环境条件
  └── 测量设备（麦克风、信号源、DAQ）
  └── 测量点位（与仿真点位对应）
  
Step 2: 数据对齐
  └── 频率轴对齐（采样率、FFT参数统一）
  └── 幅值归一化（激励条件一致化）
  └── 点位位置确认
  
Step 3: 对比分析
  └── 计算差异曲线：ΔSPL(f) = SPL_sim(f) - SPL_meas(f)
  └── 统计指标：RMS误差、最大偏差、偏差频率分布
  └── 容差评估：是否在±3dB范围内
  
Step 4: 偏差归因
  └── 系统性偏差 → 检查模型假设
  └── 频率相关偏差 → 检查材料参数、边界条件
  └── 随机偏差 → 检查测量重复性
  
Step 5: 模型修正（如需）
  └── 根据偏差分析调整模型
  └── 重新验证
  └── 记录修正历史
```

### 7.2 网格无关性验证

**验证标准模板：**

| 网格级别 | 单元数 | 最大尺寸 | 目标频段结果 | 与上级网格偏差 |
|----------|--------|----------|--------------|----------------|
| 粗网格 (Coarse) | N_c | λ/4 | SPL_c(f) | - |
| 中网格 (Medium) | N_m ≈ 3N_c | λ/6 | SPL_m(f) | |SPL_m - SPL_c| |
| 细网格 (Fine) | N_f ≈ 8N_c | λ/8-λ/12 | SPL_f(f) | |SPL_f - SPL_m| |

**收敛判定：**
- 中网格 vs 细网格偏差 < 3% → 中网格结果可接受
- 偏差 3-5% → 采用细网格结果，注明收敛程度
- 偏差 > 5% → 继续细化网格或检查模型问题

---

## 8. 工具使用规范

### 8.1 COMSOL操作日志
- 所有操作通过LiveLink for MATLAB/Python脚本记录
- 参数变更自动记录至版本控制
- 求解过程日志保存（收敛历史、内存使用）

### 8.2 计算资源管理
| 任务类型 | CPU核心 | 内存 | GPU | 预估时间 |
|----------|---------|------|-----|----------|
| 基准验证 (低频) | 4 | 32GB | - | <1h |
| 全频段指向性 | 16 | 128GB | - | 4-8h |
| 房间声学射线追踪 | 8 | 64GB | - | 2-4h |
| 多物理场耦合 | 32 | 256GB | - | 8-24h |

### 8.3 文件管理规范
```
project/
├── 01_geometry/           # 几何文件
├── 02_models/             # COMSOL模型文件
│   ├── baseline/          # 基准模型
│   ├── refined/           # 细化模型
│   └── archive/           # 归档版本
├── 03_materials/          # 材料参数
├── 04_results/            # 仿真结果
│   ├── raw_exports/       # 原始导出数据
│   ├── processed/         # 处理后数据
│   └── plots/             # 图表
├── 05_reports/            # 报告
├── 06_validation/         # 验证数据
└── README.md              # 项目索引
```

<!--
================================================================================
本段落为「声学仿真专家Agent」skill.md 的增补章节。
插入位置：作为 skill.md 的新增顶层章节（建议置于「仿真方法论」之后、
          「标准产出物」相关章节之前）。
版本：MATLAB 工具能力 v1.0.0
依据：MATLAB R2026a + Phased Array System Toolbox / Signal Processing Toolbox /
      Audio Toolbox，经 MathWorks 官方文档逐函数核验（2026-05）。
================================================================================
-->

# N. MATLAB 仿真执行能力 (MATLAB Execution Capability)

> **本章是声学仿真Agent的"执行之手"。MATLAB 不是一个独立角色，而是本Agent
> 调用的工具层能力之一，与 COMSOL / BEM 求解器并列。本Agent对一切经由
> MATLAB 产出的结果负全部物理责任——工具只负责算，物理判断永远由本Agent承担。**

## N.1 能力定位与边界

| 属性 | 说明 |
|------|------|
| **接入方式** | MATLAB MCP Core Server（MathWorks 官方，stdio transport，user scope 全局生效） |
| **MATLAB 版本** | R2026a (Linux glnxa64) |
| **已装工具箱** | Phased Array System Toolbox / Signal Processing Toolbox / Audio Toolbox |
| **工作目录** | `~/matlab-agent/`（MCP `--initial-working-folder` 限定，文件读写集中此处） |
| **显示模式** | `nodesktop`（后台运行，图形以文件落盘，不弹 GUI） |
| **调用权限** | 默认每次执行需人类批准；本Agent不得绕过批准机制 |

### N.1.1 本能力可做什么

- 线阵 / 面阵 / 任意几何阵列的指向性建模（`phased.ULA` / `phased.URA` / `phased.ConformalArray`）
- 波束宽度、旁瓣电平、指向性指数（DI）的定量计算
- 加权窗（Dolph-Chebyshev / Taylor / Hamming / Hanning）效果对比
- 栅瓣分析、阵元间距扫描（d-sweep）
- 阵元误差 / 装配公差的蒙特卡洛灵敏度分析（`phased.ULA` 的 `Taper` + 扰动注入）
- 极坐标图、频率-角度瀑布图、SPL 切面图的脚本化生成

### N.1.2 本能力不做什么（边界声明）

| 不做 | 原因 | 应转交 |
|------|------|--------|
| 复杂腔体内的三维声场 FEM | Phased Array Toolbox 是阵列工具，非有限元 | COMSOL 流程 |
| 箱体声-固耦合、热黏性声学 | 同上 | COMSOL 流程 |
| 定点化 / 滤波器系数实现 | 属 DSP 领域职责 | DSP算法Agent |
| 实测数据的最终判读权 | 实测是裁决者，仿真是被告 | 本Agent解读，但不可用仿真否定实测 |

## N.2 强制性物理正确性规则（违反即结果作废）

> 以下规则源自 MATLAB Phased Array Toolbox 在**声学场景**下的已知陷阱。
> 每一条都对应一个会导致"数值正确、物理全错"的真实错误。本Agent在任何
> MATLAB 阵列脚本中必须逐条满足，并在脚本头部以注释显式声明已满足。

### N.2.1 传播速度必须显式设为声速 —— 最高优先级

```
风险：Phased Array Toolbox 所有函数的 PropagationSpeed 默认值为光速
      （physconst('LightSpeed') ≈ 3e8 m/s）。若不改，全部波束计算偏差
      约 6 个数量级，结果完全无意义。
规则：所有 pattern / beamwidth / directivity / SteeringVector 调用，
      必须显式传入 PropagationSpeed = c，其中 c = 343（20°C 空气，标准）
      或 c = 340（工程常用）。本项目统一取 c = 343 m/s，并在脚本中
      注明温度假设。
自检：脚本中每一处阵列计算调用，grep 'PropagationSpeed' 必须命中。
```

### N.2.2 阵元间距与采样定理 —— 栅瓣边界

```
风险：当 d ≥ λ 时出现栅瓣（grating lobe），波束图出现伪主瓣。
规则：每次建模必须计算并报告栅瓣临界频率 f_grating = c / d，
      并声明工作频段上限是否安全（本项目 d=55mm → f_grating ≈ 6.2kHz，
      4kHz 工作上限安全；此结论须每次几何变更后重算）。
自检：报告中必须出现 d/λ 比值表与栅瓣临界频率。
```

### N.2.3 测量口径必须与实测一致 —— 可对比性

```
风险：仿真 BW 与竞品实测 BW 若定义不同（-3dB vs -6dB、方位面 vs
      俯仰面、插值方法差异），对比无意义。
规则：本项目波束宽度统一采用 -6dB（半功率点常用 -3dB，但本项目对标
      竞品消声室数据采用 -6dB 口径，须在每份报告首页声明）。
      beamwidth() 调用必须显式 dBDown=6。
自检：与实测对比的每个频率点，须标注口径来源。
```

### N.2.4 阵元指向性假设必须声明

```
风险：默认各向同性阵元（isotropic）会高估宽角度性能；真实 2 寸全频
      喇叭有自身指向性。
规则：基准模型可用 IsotropicAntennaElement 快速验证；与实测对标时，
      须改用 CosineAntennaElement 或导入实测喇叭指向性，并声明所用
      阵元模型及其对结果的影响方向。
自检：报告"模型描述"章节须明确阵元类型。
```

## N.3 标准建模流程（对齐 soul.md「先建基准，逐步细化」）

```
Step 1  基准验证（isotropic + 理论解对比）
  └── 建 phased.ULA，isotropic 阵元，均匀加权
  └── 与解析式 BW ≈ 0.886·λ/(N·d)·(180/π) 对比，偏差须 <5%
  └── 通过后方可进入 Step 2，否则脚本/参数有误，禁止细化

Step 2  加权窗引入（Dolph-Chebyshev -20dB）
  └── Taper = chebwin(N, 20)，重算 BW 与 SLL
  └── 确认 SLL 收敛至设计目标（-20dB），主瓣展宽幅度合理

Step 3  真实阵元 + 公差（与实测对标）
  └── 替换为 CosineAntennaElement / 实测指向性
  └── 蒙特卡洛注入阵元幅度±1dB、相位±5°、位置±0.5mm
  └── 输出最坏 5% 工况下的 BW 分布

Step 4  结果验证与报告
  └── 与竞品实测逐频率点对比，口径一致
  └── 不确定度评估（阵元模型 / 公差 / 数值三来源）
  └── 提交 Critic
```

## N.4 经核验的函数骨架（语法基线）

> 以下骨架经 MathWorks R2026a 官方文档核验。本Agent可据此扩展，但不得
> 引入未经验证的函数名。**严禁凭记忆杜撰 API**（参见 memory.md 教训：
> 曾因杜撰论文标题、误记芯片主频踩坑）。

```matlab
% ---- 声学线阵指向性基准脚本骨架（经官方文档核验）----
c   = 343;            % 声速 m/s（20°C 空气）—— N.2.1 强制
N   = 16;             % 阵元数
d   = 0.055;          % 阵元间距 m（d=55mm 竞品基准几何）
fc  = 2000;           % 评估频率 Hz

% 阵元：基准用各向同性，对标实测时改 CosineAntennaElement —— N.2.4
elem = phased.IsotropicAntennaElement;

% Dolph-Chebyshev -20dB 加权（Taper 即加权窗）—— Step 2
w = chebwin(N, 20);

array = phased.ULA('NumElements', N, ...
                   'ElementSpacing', d, ...
                   'Element', elem, ...
                   'Taper', w);

% -6dB 波束宽度（口径与实测一致）—— N.2.3
% 注意 PropagationSpeed 显式传声速 —— N.2.1
bw = beamwidth(array, fc, 'dBDown', 6, 'PropagationSpeed', c);

% 栅瓣临界频率 —— N.2.2
f_grating = c / d;    % 须报告并判断工作频段是否安全

% 指向性图（落盘，不弹窗）—— nodesktop 模式
fig = figure('Visible','off');
pattern(array, fc, -180:180, 0, ...
        'PropagationSpeed', c, ...
        'CoordinateSystem','polar', ...
        'Type','powerdb');
exportgraphics(fig, fullfile('~/matlab-agent','pattern_2kHz.png'), ...
               'Resolution', 200);
```

## N.5 可复现性要求（对齐 soul.md「结果可复现」）

| 要求 | 落实方式 |
|------|----------|
| **参数化脚本驱动** | 所有几何/频率/加权参数置于脚本头部变量区，杜绝硬编码散落 |
| **随机种子固定** | 涉及蒙特卡洛时 `rng(<固定值>)`，种子写入报告 |
| **环境记录** | 报告须记 MATLAB 版本、工具箱版本、`ver` 输出、脚本文件名与哈希 |
| **图表脚本化** | 禁止手动画图；一律 `exportgraphics` 落盘，文件名含频率与日期 |
| **数据落盘** | 波束图原始数据同步导出 CSV，供 Critic 复核与与实测对齐 |
| **脚本归档** | `.m` 脚本提交至项目版本控制，与报告同 commit |

## N.6 MATLAB 产出的自检 Checklist（提交 Critic 前必过）

- [ ] **N.2.1** 每处阵列计算均显式传 `PropagationSpeed=343`？（grep 验证）
- [ ] **N.2.2** 已报告 d/λ 与栅瓣临界频率，并判断工作频段安全？
- [ ] **N.2.3** 波束宽度口径为 -6dB，且与实测对比口径一致并声明？
- [ ] **N.2.4** 阵元模型类型已声明，其对结果的影响方向已说明？
- [ ] **Step 1** 基准模型已与解析解对比，偏差 <5%？
- [ ] 蒙特卡洛随机种子已固定并记录？
- [ ] 所有函数名均经官方文档核验，无杜撰 API？
- [ ] 脚本、图、CSV、报告四件套齐全且版本一致？
- [ ] 仿真结果若与实测冲突，是否默认先怀疑仿真而非实测？

## N.7 与实测冲突时的强制立场

> 源自本项目真实教训（d=55 仿真 1kHz=29.3° vs 竞品实测 16°）。

```
当 MATLAB 仿真结果与竞品消声室实测数据冲突时：
  1. 默认实测为权威基准，仿真为待证假设（不可用仿真否定实测）
  2. 排查顺序：口径定义 → 阵元模型 → 加权/几何参数 → 数值设置
  3. 若排查后仍冲突，须提出"竞品可能采用了本方未建模的技术"假设
     （如超指向 superdirectivity），并量化该假设下的预期偏差
  4. 任何"仿真比实测更可信"的结论，必须经 Critic + 人类CTO 双重确认
```

---

*MATLAB Execution Capability v1.0.0 — The Hand of the Acoustic Simulation Agent*
*工具负责算，物理判断永远由本Agent承担。*
