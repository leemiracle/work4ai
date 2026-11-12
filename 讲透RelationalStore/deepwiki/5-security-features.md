> 来源: [https://deepwiki.com/openharmony/distributeddatamgr_relational_store/5-security-features](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/5-security-features)
> DeepWiki openharmony/distributeddatamgr_relational_store

# Security Features

  Relevant source files 
 - [frameworks/native/rdb/include/rdb_security_manager.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_security_manager.h)
 - [frameworks/native/rdb/include/sqlite_utils.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/sqlite_utils.h)
 - [frameworks/native/rdb/include/string_utils.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/string_utils.h)
 - [frameworks/native/rdb/include/trans_db.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/trans_db.h)
 - [frameworks/native/rdb/src/rdb_security_manager.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp)
 - [frameworks/native/rdb/src/rdb_sql_utils.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_sql_utils.cpp)
 - [frameworks/native/rdb/src/sqlite_utils.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_utils.cpp)
 - [frameworks/native/rdb/src/string_utils.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/string_utils.cpp)
 - [frameworks/native/rdb/src/trans_db.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/trans_db.cpp)
 - [interfaces/inner_api/rdb/include/rdb_sql_utils.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_sql_utils.h)
 - [test/js/rdb/unittest/src/RdbstoreEncryptionJsunit.test.js](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/rdb/unittest/src/RdbstoreEncryptionJsunit.test.js)
 - [test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js)
 - [test/native/rdb/BUILD.gn](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/BUILD.gn)
 - [test/native/rdb/unittest/rdb_step_result_get_row_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_step_result_get_row_test.cpp)
 - [test/native/rdb/unittest/rdb_store_impl_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_store_impl_test.cpp)
 - [test/native/rdb/unittest/rdb_utils_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_utils_test.cpp)
 - [test/native/rdb/unittest/sqlite_utils_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/sqlite_utils_test.cpp)
 
  This document describes the security features implemented in the OpenHarmony Relational Database Management System. The system includes comprehensive security mechanisms for data protection including database encryption, secure key management, and data anonymization.

 For information about the Security Manager implementation details, see [RDB Security Manager](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/5.1-rdb-security-manager).

 
## 1. Security Architecture Overview

 The security architecture of the Relational Database Management System is built on several key components that work together to ensure data confidentiality and integrity.

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_security_manager.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp) [frameworks/native/rdb/include/rdb_security_manager.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_security_manager.h)

 
## 2. Database Encryption

 The system supports full database encryption using industry-standard cryptographic algorithms. Database encryption protects data at rest, preventing unauthorized access even if the database file is compromised.

 
### 2.1 Encryption Algorithms

 The relational store supports multiple encryption algorithms:

 
```

```

 Sources: [frameworks/native/rdb/src/sqlite_utils.cpp287-327](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_utils.cpp#L287-L327) [test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js52-74](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js#L52-L74)

 
### 2.2 Encryption Configuration

 Applications can configure database encryption through the store configuration object. The following example shows encryption configuration in JavaScript:

 
```

```

 Sources: [test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js48-60](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js#L48-L60) [test/js/rdb/unittest/src/RdbstoreEncryptionJsunit.test.js25-41](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/rdb/unittest/src/RdbstoreEncryptionJsunit.test.js#L25-L41)

 
## 3. Key Management

 The system implements a two-tier key management approach to secure databases.

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_security_manager.cpp104-115](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L104-L115) [frameworks/native/rdb/src/rdb_security_manager.cpp287-383](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L287-L383) [frameworks/native/rdb/src/rdb_security_manager.cpp442-507](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L442-L507)

 
### 3.1 Root Key

 The Root Key is the master key that secures work keys. It is generated and stored using the Huawei Universal Key Service (HUKS), which provides hardware-backed security on supported devices.

 
 - Root keys are generated per application bundle
 - Root keys never leave the HUKS service
 - Root keys use AES-256-GCM for encryption
 
 Sources: [frameworks/native/rdb/src/rdb_security_manager.cpp279-329](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L279-L329) [frameworks/native/rdb/src/rdb_security_manager.cpp442-467](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L442-L467)

 
### 3.2 Work Keys

 Work Keys are used to encrypt the actual database files. They are encrypted using the Root Key and stored in key files.

 
 - Work keys are randomly generated
 - Work keys are stored in encrypted key files
 - Key rotation is supported for work keys
 
 Sources: [frameworks/native/rdb/src/rdb_security_manager.cpp216-225](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L216-L225) [frameworks/native/rdb/src/rdb_security_manager.cpp227-250](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L227-L250)

 
### 3.3 Key Files Management

 The system manages key files associated with database files:

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_security_manager.cpp609-674](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L609-L674) [frameworks/native/rdb/include/rdb_security_manager.h64-85](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_security_manager.h#L64-L85)

 
## 4. Data Protection Mechanisms

 The system implements several mechanisms to protect data beyond encryption.

 
### 4.1 Data Anonymization

 The system includes utilities for anonymizing sensitive data in logs and error messages, mainly implemented in `SqliteUtils`:

 
 - File paths are anonymized to prevent leaking user information
 - Database names containing personal identifiers are masked
 - Anonymous method preserves enough information for debugging while protecting PII
 
 
```

```

 Sources: [frameworks/native/rdb/src/sqlite_utils.cpp132-251](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_utils.cpp#L132-L251) [test/native/rdb/unittest/sqlite_utils_test.cpp42-190](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/sqlite_utils_test.cpp#L42-L190)

 
### 4.2 Security Levels

 The system supports different security levels for database files:

 
| Security Level | Description | Use Case |
|---|---|---|
| S1 | Standard security | General app data |
| S2 | Enhanced security | Sensitive user data |
| S3 | High security | Financial or health data |
| S4 | Maximum security | Critical system data |

 Sources: [test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js27-41](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js#L27-L41) [test/native/rdb/unittest/rdb_store_impl_test.cpp446-461](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_store_impl_test.cpp#L446-L461)

 
## 5. Encryption Implementation

 The encryption implementation uses a combination of HUKS API and SQLite crypto extensions.

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_security_manager.cpp374-383](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L374-L383) [frameworks/native/rdb/src/rdb_security_manager.cpp385-440](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L385-L440) [frameworks/native/rdb/src/rdb_security_manager.cpp528-560](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L528-L560)

 
### 5.1 Encryption and Decryption Process

 The encryption and decryption processes involve several steps:

 
 - **Encryption Process:**

 
 - Generate or retrieve the Root Key from HUKS
 - Generate a random Work Key
 - Encrypt the Work Key using the Root Key
 - Store the encrypted Work Key in a key file
 - Use the Work Key to encrypt the database
 - **Decryption Process:**

 
 - Retrieve the Root Key from HUKS
 - Read the encrypted Work Key from the key file
 - Decrypt the Work Key using the Root Key
 - Use the Work Key to decrypt the database
 
 Sources: [frameworks/native/rdb/src/rdb_security_manager.cpp331-383](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L331-L383) [frameworks/native/rdb/src/rdb_security_manager.cpp385-440](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_security_manager.cpp#L385-L440)

 
## 6. Security Best Practices

 The following best practices are recommended when using the security features:

 
 - **Always use encryption for sensitive data**

 
 - Enable encryption for databases containing PII or sensitive information
 - **Use appropriate security levels**

 
 - Match the security level to the sensitivity of the data
 - **Implement key rotation**

 
 - Periodically update encryption keys for long-lived databases
 - **Secure key material**

 
 - Never hardcode encryption keys in application code
 - Use secure key derivation from user authentication when possible
 - **Handle key files securely**

 
 - Don't backup or copy key files separately from databases
 - Delete key files when deleting databases
 
 Sources: [test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js384-486](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js#L384-L486) [test/native/rdb/unittest/rdb_encrypt_decrypt_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_encrypt_decrypt_test.cpp) (referenced but not shown in the provided files)

 
## 7. Limitations and Considerations

 When using database encryption, consider the following limitations:

 
 - **Performance Impact**

 
 - Encryption adds computational overhead
 - Consider performance impact for large databases or frequent operations
 - **Key Recovery**

 
 - No built-in recovery mechanism if keys are lost
 - Implement application-level backup/recovery strategies
 - **Cross-Device Sharing**

 
 - Encrypted databases require key sharing for cross-device scenarios
 - Use distributed database features with appropriate security configuration
 
 Sources: [test/native/rdb/unittest/rdb_distributed_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_distributed_test.cpp) (referenced but not shown in the provided files)

 
## 8. Configuration Reference

 This section provides a reference for security-related configuration options.

 
### 8.1 JavaScript API Configuration

 
| Option | Description | Default |
|---|---|---|
| encrypt | Enables or disables encryption | false |
| securityLevel | Security level (S1-S4) | SecurityLevel.S1 |
| cryptoParam.encryptionKey | Custom encryption key | N/A |
| cryptoParam.iterationCount | KDF iteration count | 10000 |
| cryptoParam.encryptionAlgo | Encryption algorithm | EncryptionAlgo.AES_256_GCM |
| cryptoParam.hmacAlgo | HMAC algorithm | HmacAlgo.SHA256 |
| cryptoParam.kdfAlgo | Key derivation function | KdfAlgo.KDF_SHA256 |
| cryptoParam.cryptoPageSize | Encryption page size | 1024 |

 Sources: [test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js48-74](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbstoreEncryptionJsunit.test.js#L48-L74)

 
### 8.2 Native API Configuration

 For native applications, the `RdbStoreConfig` class provides security configuration:

 
```

```

 Sources: [test/native/rdb/unittest/rdb_store_impl_test.cpp447-461](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_store_impl_test.cpp#L447-L461)
