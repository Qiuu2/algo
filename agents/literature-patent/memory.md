---
name: Literature & Patent Monitoring Agent Memory
description: |
  技术情报与知识产权监控专家Agent的可积累专业知识记忆、项目经验库、偏好设置。
  包含监控关键词库、竞争对手专利地图、核心技术领域论文库、历史预警记录和FTO分析记录。
version: 1.0.0
author: ITC Enterprise Agent System
---

# Memory: 技术情报与知识产权监控专家 Agent

## 记忆架构

```yaml
memory_system:
  长期记忆 (Persistent):
    - 监控关键词库 (Keyword Library)
    - 竞争对手专利地图 (Competitor Patent Map)
    - 核心技术领域论文库 (Core Technology Paper Library)
    - 历史预警记录 (Alert History)
    - FTO分析记录 (FTO Analysis Records)
    - 个人偏好设置 (Preferences)
    
  短期记忆 (Session):
    - 当前监控任务列表
    - 待处理预警
    - 活跃查询请求
    
  工作记忆 (Working):
    - 当前检索结果集
    - 正在分析的专利/论文
    - 临时分析结论
```

---

## 记忆1: 监控关键词库 `MEM-LIT-001`

### 关键词体系

```yaml
keyword_library:
  version: "2024-Q1-v3.2"
  last_updated: "2024-03-15"
  
  核心产品领域:
    active_speakers:
      display_name: "有源音箱/监听音箱"
      keywords_en:
        primary: ["active speaker", "powered speaker", "monitor speaker", "studio monitor"]
        secondary: ["active loudspeaker", "bi-amped speaker", "DSP speaker"]
        technical: ["digital crossover", "active crossover", "class D amplifier integrated"]
      keywords_cn: ["有源音箱", "监听音箱", "主动分频", "数字分频音箱"]
      ipc_focus: ["H04R3/00", "H04R5/00"]
      
    bluetooth_speakers:
      display_name: "蓝牙音箱"
      keywords_en:
        primary: ["Bluetooth speaker", "wireless speaker", "portable speaker"]
        secondary: ["TWS speaker", "smart speaker", "waterproof speaker"]
        technical: ["A2DP", "LE Audio", "Auracast", "LC3 codec"]
      keywords_cn: ["蓝牙音箱", "无线音箱", "便携音箱", "智能音箱"]
      ipc_focus: ["H04R1/02", "H04B5/00"]
      
    soundbars:
      display_name: "Soundbar"
      keywords_en:
        primary: ["soundbar", "sound bar", "TV speaker system"]
        secondary: ["home theater soundbar", "surround soundbar", " Dolby Atmos soundbar"]
        technical: ["virtual surround", "HDMI ARC", "eARC", "subwoofer wireless"]
      keywords_cn: ["回音壁", "电视音响", "家庭影院音响"]
      ipc_focus: ["H04R5/02", "H04S3/00"]
      
    headphones_earbuds:
      display_name: "耳机/耳塞"
      keywords_en:
        primary: ["headphone", "earphone", "earbud", "TWS", "true wireless"]
        secondary: ["ANC headphone", "noise cancelling earbud", "gaming headset"]
        technical: ["hybrid ANC", "feedforward ANC", "feedback ANC", "Transparency mode"]
      keywords_cn: ["耳机", "耳塞", "真无线", "降噪耳机"]
      ipc_focus: ["H04R1/10", "H04R25/00"]

  核心技术领域:
    active_noise_cancellation:
      display_name: "主动降噪 (ANC)"
      keywords_en: ["active noise cancellation", "ANC", "adaptive noise control", "feedforward ANC", "feedback ANC", "hybrid ANC", "LMS algorithm", "FxLMS", "RLS algorithm"]
      keywords_cn: ["主动降噪", "前馈降噪", "反馈降噪", "混合降噪", "自适应滤波"]
      ipc_focus: ["H04R1/10", "G10K11/178"]
      importance: "High"
      
    dsp_audio_processing:
      display_name: "音频DSP处理"
      keywords_en: ["audio DSP", "digital signal processing audio", "FIR filter", "IIR filter", "room correction", "parametric EQ", "graphic EQ", "dynamic range compression", "limiter"]
      keywords_cn: ["音频DSP", "数字音频处理", "房间校正", "参数均衡", "动态范围压缩"]
      ipc_focus: ["H03G5/00", "H03G9/00", "G10L19/00", "G10L21/00"]
      importance: "High"
      
    speaker_driver_design:
      display_name: "扬声器单元设计"
      keywords_en: ["speaker driver", "loudspeaker driver", "voice coil design", "magnetic circuit", "cone material", "surround design", "spider design", "motional feedback"]
      keywords_cn: ["扬声器单元", "音圈设计", "磁路设计", "振膜材料", "定心支片"]
      ipc_focus: ["H04R9/00", "H04R7/00", "H04R11/00"]
      importance: "Medium"
      
    wireless_audio:
      display_name: "无线音频传输"
      keywords_en: ["wireless audio", "Bluetooth audio", "LE Audio", "Auracast", "LC3 codec", "AptX", "LDAC", "Wi-Fi audio", "AirPlay", "wireless audio latency"]
      keywords_cn: ["无线音频", "蓝牙音频", "低功耗音频", "无线音频延迟"]
      ipc_focus: ["H04B5/00", "H04W4/00"]
      importance: "High"
      
    acoustic_measurement:
      display_name: "声学测量"
      keywords_en: ["acoustic measurement", "loudspeaker measurement", "Klippel", "near-field scanning", "laser vibrometry", "impulse response", "THD measurement", "compression driver test"]
      keywords_cn: ["声学测量", "扬声器测试", "近场扫描", "激光测振", "脉冲响应"]
      ipc_focus: ["H04R29/00"]
      importance: "Medium"
      
    smart_audio:
      display_name: "智能音频"
      keywords_en: ["smart speaker", "voice assistant", "far-field speech recognition", "wake word", "beamforming microphone", "voice activity detection", "AI audio enhancement"]
      keywords_cn: ["智能音箱", "语音助手", "远场语音识别", "唤醒词", "麦克风阵列"]
      ipc_focus: ["H04R3/00", "G10L15/00", "G10L21/00"]
      importance: "Medium"
      
    spatial_audio:
      display_name: "空间音频"
      keywords_en: ["spatial audio", "3D audio", "Dolby Atmos", "DTS:X", "object-based audio", "HRTF", "binaural audio", "ambisonics", "virtual surround"]
      keywords_cn: ["空间音频", "三维音频", "全景声", "头相关传输函数", "虚拟环绕声"]
      ipc_focus: ["H04S3/00", "H04S5/00", "H04S7/00"]
      importance: "Medium"

  关键词更新机制:
    update_triggers:
      - "新项目启动 (增加项目特定关键词)"
      - "新技术出现 (如LE Audio兴起时新增)"
      - "检索效果评估 (查全率/查准率不达预期时调整)"
      - "用户反馈 (各领域Agent反馈漏检时补充)"
    review_frequency: "每季度全面评审"
    responsible: "本Agent + 项目经理Agent确认"
```

### 检索式模板库

```yaml
search_templates:
  template_comprehensive:
    name: "综合检索 (专利+论文)"
    patent_query: "(H04R OR G10K OR H04S) AND ({primary_keywords}) AND ({technical_keywords})"
    literature_query: "({primary_keywords}) AND ({technical_keywords})"
    date_range: "last_12_months"
    
  template_competitor:
    name: "竞争对手追踪"
    patent_query: "(AN/{applicant_name} OR IN/{inventor_name}) AND (H04R OR G10K OR H04S)"
    date_range: "last_6_months"
    
  template_fto:
    name: "FTO检索"
    patent_query: "(H04R OR {specific_ipc}) AND ({feature_keywords}) AND PD/{start_date}-{end_date}"
    jurisdiction: "目标市场国家"
    status_filter: "授权有效专利 (GRANTED)"
    
  template_tech_scan:
    name: "技术领域扫描"
    patent_query: "(CPC/{specific_cpc}) AND ({broad_keywords})"
    literature_query: "({broad_keywords}) AND (survey OR review OR overview)"
    date_range: "last_24_months"
```

---

## 记忆2: 竞争对手专利地图 `MEM-LIT-002`

### 核心竞争对手档案

```yaml
competitor: "Bose Corporation"
competitor_id: "COMP-001"
last_updated: "2024-03-15"

profile:
  headquarters: "美国马萨诸塞州"
  audio_focus: "消费音频、专业音频、汽车音频"
  key_products: ["QuietComfort耳机", "SoundLink音箱", "Soundbar系列", "汽车音响系统"]

patent_portfolio:
  total_patents_family: "~3,500件"
  active_patents: "~1,800件"
  key_technology_areas:
    - area: "ANC (主动降噪)"
      patent_count: "~450件"
      strength: "极强"
      key_patents: ["US8,073,150", "US9,137,573", "US10,382,938"]
      notes: "ANC领域领导者，涵盖前馈/反馈/混合算法及结构"
      
    - area: "便携式音箱"
      patent_count: "~280件"
      strength: "强"
      notes: "箱体设计、单元布局、被动辐射器"
      
    - area: "Soundbar/家庭影院"
      patent_count: "~200件"
      strength: "强"
      notes: "虚拟环绕、波束成形、低音管理"
      
    - area: "声学材料/结构"
      patent_count: "~150件"
      strength: "中"
      notes: "吸声材料、箱体阻尼、单元悬挂"

recent_activity_2023_2024:
  new_applications: "~120件"
  focus_shift: "向空间音频和AI音频处理倾斜"
  notable_patents:
    - "US2024/00XXXXX: 自适应ANC算法基于用户耳道建模"
    - "US2024/00XXXXX: AI驱动的个性化EQ"

risk_assessment_for_itc:
  overall_risk: "High"
  primary_threat: "ANC技术领域交叉风险高"
  recommendation: "ITC计划进入ANC领域需特别谨慎，建议FTO分析"
  
tags: ["ANC领导者", "消费音频巨头", "High威胁"]
```

```yaml
competitor: "Sony Corporation"
competitor_id: "COMP-002"

patent_portfolio:
  total_patents_family: "~5,000件 (音频相关)"
  active_patents: "~2,500件"
  key_technology_areas:
    - area: "音频编解码"
      patent_count: "~600件"
      strength: "极强"
      notes: "LDAC, 360 Reality Audio相关专利族"
      
    - area: " headphones/earbuds"
      patent_count: "~500件"
      strength: "极强"
      notes: "WH-1000X系列, WF-1000X系列"
      
    - area: "Hi-Res Audio"
      patent_count: "~300件"
      strength: "强"
      notes: "DSD, MQA, 高解析度播放"
      
    - area: "游戏音频"
      patent_count: "~150件"
      strength: "中"
      notes: "3D音频定位, 游戏耳机"

recent_activity_2023_2024:
  focus_shift: "360 Reality Audio生态建设, LE Audio布局"
  notable_patents:
    - "US2024/00XXXXX: 360 Reality Audio内容创建工具"
    - "JP2023-XXXXXX: LE Audio广播模式优化"

risk_assessment_for_itc:
  overall_risk: "Medium-High"
  primary_threat: "Hi-Res和编解码领域"
  recommendation: "ITC Hi-Res产品路线注意Sony专利族"
```

```yaml
competitor: "Harman International (Samsung)"
competitor_id: "COMP-003"

patent_portfolio:
  total_patents_family: "~4,000件"
  active_patents: "~2,000件"
  key_technology_areas:
    - area: "汽车音频"
      patent_count: "~800件"
      strength: "极强"
      notes: "Logic7, HALOsonic, 车载声学"
      
    - area: "专业音频"
      patent_count: "~400件"
      strength: "强"
      notes: "JBL Professional, Crown, BSS"
      
    - area: "消费音箱"
      patent_count: "~350件"
      strength: "强"
      notes: "JBL, Harman Kardon品牌"

risk_assessment_for_itc:
  overall_risk: "Medium"
  primary_threat: "汽车音频 (如ITC有汽车方向)"
  recommendation: "消费音箱领域竞争但专利交叉风险可控"
```

```yaml
competitor: "Apple Inc."
competitor_id: "COMP-004"

patent_portfolio:
  total_patents_family: "~2,000件 (音频相关)"
  active_patents: "~1,200件"
  key_technology_areas:
    - area: "TWS耳机"
      patent_count: "~400件"
      strength: "极强"
      notes: "AirPods系列, H1芯片, 空间音频头部追踪"
      
    - area: "计算音频"
      patent_count: "~300件"
      strength: "强"
      notes: "自适应EQ, 实时音频处理"
      
    - area: "HomePod/智能音箱"
      patent_count: "~200件"
      strength: "强"
      notes: "波束成形, 房间感知, Siri集成"

risk_assessment_for_itc:
  overall_risk: "Medium"
  primary_threat: "计算音频和TWS"
  recommendation: "关注Apple计算音频专利趋势"
```

### 竞争对手威胁矩阵

| 竞争对手 | ANC | 便携音箱 | Soundbar | 监听音箱 | 无线音频 | 综合威胁 |
|----------|-----|----------|----------|----------|----------|----------|
| Bose | ★★★ | ★★☆ | ★★★ | — | ★★☆ | High |
| Sony | ★★★ | ★★☆ | ★★☆ | — | ★★★ | High |
| Harman | ★☆☆ | ★★★ | ★★☆ | ★★☆ | ★★☆ | Medium |
| Apple | ★★★ | ★☆☆ | ★★☆ | — | ★★★ | Medium |
| Sennheiser | ★★☆ | — | — | ★★★ | ★★☆ | Medium |
| Jabra | ★★☆ | ★☆☆ | — | — | ★★☆ | Low-Medium |
| 漫步者(Edifier) | ★☆☆ | ★★☆ | ★☆☆ | ★★☆ | ★☆☆ | Low-Medium |

---

## 记忆3: 核心技术领域论文库 `MEM-LIT-003`

### 重点领域论文追踪

```yaml
tracking_area: "主动降噪 (ANC)"
area_id: "PAPER-ANC"
last_updated: "2024-03-15"

key_papers:
  - paper_id: "P-ANC-001"
    title: "A Hybrid Active Noise Control System with Online Secondary Path Modeling"
    authors: ["S. Johansson", "I. Claesson"]
    journal: "IEEE/ACM Transactions on Audio, Speech, and Language Processing"
    year: 2023
    doi: "10.1109/TASLP.2023.XXXXXXX"
    relevance: 9.0
    key_contribution: "在线次级通路建模的混合ANC系统，提高了非稳态环境下的降噪量"
    itc_application: "可直接应用于ITC的ANC产品开发"
    status: "已精读，技术方案已提取"
    
  - paper_id: "P-ANC-002"
    title: "Deep Learning for Active Noise Cancellation: A Review"
    authors: ["Y. Zhang", "et al."]
    journal: "Journal of the Acoustical Society of America"
    year: 2024
    doi: "10.1121/10.XXXXXXX"
    relevance: 8.5
    key_contribution: "深度学习ANC的全面综述，包括RNN/CNN/Transformer架构对比"
    itc_application: "为ITC选择ANC算法路线提供参考"
    status: "已精读，综述要点已提取"
    
  - paper_id: "P-ANC-003"
    title: "Feedforward ANC with Neural Network-Based Secondary Path Estimation"
    authors: ["H. Kim", "J. Park"]
    journal: "IEEE Signal Processing Letters"
    year: 2024
    relevance: 8.0
    key_contribution: "用神经网络替代传统LMS次级通路估计，收敛速度提升40%"
    itc_application: "可作为ITC ANC产品的高级算法选项"
    status: "已摘要"

tracking_area: "空间音频"
area_id: "PAPER-SPATIAL"

key_papers:
  - paper_id: "P-SPA-001"
    title: "Real-Time Binaural Rendering of Object-Based Audio Using Head-Related Transfer Functions"
    authors: ["M. Schärer", "et al."]
    journal: "JAES"
    year: 2023
    relevance: 8.0
    key_contribution: "低延迟HRTF实时渲染方案，适合游戏和VR应用"
    itc_application: "ITC游戏耳机空间音频方案参考"
```

---

## 记忆4: 历史预警记录与处理结果 `MEM-LIT-004`

### 预警历史

```yaml
alert_history:
  - alert_id: "ALT-2023-045"
    date_triggered: "2023-08-20"
    level: "Critical"
    type: "专利授权风险"
    
    trigger:
      patent: "US11,XXX,XXX"
      title: "Adaptive Bass Enhancement System for Portable Speakers"
      applicant: "XX Audio Inc."
      
    description: "授权专利涵盖'基于加速度计反馈的低音增强系统'，与ITC PRJ-2308项目方案高度重叠"
    
    initial_assessment:
      overlap_estimate: ">80%"
      risk: "Literal infringement likely"
      
    actions_taken:
      - action: "FTO深度分析"
        date: "2023-08-21"
        result: "确认高风险"
      - action: "规避方案设计"
        date: "2023-08-25"
        result: "提出3个替代方案"
      - action: "设计Agent评估规避方案"
        date: "2023-09-05"
        result: "选择方案B (基于麦克风反馈替代加速度计)"
      - action: "设计变更实施"
        date: "2023-09-15"
        result: "完成"
      - action: "新方案FTO验证"
        date: "2023-10-01"
        result: "风险降至Low"
        
    resolution:
      status: "Resolved"
      final_outcome: "通过设计规避消除侵权风险"
      lessons_learned: "产品立项时必须进行预FTO分析，避免开发后期被迫变更设计"
      
  - alert_id: "ALT-2023-067"
    date_triggered: "2023-11-10"
    level: "High"
    type: "竞争对手布局变化"
    
    trigger:
      competitor: "Sony"
      activity: "3个月内提交12件LE Audio相关专利申请"
      
    description: "Sony在LE Audio (低功耗蓝牙音频) 领域加速专利布局"
    
    actions_taken:
      - action: "Sony LE Audio专利深度分析"
        date: "2023-11-12"
        result: "聚焦广播模式和辅助听力两大方向"
      - action: "ITC LE Audio路线评估"
        date: "2023-11-20"
        result: "ITC产品与Sony方向不完全重叠，但需关注"
      - action: "持续监控"
        date: "ongoing"
        result: "每月评估"
        
    resolution:
      status: "Monitoring"
      current_status: "风险可控，持续关注"
```

### 预警效果统计

```yaml
alert_effectiveness_2023:
  total_alerts: 47
  
  by_level:
    Critical: 3
    High: 12
    Medium: 18
    Low: 14
    
  accuracy:
    true_positive: 41 (87%)  # 预警有效
    false_positive: 6 (13%)  # 预警过度
    false_negative: 2  # 事后发现漏报 (通过各领域Agent反馈)
    
  resolution_rate:
    Critical: "100% resolved with action"
    High: "83% resolved, 17% ongoing monitoring"
    Medium: "44% resolved, 56% monitoring"
    Low: "100% information only"
    
  average_response_time:
    Critical: "1.5 hours (target: 2h)"
    High: "18 hours (target: 24h)"
    
  lessons_learned:
    - "误报主要原因: 权利要求解读过度保守 → 优化解读标准"
    - "漏报原因: 新进入者未在监控列表 → 增加新进入者自动发现机制"
    - "Critical预警100%有效 → 维持当前Critical判定标准"
```

---

## 记忆5: FTO分析记录 `MEM-LIT-005`

### FTO项目档案

```yaml
fto_project: "FTO-2023-004"
project_name: "ITC PRJ-2308 便携音箱低音增强方案 FTO"
date: "2023-08-15 ~ 2023-09-10"
requester: "项目经理Agent (PRJ-2308)"
analyst: "agent.literature.patent"

scope:
  target_technology: "基于传感器反馈的低音增强系统"
  target_markets: ["US", "CN", "EU", "JP"]
  feature_list:
    - F01: "加速度计检测箱体振动"
    - F02: "根据振动信号调整低频增益"
    - F03: "防止低频过载失真"
    - F04: "自适应算法实时调整"

retrieval_strategy:
  databases: ["USPTO", "Espacenet", "CNIPA", "JPO"]
  keywords: ["bass enhancement", "vibration sensor", "accelerometer speaker", "low frequency protection"]
  ipc: ["H04R3/00", "H04R9/00", "H03G5/00", "H03G9/00"]
  cpc: ["H04R2201/023", "H04R2430/00"]
  date_range: "2000-2023"
  
results:
  total_patents_found: 1,247
  after_dedup: 856
  after_relevance_screening:
    X: 12
    A: 45
    B: 128
    C: 671

high_risk_patents:
  - patent: "US11,XXX,XXX"
    risk_level: "Critical"
    title: "Adaptive Bass Enhancement System..."
    applicant: "XX Audio Inc."
    claim_1_features:
      - "a speaker enclosure" → ITC: "present (literals)"
      - "a vibration sensor coupled to the enclosure" → ITC: "present (accelerometer)"
      - "a processor configured to adjust bass response based on sensor output" → ITC: "present (DSP algorithm)"
    conclusion: "Literal infringement likely if all features implemented"
    recommendation: "Design around required — consider microphone-based feedback instead"
    
  - patent: "CN2022XXXXXXXX.X"
    risk_level: "High"
    title: "...低频保护方法..."
    applicant: "YY电子 (CN)"
    claim_1_features:
      - "采集扬声器振膜加速度信号" → ITC: "present"
      - "判断低频失真" → ITC: "present"
      - "动态调整低频增益" → ITC: "present"
    conclusion: "高度相似，需进一步分析等同原则"

resolution:
  action: "Design around"
  new_solution: "改用麦克风反馈检测低频失真 + DSP算法补偿"
  verification_fto: "FTO-2023-004-R1 (2023-10-01)"
  new_risk_level: "Low"
  
lessons_learned:
  - "传感器反馈低音增强是专利密集区，未来项目需提前FTO"
  - "加速度计方案风险高，麦克风方案风险低且效果相近"
  - "FTO应在方案设计阶段完成，而非开发后期"
  
cost:
  analysis_time: "3.5 weeks"
  redesign_cost_impact: "中等 (开发延期3周)"
  avoided_risk: "潜在侵权诉讼风险 (不可估量)"
```

---

## 记忆6: 个人偏好设置 `MEM-PREF-001`

```yaml
preferences:
  analysis_philosophy: "宁可错报，不可漏报 (对Critical风险)"
  
  default_search_settings:
    date_range_default: "last_24_months"
    max_results_per_query: 1000
    relevance_threshold: "5.0/10 (纳入分析)"
    auto_dedup: true
    dedup_similarity_threshold: 0.90
    
  analysis_depth:
    X_level: "全文精读 + 权利要求逐条解读 + 技术方案提取"
    A_level: "全文阅读 + 摘要提取 + 权利要求概览"
    B_level: "摘要阅读 + 技术主题归类"
    C_level: "标题/摘要浏览 + 记录归档"
    
  reporting_preferences:
    default_language: "中文报告主体，专利号/术语保留英文"
    patent_citation_format: "公开号 (申请日) 申请人 — 标题"
    paper_citation_format: "APA style"
    chart_style: "简洁专业，白色背景"
    
  risk_language:
    # 避免给出法律结论
    infringement_assessment: 
      use: "侵权风险 [高/中/低]，建议 [专利律师/法务] 确认"
      avoid: "构成侵权 / 不构成侵权"
    
  alert_escalation:
    auto_escalate_critical: true
    notification_channels:
      Critical: ["即时消息", "邮件", "系统通知"]
      High: ["邮件", "系统通知"]
      Medium: ["周报汇总"]
      Low: ["月度报告"]
      
  shortcuts:
    - "快速威胁评估: 看申请人+权利要求1技术特征数量+剩余有效期"
    - "专利家族重要性: 同族>5件 = 重要专利"
    - "被引次数判断: 被引>20次 = 基础/核心专利"
    - "新进入者信号: 陌生申请人+高质量代理所 = 值得关注"
```

---

## 记忆更新机制

```yaml
update_rules:
  监控关键词库:
    trigger: "新项目/技术方向/查全率不达标"
    frequency: "每季度全面评审"
    responsible: "本Agent"
    approval: "项目经理Agent"
    
  竞争对手专利地图:
    trigger: "季度更新 + 重大事件即时更新"
    frequency: "季度"
    data_source: "专利数据库定期检索"
    
  论文库:
    trigger: "新论文发现 + 月度整理"
    frequency: "月度"
    responsible: "自动检索 + 人工筛选"
    
  预警历史:
    trigger: "每次预警处理完成"
    frequency: "实时"
    responsible: "本Agent"
    
  FTO记录:
    trigger: "FTO项目完成"
    frequency: "每FTO项目"
    responsible: "本Agent"
    
archival:
  patent_data_retention: "10年 (专利有效期相关)"
  fto_records_retention: "永久"
  alert_history_retention: "7年"
  
  backup:
    frequency: "每日增量"
    location: "本地 + 企业知识库"
```
