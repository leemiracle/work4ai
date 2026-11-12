# 11 · x402_payment_tool：402 检测→策略闸门→签名→重试的支付 agent 工具

## 角色定位

`x402_payment_tool` 解决"agent 撞上 HTTP 402 (Payment Required) 怎么办"：在 ReAct 循环里封装一个会自主完成支付协商的 fetch 工具——请求→检测 402→解析 x402 支付需求→预算闸门→签名→带凭证重试。模块 docstring 列出六步流程后紧跟安全架构四原则（`register.py:38-42`）：策略在签名**前**强制、钱包密钥与 agent 进程隔离、收款方白名单、全量审计。README 直言动因：支付操作不可逆，需要的保障远超普通工具集成。包名 `nat_x402_payment`。

## 内部结构

两个注册函数。主工具 `fetch_paid_api`（Config `register.py:64`）：`max_per_transaction` 默认 0.10 USDC（`register.py:67-70`）、`max_daily_spend` 默认 5.00（`register.py:71-74`）、`allowed_recipients` 收款方白名单（`register.py:75-78`，空=放行所有）、`wallet_signer_url`（`register.py:79-82`，空则落 inline 开发模式）。配套 `get_payment_status`（`register.py:89`）暴露消费状态与历史。

记账基建是模块级可变容器 `_spend_state`（`register.py:97-100`，注释言明用 dict 而非 global 语句是为过 pylint PLW0603）与 `_payment_log` 审计列表（`register.py:101`）。策略函数 `_check_spending_policy`（`register.py:104-134`）三闸：日窗口按 UTC 日期自动重置（`register.py:114-117`）→ 单笔超限拒绝（`register.py:119-120`）→ 日累计将超限拒绝（`register.py:122-129`）→ 白名单不通过拒绝（`register.py:131-132`），全过返回 APPROVED。402 解析 `_parse_x402_requirements`（`register.py:137-164`）：先试响应 body JSON，失败回落 `x-payment-required` header（`register.py:140-146`），取 `accepts[0]`（`register.py:151`）后按 USDC 的 6 位小数把 `maxAmountRequired` 原始整数换算成人类单位（`register.py:152-154`）。

钱包抽象在 `wallet.py`，双签名器是本示例的骨架：`WalletSigner` ABC 定 `sign_payment/get_address/get_balance` 三方法（`wallet.py:49-82`）。`InlineWalletSigner`（`wallet.py:85`）开发用——从 `WALLET_PRIVATE_KEY` env 取 key（`wallet.py:93-96`）经 `eth_account.Account.from_key` 构账户（`wallet.py:99-104`），签名用 EIP-191 `encode_defunct` 消息（`wallet.py:122-132`）；类 docstring 警告此模式私钥与 agent 同进程（`wallet.py:88-91`），且 `get_balance` 是返回 0 的桩（`wallet.py:110-112`）。`RemoteWalletSigner`（`wallet.py:148`）生产用——`WALLET_SIGNER_URL` 指向独立签名进程（`wallet.py:157-158`），address/balance/sign 全部走 HTTP 端点（`wallet.py:163-178`/`wallet.py:188-201`），模块 docstring 点题："The agent process NEVER has direct access to the private key in production"（`wallet.py:34`）。`create_wallet_signer`（`wallet.py:202`）按"有 signer_url 即 Remote"分派（`wallet.py:210-212`）。

测试闭环 `scripts/mock_x402_server.py`：8402 端口起零依赖 HTTPServer（`mock_x402_server.py:118-120`），无 `X-PAYMENT` 头的请求回 402 + `accepts[0]`（`maxAmountRequired: "50000"` 即 0.05 USDC，`mock_x402_server.py:61`；`payTo` 固定 mock 地址，`mock_x402_server.py:65`）；带支付头且 `payTo` 对得上就放行 200（`mock_x402_server.py:84`）——任意合法结构签名都过，不需要真钱包。

## 外部连接

向上：`@register_function`（`register.py:167`）挂 NAT，`payment-agent.example.yml` 用 `react_agent` 同时挂 fetch_paid_api 与 get_payment_status（LLM 默认 `meta/llama-3.3-70b-instruct`）。向外：httpx（唯一 HTTP 依赖）、eth-account（仅 inline 模式需要）、目标付费 API、远程签名进程（生产）。流水：GET（`register.py:194`）→ 非 402 直接走 200/错误分支（`register.py:197-209`）→ 402 时解析→策略→签名（`register.py:259`，失败记 signing_failed，`register.py:265-277`）→ 重试带 `X-PAYMENT` header（`register.py:280-282`）→ 200 才 `_spend_state["daily_spent"] += amount` 并记 success+tx_hash（`register.py:284-295`）；重试仍失败记 retry_failed（`register.py:310-317`）。日志输出刻意把 recipient 截到前 10 字符（`register.py:227`）。

## 数据流

一次"agent 买数据"的端到端：用户任务触发 LLM 调 `fetch_paid_api(url)` → 首次 GET 撞 402 → 解析出 (amount, recipient, asset, network) → 策略三闸（denied 则返回结构化拒绝 JSON 给 LLM，含当日已花与剩余额度，`register.py:247-255`）→ 签名器产出 `{header, tx_hash}` → 重试成功 → 返回 `{status: success, data, payment:{amount, tx_hash}}`。全程 LLM 只见 JSON 字符串，签名细节不进上下文；每次尝试（denied/signing_failed/success/retry_failed）都落 `_payment_log`，`get_payment_status` 的 `_get_status` 按今日时间戳过滤出当日流水供审计。

## 设计决策

1. **闸门前置**（`register.py:39`）：先判预算再让钱包动——被 compromise 或幻觉的 agent 也造不出超预算的有效交易，这是"签名能力最小化暴露"的落地。
2. **记账时机=重试成功后**（`register.py:285`）：失败/被拒不扣日额度，但全部留痕——审计完整性优先于惩罚性扣减。
3. **模块级状态而非持久化**：`_spend_state`/`_payment_log` 进程内有效，重启即清零——示例的诚实取舍，生产需外接账本，日重置逻辑（`register.py:114-117`）已经把时区钉死 UTC 避免歧义。
4. **白名单空=全放行的默认**（`register.py:75-78`）：对示例是对的（开箱即用），对生产是坑——部署前必须显式配置收款方。
5. 值得批评的点：inline 签名器用 EIP-191 个人消息签名模拟 x402 支付凭据（`wallet.py:122-132`），与真实 x402 规范的 EIP-3009 转账授权并不一致——mock server 之所以"任意合法结构都放行"正是为了绕开这一点；把它当协议参考实现会踩坑，当**安全架构**参考才对。

## 新人提示

最短体验路径：`python scripts/mock_x402_server.py &` → `export WALLET_PRIVATE_KEY=<任意 0x 开头 64 hex>` → 按 README 用 mock 地址 `http://localhost:8402/v1/market-data` 跑 `nat run --config_file src/nat_x402_payment/configs/payment-agent.example.yml`。验证策略闸门最直接的办法：把 config 里 `max_per_transaction` 调到 0.04（低于 mock 的 0.05）看拒绝 JSON。写自己的远程签名器只需实现 `/address` `/balance` `/sign` 三个 HTTP 端点（对照 `wallet.py:163-201` 的调用约定）。与仓内 spraay 示例对照读收获最大：那里用 x402 SDK 托管了同样的协商，且用 dry-run 模式替代了 mock server。
