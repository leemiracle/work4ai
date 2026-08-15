import numpy as np, heapq, math

# ===== Hybrid A* 路径搜索（连续空间）最小概念 =====
# 经典 A* 在网格离散；Hybrid A* 在 [x,y,theta] 连续状态空间搜索，保证路径可执行（满足转弯半径）
def hybrid_astar(start, goal, obstacles=set(), step=1.0, n_steer=5, max_steer=math.pi/4):
    # 离散运动原语：前进 + 不同转向角
    steers = np.linspace(-max_steer, max_steer, n_steer)
    L = 2.5  # 轴距
    def heuristic(x,y,t):
        return math.hypot(x-goal[0], y-goal[1])  # 启发式：到目标的距离
    open_h = [(heuristic(*start), 0, start, [])]
    visited = set()
    for _ in range(20000):
        if not open_h: return None
        f, g, (x,y,t), path = heapq.heappop(open_h)
        if math.hypot(x-goal[0], y-goal[1]) < step:
            return path + [(x,y,t)]
        key = (round(x,1), round(y,1), round(t,1))
        if key in visited: continue
        visited.add(key)
        for s in steers:
            nx = x + step*math.cos(t)
            ny = y + step*math.sin(t)
            nt = t + step/L*math.tan(s)
            if (round(nx,1),round(ny,1)) in obstacles: continue
            heapq.heappush(open_h, (g+step+heuristic(nx,ny,nt), g+step, (nx,ny,nt), path+[(x,y,t)]))
    return None

path = hybrid_astar((0,0,0), (10,6,math.pi/2))
print(f"Hybrid A* 搜索: {'成功' if path else '失败'}, 路径节点数 = {len(path) if path else 0}")
# 对比：经典 A* 只能走 8 方向，Hybrid A* 能走任意曲率，转弯平滑——这就是它用于泊车/掉头的原因
print("结论: Hybrid A* 保证了输出的路径满足车辆运动学约束(最小转弯半径)，可直接由控制层执行")
