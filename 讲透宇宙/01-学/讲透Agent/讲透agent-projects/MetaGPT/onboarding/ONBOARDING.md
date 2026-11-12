# MetaGPT 新人上手指南（ONBOARDING）

> 基于知识图谱与 39 批勘误集撰写，锚均经源码核实。仓库：geekan/MetaGPT。

## 1. 一图看懂：MetaGPT 是什么

MetaGPT 把"一家软件公司"搬进代码：**用 SOP 驱动多智能体分工**——PM 写 PRD、架构师出设计、工程师写码、QA 测试，角色只消费上游产物。核心主张：与其让 Agent 自由对话扯皮，不如**把人类协作流程显式编码进框架**。入口 `software_company.py:14` 的 `generate_repo`：雇佣→注资→跑 N 轮（`team.py:83/:92/:123`）。

对比：**LangGraph 是图编排库**（节点边自己搭）；**camel 是自由对话范式**（结构涌现自对话）；**MetaGPT 是角色流水线**（Role watch 哪些 Action 产出→被激活→产出下一环；消息即货币、SOP 即路由表）。主线已向 **RoleZero**（动态命令智能体，`roles/di/role_zero.py:55`）演进，经典 SOP 只是可切换路径。

## 2. 五分钟上手

`pip install metagpt` 后在工作目录执行 `metagpt "写一个贪吃蛇游戏"`。入口链：`setup.py:118` 注册 `metagpt=metagpt.software_company:app`，startup() 调 `generate_repo`。**首跑动作**：无用户配置时 `DEFAULT_CONFIG`（`software_company.py:127`）被写出为 `~/.metagpt/config2.yaml`（`software_company.py:152`）——"首跑生成+用户编辑"双身份文件，须填 `llm.api_key`（不读 .env）。默认阵容 TeamLeader/ProductManager/Architect/Engineer2/DataAnalyst（`software_company.py:47-52`），5 轮后产出 `workspace/<项目>/` 下 docs 与源码。走论文经典 SOP 须手改 generate_repo（三角色雇佣行在 `software_company.py:51-62` 已注释停用）。`startup.py` 是 10 行废弃桩。

## 3. 架构总览：15 层地图

- **L01 配置**：`config2.py:110` 起步，合并序 env→仓内 yaml→用户 yaml→kwargs（`config2.py:116-121`，后位覆盖前位，**环境变量优先级最低**）。
- **L02 基础抽象**：schema.py 定义 Message/Document/Plan 等 26 个契约类（`metagpt/schema.py:232`）；CostManager 记账。
- **L03 Provider 矩阵**：约 30 家厂商适配，见 4.3。
- **L04 记忆**：Role 三层记忆 + document_store 五种向量库。
- **L05 工具库**：utils/ 地基——文件仓库三级抽象（file→git→project_repo）、repair 闭环（见第 6 节）。
- **L06 Actions**：SOP 原子能力；ActionNode（`actions/action_node.py:135`）是结构化输出引擎。
- **L07/L08 角色与编排**：role.py 基类+经典阵容；Team + Environment 消息总线 + MGXEnv 仲裁（4.2）。
- **L09 工具生态**：TOOL_REGISTRY 单例（`tools/tool_registry.py:91`）。
- **L10 RAG**：rag/factories 工厂族，记忆与经验池共用底座。
- **L11 策略与经验池**：`@exp_cache`（`exp_pool/decorator.py:29`）缓存动作输出。
- **L12 Skills 资产**：metagpt/skills/ 40 个 SK 风格技能——vendored 遗产、零消费者（第 7 节）。
- **L13-L15 研究面**：四研究环境（minecraft 是 Voyager 复现）+ ext 六论文子包 + 工程外围（CI/devcontainer）。

主线一条环：**Message 从总线流出→Role 按 cause_by 认领→Action 执行→LLM 生成→落盘→回总线**。

## 4. 核心子系统深潜

### 4.1 Role / Action 抽象

Role 心脏是 `_observe→_think→_act` 循环（`roles/role.py:399/:340/:381`）：`_observe` 只认 `n.cause_by in self.rc.watch or self.name in n.send_to` 的消息（`role.py:411`，SOP 路由判定式；watch 集由 `_watch` 注册，`role.py:284`）；`_think` 按三模式选 todo；`_act` 执行并包成 AIMessage。结构化输出靠 ActionNode（`action_node.py:135`）：声明节点树，`create_model_class`（`:248`）动态生成 pydantic 校验类、`fill`（`:597`）把树编译成提示词再解析回模型。

### 4.2 Team + Environment（重磅勘误）

**重磅勘误：`team.py:43` 的 `use_mgx` 默认 True——默认环境是 MGXEnv 而非经典 Environment**。MGXEnv 把广播消息先交 TeamLeader "Mike" 仲裁再分派（`environment/mgx/mgx_env.py:28`）。连带后果：`software_company.py:51-62` 经典 SOP 三角色被注释停用，**默认跑 MGX 阵容**；复现论文流水线须显式 use_mgx=False。更微妙：ProductManager 已改继承 RoleZero（`roles/product_manager.py:21`），靠 `use_fixed_sop` 开关切换经典 SOP（`product_manager.py:43-46`）与动态智能体——经典 SOP 只是 RoleZero 的降级模式。

### 4.3 LLM Provider 矩阵

工厂链：`llm.py:15` 的 LLM() → create_llm_instance（`provider/llm_provider_registry.py:38`）按 api_type 取类。注册方向是**反的**——registry 不 import 任何 provider，各 provider 用 `@register_provider` 自注册（导入即注册）。三个易踩点：①api_type 拼错不报错——`LLMType.__missing__` 静默回退 OPENAI 兼容层（`configs/llm_config.py:48`），运行期才炸；②openrouter 双注册（双键同挂 OpenAILLM）；③`general_api_base.py` 是 **openai 0.x SDK 的 vendored fork**（`provider/general_api_base.py:3`）——智谱/ollama 走它防 SDK 升级，基类 `_interpret_response` 是无 return 空壳。

### 4.4 memory 与 LongTermMemory

短期记忆 Memory 即消息列表；长期 LongTermMemory 继承之，超容量沉入 RAG（`memory/longterm_memory.py:18`）。坑：`memory/__init__.py:12` 的 LongTermMemory re-export **被注释禁用**——`from metagpt.memory import LongTermMemory` 直接 ImportError，须走全路径；且它与 role.py 互为包级循环依赖，靠 barrel 不加载它化解。

## 5. 一次调用的生命周期

以 `metagpt "写个贪吃蛇"` 为例：

1. **需求入线**：`env.publish_message(Message(content=idea))`（`team.py:107`）；cause_by 留空由校验器兜底为 **UserRequirement**（`metagpt/schema.py:266-269`）。
2. **广播投递**：Environment（`environment/base_env.py:124`）按 member_addrs 定向投递——角色地址=watch 集+自己名字。
3. **PM 认领**：`_observe` 命中 watch 集（`product_manager.py:46`）→ BY_ORDER 选中 PrepareDocuments→WritePRD → 产出 PRD 消息 cause_by=WritePRD（`actions/write_prd.py:188`）。
4. **下游接力**：经典线 Engineer watch WriteTasks/WriteCode/WriteCodeReview/FixBug（`roles/engineer.py:106`）；MGX 线广播消息全先汇 Mike。写码完发 `send_to="Edward"`（`engineer.py:226`）——路由押在人名/动作名字符串上。
5. **落盘记账**：文档经 project_repo 写 workspace/；调用过 `CostManager.update_cost`（`cost_manager.py:35`），超预算抛错。
6. **轮次推进**：`Environment.run`（`base_env.py:197`）并发跑一轮；Team 循环至无新消息或预算耗尽。

## 6. 关键设计决策

- **cause_by 即路由表**：无中心调度器，"谁听谁"压在 cause_by（`schema.py:239`）与 watch 集匹配上。加角色=加 watch；优点零中心化，缺点字符串契约散落。
- **repair_llm_raw_output 修复-重试闭环**：坏 JSON 时 `retry_parse_json_text`（`utils/repair_llm_raw_output.py:292`）用 tenacity after 钩子（`:245`）解析异常的 line/column→修复→**改写 retry_state.kwargs['output'] 注入下一轮**（`:278`）；重试上限按开关给 3 或 0（`:283-284`），与外层 _aask_v1 构成 3×3 环。
- **config2 双身份**：首跑生成后归用户编辑（`software_company.py:127/:152`）；优先级 env<仓 yaml<用户 yaml<kwargs（`config2.py:120-121`），不读 .env。
- **skill_loader 真实数据源**：技能加载走 `docs/.well-known/skills.yaml`（`learn/skill_loader.py:70`），**不是** metagpt/skills/——后者是 SK 时代遗产（第 7 节）。
- **经验池装饰器**：`@exp_cache`（`exp_pool/decorator.py:29`）缓存 Action 输出供 RoleZero 复用。

## 7. 坑与勘误（源码实证 Top 14）

1. **默认不走经典 SOP**：use_mgx 默认 True（`team.py:43`）→MGXEnv+Mike 仲裁；经典三角色雇佣行已注释停用（见 4.2）。
2. **DFS 求解器真坏 bug**：`strategy/tot.py:193` 引用 `self.max_steps`，但基类只有 thought_tree/llm/config 三字段，应为 `self.config.max_steps`——DFS 必然 AttributeError，ToT 的 DFS/MCTS 分支不可用。
3. **Context 反序列化丢状态**：`context.py:127` 调 model_validate_json 却丢弃返回值——pydantic v2 返回新对象非原地更新，恢复后成本账本是空的。
4. **Bedrock 成本双计**：`provider/bedrock_api.py:89` 按响应头记一次，`:136` 又把 provider.usage（同源数字）再记——花费翻倍。
5. **RunCode 无沙箱**：`actions/run_code.py:87` 直接 `exec(code)`；run_script 还自动 `pip install -r requirements.txt`——必须外置沙箱。
6. **CI secrets 暴露给 fork PR**：`fulltest.yaml:5` 与 `unittest.yaml:4` 均用 pull_request_target + checkout head SHA（`fulltest.yaml:25`）——fork PR 代码在持 secrets 上下文执行，官方警示模式。
7. **frp 调试后门**：`fulltest.yaml:49` 把 RSA_PUB 写入 authorized_keys，`:54` 起 frpc 反向 SSH 隧道——维护者需知。
8. **poignancy_action 死副本**：`ext/stanford_town/prompts/poignancy_action_v1.txt` 与 event 版**字节级相同**——action 显著度从未实现（`reflect.py:71` 只分支 event/thought/chat）。
9. **拼写错误系**：`actions/__init__.py:38` 枚举成员 `WRTIE_CODE`（应 WRITE_CODE）；`skill_action.py:24` 类名 `ArgumentsParingAction`（应 Parsing）。
10. **SKILL_DIRECTORY 死接线**：`const.py:64` 定义后零引用；metagpt/skills/ 40 技能无代码消费者，真实加载链在 skill_loader。
11. **技能描述半成品**：`management/skill_manager.py:66-74` generate_skill_desc 读模板后仅 logger.info 即返回。
12. **压缩截断 -0 陷阱**：`base_llm.py:386` `[-(keep_token-current_token_count):]`——剩余额度 0 时 -0==0，切片退化 [0:]，截断失效。
13. **RAG benchmark NameError**：`rag/benchmark/base.py:119` `if text in doc:` 的 text 未定义（应 node.text），命中即崩。
14. **人名即路由契约**：Alice/Edward/Mike 散落 write_prd/engineer/mgx_env，无单一真源。

## 8. 延伸阅读

15 步导览挑 7 步进阶：**步 2 配置体系**（调模型换供应商都在这层）；**步 4 Provider 矩阵**（30 家适配同一骨架）；**步 7 Action 层**（ActionNode 是 *_an.py 的心脏）；**步 8 Role 基类**（_observe/_think/_act 是理解一切角色的钥匙）；**步 9 Team 与 MGX**（消息总线+Mike 仲裁）；**步 10 RoleZero**（主线：LLM 输出 JSON 命令流逐条执行）；**步 14 研究扩展**（ext/ 六子包对应六篇论文）。

配套：`讲透agent-projects/MetaGPT/deepwiki/`（57 页 wiki）与同目录 explain 系列。

---

**自报**：8 节齐全（一图看懂/五分钟上手/架构总览/核心深潜/生命周期/设计决策/坑与勘误/延伸阅读）；正文不计空格字符 6485；行号锚 66 处（全部 grep/sed 逐条核实于仓库 HEAD，勘误条目均与 NOTES-DIGEST 对得上）。
