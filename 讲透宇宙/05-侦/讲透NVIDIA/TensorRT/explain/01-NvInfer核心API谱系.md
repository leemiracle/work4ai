# 01 · NvInfer 核心 API 谱系：伞形头、执行三件套与插件三代演进

## 角色定位

`include/` 是 TensorRT 全部公共 C++ API 的声明层，共 14 个头文件（顶层 13 个 `.h` + `impl/NvInferPythonPlugin.h`）。它是闭源核心 `libnvinfer.so` 与外部世界之间的唯一契约面：ONNX parser、python 绑定、全部 37 个插件仓、Polygraphy 都只依赖这 14 个头编译。三巨头分工明确——`NvInfer.h`（11892 行，伞形入口）、`NvInferRuntime.h`（5479 行，全仓最大公共运行时头，本仓 tree-sitter 对纯声明头零提取、API 类谱系为图谱批甄别手工建立）、`NvInferRuntimePlugin.h`（925 行，插件接口层）。`NvInfer.h:21-22` 以 `#include "NvInferLegacyDims.h"` 与 `NvInferRuntime.h // IWYU pragma: export` 两行完成伞形聚合，自身再叠加 Builder 侧类（`INetworkDefinition` :8162、`IBuilderConfig` :10579、`IBuilder` :11513）。

## 内部结构

运行时主线是三件套：`IRuntime`（`NvInferRuntime.h:1894-1900`，`class IRuntime : public INoCopy`）持有全局配置（如 `setDLACore` :1919-1921）；`ICudaEngine`（:3081-3087）是序列化后的可执行计划，两条产出执行上下文的路径并存——`createExecutionContext(strategy)`（:3162-3165）与 `createExecutionContext(IRuntimeConfig*)`（:3245-3247，策略直接内联的新形态）；`IExecutionContext`（:4023-4032）承载单次推理的全部状态：`setInputShape` :4210-4212、`setTensorAddress` :4460、`setInputTensorAddress` :4522、`enqueueV3(cudaStream_t)` :4721。类的创建走 C ABI 工厂：`createInferRuntime_INTERNAL` 声明于 :5109，内联包装 `createInferRuntime` 在 :5139-5141 把 `NV_TENSORRT_VERSION` 编进调用，实现旧版 ABI 闸门。构建侧入口 `createNetworkV2`（`NvInfer.h:11592-11594`）与 `buildSerializedNetwork`（:11668-11670）构成 builder 闭环；`IOutputAllocator`（`NvInferRuntime.h:3895`）是 10.x 引入的输出尺寸动态分配回调面。

## 外部连接

向下：全部类只是 `TENSORRTAPI` 两段式宏导出的纯虚接口，实现体在闭源 `libnvinfer.so`/`NvInferImpl.h`（1402 行，`V` 前缀类经 `v_x_y` 命名空间委托）。向内：插件体系三代表述并存于同一套头——V2 代在 `NvInferRuntimePlugin.h` 整体标记废弃（`PluginVersionType` 枚举 kV2/kV2_EXT/kV2_IOEXT/kV2_DYNAMICEXT 全部 `TRT_DEPRECATED_ENUM`，:97-105；`IPluginV2` 类 :125-138 带 `TRT_DEPRECATED`；`IPluginV2Ext` :461、`IPluginV2IOExt` :656、`IPluginCreator` :912）；V3 代拆成能力面：`IPluginV3`（`NvInferPluginBase.h:205`）+ `IPluginCapability`（:140）+ `IPluginV3OneCore/OneBuild/OneRuntime`（`NvInferRuntime.h:830/873/1095`）+ `IPluginCreatorV3One`（:5361）。值得注意的是 **`IPluginV2DynamicExt` 类声明已从 TRT 11 头文件中物理删除**（全 include/ 仅剩 :102-104 等注释引用），枚举残留只为旧引擎反序列化。注册表 `IPluginRegistry`（`NvInferRuntimeCommon.h:39-55`）经 `getPluginRegistry`（`NvInfer.h:11811-11813`）暴露。版本锚：`NvInferVersion.h:30-33` 四宏映射到 `TRT_MAJOR_ENTERPRISE` 等产品宏，仓内 `VERSION` 文件为 11.3.0.99（enterprise 形态）。

## 数据流

用户视角一条直线：`createInferRuntime(logger)` → `deserializeCudaEngine` → `createExecutionContext` → 逐 tensor `setTensorAddress`/`setInputShape`（动态 shape 触发 shape 推断，`inferShapes` 在 :4574）→ `enqueueV3(stream)` 异步发射。Builder 视角：`createNetworkV2` → 加层/挂插件 → `buildSerializedNetwork` 产出 `IHostMemory` 计划字节流。两条流在 engine 字节流处交接：build 期插件走 `getFieldsToSerialize` 字段序列化，runtime 期 `IPluginRegistry::deserializePlugin` 复原——这正是 V2 二进制 serialize 与 V3 字段集合两条协议的代际分叉点（详见 02/03 篇）。

## 设计决策

三个可品味的决策：①**版本化命名空间叠层**——接口全部先在 `v_1_0` 内定义（如 `NvInferRuntime.h:613/728`），顶层 `using IPluginV3 = v_1_0::IPluginV3`（`NvInferPluginBase.h:273`、`NvInferRuntime.h:1246/5458`）提升；需要不兼容演进时新建 `v_2_0` 面（如 `IPluginV3OneBuild` 升级版 `InterfaceInfo{"PLUGIN_V3ONE_BUILD", 2, 0}`，:1190-1210 区域），旧面原样保留，C++ ABI 与 API 版本双轨。②**头文件三段式导出宏**（`TENSORRTAPI class ...`）让同一份声明在 Windows dllexport 与 Linux visibility 下复用，代价是 tree-sitter 类提取全盲，本图谱全部 API 类节点为手工补齐。③**enqueueV3 替代 executeV2/enqueueV2**：新接口以 tensor 名寻址取代 binding index，去掉隐式 batch 语义，是 TRT 8→10 API 收敛的收笔动作；废弃枚举值（kV1_PYTHON :119-121）保留给 python 插件位标记，显示 python JIT 插件与 C++ 插件共享同一版本坐标系。

## 新人提示

读 API 演进史首选 `NvInferRuntime.h`——同文件并置 V2 动态插件注释、V2 stream reader 与 V3 能力面三代表述，是活的化石层。两个易踩坑：① `IPluginV2DynamicExt` 在 TRT 11 头里查不到类定义不是你 grep 姿势问题，是物理删除，写新插件只能走 `IPluginV3` 四重继承（`IPluginV3+OneCore+OneBuild+OneRuntime`，插件侧范例见 qkvToContextPlugin.h:55-59）；② 版本号字符串比较是插件注册表的寻址键，同名不同 version 是双轨共存机制（本仓 plugin/ 目录大量使用），改动 version 常量等价于换插件。CHANGELOG.md 按 10.x→11.x 逐条记录 API 生死，是本篇最好的伴读。
