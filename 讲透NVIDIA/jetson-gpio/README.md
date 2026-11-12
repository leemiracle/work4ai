# 讲透 NVIDIA/jetson-gpio

Jetson 系列 GPIO 控制 Python 库（RPi.GPIO API 语义 + Linux cdev 后端 + 11 模型引脚数据库 + Debian/PyPI 双分发链）。

## 全链状态表

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki 全量 | ✅ TRUE_100 | `deepwiki/`（INDEX.md + 全页 + _coverage-check） |
| understand 图谱 | ✅ 141n/220e/6 层/6 步 tour，0 issues，fingerprints 45 文件 @ d46fefb5 | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 7 节 / 86 行号锚（任务书 7 节 25 锚超额） | `onboarding/ONBOARDING.md` |
| explain | ✅ 2 篇（gpio_cdev 绑定 / gpio_event 事件引擎） | `explain/01-…md` `explain/02-…md` |
| NOTES-DIGEST | ✅ 24 条 | 仓内 `.understand-anything/NOTES-DIGEST.md` |

## 源码级勘误清单（6 条，全部行号实证 @ d46fefb5）

1. **MANIFEST.in:1 是死行**：写的是 `include LICENCE.txt`（英式拼写），实际文件名 `LICENSE.txt`——该行自诞生起从未生效；sdist 里 LICENSE 依赖 setuptools 新版的 `license_files` 自动发现，而非此行。
2. **run_sample.sh 帮助文本与文件名脱节**：`samples/run_sample.sh:31-32` 用法清单写 `simple_output.py`，实际文件是 `samples/simple_out.py`；且清单漏列 issue40.py / issue40-trigger.py / jetson_model.py / jetson_gpio_super_test_script.py / test_all_pins_input.py / test_gpio_pinmux_lookup.py 六个现存示例。
3. **两个 postinst 逐字节相同**：`debian/python3-jetson-gpio.postinst` 与 `debian/python-jetson-gpio.postinst` diff 为空（各 23 行，有效主体仅 `groupadd -f -r gpio` 等 udev 组初始化）；而 `debian/control:21` 只构建 python3 包——python2 postinst 是 Py2 时代遗留复制体，现代构建里不会被任何包引用。
4. **图谱 scanner 对 `__init__` 误解析 4 处**：①②③ 三条伪 imports 边 `gpio.py / gpio_event.py / gpio_pinmux_lookup.py → Jetson/GPIO/__init__.py`（三文件源码从不导入包入口：`gpio.py:22-25` 导入 constants/gpio_event/gpio_pin_data/gpio_cdev，`gpio_event.py:47` 导入 gpio_cdev，`gpio_pinmux_lookup.py:29` 导入 gpio_pin_data——scanner 对 `from Jetson.GPIO import X` 句式重复建边）；④ `RPi/GPIO/__init__.py → Jetson/GPIO/__init__.py` 星号转发边在 basename 视角呈 `__init__.py → __init__.py` 自环形态，语义终点实为 gpio.py。读图谱依赖时以源码 import 语句为准。
5. **Python 2.7 支持声明失效**：`setup.py:26` classifiers 仍列 `Programming Language :: Python :: 2.7`，但 `gpio_pin_data.py:610`、`gpio_pinmux_lookup.py:58` 已用 f-string（Py3.6+ 语法）——该分类器与现状矛盾；`gpio_event.py:34-38` 的 `import thread` 双兼容残留同理是未清理的化石而非能力。
6. **CodeQL workflow 依赖退役 action**：`.github/workflows/codeql-analysis.yml:38` `actions/checkout@v2` + `:42` `github/codeql-action/init@v1`，语言矩阵硬编码 `['python']`（`:31`）——v1 系列 action 已被 GitHub 停用，此扫描线实际处于失效状态。

## 快速上手

权限链是第一关：`gpio.py:33-34` 导入期即检查 `/dev/gpiochip0` 写权限，不过直接 RuntimeError。装 `lib/python/Jetson/GPIO/99-gpio.rules`（`debian/jetson-gpio-common.udev` 同内容）+ 用户加 gpio 组。之后跑 `samples/simple_out.py`，`jetson_model.py` 验证板型探测（`gpio_pin_data.py:600` 三通道：JETSON_TESTING_MODEL_NAME → /proc/device-tree/compatible → JETSON_MODEL_NAME）。

## 深讲入口

- 图谱导览：`.understand-anything/onboard-input.json`（6 层/6 步 tour）
- 事件三姿势对照（轮询/阻塞/回调）：`explain/02` 第 6 节
- 新板适配（PADCTL 地址再生成）：`onboarding/ONBOARDING.md` 第 6 节 + `dev/update_pinmux_registers.py:32-48`
