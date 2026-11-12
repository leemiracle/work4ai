# -*- coding: utf-8 -*-
"""
列昂惕夫逆阵与乘数断言（走廊1：投入产出引擎 + 走廊2：乘数模拟）
对应章：讲透国民经济学/04-国民经济学转代码.md

数据：三部门直接消耗系数矩阵 A——【教学构造】（列和均 <1，
满足经济可行性；非任何年份官方表，口径见注）。真实表入口：
OECD ICIO / 中国全国投入产出表。
"""
import numpy as np

A = np.array([
    [0.20, 0.10, 0.05],   # 部门1 消耗各部门的中间投入（列=投入来源）
    [0.15, 0.30, 0.10],
    [0.10, 0.05, 0.15],
])
SECTORS = ["农业与原料", "制造业", "服务业"]
I3 = np.eye(3)

def main():
    # 断言1：三路互验——矩阵求逆 / 逐列线性求解 / 诺伊曼级数
    L_inv = np.linalg.inv(I3 - A)
    L_solve = np.linalg.solve(I3 - A, I3)
    L_series = sum(np.linalg.matrix_power(A, k) for k in range(60))
    assert np.allclose(L_inv, L_solve, atol=1e-12)
    assert np.allclose(L_inv, L_series, atol=1e-8)
    print(f"[1] 列昂惕夫逆阵三路互验一致（求逆=求解=级数）✓")
    print(f"    (I-A)^-1 =\n{np.round(L_inv, 4)}")

    # 断言2：部门乘数（逆阵列和）均 >1——完全拉动>直接拉动
    multipliers = L_inv.sum(axis=0)
    assert np.all(multipliers > 1.0), multipliers
    assert multipliers.argmax() == 1  # 制造业列直接消耗最大→乘数最大
    print(f"[2] 部门乘数：{dict(zip(SECTORS, np.round(multipliers, 3)))}"
          f"（均>1；制造业最大=高影响力部门）")

    # 断言3：需求冲击传播——制造业最终需求+10，三部门产出齐增、
    #        本部门增幅>冲击本身（乘数），且恒等式 X=AX+Y 成立
    dY = np.array([0.0, 10.0, 0.0])
    dX = L_inv @ dY
    assert dX[1] > 10.0 and np.all(dX > 0), dX
    X = L_inv @ np.array([20.0, 50.0, 30.0])   # 基准最终需求
    assert np.allclose(X, A @ X + np.array([20.0, 50.0, 30.0]), atol=1e-9)
    print(f"[3] 冲击传播：制造业需求+10 → 产出增量 {np.round(dX, 3)}"
          f"（本部门+{dX[1]:.2f}>10，另两部门被拉动）；恒等式 X=AX+Y ✓")

    # 断言4：收敛判据——谱半径<1 ⇔ 级数收敛 ⇔ 经济可行
    rho = max(abs(np.linalg.eigvals(A)))
    col_sums = A.sum(axis=0)
    assert rho < 1 and np.all(col_sums < 1)
    residual = np.linalg.norm(
        L_series - sum(np.linalg.matrix_power(A, k) for k in range(40)))
    assert residual < 1e-8   # 再加 20 项几乎不再变化（收敛中）
    print(f"[4] 收敛判据：谱半径 ρ(A)={rho:.3f}<1，最大列和 "
          f"{col_sums.max():.2f}<1——经济可行=级数收敛")

    # 断言5：凯恩斯乘数——MPC=0.8 时几何级数恰为 5
    mpc = 0.8
    chain = sum(mpc ** k for k in range(150))   # 1+0.8+0.64+…（尾部<1e-14）
    assert abs(1 / (1 - mpc) - 5.0) < 1e-9 and abs(chain - 5.0) < 1e-8
    print(f"[5] 凯恩斯乘数：1/(1-0.8)=5 = 支出链求和 {chain:.6f}"
          f"——与列昂惕夫级数同一个数学灵魂（自引用结构=几何级数）")

    print("\n全部断言通过 ✓ （三路对账=矩阵计算的护城河）")

if __name__ == "__main__":
    main()
