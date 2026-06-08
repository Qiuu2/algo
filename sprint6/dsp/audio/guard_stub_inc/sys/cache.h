/* DESKTOP-ONLY parse-stub of BSP <sys/cache.h> (only #included under M1_BUFFERS_IN_CACHED_MEM).
 * NOT the real BSP header. Resolves flush_data_buffer (same symbol as H1 A5 / sprint5 cache stub). */
#ifndef M1_MOCK_SYS_CACHE_H
#define M1_MOCK_SYS_CACHE_H
static inline void flush_data_buffer(void *start, void *end, int enInv)
{ (void)start; (void)end; (void)enInv; }
#endif
