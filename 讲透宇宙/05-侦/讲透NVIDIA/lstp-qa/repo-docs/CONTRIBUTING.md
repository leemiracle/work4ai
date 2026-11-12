# Contributing

Thank you for your interest in contributing to LSTP QA. These guidelines are
intended to help your contribution get reviewed and merged quickly.

Any contribution you make to this repository is under the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0.html),
as stated in each source file.

## How to contribute

1. Create a feature branch from `main` (fork the repository first if you are
   contributing from outside the project).
2. Follow the Python coding style in [README.md](README.md#python-coding-style).
3. Add SPDX license headers to new or modified source files (see existing
   `*.py` files for the required format).
4. Confirm your work can be contributed under this license (no license or
   patent conflict). You must [`sign off`](#signing-your-work) on every commit.
5. Keep pull requests focused on a single concern; avoid commented-out code.
6. Run `./style/lint` before opening a pull request. Pytest requires LSTP hardware
   and is run manually (see [README.md](README.md)).
7. Open a pull request against `main` with a clear description. All submissions
   require review; see [MAINTAINERS.md](MAINTAINERS.md).

## Security

Do not report security vulnerabilities in public GitHub issues or pull requests.
See [SECURITY.md](SECURITY.md) for how to report them to NVIDIA PSIRT.

## Signing Your Work
* We require that all contributors "sign-off" on their commits. This certifies that the contribution is your original work, or you have rights to submit it under the same license, or a compatible license.
  * Any contribution which contains commits that are not Signed-Off will not be accepted.
* To sign off on a commit you simply use the `--signoff` (or `-s`) option when committing your changes:
  ```bash
  git commit -s -m "Add cool feature."
  ```
  This will append the following to your commit message:
  ```text
  Signed-off-by: Your Name <your@email.com>
  ```
* Full text of the DCO (https://developercertificate.org):
  ```text
    Developer Certificate of Origin
    Version 1.1
    Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
    Everyone is permitted to copy and distribute verbatim copies of this
    license document, but changing it is not allowed.
    Developer's Certificate of Origin 1.1
    By making a contribution to this project, I certify that:
    (a) The contribution was created in whole or in part by me and I
        have the right to submit it under the open source license
        indicated in the file; or
    (b) The contribution is based upon previous work that, to the best
        of my knowledge, is covered under an appropriate open source
        license and I have the right under that license to submit that
        work with modifications, whether created in whole or in part
        by me, under the same open source license (unless I am
        permitted to submit under a different license), as indicated
        in the file; or
    (c) The contribution was provided directly to me by some other
        person who certified (a), (b) or (c) and I have not modified
        it.
    (d) I understand and agree that this project and the contribution
        are public and that a record of the contribution (including all
        personal information I submit with it, including my sign-off) is
        maintained indefinitely and may be redistributed consistent with
        this project or the open source license(s) involved.
  ```