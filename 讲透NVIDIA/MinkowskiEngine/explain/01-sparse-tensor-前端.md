# 01 · 稀疏张量前端：SparseTensor 与 Tensor 基类

> 涉及：`MinkowskiEngine/MinkowskiSparseTensor.py`（784 行）+ `MinkowskiTensor.py`（605 行），行号锚均经源码核实。

## 一、角色定位

引擎全部计算图围绕 **COO 稀疏张量**：坐标矩阵 `C`（N×(D+1)，首列 batch index 当第 0 空间维，`MinkowskiSparseTensor.py:76-77`）加特征矩阵 `F`。两文件是唯一权威定义：`MinkowskiTensor.py:139` 基类 `Tensor` 管属性与运算符，`MinkowskiSparseTensor.py:48` `SparseTensor` 是唯一实例化类，包揽建图脏活（断言、管理器创建/复用、量化去重）。核心分界：**坐标走 C++ 管理器、特征走 torch**——SparseTensor 只持轻量句柄 `coordinate_map_key`（`MinkowskiSparseTensor.py:30` 导入），特征 `_F` 是普通 torch.Tensor 由 autograd 管理。

## 二、内部结构

**基类与全局状态**（MinkowskiTensor.py）：`SparseTensorOperationMode`（L33）分 SEPARATE 与 SHARE（共享单例须手动 clear，L128），默认 SEPARATE（L64）；`SparseTensorQuantizationMode`（L47）六种量化模式。属性面：`coordinate_manager`（L211）、`C` 懒加载（L229-247，首次访问才拉回 torch）、`F` 直返（L261-274）、batch 分解族建在 `_batchwise_row_indices`（L276）缓存上。运算符核心 `_binary_functor`（L511）：键一致直接算 `F`；**键不一致走 union_map**（L524-537）——坐标并集、缺位补 0，即"单边坐标按 0"的实现。

**构造与量化**（MinkowskiSparseTensor.py）：`__init__`（L122-136）两条互斥路径——原始坐标（断言 2D/行数一致/同后端，L192/264/268）或复用键（此时显式断言 coordinates 必须为 None，L206）。管理器获取 L232-258：SHARE 取全局没有就建，SEPARATE 每次新建；docstring 警告（L88-95）：CPU 坐标建完再 `.to(device)` 会白造一张 CPU 坐标图。`initialize_coordinates`（L293）是量化心脏：非 IntTensor 隐式 floor+int 并告警（L294-300）→ `insert_and_map`（L304）拿回 unique_index/inverse_mapping，坐标按 unique_index 重排（L305-306）→ 有重复时按模式归并：SUM/AVERAGE 用 **SPMM autograd Function** 表达（L318-338），RANDOM_SUBSAMPLE 直接 `features[unique_index]`（L339-340），NO_QUANTIZATION 跳过（L341-343）。

**转化族**：`sparse()`（L348）/`dense()`（L460，高维花式索引用 `exec` 动态拼字符串，L550-554——D 是运行期参数）；`slice`（L577）用 inverse_mapping 摊回原始点序；`cat_slice`（L634）skip-connection 拼接入口；`interpolate`（L559）连 TensorField。模块级 `_get_coordinate_map_key`（L754）被卷积层复用决定输出坐标键（L780-782）。

## 三、外部连接

上游：`_C` 扩展（L30-35）、SPMM Function（L45）、`CoordinateManager`（L44）；下游：全部网络层的输入输出类型，`__init__.py` 门面导出。基类 `Tensor.__init__` 空操作（L217），继承的只是方法面。

## 四、数据流

`ME.SparseTensor(features[100,3], coordinates[100,4], tensor_stride=2)` 全程：`_D=3`（L226）→ 新建 CoordinateManager → `CoordinateMapKey([2,2,2],"")`（L272）→ C++ 把 100 行去重为（设）61 个唯一坐标返回 unique_index[61]/inverse_mapping[100] → RANDOM_SUBSAMPLE 下 features 变 [61,3]、坐标同步重排 → 对象持 `_F/_C` 与键，键指向管理器内那张 61 行图。此后同参数层第二次前向直接命中 kernel map 缓存——**复用单位是 (tensor_stride, string_id) 键而非坐标内容**（键碰撞时 C++ 侧改写随机 string id，`src/coordinate_map_manager.cpp:383`）。

## 五、设计决策

- **坐标与特征分离所有权**：坐标收进管理器、Python 只持键——同一坐标图可被多张量共享（残差两臂），kernel map 缓存才能跨层命中；
- **batch index 当第 0 空间维**：查重/卷积偏移在 D+1 维统一处理；代价是手拼坐标首列语义易错（v0.4 从末列挪到首列，L97-104 有迁移警告）；
- **量化用 SPMM 而非手写归并**：求导免费，代价一次矩阵构造；
- **不继承 torch.Tensor 只做代理**（`float()/detach()` 直改 `_F`，`MinkowskiTensor.py:450-478`）：避免复写整个 torch 接口面；
- **双操作模式是显式内存策略**：SEPARATE 防泄漏丢缓存，SHARE 换吞吐要手清（文档示例 L88-97）。

## 六、新人提示

1. docstring `coordiante_map_key`（L83）是**源码拼写笔误**（coordiane），照抄 AttributeError；旧博客的 `coords_man` 术语已更名 coordinate_manager/coordinate_map_key；
2. 默认量化 RANDOM_SUBSAMPLE（L130）：同 voxel **随机保留一条**特征，可复现性靠全局种子；要平均显式传 UNWEIGHTED_AVERAGE；
3. `decomposed_*` 顺序非确定（GPU 哈希插入序），跨 epoch 对齐标签用 `decomposition_permutations`（`MinkowskiTensor.py:291`）；
4. `dense()` 对负坐标默认抛 ValueError（L515-518），需传 `min_coordinate=0`；
5. 起点顺序：`MinkowskiTensor.py` 全局状态段（L33-136）→ `__init__` → `initialize_coordinates` → 再进坐标管理器（02 篇）。
