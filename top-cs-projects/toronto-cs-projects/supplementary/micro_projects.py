"""
University of Toronto DCS - 杂项微项目集
=========================================
覆盖课程（10 门）：
- CSC 428 Human-Computer Interaction
- CSC 485 Computational Linguistics
- CSC 486 Quantum Computing
- CSC 421 Numerical Optimization
- CSC 418 Computer Graphics
- CSC 320 Visual Computing (加深)
- CSC 384 Intro to AI (加深)
- CSC 401 NLP (加深)
- CSC 412 Probabilistic ML (加深)
- CSC 413 Neural Nets (加深)
"""
import math
import random
from collections import defaultdict


# ============ CSC 428: Human-Computer Interaction ============

def micro_csc428_hci():
    """HCI：Fitts 定律 + Nielsen 启发式"""
    print("\n📋 CSC 428: HCI（Fitts 定律）")
    # Fitts 定律: MT = a + b * log2(2D/W)
    # D = 到目标距离, W = 目标宽度
    a, b = 0.1, 0.2  # 经验参数

    cases = [("小按钮远距离", 200, 10), ("大按钮近距离", 50, 30), ("全屏按钮", 100, 500)]
    for name, D, W in cases:
        ID = math.log2(2 * D / W)  # 难度指数
        MT = a + b * ID  # 运动时间
        print(f"   {name}: D={D:3d}px W={W:3d}px → ID={ID:.2f} bits, MT={MT:.3f}s")
    print(f"   → 小远按钮耗时是大近按钮的数倍（UI 设计启示）")

    # Nielsen 启发式
    print(f"\n   Nielsen 10 启发式（摘要）:")
    heuristics = [
        "系统状态可见性", "系统与现实世界匹配", "用户控制与自由",
        "一致性与标准", "防错", "识别而非回忆", "灵活与效率",
        "美观与极简设计", "错误诊断与恢复", "帮助与文档"
    ]
    for i, h in enumerate(heuristics, 1):
        print(f"     {i:2d}. {h}")


# ============ CSC 485: Computational Linguistics ============

def micro_csc485_cl():
    """计算语言学：形态学 + 音系学"""
    print("\n📋 CSC 485: 计算语言学（形态学分析）")
    # 有限状态转录机（FST）简化：英语复数规则
    # rules: +s (一般), +es (s/x/z/ch/sh), y→ies (辅音+y), +s (元音+y), f→ves, etc.

    def pluralize(word):
        if word.endswith(('s', 'x', 'z', 'ch', 'sh')):
            return word + 'es'
        elif word.endswith('y') and word[-2:-1] not in 'aeiou':
            return word[:-1] + 'ies'
        elif word.endswith('f'):
            return word[:-1] + 'ves'
        elif word.endswith('fe'):
            return word[:-2] + 'ves'
        else:
            return word + 's'

    tests = ['cat', 'dog', 'box', 'watch', 'city', 'boy', 'leaf', 'knife', 'bus']
    for word in tests:
        print(f"   {word:10s} → {pluralize(word)}")

    print(f"\n   → 形态学是 NLP 中被忽视但重要的层次")


# ============ CSC 486: Quantum Computing ============

def micro_csc486_quantum():
    """量子计算：Deutsch 算法 + 量子门"""
    print("\n📋 CSC 486: 量子计算（Deutsch 算法）")
    # Deutsch 算法：判断 f: {0,1}→{0,1} 是常数还是平衡
    # 经典需要 2 次查询，量子只需 1 次

    import cmath

    def hadamard(qubit):
        """Hadamard 门: |0⟩→(|0⟩+|1⟩)/√2, |1⟩→(|0⟩-|1⟩)/√2"""
        return [(qubit[0] + qubit[1]) / math.sqrt(2),
                (qubit[0] - qubit[1]) / math.sqrt(2)]

    # 常数函数 f(x) = 0
    # 平衡函数 f(x) = x

    def deutsch(f_type):
        """模拟 Deutsch 算法（简化）"""
        # |0⟩ state
        q0 = [1.0, 0.0]
        # H gate → |+⟩
        q0 = hadamard(q0)
        # 模拟 oracle（简化）
        if f_type == "constant":
            # f(x)=0: no phase change
            phase = [1.0, 1.0]
        else:
            # f(x)=x: phase kickback
            phase = [1.0, -1.0]
        q0 = [q0[i] * phase[i] for i in range(2)]
        # H gate again
        q0 = hadamard(q0)
        # Measure
        result = 0 if abs(q0[0]) > abs(q0[1]) else 1
        f_class = "constant" if result == 0 else "balanced"
        return f_class

    print(f"   f(x) = 0 (常数):  Deutsch 测得 → {deutsch('constant')}")
    print(f"   f(x) = x (平衡):  Deutsch 测得 → {deutsch('balanced')}")
    print(f"   → 量子查询 1 次 vs 经典查询 2 次（量子优势）")


# ============ CSC 421: Numerical Optimization ============

def micro_csc421_optimization():
    """数值优化：梯度下降 + 共轭梯度"""
    print("\n📋 CSC 421: 数值优化（梯度下降 vs 共轭梯度）")
    # 最小化 Rosenbrock 函数（banana function）
    # f(x,y) = (1-x)² + 100(y-x²)²

    def rosenbrock(x, y):
        return (1 - x) ** 2 + 100 * (y - x ** 2) ** 2

    def grad_rosenbrock(x, y):
        dfx = -2 * (1 - x) - 400 * x * (y - x ** 2)
        dfy = 200 * (y - x ** 2)
        return [dfx, dfy]

    # 梯度下降
    x, y = -1.0, 1.0
    lr = 0.001
    for i in range(10000):
        gx, gy = grad_rosenbrock(x, y)
        x -= lr * gx
        y -= lr * gy
    gd_val = rosenbrock(x, y)

    # Adam（自适应）
    x2, y2 = -1.0, 1.0
    m_x, m_y, v_x, v_y = 0, 0, 0, 0
    beta1, beta2, eps = 0.9, 0.999, 1e-8
    lr_adam = 0.05
    for t in range(5000):
        gx, gy = grad_rosenbrock(x2, y2)
        m_x = beta1 * m_x + (1 - beta1) * gx
        m_y = beta1 * m_y + (1 - beta1) * gy
        v_x = beta2 * v_x + (1 - beta2) * gx ** 2
        v_y = beta2 * v_y + (1 - beta2) * gy ** 2
        m_hat_x = m_x / (1 - beta1 ** (t + 1))
        m_hat_y = m_y / (1 - beta1 ** (t + 1))
        v_hat_x = v_x / (1 - beta2 ** (t + 1))
        v_hat_y = v_y / (1 - beta2 ** (t + 1))
        x2 -= lr_adam * m_hat_x / (math.sqrt(v_hat_x) + eps)
        y2 -= lr_adam * m_hat_y / (math.sqrt(v_hat_y) + eps)
    adam_val = rosenbrock(x2, y2)

    print(f"   Rosenbrock 函数最小值: f(1,1) = 0")
    print(f"   梯度下降 (10000步):  f({x:.4f},{y:.4f}) = {gd_val:.6f}")
    print(f"   Adam (5000步):       f({x2:.4f},{y2:.4f}) = {adam_val:.6f}")
    print(f"   → Adam 在病态曲率上远优于纯梯度下降")


# ============ CSC 418: Computer Graphics ============

def micro_csc418_graphics():
    """计算机图形学：光线追踪基础"""
    print("\n📋 CSC 418: 计算机图形学（光线追踪）")
    # 光线-球体求交

    def ray_sphere(origin, direction, center, radius):
        """光线-球体求交，返回 t 或 None"""
        oc = [origin[i] - center[i] for i in range(3)]
        a = sum(d * d for d in direction)
        b = 2 * sum(oc[i] * direction[i] for i in range(3))
        c = sum(o * o for o in oc) - radius ** 2
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None
        t = (-b - math.sqrt(discriminant)) / (2 * a)
        return t if t > 0 else None

    # 场景：一个球体
    sphere_center = [0, 0, -5]
    sphere_radius = 1.0

    # 渲染 10x10 ASCII 图像
    image = []
    for py in range(10):
        row = []
        for px in range(10):
            # 光线方向
            x = (px - 5) * 0.1
            y = (py - 5) * 0.1
            direction = [x, y, -1]
            norm = math.sqrt(sum(d ** 2 for d in direction))
            direction = [d / norm for d in direction]

            t = ray_sphere([0, 0, 0], direction, sphere_center, sphere_radius)
            if t is not None:
                # 法线 → 简单着色
                hit = [direction[i] * t for i in range(3)]
                normal = [(hit[i] - sphere_center[i]) / sphere_radius for i in range(3)]
                light = [0.5, 0.5, -0.5]
                ln = sum(normal[i] * light[i] for i in range(3))
                intensity = max(0.1, min(1.0, ln))
                row.append(' .:-=+*#%@'[int(intensity * 9)])
            else:
                row.append(' ')
        image.append(''.join(row))

    print("   光线追踪（球体，10x10 ASCII）：")
    for row in image:
        print(f"   {row}")
    print(f"   → 球体中心高亮，边缘暗（Lambertian 着色）")


# ============ CSC 320: Visual Computing (加深) ============

def micro_csc320_hough_circle():
    """视觉计算加深：Hough 圆检测 + 形态学"""
    print("\n📋 CSC 320 加深: Hough 圆检测")
    # 简化：已知半径的 Hough 圆检测
    # 对每个边缘点，在半径 r 的圆上投票

    radius = 3
    edge_points = [(5, 5), (5, 6), (5, 4), (6, 5), (4, 5)]  # 模拟圆边缘

    accumulator = defaultdict(int)
    for ex, ey in edge_points:
        for theta_deg in range(0, 360, 15):
            theta = math.radians(theta_deg)
            cx = round(ex - radius * math.cos(theta))
            cy = round(ey - radius * math.sin(theta))
            accumulator[(cx, cy)] += 1

    best = max(accumulator, key=accumulator.get)
    print(f"   边缘点: {edge_points}")
    print(f"   假设半径: {radius}")
    print(f"   Hough 圆心检测: {best} (votes={accumulator[best]})")
    print(f"   → 真实圆心约在 (5, 5) 附近")


# ============ CSC 384: AI 加深 (Minimax Boggle) ============

def micro_csc384_boggle():
    """AI 加深：Boggle 单词搜索 + 启发式"""
    print("\n📋 CSC 384 加深: Boggle 搜索（DFS + 剪枝）")
    # 4x4 Boggle 棋盘
    board = [
        ['D', 'O', 'G', 'S'],
        ['A', 'R', 'T', 'K'],
        ['C', 'A', 'E', 'P'],
        ['S', 'T', 'N', 'E'],
    ]

    dictionary = {'DOG', 'CAT', 'DOGS', 'ART', 'CAR', 'CARD', 'EAT', 'ATE',
                  'PASTE', 'NEAR', 'RATE', 'DOGS', 'SPEAR', 'START'}

    def find_words(board, dictionary):
        rows, cols = len(board), len(board[0])
        found = set()

        def dfs(r, c, prefix, visited):
            if prefix in dictionary and len(prefix) >= 3:
                found.add(prefix)
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                        new_prefix = prefix + board[nr][nc]
                        # 剪枝：检查是否有以 new_prefix 开头的单词
                        if any(w.startswith(new_prefix) for w in dictionary):
                            visited.add((nr, nc))
                            dfs(nr, nc, new_prefix, visited)
                            visited.discard((nr, nc))

        for r in range(rows):
            for c in range(cols):
                dfs(r, c, board[r][c], {(r, c)})

        return found

    words = find_words(board, dictionary)
    print(f"   棋盘:")
    for row in board:
        print(f"     {' '.join(row)}")
    print(f"   找到单词: {sorted(words)}")


# ============ CSC 401: NLP 加深 (Byte-Pair Encoding) ============

def micro_csc401_bpe():
    """NLP 加深：Byte-Pair Encoding（子词分词）"""
    print("\n📋 CSC 401 加深: Byte-Pair Encoding (BPE)")
    # BPE: 迭代合并最高频字符对

    corpus = "low low low low low lower lower newest newest newest newest newest newest wider wider wider new new"
    words = corpus.split()

    # 初始化：每个词拆为字符序列 + 词频
    word_freqs = defaultdict(int)
    for word in words:
        chars = tuple(word) + ('</w>',)
        word_freqs[chars] += 1

    vocab = set()
    for chars in word_freqs:
        vocab.update(chars)

    def get_pair_stats(word_freqs):
        pairs = defaultdict(int)
        for chars, freq in word_freqs.items():
            for i in range(len(chars) - 1):
                pairs[(chars[i], chars[i+1])] += freq
        return pairs

    def merge_pair(pair, word_freqs):
        new_freqs = {}
        for chars, freq in word_freqs.items():
            new_chars = list(chars)
            i = 0
            while i < len(new_chars) - 1:
                if (new_chars[i], new_chars[i+1]) == pair:
                    new_chars = new_chars[:i] + [pair[0] + pair[1]] + new_chars[i+2:]
                else:
                    i += 1
            new_freqs[tuple(new_chars)] = freq
        return new_freqs

    # 迭代 5 次合并
    for merge_step in range(8):
        pairs = get_pair_stats(word_freqs)
        if not pairs:
            break
        best = max(pairs, key=pairs.get)
        word_freqs = merge_pair(best, word_freqs)
        vocab.add(best[0] + best[1])

    print(f"   语料词数: {len(words)}")
    print(f"   初始字符词表: {len(set(''.join(words)))+1}")
    print(f"   BPE 8 轮后词表大小: {len(vocab)}")
    print(f"   示例分词（'lowest'）:")
    # 简化：展示 'low' 被合并
    print(f"     l+o+w → low (被合并为子词)")


# ============ CSC 412: ProbML 加深 (Bayesian Network) ============

def micro_csc412_bayesnet():
    """概率ML加深：贝叶斯网络精确推断"""
    print("\n📋 CSC 412 加深: 贝叶斯网络（变量消除）")
    # 经典 Sprinkler 网络
    # Cloudy → Sprinkler, Cloudy → Rain, Sprinkler → WetGrass, Rain → WetGrass

    P_C = {True: 0.5, False: 0.5}
    P_S_given_C = {True: {True: 0.1, False: 0.9}, False: {True: 0.5, False: 0.5}}
    P_R_given_C = {True: {True: 0.8, False: 0.2}, False: {True: 0.2, False: 0.8}}
    P_W_given_SR = {
        (True, True): {True: 0.99, False: 0.01},
        (True, False): {True: 0.9, False: 0.1},
        (False, True): {True: 0.9, False: 0.1},
        (False, False): {True: 0.0, False: 1.0},
    }

    # P(WetGrass=True)
    p_wet = 0.0
    for c in [True, False]:
        for s in [True, False]:
            for r in [True, False]:
                p = P_C[c] * P_S_given_C[c][s] * P_R_given_C[c][r] * P_W_given_SR[(s, r)][True]
                p_wet += p

    # P(Rain=True | WetGrass=True)
    p_rain_and_wet = 0.0
    for c in [True, False]:
        for s in [True, False]:
            for r in [True, False]:
                p = P_C[c] * P_S_given_C[c][s] * P_R_given_C[c][r] * P_W_given_SR[(s, r)][True]
                if r:
                    p_rain_and_wet += p

    p_rain_given_wet = p_rain_and_wet / p_wet
    print(f"   贝叶斯网络: Cloudy → Sprinkler/Rain → WetGrass")
    print(f"   P(WetGrass=True) = {p_wet:.4f}")
    print(f"   P(Rain=True | WetGrass=True) = {p_rain_given_wet:.4f}")
    print(f"   → 湿草大概率是下雨导致（因果推理）")


# ============ CSC 413: Deep Learning 加深 (Grad-CAM) ============

def micro_csc413_gradcam():
    """深度学习加深：Grad-CAM 可解释性"""
    print("\n📋 CSC 413 加深: Grad-CAM（卷积可解释性）")
    # Grad-CAM: 用最后一层卷积的梯度生成热力图
    # L_cam = ReLU(Σ_k α_k^c · A_k)  其中 α_k^c = GAP(∂y^c/∂A_k)

    import numpy as np
    np.random.seed(42)

    # 模拟最后一层 conv feature map (8x8, 6 channels)
    feature_map = np.random.rand(8, 8, 6)
    # 模拟梯度
    gradients = np.random.randn(8, 8, 6) * 0.1

    # 计算每个通道的权重 α_k
    alpha = np.mean(gradients, axis=(0, 1))  # (6,)

    # 加权求和 + ReLU
    cam = np.zeros((8, 8))
    for k in range(6):
        cam += alpha[k] * feature_map[:, :, k]
    cam = np.maximum(cam, 0)
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-10)

    # ASCII 可视化
    chars = ' .:-=+*#%@'
    print(f"   Feature map: 8×8×6")
    print(f"   Grad-CAM 热力图：")
    for row in cam:
        line = ''.join(chars[min(int(v * 9), 9)] for v in row)
        print(f"     {line}")
    print(f"   → 高亮区域是模型关注的图像区域（可解释性）")


# ============ 主入口 ============

def run_all_micro():
    print("=" * 60)
    print("🎓 Toronto DCS 杂项微项目集")
    print("=" * 60)

    micro_csc428_hci()
    micro_csc485_cl()
    micro_csc486_quantum()
    micro_csc421_optimization()
    micro_csc418_graphics()
    micro_csc320_hough_circle()
    micro_csc384_boggle()
    micro_csc401_bpe()
    micro_csc412_bayesnet()
    micro_csc413_gradcam()

    print("\n" + "=" * 60)
    print("✅ 全部杂项微项目完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_micro()
