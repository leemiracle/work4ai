#!/usr/bin/env python3

def quicksort(arr):
    """基础快速排序实现"""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)


def quicksort_inplace(arr, low=0, high=None):
    """就地快速排序"""
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pivot_index = lomuto_partition(arr, low, high)
        quicksort_inplace(arr, low, pivot_index - 1)
        quicksort_inplace(arr, pivot_index + 1, high)


def lomuto_partition(arr, low, high):
    """Lomuto 分区策略"""
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def hoare_partition(arr, low, high):
    """Hoare 分区策略"""
    pivot = arr[(low + high) // 2]
    i, j = low - 1, high + 1
    
    while True:
        i += 1
        while arr[i] < pivot:
            i += 1
        
        j -= 1
        while arr[j] > pivot:
            j -= 1
        
        if i >= j:
            return j
        
        arr[i], arr[j] = arr[j], arr[i]


def quicksort_hoare(arr, low=0, high=None):
    """使用 Hoare 分区的快速排序"""
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        p = hoare_partition(arr, low, high)
        quicksort_hoare(arr, low, p)
        quicksort_hoare(arr, p + 1, high)


import random

def randomized_quicksort(arr, low=0, high=None):
    """随机化快速排序"""
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pivot_index = random.randint(low, high)
        arr[pivot_index], arr[high] = arr[high], arr[pivot_index]
        
        p = lomuto_partition(arr, low, high)
        randomized_quicksort(arr, low, p - 1)
        randomized_quicksort(arr, p + 1, high)


def quicksort_3way(arr, low=0, high=None):
    """三路快速排序（处理重复元素）"""
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        lt, gt = partition_3way(arr, low, high)
        quicksort_3way(arr, low, lt - 1)
        quicksort_3way(arr, gt + 1, high)


def partition_3way(arr, low, high):
    """三路分区"""
    pivot = arr[low]
    lt, i, gt = low, low, high
    
    while i <= gt:
        if arr[i] < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif arr[i] > pivot:
            arr[i], arr[gt] = arr[gt], arr[i]
            gt -= 1
        else:
            i += 1
    
    return lt, gt


def quickselect(arr, k, low=0, high=None):
    """快速选择 - 查找第 k 小元素"""
    if high is None:
        high = len(arr) - 1
    
    if low == high:
        return arr[low]
    
    pivot_index = lomuto_partition(arr, low, high)
    
    if k == pivot_index:
        return arr[k]
    elif k < pivot_index:
        return quickselect(arr, k, low, pivot_index - 1)
    else:
        return quickselect(arr, k, pivot_index + 1, high)


def benchmark_sorts():
    """性能测试"""
    import time
    import random
    
    test_cases = [
        ("随机", [random.randint(1, 1000) for _ in range(10000)]),
        ("已排序", list(range(10000))),
        ("逆序", list(range(10000, 0, -1))),
        ("重复", [42] * 5000 + [1] * 5000),
    ]
    
    algorithms = [
        ("基础快速排序", lambda x: quicksort(x.copy())),
        ("就地快速排序", lambda x: (quicksort_inplace(x), x)[1]),
        ("Hoare分区", lambda x: (quicksort_hoare(x), x)[1]),
        ("随机化快速排序", lambda x: (randomized_quicksort(x), x)[1]),
        ("三路快速排序", lambda x: (quicksort_3way(x), x)[1]),
    ]
    
    for case_name, arr in test_cases:
        print(f"\n测试用例: {case_name}")
        
        for algo_name, algo_func in algorithms:
            start = time.time()
            result = algo_func(arr)
            elapsed = time.time() - start
            
            # 验证正确性
            assert result == sorted(arr), f"{algo_name} 排序错误"
            
            print(f"  {algo_name:20s}: {elapsed:.4f}s")


if __name__ == "__main__":
    print("=== 快速排序算法演示 ===\n")
    
    # 基础测试
    test_arr = [64, 34, 25, 12, 22, 11, 90]
    print(f"原始数组: {test_arr}")
    
    sorted_arr = quicksort(test_arr.copy())
    print(f"排序结果: {sorted_arr}")
    
    # 就地排序
    test_arr_copy = test_arr.copy()
    quicksort_inplace(test_arr_copy)
    print(f"就地排序: {test_arr_copy}")
    
    # 快速选择测试
    test_arr2 = [7, 10, 4, 3, 20, 15]
    k = 3
    kth = quickselect(test_arr2.copy(), k)
    print(f"\n数组: {test_arr2}")
    print(f"第 {k+1} 小元素: {kth}")
    
    # 三路快速排序（重复元素）
    test_arr3 = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    print(f"\n含重复元素的数组: {test_arr3}")
    quicksort_3way(test_arr3)
    print(f"三路快速排序结果: {test_arr3}")
    
    # 性能测试
    print("\n" + "="*50)
    print("性能测试")
    benchmark_sorts()