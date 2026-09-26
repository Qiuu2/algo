# critic2 independent MC: pairing/trim value under flat vs frequency-dependent driver errors + jig noise.
import numpy as np, sys, warnings; warnings.filterwarnings("ignore")
from scipy.signal.windows import chebwin
C=343.0; D=0.055; N=16; X=(np.arange(N)-(N-1)/2)*D
def wd(s): w=chebwin(N,s); return w/w.max()
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 4242)
BF={fc:np.geomspace(fc*2**(-1/6),fc*2**(1/6),31) for fc in (1000,2000,4000)}
PG=np.geomspace(1000*2**(-1/6),4000*2**(1/6),40)          # jig measurement / pairing grid 0.9-4.5k
FALL=np.concatenate([BF[1000],BF[2000],BF[4000],PG]); U=np.log2(FALL/2000)
SL={1000:slice(0,31),2000:slice(31,62),4000:slice(62,93)}; SP=slice(93,133)
ST=np.array([0.0,1.0,-1.0])
def gp(n,ell,K=40):          # unit-variance smooth random functions of log2 f (random Fourier features, SE kernel)
    om=rng.normal(0,1/ell,(n,K)); ph=rng.uniform(0,2*np.pi,(n,K))
    return np.sqrt(2/K)*np.cos(om[:,:,None]*U[None,None,:]+ph[:,:,None]).sum(1)
def draw(n,model):
    kind,p,ell=model
    if kind=='U':   # lead's convention, freq-flat uniform
        a=rng.uniform(-1,1,n)[:,None]*np.ones(len(FALL)); f=rng.uniform(-5,5,n)[:,None]*np.ones(len(FALL))
    else:           # Gaussian with SAME variance as uniform +/-1dB,+/-5deg; fraction p freq-flat, 1-p smooth GP(ell oct)
        sa,sf=1/np.sqrt(3),5/np.sqrt(3)
        a=sa*(np.sqrt(p)*rng.normal(0,1,n)[:,None]+np.sqrt(1-p)*gp(n,ell)); f=sf*(np.sqrt(p)*rng.normal(0,1,n)[:,None]+np.sqrt(1-p)*gp(n,ell))
    return 10**(a/20)*np.exp(1j*np.deg2rad(f))
def meas(e,sm):  # jig: per-driver flat repeatability (sm dB, 6*sm deg) + per-freq noise 0.1 dB/0.5 deg
    n=e.shape[0]; F=e.shape[1]
    return e*10**((rng.normal(0,sm,(n,1))+rng.normal(0,0.1,(n,F)))/20)*np.exp(1j*np.deg2rad(rng.normal(0,6*sm,(n,1))+rng.normal(0,0.5,(n,F))))
def greedy(m):
    n=m.shape[0]; Dm=np.mean(np.abs(m[:,None,:]-m[None,:,:])**2,axis=2); Dm[np.arange(n),np.arange(n)]=np.inf
    left=set(range(n)); pairs=[]
    while len(left)>=2 and len(pairs)<8:
        L=sorted(left); sub=Dm[np.ix_(L,L)]; i,j=np.unravel_index(np.argmin(sub),sub.shape); a,b=L[i],L[j]; pairs.append((a,b)); left-={a,b}
    return pairs
def trial(w,model,strat,sm):
    n=24 if strat=='buy24' else 16
    e=draw(n,model); m=meas(e,sm); dx=rng.uniform(-5e-4,5e-4,16)   # position error belongs to the SLOT
    if strat=='buy24':
        mu=m[:,SP].mean(1); med=np.median(mu.real)+1j*np.median(mu.imag); keep=np.argsort(np.abs(mu-med))[:16]; e,m=e[keep],m[keep]
    w8=w[:8]
    if strat in ('asbuilt','amp'): pairs=[(c,15-c) for c in range(8)]; chans=list(range(8))
    else: pairs=greedy(m); chans=list(np.argsort(-w8))
    E=np.empty((16,len(FALL)),complex)
    for (i,j),c in zip(pairs,chans):
        pm=(m[i]+m[j])/2
        if strat=='asbuilt': g=np.ones(len(FALL))
        elif strat=='cplxf': g=np.ones(len(FALL),complex); g[:]=np.interp(FALL,FALL[SP],(1/pm[SP]).real)+1j*np.interp(FALL,FALL[SP],(1/pm[SP]).imag)  # ideal per-ch filter from jig data
        else: g=np.ones(len(FALL))/np.sqrt(np.mean(np.abs(pm[SP])**2))       # one real gain per channel (table)
        E[c]=e[i]*g; E[15-c]=e[j]*g
    out={}
    for fc,sl in SL.items():
        ph=np.exp(1j*2*np.pi*FALL[sl][None,:,None]/C*ST[None,None,:]*(X+dx)[:,None,None])   # (16,F,3)
        P=(np.abs(np.einsum('n,nf,nfa->fa',w,E[:,sl],ph))**2).sum(0)
        out[fc]=10*np.log10(P[0]/max(P[1],P[2]))
    return out
W={'D20':wd(20),'D35':wd(35)}
M=int(sys.argv[2]) if len(sys.argv)>2 else 400
MODELS=[('U-flat (lead)',('U',1,1),0.0),('G-flat eqvar, jig0.25',('G',1.0,1),0.25),('G p0.5 l1oct, jig0.25',('G',0.5,1.0),0.25),('G p0.25 l0.5oct, jig0.25',('G',0.25,0.5),0.25)]
STR=[('asbuilt','as-built'),('amp','+gain trim'),('pair','pair16+trim'),('buy24','buy24+pair+trim'),('cplxf','pair16+cplx filt')]
for wn in ('D35','D20'):
    for mname,model,sm in MODELS:
        if wn=='D20' and mname!='U-flat (lead)': continue
        print(f"== {wn} | {mname}   [median/yield>=30] 1k | 2k | 4k | all3>=30")
        for s,lab in STR:
            r=[trial(W[wn],model,s,sm) for _ in range(M)]
            a={fc:np.array([x[fc] for x in r]) for fc in (1000,2000,4000)}; allb=np.mean((a[1000]>=30)&(a[2000]>=30)&(a[4000]>=30))*100
            print(f"   {lab:18s} "+" | ".join(f"{np.median(a[fc]):5.1f}/{np.mean(a[fc]>=30)*100:3.0f}%" for fc in (1000,2000,4000))+f" | {allb:3.0f}%")
