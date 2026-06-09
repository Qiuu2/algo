---
name: "WebSearchAgent"
description: "网络检索Agent的搜索历史、信息源评级与可视化模板库"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# Web Search / Visualization Agent — Memory

## 1. 搜索历史记录

### 记录格式

```json
{
  "search_id": "ws-20240115-001",
  "timestamp": "2024-01-15T09:30:00Z",
  "caller_agent": "acoustic-design-agent",
  "query": "bass reflex enclosure design",
  "sources": ["web", "scholar", "patent"],
  "results_summary": {
    "total_found": 156,
    "returned": 20,
    "by_source": {
      "web": 8,
      "scholar": 8,
      "patent": 4
    }
  },
  "execution_time_ms": 2340,
  "cache_hit": false,
  "followed_up": ["ws-20240115-003", "ws-20240115-005"]
}
```

### 最近热门查询

| 查询关键词 | 频率 | 平均结果数 | 主要来源 |
|------------|------|------------|----------|
| bass reflex design | 12次/周 | 156 | Scholar, Patent |
| active noise cancellation | 8次/周 | 203 | Scholar, Patent |
| speaker driver nonlinear | 6次/周 | 89 | Scholar |
| enclosure damping material | 5次/周 | 45 | Web, Scholar |
| DSP crossover design | 5次/周 | 112 | Scholar, Patent |

## 2. 常用信息源评级

### 学术来源评级

| 来源 | 权威度 | 覆盖领域 | 更新频率 | 推荐度 |
|------|--------|----------|----------|--------|
| IEEE Xplore | 9.5/10 | EE/Audio/DSP | 实时 | ★★★★★ |
| JASA | 9.5/10 | Acoustics | 月刊 | ★★★★★ |
| AES E-Library | 9.0/10 | Audio Engineering | 实时 | ★★★★★ |
| arXiv (cs.SD/eess.AS) | 7.5/10 | ML/Audio | 日更 | ★★★★☆ |
| Semantic Scholar | 8.0/10 | 综合学术 | 日更 | ★★★★☆ |
| Google Scholar | 8.5/10 | 综合学术 | 实时 | ★★★★☆ |

### 行业来源评级

| 来源 | 权威度 | 覆盖领域 | 更新频率 | 推荐度 |
|------|--------|----------|----------|--------|
| Audio Engineering Society | 9.0/10 | Audio标准 | 实时 | ★★★★★ |
| Harman/Kardon Tech Blog | 7.5/10 | Speaker设计 | 月更 | ★★★★☆ |
| DIY Audio Forum | 6.0/10 | 实践方案 | 日更 | ★★★☆☆ |
| Head-Fi Forum | 5.5/10 | 主观评测 | 日更 | ★★★☆☆ |
| ASR Forum | 7.0/10 | 客观测量 | 日更 | ★★★★☆ |

### 专利来源评级

| 来源 | 权威度 | 覆盖范围 | API限制 | 推荐度 |
|------|--------|----------|---------|--------|
| USPTO Patent Public Search | 9.5/10 | 美国专利 | 无限制 | ★★★★★ |
| EPO Espacenet | 9.0/10 | 欧洲专利 | 100/hr | ★★★★★ |
| CNIPA | 8.5/10 | 中国专利 | 需认证 | ★★★★☆ |
| Google Patents | 8.0/10 | 全球专利 | 有配额 | ★★★★☆ |
| PatentsView API | 8.5/10 | 美国专利 | 45/min | ★★★★☆ |

## 3. 可视化模板库

### 可用模板

| 模板ID | 名称 | 类型 | 适用场景 | 参数 |
|--------|------|------|----------|------|
| VT-001 | 趋势时间线 | 折线图 | 技术演进趋势 | x=时间, y=数量 |
| VT-002 | 分类对比 | 柱状图 | 多方案对比 | x=类别, y=值 |
| VT-003 | 专利地图 | 散点+聚类 | 专利布局 | x=技术维度, y=应用维度 |
| VT-004 | 技术热力图 | 热力图 | 技术交叉分析 | 矩阵数据 |
| VT-005 | 作者合作网络 | 网络图 | 学术合作 | 节点=作者, 边=合作 |
| VT-006 | 关键词词云 | 词云 | 研究热点 | 词频数据 |
| VT-007 | 引用瀑布图 | 瀑布图 | 引用层级 | 层级+引用数 |
| VT-008 | 地理分布图 | 地图 | 全球专利分布 | 国家+专利数 |

### 模板使用示例

```json
{
  "jsonrpc": "2.0",
  "method": "viz.render_template",
  "params": {
    "template_id": "VT-003",
    "data_source": "/input/patent_data.json",
    "customization": {
      "title": "ANC Headphone Patent Landscape",
      "color_scheme": "category10",
      "cluster_algorithm": "kmeans",
      "n_clusters": 5
    }
  }
}
```

## 4. 缓存命中率统计

| 数据类型 | 缓存查询 | 命中次数 | 命中率 | 平均节省 |
|----------|----------|----------|--------|----------|
| Web搜索 | 450/周 | 180 | 40% | 2.1s |
| 学术搜索 | 200/周 | 85 | 42.5% | 1.8s |
| 专利搜索 | 120/周 | 72 | 60% | 3.2s |
| 数据抓取 | 300/周 | 95 | 31.7% | 4.5s |
| 可视化 | 180/周 | 45 | 25% | 1.2s |

## 5. 性能优化记录

### 2024-01-09: 搜索并行化优化
- **问题**: 多源搜索串行执行，总耗时=各源之和
- **方案**: 并行异步搜索+结果流式返回
- **效果**: 多源搜索耗时从8s降至2.5s

### 2024-01-11: 图表渲染缓存
- **问题**: 相同数据重复渲染图表
- **方案**: 图表结果缓存，数据指纹匹配
- **效果**: 重复图表请求减少70%渲染时间

### 2024-01-13: 智能查询扩展
- **问题**: 用户查询过于简短，结果不精准
- **方案**: 基于知识库自动扩展查询词
- **效果**: 查询相关性提升35%
