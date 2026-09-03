#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s7_intake.py -- S7 板测结果回填 -> 判读结论（宿主脚本，/usr/bin/python3，纯标准库）  v2 (2026-09-03, critic-F 后)

用法:
  s7_intake.py --schema                       # 打印空白回填模板（INI），与 S7_BOARD_RESULTS_INTAKE.md §1 逐字同源
  s7_intake.py <filled.ini> [选项]            # 读回填文件，按 S7_BOARD_RESULTS_INTAKE.md §2/§3 决策树给结论
选项: --tol 0.05  --rxpoll-tol 0.01  --overrun-tol 0.001  --full-scale-near 0x7F000000
      --ovh-tol-frac 0.05  --ovh-tol-cyc 2000  --use-optimized-baseline
退出码: 0 = 无 BLOCKER 且全部可判；1 = 有 BLOCKER；2 = 有不可判项（缺项/格式错/前置门未过）

纪律（FG2）:
  * 本脚本不含任何板上实测数字。期望值只来自: (a) 冻结 golden 头 dolph_f5_goldens.h（运行时解析）;
    (b) 由帧口径推导的阈值（帧预算 = CCLK × 64/48000）; (c) 文档已登记的对照量（REFS，带 L 标，只作对照）。
  * 空位 = 未回填 -> "不可判"，绝不默认 PASS。
  * 回灌规则：任何一节（build/臂/bench）指纹不符、板门不绿、FG 不绿 -> 该节标记无效，其读数不参与
    差距分类、三段归因、B1 门；报告里同一份读数不会既"作废"又"PASS"。
  * 容差全部是工作假设 [L4]，可改；结论行带 L 标；最终裁定权在 CTO。
  * 口径：差距分类用稳态读数（beam_cyc_min，S7_B63 §6 定义；要求 last 与 min 一致 ±tol，否则稳态不可判）；B1 余量用 beam_cyc_max（WCET）。
    帧预算与 1.5x 线由 [CLK] 节回填的 CGU 寄存器实测值解码后重算（CTO 2026-09-03 D-CCLK）；
    未回填 -> 条件 0 未满足 -> B1 挂起。1e9 只作对照（bench F7 读回 [L1]）。
"""
import sys, os, re, argparse, configparser

VERSION = "v3.3 2026-09-03"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GOLDEN_H = os.path.join(ROOT, "sprint4", "dsp", "fira", "dolph_f5_goldens.h")

# ---- 参考量（只作对照，不作期望；来源与 L 标） ---------------------------------------------
REFS = {
    "CCLK_HZ":        (1_000_000_000, "[L1 bench F7 读回 g_f7_cclk_hz，F7_CLOSING_RECORDS.md:156]；M2 工程同频为推断 [L3]（S7_B63 排查表 #15，待 g_m2_cclk_hz 对照，CTO-gated）"),
    "FRAME":          (64,            "[L1 源码] m1_loopback_tdm.h M1_FRAME"),
    "FS":             (48000,         "[L1 源码] m1_loopback_tdm.h M1_FS_HZ"),
    "T2_RATIO":       (1.5,           "[裁定] DEC-S4-CRITERION-01-FINAL；口径 = 墙钟（DEC-S7-RULINGS-01 D1）"),
    "BEAM_HIST_MAX":  (830_903,       "[L1 墙钟] DEC-S6-M2-BOARD-PASS-01 g_m2_beam_cyc_max（06-16，run 内最大值）"),
    "F7_HIST":        (463_273,       "[L1 bench] F7_CLOSING_RECORDS.md:154 8ch FIRA 含忙等"),
    "B1_LO":          (6_728,         "[L3] S7_DSP_ASSESSMENT.md §8.1 B1 低端估计"),
    "B1_HI":          (52_352,        "[L4] S7_DSP_ASSESSMENT.md §8.1 B1 高端估计"),
    "SEG_READS_BOARD":(33,            "[L1 源码] M2_SEG_CYC 链式读法每帧 CCNT 读次数（S7_B63 §3）"),
    "SEG_READS_BENCH":(25,            "[L1 源码] s7_wallclock_probe g_s7_reads_per_frame"),
    "SELFTEST_FRAMES":(8 * 1024,      "[派生] 8 通道 × 1024 帧（M2_SELFTEST 定义 = F5）"),
    "BENCH_FRAMES":   ((1024, 1020),  "[L1 源码] s7_wallclock_probe README §3 frames_total / frames"),
    "HEADROOM_Q31":   (0x49A00000,    "[L1 契约] −4.8 dBFS 输入 headroom（tree_filterbank.h；R57 判别式，M1_CCES_IMPORT_GUIDE）"),
    "L2_LO":          (0x20000000,    "[L1 文件] m1_app.ldf mem_L2_bw 起"),
    "L2_HI":          (0x200F9FFF,    "[L1 文件] m1_app.ldf mem_L2_bw 止"),
    "BLOCK1_LO":      (0x002C0000,    "[L1 文件] m1_app.ldf mem_block1_bw 起（三 pin 符号）"),
    "BLOCK1_HI":      (0x002EBFFF,    "[L1 文件] m1_app.ldf mem_block1_bw 止"),
    "L1_LO":          (0x00240000,    "[L1 文件] m1_app.ldf L1 Block0 起（FIRA DMA scratch s_seg_* 须在 L1，非 L2）"),
    "L1_HI":          (0x0039BFFF,    "[L1 文件] m1_app.ldf L1 Block3 止"),
    "CGU0_CTL":       (0x3108D000,    "[L1 头文件] CCES 2.12.1 sys/ADSP_2156x_HPC.h:13186 REG_CGU0_CTL"),
    "CGU0_STAT":      (0x3108D008,    "[L1 头文件] 同上 :13188 REG_CGU0_STAT"),
    "CGU0_DIV":       (0x3108D00C,    "[L1 头文件] 同上 :13189 REG_CGU0_DIV"),
    "CLKIN_HZ":       (25_000_000,    "[L1 文件] AD-EXKIT V2.1 核心板原理图：25 MHz 振荡器直连 SYS_CLKIN0（knowledge_base/ezkit/vendor_docs/schematics/V2.1/ADSP21569核心板原理图.pdf）；与 m1_main.c:44 adi_pwr_Init(0,25MHz) 实参、ADI 21569 家族配置头 CFG0_BIT_CGU0_CLKIN=25000000 三方一致"),
    "CCLK_MIN":       (400_000_000,   "[L1 文件] ADSP-2156x 数据手册 Rev.C(2022-11) **Table 19 Clock Operating Conditions** p.44：fCCLK 400–1000 MHz"),
    "CCLK_MAX":       (1_000_000_000, "[L1 文件] 同上"),
    "FPLL_MIN":       (1_200_000_000, "[L1 文件] 同一手册 **Table 20 Phase-Locked Loop (PLL) Operating Conditions** p.45：fPLLCLK 1.20–2.00 GHz"),
    "FPLL_MAX":       (2_000_000_000, "[L1 文件] 同上 Table 20"),
    "CLKIN_MIN":      (20_000_000,    "[L1 文件] 同一手册 **Table 33 Clock and Reset Timing**：fCKIN SYS_CLKIN0 20–30 MHz（晶振或外部时钟）"),
    "CLKIN_MAX":      (30_000_000,    "[L1 文件] 同上 Table 33"),
}
# CGU 位域（[L1 头文件] ADSP_2156x_HPC.h:13213/13214/13293/13257/13258）
CGU_MSEL_POS, CGU_MSEL_MSK = 8, 0x7F
CGU_DF_POS,   CGU_DF_MSK   = 0, 0x1
CGU_CSEL_POS, CGU_CSEL_MSK = 0, 0x1F
CGU_PLLEN_MSK, CGU_PLLBP_MSK = 0x1, 0x2
MAX_MSEL, MAX_CSEL = 128, 32   # [L1 源码] adi_pwr_def_2156x.h:129/136 ADI_PWR_MAX_MSEL / ADI_PWR_MAX_CSEL
# 解码公式（**21569 = __ADSP21569_FAMILY__，走非 21568 分支，没有 /2**）：
#   PLLEN=0 或 PLLBP=1        -> CCLK = CLKIN
#   否则 fPLL = (CLKIN/(DF+1)) * MSEL ; CCLK = fPLL / CSEL ; MSEL=0 视为 128、CSEL=0 视为 32
# 出处 [L1 源码]：CCES 2.12.1 lib/src/services/Source/pwr/adi_pwr_2156x.c adi_pwr_GetCoreClkFreq()
#   —— `#if defined(__ADSP21568_FAMILY__) fpllclk = clkin*msel/2u; #else fpllclk = (clkin/(df+1u))*msel; #endif`
#      这正是 bench F7 G6 读回 1e9 用的同一函数。
# 四锚交叉验证 [L1 工具链]（ldr/init_code/2156x_Init/src/adi_pwr_21569_family_*_config.h，CLKIN 均 25 MHz）：
#   MSEL 80 / DF 0 / CSEL 2 -> 1000 MHz ; 64/0/2 -> 800 ; 72/0/3 -> 600 ; 48/0/3 -> 400
# （critic-F delta-3 BLOCKER：v3 初稿误用 21568 家族的 /2，已按上述源码与四锚改正。）
# 参考值（仅对照；判据一律用 [CLK] 实测解码值）
FRAME_BUDGET_REF = round(REFS["CCLK_HZ"][0] * REFS["FRAME"][0] / REFS["FS"][0])   # 1,333,333
T2_LINE_REF = round(FRAME_BUDGET_REF / REFS["T2_RATIO"][0])                       #   888,889

# ---- 期望值：冻结 golden（运行时解析，不复写数字） ----------------------------------------------
def load_anchors():
    txt = open(GOLDEN_H, encoding="utf-8", errors="replace").read()
    pairs = re.findall(r"0x([0-9A-Fa-f]{8})u\s*,?\s*/\*\s*c=(\d)", txt)
    byc = {int(c): int(v, 16) for v, c in pairs}
    if sorted(byc) != list(range(8)):
        sys.exit("expected anchors c=0..7 in %s, got %s" % (GOLDEN_H, sorted(byc)))
    anchors = [byc[c] for c in range(8)]
    return anchors, anchors[7]   # c=7 unity == F4 unweighted subband golden（dolph_f5_goldens.h 注释：continuity）

# ---- 回填模板（与 S7_BOARD_RESULTS_INTAKE.md §1 同源；--schema 打印） ---------------------------
SB_COMMON = """fira_inloop =
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
"""
SB_SELFTEST = """selftest_rc =
selftest_frames =
selftest_pass =                 ; 8 个 0/1，逗号分隔
selftest_crc =                  ; 8 个 0x........，逗号分隔
selftest_crc_core =             ; 8 个 0x........，逗号分隔
selftest_mismatch_sb =          ; 8 个，逗号分隔（-1 = 无）
selftest_mismatch_idx =         ; 8 个，逗号分隔（-1 = 无）
selftest_cyc =                  ; 无期望值，只记录
selftest_cyc_ch =               ; 8 个，逗号分隔；无期望值，只记录
"""
SB_SEG = """seg_w_cyc_last =                ; 无期望值，只记录
seg_w_cyc_max =
seg_ana_cyc_last =
seg_ana_cyc_max =
seg_syn_cyc_last =
seg_syn_cyc_max =
seg_tx_cyc_last =
seg_tx_cyc_max =
"""
SCHEMA = """; S7 板测回填文件（INI）。空位 = 未回填 = 不可判。数字抄原值；十六进制带 0x；yes/no 小写。
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
{common}
[SB.B1]  ; + M2_SELFTEST=1 + M2_SEG_CYC=1（= B63 臂 0s）
{common}{selftest}{seg}
[SB.B2]  ; + M2_SELFTEST=1 + M2_SELFTEST_NEGCTRL=1（无 SEG_CYC）
{common}{selftest}
[SB.B3]  ; 无任何宏（M1 透传）：只填指纹 + main_init_rc/m1_valid/fg_stream_live/rx_block_count
{common}
; ===== 批 2：B6.3 对照臂（sprint7/docs/S7_B63_WALLCLOCK_GAP.md §1/§5）=====
[B63.A1] ; 臂 A'：Debug + GUI 勾 -O（路径 A），无 SEG_CYC；必须附 -O 凭证
o_evidence =                    ; Console 编译行含 -O 的截图文件名
ov_value =                      ; GUI 显示的 -Ov 值（原样抄）
{common}
[B63.As] ; 臂 As：Debug + -O + M2_SEG_CYC=1（可选）
o_evidence =
{common}{seg}
[B63.A2] ; 臂 A''：Debug + -O + 只取消勾 Use Debug System libraries（可选，排查表 #2 单变量）
o_evidence =
debuglib_unchecked_evidence =   ; 截图文件名
{common}
[B63.B]  ; 臂 B：Release（路径 B，旁证；可选）
o_evidence =
cproject_checked_out =          ; yes（build 后 .cproject/.project 已 checkout，不入库）
{common}
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
"""

def schema_text():
    return SCHEMA.replace("{common}", SB_COMMON).replace("{selftest}", SB_SELFTEST).replace("{seg}", SB_SEG)

# ---- 解析工具 ----------------------------------------------------------------------------------
class Missing(Exception):
    pass

def _clean(v):
    return (v or "").strip()          # 行内注释由 configparser（前置空白 + ';'）剥离；值内的 ';' 不再被截断

def has(cfg, sec):
    return sec in cfg and any(_clean(v) for v in cfg[sec].values())

def get(cfg, sec, key, kind="str", required=True):
    if sec not in cfg or key not in cfg[sec] or _clean(cfg[sec][key]) == "":
        if required:
            raise Missing("%s.%s" % (sec, key))
        return None
    v = _clean(cfg[sec][key])
    try:
        if kind == "int":  return int(v, 0)
        if kind == "hex":  return int(v, 16) if v.lower().startswith("0x") else int(v, 0)
        if kind == "list_int": return [int(x.strip(), 0) for x in v.split(",") if x.strip()]
        if kind == "list_hex": return [int(x.strip(), 16) if x.strip().lower().startswith("0x") else int(x.strip(), 0) for x in v.split(",") if x.strip()]
        if kind == "yesno": return v.lower() in ("yes", "y", "1", "true", "是")
        if kind == "int_or_na": return None if v.lower() in ("na", "n/a", "-", "不可见", "符号不存在") else int(v, 0)
    except ValueError:
        raise Missing("%s.%s（格式错：%r）" % (sec, key, v))
    return v

class Report:
    def __init__(self):
        self.lines = []; self.blockers = 0; self.majors = 0; self.unjudged = 0; self.bad_secs = set()
    def h(self, t): self.lines.append("\n## " + t)
    def ok(self, t): self.lines.append("- PASS  " + t)
    def blocker(self, t, sec=None):
        self.blockers += 1; self.lines.append("- **BLOCKER** " + t)
        if sec: self.bad_secs.add(sec)
    def major(self, t): self.majors += 1; self.lines.append("- MAJOR " + t)
    def info(self, t): self.lines.append("- info  " + t)
    def unj(self, t): self.unjudged += 1; self.lines.append("- 不可判 " + t)
    def text(self): return "\n".join(self.lines)

# ---- 批 1 附：实测 CCLK 解码（CTO 2026-09-03：条件 0 只认实测，不用旗位放行） ------------------
def decode_cclk(cfg, rep, args):
    """返回 dict(cclk, budget, line, ok, clkin, msel, df, csel) ；ok=False 表示条件 0 未满足"""
    out = {"ok": False, "cclk": None, "budget": None, "line": None}
    rep.h("批 1 附：M2 实测核心时钟（CGU 寄存器解码；帧预算与 1.5× 线的唯一依据）")
    if not has(cfg, "CLK"):
        rep.unj("[CLK] 未回填 → **条件 0 未满足**（CTO 2026-09-03：实测 CCLK 回来前条件 0 视为未满足）→ B1 挂起；帧预算/1.5× 线只能按 1e9 参考推算，不作判据")
        return out
    try:
        ctl = get(cfg, "CLK", "cgu0_ctl", "hex"); stat = get(cfg, "CLK", "cgu0_stat", "hex")
        div = get(cfg, "CLK", "cgu0_div", "hex"); clkin = get(cfg, "CLK", "clkin_hz", "int")
        rb = get(cfg, "CLK", "read_build"); rm = get(cfg, "CLK", "read_method"); ev = get(cfg, "CLK", "evidence")
    except Missing as m:
        rep.unj("[CLK] 缺回填：%s → 条件 0 未满足 → B1 挂起" % m); return out
    msel = (ctl >> CGU_MSEL_POS) & CGU_MSEL_MSK
    df   = (ctl >> CGU_DF_POS) & CGU_DF_MSK
    csel = (div >> CGU_CSEL_POS) & CGU_CSEL_MSK
    pllen = stat & CGU_PLLEN_MSK; pllbp = (stat & CGU_PLLBP_MSK) >> 1
    rep.info("原值：CGU0_CTL=0x%08X CGU0_STAT=0x%08X CGU0_DIV=0x%08X；CLKIN=%d Hz（%s）；在 build %s 用 %s 读，凭证 %s"
             % (ctl, stat, div, clkin, REFS["CLKIN_HZ"][1], rb, rm, ev))
    rep.info("解码：MSEL=%d DF=%d CSEL=%d PLLEN=%d PLLBP=%d（位域 [L1 头文件] ADSP_2156x_HPC.h）" % (msel, df, csel, pllen, pllbp))
    if not (REFS["CLKIN_MIN"][0] <= clkin <= REFS["CLKIN_MAX"][0]):
        rep.unj("CLKIN=%d Hz 超出数据手册 SYS_CLKIN0 范围 %d–%d Hz（%s）→ 抄写或出处存疑，**不按 [L1] 用** → 条件 0 未满足"
                % (clkin, REFS["CLKIN_MIN"][0], REFS["CLKIN_MAX"][0], REFS["CLKIN_MIN"][1])); return out
    if (not pllen) or pllbp:
        rep.major("CGU0_STAT：PLLEN=%d / PLLBP=%d → PLL 未使能或旁路，按 ADI 源码 CCLK = CLKIN = %d Hz，**低于数据手册 Table 19 fCCLK 下限 %d Hz**：芯片没跑在规格频率上，任何余量判定都无意义 → 先查启动配置与 `adi_pwr_Init` 返回码"
                  % (pllen, pllbp, clkin, REFS["CCLK_MIN"][0]))
        rep.unj("条件 0 未满足（CTO 定义：未实测则不满足；**PM 处置**：实测显示芯片超规运行同样不放行）→ B1 挂起"); return out
    else:
        msel_e = msel if msel else MAX_MSEL
        csel_e = csel if csel else MAX_CSEL
        if msel == 0 or csel == 0:
            rep.info("字段 0 按 ADI 源码语义取最大值：MSEL %d→%d、CSEL %d→%d（adi_pwr_def_2156x.h:129/136）" % (msel, msel_e, csel, csel_e))
        if df:
            rep.info("DF=1 → 先把 CLKIN 二分频（%d → %d Hz），再乘 MSEL（adi_pwr_2156x.c 非 21568 家族分支）" % (clkin, clkin // 2))
        fpll = (clkin // (df + 1)) * msel_e
        cclk = fpll // csel_e
        rep.info("fPLL = (CLKIN/(DF+1))×MSEL = %d Hz；CCLK = fPLL/CSEL = %d Hz（21569 走非 21568 家族分支，**无 /2**）" % (fpll, cclk))
        if fpll % csel_e: rep.info("fPLL/CSEL 有余数 %d，已向下取整" % (fpll % csel_e))
        # 物理合理性门（单点抄错即放行的防线；数据手册 [L1]）
        if not (REFS["FPLL_MIN"][0] <= fpll <= REFS["FPLL_MAX"][0]):
            rep.unj("fPLL=%d Hz 超出数据手册 PLL 范围 %d–%d Hz（%s）→ 寄存器读错位或抄写有误，**不按 [L1] 用** → 条件 0 未满足；请重读三个寄存器并附截图"
                    % (fpll, REFS["FPLL_MIN"][0], REFS["FPLL_MAX"][0], REFS["FPLL_MIN"][1])); return out
        if not (REFS["CCLK_MIN"][0] <= cclk <= REFS["CCLK_MAX"][0]):
            rep.unj("解出 CCLK=%d Hz 超出数据手册 fCCLK 范围 %d–%d Hz（%s）→ CSEL/MSEL 抄错一位即会这样，**不按 [L1] 用** → 条件 0 未满足；请重读并附截图"
                    % (cclk, REFS["CCLK_MIN"][0], REFS["CCLK_MAX"][0], REFS["CCLK_MIN"][1])); return out
    budget = round(cclk * REFS["FRAME"][0] / REFS["FS"][0]); line = round(budget / REFS["T2_RATIO"][0])
    out.update(ok=True, cclk=cclk, budget=budget, line=line, clkin=clkin, msel=msel, df=df, csel=csel)
    rep.ok("实测 CCLK = %d Hz [L1/EZKIT 寄存器解码] → 帧预算 = %d cyc、1.5× 线 = %d cyc（本报告后续一律用这两个值）" % (cclk, budget, line))
    if cclk != REFS["CCLK_HZ"][0]:
        rep.major("实测 CCLK ≠ 1e9（bench F7 G6 读回 [L1]）→ 历史帧预算 %d / 1.5× 线 %d 作废，需按实测重算；所有已登记的 cycle 数不变，但余量与 1.5× 判定全部重算，并核 bench 与 M2 是否同频"
                  % (FRAME_BUDGET_REF, T2_LINE_REF))
    return out

# ---- 批 1：指纹与板门（表 A / 板门 / .map） ---------------------------------------------------
NA = "na"
FP_EXPECT = {  # 表 A（S7_TESTER_RUNBOOK_SB.md §4 表 A，含 selftest_negctrl_built 与 seg 可见性）
    "SB.B0":  dict(fira_inloop=1, selftest_built=0, selftest_negctrl_built=NA, seg_vis=False),
    "SB.B1":  dict(fira_inloop=1, selftest_built=1, selftest_negctrl_built=0,  seg_vis=True),
    "SB.B2":  dict(fira_inloop=1, selftest_built=1, selftest_negctrl_built=1,  seg_vis=False),
    "SB.B3":  dict(fira_inloop=0, selftest_built=0, selftest_negctrl_built=NA, seg_vis=False),
    "B63.A1": dict(fira_inloop=1, selftest_built=0, selftest_negctrl_built=NA, seg_vis=False),
    "B63.As": dict(fira_inloop=1, selftest_built=0, selftest_negctrl_built=NA, seg_vis=True),
    "B63.A2": dict(fira_inloop=1, selftest_built=0, selftest_negctrl_built=NA, seg_vis=False),
    "B63.B":  dict(fira_inloop=1, selftest_built=0, selftest_negctrl_built=NA, seg_vis=False),
}
ZERO_FPS = ("static_txtest_built", "stxt_localize_built", "chmap_fix_built", "rx_right_aligned_built", "u6_addr_override_built")

def check_fingerprints(cfg, sec, rep):
    exp = FP_EXPECT[sec]; bad = []
    try:
        for k in ("fira_inloop", "selftest_built"):
            got = get(cfg, sec, k, "int")
            if got != exp[k]: bad.append("%s=%d（期望 %d）" % (k, got, exp[k]))
        for k in ZERO_FPS:
            got = get(cfg, sec, k, "int")
            if got != 0: bad.append("%s=%d（期望 0；残留了对应宏）" % (k, got))
        ng = get(cfg, sec, "selftest_negctrl_built", "int_or_na")
        if exp["selftest_negctrl_built"] == NA:
            if ng is not None:
                if get(cfg, sec, "selftest_built", "int") == 0 and ng == 0:
                    rep.major("%s selftest_negctrl_built 填了 0 但 selftest_built=0（符号应不存在，应填 na）→ 填写不一致，按 na 处理；请测试员核对 Defined symbols 截图" % sec)
                else:
                    bad.append("selftest_negctrl_built 可见=%d（期望符号不存在：该 build 不该带 M2_SELFTEST）" % ng)
        else:
            if ng is None: bad.append("selftest_negctrl_built 符号不存在（期望 %d）" % exp["selftest_negctrl_built"])
            elif ng != exp["selftest_negctrl_built"]: bad.append("selftest_negctrl_built=%d（期望 %d）" % (ng, exp["selftest_negctrl_built"]))
        vis = get(cfg, sec, "seg_w_cyc_last_visible", "yesno")
        if vis != exp["seg_vis"]: bad.append("seg_w_cyc_last 可见性=%s（期望 %s；%s）" % (vis, exp["seg_vis"], "残留了 M2_SEG_CYC" if vis else "缺 M2_SEG_CYC"))
    except Missing as m:
        rep.unj("%s 指纹缺回填：%s → 本节全部读数不可判" % (sec, m)); rep.bad_secs.add(sec); return False
    if bad:
        rep.blocker("%s 指纹不符：%s → 该 build 全部读数作废（R52 stale-state），回 runbook §3 第 1 步重做" % (sec, "；".join(bad)), sec); return False
    rep.ok("%s 指纹与表 A 一致" % sec); return True

def check_board_gate(cfg, sec, rep, args, m2=True):
    try:
        init_rc = get(cfg, sec, "main_init_rc", "int"); m1v = get(cfg, sec, "m1_valid", "int")
        fgs = get(cfg, sec, "fg_stream_live", "int"); rx = get(cfg, sec, "rx_block_count", "int")
        if m2:
            m2v = get(cfg, sec, "m2_valid", "int"); src = get(cfg, sec, "setup_rc", "int")
            fgb = get(cfg, sec, "fg_beam_live", "int"); poll = get(cfg, sec, "poll_count", "int")
            ovr = get(cfg, sec, "overrun_count", "int"); omax = get(cfg, sec, "out_max_abs", "hex")
            imax = get(cfg, sec, "m1_max_abs_sample", "hex")
            pins = [get(cfg, sec, k, "hex") for k in ("map_rx_addr", "map_tx_addr", "map_fa_addr")]
            segs = [get(cfg, sec, k, "hex") for k in ("map_seg_in_addr", "map_seg_out3_addr", "map_taskmem_addr")]
    except Missing as m:
        rep.unj("%s 板门/.map 缺回填：%s → 本节读数不可判" % (sec, m)); rep.bad_secs.add(sec); return False
    bad = []
    if init_rc != 0: bad.append("main_init_rc=%d" % init_rc)
    if m1v != 1: bad.append("m1_valid=%d" % m1v)
    if fgs != 1: bad.append("fg_stream_live=%d" % fgs)
    if rx <= 0: bad.append("rx_block_count 未增长")
    if m2:
        if m2v != 1: bad.append("m2_valid=%d" % m2v)
        if src != 0: bad.append("setup_rc=%d（-99=未跑）" % src)
        if fgb != 1: bad.append("fg_beam_live=%d" % fgb)
        if rx > 0 and abs(rx - poll) > max(1, args.rxpoll_tol * rx): bad.append("rx=%d vs poll=%d 偏差超 %.1f%%" % (rx, poll, args.rxpoll_tol * 100))
        if ovr > args.overrun_tol * max(rx, 1): bad.append("overrun=%d（> %.2f%% × rx）→ main 跟不上" % (ovr, args.overrun_tol * 100))
        if omax >= args.full_scale_near:
            if imax < REFS["HEADROOM_Q31"][0]:
                bad.append("out_max_abs=0x%08X 顶满幅 且 m1_max_abs_sample=0x%08X < 0x%08X（−4.8 dBFS 契约）→ 逐帧 FIRA 失败特征（R57 判别式）" % (omax, imax, REFS["HEADROOM_Q31"][0]))
            else:
                bad.append("out_max_abs=0x%08X 顶满幅 但 m1_max_abs_sample=0x%08X 也高 → 音源过热，先降电平重跑（R57）" % (omax, imax))
        for name, a in zip(("s_m1_rx_buf", "s_m1_tx_buf", "s_m2_fa"), pins):
            if not (REFS["BLOCK1_LO"][0] <= a <= REFS["BLOCK1_HI"][0]):
                bad.append("%s=0x%06X 不在 Block1（0x%06X–0x%06X）→ 布局漂了（IO2 疑点）" % (name, a, REFS["BLOCK1_LO"][0], REFS["BLOCK1_HI"][0]))
        for name, a in zip(("s_seg_in", "s_seg_out3", "s_taskMem"), segs):
            if not (REFS["L1_LO"][0] <= a <= REFS["L1_HI"][0]):
                bad.append("%s=0x%08X 不在 L1（落 L2 = cached，会静默污染 FIRA 输入腿，R57）" % (name, a))
    if bad:
        rep.blocker("%s 板门/.map 不绿：%s → 本节读数隔离不入账、不抢救（F4 纪律），原样发回" % (sec, "；".join(bad)), sec); return False
    rep.ok("%s 板门与 .map 全绿（rx=%d）" % (sec, rx)); return True

def check_selftest(cfg, sec, rep, anchors, f4, negctrl):
    """返回 True/False/None；False 一律把 sec 标为无效（自检读数不可信）"""
    try:
        rc = get(cfg, sec, "selftest_rc", "int"); frames = get(cfg, sec, "selftest_frames", "int")
        pas = get(cfg, sec, "selftest_pass", "list_int"); crc = get(cfg, sec, "selftest_crc", "list_hex")
        core = get(cfg, sec, "selftest_crc_core", "list_hex"); msb = get(cfg, sec, "selftest_mismatch_sb", "list_int")
        chirp = get(cfg, sec, "map_chirp_addr", "hex")
    except Missing as m:
        rep.unj("%s 自检缺回填：%s" % (sec, m)); rep.bad_secs.add(sec); return None
    if not (len(pas) == len(crc) == len(core) == len(msb) == 8):
        rep.unj("%s 自检数组长度不是 8" % sec); rep.bad_secs.add(sec); return None
    if not (REFS["L2_LO"][0] <= chirp <= REFS["L2_HI"][0]):
        rep.blocker("%s CHIRP_INPUT=0x%08X 不在 L2（%s）→ 放置假设失败，自检读数不可信；按 runbook §8 备用方案" % (sec, chirp, REFS["L2_LO"][1]), sec); return False
    if frames != REFS["SELFTEST_FRAMES"][0]:
        rep.blocker("%s selftest_frames=%d ≠ %d → 自检未跑完（Run 时间不够?）或提前退出，自检结论作废；重跑 ≥20 s" % (sec, frames, REFS["SELFTEST_FRAMES"][0]), sec); return False
    if not negctrl:
        if rc == 0 and pas == [1] * 8 and crc == anchors and core == anchors:
            rep.ok("%s 八锚自检 8/8 PASS（板上 FIRA 链与冻结 golden 逐位同，[L1/EZKIT]）" % sec); return True
        core_bad = [c for c in range(8) if core[c] != anchors[c]]
        fira_bad = [c for c in range(8) if crc[c] != anchors[c]]
        if core_bad:
            rep.blocker("%s 自检 FAIL 且 crc_core≠锚（通道 %s）→ 链前段漂（chirp 放置/读取、加权、核 tfb_analyze 在板上不同于 host）；核 .map/Run 时长/mismatch_idx；所有候选停，上报 CTO（不是「FIRA 坏」的证据，也不排除）" % (sec, core_bad), sec)
        elif fira_bad:
            rep.blocker("%s 自检 FAIL 但 crc_core==锚（FIRA 通道 %s 不符，首失配子带 %s）→ 板上 FIRA 链不 bit-exact（与 F4/F5 bench PASS 矛盾 → 比较 bench 与 M2 工程差异）；M2 波形不可信、B1 不得启动，上报 CTO" % (sec, fira_bad, [msb[c] for c in fira_bad]), sec)
        else:
            rep.blocker("%s 自检 rc=%d 但 crc 全等锚 → 判据/计数逻辑异常，自检本身不可信，上报（走 critic）" % (sec, rc), sec)
        return False
    # 负控制
    if rc == 7 and pas == [0] * 7 + [1] and all(v == f4 for v in crc):
        rep.ok("%s 负控制 rc=7、8 路 CRC 坍缩到 F4 锚 → 自检真依赖权重（FG2 通过）" % sec); return True
    if rc == 0:
        rep.blocker("%s 负控制 rc=0 = unity 权重也 PASS → 自检假绿（不依赖被测权重；指纹已证 NEGCTRL 宏在），B1 的自检 PASS 作废；查权重表读取路径，上报" % sec, sec)
    elif rc == 8:
        rep.blocker("%s 负控制 rc=8 = 连 c=7（unity）也 FAIL → CRC/比较路径坏或 F4 连续性被破坏；自检不可信" % sec, sec)
    else:
        rep.blocker("%s 负控制 rc=%d pass=%s crc=%s ≠ 预期（rc=7，全 0x%08X）→ 自检不可信，抄全表上报" % (sec, rc, pas, ["0x%08X" % v for v in crc], f4), sec)
    return False

# ---- 批 3：bench 探针有效性 -------------------------------------------------------------------
def check_bench(cfg, rep, anchors, clk):
    sec = "BENCH.P"
    try:
        done = get(cfg, sec, "done", "int"); valid = get(cfg, sec, "valid", "int"); src = get(cfg, sec, "setup_rc", "int")
        csc = get(cfg, sec, "core_selfcheck_all", "int"); fg = get(cfg, sec, "fg_pass_all", "int")
        crc = get(cfg, sec, "crc_fira", "list_hex"); ft = get(cfg, sec, "frames_total", "int"); fr = get(cfg, sec, "frames", "int")
        cclk = get(cfg, sec, "cclk_hz", "int"); crc_rc = get(cfg, sec, "cclk_rc", "int")
        rpf = get(cfg, sec, "reads_per_frame", "int"); f4 = get(cfg, sec, "f4_pass", "int"); f5 = get(cfg, sec, "f5_pass_all", "int")
        sfb = get(cfg, sec, "syn_fg_built", "int"); sfa = get(cfg, sec, "syn_fg_all", "int")
    except Missing as m:
        rep.unj("bench-P 缺回填：%s → bench 三段与参考不入账" % m); rep.bad_secs.add(sec); return False
    bad = []
    if (done, valid, src) != (1, 1, 0): bad.append("done/valid/setup_rc=%d/%d/%d（期望 1/1/0）" % (done, valid, src))
    if csc != 1: bad.append("core_selfcheck_all=%d（核链正控制未过 → 探针基建坏）" % csc)
    if fg != 1 or crc != anchors: bad.append("fg_pass_all=%d / crc_fira≠八锚（探针没量到真链）" % fg)
    if (ft, fr) != REFS["BENCH_FRAMES"][0]: bad.append("frames_total/frames=%d/%d（期望 %d/%d）" % (ft, fr, REFS["BENCH_FRAMES"][0][0], REFS["BENCH_FRAMES"][0][1]))
    if rpf != REFS["SEG_READS_BENCH"][0]: bad.append("reads_per_frame=%d（期望 %d，探针版本不对）" % (rpf, REFS["SEG_READS_BENCH"][0]))
    if (f4, f5) != (1, 1): bad.append("同 build F4/F5 旗=%d/%d（布局 canary 失效，IO2）" % (f4, f5))
    if bad:
        rep.blocker("bench-P 无效：%s → bench 三段作废、不作差距参考（回退历史 F7）" % "；".join(bad), sec); return False
    ref_cclk = clk["cclk"] if clk["ok"] else REFS["CCLK_HZ"][0]
    ref_src = "M2 实测解码值" if clk["ok"] else "历史 F7 G6 读回 1e9 [L1]"
    if crc_rc != 0:
        rep.major("bench-P cclk_rc=%d ≠ 0 → 时钟查询本身失败，cclk_hz 不可信（排查表 #15）" % crc_rc)
    elif cclk != ref_cclk:
        rep.major("bench-P cclk_hz=%d 与 %s（%d）不符 → 两工程同板却不同频，或读法有误；三段与差距须先按时钟比折算（排查表 #15）" % (cclk, ref_src, ref_cclk))
    if sfb == 1:
        rep.info("bench-P SYN_FG 旗：syn_fg_all=%d（1=合成侧对照过；-2=FG-A 未过未评估；0=记录上报，不默认作废 w/ana）" % sfa)
    rep.ok("bench-P 有效：FG 全绿、八锚 8/8（analyze 段真链）、frames %d/%d、reads %d；syn 段无锚（置信低一档，README §6c）" % (ft, fr, rpf))
    return True

# ---- 批 2：墙钟差距（口径对齐 S7_B63 §6：稳态用 last/min，WCET 用 max） -----------------------
def steady(cfg, sec, rep, args):
    """返回 (steady, max, min) 或 None；稳态 = beam_cyc_min（B63 §6 定义），要求 last 与 min 一致（±tol），按步骤 1 判离群"""
    last = get(cfg, sec, "beam_cyc_last", "int"); mx = get(cfg, sec, "beam_cyc_max", "int"); mn = get(cfg, sec, "beam_cyc_min", "int")
    if not (mn <= last <= mx):
        rep.unj("%s：beam_cyc min/last/max = %d/%d/%d 不满足 min ≤ last ≤ max → 读数抄错或不同帧，稳态不可判" % (sec, mn, last, mx)); return None
    if abs(last - mn) > args.tol * mn:
        rep.unj("%s：last（%d）与 min（%d）相差超 %.0f%% → 单帧样本不稳，稳态不可判；重跑取多帧或按 B63 §6 用 min/last 并列后由 CTO 裁" % (sec, last, mn, args.tol * 100)); return None
    if mx / mn > 1 + args.tol:
        rep.info("%s：min≈last（%d≈%d）≪ max（%d）→ max 是 run 内离群/冷帧（B63 §6 步骤 1）；稳态 = min，WCET = max" % (sec, mn, last, mx))
    else:
        rep.info("%s：min≈last≈max（%d/%d/%d）→ 系统性，稳态 ≈ WCET" % (sec, mn, last, mx))
    return mn, mx, mn

def classify_gap(cfg, rep, args, valid, bench_ok, clk):
    """返回 dict(base_max, base_steady, bench_ref, opt_max, opt_steady, gap_class, anomalous)"""
    out = {"gap_class": None, "anomalous": False}
    if not valid.get("SB.B0"):
        rep.unj("臂 0（SB.B0）无效或未回填 → 无基线，B6.3 不可判"); return out
    st0 = steady(cfg, "SB.B0", rep, args)
    if st0 is None:
        rep.unj("臂 0 稳态不可判 → B6.3 不可判"); return out
    b0s, b0m, _ = st0
    out["base_max"] = b0m; out["base_steady"] = b0s
    bud = clk["budget"] or FRAME_BUDGET_REF; ln = clk["line"] or T2_LINE_REF
    tag = "实测 CCLK" if clk["ok"] else "**参考 1e9，未实测，条件 0 未满足**"
    rep.info("臂 0 Debug 基线：稳态 %d / WCET %d；WCET 墙钟余量 %.3f×，到 1.5× 线 %+d cyc（帧预算 %d / 线 %d，来源 %s；对照 06-16 历史 %d %s）"
             % (b0s, b0m, bud / b0m, ln - b0m, bud, ln, tag, REFS["BEAM_HIST_MAX"][0], REFS["BEAM_HIST_MAX"][1]))
    if abs(b0m - REFS["BEAM_HIST_MAX"][0]) > args.tol * REFS["BEAM_HIST_MAX"][0]:
        out["hist_mismatch"] = True
        rep.major("臂 0 WCET 与 06-16 历史值相差超 %.0f%% → 先解释（build/宏/音源/首帧冷?）再用作基线" % (args.tol * 100))
    if bench_ok:
        bench_ref = get(cfg, "BENCH.P", "beam_cyc_min", "int"); bench_src = "本次 bench-P beam_cyc_min=%d [L1 bench]（与板上稳态同取 min）" % bench_ref
    else:
        bench_ref = REFS["F7_HIST"][0]; bench_src = "bench-P 缺/无效，回退历史 F7 %d %s" % (bench_ref, REFS["F7_HIST"][1])
    out["bench_ref"] = bench_ref
    r0b = b0s / bench_ref
    rep.info("臂 0 稳态 / bench 参考 = %.3f×（参考：%s）" % (r0b, bench_src))
    t = args.tol
    if r0b <= 1 + t:
        out["gap_class"] = "未复现"
        rep.info("差距未复现：臂 0 稳态已在 bench 同口径 ±%.0f%% 内 [L1] → 06-16 的 1.79× 在本次 run 上不存在（可能是当时的离群/冷帧或环境差）；-O 对照臂的「消失/缩小」无从谈起。下一步：把本次臂 0 min/last/max 与 06-16 记录并列写 DEC 行，请 CTO 裁是否以本次稳态为新基线；B1 门按臂 0 WCET 判。" % (t * 100))
        return out
    if not valid.get("B63.A1"):
        rep.unj("臂 A'（B63.A1）无效或未回填 → 零成本假设不可判；B6.3 无结论 → B1 继续挂起（D4）"); return out
    ev = get(cfg, "B63.A1", "o_evidence")
    stA = steady(cfg, "B63.A1", rep, args)
    if stA is None:
        rep.unj("臂 A' 稳态不可判 → 零成本假设不可判；B6.3 无结论 → B1 继续挂起（D4）"); return out
    a1s, a1m, _ = stA
    out["opt_max"] = a1m; out["opt_steady"] = a1s
    rA0 = a1s / b0s; rAb = a1s / bench_ref
    rep.info("臂 A'（Debug + -O，凭证 %s）：稳态 %d / WCET %d；A'/臂0 = %.3f；A'/bench = %.3f；WCET 余量 %.3f×，到 1.5× 线 %+d cyc" % (ev, a1s, a1m, rA0, rAb, bud / a1m, ln - a1m))
    # 完备划分：rA0 > 1+t 反常 | |rA0-1| ≤ t 不变 | rA0 < 1-t → (rAb ≤ 1+t 消失 / 否则 部分缩小)
    if rA0 > 1 + t:
        out["anomalous"] = True
        rep.major("反常：-O 后稳态 beam 上升 %.1f%% → 读数可疑：核指纹/宏残留/首帧冷/音源；不入账，重测；B6.3 无结论，B1 挂起" % ((rA0 - 1) * 100))
    elif abs(rA0 - 1) <= t:
        out["gap_class"] = "不变"
        rep.major("差距不变：-O 前后稳态在 ±%.0f%% 内 [L1] → 假设 b 排除（前提：-O 凭证 %s 真实且指纹一致）。差距在核侧编译之外——FIRA 驱动/中断/DMA/放置/时钟。下一步：三段归因（§2.4）；臂 A''/B 旁证系统库；排查表 #2/#3/#4/#15；仍无法归因 → 按 DEC-S7-RULINGS-02 另行申请内拆分副本。B1 基线仍臂 0。" % (t * 100, ev))
    elif rAb <= 1 + t:
        out["gap_class"] = "消失"
        rep.ok("差距消失：臂 0 稳态确有 %.2f× 差距，-O 后回收 %d cyc（%.1f%%）且落到 bench 同口径 ±%.0f%% 内 [L1] → 差距主因 = 优化等级（假设 b 成立 [L1]）。下一步：CTO 裁产品 build 是否改带 -O（改二进制 → M2 板门 + 八锚自检重跑）；新基线候选 = 臂 A'（无括号臂）；排查表其余项降非阻塞；B1 若用 -O 基线须 CTO 明示采纳（--use-optimized-baseline）。" % (r0b, b0s - a1s, (1 - rA0) * 100, t * 100))
    else:
        out["gap_class"] = "部分缩小"
        rep.info("差距部分缩小：-O 回收 %d cyc（%.1f%%），但 A'/bench 仍 %.3f > 1+%.0f%% [L1] → 优化等级是成因之一、非全部。下一步：三段占比归因（§2.4）定位剩余份额；排查表 #2（Debug 系统库，臂 A''）/#3（放置）/#4（自旋）/#15（时钟）；B1 启动口径用 A' 基线但须 CTO 明示。" % (b0s - a1s, (1 - rA0) * 100, rAb, t * 100))
    return out

def segment_shares(cfg, sec, rep, board, reads_ref, args):
    try:
        w = get(cfg, sec, "seg_w_cyc_last", "int"); a = get(cfg, sec, "seg_ana_cyc_last", "int"); s = get(cfg, sec, "seg_syn_cyc_last", "int")
        bl = get(cfg, sec, "beam_cyc_last", "int"); tx = get(cfg, sec, "seg_tx_cyc_last", "int") if board else 0
        rc = get(cfg, sec, "ccnt_read_cyc", "int", required=False) if not board else None
    except Missing as m:
        rep.unj("%s 三段缺回填：%s" % (sec, m)); return None
    tot = w + a + s + tx; ovh = bl - tot
    ovh_tol = max(args.ovh_tol_frac * bl, args.ovh_tol_cyc)
    note = "；bench ovh 参考 ≈ 1–2 × ccnt_read_cyc=%d" % rc if rc else ""
    rep.info("%s 三段（last，同帧）：w=%d ana=%d syn=%d%s → 和=%d，beam_last=%d，ovh=%d（读扰动参考 %d 次/帧%s；ovh 容差 max(%.0f%%·beam, %d cyc [L4])）"
             % (sec, w, a, s, (" tx=%d" % tx) if board else "", tot, bl, ovh, reads_ref, note, args.ovh_tol_frac * 100, args.ovh_tol_cyc))
    if ovh < 0 or ovh > ovh_tol:
        rep.major("%s 三段之和与 beam_last 不恒等（ovh=%d 超容差）→ 括号口径/同帧性存疑，本节占比不入账、不归因" % (sec, ovh)); return None
    shares = {k: v / tot * 100 for k, v in (("w", w), ("ana", a), ("syn", s), ("tx", tx))}
    return dict(w=w, ana=a, syn=s, tx=tx, tot=tot, beam_last=bl, shares=shares)

def attribute_segments(cfg, rep, args, valid, bench_ok):
    rep.h("三段归因（板上 vs bench，绝对 cyc 与占比；§2.4）")
    if not bench_ok:
        rep.unj("bench-P 无效/未回填 → 三段归因不可做"); return
    board = None; src = None
    for sec in ("B63.As", "SB.B1"):
        if has(cfg, sec) and valid.get(sec):
            board = segment_shares(cfg, sec, rep, True, REFS["SEG_READS_BOARD"][0], args); src = sec
            if board: break
    if not board:
        rep.unj("板上三段无有效回填（B63.As 或 SB.B1 需指纹/板门全绿且恒等式成立）→ 归因不可做"); return
    if src == "SB.B1": rep.info("板上三段取自 SB.B1（Debug 无 -O 的 0s 臂）；B63.As 未回填或无效")
    bench = segment_shares(cfg, "BENCH.P", rep, False, REFS["SEG_READS_BENCH"][0], args)
    if not bench: return
    ratios = {}; dshare = {}
    for seg in ("w", "ana", "syn"):
        ratios[seg] = board[seg] / bench[seg] if bench[seg] else float("inf")
        dshare[seg] = board["shares"][seg] - bench["shares"][seg]
        rep.info("%s：板 %d vs bench %d → 板/bench = %.2f×；占比 板 %.1f%% vs bench %.1f%%（Δ %+.1f 点）" % (seg, board[seg], bench[seg], ratios[seg], board["shares"][seg], bench["shares"][seg], dshare[seg]))
    if board["tx"]:
        rep.info("tx（M2 独有）：%d cyc = 板上 %.1f%%（bench 无此段，属 M2 固有开销，不计入差距归因）" % (board["tx"], board["shares"]["tx"]))
    over = [s for s in ("w", "ana", "syn") if ratios[s] > 1 + args.tol]
    if not over:
        rep.ok("三段板/bench 均在 ±%.0f%% 内 → 差距不在这三段的核侧/FIRA 调用里；剩余差 = tx 段 + ISR + 括号扰动 → 看 ovh 与 cb_cyc_max" % (args.tol * 100)); return
    rmax = max(ratios.values()); rmin = min(ratios.values())
    top = max(("w", "ana", "syn"), key=lambda s: ratios[s]); top_share = max(("w", "ana", "syn"), key=lambda s: dshare[s])
    if len(over) == 3 and rmax / rmin <= 1 + args.tol:
        rep.info("三段等比放大（%.2f–%.2f×）→ 全局成因（优化等级、时钟、cache/放置对所有代码一视同仁）；结合 §2.3：已消差 → 优化等级；否则 #15 时钟（g_m2_cclk_hz 对照，CTO-gated）与放置" % (rmin, rmax)); return
    if top == top_share:
        seg = top
        if seg in ("ana", "syn"):
            rep.info("%s 段独大（比值最大 %.2f× 且占比 Δ 最大 %+.1f 点）→ FIRA 路径：驱动 debug 变体（#2，臂 A''/B 旁证）、FIR DONE 中断延迟/自旋（#4）、DMA scratch 放置与乒乓争用（#3）、中断抢占（#6）" % (seg, ratios[seg], dshare[seg]))
        else:
            rep.info("w 段独大（%.2f×，占比 Δ%+.1f 点）→ 纯核侧循环：优化等级（-O）、权重表/缓冲放置（Block 0 争用 #3）、链式读扰动（33 vs 25 次）" % (ratios[seg], dshare[seg]))
    else:
        rep.info("放大不等比且无单段独大（比值最大 %s %.2f×，占比增最多 %s %+.1f 点）→ 全局成因与 FIRA 路径成因叠加；先按 §2.3 排除优化等级，再用臂 A''/B 与 #15 拆" % (top, ratios[top], top_share, dshare[top_share]))

# ---- B1 启动条件 -------------------------------------------------------------------------------
def b1_gate(cfg, rep, gap, st_ok, ng_ok, valid, args, clk, bench_cclk=None):
    rep.h("B1 启动条件（D4：B1 算本轮实施但卡 B6.3 结论；口径 = 墙钟 WCET；§3）")
    if not clk["ok"]:
        rep.info("条件 0 未满足：M2 实测 CCLK 未回填/未解出 → 帧预算与 1.5× 线无 [L1] 依据（CTO 2026-09-03 裁定：不设旗位放行）→ **B1 挂起**")
        return "挂起"
    rep.info("条件 0 满足：帧预算 %d / 1.5× 线 %d，由实测 CCLK %d Hz 重算 [L1/EZKIT 寄存器解码]" % (clk["budget"], clk["line"], clk["cclk"]))
    if bench_cclk is not None and bench_cclk != clk["cclk"]:
        rep.blocker("bench-P 读回 CCLK=%d 与 M2 实测解码 %d **不一致** → 两工程不同频或读法有误；忙等段与全部差距须先按时钟比折算（排查表 #15）→ B1 挂起" % (bench_cclk, clk["cclk"]))
        return "挂起"
    pending = []
    if gap.get("gap_class") == "未复现":
        pending.append("未复现：CTO 裁本次臂 0 稳态是否为新基线")
    if gap.get("hist_mismatch"):
        pending.append("臂 0 WCET 与 06-16 历史差 > tol 未解释")
    if gap.get("anomalous"):
        rep.info("§2.3 为反常 → B6.3 无结论 → B1 继续挂起"); return "挂起"
    if not gap.get("gap_class"):
        rep.info("B6.3 无结论（臂 0/A' 无效或未回填）→ B1 继续挂起"); return "挂起"
    if not (st_ok and ng_ok):
        rep.info("数值门未建立（B1 自检未 8/8 PASS 或负控制未 rc=7，或其 build 已作废）→ B1 继续挂起"); return "挂起"
    if rep.bad_secs & {"SB.B0", "SB.B1", "SB.B2"}:
        rep.info("S-B 基座某 build 有 BLOCKER → B1 继续挂起"); return "挂起"
    use_opt = bool(args.use_optimized_baseline and gap.get("opt_max") and valid.get("B63.A1") and gap.get("gap_class") in ("消失", "部分缩小"))
    if args.use_optimized_baseline and not use_opt:
        rep.info("--use-optimized-baseline 已指定但臂 A' 无效/缺，或 §2.3 不是消失/部分缩小 → 退回臂 0 基线")
    base = gap["opt_max"] if use_opt else gap["base_max"]
    which = "臂 A'（Debug + -O；须 CTO 明示采纳 -O 产品配置，且改二进制后 M2 板门 + 八锚重跑）" if use_opt else "臂 0（Debug 现状）"
    lo, hi = REFS["B1_LO"][0], REFS["B1_HI"][0]
    bud, ln = clk["budget"], clk["line"]
    to_line = ln - base
    rep.info("基线 = %s WCET beam_cyc_max=%d [L1]；余量 %.3f×；到 1.5× 线 %+d cyc；B1 估算 %d [L3] .. %d [L4]；gap=%s" % (which, base, bud / base, to_line, lo, hi, gap["gap_class"]))
    suffix = ("（待 CTO：" + "；".join(pending) + "）") if pending else ""
    if bud / (base + hi) >= REFS["T2_RATIO"][0]:
        rep.ok("B1 可启动%s：高端估计 %d 也在 1.5× 线内（启动后余量 %.3f×）。口径 = 墙钟 WCET；实施后用 EQ-on/off 的 beam_cyc 差替代估算 [L1]；仍须 CTO 批 D2/D3/D4 与本报告。" % (suffix, hi, bud / (base + hi))); return "可启动" + suffix
    if bud / (base + lo) >= REFS["T2_RATIO"][0]:
        rep.major("B1 刀刃%s：低端 %d 在线内、高端 %d 越线（启动后余量 %.3f×..%.3f×）→ 只能以「实测后若越线即回退」为条件启动，须 CTO 明示；若 §2.3 为消失/部分缩小且 CTO 采纳 -O 基线，用 --use-optimized-baseline 重算" % (suffix, lo, hi, bud / (base + hi), bud / (base + lo))); return "刀刃" + suffix
    rep.blocker("B1 挂起：连低端估计 %d 都越 1.5× 线（余量 %.3f×）→ 触发冻结令解冻条件；B1 不启动，先按 §2.3/§2.4 归因回收" % (lo, bud / (base + lo))); return "挂起"

# ---- 批 4：极性 QA -----------------------------------------------------------------------------
def polqa(cfg, rep):
    rep.h("批 4：自家阵列极性 QA（S7_POLARITY_QA_RUNBOOK.md §3/§4；D8：实测映射 = s_m2_chmap 唯一依据）")
    try:
        a = get(cfg, "POLQA", "stepA_status"); und = get(cfg, "POLQA", "stepA_undetermined")
        b = get(cfg, "POLQA", "stepB_status"); opp = get(cfg, "POLQA", "opposite_channels")
        weak = get(cfg, "POLQA", "weak_channels"); unclear = get(cfg, "POLQA", "unclear_pairs")
        chg = get(cfg, "POLQA", "lines_changed", "yesno"); rev = get(cfg, "POLQA", "reverified_after_change")
        mapping = get(cfg, "POLQA", "mapping"); ident = get(cfg, "POLQA", "mapping_identity", "yesno")
        rec = get(cfg, "POLQA", "record_file")
    except Missing as m:
        rep.unj("极性 QA 缺回填：%s → 不入库、不判；后续任何声学测试不得开始" % m); return None
    ok = True
    if a != "complete":
        rep.major("Step A 状态=%s（未定喇叭：%s）→ 逐只极性未定论；Step B 只能给通道级结论；升级 CTO" % (a, und)); ok = False
    if chg and rev.lower() != "yes":
        rep.major("改过线（lines_changed=yes）但未复测（reverified=%s）→ 改线后该路 Phase A solo + Phase B 三项必须重测（runbook §3 第 5 行）" % rev); ok = False
    if opp.lower() != "none":
        if chg and rev.lower() == "yes":
            rep.ok("Phase B 曾判 OPPOSITE（通道 %s）→ 已按 §3 第 4 行改线并复测 → 记入 %s §2.6 与 decisions_log；改线记录须含哪只/哪端/时间" % (opp, rec))
        else:
            rep.blocker("Phase B 判 OPPOSITE（通道 %s）但未改线或未复测（lines_changed=%s, reverified=%s）→ 阵列极性未统一，一切声学测试停" % (opp, chg, rev), "POLQA"); ok = False
    if weak.lower() != "none":
        rep.major("Phase A 弱/趋零通道 %s → 回 Step A 复核该路两只 + A2 接线；未闭合前该路极性不定论" % weak); ok = False
    if unclear.lower() != "none":
        rep.major("Phase B 分不清的对 %s → 挪麦/换参考路重测；仍分不清记录上报，不硬判" % unclear); ok = False
    if b != "pass":
        rep.major("Step B 状态=%s → 通道级复验未 PASS，不得写「极性 QA 已做」进 R10 第 8 项" % b); ok = False
    pairs = [p.strip() for p in mapping.replace(";", ",").split(",") if p.strip()]
    rep.info("实测映射（%d 路）：%s" % (len(pairs), "，".join(pairs)))
    if len(pairs) != 8: rep.major("映射表不是 8 路（%d）→ 映射不完整，不能作 s_m2_chmap 依据" % len(pairs)); ok = False
    if ident:
        rep.ok("映射与约定 {c,15-c} 一致（恒等）→ D8：M2_CHMAP_FIX 对自家阵列保持关闭，P1 只做 A 臂=现状；DEC-S6-TEST1-METHOD-01 无冲突")
    else:
        rep.major("映射 ≠ 约定 → 把实测映射换算成 s_m2_chmap 值写进记录 §3，仍不翻宏，P1 远场 A/B 后由 CTO 逐次裁定；同时触发铁律四对 DEC-S6-TEST1-METHOD-01 的强制重审")
    rep.info("入库：%s（R10 卡 + A1/A2/B1/B2 原值 + 映射表 + L 标结论：逐只 [L1 机械位移法]、通道级 [L1]、映射 [L1]、未做项写「未记录」）→ 独立 critic → CTO → decisions_log 行" % rec)
    return ok

# ---- 主流程 -------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ini", nargs="?", help="回填文件（INI）")
    ap.add_argument("--schema", action="store_true", help="打印空白回填模板")
    ap.add_argument("--tol", type=float, default=0.05, help="墙钟/段比容差（比例，工作假设 [L4]，默认 0.05）")
    ap.add_argument("--rxpoll-tol", type=float, default=0.01, help="rx≈poll 容差（比例 [L4]，默认 0.01）")
    ap.add_argument("--overrun-tol", type=float, default=0.001, help="overrun 允许比例（[L4]，默认 0.001 × rx）")
    ap.add_argument("--full-scale-near", type=lambda x: int(x, 0), default=0x7F000000, help="out_max_abs 视为顶满幅的阈值（[L4]，默认 0x7F000000）")
    ap.add_argument("--ovh-tol-frac", type=float, default=0.05, help="三段恒等式 ovh 容差（比例 [L4]，默认 0.05）")
    ap.add_argument("--ovh-tol-cyc", type=int, default=2000, help="三段恒等式 ovh 容差下限（cyc [L4]，默认 2000）")
    ap.add_argument("--use-optimized-baseline", action="store_true", help="B1 门用臂 A'（-O）基线（须 CTO 明示采纳 -O 产品配置；仅 §2.3 为消失/部分缩小时生效）")
    args = ap.parse_args()
    if args.schema:
        print(schema_text()); return 0
    if not args.ini:
        ap.print_help(); return 2
    cfg = configparser.ConfigParser(inline_comment_prefixes=(";",), interpolation=None)
    cfg.optionxform = str
    if not cfg.read(args.ini, encoding="utf-8"):
        print("cannot read", args.ini); return 2
    anchors, f4 = load_anchors()
    rep = Report()
    rep.lines.append("# S7 板测结果判读（自动初筛，非裁定；脚本 %s；容差 tol=%.2f [L4]）" % (VERSION, args.tol))
    rep.lines.append("帧预算与 1.5× 线由 [CLK] 实测 CGU 寄存器解码重算（未回填 → 条件 0 未满足 → B1 挂起）；参考值 %d / %d 由 1e9 %s 得出，只作对照；八锚运行时解析 %s；口径：差距=稳态 min（B63 §6，last 须一致），B1 余量=WCET max" % (FRAME_BUDGET_REF, T2_LINE_REF, REFS["CCLK_HZ"][1], os.path.relpath(GOLDEN_H, ROOT)))
    try:
        rep.info("meta：日期 %s，测试员 %s，commit %s，源码干净=%s" % (get(cfg, "meta", "date"), get(cfg, "meta", "tester"), get(cfg, "meta", "commit"), get(cfg, "meta", "git_status_clean")))
    except Missing as m:
        rep.unj("meta 缺 %s" % m)
    valid = {}
    clk = decode_cclk(cfg, rep, args)
    rep.h("批 1：S-B 四个 build（指纹 → 板门/.map → 自检）")
    for sec in ("SB.B0", "SB.B1", "SB.B2", "SB.B3"):
        if not has(cfg, sec):
            rep.unj("%s 整节未回填" % sec); valid[sec] = False; rep.bad_secs.add(sec); continue
        fp = check_fingerprints(cfg, sec, rep)
        valid[sec] = bool(fp and check_board_gate(cfg, sec, rep, args, m2=(sec != "SB.B3")))
    st_ok = check_selftest(cfg, "SB.B1", rep, anchors, f4, negctrl=False) if valid.get("SB.B1") else None
    ng_ok = check_selftest(cfg, "SB.B2", rep, anchors, f4, negctrl=True) if valid.get("SB.B2") else None
    if st_ok is None: rep.unj("B1 自检不可判（其 build 无效或未回填）")
    if ng_ok is None: rep.unj("B2 负控制不可判（其 build 无效或未回填）")
    if st_ok is False: valid["SB.B1"] = False
    if ng_ok is False: valid["SB.B2"] = False
    rep.h("批 2：B6.3 对照臂（臂 0 = SB.B0；A' = B63.A1；As / A'' / B 可选）")
    for sec in ("B63.A1", "B63.As", "B63.A2", "B63.B"):
        if not has(cfg, sec):
            valid[sec] = False; continue
        fp = check_fingerprints(cfg, sec, rep)
        gate = fp and check_board_gate(cfg, sec, rep, args, m2=True)
        extra = True
        if sec in ("B63.A1", "B63.As", "B63.A2"):
            ev = get(cfg, sec, "o_evidence", required=False)
            if not ev: rep.blocker("%s 缺 -O 编译凭证（Console 编译行截图）→ 该臂不入账" % sec, sec); extra = False
        if sec == "B63.A2":
            if not get(cfg, sec, "debuglib_unchecked_evidence", required=False): rep.major("%s 缺「取消 Debug 系统库」凭证 → 单变量证据不成立" % sec); extra = False
        if sec == "B63.B":
            co = get(cfg, sec, "cproject_checked_out", "yesno", required=False)
            if not co: rep.major("%s 未确认 .cproject/.project 已 checkout → 治理硬约束（不动 .cproject）未闭合，臂 B 读数暂不入账" % sec); extra = False
        valid[sec] = bool(gate and extra)
    rep.h("批 3：bench 探针（BENCH.P）")
    if has(cfg, "BENCH.P"):
        bench_ok = check_bench(cfg, rep, anchors, clk)
    else:
        rep.unj("bench 探针未回填 → 三段归因不可做，差距只能用历史 F7 参考"); bench_ok = False
    rep.h("批 2：墙钟差距分类（§2.3；稳态 min；参照划分：A'/臂0 > 1+t 反常｜|A'/臂0−1| ≤ t 不变｜A'/臂0 < 1−t → A'/bench ≤ 1+t 消失，否则部分缩小）")
    gap = classify_gap(cfg, rep, args, valid, bench_ok, clk)
    attribute_segments(cfg, rep, args, valid, bench_ok)
    bench_cclk = None   # 条件 0 的 [L1] 否定不受 bench FG 有效性豁免：g_s7_cclk_hz 是时钟查询，与探针 FG 无关
    if has(cfg, "BENCH.P") and get(cfg, "BENCH.P", "cclk_rc", "int", required=False) == 0:
        bench_cclk = get(cfg, "BENCH.P", "cclk_hz", "int", required=False)
    b1 = b1_gate(cfg, rep, gap, bool(st_ok), bool(ng_ok), valid, args, clk, bench_cclk)
    if has(cfg, "POLQA"):
        pq = polqa(cfg, rep)
    else:
        rep.unj("POLQA 节未回填 → 声学测试不得开始"); pq = None
    rep.h("汇总")
    rep.lines.append("- BLOCKER %d / MAJOR %d / 不可判 %d；无效节：%s；实测 CCLK = %s；B1 = %s；极性 QA = %s" % (
        rep.blockers, rep.majors, rep.unjudged, sorted(rep.bad_secs) or "无",
        ("%d Hz（帧预算 %d / 线 %d）" % (clk["cclk"], clk["budget"], clk["line"])) if clk["ok"] else "**未回填/未解出 → 条件 0 未满足**", b1,
        {True: "PASS 可入库", False: "未闭合（一切声学测试停；不影响 B1 固件侧实施）", None: "不可判"}.get(pq)))
    rep.lines.append("- 本报告是初筛：任何「结论」须经独立 critic + CTO 常识审后才进 decisions_log；数字全部为测试员回填原值 [L1/EZKIT]，本脚本不生成任何板上数字。")
    print(rep.text())
    return 1 if rep.blockers else (2 if rep.unjudged else 0)

if __name__ == "__main__":
    sys.exit(main())
