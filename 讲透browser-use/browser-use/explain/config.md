# browser_use/config.py — config 与 OldConfig 迁移

## ① 角色定位

config.py 是全库的"配置集散地"，534 行里挤着四个世代的配置机制：①`OldConfig`（config.py:47）——纯 Python 类 + @property 的环境变量惰性读取层，是旧版唯一入口，如今仍作为属性兜底层活着；②`FlatEnvConfig`（195）——pydantic-settings 的平铺字段声明，补齐 MCP/代理/扩展等新环境变量；③`DBStyleConfigJSON` 家族（252-317）——config.json 的"数据库风格"模型（uuid 当键、带 default/created_at 元数据），分 browser_profile/llm/agent 三桶；④`Config`（366）——用 `__getattr__` 动态代理把前两代黏起来的兼容门面，文末以 `CONFIG = Config()`（518）单例化，全库任何地方 `from browser_use.config import CONFIG` 即用。它解决的核心矛盾是：历史上大量代码直接读 `CONFIG.XXX` 属性，而环境变量必须"每次访问都重新读"（测试改 env、子进程改 env 都不能被缓存骗过），于是用每次访问新建实例的方式保住这一语义（docstring 369 明言"Re-reads environment variables on every access"）。

## ② 内部结构

`is_running_in_docker`（19，@cache）是启动性能的关键：三重探测——/.dockerenv 文件或 /proc/1/cgroup 含 docker、PID 1 命令行像 py/uv/app、进程总数 <10，任一命中即认容器。OldConfig 的属性分四组：运行开关（BROWSER_USE_LOGGING_LEVEL/ANONYMIZED_TELEMETRY 默认 true/BROWSER_USE_CLOUD_SYNC 默认随遥测）、云端端点（CLOUD_API_URL 默认 https://api.browser-use.com，带 '://' 断言）、路径族（XDG_CACHE_HOME/XDG_CONFIG_HOME/BROWSER_USE_CONFIG_DIR=~/.config/browseruse/PROFILES_DIR/EXTENSIONS_DIR，_ensure_dirs（121）一次性建齐三目录并置 _dirs_created 旗标防重）、七家 LLM API key（OPENAI/ANTHROPIC/GOOGLE/DEEPSEEK/GROK/NOVITA/AZURE，134-163）加运行时提示（IN_DOCKER/IS_IN_EVALS/WIN_FONT_DIR）。FlatEnvConfig（195）用 SettingsConfigDict(env_file='.env', case_sensitive=True, extra='allow') 平铺全部变量，独有 MCP 五项（BROWSER_USE_CONFIG_PATH/HEADLESS/DISABLE_SECURITY/ALLOWED_DOMAINS/LLM_MODEL，236-240）、代理四项（PROXY_URL/NO_PROXY/PROXY_USERNAME/PROXY_PASSWORD，243-246）与 BROWSER_USE_DISABLE_EXTENSIONS。DB 风格层：DBStyleEntry（252）给 uuid4 主键+default+created_at；BrowserProfileEntry（260）extra='allow' 通吃 BrowserProfile 任意字段；LLMEntry（272）/AgentEntry（281）各管 api_key/model 与 max_steps/use_vision/system_prompt。`load_and_migrate_config`（320）是所谓迁移函数：config.json 不存在则建默认；存在且三桶齐、键是带 id 的 dict 则原样加载；**否则（老格式或解析失败）直接删除重建默认**（343-361）。Config 门面（366）：`__getattr__`（376）每次访问 new 一个 OldConfig 先查、再 new 一个 FlatEnvConfig 补查、再把 get_default_profile 等五个方法名绑到内部实现；`_load_config`（466）合成三桶 dict 并叠加 MCP 环境变量覆盖（headless/disable_security/allowed_domains 逗号分割、四项代理 env 折叠成 proxy dict——bypass 拼回逗号串以匹配 Chrome 旗标，488-502）。

## ③ 外部连接

消费者遍布全库：profile.py 引用最多——CONFIG.IN_DOCKER 决定 chromium_sandbox 默认（profile.py:448）、BROWSER_USE_DEFAULT_USER_DATA_DIR 做跨通道 profile 保护（profile.py:803）、BROWSER_USE_EXTENSIONS_DIR 做扩展缓存目录（profile.py:1065）；mcp/server.py:95 用 load_browser_use_config/get_default_profile/get_default_llm 三个模块级辅助函数（config.py:522-534）读配置建会话；根 `__init__.py` import config 即触发日志初始化（读 BROWSER_USE_DEBUG_LOG_FILE/INFO_LOG_FILE）。上游依赖 pydantic-settings（FlatEnvConfig）与 psutil（docker 探测的 PID 1 命令行与进程计数）。config.json 的物理位置三级解析：BROWSER_USE_CONFIG_PATH 显式指定 > BROWSER_USE_CONFIG_DIR 下 config.json > XDG_CONFIG_HOME/browseruse/config.json（411-420）。

## ④ 数据流

属性读流（高频）：`CONFIG.IN_DOCKER` → Config.__getattr__ → OldConfig() 新实例 → property 里 os.getenv 即时读 → （IN_DOCKER 特例）短路进 @cache 的 is_running_in_docker。配置装载流（MCP 启动时一次）：config.json → load_and_migrate_config → DBStyleConfigJSON → _get_default_profile/_get_default_llm/_get_default_agent 各自找 default=True 的条目（无 default 取第一条，427-464）→ _load_config 叠环境变量覆盖（含代理折叠）→ 返回 dict → mcp/server 拿去 BrowserProfile(**profile_data) 与 ChatOpenAI(**llm)。写入流只有一条：首次触碰路径族属性触发 _ensure_dirs 落目录、config.json 缺失时 create_default_config 写默认三桶（默认 LLM 是 'gpt-4.1-mini' + 占位 api key，312）。

## ⑤ 设计决策与取舍

一是**每次访问重读 env 用代理模式实现**：不搞 invalidated cache，直接每次新建实例，代码量最小、语义最直白，代价是热路径（如 IN_DOCKER 每次构造 BrowserProfile 都查）有对象分配开销——is_running_in_docker 用 @cache 单独兜住最贵的探测。二是**老 config.json 的"迁移"实为丢弃**：load_and_migrate_config 检测到旧格式不转换数据而是删文件写默认（344-352）——因为旧格式与新 DB 风格结构差异太大，作者判断"重建比映射便宜"，函数名的 migrate 有误导性，用户旧配置会静默蒸发（仅 debug 日志）。三是**两层 env 读取并存**：OldConfig 管"带转换逻辑的旧属性"（如 CLOUD_SYNC 默认值依赖遥测开关），FlatEnvConfig 管"平铺新字段"，门面按先旧后新顺序查——新代码该往 FlatEnvConfig 加字段，别再扩 OldConfig。四是**代理 env 的字典折叠**：四个扁平 env 变量在 _load_config 收敛成 profile 的类型化 ProxySettings 所需的 dict（488-502），bypass 特意重新 join 成逗号串以贴合 --proxy-bypass-list 旗标格式。五是 DB 风格条目用 uuid 做键 + default 布尔标记，而不是数组+索引——为将来多 profile 管理与增量合并留了稳定标识。

## ⑥ 新人提示（坑/勘误）

- **甄别素材勘误**："OldConfig 的 methods 列表实为 pydantic 字段"的说法与源码不符——OldConfig 是**普通类 + @property**（config.py:47/53-54），没有任何 pydantic 成分；pydantic 化的是 FlatEnvConfig（BaseSettings 字段，195）与 DB 风格三 Entry（BaseModel 字段）。三层别混。
- **CONFIG 不是缓存**：`CONFIG.ANONYMIZED_TELEMETRY` 每次都重新 getenv，测试里 monkeypatch env 立即生效（这正是设计目标）；但 is_running_in_docker 有 @cache，测试想翻转容器态必须 patch 该函数而非文件系统。
- **docker 探测有误报路径**：进程数 <10 就判容器（39），精简的裸机/CI 环境可能中招；显式 IN_DOCKER=true/false env 可覆盖（176）。
- **旧 config.json 会被删**：升级后第一次读配置若检测旧格式，用户手工编辑过的 api_key 等全部丢失且无备份——排障时先问"config.json 最近是不是被重置过"。
- **默认 LLM 的 api_key 是占位串**（'your-openai-api-key-here'，312）：新装环境 MCP 报 401 时先查 config.json 是否还是模板值。
- **case_sensitive=True**（198）：env 变量名大小写敏感，BROWSER_USE_headless 这种写法静默不生效（extra='allow' 只是不报错，字段不会被子集化填充）。
- datetime.utcnow（257）在 Python 3.12+ 已弃用，属于已知技术债；created_at 只是元数据展示用，不影响逻辑。
