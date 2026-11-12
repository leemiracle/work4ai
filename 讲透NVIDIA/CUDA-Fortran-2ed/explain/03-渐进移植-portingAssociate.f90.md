# 03 渐进移植：portingAssociate.f90——associate 让宿主代码零改动上 GPU

## 角色定位

`code/ch06/portingAssociate.f90` 是 ch06"存量 Fortran 代码 GPU 化"方法论中最优雅的一站：以 `associate` 结构把宿主数组名透明地别名到设备数组，使原始 CPU 代码的循环体**一字不改**地被 `!$cuf kernel do` 送上 GPU。它所在的 porting 家族从 `portingBase.f90` 纯 CPU 基线出发，经 managed、device 镜像、条件指令多条路径渐进演化，全部保持"单源双跑"——同一份源码既可纯 CPU 编译也可 `-cuda` 编译。这一章的每个文件都极短（19-33 行），价值不在代码量而在**改动量对比**。

## 内部结构

文件只有 26 行。骨架完全沿用 `portingBase.f90` 的两段赋值循环（portingBase.f90:7-13）：先 `a(i) = i+1`，再 `b(i) = a(i)+1`。GPU 注入点全在指令行：`!@cuf real, device :: a_d(n), b_d(n)`（portingAssociate.f90:6）声明设备镜像；`!@cuf associate(a => a_d)`（portingAssociate.f90:9）把宿主名 a 别名到 a_d，紧随的 `!$cuf kernel do`（portingAssociate.f90:10）把 do 循环编译成 kernel；b 循环同样嵌套一层 associate（portingAssociate.f90:14-15）；最后按开括号逆序 `!@cuf end associate`（portingAssociate.f90:19-20）并用 `!@cuf a = a_d; b = b_d`（portingAssociate.f90:21）拷回。两种哨兵分工明确：`!@cuf` 后接的**那一行**代码只在 `-cuda` 模式编译，`!$cuf kernel do` 是循环级 kernel 化指令——无 `-cuda` 时两者都退化成普通注释。

## 外部连接

家族其余成员提供对照面：`portingManagedSent.f90` 走托管路径，`!@cuf attributes(managed) :: a, b`（portingManagedSent.f90:6）让同一数组名 CPU/GPU 通吃，只需 `!@cuf i = cudaDeviceSynchronize()`（portingManagedSent.f90:19）等设备完成；`portingDeviceSent.F90` 走设备镜像+宿主副本路径（portingDeviceSent.F90:5-6），打印段用 `#ifdef _CUDA` 二选一（portingDeviceSent.F90:22-28）；原生 `.cuf` 版 `portingManaged.cuf` 最短（portingManaged.cuf:5 的 `real, managed`）。构建规则见证"单源双跑"：`portingAssociate_HOST` 纯 nvfortran、`portingAssociate_CUDA` 加 `-cuda`（ch06/Makefile:62-66），同一 .f90 源产出两个可执行文件。规模化验证在 `laplace2DUse.F90`——同一手法落到 4096² Jacobi 迭代，`module arrays` 里用 `!@cuf` 声明设备镜像（laplace2DUse.F90:12-14）。

## 数据流

CPU 视角的数据流与基线完全一致：a 先填 1..8，b 再填 a+1，最后 `print *, a; print *, b`（portingAssociate.f90:24-25）。GPU 视角发生了三段替换：a 的写入经别名落进 a_d（kernel 1）；b 的计算读 a_d 写 b_d（kernel 2）——两个 kernel 间的依赖由 CUDA Fortran 在同一默认流上的顺序执行保证；结果在 print 前由 portingAssociate.f90:21 显式拷回宿主。注意 associate 块必须覆盖 kernel do 的作用域：a 的别名要一直开到 b 循环结束（portingAssociate.f90:9-20），因为第二个 kernel 仍通过别名读 a。

## 设计决策

三条路径的本质是"谁替你搬数据"的三个答案：managed 让运行时按页迁移（免拷回，代价是首次触页延迟）；device 镜像保留显式控制（拷入拷回全手写）；associate 是 device 镜像的语法糖——语义同 device 镜像，但宿主代码文本零改动，代码评审时 diff 最干净。选择 `.f90` 后缀 + `!@cuf`/`#ifdef` 而非 `.cuf`，是为了让非 CUDA 工具链（其他编译器、静态分析）也能编译同一份源码。`!@cuf` 与 `#ifdef _CUDA` 的分工在 portingDeviceSent.F90 中同框出现（指令管声明、宏管预处理器段落），提示两者机制层级不同：前者是编译器行级开关，后者是预处理替换。

## 新人提示

`!@cuf` 行尾不能再写别的语句——它只豁免紧跟的那一行（portingAssociate.f90:21 用分号把两条拷贝挤进同一行才都被激活）。associate 的结束顺序必须与开启顺序严格逆序（portingAssociate.f90:19-20 注释都标了对应关系），交叉关闭编译不过。kernel do 的循环体必须无外部依赖（不能引用循环外的可变宿主变量），这就是为什么本例第二个循环只能读 a_d 不能读宿主 a。跑 `make portingAssociate_HOST` 与 `_CUDA` 各一次，对比两组 print 与 'GPU run' 标记行（portingAssociate.f90:23）——单源双跑的正确性验收就是这两份输出一致。
