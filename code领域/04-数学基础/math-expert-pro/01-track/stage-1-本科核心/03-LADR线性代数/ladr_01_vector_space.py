"""
LADR 核心 1: 向量空间 — 从「箭头」到「抽象结构」
================================================
阶段1 / 模块03 / LADR 第1弹 (Axler 公理化线代)
向量不再是箭头, 而是「满足公理的任何对象」(多项式/矩阵/函数都是向量!)
运行: python3 ladr_01_vector_space.py  (4 张 PNG)

§1 向量空间公理: 抽象的力量 (R^n / 多项式 / 矩阵都是向量空间)
§2 张成 / 线性无关 (子空间的生成)
§3 基与维度 (同一向量的不同表示)
§4 线性映射 + 核与像 (保持结构的函数)
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# §1 向量空间公理
def section_1_axioms():
    print("=" * 70)
    print("§1 向量空间公理: 抽象的力量")
    print("=" * 70)
    print("""
    LADR 定义 (公理化!): 向量空间 V 是一个集合, 配加法 + 数乘, 满足 8 条公理:
      1. 加法交换 u+v=v+u           5. 数乘分配  a(u+v)=au+av
      2. 加法结合                   6. 数乘分配  (a+b)u=au+bu
      3. 零元  u+0=u                7. 数乘结合  a(bu)=(ab)u
      4. 逆元  u+(-u)=0             8. 单位元    1u=u
    ⭐ 关键: 向量不一定是「箭头」! 满足公理的任何对象都是向量:
        R^n (数), 多项式 P_n, m×n 矩阵, 连续函数 C[a,b]...
    这就是「抽象」的威力: 一套定理对所有向量空间通用。
    """)
    # 验证 R^2 和 多项式 P_2 都满足向量空间公理 (抽查关键几条)
    # R^2
    u = np.array([1.0, 2.0]); v = np.array([3.0, 1.0])
    print(f"  R² 验证:")
    print(f"    交换 u+v=v+u: {np.allclose(u+v, v+u)}")
    print(f"    零元 u+0=u: {np.allclose(u+np.zeros(2), u)}")
    print(f"    逆元 u+(-u)=0: {np.allclose(u+(-u), np.zeros(2))}")
    # 多项式 P_2: 用系数向量 [a,b,c] 表示 a+bx+cx²
    p = np.array([1, 2, 3]); q = np.array([0, 1, -1])   # p=1+2x+3x², q=x-x²
    print(f"  P_2 (多项式空间, 系数向量) 验证:")
    print(f"    加法对应系数相加: p+q = {(p+q).tolist()} (即 {p[0]+q[0]}+{p[1]+q[1]}x+{p[2]+q[2]}x²)")
    print(f"    数乘 2p = {(2*p).tolist()} (多项式也是向量!)")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.text(0.05, 0.8, "向量空间成员 (都满足 8 公理):\n\n"
                       "  • R^n  几何箭头 / 数据点\n"
                       "  • P_n  多项式 (系数作坐标)\n"
                       "  • M_{m,n}  矩阵\n"
                       "  • C[a,b]  连续函数\n"
                       "  • 概率分布 (期望有限)\n\n"
                       "→ 一套向量空间定理 = 全部适用",
            fontsize=12, family='monospace', va='top')
    ax.axis('off'); ax.set_title('抽象的威力: 「向量」远不止箭头')
    plt.tight_layout(); plt.savefig('ladr_vs_s1.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ladr_vs_s1.png")


# §2 张成与线性无关
def section_2_span():
    print("\n" + "=" * 70)
    print("§2 张成 / 线性无关")
    print("=" * 70)
    print("""
    张成: 向量 v₁..v_n 的所有线性组合 c₁v₁+..+c_nv_n 构成的集合。
    线性无关: 没有一个 v_i 能表为其他的线性组合。
    相关 ⟺ 行列式 = 0 (方阵时)。
    """)
    # R^3 中: 2 个向量张成平面, 3 个无关向量张成全空间
    fig = plt.figure(figsize=(13, 4.5))
    # 两向量张成平面
    v1 = np.array([1, 0, 1]); v2 = np.array([0, 1, 1])
    ax1 = fig.add_subplot(131, projection='3d')
    s, t = np.meshgrid(np.linspace(-2, 2, 10), np.linspace(-2, 2, 10))
    plane = s[..., None] * v1 + t[..., None] * v2
    ax1.plot_surface(plane[..., 0], plane[..., 1], plane[..., 2], alpha=0.4)
    for v, c in [(v1, 'r'), (v2, 'g')]:
        ax1.plot([0, v[0]], [0, v[1]], [0, v[2]], c, lw=3)
    ax1.set_title(f'2 个向量张成「平面」(2维子空间)')
    # 3 个无关向量张成全 R^3
    ax2 = fig.add_subplot(132, projection='3d')
    v3 = np.array([1, 1, 0])
    det = np.linalg.det(np.array([v1, v2, v3]).T)
    for v, c in [(v1, 'r'), (v2, 'g'), (v3, 'b')]:
        ax2.plot([0, v[0]], [0, v[1]], [0, v[2]], c, lw=3)
    ax2.set_title(f'3 个无关向量张成 R³\ndet={det:.1f}≠0 → 无关')
    # 3 个相关向量 (在第3个可由前两个表示)
    ax3 = fig.add_subplot(133, projection='3d')
    v3_dep = v1 + v2   # 相关
    det2 = np.linalg.det(np.array([v1, v2, v3_dep]).T)
    for v, c in [(v1, 'r'), (v2, 'g'), (v3_dep, 'b')]:
        ax3.plot([0, v[0]], [0, v[1]], [0, v[2]], c, lw=3)
    ax3.set_title(f'3 个相关向量 (v3=v1+v2)\ndet={det2:.1f}=0 → 相关')
    plt.tight_layout(); plt.savefig('ladr_vs_s2.png', dpi=100, bbox_inches='tight')
    print(f"  det([v1,v2,v3]) 无关时 = {det:.2f} (≠0)")
    print(f"  det([v1,v2,v3_dep]) 相关时 = {det2:.2f} (=0)")
    print("  [图已保存] ladr_vs_s2.png")


# §3 基与维度
def section_3_basis():
    print("\n" + "=" * 70)
    print("§3 基与维度: 同一向量的不同表示")
    print("=" * 70)
    print("""
    基: 张成 V 且线性无关的向量组。基的个数 = 维度 dim(V)。
    同一向量在不同基下有不同坐标 (但本质相同)。
    这是 LADR 的核心洞察: 坐标是「相对的」, 向量是「绝对的」。
    """)
    # 标准基 vs 自定义基下, 同一点 [3,2] 的坐标
    v = np.array([3.0, 2.0])
    e1, e2 = np.array([1, 0]), np.array([0, 1])          # 标准基
    b1, b2 = np.array([1, 1]), np.array([1, -1])         # 自定义基
    # v 在自定义基下的坐标: 解 [b1 b2] c = v
    B = np.column_stack([b1, b2])
    coords = np.linalg.solve(B, v)
    print(f"  向量 v = {v}")
    print(f"  标准基下坐标: {v} (平凡)")
    print(f"  自定义基 {{[1,1],[1,-1]}} 下坐标: {coords}")
    print(f"  验证: {coords[0]}·b1 + {coords[1]}·b2 = {coords[0]*b1 + coords[1]*b2}")

    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.plot([0, v[0]], [0, v[1]], 'k-', lw=3)
    ax.plot(*v, 'ko', ms=10)
    ax.arrow(0, 0, b1[0], b1[1], head_width=0.1, color='red', lw=2, length_includes_head=True)
    ax.arrow(0, 0, b2[0], b2[1], head_width=0.1, color='green', lw=2, length_includes_head=True)
    ax.arrow(0, 0, coords[0]*b1[0], coords[0]*b1[1], head_width=0.1, color='red', alpha=0.5, lw=1.5, length_includes_head=True)
    ax.arrow(*coords[0]*b1, coords[1]*b2[0], coords[1]*b2[1], head_width=0.1, color='green', alpha=0.5, lw=1.5, length_includes_head=True)
    ax.text(1.1, 1.1, f'b1=[1,1]', color='red', fontsize=12)
    ax.text(1.1, -1.3, f'b2=[1,-1]', color='green', fontsize=12)
    ax.text(3.1, 2.1, f'v={v.tolist()}\n= {coords[0]:.2f}·b1 + {coords[1]:.2f}·b2', fontsize=11)
    ax.set_xlim(-1.5, 4); ax.set_ylim(-2, 3); ax.set_aspect('equal')
    ax.axhline(0, color='gray', lw=0.5); ax.axvline(0, color='gray', lw=0.5)
    ax.grid(True, ls=':', alpha=0.3)
    ax.set_title('基与坐标: 同一向量在不同基下坐标不同\nv=[3,2] 在 {[1,1],[1,-1]} 基下 = [2.5, 0.5]')
    plt.tight_layout(); plt.savefig('ladr_vs_s3.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ladr_vs_s3.png")


# §4 线性映射 + 核与像
def section_4_maps():
    print("\n" + "=" * 70)
    print("§4 线性映射 + 核与像")
    print("=" * 70)
    print("""
    线性映射 T: V→W 满足 T(au+bv) = aT(u)+bT(v) (保持加法+数乘)。
    核 ker(T) = 被 T 映为 0 的所有向量 (T 的「盲点」)。
    像 im(T) = T 的所有输出。
    维度定理: dim(V) = dim(ker T) + dim(im T)  ← LADR 的核心定理。
    """)
    # 投影 T(x,y,z) = (x,y,0): 核=z轴, 像=xy平面
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection='3d')
    # 几个被投影的向量
    for v in [[1,1,2], [2,-1,1.5], [-1,2,1], [1.5,1.5,-1]]:
        v = np.array(v, float)
        proj = np.array([v[0], v[1], 0])
        ax.plot([0, v[0]], [0, v[1]], [0, v[2]], 'b-', lw=1.5)
        ax.plot([v[0], proj[0]], [v[1], proj[1]], [v[2], proj[2]], 'r--', lw=1)
        ax.plot([0, proj[0]], [0, proj[1]], [0, 0], 'r-', lw=2.5)
    # 标核 (z轴) 和像 (xy平面)
    ax.plot([0,0],[0,0],[-2.5,2.5], 'green', lw=3, label='ker(T)=z轴 (被映为0)')
    xx, yy = np.meshgrid(np.linspace(-2,2,5), np.linspace(-2,2,5))
    ax.plot_surface(xx, yy, 0*xx, alpha=0.15, color='orange')
    ax.text(0,0,2.7, 'ker(T)', color='green', fontsize=11)
    ax.text(2.2,2.2,0.3, 'im(T)=xy面', color='orange', fontsize=11)
    ax.set_title('线性映射 T(x,y,z)=(x,y,0) 投影:\n蓝→原向量, 红→投影(在像上), 绿→核(z轴)')
    ax.set_xlim(-2.5,2.5); ax.set_ylim(-2.5,2.5); ax.set_zlim(-2.5,2.5)
    plt.tight_layout(); plt.savefig('ladr_vs_s4.png', dpi=100, bbox_inches='tight')
    print("  T(x,y,z) = (x,y,0) 投影映射:")
    print("    dim(V)=3, dim(ker T)=1(z轴), dim(im T)=2(xy面)")
    print("    验证维度定理: 3 = 1 + 2 ✓")
    print("  [图已保存] ladr_vs_s4.png")


if __name__ == "__main__":
    print("📐 LADR 核心 1: 向量空间  |  阶段1 / 模块03\n")
    section_1_axioms()
    section_2_span()
    section_3_basis()
    section_4_maps()
    print("\n" + "=" * 70)
    print("✅ 跑通! 读 ladr_01_vector_space.md, 做练习")
    print("=" * 70)
