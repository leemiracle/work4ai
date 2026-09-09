# test_progs/function_call.s
# 验证 JAL / JALR 函数调用与返回地址
# 调用函数 double(x) 返回 2*x；主程序算 double(21) = 42
# 覆盖: jal/jalr/ret 伪指令 + 函数 ABI
# @expect: x10 = 42

            addi  a0, x0, 21        # 参数: 21
            jal   ra, double        # 调用 double，返回值在 a0
            # a0 现在应该是 42
            ecall

            # 函数 double(a0) = a0 * 2 (用加法)
            double:
            add   a0, a0, a0        # a0 *= 2
            jalr  x0, ra, 0         # ret (jalr x0, ra, 0)
