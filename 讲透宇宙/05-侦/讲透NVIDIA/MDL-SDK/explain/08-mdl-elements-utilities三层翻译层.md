# 08 · mdl_elements_utilities：core/int/ext 三层世界的翻译层与运行时服务

## 1. 角色定位

`src/io/scene/mdl_elements/mdl_elements_utilities.cpp`（9408 行，模块内最大文件）是 MDL scene 元素子系统的**公共底座**，头文件自述"Module-internal utilities related to MDL scene elements"（mdl_elements_utilities.h:9）。它服务三个世界：**core**（`mi::mdl::*`，MDL 编译器内部 AST/DAG/类型/值）、**int**（`MI::MDL::*`，scene 元素内部表示）、**ext**（`mi::neuraylib::*`，公共 API）。全文件按横幅注释分区：语义转换、名字编码、MDLE 序列化、DAG 转换器、资源更新、模块缓存与等待队列、常量折叠求值器。模块内其余 11 个 cpp 全部依赖它。

## 2. 内部结构

- **语义码转换组**：`core_semantics_to_ext_semantics()`（mdl_elements_utilities.cpp:115，328 行巨型 switch）、`core_semantics_to_ext_annotation_semantics()`（:443）、反向 `ext_semantics_to_core_semantics()`（:503）——语义枚举在三层间的双向字典。
- **DB 名编码组**：内建算子的 DB 稳定名，如 `get_array_constructor_db_name()` 返回 `"mdl::T[](...)"`（mdl_elements_utilities.cpp:955）、`get_index_operator_db_name()` 返回 `"mdl::operator[](%3C0%3E[],int)"`（:959）。`encode()`（:1067）把 `()<>,:$#?@` 转成 `%XX` 十六进制；`decode()`（:1077）支持 **strict 模式**（非法未转义字符 :1099、坏 hex :1133、意外转义 :1160 均报错进 Execution_context）与宽松模式（:1177）。
- **DAG 双向转换器**：`Dag_importer`（i_mdl_elements_utilities.h:1007）把外部 DAG_unit 导入本 unit，temporaries 按 index 缓存防重复克隆（mdl_elements_utilities.cpp:2790-2805）；`Mdl_dag_builder`（i_mdl_elements_utilities.h:1058）把 int 表达式编成 core DAG；`Mdl_dag_converter`（mdl_elements_utilities.h:379）反向展开，direct call 走 :3965、间接 call 走 :4043；轻量版 `Mdl_dag_converter_light`（:525，实现 :4344）供材料编译热路径。
- **Code_dag 参数访问**：`get_parameter_enable_if_condition()`（:4555）、`get_parameter_default()`（:4585）、`get_parameter_annotation()`（:4602）——UI 自动化取参数元信息。
- **资源值三换**：texture/light_profile/bsdf_measurement 各自转 core value（:4682/:4748/:4791），总入口 `int_value_to_core_value()`（:4834）。
- **Resource_updater**（mdl_elements_utilities.h:821，私有继承 `mi::mdl::Module_visitor`）：`update_resource_literals()`（:6131）五层重载遍历 code DAG 把资源字面量关联 DB tag，`Definition_set`/`Resource_tag_map` 防重遍历（h:866-871）。
- **并发三件套**：`Mdl_module_wait_queue`（i_mdl_elements_utilities.h:1213）为每个加载中模块建 Entry，其他线程 `wait()` 阻塞至加载线程 `notify()`（h:1243-1258），Entry 按 usage count 自销毁；`Module_cache`（i_mdl_elements_utilities.h:1404）实现 `mi::mdl::IModule_cache`，`lookup()`（mdl_elements_utilities.cpp:7251）保证只有第一个线程真加载、其余等待。
- **Call_evaluator<T> 模板**（i_mdl_elements_utilities.h:1532）：挂在 `IExpression_call::fold()` 上的常量折叠钩子，fold_tex_width/height/depth（:7600/:7659/:7718）、light_profile power/maximum（:7521/:7538）——纹理尺寸这类编译期可知值直接折叠成常量。
- **Name_mangler**（mdl_elements_utilities.h:878）：MDL < 1.8 的 namespace alias 改名器。
- **路径与纹理入口**：`get_file_path()`（mdl_elements_utilities.cpp:9153）实现三策略（USE_FIRST/USE_SHORTEST/USE_LONGEST，:9188-9204）；`create_texture()`（:9223）是纹理值创建入口。

## 3. 外部连接

- **上游编译器**：`mi/mdl/` 头十余个 + `mdl/compiler/compilercore` visitor（:83-84）——core 层全部来自 MDL 编译器库。
- **DB 与事务**：`base/data/db` 的 Access/Tag/Transaction（:87-89）；资源关联落 DB tag、模块缓存查 DB。
- **scene 姊妹元素**：`io/image` 与 `io/scene/dbimage/texture/lightprofile/bsdf_measurement`（:91-95）。
- **系统服务**：PATH 模块搜索路径（:9158-9160）、`HAL::Ospath` 规范化（:9163）、磁盘 IO（:80）。
- **公共 API**：`mi/neuraylib` 的 impexp_api/execution_context/imdl_loading_wait_handle（:62-67）——Search_option 与 wait handle 是 ext 契约的直接实现。
- **消费方**：mdl_elements 内全部 11 个实现 cpp 引用本文件符号（grep 实证）。

## 4. 数据流

**模块加载流**（最复杂路径）：MDL 编译器要 import 依赖模块 → `Module_cache::lookup(name, handle)`（mdl_elements_utilities.cpp:7251）查 DB；miss 时第一个线程拿到加载权（`processed_in_current_context()` 判同 context，h:1265），其余线程在 `Mdl_module_wait_queue::lookup()`（:7059）拿 Entry 调 `wait()` 挂起；加载线程完成后 `notify()`（:7116）广播结果码，等待线程据此继续或中止。

**DAG 表达流**：模块加载后函数体以 core DAG 存在；用户访问参数默认值/注解时 `Code_dag` 系列（:4555-4682）直读；生成可编辑表达式时 `Mdl_dag_converter` 把 core DAG 展开成 int 表达式树（资源值经 :4682-4834 三换）；改完再 builder 编回 DAG。折叠机会由 `Call_evaluator` 在 fold 回调中抓住。

**资源落地流**：`create_texture()`（:9223）→ 查 `MDL_CTX_OPTION_RESOLVE_RESOURCES` → 不解析则返回占位，解析则经 texture 元素实际装载并回填 tag；批量场景由 `Resource_updater` 整 DAG 扫描（:6131），按 `Resource_tag_map` 缓存去重。

## 5. 设计决策

- **%XX 转义做 DB 名**：`operator[](%3C0%3E[],int)`（:959）把 `<0>` 编成 `%3C0%3E`，任意 MDL 签名安全映射为 DB 唯一键；strict decode 把格式错误显式抛给 Execution_context 而非静默吞掉——错误路径一等公民。
- **三层枚举全手工映射**：:115 起 328 行 switch 是机械但不可省的胶水；反向映射（:503）同样 250 行，体积换明确性。
- **等待队列自销毁**：Entry 的 usage count 归零即 cleanup 自毁（h:1278），不依赖外部 GC——并发原语的生命周期内嵌。
- **MDL 版本条件行为**：Name_mangler 对 >= 1.8 直接返回原名（h:894-899），旧版语义完整保留——单类内做版本兼容而非分叉两套。
- **热路径轻量副本**：Mdl_dag_converter_light（:4344）证明全量 converter 开销可观，材料编译为性能单独瘦身一份。
- **FIXME 留痕**：Dag_importer 的 DbgInfo 直通（:2823）明示跨 unit 文件表未做；neuray 表示不支持 debug info（:109 的 NO_DBG 宏），缺口被诚实标注。

## 6. 新人提示

- 别被 9408 行吓到：按横幅分区读，先读 :1067-1180 的 encode/decode 与 :9153 的 get_file_path 找手感，再攻 DAG 转换器。
- **加新 intrinsic 函数**三动作缺一不可：semantics 映射、Call_evaluator 的 fold_* 方法、在 `is_evaluate_intrinsic_function_enabled()`（:7387）注册白名单。
- debug 名字显示用 `decode_for_error_msg()`（:1177）宽松模式；用户输入校验才用 strict——选错模式要么报错爆炸要么放过脏数据。
- 模块加载死锁排查先看 `Mdl_module_wait_queue::Table`（h:1281）：每事务一张表，Entry 的 `m_cache_context_id` 判同 context 重入（h:1271）。
- Resource_updater 的 `m_definition_set`/`m_resource_tag_map`（h:866-871）是防指数爆炸的命门，扩展时别绕过直接递归。
- `get_file_path` 三策略语义易混：USE_SHORTEST 指模块名最短（搜索路径最长命中），:9186-9190 注释反直觉，读代码为准。
- 改语义映射时两个方向都要测：core→ext 与 ext→core（:115/:503）不对称是常态，漏一边编译不报错、运行才炸。
