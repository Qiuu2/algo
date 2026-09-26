/* Critic: run the FROZEN repo tree_filterbank.c on a long white-noise input; for each subband k
 * produce the synthesis output with unit gain on k and zero on the others ("path outputs").
 * By linearity in the subband gains, any per-channel design y_c = sum_k w_k[c] * y^k.
 * Output: binary float64 file: [x(N), y0(N), y1(N), y2(N), y3(N), yall(N)] ; yall = all gains 1 (PR check). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include "tree_filterbank.h"
#include "fir_coeffs_hb63.h"
#define FR 64
static uint64_t s=88172645463325252ULL;
static double urand(void){ s^=s<<13; s^=s>>7; s^=s<<17; return (double)(s>>11)/9007199254740992.0; }
static void run(const int32_t *x, long N, const double g[4], double *y){
  TreeChannelState ch; tfb_channel_init(&ch);
  for(long f=0; f<N/FR; f++){
    int32_t s0[FR/8], s1[FR/4], s2[FR/2], s3[FR], out[FR];
    tfb_analyze(&ch, x+f*FR, FR, s0,s1,s2,s3);
    for(int i=0;i<FR/8;i++) s0[i]=(int32_t)llround(s0[i]*g[0]);
    for(int i=0;i<FR/4;i++) s1[i]=(int32_t)llround(s1[i]*g[1]);
    for(int i=0;i<FR/2;i++) s2[i]=(int32_t)llround(s2[i]*g[2]);
    for(int i=0;i<FR;i++)   s3[i]=(int32_t)llround(s3[i]*g[3]);
    tfb_synthesize(&ch,s0,s1,s2,s3,FR,out);
    for(int i=0;i<FR;i++) y[f*FR+i]=out[i]/2147483648.0;
  }
}
int main(int argc,char**argv){
  long N = (argc>1)? atol(argv[1]) : 262144; N -= N%FR;
  tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);
  int32_t *x=malloc(sizeof(int32_t)*N); double *xd=malloc(sizeof(double)*N), *y=malloc(sizeof(double)*N);
  for(long i=0;i<N;i++){ double v=(urand()-0.5)*0.2; x[i]=(int32_t)llround(v*2147483648.0); xd[i]=x[i]/2147483648.0; }
  FILE *fo=fopen(argv[2],"wb"); fwrite(xd,sizeof(double),N,fo);
  for(int k=0;k<5;k++){ double g[4]={0,0,0,0}; if(k<4) g[k]=1.0; else {g[0]=g[1]=g[2]=g[3]=1.0;}
    run(x,N,g,y); fwrite(y,sizeof(double),N,fo); }
  fclose(fo); fprintf(stderr,"wrote N=%ld\n",N); return 0;
}
