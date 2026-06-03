# FIRA F1：G1/G2 闭合 + Legacy/ACM 决策 + 定点格式机制

**文档 ID**：DOC-S4-FIRA-F1-01 ｜ 日期：2026-06-03 ｜ PM 直跑（grep 实证）
**挂接**：R14 / DEC-S4-DSP-01 / DOC-S4-FIRA-IMPL-01（工作单 F1）/ DOC-S4-IFACE-SURVEY-01
**范围**：F1 是工作单第一阶段，**纯分析（Linux 可做）**；F2-F8 板上待台架。

---

## 0. G1 闭合（FIRA SHARC 驱动签名缺失 → 解除）
CTO 提供 **`adi_fir_legacy_2156x.h`**（此前 gap G1），已归档 `knowledge_base/ezkit/bsp/fira_headers/adi_fir_legacy_2156x.h`（C8/铁律六）。10 函数 + CHANNEL_INFO + 枚举全确认。config 头 `adi_fir_config_2156x.h` 仓库已有多份（各 FIRA 例程 system/）。
**🆕 发现**：FIRA 例程包含 **`Split_Task/`** 子项目（`…/EE408V02/Split_Task/`）= **正是我方 Split-Task 模型的官方参考**，F2-F5 台架优先参照。

---

## 1. G2 闭合：定点格式机制（grep 实证）
**例程实际跑 LEGACY 模式**（纠正 IFACE-SURVEY「倾向 ACM」）：
- `FIR_Multi_Channel_Processing/system/.../adi_fir_config_2156x.h:77` → `ADI_FIR_CFG_ACCELERATOR_MODE = ADI_FIR_ACCELERATOR_MODE_LEGACY`。
- 例程里所有定点格式字段（`Fixed point enable`/`Format`/`Rounding`）都在 `#if …ACM`（c:135-142）内 → **Legacy 模式下被编译掉**，CHANNEL_INFO 无内联格式字段（与 legacy 头一致）。
- 例程 = **Legacy + 浮点**（config `ADI_FIR_FIXED_POINT_MODE = 0u`，c:120），**不调** `adi_fir_FixedPointEnable`（grep 0 命中）。
- 完成判定差异：Legacy `while(FIRTaskDoneCount<FIR_NUMBER_OF_TASKS)`（c:281）；ACM 等 CHANNEL 数。

**→ 我方定点 SIGNED 的两条设置路径**：
| 路径 | 怎么设 | 影响面 | 风险 |
|------|--------|--------|------|
| **(A) config 宏** | `ADI_FIR_FIXED_POINT_MODE=1` + `ADI_FIR_CFG_FIXED_INPUT_FORMAT=ADI_FIR_IN_FORMAT_SINT`（config 头）| **全 build 全任务**（全局）| 改 config 头，影响整工程；工作单红线（改前先报）|
| **(B) 运行时 API（推荐先试）** | `adi_fir_FixedPointEnable(hFirTask, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER)` 每任务 | 每任务 | **不动 config 头**；但「Legacy 下运行时 API 是否独立生效（不设全局宏）」头未明说 → **F2/F3 板上验** |

**推荐**：**先走 (B) 运行时 `adi_fir_FixedPointEnable(hTask, SIGNED_INTEGER)`**（避免改 config 头）；若板上 F2/F3 显示未生效（仍按浮点/无符号跑）→ 回退 (A) config 宏。**改 config 头前按工作单红线先报 CTO。**

---

## 2. Legacy vs ACM 决策 → **推荐 LEGACY**
| 维度 | Legacy | ACM |
|------|--------|-----|
| 板上验证 | ✅ 例程用的就是 Legacy（本板已跑过）| 例程未编（#if 编译掉）|
| 定点格式/舍入 | **全局**（config 宏 或运行时 per-task）| 每通道（CHANNEL_INFO 字段）|
| 缓冲索引 | **硬件完成后自动更新**（循环缓冲复用方便）| 硬件不更新，须 `adi_fir_UpdateTask` |
| 完成事件 | ALL_CHANNEL_DONE 可用 | 无 ALL_CHANNEL_DONE，逐通道回调 |
| 通道上限 | 适用（我方 8ch ≪ 32）| 无上限（我方用不上）|
| 我方契合 | **8ch 全同一 SIGNED 格式 + 同舍入 → 全局配置足够**；每通道 tap/抽取比仍由 CHANNEL_INFO 各自带（两模式都支持）| 灵活性我方不需要 |

**结论**：**Legacy 推荐**——例程已板上验证、我方 8 通道格式统一契合全局配置、硬件自动更新索引更简单。ACM 的 per-channel 灵活性我方用不上，且需手动 UpdateTask、无 ALL_DONE。**纠正 IFACE-SURVEY 的 ACM 倾向。**

---

## 3. F1 产出小结（喂回工作单）
- **模式**：Legacy（推荐）。
- **定点格式**：先试运行时 `adi_fir_FixedPointEnable(hTask, ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER)`；回退 config 宏（改前报 CTO）。
- **抽取**：`ADI_FIR_CHANNEL_INFO.eSampling=ADI_FIR_SAMPLING_DECIMATION` + `nSamplingRatio`（per-channel，Legacy 支持）。
- **完成**：Legacy 等 `FIRTaskDoneCount < N_TASKS`，ALL_CHANNEL_DONE 回调。
- **参考**：台架优先看 **`Split_Task/` 例程**（官方 Split-Task 模型）。

## 4. 残留（仍待台架，不臆造）
- **G2 残**：Legacy 下「运行时 FixedPointEnable 是否需配合全局宏」头未明说 → F2/F3 板上验。
- **R14 命门（F4）**：signed-fractional Q15×Q31 → 驱动 signed-**INTEGER** 映射（×2 缩放/抽取相位/截位）——**桌面无法坐实，F4 单通道逐位必上板**（crc==0x90556BC7）。
- **FIRA 自身开销**：F7 板上实测（setup/queue/callback/DMA），**不假设零成本**。
- **工程路径映射**：工作单引 `bench_core_only/…`；我方实体 = `sprint4/dsp/core_only/` + LED 脚手架，台架建 CCES 工程时对齐。

## 红线（维持）
F2-F8 板上算力收益 **R14 闭合（板上 crc==0x90556BC7）前不得写进选型/裕量结论**（铁律八/C9）。本 F1 仅分析，无算力数值。

---

*DOC-S4-FIRA-F1-01，PM 直跑 2026-06-03。G1 闭合（legacy 头归档）；G2 闭合（例程=Legacy，格式 (B)运行时优先/(A)config 回退）；Legacy 推荐（纠正 ACM 倾向）；F2-F8 + R14 命门待台架。*
