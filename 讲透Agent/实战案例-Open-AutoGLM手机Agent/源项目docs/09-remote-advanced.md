# 09 · 远程设备与高级用法

> 本文整合了三块进阶内容：远程设备连接（WiFi 调试）、交互模式（REPL）、自定义回调实战。
> 源材料来自 [README.md](../README.md)、`examples/basic_usage.py` 和 [DeepWiki 5.3/5.5/6.3](https://deepwiki.com/zai-org/Open-AutoGLM/5-user-guide)。

## 三大主题速览

| 主题 | 何时用 | 看哪节 |
|------|-------|-------|
| **远程设备连接** | 手机不在电脑边、生产部署、协助远方老人 | [§1](#1-远程设备连接) |
| **交互模式** | 探索式任务、不知道完整指令、调试 | [§2](#2-交互模式) |
| **自定义回调** | 接入 Web UI / Slack / 日志系统、自动化运维 | [§3](#3-自定义回调实战) |

---

## 1. 远程设备连接

### 为什么需要远程

- 手机插在客厅 WiFi 调试，电脑在书房
- 生产部署：树莓派 + 手机放机房，远程触发任务
- 协助远方老人操作手机（老人手机开 WiFi 调试）
- CI/CD：测试农场多台手机分布式跑

### 三平台 WiFi 调试对照

| 平台 | 准备 | 连接命令 | 默认端口 |
|------|------|---------|---------|
| Android (ADB) | 开发者选项里开"无线调试" | `adb connect IP:PORT` | 5555（或随机）|
| HarmonyOS (HDC) | 系统更新→开发者选项→无线调试 | `hdc tconn IP:PORT` | 5555 |
| iOS | 设备与主机同 WiFi，WDA 监听 8100 | `--wda-url http://IP:8100` | 8100 |

### 1.1 Android（ADB）远程

#### 步骤 1：手机开无线调试

`设置 → 开发者选项 → 无线调试`（开启）。部分 Android 11+ 会显示**随机端口**，记下来。

#### 步骤 2a：电脑直接 connect（手机已开无线调试）

```bash
adb connect 192.168.1.100:5555
adb devices    # 验证：应显示 192.168.1.100:5555 device
```

#### 步骤 2b：从 USB 转 WiFi（手机暂连 USB）

```bash
# 方法 1: CLI 命令
python main.py --enable-tcpip          # 默认 5555 端口
# 输出类似:
# ✓ Enabled TCP/IP mode on port 5555
# You can now connect remotely using:
#   python main.py --connect 192.168.1.100:5555

# 方法 2: 原生 adb 命令
adb tcpip 5555                          # 切到 TCP 模式
adb shell ip route | grep wlan          # 查 IP
# 然后拔线
adb connect 192.168.1.100:5555
```

#### 步骤 3：用 Agent

```bash
# 直连 IP:port
python main.py --device-id 192.168.1.100:5555 \
  --base-url http://localhost:8000/v1 \
  "打开抖音刷视频"

# 或环境变量
export PHONE_AGENT_DEVICE_ID=192.168.1.100:5555
python main.py "打开抖音刷视频"
```

#### Python API

```python
from phone_agent.adb import ADBConnection, list_devices

conn = ADBConnection()
success, msg = conn.connect("192.168.1.100:5555")
print(f"连接: {msg}")

# 列出所有设备(含连接类型)
for d in list_devices():
    print(f"{d.device_id} - {d.connection_type.value}")  # USB / WIFI / REMOTE

# USB 转 TCP
conn.enable_tcpip(5555)
ip = conn.get_device_ip()
print(f"设备 IP: {ip}")

# 断开
conn.disconnect("192.168.1.100:5555")
conn.disconnect()   # 无参数 = 断开所有
```

### 1.2 HarmonyOS（HDC）远程

```bash
# 手机端: 设置 → 系统和更新 → 开发者选项 → USB 调试 + 无线调试
# 记下显示的 IP:端口

# 电脑端
hdc tconn 192.168.1.100:5555
hdc list targets    # 验证

# Agent
python main.py --device-type hdc \
  --device-id 192.168.1.100:5555 \
  "打开抖音"
```

Python API 同 ADB 模式，把 `ADBConnection` 换成 `HDCConnection`。

### 1.3 iOS（WebDriverAgent）远程

iOS 不用"connect"命令，直接在 CLI 指定 WDA URL：

```bash
# 前提: iPhone 已越狱或通过 Xcode 跑起 WDA,且 WDA 监听 0.0.0.0:8100
# 在 iPhone 设置里查 WiFi IP

python main.py --device-type ios \
  --wda-url http://192.168.1.50:8100 \
  "Open Safari"
```

**iOS 远程调试更复杂**：默认 WDA 通过 `iproxy 8100 8100` 走 USB 隧道。要走 WiFi，需要在 Xcode 里启动 WDA 时让它监听所有网卡（`WebDriverAgentRunner` 的 product scheme 改 `--allow-remote-connections`）。

### 1.4 多设备管理

```bash
# 列出所有连接的设备
python main.py --list-devices

# 输出示例(多设备):
# Connected devices:
# ------------------------------------------------------------
#   ✓ emulator-5554                    [USB]
#   ✓ 192.168.1.100:5555               [WIFI]
#   ✓ 192.168.1.101:5555               [WIFI]

# 指定某台
python main.py --device-id emulator-5554 "任务 A" &
python main.py --device-id 192.168.1.100:5555 "任务 B" &
wait
```

### 1.5 远程连接故障排查

| 症状 | 可能原因 | 解决 |
|------|---------|------|
| `Connection refused` | 端口没开 / 防火墙 | 检查手机无线调试状态；防火墙放行 5555 |
| `unable to connect to ...:5555` | 设备不在线 / IP 变了 | `adb devices` 看；手机重启 WiFi |
| 设备重启后失联 | 多数设备重启会禁用 TCP/IP 模式 | USB 重新 `adb tcpip 5555` |
| 多设备时不知用哪台 | 默认用第一台 | 加 `--device-id` 指定 |

### 1.6 远程生产部署架构

```
┌──────────────────────────────────────────────────────────────┐
│  控制节点(云服务器/树莓派)                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Open-AutoGLM Agent  +  vLLM/SGLang 模型服务            │  │
│  └────────────────┬───────────────────────────────────────┘  │
└───────────────────┼──────────────────────────────────────────┘
                    │ WiFi / 局域网
                    ▼
┌──────────────────────────────────────────────────────────────┐
│  手机农场(机柜)                                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │ 手机 1  │  │ 手机 2  │  │ 手机 3  │  │ 手机 N  │          │
│  │充电+WiFi│  │充电+WiFi│  │充电+WiFi│  │充电+WiFi│          │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘          │
│  192.168.1.10  .11          .12          .13                  │
└──────────────────────────────────────────────────────────────┘
```

控制节点远程触发每台手机跑任务，适合自动化测试、内容爬取、批量操作。

---

## 2. 交互模式

### 2.1 进入交互模式

**不传 task 位置参数**即进入交互模式：

```bash
python main.py --base-url http://localhost:8000/v1
# 输出 header 后:
# Entering interactive mode. Type 'quit' to exit.
#
# Enter your task:
```

### 2.2 REPL 用法

```
Enter your task: 打开微信给张三发消息"你好"
... agent 执行 ...
Result: 已成功发送消息

Enter your task: 再给李四发"晚上一起吃饭"
... agent 执行 ...
Result: 已成功发送消息

Enter your task: quit
Goodbye!
```

**关键行为**：
- 每个任务完成后调 `agent.reset()` **清空上下文**（详见 [02-agent-loop.md](02-agent-loop.md#reset清空状态)）
- 任务之间**不共享记忆**——上一个任务的对话历史不带到下一个
- `quit` / `exit` / `q` 退出
- `Ctrl+C` 也退出（`KeyboardInterrupt` 被捕获）
- 单任务异常被 catch 打印，**不退出** REPL

### 2.3 何时用交互模式

| 场景 | 适合？ |
|------|-------|
| 探索性操作（"看看微信有什么新消息"）| ✅ |
| 连续多任务（早上开机例行操作）| ✅ |
| 不确定完整指令，想边问边做 | ✅ |
| 自动化脚本（cron / CI）| ❌ 用单任务模式 |
| 需要任务间共享上下文 | ❌ 自己用 `step()` 写 |

### 2.4 非交互模式（脚本/CI）

```bash
# 单任务(自动退出)
python main.py "打开微信"

# 在脚本里
python main.py "任务 1" && python main.py "任务 2"

# cron 定时
0 9 * * * cd /path/to/Open-AutoGLM && python main.py "打开钉钉打卡"
```

### 2.5 TTY 环境

交互模式依赖 `input()`，需要**TTY 终端**。在以下环境会报 `EOFError: EOF when reading a line`：

- IDE 输出面板（部分）
- 某些 CI 日志收集器
- `python main.py < /dev/null`
- `python main.py < input.txt`（这种重定向也算非 TTY）

**解决**：用单任务模式 `python main.py "task"`，或换 TTY 终端（ gnome-terminal / iTerm）。

---

## 3. 自定义回调实战

### 3.1 回调机制回顾

Open-AutoGLM 有两个回调注入点（详见 [04-action-handler.md](04-action-handler.md#关键-handler-详解)）：

| 回调 | 触发时机 | 签名 | 默认实现 |
|------|---------|------|---------|
| `confirmation_callback` | 模型点击带 `message` 字段的 Tap（敏感操作）| `(message: str) -> bool` | `input("Y/N")` |
| `takeover_callback` | 模型输出 `Take_over` 动作（登录/验证码）| `(message: str) -> None` | `input("Enter to continue")` |

**关键约束**：回调必须**阻塞**直到用户响应。Agent 主循环在调用期间停住。

### 3.2 默认终端实现

```python
# actions/handler.py:321-329
@staticmethod
def _default_confirmation(message: str) -> bool:
    response = input(f"Sensitive operation: {message}\nConfirm? (Y/N): ")
    return response.upper() == "Y"

@staticmethod
def _default_takeover(message: str) -> None:
    input(f"{message}\nPress Enter after completing manual operation...")
```

### 3.3 注入自定义回调

构造 PhoneAgent 时传入：

```python
from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig

agent = PhoneAgent(
    model_config=...,
    agent_config=AgentConfig(...),
    confirmation_callback=my_confirmation,   # ★ 注入
    takeover_callback=my_takeover,           # ★ 注入
)
```

iOS 版 `IOSPhoneAgent` 同样接受这两个回调。

### 3.4 实战案例 1：Web UI 确认

适合远程/无头场景，通过 Web 界面让用户确认：

```python
import time
import requests

def web_confirmation(message: str) -> bool:
    """通过 Web 界面弹窗让用户确认。"""
    # 1. 通知前端弹窗
    requests.post("http://localhost:3000/api/notify", json={
        "type": "confirmation",
        "message": message,
        "timestamp": time.time(),
    })

    # 2. 长轮询等用户响应
    while True:
        try:
            r = requests.get("http://localhost:3000/api/pending", timeout=5)
            data = r.json()
            if data.get("resolved"):
                return data["approved"]
        except requests.RequestException:
            pass    # 网络抖动继续等
        time.sleep(0.5)
```

前端可以是个 React 页面，收到 `/api/notify` 后弹 modal 显示 message + "允许 / 拒绝"按钮，点完 POST 回 `/api/pending`。

### 3.5 实战案例 2：Slack 通知接管

适合协助远方老人：Agent 卡在登录时，Slack 通知子女远程接管：

```python
import requests
import time

SLACK_WEBHOOK = "https://hooks.slack.com/services/..."

def slack_takeover(message: str) -> None:
    """通过 Slack 通知子女,等子女在 Slack 回复 done。"""
    requests.post(SLACK_WEBHOOK, json={
        "text": f"👵 妈妈的手机需要帮助: {message}\n完成后请回复 'done'",
    })

    # 轮询 Slack API 等子女最新消息是 "done"
    while not _wait_for_slack_reply("done", timeout=600):
        time.sleep(10)
        requests.post(SLACK_WEBHOOK, json={"text": "⏰ 还在等帮助..."})

def _wait_for_slack_reply(keyword: str, timeout: int) -> bool:
    # 调 Slack conversations.history API 检查最新消息
    # 简化实现,实际需 OAuth token
    return False
```

### 3.6 实战案例 3：自动允许 + 日志

适合受信场景（自己的设备、低风险任务），自动批准但仍记录审计：

```python
import logging
from datetime import datetime

audit_log = logging.getLogger("autoglm_audit")
audit_log.addHandler(logging.FileHandler("audit.log"))

def auto_approve_with_log(message: str) -> bool:
    """自动允许敏感操作,但记审计日志。"""
    audit_log.warning(f"AUTO_APPROVED | {datetime.now()} | {message}")
    return True

def log_only_takeover(message: str) -> None:
    """记录接管事件,不真的等用户。"""
    audit_log.warning(f"TAKEOVER_NEEDED | {datetime.now()} | {message}")
    # 不阻塞,直接返回(Agent 会继续下一步)
```

⚠️ **风险**：`auto_approve_with_log` 会让 Agent 自动完成支付/删除等敏感操作。仅在受信环境用。

### 3.7 实战案例 4：超时拒绝

防止 Agent 在某个登录页卡死，超时自动拒绝：

```python
import threading

def timeout_confirmation(message: str, timeout: int = 30) -> bool:
    """30 秒不响应就拒绝。"""
    result = {"approved": None}

    def get_input():
        try:
            r = input(f"{message}\nApprove? (Y/N): ")
            result["approved"] = (r.upper() == "Y")
        except EOFError:
            result["approved"] = False

    t = threading.Thread(target=get_input, daemon=True)
    t.start()
    t.join(timeout=timeout)

    if result["approved"] is None:
        print(f"\n⏰ Timeout after {timeout}s - auto rejecting")
        return False
    return result["approved"]

# 用法
agent = PhoneAgent(
    ...,
    confirmation_callback=timeout_confirmation,
)
```

### 3.8 回调实战组合

实际部署通常组合多个回调策略：

```python
def smart_confirmation(message: str) -> bool:
    """按风险等级路由。"""
    risk = _assess_risk(message)    # 自实现: 关键词匹配等

    if risk == "low":               # 如"打开新页面"
        return True
    elif risk == "high":            # 如"支付 ¥99"
        return web_confirmation(message)      # 走 Web UI
    else:                           # 中等
        return timeout_confirmation(message, timeout=60)

def _assess_risk(msg: str) -> str:
    if any(k in msg for k in ["支付", "转账", "删除", "付款"]):
        return "high"
    if any(k in msg for k in ["确认", "确定"]):
        return "medium"
    return "low"
```

---

## 4. 综合实战：远程协助老人

场景：父母手机操作不熟，子女远程通过 Agent 协助。

```python
"""
assist_parents.py - 远程协助父母手机的 Agent 服务
"""
import logging
from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.model import ModelConfig

logging.basicConfig(filename='assist.log', level=logging.INFO)

def parent_confirmation(message: str) -> bool:
    """父母手机端弹原生 dialog 询问,结果回传。"""
    # 通过 adb shell am broadcast 触发手机上的 dialog APK
    # 或者通过 SMS 通知子女,子女远程回复
    import subprocess
    subprocess.run([
        "adb", "shell", "am", "broadcast",
        "-a", "com.parent.assist.CONFIRM",
        "--es", "message", message,
    ])
    # 等手机 APK 通过文件约定写入结果
    return _wait_for_result("/sdcard/assist_result.txt", timeout=120)

def parent_takeover(message: str) -> None:
    """告诉父母手动操作。"""
    # 通过 SMS 发到父母手机
    import requests
    requests.post("https://sms-api.example.com/send", json={
        "to": "+8613800138000",
        "text": f"需要您手动操作: {message}",
    })
    # 等父母在手机上完成
    input("父母完成后按回车...")

# 启动
agent = PhoneAgent(
    model_config=ModelConfig(
        base_url="https://open.bigmodel.cn/api/paas/v4",
        api_key="your-key",
        model_name="autoglm-phone",
    ),
    agent_config=AgentConfig(
        device_id="192.168.1.50:5555",   # 父母家手机(已开 WiFi 调试)
        max_steps=30,
        verbose=True,
    ),
    confirmation_callback=parent_confirmation,
    takeover_callback=parent_takeover,
)

# 接收子女通过 Web/IM 发来的任务
while True:
    task = receive_task_from_child()    # 自实现
    if task == "quit":
        break
    try:
        result = agent.run(task)
        notify_child(f"完成: {result}")
    except Exception as e:
        notify_child(f"失败: {e}")
    agent.reset()
```

---

## 5. 常见配置速查

```bash
# 远程 Android + 智谱 API + 交互模式
python main.py \
  --device-id 192.168.1.100:5555 \
  --base-url https://open.bigmodel.cn/api/paas/v4 \
  --model autoglm-phone \
  --apikey sk-xxx

# 远程 iOS + 本地 vLLM + 单任务
python main.py \
  --device-type ios \
  --wda-url http://192.168.1.50:8100 \
  --base-url http://localhost:8000/v1 \
  "Open Safari and search for news"

# 多设备并行(后台 + nohup)
for ip in 192.168.1.{10..15}; do
  nohup python main.py \
    --device-id $ip:5555 \
    --base-url http://model-server:8000/v1 \
    "每日打卡任务" \
    > "task_$ip.log" 2>&1 &
done
```

## 下一步

- 配置远程 → 本文 §1
- 探索任务 → 本文 §2
- 接入外部系统 → 本文 §3
- 部署模型服务 → [07-deployment.md](07-deployment.md)
- 开发新功能 → [EXTENDING.md](EXTENDING.md)

---
