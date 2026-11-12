---
name: setup-autodesk-fusion
description: Configure and diagnose Fusion interoperability, transport selection, scoped profiles and qualification. Use for setup or connection problems, not design edits.
---

Call `fusion_connection_status` and `fusion_capabilities_list` first. Distinguish synthetic fixture, managed and assisted modes. Fixture output is not evidence that Autodesk is installed.

Read [setup](../../README.md) and resolve the installed plugin root. Use its bundled CLI without startup npm. Discover the explicitly configured native endpoint and enroll the actual Python tool/schema hash; never guess tools, scan ports or silently switch transports. For the typed add-in, install the assembled package and follow [the add-in guide](../../addin/README.md).

For additional required native arguments, use `native-enroll --fixed-arguments-file` with a trusted absolute JSON-object file and explicitly reviewed values. Do not infer defaults, reuse an old mapping's values or override the script argument. An optional `--url` is saved as the selected endpoint. Enrollment rejects changed profiles and never executes the native tool or establishes qualification.

Use a trusted private profile for the user's scope. Existing valid grants cover routine work; changed target, billing, publication or manufacturing risk needs matching authority. Never edit policy to bypass a denial or invent qualification evidence.

Cloud PKCE and native Data MCP authentication are separate. Let the user complete the supported Autodesk sign-in URL; never collect passwords or copy Codex credentials. Enterprise extensions are privileged deployment code.

Run [qualification](../../docs/qualification.md) on approved synthetic documents. Report the connection evidence and exact remaining configuration or licensed-environment gate.
