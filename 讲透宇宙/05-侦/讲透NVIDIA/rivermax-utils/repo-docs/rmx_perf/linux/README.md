# Rivermax Linux Performance Tool

## Overview

The `rmx_perf` tool is a comprehensive bash-based performance tuning and monitoring utility for Linux systems running NVIDIA Rivermax SDK applications. It automates the recommendations from the NVIDIA Rivermax Performance Tuning Guide.

## Documentation

**[View Full Documentation](https://nvidia.github.io/rivermax-utils/rmx_perf)**

The GitHub Pages documentation includes:
- Detailed command reference for all options and modes
- Usage examples for Device, Tune, Query, Monitor, and PTP operations
- Testing guide
- Getting started workflow

## Main Components

The tool provides several operation modes:

- **Devices (`-d`)** - Discover NVIDIA network devices with detailed information
- **Tune (`-t`)** - Apply performance tuning (network, CPU, OS, GRUB)
- **Query (`-q`)** - Report current system state without making changes
- **Monitor (`-m`)** - Continuous PTP/PHC synchronization monitoring
- **Run PTP (`--rp`)** - Configure and start PTP services (ptp4l, phc2sys)
- **Stop PTP (`--sp`)** - Stop PTP services
- **Install Tools (`--it`)** - Install required system packages

## Basic Commands

```bash
# Show available NVIDIA network devices
sudo ./rmx_perf -d

# Tune system with default settings
sudo ./rmx_perf -i eth0 -t

# Query current settings (no changes)
sudo ./rmx_perf -i eth0 -q

# Monitor PTP/PHC synchronization
sudo ./rmx_perf -i eth0 -m
```

## Resources

- **Documentation**: [View online documentation](https://nvidia.github.io/rivermax-utils/rmx_perf)
- **Built-in Help**: `./rmx_perf --help`
- **NVIDIA Rivermax Performance Tuning Guide**: Find it on the [NVIDIA Rivermax Getting Started page](https://developer.nvidia.com/networking/rivermax-getting-started)
- **Report Issues**: [File a new issue](https://github.com/NVIDIA/rivermax-utils/issues/new) on GitHub
