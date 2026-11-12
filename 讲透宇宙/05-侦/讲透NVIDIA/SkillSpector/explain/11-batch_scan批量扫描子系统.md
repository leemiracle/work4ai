# 11 · contrib/batch_scan 批量扫描子系统：三层并发、7 个猴补丁与 API key 池

## 一、角色定位

`contrib/batch_scan/`（社区贡献区，9 模块+自带测试树）解决规模问题：**一次扫一整目录技能 + 非英语静态规则缺口**。batch_scan.py 是 CLI 入口（线程池并发）；runner.py 双面——薄 graph 包装 + **7 个 DeepSeek 兼容猴补丁**（让无 response_format 的提供方跑结构化分析）；api_pool.py 多 key 负载均衡（429 退避+透明换 key）；gap_fill.py 补 9 条无语义分析器对应的规则；detection.py 零依赖语言检测；annotation.py 打语言兼容标签。不改主包一行——全部经可逆猴补丁接入。

## 二、内部结构

**batch_scan.py（入口，403 行）**：
- 三层并发（docstring :23-35）：L1=LangGraph 内 20 分析器扇出（每技能）、L2=arun_batches Semaphore(10)（每分析器）、L3=本模块 ThreadPoolExecutor（跨技能）。`--workers` 默认 4（:188-195），单技能 90s 超时（:294）。
- **.env 前置铁律**（:50-57）：dotenv 必须先于任何 skillspector import——constants.py 在 import 时读 env；`__init__.py:40-48` 重复同一防御。
- main()（:121-129）整体包在 `with deepseek_compat():` 里；`_print_lock`（:75）序列化 Rich 输出；超时不重试的理由（:302-305——worker 还卡着，重试只再占一槽）；退出码 2=errors/1=高风险/0=净（:395-398）；pool 摘要（:359-374）。

**runner.py（821 行，补丁核心）**：
- `set_api_pool`（:60-98）：把 `llm_utils` 与 `llm_analyzer_base` **两个模块的 get_chat_model 引用都替换**（:88-97）——必须双打，因 llm_analyzer_base 是 from-import 持独立引用；恢复还原两处（:75-82）。
- **7 个补丁**（:117-294）：P1 `_patched_base_init`（:127-135）在原 `__init__` 前把 `response_schema=None` 写进**实例字典**——靠"实例 dict 先于类 dict"的语言级保证（:119-123），让结构化输出绑定失效；P2/P3 parse 补丁（:142-165/:182-210）对裸文本做 fence 剥离（`_strip_markdown_fences` :592-601）+ json.loads + Pydantic 校验，meta 版另做字段消毒（:172-179：None→""、impact 非法→"low"）；P4/P5 给两类 prompt 追加"只回 JSON"指令（:214-251）；P6 `_patched_chatopenai_init`（:264-275）强制 httpx.Timeout(30s, connect=8s) 且同写别名与 canonical 字段名（:271-274，不赌 Pydantic 别名优先级）；P7 `_patched_asyncio_run`（:284-294）吞 "Event loop is closed" 噪音。
- **补丁纪律三件套**：`_verify_patch_targets`（:307-450）打补丁前逐个核对签名/深层依赖（含"位置参数变 keyword-only 会破坏调用点"检查 :478-484），上游变了立刻 RuntimeError；`_apply_patches` 用 `_patches_depth` 嵌套计数（:115, :487-518）支持可重入；`deepseek_compat`（:563-589）Save→Patch→Yield→Restore（finally 保证）。
- `run_one`（:722-813）：graph.invoke → 取 **llm_file_cache**（provider 安全缓存，:765 不重读路径不回落 local-only）→ 语言 auto 检测 → entry_from_result（:626-719，skill/risk/components/issues 四段 + enhancements 溯源）→ 非 en 且 use_llm 跑 gap_fill（:777-783）→ finally cleanup。异常进 stub error entry（:787-809）。

**api_pool.py（643 行）**：`ApiKey`（:80-118，rate_limited/consecutive_429/active_requests/max_concurrent=5）；`ApiKeyPool.acquire` 三步（:165-237）——恢复过期 key（:199）→ least-loaded（:204）→ 全满按最早恢复时刻或超时等待；`release(success=False)` 触发 `30×2^(n-1)` 退避封顶 300s（:284-289, :71-72）；`try_acquire` 非阻塞版（:239-258）；`snapshot` 九指标（:339-354）。`PooledChatModel`（:397-）每次 invoke 现建 ChatOpenAI（:534-551）、429 换 key 重试≤5 次（:70，循环 :461-489 sync / :501-532 async 先 try_acquire 再 to_thread）；`_is_rate_limit`（:553-568）认 RateLimitError 或消息关键词。`create_api_key_pool_from_env`（:576-643）：`SKILLSPECTOR_API_KEYS` 多行 `key|base_url|model`（分号或换行分隔，:601-616），回落 `OPENAI_API_KEY_2..9`（:618-633），**单 key 不成池**（:635）。

**外围四件**：discovery.py `discover_skills`（:26-37）rglob SKILL.md（根目录本身不算）；detection.py `detect_language`（:46-72）CJK/假名/谚文占比阈值 0.10/0.05/0.10 判 zh/ja/ko（:39-42），`detect_skill_language`（:75-88）逐文件投票；annotation.py 四桶规则集（_SEMANTIC 12/_GAP_FILL 9/_CODE 33/_ENGLISH_KEYWORD 25 条，:25-67）+ `is_language_compatible`（:70-79）；gap_fill.py `_GAP_FILL_RULE_IDS` = {P5,P6,P7,P8,MP1-MP3,RA1,RA2}（:37-41）——25 条英文关键词规则 17 条已有 SSD/SDI/SQP 对应，这 9 条没有（:18-25），GapFillAnalyzer 是 LLMAnalyzerBase 子类（:27-30）；reports.py 三格式（:88/:310/:376）+ 分组统计（:237-284）。

## 三、外部连接

对主包是**纯消费者 + 五个补丁点**：graph、LLMAnalyzerBase（P1/P2/P4）、LLMMetaAnalyzer（P3/P5）、ChatOpenAI（P6）、asyncio.run（P7）。api_pool 经 set_api_pool 拦截 get_chat_model 全链（分析器/meta/gap-fill 三路都过池）。SKILLSPECTOR_API_KEYS 多 key、单 key 走主包常规路径。测试自成体系（12 篇）。

## 四、数据流

目录 → discover_skills → 线程池 per-skill：deepseek_compat（7 补丁）→ set_api_pool → graph.invoke → llm_file_cache → 语言检测 → entry_from_result（打 language_compatible）→ [非 en+LLM] gap_fill 追加 findings → cleanup → risk 降序排序（:353-356）→ 渲染+pool 摘要。LLM 调用流：分析器 → 被替换的 get_chat_model → PooledChatModel → acquire（least-loaded）→ 现建 ChatOpenAI（P6 已强制超时）→ 429→退避→换 key≤5 次。

## 五、设计决策

1. **补丁可逆化+预验证**：嵌套计数上下文管理器，应用前核对 20 余个假设——"把静默难调的失败变成打补丁时的即时错误"（:310-313）；fragility 26/invasiveness 14 两套用例专测补丁本身。
2. **实例字典注入而非类属性篡改**（P1）：依赖语言规范而非库内部——上游类层级怎么改都安全（:119-123）。
3. **池的解耦设计**：吞吐随 worker 扩展，与 key 数无关（:24-27 与旧 mutex-per-key 对比）；429 是唯一移出轮换的信号。
4. **语言缺口账本化**：25 条英文规则→17 条有语义对应→9 条 gap-fill 补——language_compatible 字段标明哪些结论可信。
5. **批扫描不因单技能失败而停**：超时/崩溃/error entry 三路都"计数+继续"。

## 六、新人提示（坑与勘误）

- **补丁不是自动生效**："Importing this module does NOT apply them"（runner.py:28-29）；必须 `with deepseek_compat()` 或显式 `setup_deepseek_compat()`（后者是单向门，:297-304）。batch_scan.main() 已包好（:126-129）。
- **dotenv 顺序坑**以"provider/model 神秘失效"形态出现——`.env` 晚于任何 skillspector import 就白配（batch_scan.py:50-51；`__init__.py:40-44` 双保险）。
- P2/P3 对**已是结构化对象**的响应走原解析（:144-145/:184-185 isinstance 分支）——补丁只接管裸文本路径，OpenAI 系 provider 行为零变化。
- `_verify_patch_targets` 检查的 `response_schema` 类属性（:336-341）是 P1 前提，主包删掉它会在**启动时**报 RuntimeError——设计好的早期断裂。
- P6 原函数捕获在**模块加载时**（:257-261 避免顺序依赖）：若别人先 patch 了 ChatOpenAI 再 import runner，恢复时回到"别人的补丁"——微妙但符合注释取舍。
- 90s 超时是 `future.result(timeout=90)`（:294）——超的是**等待结果**，卡死 worker 仍占 executor 槽直到进程结束（:303-304 说不重试的原因）。
- 运行：`python -m contrib.batch_scan.batch_scan ./skills/`（非安装后的 skillspector 命令）；contrib 在 testpaths 之外，测试按 CONTRIBUTING.md:62-89 专属命令跑。
