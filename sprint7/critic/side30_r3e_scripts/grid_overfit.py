import numpy as np
C, D = 343.0, 0.055
xc = (np.arange(8) - 7.5) * D
T = {"D35q": [5868, 8179, 12739, 17834, 22954, 27510, 30932, 32768],
     "RS-Aq": [3470, 6948, 11598, 16960, 22469, 27318, 30876, 32768],
     "RS-Bq": [5285, 8787, 13546, 18697, 23762, 28068, 31143, 32768]}
def r90(w, fc, n):
    f = np.geomspace(fc*2**(-1/6), fc*2**(1/6), n); k = 2*np.pi*f/C
    p0 = (2*np.sum(w))**2
    p9 = np.sum(w[None,:]*2*np.cos(k[:,None]*xc[None,:]), 1)**2
    return 10*np.log10(n*p0/np.sum(p9))
def sector_worst(w, fc, n, th):
    f = np.geomspace(fc*2**(-1/6), fc*2**(1/6), n); k = 2*np.pi*f/C
    p0 = n*(2*np.sum(w))**2
    s = np.sin(np.deg2rad(th))
    af = np.einsum('c,ftc->ft', w, 2*np.cos(k[:,None,None]*s[None,:,None]*xc[None,None,:]))
    return 10*np.log10(p0/np.max(np.sum(af**2, 0)))
for n, q in T.items():
    w = np.array(q, float)
    a = [r90(w, fc, 31) for fc in (1000,1250,1600,2000,2500,3150,4000)]
    b = [r90(w, fc, 3001) for fc in (1000,1250,1600,2000,2500,3150,4000)]
    th = np.arange(60, 90.0001, 0.05)
    s31 = min(sector_worst(w, fc, 31, th) for fc in (1000,1250,1600,2000,2500,3150,4000))
    s3k = min(sector_worst(w, fc, 1001, th) for fc in (1000,1250,1600,2000,2500,3150,4000))
    print(f"{n:6s} R90 min7 31pt {min(a):6.2f} / 3001pt {min(b):6.2f}  max|diff| per band {np.max(np.abs(np.array(a)-np.array(b))):.3f} dB ; sector60-90 worst 31pt/0.05deg {s31:6.2f} vs 1001pt {s3k:6.2f}")
