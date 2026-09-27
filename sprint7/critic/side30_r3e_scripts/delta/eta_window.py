import sys, numpy as np
R = "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow"
sys.path.insert(0, R + "/sprint7/dsp/wtbl"); sys.path.insert(0, R + "/sprint7/sim/acoustic")
import gen_m2_wtbl as G, s7_common as S
jyt = [(30,500),(90,500),(30,1000),(90,1000),(30,2000),(90,2000),(30,4000),(90,4000)]
d35 = np.array([5868, 8179, 12739, 17834, 22954, 27510, 30932, 32768]) / 32768
jd = np.array([S.att_db(th, f, S.expand16(d35)) for th, f in jyt])
print("eta   Q15-row                                            worst(point-D35)  all>=D35")
for eta in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5, 2.0, 3.0):
    q = G.q15(G.rs_track1(60.0, 30.0, eta))
    jb = np.array([S.att_db(th, f, S.expand16(q / 32768)) for th, f in jyt])
    d = jb - jd; i = int(np.argmin(d))
    print(f"{eta:<5} {str(q.tolist()):50s} {d[i]:+.3f} @{jyt[i][1]}/{jyt[i][0]}   {bool(np.all(d >= 0))}")
