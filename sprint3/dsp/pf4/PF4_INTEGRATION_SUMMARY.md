# PF-4 定点化闭环三件套 — 整合汇总（PM → CTO）

**任务**：TASK-PF4（Sub-1/2/3）+ TASK-PF4-RV（Critic 合并评审）
**整合方**：Project Manager Agent
**日期**：2026-05-29
**关联**：simulation_coverage_audit.md v2.0 §5 P1 #4/#6/#7；PF-4（定点化未做）；DEC-S2-002（树形 FIR LOCKED）；POLICY-PROV-001
**阶段**：Sprint 3 卡 PCB 前闸门，桌面零散任务并行推进；本批为 **host 桌面 [L2] 仿真，非 SHARC [L1] 实测**

---

## 0. 结论先行

- **三个子任务全部 PASS_WITH_MINOR**（Critic 独立重算/重编译验证，无 BLOCKER、无 review 层 MAJOR）。
- **PF-4 桌面层面可关闭**：定点化 SNR 损失从"声明<0.5dB[L4]"升级为"桌面可信仿真[L2]"。
- **但揪出一个确定性代码缺陷**（节点① 半带 MAC 无饱和、对抗激励溢出 1.73×）→ 须另开代码修复工单（不阻塞 PF-4 分析关闭）。
- **本批是历次标签最干净的一次**：C1–C5 全过，无低级冒充实测。
- **三个"误导性数字"被拦在源头**（旧脚本假 FAIL、C 程序 316dB 假象、节点①潜伏溢出）——正是 POLICY-PROV-001 要防的 PF 类复发，本次成功拦截。

---

## 1. 逐子任务结论（全 [L2] 桌面，可复现）

| Sub | 内容 | 关键数字 [L2] | 裁决 | PF-4 子项 |
|-----|------|--------------|------|----------|
| **Sub-1** | Q15 系数阻带劣化 | 半带原型真阻带(15k–23.9k)：浮点 73.3 → Q15 **71.3dB**（劣化 +2.0dB）；SB0 coarse 抗混叠 浮点 81.9 → Q15 **77.7dB** ≫55dB；整树重建 PR ~300dB（代数保证，与系数精度无关）| PASS_WITH_MINOR | ✅ 桌面可关闭 |
| **Sub-2** | 定点 vs 浮点 SNR | 纯 Q31 算术截断 SNR **172.8–175.5dB**（≫140dB 门禁）；端到端定点 vs 理想浮点 **74.6–78.7dB**（由 Q15 系数字长主导，非算术缺陷）；相位漂移 **0**（互相关 1.0000）| PASS_WITH_MINOR | ✅ 算术维度桌面可关闭 |
| **Sub-3** | Q46 累加器溢出 | 节点①半带 MAC headroom 16.2bit（int64 安全）但 `>>15→Q31` 回量化 **1.731×满量程→溢出**；节点②8ch 求和 0.9998×**安全** | PASS_WITH_MINOR | ✅ 桌面可关闭（节点①缺陷转修复工单）|

---

## 2. Critic 独立验证（D3+ / D4+ / 三发现）

### D3+ —— 现行 LOCKED 系数集裁定
- **现行 LOCKED = 63 抽头半带原型**（树形路径，`tree_filterbank.c/h` + `tfb_set_coeffs` 注入）。
- 两个 `fir_coeffs.h`（`sprint2/dsp/` 与 `cces_template/src/`）经 diff **逐字节一致**，均为 437 抽头、互为副本（5/26 与 5/28 拷贝），同属**已被树形取代的历史核**，无系数身份分裂。
- → Sub-1 主打对象指向正确（半带原型），无 POLICY 数字身份证混淆。

### D4+ —— 跨 Sub Q 格式一致性
- **自洽**：Q15×Q31→Q46→>>15→Q31 数学自洽；Sub-2（节点①半带 MAC）与 Sub-3 节点②（beamformer 8ch 求和）是同一 Q 约定的两个应用点，互补不重叠。
- **无版本漂移**：三 sub 同引 `tree_filterbank.h:29` Q 锁 + `TFB_HB_TAPS=63`。

### 三个 teammate 发现 —— Critic 独立裁定（全部 CONFIRMED）
| 发现 | Critic 独立复算 | 裁定 |
|------|----------------|------|
| Sub-1 旧脚本假 FAIL | freqz：H@12k=−6.02dB，首达 −40dB 于 13261Hz → 13kHz 确在过渡带；真阻带(15k) Q15=71.3dB | ✅ 成立 |
| Sub-2 316dB 是 PR 抵消假象 | 独立编译 C（316.4dB, err 3.9e-16）+ numpy（子带 74.6–78.7 / 算术 172.8–175.5）+ 自写独立整数实现（SB0=74.9）三路吻合 | ✅ 成立 |
| Sub-3 节点①溢出 1.73× | 独立算 Σ\|h_q15\|/32768=**1.7309>1**；源码 grep 确认 `return (int32_t)(acc>>15)` 无任何饱和 | ✅ 成立 |

---

## 3. PF-4 关闭判定（CTO 提醒 #3：可关闭 vs 仍需 EZKIT）

| PF-4 子项 | 桌面 [L2] 可关闭 | 仍需 EZKIT [L1] 才能最终关闭 |
|-----------|:---:|---|
| Sub-1 Q15 阻带满足声学规格 | ✅ 是 | 上板定点 MAC 舍入/抽取相位/流水线差异（估 ±1–2dB），属上板确认 |
| Sub-2 定点算术损失（PF-4 本意）| ✅ 是（Q31 算术 ≥172dB）| SHARC 定点逐 bit 真值（含流水线/寄存器宽度/cache/中断/取模开销）属 **PF-5/EZKIT** |
| Sub-3 累加器溢出风险量化 | ✅ 是（节点②证明安全；节点①风险已量化）| 节点①实际触发率上板用满量程方波/多音/真实素材校准 headroom |

> **一句话**：PF-4「定点化未做」**桌面分析维度可关闭**——损失已从 L4 声明升级为 L2 可信仿真。**最终关闭仍需 EZKIT [L1]**（SHARC 定点真值 = PF-5，本任务不声称、未上板）。

---

## 4. 须 CTO 决策 / 知悉

### 🚨 4.1 确定性代码缺陷（须开修复工单）
- **节点① 半带 MAC `acc>>15→Q31` 无饱和**（`tree_filterbank.c:52`）：Σ|h|=1.73>1，对抗性满量程激励下回量化达 1.73× Q31 满量程 → 整型环绕/符号翻转（爆音）。
- 复合风险：下游 `hb_interp2` 再 ×2（最坏 3.46×）、合成端 int32 相加均无中间保护，直到 `beamformer.c` Q23 钳位才饱和（太晚）。
- **现有 `tree_verify.c` 用 DC=1 单位增益激励不触发此溢出** → 属"对抗激励才暴露"的潜伏点（这也是为何此前 182/316dB 验证未发现）。
- **建议整改**：节点① 加中间饱和 + `hb_interp2` ×2 补饱和 + 系统级输入预留 −4.8dB（1/1.73）headroom。**Critic 评为代码层 MAJOR**，但不阻塞 PF-4 分析关闭。

### 4.2 三个 MINOR（PM 默认不打回，记账）
1. Sub-1：旧脚本 `q15_stopband_sim.py` 的"FAIL 27.7dB"头条未标废止 → 建议加废止 banner（防误引）。
2. Sub-2：`fixed_vs_float_compare.c` 程序头条仍打印"316dB PASS"假象（正文已纠正）→ 建议头条改打子带层数字。
3. Sub-3：关闭措辞应区分"缺陷已确认（确定性）"vs"触发率待 L1"。
- ⚠️ MINOR 1/2 是**误导性数字残留在已提交文件里**——按 POLICY-PROV-001 防 PF 复发精神，建议做轻量 banner 清理（PM 可代办，不占 teammate）。

### 4.3 建议的 decisions_log 回填（待 CTO 批准后写入）
- PF-4 状态：`simulation_coverage_audit` ④定点化 从 ❌/❓部分 → **桌面 [L2] 可关闭**（SHARC [L1] 仍待 EZKIT）。
- 新增代码修复工单项：节点① 饱和缺陷（DSP 域，PCB/上板前修）。

---

## 5. 产物清单（均在 `sprint3/dsp/pf4/`）

| 文件 | 内容 |
|------|------|
| `sub1_q15_stopband.md` + `sub1_q15_stopband_v2.py` | Q15 阻带劣化（纠正旧脚本带边错误）|
| `sub2_fixed_vs_float.md` + `fixed_vs_float_compare.c` + `xcheck_subband.py` | 定点 vs 浮点（子带层正确口径 + C/numpy 双实现互验）|
| `sub3_q46_overflow.md` | Q46 累加器溢出（节点①缺陷量化）|
| `critic_review_pf4.md` | Critic 合并评审（C1-C5 + D3+/D4+ + 三发现独立复算）|
| `PF4_INTEGRATION_SUMMARY.md` | 本文件 |

---

*PM 整合，2026-05-29。全为 host 桌面 [L2] 仿真，SHARC [L1] 真值待 PF-5/EZKIT。三 sub PASS_WITH_MINOR / 无 BLOCKER；节点①代码缺陷转修复工单。*
