# Core-only → ADSP-21569 (SHARC+) Cross-build 预案 / 可移植性说明

**文档 ID**：DOC-S4-CROSS-01
**日期**：2026-06-02 ｜ 产出：PM 直跑（gcc 代理 + SHARC 静态分析）
**目标**：让台架那场 SHARC cross-build **零编译 debug**（预测并消除所有 target 相关问题）。
**对象**：embedded 子集 = `src/tree_filterbank.c`（核，verbatim）+ `src/tfb_8ch.c`（8ch 包裹）+ `include/fir_coeffs_hb63.h`（系数）+ `cces/dsp_main_core_only.c`（入口骨架）。`host/*` 是 host-only，不进 target build。

---

## ⚠️ 0. 诚实边界（措辞红线，先读）

> **本机无法跑真·SHARC cross-build**，故本文档**不声称"已 0 错 0 警告交叉编译过"**。
> - **本机 CCES 2.12.1 = ARM-only 安装**：仅 `ARM/{aarch64-none-elf, arm-none-eabi, gcc-arm-embedded, openocd, qemu}`，**无 SHARC 编译器 `cc21k`**（manifest 仅列 ARM 工具链；且 ADI `cc21k` 历来 **Windows-only**，Linux CCES 不含 SHARC DSP 核编译器）。证据：`find /opt/analog -name cc21k* → 空`；`/opt/analog/cces/2.12.1/ARM/` 仅 ARM 组件。
> - 故本文档 = **① gcc 严格警告代理 [L2 代理]（抓 cc21k 同类的通用 C 可移植性问题）+ ② SHARC 专项静态分析 [L2 分析]**。
> - **真·cc21k 0 错 0 警告 cross-build 待台架 CCES（Windows）跑**，标 [L1/CCES-target]；本文档是其零-debug 预案。

---

## 1. gcc 严格警告代理结果 — ✅ 0 警告 0 错（[L2 代理]）

命令（embedded 子集，`-c` 仅编译）：
```
gcc -std=c99 -O2 -Iinclude -Isrc -Wall -Wextra -Wconversion -Wsign-conversion -Wshadow -Wcast-align -c <src>
```
| 文件 | 结果 |
|------|------|
| `src/tree_filterbank.c` | **0 警告 / 0 错**（退出码 0） |
| `src/tfb_8ch.c` | **0 警告 / 0 错**（退出码 0） |

> 含义：**通用 C 可移植性干净**——无隐式窄化、无符号转换隐患、无 shadow、无对齐告警。cc21k 在"通用 C"层面大概率同样干净；剩余风险集中在 **SHARC target 专项**（§2），gcc 代理覆盖不到。

---

## 2. SHARC 专项静态分析（gcc 代理覆盖不到，逐项预防）

### 2.1 int 宽度（SHARC `CHAR_BIT=32`）——⚠️ 重点
SHARC（21xxx 经典核）**`char`=`short`=`int`=32 bit**（`CHAR_BIT=32`）。本码 int 类型盘点：`int32_t`（主力，state/sample）、`int64_t`（~15 处，Q46/Q62 MAC 累加）、`int16_t`（系数，`fir_coeffs_hb63.h` + `tree_filterbank.c:65/68/115`）、`uint16_t`（循环/尺寸）、`uint8_t`（`tree_filterbank.h:108` 的 `initialized` 标志 1 处；另 `tfb_8ch.h` 一处标志）。
- **预防**：
  - SHARC+（ADSP-2156x）CCES `stdint.h` **支持** int8/16/32/64_t 定义，但 `int8_t`/`int16_t` 在经典 SHARC 上**存储按 32-bit 字**（短字寻址依核而定）→ `int16_t g_hb63_q15[63]` 实占 63 字（非 126 字节），**功能正确**（加载即符号扩展），仅内存计量按字。
  - **算术安全**：核内系数先 `(int32_t)`/隐式提升再 MAC（`tree_filterbank.c` MAC 行），不依赖 16-bit 回绕语义 → **CHAR_BIT=32 不改变数值结果**（gcc 代理 0 警告佐证无窄化依赖）。
  - **台架查**：确认 CCES 21569 项目 `stdint.h` 提供 int8/16/64_t（应有）；若某老 BSP 缺 int8_t，把 `uint8_t`（`:108`，仅一处计数/标志用）改 `uint32_t` 即消。

### 2.2 `int64_t` Q46 MAC 映射——⚠️ 最高优先（关联 R14 + cycle）
核的定点 MAC = `acc += (int64_t)h * (int64_t)state`（Q15×Q31→Q46），`q31_mul = ((int64_t)a*(int64_t)b)>>31`。SHARC+ 有**原生 80-bit 定点累加器（MR）+ 单周期 MAC**，但 C 写成 `int64_t` 可能映射到 **(a) 编译器识别为硬件 MAC** 或 **(b) 64-bit 软件/库仿真**（慢且影响 cycle）。
- **预防/台架查**：① 反汇编确认 `(int64_t)*` MAC 是否落到 MR 硬件累加器（非库 `__mulli3` 类）；② 若走库仿真 → 考虑 ADI `fract`/`__builtin` 定点（§2.3），**但属优化、不挡编译**；③ **bit-exact 不受映射方式影响**（数值等价），但 **cycle 受影响**——故 R1 cycle 实测前必须确认 MAC 映射（写入 S3/S4 待办）。**此项是 cycle 实测的口径前提，非编译阻断。**

### 2.3 fract 类型 / intrinsic
- 现码**纯 int + 手动 `>>15`/`>>31`**，**不用** ADI `fract16/fract32`/`__builtin_*`。→ **编译无障碍**（不依赖任何 ADI 专有 intrinsic）。
- ADI fract 内建是**后置优化项**（SIMD/单周期 MAC），按计划 §G5「先测裸核基线、后优化」——**baseline 不引入**。
- **impl-defined 提示**：`>>` 作用于**有符号** int 的右移在 ISO C 是"实现定义"（算术 vs 逻辑）。gcc + cc21k **均为算术右移**（符号保持）→ Q-format 语义成立；台架反汇编顺带确认 ASHIFT（非 LSHIFT）即可，风险极低。

### 2.4 intrinsic / cycle 计数占位
- 现码**无任何 intrinsic 调用**（cycle 钩子 `g_tfb_cyc_reg`（`tree_filterbank.h:80-82`）在 `ENABLE_CPU_LOAD_MEASUREMENT` 下 `#ifdef` 关闭）→ 默认 build 无悬挂符号。
- **台架查**：S3 打开 cycle 计数时，`g_tfb_cyc_reg` 换 `def21569.h` 的 **CCNT/EMUCLK** 寄存器或 `__builtin_emuclk()`——此为 S3 项，**不在本 cross-build 范围**。

### 2.5 .ldf 内存布局 + L1 热点（编译/链接核心 target 项）
SHARC 栈在 L1、容量有限。本码**大局部数组在栈**：`tfb_analyze` 的 `a1/a2/a3`、`tfb_synthesize` 的 `r1[512]/r2[256]/r3[128]`（`tree_filterbank.c:144`）等，**单通道每帧栈帧数 KB**；8ch × 此 → 可能溢出 L1 栈。
- **预防（.ldf 预案，零-debug 关键）**：
  - **热点 → L1**：9 级 × `state[63]`（`HbFirState`）× 8ch 延迟线 + 帧中间数组 → 放 L1 block（单周期）。
  - **系数 → L1/L2**：`g_hb63_q15[63]`（小）放 L1；若 L1 紧张放 L2。
  - **大中间数组改静态 + section**：把 `tfb_analyze/synthesize` 的大局部数组从栈搬为**静态分配 + `.ldf` 指定 section**（或确认 L1 栈 `STACK` 段 ≥ 8ch 峰值需求），`#pragma section`/`.ldf` 显式放置 + DMA buf 对齐（端到端用）。
  - **台架给 `.ldf` 骨架**：基于 21569 默认 `app.ldf` 改 section 放置；本轮**无 .ldf 编译产物**（无 cc21k），骨架在台架 CCES 工程里配。

---

## 3. 台架零-debug Checklist（照此则 cross-build 一次过）

1. CCES（Windows，含 SHARC 工具链）新建 ADSP-21569 工程，加入 `tree_filterbank.c/.h`（verbatim，md5 比对）+ `tfb_8ch.c/.h` + `fir_coeffs_hb63.h` + `dsp_main_core_only.c`。
2. **编译开关**：`-proc ADSP-21569`，`-Wall` 等价、`-O1`（先功能后优化）。预期：通用 C 层 0 警告（gcc 代理已佐证）。
3. **若报 int8_t/int16_t**：确认项目 `stdint.h`；极端缺失则 `uint8_t`(`tree_filterbank.h:108` + `tfb_8ch.h` 标志位)→`uint32_t`（仅标志用，零数值影响）。
4. **`.ldf`**：按 §2.5 放置（热点 L1 / 系数 L1-L2 / 大数组静态+section）；确认 L1 STACK ≥ 8ch 峰值。
5. **链接**：确认无 `__mulli3` 类 64-bit 库缺失（若 int64 MAC 走库，链 SHARC runtime lib）。
6. **反汇编抽查**（非编译阻断，为 cycle 口径）：`(int64_t)*` MAC 是否落 MR 硬件累加器；`>>` 是否 ASHIFT。
7. 目标：**0 错 0 警告**（[L1/CCES-target]）→ 即可进 S2 板上 bit-exact。

---

## 4. 结论 + 挂接
- **本轮达成**：gcc 严格代理 **0/0**（通用 C 干净）[L2 代理] + SHARC 五类专项静态分析 + 台架零-debug checklist + .ldf/L1 预案。
- **未达成（诚实）**：**真·SHARC cc21k 0/0 cross-build 本机无法跑**（ARM-only / cc21k Windows-only）→ 待台架 CCES，标 [L1/CCES-target]。
- **唯一 target 风险点**：§2.2 int64 MAC 映射（影响 **cycle**，不影响编译/bit-exact）→ 已记入 S3/S4 待办。其余（int 宽/fract/intrinsic/.ldf）均有预防措施，预期零-debug。
- **挂接**：R1 / R14（FIRA 闸门维持，本文档无 FIRA）/ DEC-S3-PROC-01（21569 定点）/ DEC-S4-DSP-01 / DOC-S4-CORE-PLAN-01 / DOC-S4-CORE-S0S1-01。

---

*DOC-S4-CROSS-01，PM 直跑 2026-06-02。gcc 代理 [L2] 0/0 + SHARC 静态分析；真 SHARC 0/0 待台架 [L1/CCES-target]。本机 CCES ARM-only 无 cc21k 为诚实边界，不冒充已编译。R14 维持，无 FIRA。*
