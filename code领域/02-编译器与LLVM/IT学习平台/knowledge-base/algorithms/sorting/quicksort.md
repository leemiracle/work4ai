# 快速排序

## 基本信息
- **分类**: 排序算法 -> 分治法
- **时间复杂度**: O(n log n) 平均, O(n²) 最坏
- **空间复杂度**: O(log n) 递归栈
- **稳定性**: 不稳定

## 核心思想
选择基准元素（pivot），将数组分为小于和大于基准的两部分，递归排序。

## 算法步骤
1. 选择基准元素（通常为第一个、最后一个或随机）
2. 分区操作：将小于基准的放左边，大于的放右边
3. 递归排序左右子数组
4. 合并结果（就地排序，无需显式合并）

## 基础实现
```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# 就地版本
def quicksort_inplace(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pivot_index = partition(arr, low, high)
        quicksort_inplace(arr, low, pivot_index - 1)
        quicksort_inplace(arr, pivot_index + 1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
```

## 分区策略优化

### Lomuto 分区
```python
def lomuto_partition(arr, low, high):
    pivot = arr[high]
    i = low
    for j in range(low, high):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[high] = arr[high], arr[i]
    return i
```

### Hoare 分区
```python
def hoare_partition(arr, low, high):
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
```

## 优化技巧

### 三路快速排序
处理重复元素
```python
def quicksort_3way(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        lt, gt = partition_3way(arr, low, high)
        quicksort_3way(arr, low, lt - 1)
        quicksort_3way(arr, gt + 1, high)

def partition_3way(arr, low, high):
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
```

### 随机化选择基准
```python
import random

def randomized_quicksort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pivot_index = random.randint(low, high)
        arr[pivot_index], arr[high] = arr[high], arr[pivot_index]
        
        p = partition(arr, low, high)
        randomized_quicksort(arr, low, p - 1)
        randomized_quicksort(arr, p + 1, high)
```

## 性能分析
- **最好情况**: O(n log n) - 每次分割平衡
- **平均情况**: O(n log n)
- **最坏情况**: O(n²) - 数组已排序，基准选择不当
- **原地排序**: 不需要额外空间

## 应用场景
- 大规模数据排序
- 实时系统（常数因子小）
- 内排序

## 相关算法
- [[归并排序]]
- [[堆排序]]
- [[二分查找]]

## 参考资源
- CLRS Chapter 7
- 《算法导论》第7章
- 《算法图解》第4章

## 练习题
- 实现 k-th 元素查找（利用快速选择）
- 优化快速排序处理小数组（插入排序切换）
- 对比不同分区策略的性能