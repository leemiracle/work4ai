# 12 · common/ 母仓镜像现象学：副本头注纪律、契约分叉禁合并、shim barrel 与依赖倒置桥

> 所属仓库：openJiuwen-ai/agent-gateway。本篇是外围线收官篇，不讲单一子系统，讲**这个仓与母仓 jiuwenswarm 的代码双生关系**——34 个镜像文件的头注纪律、extensions/ 包的"反向吸收"拓扑、三种解耦武器（转发 shim、懒加载 barrel、Protocol 桥）。理解这一篇，才能在这个仓里安全地改任何一行 common/ 代码。

## ① 角色定位

agent-gateway 是从 jiuwenswarm 母仓拆出来的 Gateway 进程独立包（git 历史可见 `refactor(gateway): 包名对齐 agent-gateway`）。拆分没有一刀两断，而是留下一个**过渡态双生结构**：一部分代码以"Gateway 侧副本"形式存在——同路径、同文件名、头注声明源文件，改动双向同步；另一部分已经完成"唯一实现"迁移——本仓持有真源，母仓反向 import。

`agent_gateway/common/__init__.py:1-9` 是这个结构的宪法文件："Only modules whose logic is pure... live here; they are the single source of truth and ``jiuwenswarm`` imports them from this package instead of keeping a second copy. Stateful/shared modules (config, utils, auth, external_providers, base_crypto, etcd, updater, ...) stay under ``jiuwenswarm.common``"。即 common/ 里**同时存在两个方向的文件**：纯逻辑件是真源（母仓来 import 我），有状态件是副本（我去同步母仓）——单看目录名完全无法区分，必须读文件头。

`extensions/__init__.py` 的模块头则是 extensions/ 侧的拓扑图：auth 套件与 application_host 自 B2 从母仓"吸收"，M 组解耦后 `agentos/config_updater`、`agentos/registry_watcher`、`agentos/agentos_router`、`adx`、`agent_client`、`yuanrong_frontend_client`、`video_duplex/backend/tasks/bridge` 七族**以本包为唯一实现**，"``jiuwenswarm.extensions`` 侧已删除原文件并反向 import 本包"（`agent_gateway/extensions/__init__.py:11-17`）。

## ② 内部结构

**镜像层（34 个文件）**。`grep "Gateway 侧副本"` 命中 34 个文件，全部在 common/ 与 extensions/。头注两种形态：完整镜像一行头注（如 `common/model_catalog.py:1`："Gateway 侧副本，源文件 jiuwenswarm/common/model_catalog.py；改动请同步两侧"）；**裁剪镜像两行头注**（19 个文件）再加一行"本副本仅保留 gateway 实际引用的符号；同步母仓时请勿整体覆盖"（如 `common/config.py:1-2`、`common/model_selection_store.py:1-2`）。裁剪镜像不是独立实现，是母仓文件的**符号级子集**——同步方向是母仓→副本的增量挑拣，反向整体覆盖会把 Gateway 不需要的符号灌进来。

**契约分叉层**。config_panel 下 Web 与 TUI 两套 handler 并存：`models_handlers.py`（125 行，Web 侧）与 `tui_models_handlers.py`（986 行，TUI 侧）。

**解耦武器层**（extensions/ 三件）：
- `extensions/types.py`（16 行）：转发别名 shim，注释自述"扩展通用数据类型已迁 ``openjiuwen_protocol.types``……随 gateway 仓迁移整体退役，当前保留旧 import 路径供消费方过渡"（`agent_gateway/extensions/types.py:2-6`），实现只是 re-export（`:11-14`）。
- `extensions/sdk/__init__.py`（61 行）：PEP 562 懒加载 barrel——docstring "transport-specific contracts are lazy imports"（`:1`），`_EXPORTS` 映射九个公开符号到 (模块, 属性)（`:10`），`__getattr__` 按需 import 并缓存（`:47`）。
- `extensions/base_crypto.py`（21 行）：`CryptoProvider` Protocol（`:5`，runtime_checkable，encrypt/decrypt 双方法）+ 进程级全局钩子 `set_crypto_provider/get_crypto_provider`（`:16/:21`）。

## ③ 外部连接

- **母仓 jiuwenswarm**：34 个副本的双向同步对象；extensions/ 七族文件的**反向依赖方**（母仓 import 本仓）。
- **openjiuwen_protocol / openjiuwen core**：types shim 转发目标（两仓扩展框架共用的纯 dataclass 契约）；sdk barrel 各符号的装载目标。
- **第三方扩展**：`from jiuwenswarm.extensions.sdk import ...` 旧路径仍可用——母仓 sdk 只保留惰性转发 shim（`extensions/__init__.py:21-23`）。
- **ExtensionLoader**（`extensions/loader.py:38`）：扩展发现机制，扫搜索路径下含 `extension.yaml` 或 `extension.py` 的子目录（`:15-16`），默认目录 `gateway/extensions`（`extensions/__init__.py:24`）。
- **ExtensionRegistry**（`extensions/registry.py:85`）：单例注册表（`get_instance` 未初始化即 RuntimeError，`:101-105`），agent_server_client/crypto/third_agent/application_plugin 四槽位注册。
- **Web/TUI 通道**：config_panel 两套 handler 的宿主（03 篇）。

## ④ 数据流

**api_key 加解密的依赖倒置流**是全篇最值得画图的一条线。约束：common（如 config 的 api_key 解密）**不能 import 扩展框架**（gateway 拆分约束，`extensions/registry.py:36-37` docstring 原文）。解法三段：

1. common 侧只依赖 Protocol：`models_handlers.py:109` 的 `_get_crypto_provider` 在函数内延迟 import `base_crypto.get_crypto_provider`（`:116`），拿不到就返回 None——docstring 钉版降级语义："AgentServer 进程无 crypto 扩展时 api_key 以明文落库（与原实现一致）"（`:111-114`）；tui_models_handlers 同款（`:74-81`）。
2. registry 侧注入实现：`_RegistryCryptoBridge`（`registry.py:33`）两个静态方法在**每次调用时**解析 `ExtensionRegistry.get_instance().get_crypto_utility_extension()`，扩展未就绪时原样返回明文（`:41-51`）——与旧的 `sys.modules` 软查找惰性语义一致（`:38-39`）。
3. 装配点：`create_instance` 末尾 `base_crypto.set_crypto_provider(_RegistryCryptoBridge())`（`:122`）；`reset_instance` 同步清空（`:126-129`，注释：registry 重置后 common 不得再持有旧实例的桥接）。

依赖箭头由此从"common → extensions.registry"（违规）倒置为"extensions.registry → base_crypto ← common"（双方只指向无业务的 Protocol 模块）。

**懒加载 barrel 流**：消费方 `from agent_gateway.extensions.sdk import BaseExtension` → 包级 `__getattr__`（`sdk/__init__.py:47`）查 `_EXPORTS` → `import_module("agent_gateway.extensions.sdk.base")` → 取属性缓存进 `globals()` → 后续访问零开销。`__dir__`（`:57`）与 `__all__ = list(_EXPORTS)`（`:61`）保证自省完整。与 07 篇 agentos_router 的 barrel 同构，但动机不同：那边防循环导入，这边（docstring）是不让 transport 专属契约拖进轻量消费进程。

## ⑤ 设计决策与权衡

**决策一：镜像头注是机器可查的同步契约。** "改动请同步两侧"不是礼貌用语而是硬纪律——34 个文件的副本状态靠一行 grep 就能审计（`grep -rln "Gateway 侧副本"`）。裁剪镜像加第二行"勿整体覆盖"防同步事故。代价是没有自动校验（无 fingerprint 工具比对两侧漂移），全靠 review——这也是 06 篇式"文档即测试"缺口的一个已知洞。

**决策二：Web/TUI 契约分叉写进 docstring 且明令禁止合并。** `tui_models_handlers.py:10-16` 四条分叉逐项列明：`config.set` 的 env 键集不同（TUI 无 endpoint_profile/vendor_key、YAML setter 表含 Auto-Harness 专属项、回包无 canonical_config）；`config.validate_model` TUI 侧 api_key 对所有 provider 必填、temperature=0、返回 `response` 而非 `ok`；`models.list` 字段集不同（无 origin_index/is_free/is_agentos）；`command.model` 是 TUI 专属命令族。"与 Web 侧……契约不一致，禁止合并"——**两套 handler 是有意的双实现，不是待清理的重复**。合并会静默改变某侧的线上契约。

**决策三：paths.py 的"受控分叉"。** `common/paths.py:3-13` 是镜像中少见的**主动声明差异**的文件：返回值必须与母仓一致（共用用户工作区与 config 目录），唯一分叉是"Gateway 不再通过 import 母仓 ``utils`` 触发其模块级 ``setup_logger()``"——副作用隔离。同时诚实标注缓存局限：同进程有人调母仓 `set_user_home`，本模块缓存不跟随（`:9-10`）。

**决策四：types shim 的退役叙事。** shim 文件自己写好了墓志铭："随 gateway 仓迁移整体退役"（`types.py:5`）——转发别名是迁移的**中间态工件**，与"唯一实现 + 母仓 shim"构成同一迁移的两个相位：先在旧位置留转发（本包 types.py 转发到 protocol 包），等消费方全迁完再删。sdk barrel 同理服务第三方扩展的旧 import 路径。

**决策五：`__init__.py` 本体就是部署知识。** `extensions/__init__.py:28-31` 记录了一个真实事故："没有本文件时 setuptools.packages.find 不会把 gateway/extensions 当作包，wheel 中该目录 0 个文件——部署路径加载 SSH 协议时即 ModuleNotFoundError。B2 合入版（dd67687ba）遗漏了此文件……（与 !8044 最终版 9ca1d5f3e 一致，该 force-push 评审未及合入）"。源码即事故台账，commit 级考古直接写在头注里。

## ⑥ 新人提示与坑

1. **改 common/ 任何文件前先看第一行**：有"Gateway 侧副本"头注 → 你的改动必须同步到 jiuwenswarm 对应文件（反之从母仓同步过来时，裁剪镜像只挑 Gateway 引用的符号，别整文件覆盖）；没有头注 → 它可能是真源，母仓在 import 它（common/__init__.py 的 stateful/stateless 分界）。
2. **models_handlers / tui_models_handlers 禁合并**（`tui_models_handlers.py:10`）：修一个 config.set bug 时 temptation 是顺手统一两套——不要。两侧契约差异是产品语义（TUI 的 Auto-Harness、必填 api_key），统一等于改线上协议。
3. **明文降级是有意设计**：无 crypto 扩展的进程（AgentServer）api_key 明文落库是"与原实现一致"的既定行为（`models_handlers.py:111-114`）；若你在 AgentServer 侧看到明文 api_key，先确认这不是 bug 而是部署形态。
4. **sdk/types 的 import 路径选择**：仓内新代码直接 import 真源（`openjiuwen_protocol.types`、`agent_gateway.extensions.sdk.base`）；兼容旧路径只为第三方扩展保留，新代码再走 `agent_gateway.extensions.types` 这类 shim 会在退役时连坐。
5. **registry 单例的清场语义**：`reset_instance` 会同时摘掉 crypto 桥接（`registry.py:126-129`）——测试里 reset 后又调 common 的解密路径，拿到的是明文而非报错，别误判成桥接泄漏。
6. **加扩展目录的最小形态**：`extension.py` 或 `extension.yaml` 任一存在即被 loader 识别为扩展根（`loader.py:15-16`）；但**目录必须在包内**—— extensions/ 缺 `__init__.py` 的 wheel 空目录事故（`:28-31`）就是前车之鉴，新建子包先确认打包配置把它收进 wheel。
7. **双份同名文件高发区**：本仓至少三对易混镜像（common/config_panel/models_handlers vs tui_models_handlers、common/model_catalog vs auth/model_catalog、routing/agent_client vs common/client/agent_client），写锚与讨论必须带完整路径。

**关联阅读**：07/08 篇（agentos_router 与 adx 就是"唯一实现"七族之二）；10 篇（config_updater 同族）；11 篇（模型线三份镜像文件）；01 篇（app_gateway 主装配如何消费这些 common 件）。

---

**外围线六篇完**（07-12）。与组1 的 01-06（核心链路：app_gateway/message_handler/channel/routing/cron/transport）合计 12 篇，覆盖 agent-gateway 全部主要子系统。
