# 03 · generator_dag_generated_dag.cpp —— 从 AST 到 DAG IR 的代码生成

> 文件：`src/mdl/codegenerators/generator_dag/generator_dag_generated_dag.cpp`（8868 行，图谱 110 子节点）
> 角色：`Generated_code_dag` 类的本体实现——MDL 编译器把语义分析后的 Module AST 编译成 DAG 中间表示的所在地。

## 1. 角色定位

MDL 的后端策略是"一个中心 IR，多个后端"：DAG（有向无环图）是从语义 AST 到一切目标码（LLVM JIT、native C++、GLSL/HLSL、PTX，以及 distiller 蒸馏）之间的公共中间表示。本文件实现 `Generated_code_dag`——DAG 代码生成器的核心：遍历语义完整的 Module，把每个导出函数/材质编译成节点哈希共享的 DAG；再提供 `Material_instance` 实例化机制（参数内联后生成"类编译"材质）。它向上承接 compilercore 的 Analysis 产物，向下喂饱所有 code generator 与蒸馏规则引擎，是编译器"腰部"。

## 2. 内部结构

匿名命名空间的 visitor/辅助类群（DAG 侧）：

- `Scoped_ignore_referenced_strings`（L75）：临时屏蔽字符串引用登记。
- `Type_binder`（L137）：deferred 数组尺寸绑定——`bind_param_type`（L156）把"未定长数组参数类型"绑到实参的具体长度（L158 MDL_ASSERT 双向断言），`get_bound_type`（L176）查绑定或按 size 重建（L192 `m_tf.create_array`）。
- `Material_dumper`（L214）/`Instance_dumper`（L306）：实现 `DAG_dumper`，把材质/实例 DAG 输出为 dot 图。
- `Abstract_temporary_inserter`（L358）：IDAG_ir_visitor，`visit(DAG_call*)`（L394）扫描每个调用的实参，phen-out 计数 >1（L421 `it->second > 1`）或带名字的子表达式提升为 temporary（`create_temporary` L438 查缓存 `m_temp_map`，未命中则 `add_temporary` L444）——这是 DAG→渲染器友好形式的关键重写。
- `Parameter_collector`（L478）：收集材质/函数的全部参数节点。
- `Parameter_inliner`（L624）：实例化时把实参 DAG 内联替换形参。
- `Condition_compute`（L740）：遍历参数的 enable_if 条件（L748 `param.get_enable_if_condition()`），把条件里出现的参数索引登记进 `m_controls[ctrl_index]`（L764-766）——算出"哪个参数控制哪个参数的可见性"，GUI 折叠与后端裁剪都靠它。
- `Let_entry`（L1715）+ Local_type_enumerator（L2111）：let 临时与局部类型的登记。
- `Null_resource_modifer`（L3661）：资源置空改写。
- `Instance_cloner`（L4040）：克隆材质实例；L4201-4202 串起 `m_node_factory` 的 `enable_opt` 等 DAG_node_factory_impl 入口。
- `Transparent_layers`（L5951）：极简 visitor——`visit(DAG_call*)` 一行转发 `m_instantiate_helper.handle_transparent_layers(call)`（L5960）；实现在同名方法（L5970 起），按 semantic 识别 `df::weighted_layer/fresnel_layer/custom_curve_layer`（L5977-6010 的 switch，color 变体 `MDL_FALLTHROUGH` 复用索引表 L5994-5999），weight 为常量 0/1 时整层消解。
- `Ast_dependence_analysis`（L6420）：Module_visitor，在函数 AST 上做依赖分析（带 `Dep_analysis_cache` 缓存，L6429），annotation/name 节点一律剪枝（L6440-6462 的 `return false`）。

`Generated_code_dag` 本体方法群：

- 构造与查询（L864-1020）：`get_material_info`（L918）、`get_function_info`（L942）、`get_annotation_info`（L966）、`get_type_info`（L1000）等。
- 注解生成（L1034-1241）：`gen_function_annotations`（L1034）、`gen_module_annotations`（L1195）等。
- **编译主路径**：`compile_function`（L1241）、`compile_annotation`（L1446）、`compile_local_function`（L1589）、`compute_control_dependencies`（L1742）、`compile_material`（L1767）、`compile_local_material`（L2102）。
- `compile_material` 开场（L1767-1786）：导入返回类型进本 DAG unit 的 type factory（L1771 `m_dag_unit.import(ret_type)`），随后 L1780 `m_node_factory.identify_clear()`——注释明言 "Ensure CSE will not find old expressions"，防止跨材质的哈希碰撞串味；`Forbid_local_functions_scope`（L1783）与 `Target_material_model_mode_scope`（L1785）两个 RAII 切换编译模式。
- 尾部（L8700-8868）：`dump_material_dag`（dot 输出）、`get_interface`（L8743 区段）与一组 `create_default_*` 工厂（enum/vector/matrix/color/texture，L8753-8860）给 API 层造默认值。

## 3. 外部连接

include 证据（L35-52）：上游 `mdl/compiler/compilercore/` 全家（cc_conf/streams/mdl/visitor/hash/analysis）+ `<mdl/compiler/stdmodule/enums.h>`（标准库枚举）+ `<mdl/codegenerators/generator_code/generator_code.h>`（公共基类）；同目录 walker/builder/phen_out/derivatives/code_printer/dep_graph/serializer/dumper 八件套。被调用方：外层 `generator_dag.cpp`（模块级入口）、`generator_native`、`generator_jit`、distiller（IMaterial_instance 即本文件 Material_instance 的接口形态）。`DAG_ir_walker`/`DAG_builder` 是同目录配套 walker/builder 的实例（L347、L5972）。

## 4. 数据流

输入：语义分析后的 `Module`（AST + Definition 表）。过程：① `compile_function/compile_material` 经 `DAG_builder` 把 AST 表达式逐个翻译成 DAG 节点（constant/parameter/temporary/call 四类），call 节点带 semantic 与参数布局；② 节点入 `DAG_node_factory_impl` 的哈希表，结构相同的子表达式自动共享（CSE）；③ `Abstract_temporary_inserter` 把多引用子树提升为 temporary 序列（渲染器按序求值一次、复用多次）；④ `Condition_compute` 算参数控制关系；⑤ 实例化期 `Material_instance::Instantiate_helper` 走 `Parameter_inliner` 内联实参，`Transparent_layers` 做层级折叠。输出：`Generated_code_dag`（模块级，含全部函数/材质 DAG）或实例化后的 `IMaterial_instance`（蒸馏与后端编译的输入）。

## 5. 设计决策

- **DAG 而非线性 IR**：MDL 表达式天然无副作用为主，哈希 DAG 让 CSE 成为表示法本身（同指针即同值），后端无需再跑 CSE pass；对比 LLVM 的 SSA，这是"给翻译器看的 IR"极简选择。
- **temporary 提升（L358）显式化共享**：DAG 共享对渲染器不透明（求值次序问题），插入 temporary 把共享变成显式绑定序列——表示效率与消费端友好性的折中。
- **实例化编译（class compilation）**：材质先编成参数化 DAG，`instantiate` 时内联实参再优化（L5951 层折叠只能在内联后做，因为 weight 此刻才知是不是常量），与"模板+特化"同构。
- **RAII 模式切换**（L1783/L1785）：编译选项以 scope 对象压栈，嵌套编译局部材质时自动还原，避免全局 flag 漏复位。
- **dump 即文档**：Material_dumper（L214）输出 dot，`dump_material_dag` 是排查 DAG 形态问题的第一工具。

## 6. 新人提示

- 调试入口：对编译结果调 `dump_material_dag`（L8708 区段）拿 dot 文件，graphviz 可视化即见节点共享与 temporary 结构。
- `identify_clear()`（L1780）不能省：跨材质残留哈希会让 CSE 返回旧材质的节点——历史上是真实 bug 模式。
- enable_if 语义看 `Condition_compute::process_parameter`（L748）：控制关系是"条件里引用的参数 → 被控参数"，方向别记反。
- 透明层折叠的索引表（L5994-5999）对 weighted/fresnel/custom_curve 三族 × color/非 color 维护 weight/layer/base 实参位置，加新 layer 内建必须同步此 switch。
- 相关文件：generator_dag_builder.h（AST→DAG 翻译）、generator_dag_phen_out.h（引用计数）、generator_dag_dep_graph.h（依赖图）、上游 compilercore_analysis.cpp（本系列第 1 篇）、下游 generator_jit。
