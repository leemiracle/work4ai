# 09 · 六 Helm chart 变体——容量 × UI 的正交矩阵

> 源：`workflows/tokkio/5.0.0-ga/llm-rag/` 下 `tokkio-{1,3,6}stream-{no,with}-ui` 六目录，每目录五件：Chart.yaml / values.yaml / tokkio-app.yaml / tokkio-app-params.yaml / config/ace-controller/config.yaml

## 一、角色定位

llm-rag 目录是 Tokkio 5.0.0-GA 的**部署产物区**：六个自包含 chart 目录 = 3 档并发容量（1/3/6 路 avatar 流）× 2 档前端形态（有无 Tokkio UI）的正交组合。它不是"一个 chart 加参数"，而是六份可直接 `helm install` 的成品——每个目录连 SSL 证书（config/ssl/crt.pem+key.pem）都自带。层次上是**Helm 伞 chart 包着一个 UCF 应用**：Chart.yaml 管 Kubernetes 依赖编排，tokkio-app.yaml（specVersion 2.5.0，UCF Composer 格式）管微服务拓扑，tokkio-app-params.yaml 给 UCF 服务喂参数。

## 二、内部结构

### 2.1 三层文件的分工与相似度（md5 实证）

- **Chart.yaml**：六份 md5 完全相同（159b55b2…）。name tokkio / version 5.0.0-GA；六个依赖：本地 `file://tokkio-app-5.0.0-GA`、tokkio-ui 6.6.17（**condition: tokkio-ui.enabled**）、riva-api 2.19.1（condition）、audio2face-3d 1.3.16（condition）、redis-timeseries 0.0.23、tokkio-ingress 0.0.9——除前两者外全部来自 helm.ngc.nvidia.com。
- **values.yaml**（421 行）：六份**只差两行**——`:370` 的 `tokkio-ui.enabled: false/true` 与 `:402` 的 `MAX_NUM_SESSION: 1/3/6`（diff 实证：1s-no vs 1s-ui 仅 370 行，1s-no vs 3s-no 仅 402 行）。内容四大块：riva-api（RMIR 模型 `rmir_asr_parakeet_1-1b_en_us_str_silero:2.19.0.1`，values.yaml:13）、audio2face-3d 的 stylization（james_v2.3 模型 + 数百行 blendshape 乘子/对称表，values.yaml:22-346）、tokkio-ui 的 uiConfig 开关面板（values.yaml:347-370）、tokkio-ingress（NodePort 30888/30443/30801 与 egress 三址，values.yaml:371-405）。
- **tokkio-app.yaml**（124 行）：只差 `:124` 的 label `ui-off/tokkio-app` vs `ui-on/tokkio-app`；label 四元组 `{apps/base, 1|3|6-stream, tracing-on, ui-on/off}`（tokkio-app.yaml:120-123）。secrets 四把 K8s key（NGC/NVIDIA/OpenAI/ElevenLabs，:6-22），dependencies 八个 ucf.svc（:23-31），components 十一个（a2f 端点/ace-configurator/ace-controller/三 SDR envoy/animation-graph/renderer/riva/redis 端点/unreal-renderer/vms，:32-100），**connections 17 条显式接线**（:101-119）——ace-controller→{redis, riva, animgraph-http/grpc, a2f-grpc}、三个 SDR envoy 各自的 redis/vms 归属、unreal-renderer→animgraph gRPC 等。
- **tokkio-app-params.yaml**（no-ui 258 行 / with-ui 263 行）：差异最富的一层。**流数轴**（1s→3s→6s）：ace-controller replicas 1→3→6（`:4`）、animationServer maxStreamCapacity 1→3→6（`:17`）、nvidiaVisibleDevices 1→[1]→[1,2,3]（`:19`）、vms 的 webrtc 连接 3/8→10/10→20/20（`:72-73`）、**vms 的 gpuDisableAlloc/gpuAllocLimit 仅 3 流起出现**（3s: 206-207，gpuAllocLimit 1；6s: gpuAllocLimit 2）、ue-renderer replicas 与 ucfVisibleGpus、三个 SDR 的 sdrMaxReplicas 同步扩。**UI 轴**：with-ui 版尾部多五行——`tokkio-ui: tokkio-ui-config: refresh_policy: type: Restart / config_type: Cm`（1s-with-ui 的 tokkio-app-params.yaml:259-263），把 UI 纳入 ace-configurator 的配置分发。另外 ace-configurator 段（`:224-258`）声明各服务配置的刷新策略：**唯 ace-controller 的 app-storage-volume 是 HotReload+Pv**（:229-234），其余全 Restart+Cm。

## 三、外部连接

**上游**：helm install 消费（one-click 脚本群 scripts/one-click/ 五平台与其对接）；config/ace-controller/config.yaml 就是 10 篇的七份同源体之六。**下游**：Chart.yaml 条件依赖在 install 时按 values 的 enabled 决定拉不拉 tokkio-ui/riva-api/a2f 子 chart；tokkio-app.yaml 的 `file://tokkio-app-5.0.0-GA` 指向一个**不在本仓的本地子 chart 目录**（部署前需另获取）；UCF 服务镜像全走 nvcr.io 与 ngc-docker-reg-secret；unreal 资产 `nvidia/ace/unreal-renderer-aki-asset:0.1.1`（tokkio-app-params.yaml:201）经 ngc-resource-downloader 拉取。

## 四、数据流

部署时：helm 读 Chart.yaml 装依赖 → values.yaml 喂伞 chart 参数（enabled 门控 + ingress 容量）→ tokkio-app.yaml+params 经 UCF 编排生成 K8s 资源（deployment/service/configmap/PV）→ ace-configurator 按 params 的 refresh_policy 把各配置（含 91 行 config.yaml）分发到 PV/CM。运行时容量链：浏览器→tokkio-ingress（`:402` MAX_NUM_SESSION 限会话数）→ace-controller-sdr-envoy 调度→ace-controller（replicas N）各持一路流→vms webrtc（in/out 连接上限）→animation-graph（maxStreamCapacity）→unreal-renderer（replicas/ucfVisibleGpus）渲染→流回浏览器。

## 五、设计决策

1. **目录复制而非 values 参数化**：两轴六态全部预编译成目录——牺牲 DRY 换部署期不可变（NGC 分发、企业内网无源可寻场景友好），代价是改公共段要同步六处（Chart/config 已靠逐字节复制保持同步）。
2. **enabled 条件依赖 + label 双重标识 UI 态**：values:370 管子 chart 装不装，app.yaml:124 label 管 UCF 侧识别——同一状态在两层各写一遍。
3. **容量三旋钮同调**：ingress 会话门（values:402）、ace-controller 副本（params:4）、animation-graph 流容量（params:17）必须一致，只改其一会造成排队或空转；GPU 侧 riva 恒占 GPU0（values:5）、animation-graph 恒 GPU1（params:19）、renderer 3 流起才配额（params:206-207）——单 GPU 机器跑不了多流变体。
4. **ace-controller 配置独享 HotReload**：改人格/换 LLM 不重启容器（Restart 会让在途会话全断），而 UI/动画图配置允许重启生效——按"改动频率×中断代价"分级。

## 六、新人提示

- 判断手头 chart 是哪态：`grep MAX_NUM_SESSION values.yaml`（1/3/6）+ `grep 'enabled:' values.yaml` 第 370 行（UI），比读目录名更可靠。
- 六份 Chart.yaml/config.yaml 是逐字节同步的（md5 159b55b2…/7fcbe9f2…），改任何一份必须六处同改或改完重新分发。
- with-ui 变体不止多装 UI：params 尾部的 configurator 分发段也是 UI 轴差异，漏掉它 UI 配置不会热更新。
- 3stream 起 vms 才声明 GPU 配额（gpuDisableAlloc/gpuAllocLimit），1stream 靠默认调度——GPU 资源不足的集群优先查这组键。
- `file://tokkio-app-5.0.0-GA` 子 chart 不在仓内，helm dependency build 前需备齐，否则 install 直接失败。

## 甄别记录

任务书称 "差异全在 tokkio-app-params.yaml 与 values.yaml :370/:402 两行"；源码实证细化为：**values.yaml 差异确实仅 :370/:402 两行**（全配对 diff 验证），但**tokkio-app.yaml 也有一行差异**（:124 label ui-on/off）——差异文件是三份而非两份；params 的流数差异集中在 :4/:17/:19/:72-73/:205-210 五簇。
