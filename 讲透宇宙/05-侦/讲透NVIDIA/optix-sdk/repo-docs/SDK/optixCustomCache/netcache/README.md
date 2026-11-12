# netcache - Example Network Cache Server

A simple demonstration cache server built with Python and ZeroMQ. 
This server is designed to work with the `optixCustomCache` SDK sample and the `libcache` plugin example to demonstrate network-based caching for OptiX module compilation.

**⚠️ This is a toy example for demonstration purposes only.** It is not production-ready and should not be used or relied upon without significant hardening and testing. 
Users are responsible for implementing proper security, error handling, and reliability measures before deploying any network cache in production.

## Requirements

- Python 3.6+
- pyzmq (install via: `pip install -r requirements.txt`)

## Usage

**Start the cache server:**
```bash
python cache_server.py
```

The server listens on `tcp://localhost:5555`. 
This matches the default endpoint used by the `optixCustomCache` sample. 
A simple test client (`cache_client.py`) is included for testing purposes.

## Protocol

The server uses ZeroMQ REQ/REP pattern with a simple text-based protocol:
- Commands: `GET <key>`, `SET <key> <value>`, `SIZE <key>`, `PING`, etc.
- Responses: `OK [data]`, `NOT_FOUND`, or `ERROR: <message>`

The `libcache` plugin uses this protocol to implement an example of network-based caching for OptiX module compilation in the `optixCustomCache` sample.
