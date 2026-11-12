# 01 · CLI 入口与测试调度核心：greenlit.py 与 glt_core.py

## ① 角色定位

GreenLiT 的"怎么跑、怎么定义测试"由两个文件回答：`src/greenlit/greenlit.py`是唯一用户入口——参数解析、测试发现、断点续跑、报告输出全在此；`src/common/glt_core.py`（753 行）是对象模型层——属性装饰器（GLTTestAttr/GLTPlan/GLTRequires）、结果枚举与异常族（GLTTestResult）、拓扑调度器（GLTScheduler）。入口绑在 pyproject.toml:44 的 `glt-test-suite = "greenlit.greenlit:main"`；20 个硬件域 103 个装饰测试都是围绕 glt_core 协议写的普通函数，greenlit.py 只发现、排序、执行。

## ② 内部结构

greenlit.py 按执行时序分层：预检（root 检查 greenlit.py:136-142）；两段式解析——类别 flag 动态生成：`test_category_discover`（L712-728）只扫 modules/ 目录名不导入模块，`parse_arguments`（L296-336）据此刻类别 flag；选择解析（依赖闭包 BFS L607-671）；执行（`perform_tests` L340-412、SIGINT 存档 L257-272）。

glt_core.py 的类链条：`PostHooks`（L33-88，五槽位钩子容器，空槽填 no-op）→ `GLTConditionalCheck`（L91-158，all/any×true/false 四组条件槽，GLTAllowFailure/GLTConditionalSkip 是薄壳）→ `GLTRequires`（L161-266，四装饰器工厂登记 `category:name` 依赖，`can_start` 按已完成结果判定 L206-242）→ `GLTPlanType`+`GLTPlan`（L269-345，standard/disruptive 互斥 L339-342）→ `GLTTestAttr`（L348，元数据宿主：裸函数与包装器都挂 `.attr` L365-370，`_extract_cat` 从路径反推类别 L392-398）→ `GLTTestResult`（L485，六态枚举+skip/fail/warn 静态信号 L514-554）→ `GLTScheduler`（L558-753，Kahn 排序 L715-749）。

## ③ 外部连接

import 面即协作地图（greenlit.py:31-37）。三个最密触点：

1. **配置回填**：`apply_glt_configs`（greenlit.py:63-96）把 confs.d 下 YAML 逐条 append——allow-failure 进 `attr.allow_failure.any_true`（L89），conditional-skip 进 `conditional_skip.any_true`（L96）；条件经 `cond_to_func`（glt_conf.py:31）编译成函数。活例 confs/glt-confs.d/00_default.yaml:1-25。
2. **会话持久化**：`progress_save`（glt_core.py:708-713）写 test_progress.json；`--resume` 经 `progress_read`（L643-697）先全量校验再变更状态并回放结果。
3. **测试发现**：`test_case_discover`（greenlit.py:574-604）glob 扫 `glt_test_*.py`，`importlib.util.spec_from_file_location`→`exec_module`（L597-601）按文件路径加载；`test_case_init`（L703-709）捞出 `test_` 前缀函数——模块间零 import 耦合，类别天然隔离。

## ④ 数据流

主链：发现→解析（L674-700）→scheduler 建依赖表（glt_core.py:575-588）→sort()→会话→配置回填→`perform_tests` 循环：`requires.can_start` 不过→SKIP（L363-367）；conditional_skip 命中→SKIP（L369-373）；执行 `attr.func`（L375）——测试体内 `fail()` 经 inspect.stack 回查+`__wrapped__.attr` 写回同一 attr（glt_core.py:528-540）；异常分派 L377-386；finally 写 progress+dump_attrs（L387-390）；**PostHooks 五路分派**（L393-404）：PASS→postsuccess、SKIP→postskip、FAIL→postfail、AFAIL→postafail、WARN→postwarn——钩子可能直接 reboot（L405 注释），本轮终止。

进度跨进程存活：每步即时落盘（glt_core.py:626-641）；reboot 类测试靠 `arm_for_reset`（glt_utils.py:244-254）pkill -INT 逼进程存档再重启续跑。

## ⑤ 设计决策

**异常即结果**：测试体不返回值，skip/fail/warn 抛异常宣布非 PASS 终态，正常返回即 PASS（greenlit.py:375-376）。任意深度可直接 fail，代价是改写与异常必须同源——故 CLAUDE.md 明文禁止在非装饰函数里调 fail/skip，否则结果停留 NA。

**流水线实证（甄别）**：FAIL→AFAIL 降级分支疑为死代码。L381 用 `hasattr(attr.func, "allow_failure")` 判定，但 `attr.func` 是裸函数、其上只有 `.attr`（glt_core.py:365-366）；YAML 写的是 `attr.allow_failure`（greenlit.py:89，恒初始化于 L356；正确对照 glt_core.py:449）。全仓无代码给裸函数挂该属性，L381 恒 False、L382 永不执行。单测只断言写入侧（tests/greenlit/test_greenlit.py:145-183），perform_tests 在单测里只被 mock 从未真跑。此为静态推理结论。

**装饰器堆叠与类别推断**：attr 复用（L365）支持 `@GLTTestAttr()` 叠 `@GLTPlan`（cpu/glt_test_cpu_info.py:25-27），plans 从内层继承（glt_core.py:387-388）。**Kahn 重排队变体**：不建邻接表，入度非零节点回队尾重排（L734-746），O(n²) 换极简实现。

## ⑥ 新人提示

1. 非 root 无真机只能跑 tests/ 单测；`--list` 唯一无副作用（greenlit.py:793-797）；`--test-case` 与 `--list/--resume`/类别 flag 互斥（L217-240），格式必须 `category:test_name`（L205-214）。
2. 第一个测试照抄 cpu/glt_test_cpu_info.py:25-50 骨架：`@GLTCore.GLTTestAttr()`+`@GLTCore.GLTPlan("standard")`+`def test_x(sd, logger)`，docstring 带 JIRA/PATCH 溯源。
3. 调 AFAIL/conditional-skip 先读 00_default.yaml 与 glt_conf.py:31；后加载 YAML 整体覆盖同名条目（test_greenlit.py:145-183）。
4. 排查"没跑"按闸门逆推：plan 交集→类别→can_start→conditional_skip→progress 已 Completed。
5. 改动必跑 tests/greenlit/ 与 tests/common/test_glt_core*.py；resume 有历史包袱（greenlit.py:506-507 TODO：test_list 重建所有权未收敛）。
---
字数|锚数：3459|25
