/**
 * @file    golden_ref.h
 * @brief   内存向量法独立 golden（host 计算冻结，on-target 比对）—— 勿手改
 *
 * （2026-06-02 R14 修复：gen_golden 改读冻结 chirp_input.h；CRC 不变 0x90556BC7，
 *   证明冻结输入 ≡ 原 host chirp，golden 无需更新。详见 R14_bitexact_rootcause.md。）
 * 由 bench/gen_golden.c 在 host 跑参考单通道链（tree_verify 同源路径）导出：
 *   - GOLDEN_CRC32：全 65536 样本 int32 Q31 的 CRC32(IEEE 802.3)
 *   - GOLDEN_SPOT[64]：stride=1024 的逐位 spot 子集（紧凑覆盖，省 L1）
 *
 * ⚠️ 关键诚实标注（实测发现）：
 *   0.289 chirp(-6dBFS + -4.8dB headroom) 单通道**不触发饱和** → **SAT 与 UNSAT
 *   单通道输出逐字节相同**（两 build CRC 均 0x90556BC7）。故单通道 bit-exact 的
 *   sat/unsat 双套**比对同一 golden**：两 build 都能复现 = 核 MAC/滤波路径 bit-exact。
 *   饱和原语(sat_i64_to_i32/sat_add_i32)的 bit-exact 不被此输入覆盖（仅 8ch ~8x
 *   过载触发，见 bench_harness [D] 行为校验；过载无预算 golden = 覆盖缺口 GAP-SAT，
 *   低优先：饱和=简单钳位，S0-S1 host 已验，on-target 反汇编确认钳位指令即可）。
 */
#ifndef ITC_GOLDEN_REF_H
#define ITC_GOLDEN_REF_H
#include <stdint.h>

#define GOLDEN_NTOTAL   65536          /* FRAME 64 × 1024 帧 */
#define GOLDEN_NSPOT    64
#define GOLDEN_SPOT_STRIDE 1024

/* SAT==UNSAT（0.289 chirp 单通道不饱和，gen_golden 两 build 实测一致 2026-06-02） */
#define GOLDEN_CRC32    0x90556BC7u

static const int32_t GOLDEN_SPOT[GOLDEN_NSPOT] = {
0,197676176,-216529724,41199951,339640880,-619960150,33243234,588223571,
584959814,565734589,614924454,103060142,-590434049,618332136,-427145105,-528337611,
-451708671,-588712505,587523033,-518433361,-618994349,-66648897,-146787435,148669879,
-599606945,-265078802,-515298866,-532991814,325217500,556028019,900537,-463889900,
530454354,-560290029,605684055,343296513,615090389,-546012236,174585485,176291954,
58624323,517708849,-586386417,-415952860,-39489450,561879163,597995047,76630703,
534211910,338213295,595660907,557384424,-611917794,554935902,-589053883,-604094165,
618993255,540123072,57376116,-50927204,513060688,346667651,-416894434,449406412
};

#endif /* ITC_GOLDEN_REF_H */
