# digest_E：sprint6 / knowledge_base / tools / references 记录阅读摘要

> ⚠ 公开版说明（2026-10-02）：本摘录按写时原文照录，里面会出现已撤回或已被推翻的数字（如 d=30、17×/33×、1.5k/3k/6k 子带标签、86–144 MCPS、6.4×）。采信任何数字前，以 `sprint2/docs/decisions_log.md` 和 `sprint7/docs/S7_RETRACTION_SUBBAND_EDGES.md` 为准。

- 生成：2026-10-02，只读（未改仓库、未派子 agent）。仓库根 = `/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow`（下文路径除标 `[仓外]` 者均相对此根）。
- 仓库快照：HEAD `263e984`（2026-10-02），共 155 个 commit；**首个 commit 是 `4bf0f52`（2026-06-02）**。因此任何文件的「git 首提日期」都不早于 2026-06-02；2026-06-09 的 `43aad40`（"ITC DSP 入库…文档/sprint历史"）一次性把 `SKILL.md`、`agents/`、`tools/`、`references/`、`sprint2/`、`sprint3/` 等入库（commit 说明里写 "knowledge_base/zip 已 ignore"）。**所以 git 首提日期 ≠ 撰写日期，本摘要对每个文件同时给出文内日期 / 首提 / mtime。**
- 出处标记：`[文内]`=文件正文（path:line）；`[git]`=commit 说明（hash）；`[fs]`=文件系统 mtime/目录列表；`[dec]`=decisions_log 交叉核对（非本范围文件，仅核日期/ID，行号来自 `sprint2/docs/decisions_log.md`）。可信度序按任务要求：decisions log > runbook/执行单 > git commit > memory。
- 读法：下列文件全部完整读完（`M1_FACT_BASE.md` 分两次读 1-261、262-390 行）。另读了：`knowledge_base/standards/JYT_directional_speaker.jpeg`（图像）、`knowledge_base/ezkit` 下 4 个小 .txt、2 个厂商 PDF 首页（pdftotext，仅为溯源）、仓外 3 个 .md。

---

## 0. 读了什么

### 0.1 `sprint6/` 下全部 tracked .md（31 个，485,430 B，全部已读完）

| # | path | bytes | tracked | 读完 | git 首提 | 备注（提交数 / 末提 / mtime） |
|---|---|---|---|---|---|---|
| 1 | sprint6/BOARD_TEST_INSTRUCTIONS.md | 7390 | 是 | 是 | cd77441 2026-06-16 | 1 次；mtime 06-16 10:56 |
| 2 | sprint6/STAGE4_ALGORITHM_VALIDATION_TEST.md | 15911 | 是 | 是 | 8e419f4 2026-06-25 | 2 次，末 4f87150 2026-07-08；mtime 07-08 20:53 |
| 3 | sprint6/STAGE4_BATCH_PLAN.md | 8306 | 是 | 是 | caf6708 2026-06-09 | 6 次，末 28ad3a3 06-12 |
| 4 | sprint6/STAGE4_BRINGUP_CHECKLIST.md | 11719 | 是 | 是 | 218ead7 2026-06-06 | 5 次，末 07530d1 06-08 |
| 5 | sprint6/STAGE4_TESTER_RUNBOOK.md | 21541 | 是 | 是 | ec21908 2026-06-09 | 6 次，末 28ad3a3 06-12 |
| 6 | sprint6/dsp/audio/DEPRECATED_LOOSE_COPIES.md | 1867 | 是 | 是 | b6bc5fe 2026-09-02 | 1 次 |
| 7 | sprint6/dsp/audio/M1_ARCH_INPUT_DATA.md | 36276 | 是 | 是 | 7bf2730 2026-06-06 | 1 次 |
| 8 | sprint6/dsp/audio/M1_ARCH_REVIEW_R34.md | 15161 | 是 | 是 | b5878bf 2026-06-06 | 1 次 |
| 9 | sprint6/dsp/audio/M1_FACT_BASE.md | 55417 | 是 | 是(2 次读) | 6655d63 2026-06-06 | 1 次 |
| 10 | sprint6/dsp/audio/M1_HWCONFIRM1B_RX_SLOT_HW_RULING.md | 11324 | 是 | 是 | dc87606 2026-06-08 | 1 次 |
| 11 | sprint6/dsp/audio/M1_HWCONFIRM1_RX_SINGLE_SLOT.md | 9600 | 是 | 是 | d5517de 2026-06-06 | 1 次 |
| 12 | sprint6/dsp/audio/M1_IOCALLBACK_L1_ADJUDICATION.md | 10666 | 是 | 是 | b64f7e6 2026-06-08 | 1 次 |
| 13 | sprint6/dsp/audio/M1_SOFTCFG_ALL5_RC1_ADJUDICATION.md | 12732 | 是 | 是 | 19748df 2026-06-09 | 1 次 |
| 14 | sprint6/dsp/audio/M1_SOFTCFG_BOARD_RESCOPE.md | 5665 | 是 | 是 | 511fd07 2026-06-11 | 1 次 |
| 15 | sprint6/dsp/audio/M1_SOFTCFG_RC_ADJUDICATION.md | 12379 | 是 | 是 | 07530d1 2026-06-08 | 1 次 |
| 16 | sprint6/dsp/audio/M1_SOFTCFG_U6_ADDR_SWEEP.md | 15107 | 是 | 是 | b3d7f74 2026-06-09 | 4 次，末 511fd07 06-11 |
| 17 | sprint6/dsp/audio/M1_SOFTCFG_U6_NACK_ROOTCAUSE.md | 17388 | 是 | 是 | 3a3bb50 2026-06-09 | 3 次，末 511fd07 06-11 |
| 18 | sprint6/dsp/audio/M1_SRU_ROUTING_SURVEY.md | 11894 | 是 | 是 | 3bf91af 2026-06-08 | 1 次 |
| 19 | sprint6/dsp/audio/M1_SYMBOL_PRESURVEY.md | 8017 | 是 | 是 | 43aad40 2026-06-09 | 1 次；mtime 06-06 17:02（文内日期 06-06，晚 3 天才入库） |
| 20 | sprint6/dsp/audio/M1_SYMBOL_SURVEY.md | 16436 | 是 | 是 | 59ba0e5 2026-06-06 | 1 次 |
| 21 | sprint6/dsp/audio/M2_BEAM_WEIGHTING_SURVEY.md | 13673 | 是 | 是 | 4db187c 2026-06-08 | 1 次 |
| 22 | sprint6/dsp/audio/M2_Q_BOUNDARY_SURVEY.md | 25709 | 是 | 是 | 988f950 2026-06-08 | 3 次，末 01b8522 06-16 |
| 23 | sprint6/dsp/audio/M2_SURVEY.md | 26170 | 是 | 是 | 5136d5e 2026-06-08 | 1 次 |
| 24 | sprint6/dsp/audio/_m1_facts_S1_example_anatomy.md | 21861 | 是 | 是 | 6655d63 2026-06-06 | 1 次 |
| 25 | sprint6/dsp/audio/_m1_facts_S2_symbol_inventory.md | 20123 | 是 | 是 | 6655d63 2026-06-06 | 1 次 |
| 26 | sprint6/dsp/audio/_m1_facts_S3_datasheets.md | 20704 | 是 | 是 | 6655d63 2026-06-06 | 1 次 |
| 27 | sprint6/dsp/audio/_m1_facts_S4_topology.md | 20036 | 是 | 是 | 6655d63 2026-06-06 | 1 次 |
| 28 | sprint6/dsp/audio/m1_cces_project/M1_CCES_IMPORT_GUIDE.md | 18641 | 是 | 是 | cf0c34d 2026-06-08 | 6 次，末 28ad3a3 06-12 |
| 29 | sprint6/dsp/audio/m1_project/DEPRECATED.md | 756 | 是 | 是 | b6bc5fe 2026-09-02 | 1 次 |
| 30 | sprint6/dsp/audio/m1_project/M1_PROJECT_README.md | 5497 | 是 | 是 | 787a7a1 2026-06-08 | 2 次，末 b6bc5fe 09-02（加过期标注） |
| 31 | sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md | 7464 | 是 | 是 | 59ba0e5 2026-06-06 | 1 次 |

### 0.2 `knowledge_base/`（仓内）下全部 .md（11 个，80,739 B，全部已读完）

`.gitignore:2` 自 `43aad40`（2026-06-09）起忽略整个 `knowledge_base/`（`git log -- .gitignore` 核）。此前已入库的 7 个文件仍 tracked（7d24e6e 2026-06-03 的 1 个头文件 + 3c4bf56 2026-06-05 的 6 个 hardware_input 文件）；KB-EXT 登记文件 2026-09-02 以 `git add -f` 强制跟踪（KB-EXT…:6）；合计 8 个 tracked，其余 untracked。

| # | path | bytes | tracked | 读完 | git 首提 / mtime |
|---|---|---|---|---|---|
| 1 | knowledge_base/competitor/full_teardown_v2.md | 9909 | 否（untracked） | 是 | mtime 2026-05-29 15:43:05 |
| 2 | knowledge_base/competitor/KB-EXT-SPON-HIT9616A12_FIRMWARE_REG.md | 6289 | 是（force-add） | 是 | b6bc5fe 2026-09-02；末 c9c3f91 2026-09-02；mtime 09-02 22:27 |
| 3 | knowledge_base/competitor/SPL_anechoic_measurement_archived.md | 3770 | 否 | 是 | mtime 2026-05-30 16:04:14 |
| 4 | knowledge_base/ezkit/INDEX.md | 2973 | 否 | 是 | mtime 2026-06-01 17:46:44 |
| 5 | knowledge_base/ezkit/prep/PREP-DSP-migration.md | 9172 | 否 | 是 | mtime 2026-06-01 17:50:42 |
| 6 | knowledge_base/ezkit/prep/PREP-HW-bringup.md | 6664 | 否 | 是 | mtime 2026-06-01 17:51:26 |
| 7 | knowledge_base/ezkit/prep/PREP-TST-cyclecount.md | 7202 | 否 | 是 | mtime 2026-06-01 17:52:13 |
| 8 | knowledge_base/hardware_input/定向音柱AI数据_extracted.md | 7480 | 是 | 是 | 3c4bf56 2026-06-05；mtime 05-29 19:16:13 |
| 9 | knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md | 3600 | 是 | 是 | 3c4bf56 2026-06-05；mtime 05-30 15:53:49 |
| 10 | knowledge_base/hardware_input/KB-DRV-TEST-001_extracted.md | 12611 | 是 | 是 | 3c4bf56 2026-06-05；末 6d0a0af 2026-06-05；mtime 06-05 16:56:28 |
| 11 | knowledge_base/hardware_input/KB-DRV-TEST-001_PROPAGATION.md | 11069 | 是 | 是 | 3c4bf56 2026-06-05；mtime 06-05 15:35:59 |

### 0.3 `[仓外]` 但属于「knowledge_base」逻辑内容的 .md（父目录 `/home/it1234/algorithm_speaker/` 不是 git 仓库，故全部 untracked；因其是真正的论文库而读）

| path | bytes | 读完 | mtime |
|---|---|---|---|
| /home/it1234/algorithm_speaker/knowledge_base/papers/2026-09_side30/README_论文索引.md | 6375 | 是 | 2026-09-28 01:33:23 |
| /home/it1234/algorithm_speaker/knowledge_base/measurements/competitor_anechoic.md | 1182 | 是 | 2026-05-26 15:14:33 |
| /home/it1234/algorithm_speaker/ee-agent-team-starter/README.md | 3105 | 是（该目录其余文件只列名） | 2026-07-17 11:05 |

### 0.4 `tools/`（20 个 .md，100,235 B）与 `references/`（2 个 .md，10,887 B）——全部 tracked、全部读完

- references/agent-directory.md 4099 B；references/communication-protocol.md 6788 B。**git 首提均为 43aad40 2026-06-09（各 1 次）；mtime 均为 2026-05-24 12:46:34**。
- tools/ 五个子目录各 4 件套（均 43aad40 首提；mtime 05-24）：

| 目录 | profile | soul | skill | memory | mtime 范围 |
|---|---|---|---|---|---|
| tools/cad-interface | 2169 | 3779 | 6897 | 4384 | 05-24 12:27–12:29 |
| tools/code-execution | 2128 | 4293 | 6524 | 4790 | 05-24 12:25–12:27 |
| tools/database | 2109 | 4122 | 12637 | 4167 | 05-24 12:31–12:33 |
| tools/matlab | 2302 | 4440 | 8729 | 5566 | 05-24 12:29–12:31 |
| tools/web-search | 2779 | 4613 | 8924 | 4883 | 05-24 12:33–12:35 |

- 目录 mtime：`tools/`、`references/`、`agents/` 均为 2026-05-26 11:33:42（[fs]，推测=包被放入工作目录的时刻；文件内部 mtime 则保留 05-24）。上级目录 `Kimi_Agent_多Agent协作方案` mtime 同为 05-26 11:33。

### 0.5 非 .md 文件（只列名/类型）

**sprint6/ 非 md（54 个 tracked）**
- `sprint6/dsp/audio/` 顶层：`m1_loopback_tdm.c`(54,753 B)/`.h`(6,321 B)（松散副本，0346442 06-08，已被标过期）、`run_guard_check.sh`(9,519 B)。
- `guard_stub_inc/`（10 个桌面解析用 stub 头：adi_initialize.h、cdef21569.h、sru21569.h、drivers/sport/adi_sport.h、drivers/twi/adi_twi_2156x.h、services/pdma/adi_pdma_2156x.h、services/pwr/adi_pwr.h、services/spu/adi_spu.h、sys/cache.h、sys/platform.h；0346442 06-08 与 43aad40 06-09）。
- `board_artifacts/`（3 个板上 .map.xml，各约 1.06–1.08 MB）：`M1_Loopback_M2build_1B_20260611.map.xml`(bbc6978 06-11)、`M1_Loopback_M1build_1A_20260616.map.xml`(01b8522 06-16)、`M1_Loopback_M2build_1B_PASS_20260616.map.xml`(1fb9a06 06-16)。
- `m1_cces_project/`：`.project`、`.cproject`、`system.svc`、`src/`{m1_main.c、m1_sru.c、m1_softconfig.c、m1_cyc.c、m1_loopback_tdm.c(86,203 B)/.h、ADAU_1962Common.h、ADAU_1979Common.h、m2_static_txtest_table.h(4bf18b6 07-02)、m2_static_txtest375_table.h(02bc474 07-07)、m2_wtbl_q15.h(7686c05 09-26)}、`system/`{adi_initialize.c/.h、drivers/sport/adi_sport_config_2156x.h、drivers/twi/adi_twi_config_2156x.h、services/pdma/adi_pdma_config_2156x.h、pinmux/GeneratedSources/pinmux_config.c、sru/sru_config.c、SoftConfig_EV_SOMCRR_EZKIT_ADC_DAC.c、SoftConfig_EV_SOMCRR_EZKIT_ADAU_Reset.c、startup_ldf/{app_IVT.s、app_startup.s、app_heaptab.c、m1_app.ldf}}（骨架 cf0c34d 06-08）。
- `m1_project/`（旧骨架，已过期）：run_guard_check.sh、src/{m1_main.c、m1_cyc.c、m1_sru.c、m1_softconfig.c}、system/startup_ldf/m1_app.ldf（787a7a1 06-08）。
- `dsp/eq/`：eq_limiter.c/.h、eq_test.c、eq_compute_budget.py、eq_verify.py（59ba0e5 06-06）。

**knowledge_base/ 非 md（仓内，共 1279 个非 md 文件；只列顶层）**
- `competitor/`：无非 md。`measurements/`、`papers/`、`ezkit/raw/`：**目录存在但为空**（papers、measurements 目录 mtime 2026-05-26 15:02；raw 06-01 17:46）。
- `standards/JYT_directional_speaker.jpeg`（341,041 B，mtime 2026-05-29 17:57，untracked）。内容已看图：JY/T XXXX—XXXX（标准号空白）「定向扩声系统」6.3.1.1 指向性（3 m 处远场声压级差）、表 9（500/1000/2000/4000 Hz 各 30°/90°/180°，一/二/三级）、表 10（空场应备声压级 ≤75 dB(A)；1000/4000 Hz 稳态声场不均匀度 ≤10 dB；STIPA ≥0.50）。
- `hardware_input/KB-DRV-TEST-001_raw/`：`SPL_vs_freq_LMS.jpeg`(1,136,717 B)、`TS_params_LEAP.jpeg`(1,277,263 B)，mtime 06-01 17:37，tracked（3c4bf56）。
- `ezkit/bsp/`（282 个文件，142 MB，仅 `fira_headers/adi_fir_legacy_2156x.h` 被 tracked，7d24e6e 2026-06-03）：`a2b/ADSP-21569的A2B开发详解.pdf`；`app_notes/`（EE-414 功耗 pdf+zip、System Optimization Techniques pdf+code zip、EE-408 FIR/IIR 加速器 pdf+code zip 及已解压 `fira_accel_code/EE408V02/`（README.txt 写 "Date Created: August 19, 2019"）、DMC 板级设计指南 pdf，共 264 文件）；`datasheets/`（7 个 PDF：`adsp-21562-21563-21565-21566-21567-21569数据手册.pdf` 与 `ADSP-2156x-Datasheet-EN.pdf`（文件名不同但字节数相同 2,707,557 B）、ADAU1962A.pdf、adau1979.pdf、1963fc.pdf、is25lp512m-rmle-20210804-….pdf、ltc3307a.pdf）；`hw_reference/ADSP-21569 SHARC+ Processor Hardware Reference.pdf`(16.8 MB)；`sw_reference/SHARC+ Core Programming Reference….pdf`；`ibis_models/`（BSDL + IBIS zip）；`installers_windows/`（ADI_ADSP-2156x_EZ-KIT-Rel1.0.1.exe、ADI_EV-2156x_EZ-KIT-Rel1.0.1.exe、ADI_EV-2156x_EZ-KIT-Rel3.0.0.exe）；`reference_design/`（ev-21569-som-design-database.zip、ev-somcrr-ezkit-design-database.zip，ADI 官方设计库）。多数 mtime 2026-06-01 18:40。
- `ezkit/vendor_docs/`（994 个文件，102 MB，全 untracked，mtime 多为 2026-06-01 18:40:45）：`altium_lib/`（6：SCHLIB/PcbLib/rar/zip）、`cces_examples/`（794 文件：`code/` 下 9 个例程工程 ADSP21569_DDR/KEY/LED/LEDKEY/UART、Audio_Loopback_TDM、Audio_Loopback_TDM16、Audio_Passthrough_I2S、Power_On_Self_Test；`2. 开发板例程.zip`；`请一定先读我.txt`）、`flash_driver/Legacy_SPI/is25lp512m_dpia_2156x`（17）、`install_notes/`（2 个 txt：ADI 下载链接、CCES 2.11.1 链接）、`mechanical/`（2 个 PcbDoc）、`schematics/`（V1.0/V1.2/V2.1 各 3 份 PDF，共 9：A2B 子卡板V2.1(1).pdf；ADSP21569核心板原理图.pdf；底板三版 = 「ADSP21569底板原理图V1.0（老款，无USBi接口）」「ADSP21569底板V1.2（2024年最新，USBi接口单独引出）」「AD-EXKIT-双A2B底板（2026最新改版）」）、`sigma_examples/`（142：SigmaStudio 图形化工程 .dspproj）、`tutorials/`（22 个 PDF，板卡卖家教程，编号 0–21：硬件更新说明、初始状态说明、在线调试、CCES 例程详解、Flash 烧写、SigmaStudio 图形化编程系列、A2B 开发系列）。
- 全库 (kb) 文件类型计数前列：.c 184、.doj 183、.d 179、.h 153、.mk 133、.dspproj 61、.s 52、.pdf 45、.txt 37、.dat 36、.md 11。

**仓外 `[仓外]` /home/it1234/algorithm_speaker/knowledge_base/（24 个文件，不在 git）**
- `papers/` 第一批（mtime 2026-05-26 14:19–14:29）：`A_Current_Distribution_for_Broadside_Arrays_Which_Optimizes_the_Relationship_between_Beam_Width_and_Side-Lobe_Level.pdf`(2.6 MB)、`Properties_of_Dolph-Chebyshev_Weighting_Functions.pdf`、`boone2009.pdf`、`Design_of_Differential_Loudspe.pdf`(7.3 MB)、`Optimum Array Processing - 2002 - Van Trees.pdf`(137 MB)。
- `papers/2026-09_side30/`（mtime 2026-09-26 17:24；D_cbt 09-28 00:26）：A_sound_zones（4 PDF）、B_column_practice（8 PDF）、C_robust_calibration（3 PDF + 1 个 Chojnacki_2024 全文 XML）、D_cbt（Keele_2002_AES5653 1 PDF）、`README_论文索引.md`。
- `measurements/competitor_anechoic.md`；`competitor/` 为空目录。

**`~/下载/`（非仓库，只列与本范围对应的源件；名称/mtime，未读内容）**：`相控阵音柱_声压级测试结果.pdf`(191,254 B, 2026-05-26 14:04；另有 "(1)" 副本 14:19)、`定向音柱AI数据.docx`(14,127 B, 05-27 19:56)、`定向音柱AI数据 (1).docx`(14,795 B, 05-30 15:50)、`adi-CrossCoreEmbeddedStudio-linux-x86-2.12.1.deb`(682,742,136 B, 06-01 12:33)、`最简单的CCES注册详解V2.0.pdf`(06-01 13:06)、一个 agent 团队配置压缩包(2026-05-26 20:12；公开版不写文件名，可能属于另一项目)。**另**：`/home/it1234/algorithm_speaker/HIT-9616A12_Firmware_[Std_2025_CN]_V1.0.5_20260630.zip`(26,442,922 B, 2026-07-31 14:59) 与 KB-EXT 登记一致；`/home/it1234/algorithm_speaker/ee-agent-team-starter/`（00_governance、01_architecture、02_agent_templates、AGENT_TEAM_PLAYBOOK.md、GENERATION_PROMPT.md、ROSTER_EE.md；目录 mtime 07-17–07-22）。

---

## 1. 文件清单（日期 | path | 类型 | 一句话内容 | 状态(原文)）

日期列 = 文内日期（括号内为 git 首提/mtime）。「状态(原文)」尽量逐字，已去掉 emoji。

### 1.1 sprint6 顶层

| 日期 | path | 类型 | 一句话内容 | 状态(原文) |
|---|---|---|---|---|
| 2026-06-06（git 06-06；末次 06-08） | sprint6/STAGE4_BRINGUP_CHECKLIST.md | 预防清单 | 阶段 4 bring-up 预防清单：A 符号/头文件、B 内存放置/效度、C 测量口径/假绿、D 帧口径、E 流程/协作、F 板侧 60 秒动作；06-08 增 A6(.project XML 禁 `--`)、E6(工程跨机用 git/zip)、E7、E8 | :3「性质：2026-06-06 全天错误/教训的预防性总结（R24–R34 共 11 轮 critic 门 + 1 次 workflow 编排）」；:130「生成 2026-06-06 … 维护人：PM lead；变更过 critic 门」 |
| 2026-06-09（git 06-09；末次 06-12） | sprint6/STAGE4_BATCH_PLAN.md | 计划 | CTO 出门期间由他人代测的批量收尾计划：剩余工作 A–J 的可整合性分类、诊断镜像、测试节奏、§4B CTO-gated defer 清单 | :3「缘起 2026-06-09：CTO 出门，无法频繁测板，由他人代测」；:98 页脚「生成 2026-06-09，PM lead。批量包实现待 dsp+critic 门。」（页脚陈旧，正文已含 R55/R57 戳 :12,:47,:70,:92,:96） |
| 2026-06-09（git 06-09；末次 06-12） | sprint6/STAGE4_TESTER_RUNBOOK.md | runbook | 非专家测试员「傻瓜手册」：1A softcfg/对齐 dump、1B M2 FIRA、交接、PM 判读表、第 2 次测试；顶部有 R55 终局横幅 | :1「测试员傻瓜手册（CTO 出门期间代测）」；:13「R55 终局（2026-06-11，先读这个）」；:163「判读表【R55 存史…】」；:197「第 2 次测试 · 验证【R55 取消…本节存史】」 |
| 2026-06-16（git 06-16） | sprint6/BOARD_TEST_INSTRUCTIONS.md | 板测说明 | 给测试员的单次会话精简版：M1 build 取对齐 dump → M2 build FIRA 验证 → 恢复并打包发回 | :1「板测说明（给测试员，2026-06-16 单次会话版）」；:106「精简自 sprint6/STAGE4_TESTER_RUNBOOK.md（权威源，已过 critic R58）。本说明 2026-06-16 快照。」 |
| 2026-06-17（git 06-25；修订 06-29/07-08） | sprint6/STAGE4_ALGORITHM_VALIDATION_TEST.md | 整机测试文档 | 真功放 + 16 元阵列上验证 M2 broadside 波束有效性：测试 0–5、综合判定 A–F、记录表、安全红线；含 06-29 两处方法订正与 07-08 极性订正横幅 | :224「PM lead，2026-06-17。整机算法验证测试 v1。critic R61 CONDITIONAL→修 MAJOR-1(beam_cyc 口径)+2 MINOR→PASS。reviewer: critic @ claude-opus-4-8[1m] / 2026-06-17。」；:113「DEC-S6-TEST3-METHOD-01 …待 critic + CTO」 |

### 1.2 sprint6/dsp/audio（2026-06-06 ~ 06-16 的研究/裁定链 + 2026-09-02 过期标注）

| 日期 | path | 类型 | 一句话内容 | 状态(原文) |
|---|---|---|---|---|
| 2026-06-06（git 06-09） | sprint6/dsp/audio/M1_SYMBOL_PRESURVEY.md | 调研 | M1 符号预调研：SPORT/PDMA/TWI/codec/SPU/SRU/CCNT 逐符号对应例程 Audio_Loopback_TDM 行号 [L1] vs [board-confirm]；缓存一致性与缓冲放置裁定 | :3「dsp-algorithm teammate, 2026-06-06. CTO directive #1: survey BEFORE writing」；:4「No commit」（注：同一文件 :3-4 自述尚未 commit，实际 06-09 才随 43aad40 入库） |
| 2026-06-06 | sprint6/dsp/audio/M1_SYMBOL_SURVEY.md | 调研 | codec 寄存器序、TDM8 slot 口径、SPORT4 配置、符号路径表、io-callback 探针提案；吸收 PRESURVEY；披露「实现初稿」已写但不入库 | :4「RESEARCH + symbol pre-survey ONLY; M1 implementation HELD pending CTO architecture… No commit」；:11-13 IMPLEMENTATION-DRAFT DISCLOSURE |
| 2026-06-06 | sprint6/dsp/audio/_m1_facts_S1_example_anatomy.md | 事实库子件 | Audio_Loopback_TDM 例程 bring-up 解剖（42 条事实） | :217「VERDICT: CLEAN」，:213-223 VERIFIER_REPORT（claude-opus-4-8, 2026-06-06） |
| 2026-06-06 | sprint6/dsp/audio/_m1_facts_S2_symbol_inventory.md | 事实库子件 | SPORT/TWI/SPU/PDMA/codec 符号清单与头文件后缀非对称（49 条） | :203「VERDICT: CLEAN」，:189-204 |
| 2026-06-06 | sprint6/dsp/audio/_m1_facts_S3_datasheets.md | 事实库子件 | ADAU1979(ADC)/ADAU1962A(DAC) datasheet 寄存器序与 TDM8（43 条） | :199「VERDICT: ISSUES (仅 1 类表号标注偏移… 非 FABRICATION)」 |
| 2026-06-06 | sprint6/dsp/audio/_m1_facts_S4_topology.md | 事实库子件 | SPORT4 拓扑/主从时钟/M2 接口预留/board-confirm（49 条） | :179「VERDICT: CLEAN」，:172-181 |
| 2026-06-06 | sprint6/dsp/audio/M1_FACT_BASE.md | 事实底座 | 汇总 183 条核验事实 + 17 条 board-confirm + [inferred] 隔离区 | :3「调研型产出：仅事实 + 来源，不写实现代码、不做架构选择」；:5「核验状态：经 workflow 4 路对抗引用核验 … 2026-06-06」；:389「汇总：bring-up 前期调研员 / 2026-06-06」 |
| 2026-06-06 | sprint6/dsp/audio/M1_ARCH_INPUT_DATA.md | 数据调取 | CTO 派单 14 条目：block-rate(64 vs 120、187.5 vs 750 Hz)、1-in/8-out、DAC 8-of-12、缓冲共置、17 条板上确认清单、启动序、时钟拓扑 | :1「数据调取型产出（CTO 派单 14 条目逐条）」；:7「调取员 / 2026-06-06」；:314「数据齐, HALT」 |
| 2026-06-06 | sprint6/dsp/audio/M1_ARCH_REVIEW_R34.md | 架构审查 | critic 审「claude.ai 总工」四开口建议：①750 Hz/64 ②1→8 复制 ③TDM8 前 8 路+buffer 重算 ④pin（前提需修正） | :1「M1 架构建议独立审查（R34）」；:5「HALT 在审查产出——不出新架构, 架构由 CTO 拍。CTO 派单 2026-06-06」；:7 末「reviewer: critic @ claude-opus-4-8 / 2026-06-06」（:7 同行夹带 JSONL 原始记录） |
| 2026-06-06 | sprint6/dsp/audio/M1_HWCONFIRM1_RX_SINGLE_SLOT.md | 调研 | RX 单 slot 可行性：路径 A（ADC 发 1 slot）被 datasheet 否决；路径 B（SPORT 只收 slot 0）类可行；RX buffer 512/1024/2048 B 三候选 | :11「VERDICT: (c) local evidence is insufficient…」；:117,:120「HALT … critic gate pending」 |
| 2026-06-08 | sprint6/dsp/audio/M1_HWCONFIRM1B_RX_SLOT_HW_RULING.md | 硬件裁定 | 按 HRM（WSIZE=通道数-1、SPORT_CS 位使能、MCPDE=1 packed）判 1-slot RX 硬件合法→512 B；给 CTO 的 grep 配方 G1–G4 | :3「dsp-algorithm teammate, 2026-06-08」；:138,:140「HALT … critic gate pending」 |
| 2026-06-08 | sprint6/dsp/audio/M1_SRU_ROUTING_SURVEY.md | 调研 | SRU 路由表（8 路由+6 引脚使能）、SoftConfig 使能表、F-SRU-1 [CRITICAL]：例程 Switch_Configurator 被注释 | :3「dsp-algorithm teammate, 2026-06-08」；:98-103 F-SRU-1；:138「HALT: routing table delivered…」 |
| 2026-06-08 | sprint6/dsp/audio/M1_IOCALLBACK_L1_ADJUDICATION.md | 口径裁定 | M1 上板 PASS 后：g_m1_cb_cyc_last=12839 cyc → 9.629 MCPS，裁定其为 M1 app 负载(b)而非 io-callback 核(a)；T2 账 95.59(保守) vs 75.22；bench 污染核 | :3「M1 passthrough is board-PASS (5 readouts [L1])」；:130「HALT: awaiting CTO ledger-caliber ruling」 |
| 2026-06-08 | sprint6/dsp/audio/M2_SURVEY.md | 调研 | FIRA 波束入 M1 回调的接入点、冻结接口(fira_tree.h)、pin Block1、750 Hz 帧 deadline 核（R43 口径修正） | :3「M2 调研专员, 2026-06-08」；:8「M1 透传 loopback 已上板 PASS」；:355-358「HALT … reviewer pending: critic gate」 |
| 2026-06-08 | sprint6/dsp/audio/M2_BEAM_WEIGHTING_SURVEY.md | 调研 | 加权落级三方案：输入级 / 子带 frac-delay / 两者；dsp 推荐「both」并保留「输入级」回退 | :3「2026-06-08」；:46-48「dsp RECOMMENDATION (recommendation != ruling)」；:164-168「HALT … reviewer pending」 |
| 2026-06-08（板闭合 06-16） | sprint6/dsp/audio/M2_Q_BOUNDARY_SURVEY.md | 调研+测试设计 | M1 int32(24-in-32) ↔ FIRA Q31 转换点与对齐；R14 CRC 锚点溯源（F4=0x2E0D8C6E、F5 八行表）；bit-exact 桌面测试设计；06-16 横幅：对齐=左（identity） | :3「2026-06-08」；:152-165 横幅「CLOSED = LEFT (board L1, 2026-06-16, DEC-S6-ALIGN-LEFT-01)」；:316「No commit. reviewer pending」（正文未改） |
| 2026-06-08 | sprint6/dsp/audio/M1_SOFTCFG_RC_ADJUDICATION.md | 裁定 | softcfg_rc=1 = 真 TWI 写失败；「音频能通」判别不了是否搭载板默认；三态偏 (III)；per-write 仪表化块 | :3「2026-06-08」；:162「HALT: awaiting CTO -> apply instrumentation (after critic R44)」 |
| 2026-06-08 | sprint6/dsp/audio/M1_SOFTCFG_ALL5_RC1_ADJUDICATION.md | 裁定 | rc[0..4] 全=1 且 open/addr=0：读安装版 CCES 2.12.1 头证 adi_twi_Write 为阻塞、第 4 参=bRestart，推翻 bWaitFlag 前提→F-SRU-1 未生效 | :3「2026-06-08」；:161「HALT: awaiting CTO … (after critic R48)」 |
| 2026-06-08（横幅 06-10/06-11） | sprint6/dsp/audio/M1_SOFTCFG_U6_NACK_ROOTCAUSE.md | 根因调研 | U6 全 NACK(code 11)：R0 总线级 vs R1 地址；codec_write_rc 判别式；block B 修法分支 | :3-8「R55 FINAL (2026-06-11)… All block-B branches below are MOOT for this carrier」；:10-16 R51/R52 CORRECTION（hwerr 为枚举序数）；:214「HALT」 |
| 2026-06-08（横幅 06-11） | sprint6/dsp/audio/M1_SOFTCFG_U6_ADDR_SWEEP.md | 诊断 | 0x20–0x27 地址自探测 + 判读表 + 一次性读数清单；R55 后判读表仅存史 | :1-10「R55 FINAL (2026-06-11): the sweep RAN … exactly-one ACK at 0x21 … R1a row below is superseded」；:12「2026-06-08」 |
| 2026-06-11 | sprint6/dsp/audio/M1_SOFTCFG_BOARD_RESCOPE.md | 终局裁决 | 板身份坐实 = 第三方 AD-EXKIT V2.1 + ADSP-21569-SOM REV 1.1；codec 复位硬连线；F-SRU-1 对本板不适用；override build 取消；判据替换；C7 传播清单 | :1「M1 softcfg 终局：板身份揭晓 → F-SRU-1 re-scope 关闭（CTO 裁决 2026-06-11）」；:4-5「critic R54 CONDITIONAL PASS … R55 增量过门 → CTO 采纳」；:44「CTO 裁决（DEC-S6-FSRU1-RESCOPE-01，2026-06-11 采纳）」 |
| 2026-06-08（板闭合 06-12） | sprint6/dsp/audio/m1_cces_project/M1_CCES_IMPORT_GUIDE.md | 指南 | M1_Loopback CCES 工程一键导入、F1–F7 回退、M2 接线(M2_FIRA_INLOOP)、CTO 板上动作清单 | :3「dsp-algorithm teammate, 2026-06-08 … No commit (PM lands after critic R41)」；:6「this machine has NO CCES…」 |
| 2026-09-02 | sprint6/dsp/audio/m1_project/M1_PROJECT_README.md | README(已过期) | 06-08 route-B 早期骨架构建清单与 CTO 板上动作 | :1「已过期（2026-09-02 标注）：本目录 m1_project/ 是 2026-06-08 的 route-B 早期骨架…只加标注不删除」；:4「2026-06-08」 |
| 2026-09-02 | sprint6/dsp/audio/m1_project/DEPRECATED.md | 过期标注 | m1_project/ 被 m1_cces_project/ 取代 | :1「DEPRECATED（2026-09-02 标注，只加注不删除）」 |
| 2026-09-02 | sprint6/dsp/audio/DEPRECATED_LOOSE_COPIES.md | 过期标注 | 松散副本 m1_loopback_tdm.{c,h} 与 m1_project/ 过期；CTO 2026-09-02「只加标注不删除」；m1_softconfig.c 受 CTO_OK hook 保护 | :1「已过期副本标注（2026-09-02 housekeeping，只加注不删除）」；:11「CTO 2026-09-02 裁定『只加标注不删除』」 |

### 1.3 sprint6/dsp/eq

| 日期 | path | 类型 | 一句话内容 | 状态(原文) |
|---|---|---|---|---|
| 2026-06-06 | sprint6/dsp/eq/EQ_INTEGRATION_NOTE.md | 集成说明 | O1 EQ(master-bus biquad)+per-channel 限幅器桌面交付、M2 adapter 检查表、桌面验证(float32 vs scipy 1.51e-07)、算力账 14.4–55.2 MCPS [L2]、诚实缺口(t_base=[L4]、系数待 R3) | :4「Decision in archive: DEC-S5-EQ-O1-01」；:141「reviewer pending: independent critic (gate 2) + CTO sanity (gate 3)」；:143「dsp-algorithm teammate (instance-2) @ claude-opus-4-8 / 2026-06-06」 |

### 1.4 knowledge_base（仓内）

| 日期 | path | 类型 | 一句话内容 | 状态(原文) |
|---|---|---|---|---|
| 2026-05-27（mtime 05-29） | knowledge_base/competitor/full_teardown_v2.md | 竞品拆机归档 | 竞品技术画像：主控 ADSP-21569KBCZ10、2 寸单元、16 元 d=55 mm L=825 mm、A/B 对称串联成 8 路、功放 ACM3128A×4、TDM、密闭箱、消声室 SPL 表、Sprint 3 仿真对照 | :3「文档编号：KB-COMP-001」；:4「版本：v2（Sprint 3 Phase 1-2 完成后归档）」；:5「日期：2026-05-27」；:6「维护：项目文档专家 Agent」；:177「本文件由项目文档专家 Agent 归档，v2，2026-05-27」 |
| 2026-05-30 | knowledge_base/competitor/SPL_anechoic_measurement_archived.md | 实测原件归档 | 「相控阵音柱」消声室 SPL 5 频×6 角表（1 m，启用算法）；CTO 确认=竞品 | :3「文档 ID：KB-SPL-001」；:4「归档日期：2026-05-30（C8/铁律六补归档…第 3 个 C8 gap finding）」；:10「Attribution 已确认 = 竞品（CTO 确认 2026-05-30）」 |
| 2026-09-02（来源件落盘 2026-07-31） | knowledge_base/competitor/KB-EXT-SPON-HIT9616A12_FIRMWARE_REG.md | 外部输入登记 | 竞品 SPON(世邦) HIT-9616A12 RK3308 整机固件包仅登记元数据；CTO 裁定不解包/不分析/不参考；C8 偏差与「熟悉阶段接触程度」逐条自述 | :1「KB-EXT-001：外部输入登记」；:4「CTO 裁定（2026-09-02）」；:59「C8 状态…来源已补、授权待确认」；:84「PM 登记，2026-09-02」 |
| 2026-06-01 | knowledge_base/ezkit/INDEX.md | 资料库索引 | EV-21569-EZKIT 物理板资料库索引：目录结构、已在手工具链、迁移源、上板路径 R1 关闭 | :3「文档 ID：KB-HW-EZKIT-001」；:4「建立日期：2026-06-01」；:15-16「vendor_docs/ … 待 CTO 拷入」（原文状态列带沙漏符号）；:47「PM 建库 2026-06-01。R1 命门 P0。资料待 CTO 拷入 vendor_docs/bsp。」 |
| 2026-06-01 | knowledge_base/ezkit/prep/PREP-DSP-migration.md | 上板准备简报 | tree_filterbank → 21569/CCES 迁移的现状盘点、关键技术点、待抽取清单、最短 cycle 实测路径 | :3「作者：dsp-algorithm teammate / 日期：2026-06-01」；:6 记忆冲突提示（memory.md §2.3 仍写 dual cores） |
| 2026-06-01 | knowledge_base/ezkit/prep/PREP-HW-bringup.md | 上板准备简报 | 上电前必查：ICE-1000/JTAG、boot mode、供电与跳线、上电顺序（资料未入库版，具体值标「待 vendor_docs 确认」） | :3「文档：PREP-HW-EZKIT-BRINGUP-01 / 作者：hardware-design teammate / 日期：2026-06-01」；:4「对象：CTO（物理板已在手）」 |
| 2026-06-01 | knowledge_base/ezkit/prep/PREP-TST-cyclecount.md | 上板准备简报 | cycle count 测量方法学、L1 判据（防 PF-1 复发）、待抽取清单 | :3「文档：PREP-TST-EZKIT-001 / 作者：testing teammate / 日期：2026-06-01」 |
| 2026-05-29（mtime 05-29） | knowledge_base/hardware_input/定向音柱AI数据_extracted.md | 硬件团队输入归档 | 硬件团队 6 项未知量(U1–U6)提取：模拟接口、16 元 A/B 串联 8 路、d=55、7.4Ω/3W、15Ω、ACM3128A、TDM、ADSP-21569KBCZ10、数模分地；5 项精度追问 | :3-8 frontmatter「doc_id: KB-HW-001 … status: 已归档 … date: 2026-05-29」；:22「文件磁盘 mtime 2026-05-27 19:56」；:23「项目正式收到时间：[pending — 待 CTO 确认]」 |
| 2026-05-30 | knowledge_base/hardware_input/定向音柱AI数据_含追问回复_extracted.md | 硬件团队输入归档 | KB-HW-002：取代/扩展 KB-HW-001，含表 8 追问回复 7 条（直流 Re=15Ω[L1]、额定功率 [L4]、盆口=物理尺寸、后腔无吸音棉→新增 R13） | :3「文档 ID：KB-HW-002（取代/扩展 KB-HW-001）」；:5「归档日期：2026-05-30（C8/铁律六 24h 内入库，gap-1 闭合）」 |
| 2026-06-05 | knowledge_base/hardware_input/KB-DRV-TEST-001_extracted.md | T/S 报告提取 | 拆机喇叭单元 LEAP-4 T/S 19 项 [L1/仪器] + LMS SPL 曲线形状；SPLo 82.161 dB 与铭牌 88 dB 冲突→DEC-S3-DSP-05 解锁；限幅/EQ 仍缺 Xmax/额定功率/R3 | :5「提取日期：2026-06-05（dsp-algorithm teammate 独立提取，iron-rule-7 三方核）」；:10-12「raw 入库 2026-06-01…C8 偏差留痕：raw 入库 2026-06-01 及时，但提取/分级/传播逾期至 2026-06-05（4 天）」；:131「critic R20 第三方独立读（待）」 |
| 2026-06-05 | knowledge_base/hardware_input/KB-DRV-TEST-001_PROPAGATION.md | 传播草案 | 铁律五全库传播计划（LIVE-1…6 改动块 + HISTORICAL 加注）与 decisions_log 行草案 | :1「KB-DRV-TEST-001 铁律五传播 + DEC 行 — DRAFT（不 commit；critic R20 门）」（但已在 3c4bf56 入库） |
| 2026-09-26/28（仓外） | /home/it1234/algorithm_speaker/knowledge_base/papers/2026-09_side30/README_论文索引.md | 文献检索索引 | 侧面抑制 20→30 dB 文献：3 路检索 agent，已下载 15 PDF+1 XML，12 篇付费墙未取；09-28 取得 Keele 2002 | :1「侧面抑制 20→30 dB 文献检索索引（2026-09-26）」；:4「只下载开放获取版本，未使用任何影子图书馆」；:44「2026-09-28 已取到副本（第三方网站 audioartistry.com，非开放获取…仅内部研读、勿转发）」 |
| 2026-05-26（仓外） | /home/it1234/algorithm_speaker/knowledge_base/measurements/competitor_anechoic.md | 竞品 SPL 记录 | 同一张竞品消声室 SPL 表 + 前后比，来源「Sprint 2 CTO 提供（竞品拆机 + 消声室实测）」 | :5「记录日期：2026-05-26」 |
| 2026-07（仓外） | /home/it1234/algorithm_speaker/ee-agent-team-starter/README.md | 治理提炼包 | 「从一个音频硬件研发多-Agent 项目提炼的框架 + 治理精华」，供新项目起 agent team | :41「生成：从 itc-enterprise-workflow 提炼，2026-07。memory 一律未随带（防跨项目污染）。」 |

### 1.5 references / tools（通用模板，无项目事实）

| 日期 | path | 类型 | 一句话内容 | 状态(原文) |
|---|---|---|---|---|
| 无文内日期（mtime 2026-05-24；git 06-09） | references/agent-directory.md | 模板 | Agent 目录：编排层/领域层/工具层/人类层、通信矩阵图、4 个强制门（Plan Approval/Architecture Review/Prototype Go-No-Go/Final Approval） | 无状态字段；:38「4 mandatory gates」 |
| 同上 | references/communication-protocol.md | 模板 | YAML 消息信封与消息类型、任务状态机、DAG 依赖类型、评审流程（最多 3 轮）、质量门 G0–G4 | 无状态字段；:229「Critic performs review (max 3 rounds)」；:246-252 Gate 表 |
| 文内无日期（mtime 05-24；memory 内示例 2024-01） | tools/cad-interface/{profile,soul,skill,memory}.md | Agent 四件套模板 | CAD 接口 Agent（JSON-RPC cad.open/query_geometry/export/version_*）；memory.md 为虚构示例（项目 SpeakerSystem_A300、日期 2024-01-08~15） | 各文件 :2-5 `version: "1.0.0"` `author: "ITC-Enterprise-Architecture-Team"`；memory.md:8-60 示例 |
| 同上 | tools/code-execution/{profile,soul,skill,memory}.md | 同上 | 代码执行沙箱 Agent（Python 3.11/MATLAB Runtime/GCC，Docker 沙箱，错误码 E1001…）；memory.md 为 2024-01 示例（:157-170） | 同上 |
| 同上 | tools/database/{profile,soul,skill,memory}.md | 同上 | 数据库 Agent（PostgreSQL schema、CRUD JSON-RPC、审计、备份）；memory.md 为 schema v1.0.0(2024-01-05)…v1.3.0(2024-01-14) 示例（:14-32） | 同上 |
| 同上 | tools/matlab/{profile,soul,skill,memory}.md | 同上 | MATLAB Agent（R2023b 工具箱、matlab.run、协作接口）；memory.md 为 2024-01 优化记录示例（:164-177） | 同上 |
| 同上 | tools/web-search/{profile,soul,skill,memory}.md | 同上 | 检索/可视化 Agent（Google/Scholar/USPTO/EPO/IEEE/arXiv/Semantic Scholar 为「Connected」的假设状态、缓存策略）；memory.md 为 bass reflex/ANC 热门查询与 2024-01 优化示例（:36-44,:125-138） | 同上；profile.md:78-86「API状态 Connected」是模板默认值，非实际配置 |

---

## 2. 时间线事件（按日期）

标记：[文内]=文件正文；[git]=commit 说明；[fs]=mtime/目录；[dec]=decisions_log 交叉核。

| 日期 | 出处 | 事件 |
|---|---|---|
| 2026-05-24 12:25–12:46 | [fs] tools/*/*.md、references/*.md 的 mtime | 通用多 Agent 方案包文件的原始修改时间（模板，非项目记录）；正文 front-matter `author: "ITC-Enterprise-Architecture-Team"`（如 tools/cad-interface/profile.md:5） |
| 2026-05-26 11:33:42 | [fs] tools/、references/、agents/ 目录 mtime；父目录名 `Kimi_Agent_多Agent协作方案` | 方案包被放入工作目录（推断；未见文字记录） |
| 2026-05-26 14:04–14:29 | [fs] ~/下载/相控阵音柱_声压级测试结果.pdf（14:04）；仓外 papers/ 第一批 5 个 PDF（14:19–14:29） | 竞品消声室 SPL 原件到手；论文库第一批（Dolph-Chebyshev×2、Boone 2009、差分扬声器阵列、Van Trees 2002） |
| 2026-05-26 15:02 / 15:14 | [fs] 仓内 knowledge_base/papers、measurements 两个空目录的 mtime=15:02；[文内] 仓外 measurements/competitor_anechoic.md:3-5（文件 mtime 15:14） | 「竞品定向音柱消声室实测数据」记录，来源「Sprint 2 CTO 提供（竞品拆机 + 消声室实测）」，记录日期 2026-05-26 |
| 2026-05-26 20:12 | [fs] 本机下载目录里的一个 agent 团队配置压缩包（公开版不写文件名，可能属于另一项目） | 仅见文件名；与本仓 agents 体系的关系文中无记载 |
| 2026-05-27 | [文内] knowledge_base/competitor/full_teardown_v2.md:4-6,177 | 竞品技术画像 KB-COMP-001 v2 归档（「Sprint 3 Phase 1-2 完成后归档」）；:48「T/S 参数 拆机单元送测中，预计 2–4 周回报」 |
| 2026-05-27 19:56 | [文内] knowledge_base/hardware_input/定向音柱AI数据_extracted.md:22 | 硬件团队 docx（定向音柱AI数据.docx）落盘时间（mtime） |
| 2026-05-29 | [文内] 定向音柱AI数据_extracted.md:3-8,21 | KB-HW-001 提取归档（提取 19:14）；:23 项目正式收到时间仍 pending；U1(模拟)/U3/U4/U5/U6 文档级闭环，5 项精度追问待回 |
| 2026-05-29 17:57 | [fs] knowledge_base/standards/JYT_directional_speaker.jpeg | JY/T「定向扩声系统」表 9/表 10 截图入库（需求指标来源之一） |
| 2026-05-29 15:43 | [fs] full_teardown_v2.md mtime | 文内含 F-AC-01 撤回加注（如 :135,:152,:156），说明 v2 在 05-27 之后被改过 |
| 2026-05-30 | [文内] 定向音柱AI数据_含追问回复_extracted.md:3-6,15-25 | KB-HW-002：硬件团队 2026-05-30 提供含追问回复版；Q-① 直流 Re=15Ω[L1]→「转接板 PO 签署条件满足」；Q-⑥ 后腔无吸音棉→新增 R13 |
| 2026-05-30 | [文内] SPL_anechoic_measurement_archived.md:4,10-14 | 竞品消声室 SPL 原件补归档（原件 mtime 05-26，补归档逾期，记为第 3 个 C8 gap）；CTO 确认 attribution=竞品；R3/PF-3 不解锁 |
| 2026-06-01 12:33–13:06 | [fs] ~/下载/adi-CrossCoreEmbeddedStudio-linux-x86-2.12.1.deb、最简单的CCES注册详解V2.0.pdf；/opt/analog/cces 目录 12:41 | CCES 2.12.1 Linux 安装包与注册指引到手并安装；INDEX.md:24-27 记「已在手的工具链资料」 |
| 2026-06-01 | [文内] knowledge_base/ezkit/INDEX.md:3-8；PREP-HW-bringup.md:4 | EZKIT 资料库建立；Sprint 3 R1「命门」P0（算力 [L2]→[L1]）；「物理板已在手」 |
| 2026-06-01 17:37–17:52 | [文内/fs] KB-DRV-TEST-001_extracted.md:9-12（raw 入库）；三份 PREP 简报 :3 | T/S 报告原图 raw 入库（MD5 同源核）；dsp/hardware/testing 三份上板准备简报生成 |
| 2026-06-01 18:40:45 | [fs] ezkit/bsp、ezkit/vendor_docs 大批文件 mtime | 厂商资料/BSP/例程/教程被拷入（INDEX.md:15-20 当时仍写「待 CTO 拷入」，之后未更新） |
| 2026-06-02 | [git] 4bf0f52（仓库首个 commit）；c12cca8「ADSP21569_LED 脚手架嫁接」 | git 历史自此开始；c12cca8 说明提到「ADSP21569_LED 脚手架嫁接 + 内存向量 harness」（同名例程见 vendor_docs/cces_examples/code/ADSP21569_LED；说明未写来源路径） |
| 2026-06-03 | [git] 7d24e6e、4801575、7563b3f | 归档 `adi_fir_legacy_2156x.h`（「CTO 提供」，=knowledge_base/ezkit/bsp/fira_headers）；bench_cyc_target 接真 CCNT；7563b3f 说明「R1 状态: L1 翻盘 (cyc_8ch=1006935…)」= 首批 [L1] 周期数（范围外 commit，仅作交叉） |
| 2026-06-05 | [文内] KB-DRV-TEST-001_extracted.md:5,10-12,79-86；[git] 3c4bf56、6d0a0af | T/S 提取归档（逾期 4 天，C8 偏差）；SPLo 82.161 dB[L1] 与铭牌 88 dB[L4] 冲突→DEC-S3-DSP-05 解锁；SPL 口径裁定 DEC-S5-SPL-CALIBER-01 |
| 2026-06-06 | [文内] M1_SYMBOL_PRESURVEY.md:3；M1_SYMBOL_SURVEY.md:3；EQ_INTEGRATION_NOTE.md:143；M1_FACT_BASE.md:5；M1_ARCH_INPUT_DATA.md:7；M1_ARCH_REVIEW_R34.md:5；M1_HWCONFIRM1_RX_SINGLE_SLOT.md:3；STAGE4_BRINGUP_CHECKLIST.md:3 | WO-S6-AUDIO（阶段 4 实时音频通路）M1 前期调研批：符号预调研、事实库 183 条（4 路并行+4 路对抗核验）、架构输入 14 条、critic R34 审总工四开口、RX 单 slot 可行性、O1 EQ 桌面交付、R24–R34 教训清单 |
| 2026-06-08 | [dec] decisions_log:727（DEC-S6-M1-ARCH-01 四开口定稿）；[文内] M1_HWCONFIRM1B…:3；M1_SRU_ROUTING_SURVEY.md:3 | CTO 拍 M1 架构（750 Hz/64、1→8、TX 4096 B、M1 不 pin）；RX 1-slot 硬件裁定→512 B；SRU 路由调研 |
| 2026-06-08 | [文内] M1_IOCALLBACK_L1_ADJUDICATION.md:3,20-21；[dec] decisions_log:728 | **M1 透传 loopback 板上 PASS [L1]**（五项读数；rx=5757）；io-callback 12839 cyc=9.629 MCPS 口径裁定（R42） |
| 2026-06-08 | [文内] M1_CCES_IMPORT_GUIDE.md:3-6；STAGE4_BRINGUP_CHECKLIST.md:28-31,104-109；[git] cf0c34d、2e505b6 | M1_Loopback 一键导入 CCES 工程；板机导入报 "project description file is corrupted"（根因：XML 注释含 `--`，疑似散文件传输截断）→hotfix，增 A6/E6/E7 |
| 2026-06-08 | [文内] M2_SURVEY.md:3,8；M2_BEAM_WEIGHTING_SURVEY.md:3；M2_Q_BOUNDARY_SURVEY.md:3；[git] 12a5920 | M2（FIRA 波束入环）三份调研；M2 broadside v1 实现落库（12a5920） |
| 2026-06-08 | [文内] M1_SOFTCFG_RC_ADJUDICATION.md:3-5；M1_SOFTCFG_ALL5_RC1_ADJUDICATION.md:3-6,8-15 | 板上读到 softcfg_rc=1，后重跑为 rc[0..4] 全=1；读安装版头（/opt/analog/cces/2.12.1）证 adi_twi_Write 阻塞、第 4 参 bRestart |
| 2026-06-09 | [文内] STAGE4_BATCH_PLAN.md:3-4；[git] caf6708、ec21908、b3d7f74、43aad40(10:34 +0800) | CTO 出门→非专家代测的批量包与 runbook；U6 地址自探测；仓库一次性入库 tools/、references/、agents/、sprint2/3 等 |
| 2026-06-10 | [文内] M1_SOFTCFG_U6_NACK_ROOTCAUSE.md:10-16；[dec] decisions_log:1011 | R51/R52 修订（hwerr=枚举序数非位掩码）；团队模型 re-tier（lead→claude-fable-5[1m]；critic/dsp→claude-fable-5） |
| 2026-06-11 | [文内] M1_SOFTCFG_BOARD_RESCOPE.md:1-12,44-54；[dec] decisions_log:1012 | **板身份坐实**：第三方 AD-EXKIT V2.1 + ADSP-21569-SOM REV 1.1（非官方 EV-SOMCRR-EZKIT）；codec 复位硬连线；DEC-S6-FSRU1-RESCOPE-01；override build 取消 |
| 2026-06-12 | [文内] STAGE4_TESTER_RUNBOOK.md:21-34；[git] 28ad3a3 | R57 深审沉淀（「代码 ready 文档不 ready」）：本次板测执行单 4 步 + JTAG 纪律（Suspend→Resume 后音频不可信） |
| 2026-06-16 | [文内] M2_Q_BOUNDARY_SURVEY.md:152-165；STAGE4_BATCH_PLAN.md:44；BOARD_TEST_INSTRUCTIONS.md:1；[dec] decisions_log:1013,1014 | 板测：SPORT 字对齐=左对齐（0xFABBED00 等 8 值低字节全 0；max_abs=0x42C92C00）→DEC-S6-ALIGN-LEFT-01；**M2 FIRA 波束上板 PASS [L1]**（DEC-S6-M2-BOARD-PASS-01，「阶段4 软件部分实质收口」）；测试员板测说明快照 |
| 2026-06-17 | [文内] STAGE4_ALGORITHM_VALIDATION_TEST.md:224 | 整机算法有效性验证测试文档 v1（CTO 已接好真功放 + 16 元阵列）；critic R61 PASS |
| 2026-06-25 | [git] 8e419f4 | 上条文档才首次入库（比文内日期晚 8 天） |
| 2026-06-29 | [文内] STAGE4_ALGORITHM_VALIDATION_TEST.md:69-72,81,113-116；[dec] decisions_log:1016,1018 | 首次真阵列现场测（室外空旷地）：16 单元 108.7~111.9 dB 零哑路；原「全阵齐放近场贴近测」法与「1 m+单音+手持」指向性法被证无效并退役（DEC-S6-TEST1/TEST3-METHOD-01） |
| 2026-07-02/07-07 | [git] 4bf18b6、02bc474；[文内] DEPRECATED_LOOSE_COPIES.md:5 | M2_STATIC_TXTEST 静态缓冲差分诊断、375 Hz 声学极性测试；M2_CHMAP_FIX / M2_STXT_LOCALIZE 宏进 m1_loopback_tdm.c（权威版 897 行，2026-07-07） |
| 2026-07-08 | [文内] STAGE4_ALGORITHM_VALIDATION_TEST.md:67；[dec] decisions_log:1020；[git] 4f87150 | 「波束平」根因闭合：物理 C2/C4 两对喇叭反极性（竞品喇叭接到我方功放时接混）；板/算法平反（限本 rig）；原「极性确认对」措辞撤回 |
| 2026-07-17–22 | [fs][仓外] ee-agent-team-starter 目录；[文内] README.md:41 | 从本项目提炼的 EE agent team 起步包（「2026-07」） |
| 2026-07-19/20 | [dec] decisions_log:1021 起（SLIM-01…07） | 治理减法（CLAUDE.md 分层、skill 去重等；本范围文件未涉及） |
| 2026-07-31 14:59 | [文内] KB-EXT-SPON-HIT9616A12_FIRMWARE_REG.md:15 | 竞品 SPON HIT-9616A12 固件 zip 落盘时间（mtime，C8 的「代理」时间） |
| 2026-08-20 13:33 | [fs] /opt/analog/cces/2.12.1 及 cc21k 的 mtime | 本机 CCES 2.12.1 中 SHARC 工具链（cc21k、SHARC/include）的修改时间；06-08 的文档称本机无 CCES/无 SHARC 头（见疑点 14） |
| 2026-09-02 | [文内] KB-EXT…:4,59,84；DEPRECATED_LOOSE_COPIES.md:1,11；m1_project/DEPRECATED.md:1；M1_PROJECT_README.md:1；[dec] decisions_log:1030-1032 | Sprint 7 范围裁定（算法层升级；硬件仍 AD-EXKIT V2.1，Stage 5 无进展，线③无回函，R3 无排期，7-22 后无正式测试）；竞品固件包登记；sprint6 旧副本只加过期标注 |
| 2026-09-26 | [文内][仓外] README_论文索引.md:1,4；[git] 7686c05 | 侧面 20→30 dB 文献检索（3 路检索 agent、开放获取）；M2_WTBL_SEL 运行时加权表固件第一步 |
| 2026-09-28 | [文内][仓外] README_论文索引.md:44 | 取得 Keele 2002 直线阵 CBT 副本（第三方站点，非开放获取，仅内部研读） |

---

## 3. 前期环节线索（有记录 + 出处 / 未见）

### 3.1 需求指标 / PRD

有记录：
- **标准截图**：`knowledge_base/standards/JYT_directional_speaker.jpeg`（mtime 2026-05-29 17:57，untracked）= JY/T XXXX—XXXX「定向扩声系统」6.3.1.1 指向性按 3 m 处远场声压级差限定；表 9 水平指向（例：1000 Hz 一级 30°≥18/90°≥20/180°≥20 dB；2000 Hz 一级 ≥20/≥25/≥20；500 Hz 一级 ≥5/≥10/≥12；4000 Hz 一级 ≥22/≥10/≥20）；垂直面 30° @1000 Hz ≥12 dB；表 10 空场应备声压级 ≤75 dB(A)、STIPA ≥0.50（图像直读，标准号空白）。引用处：SPL_anechoic_measurement_archived.md:44「标准 JY/T 表9：本表是 SPL（无 BW）——禁从此 SPL 反推 BW」。
- **PRD 引用（正文不在本范围）**：M1_ARCH_REVIEW_R34.md:7（嵌在 JSON 行内）引「PRD:81 目标场景 博物馆讲解/车站广播/商场分区——全 mono 语音/广播」、DOC-S4-IO-01:27/30「用 1ch」；KB-DRV-TEST-001_PROPAGATION.md:107-111 引 `sprint2/docs/prd_update.md:168`「空场最大声压级 ≤ 75dB(A)」（与 JY/T 表 10 一致）；STAGE4_BATCH_PLAN.md:29、STAGE4_ALGORITHM_VALIDATION_TEST.md:19-21,177 提「≥90dB 对外承诺」待 R3（「PRD:183」字面只出现在 commit 6d0a0af 的说明里）；M2_BEAM_WEIGHTING_SURVEY.md:67,118 提「PRD net-isolation acceptance "X dB @ anechoic L1" is an OPEN ITEM (X TBD by CTO/PRD, DEC-S5-V1-SCOPE-01)」；EQ_INTEGRATION_NOTE.md:12,54,135 引 EQ_PRD。
- **整机验证门**：STAGE4_ALGORITHM_VALIDATION_TEST.md:134-139：0° 最大；±90° 相对 0° 落差 ≥12 dB（「保守门；理论旁瓣 −20dB，留反射裕度」）；±30°/±60°/±90° 左右差 ≤6 dB。
- **指向性频段需求**：[仓外] competitor_anechoic.md:22「与 CTO 决策『≥1 kHz 才要求强指向』一致（见 MEMORY: directivity-band-requirement）」；full_teardown_v2.md:134「低频不要求指向性（DEC-S1-002）」。
- **硬件团队输入（6 项未知量，WO-S3-001）**：KB-HW-001/002（见 3.2）。

未见：PRD 本体、客户场景需求原始文档、指标签字记录（本范围只见引用，PRD 在 `sprint2/docs/` 范围外）。

### 3.2 竞品样机拆机

有记录：
- **拆机归档 KB-COMP-001 v2（2026-05-27）**：full_teardown_v2.md:23-33 主控 ADSP-21569KBCZ10（拆机 IC 丝印）；:58-73 阵列 16 元、d=55 mm、孔径 825 mm（(N-1)d）、箱体 880 mm、A/B 对称串联成 8 路、仅 broadside；:77-88 功放 ACM3128A×4（8 通道）；:92-103 TDM（精确时序 [待核实 U4]；主控→功放接口 [待核实 U1]）；:107-114 全密闭箱、后腔连通；:118-135 消声室 SPL 表；:11-19 法律状态声明（仅内部研发参考；不含竞品 PCB/外壳/固件复制）。拆机工单：:167 指向 `sprint2/docs/sprint3_teardown_workorder.md`（WO-S3-001，范围外未读）。
- **硬件团队拆机/测量输入**：KB-HW-001（docx mtime 05-27 19:56，05-29 归档）定向音柱AI数据_extracted.md:34-63；KB-HW-002（05-30）含追问回复_extracted.md:15-25（直流 Re 15Ω[L1]；额定功率/阻抗 [L4]；盆口为物理尺寸非 Sd；后腔无吸音棉→R13）。
- **拆机喇叭单元送测**：full_teardown_v2.md:48「拆机单元送测中，预计 2–4 周回报」(05-27) → KB-DRV-TEST-001：raw 2026-06-01、提取 2026-06-05（KB-DRV-TEST-001_extracted.md:5,10-12），LEAP-4 T/S 19 项 [L1/仪器]（:23-43）；Revc 7.600 Ω 与 DC 7.4 Ω 双轨（:88-92）。
- **竞品消声室 SPL 实测**：SPL_anechoic_measurement_archived.md:28-37（原件 `相控阵音柱_声压级测试结果.pdf` mtime 05-26，:4；CTO 05-30 确认=竞品，:10-14）；仓外 competitor_anechoic.md:3-5「来源：Sprint 2 CTO 提供（竞品拆机+消声室实测）」。
- **竞品固件包（SPON HIT-9616A12，RK3308）**：KB-EXT…:12-24（CTO 2026-09-02 裁定不解包/不分析/不参考；来源「同事从竞品原厂（SPON）处获得」，渠道/授权未确认，:23,:56-59）。
- **竞品喇叭在自家 rig 上使用**：STAGE4_ALGORITHM_VALIDATION_TEST.md:67「在竞品喇叭 rig 上即用成对法查出 C2/C4 两对反极性」。
- 法律边界（DEC-S3-003）：full_teardown_v2.md:11-19；KB-EXT…:51。

未见：拆机日期/操作人/照片序列、竞品整机购买记录与价格、竞品品牌/型号名（full_teardown_v2.md 全文未写；KB-EXT 的 SPON HIT-9616A12 平台是 RK3308，文中说「与本项目 ADSP-21569 SHARC+ 平台无关」(:21)，**未说明它与被拆竞品是不是同一型号**）。

### 3.3 方案 / 芯片选型

有记录：
- **主控**：竞品用 ADSP-21569KBCZ10（full_teardown_v2.md:27）；KB-HW-001:57-58「型号 ADSP-21569KBCZ10…与芯片选型 ADSP-21569（DEC-S1-004，采购冻结 DEC-S3-PROC-01 待 EZKIT）一致」；INDEX.md:5「DEC-S3-PROC-01 LOCKED 主控、量产采购冻结待本板实测」、:7「R1 命门（算力裕量曾是纸面值，PF-1，纸面 27×/49× … 桌面树形 C 实算修正 17×(16ch)/33×(8ch)[L2]）」、:43「R1 关闭 + 21565 vs 21569 量产选型拍板（不可逆采购解冻条件）」。
- **阵列几何/拓扑**：full_teardown_v2.md:58-73 与 KB-HW-001:38-42（DEC-S3-GEOM-01 统一基线 N=16/d=55/L=825；8 路对称 broadside，DEC-S3-DSP-03）；转向不可达：M2_BEAM_WEIGHTING_SURVEY.md:63,123。
- **功放/接口**：ACM3128A（full_teardown_v2.md:77-88）；接口=模拟（KB-HW-001:34-37 U1 闭环）——但 full_teardown_v2.md:100 仍写 [待核实 U1]（见疑点 7）。
- **编解码/ADC/DAC**：板上为 ADAU1979(ADC)+ADAU1962A(DAC)（M1_SYMBOL_SURVEY.md:24-67；_m1_facts_S3 全文）；TDM8×32 bit@48k=12.288 MHz（M1_FACT_BASE.md:278-279）。
- **算法路线（sprint6 内）**：M1 架构四开口（M1_ARCH_REVIEW_R34.md:7 总表；decisions_log:727 定稿）；M2 加权落级推荐「both」（M2_BEAM_WEIGHTING_SURVEY.md:46-72，「recommendation != ruling」；CTO 裁定不在该文件）；FIRA 采用 Legacy API（[git] 7d24e6e「Legacy推荐(纠正ACM倾向)」）；O1 EQ+限幅结构（EQ_INTEGRATION_NOTE.md:12-35）。
- **开发框架/工具链**：CCES 2.12.1（INDEX.md:25-27,38；M1_CCES_IMPORT_GUIDE.md:13「THIN standalone CCES SHARC project」）；SigmaStudio 图形化教程只作为厂商资料存在（`ezkit/vendor_docs/tutorials/` 5–17 号 PDF、`sigma_examples/`），项目走手写 C（M1_PROJECT_README.md:5-7「route B」）。

未见：选型对比表（21565 vs 21569、DSP vs 其它平台）正文；DEC-S1-004 原文；最终 21565/21569 裁定（本范围只见「待拍板」INDEX.md:43）。

### 3.4 开发板 / EZKIT 采购与到货

有记录：
- **时点**：INDEX.md:3-5 建库 2026-06-01，「板卡：EV-21569-EZKIT」；PREP-HW-bringup.md:3-4「日期 2026-06-01；对象：CTO（物理板已在手）」→ **最迟 2026-06-01 板已在手**。同日 12:33/13:06 CCES 2.12.1 .deb 与注册指引到手（[fs]，INDEX.md:25-27）；18:40 厂商资料/BSP/例程批量拷入（[fs]）。06-02 commit c12cca8 提到「ADSP21569_LED 脚手架嫁接」（同名例程在 vendor_docs/cces_examples）；06-03 commit 7563b3f 出现首批 [L1] 周期数（cyc_8ch=1006935）。（后两项为范围外 commit 说明，仅作交叉。）
- **板的真实身份**：厂商教程《ADSP-21569-EVB 开发板使用说明文档（一）初始状态说明》（`ezkit/vendor_docs/tutorials/1. …pdf`，pdftotext 首页：「2023-5-29 北京」「核心板+底板」「完全照着 ADI 原厂的开发板硬件设计来 1 比 1 做的」「核心板参考 EV-21569-SOM，底板参考 EV-SOMCRR-EZKIT」）；《0. 硬件更新说明》（PDF CreationDate 2023-12-04）写第一版无 USBi 接口、新版加电源开关；`schematics/` 含 V1.0/V1.2/V2.1 三版底板。**2026-06-11 经板测 1A 读数+原理图亲读坐实**：物理板 = 第三方 AD-EXKIT V2.1 底板 + ADSP-21569-SOM REV 1.1（OpenADSP 生态），不是官方 EV-SOMCRR-EZKIT（M1_SOFTCFG_BOARD_RESCOPE.md:9-12）；图纸 Revision 栏空白，「V2.1」仅为文件名/目录级关联，换板时按 BENCH_OPS_CARD 三特征（电源开关/转接卡/双 A2B）肉眼比对（:53-54；BENCH_OPS_CARD 在 `sprint3/audit/BENCH_OPS_CARD.md`，范围外）。
- **资料入库状态**：INDEX.md:15-20 写 vendor_docs「ADI 官方 21 份 PDF」「待 CTO 拷入」；实际磁盘 vendor_docs 为卖家教程/原理图/例程（994 文件），ADI 官方 datasheet/HRM/EE-notes/设计库在 `bsp/`（282 文件）（见疑点 3）。
- **上板里程碑**：M1 透传板上 PASS 2026-06-08（M1_IOCALLBACK_L1_ADJUDICATION.md:3；decisions_log:728）；M2 板上 PASS 2026-06-16（decisions_log:1014）。
- **整机硬件**：STAGE4_ALGORITHM_VALIDATION_TEST.md:3-4,34-38：AD-EXKIT V2.1+21569-SOM → DAC → 4 片功放(8 路, ACM3128A 等效) → 16 元阵列(d=55,L=825)；[git] 8e419f4「CTO 接好真功放+16元阵列」。Stage 5（转接板/功放/电源/装配）= 「采购+物理装配，外部串行」（STAGE4_BATCH_PLAN.md:28）；「本测试仅整机验证，无采购/PO 动作」（STAGE4_ALGORITHM_VALIDATION_TEST.md:215）；DEC-S7-SCOPE-01（decisions_log:1030）「Stage 5 无进展，线③厂家函无回函」。
- **转接板 PO 闸门**：KB-HW-002:19,:34「Q-① 直流 Re 真值→转接板 PO 签署条件满足」。

未见：开发板/EZKIT 的采购订单、发货/到货日期、价格、渠道（本范围无任何此类文字）；是否曾买过官方 EV-21569-EZKIT（文中未见；已知物理板为第三方）。

### 3.5 GitHub / 论文调研、框架选择、资料入库

有记录：
- **论文库**：仓内 `knowledge_base/papers/` **为空**（0 文件，目录 mtime 05-26 15:02）。真正的论文库在 **仓外** `/home/it1234/algorithm_speaker/knowledge_base/papers/`：第一批 5 个 PDF（05-26 14:19–14:29：Dolph 1946 电流分布、Dolph-Chebyshev 权函数性质、Boone 2009、差分扬声器阵列设计、Van Trees 2002）；第二批 `2026-09_side30/`（09-26 17:24；A 声区 4、B 音柱实践 8、C 稳健/校准 3+XML、D CBT 1(09-28)）及 README_论文索引.md（来源：3 路检索 agent，只下开放获取，:4；外部数字非 L1，进 decisions_log 按铁律六 24h，:5；列出 12 篇付费墙未取，:35-53；:55-58 点名本地已有 Van Trees/Boone/Dolph/Ward/Zhang-Xiang-Zhu 2024）。README:44 指向 `sprint7/docs/S7_SIDE30_ALT_ALGOS.md §4`（范围外）。
- **GitHub**：**未见**（范围内所有 .md 对 github/gitee/arxiv/开源 的搜索：仅 tools/web-search 模板里的 arXiv 条目与 README 的 "开源" 字样，均非调研记录）。
- **官方代码/资料来源**：`install_notes/` 两个 txt 给出 ADI 官方下载链接（EV-2156x EZ-KIT Rel1.0.1 补丁包；CCES 2.11.1，「2023年4月最新」）；EE-408 FIR/IIR 加速器示例代码（`bsp/app_notes/fira_accel_code/EE408V02/README.txt`：「Date Created: August 19, 2019」）；FIRA 头文件 `adi_fir_legacy_2156x.h` 由 CTO 提供（[git] 7d24e6e）。
- **资料入库流程（C8/铁律六 24h）及延迟记录**：KB-HW-001 磁盘已存 2 天才归档、项目接收时间 pending（定向音柱AI数据_extracted.md:22-23）；KB-SPL-001 原件 05-26→05-30 补归档（SPL_anechoic…:4）；KB-DRV-TEST-001 raw 06-01 及时、提取逾期 4 天（_extracted.md:10-12）；KB-EXT 落盘 07-31→登记 09-02，逾期 33 天为下界（KB-EXT…:57-59）。
- **框架选择**：见 3.3「开发框架/工具链」；声学/DSP 工具链选择（pyroomacoustics/MATLAB 等）写在 CLAUDE.md，不在本范围。

未见：GitHub 项目调研、开源波束成形库对比、论文调研的第一批检索记录（第一批 5 篇只有文件无检索说明）。

### 3.6 团队 / 治理搭建

有记录：
- **通用方案包**：references/ 与 tools/ 22 个 .md 全为 Kimi 方案包模板（author "ITC-Enterprise-Architecture-Team"，version 1.0.0；mtime 05-24；memory 内为 2024-01 虚构示例）；references/agent-directory.md:5-38 定义编排层(PM, Critic)/领域层/工具层/人类层；references/communication-protocol.md:244-252 质量门 G0–G4。**这些文件不含任何 ADSP/定向音柱事实**。
- **项目化治理在 sprint6 中的体现**：critic 轮次 R24–R61 与「三道关（POLICY v1.8 §4B）」（M2_SURVEY.md:358；EQ_INTEGRATION_NOTE.md:141；STAGE4_BRINGUP_CHECKLIST.md:3）；C8/C9/C10 与 L 分级标签贯穿各文；角色：dsp-algorithm teammate（M1_SYMBOL_PRESURVEY.md:3）、critic、PM lead（STAGE4_BATCH_PLAN.md:7）、非专家测试员→CTO 中转→PM（STAGE4_TESTER_RUNBOOK.md:153-159）、「claude.ai 总工」（M1_ARCH_REVIEW_R34.md:1,7）；CTO_OK hook（DEPRECATED_LOOSE_COPIES.md:11）。
- **模型标签时间轴**：claude-opus-4-8（06-06~06-08 各 reviewer 行）→ 2026-06-10 re-tier 到 claude-fable-5（decisions_log:1011）→ claude-fable-5[1m]（BOARD_RESCOPE.md:5，06-11）→ 06-17 R61 仍写 claude-opus-4-8[1m]（STAGE4_ALGORITHM_VALIDATION_TEST.md:224）；M2_Q_BOUNDARY_SURVEY.md:165「R59 ran on Opus=Fable-529-fallback」。
- **仓外线索**：`ee-agent-team-starter/`（2026-07，从本项目提炼）；本机下载目录里的一个 agent 团队配置压缩包（2026-05-26 20:12；公开版不写文件名，可能属于另一项目）——仅文件名，与本仓关系文中无记载。

未见：团队何时/如何启动的决策记录（本范围最早只有 05-24/05-26 的文件 mtime 与 06-09 入库）；「Gate 1/Gate 2」签字记录（full_teardown_v2.md:157 只提「Gate 1 指标」）。

---

## 4. 阶段边界线索（日期 + 出处）

| 日期 | 出处 | 边界线索 |
|---|---|---|
| 2026-05-27 | full_teardown_v2.md:4 | 「Sprint 3 Phase 1-2 完成后归档」；:157「Gate 1 指标 BW@2kHz ≤30° 已超标」 |
| 2026-06-01 | INDEX.md:4-8；PREP-DSP-migration.md:4；PREP-HW-bringup.md:4 | Sprint 3「R1 命门 P0」= 把算力 [L2] 变板上 [L1]；板已在手、资料库建立；INDEX.md:37-43 给出 R1 关闭路径（0 CCES→1 入库→2 bring-up→3 工程→4 板上 cycle→5 R1 关闭+选型） |
| 2026-06-02 | [git] 4bf0f52（首 commit） | git 历史/FIRA 集成（DOC-S4-…）起点；本范围文件里「sprint4」「sprint5」作为路径被引用（M2_SURVEY.md:19-24；M1_IOCALLBACK…:48-49） |
| 2026-06-06 | M1_SYMBOL_PRESURVEY.md:3；STAGE4_BRINGUP_CHECKLIST.md:1-4 | **阶段 4（实时音频通路）/ WO-S6-AUDIO 启动**（sprint6=Stage 4）；Sprint 5 算力线 T2 保守闭合后（STAGE4_BRINGUP_CHECKLIST.md:49-68 的 C 节引 R27，:62-64 引 DEC-S5-T2-CLOSURE-01） |
| 2026-06-08 | M1_IOCALLBACK…:3；STAGE4_BATCH_PLAN.md:11 | M1 透传板上 PASS（阶段 4 第一里程碑） |
| 2026-06-11 | M1_SOFTCFG_BOARD_RESCOPE.md:1-12 | softcfg 命脉线收口；板身份确认 |
| 2026-06-16 | M2_Q_BOUNDARY_SURVEY.md:152-165；STAGE4_BATCH_PLAN.md:44；decisions_log:1014 | M2 板上 PASS=「阶段4 软件部分实质收口」 |
| 2026-06-17 | STAGE4_ALGORITHM_VALIDATION_TEST.md:3-6 | 「阶段④ 软件收口后、阶段⑤ 自研 PCB 之前的整机算法验证；第一次用真功放+真阵列听到算法效果」 |
| 阶段 5/6/7（未来项） | STAGE4_BATCH_PLAN.md:28-30 | Stage 5 硬件（转接板/功放/电源/装配）、Stage 6 R3 消声室、Stage 7 产品化，均「不可」纳入远程软件测试 |
| 2026-06-29 | STAGE4_ALGORITHM_VALIDATION_TEST.md:69-72,81,113 | 首次真阵列现场测与方法订正 |
| 2026-07-08 | STAGE4_ALGORITHM_VALIDATION_TEST.md:67 | 波束「平」根因（极性）闭合 |
| 2026-07-22 之后 | decisions_log:1030-1031（范围外交叉） | 「7-22 后无正式测试」 |
| 2026-09-02 | KB-EXT…:24,81；DEPRECATED_LOOSE_COPIES.md:1；decisions_log:1030 | Sprint 7：本轮=算法层升级、产品层功能不做；sprint6 旧副本过期整理 |
| 2026-09-26/28 | README_论文索引.md:1,44 | Sprint 7「侧面 30 dB」文献检索与 CBT 取证 |

---

## 5. 疑点（只列证据，不下结论）

1. **板卡命名冲突**。INDEX.md:4-5 称「EV-21569-EZKIT」；06-08 的文档按官方载板写：M1_CCES_IMPORT_GUIDE.md:13「ADSP-21569, EV-SOMCRR-EZKIT」、M1_SRU_ROUTING_SURVEY.md:72「The SOMCRR/EZKIT carrier gates the codecs behind a U6 I/O-expander…0x22」、M1_PROJECT_README.md:52「SOMCRR carrier schematic」；06-11 才确认为第三方 AD-EXKIT V2.1 + SOM REV 1.1（M1_SOFTCFG_BOARD_RESCOPE.md:9-12）；且「V2.1」仅文件名级关联（:53-54）。STAGE4_ALGORITHM_VALIDATION_TEST.md:3,34 已写 AD-EXKIT。后续文档里的「[L1/EZKIT]」标签应理解为「这块板」，不等于官方 EZKIT。
2. **采购/到货无文字记录**：范围内无采购单/到货日/渠道/价格；最早间接证据 = 2026-06-01 两处「板已在手」（INDEX.md:3-5；PREP-HW-bringup.md:4）。
3. **INDEX.md 目录语义与磁盘不符**：INDEX.md:15-16 写 `vendor_docs/` =「ADI 官方 21 份 PDF」、`bsp/` = ADI SDK，状态「待 CTO 拷入」从未更新；磁盘上 `vendor_docs/`（994 文件）是卖家教程/原理图/例程，ADI 官方 datasheet/HRM/EE-notes/设计库在 `bsp/`（282 文件）；`raw/` 为空。
4. **论文库在仓外**：仓内 `knowledge_base/papers/`、`measurements/` 为空；真正的库在 `/home/it1234/algorithm_speaker/knowledge_base/papers/`（不在任何 git 仓）。README_论文索引.md:26 提到 `_txt/` 文本提取目录，磁盘上不存在；:44 的 Keele 副本来自第三方站点（非开放获取，AES 版权）。
5. **传播改动块未落到 KB 文档**。KB-DRV-TEST-001_PROPAGATION.md:46-64（LIVE-1：full_teardown_v2.md:48-49）、:75-85（LIVE-3：含追问回复_extracted.md:20,27,31）、:87-96（LIVE-4：定向音柱AI数据_extracted.md:78）要求改的位置，磁盘上均未改（四个 KB 文档对 "KB-DRV-TEST-001" 的匹配数为 0；full_teardown_v2.md:48-49 仍写「送测中/Re 估算 7.0Ω」；hardware_input 两文件自 3c4bf56 起无后续提交）。而 3c4bf56 说明写「6 处 LIVE 翻」——可能指别处，这四个文件无法佐证。另该 PROPAGATION 文件自题「DRAFT（不 commit；critic R20 门）」(:1) 却已入库。
6. **核心 KB 文档多数不在版本控制中**：`.gitignore:2` 自 43aad40（2026-06-09）起忽略 `knowledge_base/`，仓内 11 个 md 中 7 个 untracked（full_teardown_v2、SPL_anechoic_measurement_archived、INDEX、3 份 PREP…），只剩 mtime 可作时间证据，改动不可审计；其中 full_teardown_v2.md 的 mtime（05-29 15:43）晚于其文内日期（05-27）。KB-EXT 登记文件靠 `git add -f` 才入库（KB-EXT…:6）。
7. **KB 内部状态陈旧**：KB-DRV-TEST-001_extracted.md:131「critic R20 第三方独立读（待）」，而 commit 3c4bf56 说明称 critic R20 第三读 19/19 完成；:28-29/:45-52 仍称单位前缀待核，但 :36 已写「Mms 前缀=milli 已由 Fs 自洽坐实」。full_teardown_v2.md:100 仍写 [待核实 U1]，而 KB-HW-001:34-37 已闭环 U1=模拟 [L1]（05-29）；:97-99 的 U4 TDM 精确时序仍开放。
8. **SPL_anechoic_measurement_archived.md 并存两层口径**：:10-14（CTO 已确认=竞品）与 :16-24（旧「待确认」记录，含「处置红线」）同时保留，需按 :10-14 读。
9. **in-file 评审状态普遍未更新**：M2_SURVEY.md:358、M2_BEAM_WEIGHTING_SURVEY.md:168、M2_Q_BOUNDARY_SURVEY.md:316、EQ_INTEGRATION_NOTE.md:141、M1_HWCONFIRM1(B):117/138 仍写「reviewer/critic gate pending」，而对应 commit 说明记录了 R29/R35/R36/R43/R45/R46 的过门结论。权威 verdict 应取 commit 说明/decisions_log，不是文件内页脚。
10. **M1_ARCH_REVIEW_R34.md 完整性**：:7 一行内含转义的正文，其后夹带一段 JSONL 原始记录（requestId、sessionId d706e3ea…、timestamp 2026-06-06T11:31:33.763Z、usage 字段），markdown 渲染错乱；正文内容靠 `\n` 转义恢复。
11. **STAGE4_ALGORITHM_VALIDATION_TEST.md**：文内日期 06-17，入库 06-25；:67 横幅称「极性确认对」措辞撤回，但 :81、:102、:169 仍写「接线顺序/极性确认对」（文内撤回传播不完整）；:113 的 TEST3 订正标「待 critic + CTO」。
12. **STAGE4_BATCH_PLAN.md 页脚陈旧**：:98「批量包实现待 dsp+critic 门」与正文 R55/R57 状态不符；STAGE4_TESTER_RUNBOOK.md 内多处「存史」节（:163-167,:197）只能按 R55 终局横幅（:13-19）读。
13. **softcfg 诊断链两份文档缺 R55 横幅**：M1_SOFTCFG_BOARD_RESCOPE.md:60-65 的 C7 传播清单列了 RUNBOOK、BATCH_PLAN、ADDR_SWEEP、NACK_ROOTCAUSE、memory、decisions_log，**未列** M1_SOFTCFG_RC_ADJUDICATION.md 与 M1_SOFTCFG_ALL5_RC1_ADJUDICATION.md；这两份仍按「F-SRU-1 NOT CONFIRMED / 未生效 / swap-silence 必须修」措辞（RC_ADJ:79-81；ALL5:66-69,:80-81），文内无「已被 R55 取代」提示。（BOARD_RESCOPE.md:65 写明 decisions_log 的 R48/R44 行「存史不动」，可能是有意不改；但这两个文件本身没有存史标注，单独读到会误当现行结论。）
14. **本机 CCES 状态前后不一**：M1_CCES_IMPORT_GUIDE.md:6（06-08）「this machine has NO CCES… gcc -fsyntax-only」；M1_SOFTCFG_ALL5_RC1_ADJUDICATION.md:8-15（同日）读到 /opt/analog/cces/2.12.1/ARM/… 的头文件，并称 SHARC 工具链副本「not installed here」；现 /opt/analog/cces/2.12.1 下有 SHARC/、cc21k（mtime 2026-08-20 13:33，安装时间无文字记录）。
15. **git 首提日期不能当撰写日期**：M1_SYMBOL_PRESURVEY.md（06-06 → 06-09 入库）；tools/、references/（mtime 05-24 → 06-09 入库）；STAGE4_ALGORITHM_VALIDATION_TEST.md（06-17 → 06-25）。
16. **竞品固件与拆机竞品是否同一产品未说明**（见 3.2）；KB-EXT…:23,56-59 来源渠道与授权「未确认」；:62-77 记录了裁定前对 .bin 做过 payload 级哈希、全文件 strings 与头部区解混淆。KB 登记文件自身位于被 .gitignore 忽略的目录，靠 `git add -f` 跟踪（:6）。
17. **tools/*/memory.md 内含虚构示例数据**（2024-01 日期、SpeakerSystem_A300 等，见 1.5）；web-search/profile.md:78-86 的「Connected」状态是模板默认值，不是实际接入。读者若按历史记录引用会误判。
18. **runbook 内嵌联系邮箱**：BOARD_TEST_INSTRUCTIONS.md:83、STAGE4_TESTER_RUNBOOK.md:157 写了 CTO 的中转邮箱（公开版不复写地址；仅记录文中所写，未核验是否仍有效）。
19. **R 编号口径**：M1_SOFTCFG_BOARD_RESCOPE.md:5 自述「该 critic 报告自题 R52 = 团队序号 R54，发现 ID F52-* 同轮」；M2_Q_BOUNDARY_SURVEY.md:165 注「R59 ran on Opus=Fable-529-fallback」——引用 R 号时以 commit 说明为准。
20. **M2_SURVEY.md:16-18** 仍把松散 `m1_loopback_tdm.{c,h}` 与 `m1_project/…/m1_app.ldf` 当接入点；DEPRECATED_LOOSE_COPIES.md:15 已承认路径过期、「存史不改」。
21. **PREP-DSP-migration.md:6 提出的记忆冲突无处理记录**：该简报称 `agents/dsp-algorithm/memory.md §2.3` 仍写 ADSP-21569「dual SHARC+ cores / 原生浮点」，与 INDEX.md/DEC-S3-PROC-01 的「单核 1GHz + 定点」矛盾，建议打废止 banner；本范围内未见该建议的落实或否决记录（agents/ 不在本范围，未核）。
22. **tools/ 与 references/ 的 22 个文件只是通用模板**：不含任何 ADSP/定向音柱事实；其 `author`/`version` 字段与 2024-01 示例数据易被误当项目历史（见 1.5）。手册若引用「团队搭建」应以 sprint6 内的实际角色/门（critic R 号、三道关、C8/C9/C10）为准，而非 references/ 里的 G0–G4 与 YAML 消息协议——后者在 sprint6 与 knowledge_base 的 md 中 grep 零命中（communication-protocol、agent-directory、references/、tools/*、JSON-RPC、YAML 均无）；sprint6 里出现的「G1–G4」是 M1_HWCONFIRM1B_RX_SLOT_HW_RULING.md:70-109 的 grep 配方编号，与 references 的 Gate 无关。
