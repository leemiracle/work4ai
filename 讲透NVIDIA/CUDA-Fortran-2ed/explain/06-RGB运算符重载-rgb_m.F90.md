# 06 RGB 运算符重载：rgb_m.F90——一个模块名二选一的跨端类型库

## 角色定位

`code/ch12/rgb_m.F90` 是终章光线追踪器的数学底座：定义 `rgb` 颜色派生类型并重载 `=`、`*`、`/`、`+`、`-` 共 17 个过程，让着色代码能写 `color1*color2 + t*[0.5,0.7,1.0]` 这样的自然表达式。它是全仓"单源双编译"最彻底的实现——文件头用 `#ifdef _CUDA` 在 `rgbCUDA` 与 `rgbHost` 两个模块名之间二选一（rgb_m.F90:1-6），同一源码编出 host/device 两套模块对象，ch12 全部 15 个渲染器按编译开关 `use` 对应版本。同时它也是本仓最值得细读的甄别案例：重载表里潜伏着两个"名字与语义相反"的可疑实现。

## 内部结构

类型定义极简：`type rgb` 内一个 `real :: v(3)`（rgb_m.F90:8-10）。重载界面四张：`assignment (=)` 聚合 rgbEqR3/r3EqRgb 两个赋值（rgb_m.F90:12-14）；`operator(*)` 五个过程覆盖 rgb×r3、r3×rgb、rgb×rgb、rgb×标量、标量×rgb（rgb_m.F90:16-19）；`operator(/)` 四个（rgb_m.F90:21-23）；`operator(+)` 与 `operator(-)` 各三个（rgb_m.F90:25-31）。每个过程头上都有一行 `!@cuf attributes(device) &`（如 rgb_m.F90:35-36）——`&` 续行把设备属性挂到下一行的过程声明上，`-cuda` 编译时全表变成 device 函数，纯宿主编译时又全退化为普通过程。所有算术函数的返回值都是裸 `real(4) :: res(3)` 而非 `type(rgb)`（如 rgb_m.F90:53、68），rgb 类型只在赋值两端出现。

## 外部连接

消费方模式高度一致：`ray.F90` 头部 `#ifdef _CUDA use rgbCUDA #else use rgbHost`（ray.F90:2-6）；着色函数返回 `type(rgb) :: res` 并用结构构造器 `res = rgb((1.0-t)*[1.0,1.0,1.0] + t*[0.5,0.7,1.0])`（ray.F90:45-48）——混合表达式里 rgb 与 real(3) 自由运算全靠本模块的重载表。构建侧 `ch12/Makefile` 把同一源码编两次：`rgb_m.host.o` 纯 nvfortran、`rgb_m.cuda.o` 加 `$(MCUDA)`（ch12/Makefile:30-34，MCUDA=-cuda 在第 1 行），rayHost/rayCUDA 各链各的（ch12/Makefile:38、41）。ch12 其余 14 个渲染器（sphere/metal/dielectric/texture……到 870 行的 texture.F90）全部沿用这对对象与这套 use 开关。

## 数据流

运行时数据流是"像素帧缓冲":渲染 kernel 写 `type(rgb) :: fb(nx,ny)`（ray.F90:54、67），主程序把它逐像素 `int(255*fb(i,j)%v)` 转 PPM 文本（ray.F90:124-127）。本模块内部的数据流则全是逐分量向量运算：每个函数体一行数组表达式，如 `res = rgbin%v * rin`（rgb_m.F90:54）或 `res = rgb1%v + rgb2%v`（rgb_m.F90:139）。`assignment(=)` 两个方向（rgb←r3 与 r3←rgb，rgb_m.F90:12-14）承担类型边界转换，使得着色链路中 real(3) 中间结果随时能升回 rgb 存帧。

## 设计决策

模块名二选一是不得已的工程妙招：同源模块若同名，host 与 `-cuda` 两次编译会产生两份同名 .mod 互相覆盖；改名 rgbCUDA/rgbHost 让两套对象共存，消费方用同一个 `#ifdef` 选取——这是 ch12 全章 15 个文件反复出现的固定开场。设备化用 `!@cuf attributes(device) &`（rgb_m.F90:35-36）而非拆两个文件，保持 17 个过程只写一遍。返回裸 real(3)（rgb_m.F90:53）是性能取向：派生类型构造在 kernel 内有成本，中间值留在基本类型上更轻。**甄别警示**：`r3DivRgb` 名义是 r3/rgb，函数体却是 `res = rgbin%v / rin`（rgb_m.F90:105-109），实际算 rgb/r3；`r3MinusRgb` 同病，`res = rgbin%v - rin`（rgb_m.F90:151-155）实际算 rgb−r3——除法与减法不可交换，语义与名字相反，疑为从 rgbDivR3/rgbMinusR3 复制粘贴后忘改；乘法/加法版的同款写法（rgb_m.F90:58-63、127-133）因可交换而无恙。全 ch12 grep 无任何调用方走 r3 在前的 `/` 或 `-` 表达式，故这个潜在 bug 在书内构建中永不触发——但复用本模块的人容易踩中。

## 新人提示

把这 17 个过程当 Fortran 运算符重载的字汇表读：`interface operator(*)` 里同名异型过程按**操作数类型**分发（rgb_m.F90:16-19），写 `rgb*5.0` 与 `5.0*rgb` 都合法但走不同函数。复用 rgb_m 先自查：任何 r3 在前的除/减表达式都会踩 rgb_m.F90:109、155 的反转语义；过程内 real(4) 显式 kind（rgb_m.F90:38）勿与调用方默认 real 混用。`!@cuf attributes(device) &` 的续行符 `&` 不能省（rgb_m.F90:35），断行后属性与声明分离会静默退化成宿主函数——编译能过、链接时才发现 kernel 里调不到。宏 `_CUDA` 由 `-cuda` 编译隐式定义，与 ch06 的 `#ifdef _CUDA`（portingDeviceSent.F90:22）是同一开关的全仓约定。
