import sys, numpy as np, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic")
from crit_model import *
W35 = w16(cheb16(35)[:8])
fs2k = band_f(2000, 81)
TH = np.array([0.0, 90.0, -90.0])
# precompute steering (F,T,N)
k = 2*np.pi*fs2k[:,None,None]/C
E = np.exp(1j*k*np.sin(np.deg2rad(TH))[None,:,None]*X[None,None,:])
def batt(w, both=False):
    P = (np.abs((E*w[None,None,:]).sum(-1))**2).mean(0)
    return 10*np.log10(P[0]/(max(P[1],P[2]) if both else P[1]))
# ---- wiring faults at 2k, D20 and D35
for name, W in (("D20", W20), ("D35", W35)):
    rev = [batt(W*np.where(np.arange(16)==n,-1,1), both=True) for n in range(16)]
    dead1 = [batt(W*np.where(np.arange(16)==n,0,1), both=True) for n in range(16)]
    # series pair physics: open coil -> whole pair silent ; shorted coil -> failed=0, partner gets 2x voltage
    pair_open = [batt(W*np.where((np.arange(16)==c)|(np.arange(16)==15-c),0,1), both=True) for c in range(8)]
    short = []
    for n in range(16):
        m = 15-n; e = np.ones(16); e[n]=0; e[m]=2.0; short.append(batt(W*e, both=True))
    chrev = [batt(W*np.where((np.arange(16)==c)|(np.arange(16)==15-c),-1,1), both=True) for c in range(8)]
    print(f"{name} 2k band ideal {batt(W):.2f} | 1 drv reversed med {np.median(rev):.1f} worst {min(rev):.1f} | "
          f"1 drv zeroed(lead model) med {np.median(dead1):.1f} | pair OPEN (series) med {np.median(pair_open):.1f} worst {min(pair_open):.1f} | "
          f"drv SHORT (partner x2) med {np.median(short):.1f} worst {min(short):.1f} | ch(pair) reversed med {np.median(chrev):.1f} worst {min(chrev):.1f}")
# ---- MC: D35 at 2k band, sigma 1 dB / 5 deg, frequency-flat, independent drivers
rng = np.random.default_rng(12345)
M = 3000
def cal_complex(e):
    e = e.copy()
    for c in range(8):
        g = 2.0/(e[c]+e[15-c]); e[c]*=g; e[15-c]*=g
    return e
def cal_amp(e):  # real positive per-channel gain only (B4 mechanism = real Q15 gain per channel/subband)
    e = e.copy()
    for c in range(8):
        g = 2.0/abs(e[c]+e[15-c]); e[c]*=g; e[15-c]*=g
    return e
res = {k: [] for k in ("raw+90","raw_worst","cplx_worst","amp_worst","cplx+90")}
for _ in range(M):
    e = 10**(rng.normal(0,1.0,16)/20)*np.exp(1j*np.deg2rad(rng.normal(0,5.0,16)))
    res["raw+90"].append(batt(W35*e)); res["raw_worst"].append(batt(W35*e, True))
    ec = cal_complex(e); res["cplx_worst"].append(batt(W35*ec, True)); res["cplx+90"].append(batt(W35*ec))
    res["amp_worst"].append(batt(W35*cal_amp(e), True))
for kname, v in res.items():
    v = np.array(v); print(f"MC D35 2k s=1dB/5deg {kname:11s}: median {np.median(v):.2f}  P10 {np.percentile(v,10):.2f}  P1 {np.percentile(v,1):.2f}  frac>=30 {np.mean(v>=30):.2f}")
# analytic mean-power floor
sa = np.log(10)/20*1.0; sp = np.deg2rad(5.0)
var_e = (np.exp(2*sa**2)-2*np.exp(sa**2/2)*np.exp(-sp**2/2)+1)  # E|a e^{jp}-1|^2 for lognormal a, gaussian p
floor = var_e*np.sum(W35**2)/np.sum(W35)**2
det = 10**(-batt(W35)/10)
print(f"analytic mean-power att: {-10*np.log10(floor+det):.2f} dB (error floor alone {-10*np.log10(floor):.2f})")
