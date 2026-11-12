# Install and undo

Studio Pair is an early source-built macOS utility for Spotify desktop and two Apple Studio Displays. It is not affiliated with Apple or Spotify.

## Prerequisites

- macOS 14.2 or later. Apple silicon hardware tested; Intel hardware untested.
- Exactly two Studio Displays with eight output channels each, already at 48 kHz.
- Spotify desktop, playing through one Studio Display as the normal output.
- Xcode Command Line Tools, Rust 1.87+ with Cargo, and Python 3. Install missing tools only with the user's permission. Studio Pair's installer does not download tools.

## Build and install

```sh
git clone https://github.com/browser-use/studio-pair.git
cd studio-pair
python3 scripts/manage.py install
```

The installer compiles locally, verifies its ad hoc code signature, and places the app at `~/Applications/Studio Pair.app`. On upgrade it gracefully stops the existing app and keeps one previous bundle under `build/previous/`. An unrelated app at that path is never replaced. No `sudo` is needed.

Open the speaker-pair icon in the menu bar. Allow macOS system audio capture when prompted; this lets CoreAudio route Spotify's output. Audio stays in memory on this Mac. If permission was denied, enable Studio Pair under System Settings > Privacy & Security > Screen & System Audio Recording (the label varies by macOS version), then quit and reopen it.

Use the swap button if left/right is reversed. The app cannot infer the physical arrangement of your desk. Enable **Launch at login** if desired; macOS may require approval in Login Items.

The app does not change your sound output for you. If it says it is waiting for Studio Display output, choose one of your Studio Displays in macOS Sound settings. If it reports an unsupported layout/rate, leave pairing off. Hardware layouts beyond the tested 8+8 channels at 48 kHz need separate validation.

## Stop or uninstall

Use the pairing switch or **Quit Studio Pair**. Command-line recovery:

```sh
python3 scripts/manage.py stop
```

To unregister login, stop and restore audio, then remove the installed bundle:

```sh
python3 scripts/manage.py uninstall
```

The uninstall stops if recovery or login removal fails. Reconnect a missing display and retry. It retains preferences and `~/Library/Application Support/StudioPair` for recovery; those files contain device identities and should not be attached to public issues.

If the menu is unresponsive, quit the app with Activity Monitor, then run the stop command. Recovery checks both executable path and process start time before signalling a saved worker PID. Do not delete the journal before recovery succeeds.

## Build without installing

```sh
./scripts/build.sh
```

Result: `build/Studio Pair.app`. Native host architecture only. The deployment target is macOS 14.2. Building does not start the app, request permissions, or change audio.

## Agent instructions

Read `AGENTS.md`. Preserve existing sound defaults and settings. Do not bypass macOS security prompts, install drivers, restart CoreAudio or run test tones just to install. Report waiting/permission states honestly. An installed app is not proof that Spotify is being routed; confirm the menu says **Stereo active** while music plays.
