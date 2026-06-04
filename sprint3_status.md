> **状态更新 2026-06-04：R14 已 CLOSED（DEC-S4-R14-RULING-01），>=10x 判据已退役→实时下限+余量（DEC-S4-CRITERION-01），C9 已 RELEASED 附诚实分母（DEC-S4-C9-RELEASE-01）。本文以下为写时口径，存史。**

# Sprint 3 状态快照

**更新时间**：2026-05-27（项目文档专家 Agent 更新，Sprint 3 Phase 1-2 完成）
**前版本**：2026-05-26 晚（Sprint 3 有条件 GO，等待拆机）
**维护**：Team Lead（Project Manager）/ 项目文档专家 Agent
**下次接续**：读本文件 + CLAUDE.md 末尾即可接上

---

## 当前节点

**Sprint 3 Phase 1-2 完成。** 声学/DSP/硬件/Critic 全部走完，硬件 BLOCKER F-X01 已闭环。等待人工决策进入 Phase 3（EZKIT 采购到位 + 拆机 6 项未知量确认）。

- **Sprint 2**：✅ 完成（6-agent + 2 轮 Critic，Gate 1 PASSED / Gate 2 CLOSED）
- **Sprint 3 Phase 1**：✅ 声学仿真（sweep_d55）+ DSP 8ch 算法链重设计
- **Sprint 3 Phase 2**：✅ 硬件（转接板 v2 + 自研 BOM v2）+ Critic 全领域评审（REV-S3-CRITIC-001）
  - 声学：**PASSED_WITH_MINOR**（F-AC01 SPL 降级 + F-AC03 4kHz 模型失效标注）
  - DSP：**PASSED_WITH_MINOR**（F-DSP04 broadside 裁定 + F-DSP06 d=30 残留清除）
  - 硬件：FAILED → **BLOCKER F-X01 已闭环**（DAC 改 8ch ADAU1962A / TDM 统一 8-slot/12.288MHz）→ v2 通过

### 新阵列基准（拆机真值，替代 Sprint 2 反推估算）

| 参数 | Sprint 2 反推估算 | Sprint 3 拆机真值 |
|------|----------------|----------------|
| 阵元数 N | ≈ 20 | **16** |
| 阵元间距 d | ≈ 35mm | **55mm** |
| 声学孔径 L | ≈ 665mm | **825mm** |
| 驱动通道数 | 16（独立，假设）| **8（A/B 对称串联）** |

### 关键结论（Sprint 3 Phase 1-2）

| 指标 | 结论 | 置信度 |
|------|------|--------|
| 算力裕量 | **33×**（8ch，45.7 MMAC/s；P0-2 树形 C 实算纠正纸面 30.56/49×）| 桌面算法学口径，待 EZKIT cycle 实测 |
| 端到端延迟 | **12.53ms**（scipy 解析/仿真，满足 <30ms，与通道数无关；待 EZKIT 实测）| 中（解析值，未上板）|
| BW@2kHz | **14.5°**（满足 Gate 1 ≤30°，余量极大）| 高（vs 竞品 BW≈14.9° [L2/L3 4点插值派生·F-AC-01 已撤回·非 L1 实测]，误差仅 −0.4°）|
| BW@1kHz | **29.3°**（vs 竞品 BW≈16.0° [L2/L3 4点插值派生·F-AC-01 已撤回·非 L1 实测]，差 13.3°，1kHz 超指向性评估仍有必要）| 中 |
| 栅瓣（500Hz–5kHz）| **安全**（d=55mm，d/λ < 1.0，broadside 判据）| 高 |
| 栅瓣进入可见区 | **≥ 6.2kHz**（6236Hz 严格判据；6.24kHz 起峰 0dB，泄漏 78–89%）→ 强指向上限降级 6k/5k（R6）| 高 |
| broadside-only 约束 | **仅 0° 波束，无法电子偏转**（A/B 串联物理约束）| 确定 |
| SPL 预测 | ≈117dB **[理论上限，低置信度，不可对外]**（Critic F-AC01 降级）| 低（待 T/S 实测）|

---

## 已批准的并行推进项（状态更新）

### ① 自研主线
- ✅ **EZKIT 采购可立即下单**（EV-21569-EZKIT，海外周期长，不浪费；R1 本就需要）
- ✅ **喇叭单元 datasheet 收集并行启动**（索灵敏度/BL/Re/Qts/Fs + 幅相一致性 + 样品，≥3 家；**T/S 参数已送测，预计 2–4 周回报**）
- ✅ **Sprint 3 算法链**：DSP 8ch 算法链（broadside-only，N=8 对称对，D-C 权重适配）已完成设计（待 EZKIT 实物验证 R1）

### ② 快速验证线
- ✅ **第一动作 = 拆机逆向 + 6 项未知量确认**（零采购、低成本、风险前置）
- 工单：`sprint2/docs/sprint3_teardown_workorder.md`（WO-S3-001）
- **Sprint 3 Phase 1-2 已在"N=16/d=55"基础上完成全部仿真与设计**；U1/U4 等精确时序尚待逻辑分析仪确认

---

## 暂未批准（闸门锁定）
- ⏸ **转接板设计 PO**：必须等《6 项未知量拆机确认报告》签署后才发（U1/U2/U3/U4/U5/U6 全确认）
- ⏸ **Codec / 功放 / 电源 生产料采购**：等自研 PCB v0.1 冻结

---

## 遗留 [待核实] 项（转接板 PO 闸门）

| # | 未知量 | 怎么确认 | 对转接板的影响 |
|---|--------|---------|--------------|
| **U1** | 主控↔功放接口（模拟/数字）| 逻辑分析仪/示波器看互连排线 | 决定转接板是否需要 DAC（情形①/②）|
| **U2** | 真实 N / d（已初步确认 16/55，须正式签署）| 物理点数 + 游标卡尺 | 算法几何重定向（已按 16/55 设计，正式报告待签）|
| **U3** | 功放限幅阈值 / 喇叭阻抗精确值 | 万用表 + datasheet | 衰减网络精确参数 + 限幅保护钳位 |
| **U4** | TDM 精确时序（BCLK/FSYNC/slot/电平/采样率）| 逻辑分析仪抓 | SPORT 最终配置；[待核实 ADAU1962A TDM 8-slot 支持]|
| **U5** | 功放板是否含 DSP | 读全板 IC 丝印 | 信号注入点 |
| **U6** | 供电/地结构 | 万用表测电源轨 + 目视追地 | 转接板电源隔离方案 |
| **—** | ADAU1962A 通道数（8 vs 12）+ 8-slot TDM 支持 | 查 ADI 官方 datasheet | DAC 选型最终确认 |
| **—** | ADAU1962A 单端满幅输出电压 | datasheet | 衰减网络 R1/R2 精确参数 |
| **—** | 21569 PLL 25MHz → 12.288MHz MCLK | CCES + EZKIT 验证 | 时钟方案落地 |

---

## 关键风险与遗留（Sprint 3 继续闭环）

- **R1（P0，大幅前进）**：树形 C **已落地**（P0-2，`sprint3/dsp/tree_filterbank.c`，桌面重建 SNR 182dB）；算力裕量经实算纠正为 **33×(8ch)/17×(16ch)**（纸面 49× 偏乐观、漏算分析侧 interp2）；仍待 EZKIT cycle 实测确认 ≥10×（见 DEC-S3-P0-01）
- ~~R2~~：已关闭（延迟规格放宽 <30ms，端到端 12.53ms 系 scipy 解析/仿真、非硬件实测，待 EZKIT 实测）
- **R3**：绝对 SPL 盲区（竞品 0° 106–111dB；SPL 预测 117dB 已降级为"理论上限/低置信度"，待 T/S 实测 + 消声室校准）
- ~~R4~~ **CLOSED（MOOT）**：原"d=30mm 重算 BW@2k"前提已作废——基线统一为 **d=55mm[L1拆机实测]**（DEC-S3-GEOM-01）。d=55 仿真 BW@2k=14.5°≤30° 已满足（大余量），BW 验证职责并入 R5。
- **R5（主路线唯一 BW 风险）**：d=55mm 主路线唯一遗留 BW 风险——BW@1kHz=29.3°（vs 竞品 BW≈16.0° [L2/L3 4点插值派生·F-AC-01 已撤回·非 L1 实测]，差 13.3°），1kHz 温和超指向（ε=0.01）4 项评估（叠加延迟/±2dB±21°产线可达性/温漂−10~+40°C/标定成本）+ 消声室 BW@2k 实测复核。
- **R6（新增，栅瓣 6.2–8kHz）**：d=55mm 在 **6.2–8kHz 出现栅瓣**[L1/几何]——半波长判据 3118Hz、严格判据(broadside,d=λ) 6236Hz，6.24kHz 起栅瓣峰 0dB（与主瓣等高）、带外泄漏 78–89%[L2 仿真]。应对：强指向规格上限由 8kHz 降级为 **6kHz(对内)/5kHz(对外保守)**（方向1，CTO 采纳）；500Hz–5kHz 安全。须消声室实测验证降级规格边界。
- **R7（新增，PRD 边界）**：PRD 强指向频段上限须从 8kHz 修订为 6kHz(对内)/5kHz(对外)，并写入产品规格书；下游营销/对外文案不得宣称 8kHz 强指向（受 R6 栅瓣限制）。[PRD 修订归口 PM，本 Agent 不触碰 decisions_log/PRD 正文]
- **broadside-only（R-S3-DSP-03，已裁定）**：场景可接受（博物馆/车站/商场固定安装）；须 CTO 确认"产品不需要电子偏转"以正式关闭；若未来需偏转须改 16ch 独立驱动硬件（不可算法解决）

---

## 法律红线（快速验证线，DEC-S3-003 确认）

竞品壳改装样机**禁止任何对外场合**（客户演示/展会/照片视频/含外部访客权限的内部场合）；拆机记录在案、仅研发内部参考；改装记录留档可追溯；不复制竞品 PCB/外壳；不复用竞品专有 DSP 固件；不转售竞品硬件。

向市场采购同型号公开器件（ACM3128A/ADSP-21569/ADAU 系列）按公开 datasheet 操作，合法；自研算法/PCB/电源，合法。完整边界见 DEC-S3-003 及 `knowledge_base/competitor/full_teardown_v2.md`。

---

## 下次启动动作（人工触发）

1. **等待**：硬件团队《6 项未知量拆机确认报告》正式签署（U1~U6 全确认）
2. **决策**：签署后评估转接板可行性（情形①模拟 vs 情形②数字）、决定是否发转接板 PO
3. **并行**：EZKIT 到货后启动 R1 算力实测（C 代码移植 + CCES MCPS 测量）
4. **等待**：T/S 送测报告回报（2–4 周），更新 SPL 预测与 R3 评估
5. **CTO 确认**：broadside-only 可接受（关闭 R-S3-DSP-03），写入产品规格书

**当前预计自动算力消耗：0**（等待人工输入，零自动推进）

---

## 相关文档索引

| 文档 | 路径 | 说明 |
|------|------|------|
| 决策日志（含 DEC-S3-003）| `sprint2/docs/decisions_log.md`（v1.3）| DEC-S2-012/013/014 + DEC-S3-001/002/003 |
| PRD（含 Sprint 3 硬件基线）| `sprint2/docs/prd_update.md`（v2.2）| §7 Sprint 3 硬件基线新增 |
| 竞品技术画像 | `knowledge_base/competitor/full_teardown_v2.md` | 完整拆机归档（KB-COMP-001）|
| 规格变更 | `sprint2/docs/spec_change_latency.md` | 延迟 <5ms→<30ms |
| 拆机工单 | `sprint2/docs/sprint3_teardown_workorder.md`（WO-S3-001）| 6 项未知量 |
| 采购/启动 | `sprint2/docs/sprint3_procurement_kickoff.md` | — |
| 改造评估 | `sprint2/docs/sprint3_retrofit_assessment.md` | — |
| 声学仿真（d=55）| `sprint3/acoustic/sweep_d55_report.md` | Sprint 3 AC-WP01 |
| DSP 8ch 算法链 | `sprint3/dsp/dsp_8ch_report.md` | Sprint 3 DSP-WP01 |
| 转接板（v2）| `sprint3/hardware/transition_board_design.md` | F-X01 闭环 |
| 自研 BOM（v2）| `sprint3/hardware/selfdev_bom.md` | F-X01 闭环 |
| Critic 评审 | `sprint3/critic/critic_review_s3.md` | REV-S3-CRITIC-001 |
| Sprint 2 总报告 | `sprint2/SPRINT2_CTO_REPORT.md` | — |
