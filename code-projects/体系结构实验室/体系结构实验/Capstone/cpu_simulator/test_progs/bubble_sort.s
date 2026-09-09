# test_progs/bubble_sort.s
# 经典冒泡排序：对 5 个元素升序排序
# 程序自身用 sw 初始化数组（同时覆盖 store 指令）
# 覆盖: 嵌套循环 + load/store + 6 种分支 + forwarding
# 排序后 arr[0] 应该是 1（最小值）
# @expect: x10 = 1

            # 在 mem[0x100..0x110] 写入待排序数组 [4, 2, 5, 1, 3]
            lui   s0, 0x0           # s0 = 0
            addi  s0, s0, 0x100     # s0 = 0x100 = array base
            addi  t0, x0, 4
            sw    t0, 0(s0)         # arr[0] = 4
            addi  t0, x0, 2
            sw    t0, 4(s0)         # arr[1] = 2
            addi  t0, x0, 5
            sw    t0, 8(s0)         # arr[2] = 5
            addi  t0, x0, 1
            sw    t0, 12(s0)        # arr[3] = 1
            addi  t0, x0, 3
            sw    t0, 16(s0)        # arr[4] = 3

            # n = 5
            addi  a1, x0, 5

            # 外层循环: i = 0..n-1
            addi  t0, x0, 0         # i = 0
        outer:
            addi  t1, a1, -1        # n - 1
            bge   t0, t1, done      # if i >= n-1, done
            addi  t2, x0, 0         # j = 0
            sub   t3, a1, t0        # n - i
            addi  t3, t3, -1        # n - i - 1
        inner:
            bge   t2, t3, inner_end
            slli  t4, t2, 2         # j * 4
            add   t5, s0, t4        # &arr[j]
            lw    t6, 0(t5)         # arr[j]
            lw    s1, 4(t5)         # arr[j+1]
            ble   t6, s1, no_swap   # 升序: arr[j] <= arr[j+1] 不交换；否则交换
            sw    s1, 0(t5)
            sw    t6, 4(t5)
        no_swap:
            addi  t2, t2, 1
            beq   x0, x0, inner
        inner_end:
            addi  t0, t0, 1
            beq   x0, x0, outer
        done:
            lw    a0, 0(s0)         # 取 arr[0]（排序后应为 1）
            ecall
