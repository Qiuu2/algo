import sys, io, contextlib
sys.path.insert(0, "/home/it1234/algorithm_speaker/Kimi_Agent_多Agent协作方案/itc-enterprise-workflow/sprint7/dsp/wtbl")
sys.argv = ["gen_m2_wtbl.py", "--check"]
import gen_m2_wtbl as G
for name in ("h_pristine.h", "h_valedit.h", "h_wsedit.h"):
    G.OUT_H = "/tmp/claude-1000/-home-it1234-algorithm-speaker-Kimi-Agent--Agent-----itc-enterprise-workflow/7580d6ba-0506-4074-ad49-c5ff8314648c/scratchpad/critic_r3e/" + name
    G.RS_TRACE.clear()
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            G.main()
        print(name, "->", buf.getvalue().splitlines()[0])
    except SystemExit as e:
        print(name, "-> SystemExit:", e)
