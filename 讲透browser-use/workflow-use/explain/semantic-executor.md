# workflow/semantic_executor.py — 语义执行臂：以可见文本为锚的零/低 AI 执行器

> 源文件：`workflows/workflow_use/workflow/semantic_executor.py`（3229 行，仓内最大单文件）

## 一、角色定位

`SemanticWorkflowExecutor`（L31）是"语义工作流"路线的执行端，与 `Workflow`（service.py）的确定性控制器路线互补：`Workflow.run_with_no_ai`（service.py L1047）把整个步骤循环交给它；`Workflow._execute_step` 在"无 cssSelector 但有 target_text"时也按步借调它（service.py L647-661）。它的核心主张：**执行前重建"文本→选择器"映射，以 target_text 为主锚，四层选择器瀑布兜底，配验证-重试闭环**。它是纯 CDP 实现（无 Playwright locator），全部元素操作经 `Runtime.callFunctionOn`/`Input.dispatchKeyEvent` 完成。

## 二、内部结构

- **构造参数**（L34-57）：`max_retries=3`、`max_global_failures=5`、`max_verification_failures=3` 三个熔断阈值；`enable_step_verification=False`——注释明言"Disabled by default until fully stable"（L41），`StepVerifier` 只在开启时创建（L57）。
- **CDP 元素工具族**（L59-208）：`_get_elements_by_selector`（xpath= 前缀直接跳过返回空，L67-68）、`_element_get_property`/`_element_evaluate`（L76/L104，`Runtime.callFunctionOn` 通道）、checked/visible/input_value 探测（L132/137/145）、`_element_press_key`（L150，手工 keyDown/keyUp 双事件，L166-174 键位表）。
- **元素定位三件套**：`_find_element_by_text`（L225，语义映射匹配+自有三级兜底）、`_find_element_by_pattern`（L356，动态 ID 模式匹配）、`_try_direct_selector`（L526，把 target_text 直接当 id/name/data-testid/placeholder 试）。
- **十个 execute_*_step**：navigation L687 / click L743 / input L1401 / select L1641 / key_press L1721 / scroll L1809 / go_back L1818 / go_forward L1827 / button L1836 / extract L2586；统一入口 `execute_step`（L1863）isinstance 分派。
- **验证重试核心** `_execute_with_verification_and_retry`（L1901）与错误上报链（L2088-2109）。
- **领域助手群**（L2717 起）：日历选日期、下拉选顶、航班选项打分（L3028/L3208）等预订场景专用工具。

## 三、外部连接

上游：`Workflow`（两条路径如上）；`SemanticExtractor`（L44 实例化，每步刷新映射）。下游：browser-use `Browser`/`Page` 的 CDP 接口（大量 `_client.send.*` 私有通道）、`ElementFinder`（click 步骤 P1 策略里延迟导入避免循环依赖，L760）、`StepVerifier`/`VerificationResult`（L26）、`ErrorReporter`（L24）、schema 层 8 种 Step 视图（L14-23）。LLM 仅在 `execute_extract_step` 使用（`page_extraction_llm`，L2662）——这是"optional AI extraction"的全部含义。

## 四、数据流

`execute_step`（L1863）每步先 `_refresh_semantic_mapping`（L1866，注释："避免过期选择器"），再分派到具体执行器。以最复杂的 `execute_click_step`（L743）为例：

1. **P1 显式 selectorStrategies**（L754-812）：工作流定义自带的多策略优先；命中 xpath 策略时用 `document.evaluate` JS 直接点（L778-797），这是 service.py 明确拒接、留给本模块的职责。
2. **P2 语义映射**（L814-855）：有 position_hint/container_hint 走 `_find_element_by_pattern`（动态 ID 三正则 L377-379；四级优先级：精确 ID→结构容器内可点元素→关键词模糊→容器提示，L383-477；位置选择 first/last/数字在 L483）；否则 `_find_element_by_text`。平行试 `_try_direct_selector`（L840）命中 id/name 优先；映射命中按"hierarchical 含 # 或 :nth-of-type 优先"选层（L850-855）。
3. **P3 遗留回退**（L864-893）：cssSelector → xpath → 抛错；错误消息附**页上现有元素前 15 个 key 与相似文本 top5**（L875-890），排障体验极佳。
4. **等待瀑布**（L896-922）：fallback_selectors（hierarchical → fallback_selector → `xpath=`text_xpath），`_wait_for_element`（L638）0.1s 轮询。
5. **智能点击**（L1046）：先试纯 JS 四级文本匹配（L939）完全绕过选择器；文本失败且无任何选择器时拒绝点击（L1059-1062）——宁错勿点错；radio/checkbox 特判含 Radix UI `button[role=radio]`（L1086）与 `pointer-events:none` 隐藏 input 改点容器（L1117-1123）；按钮场景逐个读 textContent（上限 20 个、每个 1s 超时，L1177-1184）；submit 关键词（L1213-1216）点击后比对 URL，同页则查校验错误后"假定成功"（L1249-1257）。
6. **验证-重试**（L1901）：入口三道熔断闸（L1904/L1909/L1914）；重试前刷新映射+sleep 1s（L1928-1930）；执行后先查表单校验错误（L2119，15 个关键词过滤 L2132-2151）再验证（StepVerifier 的 SUCCESS/SKIPPED 分流，SKIPPED 回落旧验证器，L1953-1967）；成功清零全部计数器（L1974-1976）；最终失败做五类错误分类（L2034-2047，连续失败升级 SYSTEMATIC_FAILURE L2050-2051）、截图到 `./.workflow_screenshots`（L2065-2077）、组 `ErrorContext` 上报（L2088-2109）后重抛。

提取步骤（L2586）是唯一 LLM 路径：HTML → markdownify（strip a/img/script/nav 等，L2613-2616）→ 5 万字符截断保头尾各半（L2622-2627）→ 单 prompt `ainvoke`（L2662）→ 失败降级为 raw content 前 2000 字符（L2685-2700）；无 LLM 时退化为 innerText 前 1000 字符预览（L2591-2605）。

## 五、设计决策与取舍

- **每步重建映射**（L1866）牺牲一次全页 DOM 抽取换"永不 stale"——对 SPA 是正确交易，代价是大页面的抽取耗时。
- **文本优先、选择器兜底的保守哲学**：文本点击失败且无选择器时明确拒绝（L1059-1062）；而验证端反过来宽松——按钮消失视为成功（L2474-2480），通用点击目标"存在"与"消失"都返回 True（L2486-2495）。执行端防误点、验证端防误报，方向相反但目的一致：降低假失败。
- **CDP 纯净性约束**：xpath= 在 `_get_elements_by_selector` 与 `_wait_for_element` 里都被跳过（L67/L656），label:has-text 等 Playwright 语法多处以注释标注"not supported in CDP"（L623/L1602/L2169）——移植 Playwright 习惯会踩坑。
- **三计数器状态机**：全局(5)/连续(3)/连续验证(3)各自独立熔断，成功统一清零（L1974-1976）——比单一 retry 计数更能区分"系统性坏"与"偶发抖动"。
- **select 元素输入幂等**：input 步骤发现目标是 SELECT 直接返回"Ignored"（L1499-1503），避免 fill 到下拉框产生垃圾。
- **submit 判定靠关键词表**（L1213-1216）而非表单语义——本地化按钮文案（如德语）会漏判，只能靠 selectorStrategies 兜。

## 六、新人提示（坑/勘误）

1. `_verify_click_action` 里 L2440 对 `element_info['selectors']` 逐字符迭代（`for sel in ...`）——selectors 是字符串时是逐字符循环，几乎必然空转；这是把"多选择器列表"的旧假设带进了"单字符串"新世界的化石代码。
2. L2117 `return last_result` 在 raise 之后永不执行；L1982 的 pass 分支计数逻辑依赖循环外 L2030 统一累加——读计数器代码别漏掉循环外的 `global_failure_count += 1`。
3. click P1 的 xpath 点击 JS 里 `escaped_xpath` 只转义单引号（L777），xpath 含反斜杠/换文仍有注入面。
4. 领域助手群（L2717 起，calendar/flight/dropdown）与核心执行链无耦合，是演示/实验代码；`find_element_with_context`（L2717）docstring 自称"demonstrates"——别当生产路径读。
5. `_execute_with_verification_and_retry` 的异常关键词分类（L2011-2020）匹配的是错误字符串而非异常类型——自定义异常消息里含 "timeout" 会被误分类。
6. 三处 execute 步骤（select/key_press）不做 `_try_direct_selector`（只有 click/input 做），target_text 恰是元素 id 时这两类步骤只能靠映射或 cssSelector。
