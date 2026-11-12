# 06 · workflow 图家族：注册中心、18+ 活跃图与 trajectory 子系统

## 角色定位

`dataflow_agent/workflow/` 是框架的"程序层"：每条产品线的执行流程在这里被声明为一张 LangGraph 状态图——节点函数消费/产出 State dataclass（04 篇），边的条件路由决定分支。它与 promptstemplates（"数据层"，2460 行 prompts_repo 总仓 + 14 个 pt_* 专属 repo + drawio 四阶段 prompt 库）合成 dataflow 的"程序与数据"。03 篇的 FastAPI services 与 wa_* 适配器最终都汇到本篇的 `run_workflow` 单一入口。这里是理解"一条论文转换线到底分几步"的最终答案。

## 内部结构

**注册中心与动态装配（workflow/__init__.py 70 行 + registry.py 35 行）**：`RuntimeRegistry`（registry.py:7-28）以 `@register("name")` 装饰器收集各图的 `create_*_graph` 工厂函数（registry.py:32-35），重名异体抛错。装配侧是**importlib + glob 动态发现**：`_workflow_module_names()` 用 `Path.glob("wf_*.py")` 枚举全部图模块（__init__.py:13-17），`_import_workflow_modules_until(name)` 惰性逐个 import（__init__.py:20-39）——注释自述动机：启动期全量 import 会拉起 torchvision/transformers 让后端"假死"（L23-28），所以**按需加载到目标注册名出现即停**。对外三接口：`get_workflow(name)`（L42-53）、`run_workflow(name, state)`（L56-63，工厂→builder→build→ainvoke 四连）、`list_workflows()`（L68-70，唯一会全量 import 的入口）。

**活跃图 19 个文件、21 个注册名（实测）**：顶层 19 个 wf_*.py——kb 六件（deepresearch/mindmap/page_content/podcast/report/intelligent_qa）、paper2 线（drawio/drawio_sam3/figure_image_only/figure_with_sam/expfigure/page_content/page_content_for_long_paper/poster/technical/citation/ppt_parallel_consistent_style/video）、转换线（pdf2ppt_qwenvl/image2drawio）等。**双注册遗留**：wf_paper2drawio.py:49-50 连续两个 `@register("paper2drawio")` + `@register("paper2drawio_semantic")` 给同一工厂两个名字（wf_paper2drawio_sam3.py 同样双注册）——别名期兼容手法，21 注册名 > 19 文件的原因。

**GenericGraphBuilder 状态机 API（graphbuilder/graph_builder.py 148 行）**：链式建图 DSL——`add_node(name, func, role)`（L58-63）把节点注册为 `(func, role)` 二元组；`add_nodes` 批量 + role_mapping（L64-67）；`add_edge/add_edges` 直边（L69-77）；`add_conditional_edge(s)` 条件路由（L79-87，src→cond_func）。**AOP 包装是隐藏核心**：`build()`（L132 起）先用 `_wrap_node_with_tools`（L117-129）把每个节点包成"先注册该角色 pre/post 工具→再执行原函数"的 wrapped_node，再灌进 `StateGraph(state_model)`——这就是 04 篇 @pre_tool/@post_tool 钩子的落地点；`_register_tools_for_role` 还带 `override=True` 的 try/except TypeError 兼容（L102-112）。典型用法见 wf_kb_deepresearch.py:146-154：`GenericGraphBuilder(state_model=KBDeepResearchState, entry_point="_start_")`。

**wf_paper2video.py 巨型工厂（实测 1040 行）**：视频线全链在一个 `create_paper2video_graph`（L164）闭包里。结构是"getter 家族 + 节点函数 + 条件路由"：十来个状态读取闭包（get_markdown L176、get_images_relative_path L200、get_language L214、get_is_code_wrong L223、get_beamer_code L235……），节点函数依次是 extract_pdf_node（L270 PDF→图片）、compile_beamer_node（L292 LaTeX 编译）、beamer_code_debug_node/beamer_code_upgrade_node（L301/L313 编译失败时的调试/升级循环）、subtitle_and_cursor（L391 字幕+光标轨迹）、refine_subtitle_and_cursor（L459 精修）、generate_speech（L507 双 TTS 语音合成）、generate_talking_video（L635 数字人对口型视频）；另有 _build_fallback_slide_script（L131）等降级路径。**它是唯一被 run_workflow 特判的图**：`if name == "paper2video": return await run_paper2video_via_subprocess(...)`（__init__.py:57-58）——重计算隔离到子进程（paper2video_subprocess.py + script/ 的 video worker），防 LaTeX/ffmpeg/数字人链拖垮 API 进程。

**deprecated/ 七件**：wf_image2drawio、wf_image2ppt、wf_paper2ppt_parallel、wf_pdf2ppt_optimized、wf_pdf2ppt_parallel、wf_pdf2ppt_with_sam_ocr_mineru、wf_websearch_knowledge_store——pdf2ppt 三代并行方案与 websearch 知识库存档。**注意 glob 只扫顶层**（`_pkg_path.glob("wf_*.py")` 不递归），deprecated 目录天然不注册，是"物理隔离"式停用而非删除。

**trajectory 子系统（trajectory/ 六件 1778 行）**：collector（387 行采集）→ builder（314 行构建）→ models（381 行数据模型）→ manager（308 行）→ exporter（354 行导出 JSON/JSONL/统计）。**load_from_json 是自认的半成品**：exporter.py:287-302 打开 JSON 后注释直书"这里需要实现从字典重建 Trajectory 的逻辑 / 简化版本：直接返回字典"——返回类型标注 `-> Trajectory` 实际返回裸 dict，消费方拿到的对象类型与签名不符。导出方向（轨迹→JSON）完整可用，回读方向留白；tests/test_trajectory.py 只覆盖正向。

**promptstemplates（图的"数据"半边）**：prompts_repo.py 2460 行总仓（含 WebAgentPrompts 等 9 个 Prompts 类族，L1266-1269 起）、drawio_system_prompt.py 四阶段英文 prompt 库、resources/ 14 个 pt_* 专属 repo、prompt_template.py 基础设施；配合 templates/ 7 个 jinja（04 篇 dfa create）与新图脚手架闭环。

## 外部连接

- **上游调用**：03 篇全部 wa_* 适配器与 kb 路由的 `run_workflow`（kb.py:22）→ 本篇 __init__.py:56；paper2video 线走 heavy_workflow_subprocess + script/paper2video_worker。
- **LangGraph**：GenericGraphBuilder.build 产出 langgraph StateGraph；postertool（L11 层的独立 LangGraph 海报流水线，七节点 StateGraph 自建）是同范式的旁支。
- **agentroles（04/05 篇）**：节点函数内部实例化 41 角色之一（如视频线调 p2v_* 七 agent、检索线调 websearch 四件套）。
- **promptstemplates**：节点内 agent 的 prompt 按 role_name 寻址 pt_* repo。
- **trajectory**：collector 挂在 BaseAgent 执行路径上采集步级轨迹（models/manager 支撑），供训练数据导出——但 FastAPI 层零引用（grep 实证），当前仅 CLI/测试可达。

## 数据流

一次工作流执行：HTTP → service 构造 Request → `run_workflow(name, state)` →（paper2video 特判子进程）→ `_import_workflow_modules_until(name)` 惰性加载到目标图注册 → `get_workflow` 取工厂 → `factory()` 得 GenericGraphBuilder → `build()`：StateGraph(state_model) + AOP 包装节点 + 直边/条件边 + entry_point → `graph.ainvoke(state)` → 节点链按 State 字段流转（每节点进前自动挂角色工具钩子）→ 终态写 outputs/ → 产物路径回传。视频线独有循环：compile 失败 → is_code_wrong → beamer_code_debug → 再编译 → 仍败 → beamer_code_upgrade 升级方案；成功后字幕→语音→数字人串行。

## 设计决策（含批判）

1. **惰性 import 是启动性能的关键补丁**：19 图全量加载会拉起 torch 系重依赖（注释自述"backend look dead for a long time"，__init__.py:24-28）；按需加载把冷启动从分钟级压到秒级。代价是 `list_workflows()`（管理/文档场景）仍要付全量代价，且首个请求命中未加载图时有加载抖动。
2. **glob 动态装配是双刃剑**：新图零登记自动被发现（加文件即生效），但**名字拼写错误的图会静默不存在**——没有静态检查保证 wf_*.py 里的 @register 名与调用方字符串一致；RuntimeRegistry 只在重名时报警，不在"查无此名"时给编译期信号。
3. **双注册别名是过渡态债**：同一工厂挂 paper2drawio/paper2drawio_semantic 两名（wf_paper2drawio.py:49-50），调用方分裂成两种叫法后别名就删不掉了；新图应坚持一名一图。
4. **wf_paper2video 1040 行闭包工厂是"巨型但自洽"**：getter/节点/路由全部闭包在 create 函数内，状态经闭包共享——比散装全局函数内聚，但无法单测单个节点（闭包不可注入），且实测 1040 行与任务书认知 852 行有出入，说明该文件仍在活跃膨胀。run_workflow 的硬编码特判（__init__.py:57-58）则是"一条图破坏了统一接口"的信号：更优解是注册时声明执行模式（inproc/subprocess），而非 if 名字。
5. **deprecated 物理隔离优于删除存档**：glob 不递归天然屏蔽，比 03 篇那 509 行全注释文件高明——不污染源码可读性，git 历史仍可考古。
6. **trajectory 半成品类型撒谎**：`load_from_json -> Trajectory` 实返 dict（exporter.py:298-302），任何按类型注解写的消费代码都会在运行期踩属性错；要么补全重建逻辑，要么诚实地改成 `-> dict`。整个子系统当前无生产调用方，属"预埋的训练数据管道"。
7. **AOP 工具注册藏在 build 里**：节点执行前自动挂角色工具（graph_builder.py:117-129）对图作者透明——好处是图代码干净，坏处是调试时"工具从哪来的"这个问题答案在框架深处；新人排查工具行为异常要同时看图定义与 pre/post_tool 注册表。

## 新人提示

- 新建一条产品线：`dfa create` 生成 workflow.py.jinja 骨架 → 在文件内 `@register("your_name")` + `create_xxx_graph()` 返回 GenericGraphBuilder（state_model 指向 04 篇 state.py 的成对 dataclass）→ 文件落 workflow/ 顶层即自动装配，**别放 deprecated/**。
- 查"某条线到底分几步"：直接开对应 wf_*.py 读 add_node 序列 + add_conditional_edges 路由表；kb 六件最短（百行级），视频线最长（1040 行）。
- run_workflow 报 KeyError 时先 `from dataflow_agent.workflow import list_workflows; list_workflows()` 看真实注册名——字符串名与文件名不一一对应（双注册/别名）。
- 调试工具钩子：看 GenericGraphBuilder 的 pre_tool_registry/post_tool_registry（graph_builder.py:26-27）与图的 @pre_tool 声明，工具不是 agent 自带就是图级注入。
- trajectory 只可正向用：export JSON/JSONL 完整可用，load_from_json 返回 dict 不是 Trajectory（exporter.py:287），别按注解写下游。
- 部署慢排查第一嫌疑：某个 service 顶层 import 触发了全量图加载（拉起 torch）；正确姿势是只 import run_workflow 惰性入口。
