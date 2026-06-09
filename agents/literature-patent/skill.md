---
name: Literature & Patent Monitoring Agent Skills
description: |
  技术情报与知识产权监控专家Agent的专业技能定义、工具使用规范、工作流程和输入输出标准。
  遵循Kimi/Hermes Agent Skill标准，包含与其他Agent的明确协作接口。
version: 1.0.0
author: ITC Enterprise Agent System
---

# Skill: 技术情报与知识产权监控专家 Agent

## 技能总览

```yaml
技能域:
  - 文献检索流程
  - 专利检索流程
  - 侵权风险分析
  - 技术趋势分析
  - 预警机制管理
  - 跨域协作接口

技能标准: Kimi/Hermes Agent Skill Specification v1.0
认证级别: L3 (专家级)
```

---

## 技能1: 文献检索流程 `SKILL-LIT-001`

### 概述
系统化的学术论文检索流程，覆盖音频/声学领域的核心数据库，确保技术情报全面。

### 目标数据库

| 数据库 | 覆盖范围 | 更新频率 | 优先级 | 访问方式 |
|--------|----------|----------|--------|----------|
| IEEE Xplore | 电子/信号处理/音频工程 | 周更新 | P0 | 机构订阅 + API |
| ASA Publications | 声学 (JASA/POMA) | 月刊 | P0 | 机构订阅 |
| JAES (AES) | 音频工程 | 月刊 | P0 | AES会员 |
| Web of Science | 多学科综合 | 周更新 | P1 | 机构订阅 |
| Scopus | 多学科综合 | 周更新 | P1 | 机构订阅 |
| arXiv (cs.SD/eess.AS) | 音频信号处理预印本 | 日更新 | P1 | 免费API |
| Google Scholar | 广覆盖 | 持续 | P2 | 网络检索 |
| 知网 (CNKI) | 中文学术文献 | 日更新 | P2 (中国区) | 机构订阅 |
| 万方数据 | 中文期刊/学位论文 | 日更新 | P2 (中国区) | 机构订阅 |

### 检索策略构建

#### 1.1 关键词体系

```yaml
keyword_system:
  核心关键词 (必须出现):
    - "loudspeaker"
    - "speaker"
    - "audio"
    - "acoustic"
    - "sound"
    
  技术领域关键词 (组合使用):
    主动降噪:
      - "active noise cancellation"
      - "ANC"
      - "adaptive filtering"
      - "LMS algorithm"
      - "feedforward ANC"
      - "feedback ANC"
      
    扬声器设计:
      - "loudspeaker design"
      - "driver design"
      - "voice coil"
      - "magnetic circuit"
      - "cone material"
      
    数字信号处理:
      - "audio DSP"
      - "digital crossover"
      - "room correction"
      - "equalization"
      - "DRC (dynamic range compression)"
      
    声学测量:
      - "acoustic measurement"
      - "impulse response"
      - "near-field scanning"
      - "Klippel"
      - "SoundCheck"
      
    阵列处理:
      - "microphone array"
      - "beamforming"
      - "source separation"
      - "DOA estimation"
      
    蓝牙/无线音频:
      - "Bluetooth audio"
      - "LE Audio"
      - "Auracast"
      - "LC3 codec"
      - "wireless speaker"

  布尔逻辑组合示例:
    query_1: "(loudspeaker OR speaker) AND ("active noise cancellation" OR ANC) AND (adaptive OR feedback OR feedforward)"
    query_2: "(audio DSP) AND (room correction OR equalization) AND (filter design OR FIR OR IIR)"
    query_3: "(Bluetooth audio OR "LE Audio") AND (LC3 OR codec) AND (low latency OR quality)"
```

#### 1.2 检索执行流程

```yaml
retrieval_procedure:
  Step_1_需求解析:
    input: "监控范围定义 / 专项查询请求"
    activity: "确定技术领域、时间范围、数据库优先级"
    output: "检索策略文档"
    
  Step_2_检索式构建:
    activity: "基于关键词体系构建布尔检索式"
    output: "各数据库专用检索式"
    note: "不同数据库语法适配 (IEEE vs WoS vs 知网)"
    
  Step_3_执行检索:
    activity: "多数据库并行检索"
    tool: "网络检索Agent (agent.web.retrieval)"
    output: "原始结果集 (含元数据)"
    
  Step_4_结果合并:
    activity: "多数据库结果去重、合并"
    method: "DOI匹配 + 标题相似度 > 90%"
    output: "去重后的统一结果集"
    
  Step_5_相关度排序:
    method: "加权评分模型"
    weights:
      keyword_match_score: 0.4
      citation_count: 0.2
      publication_venue_tier: 0.2
      recency: 0.1
      author_reputation: 0.1
    output: "排序后的结果列表"
    
  Step_6_摘要提取:
    activity: "高相关度论文提取关键信息"
    output: "结构化情报条目"
    
  Step_7_报告生成:
    activity: "汇总分析，生成报告"
    output: "文献监控报告"
```

#### 1.3 文献情报条目模板

```yaml
literature_entry:
  entry_id: "LIT-2024-XXXX"
  source_type: "journal_article"
  
  bibliographic_info:
    title: "论文完整标题"
    authors: ["作者1", "作者2", "..."]
    journal: "期刊名称"
    year: 2024
    volume: "XX"
    issue: "X"
    pages: "PP-PP"
    doi: "10.XXXX/XXXX"
    
  technical_summary:
    problem_addressed: "研究解决的问题"
    proposed_method: "提出的方法/技术"
    key_contribution: "核心贡献"
    experimental_results: "关键实验结果"
    
  itc_relevance:
    relevance_score: 8.5  # 0-10
    relevance_category: "High"
    affected_domains: ["声学设计", "DSP"]
    potential_applications: ["可应用于XX场景"]
    follow_up_needed: true
    follow_up_action: "深度阅读全文，评估技术可行性"
    
  tags: ["ANC", "adaptive_filter", "lms"]
  added_date: "2024-03-15"
  analyst: "agent.literature.patent"
```

---

## 技能2: 专利检索流程 `SKILL-PAT-001`

### 概述
系统化的专利检索流程，覆盖USPTO/EPO/CNIPA等主要专利局，支持FTO、无效、监控等多种检索目的。

### 目标数据库

| 数据库 | 覆盖范围 | 更新频率 | 优先级 | 访问方式 |
|--------|----------|----------|--------|----------|
| USPTO PatFT/AppFT | 美国授权/申请 | 周更新 | P0 | 免费API |
| Espacenet (EPO) | 欧洲及全球 | 周更新 | P0 | 免费API |
| 专利之星 (CNIPA) | 中国专利 | 日更新 | P0 | 免费/订阅 |
| PatSnap | 全球聚合 | 日更新 | P1 | 商业订阅 |
| Google Patents | 全球 | 持续 | P1 | 免费 |
| WIPO Patentscope | PCT国际申请 | 周更新 | P1 | 免费API |
| Derwent Innovation | 增值数据 | 周更新 | P2 | 商业订阅 |

### IPC/CPC分类号策略

```yaml
classification_strategy:
  核心分类号:
    H04R: "电声器件 (扬声器、耳机、麦克风)"
    H04S: "立体声系统"
    H04R3/00: "用于 public address 的放大器"
    H04R5/00: "立体声 arrangements"
    H04R9/00: "锥形振膜扬声器"
    H04R11/00: "平面振膜/静电扬声器"
    H04R17/00: "压电扬声器"
    H04R19/00: "动圈扬声器"
    H04R25/00: "助听器"
    H04R29/00: "电声器件的监控/测试"
    H04R31/00: "电声器件的制造"
    
    H04B: "传输"
    H04B1/00: "传输系统"
    H04B3/00: "有线传输"
    H04B5/00: "近场通信 (NFC/BT)"
    
    H04L: "数字通信"
    H04L29/00: "通信协议"
    
    G10L: "语音分析/合成"
    G10L19/00: "语音/音频编码"
    G10L21/00: "语音处理 (降噪/增强)"
    
    H03G: "放大器控制"
    H03G3/00: "增益控制"
    H03G5/00: "音调控制"
    H03G9/00: "限幅器/压缩器"
    
    H04W: "无线通信网络"
    H04W4/00: "业务/服务 (位置/推送)"
    H04W76/00: "连接管理"

  CPC细分号 (美国):
    H04R1/028: "便携式音箱"
    H04R1/40: "音箱箱体结构"
    H04R3/04: "放大器保护电路"
    H04R5/02: "手持设备集成"
    H04R9/045: "锥形扬声器结构细节"
    H04R29/001: "扬声器测试/测量"
    H04R2201/003: "防水/防尘设计"
    H04R2201/023: "波束成形扬声器阵列"
    H04R2205/022: "主动降噪 (ANC)"
    H04R2205/024: "耳机/耳罩结构"
    H04R2430/00: "信号处理连接"
    H04R2460/03: "无线连接"
    H04R2460/15: "蓝牙"

  分类号组合策略:
    strategy_1: "核心分类号 + 关键词" — 最常用
    strategy_2: "分类号树遍历" — 发现隐藏相关专利
    strategy_3: "引文追溯" — 前后向引用
    strategy_4: "申请人/发明人追踪" — 监控核心竞争对手
```

### 检索执行流程

```yaml
patent_retrieval_procedure:
  Step_1_检索目的确认:
    purposes:
      - "FTO (自由实施) 检索"
      - "专利性/新颖性检索"
      - "竞争对手监控"
      - "技术领域扫描"
      - "无效证据检索"
    output: "检索目的文档"
    
  Step_2_检索策略设计:
    components:
      - "关键词列表 (中英文)"
      - "IPC/CPC分类号列表"
      - "申请人/发明人列表"
      - "日期范围"
      - "目标国家/地区"
    output: "检索策略书"
    
  Step_3_多数据库检索:
    databases: ["USPTO", "Espacenet", "CNIPA", "PatSnap"]
    parallel: true
    output: "各数据库原始结果"
    
  Step_4_去重与合并:
    dedup_methods:
      - "申请号标准化 (去除国家代码差异)"
      - "同族专利合并"
      - "标题+申请人+申请日三维匹配"
    output: "去重后专利清单"
    
  Step_5_相关性分级:
    levels:
      X: "高度相关 — 直接影响ITC技术/产品"
      A: "相关 — 技术领域相关，需关注"
      B: "边缘相关 — 间接参考"
      C: "不相关 — 记录归档"
    method: "权利要求特征比对 + 技术方案相似度"
    
  Step_6_深度分析 (X/A级):
    activity: "全文阅读、权利要求解读、技术方案提取"
    output: "专利分析卡片"
    
  Step_7_报告输出:
    formats: ["监控周报", "FTO报告", "专项报告"]
```

### 专利分析卡片模板

```yaml
patent_card:
  card_id: "PAT-2024-XXXX"
  
  bibliographic_data:
    publication_number: "US2024/0XXXXXX A1"
    application_number: "US18/XXXXXX"
    priority_date: "2022-06-15"
    publication_date: "2024-01-18"
    applicant: "公司名称"
    inventors: ["发明人A", "发明人B"]
    ipc: ["H04R3/00", "H04R9/00"]
    cpc: ["H04R2201/023", "H04R2430/00"]
    family_members: ["EPXXXXXXX", "CNXXXXXXXXXX"]
    
  legal_status:
    current_status: "公开审查中 / 已授权 / 已驳回"
    grant_date: "YYYY-MM-DD (if applicable)"
    estimated_expiry: "YYYY-MM-DD"
    
  technical_analysis:
    problem_solved: "技术问题描述"
    technical_solution: "解决方案概述"
    key_claims:
      claim_1: "独立权利要求1的核心技术特征"
      claim_10: "独立权利要求10的核心技术特征 (如有多项)"
    key_drawing: "图X — 核心结构/流程"
    
  itc_relevance_assessment:
    relevance_level: "X / A / B / C"
    relevance_score: 8.0  # 0-10
    technology_overlap: "描述与ITC技术的重叠领域"
    affected_products: ["可能影响的产品/项目"]
    risk_assessment: "初步风险评估"
    design_around_difficulty: "规避设计难度评估 (Easy/Medium/Hard)"
    
  action_items:
    - action: "具体行动"
      priority: "P0/P1/P2"
      deadline: "YYYY-MM-DD"
      owner: "负责Agent/人"
      
  tags: ["ANC", "portable_speaker", " competitor_X"]
  analyst: "agent.literature.patent"
  analysis_date: "2024-03-15"
```

---

## 技能3: 侵权风险分析方法 `SKILL-PAT-002`

### 概述
系统化的FTO (Freedom to Operate) 分析流程，评估ITC技术/产品侵犯他人专利权的风险。

### FTO分析流程

#### 3.1 分析准备

```yaml
fto_preparation:
  input_requirements:
    - "拟实施技术/产品的详细技术描述"
    - "技术特征清单 (Feature List)"
    - "目标市场国家/地区列表"
    - "关键实施例或产品结构图"
    
  feature_list_template:
    - feature_id: "F01"
      description: "技术特征描述"
      category: "essential / optional"
      alternative_implementations: ["替代方案1", "替代方案2"]
      
    - feature_id: "F02"
      description: "另一技术特征"
      ...
```

#### 3.2 权利要求比对方法

```yaml
claim_charting_method:
  purpose: "逐特征比对，确定权利要求覆盖范围"
  
  procedure:
    Step_1: "提取目标专利的独立权利要求，分解为技术特征"
    Step_2: "将ITC产品的对应特征逐一列出"
    Step_3: "逐特征比对:"
      
      mapping_matrix:
        | 权利要求特征 | ITC产品特征 | 比对结果 | 证据 |
        |-------------|------------|----------|------|
        | 特征A: ... | 特征A': ... |  literal / equivalent / not present | 附图X, 文档Y |
        | 特征B: ... | 特征B': ... |  literal / equivalent / not present | 附图X |
        | 特征C: ... | — |  not present | — |
        
    Step_4: "判定:"
      literal_infringement: "所有权利要求特征在ITC产品中以字面形式存在"
      doctrine_of_equivalents: "特征不完全相同，但以基本相同的方式实现基本相同的功能达到基本相同的效果"
      no_infringement: "至少一个权利要求特征在ITC产品中不存在且无等同物"
      
    Step_5: "风险等级判定:"
      Critical: "高度可能侵权 (literal infringement)"
      High: "可能侵权 (需进一步分析等同原则)"
      Medium: "低可能侵权 (有可争辩的不侵权点)"
      Low: "不太可能侵权"
      None: "无侵权风险"
```

#### 3.3 FTO报告结构

```markdown
# FTO分析报告: [技术/产品名称]

## 1. 执行摘要
- 分析范围: [目标市场/技术领域]
- 检索结果: 相关专利 XX件
- 风险总结: Critical X件 / High X件 / Medium X件 / Low X件
- 主要建议: [一句话建议]

## 2. 分析范围与方法
- 2.1 技术/产品描述
- 2.2 目标市场
- 2.3 检索数据库
- 2.4 检索策略 (关键词/分类号)
- 2.5 特征清单 (Feature List)

## 3. 高风险专利分析

### 3.1 [专利号] — [标题] — [申请人]
- 法律状态: [状态/有效期]
- 风险等级: [Critical/High]
- 保护范围: [权利要求1核心特征]
- 权利要求比对表: [矩阵]
- 分析结论: [侵权风险评估]
- 规避建议: [如适用]

### 3.2 [下一高风险专利] ...

## 4. 中低风险专利清单
[表格: 专利号/标题/申请人/风险等级/简要说明]

## 5. 结论与建议
- 总体风险评估
- 优先行动项
- 进一步分析需求

## 6. 免责声明
本分析为技术情报支持，不构成法律意见。最终法律判断应由执业专利律师/代理人提供。

## 附件
- 检索日志
- 完整专利清单
- 详细权利要求比对表
```

---

## 技能4: 技术趋势分析 `SKILL-LIT-002`

### 概述
基于专利和论文数据的量化分析，识别技术发展趋势、生命周期阶段和竞争格局变化。

### 分析维度

#### 4.1 专利地图 (Patent Landscape)

```yaml
patent_landscape_dimensions:
  技术维度:
    - "IPC/CPC分类号分布"
    - "技术主题聚类"
    - "技术演化路径"
    
  时间维度:
    - "申请量趋势 (年度)"
    - "技术成熟度曲线"
    - "S曲线拟合"
    
  申请人维度:
    - "主要申请人排名"
    - "申请人技术分布"
    - "新进入者/退出者"
    
  地域维度:
    - "国家/地区分布"
    - "同族专利布局"
    - "目标市场映射"
    
  引证维度:
    - "高被引专利识别"
    - "技术传承关系"
    - "核心专利族"
```

#### 4.2 技术生命周期判断

```yaml
technology_lifecycle:
  导入期 (Introduction):
    indicators:
      - "专利申请量快速增长 (年增长>50%)"
      - "申请人数量少 (<10家)"
      - "多为基础专利"
      - "学术论文活跃"
    strategy: "关注+布局窗口期"
    
  成长期 (Growth):
    indicators:
      - "专利申请量持续上升 (年增长20-50%)"
      - "新申请人大量进入"
      - "改进型专利增多"
      - "出现标准/联盟"
    strategy: "积极布局，抢占关键位置"
    
  成熟期 (Maturity):
    indicators:
      - "申请量增长放缓 (年增长<20%)"
      - "申请人数量稳定或减少"
      - "专利密度高，差异化困难"
      - "许可/诉讼增多"
    strategy: "防御性布局，关注许可机会"
    
  衰退期 (Decline):
    indicators:
      - "申请量下降"
      - "技术被替代"
      - "专利维护率下降"
    strategy: "收割价值，关注替代技术"
```

#### 4.3 S曲线预测方法

```yaml
s_curve_analysis:
  model: "Logistic Growth Model"
  formula: "N(t) = K / (1 + exp(-r(t - t0)))"
  parameters:
    K: "技术潜力上限 (饱和专利数)"
    r: "增长率"
    t0: "拐点时间"
    
  data_input:
    - "年度专利申请量 (近15年)"
    - "年度申请人数量"
    
  output:
    - "当前生命周期阶段"
    - "预计成熟期时间窗口"
    - "技术潜力上限估计"
    
  limitations:
    - "基于历史数据，无法预测颠覆性技术"
    - "需结合专家判断"
    - "不同市场可能处于不同阶段"
```

---

## 技能5: 预警机制定义 `SKILL-LIT-003`

### 预警触发条件

```yaml
alert_triggers:
  Critical (红色预警):
    conditions:
      - "核心竞争对手在与ITC当前产品直接竞争的技术领域获得授权专利"
      - "发现ITC正在实施的技术有高度侵权风险 (literal infringement)"
      - "ITC核心产品对应的标准必要专利被声明"
      - "主要市场出现针对ITC的专利诉讼/警告函"
      
    response:
      notification: "即时推送 (2小时内)"
      recipients: ["项目经理Agent", "法务Agent", "专利律师Agent"]
      action_required: "48小时内召开紧急评估会议"
      follow_up: "FTO深度分析 + 规避方案评估"
      
  High (橙色预警):
    conditions:
      - "核心竞争对手在与ITC计划产品的技术领域提交新专利申请"
      - "发现可能侵权风险 (需进一步分析等同原则)"
      - "NPE (非执业实体) 在ITC相关领域大量收购专利"
      - "ITC计划采用的技术路线出现重要专利壁垒"
      
    response:
      notification: "24小时内推送"
      recipients: ["项目经理Agent", "相关技术Agent"]
      action_required: "1周内完成深度分析"
      follow_up: "监控 + 方案调整评估"
      
  Medium (黄色预警):
    conditions:
      - "次要竞争对手在相关领域有专利活动"
      - "技术领域出现新的研究方向或专利趋势"
      - "ITC监控的特定专利状态变化 (授权/驳回/无效)"
      
    response:
      notification: "周报汇总"
      recipients: ["项目经理Agent"]
      action_required: "关注 + 必要时分析"
      
  Low (蓝色提醒):
    conditions:
      - "新进入者在相关领域有初步专利活动"
      - "相关技术论文发表"
      - "行业标准更新/讨论"
      
    response:
      notification: "月度/季度报告"
      recipients: ["项目经理Agent"]
      action_required: "信息归档，趋势跟踪"
```

### 预警响应流程

```
[触发] → [分级判定] → [通知推送] → [接收确认] → [分析处理] → [措施建议] → [跟踪闭环]
   ↓           ↓             ↓            ↓            ↓            ↓            ↓
自动/人工    规则匹配      按级推送      要求确认      深度分析      多Agent      效果评估
检索发现    置信度评估     即时/日报/周报  升级机制      报告输出      联合决策      策略优化
```

---

## 技能6: 报告模板 `SKILL-LIT-004`

### 周度监控报告模板

```markdown
# 技术情报周度监控报告

报告期: 2024年XX月XX日 — XX月XX日
报告编号: RPT-WEEK-2024-XX

---

## 1. 本周概览

| 类别 | 新增 | 累计监控 | 关键变化 |
|------|------|----------|----------|
| 新公开专利 | XX件 | XXXX件 | — |
| 新授权专利 | XX件 | XXXX件 | +X件Critical相关 |
| 新专利申请 | XX件 | XXXX件 | — |
| 新论文 | XX篇 | XXXX篇 | — |
| 预警 | X个 | — | Critical: X / High: X |

## 2. 关键预警 (如有)

### [预警级别] [专利号/论文] — [标题]
- **触发原因**: [简述]
- **影响评估**: [对ITC的影响]
- **建议措施**: [行动建议]
- **处理状态**: [待处理/处理中/已关闭]

## 3. 新专利摘要 (Top 10)

| 序号 | 专利号 | 申请人 | 技术主题 | ITC相关度 | 备注 |
|------|--------|--------|----------|-----------|------|
| 1 | US2024/... | XX公司 | ... | X级 | ... |
| 2 | ... | ... | ... | ... | ... |

## 4. 新论文摘要 (Top 5)

| 序号 | 标题 | 作者/机构 | 期刊 | ITC相关度 | 备注 |
|------|------|-----------|------|-----------|------|
| 1 | ... | ... | ... | X级 | ... |

## 5. 竞争对手动态

| 竞争对手 | 本周新专利 | 活跃技术领域 | 值得关注 |
|----------|-----------|-------------|----------|
| XX公司 | X件 | ... | ... |

## 6. 下周计划

- [监控重点/调整方向]

---

*报告由 Literature & Patent Monitoring Agent 自动生成*
*免责声明: 本报告为技术情报参考，不构成法律意见*
```

### 月度分析模板

```markdown
# 技术情报月度深度分析报告

月份: 2024年XX月
报告编号: RPT-MONTH-2024-XX

---

## 1. 月度摘要
[一页纸摘要，包含关键发现、主要风险、建议行动]

## 2. 专利态势分析
### 2.1 申请量趋势
[图表 + 分析]

### 2.2 技术领域分布
[专利地图 + 热点识别]

### 2.3 主要申请人动态
[排名变化 + 布局分析]

## 3. 技术趋势分析
### 3.1 新兴技术识别
### 3.2 技术生命周期评估
### 3.3 S曲线分析

## 4. 风险评估
### 4.1 新识别风险
### 4.2 风险变化跟踪
### 4.3 风险缓解进展

## 5. 机会分析
### 5.1 技术空白点
### 5.2 许可/合作机会

## 6. 建议行动
[优先级排序的行动建议]

## 附件
- 完整专利清单
- 详细分析数据
- 专利地图高清图
```

---

## 技能7: 跨域协作接口 `SKILL-COL-001`

### 与网络检索Agent的协作接口

```yaml
agent_id: agent.web.retrieval
interface_type: 自动化检索 + 数据抓取
protocol: REST API + 消息队列

retrieval_tasks:
  patent_search:
    query_format:
      database: "uspto / espacenet / cnipa"
      query: "检索式 (支持各数据库语法)"
      date_range: ["YYYY-MM-DD", "YYYY-MM-DD"]
      fields: ["title", "abstract", "claims", "applicant", "inventor"]
      max_results: 1000
      
    response_format:
      results: [
        {
          "publication_number": "US2024/0XXXXXX",
          "title": "...",
          "abstract": "...",
          "applicant": "...",
          "inventors": ["..."],
          "ipc": ["..."],
          "publication_date": "YYYY-MM-DD",
          "priority_date": "YYYY-MM-DD",
          "url": "https://..."
        }
      ]
      total_hits: 523
      search_time: "2024-03-15T09:00:00Z"
      
  literature_search:
    query_format:
      database: "ieee / asa / jaes / arxiv"
      query: "检索式"
      date_range: ["YYYY-MM-DD", "YYYY-MM-DD"]
      
  alert_setup:
    format:
      alert_name: "监控任务名称"
      query: "定期执行的检索式"
      frequency: "daily / weekly"
      callback: "结果推送地址"
```

### 与数据库Agent的协作接口

```yaml
agent_id: agent.database
interface_type: 情报数据存储 + 关联分析
protocol: SQL + REST API

data_schema:
  patents_table:
    columns:
      - patent_id (PK)
      - publication_number
      - title
      - abstract
      - claims_summary
      - applicant
      - inventors (JSON array)
      - ipc_codes (JSON array)
      - cpc_codes (JSON array)
      - priority_date
      - publication_date
      - grant_date
      - legal_status
      - family_members (JSON array)
      - itc_relevance_score
      - itc_relevance_level (X/A/B/C)
      - analysis_status
      - analyst
      - analysis_date
      - tags (JSON array)
      - raw_data_url
      
  literature_table:
    columns:
      - lit_id (PK)
      - title
      - authors (JSON array)
      - journal
      - year
      - doi
      - abstract
      - itc_relevance_score
      - tags (JSON array)
      - added_date
      
  alerts_table:
    columns:
      - alert_id (PK)
      - trigger_patent_id (FK)
      - alert_level (Critical/High/Medium/Low)
      - alert_description
      - triggered_date
      - status (new/acknowledged/analyzing/resolved/closed)
      - assigned_to
      - resolution_notes
      
queries:
  competitor_tracking:
    sql: |
      SELECT applicant, COUNT(*) as patent_count, 
             STRING_AGG(DISTINCT ipc_codes, ', ') as tech_fields
      FROM patents 
      WHERE publication_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
      GROUP BY applicant
      ORDER BY patent_count DESC
      
  technology_trend:
    sql: |
      SELECT YEAR(publication_date) as year, 
             COUNT(*) as count,
             AVG(itc_relevance_score) as avg_relevance
      FROM patents
      WHERE ipc_codes LIKE '%H04R%'
      GROUP BY YEAR(publication_date)
      ORDER BY year
```

### 与各领域Agent的协作接口

```yaml
collaboration_interfaces:
  acoustic_design_agent:
    query_request:
      format: JSON
      fields:
        - "query_topic": "查询技术主题"
        - "query_context": "具体应用场景"
        - "urgency": "normal/urgent"
        - "depth": "summary/detailed"
      
    response_format:
      - "related_patents": [专利分析卡片列表]
      - "related_papers": [文献情报条目列表]
      - "risk_assessment": "风险简要评估"
      - "recommendations": "建议"
      
  project_manager_agent:
    risk_alert:
      format: JSON
      fields:
        - "alert_level": "Critical/High/Medium/Low"
        - "alert_type": "patent_risk / competitor_activity / technology_shift"
        - "description": "预警描述"
        - "affected_projects": ["项目代号"]
        - "recommended_actions": ["建议行动"]
        - "time_sensitivity": "immediate / days / weeks"
        - "supporting_data_url": "详细数据链接"
        
    status_report:
      format: Markdown
      frequency: "weekly"
      content: "周度监控报告 (见报告模板)"
      
  legal_agent:
    fto_request:
      format: JSON
      fields:
        - "request_type": "fto_analysis / infringement_assessment / validity_analysis"
        - "target_technology": "技术描述"
        - "target_markets": ["国家/地区"]
        - "target_products": ["产品/项目代号"]
        - "priority": "urgent / normal"
        - "deadline": "YYYY-MM-DD"
        
    fto_deliverable:
      format: Markdown PDF
      content: "FTO分析报告 (见FTO报告模板)"
```

---

## 输入/输出规范

### 标准输入

| 输入类型 | 格式 | 来源 | 验证规则 |
|----------|------|------|----------|
| 监控范围定义 | JSON | 项目经理Agent | 技术领域有效性 |
| 专项查询请求 | JSON | 各领域Agent | 查询主题明确性 |
| 原始检索数据 | JSON/HTML | 网络检索Agent | 数据完整性校验 |
| 专利全文 | XML/PDF | 专利数据库 | 格式解析验证 |
| 技术方案描述 | Markdown | 各设计Agent | 技术特征完整性 |

### 标准输出

| 输出类型 | 格式 | 目标 | 质量检查 |
|----------|------|------|----------|
| 技术监控周报 | Markdown + PDF | 项目经理Agent | 关键词覆盖100% |
| 专利地图 | PNG + Markdown | 项目经理Agent + 评审Agent | 数据准确性 |
| 风险预警 | JSON + Markdown | 项目经理Agent(紧急) | 分级合理性 |
| FTO分析报告 | Markdown + PDF | 法务Agent | 分析完整性 |
| 竞品分析报告 | Markdown + PDF | 项目经理Agent + 市场Agent | 情报准确性 |
| 专项查询回复 | JSON + Markdown | 查询发起Agent | 相关性>80% |

### 质量检查清单 (自检)

```yaml
pre_delivery_check:
  - [ ] 检索策略完整 (关键词+分类号+申请人)
  - [ ] 目标数据库全部覆盖
  - [ ] 去重率<5%
  - [ ] 关键专利不遗漏 (核心竞品+核心领域)
  - [ ] 权利要求比对有据
  - [ ] 风险等级判定有依据
  - [ ] 法律免责声明包含
  - [ ] 引用格式统一
  - [ ] 报告模板字段完整
  - [ ] 预警分级合理 (无过度/不足)
  - [ ] 数据已归档数据库Agent
```
