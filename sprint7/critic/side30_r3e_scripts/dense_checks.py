import numpy as np
C, D = 343.0, 0.055
xc = (np.arange(8) - 7.5) * D
T = {"D35q": [5868, 8179, 12739, 17834, 22954, 27510, 30932, 32768],
     "RS-Aq": [3470, 6948, 11598, 16960, 22469, 27318, 30876, 32768],
     "RS-Bq": [5285, 8787, 13546, 18697, 23762, 28068, 31143, 32768],
     "D20": [28404, 16525, 20371, 24031, 27287, 29934, 31802, 32768]}
def att(w, f, th):
    k = 2*np.pi*np.asarray(f)/C
    a0 = 2*np.sum(w)
    a = np.sum(w[None, :]*2*np.cos(k[:, None]*np.sin(np.deg2rad(th))*xc[None, :]), 1)
    return -20*np.log10(np.abs(a)/a0 + 1e-300)
jyt = [(30,500),(90,500),(30,1000),(90,1000),(30,2000),(90,2000),(30,4000),(90,4000)]
print("in-band minimum, 31-pt sampled vs dense (200001 pts) :")
res = {}
for n, q in T.items():
    w = np.array(q, float)
    row = []
    for th, fc in jyt:
        f31 = np.geomspace(fc*2**(-1/6), fc*2**(1/6), 31)
        fd = np.geomspace(fc*2**(-1/6), fc*2**(1/6), 200001)
        row.append((att(w, f31, th).min(), att(w, fd, th).min()))
    res[n] = row
    print(f"  {n:6s} " + "  ".join(f"{fc}/{th}: {a:6.3f}|{b:6.3f}" for (th, fc), (a, b) in zip(jyt, row)))
print("RS-B minus D35, dense in-band minimum:", "  ".join(f"{fc}/{th}: {rb[1]-rd[1]:+.3f}" for (th, fc), rb, rd in zip(jyt, res['RS-Bq'], res['D35q'])))
# u-domain peak sidelobe: pattern vs psi = k d sin(th); visible up to k d; grating onset at psi = 2 pi - main lobe
def pat_u(w, psi):
    x = (np.arange(8) - 7.5)
    return np.abs(np.sum(w[None, :]*2*np.cos(psi[:, None]*x[None, :]), 1))/(2*np.sum(w))
psi = np.linspace(0, np.pi, 400001)
for n, q in T.items():
    w = np.array(q, float)
    p = 20*np.log10(pat_u(w, psi)+1e-300)
    # interior local maxima after first null
    i0 = np.argmax(np.diff(p) > 0)   # first rise after main lobe decay = first null region
    loc = np.where((p[1:-1] > p[:-2]) & (p[1:-1] >= p[2:]))[0] + 1
    loc = loc[loc > i0]
    pk = [(psi[i], p[i]) for i in loc]
    top = max(pk, key=lambda t: t[1])
    fvis = top[0]*C/(2*np.pi*D)       # lowest f at which this side-lobe peak is visible (at 90 deg)
    print(f"  {n:6s} max side-lobe in psi (0..pi] = {top[1]:7.2f} dB at psi={top[0]:.3f} rad (visible from f >= {fvis:6.0f} Hz); "
          f"all peaks: " + " ".join(f"{p_:.1f}@{ps:.2f}" for ps, p_ in pk[:8]))
