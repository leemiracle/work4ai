"""针对 demo/calc.py 的测试。运行: python3 -m pytest demo/test_calc.py -q"""


def test_add():
    assert add(2, 3) == 5


def test_sub():
    assert sub(10, 4) == 6


def test_add_zero():
    assert add(0, 0) == 0
