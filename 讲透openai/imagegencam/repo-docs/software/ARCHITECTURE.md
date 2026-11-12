# Software Architecture

This folder is the complete runnable app for ImageGenCam. The goal is to keep the Pi Zero doing as little work as possible while still feeling like a real camera.

## Runtime Shape

- `src/imagegencam/app.py` wires together configuration, OpenAI clients, durable job stores, the camera controller, and the phone web server.
- `src/imagegencam/controller.py` owns the physical device loop: Pi camera frames, Display HAT Mini rendering, button events, PiSugar shutter events, image generation jobs, album state, Magic Mode, and battery display.
- `src/imagegencam/web.py` serves the local phone controller, image downloads, the live screen mirror, prompt editing, Magic History, and the vertical recreation endpoint.
- `src/imagegencam/openai_client.py` contains all OpenAI API calls.
- `src/imagegencam/job_store.py` is the small on-disk queue used for image-generation retry.
- `src/imagegencam/wifi_manager.py` wraps NetworkManager for safe on-device Wi-Fi scanning, saved-network switching, and rollback-protected new connections.
- `src/imagegencam/config.py` contains persistent user-editable data stores and normalization for prompts, settings, and Magic History.

## Data Folders

- `data/prompts.json` is the seed prompt list that ships with the project.
- `data/settings.json` is local device state, such as camera username and UI theme.
- `data/magic_history.json` is local runtime history. Do not commit personal/device history unless you intentionally want examples in the repo.
- `data/captures/` stores original source captures.
- `data/generated/` stores generated outputs.
- `data/queue/` stores pending generation jobs. It is runtime state and is intentionally ignored by Git.

## Reliability Rules

- Captures are saved locally before generation work is handed to OpenAI.
- Generation jobs are persisted in `data/queue/generation/` and retried after failures or restarts.
- The phone web app should stay local-LAN only. Do not expose it directly to the public internet without adding authentication.
- Wi-Fi changes must never delete existing NetworkManager profiles. New connection attempts should keep a rollback path to the previously active profile. The service installer adds a narrow sudoers rule for only the required `nmcli` connection commands.

## Pi Zero Rules

- Keep preview work cheap. The display path is the bottleneck, not the camera sensor.
- Avoid per-frame image processing unless it changes visible state.
- Prefer small, durable JSON job files over in-memory queues for anything that must survive power loss.
- Treat optional features as removable: Magic Mode can be disabled with `MAGIC_MODE_ENABLED=0`.
