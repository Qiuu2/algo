# 测试员执行单：运行时切换加权表（M2_WTBL_SEL）

> **依据**：DEC-S7-SIDE30-01 ②④（CTO 2026-09-26 同意重开 D6、改板上固件）；`sprint7/docs/S7_SIDE30_ANALYSIS.md` §3。
> **前提（缺一不做）**：
>   1. 自家 16 元阵列极性 QA 已完成，并实测出通道→位置映射（`S7_POLARITY_QA_RUNBOOK.md`）。
>   2. CTO 已就 D8 裁定是否开 `M2_CHMAP_FIX`。
>
>   在接错位置的阵列上换表，测不出任何有意义的东西（critic R2 MAJOR-3b）。
> **不写期望读数**：板上和声学的数值由你回填，PM 不替补。下文只写判读规则。

---

## 0. 这个 build 做什么

一个二进制里带 4 张加权表，用 JTAG 改变量 `g_m2_wtbl_sel` 即可切换，不用重编译：

| sel | 表 | 来源 |
|---|---|---|
| 0 | Dolph −20（现表） | 冻结的 `g_dolph_w8_q15`，与现有固件相同 |
| 1 | Dolph −25 | `m2_wtbl_q15.h`，非冻结，由 `sprint7/dsp/wtbl/gen_m2_wtbl.py` 生成 |
| 2 | Dolph −30 | 同上 |
| 3 | Dolph −35 | 同上 |

- 所有表的权重都 ≤1.0，**正前方音量只会变小，不会变大**；满驱动时轴向约低 0–2.5 dB [L2]。
- 默认值 sel=0，行为与不加这个宏的 build 完全相同。

## 1. 编译（你的 CCES，Debug 配置）

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
| c | 写 `g_m2_wtbl_sel = 2`，等 1 秒再读 `g_m2_wtbl_sel_applied` 和 `g_m2_wtbl_applied_sum` | applied 变为 2，说明选择路径生效；`applied_sum` 等于下表中 sel=2 的表内权重和，才证明乘进去的确实是这张表的**内容**（正控制） |
| d | 写 `g_m2_wtbl_sel = 7`，再读 `g_m2_wtbl_sel_applied` 和 `g_m2_wtbl_oob_count` | applied 回到 0，oob_count 持续增长：越界保护生效（负控制）；然后写回 0 |
| e | 读 `g_m2_fg_beam_live`、`g_m2_overrun_count`、`g_m2_beam_cyc_max` | 与 sel=0 时同一量级；切表不增加算力，因为是同一次乘法 |

a、c、d 三步有任何一步不符，就停下来，把截图发回。

**表内权重和**：这是数字恒等，由 `m2_wtbl_q15.h` 和冻结表直接相加得到，[L2 桌面]，不是声学读数。`g_m2_wtbl_applied_sum` 必须与所选表对应的数逐位相等：

| sel | 0（D20） | 1（D25） | 2（D30） | 3（D35） |
|---|---|---|---|---|
| 8 个 Q15 权重之和 | 211122 | 187690 | 171198 | 158784 |

第 a 步读到的 `applied_sum` 也应为 211122。开了 `M2_CHMAP_FIX` 时，和不变，因为只是换了排列。**若和对不上**：先读 `s_m2_chmap` 的 8 个值，必须恰好是 0–7 各出现一次；不是的话，说明 JTAG 改坏了映射，先恢复再测。注意这个和只能证明"用了哪张表"，证明不了表内的排列顺序；顺序由桌面 `gen_m2_wtbl.py --check` 保证（critic R3a D2）。

## 3. 声学 A/B

- 测法按 `sprint7/docs/S7_SIDE30_FARFIELD_TEST.md`：远场、分 1/3 倍频程、±90° 与 ±60°、记录 10 项条件与本底。该测试单已于 commit `db301ef` 过门入库（critic R3c 判 PASS_WITH_MINOR，MINOR 已修），**以该 commit 的版本为准**（critic R3a F12）。执行前还要先填好它的 `V_FF_MAX`，并按它的规定把 ±90°/±60° 读数标上"地面反射未隔离"。
- 同一场地、同一麦位，**只改 `g_m2_wtbl_sel` 这一个变量**（0 → 2 → 3 → 0）。每次切换前把音量调低，切换时可能有轻微的咔声，属于正常现象。
- 最后回到 sel=0 复测一次，确认场地没有漂移。
- **能下的结论**：只有 [L1 相对]，例如"同条件下 sel=3 比 sel=0 的 90° 读数多压了 X dB"。**不是**绝对规格，不能写成"达到 30 dB 口径"，除非测量条件满足 DEC-S7-SIDE30-01 ① 的全部要求。

## 4. 回填表

| 项 | sel=0 | sel=2 | sel=3 | sel=0（复测） |
|---|---|---|---|---|
| build 指纹：`.map` 中有 `g_m2_wtbl_sel` | | | | |
| `g_m2_wtbl_sel_applied` | | | | |
| `g_m2_wtbl_oob_count`（第 d 步前 / 后） | | | | |
| `g_m2_wtbl_applied_sum` | | | | |
| `g_m2_beam_cyc_max` | | | | |
| 声学：各频段 R90（按远场测试单的表） | | | | |
