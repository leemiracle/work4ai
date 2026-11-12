<!--
SPDX-FileCopyrightText: Copyright (c) 2022-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# S3 Backup System Documentation
## Complete Documentation Index

**Version:** 2.0.1 (with versions_ prefix strategy)  
**Last Updated:** November 7, 2025  

This has been tested by multiple users and in a production context however, not every scenario has been possible to test. Please work with this and notify of feature requests, bugs etc so we can improve. 

## 👀 Overview

Thanks for taking an interest in Backup Any Linux!

This set of scripts provides a user-driven backup solution for any Linux system, designed to backup data to S3-compatible storage. The system is ideal for automated nightly backups and prioritizes data safety with atomic operations and version history protection.

### Core Concept: User-Driven Backups

**Users choose what to backup** - no admin interaction required. Users simply place trigger files in their directories to opt-in to backups:

- **`backupthisdir.txt`** - Backs up only files in this specific directory (no subdirectories)
- **`backupalldirs.txt`** - Backs up all files and folders from this directory onward (recursive)

### How It Works

When a backup runs, the system:

1. **Discovers** - Scans mount points for trigger files (`backupthisdir.txt` or `backupalldirs.txt`)
2. **Analyzes** - Identifies new, modified, and deleted files using metadata and checksums
3. **Backs Up** - Uploads only new or changed files to S3 (incremental backups)
4. **Manages Versions** - Preserves deleted/modified files in a separate version history folder
5. **Cleanup** - Automatically removes old deleted files after a configurable retention period

### Key Features

- **Incremental backups** - Only transfers files that have changed
- **User-controlled** - Each user decides what to backup
- **No data loss design** - Nothing is permanently deleted immediately; all deleted and modified files are preserved in version history for recovery
- **Atomic operations** - State changes are performed atomically to ensure reliability and prevent corruption
- **Version history** - Deleted and modified files are retained for recovery
- **Configurable retention** - Control how long deleted files are kept
- **Production-tested** - Used successfully in real-world deployments
- **Flexible scheduling** - Run manually or via automated cron jobs

For detailed setup instructions, usage examples, and advanced features, see the documentation sections below.

**Upcoming features:**
- Exclude certain file types from backup e.g. .pem
- Additional state files to be backed up in S3 and associated checks

---

## 📚 Documentation Structure

This documentation is organized into three main categories:

### 🎯 [User Guide](docs/userguide) - For Users & Administrators
Start here if you want to **use** the backup system.

### 🔧 [Developer Guide](docs/developer) - For Developers & Maintainers
Start here if you want to **develop** or **maintain** the backup system.



---

## 🚀 Quick Start

**New Users:** Start with → [`docs/userguide/START_HERE.md`](docs/userguide/START_HERE.md)

**New Developers:** Start with → [`docs/developer/MODULAR_ARCHITECTURE.md`](docs/developer/MODULAR_ARCHITECTURE.md)

---

## 📖 User Guide Documentation

Perfect for system administrators, DevOps engineers, and end users.

| Document | Description | Audience |
|----------|-------------|----------|
| **[START_HERE.md](docs/userguide/START_HERE.md)** | 👈 **Begin here!** Quick onboarding guide | New users |
| **[GETTING_STARTED.md](docs/userguide/GETTING_STARTED.md)** | Comprehensive setup and first backup | All users |
| **[SIMPLE_USAGE.md](docs/userguide/SIMPLE_USAGE.md)** | Easy-to-follow usage examples | All users |

### What You'll Learn
- ✅ How to install and configure the backup system
- ✅ How to run your first backup
- ✅ How to restore files from backups
- ✅ How to schedule automated backups
- ✅ How to monitor backup status
- ✅ Troubleshooting common issues

---

## 🔧 Developer Documentation

Perfect for developers working on the codebase or integrating with the system.

### Core Architecture

| Document | Description | Focus |
|----------|-------------|-------|
| **[MODULAR_ARCHITECTURE.md](docs/developer/MODULAR_ARCHITECTURE.md)** | 👈 **Start here!** System architecture overview | Architecture |
| **[ARCHITECTURE_DIAGRAMS.md](docs/developer/ARCHITECTURE_DIAGRAMS.md)** | Visual architecture diagrams | Architecture |
| **[MODULE_CONSISTENCY_GUIDE.md](docs/developer/MODULE_CONSISTENCY_GUIDE.md)** | Module design patterns and standards | Development |
| **[LOGIC_FLOW_DIAGRAMS.md](docs/developer/LOGIC_FLOW_DIAGRAMS.md)** | Visual execution paths for all scenarios | Technical |

### Code Reference

| Document | Description | Focus |
|----------|-------------|-------|
| **[VARIABLE_FUNCTION_REFERENCE.md](docs/developer/VARIABLE_FUNCTION_REFERENCE.md)** | Complete variable and function index | Reference |
| **[DOCUMENTATION_GUIDE.md](docs/developer/DOCUMENTATION_GUIDE.md)** | Documentation standards and practices | Process |

### What You'll Learn
- ✅ Complete system architecture and design
- ✅ How each module works and interacts
- ✅ State management and file organization
- ✅ Detailed execution flows and logic paths
- ✅ Variable and function reference guide
- ✅ How to extend and maintain the system

---


---

## 🗺️ Documentation Roadmap

### What Document Should I Read?

```
┌─────────────────────────────────────────────────────────┐
│  I want to...                                           │
└─────────────────────────────────────────────────────────┘

📦 Use the backup system
   → docs/userguide/START_HERE.md
   → docs/userguide/GETTING_STARTED.md
   → docs/userguide/SIMPLE_USAGE.md
   
🔧 Understand the architecture
   → docs/developer/MODULAR_ARCHITECTURE.md
   → docs/developer/ARCHITECTURE_DIAGRAMS.md
   
📊 Understand execution flows
   → docs/developer/LOGIC_FLOW_DIAGRAMS.md
   → docs/developer/ARCHITECTURE_DIAGRAMS.md
   
🔍 Review code structure
   → docs/developer/VARIABLE_FUNCTION_REFERENCE.md
   → docs/developer/MODULE_CONSISTENCY_GUIDE.md
   
📝 Contribute documentation
   → docs/developer/DOCUMENTATION_GUIDE.md

```

---

## 📊 Key Features Documented

### Core Functionality
- ✅ Incremental backups with change detection
- ✅ S3 storage with intelligent organization
- ✅ State management with atomic operations
- ✅ Deleted file retention policies
- ✅ Separate version history (versions_* prefix)
- ✅ Forced alignment for orphaned objects
- ✅ Multi-platform support (Linux, macOS, Windows)


---

## 🔗 Related Resources

### Code Structure
```
/backup/
├── backup.sh           # Main entry point
├── lib/                # Core modules (9 modules)
│   ├── core.sh
│   ├── utils.sh
│   ├── config.sh
│   ├── state.sh
│   ├── filesystem.sh
│   ├── checksum.sh
│   ├── s3.sh
│   ├── backup.sh
│   ├── deletion.sh
│   ├── alignment.sh
│   └── state-backup.sh
├── scripts/            # Configuration and legacy
│   └── backup-config.conf
|   └── s3-inspect.sh 
└── docs/               # This documentation
```

---

## 📝 Documentation Standards

All documentation in this project follows these principles:

1. **User-First:** User guides are written for non-technical users
2. **Complete:** Developer docs include architecture, rationale, and examples
3. **Current:** Outdated docs are moved to archive, not deleted
4. **Organized:** Clear folder structure with purpose-driven categorization
5. **Accessible:** Quick reference and visual aids provided

---

## 🤝 Contributing

### For Users
If you find documentation unclear or incomplete:
1. Note the specific document and section
2. Describe what's confusing
3. Suggest improvements
4. Submit feedback to the development team

### For Developers
When adding features or fixing bugs:
1. Update relevant documentation in `docs/developer/`
2. Add user-facing docs to `docs/userguide/` if needed
3. Follow standards in `docs/developer/DOCUMENTATION_GUIDE.md`
4. Update this index if adding new documents

---

## 📞 Support

### Documentation Issues
- Unclear instructions? → Check `docs/userguide/` alternatives
- Technical details missing? → Check `docs/developer/` for in-depth info

### System Issues
- Configuration problems → `docs/userguide/GETTING_STARTED.md`
- Backup failures → `docs/userguide/SIMPLE_USAGE.md` troubleshooting section
- Development questions → `docs/developer/MODULAR_ARCHITECTURE.md`

---

## 🎯 Quick Links

**Most Common:**
- 🚀 [Get Started](docs/userguide/START_HERE.md)
- 📖 [User Guide](docs/userguide/GETTING_STARTED.md)
- 🔧 [Architecture](docs/developer/MODULAR_ARCHITECTURE.md)
- 📊 [Logic Flows](docs/developer/LOGIC_FLOW_DIAGRAMS.md)

**For Reference:**
- 🏗️ [Architecture Diagrams](docs/developer/ARCHITECTURE_DIAGRAMS.md)
- 📋 [Variable Reference](docs/developer/VARIABLE_FUNCTION_REFERENCE.md)
- 🔄 [Module Consistency](docs/developer/MODULE_CONSISTENCY_GUIDE.md)

---

## 📈 Documentation Metrics

| Category | Documents | Status |
|----------|-----------|--------|
| User Guide | 3 | ✅ Complete |
| Developer | 6 | ✅ Complete |
| **Total** | **9** | ✅ **Organized** |

---

**Last Review:** November 6, 2025  
**Documentation Version:** 2.0.1

---

## 🎉 You're All Set!

Choose your path:
- **Using the system?** → [`docs/userguide/START_HERE.md`](docs/userguide/START_HERE.md)
- **Developing/Maintaining?** → [`docs/developer/MODULAR_ARCHITECTURE.md`](docs/developer/MODULAR_ARCHITECTURE.md)

Happy backing up! 🚀
