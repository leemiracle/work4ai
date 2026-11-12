# 12 · 构建部署基础设施与 Agent 技能资产：cmake 链、docker 群、五张技能卡与 DeBERTa demo

> 图谱锚：L16「构建部署基础设施与演示/Agent 技能资产」（81 节点）· tour t16。源码：根 `CMakeLists.txt` + `cmake/modules/` + `docker/` + `.agents/skills/` + `demo/`。

## 一、角色定位

本域是"让这一切跑起来"的外圈：CMake 构建体系（编译整仓 + 生成第 8 篇 wheel 群）、docker 环境群、**仓根 `.agents/skills/` 五张 Agent 技能卡**（把专家工作流打包给 AI 助手的官方尝试）、两个 demo（DeBERTa 端到端、EfficientDet notebooks）。它回答：从裸机到 `import tensorrt`，每层谁负责什么。

## 二、内部结构

**CMake 链**：根 `CMakeLists.txt:28` 默认 `CMAKE_CUDA_ARCHITECTURES 75 80 86 89 90 100 120`（Turing 到 Blackwell 全谱），CMakeLists.txt:96-99 条件追加 SM 110（Thor，需 CUDA 13.0+）。产品形态互锁：CMakeLists.txt:53 `TRT_SAFETY_INFERENCE_ONLY` 与 CMakeLists.txt:56 `TRT_BUILD_PRODUCT` 经 CMakeLists.txt:110-116 的 FATAL_ERROR 校验构成安全构建硬约束。samples 带 GTest v1.14.0 FetchContent（CMakeLists.txt:345-352）。`cmake/modules/` 实测 **16 个模块**（批阶段笔记计 15）：Fetch 三件套（PyBind11/CCCL/nlohmann_json）、FindNCCL、Stubify、SymbolExports 等——`scripts/stubify.sh`（stubify.sh:60 以 `nm -D` 提取动态符号）配合 Stubify.cmake 实现"只发符号不发实现"的精简接口库（TRT 闭源核的接口层发布手法）。

**docker 群**：7 个 Dockerfile——rockylinux8/9、ubuntu-22.04/24.04/24.04-aarch64/26.04、cross-aarch64（交叉编译）。`build.sh:45` 以 `${arg_cudaversion:0:4}` 截取生成 CUDA_VERSION_MAJOR_MINOR 注入 build-arg；`downloadTRT.sh:5` **硬编码 TRT_VERSION="11.3.0.99"** 且 downloadTRT.sh:47 的 URL 模板里再写一遍——升级须同步双改（NOTES batch-31 钉版）。`launch.sh:19` 默认 tag `tensorrt-ubuntu24.04` 与 build.sh 默认镜像名不一致——连跑需手动 `--tag` 对齐。

**Agent 技能卡（重要甄别：实为五张非四张）**：`.agents/skills/` 实测 5 目录——重卡 `trt-perf-analysis`（图谱 82 节点：SKILL.md 定义"从 layers_*.json/profile_*.json 生成交互式 HTML 性能报告"；`scripts/package_report.py` 拉起 analyze/validate 两条子进程链，不经 import 体系；`trt_perf/data.py` 头部 ~150 行纯常量表 + validate_dag 用 Kahn 拓扑排序验 DAG；report_template/ 的 index.html 静态骨架 + app.js minified bundle + 18KB 压成 3 行的 styles.css——行数指标对 minified 资产严重失真）与 `trt-strong-typing-migration`（8 节点：migrate.py+verify.sh）；轻卡三张：trt-cpp-runtime-quickstart/trt-onnx-quickstart/trt-torch-quickstart（各单 SKILL.md）。技能卡位于**仓根**而非 tools/Polygraphy 之下。

**demo/DeBERTa**：`deberta_onnx_modify.py:76` `@gs.Graph.register()` 注册 `insert_disentangled_attention`（deberta_onnx_modify.py:77），deberta_onnx_modify.py:95 对全层扫描，deberta_onnx_modify.py:191-192 把 `Add+Gather+Gather+Transpose+Add+Div` 六节点子图（c2c/c2p/p2c 相对位置注意力的公共骨架）替换为单节点 `DisentangledAttention_TRT`（deberta_onnx_modify.py:23 点名插件名），deberta_onnx_modify.py:183 `gs.import_onnx` 进、deberta_onnx_modify.py:198 `gs.export_onnx` 出，deberta_onnx_modify.py:214-215 两次导出对应插件开/关双版本——第 10 篇图手术与 disentangledAttentionPlugin 的粘合剂。

## 三、外部连接

CMake 上游接 CUDA toolkit/nvcc 与 pybind11（Fetch）；docker 群消费 NVIDIA 官方基础镜像与 downloadTRT.sh 拉的 TensorRT-Enterprise tar.zst；技能卡消费 Polygraphy 生态的性能 dump 惯例（layers_/profile_ 命名即 trtexec/引擎序列化产物）；DeBERTa demo 依赖第 10 篇 gs + transformers 权重 + 本仓 disentangledAttentionPlugin 三方。

## 四、数据流

构建流：根 CMake 发现 CUDA → 产品形态门控组件 → cmake/modules 的 Fetch/Find 拉齐依赖 → plugin/parsers/python 三线各自出库（python 线走第 8 篇 wheel 流水线）→ Stubify/SymbolExports 产出接口层。部署流：build.sh 出镜像 → launch.sh 起容器（jupyter 可选端口映射）→ 容器内 pip 装轮子。性能诊断流（技能卡）：trtexec 导出 JSON 对 → agent 调 trt-perf-analysis → analyze_trt_perf.py 解析（data.py 常量表识别 MHA/模型名）→ validate_dag 拓扑校验 → report_template 渲染交互 HTML（netron srcdoc 嵌引擎结构）。

## 五、设计决策

1. **SM 谱系滚动 + 条件后置**：默认表只放已量产架构，Thor 因依赖 CUDA 13 后置追加——老 toolkit 构建不失败。
2. **产品形态互锁而非开关堆积**：safety 选项用 FATAL_ERROR 互锁，错误配置在 configure 期死掉而非产出带隐患的库。
3. **技能卡=专家工作流显性化**：SKILL.md（README 驱动）+ 校验脚本兜底 + 报告模板保观感三件套，是 AI 时代基建资产新形态（2025-2026 新增域，图谱为之立专层）。
4. **demo 选 DeBERTa 的深意**：disentangled attention 是"ONNX 表达不了、TRT 插件能救"的典型——同时示范图手术与插件开发两条线，是学习插件篇的最佳入口。
5. **docker 群不收敛为万能镜像**：7 Dockerfile 按发行版/架构分离，downloadTRT.sh 独立——TRT 版本与镜像版本解耦，各自滚动。

## 六、给新人的提示

构建从 `docker/build.sh` + ubuntu-24.04 起步最稳；注意 launch.sh 默认 tag 与 build.sh 默认名不一致。升级 TRT 记得 downloadTRT.sh 两处硬编码。性能优化先试 trt-perf-analysis 技能卡——比手工翻 JSON 快一个量级。跑 DeBERTa demo 按 README 三步：pytorch2onnx → onnx_modify（插件注入）→ tensorrt_inference，用 Netron 对照修改前后 ONNX 的六节点→单节点折叠最直观。改根 CMake 先 `cmake -LAH` 看全量开关——产品互锁会在意想不到的组合上报 FATAL_ERROR。
