# 讲透 NVIDIA/Cloud-Trust-Scripts

> NVIDIA Cloud Trust Scripts：9 个 POSIX sh 脚本的 IAM 自动化集——客户在自家 GCP 项目/Azure 订阅跑 `cloudtrust.sh`，创建 NVIDIA 命名服务身份并授予最小必要权限，打通 NGC 数据集服务 / Omniverse / Unified Cluster Lifecycle 三服务的云信任接入。本地仓 `/usr-data/data2/repos/agent-repos/NVIDIA/Cloud-Trust-Scripts` @ 4f32e7c3。
> 本目录=understand 全链知识库产物（2026-11-07，微仓一体通道；README+ONBOARDING 合并口径）。

## 全链状态表

| 阶段 | 状态 | 关键数据 |
|---|---|---|
| prepare | ✅ 2026-11-07 | 19 文件（9 cloudtrust.sh + 9 README 含根 + license.pdf）/ 1 批单批 |
| 批分析 | ✅ | NOTES-DIGEST 收割 9 条甄别笔记；9 脚本全量 pairwise diff 复核 |
| merge+layers/tour | ✅ | 25n/24e/2 层（云信任脚本层 / 文档与根资产层）/4 步 tour |
| finalize | ✅ | validator 0 issues；fingerprints 19 文件@4f32e7c3 |
| ONBOARDING | ✅ | `onboarding/ONBOARDING.md` 6 节 / ~3.6K 不计空格字符 / 40+ 锚（全部源码核实） |

图谱：仓内 `.understand-anything/knowledge-graph.json`（25n/24e/2 层/4 步 tour）。

## 勘误清单（源码级实证，graph 笔记/文档 vs 源码以源码为准）

1. **storage.admin 在 NGC dataset service，不在 UCL**（重磅）：批阶段笔记与任务口径均称"UCL 授予 storage.admin 全管权限"——源码实证相反：`gcp/ngc_dataset_service/prod/cloudtrust.sh:57` 是 `roles/storage.admin`；`gcp/unified_cluster_lifecycle/prod/cloudtrust.sh:57` 与 omniverse（`gcp/omniverse/prod/cloudtrust.sh:54`）同为 `roles/storage.objectViewer` 只读。语义自洽：NGC 要写数据集进客户桶所以全管，Omniverse/UCL 只读。Azure 侧同构：ngc 的自定义角色 Actions 是 `Microsoft.Storage/*/write`（`azure/ngc_dataset_service/cloudtrust.sh:26`），omniverse/UCL 是 `*/read`（`azure/omniverse/cloudtrust.sh:26`）。
2. **README 标题错位两处**：`gcp/ngc_dataset_service/prod/README.md` 标题写 "for Unified Cluster Lifecycle"、`azure/ngc_dataset_service/README.md` 标题写 "for Omniverse"——复制上家 README 忘改标题，与目录服务名不符。
3. **权限宣告与授予面不符**：8 个服务 README 的 Prerequisite 一律写 "Read/Write Storage"，但 omniverse/UCL 实际只授予 objectViewer 只读——审计以脚本为准，README 措辞照抄了 NGC 版。
4. **stg 手改漂移**：ngc/ucl 的 stg 版 `L8` 版权注释把 "reproduction" 拼成 "redevuction"（prod 版正确）；ngc prod 文件尾无换行符——stg 是手工复制改域名的旁证。
5. **变量化改造不彻底**：ngc/ucl GCP 脚本 `L38-39` 已改 `PROJECT_ID=$1` 变量风格，但 `L55` 行尾仍残留 `--project $1` 位置参数直传——同函数内两种风格混用。
6. **license 链接拼写 "licese"**：所有 9 个脚本 `L12` 的许可链接笔误（应为 license），贯穿全仓的复制系错误。
7. **clientSecret 明文回显**：`azure/*/cloudtrust.sh:41` 将 ClientSecret 直接 echo 到终端/shell history——对接便利与凭据泄露面的取舍，文档未提示客户注意。

## 生成口径

- 字数口径：ONBOARDING「不计空格字符」；本 README 与 ONBOARDING 为合并口径（微仓 <20 代码文件，不另出 explain 系列）。
- 行号锚全部从源码核实（2026-11-07，@4f32e7c3）；锚为仓库相对路径，GCP prod/stg 同构行号通用（差异仅域名行，已在文中标注）。
- 深入路径：`onboarding/ONBOARDING.md` §2 GCP 五步命令链 → §3 三服务授予面对比表 → §4 Azure entitlement 模板 → §5 安全卫生发现。
