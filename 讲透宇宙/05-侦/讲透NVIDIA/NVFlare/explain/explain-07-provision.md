# explain-07 · Provision 与部署启动链

## 一、角色定位

本篇覆盖 NVFlare 从"一份 project.yml 声明"到"可启动的联邦系统"的全链路：`nvflare/lighter/` 供给器（provision）、POC 一键模式、simulator 模拟器与 `nvflare/tool/deploy/` 的 docker/k8s/slurm 部署。定位一句话：**运行时（private/fed）管"怎么跑"，lighter 管"跑之前把每个站点的启动包造出来"**——证书、配置、启动脚本、目录布局都在 provision 阶段静态生成，运行时零配置猜测。

三种模式的关系常被新人混淆：simulator 是单进程开发回路（不产 startup kit）；POC 是本机多进程彩排（用 mode="poc" 复用同一套 Provisioner）；production 是跨机分布式。**同一个 provision 核心，三种打包强度**。

先钉勘误：`nvflare/lighter/poc.py` 已是 deprecated 占位符——只打印"please use 'nvflare poc' instead"（`nvflare/lighter/poc.py:17-23`），真 POC 实现在 `nvflare/tool/poc/poc_commands.py`；builder 动态装载也不在 provision.py 本体，而在 `nvflare/lighter/prov_utils.py:33` prepare_builders。

## 二、内部结构

**CLI 层**（`nvflare/lighter/provision.py`）：`handle_provision`（`:231`）解析四种入口——`-g` 生成样例 project.yml（dummy_project.yml，`:264` 一带，pre-2.7.0 默认行为保留）、`--gen_edge` 生成 edge 工程模板（`:257`）、`-p` 指定真实工程、无参时同 `-g`。校验 project 文件存在性后进 `provision()`（`:414`）：edge 参数走 `provision_for_edge`（`:401`）分支，常规路径依次 `prepare_project`（`:441`，把 dict 变 entity 对象树）→ `prepare_builders`/`prepare_packager`（`prov_utils.py:33`/`:58`，按 project_dict 配置动态 import builder 类）→ 构造 `Provisioner` 并调 `provision()`。

**核心引擎**（`nvflare/lighter/provisioner.py`）：`Provisioner`（`:25`）持有 builders 列表与可选 packager。`provision()`（`:77`）= `_build()`（`:97`）+ `package()`：_build 先校验 server 缺失即抛错（`:110` 一带 `project.get_server()`），再为 workspace 建根目录，然后**顺序执行每个 builder 的 build()**——builder 顺序就是依赖顺序（先签证书后渲染引用证书的启动脚本）。`add_template`（`:65`）支持合并自定义模板键。

**契约层**（`nvflare/lighter/spec.py`）：`Builder` ABC（`:21`）只要求一个 `build(project, ctx)`（`:48`）；`Packager` ABC（`:67`）负责把产物目录打成 tar。`ProvisionContext` 在 builder 间传值（如 CURRENT_PROD_DIR 指向产物目录）。

**Builder 家族**（`nvflare/lighter/impl/`）：`cert.py:110` CertBuilder 是安全根基——为 server/client/admin 签发证书链（内部状态机 `_CertState` `:45`）；`template.py:18` TemplateBuilder 用 `templates/master_template.yml`（另有 aws/azure/edge 变体，`nvflare/lighter/templates/`）渲染各端 start/stop 脚本与 fed_server.json/fed_client.json；`workspace.py:23` WorkspaceBuilder 造目录骨架；`static_file.py:39` StaticFileBuilder 拷贝静态资源；`docker.py:25` DockerBuilder 与 aws/azure 是环境适配 builder；`he.py:23` HEBuilder 分发同态加密 context；`signature.py` 签名产出。

**实体模型**（`nvflare/lighter/entity.py`）：`Project`（`:394`）聚合 `Participant`（`:240`，server/client/admin 三种角色）与参与方间的连接拓扑——`ListeningHost`（`:24`）声明服务端监听地址、`ConnectTo`（`:43`）声明客户端/管理端要连谁，这是证书 SAN 与防火墙开洞的依据。

**部署层**（`nvflare/tool/deploy/`）：`deploy_cli.py:50` def_deploy_cli_parser 注册 docker/k8s/slurm 子命令、`:155` handle_deploy_cmd 分发；docker 路径的 `docker_deploy.py:94` prepare 改造 startup kit 为容器形态；k8s 的 `k8s_deploy.py:131` prepare 同构，配 `templates/helm/{server,client}/` 的 deployment/service/role/serviceaccount 模板。

## 三、外部连接

- **运行时**：startup kit 的 fed_server.json/fed_client.json 直接喂给 `nvflare/private/fed/server/fed_server.py:205` BaseServer.deploy 与 ClientEngine——provision 的输出就是运行时的输入。
- **POC**：`nvflare/tool/poc/poc_commands.py:1299` prepare_poc 与 `:1510` prepare_poc_provision 以 mode="poc" 调 Provisioner（`WORKSPACE_KEY` `:86`；`get_stop_cmd` `:187` 生成停止脚本；`setup_service_config` `:1947`）——证明 POC 与 production 共用同一供给内核。
- **simulator**：`nvflare/private/fed/app/simulator/simulator.py:50` run_simulator 构造 `SimulatorRunner`（类定义 `nvflare/private/fed/app/simulator/simulator_runner.py:84`，n_clients/threads/gpu 参数直传），完全绕过 provision——开发回路最短。
- **Dashboard**：面板的"生成 startup kit"功能也是 provision 的 GUI 前端（见 explain-03）。
- **edge 线**：`provision_for_edge`（`provision.py:401`）对接 edge 工程模板，与 `nvflare/edge/` 子系统的 web 服务器配套。

## 四、数据流

production 全流程：①写 project.yml（声明 server/client/admin 参与方、监听与连接拓扑、builders 配置）；②`nvflare provision -p project.yml -w workspace`；③prepare_project 转 entity 树 → prepare_builders 动态装载 → CertBuilder 签证书 → template builder 渲染脚本与 fed_*.json → static_file/docker/云 builder 补环境 → Packager 打包；④workspace 下产出 `prod_*/<site>/startup` 包，分发到各站点；⑤各站点跑 start.sh 拉起 fed_server/fed_client，admin 端拿 admin.crt 连 server。POC 流程是它的单机特例：mode="poc" 下模板简化、全部站点落在本机 workspace、再由 `nvflare poc start/stop` 编排进程。

## 五、设计决策

1. **静态供给而非动态协商**：证书/地址/脚本全部预生成，运行时不需要也不会再协商信任关系——这是联邦多机构环境的工程前提（跨机构 PKI 协商不现实），代价是改拓扑必须重新 provision。
2. **Builder 流水线=可扩展点**：新增部署形态（如内部云）只需实现 `spec.py:21` 的 Builder ABC 并写进 project.yml 的 builders 数组，零核心改动；动态 import（prov_utils.py:33）让自定义 builder 可从工程目录装载（handle_provision `:240` 一带把 custom_folder 加进 sys.path）。
3. **POC 复用 production 内核**：mode 参数（provisioner.py:77 docstring 明示 "poc" or "normal"）而非分叉实现——POC 验证过的配置语义与生产一致，降低"POC 能跑生产跑不了"的迁移风险。
4. **三端对称打包**：server/client/admin 都是 Participant，接受同样的 builder 处理——admin 也有证书与 startup kit，管理面与数据面同等级安全。
5. **批判点**：project.yml 的 builders 数组是字符串路径动态 import，类名拼错要到 provision 中途才炸；模板 yml 与代码版本强耦合（升级后旧 kit 的模板引用可能失效）。

## 六、新人提示

- 入口顺序：先 `-g` 生成样例读懂 project.yml 字段，再改参与方名字/人数 provision 一遍，对比 workspace 前后差异——比读文档快。
- 排错三查：证书过期/不匹配（CertBuilder 重跑）、连接拓扑写反（ListeningHost 是 server 视角）、workspace 残留旧产物（删 prod_* 重来）。
- helm/k8s 部署先读 `templates/helm/server/deployment.yaml` 的环境变量注入方式，再对照 `k8s_deploy.py:131` prepare 的改包逻辑。
- simulator 起不来先查 clients 数与 GPU 分配参数（simulator.py:50 的 n_clients/gpu/threads），与 provision 无关——别在 lighter 里找 simulator 的锅。
