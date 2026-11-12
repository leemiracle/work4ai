# 01 · main.py —— 86 行撑起的守护进程全流程

## 1. 角色定位

`nvsm_exporters/main.py`（86 行）是全仓**唯一可执行入口**：pyinstaller 以它为起点打出 `/usr/sbin/nvsm_prometheus_exporters`，systemd 拉起的也是它。它集三职于一身——配置解析（读 `/etc/nvsm-apis/nvsm-prometheus-exporters.config`）、模块编排、Prometheus HTTP 宿主（8000 端口）。图谱中它是全仓最高枢纽（fanOut 24，星型中心）。第一印象：2018 年 **Python 2 顶层脚本**，通篇没有一个 `def`，模块级代码从 L30 写到 L86。

## 2. 内部结构

**导入区（L11-28）**：`main.py:11` 的 `import importlib` 是**死导入**——全文件再未引用，真正干动态加载的是 L70 内建 `__import__`。`main.py:17-24` 静态 import 全部 8 个 exporter；L28 全局关闭 InsecureRequestWarning（所有 exporter 都 `verify=False`）。

**默认值区（L30-38）**：port 8000（L31）、nvsm localhost:273（L33-34）、interval 20（L35）。port/exporters/interval **必须**由配置提供（L52-57 缺节点即退出），nvsm host/port 才是可选覆盖（L60）。

**配置加载区（L41-62）**：`main.py:41-42` 查文件存在性；`main.py:45-49` `yaml.load` 包在裸 `except` 里——语法/编码错误一律退化为一句 `"Error in config file"`，原始异常全丢。L53-55/L61-62 读出五项配置。

**服务与主循环（L65-86）**：`main.py:65` 起 HTTP server；`main.py:68-72` 按清单动态加载——L69 `mod = e.replace(".py", "")` 容忍带后缀写法，L70 `__import__`，L71 调 `init()` 预建静态 Gauge。`main.py:75-86` 主循环：L77 `getattr(module, 'ExportMetric')` 鸭子类型取函数，L79 以 `(nvsm_host, nvsm_port)` 驱动采集；KeyboardInterrupt 特判退出（L80-81），其余异常 `main.py:83-84` 用 Py2 print 语句打出后 continue；L86 `time.sleep(interval)`。

## 3. 外部连接

- **向下双轨**：L17-24 静态 import 是 pyinstaller 依赖分析锚点；L68-72 动态 `__import__` 决定运行时谁被 init。
- **向配置**：L38 的 YAML，经 `nvsm_exporters/Makefile.am:24-26` 装机。
- **向 Prometheus**：L65 起的 server 让各 exporter 的指标自动经 `/metrics` 暴露——main.py 自己不碰指标。
- **被消费**：`nvsm_exporters/Makefile.am:29` pyinstaller 是唯一下游；`nvsm-prometheus-exporters.service:7` 指向产物。

## 4. 数据流

```
YAML → L46 yaml.load → L53-55/L61-62 五项配置
L65 start_http_server → /metrics 就绪
L68-72 __import__ → init() → 静态 Gauge 入 REGISTRY
L75-86 while True: 逐模块串行 L79 ExportMetric()
  → exporter GET https://nvsm:273/... → Gauge.set()
  失败 L83-84 print+continue；轮末 L86 sleep(20)
```

注意**先采集后睡眠、串行执行**：GPU 一轮采集 45 秒+（其内部 sleep），20 秒名义间隔名存实亡，实际周期由最慢模块决定。

## 5. 设计决策

**勘误（importlib）**：`main.py:11` 的 importlib 从未使用，动态加载全在 `main.py:70` 的 `__import__`——盯 importlib 找加载逻辑是首陷阱。

**双轨 import（勘误："配置驱动"只是半边故事）**：pyinstaller 静态分析不认识字符串模块名，`main.py:17-24` 才是让模块进单文件的保证。新增 exporter 必须三处同改：子 Makefile.am SOURCES、静态 import、config 清单，只改配置是静默缺失。

**print 活化石**：`main.py:83-84` 是 Py2 语法，Py3 下直接 SyntaxError，不可单点修——整仓锁死 Py2。

**最小故障隔离**：L78-85 try/except 让单模块异常不拖垮进程；代价是无堆栈、无模块名区分。**无函数封装**：变量即全局，简洁但不可单测（本仓零测试）。

## 6. 新人提示

- **改参数**只动 YAML 且必须重启服务——配置只在 L46 读一次。
- **加 exporter**：复制 pcie_exporter.py（最短模板）+ 三处登记（见第 5 节）。
- **排障**：日志见 L84 "Failed" 定位失败模块；秒退是 L42/L49/L57 三个 `sys.exit` 之一。
- **别顺手现代化**：print/yaml.load/裸 except 锁死 Py2，迁移是 9 文件+deb 依赖联动工程。
- **协议精确**：新模块必须精确实现 `init()` + `ExportMetric(ip, port)`，多一个参数 L79 立即 TypeError。

---
*锚自 nvsm_exporters/main.py 逐行核实（a892c4cc）。*
