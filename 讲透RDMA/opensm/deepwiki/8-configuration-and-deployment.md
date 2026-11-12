<!-- source: DeepWiki mcp.deepwiki.com · repo linux-rdma/opensm · page 8 Configuration and Deployment · fetched 2026-11-11 -->

# Configuration and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile.am](Makefile.am)
- [complib/Makefile.am](complib/Makefile.am)
- [include/opensm/osm_config.h.in](include/opensm/osm_config.h.in)
- [libvendor/Makefile.am](libvendor/Makefile.am)
- [opensm.spec.in](opensm.spec.in)
- [opensm/Makefile.am](opensm/Makefile.am)
- [osmeventplugin/Makefile.am](osmeventplugin/Makefile.am)
- [osmtest/Makefile.am](osmtest/Makefile.am)
- [scripts/opensm.init.in](scripts/opensm.init.in)
- [scripts/opensm.sysconfig](scripts/opensm.sysconfig)
- [scripts/redhat-opensm.init.in](scripts/redhat-opensm.init.in)
- [scripts/sldd.sh.in](scripts/sldd.sh.in)

</details>



This document covers how OpenSM is built, configured, packaged, and deployed in production environments. It details the autotools-based build system, configuration options, RPM packaging, and various deployment scenarios including single-node and multi-node cluster configurations.

For information about the core OpenSM architecture and components, see [Core Architecture](#2). For management and monitoring tools, see [Testing and Management Tools](#9).

## Build System Overview

OpenSM uses a standard autotools-based build system with separate libraries and components built in dependency order. The build produces several shared libraries and the main OpenSM executable.

### Build Dependencies and Structure

```mermaid
graph TB
    subgraph "External Dependencies"
        UMAD["libibumad-devel"]
        PTHREAD["libpthread"]
        BISON["bison"]
        FLEX["flex"] 
    end
    
    subgraph "OpenSM Libraries (Built in Order)"
        COMPLIB["libosmcomp<br/>Component Library"]
        LIBOPENSM["libopensm<br/>Core SM Library"]
        LIBVENDOR["libosmvendor<br/>Vendor Abstraction"]
    end
    
    subgraph "Main Components"
        OPENSM_BIN["opensm<br/>Main SM Binary"]
        OSMTEST["osmtest<br/>Test Framework"]
    end
    
    subgraph "Optional Components"
        EVENT_PLUGIN["libosmeventplugin<br/>Event Plugin"]
        ROUTING_PLUGIN["Routing Plugins"]
    end
    
    UMAD --> LIBVENDOR
    PTHREAD --> COMPLIB
    BISON --> OPENSM_BIN
    FLEX --> OPENSM_BIN
    
    COMPLIB --> LIBOPENSM
    COMPLIB --> LIBVENDOR
    LIBOPENSM --> LIBVENDOR
    LIBOPENSM --> OPENSM_BIN
    LIBVENDOR --> OPENSM_BIN
    COMPLIB --> OSMTEST
    LIBOPENSM --> OSMTEST
    LIBVENDOR --> OSMTEST
    
    COMPLIB --> EVENT_PLUGIN
    LIBOPENSM --> EVENT_PLUGIN
```

The build system enforces proper dependency order through the `SUBDIRS` specification in [Makefile.am:3](), ensuring libraries are built before components that depend on them.

**Sources:** [Makefile.am:1-28](), [opensm/Makefile.am:51](), [complib/Makefile.am:4](), [libvendor/Makefile.am:12](), [osmtest/Makefile.am:17]()

### Library Linking Structure

```mermaid
graph LR
    subgraph "opensm Binary"
        OPENSM_MAIN["main.c"]
    end
    
    subgraph "Link Dependencies"
        LOSMCOMP["-losmcomp"]
        LOPENSM["-lopensm"]  
        LOSMVENDOR["-losmvendor"]
        OSMV_LDADD["$(OSMV_LDADD)"]
        METIS_LDADD["$(METIS_LDADD)"]
    end
    
    OPENSM_MAIN --> LOSMCOMP
    OPENSM_MAIN --> LOPENSM
    OPENSM_MAIN --> LOSMVENDOR
    OPENSM_MAIN --> OSMV_LDADD
    OPENSM_MAIN --> METIS_LDADD
```

**Sources:** [opensm/Makefile.am:51]()

## Configuration System

OpenSM supports both compile-time and runtime configuration options to customize behavior for different deployment scenarios.

### Compile-Time Configuration Options

The build system provides several configure-time options that affect OpenSM functionality:

| Option | Purpose | Config Symbol |
|--------|---------|---------------|
| `--enable-console-socket` | Enable network console interface | `ENABLE_OSM_CONSOLE_SOCKET` |
| `--enable-perf-mgr` | Enable performance monitoring | `ENABLE_OSM_PERF_MGR` |
| `--enable-default-event-plugin` | Enable event notification plugin | `ENABLE_OSM_DEFAULT_EVENT_PLUGIN` |
| `--with-node-name-map` | Specify default node name mapping file | `HAVE_DEFAULT_NODENAME_MAP` |

**Sources:** [opensm.spec.in:3-26](), [include/opensm/osm_config.h.in:13-68]()

### Runtime Configuration Hierarchy

```mermaid
graph TB
    subgraph "Configuration Sources"
        SYSCONFIG["sysconfig/opensm<br/>System Configuration"]
        CACHE_DIR["/var/cache/opensm/<br/>Runtime Cache"]
        CONFIG_DIR["OPENSM_CONFIG_DIR<br/>Configuration Files"]
    end
    
    subgraph "Configuration Files"
        OPENSM_CONF["opensm.conf<br/>Main Config"]
        PARTITION_CONF["partitions.conf<br/>Partition Config"]
        QOS_POLICY["qos-policy.conf<br/>QoS Policy"]
        NODE_NAME_MAP["node-name-map<br/>Node Names"]
    end
    
    subgraph "Cache Files"
        GUID2LID["guid2lid<br/>GUID to LID mapping"]
        GUID2MKEY["guid2mkey<br/>GUID to M_Key mapping"]  
        NEIGHBORS["neighbors<br/>Topology cache"]
    end
    
    SYSCONFIG --> OPENSM_CONF
    CONFIG_DIR --> PARTITION_CONF
    CONFIG_DIR --> QOS_POLICY
    CONFIG_DIR --> NODE_NAME_MAP
    CACHE_DIR --> GUID2LID
    CACHE_DIR --> GUID2MKEY
    CACHE_DIR --> NEIGHBORS
```

**Sources:** [scripts/opensm.sysconfig:1-3](), [scripts/sldd.sh.in:52](), [include/opensm/osm_config.h.in:35-49]()

## RPM Packaging and Distribution

OpenSM is distributed as multiple RPM packages providing different components and development files.

### Package Structure

| Package | Contents | Purpose |
|---------|----------|---------|
| `opensm` | Main SM binary, man pages, init scripts | Core subnet manager functionality |
| `opensm-libs` | Shared libraries | Runtime libraries for SM and client applications |
| `opensm-devel` | Header files, .so symlinks | Development files for building SM plugins |
| `opensm-static` | Static libraries | Static linking support |

**Sources:** [opensm.spec.in:28-74]()

### Installation and Service Integration

```mermaid
graph TB
    subgraph "RPM Installation Process"
        RPM_INSTALL["rpm -i opensm"]
        CREATE_DIRS["mkdir /var/cache/opensm"]
        INSTALL_SCRIPTS["Install init scripts"]
        REGISTER_SERVICE["Register opensmd service"]
    end
    
    subgraph "Service Management"
        CHKCONFIG["chkconfig --add opensmd"]
        UPDATE_RC["update-rc.d opensmd defaults"]
        SYSTEMCTL["systemctl daemon-reload"]
    end
    
    subgraph "Runtime Files"
        INIT_SCRIPT["/etc/init.d/opensmd"]
        LOGROTATE["/etc/logrotate.d/opensm"]
        SLDD_SCRIPT["/usr/sbin/sldd.sh"]
        CACHE_DIR["/var/cache/opensm/"]
    end
    
    RPM_INSTALL --> CREATE_DIRS
    RPM_INSTALL --> INSTALL_SCRIPTS
    RPM_INSTALL --> REGISTER_SERVICE
    
    REGISTER_SERVICE --> CHKCONFIG
    REGISTER_SERVICE --> UPDATE_RC
    REGISTER_SERVICE --> SYSTEMCTL
    
    INSTALL_SCRIPTS --> INIT_SCRIPT
    INSTALL_SCRIPTS --> LOGROTATE
    INSTALL_SCRIPTS --> SLDD_SCRIPT
    CREATE_DIRS --> CACHE_DIR
```

**Sources:** [opensm.spec.in:89-122](), [opensm.spec.in:140-151]()

## Service Management and Init Scripts

OpenSM includes comprehensive init scripts for different Linux distributions with support for daemon mode operation.

### Service Control Interface

The init script provides standard service control operations:

| Command | Function | Implementation |
|---------|----------|----------------|
| `start` | Start OpenSM daemon | [scripts/opensm.init.in:76-90]() |
| `stop` | Stop OpenSM daemon | [scripts/opensm.init.in:92-102]() |
| `status` | Check service status | [scripts/opensm.init.in:104-112]() |
| `restart` | Restart service | [scripts/opensm.init.in:114-117]() |
| `resweep` | Trigger subnet resweep | [scripts/opensm.init.in:136-139]() |
| `rotatelog` | Rotate log files | [scripts/opensm.init.in:140-143]() |

**Sources:** [scripts/opensm.init.in:120-148]()

### Daemon Configuration

```mermaid
graph LR
    subgraph "Service Configuration"
        CONFIG_FILE["CONFIG=/etc/sysconfig/opensm"]
        OPTIONS["OPTIONS variable"]
        PIDFILE["pidfile=/var/run/opensm.pid"]
    end
    
    subgraph "Runtime Parameters"
        DAEMON_FLAG["--daemon"]
        PIDFILE_FLAG["--pidfile"]
        USER_OPTIONS["$OPTIONS"]
    end
    
    CONFIG_FILE --> OPTIONS
    OPTIONS --> USER_OPTIONS
    PIDFILE --> PIDFILE_FLAG
    
    subgraph "opensm Execution"
        OPENSM_CMD["opensm --daemon --pidfile $pidfile $OPTIONS"]
    end
    
    DAEMON_FLAG --> OPENSM_CMD
    PIDFILE_FLAG --> OPENSM_CMD
    USER_OPTIONS --> OPENSM_CMD
```

**Sources:** [scripts/opensm.init.in:66-82]()

## Cluster Deployment with SLDD

For multi-node OpenSM deployments, the Standby LID Distribution Daemon (SLDD) ensures consistent LID assignments across SM instances during failover scenarios.

### SLDD Architecture

```mermaid
graph TB
    subgraph "OpenSM Cluster"
        MASTER_SM["Master SM<br/>Node A"]
        STANDBY_SM1["Standby SM<br/>Node B"] 
        STANDBY_SM2["Standby SM<br/>Node C"]
    end
    
    subgraph "SLDD Cache Synchronization"
        CACHE_FILES["Cache Files:<br/>guid2lid<br/>guid2mkey<br/>neighbors"]
        SYNC_DAEMON["sldd.sh daemon"]
    end
    
    subgraph "Network Operations"
        SSH_SCP["SSH/SCP<br/>for file transfer"]
        PING_CHECK["Ping health checks"]
    end
    
    MASTER_SM --> CACHE_FILES
    CACHE_FILES --> SYNC_DAEMON
    SYNC_DAEMON --> SSH_SCP
    SYNC_DAEMON --> PING_CHECK
    
    SSH_SCP --> STANDBY_SM1
    SSH_SCP --> STANDBY_SM2
    PING_CHECK --> STANDBY_SM1
    PING_CHECK --> STANDBY_SM2
```

**Sources:** [scripts/sldd.sh.in:31-41](), [scripts/sldd.sh.in:52-54]()

### SLDD Configuration Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `OSM_HOSTS` | Empty | Space-separated list of SM nodes |
| `CACHE_FILE` | `/var/cache/opensm/guid2lid:/var/cache/opensm/guid2mkey:/var/cache/opensm/neighbors` | Cache files to synchronize |
| `RESCAN_TIME` | 60 seconds | Interval between sync operations |
| `RSH` | `/usr/bin/ssh` | Remote shell command |
| `RCP` | `/usr/bin/scp` | Remote copy command |

**Sources:** [scripts/sldd.sh.in:52-63](), [scripts/opensm.sysconfig:1-3]()

### SLDD Operation Flow

```mermaid
graph TB
    START["SLDD Start"]
    CHECK_HOSTS["Check OSM_HOSTS config"]
    LOCAL_HOST["Identify local host"]
    
    subgraph "Main Loop"
        CHECK_CACHE["Check cache file sizes"]
        COMPARE_REMOTE["Compare with remote caches"]
        UPDATE_DECISION{"Local cache larger?"}
        UPDATE_REMOTE["Update remote nodes"]
        UPDATE_LOCAL["Update from largest remote"]
        SLEEP["Sleep RESCAN_TIME"]
    end
    
    START --> CHECK_HOSTS
    CHECK_HOSTS --> LOCAL_HOST
    LOCAL_HOST --> CHECK_CACHE
    CHECK_CACHE --> COMPARE_REMOTE
    COMPARE_REMOTE --> UPDATE_DECISION
    UPDATE_DECISION -->|Yes| UPDATE_REMOTE
    UPDATE_DECISION -->|No| UPDATE_LOCAL
    UPDATE_REMOTE --> SLEEP
    UPDATE_LOCAL --> SLEEP
    SLEEP --> CHECK_CACHE
```

**Sources:** [scripts/sldd.sh.in:196-259]()

## Build Configuration Examples

### Debug Build Configuration

```bash
# Configure for debug build with all optional features
./configure \
    --enable-debug \
    --enable-console-socket \
    --enable-perf-mgr \
    --enable-default-event-plugin \
    --with-node-name-map=/etc/opensm/node-name-map
```

### Production Build Configuration

```bash
# Configure for production deployment
./configure \
    --disable-console-socket \
    --enable-perf-mgr \
    --disable-default-event-plugin \
    --with-opensm-config-dir=/etc/opensm
```

**Sources:** [opensm.spec.in:79-86]()

---

