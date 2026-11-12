# DIY Setup Flow

Use this when guiding a fresh build from a blank microSD card to a working camera. This is the default route unless the user's prompt explicitly says they have a prebuilt or preloaded kit.

## 1. Set Up The Raspberry Pi MicroSD Card

Have the user install Raspberry Pi Imager first if they do not already have it:

```text
https://www.raspberrypi.com/software/
```

Then have them put the microSD card into their Mac and open Raspberry Pi Imager. Use plain language: this step is "setting up your Raspberry Pi," not "flashing an OS."

Use these settings:

- Device: `Raspberry Pi Zero 2 W`
- OS: `Raspberry Pi OS (64-bit) with Desktop`
- Hostname: `imagegencam`
- Username: `imagegencam`
- Password: choose one
- Wi-Fi: user's local network
- SSH: enabled
- Raspberry Pi Connect: disabled

Do not explain why this OS was chosen unless the user asks.

## 2. Assemble Hardware

After Raspberry Pi Imager finishes setting up the card, walk the user through these steps one at a time in this exact order. Do not let the user power on the Pi or attach parts out of order.

1. Insert the microSD card.
2. Connect the camera ribbon. Be specific for first-timers: find the tiny camera connector on the Raspberry Pi, gently lift the dark latch, slide the ribbon in straight, then press the latch back down. The exposed metal contacts on the ribbon should face the contacts inside the slot. Do not force it; if it does not slide in, stop and check orientation against `docs/tutorial-assets/02-connect-camera-ribbon.gif`.
3. Install the PiSugar 3 board and battery.
4. Press the Display HAT Mini onto the Pi headers.
5. Plug a USB-C power cable into the PiSugar 3 charging/power port.
6. Power on from the PiSugar shutter/Power button on the side opposite the USB-C port: tap once, then hold for about 8 seconds, then release.
7. Wait 4 minutes. The screen will probably still be black at this stage; that is expected. Make sure the user's Mac is on the same Wi-Fi network they configured in Raspberry Pi Imager.

Success for this stage is not visual. The next SSH step proves whether the Pi finished booting and joined Wi-Fi.

Use the local tutorial images when helpful:

- `docs/tutorial-assets/01-insert-microsd.gif`
- `docs/tutorial-assets/02-connect-camera-ribbon.gif`
- `docs/tutorial-assets/03-install-pisugar.gif`
- `docs/tutorial-assets/04-attach-display.gif`

If an official social post or video is available for this build, include that link as an optional visual reference. Do not block the build if the link is unavailable.

## 3. Confirm The Pi Is Reachable With SSH

Have the user open a real terminal app on their Mac:

- Open the **Terminal** app from Spotlight or Applications > Utilities.

Then try:

```bash
ssh imagegencam@imagegencam.local
```

If SSH asks whether to continue connecting, tell the user to type `yes`. When it asks for the Pi password, tell them to type the password they chose in Raspberry Pi Imager; the terminal may look blank while they type.

If hostname discovery fails, help the user find the Pi IP from their router, hotspot, or `arp -a`.

Success looks like the user reaches a Pi shell prompt. This only proves that the Pi is reachable; it is not the main work environment for the rest of the build.

## 4. Open A Remote Codex Session On The Pi

After SSH works, do not continue the rest of the build as pasted SSH commands unless Codex CLI is not ready on the Pi or the user explicitly wants the manual route.

If the user is still inside the Pi SSH terminal, have them type `exit` so they are back on their Mac.

Before opening Codex Desktop remote SSH, set up a concrete SSH alias and SSH key.

Tell the user to open the **Terminal** app and run this from the repo folder on their Mac:

```bash
./scripts/setup_mac_ssh_to_pi.sh imagegencam.local
```

If `.local` failed and an IP worked, use:

```bash
./scripts/setup_mac_ssh_to_pi.sh <pi-ip-address>
```

Codex Desktop remote SSH needs the `codex` command installed and authenticated on the Pi before the desktop app can open a remote project there. Check it from the user's Mac:

```bash
ssh imagegencam 'command -v codex && codex --version'
```

For DIY setups this will usually be missing. Install Codex CLI in one normal SSH Terminal session.

First connect to the Pi:

```bash
ssh imagegencam
```

Wait until the prompt looks like `imagegencam@imagegencam:~ $`. Then paste the Pi-side install commands:

```bash
sudo apt update
sudo apt install -y curl git
curl -fsSL https://chatgpt.com/codex/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
command -v codex && codex --version
```

Do not put `ssh imagegencam` and the install commands in the same paste block. If the user pastes both at once, the terminal can accidentally run nested SSH commands inside the Pi session.

Before the first `codex` run, prepare the user to get an OpenAI API key:

```text
https://platform.openai.com/api-keys
```

Tell them to create a new secret key:

- Name: `imagegencam`
- Project: use the default/current project unless they know they need another one
- Permissions: `All`

The first `codex` run may ask the user to authenticate with a ChatGPT account or an API key. For this tutorial, prefer the API key flow. Have the user paste the API key only into the Pi terminal when Codex asks for it. Do not ask them to paste the key into chat.

Then, while still inside the Pi SSH session, run:

```bash
codex
```

After Codex opens and authentication succeeds, tell the user to press **Control-C** until they are back at the Pi shell prompt. Do not say "tell me when you're back at the prompt" without explaining how to leave the interactive Codex session.

Do not continue to Codex Desktop remote SSH until `codex` runs successfully on the Pi.

Make sure the repo folder exists on the Pi before choosing it in Codex Desktop. This is needed because remote Codex works inside the Pi filesystem, not the temporary Mac clone used for helper scripts:

```bash
ssh imagegencam 'mkdir -p ~/Documents && cd ~/Documents && if [ ! -d imagegencam ]; then git clone https://github.com/openai/imagegencam.git; fi'
```

Then verify:

```bash
ssh imagegencam 'hostname && test -d ~/Documents/imagegencam && command -v codex'
```

Then tell the user to open Codex Desktop on their Mac:

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

Success looks like Codex Desktop is connected to the Pi and the terminal/workspace path is on the Pi, not on the user's Mac. If unsure, ask the user or run:

```bash
hostname
pwd
uname -a
```

## 5. Update and Install Base Packages In Remote Codex

Run:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

The remote session will disconnect because the Pi is rebooting. Wait 60-90 seconds, then reopen the same remote Codex project. If the remote Codex session does not reconnect cleanly, use Mac Terminal to check that the Pi is back:

```bash
ssh imagegencam 'hostname && echo pi back online'
```

Package installation uses `sudo`, so do not run it from a hidden Codex tool
terminal if the Pi may ask for the password. Tell the user to open the
**Terminal** app on their Mac, connect with `ssh imagegencam`, and run:

```bash
sudo apt install -y git python3-venv python3-picamera2 python3-pil python3-pip network-manager avahi-daemon nodejs npm
```

After the user says it completed, continue from Codex and verify with read-only
commands.

## 6. Verify Hardware Before App Setup

Do not skip hardware checks. A broken camera/display setup is harder to debug after the app is installed.

Camera:

```bash
rpicam-hello --list-cameras
```

Display SPI:

This uses `sudo`. If the Pi may ask for a password, hand it to the user's
visible Terminal instead of running it in remote Codex:

```bash
sudo raspi-config nonint do_spi 0
```

Display library:

This installer also uses `sudo`. Hand the whole block to the user's visible
Terminal if the Pi may ask for a password:

```bash
cd ~
git clone https://github.com/pimoroni/displayhatmini-python
cd displayhatmini-python
sudo ./install.sh
python3 -c "import displayhatmini; print('displayhatmini ok')"
```

PiSugar:

```bash
systemctl status pisugar-server --no-pager
```

On a fresh SD card, `pisugar-server` will usually be missing. Install PiSugar Power Manager before continuing:

This also starts with `sudo`. Use the visible Terminal handoff if the Pi may ask
for a password:

```bash
sudo raspi-config nonint do_i2c 0
cd ~
wget https://cdn.pisugar.com/release/pisugar-power-manager.sh
bash pisugar-power-manager.sh -c release
```

If the installer asks for a model, choose **PiSugar 3**. Then verify:

```bash
sudo systemctl enable --now pisugar-server
systemctl status pisugar-server --no-pager
printf 'get model\nget battery\nget battery_v\n' | nc -w 2 127.0.0.1 8423
```

## 7. Clone and Configure the App

Run:

```bash
cd ~/Documents
test -d imagegencam || git clone https://github.com/openai/imagegencam.git
cd ~/Documents/imagegencam/software
./scripts/setup.sh
```

When setup asks for an OpenAI API key, send the user to:

```text
https://platform.openai.com/api-keys
```

Do not ask them to paste the key into chat.

## 8. Manual Run

Run:

```bash
./scripts/run.sh
```

Success:

- boot image appears
- live viewfinder appears
- local web app is reachable at `http://imagegencam.local:8000`

Before installing the boot service, get the user into the mobile app:

1. Put the phone on the same Wi-Fi network as the camera.
2. Open `http://imagegencam.local:8000`.
3. If that does not load, run `hostname -I` on the Pi and open `http://<pi-ip>:8000`.
4. Have the user edit a prompt and confirm it autosaves.

Find the Pi IP with:

```bash
hostname -I
```

## 9. Install Auto-Start

Only do this after manual run succeeds:

```bash
./scripts/install_service.sh
sudo systemctl enable --now imagegencam.service
```

Verify:

```bash
sudo systemctl status imagegencam.service
sudo journalctl -u imagegencam.service -n 100 --no-pager
```

The installed service runs the web app on port 80, so the normal phone URL becomes:

```text
http://imagegencam.local
```

If `.local` fails after service install, run `hostname -I` on the Pi and open `http://<pi-ip>`.

Then test that the camera really starts on boot:

```bash
sudo reboot
```

Wait about a minute. The display should show the boot image and then live preview. Reconnect from Codex Desktop or SSH and verify:

```bash
sudo systemctl status imagegencam.service --no-pager
```

## 10. Maintenance Commands

Restart:

```bash
sudo systemctl restart imagegencam.service
```

Stop while editing:

```bash
sudo systemctl stop imagegencam.service
```

Follow logs:

```bash
sudo journalctl -u imagegencam.service -f
```

Safe shutdown:

```bash
sudo shutdown now
```

Normal physical power-off: hold the PiSugar shutter/Power button on the side opposite the USB-C port until the screen goes off, then release.
