# Migrate to Kernel Repo

A small tool that helps migrate kernels in model repos into their own kernel repos on the Hugging Face Hub. It clones the model repo, squashes all branches into one commit, and pushes to a new kernel repo.

## Requirements

- Python 3.13+
- `git` and `git-lfs` installed
- SSH access to Hugging Face Hub
- `HF_TOKEN` environment variable with write-access permissions

## Install

```bash
pip install git+https://github.com/drbh/migrate-to-kernel-repo-tool
```

Or install locally for development:

```bash
pip install -e .
```

## Usage

Run on a repo to migrate it to a kernel repo on the Hugging Face Hub:

```bash
migrate-to-kernel-repo kernels-test/relu-tvm-ffi
```

Migrate multiple repos:

```bash
migrate-to-kernel-repo org/model-a org/model-b
```

Migrate from a batch file:

```bash
migrate-to-kernel-repo --batch repos.txt
```

### Options

```
positional arguments:
  REPO_ID               One or more repo IDs to migrate (e.g. kernels-community/relu)

options:
  -b, --batch PATH      Path to a file containing repo IDs, one per line
  -n, --dry-run         Show what would be done without doing it
  -k, --keep            Keep local clone after migration
  -w, --work-dir DIR    Directory for cloned repos (default: temp directory)
  --private             Create the kernel repo as private
```

## Example output

```txt
Migrating 1 repo(s)...

repo:       kernels-test/relu-tvm-ffi
model url:  git@hf.co:kernels-test/relu-tvm-ffi
kernel url: git@hf.co:kernels/kernels-test/relu-tvm-ffi
creating kernel repo on Hub...
cloning model repo...
  $ git clone git@hf.co:kernels-test/relu-tvm-ffi /tmp/migrate-kernel-kernels-test--relu-tvm-ffi
    Cloning into '/tmp/migrate-kernel-kernels-test--relu-tvm-ffi'...
    Filtering content: 100% (6/6), 11.35 MiB | 7.09 MiB/s, done.
fetching LFS objects...
  $ git lfs fetch --all origin
    19 objects found, done.
    Fetching all references...
branches: ['main', 'v1']
squashing branches...
  squashing main
  squashing v1
pushing to kernel repo...
  $ git push --force --all origin
    Uploading LFS objects: 100% (6/6), 12 MB | 0 B/s, done.
    To hf.co:kernels/kernels-test/relu-tvm-ffi
     + ad06d39...29cea97 main -> main (forced update)
     * [new branch]      v1 -> v1
migration complete: https://huggingface.co/kernels-test/relu-tvm-ffi
cleaning up local clone

Results: 1 succeeded, 0 failed
```
