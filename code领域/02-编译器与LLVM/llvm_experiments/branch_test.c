#include <stdio.h>
#include <time.h>
#include <stdlib.h>

#define N 10000000

// 可预测的分支
int predictable_branch(int* arr) {
    int sum = 0;
    for (int i = 0; i < N; i++) {
        sum += arr[i % 100];
    }
    return sum;
}

// 不可预测的分支
int unpredictable_branch(int* arr) {
    int sum = 0;
    for (int i = 0; i < N; i++) {
        if (arr[i % 100] > 50) {
            sum += arr[i % 100];
        }
    }
    return sum;
}

int main() {
    int arr[100];
    for (int i = 0; i < 100; i++) {
        arr[i] = rand() % 100;
    }
    
    clock_t start, end;
    double cpu_time_used;
    
    start = clock();
    int result1 = predictable_branch(arr);
    end = clock();
    cpu_time_used = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("Predictable: %.6f seconds, result: %d\n", cpu_time_used, result1);
    
    start = clock();
    int result2 = unpredictable_branch(arr);
    end = clock();
    cpu_time_used = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("Unpredictable: %.6f seconds, result: %d\n", cpu_time_used, result2);
    
    return 0;
}
