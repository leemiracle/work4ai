# 讲透 Kumo-TS

> NVIDIA 开源时序分析库双子包：Kumo-Forecast（预训练 transformer backbone 预测，flan-t5 系底座）+ Kumo-Anomaly（diffusion 异常检测 TSDiffuser，DARR 模式）。前身名 NV-Tesseract。

## 全链状态表（2026-11-08）

| 阶段 | 状态 | 产出 |
|---|---|---|
| 批分析 | ✅ 9 批（13 文件，批 1/2/9 拆 part） | 447 节点 / 724 边（imports 42=scanner 35+手扫 7；批 9 scanner 零边系盲区坐实全靠手扫） |
| merge | ✅ 零丢失 | 无悬空边；tested-by linker 补 12 个 production 节点 tested 标签 |
| layers/tour | ✅ | 10 层（60 file 节点全覆盖）/ 12 步 |
| finalize | ✅ validator 0/0 | knowledge-graph.json（447n/724e） |
| fingerprints | ✅ | 60 files @ af74798b |
| onboarding | ✅ | ONBOARDING.md 4995 字 / 54 锚 |
| explain | ✅ 3 篇 | backbone（2363 字/27 锚）/ main_model（2409 字/34 锚）/ inference_ad（2445 字/27 锚） |
| 锚终验 | ✅ 真坏 0 | 151 锚全好（60+91），0 坏 |

图谱在仓内 `/usr-data/data2/repos/agent-repos/NVIDIA/Kumo-TS/.understand-anything/knowledge-graph.json`。

## 源码甄别（写作期逐行实证）

1. **项目前身名 NV-Tesseract**（CHANGELOG.md:3/11 实证，PR 链接仍指旧仓）。
2. **backbone.py 尾部 `_register_submodules()` 用 sys.modules 动态注册 `backbone.utils.utils` 等合成包**（backbone.py:829/877）——仓内 `from backbone.utils.utils import control_randomness` 实际解析到该单文件，非独立目录。
3. **两子包目录名带连字符（非法标识符）**，18 处靠 `sys.path.append(子包根)` 后以 `from models.xxx`/`from sdk.xxx` 解析（扁平模块无 __init__.py）——scanner 对此系统性盲区，批 9 的 imports 边 100% 手扫。
4. **forecasting_inference_config.yaml 默认 model_name=AutonLab/MOMENT-1-large 与 backbone.py:436 支持列表（仅 google/flan-t5-*）不一致**——MOMENT 血统残留（model.py:13 同样残留）。
5. ETTh_4feature.csv 全仓（py/md/yaml）零引用=孤儿测试夹具；另两个 ETTh CSV 被 quick_example.py 显式引用。
6. **dpm_solver_pytorch=MIT 内嵌 DPM-Solver**（third_party/dpm-solver/LICENSE+NOTICE 双证）；main_model.py:533 dpm_solver_impute + :554 内嵌导入。注意 main_model.py 在 **Kumo-Anomaly/models/** 下（TSDiffuser 主模型），Kumo-Forecast 只有 model.py 工厂——写作任务书的「Kumo-Forecast/main_model.py」路径不存在，已按源码归位。
7. NOTICE 实为法律声明文本，scanner 误标 code，按 document 归档；Ruff 配置单源=Kumo-Forecast/pyproject.toml（Makefile:7 RUFF_CONFIG）双包共用。
8. channel_flow↔interpretability 受控环依赖靠函数体内 local import 化解（源码注释自证）；test_forecasting.py 69 个 DARR 用例全部建节点（行为规格即 SDK 语义）。

## 阅读路线

`onboarding/ONBOARDING.md` 八节；深读 explain 三篇：01 Forecast/backbone.py（合成包动态注册+BackbonePipeline）→ 02 Anomaly/main_model.py（TSDiffuser+DPM-Solver 内嵌）→ 03 Anomaly/inference_ad.py（diffusion 异常检测/DARR）。
