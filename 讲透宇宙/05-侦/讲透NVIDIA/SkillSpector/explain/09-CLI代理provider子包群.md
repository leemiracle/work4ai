# 09 · CLI 代理 provider 子包群：五个本地 agent CLI 与 1255 行安全总管

## 一、角色定位

五个 `*_cli` 子包让 SkillSpector 借**本地已登录的 agent CLI**（claude/codex/gemini/opencode/agy）做语义分析，全程零 API key——鉴权交给 CLI 自己的 OAuth/keyring 会话。子包本体极薄（provider.py 36-48 行，只有一个 `BINARY_NAME` 类属性），全部行为收在两处：`_agent_cli_base.py`（97 行基类）与 `_agent_cli.py`（1255 行，**全仓唯一的安全关键 chokepoint**）。设计哲学：被扫描的 skill 内容是不可信输入，分析它的却是具备完整 agent 能力的本地 CLI——每条 argv、每个环境变量、每个输出字节都要过闸。

## 二、内部结构

**_agent_cli_base.py（基类模板）**：`AgentCLIProviderBase`（:34）四个类属性（:38-44）；`resolve_credentials` 恒 None（:48-50，CLI 自管鉴权）；`is_available`（:54-56）与 `complete`（:60-80，默认超时 300s :79）纯转发注册表；`resolve_model` 只读 `SKILLSPECTOR_MODEL`，**默认返回空串**（:90-97）——空串即 argv 省略 `--model`，CLI 用运行时默认。

**五个子包**：claude_cli（provider.py:36-44）、codex_cli（:37-45）、gemini_cli（:33-36）、opencode_cli（:32-43）各 6-10 行；antigravity_cli（:39-48）**注册即禁用**（见六节）。

**_agent_cli.py——安全核心，按段落**：
- 常量与擦洗：`MAX_INPUT_BYTES` 1MB / `MAX_OUTPUT_BYTES` 10MB / `MAX_STDERR_BYTES` 64KB / 超时 300s（:73-76）；`_SECRET_ENV_PREFIXES`（:80-107）27 个前缀（ANTHROPIC_/OPENAI_/AWS_/AZURE_/GOOGLE_/SSH_/GPG_/各厂 token）+ 自家 SKILLSPECTOR_API_KEYS；`_scrub_env`（:119-131）大小写不敏感前缀剥离。
- 参数注入防御：`_validate_model_label`（:149-172）拒 `-` 开头（旗标注入）与非白名单字符（仅字母数字 `-./: _`）。
- 四家 argv 构造：**claude**（`_build_claude_argv` :180-253）`-p --output-format text` + `--allowed-tools ""`（空允许表=默认全拒，:247-248）+ `--permission-mode dontAsk`（:249）+ `--strict-mcp-config`（零 MCP，:250）+ `--setting-sources=`（:251）+ `--disable-slash-commands`（:252）；docstring 逐条解释**为什么不用** `--bare`/`--add-dir`/`--dangerously-skip-permissions`（:228-234），text 格式论证（:188-197：json 信封跨版本变形，text 从未变过）。**codex**（:279-332）`exec --json --sandbox read-only --skip-git-repo-check --ephemeral --ignore-user-config --ignore-rules`。**gemini**（:391-425）`-p ""`（真 prompt 走 stdin，:415）`-o json --approval-mode plan --skip-trust`。**opencode**（:674-725）`run --pure --agent skillspector-deny-all-<32hex> --format json`。
- 输出解析：`_parse_claude_output`（:256-271，text 即答案，空即抛）；codex（:335-383，JSONL 取最后 agent_message，兼容新旧形状 :360-377）；gemini（:428-453，JSON 失败**回退原文** :446-447）；opencode（:728-770，拼接全部 `part.type=="text"` 事件）。
- opencode 三件套（最重）：`_prepare_opencode_env`（:516-595）先剥全部 `OPENCODE_*` 变量（:536）再注入 30 余项隔离：不可预测 agent 名（`secrets.token_hex(16)`，:715）、`OPENCODE_CONFIG_CONTENT` 内联 deny-all（`_opencode_config` :477-502：双层 `{"*":"deny"}`）、全路径重定向 temp root（XDG_*/OPENCODE_DB/OPENCODE_TEST_HOME :581-593——TEST_HOME 覆盖 AGENTS.md/.opencode/.claude 搜索路径）。docstring :519-534：**unpredictable agent 名让后到的受管配置无法提前命名该 agent 追加 allow 规则**。`_preflight_opencode_policy`（:598-671）预检：版本必须精确 1.18.32（:633-640，常量 :463），`opencode debug config` 的**最终合并配置**逐键比对 11 项期望（:651-671）——防 macOS MDM 偏好静默重开能力（:602-608）。
- 鉴权探针：claude `auth status` 解析 loggedIn（:778-793）；codex `login status`（:796-807）；**gemini 无廉价探针恒 True**（:810-817）；opencode `auth list` 计数凭据/环境 key（:820-874，剥 ANSI :865-867）。
- 执行引擎：`_run_bounded`（:1059-1123）三线程喂 stdin/排 stdout/排 stderr（防大 prompt 死锁），stdout 触顶即 kill（:1077-1079）；`_cleanup_temp_dir`（:1032-1056）Windows 句柄滞留重试 10 次，**宁可泄漏 temp 目录也不失败批**（#315，:1040-1043）；`run_agent_cli`（:1131-1255）总入口：which 找二进制（:1172-1178）→ 输入上限（:1181-1185）→ argv（:1188）→ mkdtemp 空 cwd（:1195）→ 擦洗+prepare_env/preflight（:1198-1210）→ Popen(shell=False)（:1220-1228）→ 三连 fail-closed（:1240-1250）→ 注册表解析（:1255）。

**注册表**：`CliSpec` dataclass（:947-956，六槽）；`_REGISTRY`（:959-975）五条目，opencode 独占 prepare_env+preflight 两槽；`is_available`（:988-994）= on PATH + 探针通过；扩展指南 :926-944。

## 三、外部连接

`AgentCLICapable` 判定（07 篇 base.py:84）→ llm_utils 的 `AgentCLIChatModel` 适配器（llm_utils.py:318）把 complete() 包成 LangChain 模型；`create_chat_model_with_provider` 对 CLI 提供方短路 HTTP 路径（__init__.py:236-239, :270-271）；调用方在 prompt 外再包 DATA 定界符纵深防御（:39-41）。

## 四、数据流

`SKILLSPECTOR_PROVIDER=claude_cli` → is_llm_available 改查 `is_available()` → AgentCLIChatModel.complete → run_agent_cli("claude", prompt) → argv（标签已校验）→ 擦洗 env+空 temp cwd → stdin 喂 prompt（不可信内容永不入 argv）→ 有界读取 → 非零/超时/溢出全抛 AgentCLIError → 解析出助手文本 → 返回语义线。

## 五、设计决策

1. **允许表而非拒绝表**：`--allowed-tools ""` 未来新增的 Claude 工具默认也被拒（:203-208）；opencode 的 `{"*":"deny"}` 同理。
2. **stdin 是不可信内容的唯一通道**：四家 argv 都刻意留 stdin 模式（gemini `-p ""`、codex 无位置参数、claude `-p` 读 stdin），模型标签单独白名单校验——argv 永远可信。
3. **fail-closed 三重含义**：任何失败抛错而非返回空；空输出抛错（空可能是鉴权失败，不能当"干净分析"）；antigravity 干脆注册但禁用。
4. **opencode 的"不可预测性即安全"**：随机 agent 名+内联配置+最终合并预检，三层防配置层叠顺序攻击——五家唯一需要 preflight，因其合并链最复杂。
5. **gemini 探针豁免的取舍**：没有廉价 auth 查询就信任 PATH，失败推迟到首次调用——与 fail-closed 不冲突（失败仍会抛）。

## 六、新人提示（坑与勘误）

- **antigravity_cli 是"注册但禁用"的 fail-closed 标本**：`_build_agy_argv` 直接 raise（:909-913），`_agy_auth_check` 恒 (False, reason)（:916-923）。禁用原因钉在 :877-899——`agy --print` 只渲染到 TTY，管道下**挂起且返回空 stdout**（1.0.10 实测 0 字节），prompt 走 argv 违反 stdin 铁律，后端还是 Gemini。
- **"五家 CLI 都能用"是错的**：只有四家可用；选 antigravity_cli 立刻在 is_available/complete 处拿到禁用理由。
- gemini 解析器**失败回退原文**（:446-447）是四家唯一的宽容分支——错误状态下 gemini 可能输出纯文本，抛错会丢整段分析；与"空输出必抛"并存。
- opencode 版本钉死 1.18.32（:463, :635-640）：升级被预检拒绝是特性不是 bug——deny-all 策略只对该版本的配置合并语义验证过。
- codex 的 `--sandbox read-only` 仍允许模型跑**只读文件命令**（:293-299：临时空 cwd、无网络出口、信息只回操作者报告）——严格度：claude=gemini（零工具）> codex（只读）> opencode（deny-all+预检）。
- `_claude_auth_check` JSON 解析失败时回退"returncode==0 且不含 not logged in"启发式（:789-790）——claude CLI 输出格式变化时这里是第一松动点。
- 测试主线：tests/unit/test_agent_cli.py（859 行）+ tests/provider/test_opencode_cli.py（551 行）+ tests/integration/test_agent_cli_live.py（135 行）。
