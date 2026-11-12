# JiuwenBox

JiuwenBox（包名 `jiuwenbox`）是沙箱服务。它用 FastAPI 管理沙箱的创建、停止、文件传输和命令执行。隔离范围由策略文件决定，服务在自己的进程里把策略落到具体的运行时。

安装、启动参数和 HTTP 接口以 [jiuwenbox/README_CN.md](../../../jiuwenbox/README_CN.md) 为准。

---

## 1. 代码怎么分

| 目录 | 职责 |
| --- | --- |
| `jiuwenbox/src/jiuwenbox/server` | 服务：生命周期、策略加载、审计、路由 |
| `jiuwenbox/src/jiuwenbox/supervisor` | 把策略翻译成隔离措施 |
| `jiuwenbox/src/jiuwenbox/models` | 策略、沙箱和接口的数据模型 |
| `jiuwenbox/src/jiuwenbox/proxy` | 推理请求的隐私代理，负责路由和密钥注入 |
| `jiuwenbox/src/jiuwenbox/configs` | 随包提供的策略样例 |

策略样例包括 `default-policy.yaml`、`code-agent-policy.yaml`、`enterprise-policy.yaml`、`inference-policy.yaml`、`java-policy.yaml` 和 `windows-policy.yaml`。未设置 `JIUWENBOX_POLICY_PATH` 时，服务使用包内的 `default-policy.yaml`。

## 2. Linux 上的隔离

Linux 运行时用 bubblewrap 启动沙箱进程。策略还可以打开网络命名空间、Landlock、seccomp，以及命名空间和 capability 限制。网络隔离需要 iproute2、iptables 和 nftables。需要跑 JavaScript 时，环境里要有 nodejs。

默认监听端口是 8321。换策略时把 `JIUWENBOX_POLICY_PATH` 设成该文件的绝对路径。

## 3. 和本仓库其它组件的关系

JiuwenBox 是独立服务。Agent SSAS 不负责创建沙箱。agent-shield 也不启动这个服务。调用方自己持有沙箱地址，按 README 里的接口管理沙箱。
