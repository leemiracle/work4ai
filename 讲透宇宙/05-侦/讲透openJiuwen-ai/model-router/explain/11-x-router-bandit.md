# 11 · x-router bandit 闭环：近邻证据、结局记忆与判分尺

## ① 角色定位

分类器给出档位只是先验；bandit 用**相似会话的实际结局**修正它。三文件各管一段：`bandit.py`（196 行）是纯函数决策半——拿分类档位+近邻证据算效用，决定维持或改判；`bandit_store.py`（398 行）是状态半——记住「每档干得怎么样」的 `StateProvider`，kNN 检索相似会话结局；`judge.py`（381 行）是量具——给单个 assistant turn 打 [-1,1] 分的 rubric 与解析器。`judge.py:1-9` 讲清量具为何必须统一：bandit 在轮次、宿主、时间上平均 quality，**每个宿主必须用同一把尺子，否则数字与 margin 都失义**。效用：U(t) = mean_quality(t) − λc·mean_cost(t)/cost_ref_usd（`bandit.py:15`）。

## ② 内部结构

**bandit.py——纯函数，表驱动可测**：模块头声明（`bandit.py:3-5`）唯一输入是分类档位、`RouteContext.retrieved` 与参数，可纯表测试。五个动作码（`:46-51`）：off/cold/same/ignore/override（未配置/近邻不足/维持/没过 margin/改判）。`TierEvidence`（`:56-83`）按近邻 score 加权累积 quality/cost。`parse_observations`（`:86-115`）解析 `{"observations": {tier: {quality, cost_usd}}}`，畸形条目丢弃不抛错（`:88-93`）——**状态数据是提示不是权威**。`aggregate`（`:118-138`）把 retrieved 折进证据表，weight=score（已含年龄折扣）。`utilities`（`:141-162`）易漏规则：λc>0 时**未报 cost 的档位出局**（`:156-158`）——按零成本计分白送成本项；免费档应报 cost_usd=0.0。`choose_tier`（`:165-196`）四级闸门：近邻<min_neighbors → cold（`:174-175`）；分类档无证据 → ignore（`:179-181`）；候选按 `sorted(scores)` 升序扫描（`:186-189`，平手偏便宜档）；优势≤margin → ignore（`:194-195`），否则 override。

**bandit_store.py——两阶段写的 kNN 结局记忆**：模块头（`bandit_store.py:8-20`）伪代码写明生命周期：`query(key, StateQuery{text, route_id})` 编码向量、存半条记录进 pending、返回最近已闭合记录；宿主打分后 `report(Feedback{route_id, extensions=[x-router.bandit]})` 闭合记录。**route_id 是 runtime 的**——query 前注入、feedback 带回，store 不需要自己的 id（`:17-20`）；永不闭合的 pending 按 TTL 过期。store 兼任 `MemoryState` 职责（`:22-25`）：overflow/unavailable 进排除表、ok 建亲和、样本计数——state 槽只装一个 provider，丢了排除表 `target_excluded_degrade` 就废了。隐私（`:27-31`）：只留哈希向量与数字，但文本确实跨 state 边界。检索器 `HashedNgramRetriever`（`:79-112`）：3-gram → FNV-1a 哈希（`:69-76`）→ 4096 桶 L2 归一；注释（`:82-85`）：与 EdgeTRL/agent-xrouter 同构，**向量与近邻跨三系统一致**。读侧 `query`（`:201-226`）任何失败降级纯 view（`:207-208`：坏记忆不得改变路由）；`_neighbours_locked`（`:244-279`）点积即 cosine（`:255`）、`argpartition` top-k（`:257`）、min_similarity 过滤（`:264`）、**遗忘因子** weight=similarity×γ^(Δversion)（`:267`）。写侧 `report`（`:283-302`）：call 部分喂 per-key 视图表（`:304-320`）；extension 部分闭合 pending——版本盖章用**决策时版本**（`:299-301`：中间 publish() 也必须老化）。`_append_locked`（`:336-351`）容量翻倍、满容量 FIFO。`publish`（`:375-381`）只推进版本、**从不清记录**。

**judge.py——冻结 rubric 的量具**：三准则带符号权重 task_progress 0.45 / correctness 0.35 / grounding 0.20（`judge.py:62`），注释（`:60-61`）钉死「权重是 rubric 的不是可调参数——改了存量 quality 与新量不可比」。`JUDGE_SYSTEM_PROMPT`（`:64-69`）要求只回 JSON。预算常量（`:73-76`：3000/2000/1200/400 字符）+中间截断（`:104-109`）。`build_judge_request`（`:126-158`）拼 `<transcript>`+工具清单+`<assistant_turn>` 定界 prompt。`parse_judge_score`（`:161-196`）：取**第一个**含 rubric 字段的 JSON，按在场字段权重**重归一**（`:187-189`），越界忽略而非钳制（`:185`）；兜底取最后一个裸数字（`:190-195`）；都不行抛 ValueError——**不答题的判官要被看见，而非被当 0 分平均**（`:168-171`）。后端双形态：`LocalJudgeBackend`（`:227-256`）可注入 engine 与分类器共享权重（`:230-235` 也警告：能分类的小模型通常太小判不好分）；`ApiJudgeBackend`（`:275-338`）纯标准库走 OpenAI 兼容 API，构造读 env（`:300-305`）、transport 可注入。`judge_from_config`（`:341-381`）按 kind 分派；max_tokens 默认 64（`:210`：分类器的 16 截断 JSON）。

## ③ 外部连接

闭环粘合在 `service.py`：`build_hint`（service.py:111-125）把分类器同款 preview 文本（`retrieval_text` `:97-108`，字节封顶 16384=内核 StateQuery 上限 `:78`）作 state_query 送 store 开 pending；`build_bandit_feedback`（`:159-200`）造第二份报告——`call=None` 延迟反馈挂 `x-router.bandit` extension，**必须带 route_sync 返回的 route_id**（`:176-178`）。`SERVED`（`:82`）从 reasoning 解析实际服务档（`:186-190`）。宿主接线 `build_router`（facade.py:194-225）+`build_store`（facade.py:143-155）；store 受**双重声明**约束（facade.py:158-191）：`[state] backend` 与子表必须一致，单边报错（`:174-184`）。judge 用法样例见 judge.py:11-13。

## ④ 数据流

一次带学习的请求：`route_sync(request, build_hint(...))` → runtime 把 state_query（route_id 已注入）转给 BanditStore.query → 编码向量、pending 落半条、返回 top-k 近邻 → `RouteContext.retrieved` 进 `XRouter.decide`：classify 定档 → `choose_tier` 复核 → Decision（reasoning 带 bandit=code）→ 宿主调模型、judge 打分 → `report_sync(build_bandit_feedback(...))` → store 按 route_id 闭合入库。异步形态把 settle 丢线程池，判官慢不挡请求路；失败只计数+回调不抛给调用方（service.py:26-30）。

## ⑤ 设计决策与权衡

1. **bandit 是覆盖器不是选择器**：`choose_tier` 只在「分类档自身有证据、且别档优势过 margin」时改判（`bandit.py:174-196`）——保守增量修正而非替代分类器。
2. **证据=提示**：畸形数据一律丢弃/降级（store `:207-208`、bandit `:88-93`）——记忆是加速器，坏记忆不许变成路由故障。
3. **版本遗忘 vs 清库**：publish 只涨版本（`:375-381`），γ^(Δversion) 折旧（`:267`）——旧经验指数淡化但保留形状，比清空重启快。
4. **决策时版本盖章**（`:299-301`）：异步 settle 天然晚于决策，用打分时版本会给旧决策记新账——盖决策时版本才正确老化。
5. **判分失败抛错不归零**（judge.py:168-171/`:215-216`）：判官失能化成 0 分流会把好档拉下水。与分类器「降级不升级」同构：失败选不污染统计的方向。
6. **平手偏便宜档**（`bandit.py:186-189`）：sorted 升序+严格大于，并列时胜者=最低档——确定且省钱。

## ⑥ 新人提示与坑

- **bandit 永 cold 三来源**：没配 `[x-router.bandit.store]` 却启用 bandit（facade.py:185-190 warn）；store 配了但 `[state] backend` 没写 `"x-router-bandit"`（`:174-178` 报错）；检索文本超 16384 字节被 runtime 静默降级 snapshot（service.py:75-78）。
- **免费档要报 cost_usd=0.0**（bandit.py:146-149）：省略 cost 的档 λc>0 时出局，免费本地档被误判「成本未知」。
- **`build_bandit_feedback` 必须传 route_sync 原样的 selection**（service.py:172-178）：复制丢 route_id 会 unknown+1（bandit_store.py:296-297），记录永不闭合。
- **stats 是健康仪表**（bandit_store.py:178-188）：dropped（TTL 过期=打分链路断）/unknown（report 无对应 query）/closed 比例定位闭环哪环漏。
- **换 rubric 权重=换尺子**：`RUBRIC_WEIGHTS`（judge.py:62）与 PROMPT_TEMPLATE 同级冻结；换代应配 POLICY_SLOT publish 折旧，而非静默混存。
- **5 路内置算法同构 stub**（已知勘误）：bandit 学习目前只服务 x-router 这条真算法线。
