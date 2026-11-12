"""Richardson 军备竞赛模型：稳定性判据 fc>ab（断言自验）
对应《讲透国防经济学》00 章（美之时刻①）、03 章（构造一）、
04 章（走廊 1：军备竞赛走廊）。

模型（Richardson 1919）：
    ẋ = a·y − f·x + g        x, y = 两国军备水平
    ẏ = b·x − c·y + h        a, b = 防御反应系数；f, c = 疲劳/抑制系数
                             g, h = 历史积怨（与对手无关的基线敌意）
    均衡：x* = (c·g + a·h)/(fc−ab)，y* = (b·g + f·h)/(fc−ab)
    稳定性：雅可比 [[−f, a],[b, −c]] 的特征值实部全负 ⟺ f·c > a·b

断言（自验证）：
    (a) 稳定组（fc>ab）：RK4 数值轨迹收敛到解析均衡（相对误差 < 1e-3），
        且数值特征值实部全负
    (b) 不稳定组（fc<ab）：轨迹发散（终值范数 > 初值范数 × 100），
        且存在正实部特征值——"军备螺旋"现场
    (c) 对称无积怨组（g=h=0, fc>ab）：军备完全裁撤归零——
        对称互信的数学面（均衡在原点）
"""
import numpy as np


def deriv(t, s, a, b, f, c, g, h):
    x, y = s
    return np.array([a * y - f * x + g, b * x - c * y + h])


def rk4(a, b, f, c, g, h, s0, T=50.0, dt=0.01):
    """经典四阶 Runge-Kutta 积分（动力系统走廊的标准工具）。"""
    s = np.array(s0, float)
    n = int(T / dt)
    for _ in range(n):
        k1 = deriv(0, s, a, b, f, c, g, h)
        k2 = deriv(0, s + dt / 2 * k1, a, b, f, c, g, h)
        k3 = deriv(0, s + dt / 2 * k2, a, b, f, c, g, h)
        k4 = deriv(0, s + dt * k3, a, b, f, c, g, h)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return s


def eigen_real_parts(a, b, f, c):
    return np.linalg.eigvals(np.array([[-f, a], [b, -c]])).real


def main():
    # ── (a) 稳定：抑制之积胜过反应之积 ──
    a, b, f, c, g, h = 0.3, 0.3, 0.5, 0.5, 1.0, 1.0
    det = f * c - a * b
    eq = np.array([(c * g + a * h) / det, (b * g + f * h) / det])
    s_end = rk4(a, b, f, c, g, h, s0=(0.5, 0.4))
    err = np.abs(s_end - eq) / eq
    eig = eigen_real_parts(a, b, f, c)
    print(f"(a) 稳定组 fc={f*c} > ab={a*b}：解析均衡={eq}  "
          f"数值终值={s_end.round(6)}  相对误差={err.max():.2e}   (断言 < 1e-3)")
    print(f"    特征值实部={eig.round(4)}  (断言全负)")
    assert err.max() < 1e-3 and (eig < 0).all(), "fc>ab 应收敛且特征值实部全负"

    # ── (b) 不稳定：反应之积压倒抑制之积──军备螺旋 ──
    a, b, f, c, g, h = 0.6, 0.6, 0.3, 0.3, 0.0, 0.0
    s0, s_end = np.array([0.5, 0.4]), rk4(a, b, f, c, g, h, s0=(0.5, 0.4))
    eig = eigen_real_parts(a, b, f, c)
    growth = np.linalg.norm(s_end) / np.linalg.norm(s0)
    print(f"(b) 不稳定组 fc={f*c} < ab={a*b}：终值={s_end}  "
          f"范数增长={growth:.0f} 倍  特征值实部={eig.round(4)}  "
          f"(断言增长 > 100 且存在正实部)")
    assert growth > 100 and (eig > 0).any(), "fc<ab 应发散（军备螺旋失控）"

    # ── (c) 对称无积怨：均衡在原点，军备可完全归零 ──
    a, b, f, c, g, h = 0.3, 0.3, 0.5, 0.5, 0.0, 0.0
    s_end = rk4(a, b, f, c, g, h, s0=(2.0, 1.0))
    print(f"(c) 对称无积怨（g=h=0, fc>ab）：从 (2,1) 收敛到 {s_end.round(6)}  "
          f"(断言 < 1e-3)")
    assert np.abs(s_end).max() < 1e-3, "对称互信下军备应归零"

    print("\n全部断言通过 ✅  Richardson：一条不等式分开和平与螺旋——")
    print("抑制之积 fc 压过反应之积 ab 则均衡存在；单方面克制不保证稳定")
    print("（自己的 a 调低，对手的 b 仍可能把系统拖进发散区）。")
    print("带走一句（00 章）：军备竞赛是可构造系统，但它的参数是恐惧——")
    print("气象学家算得出轨迹，算不出人有多怕。")

if __name__ == "__main__":
    main()
