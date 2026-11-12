# MCP 接入层导览

MCP 接入层将宿主发来的 Python 代码交给独立 worker 执行，并管理输出、取消和进程退出。它不实现控件查找、输入选路或原生动作，这些由 `computer_use` SDK 与平台驱动负责。

## 进程关系

```text
宿主 / MCP 客户端
  └─ MCP 服务进程：server → ExecutionSession
       └─ 持久 worker 进程：runtime.Runtime
            ├─ 模型代码的 Python 命名空间
            └─ computer_use SDK（computer_use_engine/，同进程导入）
                 └─ 平台驱动进程
```

worker 是执行进程，engine 是它导入的库，不是 worker 旁边的另一个服务。Runtime 负责执行代码与交付结果，桌面操作由 SDK 完成。worker 的进程隔离保护协议与生命周期，不构成权限沙箱。

## 文件按职责归类

| 类别 | 文件 | 职责与状态归属 |
| --- | --- | --- |
| MCP 入口 | `__init__.py` | 包标识；无运行状态。 |
| MCP 入口 | `__main__.py` | `python -m computer_use_mcp` 的入口，转到 server.cli。 |
| MCP 入口 | `server.py` | 注册工具、校验参数、协商能力、发送 MCP 通知；服务进程创建 ExecutionSession。 |
| 执行生命周期 | `session.py` | 服务进程监督 worker；持有在途执行、45 秒无进展看门狗、reset/退出屏障、HistoryGate 与 Journal。 |
| 执行生命周期 | `runtime.py` | worker 入口；持有 Python 命名空间、Computer 实例、执行守卫与输出回调；调用 SDK，不直接实现桌面动作。 |
| 内容交付 | `output.py` | OutputBuffer 限额与合并；ObservationOutput 暂存与去重；ObservationPresenter 保存差分基线。服务和 worker 各有独立输出缓冲，观察基线只在 worker。 |
| 内容交付 | `history.py` | 服务侧历史游标合同；判断宿主是否保留上次交付，向 worker 发重置/增量策略。它不持有观察正文或差分基线。 |
| 通信与平台适配 | `worker_transport.py` | worker 私有通道连接、Windows 客户端认证、帧编解码、兼容旧 JSONL、诊断批量发送；不管理进程或重试。 |
| 通信与平台适配 | `windows_worker.py` | Windows 端创建 worker、Job Object 绑定、认证监听与后代退出屏障；保持平台机制独立。 |
| 诊断记录 | `diagnostics.py` | IPC 与日志共用的诊断 JSON 编码；服务进程的 Journal 写 JSONL 日志及日志元数据。导入模块不创建日志，只有实例化 Journal 才创建。 |
| 可选桌面接入 | `desktop_bridge.py` | 在交互登录会话中创建完整 MCP 子进程，认证并转发 MCP stdio；不只是转发引擎到驱动的协议。它有独立 CLI 与连接生命周期。 |
