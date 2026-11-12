# 12 · `tests/conftest.py`：向量化等价门禁

## 一、角色定位

75 行的 conftest 只定义一个 fixture：`assert_vectorized`（`conftest.py:16-17`）。它是 v2 质量体系的灵魂——守护"**逐实例增强 + 向量化执行**"架构的正确性。语义由 docstring 钉死（`conftest.py:21-24`）：把 transform 施加于整批，再对每个元素单独施加"它自己的那份参数"，两者必须逐体素相等。任何跨元素污染、广播错位、概率门泄漏都会当场失败。真正的测试面在消费方 `tests/test_vectorization.py`（开头 docstring `test_vectorization.py:1-10` 同义重述，并声明适用边界：随机性必须在 `make_params` 里、`apply_transform` 给定参数后确定；在 `apply_transform` 内继续采样的 Noise/LabelsToImage 被排除、由各自单测覆盖）。

## 二、内部结构

**fixture 本体**（:16-17）：返回闭包 `_assert`（:32），三个参数 `transform/batch/rtol/atol`（默认 1e-5/1e-6，:34-37）。

**`_assert` 五步**（:32-75）：

1. **留底**：`copy.deepcopy(batch)`（:39）——后面要逐元素重放，原始输入不能被就地变换污染。
2. **整批执行**：`result = transform(batch)`（:40）——走 06 篇 forward 全流程（含概率门）。
3. **取证**：从历史抠参数 `result.applied_transforms[-1].params`（:41）；断言 `"_batched_keys" in params`（:42，**逐实例路径必须激活**——单样本批或未声明 supports 的变换会让此断言失败，防止测试空转）；取出簿记键与 `_keep` 门掩码（:43-44）。
4. **逐元素重放**（:47-55）：原始批 `unbatch()` 拆回 Subject（:47，注意 `SubjectsBatch.unbatch` 在 `batch.py:239`）；对每个 index：单元素重组成批（:49）、克隆输入数据留证（:50-53）、`_slice_params(params, index, batched_keys)`（:54，实现在 `batch.py:337`，把批级参数字典切成该元素的份额并剥掉 `_batch_size`/`_batched_keys`/`_keep` 三个元键——元键清单在 `batch.py:18`）、`transform.apply_transform(single, element_params)`（:55）**直接调内层跳过 forward**——不再采样、不再掷概率门，纯执行。
5. **双重断言**（:57-73）：逐图 `torch.testing.assert_close`（:60-65）整批结果的第 index 行 vs 单跑结果；若该元素被 `_keep` 门掉（:57 `gated_out` 判定），**额外**要求 `rtol=0, atol=0` 的逐位相等（:66-73）——门掉元素必须是与输入逐 bit 相同的真 no-op，不接受"数值上近似的恒等"。

**消费方参数化**（`test_vectorization.py`）：`_batch` 工厂（`test_vectorization.py:22`，4 元素 `(1,12,12,12)` 各加 index 偏移保证元素可区分）；第一组用例覆盖八变换（`test_vectorization.py:33-44`：Ghosting/Spike/Blur/BiasField/Flip/Motion/Swap/Anisotropy）；第二组 `p=0.5` 加概率门（`test_vectorization.py:51-68`，批 6 元素，门掉/保留混布）；第三组专项 `test_anisotropy_tie_rounding_matches_scalar`（`test_vectorization.py:71-81`）钉 .5 平局时 `torch.round` 与 Python `round` 的银行家舍入一致性。

## 三、外部连接

- **上游**：`SubjectsBatch` 与 `_slice_params`（`conftest.py:12-13` 从 `data/batch.py` 导入私有函数——测试直捅内部契约，参数切片协议变更时这里最先红）。fixture 经 pytest 机制注入，图谱 out 边两条（batch.py 与 fixture 自身）。
- **消费方**：`test_vectorization.py` 的三组参数化用例；任何新写向量化变换的作者都应在此加一行参数（08 篇 Motion 即 :41/:59 两处在场）。
- **被测契约的对侧**：06 篇的 `_tag_batched`（`transform.py:366`，写入 `_batch_size`/`_batched_keys`/`_keep`）与 08 篇的恒等占位 + `torch.where` 还原——没有生产侧的簿记就没有消费侧的可回放。
- **同层防线**：`test_transforms_base.py`（输入类型归一化）、`test_inverse.py`（可逆与不 mutate）、`test_hydra.py`（配置导出回放）共同构成变换体系的测试矩阵。

## 四、数据流

以 `assert_vectorized(tio.Motion(degrees=10, translation=10, num_transforms=2), batch)` 为例：

1. deepcopy 留底（:39）→ 整批 `transform(batch)`（:40）：`make_params` 采 4 组运动参数（`motion.py:84-99`），`_tag_batched` 记 `_batched_keys=["transforms"]`。
2. 取 `params`（:41）→ 断言逐实例激活（:42）。
3. 逐元素循环（:48）：`_slice_params`（`batch.py:337`）把 `transforms` 列表切出第 index 份，剥元键（`batch.py:356-359`）；`apply_transform(single, element_params)`（:55）单跑——k 空间分段替换全流程（08 篇）在 B=1 上重演。
4. 断言对垒（:60-65）：`result_images[name].data[index:index+1]` vs 单跑输出。FFT 与 grid_sample 的批实现若与单实现有浮点路径差（如 reduction 顺序），1e-5/1e-6 容差放行**数值等价**而非逐位等价——这是有意的工程妥协。
5. 若该元素被 p 门掉：加测逐位 no-op（:66-73）。两道断言合起来即门禁的全部裁决。

## 五、设计决策（含批判）

**"参数外置 + 内层直调"是可测试性的架构级投资**：随机性集中在 `make_params`、参数可序列化、`apply_transform` 纯执行——三条件齐备才让"整批 vs 逐元素重放"的等价性可以用普通断言表达（`conftest.py:26-29` 把这个前提写成 docstring）。这实质是把**性质测试**（property-based）手工内联进了 pytest：随机参数由测试播种（用例里 `torch.manual_seed(0)`）驱动，任何参数组合下的等价破坏都逃不过。

批判四点。其一，**容差 1e-5/1e-6 是经验值**：GPU 上批/单 kernel 的浮点差可能恰好压线，flaky 风险存在；门禁目前只在 CPU 矩阵跑（`tests.yml`），GPU 路径未纳管。其二，**只验证"批=单"，不验证"单=对"**：若向量化实现与标量实现共享同一个错误（如同一段 FFT 索引 off-by-one），门禁全绿——正确性锚点仍需各变换的单测与物理直觉。其三，`_keep` 全灭时批结果不写历史（`transform.py:235` 的 `_all_elements_gated_out` 检查），此时 `applied_transforms[-1]`（:41）取到的是**前一个**变换的记录——参数化矩阵里 p=0.5 批 6 元素全灭概率约 1.6%，理论上可造成偶发取错参数；当前用例未显式设防（播种缓解但未消除）。其四，白名单制（八变换）靠人肉维护：新向量化变换忘了登记，门禁静默失守——CI 无"遍历全部 supports_per_instance_params=True 变换"的完备性检查。

## 六、新人提示

1. 给新变换过门禁三步：确认 `apply_transform` 无随机性 → 在 `test_vectorization.py` 两组参数化里各加一行 → 播种跑通；若确需在执行期采样（如 Noise），转写"固定参数直调 apply_transform"的等价自测。
2. 调试失败先分诊：数值不等→广播/维度错位；`assert "_batched_keys" in params` 失败→忘了覆写 `supports_per_instance_params` 或批只有 1 个元素（`transform.py:288` 批>1 才激活）。
3. 改 `SubjectsBatch` 的簿记键（`batch.py:18`）必须同步 `conftest.py:12-13` 的直捅导入与 `_slice_params`——这是最脆的一条内部契约。
4. 断言粒度提醒：`rtol=0, atol=0`（:71-72）只对被门掉元素生效，正常元素是数值容差——别把两类失败混为一谈。
5. 这个 fixture 是理解 v2 架构的最佳入口：读懂 :21-29 的语义说明，就读懂了 06/08 篇全部设计动机的"为什么"。
