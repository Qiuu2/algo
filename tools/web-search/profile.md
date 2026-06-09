---
name: "WebSearchAgent"
description: "网络信息检索与数据可视化Agent，提供Web搜索、文献检索、数据抓取与图表生成能力"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# Web Search / Visualization Agent — Profile

## 身份定义

- **Agent ID**: `web-search-agent`
- **类型**: 工具层Agent
- **身份**: 网络信息检索与数据可视化Agent
- **所属系统**: ITC企业级多Agent协作系统

## 功能范围

| 功能域 | 说明 | 优先级 |
|--------|------|--------|
| Web搜索 | 多源Web信息检索与聚合 | P0 |
| 学术搜索 | 论文/期刊/会议文献检索 | P0 |
| 专利搜索 | 全球专利数据库检索 | P1 |
| 数据抓取 | 结构化信息提取与清洗 | P1 |
| 结果聚合 | 多源结果去重、排序、摘要 | P0 |
| 信息提取 | 关键信息实体识别与抽取 | P1 |
| 可视化呈现 | 图表生成、专利地图、趋势图 | P0 |

## 调用接口

### 入口方法 (JSON-RPC)

```json
{
  "jsonrpc": "2.0",
  "method": "search.web",
  "params": {
    "query": "bass reflex speaker enclosure design principles",
    "sources": ["web", "scholar"],
    "max_results": 20,
    "language": "en",
    "recency_days": 365
  },
  "id": 1
}
```

### 返回值格式

```json
{
  "jsonrpc": "2.0",
  "result": {
    "search_id": "ws-20240115-001",
    "total_found": 156,
    "returned": 20,
    "results": [
      {
        "rank": 1,
        "title": "Optimal Design of Bass-Reflex Speaker Systems",
        "source": "scholar",
        "authors": ["J. Smith", "A. Johnson"],
        "published": "2023-06-15",
        "url": "https://example.com/paper1",
        "snippet": "This paper presents a systematic approach to optimizing bass-reflex speaker enclosures...",
        "relevance_score": 0.95
      }
    ],
    "aggregated_summary": "Top research themes: enclosure volume optimization (35%), port tuning (28%), nonlinear effects (22%)...",
    "execution_time_ms": 2340
  },
  "id": 1
}
```

## 支持数据源

| 数据源 | 类型 | 覆盖范围 | API状态 |
|--------|------|----------|---------|
| Google Search | Web | 全球网页 | Connected |
| Google Scholar | 学术 | 学术论文 | Connected |
| USPTO | 专利 | 美国专利 | Connected |
| EPO Espacenet | 专利 | 欧洲专利 | Connected |
| IEEE Xplore | 学术 | IEEE论文 | Connected |
| arXiv | 学术 | 预印本 | Connected |
| Semantic Scholar | 学术 | 综合学术 | Connected |

## 依赖服务

| 服务 | 用途 | 健康检查 |
|------|------|----------|
| Search API Gateway | 搜索请求聚合 | `/health/search` |
| Scraping Engine | 网页抓取与解析 | `/health/scraper` |
| Visualization Engine | 图表渲染 | `/health/viz` |
| Cache Service | 结果缓存 | `/health/cache` |
