# 03 Team 与 Environment 编排：metagpt/team.py + environment/

## 一、角色定位

Team 是最外层编排器：握着一群 Role、一个消息环境（Environment 或 MGXEnv）和预算（investment），按轮次驱动所有人直到全体 idle 或破产。Environment 是消息总线 + 角色容器：维护 member_addrs 路由表，把 publish_message 的消息投进各角色私有 buffer。本仓的编排主线已经换代——Team.use_mgx 默认 True（team.py:38），即默认走 MGXEnv 的"团队领导中转"模式，经典 SoftwareEnv 自由广播模式退居非默认。

## 二、内部结构（行号锚）

**Team（team.py，138 行）**：
- team.py:29-38 `class Team(BaseModel)`，字段 env/investment=10.0/idea/use_mgx=True。
- team.py:41-50 `__init__` 三分支分派：无 env 且 use_mgx=False → Environment；无 env 且 use_mgx=True → MGXEnv；有 env（反序列化来的）只重挂 context。
- team.py:50-57 `serialize`：model_dump 后补 context 序列化写 team.json（SERDESER_PATH/team）。
- team.py:59-75 `deserialize`：读 team.json、ctx.deserialize、Team(**team_info) 重建——断点恢复入口。
- team.py:77-79 `hire` → env.add_roles。
- team.py:92-96 `invest`/`_check_balance`：cost_manager.max_budget 卡预算，超限抛 NoMoneyException。
- team.py:112-135 `run`：n_round 递减循环；env.is_idle 提前收敛（:117-119）；每轮 `_check_balance` + `await self.env.run()`；收尾 `env.archive(auto_archive)`（:134，RFC 135 归档）。start_project 已 deprecated（:109-118）。

**Environment（environment/base_env.py）**：
- base_env.py:124-134 `class Environment(ExtEnv)`：roles 字典（按 name 索引）、member_addrs（exclude=True 不序列化）、history=Memory（注释明言 For debug）。
- base_env.py:152-158 `init_roles`（model_validator）与 :160-173 add_role/add_roles：入环境即 set_env + 共享 context。
- base_env.py:175-193 `publish_message`：遍历 member_addrs，is_send_to 命中就 role.put_message；无人接收打 warning（:190-191）"Message no recipients"。
- base_env.py:195-210 `run`：跳过 idle 角色，`asyncio.gather(*futures)` 一轮并发跑所有活跃角色（:206-208）。
- base_env.py:229-233 `is_idle`：全员 idle 才算 idle——Team 循环的收敛条件。

**MGXEnv（environment/mgx/mgx_env.py，99 行）**：
- mgx_env.py:9-11 `class MGXEnv(Environment, SerializationMixin)`，新增 direct_chat_roles 集合与 is_public_chat=True。
- mgx_env.py:21-51 `publish_message` 四分支：用户 @某角色（:28-38）、角色私信回复（:40-45）、TeamLeader 发布（:46-51）、其余一律 send_to.add(tl.name) 强制经领导（:52-54）。:28 `tl = self.get_role(TEAMLEADER_NAME)` 硬编码人名 "Mike"（const.py:161）。
- mgx_env.py:53-60 ask_human/reply_to_human：远程 MGX 可覆写的真人交互钩子。
- mgx_env.py:63-76 `_publish_message`：is_public_chat 时 send_to 加 `<all>`（:17-18）再走父类广播。
- mgx_env.py:78-96 `move_message_info_to_content`：把 sent_from/send_to 元信息写进 content 前缀 `[Message] from X to Y:`（:90），并强制 role 归一为 assistant（:83-84）——LLM API 只认三种 role 的现实约束。

## 三、外部连接

Team 上游是 software_company.py:17 `generate_repo`（metagpt CLI 入口）；下游串联 Role.set_env（role.py:308-316，set_addresses 双向注册）。MGXEnv 依赖 roles 的 TeamLeader（mgx_env.py:5 引入 Role 仅作类型）；`extract_and_encode_images`（:4）给多模态消息挂图片 metadata。ExtEnv 基类（base_env.py:53）另提供 read_from_api/write_thru_api 给 werewolf/stanford_town 等游戏型环境扩展。

## 四、数据流

metagpt "做一个 2048" 的一生：generate_repo 组队（software_company.py:45-56 hire TeamLeader/ProductManager/Architect/Engineer2/DataAnalyst）→ Team.run → env.publish_message(Message(content=idea))（team.py:102-106）→ 首轮 Environment.run 并发唤起所有 watch(UserRequirement) 的角色 → 各角色 run：observe→react→publish → 消息经 member_addrs 路由进下一个角色的 buffer → 循环直到 is_idle 或预算耗尽 → archive 落盘 workspace。MGX 模式下每次发布都要过 Mike：普通消息被强制加 tl.name 由领导消化后（publicer==tl.profile 分支）再广播。

## 五、设计决策与勘误（证据锚）

- **use_mgx 默认 True（重要行为事实）**：team.py:38——不传参的 Team() 就是 MGXEnv 编排；要复刻经典论文 SOP 必须显式 use_mgx=False，且经典角色阵容已被注释停用：software_company.py:51 `# ProjectManager(),`、:55-61 Engineer/QaEngineer 的 hire 整块注释。默认阵容是 RoleZero 命令系五代目。
- **__all__ 幽灵导出（勘误，源码实证）**：environment/__init__.py:10 的 AndroidEnv import 被注释，但 :13 `__all__` 仍列 "AndroidEnv"——`from metagpt.environment import *` 会直接 AttributeError；star-import 消费者会踩坑。
- **ExtEnv 布局勘误（NOTES-DIGEST 221）**：environment/README.md 描述的基类在 base_env.py，本仓已无 ext_env.py（与旧版布局不同），7 个子域 __init__ 全是空壳桩。
- **并发模型**：Environment.run 每轮 gather 全部活跃角色（base_env.py:206），角色内多轮 react 串行——并发粒度是"轮"，不是消息，天然无消息级竞态，代价是慢角色拖整轮。
- **history 仅为 debug 存在**（base_env.py:133 注释 + Team.run 返回 env.history team.py:135）：别把它当业务存储。

## 六、新人提示

1. 复现论文式瀑布流 SOP：Team(context=ctx, use_mgx=False) + hire 经典角色；默认 MGX 模式的消息都过 Mike，行为完全不同。
2. "Message no recipients" warning（base_env.py:190）= 路由断裂第一信号：检查消息 cause_by 与目标角色 watch、send_to 与目标 addresses 的交集。
3. 断点恢复走 Team.deserialize(stg_path)，要求路径以 "team" 结尾（software_company.py:66-68 有校验）；注意 Context.deserialize 有丢 cost_manager 状态的疑似 bug（见 04 篇）。
4. n_round 是硬上限，QA 线老注释建议 ≥8 轮（software_company.py:62）；is_idle 提前退出依赖角色诚实判闲（role.py:556-559）。
5. 改角色 name 前先看 03 的人名协议（Mike 硬编码在 const.py:161 与 mgx_env.py:28）。
