# Critic I：侧面 30 dB 实施批 R3a（撤回 / 分析·DEC·PRD / 固件 M2_WTBL_SEL），2026-09-26

> 独立 critic 子代理的报告，原文要点照录。
> **判定**：包 1（撤回）FAIL，2 BLOCKER；包 2 CONDITIONAL，2 MAJOR；包 3（固件）PASS_WITH_MINOR；总体 FAIL，修正后须 delta 复审。
> **处置**：见文末"PM 修正记录"。delta 复审的判定追加在文末。

reviewer: critic @ claude-opus-5-5 / 2026-09-26

## Findings（原文要点）

1. **BLOCKER（C7）**：`S7_DSP_ASSESSMENT.md:263`"子带机制对 <1.5 kHz 无低频变窄收益"没有加标（+269 的注只覆盖 267–268），登记表第 7 行却写着"逐处加标"，不属实；文档顶部也没有横幅。
2. **BLOCKER（C2）**：统一标签和旁注文件把 [L2 host] 结果写成"实测"。涉及"实测分界 3k/6k/12k"（登记表 §3、两个旁注文件、q15_stopband_sim.py:3、sub1_q15_stopband.md:68）、"实测交叉点"（S7_DSP_ASSESSMENT.md:269）、DEC 中的"critic 在真实树上实测…12–21 dB"。按 §11.1，主机上跑树属于 L2，应逐处改为"[L2 host 复算]"。
3. **MAJOR（C7 准确性）**：
   - `sub1_q15_stopband_v2.py` 头注漏列第 147–149 行（SB1–SB3 的带定义）和第 203 行"<1.5k"；
   - `q15_stopband_sim.py` 漏列第 123 行和第 270–271 行；
   - 登记表第 6 行漏了 `s7_side30_r1_feasibility.log`（"LP-SB0 800-1.5k"）；
   - v2 头注的"数值不受影响"说过头了：detail 带隔离数值是在错误的带上算的，"≈0 dB"这个结论仍然成立，但 −0.1 dB 等具体值不成立。
4. **MAJOR**：DEC-S7-SIDE30-01 头部写"已过两轮独立 critic"，与事实不符（R1 FAIL、R2 CONDITIONAL、R3 待审）。
5. **MAJOR（标签越权）**：③ 的 PM 注写"即视为…对算力优化冻结令（ORCH）与冻结 FIRA 编排的解冻授权"，但 CTO 原话只是"立项改架构"；冻结令有自己的解冻条件（可控音柱立项或击穿 1.5×）。这一句应标为"PM 拟，待 CTO 过目"。
6. **MINOR**：
   - ④"M2 TU 改动 CTO_OK=1"和 ②"BW@1k≤30° 降为工程参考"都是 PM 的操作化，却写在裁定正文里，应改标。
   - 对未来未见的固件包给整体 CTO_OK，超出了逐包先例（d524fde），FIR 路径须单独 CTO_OK。
   - DEC 缺"风险声明"字段。
7. **MINOR**：分析文档 §3 表里混了单频点列（1k/30°：D30 21.8 / D35 17.1）和 1/3 倍频程带平均列（500/90°：D30 20.3 / D35 16.4），表头要标清楚。
8. **MINOR**："守住二级保底"没有给裕量：D35 在 500/30° 为 3.54 dB，对二级门限 3 dB 只有 +0.54 dB [L2 理想]；D30 为 +1.06 dB。
9. **MINOR**：分析文档引用的 `m1_loopback_tdm.c:543-551` 已经过时（乘法现约在 589–597 行）；critic R1 复核脚本硬编码了绝对路径，不能原样复跑。
10. **MINOR（FG1）**：`g_m2_wtbl_sel_applied` 和 `g_m2_wtbl_oob_count` 只是回显编号，证明不了实际用了哪张表的权重。执行单 c 步写"切表生效"说过头了。建议每帧公布所用那一行的 `wt[0]` 或校验和。
11. **MINOR**：`.c` 头注仍写"6 optional macros / 6 fingerprints"；宏目录里漏了 M2_WTBL_SEL。它是 #ifdef 型宏，**`-DM2_WTBL_SEL=0` 同样会开启**（已验证）。guard 注释仍写 X1..X5。
12. **MINOR**：执行单 §3 引用的远场测试单还在待审状态，须等它自己过门后再执行，并钉住 commit。
13. **INFO**：
    - 旁注文件的方式暂时可接受，但打开 .h 或 grep 的人看不到警告。
    - 不加 `_built` 指纹可以接受（M2_SEG_CYC 先例）。
    - "0 cycles"只对乘法本身成立，每帧选表要多几条指令。

**确认项（原文要点）**：
- 物理：SB0 在 2.5k 以下 0.00 dB，2.75k 为 −0.37，3k 为 −6.02，3.5k 为 −71.2；SB1 在 500 Hz 为 +5.95，1k 为 −5.72；PR 误差 8.9e-16。PM 的 −9.0 dB 是奈奎斯特处的采样假象。
- 影响分级正确：B4 逐频率数字保留，B2 待核，PF-4 头条数值不受影响。
- 文献 16/16 的 md5 和字节数一致；脚本复跑与 .log 的差异为 0 行。
- `run_wtbl_checks.sh` PASS，另外 7 组非 WTBL 宏的 gcc -E 输出与 HEAD 相同；Dolph 表逐位复现。
- 所有新权重都 ≤ 同通道的 D20 权重；逐帧快照、越界回退、chmap 掩码均正确；自检读的是冻结表；执行单里的 7 个符号都存在。
- **门**：C1 PASS · C2 FAIL · C3 PASS · C4 PASS · C5 PASS（minor）· C7 FAIL · C8 PASS · C10 PASS · FG1/FG2 PASS（minor）。

## PM 修正记录（2026-09-26）

- **F1**：263 行加标，文档顶部加部分撤回横幅。
- **F2**：全部"实测分界 / 实测交叉点 / 真实树实测"改为"[L2 host 复算]"；PF-4"已实测到"改为"已在桌面仿真 [L2] 中测到"；旁注文件改为"复算结果（[L2 host]，不是 L1 实测）"；SB0 边缘数值按 critic 更正（≤2.5k 为 0 dB，3k 为 −6 dB）。
- **F3**：两个 PF-4 脚本头注补全行号并写明 437 抽头参考核不是树；sub1 v2 与 md 改为"§2.2 带外抑制各数值作废，定性结论与 77.7 dB 抗混叠、重建 SNR 不受影响"；登记表第 6 行补上 r1 log。
- **F4/F5/F6**：DEC-S7-SIDE30-01 头部改为写明门状态并加风险声明；② 的 BW 线、③ 的解冻、④ 的 CTO_OK 都改标为"PM 拟，待 CTO 过目"，FIR 路径须单独 CTO_OK。
- **F7/F8/F9**：分析文档表头标明单频点 / 带平均；补上二级裕量 +0.54 / +1.06 dB；更新行号；R1 脚本 README 注明不能原样复跑。
- **F10**：固件新增 `g_m2_wtbl_applied_sum`，即本帧**实际乘进去**的 8 个权重之和；执行单 c 步要求它与表内权重和逐位相等。
- **F11**：更新 .c 头注和宏目录；写明 `=0` 也会开启；guard 注释改为 X1..X7。
- **F12**：执行单 §3 写明须等远场测试单过门并 commit 后执行。

## Delta 复审（2026-09-26，同一 critic）

**判定**：包 1 PASS，包 2 PASS，包 3 PASS_WITH_MINOR，总体 **PASS_WITH_MINOR**，D1 解决后可以 commit。

- **D1（MINOR）**：DEC ④ 已把"本包归属"改标为"PM 拟"，但 `m1_loopback_tdm.c:125` 和 `m2_wtbl_q15.h:7`（由生成器写入）仍写着"CTO_OK / firmware change approved"。
  - **PM 已修**：两处都改为引用 CTO 原话，并注明"本包归属为 PM 拟、待 CTO 过目"。改动在生成器里做，重新生成后 `--check` 通过；一键门 PASS。
- **D2（INFO）**：`applied_sum` 只能证明用了哪张表，证明不了表内的排列顺序；顺序由 `gen --check` 保证。开了 CHMAP_FIX 时，如果 JTAG 把映射改得不再是 0–7 的排列，和会变，这是故障安全的。
  - **PM 已修**：执行单写明"和对不上时，先检查 `s_m2_chmap`"。
- **CRITIC_I 转录**：critic 确认忠实。

reviewer: critic @ claude-opus-5-5 / 2026-09-26（delta）
