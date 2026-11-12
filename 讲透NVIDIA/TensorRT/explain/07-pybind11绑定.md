# 07 · pybind11 绑定：tensorrt Python 模块的宏体世界

> 图谱锚：L09「Python pybind11 绑定源码」（19 节点）· tour t10。源码根 `python/src/`（5 个编译单元，7430 行）。

## 一、角色定位

C++ 核心（nvinfer/nvinfer_plugin/lean/dispatch）经本域的一组 pybind11 编译单元变成 `import tensorrt`。它不含推理逻辑，只做三件事：类型桥接（Dims/DataType/PluginField）、异常翻译（返回码→Python 异常）、生命周期托管（TRT 对象归引擎所有，Python 只持句柄）。入口极小——`python/src/pyTensorRT.cpp:26` 的 `PYBIND11_MODULE(TENSORRT_MODULE, m)`，`TENSORRT_MODULE` 本身是构建期占位符（第 8 篇），同一份源码编出 `tensorrt`/`tensorrt_lean`/`tensorrt_dispatch` 三个变体。

## 二、内部结构

绑定四层，由 `pyTensorRT.cpp:52-57` 的调用顺序固定：`bindFoundationalTypes` → `bindPlugin` → `bindCore`，`bindGraph`/`bindOnnx` 藏在 `#if EXPORT_ALL_BINDINGS`（pyTensorRT.cpp:54、pyTensorRT.cpp:58）条件编译——全功能与精简变体共享入口。

- **基础类型层** `python/src/infer/pyFoundationalTypes.cpp:176`：`DataType` 枚举 12 值（pyFoundationalTypes.cpp:179-190），FLOAT 到 FP4/E8M0 全谱系；`m.attr("float32") = DataType::kFLOAT`（pyFoundationalTypes.cpp:193-199）建立 `trt.float32` 直读别名。
- **核心层** `python/src/infer/pyCore.cpp:912` `bindCore`：builder/logger/engine/runtime/context。Python 侧 logger 继承由嵌套类 `PyLogger`（pyCore.cpp:917 附近）承接——`noexcept override` 内先 `gil_scoped_acquire` 再 `PYBIND11_OVERLOAD_PURE_NAME` 回调，异常只落 stderr 不外溢；`DefaultLogger` 提供带时间戳的 C++ 默认实现。
- **插件层** `pyPlugin.cpp`（3938 行，最大）：经典 trampoline 双层——Py 基类供 Python 继承捕获 override，`*Impl` 包装类再管 `py::handle` 生命周期，文件级 `std::map<IPluginV2*, py::handle> pyObjVec` 记账防提前回收；`PLUGIN_API_CATCH` 宏统一吞 Python 异常（noexcept 虚函数内异常外溢即 terminate）。
- **图构建层** `pyGraph.cpp` 的 `bindGraph`：数百条链式 `def/def_property` 巨函数，长 lambda 集中于文件头 `lambdas` 命名空间（pyCore.cpp:33，约定见 pyCore.cpp:32 注释），如 `opt_profile_set_shape`（pyCore.cpp:36）把 min/opt/max 三次 `setDimensions` 打包。

**宏体盲区（图谱手扫注记）**：PYBIND11_MODULE 与 bindCore/bindGraph 的绑定体全在宏/巨函数内，tree-sitter 零结构提取（NOTES batch-100），图谱节点人工补齐——这是 L09 仅 19 节点的根因：文件少、每文件一个巨函数、def 链无法静态切分。

## 三、外部连接

上游：NvInfer.h 接口谱系（组 1）；`python/docstrings/` 的 Doc 类注入绑定文档；`cmake/modules/FetchPyBind11.cmake` 拉依赖。下游：wheel 流水线（第 8 篇）把产物改名 `.so/.pyd` 装包；Polygraphy `mod/trt_importer.py` 消费。half 桥：`third_party/ieee/half.h:34` 标注 `Version 1.12.0`（sourceforge half 单头库 vendored 副本）；`parsers/common/ieee_half.h` 是同源第二副本（diff 仅缩进换行差异，独立拷贝非包装引入），供 ONNX parser 半精度路径。

## 四、数据流

一次 `trt.Logger()` 调用：Python 属性访问 → pybind11 dispatch 进 bindCore 注册的 lambda → 直调 C++ → TRT `noexcept` 边界返回状态码 → `python/include/utils.h:258` `PY_ASSERT_RUNTIME_ERROR` 翻译成 Python 异常（同类 utils.h:267 INDEX_ERROR、utils.h:276 VALUE_ERROR）→ 抛回 Python。numpy 桥走 `python/src/utils.cpp:99` `nptype()` 与 utils.cpp:121 反向 `type()`；utils.cpp:160 `throwPyError` 是带 GIL 的通用抛错出口。字符串特殊：`FallbackString`（pyTensorRT.cpp:40）以 `py::nodelete` 声明——Python 绝不能释放 TRT 仍引用的字符串内存。

## 五、设计决策

1. **`py::module_local` 全线**（pyTensorRT.cpp:33-40 注释明示）：所有类/枚举必须 module-local，`tensorrt_lean` 与 `tensorrt_dispatch` 才能同进程导入——多形态分发的 ABI 基石。
2. **module_local + nodelete 句柄组合**：对象生命周期归引擎所有；context manager 被 Python 层补丁改为 deprecation 警告（第 8 篇 `__init__.py:102-116`）。
3. **vc Windows 异常体系**：`plugin/vc/` 是 MSVC 专属编译的插件公共件副本（vc=Visual C++）——`checkMacrosPlugin.h:37` `LogStream` 流式日志类（四个 `gLog*` 实例声明于 checkMacrosPlugin.h:89-92）、checkMacrosPlugin.h:203 `caughtError`、checkMacrosPlugin.h:270 与 checkMacrosPlugin.h:286 `PLUGIN_VALIDATE` 软校验宏（checkMacrosPlugin.h:98 的 `noexcept [[noreturn]]` 注释保证可用于 noexcept 函数体内）；`vfcCommon.h:36` `extern "C" setLoggerFinder` 与 vfcCommon.h:38 `getCreators` 是 Windows 插件库 C 出口。Linux 侧 `plugin/common/checkMacrosPlugin.h` 以 `#ifdef _MSC_VER` 条件 include vc 变体。
4. **宏体集中 bind**：按「文件=域」切分而非按类，pyCore 一个 912 行起跳的函数管全部核心对象——def 链书写紧凑，代价是静态分析全盲。

## 六、给新人的提示

从 `pyTensorRT.cpp`（63 行）入门，再按 bind 顺序下钻。找某个 Python API 的真实行为，grep pyCore.cpp/pyPlugin.cpp 的 def 链比看文档快——`trt.float16` 真身在 pyFoundationalTypes.cpp:195。改绑定必须同步 `python/docstrings/`，否则文档站静默失真。源码里出现 `##TENSORRT_MODULE##` 不是 bug，是模板（第 8 篇）。trampoline 异常路径只打日志不抛出——调试"Python 回调没生效"先查 stderr 而非 Python traceback。
