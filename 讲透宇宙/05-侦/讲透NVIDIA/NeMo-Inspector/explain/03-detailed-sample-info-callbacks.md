# 03 · 明细区九回调：callbacks/analyze_page/detailed_sample_info.py

## 角色定位

584 行、9 个 `@app.callback`，是分析页交互最重的模块——选中行展开答案详情、行内编辑写回、删除/恢复行、对比模式切换、动态增删模型列、切换文件与重排文件顺序，全部在这里。它与 `table_layouts.py` 的三层表格布局（explain 05）构成"回调层/布局层"对偶：本文件消费布局层产出的动态组件 id，又调布局层的渲染函数重建内容。全文件底色是 Dash **pattern-matching callbacks**——Input/State 用 `{"type": ..., "id": ALL}` 通配符匹配一族动态生成的组件，回调收到的都是列表。

## 内部结构

**① update_data_table（:46-95）行内编辑写回**。Input 是全部可编辑行的 value（:51 三键通配 `{type: editable_row, id: ALL, model_name: ALL}`）；定位三元组：`question_id = current_page * page_size + idx[0]`（:78）→ 逐模型按当前文件名找 `file_ids`（:79-86）→ 按 new_rows_id 的 id（字段名）+model_name 直写全局表（:88-93）。末行 `return "", js_trigger + " "`（:95）——js_container 清空、js_trigger 加一空格，触发高度重注入链（explain 06）。

**② show_item（:98-176）选中行展开**。双 Input（datatable.selected_rows + dummy_output.children :116-122）；触发源是 selected_rows 时，把第 0 列以外的列级过滤/排序输入清空（:152-154——保留 `[0]` 是全局模态框的输入）；算好各列 file_id（:156-163）后调 `get_detailed_info_table_content` 重建整片明细区（:164-173），顺带返回清空/回填的 filter 与 sorting 输入（:174-175）。无选中行直接 `PreventUpdate`（:147-148）。

**③ compare（:179-202）对比切换**：从 `ctx.triggered[0]["prop_id"].split(".")[0]` 反 json 出按钮 id（:197——本文件五处共用的惯用法），把行 key 在 `get_compared_rows()` 集合里进出切换（:198-201），返回 `dummy_data + "1"` 触发 show_item 二跳。

**④ edit_row（:205-273）编辑态切换**：结构同 ③，集合换成 `get_editable_rows()`，额外把该行图标在 EDIT_ICON_PATH/SAVE_ICON_PATH 间切换（:266-271）；真正的值写回由 ① 负责。

**⑤ del_row（:276-322）删除/恢复**：集合 `get_excluded_row()`，按钮文本 `-`↔`+`（:315-320）——同一颗按钮删了再点即恢复，渲染端遇 excluded 行输出空串（table_layouts.py:313-314）。

**⑥ add_model（:325-372）动态加列**：从表尾取 `last_header_id` 与 `last_cell_id`（:357/:363），表头 append 新模型列（:358-361，默认选中第一个可用模型），每行 append 对应单元格并保持连续编号 `last_cell_id + i + 1`（:364-370）。

**⑦ del_model（:375-411）动态删列**：反解析按钮 id 后，`for i, id in enumerate(id_del): if id["id"] == button_id: index = i + 2`（:403-405）再 `header.pop(index)`/逐行 `row.pop(index)`（:407-409）。**i+2 的算术必须拆解**：id_del 列表不含基准列（基准列无删除按钮，table_layouts.py:169 的 `i != 0`），故列表内第 i 项的真实列号是 i+1；而行 children = [key 列] + [模型列]，列号再 +1——两层偏移合成 i+2。改列布局时这行是第一雷区。

**⑧ change_file（:414-500）切文件/文本模式**：逐 trigger 用 `MODEL_SELECTOR_ID.format(...)` 模板（templates.py:17）把 prop_id 反解析回模型列号（:468-478，ValueError 则跳过——该 trigger 属其它组件族）；用 `get_file_id`（utils/common.py:407-418）定位新旧文件；**切片赋值** `table_data[button_id * len(rows_names) : (button_id + 1) * len(rows_names)] = 新列内容`（:488-499）——detailed_models_answers 的 ALL 输出是"按列分块"的扁平列表，重渲染只替换目标列那一段。基准列（button_id==0）变化时顺带 `dummy_data + "1"` 触发整表重渲染（:500，注意三元只作用于第二个返回值的可读性陷阱）。

**⑨ change_files_order（:503-584）列级过滤/排序重排文件**：三个 Input（apply_filter/apply_sorting/model_selector :508-511）；反解析列号（:548-557）；`apply_on_filtered_data` 开关决定从全量还是当前已过滤集合出发（:563-573）；调 `get_filtered_files`（utils/common.py:351-383）执行 `&&` 过滤+排序，重建该列 file_selector 的 options 并选中首个（:574-582）。**偏移契约**：`filter_functions[button_id + 1]`（:577-578）——索引 0 留给全局模态框的输入，列级输入从 1 起，与 ② 的保留 `[0]` 呼应。

## 外部连接

上游：layouts barrel 导入的四个渲染函数（get_table_column_header/get_detailed_info_table_column/get_detailed_info_table_row_content/get_detailed_info_table_content，:23-28，定义在 table_layouts.py:115/:177/:294/:341）；utils/common 的 getter 与 get_file_id/get_filtered_files/get_available_models（:35-43）；constants 的图标路径与 MODEL_SELECTOR_ID（:29-34）。下游：js_trigger/js_container（高度协议）、dummy_output（②的触发器）。add_model 按钮正是 test_ping.py:70-82 断言可见性的那个组件。

## 数据流

一次"点开某问题→编辑→保存"的完整链：简表 selected_rows 变 → ② 展开三层明细（经 get_detailed_info_table_content 逐列渲染）→ 点 ④ 进入编辑态（全局集合+图标）→ textarea 值变 → ① 把新值写进 `get_table_data()[qid][model][fid][field]` 并触发高度链 → 再点 ④ 退出编辑回到富文本渲染。删除/对比/切文件/重排都是"改全局状态集合或选择值 → 触发 ② 或 ⑧ 局部重渲染"的同构循环。全局表是唯一事实源，DOM 永远是它的投影。

## 设计决策

- **三态切换回调同构**（③④⑤）：集合进出 + 返回 dummy 变化 + 副输出（图标/文本），三个回调可以互为模板复制——新增行状态（如"收藏"）照抄即可。
- **dummy_output 二跳**：直接让 ② 监听九种 Input 会让签名爆炸；用一个隐藏哑组件当"状态变了"的统一信号（:202/:273/:322），② 只多监听一个 Input（:119-121）。
- **prop_id 反解析**是 pattern-matching 的标准代价：想知道"哪个动态组件触发"只能 json 解析 prop_id 前缀，本文件五处（:197/:246/:307/:398/:473/:552）。
- **扁平列表切片**（⑧）避免了逐单元格 Output 的签名膨胀，代价是"列分块"这一隐性布局契约散落在两处（渲染端 extend、回调端切片）。
- 已知脆弱点：⑦ 的 i+2 双偏移、⑧ 的三元可读性、①③⑤ 对 `idx` 为空的防御只在部分回调存在（:74 有、:460 有、:147 有——但 ⑨ :543-544 用 PreventUpdate，风格不一）。

## 新人提示

- 调试任何一个回调先打 `ctx.triggered[0]["prop_id"]`——pattern-matching 下"谁触发"永远是第一未知数。
- 改表格列布局先盘 ⑦ 的偏移算术与 table_layouts.py 的列构造（:278-280 的 `j * len(keys) + i` 编号），两处必须同步。
- 行 key 的语义是"数据字段名"（如 predicted_answer），不是行号——excluded/editable/compared 三集合都以它为键，跨问题共用（删了所有问题的该字段行）。
- 新增交互若需重渲染，优先复用 dummy_output 信号而非再开哑组件；若涉高度自适应记得返回 `js_trigger + " "`（照 ① :95 抄）。
