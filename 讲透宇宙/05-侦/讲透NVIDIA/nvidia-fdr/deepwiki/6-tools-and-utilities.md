<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-fdr · page 6 Tools and Utilities · fetched 2026-10-26 -->

# Tools and Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [fdrtool/catalog/catalog.py](fdrtool/catalog/catalog.py)
- [fdrtool/catalog/json.py](fdrtool/catalog/json.py)
- [fdrtool/fdrtool.py](fdrtool/fdrtool.py)
- [tools/fdr_dump.sh](tools/fdr_dump.sh)

</details>



## Purpose and Scope

This page provides an overview of the command-line tools used to collect, export, and analyze FDR telemetry data. The FDR system includes three primary utility components that work together to extract binary logs from the HMC and convert them into human-readable or database formats for analysis.

For detailed configuration of data collection parameters, see [Platform Configuration](#5). For information about the binary storage format that these tools decode, see [Storage Format and Protobuf](#3.3).

## Tool Architecture

The FDR tooling ecosystem consists of three main components that operate in sequence:

```mermaid
graph TB
    subgraph "On HMC/BMC"
        FDR_SVC["nvidia-fdr service<br/>Collects telemetry"]
        LOGS["/var/emmc/fdr/<br/>Binary protobuf logs"]
        DUMP_SCRIPT["fdr_dump.sh<br/>Bash collection script"]
        
        FDR_SVC -->|"writes"| LOGS
        LOGS -->|"packages"| DUMP_SCRIPT
    end
    
    subgraph "Collection Methods"
        REDFISH["Redfish API<br/>/redfish/v1/.../FDR/"]
        SCP["Direct SCP/SSH<br/>Manual retrieval"]
        
        DUMP_SCRIPT -->|"exposed via"| REDFISH
        LOGS -->|"accessible via"| SCP
    end
    
    subgraph "Analysis Host"
        FDRTOOL["nvidia-fdrtool<br/>fdrtool/fdrtool.py"]
        TAR_FILE["HMC_ENV_SN_timestamp.tar.xz<br/>Compressed archive"]
        
        REDFISH -->|"downloads"| FDRTOOL
        SCP -->|"provides"| TAR_FILE
        
        FDRTOOL -->|"extracts"| TAR_FILE
    end
    
    subgraph "Decoding Pipeline"
        CATALOG_SYS["Catalog class<br/>fdrtool/catalog/catalog.py"]
        ENTRY_TYPES["CatalogEntry subclasses<br/>JSONCatalogEntry<br/>InfluxDBCatalogEntry<br/>SQLiteDBCatalogEntry"]
        
        TAR_FILE -->|"decoded by"| CATALOG_SYS
        CATALOG_SYS -->|"creates"| ENTRY_TYPES
    end
    
    subgraph "Output Formats"
        JSON_OUT["JSON Files<br/>Human-readable logs"]
        INFLUX_OUT["InfluxDB<br/>Time-series database"]
        SQLITE_OUT["SQLite Database<br/>Relational queries"]
        
        ENTRY_TYPES -->|"writes"| JSON_OUT
        ENTRY_TYPES -->|"writes"| INFLUX_OUT
        ENTRY_TYPES -->|"writes"| SQLITE_OUT
    end
    
    classDef onDevice fill:#f9f9f9
    classDef collection fill:#e8f4f8
    classDef analysis fill:#f0e8f8
    classDef decode fill:#fff4e8
    classDef output fill:#e8f8e8
    
    class FDR_SVC,LOGS,DUMP_SCRIPT onDevice
    class REDFISH,SCP,FDRTOOL,TAR_FILE collection
    class CATALOG_SYS,ENTRY_TYPES decode
    class JSON_OUT,INFLUX_OUT,SQLITE_OUT output
```

**Sources:** [tools/fdr_dump.sh:1-475](), [fdrtool/fdrtool.py:1-587](), [fdrtool/catalog/catalog.py:1-556]()

## Component Overview

### fdr_dump.sh - On-Device Collection Script

The `fdr_dump.sh` script runs on the HMC/BMC and is responsible for packaging FDR logs into a compressed archive. This script is typically invoked automatically by the Redfish API but can also be run manually.

| Feature | Description |
|---------|-------------|
| **Location** | [tools/fdr_dump.sh]() |
| **Execution Context** | Runs on HMC/BMC as root |
| **Primary Function** | `main()` at [tools/fdr_dump.sh:214-340]() |
| **Key Operations** | Time-range filtering, size limit enforcement, tar creation |
| **Output** | `obmcdump_<id>_<timestamp>.tar` file |

Key capabilities:
- **Time-range filtering**: Collects logs between specified start/end times using `-s` and `-e` options
- **Size management**: Enforces maximum dump size via `-m` option using `check_size_and_add()` at [tools/fdr_dump.sh:93-160]()
- **File selection**: Prioritizes recent directories and preserves `*.others.dat` files from oldest directories per boot cycle
- **Manifest generation**: Creates `fdr_manifest.txt` with system metadata via `create_manifest_file()` at [tools/fdr_dump.sh:162-198]()
- **Cleanup actions**: Supports `clean` and `genbirthcert` operations via `-a` option

**Sources:** [tools/fdr_dump.sh:1-475]()

### nvidia-fdrtool - Collection and Decoding Tool

The `nvidia-fdrtool` Python application provides a unified interface for both collecting logs from the HMC (via Redfish) and decoding them into various output formats. This is the primary tool used by end users.

| Component | Implementation |
|-----------|----------------|
| **Main Entry Point** | `main()` at [fdrtool/fdrtool.py:153-369]() |
| **Collection Logic** | `CollectFdrDump()` at [fdrtool/fdrtool.py:381-529]() |
| **Redfish Interface** | Uses `python-redfish-library` |
| **Decoding Orchestration** | `dumpCollection()` at [fdrtool/fdrtool.py:43-66]() |
| **Archive Extraction** | `decodingDump()` at [fdrtool/fdrtool.py:83-132]() |

**Sources:** [fdrtool/fdrtool.py:1-587]()

### Catalog System - Binary Decoding Infrastructure

The Catalog system is the core decoding engine that converts binary protobuf logs into structured data. It uses a factory pattern to create format-specific `CatalogEntry` objects.

| Class | Purpose | File Location |
|-------|---------|---------------|
| `Catalog` | Main orchestrator for decoding all files | [fdrtool/catalog/catalog.py:64-296]() |
| `CatalogEntry` | Base class for decoded messages | [fdrtool/catalog/catalog.py:301-556]() |
| `JSONCatalogEntry` | JSON-specific decoding | [fdrtool/catalog/json.py:24-126]() |
| `InfluxDBCatalogEntry` | InfluxDB line protocol | Referenced in [fdrtool/catalog/catalog.py:150-151]() |
| `SQLiteDBCatalogEntry` | SQLite database writes | Referenced in [fdrtool/catalog/catalog.py:152-154]() |

**Sources:** [fdrtool/catalog/catalog.py:1-556](), [fdrtool/catalog/json.py:1-132]()

## Collection and Export Workflow

```mermaid
sequenceDiagram
    participant User
    participant FDRTOOL as "nvidia-fdrtool<br/>fdrtool.py"
    participant REDFISH as "Redfish API<br/>/redfish/v1/Systems/.../FDR"
    participant HMC as "HMC System"
    participant DUMP_SH as "fdr_dump.sh"
    participant FDR_LOGS as "/var/emmc/fdr/"
    
    User->>FDRTOOL: Execute with --ip, --username, --password
    FDRTOOL->>REDFISH: POST CollectDiagnosticData<br/>CollectFdrDump()
    REDFISH->>DUMP_SH: Invoke with arguments
    DUMP_SH->>FDR_LOGS: Read BootCount directories
    DUMP_SH->>DUMP_SH: check_size_and_add()<br/>Filter by time/size
    DUMP_SH->>DUMP_SH: create_manifest_file()<br/>Add metadata
    DUMP_SH->>DUMP_SH: tar --create<br/>Create archive
    DUMP_SH->>REDFISH: Return tar file path
    REDFISH->>REDFISH: Task State = "Completed"
    FDRTOOL->>REDFISH: Monitor task.is_processing
    FDRTOOL->>REDFISH: GET .../attachment<br/>Download tar
    REDFISH->>FDRTOOL: Return tar.xz file
    FDRTOOL->>User: Save to ./tmp/<br/>HMC_ENV_SN_timestamp.tar.xz
```

**Sources:** [fdrtool/fdrtool.py:381-529](), [tools/fdr_dump.sh:214-340]()

### Collection Options

The `CollectFdrDump()` function at [fdrtool/fdrtool.py:381-529]() supports the following workflow:

1. **Authentication**: Logs into Redfish using `redfish.redfish_client()` with basic auth
2. **Service Check**: Verifies FDR service is enabled via `CheckIfNvidaFdrIsActive()` at [fdrtool/fdrtool.py:371-379]()
3. **Dump Trigger**: POSTs to `/redfish/v1/Systems/HGX_Baseboard_0/LogServices/FDR/Actions/LogService.CollectDiagnosticData/`
4. **Task Monitoring**: Polls task status using `response.monitor()` until completion
5. **Download**: Retrieves archive from task's `Payload.HttpHeaders.Location` with `/attachment` suffix
6. **Naming**: Saves as `HMC_<env>_SN<serial>_<timestamp>.tar.xz` at [fdrtool/fdrtool.py:477]()

**Sources:** [fdrtool/fdrtool.py:381-529]()

## Decoding Pipeline Architecture

```mermaid
graph TB
    subgraph "Input Processing"
        TAR["tar.xz Archive"]
        EXTRACT["decodingDump()<br/>fdrtool.py:83-132"]
        EXTRACTED["./fdr_logs/<br/>Extracted directory"]
        
        TAR -->|"tarfile.open()"| EXTRACT
        EXTRACT -->|"extract()"| EXTRACTED
    end
    
    subgraph "Catalog Initialization"
        CATALOG["Catalog.__init__()<br/>catalog.py:65-83"]
        VERSION_CHECK["DecodeErrorEvents()<br/>catalog.py:85-101"]
        PARAM_DESC["CreateParamDescriptions()<br/>catalog.py:257-290"]
        
        EXTRACTED --> CATALOG
        CATALOG --> VERSION_CHECK
        CATALOG --> PARAM_DESC
        
        VERSION_CHECK -->|"Validates DataDirFormatVersion"| VERSION_CHECK
        PARAM_DESC -->|"Builds ParamIDClassDict<br/>ParamIDNameDict"| PARAM_DESC
    end
    
    subgraph "File Decoding Loop"
        CREATE_CAT["CreateCatalog()<br/>catalog.py:111-130"]
        WALK["os.walk(log_dir)<br/>Find *.dat files"]
        DECODE_FILE["decode_binary_file()<br/>catalog.py:139-165"]
        
        PARAM_DESC --> CREATE_CAT
        CREATE_CAT --> WALK
        WALK -->|"for each .dat file"| DECODE_FILE
    end
    
    subgraph "Format-Specific Decoding"
        FACTORY{"decode_format?"}
        JSON_ENTRY["JSONCatalogEntry<br/>json.py:24-126"]
        INFLUX_ENTRY["InfluxDBCatalogEntry<br/>catalog.py:150-151"]
        SQLITE_ENTRY["SQLiteDBCatalogEntry<br/>catalog.py:152-154"]
        
        DECODE_FILE --> FACTORY
        FACTORY -->|"JSON"| JSON_ENTRY
        FACTORY -->|"INFLUX"| INFLUX_ENTRY
        FACTORY -->|"SQLITE"| SQLITE_ENTRY
    end
    
    subgraph "Binary Parsing"
        DELIM_CHECK{"length_delimited?"}
        ZERO_DELIM["decode_zero_delimited_binary()<br/>catalog.py:386-409"]
        LEN_DELIM["decode_length_delimited_binary()<br/>catalog.py:358-384"]
        PROTOBUF["ParseFromString()<br/>fdr_schema.fdr_*"]
        
        JSON_ENTRY --> DELIM_CHECK
        INFLUX_ENTRY --> DELIM_CHECK
        SQLITE_ENTRY --> DELIM_CHECK
        
        DELIM_CHECK -->|"False (default)"| ZERO_DELIM
        DELIM_CHECK -->|"True"| LEN_DELIM
        
        ZERO_DELIM -->|"cobsr.decode()"| PROTOBUF
        LEN_DELIM -->|"_DecodeVarint32()"| PROTOBUF
    end
    
    subgraph "Message Processing"
        ADD_MSG["AddMessage()<br/>json.py:31-104"]
        ENTRIES["CatalogEntries dict<br/>Grouped by message type"]
        
        PROTOBUF --> ADD_MSG
        ADD_MSG -->|"Appends to messages list"| ENTRIES
    end
    
    subgraph "Output Writing"
        WRITE_ALL["WriteAllEntries()<br/>catalog.py:223-255"]
        WRITE_ENTRY["WriteEntry()<br/>json.py:120-122"]
        OUTPUT["Output Files<br/>JSON/InfluxDB/SQLite"]
        
        ENTRIES --> WRITE_ALL
        WRITE_ALL -->|"for each entry"| WRITE_ENTRY
        WRITE_ENTRY --> OUTPUT
    end
```

**Sources:** [fdrtool/fdrtool.py:83-132](), [fdrtool/catalog/catalog.py:64-296](), [fdrtool/catalog/json.py:24-126]()

### Decoding Process Details

The `Catalog` class orchestrates the entire decoding process:

1. **Initialization** ([catalog.py:65-83]()):
   - Sets `decode_format` (JSON/INFLUX/SQLITE)
   - Determines binary delimiter type (`length_delimited` flag)
   - Initializes `CatalogEntries` dictionary keyed by protobuf message type

2. **Version Validation** ([catalog.py:85-101]()):
   - Decodes `BootEvent.dat` file
   - Checks `DataDirFormatVersion` field equals "2"
   - Raises `VersionMisMatch` exception if incompatible

3. **Parameter Description Loading** ([catalog.py:257-290]()):
   - Decodes `ParamDescription.dat` file
   - Builds `ParamIDClassDict`: maps ParamID → ParamClass
   - Builds `ParamIDNameDict`: maps (CompClass, ParamID) → ParamName
   - Creates nested `ParamDescription` dictionary structure

4. **File Walking and Decoding** ([catalog.py:111-130]()):
   - Uses `os.walk()` to find all `.dat` files
   - Skips `ParamDescription.dat` and `BootEvent.dat` (already processed)
   - Calls `decode_binary_file()` for each remaining file
   - Progress tracked with `tqdm` progress bar

5. **Binary Format Handling** ([catalog.py:358-409]()):
   - **Zero-delimited** (default): Splits on `\x00`, applies COBS-R decoding via `cobsr.decode()`
   - **Length-delimited**: Reads varint32 length prefix, extracts exact message bytes

6. **Protobuf Parsing** ([catalog.py:368-383]()):
   - Determines message type from filename extension:
     - `*.stat.dat` → `fdr_stat`
     - `ParamDescription.dat` → `fdr_params`
     - `BookOfErrors.dat` → `fdr_book_of_errors`
     - `Compactor.dat` → `fdr_compactor_bookkeep`
     - `BootEvent.dat` → `fdr_boot_event`
     - `Event_*.dat` → `fdr_event_details`
     - Default → `fdr_sample`
   - Calls `ParseFromString()` on appropriate protobuf message class

**Sources:** [fdrtool/catalog/catalog.py:64-296](), [fdrtool/catalog/catalog.py:301-556]()

## Output Format Handling

### JSON Output (`JSONCatalogEntry`)

The JSON output format is designed for human readability and post-processing with standard tools.

```mermaid
graph LR
    subgraph "JSONCatalogEntry Processing"
        PROTO_MSG["Protobuf Message<br/>fdr_schema.fdr_sample"]
        TO_JSON["protobuf_json_format<br/>.MessageToJson()"]
        ENHANCE["Enhance JSON<br/>json.py:31-104"]
        APPEND_MSG["Append to messages<br/>list"]
        WRITE["WriteEntry()<br/>json.py:120-122"]
        FILE["JSON File<br/>Original filepath"]
        
        PROTO_MSG --> TO_JSON
        TO_JSON --> ENHANCE
        ENHANCE --> APPEND_MSG
        APPEND_MSG --> WRITE
        WRITE --> FILE
    end
    
    subgraph "JSON Enhancement (-kn flag)"
        ADD_NAME["Add ParamName field<br/>GetParamNameFromID()"]
        ADD_CLASS["Add ParamClass field<br/>GetParamClassFromName()"]
        ADD_COMP["Add CompClass field<br/>from filename"]
        
        ENHANCE --> ADD_NAME
        ENHANCE --> ADD_CLASS
        ENHANCE --> ADD_COMP
    end
```

When `--key_name` flag is provided, `JSONCatalogEntry.AddMessage()` at [fdrtool/catalog/json.py:31-104]() enriches each JSON message:

- **ParamName**: Looked up via `GetParamNameFromID()` at [fdrtool/catalog/catalog.py:423-457]()
- **ParamClass**: Looked up via `GetParamClassFromName()` at [fdrtool/catalog/catalog.py:459-495]()
- **CompClass**: Extracted from filename at [fdrtool/catalog/json.py:41-46]()

**Output Location**: Same directory structure as input, with JSON messages written to original filepath.

**Sources:** [fdrtool/catalog/json.py:24-126](), [fdrtool/catalog/catalog.py:423-495]()

### InfluxDB Output

InfluxDB output converts telemetry data into line protocol format for time-series database storage. The `InfluxDBCatalogEntry` class (referenced at [catalog.py:150-151]()) formats data as:

```
measurement,tag1=value1,tag2=value2 field1=value1,field2=value2 timestamp
```

**Connection Parameters**:
- `--influx_url`: Database host URL
- `--influx_org`: Organization name
- `--influx_token`: Authentication token

**Client Initialization**: `InfluxDBConnection` object created at [catalog.py:82]()

**Sources:** [fdrtool/catalog/catalog.py:80-83]()

### SQLite Output

SQLite output creates a relational database with predefined schema for complex queries.

**Schema Definition**: `FDR_TABLE_SCHEMA` dictionary at [catalog.py:34-44]() defines table structures:

| Table Name | Key Columns | Purpose |
|------------|-------------|---------|
| `CDT` | CompClass, CompID, CompLabel | Component definitions |
| `PDT` | ParamID, ParamName, ParamType | Parameter descriptions |
| `PVT` | TimeStamp, ParamID, ParamValue, BootId | Parameter values (time-series) |
| `PST` | FromTime, ToTime, ParamID, Min, Max, Avg | Parameter statistics |
| `BookOfErrors` | BootId, DeviceType, ErrorOccurTimeStamp | Error records |
| `BookKeeper` | CompactDirectory, compactStatus | Compaction metadata |
| `BootEvent` | EventTimeStamp, HMCBootCount | Boot events |
| `EventDetails` | EventTimeStamp, EventName, EventMessage | Detailed event information |

**Connection Management**:
- `SQLiteConnection` initialized at [catalog.py:83]()
- Database filename derived from baseboard serial number via `GetCatalogName()` at [catalog.py:187-215]()
- Append mode controlled by `--append` flag

**View Creation**: `CreateCombinedViews()` called at [catalog.py:248-249]() creates SQL views for convenient querying

**Sources:** [fdrtool/catalog/catalog.py:34-44](), [fdrtool/catalog/catalog.py:223-255]()

## Command-Line Interface Summary

### nvidia-fdrtool Usage Patterns

**Basic Collection and JSON Decoding**:
```bash
nvidia-fdrtool --ip https://HMC_IP --username root --password PASSWORD --json
```

**Use Local Archive**:
```bash
nvidia-fdrtool --use_local --local_file /path/to/dump.tar.xz --json
```

**SQLite Database Creation**:
```bash
nvidia-fdrtool --ip https://HMC_IP --username root --password PASSWORD --sqlite
```

**InfluxDB Upload**:
```bash
nvidia-fdrtool --ip https://HMC_IP --username root --password PASSWORD \
  --influx --influx_url http://influx:8086 --influx_org myorg --influx_token TOKEN
```

**Key Name Resolution**:
```bash
nvidia-fdrtool --use_local --local_file dump.tar.xz --json --key_name
```

**Arguments Table**:

| Argument | Required | Purpose | Example |
|----------|----------|---------|---------|
| `--ip` | Yes (unless `--use_local`) | HMC IP address | `https://10.20.30.40` |
| `--username` | Yes (unless `--use_local`) | Redfish username | `root` |
| `--password` | Yes (unless `--use_local`) | Redfish password | `0penBmc` |
| `--use_local` | No | Use local tar file | Flag only |
| `--local_file` | Yes (if `--use_local`) | Path to tar archive | `/tmp/dump.tar.xz` |
| `--json` | One required | JSON output format | Flag only |
| `--influx` | One required | InfluxDB output | Flag only |
| `--sqlite` | One required | SQLite output | Flag only |
| `--key_name` | No | Add ParamName to JSON | Flag only |
| `--append` | No | Append to existing SQLite DB | Flag only |
| `--log_root_dir` | No | Extract directory | `./fdr_logs/` (default) |

**Sources:** [fdrtool/fdrtool.py:169-221]()

### fdr_dump.sh Usage Patterns

The `fdr_dump.sh` script is typically invoked by Redfish but can be run manually:

**Basic Collection**:
```bash
/usr/bin/fdr_dump.sh -p /tmp/dumps -i 00001
```

**Time-Range Filtering**:
```bash
/usr/bin/fdr_dump.sh -p /tmp/dumps -s "2024-01-01 00:00:00 00:00" \
  -e "2024-01-02 00:00:00 00:00" -m 500000000
```

**Clean Action**:
```bash
/usr/bin/fdr_dump.sh -p /tmp/dumps -a clean
```

**Arguments**:

| Argument | Default | Purpose |
|----------|---------|---------|
| `-p` | Required | Output directory path |
| `-i` | `00000000` | Dump ID for filename |
| `-a` | `collect` | Action: `collect`, `clean`, or `genbirthcert` |
| `-s` | `0` | Start time (ISO8601) |
| `-e` | Current time | End time (ISO8601) |
| `-m` | `1000000000` | Max dump size in bytes |
| `-S` | Empty | Extended source information |

**Sources:** [tools/fdr_dump.sh:26-38](), [tools/fdr_dump.sh:343-398]()

## Common Workflows

### Workflow 1: Routine Telemetry Collection

```mermaid
graph LR
    START[("User wants<br/>telemetry data")]
    RUN["Run nvidia-fdrtool<br/>with --ip, --json"]
    WAIT["Wait for Redfish<br/>collection task"]
    EXTRACT["Tool extracts<br/>tar archive"]
    DECODE["Catalog.CreateCatalog()<br/>decodes binary"]
    WRITE["WriteAllEntries()<br/>writes JSON"]
    ANALYZE[("Analyze JSON<br/>with scripts/tools")]
    
    START --> RUN
    RUN --> WAIT
    WAIT --> EXTRACT
    EXTRACT --> DECODE
    DECODE --> WRITE
    WRITE --> ANALYZE
```

**Sources:** [fdrtool/fdrtool.py:153-369]()

### Workflow 2: Time-Series Database Population

```mermaid
graph LR
    START[("Populate InfluxDB<br/>for dashboards")]
    COLLECT["nvidia-fdrtool --influx<br/>--influx_url, --influx_org"]
    REDFISH["CollectFdrDump()<br/>Download from HMC"]
    CATALOG["Catalog.__init__()<br/>decode_format=INFLUX"]
    INFLUX_ENTRY["InfluxDBCatalogEntry<br/>Format line protocol"]
    WRITE["InfluxDBConnection.write()<br/>Upload to InfluxDB"]
    VISUALIZE[("Create Grafana<br/>dashboards")]
    
    START --> COLLECT
    COLLECT --> REDFISH
    REDFISH --> CATALOG
    CATALOG --> INFLUX_ENTRY
    INFLUX_ENTRY --> WRITE
    WRITE --> VISUALIZE
```

**Sources:** [fdrtool/fdrtool.py:153-369](), [fdrtool/catalog/catalog.py:80-83]()

### Workflow 3: Offline Analysis with SQLite

```mermaid
graph LR
    START[("Analyze archived<br/>telemetry offline")]
    LOCAL["nvidia-fdrtool --use_local<br/>--local_file dump.tar.xz"]
    SQLITE["--sqlite flag<br/>SQLiteDBCatalogEntry"]
    TABLES["Create FDR_TABLE_SCHEMA<br/>PVT, PST, BookOfErrors, etc."]
    VIEWS["CreateCombinedViews()<br/>SQL views for queries"]
    QUERY[("Run SQL queries<br/>on telemetry.db")]
    
    START --> LOCAL
    LOCAL --> SQLITE
    SQLITE --> TABLES
    TABLES --> VIEWS
    VIEWS --> QUERY
```

**Sources:** [fdrtool/fdrtool.py:153-369](), [fdrtool/catalog/catalog.py:34-44](), [fdrtool/catalog/catalog.py:246-249]()

## File and Directory Conventions

### Archive Structure

A typical FDR dump archive extracted by `decodingDump()` at [fdrtool/fdrtool.py:83-132]() contains:

```
fdr/
├── Bookkeeper/
│   ├── BirthCertificate.tar            # Initial system state (immutable)
│   ├── BookOfErrors.dat                # Error log (protobuf)
│   ├── Compactor.dat                   # Compaction metadata
│   └── BootEvent.dat                   # Boot event records
├── BootCount_<N>_<timestamp>/          # Per-boot telemetry directories
│   ├── ParamDescription.dat            # Parameter metadata (required)
│   ├── GPU.0_SXM.sensors.dat          # GPU sensor data
│   ├── GPU.0_SXM.sensors.stat.dat     # GPU statistics
│   ├── GPU.0_SXM.sensors.hifi.dat     # High-fidelity error data
│   ├── NIC.0_ConnectX7.sensors.dat    # NIC telemetry
│   ├── Baseboard.0.others.dat         # Baseboard configuration
│   └── GPU.0_SXM.Event_<timestamp>.dat # Event details
├── fdr_manifest.txt                    # Dump metadata
├── fdr_ppf_*.yaml                      # Platform profile file
└── journalctl_u_nvidia-fdr.output     # Service logs
```

### File Type Identification

The `CatalogEntry.__init__()` method at [catalog.py:302-330]() determines message type from filename:

- Ends with `.stat.dat` → `PROTO_MSG_TYPE.fdr_stat`
- Ends with `ParamDescription.dat` → `PROTO_MSG_TYPE.fdr_params`
- Ends with `BookOfErrors.dat` → `PROTO_MSG_TYPE.fdr_book_of_errors`
- Ends with `Compactor.dat` → `PROTO_MSG_TYPE.fdr_compactor_bookkeep`
- Ends with `BootEvent.dat` → `PROTO_MSG_TYPE.fdr_boot_event`
- Contains `.Event_` → `PROTO_MSG_TYPE.fdr_event_details`
- All others → `PROTO_MSG_TYPE.fdr_sample`

### Component and Parameter ID Extraction

Filename parsing at [catalog.py:306-309]():
- Split on `.` delimiter
- `compClass` = first field (e.g., "GPU", "NIC", "Baseboard")
- `compID` = last part of second field after `_` (e.g., "0", "1")
- `bootid` = extracted from directory path via `parse_bootid()` at [catalog.py:518-536]()

**Sources:** [fdrtool/catalog/catalog.py:302-330](), [fdrtool/catalog/catalog.py:518-536]()

---

