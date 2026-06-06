/* DESKTOP-ONLY parse-stub of the BSP <services/dma/adi_mdma_2156x.h> for the H2 board-hook guard-region
 * syntax check. NOT the real BSP header. Mirrors the [L1] contract CTO grepped from the installed
 *   C:\...\SHARC\include\services\dma\adi_mdma_2156x.h  (CCES 2.12.1, 2026-06-06), line numbers in comments.
 * Resolves the STREAM+CHANNEL handle model + 7-arg adi_mdma_Open so gcc -fsyntax-only compiles the
 * TARGET-guarded Block 1 of h2_board_hooks_21569som.c on a host AGAINST THE NEW SYMBOLS (not the old
 * single-handle shape). Parse-time stand-ins only; no real DMA behavior. */
#ifndef H2_MOCK_SERVICES_DMA_ADI_MDMA_2156X_H
#define H2_MOCK_SERVICES_DMA_ADI_MDMA_2156X_H
#include <stdint.h>
#include <stdbool.h>

/* :242 result type is ADI_DMA_RESULT (NOT ADI_MDMA_RESULT); success = 0 */
typedef int ADI_DMA_RESULT;
#define ADI_DMA_SUCCESS 0

/* :125 MSIZE element width enum; 4BYTES = 32-bit words */
typedef enum { ADI_DMA_MSIZE_4BYTES = 2 } ADI_DMA_MSIZE;

/* :88 stream id enum; first mem-to-mem stream */
typedef enum { ADI_DMA_MEMDMA_S0 = 0 } ADI_DMA_STREAM_ID;

/* :69 stream handle / :64 channel handle (both typedef void*) */
typedef void *ADI_DMA_STREAM_HANDLE;
typedef void *ADI_DMA_CHANNEL_HANDLE;

/* :56 stream memory size */
#define ADI_DMA_STREAM_REQ_MEMORY 96u

/* ADI_CALLBACK: void(void*,uint32_t,void*) -- the platform shape (TimerDelay.c passes such a fn, no cast) */
typedef void (*ADI_CALLBACK)(void *pCBParam, uint32_t nEvent, void *pArg);

/* :269 adi_mdma_Open -- 7 args, strict order: stream id, stream memory, &stream, &srcChannel,
 *      &destChannel, callback, cbParam */
static inline ADI_DMA_RESULT adi_mdma_Open(ADI_DMA_STREAM_ID eStreamID, void *pStreamMemory,
                                           ADI_DMA_STREAM_HANDLE *phStream,
                                           ADI_DMA_CHANNEL_HANDLE *phSrcChannel,
                                           ADI_DMA_CHANNEL_HANDLE *phDestChannel,
                                           ADI_CALLBACK pfCallback, void *pCBParam)
{ (void)eStreamID; (void)pCBParam; (void)pfCallback;
  if (phStream)      { *phStream = (ADI_DMA_STREAM_HANDLE)pStreamMemory; }
  if (phSrcChannel)  { *phSrcChannel = (ADI_DMA_CHANNEL_HANDLE)pStreamMemory; }
  if (phDestChannel) { *phDestChannel = (ADI_DMA_CHANNEL_HANDLE)pStreamMemory; }
  return ADI_DMA_SUCCESS; }

/* :293 adi_mdma_Copy1D(hStream, dest, src, msize, count) */
static inline ADI_DMA_RESULT adi_mdma_Copy1D(ADI_DMA_STREAM_HANDLE hStream, void *pMemDest, void *pMemSrc,
                                             ADI_DMA_MSIZE eElementWidth, uint32_t ElementCount)
{ (void)hStream; (void)pMemDest; (void)pMemSrc; (void)eElementWidth; (void)ElementCount;
  return ADI_DMA_SUCCESS; }

/* :290 adi_mdma_Disable(hStream) -- abort in-flight transfer */
static inline ADI_DMA_RESULT adi_mdma_Disable(ADI_DMA_STREAM_HANDLE hStream)
{ (void)hStream; return ADI_DMA_SUCCESS; }

/* :279 adi_mdma_Close(hStream, bWaitFlag) */
static inline ADI_DMA_RESULT adi_mdma_Close(ADI_DMA_STREAM_HANDLE hStream, bool bWaitFlag)
{ (void)hStream; (void)bWaitFlag; return ADI_DMA_SUCCESS; }

#endif
