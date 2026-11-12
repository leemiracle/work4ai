# 04 · distiller/dist 三件套 —— distill() 分派、DSO 插件注册表与 "none" 直通

> 文件：`src/mdl/distiller/dist/i_dist.h`（110 行，接口）+ `dist.cpp`（97 行，分派核心）+ `dist_module_impl.cpp`（290 行，插件注册表）；配套 `dist_module_impl.h`。
> 三件合计不到 500 行，却是 MDL "蒸馏"（distilling）体系的中枢骨架。

## 1. 角色定位

MDL 材质是任意复杂的层叠 BSDF 图；游戏引擎等目标平台只认少数"目标材质模型"（如 simplistic 材质的 diffuse/tint/glossy 三槽）。**Distilling = 用规则集把任意 MDL 材质自动改写/近似成目标模型材质**。DIST 模块就是这个转换器的调度中枢：它自己**不做任何规则匹配**，只负责三件事——定义模块接口（i_dist.h）、把 distill() 请求分派给正确的实现（dist.cpp）、维护"哪个 DSO 插件提供哪个 target"的注册表（dist_module_impl.cpp）。真正的蒸馏规则由外部 DSO 插件（典型如 NVIDIA 单独发布的 distiller 插件，规则用 mdltlc 编译）实现，核心仓库保持零规则依赖。

## 2. 内部结构

**i_dist.h —— 接口契约**：`class Dist_module : public SYSTEM::IModule`（L52）声明五组能力：`get_target_count/get_target_name`（L62-65，蒸馏目标枚举）；核心方法 `distill`（L86-92，参数为 call_resolver + event_handler + material_instance + target 名 + Distiller_options + error 码指针）；`get_required_module_count/name/code`（L96-104，目标所需的辅助 MDL 模块，如 `::nvidia::distilling_support`）。错误码契约在 L80-84 注释钉死：0 成功，-1/-2 保留给 API 层，-3 核心通用失败——分层错误码是本体系的关键设计。L71-72 注释强调 `::nvidia::distilling_support` 模块必须先加载（可经 `MDL::load_distilling_support_module`）。

**dist.cpp —— distill() 分派**（`Dist_module_impl::distill` L47-93）：三条路径一目了然——

- **"none" 直通**（L63-66）：`if (strcmp("none", target) == 0)` 则直接 `res = material_instance; res->retain();`——"none" 是唯一 builtin target，语义是恒等变换（返回原材质），让上层管线无需特判"不蒸馏"。
- **插件分派**（L69-83）：`m_target_to_index_map.find(target)` 命中得 `(plugin_index, target_index)` 二元组（L71-72）；经 `SYSTEM::Access_module<MDLC::Mdlc_module>` 取编译器模块（L75-76），`mdl->create_distiller_plugin_api(material_instance, &call_resolver)` 创建操作上下文（L77-78），再 `distiller_plugin->distill(*api, event_handler, material_instance, target_index, options, &error)`（L79-80）；插件返回空则 error=-3（L82-83）。
- **未知名**（L84-86）：error = -2（留给 API 层转译成"未知 target"）。
- 收尾 `TIME::Stopwatch` 计时 + `LOG::mod_log->info(... "Finished 'Distilling' after %f seconds")`（L89-91）。

**dist_module_impl.cpp —— 注册表与生命周期**：

- `Forwarding_logger`（L73-121）：实现 `mi::base::ILogger`，把插件消息按 severity 六级转投 `LOG::mod_log`（L98-119 switch）；L83-93 解析 "MODULE:CATEGORY" 双段式 category，`convert_string_to_category`（L49-70）把 14 个字符串映射到 `Mod_log::Category` 枚举（L50 `mi_static_assert(14 == NUM_OF_CATEGORIES)` 防漂移）。
- 模块自注册（L124）：`static SYSTEM::Module_registration<Dist_module_impl> s_module(M_DIST, "DIST")`；`Dist_module::get_instance()`（L126-128）返回注册入口。
- `is_valid_distiller_plugin`（L130-152）：type 须等于 `MI_DIST_MDL_DISTILLER_PLUGIN_TYPE`（L136），且 `get_api_version() == MI_MDL_DISTILLER_PLUGIN_API_VERSION`（L140）硬校验；版本不匹配发 ERROR 拒绝（L143-149）——DSO 与 SDK 的 ABI 防火墙。
- `init()`（L154-213）：持锁（L155）→ 建 logger（L156）→ **先把 "none" 压入目标表**（L161）→ 遍历 PLUG 模块全部插件描述符（L164-167）→ 合法则 `distiller_plugin->init(m_logger)`（L176）→ 逐 target 注册 `target → (plugin_index, k)` 双索引（L187-189），成功 INFO（L192-198），**重名 target 拒绝并 WARNING**（L199-207）。
- `exit()`（L215-229）：逆序调插件 `exit()`（L218-222），清空三表。
- `get_required_module_*`（L242-285）：三个同构方法——"none" 或未知名返回 0/空，命中则代理给插件（L251 等）。

## 3. 外部连接

i_dist.h 依赖 `<mi/mdl/mdl_generated_dag.h>`（IMaterial_instance 即第 3 篇的 DAG 实例）与 `<base/system/main/i_module.h>`。dist.cpp 引 `mdl/integration/mdlnr/i_mdlnr.h`、`<mi/mdl/mdl_distiller_plugin.h>`（Mdl_distiller_plugin 接口：get_api_version/init/exit/get_target_*/distill）与 `mdl_distiller_plugin_api.h`。dist_module_impl.cpp 依赖 `<base/lib/plug/i_plug.h>`（DSO 枚举）与 `module_registration.h/access_module.h`。调用方唯一：`src/api/api/neuray/neuray_mdl_distiller_api_impl.cpp::distill_material`（其 L400 调 `m_dist_module->distill`，第 5 篇）。插件侧契约在 `include/mi/mdl/mdl_distiller_plugin.h`（L54 `class Mdl_distiller_plugin : public mi::base::Plugin`）。

## 4. 数据流

输入：DAG `IMaterial_instance`（distiller 接口形态）+ target 字符串 + 选项。流：neuray API 层先 `load_distilling_support_module`（注入规则集依赖的 MDL 模块）→ DIST::distill 按 target 查注册表 → 命中插件则 MDLC 模块造 `IDistiller_plugin_api`（DAG 操作句柄 + 名字解析器）→ 插件内部跑规则匹配（IRule_matcher_event 回调报告 path_check/rule_match/postcondition_failed）→ 产出新 DAG material instance。输出：蒸馏后的 `IMaterial_instance` 或 error 码（-2 未知名/-3 失败）。注册表数据流（启动期）：PLUG 模块枚举 DSO → 版本校验 → target→(plugin,target) 双索引表。

## 5. 设计决策

- **核心/规则分离（DSO 插件架构）**：蒸馏规则迭代极快（每年新目标模型），规则留在 SDK 外的 DSO，核心仓库只管调度——与 LLVM pass registry 的设计动机同源。代价是用户必须另装 distiller 插件才有可用 target。
- **"none" 直通**（L63-66）：identity target 让"跳过蒸馏"复用同一 API 路径，管线代码零分支；retain() 而非 clone 也避免无谓拷贝。
- **双索引 map（plugin_index, target_index）**（L187-189）：一个插件可注册多个 target（如 simplistic 不同变体），两级索引让 distill 与枚举都 O(1)，同时天然支持重名检测。
- **API 版本硬门禁**（L140）：DSO 与核心无静态链接，版本不匹配立即拒绝而非运行时崩溃——比"宽松兼容"更安全，因为 distill 产出的 DAG 会被直接送渲染。
- **错误码分层**（-1/-2 API 层 vs -3 核心）：核心不知"用户传 null"这类 API 层错误的存在，接口注释（L82-84）就是两层团队间的契约文档。

## 6. 新人提示

- 第一个坑：**核心仓库 build 出来的 distill 只有 "none" 可用**——`get_target_count()` 返回 1 是正常现象，"simple" 等 target 来自外部 distiller DSO（L161 起的注册循环只在插件存在时扩充列表）。
- 调"target 不认识"错误：先查 `get_target_name(0..n)` 实际注册了什么，再查插件加载日志（"registered distiller target ..." INFO，L192-198）。
- `::nvidia::distilling_support` 未加载时插件规则引用的辅助函数解析失败——上游 API 层已代为处理（第 5 篇 L391），但绕过 API 直接用 DIST 模块就要自己来（i_dist.h L71-72 注释）。
- 改 `Mod_log::Category` 枚举时 `convert_string_to_category` 的 14 连 if 与 L50 static_assert 要同步。
- 相关文件：include/mi/mdl/mdl_distiller_plugin.h（插件作者契约）、mdl_distiller_rules.h（规则集接口）、上游 neuray_mdl_distiller_api_impl.cpp（第 5 篇）。
