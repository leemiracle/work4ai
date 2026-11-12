# 06 · mdl_types.h 与 imatrix.h —— 公共 API 的双面貌：mi::mdl 编译器内部 vs mi::neuraylib 集成者

> 文件：`include/mi/mdl/mdl_types.h`（1079 行，MDL 类型系统 IR）+ `include/mi/neuraylib/imatrix.h`（1051 行，DB 矩阵数据类型）
> 主题：同一套 `include/mi/` 目录下两个世界的分界。

## 1. 角色定位

MDL SDK 的公共头文件按受众劈成两半：`mi/mdl/` 面向**编译器工具作者**（实现新后端、mdltlc 规则编译器、模块分析器），暴露的是编译器内部 IR——语义完备但概念众多；`mi/neuraylib/` 面向**渲染应用集成者**（DF 类 app），暴露的是 DB/transaction 范型的数据容器——概念少、全 COM 风格。本篇两个文件各是一侧的典型样本：mdl_types.h 是 MDL 类型系统的完整 IR 接口（编译器一切类型判断的公共语言）；imatrix.h 是 36 个矩阵"数据类型"接口（IDatabase 里存取矩阵值的容器）。两者的"类型"一词含义完全不同：前者是**材质语言的类型系统**，后者是**API 数据容器的类型**。

## 2. 内部结构

**mdl_types.h（mi::mdl）**：

- 根接口 `class IType : public Interface_owned`（L45）：注意基类不是普通 IInterface，而是 `Interface_owned`（来自 mdl_iowned.h）——MDL 编译器所有 IR 对象带 owner 概念，类型属于创建它的编译单元/模块，这是类型唯一化（structural typing）的前提。
- `Kind` 枚举（L49-77）：TK_ALIAS/TK_ERROR/TK_VOID/TK_PTR/TK_REF/TK_AUTO/TK_BOOL/TK_INT/TK_ENUM/TK_FLOAT/TK_DOUBLE/TK_STRING/TK_BSDF/TK_HAIR_BSDF/TK_EDF/TK_VDF/TK_VECTOR/TK_MATRIX/TK_ARRAY/TK_COLOR/TK_SPECTRAL_SAMPLE/TK_SPECTRUM/TK_FUNCTION/TK_STRUCT...——一个枚举装下整个类型宇宙，每个具体类带 `static Kind const s_kind`（如 IType_bool L201）。
- `Modifier` 枚举（L80）与 `skip_type_alias()`（L98-102，const/非 const 双版本）：alias 链穿透，是全编译器使用频率最高的方法之一。
- 三大子树的骨架：**atomic**（IType_atomic L192 派生 bool L197/int L205/float L288/double L296/string L304/enum L213——enum 的 `Predefined_id`（L217-222）含 EID_USER=-1、EID_TEX_GAMMA_MODE=0、EID_INTENSITY_MODE=1，预定义枚举与用户枚举同表区分）；**reference**（IType_reference L314 → df 家族 IType_bsdf L324/IType_hair_bsdf L332/IType_edf L340/IType_vdf L348 + resource 家族 IType_resource L581 → light_profile L586/texture L594/bsdf_measurement L617，texture 自带 Shape 枚举）；**compound**（IType_compound L356 → vector L369/matrix L383/array L408/color L428/spectral_sample L439/spectrum L450/struct L503）。
- 编译期专属概念：`IType_error`（L132，错误恢复占位）、`IType_auto`（L184，未推导类型）、`IType_alias`（L112，带 modifier 的包装）、`IType_array_size`（L397）+ deferred sized array（IType_array 的 `get_deferred_size`）——数组长度可以是"另一参数的名字"，这是第 1/3 篇 Type_binder 绑定机制的存在理由。
- `IType_struct`（L503）与 `IStruct_category`（L485）：MDL 1.9 引入 struct category，struct 声明必须挂 category。
- 工厂 `IType_factory`（L856）：create_alias（L861）/create_error/create_bool/.../create_enum（L882）全家桶 + **lookup_enum（L896）**——create 与 lookup 并存说明类型经工厂唯一化（同名枚举返回同一实例），结构等价类型可用指针比较。

**imatrix.h（mi::neuraylib）**：

- 36 个接口：Boolean/Sint32/Float32/Float64 × 2_2/2_3/2_4/3_2/3_3/3_4/4_2/4_3/4_4——首段 `IBoolean_2_2`（L49）到尾部 `IFloat64_4_4`（L1028），全部同构：继承 mi::base 的 Interface_declare 体系，只提供 `get_value()/get_value(T&)` 双 overload + `set_value(const T&)`（如 L56-62）。
- 值载体是 `Boolean_2_2_struct` 等普通结构体（typedefs.h 定义，数学上等同 mi::math::Matrix）——接口只搬数据零运算。
- 文件属 `\addtogroup mi_neuray_compounds`（L45-47 文档组），与 ivector.h/icolor.h 构成 compound 类型族。

## 3. 外部连接

mdl_types.h 的消费者横跨编译器全域：compilercore 的 compilercore_tools.h/compilercore_type_cache.h/compilercore_overload.h、generator_code/generator_dag、distiller 等都以它为类型语言（grep 实证 5+ 处直接 include）。imatrix.h 消费者集中在数据层与 API 层：`src/base/data/idata/idata_compound_impl.h`（IData 实现基座）、`src/api/api/neuray/neuray_factory_impl.cpp`（类工厂注册 36 个矩阵类型）、测试 test_types_compound.cpp/test_ifactory.cpp。两文件在源码树中**零交集**——没有任何文件同时需要两套"类型"。

## 4. 数据流

mdl_types.h：编译期流动——parser 产 raw type → Analysis（第 1 篇 qualify_type L3416 等）施加 modifier/alias → IType_factory 唯一化实例 → def_table/DAG/后端全程用指针比较与 `skip_type_alias` 穿透；类型从不"求值"，只被匹配与打印。imatrix.h：运行期流动——用户 `transaction->create<mi::IFloat32_3_3>()`（经第 5 篇 neuray_factory_impl）→ set_value 填 `Float32_3_3_struct` → 存 DB → 表达式求值器按 IType_matrix 取值参与运算。一个活在编译流水线，一个活在 DB 会话。

## 5. 设计决策

- **两套类型系统而非一套**：把编译器 IR（含 error/auto/alias/deferred size）直接暴露给集成者会大幅抬高 API 学习成本；neuraylib 侧重造"傻瓜化"容器（create_deferred_sized_array 仍存在但语义被 API 层包装，见第 5 篇 Type_factory L655）。代价是第 5 篇整套 wrapper 与 ID 对照表的持续维护——经典的"内部干净 vs 边界厚"权衡。
- **IType_factory + lookup 唯一化**：类型实例全局共享使指针相等=类型相等，重载决议（第 1 篇 equal_types L9904）降为指针比较；对比每节点 new 类型对象的做法，省内存也省比较成本。
- **Interface_owned 基类**：类型带 owner 使模块卸载时可整批回收类型实例，避免跨模块悬垂——编译器长寿会话的关键设计。
- **imatrix 的结构体值语义 + 纯虚接口**：COM 风格 ABI 稳定（跨 DLL 边界安全），而数值运算交给 mi::math（同构但独立的头），容器与算法分离。
- **s_kind 静态常量**：每个类型类带编译期 Kind，模板元编程（cast<IType_function> 等）可零开销分派。

## 6. 新人提示

- 判断拿到的是哪套类型：include 路径 mi/mdl/ = 编译器侧，mi/neuraylib/ = 集成侧；mi::mdl::IType 与 mi::neuraylib::IType 是**两个不相关接口**，靠第 5 篇 Type_base wrapper 互转。
- 任何类型比较前先 `skip_type_alias()`（L98）——alias 可以层层包装；IType_error（L132）出现说明上游已报错，别再当真类型处理。
- deferred array（L397-427）是新手最大坑：数组尺寸是符号不是整数，须配合第 3 篇 Type_binder 的绑定结果使用。
- imatrix 的 36 个接口别手写 switch——用模板/宏生成（API 层 neuray_factory_impl.cpp 即如此消费）。
- 相关文件：mi/mdl/mdl_iowned.h（Interface_owned）、mi/neuraylib/itype.h（集成侧类型接口，imatrix 的姊妹）、mi/math/matrix.h（数学运算本体）、第 5 篇 neuray_type_impl.h（两世界的桥）。
