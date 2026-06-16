# 板测说明（给测试员，2026-06-16 单次会话版）

> 从已过门的 STAGE4_TESTER_RUNBOOK.md 提炼的精简执行版，只含本次要做的事。
> 你不需要懂代码、不需要判断对错——照步骤做、抄数字、复制发回即可。
> 任何一步报错或读数异常，**原样截图/复制发回，不要自己改、不要猜**。
> 工程：CCES 打开 git 仓的 `m1_cces_project`（=M1_Loopback），**原地** build。

---

## 〇、开始前（一次性确认）
1. **Git 拉最新**：`git pull`
   - 若报 `local changes would be overwritten` → **原样发回**，等回话给 stash 指令，**不要 reset**。
2. 工程已导入 CCES（若没有：File→Import，**「Copy projects into workspace」不要勾**）。
3. **.map 已启用**：Project Properties → C/C++ Build → Settings → SHARC Linker → 勾 **Generate symbol map**。
4. **加载规则**：始终 Load `Debug/M1_Loopback.dxe`（**不要** load `.ldr`）。
5. **build 尾步若只在 loader 步报 FAILED**（提示 2.11.1 / _spi.dxe）：`.dxe` 多半已生成，**确认它在就忽略**继续；其他报错原样发回。
6. **不要在程序里下断点**。流程一律 = Rebuild → Load → Run 几秒 → Suspend → 在 Expressions 窗口读变量。
7. **音源用立体声**（手机/电脑放音乐，左右声道都有），**开到最大音量**，**别用单声道插头**。

---

## 一、第 1 步 —— M1 build（基础透传，取对齐 dump）

1. 确认 Preprocessor 的 Defined symbols 里**没有** `M2_FIRA_INLOOP` 和 `FIRA_USE_REAL_ADI_FIR_HEADER` 两个宏。
2. **Rebuild** → Load `Debug/M1_Loopback.dxe`。
3. **放最大音量立体声音乐 → 点 Run → 耳听透传输出确实响**（没 Run 不出声，别在 Run 前听；不响就加大音量重 Run）→ **保持不间断跑 ~5 秒 → Suspend**。
4. 在 Expressions 窗口读下面这些，逐个抄值发回：

| 变量 | 期望 / 抄什么 |
|---|---|
| `g_m2_fira_inloop` | **应 = 0**（=1 说明 M2 宏没删干净，回〇确认宏并重 build）|
| `g_m1_valid` / `g_m1_fg_stream_live` | 都应 = 1（板上跑起来 + 有音频）|
| `g_m1_rx_block_count` / `g_m1_tx_block_count` | 两个都在增长、且相等 |
| `g_m1_max_abs_sample` | 1 个值（**重要**，见第 6 步对齐判据）|
| `g_m1_main_init_rc` | 应 = 0（注意是 `g_m1_main_init_rc`，不是 g_m1_init_rc）|

5. **对齐 dump（本次核心交付物之一）**：读数组 `s_m1_rx_buf[0][0]` 到 `s_m1_rx_buf[0][7]` 共 8 个值。
   - Expressions 里输入数组名后展开三角号，或逐个输入 `s_m1_rx_buf[0][0]`…；**抄元素的值，不是地址**。
   - 若调试器**看不到这个符号**（file-static），原样记「符号不可见」发回——靠第 6 步兜底。
   - 若 8 个值全是 0 → 注明「无输入/未注入」一并发回。
6. **对齐快速判据（即使 dump 符号看不见也能判）**：在确认音源很响的前提下——
   - `g_m1_max_abs_sample` **> 0x00800000 = 左对齐（好，符合预期）**；
   - ≤ 0x00800000 且确认音量已最大 = 右对齐 → 发回，会给你一个额外宏当天 rebuild 收口（见末尾）。
7. **导出 .map**：先把 `Debug/M1_Loopback.map`（或 .xml）**复制改名为 `map_1A_M1build`** 再做第 2 步
   （第 2 步会覆盖同名文件，上次 1A 的 .map 就是这么丢的）。发回改名后的文件。

---

## 二、第 2 步 —— M2 build（FIRA 波束，本次主测）

> 这是这次的重点：上次 M2 第一帧卡死，已修复，本次验证修好了没。

1. **加两个宏**（Properties → C/C++ Build → Settings → Preprocessor → Defined symbols → Add）：
   `M2_FIRA_INLOOP=1` 和 `FIRA_USE_REAL_ADI_FIR_HEADER`。
   - include 目录 / 链接的 3 个源文件**上周已配过，还在，不用重加**（重加会报 `resource already exists`，报了跳过即可，不是错）。
2. **Rebuild（必须显式做一次）**：Build Project；在 Console 里找 `m1_loopback_tdm.c` 的编译行确认含 `M2_FIRA_INLOOP=1`，**截图保存（=build 凭证）**。
   - ⚠ 不 Rebuild 直接 Load = 烧的还是旧 M1 程序。
3. **⚠ 安全**：第一次跑 M2 前 **功放断电、或音量调到最小**（万一异常会有大噪声）。
4. **Load 新 .dxe → 放同样立体声音乐（1B 期间也要放！）→ 不间断 Run ~5 秒 → Suspend**，读：

| 变量 | 期望 / 抄什么 |
|---|---|
| `g_m2_fira_inloop` | **第一个读，应 = 1**（=0 说明没 Rebuild 或宏没加，回第 2 步）|
| `g_m2_setup_rc` | 应 = 0（=-99 表示 FIRA 没启成）|
| `g_m2_valid` | 应 = 1 |
| `g_m2_fg_beam_live` | 应 = 1（板上只会是 -99 或 1；读到 0 = build 异常）|
| `g_m2_out_nonzero` / `g_m2_out_max_abs` | 都应 > 0（波束有输出）|
| `g_m1_rx_block_count` | 应持续增长（~750/秒）|
| `g_m2_poll_count` | 应 ≈ rx_block_count |
| `g_m2_overrun_count` | 应 ≈ 0 |
| `g_m2_beam_cyc_last` / `g_m2_beam_cyc_max` | 抄值（max 应远小于 1,333,333）|
| `g_m1_fg_stream_live` / `g_m1_nonzero_samples` | 输入活性，抄值 |
| `g_m1_max_abs_sample` / `g_m1_main_init_rc` | 抄值 |

5. **分级听音（「有声」这么拿）**：先在功放断电下读完上表 → **若 `g_m2_out_max_abs` 没顶在 0x7FFFFFFF 附近、且 `overrun_count` ≈ 0** → 功放上电、音量最小 → **重新 Load .dxe → 不间断 Run → 听** → 发回一行话：**正常 / 刺耳 / 无声 / 循环卡顿**。
6. **导出 .map**：复制改名为 `map_1B_M2build`，发回。

---

## 三、第 3 步 —— 恢复 + 打包发回

1. **删掉第 2 步加的两个宏** `M2_FIRA_INLOOP=1` / `FIRA_USE_REAL_ADI_FIR_HEADER`（include/链接源留着无害）。
2. 把以下**全部**发给 CTO（邮箱 `taricqiu@gmail.com` 或约定 IM），由 CTO 转给 PM 判读：
   - [ ] 第 1 步全部读数（含 `s_m1_rx_buf` 那 8 个值，或「符号不可见」）
   - [ ] 第 2 步全部读数
   - [ ] 两个 .map 文件：`map_1A_M1build`、`map_1B_M2build`
   - [ ] build 凭证截图（第 2 步 Console 那行）
   - [ ] 听感一行话
   - [ ] 两个 build 的 Defined symbols 截图各一张（让 PM 确认读数属于哪个 build）
3. 发完**停**，等回话。**不要重烧、不要改 build、不要自己 reset git**。

---

## 红线（务必遵守）
- **听感和 `g_m2_fg_beam_live`/`g_m2_out_max_abs` 只认「第一次不间断运行」的读数**。Suspend 后又 Resume 接着听，声音可能是乱的（计数器还是绿的）——要再听，**重新 Load 重跑**。
- M2 build Suspend 时 PC **偶尔停在 fira 自旋里属正常**，判死活**只看计数器在不在涨**，不看 PC 停哪。
- 任一步不确定 / 报错 / 读数怪 → **原样发回，停手等回话**，不猜不改。
- 第 2 步接线哪步卡住 → **可以只交第 1 步**，注明卡在哪；第 1 步的数据单独也有用。

---

## 附：可能用到的「右对齐应变宏」（仅在 PM 指令下才加）
若第 1 步判出**右对齐**，PM 会让你在 M2 build 上**再加一个宏** `M2_RX_RIGHT_ALIGNED`（和加 M2 宏同一个地方）→ Rebuild → 重测。当天即可收口，不用等下次。**没收到指令就不要加。**

---
*精简自 sprint6/STAGE4_TESTER_RUNBOOK.md（权威源，已过 critic R58）。本说明 2026-06-16 快照。*
