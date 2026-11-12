# 11 · common/ 模型线：统一目录、厂商预设注册表、模式矩阵与 reasoning 注入咽喉

> 所属仓库：openJiuwen-ai/agent-gateway。本篇覆盖 `agent_gateway/common/` 的模型五件：model_catalog（统一只读目录）、model_vendor_registry（厂商预设注册表）、model_selection / model_routing_registry（选择 DTO 与解析器）、mode_matrix（运行模式矩阵）、reasoning_injector（模型构建咽喉）。与 01 篇的请求主线、09 篇的 auth/model_catalog（登录模型发现）互为表里。

## ① 角色定位

这条线回答三个问题：**有哪些模型可用、请求该用哪个模型、模型参数怎么落成 SDK 调用**。

- `model_catalog.py` 是统一只读目录（"Unified read-only catalog for defaults, AgentOS models, and model groups"，`agent_gateway/common/model_catalog.py:2`），聚合 config.yaml 的 defaults 与 AgentOS 来源模型、模型组，并提供**引用扫描**（删除模型前查谁还在用它）。
- `model_vendor_registry.py` 是纯数据表（"A pure-data table"，`agent_gateway/common/model_vendor_registry.py:3`）：用户在模型选择 UI 挑厂商+套餐时自动补全什么配置。数据源自《模型厂商汇总表.xlsx》且**每个端点 2026-08-05 逐条 curl 验证过**（`:9-11`）。
- `mode_matrix.py` 是运行模式解析中枢：把 `work_mode`（work/code 工作环境）与 `mode`（Adapter 选择/单集群/plan）两个正交概念组合成后端 canonical mode（`:5-13` docstring 钉版背景）。
- `reasoning_injector.py` 是**所有模型构建路径的公共咽喉**——`agent_gateway/common/reasoning_injector.py:151-153` 注释明示五路共用："AgentServer, Gateway validation, TUI validation, AgentOS, and team models"（呼应 01 篇主链路）。

## ② 内部结构

**model_catalog（238 行）**：`ModelCatalog`（`:89`）构造时经 `load_models_config`（`agent_gateway/common/config.py:1134`）拍快照。读接口 `get_model/get_group/has_selection/list_public_models/list_public_groups`；安全接口 `get_public_model_detail`（`:138`）——api_key 默认剥除并登记 `write_only_fields`（`:159-166`），仅 `include_api_key and source=="defaults" and not is_login_model` 三条件齐才暴露（`:152`）；引用接口 `find_references`（`:194`）扫模型组路由、会话 metadata、cron 任务、agents/team 配置树四路。

**model_selection（76 行）+ model_routing_registry（156 行）**：前者是 pydantic DTO——`ModelSelection`（`agent_gateway/common/model_selection.py:10`，`extra="forbid"`，route_id 只对 model_group 合法）与解析结果三元组 `ResolvedModel/ResolvedRoute/ResolvedModelGroup`（`:41/56/67`）；后者 `ModelSelectionResolver`（`agent_gateway/common/model_routing_registry.py:35`）实现选择级联："Resolve stable business selections into Foundation compiler input DTOs"（`:1`）。

**model_vendor_registry（593 行）**：`PlanKind` 三值枚举 token_plan/coding_plan/custom_api（`:63`）+ `VendorPreset` frozen dataclass 十三字段（`:72`）+ `_PRESETS` 大表（`:121`）+ 前端 payload 组装 `to_frontend_payload`（`:554`）。

**mode_matrix（515 行）**：九个 canonical 模式常量（`:33-42`，8 正式 + team.design 画布专属）、Web 组合模式集合 `WEB_COMPOSABLE_MODES`（`:54`）、查表 `_WEB_MODE_TABLE`（`:164`）、总入口 `resolve_request_mode`（`:413`）。

**reasoning_injector（172 行）**：两个公开函数 `inject_reasoning_params`（`:71`）与 `build_reasoning_model_request_kwargs`（`:145`）。

## ③ 外部连接

- **config.yaml / config_panel**：目录快照与配置面板读写；`config.py:1286` 在函数内延迟 import `auth.model_catalog.list_login_model_entries` 把登录模型叠加进 defaults。
- **前端 vendors.list RPC**：`to_frontend_payload` 按 plan 分组输出厂商卡片，含逐模型 `reasoning_capabilities`（openai/anthropic 双协议，`:519-551`）与 provider 级 `reasoning_rules`（`:567-571` 注释：给 models_endpoint 拉到的新模型用，防跨厂商 fallback 漂移）。
- **openjiuwen core SDK**：`client_provider` 严格对齐 `ProviderType` 枚举（`:18-21`），中文厂商无原生枚举借 `OpenAI` 并靠 `api_base`+`endpoint_profile` 区分（`:22-24`）；reasoning 能力查询走 `get_reasoning_capability`。
- **volcengine_endpoints**：火山方舟四端点常量（`:53-58` 导入）。
- **五路消费 reasoning_injector**：config_panel/models_handlers、im_pipeline 双向、model_routing_registry、以及仓外的 AgentServer/TUI（`:151-153`）。
- **会话与 cron 存储**：`find_references` 扫 `get_agent_sessions_dir` 与 `get_cron_jobs_path`。

## ④ 数据流

**模型选择流**。请求带 `model_selection`（或没有）→ `ModelSelectionResolver.choose`（`model_routing_registry.py:45`）五级级联：显式指定 > 会话记住的 > spec 内嵌的 > enabled 且 is_default 的模型组 > legacy 名字唯一匹配 > 首个默认模型（都无则 `no model is configured`）。`restore`（`:39`）给已保存引用做"还在就复用，被删了才回退"。选定后 `_model`（`:76`）经 `build_reasoning_model_request_kwargs` 算请求默认值并剔除 `model_name/client_provider/api_base/api_key` 四个落库字段后产出 `ResolvedModel`。

**reasoning 注入流（咽喉）**。`build_reasoning_model_request_kwargs`（`reasoning_injector.py:145`）三步：装 provider 兼容补丁（`:154`）→ `inject_reasoning_params` 把 `reasoning_level` 归一成 `reasoning` 配置并叠加 api_base 级采样 override（`:71-88`）→ `_build_model_request_kwargs`（`:91`）做出口清洗：pop 掉 `model/model_name/reasoning_level/_source` 四个内部键，处理 `context_window` 的过渡期兼容（下文⑤），最后落 `model` 名。**每个模型条目无论来源，发往 core 的参数都从这里过一遍**——这是五条路径（AgentServer/Gateway 校验/TUI 校验/AgentOS/team）语义不漂移的保证。

**模式解析流**。Web 前端只发 `agent/team/agent.plan` 加新三段串（`agent.work.normal` 等，P6.4 兼容，`:50-53`）；`resolve_request_mode` 判定是否组合模式→查 `_WEB_MODE_TABLE` 得 (manager mode, sub_mode, canonical)；`team+code` 归一 `code.team`（TUI 显示 `team.code`，`:13-14`）；`team.plan` 展开为 normal/code 两个 profile 分别路由 DeepAdapter/CodeAdapter（`:16-17`）。完整模式串（TUI/CLI/IM/cron 直发）走 legacy 分支。

## ⑤ 设计决策与权衡

**决策一：端点注册表带验证出处与勘误。** 模块头把数据可信度写死（`model_vendor_registry.py:9-16`）：xlsx 六列 URL（三套餐 × OpenAI/Anthropic 双格式）逐条 curl 验证，401/403/400=存在需鉴权、200=公开、404=不存在。**阿里云 Coding Plan 的 xlsx 笔误被钉版勘误**（`:27-29`）：xlsx 写 `coding.dashscope.aliyun.com`（少 .cn，DNS 不解析），实测正确是 `coding.dashscope.aliyuncs.com`（401），注册表按验证过的主机名收录，`:200` 行内注释再钉一次。同款勘误还有 Maas 空列补查（`:30-32`）。这是"表格数据也要代码评审"的活样本——没有验证出处的注册表就是定时炸弹。

**决策二：套餐域隔离写进注释与 endpoint。** 阿里云 token-plan key 只在 token-plan maas 域名有效，通用 dashscope 域名 401 invalid_api_key，所以 models_endpoint 也必须走套餐域名（`:132-134` 实测 200、12 个模型）；Kimi/Mimo/百度同理（`:189-191/217/175-178`）。智谱的 anthropic_base 显式置 None 并留档原因（`:232-234`）："智谱当前会将普通 API key 的 Anthropic 请求错误路由到 Coding Plan 并返回 1309；暂不向前端开放"——**厂商行为缺陷以数据+注释形式固化**，而非代码特判。

**决策三：context_window 的 core 版本自适应。** `core_has_context_window_field`（`reasoning_injector.py:15-40`）运行时探测 core 的 `ModelRequestConfig` 是否已有正式 `context_window` 字段：过渡期（无字段）在出口 pop 防止透传厂商 SDK 报 unexpected keyword argument；core 加了字段则**不得** pop（否则切掉 core 想读的值）。`_build_model_request_kwargs` 的 `_source` 清理注释（`:109-114`）同样钉版"覆盖 build_model_from_entry / config.validate_model / image_modality_warmup 等所有路径"——咽喉职责的又一次自我声明。旧 AgentOS 用 `max_tokens` 表示上下文窗口的语义迁移（`:98-105`，max_tokens→context_window 防误限输出）也在这里兼容。

**决策四：跨包延迟 import。** `common/model_catalog.py:145` 在方法内才 import `auth.model_catalog.is_login_model`，`:202/:220` 才 import `common.paths`；auth 包内部 `auth/service.py:195/201` 对 `auth.model_catalog` 的回引同样延迟——因为 `auth/model_catalog.py` 顶部 import 了 `auth.service`，service 必须延迟回引才不成环；common 侧的延迟则让只读目录不把 auth 登录运行时（requests/cryptography/远程配置链）拖进每个消费进程。这是"目录读个模型列表不该连带加载 OAuth 栈"的依赖卫生。

**决策五：引用扫描失败即拒绝删除。** `find_references` 扫会话/cron 失败时不是跳过而是抛 `MODEL_RUNTIME_UNAVAILABLE`（`:212-218`），注释一针见血："An incomplete scan cannot prove that a resource is safe to delete"——删除模型是危险操作，证据不全时宁可不删。结果用 `dict.fromkeys` 去重保证确定性（`:236-238`）。

## ⑥ 新人提示与坑

1. **两份 model_catalog + 三份"模型目录"概念**：`common/model_catalog.py`（统一只读目录）vs `auth/model_catalog.py`（登录模型发现）vs `model_selection_store.py`（会话选择持久化，"仅保留 gateway 实际引用的符号；同步母仓时请勿整体覆盖"，`:1-2`）——锚引用必须带包前缀，语义讨论必须先说清是哪份。
2. **加厂商先跑 curl**：注册表的规矩是"每个端点验证过才进表"（`:9-11`），新增/修改 preset 请附验证日期与状态码；xlsx 不可盲信（阿里云笔误前车之鉴）。
3. **`model_options` 是精确表，新模型走 reasoning_rules**：models_endpoint 拉到不在表里的模型时前端回落 provider 级规则（`:567-571`），两套机制的边界别混。
4. **canonical mode 串不要手拼**：九常量之外还有别名归一（`team.plan`→`team.plan.normal`）、plan 剥离（`base_mode_without_plan`，mode_matrix.py:330）、弃用映射（`deprecate_mode`，`:341`）多层转换，直接 `resolve_request_mode` 入口进、别在中间层拼串。
5. **改 `inject_reasoning_params` 等于同时改五条路径**：咽喉的改动会被 AgentServer/TUI 等仓外进程共享（`:153` "also covers processes that never import app_agentserver"），发版前至少跑 config 校验 + im_pipeline 两路回归。
6. **`get_public_model_detail` 的 write-only 契约**：编辑对话框靠 `write_only_fields` 得知"哪些字段被服务端藏了、提交时要保留原值"（`:138-144` docstring），前端别假设响应里字段齐全。
7. **plan 枚举值即前端分组键**：`to_frontend_payload` 输出按 `PlanKind.value` 分组（`:558-560`），改枚举字符串值会直接断前端 vendors.list 渲染。

**关联阅读**：01 篇主链路里 reasoning_injector 的位置；09 篇登录模型如何叠加进 defaults；12 篇 common/ 母仓镜像同步纪律（本篇 model_catalog/model_routing_registry/model_selection_store 三个文件头都有"Gateway 侧副本"标注）。
