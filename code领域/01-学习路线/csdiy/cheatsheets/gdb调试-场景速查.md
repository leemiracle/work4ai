# GDB 调试 · 场景速查

> 命令原文 + 一句话场景。崩溃先看 bt，死锁先 info threads。

## 🚨 最常用 5 条
```bash
gdb ./a.out            # 启动调试程序
run / r                # 跑起来（可带参数: run arg1 arg2）
break main / b main    # 在函数处下断点
next / n               # 单步步过（不进函数）
backtrace / bt         # 查看调用栈——崩溃第一件事
```

---

## 调试 segfault（段错误）
```bash
gdb ./a.out                         # 加载程序
run                                 # 跑，崩了它会停
bt                                  # 看调用栈，找到崩在哪一行
bt full                             # 带所有局部变量的调用栈
frame 2 / f 2                       # 切到栈的第 2 层
list / l                            # 看当前位置附近的源码
print var / p var                   # 打印变量值
p *ptr@10                           # 把指针当数组，看连续 10 个元素
```

## 编译时必须加调试信息（否则看不到源码行号）
```bash
gcc -g -O0 hello.c -o hello         # -g 加调试符号，-O0 关优化（否则变量被优化掉）
g++ -g -fsanitize=address main.cpp  # 开 AddressSanitizer，越界/野指针立刻报
```

## 断点管理
```bash
b main                              # 函数断点
b file.c:42                         # 文件第 42 行断点
b func if x > 10                    # 条件断点，满足才停
info breakpoints / i b              # 列出所有断点
delete 2 / d 2                      # 删第 2 号断点
disable 1                           # 暂时关掉第 1 号断点
clear func                          # 清除某函数的所有断点
continue / c                        # 继续跑到下一个断点
```

## 单步执行
```bash
step / s                            # 单步步入（进函数内部）
next / n                            # 单步步过（函数当一步）
finish                              # 跑完当前函数并停下
until / u                           # 跳出循环体到下一行
```

## 多线程调试
```bash
info threads                        # 列出所有线程及所在位置
thread 3 / t 3                      # 切到 3 号线程
break func thread 3                 # 只在 3 号线程进入 func 时停
set scheduler-locking on            # 锁住调度，只让当前线程跑（调死锁神器）
thread apply all bt                 # 所有线程都打调用栈——查死锁必跑
```

## attach 到正在运行的进程
```bash
gdb -p <PID>                        # 直接附加到进程，不用重启
gdb ./a.out <PID>                   # 同上，带上程序名更准
# 或进去后：attach <PID>
detach                              # 脱离进程，让它继续跑
# 附加失败多半是权限，用 sudo 或设置 ptrace_scope:
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

## 看内存
```bash
x/16xw $rsp                         # 以十六进制看栈顶 16 个字(word)
x/8xb ptr                           # 看指针处 8 个字节
x/s str                             # 当 C 字符串看
x/i $pc                             # 反汇编当前指令
p/x var                             # 十六进制打印变量
ptype struct_name                   # 看结构体定义
```

## watchpoint（数据断点：某变量被改时停）
```bash
watch global_var                    # 变量被写入时停下，揪出谁偷改了它
watch -l *ptr                       # 监视某个内存地址（按位置不按变量）
rwatch var                          # 变量被读取时停
info watchpoints                    # 列出所有观察点
```

## 反汇编
```bash
disas / disassemble func            # 反汇编整个函数
disas $pc,$pc+32                    # 反汇编当前位置往后 32 字节
set disassembly-flavor intel        # 用 Intel 汇编语法（更易读）
display/i $pc                       # 每步自动显示当前指令
layout asm                          # 切到汇编窗口（TUI）
layout src                          # 切回源码窗口
```

## core dump 分析（程序已崩、人已离场）
```bash
ulimit -c unlimited                 # 先允许系统生成 core 文件
gdb ./a.out core                    # 用 core 文件调试
gdb -c core                         # 只有 core，自动找程序
bt full                             # 复现崩溃现场
# core 文件找不到？看路径：
cat /proc/sys/kernel/core_pattern
# 大发行版常被 apport/abrt 接管，临时直出：
sudo sysctl -w kernel.core_pattern=core
```

## 改变运行状态（边调边改）
```bash
set var x = 5                       # 直接改变量值继续跑
set args arg1 arg2                  # 设置程序参数，下次 run 生效
set environment KEY=value           # 设置环境变量
jump 100                            # 跳到第 100 行执行（危险）
return                              # 强制从当前函数返回
```

## 反复跑 / 自动化
```bash
set pagination off                  # 关掉分页确认，跑长任务用
commands 1                          # 给 1 号断点绑一组自动执行的命令
> print *node
> continue
> end
gdb -batch -ex "run" -ex "bt" ./a.out   # 一行命令跑完打印栈，CI 用
```
