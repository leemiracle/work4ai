# 01 · pybind11 绑定层：main.cpp 如何把 OptiX C API 翻成 Python

## 角色定位

`src/main.cpp`（4162 行）是全仓唯一的运行时源文件，编译为 `_optix` 扩展模块；`src/optix/__init__.py` 用 `from ._optix import *`（__init__.py:25）加动态 `__all__`（__init__.py:28）把它变成 `import optix`。绑定层职责：把 OptiX 7+ 的 C API（句柄、union 布局的 BuildInput、输出参数日志）翻译成 Python 对象语义。

## 内部结构

三类语法糖（行号 grep 实证）：①**26 个包装 struct**（main.cpp:105-961），句柄五件套 DeviceContext（main.cpp:105）/Module（:112）/ProgramGroup（:119）/Pipeline（:126）/Denoiser（:132），四种 BuildInput 数组（Triangle :170/Curve :225/CustomPrimitive :275/Instance :314），Instance（:353）、变换族 StaticTransform（:423）/MatrixMotionTransform（:468）/SRTData（:516），选项与描述符族 MotionOptions（:385）/PipelineCompileOptions（:558）/PipelineLinkOptions（:594）/ShaderBindingTable（:612）/PayloadType（:743）/ModuleCompileOptions（:774）/ProgramGroupDesc（:864）。②**31 个 `py::enum_`** 覆盖 OptixResult 到 ProgramGroupFlags。③**9 个自由函数 `m.def`**（main.cpp:2339-2347：version/deviceContextCreate/getErrorName/getErrorString/launch/sbtRecordPackHeader/sbtRecordGetHeader/convertPointerToTraversableHandle/getDeviceRepresentation）+ 41 处 class_ 方法绑定。PYBIND11_MODULE 入口在 main.cpp:2318。

## 外部连接

绑定层向上只暴露 `src/optix` 包（wheel.packages 仅此目录，pyproject.toml:67），向下链接 OptiX 头（CMake FetchContent 自 NVIDIA/optix-dev v9.1.0，CMakeLists.txt:28-33）与 CUDA driver/runtime（CMakeLists.txt:53-58）。BuildInput 族带 setXxx/sync 方法在绑定层对齐 C API 的 union 布局——Python 侧设置字段后必须 sync 才进 C 结构。

## 数据流

以 accelBuild 为例：Python 传 BuildInput 对象列表 → `convertBuildInputs` 两个重载（main.cpp:95 与 :1001）在调用点（main.cpp:1625/:1661）把列表转成 C 数组 → 结果句柄回包成 Python 对象。错误路径统一走 getErrorName/getErrorString（main.cpp:2341-2342）与 DeviceContext 日志回调。这是"Python 列表语义 → OptiX 数组参数"的边界翻译层的典型样本。

## 设计决策

- **句柄 struct 化而非裸 int**：每个句柄带 operator== 与 Python 属性，比裸指针安全且可打印。
- **宽绑定窄入口**：41 处 class_ 方法绑定把方法挂到各自句柄上（`ctx.pipelineCreate`、`denoiser.setup`），只留 9 个真正全局的函数——API 面自聚类。
- **版本语义拆两层**：pyproject `version="9.1.0"`（pyproject.toml:10）跟随 OptiX 代际，`__init__.py:20` 的 `__version__="0.1.0"` 表示绑定自身成熟度。

## 新人提示

读绑定从 main.cpp:2318 的 PYBIND11_MODULE 向上反查；记住"图谱/文档里 denoiserSetup→denoiserInvoke 的叫法不准，真实符号是 denoiserCreate/setup/invokeTiled 方法链"（denoiser.py:248/:265/:295 实证）。
