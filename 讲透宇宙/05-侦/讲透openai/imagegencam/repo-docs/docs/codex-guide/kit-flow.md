# Prebuilt Kit Flow

Use this when the user received a prepared kit with Raspberry Pi OS already on the microSD card, camera dependencies already installed, and a first-boot Wi-Fi selector on the display. The expected image contract is in `docs/kit-image-contract.md`.

## 0. Starting Point

The user should start in Codex Desktop on their Mac before assembling the kit. The intended first prompt is:

```text
Help me make the prebuilt ImageGenCam. https://github.com/openai/imagegencam
```

Do not send prebuilt-kit users to Raspberry Pi Imager or the DIY setup route. Start by identifying the prebuilt kit, then guide assembly.

## 1. Acknowledge The Prebuilt Kit

Start with a short acknowledgement:

```text
I see this is the prebuilt ImageGenCam. I will skip Raspberry Pi Imager and start with assembly.
```

Do not ask a fork-in-the-road question if the user already said "prebuilt" or "preloaded". Stay on this flow. Do not tell the user to use Raspberry Pi Imager, run the full apt install path, or reclone the repo unless verification proves the kit image is missing something.

## 2. Assemble And Power On

Guide the physical build one step at a time in this exact order. Do not let the user power on the Pi or attach parts out of order.

1. Insert the prepared microSD card if it is not already installed.
2. Connect the camera ribbon. Be specific for first-timers: find the tiny camera connector on the Raspberry Pi, gently lift the dark latch, slide the ribbon in straight, then press the latch back down. The exposed metal contacts on the ribbon should face the contacts inside the slot. Do not force it; if it does not slide in, stop and check orientation.
3. Install the PiSugar 3 board and battery.
4. Press the Display HAT Mini onto the Pi headers.
5. Plug USB-C power into the PiSugar charging/power port.
6. Power on from the PiSugar shutter/Power button on the side opposite the USB-C port: tap once, then hold it for about 8 seconds, then release.
7. Wait for the display.

Success looks like a boot screen followed by a Wi-Fi selector on the device display.

## 3. Join Wi-Fi

Have the user connect the Pi to the same Wi-Fi network as their Mac using the on-screen selector.

After Wi-Fi connects, the display should show:

- Pi IP address
- SSH username: `imagegencam`
- temporary starter password

If the Wi-Fi selector does not appear within a few minutes:

- confirm the Display HAT Mini is fully seated
- confirm the Pi has power
- ask whether the kit image might have been replaced
- use `hardware-checks.md` if the user can already reach the Pi

## 4. Confirm SSH From The Mac

In the Mac Terminal app, try:

```bash
ssh imagegencam@imagegencam.local
```

If SSH asks whether to continue connecting, the user can type `yes`. If `.local` fails, help them find the Pi IP from the router, hotspot, or `arp -a`, then try:

```bash
ssh imagegencam@<pi-ip-address>
```

Success looks like a shell prompt on the Pi. Plain SSH is only the reachability check and password-change step; the main work should continue in Codex Desktop remote.

## 5. Change The Starter Password

The starter password may be shared across kits. Treat it as temporary. Before adding an OpenAI API key or running the camera as the user's own device, have the user change it in the SSH terminal:

```bash
passwd
```

Tell the user:

- type the current starter password when asked
- type a new password twice
- the terminal may look blank while typing passwords
- do not paste the password into chat

If the kit image already forced a password change during first SSH login, count that as done.

## 6. Confirm Codex CLI And Open Remote Codex

Use `remote-codex.md`. The order matters: return to the user's Mac, set up the SSH key and concrete alias, verify or install Codex CLI on the Pi, then open the Pi from Codex Desktop.

The helper and verification commands are:

```bash
./scripts/setup_mac_ssh_to_pi.sh imagegencam.local
ssh imagegencam 'command -v codex && codex --version'
```

If `codex` is missing, use the install block in `remote-codex.md`. If it is present but Codex Desktop reports that the remote host is not authenticated, prepare the user to get an OpenAI API key from `https://platform.openai.com/api-keys`, then have the user connect to the Pi:

```bash
ssh imagegencam
```

After the prompt looks like `imagegencam@imagegencam:~ $`, have them run:

```bash
codex
```

They should create a new secret key named `imagegencam` with `All` permissions, choose API key authentication when prompted, paste the key only into the Pi terminal, and press **Control-C** until they are back at the Pi shell prompt after Codex opens successfully.

Do not continue to Codex Desktop remote SSH until `codex` runs successfully on the Pi.

Back on the user's Mac, from this repo, make sure the project folder exists before opening it in Codex Desktop. This gives remote Codex a project folder on the Pi filesystem:

```bash
ssh imagegencam 'mkdir -p ~/Documents && cd ~/Documents && if [ ! -d imagegencam ]; then git clone https://github.com/openai/imagegencam.git; fi'
ssh imagegencam 'hostname && test -d ~/Documents/imagegencam && command -v codex'
```

Then open Codex Desktop on the user's Mac:

1. Go to Settings > Connections > SSH.
2. Click **Add**.
3. Add or select the SSH host named `imagegencam`.
4. Exit Settings.
5. Click **New chat**.
6. Click the folder icon below the chat box.
7. Click **Add remote project**.
8. Select `imagegencam` as the remote host.
9. Add `/home/imagegencam/Documents/imagegencam` as the project path.
10. Start the remote chat and send `Take over from here!`.

## 7. Verify The Prebuilt Image

In remote Codex on the Pi, check:

```bash
hostname
pwd
test -d ~/Documents/imagegencam && echo "repo found"
rpicam-hello --list-cameras
python3 -c "import displayhatmini; print('displayhatmini ok')"
systemctl status pisugar-server --no-pager
```

If the repo is missing, clone it into `~/Documents/imagegencam` and continue with the DIY setup flow from app setup. If the camera, display, or PiSugar checks fail, use `hardware-checks.md`.

## 8. Configure And Run The App

Go to:

```bash
cd ~/Documents/imagegencam/software
```

If `.env` is missing or has no API key, run:

```bash
./scripts/setup_app.sh
```

When setup asks for an OpenAI API key, send the user to:

```text
https://platform.openai.com/api-keys
```

Do not ask them to paste the key into chat.

Run manually:

```bash
./scripts/run.sh
```

Success:

- display shows the boot image, then live preview
- phone controller opens at `http://imagegencam.local:8000`, or at `http://<pi-ip>:8000` if `.local` fails
- a photo can be taken
- a generated image appears in the album
- prompt edits in the phone app autosave

## 9. Auto-Start

If the service is already installed, verify it:

```bash
sudo systemctl status imagegencam.service --no-pager
```

When the service is running, the phone controller opens at `http://imagegencam.local`, or at `http://<pi-ip>` if `.local` fails.

If it is not installed and manual app launch works, use the normal service install path from `setup-flow.md`.
