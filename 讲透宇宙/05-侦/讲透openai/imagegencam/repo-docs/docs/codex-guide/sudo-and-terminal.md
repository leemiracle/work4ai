# Sudo And Terminal Handoff

Use this when a command needs `sudo`, asks for the Pi password, or blocks inside remote Codex.

## Rules

- Never ask the user to paste the Pi password into chat.
- Never ask the user to paste an OpenAI API key into chat.
- Never run password-prompting `sudo` commands in Codex's hidden tool terminal.
  The user cannot see or answer that prompt there.
- Do not use `sudo -S`.
- Keep Terminal handoff blocks short.
- After the user says the block is done, verify with read-only commands.

## Prebuilt Kit Password Change

If the user has a prebuilt kit, the first-boot screen may show a shared starter password. Have the user change it in a normal SSH Terminal session before API key setup:

```bash
ssh imagegencam@imagegencam.local
```

After the Pi shell prompt appears, run:

```bash
passwd
```

If `.local` failed, use the IP shown on the device screen:

```bash
ssh imagegencam@<pi-ip-address>
```

After the Pi shell prompt appears, run:

```bash
passwd
```

Tell the user the password input may look blank while they type. Do not ask them to paste either password into chat.

## Flow

1. Explain why admin access is needed.
2. Tell the user to open the **Terminal** app on their Mac.
3. Have them connect:

```bash
ssh imagegencam
```

4. Give only the small privileged block they need.
5. Ask them to come back and say whether it completed or share the error message with any passwords, tokens, or API keys removed.
6. Continue in remote Codex after verification.

## Example

For package install:

```bash
sudo apt update
sudo apt install -y git python3-venv python3-picamera2 python3-pil python3-pip network-manager nodejs npm
```

Verify afterward:

```bash
python3 -m venv --help >/dev/null && echo "venv ok"
rpicam-hello --list-cameras
```

## Prefer Verification Over Repetition

If a command may already have run on the prebuilt kit, check before reinstalling:

```bash
command -v rpicam-hello
python3 -c "import displayhatmini; print('displayhatmini ok')"
systemctl status pisugar-server --no-pager
```
