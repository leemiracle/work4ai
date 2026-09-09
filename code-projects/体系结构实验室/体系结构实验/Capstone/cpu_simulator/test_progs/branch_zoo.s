# test_progs/branch_zoo.s
# 把 6 种分支指令各跑一次，验证 taken/not taken 都正确
# @expect: x10 = 6   (每个 taken 分支让计数器 +1，应该有 6 个 taken)

            addi  a0, x0, 5
            addi  a1, x0, 5
            addi  a2, x0, 7
            addi  a3, x0, 3
            addi  a4, x0, -1
            addi  s0, x0, 0         # counter = 0

            # 1. beq taken (5 == 5)
            beq   a0, a1, l1
            beq   x0, x0, skip1
        l1:
            addi  s0, s0, 1
        skip1:

            # 2. bne taken (5 != 7)
            bne   a0, a2, l2
            beq   x0, x0, skip2
        l2:
            addi  s0, s0, 1
        skip2:

            # 3. blt taken (3 < 5)
            blt   a3, a0, l3
            beq   x0, x0, skip3
        l3:
            addi  s0, s0, 1
        skip3:

            # 4. bge taken (5 >= 5)
            bge   a0, a1, l4
            beq   x0, x0, skip4
        l4:
            addi  s0, s0, 1
        skip4:

            # 5. bltu taken (3 < 5 unsigned)
            bltu  a3, a0, l5
            beq   x0, x0, skip5
        l5:
            addi  s0, s0, 1
        skip5:

            # 6. bgeu taken (5 >= 3 unsigned)
            bgeu  a0, a3, l6
            beq   x0, x0, skip6
        l6:
            addi  s0, s0, 1
        skip6:

            addi  a0, s0, 0         # mv a0, s0 (期望 6)
            ecall
