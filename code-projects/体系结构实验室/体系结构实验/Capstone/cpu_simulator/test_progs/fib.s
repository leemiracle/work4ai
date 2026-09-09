# test_progs/fib.s
# 迭代计算斐波那契数列第 N 项，结果在 a1 (x11)
# fib(1)=1, fib(2)=1, fib(3)=2, ..., fib(10)=55
# 覆盖: 多变量依赖链 + 多个分支
# @expect: x11 = 55

            addi  a0, x0, 10        # n = 10
            addi  a1, x0, 0         # a = fib(0) = 0
            addi  a2, x0, 1         # b = fib(1) = 1
loop:
            beq   a0, x0, done      # if n == 0, exit
            add   t0, a1, a2        # t = a + b
            addi  a1, a2, 0         # a = b     (mv a1, a2)
            addi  a2, t0, 0         # b = t     (mv a2, t0)
            addi  a0, a0, -1        # n--
            beq   x0, x0, loop      # 无条件跳回 (用 beq x0,x0)
done:
            ecall
