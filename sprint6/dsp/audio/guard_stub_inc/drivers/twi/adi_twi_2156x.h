/* DESKTOP-ONLY parse-stub of BSP <drivers/twi/adi_twi_2156x.h> for the M1 guard-region syntax check.
 * NOT the real BSP header. Mirrors the [L1] adi_twi_* symbols CALLED in ALT.c:478-556. */
#ifndef M1_MOCK_DRIVERS_TWI_ADI_TWI_2156X_H
#define M1_MOCK_DRIVERS_TWI_ADI_TWI_2156X_H
#include <stdint.h>
#include <stdbool.h>

#define ADI_TWI_MEMORY_SIZE 64u
typedef void *ADI_TWI_HANDLE;
typedef int   ADI_TWI_RESULT;
#define ADI_TWI_SUCCESS 0
typedef enum { ADI_TWI_MASTER = 0 } ADI_TWI_MODE_MOCK;

static inline ADI_TWI_RESULT adi_twi_Open(uint32_t dev, int mode, void *pMem, uint32_t n, ADI_TWI_HANDLE *ph)
{ (void)dev;(void)mode;(void)n; if (ph) { *ph = (ADI_TWI_HANDLE)pMem; } return 0; }
static inline ADI_TWI_RESULT adi_twi_SetPrescale(ADI_TWI_HANDLE h, uint32_t v) { (void)h;(void)v; return 0; }
static inline ADI_TWI_RESULT adi_twi_SetBitRate(ADI_TWI_HANDLE h, uint32_t v) { (void)h;(void)v; return 0; }
static inline ADI_TWI_RESULT adi_twi_SetDutyCycle(ADI_TWI_HANDLE h, uint32_t v) { (void)h;(void)v; return 0; }
static inline ADI_TWI_RESULT adi_twi_SetHardwareAddress(ADI_TWI_HANDLE h, uint32_t a) { (void)h;(void)a; return 0; }
static inline ADI_TWI_RESULT adi_twi_Write(ADI_TWI_HANDLE h, void *buf, uint32_t n, bool rs)
{ (void)h;(void)buf;(void)n;(void)rs; return 0; }
static inline ADI_TWI_RESULT adi_twi_Read(ADI_TWI_HANDLE h, void *buf, uint32_t n, bool rs)
{ (void)h;(void)buf;(void)n;(void)rs; return 0; }
static inline ADI_TWI_RESULT adi_twi_Close(ADI_TWI_HANDLE h) { (void)h; return 0; }

static inline ADI_TWI_RESULT adi_twi_GetHWErrorStatus(ADI_TWI_HANDLE h, uint32_t *pErr){ (void)h; if(pErr){*pErr=0u;} return 0; }
#endif
