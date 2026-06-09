# Critic 终审 段2/3 — d=30 残留清除 + cces Q1+

**任务**：TASK-PF8-FINAL-S2 | **评审员**：Critic（critic-itc-001）| **日期**：2026-05-29
**范围**：① cces d=30 残留（CTO 点名 Q1+）② 活文档 d=30 现行基线残留 ③ 作废 banner 抽查
**前提**：d=55 硬锁不议（DEC-S3-GEOM-01）。本段未触发 🚨ESCALATE。

---

## 件 1：cces d=30 残留（CTO 点名）— ✅ 已清，零残留

grep 命令（任务指定模式）：
```
grep -rniE "30u|0\.030|d=30|30mm|= 54|54u" sprint2/dsp/cces_template/
→ EXIT=1（零命中）
```

- **cces d=30 残留已清**：`cces_template/` 全目录对 `30u / 0.030 / d=30 / 30mm / =54 / 54u` **零命中**。
- config.h 现行值核对：
  - `config.h:59  #define ARRAY_ELEMENT_SPACING_MM    55u` ✅
  - `config.h:100 #define MAX_INT_DELAY_SAMPLES       92u` ✅
  - `README.md:65` 同步标 `55 …（L1 拆机实测 / DEC-S3-GEOM-01）` ✅
- 旁证：`critic_p0b_review.md:25` 记录的 `ARRAY_ELEMENT_SPACING_MM 30u` 系“废弃全速率模板”，本次已确认不在现行 `cces_template/` 内。

**结论：cces d=30 残留已清（明确）。PASS。**

---

## 件 2：活文档无 d=30 现行基线残留 — ✅ 通过（3 处修复全部确认对）

全项目 grep（排除 55/作废/历史/归档/PF-8/deprecat/archiv/DEC-S1-003/historical 等）后逐条裁定：剩余命中**全部属合规类别**——
(a) 历史/归档文件（带 banner）；(b) 历史事件叙述（decisions_log DEC 条目、PF8_retrospective、p0b/p1b 资产清单）；(c) 更正记录行（sweep_report §7.3 “原表述不严谨予以更正”）；(d) **非阵元间距**用法（hardware skill 散热片包络 `80×60×30mm`、structure 螺钉间距 `≤30mm`）。**无任何活文档把 d=30 当现行基线。**

PM 已修的 3 处逐一核验：

| # | 文件 | 应为 | 实测 | 判定 |
|---|------|------|------|------|
| 1 | `CLAUDE.md` 启动 prompt | d=55mm | `:85 Element spacing d = 55mm (L1 teardown-measured; d=30mm … retired by PF-8/DEC-S3-GEOM-01)`；`:83` 标注 illustrative + current locked d=55 | ✅ 改对 |
| 2 | `sprint2/docs/prd_update.md` 锁定表 | d=55/L=825，旧 d=30 划线作废 | `:21` 阵元间距 **55mm[L1拆机实测]**；`:25` L=825mm；§0-历史 `:36-38` 旧 d=30/450mm 行 `~~划线~~`+作废标记 | ✅ 改对 |
| 3 | `sprint3/dsp/dsp_8ch_report.md` 栅瓣 | d=55/6.2–8k 有栅瓣 | `:38` 几何更正 d=55；`:45` SB3 “**6.2–8kHz 段有栅瓣**”；`:48-49` 500Hz–5kHz 安全/6.2–8kHz 栅瓣峰 0dB；非“d=30 全频段无栅瓣” | ✅ 改对 |

**结论：活文档无 d=30 现行基线残留；3 处修复全部确认改对。PASS。**

---

## 件 3：作废 banner 抽查 — ✅ 三件齐备，正文未删，.py 语法未破坏

| 抽查文件 | banner 在？ | 正文保留？ | 备注 |
|---|---|---|---|
| `deliverables/Gate1-baseline-array-validation-2026-05-26.md` | ✅ 行2 “⚠️ 历史归档/作废（PF-8…d=30→d=55…）” | ✅ 字段表/正文完整 | 归档=保留+加标 |
| `sprint2/SPRINT2_CTO_REPORT.md` | ✅ 行2 同款 banner | ✅ 正文完整 | 同上 |
| `sprint2/acoustic/array_sweep.py` | ✅ 置于模块 docstring `"""…"""` 内 | ✅ 代码正文完整 | banner 在三引号内，**未破坏 Python 语法** |

**结论：作废 banner 到位，归档语义正确（保留+加标），.py banner 未破坏语法。PASS。**

---

## 裁决

**PASSED**（三件全部 PASS）。

- cces d=30 残留：**已清（零命中，55u/92u 确认）**。
- 活文档 d=30 现行残留：**无**（3 处修复确认改对）。
- 作废 banner：**到位**（3 抽样齐备，.py 语法完好）。
- **BLOCKER：0** | **MAJOR：0**
- **MINOR：0**（无须修，仅备注：剩余 d=30 字样均为合规的历史/更正/非间距用法，符合“归档保留备查”策略；如后续追求洁净度可考虑给 `sprint2/acoustic/1khz_optimization.md`、`diff_1khz_optimization.py` 等仍以 d=30 为标题/基线叙述的历史分析文件补 banner，但非本段门禁项，留 PF-8 段3 统筹）。

*Critic REV-PF8-FINAL-S2 — 段2/3 完成*
