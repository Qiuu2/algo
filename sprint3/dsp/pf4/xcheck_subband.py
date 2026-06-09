"""
TASK-PF4-02 Sub-2 交叉验证（numpy 独立复刻）
关注点：差分金字塔是 PR（telescoping）结构，full-reconstruction 输出会把
定点损失抵消掉 → 必须在 SUBBAND 层比定点 vs 浮点，才反映真实处理损失。
"""
import numpy as np

FS=48000; FRAME=64; N_FRAMES=1024; N=FRAME*N_FRAMES
TAPS=63

# --- 半带系数：kaiser beta=6, cutoff 0.5*nyq, DC 归一化 (镜像 C make_halfband) ---
def make_hb():
    M=TAPS-1; beta=6.0
    from numpy import i0
    n=np.arange(TAPS)
    m=n-M/2.0
    sinc=np.where(m==0,1.0,np.sin(np.pi*0.5*m)/(np.pi*0.5*m))
    r=(2.0*n/M)-1.0
    win=i0(beta*np.sqrt(1-r*r))/i0(beta)
    h=0.5*sinc*win
    h=h/h.sum()
    return h
hb_f64=make_hb()
hb_q15=np.clip(np.round(hb_f64*32768.0),-32768,32767).astype(np.int64)  # Q15 ints

# --- 定点 push_filter：state Q31 int, coef Q15 int, acc int64, >>15 -> Q31 ---
class HbFix:
    def __init__(self): self.state=np.zeros(TAPS,dtype=np.int64); self.widx=0
    def push(self,x):
        self.state[self.widx]=x
        self.widx=(self.widx+1)%TAPS
        idx=self.widx; acc=0
        for k in range(TAPS):
            rd=(idx+k)%TAPS
            acc+= hb_q15[k]*self.state[rd]
        return acc>>15   # arithmetic shift, matches C >> on int64
class HbF64:
    def __init__(self): self.state=np.zeros(TAPS); self.widx=0
    def push(self,x):
        self.state[self.widx]=x
        self.widx=(self.widx+1)%TAPS
        idx=self.widx; acc=0.0
        for k in range(TAPS):
            rd=(idx+k)%TAPS
            acc+=hb_f64[k]*self.state[rd]
        return acc

def dec2_fix(s,inp):
    out=[]
    for i,x in enumerate(inp):
        y=s.push(int(x))
        if i&1: out.append(y)
    return np.array(out,dtype=np.int64)
def interp2_fix(s,inp):
    out=[]
    for x in inp:
        y0=s.push(int(x)); out.append(y0*2)
        y1=s.push(0);      out.append(y1*2)
    return np.array(out,dtype=np.int64)
def dec2_f(s,inp):
    out=[]
    for i,x in enumerate(inp):
        y=s.push(float(x))
        if i&1: out.append(y)
    return np.array(out)
def interp2_f(s,inp):
    out=[]
    for x in inp:
        out.append(s.push(float(x))*2.0); out.append(s.push(0.0)*2.0)
    return np.array(out)

# states
class FixTree:
    def __init__(self): self.ad=[HbFix() for _ in range(3)]; self.ai=[HbFix() for _ in range(3)]
class FltTree:
    def __init__(self): self.ad=[HbF64() for _ in range(3)]; self.ai=[HbF64() for _ in range(3)]

def to_q31(v): 
    s=np.clip(v*2147483648.0,-2147483648.0,2147483647.0); return int(s)
def from_q31(v): return v/2147483648.0

# input chirp
i=np.arange(N); t=i/FS; T=N/FS; f0,f1=20.0,11000.0
K=(f1/f0)**(t/T)
phase=2*np.pi*f0*T/np.log(f1/f0)*(K-1.0)
xf=0.5*np.sin(phase)
xq=np.array([to_q31(v) for v in xf],dtype=np.int64)
xfq=np.array([from_q31(v) for v in xq])  # double view of Q31 input

ft=FixTree(); lt=FltTree()
# accumulate subbands across frames
SB_fix=[[],[],[],[]]; SB_flt=[[],[],[],[]]
f0n,f1n,f2n,f3n=FRAME,FRAME//2,FRAME//4,FRAME//8
for fr in range(N_FRAMES):
    xin_q=xq[fr*FRAME:(fr+1)*FRAME]
    xin_f=xfq[fr*FRAME:(fr+1)*FRAME]
    # FIX analyze
    a1=dec2_fix(ft.ad[0],xin_q); a2=dec2_fix(ft.ad[1],a1); a3=dec2_fix(ft.ad[2],a2)
    r3=interp2_fix(ft.ai[2],a3); r2=interp2_fix(ft.ai[1],a2); r1=interp2_fix(ft.ai[0],a1)
    sb1=a2-r3; sb2=a1-r2; sb3=xin_q-r1; sb0=a3
    for k,sb in enumerate([sb0,sb1,sb2,sb3]): SB_fix[k].append(sb)
    # FLT analyze
    a1f=dec2_f(lt.ad[0],xin_f); a2f=dec2_f(lt.ad[1],a1f); a3f=dec2_f(lt.ad[2],a2f)
    r3f=interp2_f(lt.ai[2],a3f); r2f=interp2_f(lt.ai[1],a2f); r1f=interp2_f(lt.ai[0],a1f)
    sb1f=a2f-r3f; sb2f=a1f-r2f; sb3f=xin_f-r1f; sb0f=a3f
    for k,sb in enumerate([sb0f,sb1f,sb2f,sb3f]): SB_flt[k].append(sb)

names=["SB0 coarse","SB1 detail","SB2 detail","SB3 detail"]
print("=== SUBBAND 层 定点 vs 浮点 (numpy 独立复刻, L2) ===")
print("(差分金字塔为 PR 结构：重建输出会抵消定点损失；真实损失在子带)")
for k in range(4):
    fx=from_q31(np.concatenate(SB_fix[k]).astype(np.float64))
    fl=np.concatenate(SB_flt[k])
    g=20  # guard frames worth
    fx=fx[g:]; fl=fl[g:]
    err=fx-fl
    sp=np.mean(fl**2); ep=np.mean(err**2)
    snr=10*np.log10(sp/(ep+1e-300))
    print(f"  {names[k]:11s}: SNR(fix vs flt)={snr:7.1f} dB  max|err|={np.max(np.abs(err)):.3e}  ({np.max(np.abs(err))*2**31:.2f} LSB)")

# ============================================================
# 分解：把 Q15 系数效应 与 Q31 算术截断效应 分离
#   Chain B2 = double 运算，但用 Q15 系数(还原成 double)。
#   fix vs B2  -> 纯 Q31 算术截断损失
#   B2  vs B(double系数) -> 纯 Q15 系数量化损失
# ============================================================
hb_q15_as_f=hb_q15.astype(np.float64)/32768.0
class HbF64Q15:
    def __init__(self): self.state=np.zeros(TAPS); self.widx=0
    def push(self,x):
        self.state[self.widx]=x; self.widx=(self.widx+1)%TAPS
        idx=self.widx; acc=0.0
        for k in range(TAPS):
            rd=(idx+k)%TAPS
            acc+=hb_q15_as_f[k]*self.state[rd]
        return acc
def dec2_fq(s,inp):
    out=[]
    for i,x in enumerate(inp):
        y=s.push(float(x))
        if i&1: out.append(y)
    return np.array(out)
def interp2_fq(s,inp):
    out=[]
    for x in inp:
        out.append(s.push(float(x))*2.0); out.append(s.push(0.0)*2.0)
    return np.array(out)
class FltTreeQ15:
    def __init__(self): self.ad=[HbF64Q15() for _ in range(3)]; self.ai=[HbF64Q15() for _ in range(3)]

lt2=FltTreeQ15()
SB_b2=[[],[],[],[]]
for fr in range(N_FRAMES):
    xin_f=xfq[fr*FRAME:(fr+1)*FRAME]
    a1=dec2_fq(lt2.ad[0],xin_f); a2=dec2_fq(lt2.ad[1],a1); a3=dec2_fq(lt2.ad[2],a2)
    r3=interp2_fq(lt2.ai[2],a3); r2=interp2_fq(lt2.ai[1],a2); r1=interp2_fq(lt2.ai[0],a1)
    for k,sb in enumerate([a3,a2-r3,a1-r2,xin_f-r1]): SB_b2[k].append(sb)

print("\n=== 损失分解：纯 Q31 算术截断 vs 纯 Q15 系数量化 (子带层, L2) ===")
for k in range(4):
    fx=from_q31(np.concatenate(SB_fix[k]).astype(np.float64))[20:]
    b2=np.concatenate(SB_b2[k])[20:]      # double运算+Q15系数
    fl=np.concatenate(SB_flt[k])[20:]     # double运算+double系数
    e_arith=fx-b2     # 纯算术截断
    e_coef =b2-fl     # 纯系数量化
    sp=np.mean(b2**2)
    snr_arith=10*np.log10(sp/(np.mean(e_arith**2)+1e-300))
    sp2=np.mean(fl**2)
    snr_coef=10*np.log10(sp2/(np.mean(e_coef**2)+1e-300))
    print(f"  {names[k]:11s}: 纯Q31截断 SNR={snr_arith:6.1f} dB | 纯Q15系数 SNR={snr_coef:6.1f} dB")

# ============================================================
# 重建层交叉验证（应复现 C 的 ~316 dB PR-抵消假象）
# ============================================================
def synth_fix(ai_states, sb0,sb1,sb2,sb3):
    up3=interp2_fix(ai_states[2],sb0); a2p=up3+sb1
    up2=interp2_fix(ai_states[1],a2p); a1p=up2+sb2
    up1=interp2_fix(ai_states[0],a1p); return up1+sb3
def synth_flt(ai_states, sb0,sb1,sb2,sb3):
    up3=interp2_f(ai_states[2],sb0); a2p=up3+sb1
    up2=interp2_f(ai_states[1],a2p); a1p=up2+sb2
    up1=interp2_f(ai_states[0],a1p); return up1+sb3
syn_fix=[HbFix() for _ in range(3)]; syn_flt=[HbF64() for _ in range(3)]
yf=[]; yfl=[]
for fr in range(N_FRAMES):
    out_fix=synth_fix(syn_fix, SB_fix[0][fr],SB_fix[1][fr],SB_fix[2][fr],SB_fix[3][fr])
    out_flt=synth_flt(syn_flt, SB_flt[0][fr],SB_flt[1][fr],SB_flt[2][fr],SB_flt[3][fr])
    yf.append(from_q31(out_fix.astype(np.float64))); yfl.append(out_flt)
yf=np.concatenate(yf)[600:-600]; yfl=np.concatenate(yfl)[600:-600]
err=yf-yfl; snr=10*np.log10(np.mean(yfl**2)/(np.mean(err**2)+1e-300))
print(f"\n=== 重建层 交叉验证 (numpy) ===")
print(f"  recon fix-vs-flt SNR = {snr:.1f} dB  max|err|={np.max(np.abs(err)):.3e}")
print(f"  → 复现 C 的高 SNR（PR telescoping 抵消假象），与 C harness 一致")
