# NVSM 新人入门（ONBOARDING）

> 基于知识图谱（36 节点/89 边/7 层，commit a892c4cc）与全量源码核实撰写。仓库 NVIDIA/NVSM 下实际只有一个子项目 `NVSM-Prometheus/`，全部 19 个源文件共 1353 行（wc 实测）。

## 1. 项目定位

NVSM-Prometheus 是 NVIDIA DGX 服务器上的 **Prometheus 指标导出器**：它周期性轮询本机 NVSM-APIs（DGX 的 Redfish 风格带外管理服务，默认 `localhost:273`）的健康数据——GPU、内存 ECC、NVMe 盘、电源、风扇温度、PCIe 错误、告警——并把结果写入 Prometheus Gauge，经 `start_http_server` 在 8000 端口暴露给 Prometheus 抓取。

技术栈是 2018 年的 **Python 2** 顶层脚本（无类、几乎无函数封装）+ prometheus_client + requests + PyYAML，构建链是 Autotools（autoconf/automake）+ **pyinstaller --onefile** 打成单文件自解压"二进制"，交付物是 **Debian 包**（内含 systemd unit 与运行时配置）。规模数字：9 个 Python 源（main + 8 个 exporter）、7 层架构、8 个功能 exporter 模块、默认启用 7 个（processor 默认不启用）。

## 2. 架构总览（按 layers 逐层）

- **L01 构建引导（Autotools）**：`autogen.sh` 预建 config/m4 目录并跑 autoreconf 生成 configure；`configure.ac` 探测工具链并声明三个 AC_CONFIG_FILES 输出。
- **L02 构建与打包规则**：顶层 `Makefile.am` 提供 `make debian` 发布链；子目录 `nvsm_exporters/Makefile.am` 用 pyinstaller 打单文件并安装 unit/配置；`packaging/DEBIAN/control.in` 是包元数据模板。
- **L03 Debian 维护脚本**：`postinst`/`prerm`/`postrm` 把包生命周期接驳到 systemd。
- **L04 主入口与编排**：`nvsm_exporters/main.py`（86 行，Python 2 顶层脚本）读配置、起 HTTP server、动态加载 exporter、驱动轮询主循环。
- **L05 Exporter 模块群**：8 个 `*_exporter.py`，每个实现 `init()`/`ExportMetric()` 两函数协议；数据源分两类——私有 `/nvsm/v1/` 端点（alerts/gpu/pcie）与标准 Redfish `/redfish/v1/` 端点（memory/power/processor/storage/thermal）。
- **L06 运行时配置与服务**：`nvsm-prometheus-exporters.config`（YAML，端口 8000/间隔 20s/启用清单/NVSM 地址）；`nvsm-prometheus-exporters.service`（systemd 单元）。
- **L07 项目文档**：`README.md` 给出克隆地址、Ubuntu 16.04+ 前置依赖与三步打包流程。

## 3. 核心链路（tour 12 步的主数据流叙事）

**构建期**（step-01~05）：`autogen.sh:L12-13` 跑 autoreconf 生成 configure → `./configure --sysconfdir=/etc` 按 `configure.ac:L34-38` 生成根 Makefile、子目录 Makefile 与 `packaging/DEBIAN/control` → `make debian` 走 `Makefile.am:L22-26` 的发布链（先由 `Makefile.am:L9-13` 校验 sysconfdir=/etc，再 DESTDIR 组装 tmp_pkg_tree、拷入 DEBIAN、fakeroot dpkg-deb 打包）→ 子目录 `nvsm_exporters/Makefile.am:L28-30` 用 `pyinstaller --onefile main.py` 打出单文件可执行并改名 `nvsm_prometheus_exporters` 装到 /usr/sbin。

**部署期**（step-04~05、11）：deb 包安装时 `postinst:L7-13` daemon-reload 并 enable+restart 服务；systemd 按 `nvsm-prometheus-exporters.service:L4` 在 `nvsm-apis.service` 之后拉起 `/usr/sbin/nvsm_prometheus_exporters`，失败自动重启（`nvsm-prometheus-exporters.service:L3,L8-9`：300 秒窗口最多 10 次）。

**运行期**（step-06~10、12）：`main.py:L41-49` 检查并解析 `/etc/nvsm-apis/nvsm-prometheus-exporters.config` → `main.py:L52-62` 读出端口/间隔/启用清单/NVSM 地址 → `main.py:L65` `start_http_server(port)` → `main.py:L68-72` 对清单逐项 `__import__` 并调 `init()` 预建静态 Gauge → `main.py:L75-86` 主循环每 20 秒依次调各模块 `ExportMetric(nvsm_host, nvsm_port)`：每个 exporter 读取 `/etc/nvsm-apis/nvsm-apis-perpetual.jwt` 作 Bearer token（如 `pcie_exporter.py:L65-66`），`requests.get` 各自端点（`verify=False`），把 JSON 字段写进 Gauge；动态指标按发现的对象逐个建（GPU/盘/风扇/PSU）。指标随 8000 端口的 /metrics 暴露给 Prometheus 抓取——这就是从源码到指标的全链。

## 4. 关键文件深读

**`nvsm_exporters/main.py`（86 行，全仓枢纽）**：整个守护进程没有类、入口无函数，模块级代码从上到下即流程。L69 `mod = e.replace(".py","")` 说明配置清单带不带 .py 后缀都能加载——新增 exporter 只需写模块+改配置，不动 main（配置驱动扩展点）。L75-86 主循环对每个 `ExportMetric` 调用套 try/except，单模块抛异常只 `print e`（Python 2 语句，L83）后 continue，不会拖死其他 exporter——这是最朴素但有效的故障隔离。注意各 exporter 是**串行**执行的，一个模块慢全体慢（见第 7 节 gpu sleep）。

**`nvsm_exporters/gpu_exporter.py`（163 行，最重的采集逻辑）**：L82 先枚举 `/nvsm/v1/Systems/1/GPUs` 拿 `Members@odata.count` 设 GPU 总数；L91 从集合级 `Health.@odata.id` 取健康汇总端点；L113-117 再逐 GPU 请求 `Members[i].@odata.id` 详情。每级之间 `time.sleep(5)`（L93/L114）是给 NVSM-APIs 留的节流缓冲。L123-128 按 GPU UUID 动态创建 `pcie_link_width_<UUID>`，`PCIeLinkWidth[:-1]` 剥掉单位尾缀字符；L155-163 的 Retired Pages 是三项求和（单比特+双比特+待退休）。L141-152 的 per-GPU health 存在拼写 bug（第 7 节勘误 2）。

**`nvsm_exporters/storage_exporter.py`（189 行，全组最深轮询链）**：L100 枚举 Storage 集合 → L106-115 逐存储子系统（json 解析失败则 continue）→ L118-126 逐 NVMe 驱动。L128-131 用 `@odata.id` 是否含 `nvme0n1/nvme1n1` 区分 OS 盘与数据盘，并取 `[-7:]` 后缀做指标名；每盘建 capacity/percent_used/media_errors 三个动态 Gauge（L132-155）。L163-172 以模块级 `metric_map["status"]`（L24 初始 -1）做最大值 rollup 出全盘健康；L186-189 计算平均寿命/已用百分比。

**`nvsm_exporters/Makefile.am`（30 行，交付物形态定义）**：L11-19 把 9 个 .py 声明为程序 SOURCES（只为让 automake 追踪变更），L28-30 自定义规则跑 pyinstaller 并 `mv dist/main nvsm_prometheus_exporters`——所谓"二进制"其实是自解压 Python。L21-26 把 unit 装 `$(libdir)/systemd/system`、配置装 `$(sysconfdir)/nvsm-apis`。

**`nvsm_exporters/alerts_exporter.py`（97 行，JWT 认证样本）**：L64-65 读 perpetual JWT，L68 与 L82 分别请求 Chassis 与 Systems 两个 Alerts 私有端点；L74-79 判定条件是 `state != "cleared"` 且 `severity == "1"`（字符串比较），两端口活跃告警累加进同一个 `alerts_count` Gauge（L23）。

## 5. 模块间关系

依赖结构是**星型**：`main.py` 独居中心（fanOut 24，全仓最高），L17-24 静态 import 了全部 8 个 exporter 模块——注意这与 L68-72 的运行时 `__import__` 动态加载**双轨并存**：静态 import 保证 pyinstaller 能把所有模块打进单文件，动态加载决定运行时谁被初始化。外围契约就一条：**exporter 协议 = `init()`（无参，预建静态 Gauge）+ `ExportMetric(ip, port)`（每轮采集）**，8 个模块全部遵守，`main.py:L77` 用 `getattr(module, 'ExportMetric')` 鸭子类型取用。每个模块各自维护模块级 `metric_map` 字典做 Gauge 注册表（如 `pcie_exporter.py:L19`），动态指标名即字典键。

其余关系都走**文件与端口**而非代码调用：`nvsm-prometheus-exporters.config` → `main.py:L52-62`（YAML 三键：metric_exporter/nvsm）；全部 exporter → `/etc/nvsm-apis/nvsm-apis-perpetual.jwt`（Bearer 凭据，由 nvsm-apis 包提供）；service unit → pyinstaller 产物路径；`control.in:L9` 的 Depends 声明对 `nvsm-apis` 包的硬依赖（没有它就没有 273 端口服务和 JWT）。构建层 5 个文件（autogen/configure.ac/两个 Makefile.am/control.in）构成链式模板替换关系：configure 替换 `@PACKAGE_VERSION@` 后 Makefile 才能组装 DEBIAN 目录。

## 6. 构建与运行

按 `README.md:L29-31` 三步走（前置依赖见 L21-22：autoconf、python-pip、pip 装 pyinstaller）：

```bash
./autogen.sh                          # 生成 configure
./configure --sysconfdir=/etc --localstatedir=/var
make debian                           # 校验+组装+打包出 .deb
```

`make debian` 的完整语义在顶层 `Makefile.am:L22-26`：依赖 `check-sysconfdir`（L9-13 强制 sysconfdir=/etc，否则报错终止）与 `install_tree`（L18-19 DESTDIR 安装到 tmp_pkg_tree），然后拷入 `packaging/DEBIAN/`，`fakeroot dpkg-deb --build` 打包、`dpkg-name` 规范命名。`distclean-local`（L28-39）负责清理全部生成物。

运行：装包后 `postinst:L7-13` 自动 enable+restart；手工操作用 `systemctl start/stop nvsm-prometheus-exporters`。运行时调参全部落 `/etc/nvsm-apis/nvsm-prometheus-exporters.config`：改抓取端口（L3）、轮询间隔（L4）、增删 exporter（L5-12 的 7 项清单，加上 processor_exporter 即启用 CPU 指标）、NVSM-APIs 地址（L13-15）——**改配置无需重新打包**，重启服务生效。验证：`curl localhost:8000/metrics` 应能看到 `alerts_count`、`GPU_count`、`os_*_capacity` 等指标行。本仓**没有测试**：无 tests 目录、无 CI 配置，验证只能靠部署后看指标与日志。

## 7. 设计决策与取舍（源码甄别）

**勘误 1（图谱 vs 源码）**：图谱 summary 称 alerts exporter 写入 "nvsm_alerts Gauge"，实际指标名是 `alerts_count`（`alerts_exporter.py:L23`）；按此名在 Grafana/PromQL 里查才有数据。

**勘误 2（叙述 vs 源码）**："配置驱动动态加载"只是半边故事——`main.py:L17-24` 还静态 import 了全部 8 个 exporter。缺了静态 import，pyinstaller 单文件里根本不会包含未在配置默认清单中的模块；新增 exporter 必须同时改配置**和**补静态 import，只改配置是不够的。

**源码 bug 三处（读指标前必知）**：① `gpu_exporter.py:L147` 把 status 拼成 `staus`，叠加 L146 用 "OK" 而 L104 用 "Ok" 的大小写分裂，导致健康 GPU 的 `gpu_health_<UUID>` 常驻 2（Critical 档）——该指标系统性失真；② `processor_exporter.py:L86` 详情请求硬编码 `':273'`，忽略传入的 port 参数，改配置 nvsm 端口后此模块仍打 273；③ `power_exporter.py:L95-98` 对 `LastPowerOutputWatts=="na"` 有 set(0) 保护，但 L126 `power_usage += int(...)` 无同样保护，遇 "na" 直接 ValueError，该轮采集整体失败。

**取舍与坑**：健康 rollup 状态（storage `storage_exporter.py:L24`、thermal `thermal_exporter.py:L20-21`、power `power_exporter.py:L23` 初始 -1）存在模块级 metric_map 里**只增不减**（如 `storage_exporter.py:L170-172`）——告警恢复后 `drive_health`/`fan_health` 等不回落，重启服务才复位；这是刻意的保守告警还是疏忽，代码无注释说明。各 exporter 在主循环里**串行**执行且 gpu 每级请求间 `time.sleep(5)`（`gpu_exporter.py:L93,L114`），8 GPU 机型一轮 GPU 采集就要 45 秒+，超过 20 秒名义间隔，实际抓取周期由最慢模块决定。全系统 `verify=False` 跳证书校验（`urllib3.disable_warnings` 各文件头部），适配自签证书的 BMC 场景。健康字符串比较三种写法并存（"Ok"/"OK"/else 兜底），Redfish 标准是 "Ok"，混用是历史坑。`configure.ac:L3` 的 `AC_INIT(hrgrest, 0.1)` 包名与 L21 的 `AC_PROG_GO` 是从其他项目复制模板的残留（本仓无 Go/C 源码），distname 与 deb 包名 `nvsm-prometheus-exporters`（`control.in:L1`）不一致但互不干扰。小杂项：`storage_exporter.py:L109` 多拼一个 '/'（与 L121 不一致，产生 //redfish 双斜杠，服务器一般容错）；L186-189 除零无保护；`gpu_exporter.py:L25` 的 `health_created` 是死变量。

## 8. 新人上路

**阅读顺序**：README（5 分钟）→ `main.py` 全文 86 行（主干）→ `pcie_exporter.py`（80 行，协议最短样本）→ 按兴趣跳 `gpu_exporter.py`/`storage_exporter.py`（动态 Gauge 与多级轮询的完整形态）。改代码前先想清楚 Python 2 语法约束（`main.py:L83` 的 print 语句是活化石，别顺手"修"成 Py3——整仓依赖 Py2 运行时，`control.in:L9` 的 `python-prometheus-client`/`python-requests` 也是 Py2 时代包名）。

**第一次改动建议**：加一个新 exporter——复制 `pcie_exporter.py` 改指标名与端点，然后在 `nvsm_exporters/Makefile.am:L11-19` 的 SOURCES 加一行、`main.py:L17-24` 补 import、config 清单加名字，三处缺一不可（见第 7 节勘误 2）。**排障**：服务起不来先看 `journalctl -u nvsm-prometheus-exporters`（300 秒窗口 10 次失败会被 systemd 熔断，`nvsm-prometheus-exporters.service:L3,L9`）；单指标缺失去配置清单核对模块名；单轮失败会在日志看到 "Failed"（`main.py:L84`）但服务不退出；配置文件语法错则进程直接 `sys.exit("Error in config file")`（`main.py:L49`）。**常见坑**：指标名动态生成（含 UUID/盘名后缀），在 Prometheus 里要用 `nvsm_*`/`os_*` 前缀模糊匹配；改配置必须重启服务（配置只在启动时读一次）；GPU 健康指标失真问题（第 7 节 bug ①）在读数排障时先排除人为因素。

---
*字数统计见文末回执；锚均从源码逐行核实（NVSM-Prometheus/ 前缀的路径相对仓库根）。*
