# 10 · drawio/graph 转换线：形状库、提示词兼容层与 semantic/visual 双 workflow

> 定位层级：workflow 图构建与提示词资源 → toolkits 工具箱交叉。本篇覆盖 `dataflow_agent/workflow/wf_paper2drawio.py`（318 行）与 `wf_paper2drawio_sam3.py`（2001 行）两条注册线、`promptstemplates/drawio_system_prompt.py`（462 行）、`toolkits/shape_libraries/` 四件套、`toolkits/drawio_tools.py`（586 行）与 `toolkits/image2drawio/`（1270 行），以及 fastapi_app 侧两个 router。

## 一、角色定位

这条线负责把"论文内容/图表图片"变成**可编辑的 draw.io XML**。它有两条平行实现，靠 workflow registry 的别名对区分：

- **semantic 线**（`wf_paper2drawio.py`）：纯文本进出——读论文摘要/文本描述，LLM 规划图表类型（flowchart/architecture/sequence/mindmap/er 五类）再生成 mxCell XML，带 VLM 视觉验证回路；
- **visual 线**（`wf_paper2drawio_sam3.py`）：图片进出——已有架构图或 PDF 首页，经 OCR + SAM3 分割 + 形状分类**逆向重建**为 XML（"图转图元"）。

两条线的注册写法是全仓独有的"双 @register 别名对"：wf_paper2drawio.py:49-50 `@register("paper2drawio")` + `@register("paper2drawio_semantic")`；wf_paper2drawio_sam3.py:1651-1652 `@register("paper2drawio_sam3")` + `@register("paper2drawio_visual")`。同名工厂一次注册两个名字，路由层（fastapi_app/routers/paper2drawio.py:57 `/generate`、:108 `/chat`、:133 `/export`）按用户选的模式取对应别名。

## 二、内部结构

### 2.1 形状库四件：文档资产而非运行时数据

`toolkits/shape_libraries/` 下四个 markdown：**aws4.md（1049 行，Shapes 1032 个）**、**azure2.md（431 行，Shapes 648 个）**、gcp2.md（315 行）、kubernetes.md（58 行）。每件开头自述类型与用法：aws4 是 `Type: mxgraph shapes`、前缀 `mxgraph.aws4`（aws4.md L3-4），示例给 `shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{shape}` 的 mxCell 模板（L7-10）；**azure2 是四件中唯一的 `Type: SVG images` 型**（azure2.md L3-4，路径 `img/lib/azure2/`，用 `image=img/lib/azure2/{category}/{shape}.svg` 样式引用），且**在 Python 代码里零引用**——drawio_system_prompt.py 只把 aws4（L180-195）与 gcp2（L220-229）的常用形状硬编码进了云架构提示词，azure2/kubernetes 的清单没有任何消费者。注意：整个 shape_libraries 目录**没有 Python 读取者**（全仓 grep 零命中）——它们是给人和 LLM 看的参考资料（附录式 few-shot 素材），不是程序加载的数据文件。

### 2.2 drawio_system_prompt：三段提示词 + 兼容层

`promptstemplates/drawio_system_prompt.py` 头注直说"移植自 next-ai-draw-io 项目"（L2-3），是外部血统的提示词模块。三段核心常量：`DIAGRAM_PLANNER_PROMPT`（L9 起，规划器）、`DRAWIO_XML_GENERATOR_PROMPT`（L26 起，生成器铁律：只产出 mxCell 元素、禁止 wrapper 标签 `<mxfile>/<mxGraphModel>/<root>`、id 从 "2" 起连续编号、parent 挂 "1" 或容器 id、默认 ≤12 节点），以及云架构扩展段（L160 起的 CLOUD_ARCHITECTURE_PROMPT，内嵌 aws4/gcp2 形状速查）。函数式入口有三个：`get_planner_prompt`（L337，按 language 追加中文/英文指令）、`get_generator_prompt`（L343，`include_cloud_icons` 拼接云图标段、`minimal_style` 前置极简风格模式）、`get_editor_prompt`（L365）。

**模板系统兼容层**在 L371-372：注释明写"模板系统兼容性 - 按照 PromptsTemplateGenerator 的命名约定"，把上述常量按 `system_prompt_for_X` / `task_prompt_for_X` 成对命名再暴露一遍（diagram_planner/drawio_xml_generator/diagram_editor/drawio_vlm_validator 四组，加 `DRAWIO_VLM_VALIDATOR_PROMPT` L436）。消费方式很特别：`promptstemplates/prompts_repo.py` L2448 起的 `class DrawioPrompts` **在类体内直接 `from dataflow_agent.promptstemplates.drawio_system_prompt import ...`**（L2451-2460 八个名字）——用"类命名空间"当模板容器，导入即成为类属性，省去一层赋值。这是仓内提示词体系的双轨：函数式（get_*）与常量对式（*_for_*）并存，各自服务不同调用方。

### 2.3 semantic 线图结构（wf_paper2drawio.py）

`create_paper2drawio_graph()`（L51）用 `GenericGraphBuilder`（L60，state_model=Paper2DrawioState）搭一张小图：节点字典 L301-307（`_start_`/diagram_planner/drawio_xml_generator/diagram_editor/`_end_`），静态边 L309-313（planner→generator→end、editor→end），入口条件路由 `_route_entry`（L294-299）：请求里同时有 `edit_instruction` 与已有 `drawio_xml` 就走编辑模式进 diagram_editor，否则从 planner 全新生成。planner/generator 节点由 `create_simple_agent`/`create_react_agent` 工厂构造（L29 导入），generator 之后有 VLM 验证回路（L240-277 附近）：渲染成图→VLM 按 validator 提示词检查重叠/连线穿模/箭头方向→不过则把 `validation_feedback` 回填给生成器重试。取数函数族 `_get_paper_content`/`_get_text_content`/`_get_diagram_plan` 等（L68-137）统一处理 state 的多来源字段缺省。

### 2.4 visual 线：SAM3 五步流水线（wf_paper2drawio_sam3.py）

2001 行的 `create_paper2drawio_sam3_graph()` 文档头写明五步（L1-13）：①载入输入图（`_input_node` 支持 image 路径、PDF 首页渲染 `_render_pdf_first_page` L845、text_content 兜底三种入口）→ ②VLM OCR 文本提取（qwen-vl-ocr-latest，`_text_node` 取 OCR credentials）→ ③SAM3 text-prompt 分割（HTTP 服务，"ported from Edit-Banana/sam3_service"）→ ④形状/图标分类 + 颜色采样 → ⑤渲染 draw.io XML。几何后处理调参集中在 L158-166：`SAM3_IMAGE_RECALL_SCORE_THRESHOLD=0.35`、去重 `SAM3_DEDUP_IOU=0.65`、箭头去重 0.80、形状-图像 IoU 0.55 等；工具函数族 `_bbox_to_polygon`/`_vectorize_text_blocks`/`_build_mxcell`（L761/775/923）把检测框变成 mxCell。SAM3 的 HTTP 客户端由 toolkits 侧 `get_sam3_client` 提供（L44 导入），服务端就是第 09 篇讲的 start_model_servers 舰队。

### 2.5 drawio_tools 与 image2drawio 工具包

`drawio_tools.py` 是 XML 卫生层：`wrap_xml`（L30，把 mxCell 片段包进标准 wrapper，默认页 850x1100）、`extract_cells`（L58，反向剥离只留 cells——配合生成器"只产 mxCell"的约定）、`validate_xml`（L88，结构校验返回问题清单）、`sanitize_cells_xml`（L136，清洗模型输出里的注释/markdown 围栏）、`export_drawio_png`（subprocess 调 drawio CLI 导出图片，供 VLM 验证用）。`image2drawio/` 包（1270 行）是评测与修复线：metric_evaluator.py（692 行）的 `evaluate`（L100）用 bbox IoU/覆盖掩码算重建质量（L47 `_bbox_iou`、L193 `_create_content_mask`、L226 `_create_covered_mask`），refinement_processor.py 的 `refine`（L55）做白块/纯文本区域的启发式修整（`_is_mostly_white` L216、`_is_mostly_text` L237）。

## 三、外部连接

- **上游入口**：`fastapi_app/routers/paper2drawio.py`（generate/chat/export 三端点）与 `image2drawio.py`（`/image2drawio/generate` L21），服务层 paper2drawio_service.py/image2drawio_service.py 负责按 workflow 名取图。
- **agent 层**：`agentroles/paper2any_agents/drawio_xml_generator.py` 的 `DrawioXmlGenerator`（L23 起）是 generator 节点的人格化封装，解析 LLM 多形态输出（L145-147 dict 的 text/xml/drawio_xml 三键兜底）。
- **模型服务**：visual 线依赖 OCR API 与 SAM3 HTTP 服务（deploy 侧 8021 端口舰队）；semantic 线的 VLM 验证依赖多模态模型。
- **血统**：系统提示词与 SAM3 服务分别移植自 next-ai-draw-io 与 Edit-Banana/sam3_service（两处 docstring 钉版）；`workflow/deprecated/wf_image2drawio.py` 是被 visual 线取代的旧 image2drawio workflow，已入档 deprecated 目录。

## 四、数据流

semantic 线：`Paper2DrawioState`（含 paper_file/text_content/diagram_type/edit_instruction 等多来源输入）→ planner（LLM 出结构化计划 JSON）→ generator（按计划产 mxCell 片段，云图标可选）→ wrap_xml 包壳 → export_drawio_png 渲染 → VLM 验证（valid/issues/suggestions JSON）→ 不过则带 feedback 回 generator，过则落盘 .drawio。visual 线：输入图/PDF 首页 → OCR 出文本块坐标 → SAM3 按文本提示分割出形状实例 → 分类着色 → `_build_mxcell` 逐块转 XML → metric_evaluator 可选评测（与原图算 IoU/覆盖率）→ refine 修整。两条线输出同一格式（draw.io XML 文件），在 router 层对用户呈现为同一产品的两种模式。

## 五、设计决策（含批判）

1. **双别名注册是务实的模式开关**：semantic/visual 两条线共享 state 模型与 registry 机制，`@register` 双名让路由层用字符串选实现，不用 if/else 分叉代码。批判点：别名对的第二名字（_semantic/_visual）只在注册表里活着，代码文件名带 sam3 而注册名带 visual，新人按文件名找 "visual workflow" 会先撞墙。
2. **形状库是"给 LLM 的百科"却无人加载**：1032+648+若干形状的四件 markdown 静静躺着，实际进提示词的只有 aws4/gcp2 的几十个精选（硬编码在 CLOUD_ARCHITECTURE_PROMPT）。azure2 作为唯一 SVG 型还整库零引用——SVG 型需要 `img/lib/` 图片资产配合（托管环境才有），纯 XML 生成线用不上它，这解释了零引用的成因，但也说明这批资产对开源用户基本是死重。
3. **类体内 from import 的兼容层**：prompts_repo.py DrawioPrompts 在 class 语句里直接 import 八个常量（L2451-2460），模板即类属性。写法紧凑但反直觉——类体执行 import 依赖导入顺序，且 grep "DrawioPrompts.X" 的人会困惑属性从哪来。兼容层本身（L371 命名约定）是典型的"新模块迁就旧模板系统"的过渡态，迁移完成后理应收敛到 get_* 函数一族。
4. **生成器只产 mxCell 的契约**：禁止 wrapper/root、id 从 2 起、cells 互不嵌套（DRAWIO_XML_GENERATOR_PROMPT CRITICAL RULES）——这个约定把"模型输出不可信"的防御前移到提示词层，代码侧再用 extract_cells/sanitize 兜底，双层防线是处理 LLM 产 XML 的正确姿势。
5. **visual 线调参硬编码**：SAM3 召回阈值、三档 IoU、最小面积比全部字面量写死在 L158-166，没有走 config。对论文复现友好（数字就在眼前），但对不同分辨率/风格的输入图缺乏弹性。
6. **2001 行单文件**：visual 线把 IO、OCR、分割、分类、渲染、评测耦合在一个 workflow 文件里（工具函数已尽力前置下划线分组），是全仓第二大 Python 文件，改任何一环都要在巨文件里穿行。

## 六、新人提示

- 读线顺序：先 `drawio_system_prompt.py` 全文（462 行，读懂契约）→ `wf_paper2drawio.py`（318 行，看懂 semantic 图）→ 再啃 `wf_paper2drawio_sam3.py`（按 L1-13 的五步 docstring 当目录，跳读对应函数）。
- 找"visual 模式"代码别搜 visual，搜 sam3；注册名与文件名不一致（见第 5 节第 1 条）。
- 想加新云厂商形状：改 CLOUD_ARCHITECTURE_PROMPT（drawio_system_prompt.py L160 起的段落）而不是 shape_libraries/*.md——后者没有运行时消费者，改了白改。
- XML 输出可疑时先用 drawio_tools.validate_xml 单测片段；模型输出常混 markdown 围栏，sanitize_cells_xml 会剥，但自己写解析时别忘了这层。
- 复现 visual 线需要先起 SAM3 服务（script/start_model_servers.sh）并配好 OCR API 凭据（`_text_node` 的 get_ocr_api_credentials），缺一会导致空文本块静默降级——日志里搜 "[paper2drawio_sam3]" 前缀。
- image2drawio 的评测线（metric_evaluator/refinement_processor）可独立于 workflow 使用，测试参考 `tests/paper2expfig_test/` 与 `tests/sam3/`。
