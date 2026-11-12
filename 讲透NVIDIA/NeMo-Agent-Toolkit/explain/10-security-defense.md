# 10 · 认证与安全：authentication 供给 + security 三道防线

## 一、角色定位

NAT 的信任边界由两个互补的包把守：core 的 `authentication/`（25 文件）解决「调用者是谁」——给 workflow 装配的 LLM、工具、前端提供凭据供给（API key/OAuth2/JWT/HTTP Basic）；`nvidia_nat_security`（53 文件）解决「内容是否安全」——以中间件形态在函数调用链上设防（defense 四件套 + NeMo Guardrails + 红队测试）。前者是钥匙保管员，后者是安检门。两者都不改动 workflow 业务代码：认证经 builder 装配（`builder.py:314` `add_auth_provider`），防御经中间件链（见 02 篇），全部 config 声明式启用。

## 二、内部结构

**认证供给**（`packages/nvidia_nat_core/src/nat/authentication/`）按凭据类型分目录，每目录「provider+config+register」三件套：

- 契约：`interfaces.py:29` `class AuthProviderBase(Generic[AuthProviderBaseConfigT], ABC)`——所有认证供给的抽象基类；
- API key：`api_key/api_key_auth_provider_config.py:37` `APIKeyAuthProviderConfig(AuthProviderBaseConfig, name="api_key")` + `api_key_auth_provider.py:27` 实现；
- OAuth2 双形态：`oauth2/oauth2_auth_code_flow_provider_config.py:22` `name="oauth2_auth_code_flow"`（授权码流，交互式登录）与 `oauth2_resource_server_config.py:26` `name="oauth2_resource_server"`（资源服务器，验 token 不发 token）；provider 实现在 `oauth2_auth_code_flow_provider.py:38`；
- JWT：`jwt/` 目录 + `jwt_utils.py`；另有 `http_basic_auth/`、`credential_validator/`、`token_storage.py`（token 持久化）与 `register.py`。

这些供给被三处消费：front_ends 的 auth_flow_handlers（`front_ends/fastapi/auth_flow_handlers/http_flow_handler.py` 与 `websocket_flow_handler.py`，把 OAuth 授权码流嵌进 HTTP/WebSocket 前端）、工具执行时取凭据、MCP 的 service_account 认证（`nvidia_nat_mcp/src/nat/plugins/mcp/auth/service_account/token_client.py`）。

**防御三族**（`packages/nvidia_nat_security/src/nat/plugins/security/middleware/`）：

1. **defense 四件套**：基座 `defense_middleware.py:78` `DefenseMiddlewareConfig(FunctionMiddlewareBaseConfig)` + `defense_middleware.py:122` `DefenseMiddleware(FunctionMiddleware)`（含 :64/:71 两个字段解析异常类与「目标字段解析策略」机制——多条数据字段匹配同一目标时的行为由配置决定）；四个具体防线各自注册名：`defense_middleware_content_guard.py:43` `ContentSafetyGuardMiddlewareConfig(name="content_safety_guard")`（内容安全护栏，:61 实现）、`defense_middleware_pii.py:40` `PIIDefenseMiddlewareConfig(name="pii_defense")`（:66 实现，PII 清洗）、`defense_middleware_pre_tool_verifier.py:43` `PreToolVerifierMiddlewareConfig(name="pre_tool_verifier")`（:93 实现，工具调用前用 LLM 校验参数意图）、`defense_middleware_output_verifier.py:42` `OutputVerifierMiddlewareConfig(name="output_verifier")`（:70 实现，输出终审）；共享数据模型在 `defense_middleware_data_models.py`。
2. **guardrails**：`guardrails/nemo_guardrails_middleware.py:57` `class GuardrailsMiddleware(DynamicFunctionMiddleware)`——注意它继承的是**动态函数中间件**（改写函数行为）而非普通 FunctionMiddleware，因为 NeMo Guardrails 要拦截并重写 LLM 对话轨；配置在 `nemo_guardrails_middleware_config.py`。
3. **红队**：`red_teaming/red_teaming_middleware.py:48` `RedTeamingMiddleware(FunctionMiddleware)`——把攻击性 prompt 注入自己的 workflow 验证防御是否生效。

**security 包的另外两条腿**：`eval/red_teaming_evaluator/`（红队评测器，走 `nat.evaluators` entry-points 组注册，被 06 篇的 eval 体系消费）与 `cli/commands.py`（`nat security` 子命令，跑红队扫描）。包根 `register.py` 汇总注册。

## 三、外部连接

上游依赖 core 的中间件基座（middleware.py:118 `Middleware`、function_middleware、dynamic_function_middleware）与 data_models 的 FunctionMiddlewareBaseConfig；认证侧依赖 builder 装配 API 与 front_ends 的 auth_flow_handlers。下游：front_ends 暴露的 REST/MCP 端点是主要保护对象——`examples/MCP/simple_calculator_mcp_protected/` 是全链样例（config-server.yml 的 `general.front_end._type: mcp` 加 OAuth2 保护段）；MCP 侧还有 `introspection_token_verifier.py:27` `IntrospectionTokenVerifier`（资源服务器模式的 token 内省）。横向：eval 体系（红队评测器）、examples/safety_and_security/（17 文件专题示例）。

## 四、数据流

以受保护 MCP server 为例：客户端请求 → MCP 前端收包 → IntrospectionTokenVerifier 向授权服务器内省 token（resource_server 模式）→ 通过后进入 workflow → 中间件链按 config 顺序执行：pre_tool_verifier 先审工具参数 → pii_defense 清洗输入 → 业务函数/LLM 调用 → content_safety_guard 检输出 → output_verifier 终审 → 响应。任何一环判负即短路返回。授权码流场景（面向交互式前端）：front_end 的 flow handler 弹授权页 → OAuth2AuthCodeFlowProvider 完成交换 → token_storage 存储供后续调用复用。

## 五、设计决策

1. **防御=中间件而非独立层**：安全检查复用 02 篇的洋葱圈（pre_invoke/post_invoke），顺序即语义——config 里 middleware 列表的次序决定「先脱敏还是先验证」，给运维留了组合自由，但也埋了顺序配错的坑（见第六节）。
2. **Guardrails 用 DynamicFunctionMiddleware**：NeMo Guardrails 需要重写对话流（插入 rails 轮次），普通 pre/post 钩子不够——继承动态中间件获得函数替换能力，这是「三件套之外还有第四种中间件形态」的活例。
3. **认证供给与前端解耦**：AuthProviderBase 只管「拿凭据」，HTTP/WebSocket/MCP 各自写 flow handler 消费它——同一 oauth2_auth_code_flow 可同时服务 console 与 fastapi 前端。
4. **红队自含**：red_teaming 同时有 middleware（注入器）与 evaluator（判定器），攻击与度量一体，`nat security` 命令可直接扫描任意已部署 workflow。
5. **目标字段解析策略**：DefenseMiddlewareConfig 处理「数据里多个字段匹配同一目标」时不是简单报错，而是配置化策略（defense_middleware.py:71 异常类名即文档）——防御中间件要面对任意业务 schema，硬编码字段名不现实。

## 六、新人提示

上手顺序：先读 interfaces.py:29 的 30 行契约 → defense_middleware.py 的基类（122 行起）→ 挑 pii_defense 一个实现精读 → 跑 examples/safety_and_security/ 与 examples/MCP/simple_calculator_mcp_protected/ 两套示例。坑：①中间件顺序敏感——pii_defense 放在 pre_tool_verifier 之后等于裸奔，写 config 时显式排序并写注释；②`oauth2_resource_server` 与 `oauth2_auth_code_flow` 是二选一的形态选择：server 服务化用前者（只验不发），交互式前端用后者；③guardrails 中间件需要额外安装 NeMo Guardrails 运行时与 rails 配置文件，config 引用不存在的 rails 路径会在运行时才报错；④红队评测会产生真实攻击流量，隔离环境跑；⑤MCP introspection 需要授权服务器可达，内网部署时先打通 introspection 端点再上保护。
