"""RRT 快速扩展随机树: 连续空间采样规划 (对比A*/Hybrid A*)"""
import numpy as np, math
np.random.seed(0)

def rrt(start, goal, obstacles, max_iter=3000, step=0.8):
    """obstacles: [(cx,cy,r)] 圆形障碍"""
    nodes = [start[:2]]; parent = [-1]
    def collide(p, q):
        for (cx, cy, r) in obstacles:
            # 线段-圆碰撞检测(采样近似)
            ts = np.linspace(0, 1, 10)
            for t in ts:
                px, py = p + t*(q-p)
                if (px-cx)**2 + (py-cy)**2 < r**2: return True
        return False
    for _ in range(max_iter):
        # 10% 目标偏置加速收敛
        q_rand = np.array(goal[:2]) if np.random.rand()<0.1 else np.random.uniform(-2, 12, 2)
        d = [np.linalg.norm(n-q_rand) for n in nodes]
        near = int(np.argmin(d))
        dir = (q_rand-nodes[near]); dir = dir/np.linalg.norm(dir)*step
        q_new = nodes[near]+dir
        if collide(nodes[near], q_new): continue
        nodes.append(q_new); parent.append(near)
        if np.linalg.norm(q_new-goal[:2]) < step and not collide(q_new, goal[:2]):
            # 回溯路径
            path, i = [goal[:2]], len(nodes)-1
            while i != -1: path.append(nodes[i]); i = parent[i]
            return path[::-1]
    return None

obstacles = [(5,5,1.5), (7,3,1.0), (3,7,1.2)]   # 三个圆障碍
path = rrt(np.array([0.,0.]), np.array([10.,10.]), obstacles)
print(f"✅ RRT 规划: {'成功' if path else '失败'}, 路径节点={len(path) if path else 0}")
if path:
    L = sum(np.linalg.norm(path[i+1]-path[i]) for i in range(len(path)-1))
    print(f"   路径长度={L:.2f} (直线距离={math.hypot(10,10):.2f}, 绕障代价={L-math.hypot(10,10):.2f})")
print("💡 RRT=随机采样建树, 高维空间也能用; RRT*再加rewiring渐近最优")
