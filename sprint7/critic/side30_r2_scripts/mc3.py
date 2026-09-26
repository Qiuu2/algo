import numpy as np
src=open('mc2.py').read().split("W={'D20'")[0]; exec(src)
# (a) lead's Gaussian convention sigma 1 dB / 5 deg, freq-flat, no jig noise (dx kept, tiny)
_draw=draw
def draw(n,model):
    if model[0]=='G1':
        return (10**(rng.normal(0,1,n)/20)*np.exp(1j*np.deg2rad(rng.normal(0,5,n))))[:,None]*np.ones(len(FALL))
    return _draw(n,model)
w=wd(35); M=300
print("D35 Gaussian 1dB/5deg flat (lead: 26.9/15 -> 28.6/31 -> 32.3/77 -> 33.7/90 -> 35.7/100)")
for s in ('asbuilt','amp','pair','buy24','cplxf'):
    r=[trial(w,('G1',1,1),s,0.0) for _ in range(M)]; a2=np.array([x[2000] for x in r]); aj=np.mean([min(x.values())>=30 for x in r])*100
    print(f"  {s:8s} 2k {np.median(a2):5.1f}/{np.mean(a2>=30)*100:3.0f}%   joint1-4k {aj:3.0f}%")
# (b) Q15 headroom: trims folded into a max=1.0 table must be renormalised (GAP-SAT <=1.0 premise) -> extra on-axis loss
w8=w[:8]; L=[]
for _ in range(4000):
    e=rng.uniform(-1,1,16); ph=rng.uniform(-5,5,16); ee=10**(e/20)*np.exp(1j*np.deg2rad(ph))
    g=1/np.abs((ee[:8]+ee[15-np.arange(8)])/2); L.append(20*np.log10(max(1.0,np.max(w8*g))))
L=np.array(L); print(f"D35 as-built trim renorm loss: median {np.median(L):.2f} dB, P90 {np.percentile(L,90):.2f} dB, P(>0)= {np.mean(L>0)*100:.0f}%")
print("D35 w8 edge->centre:",np.round(w8,3))
