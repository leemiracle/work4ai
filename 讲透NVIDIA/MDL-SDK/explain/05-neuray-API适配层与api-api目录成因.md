# 05 · neuray API 适配层 —— distiller API 实现、type wrapper 体系与 src/api/api/ 双层目录成因

> 文件：`src/api/api/neuray/neuray_mdl_distiller_api_impl.cpp`（706 行）+ `src/api/api/neuray/neuray_type_impl.h`（753 行）
> 主题：公共 API（`mi::neuraylib`）与核心实现（`MI::MDL`）之间的适配层；顺带考证 `src/api/api/` 双层目录的来历。

## 1. 角色定位

MDL SDK 有两个世界：编译器核心（`mi::mdl` 命名空间，自由接口）与 neuray 集成层（`mi::neuraylib`，DB/transaction 范型、跨 DLL 的 COM 风格接口）。本篇两个文件是后者的适配层代表：`neuray_mdl_distiller_api_impl.cpp` 实现 `IMdl_distiller_api`——把 mi::IMap 形式的用户选项、DB 里的 ICompiled_material 桥接到核心 DIST 模块（第 4 篇）和 BAKER 模块；`neuray_type_impl.h` 定义 type wrapper 体系——把核心 `MDL::IType` 系列包成 `mi::neuraylib::IType` 系列公共接口。它们不实现任何编译/蒸馏算法，只做**类型桥接、生命周期管理与错误码翻译**。

## 2. 内部结构

**neuray_mdl_distiller_api_impl.cpp**：

- 选项读取三件套（L62-92）：`get_option(IMap*, name, bool&/int&/float&)` 三个重载，从 mi::IMap 类型安全取值。
- `Mdl_distiller_api_impl` 构造（L96-101）持有 dist/baker 两模块句柄；`start/shutdown`（L450-462）配对 set/reset。
- `Debug_print_stream`（L146-202）：实现 `mi::mdl::IOutput_stream`，120 字节缓冲攒行、遇 `\n` flush 到 `LOG::mod_log`（L176）；"not reference counted"（L191-193 retain/release 恒返 1）——栈对象冒充接口的合法姿势。
- `Rule_matcher_event`（L205-350）：实现 `IRule_matcher_event` 七回调，把蒸馏规则匹配桥成日志：`path_check_event`（L214，trace>=2）、`rule_match_event`（L233，trace>=1）、`postcondition_failed*`（L254-271，恒 ERROR）、`debug_print`（L273，借 Debug_print_stream 打 DAG 值）、`detailed_trace_event`（L301，七种事件枚举映射字符串 L313-335）。
- **主流程 `distill_material`**（L354-426）：① 判空返 -1（L364）；② 12 个 `get_option` 装填 `Distiller_options`（L370-381，含 `_dbg_trace` 等调试项）；③ wrapper 解包核心对象 `get_db_element()/get_db_transaction()`（L383-389）；④ `load_distilling_support_module`（L391，第 4 篇的支持模块）；⑤ 调 `m_dist_module->distill`（L400-406），仅当需要 trace 才传 event_handler（L402 三目）；⑥ 新建 `Mdl_compiled_material`（L410-417），`transaction->create` + `swap` 重新包成 API 对象（L419-423）。
- Baker 线：`create_baker`（L428-448）与 `Baker_impl`（L546-702）。构造 pin 事务（L557）、析构 unpin（L561-563）——长操作锁事务防中途提交；`bake_texture` 两层（L587/L599）、`bake_texture_with_constant_detection`（L646）、`bake_constant`（L684）；结果由 `convert_baker_constant`（L466-542）按 pixel_type（"Rgb_fp"/"Float32<2..4>"/"Sint8"）转进 mi::IColor/IFloat32_x/IBoolean；L691-694 点明 boolean 不可累积强制 samples=1。

**neuray_type_impl.h**：

- 双向 ID 转换函数群（L51-84）：`int_modifiers_to_ext_modifiers`、`int_enum_id_to_ext_enum_id`、`int_shape_to_ext_shape` 等——int=内部（MDL）、ext=外部（neuraylib）两套枚举对照表。
- **wrapper 探针接口**：`IStruct_category_wrapper`（L89）、`IType_wrapper`（L120，`get_internal_type()` 取被包核心对象）、`IType_list_wrapper`（L145）；自由函数 `get_internal_type`（L130）与模板版（L134，借 `get_interface(IID)` 向下转型）。
- 模板基类 `Type_base<E, I>`（L249-287）：`Interface_implement_2<E, IType_wrapper>` **双接口继承**——同时实现公共接口 E 与内部探针；持 Type_factory/内部类型/owner 三个 Handle（L274-276）；`get_kind` 转发 `E::s_kind`（L265）。`Struct_category`（L158）、`Type_alias`（L288）等都从它派生。
- `Type_factory`（L589）：实现 `mi::neuraylib::IType_factory`，`create_alias/create_vector/create_deferred_sized_array/create_texture...`（L621-660）全转发核心 `MDL::Type_factory` 再包装。

## 3. 外部连接；顺带考证 src/api/api/ 双层目录成因

依赖证据：distiller impl include `<mdl/distiller/dist/i_dist.h>`（L43，第 4 篇接口）、`<io/scene/mdl_elements/...>` 三头（L44-46）、`<render/baker/baker/i_baker.h>`（L47）、`neuray_compiled_material_impl.h`/`neuray_transaction_impl.h`（L52-53）；type impl include `<mi/neuraylib/itype.h>` + `<io/scene/mdl_elements/i_mdl_elements_type.h>`（L36-42）。

**为什么是 api/api 双层**：构建证据链——① `src/api/api/mdl/CMakeLists.txt` L30 `set(PROJECT_NAME api-api-mdl)`：target 名就是目录路径 `api/api/mdl` 的连字映射，NVIDIA ARC（原 mental images）内部构建系统"路径即目标名"约定的化石；② `src/api/CMakeLists.txt` 是 2023 年新增薄壳（版权头 2023-2026），仅当 `MDL_BUILD_SDK` 时 `add_subdirectory(${MDL_SRC_FOLDER}/api/api/mdl)`；③ `src/api/api/` 下只有 mdl/ 与 neuray/ 两目录，**neuray 目录没有自己的 CMakeLists**——全部源文件由 api/api/mdl/CMakeLists.txt 以 `../neuray/...` 相对路径（L36-64）统一编进 api-api-mdl 库。结论：外层 `src/api/` 是内部源码树"API 层"根（历史上应有 lib/ 等兄弟子树，开源时剥离），内层 `api/` 才是代码容器——双层是路径命名约定的历史遗留，2023 年开源化选择保留目录加薄壳适配（迁移 70+ 文件路径的成本 > 一层嵌套的认知成本）。①③为构建脚本实证，"历史兄弟子树"为基于命名约定的推断。

## 4. 数据流

distill 链：`distill_material(ICompiled_material*, target, IMap*)` → IMap→Distiller_options（L370）→ wrapper 解包（L385）→ 核心 `DIST::distill`（L400）→ 新核心材质 → `Mdl_compiled_material` 重建（L410）→ `create`+`swap` 重包 API 对象（L419-423）。type 链：核心 `MDL::IType*` → wrapper 转发公共查询，`get_internal_type` 探针随时反向取回。共同模式：**API 对象=核心对象+transaction 生命周期锚的不可变视图**。

## 5. 设计决策

- **wrapper 而非平行实现**：核心类型系统只此一份，wrapper 零拷贝持引用——避免两套类型系统的语义漂移；代价是每次 API 访问多一层虚调用，对低频操作可忽略。
- **双接口 + 探针**（Interface_implement_2，L249）：公共接口保持纯净（集成者不可见内部类型），而 SDK 内部经 `IType_wrapper` 一跳取回核心对象——比 dynamic_cast/全局注册表都轻。
- **trace 事件按需构造**（L402）：`options.trace != 0 || options.debug_print` 才传 event_handler，默认零开销——蒸馏日志海量，条件桥接是性能与可观测性的折中。
- **错误码两段转译**：-1（参数 null）产生于本层，-2/-3 透传第 4 篇核心码——与 i_dist.h L82-84 的契约一一对应。
- **事务 pin/unpin**（L557/L561）：bake 是长操作，pin 防止事务在烘焙中途提交失效——DB 范型下的标准生存期手法。

## 6. 新人提示

- 断言用 `M_NEURAY_API` tag；日志走 `SYSTEM::M_DIST`+`C_COMPILER`。
- `get_required_module_name`（L123-136）的注释值得读：编码名与原名假设一致所以敢直接返回 `const char*`——"线程安全 vs 接口形态"妥协的活标本。
- 调蒸馏问题先开 `_dbg_trace`（L380）：两级日志能直接指出卡在哪条规则。
- 找 mi::neuraylib::IType 的真身：`dynamic_cast` 不行，用 `get_internal_type<T>()` 模板（L134）。
- 相关文件：neuray_compiled_material_impl.h、i_mdl_elements_type.h、第 4 篇 dist 三件套、第 6 篇两个公共头。
