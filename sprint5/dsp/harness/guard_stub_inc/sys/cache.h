/* DESKTOP-ONLY mock of the BSP <sys/cache.h> for the H1 guard-region syntax check.
 * NOT the real BSP header. Resolves flush_data_buffer (A5 symbol signature) so gcc -fsyntax-only can
 * compile the TARGET-guarded region of h1_wcet_measure.c on a host. See h1_guard_stub.h for rationale. */
#ifndef H1_MOCK_SYS_CACHE_H
#define H1_MOCK_SYS_CACHE_H
static inline void flush_data_buffer(void *start, void *end, int enInv)
{
    (void)start; (void)end; (void)enInv;
}
#endif
