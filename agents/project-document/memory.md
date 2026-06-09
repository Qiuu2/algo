---
name: Project Document & Knowledge Management Agent Memory
description: |
  技术文档与知识管理专家Agent的可积累专业知识记忆、项目经验库、偏好设置。
  包含文档模板库、知识库目录结构、术语词典和文档质量历史数据。
version: 1.0.0
author: ITC Enterprise Agent System
---

# Memory: 技术文档与知识管理专家 Agent

## 记忆架构

```yaml
memory_system:
  长期记忆 (Persistent):
    - 文档模板库 (Document Template Library)
    - 知识库目录结构 (Knowledge Base Directory)
    - 术语词典 (Terminology Dictionary)
    - 文档质量历史 (Document Quality History)
    - 个人偏好设置 (Preferences)
    
  短期记忆 (Session):
    - 当前处理文档列表
    - 待审校文档队列
    - 活跃查询请求
    
  工作记忆 (Working):
    - 当前编辑文档
    - 临时格式转换缓存
    - 待入库条目
```

---

## 记忆1: 文档模板库 `MEM-DOC-001`

### 模板注册表

```yaml
template_registry:
  version: "2024-v3.0"
  last_updated: "2024-03-15"
  
  templates:
    - id: "TPL-DOC-001"
      name: "设计文档模板"
      category: "技术文档"
      applicable_to: ["结构设计", "声学设计", "硬件设计", "软件设计"]
      version: "v2.1"
      last_modified: "2024-02-01"
      fields_count: 25
      required_fields: 20
      usage_count: 156
      avg_quality_score: 87
      
    - id: "TPL-DOC-002"
      name: "测试报告模板"
      category: "测试文档"
      applicable_to: ["音频测试", "环境测试", "功能测试"]
      version: "v2.0"
      last_modified: "2024-01-15"
      fields_count: 18
      required_fields: 15
      usage_count: 203
      avg_quality_score: 89
      
    - id: "TPL-DOC-003"
      name: "会议纪要模板"
      category: "管理文档"
      applicable_to: ["评审会", "周例会", "专题会", "决策会"]
      version: "v1.5"
      last_modified: "2024-03-01"
      fields_count: 12
      required_fields: 10
      usage_count: 312
      avg_quality_score: 92
      
    - id: "TPL-DOC-004"
      name: "变更请求(ECR)模板"
      category: "管理文档"
      applicable_to: ["设计变更", "材料变更", "工艺变更"]
      version: "v2.0"
      last_modified: "2024-02-15"
      fields_count: 22
      required_fields: 18
      usage_count: 89
      avg_quality_score: 85
      
    - id: "TPL-DOC-005"
      name: "用户手册模板"
      category: "产品文档"
      applicable_to: ["消费产品", "专业产品"]
      version: "v1.8"
      last_modified: "2024-01-20"
      fields_count: 15
      required_fields: 12
      usage_count: 45
      avg_quality_score: 88
      
    - id: "TPL-DOC-006"
      name: "知识库条目模板"
      category: "知识管理"
      applicable_to: ["所有知识条目"]
      version: "v1.3"
      last_modified: "2024-03-10"
      fields_count: 14
      required_fields: 10
      usage_count: 567
      avg_quality_score: 90
      
    - id: "TPL-DOC-007"
      name: "项目总结报告模板"
      category: "管理文档"
      applicable_to: ["项目结项"]
      version: "v1.5"
      last_modified: "2024-02-01"
      fields_count: 20
      required_fields: 16
      usage_count: 23
      avg_quality_score: 86
      
    - id: "TPL-DOC-008"
      name: "DFM报告模板"
      category: "技术文档"
      applicable_to: ["结构设计"]
      version: "v1.2"
      last_modified: "2024-01-10"
      fields_count: 10
      required_fields: 8
      usage_count: 67
      avg_quality_score: 91
      
    - id: "TPL-DOC-009"
      name: "FTO分析报告模板"
      category: "知识产权"
      applicable_to: ["专利风险分析"]
      version: "v1.4"
      last_modified: "2024-02-20"
      fields_count: 16
      required_fields: 14
      usage_count: 12
      avg_quality_score: 88
      
    - id: "TPL-DOC-010"
      name: "技术监控周报模板"
      category: "情报文档"
      applicable_to: ["专利/论文监控"]
      version: "v1.2"
      last_modified: "2024-01-15"
      fields_count: 8
      required_fields: 6
      usage_count: 48
      avg_quality_score: 93
```

### 模板更新历史

```yaml
template_update_log:
  - date: "2024-03-10"
    template: "TPL-DOC-006"
    change: "新增'关联条目'字段，支持知识图谱"
    trigger: "知识图谱功能上线"
    approved_by: "项目经理Agent"
    
  - date: "2024-03-01"
    template: "TPL-DOC-003"
    change: "增加'下次会议'预告字段"
    trigger: "用户反馈 (缺少会议衔接)"
    approved_by: "项目经理Agent"
    
  - date: "2024-02-20"
    template: "TPL-DOC-009"
    change: "新增'免责声明'和'法律建议确认'字段"
    trigger: "法务Agent反馈 (FTO报告法律合规)"
    approved_by: "法务Agent"
    
  - date: "2024-02-15"
    template: "TPL-DOC-004"
    change: "影响分析表格增加'成本'维度"
    trigger: "项目经理Agent需求 (成本管控)"
    approved_by: "项目经理Agent"
```

---

## 记忆2: 知识库目录结构 `MEM-DOC-002`

### 知识库统计

```yaml
knowledge_base_stats:
  snapshot_date: "2024-03-15"
  total_entries: 1847
  active_entries: 1562
  archived_entries: 285
  
  by_category:
    KB-DESIGN (设计知识): 423 entries
      声学设计: 156
      结构设计: 128
      硬件设计: 89
      软件/DSP设计: 50
      
    KB-TEST (测试验证): 312 entries
      音频测试: 98
      声学测试: 67
      环境可靠性测试: 78
      自动化测试: 45
      测试设备: 24
      
    KB-MATERIAL (材料与工艺): 198 entries
      声学材料: 45
      结构材料: 78
      电子材料: 32
      加工工艺: 28
      表面处理: 15
      
    KB-PROCESS (流程与规范): 156 entries
      设计流程: 42
      测试流程: 38
      制造流程: 28
      质量管理: 25
      项目管理: 23
      
    KB-PROBLEM (问题与解决): 267 entries
      音频问题: 89
      结构问题: 56
      电子问题: 48
      软件问题: 42
      系统性问题: 32
      
    KB-INTEL (技术情报): 234 entries
      专利情报: 89
      论文摘要: 67
      竞品分析: 34
      技术趋势: 28
      标准法规: 16
      
    KB-SUPPLIER (供应商): 128 entries
      扬声器供应商: 28
      电子元器件供应商: 35
      结构加工供应商: 32
      材料供应商: 18
      测试设备供应商: 15
      
    KB-PROJECT (项目档案): 89 entries
      项目总结: 23
      设计文档归档: 34
      测试报告归档: 21
      经验教训: 11

  top_tags:
    - "ANC": 89 entries
    - "DSP": 76 entries
    - "bluetooth": 65 entries
    - "active-speaker": 54 entries
    - "class-d": 48 entries
    - "TWS": 43 entries
    - "soundbar": 38 entries
    - "LE-Audio": 32 entries
    - "subwoofer": 28 entries
    - "room-correction": 24 entries

  search_stats_last_30d:
    total_queries: 1256
    avg_response_time: "1.2s"
    top_queries:
      - "ANC算法": 45 queries
      - "箱体容积计算": 38 queries
      - "蓝牙延迟": 32 queries
      - "THD测试方法": 28 queries
      - "密封设计": 25 queries
```

### 热门条目

```yaml
popular_entries:
  - entry_id: "KB-0456"
    title: "倒相式箱体设计公式汇总"
    category: "KB-DESIGN > 声学设计"
    views_last_90d: 89
    rating: 4.8/5
    
  - entry_id: "KB-0892"
    title: "APx515操作指南"
    category: "KB-TEST > 音频测试"
    views_last_90d: 76
    rating: 4.6/5
    
  - entry_id: "KB-0234"
    title: "常用塑料材料声学性能对比"
    category: "KB-MATERIAL > 结构材料"
    views_last_90d: 65
    rating: 4.7/5
    
  - entry_id: "KB-1201"
    title: "LE Audio技术要点总结"
    category: "KB-INTEL > 技术趋势"
    views_last_90d: 58
    rating: 4.5/5
```

---

## 记忆3: 术语词典 `MEM-DOC-003`

### 标准化术语

```yaml
terminology_dictionary:
  version: "2024-v4.1"
  last_updated: "2024-03-15"
  total_terms: 456
  
  audio_domain:
    - term: "倒相式箱体"
      english: "bass-reflex enclosure"
      aliases: ["低音反射箱", "bass reflex", "vented box"]
      definition: "通过在箱体上开设倒相管，利用扬声器背面辐射的声波增强低频输出的音箱结构"
      preferred: true
      category: "声学"
      
    - term: "主动降噪"
      english: "Active Noise Cancellation (ANC)"
      aliases: ["ANC", "主动噪声控制", "active noise control"]
      definition: "通过产生与噪声相位相反的声波来抵消噪声的技术"
      preferred: true
      category: "声学"
      
    - term: "总谐波失真加噪声"
      english: "Total Harmonic Distortion plus Noise (THD+N)"
      aliases: ["THD+N", "谐波失真"]
      definition: "输出信号中谐波分量与噪声的总和相对于基波分量的比值，通常用百分比或dB表示"
      preferred: true
      category: "音频测试"
      
    - term: "频率响应"
      english: "Frequency Response"
      aliases: ["频响", "FR"]
      definition: "设备在不同频率下增益或衰减的特性，通常以dB表示"
      preferred: true
      category: "音频测试"
      
    - term: "数字信号处理器"
      english: "Digital Signal Processor (DSP)"
      aliases: ["DSP", "数字信号处理芯片"]
      definition: "专门用于数字信号处理运算的微处理器"
      preferred: true
      category: "电子"
      
    - term: "分频器"
      english: "Crossover Network"
      aliases: [" crossover", "分频网络"]
      definition: "将音频信号按频率分配到不同扬声器单元的电路或系统"
      preferred: true
      category: "声学"
      
    - term: "D类功放"
      english: "Class D Amplifier"
      aliases: ["数字功放", "class-d amplifier", "switching amplifier"]
      definition: "通过PWM方式工作的高效开关型功率放大器"
      preferred: true
      category: "电子"
      note: "注意: D类功放不是'数字功放'的准确翻译，但行业通用"
      
    - term: "有源音箱"
      english: "Active Speaker / Powered Speaker"
      aliases: ["主动音箱", "active loudspeaker"]
      definition: "内置功率放大器的音箱系统"
      preferred: true
      category: "产品"
      
    - term: "密闭式箱体"
      english: "Sealed Enclosure / Closed Box"
      aliases: ["封闭箱", "sealed box", "acoustic suspension"]
      definition: "完全密封的扬声器箱体，无倒相孔"
      preferred: true
      category: "声学"
      
    - term: "指向性"
      english: "Directivity"
      aliases: ["方向性", "directivity pattern"]
      definition: "声源在不同方向辐射声能的相对强度分布"
      preferred: true
      category: "声学"

  structure_domain:
    - term: "超声波焊接"
      english: "Ultrasonic Welding"
      aliases: ["超声焊", "USW"]
      definition: "利用高频机械振动产生的热量使塑料件熔接的工艺"
      preferred: true
      category: "工艺"
      
    - term: "拔模斜度"
      english: "Draft Angle"
      aliases: ["脱模斜度", "draft"]
      definition: "为便于注塑件从模具中脱出，在垂直于分型面的方向上设计的斜度"
      preferred: true
      category: "结构"
      
    - term: "O型圈"
      english: "O-Ring"
      aliases: ["O-ring", "密封圈"]
      definition: "截面为圆形的弹性密封件"
      preferred: true
      category: "结构"

  patent_domain:
    - term: "FTO分析"
      english: "Freedom to Operate Analysis"
      aliases: ["自由实施分析", "clearance search"]
      definition: "评估技术或产品是否可在特定市场自由实施而不侵犯他人有效专利的分析"
      preferred: true
      category: "知识产权"
      
    - term: "权利要求"
      english: "Claim"
      aliases: ["claim", "专利权利要求"]
      definition: "专利文件中定义专利权范围的法律条款"
      preferred: true
      category: "知识产权"
      
    - term: "等同原则"
      english: "Doctrine of Equivalents"
      aliases: []
      definition: "即使被控产品未字面落入权利要求范围，若其技术特征以基本相同的方式实现基本相同的功能达到基本相同的效果，仍可能构成侵权"
      preferred: true
      category: "知识产权"
```

### 缩写对照表

| 缩写 | 全称 | 首次出现建议 |
|------|------|-------------|
| ANC | Active Noise Cancellation | 主动降噪 (ANC, Active Noise Cancellation) |
| THD+N | Total Harmonic Distortion plus Noise | 总谐波失真加噪声 (THD+N) |
| DSP | Digital Signal Processor | 数字信号处理器 (DSP) |
| PCB | Printed Circuit Board | 印刷电路板 (PCB) |
| BOM | Bill of Materials | 物料清单 (BOM) |
| DFM | Design for Manufacturing | 面向制造的设计 (DFM) |
| DFA | Design for Assembly | 面向装配的设计 (DFA) |
| FEM | Finite Element Method | 有限元方法 (FEM) |
| FEA | Finite Element Analysis | 有限元分析 (FEA) |
| SPL | Sound Pressure Level | 声压级 (SPL) |
| SNR | Signal-to-Noise Ratio | 信噪比 (SNR) |
| ECR | Engineering Change Request | 工程变更请求 (ECR) |
| ECO | Engineering Change Order | 工程变更指令 (ECO) |
| FTO | Freedom to Operate | 自由实施 (FTO) |
| IPC | International Patent Classification | 国际专利分类号 (IPC) |
| TWS | True Wireless Stereo | 真无线立体声 (TWS) |
| LE Audio | Low Energy Audio | 低功耗音频 (LE Audio) |
| IP | Ingress Protection | 防护等级 (IP) |
| NPE | Non-Practicing Entity | 非执业实体/专利流氓 (NPE) |

---

## 记忆4: 文档质量历史数据 `MEM-DOC-004`

### 质量趋势

```yaml
quality_trends:
  period: "2023-Q1 ~ 2024-Q1"
  
  monthly_avg_quality_score:
    2023-01: 78
    2023-02: 79
    2023-03: 81
    2023-04: 82
    2023-05: 83
    2023-06: 84
    2023-07: 85
    2023-08: 86
    2023-09: 85
    2023-10: 87
    2023-11: 88
    2023-12: 89
    2024-01: 89
    2024-02: 90
    2024-03: 91
  
  trend_analysis: "质量得分持续改善，从78分提升至91分 (+13分)，主要改善来自术语标准化和模板完善"
  
  by_agent_source:
    structure_agent:
      avg_score: 88
      common_issues:
        - "BOM表格格式不统一 (已提供标准化模板后改善)"
        - "工程图引用缺少版本号"
      improvement: "+15分 (2023年)"
      
    testing_agent:
      avg_score: 92
      common_issues:
        - "偶尔缺少测试环境详细描述"
      improvement: "+8分 (2023年)"
      
    literature_patent_agent:
      avg_score: 89
      common_issues:
        - "专利引用格式偶尔不一致"
      improvement: "+12分 (2023年)"
      
    acoustic_design_agent:
      avg_score: 85
      common_issues:
        - "公式格式需要手动调整"
        - "图表分辨率不统一"
      improvement: "+10分 (2023年)"

  common_quality_issues_ranked:
    - issue: "术语不一致"
      frequency: "23%"
      solution: "术语词典自动替换 + 首次展开检查"
      status: "已大幅改善"
      
    - issue: "模板字段缺失"
      frequency: "18%"
      solution: "提交前字段检查清单"
      status: "改善中"
      
    - issue: "图表编号不连续"
      frequency: "12%"
      solution: "自动编号脚本"
      status: "已解决"
      
    - issue: "缩写未展开"
      frequency: "15%"
      solution: "缩写展开检查"
      status: "改善中"
      
    - issue: "修订历史不完整"
      frequency: "10%"
      solution: "强制修订历史字段"
      status: "已解决"
      
    - issue: "格式不统一"
      frequency: "8%"
      solution: "格式化脚本自动处理"
      status: "已解决"
      
    - issue: "外部链接失效"
      frequency: "5%"
      solution: "链接健康检查 (月度)"
      status: "监控中"
```

### 知识库健康度

```yaml
knowledge_base_health:
  snapshot_date: "2024-03-15"
  overall_health_score: 92/100
  
  dimensions:
    completeness:
      score: 90
      issues:
        - "KB-DESIGN > 工业设计 子分类条目较少 (12条)"
        - "KB-PROJECT > 经验教训 条目较少 (11条)"
      
    consistency:
      score: 95
      issues:
        - "3个条目使用了已废弃术语 (已标记更新)"
        
    connectivity:
      score: 88
      metrics:
        - "孤立条目 (无关联): 67条 (3.6%)"
        - "高度连接条目 (>5关联): 234条 (12.7%)"
        - "平均关联数: 2.3"
      issues:
        - "部分早期条目缺少关联"
        
    freshness:
      score: 90
      metrics:
        - "最近30天更新: 45条"
        - "最近90天更新: 123条"
        - "超过1年未更新: 289条 (15.6%)"
        - "超过2年未更新: 98条 (5.3%)"
      issues:
        - "98条超过2年未更新条目需审核是否仍有效"
        
    accessibility:
      score: 96
      metrics:
        - "平均检索响应时间: 1.2s"
        - "检索成功率: 99.2%"
        - "用户满意度: 4.6/5"
```

---

## 记忆5: 个人偏好设置 `MEM-PREF-001`

```yaml
preferences:
  document_philosophy: "文档是产品，读者是用户"
  
  formatting_defaults:
    line_width: "80 characters (代码) / 无限制 (正文)"
    list_style: "有序: 1. 2. 3. / 无序: - "
    table_alignment: "左对齐文本，右对齐数字"
    heading_style: "ATX style (# ## ###)"
    code_fence: "```language"
    
  pdf_generation:
    page_size: "A4"
    margins: "2.5cm all sides"
    font_body: "Source Han Sans CN / Noto Sans CJK"
    font_code: "Source Code Pro"
    font_size_body: "10.5pt"
    font_size_code: "9pt"
    line_spacing: "1.5"
    
  quality_thresholds:
    min_quality_score_publish: 85
    min_quality_score_archive: 70
    max_terms_inconsistency: 0  # 零容忍
    
  knowledge_management:
    auto_archive_after_days: 730  # 2年无更新自动提醒归档
    orphan_check_frequency: "weekly"
    freshness_review_frequency: "monthly"
    
  communication_style:
    default_tone: "专业、友好、建设性"
    feedback_format: "先肯定 + 具体问题 + 改进建议"
    
  shortcuts:
    - "快速术语查询: /term {查询词}"
    - "快速模板获取: /template {文档类型}"
    - "知识库搜索: /kb {查询词}"
    - "质量检查: /qc {文档ID}"
    - "生成PDF: /pdf {文档ID}"
    
  automation_rules:
    - "收到文档后30分钟内开始处理"
    - "术语替换自动化 (词典匹配率>95%)"
    - "图表编号自动连续化"
    - "修订历史格式自动校验"
    - "知识库条目入库前必须关联≥2个已有条目"
```

---

## 记忆更新机制

```yaml
update_rules:
  文档模板库:
    trigger: "新需求/反馈/定期评审"
    frequency: "每季度评审，按需更新"
    approval: "项目经理Agent"
    notification: "模板更新通知所有使用Agent"
    
  知识库目录结构:
    trigger: "新分类需求/结构优化"
    frequency: "每半年评审"
    approval: "项目经理Agent + 知识管理Agent"
    
  术语词典:
    trigger: "新术语出现/术语冲突/标准更新"
    frequency: "每月更新，即时响应冲突"
    responsible: "本Agent + 各领域Agent反馈"
    
  文档质量历史:
    trigger: "每次质量检查完成"
    frequency: "实时更新"
    responsible: "自动记录"
    
  知识库健康度:
    trigger: "定期检查"
    frequency: "每周快照，每月深度评估"
    responsible: "本Agent"

archival:
  document_retention: "7年 (产品生命周期+法规)"
  knowledge_base_retention: "永久 (知识价值)"
  quality_data_retention: "3年 (趋势分析)"
  
  backup:
    frequency: "每日增量 + 每周全量"
    location: "本地 + 企业云存储"
    test_restore: "每月一次"
```
