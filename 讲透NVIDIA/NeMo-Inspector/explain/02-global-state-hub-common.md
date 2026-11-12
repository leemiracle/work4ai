# 02 · 全局状态中枢：utils/common.py 与模块级单例的取舍

## 角色定位

`utils/common.py`（443 行）是全仓的"数据总线"：主数据集、自定义统计、标签、行状态全集住在这里的模块级可变对象里；同时它还是工具箱——数据加载（joblib 并行）、模型答案解析、用户代码 eval、指标计算、typing 工具全在这一文件。图谱里它 fanIn 13 / fanOut 53，是无可争议的第一枢纽。理解了这个文件的"全局态 + getter"设计，Dash 回调之间的所有数据流就都通了。

## 内部结构

**九个模块级全局**（:38-47）：`dataset_data`（主数据，question_id→model_name→[文件记录] 三级嵌套）、`custom_stats`/`general_custom_stats`（行内/全表自定义统计，name→func）、`stats_raw`（统计名→用户源码，编辑器回填用）、`excluded_rows`/`editable_rows`/`compared_rows`（删行/编辑/对比三态集合）、`deleted_stats`、`labels`。**getter 群**（:50-88）一一对应（`get_table_data` :83-84、`get_editable_rows` :50、`get_excluded_row` :54、`get_compared_rows` :66、`get_custom_stats` :62 等）。

**加载线**：`get_data_from_files`（:287-348）——`@functools.lru_cache(maxsize=1)` 缓存磁盘真值；读 input_file（:291-293，死路径恒 None）；`process_model_files`（:302-328）逐文件逐行拼记录（dataset 字段横向合并 :317-321、question_index 从 1 起 :322、page_index 记文件序 :323、重名文件 `_1` 后缀去重 :305-311）；`Parallel(n_jobs=-1)`（:330-334）全核并行；聚合后逐问题逐模型算指标（:336-347）。`get_available_models`（:395-404）同样 lru_cache，把 Flask config 的 model_prediction 变注册表。

**解析线**：`parse_model_answer`（:91-160）从 Flask config 取分隔符（:106-114）、`re.escape` 后拼 code 与 code+output 两个正则（:115-119），双匹配器对位消费（:120-140）产出 explanation/code/output 序列；尾部未闭合的 code 块打 `wrong_code_block: True` 并注明 "code_block was not finished"（:143-155）——下游据此渲染红边框。

**eval 线**：`get_eval_function`（:226-239）把用户文本装进模板（:227-231）——除末行外全部成为函数体，**末行被拼成 `return <末行表达式>`**（:232-236），`exec` 后从 namespace 取出函数（:237-239）；`catch_eval_exception`（:258-274）执行期兜底——异常时把错误文本计数进 errors_dict 并返回 default_answer，其中 :270 有一处精巧过滤：错误消息末词若等于某模型名（典型的"该问题缺此模型记录"KeyError）则不计数。

**统计线**：`get_stats`（:178-200）数 correct/wrong/no_response 三比例，空数据返回 (-1,-1,-1) 哨兵；`get_metrics`（:203-223）组装三内置比例（round 两位）+ 逐个应用行内自定义统计（:206-215）；`calculate_metrics_for_whole_data`（:242-255）对全表逐问题重算并把指标 merge 进每条记录。

**辅助线**：`custom_deepcopy`（:277-284）两层浅拷贝；`get_filtered_files`（:351-383）——`&&` 拆多个过滤函数（:356-359）、逐函数 filter（:361-371）、空结果哨兵 `[{FILE_NAME: ""}]`（:374）、可选排序（:375-381）；`is_detailed_answers_rows_key`（:386-392）；`get_file_id`（:407-418）按文件名找列内索引；typing 三件 `resolve_type`/`get_type_default`/`resolve_union_or_any`（:421-442）。

## 外部连接

消费面覆盖全部九大回调与分析页布局层：表格重建四件套直接 `get_table_data().sort()` 原地排序（base_layout.py:168、:178）、过滤回退时 `clear_table_data()`+重拷（:222-224）、初次渲染灌副本（:341）；明细回调切换三个行状态集合（detailed_sample_info.py:270/:198-201/:316-320）；统计回调增删 `get_custom_stats`/`get_stats_raw`（count_stats_dataset.py:104-118）。上游依赖仅两个：Flask `current_app.config`（:106/:289/:397）与 settings/constants 的字段名常量（:26-36 import）。

## 数据流

冷启动时 `get_tables_layout` 首调 `get_data_from_files`——lru_cache 把磁盘真值钉死在进程里，`custom_deepcopy` 出工作副本灌 `dataset_data`。此后一切"过滤/排序/更新"都是对 `dataset_data` 的原地改写（或从真值重新拷贝）；一切行内交互（编辑/对比/删行）只改三个状态集合 + 单条记录字段（detailed_sample_info.py:88-93 直写 `get_table_data()[qid][model][fid][field]`）。保存回调再把 `dataset_data` 中基准模型的记录剔除 EXTRA_FIELDS 后写回磁盘（save_dataset.py:75-79）。真值层与副本层的分界就是"撤销过滤"的边界。

## 设计决策

- **模块级单例 vs Dash Store**：Store 组件要求状态在浏览器↔服务器间序列化往返，大表格（数万条带全文答案）每步交互都全量传输；服务端全局则引用直达、零拷贝。代价是单进程单用户、刷新不丢（反而是优点）——对本地工具是正确取舍。
- **getter 返回引用**：`get_editable_rows()` 拿到 set 后直接 `.add()/.remove()`——getter 是"命名入口"而非"封装边界"。想做防御性拷贝反而会破坏整个回调网（改的是副本）。
- **lru_cache 三处**（:163/:287/:395）：把"配置不变"假设编译进缓存——Flask config 在进程内不变所以安全；但测试里改 config 再调这些函数会读到旧缓存，务必注意。
- **get_eval_function 的末行即返回值**：用户写单行 `data["is_correct"]` 就是过滤谓词，写多行则最后一行必须是表达式——约定俗成、文档在 README 的过滤语法节，代码里只有模板可见。
- **命名遮蔽暗坑**：`get_metrics` 内部 :205 的局部 `custom_stats = {}` 遮蔽了模块级同名全局 :38——本函数确实只该用局部结果 dict，但读者极易在此迷路；同理 `is_detailed_answers_rows_key`（:386-392）的 `A and B and C or D` 优先级等价于 `(A and B and C) or D`，即 problem 字段（D 分支）无条件入选，不是笔误是特性。
- **`get_compared_rows` 注解 `-> Dict`（:66）实为 set**——照注解写代码会炸。

## 新人提示

- 找"数据在哪改"一律 grep getter 名而非字段名：`get_table_data()` 的调用点就是全部写点。
- 改全局结构（如给记录加字段）记得三处联动：`process_model_files` 的构造（:315-326）、`EXTRA_FIELDS`（保存时剔除，configurations.py:23）、`is_detailed_answers_rows_key`（明细区是否成行）。
- 调 exec 报错先看服务端日志：`ERROR_MESSAGE_TEMPLATE`（templates.py:15）格式化的错误计数只在 logging.error 出现，UI 上静默。
- 不要在回调里 import 本文件之外再造状态——所有状态都该挂在这里，否则刷新语义和撤销语义都会破。
