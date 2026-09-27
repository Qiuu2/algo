# Critic L：FIR 算力 bench 测试包 + 测试员总览页 R3d（2026-09-27）

> 独立 critic 子代理共三轮报告，要点照录。
> 被审对象：
> - **A 部分**：`sprint7/dsp/firbench/*` 与 `sprint7/docs/S7_FIRBENCH_RUNBOOK.md`，作者为 dsp teammate；
> - **B 部分**：`sprint7/docs/S7_TESTER_INDEX_SIDE30.md`，以及它连带改动的各执行单状态页头、ANALYSIS §6，作者为 PM。
> reviewer: critic @ claude-opus-5-5 / 2026-09-27。

## 第 1 轮：CONDITIONAL

### A 部分：0 BLOCKER / 2 MAJOR / 4 MINOR / 1 INFO

§12 各门均 PASS：
- **FG1**：比对的是逐通道 CRC，不看各通道之和；
- **FG2**：占位系数 48/48 全部 FAIL，模拟器"不写输出"桩也全部 FAIL，板上另有负对照；
- **IO1**：初始化样本数、写回数、每通道独立输出区、读前 cache 失效四项都满足；
- **IO2 / ST1**：通过。

问题：
- **A-1（MAJOR）**：拿 bench 构建（开 -O）的 FIR 周期去加减 M2 构建（-O 未证实）的分段周期，两者口径不一；而且在 S-B 还没做的情况下就写了"已回收"。
- **A-2（MAJOR）**：没有要求回传 `.map` 和关键符号地址。数据放在 L1 还是可缓存的 L2，是影响周期数的一阶因素。
- **A-3（MINOR）**：CORE_C 只是可移植的 C 实现，不是核上能做到的最优，却被说成"真实账"。
- **A-4（MINOR）**：故障表缺兜底行；T8/T1 跨帧复用同一个 CHANNEL_INFO，与 fira_tree.c 的做法不同。
- **A-5（MINOR）**：README 在 [L2] 数字旁写了"实测"。
- **A-6（MINOR）**：补丁直接打在受版本控制的 `bench_main.c` 上，却没有写恢复步骤。
- **A-7（INFO）**：这个 bench 看不出抽头顺序、看不出累加器 bit 15 以下的错误，也没有测到饱和。

### B 部分：0 BLOCKER / 1 MAJOR / 4 MINOR

- **B-1（MAJOR）**：总览页没有标出各执行单的过门状态；而被引用的几份执行单页头还写着"草案 / 待审"，已经过时。
- **B-2（MINOR）**：总览页的会话顺序与 ANALYSIS §6 对不上。
- **B-3（MINOR）**：③、④ 两行漏写了前提（D8、`V_FF_MAX`）。
- **B-4（MINOR）**：没写"喇叭重装后要重做极性 QA"。
- **B-5（MINOR）**：没写 BMODE 和 JP1 这两步；"不早于某个提交"测试员没法自己核对；⑥ 的发回清单不全。

### 确认项

- critic 用自己的代码独立复算 golden，24/24 一致，系数 CRC 与 chirp CRC 也一致；
- 变异测试结果与作者所述一致；
- 补丁的 md5 可以复现，README 的 md5 表 10 个文件全部一致；
- 所有读数符号在代码里都存在；
- T8 的配置与板上验证过的 fira_tree.c 同构 [L1]；T1、P1 的行为作者已标为 [L4]。

## 第 2 轮（delta）：A PASS；B CONDITIONAL

- A-1 至 A-7 全部关闭；复跑全部通过；冻结件和补丁都没有变。
- B-1 至 B-5 关闭，各执行单页头写的过门状态经核实都准确。
- 新发现：
  - **N1（MAJOR）**：ANALYSIS §6 调整顺序后，DRIVER:24、DESIGN:114/:306 这三处引用的步骤号没有跟着改；
  - **N2（MINOR）**：§6 的调整没有写带日期的变更注；
  - **N3（MINOR）**：总览页把调整依据写成了"R3c 的建议"，出处不准确。

## 第 3 轮（mini-delta）：A PASS；B PASS_WITH_MINOR

- N1、N2、N3 和 INFO 全部关闭，全库再搜没有残留。
- 新 MINOR：CRITIC_K:18 是审计记录，被原地改写却没有补注标记。**PM 已在入库前补上**：保留原句，另加"2026-09-27 PM 补注"一行并注明出处。
- **仍需**：S-FIRB 会话要等 CTO_OK 后才能交给测试员。
