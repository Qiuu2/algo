import sys
sys.path.insert(0, "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint7/dsp/wtbl")
import gen_m2_wtbl as G
G.OUT_H = sys.argv[1]
sys.argv = ["gen_m2_wtbl.py", "--check"]
G.main()
