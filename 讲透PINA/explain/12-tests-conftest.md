# 12 · tests/conftest.py —— 17 行共享装置与"每文件自洽"的测试哲学

## 一、角色定位

`tests/conftest.py` 全文 17 行，只定义一个 pytest 夹具 `clean_tmp_dir`——却是整个测试体系（126 个 py 文件）唯一的共享装置。把它选进精讲系列，不是因为代码量，而是因为它是一枚透镜：PINA 测试体系的组织哲学（显式、无状态、每文件可独立阅读）在这个最小公共件上体现得最彻底。反差是理解点：同类科研库的 conftest 常膨胀成夹具工厂（随机种子、设备选择、样例问题构造层层堆叠），PINA 却把共享面压到只剩"一个干净的临时目录"，其余全部下放回各测试文件。

## 二、内部结构

逐行地图：

- `tests/conftest.py:1-3`：三个 import——`shutil`（删树）、`pathlib.Path`（路径对象）、`pytest`（夹具装饰器）。
- `tests/conftest.py:6-7`：`@pytest.fixture` + `def clean_tmp_dir(tmp_path)`。参数 `tmp_path` 是 pytest 内建夹具，每次测试自动给一个唯一空目录；本夹具是它的薄包装。
- 建段（L8-13）：L8 转 `Path` 对象；L10-11 `if path.exists(): shutil.rmtree(path)`——`tmp_path` 本身就是新建空目录，这步 rmtree 是防御性重置，保证起点幂等（目录已存在也不带残留）；L13 `path.mkdir(parents=True, exist_ok=True)` 重建。
- 用段（L14）：`yield path`——yield 前是 setup、yield 后是 teardown 的 pytest 经典三段式；测试体内拿到的就是可写目录。
- 清段（L16-17）：再判存在则 `rmtree` 清场。Lightning 的 checkpoint 会生成 `lightning_logs/version_0/checkpoints/` 深层树，这里负责连根拔掉。

注意没有 `scope` 参数：默认 function 级，每个测试函数拿到独立目录——这是"无状态"哲学的机制保障。

## 三、外部连接

conftest.py 靠 pytest 的自动发现机制生效，没有任何 import 边——图谱里它只有一条 `depends_on` 入边（来自 `code_formatter.sh`，black 检查对象），是全测试网的隐性底座。消费者实测：`grep -rln clean_tmp_dir tests/` 命中 12 个文件，集中在两类场景——checkpoint 存取恢复（如 `tests/test_solver/test_physics_informed_single_model_solver.py:151` 的 `def test_train_load_restore(clean_tmp_dir, case)`）与需要落盘产物的回调/模型测试。测试网全景（图谱口径）：126 文件分两组镜像——训练主链路六套件 61 文件（test_model/test_solver/test_callback 等），组件层 13 套件 65 文件（condition/equation_zoo/problem_zoo/domain 等）；几乎全部经 `import pina` 门面进入（test_solver 对门面 55 边），测试因此天然是公共 API 契约的活文档。CI 侧由 `.github/workflows/tester.yml` 守护：L16 三平台矩阵 `os: [windows-latest, macos-latest, ubuntu-latest]`、L17 五版本 `python-version: ['3.10', ..., '3.14']`、L14 `fail-fast: false` 不因单格失败取消其余组合；L40 起 black 检查独立成 job。

## 四、数据流

以最典型的消费者走读一次夹具生命周期——checkpoint 往返测试 `test_train_load_restore`（`tests/test_solver/test_physics_informed_single_model_solver.py:151`）：

1. pytest 收集到测试函数签名里的 `clean_tmp_dir`，向上找到 conftest，执行 setup（建目录）后把 `path` 注入参数；L154 `dir = clean_tmp_dir` 接收。
2. L166-175 构造 `Trainer(solver=..., default_root_dir=dir, max_epochs=5, ...)`——Lightning 把日志与 checkpoint 全部落进该目录（`lightning_logs/version_0/checkpoints/epoch=4-step=5.ckpt`）。
3. L176 `trainer.train()` 训完；L179-183 新建 Trainer 用 `ckpt_path` 从该路径续训；L186-190 `PhysicsInformedSingleModelSolver.load_from_checkpoint(...)` 再走一次加载。
4. L196-199 对新旧 solver 的 forward 输出 `torch.testing.assert_close`——存取往返无损的强断言。
5. 测试函数返回，pytest 恢复夹具生成器，执行 yield 之后的 L16-17 清场。整个测试不留任何磁盘痕迹，重复跑、并行跑（pytest-xdist）互不干扰。

## 五、设计决策（含批判视角）

- **唯一夹具的取舍**：共享装置最小化换来的是"每个测试文件可独立阅读"——定位问题不需要追溯夹具链，新文件复制粘贴即可起跑。代价同样明显：样例构造在文件间重复，`tests/test_solver/test_physics_informed_single_model_solver.py:16` 的 `define_direct_problem_model` 与 `tests/test_callback/test_r3_refinement.py:41` 起的 Poisson 问题构造几乎是同款代码，问题/模型样板在 test_solver 十一个文件里各写一份。这是"测试即文档"（可抄性优先）对"测试即代码"（DRY 优先）的主动选择，库规模小时净收益为正，套件再涨一个量级会开始疼。
- **夹具管目录不管种子**：`clean_tmp_dir` 只负责文件系统卫生；随机性控制（torch 种子、采样点）完全缺席，测试可重复性依赖各文件自觉。配合 CI 矩阵 15 个组合（`.github/workflows/tester.yml:16-17`），偶发失败难以本地复现是这套体系的真实风险。
- **对拍作为质量底线**：zoo 系列是"实现与已知解互证"的范式——`tests/test_equation_zoo/test_advection_equation.py:8-10` 手工构造带标签的 `pts`/`u` 张量，L28-29 断言 `residual.shape == u.shape`，L31-33 验证缺 `t` 标签、`c` 长度不匹配空间维时的负例。11 个 zoo 方程文件逐一如此对拍，改方程实现后跑这套件是最低验证标准。
- **冒烟下限**：`tests/test_package.py:1-2` 整个文件只有一行 `import pina`——发行版"可装可导"的最后门卫，简单到不会出错，但也只证明 import 不炸。
- **无覆盖率门禁**：.github/workflows/tester.yml 只有 pytest 与 black 两个 step，没有 coverage 阈值——对 0.3.x 阶段的科研库是务实选择，长期看挡不住"只测 happy path"的漂移。

## 六、新人提示

读懂一个 API 最快的路径不是文档而是它的测试文件：找用法去 `tests/test_solver/`，找方程语义去 `tests/test_equation_zoo/`，两个目录都比 Sphinx 页面更新得更勤。实操命令：单套件 `pytest tests/test_solver -k constructor`，全套件 `python3 -m pytest`（CI 同款，`.github/workflows/tester.yml` 的 Install 步骤装 `.[test]` extras）。写新测试的三条约定：直接抄同目录文件的五段式骨架（constructor/train/validation/test/load_restore）；需要落盘就用 `clean_tmp_dir`，别自建 tmp 逻辑；抵制往 conftest 加新夹具的冲动——共享面膨胀会破坏"每文件自洽"这个本仓最重要的测试资产。跑测前确认依赖装的是 `pip install .[test]`（含 scipy），否则 zoo 对拍会因缺依赖假失败。

---
*自报：正文不计空格字符 3605；file:line 锚 9 处（全部对 commit 60ea474a 逐条 grep 核实）。*
