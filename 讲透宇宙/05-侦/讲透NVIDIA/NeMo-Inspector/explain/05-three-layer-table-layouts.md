# 05 · 三层表格布局：layouts/analyze_page_layouts/table_layouts.py

## 角色定位

400 行、十个布局函数，产出分析页的"简表+明细表+全局统计"三层结构。它是全仓动态组件 id 的发源地——明细区每一族组件（模型选择器、文件选择器、行名、编辑/对比/删除按钮、可编辑行）的 pattern-matching id 都在这里生成，回调层（explain 03）按 `{type, id}` 通配消费。注意本文件的独特气质：**布局函数在渲染时读数据**——`get_general_stats_layout` 甚至在布局构建期就执行用户的自定义统计函数。布局与内容分离是它的另一半设计：结构函数只造空骨架，单元格内容由 show_item/change_file 回调事后灌入。

## 内部结构

**第一层：简表** `get_short_info_table_layout`（:63-112）。单个 `dash_table.DataTable`：id="datatable"（:68），列=STATS_KEYS（question_index/problem，configurations.py:24-27）+ `get_metrics([]).keys()`（:75——借空数据调用拿到内置统计列名，聪明的反射用法）；`row_selectable="single"`（:77，选中行驱动明细区）；`page_action="custom"`+`page_size=DATA_PAGE_SIZE`（10）+`page_count=math.ceil(len/10)`（:79-82）——**服务端分页**，数据不内嵌，分页切片由 short_info_table.py:61 的 change_page 回调喂；:83-108 是紧凑样式与三条 CSS 选择器（隐藏 spreadsheet 菜单/过滤框/隐藏列按钮）。

**第二层：明细表**，四个函数搭网格：

- `get_table_header`（:155-174）：首列 `first_column`（width=2，:159-166）+ 逐模型列（:168-171，`i != 0` 决定非基准列才有删除按钮），行 id="detailed_answers_header"——add_model/del_model 回调的输出锚点。
- `get_table_column_header`（:115-152）：单列表头 = 模型选择器 + 该列专属排序/过滤/标签三个模态框按钮 + 可选删列按钮 + 文本模式开关（:133-147），内联排布（:148）。
- `get_detailed_info_table_column`（:177-191）：单元格列容器，动态 id `{type: detailed_models_answers, id}`（:185-188），首行可内嵌 file_selector（:181）。
- `get_detailed_info_table_rows`（:194-284）：逐字段行——行名（:202-205）+ 编辑/对比/删除三按钮（:207-231/:232-254/:255-268，图标按钮；FILE_NAME/LABEL 行隐藏编辑钮、FILE_NAME 行隐藏对比钮，靠 style 里的 display 控制）；列编号公式 `j * len(keys) + i`（:278-280）——列分块扁平化的编号契约，change_file 回调的切片算术（detailed_sample_info.py:488）与之严格对偶；行 id `{type: detailed_answers_row, id: i}`（:281）。

**内容渲染**：`get_detailed_info_table_row_content`（:294-338）是单列单元格的五分支状态机——排除行/越界返回空（:313-314）、FILE_NAME 返回文件选择器（:315-320）、该列文件被滤光返回空（:321-322，判据 :306-308）、可编辑行返回裸字符串（:323-324，外层 :331-337 再装进 Textarea）、普通行返回多模式富文本（:325-330，对比模式下追加 COMPARE 模式并传入 compare_to 基准文本）。`get_detailed_info_table_content`（:341-372）是列循环：zip 五元组（模型/文件号/过滤/排序/模式，:351-353），列内文件列表先经 `get_filtered_files` 过滤排序（:358-365），**compare_to 恒取基准列**（models[0] 的当前文件，:369）——对比锚点的定义就在这一行。

**第三层：统计** `get_general_stats_layout`（:375-400）：对基准模型逐问题取数（:378），逐个执行全表自定义统计并 catch 异常记日志（:379-390），拼 dataset size / overall samples / generations per sample 三个内置量（:392-398）+ 自定义统计，`html.Pre` 逐行输出（:400）。

## 外部连接

上游 import：modals_layouts 三个模态框工厂（:24-28）、common_layouts 的选择器/富文本/模式开关（:29-33）、constants 十四项（:34-48）、utils/common 九个工具（:49-60）。下游：base_layout.py 表格重建四件套全部以本文件三件（short/general_stats/detailed_info）拼装返回（:196-211/:320-336/:342-357）；回调层 five 族动态 id 消费（explain 03）。简表的列定义与 utils/common.py:390 的 `is_detailed_answers_rows_key` 共享"哪些键算统计列"的判定（STATS_KEYS + get_metrics 键）。

## 数据流

初次渲染：`get_tables_layout`（base_layout.py:339-358）→ 简表（page_count 按全局表算好）+ 统计（当场执行统计函数）+ 明细骨架（rows 按 base_model 记录的字段名生成，:347-355）。用户选中行：show_item 调 `get_detailed_info_table_content` 重灌全部 `detailed_models_answers` 容器（detailed_sample_info.py:164-173）。此后任何列级变化（切文件/模式/过滤）都走 row_content 分支机局部重渲染。结构层与内容层的边界 = `detailed_models_answers` 容器的 children 属性。

## 设计决策

- **结构/内容分离**：行骨架只在字段集合变化时重建（表格重建四件套），内容随选择高频刷新——避免整片 DOM 重挂导致的滚动位置/输入焦点丢失。
- **布局期执行统计**（:379-390）：统计函数在每次重建表格布局时重新执行而非缓存——保证过滤/编辑后统计即时反映；代价是大表上每次重渲染都全量重算。
- **列分块扁平编号**（:278-280）与回调切片（detailed_sample_info.py:488-499）是一对隐性契约，两处算术必须同步演化。
- **对比锚点固定基准列**（:369）：多列对比时每列都与基准比，列间互不比——简单且符合"评审基准模型"的工作流。
- 已知瑕疵：三按钮 style dict 各有重复 `display` 键（:223/:225-229、:246/:250-252，后者覆盖前者，前者死代码）；`:302` 可变默认参数 `text_modes=[CODE, LATEX, ANSI]`（只读未爆雷）；:90-91 `style_header` 的 `"color": "text-primary"` 是 Bootstrap 类名不是合法 CSS 颜色值，浏览器会丢弃该声明（无实际效果的装饰性代码）。

## 新人提示

- 加一列 UI 元素（如新按钮）：先在 `get_table_column_header` 或 `get_detailed_info_table_rows` 造组件+发 id，再去回调层加 pattern-matching——id 的 type 字符串是两层之间的全部接口。
- 隐藏行用 style 的 display 而非不渲染（:225-229 的写法），因为 pattern-matching 的 ALL 输出要求组件族成员稳定存在。
- 调简表列不见了：查 STATS_KEYS（configurations.py:24-27）与 get_metrics 返回键——列名即数据键，没有独立配置。
- 改分页大小只动 DATA_PAGE_SIZE（configurations.py:22），page_count 会自动重算；但已渲染页的 page_current 由回调层管，别在布局层动它。
