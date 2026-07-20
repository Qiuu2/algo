---
name: Project Document & Knowledge Management Agent Skills
description: |
  ITC 项目的技术文档与知识管理【执笔】Agent：撰写 decisions_log、交付物与报告，
  并强制执行 POLICY-PROV-001 溯源纪律（L0–L4 分级 / DEC 条目格式 / 铁律五撤回全库传播 / C1·C7·C8 门）。
  通用文档技能（模板/多格式/术语）服务于该纪律，而非替代它。
version: 1.0.0
author: ITC Enterprise Agent System
---

# Skill: 技术文档与知识管理专家 Agent

## 技能总览

```yaml
技能域:
  - 报告生成流程
  - 文档模板库
  - 知识库维护规范
  - 版本管理策略
  - 文档质量检查
  - 跨域协作接口

技能标准: Kimi/Hermes Agent Skill Specification v1.0
```

---

## 技能0: 溯源纪律绑定 `SKILL-DOC-000`（本项目治理，最高优先，一切文档/日志写作的前置）

> **本 agent 是 `sprint2/docs/decisions_log.md` 与所有交付物的执笔者——因此它必须先懂 `POLICY-PROV-001`。**
> 项目化焊接（roadmap#5 样板，DEC-S6-GOVERNANCE-SLIM-05）：原 skill 通篇是通用技术写作，**零处提 L 分级/C 门/铁律/decisions_log**——写 log 的 agent 对 log 的规则失明。此技能把它绑回本项目治理。

### 0.1 每个进文档/日志/规格/承诺的数字必须挂 L 级（C1，BLOCKER）
- `[L1 实测]`（板上/EZKIT/仪器/measured）｜`[L2 仿真/工具]`（numpy/MATLAB/COMSOL/host）｜`[L3 解析]`（闭式/手算）｜`[L4 占位]`（placeholder/未实测收益）｜`[L0 目测]`（拍脑袋，严禁 LOCKED 决策）。
- **绝不把 L2/L3/L4 措辞成"实测/measured/已验证"**（C2，BLOCKER，红线词只限真 L1）。无 L 标的数字**不得进 decisions_log**。（注：C2 的"确认/已验证"只在**修饰数字可信度**时触发，不误伤"CTO 确认决策"这类正当用法。）

### 0.2 decisions_log 条目格式（POLICY §5 的**六个强制字段**，一个不能少）
每条：`*YYYY-MM-DD **DEC-{S#}-{TOPIC}-{seq}**（一句话摘要）：<决策> ｜①依据数字 + ②来源等级 + ③数据出处 <如 94.0dB [L2/待消声室 L1]> ｜④可逆性 <可逆/不可逆> ｜⑤验证状态 <已验证L1 / 待L1回填 / 未验证> ｜⑥风险声明 <当证据强度低于可逆性要求时必须明示，如"桌面口径未含 cache/中断"> ｜reviewer: critic @ <exact model ID> / <date>。*`
- **①–⑥ 是 POLICY §5 强制字段;`reviewer:` 属 §4B/commit 纪律(非 §5 字段),但同样必带。** 漏 ⑤⑥ = PF-1 类病根(不可逆 L2 决策没写风险)。
- 不可逆决策须 L1（或 L2+CTO 签字）；强约束 L2 起（L3 须挂「待 L1/L2 验证」）。
- **无 `reviewer:` 独立 critic 标记的承重结论不得落库**（commit 纪律）。

### 0.3 撤回传播（铁律五 / C7，BLOCKER）——**这是执笔 agent 的核心职责**
数字被撤回时,**三步缺一不生效**:①写撤回声明 ②**全库反扫**其所有引用(含派生值/反推值/别名,grep decisions_log + sprint*_status + deliverables + 对外交付) ③逐处「加撤回警示标 或 删除」。清扫未完成前不得宣称"已撤回/已修正"。（worked example：PF-8 撤 d=30→全库反扫加标，见 decisions_log。）

### 0.4 外部输入入库（铁律六 / C8，≤24h，BLOCKER）
CTO 外部接收的 datasheet/报价/文档 ≤24h 入库并标日期+来源；Sprint 收尾以 CTO 外部接收声明清单为唯一核对基线。

### 0.5 三道关（产出含修正稿）
本 agent 的文档/日志草稿**不是权威**,须过 自动verify→**独立 critic**→CTO 常识审;修正稿同等过门（缘起 R8/R9 修正稿自带新错）。

### 0.6 绑定的真实产物（非虚构服务）
权威源：`sprint2/docs/POLICY-PROV-001_数字来源分级制度.md`（治理全文）、`sprint2/docs/decisions_log.md`（决策）、`sprint*_status.md`（状态）、`deliverables/`（交付物）、`.claude/skills/critic/SKILL.md`（C1–C10/§12 门）。**读写=直接操作这些 repo 文件；通信=SendMessage；无独立数据库/REST 服务（原 §6 的 API 是虚构，已删）。**

---

## 技能1: 报告生成流程 `SKILL-DOC-001`

### 概述
将各领域Agent的原始产出转化为标准化、高质量的技术文档，确保信息准确、格式统一、可读性强。

### 标准生成流程

```yaml
report_generation_pipeline:
  Step_1_数据收集:
    input: "各领域Agent的原始产出"
    format: "Markdown / JSON / CSV / 结构化文本"
    validation: "检查数据完整性，确认必需字段"
    
  Step_2_结构生成:
    activity: "根据文档类型选择模板，生成文档骨架"
    output: "带占位符的文档结构"
    
  Step_3_内容填充:
    activity: "将原始数据映射到模板字段"
    rules:
      - "数据直接填入对应字段"
      - "缺失字段标记为 [待补充]"
      - "长数据自动分页/分节"
      - "图表自动生成引用编号"
      
  Step_4_术语统一:
    activity: "使用术语词典统一术语"
    method: "自动替换 + 首次出现展开"
    output: "术语统一的文档草稿"
    
  Step_5_格式标准化:
    activity: "应用文档格式规范"
    items:
      - "标题层级统一 (# ## ###)"
      - "列表格式统一"
      - "表格格式统一"
      - "代码块标注语言"
      - "图片编号连续 (图1, 图2...)"
      - "表格编号连续 (表1, 表2...)"
      
  Step_6_审校:
    activity: "质量检查"
    checks:
      - "完整性: 模板字段覆盖率100%"
      - "一致性: 术语/格式/编号"
      - "可读性: 语言简洁，逻辑清晰"
      - "准确性: 数据与原始记录一致"
      - "★溯源(§0/C1): 每个数字挂 L 标? 有无 L2/L3/L4 被措辞成'实测/measured'(C2)?"
      - "★撤回(§0/C7): 引用的数字若已撤回,是否已加标/删(铁律五全库传播完成)?"
      - "★权威: 承重结论有 reviewer:critic 标记? 未过独立 critic 的草稿不标'已发布'"
      
  Step_7_输出:
    formats: ["Markdown (源文件)", "PDF (发布版)", "HTML (在线版)"]
    output: "多格式文档包"
```

### 多格式输出规范

```yaml
output_formats:
  markdown_source:
    purpose: "可编辑源文件"
    naming: "{doc_id}_{title}_v{version}.md"
    structure: "完整的Markdown + YAML frontmatter"
    
  pdf_output:
    purpose: "正式发布/打印"
    tool: "WeasyPrint / wkhtmltopdf"
    template: "ITC企业样式 (页眉/页脚/页码)"
    features:
      - "封面页 (标题/版本/日期/作者)"
      - "目录 (自动生成)"
      - "页眉 (文档标题)"
      - "页脚 (页码 + 公司名)"
      - "修订历史表"
      
  html_output:
    purpose: "在线浏览/Confluence导入"
    features:
      - "响应式布局"
      - "语法高亮"
      - "可折叠章节"
      - "内部锚点链接"
      
  word_output:
    purpose: "外部协作 (如需)"
    tool: "Pandoc md→docx"
    template: "ITC Word模板"
```

---

## 技能2: 文档模板库 `SKILL-DOC-002`

### 模板清单

#### 2.1 设计文档模板 `TPL-DOC-001`

```markdown
---
doc_id: "DOC-XXX-001"
title: "[项目名称] — [文档类型]"
version: "V1.0.0"
status: "草稿 / 审核中 / 已发布"
author: "[来源Agent名称]"
date: "YYYY-MM-DD"
template_version: "TPL-DOC-001-v2.1"
---

# [产品/项目名称] 设计文档

## 修订历史

| 版本 | 日期 | 作者 | 变更描述 |
|------|------|------|----------|
| V0.1 | YYYY-MM-DD | [Agent] | 初稿 |
| V1.0 | YYYY-MM-DD | [Agent] | 正式发布 |

## 1. 概述
### 1.1 目的
[本文档的目的和范围]

### 1.2 参考文档
| 编号 | 文档名称 | 版本 | 来源 |
|------|----------|------|------|
| REF-001 | [文档名] | VX.Y | [Agent/系统] |

### 1.3 术语和缩写
| 术语/缩写 | 全称 | 定义 |
|-----------|------|------|
| [缩写] | [全称] | [定义] |

## 2. 设计输入
### 2.1 需求追溯
| 需求ID | 需求描述 | 设计对应章节 |
|--------|----------|-------------|
| REQ-001 | [需求] | 第X节 |

### 2.2 约束条件
[设计约束列表]

## 3. 设计方案
### 3.1 方案概述
[设计思路和方案选择]

### 3.2 详细设计
[分节详细描述]

#### 3.2.X [子系统/模块名称]
[详细设计内容，含图表引用]

图X — [图标题]

## 4. 设计验证
### 4.1 验证方法
### 4.2 验证结果
### 4.3 遗留问题

## 5. 附录
### 5.1 参考文献
### 5.2 变更记录
```

#### 2.2 测试报告模板 `TPL-DOC-002`

```markdown
---
doc_id: "DOC-XXX-002"
title: "[项目名称] — 测试报告"
version: "V1.0.0"
template_version: "TPL-DOC-002-v2.0"
---

# [产品/项目名称] 测试报告

## 1. 测试概要
| 项目 | 内容 |
|------|------|
| 测试阶段 | EVT / DVT / PVT |
| 测试时间 | YYYY-MM-DD ~ YYYY-MM-DD |
| 测试样品 | SN: XXXXX ~ XXXXX (共N台) |
| 测试环境 | 温度: XX°C, 湿度: XX%RH |
| 测试设备 | [设备清单] |

## 2. 测试项目汇总
| 类别 | 测试项数 | Pass | Fail | N/A | 通过率 |
|------|----------|------|------|-----|--------|
| 音频性能 | XX | XX | XX | XX | XX% |
| 环境可靠性 | XX | XX | XX | XX | XX% |
| ... | ... | ... | ... | ... | ... |
| **合计** | **XX** | **XX** | **XX** | **XX** | **XX%** |

## 3. 详细测试结果
### 3.X [测试类别]
#### 3.X.Y [测试项]
- **测试ID**: TC-XXX-YYY
- **测试条件**: [条件]
- **测试结果**: [数据/曲线]
- **判定**: Pass / Fail
- **备注**: [如有]

## 4. 问题汇总
| 问题ID | 严重度 | 描述 | 状态 |
|--------|--------|------|------|
| ISS-001 | Critical/High/Med/Low | [描述] | 开放/关闭 |

## 5. 结论
[总体结论和放行建议]

## 附录
- 原始数据文件
- 测试日志
```

#### 2.3 会议纪要模板 `TPL-DOC-003`

```markdown
---
doc_id: "DOC-MTG-001"
title: "[会议主题] — 会议纪要"
template_version: "TPL-DOC-003-v1.5"
---

# 会议纪要: [会议主题]

| 项目 | 内容 |
|------|------|
| 会议时间 | YYYY-MM-DD HH:MM ~ HH:MM |
| 会议地点 | [地点/线上] |
| 会议类型 | 评审会 / 周例会 / 专题讨论 / 决策会 |
| 记录人 | [文档Agent] |

## 出席人员
| 角色 | Agent/人员 | 出席 |
|------|-----------|------|
| 主持 | [项目经理Agent] | ✓ |
| [角色] | [Agent名称] | ✓/✗ |

## 议程
1. [议程项1]
2. [议程项2]

## 讨论纪要

### 议题1: [议题标题]
**提出**: [提出者]
**讨论内容**: [要点记录]
**决议**: [决议内容 / 未决]
**行动项**: [如有，见行动项表]

## 行动项跟踪

| 编号 | 行动项 | 负责人 | 截止日期 | 优先级 | 状态 |
|------|--------|--------|----------|--------|------|
| A01 | [具体行动] | [Agent] | YYYY-MM-DD | P1 | 待开始 |

## 下次会议
- 时间: [YYYY-MM-DD HH:MM]
- 主要议题: [预告]

---
*本纪要由 Project Document Agent 整理，如有遗漏请联系*
```

#### 2.4 变更请求(ECR)模板 `TPL-DOC-004`

```markdown
---
doc_id: "ECR-XXXX"
title: "[项目名称] — 变更请求"
template_version: "TPL-DOC-004-v2.0"
---

# 工程变更请求 (ECR)

| 项目 | 内容 |
|------|------|
| ECR编号 | ECR-XXXX |
| 提出日期 | YYYY-MM-DD |
| 提出人/Agent | [名称] |
| 变更类别 | 设计变更 / 材料变更 / 工艺变更 / 规格变更 |
| 优先级 | P0(紧急) / P1(重要) / P2(一般) |
| 状态 | 提交 / 评审中 / 已批准 / 已拒绝 / 已实施 |

## 1. 变更描述
### 1.1 变更原因
[变更的背景和原因]

### 1.2 变更内容
[具体变更描述]

**变更前**: [原方案/参数]
**变更后**: [新方案/参数]

## 2. 影响分析
### 2.1 影响范围
| 影响领域 | 影响程度 | 具体影响 | 需确认Agent |
|----------|----------|----------|-------------|
| 结构 | 高/中/低/无 | [描述] | [Agent] |
| 声学 | 高/中/低/无 | [描述] | [Agent] |
| 硬件 | 高/中/低/无 | [描述] | [Agent] |
| 软件 | 高/中/低/无 | [描述] | [Agent] |
| 测试 | 高/中/低/无 | [描述] | [Agent] |
| 制造 | 高/中/低/无 | [描述] | [Agent] |
| 成本 | 高/中/低/无 | [描述] | [Agent] |

### 2.2 风险分析
| 风险项 | 概率 | 影响 | 缓解措施 |
|--------|------|------|----------|
| [风险] | 高/中/低 | [描述] | [措施] |

## 3. 验证计划
[变更后如何验证]

## 4. 审批
| 审批角色 | 审批人/Agent | 审批意见 | 日期 |
|----------|-------------|----------|------|
| 技术评审 | [评审Agent] | [同意/反对+理由] | YYYY-MM-DD |
| 项目经理 | [PM Agent] | [同意/反对+理由] | YYYY-MM-DD |

## 5. 实施记录
| 项目 | 内容 |
|------|------|
| ECO编号 | [关联的ECO编号] |
| 实施日期 | YYYY-MM-DD |
| 验证结果 | [结果] |
| 关闭日期 | YYYY-MM-DD |
```

#### 2.5 用户手册模板 `TPL-DOC-005`

```markdown
---
doc_id: "DOC-UM-001"
title: "[产品名称] — 用户手册"
version: "V1.0"
template_version: "TPL-DOC-005-v1.8"
---

# [产品名称] 用户手册

## 1. 产品概述
### 1.1 产品简介
### 1.2 包装清单
### 1.3 产品规格

## 2. 快速入门
### 2.1 外观介绍
### 2.2 首次使用
### 2.3 基本操作

## 3. 详细功能
### 3.1 [功能1]
### 3.2 [功能2]

## 4. 连接方式
### 4.1 蓝牙配对
### 4.2 有线连接
### 4.3 应用程序

## 5. 维护与故障排除
### 5.1 日常维护
### 5.2 常见问题
| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| [问题] | [原因] | [方法] |

## 6. 安全须知

## 7. 规格参数

## 8. 售后服务
```

---

## 技能3: 知识库维护规范 `SKILL-DOC-003`

### 分类体系

```yaml
knowledge_base_taxonomy:
  version: "2024-v2.0"
  
  一级分类:
    - id: "KB-DESIGN"
      name: "设计知识"
      description: "产品设计相关的技术知识"
      subcategories:
        - "声学设计"
        - "结构设计"
        - "硬件设计"
        - "软件/DSP设计"
        - "工业设计"
        
    - id: "KB-TEST"
      name: "测试验证"
      description: "测试方法、标准、经验"
      subcategories:
        - "音频测试"
        - "声学测试"
        - "环境可靠性测试"
        - "自动化测试"
        - "测试设备"
        
    - id: "KB-MATERIAL"
      name: "材料与工艺"
      description: "材料性能、加工工艺知识"
      subcategories:
        - "声学材料"
        - "结构材料"
        - "电子材料"
        - "加工工艺"
        - "表面处理"
        
    - id: "KB-PROCESS"
      name: "流程与规范"
      description: "工作流程、标准规范"
      subcategories:
        - "设计流程"
        - "测试流程"
        - "制造流程"
        - "质量管理"
        - "项目管理"
        
    - id: "KB-PROBLEM"
      name: "问题与解决"
      description: "历史问题、根因、解决方案"
      subcategories:
        - "音频问题"
        - "结构问题"
        - "电子问题"
        - "软件问题"
        - "系统性问题"
        
    - id: "KB-INTEL"
      name: "技术情报"
      description: "竞争情报、专利、论文"
      subcategories:
        - "专利情报"
        - "论文摘要"
        - "竞品分析"
        - "技术趋势"
        - "标准法规"
        
    - id: "KB-SUPPLIER"
      name: "供应商"
      description: "供应商信息、评估记录"
      subcategories:
        - "扬声器供应商"
        - "电子元器件供应商"
        - "结构加工供应商"
        - "材料供应商"
        - "测试设备供应商"
        
    - id: "KB-PROJECT"
      name: "项目档案"
      description: "历史项目文档和经验"
      subcategories:
        - "项目总结"
        - "设计文档归档"
        - "测试报告归档"
        - "经验教训"
```

### 标签系统

```yaml
tagging_system:
  标签类型:
    technology:
      examples: ["ANC", "DSP", "bluetooth", "LE-Audio", "spatial-audio", "class-d"]
      source: "技术领域自动提取 + 手动标注"
      
    product_type:
      examples: ["active-speaker", "soundbar", "TWS", "portable-speaker", "subwoofer"]
      source: "产品类型分类"
      
    difficulty:
      examples: ["beginner", "intermediate", "advanced", "expert"]
      source: "内容复杂度评估"
      
    status:
      examples: ["current", "deprecated", "draft", "reviewed"]
      source: "知识条目状态"
      
    project:
      examples: ["PRJ-2401", "PRJ-2403"]
      source: "关联项目"
      
    agent_source:
      examples: ["agent.structure", "agent.testing", "agent.acoustic"]
      source: "知识来源Agent"

  标签规则:
    - "每条知识至少3个标签"
    - "技术标签 mandatory"
    - "标签使用规范写法 (小写，连字符连接)"
    - "定期清理废弃标签"
```

### 关联规则

```yaml
linking_rules:
  关联类型:
    relates_to:
      description: "一般关联，内容相关"
      strength: 1
      
    depends_on:
      description: "依赖关系，B依赖A"
      strength: 3
      
    supercedes:
      description: "替代关系，B替代A"
      strength: 3
      
    contradicts:
      description: "矛盾关系，B与A矛盾"
      strength: 2
      
    example_of:
      description: "实例关系，B是A的实例"
      strength: 1
      
    prerequisite:
      description: "前置知识，学习B前需了解A"
      strength: 2

  关联维护:
    - "新条目创建时自动推荐关联 (基于标签和内容相似度)"
    - "每周检查孤立条目 (无关联)"
    - "每月审查关联准确性"
    - "知识库Agent自动维护关联图谱"
```

---

## 技能4: 版本管理策略 `SKILL-DOC-004`

### 版本号规则

```yaml
version_numbering:
  format: "VX.Y.Z"
  
  X_主版本:
    increment: "重大结构变更、重新组织、换版"
    examples: "V1.0.0 → V2.0.0"
    
  Y_次版本:
    increment: "内容增补、新章节、重要更新"
    examples: "V1.0.0 → V1.1.0"
    
  Z_修订版本:
    increment: "错别字修正、格式调整、小幅更新"
    examples: "V1.0.0 → V1.0.1"
    
  special_suffixes:
    - "-draft": 草稿状态"
    - "-review": 审核中"
    - "-final": 最终版"
    
  examples:
    - "V1.0.0-draft: 初稿"
    - "V1.0.0-review: 提交审核"
    - "V1.0.0: 正式发布"
    - "V1.0.1: 发布后小修正"
    - "V1.1.0: 增加新章节"
    - "V2.0.0: 重大改版"
```

### 变更历史管理

```yaml
change_log_format:
  revision_history_table:
    columns:
      - "版本"
      - "日期"
      - "作者"
      - "变更类型 (新增/修改/删除/修正)"
      - "变更描述"
      - "影响范围"
      
  change_types:
    ADDED: "新增内容"
    MODIFIED: "修改现有内容"
    DELETED: "删除内容"
    FIXED: "修正错误"
    REFACTORED: "重构 (无内容变更)"
    
  best_practices:
    - "每次变更产生新版本号"
    - "变更描述具体到章节"
    - "重大变更说明理由"
    - "保持完整的版本链"
```

### 审批流程

```yaml
approval_workflow:
  draft:
    status: "草稿"
    editable_by: "来源Agent"
    next_state: "submitted"
    
  submitted:
    status: "已提交待审"
    action: "文档Agent进行格式和质量检查"
    if_pass: → review
    if_fail: → draft (退回修正)
    
  review:
    status: "审核中"
    reviewers: "领域专家Agent + 评审Agent"
    parallel: true
    if_approved: → approved
    if_rejected: → draft (附修改意见)
    
  approved:
    status: "已批准"
    action: "文档Agent最终格式化"
    next_state: "published"
    
  published:
    status: "已发布"
    action: "归档到知识库，通知相关Agent"
    locked: true  # 发布后不可直接编辑
    edit_path: "走ECR流程"
    
  archived:
    status: "已归档"
    trigger: "被新版本替代 / 项目结束 / 内容过期"
    action: "保留历史版本，标记为已归档"
```

---

## 技能5: 文档质量检查 `SKILL-DOC-005`

### 质量检查清单

#### 完整性检查

```yaml
completeness_check:
  frontmatter:
    - [ ] doc_id 存在且唯一
    - [ ] title 存在且描述性
    - [ ] version 存在且符合格式
    - [ ] author 存在
    - [ ] date 存在且合理
    - [ ] template_version 存在
    
  structure:
    - [ ] 模板必需章节全部存在
    - [ ] 无空章节 (至少有一句描述)
    - [ ] 修订历史存在且非空
    - [ ] 目录结构合理 (层级≤4)
    
  content:
    - [ ] 无 [待补充] 占位符 (草稿除外)
    - [ ] 所有表格非空
    - [ ] 图表有标题和编号
    - [ ] 外部引用有超链接或编号
```

#### 一致性检查

```yaml
consistency_check:
  terminology:
    - [ ] 术语使用与术语词典一致
    - [ ] 缩写首次出现有展开
    - [ ] 同一概念不使用不同术语
    - [ ] 产品名称/型号前后一致
    
  formatting:
    - [ ] 标题层级连续 (无跳级)
    - [ ] 列表格式统一
    - [ ] 表格列数一致
    - [ ] 代码块有语言标注
    - [ ] 图片有alt文本
    
  numbering:
    - [ ] 图表编号连续
    - [ ] 章节编号连续
    - [ ] 引用编号正确
    - [ ] 版本号与修订历史一致
```

#### 可读性检查

```yaml
readability_check:
  language:
    - [ ] 句子长度适中 (<30字)
    - [ ] 段落长度适中 (<5行)
    - [ ] 无错别字
    - [ ] 无语法错误
    - [ ] 技术术语使用恰当
    
  structure:
    - [ ] 逻辑顺序清晰
    - [ ] 信息密度适中
    - [ ] 重点突出 (加粗/列表)
    - [ ] 过渡自然
    
  accessibility:
    - [ ] 图表有文字说明
    - [ ] 缩写有解释
    - [ ] 外部引用可访问
```

### 质量评分标准

| 维度 | 权重 | 优秀 (90-100) | 良好 (75-89) | 合格 (60-74) | 不合格 (<60) |
|------|------|---------------|-------------|-------------|-------------|
| 完整性 | 0.30 | 100%字段填充 | <5%缺失 | <15%缺失 | >15%缺失 |
| 一致性 | 0.25 | 零问题 | <3个问题 | <8个问题 | ≥8个问题 |
| 可读性 | 0.25 | 流畅易读 | 基本清晰 | 需要改进 | 难以理解 |
| 格式规范 | 0.20 | 完全符合模板 | 小偏差 | 明显偏差 | 严重偏差 |

---

## 技能6: 跨域协作接口 `SKILL-COL-001`

### 知识库 = repo 内的 markdown 文件（无独立数据库/REST 服务）

> **项目化焊接（roadmap#5 样板）：原文此处是虚构的 `agent.database` REST API + GraphQL（POST /api/kb/entries、graph_query、`total_hits: 156` 等）——本项目没有这个服务，全是占位。已删。**

- **知识库实体** = repo 里的 markdown：`sprint2/docs/decisions_log.md`（决策台账）、`sprint*_status.md`（状态）、`deliverables/`（交付物）、各 `sprint*/` 文档、`knowledge_base/`（厂商资料，gitignore 本地）。
- **CRUD** = 直接用文件工具读写这些 md + git 版本管理（非 REST）；**检索** = 仓库内 grep/文件搜索。
- **关联/图谱** = 靠文内 `[[链接]]` / DEC-ID 交叉引用 + grep，非图数据库。
- **写入纪律**：任何进 decisions_log/交付物的数字先过 §0（L 标 / DEC 格式 / 铁律五传播）。

### 与各领域Agent的协作接口

```yaml
collaboration_interfaces:
  structure_agent:
    document_delivery:
      trigger: "结构设计完成"
      input: "结构设计文档 (Markdown) + BOM (CSV) + DFM报告 (Markdown)"
      processing: "模板匹配 + 术语统一 + 格式标准化 + 质量检查"
      output: "标准化文档包 + 知识库条目"
      feedback: "质量检查报告 (如有问题需修正)"
      
    # 模板/术语非 REST 服务（原 GET /api/doc/... 为虚构，已删）：模板 = 本 skill §技能2 的
    # TPL-DOC-*；术语 = repo 内术语表文件；直接读取，不调 API。交付触发/输入靠 SendMessage。
    
  testing_agent:
    document_delivery:
      trigger: "测试完成"
      input: "测试报告 (Markdown) + 原始数据 (CSV) + 缺陷报告 (JSON)"
      processing: "模板渲染 + 数据整合 + 统计图表生成"
      output: "标准化测试报告 (MD + PDF)"
      
  literature_patent_agent:
    document_delivery:
      trigger: "情报报告发布"
      input: "监控周报/月报 (Markdown) + 专利分析 (Markdown)"
      processing: "模板匹配 + 情报分类归档"
      output: "标准化报告 + 知识库情报条目"
      
    intelligence_archive:
      action: "专利/论文情报自动入库"
      category: "KB-INTEL"
      auto_tag: true
      
  project_manager_agent:
    meeting_minutes:
      trigger: "会议结束"
      input: "会议录音/纪要草稿"
      processing: "结构化整理 + 行动项提取 + 决议归档"
      output: "标准会议纪要 + 行动项跟踪表"
      
    status_report:
      trigger: "项目里程碑 / 定期(周)"
      input: "各Agent状态JSON"
      processing: "汇总 + 可视化 + 风险高亮"
      output: "项目状态报告 (MD + PDF)"
      
    ecr_management:
      trigger: "ECR提交"
      processing: "ECR文档化 + 影响分析表格化 + 审批流程跟踪"
      output: "标准化ECR文档 + 审批状态"
```

### 自动生成摘要和关键词

```yaml
auto_summarization:
  input: "长文档 (设计文档/测试报告/技术报告)"
  output: "摘要 + 关键词"
  
  methods:
    extractive:
      description: "提取原文关键句子"
      technique: "TF-IDF + TextRank"
      length: "原文的10-15%"
      
    abstractive:
      description: "生成式摘要"
      technique: "LLM-based (如可用)"
      length: "100-200字"
      
  keyword_extraction:
    methods:
      - "TF-IDF 关键词提取"
      - "命名实体识别 (NER)"
      - "技术术语词典匹配"
    output_count: "5-10个关键词"
    format: "规范写法 (小写，连字符)"
```

---

## 输入/输出规范

### 标准输入

| 输入类型 | 格式 | 来源 | 验证规则 |
|----------|------|------|----------|
| 原始技术文档 | Markdown | 各领域Agent | 基本Markdown语法 |
| 结构化数据 | JSON/CSV | 各领域Agent | Schema验证 |
| 会议纪要草稿 | Markdown/文本 | 项目经理Agent | 时间/出席/议题完整 |
| ECR申请 | Markdown JSON | 各领域Agent | 变更描述+影响分析 |
| 知识条目提交 | Markdown JSON | 各领域Agent | 分类+标签+内容 |
| 查询请求 | JSON | 各Agent | 查询类型+参数 |

### 标准输出

| 输出类型 | 格式 | 目标 | 质量检查 |
|----------|------|------|----------|
| 标准化文档 | MD + PDF | 来源Agent + 评审 | 质量评分≥85 |
| 知识库条目 | Markdown | 知识库用户 | 分类+标签完整 |
| 会议纪要 | Markdown | 参会Agent | 决议+行动项完整 |
| 项目状态报告 | MD + PDF | 项目经理Agent | 数据准确+可视化 |
| ECR文档 | MD + PDF | 审批链Agent | 影响分析完整 |
| 用户手册 | MD + PDF | 市场Agent+用户 | 读者测试通过 |
| 术语查询结果 | JSON | 查询Agent | 定义准确 |
| 模板列表 | JSON | 请求Agent | 模板ID+描述 |

### 质量检查清单 (自检)

```yaml
pre_delivery_check:
  - [ ] 文档ID唯一且规范
  - [ ] 版本号正确递增
  - [ ] 模板字段100%填充 (或标记为N/A)
  - [ ] 术语与术语词典一致
  - [ ] 缩写首次出现已展开
  - [ ] 图表编号连续
  - [ ] 外部引用可访问/可追踪
  - [ ] 修订历史完整
  - [ ] 格式符合模板规范
  - [ ] Markdown语法正确
  - [ ] PDF生成成功且格式正确
  - [ ] 知识库条目分类+标签完整
  - [ ] 关联条目正确
  - [ ] 质量评分≥85 (或标注例外原因)
```
