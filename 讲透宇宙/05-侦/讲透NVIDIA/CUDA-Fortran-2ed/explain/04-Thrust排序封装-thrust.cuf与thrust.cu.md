# 04 Thrust 排序封装：thrust.cuf + thrust.cu——把 C++ 模板库搬进 Fortran

## 角色定位

`code/ch07/thrust.cuf` 与配套的 `code/ch07/thrust.cu` 共同演示 ch07 的核心命题：CUDA Fortran 程序不必手写一切，C++ 生态（Thrust、cuBLAS、cuSPARSE……）都能接入。Thrust 是 C++ 模板库，符号无法直接跨语言链接，这对文件给出标准解法——C++ 侧用 `extern "C"` 导出定型包装函数，Fortran 侧用 `bind(C)` 接口 + 泛型界面把它包装回"像 Fortran 子程序"的形态；23 行的 thrust.cuf 示范的正是这条复用任何 C++ GPU 库的通用通道。

## 内部结构

`thrust.cuf` 的 `module thrust`（thrust.cuf:1）内是泛型界面 `interface thrustsort`（thrust.cuf:3），聚合三个绑定不同 C 符号的实现：`sort_int` 绑 `sort_int_wrapper`（thrust.cuf:4）、`sort_float` 绑 `sort_float_wrapper`（thrust.cuf:10）、`sort_double` 绑 `sort_double_wrapper`（thrust.cuf:16）。接口体全走 ISO_C_BINDING：设备形参 `integer(c_int), device :: input(*)`（thrust.cuf:6）、长度 `integer(c_int), value :: N`（thrust.cuf:7）。C++ 侧 `extern "C"` 块（thrust.cu:5-27）里三个包装同构：`thrust::device_ptr<int> dev_ptr(data)` 把裸指针包成 Thrust 迭代器（thrust.cu:9）、`thrust::sort(dev_ptr, dev_ptr+N)` 原地排序（thrust.cu:11），头文件引 device_vector/sort（thrust.cu:1-2）。

## 外部连接

消费方 `code/ch07/testSort.cuf` 是三行核心：`use thrust`（testSort.cuf:2）后，`gpuData=cpuData` 上行（testSort.cuf:13），`call thrustsort(gpuData, size(gpuData))` 一句完成排序（testSort.cuf:14）——实参是 `real, device` 数组，编译器按类型自动分发到 sort_float，`cpuData=gpuData` 拷回（testSort.cuf:15）。构建链在 ch07/Makefile：nvcc 以 `-arch=sm_75` 编出 thrust.C.o（ch07/Makefile:66-67），nvfortran 链三件并挂 `-gpu=cc75 -c++libs`（ch07/Makefile:69-70）；注释明说 Ubuntu 20.04 链接 C++ 运行时必需 `-c++libs`（ch07/Makefile:9）。同章 `callingC.cuf` 是互操作的另一极：直接给 C kernel 绑 Fortran 界面并用 `<<<1,1>>>` 启动（callingC.cuf:3-5、39），其 C 侧编译还要 `-rdc=true`（ch07/Makefile:12）支持设备端跨编译单元调用。

## 数据流

数据全程留在显存：宿主 `cpuData` 随机填充并埋哨兵 `cpuData(5)=100.`（testSort.cuf:8-9）→ 显式赋值进设备数组 gpuData（testSort.cuf:13）→ thrustsort 收到的是**裸设备指针**，Fortran 编译器把 `real, device :: input(*)` 直接按地址传给 C → Thrust 在设备端排序 → 拷回宿主验证（testSort.cuf:15-17）。这条链上没有隐藏的主存中转：`device_ptr` 只是指针包装不是容器拷贝（thrust.cu:9），这正是该模式高效的关键。N 用 `value` 传值（thrust.cuf:7）与 C 按值语义对齐，避免引用传参踩到指针语义。

## 设计决策

Fortran 泛型 `interface thrustsort` 是对 C++ 模板的**手工实例化镜像**：C++ 靠模板生成 int/float/double 三版，跨语言后被 extern "C" 定死为三个具体符号，Fortran 侧只能用泛型界面把"类型重载"体验拼回来（thrust.cuf:3-21）——这是跨语言边界的通用税。包装函数只做指针包装不搬运数据（thrust.cu:9-11），把传输决策权留给调用方。所有形参显式用 `c_int`/`c_float`/`c_double`（thrust.cuf:6、12、18）而非默认整型实型，是可移植性的纪律：C 端类型宽度固定，Fortran 默认 kind 因编译器而异。`bind(C, name="sort_int_wrapper")`（thrust.cuf:4）显式钉死符号名，免受名称修饰规则差异影响。

## 新人提示

这个 interface 没有声明 `attributes(global)`——thrustsort 是普通宿主过程（内部由 Thrust 启动它自己的 kernel），与 callingC.cuf:3 的"绑 C kernel 再 <<<>>> 启动"是两条不同通路，别混用。新增类型支持要三处同步：thrust.cu 加 wrapper、thrust.cuf 加接口体、interface 聚合表加名（thrust.cuf:3-21），漏一处是链接错误而非运行错误。数组从 `input(1)` 起传——Fortran 设备数组地址与 C 指针直接对应，没有下标偏移换算。链接报错先查 nvcc/nvfortran 架构参数是否一致（ch07/Makefile:5-6：sm_75 与 cc75 是同一代两种写法）。
