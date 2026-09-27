# 测试员执行单：运行时切换加权表（M2_WTBL_SEL）

> **依据**：DEC-S7-SIDE30-01 ②④（CTO 2026-09-26 同意重开 D6、改板上固件）；`sprint7/docs/S7_SIDE30_ANALYSIS.md` §3。
> **前提（缺一不做）**：
>   1. 自家 16 元阵列极性 QA 已完成，并实测出通道→位置映射（`S7_POLARITY_QA_RUNBOOK.md`）。
>   2. CTO 已就 D8 裁定是否开 `M2_CHMAP_FIX`。
>
>   在接错位置的阵列上换表，测不出任何有意义的东西（critic R2 MAJOR-3b）。
> **过门状态（2026-09-27）**：critic R3a 固件包 PASS_WITH_MINOR → delta 已修（commit `7686c05` / `42f38a0`）；**CTO 常识审待**。
> **2026-09-28 增补**：新增两张"稳健扇区表"。
> - sel 4（RS-A）：CTO 2026-09-27 同意加的那一张，原话「我同意，你依次干吧」。
> - sel 5（RS-B）：PM 追加的第二张，**待 CTO 过目**。CTO 若不要它，本单会改回 sel 0–4。
>
> 本增补已过 critic 门 R3e（第 1 轮 CONDITIONAL → 修正 → delta PASS_WITH_MINOR，`sprint7/critic/CRITIC_M_SIDE30_R3E_20260928.md`）；**CTO 过目：待**。CTO 过目之前，按总览页规矩先请 CTO 看一眼。
> **不写期望读数**：板上和声学的数值由你回填，PM 不替补。下文只写判读规则。

---

## 0. 这个 build 做什么

一个二进制里带 6 张加权表，用 JTAG 改变量 `g_m2_wtbl_sel` 即可切换，不用重编译：

| sel | 表 | 来源 |
|---|---|---|
| 0 | Dolph −20（现表） | 冻结的 `g_dolph_w8_q15`，与现有固件相同 |
| 1 | Dolph −25 | `m2_wtbl_q15.h`，非冻结，由 `sprint7/dsp/wtbl/gen_m2_wtbl.py` 生成 |
| 2 | Dolph −30 | 同上 |
| 3 | Dolph −35 | 同上 |
| 4 | 稳健扇区表 RS-A（侧面优先） | 同上（2026-09-28 新增） |
| 5 | 稳健扇区表 RS-B（保 JY/T 二级裕量；PM 追加，待 CTO 过目） | 同上（2026-09-28 新增） |

- sel 4、sel 5 是专门按"60–90° 侧面 + 喇叭误差"优化出来的表，设计和评估见 `sprint7/docs/S7_SIDE30_ANALYSIS.md` §3.1。它们和 Dolph 表一样是全频段单表，切换方法、读数方法完全相同。
- 所有表的权重都 ≤1.0，而且每一路都不超过现表（sel 0）同一路的权重，所以**正前方音量只会变小，不会变大**。
- 默认值 sel=0，行为与不加这个宏的 build 完全相同。

## 1. 编译（你的 CCES，Debug 配置）

0. 先打开 `sprint6/dsp/audio/m1_cces_project/src/m2_wtbl_q15.h`，确认里面有一行 `#define M2_WTBL_NEXTRA  5`。不是 5，说明代码不是最新：先按总览页第 0 步 `git pull`，再看一次；仍不是 5 就停下，把截图发回。
1. Properties → C/C++ Build → Settings → SHARC C/C++ Compiler → Preprocessor → Defined symbols，在原有的 `M1_TARGET_BOARD`、`TARGET_SHARC`、`M2_FIRA_INLOOP=1` 之外：
   - 加 `M2_WTBL_SEL`（**只写名字，不要写 =0 或 =1**：只要定义了就是开启，写成 `M2_WTBL_SEL=0` 也照样开启；要关闭必须把它从列表里删掉）；
   - 建议同时加 `M2_SELFTEST=1`，让八锚自检证明整条链路健康；
   - D8 裁定要开时，再加 `M2_CHMAP_FIX`。
2. **不能和 `M2_STATIC_TXTEST` 同时加**，同时加会被 `#error` 拒绝编译，这是有意设计的。
3. 编译。任何报错都截图原样发回。
4. **指纹检查**：在 `.map` 里搜 `g_m2_wtbl_sel`，必须能找到；找不到说明宏没有生效，停下来发回。

## 2. 上板读数（功放先断电或调到最小音量）

按 `sprint3/audit/BENCH_OPS_CARD.md` 的 JTAG 顺序上电、Load、Run，然后在 Expressions 窗口依次操作：

| 步 | 操作 | 应看到（判读规则，不是数值期望） |
|---|---|---|
| a | 读 `g_m2_wtbl_sel_applied` | 等于 0：已经跑过帧、默认用现表 |
| b | 读 `g_m2_selftest_rc`（若编了 SELFTEST） | 与 S-B 执行单的判读一致：全 PASS 才继续 |
| c | 写 `g_m2_wtbl_sel = 2`，等 1 秒再读 `g_m2_wtbl_sel_applied` 和 `g_m2_wtbl_applied_sum`；然后依次写 4、写 5，每次同样等 1 秒、读这两个量 | applied 依次变为 2、4、5，说明选择路径生效；每次的 `applied_sum` 都等于下表中对应 sel 的表内权重和，才证明乘进去的确实是这张表的**内容**（正控制） |
| d | 写 `g_m2_wtbl_sel = 6`（比最大合法值 5 大 1），再读 `g_m2_wtbl_sel_applied` 和 `g_m2_wtbl_oob_count` | applied 回到 0，oob_count 持续增长：越界保护生效（负控制）；然后写回 0 |
| e | 读 `g_m2_fg_beam_live`、`g_m2_overrun_count`、`g_m2_beam_cyc_max` | 与 sel=0 时同一量级；切表不增加算力，因为是同一次乘法 |

a、c、d 三步有任何一步不符，就停下来，把截图发回。

**表内权重和**：这是数字恒等，由 `m2_wtbl_q15.h` 和冻结表直接相加得到，[L2 桌面]，不是声学读数。`g_m2_wtbl_applied_sum` 必须与所选表对应的数逐位相等：

| sel | 0（D20） | 1（D25） | 2（D30） | 3（D35） | 4（RS-A） | 5（RS-B） |
|---|---|---|---|---|---|---|
| 8 个 Q15 权重之和 | 211122 | 187690 | 171198 | 158784 | 152407 | 162056 |

（这一行由桌面检查 `sprint7/dsp/wtbl/run_wtbl_checks.sh` 第 4 步用 gcc 编译同两份头文件逐项核对，改表而不改这里会 FAIL。）

第 a 步读到的 `applied_sum` 也应为 211122。开了 `M2_CHMAP_FIX` 时，和不变，因为只是换了排列。**若和对不上**：先读 `s_m2_chmap` 的 8 个值，必须恰好是 0–7 各出现一次；不是的话，说明 JTAG 改坏了映射，先恢复再测。注意这个和只能证明"用了哪张表"，证明不了表内的排列顺序；顺序由桌面 `gen_m2_wtbl.py --check` 保证（critic R3a D2）。

## 3. 声学 A/B

- 测法按 `sprint7/docs/S7_SIDE30_FARFIELD_TEST.md`：远场、分 1/3 倍频程、±90° 与 ±60°、记录 10 项条件与本底。该测试单已于 commit `db301ef` 过门入库（critic R3c 判 PASS_WITH_MINOR，MINOR 已修），**以该 commit 的版本为准**（critic R3a F12）。执行前还要先填好它的 `V_FF_MAX`，并按它的规定把 ±90°/±60° 读数标上"地面反射未隔离"。
- 同一场地、同一麦位，**只改 `g_m2_wtbl_sel` 这一个变量**，顺序为 0 → 3 → 4 → 5 → 0 → 2 → 0。每次切换前把音量调低，切换时可能有轻微的咔声，属于正常现象。
- 一共 7 次测量，外场时间较长。时间不够时，可以省掉最后的"2 → 0"一段，只丢 D30 的数据；前面一段不要拆开。
- 中间和最后各回到 sel=0 复测一次，用来查场地漂移。这是远场测试单 §10 的 A → B → A 纪律；表多了，就在中间多插一次参考。是否漂移、哪几张表因此不可判，由 PM 按该测试单 §10 第 3 条判读；测试员只管照抄原值。
- 本单只测远场测试单规定的 0°、±60°、±90°。`S7_VERIFICATION_PLAN.md` §5.3 的 30° 主判角实验**不在本单内**，何时做、由谁出单待 CTO 定（见总览页 §5）。
- **能下的结论**：只有 [L1 相对]，例如"同条件下 sel=3 比 sel=0 的 90° 读数多压了 X dB"。**不是**绝对规格，不能写成"达到 30 dB 口径"，除非测量条件满足 DEC-S7-SIDE30-01 ① 的全部要求。

## 4. 回填表

| 项 | sel=0 | sel=3 | sel=4 | sel=5 | sel=0（中间复测） | sel=2 | sel=0（最后复测） |
|---|---|---|---|---|---|---|---|
| build 指纹：`.map` 中有 `g_m2_wtbl_sel` | | | | | | | |
| `g_m2_wtbl_sel_applied` | | | | | | | |
| `g_m2_wtbl_oob_count`（第 d 步前 / 后） | | | | | | | |
| `g_m2_wtbl_applied_sum` | | | | | | | |
| `g_m2_beam_cyc_max` | | | | | | | |
| 声学：各频段 R90（按远场测试单的表） | | | | | | | |
