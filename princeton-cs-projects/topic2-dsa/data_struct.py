"""
COS 226 Data Structures and Algorithms（Princeton）
====================================================
覆盖主题（Sedgewick & Wayne, Algorithms 4th ed）：
- 红黑树（左倾 LLRB，Sedgewick 简化版）
- KMP 子串搜索（Knuth-Morris-Pratt）
- FFT 基础（Cooley-Tukey 蝶形运算）
- TST（Ternary Search Trie）
- Separate-chaining hash table

核心教材/论文：
- Sedgewick & Wayne "Algorithms" 4th ed, Ch 3 (Searching) + Ch 5 (Strings)
- Sedgewick 2008 "Left-Leaning Red-Black Trees" (LLRB 简化)
- Knuth, Morris, Pratt 1977 "Fast Pattern Matching in Strings" SIAM J Comput
- Cooley & Tukey 1965 "An Algorithm for the Machine Calculation of Complex Fourier Series" Math Comp

本文件实现：
1. LLRB 红黑树（insert + in-order traversal + height check）
2. KMP 字符串匹配（failure function + search）
3. 递归 FFT（Cooley-Tukey DIT）
4. TST 三叉搜索 trie
5. Separate-chaining hash table

运行：
    python data_struct.py
"""
from __future__ import annotations
import math
import cmath


# ================================================================
# 1. Left-Leaning Red-Black Tree (LLRB)
# ================================================================
# Sedgewick's simplification: red links lean left only.
# Equivalent to 2-3 tree. Guarantees height ≤ 2*log2(N).

RED = True
BLACK = False


class RBNode:
    __slots__ = ['key', 'val', 'left', 'right', 'color']

    def __init__(self, key, val, color=RED):
        self.key = key
        self.val = val
        self.left = None
        self.right = None
        self.color = color


class LLRBTree:
    """Left-Leaning Red-Black Tree (Sedgewick 2008)"""

    def __init__(self):
        self.root = None
        self._size = 0

    def put(self, key, val):
        self.root = self._put(self.root, key, val)
        self.root.color = BLACK
        self._size += 1

    def _put(self, h, key, val):
        if h is None:
            return RBNode(key, val, RED)
        if key < h.key:
            h.left = self._put(h.left, key, val)
        elif key > h.key:
            h.right = self._put(h.right, key, val)
        else:
            h.val = val
            self._size -= 1  # overwrite, don't count
        # Fix-up: rotate left if right is red and left is black
        if self._is_red(h.right) and not self._is_red(h.left):
            h = self._rotate_left(h)
        # Rotate right if two consecutive left reds
        if self._is_red(h.left) and self._is_red(h.left.left if h.left else None):
            h = self._rotate_right(h)
        # Split 4-node: two red children
        if self._is_red(h.left) and self._is_red(h.right):
            self._flip_colors(h)
        return h

    @staticmethod
    def _is_red(node):
        return node is not None and node.color == RED

    @staticmethod
    def _rotate_left(h):
        x = h.right
        h.right = x.left
        x.left = h
        x.color = h.color
        h.color = RED
        return x

    @staticmethod
    def _rotate_right(h):
        x = h.left
        h.left = x.right
        x.right = h
        x.color = h.color
        h.color = RED
        return x

    @staticmethod
    def _flip_colors(h):
        h.color = not h.color
        h.left.color = not h.left.color
        h.right.color = not h.right.color

    def in_order(self) -> list:
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)

    def height(self) -> int:
        return self._height(self.root)

    def _height(self, node) -> int:
        if node is None:
            return 0
        return 1 + max(self._height(node.left), self._height(node.right))

    @property
    def size(self):
        return self._size


# ================================================================
# 2. KMP Substring Search
# ================================================================

def kmp_failure_table(pattern: str) -> list[int]:
    """Build KMP failure (partial match) table. O(m) time."""
    m = len(pattern)
    fail = [0] * m
    j = 0  # length of previous longest prefix suffix
    i = 1
    while i < m:
        if pattern[i] == pattern[j]:
            j += 1
            fail[i] = j
            i += 1
        elif j > 0:
            j = fail[j - 1]
        else:
            fail[i] = 0
            i += 1
    return fail


def kmp_search(text: str, pattern: str) -> list[int]:
    """KMP search: return all start indices where pattern appears in text."""
    if not pattern:
        return []
    fail = kmp_failure_table(pattern)
    matches = []
    i = j = 0  # i into text, j into pattern
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == len(pattern):
                matches.append(i - j)
                j = fail[j - 1]
        elif j > 0:
            j = fail[j - 1]
        else:
            i += 1
    return matches


# ================================================================
# 3. Recursive FFT (Cooley-Tukey)
# ================================================================

def fft(a: list[complex]) -> list[complex]:
    """Recursive Cooley-Tukey FFT. Input length must be power of 2.
    Computes X[k] = Σ x[n] * W_N^(nk), W_N = e^(-2πi/N)
    """
    n = len(a)
    if n <= 1:
        return list(a)
    # Check power of 2
    if n & (n - 1) != 0:
        # Pad to next power of 2
        next_pow2 = 1 << (n - 1).bit_length()
        a = list(a) + [0j] * (next_pow2 - n)
        n = next_pow2
    even = fft(a[0::2])
    odd = fft(a[1::2])
    result = [0j] * n
    for k in range(n // 2):
        w = cmath.exp(-2j * math.pi * k / n)
        result[k] = even[k] + w * odd[k]
        result[k + n // 2] = even[k] - w * odd[k]
    return result


def ifft(a: list[complex]) -> list[complex]:
    """Inverse FFT"""
    n = len(a)
    conj = [x.conjugate() for x in a]
    y = fft(conj)
    return [x.conjugate() / n for x in y]


def dft(a: list[complex]) -> list[complex]:
    """Naive O(n²) DFT — direct evaluation of the DFT formula.

    Used only for benchmarking against FFT to demonstrate the
    O(n²) vs O(n log n) speedup empirically.
    """
    n = len(a)
    return [sum(a[k] * cmath.exp(-2j * math.pi * k * j / n)
                for k in range(n)) for j in range(n)]


# ================================================================
# 4. Ternary Search Trie (TST)
# ================================================================

class TSTNode:
    __slots__ = ['c', 'left', 'mid', 'right', 'val']

    def __init__(self, c):
        self.c = c
        self.left = None
        self.mid = None
        self.right = None
        self.val = None  # None = not a terminal key


class TST:
    """Ternary Search Trie — combines trie structure with BST.

    Space-efficient trie: each node has 3 children (less, equal, greater).
    Sedgewick & Wayne Algorithms 4th ed, Ch 5.2
    """

    def __init__(self):
        self.root = None

    def put(self, key: str, val):
        self.root = self._put(self.root, key, val, 0)

    def _put(self, node, key, val, d):
        c = key[d]
        if node is None:
            node = TSTNode(c)
        if c < node.c:
            node.left = self._put(node.left, key, val, d)
        elif c > node.c:
            node.right = self._put(node.right, key, val, d)
        elif d < len(key) - 1:
            node.mid = self._put(node.mid, key, val, d + 1)
        else:
            node.val = val
        return node

    def get(self, key: str):
        node = self._get(self.root, key, 0)
        return node.val if node else None

    def _get(self, node, key, d):
        if node is None:
            return None
        c = key[d]
        if c < node.c:
            return self._get(node.left, key, d)
        elif c > node.c:
            return self._get(node.right, key, d)
        elif d < len(key) - 1:
            return self._get(node.mid, key, d + 1)
        return node


# ================================================================
# 5. Separate-Chaining Hash Table
# ================================================================

class HashTable:
    """Separate-chaining hash table with linked lists."""

    def __init__(self, capacity: int = 16):
        self.m = capacity
        self.buckets: list[list] = [[] for _ in range(self.m)]
        self.n = 0

    def _hash(self, key) -> int:
        # Parentheses are CRITICAL: % binds tighter than & in Python.
        # Without them: hash(key) & (0x7FFFFFFF % self.m) — when m is not a
        # power of 2, 0x7FFFFFFF % m can be as small as 1 (e.g. m=7 → 1),
        # collapsing all keys into 2 buckets.  With parentheses the high
        # bit is masked first, then reduced mod m — the standard Java/Sedgewick
        # idiom.
        return (hash(key) & 0x7FFFFFFF) % self.m

    def put(self, key, val):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.buckets[idx]):
            if k == key:
                self.buckets[idx][i] = (key, val)
                return
        self.buckets[idx].append((key, val))
        self.n += 1
        # Resize if load factor > 0.75
        if self.n > 0.75 * self.m:
            self._resize(self.m * 2)

    def get(self, key):
        idx = self._hash(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        return None

    def _resize(self, new_m):
        old = self.buckets
        self.m = new_m
        self.buckets = [[] for _ in range(self.m)]
        self.n = 0
        for chain in old:
            for k, v in chain:
                self.put(k, v)

    def load_factor(self) -> float:
        return self.n / self.m

    def max_chain(self) -> int:
        return max(len(b) for b in self.buckets) if self.buckets else 0


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("COS 226: Data Structures & Algorithms Demo")
    print("=" * 60)

    # --- 1. LLRB Tree ---
    print("\n📋 1. Left-Leaning Red-Black Tree (LLRB)")
    tree = LLRBTree()
    import random
    random.seed(42)
    keys = random.sample(range(1, 1000), 100)
    for k in keys:
        tree.put(k, f"val_{k}")
    sorted_keys = tree.in_order()
    print(f"   插入 {tree.size} 个随机 key")
    print(f"   in-order 是否已排序: {sorted_keys == sorted(keys)}")
    print(f"   树高度: {tree.height()}")
    print(f"   理论最小高度 (log2 N): {int(math.log2(tree.size))}")
    print(f"   LLRB 保证: height ≤ 2*log2(N) = {2 * int(math.log2(tree.size))}")

    # --- 2. KMP ---
    print("\n📋 2. KMP Substring Search")
    text = "ABABDABACDABABCABAB" * 3
    pattern = "ABABCABAB"
    fail = kmp_failure_table(pattern)
    print(f"   Pattern: {pattern}")
    print(f"   Failure table: {fail}")
    matches = kmp_search(text, pattern)
    print(f"   在 {len(text)} 字符文本中找到 {len(matches)} 处匹配: {matches}")

    # Compare with naive
    naive = []
    for i in range(len(text) - len(pattern) + 1):
        if text[i:i + len(pattern)] == pattern:
            naive.append(i)
    print(f"   暴力法验证: {naive}")
    print(f"   匹配结果一致: {matches == naive}")

    # --- 3. FFT ---
    print("\n📋 3. FFT (Cooley-Tukey)")
    # Signal: 2 sine waves
    n = 64
    sr = 64.0
    signal = [math.sin(2 * math.pi * 5 * i / sr) +
              0.5 * math.sin(2 * math.pi * 12 * i / sr)
              for i in range(n)]
    spectrum = fft(signal)
    magnitudes = [abs(x) for x in spectrum[:n // 2]]
    # Find top 2 peaks
    peaks = sorted(range(len(magnitudes)), key=lambda i: -magnitudes[i])[:4]
    print(f"   信号: 5Hz + 12Hz 正弦波，采样 {n} 点")
    print(f"   FFT 频谱峰值的 bin: {sorted(peaks[:4])}")
    print(f"   对应频率: {[i * sr / n for i in sorted(peaks[:4])]} Hz")

    # --- 4. TST ---
    print("\n📋 4. Ternary Search Trie (TST)")
    trie = TST()
    words = ["cat", "car", "card", "care", "careful", "dog", "do"]
    for w in words:
        trie.put(w, len(w))
    for w in ["cat", "careful", "dog", "missing"]:
        val = trie.get(w)
        print(f"   get('{w}') = {val}")

    # --- 5. Hash Table ---
    print("\n📋 5. Separate-Chaining Hash Table")
    ht = HashTable(capacity=8)
    for i in range(50):
        ht.put(f"key_{i}", i * 10)
    print(f"   插入 50 个 key，capacity 扩展到 {ht.m}")
    print(f"   负载因子: {ht.load_factor():.3f}")
    print(f"   最大链长: {ht.max_chain()}")
    print(f"   get('key_25') = {ht.get('key_25')}")
    print(f"   get('key_999') = {ht.get('key_999')}")

    # 反直觉发现
    print("\n💡 反直觉发现：")

    # (a) DFT O(n²) vs FFT O(n log n) — real timing, not just a claim
    import time
    print("   (a) FFT vs DFT 实测计时（同样的输入，同样的输出）：")
    for n_fft in [512, 1024]:
        sig = [math.sin(2 * math.pi * 7 * i / n_fft) for i in range(n_fft)]
        t0 = time.perf_counter()
        _ = dft(sig)
        t_dft = time.perf_counter() - t0
        t0 = time.perf_counter()
        _ = fft(sig)
        t_fft = time.perf_counter() - t0
        ratio = t_dft / max(t_fft, 1e-12)
        print(f"       n={n_fft:>5}: DFT={t_dft:.3f}s  FFT={t_fft:.5f}s  → 加速 {ratio:.0f}×")
    print(f"       理论比值 n/log₂(n): 1024→{1024/10:.0f}×  (实测因递归开销低于理论上界)")

    # (b) Hash table: max chain far smaller than n (balls-into-bins)
    print("\n   (b) Hash table 链长分布（修正 & 运算符优先级后）：")
    ht_big = HashTable(capacity=1031)  # prime — triggers old bug!
    for i in range(10000):
        ht_big.put(f"key_{i}", i)
    chains = sorted(len(b) for b in ht_big.buckets)
    avg = ht_big.n / ht_big.m
    print(f"       {ht_big.n} keys / {ht_big.m} buckets (load factor α={avg:.1f})")
    print(f"       max_chain={ht_big.max_chain()}, avg_chain={avg:.1f}, "
          f"min_chain={chains[0]}")
    print(f"       → 最大链长仅 {ht_big.max_chain()}（远小于 n={ht_big.n}），")
    print(f"         符合 balls-into-bins 理论: max ≈ α + O(√(α·ln m))")

    print("\n✅ COS 226 Demo 完成！")


if __name__ == "__main__":
    demo()
