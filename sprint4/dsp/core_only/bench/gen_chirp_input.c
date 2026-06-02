/**
 * @file    gen_chirp_input.c
 * @brief   生成冻结 chirp 输入头 chirp_input.h（host 64-bit double 算一次 → const int32）
 *
 * 根因（R14 上板 bit-exact 失败）：原 bench_harness.c 在运行期用 double+pow/sin/log 算 chirp，
 *   SHARC -double-size-32 下 double=32-bit float，与 host 64-bit double 分叉 → 输入样本不一致
 *   → 输出 CRC 挂。修法：host 用 64-bit double 预算一次，冻结成 const int32_t CHIRP_INPUT[]，
 *   host 与 target 都读同一份 → 输入 bit-identical，隔离"输入分叉"与"算法分叉"。
 *
 * 用法：gcc -O2 -o /tmp/gci gen_chirp_input.c -lm && /tmp/gci > chirp_input.h
 * chirp 公式与原 bench_harness.c gen_input 逐字一致（f0=20,f1=11000,0.289,对数扫频）。
 */
#include <stdio.h>
#include <math.h>
#include <stdint.h>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#define FS 48000
#define FRAME 64
#define NFR 1024
#define N (FRAME*NFR)   /* 65536 */

static int32_t to_q31(double v){double s=v*2147483648.0;if(s>2147483647.0)s=2147483647.0;if(s<-2147483648.0)s=-2147483648.0;return (int32_t)s;}

int main(void){
    printf("/**\n * @file chirp_input.h\n * @brief 冻结 chirp 输入（host 64-bit double 预算，勿手改；gen_chirp_input.c 生成）\n");
    printf(" * 用途：R14 上板 bit-exact——host 与 target 读同一份冻结输入，消除 -double-size-32 输入分叉。\n */\n");
    printf("#ifndef ITC_CHIRP_INPUT_H\n#define ITC_CHIRP_INPUT_H\n#include <stdint.h>\n");
    printf("#define CHIRP_INPUT_N %d   /* = FRAME 64 * 1024 帧 */\n", N);
    printf("static const int32_t CHIRP_INPUT[CHIRP_INPUT_N] = {\n");
    for(int i=0;i<N;i++){
        double t=(double)i/FS, T=(double)N/FS, f0=20.0, f1=11000.0;
        double K=pow(f1/f0, t/T);
        double ph=2.0*M_PI*f0*T/log(f1/f0)*(K-1.0);
        int32_t x=to_q31(0.289*sin(ph));
        printf("%d,", x);
        if((i&15)==15) printf("\n");
    }
    printf("\n};\n#endif /* ITC_CHIRP_INPUT_H */\n");
    return 0;
}
