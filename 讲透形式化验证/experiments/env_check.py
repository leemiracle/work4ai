"""环境自检：工具生态卷全部 lab 的依赖一次验通。
跑法: python env_check.py
全部 OK 才开始后续章节。"""
import importlib

DEPS = {  # 模块名: (导入名, 一句话用途)
    "z3-solver": ("z3", "SMT 求解（lab03/04/06/09）"),
    "cvc5": ("cvc5", "SMT 求解器对拍（lab03）"),
    "dd": ("dd", "BDD 库（lab12）"),
    "automata-lib": ("automata", "自动机库（lab14）"),
    "pyformlang": ("pyformlang", "形式语言库（lab13/14）"),
    "numpy": ("numpy", "数值计算（lab05/10/11）"),
    "scipy": ("scipy", "稀疏矩阵（lab11）"),
}

def main():
    ok = True
    for pkg, (mod, use) in DEPS.items():
        try:
            importlib.import_module(mod)
            print(f"[OK]   {pkg:<14} → {use}")
        except ImportError as e:
            ok = False
            print(f"[FAIL] {pkg:<14} → {e}")
    # 快速功能冒烟
    from z3 import Int, Solver
    s = Solver(); x = Int("x"); s.add(x > 1)
    assert s.check(), "z3 冒烟失败"
    print("\n环境自检:", "全部通过" if ok else "存在缺失，先补装")
    assert ok

if __name__ == "__main__":
    main()
