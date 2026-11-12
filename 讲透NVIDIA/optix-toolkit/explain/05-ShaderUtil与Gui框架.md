# 05 · ShaderUtil 与 Gui/OTKApp：设备侧算法库与宿主应用框架

## 角色定位

两个"公共件"库撑起全仓两半：**ShaderUtil**（`ShaderUtil/`，52 文件头文件库）是设备侧可复用算法集合，OptiX/CUDA kernel 直接 include 使用；**Gui/OTKAppBase/Testing**（`examples/Gui`、`examples/OTKAppBase`、`Testing/`）是宿主侧应用框架，让每个示例不必重写窗口/相机/管线样板。一半在 device，一半在 host，合起来是"写一个 OptiX 应用"的全部脚手架。

## 内部结构

**ShaderUtil**：数学底座 `ShaderUtil/include/OptiXToolkit/ShaderUtil/vec_math.h`（**5367 行全仓最大工具头**）自 `vec_math.h:42`（max）/`vec_math.h:47`（min）/`vec_math.h:52`/`vec_math.h:57`（long long 变体）起是 OTK_HOSTDEVICE 限定的 float2/3/4+矩阵完整运算库（clamp/dot/length/lerp/变换/四元数，500+ 函数 host/device 通用）。采样算法：`ShaderUtil/include/OptiXToolkit/ShaderUtil/AliasTable.h:26`（struct AliasRecord）+ `AliasTable.h:32`（struct AliasTable）——Walker 别名表，POD+函数族形态，host 构建表、device O(1) 重要度采样；`CdfInversionTable.h`/`PdfTable.h`（CDF 反演）、`Reservoir.h`。滤波与几何：`CubicFiltering.h`、`stochastic_filtering.h`、`ray_cone.h`（218 行光线锥全套——初始化三相机/传播/反射/折射/散射/曲率/纹理梯度推导）、`Transform4.h`/`color.h`/vec_printers。经典痛点自相交规避三实现：通用 `SelfIntersectionAvoidance.h`（45 行+`SelfIntersectionAvoidance/` 子目录）+`CudaSelfIntersectionAvoidance.h`+`OptixSelfIntersectionAvoidance.h` 按运行时选。配套 docs/ 五篇算法 README 与 tests/ 19 份一一对应。

**Gui**：`examples/Gui/include/OptiXToolkit/Gui/CUDAOutputBuffer.h:32`（class CUDAOutputBuffer<PIXEL_FORMAT>，350 行）多后端帧输出——`CUDAOutputBuffer.h:22`（enum CUDAOutputBufferType：GL 互操作/PBO/零拷贝/设备内存）、getPBO（`CUDAOutputBuffer.h:256`）/deletePBO（`CUDAOutputBuffer.h:317`）、`CUDAOutputBuffer.h:89` 注释明确 GL Interop 要求显示设备与计算设备同机；Window/GLDisplay/GLCheck 窗口链；Trackball/TrackballCamera/Camera 相机族；vendored glad/glfw3 头（`glfw3.h` 按构建开关选 vendored 或 FetchContent）。

**OTKAppBase**：`examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKApp.h`（162 行）约 45 方法基类——OptiX 管线+按需加载+相机+GUI+渲染循环完整骨架，RayCones/StochasticTextureFiltering/TexturePainting/NeuralTextureViewer 等多示例公共父类。**Testing**：`Testing/include/OptiXToolkit/Testing/MockOptix.h:44`（class MockOptix——OptiX C API mock+函数表替换，无 GPU/SDK 跑库测试）、`Matchers.h`/`OptixCompare.h`（浮点/向量/矩阵 gtest 比较器），被 DemandLoading/OmmBaking 测试复用。

## 外部连接

ShaderUtil 被 DemandLoading kernel（stochastic_filtering 配按需纹理）、DemandPbrtScene（ray_cone 推 LOD）、所有示例着色器 include；vec_math 是事实标准——改它等于动全仓 device 代码。Gui/OTKApp 被全部查看器示例依赖；Testing 是 CI 无 GPU 回归的关键（MockOptix 替换 OptiX 函数表）。`Memory/include/OptiXToolkit/Error/cudaErrorCheck.h`/`cuErrorCheck.h`/`optixErrorCheck.h`/`ErrorCheck.h` 四套错误检查宏是两个世界共用的错误处理惯例出处。Util 库（AssetLocator/EXRInputFile/ImageBuffer/Logger）补齐资产定位与日志。

## 数据流

Gui 侧一帧：CUDA kernel 渲染进 `examples/Gui/include/OptiXToolkit/Gui/CUDAOutputBuffer.h:32` 的多后端缓冲（`CUDAOutputBuffer.h:22` 四后端之一）→ GLDisplay 拿 texture/PBO 上屏 → ImGui（经 Gui.h 接口）叠 UI → TrackballCamera 把鼠标变换进下一帧相机矩阵 → OTKApp 渲染循环里 `DemandLoading/DemandLoading/src/DemandLoaderImpl.cpp:297`（loadTextureTiles 一族）与 processRequests 服务缺页。ShaderUtil 侧纯被 include：`AliasTable.h:26` host 建表 → device `__device__` 采样函数 O(1) 出样本；`ray_cone.h` 随 ray 传播更新锥宽 → 推导纹理梯度 → 决定采样 mip；SelfIntersectionAvoidance 三版在命中点沿法线偏移起点避免 numeric 假命中。

## 设计决策

①**头文件库（header-only）**——ShaderUtil 无构建产物，include 即用，device 编译器内联优化友好；代价是 `vec_math.h` 巨型头的编译时间税；②**三实现自相交规避**——通用/CUDA/OptiX 三版对应"无 intrinsics/有 CUDA/有 OptiX 曲面信息"三场景，精度与成本逐级换；③**CUDAOutputBuffer 四后端**（`CUDAOutputBuffer.h:22`）——GL 互操作最快但设备绑定（`:89`），零拷贝/设备内存后端让无显示环境（CI/远程）也能跑；④**OTKApp 基类约 45 方法**——框架税换示例零样板，Simple/OtkHello 演示最小组装；⑤**MockOptix 函数表替换**（`MockOptix.h:44`）——OptiX 是闭源 SDK，mock 其函数表让库测试脱离 GPU 与许可证。

## 新人提示

写 kernel 先扫 ShaderUtil（大概率已实现：采样查 `AliasTable.h:32`/`CdfInversionTable.h`，LOD 查 `ray_cone.h`，偏移查 SelfIntersectionAvoidance 三选一），再看 examples/DemandLoading/RayCones 等对应示范。写查看器从 OtkHello 抄起，显示问题九成在 `CUDAOutputBuffer.h:22` 的后端选择与 `CUDAOutputBuffer.h:89` 的设备匹配。全仓 device 数学**不要自己写** float3 运算——`vec_math.h:42` 起已有且被广泛内联依赖。无 GPU 开发流：`MockOptix.h:44` 支撑的 gtest 全绿再上真机。改 `vec_math.h` 跑全仓测试（编译半径极大）。
