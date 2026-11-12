#!/usr/bin/env python3
"""lab04 · 有界模型检查：把循环程序 k 步展开喂给 SMT（04 章 §二）。
程序: a[3]; for i in 0..2: a[i]=i;
断言1: a[0]+a[1]+a[2]==3  → 成立（编码取反后 UNSAT）
断言2: a[0]+a[1]+a[2]==7  → 违反（取反后 SAT，反例=模型）
手推锚点（章内§二）: SSA 展开 σ0→σ1→σ2→σ3，a0_σ3=0, a1_σ3=1, a2_σ3=2。
"""
import argparse
from z3 import Int, Solver, Not, unsat


def bmc_check(prop_value):
    """展开 k=3 的编码，prop_value 为断言的期望值。返回 ('成立'|'违反', model|None)。"""
    s = Solver()
    # k 步展开的 SSA 变量: a_{j}_k 表示第 k 轮后 a[j] 的值; 本例每轮只写一个下标
    a0_1, a1_2, a2_3 = Int("a0_1"), Int("a1_2"), Int("a2_3")
    s.add(a0_1 == 0)          # i=0: a[0]=0（其后不再写）
    s.add(a1_2 == 1)          # i=1: a[1]=1
    s.add(a2_3 == 2)          # i=2: a[2]=2
    # 断言取反 = 存在执行到此处且断言不成立 → SAT 即反例
    s.add(Not(a0_1 + a1_2 + a2_3 == prop_value))
    r = s.check()
    if r == unsat:
        return "成立", None
    return "违反", s.model()


def selftest():
    r, _ = bmc_check(3)
    assert r == "成立", r
    r, m = bmc_check(7)
    assert r == "违反" and m is not None
    print("反例模型:", m)
    print("lab04 自检通过: ==3 成立 / ==7 违反 ✓")


def native_cbmc():
    p = argparse.ArgumentParser(); p.add_argument("--native", action="store_true")
    if p.parse_args().native:
        import subprocess
        out = subprocess.run(["cbmc", "loop3.c", "--unwind", "3"],
                             capture_output=True, text=True)
        print(out.stdout[-2000:])
    else:
        print("（默认跳过 cbmc；正文给 Windows 安装命令: github.com/diffblue/cbmc/releases zip 解压加 PATH）")


if __name__ == "__main__":
    selftest(); native_cbmc()
