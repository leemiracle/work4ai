# 06 测试体系：mock_sandbox 夹具族、真容器探测跳过与 conftest 链

## 角色定位

`examples/sandbox_agent/tests/` 共 12 文件 2408 行（对照 src 的 3088 行，测试/源码比≈0.78，example 工程里罕见的厚度）。体系分两层：**单元层**（10 个 test_*.py，全部基于 mock，零外部依赖、毫秒级）与**集成层**（test_docker_sandbox_integration.py，324 行，真起容器）。两层之间的粘合剂是 conftest.py 的夹具族——尤其 `mock_sandbox`，它以 30 行代码替代了"每个测试自建沙箱桩"的重复劳动，是整个 tools 层测试的策略核心。集成层的"探测-跳过"模式则保证同一套测试在有无 Docker 的环境里都能安全运行，这是 sandbox 类项目 CI 化的关键设计。

## 内部结构

**conftest.py（86 行）四夹具**。`event_loop`（conftest.py:27-32）session 级手工建事件循环，供 pytest-asyncio 复用；`mock_sandbox`（conftest.py:35-58）是核心：`MagicMock(spec=BaseSandbox)`（conftest.py:44）——spec 约束让 mock 只暴露 ABC 声明过的方法，接口漂移立即爆 AttributeError；随后六行 AsyncMock 把核心方法全部异步桩化：`run_command` 恒回 `CommandResult(exit_code=0, stdout="output", stderr="")`（conftest.py:47）、read_file/read_file_bytes/write_file/start/cleanup 各回合理默认（conftest.py:50-56）。`docker_sandbox_config`/`daytona_sandbox_config`（conftest.py:61-86）提供两份现成配置字典，供 factory 测试复用。

**集成层的探测-跳过**。test_docker_sandbox_integration.py 模块加载即探测一次：`docker_available()` 尝试 `docker.from_env().client.ping()`（test_docker_sandbox_integration.py:27-35），结果存模块级 `_docker_available`（test_docker_sandbox_integration.py:39）；`pytestmark = [integration, asyncio]` 打双标（test_docker_sandbox_integration.py:42-45）；真正生效的是 `@pytest.fixture(autouse=True) def skip_without_docker()`——无 Docker 则 `pytest.skip`（test_docker_sandbox_integration.py:49-53）。注释直言这是"fixture 条件跳过而非 pytestmark"的有意选择（test_docker_sandbox_integration.py:48），因为 pytestmark 无法按环境条件化。

**集成测试五个类**按 ABC 能力面切分：Lifecycle（start 后 `_container is not None`、cleanup 后置 None，test_docker_sandbox_integration.py:76-88）、Commands（echo 成功/exit 1 失败/stderr 分流，以及用写文件代替 `python -c` 内联规避转义，test_docker_sandbox_integration.py:145-154）、FileOperations（写读回环；不存在文件抛 FileNotFoundError，test_docker_sandbox_integration.py:204-205；嵌套父目录自动创建，test_docker_sandbox_integration.py:208-215）、Network（开网 DNS 可解析 test_docker_sandbox_integration.py:238-244 vs 断网 socket 解析必败 test_docker_sandbox_integration.py:263-271——网络开关的**双向断言**）、ResourceLimits（64m 容器里分配 100MB，test_docker_sandbox_integration.py:277-303；sleep 10 配 timeout 2 必失败，test_docker_sandbox_integration.py:305-324）。每个类的 sandbox fixture 都是 yield 后 try cleanup（test_docker_sandbox_integration.py:68-73），容器不跨测试泄漏。

**单元层全景**：test_sandbox.py 锁 CommandResult 语义（success property/to_dict，test_sandbox.py:27-52）与 factory 判别（create_sandbox_from_dict 返回类型，test_sandbox.py:105-116）；test_register.py 锁配置默认值与自定义值（test_register.py:27-45）及 volumes/environment 字段（test_register.py:54-69）；test_tools_sandbox.py（422 行最大）逐工具验证信封格式与截断行为——还能就地下钻重定义 mock，如把 run_command 换成回 `stdout="output.txt\ndata.json\n"` 验证 list_generated_files 解析（test_tools_sandbox.py:74-77）；test_daytona_sandbox.py（230 行）全是 MagicMock 桩测 Daytona 逻辑，云后端零真实调用。

## 外部连接

- **依赖链**：conftest.py 直接 import 生产代码 `BaseSandbox/CommandResult`（conftest.py:23-24）做 mock spec——测试与 ABC 契约强绑定，base.py 改方法签名会立刻打断测试桩，这是免费的契约测试。
- **与 src 的镜像关系**：测试文件与源码模块一一对应（test_register↔register.py、test_tools_host↔host/、test_tools_sandbox↔sandbox/…），新人找某模块的测试零搜索成本。
- **pytest 生态**：pytest-asyncio（pytestmark asyncio、event_loop）+ unittest.mock；integration 标记需在 pyproject.toml 注册后可用 `-m "not integration"` 反向排除。
- **CI 接口**：单元层天然进 CI；集成层靠探测自动降级为 skip——CI 无 dind 全绿跳过，本地有 Docker 自动升级为真验证。

## 数据流

单元测试流：测试函数请求 `mock_sandbox` → conftest 桩化六方法 → 被测组件（executor/工具/工厂）零 IO → 断言信封字段与截断文本。集成测试流：模块加载探测 Docker（test_docker_sandbox_integration.py:39）→ autouse 夹具裁决 skip 或放行（test_docker_sandbox_integration.py:52-53）→ sandbox fixture 真建容器（256m/0.5CPU 压小规格，test_docker_sandbox_integration.py:62-67）→ 真实 exec_run/tar 往返 → yield 后 force cleanup。两条流共用 conftest 配置字典夹具，验证 dict→Config→实例的判别链。

## 设计决策

1. **spec=MagicMock 而非裸 MagicMock**（conftest.py:44）：接口即契约，ABC 多一个方法、mock 少一个桩，测试即红——把"接口漂移检测"前置到夹具定义处。
2. **探测一次、模块级缓存**（test_docker_sandbox_integration.py:38-39）：ping 不进每个测试，探测开销归一。
3. **autouse fixture 而非 skipif 装饰器**：skipif 在收集期求值，autouse 在 setup 期——后者能配合模块加载期事实 `_docker_available`，注释（test_docker_sandbox_integration.py:48）表明作者做过显式取舍。
4. **集成断言写"现象"不写"机制"**：内存限制测试只断言 `result is not None`+"不该挂死"（test_docker_sandbox_integration.py:297-300，注释承认具体行为依 Docker 配置而异）——对环境敏感的集成点，弱断言+不挂死优于强断言+flaky。
5. **网络双测**（通 & 断，test_docker_sandbox_integration.py:238-271）把 network_mode="none"（docker_sandbox.py:110）这一安全属性纳入回归——隔离能力本身被测试保护。
6. **mock 夹具只给"成功路径"默认值**：失败路径由各测试就地重配 AsyncMock（test_tools_sandbox.py:74-77）——集中默认+局部覆盖，避免夹具膨胀。

## 新人提示

- 跑法：`pytest tests/ -m "not integration"` 纯单测秒级；本机有 Docker 直接 `pytest tests/` 全量；想看集成跳过原因加 `-rs`。
- 给新工具写测试的样板在 test_tools_sandbox.py:74-77：先 mock_sandbox、需要非默认回包就地重定义 run_command、断言 status 信封。
- mock_sandbox 的 read_file 恒回 "file content"（conftest.py:50）——测截断逻辑时记得传足够长的自定义串，别被默认短串骗过。
- Daytona 无集成层：改 daytona_sandbox.py 后单测全绿不代表云端能跑，发布前须手工冒烟（API key 成本）。
- event_loop 夹具是 session 级自定义，升级 pytest-asyncio 新版可能冲突（自带 loop 政策），届时优先删它而非禁插件。
