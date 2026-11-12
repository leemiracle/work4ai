# 讲透 remote-media

> NVIDIA 维护的 OpenBMC remote-media（VirtualMedia 守护进程）—— Redfish 虚拟介质服务：https/smb/file 三源镜像经 NBD + USB gadget 虚拟成 BMC 的 CD/USB，含掉电安全的重启持久化挂载。
> 本地仓：/usr-data/data2/repos/agent-repos/NVIDIA/remote-media（commit cee2e0e5，约 4700 行 C++/hpp）

## 状态（2026-11-10 ✅ 全链路完成）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki)（38 内容页 100%） |
| understand 中文图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（**72 节点/136 边/5 层/6 步 tour**，validator 0 issues，fingerprints 24 文件基线@cee2e0e5） |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（8663 不计空格字符，7 节，46 行号锚全验证通过） |
| explain 系列 | ✅ | [explain/](explain) 2 篇（5030/4130 字符，六节结构，锚 52+10 全验证） |

## explain 索引（2 篇）

| # | 篇 | 对象 |
|---|---|---|
| 01 | [state-machine.md](explain/01-state-machine.md) | MountPointStateMachine：variant 六态六事件转移表+operator() 重载分派 |
| 02 | [persistence.md](explain/02-persistence.md) | persistence.hpp 三 hook 原子写+自愈读+main.cpp 启动 replay 协程 |

## 本轮沉淀的勘误（对 DeepWiki/图谱摘要/NOTES 的修正，均源码实证）

- **根 README.md 是 GitLab 自动生成模板**（Getting started 样板章节，零项目信息）——真实设计文档在 docs/persistent-mount.md（486 行，Status: Implemented，Source 栏 docs/persistent-mount.md:10 指向四个实现文件）
- **六状态真名与图谱 tour 不符**：源码是 InitialState/ReadyState/ActivatingState/WaitingForGadgetState/ActiveState/WaitingForProcessEndState（src/state_machine.hpp:84-209），tour 写的 Invalid/Waiting/Detached/Busy 不存在于源码
- **配置文件打不开 = 服务退出**，非"警告后空配置继续"：loadConfiguration Critical + return false（src/configuration.hpp:74-79），main 随即退出（src/main.cpp:375-379）
- **SMB 卸载用 ::umount 非 umount2**（src/smb.hpp:105，图谱摘要误写 umount2）
- **gtest 用例是 26 个非 29**（grep -c "^TEST"=26：6 个 UrlPredicates TEST tests/test_persistence.cpp:35-100 + 20 个 PersistenceFsTest TEST_F :174-383）
- **logger 是 7 个 tag 结构非 6 个空结构**：Struct/Debug/Info/Warning/Error/Critical 各带 constexpr value+name 两成员（src/logger.hpp:11-45）；LOG_LEVEL 硬编码 Debug（logger.hpp:6）把 value=6 的 Struct 假级别编译期滤掉
- tree-sitter 双盲区再证：嵌套 struct（六状态六事件）与 TEST/TEST_F 宏展开的测试函数在静态提取里全空，图谱这批节点为批分析手工补齐

## 工程信息

- 流水线：DeepWiki MCP 通道 + understand 批分析（嵌套 struct 手补域）+ layers/tour + finalize + 写作收官
- 字数口径：不计空格总字符；行号锚口径：仓内唯一 basename 自动展开后逐一验证（46/52/10 全过）
