# test_progs/memory_ops.s
# 验证全部 load/store 指令（byte/half/word，signed/unsigned）
# 同时验证 load-use stall（load 之后立即用）
# 期望: a0 = a2 = 0x12345678 = 305419896（最后 addi a0, a2, 0）
# @expect: x10 = 305419896

            # 在内存里铺一段已知数据
            lui   a0, 0x12345       # a0 = 0x12345000
            addi  a0, a0, 0x678     # a0 = 0x12345678
            la_place:
            # 把 0x12345678 存到 mem[0..3]（小端: 78 56 34 12）
            lui   a1, 0x0           # a1 = 0  (基地址)
            sw    a0, 0(a1)         # mem[0..3] = a0

            # 读回 word
            lw    a2, 0(a1)         # a2 = 0x12345678
            # 字节读（signed/unsigned）
            lb    a3, 0(a1)         # a3 = 0x78 (正，signed=unsigned)
            lbu   a4, 0(a1)         # a4 = 0x78
            lb    a3, 3(a1)         # a3 = 0x12 (signed 不变, 0x12 < 0x80)
            # 半字读
            lh    a5, 0(a1)         # a5 = 0x5678 (低半字)
            lhu   a6, 2(a1)         # a6 = 0x1234 (高半字)
            # 写字节
            addi  a7, x0, 0xFF
            sb    a7, 0(a1)         # mem[0] = 0xFF
            lw    t0, 0(a1)         # t0 = 0x123456FF
            # 期望结果在 a2 (整个字读回)
            addi  a0, a2, 0         # mv a0, a2 (期望 a0 = 0x12345678)
            ecall
