# Hub 发布流程（hub-publish）

> Hub：`https://swarmskills.openjiuwen.com`（可用 `JIUWENSWARM_HUB_BASE_URL` 覆盖）。
> 资产类型映射：本仓 `plugin` 包 ↔ Hub `agent-plugin`。上传协议：
> `POST /api/v1/plugins`，multipart + Bearer token + `X-Checksum-SHA256`。

## 前置条件

1. Hub 发布令牌：设置环境变量 `JIUWENSWARM_HUB_TOKEN`（令牌不落任何文件、不进 git）。
2. jiuwenswarm 运行环境（热加载校验需要 `openjiuwen` 可导入，如主仓 `.venv`）。

## 发布步骤

```bash
# 0.（可选但推荐）在 jiuwenswarm 运行环境下确认三层校验全绿
python scripts/validate.py --only <name> --require-hot-load

# 1. 一键发布：校验 → 打包 → 上传
python scripts/publish.py <name>

# 产物：dist/<id>-<version>.zip（不进 git）
```

`publish.py` 的字段映射：`asset_name` ← manifest `id`；`plugin_version` ← `version`；
`display_name` ← `display_name.zh`；`description` ← manifest `description`；
`tags` ← 中文标签逗号拼接；可见性默认 public（`--private` 可改）。

## 版本规则

- Hub 以 `(package_name, version)` 定位资产：**重发布必须递增 version**，同版本覆盖需显式 `--force`（谨慎，用户端可能已缓存旧包）。
- 发布完成后运行 `python scripts/catalog.py` 并提交更新的 `catalog/catalog.json`（发布对账用）。
- 合并到 main 不自动发布；按 `release/<plugin-name>-<version>` tag 触发发布流水线。

## 回滚

1. Hub 侧下架/隐藏对应资产版本（联系 Hub 管理员或使用 Hub 控制台）。
2. 仓内回退包内容 commit 并递增 version 重新发布——**不要原地 force 覆盖**已被安装的版本。
3. 若是插件改名场景：旧 id 发最后一个版本，README 指向新插件；`renames.json` 登记映射，并同步到 Hub 侧资产别名。

## 打包约束（scripts/build.py 强制）

- 黑名单目录不进包：`.git` `.archive` `__pycache__` `.pytest_cache` `node_modules` `out` `.venv` `tests` `.idea`
- 黑名单文件不进包：`id_rsa` `id_ed25519` `credentials.json` `token.json` `tokens.json` `.DS_Store`；后缀 `.key` `.p12` `.pfx` `.pyc`；`.env*`（`.env.example` / `.env.template` 除外）
- 拒绝 symlink 与非普通文件；文件数 ≤10000，总大小 ≤512MB，路径深度 ≤32，**zip ≤50MB**
