# 12 · mdl_browser 与 example_materialx_shared：示例基础设施两件套

## 1. 角色定位

本篇覆盖 examples 的两块基础设施。**mdl_browser** 是 Qt6/QML 材质浏览器（`mdl_browser/` 可执行壳 + `mdl_qt_plugin/` QML 扩展插件，metadata.json 注册名 "MdlQtPlugin"），让用户在包/模块树里浏览、搜索、预览 MDL 材质并选中回传宿主。它的性能命脉是**发现缓存**（`mdl_qt_plugin/cache/`）：把昂贵的 MDL discovery API 结果与材质元数据（缩略图、隐藏注解）持久化成 XML，下次启动增量更新。**`shared/example_materialx_shared.cpp`**（545 行）是 MaterialX→MDL 桥的共享封装：`Mdl_generator` 把 .mtlx 材质经 MaterialX SDK 的 MdlShaderGenerator 翻译成 MDL 源码，被 df_vulkan 与 dxr 两个示例复用——"shared" 目录的典型意义：一份集成代码喂多个示例。

## 2. 内部结构

**缓存接口层** imdl_cache.h（292 行）自述"Base class of the cache hierarchy... Follows the interface style of the MDL SDK"（:12-14）。类层次：`IMdl_cache_item`（imdl_cache.h:57）是基类，Kind 枚举四值 CK_PACKAGE/CK_MODULE/CK_MATERIAL/CK_FUNCTION（:61-67），接口含 entity_name/simple_name/qualified_name 三级命名（:75-83）与通用 key-value 存储（:86-96）；`IMdl_cache_node`（:110）给 package/module 加子表，Child_map_key 是 (kind, name) 二元组（:115-130），哈希函数留有 TODO"换更稳的组合"（:139-141），timestamp 支持增量更新提前终止（:180-182）；四个叶子类 package（:187）/module（:194，含 located_in_archive :200）/material（:216）/function（:223）；`IMdl_cache`（:234）管根、discovery result 与工厂 create()（:253-257）。**实现层** Mdl_cache::update()（mdl_cache.cpp:123）三段式：跑 discovery API 拿包/模块图（:126-135）→ 递归 update 缓存树（:145-147）→ 重建搜索倒排索引（:152）；持久化走 save_to_disk/load_from_disk + XML 序列化器（:176-190，mdl_cache_serializer_xml_impl.cpp）。材质/模块的元数据提取在叶子 update：`anno::hidden()` 注解写 is_hidden（mdl_cache_material.cpp:59-60、mdl_cache_module.cpp:116-117），隐藏性沿树下传（mdl_cache_module.cpp:165-167），缩略图路径取 get_thumbnail()（mdl_cache_material.cpp:108）。**UI 层**：Mdl_browser_tree::build（mdl_browser_node.cpp:45）把 discovery 图+缓存树合成节点树并统计数量（:81-86）；View_model（view_model.cpp:53 起）是 QML 上下文属性 "vm_mdl_browser"（plugin.cpp:98），Qt 信号槽串联导航/选择/过滤（view_model.cpp:160-180）。

**MaterialX 桥**分两类。`Mdl_string_resolver`（example_materialx_shared.cpp:63，继承 `mx::StringResolver`）：initialize() 把 mtlx 文档源路径与 MDL 配置的全部搜索路径去重合并（:78-110）；resolve() 处理两类资源路径——绝对路径找"是它前缀的最高优先级搜索路径"截出相对部分（:118-146），相对路径交给 MDL entity_resolver 验证（:147-163），都失败则打印错误并**返回空串丢弃资源**（:165-172，注释给出替代：拷进搜索路径）。`Mdl_generator`（:197-243 配置 setter 家族 + generate() :249）是主流程：装标准库（m_add_mtlx_std_path 时从示例资源目录 materialx/ 找，:268-277；loadLibraries :290-297）→ 建单位注册表与色彩管理 → `mx::GenContext = mx::MdlShaderGenerator::create()`（:317）→ 挂 ColorManagementSystem/UnitSystem（:332/:356）→ registerTypeDefs 后 generate 出 shader（:508-510）。

## 3. 外部连接

- **MDL SDK**：browser 侧 IMdl_discovery_api/IMdl_package_info（mdl_cache.cpp:128-135）、IMdl_i18n_configuration 的 locale（view_model.cpp:81-96）、Mdl_sdk_helper 封装 neuray 启动；materialx 侧 IMdl_configuration 的搜索路径与 entity_resolver（example_materialx_shared.cpp:100-108/:151-152）。
- **Qt6**：QQmlExtensionPlugin（plugin.cpp:59 registerTypes/:78 initializeEngine）、QML 引擎；信号槽 DirectConnection 保证过滤同步（view_model.cpp:170-180）。
- **MaterialX SDK**：MaterialXCore/Format/GenMdl/GenShader（:35-42），MdlShaderGenerator 是翻译核心——**仓外依赖，需 vcpkg/自备**。
- **消费方**：example_materialx_shared 被 df_vulkan（example_df_vulkan.cpp:3278-3296）与 dxr（mdl_material_description_loader_mtlx.cpp:72-73）引用；mdl_browser 被 DCC 厂商当参考实现。
- **文件系统**：缓存 XML 固定在可执行目录（view_model.cpp:69 "mdl_cache.xml"），设置另存 settings.xml（:65）。

## 4. 数据流

**浏览器启动流**：View_model 构造（view_model.cpp:53）→ new Mdl_cache → 非 rebuild 模式先 load_from_disk（:69-73）→ 比对当前与缓存的 locale，不一致整缓存丢弃重建（:89-96——本地化字符串影响实体名）→ `m_cache->update()`：discovery 全量跑、按 timestamp 增量合并、索引重建（mdl_cache.cpp:123-155）→ save_to_disk 落盘（view_model.cpp:106-109）→ Mdl_browser_tree::build 合成 UI 树（mdl_browser_node.cpp:45）→ QML 界面（Main.qml）导航/搜索/选中，结果经 Mdl_browser_callbacks 回宿主。

**MaterialX 翻译流**：宿主设好路径/库/版本 → generator.generate()：加载 mtlx 标准库与目标文档 → resolver.initialize 同步两套搜索路径 → MdlShaderGenerator 产出 MDL 源码与资源清单 → resolve() 逐个把资源路径翻译成 MDL 搜索路径内相对路径 → Mdl_generator_result 交回宿主 import 进 MDL SDK。

## 5. 设计决策

- **缓存接口仿 MDL SDK 风格**（imdl_cache.h:14）：手写接口类而非直接用 Qt 模型，让缓存层可脱离 Qt 测试、与 SDK API 习惯一致——示例代码也在教架构。
- **locale 失效整缓存弃用**（view_model.cpp:89-96）：宁重算不用错名，交互式程序的正确性优先于启动速度；配合 timestamp 增量把重算成本压回可接受。
- **资源解析失败即丢弃**（example_materialx_shared.cpp:165-172）：resolve 返回空串让 MaterialX 删掉该资源引用，而非让翻译失败——降级保可用，注释还列出"拷进搜索路径"的更优替代，权衡留痕。
- **两套搜索路径合一**（:78-110）：MaterialX 自己的 FileSearchPath 与 MDL 的 mdl_paths 是两个世界，resolver 在初始化时对齐，运行期 resolve 才能零分歧——集成层最典型的"路径缝合"工程。
- **kind+name 复合键**（imdl_cache.h:115-130）：同名可以同时是包和材质（MDL 命名空间允许），Child_map_key 防碰撞；哈希实现自带 TODO 承认不够稳（:139）。
- **共享代码放 shared/**：df_vulkan 与 dxr 的 MaterialX 需求几乎相同，一份 Mdl_generator 双消费，避免两处漂移。

## 6. 新人提示

- browser 调缓存问题先删可执行目录旁的 mdl_cache.xml——陈旧缓存是最常见"材质不显示"原因；locale 切换会自动触发重建（view_model.cpp:89-96）。
- imdl_cache.h 是纯虚接口（无 Qt 依赖），读它比读实现快得多；实现细节按 package→module→material 顺序读 mdl_cache_*.cpp 同名对。
- 加新元数据字段三步：IMdl_cache_item 的 get/set_cache_data 本就支持任意 key-value（imdl_cache.h:86-96），但要在 UI 可见还需动 Mdl_browser_node 与 QML——XML 序列化器自动跟随 key-value。
- MaterialX 集成的坑在路径而非生成器：resolve() 的两条分支（example_materialx_shared.cpp:118/:147）覆盖绝对/相对，但跨盘符或符号链接会掉进 :165 的丢弃分支，先查 stderr 错误行。
- MdlShaderGenerator 属于 MaterialX GenMdl 模块，MDL SDK 不自带 MaterialX——构建示例前确认 vcpkg.json 或手动装库。
- browser 工程只在有 Qt6 环境时可编（CMake 找包失败即跳过），CI 上常被静默排除，别拿它验证 SDK 主体是否编译正常。
- set_materialxtest_mode（:232）是测试钩子，生成确定性输出供回归比对，复用这份代码时可参考其做法。
