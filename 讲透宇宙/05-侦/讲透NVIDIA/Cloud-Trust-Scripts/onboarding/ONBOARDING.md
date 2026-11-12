# Cloud-Trust-Scripts ONBOARDING —— NVIDIA 云信任 IAM 自动化脚本集

> 仓：`NVIDIA/Cloud-Trust-Scripts` @ 4f32e7c3（本地 `/usr-data/data2/repos/agent-repos/NVIDIA/Cloud-Trust-Scripts`）。
> 图谱：仓内 `.understand-anything/knowledge-graph.json`（25n/24e/2 层/4 步 tour，validator 0 issues，fingerprints 19 文件）。
> 本文所有行号锚均从源码核实（2026-11-07）。

## 1. 项目定位：9 个脚本做同一件事

这是 NVIDIA 为**云上托管服务接入客户云账号**提供的 IAM 自动化脚本集：客户在自己的 GCP 项目 / Azure 订阅里跑一个 `cloudtrust.sh`，脚本创建一个 NVIDIA 命名的服务身份，把最小必要权限授予 NVIDIA 侧的信任服务账号，从而让 NVIDIA 云服务（NGC 数据集服务、Omniverse、Unified Cluster Lifecycle 集群生命周期）能在授权范围内操作客户资源。仓内共 9 个可执行脚本：

- **GCP 6 个**：`gcp/{omniverse,ngc_dataset_service,unified_cluster_lifecycle}/{prod,stg}/cloudtrust.sh`——三个服务 × 生产/预发信任域两份；
- **Azure 3 个**：`azure/{omniverse,ngc_dataset_service,unified_cluster_lifecycle}/cloudtrust.sh`——Azure 无 prod/stg 之分；
- 配套 8 个 README（每目录一个）+ 根 README + `license.pdf`（LicenseRef-NvidiaProprietary，脚本头 L3-12 均指向它）。

理解本仓只需抓住两条轴：**云平台轴**（GCP 用 gcloud+服务账号，Azure 用 az+自定义角色/SP）与**服务轴**（三服务需要的存储权限不同：NGC 要写、Omniverse/UCL 只读）。

## 2. GCP 六脚本：一个模板的两种风格、一个域名差异

六个脚本 60-61 行，命令链五步完全一致（以 `gcp/omniverse/prod/cloudtrust.sh` 为例）：

1. **启用 API**：`gcloud services enable compute.googleapis.com` + `storage-component.googleapis.com`（`L42-43`）；
2. **项目级绑定**：把 NVIDIA 信任账号 `nvidia-cloud-trust@nv-cloudtrust-prod.iam.gserviceaccount.com` 绑定为 `roles/iam.serviceAccountTokenCreator`（`L46`）——这是"客户授权 NVIDIA"的信任锚点；
3. **创建客户侧 SA**：`gcloud iam service-accounts create $2 --display-name="Cloud Trust Access Service Account"`（`L49`）；
4. **SA 级绑定**：新 SA 上再给 NVIDIA 信任账号挂 tokenCreator（`L52`），使 NVIDIA 可代签该 SA 的短期 token；
5. **数据面授权**：项目级给新 SA 挂数据角色（`L54-55`）。

**prod vs stg 的全部差异**就是信任账号域名：`nv-cloudtrust-prod` vs `nv-cloudtrust-dev`，各出现两处（omniverse 在 `L46/L52`，ngc/ucl 在 `L49/L55`）——diff 实证别无差异（ngc/ucl stg 另有一处版权注释拼写漂移，见勘误）。stg 目录存在的原因：预发环境用独立的 NVIDIA 侧 dev 项目，客户要分别对两个域授权。

**两种参数风格**：omniverse 全程 `$1/$2` 位置参数直传（`L38-39` 的 echo 直接用 `$1`）；ngc_dataset_service 与 unified_cluster_lifecycle 先 `PROJECT_ID=$1; SERVICE_ACCOUNT_NAME=$2` 存变量再引用（两脚本 `L38-39`）——同一模板的两个演化代际，且后者变量化不彻底：`L55` 行尾仍残留 `--project $1` 直传。

**usage() 函数族**：六个脚本统一在 `L20-29` 定义 `usage()`（heredoc 打印 `Usage: $PROGNAME PROJECT_ID SERVICE_ACCOUNT_NAME`），`L32-36` 做 `$# -ne 2` 校验后调用——这套"PROGNAME=$(basename $0) → usage() → 参数计数"骨架是 POSIX sh 教科书式写法。语言栈判定依据：shebang `#! /bin/sh`（`L1`，注意 `#!` 后有空格）+ `set -e`（`L16`）+ 纯 POSIX 语法（无 bashism），全仓无 Python/Go，是纯 POSIX sh 仓。

## 3. GCP 授予面：三服务的权限差异（源码实证）

数据面角色是三服务的本质区别（也是本仓的安全核心）：

| 服务 | 存储角色 | 计算角色 | 行号锚 |
|---|---|---|---|
| omniverse | `roles/storage.objectViewer`（只读） | `roles/compute.instanceAdmin` | `gcp/omniverse/prod/cloudtrust.sh:54-55` |
| **ngc_dataset_service** | **`roles/storage.admin`（全管，含写）** | `roles/compute.instanceAdmin` | `gcp/ngc_dataset_service/prod/cloudtrust.sh:57-58` |
| unified_cluster_lifecycle | `roles/storage.objectViewer`（只读） | `roles/compute.instanceAdmin` | `gcp/unified_cluster_lifecycle/prod/cloudtrust.sh:57-58` |

**授予面最强的是 NGC dataset service 而非 UCL**——NGC 要把数据集**写入**客户存储桶所以拿 `storage.admin`；Omniverse/UCL 只读。语义自洽，但批阶段笔记与常见转述常把 storage.admin 误记在 UCL 头上（见 README 勘误 1）。所有 GCP 服务还共同授予 `compute.instanceAdmin`（实例管理，用于 UCL 类集群操作，但三服务都给了）。

## 4. Azure 三脚本：entitlement 变量模板与五元组输出

Azure 侧是**同一 41 行模板的三份实例**，仅三处变量差异。以 `azure/omniverse/cloudtrust.sh` 为例：

- `entitlement="omniverse"` + `display_name="Omniverse"`（`L19-20`）——服务身份变量，ngc 版为 `"ngc_dataset_service"`/`"NGC DataSet Service"`、UCL 版为 `"UCL"`/`"Unified Cluster Lifecycle"`；
- **自定义角色**：`az role definition create` 建角色 `Role_for_NVIDIA_${entitlement}`（`L22-29`），Actions 差异是唯一实质权限差：omniverse/UCL=`Microsoft.Storage/*/read` + `Microsoft.Compute/*/read`（`L26`），**ngc=`Microsoft.Storage/*/write`**+`Microsoft.Compute/*/read`（ngc 版 `L26`）——与 GCP 侧"NGC 写、其余读"的模式严格对偶；
- **SP 创建**：`az ad sp create-for-rbac --name NV-Trust-Broker-${entitlement} --role ... --scopes /subscriptions/$subscriptionId --years 1`（`L32`，凭据一年期）；subscriptionId 从 `az account show` 取（`L18`）；
- **五元组回显**：`jq` 从 SP 输出提 `appId`/`password`（`L34-35`），`az ad app credential list` 查 `keyId`/`endDateTime`（`L36-37`），最后 echo SubscriptionId/TenantId/AppId/ClientSecret/ClientSecretId/Expiry（`L41`）——客户把这串凭据登记到 NVIDIA 云信任门户即完成对接（各 README 的 Verify 节均指向"登录 NVIDIA Cloud Trust Account 验证"）。

与 GCP 的结构对照：Azure **无 usage()、无参数校验、无 prod/stg 之分**（订阅即边界）；GCP 是"启用 API→建 SA→绑角色"三段式，Azure 是"建角色→建 SP→发凭据"三段式。Azure 侧需要额外依赖 `jq`（`L34-35`）。

## 5. 复制漂移与卫生问题（安全审计视角)

小仓也有真实的安全/卫生发现，全部源码实证：

1. **clientSecret 明文回显**：`azure/*/cloudtrust.sh:41` 把 ClientSecret 直接 echo 到终端与 shell history——对接流程图省事，但敏感凭据落终端日志的风险应在文档中提示客户；
2. **权限宣告与实际授予不符**：8 个 README 的 Prerequisite 一律写 "Read/Write Storage"（如 `gcp/omniverse/prod/README.md` Prerequisite 节），但 omniverse/UCL 实际只授予 objectViewer 只读（§3）——README 措辞照抄了 NGC 版本，审计时应以脚本为准；
3. **README 标题错位两处**：`gcp/ngc_dataset_service/prod/README.md` 标题是 "Setting up NVIDIA Cloud Trust for **Unified Cluster Lifecycle**"、`azure/ngc_dataset_service/README.md` 标题是 "...for **Omniverse**"——复制上家 README 忘改标题，内容与目录服务名不符；
4. **stg 手改痕迹**：ngc/ucl 的 stg 版版权注释 `L8` 把 "reproduction" 拼成 "redevuction"（prod 版正确）——stg 是手工复制的旁证；ngc prod 文件尾无换行符；
5. **license 链接拼写**：所有脚本 `L12` 的许可链接 "licese"（应为 license）——贯穿全仓的复制系笔误。

## 6. 新人上手路径

1. **按需求选脚本**：GCP 客户 → `gcp/<service>/<prod|stg>/cloudtrust.sh PROJECT_ID SA_NAME`（两位置参数，`L32` 校验恰好 2 个）；Azure 客户 → `azure/<service>/cloudtrust.sh`（零参数，但先 `az login` 到正确订阅，脚本用当前订阅 `L18`）。前提都是"有权限创建角色/SA 并绑定 IAM"。
2. **读懂一条信任链**：GCP 的 tokenCreator 双绑定（项目级 `L46` + SA 级 `L52`）= NVIDIA 可为客户 SA 签短期 token、以客户身份行事——理解这一点，三个数据角色就是这条代理链能做的事的边界。
3. **改动守则**：改任何脚本先想"这是模板的第几份实例"——9 个脚本实为 3 个模板，改 GCP 模板要同步 6 处（3 服务×prod/stg），域名 prod/dev、角色行、变量风格都是易漂移点；本仓既有的漂移（勘误 3/4）就是没同步的实例。
4. **验收**：跑完看输出——GCP 最后 echo 完整 SA 邮箱（omniverse `L58` / ngc·ucl `L61`），Azure echo 五元组（`L41`）；再按各 README Verify 节登录 NVIDIA 信任门户确认。
5. **图谱导览对应**：tour 4 步=全景→GCP 六脚本→Azure 三服务→授予面对比；两层的 L01 脚本层 9 节点 / L02 文档层，与本文 §2-§4 / §5 的展开顺序一致。

（完 · 锚 40+，字数口径=不计空格字符）
