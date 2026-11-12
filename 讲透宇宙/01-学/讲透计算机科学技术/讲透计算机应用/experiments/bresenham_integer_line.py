# -*- coding: utf-8 -*-
"""
bresenham_integer_line.py —— 00/03 章实验：整数运算画直线（图形学最原子算法）

对应章：00-体系结构（假设表"像素离散网格"）/ 03-可构造与结构（不变量篇）
核心：不用浮点、不用乘除——纯整数加法与比较，把"连续直线"构造为离散像素集。
断言的不是某条线的具体坐标，而是构造的**结构性质**（00 章管线思想的原子案例）：
  1. 连续性：相邻像素八连通（每步 |dx|<=1 且 |dy|<=1）
  2. 命中界：像素到直线的整数偏差有界（|F(x,y)| <= max(|dx|,|dy|)）
  3. 端点封闭：起点终点都在集合内
  4. 像素数：恰好 max(dx,dy)+1 个（无冗余像素）
"""
import math


def bresenham(x0, y0, x1, y1):
    """经典整数 Bresenham。返回像素列表 [(x, y), ...]，从 (x0,y0) 到 (x1,y1)。"""
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    pts = []
    x, y = x0, y0
    while True:
        pts.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return pts


def structural_asserts(x0, y0, x1, y1):
    """对一个线段跑全部结构断言。"""
    pts = bresenham(x0, y0, x1, y1)
    dx, dy = abs(x1 - x0), abs(y1 - y0)

    # 断言 3：端点封闭
    assert pts[0] == (x0, y0) and pts[-1] == (x1, y1), "端点缺失"

    # 断言 1：八连通连续性
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        assert abs(bx - ax) <= 1 and abs(by - ay) <= 1, "出现断裂像素"

    # 断言 2：整数偏差有界  F(x,y) = (y-y0)*(x1-x0) - (x-x0)*(y1-y0)（带符号隐式式，
    # 对任意方向斜率成立；像素到直线的垂直距离 = |F|/len）
    for (x, y) in pts:
        F = (y - y0) * (x1 - x0) - (x - x0) * (y1 - y0)
        assert abs(F) <= max(dx, dy), f"像素 {x},{y} 偏离直线：F={F}"

    # 断言 4：像素数恰为 max(dx,dy)+1
    assert len(pts) == max(dx, dy) + 1, f"像素数 {len(pts)} != {max(dx,dy)+1}"

    # 反直觉彩蛋：0 乘除、0 浮点——只用了加、减、移位级比较
    return pts


if __name__ == "__main__":
    cases = [(0, 0, 20, 7), (0, 0, 7, 20), (5, 9, -14, -3), (0, 0, 15, 15),
             (10, 0, 0, 10), (0, 0, 30, 1)]
    for (x0, y0, x1, y1) in cases:
        pts = structural_asserts(x0, y0, x1, y1)
        F_max = max(abs((y - y0) * (x1 - x0) - (x - x0) * (y1 - y0)) for (x, y) in pts)
        print(f"({x0},{y0})→({x1},{y1}): {len(pts)} 像素, 最大整数偏差 F={F_max}")

    # 可视化（ASCII）小例：斜率 5/2 的"锯齿直线"
    pts = bresenham(0, 0, 10, 4)
    grid = [[" ."] * 11 for _ in range(5)]
    for (x, y) in pts:
        grid[y][x] = " #"
    print("\n斜率 4/10 的整数直线（# 为命中像素）：")
    for row in reversed(grid):
        print("".join(row))

    print("\n[ALL ASSERTS PASSED] 全部结构断言通过：整数加法与比较，"
          "构造出连续、有界、无冗余的离散直线。")
    print("带走一句（03 章）：z-buffer 把排序变成表示，Bresenham 把除法变成"
          "误差累积——图形学的两大'计算消失术'。")
