# NVIDIA Networking YANG

This repository publishes the YANG models supported over the gNMI interface for each Cumulus and NVOS release.

Top-level directories correspond to releases of Cumulus Linux or NVOS. Under each release, you will find:

- **gnmi-supported-paths.html** — Browsable guide to the YANG paths supported in that release
- **ietf/** — IETF-defined YANG modules
- **not-supported/** — YANG deviations for IETF and OpenConfig paths not supported by the release
- **openconfig/** — OpenConfig YANG modules plus NVIDIA augmentations (in `openconfig/nvidia`)
