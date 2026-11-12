# 04 · processing_gr00t_n1d7.py — 数据侧心脏：Collator、Processor 与归一化闭环

> 源码：`gr00t/model/gr00t_n1d7/processing_gr00t_n1d7.py`（889 行，本目录最大文件）。样本→张量、观测→模型输入、模型输出→物理关节量，全在此文件闭环。

## 一、角色定位

文件定义两个协作组件：`Gr00tN1d7DataCollator`（processing_gr00t_n1d7.py:159）把样本列表合成 batch（含 VLM tokenize+padding）；`Gr00tN1d7Processor`（processing_gr00t_n1d7.py:214）做单样本变换——状态/动作归一化、图像增广、语言正规化、chat 模板，并持有逆变换（decode_action/unapply）与三文件持久化。末尾 `AutoProcessor.register("Gr00tN1d7", ...)`（processing_gr00t_n1d7.py:889）挂进 HF 生态。它同时服务两条链路：训练时被数据集逐样本调用（`__call__`，processing_gr00t_n1d7.py:580），推理时被 `Gr00tPolicy` 的 `process_observation`（:445）调用——同一套归一化保证训推一致。

## 二、内部结构

**本体→projector 索引表**：`_PROJECTOR_INDEX_GROUPS`（processing_gr00t_n1d7.py:69-96）是分组形态的 source of truth——索引不连续（0,1,2,10,11,24,25,26,27），因为它们要对齐预训练 checkpoint 里 CategorySpecificMLP 的 32 档权重槽位（configs/model/gr00t_n1d7.py:123 的 max_num_embodiments）；同组多 tag 仅限"同一物理机器人的数据源变体"（如 26 号组的四条 real_r1_pro_sharpa，processing_gr00t_n1d7.py:85-90）。`_build_tag_to_projector_index`（:99-115）摊平成 `{tag: index}` 并对一 tag 多组直接 ValueError（:108-113）。构造器会用内置表回填用户 mapping 缺失的 tag（:294-296）。

**Collator**（:159-211）：构造时建 Qwen3VLProcessor 并把 tokenizer `padding_side` 设为 "left"（:169，Flash Attention 兼容）；`__call__` 对键分三类——`vlm_content` 走特殊通道抽出 text/images 交给 VLM 处理器统一 tokenize+pad（:179-197）；`pixel_values/input_ids` 等裸键直接 `raise Exception("Not implemented")`（:198-204，防上游绕过 vlm_content 双重处理）；其余（state/action/mask）np.stack 成 batch（:207）。

**Processor 构造器**（:217-331）：28 个参数里藏两个易踩默认值——`max_state_dim/max_action_dim` 默认 29（:232-233）是 N1.5 时代遗产，而模型 config 默认 132（configs/model/gr00t_n1d7.py:74-75），实际值由 checkpoint 的 processor_config.json 覆盖，from_pretrained 不踩坑、手工构造可能踩；`validate_action_horizons`（processing_gr00t_n1d7.py:132-156，在 :282 调用）把"本体 horizon 超过模型 action_horizon"从首次 forward 才爆提前到构造期。图像变换二选一：albumentations（带 mask replay，:305-317）或 torchvision（:318-325）；默认进训练模式（:331）。

## 三、外部连接

- 依赖 StateActionProcessor 做归一化/相对动作转换（processing_gr00t_n1d7.py:251-258）、image_augmentations.py 四函数（:41-45）、Qwen3VLProcessor（try/except 导入 :48-51）。
- 双实例化点：`Gr00tN1d7` 模型内建 collator 处理 vlm_content（gr00t_n1d7.py:547-551）；`Gr00tPolicy` 分持 processor+collator——collate_fn 取自 processor.collator（gr00t/policy/gr00t_policy.py:166）、逐样本 processor(messages)（gr00t_policy.py:409）、batch 后 collate_fn（:412）、推理后 decode_action 回物理量（:421-424）。
- 图谱佐证：本文件与 gr00t_policy.py、gr00t_n1d7.py 构成数据管线三角环，是 modality_configs 之外唯一触碰归一化统计的模块。

## 四、数据流

**训练路径**（`__call__`，:580-701）：断言单样本（:584）→ StateActionProcessor.apply 同时归一化 state/action 并处理相对动作（:591-595）→ action 沿维拼到 max_action_dim=132、沿时序 pad 到 max_action_horizon，并生成 action_mask（有效=1，pad=0，:597-636；无 action 时训练模式直接 assert 失败 :638）→ state 同样 pad（:659-668），且 `state_dropout_prob>0` 时在**数据侧**就把原始 state 置零（:647-654，与模型侧编码后置零 gr00t_n1d7.py:220-226 形成双层 dropout）→ 按训练/评估选图像变换（:671-674）→ `formalize_language` 做 lower+去标点（:677-681）→ `_get_vlm_inputs`（:703-752）逐视角堆叠图像、uint8/4D/3 通道断言（:740-745）、拍平成 (T*V,C,H,W) → `_apply_vlm_processing`（:546-578）组 chat 对话（图像在前文本在后，:556-564）、`apply_chat_template(tokenize=False)` 只产文本（:567-569），真正的 tokenize 留给 collator 批内统一 padding——**两段式设计**是本文件的隐藏主线。

**推理路径**（process_observation，:445-544）：输入已是 batch 张量——state 归一化+pad（:470-485）、图像 (B,T,V,H,W,C) 重排后整批过变换（:487-508）、语言正规化（:510-514）、逐样本 `_apply_vlm_processing` 再统一 `self.processor(...)` tokenize（:516-524）、embodiment_id 查表填充（:526-529）、action_mask 前 horizon 置 1（:531-542）。

**逆变换**：decode_action（:382-404）与 unapply（:406-443）结构相同——按 modality_keys 切开拼起来的 132 维动作，交 `unapply_action` 反归一化并把相对动作加回 state 变绝对量；unapply 额外做 "state." 前缀剥离（:436-438）与 "action." 前缀回填（:443）适配观测字典协议。

**持久化**：save_pretrained 落三文件 processor_config.json/statistics.json/embodiment_id.json（:754-805）；from_pretrained（:807-886）透传 8 个 hub 参数（:812-821）、对老 checkpoint 回填 setdefault（:858-860）、`override_keys` 白名单允许运行时覆盖 11 个键（:868-880）、modality_configs 只增不改（:865-867）。

## 五、设计决策

1. **两段式 VLM 处理**（chat 模板在 Processor、tokenize 在 Collator）：tokenize 需批内统一 padding 对齐，单样本提前 tokenize 长度不一致；代价是 vlm_content 协议被两层共享（:572-577 与 :179-197）。
2. **set_statistics 的静默丢弃防线**（:345-371）：override=False 时新统计被丢弃只发 warning，注释直言混合数据集场景下"训练会带着错误的 mean/std 继续跑"（:357-362）——这是本文件最容易造成隐性训练事故的开关，override_pretraining_statistics 数据集级参数才是在线合并正道。
3. `raise Exception` 而非 `NotImplementedError`（:204）属风格瑕疵，但语义是硬闸：禁止上游直接喂已 tokenize 的 VL 键，强制走 vlm_content 单一通道。
4. formalize_language 默认 True（config 默认）——预训练语料都是小写无标点，推理时不正规化会造成分布漂移。
5. 甄别一条：state dropout 的 0.8 高比例（configs/model/gr00t_n1d7.py:118）由数据侧（:647-654）与模型侧（gr00t_n1d7.py:220-226）各挡一层，前者在归一化前置零、后者在编码后置零；两者概率同源 config，语义不同（丢原始观测 vs 丢表征）。
6. projector 索引表用"分组 dict"而非平铺 dict 作 source of truth（:58-68 注释）：平铺表里两个 tag 撞号会被后者静默覆盖，分组表+摊平器把撞号变成构造期异常（:108-113）。

## 六、新人提示

- 加新机器人：先在 `_PROJECTOR_INDEX_GROUPS` 给未用索引（:69-96 里挑空号），再配 modality_configs，最后 finetune——`new_embodiment`（10 号组，:75）就是官方预留槽。
- 调试归一化问题先看三处：statistics.json 是否真的进了 checkpoint、set_statistics 日志有没有 "DISCARDED"（:363-371）、decode_action 用的 norm_params 与训练是否同源。
- `processor.train()/eval()`（:337-343）控制图像增广与 state dropout，评测忘切 eval 会得到虚高噪声。
- collator 的 `__str__`（:210-211）会打印 model_name/model_type，多模型环境排查张量混批时先打它。
- unapply 的 prev_action 形参已废弃仅保 API 兼容（:419 注释），新代码别依赖。
