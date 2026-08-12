"""
CSC 108 / CSC 148 Introduction to Computer Science (University of Toronto)
=========================================================================
覆盖主题：
- 基本数据结构可视化（栈/队列/链表/二叉搜索树）
- 递归与回溯（N-Queens、迷宫求解、排列组合）
- 面向对象设计（类继承、多态、封装）

核心教材：
- "Practical Programming" by Campbell, Gries, Montojo (3rd ed.)
- "Think Python" by Downey
- Abelson & Sussman "Structure and Interpretation of Computer Programs" (MIT, 1985)

本文件实现：
- Stack / Queue / LinkedList / BST 从零实现（纯 Python）
- N-Queens 回溯求解器（含剪枝计数）
- OOP 类层次：Shape → Circle/Rectangle/Triangle 多态面积
- 递归 vs 迭代性能对比

运行：
    python intro.py
"""
from __future__ import annotations
import time
from abc import ABC, abstractmethod


# ============ 1. 基本数据结构 ============

class Stack:
    """栈：LIFO（后进先出）"""
    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        return self._data[-1] if self._data else None

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"Stack({self._data})"


class Queue:
    """队列：FIFO（先进先出）"""
    def __init__(self):
        self._data = []

    def enqueue(self, item):
        self._data.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._data.pop(0)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)


class LinkedList:
    """单链表"""
    class _Node:
        def __init__(self, val, nxt=None):
            self.val = val
            self.next = nxt

    def __init__(self):
        self.head = None
        self._size = 0

    def prepend(self, val):
        self.head = self._Node(val, self.head)
        self._size += 1

    def append(self, val):
        if self.head is None:
            self.head = self._Node(val)
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = self._Node(val)
        self._size += 1

    def to_list(self) -> list:
        result, cur = [], self.head
        while cur:
            result.append(cur.val)
            cur = cur.next
        return result

    def reverse(self):
        prev, cur = None, self.head
        while cur:
            nxt = cur.next
            cur.next = prev
            prev, cur = cur, nxt
        self.head = prev


class BST:
    """二叉搜索树"""
    class _Node:
        def __init__(self, val):
            self.val = val
            self.left = self.right = None

    def __init__(self):
        self.root = None

    def insert(self, val):
        self.root = self._insert(self.root, val)

    def _insert(self, node, val):
        if node is None:
            return self._Node(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        return node

    def inorder(self) -> list:
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)

    def search(self, val) -> bool:
        node = self.root
        while node:
            if val == node.val:
                return True
            node = node.left if val < node.val else node.right
        return False

    def depth(self) -> int:
        def _d(n):
            if n is None:
                return 0
            return 1 + max(_d(n.left), _d(n.right))
        return _d(self.root)


# ============ 2. 递归与回溯 ============

def n_queens(n: int) -> list[list[str]]:
    """
    N-Queens 回溯求解器
    返回所有解（每个解是棋盘字符串列表）
    """
    solutions = []
    cols = set()
    diag1 = set()  # r + c
    diag2 = set()  # r - c

    def backtrack(row, placement):
        if row == n:
            board = []
            for r in range(n):
                board.append('.' * placement[r] + 'Q' + '.' * (n - placement[r] - 1))
            solutions.append(board)
            return
        for col in range(n):
            if col in cols or (row + col) in diag1 or (row - col) in diag2:
                continue
            cols.add(col)
            diag1.add(row + col)
            diag2.add(row - col)
            placement.append(col)
            backtrack(row + 1, placement)
            placement.pop()
            cols.discard(col)
            diag1.discard(row + col)
            diag2.discard(row - col)

    backtrack(0, [])
    return solutions


def fibonacci_recursive(n: int) -> int:
    """朴素递归 Fibonacci（指数级慢）"""
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def fibonacci_memo(n: int, memo=None) -> int:
    """记忆化 Fibonacci（线性快）"""
    if memo is None:
        memo = {0: 0, 1: 1}
    if n in memo:
        return memo[n]
    memo[n] = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)
    return memo[n]


def solve_maze(maze: list[list[str]]) -> list[tuple[int, int]] | None:
    """
    迷宫求解：回溯找到从 (0,0) 到右下角的路径
    '#' = 墙, '.' = 可走
    """
    rows, cols = len(maze), len(maze[0])
    visited = set()
    path = []

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return False
        if (r, c) in visited or maze[r][c] == '#':
            return False
        visited.add((r, c))
        path.append((r, c))
        if r == rows - 1 and c == cols - 1:
            return True
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            if dfs(r + dr, c + dc):
                return True
        path.pop()
        return False

    if dfs(0, 0):
        return path
    return None


# ============ 3. 面向对象设计 ============

class Shape(ABC):
    """抽象基类：多态面积"""
    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def __repr__(self):
        pass


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159265358979 * self.radius ** 2

    def __repr__(self):
        return f"Circle(r={self.radius})"


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def __repr__(self):
        return f"Rectangle({self.width}x{self.height})"


class Triangle(Shape):
    def __init__(self, base: float, height: float):
        self.base = base
        self.height = height

    def area(self) -> float:
        return 0.5 * self.base * self.height

    def __repr__(self):
        return f"Triangle(base={self.base}, h={self.height})"


# ============ 数据结构可视化 ============

def visualize_bst(values: list[int]) -> str:
    """ASCII 可视化 BST 层次结构"""
    if not values:
        return "(empty)"
    from collections import deque
    tree = BST()
    for v in values:
        tree.insert(v)
    lines = []
    queue = deque([(tree.root, 0)])
    current_level = 0
    level_nodes = []
    while queue:
        node, level = queue.popleft()
        if level > current_level:
            lines.append("  ".join(str(n) for n in level_nodes))
            level_nodes = []
            current_level = level
        if node:
            level_nodes.append(node.val)
            queue.append((node.left, level + 1))
            queue.append((node.right, level + 1))
        else:
            level_nodes.append("·")
    if level_nodes:
        lines.append("  ".join(str(n) for n in level_nodes))
    return "\n".join(lines)


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CSC 108/148: Intro to Computer Science Demo")
    print("=" * 60)

    # 1. 数据结构
    print("\n📋 1. 数据结构演示")
    s = Stack()
    for ch in "ABCDE":
        s.push(ch)
    print(f"   Stack push A-E: {s}")
    print(f"   pop: {s.pop()}, pop: {s.pop()} → {s}")

    q = Queue()
    for i in range(5):
        q.enqueue(i)
    print(f"   Queue 0-4: dequeue={q.dequeue()}, dequeue={q.dequeue()}")

    ll = LinkedList()
    for v in [3, 1, 4, 1, 5, 9]:
        ll.append(v)
    print(f"   LinkedList: {ll.to_list()}")
    ll.reverse()
    print(f"   Reversed:   {ll.to_list()}")

    bst = BST()
    for v in [50, 30, 70, 20, 40, 60, 80]:
        bst.insert(v)
    print(f"   BST inorder: {bst.inorder()}")
    print(f"   BST depth: {bst.depth()}")

    # 2. BST 可视化
    print("\n📋 2. BST 可视化")
    print(visualize_bst([50, 30, 70, 20, 40, 60, 80]))

    # 3. N-Queens
    print("\n📋 3. N-Queens 回溯")
    for n in [4, 5, 6, 7, 8]:
        sols = n_queens(n)
        print(f"   {n}-Queens: {len(sols)} solutions")
    print("\n   4-Queens 第一个解:")
    for row in n_queens(4)[0]:
        print(f"     {row}")

    # 4. 递归 vs 记忆化（反直觉发现）
    print("\n📋 4. 递归 vs 记忆化（反直觉发现）")
    # 朴素递归
    t0 = time.perf_counter()
    result_naive = fibonacci_recursive(30)
    t1 = time.perf_counter()
    naive_ms = (t1 - t0) * 1000

    # 记忆化
    t0 = time.perf_counter()
    result_memo = fibonacci_memo(100)
    t1 = time.perf_counter()
    memo_ms = (t1 - t0) * 1000

    print(f"   fib(30) 朴素递归: {result_naive} in {naive_ms:.1f}ms")
    print(f"   fib(100) 记忆化:  {result_memo} in {memo_ms:.3f}ms")
    print(f"   → 反直觉：记忆化算 fib(100) 比朴素递归算 fib(30) 快 {naive_ms/max(memo_ms, 0.001):.0f}x！")
    print(f"   → fib(30) 需要 {fib_call_count(30):,} 次递归调用，fib(100) 记忆化只需 ~200 次")

    # 5. 迷宫求解
    print("\n📋 5. 迷宫回溯求解")
    maze = [
        ['.', '.', '#', '.', '.'],
        ['#', '.', '#', '.', '#'],
        ['.', '.', '.', '.', '.'],
        ['.', '#', '#', '#', '.'],
        ['.', '.', '.', '.', '.'],
    ]
    path = solve_maze(maze)
    if path:
        print(f"   路径长度: {len(path)}")
        print(f"   路径: {path}")

    # 6. OOP 多态
    print("\n📋 6. 面向对象多态")
    shapes = [Circle(5), Rectangle(3, 4), Triangle(6, 8)]
    total = 0
    for shape in shapes:
        print(f"   {shape}: area = {shape.area():.2f}")
        total += shape.area()
    print(f"   总面积: {total:.2f}")

    print("\n✅ CSC 108/148 完成！")
    print("💡 覆盖：栈/队列/链表/BST + N-Queens回溯 + 记忆化 + OOP多态")


def fib_call_count(n: int) -> int:
    """计算朴素递归 fib(n) 的调用次数"""
    if n <= 1:
        return 1
    return 1 + fib_call_count(n - 1) + fib_call_count(n - 2)


if __name__ == "__main__":
    demo()
