# 讲透 NVIDIA NVSM

> 源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/NVSM` @ commit `a892c4cc`
> 知识图谱：仓内 `.understand-anything/knowledge-graph.json`

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| 批分析（2 批/20 文件） | ✅ 2/2 | 终验 0 issues；imports 8/8 AST 重扫零差异；b2 全 configures/deploys/depends_on/documents 语义边 |
| understand 图谱 | ✅ 完成 | **36 节点 / 89 边 / 7 层 / 12 步导览**，validator **0 issues 0 warnings**，fingerprints 基线 **20 文件 @ a892c4cc** |
| Onboarding | ✅ 完成 | `onboarding/ONBOARDING.md`（8 节 / 7903 不计空格字符 / 锚 95 处粗计；1302 死于统计期，盘上验收采纳） |
| explain 精讲 | ✅ 3/3 | `explain/01-03`，六节结构、53 锚全核验（13 个勘误级锚做了内容断言） |

## explain 索引（3 篇）

| # | 篇目 | 主题 | 字数（不计空格）/锚 |
|---|---|---|---|
| 01 | main.py | Python 2 顶层脚本：exporter 注册编排（importlib 死导入/__import__ 实用） | 2482 / 15 |
| 02 | exporter 群 | redfish 系统视角/三级轮询动态 Gauge/chassis 机箱视角 | 2500 / 19 |
| 03 | 打包部署链 | autotools + pyinstaller + systemd | 2499 / 19 |

## 勘误与甄别（源码一手核实）

1. **main.py 是 Python 2 脚本**：L83 `print e` 语句级证据（ast.parse 失败）；control.in 的 `python-prometheus-client` Py2 包名互证。tree-sitter 零函数提取属正确（本就无函数定义）。
2. **importlib 死导入**：import 的 importlib 从未使用，实际动态装载走 `__import__`。
3. **configure.ac 模板复制痕迹**：`AC_INIT(hrgrest, 0.1)` 残留无关包名 + AC_PROG_GO 声明但仓内零 Go 源码。
4. **processor_exporter 被编译但默认禁用**：且 L86 硬编码 `:273` 端口忽略 port 参数、config 的 host 字段全仓无人消费。
5. **默认 config 只启用 7 个 exporter**（共 8 个 exporter 模块）。
6. **API 双风格并存**：`/nvsm/v1/*` 与 `/redfish/v1/*` 两套路由。
7. **根 Makefile.am 的 release 目标依赖未定义的 rpm 目标**（构建断链）。
8. **`nvsm_prometheus_exporters` "二进制"实为 pyinstaller --onefile 产物**（Python 打包，非原生编译）。

## 一句话

NVIDIA System Management 的 Prometheus exporter：Python 2 时代遗产 + Redfish/NVSM 双风格 API + autotools/pyinstaller/systemd 三层打包——历史地层丰富的老仓，读它先认 Py2 语法与模板残迹。
