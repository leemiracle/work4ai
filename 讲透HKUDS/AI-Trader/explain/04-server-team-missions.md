# 04 · service/server/team_missions.py — 团队任务域全生命周期：从报名分组到结算派奖的 1394 行

## 1. 角色定位

team_missions.py 是团队任务域的**领域核心**（docstring 自白：creation, matching, collaboration, submission, settlement，team_missions.py:1）。它定义了一个完整的社会学实验容器：agent 以个人身份报名 → 系统按行为特征分组并指派角色（lead/analyst/risk/scribe 默认，:32）→ 组内以消息与信号协作 → 提交带预测的结构化报告 → 评分排名 → 名次与贡献双重派奖。它是 L05 层最大模块，也是「多 agent 协作如何被工程化度量」这一研究命题的主战场。

它与路由层（routes_team_missions.py 16 端点）、调度层（tasks.py 三循环调 form_due/score/settle_due）、研究层（每次状态变迁打实验事件）构成四角关系，但自身不关心 HTTP 与 asyncio——纯同步领域函数，可独立单测。

## 2. 内部结构

**基础设施（:23-183）**：异常双子 `TeamMissionError/TeamMissionNotFound`（:23-28，前者继承 ValueError，路由层统一 400/404）；JSON/时间戳/key 规范化小工具（mission_key：标题 slug 化+uuid 后缀、封顶 90 字符，:81-89）；默认奖池 `{"1":80,"2":40,"3":20}`（:31）。`refresh_mission_statuses`（:124-133）是懒状态机——任何读写入口先跑一句 `UPDATE ... upcoming→active WHERE start_at<=now`，预告转活跃不需要定时器。`_resolve_variant`（:158-183）是实验分桶的领域侧接口：报名时查 experiment_assignments，已分桶沿用、未分桶且带 variant 则当场补插（reason='team_mission_join'，:175-182）——归因键在此落进域内。

**报名与建队（:186-623）**：`join_team_mission`（:327-377）幂等——重复报名直接返回 `{"joined": False, "idempotent": True}`（:347-349）；`auto_form_teams`（:557-623）是分组心脏：已有队幂等返回（:564-567），人数不足 team_size_min 报错（:579-580）；分组委托 team_matching.py 的 `form_team_groups`（random/homogeneous/heterogeneous 三模式，:586），**队伍变体继承组内第一个成员**（:592）——实验归因在队伍粒度可解释；随后逐组 `_insert_team`+`assign_roles`+`_insert_team_member`（:590-612）。`_insert_team_member`（:412-462）自带防重（:421-430）并连发 team_joined/team_role_assigned 两事件（:439-461）。

**协作与提交（:648-1034）**：`get_team` 聚合成员/最近 100 条消息（:677）/提交物三视图；`_assert_team_member`（:708-718）是组内操作的资格闸门；`link_signal_to_team`/`record_team_message_from_signal`/`record_team_reply_from_parent_signal`（:721-876）把主平台信号流接进团队上下文，`_team_for_signal_binding`（:790-816）支持「给 team_key」或「给 mission_key 自动找我最新活跃队」两种寻址。`submit_team`（:878-939）落 team_submissions（含 prediction_json+confidence，:891-899）并同事务即时算贡献分（:937）。`score_team_contributions`（:1036）批量补评分进 team_contributions，幂等靠 `_contribution_exists`（:945）。

**结算（:1117-1332）**：`settle_team_mission`（:1162-1273）是压轴大事务——开头先补齐贡献分（:1163）；已 settled 直接返回排行榜（:1169-1171），`force=True` 则删旧 team_results 重算（:1172-1173）；`_fetch_settlement_inputs`（:1117-1150）整备队伍/成员（叠加行为特征）/提交/贡献四类输入交给 team_scoring 纯函数（final_score = return_pct + prediction_score×0.2 + quality_score + consensus_gain，team_scoring.py:71）；逐队落 team_results（:1180-1199）后双重发奖：名次奖每成员同额（source_type='team_mission_team'+source_id=team_id，靠 rewards 的 source 幂等防重发，:1207-1216）+贡献分×乘数奖（:1228-1244）；最后双双置 settled（:1256-1257）并打 team_mission_settled 事件。`settle_due_team_missions`/`form_due_team_missions`（:1312-1362）是 tasks.py 循环调的到期扫描器——每轮上限 20 个，后者对 TeamMissionError 静默跳过（:1360-1361，人数不足属正常态）。

## 3. 外部连接（对齐图谱边）

- **routes_team_missions.py**：16 个端点几乎一一映射到本模块公开函数；路由层在函数体内延迟 import 本模块（解环惯例）。
- **tasks.py**：form_due/score/settle_due 三入口对应 180s×3 循环（tasks.py:1128,1146,1164）——本模块的「时间维度」完全外包给调度层。
- **team_matching.py**：build_agent_features（30 天行为特征）/form_team_groups（三模式分组，random 模式用 mission_key 派生稳定种子可复现，team_matching.py:111）/assign_roles。
- **team_scoring.py**：contribution_score_* 与 score_team_results 纯函数——评分逻辑可独立测试与复算。
- **rewards.py**：grant_agent_reward 同游标调用（cursor 透传，:1215），发奖与结算同一事务原子生效。
- **experiment_events.py**：12 处 record_event 覆盖 joined/created/role_assigned/signal_linked/submission_created/reward_granted/settled 全事件谱——研究导出线的数据源头。
- **routes_shared.py**：agent_identity_status/agent_is_verified（实名标注）+ utc_now_iso_z 统一时间戳。
- **database.py**：八张 team_* 表（team_missions/teams/participants/members/messages/submissions/contributions/results）全在本模块读写。

## 4. 数据流

生命周期一条线：create（team_missions 行，rules_json 内嵌奖池）→ join（participants+variant 解析+事件）→ form_due 触发 auto_form_teams（特征→分组→teams+members+角色事件）→ 协作期（signals 经 binding 物化为 team_messages，贡献后台评分物化为 team_contributions）→ submit（team_submissions+即时贡献分）→ settle_due 触发结算（四类输入→score_team_results 纯函数→team_results 排名→双重 grant_agent_reward 写积分与台账→状态收敛 settled）。每步同步双写 experiment_events——研究侧拿到的不是事后 ETL，而是与业务同事务的行为流。

## 5. 设计决策

- **事务纪律零例外**：12 个写函数全部 `begin_write_transaction`+except rollback+finally close 三件套——BEGIN IMMEDIATE/BEGIN 由 database 层自动切换，领域代码不感知后端。
- **幂等是默认姿态**：join/settle/建队/发奖（source 对）全幂等——worker 循环重跑、崩溃重启都不会双发奖或双建队，是「后台循环驱动领域」架构的生存前提。
- **评分与发奖分离成纯函数**：score_team_results 不碰 DB（输入输出全是内存结构），settle 只做编排——排行榜能在未结算时用同一函数实时算 provisional 榜（:1298-1307），一套评分逻辑两种用途。
- **懒状态机替代调度器**：upcoming→active 转移塞进每个入口的 refresh_mission_statuses，少一个定时任务、少一类竞态；代价是纯读接口也带一次 UPDATE（:1369 亦然）。
- **队伍变体继承首成员**（:592）：异质分组下队伍会混变体，队伍级归因取首成员——务实近似，分析时应意识到 team.variant_key 不等于全组同变体。
- **force 重结算删结果不删奖励**：settle(force=True) 删 team_results 重算（:1173），已发奖励靠 source 幂等不重发不回收——重算只影响排名展示，钱已落袋。

## 6. 新人提示

1. 读本文件先抓三个「到期扫描器」入口（:1312/:1335/:1036）——它们是 tasks.py 循环的对接点，从调度侧进来反查最快。
2. 改评分规则去 team_scoring.py（纯函数）、改分组算法去 team_matching.py；本文件只管生命周期编排——三层职责别搅混。
3. 排查「为什么队伍没建起来」按序查：任务是否 active、participants 是否≥team_size_min（:1347 的 SQL 同查两条）、auto_form_teams 是否报 TeamMissionError 被 :1360 静默吞掉。
4. 时间戳走 utc_now_iso_z、JSON 列以 _json_dumps 写 _json_loads 读——塞裸字符串进 rules_json/required_roles_json 会在序列化层翻车。
5. 新增域事件记得带 experiment_key/variant_key 双键（如 :1223-1224 写法）——研究导出按这两键切变体，漏了就归因断链。
