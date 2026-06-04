# 可控音柱算力余量扫描报告（DRAFT — 待独立 critic 门，未呈 CTO 正式版）

> 生成: 2026-06-04, workflow steering-headroom-scan (31 agents, 5 维侦察 + 逐发现对抗证伪; 幸存 findings 见附录).
> 时点注记: 扫描启动时 R14 裁定 PENDING; 现 CTO 已三连裁定(R14 CLOSED / 判据复议 / C9 松绑附诚实分母).
> 报告内 FLAG-C 'R14 PENDING' 表述系扫描时点快照; 隔离原则不变: 本线估算 [L4/待验证] 不进选型基准.
> v1 路线注记 (2026-06-04): CTO 已裁 v1=聚焦/分区(DEC-S5-STEER-V1-01); 角度偏转转独立项(16ch 叉 ROI 待评). 优化排序 HW-1(IIR EQ)最高优先+item-3 PRD 同推(DEC-S5-OPT-ORDER-01). 口径采纳: 49x/340x 双作废(同源 1cyc/MAC 理想记账); 聚焦增量 86-144 MCPS[L4](30-50 cyc/MAC 板证包络), 聚焦后算法侧 margin 2.04-2.31x. 本报告 [L4/待验证] 估算不进选型基准, 须连体 §8 未计入清单呈现(DEC-S4-C9-RELEASE-01).

〔critic R8 修正注：synthesizer 原工作注曾以 ~21.7 MCPS 为 FRAME=256 下界——该值把 MAC 项也 /4 摊薄，正是 workflow 内部 verifier 已纠正过的算错（21.7 撤回）。verifier 下界 86.9 MCPS 才是正确 floor。本报告正文已按 verifier-correct 区间呈现：FRAME=256: 86.9–341.6 MCPS（margin 2.93x–11.51x）；FRAME=128: 173.7–343.6 MCPS（2.91x–5.76x）。此事例证 synthesizer 可能撤销自家 verifier 的纠正——独立 critic 命门不可省。〕
〔修正台账 #2（critic R9，缘起 CTO 质询）：STEER-2 原「~49x 纯核余量」退役——49x=1500/30.56 系桌面理想 1cyc/MAC 的**整路径**余量（dsp_8ch_report.md:64-68），被误挂到聚焦增量头上（类别错误），且同口径已被板上推翻（~30-50 cyc/MAC 实测，decisions_log:234/770）。修正后口径：聚焦增量 86–144 MCPS [L4]（板实测包络），margin 2.878x→~2.04x–2.31x，连体 §8 呈现。R9 同时抓住修正稿自身两处偏乐观新错（2.55x 低端算错应 2.31x；3 cyc/MAC 下界无板证）——修数的文档也要过门。〕

---

# 算力余量扫描报告 — 可转向音柱产品线（Steerable Column Speaker）
**SCAN: compute-headroom for steering line | READ-ONLY | 本扫描不裁定任何事，仅为 CTO 决策供事实**
日期 2026-06-04 | 基线 = FIRA build, EZKIT, CCLK=1GHz 实测, FRAME=64@48k => 750 frames/s
所有数字遵守 C9/铁律八：R14 裁定 PENDING CTO 前，FIRA 收益一律 [L4/待验证]，不得入任何选型/流片/承诺基准。

---

## 0. 一句话结论（给 CTO）
本扫描的两条战略闸（STEER-1 16ch 硬件叉 + STEER-3/ORCH-2 SC-S3-GEOM-01 d 重议）**支配整张优化表**：在现锁定基线上，"转向"中的**角度偏转（off-axis tilt）是硬件物理不可达**，不是固件/算力问题。算力优化（ORCH/FRAME/HW 各项）只在**对称兼容子集（broadside 聚焦/分区）**或**CTO 重开 16ch 叉之后**才有意义。因此：**优先级 #1/#2 是两条 CTO 闸，不是任何 cyc/frame 数字。**

---

## 1. RANKED OPTIMIZATION LIST（按余量收益排序）

> 注：排序综合"收益量级 × 是否阻断转向线 × 证据等级"。除两条战略闸外，所有量级均 [L4/待验证]，方向/调用次数为 [L3]，датasheet 能力为 [L2]。**没有一个量级数字经过板测**。

| # | id | 标题 | 收益（含等级） | Effort | 主要风险 | 依赖/交互 |
|---|----|------|---------|--------|---------|----------|
| **S1** | **STEER-1** | 配对 A/B 串联拓扑使 broadside-only 成为**硬件属性**；角度偏转必须 16ch 硬件叉 | **决策性 [L1]**（拆机实测 + DEC-S3-DSP-03 锁定）。非余量项——它**界定**整张表：off-axis 转向在现板上算力优化全部 moot | **L**（Gate-2 级不可逆硬件重设计：DAC 8→16、功放翻倍、转接板重做） | 若有人把"余量 2.878x"读成"转向=固件功能"=类别错误，违背 L1 物理 | 量化 16ch 叉后余量见 STEER-4；触发 STEER-3 d 重议 |
| **S2** | **STEER-3 / ORCH-2** | 转向 PRD **自动触发 SC-S3-GEOM-01 d 重议**（偏转把栅瓣拉进带内，clean 带由 6.2k 跌到 θ=10°→5.3k / θ=30°→4.16k） | **决策性 [L3]**（fc(θ)=c/(d(1+\|sinθ\|))，broadside fc=6236Hz 复现 L1 严格判据） | **L**（CTO 几何重决 + 声学重仿 + N/d/孔径联动改 → 全部算力估值重算） | governance-certain once steered-directivity PRD 存在；恢复带的具体 d 是开放问题 | d 改变 → STEER-4 全部 MCPS 重算；与 STEER-1 同为 CTO 闸 |
| **#1** | **HW-1** | 把 item-3 EQ/限幅链 offload 到 IIR 加速器（最大余量威胁移出核） | 恢复核需求至多 **~290 MCPS**：worst-case 637.45→347.45 MCPS（margin 1.569x→2.878x）；nominal item-3=150 则 2.010x→2.878x **[L4 包络]** | **M**（架构绑定，非代码改；adi_iir SHARC 头本机缺失，需上板 bring-up） | item-3 当前 [L4]，若 PRD 无 EQ（DOC-S4-IO-01 直进直出）则威胁=0 收益=0；IIR 定点 bit-exact 须板验；并发总线仲裁见 HW-2 | 由 HW-2 使能（FIR+IIR 并发）；条件性——仅当 PRD 真有 rich EQ |
| **#2** | **FRAME-1** | FRAME 64→128/256 摊薄每帧固定 orchestration → FIRA 路径 MCPS 严格下降 | 方向 [L3] firm；**量级 [L4/待验证]**。真区间（O-split 未测，critic R8 按 verifier-correct 修正）FRAME=256: **86.9–341.6 MCPS（margin 2.93x–11.51x）**；FRAME=128: 173.7–343.6（2.91x–5.76x）。"≥10x 可达"仅当 orchestration≈95%+ 每通道成本（未测假设，MATLAB 复核 O≈0.95·PERCH 时 10.04x） | **M**（FRAME 是可调参数，但=全套 R14 bit-exact 重门，见 FRAME-4） | EXACT margin 未确认；**仅 FIXED-share 摊薄（2.23%）是 firm**；O-amortization 只会更好但量级未知 | 由 FRAME-2（延迟）/FRAME-3（内存）/FRAME-4（重门成本）共同 gate；ORCH 系列在新 FRAME 上重测 |
| **#3** | **ORCH-1** | 8 个同层通道合并为 **1 个多通道 CreateTask/QueueTask**（72→9 段调用/帧） | 调用次数 72→9 砍掉 63 round-trip+63 spin+63 callback [L3]；**量级 [L4]**：若 orchestration 占段成本 15–25% ⇒ ~50k–110k cyc/frame ⇒ margin **2.878x→~3.2–3.6x** | **M**（重构 8ch 驱动数据流为 level-outer/channel-inner；FIR_MEM_SIZE(8) 本机未定义；须重过 R14 F4 0x2E0D8C6E + F5 8/8） | 批处理可能重排 DMA writeback vs per-segment flush → 重引 cache hazard；**转向部分杀此项**：每通道 steered 系数不同（但 window 分组仍存活） | 与 ORCH-2(任务复用)、ORCH-3(流水线) 交互；与转向动态系数冲突 |
| **#4** | **ORCH-2** | FIRA 任务**一次性创建**（持久任务内存），每帧只 re-queue → 消除每帧 CreateTask+FixedPointEnable | 砍 72 CreateTask + 72 FixedPointEnable/帧 [L3]；**量级纯 [L4 推测]**（无任何测量锚）：若每段 ~1–2k cyc ⇒ ~72k–144k cyc/frame ⇒ margin ~3.3–4.0x | **M**（hoist 到 fira_tree_setup + 静态定点配置；须重过 R14 + buffer 契约重验） | **转向下可能 BLOCK**：动态系数若每帧变，CreateTask 或须重建——除非 adi_fir_SetChannelCoefficientBuffer 可在持久任务上换系数（**G1 gap，本机未验**） | 与 ORCH-1 天然配对；转向兼容性 [L4/待验证] 待闭 G1 |
| **#5** | **ORCH-3** | 用 callback 流水线 / queue-depth>1 替换 busy-spin，使段重叠不串行 | **量级完全 [L4]**：若 spin 占段 30–50% ⇒ 隐藏可省 ~100k–200k cyc/frame ⇒ margin 趋 ~4–6x（乐观上界，per-frame fixed 仅 2.23% 故实际由跨通道重叠主导，**不可与 ORCH-1 相加**） | **L**（真流水线须双缓冲 s_seg_in/s_seg_out3，重引 cache 一致性 hazard；树内数据依赖串行，仅跨通道可重叠） | 最高 bit-exact 回归风险，2.23% 上界 vs 高成本 | **部分重复 ORCH-1 收益**——勿求和；先做 F7 Q3(iii) 单段 CCNT 仪表化测 spin 占比再决定 |
| **#6** | **HW-2** | FIR+IIR 加速器**并发**（datasheet 确认）使 EQ 链与波束链 MAC 并行、均离核 | [L2] 能力确认；**收窄修正**：仅 MAC 计算重叠离核，两链的**核侧 orchestration 仍叠在单核时间线**（占比未测，F7_CLOSING_RECORDS.md:120）；L1 总线仲裁未量化 | **M**（需 HW-1 IIR bring-up + 1 板测并发周期成本） | "并发"是能力非零竞争保证；并发净成本板测 TBD | 使能 HW-1；与 HW-3 共享多通道/队列杠杆 |
| **#7** | **HW-4** | 描述符链 DMA + TRU 链接加速器/SPORT I/O，免核 spin | **量级 [L3]，上界被高估**：item-1(5–30)+item-2(2–15)=~7–45 MCPS，但 cache-invalidate 不可 offload、per-block callback 仍在；spin-idle 重收在裸机 free-run 上≈0（已是 idle），**仅当转向加并发工作填窗才有用** | **M**（orchestration only；驱动级重写 + bit-exact 重验 + 多板测） | TRU 重排 invalidate vs FIRA writeback → 重引 flush-back hazard | 低于 HW-1/HW-2 优先级（item-3 dwarfs item-1/2）；转向加段时才 material |
| **#8** | **ORCH-1(constraints 视角=同一项)** | — 与 #3 同条，constraints 维度复述其 governance-free 性质 | 见 #3 | 见 #3 | 见 #3 | 见 #3 |
| **#9** | **HW-3** | 多通道 CreateTask/通道分组削减 72 次/帧调用开销（与 ORCH-1 同机理，硬件维度） | **grade 修正**：固定份额 10,345 cyc=2.23% 是 [L1] 但**那不是分组能回收的部分**；可回收量在每通道 56,616 里，**[L4/待验证]**，量级 ~single-digit-thousands cyc/frame | **L**（破 [ASSUME-A1] 须 per-task scratch + bit-exact 全重验，多板测） | 2.23% 天花板 vs 高回归风险；建议 deprioritize | 16ch ~线性扩展（无免费摊薄）——转向预算输入 |
| **#10** | **ORCH-4(flush)** | 若驱动 ADI_CACHE_MANAGEMENT 已 invalidate 输出区，删每段 flush_data_buffer | **量级 [L4]，最小项**（~single-digit-thousands cyc/frame）；FIRA_IMPL.md:35/155 称驱动已 invalidate，但 21569 驱动源本机缺失=**UNVERIFIABLE** | **S（验证 catch：删一个看似冗余实则 load-bearing 的 cache op = 静默数据损坏）** | HIGH regret if wrong；**建议：measure first, likely KEEP**，勿投机删 | 与转向正交；G1-class gap |
| **#11** | **STEER-2** | broadside **近场聚焦/分区**是 A/B 兼容的（仅角度 tilt 被阻），可在现 8ch 上做 | **聚焦/分区 = 8ch 分数延迟 FIR（STEER-4 同类，8 distinct ch），静态区延迟更新率≈0**。成本口径修正（CTO 挑出 49x 误用，critic R9 过门）：源 `dsp_8ch_report.md:59-72` 的「2.88 MMAC/s 于 30.56 总、49x」是 **桌面理想 1 cyc/MAC 口径**（49x=1500/30.56=整路径余量，非聚焦 ADD 的余量；同口径已被板上推翻：桌面 33x/17x→板 0.92x，decisions_log:234）。**板上真实 ADD ≈ 2.88 MMAC/s × 30–50 cyc/MAC（板实测包络 decisions_log:234/770）= ~86–144 MCPS [L4 区间]**（理论最优短 FIR 内核或低至 ~3 cyc/MAC≈9 MCPS，但**无项目板测支撑，仅乐观下界**），落在 post-FIRA 8ch 算法 headroom（1000−347.45=**652.5 MCPS [L1-derived]**）的 ~13.2%–22.1%（margin 2.878x→**~2.04x–2.31x**）。**必须与 §8 整系统未计入清单（43–379 MCPS，残余 1.38x–2.56x，DEC-S4-C9-RELEASE-01）连体呈现，不得以 49x 或单独 2.88 示人。** FIRA-offload 聚焦 FIR = [L4 选项]（MAC 移出核但每加一段付 ~6,290 cyc/段 orchestration，F7 g_f7_cyc_1ch_fira/9 [L1-derived]；C9 闸下）。聚焦疗效 [L3/待 acoustic-sim] | **S/M**（固件 only IF PRD=broadside 聚焦/分区；触碰冻结滤波器输入缓冲则须重 bit-exact） | PRD 歧义："steerable" 口语指角度转向（STEER-1 阻）；对称聚焦疗效待声学仿确认 | 现板唯一有余量的"转向-like"能力；强制 PRD 二选一 |

**未单列但已含的项**：HW-6（闲置硬件清单 ASRC/PCG/S/PDIF/SIMD-PEy/crypto，均不可映射，见 EXCLUSIONS）；STEER-4/STEER-5（转向自身算力，见 §3）；ORCH-3/ORCH-4/ORCH-5（constraints 维度=分类与引用项，见 §2 & §5）。

---

## 2. STRATEGIC FLAGS（支配优化表的两条 + governance）

### FLAG-A：8ch 配对拓扑使角度转向成为硬件物理不可达（STEER-1，决策性 [L1]）
- **物理根**：拆机 [L1/硬件实测] A 区元 n 与 B 区元 (17−n) **串联**成 8 路（15Ω 实测），配对 {c,15-c} 物理接收**同一激励**（`定向音柱AI数据_含追问回复_extracted.md:12`；`audio_io_topology.md:32`）。
- **结论**：off-axis tilt 需配对元间**非对称渐进延迟**，串联硬线无法施加 → 阵列因子是纯实偶函数 = 零非对称相位 = 零转向权（`dsp_8ch_report.md:159`；MATLAB 机器精度交叉核 `matlab_verify_m3_superdir_8pair.md:99-101`）。
- **锁定**：DEC-S3-DSP-03（CTO-APPROVED，R-S3-DSP-03 已闭）原文："**未来若重启电子偏转需求，必须改回 16ch 独立驱动硬件，算法无法绕过**"（`decisions_log.md:381`）。
- **决策强制**：转向 = **Gate-2 级不可逆硬件叉**，不是固件任务。16ch 叉后核侧算力**翻倍**（orchestration ~97.8% 每通道）；16ch **core-only** 需求已 = **0.55x**（`F7_MARGIN_MATERIAL.md:112`，1000/1803.35），在加任何转向算力前已不满足实时。

### FLAG-B：转向 PRD 自动触发 SC-S3-GEOM-01 的 d 重议（STEER-3/ORCH-2，决策性 [L3]）
- **机理**：d=55mm 锁定**明文条件于**"PRD 不新增 6-8kHz 强指向硬需求"；偏转把虚区栅瓣扫入可视区，把 clean 带从 broadside 的 6236Hz 单调压低：θ=10°→5314Hz，θ=20°→4647Hz，θ=30°→4158Hz（fc=c/(d(1+\|sinθ\|))，broadside 值复现 L1 严格判据 c/d=6236Hz，`decisions_log.md:455`）。
- **治理**：SC-S3-GEOM-01 原文照录："**任何 PRD 变更涉及 6-8kHz 强指向 → 自动触发 d 重议，无 PM 自治权。永久产品边界**"（`decisions_log.md:457-458`；`CLAUDE.md:204`）。
- **决策强制**：一个想保留偏轴指向性的转向 PRD **几乎必然**跨过此前提 → CTO 几何重决 → N/d/孔径改 → **所有算力估值重算**。caveat：若转向 PRD 严格 ≤5kHz **且偏转角受限（θ≤~14° 保 fc(θ)≥5kHz；θ=30° 时 clean 带已落到 4158Hz）**则不跨闸（critic R8 补精确化；finding 已诚实披露方向）。

### FLAG-C（governance）：本扫描线 OUT of R14/C9 闭合（ORCH-4-constraints）
- R14 数据 COMPLETE 但**裁定 PENDING CTO**（DEC-S4-F7-CLOSE-01，`decisions_log.md:705,748`）。C9/铁律八仍 BIND："C9 管 USE 非 provenance"。
- **本扫描所有 cyc/MCPS/margin 数字一律 [L4/待验证] 探索性，零贡献于 R14 闭合，不得写入 F7_R14_RULING_MATERIAL.md 或任何选型/流片/承诺基准。** 即便复用 2.878x/3.07x 这类 [L1-derived] 数也只能在边界讨论中标注"不入基准"。

---

## 3. STEERING COMPUTE BUDGET [L4]（仅在 16ch 叉之后才适用 off-axis）

**Part A — 转向自身算力（STEER-4，全 [L4/待验证]）**
- 整数样延迟 = buffer index offset ≈ **0 MCPS**。分数延迟 = 短 per-channel FIR。
- 板现实 cyc/MAC = **30–50**（非理想 1–2；F7 板测把 33x 打成 1.32x，`F7_MARGIN_MATERIAL.md:191`），主导不确定性（25x 展宽）。
- 16-tap 分数延迟 FIR：**8ch ≈ 184–307 Mcyc/s**；**16ch ≈ 369–614 Mcyc/s**（8-tap 减半，32-tap 翻倍）。

**vs 可用残余余量**
- 8ch FIRA 基线 margin **2.878x**（=347.45 MCPS 需求）。叠 16-tap@8ch 转向 FIR → margin 趋 **~1.53–1.88x**（修正区间，比 finding 的 1.4–2.1x 更可辩护）。
- 16ch 路径基线本身 [L3 外推] margin 仅 ~1.44–1.73x（**无 FIRA 16ch 板测，纯外推**）；叠 369–614 Mcyc/s 转向 FIR → 趋/破 **1.0x**（post-steer 0.76–1.06x）。
- 全系统残余余量（含 DMA/中断/EQ/控制/WCET）= **1.38x–2.56x [L4]**；rich EQ 链（~250–290 MCPS @30cyc/MAC 板现实）可把 worst case 拉向 ~1.0x。

**Part B — 更新率（STEER-5，[L4]，机理修正）**
- 转向成本是 **orchestration 成本，非 MAC 成本**。静态博物馆/车站分区 → 延迟一次设定，摊销≈0。**修正**：as-built 基线**已**每帧每段 CreateTask（72+24 次），故"连续追踪额外付 re-create"被**高估**——基线本就付；真正开放问题是改延迟是否需任何超出已计 CreateTask 的额外工作（很可能不需，因 Dolph 窗不变、仅相位/延迟变），且 re-create-vs-reload 区分是 **G1/G2 板/工具链 gap**（adi_fir_2156x.h 本机缺失）。

**是否 fit 当前包络？**
- **off-axis 角度转向：在现 8ch 板上 NOT FEASIBLE（硬件物理，FLAG-A）。** 16ch 叉后，core-only 已 0.55x 不满足实时，FIRA-16ch 余量未板测——**必须先板测 16ch FIRA + 测转向 FIR 板成本**才能判 fit。
- **broadside 聚焦/分区（STEER-2）：fit，固件 only（若不碰冻结输入缓冲）**。算力口径修正（critic R9）：原「~49x 纯核 headroom」是桌面理想 MAC（1 cyc/MAC）口径，**不可与板上 L1 并置**（49x=1500/30.56 整路径，已被板上 0.92x 推翻同源）。板上真实聚焦 ADD ≈ **86–144 MCPS [L4]**（2.88 MMAC/s × 30–50 cyc/MAC 板实测包络；~3 cyc/MAC=9 MCPS 仅理论乐观下界无板证），约 post-FIRA 652.5 MCPS [L1-derived] headroom 的 13.2%–22.1%（margin → ~2.04x–2.31x）；**呈现须连体 §8 未计入清单（残余 1.38x–2.56x）**。结论方向（聚焦在现板可负担）不变，但量级降为 [L4 区间]，非 49x。

**承诺前必须先 pin（pin-first 清单）**
1. **PRD 定义**："steerable" = 角度 tilt（→16ch 硬件叉，CTO Gate-2）还是 broadside 聚焦/分区（→固件可达）？（STEER-2 强制二选一）
2. **item-3 EQ/限幅是否存在**（决定 HW-1 收益 0 vs ~290 MCPS）。
3. **板测 56,616 内 orchestration:MAC 拆分**（解锁 ORCH-1/2/3 与 FRAME-1 真量级；F7 Q3 选项 idle tail-read 或单段 CCNT 仪表化）。
4. **G1 闭合**（adi_fir_SetChannelCoefficientBuffer 是否可在持久任务换系数 → 决定 ORCH-2 转向兼容性 + STEER-5 追踪成本）。
5. **若 16ch**：板测 16ch FIRA 真余量（现仅 [L3] 外推 1.44–1.73x）+ 转向 FIR 板 cyc/MAC。
6. **SC-S3-GEOM-01 d 重议**（若 PRD 保留偏轴指向性）。

---

## 4. EXCLUSIONS ROLL-UP（考虑过并排除，每项一行，无静默丢弃）

**REFUTED 发现（驳回，存档）**
- **HW-5**（把 Dolph 权折进 FIR 系数）：**驳回**——冻结核 tree_filterbank.c 是 3 级 dyadic 差分金字塔非单 FIR；`sb3 = in - r1` 用**原始 in**（不过任何系数），折叠给出**精确算术下的错误答案**（sb3=in−w·interp 而非 w·(in−interp)），机理不可建。次要错：误引退役 e2e golden 0x90556BC7（真判据=8 个 per-channel CRC）；1024-word 限未钉到 datasheet 页。

**FRAME 维度排除**
- FRAME=512：精确硬天花板（FIRA_MAXWINDOW=512 guard + r1/a1p/up1[512]），但达到须改**冻结** tree_filterbank.c 数组 → 禁。FRAME=256 是不碰冻结码的实际上限。
- 改 halfband 滤波器/树深（TFB_NUM_LEVELS=3）减 MAC：冻结核，重开 R14，禁。
- FRAME=128/256 单一 MCPS 值：56,616 内 O:MAC 拆分未测，仅 RANGE 可辩护，**未静默取中点**。
- 16ch FRAME-scaling 作主发现：R1 绑 8ch（DEC-S4-R1-8CH-01），16ch 仅参考。
- core-only 路径 FRAME scaling 作 win：无 per-segment QueueTask 可摊（仅 ~0.8% 循环开销），且本就不满足实时。
- 12.53ms 延迟作 L1：是 scipy 解析 [L3]，待 EZKIT [L1]。
- ≥10x vs 修订判据的推荐：CTO 判据政策决定，本扫描仅供"FRAME=256 使 ≥10x 由摊薄可达"事实。
- knowledge_base/standards/ 无额外数值延迟标准（仅一张未解析图）。

**Hardware 维度排除**
- 多核/第二 SHARC+：21569 是单核（datasheet line 1）；SC589（2×SHARC++ARM）是芯片改但 DEC-S1-004 LOCKED 不可逆，CTO 决定不假设。
- SIMD PEy 向量化：核在冻结 tree_filterbank.c，重写须重过 bit-exact 全门，禁。
- ASRC(2×4)：固定同步 48k TDM 直进直出，无需率转换。S/PDIF(2×1)：不在信号链。PCG(2×2)：生成时钟非算力 offload。
- Crypto/PKA：无加密需求。双 CRC 引擎：测试基础设施非产品数据路径（golden_ref 冻结）。FFT/butterfly：波束是时域 dyadic-tree FIR 非 FFT。HADC/link ports/MLB：控制/遥测外设非音频算力。
- 软件 postscale/decimate：设计上留核（R14 80-bit→Q31 + 抽取相位修正，移动重开 R14）。

**Constraints 维度排除**
- FRAME=64 作"锁定决策":排除——仅 harness/build 常量，无 DEC- 锁；改它 governance-heavy（重定义冻结 goldens）但本身非锁定。
- DEC-S2-006 d=30mm：退役（PF-8/DEC-S3-GEOM-01），不得作任何决策基础；仅 d=55mm 活。
- DEC-S2-007 N=16/24：N=16 LOCKED；16-vs-24 是元数余量问题非转向拓扑闸（转向 blocker 是 A/B 串联拓扑非 N）。
- DEC-S2-012 <30ms：非转向 blocker，是吸收 FRAME 增量的 headroom（FRAME 256→5.33ms 群延 ≪30ms）。
- 1kHz 超指向 (R5)/R6 栅瓣降级/R10 FIB：均 broadside 对称权问题，非转向（非对称相位）能力；R6 转向相关性已折入 SC-S3-GEOM-01 自动触发。
- 芯片改 21569→SC589：非转向必需（16ch 叉加 I/O/算力但无证据 21569 单核托不住）；自身独立 Gate-2。
- 冻结核改杠杆（系数预缩放、hb63 重构）：任务硬规则禁，仅在 ORCH-3 标为 governance-heavy 边界防误提。

---

## 5. WHAT STAYS UNVERIFIED（须板测/PRD 决策才能 load-bearing）

| 项 | 当前等级 | 变 load-bearing 所需 |
|---|---|---|
| **所有 ORCH/FRAME/HW cyc·MCPS·margin 量级** | [L4/待验证] | 56,616 内 orchestration:MAC 拆分板测（F7 Q3 idle tail-read 或单段 CCNT 仪表化）——**这一个未测量决定 ORCH-1/2/3 与 FRAME-1 是否值得** |
| ORCH-1 margin ~3.2–3.6x（72→9 之收益量级） | [L4] | ≥1 FIRA 板测 + R14 bit-exact 重过（F4 0x2E0D8C6E + F5 8/8）；FIR_MEM_SIZE(8) 本机未定义须板验 |
| ORCH-2 ~3.3–4.0x（纯推测，无锚） | [L4] | 板测 CreateTask+FixedPointEnable 实际 cyc；**转向兼容性待闭 G1**（adi_fir_SetChannelCoefficientBuffer 在 21569 头是否存在） |
| ORCH-3 spin 占比（~4–6x 上界） | [L4] | 单段 CCNT 仪表化（F7 Q3 iii）——先测 spin 占比再决定流水线重构 |
| ORCH-4 flush 是否冗余 | [L4]/G1-class | 21569 SHARC Legacy 驱动源本机缺失=UNVERIFIABLE；上板 A/B bit-exact 证明驱动自 invalidate 才可删，否则 KEEP |
| FRAME-1 真 MCPS@128/256 | [L4]（方向 [L3]） | 重测 g_f7_cyc_8ch_fira @新 FRAME；"≥10x 可达"须验 O≈95%+ 假设 |
| FRAME-2 12.53ms→新 FRAME e2e | [L3 解析] | EZKIT [L1] 端到端实测；**注**：修正后 FRAME=256 e2e≈20.5ms 会破 PRD 表未更新的 ≤20ms 行（prd_update.md:183），仅 draft DEC-S2-012 的 30ms 容纳 |
| FRAME-3 Block-0 占用 | [L3/PROXY-ldf] | 上板 .map L1 Block-0 占用核查（s_y/.bss 随 FRAME 增，F7 PC=0x1 崩溃先例真实） |
| FRAME-4 重门：goldens/chirp 再生 | [L1 流程] | **修正**：golden_ref.h/chirp_input.h 是 FIRA_IMPL.md:51 红线冻结（"不重生成"），改 FRAME 须先 CTO/critic 解冻 + 板上 per-subband F4/F5 tol=0 重过 + cycle 重测 |
| HW-1 item-3 EQ 是否存在 + ~290 MCPS 包络 | [L4] | PRD 定义 EQ/限幅链；adi_iir SHARC 头本机缺失须 bring-up + 并发 FIR+IIR 周期板测 |
| HW-2 并发净成本（含 L1 仲裁竞争） | [L2 能力] | 板测并发模式 cycle；核侧 orchestration 仍叠单核时间线（拆分未测） |
| HW-3 分组可回收量 | [L4]（10,345 是 [L1] 但非可回收部分） | 分组原型板测；建议 deprioritize vs HW-1 |
| HW-4 TRU 实际回收 | [L3]（上界高估） | 远低于 45 MCPS 上限；仅转向加并发工作填窗才有用 |
| STEER-4 转向 FIR 板成本 | [L4]（cyc/MAC 30–50 是 25x 展宽主因） | FIRA build 板测 |
| STEER-2 近场聚焦疗效 | [L3 解析] | acoustic-sim teammate 确认（对称权 broadside-only 是标准阵理论） |
| STEER-3 偏轴 usable-directivity-vs-栅瓣真带边 | [L3]（fc 解析，broadside 锚 L1） | acoustic-sim [L2] 设真带边；恢复带的具体 d 是开放 |
| 16ch FIRA 真余量（1.44–1.73x） | [L3 外推，无板测] | 16ch FIRA 板测（现仅外推，core-only 16ch=0.55x 已 [L3-arith-on-L1]） |

---

*本扫描不裁定任何事。两条 CTO 闸（STEER-1 16ch 叉 + STEER-3/ORCH-2 d 重议）支配全表，须先于任何算力优化由 CTO 决策。所有量级数字 [L4/待验证]，零入 R14 闭合与任何选型/承诺基准（C9/铁律八）。*

---

**相关文件路径**（绝对路径，供 team lead / critic gate）
- 基线证据：`/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md`、`.../F7_CLOSING_RECORDS.md`、`.../F7_MARGIN_MATERIAL.md`、`.../F5_F7_PLAN.md`、`.../FIRA_IMPL.md`
- orchestration 源：`/home/it1234/.../sprint4/dsp/fira/fira_tree.c`、`.../fira_regression.c`
- FRAME/golden：`/home/it1234/.../sprint4/dsp/core_only/bench/{bench_harness.h,golden_ref.h,chirp_input.h}`、`.../core_only/src/{tree_filterbank.c,tfb_8ch.h}`
- 接口 gap：`/home/it1234/.../sprint4/iface_survey.md`（G1/G4/G8）、`.../audio_io_topology.md`
- 拓扑/几何锁定：`/home/it1234/.../sprint2/docs/decisions_log.md`（DEC-S1-004 / DEC-S2-008 / DEC-S3-DSP-03 / SC-S3-GEOM-01 / DEC-S4-F7-CLOSE-01）、`.../knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md`、`.../sprint3/dsp/dsp_8ch_report.md`、`.../sprint3/audit/matlab_verify_m3_superdir_8pair.md`
- datasheet：`/home/it1234/.../knowledge_base/ezkit/bsp/datasheets/ADSP-2156x-Datasheet-EN.pdf`（IIR/FIR 并发、TRU、单核、ASRC）
- ADI 示例：`/home/it1234/.../knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/FIR_Multi_Channel_Processing/`、`.../ADSP_2156x_FIRA_Performance/`

---

## APPENDIX: adversarially-verified findings (machine record)

```json
{
 "findings": [
  {
   "id": "ORCH-1",
   "title": "Batch all 8 same-level channels into ONE multi-channel CreateTask/QueueTask instead of 72 single-channel tasks/frame",
   "claim": "fira_tree.c calls adi_fir_CreateTask(s_hFir, &ch, 1u, ...) with exactly ONE channel per segment, then one QueueTask + one busy-spin + one flush, repeated for all 8 channels x 9 segments = 72 invocations/frame. The ADI driver and example support N channels in ONE task (CreateTask with nNumChannels, ONE QueueTask, ONE ALL_CHANNEL_DONE callback). Batching the 8 channels of the same tree level into one multi-channel task collapses the 72 QueueTask round-trips (+ 72 spin-waits + 72 callback fires) to 9 (one per level) — the single largest orchestration reduction available, and it does NOT touch any frozen file (fira_tree.c is the orchestration layer, not in the frozen list).",
   "evidence": [
    {
     "source": "sprint4/dsp/fira/fira_tree.c:472-481",
     "detail": "Per segment: adi_fir_CreateTask(s_hFir, &ch, 1u, (void*)s_taskMem, FIR_MEM_SIZE(1), &hTask) — literally 1u channels; then FixedPointEnable; g_FIRTaskDoneCount=0; QueueTask; while(g_FIRTaskDoneCount<1u){} spin. One full lifecycle per segment."
    },
    {
     "source": "sprint4/dsp/fira/fira_tree.c:697-710 + 752/759/766",
     "detail": "fira_tfb_analyze issues 6 fira_run_segment_stateful calls/channel (segs 0-5) and fira_tfb_synthesize 3 (segs 6-8); called once per channel in the F7 8ch loop (fira_regression.c:612-617) => 8x9=72 segment lifecycles/frame."
    },
    {
     "source": "knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/FIR_Multi_Channel_Processing/src/FIR_Multi_Channel_Processing.c:128-256",
     "detail": "ADI example builds FirTask1_Channels[2] (an ADI_FIR_CHANNEL_INFO ARRAY) and calls adi_fir_CreateTask(hFir, FirTask1_Channels, FIR_NUMBER_OF_CHANNELS_TASK1=2, ...) — 2 channels in ONE task. Channels in a task may even differ in tap length/window (FIR_Multi_Channel_Processing.h:14,20 comments)."
    },
    {
     "source": "knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/FIR_Multi_Channel_Processing/src/FIR_Multi_Channel_Processing.c:281-282",
     "detail": "Legacy mode: while(FIRTaskDoneCount<FIR_NUMBER_OF_TASKS) — ONE ALL_CHANNEL_DONE callback per TASK after ALL its channels finish (not per channel), so 8-channel task = 1 spin target, not 8."
    },
    {
     "source": "sprint4/iface_survey.md:105-108",
     "detail": "adi_fir_CreateTask signature (hDev, *ADI_FIR_CHANNEL_INFO[], nNumChannels, *pMem, nMemSize, *phTask) confirmed from example; FIR_MEM_SIZE(n) scales with channel count."
    }
   ],
   "benefit": "L1-derived per-frame FIXED (non-per-channel) share is 10,345 cyc/frame = 2.23% (463,273 - 8x56,616, F7_CLOSING_RECORDS_DRAFT.md:114). The per-CHANNEL cost is 56,616 cyc but this LUMPS orchestration + MAC and the split is unmeasured [L4]. Batching removes 63 of 72 QueueTask round-trips + 63 spin-waits + 63 callback fires (keeps 9). Upper bound on saving = the orchestration fraction inside the 8x56,616=452,928 per-channel cyc; if orchestration is even ~15-25% of a segment (plausible given the 9 tiny windows of 8/16/32/64 samples make MAC small relative to fixed CreateTask/spin), saving is order ~50,000-110,000 cyc/frame => 8ch margin from 2.878x toward ~3.2-3.6x. Exact value [L4/待验证] pending a board re-run; the saving direction and the 72->9 call-count reduction are [L3].",
   "benefit_grade": "L3",
   "effort": "Medium. Rewrite fira_run_segment to accept an ADI_FIR_CHANNEL_INFO[8] array (one per channel, same level) + size s_taskMem to FIR_MEM_SIZE(8); restructure fira_tfb_analyze/synthesize so the 8-channel loop is INSIDE per-level (transpose loop order: level-outer, channel-inner) — this is a non-trivial dataflow refactor of the 8ch driver, NOT fira_tree.c alone. MUST re-pass R14 bit-exact (F4 0x2E0D8C6E + F5 8/8 per-channel goldens) since the per-channel histories (ch->hist[seg]) and postscale must stay per-channel within the shared task. Needs >=1 FIRA board run.",
   "risk": "Steering KILLS part of this: per-channel steered coefficients differ across the 8 channels, but same-level batching only needs same WINDOW/SAMPLING (coeffs are per-channel-info, allowed to differ within a task per FIR_Multi_Channel_Processing.h:14). So batching survives steering for the window/mode grouping, but each channel still carries its own CoeffIndex. Re-creation cost on coeff change (steering) interacts with ORCH-3. Frozen-core: untouched (filter math stays in core-side sat/sub/add and the frozen hb63 coeffs; only task grouping changes). Bit-exact MUST be re-proven — a batched task could reorder DMA writeback vs the per-segment flush, reintroducing the cache hazard fira_tree.c:483-524 papered over.",
   "notes": "This is the direct answer to the CTO's '3.1x is too low, overhead eats it' concern: the overhead is per-SEGMENT (72 lifecycles), and the driver explicitly supports collapsing the channel dimension 8:1.",
   "dimension": "orchestration",
   "verdict": {
    "finding_id": "ORCH-1",
    "verdict": "confirmed",
    "grade_ok": true,
    "reasons": "Core claim holds against the sources I opened myself.\n\n(1) Mechanism CONFIRMED verbatim. fira_tree.c:472-481 calls adi_fir_CreateTask(s_hFir, &ch, 1u, (void*)s_taskMem, FIR_MEM_SIZE(1), &hTask) with literally 1u channel, then FixedPointEnable, g_FIRTaskDoneCount=0, QueueTask, and busy-spin while(g_FIRTaskDoneCount<1u){}, then flush_data_buffer + postscale — one full lifecycle per segment.\n\n(2) Segment count 72 CONFIRMED. fira_regression.c:612-617 loops c=0..7 calling fira_tfb_analyze + fira_tfb_synthesize; fira_tfb_analyze issues 6 fira_run_segment_stateful (segs 0-5, fira_tree.c:697-710) and fira_tfb_synthesize 3 (segs 6-8, :752/759/766) => 8x9=72 segment lifecycles/frame. NOTE: the evidence-2 sub-phrase \"72 analyze + 24 synth\" is mislabeled (analyze is 8x6=48, synth 8x3=24; total 72). This same mislabel exists in the source comment fira_regression.c:607-608, so the finding inherited it. The TOTAL 72 used in the benefit math is correct; the mislabel does not change any number.\n\n(3) Multi-channel API CONFIRMED. FIR_Multi_Channel_Processing.c:128-256 builds ADI_FIR_CHANNEL_INFO FirTask1_Channels[2] and calls adi_fir_CreateTask(hFir, FirTask1_Channels, FIR_NUMBER_OF_CHANNELS_TASK1=2, ...). Header .h:14/20 confirm tap-length and window-size MAY vary across channels in a task — the finding's same-level grouping (same window) is strictly easier than what the example already does.\n\n(4) One-callback-per-task CONFIRMED — the decisive cost point. FIR_Multi_Channel_Processing.c:281-282 Legacy mode: while(FIRTaskDoneCount<FIR_NUMBER_OF_TASKS) and comment :275 \"the callbacks are received after completion of all the channels of the task.\" fira_tree.c:478 explicitly uses Legacy (\"MCP.c:282\"). So an 8-channel task = 1 spin target / 1 callback, not 8. 72 single-channel tasks -> 9 multi-channel tasks (channel collapse 8:1 over 9 segs); removes 63 QueueTask round-trips + 63 spins + 63 callback fires. Verified: 8x9=72 -> 1x9=9.\n\n(5) Signature CONFIRMED iface_survey.md:105 (hDev, *ADI_FIR_CHANNEL_INFO[], nNumChannels, *pMem, nMemSize, *phTask). Caveat: iface_survey.md:100 states the 2156x API is known ONLY from example source (\"本机 header 无定义 -> 源码即唯一证据\"), and FIR_MEM_SIZE(n) macro definition is absent on this host (iface_survey.md:111). So the batching mechanism rests on [L2 vendor-example], not a host header — which is exactly why the finding requires a board run and grades the magnitude [L4]. Honest.\n\nBENEFIT ARITHMETIC verified against L1-derived baseline (F7_CLOSING_RECORDS.md:114, :37-38, :120-121): 463,273 - 8x56,616 = 10,345 cyc/frame = 2.23% fixed share (recomputed, exact). Margin recompute: base MCPS=463273*750/1e6=347.45, margin 1000/347.45=2.878x (matches). Removing 50k cyc -> margin 3.226x; 110k -> 3.774x. The finding's \"~3.2-3.6x\" is within this band. All of this is correctly tagged [L4/待验证] for magnitude, [L3] for direction/call-count.\n\nL-GRADE HONEST. F7_CLOSING_RECORDS.md:120-121 EXPLICITLY states the orchestration-vs-MAC ratio inside the 56,616 \"CANNOT [be determined], without more data — the 56,616 lumps CreateTask + FixedPointEnable + QueueTask + spin + ... MAC.\" The finding faithfully reflects this: it labels the per-channel 56,616 as lumped/unmeasured [L4], grades the savings magnitude [L4/待验证], and only the 72->9 call-count reduction + direction as [L3]. No L4 dressed as L1/L2. benefit_grade=L3 is defensible because the load-bearing claim (call-count reduction, direction of saving) IS L3-analytic; the dollar figure is explicitly L4.\n\nCONSTRAINTS not violated. Frozen-core untouched: tree_filterbank.c / tfb_8ch.c / fir_coeffs_hb63.h all live in sprint4/dsp/core_only/ (confirmed by find); the change is in fira_tree.c orchestration + the fira_regression.c 8ch loop. pCoefficientIndex is a per-channel field (fira_tree.c:181), so the finding's steering caveat (per-channel steered coeffs may differ within one task) is structurally correct. R14 bit-exact re-pass is correctly demanded: F4 anchor 0x2E0D8C6E exists across F4/F5 handoffs (confirmed), and a board FIRA run is required. The cache-hazard risk note is legitimate — the IO1d flush_data_buffer is currently PER-SEGMENT (fira_tree.c:483-524); batching changes writeback granularity and could reintroduce the hazard, so bit-exact MUST be re-proven. No R14/C9 separation violation (this is orchestration headroom analysis, no FIRA benefit folded into selection/commitment).\n\nMINOR DEFECTS (do not change verdict): (a) benefit cites \"F7_CLOSING_RECORDS_DRAFT.md:114\" but the actual file is F7_CLOSING_RECORDS.md — line 114 content matches exactly (10,345 / 2.23%). (b) \"72 analyze + 24 synth\" sub-phrasing is wrong (48/24); harmless. Both are citation hygiene, not substance.",
    "corrected": "No correction to the benefit needed — arithmetic and grade are honest. Two citation fixes recommended for the record: (1) source is F7_CLOSING_RECORDS.md:114 (not ...DRAFT.md); (2) the segment split is 48 analyze + 24 synth = 72 total, not \"72 analyze + 24 synth\" (this mislabel also exists at fira_regression.c:607-608 and should be corrected at source). The 72->9 channel-collapse and the 2.878x -> ~3.2-3.6x margin band are confirmed but remain [L4/待验证] for magnitude pending >=1 FIRA board run + R14 bit-exact re-pass (F4 0x2E0D8C6E + F5 8/8 per-channel goldens) + critic gate. Additional risk to flag for the steering line: FIR_MEM_SIZE(n) macro is undefined on this host, so s_taskMem sizing for the 8-channel task is itself board-unverified.",
    "grade_fix": "none required; benefit_grade=L3 is honest (direction/call-count is L3-analytic; magnitude already labeled [L4/待验证]). The L1 anchors it derives from (463,273 / 56,616 / 10,345) are correctly cited as L1-derived from F7_CLOSING_RECORDS.md."
   }
  },
  {
   "id": "ORCH-2",
   "title": "Create FIRA tasks ONCE (persistent task memory), re-queue every frame — eliminate per-frame CreateTask+FixedPointEnable",
   "claim": "fira_run_segment calls adi_fir_CreateTask + adi_fir_FixedPointEnable on EVERY segment EVERY frame (72x/frame x 750 frames/s). The ADI example creates tasks ONCE (before the frame/queue loop) and only re-QueueTasks; CreateTask parses the channel-info array and lays out task memory — pure setup that does not change frame-to-frame for a FIXED-coefficient build. The geometry is broadside-only with one frozen hb63 set (fira_tree.c:62 g_hb_fira = g_hb63_fira32 for all segments), so the channel-info (taps, window, in/out bases) is frame-invariant => CreateTask can be hoisted out of the per-frame path into fira_tree_setup.",
   "evidence": [
    {
     "source": "sprint4/dsp/fira/fira_tree.c:468-477",
     "detail": "Inside fira_run_segment (per-frame, per-segment): ch = fira_make_channel(...); adi_fir_CreateTask(...); adi_fir_FixedPointEnable(hTask, SIGNED). Both run every frame for all 72 segments."
    },
    {
     "source": "knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/FIR_Multi_Channel_Processing/src/FIR_Multi_Channel_Processing.c:251-272",
     "detail": "Example: 2x adi_fir_CreateTask BEFORE the for-loop, then for(...) adi_fir_QueueTask(hFirTasks[count]) — tasks created once, queued in the loop. The handles persist in hFirTasks[FIR_NUMBER_OF_TASKS]."
    },
    {
     "source": "sprint4/dsp/fira/fira_tree.c:288-301",
     "detail": "fira_tree_setup (the once-per-startup hook) currently only does Open + RegisterCallback and a comment 'CreateTask grouped per segment = F4/F5 bench-side' — i.e. CreateTask was deliberately left in the per-frame path; hoisting it here is the intended home."
    },
    {
     "source": "knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/FIR_Multi_Channel_Processing/system/drivers/fir/adi_fir_config_2156x.h:120,138",
     "detail": "Legacy supports STATIC fixed-point: ADI_FIR_FIXED_POINT_MODE=1 + ADI_FIR_CFG_FIXED_INPUT_FORMAT=ADI_FIR_IN_FORMAT_SINT, set once at config-header compile time — removes the per-task runtime adi_fir_FixedPointEnable call entirely (72 calls/frame -> 0)."
    }
   ],
   "benefit": "Removes 72 CreateTask + 72 FixedPointEnable calls/frame from the steady-state path (re-queue keeps 72 QueueTask, or 9 if combined with ORCH-1). CreateTask does channel-info validation + task-memory layout (non-trivial vs a bare QueueTask). Saving is a slice of the unmeasured orchestration lump inside 56,616 cyc/channel [L4]; combined with ORCH-1, the residual per-frame work approaches the pure MAC + DMA-wait + postscale. Order-of-magnitude: if CreateTask+FixedPointEnable are even ~1,000-2,000 cyc combined per segment, that is ~72,000-144,000 cyc/frame removed => margin 2.878x toward ~3.3-4.0x. Magnitude [L4/待验证]; the call-count elimination is [L3].",
   "benefit_grade": "L4",
   "effort": "Low-Medium. Move CreateTask into fira_tree_setup (build 72 persistent ADI_FIR_CHANNEL_INFO with frame-invariant bases into static task memory, store 72 hTask handles, or 9 if ORCH-1 batched). Per-frame path becomes: refresh input buffers + QueueTask + spin + flush + postscale. Switch to static fixed-point config to drop FixedPointEnable. MUST re-pass R14 (the channel-info in/out base pointers must point at the SAME static buffers the per-frame data is copied into — verify s_seg_in/s_seg_out3 contract still holds). >=1 board run.",
   "risk": "BLOCKS under steering with dynamic coefficients: if coeffs change per frame (beam steering re-computes per-channel weights), CreateTask MAY need re-running when CoefficientIndex/values change — UNLESS adi_fir_SetChannelCoefficientBuffer (adi_fir_v2.h:240, per iface_survey.md:97) lets coeffs be swapped on a persistent task without full re-creation. That API exists in v2 but its presence on the 21569 SHARC header is a G1 gap (iface_survey.md:303) — unverified. So persistent-task reuse is a clean win for the CURRENT broadside frozen-coeff build, but its steering compatibility is [L4/待验证] and depends on closing G1. Frozen-core untouched.",
   "notes": "Pairs naturally with ORCH-1. For steering, the key question to answer on-bench: can coeffs be updated on a live task (SetChannelCoefficientBuffer) or must the task be re-created each steering update?",
   "dimension": "orchestration",
   "verdict": {
    "finding_id": "ORCH-2",
    "verdict": "confirmed",
    "reasons": "All cited evidence verified by direct read:\n\n(1) Per-frame redundancy is REAL. fira_tree.c:472-477 — inside fira_run_segment (per-segment, per-frame) it calls adi_fir_CreateTask then adi_fir_FixedPointEnable(hTask, SIGNED_INTEGER) on EVERY invocation. fira_make_channel is rebuilt each call (line 468). Segment count: each channel runs 9 FIRA segments — analyze = seg 0-5 (3 DEC at :697-699 + 3 INT at :708-710) and synthesize = seg 6-8 (:752/:759/:766). 9 x 8ch = 72 main-path segments/frame. F7_R14_RULING_MATERIAL.md:15 independently lists \"72+24 segments ... CreateTask/FixedPointEnable/QueueTask/spin/postscale/cache-invalidate\" as the steady-frame breakdown — corroborates the per-frame CreateTask+FixedPointEnable claim.\n\n(2) Frame-invariance is REAL (the load-bearing precondition for hoisting). fira_run_segment_stateful (fira_tree.c:604-657) ALWAYS calls fira_run_segment with the SAME static buffers: in = s_seg_in (static, :602), out = s_seg_out3 (static, :438). The per-frame data is memcpy'd INTO s_seg_in (:615-616, :634-639) before the call. Coeffs are the single frozen set g_hb63_fira32 for all segments (:62), and the set is a verified palindrome so tap-orientation is moot (:138-143). So the ADI_FIR_CHANNEL_INFO in/out bases + coeffs + taps ARE frame-invariant => CreateTask is hoistable. The only per-segment-level variation is nWindowSize/nInputBuffCount (f0=64..f3=8), which is why the finding correctly calls for ~72 distinct persistent channel-infos, not one.\n\n(3) ADI example checks out: FIR_Multi_Channel_Processing.c:251-272 — 2x CreateTask BEFORE the for-loop, then for(...) adi_fir_QueueTask(hFirTasks[count]); handles persist. Create-once-queue-many is exactly as cited.\n\n(4) Static fixed-point config checks out: adi_fir_config_2156x.h:120 (ADI_FIR_FIXED_POINT_MODE) and :138 (ADI_FIR_CFG_FIXED_INPUT_FORMAT) — both \"only have effect in Legacy mode\" (:115,132) and are set once at compile time. The repo build IS Legacy (fira_tree.c:478 \"Legacy, MCP.c:282\"), so setting MODE=1 + format=SINT would drop the 72 per-frame FixedPointEnable calls to 0. Valid.\n\nGRADE HONESTY (the key adversarial test): the cycle-savings magnitude (~1,000-2,000 cyc/seg => 72k-144k cyc/frame) is a pure guess with NO measurement basis. The repo's OWN L1-derived analysis (F7_CLOSING_RECORDS.md:120-122) states explicitly: \"CANNOT, without more data — the orchestration-vs-MAC ratio INSIDE the 56,616 ... Splitting these is what tells us how much LARGER FRAME would amortize\" and lists FRAME-sweep / segment-instrumentation as the only ways to get it. The finding does NOT dress this up: benefit_grade=\"L4\", text says magnitude \"[L4/待验证]\" and call-count elimination \"[L3]\". That is exactly the honest split.\n\nARITHMETIC: margin projection is internally consistent — removing 144k from 463,273 => 319,273 => 2.878 x (463273/319273) = 4.18x; removing 72k => 391,273 => 3.41x; so \"~3.3-4.0x\" is a reasonable approximation of the (hypothetical) band. Call-count: 72 CreateTask + 72 FixedPointEnable removed per frame is correct.\n\nCONSTRAINTS: frozen core untouched (change lives in fira_tree.c orchestration + a config header, not tree_filterbank.c/tfb_8ch.c/hb63). FRAME is brief-declared negotiable. No R14/C9 violation: finding folds NOTHING into selection/promises, explicitly requires re-passing R14 + >=1 board run + buffer-contract re-verification (s_seg_in/s_seg_out3 contract — which I confirmed is exactly what the persistent channel-info bases must point at). Effort/risk realistic.\n\nWEAKNESSES (do not change verdict): (a) the finding's \"+24 (1ch x 3 warm? actually 72 main + 24 aux)\" gloss is muddled/hedged — the +24 is the c=7 unity instrumentation/aux channel path (fira_regression.c:632-646 cited in F7 material), not a clean 8ch path item; but the load-bearing 72 main count is correct and the proposal's value does not depend on the +24. (b) The headline cycle number is unmeasured speculation — but it is correctly graded [L4], so this is a disclosed limitation, not a misrepresentation.\n\nSteering-risk caveat verified: iface_survey.md:97 lists adi_fir_SetChannelCoefficientBuffer at adi_fir_v2.h:240, and :303 (G1) confirms the SHARC-side adi_fir_2156x.h is missing on this host — so live-coeff-swap on a persistent task is genuinely unverified [L4/待验证], exactly as the finding states.",
    "grade_ok": true,
    "corrected": "Core claim confirmed as-is. Two clarifications, neither weakening the proposal: (1) the per-frame segment count is 72 main-path (8ch x 9 = 3 DEC + 3 INT analyze + 3 INT synth); the finding's \"+24\" is the c=7 unity instrumentation/aux path and is not load-bearing — drop the hedge. (2) The CYCLE benefit (~72k-144k cyc/frame, margin -> ~3.3-4.0x) is UNMEASURED speculation with no anchor in any L1 number; the repo's own F7_CLOSING_RECORDS.md:120-122 states the orchestration-vs-MAC split inside the 56,616/channel is unknown without a FRAME sweep or per-segment CCNT instrumentation. The finding already grades this magnitude [L4/待验证] (only the 72+72 call-count elimination is [L3]) — so the claim is honest; just ensure any downstream consumer treats the headroom figure as L4 exploration, never as a basis for any selection/promise (C9) until measured on bench.",
    "grade_fix": "No fix needed — grade is honest. benefit_grade=\"L4\" matches the unmeasured cycle magnitude; call-count elimination correctly tagged [L3]; steering-compatibility correctly tagged [L4/待验证] pending G1 closure."
   }
  },
  {
   "id": "ORCH-3",
   "title": "Replace busy-spin (while g_FIRTaskDoneCount<1) with callback-driven pipelining / queue depth >1 so segments overlap instead of serializing",
   "claim": "fira_run_segment QUEUES one segment then BUSY-SPINS the core on while(g_FIRTaskDoneCount<1u){} until that one segment's ALL_CHANNEL_DONE, THEN does the next segment. The 72 segments are fully serialized: core idles during every FIRA DMA/MAC, FIRA idles during every core postscale/flush/setup. The driver supports queueing multiple tasks (example queues 2 tasks back-to-back then waits, FIR_Multi_Channel_Processing.c:268-282) and a registered callback (already wired, fira_done_cb fira_tree.c:222-228). Queue-depth>1 / callback continuation lets the core prepare/postscale segment N+1 while FIRA computes segment N, hiding the spin.",
   "evidence": [
    {
     "source": "sprint4/dsp/fira/fira_tree.c:478-481",
     "detail": "g_FIRTaskDoneCount=0; adi_fir_QueueTask(hTask); while(g_FIRTaskDoneCount<1u){} — synchronous busy-wait, one task in flight at a time, core spins (no useful work) for the whole FIRA latency of each of the 72 segments."
    },
    {
     "source": "knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/FIR_Multi_Channel_Processing/src/FIR_Multi_Channel_Processing.c:267-282",
     "detail": "Example queues ALL tasks first (for-loop QueueTask) THEN waits for all callbacks — demonstrates >1 task queued concurrently; the driver tracks completion via FIRCompletedTaskHandles[] and a per-task callback arg (pArg)."
    },
    {
     "source": "sprint4/dsp/fira/fira_tree.c:222-228",
     "detail": "fira_done_cb already registered and increments g_FIRTaskDoneCount on ALL_CHANNEL_DONE; the callback mechanism needed for pipelining is already present — only the spin-then-next control structure blocks overlap."
    },
    {
     "source": "sprint4/iface_survey.md:99",
     "detail": "adi_fir_WaitForEvent(hConfig, eEvent, *pArg) exists (adi_fir_v2.h:190) — an event/idle wait alternative to busy-spin (lets the core sleep or do other work instead of burning cycles)."
    },
    {
     "source": "sprint4/dsp/fira/fira_tree.c:278",
     "detail": "Code comment acknowledges the spin is a placeholder: 'spin; bench can switch to idle/event wait' — the design already flags this as a known optimization point."
    }
   ],
   "benefit": "The spin time is core cycles spent doing NOTHING but waiting for FIRA — it is inside the measured 463,273 cyc (F7 measures wall cycles incl. spin, fira_regression.c:611-619). If FIRA MAC/DMA latency per segment is non-trivial (the whole point of offload), the spin dominates many of the 72 segments. Overlapping core postscale/setup of seg N+1 with FIRA compute of seg N can hide most of one or the other. Potential: convert serial (core + spin + FIRA) per segment into max(core, FIRA) per segment. If spin is ~30-50% of a segment, hiding it saves order ~100,000-200,000 cyc/frame => margin 2.878x toward ~4-6x. Magnitude entirely [L4/待验证] — depends on the unmeasured FIRA-latency-vs-core-work ratio inside 56,616; only a segment-instrumented board run (F7_CLOSING Q3 option iii) can quantify.",
   "benefit_grade": "L4",
   "effort": "High. True pipelining requires double-buffering the per-segment in/out scratch (s_seg_in/s_seg_out3 are SINGLE static buffers, fira_tree.c:438,602 — explicitly NON-reentrant, see the stack DECISION note) so segment N+1 can be prepared while N is in flight; and the tree dataflow has DATA DEPENDENCIES (a1->a2->a3 are sequential decimations, fira_tree.c:697-699; synthesize is telescoping, 752-773) so only INDEPENDENT segments overlap (e.g. across the 8 channels at the same level — which ORCH-1 already groups). Realistically pipelining is the cross-channel parallelism of ORCH-1 plus the postscale/setup overlap. MUST re-pass R14. Multiple board runs.",
   "risk": "The data dependency chain inside one channel's tree is mostly serial (each level feeds the next), so single-channel pipelining gains little; the real overlap is cross-channel (ORCH-1 territory) — partially double-counts ORCH-1's benefit, do not sum them. Double-buffering reintroduces the cache-coherence hazard the current single-buffer + flush_data_buffer design (fira_tree.c:483-524) was carefully built to avoid (approach B 'no memset'); a pipelined design must re-derive the flush/invalidate ordering for 2 in-flight buffers — high bit-exact regression risk. Steering: orthogonal (helps regardless). Frozen-core untouched.",
   "notes": "Lowest-confidence benefit (pure L4) but potentially the largest if FIRA latency is high. The cheap precursor is F7_CLOSING_RECORDS_DRAFT.md Q3 option (iii): instrument one segment (CreateTask vs QueueTask vs spin vs postscale CCNT) to learn the spin fraction BEFORE committing to a pipelining refactor.",
   "dimension": "orchestration",
   "verdict": {
    "finding_id": "ORCH-3",
    "verdict": "confirmed",
    "reasons": "All cited evidence verified by opening the files myself. (1) Busy-spin confirmed at fira_tree.c:479-481: `g_FIRTaskDoneCount=0; adi_fir_QueueTask(hTask); while(g_FIRTaskDoneCount<1u){}` — exactly one task in flight, core spins for the whole FIRA latency; same pattern at :278. The self-flagging comment \"spin; bench can switch to idle/event wait\" is verbatim at both :278 and :481. (2) Callback already wired: fira_tree.c:222-228 fira_done_cb increments g_FIRTaskDoneCount on ADI_FIR_EVENT_ALL_CHANNEL_DONE. (3) The load-bearing example claim checks out — FIR_Multi_Channel_Processing.c:267-272 QUEUES 2 tasks in a for-loop, THEN :282 `while(FIRTaskDoneCount<FIR_NUMBER_OF_TASKS)` waits for both, proving the driver supports >1 task concurrently in Legacy mode. (4) adi_fir_WaitForEvent exists (iface_survey.md:99 -> adi_fir_v2.h:190), a real event/idle alternative to busy-spin. (5) Single-buffer non-reentrancy confirmed: s_seg_out3 (fira_tree.c:438) and s_seg_in (601-602) are file-scope static with explicit `[ASSUME] FIRA orchestration is single-threaded/non-reentrant per frame... If F5 8ch concurrency runs segments in parallel, this must become per-task scratch` (598-600) — so double-buffering is genuinely required for pipelining. (6) Data dependencies confirmed: analyze a1->a2->a3 are sequential decimations (697-699), synthesize is telescoping (752-773: each fira_run_segment_stateful output feeds f_sat_add_i32 which feeds the next segment's input) — so only cross-channel segments overlap, exactly as the finding's risk note states.\n\nArithmetic/anchoring verified: baseline numbers are all L1 from F7_R14_RULING_MATERIAL.md (463,273 cyc :15; 347.45 MCPS :39-40; 2.878x :41-42; 1ch 56,616 :312) and F7_CLOSING_RECORDS.md (10,345 cyc=2.23% fixed share :114,234 = 463,273-8*56,616). F7 measures WALL cycles incl spin (fira_regression.c:611-619 brackets the full FIRA path which contains the :481 spin) — so the spin IS inside the measured 463,273, as claimed. Critically the benefit MAGNITUDE (~100-200k cyc, margin toward 4-6x) is honestly and explicitly [L4/待验证] because the spin fraction inside the 56,616 LUMP is genuinely unmeasured — F7_CLOSING_RECORDS.md:121 confirms 56,616 lumps CreateTask+FixedPointEnable+QueueTask+spin+postscale and is NOT split; only Q3 option (iii) segment-CCNT instrumentation (F7_CLOSING_RECORDS.md:133-134, correctly described as high-effort/invasive) can quantify it.\n\nConstraints OK: frozen core untouched (works around orchestration/buffering only); R14 confirmed OPEN (F7_R14_RULING_MATERIAL.md:7 'MATERIAL ONLY. Does NOT decide R14 closure or relax C9') and C9/iron-rule-8 binds (decisions_log.md:258) — but this is an optimization PROPOSAL graded [L4], not a benefit entering selection/流片/commitment, so it does not violate C9 by itself. Finding correctly refuses to sum with ORCH-1 (flags partial double-count of cross-channel overlap). Effort/risk realistic: double-buffering reintroduces the cache-coherence hazard the single-buffer approach-B + flush_data_buffer design (fira_tree.c:483-524) was built to avoid, and re-passing R14 needs multiple board runs.\n\nTwo minor non-material slips (do not weaken): (a) finding cites filename `F7_CLOSING_RECORDS_DRAFT.md`; actual is `F7_CLOSING_RECORDS.md` (content/Q3-option-iii correct). (b) benefit ceiling '2.878x toward 4-6x' is optimistic given the 2.23% per-frame fixed share is small, but the finding self-caveats this is entirely L4 and that the real overlap is cross-channel — so no overclaim.",
    "grade_ok": true,
    "grade_fix": "No grade change needed. benefit_grade [L4] is honest and not dressed up — the finding repeatedly states the magnitude is pure [L4/待验证] and that only a board run (Q3 option iii) can quantify it. Cited baselines are correctly attributed L1; the proposal does not assert any measured speedup.",
    "corrected": "No correction to the core claim. Optional precision: (1) fix the citation `F7_CLOSING_RECORDS_DRAFT.md` -> `F7_CLOSING_RECORDS.md`. (2) The realistic benefit is bounded BELOW the headline 4-6x: with the per-frame FIXED share only 10,345 cyc (2.23%), the spin/overlap is per-segment/per-channel, so the achievable gain is dominated by cross-channel overlap (ORCH-1 territory) plus postscale/setup hiding — do NOT sum with ORCH-1. Keep the F7 Q3 option (iii) segment-CCNT precursor as the gate before any pipelining refactor; the spin fraction is the single unmeasured quantity that decides whether this is worth the high bit-exact/R14 re-validation cost."
   }
  },
  {
   "id": "ORCH-4",
   "title": "Eliminate the per-segment flush_data_buffer if the driver's ADI_CACHE_MANAGEMENT already invalidates the output region (avoid double cache op)",
   "claim": "fira_run_segment calls flush_data_buffer(s_seg_out3, ..., enInv=1) after EVERY segment (72x/frame) to invalidate the FIRA DMA output region before postscale reads it. But the ADI FIR config has ADI_CACHE_MANAGEMENT=1 (adi_fir_config_2156x.h:64), and the code's OWN comment (fira_tree.c:507-511) notes the Legacy driver 'may already invalidate the output region at QueueTask completion' when the output buffer is cache-aligned (s_seg_out3 is #pragma align 32). If the driver already does it, the explicit flush is redundant work on the per-frame path.",
   "evidence": [
    {
     "source": "sprint4/dsp/fira/fira_tree.c:522-524",
     "detail": "flush_data_buffer((void*)s_seg_out3, (void*)(s_seg_out3+fira_window*3u), 1) called per segment, 72x/frame. A cache range op over up to 512*3=1536 words touches up to 48 cache lines each call."
    },
    {
     "source": "sprint4/dsp/fira/fira_tree.c:507-511",
     "detail": "Code comment: 'NOTE on driver auto-invalidate (FIRA_IMPL.md L35/L155): when the FIR config header has ADI_CACHE_MANAGEMENT=1 AND the output buffer is ADI_CACHE_ALIGN'd, the Legacy driver may already invalidate the output region at QueueTask completion. This explicit call is then idempotent ... kept as defense for the cache-management-off case.'"
    },
    {
     "source": "knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/FIR_Multi_Channel_Processing/system/drivers/fir/adi_fir_config_2156x.h:61-64",
     "detail": "#define ADI_CACHE_MANAGEMENT (1) — driver-managed cache IS enabled in the ADI reference config; comment: 'If the application wants to manage cache, this macro has to be set to 0.'"
    }
   ],
   "benefit": "Removes up to 72 cache-range invalidate operations/frame if confirmed redundant. Each flush_data_buffer over ~tens of cache lines is small but non-zero and on the hottest path. Saving is a small slice of the orchestration lump [L4]; likely the smallest of the four findings (order single-digit thousands of cyc/frame), but zero-cost-direction (deleting redundant work). Magnitude [L4/待验证].",
   "benefit_grade": "L4",
   "effort": "Low to verify, but the verification is the catch: on-bench A/B (flush present vs absent) must show IDENTICAL bit-exact result (F4/F5 goldens) AND no stale-data corruption across many frames. This is exactly the false-green / IO-buffer-contract gate territory (CLAUDE.md DSP/FIRA special gates) — removing a cache op that LOOKS redundant but is load-bearing = silent data corruption. Must re-pass R14 with the flush removed, on board, over the full chirp. 1 board run.",
   "risk": "HIGH regret if wrong: the entire DEC-PHASE / IO1d cache discipline (fira_tree.c:483-524) was hard-won; the comment itself keeps the flush 'as defense for the cache-management-off / region-not-driver-tracked case'. Whether the 21569 SHARC Legacy driver actually auto-invalidates is a G1-class gap (the real adi_fir_2156x.h is absent on this host, iface_survey.md:303,318) — UNVERIFIABLE here. Recommend KEEP unless bench proves the driver invalidates. Do NOT remove speculatively. Steering: orthogonal. Frozen-core untouched.",
   "notes": "Lowest priority; included for completeness because it is one of the explicit per-segment ops the task asked to inventory. The honest call is 'measure first, likely keep'.",
   "dimension": "orchestration",
   "verdict": {
    "finding_id": "ORCH-4",
    "verdict": "confirmed",
    "reasons": "All cited evidence checks out against the files I opened myself. (1) fira_tree.c:522-524 holds exactly one flush_data_buffer(s_seg_out3, s_seg_out3+fira_window*3u, enInv=1); grep confirms it is the ONLY flush_data_buffer in the file. (2) The comment at fira_tree.c:507-511 is verbatim as quoted (\"...the Legacy driver may already invalidate the output region at QueueTask completion... kept as defense for the cache-management-off / region-not-driver-tracked case\"). (3) adi_fir_config_2156x.h:64 is #define ADI_CACHE_MANAGEMENT (1) with the quoted comment at 61-62. (4) The 72x/frame count is correct: F5_F7_PLAN.md:33 states \"8ch x 9 seg = 72 个串行 QueueTask\"; each segment runs fira_run_segment_stateful -> fira_run_segment (lines 697-766 issue the 9 seg invocations per channel), each containing exactly one flush. The flush range is fira_window*3 (DEC: FIRA_RATIO*out_count, MAXWINDOW=512), so the \"up to 512*3=1536 words / ~48 cache lines\" worst case is right (line 523, 450).\nSTRENGTHENING (finding under-states): FIRA_IMPL.md:35 and :155 (the cited L35/L155) state plainly that with ADI_CACHE_MANAGEMENT=1 the QueueTask path does \"flush 输入/系数、invalidate 输出\" — the project's own L2-doc asserts the driver already invalidates the output, which makes the redundancy hypothesis stronger than the in-code comment's hedge.\nLOAD-BEARING CAVEAT (honest): the driver source adi_fir_legacy_2156x.c and MCP.c are NOT present on this host (find returned nothing), and the header adi_fir_2156x.h is confirmed absent (iface_survey.md:303 G1, :318). So the \"invalidate 输出\" assertion is interpretation, not source-confirmed; the actual 21569 SHARC Legacy driver behavior is genuinely UNVERIFIABLE here. The finding's \"UNVERIFIABLE / G1-class gap / KEEP unless bench proves\" is accurate.\nCONSTRAINTS clean: fira_tree.c is NOT frozen-core (red line per FIRA_IMPL.md:51 is tree_filterbank.{c,h}/golden_ref.h/chirp_input.h/adi_fir_config_2156x.h/coeffs); the finding correctly removes only the explicit fira_tree.c flush and leaves the config header untouched. Re-validation correctly scoped to a board R14 bit-exact pass + the false-green/IO-buffer-contract gates (CLAUDE.md DSP/FIRA gates IO1) over the full chirp. Steering-orthogonal; R14/C9 separation not implicated. Minor note: line 487/515 describes the postscale READ span as out_count*3 (DEC odd-phase), while the actual flush at 523 uses the full fira_window*3 — the finding's 1536-word worst case correctly references the flush span, consistent.",
    "grade_ok": true,
    "corrected": "Benefit grade [L4] is honest: no per-op cycle measurement exists anywhere in the repo, so \"order single-digit thousands of cyc/frame\" is a plausible estimate (72 calls x ~tens of cache lines), consistent with being a small slice of the 10,345-cyc L1 per-frame fixed share. Not dressed as L1/L2. No correction needed. The only refinement: the finding's own conservative recommendation (\"measure first, likely keep\") is the right call given the driver source is absent here — this is correctly the lowest-priority of the four findings and must NOT be removed speculatively; removal is conditional on a board A/B bit-exact R14 pass proving the driver auto-invalidate is real."
   }
  },
  {
   "id": "FRAME-1",
   "title": "FRAME=128/256 MCPS model for the FIRA path: per-second MCPS DROPS, win grows — but magnitude bounded by an UNMEASURED orchestration:MAC split",
   "claim": "Doubling/quadrupling FRAME amortizes the per-frame fixed orchestration (10,345 cyc/frame, the 2.23% fixed share measured at FRAME=64) over 2x/4x the samples, so the FIRA path's MCPS at FRAME=128/256 is STRICTLY BELOW 347.45 MCPS. Exact reduction is a RANGE because the orchestration-vs-MAC split INSIDE the 56,616 cyc/channel is NOT measured (the analyze/synth tail-reads errored, F7_R14_RULING_MATERIAL.md:312-321). Model: let total per-frame cyc = FIXED + PERCH, where FIXED=10,345 (measured), PERCH=452,928 (=8x56,616, the per-channel work). Split PERCH into orchestration O (per-segment CreateTask/QueueTask/spin/postscale/cache-inval, ~constant per call, 96 segment-calls/frame) + MAC M (scales linearly with window). At FRAME=N (N=128 => x2, N=256 => x4 relative to 64): cyc(N) = FIXED + O + M*(N/64); fps(N)=48000/N; MCPS(N)=cyc(N)*fps(N)/1e6. Because FIXED and O are amortized while M*(N/64)*fps stays ~constant (M MCPS is frame-independent), MCPS falls. BOUNDS at FRAME=256: if O=0 (all-MAC, pessimistic for amortization) MCPS_256 ~= (10,345/4 + 452,928)*(48000/256)/1e6 = 85.0 MCPS, margin 1000/85.0=11.8x. If O is large (say O=0.7*PERCH, MAC small) MCPS_256 -> dominated by amortized O/4: ~ (10,345+0.7*452,928)/4 + 0.3*452,928 ... )*187.5/1e6 ~= 86 MCPS too but driven differently — the floor is set by the irreducible MAC-MCPS. NET: FRAME=128 FIRA MCPS in ~174-180 MCPS (margin ~5.6-5.7x); FRAME=256 in ~85-90 MCPS (margin ~11-11.8x). Only the per-frame FIXED 10,345 amortization is FIRM; the O-amortization adds on top and only IMPROVES it.",
   "evidence": [
    {
     "source": "sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:312-313",
     "detail": "L1 facts: g_f7_cyc_1ch_fira=56,616; 8x56,616=452,928 vs g_f7_cyc_8ch_fira=463,273 => per-frame FIXED share = 10,345 cyc = 2.23%, flat per-channel cost"
    },
    {
     "source": "sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:314-321",
     "detail": "g_f7_cyc_analyze_fira / g_f7_cyc_synth_fira read ERRORED in CCES — the orchestration-vs-MAC split inside 56,616 is therefore UNMEASURED; MCPS model must be a RANGE parameterized by that split"
    },
    {
     "source": "sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:154-166",
     "detail": "dsp teammate's own [L3] scaling argument: per-segment orchestration C ~constant, MAC proportional to window (8/16/32/64 at FRAME=64); larger FRAME amortizes C over more samples => FIRA cyc/sample DROP, FIRA-vs-core speedup widens"
    },
    {
     "source": "sprint4/dsp/core_only/bench/bench_harness.c:123-124",
     "detail": "fpf=BENCH_FS/BENCH_FRAME; mcps=cyc_frame*fpf/1e6 — confirms fps halves at FRAME=128, quarters at FRAME=256, so MCPS = cyc(N)*fps(N) is the correct model"
    }
   ],
   "benefit": "FIRA-path realtime margin improves from 2.878x (FRAME=64) to ~5.6-5.7x (FRAME=128) to ~11-11.8x (FRAME=256) at 1GHz [L3 model, L1 inputs]. The ~10x criterion (currently KILLED at FRAME=64 per F7 §3c) becomes REACHABLE at FRAME=256 by amortization alone, before any other optimization. Headroom freed for steering: at FRAME=256 the algorithm core drops from 34.7% to ~8.5-9% of one core, freeing ~25 percentage-points (~250 MCPS) of budget.",
   "benefit_grade": "L3",
   "effort": "Low code scope: FRAME is a negotiable parameter (NOT frozen core). Change BENCH_FRAME (bench_harness.h:31), TFB8_FRAME (tfb_8ch.h:33). BUT requires full bit-exact re-validation on board (goldens are FRAME-dependent, see FRAME-4) + a re-measure of g_f7_cyc_8ch_fira at the new FRAME to convert the [L3] model to [L1]. Board runs needed: 1 bit-exact re-gate + 1 cycle re-measure per FRAME value.",
   "risk": "The MCPS numbers are [L3] model, NOT measured — the O-split uncertainty means the EXACT margin at 128/256 is unconfirmed (though the DIRECTION and the FIXED-share floor are firm). C9/iron-rule-8: these FIRA benefit numbers stay [L4/待验证] for any selection/steering-commitment use until R14 is ruled CLOSED and the new-FRAME cycle is re-measured [L1]. Cheap de-risk: read the errored g_f7_cyc_analyze_fira/synth_fira split first (zero new board run, idle tail-read per F7 §7B).",
   "dimension": "frame",
   "verdict": {
    "finding_id": "FRAME-1",
    "verdict": "weakened",
    "grade_ok": true,
    "reasons": "VERIFIED CORRECT (firm): (a) FIXED-share = 10,345 cyc/frame = 2.23% from 8x56,616=452,928 vs 463,273 — matches F7_R14_RULING_MATERIAL.md:312-313 [L1] exactly. (b) MCPS model cyc(N)*fps(N)/1e6 with fps=FS/FRAME matches bench_harness.c:123-124; baseline 463,273*750/1e6=347.45 MCPS, margin 2.878x confirmed. (c) FRAME constants: BENCH_FRAME=64 (bench_harness.h:31) and TFB8_FRAME=64 (tfb_8ch.h:33, located at core_only/src/tfb_8ch.h) — both line refs correct; FRAME is negotiable, not frozen core. (d) analyze/synth split IS unmeasured (read ERROR, lines 314-321) — finding honestly flags this. (e) Direction-of-drop is CORRECT: I computed worst-case O=0 gives MCPS@128=343.58, @256=341.64, both strictly < 347.45 — FIXED amortization floor is real.\n\nBROKEN (load-bearing): The finding's quantitative BOUNDS are arithmetically inverted and collapsed. Its O=0 (\"pessimistic-for-amortization\") formula (10,345/4 + 452,928)*(48000/256)/1e6 = 85.0 MCPS divides FIXED by 4 while leaving PERCH=452,928 UNSCALED — that is algebraically the O=PERCH (all-orchestration) case, NOT O=0. At true O=0 (all-MAC, M scales x4 with frame) MCPS barely moves: @256 = 341.6 MCPS (margin 2.93x), @128 = 343.6 (margin 2.91x). I swept O in [0,PERCH]: TRUE range FRAME=256 = 86.9-341.6 MCPS (margin 2.93x-11.51x); FRAME=128 = 173.7-343.6 (margin 2.91x-5.76x). The finding's stated \"~85-90 MCPS / margin 11-11.8x\" (256) and \"~174-180 / 5.6-5.7x\" (128) are ONLY the most-OPTIMISTIC (O=PERCH) end, presented as if both ends of the range converge there. The two extremes were mislabeled and the worst-case end dropped.\n\nConsequence for benefit: \"10x REACHABLE at FRAME=256 by amortization alone\" and \"frees ~250 MCPS / 25 pts\" require O >= ~0.95*PERCH (orchestration ~95%+ of per-channel cost) — exactly the split the finding admits is UNMEASURED (lines 314-321). At worst-case O=0 only ~6 MCPS freed, margin stays 2.93x, 10x NOT reached (F7 §3c/§359 KILLED stands). So the headline benefit is conditional on an unmeasured assumption but stated as near-certain.\n\nGRADE HONEST: benefit labeled [L3 model, L1 inputs] is the right grade-name (model on measured inputs, not L4-as-L1); risk correctly keeps FIRA numbers [L4/待验证] under C9/iron-rule-8 until R14 closes + re-measure. No frozen-core/locked-decision violation. The grade is honest; the [L3] arithmetic inside it is wrong."
   }
  },
  {
   "id": "FRAME-2",
   "title": "Latency cost of larger FRAME is COMFORTABLY within the PRD spec — group delay dominated by tree structure, not block size",
   "claim": "FRAME enlargement's added latency is the block/group delay = FRAME/fs: 64=1.333ms, 128=2.667ms, 256=5.333ms. There IS a PRD latency requirement and it is NOT a blocker: end-to-end <=30ms (DEC-S2-012, relaxed from <5ms because the product is one-way playback — museum/station/PA — no lip-sync/dialogue loop). Current analytical/simulation end-to-end budget is 12.53ms (tree group delay 9.04 + DMA ping-pong 2.67 + DAC 0.75 + frac-delay 0.07). Going FRAME 64->256 adds the DMA-block term roughly +2.67ms->+5.33ms-ish on the ping-pong side (the 2.67ms ping-pong is itself FRAME-derived) i.e. on the order of +4ms worst case, landing end-to-end near ~16-17ms — still < the 30ms spec with >13ms margin. NOTE the PRD <30ms is itself LOCKED-IN-PRINCIPLE / draft pending market alignment, and 12.53ms is scipy analytical [L3], NOT board-measured (待 EZKIT 实测).",
   "evidence": [
    {
     "source": "sprint2/docs/decisions_log.md:280-290",
     "detail": "DEC-S2-012: end-to-end latency spec relaxed <5ms -> <30ms; rationale = one-way playback, no dialogue loop; 12.53ms analytical breakdown given; status LOCKED-IN-PRINCIPLE (draft, pending market alignment); closes R2"
    },
    {
     "source": "sprint2/docs/prd_update.md:183",
     "detail": "PRD table: 处理延迟 <=20ms (端到端) line; and prd_update.md:316 lists 端到端延迟 12.53ms 满足 <30ms 规格"
    },
    {
     "source": "sprint2/docs/decisions_log.md:284-285",
     "detail": "DMA ping-pong term = 2.67ms (this is the FRAME=64 block term at the 256-style block used in latency calc; doubling FRAME scales this block term), tree group delay 9.04ms is the FIXED structural cost independent of FRAME"
    },
    {
     "source": "sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:167-169",
     "detail": "dsp teammate flags larger FRAME = larger group delay FRAME/fs (64->1.33ms,128->2.67ms,256->5.33ms); 'announce/PA use may tolerate several ms'"
    }
   ],
   "benefit": "Confirms FRAME can be raised to 256 (5.33ms block delay) without breaching the <30ms PRD spec — ~13ms+ headroom remains. Removes latency as an objection to the FRAME-1 amortization win.",
   "benefit_grade": "L3",
   "effort": "None additional — this is the constraint check that GATES FRAME-1. The 12.53ms baseline and the DMA-block scaling are [L3] analytical; an EZKIT [L1] end-to-end measurement at the chosen FRAME would close the latency item (待 EZKIT, already a pending R2/PF-2 item).",
   "risk": "PRD <30ms is draft (LOCKED-IN-PRINCIPLE, pending market/customer alignment) — if a future PRD adds a hard low-latency use case (e.g. interactive/sync), the FRAME ceiling tightens. Latency numbers are [L3] analytical, not [L1] board. If steering adds its own latency (e.g. per-beam recompute), it stacks on top and must be re-budgeted against 30ms.",
   "dimension": "frame",
   "verdict": {
    "finding_id": "FRAME-2",
    "verdict": "weakened",
    "grade_ok": true,
    "reasons": "Core thesis survives but two material numbers are off. VERIFIED OK: (a) group-delay relation 64=1.333/128=2.667/256=5.333ms is verbatim at sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:167-169 and DEC-S2-012; (b) DEC-S2-012 fully confirmed at decisions_log.md:280-290 — relaxed <5ms→<30ms, one-way-playback rationale, 12.53ms scipy analytical (explicitly 非硬件实测/待 EZKIT), status LOCKED-IN-PRINCIPLE (草稿待市场对齐), closes R2, breakdown 9.04+2.67+0.75+0.07; (c) thesis \"group delay dominated by tree structure not block size\" is correct — tree group delay 9.04ms is structural/FRAME-independent (spec_change_latency.md:35 'multirate reconstruction', prd_update.md:316 '结构性延迟,与通道数无关') vs 2.67ms block term. L-GRADE HONEST: benefit labeled L3; 12.53ms explicitly tagged scipy analytical/非硬件实测/待 EZKIT; PRD flagged as draft; no L4-as-L1/L2; no frozen-core violation (FRAME explicitly negotiable subject to re-validation per task rules); no R14/C9 entanglement (this is a latency-spec gate, not FIRA-benefit-into-selection). WEAKENED ON TWO POINTS. (1) ARITHMETIC: finding says FRAME 64→256 adds '~+4ms worst case, e2e ~16-17ms, >13ms margin'. The +4ms is the SINGLE-block FRAME/fs delta (5.333-1.333). But the budget's ping-pong term is 2 FRAMES (spec_change_latency.md:36 '2帧 2.67ms 64样点/帧固定开销'); scaling 2×FRAME/fs gives 10.667ms at FRAME=256, delta +8.0ms → e2e ≈ 20.53ms, margin to 30ms ≈ 9.47ms — about half the claimed >13ms. Conclusion (<30ms) still holds but headroom is overstated ~2×. (2) SPEC DISCREPANCY: finding's claim presents '<=30ms (DEC-S2-012)' as the working PRD ceiling, yet its OWN cited evidence prd_update.md:183 still reads '延迟(处理延迟) ≤ 20ms(端到端)' — the PRD table body was never updated to the relaxed 30ms; DEC-S2-012 is a Sprint-2 patch decision, draft/LOCKED-IN-PRINCIPLE pending market alignment. At the careful FRAME=256 e2e (20.5ms) this would BREACH the un-updated ≤20ms PRD table line even though it stays under the 30ms decision. The finding leans on the more generous still-draft number without noting its own evidence carries the stricter 20ms.",
    "corrected": "FRAME 64→256 adds the DMA ping-pong term which is a 2-frame term (2.67ms@64 per spec_change_latency.md:36), so it scales as 2×FRAME/fs: +8.0ms (not +4ms) → end-to-end ≈ 20.5ms, leaving ≈ 9.5ms margin to the 30ms decision (not >13ms). FRAME=128 → e2e ≈ 15.2ms. Still passes DEC-S2-012's <30ms. CAVEAT: the live PRD table (prd_update.md:183) still specifies ≤20ms — FRAME=256's 20.5ms careful estimate would breach that un-updated table line; only the draft DEC-S2-012 30ms ceiling accommodates it. All values [L3] scipy analytical, 待 EZKIT [L1] end-to-end measurement at chosen FRAME.",
    "grade_fix": "none — L3 grade is honest; no change needed"
   }
  },
  {
   "id": "FRAME-3",
   "title": "FIRA-side memory scales with FRAME but stays within EXISTING static buffers up to FRAME=256; FRAME=512 is the hard structural ceiling (and Block-0/stack pressure is the live hazard, not theoretical)",
   "claim": "Buffers that scale with FRAME: (a) the per-segment history hist[9][62] does NOT scale (fixed at FIRA_HIST=ntaps-1=62, independent of FRAME — fira_tree.h:107); (b) the FIRA scratch s_seg_out3[FIRA_MAXWINDOW*3] and assembly s_seg_in[62+2*FIRA_MAXWINDOW] are sized by FIRA_MAXWINDOW=512 (fira_tree.c:422,438,602); (c) the analyze/synth working buffers a1[256]/r1[512]/a1p[512]/up1[512] (fira_tree.c:681-682,736-737) and the frozen-core twins (tree_filterbank.c:143-144,188-189) are sized for f0<=512. The largest FIRA window = DEC seg0 fira_window = FIRA_RATIO*f1 = FRAME (full-rate), and INT seg up to f0=FRAME; the guard `if (fira_window > FIRA_MAXWINDOW) return -3` (fira_tree.c:455) trips when FRAME>512. THEREFORE: FRAME=128 and FRAME=256 fit WITHIN all existing static buffers (no resize needed); FRAME=512 is the exact hard ceiling and FRAME>512 requires resizing FIRA_MAXWINDOW + r1/a1p/up1 + the frozen-core a1/r1 arrays (which would touch frozen tree_filterbank.c). The I/O contract G4 (input buffer >= ntaps+window-1, fira_make_channel sets nInputBuffCount = ntaps+window-1, fira_tree.c:202) scales automatically with window. The L1 Block-0 pressure precedent is REAL: the F7 stack-overflow crash (PC=0x1) happened when st8 (~37KB Tfb8State) + out8 (~2KB) as stack locals overflowed the shrunken RESERVE_EXPAND L1-Block0 stack remainder; FIX2 moved them to .bss (bench_harness.c:80-96). Larger FRAME enlarges these same structures, re-pressuring L1 Block-0.",
   "evidence": [
    {
     "source": "sprint4/dsp/fira/fira_tree.c:422,438,455,602",
     "detail": "FIRA_MAXWINDOW=512 ('largest segment output window = frame f0'); s_seg_out3[512*3]; guard return -3 if fira_window>512; s_seg_in[62+2*512]=1086 int32 ~4.3KB — sets the FRAME=512 hard ceiling"
    },
    {
     "source": "sprint4/dsp/fira/fira_tree.h:107",
     "detail": "FIRA_HIST=62 = ntaps-1, hard-coded, FRAME-INDEPENDENT — history hist[9][62] does NOT scale with FRAME (it scales with ntaps, which is frozen)"
    },
    {
     "source": "sprint4/dsp/fira/fira_tree.c:681-682,736-737",
     "detail": "analyze a1[256],a2[128],a3[64],r1[512],r2[256],r3[128]; synth a2p[256],a1p[512],up3[128],up2[256],up1[512] — r1/a1p/up1 cap at f0=512 i.e. FRAME<=512"
    },
    {
     "source": "sprint4/dsp/core_only/src/tree_filterbank.c:143-144,188-189",
     "detail": "FROZEN-core twins a1[256]/r1[512] (analyze) and a2p[256]/a1p[512]/up1[512] (synth) — same 512 cap; raising FRAME>512 would require editing the FROZEN file (not allowed)"
    },
    {
     "source": "sprint4/dsp/core_only/bench/bench_harness.c:80-96",
     "detail": "F7-FIX2: board crash PC=0x1 — st8(~37KB)+out8(~2KB) stack locals overflowed shrunken L1-Block0 RESERVE_EXPAND stack remainder; moved to .bss static. [L3/PROXY-ldf]. Live precedent that FRAME-driven buffer growth re-pressures Block-0; mitigation = #pragma section to L2/L3 (CROSS_BUILD_NOTES.md:61)"
    }
   ],
   "benefit": "FRAME=128 and FRAME=256 require ZERO buffer resizing (fit existing statics) — the FRAME-1 amortization win is achievable with no memory-layout change up to 256. This bounds the change scope and avoids touching the frozen core (which FRAME>512 would force).",
   "benefit_grade": "L3",
   "effort": "FRAME<=256: no buffer code change. Must re-check L1 Block-0 .map occupancy after raising FRAME (the .bss statics st8/out8 and per-frame s_y[FRAME*1024] grow) to confirm no link-time Block-0 overflow; if it overflows, #pragma section to L2/L3. FRAME=512+: blocked by frozen-core array sizing — do not pursue.",
   "risk": "BLOCKER-class if ignored: s_y[BENCH_FRAME*BENCH_NFR] (bench_harness.c:26) and the .bss state grow with FRAME and could re-trigger the F7 Block-0 overflow (now link-caught, not silent — IF kept static). Must verify .map L1 Block-0 occupancy on board. The Block-0 inference is [L3/PROXY-ldf], not verified against the real board .ldf. FRAME=512 is a hard ceiling set by FROZEN tree_filterbank.c arrays — cannot exceed without reopening the frozen baseline.",
   "dimension": "frame",
   "verdict": {
    "finding_id": "FRAME-3",
    "verdict": "confirmed",
    "reasons": "All cited evidence opened and verified true. (a) hist does NOT scale with FRAME: fira_tree.h:107 `#define FIRA_HIST 62` = ntaps-1, hard-coded FRAME-independent; struct hist[FIRA_SEGS_PER_CHAN=9][FIRA_HIST] (fira_tree.h:113, FIRA_SEGS_PER_CHAN=9 @:65). (b) FIRA scratch sized by FIRA_MAXWINDOW=512: fira_tree.c:422 `#define FIRA_MAXWINDOW 512u`; :438 `static int32_t s_seg_out3[FIRA_MAXWINDOW*3u]`; :602 `static int32_t s_seg_in[FIRA_HIST + 2u*FIRA_MAXWINDOW]` (=62+1024=1086 int32 ~4.3KB). (c) analyze a1[256]/r1[512] @ fira_tree.c:681-682; synth a2p[256]/a1p[512]/up1[512] @ :736-737; frozen-core twins a1[256]/r1[512] @ tree_filterbank.c:143-144 and a2p[256]/a1p[512]/up1[512] @ :188-189 — same 512 cap, and tree_filterbank.c IS in the frozen list, so FRAME>512 would force editing it (correctly barred).\n\nARITHMETIC EXACT: FIRA_RATIO=2 (fira_tree.h:66). DEC seg0 call passes window=FIRA_RATIO*f1 (fira_tree.c:697); in fira_run_segment fira_window = FIRA_RATIO*out_count = 2*(frame/2) = frame = f0 (:450). Guard `if (fira_window > FIRA_MAXWINDOW) return -3` (:455) trips precisely when FRAME>512 => FRAME=512 is the exact hard ceiling. FRAME=128 and 256 (f0=128/256 <= 512) fit r1/a1p/up1[512] with zero resize — confirmed. G4 I/O contract scales automatically: fira_tree.c:202 `nInputBuffCount = g_hb_fira_n + window - 1` (= ntaps+window-1).\n\nL1 BLOCK-0 PRECEDENT IS REAL: bench_harness.c:80-96 documents the F7 PC=0x1 crash exactly as claimed — st8(~37KB Tfb8State)+out8(~2KB) stack locals overflowed the shrunken RESERVE_EXPAND L1-Block0 stack remainder after the F7 block added ~36KB .bss (f7_fa/f7_ca); FIX2 moved them to .bss static (:96 `static Tfb8State st8`, :116 `static int32_t out8[...]`). s_y[BENCH_FRAME*BENCH_NFR] @ :26. Mitigation #pragma section to L2/L3 confirmed at CROSS_BUILD_NOTES.md:61.\n\nGRADE HONEST: benefit=L3 is correct (deductive from static array constants read from source, not measured/estimated). The Block-0 precedent is carried explicitly as `[L3/PROXY-ldf inference]` (bench_harness.c:88 uses this exact label) and the finding repeatedly states it is NOT verified against the real board .ldf — no L4/L3 dressed as L1/L2. Constraint compliance: frozen core respected (FRAME>512 barred); no R14/C9 selection-commit violation (pure headroom-scoping). Effort/risk realistic: correctly requires on-board .map L1 Block-0 occupancy check + bit-exact board re-validation for any FRAME change. Minor scope note (not a weakening): \"zero buffer resizing\" is accurate for the named FIRA/core data-path scratch arrays; the per-frame s_y and .bss state still grow with FRAME — the finding itself states this explicitly in the risk field as BLOCKER-class, so nothing is hidden.",
    "grade_ok": true
   }
  },
  {
   "id": "FRAME-4",
   "title": "Re-validation required: goldens, chirp input, and the cycle measurement are ALL FRAME-dependent — a FRAME change is a full bit-exact re-gate, not a free tuning knob",
   "claim": "Changing FRAME invalidates the entire R14 bit-exact evidence chain and requires a full re-run: (a) GOLDEN_CRC32=0x90556BC7 and GOLDEN_SPOT[64] are computed over GOLDEN_NTOTAL=65536 = 'FRAME 64 x 1024 frames' with GOLDEN_SPOT_STRIDE=1024 (golden_ref.h:23-28) — the frame-boundary subband values change when FRAME changes, so the golden MUST be regenerated; (b) CHIRP_INPUT_N=65536 = 'FRAME 64 * 1024 帧' (chirp_input.h:9) — at FRAME=256 the same 65536 samples = 256 frames, changing the frame partitioning and thus every cross-frame history boundary; (c) the per-segment cross-frame history bit-exactness (the entire F5/F4 proof: g_fira_f4_crc=0x2E0D8C6E, g_f5_pass_all=1) was proven at FRAME=64 windows (8/16/32/64) — at FRAME=128/256 the windows become 16/32/64/128 etc., and the DEC/INT decimation-phase + zero-stuff history logic must be RE-PROVEN bit-exact on board; (d) the F7 cycle number 463,273 was measured at FRAME=64 — the FRAME-1 model must be confirmed by a fresh g_f7_cyc_8ch_fira at the new FRAME to become [L1].",
   "evidence": [
    {
     "source": "sprint4/dsp/core_only/bench/golden_ref.h:23-28",
     "detail": "GOLDEN_NTOTAL=65536 '= FRAME 64 x 1024 帧'; GOLDEN_SPOT_STRIDE=1024; GOLDEN_CRC32=0x90556BC7 — golden is explicitly FRAME=64-derived"
    },
    {
     "source": "sprint4/dsp/core_only/bench/chirp_input.h:9",
     "detail": "CHIRP_INPUT_N 65536 '= FRAME 64 * 1024 帧' — same total samples re-partition into fewer/larger frames at higher FRAME, changing every frame-boundary history state"
    },
    {
     "source": "sprint4/dsp/fira/fira_tree.c:81-95",
     "detail": "fira_channel_init sets per-segment window = frame/2^level (f1=frame/2,f2=frame/4,f3=frame/8) — all 9 segment windows scale with FRAME, so the bit-exact subband regression (DEC-S4-R14-GRANULARITY) is window-specific and must re-run"
    },
    {
     "source": "sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:202-206",
     "detail": "R14 closure = (i) FIRA bit-exact vs golden + (ii) FIRA cycle measured with all overhead + true CCLK; both are FRAME=64 artifacts — a FRAME change reopens both legs"
    }
   ],
   "benefit": "Quantifies the TRUE effort of the FRAME-1 win: it is not a one-line constant edit but a full R14 re-gate (regenerate golden + chirp partition + per-subband bit-exact board run + cycle re-measure). This prevents under-costing the amortization opportunity.",
   "benefit_grade": "L1",
   "effort": "High validation effort despite low code scope: regenerate golden_ref.h via gen_golden.c at new FRAME; re-run the host bit-exact + on-board F4/F5 per-subband regression (must PASS bit-exact, tolerance 0) + F7 cycle re-measure; all must re-pass before the FRAME-1 margins can be cited [L1]. Goldens/chirp are bench files (NOT frozen), so regeneration is allowed.",
   "risk": "If the FRAME change silently breaks frame-boundary history bit-exactness and the golden is regenerated WITHOUT re-proving against the placeholder-FAIL (FG2) and telescoping-blind (FG1) gates, a false-green could pass. The per-subband golden (not e2e CRC) discipline must be preserved at the new FRAME. The decimation-phase fix (fira_tree.c:155-176) and zero-stuff history (lines 549-571) are window-pattern-specific and are the highest-risk re-validation items.",
   "dimension": "frame",
   "verdict": {
    "finding_id": "FRAME-4",
    "verdict": "weakened",
    "grade_ok": true,
    "reasons": "CORE CLAIM CONFIRMED — a FRAME change is a full R14 bit-exact re-gate, not a free tuning knob. I opened all four cited sources myself and they say exactly what is claimed:\n\n(a) golden_ref.h:23 — GOLDEN_NTOTAL=65536 \"/* FRAME 64 × 1024 帧 */\", GOLDEN_SPOT_STRIDE=1024 (:25), GOLDEN_CRC32=0x90556BC7 (:28). Confirmed structurally FRAME-dependent: gen_golden.c:74 sizes sub-band arrays sb0[FRAME/8],sb1[FRAME/4],sb2[FRAME/2],sb3[FRAME] and loops N_FRAMES=N_TOTAL/FRAME (gen_golden.c:30), so both the per-frame partitioning AND the frame count over which the CRC accumulates change with FRAME. Golden MUST be regenerated. TRUE.\n\n(b) chirp_input.h:9 — CHIRP_INPUT_N 65536 \"/* = FRAME 64 * 1024 帧 */\". Same 65536 samples re-partition into fewer/larger frames at higher FRAME, moving every frame-boundary history state. TRUE.\n\n(c) fira_tree.c:81-95 — fira_channel_init sets all 9 segment windows = frame/2,frame/4,frame/8,frame (f1/f2/f3) — every window scales with FRAME. The cited decimation-phase fix (155-176) and zero-stuff INT history (549-571, read in full) are explicitly window-pattern/phase-specific and DESKTOP-PROVEN-only; board re-proof needed. Independently corroborated by F7_R14_RULING_MATERIAL.md:161 \"the output window (8/16/32/64 samples at FRAME=64). At FRAME=128/256 the windows double/quadruple.\" TRUE.\n\n(d) F7_R14_RULING_MATERIAL.md:205-206,219 — g_f7_cyc_8ch_fira=463,273 [L1] measured at FRAME=64 (line 219 literally states \"FRAME=64\"); R14 closure = (i) bit-exact + (ii) cycle measured (:197-199). Anchors g_fira_f4_crc==0x2E0D8C6E (:21,202) and g_f5_pass_all==1 (:20,203) verified. TRUE.\n\nArithmetic: no new MCPS/margin math is asserted in the benefit; the L1 numbers it leans on (463,273; 0x2E0D8C6E; g_f5_pass_all==1; 0x90556BC7) all match the sources. benefit_grade L1 is acceptable — the conclusion is a process/governance statement derived strictly from existing L1 artifacts and documented closure rules, not a new measurement dressed up as L1. No false-green inflation. R14/C9 separation respected (benefit does not feed FIRA gain into selection).\n\nWHY WEAKENED (one real flaw, in the LESS-conservative direction): the effort field asserts \"Goldens/chirp are bench files (NOT frozen), so regeneration is allowed.\" This is FALSE. Both the scanner brief's own frozen-core list (tree_filterbank.c/tfb_8ch.c/fir_coeffs_hb63.h/golden_ref.h/chirp_input.h) AND FIRA_IMPL.md:51 红线 explicitly forbid changing golden_ref.h and chirp_input.h, with golden_ref.h annotated \"不重生成\" (do NOT regenerate). So regeneration at a new FRAME is NOT a sanctioned free action — it requires lifting a documented freeze (a CTO/critic decision), which makes the FRAME-change effort even HIGHER than the finding states. This error does not undermine the central thesis (it reinforces it: the re-gate is even costlier/more-gated than claimed); it only corrupts the permissibility framing.\n\nRisk section is realistic: it correctly insists the per-SUBBAND golden discipline (DEC-S4-R14-GRANULARITY, fira_tree.c:36-38,123-124) must be preserved over the retired telescoping-blind e2e CRC, and flags decphase (155-176) + zero-stuff (549-571) as highest-risk re-validation items — matches the code.",
    "corrected": "Effort/permissibility correction: regenerating golden_ref.h and chirp_input.h at a new FRAME is NOT \"allowed because they are bench files\" — both are on the FIRA_IMPL.md:51 红线 (do-not-change) list (golden_ref.h marked 不重生成) and on the scanner brief's own frozen-core list. A FRAME change therefore additionally requires a CTO/critic decision to lift that freeze BEFORE regeneration, on top of: re-run gen_chirp_input.c + gen_golden.c at new FRAME, re-run on-board per-SUBBAND F4 (g_fira_f4_crc) + F5 (g_f5_pass_all, 8/8) bit-exact regression with tolerance 0, AND re-measure g_f7_cyc_8ch_fira before any new-FRAME margin can be cited [L1]. Net: the FRAME-1 amortization win is even more gated than the finding states (governance freeze + board re-gate), strengthening the finding's central point that FRAME is not a free knob.",
    "grade_fix": "benefit_grade L1 is honest as-is (process conclusion grounded in existing L1 artifacts, no inflated measurement). No grade change needed. The only fix is factual, not L-grade: correct the effort field's false \"NOT frozen, regeneration allowed\" clause — both files ARE red-line frozen per FIRA_IMPL.md:51 and the scanner brief, so the work requires a freeze-lift decision first."
   }
  },
  {
   "id": "FRAME-5",
   "title": "ADI FIRA examples STRONGLY favor larger windows: every EE408V02 example uses window 256-1024, never 64 — FRAME=64 is below ADI's smallest profiled point",
   "claim": "The ADI FIRA reference examples (EE408V02) universally use windows far larger than our FRAME=64, confirming the dsp teammate's open concern (G4) that FRAME=64 may be FIRA-inefficient: Pipelined/Split_Task use BLOCK_SIZE=256 (Processing.h:13) as the FIR/FIRA window; the FIRA throughput benchmark (FIR_Throughput_21569.h) uses MAX_WINDOW_SIZE=1024 and its ParamList.dat sweeps windows {256,512,1024,2048,4096} — the SMALLEST profiled window is 256; SC57x example sizes InputBuff[MAX_TAP_LENGTH+MAX_WINDOW_SIZE-1] confirming the ntaps+window-1 input contract. FRAME=64 (our DEC seg0 full-rate window=64, and the deeper-level windows are 32/16/8) is BELOW the entire ADI-characterized range, where per-call orchestration overhead is least amortized — exactly the regime FRAME-1 escapes. Raising FRAME to 256 puts our largest window at ADI's smallest profiled point (256), aligning with the validated/benchmarked operating range.",
   "evidence": [
    {
     "source": "knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/Pipelined/src/Processing.h:13-18",
     "detail": "BLOCK_SIZE=256 (FIR window); CIRCULAR_BUFFER_LENGTH=768 >= BLOCK_SIZE+FIR_TAPS; FIR_TAPS=512; nWindowSize=BLOCK_SIZE=256 set at Processing.c:171"
    },
    {
     "source": "knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/ADSP_2156x_FIRA_Performance/src/FIR_Throughput_21569.h:15-16",
     "detail": "MAX_TAP_LENGTH=4096, MAX_WINDOW_SIZE=1024 — the 21569 FIRA throughput benchmark window ceiling"
    },
    {
     "source": "knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/ADSP_2156x_FIRA_Performance/src/ParamList.dat",
     "detail": "window sweep {256,512,1024,2048,4096} across tap-counts {1,8,32,64,256,512} — SMALLEST window profiled = 256; FRAME=64 is below the entire characterized range"
    },
    {
     "source": "sprint4/iface_survey.md:306",
     "detail": "G4 gap (verbatim): 'FRAME=64 vs example block=256/window=1024 ... 我方 FRAME=64 无对应实例 ... FRAME=64 是否过小影响 FIRA 效率待评' — the dsp survey itself flags FRAME=64 as sub-window-range and efficiency-unevaluated"
    },
    {
     "source": "knowledge_base/ezkit/bsp/app_notes/fira_accel_code/EE408V02/ADSP_SC57x_FIRA_Performance/src/FIRA_Throughput_SC573_Core1.c:24",
     "detail": "InputBuff[MAX_TAP_LENGTH+MAX_WINDOW_SIZE-1] — confirms the ntaps+window-1 input layout (G4 contract) scales with window, matching fira_make_channel:202"
    }
   ],
   "benefit": "Independent ADI-example corroboration (vendor [L2]) that FRAME=64 is below FIRA's efficient/characterized window range and FRAME=256 lands at ADI's smallest profiled point — raising confidence that the FRAME-1 amortization win is real and not a desktop artifact. Also de-risks the buffer/contract math (ntaps+window-1) since ADI uses the identical layout.",
   "benefit_grade": "L2",
   "effort": "Evidence-only (no code). Confirms FRAME=256 sits in a vendor-validated window regime, reducing the unknowns in the FRAME-1 board re-measure.",
   "risk": "ADI examples are SINGLE_RATE float FIR with large taps (512-4096), NOT our 63-tap dyadic halfband tree with software dec/int — the efficiency curve may differ. The window-256 'sweet spot' is inferred from ParamList coverage, not a measured efficiency-vs-window curve on OUR kernel; the actual FIRA cyc/sample-vs-FRAME curve for our 9-segment tree is [L4/待验证] until measured on board. Does not by itself prove the magnitude of the FRAME-1 win.",
   "dimension": "frame",
   "verdict": {
    "finding_id": "FRAME-5",
    "verdict": "weakened",
    "grade_ok": true,
    "reasons": "All five evidence items verified verbatim by opening the files myself: (1) Processing.h:13 BLOCK_SIZE=256, FIR_TAPS=512 (line 18), CIRCULAR_BUFFER_LENGTH=768 with comment \">= BLOCK_SIZE+FIR_TAPS\"; Processing.c:171 nWindowSize=BLOCK_SIZE. (2) FIR_Throughput_21569.h:15-16 MAX_TAP_LENGTH=4096, MAX_WINDOW_SIZE=1024. (3) ParamList.dat (dumped via cat -v) sweeps the inner value {256,512,1024,2048,4096} across {1,8,32,64,256,512} — smallest swept window = 256, confirmed; FIR_Throughput_21569.c:5-6 documents these as {Window,Taps} combinations. (4) SC57x FIRA_Throughput_SC573_Core1.c:24 InputBuff[MAX_TAP_LENGTH+MAX_WINDOW_SIZE-1] confirmed. (5) iface_survey.md:306 G4 text matches the paraphrase (\"FRAME=64 是否过小影响 FIRA 效率待评\").\n\nGrade is honest: benefit_grade=L2 is correctly scoped to documentary vendor corroboration (ADI never profiled below window=256), NOT a measured efficiency win. The risk section explicitly downgrades the actual cyc/sample-vs-FRAME curve for OUR 9-segment 63-tap dyadic-halfband tree to [L4/待验证] until board-measured, and flags that ADI examples are single-rate float 512-4096-tap FIR — a genuinely different efficiency regime. No L4 dressed as L2. The ntaps+window-1 contract de-risk is sound: fira_tree.c:202 sets nInputBuffCount = g_hb_fira_n + window - 1, the identical layout ADI uses. No frozen-core touch (evidence-only), FRAME is negotiable per brief, no R14/C9 injection.\n\nWEAKENED on two points. (A) Factual slip: the claim says \"our DEC seg0 full-rate window=64,\" but fira_tree.c:86 shows seg0 window[0]=f1=frame/2=32. The window=64 (=frame) is actually at segs 5 and 8 (fira_tree.c:91,94, the full-rate INT outputs). The load-bearing conclusion is unaffected — largest tree window = FRAME = 64 (segs 5,8), others are 32/16/8, all below 256 — but the seg0=64 attribution is wrong. (B) Title overclaim: \"STRONGLY favor larger windows / FRAME=64 is FIRA-inefficient\" overstates the evidence. ParamList proves only that ADI never *characterized* below 256 (absence of coverage), which is NOT a measured demonstration of inefficiency at 64. The claim body (\"may be FIRA-inefficient,\" \"BELOW the characterized range\") and the risk section are appropriately careful, so the finding stands as a valid L2 corroboration that raises confidence in FRAME-1; but the headline word \"inefficient\" should be \"uncharacterized/below ADI's profiled range.\"",
    "corrected": "Corrected benefit: ADI's EE408V02 FIRA examples never characterize windows below 256 (ParamList.dat smallest swept window=256; Pipelined BLOCK_SIZE=256 per Processing.h:13; 21569 throughput MAX_WINDOW_SIZE=1024). This is [L2] documentary evidence that our FRAME=64 sits BELOW ADI's profiled/validated window range — NOT a measurement that FRAME=64 is inefficient. Our tree's LARGEST window = FRAME = 64 at segs 5 and 8 (fira_tree.c:91,94), with deeper segments at 32/16/8 (seg0 is 32 per :86, NOT 64 as the claim states); all are below ADI's smallest profiled point. Raising FRAME to 256 would put our largest window exactly at ADI's smallest characterized point. The de-risk on the ntaps+window-1 buffer contract is solid (fira_tree.c:202 nInputBuffCount=g_hb_fira_n+window-1 == ADI InputBuff[MAX_TAP_LENGTH+MAX_WINDOW_SIZE-1]). The MAGNITUDE of any FRAME-1 amortization win remains [L4/待验证] until measured on board with our kernel — the single-rate float 512-4096-tap ADI curve does not transfer to our 63-tap dyadic halfband tree with software dec/int. Title should read \"FRAME=64 is below ADI's smallest profiled window (256)\" rather than \"FIRA-inefficient.\"",
    "grade_fix": "benefit_grade=L2 is honest and needs no change. It correctly labels documentary vendor-example corroboration (windows 256-4096 only), not a measured efficiency claim. Keep L2 for the \"FRAME=64 below ADI's characterized range\" fact and the ntaps+window-1 contract de-risk; the FRAME-1 win magnitude is already correctly carried as [L4/待验证] in the risk field. No grade inflation found."
   }
  },
  {
   "id": "HW-1",
   "title": "Offload the item-3 EQ/limiter chain to the IIR accelerator (the dominant margin threat moves OFF the core)",
   "claim": "The single largest residual-margin unknown is item-3 (post-beamform per-channel mixing/EQ/limiter), an [L4] envelope of 0-150 MCPS, explicitly up to ~250-290 MCPS for a rich 5-band+limiter x8ch at board ~30 cyc/MAC. The ADSP-21569 has a dedicated IIR accelerator (1440-word biquad coefficient memory, 1 MAC unit, runs at CCLK) that can run a per-channel biquad EQ chain entirely in hardware, taking that load OFF the SHARC+ core. A rich 5-band (5 biquad) x8ch EQ = 9.6 MMAC/s, which is <1% of the IIR accelerator's ~1 GMAC/s throughput ceiling at 1 GHz. This is the highest-value headroom move BEFORE the steering line commits, because steering adds compute on top of an already-borderline (1.38x-2.56x [L4]) residual.",
   "evidence": [
    {
     "source": "knowledge_base/ezkit/bsp/datasheets/ADSP-2156x-Datasheet-EN.pdf (pdftotext line 1156-1164)",
     "detail": "\"The infinite impulse response (IIR) accelerator consists of a 1440 word coefficient memory for storage of biquad coefficients, a data memory for storing the intermediate data, and one MAC unit... runs at the core clock frequency. The IIR accelerator can access all memory spaces and run concurrently with the other accelerators.\""
    },
    {
     "source": "sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:339",
     "detail": "Item-3 = Mixing/limiter/EQ, 0-150 MCPS (0-15%), [L4], \"the DOMINANT uncertainty\"; NB at board ~30 cyc/MAC a rich 5-band+limiter x8 reaches ~250-290 MCPS (>150)."
    },
    {
     "source": "sprint4/dsp/fira/F7_MARGIN_MATERIAL.md:339-355",
     "detail": "residual whole-system margin ~1.38x (worst) to 2.56x (best) [L4]; \"The dominant swing is item 3 (mixing/EQ/limiter, 0-150 MCPS)\"."
    },
    {
     "source": "sprint2/docs/decisions_log.md:234",
     "detail": "board cycle-efficiency ~30-50 cycle/MAC (the figure used to derive item-3's 250-290 MCPS upper envelope)."
    }
   ],
   "benefit": "Removes item-3 from the CORE demand denominator. Worst-case core demand drops from 347.45+290 = 637.45 MCPS (margin 1.569x) back toward 347.45 MCPS (margin 2.878x). Even nominal item-3=150 case improves 2.010x -> 2.878x. Net core headroom recovered = up to ~290 MCPS / ~217,000 cyc/frame, freed for the steering line. Derivation: 5 biquad x 5 MAC x 8ch x 48kHz x 30 cyc/MAC = 288 MCPS [L4 envelope]; offloaded core cost ~ IIR setup/QueueTask only.",
   "benefit_grade": "L4",
   "effort": "Moderate. Item-3 is NOT yet spec'd (PRD/algorithm-definition input per F7_R14_RULING_MATERIAL.md:383-384,398) -- so this is an architecture recommendation to bind the EQ chain to the IIR accel at spec time, not a code change to the frozen FIRA core. Needs: adi_iir SHARC header (adi_iir_2156x.h is MISSING on this host per iface_survey.md:318) acquired on bench, IIR driver bring-up, board re-measure of concurrent FIR+IIR cycle cost. No frozen-core file touched (EQ is a NEW post-beamform stage). One+ board run.",
   "risk": "(1) Item-3 is [L4] -- if PRD defines NO EQ/limiter (pure beamform pass-through, DOC-S4-IO-01 currently direct-in-direct-out), the threat is 0 and the offload is unneeded; benefit only realizes if/when a rich EQ is added. (2) IIR accel is signed-fractional/format-sensitive like FIRA R14-3 was -- bit-exactness must be board-validated, not assumed. (3) Concurrent FIR+IIR memory-bus arbitration could add cycles (see HW-2). C9/iron-rule-8: this is a FIRA/accelerator benefit -- must be tagged [L4/待验证] and NOT counted into selection/承诺 until board-measured.",
   "notes": "This directly answers the dimension's KEY QUESTION. The IIR accel is purpose-built for exactly this (biquad coeff memory). adi_iir driver existence is a gap (G8 in iface_survey.md flags FIR-vs-FIR+IIR route undecided; example Pipelined uses FIR(512tap)+5-band IIR + float, proving the FIR+IIR concurrent pattern is an ADI-supported topology).",
   "dimension": "hardware",
   "verdict": {
    "finding_id": "HW-1",
    "verdict": "confirmed",
    "grade_ok": true,
    "reasons": "I opened every cited source. DATASHEET: ADSP-2156x-Datasheet-EN.pdf lines 1998-2004 (pdftotext) verbatim confirm the IIR accelerator quote: \"1440 word coefficient memory for storage of biquad coefficients... one MAC unit... runs at the core clock frequency... run concurrently with the other accelerators.\" The finding's quote is accurate (the cited line range 1156-1164 differs from my extraction's 1998-2004 — pagination/extractor variance — but the text is real and exact). FIR accel (4 MAC, 1024-word) sits adjacent and \"can run concurrently with the IIR accelerator\" (line 1995), which substantiates the FIR+IIR concurrent topology claim. ITEM-3 framing: F7_R14_RULING_MATERIAL.md:339 confirms item-3 = Mixing/limiter/EQ, 0-150 MCPS [L4], \"the DOMINANT uncertainty,\" with the explicit NB that at ~30 cyc/MAC a rich 5-band+limiter x8 reaches ~250-290 MCPS. MARGIN BAND: 1.38x(worst)/2.56x(best) [L4] confirmed at F7_R14_RULING_MATERIAL.md:349-354 (derived 1000/390.2 and 1000/726.2). decisions_log.md:234 confirms ~30-50 cyc/MAC board efficiency. ARITHMETIC (all re-derived, all match): 288 MCPS = 5biquad x 5MAC x 8ch x 48000 x 30; 9.6 MMAC/s = 5x5x8x48000 (=0.96% of the 1 MAC @1GHz ~1 GMAC/s IIR ceiling, so \"<1%\" is correct); L1 baseline 463,273 cyc/frame -> 347.45 MCPS -> 2.878x confirmed verbatim at F7_R14_RULING_MATERIAL.md:15,39-42; margin recovery 347.45+290=637.45->1.569x and 347.45+150=497.45->2.010x match the benefit's stated 1.569x/2.010x->2.878x exactly. L-GRADE HONEST: benefit_grade=L4 correctly inherits item-3's [L4]; risk section explicitly binds C9/iron-rule-8 ([L4/待验证], NOT into selection/承诺 until board-measured) — no L4-dressed-as-L1/L2. FROZEN CORE: no violation — EQ is genuinely a NEW post-beamform stage; none of tree_filterbank.c/tfb_8ch.c/fir_coeffs_hb63.h/golden_ref.h/chirp_input.h is touched; this is an architecture-binding recommendation at spec time, not a core code change. EFFORT REALISTIC: iface_survey.md:15,318 confirm adi_iir_2156x.h is MISSING on this host (genuine gap, needs bench acquisition); G8 (iface_survey.md:310) confirms FIR-vs-FIR+IIR route is UNDECIDED and the Pipelined example uses FIR(512tap)+5-band IIR (float, c:535-557), so the concurrent FIR+IIR pattern is an ADI-supported topology as claimed; risk correctly flags bit-exactness must be board-validated and concurrent-bus arbitration (HW-2) as open. WEAKNESSES FOUND but do not break the core claim: (a) evidence entry #3 mis-attributes the 1.38x-2.56x band + \"dominant swing is item 3\" to F7_MARGIN_MATERIAL.md:339-355 — those numbers/quote actually live in F7_R14_RULING_MATERIAL.md:349-355; F7_MARGIN_MATERIAL.md does not contain 347.45 or the band (grep returned nothing). Wrong file pointer, true fact. (b) The threat is CONDITIONAL: DOC-S4-IO-01 is currently direct-in-direct-out with NO EQ/limiter named (F7_R14_RULING_MATERIAL.md:339), so item-3 may legitimately be 0 and the offload then has zero benefit — the finding discloses this in its own risk(1), so \"highest-value headroom move\" is aspirational, not guaranteed. Both are disclosed/minor; the technical core (IIR accel can host an off-core biquad EQ chain, freeing up to ~290 MCPS if a rich EQ is ever spec'd, must remain [L4/待验证] under C9) is sound and correctly graded."
   }
  },
  {
   "id": "HW-2",
   "title": "Concurrent FIR + IIR accelerator operation at 1 GHz is datasheet-confirmed (FIRA beamform + IIR EQ run in parallel, both off-core)",
   "claim": "The datasheet explicitly states the FIR accelerator \"can run concurrently with the IIR accelerator\" and both \"run at the core clock frequency.\" They are integrated via a dedicated SHARC fabric that gives the accelerators direct, reduced-latency access to SHARC L1 memory WITHOUT going through the main system fabric, arbitrated against the core's completer ports. This means the existing 8ch FIRA halfband beamform chain and a future per-channel IIR EQ chain can execute in parallel hardware, both offloaded from the SHARC+ core, at 1 GHz.",
   "evidence": [
    {
     "source": "ADSP-2156x-Datasheet-EN.pdf (pdftotext line 1150-1153)",
     "detail": "\"The FIR accelerator runs at the core clock frequency. The FIR accelerator can access all memory spaces and can run concurrently with the IIR accelerator on the processor.\""
    },
    {
     "source": "ADSP-2156x-Datasheet-EN.pdf (pdftotext line 615-623)",
     "detail": "\"The FIR/IIR accelerators ... are integrated closely with the SHARC+ core with the help of a dedicated SHARC fabric and run at CCLK speed. This allows the FIR/IIR accelerator requester ports to directly access the SHARC L1 memory with reduced latency, as these accesses do not go through the main system fabric. These accesses are arbitrated between both the SHARC+ core completer ports.\""
    },
    {
     "source": "ADSP-2156x-Datasheet-EN.pdf (pdftotext line 1166-1171)",
     "detail": "FIR/IIR accelerators support \"dynamic queuing of unlimited FIR/IIR channels, selective interrupt generation for each channel, and trigger requester/completer support.\""
    }
   ],
   "benefit": "Enables HW-1's benefit to be realized WITHOUT serializing FIR-then-IIR on the core timeline -- the EQ stage overlaps the beamform stage in hardware. Qualitatively: the up-to-290 MCPS EQ cost and the 347.45 MCPS FIRA cost do not stack on the core's single timeline; both are accelerator-resident.",
   "benefit_grade": "L2",
   "effort": "Low to characterize (datasheet-confirmed capability). Realizing it needs the IIR bring-up of HW-1 plus a board measurement of whether L1 memory-bus arbitration between concurrent FIR+IIR+core adds cycles in practice (datasheet says 'arbitrated' -- contention is possible but unquantified). 1 board run to measure concurrent-mode cycle cost.",
   "risk": "\"Concurrently\" is a capability statement, not a zero-contention guarantee -- the SHARC fabric arbitrates accelerator and core completer-port accesses to L1, so real concurrent throughput must be board-measured (not [L1] until then). Does not interact with the frozen core code; it is an orchestration/topology property.",
   "notes": "This is the enabling fact for HW-1. The 'unlimited channels / selective per-channel interrupt' feature is also the lever for HW-3 (reducing per-segment orchestration overhead via multichannel/queued tasks).",
   "dimension": "hardware",
   "verdict": {
    "finding_id": "HW-2",
    "verdict": "weakened",
    "grade_ok": true,
    "reasons": "CORE CLAIM CONFIRMED. All three datasheet quotes verified verbatim in ADSP-2156x-Datasheet-EN.pdf (I ran pdftotext myself): (a) \"The FIR accelerator runs at the core clock frequency. The FIR accelerator can access all memory spaces and can run concurrently with the IIR accelerator on the processor\" (my extraction line ~1995; IIR section symmetric ~2003); (b) \"integrated closely with the SHARC+ core with the help of a dedicated SHARC fabric and run at CCLK speed... directly access the SHARC L1 memory with reduced latency, as these accesses do not go through the main system fabric. These accesses are arbitrated between both the SHARC+ core completer ports\" (my line 990-993); (c) \"dynamic queuing of unlimited FIR/IIR channels, selective interrupt generation for each channel, and trigger requester/completer support\" (my line 2007-2009). The cited line numbers (1150-1153/615-623/1166-1171) don't match my pdftotext numbering, but the quoted STRINGS are exact and present — benign extraction-tool line-numbering difference, not fabrication. Datasheet gives NO quantified concurrent-throughput or zero-contention guarantee (grep for contention/bandwidth/stall near accel section found nothing relevant) — finding correctly hedges this.\n\nBASELINE ARITHMETIC anchors verified: 463,273 cyc/frame, 347.45 MCPS, 2.878x margin, 250-290 MCPS EQ envelope all present in-repo (F7_CLOSING_RECORDS.md:38,162; F7_R14_RULING_MATERIAL.md:368-369). EQ figure is correctly carried as [L4] envelope, not a measured cost.\n\nWHY WEAKENED (benefit overstated): The headline benefit — \"the up-to-290 MCPS EQ cost and the 347.45 MCPS FIRA cost do not stack on the core's single timeline; both are accelerator-resident\" — overstates. The 347.45 MCPS FIRA path INCLUDES substantial CORE-RESIDENT orchestration (CreateTask/FixedPointEnable/QueueTask/spin-on-done/postscale/cache-invalidate per segment), confirmed by FIRA_IMPL.md:32-33 (lifecycle is core-side calls) and F7_CLOSING_RECORDS.md:120-122 which states the orchestration-vs-MAC split inside the path \"CANNOT [be determined], without more data\" — it is UNMEASURED. A future IIR EQ chain needs its OWN per-channel core-side lifecycle orchestration (same Open/CreateTask/QueueTask/spin model). So only the MAC compute overlaps off-core; the orchestration fractions of BOTH stack on the single core timeline, and the L1 bus is \"arbitrated\" (datasheet) so even MAC portions contend. The finding does separately hedge (\"arbitrated -- contention possible but unquantified\", \"must be board-measured\", benefit graded L2 not L1), but the benefit sentence itself implies the ENTIRE 347.45 stays off-core, which the repo's own unmeasured-split caveat contradicts.\n\nGRADE HONEST: benefit graded [L2] (datasheet capability), explicitly \"not [L1] until board-measured.\" No L4-as-L2/L1 dressing. CONSTRAINTS: no frozen-core touch; does NOT violate C9/R14 (decisions_log:258, critic SKILL.md:1086) — this is a datasheet hardware-topology capability, not a quantified FIRA-offload compute benefit fed into selection/tape-out/commitment, and chip ADSP-21569 is already LOCKED, so R14's offload-benefit-into-selection gate is not tripped. EFFORT/RISK realistic: names HW-1 IIR bring-up dependency + a board run to measure concurrent-mode arbitration cost.",
    "corrected": "Corrected benefit: The datasheet confirms FIR and IIR accelerators CAN run concurrently at CCLK via a dedicated L1-access SHARC fabric, so the MAC-compute portions of an 8ch FIRA beamform chain and a future per-channel IIR EQ chain CAN overlap in hardware rather than serializing their MACs on the core. HOWEVER, this does NOT mean \"the 290 MCPS EQ cost and the 347.45 MCPS FIRA cost do not stack on the core timeline.\" The 347.45 MCPS FIRA figure includes core-resident per-segment orchestration (CreateTask/QueueTask/spin/postscale/cache mgmt), and the orchestration-vs-MAC split is currently UNMEASURED (F7_CLOSING_RECORDS.md:120). A future IIR EQ adds its own core-side orchestration. Therefore: (1) accelerator MAC work overlaps off-core [datasheet L2]; (2) the core-orchestration fractions of BOTH chains still stack on the single core timeline [unmeasured]; (3) L1 access is arbitrated, so concurrent throughput (including contention/stall on shared L1 between FIR+IIR+core completer ports) must be board-measured before any quantified overlap saving is claimed [not L1 until then]. The enabling-fact and capability claim stand; the quantitative \"do not stack\" framing should be narrowed to \"MAC compute overlaps; core orchestration of both still stacks; net concurrent cost is board-TBD.\"",
    "grade_fix": "No grade change needed — benefit [L2] is honest (datasheet capability, explicitly deferred to board for the realized/quantified portion). The fix is to the benefit WORDING, not the L-grade: replace \"both are accelerator-resident / costs do not stack on the core timeline\" with \"MAC compute overlaps off-core; per-channel orchestration of both chains still consumes core timeline (unmeasured split, F7_CLOSING_RECORDS.md:120); concurrent net cost incl. arbitrated-L1 contention is board-TBD.\""
   }
  },
  {
   "id": "HW-3",
   "title": "Per-segment FIRA orchestration is flat per-channel (no cross-channel amortization) -- multichannel CreateTask / channel-grouping could cut the 72 per-frame invocation overheads",
   "claim": "Board measurement shows per-channel FIRA cost is FLAT: 8 x 1ch_fira (8 x 56,616 = 452,928) vs measured 8ch (463,273) => per-frame fixed share is only 10,345 cyc = 2.23%. The current 8ch path makes 72 (8ch x 9 segment) serial QueueTask invocations, each paying its OWN CreateTask + FixedPointEnable + QueueTask + spin-on-done + postscale + cache-invalidate -- there is NO shared per-frame orchestration being amortized across channels. The datasheet's 'dynamic queuing of unlimited channels' + multichannel CreateTask (adi_fir_CreateTask takes a CHANNEL_INFO[] array, nNumChannels) means same-level channels could be grouped into one task, amortizing the per-invocation fixed cost. The current code uses a STRICT serial single-handle discipline ([ASSUME-A1]) explicitly because grouping was deferred to bench.",
   "evidence": [
    {
     "source": "sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:312-313",
     "detail": "\"g_f7_cyc_1ch_fira = 56,616 [L1] -> 8 x 56,616 = 452,928 vs 463,273 -> per-frame fixed share = 10,345 cyc = 2.23% (consistent, flat per-channel cost).\""
    },
    {
     "source": "sprint4/dsp/fira/fira_regression.c:276-283",
     "detail": "[ASSUME-A1]: \"8ch x 9seg = 72 QueueTask all run on the SINGLE shared FIRA handle... STRICT SINGLE-THREADED SERIAL discipline... If task grouping / concurrency is ever introduced this [ASSUME-A1] breaks and per-task scratch is required.\""
    },
    {
     "source": "sprint4/iface_survey.md:105,107",
     "detail": "adi_fir_CreateTask(hDev, *ADI_FIR_CHANNEL_INFO[], nNumChannels, ...) -- takes a channel ARRAY; example FIR_Multi_Channel_Processing.c builds multi-channel CHANNEL_INFO[]."
    },
    {
     "source": "sprint4/dsp/fira/fira_tree.c:396-481",
     "detail": "fira_run_segment: one halfband segment = full adi_fir lifecycle (CreateTask + FixedPointEnable + QueueTask + spin until FIRTaskDoneCount<1 + postscale + flush_data_buffer invalidate) -- paid once PER segment."
    }
   ],
   "benefit": "Upper bound is modest: the per-frame fixed share is only 2.23% (10,345 cyc/frame). Grouping same-level channels reduces the count of CreateTask/spin/cache-invalidate cycles paid; realistic recovery is a fraction of that 2.23% plus reduced spin-idle (the core spins on g_FIRTaskDoneCount per segment -- 72 spins/frame). Order ~single-digit-thousands cyc/frame. Small vs HW-1, but it is core-resident and steering-multiplied (more segments per added beam).",
   "benefit_grade": "L1",
   "effort": "Higher and FROZEN-CORE-ADJACENT. Grouping breaks [ASSUME-A1] -> requires PER-TASK scratch (not shared s_seg_in/s_seg_out3/s_taskMem) and re-validation of bit-exactness (crc==0x90556BC7, 8/8 per-channel subband). fira_tree.c / tfb_8ch.c orchestration is NOT in the frozen list, but the change is intricate and the bit-exact gate must be fully re-passed on board. Multiple board runs.",
   "risk": "Bit-exactness is the gate: concurrent/grouped tasks change scratch lifetime and cache-coherence windows (the carefully-reasoned single-writer/single-reader invariant in fira_tree.c:434-500 would be invalidated). High regression risk for a 2.23%-ceiling reward. Recommend deprioritize vs HW-1/HW-2 unless steering's added segment count makes the 72->more invocation overhead material.",
   "notes": "The 2.23% flat-cost finding also means 16ch scales ~linearly (no free amortization) -- relevant input for steering's compute budget, independent of whether grouping is pursued.",
   "dimension": "hardware",
   "verdict": {
    "finding_id": "HW-3",
    "verdict": "weakened",
    "reasons": "All four evidence anchors verified by opening the files myself; every factual claim holds, the only issue is a benefit_grade mislabel. (1) F7_R14_RULING_MATERIAL.md:312-313 quote is verbatim and exact: g_f7_cyc_1ch_fira=56,616 [L1], 8x56,616=452,928 vs measured 463,273. I re-derived the arithmetic independently: 463,273-452,928=10,345 = 2.233% of 463,273. Correct to the digit. (2) fira_regression.c:276-283 [ASSUME-A1] confirmed verbatim: 8ch x 9seg = 72 QueueTask on the SINGLE shared s_hFir under STRICT SINGLE-THREADED SERIAL discipline; explicitly states that introducing task grouping/concurrency breaks A1 and requires per-task scratch. (3) iface_survey.md:105,107 confirmed: adi_fir_CreateTask(hDev,*ADI_FIR_CHANNEL_INFO[],nNumChannels,...) takes a channel ARRAY; FIR_Multi_Channel_Processing.c builds multi-channel CHANNEL_INFO[]. So multichannel grouping is a real API affordance. (4) fira_tree.c:396-505 confirmed: fira_run_segment pays the full lifecycle once PER segment (CreateTask line 472, FixedPointEnable 476, QueueTask+spin 479-481, postscale, flush_data_buffer cache-invalidate 483-505), on shared static s_seg_out3/s_taskMem; the single-writer(FIRA DMA)/single-reader(postscale) cache invariant at 434-505 is exactly as claimed and would be invalidated by grouping. The 9-segment count is confirmed: 9 fira_run_segment_stateful call-sites seg 0-8 (fira_tree.c:697-766), and F5_F7_PLAN.md:33 states '8ch x 9 seg = 72 串行 QueueTask'. Constraint checks pass: frozen redline (FIRA_IMPL.md:51) is tree_filterbank.{c,h}/golden_ref.h/chirp_input.h/fir_coeffs -- NOT fira_tree.c or tfb_8ch.c, so the finding correctly says those orchestration files are non-frozen. No C9/R14 violation: the finding proposes no selection/commit benefit and recommends deprioritization, so iron-rule-8 is not engaged. WHY WEAKENED (not confirmed): benefit_grade='L1' is misapplied. The 10,345 cyc / 2.23% is genuinely L1-measured, BUT it is the per-frame FIXED share -- the part that by definition does NOT scale per channel and is therefore NOT what grouping recovers. The per-segment overheads grouping would amortize (CreateTask/FixedPointEnable/spin/cache-invalidate, x72) live inside the flat per-channel 56,616 cyc, NOT in the 10,345 fixed share (F7_R14_RULING_MATERIAL.md:284: flat per-channel => 'NO shared per-frame fixed share'). The finding's own benefit text correctly hedges the recovery as 'a fraction of that 2.23% plus reduced spin-idle... Order ~single-digit-thousands cyc/frame' -- that recovery figure is an UNMEASURED [L4/待验证] estimate, not L1. So the L1 grade is honest for the cited measurement but is attached to a benefit (recoverable savings) that is L4. The 'ceiling' framing is also slightly off (and conservative): the true theoretical ceiling is the per-segment fixed overhead inside the 56,616, which exceeds 10,345, so 2.23% understates the target while the recovery estimate remains L4. Effort/risk assessment is realistic: grouping breaks A1, needs per-task scratch, invalidates the cache invariant, and requires full board re-validation of bit-exactness (per-channel subband CRC) -- multiple board runs, correctly flagged as deprioritize-vs-HW-1. The 16ch ~linear-scaling note is sound (no free amortization since per-channel cost is flat).",
    "grade_ok": false,
    "grade_fix": "Split the grade: the measured fixed-share figure (10,345 cyc = 2.23%, from 56,616x8 vs 463,273) is correctly [L1]. But the PROPOSED BENEFIT of grouping (recoverable cycles) is an unmeasured estimate and must carry benefit_grade=[L4/待验证], NOT L1. Restate benefit as: '[L4/待验证] estimate: grouping amortizes per-segment CreateTask/FixedPointEnable/spin/cache-invalidate overheads that currently sit inside the flat per-channel 56,616 cyc (not inside the 10,345 fixed share); order ~single-digit-thousands cyc/frame, requires board measurement of a grouped prototype to grade L1.'",
    "corrected": "[L1] per-frame fixed share = 10,345 cyc = 2.23% (8 x 56,616 = 452,928 vs measured 463,273) -- a flat-per-channel/no-amortization MEASUREMENT, correctly L1. [L4/待验证] grouping recovery: amortizing the 72 per-segment fixed overheads (which reside in the per-channel 56,616, not in the 10,345 fixed share); estimated order ~single-digit-thousands cyc/frame, UNMEASURED until a grouped prototype runs on board. Headroom context: 10,345 cyc is ~1.19% of the 870,060 cyc/frame realtime headroom (1,333,333 budget @750fps/1GHz - 463,273). Recommendation stands: deprioritize vs HW-1/HW-2 unless steering's added segment count makes the 72->more invocation overhead material. No frozen-core or C9 violation."
   }
  },
  {
   "id": "HW-4",
   "title": "Descriptor-chained DMA + Trigger Routing Unit (TRU) can chain accelerator/SPORT I/O without core spin",
   "claim": "The ADSP-21569 supports descriptor-based DMA where multiple sequences chain together (one channel auto-starts the next on completion), and a Trigger Routing Unit (TRU) that provides 'system-level sequence control without core intervention,' explicitly able to 'automatically trigger the start of a DMA sequence after a sequence from another DMA channel completes.' Today the FIRA path spins the core on g_FIRTaskDoneCount per segment (72 spins/frame) and the SPORT audio I/O already uses ping-pong PDMA descriptor lists. TRU + descriptor chaining is the hardware path to move FIRA-segment I/O sequencing and SPORT-to-memory staging off the core's spin-wait timeline.",
   "evidence": [
    {
     "source": "ADSP-2156x-Datasheet-EN.pdf (pdftotext line 768-776)",
     "detail": "\"Descriptor-based DMA transfers allow multiple DMA sequences to be chained together. Program a DMA channel to set up and start another DMA transfer automatically after the current sequence completes.\""
    },
    {
     "source": "ADSP-2156x-Datasheet-EN.pdf (pdftotext line 796-806)",
     "detail": "TRU \"provides system-level sequence control without core intervention... Automatically triggering the start of a DMA sequence after a sequence from another DMA channel completes\", plus software triggering and synchronization of concurrent activities."
    },
    {
     "source": "sprint4/iface_survey.md:205-213",
     "detail": "SPORT audio I/O already runs on ADI_PDMA_DESC_LIST ping-pong descriptor chains (pNxtDscp ring); \"SPORT 经 adi_sport_DMATransfer 直接驱动 PDMA, 无需单独调 adi_dma.\""
    },
    {
     "source": "sprint4/dsp/fira/fira_tree.c:481",
     "detail": "current per-segment core spin: \"while (g_FIRTaskDoneCount < 1u) { /* spin */ }\" -- 72 such spins per 8ch frame."
    }
   ],
   "benefit": "Reclaims core cycles currently lost to per-segment spin-wait (72 spins/frame) and to per-block DMA-buffer management (item-1 = 5-30 MCPS [L3], item-2 interrupts 2-15 MCPS [L3]). If FIRA segment completion can trigger the next via TRU/chained DMA instead of core polling, the core is free during accelerator execution. Quantitative recovery bounded by item-1+item-2 (~7-45 MCPS [L3]) plus spin-idle reclaim.",
   "benefit_grade": "L3",
   "effort": "Moderate-high; orchestration only (no frozen-core edit). The FIRA legacy callback model currently increments a counter the core polls; converting to TRU-triggered chaining needs driver-level rework + board validation that completion ordering and cache-coherence (the flush_data_buffer invalidate windows) still hold. Bit-exact re-validation required. Multiple board runs.",
   "risk": "Cache-coherence: the current code relies on a precise post-DMA invalidate ordered against the spin completion (fira_tree.c:485-500). TRU-driven chaining changes WHEN the invalidate must fire relative to FIRA writeback -- mis-ordering reintroduces the flush-back hazard (a documented DSP/FIRA IO-contract gate). Benefit is [L3] (cycle costs estimated, not board-measured). Interacts with steering only insofar as steering adds segments (more spins to reclaim).",
   "notes": "Lower priority than HW-1; this is a polish/efficiency lever. The bigger structural win (HW-1/HW-2) should land first since item-3 dwarfs item-1/2.",
   "dimension": "hardware",
   "verdict": {
    "finding_id": "HW-4",
    "verdict": "weakened",
    "grade_ok": true,
    "reasons": "CLAIM AND EVIDENCE VERIFIED. All four cited sources check out when opened directly: (1) Datasheet quotes are VERBATIM and not cherry-picked. I converted ADSP-2156x-Datasheet-EN.pdf myself; \"Descriptor-based DMA transfers allow multiple DMA sequences to be chained together. Program a DMA channel to set up and start another DMA transfer automatically after the current sequence completes\" appears at /tmp text lines 1332-1334; TRU \"provides system-level sequence control without core intervention\" (line 1397-1398) and \"Automatically triggering the start of a DMA sequence after a sequence from another DMA channel completes\" (line 1408-1409). I read the full surrounding paragraphs (lines 1325-1415) — no mischaracterization. (The finding's \"pdftotext line 768-776/796-806\" do not match my conversion's line numbers, a layout-mode difference, but the TEXT is exact.) (2) iface_survey.md:205-213 confirms SPORT runs on ADI_PDMA_DESC_LIST ping-pong descriptor chains and \"SPORT 经 adi_sport_DMATransfer 直接驱动 PDMA, 无需单独调 adi_dma\" verbatim. (3) fira_tree.c:481 \"while (g_FIRTaskDoneCount < 1u) { /* spin */ }\" verbatim; the cache-coherence risk (fira_tree.c:483-509, A5 HARD GATE) is real and exactly as the risk field describes — the post-DMA flush_data_buffer invalidate is precisely ordered against spin completion, so TRU-driven reordering genuinely risks the flush-back hazard. (4) \"72 spins/frame\" corroborated: F7_R14_RULING_MATERIAL.md:15 states \"72+24 segments\" and F7_CLOSING_RECORDS.md:121 states 56,616 lumps \"per channel, 9 FIRA segments\" => 8ch x 9 = 72 main segments (total invocations 72+24=96; the 72 framing is main-segment-only, minor imprecision, not misleading).\n\nARITHMETIC VERIFIED. Benefit cites item-1 = 5-30 MCPS [L3] and item-2 = 2-15 MCPS [L3], summing to ~7-45 MCPS. Both match the source exactly: F7_R14_RULING_MATERIAL.md:337 (Codec/I/O DMA 5-30 MCPS, \"[L3] structure [L2/ADI example], cycle cost engineering-estimated\") and :338 (System interrupts 2-15 MCPS, \"[L3] cadence [L2], per-ISR cost estimated\"). Sum 7-45 is correct. L1 baseline anchors (463,273 cyc/frame, 56,616 1ch, 10,345=2.23% fixed share, 347.45 MCPS, 2.878x margin) all confirmed against F7_CLOSING_RECORDS.md:37-45,114,162.\n\nNO CONSTRAINT VIOLATION. Orchestration/driver-level only — does not touch any frozen-core file (tree_filterbank.c/tfb_8ch.c/fir_coeffs_hb63.h/golden_ref.h/chirp_input.h). Does not fold FIRA speedup into selection/flow/commitment, so no R14/C9 separation breach — it reclaims core cycles within an already-measured path. Effort/risk realistic: explicitly states bit-exact re-validation + multiple board runs needed, and the cache-coherence reordering hazard is the genuine technical risk.\n\nWHY WEAKENED (benefit magnitude over-stated, claim itself sound): The recovery is framed as \"bounded by item-1+item-2 (~7-45 MCPS) plus spin-idle reclaim,\" which is an optimistic CEILING that TRU cannot fully deliver. (a) item-1/item-2 per the source (:337-338) are the per-block callback + descriptor/pointer mgmt + cache-invalidate + frame-ISR costs; TRU offloads the SEQUENCING/triggering of these but the cache-invalidate before the core reads DMA output does NOT vanish (it is the very hazard the risk field flags) and the per-block callback work remains — so only a fraction of 7-45 MCPS is actually reclaimable, not the whole envelope. (b) The \"spin-idle reclaim\" term is near-zero on the current bare-metal free-run bench (bench_main.c plain main+idle loop, :338): the 463,273 cyc/frame ALREADY counts the spin cycles, and the core has no other work during the spin, so reclaiming spin time yields usable MCPS ONLY if steering adds concurrent work to overlap. The finding correctly hedges (\"bounded by\", \"interacts with steering only insofar as steering adds segments\") but leads the benefit with reclaim as if it were free additive MCPS. CORRECTED BENEFIT below.",
    "corrected": "Mechanism CONFIRMED: TRU + descriptor-chained DMA is a genuine ADSP-21569 capability (datasheet verified) that can sequence FIRA-segment I/O and SPORT-to-memory staging without core polling, and the 72-spin-per-frame poll model + ping-pong PDMA chains are real in-repo. But the recoverable benefit is a FRACTION of the cited 7-45 MCPS [L3] ceiling, not the full envelope: (1) the per-segment cache-invalidate before postscale read (fira_tree.c:483-509) must still fire and cannot be offloaded — it is in fact the dominant correctness risk of doing this; (2) the per-block callback/buffer work inside item-1/item-2 does not disappear, only its triggering does; (3) \"spin-idle reclaim\" yields usable headroom only once the steering line adds concurrent core work to overlap the accelerator window — on today's bare-metal free-run bench those spin cycles are already idle, so reclaiming them is zero net MCPS until there is competing work. Honest statement: this is a polish/efficiency lever whose realized recovery is unquantified [L3] and likely well under the 45 MCPS top of range; it becomes meaningfully valuable specifically when steering adds segments/parallel work to fill the freed spin windows. Keep benefit_grade [L3], keep \"lower priority than HW-1/HW-2\" (item-3 EQ/limiter 0-150 MCPS [L4] dwarfs item-1/2). All L-grades honest; no frozen-core/R14/C9 violation.",
    "grade_fix": "No grade fix needed. benefit_grade [L3] is honest and matches the source grades of item-1 (F7_R14_RULING_MATERIAL.md:337, [L3]) and item-2 (:338, [L3]). Datasheet evidence is correctly treated as [L2] vendor doc, not dressed as L1/measured. The finding explicitly states \"Benefit is [L3] (cycle costs estimated, not board-measured)\" — no L4-as-L2/L1 inflation, no measured-claim overreach. The only adjustment is to the benefit MAGNITUDE/framing (over-stated ceiling, double-counted already-idle spin cycles), not to the L-grade."
   }
  },
  {
   "id": "HW-6",
   "title": "Idle hardware inventory: ASRC (2x4), PCG (2x2), S/PDIF, SIMD PEy, crypto/PKA -- mostly NOT mappable to our chain (documented exclusions)",
   "claim": "Full offload-resource inventory with page cites. Beyond FIR/IIR accel and DMA/TRU (HW-1..4), the ADSP-21569 has: 2x4 ASRC (8 ASRC blocks, sample-rate conversion 'without using internal processor resources'), 2x2 Precision Clock Generators, 2x1 S/PDIF Rx/Tx, SIMD dual processing elements (PEx/PEy), and crypto/PKA accelerators. NONE of these maps to compute-headroom for our beamform/EQ chain in a way the chain can use: our path is a fixed 48 kHz synchronous TDM direct-in/direct-out (no rate conversion, no S/PDIF, no crypto), and SIMD PEy lives inside the frozen core (tree_filterbank.c may not be touched).",
   "evidence": [
    {
     "source": "ADSP-2156x-Datasheet-EN.pdf (pdftotext line 953-962)",
     "detail": "ASRC: \"contains eight ASRC blocks... performs synchronous or asynchronous sample rate conversion across independent stereo channels, without using internal processor resources... can clean up audio data from jittery clock sources such as the S/PDIF receiver.\""
    },
    {
     "source": "ADSP-2156x-Datasheet-EN.pdf (pdftotext line 46,173-175)",
     "detail": "front-page block diagram: 2x4 ASRC, 2x2 Precision Clock Generators, 2x1 S/PDIF Rx/Tx."
    },
    {
     "source": "ADSP-2156x-Datasheet-EN.pdf (pdftotext line 1,153,426-494)",
     "detail": "\"SHARC+ Single Core\"; \"based on the SHARC+ single core\"; SIMD core has two processing elements PEx/PEy executing same instruction on different data."
    },
    {
     "source": "sprint4/iface_survey.md:6 / DOC-S4-IO-01",
     "detail": "signal chain = ADAU1979(ADC)->SPORT4(TDM)->21569(FIRA)->SPORT4(TDM)->ADAU1962A(DAC), 直进直出, fixed 48k -- no rate conversion, no A2B, no S/PDIF in product path."
    }
   ],
   "benefit": "None directly (these are exclusions). Documenting them prevents future false-headroom claims. The only conditionally-useful idle block is the PCG/ASRC if a future product variant needs clock cleanup or async sources -- not the current broadside baseline.",
   "benefit_grade": "L2",
   "effort": "N/A (inventory/exclusion documentation).",
   "risk": "SIMD PEy is the tempting-but-forbidden item: the software core path (tree_filterbank.c) may not be using both PEs, but that file is FROZEN -- proposing a SIMD rewrite of the core is out of scope and would re-open the entire bit-exact gate. Multicore is excluded by lock (see exclusions). No risk if simply documented.",
   "notes": "Confirms single SHARC+ core (no second core to offload to). The ADSP-SC589 (2x SHARC+ + ARM) is a CHIP-CHANGE option but the chip decision is LOCKED -- see exclusions list.",
   "dimension": "hardware",
   "verdict": {
    "finding_id": "HW-6",
    "verdict": "confirmed",
    "reasons": "Verified every cited fact against the datasheet myself (pdftotext of knowledge_base/ezkit/bsp/datasheets/ADSP-2156x-Datasheet-EN.pdf). The finding's pdftotext line numbers (953-962, 46, 173-175, 1/153/426-494) do NOT match my conversion's line numbers, but the QUOTED TEXT is verbatim-present, so this is a pdftotext-version/layout difference, not a fabrication. Confirmed: (1) ASRC quote is exact at ds.txt:1677-1685: \"contains eight ASRC blocks... performs synchronous or asynchronous sample rate conversion across independent stereo channels, without using internal processor resources... can clean up audio data from jittery clock sources such as the S/PDIF receiver.\" (2) Block-diagram peripherals: \"2×4 ASRC PAIRS\" (ds.txt:89), \"2×2 PRECISION CLOCK\" (ds.txt:76), \"2×1 S/PDIF Rx/Tx\" (ds.txt:113). (3) \"SHARC+ Single Core\" / \"based on the SHARC+® single core\" (ds.txt:1,319); PEx/PEy SIMD at ds.txt:768-772 (\"two computational processing elements... PEx is always active, PEy is enabled by setting the PEYEN mode bit\"); crypto/PKA at ds.txt:1426,1473 (\"Public key accelerator (PKA) is available to offload computation intensive public key cryptography operations\"). (4) Signal-chain exclusion grounded: iface_survey.md:6 shows ADAU1979->SPORT4(TDM)->21569(FIRA)->SPORT4(TDM)->ADAU1962A, 直进直出 (direct-in-direct-out), and DOC-S4-IO-01 (audio_io_topology.md:79) locks 48k/24bit -- so no rate conversion, no S/PDIF, no A2B in product path. Constraint check PASSES: chip decision DEC-S1-004 (decisions_log.md:63-66,204-205) LOCKS ADSP-21569 single core, Gate 2 closed = irreversible -- so SC589 multicore is correctly flagged as locked-out, not proposed. Frozen-core check PASSES: all 5 frozen files exist (tree_filterbank.c, tfb_8ch.c, fir_coeffs_hb63.h, golden_ref.h, chirp_input.h) and are confirmed frozen (golden CRC 0x90556BC7, \"勿手改\"); the finding correctly treats SIMD PEy as forbidden-because-inside-frozen-core and does NOT propose a SIMD rewrite. No R14/C9 violation: zero FIRA/accelerator benefit is counted into selection -- the finding's entire thesis is that these blocks yield NO usable compute-headroom. The \"may not be using both PEs\" is appropriately hedged (I confirmed tree_filterbank.c has no explicit SIMD pragma, but the finding doesn't overclaim knowledge of that). No arithmetic to check -- benefit is explicitly \"None directly\". This is an honest exclusion/inventory finding that prevents false-headroom claims.",
    "grade_ok": true,
    "grade_fix": "Grade is honest. Benefit \"L2\" is attached to an exclusion/inventory documentation claim sourced entirely from L2 vendor datasheet pages + project-locked architecture docs (DOC-S4-IO-01); critically, NO compute-headroom number is asserted, so there is no L4-estimate-dressed-as-L2/L1 problem. If anything one could argue the signal-chain exclusion leans on DOC-S4-IO-01 which is project-locked architecture (arguably stronger than generic L2), but L2 is conservative and correct. No change needed.",
    "corrected": "No correction needed. One optional precision note for the parent: the finding's datasheet line numbers do not match a fresh pdftotext run (correct locations are ds.txt:1677-1685 for ASRC, :89/:76/:113 for the block-diagram peripherals, :319/:768-772/:1473 for single-core/PEx-PEy/PKA) -- the quoted text itself is verbatim-accurate, so this is a tooling-version artifact, not a substantive error. The benefit/claim itself stands fully confirmed."
   }
  },
  {
   "id": "STEER-1",
   "title": "HARD STOP: paired A/B series topology makes broadside-only a HARDWARE property — off-axis steering is impossible without a 16-channel hardware fork",
   "claim": "Off-broadside beam steering requires ASYMMETRIC per-element progressive delay; element c and element (15-c) must get DIFFERENT delays. But the LOCKED hardware wires each symmetric pair {c,15-c} in A/B SERIES onto ONE of 8 amplifier signals, so the two paired elements physically receive the IDENTICAL excitation. No firmware/algorithm change can impose a delay difference across a hard-wired series pair. Therefore off-axis tilt is NOT a firmware setting on this hardware — it requires reverting to 16 independent DAC/amp paths (hardware redesign). This single fact likely dominates the entire steering line's feasibility.",
   "evidence": [
    {
     "source": "knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md:12",
     "detail": "'16 个喇叭，分 A/B 区，A 区第 n 个 + B 区第 (17−n) 个串联（串联真实阻抗 15Ω [L1]），共 8 路' — pairs {n,17-n} (1-indexed) = {c,15-c} (0-indexed) hard-wired in series to 8 amp channels."
    },
    {
     "source": "knowledge_base/hardware_input/定向音柱AI数据_extracted.md:40-42",
     "detail": "'A 区第 1 个与 B 区第 16 个串联…16 个喇叭经 A/B 串联组成 8 路 [L1/硬件实测]'; closure note confirms 8-路 broadside symmetric series architecture (DEC-S3-DSP-03)."
    },
    {
     "source": "sprint4/audio_io_topology.md:32",
     "detail": "DOC-S4-IO-01: '8ch → ADAU1962A (12ch DAC, 用 8ch) → 8 路 ACM3128A 功放 → 8 路 A/B 对称串联 = 16 喇叭'; teardown KB-HW-001: 转接板 16ch 实为 8 路驱动."
    },
    {
     "source": "sprint2/docs/decisions_log.md:376,381",
     "detail": "DEC-S3-DSP-03 (CTO-approved): 'broadside-only 架构（无电子偏转能力）'; explicit warning '未来若重启电子偏转需求，必须改回 16ch 独立驱动硬件，算法无法绕过' (future steering MUST revert to 16ch independent-drive hardware, algorithm cannot work around it)."
    },
    {
     "source": "CLAUDE.md:203",
     "detail": "Locked baseline: '8 路 A/B 对称串联 / broadside-only'."
    }
   ],
   "benefit": "N/A — this is a strategic BLOCKER flag, not a headroom optimization. It bounds the scan: steering compute optimization on the current 8ch path is moot for OFF-AXIS steering because the hardware cannot realize it. Headroom only matters for the symmetric-compatible subset (STEER-2) or after a 16ch fork. Quantified scope: a 16ch fork DOUBLES channel-side compute (see STEER-4: FIRA 16ch margin already only 1.44x-1.73x [L3] before any steering compute is added).",
   "benefit_grade": "L1",
   "effort": "Realizing off-axis steering = full hardware redesign: 16 independent DAC channels (ADAU1962A has 12 — needs a 2nd DAC or TDM-32 + multi-DAC, decisions_log:109 / audio_io_topology.md:46) + 16 amp channels + new adapter board + breaks the A/B series teardown baseline. This is a Gate-2-class irreversible hardware decision (CLAUDE.md Gate 2), NOT a firmware task.",
   "risk": "None to the finding — it is L1-grounded in teardown + locked decision. Risk is to the steering PRODUCT LINE: if anyone assumes 'steering = a firmware feature on the existing board' they are wrong by hardware physics. C10/iron-rule-9 (hardware irreversible action) and Gate 2 apply to any 16ch fork.",
   "notes": "Nuance for STEER-2: symmetric excitation across {c,15-c} CAN still do something useful — see next finding.",
   "dimension": "steering",
   "verdict": {
    "finding_id": "STEER-1",
    "verdict": "confirmed",
    "reasons": "Core BLOCKER claim is fully substantiated; I opened every cited source. (1) Evidence verbatim-confirmed: knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md:12 = \"A区第n个 + B区第(17−n)个串联（串联真实阻抗15Ω [L1]），共8路\"; 定向音柱AI数据_extracted.md:40-42 = \"A区第1个与B区第16个串联...16个喇叭经A/B串联组成8路 [L1/硬件实测]\" + d=55mm L1; sprint4/audio_io_topology.md:32 = DOC-S4-IO-01 \"8ch→ADAU1962A(12ch DAC,用8ch)→8路ACM3128A→8路A/B对称串联=16喇叭, 转接板16ch实为8路驱动\"; sprint2/docs/decisions_log.md:376 = DEC-S3-DSP-03 \"broadside-only架构（无电子偏转能力）\" CTO-APPROVED, and :381 verbatim \"未来若重启电子偏转需求，必须改回16ch独立驱动硬件，算法无法绕过\"; CLAUDE.md:203 = locked baseline \"8路A/B对称串联 / broadside-only\". Every citation says exactly what STEER-1 claims.\n(2) Physics is correct textbook phased-array theory: off-broadside steer angle θ needs progressive phase φ_n = -(2π/λ)·n·d·sinθ, so symmetric elements c and 15-c require DIFFERENT (mirror-signed) delays for θ≠0. Series-wiring {c,15-c} onto one of 8 amp signals forces identical excitation → no firmware/parameter change can impose the delay difference. The CTO-approved decisions_log:381 states this same conclusion in plain language, so the \"algorithm cannot work around it\" rests on L1 hardware + a locked decision, not the scanner's own assertion.\n(3) Effort/risk realistic: 16ch fork is a Gate-2 irreversible hardware redesign. ADAU1962A is confirmed 12-channel (audio_io_topology.md:14, datasheet ADAU1962A.pdf p1 \"12-Channel...24-Bit DAC\"), so 16 independent DAC channels genuinely needs a 2nd DAC or TDM-32+multi-DAC per decisions_log:109 — matches the finding. C10/iron-rule-9/Gate-2 correctly invoked. No frozen-core modification proposed; R14/C9 separation respected.\nONE non-fatal blemish (does not change verdict): the scope-quantification footnote cites STEER-4's \"FIRA 16ch margin 1.44x-1.73x [L3]\". I could NOT find those figures in-repo. What sprint4/dsp/fira/F7_MARGIN_MATERIAL.md:112 actually shows is the CORE-ONLY (software, NOT FIRA) 16ch estimate = 1803.35 Mcyc/s = 0.55x at 1GHz (FAILS), and 8ch core = 0.92x (line 111). No 16ch FIRA margin number was located by me. This is a cross-reference to a sibling finding, not STEER-1's own load-bearing arithmetic; the directionally-true claim it supports (\"16ch fork roughly doubles channel-side compute\") is consistent with the baseline that orchestration is ~98% per-channel and with mcps_16ch_est = (cyc_8ch_frame + 8*cyc_analyze_1ch)*fpf/1e6 (bench_harness.c:125). I recommend STEER-1 cite the in-repo 0.55x core-only 16ch figure for scope rather than the unverified 1.44x-1.73x FIRA number.",
    "grade_ok": true,
    "corrected": "Core claim and benefit_grade L1 stand as written. Only correction: replace the scope footnote's unverified \"FIRA 16ch margin 1.44x-1.73x [L3]\" with the in-repo L1-anchored figure — 16ch CORE-ONLY demand = 0.55x at 1GHz (F7_MARGIN_MATERIAL.md:112; arithmetic 1000/1803.35=0.555 at line 114), already failing realtime BEFORE any steering compute. A 16ch FIRA margin number was not found in-repo and should not be cited until measured.",
    "grade_fix": "benefit_grade L1 is honest (teardown series-pairing = L1 hardware measurement + CTO-locked DEC-S3-DSP-03). No L4-as-L1 dressing. Only the cross-referenced STEER-4 \"1.44x-1.73x [L3]\" 16ch FIRA margin is unverifiable from sources I checked — recommend swapping to the in-repo 0.55x core-only 16ch [L3-arithmetic-on-L1-demand] figure."
   }
  },
  {
   "id": "STEER-2",
   "title": "What symmetric excitation CAN do: near-field FOCUSING and zone shaping are A/B-compatible; only off-axis TILT is blocked",
   "claim": "A symmetric pair driven by one signal forces a symmetric array aperture function. Real symmetric weights/delays about the array center always produce a BROADSIDE (0°) mainlobe — no off-axis tilt. BUT symmetric delay profiles ARE realizable and DO have a use: near-field FOCUSING (concave/curved delay symmetric about center → focus distance control) and broadside beamwidth/zone shaping are symmetric-compatible. So a 'steerable' PRD that actually means 'focus distance / zone width control at broadside' may be feasible on the EXISTING 8ch hardware; only true angular steering needs the 16ch fork (STEER-1). This distinction must be nailed in the PRD before committing.",
   "evidence": [
    {
     "source": "knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md:12",
     "detail": "Pair {c,15-c} symmetric about array center; one shared excitation per pair ⇒ aperture function is forced even-symmetric ⇒ mainlobe stays at broadside (standard array-factor property; symmetric real aperture ⇒ peak at 0°)."
    },
    {
     "source": "sprint2/docs/decisions_log.md:378",
     "detail": "DEC-S3-DSP-03 rationale: museum/station/mall zones are '固定前向波束安装场景，无运行期电子偏转需求' — confirms the product scenarios are broadside-fixed; focusing/zoning (symmetric) covers them without angular tilt."
    },
    {
     "source": "sprint4/audio_io_topology.md:31",
     "detail": "DSP path = '4 子带 dyadic 树形 + broadside beamform, 8 通道输出' — current firmware already produces 8 symmetric-pair signals; a symmetric focus-delay profile is the same channel count, no topology change."
    }
   ],
   "benefit": "Compute for symmetric focusing = same fractional-delay-FIR cost as STEER-4 but only 8 distinct channels (pairs share a signal) and delays bounded/static for fixed zones ⇒ near-zero update-rate cost. This is the ONLY steering-like capability with headroom on the current board. Bounds the 'cheap' steering envelope.",
   "benefit_grade": "L3",
   "effort": "Firmware-only IF PRD = broadside focusing/zoning: add a symmetric per-pair delay profile feeding the existing 8ch chain. No hardware change. Must re-validate FRAME/latency and re-pass bit-exact gates if it touches the frozen filterbank input buffering.",
   "risk": "Risk = PRD ambiguity: 'steerable column speaker' colloquially means ANGULAR steering (STEER-1 blocked). If the PRD truly needs off-axis tilt, STEER-2 does NOT rescue it. The symmetric-mainlobe-always claim is standard array theory [L3] — should be confirmed by an acoustic-sim teammate before being load-bearing in a PRD.",
   "notes": "Frame this as: 'broadside focus/zone = firmware; angular tilt = 16ch hardware fork.' Forces the PRD to choose.",
   "dimension": "steering",
   "verdict": {
    "finding_id": "STEER-2",
    "verdict": "confirmed",
    "grade_ok": true,
    "reasons": "Opened all three cited sources plus corroborating repo files. CORE CLAIM HOLDS. (1) Symmetric-real-aperture -> broadside-only mainlobe is directly corroborated by the repo's own array-factor formula AF(theta)=2*sum w_n cos[(2n-1)*pi*d*sin theta/lambda] (even function), sprint3/dsp/dsp_8ch_report.md:164, and explicitly validated by the project critic: \"AF 为纯实偶函数...broadside 时分数延迟 τ≈0——全部物理正确\" (sprint3/critic/critic_review_s3.md:106). evidence[0] (hardware_input:12) confirms the {c,15-c}/(n,17-n) center-symmetric series pairing, one shared excitation per pair (also dsp_8ch_report.md:153: the two pair elements are series-locked, \"完全相同的信号 同幅同相\"). The finding's \"{c,15-c}\" is a 0-indexed restatement of the file's 1-indexed \"(n,17-n)\" — same pairing, not a misquote. (2) NEAR-FIELD FOCUSING claim is physically sound and architecture-compatible: each of the 8 distinct pair-channels can carry a distinct delay; a focus delay profile that is mirror-symmetric about array center keeps the two elements of every pair phase-locked, so it satisfies the series-pairing constraint. dsp_8ch_report.md:191 confirms broadside => all per-channel delays = 0 (unit impulse); finite-distance focus simply makes those currently-zero delays nonzero through the SAME existing \"分数延迟 FIR × 4 子带, 8 ch\" stage (dsp_8ch_report.md:59) which is a SEPARATE beamforming stage OUTSIDE the frozen halfband filterbank core (frozen core per FIRA_IMPL.md:51 = tree_filterbank/golden_ref/chirp_input/hb63 segments). So focusing works AROUND the frozen core — constraint respected; finding correctly hedges re-validation \"if it touches the frozen filterbank input buffering.\" (3) BENEFIT ARITHMETIC anchored to pure-core L1/established path: fractional-delay FIR = 2.88 MMAC/s within 30.56 MMAC/s total, 49x headroom (dsp_8ch_report.md:59-72); static-zone delays => near-zero per-frame update cost — sound L3 analytical reasoning, NOT a board measurement and NOT FIRA — so NO C9/iron-rule-8 violation (no accelerator benefit folded into selection/commitment; the finding explicitly frames focus/zone-vs-angular-tilt as an open PRD-scoping decision, \"must be nailed in the PRD before committing\"). DEC-S3-DSP-03 broadside-only (decisions_log:381) is respected, not contradicted. WEAKNESS (minor, non-core): evidence[1] (decisions_log:378) over-reads — line 378 literally says \"固定前向波束安装场景，无运行期电子偏转需求,\" which establishes \"angular tilt NOT needed\" but does NOT establish that focusing/zoning is a NEEDED or \"covered\" requirement; the finding's detail asserts the latter as an inference. This is a citation-precision issue, neutralized by the finding's own framing that the PRD must choose. Does not break the core claim.",
    "grade_fix": "L-grades are honest as written. Benefit L3 (analytical array theory + pure-core MMAC budget) is correct — not dressed as L1/L2/measured. Optional tightening: down-grade evidence[1]'s \"focusing/zoning covers them\" inference to [L3/待 PRD 确认] since decisions_log:378 only supports \"angular tilt dispensable,\" not \"focusing required/covered.\" Add risk note that near-field focusing efficacy at finite F has not been acoustic-sim verified (finding already flags this: \"should be confirmed by an acoustic-sim teammate before being load-bearing in a PRD\").",
    "corrected": "Core benefit stands uncorrected: broadside near-field focusing / zone-width shaping is A/B-symmetric-compatible and realizable on the existing 8ch hardware via the already-budgeted 8ch fractional-delay FIR stage (2.88 MMAC/s of 30.56 total, ~49x headroom, dsp_8ch_report.md:59-72), outside the frozen filterbank core, with near-zero update cost for static zones — the only steering-like capability with headroom on the current board; true off-axis angular tilt remains blocked and needs the 16ch hardware fork (DEC-S3-DSP-03 / dsp_8ch_report.md:179). One evidence wording weakened: decisions_log:378 supports \"angular tilt not needed,\" not \"focusing/zoning is a covered PRD requirement\" — treat focusing efficacy as [L3/待 acoustic-sim + PRD 确认], not load-bearing until an acoustic-sim teammate confirms."
   }
  },
  {
   "id": "STEER-3",
   "title": "A steerable PRD almost certainly TRIGGERS the SC-S3-GEOM-01 d-renegotiation clause (steering shrinks the grating-lobe-free band well below 6 kHz)",
   "claim": "At d=55mm the grating-lobe-free upper edge is fc=c/(d(1+|sin θ|)). At broadside (θ=0) fc=6236 Hz (reproduces the repo's L1 strict criterion exactly). Steering off-axis MOVES grating lobes into band: θ=10°→5314 Hz, θ=20°→4647 Hz, θ=30°→4158 Hz. The d=55mm lock is explicitly conditioned on 'PRD adds no 6-8kHz strong-directivity requirement'; a steering PRD that wants usable directivity while tilting pushes the clean band even further below 6 kHz, which collides with that premise. Per SC-S3-GEOM-01 this AUTOMATICALLY triggers a d-renegotiation — and d is geometry-LOCKED with no PM autonomy (must escalate to CTO).",
   "evidence": [
    {
     "source": "sprint2/docs/decisions_log.md:455",
     "detail": "L1 grating criterion: 半波长 c/(2d)=3118Hz, 严格 c/d=6236Hz; broadside 真问题带 6.2–8kHz, 500Hz–5kHz 安全. My [L3] fc(θ=0)=6236.4Hz reproduces the strict L1 value with c=343 m/s, d=0.055 m — formula validated."
    },
    {
     "source": "sprint2/docs/decisions_log.md:457-458,239-240",
     "detail": "SC-S3-GEOM-01 (CTO 原文照录, 永久产品边界): 'PF-8 d=55 决策的不可逆性以\"PRD 不新增 6-8kHz 强指向硬需求\"为前提。任何 PRD 变更涉及 6-8kHz 强指向 → 自动触发 d 重议，无 PM 自治权。' R7 watch flag mirrors this."
    },
    {
     "source": "CLAUDE.md:204",
     "detail": "'受 CTO 硬约束 SC-S3-GEOM-01 永久边界约束（PRD 不新增 6–8kHz 强指向硬需求为前提，否则触发 d 重议）'."
    },
    {
     "source": "computed [L3]",
     "detail": "fc(θ): 0°=6236, 5°=5736, 10°=5314, 15°=4954, 20°=4647, 30°=4158, 45°=3653 Hz (c=343, d=0.055). Each steer degree lowers the clean ceiling monotonically."
    }
   ],
   "benefit": "Strategic gating value: prevents the steering line from quietly committing d=55mm geometry that is incompatible with steered directivity. The headroom 'cost' is a forced CTO geometry re-decision (smaller d to recover band) which itself changes element count/aperture and feeds back into ALL compute estimates.",
   "benefit_grade": "L3",
   "effort": "Analysis-only to FLAG (this finding). Resolving it = CTO-level geometry re-decision (SC-S3-GEOM-01) + acoustic re-sim + potential N/d/aperture change cascading into DSP compute re-budget. Not a firmware task.",
   "risk": "The fc(θ) formula and angles are [L3] analytical (validated against the L1 broadside value); the actual usable-directivity-vs-grating tradeoff at a given steer angle needs acoustic-sim [L2] to set the real band edge. The TRIGGER itself is governance-certain once a steered-directivity PRD exists; the exact d that recovers the band is the open question.",
   "notes": "Two strategic flags (STEER-1 16ch fork + STEER-3 d-renegotiation) plausibly dominate the whole scan; both are CTO-gate items.",
   "dimension": "steering",
   "verdict": {
    "finding_id": "STEER-3",
    "verdict": "confirmed",
    "grade_ok": true,
    "reasons": "Opened every cited source and re-derived every number; all check out.\n\nEVIDENCE VERIFIED:\n- decisions_log.md:455 (read directly): \"半波长判据 c/(2d)=3118Hz、严格判据 c/d=6236Hz；broadside 真问题带为 6.2–8kHz，500Hz–5kHz 安全 [L1]\" — quoted accurately. My recompute c=343, d=0.055: c/d=6236.4Hz, c/2d=3118.2Hz — matches the L1 values exactly, so the finding's [L3] fc(θ=0)=6236.4Hz genuinely reproduces the L1 anchor.\n- decisions_log.md:457-458 (read directly): SC-S3-GEOM-01 CTO 原文照录 verbatim: \"PF-8 d=55 决策的不可逆性以\\\"PRD 不新增 6-8kHz 强指向硬需求\\\"为前提。任何 PRD 变更涉及 6-8kHz 强指向 → 自动触发 d 重议，无 PM 自治权。永久产品边界。\" — quoted correctly.\n- decisions_log.md:240 (R7 watch flag) read directly: mirrors the clause as the finding states.\n- decisions_log.md:448-451 confirms d=55mm is L1 teardown-measured and 强约束 LOCKED under SC-S3-GEOM-01 — geometry is genuinely CTO-gated with no PM autonomy, as claimed.\n- CLAUDE.md:204 (grep): verbatim match to the finding's quote.\n\nARITHMETIC VERIFIED (my own python run): fc(θ)=c/(d(1+|sinθ|)) gives 0°=6236.4, 5°=5736.4, 10°=5313.7, 15°=4954.1, 20°=4647.0, 30°=4157.6, 45°=3653.2 Hz — every value matches the finding to the decimal. The formula is the standard steered-ULA grating-lobe-free condition (d/λ<1/(1+|sinθ_steer|)) and correctly reduces to c/d at broadside. Monotonic erosion of the clean ceiling with steer angle is real: θ=10° already drops the ceiling to 5314Hz, below the existing 6.2-8k problem band and into the 5k/6k spec-downgrade margin.\n\nGRADE HONESTY: L-grades are clean. Formula=[L3], broadside ceiling anchored to [L1] criterion, real usable-directivity-vs-grating band edge correctly deferred to [L2] acoustic-sim, benefit graded [L3] strategic. No [L4] dressed as L2/L1; no estimate dressed as \"measured.\" No frozen-core touch (tree_filterbank/tfb_8ch/hb63/golden/chirp untouched — this is geometry/governance only). Fully orthogonal to R14/C9 (FIRA compute closure) — no entanglement.\n\nCAVEAT (does not refute): the title's \"almost certainly TRIGGERS\" is slightly stronger than the clause is literally tautological — the clause fires on a 6-8kHz strong-directivity *requirement*, and a steering PRD scoped to ≤5kHz would NOT cross it. But the finding's own risk field discloses this honestly (\"governance-certain once a steered-directivity PRD exists; the exact d that recovers the band is the open question\"). For any meaningful steering product wanting retained directivity off-axis, the monotonic ceiling erosion makes the collision highly likely. The strategic gate (flag before the steering line commits d=55) is valid and correctly framed as a CTO escalation item, not a firmware task. Effort/risk realistic: flagging is analysis-only; resolution genuinely needs CTO geometry re-decision + acoustic re-sim cascading into compute re-budget."
   }
  },
  {
   "id": "STEER-4",
   "title": "PART A steering compute cost [L4]: fractional-delay FIR is CHEAP vs the filterbank, but stacks on an ALREADY-THIN margin and explodes at 16ch",
   "claim": "Integer-sample steering delay = buffer-index offset (~0 MCPS). Fractional delay = a short per-channel FIR. Cost MCPS = taps × 48000 × Nch / 1e6 × (cyc/MAC). On SHARC+ board reality the relevant cyc/MAC is ~30-50 (NOT the ideal 1-2; the repo's own board data shows real ~30-50 cyc/MAC after cache/interrupt). Cheap in isolation, but it ADDS on top of an 8ch FIRA path already at only 2.878x realtime margin and a 16ch path already at 1.44x-1.73x [L3] BEFORE steering.",
   "evidence": [
    {
     "source": "computed [L4/待验证] arithmetic",
     "detail": "16-tap frac-delay FIR: 8ch=6.14 MMAC/s, 16ch=12.29 MMAC/s. @1-2 cyc/MAC (ideal): 8ch 6.1-12.3 Mcyc/s, 16ch 12.3-24.6. @30-50 cyc/MAC (board reality): 8ch 184-307 Mcyc/s, 16ch 369-614 Mcyc/s. 8-tap halves; 32-tap doubles."
    },
    {
     "source": "sprint4/dsp/fira/F7_MARGIN_MATERIAL.md:191",
     "detail": "Board reality: 'real ~30-50 cycle/MAC + cache/interrupt, collapsing 33x to 1.32x' — the ideal cyc/MAC assumption was overturned on board; steering FIR must be costed at the same 30-50 cyc/MAC."
    },
    {
     "source": "sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:39-41",
     "detail": "8ch FIRA demand 347.45 MCPS, margin 2.878x [L1-derived]. A 184-307 Mcyc/s core-side steering FIR (16-tap, 8ch, board cyc/MAC) is comparable in size to a large EQ chain and would erode that margin toward ~1.4-2.1x."
    },
    {
     "source": "sprint4/dsp/fira/F7_R14_RULING_MATERIAL.md:74-75",
     "detail": "16ch FIRA margin defensible range 1.44x (naive 2x) to 1.73x (analyze-only convention) [L3]. Adding 369-614 Mcyc/s of 16-tap steering FIR on top could push a 16ch steered path toward/below 1.0x realtime."
    },
    {
     "source": "sprint4/dsp/fira/FIRA_IMPL.md:34",
     "detail": "FIRA supports per-channel DECIMATION/SINGLE_RATE FIR via ADI_FIR_CHANNEL_INFO; a frac-delay FIR could be offloaded as 'just another segment' rather than core MACs — but see STEER-5 for the per-task overhead penalty on adding segments."
    }
   ],
   "benefit": "Quantifies the steering compute envelope so it can be checked against headroom BEFORE commit: 16-tap@8ch ≈ 184-307 Mcyc/s board (≈ the EQ-chain worst case already flagged in the brief); 16-tap@16ch ≈ 369-614 Mcyc/s. Lets the team pick tap count / offload target against the 2.878x (8ch) or 1.44-1.73x (16ch) margin.",
   "benefit_grade": "L4",
   "effort": "Per CLAUDE.md C9/iron-rule-8 ALL these numbers stay [L4/待验证] — they are not board-measured and must NOT enter selection/commit until measured on the FIRA build. Implementing = a per-channel delay-line index + short FIR (core or FIRA segment) + bit-exact re-validation if it touches frozen-core input buffering (tree_filterbank.c is FROZEN). Needs a board run to grade.",
   "risk": "cyc/MAC is the dominant uncertainty (1-2 ideal vs 30-50 board → 25x spread). Buffer contract: the delay-line for steering must keep ≥ntaps+window-1 initialized samples (FIRA I/O contract, FIRA_IMPL.md / fira_tree.c:116) or it reads uninitialized/over-reads (IO1 gate). Integer-delay indexing into the frozen filterbank's input buffer risks the layout-sensitivity (IO2) trap.",
   "notes": "Integer part is ~free; fractional FIR is the only real cost. Tracking-rate cost is STEER-5.",
   "dimension": "steering",
   "verdict": {
    "finding_id": "STEER-4",
    "verdict": "confirmed",
    "reasons": "Grade is honest. Every number is [L4/待验证]; the finding explicitly invokes C9/iron-rule-8 and states the numbers must NOT enter selection/commit until board-measured. No L4 estimate is dressed as L2/L1. The board cyc/MAC (30-50) is correctly sourced to the L1-overturn record (F7_MARGIN_MATERIAL.md:191) rather than invented. The 8ch 2.878x base and 16ch 1.44-1.73x base are correctly labeled [L1-derived] and [L3] respectively, and the finding does not over-promote them — it treats the whole erosion analysis as analytic sizing under C9, not a commitment.",
    "grade_ok": true,
    "corrected": "No correction to the verdict. Optional tightening for downstream use: (1) 8ch post-steering margin band is 1.53-1.88x (16-tap, board 30-50 cyc/MAC) — narrower and more defensible than the finding's stated \"~1.4-2.1x\". (2) Cite FIRA offload as DECIMATION per-channel only (FIRA_IMPL.md:34); drop \"SINGLE_RATE\" unless a separate line is found, or grade it [L4/assumed]. (3) The 16ch numbers (1.44-1.73x base, 0.76-1.06x post-steer) themselves rest on [L3] extrapolation with no FIRA 16ch measurement existing (R14_RULING:56-59) — keep them strictly [L4/待验证] for any selection use, which the finding already does.",
    "grade_fix": "none required"
   }
  },
  {
   "id": "STEER-5",
   "title": "PART A update-rate cost: static museum zones amortize to ~0, but CONTINUOUS tracking pays the FIRA per-task re-creation penalty (orchestration is the cost, not the MACs)",
   "claim": "Dolph weights are UNCHANGED by steering (steering = added linear phase; window stays), so the static beam goes on as before. But if steering delays are implemented as FIRA segments and the steer angle CHANGES per frame (continuous target tracking), the per-channel FIRA tasks may need re-CreateTask each update — and the repo shows orchestration (CreateTask/FixedPointEnable/QueueTask/spin/postscale/cache-invalidate, fixed 72+24 segment calls) is a LARGE constant per-segment cost, NOT amortized by larger work. Museum/station 'static zones' = rare updates → amortized ~0. Continuous tracking → pay the task-recreate path every frame.",
   "evidence": [
    {
     "source": "sprint4/dsp/fira/fira_tree.c:212-213,269-277",
     "detail": "Per-task lifecycle: Open→RegisterCallback→CreateTask→FixedPointEnable(SIGNED)→QueueTask→spin(FIRTaskDoneCount<N_TASKS)→Close, with adi_fir_CreateTask called per segment/channel (nNumChannels=1 at :269). Changing coefficients/config implies re-CreateTask."
    },
    {
     "source": "sprint4/dsp/fira/F7_CLOSING_RECORDS.md:121-131",
     "detail": "The 56,616 cyc/ch lumps 9 FIRA segments' CreateTask+FixedPointEnable+QueueTask+spin+postscale+cache-invalidate; 'orchestration is ~constant per segment (fixed call count 72+24), MAC scales with window' — orchestration dominates and does NOT shrink with small kernels."
    },
    {
     "source": "sprint4/dsp/fira/FIRA_IMPL.md:144",
     "detail": "'63-tap 小核 → FIRA per-task 固定开销 (QueueTask / 中断 core cycle) 可能吞掉部分 offload 收益' — confirms per-task fixed overhead is significant relative to small kernels; a tracking re-create adds another such fixed cost per update."
    },
    {
     "source": "sprint4/dsp/fira/F7_CLOSING_RECORDS.md:37-40",
     "detail": "Per-frame FIXED orchestration share = 10,345 cyc/frame = 2.23% [L1-derived]; this is the steady-state (tasks already created). A per-frame re-CreateTask for tracking would ADD to this, not reuse it."
    }
   ],
   "benefit": "Decision rule: STATIC zones (the locked product scenarios, DEC-S3-DSP-03:378) → steering delays are set once, amortized ~0 extra orchestration, only the steady MAC cost of STEER-4 applies. CONTINUOUS tracking → add per-frame task-recreate overhead (bounded above by the per-segment orchestration constant, [L4] until measured). This lets the PRD choose update model with eyes open.",
   "benefit_grade": "L4",
   "effort": "If static: implement steer as fixed per-channel delay set at config time (cheap). If tracking: needs a measured task-recreate cost (board run) and possibly a coefficient-update path that avoids full CreateTask. All [L4/待验证] per C9.",
   "risk": "Whether changing only the delay (phase) actually forces a full re-CreateTask vs a lighter coefficient reload is NOT confirmed from the repo (the adi_fir 2156x header is missing locally — iface_survey G1/G2). The re-create-vs-reload distinction is a board/toolchain gap. Ties to STEER-1: this whole question is moot for off-axis unless the 16ch fork happens.",
   "notes": "The cost of steering tracking is an ORCHESTRATION cost, consistent with the brief's DIMENSION-1 task-reuse theme, not a MAC cost.",
   "dimension": "steering",
   "verdict": {
    "finding_id": "STEER-5",
    "verdict": "weakened",
    "grade_ok": true,
    "corrected": "CORRECTED FRAMING: \"Steering's cost is an ORCHESTRATION cost, not a MAC cost (per-segment FIRA lifecycle dominates; the per-frame FIXED share is only 10,345 cyc = 2.23% of 463,273, the rest is per-channel/per-segment) [L1-derived]. WHETHER continuous tracking adds ANY measurable cost over a static beam is an OPEN board/toolchain question [L4/待验证], because: (a) the as-built F7 baseline ALREADY calls adi_fir_CreateTask per segment per frame (fira_tree.c:472, inside fira_run_segment, 72+24 times/frame) — so 56,616 cyc/ch and the 10,345 cyc/frame fixed share ALREADY INCLUDE per-frame CreateTask; tracking does NOT add a 'fresh' CreateTask on top of an otherwise-reusing steady state, because there is no reusing steady state in the as-built code; (b) steering = added per-element linear phase/delay with the Dolph amplitude window UNCHANGED [L3-analytical] — changing only the input delay/phase plausibly needs NO new CreateTask beyond what the baseline already pays. The genuine, repo-honest decision input is therefore: orchestration already dominates per frame; an OPTIMIZED implementation that hoists CreateTask out of the per-frame loop would benefit a STATIC beam (rare-update zones) — but that hoist is itself an un-built optimization, NOT a property of the L1 baseline. All of this is moot unless the 16ch hardware fork happens (DEC-S3-DSP-03:375-382: locked broadside-only, 'algorithm cannot work around', requires 16ch independent-drive HW to re-enable steering).\"",
    "grade_fix": "Keep benefit_grade=L4. No grade inflation found — estimates are correctly L4, the 10,345/2.23% fixed share is correctly cited [L1-derived], the linear-phase/window-independence premise is implicitly L3-analytical and not dressed up. The honesty about the re-create-vs-reload distinction being a board/toolchain gap (iface_survey G1/G2) is accurate and well-graded.",
    "reasons": "Verified all cited evidence directly. (1) fira_tree.c:212-213 lifecycle (Open->RegisterCallback->CreateTask->FixedPointEnable(SIGNED)->QueueTask->spin->Close) and :269-277 (CreateTask with nNumChannels=1) check out EXACTLY. (2) F7_CLOSING_RECORDS.md:37-40 confirms 8x56,616=452,928 vs 463,273 -> 10,345 cyc/frame = 2.23% fixed share [L1-derived]; arithmetic re-verified: 10,345/463,273=2.233%. (3) FIRA_IMPL.md:144 verbatim confirms '63-tap 小核 -> FIRA per-task 固定开销 (QueueTask/中断 core cycle) 可能吞掉部分 offload 收益' — supports orchestration-dominates thesis. (4) 72+24 segment count verified at fira_regression.c:608 ('72 analyze + 24 synth FIRA segment invocations across 8 channels') and :276/:442/:457. CORE THESIS CONFIRMED (orchestration is the cost, per-segment lifecycle dominates, MACs are small for 63-tap kernels). HOWEVER the finding is WEAKENED on its load-bearing cost-asymmetry framing: evidence #4's narrative says 'this is the steady-state (tasks already created); a per-frame re-CreateTask for tracking would ADD to this, not reuse it.' This MISDESCRIBES the as-built baseline. fira_run_segment (fira_tree.c:424-480) calls adi_fir_CreateTask at line 472 INSIDE every segment invocation — i.e. the L1 baseline ALREADY re-creates the task 72+24 times PER FRAME for the (static-beam) regression. There is NO 'tasks-already-created steady state' in the measured code; the 56,616 cyc/ch and the 10,345 cyc fixed share ALREADY pay per-frame CreateTask. So tracking would NOT necessarily ADD a fresh CreateTask on top of a reusing baseline — the baseline already pays it regardless of static/tracking. The TRUE distinction (which the finding's own risk note correctly flags as unconfirmed, citing iface_survey G1/G2: adi_fir_2156x.h missing, re-create-vs-reload not determinable from repo; and v2.h:228/240 SetChannelTapLength/SetChannelCoefficientBuffer hint a lighter reload path MAY exist) is whether changing only the steer delay needs ANY extra work over the already-counted per-frame CreateTask — plausibly none, since steering changes phase/delay with the Dolph window unchanged. Net: the qualitative thesis (orchestration-bound, not MAC-bound) is solid and useful for the PRD; the quantitative asymmetry (static~0 vs tracking-pays-re-create) is overstated relative to the as-built baseline and should be reframed as 'orchestration already dominates per-frame; hoisting CreateTask out of the loop would help a static beam but is an un-built optimization.' CONSTRAINTS OK: frozen core untouched (proposes orchestration/param changes only); C9 respected (no FIRA benefit fed into selection; all tracking cost [L4/待验证]); correctly gated behind STEER-1's 16ch fork, consistent with DEC-S3-DSP-03:375-382 locked broadside-only ('algorithm cannot work around', needs 16ch HW). L-grades honest throughout."
   }
  },
  {
   "id": "ORCH-1",
   "title": "Steering collides head-on with the broadside-only LOCKED decision; it is a HARDWARE fork, not a compute-headroom item",
   "claim": "A beam-steering product CANNOT be delivered on the current locked baseline by any orchestration/compute change. DEC-S3-DSP-03 (APPROVED, closed R-S3-DSP-03) accepts the 8-route A/B center-symmetric series topology as broadside-only and states explicitly that re-opening electronic steering 'must revert to 16ch independent-drive hardware; the algorithm cannot work around it'. The constraint is rooted in L1 teardown physics (A region elem n + B region elem 17-n series-wired, 8 routes, 15ohm measured), so the array factor is a purely-real even function = zero asymmetric phase delay = zero steering authority. Any headroom this scan finds is therefore moot for a steering line UNTIL the hardware-topology decision is re-opened by CTO; the scan's job is to size headroom AFTER that fork, not to enable steering.",
   "evidence": [
    {
     "source": "sprint2/docs/decisions_log.md:375-383",
     "detail": "DEC-S3-DSP-03 broadside-only architecture accepted (CTO, APPROVED, R-S3-DSP-03 formally closed); warning: future steering 'must revert to 16ch independent drive hardware, algorithm cannot work around'"
    },
    {
     "source": "sprint3/dsp/dsp_8ch_report.md:159-179",
     "detail": "Center-symmetric AF is purely-real even function, supports only broadside; 'if steering needed, MUST modify hardware (16ch independent drive), algorithm cannot bypass'"
    },
    {
     "source": "knowledge_base/hardware_input/定向音柱AI数据_extracted.md:40-42",
     "detail": "[L1/hardware-measured] A-region elem 1 series with B-region elem 16, etc. -> 16 speakers form 8 routes; matches DEC-S3-GEOM-01 / DEC-S3-DSP-03"
    },
    {
     "source": "sprint3/audit/matlab_verify_m3_superdir_8pair.md:99-101",
     "detail": "8-pair real-weight symmetry equivalence to 16-elem holds ONLY for broadside+symmetric weights; 'electronic steering / asymmetric beam NOT equivalent' (machine-precision MATLAB cross-check)"
    }
   ],
   "benefit": "Strategic gate, not a cyc/frame number: prevents the steering line from being scoped as a software/orchestration task. The realtime budget after a 16ch fork would roughly double the per-channel orchestration (8->16 channels), each channel paying CreateTask/QueueTask/spin/postscale/cache-invalidate, so the 2.878x [L1] FIRA margin would be consumed toward ~1.4x on the SAME chip before steering math is even added. Quantifying that is the headroom question — but only after CTO re-opens DEC-S3-DSP-03.",
   "benefit_grade": "L3",
   "effort": "N/A for software. Re-opening = CTO gate on DEC-S3-DSP-03 + hardware fork (8-route A/B series -> 16ch independent drive: DAC channels 8->16, power-amp channels double, transfer-board redesign, BOM change) + PRD change adding a steering requirement. No board run can substitute.",
   "risk": "If a stakeholder reads 'headroom exists (2.878x)' as 'steering is feasible in software', that is a category error against DEC-S3-DSP-03 and the L1 topology. Headroom does not buy steering authority; only the hardware fork does.",
   "dimension": "constraints",
   "verdict": {
    "finding_id": "ORCH-1",
    "verdict": "confirmed",
    "grade_ok": true,
    "reasons": "All 4 cited evidence items verified verbatim by me: (1) sprint2/docs/decisions_log.md:375-383 — DEC-S3-DSP-03 APPROVED by CTO, R-S3-DSP-03 formally closed, explicit warning \"未来若重启电子偏转需求，必须改回 16ch 独立驱动硬件，算法无法绕过\". (2) sprint3/dsp/dsp_8ch_report.md:159 — \"中心对称结构的 AF...纯实数偶函数，仅支持 broadside...无法产生不对称的相位延迟偏转\"; :179 \"如需波束偏转，必须修改硬件...算法无法绕过\". (3) knowledge_base/hardware_input/定向音柱AI数据_extracted.md:40-41 — [L1/硬件实测] A1 series B16 etc -> 16 speakers form 8 routes, d=55mm (15ohm series is at :46, also [L1], with a precision-caveat the finding omitted but the claim does not hinge on it). (4) sprint3/audit/matlab_verify_m3_superdir_8pair.md:98-101 — \"电子偏转能力 不等价/丧失...偏转需非对称复权\", machine-precision MATLAB cross-check; equivalence holds ONLY for broadside+symmetric weights. CORE CLAIM (steering = hardware fork, not orchestration/compute) is rooted in both the locked decision and the physics; sound. BENEFIT ARITHMETIC verified against the repo's OWN L1-derived projection: F7_R14_RULING_MATERIAL.md:61-62 gives naive-2x conservative case 1000/694.9 = 1.44x (range 1.44x-1.73x-<2.88x, \"[L3 extrapolation on L1 base]\"). The finding's \"toward ~1.4x\" matches the conservative end exactly — it is the repo's own number, not invented. The 8->16 \"roughly double per-channel orchestration\" reasoning is ju
```
