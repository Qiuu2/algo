import sys, numpy as np, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic")
from crit_model import *
W35, W30 = w16(cheb16(35)[:8]), w16(cheb16(30)[:8])
def Aw(f):  # IEC 61672 A-weighting (dB), exact formula
    f2 = f*f
    ra = (12194**2*f2**2)/((f2+20.6**2)*np.sqrt((f2+107.7**2)*(f2+737.9**2))*(f2+12194**2))
    return 20*np.log10(ra)+2.00
def design(sb_edges, tables):
    """brick-wall: sb_edges e.g. (1500,3000,6000) ; tables list of 4 w16"""
    def w(f):
        i = int(np.searchsorted(sb_edges, f, side='right')); return tables[i]
    return w
LEAD_EDGES = (1500.0, 3000.0, 6000.0)
TRUE_EDGES = (3000.0, 6000.0, 12000.0)    # measured on the frozen tree (critic probe)
D0 = design(LEAD_EDGES, [W20, W20, W20, W20])
D2 = design(LEAD_EDGES, [W30, W35, W35, W20])
D1 = design(LEAD_EDGES, [W20, W35, W35, W20])
CENT = [250,315,400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300,8000,10000,12500,16000]
def bb(wf, hpf=0, lpf=1e9, weight="A", n=61):
    p0 = p90 = 0.0
    for fc in CENT:
        if fc < hpf or fc > lpf: continue
        fs = band_f(fc, n)
        for f in fs:
            g = 10**(Aw(f)/10) if weight=="A" else 1.0
            a = af([0.0, 90.0], f, wf(f))[0]
            p0 += g*abs(a[0])**2/len(fs); p90 += g*abs(a[1])**2/len(fs)
    return 10*np.log10(p0/p90)
print("Broadband pink, 1/3-oct bands, att at 90 deg (ideal isotropic, far field):")
for nm, wf in (("D0 all D20", D0), ("D1 SB0 D20|D35|D35", D1), ("D2 SB0 D30|D35|D35", D2)):
    print(f"  {nm:20s} A 250-5k: HPF0 {bb(wf,0,5000):5.1f} HPF630 {bb(wf,630,5000):5.1f} | "
          f"A 250-6.3k HPF630 {bb(wf,630,6300):5.1f} | A 250-10k HPF630 {bb(wf,630,10000):5.1f} | A 250-16k HPF0 {bb(wf,0,16000):5.1f} | Z 250-5k HPF0 {bb(wf,0,5000,'Z'):5.1f}")
# ---- near field: exact spherical, isotropic
def nf_att(fc, w, r, n=81):
    fs = band_f(fc, n); P0 = P90 = 0.0
    for f in fs:
        k = 2*np.pi*f/C
        for th, acc in ((0.0, 0), (90.0, 1)):
            mx, my = r*np.sin(np.deg2rad(th)), r*np.cos(np.deg2rad(th))
            R = np.sqrt((mx-X)**2+my**2)
            p = abs(np.sum(w*np.exp(-1j*k*R)/R))**2
            if acc == 0: P0 += p
            else: P90 += p
    return 10*np.log10(P0/P90)
print("\nNear-field band-avg att90 (ideal isotropic) vs mic distance r from array centre:")
for nm, w in (("D20", W20), ("D35", W35)):
    for fc in (1000, 2000, 4000):
        print(f"  {nm} {fc:5d} Hz: " + "  ".join(f"r={r:>4}m {nf_att(fc,w,r):5.1f}" for r in (1, 2, 4, 8, 16)) + f"  far {band_att(fc,w):5.1f}")
# ---- as-built A arm (competitor-speaker rig, M2_CHMAP_FIX off): physical rank r gets w[perm[r]]
w8 = read_w8(); perm = [4,5,6,7,0,1,2,3]
WA = w16(np.array([w8[perm[r]] for r in range(8)]))
print("\nA-arm (mis-mapped) weights edge->centre:", np.round(WA[:8],3))
print("  point att90 1k/2k/4k:", [round(att_point(90,f,WA),1) for f in (1000,2000,4000)], " (EXP_CHMAP_AB predicts 15.1 / 30.3 at 1k/2k)")
print("  band-avg att90 far:", {fc: round(band_att(fc,WA),1) for fc in (500,630,800,1000,1250,1600,2000,2500,3150,4000,5000)})
print("  band-avg att90 at r=1m:", {fc: round(nf_att(fc,WA,1.0),1) for fc in (1000,2000,4000)}, " D20 at 1m:", {fc: round(nf_att(fc,W20,1.0),1) for fc in (1000,2000,4000)})
print("  pink-A broadband 250-5k HPF0: A-arm %.1f vs D20 %.1f" % (bb(lambda f: WA,0,5000), bb(D0,0,5000)))
