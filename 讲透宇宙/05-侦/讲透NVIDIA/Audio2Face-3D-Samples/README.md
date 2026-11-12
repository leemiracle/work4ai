# 讲透 NVIDIA Audio2Face-3D-Samples（全链状态总索引）

> 上游仓：[NVIDIA/Audio2Face-3D-Samples](https://github.com/NVIDIA/Audio2Face-3D-Samples) · 本地 `/usr-data/data2/repos/agent-repos/NVIDIA/Audio2Face-3D-Samples` · commit `a2d0150`（2026-03-11 "Add NGC Catalog links to README"）。
> 定位：A2F-3D NIM 官方示例集——proto gRPC 契约 + 三套客户端（NVCF api_client / early_access authoring / 本地 interaction app）+ 配置族 + quick-start 容器编排 + v1.0→v1.2 迁移工具。

## 全链状态表

| 阶段 | 产物 | 状态 |
|---|---|---|
| DeepWiki 抓取 | [deepwiki/](deepwiki)（2026-10-26 轮，MCP 通道）：结构 20 页 100% 命中，全文 206,139 字符，INDEX + _coverage-check + wiki_full，终判真一百分 | ✅（前置轮已有） |
| understand 图谱 | 仓内 `.understand-anything/knowledge-graph.json`：**220 节点 / 395 边 / 10 层 / 15 步 tour**，validator 0 issues，fingerprints **87 文件@a2d01500** | ✅ finalize |
| 批甄别笔记 | 仓内 `.understand-anything/NOTES-DIGEST.md`（21 条，本 README 勘误清单的底稿） | ✅ |
| onboarding | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)：8 节，8689 字（不计空格），**41 个全路径行号锚**（另含上下文短锚 50 处） | ✅ |
| explain | [explain/](explain) 6 篇，六节结构（角色定位/内部结构/外部连接/数据流/设计决策/新人提示），合计 15031 字（不计空格），全路径锚 33 + 上下文短锚 123 | ✅ |

### explain 索引

| 篇 | 主题 | 字数（不计空格） |
|---|---|---|
| [01-proto契约层.md](explain/01-proto契约层.md) | 16 proto 全契约面：AudioStream→FaceParameters 主链、双向流 ProcessAudioStream、双 AudioStreamHeader 同名异构、whl 预编译 vs generate_code_from_protos 生成链 | 2640 |
| [02-api_client.md](explain/02-api_client.md) | NVCF 云端三件套：auth（grpc.aio）/service（write_to_stream+read_from_stream）/nim_a2f_3d_client 入口；Riva 遗留 docstring | 2222 |
| [03-early_access-authoring.md](explain/03-early_access-authoring.md) | Authoring 服务客户端：UploadAudioClip+GetAvatarFacePose 逐帧范式、本地/NVCF 双部署、LatencyTesterClient 线程压测 | 2389 |
| [04-交互app与压测.md](explain/04-交互app与压测.md) | a2f_3d.py 主力脚本（health_check/run_inference/tls-mtls）+ nim_performance_test 多进程压测与 stdout 时间戳解析 | 2547 |
| [05-配置族.md](explain/05-配置族.md) | 三角色×双族（diffusion 仅差两键）、camelCase/snake_case 两套方言、双拷贝与符号链接消费链 | 2595 |
| [06-容器编排与迁移.md](explain/06-容器编排与迁移.md) | quick-start 双 compose（init→service 接力、sed 开遥测、jaeger+prometheus）+ v1.0→v1.2 dataclass 迁移链 | 2638 |

字数口径：不计空格字符（Gymnasium 轮钉版）；explain 上限按 DeepChat 轮先例随行号锚密度放宽至 ~2600。

## 源码级勘误清单（10 条，均经 commit a2d0150 逐行核实）

1. **`proto/files_to_compile.yaml` animation_data 重复条目**：`nvidia_ace.animation_data.v1.proto` 在清单出现两次（L24 与 L33），16 条仅 15 唯一；且 `nvidia_ace.services.animation_data.v1.proto` 文件存在却不在清单——预编译 wheel（50 条目）同样不含 `services/animation_data` 模块，两处缺漏互相印证。重复条目 protoc 幂等无实害，真正后果是该服务模块生不出来。
2. **压测输出目录笔误**：`nim_performance_test.py` 的 create_parser docstring 写 "Outputs NIM performance in a csv file in output/ folder"（L127），实际 `OUTPUT_FOLDER='performance_output'`（L37）；README 倒是写的 performance_output——以代码为准。
3. **`get_filed_name` 拼写笔误**：`StatsHolder.get_filed_name`（nim_performance_test.py:223）应为 `get_field_name`；内部调用一致所以能跑，外部按正确名调用会 AttributeError。
4. **config yml 逐字节双拷贝**：`config_{claire,james,mark}.yml` 在 `scripts/audio2face_3d_api_client/config/` 与 `scripts/audio2face_3d_microservices_interaction_app/config/` 各存一份，md5 三对全等（6bc7e102/55adb663/84a14965）——改一处不改另一处的漂移风险源。
5. **两处"符号链接"真身不同**：`quick-start/configs` 是真符号链接（git mode 120000 → `../configs`）；`migration/deployment_configuration_files_from_v1.0_to_v1.2/default_configs_v1_2` 是**普通文本文件**（git mode 100644，仅 13 字节内容 `../../configs`）——迁移脚本 `convert_configuration_files.py:170-172` 拿它当目录 join 读会直接失败，须先手工 `ln -sfn ../../configs default_configs_v1_2` 还原。两者目标同为根 configs/。
6. **压测矩阵硬编码**：`nim_performance_test.py:350-355` 写死 6 个 Claire_sadness 变体（16khz/44.1khz × 5/10/20s），且 `run_single_client` 命令串写死 `config/config_mark.yml`（L140）与 `../../example_audio/` 相对路径——换音频/配置/目录必改源码。
7. **Riva 遗留与端口自相矛盾**：`api_client auth.py` 的 Auth docstring 自称 "a Riva URI" 且写默认 `localhost:50051`（L57），实际默认参数 `localhost:50052`（L46）；本仓真实服务端口是 `deployment_config.yaml:50` 的 0.0.0.0:52000——三个口径互不相同，别照抄 docstring。
8. **emotion_key_frames 休眠 KeyError**：`read_from_stream` 初始化只含 `input`/`a2f_smoothed_output` 两键（api_client service.py:101-104；interaction a2f_3d.py:135-138），而 `parse_emotion_data` 会写 `emotion_key_frames["a2e_output"]`（service.py:76 / a2f_3d.py:100）——服务端 EmotionAggregate 一旦真回 a2e_output 条目即 KeyError；且 a2e_output 一路本就无 CSV 落盘通道（两份拷贝共有）。
9. **四代版本号并存**：根 README NGC 目录表已列 2.0.0，quick-start 两 compose 镜像仍是 `audio2face-3d:1.3`（docker-compose.yml:18/:37），proto wheel 是 `nvidia_ace-1.2.0`，proto/README.md:18 明言 "NIM v1.3 continues to use v1.2.0"——样例整体锚定 1.3 代，读 2.0 文档时须对表。
10. **拼写/笔误杂项**：`common.py:301` "Receivedd RPC error"（双 d）、`common.py:532/557` `blenshape_names`、early_access README 实录 "Saved lantecy data"；`nvidia_ace.services.a2x_export_config.v1.proto:43` 尾注包名写成 `a2f_export_config`（a2f≠a2x，footer 注释笔误）。

## 图谱分层速查（10 层）

L01 文档门面 · L02 early_access 授权示例 · L03 API 客户端 · L04 微服务交互 app · L05 proto 契约 · L06 风格化配置 · L07 v1.0→v1.2 迁移工具 · L08 部署编排 · L09 配置抓取辅助 · L10 示例音频资产。15 步 tour 主线：proto 主文件→全契约面→生成链→api_client→authoring→交互 app→压测矩阵→音频库→配置双族→配置消费→迁移→容器编排→配置抓取→端到端数据流（wav→gRPC 双向流→FaceParameters 流回）。

---
生成：2026-11-06 · 图谱代 @a2d0150 · 行号锚全量从源码核实（含 1308 中断后盘上产物零损失续跑）
