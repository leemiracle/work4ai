# 02 · 双 API 门面与 client 引擎：gusli_client_api + client_imp + io_executors

> 文件：`gusli_client_api.hpp`（286 行）、`05clnt/client_imp.hpp/.cpp`（197/1046 行）、`05clnt/io_executors.hpp`（452 行）；图谱 L05+L06，gusli_client_api.hpp fanOut 25 全仓最大

## 角色定位

Gusli 对外只发布两个单头；client 门面定义**全部数据模型与生命周期语义**，client_imp 是藏在 global_clnt_context 空壳后的隐藏单例（L246 注释 "obscures singleton"），io_executors 把一份 io_request 适配到多种执行后端。三者回答：**用户的 IO 如何安全穿过校验、限流、执行、取消、回收五道关**。

## 内部结构

**门面**（gusli_client_api.hpp）：

- bdev_config_params 五型设备（L59-66）：'x' 永败/'s' 永挂/'F' 文件/'K' 内核块/'N' 远端；附 ACL 与 security_cookie。
- io_request_base::params_t（L157-203）：48B 位域——操作/优先级/mutable_data/safe_io/try_uring/has_mm/async_no_comp/is_remote/11 位 uid+回调。三档完成语义 set_completion/set_blocking/set_async_pollable（L176-178）。
- 生命周期四件套：submit_io（L205）→get_error（L206）→cancel_wait（L208）→done（L209，必须显式收尾）；io_request 子类（L215-218）加防御析构。
- global_clnt_context（L245-284）：常规四步 connect/register/unregist/disconnect；引用计数自动版（L267-268）；危机管理 bdev_force_close（L276，排空卡死 IO+可选重连）、bdev_ctl_report_data_corruption（L278，杀 server）、bdev_ctl_reboot（L281，模拟 server 崩溃重连）。

**引擎**（client_imp.hpp）：server_bdev（L79-94）=一个 bdev 连接反射（conf+bdev_backend_api+递归锁）；bdev_backend_api（L41-77）管控制面 socket/握手/create_dp/内存注册/check_incoming；global_clnt_context_imp（L167-194）聚合配置表+全局 shm 表。

**client_imp.cpp 要点**：parse_conf（L43-94；L89 注释留 "%64s→65 字节越界写"修复史）；server_bdev::connect（L142-223）按五型分支——dummy 直接造 info（fd=100000001，L153），'F'/'K' 走 open+fstat/BLKGETSIZE64，'N' 走 hand_shake（L796-838）；create_dp（L770-794）建环写 cookie 并起监听线程（L1019）。**重连**：listener 死亡→do_on_listener_thread_terminate（L1037）起 cREC 线程（L276-302）→bdev_stop_all_ios（L333-380）internal_cancel 逐个排空→断开→重连→重注册缓冲。**节流**：执行器构造时 in_air.insert 失败即返回 E_THROTTLE_RETRY_LATER（io_executors.hpp:108-112）。

## 外部连接

- 向下依赖 cp_messaging（17 种消息）、dp_io_ring（clnt_send_io/clnt_receive_completion）、shared_mem_bufs。
- **执行器族**（io_executors.hpp）：io_autofail（L25-31，栈上秒败）、sync（L257-286，pread/pwrite 逐 range）、aio（L162-248，libaio+SIGEV_THREAD 多 range 聚合）、uring（L337-446，#ifdef HAS_URING_LIB）、wrap_remote_io_exec_blocking/async（L290-307/309-316，把远端异步包装成本地阻塞——completion_t 语义反转——或透传）、never_reply（L320-329，'s' 卡死注入）。dummy 'x' 直接 io_autofail 注错（client_imp.cpp:656）。

## 数据流

submit_io（L623-689）：重入防护（L624）→find_by_io→本地（safe_io 可跳校验）优先 uring（无回调且 opt-in，L644-647）→aio/sync→run()；远端选 wrap 执行器→clnt_send_io 写环→必要时 dp_wakeup_server doorbell（L1009）→阻塞模式 is_still_running() 等完成。完成反向到达：监听线程收 dp_complete→clnt_receive_completion→client_receive_server_finish_io（L619-621）→extern_notify_completion→用户回调。取消：cancel_wait（L708-722）cancel 后 10µs 步进轮询终止；internal_cancel（L724-735）在 socket 断时模拟完成；done()（L737）detach 执行器。

## 设计决策

1. **空壳门面+隐藏单例**：global_clnt_context 空类，全转发 imp::get()（client_imp.cpp:28-32）——ABI 极稳；BREAKING_VERSION=1 编译期检测（L254）。
2. **done() 显式收尾**：README.md:142 自述"强迫用户思考并发生命周期"；io_request 析构兜底强制清理（L745-758）。
3. **并发契约写在代码**：client_imp.cpp:588-618 穷举竞态与"GUSLI 不防护的用户误用清单"——比文档更权威。
4. **backend_bdev_id 刻意不依赖 uuid.lib**（L32）：16B 裸数组 memcmp。
5. **线程命名 gusli_ 前缀**（L227）：listener 名 `<srvr>cIOl`、重连 cREC（client_imp.cpp:1023/284）。

## 新人提示

- 先读 gusli_client_api.hpp 注释再看实现——注释密度全仓最高。
- cancel_wait 阻塞且可能无界（README.md:139），勿持锁调用。
- uring 要求"无回调+opt-in"且 K8s 默认容器不可用；本地异步默认 libaio。
- 配置可直接传内容字符串（"# "开头判定，client_imp.cpp:46），单测大量使用。
- 提交失败也走回调（L681-683）——别假设回调只在成功提交后到来。

（约 2250 字符不计空格；锚 40+ 处均经核实）
