/* DESKTOP-ONLY parse-stub of BSP <drivers/sport/adi_sport.h> for the M1 guard-region syntax check.
 * NOT the real BSP header. Mirrors the [L1] symbols CALLED in Audio_Loopback_TDM.c (ALT.c, file:line
 * in M1_SYMBOL_PRESURVEY.md sec A1). Parse-time stand-ins only; no real SPORT behavior. */
#ifndef M1_MOCK_DRIVERS_SPORT_ADI_SPORT_H
#define M1_MOCK_DRIVERS_SPORT_ADI_SPORT_H
#include <stdint.h>
#include <stdbool.h>

#define ADI_SPORT_MEMORY_SIZE 256u
typedef void *ADI_SPORT_HANDLE;
typedef int   ADI_SPORT_RESULT;
#define ADI_SPORT_SUCCESS 0

typedef enum { ADI_HALF_SPORT_A = 0, ADI_HALF_SPORT_B = 1 } ADI_SPORT_CHANNEL_DIR_MOCK;
typedef enum { ADI_SPORT_DIR_TX = 0, ADI_SPORT_DIR_RX = 1 } ADI_SPORT_DIRECTION_MOCK;
typedef enum { ADI_SPORT_MC_MODE = 0 } ADI_SPORT_MODE_MOCK;
typedef enum { ADI_SPORT_DTYPE_SIGN_FILL = 0 } ADI_SPORT_DTYPE_MOCK;
typedef enum { ADI_SPORT_CHANNEL_PRIM = 0 } ADI_SPORT_CHANNEL_MOCK;
typedef enum { ADI_PDMA_DESCRIPTOR_LIST = 0 } ADI_SPORT_XFER_MODE_MOCK;
#define ADI_SPORT_EVENT_RX_BUFFER_PROCESSED 1u

typedef void (*ADI_CALLBACK)(void *pAppHandle, uint32_t nEvent, void *pArg);

static inline ADI_SPORT_RESULT adi_sport_Open(uint32_t dev, int half, int dir, int mode,
                                              void *pMem, uint32_t nMem, ADI_SPORT_HANDLE *ph)
{ (void)dev;(void)half;(void)dir;(void)mode;(void)nMem; if (ph) { *ph = (ADI_SPORT_HANDLE)pMem; } return 0; }
static inline ADI_SPORT_RESULT adi_sport_ConfigData(ADI_SPORT_HANDLE h, int t, int w, bool a, bool b, bool c)
{ (void)h;(void)t;(void)w;(void)a;(void)b;(void)c; return 0; }
static inline ADI_SPORT_RESULT adi_sport_ConfigClock(ADI_SPORT_HANDLE h, int ck, bool a, bool b, bool c)
{ (void)h;(void)ck;(void)a;(void)b;(void)c; return 0; }
static inline ADI_SPORT_RESULT adi_sport_ConfigFrameSync(ADI_SPORT_HANDLE h, int fs, bool a, bool b, bool c, bool d, bool e, bool f)
{ (void)h;(void)fs;(void)a;(void)b;(void)c;(void)d;(void)e;(void)f; return 0; }
static inline ADI_SPORT_RESULT adi_sport_ConfigMC(ADI_SPORT_HANDLE h, uint8_t mfd, uint8_t wsz, uint8_t wo, bool en)
{ (void)h;(void)mfd;(void)wsz;(void)wo;(void)en; return 0; }
static inline ADI_SPORT_RESULT adi_sport_SelectChannel(ADI_SPORT_HANDLE h, uint8_t a, uint8_t b)
{ (void)h;(void)a;(void)b; return 0; }
static inline ADI_SPORT_RESULT adi_sport_RegisterCallback(ADI_SPORT_HANDLE h, ADI_CALLBACK cb, void *p)
{ (void)h;(void)cb;(void)p; return 0; }
static inline ADI_SPORT_RESULT adi_sport_DMATransfer(ADI_SPORT_HANDLE h, void *pDesc, uint32_t n, int mode, int ch)
{ (void)h;(void)pDesc;(void)n;(void)mode;(void)ch; return 0; }
static inline ADI_SPORT_RESULT adi_sport_Enable(ADI_SPORT_HANDLE h, bool en) { (void)h;(void)en; return 0; }
static inline ADI_SPORT_RESULT adi_sport_StopDMATransfer(ADI_SPORT_HANDLE h) { (void)h; return 0; }
static inline ADI_SPORT_RESULT adi_sport_Close(ADI_SPORT_HANDLE h) { (void)h; return 0; }

#endif
