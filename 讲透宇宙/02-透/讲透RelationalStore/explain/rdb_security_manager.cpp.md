# rdb_security_manager.cpp 精讲

> 源码：frameworks/native/rdb/src/rdb_security_manager.cpp（858 行）＋ include/rdb_security_manager.h

## 1. 角色定位

知识图谱 rdb-kernel 层，导览第 10 步主角。加密本体由 SQLite codec 完成（sqlite3_key/sqlite3_rekey），"密钥从哪来、存哪、怎么轮换"则由本文件单例 RdbSecurityManager（GetInstance() L535）承担：应用不传密钥时自动生成 32 字节 work key，且密钥绝不明文落盘——磁盘只存 HUKS 根密钥加密后的密文。

## 2. 内部结构

- RdbPassword（L50-110）：定长数组避免堆残留，SetValue（L80）覆写旧值，析构 Clear() 归零。
- RdbSecurityManager 四组方法：
  - 生成/存取：GenerateRandomNum（L155）；写链 SaveSecretKeyToFile（L172）→EncryptWorkKey（L285）→SaveSecretKeyToDisk（L216）；读链 LoadSecretKeyFromDisk（L460）→Unpack（L626）→Decrypt（L731）→DecryptWorkKey（L306）。
  - 主入口 GetRdbPassword（L486）：flock 锁→旧格式迁移→文件为空才生成新钥。
  - 生命周期：DelAllKeyFiles（L505）、ChangeKeyFile（L556）等。
  - 版本迁移：UnpackV0/V1、DecryptV0/V1，LOAD_KEY_HANDLERS 表分派（h L155-158）。
- 内嵌 KeyFiles（L757-856）：拼 key/ 目录 .pub_key_v2 路径，lock/ 目录 .key_lock 上 flock（L794）跨进程互斥。

V2 密钥文件格式：version(1B)+nonce(12B)+HUKS 密文+HMAC-SHA256 前 8 字节。

## 3. 外部连接

向下：dlopen librelational_store_crypt.z.so（L570）＋dlsym 解析 CreateRdbCryptoDelegate（L749）与 GenerateRdbRandomNum（L161），返回 RDBCrypto 接口（relational_store_crypt.h L40-47），由 HUKS 密钥服务实现，根密钥别名 "DistributedDataRdb"（h L174）；动态加载使主库与 HUKS 解耦。

向上（grep 实证）：rdb_store_config.cpp L406/L413（取钥入口）、sqlite_connection.cpp L851/L884（Rekey 轮换）、rdb_helper.cpp L144（删库清 key）。失败路径经 ReportCryptFault（L244）上报。

## 4. 数据流：加密库打开全流程

1. 取钥：RdbStoreConfig::GenerateEncryptedKey（rdb_store_config.cpp L404-427）→Init(bundleName) 预热代理（GetDelegate L252 懒加载）→GetRdbPassword(path, PUB_KEY_FILE)，key 存入 config 内存。
2. GetRdbPassword（L486）：KeyFiles::Lock()→UpgradeKey（L415）把旧钥文件按 V2 重存→文件为空则生成 32B 随机 work key，EncryptWorkKey 产 12B nonce 以根密钥加密，落盘拼 HMAC。
3. 读回：Unpack 校验 HMAC（失败仅上报不阻断，L639）→DecryptWorkKey（L306）先全局根别名解密，失败把 bundle 名追加到根别名重试（L321-334）——解决应用改包名后旧钥打不开。
4. 注入：SqliteConnection::Open→SetEncrypt（sqlite_connection.cpp L1045）→sqlite3_key（L1104），PRAGMA version 验证解密（L1114-1118）。
5. 复用与轮换：明文 key 驻留 config，后续读连接直接取用不再读密钥文件；sqlite3_rekey 成功后 ChangeKeyFile 把 .new 转正。

## 5. 设计决策

- HUKS vs 本地存钥：直接存密钥文件等于锁钥匙同放；本方案磁盘只有密文，根密钥不出 TEE。代价是开库多一次 IPC，故 key 缓存于 config 供连接复用。
- 版本管理：V0（nonce 固定串）→V1（magic 0x6B6B6B6B＋nonce）→V2（加 HMAC）。UpgradeKey 惰性迁移，新版本只需 handler 表加一行。
- SaveSecretKey 时机：只在文件缺失时生成（L492-498），已有库绝不换 key——换了老数据全打不开；迁移换的只是外层封装。
- 内存卫生：析构委托擦除（L180、L698）＋退出路径清零，纵深防御。

## 6. 新人提示

- 切入点：GetRdbPassword（L486）是唯一读入口，沿 L486→L172→L285→L216 下钻覆盖写路径；注入点对照 sqlite_connection.cpp L1045-1118。
- 易错点：①加密库降级：V2 密钥文件老系统解析不了，降级前需 RekeyToPlainText（L928-947）并 DelAllKeyFiles；②HMAC 校验失败只上报不拒绝（L637-642）；③删库忘调 DelAllKeyFiles 残留孤儿密钥；④无 crypt 动态库时取钥返回空，开库报错而非崩溃。
- 测试：test/native/rdb/unittest/ 下 rdb_security_manager_test、rdb_encrypt_decrypt_test、rdb_encrypt_upgrade_test。
