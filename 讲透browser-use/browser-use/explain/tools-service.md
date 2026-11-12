# browser_use/tools/service.py 精讲——Tools（旧名 Controller）动作层

## 一、角色定位

`browser_use/tools/service.py`（2327 行）定义 `Tools` 类（L441）——Agent 的"手"。模型输出的每个动作（点击、输入、导航、抽取、结束任务……）最终落到这里注册的 action 处理器。它做三件事：**构造器注册约 25 个默认动作**（闭包在 `__init__` 内）；**`act()` 统一执行入口**（L2178，带超时、错误归一、可观测性）；**扩展点**注册自定义动作（`action()` L2102）。

历史包袱：`Controller = Tools` 是文件末尾纯别名（L2326-2327），`controller/__init__.py` 仅 3 行 import。教程的 `Controller(...)` 即 `Tools(...)`。

## 二、内部结构

**构造即注册**。`__init__`（L442-455）先建 `Registry[Context]`，再 `_register_done_action()`，然后按组写内嵌闭包：导航组（`search` L463 / `navigate` L507 / `go_back` L584 / `wait` L598）、交互组（`_click_by_coordinate` L656 / `_click_by_index` L704 / `input` L778 / `upload_file` L864）、标签组（`switch` L1009 / `close` L1042）、信息组（`extract` L1071 / `search_page` L1311 / `find_elements` L1348 / `screenshot` L1529 / `save_as_pdf` L1569 / `dropdown_options` L1683 / `select_dropdown` L1711）、文件组（`write_file` L1763 / `replace_file` L1790 / `read_file` L1798）、高级组（`evaluate` L1837 / `scroll` L1383 / `send_keys` L1488 / `find_text` L1504）。每个 `@self.registry.action(...)` 带描述、`param_model`（Pydantic 参数模型 = 模型看到的函数签名）与元数据——`terminates_sequence=True`（L461、L505）被 multi_act 判断"页面要变，作废队列剩余"。

**done 动作双形态（L2008-2090）**是结构化输出开关：传 `output_model` 时注册 `StructuredOutputAction[output_model]` 版——模型按用户 schema 填 `data`，返回 `model_dump(mode='json')` 序列化（L2019，mode='json' 才能正确序列化嵌套枚举），自动附两类附件：`files_to_display` 显式要展示的 + CDP 追踪的本会话下载（L2030-2037，刻意不含用户白名单）；没传则注册朴素 `DoneAction` 版，长文本截 100 字符进长期记忆（L2056-2060）。`use_structured_output_action()`（L2092）支持运行时切换——Agent 构造器探测到 Tools 的 output_model 就调它（agent/service.py L360-365）。

**act() 统一入口（L2178-2266）**：`action.model_dump(exclude_unset=True)` 取出唯一设置的动作（L2200）→ 可选 Laminar span 包裹（L2203-2216，lmnr 未装时 nullcontext 降级）→ `asyncio.wait_for(registry.execute_action(...), timeout)`（L2220-2232）→ 三层异常归一：`BrowserError` 走 `handle_browser_error`（保留结构化记忆如下拉选项）、`TimeoutError` 生成"浏览器可能无响应，换方法"的可恢复文案（L2236-2249）、其余字符串化（L2250-2253）。超时默认 180s（docstring L2191-2195：远程浏览器的 CDP 内部调用无自身超时，静默 WebSocket 会挂死一切）。结果归一：str→ActionResult、None→空（L2258-2263）。

**`__getattr__` 动态方法（L2268-2323）**：任何已注册动作可 `tools.navigate(url=..., browser_session=...)` 直呼——现场用 `pydantic.create_model` 造 `DynamicActionModel`（L2307-2311）再走 `act()`，直呼与主循环同错误处理，是测试与直接集成的后门。

**依赖注入约定**：处理器签名里的 `browser_session`/`file_system`/`page_extraction_llm` 等不是模型填的，是 `Registry.execute_action`（registry/service.py L331-395）按名注入的"特殊参数"（L368-375）；`sensitive_data` 只注入给 `input`（L377-379 白名单），`page_url`/`cdp_client` 有 session 自动附加（L382-390）。

## 三、外部连接

- **被 Agent 调**：`multi_act` → `tools.act(...)`（agent/service.py L2807-2815）传七类上下文；`get_output_model()` 供探测（L2096）；`set_coordinate_clicking`/`exclude_action` 由 Agent 构造器调用（agent/service.py L325/L334）。
- **向下派发事件**：动作层不直接操作浏览器，而是往 `browser_session.event_bus` 派发 `NavigateToUrlEvent`（L510）、`TypeTextEvent`（L803）等，由 DefaultActionWatchdog 执行——**动作层与浏览器层解耦成"提案—执行"两级**。
- **消费** `dom/service.py`（节点类型）、`filesystem/file_system.py`（沙箱文件系统）、`llm/base.py`（extract 二次加工）。
- **Registry 子包**：注册表与依赖注入机械装置。

## 四、数据流

以 `input` 为例（L778-858）：模型输出 `{"input": {"index": 12, "text": "<secret>password</secret>"}}` → `act()` 解包 → Registry 先做**敏感占位符替换**（registry L354-365：按当前 URL 域名匹配 sensitive_data，把 `<secret>x</secret>` 还原真值）→ 注入依赖 → 处理器 `get_element_by_index` 查节点（L785，找不到返回可恢复错误而非异常）→ 高亮非阻塞派发（L792-794）→ 派发 `TypeTextEvent`（带 is_sensitive，L803-811）→ 拿回 metadata 做三项增值：敏感时消息脱敏成 `Typed <password>`（L816-825）、非敏感比对 actual_value 提示"页面可能改写了输入"（L834-835）、combobox 字段自动 sleep 0.4s 并提示"点建议别按回车"（L837-844）。

`extract`（L1071 起）是另一条 LLM 流：整页 HTML → `extract_clean_markdown` 清洗（L1113）→ 结构感知分块（L1125，替代朴素字符截断）→ 有 schema 则 `schema_dict_to_pydantic_model` 动态建模（L1102-1104，失败降级自由文本）→ 组 prompt 喂 page_extraction_llm。查询含 image 关键词自动开图片抽取（L1089-1092）；分块带 `next_start_char` 续读指针（L1142），模型可翻页式吃完整长文档。

`navigate` 健康检查（L514-544）：导航后检测 `_root is None` 或空 `llm_representation()`（注释 L517-518：两者要分开判——repr 在 _root 为 None 时返回非空占位串），空则等 3s 重查、再空 reload 等 5s、仍空才报错。

## 五、设计决策与取舍

1. **闭包注册而非方法表**：默认动作是 `__init__` 局部闭包，天然捕获 self；代价是 grep 方法定义看不到动作名，得搜 `@self.registry.action`。
2. **错误一律 ActionResult 不抛**：失败压平成带 error 的 ActionResult 回给模型，让它决定重试或换路；只有连接类错误被 Agent 侧重新抛出走重连。"错误是数据不是异常"是健壮性地基。
3. **sensitive_data 双层最小暴露**：Registry 层只在执行瞬间替换真值且只喂 input；日志与消息只见占位符（L816-825）。真值永不进消息历史。
4. **路径安全防御纵深（L879-898）**：upload_file 处理 agent 控制的 `params.path` 时按 basename 在 FileSystem 匹配、拼 `file_obj.full_name`，再 realpath 校验不逃出 data_dir——注释引用 GHSA-j9hj-92j8-jv9h，真实 CVE 修补。远程浏览器场景刻意不改写本地路径（L874-878 注释：`/tmp/note.md` 与本地 `note.md` 撞名会静默上传错文件）。
5. **超时兜底放动作层**：CDP 内部调用无自身超时，外层统一 `asyncio.wait_for` 是唯一兜得住静默 WebSocket 的位置。

## 六、新人提示（坑/勘误）

- **搜 `def click` 找不到 click**：click 是 `_register_click_action`（L2120）注册的闭包，有坐标/索引两形态（L2132/L2149）
- **`exclude_action` 只能减不能加**：加动作用 `@tools.action(...)`。
- **`upload_file` 白名单**：文件必须在 `available_file_paths`（Agent 参数）或本会话下载或 FileSystem 里，否则报错提示加 `Agent(available_file_paths=[...])`（L901）——安全设计。
- **`evaluate` 有 JS 预检**：`_validate_and_fix_javascript`（L1943）自动修 XPath/selector/closest/matches 引号，模型引号错常被救回。
- **`extract` 的 `already_collected` 参数**（L1085-1087）：跨步去重机制，翻页采集把已收条目传回让 LLM 跳过——长列表防重复关键
- **`done` 只在单动作时有效**：multi_act 规定 done 不能与其他动作并列（agent/service.py L2786-2790），排错先查。
