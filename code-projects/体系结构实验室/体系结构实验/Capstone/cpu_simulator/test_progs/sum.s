# test_progs/sum.s
# 计算 sum = 1 + 2 + ... + 10 = 55，结果在 a0 (x10)
# 覆盖: addi / add / bne（带分支预测）
# @expect: x10 = 55

            addi  a0, x0, 0         # sum = 0
            addi  a1, x0, 1         # i = 1
            addi  a2, x0, 11        # end = 11 (i 走到 11 时退出)
loop:
            add   a0, a0, a1        # sum += i  (forwarding 依赖)
            addi  a1, a1, 1         # i++
            bne   a1, a2, loop      # if i != 11, loop
            ecall
