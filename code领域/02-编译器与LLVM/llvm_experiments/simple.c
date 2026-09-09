#include <stdio.h>

int add(int a, int b) { return a + b; }

int factorial(int n) {
  if (n <= 1) {
    return 1;
  }
  return n * factorial(n - 1);
}

int main() {
  int x = 5;
  int y = 3;
  int sum = add(x, y);
  int fact = factorial(x);

  printf("add(%d, %d) = %d\n", x, y, sum);
  printf("factorial(%d) = %d\n", x, fact);

  return 0;
}
