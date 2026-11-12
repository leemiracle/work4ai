# 08 · `src/torchio/transforms/intensity/motion.py`：Motion——k 空间伪影与向量化范式

## 一、角色定位

`Motion`（`motion.py:30`，`IntensityTransform` 子类）模拟 MRI 采集期患者运动伪影：扫描中头部移动会让 k 空间不同分段携带不同刚体运动的图像信息，重建后出现特征性振铃与模糊。实现遵循 Shaw et al., PMLR 2019（`motion.py:36` 给出链接）：把 k 空间沿某轴切成 `num_transforms+1` 段，逐段施加独立刚体变换后回填对应谱线，逆 FFT 重建（docstring 三步流程在 `motion.py:40-45`）。它是 intensity 目录最大文件（561 行），也是**向量化逐实例范式的教科书样本**：每个批元素独立采样运动事件、单次批处理完成全部 FFT 与重采样——因此被纳入 `tests/test_vectorization.py:41` 的八变换等价门禁（12 篇）。

## 二、内部结构

**类层（:30-137）**：类型别名区（:19-22）定义 `RigidTransform`（degrees+translation 三元组的 dict）、`MotionTransforms`（其列表）、`PerElementMotionTransforms`（逐元素嵌套列表）与 `_IDENTITY_TRANSFORM`（:24-27，全零恒等，供被门掉元素占位）。`__init__`（:68）三个参数：`degrees`/`translation` 默认 10.0（经 `to_range` :77-78 转区间对象，注意 translation 单位是**体素**而非 mm，docstring :52-53 明示）、`num_transforms` 正整数校验（:79-82）。`make_params`（:84-99）标准双路径：批共享采一组（:87-89），逐实例采 B 组且被门掉元素放空列表（:90-98）。能力声明两个 supports 均 True（:111-117）。`apply_transform`（:119-137）极薄：按 `_is_per_instance_params`（`transform.py:362` 判 `_batched_keys`）选 `_apply_motion`（:140，共享）或 `_apply_motion_per_instance`（:164），对每个选中图像批整体替换 `.data`。

**共享路径（:140-161）**：`_apply_motion` 把一组参数经 `_shared_motion_parameters`（:255，`_repeat_parameter` :331 用 einops `repeat` 扩到 B 份）复制成批形态，复用同一条段处理管线。

**逐实例路径（:164-189）**：`_check_batch_size`（:192）对账参数数与批大小；`_active_motion_mask`（:213）把空列表转 `(B,)` 布尔门；`_num_motion_transforms`（:233）校验活跃元素事件数一致；`_per_instance_motion_parameters`（:279）用 `partial(_segment_transform_or_identity, ...)`（:294-298）+ `itemgetter`（:300-307）把每段参数拼成 `(B,3)` 张量——被门掉元素自动填恒等（:312-328）；关键收尾在 :188-189：`torch.where(active, transformed, data)` **逐位还原**被门掉元素，保证门掉=零污染。

**物理引擎（:350-449）**：`_apply_motion_segments`（:350）是算法核心——段数 `len(segment_parameters)+1`（:364），首空间轴整除得段宽（:366，除不尽即报错 :367-373 提示减小 num_transforms）；对参考谱 `torch.fft.fftn`（:374）后，逐段对图像施加刚体变换（:379）、变换后图像再 FFT（:380）、用其谱**替换**对应段（`spectrum[:, :, start:end] = moved_spectrum[:, :, start:end]`，:387，段边界由 `_segment_bounds` :393 计算，末段吞掉余数 :411-412），最后 `ifftn(...).real` 重建（:389）并还原 dtype（:390）。

**刚体批执行（:416-561）**：`_apply_rigid_transform`（:416）是纯 torch 批量重采样——`_affine_matrices`（:452）组装 `(B,3,4)` theta（旋转 `_rotation_matrices` :500 做 `Rz@Ry@Rx` :514，平移 `_normalized_translation` :479 除以半尺寸归一到 affine_grid 坐标系 :497），`functional.affine_grid`（:435）生成网格后 `repeat` 到通道维（:441），`functional.grid_sample`（:442）一次完成 B×C 个体素重采样（`rearrange` 在 `(b c)` 合并维与还原之间穿梭 :440/:449）。`_axis_rotation_matrices`（:517）手写三轴旋转矩阵的批版本。

## 三、外部连接

- **上游**：`IntensityTransform`（:17，经其 `_get_images` 只作用 ScalarImage、跳过 LabelMap——`transform.py:684`）；`to_range`（:16，`parameter_range.py` 的区间工具）；einops（:11-12）承担全部形状体操。
- **下游/消费方**：门面 `Motion`（`src/torchio/__init__.py:62`）；`tests/test_noise.py` 邻域之外另有 `tests/test_motion*.py` 直接单测；`tests/test_vectorization.py:41/:59` 两处参数化用例（含 p=0.5 门控版）是它的等价性裁判。
- **对比参照**：同目录 `ghosting.py`（277 行，另一种 k 空间伪影）与 `spike.py`（223 行，谱尖峰）共享"频域手术"思路但无刚体重采样环节——Motion 是其中物理链最长者。

## 四、数据流

`Motion(degrees=10, translation=10, num_transforms=2)` 作用于 `(4,1,12,12,12)` 批（逐实例）：

1. `Transform.forward` 深拷贝→包装成批→概率门（06 篇）；`make_params`（:84）：`n=4` → 每元素 `_sample_transforms`（:101）采 2 个 `{degrees: (dx,dy,dk), translation: ...}`，`p` 门掉者记 `[]`（:93-95），`_tag_batched` 写簿记键（:98）。
2. `apply_transform`（:119）→ `_apply_motion_per_instance`（:164）：mask 判活（:180-182 全灭直接返回）。
3. 每段循环（:183-186）：`_per_instance_motion_parameters`（:279）把 4 个元素该段的 degrees/translation 堆成 `(4,3)` 张量。
4. `_apply_motion_segments`（:350）：fftn 原图 → 对每段：`_apply_rigid_transform`（:416，affine_grid+grid_sample 批量刚体重采样）→ 该段变换图的 FFT 谱**覆盖**参考谱对应带（:387）→ 3 段拼完 ifftn 取实部（:389）。
5. `torch.where`（:189）还原门掉元素 → 写回 `img_batch.data`（:128）→ 历书记录含 `_keep` 与 `_batched_keys=["transforms"]`。

物理含义：k 空间低频（中心）决定整体形状、高频决定边缘——分段替换等价于"运动时刻不同的器官轮廓相互错位叠加"，振铃由此而来。

## 五、设计决策（含批判）

**"参数 Python 化、执行张量化"**是本文件的精髓：`make_params` 阶段参数是普通 dict 列表（可 JSON 序列化、可逐元素切片回放），`apply_transform` 阶段才物化成批张量（:299-307）。这样 12 篇门禁的"逐元素单跑对比"才成为可能——参数能从历史里抠出来重放。恒等占位（:24/:312）+ `torch.where` 精确还原（:189）的组合把"概率门"做成了逐位 no-op 而非近似 no-op，门禁因此可用 `rtol=0, atol=0` 断言（`conftest.py:71-72`）。

批判四点。其一，**段切分沿固定的第一空间轴**（:365-366 用 `shape[-3]`）：docstring 说 "along a random axis"（:40-41），实现却是确定的第一轴——文档与代码不符，且相位编码方向通常并非第一轴，物理保真度打折。其二，**每个运动事件一次全卷 FFT + 一次全卷重采样**（:374-387 循环体）：复杂度 `O(num_transforms × N log N)`，docstring 的 Warning（:58-60）只说慢没说多慢，3D 大卷上 num_transforms=4 的实测成本常超预期。其三，translation 用体素单位且在归一化网格坐标里近似（:52-53/:479-497），与 `Affine` 的 mm 语义不一致——同一数字两个变换强度差一个 spacing 因子。其四，`_num_motion_transforms`（:233）要求活跃元素事件数一致——因为构造期 num_transforms 固定这天然成立，但该约束写死在执行层，未来支持随机事件数时会被静默卡住。

## 六、新人提示

1. 把它当**向量化变换写作模板**读：`make_params` 双路径（:84）+ supports 声明（:111）+ 恒等占位（:312）+ `torch.where` 还原（:189），四件套照抄即可过 12 篇门禁。
2. 增强强度三旋钮：`degrees`/`translation` 控单次运动幅度、`num_transforms` 控事件数（伪影复杂度）；从默认 `Motion()`（10/10/2）起步观察 `plot` 差异再调。
3. 复现实验务必 `torch.manual_seed`（门禁测试 `test_vectorization.py:47` 即如此）——随机性全在 make_params，播种后参数可从 `subject.applied_transforms[-1].params["transforms"]` 打印核对。
4. 2D 切片慎用：段宽=首轴长//(num+1)（:366），薄片轴切出来的"谱段替换"物理意义弱，宁可对体数据施加后重建再取层。
5. LabelMap 自动豁免（IntensityTransform 过滤），不必手动 exclude；但若标签需同步模拟伪影（半监督场景），得另写自定义变换。
