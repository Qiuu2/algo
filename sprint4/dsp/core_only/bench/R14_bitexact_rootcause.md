# R14 上板 bit-exact 失败 — 根因报告 + 冻结输入修复

**文档 ID**：DOC-S4-R14-RC-01 ｜ 日期：2026-06-02 ｜ PM 直跑（审计+修复+host 验证）
**挂接**：R14 / 铁律八 ｜ **二值判据**：target crc32 == 重算后 host golden（spot_match=1）

---

## 1. 症状
台架上板 core-only：`target crc32 = 0x21a3d598` vs `golden 0x90556BC7`，`spot_match=0`。
→ 输出**数值级**不一致（非 CRC 移植问题——CRC 算法本身若移植错会全错，而这里是逐样本数值分叉）。

## 2. 审计 float/double 用点（task 1）
| 位置 | 是否用浮点 | 出处 |
|------|-----------|------|
| **chirp 生成（bench_harness.c `gen_input`）** | **是 → double + pow/sin/log** | 原 `bench_harness.c:31,35,36`（`to_q31(double)` / `pow`/`log`/`sin`） |
| 算法核 `tree_filterbank.c` | **否（0）** | `grep -c double\|float = 0`，纯整数 Q15/Q31/Q46 |
| 8ch 包裹 `tfb_8ch.c` | **否（0）** | 同上 |

→ **bit-exact 路径唯一浮点 = 运行期 chirp 生成**。

## 3. 根因（确认 CTO 头号嫌疑成立）
SHARC 编译 `-double-size-32` → `double` 实为 **32-bit float**；host golden 用 **64-bit double**。
chirp 在**运行期**用 `pow/sin/log`（double）算样本 → target（32-bit）与 host（64-bit）**输入样本逐位分叉** → 喂进（本身正确的整数）算法 → 输出数值分叉 → CRC 挂、spot_match=0。
**这是输入级分叉，不是算法级**（算法纯整数、S0-S1 host 已逐位验过）。症状（数值级不一致、spot 全错）与"输入分叉"一致。

## 4. 修复：冻结输入（task 2-3）
- **新增 `gen_chirp_input.c`**：host 64-bit double 算一次 chirp → 输出 **`chirp_input.h`**（`const int32_t CHIRP_INPUT[65536]`）。
- **`bench_harness.c` 改**：删运行期 chirp（`gen_input`/`to_q31`/`<math.h>`/`M_PI`），算法**直接读 `CHIRP_INPUT[]`**（编译期 `chirp_len_check` 校验长度）→ **bit-exact 路径零 double**。
- **`gen_golden.c` 改**：读同一份 `CHIRP_INPUT[]` 重算 golden（证明 golden 基于冻结输入）。
- host 与 target 读**同一份冻结整数输入** → 输入 bit-identical，把"输入分叉"与"算法分叉"彻底隔离。

## 5. host 验证（[L2 host 预验]）
- `gen_golden`（冻结输入）→ `GOLDEN_CRC32 = 0x90556BC7`（**与原值一致**——证明冻结输入 ≡ 原 host chirp，无引入新差异）。
- `bench_harness`（冻结输入，`-Wall -Wextra`）→ **SAT + UNSAT bit-exact PASS**（CRC=0x90556BC7，spot_match=1），**0 警告**。
- 残留 double：仅 MCPS 报告行（`bench_harness.c:97-99`，cycle 派生显示值，**非 bit-exact 路径**）→ 不影响 crc；如需 target 上 MCPS 显示也精确可后续整数化（非本修复必需）。

## 6. 预测 + 下一步（task 4 升级条件）
- **预测**：target 用冻结输入重跑 → `crc32` 应 = **0x90556BC7**、spot_match=1（输入分叉已消，算法纯整数）。**二值判据达成即 R14 输入级闭合。**
- **若仍不一致** → 升级为**算法级整数移植问题**（非输入），排查序：
  1. **有符号右移**：`>>15`/`>>31` 作用于 signed int——cc21k 应为算术右移（符号保持），反汇编确认 ASHIFT 非 LSHIFT；
  2. **int64 MAC 截断点**：`(int64_t)h*state` 累加 + `>>15` 回 Q31，确认 SHARC 80-bit MR / int64 路径与 host 逐位等价；
  3. **int16_t 系数（CHAR_BIT=32）**：确认 `g_hb63_q15` 加载符号扩展正确；
  4. 对照法：target 逐级 dump（SB0-3 子带中间值）vs host golden 中间值，定位首个分叉级。

## 7. CCES 工程更新（台架）
- **新增 `chirp_input.h`** 加入工程（被 `bench_harness.c` #include；672KB，放 L2/L3/flash 只读 section，非 L1 热点）。
- `bench_harness.c` 已无 `<math.h>` 依赖（bit-exact 路径）。
- 红线维持：R14 未闭合前 FIRA 收益不进选型（铁律八/C9）；本修复仅 core-only 输入路径，未碰 FIRA。

---

*DOC-S4-R14-RC-01，PM 直跑 2026-06-02。根因=运行期 chirp double 在 -double-size-32 下输入分叉；修=冻结 CHIRP_INPUT[]；host 验证 bit-exact PASS、golden 不变 0x90556BC7。target 重跑待台架（二值判据 crc==0x90556BC7）。*
