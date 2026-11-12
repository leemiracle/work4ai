# Studio Pair

Native macOS utility: Rust real-time audio engine, Objective-C CoreAudio bridge, Swift/AppKit menu bar.

- Keep the audio callback allocation-free, lock-free, and free of I/O.
- Never change default input/output devices or hardware sample rates.
- Journal secondary volume/mute before writing; restore only values still owned by this app.
- Keep rollback and crash recovery working. Do not install a HAL driver or restart CoreAudio.
- Use native AppKit controls. Keep product UI concise.
- Run cargo fmt --check, cargo test, cargo clippy -- -D warnings, and ./scripts/build.sh.
- Hardware checks play a quiet tone and require two Studio Displays. Run them only when explicitly authorized and with the app stopped.
- Do not publish local diagnostics, device UIDs, process inventories, or audio.
