# 讲透 NVIDIA NV-Kernels

> 源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/NV-Kernels` @ commit `c3d16b0f`（GitHub Actions CI 分支）
> 知识图谱：仓内 `.understand-anything/knowledge-graph.json`

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| 批分析（2 批/11 文件） | ✅ 2/2 | 终验 0 issues；无扩展名 Python 脚本（validate-pr/patchscan）tree-sitter 零提取，28 个函数节点全手扫；手扫补 17 条 CI 编排语义边 |
| understand 图谱 | ✅ 完成 | **50 节点 / 57 边 / 6 层 / 12 步导览**，validator **0 issues 0 warnings**，fingerprints 基线 **11 文件 @ c3d16b0f** |
| Onboarding | ✅ 完成 | `onboarding/ONBOARDING.md`（8 节 / 5000 不计空格字符 / 23 锚 / 3 勘误） |
| explain 精讲 | ✅ 3/3 | `explain/01-03`，六节结构、111 锚、59 处抽验 0 真坏 |

## explain 索引（3 篇）

| # | 篇目 | 主题 | 字数（不计空格）/锚 |
|---|---|---|---|
| 01 | validate-pr | 1086 行 PR 校验规则全解（无扩展名 Python） | 2679 / 39 |
| 02 | patchscan | pull_request_target 注入防护 + 扫描脚本 | 2696 / 39 |
| 03 | kernel-build | arm64 6.12.33 内核构建 + 4K/64K 页配置 | 2910 / 33 |

## 勘误与甄别（源码一手核实）

1. **README 未提及 validate-pr-tests.yml**：文档只覆盖 3 个 workflow，实际 4 个（文档滞后）。
2. **action 钉法三态并存**：patchscan.yml 用 @v6/@v9 tag、kernel-build.yml 用 @v4、**只有 validate-pr-tests.yml 是 SHA 钉**——"全套 SHA 钉"的说法仅适用于后者（explain 期甄别钉版）。
3. **validate-pr 规则编号 R2/R4 空洞**：实引外部规范全集，代码仅实现八条。
4. **config_4k vs config_64k 差异口径钉死 72 行**（< 51 + > 21，不含 diff 标记行；页大小/页表级数/VA bits）。
5. **requirements.txt 被扫描器误归 docs**：实为 pip 依赖锁定（b4/colorama/GitPython），已按 config 节点建模。
6. **patchscan.yml 用 pull_request_target 且带全套注入防护**（SHA/ref/repo 正则校验 + persist-credentials:false + action 钉版本）——危险的 trigger 与防御并存的样板。

## 一句话

NVIDIA 开源 Linux 内核仓（Grace arm64）的 CI 分支仓：四条 workflow + 两个无扩展名 Python 校验脚本，1.47 万行内核 .config×2——仓库小而 CI 工程浓度高。
