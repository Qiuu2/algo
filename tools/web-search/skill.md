---
name: "WebSearchAgent"
description: "网络检索Agent的搜索接口、数据抓取规范、可视化能力与协作接口"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# Web Search / Visualization Agent — Skill

## 1. 搜索接口（JSON-RPC）

### Web搜索: `search.web`

```json
{
  "jsonrpc": "2.0",
  "method": "search.web",
  "params": {
    "query": "bass reflex enclosure port tuning formula",
    "max_results": 20,
    "language": "en",
    "recency_days": 365,
    "safe_search": true,
    "result_fields": ["title", "url", "snippet", "published", "source_domain"]
  },
  "id": "ws-req-001"
}
```

### 学术搜索: `search.scholar`

```json
{
  "jsonrpc": "2.0",
  "method": "search.scholar",
  "params": {
    "query": "loudspeaker nonlinear distortion compensation",
    "authors": [],
    "year_from": 2020,
    "year_to": 2024,
    "venues": ["IEEE", "JASA", "AES"],
    "max_results": 15,
    "sort_by": "relevance"
  },
  "id": "ws-req-002"
}
```

### 专利搜索: `search.patent`

```json
{
  "jsonrpc": "2.0",
  "method": "search.patent",
  "params": {
    "query": "bass reflex speaker",
    "patent_offices": ["USPTO", "EPO", "CNIPA"],
    "date_from": "2020-01-01",
    "date_to": "2024-01-15",
    "status": "granted",
    "max_results": 15
  },
  "id": "ws-req-003"
}
```

### 综合检索: `search.combined`

```json
{
  "jsonrpc": "2.0",
  "method": "search.combined",
  "params": {
    "query": "active noise cancellation headphone design",
    "sources": ["web", "scholar", "patent"],
    "max_results_per_source": 10,
    "cross_verify": true,
    "generate_visualization": true
  },
  "id": "ws-req-004"
}
```

## 2. 数据抓取规范

### 抓取规则

```yaml
scraping_rules:
  robots_txt_compliance: strict
  crawl_rate_limit:
    default: 1 request per 2 seconds
    academic_sources: 1 request per 5 seconds
    government_sources: 1 request per 3 seconds
  
  max_page_size: 5MB
  timeout: 15 seconds
  retry_policy:
    max_retries: 3
    backoff: [2s, 5s, 10s]
  
  forbidden_patterns:
    - login pages
    - payment walls
    - personal data
    - copyright protected content
  
  extraction_priority:
    - title
    - authors
    - publication_date
    - abstract/summary
    - key_metrics
    - citations
```

### 数据清洗流水线

```
Raw HTML → Text Extraction → Entity Recognition → 
  → Deduplication → Normalization → Structured JSON
```

### 抓取接口: `scrape.extract`

```json
{
  "jsonrpc": "2.0",
  "method": "scrape.extract",
  "params": {
    "url": "https://example.com/technical-paper",
    "extract_fields": {
      "title": "h1.article-title",
      "authors": [".author-name"],
      "abstract": "div.abstract p",
      "published": "meta[name='date-published']@content",
      "keywords": [".keyword-tag"]
    },
    "timeout": 15
  }
}
```

## 3. 可视化能力

### 支持的图表类型

| 图表类型 | 库 | 用途 | 输出格式 |
|----------|-----|------|----------|
| 趋势折线图 | Plotly | 时间序列趋势 | PNG/HTML |
| 柱状图 | Plotly | 分类对比 | PNG/HTML |
| 散点图 | Plotly | 相关性分析 | PNG/HTML |
| 热力图 | Plotly | 矩阵数据 | PNG/HTML |
| 专利地图 | Matplotlib | 专利布局分析 | PNG |
| 技术趋势图 | Plotly | 技术演进时间线 | PNG/HTML |
| 词云图 | Matplotlib | 关键词频率 | PNG |
| 网络关系图 | Plotly | 引用/合作关系 | HTML |

### 可视化接口: `viz.chart`

```json
{
  "jsonrpc": "2.0",
  "method": "viz.chart",
  "params": {
    "chart_type": "trend_line",
    "data": [
      {"year": 2020, "patents": 45, "papers": 120},
      {"year": 2021, "patents": 52, "papers": 145},
      {"year": 2022, "patents": 68, "papers": 180},
      {"year": 2023, "patents": 85, "papers": 210}
    ],
    "x_axis": "year",
    "y_axes": ["patents", "papers"],
    "options": {
      "title": "ANC Technology Trends (2020-2023)",
      "x_label": "Year",
      "y_label": "Count",
      "width": 1000,
      "height": 500,
      "format": "png",
      "dpi": 300
    }
  }
}
```

### 专利地图接口: `viz.patent_map`

```json
{
  "jsonrpc": "2.0",
  "method": "viz.patent_map",
  "params": {
    "patent_data": "/input/patent_search_results.json",
    "map_type": "technology_landscape",
    "options": {
      "color_by": "assignee",
      "size_by": "citation_count",
      "clustering": true,
      "title": "ANC Patent Technology Landscape"
    }
  }
}
```

## 4. 与文献/专利监控Agent的协作

### 自动化检索任务接口

```json
{
  "interface": "search-to-monitor",
  "scenario": "literature_monitoring",
  "task_definition": {
    "task_name": "weekly_anc_paper_monitor",
    "schedule": "0 9 * * 1",
    "queries": [
      {
        "query": "active noise cancellation headphone",
        "sources": ["scholar"],
        "filters": {"year_from": 2023}
      },
      {
        "query": "adaptive feedback ANC",
        "sources": ["scholar", "patent"],
        "filters": {"year_from": 2023}
      }
    ],
    "alert_conditions": {
      "min_results": 1,
      "citation_threshold": 10,
      "key_authors": ["Author A", "Author B"]
    },
    "output": {
      "format": "markdown_report",
      "destination": "/shared/monitoring/weekly_anc.md",
      "include_visualization": true
    }
  }
}
```

## 5. 与项目文档Agent的协作

### 图表嵌入报告接口

```json
{
  "interface": "viz-to-document",
  "scenario": "report_chart_embedding",
  "data_flow": {
    "input": {
      "chart_spec": "/shared/chart_spec.json",
      "report_context": {
        "section": "Technology Landscape",
        "figure_number": 3,
        "caption_template": "Figure {n}: {title} (Source: {sources})"
      }
    },
    "processing": [
      "generate_chart_png",
      "generate_chart_svg",
      "create_markdown_reference",
      "embed_in_report"
    ],
    "output": {
      "png_file": "/shared/reports/fig3_tech_landscape.png",
      "svg_file": "/shared/reports/fig3_tech_landscape.svg",
      "markdown_ref": "![Figure 3](fig3_tech_landscape.png)",
      "embedded_report": "/shared/reports/section3.md"
    }
  }
}
```

## 6. 缓存策略

### 多级缓存架构

```
L1: In-Memory (Redis) — 热点查询，TTL 1小时
L2: Local Disk — 近期查询，TTL 24小时
L3: Object Storage — 历史归档，永久保留
```

### 缓存规则

| 查询类型 | 缓存TTL | 缓存层级 | 刷新策略 |
|----------|---------|----------|----------|
| Web搜索 | 2小时 | L1, L2 | 异步刷新 |
| 学术搜索 | 24小时 | L1, L2 | 手动刷新 |
| 专利搜索 | 72小时 | L2, L3 | 定时刷新 |
| 数据抓取 | 12小时 | L2 | 条件刷新 |
| 可视化图表 | 1小时 | L1 | 即时生成 |

### 缓存控制接口

```json
{
  "jsonrpc": "2.0",
  "method": "cache.control",
  "params": {
    "action": "invalidate",
    "patterns": ["search:bass_reflex:*", "viz:*"]
  }
}
```

## 7. 输出格式

### Markdown报告

```markdown
# Search Report: Bass Reflex Speaker Design

**Query**: bass reflex speaker enclosure design
**Date**: 2024-01-15
**Sources**: Web(15) + Scholar(8) + Patent(5)

## Key Findings

### 1. Enclosure Volume Optimization
**Sources**: [^1] Smith et al. (2023), [^2] AES Convention Paper

The optimal enclosure volume depends on the driver parameters:
- Vas: equivalent air volume
- Qts: total Q factor
- Fs: resonant frequency

**Formula**: Vb = Vas / ((Qtc/Qts)^2 - 1)

### 2. Port Design Guidelines
...

## Technology Trends
![Trend Chart](trend_chart.png)

## Patent Landscape
![Patent Map](patent_map.png)

## References
[^1]: Smith, J. et al. "Optimal Design..." JAES 2023
[^2]: Johnson, A. "Bass Reflex Tuning" AES Convention 2022
```

### HTML页面

```json
{
  "jsonrpc": "2.0",
  "method": "output.html",
  "params": {
    "template": "interactive_dashboard",
    "title": "ANC Technology Research Dashboard",
    "sections": ["summary", "trends", "patents", "papers", "key_players"],
    "interactive": true,
    "output_path": "/output/dashboard.html"
  }
}
```

### PNG图表

```json
{
  "jsonrpc": "2.0",
  "method": "output.chart_png",
  "params": {
    "chart_type": "bar_chart",
    "data": [...],
    "width": 1200,
    "height": 600,
    "dpi": 300,
    "output_path": "/output/chart.png"
  }
}
```

## 8. 错误码体系

| 错误码 | 类别 | 说明 |
|--------|------|------|
| `W1001` | 搜索错误 | 数据源不可用 |
| `W1002` | 搜索错误 | API限流/拒绝 |
| `W1003` | 搜索错误 | 查询无结果 |
| `W2001` | 验证错误 | 来源可信度不足 |
| `W2002` | 验证错误 | 多源数据冲突 |
| `W3001` | 可视化错误 | 图表渲染失败 |
| `W3002` | 可视化错误 | 数据格式不支持 |
| `W4001` | 缓存错误 | 缓存失效 |
| `W4002` | 抓取错误 | 目标反爬/拒绝 |
| `W4003` | 抓取错误 | robots.txt禁止 |
| `W5001` | 网络错误 | 连接超时 |
| `W9001` | 系统错误 | 内部服务错误 |
