# 06 · 训练配置族与安全专节

## 角色定位

`examples/` 是 DataFlex 的可运行脸面：train_lora 26 个组件配方、train_full 12 个全参配方、test 4 个冒烟配置，加 deepspeed 五个 ZeRO 配置。本篇讲配置族全景、DoReMi 三步链还原、**必须优先处理的安全发现**。

## 内部结构

**目录分工**：`train_lora/selectors/` 17 个、`weighters/` 7 个（与 components.yaml 一一对应）、`mixers/` 4 个（外加 presel 离线预选对照臂）；`train_full/` 是 DoReMi 三步链、ODM、DynamicMoE、saw 静/动态、coincide、icons、lego 双管线；`deepspeed/` 五配置 ds_z0/z2/z2_offload/z3/z3_offload 覆盖显存阶梯；`accelerate/` 两个 FSDP 配置。字段体系=LlamaFactory 标准+DataFlex 扩展（train_type/component_name/warmup_step 等，dynamic_params.py:38-72）。

**DoReMi 三步链还原**（train_full/mixers/）：
1. **Step 1**（doremi_step1_static_qwen_pt_full.yaml:54-62）：Qwen2.5-0.5B，`dynamic_mix`+`static` mixer+`static_mix: true`，`init_mixture_proportions: [0.5, 0.5]`（:58 注释"uniform as reference weight"）——小模型均匀混比训练出参考模型。
2. **Step 2**（doremi_step2:54-61）：`component_name: doremi`，components.yaml:230 的 `reference_model_path` 指回 Step 1 checkpoint。每边界算超额损失更新 α_t（第 3 篇），采样始终 uniform、损失按 α_t 加权（mix_trainer.py:222-285）；结束 `save_average_weights` 落 `doremi_average_weights.json`+可粘贴的 `doremi_step3_proportions.txt`（doremi_mixer.py:288-310）。
3. **Step 3**（doremi_step3:2,56-62）：目标模型换 Qwen2.5-1.5B，回 static mixer，`init_mixture_proportions: [0.3, 0.7]`（:58 注释"using the weights optimized from DoReMi Step 2"）。

**安全专节（最高优先级）**：
- **swanlab_api_key 明文残留**：`AnLWTMijcbd4cyEfundi3` 以注释留在 **19 个 YAML**（逐文件 grep 实证，如 doremi_step2_dynamic_qwen_pt_lora.yaml:42、odm_dynamic_qwen_pt_full.yaml:42、test_select.yaml:39 等）。注释不执行，但密钥已进 git 历史，视为已泄露。
- **lark_secret 残留恰好 8 个 YAML**：`swanlab_lark_secret: cySzwTbCJh08349FGAhBSf`+飞书 bot webhook URL，在 doremi_step1/2/3_full、odm_full、train_lora/mixers/random、test_select、test_weight 共 8 处（任务书"8 个"对应 lark_secret 集，与 swanlab key 的 19 处是两个口径）。
- **处置：两把凭据（swanlab key+飞书 bot secret）应立即轮换**，再清 git 历史；轮换前该 key 关联的 workspace 可被任何拿到仓库的人读写。对照组：components.yaml:38 的 `DF_API_KEY`、cluster_less.yaml:38 的 `your_api_key` 均为占位符——正确写法。

**两处工程瑕疵**：①`multimodal_fullsft.yaml` 引用不存在的注册键——`:13 dataset: mmfinereason_sft`、`:44 eval_dataset: mmfinereason_eval`，但 `data/dataset_info.json` 只注册了 `mmfinereason_sft_demo/mmfinereason_eval_demo`，开箱即跑必报数据集不存在；②CI 的 pytest 步被注释停用（.github/workflows/test.yml:81-84），三 OS × Python 3.11/3.12 矩阵只做 CLI 冒烟（:63-70）与 import 检查（:72-79），**任何单测回归不会被 CI 拦截**。

## 外部连接

配置族是全系列的汇合点：字段进 dynamic_params 被四 trainer 消费（第 4 篇），component_name 进 components.yaml 五族预设（第 1-3 篇），lego 配方引用 pipelines 桶（第 5 篇）。examples/README.md 与 skills/how_to_use.md 是官方手册。

## 数据流

同一 config 双通道读取：OmegaConf 读全量（cli.py:206-216，支持 CLI 覆盖），load_component 按 component_name 取 params 子集；`${output_dir}` 类占位符在 load_component 替换。components_cfg_file 缺省 `src/dataflex/configs/components.yaml`，cache_dir 多以 `../dataflex_saves/` 开头。

## 设计决策（含批判）

"每预设一个示例 YAML"让 examples 成为活文档；DoReMi 三步三个 YAML 显式还原论文流程、Step 2 自动生成 Step 3 比例文件，链路可追溯。批判：①秘钥走注释说明实验配置曾直接带真实凭据跑过，审查无人拦下；②CI 停用 pytest 却保留三 OS 矩阵——最贵组合跑最浅检查；③模型/数据路径大量硬编码私有机器路径（/jizhicfs/...、/path/to/ckpt/...）。

## 新人提示

第一个实验：`dataflex-cli train examples/test/test_mix.yaml`（仓内 demo 数据）。跑 DoReMi 链记牢 step1→step2→step3，把 components.yaml:230 的 reference_model_path 改成自己的 Step 1 checkpoint。贡献配置前自查三件事：密钥是否走环境变量、dataset 键是否真在 dataset_info.json、是否顺手恢复 CI 的 pytest 步。
