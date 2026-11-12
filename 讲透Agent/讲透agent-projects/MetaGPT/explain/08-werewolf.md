# 08 Werewolf 狼人杀：密语消息驱动的角色路由范式

## 1. 角色定位

Werewolf 是 MetaGPT 官方给出的"用软件公司范式跑一场游戏"的示范子系统：把白天发言当 WritePRD、把夜晚技能当密聊，Team/Environment/Message 基建一行不改全部复用。代码分两处：`metagpt/ext/werewolf/`（角色与动作，Guard/Seer/Witch/Werewolf/Villager/Moderator/HumanPlayer 七种 + HumanPlayer）与 `metagpt/environment/werewolf/`（游戏状态机与主持词常量）。任务描述给的 `metagpt/ext/werewolf/` 正确，但游戏规则本体（胜负判定、STEP_INSTRUCTIONS 主持词）在 environment 侧，两侧必须对照读。入口 `werewolf_game.py:10` 的 `WerewolfGame(Team)` 自述 "Use the software company paradigm to hold a werewolf game"。

## 2. 内部结构

游戏状态机核心是 `environment/werewolf/const.py:36` 的 `STEP_INSTRUCTIONS` 字典——0..17 步主持人台词，每步带 `send_to/restricted_to` 三元组：step 2 Guard 保护密语、step 5 狼人互认、step 8 解药（"You have a bottle of antidote... say \"Save\""）、step 9 毒药（"say ONLY \"Poison PlayerX\""）。`werewolf_ext_env.py:18` 的 `WerewolfExtEnv(ExtEnv)` 持有玩家状态并实现 `observe`（L58）；`RoleState` 枚举（const.py:20-25）区分 ALIVE/DEAD/KILLED/POISONED/SAVED/PROTECTED 六态。角色侧 `base_player.py:22` 的 `BasePlayer(Role)` 是全部玩家基类：L26-27 默认 `use_reflection=True/use_experience=False`，L44-46 强制约束"没有 reflection 就不准用 experience"（warning 后强制关闭）；L63 用 `m.restricted_to` 过滤无关密语；`_think`（L79）按消息可见性路由，`_act`（L91）先 `Reflect().run`（L103）再条件性 `RetrieveExperiences().run`（L109，注意是同步调用无 await）。`witch.py:12` 的 `_think` 是全子系统中唯一重写路由的角色：公开消息走 `Speak`，密语按关键词 `"save" in news.content.lower()`（L23）→`Save()`、`"poison"`（L25）→`Poison()`、都没有则 L28 直接 `raise ValueError`——FIXME 注释自认 "hard code to split"。

## 3. 外部连接

向上：`WerewolfGame(Team)` 继承 metagpt/team.py，但其 `__init__`（werewolf_game.py:15-20）用 `super(Team, self).__init__(**data)`（L16）显式跳过 Team 自身初始化、直调更上层，再自行注入 Context 与 WerewolfEnv，为的是支持反序列化场景 env 已分配时仅补 context。向下：经验复用链直插 RAG 子系统——`experience_operation.py:17-18` 的 `PERSIST_PATH = DEFAULT_WORKSPACE_ROOT.joinpath("werewolf_game/chroma")` 且 `PERSIST_PATH.mkdir` 是模块级副作用（import 即建目录）；两个 Action 经 `model_validator(mode="after")` 惰性构造 Chroma `SimpleEngine`（collection 名硬编码 `"role_reflection"`，L15 FIXME）。横向：`schema.py` 的 `WwMessage` 扩展了 restricted_to 密语语义，Moderator（moderator.py:26）是唯一全场视角角色，负责推进 STEP_INSTRUCTIONS 并在终局调 `_record_all_experiences`（L53）给每个玩家记胜负经验。

## 4. 数据流

一轮夜循环：Moderator 发 step N 密语（restricted_to=主持人+目标角色）→ 各 BasePlayer 在 `_watch` 阶段按 L63 过滤出自己可见的消息 → `_think` 路由出 todo（Speak 或专属 NighttimeWhispers）→ `_act` 组装 context（全部记忆）+ latest_instruction + reflection + experiences 五元组喂给动作（witch_actions.py:5 的 Save 与 L29 的 Poison 都从 common_actions.py:82 的 NighttimeWhispers 派生）→ 回包再次以 restricted_to={Moderator, profile} 加密回传（base_player.py:132）→ Moderator 解析 JSON 更新 env 玩家状态 → 推进步数。终局 Moderator 逐玩家写 RoleExperience，`AddNewExperiences.run` 生成 `{profile}-{name}-step{i}-round_{round_id}` 主键入 Chroma 并本地落 JSON 备份（experience_operation.py:64-76）。

## 5. 设计决策

其一，密语即消息可见性：不用私有信道 API，而是给 Message 加 restricted_to 集合，由接收端自行过滤——最小侵入复用 Env.publish_message。其二，主持人即状态机：规则全在 const.py 数据结构里，Moderator 只是解释器，改游戏流程零代码。其三，经验作为可消融能力而非默认能力。四处实锤坑：STEP_INSTRUCTIONS step 8/9 文案与 witch._think 关键词路由构成隐式耦合——主持词把 "Save"/"Poison" 换成中文或同义词，女巫路由立刻 `ValueError` 且无测试能拦；`base_player._act` 局部变量 `restricted_to` 只在 Speak（L126）与 NighttimeWhispers（L132）两分支赋值，`WwMessage(..., restricted_to=restricted_to)`（L133）在 todo 为其他类型时 UnboundLocalError，当前仅靠 _think 产出受控才安全；`experience_operation.py:119-121` 对 `profile == RoleType.WEREWOLF.value` 直接返回空串并 warning "Disable werewolves' experiences"——消融实验硬编码进生产路径，做狼人胜率对比时它就是基线开关，不知道的人会以为狼人"没有经验"是 bug；const.py:25 `PROTECTED = "projected"` 值与注释双双拼错（应为 protected），全仓 grep 零消费者，属死枚举值无运行时影响。

## 6. 新人提示

跑通游戏先读 examples/werewolf_game，角色分配在 WerewolfEnv 初始化。改游戏规则只动 STEP_INSTRUCTIONS 与 const.py 的解析正则；新增角色照抄 Witch 的三步：派生 NighttimeWhispers 动作、重写 _think 路由、在 Moderator 记分逻辑里认领身份。研究"LLM 会撒谎吗"类实验，本子系统自带 reflection/experience 双开关与狼人禁用基线，是现成的实验台架——但注意 moderator.py:61 的胜负归属用 `role.profile in RoleType.WEREWOLF.value` 子串包含而非 ==，当前单角色名场景等价，若引入前缀重叠的角色名会误判胜负。调试"角色收到不该收的消息"先打印 WwMessage.restricted_to 与 base_player.py:63 的过滤条件，再查 Moderator 是否把 empty_set 写错成具体角色。
