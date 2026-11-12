# 05 · toolkits 工具箱：模型服务、多模态、检索与算子

## 角色定位

`dataflow_agent/toolkits/` 是 agent 的"手"——BaseAgent（04 篇）负责思考，本层负责与外部世界打交道：起模型服务、发 OCR/VLM 请求、搜网页、查引文、下载 arXiv、执行沙箱代码。子目录十三个，可归并为七大块：**model_servers（模型服务托管）、multimodaltool（多模态 16 件，含 MinerU 与 OCR）、sam3（分割服务）、websearch 线（agentroles 四件套 + WebAgent）、optool（算子工具）、citationtool（三源引文）、rebuttal（审稿工具）**。它同时是国产硬件适配与上游 DataFlow 血统残留最集中的一层。

## 内部结构

**model_servers（6 件）**：四个自建推理服务 + 一个负载均衡。sam3_server.py（315 行）托管文本提示分割模型，核心是 **LRU 状态缓存**——`state_cache: OrderedDict`（sam3_server.py:141）+ asyncio.Lock（L142），命中即 `move_to_end`（L146-149），默认容量 2（L126 `cache_size: int = 2`）：SAM3 对同一图片的多轮交互（点击/框选累积）复用编码状态，避免重复编码。sam_server、ocr_server、miner_server 各自独立起 FastAPI 小服务；generic_lb.py（78 行）是**轮询负载均衡 proxy**（L17 `async def proxy(request, path_name)`），把请求转给 mineru_server.py 里配置的后端 URL 列表（mineru_server.py:67-74 `--backends` 参数，"No backends configured" 503 兜底）。

**GPU 三通道发现（script/start_model_servers.sh，服务启动侧）**：`discover_available_gpus`（start_model_servers.sh:148-191）按序尝试四路——①manual：`SAM3_GPUS_RAW` 环境变量直读（L149-153）；②`nvidia-smi --query-gpu`（L163-166）；③**mx-smi 沐曦国产适配**（L156-157 由 `DEPLOY_TARGET=muxi` 自动选中，L167-174 `mx-smi -L | awk '/^GPU#[0-9]+/ && /Available/'` 解析可用卡号——沐曦输出的 `GPU#N` 前缀与 NVIDIA CLI 完全不同形，awk 专门为此写）；④torch 兜底：`torch.cuda.mem_get_info` 按空闲显存排序（L176-191）。配合 deploy/profiles/ 的 muxi/nv 双硬件商 env 样例，这是仓内"国产 GPU 一等公民"的实证。

**multimodaltool（16 件）**：providers.py 的 13 供应商 + LLMClient 门面已在 04 篇拆解；其余按用途分——ocr_config.py（38 行）`get_ocr_api_credentials` 集中管理 OCR 供应商凭据，ocr_utils.py（65 行）做 bbox 容错；sam3_tool/sam_tool/bg_tool（抠图，RMBG-2.0 模型）操作分割；req_img/req_ocr/req_tts/req_understanding/req_videos 五个 req_* 是"请求级"工具封装；ppt_tool + ppt_text_fit（文字溢出适配）；utils 杂务。**MinerU 文档解析的"五后端"实为五种调用变体、单一 http-client 后端**：mineru_tool.py 提供同步单张/批量（run_two_step_extract L246、run_batch_two_step_extract L260）、异步单张/批量（run_aio_two_step_extract L274、run_aio_batch_two_step_extract L288）、第五个是"按 MinerU bbox & type 裁剪原图"（L300 起）——全部 `backend="http-client"` 指向本地 mineru server（L251/265/279/293）。

**websearch 检索线（四件套 + WebAgent）**：agentroles/paper2any_agents 下的 websearch_initial_analyzer（任务拆解 L259 起的 prompt 明言"子任务将由 WebAgent 自动执行"）/planner/researcher/curator 四角色。**researcher.py 内嵌完整浏览器 agent**：`class WebAgent`（websearch_researcher.py:533）自带 PlaywrightToolKit + DomFetcher（反爬 DOM 抓取，L541）+ AsyncOpenAI 客户端（L552-556）+ 动作历史/可达性树/连续失败计数（L536-538）。**L548 参数错位 bug 实锤**：`__init__` 在 L543-547 已为 `self.llm_config` 准备了含环境变量默认值的兜底字典，但紧接着 L548-550 的 `api_key = llm_config.get("api_key")` 读的是**入参**而非 `self.llm_config`——传 `llm_config=None`（该参数 Optional 且有默认处理）时这三行直接 `AttributeError: 'NoneType' object has no attribute 'get'`，兜底逻辑形同虚设。修复应改为从 `self.llm_config` 取值。

**optool（算子工具，958 行）**：DataFlow 算子体系（OPERATOR_REGISTRY）的查询/源码工具。**get_prompt_sources_of_operator 双重定义**：op_tools.py:247 与 op_tools.py:367 存在**逐字相同**的两个函数定义（docstring、random.sample 采样 2 个示例、inspect.getsource 取源码全部一致）——Python 后者静默覆盖前者，运行无害但属复制粘贴/合并残留，两个定义读起来极易误导（改了 L247 版本会"改了没生效"）。

**citationtool（三源引文）**：citation_utils.py 定义三大异构源——OpenAlex（honor_enrichment.py:17 `OPENALEX_BASE_URL`）、Crossref（citation_utils.py:14 `CROSSREF_BASE_URL`，get_crossref_metadata L644、merge_crossref_metadata L792）、DBLP（honor_enrichment.py:18 按 pid 拉 XML，_extract_dblp_pid L170）——全异步并发 + 作者消歧（openalex_author_id 候选比对 L222-223）；context_locator.py 负责引文在正文中的定位。

**rebuttal（审稿工具）**：arxiv.py 论文下载 + tools.py 工具集，被 03 篇 rebuttal_service 的 12 agent 消费（双 PDF 解析器在 service 层）。

**配套小件**：dockertool（mini_docker 沙箱执行 LLM 生成代码，Makefile 移植残留见 04 篇批判 5）、ragtool 向量库、filetool、pipetool、p2vtool、drawio_tools/research_tools 门面、shape_libraries（4 云厂商形状库）、image2drawio 评估精修、basetool 基类、tool_manager.py（118 行，角色化注册，04 篇已述）。

## 外部连接

- **model_servers ← script/**：start_model_servers.sh 拉起全部服务（三通道 GPU 发现 + SAM3 多实例）；deploy/profiles/muxi|nv 提供 DEPLOY_TARGET。
- **multimodaltool ← model_servers**：req_ocr/req_img 等工具打 ocr_server/sam3_server 的 HTTP 端口；MinerU http-client 走 generic_lb 轮询。
- **websearch 线 ← 06 篇 kb_deepresearch 图**：DeepResearch web 模式（02 篇）最终落到这四个 agent；WebAgent 的 Playwright 需要浏览器运行时。
- **citationtool ← paper2citation 线**：wa_paper2citation 适配器 → citation service → 本工具。
- **optool ← DataFlow 算子注册表**：OPERATOR_REGISTRY 是上游数据清洗算子的注册中心，本仓保留其查询工具。
- **providers ← 前端自备网关**：apiyi/comfly/本地 123 端口等供应商 URL 恰是 01 篇 config/api.ts `API_URL_OPTIONS` 的默认值——用户自备 LLM 网关的生态闭环。

## 数据流

模型服务链：start_model_servers.sh 三通道发现 GPU → 逐卡拉起 sam3/ocr/mineru server 实例 → generic_lb 聚合为单一入口。文档解析链：PDF/图片上传 → multimodaltool 按 server 地址构造 http-client → two_step_extract（同步或 aio 变体）→ markdown + bbox → 裁剪变体产出图片区域。检索链：DeepResearch 主题 → initial_analyzer 拆子任务 → planner 排程 → researcher 起 WebAgent：DomFetcher 抓 DOM → 可达性树喂 LLM → 动作（点击/输入/滚动）→ PlaywrightToolKit 执行 → 循环至完成 → curator 策展。引文链：paper2citation 请求 → 三源并发查询 → 作者消歧 → Crossref 元数据合并 → 结构化引文列表。

## 设计决策（含批判）

1. **text.py 把 api_key 写进日志是安全红线**（llm_callers/text.py:33-39）：`log.info("[LLM Output]\napi_key={self.state.request.api_key}...")` 在每次 LLM 响应后把**明文 api_key** 连同输出落盘——日志采集器/运维 grep/崩溃转储都会带走它。生产部署必须删除该行或脱敏；这是全仓最应优先修的一行。
2. **WebAgent L548 的 NoneType 崩溃与死兜底**（websearch_researcher.py:548-550）：默认值兜底写了却不读，`llm_config=None` 路径 100% 崩溃；由于调用方（L852）总是传 config，线上未炸纯属侥幸——任何新调用点按签名省略参数就会踩雷。属"代码有测试盲区的隐性契约"。
3. **mx-smi 适配是国产化诚意的样本**：不为沐曦改全局架构，只在发现层加一条通道 + awk 解析差异（start_model_servers.sh:167-174），配合 profiles 目录的 env 样例——这种"边缘适配不动核心"的做法值得沿用到其他国产硬件。
4. **op_tools 双重定义必须删一个**：op_tools.py:247 与 :367 的逐字重复是事故残留；保留 L367（生效版）、删 L247 是零风险清理——但清理前应 git blame 确认两段是否曾在不同分支各自演化（本例 docstring 都一致，纯复制事故）。
5. **sam3 LRU 容量默认 2 偏保守**：cache_size=2 意味并发多图交互时状态频繁逐出重编码；但 SAM3 编码状态显存占用大，2 是显存安全阀——调优需连带测量显存曲线，不宜盲目上调。
6. **MinerU"五后端"命名误导**：五个函数是同一 http-client 后端的同步/异步/批量/裁剪变体，不是五个独立引擎；读代码时勿被"五后端"印象带偏，真正的后端多路复用发生在 generic_lb/mineru_server 层。
7. **websearch 的浏览器 agent 内嵌在 researcher 而非 toolkits**：PlaywrightToolKit/DomFetcher/WebAgent 全在 agentroles/paper2any_agents/websearch_researcher.py 里，toolkits 只提供基础件——框架"角色即模块"的组织方式在此处越层，检索线想复用 WebAgent 必须从 researcher 模块导入。

## 新人提示

- 起本地模型服务：跑 `script/start_model_servers.sh`（沐曦机器 export DEPLOY_TARGET=muxi）；确认 GPU 发现输出非空再等服务 ready，`generic_lb` 报 503 说明 backends 列表为空（mineru_server.py:20）。
- 安全第一课：部署前 grep 掉 llm_callers/text.py:33-39 的 api_key 日志行；同理检查 WebAgent 默认 api_key（`sk-xxx` 占位，websearch_researcher.py:545）不要进配置文件。
- 用 WebAgent 前必须传完整 llm_config（base_url/api_key/model 三键全给），别依赖默认值——L548 bug 会让 None 直接崩。
- 改算子 prompt 源码逻辑只改 op_tools.py:367 那份定义（生效版）；L247 是死代码。
- OCR/抠图/分割工具的凭据与容错集中在 ocr_config.py/ocr_utils.py，别在业务代码里散落硬编码。
- MinerU 调用选变体：交互式 UI 用同步 two_step_extract，批处理走 aio_batch（mineru_tool.py:277-296），裁剪区域用第五个函数（L299 起）。
