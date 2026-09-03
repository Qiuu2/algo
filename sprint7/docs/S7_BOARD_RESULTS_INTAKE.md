# S7 板测结果判读方案（S7_BOARD_RESULTS_INTAKE）— 四批回填表 · 判读决策树 · B1 启动条件 · 宿主判读脚本

> **性质**：预写的判读方案（CTO 2026-09-03 指令，DEC-S7-RULINGS-02"准备工作"）。测试员数据回来之前写好，**避免临场决定怎么判**。本文与 `sprint7/tools/s7_intake.py`（v3.3，2026-09-03）同源：脚本 `--schema` 打印的回填模板 = §1 原文；脚本的判据 = §2/§3 决策树，§2 每一支都在脚本里有对应判定。
> **数字纪律**：本文**没有任何板上实测数字**。回填表全部留空；每个空位标明期望值来源：**冻结锚**（`dolph_f5_goldens.h`，脚本运行时解析）、**派生阈值**、**文档已登记的对照量**、或**"无期望值，只记录"**。容差（默认 5%）是工作假设 [L4]。
> **CCLK 前提（C4；CTO 2026-09-03 裁定，DEC-S7-RULINGS-03）**：帧预算 = CCLK × 64/48000、1.5× 线 = 帧预算 / 1.5，**一律用测试员实测的 M2 核心时钟重算，不设旗位放行**。测试员在 B0 上用 Register/Memory 视图读 `CGU0_CTL/STAT/DIV`（`0x3108D000` / `0x3108D008` / `0x3108D00C`，出处 CCES 2.12.1 `sys/ADSP_2156x_HPC.h`），只读、不改二进制、不加代码（runbook 第 6b 步与表 D）。脚本按 **`fPLL = (CLKIN / (DF+1)) × MSEL`、`CCLK = fPLL / CSEL`** 解码（`MSEL=0` 视为 128、`CSEL=0` 视为 32；`PLLEN=0` 或 `PLLBP=1` → `CCLK = CLKIN`）。出处 [L1 源码]：CCES 2.12.1 `lib/src/services/Source/pwr/adi_pwr_2156x.c` 的 `adi_pwr_GetCoreClkFreq()` —— 21569 属 `__ADSP21569_FAMILY__`，走非 21568 分支，**没有 ÷2**；这正是 bench F7 G6 读回 1e9 用的同一函数。四锚交叉验证 [L1 工具链]：`adi_pwr_21569_family_{1GHz,800MHz,600MHz,400MHz}_config.h`（CLKIN 均 25 MHz）MSEL/CSEL = 80/2、64/2、72/3、48/3 → 1000、800、600、400 MHz 逐一相等。**解出的值还要过数据手册合理性门**（ADSP-2156x 数据手册 Rev.C 2022-11 [L1 文件]）：`SYS_CLKIN0` 20–30 MHz（**Table 33** Clock and Reset Timing）、`fPLLCLK` 1.20–2.00 GHz（**Table 20** PLL Operating Conditions, p.45）、`fCCLK` 400–1000 MHz（**Table 19** Clock Operating Conditions, p.44）；任一越界 → 判抄写/读错，**不按 [L1] 用**，条件 0 未满足。**`[CLK]` 未回填或缺项 → 条件 0 未满足 → B1 挂起**（PLL 旁路与字段 0 照常解码，另打 MAJOR/info）；实测与 bench `g_s7_cclk_hz` 不一致 → BLOCKER，先按时钟比折算（排查表 #15）。旧参考值 1,333,333 / 888,889 由 bench 读回的 1e9 [L1] 得出，**只作对照**。
> **口径**：墙钟（DEC-S7-RULINGS-01 D1）。三口径互不可比纪律不变。**差距分类用稳态读数（`beam_cyc_min`，`S7_B63 §6` 的定义；要求 `last` 与 `min` 一致 ±t，否则稳态不可判；min≈last≪max 时 max 是离群/冷帧）；B1 余量用 WCET（`beam_cyc_max`）**——两者在报告里分开写。
> **回灌规则（FG2）**：任何一节（build/臂/bench）指纹不符、板门不绿、FG 不绿 → 该节无效，其读数不参与差距分类、三段归因、B1 门；同一份读数不会既"作废"又"PASS"。
> **谁判**：脚本只做初筛；结论进 decisions_log 前须独立 critic + CTO 常识审。
> **状态**：critic-F 三轮（首轮 FAIL → delta CONDITIONAL → delta-2 PASS_WITH_MINOR，MINOR 已在同一提交修）；verdict 见 `sprint7/critic/CRITIC_F_INTAKE_20260903.md`。落库后 PM **停止**，等测试员数据。

---

## 0. 四批数据从哪来（对应 runbook）

| 批 | 内容 | 回填来源 runbook | INI 节 |
|---|---|---|---|
| 1 | S-B 四个 build：B0 基线 / B1 +SELFTEST+SEG_CYC / B2 +NEGCTRL / B3 无宏 | `sprint7/docs/S7_TESTER_RUNBOOK_SB.md` §2–§5 | `[SB.B0]` `[SB.B1]` `[SB.B2]` `[SB.B3]` |
| 1 附 | **M2 实测核心时钟**：B0 上读三个 CGU 寄存器 + CLKIN（只读一次，零改码） | 同上 第 6b 步 + 表 D | `[CLK]` |
| 2 | B6.3 对照臂：A'（Debug + -O）、As（+SEG_CYC，可选）、A''（只取消 Debug 系统库，可选）、B（Release，可选）；臂 0 = SB.B0 | `sprint7/docs/S7_B63_WALLCLOCK_GAP.md` §1.3/§1.6/§5 | `[B63.A1]` `[B63.As]` `[B63.A2]` `[B63.B]` |
| 3 | bench 探针 bench-P（无副本；内拆分副本按 DEC-S7-RULINGS-02 不做） | `sprint7/dsp/probe/README.md` §2/§3 | `[BENCH.P]` |
| 4 | 自家 16 元阵列极性 QA（Step A 电池逐只 + Step B 375 Hz 成对） | `sprint7/docs/S7_POLARITY_QA_RUNBOOK.md` §4 | `[POLQA]` |

**回填规则**：数字抄原值；十六进制带 `0x`；yes/no 小写；符号不存在写 `na`；**空位 = 未回填 = 不可判**（脚本绝不默认 PASS）。第 2 遍快照（F3 纪律）与原始截图/`.map`/R10 记录卡按各 runbook 的发回清单一并交，INI 只是机读汇总，不替代原件。

---

## 1. 统一回填表（INI；= `s7_intake.py --schema` 输出，逐字同源）

期望值来源标注：**[锚]** = 冻结 golden（脚本解析 `sprint4/dsp/fira/dolph_f5_goldens.h`）；**[表 A]** = S-B runbook 表 A 指纹期望（build 事实）；**[门]** = M2 板门（DEC-S6-M2-BOARD-PASS-01 判据）；**[派生]** = 由源码/ldf 派生；**[记录]** = 无期望值，只记录。

| 字段族 | 期望值来源 |
|---|---|
| `fira_inloop / selftest_built / selftest_negctrl_built / seg_w_cyc_last_visible` | [表 A]：B0：1/0/na/no；B1：1/1/0/yes；B2：1/1/1/no；B3：0/0/na/no；A'/A''/B 同 B0；As 同 B0 但 yes |
| `static_txtest / stxt_localize / chmap_fix / rx_right_aligned / u6_addr_override _built` | [表 A]：全部 0（任何 build） |
| `main_init_rc / m1_valid / m2_valid / setup_rc / fg_stream_live / fg_beam_live` | [门]：0 / 1 / 1 / 0 / 1 / 1（B3 只看 `main_init_rc / m1_valid / fg_stream_live / rx_block_count`） |
| `rx_block_count / poll_count / overrun_count` | [门]：rx 增长、rx≈poll（默认 ±1%）、overrun ≈ 0（默认 ≤ 0.1%×rx）[L4 容差] |
| `out_max_abs / m1_max_abs_sample` | [门 + R57 判别式]：不顶满幅（默认 < 0x7F000000 [L4]）；若顶满幅：`m1_max_abs_sample` < 0x49A00000（−4.8 dBFS 契约 [L1]）= 逐帧 FIRA 失败特征，否则 = 音源过热先降电平 |
| `map_rx/tx/fa_addr` | [派生 `m1_app.ldf`]：三 pin 在 Block 1 0x2C0000–0x2EBFFF（DEC-S6-M2-BOARD-PASS-01 已证；本次核未漂，IO2） |
| `map_seg_in / seg_out3 / taskmem_addr` | [派生 `m1_app.ldf`]：FIRA DMA scratch 在 L1 0x240000–0x39BFFF，**不得**落 L2（cached → R57 静默污染） |
| `map_chirp_addr` | [派生 `m1_app.ldf`]：落 `mem_L2_bw` 0x20000000–0x200F9FFF（仅带 SELFTEST 的 build） |
| `selftest_rc / pass[8] / crc[8] / crc_core[8]` | [锚]：B1 = 0 / 全 1 / 八锚 / 八锚；B2 = 7 / `0×7,1` / 全 F4 锚 / 全 F4 锚 |
| `selftest_frames` | [派生]：8 × 1024 = 8192（不满 = 未跑完） |
| `selftest_mismatch_sb/idx`、`selftest_cyc`、`selftest_cyc_ch[8]` | [记录] |
| `beam_cyc_last/max/min`、`seg_*_cyc_*`、`cb_cyc_max` | **[记录]**：无期望值；脚本只做比值、恒等式与离群判定（§2.3/§2.4） |
| `o_evidence`（A'/As/A''）、`debuglib_unchecked_evidence`（A''）、`cproject_checked_out`（B） | [凭证]：非空 / 非空 / yes；缺 → 该臂不入账 |
| bench `done / valid / setup_rc / core_selfcheck_all / fg_pass_all / crc_fira[8] / f4_pass / f5_pass_all` | [锚]/[README §3]：1 / 1 / 0 / 1 / 1 / 八锚 / 1 / 1 |
| bench `frames_total / frames / reads_per_frame / cclk_hz / cclk_rc` | [README §3 / 源码]：1024 / 1020 / 25 / 1e9 / 0（cclk ≠ 1e9 → 帧预算前提动摇，MAJOR） |
| bench `ccnt_read_cyc / f7_cyc_8ch_fira / fa_block1 / syn_fg_*` | [记录]（`syn_fg_all=1` 才算合成侧对照过；-2 未评估；0 记录上报） |
| `POLQA.*` | 无数值；状态与列表（§2.5）；`mapping` 八路逗号分隔 |
| `CLK.cgu0_ctl / cgu0_stat / cgu0_div` | **[记录]**：无期望值，原样抄；脚本解码出 MSEL/DF/CSEL 与 PLL 状态 |
| `CLK.clkin_hz` | **[L1 文件：原理图]** AD-EXKIT V2.1 核心板原理图 25 MHz 振荡器直连 `SYS_CLKIN0`；与 `m1_main.c:44` 实参、ADI 21569 家族配置头 `CFG0_BIT_CGU0_CLKIN=25000000` 三方一致；须落在数据手册 `fCKIN` 20–30 MHz 内。板上实物不同则以实物为准并写出处 |
| `CLK.read_build / read_method / evidence` | [凭证]：在哪个 build 读、Register 还是 Memory 视图、截图名 |

```ini
; S7 板测回填文件（INI）。空位 = 未回填 = 不可判。数字抄原值；十六进制带 0x；yes/no 小写。
; 第 2 遍快照（F3 纪律：主数差 <0.1% 才入账）抄在原件回执里，本文件填第 1 遍。
[meta]
date =
tester =
commit =                        ; git log -1 --oneline
git_status_clean =              ; yes / no（sprint6/dsp/audio/m1_cces_project/src 干净?）

; ===== 批 1 附：M2 工程实测核心时钟（CGU 寄存器；CTO 2026-09-03 裁定，条件 0 的唯一依据）=====
[CLK]
cgu0_ctl =                      ; 0x........ 原样抄（地址 0x3108D000）
cgu0_stat =                     ; 0x........ 原样抄（地址 0x3108D008）
cgu0_div =                      ; 0x........ 原样抄（地址 0x3108D00C）
clkin_hz =                      ; 25000000（核心板原理图 V2.1：25 MHz 振荡器接 SYS_CLKIN0）；实物不同则抄实际值并在 note 写出处
read_build =                    ; 在哪个 build 上读的（B0 / B1 / B2 / B3）
read_method =                   ; register_view / memory_view / other（other 写清楚）
evidence =                      ; 寄存器窗口截图文件名
note =                          ; 异常或偏差说明（无则 none）

; ===== 批 1：S-B 四个 build（sprint7/docs/S7_TESTER_RUNBOOK_SB.md）=====
[SB.B0]  ; Debug 现状：M2_FIRA_INLOOP=1 FIRA_USE_REAL_ADI_FIR_HEADER；无 SELFTEST 无 SEG_CYC（= B63 臂 0）
fira_inloop =
selftest_built =
selftest_negctrl_built =        ; 0 / 1 / na（符号不存在写 na）
static_txtest_built =
stxt_localize_built =
chmap_fix_built =
rx_right_aligned_built =
u6_addr_override_built =
seg_w_cyc_last_visible =        ; yes / no（符号是否存在）
main_init_rc =
m1_valid =
m2_valid =
setup_rc =
fg_stream_live =
fg_beam_live =
rx_block_count =
poll_count =
overrun_count =
out_nonzero =
out_max_abs =                   ; 0x...
m1_max_abs_sample =             ; 0x...
beam_cyc_last =
beam_cyc_max =
beam_cyc_min =
cb_cyc_max =
listen =                        ; 正常 / 刺耳 / 无声 / 循环卡顿
map_rx_addr =                   ; 0x... s_m1_rx_buf
map_tx_addr =                   ; 0x... s_m1_tx_buf
map_fa_addr =                   ; 0x... s_m2_fa
map_seg_in_addr =               ; 0x... s_seg_in（FIRA DMA scratch，须在 L1）
map_seg_out3_addr =             ; 0x... s_seg_out3
map_taskmem_addr =              ; 0x... s_taskMem
map_chirp_addr =                ; 0x... CHIRP_INPUT（仅带 M2_SELFTEST 的 build）
evidence =                      ; Defined symbols 截图 / Console 编译行截图 文件名

[SB.B1]  ; + M2_SELFTEST=1 + M2_SEG_CYC=1（= B63 臂 0s）
fira_inloop =
selftest_built =
selftest_negctrl_built =        ; 0 / 1 / na（符号不存在写 na）
static_txtest_built =
stxt_localize_built =
chmap_fix_built =
rx_right_aligned_built =
u6_addr_override_built =
seg_w_cyc_last_visible =        ; yes / no（符号是否存在）
main_init_rc =
m1_valid =
m2_valid =
setup_rc =
fg_stream_live =
fg_beam_live =
rx_block_count =
poll_count =
overrun_count =
out_nonzero =
out_max_abs =                   ; 0x...
m1_max_abs_sample =             ; 0x...
beam_cyc_last =
beam_cyc_max =
beam_cyc_min =
cb_cyc_max =
listen =                        ; 正常 / 刺耳 / 无声 / 循环卡顿
map_rx_addr =                   ; 0x... s_m1_rx_buf
map_tx_addr =                   ; 0x... s_m1_tx_buf
map_fa_addr =                   ; 0x... s_m2_fa
map_seg_in_addr =               ; 0x... s_seg_in（FIRA DMA scratch，须在 L1）
map_seg_out3_addr =             ; 0x... s_seg_out3
map_taskmem_addr =              ; 0x... s_taskMem
map_chirp_addr =                ; 0x... CHIRP_INPUT（仅带 M2_SELFTEST 的 build）
evidence =                      ; Defined symbols 截图 / Console 编译行截图 文件名
selftest_rc =
selftest_frames =
selftest_pass =                 ; 8 个 0/1，逗号分隔
selftest_crc =                  ; 8 个 0x........，逗号分隔
selftest_crc_core =             ; 8 个 0x........，逗号分隔
selftest_mismatch_sb =          ; 8 个，逗号分隔（-1 = 无）
selftest_mismatch_idx =         ; 8 个，逗号分隔（-1 = 无）
selftest_cyc =                  ; 无期望值，只记录
selftest_cyc_ch =               ; 8 个，逗号分隔；无期望值，只记录
seg_w_cyc_last =                ; 无期望值，只记录
seg_w_cyc_max =
seg_ana_cyc_last =
seg_ana_cyc_max =
seg_syn_cyc_last =
seg_syn_cyc_max =
seg_tx_cyc_last =
seg_tx_cyc_max =

[SB.B2]  ; + M2_SELFTEST=1 + M2_SELFTEST_NEGCTRL=1（无 SEG_CYC）
fira_inloop =
selftest_built =
selftest_negctrl_built =        ; 0 / 1 / na（符号不存在写 na）
static_txtest_built =
stxt_localize_built =
chmap_fix_built =
rx_right_aligned_built =
u6_addr_override_built =
seg_w_cyc_last_visible =        ; yes / no（符号是否存在）
main_init_rc =
m1_valid =
m2_valid =
setup_rc =
fg_stream_live =
fg_beam_live =
rx_block_count =
poll_count =
overrun_count =
out_nonzero =
out_max_abs =                   ; 0x...
m1_max_abs_sample =             ; 0x...
beam_cyc_last =
beam_cyc_max =
beam_cyc_min =
cb_cyc_max =
listen =                        ; 正常 / 刺耳 / 无声 / 循环卡顿
map_rx_addr =                   ; 0x... s_m1_rx_buf
map_tx_addr =                   ; 0x... s_m1_tx_buf
map_fa_addr =                   ; 0x... s_m2_fa
map_seg_in_addr =               ; 0x... s_seg_in（FIRA DMA scratch，须在 L1）
map_seg_out3_addr =             ; 0x... s_seg_out3
map_taskmem_addr =              ; 0x... s_taskMem
map_chirp_addr =                ; 0x... CHIRP_INPUT（仅带 M2_SELFTEST 的 build）
evidence =                      ; Defined symbols 截图 / Console 编译行截图 文件名
selftest_rc =
selftest_frames =
selftest_pass =                 ; 8 个 0/1，逗号分隔
selftest_crc =                  ; 8 个 0x........，逗号分隔
selftest_crc_core =             ; 8 个 0x........，逗号分隔
selftest_mismatch_sb =          ; 8 个，逗号分隔（-1 = 无）
selftest_mismatch_idx =         ; 8 个，逗号分隔（-1 = 无）
selftest_cyc =                  ; 无期望值，只记录
selftest_cyc_ch =               ; 8 个，逗号分隔；无期望值，只记录

[SB.B3]  ; 无任何宏（M1 透传）：只填指纹 + main_init_rc/m1_valid/fg_stream_live/rx_block_count
fira_inloop =
selftest_built =
selftest_negctrl_built =        ; 0 / 1 / na（符号不存在写 na）
static_txtest_built =
stxt_localize_built =
chmap_fix_built =
rx_right_aligned_built =
u6_addr_override_built =
seg_w_cyc_last_visible =        ; yes / no（符号是否存在）
main_init_rc =
m1_valid =
m2_valid =
setup_rc =
fg_stream_live =
fg_beam_live =
rx_block_count =
poll_count =
overrun_count =
out_nonzero =
out_max_abs =                   ; 0x...
m1_max_abs_sample =             ; 0x...
beam_cyc_last =
beam_cyc_max =
beam_cyc_min =
cb_cyc_max =
listen =                        ; 正常 / 刺耳 / 无声 / 循环卡顿
map_rx_addr =                   ; 0x... s_m1_rx_buf
map_tx_addr =                   ; 0x... s_m1_tx_buf
map_fa_addr =                   ; 0x... s_m2_fa
map_seg_in_addr =               ; 0x... s_seg_in（FIRA DMA scratch，须在 L1）
map_seg_out3_addr =             ; 0x... s_seg_out3
map_taskmem_addr =              ; 0x... s_taskMem
map_chirp_addr =                ; 0x... CHIRP_INPUT（仅带 M2_SELFTEST 的 build）
evidence =                      ; Defined symbols 截图 / Console 编译行截图 文件名

; ===== 批 2：B6.3 对照臂（sprint7/docs/S7_B63_WALLCLOCK_GAP.md §1/§5）=====
[B63.A1] ; 臂 A'：Debug + GUI 勾 -O（路径 A），无 SEG_CYC；必须附 -O 凭证
o_evidence =                    ; Console 编译行含 -O 的截图文件名
ov_value =                      ; GUI 显示的 -Ov 值（原样抄）
fira_inloop =
selftest_built =
selftest_negctrl_built =        ; 0 / 1 / na（符号不存在写 na）
static_txtest_built =
stxt_localize_built =
chmap_fix_built =
rx_right_aligned_built =
u6_addr_override_built =
seg_w_cyc_last_visible =        ; yes / no（符号是否存在）
main_init_rc =
m1_valid =
m2_valid =
setup_rc =
fg_stream_live =
fg_beam_live =
rx_block_count =
poll_count =
overrun_count =
out_nonzero =
out_max_abs =                   ; 0x...
m1_max_abs_sample =             ; 0x...
beam_cyc_last =
beam_cyc_max =
beam_cyc_min =
cb_cyc_max =
listen =                        ; 正常 / 刺耳 / 无声 / 循环卡顿
map_rx_addr =                   ; 0x... s_m1_rx_buf
map_tx_addr =                   ; 0x... s_m1_tx_buf
map_fa_addr =                   ; 0x... s_m2_fa
map_seg_in_addr =               ; 0x... s_seg_in（FIRA DMA scratch，须在 L1）
map_seg_out3_addr =             ; 0x... s_seg_out3
map_taskmem_addr =              ; 0x... s_taskMem
map_chirp_addr =                ; 0x... CHIRP_INPUT（仅带 M2_SELFTEST 的 build）
evidence =                      ; Defined symbols 截图 / Console 编译行截图 文件名

[B63.As] ; 臂 As：Debug + -O + M2_SEG_CYC=1（可选）
o_evidence =
fira_inloop =
selftest_built =
selftest_negctrl_built =        ; 0 / 1 / na（符号不存在写 na）
static_txtest_built =
stxt_localize_built =
chmap_fix_built =
rx_right_aligned_built =
u6_addr_override_built =
seg_w_cyc_last_visible =        ; yes / no（符号是否存在）
main_init_rc =
m1_valid =
m2_valid =
setup_rc =
fg_stream_live =
fg_beam_live =
rx_block_count =
poll_count =
overrun_count =
out_nonzero =
out_max_abs =                   ; 0x...
m1_max_abs_sample =             ; 0x...
beam_cyc_last =
beam_cyc_max =
beam_cyc_min =
cb_cyc_max =
listen =                        ; 正常 / 刺耳 / 无声 / 循环卡顿
map_rx_addr =                   ; 0x... s_m1_rx_buf
map_tx_addr =                   ; 0x... s_m1_tx_buf
map_fa_addr =                   ; 0x... s_m2_fa
map_seg_in_addr =               ; 0x... s_seg_in（FIRA DMA scratch，须在 L1）
map_seg_out3_addr =             ; 0x... s_seg_out3
map_taskmem_addr =              ; 0x... s_taskMem
map_chirp_addr =                ; 0x... CHIRP_INPUT（仅带 M2_SELFTEST 的 build）
evidence =                      ; Defined symbols 截图 / Console 编译行截图 文件名
seg_w_cyc_last =                ; 无期望值，只记录
seg_w_cyc_max =
seg_ana_cyc_last =
seg_ana_cyc_max =
seg_syn_cyc_last =
seg_syn_cyc_max =
seg_tx_cyc_last =
seg_tx_cyc_max =

[B63.A2] ; 臂 A''：Debug + -O + 只取消勾 Use Debug System libraries（可选，排查表 #2 单变量）
o_evidence =
debuglib_unchecked_evidence =   ; 截图文件名
fira_inloop =
selftest_built =
selftest_negctrl_built =        ; 0 / 1 / na（符号不存在写 na）
static_txtest_built =
stxt_localize_built =
chmap_fix_built =
rx_right_aligned_built =
u6_addr_override_built =
seg_w_cyc_last_visible =        ; yes / no（符号是否存在）
main_init_rc =
m1_valid =
m2_valid =
setup_rc =
fg_stream_live =
fg_beam_live =
rx_block_count =
poll_count =
overrun_count =
out_nonzero =
out_max_abs =                   ; 0x...
m1_max_abs_sample =             ; 0x...
beam_cyc_last =
beam_cyc_max =
beam_cyc_min =
cb_cyc_max =
listen =                        ; 正常 / 刺耳 / 无声 / 循环卡顿
map_rx_addr =                   ; 0x... s_m1_rx_buf
map_tx_addr =                   ; 0x... s_m1_tx_buf
map_fa_addr =                   ; 0x... s_m2_fa
map_seg_in_addr =               ; 0x... s_seg_in（FIRA DMA scratch，须在 L1）
map_seg_out3_addr =             ; 0x... s_seg_out3
map_taskmem_addr =              ; 0x... s_taskMem
map_chirp_addr =                ; 0x... CHIRP_INPUT（仅带 M2_SELFTEST 的 build）
evidence =                      ; Defined symbols 截图 / Console 编译行截图 文件名

[B63.B]  ; 臂 B：Release（路径 B，旁证；可选）
o_evidence =
cproject_checked_out =          ; yes（build 后 .cproject/.project 已 checkout，不入库）
fira_inloop =
selftest_built =
selftest_negctrl_built =        ; 0 / 1 / na（符号不存在写 na）
static_txtest_built =
stxt_localize_built =
chmap_fix_built =
rx_right_aligned_built =
u6_addr_override_built =
seg_w_cyc_last_visible =        ; yes / no（符号是否存在）
main_init_rc =
m1_valid =
m2_valid =
setup_rc =
fg_stream_live =
fg_beam_live =
rx_block_count =
poll_count =
overrun_count =
out_nonzero =
out_max_abs =                   ; 0x...
m1_max_abs_sample =             ; 0x...
beam_cyc_last =
beam_cyc_max =
beam_cyc_min =
cb_cyc_max =
listen =                        ; 正常 / 刺耳 / 无声 / 循环卡顿
map_rx_addr =                   ; 0x... s_m1_rx_buf
map_tx_addr =                   ; 0x... s_m1_tx_buf
map_fa_addr =                   ; 0x... s_m2_fa
map_seg_in_addr =               ; 0x... s_seg_in（FIRA DMA scratch，须在 L1）
map_seg_out3_addr =             ; 0x... s_seg_out3
map_taskmem_addr =              ; 0x... s_taskMem
map_chirp_addr =                ; 0x... CHIRP_INPUT（仅带 M2_SELFTEST 的 build）
evidence =                      ; Defined symbols 截图 / Console 编译行截图 文件名

; ===== 批 3：bench 探针（sprint7/dsp/probe/README.md §3）=====
[BENCH.P]
done =
valid =
setup_rc =
core_selfcheck_all =
fg_pass_all =
crc_fira =                      ; 8 个 0x........，逗号分隔
frames_total =
frames =
cclk_hz =
cclk_rc =
ccnt_read_cyc =                 ; 无期望值，只记录（扣扰动用）
beam_cyc_last =
beam_cyc_max =
beam_cyc_min =
seg_w_cyc_last =
seg_w_cyc_max =
seg_w_cyc_min =
seg_ana_cyc_last =
seg_ana_cyc_max =
seg_ana_cyc_min =
seg_syn_cyc_last =
seg_syn_cyc_max =
seg_syn_cyc_min =
seg_sum_last =
probe_ovh_last =
reads_per_frame =
f4_pass =                       ; 同 build 同次跑 g_fira_f4_pass
f5_pass_all =                   ; 同 build 同次跑 g_f5_pass_all
f7_cyc_8ch_fira =               ; 同 build 同次跑（对照锚，无期望值）
fa_block1 =                     ; g_s7_fa_block1：0 / 1，只记录
syn_fg_built =                  ; 0 / 1
syn_fg_all =                    ; -99 未编 / -2 未评估 / 0 / 1
; ===== 批 4：自家阵列极性 QA（sprint7/docs/S7_POLARITY_QA_RUNBOOK.md §4）=====
[POLQA]
stepA_status =                  ; complete / conditional / incomplete
stepA_undetermined =            ; 未定喇叭 pos 列表（无则 none）
stepB_status =                  ; pass / fail / not_done
opposite_channels =             ; Phase B 判 OPPOSITE 的通道 c 列表（无则 none）
weak_channels =                 ; Phase A 弱/趋零通道列表（无则 none）
unclear_pairs =                 ; 分不清的对（无则 none）
lines_changed =                 ; yes / no（是否改过线）
reverified_after_change =       ; yes / no / n/a
mapping =                       ; c0:posA-posB,c1:...,c7:...（实测通道→物理对，逗号分隔，不要用分号）
mapping_identity =              ; yes / no（是否与约定 {c,15-c} 一致）
record_file =                   ; deliverables/algorithm_validation/POLQA_OWNARRAY_<date>.md

```

---

## 2. 判读决策树（脚本逐条实现；每条结论带 L 标；"下一步"只到"提交 CTO 裁"为止）

### 2.0 先决门（任一不过 → 该节全部读数隔离、不入账、不抢救，且**不进入 §2.3/§2.4/§3**）
1. **指纹 ≠ 表 A**（含 `selftest_negctrl_built` 与 `seg_w_cyc_last` 可见性）→ BLOCKER：R52 stale-state，读数不属于声称的 build；回 runbook §3 第 1 步重做。例外：不带 SELFTEST 的 build 把 `selftest_negctrl_built` 填成 0 而非 `na` → 填写不一致（MAJOR，按 na 处理），不作废该 build。
2. **板门不绿**（`main_init_rc≠0`、`m1_valid/m2_valid≠1`、`setup_rc≠0`、FG≠1、rx≉poll、overrun 涨）→ BLOCKER 隔离。**`out_max_abs` 顶满幅**：`m1_max_abs_sample` < 0x49A00000 → 逐帧 FIRA 失败特征（R57）；否则音源过热先降电平重跑。
3. **`.map`**：`CHIRP_INPUT` 不在 L2 → 自检读数不可信（走 S-B runbook §8 备用方案）；三 pin 漂出 Block 1 0x2C0000–0x2EBFFF → IO2 疑点，BLOCKER 隔离，先解释再入账；`s_seg_*`/`s_taskMem` 落 L2 → R57 静默污染，BLOCKER。
4. **臂凭证**：A'/As/A'' 缺 `-O` 编译行截图 → 该臂不入账（BLOCKER）；A'' 缺"取消 Debug 系统库"截图 → 单变量证据不成立；臂 B 未确认 `.cproject/.project` 已 checkout → 臂 B 暂不入账（治理硬约束）。
5. **bench-P**：`done/valid/setup_rc` ≠ 1/1/0、`core_selfcheck_all≠1`、`fg_pass_all≠1` 或 `crc_fira` ≠ 八锚、`frames` ≠ 1024/1020、`reads_per_frame≠25`、同 build F4/F5 旗 ≠ 1 → bench 三段作废、不作差距参考（回退历史 F7 463,273 [L1]，报告里明标"回退"）。

### 2.1 自检八锚（批 1 B1）
| 观察 | 结论 | 下一步 |
|---|---|---|
| `rc=0`，`pass` 全 1，`crc == crc_core == 八锚`，`frames=8192`，CHIRP 在 L2 | 板上 FIRA 链与冻结 golden 逐位同 **[L1/EZKIT]**；M2 固件首次有数值门 | 记 DEC 行（M2 数值门建立）；B1/B2/B4/B5 的上板旁路等价从此有依据 |
| CHIRP 不在 L2 或 `frames ≠ 8192` | 自检未按设计跑（放置假设失败 / 未跑完）→ **自检结论作废**（不是 PASS 也不是 FAIL） | 重跑 ≥20 s；放置问题走 §8 备用方案 |
| 任一 `crc_core ≠ 锚` | **链前段漂**：chirp 读取/放置、加权、核 `tfb_analyze` 在板上与 host 不同 | 核 `map_chirp_addr`、`mismatch_idx`；**所有候选停**，上报 CTO。不是"FIRA 坏"的证据，也不排除 |
| `crc_core == 锚` 但 `crc ≠ 锚` | **板上 FIRA 链不 bit-exact**（与 F4/F5 bench PASS 矛盾） | 比较 bench 工程与 M2 工程差异（驱动版本/优化等级/放置/中断上下文）；`mismatch_sb` 定位子带；M2 波形不可信、**B1 不得启动**；上报 CTO |
| `rc≠0` 但 `crc` 全等锚 | 判据/计数逻辑异常 | 自检本身不可信，上报（代码问题，走 critic） |

### 2.2 负控制（批 1 B2；先决：`selftest_negctrl_built=1`，否则是 build 错，不是假绿）
| 观察 | 结论 | 下一步 |
|---|---|---|
| `rc=7`，`pass = 0×7,1`，`crc` 全 = F4 锚 | 自检真依赖权重（FG2 过） | 数值门有效 |
| `rc=0` | unity 权重也 PASS = **自检假绿**（不依赖被测权重） | B1 的 PASS 作废；查权重表读取路径；上报 |
| `rc=8` | 连 c=7（unity）也 FAIL | CRC/比较路径坏或 F4 连续性被破坏；自检不可信；上报 |
| 其它 | 不符预期 | 抄全表上报，不判 |

### 2.3 对照 build 后的墙钟差距（批 2；稳态 `beam_cyc_min`，`last` 须一致；t = tol，默认 5% [L4]）
记 B0 = 臂 0 稳态（`beam_cyc_min`）、A' = 臂 A' 稳态、bench = bench-P `beam_cyc_min`（与板上同取 min，口径对称；bench-P 无效时回退历史 F7 463,273 [L1]，它是 F7 的单次读数，报告明标"回退"）。先决：臂 0、臂 A' 都过 §2.0，且各自 `min ≤ last ≤ max`、`last` 与 `min` 一致（±t）；否则稳态不可判 → B6.3 不可判。
**步骤 0：差距是否复现** —— B0/bench ≤ 1+t → **未复现**：06-16 的 1.79× 在本次 run 上不存在（可能当时是离群/冷帧或环境差）；-O 的"消失/缩小"无从谈起；把本次臂 0 min/last/max 与 06-16 记录并列写 DEC 行，请 CTO 裁是否以本次稳态为新基线；B1 门按臂 0 WCET 判。
**步骤 1（复现后）：完备划分，按 A'/B0 分支，互斥无空档**：

| 观察 | 结论 | 下一步 |
|---|---|---|
| **反常**：A'/B0 > 1+t | -O 后更慢，读数可疑 | 核指纹/宏残留/首帧冷/音源；不入账，重测；**B6.3 无结论 → B1 挂起** |
| **不变**：\|A'/B0 − 1\| ≤ t | 假设 b 排除 **[L1]**；差距在核侧编译之外 | 三段归因（§2.4）；臂 A''/B 旁证系统库；排查表 #2/#3/#4/#15；仍无法归因 → 按 DEC-S7-RULINGS-02 另行申请内拆分副本；B1 基线仍 B0 |
| **消失**：A'/B0 < 1−t **且** A'/bench ≤ 1+t | 差距主因 = 优化等级（假设 b 成立 **[L1]**） | CTO 裁产品 build 是否改带 `-O`（改二进制 → M2 板门 + 八锚重跑）；新基线候选 = 臂 A'；排查表其余项降非阻塞；B1 用 -O 基线须 CTO 明示采纳 |
| **部分缩小**：A'/B0 < 1−t **且** A'/bench > 1+t | 优化等级是成因之一、非全部 **[L1]** | 三段占比归因定位剩余份额；#2（臂 A''）/#3/#4/#15；B1 基线用 A' 须 CTO 明示 |
| 臂 0 WCET 与 06-16 历史 830,903 相差 > t | 基线本身变了（build/宏/音源/首帧冷） | 先解释再用作基线（MAJOR，与上述分支并列） |

### 2.4 三段占比 板上 vs bench 不一致时的归因（批 2 As 或批 1 B1 + 批 3 bench-P）
先决：bench-P 过 §2.0.5；板上节过 §2.0；两侧 `w+ana+syn(+tx)+ovh == beam_last` 同帧恒等，ovh ∈ [0, max(5%·beam, 2000 cyc)]（两个容差都是 [L4]，`--ovh-tol-frac/--ovh-tol-cyc` 可调；bench 的 ovh 参考 ≈ 1–2 × `ccnt_read_cyc`）。**恒等式不成立 → 占比不入账，不再归因**。

| 观察 | 归因方向 | 用哪个读数证实/排除 |
|---|---|---|
| 三段板/bench **都在 ±t 内** | 差距不在三段里 | 剩余差 = tx 段 + ISR + 括号扰动 → `seg_tx`、`cb_cyc_max`、ovh；tx 是 M2 固有开销 |
| 三段**等比放大**（都 > 1+t 且互差 ≤ t） | 全局成因：优化等级、时钟、cache/放置一视同仁 | §2.3 已消差 → 优化等级；否则 #15 时钟（`g_m2_cclk_hz`，CTO-gated）、放置 |
| **单段独大**（= 比值最大 **且** 占比 Δ 最大的同一段）：ana 或 syn | FIRA 路径：驱动 debug 变体（#2，臂 A''/B 旁证）、FIR DONE 中断延迟/自旋（#4）、DMA scratch 放置与乒乓争用（#3）、中断抢占（#6） | 臂 A''、臂 B；`cb_cyc_max`；`.map` 三 pin 与 `s_seg_*` |
| **单段独大**：w | 纯核侧循环：优化等级、权重表/缓冲放置（Block 0 争用 #3）、链式读扰动（33 vs 25 次） | A' vs B0 的 w 段；`.map` `s_m2_xw/sb*` |
| 放大不等比且无单段独大 | 全局成因与 FIRA 路径成因叠加 | 先按 §2.3 排除优化等级，再用臂 A''/B 与 #15 拆 |

### 2.5 极性 QA（批 4；D8：实测映射 = `s_m2_chmap` 唯一依据）
| 观察 | 结论 | 处理与入库 |
|---|---|---|
| Step A `complete`、Step B `pass`、`opposite/weak/unclear = none`、映射 8 路齐 | 自家阵列极性统一 **[L1 逐只 + L1 通道级]** | 入库 `deliverables/algorithm_validation/POLQA_OWNARRAY_<date>.md`（R10 + A1/A2/B1/B2 原值 + 映射表 + L 标结论）→ critic → CTO → decisions_log 行；R10 第 8 项可写"极性 QA 已做" |
| Phase B **OPPOSITE**（通道 c） | 该路存在反接 | 功放断电 → 回 Step A 复核该路两只与 A2 → 改线（记哪只/哪端/时间）→ 重测该对三项应转 SAME；改线与复测都写进记录 §2.6；`lines_changed=yes` 且 `reverified=yes` 才算闭合，否则**一切声学测试停**（BLOCKER） |
| `lines_changed=yes` 但 `reverified≠yes`（无论有无 OPPOSITE） | 改线未复测 | MAJOR：该路 Phase A solo + Phase B 三项重测 |
| Phase A 弱/趋零 | 该路可能死/断/通道内单只反接 | 回 Step A 复核；未闭合前该路极性不定论 |
| 分不清的对 | 分辨率不够 | 挪麦/换参考路重测；仍分不清记录上报，不硬判 |
| **映射 = 恒等**（与约定 {c,15−c} 一致） | 权重/延时按下标即正确 | **CTO D8 裁定：`M2_CHMAP_FIX` 对自家阵列保持关闭**；PM 处置：P1 只做 A 臂 = 现状；DEC-S6-TEST1-METHOD-01 无冲突 |
| **映射 ≠ 恒等** | 需要置换表 | PM 处置：把实测映射换算成 `s_m2_chmap` 值写进记录 §3，**仍不翻宏**（CTO D8：不预授权）；P1 远场 A/B 后 CTO 逐次裁；触发铁律四对 DEC-S6-TEST1-METHOD-01 的强制重审 |

极性 QA 未闭合 → **一切声学测试停**；它不阻塞 B1 固件侧实施（B1 门见 §3），报告分开写。

### 2.6 实测核心时钟解码（批 1 附；条件 0 的唯一依据）
| 观察 | 结论 | 下一步 |
|---|---|---|
| 三个寄存器齐全、`PLLEN=1` 且 `PLLBP=0`、解出值三门全过 | 解出 CCLK **[L1/EZKIT 寄存器解码]** → 帧预算与 1.5× 线按它重算，报告后续全用重算值 | 条件 0 满足；解出值 ≠ 1e9 时历史帧预算/线作废（cycle 数不变，余量与 1.5× 判定全部重算） |
| `[CLK]` 未回填或缺项 | 条件 0 **未满足**（CTO 2026-09-03） | **B1 挂起**；差距分类仍可做（cycle 比值与时钟无关），余量只能标"参考" |
| `PLLEN = 0` 或 `PLLBP = 1` | PLL 未使能/旁路 → CCLK = CLKIN，**低于 Table 19 `fCCLK` 下限 400 MHz**，芯片没跑在规格频率上 | MAJOR + **条件 0 未满足**（CTO 定义：未实测则不满足；**PM 处置**：实测显示超规运行同样不放行，理由 = 余量判定无意义）：先查启动配置与 `adi_pwr_Init` 返回码 |
| MSEL = 0 或 CSEL = 0 | 按 ADI 源码语义取最大值（128 / 32，`adi_pwr_def_2156x.h:129/136`） | info：解码照常，报告写明代入值 |
| `DF = 1` | CLKIN 先二分频再乘 MSEL（非 21568 家族分支） | info：解码照常 [L1 源码] |
| `CLKIN` 不在 20–30 MHz | 抄写或出处存疑（数据手册 Table 33 `fCKIN`） | **不可判**：不按 [L1] 用 → 条件 0 未满足 |
| `fPLL` 不在 1.20–2.00 GHz | 寄存器读错位/抄错（数据手册 Table 20 `fPLLCLK`） | **不可判**：重读三个寄存器并附截图 → 条件 0 未满足 |
| 解出 `CCLK` 不在 400–1000 MHz | **CSEL 或 MSEL 抄错一位就会这样**（数据手册 Table 19 `fCCLK`） | **不可判**：重读并附截图 → 条件 0 未满足（防单点抄写错放行） |
| 解码值 ≠ bench `g_s7_cclk_hz` | 两工程不同频，或读法有误 | **BLOCKER**：忙等段与全部差距先按时钟比折算（排查表 #15），再谈 -O |

---

## 3. 每种结果对 B1 启动条件的影响（D4：B1 算本轮实施，但卡 B6.3 结论；口径 = 墙钟 WCET）

B1 可以启动，当且仅当下面五条**同时**成立；任一不成立 → **继续挂起**：

| # | 条件 | 依据 |
|---|---|---|
| 0 | **`[CLK]` 已回填且解出 M2 实测 CCLK**（§2.6）；帧预算与 1.5× 线按实测重算。未回填或缺项 → 条件 0 未满足 → 挂起；PLL 未使能/旁路、或解出值越三门之一 → 同样不放行（§2.6）；字段 0 照常按 128/32 解码；解码值与 bench 读回不一致 → BLOCKER 挂起。**不设旗位放行**（CTO 2026-09-03，DEC-S7-RULINGS-03） | C4：L3 撑强约束须挂待验；实测后升 [L1] |
| 1 | §2.3 有结论：未复现 / 消失 / 部分缩小 / 不变 四者之一（**反常、臂无效、未回填都不算结论**） | D4"不得在 B6.3 出结论之前启动" |
| 2 | 数值门建立：B1 自检 8/8 PASS **且** B2 负控制 rc=7，且两 build 均过 §2.0 | 验证计划 §1.1 D3 |
| 3 | B0/B1/B2 三个 build 无 BLOCKER | 读数归属与 FG |
| 4 | **余量**：以 CTO 采纳的基线 WCET `beam_cyc_max`（默认臂 0；`--use-optimized-baseline` 用臂 A'，仅当 §2.3 为消失/部分缩小时生效，且报告注明"须 CTO 明示采纳 -O 产品配置"）判：帧预算 / (基线 + B1 估算) ≥ 1.5 | D1 墙钟口径 |

余量判定（B1 估算 6,728 [L3]..52,352 [L4]，`S7_DSP_ASSESSMENT.md §8.1`）：
- 基线 + 52,352 仍 ≥ 1.5× → **可启动**：高端估计也在线内；实施后用 EQ-on/off 的 `beam_cyc` 差替代估算 [L1]。
- 只有基线 + 6,728 ≥ 1.5× → **刀刃**：只能以"实测后若越线即回退"为条件启动，须 CTO 明示；若 §2.3 为消失/部分缩小且 CTO 采纳 -O 基线，用 `--use-optimized-baseline` 重算。
- 基线 + 6,728 < 1.5× → **挂起**：连低端估计都越 1.5× 线 = 触发冻结令解冻条件；先按 §2.3/§2.4 归因回收。

结果 → B1 的映射：未复现 → 按臂 0 WCET 判，headline 带「待 CTO 裁新基线」；臂 0 与 06-16 历史差 > t 未解释 → headline 带「待 CTO」；消失/部分缩小 → 默认仍按臂 0，CTO 采纳 -O 后才用 A'；不变 → 臂 0；反常 → 挂起；自检/负控制任一不过 → 挂起；极性 QA 不影响 B1。T2 争用账只并列不相加；启动后的实测 EQ 成本对照 T2 固定侧 O1 60 [L4]，不坐实争用侧 15。

---

## 4. 宿主判读脚本 `sprint7/tools/s7_intake.py`（v3）

- 用法：`/usr/bin/python3 sprint7/tools/s7_intake.py --schema > filled.ini`（生成空白模板）→ 测试员/PM 填 → `/usr/bin/python3 sprint7/tools/s7_intake.py filled.ini`。
- 输出：Markdown 报告（每条带 PASS/BLOCKER/MAJOR/不可判/info + L 标 + 下一步），末尾汇总无效节、B1 门与极性 QA 状态。退出码 0 = 无 BLOCKER 且全可判；1 = 有 BLOCKER；2 = 有不可判项。
- 期望值来源：八锚与 F4 锚**运行时解析** `sprint4/dsp/fira/dolph_f5_goldens.h`（不复写）；帧预算/1.5× 线由 CCLK 派生（带 [L1 bench / L3 M2 推断] 双标）；历史对照量与 B1 估算带 L 标写在 `REFS` 表里，只作对照。
- 容差参数：`--tol`、`--rxpoll-tol`、`--overrun-tol`、`--full-scale-near`、`--ovh-tol-frac`、`--ovh-tol-cyc`；均为工作假设 [L4]，改了要在报告里注明。裁定旗：`--use-optimized-baseline`，只在 CTO 明示后使用（`--cclk-inference-accepted` 已按 DEC-S7-RULINGS-03 删除）。
- **假数据纪律**：脚本逻辑用 scratchpad 里的假回填文件验过（见 §5），假文件**不入库、不出现在任何文档正文**；本文与脚本里没有任何板上数字。
- 脚本不替代人的判断：报告里的每个"结论"都要过独立 critic + CTO 常识审。

---

## 5. 脚本逻辑验证（假数据，仅 scratchpad；此处只记场景与预期分类，不记任何数值；脚本 v2，2026-09-03 重跑）

| 场景（假数据） | 预期脚本输出 |
|---|---|
| 全绿 + 差距复现且消失 + 极性恒等 | 0 BLOCKER；§2.3 消失；B1 按臂 0 判，`--use-optimized-baseline` 时改按 A' 并提示须 CTO 采纳；极性 PASS 可入库 |
| 差距不变 + 三段 ana 独大 | §2.3 不变；§2.4 ana 独大 → FIRA 路径；B1 按 B0 基线判 |
| 自检某通道 `crc_core≠锚` | BLOCKER 链前段漂；B1 节无效；B1 挂起 |
| 负控制 `rc=0`（NEGCTRL 指纹在） | BLOCKER 自检假绿；B1 挂起 |
| 极性 OPPOSITE 未改线 | BLOCKER 声学测试停；不影响 B1 门 |
| 指纹残留（B0 里 `seg_w_cyc_last` 可见） | BLOCKER 该 build 作废；差距不可判；B1 挂起 |
| 空模板 | 全部不可判，退出码 2，无任何 PASS |
| `[CLK]` 未填 / PLL 未使能或旁路 / 解码值与 bench 不符 | 条件 0 未满足或 BLOCKER → B1 挂起；差距分类不受影响 |
| 真 1 GHz 配置（MSEL 80 / DF 0 / CSEL 2） | 解出 1e9 → 帧预算 1,333,333、线 888,889，与历史参考一致 |
| CSEL 抄错一位 / 字段 0 代入后超规 / CLKIN 越界 / PLL 旁路 | 三道数据手册门拦下 → 不可判或 MAJOR，条件 0 未满足，不会出「可启动」 |
| critic-F 边界集（20 + 15 个：bench cclk≠1e9 / last 与 min 不一致 / B0 误填 negctrl 指纹 / A' 指纹残留 / A' 板门不绿 / bench FG 不绿 / CHIRP 不在 L2 / frames 不满 / 差距未复现 / 反常 / B2 漏 NEGCTRL 宏 / rc=8 / rc=3 / 缺 -O 凭证 / 部分缩小 / 恰在线上 / ovh 为负 / rx≉poll / 改线未复测 等） | 无效节的读数不再进入差距/归因/B1；每支落到 §2 对应行 |

---

## 6. 与治理的对接
- 本方案不产生任何 LOCKED 决策；脚本输出是"初筛"，裁定权在 CTO。
- 数据回来后的入库路径：原件（截图/.map/R10）→ INI 汇总 → 脚本报告 → 独立 critic（核脚本报告与原件一致、无替补数字）→ CTO 常识审 → decisions_log 行（带 L 标与 reviewer 标）。
- 任何 L1 结果与已录 DEC 冲突 → 铁律四强制重审（先例：BEAM_POLARITY_CLOSURE 撤回"极性确认对"）。
- 本方案落库后 PM **停止**，不启动其他候选（DEC-S7-RULINGS-02）。

---
*PM lead @ claude-fable-5-1，2026-09-03（v3.3：CTO DEC-S7-RULINGS-03 落库；公式按 critic-F delta-3 改正为 21569 家族分支无 ÷2；delta-4 加数据手册三道合理性门；delta-5 修表号、条件 0 措辞与退出码一致性）。*
