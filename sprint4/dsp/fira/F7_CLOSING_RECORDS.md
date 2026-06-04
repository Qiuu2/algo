# F7 CLOSING RECORDS DRAFT — answers to CTO's 3 questions + closing-record drafts

> DRAFT ONLY. Not committed; independent critic gates first, then lead commits.
> All board values [L1/EZKIT, CTO-measured 2026-06-04]. Source citations file:line. Arithmetic [L1-derived] or [L3] as marked.

---

## Q1 — FIRA analyze/synth split: the splits EXIST. CTO's "hardware-integrated, no split" is CONTRADICTED by source. It is a CCES READ-SIDE problem, the data is NOT lost.

**Source proof the splits exist and were written this run:**
- Definitions, identical storage class, adjacent lines: `fira_regression.c:500-502`
  - `volatile uint32_t g_f7_cyc_1ch_fira    = 0u;`
  - `volatile uint32_t g_f7_cyc_analyze_fira = 0u;`
  - `volatile uint32_t g_f7_cyc_synth_fira   = 0u;`
- Externs in bench_main.c, identical form: `bench_main.c:85-87`.
- All three WRITTEN in the same code block, same scope, same run: `fira_regression.c:643` (`g_f7_cyc_analyze_fira = t5 - t4;`), `:647` (`g_f7_cyc_synth_fira = t5 - t4;`), `:648` (`g_f7_cyc_1ch_fira = g_f7_cyc_analyze_fira + g_f7_cyc_synth_fira;`).
- **No #if-guard difference** between the three (all under the one `FIRA_USE_REAL_ADI_FIR_HEADER && TARGET_SHARC` block; verified 495-503). Same `volatile` storage class -> **no linker-elimination difference** (and `1ch_fira` is itself "written-but-the-product-of-two-writes" — if linker elimination applied it would hit `1ch_fira` too; it read fine).

**Decisive logical point:** `g_f7_cyc_1ch_fira = 56,616` read FINE, and line :648 computes it as the LITERAL SUM `analyze_fira + synth_fira`. A non-zero `1ch_fira` PROVES both addends were computed and stored on the board. **So the analyze/synth values are physically in memory — this is a CCES Expressions DISPLAY/read failure, not a missing measurement and not hardware integration.** The FIRA Legacy path is software-orchestrated per-segment (CreateTask/QueueTask/spin), so "hardware integrated, no split" is also wrong on the mechanism: analyze and synthesize are separate `fira_tfb_analyze`/`fira_tfb_synthesize` calls (`:641` / `:645`).

**Why two globals ERROR while `1ch_fira` reads fine — the candidate causes, ranked:**
1. **Symbol-name typo in the Expressions watch** (most likely). The two failing names contain a word
   suffix (`_analyze_fira` / `_synth_fira`) vs the short `_1ch_fira`. Exact spellings to paste VERBATIM:
   - `g_f7_cyc_analyze_fira`
   - `g_f7_cyc_synth_fira`
   (note: `synth` NOT `synthesize`; `analyze` NOT `analyse`/`analyzed`; all lowercase, single underscores.)
2. **Scope/translation-unit qualification** — if CCES resolved `1ch_fira` from the bench_main extern but
   the other two from a different scope guess, qualify with the defining TU or use the global file-scope
   symbol directly (they are file-scope globals in fira_regression.o).
3. NOT a guard/storage/link cause (ruled out above).

**Retry instruction for CTO (free, one read):** in CCES Expressions add exactly `g_f7_cyc_analyze_fira`
and `g_f7_cyc_synth_fira` (copy the spellings above). If still ERROR, read them via the Memory browser at
their addresses (they sit adjacent to `g_f7_cyc_1ch_fira` in `.bss`, defined consecutively :500-502), or
read the structure-of-three as a uint32[3] starting at `&g_f7_cyc_1ch_fira`.

**Cross-check that 56,616 is internally consistent [L1-derived]:** `8 x 56,616 = 452,928` vs the measured
8ch `463,273` -> per-frame FIXED share = **10,345 cyc/frame = 2.23%**. This is small and consistent with 8
sequential single-channel iterations (the 8ch span IS 8x the 1ch loop, `fira_regression.c:612-617`), i.e.
the per-channel cost is ~flat and there is only a ~2% per-frame fixed overhead outside the per-channel work.

**Recoverable? YES, cheaply (one corrected read).** If the retry succeeds, `g_f7_cyc_analyze_fira` lands
(expected ~37.5k (66% of 56,616) per §7B) and the **16ch convention estimate upgrades [L3] -> [L1-derived]** (1.72-1.74x).
**If NOT recoverable:** the 16ch core-style estimate STAYS [L3] (it needs `analyze_fira`); nothing else is
lost — the 8ch margin (2.878x), the speedup (Q2), and the 2.23% fixed-share are all already L1-derived
from `1ch_fira` + `8ch_fira`, which read fine.

---

## Q2 — Official speedup ruling (from measurement methodology)

**RULING: official net FIRA speedup = 3.07x [L1-derived]** (`g_f7_cyc_8ch_core / g_f7_cyc_8ch_fira =
1,420,543 / 463,273 = 3.0663x`).

**Reasoning (methodology, source-cited):**
- (a) **In-build 1,420,543 -> 3.07x is the methodologically CLEAN speedup.** Both numerator and denominator
  were measured in the SAME build, on the SAME frame, with the SAME input preparation (per-channel
  `f5_apply_w` weighting) and the SAME loop structure (manual 8x per-channel loop) — only the inner kernel
  differs (FIRA `fira_tfb_*` at :615-616 vs core `tfb_*` at :626-627). That is a controlled A/B: everything
  except the unit-under-test is held constant. This is the speedup to report. **[L1-derived]**
- (b) **Core-only 1,451,030 -> 3.13x is RETIRED as the speedup** because it mixes builds/inputs/loops:
  it is unweighted, goes through the `tfb8_process` wrapper (`bench_harness.c:118`), and was measured in a
  DIFFERENT build (core-only). It is a valid number for ITS OWN purpose (below), but as a speedup ratio it
  confounds the kernel change with build/wrapper/weighting differences.
- **1,451,030 is RETAINED as the core-path DEMAND number** for the core-only margin (0.92x, F7_MARGIN_MATERIAL
  v1): it is the cycle cost of `tfb8_process`, the path the PRODUCT would actually run WITHOUT FIRA. So:
  - **Speedup (FIRA vs core, clean A/B): 3.07x [L1-derived]** (use 1,420,543).
  - **Core-only realtime demand / margin: 1,451,030 cyc -> 1088.66 MCPS -> 0.92x** (use 1,451,030, product path).
  - **3.13x: retired** (mixed-build artifact; documented in the anomaly trail, not cited as the speedup).

**Three-layer consistency cross-validation [L1-derived] — strengthens the ruling:**
- in-build 8ch: `1,420,543 / 463,273 = 3.07x`
- 1ch (c=7 unity): `179,882 / 56,616 = 3.18x` (179,882 = core 1ch analyze+synth = 119,116+60,766, confirmed)
- (mixed 8ch, for reference only: 3.13x)
The clean-comparison layers (3.07x, 3.18x) agree within ~3.6%, consistent with the ~2% per-frame fixed
share (Q1) diluting the 8ch ratio slightly below the 1ch ratio. **The speedup is robustly ~3.1x; the
official single value is 3.07x (same-build A/B).**

---

## Q1-supplement — why is the manual weighted loop (1,420,543) ~2% FASTER than the unweighted `tfb8_process` (1,451,030)? [L3, reasoned from source]

The result is counter-intuitive (it adds 512 `f5_apply_w` weighting ops yet runs ~30,487 cyc / 2.1% LESS).
My §7A band predicted slightly HIGHER and was WRONG on direction+magnitude. Honest source-based reasons,
most-to-least likely:

1. **Wrapper call/struct-indirection overhead in `tfb8_process` (likely dominant).** The core-only path
   calls `tfb8_process(&st8, s_in8, ...)` once (`bench_harness.c:118`), which internally iterates 8 channels
   through the `Tfb8State` struct (`ana[8]`/`syn[8]`, tfb_8ch.h) — extra struct member indirection, an
   internal per-channel dispatch, and a 2D input array `s_in8[c][i]` (`bench_harness.c:115`, strided
   access). The F7 manual loop (`fira_regression.c:623-628`) calls `tfb_analyze`/`tfb_synthesize` DIRECTLY
   on a flat `f7_ca[c]` with a flat `xw[]` buffer — fewer indirections, simpler addressing. On SHARC,
   addressing-mode and pointer-setup cycles are non-trivial; saving them across 8ch x per-frame can exceed
   the 512 cheap weighting MACs (a 64-bit mult + shift is a few cycles, ~1.5-5k total << 30k).
2. **Cache/layout: `st8` (one ~37 KB monolithic struct) vs `f7_ca[8]` (array of per-channel structs).**
   Different L1 cache-line behavior; the per-channel-contiguous `f7_ca[c]` may have better locality per
   channel iteration than the interleaved `Tfb8State` layout. Both are static (post-FIX2), but their
   placement/footprint differ -> different miss patterns. [L3, not measured]
3. **Input data path:** core-only reads `s_in8[c][i]` (a 2D array filled at `bench_harness.c:115`); F7 reads
   `xw[i]` (a flat 64-elem buffer rebuilt per channel). The flat buffer is smaller/hotter in cache.
4. **Same-frame vs separate measurement:** F7's core span runs right after its FIRA span on an already-warm
   core (`fira_regression.c:622`), maximally warm; core-only's was a standalone S3 block — marginally cooler.

**Net [L3]:** the ~2% is plausibly wrapper-indirection + cache-layout savings exceeding the small weighting
cost. It does NOT affect the ruling: 3.07x uses the in-build (clean) number precisely to avoid this
wrapper/build confound. The §7A miss is logged honestly (I predicted direction-agnostic but band-wrong;
the magnitude came from wrapper overhead I under-weighted).

---

## Q3 — Option (d) amortization: what CAN / CANNOT be estimated now

**CAN, now, from existing L1 reads:**
- **Per-frame FIXED share ~10,345 cyc/frame = 2.23%** (`463,273 - 8 x 56,616`, Q1). This is the portion of
  the 8ch frame NOT proportional to channel count -> the part that 16ch would NOT pay twice -> the (small)
  amortization headroom. [L1-derived]
- **Per-channel cost ~56,616 cyc** (1ch_fira) -> 16ch naive incremental ~ +8x57,909 (8ch per-ch) or via the
  convention formula (needs analyze_fira). [L1-derived for the per-channel base.]

**CANNOT, without more data — the orchestration-vs-MAC ratio INSIDE the 56,616:**
The 56,616 lumps (per channel, 9 FIRA segments): CreateTask + FixedPointEnable + QueueTask + spin +
postscale + cache-invalidate (orchestration) AND the actual FIR MACs. Splitting these is what tells us how
much LARGER FRAME would amortize. **This needs one of:**
- **(i) Recover the two split reads (FREE).** `analyze_fira` vs `synth_fira` gives the analyze/synth balance
  but NOT the orchestration-vs-MAC split directly; still, it pins the 16ch convention (Q1) and is zero-cost.
  Info gain: 16ch [L3]->[L1-derived]; modest amortization insight.
- **(ii) FRAME sweep 64->128->256 (CODE CHANGE + board runs).** Run F7 at FRAME=128/256 (the F7 code uses
  BENCH_FRAME; a sweep needs a parameterized rebuild — a code change, hence a critic gate). Expected info
  gain: HIGH — orchestration is ~constant per segment (fixed call count 72+24), MAC scales with window, so
  plotting cyc/sample vs FRAME directly reveals the orchestration intercept and the MAC slope -> the exact
  amortization curve and the FRAME at which FIRA's margin crosses any chosen threshold. Cost: code change +
  >=2 board runs + critic gate. Latency tradeoff: FRAME/fs (64->1.33ms, 128->2.67ms, 256->5.33ms), PRD-side.
- **(iii) Segment-level instrumentation (MORE INVASIVE).** Bracket each `fira_run_segment` (CreateTask vs
  QueueTask vs spin vs postscale) with CCNT reads. Highest fidelity (exact orchestration breakdown) but
  touches the measured path / FROZEN-adjacent code, larger diff, bigger critic surface. Cost: HIGH.

**No recommendation on whether to do any — feasibility + cost only:** (i) free now; (ii) medium effort, high
info, needs gate; (iii) high effort/invasive. Per C9 none of this is needed for the R14 ruling (the 8ch
margin and speedup are already L1-derived).

---

## DRAFT (a) — decisions_log row(s): F7 CLOSING entry

> For lead to append to `sprint2/docs/decisions_log.md` (F7 row / new DEC). Draft text:

```
## F7 CLOSING — R14 数据采集 COMPLETE (2026-06-04, board L1/EZKIT, FIRA build)

### DEC-S4-F7-CLOSE-01：R14 cycle/CCLK 数据采集完成（裁定权在 CTO，本条仅录数据）
- **板上 L1 数据全集 [L1/EZKIT, CTO 实测 2026-06-04, FIRA build 自由运行 idle 读]**：
  - 核路径(g_bench_result): crc32=0x90556BC7 / cyc_8ch_frame=1,451,030 / cyc_analyze_1ch=119,116 /
    cyc_synth_1ch=60,766 / mcps_8ch=1088.66（产品无-FIRA 核需求路径 tfb8_process）。
  - FIRA 8ch 全链(含全开销): g_f7_cyc_8ch_fira=463,273 cyc/frame。
  - in-build 核 8ch(同 build/同输入/同循环, f5_apply_w 加权 + 手写循环): g_f7_cyc_8ch_core=1,420,543。
  - 1ch FIRA(c=7 unity): g_f7_cyc_1ch_fira=56,616（=analyze+synth 字面和, fira_regression.c:648）。
  - CCLK: g_f7_cclk_hz=1,000,000,000 [L1] (g_f7_cclk_rc=0) → **G6 CLOSED**（核频不再假设, 实测 1GHz）。
  - 连续性门: g_f5_pass_all=1（8/8 子带逐位 PASS）/ g_fira_f4_crc=0x2E0D8C6E（==核 golden）。
- **官方加速比 = 3.07x [L1-derived]**（in-build 同 build A/B：1,420,543/463,273=3.0663；方法学最干净,
  控制了 build/wrapper/加权/循环变量）。三层一致性交叉验证：in-build 8ch 3.07x / 1ch 3.18x（179,882/56,616）
  收敛 ~3.1x（差 ~3.6% 由 2.23% 每帧固定份额稀释）。**3.13x（核-only 1,451,030/463,273）退役**=混 build 伪值。
- **8ch 实时裕量 = 2.878x [L1-derived]**（1000 MCPS / 347.45 MCPS；分子分母均 L1：cclk 实测 1e9 +
  需求 463,273×750/1e6；1GHz datasheet 假设已退役换 L1 实测）。核-only 裕量 0.92x（1,451,030 产品核路径）。
- **16ch 状态**：参考性（R1 绑 8ch, DEC-S4-R1-8CH-01）。约定式估算 1.73x 待 g_f7_cyc_analyze_fira 读回升
  [L1-derived]；当前该全局 CCES Expressions 读 ERROR（疑符号名 typo/读侧, 非缺测——数据在板上, 见 §Q1
  retry）。未读回则 16ch 维持 [L3]；naive-2x 保守界 1.44x 始终可用。
- **异常解决留痕**：上轮 g_f7_cyc_8ch_core 报 1,451,030（与核-only 逐字节相等=可疑）→ 本轮实读 1,420,543
  （低 2.1%）→ 确诊上轮为 **转录替代**（误填核-only 值）。低 2% 方向：手写加权循环比 tfb8_process wrapper 快,
  疑 wrapper 间接寻址/struct/cache 开销 > 512 次 f5_apply_w 加权 [L3]。不影响裁定（3.07x 用 in-build 干净值）。
- **C9/铁律八仍约束**：FIRA 收益虽 L1 出处, 在 CTO 裁 R14 闭合前不进选型/承诺（C9 管 USE 非 provenance）。
- **R14 数据采集 = COMPLETE**；R14 闭合/判据/C9 松绑 = **裁定 PENDING CTO**。证据齐：F4/F5 逐位 [L1] +
  cycle 含全开销 [L1] + CCLK 实测 [L1]。判据(>=10x vs 实时floor+headroom) = CTO 政策选择, 见 ADDENDUM B
  残差裕量 1.38x-2.56x[L4]（5 未计入项）。
```

(Also: mark the existing decisions_log F7 row status 待板跑 -> ✅板跑完成·R14数据COMPLETE·裁定待CTO,
and the G6 entry -> CLOSED per the iface_survey change block in F7_R14_RULING_MATERIAL §2.)

---

## DRAFT (b) — F7_R14_RULING_MATERIAL.md reconciliation change blocks

**§1A (speedup) — replace the provisional grade with the ruled value:**

old:
```
`1,451,030 / 463,273 = 3.1321x`. **CTO's 3.132x CONFIRMED.** This is the net per-frame speedup of the
full 8ch FIRA path (incl. ALL orchestration overhead) vs the core 8ch path, at FRAME=64.
Grade: **[L1-derived, provisional pending the §1E re-read of `g_f7_cyc_8ch_core`]** — ratio of two
[L1/EZKIT] board cycle counts, but the denominator's build-identity is in question (see 1E).
```
new:
```
**OFFICIAL net speedup = 3.07x [L1-derived]** = `g_f7_cyc_8ch_core(in-build) / g_f7_cyc_8ch_fira`
= `1,420,543 / 463,273 = 3.0663x`. This is the same-build / same-input / same-loop A/B (only the kernel
differs: FIRA `fira_tfb_*` vs core `tfb_*`, fira_regression.c:615-616 vs :626-627) -- the methodologically
clean comparison. The earlier `1,451,030 / 463,273 = 3.13x` is RETIRED as a speedup (mixed build: unweighted
+ tfb8_process wrapper + core-only build); 1,451,030 is RETAINED only as the product core-only DEMAND
(0.92x margin). Cross-validation: 1ch speedup `179,882/56,616 = 3.18x` agrees within ~3.6% (dilution = the
2.23% per-frame fixed share, §1E/Q1). [L1-derived]
```

**§1E (exact-equal anomaly) — replace "ANOMALY/unresolved" with the resolution:**

old (heading + body asserting the suspected substitution):
```
### 1E. **EXACT-EQUAL CORE BASELINE — ANOMALY, MY EARLIER PREDICTION WAS WRONG, CRITIC WILL PROBE THIS**
...（全段：怀疑 transcription substitution，待 re-read 确认）
```
new:
```
### 1E. EXACT-EQUAL CORE BASELINE — RESOLVED (re-read 2026-06-04)
The in-build `g_f7_cyc_8ch_core` re-read = **1,420,543** [L1/EZKIT], NOT the 1,451,030 reported last
session. => the prior 1,451,030 was a **transcription substitution** of the core-only value (anomaly
RESOLVED). The true in-build core is **2.1% LOWER** than core-only (1,451,030), not higher as §7A's band
predicted -- the manual weighted F7 loop is ~2% faster than the unweighted `tfb8_process` wrapper, most
likely wrapper indirection / struct (`Tfb8State`) / cache-layout overhead exceeding the 512 cheap
`f5_apply_w` weighting ops [L3, see F7_CLOSING_RECORDS Q1-supplement]. IMPACT: the OFFICIAL speedup uses
this clean in-build value = 3.07x (§1A); the 2.878x realtime margin is unaffected (uses only
`g_f7_cyc_8ch_fira` + cclk). §7A prediction logged as direction-agnostic-but-band-wrong (honest miss).
```

**§7A / §7B (worksheet) — annotate with actual reads:**

§7A append:
```
ACTUAL (2026-06-04): `g_f7_cyc_8ch_core = 1,420,543` -> outcome was "resolved as substitution" but value
LOWER (1.4205M), outside the predicted 1.4525-1.4562M band (band assumed weighting ADDED cost; wrapper
overhead REMOVED more -> net lower). Speedup recompute -> 3.07x (§1A). Band-miss logged.
```
§7B append:
```
ACTUAL (2026-06-04): `g_f7_cyc_1ch_fira = 56,616` [L1] -> `8 x 56,616 = 452,928` vs `463,273` ->
per-frame fixed share = **10,345 cyc = 2.23%** (consistent, flat per-channel cost). BUT
`g_f7_cyc_analyze_fira` / `g_f7_cyc_synth_fira` read ERROR in CCES Expressions (suspected symbol-name /
read-side issue, NOT missing data -- `1ch_fira` is their literal sum at fira_regression.c:648 and read
fine, proving both were written). RETRY with exact spellings `g_f7_cyc_analyze_fira` /
`g_f7_cyc_synth_fira` or Memory-browser at `&g_f7_cyc_1ch_fira`+adjacent. Until recovered, the 16ch
convention estimate STAYS [L3] (it needs `analyze_fira`); naive-2x 1.44x conservative bound unaffected.
```

---

## What desktop CANNOT verify
- The corrected `analyze_fira`/`synth_fira` re-read (board globals) -- expectation only; if recovered, 16ch -> [L1-derived].
- The ~2% wrapper-vs-loop cause (§Q1-supplement) -- [L3] reasoned from source, not profiled on board.
- No SHARC toolchain/board here: board values taken as CTO-supplied [L1/EZKIT]; source citations file:line; arithmetic [L1-derived]/[L3] as labeled.
```
