#!/usr/bin/env python3
"""
residual_pack80_repro.py  [DESKTOP host model, [L2], NOT board]

ONE QUESTION (Critic round-5 mandate, 2026-06-04):
  residual_repro.py BYPASSED the 80-bit -> 3x32-bit writeback pack/unpack.
  Does a faithful HW sec.38-10 3-word pack (of the EXACT int64 MAC) +
  our actual fira_reassemble80 unpack (fira_tree.c:335) reproduce the board
  sb3 residual [0,-2,0,+2,0,-2,0,+6] ?

sec.38-10 writeback layout (DOC-S4-FIRA-DP-01):
  w[0] = LSW   (acc bits  0..31)
  w[1] = MSW   (acc bits 32..63)
  w[2] = 16-bit overflow (acc bits 64..79, sign)

fira_reassemble80 (fira_tree.c:335-343) reconstructs:
  lsw = (uint32_t)w[0]; msw = (uint32_t)w[1];
  acc = (int64_t)((msw << 32) | lsw);   # low 64 bits as signed, w[2] IGNORED

So: model = pack exact int64 MAC into (LSW,MSW,OVF), then unpack low-64 signed,
then current postscale ((acc>>15)*2), compare to core.

ASCII-only. No board claim. No FIRA benefit numbers (C9).
"""
import importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rr", os.path.join(HERE, "residual_repro.py"))
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)

MASK32 = 0xFFFFFFFF


def pack80(acc):
    """HW sec.38-10: 80-bit two's-complement -> 3x32 (LSW, MSW, 16-bit OVF)."""
    u = acc & ((1 << 80) - 1)            # 80-bit two's complement
    w0 = u & MASK32                      # LSW  bits 0..31
    w1 = (u >> 32) & MASK32              # MSW  bits 32..63
    w2 = (u >> 64) & 0xFFFF              # 16-bit overflow bits 64..79
    # store as int32 (signed C container), like the FIRA output buffer int32 words
    def to_i32(x):
        return x - (1 << 32) if x >= (1 << 31) else x
    return [to_i32(w0), to_i32(w1), to_i32(w2 - (1 << 16) if w2 >= (1 << 15) else w2)]


def reassemble80(w):
    """EXACT mirror of fira_tree.c:335-343 fira_reassemble80 (w[2] DROPPED).

    MINOR fix (critic, 2026-06-04): dropping w[2] is LOSSLESS not because
    "w[2] is exactly 0" -- it is NOT always 0.  For negative accumulator values
    w[2] is the sign-extension word 0xFFFF (critic measured 29/64 accs over the
    frame have w[2]=0xFFFF).  It is lossless because every acc in this filter
    fits in a signed 64-bit value, so the low 64 bits (w[1]<<32 | w[0])
    REINTERPRETED as int64 already carry the correct sign and magnitude; the
    high word w[2] is pure redundant sign extension and reconstructs no
    information.  (The pack80->reassemble80 self-check below proves this over the
    full +-2^47 range that actually occurs.)"""
    lsw = w[0] & MASK32                  # (uint32_t)w[0]
    msw = w[1] & MASK32                  # (uint32_t)w[1]
    acc = (msw << 32) | lsw              # low 64 bits
    if acc >= (1 << 63):                 # (int64_t) signed reinterpret -> sign already correct
        acc -= (1 << 64)
    return acc


def sat_i64_to_i32(v):
    return rr.sat32(v)


def fira_interp_pack80(prime_zs, frame_raw):
    """SINGLE_RATE FIR over zero-stuffed stream, but route acc through pack80+reassemble80."""
    ring = rr.Ring()
    for p in prime_zs:
        ring.push_raw_acc(int(p))
    out = []
    stream = []
    for x in frame_raw:
        stream.append(int(x)); stream.append(0)
    for x in stream:
        acc = ring.push_raw_acc(int(x))      # exact int64 MAC (same as core/FIRA)
        w = pack80(acc)                      # HW sec.38-10 writeback
        acc2 = reassemble80(w)               # our actual fira_reassemble80
        q31 = (acc2 >> 15) * 2               # current fira_postscale_int (b)+(c)
        out.append(sat_i64_to_i32(q31))      # (e)
    return out


def run_frame0_pack80():
    chirp = rr.load_chirp(rr.FRAME * 2)
    x = chirp[:rr.FRAME]
    f0 = rr.FRAME
    cdec = rr.Ring(); cint = rr.Ring()
    a1_core = rr.core_decimate2(cdec, x)
    r1_core = rr.core_interp2(cint, a1_core)
    sb3_core = [x[i] - r1_core[i] for i in range(f0)]

    a1_fira = rr.fira_decimate(x)
    prime_zs = [0] * rr.HIST
    r1_fira = fira_interp_pack80(prime_zs, a1_fira)
    sb3_fira = [x[i] - r1_fira[i] for i in range(f0)]
    return sb3_core, sb3_fira


if __name__ == "__main__":
    print("=== sec.38-10 3-word pack + fira_reassemble80 unpack (desktop [L2]) ===")
    print("BOARD sb3 core dump :", [hex(v) for v in rr.BOARD_CORE])
    print("BOARD sb3 residual  :", rr.BOARD_RES, "(fira-core)\n")

    # self-check pack/unpack identity for a range of accs that occur
    bad = 0
    for t in [0, 1, -1, 12345678, -12345678, (1 << 46) - 1, -(1 << 46),
              (1 << 47) + 3, -(1 << 47) - 7]:
        if reassemble80(pack80(t)) != t:
            print("  PACK/UNPACK MISMATCH at", t, "->", reassemble80(pack80(t)))
            bad += 1
    print("pack80->reassemble80 identity over 48-bit range : %s" % ("OK" if bad == 0 else "FAIL"))

    sb3_c, sb3_f = run_frame0_pack80()
    i0, cc, ff, res = rr.first_substantial_dump(sb3_c, sb3_f)
    core_match = (cc == rr.BOARD_CORE)
    res_match = (res == rr.BOARD_RES)
    print("our core sb3 dump   :", [hex(v & 0xffffffff) for v in cc], " match_board=", core_match)
    print("residual (fira-core):", res)
    print("REPRODUCES BOARD [0,-2,0,2,0,-2,0,6] ? ->", res_match)

    # also report max effective bit width of acc seen, to justify the "fits in 48 bits" claim
    ring = rr.Ring()
    chirp = rr.load_chirp(rr.FRAME * 2); x = chirp[:rr.FRAME]
    a1 = rr.fira_decimate(x)
    stream = rr.zero_stuff(a1)
    r2 = rr.Ring(); maxabs = 0
    for v in stream:
        a = r2.push_raw_acc(int(v)); maxabs = max(maxabs, abs(a))
    print("max |acc| over frame0 interp =", maxabs, "(needs %d bits)" % (maxabs.bit_length() + 1))
