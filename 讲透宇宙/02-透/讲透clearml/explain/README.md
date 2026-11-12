# explain 索引（clearml 重要文件精讲 12 篇）

> 六节结构：角色定位/内部结构/外部连接/数据流/设计决策/新人提示。字数口径=不计空格字符 2500-4800/篇；行号锚全部 grep -n 实证（26/26 抽验命中，含 1 处差行修正）。

## SDK 核心线

| 篇 | 文件 | 主题 |
|---|---|---|
| 01 | clearml/task.py | Task 门面（5000+ 行核心，init 生命周期/get_tasks:1516） |
| 02 | clearml/backend_api/session/ | 通信层（session/client/apiproxy） |
| 03 | clearml/config/ | 配置体系（sdk.conf 多级加载+环境变量双名回落） |
| 04 | clearml/backend_interface/task/ | repo 捕获/脚本分析 |

## 存储/自动化/绑定线

| 篇 | 文件 | 主题 |
|---|---|---|
| 05 | clearml/storage/helper.py | Storage 五协议驱动（4800+ 行，S3/GS/Azure/File） |
| 06 | clearml/automation/controller.py | PipelineController 流水线 |
| 07 | clearml/binding/ + frameworks/ | 框架自动绑定捕获原理 |
| 08 | vendored 六库 | jsonmodels/pigar/requests_toolbelt/pyrsmi/distutils_version 内嵌哲学 |

## CLI/工具/示例线

| 篇 | 文件 | 主题 |
|---|---|---|
| 09 | clearml/cli/task/ | `clearml-task` 远程执行命令 |
| 10 | clearml/utilities/http_router/ | HttpRouter 本地端口转发 |
| 11 | examples/frameworks/ | 框架集成示例体系（19 框架矩阵） |
| 12 | clearml/utilities/gpu/ | GPU 监控三驱动（gpustat/pynvml/pyrsmi） |
