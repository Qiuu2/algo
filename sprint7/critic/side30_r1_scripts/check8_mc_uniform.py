import sys, numpy as np, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic")
from crit_model import *
W35 = w16(cheb16(35)[:8])
rng = np.random.default_rng(777)
def run(fc, W, M=2000, mode="unif", pos=True):
    fs = band_f(fc, 61); k = 2*np.pi*fs/C
    out = {"raw": [], "cplx": [], "amp": []}
    for _ in range(M):
        if mode == "unif":
            a = rng.uniform(-1, 1, 16); p = np.deg2rad(rng.uniform(-5, 5, 16))
            dx = rng.uniform(-5e-4, 5e-4, 16) if pos else np.zeros(16); dz = rng.uniform(-5e-4, 5e-4, 16) if pos else np.zeros(16)
        e = 10**(a/20)*np.exp(1j*p)
        def P(th, gcal):
            s = np.sin(np.deg2rad(th)); c_ = np.cos(np.deg2rad(th))
            ph = np.exp(1j*k[:, None]*((X+dx)[None, :]*s + dz[None, :]*c_))
            return (np.abs((ph*(W*e*gcal)[None, :]).sum(1))**2).mean()
        # broadside pair-sum calibration measured at band centre, applied flat (complex or amplitude-only)
        k0 = 2*np.pi*fc/C
        ebs = e*np.exp(1j*k0*dz)                        # what a broadside measurement sees (depth offsets included)
        gc = np.ones(16, complex); ga = np.ones(16)
        for c in range(8):
            s_ = ebs[c]+ebs[15-c]; gc[c] = gc[15-c] = 2/s_; ga[c] = ga[15-c] = 2/abs(s_)
        for nm, g in (("raw", np.ones(16)), ("cplx", gc), ("amp", ga)):
            p0 = P(0, g); out[nm].append(10*np.log10(p0/max(P(90, g), P(-90, g))))
    return {n: (np.median(v), np.percentile(v, 10)) for n, v in out.items()}
for fc in (1000, 2000, 4000):
    r = run(fc, W35)
    print(f"D35 {fc} Hz, UNIFORM +/-1dB/+/-5deg/+/-0.5mm (project MC convention), worst of +/-90: " +
          "  ".join(f"{n}: med {m:.1f} P10 {q:.1f}" for n, (m, q) in r.items()))
