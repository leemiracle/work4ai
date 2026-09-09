/*
 * Lab01/src/calling_conv.c — ARM64 (AAPCS64) 调用约定探测
 *
 * 运行时验证 + objdump 反汇编对照：
 *   1. 前 8 整数参数走 X0-X7，第 9 个走栈
 *   2. 前 8 浮点参数走 V0-V7
 *   3. callee-saved X19-X28（被调用方保存）
 *   4. 帧指针 X29 / 返回地址 X30 的保存恢复
 *
 * 运行：./calling_conv
 * 反汇编对照：objdump -d calling_conv | sed -n '/<test_9args>:/,/ret/p'
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>

/* 9 个 int 参数：前 8 走 X0-X7，第 9 个应走栈 */
__attribute__((noinline))
int test_9args(int a1,int a2,int a3,int a4,int a5,int a6,int a7,int a8,int a9) {
    return a1 + a9;   /* 用首尾，强制两边都读 */
}

/* 8 个 int 参数：全走寄存器 */
__attribute__((noinline))
int test_8args(int a1,int a2,int a3,int a4,int a5,int a6,int a7,int a8) {
    return a1 + a8;
}

/* 4 个 double 参数：走 V0-V3 */
__attribute__((noinline,optimize("no-fast-math")))
double test_4doubles(double a,double b,double c,double d) {
    return a + b + c + d;
}

/* 混合 int + float 参数（AAPCS64 分配规则）*/
__attribute__((noinline,optimize("no-fast-math")))
double test_mixed(int i1, double d1, int i2, double d2) {
    return (double)(i1 + i2) + d1 + d2;
}

/* 触发帧指针保存的函数（用足够多局部变量）*/
__attribute__((noinline))
uint64_t frame_probe(uint64_t n) {
    uint64_t a = n, b = n+1, c = n+2, d = n+3;
    volatile uint64_t arr[4] = {a, b, c, d};  /* 强制栈使用 */
    return arr[0] + arr[1] + arr[2] + arr[3];
}

int main(void) {
    printf("== Lab01.2: 调用约定 (AAPCS64) ==\n\n");

    int r9 = test_9args(1,2,3,4,5,6,7,8,9);
    printf("  test_9args(1..9) = %d %s\n", r9, r9 == 10 ? "✓" : "✗");
    printf("    → 前 8 参数走 X0-X7, 第 9 参数走栈 ([sp])\n\n");

    int r8 = test_8args(1,2,3,4,5,6,7,8);
    printf("  test_8args(1..8) = %d %s\n", r8, r8 == 9 ? "✓" : "✗");
    printf("    → 8 参数全走 X0-X7, 无栈访问\n\n");

    double rd = test_4doubles(1.0, 2.0, 3.0, 4.0);
    printf("  test_4doubles(1,2,3,4) = %.1f %s\n", rd, rd == 10.0 ? "✓" : "✗");
    printf("    → 浮点参数走 V0-V3\n\n");

    double rm = test_mixed(10, 1.5, 20, 2.5);
    printf("  test_mixed(10,1.5,20,2.5) = %.1f %s\n", rm, rm == 34.0 ? "✓" : "✗");
    printf("    → int 走 X0/X1, double 走 V0/V1 (独立编号空间)\n\n");

    uint64_t rf = frame_probe(100);
    printf("  frame_probe(100) = %llu %s\n", (unsigned long long)rf,
           rf == 406 ? "✓" : "✗");
    printf("    → 用了栈（局部数组），应有 stp x29,x30 保存帧\n\n");

    printf("  == objdump 反汇编对照 ==\n");
    printf("  看第 9 参数走栈:\n");
    printf("    objdump -d calling_conv | sed -n '/<test_9args>:/,/ret/p'\n");
    printf("    预期: ldr wN, [sp, #X] (从栈读第 9 参数)\n\n");
    printf("  看 callee-saved / 帧指针保存:\n");
    printf("    objdump -d calling_conv | sed -n '/<frame_probe>:/,/ret/p'\n");
    printf("    预期入口: stp x29, x30, [sp, #-16]! (保存 FP+LR)\n");
    printf("    预期返回: ldp x29, x30, [sp], #16 (恢复)\n\n");
    printf("  AAPCS64 关键规则:\n");
    printf("    X0-X7  : 参数/返回值 (caller-saved)\n");
    printf("    X8     : 间接结果位置 (结构体返回) / 临时\n");
    printf("    X9-X15 : 临时 (caller-saved, 调用前自行保存)\n");
    printf("    X16-X18: IP0/IP1 (过程调用 stub) / 平台保留\n");
    printf("    X19-X28: callee-saved (被调用方必须保存恢复)\n");
    printf("    X29    : FP (帧指针, callee-saved)\n");
    printf("    X30    : LR (返回地址)\n");
    printf("    V0-V7  : 浮点参数/返回值\n");
    printf("    V8-V15 : callee-saved (低 64 位)\n");
    printf("    V16-V31: caller-saved\n");
    return 0;
}
