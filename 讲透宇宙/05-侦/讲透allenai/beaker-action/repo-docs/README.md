# beaker-command

A GitHub Action for using the Beaker CLI.

## Inputs

### `token` (required)

Your Beaker [token](https://beaker.org/user).

### `command` (required)

The Beaker command to run (e.g. `image` or `experiment`).

### `args` (required)

The arguments to the Beaker command.

## Example

```yaml
uses: allenai/beaker-command@v0
with:
  token: ${{ secrets.BEAKER_TOKEN }}
  command: account
  args: whoami
```
