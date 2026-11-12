# 12 · AutoGraph vendored 与 c_api 双代

## 一、角色定位

L15（76 文件）是 `dali/python/nvidia/dali/_autograph/`——从 TensorFlow v2.10.0 整体抽出的 AutoGraph（`_autograph/VERSION` 记版本与源 commit 359c3cdf），经 DALI 适配后承担一件事：`pipeline_def` 装饰的普通 Python 函数里出现 if/for/while 控制流时，把它改写成等价的 DALI 符号图分支节点。同篇并讲 c_api 双代：`dali/c_api/`（一代极简句柄）与 `dali/c_api_2/`（二代面向对象包装）加上 `include/dali/c_api.h` 纯 C ABI——这是 Python 之外（Rust/Go/C 绑定）消费 DALI 的出口，两者同属"语言边界层"。

## 二、内部结构

**AutoGraph 四子包**：converters/ 控制流转换器——`dali/python/nvidia/dali/_autograph/converters/control_flow.py:227` 生成 `ag__.if_stmt(...)` 调用、`dali/python/nvidia/dali/_autograph/converters/control_flow.py:281` 对应 while_stmt，另覆盖 break/continue/列表推导/逻辑表达式；operators/ 是改写后调用的运行时算子，`operators/control_flow.py` 模块 docstring 明示"成对 get_state/set_state 捕获代码块突变"的函数化语义；pyct/ 是静态分析工具链——parser（gast 兼容 AST）、cfg.py 构 CFG、`pyct/transpiler.py:280` `transform()` 主流程、`pyct/static_analysis/liveness.py:36` `Analyzer(cfg.GraphVisitor)` 做活性分析（另有 reaching_definitions 等）；core/ 管 converter 注册与 ag_ctx；impl/conversion.py 管 converted_call；lang/ 是 directive。版权头 `pyct/transformer.py:1` 保留 "Copyright 2017 The TensorFlow Authors"（Apache-2.0）。

**DALI 接入点**：`pipeline.py:23` 导入 `_conditionals`；`pipeline.py:2124` `_conditionals._autograph.convert(recursive=True, user_requested=True)(func)` 是转换唯一入口；`pipeline.py:2137-2145` 建立 ConditionStack 并 `register_data_nodes` 把分支变量注册成 DALI DataNode。

**c_api 一代**：`include/dali/c_api.h:34` `typedef struct DALIPipeline *daliPipelineHandle` 不透明句柄即全部抽象；`c_api.cc:244`→`:255`→`:274` daliCreatePipeline→2→3 版本链式包装（新参数只加新函数，ABI 冻结）。句柄内部其实是 shared_ptr+两张 map（`c_api.cc:58-69` batch_size_map/data_id_map），`c_api.cc:121` SetExternalInput 经 reinterpret_cast 还原。错误处理是选择性 catch（`c_api.cc:564` out_of_range、`:782`/`:791` bad_alloc）——甄别修正：批阶段笔记称"异常统一转 daliLastError 风格错误码"，一代实为选择性捕获+返回码，全量异常翻译是二代才有的。

**c_api_2 二代**：`dali/c_api_2/error_handling.cc:25` ErrorInfo、`:34` `thread_local ErrorInfo g_daliLastError`、`:87` `HandleError(std::exception_ptr)` 统一翻译，`dali/c_api_2/error_handling.h:64` TRY 宏把 current_exception 交给它；`ref_counting.h:25` RefCountedObject/`:56` RefCountedPtr 侵入式引用计数供句柄族共享；`dali/c_api_2/pipeline.cc:28` ToPointer(h→Wrapper*)、`:334` daliPipelineRun；`pipeline_outputs.cc:90` daliPipelineOutputsGet、`:119` GetTraces；`data_objects.cc:332` daliTensorListResize；`dali/c_api_2/init.cc:40` daliInit。

## 三、外部连接

AutoGraph 上游是 TF AutoGraph 源码树（vendored 钉 v2.10.0，隔离上游演进、剥离 TF 运行时依赖）；下游消费者是 `_conditionals.py` 与 `pipeline_def`（L14）。DALI 适配痕迹集中在条件支持：register_data_nodes 让 if 分支两侧都产生 DataNode 进图。c_api 面向外语绑定：`c_api/c_api_test.c` 纯 C 编译链接冒烟（验证无 C++ mangle）；c_api_2 带 op_test/ 复杂管线端到端；与 L14 `backend_impl.cc` 的 pybind 通道构成 Python/C 双出口。

## 四、数据流

pipeline_def 转换链：装饰→inspect 取源→pyct parser（gast）→CFG 构建+活性/到达定义分析→converters 逐节点改写（if 语句→ag__.if_stmt(basic/body/orelse 三态闭包，变量经活性分析决定哪些需跨分支携带）→codegen 产出新函数对象并按源码指纹缓存（pyct/cache）→定义期执行生成 OpDef。c_api_2 调用链：daliInit→daliPipelineCreate（Wrapper 包装 C++ Pipeline）→喂输入→daliPipelineRun→daliPipelineOutputsGet 换 daliTensorList 句柄→Destroy；任何一步 C++ 异常被 TRY 宏捕获、写 thread_local 槽，调用方随后读错误串——C 边界零异常逃逸。

## 五、设计决策与取舍

vendored 而非 pip 依赖 TF：AutoGraph 转换器与 TF 运行时本就解耦，钉住版本换来零 TF 依赖+自由改造（条件支持即 DALI 私有扩展）；代价是上游修复须手动同步。pyct 静态分析是正确性基座——没有活性分析就不知道循环变量哪些要提升到分支图两侧，这是控制流函数化最易错处。c_api 双代并存是 ABI 演进策略：一代句柄面已冻结（只增函数不改签名），二代把张量/输出/检查点全部对象化，宁可用侵入式引用计数+Wrapper 层也不动公共头。两代错误处理哲学差（选择性 catch vs thread_local 全量槽）正是 C 边界错误设计的两代答案。

## 六、新人提示

查"我的 if 怎么变成图分支"从 `dali/python/nvidia/dali/_autograph/converters/control_flow.py:227` 的 if_stmt 模板入手，配 pyct/pretty_printer 打印转换后 AST；调试报错行号错位看 pyct/origin_info（保留原始行号）。写外部绑定选 c_api_2，样板读 `c_api_2/pipeline_builder_test.cc`；改 `include/dali/c_api.h` 是 ABI 变更，只能加不能改。pipeline_def 的 enable_conditionals 开关经 `pipeline.py:2066-2069` 的 argspec 检查生效，条件开关关闭时控制流走急切求值（Python 语义）而非图分支——两套语义别混。
