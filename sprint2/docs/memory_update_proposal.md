# 项目记忆更新建议（Sprint 2 → MEMORY 条目草案）

> ⚠️ 历史归档/作废（PF-8，2026-05-29）：本文件含基于 d=30 错误几何（Sprint2 视觉估测值，已被拆机实测真值 d=55 取代，DEC-S3-GEOM-01）的结论/数据，仅作历史留痕，**不可作任何决策依据**。现行 d=55 基线见 decisions_log DEC-S3-GEOM-01 / PROJECT_HANDOVER.md。

**文档 ID**：DOC-MEM-002  
**版本**：v1.0  
**作者**：项目文档专家 Agent  
**日期**：2026-05-26  
**状态**：⚠️ 建议草案，需 Team Lead（项目经理 Agent）+ CTO 确认后方可写入 MEMORY

> 本文件仅为提案，不直接修改 MEMORY 系统。确认流程：
> 1. 项目文档 Agent 提交本草案
> 2. Project Manager Agent 审核后提交 CTO
> 3. CTO 批准 → 由 Team Lead 执行写入操作

---

## 建议新增 MEMORY 条目

### 条目 1：Sprint 2 算法与硬件基线（建议写入）

**标题**：Sprint 2 算法/声学/硬件基线

**推荐 MEMORY 标题行**：
```
- [Sprint 2 baseline: acoustics, DSP, HW, patent](sprint2-baseline.md)
  — 4 候选阵元方案 + dyadic FIR 结构 + BOM 估算 + 专利风险修订
```

**建议写入 sprint2-baseline.md 的内容**：

```markdown
# Sprint 2 基线汇总（已过 Critic 评审）
更新时间：2026-05-26

## 声学仿真基线
- 竞品逆向反推：N≈20 / d=35mm / Dolph-Cheby -20dB（RMS误差2.84dB，置信度中等）
- 竞品隐含BW：1kHz≈36.6° / 2kHz≈18.1° / 4kHz≈9.0°（4kHz仅供参考）
- 候选方案仿真BW（-6dB @ 2kHz）：
  - N=16/d=35/uniform：≈21.3°，旁瓣-13dB
  - N=24/d=35/Dolph-30dB：≈17.8°，旁瓣-30dB
  - N=32/d=35/uniform：≈10.6°，旁瓣-13dB
- 栅瓣警告：d=35mm在8kHz出现栅瓣；d=30mm临界频率5.7kHz，更安全
- Critic倾向：d=30mm

## DSP算法基线
- 采用路线：dyadic树形半带FIR（非全速率）+ 4子带DAS，48kHz
- 算力：56.4 MMAC/s（16ch），83 MMAC/s（24ch），裕量分别27×/18×
- SRAM：27.3KB（1.6%）
- Kaiser FIR阻带：58-73dB
- 残留风险：树形C代码未实现，Sprint 3需完成CCES移植

## I/O约束（24ch扩展时）
- 需2×SPORT或TDM-32模式 + 第3片Codec（3×ADAU1962A）
- 算力不是瓶颈，I/O接口才是关键约束

## 硬件BOM（1k量级估算，含Critic修正）
- 16ch：¥1169-2065（ADSP-21569 ¥120-220，非原报告偏高值）
- 24ch：¥1452-2631
- 功耗：典型语音 16ch≈54W / 24ch≈80W

## 专利基线
- Dolph-Chebyshev：公有领域，可自由使用
- Boone endfire EP1986464A1：降级为低风险（ITC走broadside）
- 需关注：broadside可控阵列组合专利（如Fincham类，≈2027到期）
- 5个差异化方向：子带SCBT / 低频差分+高频相控混合 / 单元自校准 / 近场多区聚焦 / AI声场自适应
```

---

## 4 个待决策项（Sprint 3 前 CTO 必须拍板）

以下为 Gate 2 决策清单，建议同步写入 MEMORY 的待决策区：

### PEND-001：阵元间距 d

| 要素 | 内容 |
|------|------|
| **决策问题** | d = 30mm（栅瓣安全）vs d = 35mm（指向好但 8kHz 栅瓣）？ |
| **技术倾向** | Critic Agent 倾向 d=30mm |
| **待决策方** | CTO |
| **影响范围** | 阵列总长、频率上限、PRD 指标 |
| **截止要求** | Sprint 3 启动前 |

---

### PEND-002：阵元数 N

| 要素 | 内容 |
|------|------|
| **决策问题** | N = 16（简单低成本）vs N = 24（性能接近竞品但 I/O 复杂）？ |
| **技术数据** | 16ch BW@2k≈21.3°；24ch BW@2k≈17.8°（竞品≈18.1°） |
| **成本差异** | BOM 差约 ¥283-566（24ch 偏高） |
| **待决策方** | CTO |
| **影响范围** | Codec 数量、功放数量、PCB 面积、BOM 成本 |
| **截止要求** | Sprint 3 启动前 |

---

### PEND-003：差异化专利申请启动

| 要素 | 内容 |
|------|------|
| **决策问题** | 是否立即启动专利申请？选哪 1-2 个方向？ |
| **可选方向** | ①子带SCBT ②低频差分+高频相控混合 ③单元自校准 ④近场多区聚焦 ⑤AI声场自适应 |
| **建议优先** | ①②（技术成熟度和差异化程度综合最优） |
| **待决策方** | CTO |
| **影响范围** | 知识产权布局、研发资源分配、Sprint 3 排期 |
| **截止要求** | 方向选择在 Sprint 3 前；实际申请可延后 |

---

### PEND-004：委托专利代理核查 broadside 可控阵列组合专利

| 要素 | 内容 |
|------|------|
| **决策问题** | 是否委托专利代理核查 Fincham 类专利的中国同族？ |
| **风险背景** | 约 2027 年到期；若中国同族有效，2027 年前商业化存在风险 |
| **不核查的代价** | 盲目规避成本高；若侵权则法律风险 |
| **核查成本估算** | 专利检索 ¥5000-20000（代理机构报价区间，待询价） |
| **待决策方** | CTO |
| **影响范围** | 法律合规、商业化时间表 |
| **截止要求** | Sprint 3 启动前（越早越好） |

---

## 建议 MEMORY INDEX 更新格式

在 `/home/it1234/.claude/projects/.../memory/MEMORY.md` 中追加以下行：

```markdown
- [Sprint 2 baseline: acoustics/DSP/HW/patent](sprint2-baseline.md)
  — dyadic树形FIR基线 + 三档候选方案BW数据 + BOM估算(Critic修正) + 专利风险修订
```

同时在对应 sprint2-baseline.md 文件中写入上方"建议写入内容"块的正文。

---

## 确认授权单

| 事项 | 负责人 | 状态 |
|------|--------|------|
| 草案内容技术核准 | Project Manager Agent | ⏳ 待核准 |
| MEMORY 写入授权 | CTO（总工） | ⏳ 待批准 |
| 执行写入操作 | Team Lead（Project Manager Agent） | ⏳ 待执行 |
| PEND-001 拍板 | CTO | ⏳ 待决策 |
| PEND-002 拍板 | CTO | ⏳ 待决策 |
| PEND-003 拍板 | CTO | ⏳ 待决策 |
| PEND-004 拍板 | CTO | ⏳ 待决策 |

---

*本草案由项目文档专家 Agent 依据 Sprint 2 各领域 Agent 产出（已过 Critic 评审）生成*  
*文档专家 Agent 无权直接写入 MEMORY — 须经 Team Lead + CTO 授权执行*  
*v1.0，2026-05-26*
