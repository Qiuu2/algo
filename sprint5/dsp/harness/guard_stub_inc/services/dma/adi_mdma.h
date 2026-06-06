/* DESKTOP-ONLY parse-stub of the BSP <services/dma/adi_mdma.h> for the H2 board-hook guard-region
 * syntax check. NOT the real BSP header. Resolves the adi_mdma_* mem-to-mem service symbols NAMED in
 *   knowledge_base/ezkit/vendor_docs/cces_examples/code/Power_On_Self_Test/EZ-Board/21569/sharc/system/
 *     services/dma/adi_mdma_config_2156x.h  (adi_mdma_Copy1D, adi_mdma_CopyList)
 * so gcc -fsyntax-only can compile the TARGET-guarded region of h2_board_hooks_21569som.c on a host.
 * NOTE: no local example CALLS the MDMA API, so the exact open/Copy1D signatures here are the documented
 * shape and are flagged [board-confirm] in the hook source. Parse-time stand-ins only; no real behavior. */
#ifndef H2_MOCK_SERVICES_DMA_ADI_MDMA_H
#define H2_MOCK_SERVICES_DMA_ADI_MDMA_H
#include <stdint.h>

#define ADI_MDMA_MEMORY 256u
typedef void *ADI_MDMA_HANDLE;
typedef int   ADI_MDMA_RESULT;
#define ADI_MDMA_SUCCESS 0

/* MSIZE enum (transfer element width); ADI_DMA_MSIZE_4BYTES = 32-bit words. */
typedef enum { ADI_DMA_MSIZE_4BYTES = 2 } ADI_DMA_MSIZE;

typedef void (*ADI_MDMA_CALLBACK)(void *pCBParam, uint32_t nEvent, void *pArg);

static inline ADI_MDMA_RESULT adi_mdma_Open(uint32_t streamID, void *pMemory, uint32_t nMemSize,
                                            ADI_MDMA_CALLBACK cb, void *pCBParam, ADI_MDMA_HANDLE *phStream)
{ (void)streamID; (void)pMemory; (void)nMemSize; (void)cb; (void)pCBParam;
  if (phStream) { *phStream = (ADI_MDMA_HANDLE)pMemory; } return ADI_MDMA_SUCCESS; }

static inline ADI_MDMA_RESULT adi_mdma_Copy1D(ADI_MDMA_HANDLE h, void *pDst, void *pSrc,
                                              ADI_DMA_MSIZE msize, uint32_t count)
{ (void)h; (void)pDst; (void)pSrc; (void)msize; (void)count; return ADI_MDMA_SUCCESS; }

static inline ADI_MDMA_RESULT adi_mdma_Close(ADI_MDMA_HANDLE h)
{ (void)h; return ADI_MDMA_SUCCESS; }

#endif
