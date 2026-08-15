"""
CS237A - Principles of Robot Autonomy I
覆盖课程模块：L2 运动规划 (A*, RRT) + L3 控制 (PID)

实现内容：
1. A* 路径规划（grid world）
2. RRT 简化版
3. PID 控制
4. 2D 运动学

参考：
- LaValle "Planning Algorithms"
- Pavone CS237A lecture notes
"""
from __future__ import annotations
import math
import heapq
import random
from dataclasses import dataclass, field
from typing import Optional


# ============ 1. A* Path Planning ============

@dataclass
class GridWorld:
    """2D 网格世界（0=空，1=障碍）"""
    width: int
    height: int
    obstacles: set = field(default_factory=set)  # (x, y) tuples

    def is_free(self, x: int, y: int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return (x, y) not in self.obstacles

    def neighbors(self, x: int, y: int) -> list[tuple[int, int, float]]:
        """8-connectivity，对角线 sqrt(2) 代价"""
        result = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.is_free(nx, ny):
                    cost = math.sqrt(dx*dx + dy*dy)
                    result.append((nx, ny, cost))
        return result


def astar(grid: GridWorld, start: tuple, goal: tuple,
          heuristic=None) -> Optional[list]:
    """A* 算法"""
    if heuristic is None:
        def heuristic(a, b):
            return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    open_set = [(0, start)]
    came_from: dict = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            # 重构路径
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        for nx, ny, cost in grid.neighbors(*current):
            neighbor = (nx, ny)
            tentative_g = g_score[current] + cost
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor, goal)
                f_score[neighbor] = f
                heapq.heappush(open_set, (f, neighbor))
    return None  # 没找到路径


# ============ 2. RRT (Rapidly-exploring Random Tree) ============

@dataclass
class Node:
    x: float
    y: float
    parent: Optional['Node'] = None


def rrt(start: tuple, goal: tuple, is_free_fn, bounds: tuple,
        max_iter: int = 1000, step_size: float = 0.5, goal_threshold: float = 0.5):
    """简化版 RRT"""
    start_node = Node(start[0], start[1])
    nodes = [start_node]
    x_min, x_max, y_min, y_max = bounds

    for _ in range(max_iter):
        # 随机采样（5% 概率偏向 goal）
        if random.random() < 0.05:
            rx, ry = goal
        else:
            rx = random.uniform(x_min, x_max)
            ry = random.uniform(y_min, y_max)

        # 找最近节点
        nearest = min(nodes, key=lambda n: (n.x - rx)**2 + (n.y - ry)**2)

        # 沿方向走 step_size
        dx, dy = rx - nearest.x, ry - nearest.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 1e-6:
            continue
        new_x = nearest.x + step_size * dx / dist
        new_y = nearest.y + step_size * dy / dist

        # 碰撞检测（简化）
        if not is_free_fn(new_x, new_y):
            continue

        new_node = Node(new_x, new_y, parent=nearest)
        nodes.append(new_node)

        # 检查是否到 goal
        if (new_x - goal[0])**2 + (new_y - goal[1])**2 < goal_threshold**2:
            goal_node = Node(goal[0], goal[1], parent=new_node)
            nodes.append(goal_node)
            # 重构路径
            path = []
            cur = goal_node
            while cur:
                path.append((cur.x, cur.y))
                cur = cur.parent
            return path[::-1]
    return None


# ============ 3. PID 控制 ============

class PIDController:
    """标准 PID 控制器"""

    def __init__(self, Kp: float, Ki: float, Kd: float, setpoint: float = 0):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.setpoint = setpoint
        self.integral = 0.0
        self.prev_error = 0.0

    def update(self, measurement: float, dt: float) -> float:
        """根据当前测量返回控制信号"""
        error = self.setpoint - measurement
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error
        return self.Kp * error + self.Ki * self.integral + self.Kd * derivative


def simulate_pid(Kp=1.0, Ki=0.1, Kd=0.05, setpoint=10.0,
                  steps=100, mass=1.0, friction=0.1):
    """模拟 PID 控制一个质量-摩擦系统"""
    pid = PIDController(Kp, Ki, Kd, setpoint)
    state = 0.0  # 初始位置
    velocity = 0.0
    log = []
    for t in range(steps):
        dt = 0.1
        force = pid.update(state, dt)
        # 牛顿运动方程：F - 摩擦 = m * a
        accel = (force - friction * velocity) / mass
        velocity += accel * dt
        state += velocity * dt
        log.append({"t": t * dt, "state": state, "setpoint": setpoint,
                    "force": force, "error": setpoint - state})
    return log


# ============ 4. 2D 运动学（差速驱动） ============

@dataclass
class DifferentialDrive:
    """差速驱动机器人"""
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0  # 朝向（弧度）

    def step(self, v_left: float, v_right: float, dt: float, L: float = 0.5):
        """L = 两轮间距"""
        v = (v_left + v_right) / 2
        omega = (v_right - v_left) / L
        self.x += v * math.cos(self.theta) * dt
        self.y += v * math.sin(self.theta) * dt
        self.theta += omega * dt

    def state(self) -> tuple:
        return (self.x, self.y, self.theta)


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CS237A: Robot Autonomy - Planning & Control")
    print("=" * 60)

    # 1. A* 路径规划
    print("\n📋 1. A* Path Planning")
    grid = GridWorld(width=10, height=10,
                     obstacles={(3,3), (3,4), (3,5), (4,5), (5,5), (6,5)})
    start, goal = (0, 0), (9, 9)
    path = astar(grid, start, goal)
    if path:
        print(f"   Path found ({len(path)} steps):")
        # 可视化
        for y in range(grid.height):
            row = ""
            for x in range(grid.width):
                if (x, y) in grid.obstacles:
                    row += "██"
                elif (x, y) == start:
                    row += "S "
                elif (x, y) == goal:
                    row += "G "
                elif (x, y) in path:
                    row += "· "
                else:
                    row += ". "
            print(f"     {row}")

    # 2. RRT
    print("\n📋 2. RRT")
    random.seed(42)
    def is_free(x, y):
        return 0 <= x <= 10 and 0 <= y <= 10 and not (3 <= x <= 4 and 3 <= y <= 6)
    rrt_path = rrt(start=(0, 0), goal=(9, 9), is_free_fn=is_free,
                    bounds=(0, 10, 0, 10), max_iter=2000)
    print(f"   RRT path: {len(rrt_path) if rrt_path else 0} waypoints")
    if rrt_path:
        print(f"   起点: {rrt_path[0]}, 终点: {rrt_path[-1]}")

    # 3. PID
    print("\n📋 3. PID Control")
    log = simulate_pid(Kp=1.0, Ki=0.2, Kd=0.1, steps=100, setpoint=10.0)
    final_error = abs(log[-1]["error"])
    print(f"   目标: 10.0, 最终状态: {log[-1]['state']:.3f}, 误差: {final_error:.3f}")
    print(f"   上升时间: 到达 95% 的时间步")
    for entry in log:
        if entry["state"] >= 9.5:
            print(f"     t = {entry['t']:.2f}")
            break

    # 4. 差速驱动
    print("\n📋 4. 差速驱动运动学")
    robot = DifferentialDrive(x=0, y=0, theta=0)
    print(f"   初始: {robot.state()}")
    # 走方形
    for v_l, v_r, n in [(1, 1, 50), (1, 0, 16), (1, 1, 50), (1, 0, 16),
                        (1, 1, 50), (1, 0, 16), (1, 1, 50)]:
        for _ in range(n):
            robot.step(v_l, v_r, dt=0.1)
    print(f"   走完方形后: x={robot.x:.2f}, y={robot.y:.2f}, θ={math.degrees(robot.theta):.1f}°")

    print("\n✅ CS237A 完成！")


if __name__ == "__main__":
    demo()
