# 03 宿主工具族：web_search/web_fetch/image_describe 与双工厂架构

## 角色定位

`src/nat_sandbox_agent/tools/` 采用**双工厂双域架构**：宿主工具（tools/host/：web_search、web_fetch、image_describe）直接跑在宿主机，沙箱工具（tools/sandbox/：shell、python、file_*、web_browse）跑进隔离容器；`tools/factory.py` 的 `create_all_tools`（tools/factory.py:28）把两族汇成一份工具表交 LangGraph 绑定。为什么 web 工具不放沙箱？web_search.py 给出三条官方理由（web_search.py:17-21）：**安全**（API key 不暴露给沙箱——沙箱内代码是 LLM 生成的，容器被攻破即密钥泄露）、**低延迟**（免 Docker exec 开销）、**高可靠**（沙箱网络故障不连坐）。这是"按信任边界而非按功能"切分工具域的示范：搜索/取网页是"凭据型能力"，留在宿主；执行代码是"危险型能力"，关进沙箱。`SandboxToolExecutor`（tools/sandbox/executor.py:26）是沙箱族的共享执行底座，两族工厂在此汇合。

## 内部结构

**web_search.py**（132 行）：`HostWebSearchTool`（web_search.py:46）先参数后环境变量取 key（web_search.py:58），`_get_client` 懒加载 `AsyncTavilyClient`（web_search.py:61-69）。`search()` 以 `include_answer=True` 让 Tavily 顺带返回聚合答案（web_search.py:88），结果精简成 title/url/snippet/score 四字段（web_search.py:91-96），返回 `{status, results, answer}` 信封。`create_web_search_tool`（web_search.py:114-132）用 `StructuredTool.from_function(coroutine=...)` 包装，`WebSearchInput` 限 num_results 1-10（web_search.py:38-43）。

**web_fetch.py**（204 行）：函数式实现，httpx + markdownify（web_fetch.py:26-27）。UA 显式自报家门 `NATSandboxAgent/1.0`（web_fetch.py:37），单页默认 5000 字符（web_fetch.py:40）。核心 `web_fetch()`（web_fetch.py:65）：follow_redirects + 30s 超时（web_fetch.py:91-95）；按 content-type 分流——HTML 走 markdownify 转 Markdown 并 strip 掉 script/style/nav/footer/header 噪声（web_fetch.py:104-110）+ 连续空行折叠（web_fetch.py:112-124）；随后**双层分页**：`start_index/max_length` 软窗口切片（web_fetch.py:130-132）+ `max_output_chars` 硬顶（web_fetch.py:135-136），返回体带 `has_more/next_start_index` 提示模型自己翻页（web_fetch.py:148-151）。

**image_describe.py**（175 行）：唯一跨域工具——跑在宿主（vision LLM 的 key 不进沙箱）但**读沙箱文件**。`ImageDescribeTool.describe` 六步流水（image_describe.py:75-150）：扩展名白名单校验（七种格式，image_describe.py:37、88-95）→ `sandbox.read_file_bytes`（image_describe.py:99）→ base64+MIME 拼 data URI（image_describe.py:115-117）→ LangChain 多模态 HumanMessage（image_describe.py:120-129）→ `vision_llm.ainvoke`（image_describe.py:133）→ 返回描述。

**共享底座**：common.py 定 `DEFAULT_MAX_OUTPUT_CHARS=16000`（common.py:19，≈4000 token）与 `truncate_output`（common.py:22-33，截断附 "... (truncated, N total chars)"）。`SandboxToolExecutor`（executor.py:26）绑沙箱实例+截断上限+默认超时 120s（executor.py:47-49），docstring 点明"所有工具共享同一沙箱实例，保证文件系统状态一致"（executor.py:30-31）；`list_generated_files` 用 `ls -1 /workspace/output` 回收产物清单（executor.py:55-64）。

## 外部连接

- **汇合点** `create_all_tools`（tools/factory.py:28-75）：建沙箱族（tools/factory.py:54-57）+ 宿主族（tools/factory.py:60-63），dict 合并（tools/factory.py:65），vision LLM 存在才追加 image_describe（tools/factory.py:68-70），最后 `include_tools` 白名单过滤且**静默跳过未知名**（tools/factory.py:72-73）。
- **宿主族工厂** `create_host_tools`（host/__init__.py:33-49）只吐 web_search+web_fetch；image_describe 因需 sandbox+vision_llm 双依赖独立出厂。
- **上游** register.py:173-178 是唯一调用方，vision_llm 从 config 注入（register.py:177）。
- **第三方**：tavily、httpx、markdownify；image_describe 复用第 2 篇的 `BaseSandbox.read_file_bytes`。
- **沙箱族工厂对照**：`create_sandbox_tools`（tools/sandbox/__init__.py:37-77）单 executor 造五工具（tools/sandbox/__init__.py:61-67），include_tools 未知名 **raise ValueError**（tools/sandbox/__init__.py:71-74）——与顶层静默跳过形成行为差异。

## 数据流

一次搜索流：web_search（宿主 Tavily 完成请求）→ 四字段结果经截断回给模型；模型拿 URL 调 web_fetch → 宿主 httpx GET → Markdown 化 + 分页 → 模型读 `has_more` 决定续读。图片流：web_browse/python 下载图片到 /workspace/input → image_describe 跨层读字节 → base64 → vision LLM。配置流：register.py:172 把 `max_observation_tokens*4` 字符预算下贯到两族工厂与 executor，全链路共用一个截断口径。

## 设计决策

1. **把"使用说明"写进工具 description**。web_fetch 的 description 内嵌四个 JSON API 模板 URL——Wikipedia 修订历史、GitHub issue events/timeline、arXiv 月度列表（web_fetch.py:197-202），prompt-in-tool-description 的极致用法：模型在工具签名里直接拿到"检索配方"，省一轮探索。
2. **web_fetch 与 web_browse 的分工是梯度降级**：fetch 轻快但不渲染 JS，browse 重（Playwright）但全能；system_prompt 明令 "Default to web_fetch… 403/405/captcha 再用 web_browse"（system_prompt.py:38-40），工具描述同步背书（web_fetch.py:194-196）——三层（宪法、工具描述、实现）口径一致。
3. **image_describe 的跨界设计**是本篇精髓：密钥在宿主、数据在沙箱，工具做"受控桥"（注释明示 image_describe.py:18-19）。
4. **统一 status 信封**：全部工具返回 `{status: success|error, ...}`，错误也是返回值而非异常——LLM 能读到错误并自我修正（web_search.py:100-111、image_describe.py:91-95）。
5. **截断预算全局一处定义**（common.py:19）+ 各工具硬软双限（web_fetch.py:130-136），防上下文爆炸的纵深防御。

## 新人提示

- 加宿主工具三步：实现类/函数 + `create_*_tool` 包装（照抄 web_fetch.py:189-204 的 StructuredTool 样板）+ 在 host/__init__.py:46-49 列表里注册；要进沙箱族则改 tools/sandbox/__init__.py:61-67。
- 顶层工厂 include_tools 拼错名**不报错**（tools/factory.py:73），沙箱族工厂拼错**报错**（tools/sandbox/__init__.py:73）——调试"工具没出现"先怀疑前者。
- TAVILY_API_KEY 有两条路进系统：宿主工具读环境变量（web_search.py:58）、沙箱容器经 DEFAULT_PASS_ENV_VARS 注入（sandbox/factory.py:27），用途不同别混。
- 测试锚：test_tools_host.py（367 行）与 test_tools_image_describe.py 全部基于 mock，无网络依赖，可放心常跑。
