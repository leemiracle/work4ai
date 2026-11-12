# nvidia-driver-assistant

This piece of software is meant to help users deciding on which NVIDIA graphics
driver to install, based on the detected system's hardware.

## Command line interface

By default, the `nvidia-drivers-assistant` command line tool will show the driver
packages suitable for the hardware, and print the instructions relevant to
the current Linux distribution (see the list of supported Linux
distributions in the next section).

Optionally, `nvidia-driver-assistant --install`, can also install the driver
automatically.

Additional supported arguments:
- `--branch [BRANCH]` - Specify the desired NVIDIA driver branch
- `--supported-gpus [SUPPORTED_GPUS]` - Use a different version of the `supported-gpus.json` file
- `--sys-path [SYS_PATH]` - Use a different /sys path. Useful for testing
- `--os-release-path [OS_RELEASE_PATH]` - Use a different path for the os-release file. Useful for testing
- `--distro [DISTRO]` - Specify a Linux distro using the `"DISTRO:VERSION"` or `"DISTRO"` pattern. Useful for testing
- `--module-flavor [MODULE_FLAVOR]` - Specify a kernel module flavor. Useful for testing
- `--verbose` - Verbose output

Please see `nvidia-driver-assistant --help` for further details.

## Supported Linux distributions

The following Linux distributions are currently supported:

- [ ] Amazon Linux 2023
- [ ] CBL-Mariner (Azure Linux)
- [ ] Debian
- [ ] Fedora
- [ ] Kylin
- [ ] Red Hat Enterprise Linux (RHEL)
- [ ] openSUSE
- [ ] SUSE Linux Enterprise Server Distribution (SLES)
- [ ] Ubuntu

## Test suite

To use the test suite `nvidia-driver-assistant` comes with, you are going to need the following dependencies:

```python3-gi and umockdev gir1.2-umockdev-1.0```

The test suite can be run as follows:

```shell
$ PYTHONPATH=. tests/run --suite test_nvidia_driver_assistant.py
```

Note: no actual NVIDIA hardware is required for testing, since umockdev is used to simulate the
      presence of such devices.


## Authors and acknowledgment
Alberto Milone <amilone@nvidia.com>

## License
All the included code and assets are MIT licensed.
