# 03 — Telemetry 遥测系统

> Mem0 用 PostHog 收**匿名遥测**——知道哪些功能被用、benchmark 数字、错误率,但**不收 memory 内容**。
> 本篇讲清"它收什么、怎么关、隐私边界"。

---

## 1. 文件位置

| 文件 | 行数 | 用途 |
|------|------|------|
| `mem0/memory/telemetry.py` | 241 | 核心：`AnonymousTelemetry` 类、`capture_event` / `capture_client_event` 函数 |
| `mem0/memory/notices.py` | 1582 | 用户 notice 系统（首次使用、scale、slow-query 等） |
| `mem0/memory/setup.py` | 166 | `get_user_id()` / `get_or_create_user_id()` 生成 anon ID |

---

## 2. 关键常量

`mem0/memory/telemetry.py`：

```python
MEM0_TELEMETRY = os.environ.get("MEM0_TELEMETRY", "True")
PROJECT_API_KEY = "phc_hgJkUVJFYtmaJqrvf6CYN67TIQ8yhXAkWzUn9AMU4yX"
HOST = "https://us.i.posthog.com"
FEATURE_FLAGS_REQUEST_TIMEOUT_SECONDS = 0.5

_DEFAULT_SAMPLE_RATE = 0.1   # ⭐ hot-path 事件采样 10%

_LIFECYCLE_EVENTS = frozenset({
    "mem0.init", "mem0.reset",
    "mem0._create_procedural_memory", "mem0.notice_displayed",
    "$identify",
})
```

> PostHog 的 public API key 是**公开**的（写入到 client 是正常做法,真正的 auth 在 PostHog 后台）。

---

## 3. ⭐ 采样机制（节省带宽）

```python
def _sampling_before_send(msg):
    """PostHog before_send hook: 采样 hot-path,标记 lifecycle。"""
    if not isinstance(msg, dict):
        return None

    event_name = msg.get("event", "")
    is_lifecycle = event_name in _LIFECYCLE_EVENTS

    # >= 让 rate=0 全 drop,rate=1 全 keep
    if not is_lifecycle and random.random() >= MEM0_TELEMETRY_SAMPLE_RATE:
        return None

    # 标 sample_rate,让 PostHog 后台能 extrapolate 真实计数
    properties = msg.setdefault("properties", {})
    properties["sample_rate"] = 1.0 if is_lifecycle else MEM0_TELEMETRY_SAMPLE_RATE
    return msg
```

### 哪些事件永远 100% 上报

- `mem0.init` —— SDK 初始化
- `mem0.reset` —— 用户主动 reset
- `mem0._create_procedural_memory` —— procedural memory 创建
- `mem0.notice_displayed` —— notice 系统展示
- `$identify` —— 用户登录（PostHog person merging）

### 哪些事件采样（默认 10%）

- `mem0.add` / `mem0.search` / `mem0.get` / `mem0.get_all` / `mem0.update` / `mem0.delete` / `mem0.delete_all` / `mem0.history`

> 这些是 hot-path,每次调用都报会爆。10% 采样后 PostHog 后台用 `1/sample_rate` extrapolate 估算真实量。

---

## 4. `AnonymousTelemetry` 类

```python
class AnonymousTelemetry:
    def __init__(self, vector_store=None, before_send=None):
        if not MEM0_TELEMETRY:
            self.posthog = None
            self.user_id = None
            return

        self.posthog = Posthog(
            project_api_key=PROJECT_API_KEY,
            host=HOST,
            before_send=before_send or _sampling_before_send,
            feature_flags_request_timeout_seconds=FEATURE_FLAGS_REQUEST_TIMEOUT_SECONDS,
        )
        self.user_id = get_or_create_user_id(vector_store)

    def capture_event(self, event_name, properties=None, user_email=None, flags=None):
        if self.posthog is None:
            return

        distinct_id = self.user_id if user_email is None else user_email
        if distinct_id is None:
            return

        # 上报
        self.posthog.capture(
            distinct_id=distinct_id,
            event=event_name,
            properties=properties or {},
            groups={"Organization": ..., "Project": ...},
        )
```

---

## 5. ⭐ 隐私保护（secret redaction）

`mem0/memory/main.py` L96-L132 定义敏感字段：

```python
# 运行时字段（不清红,因为它们是连接对象,不是 secret）
_RUNTIME_FIELDS = frozenset({"http_auth", "auth", "connection_class", "ssl_context"})

# 已知 secret 字段（telemetry 时清空）
_SENSITIVE_FIELDS_EXACT = frozenset({
    "api_key", "secret_key", "private_key", "access_key", "password",
    "credentials", "credential", "secret", "token", "access_token",
    "refresh_token", "auth_token", "session_token", "client_secret",
    "auth_client_secret", "azure_client_secret", "service_account_json",
    "aws_session_token",
})

# 字段名后缀暗示 secret
_SENSITIVE_SUFFIXES = ("_password", "_secret", "_token", "_credential", "_credentials")


def _is_sensitive_field(field_name: str) -> bool:
    """Layered approach:
    1. Runtime fields (allowlist) — always preserved
    2. Exact deny list — known secret field names
    3. Suffix deny list — catches db_password, auth_secret, etc.
    """
    name = field_name.lower().strip()
    if name in _RUNTIME_FIELDS:
        return False
    if name in _SENSITIVE_FIELDS_EXACT:
        return True
    return any(name.endswith(suffix) for suffix in _SENSITIVE_SUFFIXES)
```

### `_safe_deepcopy_config`

`mem0/memory/main.py` L270-L298：

```python
def _safe_deepcopy_config(config):
    """安全 deepcopy config,敏感字段清空。"""
    try:
        return deepcopy(config)
    except Exception:
        # fallback: dict-based cloning with redaction
        ...
        for field_name in list(clone_dict.keys()):
            if field_name in _RUNTIME_FIELDS and hasattr(config, field_name):
                clone_dict[field_name] = getattr(config, field_name)
            elif _is_sensitive_field(field_name):
                clone_dict[field_name] = None   # ⭐ 清空
        ...
```

### telemetry 实际上报什么

| 上报 | 不上报 |
|------|------|
| event 名（"mem0.add"） | ❌ memory 内容 |
| `version`（"v1.1"） | ❌ user_id 真实值 |
| `sync_type`（"sync" / "async"） | ❌ query 内容 |
| `limit` / `top_k` / `threshold` | ❌ response |
| `keys`（filter key 名,如 "user_id"） | ❌ 任何 secret |
| `encoded_ids`（hash 后的 ID） | ❌ IP（PostHog 自己处理） |

> 看 `capture_event` 调用点（main.py L1195-L1200）：
> ```python
> keys, encoded_ids = process_telemetry_filters(filters)
> capture_event("mem0.add", self, {
>     "version": self.api_version,
>     "keys": keys,           # ["user_id", "agent_id"]
>     "encoded_ids": encoded_ids,  # hashed 值
>     "sync_type": "sync",
> })
> ```
> **filters 的 value 被 hash 后上报**,不是原值。

---

## 6. ⭐ `process_telemetry_filters`

```python
# mem0/memory/utils.py
def process_telemetry_filters(filters):
    """Hash filters 的 value,只保留 key 名 + hash 值。"""
    if not filters:
        return [], []
    keys = []
    encoded_ids = []
    for k, v in filters.items():
        if k in ENTITY_PARAMS and v:
            keys.append(k)
            # hash value (避免上报真实 user_id)
            encoded_ids.append(hashlib.sha256(str(v).encode()).hexdigest()[:16])
    return keys, encoded_ids
```

> Mem0 知道"用户的 user_id 是这串 hash",但**反推不出真实 user_id**。

---

## 7. anon ID 生成（`memory/setup.py`）

```python
def get_or_create_user_id(vector_store=None):
    """生成本地 anon ID,持久化到 ~/.mem0/config.json"""
    config_path = os.path.join(mem0_dir, "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        if "user_id" in config:
            return config["user_id"]

    # 没有就生成
    user_id = str(uuid.uuid4())
    config = {"user_id": user_id, "telemetry": {"enabled": True}}
    os.makedirs(mem0_dir, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    return user_id
```

> 每台机器一个 UUID。除非用户删 `~/.mem0/config.json`,否则永远是同一个。

---

## 8. `_maybe_alias_anon_to_email`（用户登录合并）

`mem0/client/main.py` L56-L79：

```python
def _maybe_alias_anon_to_email(user_email):
    """Fire $identify per prior anon ID so PostHog merges them into email.

    Idempotent via telemetry.aliased_pairs.
    Best-effort: never raises.
    """
    if client_telemetry.posthog is None:
        return
    if not user_email or "@" not in user_email:
        return
    try:
        anon_ids = read_anon_ids()
        seen = set()
        for anon_id in (anon_ids.get("oss"), anon_ids.get("cli")):
            if not anon_id or anon_id == user_email or anon_id in seen:
                continue
            seen.add(anon_id)
            if is_aliased(anon_id, user_email):
                continue
            if client_telemetry.capture_identify(anon_id, user_email):
                mark_aliased(anon_id, user_email)
    except Exception as e:
        logger.debug("Failed to alias anon telemetry to %r: %s", user_email, e)
```

> 用户先用 OSS（anon ID = UUID）,后注册平台（email）,PostHog 通过 `$identify` 事件合并两者到一个 person。

---

## 9. 怎么关闭 telemetry

### 方法 1：环境变量（推荐）

```bash
export MEM0_TELEMETRY=False
```

或在 Python：

```python
import os
os.environ["MEM0_TELEMETRY"] = "False"
# 必须在 from mem0 import ... 之前设
from mem0 import Memory
m = Memory()   # telemetry 关闭
```

### 方法 2：改 config.json

```bash
# ~/.mem0/config.json
{
  "user_id": "...",
  "telemetry": {"enabled": false}
}
```

### 方法 3：调采样率（不全关）

```bash
export MEM0_TELEMETRY_SAMPLE_RATE=0.0   # 全 drop
export MEM0_TELEMETRY_SAMPLE_RATE=1.0   # 全 keep
export MEM0_TELEMETRY_SAMPLE_RATE=0.01  # 仅 1% 上报
```

---

## 10. ⭐ Notices 系统（1582 行）

`mem0/memory/notices.py` 不是 telemetry,但是相关的——给用户**显示一次性提示**：

| Notice 类型 | 触发 | 例子 |
|----------|------|------|
| `display_first_run_notice` | 用户第一次用某 method | "Welcome! See docs.mem0.ai" |
| `display_scale_threshold_notice` | top_k 或 memory 数超阈值 | "You have 10K+ memories, consider Platform scale tier" |
| `display_performance_slow_query_notice` | search 慢 | "Query took 2s, BM25 might help" |
| `display_temporal_usage_notice` | query 含时间词 | "Try Platform temporal reasoning" |
| `display_decay_usage_notice` | delete_all 大量 | "Try Platform decay instead" |

每个 notice 用 `mem0.notice_displayed` telemetry 事件追踪（lifecycle,100% 上报）,确保**只显示一次**（用户看过就不再弹）。

> 这是"产品教育"机制——边用边学 Mem0 的高级特性。

---

## 11. 隐私 FAQ

### Q: Mem0 会偷看我的 memory 内容吗？
A: **不会**。Telemetry 只收 event 名 + 配置元数据（不含 memory value）。

### Q: user_id 会被看到吗？
A: **SHA-256 hash 前 16 字符**。Mem0 知道两个调用是不是同一个 user,但反推不出真实 ID。

### Q: PostHog 能看到我的 IP 吗？
A: 是,但 PostHog 默认不长期存（可配置）。Mem0 自己看不到 IP（PostHog 后台才看到）。

### Q: 关掉 telemetry 会损失什么？
A: 0 功能损失。telemetry 纯为 Mem0 团队改进产品。关掉只影响"统计数据精度"。

### Q: 自托管 server 也上报 telemetry 吗？
A: **是的**（除非设 `MEM0_TELEMETRY=False`）。Server 也 import mem0 SDK,所以同样规则。

---

## 12. 接下来

| 想看 | 去哪 |
|------|------|
| 双模式对比 | [`../00-overview/05-two-modes.md`](../00-overview/05-two-modes.md) |
| MemoryClient | [`01-client.md`](./01-client.md) |
| 配置系统 | [`../01-py-sdk-core/04-configs.md`](../01-py-sdk-core/04-configs.md) |

---

📌 **下一步** → [`../04-ts-sdk/`](../04-ts-sdk/) TypeScript SDK。
