# 07 Stanford Town 小镇模拟：Generative Agents 的 MetaGPT 移植

## 1. 角色定位

Stanford Town 是 Park et al. 2023《Generative Agents: Interactive Simulacra of Human Behavior》的完整移植——25 个 LLM 驱动的小镇居民按时刻表生活、社交、反思并涌现出派对行为。它是 MetaGPT 中罕见的"仿真型"多智能体子系统：软件公司线（Role/Action/Team）求解任务，这里则求解"像人"。选址勘误：任务描述指向 `metagpt/environment/stanford_town/`，该目录其实只有 3 个文件的环境适配层；认知主体在 `metagpt/ext/stanford_town/`（actions/memory/plan/reflect/roles/prompts/utils 十余个子包）。入口 `stanford_town.py:15` 定义 `class StanfordTown(Team)`，复用 Team 的hire/run 骨架但 hire 只收 STRole（`stanford_town.py:26`）。

## 2. 内部结构

物理世界与认知架构两轴。物理世界在 `metagpt/environment/stanford_town/stanford_town_ext_env.py`：`StanfordTownExtEnv(ExtEnv)`（L25）持有 `maze_width=140/maze_height=100/sq_tile_size=32` 默认值（L29-31），核心是 `@model_validator(mode="before")` 的 `_init_maze`（L41）——构造期一口气读完 the Ville 全部地图资产：`maze_meta_info.json`（L47）取宽高；special_blocks 五张"色块编号→语义标签"表（world/sector/arena/game_object/spawning_location，L64-92，world 表取 `wb_rows[0][-1]` L66，game_object 表 sector 列恒为 `<all>`）；五个迷宫矩阵 CSV 经 `read_csv_to_list(_cm, header=False)[0]` 读入（L97-107）。随后 L124-130 按宽度切片重塑二维网格，L141-159 组装逐格 dict 的 `tiles`，L172-208 构建反向索引 `address_tiles`（注释自述 optimization component，如 `address_tiles['<spawn_loc>bedroom-2-a'] == {(58, 9)}` L177）。

认知架构在 `metagpt/ext/stanford_town/`：`st_action.py:36` 的 `generate_prompt_with_tmpl_filename` 用 `open(prompt_dir/tmpl_filename)` 运行时读 20 个 txt 模板并替换 `!<INPUT N>!` 占位符；`reflect.py:71` 的 `generate_poig_score` 对 "is idle" 直接返回 1（L73），event/thought 走 `AgentEventPoignancy`（L76），chat 走 `AgentChatPoignancy`（L79）；`memory/retrieve.py:14` 的 `agent_retrieve` 实现 Generative Agents 签名的三因子检索——importance（poignancy）、recency、relevance 分别提取（L40-42）后按 gw 加权求和（L49），recency 是 `memory_forget**day_count` 指数衰减（L126）；`memory/scratch.py:14` 的 `Scratch(BaseModel)` 存人物超参与人格（vision_r=4/att_bandwidth=3/retention=5，L16-18）；`roles/st_role.py:63` 的 STRole 在执行移动时经 `self.rc.env.observe()["collision_maze"]` 消费重塑后的碰撞矩阵并调 `path_finder` 寻路（L418-434）。

## 3. 外部连接

向上：StanfordTown 继承 `metagpt/team.py` 的 Team；ExtEnv 基类来自 `metagpt/environment/base_env.py`（勘误：`environment/README.md` 仍描述旧版 ext_env.py 布局）。向旁边：`utils/const.py` 的 `STORAGE_PATH/TEMP_STORAGE_PATH`（L10-11）指向 examples/stanford_town 的仿真目录；`utils/mg_ga_transform.py` 的 `save_movement`（L19）/`save_environment`（L34）落盘 movement JSON，供上游 generative_agents 的 Django frontend_server 可视化消费（README 称其"前端服务"，实为仿真可视化服务器，与 MetaGPT 本体无依赖）。资产层：`static_dirs/assets/the_ville` 是上游 the Ville 地图的原样拷贝；`utils/const.py:15` 的 `collision_block_id = "32125"` 与 collision_maze.csv 唯一非零值精确配对。

## 4. 数据流

启动流：maze CSV + blocks CSV → `_init_maze` → tiles/address_tiles/collision_maze 常驻环境对象。认知循环：persona 种子 JSON → Scratch（人格+时刻表）→ plan 逐时分解动作 → 动作执行产生 event/chat → 写入 agent_memory（带 poignancy 分）→ 下一步决策前 `new_agent_retrieve`（retrieve.py:58）三因子取回相关记忆 → 周期性 run_reflect 生成洞察再入记忆。模板流是运行期字符串拼装：action 文件按文件名加载 txt（st_action.py:36），无 import 关系——图谱中模板到代码的连接全部是 depends_on 动态边。

## 5. 设计决策

其一，prompt 全部外置 txt 而非 Python 常量，为与上游逐字对齐、可 diff 可替换，代价是静态分析零可见（scanner batchImportData 全空）。其二，`model_validator(mode="before")` 在构造期完成全部资产 IO，环境对象即世界状态快照，简单但不可增量加载。其三，address_tiles 反向索引用空间换寻路时间（L172-176 注释明言）。其四，importance 直接复用 LLM 实时打分的 poignancy 而非事后评估——把"记忆值得记多久"交给模型自己判断，这是论文的核心赌注。三处踩坑实锤：poignancy_action_v1.txt 与 poignancy_event_v1.txt `diff` 零差异且首行自报名都写 "poignancy_event_v1.txt"——action 版是从 event 版复制后从未按 action 语义改写的死副本，全仓无消费方，因为 reflect.py:71 的分支只有 event/thought/chat 三路，thought 显著度复用 event 模板；模板头 Variables 注释普遍滞后于正文槽位——action_location_sector_v1.txt 头注释只标 INPUT 0..9（L1-10）而正文 L34 用到 `!<INPUT 10>!/!<INPUT 11>!`，insight_and_evidence_v1.txt 把 INPUT 1 注释为 persona name 实为数量，以正文为准；五个迷宫 CSV 是"单行扁平"格式——collision_maze.csv `wc -l` 为 0、逗号分域恰 14000 个（140×100），看起来空文件实为 42KB，必须配合 maze_meta_info.json 的宽度才能重塑，单元格值是 special_blocks 色块编号而非坐标，脱离 blocks 字典无语义。

## 6. 新人提示

先读论文再看代码，目录结构与论文章节（memory stream/retrieval/reflection/planning）一一对应。改主持词/prompt 时只动 prompts/ 下 txt，注意占位符按位置传参、头注释不可信。调试"为什么角色不动"先查 collision_maze 与 collision_block_id 是否匹配，再查 path_finder 的目标 tile 是否在 address_tiles 里。想接入自己的地图：用 Tiled 导出五层色块 CSV（单行扁平）+ special_blocks 字典 + maze_meta_info.json 三件套。读懂本子系统的关键是抓住"记忆即世界模型"——tiles 是物理世界，agent_memory 是认知世界，两者经 observe() 与 movement 回写缝合。
