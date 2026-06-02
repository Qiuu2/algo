# core-only S0-S1 host bit-exact 预验 Makefile  [L2 host 预验]
# 算法核 tree_filterbank.c/h verbatim 复制 (md5 一致), 不修改。
CC      ?= gcc
CFLAGS  := -O2 -Wall -Iinclude -Isrc
LDLIBS  := -lm
SRC_CORE := src/tree_filterbank.c src/tfb_8ch.c
HARNESS  := host/host_bitexact.c

.PHONY: all gen coeffs sat unsat run clean

all: sat unsat

# 重新生成冻结系数头 (一次性; 提交后无需重跑)
coeffs: host/gen_hb63.c
	$(CC) -O2 -o /tmp/gen_hb63 host/gen_hb63.c $(LDLIBS)
	/tmp/gen_hb63 > include/fir_coeffs_hb63.h

host_bitexact_sat: $(HARNESS) $(SRC_CORE) include/fir_coeffs_hb63.h
	$(CC) $(CFLAGS) -o $@ $(HARNESS) $(SRC_CORE) $(LDLIBS)

host_bitexact_unsat: $(HARNESS) $(SRC_CORE) include/fir_coeffs_hb63.h
	$(CC) $(CFLAGS) -DTFB_DISABLE_SAT -o $@ $(HARNESS) $(SRC_CORE) $(LDLIBS)

sat:   host_bitexact_sat
unsat: host_bitexact_unsat

run: sat unsat
	@echo "===== SAT 套 ====="   ; ./host_bitexact_sat   ; echo "(exit=$$?)"
	@echo "===== UNSAT 套 =====" ; ./host_bitexact_unsat ; echo "(exit=$$?)"

clean:
	rm -f host_bitexact_sat host_bitexact_unsat /tmp/gen_hb63
