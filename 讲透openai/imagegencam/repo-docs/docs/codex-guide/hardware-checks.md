# Hardware Checks

Use this when a component may not be connected, enabled, or detected.

If a fix uses `sudo` and may ask for the Pi password, do not run it in Codex's
hidden tool terminal. Tell the user to run the short command block in their
visible Mac Terminal over `ssh imagegencam`, then verify here afterward.

## Camera

Check:

```bash
rpicam-hello --list-cameras
```

Expected: at least one camera is listed.

If no camera appears:

- Stop the app service if it is running.
- Power down safely.
- Reseat the camera cable.
- Confirm the cable orientation.
- Boot and run the check again.

Do not continue to app debugging until the camera appears here.

## Display HAT Mini

Enable SPI:

```bash
sudo raspi-config nonint do_spi 0
```

Verify Python import:

```bash
python3 -c "import displayhatmini; print('displayhatmini ok')"
```

If import fails, install the library:

```bash
cd ~
git clone https://github.com/pimoroni/displayhatmini-python
cd displayhatmini-python
sudo ./install.sh
```

If the import works but the screen is blank, check service logs and confirm the Display HAT Mini is fully seated on the headers.

## PiSugar 3

Check service:

```bash
systemctl status pisugar-server --no-pager
```

Check local TCP API:

```bash
printf 'get model\nget battery\nget battery_v\n' | nc -w 2 127.0.0.1 8423
```

Expected:

- model reports PiSugar 3
- battery reports a percentage
- voltage is plausible for a LiPo battery

If the app battery icon looks wrong, prefer `pisugar-server` readings before raw I2C register readings.

Power button behavior:

- power on: use the PiSugar shutter/Power button on the side opposite the USB-C port; tap once, then hold it for about 8 seconds, then release
- power off: hold the PiSugar shutter/Power button down until the screen goes off, then release

## Network

Show IP:

```bash
hostname -I
```

Show Wi-Fi:

```bash
nmcli -t -f active,ssid dev wifi | grep '^yes:' || true
```

The phone must be on the same LAN to open:

```text
http://imagegencam.local:8000
```

During manual runs, if `.local` fails on the phone, use `http://<pi-ip>:8000` instead. After the auto-start service is installed, use `http://imagegencam.local` or `http://<pi-ip>`.

## On-Device Wi-Fi Selector

From live preview, triple-tap the top-right button to open the connection screen. It shows the current Wi-Fi network and a QR code for the phone app.

Controls:

- top-left: open Wi-Fi settings
- bottom-left: exit back to live preview
- top-right: open the deeper diagnostics screen with CPU, MAC address, and IP address

The selector must remain non-destructive:

- saved NetworkManager profiles are never deleted
- saved networks can be selected without retyping passwords
- selecting a network opens a detail screen before connecting
- saved network passwords can be re-entered from the detail screen
- new networks use an on-screen keyboard
- connection attempts schedule rollback to the previous active profile
- the user must confirm the new network on the device to keep it
