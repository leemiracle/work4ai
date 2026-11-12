# 08 · postertool：LangGraph 七节点学术海报流水线

> 定位层级：toolkits 工具箱 → postertool LangGraph 海报流水线。本篇覆盖 `dataflow_agent/toolkits/postertool/` 全目录（约 4527 行 Python + 10 个 prompt 模板 + 字体资源），是仓内唯一一条 LangGraph 状态图流水线，与主框架 dataflow_agent 的自研 workflow 引擎并行存在。

## 一、角色定位

postertool 负责"论文 PDF → 单页学术海报（PPTX）"。它的血统独立：不是用本仓 dataflow_agent 自己的 workflow 基类（`dataflow_agent/workflow/` 那套），而是直接建在 **LangGraph StateGraph** 上——`src/workflow/pipeline.py:29` `from langgraph.graph import StateGraph, START, END`。整条流水线是纯线性七节点链，无循环无分支，LangGraph 在这里只被当作"节点编排器"用，条件边、检查点等高级能力一概未用。上游入口是 `fastapi_app/services/paper2poster_service.py` 与 `script/paper2poster_worker.py`，测试线在 `tests/test_paper2poster_*.py` 四件（parser/renderer/curator/outputs）。

## 二、内部结构

### 2.1 七节点流水线（pipeline.py:36-52）

`create_workflow_graph()`（L31）注册七个节点并连成直线：

```
START → parser → curator → color_agent → section_title_designer
      → layout_optimizer → font_agent → renderer → END
```

节点注册在 pipeline.py L36-42，边在 L45-52，一一对应 `add_edge`，无一条条件边。各节点文件与体量：

| 节点 | 文件（src/agents/） | 行数 | 职责 |
|---|---|---|---|
| parser | parser.py | 767 | PDF→文本/图表提取、ABT 叙事、视觉分类、章节结构化（4 个 LLM 调用） |
| curator | curator.py | 481 | 空间内容规划（story_board）、列利用率分析 |
| color_agent | color_agent.py | 348 | logo 主题色提取、图表配色适配 |
| section_title_designer | section_title_designer.py | 130 | **纯代码色块标题设计，零 LLM** |
| layout_optimizer | layout_with_balancer.py | 93 | 三阶段布局编排（见 2.3） |
| font_agent | font_agent.py | 338 | 关键词提取、字号分级 |
| renderer | renderer.py | 794 | python-pptx 落盘（L10 `from pptx import Presentation`） |

**section_title_designer 是七节点中唯一不调 LLM 的**：文件头注释直说 "Fixed style for current version"（L1-4），`__call__` 里日志写明 "code-based, Style 2 only"（L22），`_generate_colorblock_design`（L49 起）拿 curator 的 story_board 和 color_agent 的 color_scheme 做确定性色块排版。它是"占坑等 LLM 化"的节点——接口对齐其余六节点（吃 PosterState 吐 PosterState），未来换实现零改动。

### 2.2 poster_state：单一状态字典

`src/state/poster_state.py` 用 TypedDict 定义全流水线唯一状态 `PosterState`（L29-143）：路径三元组（pdf_path/output_dir/poster_name）、双模型配置（text_model/vision_model，`ModelConfig` dataclass L9-13）、以及按节点递进的结果槽位——parser 产出 narrative_content/classified_visuals/structured_sections，curator 产出 story_board，color_agent 写 color_scheme，section_title_designer 写 section_title_design，layout 线写 design_layout，最后 renderer 消费全部。`TokenUsage`（L16-27）分文本/视觉两通道各记 input/output 四个计数器，layout 三阶段汇总时 `add_text` 累加（layout_with_balancer.py:60-63）。这是教科书式 LangGraph 共享状态模式：节点间不传消息、只改字典。

### 2.3 layout_optimizer 的三阶段套娃

pipeline.py:21 `from src.agents.layout_with_balancer import layout_with_balancer_node as layout_optimizer_node`——节点名与实现名错位。`LayoutWithBalancerAgent.__call__`（layout_with_balancer.py:19-67）内部编排三阶段：phase 1 `self.layout_agent(state, mode="initial")` 产初始布局 → phase 2 `self.balancer_agent(...)`（balancer_agent.py，146 行）做列利用率平衡 → phase 3 `self.layout_agent(initial_state, mode="final")` 收尾。也就是说图上的一个节点实际是 LayoutAgent→BalancerAgent→LayoutAgent 三连 LLM 调用。

### 2.4 langgraph_utils：七 provider 模型工厂

`utils/langgraph_utils.py`（317 行）是流水线的模型层：`create_model`（L22）按 `ModelConfig.provider` 分发到 **七家 provider**——openai（L34）、anthropic（L50）、google（L66）、zhipu（L82）、moonshot（L105）、minimax（L121）、alibaba（L137），每家都支持 `*_BASE_URL` 环境变量覆盖。`LangGraphAgent`（L168）封装 system_msg+config 的对话体，`step`（L182）挂 tenacity 重试装饰器（L181 `@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=10))`），`_step_vision`（L230）走多模态分支；`extract_json`（L280）做 LLM 输出的 JSON 抽取，`load_prompt`（L309）读模板文件。配置面在 `config/poster_config.yaml` + `src/config/poster_config.py`。

## 三、外部连接

- **宿主框架**：postertool 位于 `dataflow_agent/toolkits/` 下，与 drawio_tools、multimodaltool（MinerU）并列；parser 的文本提取直接 import `dataflow_agent.toolkits.multimodaltool.mineru_tool`（parser.py:19），MinerU HTTP 失败回落 PyMuPDF（parser.py:136-145 `_extract_raw_text` 的 try/except 结构）。
- **服务入口**：`fastapi_app/routers/paper2poster.py` → `paper2poster_service.py`；独立运行走 `script/paper2poster_worker.py` 与 `script/run_paper2poster_cli.py`。
- **资源**：fonts/ 下 Arial.ttf、HelveticaNeue.ttf 供 renderer/font_agent 度量（`src/layout/text_height_measurement.py`）；`.env` 由 pipeline.py:25-26 `load_dotenv(override=False)` 加载。

## 四、数据流

PDF 进入 parser 后先产出三份 JSON（narrative_content/classified_visuals/structured_sections，落盘在 output_dir/content/，parser.py:93-95），curator 把章节内容规划进三栏 story_board 并给出 column_utilizations（curator.py:362 空章节时返回 warning），color_agent 从 logo/图表提取主题色板，section_title_designer 确定性生成标题色块，layout_optimizer 三阶段产出 optimized_story_board 与 final design_layout（layout_with_balancer.py:46-47 写回状态、`_save_balancer_output` L69 落盘 optimized_story_board.json），font_agent 定字号层级，renderer 逐元素绘制成 16:9 页面并写 PPTX。所有节点失败都走同一约定：捕获异常、`state["errors"].append(...)`、原样返回状态（见 section_title_designer.py:42-44），错误在状态字典里"传染"到下游，流水线不中断。

## 五、设计决策（含批判）

1. **占位符双机制（必收录坑）**：同一个目录的 prompt 模板存在**两套互不兼容的占位符语法**。`layout_balancer.txt` 用 Python `str.format` 单花括号（L4-8 `{left_utilization}`、L71 `{structured_sections}`），消费方 balancer_agent.py:49 `self.balancer_prompt.format(**variables)`；其余全部模板用 **Jinja2 双花括号**（extract_title_authors.txt:18 `{{ markdown_document }}`、classify_visuals.txt:4、extract_keywords.txt:4-5、extract_structured_sections.txt:4 等），消费方是 parser.py:16 `from jinja2 import Template` 加四处 `Template(...).render(...)`（parser.py:270/592/649/715）与 curator.py:98。踩法：往 layout_balancer.txt 里写 JSON 示例（天然带 `{}`）会当场 KeyError/IndexError；反过来把 Jinja2 过滤器写进单花括号模板则静默不渲染。两套机制并存纯属两拨代码各自演化未被归一。
2. **sys.path.insert 隐式包根**：pipeline.py:13 `sys.path.insert(0, str(Path(__file__).parent.parent.parent))` 把 postertool/ 根塞进 sys.path，于是全目录的 import 都是 `from src.state.poster_state import ...`、`from utils.src.logging_utils import ...`（pipeline.py:20-27）——`src` 和 `utils` 不是安装包而是**目录名直接当顶层包**。这要求必须从 pipeline.py 这一个入口先执行（或同样 insert）才能 import 任何 agent；任何想以 `dataflow_agent.toolkits.postertool.src.agents.parser` 正规路径引用的尝试都会因其内部绝对导入而失败。工具独立性（自带 pyproject.toml，可脱离主仓安装）与主仓集成之间的妥协，代价是主仓测试只能走 worker/CLI 间接驱动。
3. **LangGraph 用法极保守**：七节点纯线性 + 共享 TypedDict，用循环也能表达。选 LangGraph 的实际收益只有状态类型约束与可视化拓扑；批判地看，`dataflow_agent/workflow/` 主框架已有编排能力，postertool 另起炉灶是"仓中仓"——七 provider 工厂、重试、JSON 抽取这些 langgraph_utils 里的轮子，在主框架 llm_callers/ 下都有对应物。
4. **GPT-4o-image_generation.txt 死资产**：`config/prompts/GPT-4o-image_generation.txt` 是一份"GPT-4o 直接端到端生成 1536x1024 海报单图"的巨型提示词（要求内容忠实、结构完整、header 含标题作者），但全目录零 Python 引用——它属于更早的"单模型一步出图"技术路线的遗物，后被七节点流水线取代却未删除，对读代码的人是误导（会以为有图像生成通道）。
5. **错误处理的"带病前行"**：节点错误只 append 进 state["errors"] 不抛出，优点是流水线总能跑到 renderer 看到半成品，缺点是上游脏数据会引发下游难解的二次错误（例如 story_board 缺失时 section_title_designer.py:30-31 才 raise ValueError 进 errors）。

## 六、新人提示

- 入口读 `src/workflow/pipeline.py` 全文 166 行即可拿到整图；再按 2.1 表格挑一个 agent 精读（推荐 curator：既有 Jinja2 填充又有列分析）。
- 改 prompt 模板前先看它是哪种花括号：`grep '{{' <file>` 有输出走 Jinja2/`Template().render()`，无输出且见 `{xxx}` 走 `.format()`。JSON 示例进 `.format()` 模板必须把字面 `{`/`}` 转义成 `{{`/`}}`——这正是双机制最容易炸的点。
- 本地跑通优先用 CLI：`script/run_paper2poster_cli.py`，模型选择靠 `ModelConfig(provider=...)` 加对应 `*_BASE_URL` 环境变量；`.env` 放 postertool/ 根（pipeline.py:25 的路径）。
- 断点排查看 output_dir/content/ 下的中间 JSON（narrative_content/optimized_story_board 等），每个 agent 都把中间产物落盘，这是没有检查点机制下的"穷人版 checkpoint"。
- 测试在 `tests/test_paper2poster_{parser,renderer,curator,outputs}.py`，注意它们驱动方式受 sys.path 机制约束（见第 5 节第 2 条）。
