import sys, numpy as np, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic")
from crit_model import *
def nf_point(f, w, r, th):
    k = 2*np.pi*f/C; mx, my = r*np.sin(np.deg2rad(th)), r*np.cos(np.deg2rad(th))
    R = np.sqrt((mx-X)**2+my**2); return np.sum(w*np.exp(-1j*k*R)/R)
def nf_att_pt(f, w, r, th=90.0): return 20*np.log10(abs(nf_point(f,w,r,0.0))/abs(nf_point(f,w,r,th)))
def nf_att_band(fc, w, r, th=90.0, n=81):
    fs = band_f(fc, n); p0 = sum(abs(nf_point(f,w,r,0.0))**2 for f in fs); p = sum(abs(nf_point(f,w,r,th))**2 for f in fs)
    return 10*np.log10(p0/p)
W = {"uniform": np.ones(16), "D20": W20, "D25": w16(cheb16(25)[:8]), "D30": w16(cheb16(30)[:8]), "D35": w16(cheb16(35)[:8])}
print("r=1 m, 90 deg attenuation: point @1k/2k/4k | band @1k/2k/4k ;  competitor [L1, 1 m, algo on] 90deg: 32.0 / 24.8 / 25.4 ; 60deg: 26.9/24.3/20.7")
for nm, w in W.items():
    print(f"  {nm:8s} pt {nf_att_pt(1000,w,1):5.1f} {nf_att_pt(2000,w,1):5.1f} {nf_att_pt(4000,w,1):5.1f} | band {nf_att_band(1000,w,1):5.1f} {nf_att_band(2000,w,1):5.1f} {nf_att_band(4000,w,1):5.1f} | 60deg band {nf_att_band(1000,w,1,60):5.1f} {nf_att_band(2000,w,1,60):5.1f} {nf_att_band(4000,w,1,60):5.1f}")
# baffled-piston 90deg element factor for plausible driver radii (upper bound on extra side attenuation, far field)
from scipy.special import j1
for a in (0.020, 0.025):
    vals = []
    for f in (1000, 2000, 4000, 5000, 6300, 8000):
        ka = 2*np.pi*f/C*a; vals.append(-20*np.log10(abs(2*j1(ka)/ka)))
    print(f"baffled piston radius {a*1000:.0f} mm: extra 90deg atten at 1k/2k/4k/5k/6.3k/8k = {np.round(vals,1)} dB")
print("\n1 m point attenuation at 30/60/90 deg for fixed Dolph tapers vs competitor [L1 1 m]:")
comp = {1000: (22.5, 26.9, 32.0), 2000: (24.1, 24.3, 24.8), 4000: (18.8, 20.7, 25.4), 500: (7.5, 14.9, 21.3)}
for f in (500, 1000, 2000, 4000):
    line = f"  {f:5d} Hz competitor 30/60/90 = {comp[f]} |"
    for sll in (20, 25, 30, 35, 40):
        w = W20 if sll == 20 else w16(cheb16(sll)[:8])
        line += f" D{sll}: {nf_att_pt(f,w,1,30):4.1f}/{nf_att_pt(f,w,1,60):4.1f}/{nf_att_pt(f,w,1,90):4.1f}"
    print(line)
