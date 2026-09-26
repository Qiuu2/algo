import sys, numpy as np, warnings
warnings.filterwarnings("ignore")
SP = "/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic"
sys.path.insert(0, SP)
from crit_model import *
W35, W30 = w16(cheb16(35)[:8]), w16(cheb16(30)[:8])
raw = np.fromfile(f"{SP}/paths.bin", dtype=np.float64); Ns = raw.size//6
x, y0, y1, y2, y3, yall = raw.reshape(6, Ns)
seg = 16384; nseg = Ns//seg; fs = 48000.0
def spec(s): return np.fft.rfft(s[:nseg*seg].reshape(nseg, seg)*np.hanning(seg), axis=1)
Yk = np.array([spec(y) for y in (y0, y1, y2, y3)]); freq = np.fft.rfftfreq(seg, 1/fs)
def Aw(f):
    f2 = f*f; ra = (12194**2*f2**2)/((f2+20.6**2)*np.sqrt((f2+107.7**2)*(f2+737.9**2))*(f2+12194**2)); return 20*np.log10(ra)+2.0
def pw(tables, theta):
    k = 2*np.pi*freq/C; Wt = np.array(tables)
    coef = Wt @ np.exp(1j*np.outer(X, k*np.sin(np.deg2rad(theta))))
    return (np.abs(np.einsum('kf,ksf->sf', coef, Yk))**2).mean(0)
def bb(tables, lo, hi):
    m = (freq >= lo*2**(-1/6)) & (freq <= hi*2**(1/6)) & (freq > 0)
    g = 10**(Aw(freq[m])/10)/freq[m]     # pink (1/f) x A-weighting, input white
    return 10*np.log10((pw(tables,0)[m]*g).sum()/(pw(tables,90)[m]*g).sum())
cases = {"D0 all D20": [W20]*4, "lead D2 (D30|D35|D35|D20)": [W30,W35,W35,W20],
         "SB0 D20 | SB1-3 D35": [W20,W35,W35,W35], "SB0 D30 | SB1-3 D35": [W30,W35,W35,W35], "all D35": [W35]*4}
print("REAL frozen tree, pink+A broadband att at 90 deg:")
for nm, T in cases.items():
    print(f"  {nm:28s} 250-5k {bb(T,250,5000):5.1f} | 630-5k {bb(T,630,5000):5.1f} | 630-6.3k {bb(T,630,6300):5.1f} | 1k-4k {bb(T,1000,4000):5.1f}")
# on-axis (0 deg) magnitude response ripple (linear part via cross-spectrum), 200-2800 Hz and 3.5-5 kHz
X_ = spec(x); Sxx = (np.abs(X_)**2).mean(0); H = np.array([(np.conj(X_)*Yk[k]).mean(0)/Sxx for k in range(4)])
print("\nOn-axis linear response ripple (dB, relative to its own median), REAL tree:")
for nm, T in cases.items():
    Wt = np.array(T); on = (Wt.sum(1)[:, None]*H).sum(0)
    for lo, hi in ((200, 2800), (3500, 5000)):
        m = (freq >= lo) & (freq <= hi); mag = 20*np.log10(np.abs(on[m])); med = np.median(mag)
        print(f"  {nm:28s} {lo}-{hi} Hz: min {mag.min()-med:+6.1f}  max {mag.max()-med:+5.1f}")
