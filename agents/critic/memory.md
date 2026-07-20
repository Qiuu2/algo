---
name: critic-memory
description: >
  Critic Agent的记忆配置文件。
  包含历史评审记录、各领域Checklist演进、评审效率数据、误判分析。
  所有记忆条目可学习和更新，驱动Critic Agent的持续改进。
version: 1.0.0
author: ITC Architecture Team
---

# Critic Agent — Memory

## 1. Memory Architecture

```
Critic Memory Store
├── Review History             # 所有评审的详细记录
│   ├── Individual Reviews     # 单次评审记录
│   ├── Finding Patterns       # 发现的问题模式
│   └── Agent Profiles         # 各Agent的评审画像
│
├── Checklist Evolution        # Checklist的演进记录
│   ├── Current Checklists     # 当前版本
│   ├── Change History         # 变更历史
│   └── Effectiveness Data     # 各检查项的有效性数据
│
├── Performance Metrics        # Critic自身的效率数据
│   ├── Review Efficiency      # 评审效率
│   ├── Detection Rates        # 发现率
│   └── Error Analysis         # 误判分析
│
└── Knowledge Base             # 领域知识库
    ├── Standards Library      # 标准库
    ├── Lesson Library         # 教训库
    └── Pattern Library        # 模式库
```

## 2. Review History

### 2.1 Individual Review Records

> ⚠ **本节为占位/模板评审记录**（`total_reviews: 156`、`2024-01-XX` 假日期、`REV-XX` 假 ID，无采集器）——与已删的 §3/§4 同class 伪造，按本项目 POLICY 属无标 L0/L4。**SLIM-03 有意延后清理本节**（属"评审历史"非"指标层"）；真实评审见 `sprint2/docs/decisions_log.md` 的 `reviewer: critic @ …` 链。待后续一并归档或删。

```yaml
review_history:
  total_reviews: 156
  last_updated: "2024-01-15T10:00:00Z"
  
  records:
    - review_id: "REV-AC-001-v1"
      date: "2024-01-10T09:30:00Z"
      deliverable: "Acoustic Cavity FEM Report"
      agent: "acoustics-agent"
      task_id: "TASK-ITCQ1-001"
      verdict: "FAILED"
      duration_minutes: 95
      findings:
        - severity: "MAJOR"
          category: "methodology"
          description: "网格收敛性未验证"
          pattern_match: "AC-ERR-001"
          agent_resolved: true
        - severity: "MINOR"
          category: "documentation"
          description: "图表缺少单位标注"
          agent_resolved: true
      re_review_cycles: 2
      final_verdict: "PASSED"
      lesson: "Acoustic FEM reports consistently miss mesh convergence — prioritize this check"
      
    - review_id: "REV-DSP-003-v1"
      date: "2024-01-11T14:00:00Z"
      deliverable: "IIR Filter Implementation"
      agent: "dsp-agent"
      task_id: "TASK-ITCQ1-008"
      verdict: "PASSED"
      duration_minutes: 45
      findings:
        - severity: "INFO"
          category: "optimization"
          description: "可考虑使用级联二阶节替代直接型，提高数值稳定性"
          agent_resolved: false  # info only, not required
      re_review_cycles: 0
      lesson: "dsp-agent consistently high quality — can reduce review depth"
      
    - review_id: "REV-HW-005-v2"
      date: "2024-01-12T11:20:00Z"
      deliverable: "Amplifier PCB Layout (Rev 2)"
      agent: "hardware-agent"
      task_id: "TASK-ITCQ1-012"
      verdict: "FAILED"
      duration_minutes: 120
      findings:
        - severity: "BLOCKER"
          category: "safety"
          description: "LDO输出未加过压保护，超过最大输入电压时会损坏后端电路"
          pattern_match: "HW-ERR-001-related"
          agent_resolved: true
        - severity: "MAJOR"
          category: "thermal"
          description: "功放芯片下方缺少散热过孔"
          pattern_match: "HW-ERR-002"
          agent_resolved: true
        - severity: "MAJOR"
          category: "signal_integrity"
          description: "音频差分对长度不匹配（差120mil）"
          agent_resolved: true
      re_review_cycles: 1
      final_verdict: "PASSED"
      lesson: "hardware-agent PCB submissions need extra attention on thermal and SI"
      
    - review_id: "REV-ST-002-v1"
      date: "2024-01-13T16:00:00Z"
      deliverable: "Enclosure 3D Model"
      agent: "structure-agent"
      task_id: "TASK-ITCQ1-015"
      verdict: "PASSED_WITH_MINOR"
      duration_minutes: 60
      findings:
        - severity: "MINOR"
          category: "dfm"
          description: "深腔区域脱模斜度可增加到1.5°以改善流动性"
          agent_resolved: true
      re_review_cycles: 0
      lesson: "structure-agent generally solid; DFM items are minor suggestions"
```

### 2.2 Finding Patterns by Domain

```yaml
finding_patterns:
  acoustics:
    top_categories:
      - category: "mesh_convergence"
        count: 8
        severity_distribution: { MAJOR: 7, MINOR: 1 }
        avg_resolution_cycles: 1.5
        trend: "stable"
        
      - category: "measurement_conditions"
        count: 6
        severity_distribution: { MAJOR: 5, MINOR: 1 }
        avg_resolution_cycles: 1.0
        trend: "decreasing"  # agent improving
        
      - category: "statistical_significance"
        count: 4
        severity_distribution: { MINOR: 4 }
        avg_resolution_cycles: 1.0
        trend: "stable"
        
    agent_improvement_trend:
      acoustics-agent:
        first_5_reviews_avg_findings: 4.2
        last_5_reviews_avg_findings: 2.4
        improvement_rate: "-43%"
        
  dsp:
    top_categories:
      - category: "fixed_point_overflow"
        count: 12
        severity_distribution: { BLOCKER: 8, MAJOR: 4 }
        avg_resolution_cycles: 1.2
        trend: "decreasing"
        
      - category: "mips_verification"
        count: 7
        severity_distribution: { MAJOR: 7 }
        avg_resolution_cycles: 1.1
        trend: "decreasing"
        
      - category: "filter_stability"
        count: 5
        severity_distribution: { BLOCKER: 5 }
        avg_resolution_cycles: 1.0
        trend: "stable"
        
    agent_improvement_trend:
      dsp-agent:
        first_5_reviews_avg_findings: 2.8
        last_5_reviews_avg_findings: 1.6
        improvement_rate: "-43%"
        
  hardware:
    top_categories:
      - category: "thermal_design"
        count: 9
        severity_distribution: { MAJOR: 9 }
        avg_resolution_cycles: 1.8
        trend: "stable"  # persistent issue
        
      - category: "erc_drc"
        count: 11
        severity_distribution: { BLOCKER: 11 }
        avg_resolution_cycles: 1.0
        trend: "decreasing"
        
      - category: "component_derating"
        count: 6
        severity_distribution: { MAJOR: 6 }
        avg_resolution_cycles: 1.3
        trend: "stable"
        
      - category: "emc_emi"
        count: 5
        severity_distribution: { MAJOR: 5 }
        avg_resolution_cycles: 1.6
        trend: "stable"
        
    agent_improvement_trend:
      hardware-agent:
        first_5_reviews_avg_findings: 5.6
        last_5_reviews_avg_findings: 4.8
        improvement_rate: "-14%"  # slow improvement
        
  structure:
    top_categories:
      - category: "wall_thickness"
        count: 4
        severity_distribution: { BLOCKER: 3, MAJOR: 1 }
        avg_resolution_cycles: 1.0
        trend: "decreasing"
        
      - category: "interference_check"
        count: 5
        severity_distribution: { MAJOR: 5 }
        avg_resolution_cycles: 1.2
        trend: "stable"
        
    agent_improvement_trend:
      structure-agent:
        first_5_reviews_avg_findings: 3.0
        last_5_reviews_avg_findings: 2.2
        improvement_rate: "-27%"
        
  test:
    top_categories:
      - category: "coverage_gap"
        count: 6
        severity_distribution: { MAJOR: 6 }
        avg_resolution_cycles: 1.3
        trend: "stable"
        
      - category: "pass_fail_criteria"
        count: 5
        severity_distribution: { MINOR: 5 }
        avg_resolution_cycles: 1.0
        trend: "decreasing"
        
    agent_improvement_trend:
      test-agent:
        first_5_reviews_avg_findings: 3.4
        last_5_reviews_avg_findings: 2.0
        improvement_rate: "-41%"
```

### 2.3 Agent Review Profiles

```yaml
agent_review_profiles:
  acoustics-agent:
    total_reviews: 23
    first_pass_rate: 0.55          # 55% pass on first try
    avg_findings_per_review: 3.1
    avg_review_cycles: 1.8
    
    strengths:
      - "Technical depth in FEM simulation"
      - "Good documentation of methodology"
    weaknesses:
      - "Often skips mesh convergence verification"
      - "Measurement condition recording inconsistent"
      
    recommended_review_depth: "standard"
    special_attention:
      - "Always verify mesh convergence section"
      - "Check for environmental condition records"
      
  dsp-agent:
    total_reviews: 31
    first_pass_rate: 0.82
    avg_findings_per_review: 1.4
    avg_review_cycles: 1.2
    
    strengths:
      - "Excellent first-pass rate"
      - "Thorough fixed-point analysis"
      - "Good documentation"
    weaknesses:
      - "Occasionally misses MIPS edge cases"
      
    recommended_review_depth: "lighter"  # Known good agent
    special_attention:
      - "Verify MIPS worst-case scenarios"
      
  hardware-agent:
    total_reviews: 19
    first_pass_rate: 0.48
    avg_findings_per_review: 4.6
    avg_review_cycles: 2.3
    
    strengths:
      - "Comprehensive schematic designs"
      - "Good component selection documentation"
    weaknesses:
      - "Frequently misses thermal design"
      - "High revision rate on PCB layouts"
      - "DRC issues common"
      
    recommended_review_depth: "deep"     # Needs extra attention
    special_attention:
      - "Mandatory thermal checklist"
      - "ERC/DRC pre-check reminder"
      - "Component derating verification"
      
  structure-agent:
    total_reviews: 15
    first_pass_rate: 0.68
    avg_findings_per_review: 2.3
    avg_review_cycles: 1.5
    
    strengths:
      - "Good CAD model quality"
      - "DFM awareness"
    weaknesses:
      - "Interference checks sometimes missed"
      - "Tolerance analysis occasionally incomplete"
      
    recommended_review_depth: "standard"
    special_attention:
      - "Verify interference check report"
      
  test-agent:
    total_reviews: 27
    first_pass_rate: 0.78
    avg_findings_per_review: 1.9
    avg_review_cycles: 1.3
    
    strengths:
      - "Good test plan structure"
      - "Consistent improvement trend"
    weaknesses:
      - "Coverage gaps in complex scenarios"
      
    recommended_review_depth: "standard"
    special_attention:
      - "Verify requirement coverage matrix"
```

## 3–4. Checklist Evolution / Performance Metrics 〔占位与伪造数据已删除 2026-07-20，DEC-S6-GOVERNANCE-SLIM-03〕

> 原 §3（Checklist 版本/变更史/有效性）+ §4（评审效率/检测率/逃逸缺陷）整段 = **占位模板 + 编造数字**：
> 2023–2024 假日期、检测率 0.98/0.92/0.85、周转 median 1.7h/p95 4.2h、REV-XX 假评审 ID、escaped-defect 假案例。
> 本项目实际用 **R 编号 / DEC-ID / 2026 日期**。这些数字**无任何采集器，按本项目 POLICY 属无标 L0/L4、违 C1/C2**——
> 且躺在 critic 自己的记忆里执行溯源制度，最讽刺。已删。
> **真实的 critic 学习/有效性记录见**：§5 误判分析、§6 知识库（LESSON-006~015）、§7 学习规则、
> 文末「2026-06-06 轮次教训（R24–R34）」，以及 `sprint2/docs/decisions_log.md` 的 `reviewer: critic @ …` 标记链。
> 若将来要真指标：先定「采集事件 + 存储位置 + L 级」，别再填常数。

## 5. Misjudgment Analysis

### 5.1 False Positives

```yaml
false_positives:
  # Critic flagged issues that were later deemed acceptable
  
  total_fp: 7
  fp_rate: 0.05                    # 5% false positive rate
  
  examples:
    - review_id: "REV-AC-004-v1"
      finding: "MAJOR: 仿真频率范围只到20kHz，建议扩展到40kHz"
      agent_response: "产品规格要求只到20kHz，扩展无意义且增加计算量"
      resolution: "ACCEPTED_AS_IS"
      lesson: "Verify specification requirements before challenging scope"
      
    - review_id: "REV-HW-008-v1"
      finding: "MAJOR: 建议增加额外的去耦电容"
      agent_response: "已通过PI仿真验证，当前去耦方案满足阻抗要求"
      resolution: "ACCEPTED_AS_IS"
      lesson: "Request simulation evidence before flagging component count issues"
      
    - review_id: "REV-DSP-007-v1"
      finding: "MINOR: 建议使用更高效的数据结构"
      agent_response: "当前结构满足MIPS预算且更易维护"
      resolution: "ACCEPTED_AS_IS"
      lesson: "Optimization suggestions should reference specific requirement gaps"
```

### 5.2 False Negatives

```yaml
false_negatives:
  # Issues Critic missed (found by others later)
  # Documented in escaped_defects section above
  
  root_cause_analysis:
    checklist_gap: 2      # Checklist missing the specific check
    execution_gap: 1      # Checklist had it but Critic missed it
    
  improvement_actions:
    - "Add quantitative thresholds to all checklist items (eliminate yes/no)"
    - "Add automated cross-domain parameter comparison"
    - "Quarterly checklist review with escaped defect analysis"
```

## 6. Knowledge Base

### 6.1 Standards Library

```yaml
standards_library:
  acoustics:
    - standard: "IEC 60268-5"
      title: "Sound system equipment — Part 5: Loudspeakers"
      applicable_checks: ["measurement_distance", "frequency_range", "power_rating"]
      
    - standard: "IEC 61672-1"
      title: "Electroacoustics — Sound level meters"
      applicable_checks: ["measurement_accuracy", "frequency_weighting"]
      
  dsp:
    - standard: "ITU-R BS.1387"
      title: "Method for objective measurements of perceived audio quality"
      applicable_checks: ["quality_metrics"]
      
  hardware:
    - standard: "IPC-2221"
      title: "Generic Standard on Printed Board Design"
      applicable_checks: ["trace_width", "clearance", "drill_sizes"]
      
    - standard: "IPC-A-610"
      title: "Acceptability of Electronic Assemblies"
      applicable_checks: ["solder_joint_quality", "component_placement"]
      
    - standard: "UL 62368-1"
      title: "Audio/video, information and communication technology equipment"
      applicable_checks: ["safety_clearance", "insulation", "temperature_limits"]
      
  structure:
    - standard: "ISO 2768"
      title: "General tolerances"
      applicable_checks: ["dimensional_tolerance"]
      
  test:
    - standard: "IEC 60068"
      title: "Environmental testing"
      applicable_checks: ["temperature", "humidity", "vibration", "shock"]
```

### 6.2 Lesson Library

```yaml
lesson_library:
  lessons:
    - id: "LESSON-001"
      date: "2023-11-15"
      domain: "hardware"
      title: "Always verify thermal simulation evidence"
      description: "hardware-agent consistently claims thermal design is adequate without providing simulation data. Always require thermal simulation screenshot or calculation sheet."
      triggered_by: "prototype_overheat"
      
    - id: "LESSON-002"
      date: "2023-12-01"
      domain: "acoustics"
      title: "Mesh convergence is non-negotiable"
      description: "Multiple acoustic FEM results were later found to be inaccurate due to insufficient mesh. Mesh convergence verification is now a BLOCKER item."
      triggered_by: "measurement_simulation_mismatch"
      
    - id: "LESSON-003"
      date: "2023-12-10"
      domain: "cross_domain"
      title: "Coordinate-level cross-domain check is essential"
      description: "2mm misalignment between acoustic port and structural opening caused prototype issue. Always compare exact coordinates, not just dimensions."
      triggered_by: "integration_test_failure"
      
    - id: "LESSON-004"
      date: "2024-01-05"
      domain: "dsp"
      title: "MIPS worst-case != typical-case"
      description: "dsp-agent typically reports average MIPS, but worst-case can be 2-3x higher. Always require worst-case MIPS with specific stimulus."
      triggered_by: "realtime_glitch"
      
    - id: "LESSON-005"
      date: "2024-01-10"
      domain: "test"
      title: "Coverage matrix must be bidirectional"
      description: "Unidirectional traceability (requirement → test) can miss tests that don't map to requirements. Bidirectional check catches orphaned tests and untraced requirements."
      triggered_by: "cto_gate_review"

    - id: "LESSON-006"
      date: "2026-05-27"
      domain: "acoustics / cross_domain"
      title: "竞品参数反推必须以实测拆机数据为准（绝不可作设计锁定依据）"
      description: >
        Sprint2 声学远场反推竞品阵列为 ≈20元/35mm（RMS 2.84dB，置信度中等）；
        Sprint3 拆机实测真值为 16元/55mm（L825），间距差异显著（35→55mm）。
        根因：远场指向性反推存在多解性——不同 N/d 组合可拟合相近方向图，反推天然欠定。
        裁定规则：① 反推结论仅作 PRD 对标参考，禁止作为几何/设计锁定依据；
        ② 一旦取得实测/拆机数据，必须以实测为准并显式修正旧反推（标注废止）；
        ③ 评审任何"基于反推参数"的下游设计时，必须追问"是否已有实测数据可替代"。
      triggered_by: "teardown_vs_reverse_engineering_mismatch"
      cto_emphasis: true

    - id: "LESSON-007"
      date: "2026-05-28"
      domain: "cross_domain / process"
      title: "数字来源分级制度（POLICY-PROV-001）—— 每个进决策的数字必须标 L1-L4 来源等级"
      description: >
        DOC-AUDIT-SIM-001 暴露系统性缺陷：纸面/仿真数被措辞成"实测"，当成不可逆决策依据。
        典型 PF-1——算力裕量 27×/49× 是 L3 纸面解析值（树形 C 从未落地），却 LOCKED 芯片选型
        并触发不可逆采购；真实树形 C 实算为 17×/33×（纸面低估 1.6×）。
        强制制度（POLICY-PROV-001）：四级来源 L1 实测 / L2 仿真 / L3 解析估算 / L4 占位假设；
        数字后紧跟标签如"33× [L2 仿真/桌面树形C]"；按可逆性限制决策权重。
        三铁律：① L4 占位严禁作不可逆决策（采购/选型/流片）唯一依据；
        ② L3 解析支撑强约束决策必须挂"待 L1/L2 验证"标记、实测到位回填；
        ③ 措辞红线——严禁把 L2/L3/L4 说成"实测/已验证/确认"（"实测"仅限 L1）。
        Critic 强制检查 C1-C5（见 skill.md §11）：C1 未标等级=BLOCKER；C2 低等级冒充"实测"=BLOCKER；
        C3 L4 独撑不可逆决策=BLOCKER；C4 L3 撑难逆决策未挂待验证=MAJOR；C5 出处不可追溯=MAJOR。
      triggered_by: "audit_paper_value_locked_irreversible_procurement (PF-1)"
      cto_emphasis: true
      enforcement: "每次评审必查 C1-C5，C1/C2/C3 任一 FAIL 即整体 BLOCKER"

    - id: "LESSON-008"
      date: "2026-05-28"
      domain: "acoustics / cross_domain"
      title: "波束宽度半角/全角口径误读差点误导 CTO 撤销决策 —— 反转决策前先独立核验关键数字"
      description: >
        AC-WP01 初版报 1kHz BW=14.63° 并断言 numpy 有"因子-2 bug"，差点据此让 CTO 撤销 1kHz 超指向。
        经 DSP 审计 + 主 Claude 独立 MATLAB + Critic 独立阵因子复算三方推翻：14.63° 是单边半角
        （-6dB 交点 ±14.64°），正确 -6dB 全角=29.28°（=numpy 值），numpy 无 bug；脚本根因=max() 选中
        ±180° 端瓣 + 边界截断测成半宽。
        裁定/检查规则：① 项目统一口径 BW=全角=2×单边半角，半角必显式标注 ±/half；
        ② 一秒判据——-6dB 全角必 > -3dB 全角（本例 21.24°），若"-6dB BW"小于 -3dB BW 则必是半角或 bug；
        ③ 任何会推翻既有决策的关键数字，转报 CTO/据此行动前必须独立复算核验，不照单全收 teammate 结论；
        ④ 与 LESSON-007 呼应：14.63° 一度被当"MATLAB 实测"，正是把 L2 结果误信、未独立验证之过。
      triggered_by: "half_angle_vs_full_angle_misread (AC-WP01)"
      cto_emphasis: true
    - id: "LESSON-009"
      date: "2026-05-29"
      domain: "cross_domain / governance"
      title: "PF-8 估测当实测 + 实测与 LOCKED 冲突未重审 —— 几何 L0 目测被锁、'两条几何并存'掩盖近一个 Sprint"
      description: >
        阵元间距 d=30mm 系 Sprint2 视觉估测（L0 目测，无卡尺），却 LOCKED 进 DEC-S2-006 作几何基线；
        Sprint3 拆机实测 d=55mm（L1）与之冲突（孔径差 1.83×），但未触发对 DEC-S2-006 的重审，
        反被"自研 d=30 + 竞品 d=55 两条几何并存"合理化掩盖，直到 PF-8 审计才暴露、由 DEC-S3-GEOM-01 撤销。
        新维度：与 LESSON-007/008（标注/口径问题）不同，PF-8 是"冲突处置"问题——两个数字打架时谁说了算，
        光标注解决不了，需强制重审机制。
        裁定/检查规则（→ POLICY v1.2 + §11 C6）：① L0 等级（纯目测，比 L4 更严，严禁任何 LOCKED）；
        ② 铁律四——L1 实测与已 LOCKED 冲突即强制重审、禁"并存/折衷"、立即上报 PM+CTO；
        ③ C6 几何门禁——几何/尺寸 LOCKED 前必须 L1 实测证据，否则 BLOCKER；
        ④ 自省：锁 d=30 时 Critic 未拦（当时无 POLICY/无几何门禁/无 L0），制度缺位处 Critic 应主动补门。
      triggered_by: "visual_estimate_locked_as_geometry + measured_vs_locked_conflict_not_reviewed (PF-8)"
      cto_emphasis: true
    - id: "LESSON-010"
      date: "2026-05-29"
      domain: "cross_domain / governance"
      title: "PF-9 撤回未传播 —— 已撤回的派生值残留'实测'标签，喂养外部 AI 误引"
      description: >
        竞品 BW 14.9°/19.1°/16.0° 系竞品 SPL 4 点插值反推（L2/L3 派生，竞品只实测 SPL 无 BW），
        已被 F-AC-01 撤回；19.2° 更是 ITC 自仿 N16/d25 行张冠李戴。但撤回只在源头（sweep_report）发生，
        未全库反扫——full_teardown_v2.md（权威画像）等多处仍标"竞品实测 BW"无警示，
        外部 AI 顺势把它们引为"竞品 L1 实测"（C1+C2 双 FAIL/BLOCKER）。
        新维度：PF-6 是单点引用丢警示；PF-9 是"撤回未在全库传播"（系统性 + 撤回维度）。
        裁定/检查规则（→ POLICY v1.3 + §11 C7）：① 铁律五——撤回=撤回声明+全库反扫+逐处加标/删，三步缺一不生效；
        ② C7 撤回传播门禁——撤回后残留 ≥1 处未处理 = BLOCKER（C1–C6→C1–C7）；
        ③ 数字生命周期全闭环：C6 入口（防错误数字 LOCKED）+ C7 出口（防撤回值残留传播）+ 铁律四该改 + 铁律五改干净；
        ④ 制度对所有引用者平等（含外部 AI/CTO/未来成员）；内部残留是外部误引的直接喂养源，须自查。
      triggered_by: "retracted_derived_value_residue_fed_external_citation (PF-9, AI assistant cited as L1)"
      cto_emphasis: true
    - id: "LESSON-011"
      date: "2026-05-29"
      domain: "governance / positive_case"
      title: "POLICY 从'立'到'用'实战检验 —— teammate 派单阶段自行内化 POLICY + 铁律五反噬自身被自修复"
      description: >
        两个正面/自检验证据（详见 PF8_retrospective.md §8）：
        案例 A（C7 首次主动评审）：PF-9 立法后首个任务（仿真全景+竞品对比），在派单 prompt 阶段就钉死
        "禁 SPL→BW / 禁撤回值 / 仅同口径"三铁规；acoustic teammate **未等 Critic、自行拦下 3 个 PF-9 诱惑点**
        （插值反推竞品 BW / 117dB[L4] vs 竞品 106-111dB[L1] / 凑伪前后比）；Critic C1/C2/C7 复核全 PASS、零 BLOCKER。
        → 制度成熟最高信号 = teammate 产出前就不犯错（POLICY 从外部门禁内化为默认行为）；
        是 DEC-S3-PF4-01（守门拦截）→ PF-8/9（主动审计+立法）之后第三阶段"预防内化"。
        C7 二次主动评审（竞品对比定性，TASK-COMPQUAL-GATE）亦零 BLOCKER，连续两次零 BLOCKER = teammate 内化 POLICY 的硬证据。
        案例 B（铁律五反噬自身）：E-NEW-3 清扫完成、C7 残留 0 后，audit §2/页脚却仍写"未执行清扫"
        （"已完成"状态未传播），被后续 Critic 读 stale 页脚误导一次，PM 核实并修复。
        → 状态变更（含"已完成/已撤回"状态位，非只数值）也须按铁律五全库传播；"工单完成"收尾须回填所有引用其状态的文档。
        检查规则：① Critic 复核应认可"teammate 自拦"为正向信号、计入 teammate 内化度；
        ② 任何工单/撤回"完成"时，Critic 终审查"状态是否全库传播"（铁律五含状态位，不只数值）。
      triggered_by: "policy_v1.3_first_proactive_review_zero_blocker + ironrule5_self_applied_to_status_propagation"
      cto_emphasis: true

    - id: "LESSON-012"
      date: "2026-05-29"
      domain: "governance / methodology / positive_case"
      title: "三轨独立工具验证（numpy + MATLAB-agent + MATLAB-CTO）M1-M3 各项对照通过、零 BLOCKER —— 坐实双轨/三轨独立工具复核价值，支撑 POLICY v1.4"
      description: >
        C7 第三次主动评审（TASK-MATLAB-RV），双轨/三轨独立工具验证维度首次。
        acoustic teammate 对 6 指标（SLL/WNG/DI/MC/超指向/8路等价）用三条独立实现轨
        （numpy/scipy、本 agent MATLAB R2026a、CTO MATLAB）逐项对照，d=55 几何。
        Critic 复核全 PASS（C1/C2/C7 三门禁零 BLOCKER），并**独立用 Python 复算 4 个关键值不全信**：
        WNG 标称 11.868dB ✓、WNG 草稿 bug −0.173dB ✓（误差恰=10log10(16)=12.041dB）、
        BW 标称 29.269° ✓、MVDR ε=0.3/0.01/0.003 BW 24.96/22.87/22.19° + WNG 10.94/4.57/−2.08dB ✓，
        全部 bit 级吻合 → 确认三轨一致非编造。
        **核心证据**：M1 WNG 草稿 bug（公式多除 |a|²=N，致 12dB 量级偏差）在落盘前被三轨交叉核
        **当场抓出并精确定位为"numpy 草稿错、MATLAB/CTO 对"**，Critic 独立数学验证定位正确。
        → 这是"双轨/三轨独立工具复核"价值的硬证据：12dB 量级笔误若单轨开发将直接落盘，
        三轨交叉使其在发布前即被拦截并定位错源。E-MATLAB-1（两轨发散触发器）未触发，
        独立确认无漏报发散（MC 8-pair@1k 三轨 5.33-6.27% 落 ~2σ 收敛，Critic 第4种子 MC 同量级）。
      check_rule: >
        ① 凡涉关键数值结论的仿真交付，倡导≥双轨独立工具实现 + 交叉核（不同工具/不同种子）；
        ② Critic 终审须自己独立复算 1-2 个 load-bearing 值，不全信 teammate 自述的"三轨一致"；
        ③ teammate 草稿期自纠的笔误（未落盘）记为正向信号，非 BLOCKER，但须确认错源定位正确。
      supports: "POLICY v1.4（双轨/三轨独立工具复核机制入制）"
      triggered_by: "policy_v1.3_third_proactive_review_multitrack_tool_verification_zero_blocker"
      cto_emphasis: true
      followup_note: >
        标准12点合规补算（TASK-STD-A-RV，C7 第四次主动评审）亦零 BLOCKER；连续四次零 BLOCKER。
        关键防线 = 180° isotropic artifact（AF(180°)=AF(0°)→≈0dB）未被误报达标/不达标（全标"现模型不可评，待COMSOL障板+消声室"），
        且平面口径假设（阵列波束平面=表9水平面，依赖音柱水平安装）已显式声明 + 竖装失效条件诚实标注。
        Critic 独立 Python(scipy chebwin) 复算 R8=5.8574dB（一级裕量+0.857dB）与 2k/90°=23.01dB（仅二级）逐点吻合到 0.001dB，确认三轨一致非编造。
        A1/A2/A3（静态加权/FIB/决策）复核：A2 一处 PF-9 复发（撤回竞品 19.1° 称'实测'作锚点）被 C7 第五次主动评审当场抓出并修复——**C7 实战首次"抓到 BLOCKER"，印证门禁有效（非走过场）**；子带标量加深零成本关 R10 主张独立验证成立。

    - id: "LESSON-013"
      date: "2026-05-30"
      domain: "governance / process"
      title: "信息透明义务 —— docx 5-28 入手、5-30 才入库，活跃产出期未用上；CTO 层缺 24h 入库机制 → 催生 POLICY v1.5（铁律六 + C8）"
      description: >
        `定向音柱AI数据.docx` 硬件团队 2026-05-28 发 CTO，CTO 2026-05-30 才转 PM/agent team 进 KB
        （间隔 ~2 天，超 24h）。期间 Sprint 3 活跃产出（三轨独立工具验证 / 仿真全景 panorama /
        标准 12 点合规 standard_check）全部未用上该 docx 信息（典型后果：R3 SPL 仍占位流通，
        未被 docx 中可能的硬件实测/datasheet 替换）。
        根因：**CTO 层外部信息流无 24h 强制入库机制**——信息"已入手（到 CTO 手里）"但"未入库（没进 KB / 没同步 handover）"，
        下游 agent team 看不见 = 等于没收到。
        新维度（与 PF-9 对偶）：PF-9 = 已撤回未清扫（数字该出库却赖在库里）= **出站**（铁律五/C7 守）；
        本次 = 已入手未入库（数字该进库却卡在 CTO 手里）= **入站**——数字生命周期另一端的盲区。
        裁定/检查规则（→ POLICY v1.5）：
        ① 铁律六「信息透明义务」——凡 CTO 收到的外部技术输入（硬件参数/datasheet/测试报告/标准/客户反馈），
           24h 内须进 KB + handover 同步，由 CTO 通过 PM 触发归档（与铁律五"出站"对照，本条守"入站"）；
        ② Critic C8 入库传播门禁——C7（撤回/出站）+ C8（入库/入站）双向门禁，Sprint 收尾归档时 Critic
           必须复核"近 1 周 CTO 外部接收入库状态"，超 24h 未入库/未入库 = BLOCKER（C1–C7 → C1–C8）；
        ③ 数字生命周期全闭环升级为两端：入站 C8/铁律六 + 出口 C7/铁律五 + 入口 C6 + 冲突铁律四 + 双轨核（v1.4）。
        定位：**非惩罚性预防**——Sprint 4 / 量产阶段外部输入更多更频，入库盲区风险上升，提前补门。
        产物：POLICY_v15_draft.md（草案 A 双轨核[v1.4/LESSON-012] + 草案 B 入库传播[v1.5] + 草案 C 整合），DRAFT 待 CTO 审批。
      triggered_by: "external_doc_received_2days_late_not_in_KB_active_outputs_missed_it (inbound dual of PF-9 outbound)"
      cto_emphasis: true
      preventive_non_punitive: true
      supports: "POLICY v1.5（铁律六 信息透明义务 + Critic C8 入库传播门禁；与 v1.4 双轨核同批整合）"

    - id: "LESSON-014"
      date: "2026-06-02"
      domain: "governance / process"
      title: "FIRA 适配评估暴露两个 HIGH 风险（定点 bit-exact / Split-Task 非 1:1 替换）只活在评估文档 → 强制登记 R14 + Sprint4 输入 + C9 不可逆闸门（CTO 拍板）"
      description: >
        `fira_fit_assessment.md`（双轨核通过，总判定"部分适配"）暴露两个 HIGH 级问题：
        ① FIRA 定点 Q15↔Q31 bit-exact 映射"HIGH 风险待实测"；② 我方树形非 1:1 FIRA 替换，需 Split-Task 手动切分。
        风险：HIGH 级预警若只活在一份评估文档、不进 R-list / Sprint 4 输入，将来上板若指向性/精度对不上桌面验证，
        无人记得曾被预警 —— 这是 **PF-9（预警丢失/撤回未传播）的同类陷阱**（数字/预警该传播却卡在单文档）。
        裁定/检查规则（→ POLICY 铁律八 + Critic C9）：
        ① **R14 入 R-list**（全强制字段：编号/风险/等级/验证状态/数据出处/可逆性影响/风险声明/挂接，见 decisions_log）；
        ② **Split-Task 入 Sprint 4 输入清单**（DOC-S4-INPUT-01，标 HIGH 复杂度 + dsp 三项 migration 待办：哪些下 FIRA/哪些留核内/bit-exact 回归怎么验）；
        ③ **不可逆闸门（C9，BLOCKER）**：R14 关闭（EZKIT bit-exact L1 实测通过）前，严禁把"FIRA offload 算力收益"写进任何选型/流片/客户承诺依据；选型/承诺只许引纯核裕量。
        定位：**非惩罚性预防**——把"上板才能验"的加速器收益与"已坐实"的纯核口径严格隔离，防 PF-1（纸面当实测）+ PF-9（预警丢失）复合。
      wording_redline_examples:   # 措辞红线正反示例（与 §11 C9 / 铁律八 并列，CTO 指定纳入）
        negative_wrong: "❌ '算力裕量 33× + FIRA offload 进一步提升，选型按提升后算'（FIRA 收益未实测却计入选型依据 = C9② BLOCKER）"
        positive_correct: "✅ '纯核裕量 33×(8ch)[L1待实测，dsp_8ch_report.md §4.3]；FIRA offload 为上板后优化空间，收益未实测[L4/待验证]，不计入选型依据（见 R14）'"
      triggered_by: "fira_assessment_HIGH_risks_lived_only_in_one_doc_not_in_Rlist_or_sprint4_input (PF-9-class warning-loss)"
      cto_emphasis: true
      preventive_non_punitive: true
      supports: "POLICY 铁律八（加速器收益不可逆闸门）+ Critic C9（FIRA-offload 不可逆门禁，①②BLOCKER/③④MAJOR）；挂接 R14 / DEC-S3-PROC-01 / Split-Task(DOC-S4-INPUT-01)"

    - id: "LESSON-015"
      date: "2026-06-03"
      domain: "DSP / FIRA / verification process"
      title: "R14 端到端假绿 + FIRA D1/D2 I/O 契约垃圾 — critic 连漏两次结构性问题、均由 CTO 兜住 → 立 §12 DSP/FIRA 验证专项门"
      description: >
        两次连漏（均非 critic/门禁拦下，由 CTO 挑战兜住，是 critic 命门）：
        ① 假绿：fira_tfb_* 占位（FIRA 段 memset 0、fira_postscale 从未调），输出 out=in；核 golden 是 PR telescoping out=in
           → 端到端单通道 CRC（0x90556BC7=CRC(in)）两者皆撞、零真 FIRA 仍 PASS=1。根因：完美重建 telescoping 是
           代数恒等、与滤波系数无关（PF-4 Sub-1 已注"PR 与系数精度无关"），端到端 CRC 验不了滤波/加速器段。
        ② D1/D2 I/O 契约垃圾：真 FIRA 接好后首板验输出非单调/带负/比值乱，且只改 harness 全局（FIRA 段未动）输出就变。
           静态查出 fira_tree.c 两结构 bug：D1 输入过读（nInputBuffCount=ntaps+window-1 远超级联 buffer 有效样本→读未初始化）；
           D2 postscale 双重抽取（FIRA 已抽 + postscale 又按 ratio=2 抽→out 只填一半、留未初始化尾）；共用 scratch 段间不清零。
        裁定（→ skill.md §12 DSP/FIRA 验证专项门，与 C1-C10 并列）：
        FG1 假绿恒等盲区（比对取依赖被测物的中间值如子带 + 必证占位版 FAIL）；FG2 占位冒充实测（跑占位版确认 FAIL）；
        IO1 加速器 I/O 缓冲契约（输入≥已初始化 nInputBuffCount / 后处理恰填 out_count / scratch 段间清零 / DMA 读前 cache 失效）；
        IO2 布局敏感=读未初始化越界（哨兵 A/B 隔离）；ST1 流式状态一致。FG1/FG2/IO1/IO2 任一 FAIL=BLOCKER。
        定位：非惩罚性预防——把"测试是否真验了被测物"+"加速器 I/O 内存契约"固化成门，堵代数恒等假绿 + 未初始化/越界垃圾两类命门。
      triggered_by: "R14_end_to_end_false_green_placeholder_passed + FIRA_D1_D2_io_buffer_contract_garbage_caught_by_CTO_not_critic"
      cto_emphasis: true
      preventive_non_punitive: true
      supports: "skill.md §12 DSP/FIRA 验证专项门（FG1/FG2/IO1/IO2/ST1）；挂接 R14 / DEC-S4-R14-GRANULARITY / fira_tree.c(D1/D2) / decisions_log「R14 假绿回退」「F4b 首板验」"
```

### 6.3 Pattern Library

```yaml
pattern_library:
  high_risk_indicators:
    - pattern: "Agent submits right before deadline"
      risk: "Rushed work, insufficient self-check"
      action: "Increase review depth; expect more issues"
      
    - pattern: "Large deliverable (>50 pages) with short estimation"
      risk: "Underestimated effort, possible quality compromise"
      action: "Verify scope alignment with task description"
      
    - pattern: "First submission from new agent"
      risk: "Unfamiliar with standards and expectations"
      action: "Full checklist review; extra guidance in feedback"
      
    - pattern: "Agent's 3rd+ revision of same deliverable"
      risk: "Agent struggling with concept or fix"
      action: "Consider escalation; may need expert consultation"
      
    - pattern: "Deliverable with no self-identified issues"
      risk: "Overconfidence or insufficient self-review"
      action: "Extra vigilance; likely issues present"
      
  quality_predictors:
    - predictor: "Agent first_pass_rate > 80%"
      prediction: "Likely PASSED or PASSED_WITH_MINOR"
      confidence: 0.85
      
    - predictor: "Agent avg_findings > 4 per review"
      prediction: "Likely FAILED on first submission"
      confidence: 0.75
      
    - predictor: "Deliverable modifies critical safety component"
      prediction: "High probability of BLOCKER findings"
      confidence: 0.70
```

## 7. Learning & Adaptation Rules

```yaml
learning_rules:
  per_review:
    - "Record all findings with severity and category"
    - "Track resolution time and cycles"
    - "Identify pattern matches with known error types"
    - "If finding was incorrect → log false positive with reason"
    
  per_escaped_defect:
    - "Immediate checklist update"
    - "Root cause analysis: why was it missed?"
    - "Update detection patterns"
    - "Share lesson with all agents via PM"
    
  per_week:
    - "Review finding distribution trends"
    - "Identify agents needing attention"
    - "Update review depth recommendations"
    
  per_sprint:
    - "Review false positive rate; adjust sensitivity if needed"
    - "Update checklist effectiveness scores"
    - "Identify checklist items to add/remove/modify"
    - "Generate agent coaching recommendations for PM"
    
  per_project:
    - "Full calibration of severity assignment accuracy"
    - "Review agent improvement trends"
    - "Update standards library with any new applicable standards"
    - "Archive lessons and patterns"
    - "Generate Critic performance report for CTO"
```

---

*Critic Agent Memory v1.0.0 — Learning from Every Finding, Every Mistake, Every Success*


---

## 2026-06-06 轮次教训（R24-R34 实战，下一轮 = R35）

> 完整预防清单：`sprint6/STAGE4_BRINGUP_CHECKLIST.md`。本节是门禁侧增量规则。

- **同源自证盲区（R25）**：guard-stub 按与实现同一份情报写 → 参数计数/类型错结构性测不出（mock 7 参、hook 7 参、永远 PASS）。同源项唯一闭合 = 板上 grep 原文；审 stub 时必查情报源是否独立。
- **FG 升级义务（R27）**：FG「存在性」全绿伴 62× 率错 = §12 FG 的实战盲区。周期激励的 FG 必须含「率在带」判据（FG-B' [950,1050]Hz 类）；审 harness 时问「这个 FG 验的是存在还是正确」。
- **点估须带误差带（R27 F27-MAJOR-1）**：反推量（62kHz）无误差带 = 不合格；敏感性扫描出下界（10kHz）后定性结论才稳。
- **聚合实测数 relabel 强制（R27/T2 闭合）**：拆解（99.8% ISR vs 0.2% DMA）后才许标签；凡引必带 relabel，禁裸引——已入 DEC-S5-T2-CLOSURE-01。
- **「保守闭合 ≠ clean 闭合」互替禁止（R28）**：不得据保守闭合称已 [L1] 实测，不得因 clean 未达否定过线。
- **harness/产品 build 边界（R34）**：审放置/占用类主张先问「这产物在哪个 build」——把 harness .map 当产品事实 = 前提为假（总工④实例）。
- **审查型角色变体（R34）**：架构建议审查 = 三态判定（数据支撑/盲点/错误）+ 抓漏耦合 + 不替 CTO 裁；与过门 verdict 并列的第二种产出形态。
- 轮次记录：R24 hooks 实现 / R25 MDMA 符号修复（板 grep 情报）/ R26 .map 放置判定 / R27 读数异常 / R28 T2 保守闭合 / R29 O1 EQ / R30 H2R 重测包 / R31 M1 survey / R32 M1 事实库 / R33 数据表轻门 / R34 架构审查。
