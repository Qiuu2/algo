/* DESKTOP-ONLY parse-stub of BSP <sru21569.h> for the M1 SRU guard-region syntax check.
 * NOT the real BSP header. The real one defines SRU2() to expand to DAI1 routing-register writes and
 * defines hundreds of DAI1 and SPT4 connection-point tokens. For -fsyntax-only we only need the tokens
 * used by m1_sru.c to RESOLVE so the routing calls parse. SRU2 is a parse-only no-op consuming 2 args.
 *
 * NOTE [board-confirm]: this stub CANNOT validate that a given (source,dest) pair is a LEGAL SRU route
 * (the real header per-group encoding is not reproduced). Route correctness is proven by the R39 table
 * plus board bring-up (signal reaches the codec), NOT by this guard-check. The guard-check only proves
 * the routing TU parses and the token names are spelled right. */
#ifndef M1_MOCK_SRU21569_H
#define M1_MOCK_SRU21569_H

/* parse-only SRU2: consume both args, do nothing (real one writes routing regs) */
#define SRU2(src, dst)  do { (void)(src); (void)(dst); } while (0)

/* connection-point tokens used by m1_sru.c (values are dummies; only the NAMES must resolve) */
#define LOW                0
#define HIGH               1

#define DAI1_PB02_I        1
#define DAI1_PB04_O        2
#define DAI1_PB05_O        3
#define DAI1_PB06_O        4
#define DAI1_PB12_I        5
#define DAI1_PB20_I        6

#define DAI1_PBEN02_I      10
#define DAI1_PBEN04_I      11
#define DAI1_PBEN05_I      12
#define DAI1_PBEN06_I      13
#define DAI1_PBEN12_I      14
#define DAI1_PBEN20_I      15

#define SPT4_ACLK_I        20
#define SPT4_BCLK_I        21
#define SPT4_AFS_I         22
#define SPT4_BFS_I         23
#define SPT4_AD0_O         24
#define SPT4_BD0_I         25

#endif
