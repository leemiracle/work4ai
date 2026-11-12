# 02 · exporter 群 —— 8 个同构模块的采集面

## 1. 角色定位

`nvsm_exporters/` 下 8 个 `*_exporter.py`（80-189 行）是仓库的采集面，全部遵守两函数协议：`init()`（预建静态 Gauge）+ `ExportMetric(ip, port)`（每轮采集），由 `main.py:77` 鸭子类型驱动。数据源分两类：私有端点 `/nvsm/v1/`（alerts/gpu/pcie）与标准 Redfish `/redfish/v1/`（其余五个，分系统视角 `Systems/1/` 与机箱视角 `Chassis/1/`）。默认启用 7 个，processor 唯一缺席。

## 2. 内部结构

**协议模板（pcie_exporter.py，最短样本）**：L19 模块级 `metric_map = {}` 是 Gauge 注册表；L21-22 静态指标名；L24-46 init 幂等建 Gauge；L48 默认参 port 为字符串、main 传 int，靠 `str(port)` 兜住。

**三级轮询（gpu_exporter.py）**：L82 GET `/nvsm/v1/Systems/1/GPUs` 集合、L89 取 `Members@odata.count` 设 GPU 总数；L96 请求集合级 `Health.@odata.id` 汇总；L113-117 逐 GPU 请求详情；级间 `time.sleep(5)`（L93/L114）节流，8 GPU 机型单轮采集 45 秒+。

**动态 Gauge 惯用形**：GPU 侧 L123-128 以 UUID 拼 `pcie_link_width_<UUID>`，`PCIeLinkWidth[:-1]` 剥单位（x16→16）；L155-163 Retired Pages 为三项求和。存储侧 `storage_exporter.py:128-131` 以 `@odata.id` 含 `nvme0n1/nvme1n1` 判 OS/数据盘、`[-7:]` 拼名，每盘三 Gauge。

**健康汇总两种形态**：storage/power/thermal 用模块级 `metric_map["status"]`（初值 -1，`storage_exporter.py:24`）做 max rollup（L163-172）；memory 例外——`memory_exporter.py:109-118` 在 DIMM 循环内对同一 `dimm_health` 直接 set，**最后一个 DIMM 覆盖前面所有**。

## 3. 外部连接

- **向上**：被 `main.py:17-24` 静态 import（进 pyinstaller 单文件）+ L68-72 动态加载。
- **向凭据**：每轮读 `/etc/nvsm-apis/nvsm-apis-perpetual.jwt`（`pcie_exporter.py:65-66`）作 Bearer token。
- **向数据源与输出**：统一 `requests.get('https://'+ip+':'+port+endpoint, verify=False)`（`pcie_exporter.py:69`）；Gauge 入默认 REGISTRY 经 :8000/metrics 暴露，模块间零调用全靠 main 串接。

## 4. 数据流

```
读 JWT → Bearer GET https://<host>:273/<endpoint> → r.json()
  静态指标直接 set（pcie_exporter.py:78-79）
  集合响应：枚举 Members → 逐对象 GET @odata.id → 动态建 Gauge

深链两例：GPU 三级（`gpu_exporter.py:82→96→117`）；storage 双级嵌套（`storage_exporter.py:100→109→121`）。

## 5. 设计决策

**勘误（processor 双重边缘化）**：`nvsm-prometheus-exporters.config:5-12` 清单只有 7 项，processor 默认不启用；且 `processor_exporter.py:86` 详情请求硬编码 `':273'` 无视传入 port——改配置 nvsm 端口后它仍打 273，属"禁用了没人发现"的缺陷。

**健康字符串三写法并存**：`"Ok"`（`gpu_exporter.py:104`）与 `"OK"`（`gpu_exporter.py:146`、`storage_exporter.py:164`）及 else 兜底并存；Redfish 标准是 "Ok"，私有端点用 "OK"。叠加 `gpu_exporter.py:147` 变量名拼成 `staus` 且赋错对象，健康 GPU 的 `gpu_health_<UUID>` 常驻 2（Critical 档），系统性失真。

**rollup 只增不减**：`metric_map["status"]` 只接受更大值（`storage_exporter.py:170-172`），告警恢复后 `drive_health`/`fan_health` 不回落，重启才复位。**不对称保护**：`power_exporter.py:95-98` 对 `"na"` 有 set(0) 保护但 L126 求和无保护，遇 "na" 即 ValueError 整轮失败。

## 6. 新人提示

- **写新 exporter**：复制 pcie_exporter.py 改指标名/端点/解析；集合型端点抄 storage 双级循环骨架。
- **指标名**：动态名含 UUID/盘名，PromQL 用 `pcie_link_width_*` 模糊匹配；告警指标真名是 `alerts_count`（`alerts_exporter.py:23`），不是图谱写的 nvsm_alerts。
- **读数先验假**：per-GPU health 失真、dimm_health 只反映最后一个 DIMM，以 `gpu_healthrollup` 为准。
- **节流模块自治**：sleep(5) 在 gpu 模块内，main 的 interval 管不到；启用 processor 前先修 L86。

*锚自各 exporter 源文件逐行核实（a892c4cc）。*