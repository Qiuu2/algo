---
name: testing
description: >-
  Test & verification expert for the ITC column speaker. Use for test-case design,
  audio/acoustic performance test procedures, environmental reliability, automation,
  and test-data analysis. Critical: pass/fail criteria must be the right metric and
  must be filter/compute-dependent (no false-green, no placeholder-pass) per CLAUDE.md
  DSP/FIRA special gates.
---

<!-- CANONICAL source of record for the testing skill (DEC-S6-GOVERNANCE-SLIM-04, 2026-07-20);
     agents/testing/skill.md is now a pointer — edit ONLY here. Persona/memory: agents/testing/{profile,soul,memory}.md -->
<!-- 旧内嵌 frontmatter 存史: name "Testing & Validation Agent Skills" / v1.0.0 / ITC Enterprise Agent System -->

# 测试验证专家 Agent — 技能（项目焊接版）

> **从真跑蒸馏**（本项目 `deliverables/algorithm_validation/EXP_*.md` 实测文档 + 测法订正 DEC + `sprint6/STAGE4_*` + critic §12），**不是预制模板**。
> 项目化（roadmap#5，DEC-S6-GOVERNANCE-SLIM-06）：上一版是 2024 通用**立体声 QA** 模板 + 虚构实验室基建；**description 已吹"no false-green/placeholder-pass" 但正文从没实现**——本次让它落地（A4）。已砍见文末。
> **结构**：**A** 项目真本事（逐条带出处）｜**B** 通用骨架（标注）｜**C** 缺口（薄、不编造）。**每数字挂 L 标；相对/近场值绝不冒充远场规格。**

---

# A. 项目真本事（蒸馏所得，每条带出处）

## A0. 测试目标 & 真 rig（先吃，一切前提）
- **被测 = 单声道广侧柱**（M2 FIRA broadside v1：每路 = FIRA(input×Dolph w[c])，全同相，无偏转；喂**单 mono**）——**不是立体声**。`← STAGE4:34-36; EXP_CHMAP_AB.md:39`
- **几何**：16 元线阵 / d=55mm / L=825mm / broadside；每路驱**对称镜像串联对 {c,15−c}**（c7=中心对、c0=最外）。`← STAGE4:36,38; TEST1_FIELDLOG:17; DEC-S3-GEOM-01`
- **8 路输出 = 单端 DAC1P–DAC8P（无 N 脚）→ 极性只可能在喇叭端翻**。`← BEAM_POLARITY_CLOSURE:14 (③,[L1 硬件])`
- **真测量 rig = 手机分贝计（半定量）+ 室外空旷地**；本底 40dB[L1]、solo 87.5dB[L1]。别假设消声室/APx。`← TEST1_FIELDLOG:86; BEAM_POLARITY_CLOSURE:27`
- **核心判据 = ±90° 落差 ≥12dB**（保守门；理论旁瓣 −20dB，留反射裕度）。`← STAGE4:136,171`

## A1. 真跑通/订正的测法（本项目实战，优先照用）
- **远场距离按频点**：Fraunhofer 2L²/λ（L=0.825）→ **1k≥4m / 2k≥8m / 4k≥16m**；**退役"1m+纯音+手持"**（1m 是近场，方向图没成形）。`← DEC-S6-TEST3-METHOD-01 (decisions_log:1016); EXP_CHMAP_AB.md:56; STAGE4:114`
- **信号 = warble(±5%) 或 1/3 倍频程粉噪，读 Leq**（非纯音，带宽平掉梳状零点）；**别混用**(粉噪±12% 太宽)。`← EXP_CHMAP_AB.md:68; EXP_COMPET:40`
- **375Hz 逐对极性定位**：等幅单音、一次一路掩码、**参考=中心路**；同极性 +6dB 相长 / 反极性深零点相消。实证：C7+{C0,C1,C3,C5,C6}=93.5dB、C7+{C2,C4}=71dB → C2/C4 反接。`← EXP_STATIC_POL375.md:§5; BEAM_POLARITY_CLOSURE:15`
- **受控 A/B（只改一个变量）**：mapfix = 单 build、JTAG 活切 `s_m2_chmap`（A={0..7}现状 / B={4,5,6,7,0,1,2,3}修对），**同二进制/麦/音量,只差 8 字节**。`← EXP_CHMAP_AB.md:41`
- **竞品 beam-vs-freq 对比**：甲(竞品)/乙(我们)/**丙(单喇叭对照)** 同场背靠背；**丙测单喇叭方向图 E(θ,f),从甲乙 dB 域扣除得纯阵因子**再比。`← EXP_COMPET:18,22 (§1b 决定成败)`
- **电池纸盆极性测**：1.5V(或 9V 极短瞬触)碰喇叭端子看纸盆外弹/内缩=逐只极性**定论**(测机械位移,不靠声压)。`← EXP_STATIC_POL375.md:93 (§7)`
- **地面反射门控**(小场地退路):REW/ARTA 脉冲加窗,截直达声在首反射前=准远场极图。`← EXP_CHMAP_AB.md:64`
- **逐路 solo**(替代整阵齐放,DEC-S6-TEST1-METHOD-01);**静态缓冲差分测**(软件无示波器:填静态 Dolph+跳 beam poll→撕裂构造上不可能→静态出指向=固件/仍平=硬件)。`← TEST1_FIELDLOG §5-6; EXP_STATIC_TXTEST.md:§0`

## A2. 坑 + 触发器库（看到症状先查这里，各挂来源）
- **0° 不是最大 / ±30-60° 比 0° 响** → **1m 近场 Fresnel 假象**(1m≪远场 7.9m@2k),非算法坏 → 远场 ≥8m 重测。`← STAGE4:115; TEST1_FIELDLOG:110`
- **"16 路 solo 都响且齐" 却怀疑极性** → **solo-SPL 对极性天生盲**(取反=波形×−1,幅度/RMS 不变,分贝一样)→ 只能成对相消或电池测。`← test3-diagnosis-state（CTO 追问逼出）; BEAM_POLARITY_CLOSURE:90 (§7)`
- **整阵齐放贴测每对 → 读数乱(挪几 cm 差 10dB)** → 近场相干干涉(Dolph 锥化 6dB < ±10dB 抖动,SNR<1);c5 首测 −9.7dB 是零点、solo 复测反是最响。`← TEST1_FIELDLOG:28-49`
- **同角度时间上跳 10+dB** → 纯音驻波(2k 零点间距 85.8mm)+ 风/湍流漂移 + 手持晃过半波 → warble/Leq/三脚架/防风棉/无风。`← TEST1_FIELDLOG:112; STAGE4:116`
- **60/90° 巧合深零点(尤 2k@90°)误导** → 修对版在那"抬高"是正常 → **只判 30°,别用 60/90°**。`← EXP_CHMAP_AB.md:30,81`
- **±30/60° 散布 8-16dB 而 0°/±90° 稳** → 在旁瓣陡坡采样(极值点斜率≈0),方向图存在、是采样问题。`← TEST1_FIELDLOG:111`
- **2250Hz 极性测把外侧对误判反接** → 近场;换 **375Hz**(300-400,500 硬顶)定位极性。`← EXP_STATIC_TXTEST.md:79; EXP_PLAN:20`
- **一对中单只反接在成对/求和测里隐形**(正前自抵消=像"该对坏")→ 先 solo 逐路;**±45° 区分死(静音)vs 内部反接(偶极子离轴瓣抬)**。`← EXP_PLAN:66; EXP_STATIC_POL375.md §0 分辨率边界`
- **4k 在 8m 仍近场**(Fresnel,主瓣按 taper 展宽、非共模)→ 读不准 4k 波束宽,需 ≥16m 或距离不变性检查。`← EXP_COMPET:30 (§2 M1)`
- **平≈近全向不是混极性独有**(死/弱/去相干也平)→ 仍须测,别只凭"平"下结论。`← test3-diagnosis-state (7-07)`

## A3. 判据 & L 标（可证伪的门）
- **±90° ≥12dB [远场]**;**距离 = 2L²/λ [L3]**(1k≥4m/2k≥8m/4k≥16m);**SNR ≥15dB 逐 角度×频率×台 门**。`← STAGE4:136; EXP_CHMAP_AB.md:56; EXP_STATIC_TXTEST.md §4; EXP_COMPET:43`
- **Test1 1A**:每镜像对 L-R 差 ≤1.5dB + 无元件低于均值 >6dB。实测 [L1 2026-06-29]:16 元 108.7-111.9dB(span 3.2)、最大对差 0.9dB、零哑路。`← STAGE4:81; TEST1_FIELDLOG:73`
- **主瓣变宽是正常**:正确 Dolph 用 +3.6° 主瓣宽换 −10dB 旁瓣/+13dB@30°;错位版的"25.7°窄"是假象。`← EXP_CHMAP_AB.md:31; BEAM_POLARITY_CLOSURE §5.1`
- **重复性地板 ~1.5dB [L1]** → −6dB 斜坡上 ±2-3° 波束宽不确定度;**实测的差必须 > 地板**才算数。`← EXP_COMPET:54 (§6④)`
- **>3dB 散布 = 场地太糙,换场**;精确值终归 R3 消声室。左右对称 ≤6dB。`← STAGE4:124,137`
- **Test4 频率**:越高越窄;**≥6.24kHz 栅瓣回归**(证 d=55mm)。`← STAGE4:143`
- **SPL 94.0dB @1W 总输入 [L2 模型,待消声室 R3 L1]**(SPLo 82.161[L1单只]+10log10(16)−taper 0.17;对外冻结至 R3)。`← DEC-S5-SPL-CALIBER-01 (decisions_log:991)`
- **mapfix A/B 门**:B 在 30° 比 A 低 ≥6dB(预测 2k −7dB/1k −13dB [L2 numpy]);不用 60/90°。`← EXP_CHMAP_AB.md:79`

## A4. ★假绿纪律（测试的立命之本——现 skill 只在 description 吹、正文从没做，本次做实）
- **FG1 恒等盲区(BLOCKER)**:测试必须**真依赖被测物**。`out==in` 代数恒等(端到端 CRC)验不了滤波/加速器 → 取依赖滤波的中间值(子带) + **证占位/置零版会 FAIL**。`← critic/SKILL.md §12:1132; CLAUDE.md 假绿段`
- **FG2 占位冒充(BLOCKER)**:compute 被 stub(memset0/#else/未接线)还 PASS = L4 冒充 L1 → **跑占位版确认其 FAIL**。（IO1/IO2/ST1 见 critic §12,任一 FAIL=BLOCKER。）`← critic/SKILL.md §12:1133-1139`
- **测前格式门(防"填错=假结论")**:测量前 JTAG 回读 8 路缓冲,须对上期望 Dolph 比 + 符号 + c7 低字节,否则 fill/build 错 → **停,别测**(否则"静态平"是填错假象=假结果)。`← EXP_STATIC_TXTEST.md §4③(c):53-68; EXP_STATIC_POL375.md §3`
- **受控 A/B 只改一个变量**:mapfix 只差 8 字节;极性闭合 07-07→07-08 **只换 C2/C4 喇叭线、板/build 没动**=干净 A/B,证"板+算法能成波束"。**"平→有指向"这个受控步是最硬证据**(相对、与测距方法无关)。`← EXP_CHMAP_AB.md:50; BEAM_POLARITY_CLOSURE:43,29`
- **相对 vs 绝对口径**:1m 18dB@2k/9dB@1k 是**相对/近场证据,不是远场规格**;别拿近场值报规格。`← BEAM_POLARITY_CLOSURE:29; EXP_PLAN:8`
- **存在性 ≠ 正确性**:门要证 poll 真跑了(`g_m2_fg_beam_live=1`),区分静态模式的"诚实死"(−99)与失败,别在静态跑上读 beam-mode FG。`← EXP_STATIC_TXTEST.md §4(b); EXP_STATIC_POL375.md §1`
- **铁律四强制重审**:L1 实测与已录 DEC 冲突 → 强制重审(极性闭合推翻 DEC-S6-TEST1"极性确认对"=solo-SPL 对极性盲,已撤)。`← BEAM_POLARITY_CLOSURE:90; DEC-S6-BEAM-POLARITY-CLOSURE-01`

## A5. 口径 & 交付纪律
- 现场半定量 SPL 只支撑**相对/对称**判据;绝对波束宽/旁瓣/±90° 有效性规格**待远场/消声室 R3 L1**。每个数字挂 L 标,别把 [L2/仿真] 或近场说成"实测规格"。

---

# B. 通用骨架（通用测试方法，**非本项目蒸馏**；有用则用，别当项目本事）
- **测试用例设计**:等价类划分 / 边界值 / 场景覆盖 / 需求-测试双向追溯（通用方法,本项目具体门见 A3）。
- **测量学基本原则**:先测本底 SNR、固定测点/麦位、取多次中值、报不确定度（本项目现场形态见 A1/A2/A3）。
- **数据分析**:归一化到 0°(或真峰值)再比方向图、误差棒、可复现性检查（本项目应用见 A1 竞品对比 / A3 地板）。

---

# C. 缺口 / 未跑过（保持薄、不编造；要用先补真料）
- **消声室 / R3 远场规格 = OPEN**：现读数全近场 1m;正式 ±90°≥12dB 待远场重测。`← BEAM_POLARITY_CLOSURE:73 (§5.2); STAGE4:19`
- **竞品 beam-vs-freq 测 = 已设计未跑**（EXP_COMPET_BEAM_VS_FREQ.md 是实验程序,待测试员执行）。`← EXP_COMPET 全文`
- **mapfix A/B 远场 = 待测试员坐实**。`← EXP_CHMAP_AB.md §0; test3-diagnosis-state`
- **自家阵列极性从未真验**（C2/C4 是竞品喇叭+我们接线;换回自家须 16 只电池统一极性 + 成对复验,装配 QA / 选项 C）。`← BEAM_POLARITY_CLOSURE:74 (§5.3)`
- **环境可靠性(跌落/振动/温湿)= 休眠未跑;量产 Cpk = 无量产** → 保持薄,要做先立真测计划。

---

# 已移除（项目化 roadmap#5 砍掉的错/无关内容，存档说明）
- **立体声 QA**:通道平衡"左右差 ≤1dB"、串扰 L→R/R→L、麦"左右位置固定"——**单声道柱不适用**。`← 原 SKILL.md:169-176,315-338,726-743`
- **虚构实验室基建**:APx515/525(带假序列号+校准日期)、B&K 4190/2669、ESPEC SH-642、LDS V875、pyaudio_precision/InfluxDB/JIRA/自建 CI audio-lab——**本项目真 rig=手机分贝计+室外**,这些不存在。`← 原 SKILL.md:664-796; memory.md:398-497`
- **无关消费级用法**:多设备切换（蓝牙/AUX/光纤）——固定 DSP 评估柱不适用。`← 原 SKILL.md:141`
- **通用 IEC 环境电池**当"适用"陈述:休眠未跑,移入 C。`← 原 SKILL.md:466-603`
- memory.md 里 2022-2024 假缺陷库(347 defects)+ 2023-Q4 假样本表,属同类,另行清理(persona 层)。`← memory.md:164-289`
