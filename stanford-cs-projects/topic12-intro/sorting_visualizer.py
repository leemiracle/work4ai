"""
CS106B - Programming Abstractions
覆盖课程模块：CS106B 数据结构 + 算法（Stanford CS 本科核心）

实现内容：
1. 5 种排序算法（冒泡 / 选择 / 插入 / 归并 / 快排）
2. 复杂度对比（带步数统计）
3. 经典数据结构（链表 / 栈 / 队列 / BST）
4. 递归可视化

参考：Zelenski CS106B / "Thinking Recursively in C++"
"""
from __future__ import annotations
import random
import time
from dataclasses import dataclass, field


# ============ 1. 排序算法（带计数） ============

@dataclass
class SortStats:
    comparisons: int = 0
    swaps: int = 0
    name: str = ""

    def __str__(self):
        return f"{self.name}: {self.comparisons} comparisons, {self.swaps} swaps"


def bubble_sort(arr, stats: SortStats):
    """冒泡排序"""
    a = list(arr)
    n = len(a)
    for i in range(n):
        for j in range(0, n-i-1):
            stats.comparisons += 1
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                stats.swaps += 1
    return a


def selection_sort(arr, stats):
    """选择排序"""
    a = list(arr)
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            stats.comparisons += 1
            if a[j] < a[min_idx]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            stats.swaps += 1
    return a


def insertion_sort(arr, stats):
    """插入排序"""
    a = list(arr)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            stats.comparisons += 1
            if a[j] > key:
                a[j+1] = a[j]
                stats.swaps += 1
                j -= 1
            else:
                break
        a[j+1] = key
    return a


def merge_sort(arr, stats):
    """归并排序"""
    a = list(arr)
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid], stats)
    right = merge_sort(a[mid:], stats)
    # Merge
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        stats.comparisons += 1
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
            stats.swaps += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(arr, stats, low=0, high=None):
    """快速排序"""
    a = list(arr) if high is None else arr
    if high is None:
        high = len(a) - 1
    if low < high:
        pi = _partition(a, low, high, stats)
        quick_sort(a, stats, low, pi-1)
        quick_sort(a, stats, pi+1, high)
    return a


def _partition(arr, low, high, stats):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        stats.comparisons += 1
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            stats.swaps += 1
    arr[i+1], arr[high] = arr[high], arr[i+1]
    stats.swaps += 1
    return i + 1


def compare_sorts(n: int = 100):
    """比较所有排序算法"""
    random.seed(42)
    arr = [random.randint(0, 1000) for _ in range(n)]
    print(f"\n📋 排序算法对比 (n={n}):")

    sorts = [
        ("Bubble", bubble_sort),
        ("Selection", selection_sort),
        ("Insertion", insertion_sort),
        ("Merge", merge_sort),
        ("Quick", quick_sort),
    ]

    results = []
    for name, fn in sorts:
        stats = SortStats(name=name)
        start = time.time()
        sorted_arr = fn(arr, stats)
        elapsed = time.time() - start
        results.append((name, stats, elapsed))
        correct = sorted_arr == sorted(arr)
        print(f"   {name:10}: {stats.comparisons:8d} cmp, {stats.swaps:8d} swp, "
              f"{elapsed*1000:6.2f}ms {'✓' if correct else '✗'}")
    return results


# ============ 2. 数据结构 ============

class LinkedList:
    """单向链表"""

    class Node:
        def __init__(self, val, next_=None):
            self.val = val
            self.next = next_

    def __init__(self):
        self.head = None
        self.size = 0

    def push_front(self, val):
        self.head = self.Node(val, self.head)
        self.size += 1

    def pop_front(self):
        if not self.head:
            return None
        val = self.head.val
        self.head = self.head.next
        self.size -= 1
        return val

    def to_list(self) -> list:
        result = []
        cur = self.head
        while cur:
            result.append(cur.val)
            cur = cur.next
        return result


class Stack:
    """栈（用 list）"""

    def __init__(self):
        self._items = []

    def push(self, x): self._items.append(x)

    def pop(self): return self._items.pop() if self._items else None

    def peek(self): return self._items[-1] if self._items else None

    def is_empty(self): return len(self._items) == 0

    def __len__(self): return len(self._items)


class Queue:
    """队列（用 list 模拟，O(n) pop；用 deque 可优化到 O(1)）"""

    def __init__(self):
        self._items = []

    def enqueue(self, x): self._items.append(x)

    def dequeue(self):
        return self._items.pop(0) if self._items else None

    def is_empty(self): return len(self._items) == 0


@dataclass
class BSTNode:
    val: int
    left: 'BSTNode' = None
    right: 'BSTNode' = None


class BST:
    """二叉搜索树"""

    def __init__(self):
        self.root: BSTNode = None

    def insert(self, val: int):
        self.root = self._insert(self.root, val)

    def _insert(self, node, val):
        if node is None:
            return BSTNode(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        return node

    def search(self, val: int) -> bool:
        return self._search(self.root, val)

    def _search(self, node, val):
        if node is None:
            return False
        if val == node.val:
            return True
        elif val < node.val:
            return self._search(node.left, val)
        else:
            return self._search(node.right, val)

    def inorder(self) -> list:
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)


# ============ 3. 递归可视化 ============

def fibonacci_tree(n: int, depth: int = 0) -> str:
    """斐波那契递归树（可视化）"""
    indent = "  " * depth
    if n <= 1:
        return f"{indent}fib({n}) → {n}\n"
    s = f"{indent}fib({n})\n"
    s += fibonacci_tree(n-1, depth+1)
    s += fibonacci_tree(n-2, depth+1)
    return s


def hanoi(n: int, src='A', aux='B', dst='C', moves=None):
    """汉诺塔"""
    if moves is None:
        moves = []
    if n == 1:
        moves.append(f"Move disk 1: {src} → {dst}")
        return moves
    hanoi(n-1, src, dst, aux, moves)
    moves.append(f"Move disk {n}: {src} → {dst}")
    hanoi(n-1, aux, src, dst, moves)
    return moves


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CS106B: Programming Abstractions")
    print("=" * 60)

    # 1. 排序对比
    compare_sorts(n=100)
    print("\n   结论：")
    print("   - 冒泡 / 选择：O(n²)")
    print("   - 插入：O(n²) 但常数小，对近乎有序数据快")
    print("   - 归并 / 快排：O(n log n)")

    # 2. 数据结构
    print("\n📋 数据结构:")
    ll = LinkedList()
    for x in [3, 1, 4, 1, 5, 9]:
        ll.push_front(x)
    print(f"   链表: {ll.to_list()}")

    s = Stack()
    for c in "Hello":
        s.push(c)
    reversed_str = "".join(s.pop() for _ in range(len(s)))
    print(f"   栈反转 'Hello' → '{reversed_str}'")

    bst = BST()
    for x in [5, 3, 7, 1, 4, 6, 8]:
        bst.insert(x)
    print(f"   BST 中序遍历: {bst.inorder()} (应有序)")
    print(f"   查找 4: {bst.search(4)}, 查找 99: {bst.search(99)}")

    # 3. 递归
    print("\n📋 递归可视化:")
    print("   fib(5) 调用树:")
    print(fibonacci_tree(5))

    print("\n📋 汉诺塔 (n=3):")
    for m in hanoi(3):
        print(f"   {m}")

    print("\n✅ CS106B 完成！")
    print("\n💡 核心思想:")
    print("   1. 时间复杂度（O(n) 与 O(n²) 差距巨大）")
    print("   2. 选择合适数据结构（栈 vs 队列 vs BST）")
    print("   3. 递归思维（基线 + 递归步骤）")


if __name__ == "__main__":
    demo()
