/* DESKTOP-ONLY parse-stub of BSP <services/pwr/adi_pwr.h> for the M1 main guard-region syntax check.
 * NOT the real BSP header. Resolves adi_pwr_Init (startup power-service init). Mirrors the sprint5 stub. */
#ifndef M1_MOCK_ADI_PWR_H
#define M1_MOCK_ADI_PWR_H
#include <stdint.h>
typedef int ADI_PWR_RESULT;
static inline ADI_PWR_RESULT adi_pwr_Init(uint32_t dev, uint32_t clkin)
{ (void)dev; (void)clkin; return 0; }
#endif
