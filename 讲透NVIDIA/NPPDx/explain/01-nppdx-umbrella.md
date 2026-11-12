# 01 · nppdx 伞头与入口值类型层：一个为"三编译世界"设计的零依赖门面

> 涉及文件：`include/nppdx.hpp`、`include/nppdx/nppdx.hpp`、`include/nppdx/types.hpp`、`include/nppdx/utils.hpp`、`include/nppdx/detail/config.hpp`、`include/nppdx/detail/decl.hpp`（commit e7efdc12）

## 一、角色定位

NPPDx 是 NVIDIA 性能原语库 NPP 的下一代实验形态：头文件_only 的 C++ 模板库，把图像处理表达成"算子表达式"在编译期组装。整个库对外只暴露一个入口 `#include <nppdx.hpp>`——图谱中该节点 fanIn=22、fanOut=1，是全库被消费最多的头。

这个入口层的设计张力在于：NPPDx 的代码必须同时活在三个编译世界里——普通 host 编译器（MSVC/GCC/Clang host pass）、nvcc device pass、以及 NVRTC 运行时编译（`__CUDACC_RTC__`，无完整 libstdc++，只能用 libcu++ 的 `cuda::std`）。入口值类型层（图谱 L06 层，9 个文件）就是为此打造的"地基中的地基"：它不依赖任何 CUDA 运行时头，甚至连 `uint8_t` 都要经宏垫片引入。

双层伞头结构：外层 `include/nppdx.hpp`（24 行）只做一件事——`#include "nppdx/nppdx.hpp"`（nppdx.hpp:22）；内层 `include/nppdx/nppdx.hpp` 才是真聚合器，按序包含 10 个头（nppdx/nppdx.hpp:21-31）。外层存在的意义是安装布局：用户写 `<nppdx.hpp>`，库内部相对包含活在 `nppdx/` 子目录下，两种写法都成立。

## 二、内部结构

**伞头聚合（include/nppdx/nppdx.hpp:21-31）**：包含顺序有讲究——`config.hpp` 必须最先（定义 `NPPDX_STD` 命名空间别名与整套 `NPPDX_STD_INCLUDE_*` 头选择宏），`operators.hpp` 与 `traits.hpp` 随后（DSL 主体），`types.hpp` 反而排在后面，说明值类型对算子层无前向依赖压力。

**config.hpp（84 行，图谱枢纽 fanIn=27）**：核心是 L25-27 的判定 `#ifdef __CUDACC_RTC__ → NPPDX_DETAIL_USE_CUDA_STL`，以及 L31/L46 的二分：NVRTC 下 `NPPDX_STD` = `::cuda::std`、标准头全部映射到 `<cuda/std/...>`（L32-44）；否则 `::std` + 普通标准头。第三个世界藏在 L47-65：定义 `NPPDX_CLANG_CUDA_COMPAT` 时，algorithm/cmath/cstdlib 三个最常出问题的头被改道到 `nppdx/detail/clang_cuda_compat/` 自带垫片（供 clang 编 CUDA 的场景，如 example/nppdx/clang_ptx/）。L76-80 再给出 `NPPDX_HOST_DEVICE_FORCEINLINE_FUNC` 的条件定义。

**decl.hpp（243 行，fanIn=25）**：声明修饰符速记宏表。助记字母顺序固定为 N（`[[nodiscard]]`）S（static）C（constexpr）E（explicit）I/F（inline/`__forceinline__`）H（`__host__`）D（`__device__`），组合出从 `NPPDX_DECL_D`（decl.hpp:49）到 `NPPDX_DECL_NSCEFHD`（decl.hpp:239）的全排列。decl.hpp:21-24 注释道明动机：原型期写全修饰符太啰嗦容易被省略，导致微妙 bug——干脆把"好习惯"压缩成 8 个字母的 DSL。

**types.hpp（255 行）**：四个主角——
- `Array<T, Size>`（types.hpp:30-69）：按值传数组的薄包装，`get()` 在 Size==1 时退引用返回标量（L34-42 宏），`transform`/`cast` 提供逐元素映射（L50-63）；
- `ImageLayout<T, PlaneCount>`（L78-86）：多平面图像的"指针+行距"对，刻意不含尺寸（L76-77 注释），`element_strides()` 把字节步距换算成元素步距（L83-85）；
- `TexObjT`/`SurfObjT`（L116-117）：直接 `using ... = unsigned long long`，L101 注释明说是为了不引入 `<cuda_runtime.h>`（FFmpeg 兼容）；`TexObjPlanes<NumPlanes>`/`SurfObjPlanes`（L122-125）按平面数打包成 Array；
- `vec2<T>`（L139-204）：二维向量全套，运算符全部经 hidden-friend 宏生成（L178-199），算术运算返回 `vec2<T>`、逻辑运算返回 `vec2<bool>`（L183-184 两个派生宏）。另有 `tp::Vec2D`（L220-228）把 2D 值搬进非类型模板参数，`Int2D`/`UInt2D`（L241-251）与 `NPPDX_MAKE_INT2D` 宏是其门面。

**utils.hpp（313 行）**：`ceil_div`（utils.hpp:59-65，注释解释为何不用 `(a+b-1)/b`：让编译器在同时需要商和余数时优化更好）；有向商余 `dir_quot`/`dir_rem`（L78-131，保证负被除数侧也满足 0<=r<d 的欧几里得式语义）；`CVal<Val>`/`C<Val>` 编译期-运行期统一载体（L153-191，L138-151 长注释明说这是 C++20 concept 出现前的替代品）；三平台 `fatal_error`（L193-205，device 走 `__trap()`、host 有异常时 throw、否则 terminate）；`copy()`（L268-271）与 tagged_type（L278-297）。

## 三、外部连接

伞头之下是严格的单向依赖漏斗：`nppdx.hpp`(外) → `nppdx/nppdx.hpp`(内) → `config.hpp` → `commondx/detail/config.hpp`（commondx 是 NPP 家族共享的"公共 DX"基座库，版权注释可佐证血统：commondx 侧 2020-2024、nppdx 侧 2025-2026，见 expressions.hpp:2 与 nppdx/nppdx.hpp:2）。`decl.hpp`（fanIn=25）与 `config.hpp`（fanIn=27）是全库被包含最多的两个基础件。`types.hpp` fanIn=14/fanOut=9，被数据库层的 cell/region 计算与纹理后端同时消费；`utils.hpp` 的 `dir_quot`/`ceil_div` 家族被 resize 几何、tile 划分等所有需要"负坐标取整方向"的模块引用。外部世界对这一层的引用几乎只有一条路径：`#include <nppdx.hpp>`（example 侧经 common.hpp 条件引入，NVRTC 模式下由 common_nvrtc.hpp 预定义宏接管）。

## 四、数据流

这一层没有运行时数据流，流通的是**类型与编译期值**：

1. **编译环境探测**：`__CUDACC_RTC__`/`__CUDACC__`/`NPPDX_CLANG_CUDA_COMPAT` 三个宏进入 `config.hpp`，输出 `NPPDX_STD` 别名与 `NPPDX_STD_INCLUDE_*` 宏集 → 全库所有标准库引用都经这套宏间接寻址（如 types.hpp:25-26）。
2. **修饰符展开**：源码里的 `NPPDX_DECL_NCFHD` 在预处理期展开为 `[[nodiscard]] constexpr __forceinline__ __host__ __device__`，成为每个函数签名的统一前缀。
3. **值类型实例化**：用户与库代码用 `vec2<int>` 做坐标运算（hidden-friend 运算符全内联）、用 `ImageLayout` 描述外部图像内存、用 `TexObjPlanes<2>` 携带 NV12 双平面纹理句柄进入执行层。
4. **编译期值升格**：运行期 `vec2` 经 `NPPDX_MAKE_INT2D(v)`（types.hpp:245）变成 `Int2D<v.x, v.y>` 编译期值，作为非类型模板参数驱动算子特化选择——这是入口层通往算子 DSL 的桥。

## 五、设计决策

- **为什么纹理句柄用裸 `unsigned long long`？** types.hpp:99-115 的注释链给了完整答案：避免 `<cuda_runtime.h>` 依赖（FFmpeg 兼容），且调用方自建纹理/表面对象、库不检查不重配——配置错了会**静默产出错误结果**而非报错（L107 明示）。「勘误」直觉：`TexObjT` 与 `SurfObjT` 是同一底层类型，重载消歧靠 ingest/exgest 的**操作方向**而非句柄类型（L102-103），别指望类型系统能帮你区分读写。
- **decl.hpp 是"反娇气"设计**：修饰符组合表按固定顺序生成（decl.hpp:29-38），杜绝了 `__host__ __device__` 顺序/遗漏导致的跨编译器兼容问题。代价是可读性下降——新人必须先背 8 个助记字母。
- **`copy()` 不是多余**：utils.hpp:260-267 注释列出它压制的两个真实编译器缺陷——GCC 9.4-13.4 对非类型模板参数来源变量的错误 constexpr 抱怨，以及 `static constexpr` 在 device 函数中被引用取址时无符号生成的问题。types.hpp:237 的 `NPPDX_MAKE_TP_VEC2D` 宏就是第一个缺陷的现场 workaround。
- **`ceil_div` 写成 `a/b + (a%b!=0)`**：utils.hpp:60-63 注释言明是为了让"商余同时需要"的常见场景共享一次除法优化，比经典 `(a+b-1)/b` 更优。

## 六、新人提示

1. **加新公共头时**：必须挂进 `include/nppdx/nppdx.hpp` 的聚合列表（而非外层 nppdx.hpp），并保持 config → operators → traits → types → detail 的顺序惯例；`detail/` 下的头不应被用户直接包含。
2. **别在这层引入任何 CUDA 头**：types.hpp/utils.hpp 能在 NVRTC 里活，靠的就是零 CUDA 依赖。需要标准库时一律走 `NPPDX_STD_INCLUDE_*` 宏（参考 types.hpp:25-26 的写法），直接写 `<cstdint>` 会在 NVRTC 构建里炸。
3. **用 min/max 请走 `nppdx_min`/`nppdx_max`**（utils.hpp:36-56）：它们按 `__CUDA_ARCH__` 与 clang-compat 三路分派，裸 `std::min` 在 device 侧不可用。
4. **新函数修饰符直接查 decl.hpp 助记表**，不要手写全称——与全库风格一致性本身就是这里的防御手段。
5. **`vec2` 逻辑运算符返回 `vec2<bool>` 不是 `bool`**（types.hpp:184），配 `all()`/`any()` 归约（L208-213）；把 `a < b` 直接当条件用会编译失败，这是刻意为之。

