---
name: project-manager-memory
description: >
  Project Manager Agent的记忆配置文件。
  包含项目历史数据、团队能力图谱、风险库和调度策略优化记录。
  所有记忆条目均可学习和更新，驱动PM Agent的持续改进。
version: 1.0.0
author: ITC Architecture Team
---

# Project Manager Agent — Memory

## 1. Memory Architecture

```
Memory Store
├── Project History          # 已完成项目的完整记录
│   ├── Task Records         # 每个任务的执行数据
│   ├── Schedule Data        # 计划vs实际对比
│   └── Quality Metrics      # 质量相关指标
│
├── Team Capability Map      # 各Agent的能力画像
│   ├── Domain Expertise     # 领域专长评分
│   ├── Performance Metrics  # 历史性能数据
│   └── Workload History     # 负载和效率记录
│
├── Risk Library             # 历史风险模式与解决方案
│   ├── Risk Patterns        # 风险类型和触发条件
│   ├── Mitigation Playbook  # 应对措施库
│   └── Outcome Records      # 风险处理结果
│
└── Scheduling Heuristics    # 调度策略优化记录
    ├── Estimation Models    # 各领域估算校准
    ├── Priority Rules       # 优先级规则演进
    └── Reallocation Log     # 资源调整历史
```

## 2. Project History

### 2.1 Task Records

```yaml
task_record_template:
  task_id: "TASK-{project}-{seq}"
  project: "project_name"
  name: "task_name"
  domain: "acoustics|dsp|hardware|structure|test"
  assigned_agent: "agent_id"
  
  # Estimation
  estimated_hours: 0.0       # 初始估算
  actual_hours: 0.0          # 实际耗时
  estimation_error_pct: 0.0  # (actual - estimated) / estimated
  
  # Timeline
  created_at: "ISO8601"
  assigned_at: "ISO8601"
  started_at: "ISO8601"
  submitted_at: "ISO8601"
  reviewed_at: "ISO8601"
  completed_at: "ISO8601"
  
  # Quality
  critic_cycles: 0           # 通过Critic所需的轮次
  findings_total: 0          # Critic发现的问题总数
  findings_by_severity:
    BLOCKER: 0
    MAJOR: 0
    MINOR: 0
    INFO: 0
  final_verdict: "PASSED|FAILED"
  
  # Dependencies
  depended_on: []            # 依赖的任务ID列表
  blocked_tasks: []          # 被阻塞的任务ID列表
  
  # Status
  status: "COMPLETED|ARCHIVED"
  tags: []
```

### 2.2 Historical Task Database (Example Entries)

```yaml
project_history:
  project: "ITC-Pro-2024-Q1"
  tasks:
    - task_id: "TASK-ITCQ1-001"
      name: "Acoustic Cavity FEM Simulation"
      domain: "acoustics"
      agent: "acoustics-agent"
      estimated_hours: 8.0
      actual_hours: 11.5
      estimation_error_pct: 43.75
      critic_cycles: 2
      findings_total: 3
      findings: { BLOCKER: 0, MAJOR: 1, MINOR: 2, INFO: 0 }
      root_cause_delay: "Mesh convergence slower than expected; MAJOR finding on boundary condition validation"
      lesson: "Acoustic FEM tasks need +50% buffer for mesh convergence; require preliminary mesh study"
      
    - task_id: "TASK-ITCQ1-005"
      name: "DSP Filter Coefficient Calculation"
      domain: "dsp"
      agent: "dsp-agent"
      estimated_hours: 6.0
      actual_hours: 5.5
      estimation_error_pct: -8.33
      critic_cycles: 1
      findings_total: 1
      findings: { BLOCKER: 0, MAJOR: 0, MINOR: 1, INFO: 0 }
      lesson: "DSP coefficient tasks well-estimated; agent has strong track record"
      
    - task_id: "TASK-ITCQ1-012"
      name: "PCB Layout for Amplifier Stage"
      domain: "hardware"
      agent: "hardware-agent"
      estimated_hours: 12.0
      actual_hours: 18.0
      estimation_error_pct: 50.0
      critic_cycles: 3
      findings_total: 7
      findings: { BLOCKER: 1, MAJOR: 2, MINOR: 3, INFO: 1 }
      root_cause_delay: "Thermal layout iteration; BLOCKER on clearance violation"
      lesson: "Hardware PCB layout: always include thermal simulation step; add DRC pre-check"
```

### 2.3 Schedule Performance Data

```yaml
schedule_performance:
  project: "ITC-Pro-2024-Q1"
  
  planned_vs_actual:
    milestone_1_plan: "2024-01-15"
    milestone_1_actual: "2024-01-17"
    milestone_1_delay_days: 2
    
    milestone_2_plan: "2024-02-01"
    milestone_2_actual: "2024-02-05"
    milestone_2_delay_days: 4
    
  spi_trend: [1.0, 0.95, 0.92, 0.88, 0.90]  # Schedule Performance Index over time
  
  critical_path_accuracy:
    predicted_critical_tasks: ["T001", "T005", "T012"]
    actual_critical_tasks: ["T001", "T005", "T012", "T008"]
    accuracy_pct: 75.0
    miss: "T008 (DSP unit test) became critical due to acoustic delay ripple"
```

## 3. Team Capability Map

### 3.1 Domain Agent Profiles

```yaml
team_capability:
  agents:
    - agent_id: "acoustics-agent"
      domain: "acoustics"
      expertise:
        FEM_simulation: 0.92        # 0-1 proficiency score
        acoustic_measurement: 0.88
        speaker_design: 0.85
        room_acoustics: 0.70
        
      performance_metrics:
        tasks_completed: 23
        avg_estimation_error_pct: 35.0   # tends to underestimate
        avg_critic_cycles: 1.8
        first_pass_rate_pct: 55.0        # 55% pass on first try
        avg_task_duration_hours: 12.5
        on_time_delivery_pct: 78.0
        
      workload:
        current_tasks: 2
        max_capacity: 3
        utilization_pct: 67.0
        
      calibration:
        estimation_bias: "underestimate"
        recommended_buffer_pct: 40.0     # add 40% to acoustic estimates
        strength: "Deep technical expertise; high quality output"
        weakness: "Tends to underestimate complex simulation time"
        
    - agent_id: "dsp-agent"
      domain: "dsp"
      expertise:
        filter_design: 0.95
        fft_analysis: 0.93
        real_time_processing: 0.87
        codec_implementation: 0.82
        
      performance_metrics:
        tasks_completed: 31
        avg_estimation_error_pct: -5.0   # slight overestimate (good)
        avg_critic_cycles: 1.2
        first_pass_rate_pct: 82.0
        avg_task_duration_hours: 8.0
        on_time_delivery_pct: 94.0
        
      workload:
        current_tasks: 1
        max_capacity: 3
        utilization_pct: 33.0
        
      calibration:
        estimation_bias: "slight_overestimate"
        recommended_buffer_pct: 5.0
        strength: "Excellent estimator; high first-pass rate"
        weakness: "Can be slow on novel algorithm research tasks"
        
    - agent_id: "hardware-agent"
      domain: "hardware"
      expertise:
        pcb_design: 0.90
        schematic_capture: 0.88
        thermal_analysis: 0.75
        emc_compliance: 0.72
        
      performance_metrics:
        tasks_completed: 19
        avg_estimation_error_pct: 42.0
        avg_critic_cycles: 2.3
        first_pass_rate_pct: 48.0
        avg_task_duration_hours: 15.0
        on_time_delivery_pct: 68.0
        
      workload:
        current_tasks: 2
        max_capacity: 3
        utilization_pct: 67.0
        
      calibration:
        estimation_bias: "underestimate"
        recommended_buffer_pct: 45.0
        strength: "Comprehensive PCB design skills"
        weakness: "Frequently misses thermal and DRC issues; high revision rate"
        
    - agent_id: "structure-agent"
      domain: "structure"
      expertise:
        cad_modeling: 0.91
        thermal_design: 0.83
        mold_design: 0.78
        dfm_analysis: 0.80
        
      performance_metrics:
        tasks_completed: 15
        avg_estimation_error_pct: 15.0
        avg_critic_cycles: 1.5
        first_pass_rate_pct: 68.0
        avg_task_duration_hours: 10.0
        on_time_delivery_pct: 85.0
        
      workload:
        current_tasks: 1
        max_capacity: 2
        utilization_pct: 50.0
        
      calibration:
        estimation_bias: "slight_underestimate"
        recommended_buffer_pct: 20.0
        strength: "Solid CAD skills; good DFM awareness"
        weakness: "Mold design tasks need more time"
        
    - agent_id: "test-agent"
      domain: "test"
      expertise:
        test_planning: 0.90
        automation: 0.85
        audio_measurement: 0.88
        reliability_testing: 0.80
        
      performance_metrics:
        tasks_completed: 27
        avg_estimation_error_pct: 10.0
        avg_critic_cycles: 1.3
        first_pass_rate_pct: 78.0
        avg_task_duration_hours: 9.0
        on_time_delivery_pct: 88.0
        
      workload:
        current_tasks: 1
        max_capacity: 3
        utilization_pct: 33.0
        
      calibration:
        estimation_bias: "neutral"
        recommended_buffer_pct: 10.0
        strength: "Consistent performer; good test coverage"
        weakness: "Reliability testing takes longer than estimated"
```

### 3.2 Team Summary Dashboard

```
┌────────────────┬──────────┬──────────┬──────────┬──────────┬──────────────┐
│ Agent          │ Tasks    │ Est.     │ Critic   │ On-Time  │ Capacity     │
│                │ Done     │ Error%   │ Cycles   │ %        │ (used/max)   │
├────────────────┼──────────┼──────────┼──────────┼──────────┼──────────────┤
│ acoustics      │ 23       │ +35%     │ 1.8      │ 78%      │ 2/3          │
│ dsp            │ 31       │ -5%      │ 1.2      │ 94%      │ 1/3          │
│ hardware       │ 19       │ +42%     │ 2.3      │ 68%      │ 2/3          │
│ structure      │ 15       │ +15%     │ 1.5      │ 85%      │ 1/2          │
│ test           │ 27       │ +10%     │ 1.3      │ 88%      │ 1/3          │
├────────────────┼──────────┼──────────┼──────────┼──────────┼──────────────┤
│ TEAM AVG       │ 115      │ +19.4%   │ 1.62     │ 82.6%    │ 7/14 (50%)   │
└────────────────┴──────────┴──────────┴──────────┴──────────────┴──────────────┘
```

## 4. Risk Library

### 4.1 Risk Pattern Database

```yaml
risk_library:
  patterns:
    - risk_id: "RISK-001"
      name: "Acoustic Simulation Convergence Failure"
      category: "technical"
      domains: ["acoustics"]
      frequency: 3                    # times encountered
      detection_signals:
        - "FEM mesh quality score < 0.7"
        - "Solver iteration count > 1000"
        - "Residual error plateau > 1e-3"
      typical_impact:
        delay_hours: 8.0
        affected_downstream: ["dsp", "structure"]
      root_causes:
        - "Complex geometry with sharp edges"
        - "Inadequate mesh refinement"
        - "Material property uncertainty"
      mitigations:
        - "Pre-run mesh convergence study (add 4h upfront)"
        - "Use simplified geometry for initial pass"
        - "Engage acoustics expert for complex geometries"
      effectiveness_rating: 0.85
      
    - risk_id: "RISK-002"
      name: "DSP Algorithm Real-Time Performance Gap"
      category: "technical"
      domains: ["dsp"]
      frequency: 2
      detection_signals:
        - "MIPS estimate exceeds target processor capacity"
        - "Latency calculation > requirement"
        - "Memory footprint > available RAM"
      typical_impact:
        delay_hours: 12.0
        affected_downstream: ["hardware"]
      root_causes:
        - "Algorithm complexity underestimated"
        - "Target platform specs unclear"
        - "No early prototype on target hardware"
      mitigations:
        - "Early MIPS budget allocation"
        - "Algorithm complexity analysis before implementation"
        - "Keep fallback simplified algorithm option"
      effectiveness_rating: 0.90
      
    - risk_id: "RISK-003"
      name: "PCB Layout Thermal Issue"
      category: "technical"
      domains: ["hardware"]
      frequency: 4
      detection_signals:
        - "Power density > 0.5W/cm²"
        - "No thermal vias in high-power regions"
        - "Component junction temp estimate > 80% of max"
      typical_impact:
        delay_hours: 10.0
        affected_downstream: ["test", "structure"]
      root_causes:
        - "Thermal simulation skipped or late"
        - "Compact layout prioritizes space over thermal"
        - "High-power components clustered"
      mitigations:
        - "Mandatory thermal simulation checkpoint before layout finalization"
        - "Thermal design guidelines checklist"
        - "Early engagement with structure for heat sink design"
      effectiveness_rating: 0.80
      
    - risk_id: "RISK-004"
      name: "Cross-Domain Interface Mismatch"
      category: "integration"
      domains: ["all"]
      frequency: 5
      detection_signals:
        - "Interface spec versions differ between domains"
        - "Data format incompatibility in integration test"
        - "Physical dimensions don't match between structure and acoustics"
      typical_impact:
        delay_hours: 6.0
        affected_downstream: ["test"]
      root_causes:
        - "Interface specs updated without cross-domain notification"
        - "No central interface registry"
        - "Late integration testing"
      mitigations:
        - "Interface Control Document (ICD) maintained by PM"
        - "Weekly cross-domain interface sync"
        - "Early stub/mock integration test"
      effectiveness_rating: 0.88
      
    - risk_id: "RISK-005"
      name: "Scope Creep from Stakeholder"
      category: "project"
      domains: ["all"]
      frequency: 2
      detection_signals:
        - "New requirements after architecture freeze"
        - "'Can we also add...' requests"
        - "Requirements document version > 3.0"
      typical_impact:
        delay_hours: 16.0
        affected_downstream: ["all"]
      root_causes:
        - "Weak requirements change control"
        - "No formal change request process"
        - "Stakeholder not aligned on MVP"
      mitigations:
        - "Formal change request process with impact analysis"
        - "MVP vs Phase 2 explicit separation"
        - "CTO as change request approver"
      effectiveness_rating: 0.92
```

### 4.2 Risk Register (Current Project)

```yaml
current_risk_register:
  project: "ITC-Pro-2024-Q2"
  risks:
    - risk_id: "R-001"
      description: "New DSP chip availability delayed by supplier"
      probability: 0.30
      impact: "HIGH"
      score: 0.30                       # probability × impact_weight
      owner: "hardware-agent"
      status: "MONITORING"
      mitigation: "Qualify alternative chip; maintain dual-design until confirmation"
      contingency: "Switch to alternative with 2-week buffer"
      trigger: "Supplier confirmation deadline: 2024-03-15"
      
    - risk_id: "R-002"
      description: "Acoustic target curve may change based on listening test"
      probability: 0.50
      impact: "MEDIUM"
      score: 0.25
      owner: "acoustics-agent"
      status: "ACTIVE"
      mitigation: "Early listening test with rough prototype; validate curve before DSP design"
      contingency: "DSP design parameterized for easy curve adjustment"
```

## 5. Scheduling Heuristics

### 5.1 Estimation Calibration Models

```yaml
estimation_calibration:
  # Per-domain calibration factors based on historical data
  domain_factors:
    acoustics:
      raw_estimate_multiplier: 1.40    # add 40%
      variance: 0.25
      confidence_interval_95: "estimate × [1.15, 1.75]"
      
    dsp:
      raw_estimate_multiplier: 1.05    # add 5%
      variance: 0.10
      confidence_interval_95: "estimate × [0.95, 1.20]"
      
    hardware:
      raw_estimate_multiplier: 1.45    # add 45%
      variance: 0.30
      confidence_interval_95: "estimate × [1.15, 1.90]"
      
    structure:
      raw_estimate_multiplier: 1.20    # add 20%
      variance: 0.15
      confidence_interval_95: "estimate × [1.05, 1.45]"
      
    test:
      raw_estimate_multiplier: 1.10    # add 10%
      variance: 0.12
      confidence_interval_95: "estimate × [0.98, 1.28]"
  
  # Task-specific adjustments
  task_type_adjustments:
    novel_work: 1.30                   # 30% premium for first-time tasks
    repeat_work: 0.80                  # 20% discount for similar past tasks
    integration_task: 1.25             # 25% premium for cross-domain integration
    review_cycle_buffer: "+1 cycle for hardware, +0.5 for others"
```

### 5.2 Priority Rules (Evolved)

```yaml
priority_rules:
  version: 3                          # incremented when rules change
  last_updated: "2024-01-10"
  
  rules:
    - id: "PR-001"
      name: "Critical Path Priority"
      condition: "task is on critical path"
      action: "priority = max(current, P1_HIGH)"
      weight: 1.0
      effectiveness: 0.95
      
    - id: "PR-002"
      name: "Fan-Out Priority"
      condition: "task has > 2 downstream dependents"
      action: "priority += 1 level"
      weight: 0.80
      effectiveness: 0.88
      
    - id: "PR-003"
      name: "High-Risk Early Start"
      condition: "task risk_score > 0.6 AND estimated_hours > 8"
      action: "start immediately after dependencies met; add 20% buffer"
      weight: 0.75
      effectiveness: 0.82
      
    - id: "PR-004"
      name: "Quick Win Insertion"
      condition: "task estimated_hours < 4 AND priority >= P2_NORMAL"
      action: "can be inserted between larger tasks if no dependency conflict"
      weight: 0.60
      effectiveness: 0.70
      
    - id: "PR-005"
      name: "Agent Load Balancing"
      condition: "one agent utilization > 90% AND another same-domain agent < 50%"
      action: "reassign pending tasks to underutilized agent"
      weight: 0.85
      effectiveness: 0.90
```

### 5.3 Reallocation Decision Log

```yaml
reallocation_log:
  - timestamp: "2024-01-08T14:30:00Z"
    from_agent: "hardware-agent"
    to_agent: "hardware-agent-2"
    task_id: "TASK-012"
    reason: "hardware-agent overloaded (3 tasks, 105% utilization); reallocation to balance"
    outcome: "Successful; task completed on time"
    lesson: "Monitor utilization > 90% trigger for reallocation"
    
  - timestamp: "2024-01-10T09:15:00Z"
    task_id: "TASK-008"
    action: "Split task into two parallel subtasks"
    reason: "Original task (20h) blocking 3 downstream tasks; split by module"
    outcome: "Reduced critical path by 6 hours"
    lesson: "Tasks > 16h on critical path should be evaluated for splitting"
```

## 6. Learning & Adaptation Rules

```yaml
learning_rules:
  # Triggered after each task completion
  per_task_update:
    - "Update agent's avg_estimation_error with exponential moving average (α=0.3)"
    - "Increment tasks_completed counter"
    - "Update critic_cycles average"
    - "If estimation_error > 30%, flag for calibration review"
  
  # Triggered after each sprint
  per_sprint_update:
    - "Recalculate domain calibration factors"
    - "Update priority rule effectiveness scores"
    - "Review and update risk library with new observations"
    - "Generate sprint retrospective insights"
  
  # Triggered after each project
  per_project_update:
    - "Full recalibration of all estimation models"
    - "Update team capability scores"
    - "Archive risk patterns and outcomes"
    - "Generate project post-mortem report"
    - "Update scheduling heuristics based on project outcomes"
```

---

## 7. ITC 定向音柱项目 — 实战记忆（2026 Sprint 2–3）

### 7.1 关键技术发现
- **ADSP-21569 真实参数已核实**：单核 SHARC+ **1 GHz**；片上 SRAM **640 KB L1 + 1024 KB L2**；封装 **400-ball CSP_BGA，17×17 mm**。无 ARM、无网络、无显示屏。
- **推荐采购型号：ADSP-21569KBCZ10**（CTO 指定）。
  > ⚠️ 待办：订货号后缀须在**发 PO 前 web 核实**——Sprint 2 BOM 曾写作 `ADSP-21569KBCZ-1A`，与 `KBCZ10` 不一致，需对 ADI 官方料号表统一确认（勿凭印象定型号）。

### 7.2 关键警示（教训）
- **频率误标教训**：本项目早期曾把 ADSP-21569 主频**误标为 500MHz**（实际 1 GHz）。芯片关键参数若凭印象/记忆给出，会一路传导到算力预算、子带方案、BOM，造成系统性错误。**任何芯片/器件参数落档前必须核实。**

### 7.3 用户（CTO）偏好 — 强约束
- **所有技术参数必须 web 核实，不接受凭印象给数据。** 适用于：芯片频率/SRAM/封装/料号、器件 datasheet 参数、专利号/状态、竞品规格。不确定的标"待核实"，不得编造。
- 关联：CTO 善用对抗式 Critic，重视"诚实暴露问题"胜过"漂亮结论"（Sprint 2 中 Critic 主动暴露 DSP 1.0× 裕量、纠正专利过度告警，均获肯定）。
- 关联：CTO 要求**算力/预算受控**——明确指示时（如"启动前不消耗额外算力"）须严格零自动推进。

### 7.4 当前节点（接续点）
- Sprint 3「快速验证法」有条件 GO，第一动作=拆机逆向 6 项未知量（WO-S3-001）。详见项目根 `sprint3_status.md`。

---

*Project Manager Agent Memory v1.0.0 — Learning from Every Task, Every Sprint, Every Project*


---

### 7.5 多 agent 运维教训（2026-06-06 增量）

> 完整清单：`sprint6/STAGE4_BRINGUP_CHECKLIST.md` E 节。

- **排队消息会被合并吞**：同一 agent 连发多单，回包可能只含最后一单——逐单核收 verdict，缺的立即追讨（R29/R30 实例）。
- **流超时恢复**：先查磁盘现场（git status + 产物 ls），按现场紧派单，不盲目重发原单。
- **机械落位 assert 守卫**：apply 脚本 assert 锚唯一性，失败即中止 commit（25e9253 教训延续执行）。
- **长调研任务勿强制结构化输出**：schema 强制对多步研究 agent 系统性失败；磁盘中转（写文件+一行确认）稳。
- **范围变更竞态**：CTO 改令可能晚于 agent 已动工——改令送达后查盘上已写产物，冻结不扩展不删，如实报 CTO（M1 draft 实例）。
