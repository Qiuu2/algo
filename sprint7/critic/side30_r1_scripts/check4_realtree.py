import sys, numpy as np, warnings
warnings.filterwarnings("ignore")
SP = "/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic"
sys.path.insert(0, SP)
from crit_model import *
W35, W30 = w16(cheb16(35)[:8]), w16(cheb16(30)[:8])
raw = np.fromfile(f"{SP}/paths.bin", dtype=np.float64)
Ns = raw.size // 6
x, y0, y1, y2, y3, yall = raw.reshape(6, Ns)
print("PR checks: max|y0+y1+y2+y3-yall| = %.2e ; max|yall-x| = %.2e (x rms %.3f)" % (np.max(np.abs(y0+y1+y2+y3-yall)), np.max(np.abs(yall-x)), x.std()))
# path transfer (linear part) estimate via cross-spectrum with x, and alias/nonlinear residual power
fs = 48000.0
seg = 8192; nseg = Ns // seg
def spec(sig): return np.fft.rfft(sig[:nseg*seg].reshape(nseg, seg) * np.hanning(seg), axis=1)
X_ = spec(x); Ys = [spec(y) for y in (y0, y1, y2, y3)]
freq = np.fft.rfftfreq(seg, 1/fs)
Sxx = (np.abs(X_)**2).mean(0)
H = [ (np.conj(X_)*Y).mean(0)/Sxx for Y in Ys ]
print("\nPath linear gains |H_k| (dB) at selected f  [SB0, SB1, SB2, SB3]:")
for f in (200, 500, 1000, 1500, 2000, 2500, 2800, 3000, 3200, 4000, 5000, 6000, 8000):
    i = np.argmin(abs(freq-f))
    print(f"  {f:5d} Hz: " + "  ".join(f"{20*np.log10(abs(h[i])+1e-15):6.1f}" for h in H))
# ---- array response with REAL tree: per channel y_c = sum_k w_k[c]*y^k  ; far-field P(theta,f) = sum_n Y_c(n)(f) e^{jk x_n sin th}
Yk = np.array(Ys)                                   # (4, nseg, F)
def real_tree_att(tables, fcs, theta=90.0):
    # tables: list of 4 w16 (per subband); returns band-avg att at theta for each fc (power ratio of sums over bins/segments)
    k = 2*np.pi*freq/C
    st = np.sin(np.deg2rad(theta))
    # per-element spectra: Y_n = sum_k w_k[n] Yk
    Wt = np.array(tables)                           # (4,16)
    steer0 = np.ones((16, freq.size))
    steerT = np.exp(1j*np.outer(X, k*st))           # (16,F)
    coefT = Wt @ steerT                              # (4,F) : sum_n w_k[n] e^{...}
    coef0 = Wt @ steer0
    P_T = np.abs(np.einsum('kf,ksf->sf', coefT, Yk))**2
    P_0 = np.abs(np.einsum('kf,ksf->sf', coef0, Yk))**2
    out = {}
    for fc in fcs:
        m = (freq >= fc*2**(-1/6)) & (freq <= fc*2**(1/6))
        wpink = 1.0/freq[m]                          # pink weighting within band (input is white)
        out[fc] = 10*np.log10((P_0[:, m]*wpink).sum()/(P_T[:, m]*wpink).sum())
    return out
FC = [500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]
def brick(tables, edges, fc):
    def w(f): return tables[int(np.searchsorted(edges, f, side='right'))]
    return band_att(fc, w, n=101)
designs = {"D0 all D20": [W20]*4, "D1 lead (SB0 D20,SB1 D35,SB2 D35,SB3 D20)": [W20, W35, W35, W20],
           "D2 lead (SB0 D30,SB1 D35,SB2 D35,SB3 D20)": [W30, W35, W35, W20],
           "D35 in ALL subbands (equal gains, PR)": [W35]*4}
for nm, T in designs.items():
    rt = real_tree_att(T, FC)
    print(f"\n{nm}")
    print("   fc   | REAL frozen tree | brick @ lead edges 1.5/3/6k | brick @ true edges 3/6/12k")
    for fc in FC:
        print(f"  {fc:5d} | {rt[fc]:7.1f}          | {brick(T,(1500.,3000.,6000.),fc):7.1f}                    | {brick(T,(3000.,6000.,12000.),fc):7.1f}")
