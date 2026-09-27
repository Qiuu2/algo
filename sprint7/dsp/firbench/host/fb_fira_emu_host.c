/*
 * fb_fira_emu_host.c -- DESKTOP-ONLY behavioural model of the Legacy adi_fir_* API, used ONLY to exercise the FIRA
 * orchestration code of s7_firbench.c on a host (buffer layout, history, index arithmetic, postscale, IO1 sentinel
 * check). It is NOT the hardware and NOT evidence about the hardware: a host PASS through this model is
 * [L2 emulated plumbing]; the board run is the only judge [L1]. Never linked into a target build.
 *
 * Model (each item is an ASSUMPTION the board confirms or refutes through the goldens):
 *   - one ALL_CHANNEL_DONE callback per queued task, after all its channels (MCP.c:103);
 *   - fixed point only after adi_fir_FixedPointEnable(SIGNED_INTEGER) (else outputs 0 -> the goldens FAIL);
 *   - SINGLE_RATE: output j = sum_k coef[k] * in[(idx + j + ntaps - 1 - k) mod count] (symmetric sets: orientation moot);
 *   - exact 64-bit accumulate, written as 3 words LSW / MSW / sign word (DP-01 layout, low 64 bits exact);
 *   - [ASSUME P1-IDX] after a run the channel's input index advances by nWindowSize mod nInputBuffCount and the
 *     output index by 3*nWindowSize mod nOutputBuffCount; CreateTask resets them from the CHANNEL_INFO.
 * -DFB_EMU_STUB: the "accelerator" writes NOTHING but still signals DONE (the placeholder/stub case that FG2 says
 *   must FAIL) -> every FIRA path must miss its goldens and the IO1 sentinel check must fail.
 * Header: sprint7/dsp/probe/guard_stub_inc/drivers/fir/adi_fir.h (Legacy transcription). ASCII-only.
 */
#include <stdint.h>
#include <string.h>
#include <drivers/fir/adi_fir.h>

#define EMU_MAXTASK 4
#define EMU_MAXCH   8

typedef struct {
    void                *mem;
    int                  fixed;
    uint32_t             nch;
    ADI_FIR_CHANNEL_INFO ci[EMU_MAXCH];
    uint32_t             iidx[EMU_MAXCH];
    uint32_t             oidx[EMU_MAXCH];
} EmuTask;

static EmuTask      s_task[EMU_MAXTASK];
static ADI_CALLBACK s_cb;
static void        *s_cbp;
static int          s_open;

ADI_FIR_RESULT adi_fir_Open(uint8_t nDeviceNum, ADI_FIR_DEV_HANDLE *phFirHandle)
{
    (void)nDeviceNum;
    if (s_open) return ADI_FIR_RESULT_FAILED;
    s_open = 1; memset(s_task, 0, sizeof(s_task)); *phFirHandle = (void *)&s_open;
    return ADI_FIR_RESULT_SUCCESS;
}

ADI_FIR_RESULT adi_fir_RegisterCallback(ADI_FIR_DEV_HANDLE h, ADI_CALLBACK pfCallback, void *pCBParam)
{
    if (h != (void *)&s_open || !s_open) return ADI_FIR_RESULT_INVALID_HANDLE;
    s_cb = pfCallback; s_cbp = pCBParam;
    return ADI_FIR_RESULT_SUCCESS;
}

ADI_FIR_RESULT adi_fir_CreateTask(ADI_FIR_DEV_HANDLE h, ADI_FIR_CHANNEL_INFO *pList, uint32_t n, void *pMem,
                                  uint32_t nMemSize, ADI_FIR_TASK_HANDLE *phTask)
{
    int i, slot = -1;
    uint32_t c;
    if (h != (void *)&s_open || !s_open) return ADI_FIR_RESULT_INVALID_HANDLE;
    if (n == 0u || n > EMU_MAXCH || nMemSize < (uint32_t)FIR_MEM_SIZE(n) || pMem == 0) return ADI_FIR_RESULT_FAILED;
    for (i = 0; i < EMU_MAXTASK; i++) if (s_task[i].mem == pMem) slot = i;          /* same memory = re-create */
    for (i = 0; i < EMU_MAXTASK && slot < 0; i++) if (s_task[i].mem == 0) slot = i;
    if (slot < 0) return ADI_FIR_RESULT_FAILED;
    memset(&s_task[slot], 0, sizeof(EmuTask));
    s_task[slot].mem = pMem; s_task[slot].nch = n;
    for (c = 0; c < n; c++) {
        s_task[slot].ci[c]   = pList[c];
        s_task[slot].iidx[c] = (uint32_t)((int32_t *)pList[c].pInputBuffIndex - (int32_t *)pList[c].pInputBuffBase);
        s_task[slot].oidx[c] = (uint32_t)((int32_t *)pList[c].pOutputBuffIndex - (int32_t *)pList[c].pOutputBuffBase);
        if (s_task[slot].iidx[c] >= pList[c].nInputBuffCount) return ADI_FIR_RESULT_FAILED;
        if (pList[c].nOutputBuffCount < 3u * pList[c].nWindowSize) return ADI_FIR_RESULT_FAILED;   /* DP-01 x3 */
        if (pList[c].nInputBuffCount < pList[c].nTapLength + pList[c].nWindowSize - 1u) return ADI_FIR_RESULT_FAILED; /* IO1a */
    }
    *phTask = (void *)&s_task[slot];
    return ADI_FIR_RESULT_SUCCESS;
}

ADI_FIR_RESULT adi_fir_FixedPointEnable(ADI_FIR_TASK_HANDLE hTask, ADI_FIR_FIXED_INPUT_FORMAT eInputFormat)
{
    EmuTask *t = (EmuTask *)hTask;
    if (t == 0) return ADI_FIR_RESULT_INVALID_HANDLE;
    t->fixed = (eInputFormat == ADI_FIR_FIXED_INPUT_FORMAT_SIGNED_INTEGER) ? 1 : 2;
    return ADI_FIR_RESULT_SUCCESS;
}

ADI_FIR_RESULT adi_fir_QueueTask(ADI_FIR_TASK_HANDLE hTask)
{
    EmuTask *t = (EmuTask *)hTask;
    uint32_t c, j, k;
    if (t == 0 || !s_open) return ADI_FIR_RESULT_INVALID_HANDLE;
    for (c = 0; c < t->nch; c++) {
        const ADI_FIR_CHANNEL_INFO *ci = &t->ci[c];
        const int32_t *in = (const int32_t *)ci->pInputBuffBase;
        const int32_t *cf = (const int32_t *)ci->pCoefficientIndex;
        int32_t *out = (int32_t *)ci->pOutputBuffBase;
        const uint32_t L = ci->nInputBuffCount, N = ci->nTapLength, W = ci->nWindowSize, OC = ci->nOutputBuffCount;
#ifndef FB_EMU_STUB
        for (j = 0; j < W; j++) {
            int64_t acc = 0;
            uint32_t o = (t->oidx[c] + 3u * j) % OC;
            if (t->fixed == 1)
                for (k = 0; k < N; k++) acc += (int64_t)cf[k] * (int64_t)in[(t->iidx[c] + j + N - 1u - k) % L];
            out[o]            = (int32_t)(uint32_t)((uint64_t)acc & 0xFFFFFFFFu);
            out[(o + 1u) % OC] = (int32_t)(uint32_t)((uint64_t)acc >> 32);
            out[(o + 2u) % OC] = (acc < 0) ? -1 : 0;
        }
#else
        (void)in; (void)cf; (void)out; (void)N; (void)j; (void)k;
#endif
        t->iidx[c] = (t->iidx[c] + W) % L;
        t->oidx[c] = (t->oidx[c] + 3u * W) % OC;
    }
    if (s_cb) s_cb(s_cbp, ADI_FIR_EVENT_ALL_CHANNEL_DONE, 0);
    return ADI_FIR_RESULT_SUCCESS;
}

ADI_FIR_RESULT adi_fir_DeleteTask(ADI_FIR_TASK_HANDLE hTask)
{
    EmuTask *t = (EmuTask *)hTask;
    if (t == 0) return ADI_FIR_RESULT_INVALID_HANDLE;
    memset(t, 0, sizeof(*t));
    return ADI_FIR_RESULT_SUCCESS;
}

ADI_FIR_RESULT adi_fir_GetFirTaskStatus(ADI_FIR_TASK_HANDLE hTask, ADI_FIR_TASK_STATE *TaskStatus)
{
    (void)hTask; if (TaskStatus) *TaskStatus = ADI_FIR_TASK_STATE_COMPLETED;
    return ADI_FIR_RESULT_SUCCESS;
}

ADI_FIR_RESULT adi_fir_FloatingPointEnable(ADI_FIR_TASK_HANDLE hTask, ADI_FIR_FLOAT_ROUNDING_MODE eRoundingMode)
{
    EmuTask *t = (EmuTask *)hTask; (void)eRoundingMode;
    if (t == 0) return ADI_FIR_RESULT_INVALID_HANDLE;
    t->fixed = 0;
    return ADI_FIR_RESULT_SUCCESS;
}

ADI_FIR_RESULT adi_fir_Close(ADI_FIR_DEV_HANDLE h)
{
    if (h != (void *)&s_open || !s_open) return ADI_FIR_RESULT_INVALID_HANDLE;
    s_open = 0;
    return ADI_FIR_RESULT_SUCCESS;
}

ADI_FIR_RESULT adi_fir_UpdateTask(ADI_FIR_TASK_HANDLE hTask, ADI_FIR_CHANNEL_BUFFER_INFO *pList, uint32_t n)
{
    (void)hTask; (void)pList; (void)n;
    return ADI_FIR_RESULT_INVALID_OPERATION;       /* not used by the bench */
}
