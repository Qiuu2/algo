# SIM PLAN — v1 On-Axis Focusing / Depth-Zoning Acoustic Efficacy Simulation

> PREREQUISITE #2 (CTO-ordered). Sprint 5 / efficacy_sim.
> Workflow role: **POLICY v1.8 三道关 = GATE 1 SCREENING ONLY**. Independent critic + CTO follow.
> **NO efficacy verdict in this workflow.** Produce METRICS only; sufficiency judgment belongs to CTO/PRD.
> All simulation outputs = **[L2/仿真]**; closed-form / geometry-only checks = **[L3]**.
> 铁律七 dual-track: **numpy primary + MATLAB R2026a independent implementation**, compared quantitatively.
> Author: acoustic-simulation teammate. Date: 2026-06-04.

---

## 0. The question this sim answers (state it plainly)

Does on-axis (broadside-normal) near-field **focusing / depth-zoning** deliver USEFUL acoustic
differentiation (focal gain, axial zone-depth isolation, cross-zone isolation) on the **LOCKED
geometry**, or is the v1 focusing premise **acoustically empty** at the product distances?

The honest core is a **physics gate**: focusing only produces a focal gain if the focal point F
lies inside the array's **near field**. Beyond the near-field (Fresnel/Rayleigh) limit, the array
already behaves as a far-field beamformer — applying "focusing" delays converges to the broadside
plane-wave solution and the focal gain -> 0 dB (premise empty there). So the sim must first compute,
per frequency, **at which (f, F) combos focusing is physically possible vs not**, then quantify the
gain only where it is possible.

---

## 1. LOCKED inputs (do NOT re-derive)

### 1.1 Geometry [L1/teardown + DEC-S3-GEOM-01]
- N = 16 elements, d = 55 mm, **acoustic aperture L = (N-1)*d = 825 mm**, vertical line array.
- Element positions (centered): `x_n = (n - (N-1)/2) * d`, n = 0..15, i.e. -0.4125 m .. +0.4125 m.
  - Box physical length N*d = 880 mm is NOT the aperture; all near-field/BW math uses **L = 825 mm**.
- Speed of sound c = 343.0 m/s (20 C), declared explicitly in both tracks.

### 1.2 HARD topology constraint [L1] — symmetric-only excitation
- **8 amplifier channels.** Channel c (c = 0..7) drives the symmetric PAIR {c, 15-c} **in series**.
  => any delay tau_c AND weight w_c applied to channel c hits **BOTH** element c and element 15-c
  **identically**. Only SYMMETRIC excitations are realizable.
- **On-axis focusing IS symmetric-compatible**: for a focal point F on the array's perpendicular
  bisector (the broadside-normal axis), element n and element 15-n are **equidistant** from F
  (r_n(F) = r_{15-n}(F)). So the focusing delay law naturally yields tau_n = tau_{15-n} — the 8
  free delay values map one-to-one onto the 8 channels with NO approximation. Built into the model.
- **Off-axis / lateral steering is NOT symmetric-compatible** — already ruled out (DEC-S3-DSP-03).
  This sim does on-axis focusing ONLY.

### 1.3 Channel weights [L2/dual-track, frozen F5-C] — READ, do not assume
Source: `sprint4/dsp/fira/dolph_w8_q15.csv` and `dolph_w8_q15.h` (Dolph-Chebyshev -20 dB, N=16,
center-symmetric taper; the 8 distinct half-aperture values). Channel c -> element PAIR {c, 15-c}:

| ch c | pair {c,15-c} | w_float (track-1 scipy chebwin) | w_q15 |
|------|---------------|----------------------------------|-------|
| 0 | {0,15} edge   | 0.8668296927388105 | 28404 |
| 1 | {1,14}        | 0.5043100646541281 | 16525 |
| 2 | {2,13}        | 0.6216704381816565 | 20371 |
| 3 | {3,12}        | 0.7333793765883259 | 24031 |
| 4 | {4,11}        | 0.8327331038598036 | 27287 |
| 5 | {5,10}        | 0.9135146112868511 | 29934 |
| 6 | {6,9}         | 0.9705186581255053 | 31802 |
| 7 | {7,8} center  | 1.0000000000000000 | 32768 (= DOLPH_W8_ONE, unity) |

- Taper is NON-monotonic (raised edge c=0 > c=1; characteristic Dolph behaviour, not an error).
- 16-element full weight vector = `[w0..w7, w7..w0]` (mirror reproduced PHYSICALLY by the A/B series
  pair, NOT in DSP). All distinct (FG1 distinctness), all <= 1.0.
- **Use the .csv float values for the sim**; the q15 column is the on-board fixed-point form (not
  needed for the acoustic field model, but recorded for traceability).
- Band of validity: **500 Hz - 6 kHz** (strong directivity degraded to <=6 kHz; grating lobes enter
  visible region at d>=lambda i.e. f >= c/d = 6236 Hz, the 6.2-8 kHz P0 zone, excluded here).

---

## 2. Physical model

### 2.1 Near-field spherical-wave (focused) field — the CORE model [L2]
Replace the far-field plane-wave array factor with an **exact near-field spherical-wave sum** so
that focal gain at finite distance is captured:

```
p(P) = sum_{n=0..15}  w_n / (4*pi*r_n)  *  exp( -j*k*( r_n - c*tau_n ) )
```
- `r_n = |P - x_n|`  = Euclidean distance from element n (at (0,0,x_n) along the column axis) to
  field point P. (2-D plane through the array axis is sufficient: axial coord z = on-axis distance,
  lateral coord y.)
- `k = 2*pi*f / c`.
- `w_n` = symmetric Dolph weight (section 1.3), `w_n = w_{15-n}`.
- `tau_n` = per-element focusing delay; under the topology constraint `tau_n = tau_{15-n}`
  (8 free values applied to pairs — symmetric constraint BUILT IN).
- The `1/(4*pi*r_n)` spherical spreading term is what makes near-field focusing have a real focal
  gain (closer elements contribute more); dropping it (far-field) is exactly why focusing vanishes
  far out.

### 2.2 Focusing delay law (on-axis focal point F)
For focal point F = (0, F_dist) on the broadside-normal axis:
```
r_n(F) = sqrt( x_n^2 + F_dist^2 )
tau_n  = ( r_n(F) - min_m r_m(F) ) / c      # non-negative delays; phase-aligns all elements at F
```
- `min_m r_m(F)` is the center-element distance (x ~ 0). Delays compensate the extra path of the
  edge elements so all 16 wavefronts arrive in phase at F.
- Symmetric automatically: r_n(F) = r_{15-n}(F) => tau_n = tau_{15-n}. The 8 channel delays =
  tau_0..tau_7 applied to pairs {c,15-c}. (No off-axis term — would break symmetry, excluded.)

### 2.3 Broadside-unfocused reference
`tau_n = 0 for all n` (the frozen F5-C broadside config). Same weights, no focusing delays.
This is the **baseline** against which focal gain is measured.

---

## 3. Near-field feasibility gate (THE honest core — compute, then report plainly)

Compute per frequency the array near-field / focusing limit and tabulate where focusing is even
physically possible. Aperture L = 0.825 m.

```
lambda = c/f ;  Fresnel-onset L^2/lambda ;  Rayleigh distance R = 2*L^2/lambda
```

**Pre-computed [L3, closed-form] (to be reproduced in-script, both tracks):**

| f (Hz) | lambda (m) | L/lambda | L^2/lambda (m) | Rayleigh 2L^2/lambda (m) |
|--------|-----------|----------|----------------|--------------------------|
| 500   | 0.6860 | 1.203  | 0.992  | 1.984  |
| 1000  | 0.3430 | 2.405  | 1.984  | 3.969  |
| 2000  | 0.1715 | 4.810  | 3.969  | 7.937  |
| 4000  | 0.0858 | 9.621  | 7.937  | 15.875 |
| 6000  | 0.0572 | 14.431 | 11.906 | 23.812 |

**Focus-feasibility matrix** (Y = F inside near field, focusing produces real focal gain;
N = F beyond Rayleigh => array already far-field, focal gain -> ~0 dB, premise empty):

| F \ f | 500 Hz | 1 kHz | 2 kHz | 4 kHz | 6 kHz |
|-------|--------|-------|-------|-------|-------|
| 2 m   | **N**  | Y     | Y     | Y     | Y     |
| 3 m   | **N**  | Y     | Y     | Y     | Y     |
| 5 m   | **N**  | N     | Y     | Y     | Y     |
| 8 m   | **N**  | N     | N     | Y     | Y     |
| 12 m  | **N**  | N     | N     | Y     | Y     |

**Plain-language consequences the sim must surface (NOT a verdict — metrics + physics):**
- At **500 Hz the array has essentially no usable focusing at any product distance** (Rayleigh
  ~2 m; museum/station/mall zones all >= 2-15 m are far-field). v1 "focusing" at 500 Hz is
  physically empty.
- At **1 kHz** focusing is real only for the closest zones (~2-3 m, museum 博物馆讲解 close range);
  by 5 m it is already far-field.
- The near-field zone deepens with frequency: at 4-6 kHz focusing remains physical out to ~8-16 m.
- => focal-gain numbers in section 4 are expected NON-trivial only in the matrix-Y cells; report
  the Y-cell gains AND the N-cell ~0 dB results side by side so the CTO sees exactly where the
  premise holds. The simulator must NOT clip / hide the N-cell near-zero results.

Product scenarios mapped to the matrix: 博物馆讲解 zones ~2-5 m, 商场分区 ~3-8 m, 车站广播 ~5-15 m.

---

## 4. Metrics to produce (per (f, F) where applicable)

Frequencies {500, 1000, 2000, 4000, 6000} Hz. Focal distances {2, 3, 5, 8, 12} m.
All on the broadside-normal axis (lateral y = 0) unless stated. All values tagged **[L2/仿真]**.

(a) **Focal gain [dB]** = SPL(at focal point F, FOCUSED to F) - SPL(at same point F, BROADSIDE-
    unfocused). Both use identical weights; difference is only the tau_n. Computed for every
    matrix cell (incl. the N-cells, expected ~0 dB — that is the empty-premise evidence).

(b) **Axial -6 dB zone depth [m]** = extent along the on-axis line (vary z around F at y=0) over
    which |p|^2 stays within 6 dB of the focal peak. Reported as (z_near, z_far, depth = z_far -
    z_near). Tells whether depth-zoning can isolate a near zone from a far zone.

(c) **Lateral -6 dB width [m]** at the focal plane (fix z = F_dist, vary y). Cross-check: in the
    far-field limit this width / F_dist must reproduce the angular -6 dB beamwidth (anchor below).

(d) **Cross-zone isolation [dB]** = for two candidate zone centers Z1, Z2 on-axis (e.g. 3 m and
    8 m), the SPL difference SPL(Z1) - SPL(Z2) when the array is FOCUSED at Z1, and symmetrically
    when focused at Z2. Positive, large => the system can preferentially energize one depth zone
    over another (the actual depth-zoning claim). Report the full 2x2 (focus@Z1, focus@Z2) x
    (measured@Z1, measured@Z2) SPL table per frequency, plus the isolation = on-target minus
    off-target.

### Output artifacts (write ONLY under sprint5/efficacy_sim/)
- `efficacy_sim.py` — numpy primary implementation (the model of section 2-4).
- `efficacy_sim_matlab.m` — MATLAB R2026a independent track (section 6).
- `results/focal_gain.csv`, `results/zone_depth.csv`, `results/lateral_width.csv`,
  `results/cross_zone_isolation.csv`, `results/nearfield_feasibility.csv`.
- `results/dualtrack_compare.csv` — numpy-vs-MATLAB quantitative diff per metric.
- `plots/` — field maps / axial & lateral cuts saved with `matplotlib Agg`; plots are data-backed,
  the CSVs are authoritative ("plots-as-data": every plotted curve also dumped to CSV).

---

## 5. Validation anchors (must reproduce before any metric is trusted)

| Anchor | Target | How |
|--------|--------|-----|
| **A1 — far-field BW@1k** | broadside -6 dB FULL-angle BW = **29.269 deg** [L2 anchor, F5-C beam gate / m3_numpy_8pair_equiv.csv] | Run the SAME far-field array-factor model as `sprint3/acoustic/sweep_d55.py` (`array_factor_db` + `beamwidth_6db`) with the section-1.3 weights at 1 kHz; must match 29.269 deg. Also: in the near-field model, push F -> infinity (or evaluate the unfocused far pattern) and the angular -6 dB width must converge to 29.269 deg. |
| **A2 — symmetric-pair equivalence** | 16-elem-with-paired-delays field == 8-pair-model field, diff = 0 (machine eps) | Build the field two ways: (i) 16 independent elements with delays/weights that happen to satisfy tau_n=tau_{15-n}, w_n=w_{15-n}; (ii) 8-pair model that assigns each channel's (tau_c, w_c) to both {c,15-c}. Max |p_i - p_ii| over the field grid must be ~0 (reproduces the 0.000e+00 result in `m3_numpy_8pair_equiv.csv`). Confirms the symmetric constraint is correctly built in. |
| **A3 — SLL sanity** | broadside peak SLL = -20.00 dB | far-field pattern with the Dolph -20 dB weights, via the reused `peak_sll`. |
| **A4 — feasibility self-consistency** | focal gain ~0 dB in every section-3 N-cell | the model itself must show focusing collapsing to broadside beyond Rayleigh (no hand-forcing). |

> Reuse the EXACT BW/SLL definitions from `sweep_d55.py` (`-6 dB FULL angle = 2x half angle`;
> `beamwidth_6db`, `peak_sll`, `array_factor_db`) so A1/A3 are bit-comparable to the prior gate.
> Note from memory: BW = full -6 dB angle = 2x half angle; a -6 dB full angle is always wider than
> a -3 dB full angle — do not conflate.

---

## 6. Dual-track discipline (铁律七)

- **Track 1 (primary) — numpy/scipy.** `efficacy_sim.py`. Spherical-wave sum of section 2,
  feasibility table of section 3, metrics of section 4. Weights read from
  `sprint4/dsp/fira/dolph_w8_q15.csv` (float column) — NOT hardcoded. c=343 explicit.
- **Track 2 (independent) — MATLAB R2026a** (verified available: Phased Array System Toolbox,
  Signal Processing, DSP System, Audio). `efficacy_sim_matlab.m`, run via the matlab MCP
  (`mcp__matlab__run_matlab_file` / `evaluate_matlab_code`). Independent implementation of the
  SAME spherical-wave equation (not a call into the numpy result). Weights re-read independently
  (MATLAB `chebwin(16,20)` normalized OR read the same CSV) and the two weight vectors compared.
- **Quantitative compare** dumped to `results/dualtrack_compare.csv`: per (f,F) focal gain,
  zone depth, lateral width, cross-zone isolation — report max abs diff and relative diff.
  Acceptance for "consistent": numerical agreement to within tight tolerance (target |diff| at the
  CSV precision used in the prior m3 tri-track, where tracks agreed to ~1e-12). Any two-track
  disagreement beyond tolerance => flag, do not average, escalate (per prior `E-MATLAB-1` rule).
- L-grade everything: spherical-wave sim = [L2/仿真]; the L^2/lambda feasibility table = [L3/解析];
  no value is labeled "measured" — there is no L1 here (no bench/anechoic data in scope).

---

## 7. Model boundaries / honesty declarations (carry into results)

1. **Point-source isotropic elements.** No element directivity, no enclosure diffraction, no mutual
   coupling. >=2 kHz the point-source assumption underestimates real-element high-freq directivity
   (prior memory 7.3: point-source confidence low >=2 kHz). Focal-gain trends are L2-directional, not
   acceptance numbers.
2. **No grating-lobe content above 6 kHz** — band capped at 6 kHz by design (d>=lambda at 6236 Hz).
   This sim does not characterize the 6.2-8 kHz P0 grating zone.
3. **SPL absolute level not modeled** — focal gain and isolation are RELATIVE dB (focused minus
   broadside, on-target minus off-target); T/S params and absolute SPL are out of scope (and were
   [估算] in prior work). Only differential acoustic differentiation is produced.
4. **Symmetric-only.** Every result assumes the topology constraint; off-axis steering excluded.
5. This is **GATE-1 screening**. The "useful vs empty" sufficiency call is the CTO's, against the
   PRD zone-separation requirement — this plan deliberately produces NO efficacy verdict.

---

## 8. Execution order (for the implementer)

1. Read weights from `dolph_w8_q15.csv` (float), assert symmetric expansion + all-distinct (FG1).
2. Build near-field spherical-wave field function; build broadside reference.
3. Reproduce anchors A1 (29.269 deg), A2 (8-pair equivalence = 0), A3 (-20 dB SLL), A4
   (N-cell ~0 dB). Halt if any anchor fails.
4. Compute the section-3 feasibility table in-script (do not just trust the pre-computed table).
5. Compute metrics (a)-(d) over the {f} x {F} grid; dump all CSVs + plots-as-data.
6. Run MATLAB track; dump `dualtrack_compare.csv`; confirm agreement.
7. Hand the metrics + feasibility matrix to independent critic, then CTO. No verdict from this run.
```
```
