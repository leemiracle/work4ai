<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: GPL-2.0-only OR Apache-2.0
-->

# NVMesh by NVIDIA

## Notice
The NVMesh Roadmap is subject to change at any point and should not be considered a commitment for any purpose.

## NVMesh 3.4

The first open source version of NVMesh published as open source is a release candidate (RC) of NVMesh 3.4.0.

A generally available version is expected mid-March 2026.

## NVMesh 3.5

The current planned features for NVMesh 3.5 are:

* Introduction of 3-way mirroring for RAID-10, i.e., striped and mirrored volumes.
  
* Addition of a striping option for erasure coded volumes, i.e., RAID-60 support.

* Add support for TCP / SoftiWarp client-target communication on NVIDIA Grace CPUs with a 64K page size.

* Release of unused VPG space from a VPG's reserved space.

This version is expected mid-2026.

## NVMesh 4.0

NVMesh 4.0 will be a user-mode version of NVMesh functionality excluding TCP / SoftiWarp client-target communication, i.e., will require RDMA support.

This version is expected late 2026.

## NVMesh 4.1

The current planned features for NVMesh 4.1 are:

* User-mode version will include TCP / SoftiWarp support bringing it to feature parity with the kernel version.

* Support for drives larger than 32 TB.

This version is expected early 2027.
