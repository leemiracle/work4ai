# 讲透 Chromium · 深度知识库

> 基于 understand-anything 中文知识图谱 + 官方文档 + 核心源码深解的 Chromium 学习知识库。
> 生成于 2026-10-10，对应源码 GitHub 官方镜像 chromium/chromium @`8fe2331`（2026-10-08 main）。

## 这是什么

Chromium 是 Google 的开源浏览器引擎主体（Chrome 的上游），多进程架构 + C++ 主体的超级代码库。本知识库是**迄今本机最大规模**的 understand 图谱实践（509k 文件裁剪至 10,929 核心 文件全量分析），服务于三类场景：

| 场景 | 用哪部分 | 怎么用 |
|---|---|---|
| 新人系统上手 | `onboarding/ONBOARDING.md` | 从头读：技术栈总览→多进程架构→16 层金字塔→一条 URL 的生命周期→目录速查→6 周上手路径 |
| 啃核心源码 | `explain/`（12 篇） | 每篇一个核心文件的深度解析：角色定位→内部结构→外部连接→数据流→设计决策→新人提示（行号实证） |
| 交互式探索 | 知识图谱（仓内） | **40,412 节点/102,182 边/16 层/16 步导览**全中文图谱，位于 `/usr-data/data1/browser/chromium/src/.understand-anything/knowledge-graph.json`（39MB），用 understand-anything 插件 `/understand-chat`、`/understand-dashboard` 交互查询 |
| 查官方一手文档 | `repo-docs/` + `docs-online/` | 仓内文档 1818 篇 + chromium.org 在线架构文档 8 篇（多进程模型/IPC/渲染/站点隔离等） |

> 注：DeepWiki 未收录 Chromium（探测确认为未索引状态，见 `deepwiki/_PROBE.md`），本知识库以 understand 图谱为主力数据源、官方文档为补充。

## 规模与统计

| 指标 | 数值 |
|---|---|
| 源码基线 | chromium/chromium @8fe2331（浅克隆 7.5G/509k 文件） |
| 分析文件（白名单裁剪后） | 10,929（.understandignore v3：大目录全裁+反选核心） |
| 图谱节点/边 | **40,412 / 102,182**（file 10,809 + function/class/concept 等约 29.6k） |
| 分层 | 16 层（chrome 外壳→content 三分→渲染栈 cc/viz/gpu→网络 net/services→mojo→sandbox→base） |
| 导览 | 16 步（进程模型→启动→IPC→页面加载→渲染管线→显示输入→浏览器壳→服务化→地基收尾） |
| 批分析 | 442 批（439 完成 + 15 零代码跳过），4 并发滚动派发，0 损坏 |
| 校验 | ua-inline-validate **0 issues**（节点完整性/边悬挂/层覆盖/file 全归层） |
| 指纹基线 | fingerprints.json @8fe2331，支持增量更新 |

## 目录结构

```
讲透Chromium/
├── README.md                  # 本文件
├── onboarding/
│   └── ONBOARDING.md          # 新人上手指南（10,107 字，8 节，83 代表文件零编造）
├── explain/                   # 12 篇核心文件深解（2500-4800 字/篇，行号实证）
│   ├── render-process-host.md         # 渲染器宿主 RenderProcessHostImpl（13 节点）
│   ├── child-process-launcher.md      # 子进程孵化 ChildProcessLauncher
│   ├── net-url-request.md             # 网络请求核心 URLRequest（15 节点）
│   ├── dns-host-resolver.md           # DNS 解析调度 HostResolverManager（40 节点）
│   ├── cc-layer-tree-impl.md          # 合成器层树 LayerTreeImpl（48 节点）
│   ├── viz-root-frame-sink.md         # 显示合成 RootCompositorFrameSinkImpl
│   ├── gpu-webgpu-decoder.md          # GPU 命令解码 WebGPUDecoderImpl
│   ├── views-view.md                  # View 基类（4244 行）
│   ├── views-widget.md                # Widget 窗口容器（69 节点全图谱前列）
│   ├── chrome-profile.md              # Profile 用户配置
│   ├── base-thread-pool.md            # 线程池调度 ThreadPoolImpl
│   └── sandbox-target-process.md      # 沙箱目标进程
├── repo-docs/                 # 仓内文档 1818 篇（docs/ 全量转 md）
├── docs-online/               # chromium.org 架构文档 8 篇 + INDEX.md
└── deepwiki/_PROBE.md         # DeepWiki 探测记录（未索引结论）
```

## 推荐阅读路径

```
docs-online/（30min：多进程模型 + displaying-a-web-page 两篇建立世界观）
   ↓
ONBOARDING.md（2h：16 层金字塔 + 一条 URL 的生命周期）
   ↓ 挑感兴趣的子系统
explain/ 进程与加载线（render-process-host → child-process-launcher → net-url-request → dns-host-resolver）
   ↓ 渲染显示线（cc-layer-tree-impl → viz-root-frame-sink → gpu-webgpu-decoder）
   ↓ UI 与地基线（views-view → views-widget → chrome-profile → base-thread-pool → sandbox-target-process）
   ↓ 想动手时
知识图谱交互探索（understand-chat / understand-dashboard）
```

## 生成方式

- 源码：GitHub 官方镜像（googlesource git 协议被本机链路系统性掐死，走 chromium/chromium 镜像 + ghfast 轮转）
- 图谱：understand-anything 流水线（scan 10,929 文件 → 442 批 file-analyzer 4 并发滚动 → merge 40,412 节点/102,182 边 → 16 层 architecture-analyzer（前缀法适配万级节点）→ 16 步 tour-builder → 校验 0 issues → fingerprints 基线）
- 指南与深解：全部基于图谱 + 源码只读交叉验证（行号实测），零编造校验通过
