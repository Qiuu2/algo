"""Track 2 (no C code): analytic LTI part of the telescoping pyramid with per-subband gains.
out = g3 x + (g2-g3) L1 x + (g1-g2) L1L2 x + (g0-g1) L1L2L3 x ,  L_l = H_l(f)^2 (halfband at rate 48k/2^(l-1), dec+interp, x2 gain)"""
import sys, re, numpy as np, warnings
warnings.filterwarnings("ignore")
SP = "/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic"
sys.path.insert(0, SP)
from crit_model import *
src = open("/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint4/dsp/core_only/include/fir_coeffs_hb63.h").read()
h = np.array([int(v) for v in re.findall(r"-?\d+", src.split("{")[1].split("}")[0])]) / 32768.0
assert h.size == 63
def Hhb(f, rate):   # causal FIR response at frequency f for a filter running at `rate`
    n = np.arange(63); return (h[None, :]*np.exp(-2j*np.pi*np.outer(f, n)/rate)).sum(1)
def paths(f):
    L1 = Hhb(f, 48000)**2; L2 = Hhb(f, 24000)**2; L3 = Hhb(f, 12000)**2
    P = np.array([L1*L2*L3, L1*L2 - L1*L2*L3, L1 - L1*L2, 1 - L1])  # SB0, SB1, SB2, SB3 linear path gains
    return P
for f in (500, 1500, 2000, 3000, 4000):
    print(f, "analytic |path| dB:", np.round(20*np.log10(np.abs(paths(np.array([f]))[:, 0])+1e-15), 1))
W35, W30 = w16(cheb16(35)[:8]), w16(cheb16(30)[:8])
def att(tables, fc, n=801):
    fs = band_f(fc, n); P = paths(fs)                 # (4,F)
    k = 2*np.pi*fs/C; Wt = np.array(tables)
    c90 = (Wt @ np.exp(1j*np.outer(X, k))) ; c0 = Wt @ np.ones((16, fs.size))
    return 10*np.log10((np.abs((c0*P).sum(0))**2).sum()/(np.abs((c90*P).sum(0))**2).sum())
for nm, T in (("D1 lead", [W20, W35, W35, W20]), ("D2 lead", [W30, W35, W35, W20]), ("SB0 D20|SB1-3 D35", [W20, W35, W35, W35]), ("all D20 (control)", [W20]*4)):
    print(f"{nm:20s}", [round(att(T, fc), 1) for fc in (500, 800, 1000, 1600, 2000, 2500, 3150, 4000, 5000)])
