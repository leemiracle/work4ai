# 09 · Polygraphy 运行时：backend 分舱、functor 流水线与工具注册盲区

> 图谱锚：L11「Polygraphy 核心运行时库」（219 节点，单域最大）+ L13 扩展生态 · tour t12/t13。源码根 `tools/Polygraphy/polygraphy/`。

## 一、角色定位

Polygraphy 是 TensorRT 的「深度推理调试/比较/转换瑞士军刀」：一个 Python 库 + 一族 CLI。核心运行时只做三件事——**把各后端（TRT/ONNX-Runtime/TF/PyTorch）统一成相同 Loader/Runner 协议**、**生成可复现 Python 脚本代替 shell 命令**、**多后端输出精度比较**。它不链接 C++，重依赖全经 `mod.lazy_import` 按需拉起，裸环境 import 秒级完成。219 个图谱节点里没有"引擎"类——推理都在后端库里，Polygraphy 是编排层。

## 二、内部结构

**backend 八分舱**（`polygraphy/backend/`）：`base`（协议）、`trt`、`onnx`、`onnxrt`、`tf`、`pyt`、`pluginref`、`common`，2025 新增 `tensorrt_rtx`。

- **协议舱**：`backend/base/loader.py:22` `BaseLoader` 只定两件事——`call_impl`（base/loader.py:29，子类实现）与 `__call__`（base/loader.py:33，functor 入口）；`backend/base/runner.py:30` `BaseRunner` 附类级计数器 `RUNNER_COUNTS`（base/runner.py:35，base/runner.py:49-50 为匿名 runner 生成唯一默认名）。全部后端类继承这两个基类，**Loader/Runner 可像函数一样链式调用**。
- **TRT 构建链**（`backend/trt/loader.py`，全仓最大后端模块）是 functor 流水线：`LoadPlugins`（trt/loader.py:38）→ `CreateNetwork`（trt/loader.py:82）→ `BaseNetworkFromOnnx`（trt/loader.py:161，派生 Bytes/Path 两形态 trt/loader.py:272、trt/loader.py:344）→ `PostprocessNetwork` 家族（trt/loader.py:419 起：`ModifyNetworkOutputs` trt/loader.py:474、`SetLayerPrecisions` trt/loader.py:521 等）→ `EngineBytesFromNetwork`（trt/loader.py:716）→ `EngineFromNetwork`（trt/loader.py:847，call_impl 在 trt/loader.py:891）→ `EngineFromBytes/Path`（trt/loader.py:906/964）→ 反向 `BytesFromEngine`（trt/loader.py:1024）。一行 `EngineFromNetwork(NetworkFromOnnxPath("m.onnx"), CreateConfig(...))` 即完成构建。
- **mod 延迟加载双翼**：`mod/importer.py:67` `lazy_import` 返回 `LazyModule`（importer.py:237，`__getattr__` 在 importer.py:246 才真正 import 并校验版本），`autoinstall`（importer.py:287）可 pip 子进程补装；`mod/exporter.py` 的 `export(deprecated=...)` 允许符号先于实现存在；`mod/trt_importer.py` 是 TRT 导入统一收口（2025 新增）。这套机制是 scanner 系统性盲区——大量 `depends_on 0.6` 边为批阶段手补。

## 三、外部连接

上游消费第 7/8 篇的 `tensorrt` 绑定（经 trt_importer 收口）；平级引用 onnx-graphsurgeon（第 10 篇）做图手术；下游被 `polygraphy-extension-trtexec`（L13，扩展协议范本：`import *` 只暴露 `@mod.export()` 装饰对象）与仓根 `.agents/skills`（第 12 篇）间接使用。comparator 流式模式用 multiprocessing.Process/Queue 把数据生成放子进程逐批喂推理端，`LazyArray` 把超阈值大数组序列化到临时文件惰性读。

## 四、数据流

CLI 数据流：`polygraphy/tools/registry.py` 在**模块导入期**用 `importlib.import_module`（registry.py:17）拉起十个工具模块（registry.py:51-60：run/convert/inspect/check/surgeon/template/debug/data/plugin/multi_device）——导入副作用即注册，非常见的惰性模式；失败工具以 `MissingTool`（registry.py:25）占位；registry.py:63-68 重名检查。参数进 `tools/args/` 参数组体系（构造注入 + `*_impl` 模板方法），`tools/script.py` 把用户意图渲染成等价 Python 脚本——写入经 `ensure_safe`（script.py:67）守门，`Script` 类（script.py:226）的 `add_import`（script.py:307）收集导入清单；最终 `tools/run/run.py` 默认 `exec(str(script))`（`--gen-script` 落盘复现）。**registry.py 的字符串动态加载是静态分析全盲区**：十条工具依赖边全部手补（NOTES batch-17 钉版）。

## 五、设计决策（含 AOT/JIT 双模式跨域联动）

1. **functor 协议优于类层次**：`call_impl/__call__` 两段式让配置对象与函数同构，管道任意嵌套重排，可测试性显著优于继承式 builder。
2. **脚本生成器是可复现性载体**：每个 CLI 命令都能吐出等价 Python——这是 Polygraphy 区别于 trtexec 的根本卖点。
3. **延迟加载是生存策略**：任何顶层硬 import 都会把轻量调试工具变成重型环境；代价是静态分析必须大量手补边。
4. **AOT/JIT 双模式（跨域注记）**：Python 原生插件的 AOT/JIT 判定真身在 `python/packaging/bindings_wheel/tensorrt/plugin/_lib.py`（L10 域，tour t11）——`_lib.py:302` STRICT_AOT 无 aot_impl 即报错、`_lib.py:316` PREFER_AOT、`_lib.py:321` 双实现并存时必须经 NetworkDefinitionCreationFlag 指明偏好、`_lib.py:348` AOT 路径实例化 `_TemplateAOTPlugin`（类定义在 `_plugin_class.py:319-444` 的 IS_AOT_ENABLED 条件块，tree-sitter 盲区手补）；绑定侧入口是 pyGraph.cpp 的 `add_plugin_default_func`。Polygraphy `tools/plugin/autotune` 是其上层消费者。
5. **版本门控测试**：`skip_if_trt_11` 按 TRT 版本裁剪 INT8/校准用例——TRT 11 起强类型网络移除弱类型精度标志。

## 六、给新人的提示

入门顺序：读 `backend/base/` 两个文件（<200 行）理解协议 → `examples/api/` 前十例 → `polygraphy run model.onnx --gen-script` 观察脚本生成。"工具没注册"直接看 registry.py 调用表；写扩展记住可见性协议——不 `@mod.export()` 的符号包级 `import *` 不可见。改 backend 坚持用 lazy_import，一个顶层 `import tensorrt` 就会破坏无 TRT 环境的用例（tests 有守卫）。深挖精度先读 `tools/debug/debug.py` 的 raw-string docstring——完整迭代调试方法论，全工具族权威入口。
