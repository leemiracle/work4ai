# 01 起步链路：increment.cuf——把一个 do 循环送上 GPU

## 角色定位

`code/ch01/increment.cuf` 是全书第一颗完整 kernel，也是本仓"CPU 基线 vs GPU 版"教学法的起点：它与纯 CPU 的 `code/ch01/increment.f90` 逐行对照，把一个 `do` 循环改写 GPU 所需的**全部**改动浓缩在 36 行里——`attributes(global)` 标注、设备数组、显式拷入拷回、`<<<>>>` 启动。后续 ch01 的 multiblock/multidim 只是把同一骨架往"多块网格"和"二维网格"推广，ch06 的移植方法论则反向引用它作为改动量参照。看懂这一对文件，等于拿到全仓 300 多个示例的公共骨架。

## 内部结构

文件两段式。`module m`（increment.cuf:1-13）内是 kernel 本体：`attributes(global) subroutine increment(a, b)`（increment.cuf:3）声明设备程序；形参 `integer, intent(inout) :: a(*)` 用假定大小数组（increment.cuf:5），标量 `integer, value :: b` 必须加 `value`（increment.cuf:6）。函数体只有两行：`i = threadIdx%x`（increment.cuf:9）取线程号，`a(i) = a(i)+b`（increment.cuf:10）做增量。`program incrementGPU`（increment.cuf:16-36）是宿主侧：`use cudafor`（increment.cuf:17）引入 CUDA Fortran 环境，`integer, device :: a_d(n)`（increment.cuf:22）声明设备镜像，n=256（increment.cuf:20）。

## 外部连接

对照基线 `increment.f90`：CPU 版是普通 `subroutine increment(a, b)`（increment.f90:3），形参可用假定形状 `a(:)`（increment.f90:5），循环体 `do i = 1, n`（increment.f90:10-12）由 `size(a)`（increment.f90:9）取界。两版差异恰是 CUDA Fortran 的最小语法集。推广链上，`code/ch01/multiblock.cuf` 把单块改成全局线性索引 `blockDim%x*(blockIdx%x-1)+threadIdx%x`（multiblock.cuf:9）并加越界守卫 `if (i <= n)`（multiblock.cuf:10），启动配置换成 `(n-1)/tPB+1` 块（multiblock.cuf:30）；`code/ch01/multidim.cuf` 再用 `dim3` 表达二维网格（multidim.cuf:29-31）。构建侧 `code/ch01/Makefile` 用两条单命令规则分别产出 incrementf90/incrementcuf（ch01/Makefile:10-14）。

## 数据流

数据流是一条最短的 H2D→kernel→D2H 闭环：宿主初始化 `a = 1; b = 3`（increment.cuf:24-25）→ `a_d = a` 上行拷贝（increment.cuf:27）→ `call increment<<<1,n>>>(a_d, b)` 启动一个 256 线程的块（increment.cuf:28）→ `a = a_d` 下行拷回（increment.cuf:29）→ `any(a /= 4)` 校验（increment.cuf:31）。CUDA Fortran 的数组赋值语句自带隐式同步：拷回完成时 kernel 必已结束，所以不需要手写 `cudaDeviceSynchronize`。n=256 恰等于块大小，`threadIdx%x`（increment.cuf:9）不需要守卫——这正是 multiblock 版才引入 `if (i <= n)` 的原因。

## 设计决策

其一，kernel 装进 `module` 而非裸过程：Fortran 调用带 `<<<>>>` 的程序要求显式接口，module 自动提供。其二，标量形参加 `value`（increment.cuf:6）：Fortran 默认引用传参，而 kernel 标量必须按值传，这是 C 端习惯与 Fortran 默认的正面碰撞点。其三，kernel 形参用 `a(*)` 而非基线版的 `a(:)`（increment.f90:5）：假定形状数组依赖宿主侧数组描述符，设备代码不支持，本仓全部 kernel 都遵循 `a(*)` 或显式定界（如 multidim.cuf:5 的 `a(n1,n2)`）。其四，`module m` 本身不 `use cudafor`（increment.cuf:1-13），只有 program 才需要（increment.cuf:17）——kernel 语法 `attributes(global)` 是编译器内建识别，不依赖模块。

## 新人提示

`threadIdx%x` 从 1 开始计数，与 Fortran 数组下标天然对齐——从 CUDA C 移植公式时务必去掉 `-1` 偏移（multiblock.cuf:9 的索引式是与 C 版逐项对照的范本）。`<<<1,n>>>` 的块大小上限是 1024，超出即走 multiblock.cuf:30 的网格公式。改动任何示例后先盯输出：`'**** Program Failed ****'`（increment.cuf:32）是全仓统一的失败哨兵。记住 ch01/Makefile:13-14 的隐含信息：`.cuf` 后缀让 nvfortran 自动进入 CUDA Fortran 模式，无需额外开关。
