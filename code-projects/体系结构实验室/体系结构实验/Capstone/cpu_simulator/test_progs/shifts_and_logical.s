# test_progs/shifts_and_logical.s
# 验证全部移位与逻辑指令
# 覆盖: slli/srli/srai/sll/srl/sra/and/or/xor/andi/ori/xori
# 期望: t0=0x40, t1=0x10, t2=0xff000000, t3=0x0c, t4=0x33, t5=0x03, t6=0x30
# @expect: x5  = 64

            addi  t0, x0, 0x100     # 0x100
            srli  t0, t0, 2         # 0x40 = 64        ← 期望值
            slli  t1, t0, 2         # 0x100
            srli  t1, t1, 4         # 0x10
            # 算术右移: 0x80000000 的 sar
            lui   t2, 0x80000       # t2 = 0x80000000
            srai  t2, t2, 4         # 算术右移 4 位 → 0xF8000000
            # 逻辑与/或/异或
            addi  t3, x0, 0x0F
            addi  t4, x0, 0x33
            and   t5, t3, t4        # 0x0F & 0x33 = 0x03
            or    t6, t3, t4        # 0x0F | 0x33 = 0x3F (但我们只测 t0)
            xor   t5, t3, t4        # 0x0F ^ 0x33 = 0x3C
            # R-type 变量移位
            addi  t6, x0, 4
            sll   t4, t0, t6        # 0x40 << 4 = 0x400
            srl   t4, t4, t6        # 0x400 >> 4 = 0x40
            ecall
