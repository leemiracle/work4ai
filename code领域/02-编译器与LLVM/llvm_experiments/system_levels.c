// 实验：理解计算机系统层次结构
// 从高层语言到底层硬件的转换

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// 实验1: 理解内存模型
void memory_experiment() {
  // 栈上分配
  int stack_var = 42;

  // 堆上分配
  int *heap_var = (int *)malloc(sizeof(int));
  *heap_var = 100;

  // 全局/静态变量
  static int static_var = 200;

  printf("Stack var address: %p\n", (void *)&stack_var);
  printf("Heap var address: %p\n", (void *)heap_var);
  printf("Static var address: %p\n", (void *)&static_var);

  free(heap_var);
}

// 实验2: 理解函数调用约定
int __attribute__((noinline))
add_numbers(int a, int b, int c, int d, int e, int f) {
  // 在x86_64上，前6个参数通过寄存器传递 (rdi, rsi, rdx, rcx, r8, r9)
  // 更多参数通过栈传递
  return a + b + c + d + e + f;
}

void calling_convention_experiment() {
  int result = add_numbers(1, 2, 3, 4, 5, 6);
  printf("Add result: %d\n", result);
}

// 实验3: 理解条件分支和预测
void branch_experiment(int n) {
  // 可预测的分支
  int sum1 = 0;
  for (int i = 0; i < n; i++) {
    sum1 += i;
  }

  // 不可预测的分支
  int sum2 = 0;
  for (int i = 0; i < n; i++) {
    if (i % 2 == 0) {
      sum2 += i;
    }
  }

  printf("Sum1: %d, Sum2: %d\n", sum1, sum2);
}

// 实验4: 理解位操作和寄存器级操作
void bitwise_experiment() {
  uint32_t x = 0xFF00AA55;

  printf("Original: 0x%08X\n", x);
  printf("Low 8 bits: 0x%02X\n", x & 0xFF);
  printf("High 8 bits: 0x%02X\n", (x >> 24) & 0xFF);
  printf("Bit 5 set: %d\n", (x >> 5) & 1);
  printf("Set bit 7: 0x%08X\n", x | (1 << 7));
  printf("Clear bit 16: 0x%08X\n", x & ~(1 << 16));
  printf("Toggle bit 24: 0x%08X\n", x ^ (1 << 24));
}

// 实验5: 理解指针和内存地址运算
void pointer_experiment() {
  int arr[4] = {10, 20, 30, 40};
  int *ptr = arr;

  printf("arr[0]: %d, address: %p\n", *ptr, (void *)ptr);
  printf("arr[1]: %d, address: %p\n", *(ptr + 1), (void *)(ptr + 1));
  printf("arr[2]: %d, address: %p\n", *(ptr + 2), (void *)(ptr + 2));

  // 指针算术
  printf("Pointer diff: %ld\n", (ptr + 3) - ptr);
}

// 实验6: 理解结构体和内存布局
struct __attribute__((packed)) packed_struct {
  char c;
  int i;
  short s;
};

struct normal_struct {
  char c;
  int i;
  short s;
};

void struct_experiment() {
  printf("Packed struct size: %zu\n", sizeof(struct packed_struct));
  printf("Normal struct size: %zu\n", sizeof(struct normal_struct));

  struct normal_struct s = {'A', 100, 200};
  printf("s.c offset: %zu\n", (size_t)&s.c - (size_t)&s);
  printf("s.i offset: %zu\n", (size_t)&s.i - (size_t)&s);
  printf("s.s offset: %zu\n", (size_t)&s.s - (size_t)&s);
}

// 实验7: 理解递归和栈帧
int __attribute__((noinline)) recursive_fibonacci(int n) {
  if (n <= 1) {
    return n;
  }
  return recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2);
}

void recursion_experiment() {
  int n = 10;
  int result = recursive_fibonacci(n);
  printf("fibonacci(%d) = %d\n", n, result);
}

// 实验8: 理解内联汇编（GCC风格）
void inline_asm_experiment() {
  int a = 5, b = 3, result;

  __asm__("addl %1, %2\n\t"
          "movl %2, %0"
          : "=r"(result)
          : "r"(a), "r"(b)
          : "memory");

  printf("Inline asm add: %d + %d = %d\n", a, b, result);
}

// 实验9: 理解volatile和编译器优化
void volatile_experiment() {
  volatile int vol = 0;
  int normal = 0;

  // 编译器不能优化掉volatile变量的访问
  for (int i = 0; i < 10; i++) {
    vol += i;
  }

  // 编译器可能优化这个循环
  for (int i = 0; i < 10; i++) {
    normal += i;
  }

  printf("Volatile: %d, Normal: %d\n", vol, normal);
}

int main() {
  printf("=== 计算机系统层次实验 ===\n\n");

  printf("--- 1. 内存模型 ---\n");
  memory_experiment();
  printf("\n");

  printf("--- 2. 调用约定 ---\n");
  calling_convention_experiment();
  printf("\n");

  printf("--- 3. 分支预测 ---\n");
  branch_experiment(100);
  printf("\n");

  printf("--- 4. 位操作 ---\n");
  bitwise_experiment();
  printf("\n");

  printf("--- 5. 指针算术 ---\n");
  pointer_experiment();
  printf("\n");

  printf("--- 6. 结构体内存布局 ---\n");
  struct_experiment();
  printf("\n");

  printf("--- 7. 递归和栈帧 ---\n");
  recursion_experiment();
  printf("\n");

  printf("--- 8. 内联汇编 ---\n");
  inline_asm_experiment();
  printf("\n");

  printf("--- 9. Volatile ---\n");
  volatile_experiment();
  printf("\n");

  return 0;
}
