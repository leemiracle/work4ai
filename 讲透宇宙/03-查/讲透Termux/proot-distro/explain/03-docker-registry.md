# 03 · `proot_distro/helpers/docker/`——纯 Python 的 Docker Registry v2 客户端

## 一、角色定位

`proot_distro install ubuntu` 的背后是一条完整的 **OCI Distribution Spec（Registry v2）客户端**——不依赖 docker CLI/SDK/daemon，纯标准库拉镜像、解成 proot rootfs。Termux 无 root 无 daemon，"拉镜像"必须降级成"纯 HTTP + tar 解包 + sha256 校验"，气质是**协议面薄、校验面厚**：来的字节都过 digest 一关。子包职责自画像见 `__init__.py:21-39`；上游调用方五处——`commands/install.py:320`、build 的 FROM 与 `COPY --from`（`engine.py:676`、`copy_step.py:481`）、`commands/push.py:102`、`commands/search.py:86`，全部 registry 流量都走这五处。

## 二、内部结构

| 模块 | I/O | 职责 |
|---|---|---|
| `refs.py` | 无 | 引用文法解析（refs.py:22） |
| `media.py` | 无 | mediaType 常量 + `canonical_json` |
| `transport.py` | HTTP | 认证、重定向、元数据上限 |
| `cache.py` | 磁盘 | 缓存读写与 blob 完整性 |
| `layers.py` | HTTP+磁盘 | 单 blob 下载与应用 |
| `pull.py`/`push.py` | 全部 | 两条流水线（708/516 行） |
| `search.py` | HTTP | Hub 仓库搜索 |

依赖单向：pull/push 编排，向下用 layers/cache，transport 四家共享，refs/media 是纯函数底座。`media.py:30-38` 的 `canonical_json`（sort_keys+无空格）是统一序列化——统一它，push 重新序列化的 digest 才能与 build 写进缓存的一致（见 4.3）。

`refs.py` 复刻 Docker 官方 `distribution/reference` 文法。`parse_reference`（refs.py:179-242）拒绝 Docker 拒绝的一切：64 位 hex 判为 image ID、digest 只收 sha256（refs.py:228-235——不能验证的 pin 等于没有 pin）。`_split_domain`（refs.py:156-176）切域名：首组件含 `.`/`:`、是 `localhost` 或含大写才算 registry，否则单组件名补 `library/`。另一组"永不抛异常"的宽容函数（refs.py:302-347）服务缓存与容器 manifest 里的历史字符串——**严格文法管一切到 registry 的出口，宽容拆分管纯查找**，是 refs 最值得学的设计。

## 三、外部连接

**向下依赖**：`download.py` 的 `retry_http`（download.py:595，max_retries=5）与重定向基类（download.py:298）；`statedir.open_state_dir`（statedir.py:156-176）逐组件 `O_NOFOLLOW` 开目录；`tar_extract.py:446` 的 whiteout 判定；`atomic.py` 原子写。

**环境契约**：唯一认证入口 `PD_DOCKER_AUTH=username:password`，`env_basic_auth()`（transport.py:557-579）读取，缺冒号即 RuntimeError。

**磁盘契约**：`oci_layers/` 存层 blob，文件名是 digest 冒号换下划线（cache.py:151-158）；`oci_manifests/` 存清单，键为 `sha256("<canonical_ref>_<arch>")` 前 16 hex（cache.py:175-188），目录见 constants.py:98-99。键是纯哈希，条目须冗余存 `image_ref`/`arch` 供辨认。

## 四、数据流

### 4.1 认证链（get_auth_token，transport.py:700-857）

返回 `(authorization, base_url)`；pull 用 `actions="pull"`，push 传 `"pull,push"`（push.py:432）。

**Hub 快路径**（transport.py:754-774）：设了 PD_DOCKER_AUTH 先发**无 scope 的 token 请求**当预检（`_check_credentials`，transport.py:657-697，`docker login` 同款）——错误密码在 pull 前叫停而非伪装成镜像无权限；随后带 `service`+`scope` 换 Bearer token。

**自定义 registry**（transport.py:776-857）：HTTPS 探 `GET /v2/`——200 即全开放；401 读 `WWW-Authenticate`；TLS 失败则判"HTTP-only"（明文重探 transport.py:368-390），仅 `--allow-insecure` 下降级 http 重试（transport.py:849-856）。401 两分支：

- **Bearer**（transport.py:815-838）：`_parse_bearer_challenge`（transport.py:541-554）按 RFC 7235 解析 realm/service（quoted/裸 token 都收）；`_require_usable_realm`（transport.py:582-629）是安全闸——realm 主机归 registry 选（Hub 的在 auth.docker.io），但 scheme 必须 https（http 仅 --allow-insecure），file/ftp/data 一律拒绝，否则恶意 challenge 就能让进程把密码发往任意 URL。
- **Basic**（transport.py:799-814）：htpasswd 型 registry（Nexus/Artifactory 类）无 token 可换，凭据本身就是要发的 Authorization——先在 `/v2/` 预检再返回。

token 再过 `_grant_token`（transport.py:264-292）：非字符串/控制字符/超 Latin-1 一律拒——**响应头注入防护**，防 registry 借 token 夹带 CRLF。

### 4.2 pull（pull.py）

`pull_image`（pull.py:438-495）先过文法门，再分缓存/网络两路。

**manifest/config/digest 链**：网络路径（pull.py:283-310）带四类型 Accept 头（pull.py:90-95）取 manifest；多架构 index 由 `_pick_platform`（pull.py:188-226）两轮匹配——先 arch+variant 精确、再变体无关回退，全落空则列出可用平台。**digest pin 引用**走 `_resolve_pinned`（pull.py:254-280）：pin 文档与 index 的 child manifest 每个都 `require_data_digest` 现场验证——注释称之为 hostile mirror 场景下唯一的拦截（pull.py:138-141）；config blob 同样按 digest 验证（pull.py:313-350）。链路即 **tag →（信任 TLS）→ index → child digest → config digest → layer digest，除第一跳外全程内容寻址**。

**层循环**（pull.py:639-703）：逐层"命中缓存则跳过，否则 download_blob 后立即 apply_layer"。"并发"真相：**层是串行下载串行应用的**——OCI 层是有序栈，第 N 层的 whiteout 可删第 N-1 层的文件，顺序即语义。流水线感来自三处零重复：①下载字节流边写盘边过 sha256（layers.py:85-97）；②缓存判定 `_usable_cached_layers`（pull.py:402-426）每 blob 哈希一次，**描述符整个 pull 期间持有**，apply 读的就是刚哈希的 inode；③`download_blob` 返回 `os.dup(tmp_fd)`（layers.py:116-117）——改名不换 inode。apply（layers.py:126-148）开 whiteout 并边解压边重哈希，封住"同 inode 被截断重写"的最后 TOCTOU。

### 4.3 push（push.py）

`push_image`（push.py:343-516）：先重查文法且**拒绝 digest 命名**（refs.py:245-257——digest 由 registry 算出，无权指定）；config 自检——重新 canonical 序列化 `image_config`，哈希须等于 manifest 的 `config.digest`（push.py:408-423），不等即判缓存污染拒推。每 blob 先 HEAD 探测（push.py:128-147）已存在则跳过；否则 `POST /v2/<repo>/blobs/uploads/` 拿 Location，`PUT <location>?digest=` 单块上传（monolithic），重试单元=重开 session+重传全部字节（push.py:186-288）。最后 PUT manifest，读回 `Docker-Content-Digest` 头（push.py:313）。

### 4.4 search（search.py）

**唯一 Hub 专属** API（搜索不在 OCI spec 内，硬编码 `index.docker.io` 只在此文件，search.py:68）。匿名访问且**故意不转发凭据**（search.py:31-35）——Hub 此端点忽略 Basic（错误密码照样 200），发密码等于白送第三个端点。单页上限 100，更大 limit 用恒定 page_size 翻页（search.py:45-47，页码是偏移乘数）。

## 五、设计决策：内容寻址与缓存投毒防护

cache.py 的威胁模型：**缓存目录 guest 可写**——`BASE_CACHE_DIR` 在 `$TERMUX_PREFIX` 下（constants.py:77），被读写绑定进每个非隔离容器（cache.py:28-33）。四件套：

1. **名字不是证据**：blob 文件名不构成内容证明，消费前一律重哈希。`open_verified_layer`（cache.py:515-558）管可重取 blob，不匹配即删令重下；`open_required_layer`（cache.py:561-585）管本地构建的 blob，不匹配只报错留现场。manifest 缓存同理——tag 条目只能信字面，**pin 条目把当初验证过的原始文档 base64 存进 `documents`，缓存命中时整链重验**（`_cached_pin`，pull.py:498-535），离线安装也逃不过 pin 裁决。
2. **描述符而非路径**：哈希名字后再按名重开是两次打开两个可能不同的文件——guest 可在两步间调包，所以全链路传 fd（cache.py:444-462）。
3. **目录也是名字**：`oci_layers -> <host dir>` 链接能让路径操作打到宿主。缓存目录从信任根逐组件 `O_NOFOLLOW` 走下来（cache.py:203-223），blob 以 `(dir_fd, name)` 打开与删除（cache.py:465-494）；锚定正则拒绝伪 digest 路径穿越（cache.py:94-96）。
4. **服务器不决定分配**：内存态元数据一律 16 MiB 上限（transport.py:112；读 cap+1 字节多一即拒，transport.py:233-239），JSON 形状逐层检查（transport.py:300-322、cache.py:112-148）——恶意响应最坏导致一条干净 RuntimeError，永不 traceback、永不超大分配。

凭据同源规则 `same_auth_origin`（transport.py:122-154）：Authorization 只发同 origin（scheme+host+port），唯一豁免是默认端口 http→https 升级。两个消费点：重定向跨源剥头（transport.py:157-178，Hub blob CDN 对 Bearer 头回 400）；push 上传 Location 跨源剥头（push.py:109-125）。

## 六、新人提示

- **先读模块头注释**：每文件开头 20-75 行 `# Architecture:` 是权威（cache.py:21-73、transport.py:21-73），设计动机多在注释里。
- **RuntimeError 是对外契约**：`InvalidReference` 继承 RuntimeError（refs.py:110），命令层只捕获它——别让 ValueError/TypeError/KeyError 漏出去。
- **测试即活文档**：`tests/unit/` 有 refs/transport/pull/push/search 五套单测，`tests/_registry.py` 是假 registry；`tests/security/` 的 test_layer_cache_integrity 对应第五节。
- **踩坑点**：manifest 的 `_ct` 是 pull 注入的私有键，push 回传前必须剥掉（push.py:333-340）；`canonical_json` 格式不能动，一动 digest 自检便与历史缓存互斥；Docker Hub 无论 `--allow-insecure` 永远验证 HTTPS（transport.py:325-341）。
- **调试抓手**：429 报错自带三种话术，`_relays_docker_hub`（transport.py:433-453）靠 `Docker-RateLimit-Source` 头识别 Hub 前端镜像。
