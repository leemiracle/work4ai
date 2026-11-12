# Security Policy: cstruct

## Reporting a Vulnerability

If you discover a potential security vulnerability, please **do not open a public
GitHub issue, discussion, or pull request.**

- **Web (preferred):** [NVIDIA Vulnerability Disclosure Program](https://www.nvidia.com/en-us/security/)
- **E-mail:** [psirt@nvidia.com](mailto:psirt@nvidia.com)
  - For secure communication, use the [NVIDIA public PGP key](https://www.nvidia.com/en-us/security/pgp-key).
- **GitHub:** Use this repository's **Security** tab and select **Report a vulnerability**.

Please include:

- Project name (`cstruct`) and the affected branch, commit, or module version
- Affected API (`Examine`, `Pack`, `Unpack`) and input shape when relevant
- Vulnerability type, reproduction steps, proof-of-concept if available, and impact assessment

NVIDIA's Product Security Incident Response Team (PSIRT) will acknowledge the report,
validate severity, coordinate remediation, and publish a security bulletin when
appropriate. See [PSIRT policies](https://www.nvidia.com/en-us/security/psirt-policies/).

## Supported Versions

`cstruct` is developed on the `development` branch. Security fixes land there
unless a release branch is explicitly announced.

| Version or branch | Supported |
| --- | --- |
| `development` | Yes |
| Older tags / branches | No, unless explicitly stated |

## Security Architecture & Context

`cstruct` is a Go library that serializes and deserializes Go structs in a
cstruct-style layout (`Examine`, `Pack`, `Unpack`) with selectable byte order.
It has no network listeners, credentials, or persistence layer of its own.

This software operates at the **library** level. Its primary security
responsibility is safe handling of caller-supplied structs and byte slices so
that pack/unpack cannot corrupt memory outside those buffers or be treated as an
authorization boundary for privileged data.

**Repository Exposure Classification:** Public.
Basis: origin remote is the publicly accessible `NVIDIA/cstruct` GitHub repository.

**Service Exposure Classification:** External / Regulated (high confidence).
Basis: externally distributed open-source Go library under the NVIDIA GitHub
organization.

Key security boundaries:

- Callers supply both the Go value graph and the `[]byte` buffers.
- Reflection-based packing/unpacking must respect sizes reported by `Examine`
  and must not assume input length or struct layout trust beyond what the
  caller intentionally provides.

### Threat Model

1. **Hostile byte slices into `Unpack`:** Malformed or truncated input causes
   panics, excessive allocation, or incorrect field population that callers
   later treat as trusted structured data.
2. **Unexpected struct shapes into `Pack`/`Examine`:** Pointer cycles,
   unsupported field types, or trailing-slice edge cases lead to incorrect
   sizes, panics, or incomplete serialization.
3. **Misuse as a trust boundary:** Applications that unpack untrusted network or
   file bytes with `cstruct` and then act on the result without further
   validation inherit integrity failures as application-level bugs.

### Critical Security Assumptions

- Callers validate semantic correctness of unpacked data for their protocol.
- `cstruct` does not authenticate, encrypt, or integrity-protect payloads.
- The Go runtime and standard `encoding/binary` behavior are trusted substrates.
- This library is not a multi-tenant or privilege boundary.

## Out of Scope

- Application protocols that choose insecure layouts or skip validation after
  `Unpack`.
- Denial of service from intentionally feeding pathological inputs in a local
  test harness without isolation.
- Issues solely in dependent applications that embed `cstruct`.
