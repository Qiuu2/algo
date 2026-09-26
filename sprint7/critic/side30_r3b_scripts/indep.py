# Independent critic re-derivation (own code path: 16-element complex AF from CSV coeffs, own band grid, own seed)
import csv, numpy as np
from scipy.signal.windows import chebwin
R="/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint7/sim/side30/fir/"
c0=343.0; d=0.055; N=16; X=(np.arange(N)-7.5)*d; FS=48000.0
H={}
for row in csv.reader(open(R+"s7_fir_coeffs_127tap.csv")):
    if row[0]=="variant": continue
    H.setdefault(row[0],np.zeros((8,127)))[int(row[2])]=np.array(row[3:],float)
for v,h in H.items():
    s=2*h.sum(0); dl=np.zeros(127); dl[63]=1
    print(f"[{v}] identity max|sum2h-delta|={np.abs(s-dl).max():.2e}  symmetric(typeI) max|h-h[::-1]|={np.abs(h-h[:,::-1]).max():.1e}  L1/ch max={np.abs(h).sum(1).max():.4f}")
def Afir(h,f):
    n=np.arange(h.shape[1]); w=2*np.pi*np.atleast_1d(f)/FS
    Hc=np.exp(-1j*np.outer(w,n))@h.T              # (F,8) complex
    Z=Hc*np.exp(1j*w*63)[:,None]
    return Z.real, np.abs(Z.imag).max()
def w16(A): return np.concatenate([A,A[:,::-1]],1)  # element n -> channel min(n,15-n)
def P(W,f,th,xe=X,e=None):
    k=2*np.pi*np.atleast_1d(f)/c0; st=np.sin(np.deg2rad(np.atleast_1d(th)))
    E=np.ones(N) if e is None else e
    return np.abs(np.einsum("fn,n,ftn->ft",W,E,np.exp(1j*k[:,None,None]*st[None,:,None]*xe[None,None,:])))**2
def band(fc,n): return np.geomspace(fc*2**(-1/6),fc*2**(1/6),n)
d35=chebwin(16,35); d35=d35/d35.max()
for v in ("V1","V2"):
    for npts in (31,201):
        out=[]
        for fc in (1000,2000,4000):
            fb=band(fc,npts); A,im=Afir(H[v],fb); p=P(w16(A),fb,[0,90,-90]).sum(0)
            out.append(10*np.log10(p[0]/max(p[1],p[2])))
        print(f"[{v}-128] att90 worse-side band {npts}pts 1k/2k/4k = "+"/".join(f"{x:.2f}" for x in out)+f"  (max imag resid {im:.1e})")
# BW@1k own bisection on exact 1000 Hz pattern
def bw6(W1,f):
    p0=P(W1,f,[0.0])[0,0]
    g=lambda t: 10*np.log10(P(W1,f,[t])[0,0]/p0)+6
    th=np.arange(0,90,0.01); vals=np.array([g(t) for t in th]); i=np.argmax(vals<0); a,b=th[i-1],th[i]
    for _ in range(60):
        m=(a+b)/2; a,b=(m,b) if g(m)>0 else (a,m)
    return 2*a
for v in ("V1","V2"):
    A,_=Afir(H[v],[1000.0]); print(f"[{v}-128] BW-6 full @1k = {bw6(w16(A),1000.0):.3f} deg")
print(f"[D35 table] BW-6 full @1k = {bw6(np.tile(d35,(1,1)),1000.0):.3f} deg")
# own MC: U-flat as-built, per-driver flat errors, +/-0.5mm, worse side, joint >=30 dB @1k,2k,4k
rng=np.random.default_rng(777); M=4000; nb=41
BF={fc:band(fc,nb) for fc in (1000,2000,4000)}
Wd={"D35":{fc:np.tile(d35,(nb,1)) for fc in BF}, "V1-128":{fc:w16(Afir(H["V1"],BF[fc])[0]) for fc in BF}, "V2-128":{fc:w16(Afir(H["V2"],BF[fc])[0]) for fc in BF}}
res={k:np.empty((M,3)) for k in Wd}; pw={k:np.empty((M,3)) for k in Wd}
for t in range(M):
    e=10**(rng.uniform(-1,1,N)/20)*np.exp(1j*np.deg2rad(rng.uniform(-5,5,N))); xe=X+rng.uniform(-5e-4,5e-4,N)
    for k,W in Wd.items():
        for b,fc in enumerate(BF):
            p=P(W[fc],BF[fc],[0,90,-90],xe,e).sum(0); res[k][t,b]=10*np.log10(p[0]/max(p[1],p[2])); pw[k][t,b]=(p[1]+p[2])/2/p[0]
se=lambda p: 100*np.sqrt(p/100*(1-p/100)/M)
for k in res:
    j=100*np.mean(np.all(res[k]>=30,1)); med=np.median(res[k],0); mp=10*np.log10(pw[k].mean(0))
    print(f"[MC own, U-flat as-built, {M} arrays, seed 777] {k:7s} joint={j:5.1f}% (+/-{se(j):.1f} 1SE)  median 1k/2k/4k={med[0]:.1f}/{med[1]:.1f}/{med[2]:.1f}  mean-power att (avg side) {-mp[0]:.1f}/{-mp[1]:.1f}/{-mp[2]:.1f}")
# floor formula: sigma_eff^2 * ||w||^2/|sum w|^2 (mean over band), sigma_eff^2 = var(e)/|E e|^2
g=10**(rng.uniform(-1,1,10**6)/20)*np.exp(1j*np.deg2rad(rng.uniform(-5,5,10**6))); s2=np.var(g)/abs(g.mean())**2
print(f"sigma2 E|g-1|^2={np.mean(abs(g-1)**2):.5f}  var/|mean|^2={s2:.5f}")
for k,W in Wd.items():
    fl=[s2*np.mean((W[fc]**2).sum(1)/(W[fc].sum(1))**2) for fc in BF]
    print(f"  floor {k:7s} 1k/2k/4k = "+"/".join(f"{-10*np.log10(x):.1f}" for x in fl)+" dB (mean power, error-only)")
