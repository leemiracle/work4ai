# 03 · 六平台 Git 门面：`integrations/` 的 mixin 组装术

> 覆盖：`openhands/integrations/`（azure_devops/bitbucket/bitbucket_data_center/forgejo/github/gitlab + protocols/service_types.py/provider.py）
> 选题甄别：任务书"bitbucket_cloud"实为目录 `bitbucket`（Cloud API 版），另有独立平台 `bitbucket_data_center`。

## 1. 角色定位

`openhands/integrations/` 是 OpenHands 与外部 Git 托管平台的**全部边界**：仓库/分支/PR、microagent 解析、建议任务、OAuth token 刷新。六平台（GitHub/GitLab/Bitbucket Cloud/Bitbucket DC/Forgejo/Azure DevOps）共享一套接口，靠 **mixin-composition** 组装各平台服务类。它是**跨代际共享层**：V0 git 路由（`openhands/server/routes/git.py:17`）与 V1 app_server 都消费它——重构中不被拆除的稳定层。平台服务类还带企业扩展点（get_impl 运行时替换）。

## 2. 内部结构

**契约层 service_types.py**：`ProviderType` 七值枚举（`openhands/integrations/service_types.py:20-28`，含无实现的 `ENTERPRISE_SSO`）；领域模型 `Repository`（`:153`）/`Branch`（`:138`）/`SuggestedTask`（`:44`）；异常族全继承 ValueError——`AuthenticationError`（`:176`）等六种，正是 01 篇 `app.py:83-88` 全局 401 的捕获对象。两接口：`BaseGitService(ABC)`（`:217`）承载 **microagent 模板方法族**——`_get_cursorrules_url`（`:231-234`）、`_get_microagents_directory_url`（`:236-241`）、`_is_valid_microagent_file`（`:248-251`）等抽象钩子 + 已实现的 `_determine_microagents_path`（`:263-273`，`.openhands`/`openhands-config` 仓走特例 `:268-270`）；`GitService(Protocol)`（`:456`）定义业务面：构造签名（`:459-467`）、`get_user`（`:475`）、`search_repositories`（`:479-489`）、`get_branches`（`:517-523`）、`get_microagents`（`:530`）、`get_pr_details`（`:544`）、`is_pr_open`（`:556`）。`InstallationsService(Protocol)`（`:450-453`）单方法——仅 GitHub App 装置语义。

**HTTP 原语层**：`HTTPClient(ABC)`（`openhands/integrations/protocols/http_client.py:20`）抽象 `_get_headers`（`:47`）、`_make_request`（`:52`）、`_has_token_expired`（`:61`）、`execute_request`（`:65`）、`handle_http_status_error`（`:78`）——统一限流/超时/401 异常翻译。

**mixin 层**：每平台 `service/` 目录 = base.py（MixinBase）+ 4-6 能力 mixin（repos/branches/prs/features/resolver；Azure 多 work_items）；`github/service/__init__.py:3-8` 导出六部件，`__all__` 收口（`:10-17`）。

**组装现场**：`GitHubService` 基类列表（`openhands/integrations/github/github_service.py:21-30`）：五 mixin→`BaseGitService`→`GitService`→`InstallationsService`——**mixin 在前契约在后**，MRO 使 mixin 实现优先于 Protocol 桩；GitLab 同构（`openhands/integrations/gitlab/gitlab_service.py:20-28`）。Azure DevOps 变体：七 mixin 含 `AzureDevOpsWorkItemsMixin`（`azure_devops_service.py:36`）+直接把 `HTTPClient` 列进基类（`:39`），其 `service/__init__.py` 仅一行注释（`openhands/integrations/azure_devops/service/__init__.py:1`），mixin 逐模块直连导入（`azure_devops_service.py:7-21`）；各 mixin 各自继承 `AzureDevOpsMixinBase`（`service/repos.py:8`、`service/prs.py:10`）。

**MixinBase 承担平台公共态**：`GitHubMixinBase(BaseGitService, HTTPClient)`（`openhands/integrations/github/service/base.py:18`）声明 BASE_URL/GRAPHQL_URL（`:23-24`）、Bearer 头（`:46-49`）、带过期重试的 `_make_request`（`:54-95`：401 刷新重发一次 `:74-83`、透传分页 Link 头 `:87-88`）、GraphQL 执行器（`:97-122`，errors 即抛 `:112-115`）、primary+verified 双条件邮箱解析（`:26-37`）与 `get_user` 回退链（`:144-153`）。`ForgejoMixinBase`（`openhands/integrations/forgejo/service/base.py:24`）是**自带完整 `__init__` 的急切变体**：默认 Codeberg（`:27-28`）、token 参数→`FORGEJO_TOKEN` 环境变量（`:48-53`）、`FORGEJO_BASE_URL` 解析（`:55-56`）、token 前缀 `token ` 非 `Bearer`（`:78`）。

**扩展点三件套（GitHub 例）**：① env 替换 `OPENHANDS_GITHUB_SERVICE_CLS`（`github_service.py:74-77`），六平台同款（gitlab `gitlab_service.py:78-79`、bitbucket `bitbucket_service.py:63-64`、bdc `bitbucket_dc_service.py:75-76`、forgejo `forgejo_service.py:52-55`、azure `azure_devops_service.py:244`）；② `get_impl` 类型安全替换（`openhands/utils/import_utils.py:42`）；③ 懒加载 Proxy：`_GitHubServiceImplProxy` 以 `__getattr__/__call__` 双转发（`github_service.py:92-101`），模块级 `GithubServiceImpl` 是其实例（`:104`），注释 "Lazy loading to avoid circular imports"（`:79-80`），首访才 `get_impl`（`:83-88`）。**Forgejo 反道行之**：导入期急切 `get_impl`（`forgejo_service.py:56`）——无环风险且自带初始化。

**provider.py 工厂**：`ProviderHandler`（`openhands/integrations/provider.py:107`）维护 `PROVIDER_DOMAINS`（`:108-115`）与 `service_class_map` 六平台映射（`:131-139`）；构造强制 tokens 为 MappingProxyType 防篡改（`:124-127`）；`REFRESH_TOKEN_URL` 从 WEB_HOST 拼 SAAS 端点（`:148-150`）；`get_service()` 实例化并下发 token 五元组（`:156-170`）；`get_user()` 遍历已配平台聚合异常（`:172-175`）。

## 3. 外部连接

- **上游**：V0 git 路由 `openhands/server/routes/git.py:17`；01 篇 AuthenticationError 处理链回到 `service_types.py:176`；microagent 结果对接 `openhands/microagent/types.py`（`provider.py:47`）。
- **内部**：mixin 依赖 HTTPClient（`github/service/base.py:8`）、logger（`:7`）、`httpx_verify_option`（`:15`）；provider.py 还 import `EventStream/CmdRunAction`（`:29-31`）——为 `templates/resolver/` j2 模板把 URL 变 agent 命令。
- **包结构**：`openhands/integrations/` 自身**无 `__init__.py`**（PEP 420 隐式命名空间包），六平台目录仅 forgejo 有顶层 `__init__.py`——与 `openhands/__init__.py` 多分发包策略同源。
- **GitHub 企业版支线**：非 github.com 域自动改写 GHES 的 `/api/v3`+`/api/graphql`（`github_service.py:62-64`）。

## 4. 数据流

以"用户打开 GitHub 仓库选择器"为例：git 路由以 MappingProxyType 包装的 tokens 构造 `ProviderHandler` → `get_service(ProviderType.GITHUB)`（`provider.py:156`）取 `GithubServiceImpl`（此刻 Proxy 才触发加载）并实例化（`:159-168`）→ `get_paginated_repos`（契约 `service_types.py:497-506`）落到 `GitHubReposMixin` → `GitHubMixinBase._make_request`（`github/service/base.py:54`）：`_get_headers` 组 Bearer（`:39-49`，空 token 先刷新）→ httpx → 401 且 refresh 开启则重试（`:74-83`）→ Link 头透传分页（`:87-88`）→ 异常被 `handle_http_status_error` 翻译成异常族上抛 401/429/504。microagent 链同理：`get_microagents`（`service_types.py:530`）→ BaseGitService 模板方法调平台钩子列目录→过滤→解析 triggers。

## 5. 设计决策（V0→V1 代际语境）

- **Protocol 与 ABC 并用是有意分层**：`GitService` 用 Protocol（`service_types.py:456`）使任何类无需继承即满足类型——对 get_impl 替换的企业自定义类尤其重要；`BaseGitService` 用 ABC 强制 microagent 钩子齐整。GitHubService docstring 的 TODO（`github_service.py:34`"doesn't seem a good candidate for the get_impl() pattern"）坦承边界仍在自我审视。
- **mixin 拆分对抗千行化**：每平台 4-6 个百行 mixin，PR 冲突面与测试粒度更小；代价是 MRO 复杂、单平台全貌要拼图。
- **Forgejo 急切 vs GitHub 懒加载是循环依赖史化石**：GitHub 服务被 provider.py 顶层 import（`provider.py:34`），Proxy 打破历史环；Forgejo 后进无包袱直接急切。
- **token 安全**：全 SecretStr（`github_service.py:51-52`）、tokens 只读映射（`provider.py:124-127`）。
- **microagent 模板方法放 BaseGitService 而非 mixin**（`service_types.py:263-286`）：发现流程六平台同构，仅 URL 形态与过滤谓词不同——钩子下沉、骨架上提，本目录最教科书的一处。

## 6. 新人提示

- **MRO 坑：`GitHubService.__init__` 不调 `super().__init__`**（`github_service.py:47-67` 手工赋值）——Forgejo 却显式调 `ForgejoMixinBase.__init__`（`forgejo_service.py:40-49`），两种约定并存；给 GitHub 加公共初始化别指望协作式 super 链。
- **坑：`GithubServiceImpl` 是"类的代理"非类**（`github_service.py:104`）——`isinstance(x, GithubServiceImpl)` 不可用；issubclass 检查改用 `get_github_service_impl()`（`:83`）。
- **勘误：Proxy 注释说避免循环导入**（`:79`），当前 import 图已无环——历史防御+模板一致性产物。
- **坑：env 替换变量 import 期求值**（`:74`）+Proxy 全局缓存（`:80`）——测试设 env 晚了不生效，改 env 后需清缓存。
- **Bitbucket 两兄弟别混**：Cloud 与 Data Center 是两个 ProviderType（`service_types.py:23-24`）两套 mixin，认证与分页语义不同。
- **`ENTERPRISE_SSO` 无服务实现**：`service_class_map`（`provider.py:131-139`）不含它——枚举值≠有实现。
- **安全注意：`FORGEJO_TOKEN` 环境变量被读进服务实例**（`forgejo/service/base.py:51-53`）——多租户下是进程级共享凭据，与 per-user token 模型并存，审计留意。
