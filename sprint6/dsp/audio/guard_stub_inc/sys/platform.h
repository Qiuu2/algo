/* DESKTOP-ONLY parse-stub of BSP <sys/platform.h> for the M1 SRU guard-region syntax check.
 * NOT the real BSP header. Resolves the pREG_PADS0_DAI*_IE register pointers used in m1_sru.c.
 * Parse-time stand-ins only; the addresses are dummies (no real MMIO on host). */
#ifndef M1_MOCK_SYS_PLATFORM_H
#define M1_MOCK_SYS_PLATFORM_H
#include <stdint.h>
/* DAI port input-enable registers (real ones are volatile MMIO in the BSP header) */
static volatile unsigned int m1_mock_pads0_dai0_ie;
static volatile unsigned int m1_mock_pads0_dai1_ie;
#define pREG_PADS0_DAI0_IE (&m1_mock_pads0_dai0_ie)
#define pREG_PADS0_DAI1_IE (&m1_mock_pads0_dai1_ie)
#endif
