#!/usr/bin/env python3
"""Critic R3e: OWN Monte Carlo (no project imports, own seeds, own RNG streams, own GP method).
Model: 16 isotropic point sources, d = 55 mm, c = 343; per-driver complex error g_n(f), position dx_n ~ U(+/-0.5 mm).
  U-flat : a ~ U(+/-1 dB), phi ~ U(+/-5 deg), frequency-flat.
  G-like : Gaussian, same variances; 50 % of the variance flat, 50 % a smooth GP in log2 f with a squared-exponential
           kernel of length 1 octave, drawn by CHOLESKY (not random Fourier features); jig error 0.25 dB / 1.5 deg
           per driver + 0.1 dB / 0.5 deg per frequency (measurement only).
Strategies: asbuilt ; amp (per-channel trim by 1/rms of the pair's measured mean response over 0.9-4.5 kHz) ;
            pair (greedy best-matched pairing on the measured responses, best pairs -> largest weights, then trim).
Metric: 1/3-oct band power average (31 log pts) at +90 and -90 deg vs 0 deg, WORSE side per band; JOINT7 = all 7 bands
        1k..4k >= 30 dB. Common random numbers across designs; paired differences with bootstrap-free exact
        McNemar-style counts."""
import sys
import numpy as np

C, D, N = 343.0, 0.055, 16
X = (np.arange(N) - 7.5) * D
BANDS = [1000, 1250, 1600, 2000, 2500, 3150, 4000]
FE = np.concatenate([fc * 2.0 ** np.linspace(-1 / 6, 1 / 6, 31) for fc in BANDS])       # 217 eval freqs
FJ = 1000 * 2 ** (-1 / 6) * (4000 * 2 ** (1 / 6) / (1000 * 2 ** (-1 / 6))) ** np.linspace(0, 1, 40)  # jig grid
FALL = np.concatenate([FE, FJ])
NE = len(FE)
U = np.log2(FALL / 2000.0)
Kc = np.exp(-0.5 * (U[:, None] - U[None, :]) ** 2 / 1.0 ** 2) + 1e-9 * np.eye(len(FALL))
Lc = np.linalg.cholesky(Kc)

TABLES = {
    "D35q":  [5868, 8179, 12739, 17834, 22954, 27510, 30932, 32768],
    "RS-Aq": [3470, 6948, 11598, 16960, 22469, 27318, 30876, 32768],
    "RS-Bq": [5285, 8787, 13546, 18697, 23762, 28068, 31143, 32768],
    "D30q":  [9535, 10397, 14932, 19718, 24327, 28300, 31221, 32768],
}
SC = "/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic_r3e/"
for lab in ("RS-A", "RS-B"):
    try:
        w = np.load(SC + f"{lab}_full.npy")
        TABLES[lab + "full"] = list(np.round(w * 32768).astype(int))
    except FileNotFoundError:
        pass
W8 = {k: np.array(v, float) / 32768.0 for k, v in TABLES.items()}


def draw(rng, M, model):
    if model == "U":
        a = rng.uniform(-1, 1, (M, N))[:, :, None] * np.ones(len(FALL))
        p = rng.uniform(-5, 5, (M, N))[:, :, None] * np.ones(len(FALL))
    else:
        sa, sp = 1 / np.sqrt(3), 5 / np.sqrt(3)
        za = rng.standard_normal((M, N, len(FALL))) @ Lc.T
        zp = rng.standard_normal((M, N, len(FALL))) @ Lc.T
        a = sa * (np.sqrt(0.5) * rng.standard_normal((M, N))[:, :, None] + np.sqrt(0.5) * za)
        p = sp * (np.sqrt(0.5) * rng.standard_normal((M, N))[:, :, None] + np.sqrt(0.5) * zp)
    return 10 ** (a / 20) * np.exp(1j * np.deg2rad(p))


def measure(rng, e, model):
    M = e.shape[0]
    sm = 0.0 if model == "U" else 0.25
    ej = e[:, :, NE:]
    ga = rng.normal(0, sm, (M, N, 1)) + rng.normal(0, 0.1, ej.shape) if sm > 0 else rng.normal(0, 0.1, ej.shape)
    gp = (rng.normal(0, 6 * sm, (M, N, 1)) if sm > 0 else 0.0) + rng.normal(0, 0.5, ej.shape)
    return ej * 10 ** (ga / 20) * np.exp(1j * np.deg2rad(gp))


def greedy_pairs(m):
    """m: (16, F) measured responses of one array -> 8 pairs, best matched first."""
    Dm = np.mean(np.abs(m[:, None, :] - m[None, :, :]) ** 2, axis=2)
    np.fill_diagonal(Dm, np.inf)
    left = list(range(N))
    out = []
    while len(out) < 8:
        sub = Dm[np.ix_(left, left)]
        i, j = np.unravel_index(np.argmin(sub), sub.shape)
        a, b = left[i], left[j]
        out.append((a, b))
        left = [x for x in left if x not in (a, b)]
    return out


def run(model, strat, M, seed):
    rng = np.random.default_rng(seed)
    e = draw(rng, M, model)                                   # (M,16,Fall) driver errors (driver index)
    mm = measure(rng, e, model)                               # (M,16,40)
    dx = rng.uniform(-0.5e-3, 0.5e-3, (M, N))                 # per POSITION
    k = 2 * np.pi * FE / C
    res = {}
    for lab, w8 in W8.items():
        # driver -> position map and per-position trim
        E = np.empty((M, N, NE), complex)
        gains = np.ones((M, N))
        order = np.argsort(-w8)                                # channels, largest weight first
        for t in range(M):
            if strat == "pair":
                prs = greedy_pairs(mm[t])
                perm = np.empty(N, int)
                for (a, b), c in zip(prs, order):
                    perm[c], perm[15 - c] = a, b
            else:
                perm = np.arange(N)
            E[t] = e[t, perm, :NE]
            if strat in ("amp", "pair"):
                for c in range(8):
                    pm = 0.5 * (mm[t, perm[c]] + mm[t, perm[15 - c]])
                    g = 1.0 / np.sqrt(np.mean(np.abs(pm) ** 2))
                    gains[t, c] = gains[t, 15 - c] = g
        w16 = np.concatenate([w8, w8[::-1]])[None, :] * gains             # (M,16)
        P = []
        for s in (0.0, 1.0, -1.0):
            ph = np.exp(1j * k[None, None, :] * s * (X[None, :, None] + dx[:, :, None]))   # (M,16,F)
            af = np.einsum("mn,mnf,mnf->mf", w16, E, ph)
            P.append(np.abs(af) ** 2)
        P0, Pp, Pm = P
        R = np.empty((M, 7))
        for b in range(7):
            sl = slice(31 * b, 31 * b + 31)
            R[:, b] = 10 * np.log10(P0[:, sl].sum(1) / np.maximum(Pp[:, sl].sum(1), Pm[:, sl].sum(1)))
        res[lab] = np.all(R >= 30.0, axis=1)
    return res


if __name__ == "__main__":
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    seeds = [int(s) for s in sys.argv[2].split(",")] if len(sys.argv) > 2 else [11, 22, 33]
    cells = [("U", "asbuilt"), ("U", "amp"), ("U", "pair"), ("G", "asbuilt"), ("G", "amp"), ("G", "pair")]
    for model, strat in cells:
        acc = {lab: [] for lab in W8}
        for sd in seeds:
            r = run(model, strat, M, sd * 1000 + hash((model, strat)) % 997)
            for lab in W8:
                acc[lab].append(r[lab])
        cat = {lab: np.concatenate(v) for lab, v in acc.items()}
        n = len(cat["D35q"])
        line = f"[{model}|{strat:7s}] n={n}  joint7 %: " + "  ".join(f"{lab} {100*cat[lab].mean():5.1f}" for lab in W8)
        print(line)
        per_seed = {lab: [100 * x.mean() for x in acc[lab]] for lab in W8}
        print("      per-seed: " + "  ".join(f"{lab} " + "/".join(f"{v:.1f}" for v in per_seed[lab]) for lab in ("D35q", "RS-Aq", "RS-Bq")))
        for lab in ("RS-Aq", "RS-Bq") + tuple(k for k in W8 if k.endswith("full")):
            a, b = cat[lab], cat["D35q"]
            n10, n01 = int(np.sum(a & ~b)), int(np.sum(~a & b))
            dlt = 100 * (a.mean() - b.mean())
            se = 100 * np.sqrt(n10 + n01 - (n10 - n01) ** 2 / n) / n
            print(f"      {lab} - D35q = {dlt:+5.2f} pts  (paired SE {se:.2f}; only-{lab} {n10} / only-D35 {n01})")
        a, b = cat["RS-Aq"], cat["RS-Bq"]
        n10, n01 = int(np.sum(a & ~b)), int(np.sum(~a & b))
        se = 100 * np.sqrt(n10 + n01 - (n10 - n01) ** 2 / n) / n
        print(f"      RS-Aq - RS-Bq = {100*(a.mean()-b.mean()):+5.2f} pts (paired SE {se:.2f})")
        sys.stdout.flush()
