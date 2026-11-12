# 讲透 NVIDIA/NemoClaw

NVIDIA NemoClaw（OpenClaw 系命名）是把 always-on AI agent（OpenClaw/Hermes/Deep Agents Code）安全装进 NVIDIA OpenShell 沙箱的开源参考栈。本目录是三步流水线（DeepWiki → understand 图谱 → onboard+explain）的完整产物集。

## 状态表

| 阶段 | 状态 | 说明 |
|---|---|---|
| DeepWiki | ✅ 完成 | 38/38 结构页 100%（2026-10-26 全层级对账终判"真一百分"；`deepwiki/` 含 INDEX/coverage/wiki_full） |
| understand 图谱 | ✅ 完成 | **14199 节点 / 31394 边 / 16 层 / 16 步 tour**，validator 0 issues 0 warnings，fingerprints **4071 文件 @ `ccf68dae`**（`ccf68daed3aa8dc1c6bf074b9ee3d32cad684295`）；图谱在仓内 `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ 完成 | `onboarding/ONBOARDING.md`（37KB，行号锚全源码实核） |
| explain 01-06（核心链路，组 1） | ✅ 完成 | sandbox 核心 / rebuild / gateway / preflight / policy / inference |
| explain 07-12（外围+资产线，组 2） | ✅ 完成 | MCP 桥 / 凭据安全域 / 技能体系 / .dsh+hermes / 二进制种子 / schema+Serving |

**字数口径（钉版）**：explain 系列按「不计空格总字符」验收，实际区间 3546-4608/篇（六节结构+行号锚密度下 2000-3500 不可达，沿系列 norm 上限 4800）。行号锚密度：07-12 每篇 17-47 处（文件锚+上下文裸行号锚），全部对照源码 `ccf68dae` 逐条核实。

## explain 索引（12 篇）

| 篇 | 主题 | 一句话 |
|---|---|---|
| 01 | sandbox 核心与 GPU 创建流 | onboard 状态机与 docker-gpu-patch 路由（组 1） |
| 02 | rebuild 子系统与断点续跑 | 事务化 rebuild 与 journal 恢复（组 1） |
| 03 | gateway 所有权与生命周期 | 网关双权威与跨 UID 治理（组 1） |
| 04 | preflight 与 readiness 就绪体系 | 就绪探针分层与失败分类（组 1） |
| 05 | policy 引擎与策略预设 | 90+ 函数的 preset 生命周期（组 1） |
| 06 | inference 受管推理与受管启动 | vLLM 集群/宿主本地双线（组 1） |
| 07 | MCP 桥与工具发现 | provider-mutation TOCTOU 补偿三明治 + sdk 1.30.0 锁定 + names-only 发现协议 |
| 08 | openshell 凭据安全域 | 五版本审计基线链 + dcode-wrapper 形状谓词族 + SSRF 双 BlockList（NAT64/6to4） |
| 09 | 双技能体系 | 22 maintainer + 6 contributor + 双 guide + _shared 8 = 31 目录 150 文件 |
| 10 | .dsh 工具与 hermes 补丁 | 68 ambient 工具宪法 + 3441 行 start.sh + 12 个带删除条件的 patch-*.py |
| 11 | 二进制种子与构建资产 | npm-cache-seed 85 归档 + esbuild 文本 bundle + 32 阶段 Dockerfile 430 处 checksum |
| 12 | 配置 schema 与 Serving 体系 | 仓级 9 schema + Model/Recipe/Preset 三分目录 + HF revision 三形态钉扎 |

## 勘误清单（源码核实 ≥10 条）

以下为 explain/onboard 写作与图谱甄别中对照源码 `ccf68dae` 实证的差异与修正，引用本仓数据时以本清单为准：

1. **`.dsh` 工具实为 68 个（非早期口径 20+）**：`ls .dsh/tools/` 70 项 = 68 个工具目录 + AGENTS.md + README.md；图谱 `file:.dsh/` 节点恰 68，盘图一致。68 个均为单 `index.ts` + 恰一个 async default 导出（AGENTS.md:25 宪法）。
2. **skills 是 31 目录 150 文件**：22 maintainer + 6 contributor + 2 guide（skills-guide/user-guide）+ `_shared`（8 文件）。图谱以三种 id 前缀并存（file:/document:/config:）合计恰 150 节点 31 目录；只查 `file:` 前缀会误得 30——**盘点 skills 必须跨前缀聚合**。
3. **`.mts/.cts` bundled 提取器零输出 → 补充提取器救回**：bundled 提取器对 `.mts`/`.cts` 扩展名初始零输出，补充提取后 145 个该类文件恢复出 1054 个 function/class 子节点（.agents/skills 脚本占大头）。配套的五型 TS 盲区手补量（languageNotes 全量统计）：barrel/re-export 60、vi.mock 56、`typeof import()` 21、requireDist/运行时 require 13、inline 类型位置 import 8（另有动态 import 11）。
4. **dist→src 重写**：`src/lib/private-networks.ts`、`src/lib/core/service-port-boundary.ts` 等的 import 指向 `nemoclaw/dist/shared/*.cjs` 编译产物（未构建克隆盘上不存在），依赖边一律归一到真实源 `nemoclaw/src/shared/*.cts`；`banner-boundary.cts` 节点注明"源模式 tsx 把 .cjs specifier 映射回 .cts"。
5. **根相对 require 兜底**：`bin/lib/agent-defs.js` 等 7+ 垫片以 `require("../../dist/…")` 根相对路径取编译产物，图谱解析按 dist→src 重写兜底（`bin/lib/*.js` 全部为"薄再导出垫片"形态）。
6. **诚实二进制 gzip 实证**：npm-cache-seed 的 102 个二进制文件（78 tgz + 24 分片）图谱节点全部如实标注"gzip 二进制（分片），结构提取为空属实"，零伪造结构；`.gitattributes:8` 注释钉版 `text=auto` 保留二进制检测是 tgz 可入库的前提。
7. **副作用模块零结构属预期**：`agents/langchain-deepagents-code/generate-config-entrypoint.ts`（load 即执行）、`nemoclaw-blueprint/scripts/http-proxy-fix.js`（猴子补丁）等脚本式模块结构提取为空是真实形态，勿当提取失败返工。
8. **NemoClawCommand abstract 全盲手工建**：`src/lib/cli/nemoclaw-oclif-command.ts:53` `export abstract class NemoClawCommand extends Command`——tree-sitter 对 abstract class 声明全盲，该 class 节点（全仓 100+ 命令的父类，注入 portable host fence/生命周期锁）为人工补建。
9. **#6576 双权威语义**：preflight 网关清理遵循双权威——NemoClaw 自持 vs 外部监督（supervised）两种模式下，外部监督网关一律 noop（`preflight-gateway-cleanup-decision.ts`："陈旧元数据不得销毁监督方持有的活网关"）；原 #6576 回归正是"两个受保护阶段+一个未保护阶段"，单阶段测试无法捕获（`preflight-gateway-sequence.test.ts` 节点注释钉版）。
10. **TOCTOU 补偿自带删除条件**：`src/lib/actions/sandbox/mcp-bridge-provider-mutation.ts:4-16` 头注释即完整设计文档——OpenShell v0.0.99 无 caller-supplied provider CAS，NemoClaw 以随机 provider 名 + mcp-lifecycle-lock + 不可变身份/resourceVersion 后检三重补偿，inspect-mutate-inspect 三明治 + 一律 fail closed；removalCondition 明写等上游暴露原生 CAS 后移除。
11. **start.sh 实测 3441 行 / 86 个函数定义**（任务前期口径 3142 行/65 函数已过时）：`wc -l`=3441；函数定义按 `^[a-z_0-9]+\(\) *\{` 计 86。
12. **dcode-wrapper.sh 实测 1079 行**（非 1017）：密钥形状谓词族 `is_secret_shaped_value`（:283）串十余个 token 正则族（sk-proj/nvapi/ghp/AK·SIA/JWT/xox/lsv2 等）。
13. **npm-cache-seed 对账口径差**：manifest `archiveCount: 85` 按"归档"计（78 完整 tgz + 7 个分片化大包），磁盘文件数 102（+manifest.json=103 目录项）——`ls | wc -l` 对不上是预期，对账以 manifest 为准；`npm-ci-locked.sh:21-27` 显式拒绝完整+分片并存。
14. **`.bundle` 是 esbuild 文本非二进制**：`file` 命令实测三个 bundle 均 ASCII text（CJS 打包），受 `.gitattributes:13` `linguist-generated -diff` 标记；可 diff 可 grep 审计。
15. **MCP SDK 版本两处口径勿混**：`tools/mcp-tool-discovery-runtime/package.json:10` 精确锁 `@modelcontextprotocol/sdk: 1.30.0`（沙箱 runtime 专用）；根 package-lock 里 `^1.25.2` 是 pi-coding-agent 的 optional peerDep——引用"1.30.0 锁定"时必须指明前者。
16. **凭据审计基线的 provenance 是 v0.0.101 才有的**：五版本链 v0.0.72/85/99/101/116 中，前三个无 `generation` 块（method+逐源文件 sha256 证据），v0.0.101 起加入——"审计协议 generation.method"不可回溯套用到早期基线。
17. **32 阶段 Dockerfile 的真实密度**：主 Dockerfile `FROM` 32 处、`ADD --chmod=0444 --checksum=sha256:` 430 处、node 基础镜像以 tag+digest 双钉（`node:24.18.1-trixie-slim@sha256:ac39e4b5…`，:16 与 :608 两处复用）。

## 数据 provenance 备注

- 图谱/指纹/校验报告在仓内 `.understand-anything/`（knowledge-graph.json、fingerprints.json v5、validate-report.json、meta.json）。
- **NOTES-DIGEST.md 事故记录（2026-11-07）**：批阶段甄别笔记曾被协调会话误清，现仅恢复批 146-175 段；批 1-145 段不可恢复，但批甄别结论大部分同步在图谱节点 `languageNotes` 字段（本 README 勘误第 2/3/4/5/8/9 条的统计与引文均直接出自 languageNotes 与源码，不依赖 digest）。
- explain 07-12 全部行号锚经「文件边界校验 + 内容 grep 抽查」双通道核实（30 处 file:line 锚 + 每篇 10-39 处上下文行号锚）。
