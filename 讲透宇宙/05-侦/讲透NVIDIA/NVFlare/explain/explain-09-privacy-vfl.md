# explain-09 · 隐私计算与纵向联邦

## 一、角色定位

本篇覆盖 NVFlare 的三条隐私技术线与纵向联邦（VFL）底座：PSI（样本求交）、HE（同态加密聚合）、DP（差分隐私 filter），以及 `nvflare/collab/` 协作 API 与 xgboost 纵向实现。分工：**PSI 解决"样本对齐不泄露集合"、HE 解决"聚合密文不见明文权重"、DP 解决"输出统计不泄露个体"**——三者正交可叠加。与横向 FL（数据独立同分布、交换模型）不同，纵向 FL 是**特征分布在多方、样本需先对齐**：cifar10-splitnn 里 image site 拿特征、label site 拿标签（`examples/advanced/vertical_federated_learning/cifar10-splitnn/job.py:75`），训练时两方交换中间激活而非权重。

先钉勘误：任务书指向的 `nvflare/app_common/homomorphic_encryption/` 整目录是**弃用垫片**——每个文件只发 FutureWarning 再从 `nvflare.app_opt.he` 重导出（`nvflare/app_common/homomorphic_encryption/homomorphic_encrypt.py:17-24`），真实现全在 `nvflare/app_opt/he/`。同理 `nvflare/collab/` 没有 sender/receiver 文件，真实结构是 `api/` + `runtime/` 两层（运行时挂点 `nvflare/collab/runtime/executor.py:39` CollabExecutor）。

## 二、内部结构

**PSI**：三层装配。`PSIController` 只做编排，control_flow 依次调 workflow 的 pre_process/run/post_process（`nvflare/app_common/psi/psi_controller.py:29`）；协议本体在 `dh_psi/dh_psi_workflow.py` 的 DhPSIWorkFlow（`:34`），基于 DH 风格双钥交换：pre_process 收集各 site 集合大小并排序（`:53-63`），forward_pass 沿有序站点链两两传递加密集合（`:148-244`），backward_pass 把交集回传各方（`:283`），bloom filter fpr 低至 1e-11（`:35`）。client 侧 `psi_spec.py:23` 的 ABC 只要求 `load_items()`（`:46`）。用户视角极简：`LocalPSI` 读 CSV（`examples/advanced/psi/user_email_match/job.py:65`），`DhPSIRecipe` 三行成 job（`job.py:67-72`）。

**HE**：TenSEAL CKKS 实现。`homomorphic_encrypt.py:15` 导入 tenseal，context 从 client workspace 加载（`nvflare/app_opt/he/homomorphic_encrypt.py:22`）。加密侧 `HEModelEncryptor` 是 DXOFilter（`model_encryptor.py:33`），START_RUN 加载 context、未指定 encrypt_layers 时加密全部层（`:96-103`），加密前先把聚合权重乘上去（`:130-134`）——服务端对密文做加法即完成加权平均。聚合侧 `HEInTimeAccumulateWeightedAggregator` 直接 `isinstance(v, ts.CKKSVector)` 判密文层（`intime_accumulate_model_aggregator.py:53-67`）；`CKKSVectorDecomposer`（`decomposers.py:23`）注册进 fobs 使密文可序列化。解密侧 `HEModelDecryptor` 持私钥（`model_decryptor.py:35`）。sag_pt_he 模板 encryptor/decryptor 成对出现（`job_templates/sag_pt_he/config_fed_client.conf:31`）。

**DP filters**：`nvflare/app_common/filters/` 三件。`PercentilePrivacy` 按 percentile 裁剪+gamma 噪声（`percentile_privacy.py:25-26`）；`svt_privacy.py` 实现稀疏向量定理，显式管理 privacy budget（`:27-29`），epsilon 按 SVT 标准切分（`:89-91`）；`StatisticsPrivacyFilter` 是联邦统计结果清洗器（`statistics_privacy_filter.py:26`）。

**XGBoost 纵向**：三代并存。`histogram_based/controller.py` 的 XGBFedController 在 server 拉起 gRPC server、管理证书（`:33`、`:65`），直通 XGBoost 原生 federated 学习；v2 版（`histogram_based_v2/fed_controller.py:26` + `fed_executor.py:24`）重构为 adaptor 架构，模板 `vertical_xgb/config_fed_server.conf` 配 `data_split_mode = 1` 与 `secure_training`（`:8-12`）——置 true 即走 HE 加密直方图，正是 `examples/advanced/xgboost/fedxgb_secure/job_vertical.py` 的主题（docstring `:15`、`--secure` 开关 `:63-65`）。tree_based 是另一路线：`FedXGBTreeExecutor` 本地 boost + bagging/cyclic 聚合（`tree_based/executor.py:56`、`:224`）。数据侧 `XGBDataLoader` ABC（`data_loader.py:22`），`data_split_mode` 区分横/纵（`:58`）。

**collab 纵向底座**：Python 原生 RPC 风格。`@collab.publish` 暴露 client 方法（`nvflare/collab/api/decorators.py:60`）、`@collab.main` 标记 server 主循环（`:108`）；`App` 在 setup 拿到 workspace 与 server/clients 代理（`nvflare/collab/api/app.py:126`），`Facade` 提供 `collab.server/clients` 拓扑访问（`nvflare/collab/api/facade.py:99`）。hello-collab 里 server 主循环一行 `collab.clients.train(global_weights)` 即广播并收集全部返回（`examples/hello-world/hello-collab/job.py:106`）；splitnn 演示 per-site 配置注入——`set_per_site_config` 各发各的（`cifar10-splitnn/job.py:75-78`），`add_client_file` 打包依赖（`:85`）。

## 三、外部连接

对照系：横向 FL 的模型交换走 `PTFileModelPersistor`（`nvflare/app_opt/pt/file_model_persistor.py:39`）——server 端 load_model/save_model 落盘全局模型（`:229`、`:361`）。纵向线的 collab 不传模型传**函数调用与张量**：SplitNN 两段前向里 image site 把底层激活发给 label site、反向梯度再发回来——通信内容是中间表示而非权重，这正是"纵向"的架构含义。confidential_computing 补上机密计算证明层（TDX/SNP/SEV-CVM/GPU attestation authorizer，`nvflare/app_opt/confidential_computing/`），把"运行环境可信"补进"数据加密"之外。

## 四、数据流

以纵向 XGB 全流程为例：①各方本地 CSV；②PSI job 先行——DhPSIRecipe 跑出各 site 的 intersection.txt（`examples/advanced/xgboost/fedxgb/job_vertical.py:59-62`）；③训练 job 读交集对齐特征分片，XGBFedController 协调基于（可选加密）直方图聚合建树；④模型与指标落盘。横向对照流：persistor 出全局模型 → 广播 → 本地训练 → 权重回传 → 加权平均。差异本质是**交换单位**：横向换"完整模型状态"，纵向换"对齐索引 + 中间张量"。

## 五、设计决策

1. **三种隐私技术正交叠加而非互斥**：PSI 管输入对齐、HE 管传输聚合、DP 管输出发布，vertical_xgb 模板可同时开 PSI+HE。这是对"隐私"的工程化拆解——不是一个开关而是可组合的威胁模型。
2. **HE 的服务端零密钥设计**：加密在 client、聚合在密文域做加法、解密持私钥——服务端全程不见明文权重；代价是 CKKS 精度损失与序列化开销，大模型常只加密敏感层（encrypt_layers 支持正则筛选，`model_encryptor.py:110-116`）。
3. **collab 是"RPC 化 VFL"的赌注**：装饰器+Proxy 把联邦编程降到"写普通 Python"（hello-collab 全程无 FL 概念），代价是与 Controller/Executor 生态并存的第三种编程模型，控制粒度变粗。
4. **弃用垫片的双刃**：app_common 的 HE 垫片保住兼容，但 grep "homomorphic" 双倍命中，新人极易读错文件。
5. **批判点**：DhPSIWorkFlow 的链式协议多 site 轮次 O(n)（`dh_psi_workflow.py:148-244`），链上任一 site 掉线整链失败，容错弱于横向的广播-收集。

## 六、新人提示

- 学习顺序：hello-collab（collab 直觉）→ psi/user_email_match（PSI 三行用法）→ fedxgb/job_vertical.py（PSI+纵向 XGB）→ fedxgb_secure（叠加 HE）→ v2 源码。
- 写 HE 作业时 context 文件必须预先 provision 到各 client workspace（`homomorphic_encrypt.py:22`）——漏分发报加载错误而非缺文件。
- 纵向作业先问三问：特征怎么分片（data_split_mode）、样本怎么对齐（PSI 输出路径）、标签在哪方（label_site）——答案定下 job 骨架。
- app_common/homomorphic_encryption 别再引用，直接用 app_opt/he；旧/新 persistor 并存时以模板实际引用为准。
- DP filter 是 task_result_filters 配置项而非算法参数——挂在数据流管道上，与训练代码解耦。
