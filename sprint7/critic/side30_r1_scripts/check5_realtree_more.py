import sys, numpy as np, warnings
warnings.filterwarnings("ignore")
SP = "/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic"
sys.path.insert(0, SP)
from crit_model import *
exec(open(f"{SP}/check4_realtree.py").read().split("FC = [")[0].split("print(\"\\nPath linear")[0])  # reuse loading + spectra (no printing of tables)
W35, W30 = w16(cheb16(35)[:8]), w16(cheb16(30)[:8])
Yk = np.array(Ys)
def rt(tables, fcs, lin_only=False, theta=90.0):
    k = 2*np.pi*freq/C; st = np.sin(np.deg2rad(theta))
    Wt = np.array(tables); coefT = Wt @ np.exp(1j*np.outer(X, k*st)); coef0 = Wt @ np.ones((16, freq.size))
    if lin_only:
        Hk = np.array(H)                                   # (4,F) linear part only
        P_T = np.abs((coefT*Hk).sum(0))**2 * Sxx; P_0 = np.abs((coef0*Hk).sum(0))**2 * Sxx
        P_T = P_T[None, :]; P_0 = P_0[None, :]
    else:
        P_T = np.abs(np.einsum('kf,ksf->sf', coefT, Yk))**2; P_0 = np.abs(np.einsum('kf,ksf->sf', coef0, Yk))**2
    out = []
    for fc in fcs:
        m = (freq >= fc*2**(-1/6)) & (freq <= fc*2**(1/6)); wp = 1/freq[m]
        out.append(10*np.log10((P_0[:, m]*wp).sum()/(P_T[:, m]*wp).sum()))
    return np.round(out, 1)
FC = [500, 800, 1000, 1600, 2000, 2500, 3150, 4000, 5000]
print("fc:", FC)
print("D1 real (full)        :", rt([W20, W35, W35, W20], FC))
print("D1 real (linear only) :", rt([W20, W35, W35, W20], FC, lin_only=True))
print("SB0 D20 | SB1-3 D35   :", rt([W20, W35, W35, W35], FC))
print("SB0 D30 | SB1-3 D35   :", rt([W30, W35, W35, W35], FC))
print("SB0 D35 | SB1-3 D20   :", rt([W35, W20, W20, W20], FC))
# per-channel ripple of the linear response for D1 (edge pair c=0 and centre c=7)
for c in (0, 3, 7):
    g = np.array([W20[c], W35[c], W35[c], W20[c]])
    Hc = (g[:, None]*np.array(H)).sum(0)
    m = (freq > 300) & (freq < 2800)
    mag = 20*np.log10(np.abs(Hc[m]))
    print(f"D1 channel c={c}: nominal gains SB0..3 = {np.round(g,3)}; linear response 300-2800 Hz: min {mag.min():.1f} dB max {mag.max():.1f} dB (flat target {20*np.log10(g[0]):.1f})")
