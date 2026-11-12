# IDM 动作提取管线：合成视频到可训练轨迹的全链

## 一、角色定位

`IDM_dump/` 四脚本 + `gr00t/model/idm.py` 是 DreamGen（2505.12705）中段执行器：世界模型只产出"看起来对"的视频，IDM（Inverse Dynamics Model）反演出动作，让合成数据可训练策略。四步分工——`split_video_instruction.py` 按文件名拆指令（`split_video_instruction.py:L38`）；`preprocess_video.py` 画面预处理（四象限切三视角/GR1 比例裁剪，`preprocess_video.py:L131-148`）；`raw_to_lerobot.py` 生成 LeRobot 骨架数据集；`dump_idm_actions.py` 跑 IDM 推理回填。`IDM` 类（`idm.py:L51`）与 `GR00T_N1` 同构但更轻：backbone 直通、感知全在动作头。

## 二、内部结构

**模型侧**：`IDM.__init__` 用 hydra 的 `instantiate` 装配两个子模块（`idm.py:L71-72`），配置树在 `IDM_dump/base.yaml`：顶层 `_target_: gr00t.model.idm.IDM`，`_recursive_: false` 下挂 `backbone_cfg`（IdentityBackbone）与 `action_head_cfg`（FlowMatchingActionHeadIDM，再递归挂 siglip/DiT/mm_projector）。与 GR00T 版最大差异是**自带视觉前端**：加载 siglip2-large-patch16-256 后 `del self.siglip_model.text_model`（`flow_matching_action_head_idm.py:L193-195`）砍文本塔；`encode_images`（`flow_matching_action_head_idm.py:L322-331`）取隐层过两级 projector 叠视角嵌入。拼装在 `prepare_input_embs`（`flow_matching_action_head_idm.py:L333-369`）：用 token id 图（`_IMG_TOKEN=1`/`_ACT_TOKEN=4`，`flow_matching_action_head_idm.py:L13-18`）scatter。siglip 末层与 logit 参数永远冻结（`flow_matching_action_head_idm.py:L254-262`）。

**数据侧**：`GR00TIDMTransform` 是 XEmbDiT 风格整形器（每帧 16 token、最多 6 帧、序列上限 112，`transforms_idm.py:L84-99`）；`_build_token_ids`（`transforms_idm.py:L196-209`）只拼 IMG/ACT 两段。

## 三、外部连接

- **HF checkpoint**：预训练 IDM 以 HF repo 发布，用例 `--checkpoint "seonghyeonye/IDM_gr1"`（`IDM_dump/scripts/preprocess/gr1.sh`）；`dump_idm_actions.py` 以路径含 `/` 且不存在判定 repo（`dump_idm_actions.py:L24`），拉 conf.yaml 复原配置。
- **数据层**：全链复用第 2 篇的 `LeRobotSingleDataset` 与 transform 体系。
- **下游 GR00T**：dump 给 tasks.jsonl 打 `<DREAM>` 前缀（`dump_idm_actions.py:L406-407`），第 1 篇的 `GR00TTransform` 据此把合成样本 state 置零。

## 四、数据流

1. **split**：文件名 → `{idx}.mp4` + 同名 txt 指令；
2. **preprocess**：`process_batch_frames`（`preprocess_video.py:L150-172`）按本体分派——robocasa/franka 四等分三视角再 resize，gr1 比例裁剪（`preprocess_video.py:L15`），so100 保比例 pad；
3. **raw_to_lerobot**：`episode_data` 里 state 与 action 全是 `np.zeros(44)` 占位（`raw_to_lerobot.py:L272-274`）**动作未知**正是本管线要解决的；`modality.json`/`stats.json` 从真机数据集的 `global_metadata/{embodiment}` 拷贝（`raw_to_lerobot.py:L503-506`），合成数据继承真值归一化统计；
4. **dump**：多 GPU 按 trajectory 分，`load_and_transform_step`（`dump_idm_actions.py:L176-191`）整段解帧缓存、按时间戳取帧；`get_action` 后 `unapply` 还原物理单位（`dump_idm_actions.py:L221-225`），按 `modality.json` 分段重组；重叠时间步多预测取平均写回 parquet（`dump_idm_actions.py:L277-290`）——动作 ensemble。

## 五、设计决策

1. **零占位 + 继承统计**：合成视频天然无动作，先零占位再回填的两段式让"建库"与"标注"解耦；统计继承真机数据保证归一化连续。
2. **ensemble 平均**：每步动作由至多 action_horizon 个滑窗预测平均（`dump_idm_actions.py:L288-290`），单步噪声摊薄。
3. **配置随 checkpoint 走**：`experiment_cfg/conf.yaml` 存进模型 repo（`dump_idm_actions.py:L30-34`），推理端复原。
4. **本体从路径猜**：`raw_to_lerobot.py` 用 `'robocasa' in output_dir` 等子串判定本体与 annotation_source（`raw_to_lerobot.py:L447-465`），目录命名成隐形契约。

## 六、新人提示（含源码级 bug 清单）

- **vis_sep_embedding 是死代码 bug**：`prepare_input_embs` 引用 `self.vis_sep_embedding`（`flow_matching_action_head_idm.py:L349`），该属性**从未定义**；因 `_build_token_ids` 不生成 `_IMG_SEP_TOKEN=5`、`num_sep>0` 分支永不触发才不崩（`flow_matching_action_head_idm.py:L345-351`）。base.yaml 的 `add_seperator_token: true` 是幽灵配置。
- **硬编码 .cuda()**：`(torch.ones(...) * t_discretized).cuda().to(device)`（`flow_matching_action_head_idm.py:L457`）先上 GPU0 再搬目标设备，CPU 推理会崩。
- **fps 内部矛盾**：cosmos_predict2 模式时间戳按 16fps 生成（`raw_to_lerobot.py:L269`）而 info.json 写 8fps（`raw_to_lerobot.py:L346`），help 还写 "FPS=8, frames=81"（实际 93 帧），按 timestamp 取帧有漂移风险。
- **失效的过滤**：过滤 VideoColorJitter 的判断串写成 `"groot.data.transform.VideoColorJitter"`（`dump_idm_actions.py:L69`），包名错拼永匹配不上，靠 `transforms.eval()` 兜底。
- **新本体接入**：补 `global_metadata/{name}` 两文件与 `data_config_idm.py` 配置，训练自己的 IDM（`scripts/idm_training.py`）。
