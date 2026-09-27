/* wtbl_sums_host.c -- S7-SIDE30 M2_WTBL_SEL desktop check (host gcc, not firmware).
 * Prints the 8-weight Q15 sums of the frozen sel-0 table and of every g_m2_wtbl_q15 row, computed by the C compiler
 * from the SAME two headers the firmware includes (frozen dolph_w8_q15.h + generated m2_wtbl_q15.h).
 * run_wtbl_checks.sh step 4 compares this line with the sums table the tester reads in S7_TESTER_RUNBOOK_WTBL.md,
 * so the numbers g_m2_wtbl_applied_sum is checked against cannot drift from the headers. [L2 desktop identity] */
#include <stdio.h>
#include "dolph_w8_q15.h"
#include "m2_wtbl_q15.h"

int main(void)
{
    long s = 0;
    for (int c = 0; c < DOLPH_W8_NCH; c++)
        s += g_dolph_w8_q15[c];
    printf("%ld", s);
    for (int k = 0; k < M2_WTBL_NEXTRA; k++) {
        long t = 0;
        for (int c = 0; c < DOLPH_W8_NCH; c++)
            t += g_m2_wtbl_q15[k][c];
        printf(" %ld", t);
    }
    printf("\n");
    return 0;
}
