# NVMesh 3.5.0 CLI Guide

<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

API Version: **18.0.0**

## Copyright and Trademark Information

Copyright 2026 NVIDIA All rights reserved.

Specifications are subject to change without notice.
NVMesh is a registered trademark of NVIDIA.
All other brands or products are trademarks or registered trademarks of their respective holders
and should be treated as such.

## Preface

This document describes the command-line interface of the NVMesh storage solution.
For more information on NVMesh, refer to the *NVMesh User Guide*.

**Audience** - Storage and application administration personnel responsible for
installing and deploying NVMesh.

## Introduction

The `nvmesh` CLI tool provides a command-line user interface to manage NVMesh.
It can be used to send one-line commands or write shell scripts, and it offers
an interactive shell.

`nvmesh` uses the NVMesh RESTful API, terminal command-line tools, and SSH for
day-to-day management and provisioning activities with homogeneous semantics.

The CLI tool interacts with the Management Servers using management's REST API.
The outputs from the CLI are strongly dependent on this API.
This document is based on management **API version 18.0.0**.

## Installation

Install the `nvmesh-utils` package, which should be available from the NVMesh
yum/apt repo:

```bash
sudo yum install nvmesh-utils    # RHEL/CentOS
sudo apt install nvmesh-utils    # Debian/Ubuntu
```

To start the NVMesh shell, run `nvmesh` in a terminal.

## Using the NVMesh CLI

### Prerequisites

Two configurations should be made initially:

1. Set definitions for accessing NVMesh Management using its REST API in
   `/etc/nvmesh/nvmesh.conf`. Typically, if the NVMesh client or NVMesh target
   have been configured for this machine, these will already be in place.
   Otherwise, set `_REST_SERVERS` and `_REST_AUTH_METHOD` per the instructions
   in the file.

2. Provide login credentials. Initially, `nvmesh` has no stored credentials.
   It requires management/API login information for an administrator account.
   Upon first launch, the tool will prompt for credentials:

   ```
   Management: management-host
   User: admin
   Password:
   ```

   Credentials are stored in `~/.nvmesh/`.

### Interactive vs CLI

All capabilities are available in two modes: **Interactive** and **CLI**.

#### CLI Mode

Invoke `nvmesh` with all required parameters on a single line:

```bash
nvmesh -m management-host volume show
nvmesh -m management-host volume create --name my-vol --capacity 100G --raid-level 1
nvmesh -m management-host client attach --id client-1 --volume my-vol
```

#### Interactive Mode

Invoke `nvmesh` with no additional arguments to enter the interactive shell:

```bash
$ nvmesh -m management-host
[management-host] volume show
[management-host] volume create --name my-vol --capacity 100G --raid-level 1
```

Interactive mode features:

- Use the `!` prefix to execute shell commands locally: `! ls -l`
- Use **Tab** for auto-completion of commands and arguments
- Navigate history with **Up/Down** arrows and search with **Ctrl+R**

### Command Structure

The full command structure is obtained with `nvmesh --help`, which provides the
first level of available commands and options.

Most commands represent NVMesh entities (volumes, drives, clients, etc.).
For every entity, there is a second level of commands that are operations on
that entity - for example:

```bash
nvmesh volume --help          # List volume operations
nvmesh volume create --help   # Help for 'volume create'
```

Common operations across entities:

| Operation | Description |
|-----------|-------------|
| `show`    | List instances (with optional filters and output formats) |
| `count`   | Show how many instances exist |
| `create`  | Create a new instance |
| `update`  | Modify properties of an existing instance |
| `delete`  | Delete one or more instances |
| `wait`    | Block until a property reaches a desired value |

---

## Command Reference

### Table of Contents

- [client](#client)
  - [client attach](#client-attach)
  - [client count](#client-count)
  - [client delete](#client-delete)
  - [client detach](#client-detach)
  - [client set-emulation-mode](#client-set-emulation-mode)
  - [client show](#client-show)
  - [client wait](#client-wait)
- [cluster](#cluster)
  - [cluster show](#cluster-show)
  - [cluster update-cluster-id](#cluster-update-cluster-id)
- [config-profile](#config-profile)
  - [config-profile apply](#config-profile-apply)
  - [config-profile count](#config-profile-count)
  - [config-profile create](#config-profile-create)
  - [config-profile delete](#config-profile-delete)
  - [config-profile show](#config-profile-show)
  - [config-profile update](#config-profile-update)
- [drive](#drive)
  - [drive count](#drive-count)
  - [drive delete](#drive-delete)
  - [drive evict](#drive-evict)
  - [drive exclude-nvme](#drive-exclude-nvme)
  - [drive format](#drive-format)
  - [drive include-nvme](#drive-include-nvme)
  - [drive reinstate](#drive-reinstate)
  - [drive show](#drive-show)
  - [drive wait](#drive-wait)
- [drive-class](#drive-class)
  - [drive-class count](#drive-class-count)
  - [drive-class create](#drive-class-create)
  - [drive-class delete](#drive-class-delete)
  - [drive-class show](#drive-class-show)
  - [drive-class update](#drive-class-update)
- [env](#env)
- [general-settings](#general-settings)
  - [general-settings show](#general-settings-show)
  - [general-settings update](#general-settings-update)
- [generate-docs](#generate-docs)
- [key-pair](#key-pair)
  - [key-pair count](#key-pair-count)
  - [key-pair create](#key-pair-create)
  - [key-pair delete](#key-pair-delete)
  - [key-pair download](#key-pair-download)
  - [key-pair show](#key-pair-show)
  - [key-pair update](#key-pair-update)
- [log](#log)
  - [log acknowledge](#log-acknowledge)
  - [log acknowledge-all](#log-acknowledge-all)
  - [log count](#log-count)
  - [log show](#log-show)
- [login](#login)
- [management](#management)
  - [management count](#management-count)
  - [management show](#management-show)
  - [management status](#management-status)
- [target](#target)
  - [target count](#target-count)
  - [target delete](#target-delete)
  - [target delete-nic](#target-delete-nic)
  - [target evict](#target-evict)
  - [target set-zone](#target-set-zone)
  - [target show](#target-show)
  - [target wait](#target-wait)
- [target-class](#target-class)
  - [target-class count](#target-class-count)
  - [target-class create](#target-class-create)
  - [target-class delete](#target-class-delete)
  - [target-class show](#target-class-show)
  - [target-class update](#target-class-update)
- [upgrade](#upgrade)
  - [upgrade count](#upgrade-count)
  - [upgrade create](#upgrade-create)
  - [upgrade delete](#upgrade-delete)
  - [upgrade resume](#upgrade-resume)
  - [upgrade show](#upgrade-show)
  - [upgrade skip-failed-machine](#upgrade-skip-failed-machine)
  - [upgrade start](#upgrade-start)
- [upgrade-agent](#upgrade-agent)
  - [upgrade-agent count](#upgrade-agent-count)
  - [upgrade-agent delete](#upgrade-agent-delete)
  - [upgrade-agent keepalive](#upgrade-agent-keepalive)
  - [upgrade-agent show](#upgrade-agent-show)
- [upgrade-step](#upgrade-step)
  - [upgrade-step count](#upgrade-step-count)
  - [upgrade-step mark-as-completed](#upgrade-step-mark-as-completed)
  - [upgrade-step set-breakpoint](#upgrade-step-set-breakpoint)
  - [upgrade-step show](#upgrade-step-show)
- [user](#user)
  - [user change-password](#user-change-password)
  - [user count](#user-count)
  - [user create](#user-create)
  - [user delete](#user-delete)
  - [user show](#user-show)
  - [user update](#user-update)
- [version](#version)
- [volume](#volume)
  - [volume add-passphrase](#volume-add-passphrase)
  - [volume count](#volume-count)
  - [volume create](#volume-create)
  - [volume delete](#volume-delete)
  - [volume delete-passphrase](#volume-delete-passphrase)
  - [volume extend](#volume-extend)
  - [volume init-encryption](#volume-init-encryption)
  - [volume rebuild](#volume-rebuild)
  - [volume rotate-passphrase](#volume-rotate-passphrase)
  - [volume show](#volume-show)
  - [volume update](#volume-update)
  - [volume wait](#volume-wait)
- [volume-security-group](#volume-security-group)
  - [volume-security-group count](#volume-security-group-count)
  - [volume-security-group create](#volume-security-group-create)
  - [volume-security-group delete](#volume-security-group-delete)
  - [volume-security-group show](#volume-security-group-show)
  - [volume-security-group update](#volume-security-group-update)
- [vpg](#vpg)
  - [vpg count](#vpg-count)
  - [vpg create](#vpg-create)
  - [vpg delete](#vpg-delete)
  - [vpg extend](#vpg-extend)
  - [vpg reclaim](#vpg-reclaim)
  - [vpg show](#vpg-show)
  - [vpg update](#vpg-update)

---

### client

#### client attach

_Attach one or more volumes to the specified client_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |
| `--volume` | id/name | Yes | Volume |  |  |
| `--mode` | text |  | Mode (options: ['SHARED_READ_ONLY', 'SHARED_READ_WRITE', 'EXCLUSIVE_READ_WRITE']) |  | SHARED_READ_WRITE |
| `--reservation-version` | integer |  | Reservation Version |  |  |
| `--preempt` | flag |  | Preempt |  |  |
| `--is-detach-others` | flag |  | Is Detach Others |  |  |
| `--emulation-mode` | text |  | Emulation Mode (options: ['NONE', 'STATIC', 'HOTPLUG']) |  |  |
| `--reference-id` | text |  | Reference ID |  |  |
| `--wait` | flag |  | Wait for operation to take effect |  |  |
| `--timeout` | integer |  | Seconds to wait (default 60) |  | 60 |

#### client count

_Show how many instances of this type are in the system_

#### client delete

_Delete one or more specified clients_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |

#### client detach

_Detach one or more volumes from the specified client_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |
| `--volume` | id/name |  | Volume |  |  |
| `--force` | flag |  | Force |  |  |
| `--reference-id` | text |  | Reference ID |  |  |
| `--wait` | flag |  | Wait for operation to take effect |  |  |
| `--timeout` | integer |  | Seconds to wait (default 60) |  | 60 |
| `-a`, `--all` | flag |  | Preform <Command detach> on all attachments |  |  |

#### client set-emulation-mode

_Set emulation mode on a UM client volume attachments_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |
| `--volume` | id/name | Yes | Volume |  |  |
| `--emulation-mode` | text |  | Emulation Mode (options: ['NONE', 'STATIC', 'HOTPLUG']) |  |  |

#### client show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### client wait

_Wait for a property to reach a desired value_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text | Yes |  |  |  |
| `-p`, `--property` | text | Yes | Property to wait for |  |  |
| `-v`, `--value` | text | Yes | Value to wait for (multiple allowed) |  |  |
| `-b`, `--boolean` | flag |  | Value is true/false |  |  |
| `-m`, `--missing` | text |  | Default value if actual missing |  |  |
| `--poll` | integer |  | Seconds to wait between polling |  | 1 |
| `--timeout` | integer |  | Seconds to wait before timeout |  | 60 |

---

### cluster

#### cluster show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-i`, `--id` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### cluster update-cluster-id

_Update the cluster's ID_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | text | Yes | ID |  |  |

---

### config-profile

#### config-profile apply

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--name`, `-n` | id/name | Yes |  |  |  |
| `--hosts` | id/name | Yes | Hosts |  |  |

#### config-profile count

_Show how many instances of this type are in the system_

#### config-profile create

_Create a new instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--hosts` | id/name |  | Hosts |  | [] |
| `--labels` | text |  | Labels |  | [] |
| `--name`, `-n` | text | Yes | Name |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--config` | key=value |  | Config |  | {} |

#### config-profile delete

_Delete a specified instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | id/name | Yes |  |  |  |

#### config-profile show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### config-profile update

_Update properties of an existing instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--hosts` | id/name |  | Hosts |  |  |
| `--labels` | text |  | Labels |  |  |
| `--name`, `-n` | id/name | Yes | Name |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--config` | key=value |  | Config |  |  |
| `--delete-config` | text |  | Delete key(s) from config |  |  |

---

### drive

#### drive count

_Show how many instances of this type are in the system_

#### drive delete

_Delete one or more specified drives_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |

#### drive evict

_Evict a drive from a target_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |

#### drive exclude-nvme

_Exclude NVME drive via /usr/bin/nvmesh_target on target_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--name`, `-n` | id/name | Yes | Drive id |  |  |

#### drive format

_Format a drive (wiping existing data)_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |
| `--format-type` | text |  | Format Type (options: ['format_ec', 'format_raid']) |  |  |
| `-y`, `--yes` | flag |  | Auto-confirm the operation |  |  |

#### drive include-nvme

_Include NVME drive via /usr/bin/nvmesh_target on target_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--name`, `-n` | id/name | Yes | Drive id |  |  |

#### drive reinstate

_Reinstate Drive_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |

#### drive show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### drive wait

_Wait for a property to reach a desired value_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text | Yes |  |  |  |
| `-p`, `--property` | text | Yes | Property to wait for |  |  |
| `-v`, `--value` | text | Yes | Value to wait for (multiple allowed) |  |  |
| `-b`, `--boolean` | flag |  | Value is true/false |  |  |
| `-m`, `--missing` | text |  | Default value if actual missing |  |  |
| `--poll` | integer |  | Seconds to wait between polling |  | 1 |
| `--timeout` | integer |  | Seconds to wait before timeout |  | 60 |

---

### drive-class

#### drive-class count

_Show how many instances of this type are in the system_

#### drive-class create

_Create a new instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--domains` | domain |  | Domains |  |  |
| `--drives` | id/name |  | Drives |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--name`, `-n` | text | Yes | Name |  |  |

#### drive-class delete

_Delete a specified instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | id/name | Yes |  |  |  |

#### drive-class show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### drive-class update

_Update properties of an existing instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--domains` | domain |  | Domains |  |  |
| `--drives` | id/name |  | Drives |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--name`, `-n` | id/name | Yes | Name |  |  |

---

### env

_Show active environment_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-v`, `--var` | text |  |  |  |  |

---

### general-settings

#### general-settings show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-i`, `--id` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### general-settings update

_Update properties of an existing instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--days-before-log-entry-expires` | integer |  | Days Before Log Entry Expires |  |  |
| `--enable-zones` | flag |  | Enable Zones |  |  |
| `--enable-nvmf` | flag |  | Enable NVMf |  |  |
| `--logging-level` | logginglevel |  | Logging Level (options: ['INFO', 'WARNING', 'ERROR', 'DEBUG', 'VERBOSE', 'NONE'] |  |  |
| `--domain` | text |  | Domain |  |  |

---

### generate-docs

_Generate CLI reference in Markdown (requires management connection)_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-v`, `--release-version` | text |  | Release version for title (default: derived from management) |  |  |

---

### key-pair

#### key-pair count

_Show how many instances of this type are in the system_

#### key-pair create

_Create a new instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--name`, `-n` | text | Yes | Name |  |  |

#### key-pair delete

_Delete a specified instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | id/name | Yes |  |  |  |

#### key-pair download

_Download a key-pair to a file_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text | Yes |  |  |  |
| `-p`, `--path` | file | Yes |  |  |  |
| `--overwrite` | flag |  |  |  |  |

#### key-pair show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### key-pair update

_Update properties of an existing instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--name`, `-n` | id/name | Yes | Name |  |  |

---

### log

#### log acknowledge

_Acknowledge a log_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |

#### log acknowledge-all

_Acknowledge all alerts_

#### log count

_Count of logs or alerts_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--alerts`, `-a` | flag |  | Only count alerts |  |  |

#### log show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-i`, `--id` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |
| `-a`, `--alerts` | flag |  | Only show alerts |  |  |

---

### login

_Connect to a management server_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-m`, `--management` | text |  | Management address as host[:port] |  |  |
| `-u`, `--user` | text |  |  |  |  |
| `-p`, `--password` | text |  |  |  |  |
| `--use-tls` | flag |  |  |  |  |
| `--cert` | text |  | Cert file for TLS connection with management |  |  |
| `--key` | text |  | Key file for TLS connection with management |  |  |
| `--ca` | text |  | CA file for TLS connection with management |  |  |
| `--save` | flag |  |  |  |  |

---

### management

#### management count

_Show how many instances of this type are in the system_

#### management show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-i`, `--id` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### management status

_Show HA status_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-f`, `--fields` | text |  | Comma separated fields to show - case insensitive, use "-" for space |  |  |

---

### target

#### target count

_Show how many instances of this type are in the system_

#### target delete

_Delete one or more specified targets_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |

#### target delete-nic

_Delete a nic from a target_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |
| `--nic-id`, `-n`, `--name` | text | Yes | NIC ID |  |  |

#### target evict

_Delete a server while evicting all of it's drives_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |

#### target set-zone

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |
| `--zone` | integer | Yes | Zone |  |  |

#### target show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### target wait

_Wait for a property to reach a desired value_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text | Yes |  |  |  |
| `-p`, `--property` | text | Yes | Property to wait for |  |  |
| `-v`, `--value` | text | Yes | Value to wait for (multiple allowed) |  |  |
| `-b`, `--boolean` | flag |  | Value is true/false |  |  |
| `-m`, `--missing` | text |  | Default value if actual missing |  |  |
| `--poll` | integer |  | Seconds to wait between polling |  | 1 |
| `--timeout` | integer |  | Seconds to wait before timeout |  | 60 |

---

### target-class

#### target-class count

_Show how many instances of this type are in the system_

#### target-class create

_Create a new instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--domains` | domain |  | Domains |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--targets` | id/name |  | Targets |  |  |
| `--name`, `-n` | text | Yes | Name |  |  |

#### target-class delete

_Delete a specified instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | id/name | Yes |  |  |  |

#### target-class show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### target-class update

_Update properties of an existing instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--domains` | domain |  | Domains |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--targets` | id/name |  | Targets |  |  |
| `--name`, `-n` | id/name | Yes | Name |  |  |

---

### upgrade

#### upgrade count

_Show how many instances of this type are in the system_

#### upgrade create

_Create a new instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--max-errors-threshold` | integer |  | Max Errors Threshold |  |  |
| `--execution-mode` | upgradeexecutionmodes |  | Execution Mode (options: ['manual', 'manualStart', 'automatic'] |  |  |
| `--skip-machines-on-failure` | flag |  | Skip Machines On Failure |  |  |
| `--destination-version` | text |  | Destination Version |  |  |
| `--machines-to-upgrade` | id/name |  | Machines To Upgrade |  |  |
| `--min-redundancy-level` | upgraderedundancylevels |  | Min Redundancy Level (options: ['minimal', 'max', 'none'] |  |  |
| `--max-concurrent-clients` | integer |  | Max Concurrent Clients |  |  |

#### upgrade delete

_Delete a specified instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-u`, `--uuid` | id/name | Yes |  |  |  |

#### upgrade resume

_Resume an upgrade_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--uuid` | id/name | Yes |  |  |  |

#### upgrade show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-u`, `--uuid` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### upgrade skip-failed-machine

_Mark UpgradeStep as completed_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--uuid` | id/name | Yes |  |  |  |

#### upgrade start

_Start an upgrade_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--uuid` | id/name | Yes |  |  |  |

---

### upgrade-agent

#### upgrade-agent count

_Show how many instances of this type are in the system_

#### upgrade-agent delete

_Delete one or more specified upgrade agents_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--hostname` | id/name | Yes |  |  |  |

#### upgrade-agent keepalive

_Request keepalive from an agent_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--hostname` | id/name | Yes |  |  |  |

#### upgrade-agent show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-h`, `--hostname` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

---

### upgrade-step

#### upgrade-step count

_Show how many instances of this type are in the system_

#### upgrade-step mark-as-completed

_Mark UpgradeStep as completed_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |

#### upgrade-step set-breakpoint

_Set/Clear breakpoint on UpgradeStep_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--id` | id/name | Yes |  |  |  |
| `--clear` | flag |  | Clear |  |  |

#### upgrade-step show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-u`, `--uuid` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

---

### user

#### user change-password

_Change password_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--password` | text | Yes | Password |  |  |

#### user count

_Show how many instances of this type are in the system_

#### user create

_Create a new instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--role` | role |  | Role (options: ['Admin', 'Observer'] |  | Observer |
| `--email` | text | Yes | Email |  |  |
| `--notification-level` | notificationlevel |  | Notification Level (options: ['NONE', 'WARNING', 'ERROR'] |  | NONE |
| `--description`, `-d` | text |  | Description |  |  |
| `--password` | text |  | Password |  |  |
| `--relogin` | flag |  | Relogin |  |  |

#### user delete

_Delete a specified instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-e`, `--email` | id/name | Yes |  |  |  |

#### user show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-e`, `--email` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### user update

_Update properties of an existing instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--role` | role |  | Role (options: ['Admin', 'Observer'] |  |  |
| `--email` | id/name | Yes | Email |  |  |
| `--notification-level` | notificationlevel |  | Notification Level (options: ['NONE', 'WARNING', 'ERROR'] |  |  |
| `--description`, `-d` | text |  | Description |  |  |

---

### version

_Show tool, infra and API versions_

---

### volume

#### volume add-passphrase

_Add a passphrase for encrypted volume_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--name`, `-n` | id/name | Yes |  |  |  |
| `--current-passphrase` | text | Yes | Current Passphrase |  |  |
| `--new-passphrase` | text | Yes | New Passphrase |  |  |
| `--slot` | integer |  | Slot |  |  |

#### volume count

_Show how many instances of this type are in the system_

#### volume create

_Create a new instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--crc-enabled` | flag |  | CRC Enabled |  |  |
| `--name`, `-n` | text | Yes | Name |  |  |
| `--target-classes` | id/name |  | Target Classes |  |  |
| `--drive-classes` | id/name |  | Drive Classes |  |  |
| `--mdv-spec-limit-by-nodes` | id/name |  | Mdv Spec Limit By Nodes |  |  |
| `--mdv-spec-limit-by-disks` | id/name |  | Mdv Spec Limit By Disks |  |  |
| `--mdv-spec-server-classes` | id/name |  | Mdv Spec Server Classes |  |  |
| `--mdv-spec-disk-classes` | id/name |  | Mdv Spec Disk Classes |  |  |
| `--mdv-spec-vpg` | id/name |  | Mdv Spec Vpg |  |  |
| `--limit-by-nodes`, `-T` | text |  | Limit By Nodes |  | [] |
| `--enabled-nvmf-clients` | text |  | Enabled NVMf Clients |  |  |
| `--nvmf-enabled` | flag |  | NVMf Enabled |  |  |
| `--vsgs`, `--volume-security-group` | id/name |  | VSGs |  | [] |
| `--relative-rebuild-priority` | integer |  | Relative Rebuild Priority |  |  |
| `--is-read-only` | flag |  | Is Read Only |  |  |
| `--source-id` | text |  | Source ID |  |  |
| `--limit-by-disks`, `-D` | text |  | Limit By Disks |  | [] |
| `--description`, `-d` | text |  | Description |  |  |
| `--metadata` | key=value |  | Metadata |  | {} |
| `--allow-allocation-on-offline-drives` | flag |  | Allow Allocation On Offline Drives |  |  |
| `--capacity`, `-c` | size |  | Capacity |  |  |
| `--encryption-header-size` | integer |  | Encryption Header Size |  | 16 |
| `--protection-level` | ecseparationtype |  | Protection Level (options: ['ignore', 'full', 'minimal'] |  |  |
| `--raid-level`, `--rl` | raidlevel |  | Raid Level (options: ['ec', 'sec', 'lvm', '0', '1', '10'] |  |  |
| `--stripe-size` | integer |  | Stripe Size |  |  |
| `--parity-blocks` | integer |  | Parity Blocks |  |  |
| `--number-of-mirrors` | integer |  | Number Of Mirrors |  |  |
| `--vpg` | text |  | Vpg |  |  |
| `--stripe-width` | integer |  | Stripe Width |  |  |
| `--ignore-node-separation` | flag |  | Ignore Node Separation |  |  |
| `--data-blocks` | integer |  | Data Blocks |  |  |
| `--is-encrypted` | flag |  | Is Encrypted |  |  |
| `--domain` | text |  | Domain |  |  |
| `--wait` | flag |  | Wait for operation to take effect |  |  |
| `--timeout` | integer |  | Seconds to wait (default 60) |  | 60 |

#### volume delete

_Delete a specified instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | id/name | Yes |  |  |  |
| `--wait` | flag |  | Wait for operation to take effect |  |  |
| `--timeout` | integer |  | Seconds to wait (default 60) |  | 60 |
| `-y`, `--yes` | flag |  | Auto-confirm the operation |  |  |

#### volume delete-passphrase

_Delete a passphrase for encrypted volume_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--name`, `-n` | id/name | Yes |  |  |  |
| `--current-passphrase` | text | Yes | Current Passphrase |  |  |
| `--slot` | integer |  | Slot |  |  |

#### volume extend

_Extend the size of a volume_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--name`, `-n` | id/name | Yes |  |  |  |
| `--capacity`, `-c` | size | Yes | Capacity |  |  |
| `--allow-allocation-on-offline-drives` | flag |  | Allow Allocation On Offline Drives |  |  |

#### volume init-encryption

_Initialize keys for encrypted volume_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--name`, `-n` | id/name | Yes |  |  |  |
| `--passphrase` | text | Yes | Passphrase |  |  |
| `--slot` | integer |  | Slot |  |  |
| `--number-of-slots` | integer |  | Number Of Slots |  |  |
| `--key-size` | text |  | Key Size (options: [256, 512]) |  |  |

#### volume rebuild

_Rebuild a volume_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--name`, `-n` | id/name | Yes |  |  |  |
| `--allow-allocation-on-offline-drives` | flag |  | Allow Allocation On Offline Drives |  |  |

#### volume rotate-passphrase

_Rotate a passphrase for encrypted volume_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--name`, `-n` | id/name | Yes |  |  |  |
| `--current-passphrase` | text | Yes | Current Passphrase |  |  |
| `--new-passphrase` | text | Yes | New Passphrase |  |  |
| `--slot` | integer |  | Slot |  |  |

#### volume show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### volume update

_Update properties of an existing instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--crc-enabled` | flag |  | CRC Enabled |  |  |
| `--name`, `-n` | id/name | Yes | Name |  |  |
| `--target-classes` | id/name |  | Target Classes |  |  |
| `--drive-classes` | id/name |  | Drive Classes |  |  |
| `--mdv-spec-limit-by-nodes` | id/name |  | Mdv Spec Limit By Nodes |  |  |
| `--mdv-spec-limit-by-disks` | id/name |  | Mdv Spec Limit By Disks |  |  |
| `--mdv-spec-server-classes` | id/name |  | Mdv Spec Server Classes |  |  |
| `--mdv-spec-disk-classes` | id/name |  | Mdv Spec Disk Classes |  |  |
| `--mdv-spec-vpg` | id/name |  | Mdv Spec Vpg |  |  |
| `--limit-by-nodes`, `-T` | text |  | Limit By Nodes |  |  |
| `--enabled-nvmf-clients` | text |  | Enabled NVMf Clients |  |  |
| `--nvmf-enabled` | flag |  | NVMf Enabled |  |  |
| `--vsgs`, `--volume-security-group` | id/name |  | VSGs |  |  |
| `--relative-rebuild-priority` | integer |  | Relative Rebuild Priority |  |  |
| `--is-read-only` | flag |  | Is Read Only |  |  |
| `--source-id` | text |  | Source ID |  |  |
| `--limit-by-disks`, `-D` | text |  | Limit By Disks |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--metadata` | key=value |  | Metadata |  |  |
| `--delete-metadata` | text |  | Delete key(s) from metadata |  |  |
| `--allow-allocation-on-offline-drives` | flag |  | Allow Allocation On Offline Drives |  |  |

#### volume wait

_Wait for a property to reach a desired value_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text | Yes |  |  |  |
| `-p`, `--property` | text | Yes | Property to wait for |  |  |
| `-v`, `--value` | text | Yes | Value to wait for (multiple allowed) |  |  |
| `-b`, `--boolean` | flag |  | Value is true/false |  |  |
| `-m`, `--missing` | text |  | Default value if actual missing |  |  |
| `--poll` | integer |  | Seconds to wait between polling |  | 1 |
| `--timeout` | integer |  | Seconds to wait before timeout |  | 60 |

---

### volume-security-group

#### volume-security-group count

_Show how many instances of this type are in the system_

#### volume-security-group create

_Create a new instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--name`, `-n` | text | Yes | Name |  |  |
| `--key-pairs` | text |  | Key Pairs |  |  |

#### volume-security-group delete

_Delete a specified instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | id/name | Yes |  |  |  |

#### volume-security-group show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### volume-security-group update

_Update properties of an existing instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--name`, `-n` | id/name | Yes | Name |  |  |
| `--key-pairs` | text |  | Key Pairs |  |  |

---

### vpg

#### vpg count

_Show how many instances of this type are in the system_

#### vpg create

_Create a new instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--vsgs`, `--volume-security-group` | id/name |  | VSGs |  |  |
| `--name`, `-n` | text | Yes | Name |  |  |
| `--allow-allocation-on-offline-drives` | flag |  | Allow Allocation On Offline Drives |  |  |
| `--capacity`, `-c` | size |  | Capacity |  |  |
| `--encryption-header-size` | integer |  | Encryption Header Size |  | 16 |
| `--protection-level` | ecseparationtype |  | Protection Level (options: ['ignore', 'full', 'minimal'] |  |  |
| `--target-classes` | id/name |  | Target Classes |  |  |
| `--raid-level`, `--rl` | raidlevel |  | Raid Level (options: ['ec', 'sec', 'lvm', '0', '1', '10'] |  |  |
| `--drive-classes` | id/name |  | Drive Classes |  |  |
| `--stripe-size` | integer |  | Stripe Size |  |  |
| `--parity-blocks` | integer |  | Parity Blocks |  |  |
| `--allow-overflow` | flag |  | Allow Overflow |  |  |
| `--number-of-mirrors` | integer |  | Number Of Mirrors |  |  |
| `--stripe-width` | integer |  | Stripe Width |  |  |
| `--ignore-node-separation` | flag |  | Ignore Node Separation |  |  |
| `--data-blocks` | integer |  | Data Blocks |  |  |
| `--is-encrypted` | flag |  | Is Encrypted |  |  |
| `--domain` | text |  | Domain |  |  |
| `--crc-enabled` | flag |  | CRC Enabled |  |  |

#### vpg delete

_Delete a specified instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | id/name | Yes |  |  |  |

#### vpg extend

_Extend the size of a VPG_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--name`, `-n` | id/name | Yes |  |  |  |
| `--capacity`, `-c` | size | Yes | Capacity |  |  |
| `--allow-allocation-on-offline-drives` | flag |  | Allow Allocation On Offline Drives |  |  |

#### vpg reclaim

_Reclaim VPG reserved space_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--name`, `-n` | id/name | Yes |  |  |  |

#### vpg show

_Show instances_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `-n`, `--name` | text |  | Show specific instance(s) (default is show all) |  |  |
| `-o`, `--output-format` | choice |  |  | `tabular`, `rows`, `json`, `list` |  |
| `-l`, `--limit` | integer |  | Page limit (0 is unlimited) |  |  |
| `-s`, `--skip` | integer |  |  |  | 0 |
| `-1`, `--onepage` | flag |  | Print one page and stop - no prompt |  |  |
| `-f`, `--fields` | text |  | Comma separated fields to show (besides ID/Name) - case insensitive, use "-" for space |  |  |

#### vpg update

_Update properties of an existing instance_

| Argument | Type | Required | Description | Choices | Default |
|----------|------|----------|-------------|---------|---------|
| `--cli-template` | text |  | Pull default values from a named template |  |  |
| `--cli-property` | text |  | Enable future properties as --extra-property foo=bar |  |  |
| `--description`, `-d` | text |  | Description |  |  |
| `--vsgs`, `--volume-security-group` | id/name |  | VSGs |  |  |
| `--name`, `-n` | id/name | Yes | Name |  |  |
| `--allow-allocation-on-offline-drives` | flag |  | Allow Allocation On Offline Drives |  |  |

---

