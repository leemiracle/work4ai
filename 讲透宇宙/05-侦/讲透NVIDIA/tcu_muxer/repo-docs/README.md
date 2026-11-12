# tcu_muxer

`tcu_muxer` is the BMC userspace endpoint for Tegra Combined UART. It owns one
physical UART descriptor, decodes TCU channel tags, and exposes one
pseudo-terminal and optional log per firmware channel.

## Receive architecture

```text
/dev/ttyUSB* read
        |
        +--> exact pre-parser raw log (-l; current qualification source)
        |
        +--> optional binary-record diagnostic capture (-R; disabled today)
        |
        `--> TCU parser --> per-VSER 1 MiB queue --> PTY + demux log
```

The physical reader requests up to 16 KiB per syscall, parses that bounded read
into per-VSER batches, and enqueues each touched VSER once. The larger read
drains a USB-serial burst without four-to-sixteen avoidable scheduling gaps; the
batching preserves byte order and the existing CR/LF completion rule while
avoiding a mutex operation and worker wakeup for every character. It then
returns promptly to `/dev/ttyUSB*` instead of waiting for a PTY consumer or
demultiplexed log write. Each VSER worker retries `EINTR` and `EAGAIN`,
preserves short-write suffixes, and isolates a stalled channel behind its own
bounded queue. Queue overflow is reported and marks that VSER unhealthy; bytes
are never silently evicted.

The same VSER worker owns persistent console logging. Timestamp formatting is
accumulated in a 16 KiB buffer and flushed once per PTY batch, avoiding
synchronous per-character filesystem writes during RAS/UCF bursts while
retaining the existing timestamp and rotation behavior.

## Native physical-read capture

The current SBIOS product qualification runs the installed service command
unchanged. It does not enable either diagnostic capture mode. End-to-end
producer and consumer ledgers decide the verdict; normal demultiplexed logs and
the counters below provide supporting diagnosis.

`-R <path>` records every successful physical `read()` before framing, routing,
timestamping, PTY delivery, or log output. A dedicated worker writes versioned
binary records while the physical thread only copies into a bounded queue. The
active file and `<path>.1` are each bounded to 16 MiB.

Each record contains:

- format magic/version and record type;
- realtime and monotonic timestamps;
- monotonically increasing physical-read sequence;
- exact payload length and CRC32;
- explicit dropped-record and dropped-byte counts for a GAP record.

A GAP, CRC mismatch, truncated record, unknown version, or non-increasing
sequence makes the capture invalid. This is intentional: diagnostic evidence
must fail closed rather than resemble a valid but incomplete UART stream.

Send `SIGUSR1` to request a read-only statistics snapshot. `SIGINT` and
`SIGTERM` request an orderly, bounded shutdown. Physical-UART transmit retries
stop when shutdown is requested, native capture drains in normal thread context,
and every VSER reports any bytes discarded from its output queue as
`shutdown_dropped`. The process then prints final counters and releases the UART
lock. A nonzero `shutdown_dropped` value makes the corresponding evidence
boundary incomplete; it is never presented as successful delivery.

## Physical UART transmit reliability

Data written by an obmc-console client is tagged and escaped, then admitted as a
complete encoded block into a bounded 4 MiB shared TX queue. Normal commands and
the 1.3 MiB qualification stream fit inside this smoothing window. When the
finite queue is full, the input worker waits instead of continuing to drain the
PTY. Kernel backpressure then propagates through the corrected obmc-console
relay and SSH to the original sender without discarding an unwritten suffix.

One physical UART worker preserves the order of all VSER blocks. It submits at
most 1024 bytes per `write()`, retains the exact unwritten suffix, and removes
bytes only after the BMC TTY accepts them. The 4 MiB allocation makes ring wrap
safe while bounding memory use. If no queue progress occurs for five seconds,
the complete new block is rejected, TX is marked unhealthy, and the muxer stops.
The failure is explicit rather than a partial command followed by misleading
continued use.

A successful `write()` may accept fewer bytes than were requested. The worker
therefore retains an offset into the encoded buffer, advances it only by the
positive return value, and retries the unwritten suffix. `EINTR`, `EAGAIN`, and
`EWOULDBLOCK` never advance that offset.

The statistics snapshot reports each VSER's PTY input bytes/reads, TX queue
high-water mark, backpressure waits, admission timeouts, requested and accepted
physical bytes, write calls, positive short writes, retryable errors, physical
timeouts, zero-progress writes, and fatal errors. This creates three separate
proof boundaries:

1. sender ledger versus VSER input proves delivery into the muxer;
2. queue input versus physical accepted bytes proves muxer handling;
3. physical accepted bytes versus the CCPLEX receiver ledger tests the
   driver/electrical/target suffix.

Matching requested/accepted physical totals with no terminal error proves that
the muxer delivered every encoded byte to the BMC TTY driver; it does not by
itself prove electrical delivery to CCPLEX. A recovered HUP can leave these
totals unequal because the interrupted attempt and its retry are both retained
as evidence; use the lifecycle counters and the target ledger to classify that
case.

### Physical UART disconnect and reopen

The RX reader owns physical-descriptor replacement. A dedicated lifecycle mutex
pins the descriptor generation while a TX `poll()`/`write()` transaction is
active. Reopen prevents new TX transactions, waits for the active one to release
the descriptor, then serializes `close()`, `open()`, termios setup, and the
complete TCU reset sequence. Normal physical I/O does not hold the mutex, so
sustained full-duplex RX remains responsive. The lifecycle mutex is deliberately
separate from `tty_data.write_lock`: a PTY producer can wait for TX queue space
while holding that lock, so making the TX worker acquire it would create a
queue-full deadlock.

```text
RX observes HUP/ERR/NVAL          TX observes HUP/ERR/NVAL
          |                                  |
          `---------- request reopen --------'
                             |
                 RX takes lifecycle lock
                             |
          close old fd -> open/configure new fd
                             |
                 emit complete TCU reset
                             |
             increment descriptor generation
                             |
               wake TX; retry queue snapshot
```

The shared descriptor is never closed while TX is polling or writing it. A
disconnect does not dequeue the current TX snapshot. TX waits for RX to publish
a newer descriptor generation, then retries the unchanged snapshot; only a
complete successful write advances the queue head. Reopen failure is terminal
and visible rather than allowing use of a stale or reused descriptor number.

`SIGUSR1` and shutdown statistics report the descriptor generation, whether a
descriptor is available, pending/in-progress/failed state, reopen requests,
attempts, successes, failures, and TX retries. These counters distinguish a
recovered cable/driver HUP from an unexplained muxer restart.

## Invalid TCU tag handling

Every physical byte is still written to the pre-parser raw evidence. When the
decoder sees an unknown `FF xx` control sequence, it records the control byte,
physical-read byte offset, realtime timestamp, monotonic timestamp, and the
previous VSER. It then enters quarantine instead of retaining the previous
route. Untagged payload bytes are counted but not delivered to any semantic VSER
until a valid channel tag or TCU reset resynchronizes the parser.

This policy prevents a damaged selector from appending subsequent CCPLEX bytes
to PSC, OOBHUB, or another previously selected log. The statistics snapshot
reports invalid tags, quarantined bytes, resynchronizations, and the last
invalid offset/time. A completely missing selector that leaves no invalid
control sequence is not distinguishable from legal continuation bytes at this
protocol layer; detecting that case requires a higher-level framed payload or
UTC protocol change.

## Build

```bash
make clean
make
```

Run the process-level regression with:

```bash
make check
```

The regression uses two pseudoterminals as successive physical UARTs. It fills
the TX path from the generated CCPLEX PTY, atomically changes the stable device
symlink, and closes the old endpoint while TX is active. It requires the new
stream to start with one complete reset, requires a queued sentinel to arrive,
checks that the muxer remains alive, and verifies a successful descriptor
generation change with no reopen failure. It then sends more than six maximum
physical-read batches in the reverse direction, including every byte value and
escaped `0xff` bytes, and requires the CCPLEX PTY to receive the original
logical payload exactly. This also guards the batched parser/routing path.
