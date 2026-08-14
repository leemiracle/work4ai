"""演示目标文件: 故意带一个 bug。add() 实现成了减法。"""


def add(a, b):
    return a - b   # bug: 应为 a + b


def sub(a, b):
    return a - b
