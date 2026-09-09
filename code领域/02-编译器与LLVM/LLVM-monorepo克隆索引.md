# LLVM monorepo 克隆索引卡

> 本目录不含 LLVM monorepo 本体——156,484 个跟踪文件 / git 对象库 2.14 GiB，
> 整体搬入会突破 GitHub 推送上限（单推 ≤2GB）并拖垮本机 `git status`。
> 2026-09-09 用户决策：只迁自有层，monorepo 留此索引卡，可随时重克隆。

## 克隆信息

| 项 | 值 |
|---|---|
| 上游 | <https://github.com/llvm/llvm-project> |
| 本地删除前 commit | `f4c76bba5909e9c3e542ac723b9a1c0f1c229e79`（main 分支） |
| 重装命令（直连） | `git clone https://github.com/llvm/llvm-project.git --depth 1` |
| 重装命令（国内加速） | `git clone https://ghproxy.cn/https://github.com/llvm/llvm-project.git --depth 1`（`--depth 1` 省 2GB 历史） |

## 本地曾有的自有层（已全部抢救进本目录）

| 内容 | 去向 |
|---|---|
| `llvm_experiments/`（LEARNING_PATH/QUICK_START/C 实验/脚本，工作树 37 文件） | [`llvm_experiments/`](./llvm_experiments/) |
| 根目录 IT 学习与项目管理平台（backend/cli/frontend/knowledge-base/python-learning-project/docs + 10 个架构 md，154 文件） | [`IT学习平台/`](./IT学习平台/) |
| `llvm/include/llvm/IR/Use.h` 与 `Value.h` 的本地改动（751 行 diff） | [`patches/Use-Value头文件改动.patch`](./patches/Use-Value头文件改动.patch)（重克隆后 `git apply` 恢复） |
| 根目录 `planning-methodology.md`（曾在 index、工作树已删，1325 行） | [`planning-methodology.md`](./planning-methodology.md) |
| `LLVM项目研究/`（Expert_01..13 专家笔记 45 md，原在 C:\workspace 独立目录） | [`LLVM项目研究/`](./LLVM项目研究/) |

## 未迁内容说明

- monorepo 的 34 个 symlink 状态文件（Windows `git status` 误报 M/D 的测试 symlink）——非用户改动，无价值
- `.env`（敏感配置，按仓库红线不迁移）
- 其余 15.6 万上游源文件——即索引卡存在的理由
