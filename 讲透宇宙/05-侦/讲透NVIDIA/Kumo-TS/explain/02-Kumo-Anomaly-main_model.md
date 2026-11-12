# 02 · Kumo-Anomaly/models/main_model.py — TSDiffuser 扩散主模型与 DPM-Solver

## 角色定位

main_model.py 是异常线的模型心脏：TSDiffuser_base（main_model.py:63）实现完整的"条件扩散做时序补全"训练与推理管线，TSDiffuser_Generic（main_model.py:826）把它泛化到任意数据集。异常检测语义由此而来——把窗口的"可疑段"当缺失值，用扩散模型按正常模式补全，补全值与观测值的残差即异常分数。文件头 docstring 是三种采样的最佳导航（main_model.py:4）。

## 内部结构

构造段：从 config 读扩散参数（num_steps、beta schedule quad/linear main_model.py:113）、建去噪网络 diffmodel=diff_TSDiffuser（main_model.py:109，网络本体在 diff_models.py:79），并预计算 alpha 累积乘积加 clip 防数值事故（main_model.py:129）。条件段：get_randmask 随机掩码（main_model.py:159）与 get_hist_mask 历史模式掩码（main_model.py:171）两种策略；get_side_info 把时间与特征嵌入拼成边信息（main_model.py:186）。损失段 calc_loss（main_model.py:294）：噪声预测 MSE 只算 target_mask 上（main_model.py:344），可选时间一致性辅助损失（一阶速度/二阶加速度对齐，main_model.py:251）作用在反推的去噪数据上。采样段三种：impute 标准 DDPM 反向（main_model.py:442）、ddim_impute 确定性子采样（main_model.py:486）、dpm_solver_impute ODE 快速求解（main_model.py:533）。

## 外部连接

上游：sdk/inference_ad.py 加载 TSDiffuser_Generic 检查点推理（inference_ad.py:1187）；examples/finetune_example.py 用它微调。下游：diff_models.py 提供去噪网络；utils/dpm_solver_pytorch.py 是内嵌的 MIT DPM-Solver（文件头双许可声明），dpm_solver_impute 内延迟导入（main_model.py:554）并用 NoiseScheduleVP 从既有 beta 构造连续调度（main_model.py:562）。评测侧 evaluate/evaluate_with_dpm 成对出现（main_model.py:746/781），后者被 models/utils.py 的 evaluate 入口按 use_dpm_solver 开关调用。

## 数据流

训练（forward main_model.py:714）：process_data 取七元组 → 选 cond_mask（随机或历史掩码）→ get_side_info → calc_loss：对观测数据做逐窗标准化（main_model.py:414）、加噪成 x_t、与条件观测拼双通道输入（main_model.py:432）、diffmodel 预测噪声、仅在 target_mask=observed-cond 上计损。推理（evaluate_with_dpm main_model.py:781）：同样归一化后走 dpm_solver_impute——闭包 model_fn 把 DPM-Solver 的连续时间 t 映射回离散步（main_model.py:601）、按条件策略拼输入，外包成 model_wrapper（main_model.py:638），DPM_Solver 以 dpmsolver++ 二阶 singlestep 采样（main_model.py:647），steps 默认 20（main_model.py:655）；样本再反归一化回原尺度（main_model.py:428）交给 SDK 算残差。

## 设计决策

一为"掩码即缺失"的统一抽象：训练时模拟缺失、推理时把待评估点当缺失，同一套补全机制服务两阶段。二为推理速度押注 DPM-Solver：把上千步迭代压到 10-20 步且无需重训（docstring 宣称 50-100x，main_model.py:19），代价是引入 vendor 依赖与连续-离散时间映射的工程复杂度（无条件的 noisy 条件历史需按求解器实际用到的时间步预计算，main_model.py:567）。三为数值稳定层层设防：alpha clip、噪声乘 0.999、NaN/Inf 检测清洗、float16 兼容 epsilon（calc_loss 内多处）。四为辅助损失可配置默认关：use_aux_loss 才启用，权重与裁剪均可调（main_model.py:75）。

## 新人提示

先读文件头 46 行 docstring 再读代码，三种采样对照表就写在里面。追 DPM 路径时注意 model_fn 闭包里 t_discrete 取批内首元素（main_model.py:609）——DPM-Solver 整批同 t 的假设被显式固化。evaluate 与 evaluate_with_dpm 的 target_mask 都会把 cut_length 前缀清零避免双重评估（main_model.py:777）。改归一化必须同步训练与评测两侧——test_inference_scale_contract.py 专锁这个契约。THRESHOLD 不在本文件：残差出来后的判阈在 utils/adaptive_threshold.py 与 sdk/thresholds.py。
