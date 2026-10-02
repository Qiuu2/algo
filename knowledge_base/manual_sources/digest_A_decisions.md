# Digest A — 决策日志 / PRD / 状态快照 逐条摘要（最高可信层）

> ⚠ 公开版说明（2026-10-02）：本摘录按写时原文照录，里面会出现已撤回或已被推翻的数字（如 d=30、17×/33×、1.5k/3k/6k 子带标签、86–144 MCPS、6.4×）。采信任何数字前，以 `sprint2/docs/decisions_log.md` 和 `sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md` 为准。

> 读者：records reader A（只读，未改仓库任何文件，未推断原文以外内容）｜生成：2026-10-02
> 仓库：`/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow`
> 记号：`decisions_log.md` = `sprint2/docs/decisions_log.md`；`prd_update.md` = `sprint2/docs/prd_update.md`；行号均为文件实际行号。
> 「谁决定」一栏照抄原文措辞（CTO（总工）/ CTO 拍板 / CTO 正式裁定 / CTO 会话内裁定 / critic / PM 注 / 非决策·留痕 等）。

---

## 0. 读了什么

| 文件 | 字节 | 行数 | 读取范围 | 不可读/异常 |
|---|---|---|---|---|
| `sprint2/docs/decisions_log.md` | 225,187 | 1,322 | **1–1322 全部**（Read 分 19 批：1-200 / 201-320 / 321-430 / 431-520 / 521-600 / 601-660 / 661-710 / 711-732 / 732-801 / 802-901 / 902-1001 / 1001-1017 / 1018-1025 / 1026-1035 / 1036-1065 / 1066-1085 / 1086-1100 / 1101-1200 / 1201-1322） | 无不可读行（最长行 < 1,900 字符，未被截断；awk 报的 2,747 是字节数）。格式异常：:957 孤立 ``` 、:961/:985/:1000 落档包一级标题残留（见 §5-11） |
| `sprint2/docs/prd_update.md` | 35,209 | 417 | **1–417 全部**（3 批） | 无 |
| `sprint3_status.md` | 9,858 | 132 | **1–132 全部** | 无 |
| `PROJECT_REFERENCE.md` | 6,790 | 118 | **1–118 全部** | 无 |

补充核对：对以上 4 文件用 Python 正则复查了 `21565`、`GitHub/开源`、`到货`、`reference design/Audio Toolbox`、`文献/登记 #`、`Sprint 4–7/阶段/Stage`、`push/origin`、`R1 闭合`、`86–144` 等关键词（结果已并入 §3/§5）。

---

## 1. 决策日志逐条时间线（按文件顺序；共 173 行）

格式：`# | 日期 | 出处 | ID | 谁（原文措辞） | 摘要`

### 1.A 表头 / 制度引用
1. 2026-05-26（表头日期） | decisions_log.md:1-8 | DOC-DEC-002 v2.0 表头 | 作者"项目文档专家 Agent" | 标题"决策日志（Sprint 1 + Sprint 2）"；版本 v2.0（PF-8 几何统一）、前版本 v1.9（PF-4）；状态"Gate 1 PASSED / Gate 2 CLOSED，阵列基线已全部锁定"（表头日期与页脚 v2.0=05-29 不符，见 §5-1）
2. 无日期 | decisions_log.md:12-17 | POLICY-PROV-001 强制引用 | — | 缘起 PF-1（纸面算力值 LOCKED 芯片选型）；新 DEC 须 6 字段；历史 DEC 下次修订回填；Critic 每次查 C1–C5

### 1.B Sprint 1（全部无日期）
3. 无日期（"Sprint 1"） | decisions_log.md:35-40 | DEC-S1-001 | CTO（总工） | 技术路线 = 相控阵线阵（DAS + 子带）；依据含"竞品拆机分析证实主流路线为 ADI 系芯片驱动的线阵相控阵"；✅ LOCKED
4. 无日期（"Sprint 1"） | decisions_log.md:44-50 | DEC-S1-002 | CTO（总工） | 仅 ≥1kHz 要求强指向，250–500Hz 不作要求（"CTO 明确用户需求集中在语音清晰度频段"）；✅ LOCKED
5. 无日期（"Sprint 1 末"） | decisions_log.md:54-59 | DEC-S1-003 | "Project Manager Agent + Critic Agent，经 CTO 认可" | Gate 1 基线 16 元/d=30mm 可行性通过；全速率不可行、dyadic 树形 27×；✅ LOCKED（Sprint 2 比较基准）
6. 无日期（"Sprint 1"） | decisions_log.md:63-73 | DEC-S1-004 | CTO（总工） | DSP 锁定 ADSP-21569（无 ARM、1GHz、1664KB SRAM、CCES 免费、"EV-21569-EZKIT 开发板可购"、¥120-220）；✅ LOCKED（不可逆）

### 1.C Sprint 2（DEC-S2-001~005 无日期）
7. 无日期（"Sprint 2"） | decisions_log.md:79-86 | DEC-S2-001 | 声学仿真 Agent，经 Critic Agent 审核 | 竞品逆向（由竞品实测指向性拟合）：约 N=20/d=35mm/Dolph-20，RMS 2.84dB；隐含 BW 36.6/18.1/9.0°"供 PRD 对标参考"；📋 CONFIRMED（不作设计锁定）
8. 无日期（"Sprint 2"） | decisions_log.md:90-101 | DEC-S2-002 | DSP 算法 Agent，经 Critic 审核 | dyadic 树形半带 FIR、48kHz、4 子带；56.4 MMAC/s、27×；树形 C 未实现，Sprint 3 待 CCES 移植；✅ LOCKED（算法路线）
9. 无日期（"Sprint 2"） | decisions_log.md:105-112 | DEC-S2-003 | DSP 算法 Agent + 硬件设计 Agent，经 Critic | 16→24ch 真正约束为 I/O（2×SPORT/TDM-32 + 3×ADAU1962A）；📋 CONFIRMED
10. 无日期（"Sprint 2"） | decisions_log.md:116-128 | DEC-S2-004 | 专利文献 Agent，经 Critic | Boone EP1986464A1 降为低风险；关注 Fincham 类 broadside 专利（约 2027 到期）；Dolph-Chebyshev 公有领域；5 个差异化专利方向；📋 CONFIRMED（方向待 CTO 批）
11. 无日期（"Sprint 2"） | decisions_log.md:132-144 | DEC-S2-005 | 硬件设计 Agent，经 Critic | BOM：ADAU1966A、TAS5825M、24.576MHz TCXO、明纬电源；16ch ¥1169-2065；21569 单价由 Critic 修正为 ¥120-220；📋 CONFIRMED

### 1.D Gate 与 2026-05-26 CTO 裁决
12. 2026-05-26 | decisions_log.md:148-154 | Gate 1 | CTO（总工），基于 PM + Critic 评审 | 首次阵列设计方案 PASSED：N=16/d=30mm/Dolph-20（本条原文未加 PF-8 作废标，见 §5-6）
13. 2026-05-26 | decisions_log.md:156-160 | Gate 2 | CTO（总工） | ADSP-21569 确认，进入采购流程；✅ CLOSED
14. 2026-05-26 | decisions_log.md:166-172 | PEND-001→DEC-S2-006 | CTO（总工） | 锁 d=30mm → ⚠️ 作废(PF-8)：系 Sprint2 视觉估测 [L0 目测]，由 DEC-S3-GEOM-01（2026-05-29）撤销
15. 2026-05-26 | decisions_log.md:176-182 | PEND-002→DEC-S2-007 | CTO（总工） | N=16；✅ LOCKED
16. 2026-05-26 | decisions_log.md:186-191 | DEC-S2-008 | CTO（总工） | Dolph-Chebyshev −20dB；✅ LOCKED
17. 2026-05-26 | decisions_log.md:195-200 | DEC-S2-009 | CTO（总工） | 4 子带（500-1k/1k-2k/2k-4k/4k-8k）；✅ LOCKED
18. 2026-05-26 | decisions_log.md:204-208 | DEC-S1-004（Gate 2 复核） | CTO（总工） | ADSP-21569 最终确认（不可逆采购）；📋 CONFIRMED（已进采购流程）
19. 2026-05-26 | decisions_log.md:212-217 | PEND-003→DEC-S2-010 | CTO（总工） | 差异化专利申请推迟到 Sprint 4；⏸️ DEFERRED
20. 2026-05-26 | decisions_log.md:221-226 | PEND-004→DEC-S2-011 | CTO（总工） | 批准委托专利代理核查 Fincham 类中国同族；✅ APPROVED（Sprint 3 执行）

### 1.E Sprint 3 Carry-Forward 风险表（:230-274，含后期回填）
21. 2026-06-03（回填） | decisions_log.md:234 | R1 行 | — | EZKIT [L1] `cyc_8ch_frame`=1,006,935 → 8ch 裕量 1.32×；桌面 33×/17× 高估约 25× → FIRA 由可选转必需；core-only bit-exact PASS crc=0x90556BC7；R1 绑 8ch（DEC-S4-R1-8CH-01）
22. 无日期 | decisions_log.md:235 | R2 | — | 已关闭：端到端 12.53ms（scipy，非实测），规格放宽 <30ms（DEC-S2-012）
23. 无日期 | decisions_log.md:236 | R3 | — | 绝对 SPL 盲区（竞品 0° 106-111dB），待单元选定 + 消声室
24. 无日期 | decisions_log.md:237 | R4 | — | 已关闭（PF-8，d=30 撤销，moot）
25. 无日期 | decisions_log.md:238 | R5 | — | d=55 BW@1k=29.28° [L2] 仅 0.72° 余量 = 主路线唯一 BW 风险；超指向 fallback 待消声室
26. 无日期 | decisions_log.md:239 | R6 | — | 栅瓣 6.2–8kHz；规格降级 8k→6k 对内/5k 对外（critic PASSED）
27. 无日期 | decisions_log.md:240 | R7 | — | watch：PRD 新增 6–8k 强指向 → 自动触发 d 重议（SC-S3-GEOM-01）
28. 无日期 | decisions_log.md:241-245 | R8–R12（JY/T 表9/表10） | — | R8 500/30° 一级仅 +0.86dB；R9 180° 不可评（高）；R10 2k/90° 仅二级；R11 4k/30° 仅 +1.01dB；R12 表10 未评估
29. 无日期 | decisions_log.md:246 | R13 | — | 后腔连通无吸音棉 [L1 硬件，KB-HW-002 Q-⑥]，加剧 R9
30. 2026-06-02 | decisions_log.md:247 | R14（新增） | "CTO 拍板 2026-06-02" | FIRA 定点 bit-exact（Q15↔Q31）偏差，🔴 HIGH；不影响纯核选型
31. 2026-06-02 | decisions_log.md:249-259 | R14 完整字段登记 | CTO 拍板 | 🔒 不可逆闸门：R14 关闭前严禁把 FIRA 收益写进选型/流片/客户承诺（C9 守门）
32. 2026-06-02 | decisions_log.md:261-266 | GAP-SAT 登记 | — | 饱和路径 bit-exact 未测；低优先，不阻塞 R1
33. 2026-06-04 | decisions_log.md:268-272 | GAP-SAT 处置更新 | — | closed-by-topology：F5-B 删 8→1 求和 wrapper；"CTO 锁定产品拓扑 = 8 通道各自独立输出到 8 个 DAC…broadside = 声学叠加"
34. 2026-06-04 | decisions_log.md:273-274 | GAP-SAT 前提验证 | — | F5-C 三轨验证全权重 ≤1.0 → premise-VERIFIED

### 1.F Sprint 2 补做 + Sprint 3 启动（2026-05-26）
35. 2026-05-26 | decisions_log.md:280-290 | DEC-S2-012 | CTO（总工） | 端到端延迟 <5ms → <30ms（12.53ms 为 scipy 解析/仿真，非实测）；✅ LOCKED-IN-PRINCIPLE（"草稿待市场/客户对齐后正式生效"，`spec_change_latency.md`）；关闭 R2
36. 2026-05-26 | decisions_log.md:294-306 | DEC-S2-013 | CTO（总工） | 1kHz 温和超指向（MVDR ε=0.01，BW@1k 55.2°→35.4°）原则同意；4 项补充评估排 Sprint 3；📋 APPROVED-IN-PRINCIPLE
37. 2026-05-26 | decisions_log.md:310-316 | DEC-S2-014 | CTO（总工） | Sprint 3 分级采购：立即批准 EV-21569-EZKIT（下单索货期）、CCES + SHARC Audio Toolbox、消声室档期（按 6 周后倒推）；并行喇叭单元供应商联络；暂缓 Codec/功放/电源；✅ APPROVED（`sprint3_procurement_kickoff.md`）
38. 2026-05-26（节标题） | decisions_log.md:320-332 | DEC-S3-001 | CTO（总工） | "硬件平台快速验证法"（保留竞品喇叭/功放/箱体，主控换 EZKIT+转接板），与自研并行；EZKIT 可立即下单（海外周期长）；转接板 PO 须《6 项未知量拆机确认报告》签署后；"转接板须自带 16ch DAC（EZKIT 板载仅 12ch）"；法律红线；✅ APPROVED（有条件）
39. 2026-05-26（节标题） | decisions_log.md:334-338 | DEC-S3-002 | CTO（总工） | 第一动作 = 拆机逆向 + 6 项未知量（U1–U6）；工单 `sprint3_teardown_workorder.md`；✅ APPROVED

### 1.G 2026-05-27
40. 2026-05-27 | decisions_log.md:342-369 | DEC-S3-003 | CTO（总工）；合法性边界"Critic Agent 裁定，REV-S3-CRITIC-001" | 竞品借鉴三阶段（短期以竞品 N=16/d=55/L=825/8 路 A/B 串联作工程基准；中期自研主板；长期自主选型量产）+ 合法/红线表；归档 `knowledge_base/competitor/full_teardown_v2.md`；✅ APPROVED
41. 2026-05-27（节标题"CTO 独立 review + Python 物理核验后拍板"） | decisions_log.md:375-383 | DEC-S3-DSP-03 | CTO（总工） | 接受 8 路 A/B 对称串联 broadside-only（无电子偏转）；裕量 27×→49×；关闭 R-S3-DSP-03；✅ APPROVED
42. 2026-05-27 | decisions_log.md:385-391 | DEC-S3-DSP-04 | CTO（总工） | 1kHz 超指向降级为"实测后可关闭"（d=55 BW@1k=29.3° 原生满足）；✅ APPROVED（重审中）
43. 2026-05-28（复核备注） | decisions_log.md:388 | DEC-S3-DSP-04 备注 | — | 29.28° 经 MATLAB R2026a + 手动积分双确认；AC-WP01 初版半角误判已推翻
44. 2026-05-27 | decisions_log.md:393-398 | DEC-S3-DSP-05 | CTO（总工） | SPL 预测 ~117dB 标"低置信度、仅内部、不可对外"；✅ APPROVED（降级）

### 1.H 2026-05-28
45. 2026-05-28 | decisions_log.md:402-429 | DEC-S3-DSP-06 | CTO（总工）"2026-05-28 重审拍板"；DSP 审计 + 主 Claude MATLAB + Critic REV-S3-BWANGLE（PASS/HIGH）三方推翻初版 | AC-WP01 半角误读纠正：BW@1k 全角 29.28°（非 14.63°）、numpy 无因子-2 bug；作废"撤销超指向"；超指向保持降级/fallback 待消声室；全项目 BW = 全角 −6dB；MINOR-1/2 闭环；✅ RESOLVED
46. 2026-05-28 | decisions_log.md:431-436 | DEC-S3-AC-01 | CTO（总工） | 竞品 4kHz≈19.2° 反常记为存疑，暂不专项实测；📋 NOTED

### 1.I 2026-05-29 几何统一 / 制度（文件位置在 05-28 闸门之前）
47. 2026-05-29 | decisions_log.md:440-466 | DEC-S3-GEOM-01 | CTO（总工） | 撤销 d=30 [L0]，自研基线统一 N=16/d=55mm/L=825mm [L1 拆机]；栅瓣判据 3118/6236Hz；附 CTO 硬约束 SC-S3-GEOM-01 原文（PRD 不新增 6–8kHz 强指向为前提，否则自动触发 d 重议，无 PM 自治权，永久边界）；PF-8 事件经过；✅ LOCKED（强约束）
48. 2026-05-29 | decisions_log.md:470-472, :481 | POLICY-PROV-001 v1.2 / v1.3 | 制度补丁 | v1.2（PF-8）：新增 L0、铁律四、C6；v1.3（PF-9）：铁律五撤回传播 + C7；"✅ 生效（v1.3，2026-05-29）"
49. 2026-05-30 | decisions_log.md:473-480 | POLICY-PROV-001 v1.5 | "CTO（v1.5 已审批 2026-05-30）"；critic 主拟 TASK-POLICY-V15 + PM/文档 agent 落地 TASK-V15-LAND | 铁律七 双轨核 + C5 扩；铁律六 外部输入 24h 入库 + C8；CTO 外部接收声明义务；缘起 LESSON-012（M1 WNG bug）/ LESSON-013（"定向音柱AI数据.docx 硬件团队 5-28 发 CTO、CTO 5-30 才转 KB"）
50. 2026-05-29 | decisions_log.md:481 | E-NEW-3 全库撤回清扫关闭 | "Critic C7 全库终扫 PASS" | 7 组主体 + 全域审计 + 2 项 park 加警示，零裸残留；铁律五三步闭环
51. 2026-05-29 | decisions_log.md:485-489 | SC-S3-GEOM-02 | CTO（总工）（"目标场景…全部水平安装（CTO 签认）"） | 水平安装为锁定前提（JY/T 表9 水平指向）；车站竖装留 Sprint 4；✅ LOCKED（强约束）

### 1.J 2026-05-28 PCB 前闸门 / P0
52. 2026-05-28 | decisions_log.md:493-501 | DEC-S3-PROC-01 | CTO（总工） | 芯片选型不可逆采购冻结至 P0-2 树形 C + EZKIT MCPS 实测；21565 vs 21569 重评窗口开启；EZKIT 采购不受影响；✅ APPROVED（闸门）（状态行补记 P0-2 桌面已完成）
53. 2026-05-28 | decisions_log.md:505-519 | DEC-S3-P0-01 | CTO（总工）；Critic REV-S3-P0 PASS_WITH_MINOR/HIGH | P0-2 树形 C 落地（SNR 182.4dB），MCPS 纠正 16ch=88.7/8ch=45.7（17×/33×）；P0-1 公差 MC；P0-3 超指向 d=55 重算、DEC-S2-013 条件④关闭、端到端 15.11ms；✅ 记录归档
54. 2026-09-26（后加勘误） | decisions_log.md:518 | 勘误 → DEC-S7-RETRACT-SUBBAND-01 | "不改原文" | F-2 "12k/6k/3k/1.5k" 实为 3k/6k/12k，1kHz 在 SB0 内部

### 1.K 2026-05-29 PF-4 / 硬件文档
55. 2026-05-29 | decisions_log.md:523-555 | DEC-S3-PF4-01 | CTO（总工）；Critic 合并评审 PASS_WITH_MINOR | PF-4 定点化桌面闭环 [L2]：Q15 阻带 ≥71.3dB、端到端定点 vs 浮点 74.6–78.7dB；拦截 3 个误导数字（27.7dB 假 FAIL / 316dB PR 假象 / 节点①溢出）；"正面案例"；✅ APPROVED
56. 2026-05-29 | decisions_log.md:557-564 | WO-PF4-NODE1-SAT（DOC-WO-PF4-01） | CTO（总工）"批立即桌面修复" | `tree_filterbank.c:51` 节点①回量化无饱和（半带核绝对值和 1.73）；✅ APPROVED（P1）
57. 2026-05-29 | decisions_log.md:568-585 | DEC-S3-HWDOC-01 | "归档由 project-document teammate 执行；正式签署解锁待 CTO/硬件负责人" | `定向音柱AI数据.docx`（mtime 2026-05-27，5-29 提取；"项目正式收到时间待 CTO 确认 [pending]"）→ KB-HW-001；U1–U6 1/6→6/6 文档级闭环（U1 模拟输入 D 类功放 / U2 16·55 / U3 喇叭 7.4Ω·串联 15Ω、功放 ACM3128A / U4 TDM / U5 主芯片 ADSP-21569KBCZ10 / U6 数模分地）；5 项精度追问 pending；转接板 PO 技术上可解锁待签署；✅ 归档

### 1.L Sprint 4 线索（2026-06-02 ~ 06-04）
58. 2026-06-02 | decisions_log.md:589-601 | DEC-S4-DSP-01 | 节标题"CTO 拍板 G1 决策"；依据"PM 直跑核实" | bit-exact 迁移基准 = C golden（`tree_io_sat/unsat.csv`）+ numpy；G1 MATLAB 独立参考推后不补；✅ LOCKED
59. 2026-06-03 | decisions_log.md:605-615 | DEC-S4-R1-8CH-01 | 节标题"CTO 拍板" | R1 WCET 判据 16ch→8ch；绑定 `cyc_8ch_frame`=1,006,935 [L1/EZKIT] → 1.32×（按 1GHz，CCLK 待实测）；R1 未闭合，靠 FIRA；✅ APPROVED
60. 无日期 | decisions_log.md:623-624 | F-progress F0/F1 | — | F0 闸门 ✅；F1 Legacy + Path B `FixedPointEnable(SIGNED)`（DOC-S4-FIRA-F1-01）
61. 2026-06-03 | decisions_log.md:625 | F2 FIRA 冒烟 | — | 管路 PASS [L1/EZKIT 2026-06-03]：`g_fira_f2_rc=0`、done=1；G2 仍 open
62. 无日期 | decisions_log.md:626 | F3 接真系数 | critic PASS | 草案就绪·待台架（commit 9139de3）
63. 2026-06-04（CTO 确认口径） | decisions_log.md:627 | F4 单通道 bit-exact | "CTO 确认口径 2026-06-04" | "R14 关键里程碑"：FIRA 单通道子带定点 bit-exact（L1，commit 9d9fbec，crc 0x2E0D8C6E）；六轮独立 critic 上板前拦截
64. 2026-06-04（CTO 确认口径） | decisions_log.md:628 | F5 8ch | "CTO 确认口径 2026-06-04" | 8ch 子带定点 bit-exact 上板（44a99e8；F5-C ae4a837；F5-B 360ba7e）；映射 {c,15-c} [L1]
65. 无日期 | decisions_log.md:629 | F6 | — | 原定义"全链 0x90556BC7"作废（无真 8ch golden）
66. 2026-06-04 | decisions_log.md:630 | F7 cycle（DEC-S4-F7-CLOSE-01）+ 流程偏差#2 留痕修正 | "CTO 令"；真·独立 verdict `reviewer: critic @ claude-opus-4-8 / 2026-06-04`（事后补门） | e338288 commit message 预写"critic独立verdict PASS"实为自审 = 假留痕；team_config Fallback 条款（81c4e27）
67. 2026-06-04 | decisions_log.md:631 | C9/铁律八 RELEASED 提示框 | — | FIRA 收益以 [L1] 进选型须连体 §8 未计入清单 43-379 MCPS；官方 3.07x；3.13x 禁入
68. 2026-06-03 | decisions_log.md:633-639 | R14 假绿回退 + 中间层验证 | "CTO 防假绿自查（要求贴码）" | F4b 板读 pass=1/crc=0x90556BC7 实为 FIRA 段 memset 0 占位 + telescoping out=in 的假绿；端到端 CRC 验不了滤波 → 改子带 sb0-3 中间层比对
69. 2026-06-03 | decisions_log.md:641-650 | F4b 首板验 + 自检锚改正 | "CTO 抓出读数门矛盾" | 真 FIRA 首跑（commit 604a1f7）pass=0（预期）；核子带 golden=0x2E0D8C6E；闭合判据改子带级；R14 未闭合
70. 2026-06-03 | decisions_log.md:654-661 | DEC-S4-R14-GRANULARITY | 节标题"CTO 拍板" | R14 闭合判据 = 单通道全链 crc==0x90556BC7；原 F6 作废；GAP-SAT → F5 复议；✅ APPROVED（同日 :639 又称此"端到端粒度判据作废，改中间层"，见 §5-7）

### 1.M 决策状态汇总表（:665-730）
71. —（汇总） | decisions_log.md:667-705 | 汇总表 DEC-S1-001 … DEC-S4-R14-GRANULARITY 各行 | — | 复述上文状态，无新日期（不重复列出）
72. 无日期 | decisions_log.md:706 | DEC-S4-F7-CLOSE-01（汇总行） | — | 3.07x[L1-derived]、2.878x、3.13x 退役；R14/判据/C9 裁定 PENDING CTO（写时口径）
73. 2026-06-04 | decisions_log.md:707 | R14 三裁定（汇总行） | "CTO 正式裁定 2026-06-04" | RULING-01 / CRITERION-01 / C9-RELEASE-01；尾注"正式阈值已定 T2 ≥1.5x，2026-06-05"
74. 2026-06-04 | decisions_log.md:708 | DEC-S5-STEER-V1-01（汇总行） | — | v1 = 聚焦/分区；角度偏转独立立项
75. 2026-06-04 | decisions_log.md:709 | DEC-S5-OPT-ORDER-01（汇总行） | — | HW-1 IIR EQ offload 最高优先 + item-3 EQ PRD
76. 2026-06-04 | decisions_log.md:710 | DEC-S5-POLICY-3GATE-01（汇总行） | — | POLICY v1.8 三道关（含修正稿）
77. 2026-06-05 | decisions_log.md:711 | DEC-S5-OPT-ORDER-02 | "CTO 确认" | 执行序重排：harness+WCET 同板跑优先、R3 第二、HW-1 降可选；"取代 DEC-S5-OPT-ORDER-01"（仅汇总表有此条，无详节）
78. 2026-06-05 | decisions_log.md:712 | H1 FG-BLOCKER→R15 | "CTO 批 fix(a)" | ST1 跨态 CRC 自检设计缺陷；数据 quarantined 不 salvage；MAC-2x 发现（86-144→173-288 [L4]）；尾注 FG-BLOCKER CLOSED 2026-06-05
79. 2026-06-05 | decisions_log.md:713 | WO-S5-H2 实现 | — | DMA/ISR harness 代码就绪，待 critic R19 + 板 hook + 板跑
80. 2026-06-05 | decisions_log.md:714 | KB-DRV-TEST-001 入库提取 | critic R20 第三方核 | 拆机单元 T/S 实测报告：raw 6-01 入库、6-05 提取（"C8 偏差留痕"，逾期 4 天）；19 项 T/S [L1/仪器]；SPLo 82.161 vs 铭牌 88 → 解锁 DEC-S3-DSP-05 SPL 重做
81. 2026-06-05 | decisions_log.md:715 | DEC-S5-SPL-CALIBER-01（汇总行） | — | 内部 94.0 dB @1W [L2]；对外冻结至 R3 L1
82. 2026-06-05 | decisions_log.md:716 | 线③ 厂家函（汇总行） | "CTO 批准线③函稿准发" | 索 Xmax / 热额定功率 / 送测条件
83. 2026-06-05 | decisions_log.md:717 | DEC-S5-BUDGET-L1-01（汇总行） | — | focus 49.03 MCPS [L1]；残余 1.46-2.14x
84. 2026-06-05 | decisions_log.md:718 | DEC-S4-CRITERION-01-FINAL（汇总行） | — | T2 ≥1.5x；尾注"状态更新 2026-06-06：系统侧已保守闭合"
85. 2026-06-05 | decisions_log.md:719 | WO-S5-H2 登记（汇总行） | "待 CTO 排期" | 尾注 2026-06-06：已实现（R19/R24/R25/R26）+ 板跑入账（R27）
86. 2026-06-05 | decisions_log.md:720 | H1 FG-BLOCKER CLOSED | — | R15 snapshot 修 → R16 build 修 → v2 板跑 FG 双门过
87. 2026-06-05 | decisions_log.md:721 | DEC-S5-V1-SCOPE-01（汇总行） | — | v1 = 近场高频展区分区；车站 zoning 剔除；PRD 重写
88. 2026-06-05 | decisions_log.md:722 | DEC-S5-EQ-O1-01（汇总行） | — | EQ = O1 + 保护限幅器 REQUIRED
89. 2026-06-06 | decisions_log.md:723 | H2 板跑读数入账 | critic R27 | EZKIT [L1] 两遍 0% 差；ISR 实际率 ~10-62kHz 非 1kHz（re-arm 缺陷）；M_contention=20.59 必带 relabel
90. 2026-06-06 | decisions_log.md:724 | DEC-S5-T2-CLOSURE-01 | "CTO 裁定选项 A 分体"；"CTO 终裁 2026-06-06"；`reviewer: critic R27+R28 @ claude-opus-4-8` | T2 ≥1.5x 系统侧保守闭合 [L1-保守上界]：DMA 腿 0.038 MCPS [L1 CLEAN]、ISR 腿隔离、95.6 ≤ 210.19；三预留钉 30/15/30；非 clean-L1（仅汇总表，无详节）
91. 2026-06-06 | decisions_log.md:725 | WO-S5-H2R 登记 | "CTO 排期" | ISR 重测四件套；FG-B' 率落 [950,1050]Hz
92. 2026-06-06 | decisions_log.md:726 | 算力优化冻结令 | "维持并正式落档（CTO 2026-06-06）" | HW-1/FRAME/ORCH 全停；例外 = O1 EQ、保护限幅器、SPORT bring-up（"阶段 4"）；解冻 = 可控音柱立项或 margin 击穿 1.5x
93. 2026-06-08 | decisions_log.md:727 | DEC-S6-M1-ARCH-01 | "CTO 拍，基于 claude.ai 总工设计 + critic R34 审查"；critic R31-R36 2026-06-06~08；"CTO 终裁 2026-06-08" | "阶段 4 实时音频通路" M1 四开口：750Hz/64 样本帧、1→8 mono、TX 4096B/RX 512B、M1 不 pin；WO-S6-AUDIO-M1 已派
94. 2026-06-08 | decisions_log.md:728 | M1 上板 PASS + io-callback 口径裁定 | critic R42 | M1 透传 loopback 板上 PASS [L1/EZKIT]（"阶段 4 第一里程碑达成"）；9.629 MCPS 仅 app 负载 (b)，io-callback 核预留 30 [L3] 不动
95. 2026-06-09 | decisions_log.md:729 | F-SRU-1 确定未生效 | critic R48 | softcfg 5 写全失败 → codec 靠载板默认；（CCES 2.12.1 安装版头）；尾注：已被 R55（DEC-S6-FSRU1-RESCOPE-01）re-scope 取代存史
96. 2026-06-08 | decisions_log.md:730 | F-SRU-1 未确认（R44 存史） | critic R44；"CTO 拍是否 apply+重跑" | softcfg_rc=1，换板静默风险 OPEN

### 1.N 锁定基线一览
97. 2026-05-29（更新） | decisions_log.md:732-745 | 锁定基线一览 | — | 单一 d=55 基线；DSP 33×/17×（写时）；<30ms；遗留 R1/R3/R5/R6/R7；:745 数据可信度备注"2026-05-28 经 MATLAB R2026a 全面复算…全部正确"

### 1.O F7 / R14 三裁定 / STEER（2026-06-04）
98. 2026-06-04 | decisions_log.md:750-778 | DEC-S4-F7-CLOSE-01 | "[L1/EZKIT, CTO 实测 2026-06-04]"；"裁定权在 CTO，本条仅录数据"；critic R3–R6 `@ claude-opus-4-8 / 2026-06-04` | FIRA 8ch 463,273 cyc；in-build 核 1,420,543；官方加速 3.07x；8ch 裕量 2.878x；CCLK 实测 1e9（G6 CLOSED）；核-only 0.92x；3.13x 退役；R14 数据采集 COMPLETE
99. 2026-06-04 | decisions_log.md:783-788 | DEC-S4-R14-RULING-01 | CTO 正式裁定（"依据（逐字 CTO）"） | R14 CLOSED；"FIRA 把系统从纯软 0.92x（跑不动）救到能实时"
100. 2026-06-04 | decisions_log.md:790-796 | DEC-S4-CRITERION-01 | CTO 正式裁定（逐字） | ≥10x 判据退役 → 实时下限 + 余量；临时下限 ≥1.0x；:796 尾注"FINAL 2026-06-05 = T2"
101. 2026-06-04 | decisions_log.md:798-803 | DEC-S4-C9-RELEASE-01 | CTO 正式裁定（逐字） | C9/铁律八 RELEASED 附诚实分母（§8 未计入 5 项 + 残余 1.38-2.56x [L4]）；3.07x 锁定，3.13x 禁入
102. 无日期 | decisions_log.md:805-809 | 后续待办（不阻塞 R14） | — | item-3 EQ PRD；WCET 冷 cache；DMA/中断 harness；重读 analyze/synth_fira
103. 2026-06-04 | decisions_log.md:812-828 | DEC-S5-STEER-V1-01 | CTO 正式裁定（"substance 逐字"） | v1 = 聚焦/分区（现板）；角度偏转（拓扑不可达 [L1]，需 16ch 硬件叉 + d 重议）独立立项、CTO 后评 ROI；聚焦增量 86–144 MCPS [L4]、margin 2.04–2.31x；49x/340x 作废
104. 2026-06-04 | decisions_log.md:830-844 | DEC-S5-OPT-ORDER-01 | CTO（substance 逐字） | HW-1 IIR EQ offload + item-3 EQ PRD 最高优先；聚焦 harness 第二；ORCH-4 measure-first likely KEEP（详节未注"已被 OPT-ORDER-02 取代"）
105. 2026-06-04 | decisions_log.md:846-853 | DEC-S5-POLICY-3GATE-01 | CTO（substance 逐字） | POLICY-PROV-001 v1.8 §4B：任何 workflow 产出（含修正稿）三道关；缘起 R8/R9

### 1.P 2026-06-05（v1 收窄 / EQ / 算力线收官 / SPL）
106. 2026-06-05 | decisions_log.md:855-874 | DEC-S5-V1-SCOPE-01 | CTO 正式裁定（"走 (a)"） | v1 zoning = 近场高频展区分区（2–5m、≥4kHz）；车站 zoning 剔除（保留 broadside 定向）；验收"高频近场净隔离 ≥X dB"X 待 CTO/PRD；"PRD 重写 mandated"
107. 2026-06-05 | decisions_log.md:876-896 | DEC-S5-EQ-O1-01 | CTO 正式裁定（"EQ 取 O1"） | 2–3 biquad master-bus 整形 EQ；保护限幅器 REQUIRED、per-channel、T_k=T·w[k]；band 数待 R3；成本 29–60 MCPS [L4]；功放未锁（Plan A ACM3128A / 备选 TAS5825M）
108. 2026-06-05 | decisions_log.md:898-911 | DEC-S5-BUDGET-L1-01（槌一） | CTO 正式裁定 | H1 v2 板跑 [L1/EZKIT 2026-06-05] focus_only=65,371 cyc → 49.03 MCPS；cyc/MAC 8.51；86-144/173-288 双退役；残余 1.46-2.14x [L4]
109. 2026-06-05 | decisions_log.md:913-922 | DEC-S4-CRITERION-01-FINAL（槌二） | CTO（substance 逐字）；达标账"critic R18 F18-MAJOR-1 口径修正" | 正式阈值 T2 ≥1.5x；best 2.14x 达标 / worst 1.46x 差 2.7%；纯算法 2.52x [L1]；"算力线收官归档"；尾注 2026-06-06 保守闭合
110. 2026-06-05 | decisions_log.md:924-929 | WO-S5-H2（登记，未实现） | "CTO 排期" | DMA/ISR small harness = T2 系统侧闭合钥匙
111. 2026-06-05 | decisions_log.md:931-950 | DEC-S5-SPL-CALIBER-01 | 节标题"CTO 拍板"；"线②，不可逆项，CTO 2026-06-05" | 内部 94.0 dB @1W 总输入 [L2 模型，待消声室坐实] 必带标；对外冻结至 R3 L1；117/88 旧值不改；94.0 = SPLo 82.161 + 12.04 − 0.173
112. 2026-06-05 | decisions_log.md:952-956 | 线③ 厂家函 | "CTO 准发 2026-06-05" | Xmax / 热额定功率 / 绝对电平送测条件；回数标 L1/待核
113. 2026-06-05 | decisions_log.md:961-981 | "# 2. RE 层级回显"（落档包残留） | "critic R22 裁 CLEAN" | Re 7.600Ω = 单元级；DC ~15Ω = 整通道级（A/B 串联）
114. 无独立日期（位于 2026-06-05 SPL 裁定包内） | decisions_log.md:985-996 | "# 3. PRD change block" | "critic R23 裁定" | prd_update.md §3.2 新增内部灵敏度 94.0 行；:183（现 :189）承诺行"≥90dB"不改、与 94.0 同口径，~4dB 接近性 FLAG CTO
115. 无日期 | decisions_log.md:1000 | "# 4. 传播（status pointers + 117 库 R7 分类）" | — | 仅标题，无正文

### 1.Q 文档版本页脚（:1004-1010，倒序）
116. 2026-05-29 | decisions_log.md:1004 | 文档 v2.0 | — | PF-8 几何统一修正（DEC-S3-GEOM-01、DEC-S2-006 作废标、R4 关/R5 升/R6/R7 新增）
117. 2026-05-29 | decisions_log.md:1005 | 文档 v1.9 | — | DEC-S3-PF4-01 + WO-PF4-NODE1-SAT
118. 2026-05-28 | decisions_log.md:1006 | 文档 v1.8 | — | AC-WP01 全程闭环
119. 无日期 | decisions_log.md:1007-1008 | 页脚摘要 | — | Gate 1/2；Sprint 2 补做 DEC-S2-012/013/014；Sprint 3 Phase 1-2 DEC-S3-003
120. 2026-05-27 | decisions_log.md:1009 | 页脚摘要 | — | DEC-S3-DSP-03/04/05 拍板归档
121. 2026-05-28 | decisions_log.md:1010 | 页脚摘要 | — | AC-WP01 三方推翻；DEC-S3-DSP-06 RESOLVED；TASK-S3-NUMPY-AUDIT

### 1.R 2026-06-10 ~ 07-20（页脚斜体条目；DEC-S6 段）
122. 2026-06-10 | decisions_log.md:1011 | 团队模型 re-tier（change-control） | "CTO 会话内批准" | lead claude-opus-4-8 → claude-fable-5[1m]；critic/dsp → claude-fable-5（下次 spawn 起）；理由 Fable 5（2026-06-09 发布）、Max 免费窗口至 06-22
123. 2026-06-11 | decisions_log.md:1012 | DEC-S6-FSRU1-RESCOPE-01 | "CTO 采纳"；critic R54 CONDITIONAL→修正→增量过门 @claude-fable-5[1m] | 板身份坐实 = 第三方 AD-EXKIT V2.1 + ADSP-21569-SOM REV 1.1（非官方 EV-SOMCRR-EZKIT）；F-SRU-1 对本载板不适用；override build 取消；判据替换（换同款 AD-EXKIT = 安全）
124. 2026-06-16 | decisions_log.md:1013 | DEC-S6-ALIGN-LEFT-01 | `reviewer: critic @ claude-opus-4-8`（R59，Fable-529-fallback；CONDITIONAL→PASS） | SPORT 字左对齐 → M2 RX/TX 转换 = IDENTITY；OPENING-5 闭合 [L1]
125. 2026-06-16 | decisions_log.md:1014 | DEC-S6-M2-BOARD-PASS-01 | critic R60（CONDITIONAL→修 F60-MAJOR-1→PASS）；"CTO 耳听声音正常" | M2 FIRA 波束上板 PASS [L1/EZKIT AD-EXKIT]（"阶段4 软件部分实质收口"）；R56 死锁修复坐实 overrun=0；beam_cyc_max=830,903 cyc = 帧周期 62.3%（墙钟口径）；点名 WO-S6-BEAMCYC-SPLIT
126. 2026-09-02（后加注） | decisions_log.md:1015 | 注（"CTO 裁定 D12，不改原文"） | CTO 裁定 | "6.4 倍"为跨口径比；同口径 M2/F7 = 1.79×、/H2 base = 1.83×
127. 2026-06-29 | decisions_log.md:1016 | DEC-S6-TEST1-METHOD-01 | "reviewer: pending（PM 现场底稿，待 critic + CTO）" | 整机验证测试1：原"全阵齐放 + 贴近测每对"退役，改逐路 solo；现场 [L1] 16 单元 108.7~111.9dB、1A PASS；测试0 全绿
128. 2026-07-08（后加注） | decisions_log.md:1017 | SUPERSEDED-IN-PART | "铁律四 强制重审 / critic BLOCKER-1" | "1A PASS = 极性确认对"撤回（solo-SPL 对极性盲）；自家阵列极性仍未验
129. 2026-06-29 | decisions_log.md:1018 | DEC-S6-TEST3-METHOD-01 | "reviewer: pending（PM 现场底稿，待 critic + CTO）" | 测试2 极性 PASS（可靠性低）；测试3"1m + 2kHz 纯单音 + 手持"无效退役（1m 为近场，远场 7.9m）；订正法 ≥3~4m、1/3 倍频程粉噪/warble、Leq；非算法 FAIL
130. 2026-07-08（后加注） | decisions_log.md:1019 | REFINED | — | 远场判据不变；07-07→07-08 受控 A/B 表明"平"可有真实物理根因（喇叭混极性）
131. 2026-07-08 | decisions_log.md:1020 | DEC-S6-BEAM-POLARITY-CLOSURE-01 | 独立 critic CONDITIONAL→PASS @claude-opus-4-8；"CTO 签" | 整机"波束平"根因 = 物理 C2/C4 两对喇叭 +/− 接反（接竞品喇叭时接混）；375Hz 逐路成对定位；翻正后 M2 波束恢复指向（1m 近场 18dB@2k / 9dB@1k 为相对证据）；07-01"板 vs 板"差异至今未解释；仍开放：通道映射错位（选项 B）、自家阵列极性（选项 C）
132. 2026-07-19 | decisions_log.md:1021 | DEC-S6-GOVERNANCE-SLIM-01 | "CTO 发起"；独立 critic R1 CONDITIONAL → R2 → clean；"已 commit c3dcd50 + push（2026-07-19，CTO 放行）" | critic skill 去重（agents/critic/skill.md 1124→51 行指针，权威 = `.claude/skills/critic/SKILL.md`）；修 ST1-E/frontmatter；CLAUDE.md"八铁律"→"九铁律"
133. 2026-07-19 | decisions_log.md:1022 | DEC-S6-GOVERNANCE-SLIM-02 | 独立 critic CONDITIONAL→clean；"待 CTO 签"；commit ed83668 + push | CLAUDE.md 294→128 行；新建 PROJECT_REFERENCE.md（移动非删除）
134. 2026-07-20 | decisions_log.md:1023 | DEC-S6-GOVERNANCE-SLIM-03 | 独立 critic PASS；"待 CTO 签" | 删 critic memory 伪造指标 182 行等；R14/C9 状态传播；team_config 矛盾修
135. 2026-07-20 | decisions_log.md:1024 | DEC-S6-GOVERNANCE-SLIM-04 | "CTO 令「过 critic 确认真无用」已满足"；独立 critic PASS | dsp/testing/structure 三个 agents skill 副本改指针（净 −2185 行）
136. 2026-07-20 | decisions_log.md:1025 | DEC-S6-GOVERNANCE-SLIM-05 | 独立 critic 各过 | project-document skill 加溯源纪律；dsp-algorithm skill 678→115 行（砍错平台 ADAU1467，蒸馏真本事）
137. 2026-07-20 | decisions_log.md:1027 | DEC-S6-GOVERNANCE-SLIM-06 | "独立 critic 过，CTO 签" | testing skill 1145→99 行（删虚构实验室；"本项目真 rig = 手机分贝计 + 室外"）
138. 2026-07-20 | decisions_log.md:1029 | DEC-S6-GOVERNANCE-SLIM-07 | "独立 critic 过，CTO 签" | structure skill 883→50 行（结构域零真跑）；revert critic 装饰试点

### 1.S Sprint 7（2026-09-02 ~ 09-03）
139. 2026-09-02 | decisions_log.md:1030 | DEC-S7-SCOPE-01 | "CTO 会话内裁定" | Sprint 7 = 算法层升级；产品层（网络/控制/OTA）不做；硬件仍 AD-EXKIT V2.1 + 21569-SOM；"Stage 5 无进展，线③厂家函无回函，R3 消声室无排期；7-22 后无正式测试"；候选 B1–B6
140. 2026-09-02 | decisions_log.md:1031 | DEC-S7-OBS-OWNRIG-01 | "CTO 2026-09-02 裁定例外"；来源 CTO 口述 | 自家 rig 正面 100 / 侧面约 80（10 项条件全未记录）按 [L0] 隔离登记，不作规格/判据
141. 2026-09-02 | decisions_log.md:1032 | DEC-S7-EXTINPUT-HIT9616-01 | "CTO 裁定"；PM + 独立 critic 双轨核 | 竞品 SPON HIT-9616A12（RK3308）整机固件包"不解包、不分析、不参考"；落盘 mtime 2026-07-31 → C8 逾期 33 天（下界）；ESCALATE
142. 2026-09-02（后加注） | decisions_log.md:1033 | 注（"CTO 裁定 D9（DEC-S7-RULINGS-01）"） | CTO 裁定 | 来源 = 同事自竞品原厂 SPON 获得；渠道与授权未确认；C8 闭合到可闭合程度
143. 2026-09-02 | decisions_log.md:1034 | S7 housekeeping（A3/A4） | "非决策，留痕"；模型变更 approver = CTO in-session | EXP_COMPET_BEAM_VS_FREQ.md 补入库（文内称 07-15 评审；4 数无落盘出处 → 降"未落盘"）；guard_check 改指 m1_cces_project；过期副本加注；lead 模型 → claude-fable-5-1（2026-09-02 起）
144. 2026-09-02 | decisions_log.md:1035 | `reviewer: critic @ claude-fable-5-1` | critic | S7 A 批次 CONDITIONAL-PASS → delta PASS（`CRITIC_A_HOUSEKEEPING_20260902.md`）
145. 2026-09-02 | decisions_log.md:1036 | S7 B 算法层升级提案落库 | "供 CTO 裁定；非决策，留痕"；PM 综合 | 推荐 B6.3（M2 墙钟 830,903 vs bench 463,273 = 1.79×）→ B6.4/B6.5 数值门 → 测试战役 → B1 O1 EQ+限幅；B2 下轮；B4/B5 挂起；B3/B7/全频换窗不做；14 条 CTO 决策清单
146. 2026-09-26（后加注） | decisions_log.md:1037 | 注 DEC-S7-RETRACT-SUBBAND-01 | "不改原文" | B4/B5 所引子带前提撤回
147. 2026-09-02 | decisions_log.md:1038 | `reviewer: critic @ claude-fable-5-1` | critic | S7 B 全包初审 FAIL（1 BLOCKER）→ delta PASS
148. 2026-09-02 | decisions_log.md:1039-1054 | DEC-S7-RULINGS-01 | 标签规则："「CTO 裁定」= CTO 原话；「PM 注」…；「待 CTO 确认」…" | D1 解冻判据用墙钟口径；D2 批 B6.3；D3 批 M2_SELFTEST 等（CTO_OK=1）；D4 B1 t_base=1.0、须待 B6.3；D5 B2 推下轮；D6 B3/B7 不做、B4 挂起、B5-1 不做、B5-2 待确认；D7 测试接自家 16 元阵列；D8 待确认；D9 固件包来源；D10 4 数保持未落盘；D11 删副本；D12 加注；D13 待确认；D14 待权衡
149. 2026-09-26（后加注） | decisions_log.md:1045 | D6 尾注 | — | B5-1 已由 CTO 同意重开（DEC-S7-SIDE30-01 ②）；B5-2 子带前提撤回
150. 2026-09-02 | decisions_log.md:1055-1062 | DEC-S7-IMPL-01 | "CTO 原话（范围与硬约束）"；PM 注 1/2 | 实施第一步只三项：(1) B6.3 墙钟差距对照；(2) B6.4/B6.5 数值门基座；(3) 自家阵列极性 QA 零代码准备；不开始 B1；允许 push b6bc5fe/5adfe91
151. 2026-09-03（后加注） | decisions_log.md:1059 | PM 注 2 闭合 | "由 DEC-S7-RULINGS-02 追认、RULINGS-03 明确为四段含 tx，CTO_OK=1" | —
152. 2026-09-02 | decisions_log.md:1063 | `reviewer: critic @ claude-fable-5-1` | critic | 裁定落库批次 CONDITIONAL → delta PASS
153. 2026-09-03 | decisions_log.md:1064 | S7 IMPL-01 第 2 项落库（D3 包） | — | M2_SELFTEST 八锚、6 宏指纹、#error 守卫、M2_SEG_CYC 四段；[L2 桌面]，板上未验（本机无 cc21k license）
154. 2026-09-03 | decisions_log.md:1065 | S7 IMPL-01 第 3 项落库 | — | `S7_POLARITY_QA_RUNBOOK.md`（电池法 + 375Hz 成对；零期望数值）
155. 2026-09-03 | decisions_log.md:1066 | `reviewer: critic @ claude-fable-5-1` | critic | D3 包 CONDITIONAL→PASS；极性 runbook PASS_WITH_MINOR
156. 2026-09-03 | decisions_log.md:1067 | S7 IMPL-01 第 1 项落库（B6.3） | — | `S7_B63_WALLCLOCK_GAP.md` + probe；M2 工程 Debug "-O 无 value"（优化关）vs bench "-O -Ov=100"；板上数字留空待测试员回填；排查表 15 条
157. 2026-09-03 | decisions_log.md:1068 | `reviewer: critic @ claude-fable-5-1` | critic | B6.3 包 CONDITIONAL → delta PASS
158. 2026-09-03 | decisions_log.md:1069-1080 | DEC-S7-RULINGS-02 | 「CTO 裁定」/「PM 注」 | D6 补：B5-1 不做、B5-2 挂起待 B6.10；D8 不预授权 M2_CHMAP_FIX；D10 补 1.9dB 为仿真 L2；D13 同意；D14 暂不补 license；B1 算本轮但卡 B6.3；M2_SEG_CYC 追认 D3 扩展；内拆分不必做；push 由 CTO 本人；指令预写 `S7_BOARD_RESULTS_INTAKE.md` 后"停止，等测试员数据"
159. 2026-09-03 | decisions_log.md:1082 | `reviewer: critic @ claude-fable-5-1` | critic | 包 1 → PASS；包 2（判读方案 + s7_intake.py）初审 FAIL（1 BLOCKER）→ v2.1 PASS_WITH_MINOR
160. 2026-09-03 | decisions_log.md:1084-1087 | DEC-S7-RULINGS-03 | 「CTO 裁定」/「PM 注」 | S7_PROBE_SYN_FG 不必做；四段（含 tx）追认 CTO_OK=1；B1 条件 0：须测试员实测 CCLK（CGU 寄存器）回填，未回则不满足；PM 注更正把 21568 ÷2 误用于 21569（critic-F delta-3 BLOCKER）

### 1.T S7 侧面 30 dB 线（2026-09-26 ~ 10-02）
161. 2026-09-26 | decisions_log.md:1089 | DEC-S7-RETRACT-SUBBAND-01 | "CTO 会话授权「根据目前的信息先开干」（2026-09-26）" | 撤回"冻结子带树分界 1.5k/3k/6k、子带可分别加权"；实际 3k/6k/12k，detail 带为梳状残差；根因 `tree_filterbank.h:19,24` 注释错 + S7 声学报告 C2 型错标；作废 B5-2 等；15 个 tracked 文件反扫；冻结头不动，改放 ERRATUM 旁注
162. 2026-09-26 | decisions_log.md:1091-1097 | DEC-S7-SIDE30-01 | "CTO 裁定（原话，2026-09-26）：「30 dB 的正式口径、是否重开 D6、是否立项改架构、改板上固件 这些我都同意」"；参数"PM 拟，待 CTO 过目"；门状态"未全部过门" | ① R90 ≥30 dB 正式口径（r ≥8m、1k–4k 七个 1/3 倍频程）；② 重开 D6（允许更深单一加权表）；③"每通道滤波器"路径立项；④ 改板上固件（M2_WTBL_SEL 包）
163. 2026-09-26 | decisions_log.md:1099-1103 | `reviewer: critic @ claude-opus-5-5` | critic | 侧面 30 dB 批次：R1 FAIL（子带边界 BLOCKER → 形成撤回）；R2 CONDITIONAL；R3a FAIL→PASS_WITH_MINOR；涉及 PRD v2.5
164. 2026-09-26 | decisions_log.md:1105-1120 | 每通道滤波器桌面原型落库 | "非决策，留痕"；critic R3b 4 轮 → PASS_WITH_MINOR @claude-opus-5-5 | 8 路线性相位 FIR 稳健设计；装好直接用 16.9–23.0%、配对+微调 ~90%、配对+复数校准 97–100% [L2 on L4 spread]；"配对是最大的杠杆"；算力未证实
165. 2026-09-26 | decisions_log.md:1122-1138 | 测试执行单与配对工具落库 | "非决策，留痕"；critic R3c → PASS_WITH_MINOR | `S7_DRIVER_MATCHING_RUNBOOK.md`、`S7_SIDE30_FARFIELD_TEST.md`（V_FF_MAX 空栏待 CTO）、`s7_driver_pairing.py`
166. 2026-09-27 | decisions_log.md:1140-1153 | FIR 算力 bench 测试包 + 测试员总览页 | "非决策，留痕"；critic R3d → PASS / PASS_WITH_MINOR @claude-opus-5-5 | `sprint7/dsp/firbench/`（63/127/255 抽头，5 路径）；"交给测试员之前须 CTO_OK"；`S7_TESTER_INDEX_SIDE30.md`
167. 2026-09-27 | decisions_log.md:1156 | CTO 同意（引于 09-28 条内） | CTO 回复「我同意，你依次干吧」 | 同意 PM 提议：稳健扇区表做第 5 张表 + 桌面评估 IIR 与延时 CBT
168. 2026-09-28 | decisions_log.md:1155-1197 | 稳健扇区表 RS-A/RS-B 加入 M2_WTBL_SEL（sel 4/5） | "非决策，留痕；执行 CTO 2026-09-27 的同意"；"RS-B 是 PM 在执行中加的第二张"（PM 拟，待 CTO 过目）；critic R3e → PASS_WITH_MINOR | 良率 [L2 on L4 spread]：RS-A 13.6/17.2%、RS-B 10.4/12.3%、D35 6.0/8.1%；修 `run_wtbl_checks.sh` 第 1 步自 7686c05 起不会 FAIL；本包不是选表
169. 2026-09-28 | decisions_log.md:1199-1223 | 低阶 IIR 分频加权与 Keele 延时 CBT 桌面评估 | "非决策，留痕"；critic R3f（FAIL→mini-delta PASS）@claude-opus-5-5；"CTO 常识审：待" | X3-LR4 良率与 FIR 打平但瞬态 +7.4 dB；Duran DDC 原样 4k R90 8.5dB；Keele CBT 弧越宽越差；文献 Keele 2002（登记 #17）、van Beuningen & Start 2000（登记 #12）
170. 2026-09-29（后加注） | decisions_log.md:1225 | 注（"critic R3g F1 / F8 / I7，不改原文"） | critic | 上条把 FIR 当作不受限幅器问题影响不准确；省算力候选改为 LPX3-b
171. 2026-09-29 | decisions_log.md:1227-1237 | S-FIRB CTO_OK | "CTO 裁定，原话：「恩，我同意sfirb可以」" | 每通道 FIR 算力台架可执行（包已入库 0ef46c4）；此前"好"PM 未当作本项授权
172. 2026-09-29 | decisions_log.md:1239-1266 | hybrid「共享线性相位分频 + 每通道频段增益」桌面评估 | "非决策，留痕"；授权 = "CTO 2026-09-29 回复「好」"；critic R3g → PASS_WITH_MINOR @claude-opus-5-5；"CTO 常识审：待" | LPX3-b（127/63 阶）良率≈FIR、方波仅 +1.32 dB、不削顶只退 0.81 dB、MAC 少 4.3–4.8×；PM 拟 LPX3-b 与每通道 FIR 并列候选；保护限幅器须联动（待 CTO）
173. 2026-10-02 | decisions_log.md:1268-1322 | 远场逐带信号文件包 s7ff_v1 落库 | "非决策，留痕；执行 CTO 2026-10-02「好，你先做信号文件」"；交付方式"CTO 会话内选定，2026-10-02"：WAV 进 git；critic CONDITIONAL→delta PASS_WITH_MINOR @claude-opus-5-5；"CTO 常识审：待" | 61 个 WAV（12 带 × 5 档 + 静音，24-bit/48k/36s）；MANIFEST md5 755631003ecdcaa12da95c4d48f79baf；仓库 ~24MB→~0.28GB（进 git 不可逆，CTO 知情选定）；PM 10-01 汇报时指出文件未生成

---

## 2. PRD 版本史（`prd_update.md`，文档 ID DOC-PRD-002）

| 版本 | 日期 | 改了什么 | 出处 |
|---|---|---|---|
| v2.0 | **无日期**（仅写"Sprint 2 竞品逆向"） | "PRD 更新版（基于 Sprint 2 竞品实测）"；竞品对标参数表 N≈20/d≈35/BW 36.6/18.1/9.0°（现已标"已被拆机真值取代"） | prd_update.md:1, :5, :89-103 |
| v2.1 | 2026-05-26 | Gate 1/2 拍板：§0 锁定基线表 N=16/d=30/Dolph-20/4 子带/ADSP-21569；§3.1 BW@2k ≤30°（目标 ≤25°）、栅瓣按 d=30 安全；§3.5 BOM 锁 16ch、阵长 ≈450mm；§4 候选表标 ★（d=30 部分已作废） | prd_update.md:5, :279-285, :417 |
| v2.2 | 2026-05-27 | 新增 §7"Sprint 3 硬件基线"（拆机真值 d=55/L=825/8 路 A/B；ADAU1962A 8ch / ACM3128A / 21569 / TDM-8 / 25MHz 晶振；仿真结论 BW/算力 33×/延迟 12.53ms/栅瓣；[待核实] 清单）；历史 §0–§6 不动 | prd_update.md:5, :309-365, :369-374, :417 |
| v2.3 | 2026-05-29 | PF-8 几何统一（DEC-S3-GEOM-01）：§0 撤 d=30→d=55/L=825 并加 §0-历史；§0.1 写入 SC-S3-GEOM-01；§1 阵列配置；§3.1 强指向上限 6k(对内)/5k(对外)、栅瓣 6.2–8k；§3.2；§3.5 阵长 450→825mm（+72%）；§4 PF-8 归档；§6 R4 关闭、新增 R5/R6/R7 | prd_update.md:5, :378-390, :417 |
| v2.4 | 2026-05-29 | TASK-STD-B：§0.2 SC-S3-GEOM-02 水平安装；§3.1 改 JY/T 表9 12 点 SPL 差值口径（§3.1.2 [L2] 表）+ §3.1.1 双层目标（二级保底=锁定承诺 / 一级冲刺=非承诺，"CTO 拍板"）；BW 降为工程参考；§3.1.4 表10 指标占位；§6 扩列 R8–R12 | prd_update.md:4, :7, :9, :394-403, :416 |
| （未升版、未入版本记录） | 2026-06-05 | DEC-S5-V1-SCOPE-01：§0.2 v1 zoning 定义（:64-70）、§1 场景注（:81）、§3.1.4 新增"高频近场净隔离 ≥X dB"OPEN ITEM（:177）；DEC-S5-SPL-CALIBER-01：§3.2 新增"系统灵敏度（内部工程口径）94.0 dB [L2]"行（:190；change block 见 decisions_log.md:985-996，critic R23）；DEC-S5-EQ-O1-01：新增 §3.4"输出级 EQ / 限幅链"+ 2026-06-05 算力账（T2 ≥1.5x）（:205-216） | prd_update.md:64-70, :81, :177, :190, :205-216 |
| v2.5 | 2026-09-26 | 来源 DEC-S7-SIDE30-01 / DEC-S7-RETRACT-SUBBAND-01：§3.1 新增"侧面抑制内部目标 R90 ≥30 dB（1k–4k，远场自由场）"（口径参数 PM 拟，待 CTO 过目）；"BW@1k ≤30°"内部线降为工程参考（D6 重开）；登记子带分界勘误 3k/6k/12k（"本 PRD 正文未直接引用该边界"）。**表头 :4/:7 与页脚 :416 仍写 v2.4/2026-05-29** | prd_update.md:116-120, :407-412；decisions_log.md:1099（"PRD v2.5"） |

PRD 关键承诺口径（供手册引用）：二级保底 = 唯一锁定承诺、禁承诺一级（:126-133）；灵敏度承诺 ≥90dB SPL/1W/1m（:189）；强指向 1k–6k(对内)/5k(对外)（:160, :187）；SC-S3-GEOM-01 / -02 两条硬约束（:42-72）。

---

## 3. 前期环节线索（仅限这 4 个文件）

### 3.1 需求指标 / PRD 来源 —— **部分有记录**
- 最早可见的需求性裁定：DEC-S1-002"CTO 明确用户需求集中在语音清晰度频段（1kHz 以上）"（decisions_log.md:44-50，Sprint 1，无日期）；目标场景博物馆/车站/商场（prd_update.md:81；decisions_log.md:378）。
- 原始规格数字只在变更记录中可见：延迟原 <5ms（decisions_log.md:280-281；prd_update.md:290）；BW@2k ≤30°/目标 ≤25°（prd_update.md:283）；算力 ≥10×（prd_update.md:198）；灵敏度 ≥90dB（prd_update.md:189）。
- PRD 文档链最早可见版本 = v2.0"Sprint 2 竞品逆向"（无日期，prd_update.md:1-5）；竞品隐含指标"供 PRD 对标参考"（decisions_log.md:82）。
- 标准来源：JY/T 表9/表10（TASK-STD-A/B，`sprint3/audit/standard_compliance_check.md`；prd_update.md:9, :109-113；decisions_log.md:241-245）；GB 3096-2008（prd_update.md:178）。
- 资源约束：2 个 Claude Max plan、基础测量话筒 + 多通道声卡、消声室外租 2000–5000 元/次（PROJECT_REFERENCE.md:61）。
- **未见**：v2.0 之前的初版 PRD、CTO 原始 PRD 文本及日期、需求来自哪个客户/市场的记录；DEC-S2-012"待市场/客户对齐后正式生效"的后续生效记录。

### 3.2 竞品样机拆机 —— **有记录**
- Sprint 1：DEC-S1-001 依据"竞品拆机分析证实主流路线为 ADI 系芯片驱动的线阵相控阵"（decisions_log.md:37）；PROJECT_REFERENCE.md:108（2026-05 写）"竞品已拆机（ADI 系）"。
- Sprint 2：DEC-S2-001 由"竞品实测指向性数据"反推几何（decisions_log.md:79-86）；d=30 是"Sprint2 视觉估测 [L0 目测]"（:167）。
- 2026-05-26：DEC-S3-002 Sprint 3 第一动作 = 拆机逆向 + 6 项未知量，工单 WO-S3-001 `sprint2/docs/sprint3_teardown_workorder.md`（:334-338）；sprint3_status.md:6"2026-05-26 晚…等待拆机"。
- 2026-05-27：DEC-S3-003 拆机真值 N=16/d=55/L=825/8 路 A/B 串联，归档 `knowledge_base/competitor/full_teardown_v2.md`（KB-COMP-001，sprint3_status.md:122）（decisions_log.md:342-369；sprint3_status.md:23-30）。
- 2026-05-29：DEC-S3-HWDOC-01 硬件团队输入 `定向音柱AI数据.docx` → KB-HW-001，U1–U6 文档级闭环（竞品主芯片 ADSP-21569KBCZ10、功放 ACM3128A、喇叭 7.4Ω/3W）（:570-585）；DEC-S3-GEOM-01 d=55 [L1 拆机]（:448）。
- 2026-06-01/05：拆机单元 T/S 送测回报 KB-DRV-TEST-001（:714）。
- 后续：竞品整机仍在手，07-01 "竞品整套只换板"实验、竞品喇叭 rig（:1020, :1031, :1046）；竞品固件包 SPON HIT-9616A12（RK3308）（:1032）——**它与拆机竞品是否同一型号，4 文件内未明说**。
- **未见**：拆机实际执行日期与执行人；《6 项未知量拆机确认报告》正式签署记录（:584-585 写"正式签署待 CTO/硬件负责人"；sprint3_status.md:106 写"等待…正式签署"）；拆机条目中的竞品品牌/型号。

### 3.3 方案 / 芯片选型 —— **有记录**
- DEC-S1-001 技术路线、DEC-S1-004 ADSP-21569（Sprint 1，CTO；decisions_log.md:35-40, :63-73）；Gate 2 2026-05-26（:156-160, :204-208）；DEC-S2-002 树形 FIR、DEC-S2-003/005 I/O 与 BOM（Sprint 2）；DEC-S3-DSP-03 8 路 broadside（2026-05-27，:375-383）；DEC-S3-PROC-01 芯片不可逆采购冻结 + 21565 vs 21569 重评（2026-05-28，:495-501）；FIRA 转必需（2026-06-03，:234）；R14 CLOSED（2026-06-04，:783-788）；功放未锁（ACM3128A Plan A / TAS5825M 备选，:888-889）。
- **未见**：DEC-S3-PROC-01 冻结的解除条目及 21565 vs 21569 重评结论（日志全文 `21565` 仅 7 处，均为开窗/估算语境）；PROJECT_REFERENCE.md:101/:110 写"芯片 LOCKED 21569"；量产芯片采购记录。

### 3.4 开发板 / EZKIT 采购与到货 —— **采购批准有记录；到货未见**
- 批准/计划：DEC-S1-004"EV-21569-EZKIT 开发板可购"（:69）；DEC-S2-014（2026-05-26）立即批准 EV-21569-EZKIT（下单索货期）+ CCES + SHARC Audio Toolbox（:311）；DEC-S3-001"EZKIT 采购可立即下单（海外周期长）""EZKIT 板载仅 12ch"（:326, :329）；sprint3_status.md:14（"等待…EZKIT 采购到位"）、:50、:108（"EZKIT 到货后启动 R1 算力实测"）。
- 间接证据：首个板上 [L1/EZKIT] 数据 2026-06-03（:234, :608-610, :625）。
- 板身份：2026-06-11 DEC-S6-FSRU1-RESCOPE-01 坐实为**第三方 AD-EXKIT V2.1 + ADSP-21569-SOM REV 1.1（非官方 EV-SOMCRR-EZKIT）**（:1012）；2026-09-02 仍是该板（:1030）；CLKIN 25MHz 出处 = AD-EXKIT V2.1 核心板原理图（:1087）。工具：CCES 2.12.1（:729, :1087）；本机 cc21k 无 license（:1053, :1074）。
- **未见**：下单日期、到货日期、为何实际使用第三方 AD-EXKIT 而非 DEC-S2-014 批准的 EV-21569-EZKIT。

### 3.5 GitHub / 论文调研 / 确定框架 / 资料入库 —— **GitHub 未见；其余部分有记录**
- GitHub / 开源调研：**未见**（4 文件 0 处）。只见 git 推送：push 到 origin（:1056）、push 由 CTO 本人执行（:1078, :1097）、"公开仓库的历史"（:1313）。
- 专利/文献：DEC-S2-004 专利调研（Sprint 2，专利文献 Agent：Boone EP1986464A1、Fincham 类、Dolph 公有领域）（:116-128）；DEC-S2-010/011（2026-05-26，:212-226）；Keele 2002（登记 #17，第三方网站副本，AES 版权）、van Beuningen & Start 2000（登记 #12）、Duran DDC（2026-09-28，:1208-1210）；"分析与文献登记"（:1099）。**Sprint 1–2 的算法论文调研记录未见。**
- 确定框架：DAS + 子带（DEC-S1-001）；dyadic 树形半带 FIR（DEC-S2-002）；SHARC Audio Toolbox（DEC-S2-014 :311）；"参考 ADI reference design 自研核心波束"（PROJECT_REFERENCE.md:108）；FIRA 硬件加速（2026-06-03 起，:234）。
- knowledge_base 入库：`competitor/full_teardown_v2.md`（KB-COMP-001，2026-05-27）；`hardware_input/定向音柱AI数据_extracted.md`（KB-HW-001，2026-05-29）；KB-HW-002（:246，无日期）；KB-DRV-TEST-001（raw 2026-06-01、提取 2026-06-05）；`competitor/KB-EXT-SPON-HIT9616A12_FIRMWARE_REG.md`（2026-09-02）；原理图"[L1/vendor-schematic]"（:1012）。入库规则：铁律六 24h（2026-05-30，:475）。

### 3.6 团队 / 治理搭建 —— **有记录（起始日期未见）**
- Agent team：启动 prompt、角色目录树（PROJECT_REFERENCE.md:10-46, :66-95）；Sprint 1 Gate 1 由"Project Manager Agent + Critic Agent"评审（decisions_log.md:57）；Sprint 2"6-agent + 2 轮 Critic"（sprint3_status.md:16）；CLAUDE.md v1.0.0 生成于"2026-05"（PROJECT_REFERENCE.md:118 页脚）。
- POLICY-PROV-001：缘起 PF-1（:13）；v1.2/v1.3（2026-05-29）、v1.5（2026-05-30 CTO 审批）（:470-481）；v1.8 三道关（2026-06-04，:846-853）。
- critic 独立门与模型标签：2026-06-04 流程偏差#2 + team_config Fallback 条款 81c4e27（:630）；模型 re-tier 2026-06-10（:1011）、2026-09-02（:1034）；CTO_OK hook（:1030）。
- 治理减法 SLIM-01~07（2026-07-19/20，:1021-1029）。
- **未见**：agent team 首次组建日期；POLICY v1.0/v1.1 日期；v1.6/v1.7 升级条目（日志只在 :1023 提到 critic skill"v1.7"→v1.8）。

---

## 4. 阶段边界线索

> 日志**没有**"Sprint 4/5/6 启动"的显式条目；这三个边界只能从 ID 前缀（DEC-S4/S5/S6）首次出现推断。前缀表示议题谱系，不严格按日期切：DEC-S4-* 与 DEC-S5-* 在 2026-06-04 同日出现，DEC-S4-CRITERION-01-FINAL（S4 前缀）日期为 2026-06-05。"阶段"（①③/4/Stage 5）是另一套编号，与 Sprint 并存。

| 边界 / 里程碑 | 日期 | 出处 | 原文要点 |
|---|---|---|---|
| Sprint 1 决策（已完结） | 无日期 | decisions_log.md:33-73 | 决策时间均写"Sprint 1"；DEC-S1-003 写"Sprint 1 末" |
| Sprint 2 决策 | 无日期 | decisions_log.md:77-144 | 决策时间写"Sprint 2" |
| Gate 1 PASSED / Gate 2 CLOSED（Sprint 2 收口） | 2026-05-26 | decisions_log.md:148-160；sprint3_status.md:16 | "Sprint 2：✅ 完成（6-agent + 2 轮 Critic）" |
| Sprint 3 启动（有条件 GO） | 2026-05-26 | decisions_log.md:320-338；sprint3_status.md:6；PROJECT_REFERENCE.md:113-115 | "Sprint 3 启动决策（2026-05-26，CTO 拍板）"；"2026-05-26 晚（Sprint 3 有条件 GO，等待拆机）" |
| Sprint 3 Phase 1-2 完成 | 2026-05-27 | decisions_log.md:373；sprint3_status.md:5, :14-21 | 等人工决策进 Phase 3（EZKIT 到位 + 6 项未知量确认） |
| AC-WP01 反转纠正；PCB 前闸门（芯片采购冻结）；P0 桌面仿真完成 | 2026-05-28 | decisions_log.md:402-429, :493-501, :505-519 | — |
| PF-8 几何统一（撤 d=30，d=55 LOCKED）；SC-S3-GEOM-02；PF-4 闭环；E-NEW-3 撤回清扫关闭；POLICY v1.3 | 2026-05-29 | decisions_log.md:440-489, :523-585 | — |
| POLICY v1.5 | 2026-05-30 | decisions_log.md:473-481 | — |
| 首个 DEC-S4 条目（Sprint 4 线索） | 2026-06-02 | decisions_log.md:589-601 | DEC-S4-DSP-01；R14 同日登记（:247-259） |
| 首个板上 [L1/EZKIT] 数据（R1 翻盘，FIRA 转必需） | 2026-06-03 | decisions_log.md:234, :608-610, :625 | — |
| R14 CLOSED / C9 RELEASED / ≥10x 退役 | 2026-06-04 | decisions_log.md:781-803；sprint3_status.md:1 横幅 | — |
| 首个 DEC-S5 条目（Sprint 5 线索）；POLICY v1.8 三道关 | 2026-06-04 | decisions_log.md:812-853 | 日志全文无"Sprint 5"字样 |
| 算力线收官双槌（T2 ≥1.5x） | 2026-06-05 | decisions_log.md:898-922（:917"算力线收官归档"） | — |
| T2 系统侧保守闭合；算力优化冻结令 | 2026-06-06 | decisions_log.md:724, :726 | 冻结令例外含"SPORT bring-up（阶段 4）" |
| 首个 DEC-S6 条目（Sprint 6 线索）；"阶段 4 实时音频通路" M1 架构定稿 | 2026-06-08 | decisions_log.md:727 | — |
| M1 上板 PASS"阶段 4 第一里程碑达成" | 2026-06-08 | decisions_log.md:728 | — |
| 板身份坐实为 AD-EXKIT | 2026-06-11 | decisions_log.md:1012 | — |
| M2 FIRA 波束上板 PASS"阶段4 软件部分实质收口" | 2026-06-16 | decisions_log.md:1014 | — |
| 整机验证测试 0–3（方法订正） | 2026-06-29 | decisions_log.md:1016, :1018 | — |
| 波束极性根因闭合 | 2026-07-08 | decisions_log.md:1020 | — |
| 治理减法 SLIM-01~07 | 2026-07-19 ~ 07-20 | decisions_log.md:1021-1029；PROJECT_REFERENCE.md:4, :101 | PROJECT_REFERENCE（07-19 写）："现已 Sprint 6，芯片 LOCKED 21569，波束已上板" |
| 最后一次正式测试 | "7-22"（无当日条目） | decisions_log.md:1030 | "7-22 后无正式测试" |
| 日志空窗 | 2026-07-20 → 2026-09-02 | decisions_log.md:1029 → :1030 | 期间无任何条目 |
| Sprint 7 启动（范围裁定） | 2026-09-02 | decisions_log.md:1030 | "Sprint 7 范围裁定"；"Stage 5 无进展" |
| S7 实施第一步 + RULINGS-01/02/03 | 2026-09-02 ~ 09-03 | decisions_log.md:1039-1087 | RULINGS-02 指令"停止，等测试员数据"（:1080） |
| 子带分界撤回 + 侧面 30 dB 线立项 | 2026-09-26 | decisions_log.md:1089-1097 | — |
| 最新条目 | 2026-10-02 | decisions_log.md:1268-1322 | s7ff_v1 信号文件包 |

"阶段"编号出处：PROJECT_REFERENCE.md:107（"阶段 ① 需求建模 + 阶段 ③ 算法仿真并行启动"，2026-05 写）；decisions_log.md:726-728, :1014（"阶段 4"）；:1030（"Stage 5"）。4 文件内**未见**阶段 ①–⑤ 的定义表。

撤回 / 作废里程碑：DEC-S2-006 d=30 作废（2026-05-29，:166-172, :442）｜AC-WP01 初版"撤销超指向"作废（2026-05-28，:419）｜E-NEW-3 全库撤回清扫（2026-05-29，:481）｜≥10x 判据退役、3.13x 退役、49x/340x 作废（2026-06-04，:793, :763, :821）｜86–144 / 173–288 MCPS 退役（2026-06-05，:902-908）｜F-SRU-1 旧判据 re-scope（2026-06-11，:1012）｜"极性确认对"撤回（2026-07-08，:1017）｜子带分界 1.5k/3k/6k 撤回（2026-09-26，:1089）。

LOCKED 里程碑：DEC-S1-001~004（Sprint 1）｜DEC-S2-002（Sprint 2）｜DEC-S2-007/008/009（2026-05-26）｜DEC-S3-GEOM-01、SC-S3-GEOM-02（2026-05-29）｜DEC-S4-DSP-01（2026-06-02）。

---

## 5. 疑点

1. **日志表头过时**：decisions_log.md:1 标题仍为"Sprint 1 + Sprint 2"，:4 版本 v2.0，:7 日期 2026-05-26；但页脚 :1004 记 v2.0 = 2026-05-29，日志内容延续到 2026-10-02 却没有升版。
2. **文件顺序 ≠ 时间顺序**：05-29 的 DEC-S3-GEOM-01（:440）排在 05-28 的 DEC-S3-PROC-01（:493）、DEC-S3-P0-01（:505）之前；06-02~06-04 的 R14/GAP-SAT（:247-274）插在 05-26 的 Sprint 2/3 条目中间；汇总表（:665-730）含 06-04~06-09 内容，却排在 06-04/05 的详节（:750-956）之前；汇总表 :729（06-09，R48）排在 :730（06-08，R44）前；页脚版本记录倒序（:1004 v2.0 → :1006 v1.8）。
3. **无日期条目**：Sprint 1 的 4 条与 DEC-S2-001~005 只写"Sprint 1/Sprint 2"，4 文件都没有 Sprint 1/2 的起止日期；DEC-S3-001/002 无"决策时间"字段，只有节标题日期 05-26。
4. **`定向音柱AI数据.docx` 的日期互相矛盾**：:571 写"磁盘 mtime 2026-05-27，今日 5-29 提取归档；项目正式收到时间待 CTO 确认 [pending]"；:478 LESSON-013 写"硬件团队 5-28 发 CTO、CTO 5-30 才转 KB"。KB-HW-001 已在 5-29 提取归档，与"5-30 才转 KB"对不上。
5. **d=30 的等级标注不一致**：decisions_log.md:167/:449 与 prd_update.md:260 标 [L0 目测]；prd_update.md:15 标"[L3/目测]"。
6. **Gate 1 原文未加 PF-8 作废标**：Gate 1（:150-154）与 DEC-S1-003（:54-59）以 d=30 获批，作废标只加在 DEC-S2-006（:166-172）。另外 DEC-S1-003 把 Gate 1 可行性验证写在"Sprint 1 末"，Gate 1 正式 PASSED 写的是 2026-05-26。
7. **DEC-S4-R14-GRANULARITY 前后矛盾**：:654-661 定 R14 闭合判据 = 单通道端到端 crc 0x90556BC7（2026-06-03 APPROVED）；同日 :639 却说"DEC-S4-R14-GRANULARITY（端到端粒度判据作废，改中间层）"，F4/F5 实际按子带 CRC 0x2E0D8C6E 判定。:654 节本身没有作废尾注。
8. **R1 风险没有显式关闭条目**：:612、:704 写"R1 未闭合"；:234 的 R1 行仍是 06-03 口径（"R1 闭合现 gating 于 R14…"）；:743 遗留风险仍列 R1。之后判据演进到 T2 并"保守闭合"（:724, :918），但全文没有"R1 CLOSED"。
9. **被取代的数字没加尾注**：DEC-S5-STEER-V1-01（:818, :820）、DEC-S5-OPT-ORDER-01（:832, :838）、DEC-S5-V1-SCOPE-01（:867）仍写聚焦增量 86–144 MCPS [L4] / margin 2.04–2.31x，没有"已被 49.03 MCPS [L1] 取代"的尾注（退役只记在 :711, :717, :900-909）。DEC-S5-OPT-ORDER-01 详节（:830）也没注"已被 OPT-ORDER-02 取代"（只在汇总行 :711 提到）。
10. **只在汇总表、没有详节的决策**：DEC-S5-OPT-ORDER-02（:711）、DEC-S5-T2-CLOSURE-01（:724）、算力优化冻结令（:726）、DEC-S6-M1-ARCH-01（:727）、M1 PASS（:728）、F-SRU-1 R44/R48（:729-730），以及 H1/H2 系列（:712-713, :719-720, :723, :725）。
11. **落档包残留格式**：:957 有一个前文没有对应开启的 ```；:961/:985/:1000 出现"# 2./# 3./# 4."一级标题，是某个落档包的 §2 回显、§3 PRD change block、§4 传播；"# 4. 传播"没有正文。2026-06-10~2026-10-02 的条目全部以斜体页脚段落追加（:1011-1322），文件里没有对应的 Sprint 6/7 章节标题。
12. **DEC-S3-PROC-01 采购冻结没有解除条目**：21565 vs 21569 重评的结论不在日志里；PROJECT_REFERENCE.md:101/:110 说"21569 LOCKED"。
13. **开发板名称与实物不一致**：2026-06-11 之前，日志一律称"EZKIT / [L1/EZKIT]"，DEC-S2-014 批准采购的是"EV-21569-EZKIT"；2026-06-11（:1012）才坐实实物是第三方 AD-EXKIT V2.1 + 21569-SOM（非官方）。两者之间的采购/到货过程没有记录。
14. **PRD 版本号与内容不同步**：表头 :4/:7 与页脚 :416 仍为 v2.4/2026-05-29，但正文已含 2026-06-05 内容（:64-70, :81, :177, :190, :205-216）和 2026-09-26 的 v2.5 内容（:116-120, :407-412）。2026-06-05 那批改动没有写进版本记录。
15. **PRD 内部有过时或冲突的指标**：
    - 算力：§3.3"DSP 算力裕量 ≥10×"（:198）、§6 R1（:291）没有随 ≥10x 退役更新，而同文件 :215 已写 T2 ≥1.5x。
    - 延迟：§3.3"延迟 ≤20ms"（:200），DEC-S2-012 是 <30ms（decisions_log.md:280），§7.3 又写"12.53ms 满足 <30ms"（:347）；§6 :290 的 R2"4.54ms 逼近广播 <5ms"是旧口径。
    - 编号："§3.4"重复（:205 输出级 EQ/限幅，:218 功耗散热）。
    - BOM：§3.5（:235）仍是"ADAU1966A + TAS5825M×8"，§7.2（:334-336）是 ADAU1962A 8ch + ACM3128A。
    - 子带：§0/§3.3 与 DEC-S2-009 的"4 子带 500-1k/1k-2k/2k-4k/4k-8k"（prd_update.md:23, :196；decisions_log.md:195-200, :737），与 2026-09-26 撤回条目给出的冻结树实际分界"3k/6k/12k（SB0≈0–3k）"（decisions_log.md:1089）字面不一致。这两组数字是什么关系，需 CTO 澄清。
16. **sprint3_status.md 表头日期过时**：表头写"更新时间 2026-05-27"，但正文已含 05-28 内容（P0-2 33×，:36, :85）和 05-29 内容（DEC-S3-GEOM-01、R4 MOOT，:88）；:120-121 的文档索引仍指向 decisions_log v1.3 / PRD v2.2；顶部 :1 另有一条 2026-06-04 状态横幅。
17. **治理条目状态措辞不一**：SLIM-01（:1021）括注"独立 critic pending"，正文却写 R1/R2 两轮已 clean 并已 commit+push；SLIM-02/03 标"待 CTO 签"，之后没有签署记录。
18. **模型变更留痕有缺口**：:1034 记 2026-09-02 起 lead = claude-fable-5-1；但从 2026-09-26（:1099）起 reviewer 标为 claude-opus-5-5，没有对应的 change-control 条目。
19. **事件发生日没有当日条目（事后补记或只被引用）**：07-01 竞品"整套只换板"实验（:1020, :1031）；07-07 静态测试（:1020）；7-09～7-15 测量（:1049"有测量但无单独原始记录"）；07-15 EXP_COMPET 评审（:1034）；7-22 最后正式测试（:1030）；07-31 固件包落盘（:1032，09-02 才登记，逾期 33 天为下界）。KB-DRV-TEST-001 06-01 入库、06-05 才提取（:714 自述 C8 偏差）。2026-07-20 → 2026-09-02 日志完全空白。
20. **第三道关与 PM 拟稿未完成**：
    - "CTO 常识审：待"：:1223, :1266, :1322。
    - "PM 拟，待 CTO 过目"：:1093-1096, :1157, :1211, :1252, :1283。
    - DEC-S6-TEST1/TEST3-METHOD-01（06-29）reviewer pending（:1016, :1018）；之后只有 07-08 的 supersede/refine 注，没有这两条本身的 critic/CTO 结案。
21. **挂起项在 4 文件中没有结案**：
    - DEC-S2-012"待市场/客户对齐后正式生效"（:289）。
    - DEC-S2-010 专利申请"Sprint 4 重启评估"（:217）。
    - DEC-S2-011 中国同族检索（:226）。
    - SC-S3-GEOM-02 车站竖装"留待 Sprint 4"（:488；prd_update.md:62）。
    - DEC-S3-HWDOC-01 拆机报告正式签署（:584-585）。
    - DEC-S2-013 超指向去留"待消声室实测"（:421）。
22. **Sprint 1 拆机线索不清**：DEC-S1-001 的依据已引"竞品拆机分析"（Sprint 1），而 DEC-S3-002（2026-05-26）把"拆机逆向"列为 Sprint 3 第一动作。Sprint 1 那次"拆机分析"的内容和范围，4 文件里没有。
23. **两套编号并存**："阶段 ①/③"（PROJECT_REFERENCE.md:107）、"阶段 4"（decisions_log.md:726-728, :1014）、"Stage 5"（:1030）与 Sprint 编号并存，4 文件里没有对照表。
