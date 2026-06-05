# KB-DRV-TEST-001 铁律五传播 + DEC 行 — DRAFT（不 commit；critic R20 门）

> 缘起：T/S 报告 raw 入库 2026-06-01，提取/传播逾期至 2026-06-05（C8 偏差）。全队沿用「待 T/S 2–4 周」陈旧口径。
> 原则：历史按写时为真（保留+加注）；活状态翻转（T/S 已到库 KB-DRV-TEST-001，仍缺=额定功率(thermal)/Xmax/条件细节/系统级 R3）。
> **防过度关闭**：Q-②/Q-③（额定功率/阻抗）+ Xmax **未被本报告关闭**——只翻「T/S 参数到库」，不翻「热额定/位移限到库」。

---

# 1. decisions_log 行草案

## 1.1 summary-table 追加行
```
| **KB-DRV-TEST-001 入库提取** | ✅ **T/S 实测报告提取归档（raw 6-01 / 提取 6-05，C8 偏差留痕）；SPLo 82.161 解锁 DEC-S3-DSP-05**（2026-06-05）| 拆机单元送测回报（full_teardown_v2:48），raw MD5 同源入库 2026-06-01，**提取/分级/传播逾期 4 天=C8 偏差**（原件入库及时，提取传播逾期，致全队 4 天陈旧「待 T/S」口径）。LEAP-4 双曲线 19 项 T/S [L1/仪器]（iron-rule-7 三方核：dsp+lead 逐项一致，critic R20 第三方读待；单位前缀 µ/m 三方专核）：Revc7.600/Fs235.907/BL2.030/Qts1.463/SPLo82.161 等。**冲突**：SPLo 82.161 [L1] vs 铭牌 88 [L4] ~5.8dB（铁律四）→ **DEC-S3-DSP-05 SPL 重做解锁（BL/Re/Fs/Qts 到齐），方向预判更低（<88<旧117），登记 CTO 排期，本任务不重做**。Re：LEAP 7.600 vs DC 7.4 双轨一致 [L1]（取代估算 7.0）。**未关**：额定功率(thermal Q-②)/Xmax(截图无)/SPL 条件/系统级 R3。详见 KB-DRV-TEST-001_extracted.md |
```

## 1.2 详细节
```
### DEC-?-KBDRV-TEST-001：T/S 实测报告入库提取（C8 完成 + 偏差留痕）
- **入库时间线**：raw 入库 2026-06-01（MD5 与 CTO 微信原件同源核，KB-DRV-TEST-001_raw/）；**提取/分级/传播
  2026-06-05**。**C8 偏差**：铁律六要求外部输入 ≤24h 入库——原件入库及时（达标），但**提取传播逾期 4 天**，期间
  全队（含 lead 近期文档）沿用「待 T/S 2–4 周」陈旧口径。留痕，未致不可逆损（无基于陈旧口径的 LOCKED 决策）。
- **数据 [L1/仪器]**：LEAP-4 双曲线 Delta Mass 19 项（KB-DRV-TEST-001_extracted §1）；SPL vs Freq 形状（§2）。
  iron-rule-7 三方核：dsp 独立提取 + lead 独立读**逐项一致**；critic R20 第三方独立读待；单位前缀（Mmd/Mms µ/m、
  Vas）三方专核（数字逐位一致，前缀待定，仅影响派生计算非冲突结论）。
- **冲突/解锁**（extracted §3）：
  (a) SPLo 82.161[L1] vs 铭牌 88[L4] ~5.8dB 冲突（铁律四）→ **DEC-S3-DSP-05 UNLOCKED**（BL2.030/Revc7.600/
      Fs235.907/Qts1.463 到齐）；SPL 重做方向预判 **<88<旧117dB**；**登记工作项，CTO 排期（声学/硬件线），本任务不重做**。
  (b) Re：LEAP Revc 7.600 与 DC 7.4[L1] 双轨一致 → Re≈7.5 坐实，取代 full_teardown_v2:49 估算 7.0。
  (c) 限幅阈值：T/S 解锁电压-位移电声基础（BL/Cms/Mms/Fs/Re）；**绝对阈值仍缺 Xmax(截图无)+额定功率(Q-②)** →
      DEC-S5-EQ-O1-01 限幅**结构不变**，**绝对阈值未关**。
  (d) EQ band：driver-level 形状（100-300 ripple + 4.7-5k breakup 峰 ~102dB）≈ O1 2-3 biquad 量级[L2-preview]；
      **system-level band 终定仍待 R3**（单驱动≠16元阵+箱体+波束系统响应）。
- **未关闭（防过度关闭）**：额定功率 thermal Q-②[L4 vendor]/Xmax/SPL 测量条件/系统级 R3 — 均**不由本报告关**。
- **状态**：C8 提取完成；T/S [L1] 入档；DEC-S3-DSP-05 解锁登记；铁律五传播见 KB-DRV-TEST-001_PROPAGATION §2。
```

---

# 2. 铁律五全库传播（LIVE 翻 / HISTORICAL 加注）

> 翻转活状态口径 = **「T/S 已到库 KB-DRV-TEST-001（raw 6-01/提取 6-05）；仍缺=额定功率(thermal)/Xmax/SPL条件/系统级R3」**。
> 不翻：①历史里程碑/写时记录 ②Q-②/Q-③ 热额定（未关）。SPL 117dB 占位「待 T/S」翻为「T/S 已到，SPL 重做解锁待排期」。

## 2.1 LIVE — 必须翻（change blocks）

### LIVE-1：`knowledge_base/competitor/full_teardown_v2.md:48-49`（T/S 送测中 / Re 估算 → 已到库）
old(:48):
```
| **T/S 参数（精确值）** | 拆机单元送测中，预计 2–4 周回报 | 专业测量中 |
```
new:
```
| **T/S 参数（精确值）** | ✅ **已回报入库 KB-DRV-TEST-001**（raw 6-01/提取 6-05）：LEAP-4 双曲线 19 项 [L1/仪器]，Revc7.600/Fs235.907/BL2.030/Qts1.463/SPLo82.161 等（全表见 KB-DRV-TEST-001_extracted）| 送测回报，iron-rule-7 三方核 |
```
old(:49):
```
| **Re（估算）** | ≈ 7.0Ω | **[估算]**，待 T/S 测量更新 |
```
new:
```
| **Re** | **7.600Ω**（LEAP Revc）/ 7.4Ω（DC 万用表）双轨 | **[L1/仪器+实测]**（取代旧估算 7.0；KB-DRV-TEST-001 §3b） |
```
（:45 铭牌 88dB[L4] 行**保留**，加注 `〔实测 SPLo 82.161dB[L1]，差~5.8dB，DEC-S3-DSP-05 解锁，KB-DRV-TEST-001 §3a〕`。
 :54「[估算]注」=写时口径，HISTORICAL 加注「T/S 已到库 2026-06-05」。）

### LIVE-2：`sprint3_status.md`（多处「待 T/S 实测」活状态）
:43 SPL 预测行 / :51 datasheet 收集行（「T/S 参数已送测，预计 2–4 周回报」）/ :87 R3 / :109「等待 T/S 回报」 →
顶部加活状态指针（正文写时保留）：
```
> **状态更新 2026-06-05（KB-DRV-TEST-001）**：T/S 实测报告已到库（raw 6-01/提取 6-05），19 项 [L1/仪器]；
>   SPL 预测重做**解锁**（DEC-S3-DSP-05，BL/Re/Fs/Qts 到齐，方向预判 <88<117dB，待 CTO 排期，未做）；
>   **仍缺**=额定功率(thermal)/Xmax/SPL测量条件/系统级 R3 消声室。以下「待 T/S」为写时口径，存史。
```

### LIVE-3：`knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md:20,27,31`（仍等 T/S）
:20「Q-② 额定功率…仍等 T/S」**保留**（额定功率确实未关）但加注：`〔T/S 参数报告已到库 KB-DRV-TEST-001
2026-06-05，但**额定功率(thermal)无**，Q-② 仍 vendor-pending〕`。
:27 红线「不解锁 SPL 重做（DEC-S3-DSP-05 维持，仍需 BL/Re/Fs/Qts+T/S）」→ 翻：
```
> ⚠️ **措辞红线（2026-06-05 更新）**：8Ω/10W/额定功率 = [L4/标称]，**额定功率(thermal)仍未到**；但 **BL/Re/Fs/Qts
>   已由 T/S 报告 KB-DRV-TEST-001 [L1] 到齐 → DEC-S3-DSP-05 SPL 重做已解锁**（待 CTO 排期，本轮未做；方向 <88<117dB）。
>   15Ω 直流/7.4Ω/盆口/后腔无吸音 = [L1]。Xmax 仍缺（限幅绝对阈值待）。
```
:31「仍 pending：Q-②/Q-③(额定功率/阻抗，等 T/S)」→ 加注：`〔T/S 参数到库，但额定功率(thermal) Q-② 无，仍 pending；
Q-③ 阻抗 Re≈7.5 双轨 [L1] 部分坐实，标称额定阻抗口径仍 vendor〕`。

### LIVE-4：`knowledge_base/hardware_input/定向音柱AI数据_extracted.md:78`（88dB 不解锁 SPL）
old:
```
> ⚠️ 注：喇叭灵敏度 88dB...88dB [L4] **不解锁** SPL 重做（重做需 BL/Re/Fs/Qts 电声模型，本文档未给）。
```
加注（正文保留，因写时该文档确实未给 T/S）：
```
〔2026-06-05 更新：T/S 报告 KB-DRV-TEST-001 已到库，BL2.030/Re7.6/Fs236/Qts1.463 [L1] 到齐 → SPL 重做**已解锁**
  （DEC-S3-DSP-05）；实测 SPLo 82.161dB < 铭牌 88 < 旧占位 117，方向预判更低，待 CTO 排期。本注为写时口径〕
```

### LIVE-5：sprint5 线（V1_NARROWING follow-up / COMPUTE_LINE_CLOSURE remaining-open / NEXT_SESSION / EQ_PRD / H2 WO）
- `sprint5/COMPUTE_LINE_CLOSURE_LANDING.md` §4 remaining-open「R3 消声室（X+EQ band+efficacy），待 T/S 2-4 周」→
  顶注或该行加注：`〔T/S 参数已到库 KB-DRV-TEST-001 2026-06-05[L1]；R3 系统级（X dB/EQ band 终定/efficacy）仍待消声室；
  driver-level SPL 形状已可见（KB-DRV-TEST-001 §3d）；SPL 重做解锁待排期〕`。
- `sprint5/H2_WORKORDER.md` / `sprint5/H1_*`：若含「待 T/S」→ 同款加注（H1/H2 主要是算力线，T/S 关联弱；扫到即注）。
- `EQ_PRD_DECISION_MATERIAL.md`（:44/:45 限幅阈值待 U3/T-S、band 数待 R3）→ 加注：`〔T/S 到库 KB-DRV-TEST-001：
  BL/Cms/Mms/Fs/Re [L1] 解锁电压-位移建模；但 Xmax(截图无)+额定功率(Q-②)仍缺→限幅绝对阈值未关；EQ band system-level
  仍待 R3。DEC-S5-EQ-O1-01 限幅结构不变〕`。

### LIVE-6：`sprint2/docs/prd_update.md:168`（空场最大声压级 待 T/S+实测）
old 第 3 cell「待 T/S 参数 + 实测…喇叭 T/S 送测 2–4 周 + 消声室」→ 翻：
```
| **空场最大声压级** | ≤ 75dB(A)（空场） | **T/S 已到库 KB-DRV-TEST-001 [L1]（SPLo 82.161dB，DEC-S3-DSP-05 SPL 重做解锁，待排期）；绝对 SPL 仍待 SPL 重做 + 系统级消声室 + 额定功率/Xmax** | T/S 已到；消声室空间扫描 + SPL 重做 |
```

## 2.2 HISTORICAL — 逐字保留 + 加注
| 站点 | 处理 |
|---|---|
| decisions_log:393/693 DEC-S3-DSP-05 | 逐字保留；加注 `〔BL/Re/Fs/Qts 已由 KB-DRV-TEST-001 [L1] 到齐，SPL 重做解锁 2026-06-05，待排期；实测 SPLo 82.161<88<117〕` |
| decisions_log:730 R3 行（SPL 降级待 T/S+消声室） | 加注 `〔T/S 到库 2026-06-05；SPL 重做解锁；系统级仍待消声室〕` |
| sprint3/audit/PF_atlas/NEXT_SESSION/blindspot_triage/PF9（PF-3 SPL 占位待 T/S） | 历史规划快照，逐字保留；可选加注「T/S 到库 2026-06-05，SPL 重做解锁待排期」 |
| sprint3/acoustic/pf8/* + acoustic/critic memory（离轴指向性待 T/S/消声室） | **离轴指向性图 T/S 报告并未给**（LEAP/LMS 是正轴向 + T/S 参数，无离轴方向图）→ 该「待」**部分仍真**（离轴仍待消声室离轴扫描）；加注 `〔T/S 参数到库 KB-DRV-TEST-001；但离轴指向性图未含，仍待消声室离轴〕`——**不过度翻** |
| SPL_anechoic_measurement_archived.md:13 / SPRINT3_DESKTOP_CLOSURE | 历史；加注 T/S 到库 |
| critic skill / POLICY 制度文本 | 不涉，无须改 |

## 2.3 grep 分类原则（R7 纪律）
- LIVE「待 T/S 实测/T/S 送测 2-4 周」当前状态陈述 → 翻「T/S 到库 KB-DRV-TEST-001（仍缺 thermal/Xmax/条件/系统级R3）」。
- HISTORICAL 里程碑/规划快照/写时记录 → 逐字 + 加注。
- **离轴指向性「待 T/S」= 部分仍真**（T/S 报告无离轴图）→ 翻为「待消声室离轴」，不假关。
- **额定功率/Xmax「待 T/S/厂家」= 仍真**（本报告无）→ 不翻，明示 Q-② 仍 pending。

---

# 3. 无法核实 / 待第三方
- 单位前缀（Mmd/Mms µ vs m；Vas Gal）：截图判读，三方核（critic R20 第三方读）。
- SPL 绝对电平：测量条件未标，绝对 dB 待条件确认（形状 [L1]，绝对 [L2-条件未定]）。
- SPL 重做、系统级 R3、额定功率、Xmax：均不由本报告关，登记/排期。
- decisions_log/各文档精确行号随提交漂移；锚字符串定位，lead apply 复核。
```
