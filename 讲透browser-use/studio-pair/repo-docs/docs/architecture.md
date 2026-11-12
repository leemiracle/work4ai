# Audio and recovery

`app/App.swift` owns the menu bar, preferences, login registration and worker lifecycle. It waits for two Studio Displays, a Studio Display default output and an active Spotify audio process. One app lock prevents duplicate controllers. A worker lock prevents competing routes that share a journal.

`src/bridge.m` identifies Spotify's CoreAudio processes and creates a private device-stream tap. A private aggregate includes the two physical endpoints and that tap. It reads back the aggregate's subdevice order, privacy, stacking and secondary drift correction before starting. The tap starts unmuted; callback and nonzero-input checks must pass before direct Spotify output is muted while tapped.

`src/main.rs` validates the buffers, duplicates input L to the first display's front pair and input R to the second display's front pair, and clears unused channels. The callback performs no allocation, file I/O or locking. Gain ramps toward 0.5 (-6 dB); nonfinite values become zero and samples are bounded. It is a stereo router, not an Atmos decoder, equalizer or acoustic calibration system.

The default output remains physical. Volume and mute on that display are mirrored to the secondary every ~100 ms. The secondary's original values and the intended write are saved atomically before mutation. Restoration uses stable device UID and restores only controls still matching the app's last write; a secondary that became the default output is left alone. User changes to the primary remain intact.

Normal stop fades the routed signal down, unmutes/destroys the tap and restores owned controls. Worker/parent watchdogs release stalled private routes; the GUI restores the journal after worker exit. Recovery identifies a live process by PID, executable path and process start timestamp. Completed journals never signal a saved PID. A disconnected secondary may need reconnection before restoration can finish; new routing waits for recovery.

Sleep stops the worker; wake and Spotify launch/termination trigger readiness checks. These paths exist but need broader hardware validation. Failures back off instead of repeatedly taking over audio. A process tap excludes unrelated application audio; sharing the physical display volume still affects everything playing on that endpoint.

## Local data

Preferences contain pairing enabled and the left display UID. Runtime files live under `~/Library/Application Support/StudioPair` with a private directory and restricted file modes: rollback journal, status, locks and bounded event logs. Logs record state and levels, never audio samples. No network client or telemetry is included. Do not publish these files; the `inspect` CLI also prints process and device identities.
