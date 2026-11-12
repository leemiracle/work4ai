# deterministic_converter.py 精讲——确定性动作转换器（录制历史→语义步骤，零 LLM 步骤生成）

## ① 角色定位

`workflows/workflow_use/healing/deterministic_converter.py`（912 行）是 healing 子系统里**把 browser-use agent 的执行历史（AgentHistoryList）程序化翻译成语义工作流步骤**的转换器。docstring（L1-4）开宗明义：不依赖 LLM 创建步骤，LLM 只用于变量识别。它是「AI 录制 → 确定性工作流」产品线的核心压缩机——agent 跑时可天马行空，落地时每步都被压成 `{type, target_text, value, description, verification_checks}` 的可复放结构。

图谱属 L06「healing 自愈子系统」。与 `selector_generator.py`（供给 selector_strategies）、`service.py`（L358 调用、L853 注入元素映射）同层协作；与 LLM 生成路线构成替代——确定性路线快、可预测、无幻觉，代价是语义质量依赖启发式。

## ② 内部结构

类 `DeterministicWorkflowConverter`（L11-912），构造函数（L20-24）持三个映射：`element_text_map`、`element_hash_map`（索引→hash，L23，回填给 service 层填 selector）、`captured_element_text_map`（索引→元素数据，由 service.py L853 注入）。方法按流水线顺序：

- **convert_history_to_steps**（L26-111）主循环：逐条历史→提取 agent 推理（AgentBrain 的 memory/thought/evaluation_previous_goal 级联 L49-56）→ 组 agent_context（reasoning/page_url/page_title，L58-62）→ 取步时长（L65-67）→ 逐 action 解包。browser-use 的 action 格式是 `{action_type: {params}}`，L78-82 找第一个非 'type' 的 dict 值定为动作类型，找不到退旧格式（L84-87）。
- **_get_element_data**（L113-207）四级查找：captured_element_text_map（L128）→ tabs[0].selector_map（L149-160）→ interactive_elements（L163-175）→ interacted_element 按 highlight_index 匹配（L180-190）。box overlay 索引≠元素本身的语义见 docstring L116-118。
- **_normalize_element_data**（L264-325）双分支归一化：dict 分支与 DOM 对象分支（L311-323），统一产出 node_name/node_value/attributes/xpath/element_hash，dict 分支额外透传 selector_strategies（L295-297）。
- **_extract_target_text**（L327-525）十级优先级链（见④）；**_convert_action_to_step**（L535-883）动作映射大分派；**_add_wait_time_to_step**（L527-533）wait_time=时长×0.75；**_create_semantic_description**（L209-262）加语义后缀；**create_workflow_definition**（L885-912）组装终态。

## ③ 外部连接

- **上游**：`browser_use.agent.views.AgentHistoryList`（L8）——与宿主框架最紧的耦合点；captured_element_text_map 与 selector_strategies 均由 service.py 注入。
- **下游**：service.py L358 调主入口，L374-375 读 element_hash_map 回填 selector，L405 组终态；步骤 dict 经 `WorkflowDefinitionSchema` 校验后入 storage，由执行引擎执行。
- **check_function 契约**：verification_checks 引用 `check_url_matches`/`check_page_loaded`/`check_input_value`/`check_no_validation_errors`/`check_page_state_changed`/`check_scroll_position` 六个校验函数名（L576-585 等），执行端按名分派——改名即断链。

## ④ 数据流

一条 click 动作的完整旅程：

1. **解包**（L70-87）：识别出 `('click', {'index': 42})`，index 四级查找命中 captured map → _normalize_element_data 算出 element_hash（sha256 前 10 位，L99/L113/L303）。
3. **目标文本提取**（L645→L327）十级瀑布：① node_value 可见文本（input/textarea/select 除外，L356）→ ② aria-label/placeholder/title/alt（L362）→ ③ 推理里的结构化 `[ELEMENT: "text"]` 标记，**取最后一次出现**（L382-387，离动作最近）→ ④ 无引号变体（L390）→ ⑤ "value ... into the X field" 值锚定正则（L407-411）→ ⑥⑦ 裸模式（L418/L425）→ ⑧ "click the X button"（L432）→ ⑨ name/id 先过 `is_human_readable`（L443-453，黑名单 $/ctl/ctr/dnn/aspnet/viewstate/__/guid + 大写数字占比>70% 判技术 ID），不过关再 `extract_semantic_part` 从 `dnn$ctr434$...$FirstName$txtParameter` 式 ID 倒序拆语义段、驼峰转空格（L455-484）→ ⑩ href 末段转 Title（L499-516）→ node_name 兜底（L520）→ `'element'`（L525）。
4. **动态 ID 泛化**（L650-710，click 独有）：target_text 命中三类正则（字母+数字 L658、纯数字 L659、带分隔符编号 L660-662）即视为记录级标识，按推理关键词映射成 `order id link` 等 12 种泛化名（L675-688），附 position/container 提示（L695-696）——工作流跨记录可复用的关键。
5. **组步骤**（L716-730）：挂 `check_page_state_changed`；elementHash/selectorStrategies 等按存在性附加（L738-752）；wait_time=时长×75%。

动作映射全景：navigate/go_to_url（L564）、input/input_text（L596）、send_keys→key_press（L757）、extract 三别名（L783）、scroll（L801，pages×800 像素 L806）、select_dropdown_option 降级 click（L834）、go_back/go_forward（L845/L860）、跳过 done/switch_tab/close_tab 等（L876-877）、未知 warn（L879-883）。

## ⑤ 设计决策与取舍

**确定性优先于智能**。描述、校验、目标文本全走启发式——录制一次几十步，每步调 LLM 既慢又贵还可能幻觉。代价是覆盖面有限：十级瀑布有 4 级在正则解析英文推理文本，非英文站点里 ③-⑧ 级基本失效。

**[ELEMENT: "text"] 结构化协议是点睛之笔**（L369-394）：与其费力解析自由文本，不如在 agent 系统提示里**规定**它输出结构化标记，转换端只需一个正则。取 last 匹配（L384）——最后提到的才是本动作目标，"约束生成端来简化解析端"的典型手法。

**动态 ID 泛化让工作流可复用**（L650-710）：录 "AP00945776" 这样的许可证号，回放换记录就必须泛化——用推理关键词定语义（L675-688）是对录制意图最便宜的留存。

**wait_time = 0.75×时长**（L530）：录制耗时含人的思考与网络抖动，打 75 折作回放等待的经验值。**dump 大量 print 而非 logging**（L90-110 等 30 余处）则是调试期产物，会污染 stdout，与 selector_generator 用 logger 形成风格反差。

## ⑥ 新人提示（坑/勘误）

1. **`self.llm` 是死属性**：L20-21 接收后零读取。docstring 说 "LLM is only used for variable identification"，但变量识别实际在 service 层——本文件根本不碰 LLM。`element_text_map`（L22）同样死属性：零读写，真正工作的是 captured_element_text_map（外部注入）和 element_hash_map（内部回填）。
2. **两个分支的 element_hash 不可比**（重要）：dict 分支哈希源是 `xpath or str(attributes)`（L302-303），DOM 对象分支是 `getattr(raw_data, 'element_hash', '')`（L313）——同一元素走不同查找路径得到不同 hash，elementHash 关联 selector 时可能对不上。
3. **`'sec' in reasoning_lower` 误报**（L249）：用子串匹配判 "Filings section"，而 "sec" 是 "second"/"security" 的子串——推理含这些词时 click 描述被错标；整个 for-keyword 循环只在 5 个细分分支之一命中才 return，否则静默落 L259。
4. **href 提取的 skip_terms 硬编码演示域名**（L512）：`'www.edison.com', 'edison.com'` 出现在通用代码里——某次演示调参的产物泄漏，其它站点的域名不会被过滤。
5. **`javascript:` href 过滤只覆盖 dict 分支且仅 tag='a'**（L282-283）：DOM 对象分支（L311+）不过滤同类脏数据。
6. **scroll 的 800 像素/页是估算**（L806）：browser-use 用页数、工作流用像素，系数写死——高 DPI 或小视口下回放滚动量会偏离录制。
7. **select_dropdown_option 被降级为 click**（L834-842）：target_text 用**选项文本**而非下拉框本体，click 一个 option 在多数自定义 UI 库上不生效——L833 注释自认 "convert to click for now"。
8. **跳过名单不含新动作**：宿主库升级新增动作类型会落进 L879 的 unknown 分支被 warn 丢弃——升级后要对照动作枚举补映射。
