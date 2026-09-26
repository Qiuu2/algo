/* Critic probe: run the FROZEN repo tree_filterbank.c (compiled read-only from repo path) on host.
 * Mode 1: sine at f -> RMS of each subband output (which band does f land in?).
 * Mode 2: impulse response of each synthesis path with per-subband gains (g0,g1,g2,g3) -> dump output.
 * fs = 48000, frame = 64 (as M2). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include "tree_filterbank.h"
#include "fir_coeffs_hb63.h"

#define FS 48000.0
#define FR 64

static int32_t q31(double v){ double s=v*2147483647.0; if(s>2147483647.0)s=2147483647.0; if(s<-2147483648.0)s=-2147483648.0; return (int32_t)llround(s);}

int main(int argc, char**argv){
  tfb_set_coeffs(g_hb63_q15, FIR_HB63_NTAPS);
  if(argc>1 && strcmp(argv[1],"sine")==0){
    double freqs[]={200,500,800,1000,1250,1500,1750,2000,2250,2500,2750,3000,3250,3500,4000,5000,6000,7000,8000,10000,12000,14000};
    int nf=sizeof(freqs)/sizeof(freqs[0]);
    printf("f_Hz   rms_sb0(@6k)  rms_sb1(@12k)  rms_sb2(@24k)  rms_sb3(@48k)   [dB re input rms]\n");
    for(int fi=0;fi<nf;fi++){
      TreeChannelState ch; tfb_channel_init(&ch);
      int32_t in[FR], s0[FR/8], s1[FR/4], s2[FR/2], s3[FR];
      double e0=0,e1=0,e2=0,e3=0; long n0=0,n1=0,n2=0,n3=0; long t=0;
      int nframes=3000;
      for(int k=0;k<nframes;k++){
        for(int i=0;i<FR;i++,t++) in[i]=q31(0.25*sin(2*M_PI*freqs[fi]*t/FS));
        tfb_analyze(&ch,in,FR,s0,s1,s2,s3);
        if(k>200){
          for(int i=0;i<FR/8;i++){double v=s0[i]/2147483648.0; e0+=v*v; n0++;}
          for(int i=0;i<FR/4;i++){double v=s1[i]/2147483648.0; e1+=v*v; n1++;}
          for(int i=0;i<FR/2;i++){double v=s2[i]/2147483648.0; e2+=v*v; n2++;}
          for(int i=0;i<FR;i++){double v=s3[i]/2147483648.0; e3+=v*v; n3++;}
        }
      }
      double rin=0.25/sqrt(2.0);
      printf("%6.0f  %8.2f  %8.2f  %8.2f  %8.2f\n",freqs[fi],
        20*log10(sqrt(e0/n0)/rin+1e-12),20*log10(sqrt(e1/n1)/rin+1e-12),
        20*log10(sqrt(e2/n2)/rin+1e-12),20*log10(sqrt(e3/n3)/rin+1e-12));
    }
    return 0;
  }
  if(argc>5 && strcmp(argv[1],"imp")==0){
    /* impulse through analysis, scale subbands by g0..g3 (double), synthesize, print output samples */
    double g[4]; for(int i=0;i<4;i++) g[i]=atof(argv[2+i]);
    int nframes=64; /* 4096 samples */
    TreeChannelState ch; tfb_channel_init(&ch);
    long t=0;
    for(int k=0;k<nframes;k++){
      int32_t in[FR], s0[FR/8], s1[FR/4], s2[FR/2], s3[FR], out[FR];
      for(int i=0;i<FR;i++,t++) in[i]= (t==1000)? q31(0.25):0;   /* impulse at t=1000 (mid frame) */
      tfb_analyze(&ch,in,FR,s0,s1,s2,s3);
      for(int i=0;i<FR/8;i++) s0[i]=(int32_t)llround(s0[i]*g[0]);
      for(int i=0;i<FR/4;i++) s1[i]=(int32_t)llround(s1[i]*g[1]);
      for(int i=0;i<FR/2;i++) s2[i]=(int32_t)llround(s2[i]*g[2]);
      for(int i=0;i<FR;i++)   s3[i]=(int32_t)llround(s3[i]*g[3]);
      tfb_synthesize(&ch,s0,s1,s2,s3,FR,out);
      for(int i=0;i<FR;i++) printf("%.10e\n", out[i]/2147483648.0/0.25);
    }
    return 0;
  }
  fprintf(stderr,"usage: sine | imp g0 g1 g2 g3\n"); return 1;
}
