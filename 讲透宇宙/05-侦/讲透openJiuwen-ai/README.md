# 讲透openJiuwen-ai — openJiuwen-ai org 全量知识库（2026-11-02）

GitHub org [openJiuwen-ai](https://github.com/orgs/openJiuwen-ai/repositories) 全部 **26 仓**，2026-11-02 单轮完成 DeepWiki 流水线（MCP 通道批量抓取 + 全层级终判 + repo-docs 兜底）。

## 状态表

| 仓 | stars | 语言 | DeepWiki | 页数 | 规模 | 兜底 |
|---|---:|---|---|---:|---|---|
| jiuwenswarm | 8543 | Python | ✅ TRUE_100 | 43 | 748K | — |
| agent-core | 465 | Python | ✅ TRUE_100 | 74 | 1971K | — |
| iCode | 410 | Python | ✅ TRUE_100 | 47 | 773K | — |
| agent-studio | 192 | Java | ✅ TRUE_100 | 60 | 3476K | — |
| sciencediscovery | 184 | TypeScript | ✅ TRUE_100 | 31 | 404K | — |
| deepsearch | 129 | Python | ✅ TRUE_100 | 37 | 572K | — |
| agent-protocol | 115 | Python | ✅ TRUE_100 | 31 | 391K | — |
| agent-infer | 105 | Python | ✅ TRUE_100（终判） | 31 | 608K | — |
| agent-memory | 75 | Python | ✅ TRUE_100（终判） | 37 | 557K | — |
| jiuwensymbiosis | 69 | Python | ✅ TRUE_100（终判） | 42 | 1183K | — |
| agent-core-java | 46 | Java | ✅ TRUE_100 | 40 | 788K | — |
| agent-runtime-java | 34 | Java | ✅ TRUE_100 | 38 | 1278K | — |
| docs | 32 | — | ✅ TRUE_100 | 13 | 121K | — |
| skillhub | 32 | Python | ✅ TRUE_100（终判） | 29 | 517K | — |
| agentos-enterprise | 20 | Shell | ✅ TRUE_100（终判） | 28 | 347K | — |
| agent-tools | 19 | C++ | ✅ TRUE_100（终判） | 26 | 414K | — |
| agent-runtime | 15 | Python | ✅ TRUE_100（终判） | 31 | 483K | — |
| community | 13 | — | ✅ TRUE_100 | 22 | 287K | — |
| model-router | 13 | Python | ❌ NOT_INDEXED | — | — | 📄 repo-docs 14 md |
| relay | 5 | TypeScript | ✅ TRUE_100 | 32 | 687K | — |
| agent-dx | 3 | Rust | ✅ TRUE_100（终判） | 24 | 298K | — |
| computer-use | 3 | Python | ❌ NOT_INDEXED | — | — | 📄 repo-docs 5 md |
| agent-gateway | 4 | Python | ❌ NOT_INDEXED | — | — | 📄 repo-docs 27 md |
| agent-security | 7 | Python | ❌ NOT_INDEXED | — | — | 📄 repo-docs 69 md |
| agent-plugin | 1 | Python | ❌ NOT_INDEXED | — | — | 📄 repo-docs 16 md |
| .github | 4 | — | ❌ NOT_INDEXED | — | — | —（org 配置仓，无文档） |

**合计：20/26 TRUE_100（716 页 ≈17.5MB）· 6 NOT_INDEXED（5 仓 repo-docs 兜底 + .github 无文档）**

## 目录结构

- `<repo>/deepwiki/` — DeepWiki 全量页（INDEX.md + 编号页 + `_coverage-check.md`）
- `<repo>/repo-docs/` — 未收录仓的仓内文档收割（README/docs 原样镜像，`_filelist.txt` 清单）
- `<repo>/onboarding/` · `<repo>/explain/` — understand 全链产物（ONBOARDING.md ~6000字8节 + explain 精讲系列）

## understand 全链状态（2026-11-02 晚起，6 仓队列）

| 仓 | 文件/批 | 图谱 | onboard | explain | 备注 |
|---|---|---|---|---|---|
| agent-plugin | 60/8 | ✅ 162n/331e/14层/15步@f05b329 | ✅ 5999字48锚 | ✅ 6 篇 632 锚 37332 字 | **全链收官**；小仓口径 |
| model-router | 120/7 | ✅ 442n/944e/15层/16步@dd68ef0a | ✅ 6996字53锚 | ✅ 12 篇 404+142 锚 | **全链收官**；Rust+PyO3 双语言 |
| agent-gateway | 329/18 | ✅ 1445n/2961e/16层/15步@7af20225 | ✅ 6991字33锚 | ✅ 12 篇 89792 字 | **全链收官**；scanner 全盲仓 464 边全靠 ast 重扫 |
| agent-security | 400/30 | ✅ 1209n/2725e/16层/16步@3cf4c82a | ✅ 7773字61锚 | ✅ 12 篇 243+锚 | **全链收官**；四子系统安全合集 |
| computer-use | 1020/42 | ✅ 3238n/8174e/16层/16步@8a21429e | ✅ 12008字 | ✅ 12 篇 121570 字符 162 锚 | **全链收官**；scanner 稀疏（300 边/1020 文件）靠 ast 重扫+47 inherits 手术补录 |
| jiuwenswarm | 4877/257 | ✅ 19290n/39329e/16层/16步@8827ad7b5e | ✅ 7563字 | ✅ 12 篇 132607 字符 737 锚 | **全链收官**；8543★ 旗舰，史上最大图谱；drop 255 三段归因+手术补 82 |

图谱在各仓 `.understand-anything/knowledge-graph.json`；台账 `/usr-data/data2/repos/agent-repos/deepwiki-batch/understand-oj.md`。

## 轮次说明

- **抓取通道**：`dw_fetch_mcp.py`（mcp.deepwiki.com/mcp stateless），10 并发单轮 ~3min 零限流
- **终判**：10 仓 exit1 全为三级页假阴性（结构外页形态，如 agent-dx 23/19），`dw_reconcile_dir.py --write` 全层级对账后 **MISSING=0 全数 TRUE_100**，结论已回写各 `_coverage-check.md`
- **本地克隆**：26/26 全量已 clone 至 `/usr-data/data2/repos/agent-repos/openJiuwen-ai/`（本轮补齐 11 个低星仓 + 15 仓 pull 更新，origin 混直连/镜像三通道容错）
- **台账**：`/usr-data/data2/repos/agent-repos/deepwiki-batch/`（manifest-oj.txt · oj-status/ · oj-logs/ · oj-worker.sh · 放弃清单-oj.txt）

## 钉版坑（本轮实录）

1. **dotfile 三连坑**：`ls`/glob `*/`/`grep oj-status/*.status` 全部漏 `.github`（状态盘点必须 `ls -A` + 显式点名）；repo_docs_harvest 也跳过 dotdir，`.github` 如实记"无文档"
2. **dw_reconcile_dir.py 的 DIR 参数必须指到 `deepwiki/` 层**（含 `_structure.txt`），指到 `<repo>/` 层报 NO_DIR_OR_STRUCTURE
3. **worker 预建空 `deepwiki/` 目录**要在终态前清掉，否则统计脚本把 NOT_INDEXED 仓误判为"有 deepwiki 0 页"
4. **网络三级容错实战**（clone 阶段）：clash 节点死→直连通→直连被掐→gh-proxy 镜像全胜——单通道脚本扛不住这种抖动，`/tmp/oj_clone_one.sh` 的 direct→gh-proxy→clash 降级链是本轮唯一全胜姿势
