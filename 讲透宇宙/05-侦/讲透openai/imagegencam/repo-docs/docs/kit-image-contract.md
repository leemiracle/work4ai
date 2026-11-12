# Prebuilt Kit Image Contract

Use this when preparing microSD cards for kits. The user-facing tutorial assumes these pieces are already present on the card.

## Identity

- Hostname: `imagegencam`
- User: `imagegencam`
- SSH: enabled on the local network
- mDNS/Avahi: enabled so `imagegencam.local` usually works
- NetworkManager: enabled
- Installed web app service: listens on port 80 so `http://imagegencam.local` works without a port number

The kit image may use a shared starter SSH password only as a temporary bootstrap credential. Do not expose SSH or any app-server transport to the WAN. Do not configure port forwarding, a public tunnel, or unauthenticated public listeners.

Do not bake in any OpenAI API key.

## First Boot

- The physical kit instructions should tell the user to open Codex Desktop on their Mac before assembling parts and ask: `Help me make the prebuilt ImageGenCam. https://github.com/openai/imagegencam`
- Boot to the device display.
- Show the Wi-Fi selector if the Pi is not already connected.
- Join the same local network as the user's Mac.
- After Wi-Fi connects, show the Pi IP address, SSH username, and starter SSH password on the device display.
- Make clear that the password is temporary and should be changed in the tutorial before API key setup.
- Keep the desktop recovery fallback available for offline troubleshooting.

Prefer expiring the starter password so the first SSH login forces the user to choose a new one:

```bash
sudo chage -d 0 imagegencam
```

If forced expiration is not compatible with the first-boot UI, the tutorial must still make `passwd` the first action after successful SSH.

## Remote Codex Readiness

The Pi user must have `codex` available on `PATH`:

```bash
command -v codex
codex --version
```

The user may still need to authenticate Codex on first use. The tutorial prepares them to use an OpenAI API key from `https://platform.openai.com/home`. The remote Codex Desktop step must not start until the user can run `codex` successfully on the Pi.

## Repo And App

The repo should be present at:

```text
/home/imagegencam/Documents/imagegencam
```

The image should include:

- `git`
- `nodejs` and `npm`
- `python3-venv`
- `python3-picamera2`
- `python3-pil`
- `python3-pip`
- `network-manager`
- Display HAT Mini Python library
- PiSugar 3 server
- camera app Python dependencies, where practical

Leave `software/.env` absent or with an empty `OPENAI_API_KEY`. The user should create their own key during setup.

## Verification Checklist

Run these before shipping a card:

```bash
hostname
command -v codex
sudo chage -l imagegencam
rpicam-hello --list-cameras
python3 -c "import displayhatmini; print('displayhatmini ok')"
systemctl status pisugar-server --no-pager
test -d ~/Documents/imagegencam && echo "repo found"
```

The app may be installed as a service, but manual launch must also work:

```bash
cd ~/Documents/imagegencam/software
./scripts/run.sh
```
