# Validation

Initial release validation: 2026-10-27, one Apple M5 Pro Mac on macOS 27.0, two Apple Studio Displays at 48 kHz. This is a beta, not a broad compatibility or listening-quality study.

| Check | Result |
| --- | --- |
| Rust routing, swapped channels, interleaved/planar layouts | Passed |
| Silent warmup and invalid buffer rejection | Passed |
| Nonfinite/bounded samples and gain ramp | Passed |
| Completed journal cannot signal a reused PID | Passed; failed on the old implementation |
| Same path but different process start time cannot be signalled | Passed; failed on the old implementation |
| Incomplete live legacy identity is refused | Passed; failed on the old implementation |
| Non-object journal reports an error without signalling | Passed; old implementation crashed |
| Real CoreAudio route: normal stop, forced worker death + restore, finite duration, continuous mode | Passed on the test setup |
| Continuous mode | Survived the short test, then stopped on request; no long-duration claim |
| Defaults, sample rates and secondary controls after those runs | Returned to captured baseline |
| Native left/right swap and pairing switch | Observed working |
| Controller recovers from killed audio worker | Passed with Spotify playing |
| Quit/relaunch preserves assignment, pairing and login | Passed |
| Source installer upgrade and uninstall | Passed; uninstall removed bundle, unregistered login and restored journal |
| Menu-bar launch at login registration | Enabled in macOS; actual reboot not tested |
| Deployment target | Both app and engine Mach-O load commands report macOS 14.2 |
| Signing | Ad hoc signature verified; not Developer ID signed or notarized |

The hardware runner uses its own quiet stereo source to isolate the route. Separately, Spotify playback reached **Stereo active** in the native app. Neither is a measurement of acoustic phase, latency, room response or subjective quality.

CI covers formatting, Rust tests, Clippy, a native app build and process-recovery regressions. It does not exercise hardware, audio permissions, menu interaction or login.

Still unverified: macOS 14.2 hardware behavior, Intel Macs, actual reboot startup, sleep/wake, display unplug/reconnect, Spotify upgrades, long sessions and acoustic synchronization. Unsupported layouts fail closed. Please report macOS version and redacted failure text, not raw journals or device inventories.
