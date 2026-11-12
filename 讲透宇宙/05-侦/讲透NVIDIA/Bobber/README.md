# 讲透 NVIDIA/Bobber

> NVIDIA Bobber（v6.3.1）：容器化 AI 系统性能基准框架——单/多节点 NCCL 集合通信、fio 存储（1MB 带宽/125K 块/4K IOPS）、mdtest 元数据、DALI 数据摄取四条运行链 + OSU/MLPerf 两个"建好待用"接口，build/cast/execute 容器生命周期与 parse-results 解析验收闭环。本地仓 `/usr-data/data2/repos/agent-repos/NVIDIA/Bobber` @ 39435ee。
> 本目录=understand 全链知识库产物（2026-11-07，微仓一体通道）。

## 全链状态表

| 阶段 | 状态 | 关键数据 |
|---|---|---|
| prepare | ✅ 2026-11-07 | 45 文件（.understandignore 仅排除 /.understand-anything/ 自身与二进制资源 *.png/*.jpg/*.pdf/*.bin；docs/ 7 篇全入图谱）/ 11 批 |
| 批分析 | ✅ | NOTES-DIGEST 收割 16 条甄别笔记（批阶段逐文件源码锚） |
| merge+layers/tour | ✅ | 149n/294e/4 层（入口门面/子系统/脚本与 CI/文档）/6 步 tour |
| finalize | ✅ | validator 0 issues；fingerprints 45 文件@39435ee6 |
| ONBOARDING | ✅ | `onboarding/ONBOARDING.md` 8 节 / ~5.5K 不计空格字符 / 60+ 锚（全部源码核实） |
| explain | ✅ 4 篇（微仓从简档） | 01 主入口与五子系统 / 02 解析器族与聚合链 / 03 容器与测试脚本 / 04 CI 双轨与基线；每篇 ~2K 字符 / 21-23 锚 |

图谱：仓内 `.understand-anything/knowledge-graph.json`（149n/294e/4 层/6 步 tour）。

## 勘误清单（源码级实证，graph 笔记/文档 vs 源码以源码为准）

1. **DGX_2 预设键连字符 vs A100 下划线**（本仓最典型一致性坑）：`bobber/lib/constants.py:41-49` 的 `DGX_2` 字典用 `bw-threads`/`batch-size-sm` 等连字符键，而 `DGX_A100_SINGLE/DUAL`（`constants.py:15-37`）用 `bw_threads` 下划线键。`load_settings()` 把预设键直接 setattr 成 args 属性（`bobber/bobber.py:345-347`），消费端 `run_tests.py:84` 只认 `args.bw_threads`——选 `--system dgx-2` 且不显式覆盖时连字符键落不到正确属性上，预设等于部分失效。
2. **"五类基准"口径要拆开说**：任务/图谱口径"NCCL/OSU/IO500/fio/mlperf 五类"中，OSU 只被构建进镜像（`Dockerfile:56-62` 编译、`Dockerfile:111` 拷贝）但 `test_scripts/` 无任何 osu runner；MLPerf 只有独立解析器 `bobber/lib/analysis/parse-mlperf.py`（无 runner、全仓零 import）。运行链真正有 runner 的是 NCCL/fio×3/mdtest/DALI 四条。
3. **`GIT_SUBMODULE_STRATEGY: recursive` 是残留配置**：`.gitlab-ci.yml:7` 声明子模块递归拉取，但本仓**无 `.gitmodules`**（ls 实证）；nccl-tests/io-500-dev 是 Dockerfile 构建期 `git clone`+`reset --hard` 钉 commit（`Dockerfile:50-53/65-68`），不是 git 子模块。批阶段笔记"以子模块方式引入测试工具仓"系误读，已钉正。
4. **`parse-results` 无条件覆盖写 `baseline.yaml`**：`parse_results.py:404` 每次解析都把本次结果写成基线文件（`save_yaml_baseline`，`parse_results.py:257-304`），手工维护的自定义基线若放在结果目录同名文件会被覆盖——`--custom-baseline` 应指向目录外路径。
5. **`fio_fill_single.sh` 不可用（历史残留）**：`bobber/test_scripts/fio_fill_single.sh:4` `cd /storage-perf-test`，该目录不在镜像内（Dockerfile 只拷 nccl-tests/osu/io-500 产物），且转调的 `run_disk_fill_test.sh` 同样不存在。
6. **mdtest 线程数硬编码 44**：`mdtest_multi.sh:4-5` 注释自认"线程多了会 blow up、原因不明"——上游 io-500 mdtest 的已知行为，非本仓 bug，但别当可调参数。
7. **DALI 聚合口径是"单节点均值×N"**：`dali.py:272-275` 把平均吞吐乘系统数外推集群值，warmup 丢弃用"最低 N 个当首轮"启发式（`dali.py:210`）——多机数字是近似外推，不是逐节点实测求和，与 fio 的 sum 逐节点求和（`fio.py:209-210`）口径不同。
8. **NCCL max_bus_bytes 取众数不取均值**：`aggregate_results.py:458-459` 取出现次数最多的字节数——尺寸档位是离散的，这是正确取舍，但读 JSON 的人常误以为是均值。

### 图谱工程注记（流水线侧，非源码问题）

- **scanner 自引用污染**：scan 吞过 `.understand-anything/` 自身旧产物形成幽灵节点/边，merge 前已删除（.understandignore 已补排除）。
- **tree-sitter 漏提两类**：`parse-mlperf.py` 的 `Aggregate`（`:9`）与 `Results`（`:32`）两个 class 声明未被提取，批阶段手工补齐进图谱。
- **importMap 漏 1 条**：`bobber/bobber.py:6` 的 `from bobber import __version__` 在 scanner importMap 中缺失，已补。

## 生成口径

- 字数口径：ONBOARDING/explain 均「不计空格字符」；explain 微仓从简档 4 篇（<50 代码文件仓规格）。
- 行号锚全部从源码核实（2026-11-07，@39435ee）；`Dockerfile`/`*.sh`/`*.yml` 锚为仓库相对路径。
- 快速上手：`onboarding/ONBOARDING.md` §8 有 6 步新人路径；四篇 explain 对应图谱 tour 的 2-5 步。
