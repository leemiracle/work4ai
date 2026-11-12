# 11 · HF 模型生态双向：push_to_hub.py 上传管线 + load_from_hub.py 下载复用

## ① 角色定位

zoo 的 pretrained agents 资产全部托管在 Hugging Face Hub 的 `sb3` organization（<https://huggingface.co/sb3>，`docs/guide/integrations.md:8`）。这一对脚本就是这条生态链的双向闸门：`rl_zoo3/push_to_hub.py` 把一个训练产物（模型 zip + 归一化统计 + 配置 + 评测结果 + replay 视频 + model card）打包成完整 HF repo 并上传；`rl_zoo3/load_from_hub.py` 把远端 repo 反向还原成 zoo 本地目录结构，使 `enjoy.py`/`benchmark.py` 可以像读本地模型一样消费它。上传侧管「一个模型 = 一个自描述 repo」，下载侧管「repo → logs/ 目录结构」，两者共享 `huggingface_sb3` 包的命名协议（`ModelName`/`ModelRepoId`），这就是 roundtrip 不失真的关键。

## ② 内部结构

**push_to_hub.py（432 行）**三个函数 + 一个 CLI：

- `save_model_card()`（`rl_zoo3/push_to_hub.py:30-43`）：写 `README.md`——注意 `rl_zoo3/push_to_hub.py:38` 注释 "Always overwrite README"，先 f.write 全文（`rl_zoo3/push_to_hub.py:39-40`），再 `metadata_save(readme_path, metadata)`（`rl_zoo3/push_to_hub.py:43`）把 YAML front matter（library_name/tags/model-index 评测指标）合并回文件头。
- `generate_model_card()`（`rl_zoo3/push_to_hub.py:46-125`）：两步。第一步 `generate_metadata(algo_class_name, env_id, mean_reward, std_reward)`（`rl_zoo3/push_to_hub.py:66`，来自 huggingface_sb3，生成 `library_name: stable-baselines3` + tags `[env_id, deep-reinforcement-learning, reinforcement-learning, stable-baselines3]` + model-index 中 `mean_reward ± std`）。第二步拼模板：标题段 `# **{algo_class_name}** Agent playing **{env_id}**`（`rl_zoo3/push_to_hub.py:69-78`）；Usage 段给出可直接复制的 `load_from_hub` + `enjoy` 命令（`rl_zoo3/push_to_hub.py:93-103`）和 Training 段的 `train` + `push_to_hub` 命令（`rl_zoo3/push_to_hub.py:105-110`）；Hyperparameters 段用 `pformat(hyperparams)` 整体 dump（`rl_zoo3/push_to_hub.py:112-115`）；若 `env_kwargs` 非空追加 Environment Arguments 段（`rl_zoo3/push_to_hub.py:117-123`）。model card 里的命令本身就是用 `algo_name/env_id/organization` 参数化的——文档即代码。
- `package_to_hub()`（`rl_zoo3/push_to_hub.py:128-278`）：五步全管线。Step 1 建仓：`HfApi().create_repo(exist_ok=True)`（`rl_zoo3/push_to_hub.py:193-198`，已存在则复用），`api.snapshot_download` 先拉下远端现状（`rl_zoo3/push_to_hub.py:201`，保住已有文件不误删），再往 `.gitattributes` 追加 `*.mp4 filter=lfs...`（`rl_zoo3/push_to_hub.py:204-207`）保证视频走 LFS。接着 `model.save()`（`rl_zoo3/push_to_hub.py:211`）、`unwrap_vec_normalize(eval_env)` 拆出统计存 `vec_normalize.pkl` 并置 `training=False`、`norm_reward=False`（`rl_zoo3/push_to_hub.py:215-223`，推理态的统计冻结）、解包 zip（`rl_zoo3/push_to_hub.py:226-227`）。Step 2 拷配置：`args.yml`/`config.yml` 直接 copy、`env_kwargs.yml` 用 `yaml.dump` 现写（`rl_zoo3/push_to_hub.py:230-236`），再把 `evaluations.npz` + 全部 monitor csv 打进 `train_eval_metrics.zip`（`rl_zoo3/push_to_hub.py:239-243`）。Step 3 `_evaluate_agent` 跑 10 episode 评测（`rl_zoo3/push_to_hub.py:246`）。Step 4 `_generate_replay` 录 replay.mp4，之后手工清理散落的 `test.mp4` 与 `*.meta.json`（`rl_zoo3/push_to_hub.py:249-258`，TODO 注释承认该清理本应上游做）。Step 5 生成并保存 model card（`rl_zoo3/push_to_hub.py:260-272`），`api.upload_folder` 一次性整目录提交（`rl_zoo3/push_to_hub.py:275`）。
- `__main__`（`rl_zoo3/push_to_hub.py:281-431`）：CLI 与 enjoy.py 高度同构——`get_model_path` 定位模型（`rl_zoo3/push_to_hub.py:324-332`）、off-policy 算法强制 `n_envs=1`（`rl_zoo3/push_to_hub.py:337-340`）、从 `args.yml` 读回 `env_kwargs`（`rl_zoo3/push_to_hub.py:356-362`，注意用 `yaml.UnsafeLoader`，`rl_zoo3/push_to_hub.py:360`）、默认加 `render_mode="rgb_array"`（`rl_zoo3/push_to_hub.py:366-367`，录像需要）、`create_test_env` 建评测环境（`rl_zoo3/push_to_hub.py:373-382`）、off-policy 用 `buffer_size=1` 假 buffer 省内存（`rl_zoo3/push_to_hub.py:385-393`）。差异化点：加载时 `custom_objects` 为空 dict——`rl_zoo3/push_to_hub.py:395-396` 注释明说假设「推送机与训练机同 Python 版本」，否则需按 enjoy.py 方式传 custom objects；atari/minigrid 默认随机策略（`rl_zoo3/push_to_hub.py:401-402`）；最后 `ModelName(algo, env_name)`（`rl_zoo3/push_to_hub.py:405`）与 `ModelRepoId(organization, repo_name)`（`rl_zoo3/push_to_hub.py:410`）拼出 repo id，`generate_video=not args.no_render`（`rl_zoo3/push_to_hub.py:430`）。

**load_from_hub.py（124 行）**一个函数 + CLI：

- `download_from_hub()`（`rl_zoo3/load_from_hub.py:13-98`）：命名协商先行——`ModelName(algo, env_name)`（`rl_zoo3/load_from_hub.py:38`）默认即 repo 名（`rl_zoo3/load_from_hub.py:40-41`），`ModelRepoId` 拼 `{org}/{repo}`（`rl_zoo3/load_from_hub.py:44`）。然后五连下载：模型 zip 与 `config.yml` 必需（`rl_zoo3/load_from_hub.py:47-48`）；`vec_normalize.pkl` 用 `try/except HTTPError` 容错（`rl_zoo3/load_from_hub.py:51-55`，没有归一化文件不是错误）；`args.yml`/`env_kwargs.yml`/`train_eval_metrics.zip`（`rl_zoo3/load_from_hub.py:57-59`）。落盘侧：`exp_id==0` 时 `get_latest_run_id(...)+1` 开新实验目录（`rl_zoo3/load_from_hub.py:61-62`）；目录已存在时 `--force` 走 `shutil.rmtree` 否则抛 ValueError（`rl_zoo3/load_from_hub.py:71-80`）；模型存成 `{env_name}.zip`（`rl_zoo3/load_from_hub.py:89`），三个 yml 存进 `{log_path}/{env_name}/` 配置子目录（`rl_zoo3/load_from_hub.py:90-92`），归一化文件改名 `vecnormalize.pkl`（`rl_zoo3/load_from_hub.py:93-94`），metrics zip 解包到 log_path（`rl_zoo3/load_from_hub.py:97-98`）。CLI 默认 `-orga sb3`（`rl_zoo3/load_from_hub.py:105`）。

## ③ 外部连接

- **依赖 huggingface_sb3**：`rl_zoo3/push_to_hub.py:15-16` import 了 `EnvironmentName/ModelName/ModelRepoId` 命名三件套与 `_evaluate_agent/_generate_replay/generate_metadata`——后两个带下划线，是直接借用的上游内部函数（版本钉在 `pyproject.toml:36` 的 `huggingface_sb3>=3.0,<4.0`）。命名协议在上游 `naming_schemes.py`：`EnvironmentName` 是 str 子类（斜杠转横杠、冒号取后半），`ModelName` 即 `{algo}-{env}` 且 `.filename` 属性给 `.zip` 后缀。
- **被 enjoy.py 消费**：本地找不到模型时自动回退下载——`rl_zoo3/enjoy.py:102` 打印 "Pretrained model not found, trying to download it from sb3 Huggingface hub"，`rl_zoo3/enjoy.py:104-117` 调 `download_from_hub` 后重新 `get_model_path`。
- **被 benchmark.py 消费**：`rl_zoo3/benchmark.py:13` import、`rl_zoo3/benchmark.py:115-119` 同样的自动下载回退。
- **被 migrate_to_hub.py 驱动**：批量迁移脚本用 `get_hf_trained_models`（`scripts/migrate_to_hub.py:8`）与本地 `get_trained_models` 做集合差（`scripts/migrate_to_hub.py:9`），对每个缺失模型 `subprocess.call(["python", "-m", "rl_zoo3.push_to_hub", ...])`（`scripts/migrate_to_hub.py:19`）——`sb3` org 里几百个 agent 就是这样灌上去的。
- **hub 工具链**：`HfApi`/`metadata_save`/`snapshot_download`/`upload_folder` 全部来自 `huggingface_hub`（`rl_zoo3/push_to_hub.py:13-14`）；上游 `load_from_hub` 底层是 `hf_hub_download`，且带 `TRUST_REMOTE_CODE` 门禁——SB3 zip 用 `pickle.load` 反序列化，存在任意代码执行风险。

## ④ 数据流

上传链（`python -m rl_zoo3.push_to_hub --algo ppo --env CartPole-v1 -f logs/ -orga sb3`）：logs 目录产物（模型 zip、args.yml、config.yml、vec_normalize.pkl、evaluations.npz、monitor csv）→ CLI 加载模型+建评测环境 → `package_to_hub` 在本地 `hub/{repo_name}/` 组装完整 repo（模型、解包目录、三个 yml、metrics zip、replay.mp4、README.md）→ `upload_folder` 推到 `{org}/{algo}-{env}`。下载链（反向）：`hf_hub_download` 五个文件 → 按 zoo 结构写回 `logs/{algo}/{env}_{exp_id}/`（zip 在根、yml 在 `{env_name}/` 子目录、metrics 解包）→ `enjoy.py` 的 `get_model_path`/`get_saved_hyperparams` 无感消费。关键对应关系：上传侧 `rl_zoo3/push_to_hub.py:235-236` 写出的 `env_kwargs.yml`，正是下载侧 `rl_zoo3/load_from_hub.py:92` 落盘、enjoy 回读的那个文件——同一份 env 构造参数全程随模型旅行。

## ⑤ 设计决策

- **一模型一 repo、自描述**：model card 内嵌超参（pformat dump）与可复制命令，评测分数进 metadata 的 model-index——HF 页面可直接按 mean_reward 过滤排序，repo 脱离 zoo 也自足。
- **先 snapshot 再上传**：`rl_zoo3/push_to_hub.py:201` 先拉远端现状，是「增量追加」而非「清空重传」，多次推送（如 best model 更新）不会丢历史文件。
- **统计与模型分离**：`vec_normalize.pkl` 独立存在（`rl_zoo3/push_to_hub.py:219`）并在上传前就切换到推理态（training=False/norm_reward=False），保证下载者拿到的统计直接可用。
- **命名即协议**：`ModelName`/`ModelRepoId` 字符串子类让 `{algo}-{env}` 同一时间合法于文件路径、URL、repo id 三个命名空间，双向脚本与 migrate 批量脚本共用同一推导。
- **容错分层**：`vec_normalize.pkl` 缺失是正常变体（HTTPError 捕获），本地目录冲突才是错误（ValueError）；replay 视频失败不阻断上传（上游 `_generate_replay` 内部 try/except）。

## ⑥ 新人提示

- **读码入口**：先读 `package_to_hub` 的五步注释（Step 1-5）再读 `__main__`，CLI 与 enjoy.py 九成同构，可对照着跳读。
- **文件名不对称陷阱**：上传时叫 `vec_normalize.pkl`（`rl_zoo3/push_to_hub.py:219`），落盘后叫 `vecnormalize.pkl`（`rl_zoo3/load_from_hub.py:94`），且 `get_saved_hyperparams` 找的是后者——排查归一化问题时别被两个拼写绕晕。
- **`yaml.UnsafeLoader`**（`rl_zoo3/push_to_hub.py:360`、`rl_zoo3/record_video.py:86` 同款）：args.yml 由训练机写入、含任意 Python 对象，加载等价于执行代码，只对可信来源使用。
- **同机假设**：跨 Python 版本推送旧模型会因 pickle 兼容炸载入，`rl_zoo3/push_to_hub.py:395-396` 注释是权威提示，解法参照 enjoy.py 的 `--custom-objects`。
- **改动连锁**：动 zoo 的 log 目录布局会同时打断 `package_to_hub` 的 config 拷贝（`rl_zoo3/push_to_hub.py:230-234`）与 `download_from_hub` 的还原（`rl_zoo3/load_from_hub.py:85-94`）——这对函数是布局的双向镜像，改一处必须改另一处；动 model card 模板（`generate_model_card`）要记得 README 会整体覆写（`rl_zoo3/push_to_hub.py:38`），远端手工编辑的内容会被冲掉。
- **上传前自测**：`TRUST_REMOTE_CODE` 环境变量与 HF token 是两类常见失败源；token 走 `huggingface-cli login`，`rl_zoo3/push_to_hub.py:427` 显式传 `token=None` 即交给全局配置。

<!-- chars(no-space): 7058, anchors: 73 -->
