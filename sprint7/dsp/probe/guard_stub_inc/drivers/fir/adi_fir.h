/* DESKTOP-ONLY parse stub of the BSP <drivers/fir/adi_fir.h> (Legacy mode) for the S7 probe guard check.
 * NOT the real BSP header; never linked or run. It is a field-for-field TRANSCRIPTION of the archived real
 * Legacy header knowledge_base/ezkit/bsp/fira_headers/adi_fir_legacy_2156x.h (:15-18 macros, :20-21 handles,
 * :24-43 enums, :46-54 ADI_FIR_CHANNEL_INFO in the SAME field order, :57-61 BUFFER_INFO, :63 events, :66-79 the
 * 10 API functions), so that gcc -fsyntax-only can parse the TARGET-guarded body of the diagnostic copy
 * fira_tree_probe.c (which -- unlike the sprint5 harness files -- calls the raw adi_fir_* API and fills every
 * CHANNEL_INFO field). The sprint5 stub (sprint5/dsp/harness/guard_stub_inc/drivers/fir/adi_fir.h) is too
 * thin for that (different field set, no FIR_MEM_SIZE, no API prototypes).
 * ADI_CALLBACK is declared AFTER ADI_FIR_EVENT with the event parameter typed as ADI_FIR_EVENT, matching the
 * callback signature fira_tree.c (fira_done_cb) and ADI's own example (FIR_Multi_Channel_Processing.c:94) use.
 * See run_s7_probe_guard_check.sh. */
#ifndef S7_MOCK_ADI_FIR_H
#define S7_MOCK_ADI_FIR_H
#include <stdint.h>

#ifndef ADI_CACHE_LINE_LENGTH
#define ADI_CACHE_LINE_LENGTH 32u
#endif

#define ADI_FIR_TASK_INFO_SIZE   (28u + ADI_CACHE_LINE_LENGTH)
#define ADI_FIR_TCB_INFO_SIZE    (52u)
#define FIR_MEM_SIZE(NO_OF_CHANNELS) (ADI_FIR_TASK_INFO_SIZE + ((NO_OF_CHANNELS) * ADI_FIR_TCB_INFO_SIZE))

typedef void* ADI_FIR_DEV_HANDLE;
typedef void* ADI_FIR_TASK_HANDLE;

typedef enum { ADI_FIR_TASK_STATE_NONE, ADI_FIR_TASK_STATE_QUEUED,
               ADI_FIR_TASK_STATE_RUNNING, ADI_FIR_TASK_STATE_COMPLETED } ADI_FIR_TASK_STATE;

typedef enum { ADI_FIR_RESULT_SUCCESS, ADI_FIR_RESULT_FAILED, ADI_FIR_RESULT_INVALID_HANDLE,
               ADI_FIR_RESULT_INVALID_STATE, ADI_FIR_RESULT_INVALID_OPERATION,
               ADI_FIR_RESULT_TASK_STATE_RUNNING } ADI_FIR_RESULT;

typedef enum { ADI_FIR_SAMPLING_SINGLE_RATE, ADI_FIR_SAMPLING_DECIMATION,
               ADI_FIR_SAMPLING_INTERPOLATION } ADI_FIR_SAMPLING;

typedef enum { ADI_FIR_FLOAT_ROUNDING_MODE_IEEE_ROUND_TO_NEAREST_EVEN = 0,
               ADI_FIR_FLOAT_ROUNDING_MODE_IEEE_ROUND_TO_ZERO         = 1 } ADI_FIR_FLOAT_ROUNDING_MODE;

typedef enum { ADI_FIR_FIXED_INPUT_FORMAT_UNSIGNED_INTEGER,
               ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER } ADI_FIR_FIXED_INPUT_FORMAT;

typedef struct {
    uint32_t  nTapLength;
    uint32_t  nWindowSize;
    ADI_FIR_SAMPLING eSampling;
    uint32_t  nSamplingRatio;
    uint32_t  nCoefficientCount;   void* pCoefficientIndex;  int32_t nCoefficientModify;
    void*  pOutputBuffBase;  uint32_t nOutputBuffCount;  int32_t nOutputBuffModify;  void* pOutputBuffIndex;
    void*  pInputBuffBase;   uint32_t nInputBuffCount;   int32_t nInputBuffModify;   void* pInputBuffIndex;
} ADI_FIR_CHANNEL_INFO;

typedef struct {
    void* pOutputBuffBase; uint32_t nOutputBuffCount; int32_t nOutputBuffModify; void* pOutputBuffIndex;
    void* pInputBuffBase;  uint32_t nInputBuffCount;  int32_t nInputBuffModify;  void* pInputBuffIndex;
} ADI_FIR_CHANNEL_BUFFER_INFO;

typedef enum { ADI_FIR_EVENT_CHANNEL_DONE, ADI_FIR_EVENT_ALL_CHANNEL_DONE } ADI_FIR_EVENT;

typedef void (*ADI_CALLBACK)(void *pCBParam, ADI_FIR_EVENT Event, void *pArg);

ADI_FIR_RESULT adi_fir_Open(uint8_t nDeviceNum, ADI_FIR_DEV_HANDLE *phFirHandle);
ADI_FIR_RESULT adi_fir_CreateTask(ADI_FIR_DEV_HANDLE hFirHandle, ADI_FIR_CHANNEL_INFO *pChannelList,
                                  uint32_t nNumChannels, void *pMemory, uint32_t nMemSize,
                                  ADI_FIR_TASK_HANDLE *phFirTask);
ADI_FIR_RESULT adi_fir_QueueTask(ADI_FIR_TASK_HANDLE hFirTask);
ADI_FIR_RESULT adi_fir_DeleteTask(ADI_FIR_TASK_HANDLE hFirTask);
ADI_FIR_RESULT adi_fir_GetFirTaskStatus(ADI_FIR_TASK_HANDLE hFirTask, ADI_FIR_TASK_STATE *TaskStatus);
ADI_FIR_RESULT adi_fir_FixedPointEnable(ADI_FIR_TASK_HANDLE hFirTask, ADI_FIR_FIXED_INPUT_FORMAT eInputFormat);
ADI_FIR_RESULT adi_fir_FloatingPointEnable(ADI_FIR_TASK_HANDLE hFirTask, ADI_FIR_FLOAT_ROUNDING_MODE eRoundingMode);
ADI_FIR_RESULT adi_fir_Close(ADI_FIR_DEV_HANDLE hFirHandle);
ADI_FIR_RESULT adi_fir_RegisterCallback(ADI_FIR_DEV_HANDLE hFirHandle, ADI_CALLBACK pfCallback, void *pCBParam);
ADI_FIR_RESULT adi_fir_UpdateTask(ADI_FIR_TASK_HANDLE hFirTask, ADI_FIR_CHANNEL_BUFFER_INFO *pChannelParamsList,
                                  uint32_t nNumChannels);

#endif /* S7_MOCK_ADI_FIR_H */
