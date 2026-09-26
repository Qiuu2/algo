# critic2: independent ideal-table numbers (no s7_common import)
import numpy as np
from scipy.signal.windows import chebwin
C=343.0; D=0.055; N=16; X=(np.arange(N)-(N-1)/2)*D
def wd(s): w=chebwin(N,s); return w/w.max()
W={'D20':wd(20),'D30':wd(30),'D35':wd(35)}
def af(w,f,th):
    st=np.sin(np.deg2rad(np.atleast_1d(th)))
    return np.abs(np.exp(1j*2*np.pi*f/C*np.outer(st,X))@w)
def bandp(w,fc,th,n=41):
    fs=np.geomspace(fc*2**(-1/6),fc*2**(1/6),n); return np.mean([af(w,f,th)**2 for f in fs],axis=0)
def A(f):
    ra=12194**2*f**4/((f**2+20.6**2)*np.sqrt((f**2+107.7**2)*(f**2+737.9**2))*(f**2+12194**2)); return 20*np.log10(ra)+2.0
BC=[500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300]
for k,w in W.items():
    att={fc:10*np.log10(bandp(w,fc,[0])[0]/bandp(w,fc,[90])[0]) for fc in BC}
    ang=np.linspace(0,90,90001); p=20*np.log10(af(w,1000,ang)/af(w,1000,[0])[0]); bw=2*ang[np.argmax(p<-6)]
    a30=lambda f:20*np.log10(af(w,f,[0])[0]/af(w,f,[30])[0])
    def bb(bands):
        p0=sum(10**(A(fc)/10)*bandp(w,fc,[0])[0] for fc in bands); p9=sum(10**(A(fc)/10)*bandp(w,fc,[90])[0] for fc in bands); return 10*np.log10(p0/p9)
    print(k,' '.join(f"{fc}:{att[fc]:.1f}" for fc in BC))
    print(f"   BW1k={bw:.2f}  a30@1k={a30(1000):.1f}  a30@500={a30(500):.2f}  axis vs D20={20*np.log10(w.sum()/W['D20'].sum()):+.2f} dB  maxw={w.max():.3f}  bbA(630-5k)={bb(BC[1:11]):.1f}  bbA(630-6.3k)={bb(BC[1:]):.1f}")
# near-field endfire check, ideal D35 and D30: exact spherical sum, band-avg, broadside vs endfire at same r
print("near-field (exact 1/R, band avg) att90 vs far-field:")
for k in ('D30','D35'):
    w=W[k]
    for fc in (1000,2000,4000):
        fs=np.geomspace(fc*2**(-1/6),fc*2**(1/6),41); ff=10*np.log10(bandp(w,fc,[0])[0]/bandp(w,fc,[90])[0]); s=f"  {k} {fc}: ff {ff:.1f}"
        for r in (4,8,16,32):
            Rb=np.sqrt(r**2+X**2); Re=np.abs(r-X)
            pb=np.mean([abs(np.sum(w*np.exp(-1j*2*np.pi*f/C*Rb)/Rb))**2 for f in fs]); pe=np.mean([abs(np.sum(w*np.exp(-1j*2*np.pi*f/C*Re)/Re))**2 for f in fs])
            s+=f" | r={r}m {10*np.log10(pb/pe):.1f}"
        print(s)
