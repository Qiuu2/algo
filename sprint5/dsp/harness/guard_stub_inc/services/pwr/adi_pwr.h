/* DESKTOP-ONLY mock of the BSP <services/pwr/adi_pwr.h> for the H1 guard-region syntax check.
 * NOT the real BSP header. Resolves adi_pwr_GetCoreClkFreq so gcc -fsyntax-only can compile the
 * TARGET-guarded region of h1_wcet_measure.c on a host. See h1_guard_stub.h header for rationale. */
#ifndef H1_MOCK_ADI_PWR_H
#define H1_MOCK_ADI_PWR_H
#include <stdint.h>
typedef int ADI_PWR_RESULT;
static inline ADI_PWR_RESULT adi_pwr_GetCoreClkFreq(uint32_t dev, uint32_t *fcclk)
{
    (void)dev; if (fcclk) *fcclk = 1000000000u; return 0;
}
#endif
