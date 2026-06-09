# Communication Protocol

## Message Format

All inter-agent messages follow a standardized YAML envelope format:

```yaml
message:
  header:
    message_id: "uuid-v4"
    timestamp: "ISO-8601"
    from: "agent-id"
    to: "agent-id | broadcast"
    message_type: "TASK_ASSIGN | STATUS_UPDATE | DELIVERABLE | REVIEW_REQUEST | REVIEW_RESULT | ESCALATION | HUMAN_REVIEW | TOOL_CALL | TOOL_RESULT"
    priority: "CRITICAL | HIGH | NORMAL | LOW"
    
  body:
    # Type-specific payload
    
  trace:
    project_id: "project-uuid"
    task_id: "task-uuid"
    chain: ["message-id-1", "message-id-2", ...]
    
  signature:
    integrity_hash: "sha256"
    version: "1.0"
```

## Message Types

### TASK_ASSIGN (Project Manager → Domain Agent)

```yaml
body:
  task:
    task_id: "task-uuid"
    title: "Task description"
    description: "Detailed requirements"
    deliverables: ["item1", "item2"]
    dependencies: ["task-uuid-1", "task-uuid-2"]
    deadline: "ISO-8601"
    acceptance_criteria: ["criterion1", "criterion2"]
    input_artifacts:
      - type: "file | data | reference"
        source: "artifact-uri"
        format: "step | mat | csv | pdf"
```

### DELIVERABLE (Domain Agent → Project Manager)

```yaml
body:
  deliverable:
    task_id: "task-uuid"
    status: "COMPLETED | PARTIAL | BLOCKED"
    artifacts:
      - type: "report | design | data | code | model"
        path: "artifact-uri"
        format: "md | pdf | step | m | py | csv"
        checksum: "sha256"
    self_assessment:
      completeness: "0-100"
      confidence: "0-100"
      known_issues: ["issue1", "issue2"]
    next_steps: ["recommendation1"]
```

### REVIEW_REQUEST (Project Manager → Critic)

```yaml
body:
  review:
    deliverable_id: "deliverable-uuid"
    scope: "FULL | DELTA"
    focus_areas: ["area1", "area2"]
    previous_reviews: ["review-id-1"]
    context:
      project_phase: "CONCEPT | DESIGN | PROTOTYPE | PRODUCTION"
      risk_level: "HIGH | MEDIUM | LOW"
      cross_domain_impact: true | false
```

### REVIEW_RESULT (Critic → Project Manager)

```yaml
body:
  review_result:
    deliverable_id: "deliverable-uuid"
    verdict: "PASSED | PASSED_WITH_MINOR | FAILED | ESCALATED"
    severity_counts:
      BLOCKER: 0
      MAJOR: 1
      MINOR: 3
      INFO: 2
    findings:
      - id: "F-001"
        severity: "BLOCKER | MAJOR | MINOR | INFO"
        category: "ASSUMPTION | ERROR | STANDARD | CROSS_DOMAIN | DOCUMENTATION"
        domain: "acoustic | dsp | hardware | structure | testing | document"
        description: "Finding description"
        evidence: "Supporting evidence"
        recommendation: "How to fix"
        related_findings: ["F-002"]
    cross_domain_checks:
      - domains: ["acoustic", "dsp"]
        interface_parameter: "sample_rate"
        declared_value: "48000"
        verified: true | false
    assumptions_challenged:
      - assumption: "Temperature will not exceed 40C"
        challenge: "What if operating in 50C ambient?"
        impact: "Thermal design margin may be insufficient"
    review_statistics:
      time_spent_minutes: 45
      code_lines_reviewed: 0
      pages_reviewed: 12
      previous_escapes: 0
```

### TOOL_CALL (Domain Agent → Tool Agent)

```yaml
body:
  tool_call:
    call_id: "call-uuid"
    tool: "code-execution | cad-interface | matlab | database | web-search"
    method: "execute | query | run | search"
    parameters:
      param1: "value1"
      param2: "value2"
    timeout_seconds: 300
    resource_limits:
      memory_mb: 2048
      cpu_cores: 2
```

### TOOL_RESULT (Tool Agent → Domain Agent)

```yaml
body:
  tool_result:
    call_id: "call-uuid"
    status: "SUCCESS | ERROR | TIMEOUT"
    output:
      format: "json | text | binary | image"
      data: "result-data"
      files: ["file-uri-1"]
    metrics:
      execution_time_ms: 1500
      memory_peak_mb: 512
      cpu_time_ms: 1200
    error:
      code: "E1001"
      message: "Error description"
      recoverable: true | false
```

### ESCALATION (Agent → Chief Engineer)

```yaml
body:
  escalation:
    level: "L1 | L2 | L3 | L4"
    category: "TECHNICAL | SCHEDULE | RESOURCE | RISK | QUALITY"
    summary: "One-line summary"
    details: "Detailed description"
    impact:
      schedule: "Impact on timeline"
      technical: "Technical impact"
      business: "Business impact"
    options:
      - description: "Option A"
        pros: ["pro1"]
        cons: ["con1"]
      - description: "Option B"
        pros: ["pro1"]
        cons: ["con1"]
    recommendation: "Recommended option with rationale"
    decision_deadline: "ISO-8601"
```

## Task State Machine

```
PENDING
  |
  | assign
  v
ASSIGNED ──(accept)──> IN_PROGRESS
  |                        |
  | decline                | submit
  |                        v
  |                   REVIEW ──(PASSED)──> COMPLETED
  |                      |                  |
  |                      | FAILED           | human_approve
  |                      v                  v
  |                   REJECTED          HUMAN_REVIEW
  |                      |                  |
  |                      | revise           | approved
  |                      v                  v
  +───────────────(restart)           APPROVED
                            
Special states:
  - ESCALATED: Any state → escalate to human
  - BLOCKED: IN_PROGRESS → blocked by dependency
  - PAUSED: Any state → pause (human decision)
```

## DAG Dependency Types

| Type | Symbol | Description |
|------|--------|-------------|
| Data Dependency | `D→` | Output of A is input to B |
| Resource Dependency | `R→` | A and B share limited resource |
| Spatial Dependency | `S→` | Physical layout dependency |
| Execution Dependency | `E→` | B must execute after A completes |
| Review Dependency | `V→` | B can start after A passes review |

## Review Flow

```
Domain Agent submits deliverable
         |
         v
Project Manager routes to Critic
         |
         v
Critic performs review (max 3 rounds)
         |
    +----+----+
    |         |
    v         v
 PASSED    FAILED
    |         |
    v         v
COMPLETED  RETURN
 (or HUMAN  (revise &
 REVIEW)    resubmit)
```

Every deliverable MUST pass Critic review before human review (except L4 escalations).

## Quality Gates

| Gate | Phase | Approver | Check Items |
|------|-------|----------|-------------|
| G0 | Kickoff | PM + Critic | PRD completeness, team readiness |
| G1 | Plan | Chief Engineer | WBS, schedule, resource plan |
| G2 | Architecture | Chief Engineer | System architecture, interfaces |
| G3 | Prototype | Chief Engineer + Critic | Design review, risk assessment |
| G4 | Final | Chief Engineer | Full validation, documentation |
