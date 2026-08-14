"""
ETH Zürich Informatik — 本科补充课程微项目
==========================================
覆盖 10 门本科课程：
1. Diskrete Mathematik — 图论、组合
2. Lineare Algebra — 矩阵运算
3. Numerik — 数值方法
4. Rechnerarchitektur — CPU 流水线
5. Betriebssysteme — 页面置换
6. Rechnernetze — TCP/ARQ
7. Computer Graphics (Gross) — 光栅化
8. Software Engineering — 设计模式
9. Datenbanksysteme (undergrad) — SQL 解析
10. Programmiersprachen — 类型推断
"""
import math
import random


# ============ 1. Diskrete Mathematik ============

def micro_dm_graph_coloring():
    """图着色 + 四色定理演示"""
    print("\n📋 Diskrete Mathematik: 图着色")
    # 完全图 K4 需要 4 色
    n = 4
    adj = {i: [(i+1) % n, (i+2) % n, (i+3) % n] for i in range(n)}
    # 贪心着色
    colors = [0] * n
    for v in range(n):
        used = {colors[u] for u in range(v) if u in adj.get(v, [])}
        c = 0
        while c in used:
            c += 1
        colors[v] = c
    print(f"   K4 贪心着色: {colors} (需要 {max(colors)+1} 色)")
    # 平面图测试
    n2 = 6
    adj2 = {0: [1, 2], 1: [0, 2, 3], 2: [0, 1, 3], 3: [1, 2, 4], 4: [3, 5], 5: [4]}
    colors2 = [0] * n2
    for v in range(n2):
        used = {colors2[u] for u in adj2.get(v, []) if u < v}
        c = 0
        while c in used:
            c += 1
        colors2[v] = c
    print(f"   稀疏图: {colors2} (仅需要 {max(colors2)+1} 色)")


# ============ 2. Lineare Algebra ============

def micro_la_matrix_ops():
    """矩阵运算 + 特征值"""
    print("\n📋 Lineare Algebra: 矩阵乘法 + 幂法求最大特征值")
    A = [[2, 1], [0, 3]]
    B = [[1, 0], [1, 2]]
    # 矩阵乘
    C = [[sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    print(f"   A×B = {C}")

    # 幂法求最大特征值
    v = [1.0, 1.0]
    for _ in range(20):
        new_v = [A[0][0]*v[0] + A[0][1]*v[1], A[1][0]*v[0] + A[1][1]*v[1]]
        norm = math.sqrt(sum(x**2 for x in new_v))
        v = [x / norm for x in new_v]
    eigenval = v[0] * (A[0][0]*v[0] + A[0][1]*v[1]) + v[1] * (A[1][0]*v[0] + A[1][1]*v[1])
    print(f"   A 最大特征值 ≈ {eigenval:.4f} (精确值=3.0)")


# ============ 3. Numerik ============

def micro_num_newton():
    """牛顿法求根 + 数值积分"""
    print("\n📋 Numerik: 牛顿法 + 梯形积分")
    # 牛顿法求 x²-2=0
    x = 2.0
    for i in range(10):
        fx = x**2 - 2
        fpx = 2 * x
        x = x - fx / fpx
    print(f"   √2 (牛顿法) = {x:.10f} (精确 {math.sqrt(2):.10f})")

    # 梯形法积分 sin(x) [0, π]
    n = 100
    h = math.pi / n
    integral = 0.5 * (0 + 0)  # sin(0)=sin(π)=0
    for i in range(1, n):
        integral += math.sin(i * h)
    integral *= h
    print(f"   ∫sin(x)dx [0,π] (梯形法) = {integral:.6f} (精确=2.0)")


# ============ 4. Rechnerarchitektur ============

def micro_arch_pipeline():
    """CPU 5 级流水线模拟"""
    print("\n📋 Rechnerarchitektur: 5 级流水线")
    stages = ["IF", "ID", "EX", "MEM", "WB"]
    instrs = ["ADD R1,R2,R3", "SUB R4,R5,R6", "MUL R7,R8,R9", "LD R10,[R1]"]
    cycles = len(instrs) + len(stages) - 1
    print(f"   {len(instrs)} 条指令, {len(stages)} 级流水")
    print(f"   总周期 = {cycles} (理想) vs {len(instrs)*len(stages)} (无流水)")
    print(f"   加速比 = {len(instrs)*len(stages)/cycles:.2f}x")

    # 数据冒险
    print(f"   数据冒险: ADD R1,... → SUB R2,R1,... 需要 stall 1 周期")
    print(f"   分支冒险: 跳转指令需 flush 流水线")


# ============ 5. Betriebssysteme ============

def micro_os_page_replacement():
    """页面置换算法"""
    print("\n📋 Betriebssysteme: 页面置换")
    from collections import deque
    reference = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    frames = 3

    # FIFO
    fifo = deque()
    faults_fifo = 0
    for page in reference:
        if page not in fifo:
            faults_fifo += 1
            if len(fifo) >= frames:
                fifo.popleft()
            fifo.append(page)
    print(f"   FIFO (frames={frames}): {faults_fifo} 缺页")

    # LRU
    lru = []
    faults_lru = 0
    for page in reference:
        if page in lru:
            lru.remove(page)
        else:
            faults_lru += 1
            if len(lru) >= frames:
                lru.pop(0)
        lru.append(page)
    print(f"   LRU  (frames={frames}): {faults_lru} 缺页")


# ============ 6. Rechnernetze ============

def micro_net_arq():
    """ARQ 协议（停等 / Go-Back-N）"""
    print("\n📋 Rechnernetze: ARQ 协议")
    # 停等 ARQ
    packets = list(range(8))
    loss_rate = 0.2
    random.seed(42)
    sent = 0
    acked = 0
    for p in packets:
        while True:
            sent += 1
            if random.random() > loss_rate:
                acked += 1
                break
    print(f"   停等 ARQ: {len(packets)} 包, {sent} 次发送 ({loss_rate:.0%} 丢包)")
    print(f"   效率 = {len(packets)}/{sent} = {len(packets)/sent:.2%}")


# ============ 7. Computer Graphics (Gross) ============

def micro_cg_rasterize():
    """线段光栅化 (Bresenham)"""
    print("\n📋 Computer Graphics: Bresenham 线段光栅化")
    def bresenham(x0, y0, x1, y1):
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return points

    pts = bresenham(0, 0, 7, 3)
    grid = [['.' for _ in range(8)] for _ in range(4)]
    for x, y in pts:
        grid[y][x] = '#'
    print(f"   Bresenham(0,0)→(7,3):")
    for row in reversed(grid):
        print(f"   {' '.join(row)}")


# ============ 8. Software Engineering ============

def micro_se_design_patterns():
    """设计模式演示"""
    print("\n📋 Software Engineering: 设计模式")

    # Observer 模式
    class Subject:
        def __init__(self):
            self.observers = []
        def attach(self, obs):
            self.observers.append(obs)
        def notify(self, event):
            for obs in self.observers:
                obs.update(event)

    class Observer:
        def __init__(self, name):
            self.name = name
        def update(self, event):
            pass  # 简化

    # Singleton 模式
    class Singleton:
        _instance = None
        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    s1 = Singleton()
    s2 = Singleton()
    print(f"   Singleton: s1 is s2 = {s1 is s2}")

    # Factory 模式
    def shape_factory(shape_type):
        if shape_type == "circle":
            return {"type": "circle", "radius": 5}
        elif shape_type == "square":
            return {"type": "square", "side": 4}
        return None

    print(f"   Factory('circle') = {shape_factory('circle')}")


# ============ 9. Datenbanksysteme (undergrad) ============

def micro_db_sql_parser():
    """简易 SQL 解析"""
    print("\n📋 Datenbanksysteme: SQL 解析")
    sql = "SELECT name, age FROM students WHERE age > 20 ORDER BY name"
    tokens = sql.split()
    # 简单解析
    select_idx = tokens.index("SELECT")
    from_idx = tokens.index("FROM")
    cols = tokens[select_idx+1:from_idx]
    if "WHERE" in tokens:
        where_idx = tokens.index("WHERE")
        table = tokens[from_idx+1:where_idx][0]
        condition = " ".join(tokens[where_idx+1:])
    else:
        table = tokens[from_idx+1][0]
        condition = ""
    print(f"   SQL: {sql}")
    print(f"   列: {cols}")
    print(f"   表: {table}")
    print(f"   条件: {condition}")


# ============ 10. Programmiersprachen ============

def micro_pl_type_inference():
    """Hindley-Milner 类型推断（简化）"""
    print("\n📋 Programmiersprachen: 类型推断")
    # 简化版：lambda x -> x + 1 推断 x: int
    # 模拟类型约束传播
    constraints = []
    # f = λx. x + 1
    # x + 1 需要 x: int (因为 1: int)
    constraints.append(("x", "int"))  # x 必须是 int
    constraints.append(("result", "int"))
    # f 的类型 = int -> int
    type_env = dict(constraints)
    print(f"   λx. x + 1")
    print(f"   约束: {constraints}")
    print(f"   推断: f : {type_env['x']} -> {type_env['result']}")


# ============ 主入口 ============

def run_all():
    print("=" * 60)
    print("🎓 ETH Zürich 本科补充课程微项目")
    print("=" * 60)

    micro_dm_graph_coloring()
    micro_la_matrix_ops()
    micro_num_newton()
    micro_arch_pipeline()
    micro_os_page_replacement()
    micro_net_arq()
    micro_cg_rasterize()
    micro_se_design_patterns()
    micro_db_sql_parser()
    micro_pl_type_inference()

    print("\n" + "=" * 60)
    print("✅ 全部本科补充课程完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all()
