# 12 · spraay_crypto_payments：x402 网关多付方案与 dry-run 替代 mock

## 角色定位

`spraay_crypto_payments` 是本仓第二条加密支付线：对接 Spraay x402 网关（生产地址 `gateway.spraay.app`），让 agent 用 USDC 微支付跨 15 条链执行**批量多收款方转账**（BPA batch）、托管与 RTP 支付。与 11 篇的 x402_payment_tool 对照：那边手写协商+本地 mock server，这边 x402 SDK 全托管+**dry-run 模式替代 mock**——不设私钥时一切付费端点返回结构化报价，不动一分钱，CI 与演示天然安全（模块 docstring `spraay_client.py:21-32` 明列双模式）。

## 内部结构

HTTP 客户端层 `spraay_client.py`（441 行）：`_TOKEN_DECIMALS` 表钉死六种代币精度（ETH/WETH/DAI=18、USDC/USDT/EURC=6，`spraay_client.py:52-59`），未知代币默认 18（`spraay_client.py:61`）。`to_batch_execute_payload`（`spraay_client.py:64-120`）是批量支付的**单位陷阱防御**：免费 validate/estimate 端点收人类可读小数 `[{"to":addr,"amount":"1.5"}]`，付费 `/api/v1/batch/execute` 要平行数组+原始最小单位（docstring 对比 `spraay_client.py:67-73`）——函数先幂等检测已是扁平形态（`spraay_client.py:94-95`），再按 token 查精度用 `Decimal` 精确换算（`spraay_client.py:97-99`、`spraay_client.py:111`），1.5 USDC → "1500000"。

`SpraayClient`（`spraay_client.py:123`）构造时只存 gateway_url/timeout 并读一次 `EVM_PRIVATE_KEY`（`spraay_client.py:130`，docstring 承诺永不落日志/回显，`spraay_client.py:34-35`）；x402 客户端懒构造缓存（`spraay_client.py:133-134`）。dry-run 路径 `_parse_402_response`（`spraay_client.py:136`）把网关 402 报文转成 `mode: dry_run` 结构化报价；live 路径三件：`_get_x402_client`（`spraay_client.py:181`，函数内 import `x402Client` 与 `register_exact_evm_client`/`EthAccountSigner`，`spraay_client.py:200-201`/`spraay_client.py:217-219`，依赖缺失给出可执行的 pip 提示，`spraay_client.py:204-205`）、`_decode_payment_response`（`spraay_client.py:232`，base64 解码结算头里的交易哈希）、`_live_request`（`spraay_client.py:246`）用 `wrapHttpxWithPayment`（`spraay_client.py:288`）把 httpx 包进支付传输——402 由 SDK 自动签 EIP-3009 `TransferWithAuthorization` 重试（模块 docstring `spraay_client.py:26-32`），若重试后仍 402 则给出"检查钱包 USDC 是否足够"的结构化错误（`spraay_client.py:294-302`）。

工具层 `register.py`（410 行）用 **function group** 组织：`SpraayToolsGroupConfig`（`register.py:38`，name=`spraay`）+ `@register_function_group`（`register.py:51`），组内共享一个 `SpraayClient`（`register.py:56`）。十个工具两档：免费六件恒注册——health/routes/chains/price/batch_validate/batch_estimate（`register.py:399-404` 的 `add_function`）；付费四件 balance/batch_send/escrow_create/rtp_discover（`register.py:256`/`register.py:316`/`register.py:340` 等）挂 `filter_fn=_requires_evm_key`（`register.py:406-410`）——谓词是构造时捕获的常量 `bool(os.environ.get("EVM_PRIVATE_KEY"))`（`register.py:384-390`，注释言明这是 NAT 条件工具成员的惯用法），无 key 时它们**从 agent 工具集里直接消失**并打 INFO 日志说明（`register.py:392-395`）。

## 外部连接

`configs/config.yml` 三行接线：function_groups 引 `spraay` 组、`gateway_url: ${SPRAAY_GATEWAY_URL:-https://gateway.spraay.app}` 环境变量带生产默认、workflow 的 `tool_names: [spraay]` 引整组。LLM 用 `meta/llama-3.1-70b-instruct`。向外依赖：Spraay 生产网关（免费端点也是真的）、Base 链 USDC（live 模式，README.md:292 要求钱包同时覆盖网关费 $0.02 与批量金额）、x402 SDK 的 `[evm,httpx]` extras。README 的 live 警告直言 batch_send 动真钱、建议专用小额钱包先测单收款方（README.md:256）。

## 数据流

dry-run 全链（默认）：agent 调 batch_validate/batch_estimate → 客户端打免费端点拿校验/估价（含 `protocolFeeBps: 30` 即 0.3% 协议费）→ agent 调 batch_send → 网关 402 → `_parse_402_response` 返回 `mode: dry_run` 报价 JSON，零签名零扣款。live 全链：同上直至 402 → SDK 自动签 EIP-3009 → 带 `X-PAYMENT` 重试 → facilitator 链上结算 → 工具返回业务结果+`settlement`（交易哈希经 `X-PAYMENT-RESPONSE` 解码）。README.md:306 给出的渐进验证法：同一命令先无 key 跑（报价）再有 key 跑（真付），差额行为可预期。

## 设计决策

1. **dry-run 替代 mock server**：与 x402 例的 `mock_x402_server.py` 相映成趣——mock 在本地伪造协议对端（连签名格式都能宽容），dry-run 用**生产网关的真 402 报文**只截断在签名一步。后者保真度更高（报文 schema 永远与线上一致）且零维护，但依赖外网；本仓因此两者兼有，mock_x402_server.py 与 agent_identity_tool 的 mock_registry_server.py 是仅有的两个本地 mock，支付线 Spraay 侧独走 dry-run。
2. **filter_fn 渐进披露**（`register.py:406-410`）：付费工具"无 key 不存在"而非"存在但报错"——LLM 看不见就不会尝试，杜绝幻觉调用烧 gas 的可能，这比事后拒绝更安全。
3. **Decimal 强制精确**（`spraay_client.py:111`）：float 乘 10^18 必丢精度，链上金额用二进制浮点是经典事故源，这里从工具函数层面杜绝。
4. **签名器进程内但懒加载**：与 x402 例的"生产必须远程签名进程"不同，Spraay 把 key 读进 agent 进程内存（`spraay_client.py:130`）——代价换来 SDK 托管的完整协商；安全边界靠 dry-run 默认+显式 env 开关，是"个人 agent 工具"与"企业部署工具"两种威胁模型的分野。
5. 值得批评的点：付费工具的 filter 谓词在**构建时**固化（`register.py:384-390`），进程内无法热启停——误配 key 启动的进程只能重启才能收回付费能力。

## 新人提示

零成本起步：不设任何环境变量，`uv pip install -e .` 后 `nat run --config_file configs/config.yml --input "validate batch ..."` 即可走通全部免费工具与 dry-run 报价，仅需 `NVIDIA_API_KEY`。上 live 前：README.md:292 的两条硬前提（Base 链 USDC 覆盖费+金额、`sender` 填派生地址否则 batch 工具填零地址占位只适合 dry-run）；首次真实支付建议绕过 agent 用 README.md:306 指向的 smoke 脚本单笔验证。排错首选信号：live 重试后仍 402 几乎总是 USDC 余额不足（`spraay_client.py:294-302` 的报错就是这个意思）。与 11 篇对照读：同一个 x402 协议，"手写协商+隔离签名器"与"SDK 托管+条件注册"两套取舍，几乎是一份支付工具设计决策对照表。
