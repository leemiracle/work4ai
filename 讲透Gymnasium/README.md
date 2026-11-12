# 讲透 Gymnasium

> Farama-Foundation/Gymnasium —— RL 环境标准 API 事实规范（Env/Wrapper/Spaces/VectorEnv/注册体系）。
> 本地仓：/usr-data/data1/workspace/rl/Gymnasium（commit 8b22ad4，2026-10-13）

## 状态（2026-10-14 ✅ 全链路完成）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki/)（37 页 100%+超额，621K 字符） |
| understand 中文图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（**1153 节点/2819 边/16 层/16 步 tour**，validator 0 issues，fingerprints 284 基线@8b22ad4） |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（4029 字 8 节 63 行号锚） |
| explain 系列 | ✅ | [explain/](explain/) 12 篇（2500-4800 字/篇，六节结构，行号锚独立抽验 11/11 命中） |

## explain 索引（12 篇，按 16 步 tour 主线排序）

| # | 篇 | 对象 |
|---|---|---|
| 01 | [core.md](explain/01-core.md) | core.py：Env 五元组契约与 Wrapper 显式委托模型 |
| 02 | [spaces.md](explain/02-spaces.md) | Space 类型系统：四大原语/Box/Discrete/批量空间 |
| 03 | [registration.md](explain/03-registration.md) | 注册体系：env_id→EnvSpec→make 五步解析链+版本谱系 |
| 04 | [cartpole.md](explain/04-cartpole.md) | CartPole 范本环境：动力学/渲染/种子协议 |
| 05 | [frozen-lake.md](explain/05-frozen-lake.md) | FrozenLake：显式转移概率表与表格型 MDP |
| 06 | [mujoco-env.md](explain/06-mujoco-env.md) | MujocoEnv 基类：MJCF 资产/frame_skip/渲染四模式 |
| 07 | [transform-wrappers.md](explain/07-transform-wrappers.md) | 变换 wrappers：ObservationWrapper 模板方法/singledispatch |
| 08 | [common-wrappers.md](explain/08-common-wrappers.md) | 默认包装链五件套：TimeLimit/OrderEnforce/统计/Autoreset |
| 09 | [stateful-wrappers.md](explain/09-stateful-wrappers.md) | 有状态 wrappers：三分档光谱/StickyAction 状态机 |
| 10 | [vector-env.md](explain/10-vector-env.md) | VectorEnv 引擎：Sync/Async/共享内存/autoreset 三态 |
| 11 | [vector-wrappers.md](explain/11-vector-wrappers.md) | vector wrappers：array_conversion 树遍历/懒加载网关 |
| 12 | [env-checker.md](explain/12-env-checker.md) | 质量闸：check_env 主动版 vs passive 只读版 |

## 本轮沉淀的勘误（对 DeepWiki/直觉的修正，均源码实证）

- Wrapper 是**显式委托**非 `__getattr__` 透传（后者是 Gym 活化石，core.py:L537 docstring）
- CartPoleEnv **不**继承 EzPickle（MRO 实证）；EzPickle 用户是 MuJoCo/Box2D 全族
- DelayObservation/FrameStack/Normalize 等**在 stateful_observation.py 非 transform_observation.py**；LazyFrames 已于 v1.0 移除
- 向量版 NormalizeObservation 是全 env **共享**统计（RunningMeanStd 无 num_envs 维）
- FlatListToDict 系旧 gym 遗产，现版 shared_memory 走 `read_from_shared_memory` singledispatch
- make 默认链（内→外）：PassiveEnvChecker→OrderEnforcing→TimeLimit；v1.0 已移除 make 的 autoreset 参数
- functional 文件实在 `gymnasium/envs/` 非 `experimental/`（图谱摘要已纠）；JAX 对接协议是 `metadata["jax"]=True`

## 工程信息

- 流水线：MCP DeepWiki 通道 + understand 批分析（17 批 44 产物，4 并发零事故）+ layers/tour + finalize
- 台账：仓内 `.understand-anything/PROGRESS.md`（断点续跑锚点）；`.understandignore` 裁剪 /docs//assets//bin/
- 工具修复钉版：finalize_graph.py 需解包 layers/tour 包裹对象；onboard_prep.py 字段兼容（summary/id）
