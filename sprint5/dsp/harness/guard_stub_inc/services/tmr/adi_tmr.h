/* DESKTOP-ONLY parse-stub of the BSP <services/tmr/adi_tmr.h> for the H2 board-hook guard-region
 * syntax check. NOT the real BSP header. Resolves the adi_tmr_* service symbols PROVEN in
 *   knowledge_base/ezkit/vendor_docs/cces_examples/code/Power_On_Self_Test/common/source/TimerDelay.c
 * so gcc -fsyntax-only can compile the TARGET-guarded region of h2_board_hooks_21569som.c on a host.
 * Signatures mirror that real [L1] usage (Open/SetWidth/SetDelay/Enable/Close + ADI_TMR_* enums/macros).
 * Mocks are parse-time stand-ins only; they carry NO real timer behavior. */
#ifndef H2_MOCK_SERVICES_TMR_ADI_TMR_H
#define H2_MOCK_SERVICES_TMR_ADI_TMR_H
#include <stdint.h>
#include <stdbool.h>

#define ADI_TMR_MEMORY 64u
typedef void *ADI_TMR_HANDLE;
typedef int   ADI_TMR_RESULT;
#define ADI_TMR_SUCCESS 0

/* event enum (TimerDelay.c switches on ADI_TMR_EVENT_DATA_INT) */
typedef enum { ADI_TMR_EVENT_DATA_INT = 0 } ADI_TMR_EVENT;

typedef void (*ADI_CALLBACK)(void *pCBParam, uint32_t nEvent, void *pArg);

static inline ADI_TMR_RESULT adi_tmr_Open(uint32_t devnum, void *pMemory, uint32_t nMemSize,
                                          ADI_CALLBACK cb, void *pCBParam, ADI_TMR_HANDLE *phDevice)
{ (void)devnum; (void)pMemory; (void)nMemSize; (void)cb; (void)pCBParam;
  if (phDevice) { *phDevice = (ADI_TMR_HANDLE)pMemory; } return ADI_TMR_SUCCESS; }

static inline ADI_TMR_RESULT adi_tmr_SetWidth(ADI_TMR_HANDLE h, uint32_t w)
{ (void)h; (void)w; return ADI_TMR_SUCCESS; }

static inline ADI_TMR_RESULT adi_tmr_SetDelay(ADI_TMR_HANDLE h, uint32_t d)
{ (void)h; (void)d; return ADI_TMR_SUCCESS; }

static inline ADI_TMR_RESULT adi_tmr_Enable(ADI_TMR_HANDLE h, bool en)
{ (void)h; (void)en; return ADI_TMR_SUCCESS; }

static inline ADI_TMR_RESULT adi_tmr_Close(ADI_TMR_HANDLE h)
{ (void)h; return ADI_TMR_SUCCESS; }

#endif
