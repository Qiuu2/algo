/* DESKTOP-ONLY parse-stub of BSP <services/spu/adi_spu.h> for the M1 guard-region syntax check.
 * NOT the real BSP header. Mirrors the [L1] adi_spu_* symbols CALLED in ALT.c:453-476. */
#ifndef M1_MOCK_SERVICES_SPU_ADI_SPU_H
#define M1_MOCK_SERVICES_SPU_ADI_SPU_H
#include <stdint.h>
#include <stdbool.h>

#define ADI_SPU_MEMORY_SIZE 64u
typedef void *ADI_SPU_HANDLE;
typedef int   ADI_SPU_RESULT;
#define ADI_SPU_SUCCESS 0

static inline ADI_SPU_RESULT adi_spu_Init(uint32_t dev, void *pMem, void *a, void *b, ADI_SPU_HANDLE *ph)
{ (void)dev;(void)a;(void)b; if (ph) { *ph = (ADI_SPU_HANDLE)pMem; } return 0; }
static inline ADI_SPU_RESULT adi_spu_EnableMasterSecure(ADI_SPU_HANDLE h, uint32_t id, bool en)
{ (void)h;(void)id;(void)en; return 0; }

#endif
