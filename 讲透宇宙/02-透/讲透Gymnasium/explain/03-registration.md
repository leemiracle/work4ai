# 03 · registration.py：env_id 解析与默认包装链

> 源码 v1.4.0+14（8b22ad4）。registration.py 共 1091 行，伴生 `envs/__init__.py` 400 行、63 条 register。未注明文件的锚均指 registration.py。

## 一、角色定位

`core.py` 定契约（reset/step/render 五元组），registration.py 是生态的户籍管理局：全局注册表 `registry: dict[str, EnvSpec]`（L254）把环境 ID（如 `CartPole-v1`）映射为可实例化的工厂描述 EnvSpec，再由 make 按描述延迟导入真正的环境类并套上默认包装链。

它解决三个问题：解耦（调用方只握字符串 ID，重依赖实例化时才加载）、元数据集中（训练约定与代码分离，一个类注册多版本）、生态扩展（第三方包经同一张表注入）。伴生的 `envs/__init__.py` 是户口申报现场：`import gymnasium`（顶层 `__init__.py:L30-31` 显式导入 envs 包）时逐条执行 register，63 个条目一次性入册。

## 二、内部结构

文件四层：数据结构、解析、校验、公开 API。

数据结构层。`WrapperSpec`（L57-68）是记录 wrapper 重建信息的三元组 name、entry_point、kwargs。`EnvSpec`（L71-242）是核心 dataclass，字段分四组：身份字段 id 与 entry_point（`"模块路径:类名"` 或 callable，L91）；环境属性 reward_threshold、nondeterministic（L94-95）；包装策略字段 max_episode_steps（L98，TimeLimit 依据）、order_enforce（L99，默认 True）、disable_env_checker（L100，默认 False 即开检查）、additional_wrappers（L111）、vector_entry_point（L114）与透传给构造器的 kwargs（L103）。`__post_init__`（L116-118）即刻调 parse_env_id 把 id 拆成 namespace、name、version（L106-108）。autoreset 属性已在 v1.0 移除（L87 钉版），改由 VectorEnv 的 metadata 表达。

ID 语法。正则 `ENV_ID_RE`（L24-26）定义合法格式 `[namespace/](env-name)[-v(version)]`；parse_env_id（L258-279）不匹配即抛 Error，get_env_id（L282-299）为逆。

校验层是一族私有函数：查名与命名空间时以 difflib 纠错（L322-368）；_check_version_exists（L371-428）区分三种病情——仅有无版本默认环境抛 DeprecatedEnv（L407）、版本高于现存抛 VersionNotFound（L422）、低于最高版抛 DeprecatedEnv 附升级指引（L424-428）；_check_spec_register（L431-467）令同家族"有版本/无版本"注册互斥。

公开 API 层：register 写入（L563-637）、make 实例化（L640-832）、make_vec 向量化（L835-990）、spec 查询与 pprint_registry 列册（L993-1091）。两个小件：load_env_creator（L533-545）五行——冒号切分后 importlib.import_module 再 getattr，全部延迟导入魔法的本体；register_envs（L548-550）为空函数，让第三方"依赖注册副作用"的写法对 IDE 可见。

## 三、外部连接

向上，`gymnasium/__init__.py:L13-21` 把四大函数提升为 `gym.make` 等顶层 API。向下，load_env_creator 的字符串入口指向各环境实现模块（classic_control、mujoco 等），注册表是注册层与实现族间的唯一桥。横向依赖 wrappers 体系：默认包装链消费 TimeLimit、PassiveEnvChecker、OrderEnforcing（common.py:L43/L225/L371）与 HumanRendering、RenderCollection（rendering.py:L446/L34）。异常族见 error.py:L13-L42。生态侧，shimmy 安装后会覆盖重注册 GymV21 与 GymV26 两个兼容条目（`envs/__init__.py:L399-400` 先以报错函数占位）。

## 四、数据流

以 `gym.make("CartPole-v1", render_mode="human")` 为例。

入口分派（L669-682）：id 是 EnvSpec 实例则直用（缺 additional_wrappers 时补空元组），字符串则交给 _find_spec（L488-530）——它先识别 `"module:env_id"` 形式，含冒号则先导入该模块再查表（L493-501），此即第三方包"导入即注册"机制。id 未带版本则自动升到家族最新版并警告（L515-522）；落空时先走 _check_version_exists 拿精准报错，再抛兜底 Error（L524-528）。

合并参数（L687-688）：深拷贝 spec.kwargs 再以 make 的 kwargs 覆盖，不污染注册表原件。加载 creator（L691-697）：入口 None 报错；callable 直接用——mujoco v2/v3 占位正是 callable；字符串走 load_env_creator。render_mode 预处理（L700-735）：模式不受支持时自动补位——要 human 而环境只有 rgb_array 则改写 kwargs 并稍后套 HumanRendering，带 \_list 后缀则套 RenderCollection（L717-730）。实例化（L738）后检查返回物须继承 gymnasium.Env（L754-767），甚至识别基类为 gym.core.Env 的 old gym 环境并给迁移指引（L756-762）。

随后给 env.unwrapped.spec 回写净化版 EnvSpec（L770-781）——三个包装字段归零，因默认 wrapper 即将由 make 亲手套上，spec 再记一遍会导致二次重建时重复包装；entry_point 自带预包装 wrapper 时逐项比对前缀（L784-799，ale-py 用之）。

最后是默认包装链，由内向外五层：PassiveEnvChecker 最底层（L801-805，注释明言贴裸环境检查）；OrderEnforcing（L807-809，保证先 reset 后 step）；TimeLimit（L811-816，make 参数优先于 spec 值，传 -1 显式禁用）；additional_wrappers 逐个经 load_env_creator 应用（L818-824，未继承 RecordConstructorArgs 者 kwargs 为 None，拒绝重建）；HumanRendering/RenderCollection 最外层（L826-830）。最终返回 `HumanRendering(TimeLimit(OrderEnforcing(PassiveEnvChecker(CartPoleEnv))))` 套娃。

register 写入流（L563-637）对称而短：先强制 entry_point 与 vector_entry_point 至少其一（L598-601），再解析 id（L602）、处理 namespace——处于 namespace() 上下文管理器（L553-560 切换全局 current_namespace）时覆盖并告警冲突（L606-618）——过互斥校验（L633）后写入；重复注册仅告警不阻止（L635-637）。

## 五、设计决策

版本谱系即数据：版本不是代码分支而是注册表条目。CartPole-v0 与 v1 共享同一个 CartPoleEnv 类，只差 max_episode_steps 200 对 500、reward_threshold 195 对 475（`envs/__init__.py:L18-32`）。MuJoCo 是三层年轮：v2、v3 基于 mujoco_py 已废弃，但仍以抛 ImportError 的 callable 占位（L195-198；Reacher-v2 在 L204），让老代码拿到明确迁移指引；v4、v5 才是官方绑定真身（如 HumanoidStandup-v5，L384-388）。Box2D 只留 v3——LunarLander-v2 在 1.0 已删除，make 旧 ID 触发升级提示。无版本 ID 恒指最新版——`make("CartPole")` 即最新，方便但破坏复现性，注册侧因此禁止同家族混注册两种形态（L456-467）。

registry 全局字典的代价：import gymnasium 即执行全部 63 条 register，副作用式注册换来零配置开箱即用；代价是导入时间，且 `envs/__init__.py:L1` 文档串仍称加载插件，实际 1.x 已删插件扫描（文档滞后），第三方接入改为"导入即注册 + 冒号语法"。

apply_api_compatibility 的退役：1.0 之前 make 曾有该参数，用兼容 wrapper 把 old gym 四元组 step 转成新五元组；1.0 起把它连同 autoreset 一起删除（L596 与 L667 钉版），迁移责任整体移交 shimmy，仓库只留两个占位条目。

make_vec 的三模式（L835-990）：缺省时优先用 spec 自带的向量化入口（CartPole 即有原生 CartPoleVectorEnv，`envs/__init__.py:L21`），否则退回 SyncVectorEnv（L889-893）；原生入口分支禁用 wrappers 参数（L940-947），因向量化环境内部自管包装。jax 系 phys2d 与 tabular 则关闭检查器（`envs/__init__.py:L71、L181`），因 PassiveEnvChecker 不识别 functional 环境。

## 六、新人提示

排查"环境不存在"先跑 `gym.pprint_registry()` 看全表；报错本身带 difflib 拼写建议（L339-344），读异常文本往往就够。复现实验请写全版本号：省略版本会静默升到最新版只留一条 warning；CartPole v0/v1 的阈值差异不是环境变难，是注册参数不同。env.unwrapped.spec 即净化 spec。

自定义环境三步：继承 gymnasium.Env，`register(id="MyEnv-v0", entry_point="my_module:MyEnv")`，再 make。id 必须匹配 L24-26 的正则否则当场抛错；建议用 namespace 前缀（仿 phys2d/tabular）避免撞名。老 gym 环境报不兼容（L759-762）时，正解是装 shimmy 走 GymV26 条目，不要自己改基类。

读源码时抓住三条不变式：registry 的 key 恒等于 EnvSpec.id；包装顺序恒为 checker、order、timelimit、additional、rendering 由内向外；一切动态导入只发生在 load_env_creator 与 _find_spec 两处。
