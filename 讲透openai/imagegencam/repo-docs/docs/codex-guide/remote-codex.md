# Remote Codex Handoff

Use this when the Pi is on Wi-Fi and the user needs Codex Desktop on their Mac to control the Raspberry Pi over the local network.

## Principle

Plain SSH proves the user's Mac can reach the Pi. Remote Codex is the working environment. Once remote Codex is connected, commands should run on the Pi, not on the user's Mac.

Codex Desktop remote SSH needs three things before the remote session can start:

- a concrete host alias for `imagegencam`
- working SSH from the user's Mac to the Pi, preferably with SSH keys so Codex Desktop is not blocked by password prompts
- the `codex` command installed and authenticated on the Pi user's login-shell `PATH`

## Easiest Path

Do this before opening the Pi from Codex Desktop.

First set up the SSH alias and SSH key. Tell the user to open the **Terminal** app from Spotlight or Applications > Utilities. From this repo on the Mac:

```bash
./scripts/setup_mac_ssh_to_pi.sh imagegencam.local
```

If `.local` is unreliable, use the Pi IP:

```bash
./scripts/setup_mac_ssh_to_pi.sh <pi-ip-address>
```

The script should finish with `ssh key ok`. If the user is still inside a Pi SSH shell, have them type `exit` first so this command runs on their Mac.

Then verify the remote Codex command from the user's Mac:

```bash
ssh imagegencam 'command -v codex && codex --version'
```

If that prints a path and version, SSH into the Pi and run the first interactive Codex session:

```bash
ssh imagegencam
```

Wait until the prompt looks like `imagegencam@imagegencam:~ $`, then run:

```bash
codex
```

Before the first `codex` run, prepare the user to get an OpenAI API key:

```text
https://platform.openai.com/api-keys
```

Tell them to create a new secret key:

- Name: `imagegencam`
- Project: use the default/current project unless they know they need another one
- Permissions: `All`

The first `codex` run may ask the user to authenticate with a ChatGPT account or an API key. For this tutorial, prefer the API key flow. Have the user paste the API key only into the Pi terminal when Codex asks for it. This is separate from the camera app's later `.env` setup, even if the user chooses to reuse the same OpenAI API key. After Codex opens successfully, tell the user to press **Control-C** until they are back at the Pi shell prompt.

If `codex` is missing, SSH into the Pi first:

```bash
ssh imagegencam
```

Wait until the prompt looks like `imagegencam@imagegencam:~ $`, then paste the Pi-side install commands:

```bash
sudo apt update
sudo apt install -y curl git
curl -fsSL https://chatgpt.com/codex/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
command -v codex && codex --version
```

Then run Codex:

```bash
codex
```

Do not give the user one paste block that starts with `ssh imagegencam` and also includes Pi-side commands. That can accidentally run nested SSH inside the Pi session.

Do not continue to Codex Desktop remote SSH until `codex` runs successfully on the Pi.

Make sure the project folder exists on the Pi before opening the remote chat. This copies the project onto the Pi so remote Codex can read, edit, and run the camera code on the Pi filesystem:

```bash
ssh imagegencam 'mkdir -p ~/Documents && cd ~/Documents && if [ ! -d imagegencam ]; then git clone https://github.com/openai/imagegencam.git; fi'
```

Then have the user open Codex Desktop on their Mac:

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

## Manual SSH Config

If the helper script is unavailable, add this to `~/.ssh/config` on the Mac:

```sshconfig
Host imagegencam
  HostName imagegencam.local
  User imagegencam
  IdentityFile ~/.ssh/imagegencam_ed25519
  IdentitiesOnly yes
```

Use the Pi IP for `HostName` if `.local` failed. Then create the dedicated key if needed and copy the local public key to the Pi:

```bash
test -f ~/.ssh/imagegencam_ed25519 || ssh-keygen -t ed25519 -f ~/.ssh/imagegencam_ed25519 -N "" -C imagegencam
cat ~/.ssh/imagegencam_ed25519.pub | ssh imagegencam@imagegencam.local 'umask 077; mkdir -p ~/.ssh; touch ~/.ssh/authorized_keys; key="$(cat)"; grep -qxF "$key" ~/.ssh/authorized_keys || printf "%s\n" "$key" >> ~/.ssh/authorized_keys'
```

After this, `ssh imagegencam` should connect without asking for the Pi password.

## Verify Remote Context

In remote Codex, run:

```bash
hostname
pwd
uname -a
command -v codex
```

Success looks like:

- `hostname` is `imagegencam`
- `pwd` is under `/home/imagegencam`
- `uname -a` reports Linux on Raspberry Pi hardware
- `command -v codex` returns a path

If commands run on the user's Mac, stop and reconnect Codex to the SSH host before installing packages or editing files.

## Common Failures

- `.local` does not resolve: use the router, hotspot client list, or `arp -a` to find the Pi IP.
- `codex` is missing on the Pi: connect with SSH first, then run the install block above in the Pi shell.
- SSH still asks for a password after setup: rerun `./scripts/setup_mac_ssh_to_pi.sh <pi-ip-address>` and confirm the final `ssh key ok` message.
- SSH alias points at an old IP: rerun `./scripts/setup_mac_ssh_to_pi.sh imagegencam.local`; the helper removes old exact `Host imagegencam` blocks before writing the new one.
- SSH host key changed after reflashing or reusing the same hostname: run `ssh-keygen -R imagegencam.local`, `ssh-keygen -R imagegencam`, and `ssh-keygen -R <pi-ip-address>`, then connect again.
- Password prompt blocks Codex: use `sudo-and-terminal.md` for a small Terminal handoff.
