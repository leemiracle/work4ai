"""范畴论：函子、自然变换与伴随
================================
数学概念：范畴 / 对象 / 态射 / 函子 / 自然变换 / 伴随 / Yoneda / 极限
应用领域：函数式编程(Haskell/Monad) / Lean形式化 / 数据库 / 系统建模 / AI组件化
核心思想：范畴论不关心对象"是什么"，只关心对象"之间的关系"。
  范畴 C = (对象, 态射, 复合, 恒等)
  函子 F:C→D 保持结构（对象→对象，态射→态射）
  自然变换 α:F⇒G 是函子间的映射（"函子的态射"）
  伴随 L⊣R：Hom_D(LA,B) ≅ Hom_C(A,RB)（最接近的翻译）
运行方式：python "33-范畴论.py"
依赖：numpy, matplotlib"""
import numpy as np, matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Callable, Any, List, Generic, TypeVar
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

T = TypeVar('T'); U = TypeVar('U')

# ============ 1. 用Python实现范畴论核心概念 ============

@dataclass
class Morphism:
    """态射：从源对象到目标对象的箭头。"""
    source: str; target: str; name: str; func: Callable

class Category:
    """简单范畴实现：对象 + 态射 + 复合。"""
    def __init__(self, name):
        self.name = name
        self.objects = set()
        self.morphisms = {}  # (source, target) -> Morphism

    def add_object(self, obj):
        self.objects.add(obj)

    def add_morphism(self, src, tgt, name, func):
        self.add_object(src); self.add_object(tgt)
        self.morphisms[(src, tgt)] = Morphism(src, tgt, name, func)

    def identity(self, obj):
        """恒等态射 id_A: A → A"""
        return Morphism(obj, obj, f"id_{obj}", lambda x: x)

    def compose(self, m1, m2):
        """复合 m2 ∘ m1（先 m1 后 m2）"""
        assert m1.target == m2.source
        return Morphism(m1.source, m2.target, f"{m2.name}∘{m1.name}",
                       lambda x: m2.func(m1.func(x)))

# ============ 2. 函子（Functor）============

class ListFunctor:
    """List 函子：Set → Set。
    将类型 T 映射为 List[T]，将函数 f:T→U 映射为 map(f):List[T]→List[U]。
    满足函子律：map(id) = id, map(f∘g) = map(f)∘map(g)
    """
    @staticmethod
    def map_object(T_type):
        return List[T_type]

    @staticmethod
    def map_morphism(f: Callable[[T], U]) -> Callable[[List[T]], List[U]]:
        return lambda lst: [f(x) for x in lst]

class MaybeFunctor:
    """Maybe 函子：T → Optional[T]。
    处理"可能失败"的计算。
    """
    @staticmethod
    def map_morphism(f):
        return lambda x: None if x is None else f(x)

# ============ 3. 实验 ============

def main():
    print("="*60); print("实验 1：范畴 = 对象 + 态射"); print("="*60)
    # 构造一个简单的"类型范畴"（Set 的子范畴）
    cat = Category("小范畴")
    cat.add_morphism("Int", "String", "show", str)
    cat.add_morphism("String", "Int", "parse", lambda s: int(s) if s.isdigit() else 0)
    cat.add_morphism("Int", "Float", "toFloat", float)
    cat.add_morphism("Float", "Int", "round", round)
    print(f"范畴 '{cat.name}' 的对象: {cat.objects}")
    print(f"态射:")
    for (src, tgt), m in cat.morphisms.items():
        print(f"  {src} --{m.name}--> {tgt}")

    # 复合
    show = cat.morphisms[("Int","String")]
    parse = cat.morphisms[("String","Int")]
    print(f"\n复合 parse ∘ show: Int → Int")
    composed = cat.compose(show, parse)
    print(f"  (parse∘show)(42) = {composed.func(42)}")

    print("\n"+"="*60); print("实验 2：函子——保持结构的映射"); print("="*60)
    # List 函子
    f = lambda x: x * 2  # Int → Int
    Ff = ListFunctor.map_morphism(f)  # List[Int] → List[Int]
    print(f"函数 f(x) = x*2")
    print(f"List 函子提升后 Ff([1,2,3]) = {Ff([1,2,3])}")

    # 函子律验证
    identity_list = ListFunctor.map_morphism(lambda x: x)
    assert identity_list([1,2,3]) == [1,2,3], "恒等律失败"
    g = lambda x: x + 1
    Fg = ListFunctor.map_morphism(g)
    composed_fg = lambda lst: Ff(Fg(lst))
    map_composed = ListFunctor.map_morphism(lambda x: f(g(x)))
    assert composed_fg([1,2,3]) == map_composed([1,2,3]), "复合律失败"
    print(f"\n函子律验证：")
    print(f"  恒等律 map(id)([1,2,3]) = {identity_list([1,2,3])} = [1,2,3] ✓")
    print(f"  复合律 map(f∘g) = map(f)∘map(g) ✓")
    print(f"\n[解读] 函子 = '提升'：把普通函数提升到容器(List/Maybe)上。")
    print(f"       Python 的 map()、Scala 的 .map、Haskell 的 fmap 都是函子。")

    print("\n"+"="*60); print("实验 3：自然变换——函子间的映射"); print("="*60)
    # head: List → Maybe（取第一个元素，空列表→None）
    def natural_transform_head(lst):
        """head: ListFunctor ⇒ MaybeFunctor
        将 List[T] 映射到 Optional[T]（第一个元素或 None）。
        自然性条件：head ∘ map(f) = map_maybe(f) ∘ head
        """
        return lst[0] if lst else None

    # 验证自然性条件
    test_lists = [[1,2,3], [], [5]]
    f_str = str  # Int → String
    print(f"自然变换 head: List → Maybe（取首元素）")
    print(f"验证自然性 head(map(f)(lst)) = map_maybe(f)(head(lst)):")
    for lst in test_lists:
        left = natural_transform_head(ListFunctor.map_morphism(f_str)(lst))
        right = MaybeFunctor.map_morphism(f_str)(natural_transform_head(lst))
        print(f"  lst={str(lst):<12} 左={left}  右={right}  {'✓' if left == right else '✗'}")

    print(f"\n[解读] 自然变换 = 函子间的'态射'。")
    print(f"       head 把 List 变成 Maybe，且'先映射再取首' = '先取首再映射'。")
    print(f"       这种'交换性'就是自然性的本质。")

    print("\n"+"="*60); print("实验 4：伴随——'最接近的翻译'"); print("="*60)
    print("伴随 L ⊣ R：Hom(L(A), B) ≅ Hom(A, R(B))")
    print("\n经典伴随：Free ⊣ Forgetful")
    print("  自由群函子 F: Set → Grp（给集合配最一般群结构）")
    print("  遗忘函子 U: Grp → Set（忘掉群结构只留集合）")
    print("  Hom_Grp(F(S), G) ≅ Hom_Set(S, U(G))")
    print("  含义：'从S生成的群到G的群同态' = '从S到G底层集合的函数'")

    print("\n"+"="*60); print("实验 5：Monad——计算效应的范畴论"); print("="*60)
    print("Monad = '自函子范畴上的幺半对象'")
    print("  T: C → C（自函子，如 List: Set → Set）")
    print("  unit: A → T(A)（注入，如 x → [x]）")
    print("  join: T(T(A)) → T(A)（扁平化，如 [[1],[2]] → [1,2]）")
    # 演示
    unit_list = lambda x: [x]
    join_list = lambda lst_of_lst: [x for sub in lst_of_lst for x in sub]
    print(f"\n  unit(42) = {unit_list(42)}")
    print(f"  join([[1,2],[3],[4,5]]) = {join_list([[1,2],[3],[4,5]])}")
    print(f"\nMonad 三定律：")
    print(f"  1. join ∘ unit = id（注入后扁平化 = 不变）")
    print(f"  2. join ∘ map(unit) = id（同样）")
    print(f"  3. join ∘ join = join ∘ map(join)（结合律）")

    print("\n"+"="*60); print("实验 6：范畴论的应用"); print("="*60)
    apps = [("Haskell Monad", "IO/Maybe/List/State 都是 Monad"),
            ("Lean Mathlib", "范畴论组织数学知识"),
            ("数据库", "Entity-Relation = 范畴的 sketch"),
            ("信号处理", "信号 = 对象，滤波器 = 态射，串联 = 复合"),
            ("AI Agent", "组件 = 对象，接口 = 态射，编排 = 函子"),
            ("拓扑数据分析", "持续同调 = 范畴论函子")]
    for app, desc in apps: print(f"  {app:<18} → {desc}")

    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    ax = axes[0]
    # 画范畴图
    objects = {'A': (0.2, 0.5), 'B': (0.5, 0.8), 'C': (0.8, 0.5), 'D': (0.5, 0.2)}
    for name, (x, y) in objects.items():
        ax.scatter(x, y, s=500, c='steelblue', zorder=5)
        ax.text(x, y, name, ha='center', va='center', fontsize=14, color='white', fontweight='bold')
    arrows = [('A','B','f'),('B','C','g'),('A','D','h'),('D','C','k')]
    for src, tgt, label in arrows:
        x1, y1 = objects[src]; x2, y2 = objects[tgt]
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', lw=2, color='red'))
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.02, my+0.02, label, fontsize=12, color='red')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_title('范畴：对象 + 态射 + 复合'); ax.axis('off')
    # 画函子图
    ax = axes[1]
    # 范畴 C
    for name, x, y in [('A', 0.1, 0.7), ('B', 0.3, 0.7)]:
        ax.scatter(x, y, s=400, c='steelblue', zorder=5)
        ax.text(x, y, name, ha='center', va='center', fontsize=12, color='white')
    ax.annotate('', xy=(0.3,0.7), xytext=(0.1,0.7), arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))
    ax.text(0.2, 0.75, 'f', fontsize=11, ha='center', color='red')
    ax.text(0.2, 0.5, 'F', fontsize=20, ha='center', color='green')
    ax.annotate('', xy=(0.2, 0.62), xytext=(0.2, 0.4), arrowprops=dict(arrowstyle='->', lw=3, color='green'))
    # 范畴 D
    for name, x, y in [('F(A)', 0.55, 0.7), ('F(B)', 0.85, 0.7)]:
        ax.scatter(x, y, s=400, c='coral', zorder=5)
        ax.text(x, y, name, ha='center', va='center', fontsize=9, color='white')
    ax.annotate('', xy=(0.85,0.7), xytext=(0.55,0.7), arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))
    ax.text(0.7, 0.75, 'F(f)', fontsize=11, ha='center', color='red')
    ax.set_xlim(0, 1); ax.set_ylim(0.2, 0.9)
    ax.set_title('函子 F:C→D：保持结构'); ax.axis('off')
    plt.tight_layout(); plt.savefig("33-范畴论_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 33-范畴论_结果.png")
    print("\n[总结] 1. 范畴=对象+态射+复合+恒等(只看关系不看内部)")
    print("2. 函子=范畴间的保结构映射(Python map/Haskell fmap)")
    print("3. 自然变换=函子间的态射(交换性=自然性)")
    print("4. 伴随Free⊣Forgetful='最接近的翻译'")
    print("5. Monad=自函子+unit+join=计算效应的抽象(Haskell/函数式)")

if __name__ == "__main__": main()
