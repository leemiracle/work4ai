# Troubleshooting

Use this when something fails. Keep diagnostics small and specific.

## Service Health

Status:

```bash
sudo systemctl status imagegencam.service --no-pager
```

Recent logs:

```bash
sudo journalctl -u imagegencam.service -n 100 --no-pager
```

Follow logs:

```bash
sudo journalctl -u imagegencam.service -f
```

Stop while editing:

```bash
sudo systemctl stop imagegencam.service
```

## Camera App Crash Loop

If systemd repeatedly restarts the app, stop it first:

```bash
sudo systemctl stop imagegencam.service
```

Then check:

```bash
rpicam-hello --list-cameras
```

If Picamera2 logs `IndexError: list index out of range`, it usually means the camera stack sees no camera.

## Image Generation Fails

Check local config exists:

```bash
test -f ~/Documents/imagegencam/software/.env && echo ".env exists"
```

Check API key is set without printing it:

```bash
grep -q '^OPENAI_API_KEY=.' ~/Documents/imagegencam/software/.env && echo "API key present"
```

Check queue:

```bash
find ~/Documents/imagegencam/software/data/queue -type f | sort
```

Pending queue files mean work is preserved and should retry later.

## Web App Does Not Open

Check service:

```bash
sudo systemctl status imagegencam.service --no-pager
```

Check IP:

```bash
hostname -I
```

Check port:

```bash
ss -ltnp | grep -E ':(80|8000)' || true
```

Manual runs listen on port 8000. The installed service listens on port 80 so users can open `http://imagegencam.local`.

The web app is intentionally local-LAN only.

## Wi-Fi Change Failed

Do not delete saved connections while debugging. First list known profiles:

```bash
nmcli -t -f NAME,TYPE,AUTOCONNECT,DEVICE connection show
```

Show nearby Wi-Fi:

```bash
nmcli -t -f active,ssid,signal,security dev wifi list --rescan yes
```

Reconnect a known good profile:

```bash
sudo nmcli connection up id "PROFILE_NAME"
```

The on-device Wi-Fi selector schedules rollback before trying a new network. If the user does not press KEEP on the device, it should return to the previous active profile automatically.

If the display says activation failed and NetworkManager logs `Not authorized to control networking`, reinstall the service files:

```bash
cd ~/Documents/imagegencam/software
./scripts/install_service.sh
sudo systemctl restart imagegencam.service
```

That installs the narrow sudoers rule used for non-interactive Wi-Fi switching from the camera service.

## High CPU or Sluggish Preview

Check processes:

```bash
ps -eo pid,comm,args,%cpu,%mem --sort=-%cpu | head -20
```

Stop the app while editing:

```bash
sudo systemctl stop imagegencam.service
```

The Pi Zero 2 W is small. Avoid desktop, browser rendering, or extra services during camera use.

## Prompt/Web Data

Runtime data lives in:

```text
~/Documents/imagegencam/software/data
```

Do not commit personal runtime data unless the user intentionally wants it in the repo.
