# DSX Air SDK

This project provides a Python SDK for interacting with the NVIDIA DSX Air API.

## Documentation

For the full SDK documentation, please refer to the [SDK](https://docs.nvidia.com/dsx-air/sdk) page on NVIDIA docs.

For tutorials and code examples, please refer to the [examples README](./docs/README.md) in the `docs` directory. There you will find Jupyter notebooks covering various SDK features such as ZTP scripts and simulation import/export.

## Prerequisite

The SDK requires Python 3.10. There are a number of ways to achieve this such as `poetry`, `uv` or `virtualenv`.
The following shows how to achieve this on a few popular OS's using `virtualenv`.

```
# Install Python 3.10
brew install python@3.10  # MacOS
apt-get install python3.10  # Ubuntu/Debian
sudo pacman -S python310  # Arch

# Install, create and activate a Python 3.10 virtual environment
python3.10 -m pip install virtualenv
python3.10 -m virtualenv venv
. venv/bin/activate
```


## Installation

`pip install nv-air-sdk`

## Authentication Options

1. NGC Device Login with `AirApi.with_device_login(email=<YOUR_EMAIL>, org_num=<YOUR_NGC_ORG_NUMBER>)`
2. NGC CLI Login with `AirApi.with_ngc_config()` (or just `AirApi()`)   
3. Explicitly specify an NGC API Key (also known as a Starfleet API Key, or "SAK") by instantiating `AirApi.with_api_key(api_key=<YOUR_STARFLEET_API_KEY>)`

And to use option 2 you will need to have the [NGC CLI](https://org.stg.ngc.nvidia.com/setup/installers/cli) installed and to have configured it with `ngc config set`. This will create a file at `~/.ngc/config` which contains your NGC credentials that will be auto-detected by the Air SDK.


## License

MIT License - see LICENSE file for details

This project will download and install additional third-party open source software projects. Review the license terms of these open source projects before use.

## Contributing

This project is currently not accepting contributions.