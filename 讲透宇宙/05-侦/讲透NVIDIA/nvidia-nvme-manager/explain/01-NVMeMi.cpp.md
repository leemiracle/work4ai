# 讲透 NVMeMi.cpp（NVMe-MI 传输层，1618 行）

## 角色定位
全仓的传输底座：把 libnvme-mi 的 C API 包成异步回调风格，供 NVMeDevice/传感器/固件更新共用。每盘一个 NVMeMi 实例（持 nvme_mi_ep），底层共享极简线程设施。

## 内部结构
三块：①端点管理——ctor（:45）开端点并设 2000ms 响应超时（:22/:96），closeEndpoint（:166）持 endpointMux 关闭；②Worker 线程（:103-138）——自搓 io_context+condition_variable 循环（注释 :108-110：BOOST_ASIO_DISABLE_THREADS 下 work_guard 跨线程失效才不用 asio 原生方案）；③命令层——MI 命令（miPCIePortInformation :240 / miSubsystemHealthStatusPoll :341 / miScanCtrl :405 / miVpdRead :474）与 Admin 命令（adminIdentify :560、adminGetLogPage :924、adminSanitize :822、adminXfer :1216、adminSecuritySend/Receive :1509/:1552、adminFwCommit/Download :1316/:1419）。

## 外部连接
上被 NVMeIntf variant 工厂持有（NVMeIntf.hpp:71），NVMeDevice::getIntf() 透传；下连 libnvme-mi 全家（nvme_mi_open_mctp/libmctp、nvme_mi_admin_*）；日志走 phosphor-logging lg2。controllers 映射 eid→nvme_mi_ctrl_t 由 miScanCtrl 填（:457）。

## 数据流
标准命令：post()（:199）→ 三重 commandsCancelled 检查（入队 :201 / 出队 :207 / 拿锁后 :215）→ worker 线程持 endpointMux 串行执行 → boost::asio::post 回主 io_context 发回调。rc 约定：rc<0 传输/库错误（errno 转 errc），rc>0 协议响应状态（bad_message），rc==0 才是成功（每个命令重复此模式）。**两个异类**：adminFwCommit/adminFwDownload 不进 worker，直接调用线程持 endpointMux 同步执行（:1337/:1447）——为固件线程（FwUpdateHandler 的 detached thread）独占端点让路。

## 设计决策
①全局单 worker（workerMap 硬编码 key 0，:62-72 注释 "only create one share worker for all drives"）——MCTP 总线本来串行，多 worker 无益反增锁复杂度；代价是任一盘慢命令阻塞全队列，故 error log 特意只搬一箱（:961-963）；②取消用 atomic bool 三查而非撤队列——队列里的任务自检后空转，配合 host 断电时"先全 cancel 再逐个 close"（NVMeDeviceMain.cpp:1370-1376）保证排干；③adminXfer 用完临时超时立即复原（:1267-1275），不污染全局端点配置；④SecurityReceive 单次上限 4096（:1557）且对返回超长按 protocol_error 拒收（:1589-1598）。

## 新人提示
加命令照抄模板：无效端点先发 no_such_device（每个入口的 nvmeEP==nullptr 分支）、try/catch runtime_error 转 no_such_device（post 已停时）。注意两处上游复制粘贴日志错：adminSecurityReceive 的超长错误文案写的是 "nvme_mi_admin_security_send"（:1591-1593）、post 失败文案写 "adminSecuritySend post failed"（:1611-1614）——读日志时别被误导成 Send 路径。miPCIePortInformation 的端口循环上界是 `i <= ssInfo.nump`（:288），比端口号域多探一次，属上游容忍写法。
