# Contributing

Small changes welcome. Read `AGENTS.md`, explain the behavior being fixed, and keep the recovery path reviewable.

```sh
cargo fmt --check
cargo test --locked
cargo clippy --locked -- -D warnings
./scripts/build.sh
python3 tests/recovery_check.py
python3 -m py_compile scripts/manage.py scripts/hardware_check.py
```

CI runs these checks on macOS. It has no Studio Displays and cannot prove audio, permissions or login behavior.

Hardware checks play a quiet test tone. Run only with the user's approval, the app quit, two connected Studio Displays, and low listening volume:

```sh
python3 scripts/hardware_check.py --play-test-tone
```

Results under `work/` are private and ignored by Git. They contain hardware identifiers. Report a redacted summary, macOS version and failure text in issues; do not upload raw diagnostics or captured audio.

Support for additional applications, display layouts or macOS versions needs an explicit test of direct-playback recovery. Never claim surround sound or measured synchronization from channel routing alone.
