# pingpong

`pingpong` is a Linux core-to-core latency microbenchmark. It pins two worker
threads to selected CPU cores, exchanges ownership of one or two cache lines,
and reports one-way latency in CPU cycles and nanoseconds.

The benchmark is intended for reproducible external reporting of core-to-core
latency heat maps, including Grace and Vera platform measurements.

## Requirements

- Linux
- GCC or a compatible C compiler
- GNU Make
- pthreads
- Linux `perf_event_open` access for hardware CPU cycle counters

Depending on the system configuration, `perf_event_open` may require relaxed
`perf_event_paranoid` settings or elevated permissions.

## Build

```sh
make
```

To remove build outputs:

```sh
make clean
```

## Usage

Show command-line options:

```sh
./pingpong -h
```

Measure one core pair:

```sh
./pingpong -p 0,1 -n 1048576 -w 0
```

Run a full pairwise sweep and write CSV matrices:

```sh
./pingpong -o data.csv
```

The default full sweep writes cycle results to `data.csv` and nanosecond results
to `data_ns.csv`. Reported values are one-way latency, equal to half of a
ping-pong round trip.

## Worker Modes

- `-w 0`: one cache line, load/store handoff
- `-w 1`: two cache lines, single-writer/single-reader handoff
- `-w 2`: one cache line, compare-and-swap handoff

Use `-L` to first-touch the shared line on the first core's NUMA node for each
pair, which reduces home-node placement artifacts.

## Contributions

This project is currently not accepting contributions.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the current contribution policy and
[MAINTAINERS.md](MAINTAINERS.md) for the project maintenance model.

## Support

See [SUPPORT.md](SUPPORT.md) for the project support policy.

## Security

To report a potential security vulnerability, follow the private reporting
instructions in [SECURITY.md](SECURITY.md). Do not report security
vulnerabilities through GitHub.

## License

This project is licensed under the Apache License 2.0. See
[LICENSE](LICENSE) for details.
