import sys, numpy as np, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic")
from crit_model import *
print("anchor point att90 D20 @1k/2k/4k:", [round(att_point(90, f, W20), 3) for f in (1000, 2000, 4000)], " (want 22.40/23.01/26.03)")
print("anchor att30 D20 @1k:", round(att_point(30, 1000, W20), 3), "(want 23.10)")
W35, W30 = w16(cheb16(35)[:8]), w16(cheb16(30)[:8])
# check chebwin symmetric -> w16 of first 8 equals full
assert np.allclose(W35, cheb16(35)) and np.allclose(W30, cheb16(30))
print("\nBand-avg (201 pts) att90 and worst 60-90 sector, full-band fixed weights:")
print(" fc   | D20 a90  D20 s60-90 | D35 a90  D35 s60-90 | D30 a90 | uniform a90")
for fc in (250,315,400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300):
    r = [band_att(fc, W20), band_att(fc, W20, thetas=np.arange(60,90.01,0.5)),
         band_att(fc, W35), band_att(fc, W35, thetas=np.arange(60,90.01,0.5)),
         band_att(fc, W30), band_att(fc, np.ones(16))]
    print(f"{fc:5d} | {r[0]:6.2f}  {r[1]:6.2f}     | {r[2]:6.2f}  {r[3]:6.2f}     | {r[4]:6.2f}  | {r[5]:6.2f}")
print("\n41-pt vs 201-pt D35 @2k/4k:", round(band_att(2000, W35, n=41),2), round(band_att(4000, W35, n=41),2))
print("On-axis full-drive vs D20 (max w=1): D35 %.2f dB, D30 %.2f dB" % (20*np.log10(W35.sum()/W20.sum()), 20*np.log10(W30.sum()/W20.sum())))
print("BW6@1k: D20 %.2f  D30 %.2f  D35 %.2f" % (bw6(1000,W20), bw6(1000,W30), bw6(1000,W35)))
# point att90 of D35 vs f near grating region
print("\nPoint att90 near grating: f, D20, D35")
for f in (4500,5000,5200,5400,5500,5600,5700,5800,6000,6236):
    print(f, round(att_point(90,f,W20),1), round(att_point(90,f,W35),1))
