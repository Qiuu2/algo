# Critic 独立对抗复核 — 节点① 饱和修复（TASK-PF4-FIX-RV）

**报告 ID**：REV-PF4-NODE1-SAT-v1
**评审对象**：`tree_filterbank.c` 饱和补丁 + `WO_node1_saturation_fix.md §6` 验证证据
**评审人**：Critic（质量守门员）
**日期**：2026-05-29
**评审深度**：full（独立复算 + harness 逻辑审查，未轻信 PM/teammate 数字）
**口径声明**：本复核全程 HOST gcc 桌面 [L2]，禁称"实测"；SHARC 真值属 EZKIT [L1]，不在范围。

---

## 0. 裁决

> **PASS_WITH_MINOR** — 置信度 HIGH。
> 缺陷前提成立、缺陷确定性复现、修复有效、标称 bit-exact 无回退，全部由 Critic **独立重编译重跑 + 独立 Python 复算**确认，**非轻信 WO 数字**。harness 逻辑自洽（对抗激励真达理论上界、判据真能证伪而非放水），CTO"不能用 DC=1"的要求已满足（用符号对齐满量程 + 满量程方波，非 DC=1）。
> 唯一 MINOR：对抗 harness 的 PASS 判据含一个冗余且非区分性的子句 `out_max<=1.0`（见 F-1），不影响裁决但应澄清。
> **无 BLOCKER。修复可桌面闭环。**

---

## 1. 独立核对 Σ|h|（缺陷前提）[L2]

Critic 自写 Python（Kaiser β=6，63tap，DC 归一化），**不复用 teammate 脚本**：

| 量 | Critic 独算值 [L2] | WO 声称 | 一致 |
|----|------|--------|------|
| Σ\|h_q15\| | 56717 | 56717 | ✓ |
| Σ\|h_q15\|/32768 | **1.73087** | 1.7309 | ✓ |
| DC 增益（Σh_f64） | 1.0000 | DC=1 | ✓ |
| 量化后 DC（Σq15/32768） | 0.99991 | — | ✓（量化误差内）|
| 中心抽头 | 16385 = 0.5000 | ≈0.5 | ✓ |

**结论**：缺陷前提成立——半带核 DC=1 但 Σ\|h\|=1.731>1，回量化 `acc>>15` 最坏可达 1.731× Q31 FS，原 `(int32_t)` 窄化必符号翻转。**[L2]**

---

## 2. 独立重编译重跑对抗 harness（SAT ON / -DTFB_DISABLE_SAT）[L2]

Critic 用 `gcc -O2` 在自己的目录重新编译 `tree_verify_adversarial.c + tree_filterbank.c` 两口径并运行（**用对抗激励，非 DC=1**）：

**激励1（与抽头符号逐点对齐满量程，理论最坏）**：
- `acc>>15 = 3,717,005,310 = 1.7309× Q31 FS`（与 WO 一致）
- SAT OFF（修复前）：`(int32_t) = −577,961,986` → **符号翻转**（正峰翻大负 = 爆音根因）✗
- SAT ON（修复后）：`= 2,147,483,647` → **干净钳位到 Q31 满量程** ✓

**激励2（满量程 3kHz 方波，32768 样点过 L1 半带）**：
- L1 回量化峰值 = **1.1598× FS**，超 FS 样点 = **16368**
- SAT OFF：16368 样点**全部符号翻转**（复现爆音，符合缺陷描述）✗
- SAT ON：16368 样点**全部符号保持、干净钳位**，输出有界 |max|=1.000 FS → **PASS（exit 0）** ✓

→ 三项数字与 WO §6.2 **逐一吻合**。

---

## 3. 独立 Python 复算（库外第三方实现，交叉印证）[L2]

为防"C harness 与库同源自证"，Critic 用纯 Python **从头实现**全长卷积 + 回量化 + 两种窄化语义：

| 量 | Critic Python [L2] | harness/库 | 一致 |
|----|------|--------|------|
| 激励1 acc>>15 | 3,717,005,310（=理论 Σ\|h\|·FS 的 **99.99999%**）| 同 | ✓ |
| 方波 L1 峰值 | 1.1598× FS | 1.1598 | ✓ |
| 超 FS 样点数 | 16368 | 16368 | ✓ |
| SAT OFF 符号翻转数 | 16368 | 16368 | ✓ |
| SAT ON 符号保持钳位数 | 16368 | 16368 | ✓ |

**关键印证**：激励1 达理论上界 Σ\|h\|·FS 的 99.99999%——**对抗激励是真最坏，不是稻草人**（用 INT32_MIN 给负系数项，幅度甚至略超 +FS，确保不低估）。

---

## 4. 独立重跑标称 harness（bit-exact + SNR 无回退）[L2]

Critic 重编译重跑 `tree_verify.c` 两口径：

| 口径 | 重建 SNR [L2] | RMS 误差 | 最大绝对误差 |
|------|------|------|------|
| SAT ON | **177.6 dB** | 2.689e-10 | 4.656e-10 |
| SAT OFF | **177.6 dB** | 2.689e-10 | 4.656e-10 |

- Critic 用自己 fresh 编译的两个二进制各自生成 `tree_io.csv`，`cmp` 比对 → **逐字节完全一致（bit-exact）**。仓库内 `tree_io_sat.csv` vs `tree_io_unsat.csv` 亦 `cmp` 一致。
- 177.6dB ≫ 140dB 门禁 → **SNR 无回退**；饱和在 −4.8dB headroom 内标称信号下**不激活、对标称完全透明**。

> 注：WO §6.1 与代码注释提到旧值"182dB/316dB"，本次实跑两口径均为 177.6dB——属不同激励电平（0.289FS headroom 版）下的量化底，非缺陷，且两口径一致，无回退结论成立。

---

## 5. Harness 逻辑审查（防"测试本身有 bug / 放水"）

| 审查点 | 结论 |
|--------|------|
| **激励1 是否真给 Σ\|h\|·FS 上界？** | ✅ 是。x=sign(h)·FS 逐抽头对齐，Critic 独算达理论上界 99.99999%（负项用 INT32_MIN 幅度略超 → 不低估）。真最坏。|
| **SAT OFF 是否真复现缺陷？** | ✅ 是。库外独立 Python 复算 16368/16368 符号翻转，与 C 一致；非依赖方波边沿良性跳变，而是 acc>>15 真实溢出。|
| **PASS 判据是否真能证伪？** | ⚠️ 见 F-1。判据 = `flip_clamp_ok==sat_events`（所有超FS样点符号保持）**且** `out_max<=1.0`。前者 sound 且具区分力（SAT OFF 时为 0/16368 → FAIL）；后者冗余非区分。|
| **旁路探针与库内饱和语义是否一致？** | ✅ 一致。探针 clamp = `if(q>MAX)MAX; if(q<MIN)MIN`，与库 `sat_i64_to_i32` 同式；钳位按构造不可能翻转符号（q>0→正MAX，q<0→负MIN），Critic 复算确认符号保持数=超FS数。|

### F-1 [MINOR] PASS 判据含冗余非区分子句 `out_max<=1.0`
- **位置**：`tree_verify_adversarial.c:176` `int pass = (flip_clamp_ok==sat_events) && (out_max <= 1.0 + 1e-9);`
- **问题**：Critic 独立比对库**最终输出 y[]** 在两口径下——SAT ON `max|y|=1.0000 FS`，SAT OFF 也 `max|y|=1.0000 FS`（因 int32 输出物理上界恒为 1.0，且合成末级 `sat_add_i32` 与环绕在输出端碰巧都落在界内）。**故 `out_max<=1.0` 在修复前后均成立，无区分力**。但 Critic 同时比对 y[] checksum：SAT ON = −11,253,075,209 vs SAT OFF = −16,384——**库内确实被污染**，只是污染未冒出输出物理上界。
- **影响**：判据**不会放水**——真正的区分项 `flip_clamp_ok==sat_events`（节点①回量化点符号保持）是 sound 的，SAT OFF 下该项必 FAIL。`out_max<=1.0` 仅是冗余加强项，既不会误判 PASS（它对两口径都真），也不削弱另一项。
- **建议（可延期）**：注释里点明 `out_max<=1.0` 是"int32 物理恒真、非区分性"的辅助 sanity 项，真正判据是符号保持；或改为比对 y[] checksum 以让输出级差异显性化。不阻塞关闭。

---

## 6. 来源分级检查 C1–C5（POLICY-PROV-001）— 查 WO §6

| 项 | 结论 | 证据 |
|----|------|------|
| **C1 标等级** | ✅ PASS | WO §6 标题/表头明确 `host gcc 桌面 [L2]`；缺陷上界 `[L3 解析]`；上板标定 `[L1]`。进决策数字均带等级。|
| **C2 无冒充实测** | ✅ PASS | 全文称"host 桌面 [L2]""算法学 MCPS"，**未把 L2/L3 说成"实测/measured"**；§6.3 明确标定属 EZKIT [L1] 未声称。无红线词误用。|
| **C3 无 L4 独撑不可逆** | ✅ PASS | 本工单为桌面代码修复，**不触碰 LOCKED 架构、不触发采购/选型**（§5 明示）。无不可逆决策依赖 L4。|
| **C4 L3 强约束挂待验证** | ✅ PASS | 1.73×/3.46× 上界为 [L3]，但仅用于论证"需加饱和"（方向性），实际修复有效性由 [L2] 对抗实跑证；触发率/headroom 取值显式挂"待 EZKIT [L1] 标定"。|
| **C5 出处可追溯** | ✅ PASS | 指向 `tree_filterbank.c:40-52/85-105`、`tree_verify_adversarial.c`、`sub3_q46_overflow.md §2.4`；Critic 已逐一打开核对，脚本可复现。|

→ **C1–C5 全 PASS，无 BLOCKER。**

---

## 7. 给 PM 的结构化返回

```yaml
verdict: PASS_WITH_MINOR
confidence: HIGH
independent_recompute:                # 全部 Critic 独立复算/重跑 [L2]，未轻信
  sum_h_q15_over_32768: 1.73087        # 自写 Python，缺陷前提成立 (DC=1, 中心0.5)
  adversarial_stim1_acc15: 3717005310  # =1.7309xFS, 达理论上界 99.99999%
  before_fix: "符号翻转 -577,961,986 (爆音根因) ✗"
  after_fix:  "干净钳位 2,147,483,647 (Q31 FS) ✓"
  adversarial_sqwave: "L1峰1.1598xFS; 超FS 16368样点; SAT OFF全翻转 / SAT ON全符号保持钳位; PASS"
  nominal_SNR_both: 177.6 dB           # >>140dB门禁，无回退
  bit_exact: "SAT vs UNSAT 标称 CSV 逐字节一致 (Critic fresh 编译 cmp 确认)"
harness_self_consistent: true
  - 激励1真达Σ|h|·FS理论上界(非稻草人)
  - SAT OFF真复现16368/16368符号翻转(库外Python独立印证)
  - 判据 flip_clamp_ok==sat_events 具区分力且sound、不放水
minor_findings:
  - "F-1[MINOR]: PASS判据子句 out_max<=1.0 冗余非区分(int32输出物理恒界);
     真区分项是节点①符号保持,该项sound。建议注释澄清/改比对y[]checksum。不阻塞。"
provenance_C1_C5: "全 PASS (L2/L3 标注规范, 无实测冒充, 不触不可逆决策, 出处可追溯)"
blocker: NONE
desktop_closure: YES                   # 缺陷确定性复现+修复有效+标称bit-exact, 桌面可闭环
remaining_L1: "节点①实际触发率 + -4.8dB headroom 取值最终标定须 EZKIT 实测(PF-5/[L1]),非桌面范围"
```

---

*REV-PF4-NODE1-SAT-v1，Critic 独立对抗复核。所有数字 [L2 host 桌面]，不称实测。*
