# 06 · 配置层与应用映射

> 本文解析 `phone_agent/config/` 目录（9 个文件，~1300 行），覆盖：
> 应用映射（apps×3）、system prompt（prompts×3）、UI 国际化（i18n）、时间常量（timing）。

## 文件地图

```
phone_agent/config/
├── __init__.py          53 行   包导出 + get_system_prompt(lang) 路由
├── apps.py             226 行   Android 168 个 app 包名
├── apps_harmonyos.py   266 行   HarmonyOS 154 个 app + APP_ABILITIES
├── apps_ios.py         339 行   iOS 182 个 bundle ID + iTunes API
├── prompts.py           75 行   ⚠ 遗留废弃(与 prompts_zh.py 95% 重复,无人 import)
├── prompts_zh.py        77 行   中文 system prompt(15 动作 + 18 规则)
├── prompts_en.py        79 行   英文 system prompt(7 动作,精简版)
├── i18n.py              81 行   UI 消息国际化(22 key × 中/英)
└── timing.py           167 行   14 个时间常量 + 环境变量覆盖
```

## `__init__.py`：包导出与路由

### 导出清单

`config/__init__.py:37-53` 导出 5 类 API：

| 类别 | 导出符号 |
|------|---------|
| 应用映射 | `APP_PACKAGES`（Android）、`APP_PACKAGES_IOS`（iOS）|
| Prompt | `SYSTEM_PROMPT`、`SYSTEM_PROMPT_ZH`、`SYSTEM_PROMPT_EN`、`get_system_prompt(lang)` |
| i18n | `get_messages(lang)`、`get_message(key, lang)` |
| Timing | `TIMING_CONFIG`、`TimingConfig`、`ActionTimingConfig`、`DeviceTimingConfig`、`ConnectionTimingConfig`、`get_timing_config()`、`update_timing_config()` |

### `get_system_prompt(lang)` 路由

```python
def get_system_prompt(lang: str = "cn") -> str:
    if lang == "en":
        return SYSTEM_PROMPT_EN
    return SYSTEM_PROMPT_ZH    # 默认中文(向后兼容)
```

**`lang` 只接受 `"cn"` 或 `"en"`**（虽然签名是 `str`，但其他值会 fallback 到中文）。

### 导出缺口

- **`apps_harmonyos.py` 的 `APP_PACKAGES` 和 `APP_ABILITIES` 没有被 `__init__.py` 导出**——hdc 设备层直接从子模块 import。三平台地位不完全平等。
- `prompts.py`（遗留）也没有被导出，是死文件。

## 应用映射（apps×3）

### 数据结构对比

| 维度 | `apps.py`（Android） | `apps_harmonyos.py` | `apps_ios.py` |
|------|---------------------|---------------------|---------------|
| 主字典 | `APP_PACKAGES: dict[str,str]` | `APP_PACKAGES: dict[str,str]` | `APP_PACKAGES_IOS: dict[str,str]` |
| 额外字典 | 无 | `APP_ABILITIES: dict[str,str]` | 无 |
| 映射语义 | 显示名 → Android package | 显示名 → HarmonyOS bundle | 显示名 → iOS bundle ID |
| 条目数 | 168 | 154（+22 注释掉的） | 182 |
| 查询函数 | `get_package_name()`、`get_app_name()`、`list_supported_apps()` | 同左（相同签名） | `get_bundle_id()`、`get_app_name()`、`list_supported_apps()` + 3 个 iTunes API |

### 同一 app 在三平台的 ID 完全不同

| 显示名 | Android package | HarmonyOS bundle | iOS bundle ID |
|--------|----------------|-----------------|---------------|
| 微信 | `com.tencent.mm` | `com.tencent.wechat` | `com.tencent.xin` |
| 淘宝 | `com.taobao.taobao` | `com.taobao.taobao4hmos` | `com.taobao.taobao4iphone` |
| 抖音 | `com.ss.android.ugc.aweme` | `com.ss.hm.ugc.aweme` | `com.ss.iphone.ugc.Aweme` |
| 知乎 | `com.zhihu.android` | `com.zhihu.hmos` | `com.zhihu.ios` |
| 哔哩哔哩 | `com.bilibili.app`（键: `"bilibili"`） | `com.bilibili.hmos`（键: `"哔哩哔哩"`） | `com.bilibili.client`（键: `"哔哩哔哩"`） |

**关键洞察**：各家厂商为不同 OS 发布独立包，三平台 ID 完全不同。

### HarmonyOS 独有：APP_ABILITIES

HarmonyOS 启动 app 需要 bundle name **+** ability name：

```python
# apps_harmonyos.py:10-57
APP_ABILITIES: dict[str, str] = {
    "cn.wps.mobileoffice.hap": "DocumentAbility",
    "com.tencent.videohm": "AppAbility",
    # ...
}
```

`hdc/device.py:281-282` 的消费逻辑：

```python
ability = APP_ABILITIES.get(bundle_name, "EntryAbility")   # 默认 EntryAbility
```

未在 `APP_ABILITIES` 中找到时默认 `"EntryAbility"`。这是 HarmonyOS 平台独有的二级查找。

### 命名容错（apps.py 特有）

Android `apps.py` 有大量大小写/空格/连字符变体指向同一包名：

```python
"Chrome": "com.android.chrome",
"chrome": "com.android.chrome",
"Google Chrome": "com.android.chrome",
"google chrome": "com.android.chrome",
```

这是为了**容错模型输出的不同写法**——模型可能输出 `"Chrome"` 或 `"chrome"` 或 `"Google Chrome"`，都能命中。

### 三平台 app 交集

| 交集 | app 数 |
|------|--------|
| Android ∩ HarmonyOS | 34 |
| Android ∩ iOS | 33 |
| HarmonyOS ∩ iOS | 48 |
| **三平台共有** | **20** |

三平台共有的 20 个 app 包括：QQ、QQ音乐、京东、今日头条、喜马拉雅、大众点评、小红书、微信、微博、快手等。

### iOS 独有：iTunes API

`apps_ios.py:243-339` 提供了 3 个其他平台没有的函数：

| 函数 | 行号 | 作用 |
|------|------|------|
| `check_app_installed(app_name, wda_url)` | 243 | 通过 iTunes Lookup API 检查 app 是否存在 |
| `get_app_info_from_itunes(bundle_id)` | 282 | 用 bundle ID 查 iTunes 获取 app 信息 |
| `get_app_info_by_id(app_store_id)` | 312 | 用 App Store 数字 ID 查 app 信息 |

这些函数调用 `https://itunes.apple.com/lookup`，依赖 `requests` 库（延迟 import）。

### 添加新 app 的步骤

以添加 "抖音极速版" 为例：

| 步骤 | 文件 | 改什么 | 必需？ |
|------|------|--------|--------|
| 1 | `apps.py` | 加 `"抖音极速版": "com.ss.android.aweme.lite"` | ✅ Android 支持 |
| 2 | `apps_harmonyos.py` | 加 `"抖音极速版": "com.ss.hm.aweme.lite"` | ✅ HarmonyOS |
| 2b | `apps_harmonyos.py` → `APP_ABILITIES` | 若 ability ≠ `EntryAbility`，加映射 | ⚠️ 条件必需 |
| 3 | `apps_ios.py` | 加 `"抖音极速版": "com.ss.iphone.ugc.aweme.lite"` | ✅ iOS 支持 |
| 4 | `__init__.py` | **不需要改** | — |
| 5 | prompts / i18n / timing | **不需要改** | — |

**结论**：添加新 app 需要改 **1-3 个文件**（看支持几个平台），其他配置无需动。较好的关注点分离。

## System Prompt（prompts×3）

### 三份文件的关系

| 文件 | 状态 | 被谁 import |
|------|------|------------|
| `prompts.py` | **遗留废弃** | **无人 import**（grep 确认零引用） |
| `prompts_zh.py` | 当前中文 | `__init__.py:7`，通过 `get_system_prompt("cn")` |
| `prompts_en.py` | 当前英文 | `__init__.py:6`，通过 `get_system_prompt("en")` |

`prompts.py` 与 `prompts_zh.py` 内容 95% 相同，唯一区别：
- `prompts.py:6` — 日期格式 `"%Y年%m月%d日"`（无星期）
- `prompts_zh.py:8` — 日期格式 `"%Y年%m月%d日 星期X"`（多了星期）

`prompts.py` 是旧版，已被 `prompts_zh.py` 替代但未删除。

### `prompts_zh.py` 结构（中文，~1200 token）

| 段落 | 行号 | 主题 |
|------|------|------|
| 日期注入 | 5-8 | 动态注入今天日期 + 星期几 |
| 角色定义 | 14 | "你是一个智能体分析专家" |
| 输出格式 | 15-21 | `<think>{think}</think><answer>{action}</answer>` |
| 动作指令清单 | 23-55 | **15 种** `do(action=...)` + `finish(...)` |
| 行为规则 | 57-75 | **18 条**硬性规则 |

**15 种动作**：Launch、Tap、Tap+message（敏感）、Type、Type_Name、Interact、Swipe、Note、Call_API、Long Press、Double Tap、Take_over、Back、Home、Wait + finish。

**18 条规则的主题**（节选）：
- 导航规则（规则 1-2）：先检查 app、走错页 Back
- 等待规则（规则 3）：最多连续 Wait 3 次
- 搜索规则（规则 5、11、17）：滑动查找、多次搜索、返回上级重试
- 购物车规则（规则 8）：全选/取消全选逻辑
- 外卖规则（规则 9-10）：清空购物车、同店购买
- 游戏规则（规则 16）：自动战斗开关
- 日期规则（规则 12）：反向滑动查找
- 死循环防护（规则 13）：不在同一项目栏多次查找
- 完成校验（规则 18）：检查错选/漏选/多选

这些规则是**领域知识硬编码进 prompt**，对中文 app 生态做了大量调优。

### `prompts_en.py` 结构（英文，~650 token）

| 段落 | 行号 | 主题 |
|------|------|------|
| 日期注入 | 5-6 | `"%Y-%m-%d, %A"` |
| 角色定义 | 12-13 | "professional Android operation agent assistant" |
| 输出格式 | 15-27 | 同样的 `<think>/<answer>` 格式 + 多行示例 |
| 动作指令 | 29-71 | **仅 7 种**：Tap、Type、Swipe、Long Press、Launch、Back、Finish |
| 记忆规则 | 74-78 | **3 条** REMEMBER 规则 |

### 中英文 prompt 的关键差异

| 维度 | 中文版 | 英文版 |
|------|--------|--------|
| 动作种类 | **15 种** + finish | **7 种** + finish |
| 行为规则 | **18 条**详细规则 | **3 条**通用规则 |
| 特定场景指导 | 有（购物车、外卖、游戏、小红书筛选等） | 无 |
| Token 估算 | ~1200 token | ~650 token |
| 适用场景 | 中文 app 生态 | 英文 app（更通用） |

**英文版是精简版**，缺少中文版中大量领域特定策略。如果你的目标 app 是英文环境且场景简单，英文 prompt 更省 token；如果复杂任务，中文 prompt 的规则会显著提升成功率。

### 协议演进：prompt 与实现的脱节

`prompts_zh.py` 要求输出：

```
<think>{think}</think>
<answer>{action}</answer>
```

但 `model/client.py:_parse_response` **优先匹配裸 `do(action=`/`finish(message=`**，XML 标签是 fallback（详见 [05-model-client.md](05-model-client.md#_parse_response-解析规则)）。

这说明**模型实际输出已演化为直接函数调用**，prompt 描述滞后。实践影响：模型偶尔输出 XML 格式时仍能正确解析（fallback 兜底），但 prompt 与代码不一致是文档债。

**没有 HarmonyOS 专属 prompt**——HarmonyOS 设备复用 Android 的中文 prompt（其中提到"Android 的返回按钮"），对 HarmonyOS 不完全准确但可用。

## `i18n.py`：UI 消息国际化

### 工作机制

```python
def get_messages(lang="cn") -> dict:
    if lang == "en":
        return MESSAGES_EN
    return MESSAGES_ZH

def get_message(key, lang="cn") -> str:
    return get_messages(lang).get(key, key)   # fallback: 返回 key 本身
```

### 支持的 22 个 key

| 类别 | key 列表 |
|------|---------|
| 流程状态 | `thinking`、`action`、`task_completed`、`done`、`starting_task`、`final_result`、`task_result` |
| 交互确认 | `confirmation_required`、`continue_prompt`、`manual_operation_required`、`manual_operation_hint`、`press_enter_when_done` |
| 连接 | `connection_failed`、`connection_successful` |
| UI 标签 | `step`、`task`、`result` |
| 性能指标 | `performance_metrics`、`time_to_first_token`、`time_to_thinking_end`、`total_inference_time` |

### 用途定位

**给 UI 终端显示用，不是给模型用。**

消费者证据：
- `agent.py:173` — `msgs = get_messages(self.agent_config.lang)` 用于终端输出标签（`💭 thinking:`、`🎯 action:`）
- `model/client.py:152-163` — `get_message('performance_metrics', lang)` 用于打印推理性能指标

这些是人类可读的终端消息，与 system prompt（给模型）完全分离。如果你做 GUI/Web 前端，会用自己的 i18n 方案，这套不直接复用。

## `timing.py`：时间常量配置

### 结构：4 个 dataclass

```
TimingConfig (组合根, timing.py:100-111)
├── action: ActionTimingConfig       (4 个常量)
├── device: DeviceTimingConfig       (8 个常量)
└── connection: ConnectionTimingConfig  (2 个常量)
```

### 全部 14 个时间常量

| 分类 | 常量 | 默认值(秒) | 环境变量 | 用途 |
|------|------|-----------|---------|------|
| **Action** | `keyboard_switch_delay` | 1.0 | `PHONE_AGENT_KEYBOARD_SWITCH_DELAY` | 切换到 ADB 键盘后等 |
| | `text_clear_delay` | 1.0 | `PHONE_AGENT_TEXT_CLEAR_DELAY` | 清空文本后等 |
| | `text_input_delay` | 1.0 | `PHONE_AGENT_TEXT_INPUT_DELAY` | 输入文本后等 |
| | `keyboard_restore_delay` | 1.0 | `PHONE_AGENT_KEYBOARD_RESTORE_DELAY` | 恢复键盘后等 |
| **Device** | `default_tap_delay` | 1.0 | `PHONE_AGENT_TAP_DELAY` | 点击后等 |
| | `default_double_tap_delay` | 1.0 | `PHONE_AGENT_DOUBLE_TAP_DELAY` | 双击后等 |
| | `double_tap_interval` | 0.1 | `PHONE_AGENT_DOUBLE_TAP_INTERVAL` | 双击两次之间隔 |
| | `default_long_press_delay` | 1.0 | `PHONE_AGENT_LONG_PRESS_DELAY` | 长按后等 |
| | `default_swipe_delay` | 1.0 | `PHONE_AGENT_SWIPE_DELAY` | 滑动后等 |
| | `default_back_delay` | 1.0 | `PHONE_AGENT_BACK_DELAY` | 返回键后等 |
| | `default_home_delay` | 1.0 | `PHONE_AGENT_HOME_DELAY` | Home 键后等 |
| | `default_launch_delay` | 1.0 | `PHONE_AGENT_LAUNCH_DELAY` | 启动 app 后等 |
| **Connection** | `adb_restart_delay` | 2.0 | `PHONE_AGENT_ADB_RESTART_DELAY` | TCP/IP 模式启用后等 |
| | `server_restart_delay` | 1.0 | `PHONE_AGENT_SERVER_RESTART_DELAY` | ADB server 重启间隔 |

### 双层配置机制

每个 dataclass 都有 `__post_init__`，支持**环境变量覆盖**：

```python
# timing.py:21-34
def __post_init__(self):
    self.keyboard_switch_delay = float(
        os.getenv("PHONE_AGENT_KEYBOARD_SWITCH_DELAY", self.keyboard_switch_delay)
    )
```

**优先级**：环境变量 > 代码默认值。

运行时还可用 `update_timing_config()` 函数热更新全局实例（`timing.py:129-156`）。

### 为什么需要单独配置时间

1. **设备性能差异**：低端手机渲染慢，需更长等待；高端可缩短提速
2. **网络条件**：ADB 无线连接 vs USB 连接延迟不同
3. **免改代码调参**：通过环境变量即可调，无需改源码（运维友好）
4. **实际消费者**：
   - `actions/handler.py:159-171`（文本输入 4 个 delay）
   - `adb/device.py:54-223`（7 个 device delay）
   - `adb/connection.py:249-318`（2 个 connection delay）
   - hdc 层对称消费

### 调优建议

```bash
# 低端设备: 拉长延迟
export PHONE_AGENT_TAP_DELAY=2.0
export PHONE_AGENT_LAUNCH_DELAY=3.0

# 高端设备 / 模拟器: 缩短延迟提速
export PHONE_AGENT_TAP_DELAY=0.3
export PHONE_AGENT_TEXT_INPUT_DELAY=0.5

# ADB 无线不稳定: 拉长连接相关
export PHONE_AGENT_ADB_RESTART_DELAY=5.0
```

**注意**：iOS 版（`handler_ios.py`）的 `time.sleep(0.5)` **硬编码，不受 TIMING_CONFIG 控制**。调时间常量对 iOS 无效，需要改源码。

## 设计观察

### 重复问题

| 问题 | 详情 |
|------|------|
| `prompts.py` 完全冗余 | 与 `prompts_zh.py` 95% 重复，无人 import。应删除 |
| `apps_harmonyos.py` 22 条注释 | `# 未在 hdc 列表中找到`，是从 apps.py 复制后逐个验证的遗留 |
| 三套 apps 查询函数签名重复 | 都定义了几乎相同的 `get_*` 函数，没提取到基类 |
| iOS 函数命名不一致 | iOS 用 `get_bundle_id()` 而非 `get_package_name()`，但 `xctest/device.py:7` 做了别名 `APP_PACKAGES_IOS as APP_PACKAGES` 统一消费 |

### 国际化机制不统一

存在**两套独立 i18n 机制**，互不相通：

| 机制 | 覆盖范围 | 路由 |
|------|---------|------|
| `get_system_prompt(lang)` | 模型行为指令 | `__init__.py` if/else |
| `get_message(key, lang)` | UI 终端消息 | `i18n.py` if/else |

两套都只支持中/英，且**中文内容显著多于英文**（中文 15 动作+18 规则 vs 英文 7 动作+3 规则）。

### 添加新语言（如日语）

需要改：
1. 新建 `prompts_ja.py`（参考 prompts_zh.py 翻译）
2. 新建 `i18n.py` 里加 `MESSAGES_JA` 字典
3. `__init__.py:get_system_prompt` 加 `elif lang == "ja"` 分支
4. `i18n.py:get_messages` 加 `elif lang == "ja"` 分支
5. `main.py:--lang` choices 加 `"ja"`

5 个文件改动，相对繁琐。理想方案是 prompt 和 i18n 都用文件目录约定（如 `prompts/<lang>.py`、`locales/<lang>.json`），自动发现。

## 下一步

- 想改 prompt 增强某类任务 → 直接改 `prompts_zh.py` 或 `prompts_en.py`
- 想加新 app → 见本文「添加新 app 的步骤」
- 想调时间常量 → 用环境变量，无需改代码
- 想加新动作类型 → [04-action-handler.md](04-action-handler.md) + 改 prompt 描述
- 想做完整扩展 → [EXTENDING.md](EXTENDING.md)

---
