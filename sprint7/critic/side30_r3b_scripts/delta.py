import csv, numpy as np, warnings; warnings.filterwarnings("ignore")
from scipy.signal.windows import chebwin
R="/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint7/sim/side30/fir/"
O="/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic3b/rerun/"
rd=lambda p: list(csv.DictReader(open(p)))
# 1) regression: old (first review) vs new numbers
o,n=rd(O+"s7_fir_mc.csv"),rd(R+"s7_fir_mc.csv"); ks=["design","error_model","strategy","band_fc_hz","median_db","p10_db","yield_ge30_pct","joint_yield_pct","seed","arrays"]
print("MC rows",len(o),len(n),"key cols identical:",all(all(a[k]==b[k] for k in ks) for a,b in zip(o,n)))
o,n=rd(O+"s7_fir_bands.csv"),rd(R+"s7_fir_bands.csv"); print("bands old cols identical:",all(all(a[k]==b[k] for k in a) for a,b in zip(o,n)))
o,n=list(csv.reader(open(O+"s7_fir_summary.csv"))),list(csv.reader(open(R+"s7_fir_summary.csv"))); print("summary values identical:",o[1:]==n[1:])
# 2) new CSVs
for r in rd(R+"s7_fir_headroom.csv"): print("HEADROOM",r)
v=rd(R+"s7_fir_verify.csv"); cols=[c for c in v[0] if c.startswith("dev_")]
for c in cols: xs=[float(r[c]) for r in v]; print(f"VERIFY {c}: {max(xs):.1f} .. {min(xs):.1f}")
print("VERIFY counts:",[(r["design"],r["st1_history_samples"],r["io1_input_samples_odd_len"],r["io1_input_samples_padded_slot"]) for r in v][:9:4])
nf=[r for r in rd(R+"s7_fir_nearfield.csv") if r["design"]=="Dolph-20" and r["r_m"] in ("1.0","1")]; print("NF D20 1m band/single:",[(r["band_fc_hz"],r["att90_band_db_41pt"],r["att90_single_f_db"]) for r in nf])
j=[r for r in rd(R+"s7_fir_jyt.csv") if r["design"]=="Dolph-35" and r["angle_deg"]=="30" and r["band_fc_hz"]=="500"]; print("JYT D35 30/500:",j)
print("JYT NA rows:",sum(1 for r in rd(R+"s7_fir_jyt.csv") if r["att_band_db"]=="NA"))
# 3) own MC: 3-band vs 7-band (DEC-S7-SIDE30-01 criterion) joint yield, U-flat as-built
c0=343.0;d=0.055;N=16;X=(np.arange(N)-7.5)*d;FS=48000.0
H={}
for row in csv.reader(open(R+"s7_fir_coeffs_127tap.csv")):
    if row[0]=="variant": continue
    H.setdefault(row[0],np.zeros((8,127)))[int(row[2])]=np.array(row[3:],float)
def Afir(h,f):
    w=2*np.pi*np.atleast_1d(f)/FS; return ((np.exp(-1j*np.outer(w,np.arange(127)))@h.T)*np.exp(1j*w*63)[:,None]).real
w16=lambda A: np.concatenate([A,A[:,::-1]],1)
d35=chebwin(16,35); d35/=d35.max()
B7=(1000,1250,1600,2000,2500,3150,4000); nb=31
BF={fc:np.geomspace(fc*2**(-1/6),fc*2**(1/6),nb) for fc in B7}
W={"D35":{fc:np.tile(d35,(nb,1)) for fc in B7},"V1-128":{fc:w16(Afir(H["V1"],BF[fc])) for fc in B7},"V2-128":{fc:w16(Afir(H["V2"],BF[fc])) for fc in B7}}
rng=np.random.default_rng(4242);M=3000;res={k:np.empty((M,7)) for k in W}
st=np.array([0.0,1.0,-1.0])
for t in range(M):
    e=10**(rng.uniform(-1,1,N)/20)*np.exp(1j*np.deg2rad(rng.uniform(-5,5,N)));xe=X+rng.uniform(-5e-4,5e-4,N)
    for bi,fc in enumerate(B7):
        k=2*np.pi*BF[fc]/c0; ph=np.exp(1j*k[:,None,None]*st[None,:,None]*xe[None,None,:])
        for key in W:
            p=(np.abs(np.einsum("fn,n,ftn->ft",W[key][fc],e,ph))**2).sum(0); res[key][t,bi]=10*np.log10(p[0]/max(p[1],p[2]))
i3=[0,3,6]
for key,r in res.items():
    y3=100*np.mean(np.all(r[:,i3]>=30,1)); y7=100*np.mean(np.all(r>=30,1))
    print(f"OWN MC U-flat as-built {M} arrays seed 4242 {key:7s}: joint 3-band {y3:5.1f}%  7-band {y7:5.1f}%  per-band yield "+"/".join(f"{100*np.mean(r[:,b]>=30):.0f}" for b in range(7)))
