/* DESKTOP-ONLY parse-stub of BSP <services/pdma/adi_pdma_2156x.h> for the M1 guard-region syntax check.
 * NOT the real BSP header. Mirrors the [L1] ADI_PDMA_DESC_LIST struct + ENUM used in ALT.c:114-284. */
#ifndef M1_MOCK_SERVICES_PDMA_ADI_PDMA_2156X_H
#define M1_MOCK_SERVICES_PDMA_ADI_PDMA_2156X_H
#include <stdint.h>

typedef struct ADI_PDMA_DESC_LIST_s {
    void   *pStartAddr;
    uint32_t Config;
    uint32_t XCount;
    int32_t  XModify;
    uint32_t YCount;
    int32_t  YModify;
    struct ADI_PDMA_DESC_LIST_s *pNxtDscp;
} ADI_PDMA_DESC_LIST;

#define ENUM_DMA_CFG_XCNT_INT 0u

#endif
