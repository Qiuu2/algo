---
name: "DatabaseAgent"
description: "数据库Agent的Schema定义、CRUD接口、查询规范与协作数据交换格式"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# Database Agent — Skill

## 1. 数据库Schema

### 核心表结构

#### 项目表 (projects)

```sql
CREATE TABLE projects (
    id              VARCHAR(16) PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    status          VARCHAR(20) DEFAULT 'draft' 
                    CHECK (status IN ('draft', 'active', 'paused', 'completed', 'archived')),
    priority        VARCHAR(10) DEFAULT 'medium'
                    CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    created_by      VARCHAR(64) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    target_date     DATE,
    completion_rate DECIMAL(5,2) DEFAULT 0.00,
    metadata        JSONB DEFAULT '{}'
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
```

#### 任务表 (tasks)

```sql
CREATE TABLE tasks (
    id              VARCHAR(16) PRIMARY KEY,
    project_id      VARCHAR(16) REFERENCES projects(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    status          VARCHAR(20) DEFAULT 'pending'
                    CHECK (status IN ('pending', 'in_progress', 'review', 'completed', 'blocked')),
    assignee_type   VARCHAR(20) CHECK (assignee_type IN ('human', 'agent')),
    assignee_id     VARCHAR(64),
    parent_task_id  VARCHAR(16) REFERENCES tasks(id),
    priority        VARCHAR(10) DEFAULT 'medium',
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    due_date        DATE,
    estimated_hours DECIMAL(6,2),
    actual_hours    DECIMAL(6,2),
    output_refs     JSONB DEFAULT '[]',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_type, assignee_id);
```

#### Agent表 (agents)

```sql
CREATE TABLE agents (
    id              VARCHAR(32) PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    agent_type      VARCHAR(50) NOT NULL,
    layer           VARCHAR(20) CHECK (layer IN ('orchestration', 'domain', 'tool')),
    status          VARCHAR(20) DEFAULT 'active'
                    CHECK (status IN ('active', 'inactive', 'error', 'maintenance')),
    capabilities    JSONB DEFAULT '[]',
    current_task_id VARCHAR(16) REFERENCES tasks(id),
    last_heartbeat  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    metadata        JSONB DEFAULT '{}'
);

CREATE INDEX idx_agents_layer ON agents(layer);
CREATE INDEX idx_agents_status ON agents(status);
```

#### 产出表 (deliverables)

```sql
CREATE TABLE deliverables (
    id              VARCHAR(16) PRIMARY KEY,
    task_id         VARCHAR(16) REFERENCES tasks(id) ON DELETE CASCADE,
    project_id      VARCHAR(16) REFERENCES projects(id) ON DELETE CASCADE,
    agent_id        VARCHAR(32) REFERENCES agents(id),
    type            VARCHAR(50) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    file_path       VARCHAR(512),
    file_size       BIGINT,
    file_hash       VARCHAR(64),
    content_summary TEXT,
    status          VARCHAR(20) DEFAULT 'draft'
                    CHECK (status IN ('draft', 'review', 'approved', 'rejected', 'superseded')),
    version         VARCHAR(10) DEFAULT 'v1.0',
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_deliverables_task ON deliverables(task_id);
CREATE INDEX idx_deliverables_project ON deliverables(project_id);
CREATE INDEX idx_deliverables_type ON deliverables(type);
```

#### 评审记录表 (reviews)

```sql
CREATE TABLE reviews (
    id              VARCHAR(16) PRIMARY KEY,
    deliverable_id  VARCHAR(16) REFERENCES deliverables(id) ON DELETE CASCADE,
    reviewer_type   VARCHAR(20) CHECK (reviewer_type IN ('human', 'agent')),
    reviewer_id     VARCHAR(64) NOT NULL,
    verdict         VARCHAR(20) CHECK (verdict IN ('approved', 'approved_with_comments', 'rejected', 'needs_revision')),
    comments        TEXT,
    criteria_scores JSONB DEFAULT '{}',
    reviewed_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reviews_deliverable ON reviews(deliverable_id);
```

### Schema关系图

```
projects (1)
  ├── tasks (N)
  │     ├── deliverables (N)
  │     └── sub_tasks (self-reference)
  └── deliverables (N)

agents (1)
  ├── tasks (N) [current_task]
  └── deliverables (N) [creator]

deliverables (1)
  └── reviews (N)
```

## 2. CRUD接口规范（RESTful风格JSON-RPC）

### 创建: `db.create`

```json
{
  "jsonrpc": "2.0",
  "method": "db.create",
  "params": {
    "table": "projects",
    "data": {
      "id": "P002",
      "name": "Speaker B200",
      "description": " bookshelf speaker design",
      "status": "active",
      "priority": "high",
      "created_by": "pm-agent-001",
      "target_date": "2024-03-15"
    }
  },
  "id": "db-req-001"
}
```

### 查询: `db.query`

```json
{
  "jsonrpc": "2.0",
  "method": "db.query",
  "params": {
    "table": "tasks",
    "operation": "select",
    "filters": {
      "project_id": "P001",
      "status": {"in": ["in_progress", "pending"]},
      "priority": {"gte": "medium"}
    },
    "fields": ["id", "title", "status", "assignee_id", "due_date"],
    "join": [
      {
        "table": "agents",
        "on": "tasks.assignee_id = agents.id",
        "fields": ["name as assignee_name"]
      }
    ],
    "sort": [{"field": "due_date", "direction": "asc"}],
    "limit": 50,
    "offset": 0
  },
  "id": "db-req-002"
}
```

### 更新: `db.update`

```json
{
  "jsonrpc": "2.0",
  "method": "db.update",
  "params": {
    "table": "tasks",
    "filters": {
      "id": "T001"
    },
    "data": {
      "status": "in_progress",
      "started_at": "2024-01-15T10:00:00Z"
    }
  },
  "id": "db-req-003"
}
```

### 删除: `db.delete`

```json
{
  "jsonrpc": "2.0",
  "method": "db.delete",
  "params": {
    "table": "tasks",
    "filters": {
      "id": "T099",
      "status": "pending"
    },
    "soft_delete": true
  },
  "id": "db-req-004"
}
```

## 3. 查询接口

### 按项目查询

```json
{
  "jsonrpc": "2.0",
  "method": "db.query.project_summary",
  "params": {
    "project_id": "P001",
    "include": ["tasks", "agents", "deliverables", "progress"]
  }
}
```

### 按Agent查询

```json
{
  "jsonrpc": "2.0",
  "method": "db.query.agent_activity",
  "params": {
    "agent_id": "acoustic-agent-001",
    "time_range": {
      "from": "2024-01-01T00:00:00Z",
      "to": "2024-01-15T23:59:59Z"
    },
    "include_tasks": true,
    "include_deliverables": true
  }
}
```

### 按状态查询

```json
{
  "jsonrpc": "2.0",
  "method": "db.query.by_status",
  "params": {
    "entity": "tasks",
    "status": "blocked",
    "include_blocking_reason": true
  }
}
```

### 按时间范围查询

```json
{
  "jsonrpc": "2.0",
  "method": "db.query.timeline",
  "params": {
    "project_id": "P001",
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-15T23:59:59Z",
    "granularity": "daily",
    "events": ["task_created", "task_completed", "deliverable_submitted", "review_done"]
  }
}
```

## 4. 知识库表结构

### 知识条目表 (knowledge_entries)

```sql
CREATE TABLE knowledge_entries (
    id              VARCHAR(16) PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    content         TEXT NOT NULL,
    content_type    VARCHAR(20) DEFAULT 'markdown'
                    CHECK (content_type IN ('markdown', 'code', 'json', 'table', 'image')),
    category        VARCHAR(50) NOT NULL,
    tags            VARCHAR(50)[] DEFAULT '{}',
    source_agent    VARCHAR(32),
    source_project  VARCHAR(16),
    related_entries VARCHAR(16)[],
    confidence      DECIMAL(3,2) DEFAULT 1.00,
    usage_count     INTEGER DEFAULT 0,
    last_accessed   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_knowledge_category ON knowledge_entries(category);
CREATE INDEX idx_knowledge_tags ON knowledge_entries USING GIN(tags);
CREATE INDEX idx_knowledge_source ON knowledge_entries(source_agent);
```

### 全文检索配置

```sql
-- Create text search vector
ALTER TABLE knowledge_entries ADD COLUMN search_vector tsvector;

-- Update trigger for search vector
CREATE TRIGGER knowledge_search_update
    BEFORE INSERT OR UPDATE ON knowledge_entries
    FOR EACH ROW EXECUTE FUNCTION
    tsvector_update_trigger(search_vector, 'pg_catalog.english', title, content);

-- GIN index for fast full-text search
CREATE INDEX idx_knowledge_search ON knowledge_entries USING GIN(search_vector);
```

### 知识库查询接口

```json
{
  "jsonrpc": "2.0",
  "method": "db.knowledge.search",
  "params": {
    "query": "bass reflex enclosure design port",
    "categories": ["acoustic_design", "enclosure_design"],
    "tags": ["speaker", "bass_reflex"],
    "limit": 10,
    "min_confidence": 0.8
  }
}
```

## 5. 审计日志记录

### 审计日志表 (audit_log)

```sql
CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    timestamp       TIMESTAMPTZ DEFAULT NOW(),
    actor_type      VARCHAR(20) CHECK (actor_type IN ('human', 'agent', 'system')),
    actor_id        VARCHAR(64) NOT NULL,
    action          VARCHAR(50) NOT NULL,
    target_table    VARCHAR(50),
    target_id       VARCHAR(16),
    old_values      JSONB,
    new_values      JSONB,
    result          VARCHAR(20) CHECK (result IN ('success', 'failure', 'denied')),
    error_message   TEXT,
    ip_address      INET,
    session_id      VARCHAR(64),
    request_id      VARCHAR(32)
);

CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_actor ON audit_log(actor_type, actor_id);
CREATE INDEX idx_audit_target ON audit_log(target_table, target_id);
```

### 审计日志格式

```json
{
  "timestamp": "2024-01-15T09:30:00Z",
  "actor_type": "agent",
  "actor_id": "structural-agent-001",
  "action": "UPDATE",
  "target_table": "deliverables",
  "target_id": "D005",
  "old_values": {"status": "draft", "version": "v1.0"},
  "new_values": {"status": "review", "version": "v1.1"},
  "result": "success",
  "request_id": "req-uuid-009"
}
```

## 6. 备份策略

### 备份计划

| 备份类型 | 频率 | 保留期 | 存储位置 |
|----------|------|--------|----------|
| 全量备份 | 每周日 02:00 | 4周 | S3冷存储 |
| 增量备份 | 每日 02:00 | 30天 | S3标准存储 |
| WAL归档 | 实时 | 7天 | S3标准存储 |
| 逻辑导出 | 每日 04:00 | 90天 | S3标准存储 |

### 恢复接口

```json
{
  "jsonrpc": "2.0",
  "method": "db.backup.restore",
  "params": {
    "backup_type": "incremental",
    "backup_date": "2024-01-14",
    "target_database": "itc_production",
    "verify_after_restore": true
  }
}
```

## 7. 与各Agent的数据交换格式

### 标准化JSON数据包

```json
{
  "packet_version": "1.0",
  "timestamp": "2024-01-15T09:30:00Z",
  "sender": {
    "agent_id": "acoustic-agent-001",
    "agent_type": "domain"
  },
  "data": {
    "entity_type": "deliverable",
    "entity_id": "D005",
    "operation": "create",
    "payload": {
      "name": "Acoustic Simulation Report",
      "type": "simulation_report",
      "file_path": "/deliverables/D005/report.pdf",
      "content_summary": "Frequency response simulation results...",
      "metadata": {
        "simulation_type": "COMSOL",
        "mesh_elements": 125000,
        "frequency_range_hz": [20, 20000]
      }
    }
  },
  "audit_context": {
    "request_id": "req-uuid-010",
    "session_id": "sess-abc123"
  }
}
```

## 8. 错误码体系

| 错误码 | 类别 | 说明 |
|--------|------|------|
| `D1001` | 权限错误 | 无权访问表/行 |
| `D1002` | 数据错误 | 字段值无效 |
| `D1003` | 安全错误 | SQL注入检测 |
| `D1004` | 验证错误 | 违反唯一约束 |
| `D2001` | 事务错误 | 约束违反 |
| `D2002` | 并发错误 | 死锁检测 |
| `D2003` | 连接错误 | 连接超时/池满 |
| `D3001` | 一致性错误 | 影响行数不符 |
| `D3002` | 关联错误 | 外键冲突 |
| `D4001` | 查询错误 | 语法/字段不存在 |
| `D4002` | 性能错误 | 查询超时 |
| `D9001` | 系统错误 | 数据库不可用 |
| `D9002` | 备份错误 | 备份/恢复失败 |
