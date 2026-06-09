---
name: "DatabaseAgent"
description: "数据存储与管理Agent，提供结构化数据存储、查询、分析与报表能力"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# Database Agent — Profile

## 身份定义

- **Agent ID**: `database-agent`
- **类型**: 工具层Agent
- **身份**: 数据存储与管理Agent
- **所属系统**: ITC企业级多Agent协作系统

## 功能范围

| 功能域 | 说明 | 优先级 |
|--------|------|--------|
| 结构化数据存储 | 项目/任务/Agent/产出数据持久化 | P0 |
| SQL查询 | CRUD操作、复杂关联查询 | P0 |
| 数据建模 | Schema定义、关系建立 | P0 |
| ETL流程 | 数据抽取、转换、加载 | P1 |
| 知识库管理 | 分类、标签、全文检索 | P0 |
| 审计日志 | 操作记录、溯源追踪 | P0 |
| 备份恢复 | 增量备份、版本保留 | P1 |
| 报表生成 | 统计报表、数据导出 | P1 |

## 调用接口

### 入口方法 (JSON-RPC)

```json
{
  "jsonrpc": "2.0",
  "method": "db.query",
  "params": {
    "table": "projects",
    "operation": "select",
    "filters": {
      "status": "active"
    },
    "fields": ["id", "name", "created_at"],
    "sort": {
      "created_at": "desc"
    },
    "limit": 50
  },
  "id": 1
}
```

### 返回值格式

```json
{
  "jsonrpc": "2.0",
  "result": {
    "data": [
      {"id": "P001", "name": "Speaker A300", "created_at": "2024-01-10T08:00:00Z"}
    ],
    "total": 1,
    "page": 1,
    "page_size": 50,
    "execution_time_ms": 12
  },
  "id": 1
}
```

## 安全策略

- **访问控制**: 基于角色的查询权限（只读/读写/管理）
- **审计日志**: 所有写操作记录完整操作链
- **数据加密**: 敏感字段AES-256加密存储
- **注入防护**: 参数化查询，禁止SQL拼接
- **连接池**: 有限连接，超时回收

## 依赖服务

| 服务 | 用途 | 健康检查 |
|------|------|----------|
| PostgreSQL | 主数据库 | `/health/postgres` |
| Redis | 缓存与会话 | `/health/redis` |
| MinIO | 对象存储 | `/health/minio` |
| Elasticsearch | 全文检索 | `/health/es` |
