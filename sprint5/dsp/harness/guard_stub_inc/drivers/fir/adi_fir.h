/* DESKTOP-ONLY mock of the BSP <drivers/fir/adi_fir.h> for the H1 guard-region syntax check.
 * NOT the real BSP header. fira_tree.h #includes this under FIRA_USE_REAL_ADI_FIR_HEADER; the H1
 * harness only uses FiraChannelState + the fira_* wrappers (raw adi_fir_* live in fira_tree.c, which
 * this check does NOT compile). So this mock provides just enough (the cache-line define + the handle
 * typedefs + the few enums/structs fira_tree.h names) for fira_tree.h to PARSE on a host.
 * See run_guard_check.sh for rationale (R16 gap closure). Never linked/run. */
#ifndef H1_MOCK_ADI_FIR_H
#define H1_MOCK_ADI_FIR_H
#include <stdint.h>

#ifndef ADI_CACHE_LINE_LENGTH
#define ADI_CACHE_LINE_LENGTH 32u
#endif

typedef void* ADI_FIR_DEV_HANDLE;
typedef void* ADI_FIR_TASK_HANDLE;
typedef int   ADI_FIR_RESULT;

typedef enum { ADI_FIR_SAMPLING_SINGLE_RATE, ADI_FIR_SAMPLING_DECIMATION,
               ADI_FIR_SAMPLING_INTERPOLATION } ADI_FIR_SAMPLING;
typedef enum { ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER,
               ADI_FIR_FIXED_INPUT_FORMAT_UNSIGNED_INTEGER } ADI_FIR_FIXED_INPUT_FORMAT;
typedef enum { ADI_FIR_EVENT_ALL_CHANNEL_DONE } ADI_FIR_EVENT;
typedef enum { ADI_FIR_RESULT_SUCCESS = 0, ADI_FIR_RESULT_FAILURE = 1 } ADI_FIR_RESULT_ENUM;

typedef struct {
    void    *pCoefficientBase;
    void    *pInputBase;
    void    *pOutputBase;
    uint32_t nInputBuffCount;
    uint32_t nOutputBuffCount;
    uint32_t nCoefficientCount;
    uint32_t nWindowSize;
    uint32_t nSamplingRatio;
    ADI_FIR_SAMPLING eSampling;
} ADI_FIR_CHANNEL_INFO;

#endif /* H1_MOCK_ADI_FIR_H */
