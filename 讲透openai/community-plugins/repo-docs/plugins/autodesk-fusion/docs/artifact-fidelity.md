# Artifact fidelity and provenance

New desktop artifact receipts use `manifest_version: 2`. A successful receipt means that the broker observed a successful producer response, checked the output files against the bounded checks below, and bound the result to its producing plan. It does **not** establish source-shape equivalence, correct rendered appearance, engineering approval, or suitability for manufacture.

This implements the artifact-recording part of implementation-plan §9.5 and strengthens W14 export/capture validation. Qualified Fusion round trips, image review, engineering measurements, target-system compatibility, and machine-specific manufacturing review remain separate acceptance work. Additional exchange formats require their own reviewed producer and validator; a filename extension does not add support.

## Completion and quarantine

1. Preparing an artifact operation reserves an approved output root, unique artifact directory, filename, format, and manifest version in the immutable producer plan.
2. Execution creates the private directory. Output bytes remain quarantined while the operation or provider future is incomplete. Reading an artifact, including a valid-looking file, cannot finalize it.
3. Only the broker's retained successful dispatch or future-poll response may call completion. An asynchronous response must identify the exact submitted future and explicit `succeeded` status. The complete stored producer content is hashed again before its source observations become provenance; two matching hash fields alone are insufficient. Source/document and producer/reservation contradictions fail validation.
4. The broker checks the actual bounded files. For a single-file output, a provider-reported SHA-256 or byte count must match the locally inspected bytes whenever the provider supplied those fields. Bundle hash semantics are not guessed: HTML/NC packages bind every enumerated file independently.
5. Passing checks produce the versioned immutable manifest. A later inspection rechecks the file hashes and declared validation grade without rewriting the receipt. Failures retain the output as quarantined evidence; there is no write replay, rollback, repair, upload, machine transfer, or automatic opening of active content.

The existing filesystem controls still apply: an approved canonical root, one unique private output directory, no symbolic/hard links, no Unicode/case aliases, bounded ordinary files, at most 500 entries and 256,000,000 total bytes, and at most eight directory levels for HTML packages. Other single-file formats reject undeclared auxiliary files. The PNG/STL parsers independently enforce their own limits even when called outside the artifact manager.

## Validation grades

| Output | Version 2 checks | Deliberate limits |
| --- | --- | --- |
| Viewport/render PNG | PNG signature; first and unique IHDR; legal dimensions and basic coding fields; bounded chunk lengths/count; ASCII chunk types and reserved bit; every chunk CRC; supported critical-chunk order and palette rules; consecutive nonempty image-data stream; final IEND; exact requested width and height | Compressed pixels and text are not inflated. Ancillary chunk semantics, APNG consistency, pixel appearance, camera correctness, and visual content are not qualified. |
| STL | Binary fixed-record size/count or one ASCII solid with complete triangular facet grammar; finite normal and vertex components; nonzero facet count; coordinate minimum/maximum; encoding consistent with the bound binary desktop export settings | Does not verify normals' direction or length, nondegenerate triangles, winding, manifoldness, watertightness, intersections, tessellation fidelity, physical scaling, or color/attribute conventions. |
| STEP | Nonempty file, envelope markers, bytes/hash | Does not parse the exchange model or establish topology, dimensions, materials, or metadata parity. |
| F3D | Nonempty file, archive signature, bytes/hash | No archive extraction. Internal completeness and target Fusion compatibility require a qualified reopen. |
| Drawing PDF / flat-pattern DXF | Nonempty file, bounded format-specific signature/framing, bytes/hash | No sheet-count, drawing dimension, layer, manufacturing, or source-equivalence qualification. |
| NC / HTML setup-sheet package | Bounded package enumeration and per-file hashes; existing NC text / HTML / CSS / JPEG checks; PNG auxiliaries receive container checks without a requested image-size claim | No NC execution/simulation, collision check, machine release, or HTML sanitization. Embedded content must not be opened or published automatically. |

PNG checks follow the critical container structure in the [W3C PNG specification](https://www.w3.org/TR/png-3/). A valid CRC is a byte-consistency check, not proof that compressed pixels decode. Receipts say `pixel_data_decoded: false`; unsupported animation semantics are explicitly outside the grade, even if animation-related chunks are observed.

The generic STL parser accepts both [registered STL encodings](https://www.iana.org/assignments/media-types/model/stl). Exact binary record length takes precedence over an ASCII-looking header because binary headers can start with `solid`. ASCII admission is a bounded single-solid, line-oriented subset: three finite decimal/exponent normal components, exactly three vertices per facet, and complete loop/facet/solid terminators. Binary attribute words are counted when nonzero but are not interpreted. Multi-solid ASCII, arbitrary extensions, control characters, nondecimal numbers, and trailing data are rejected.

Parser bounds are 256,000,000 input bytes, 100,000 PNG chunks, 64,000,000 declared PNG pixels, 5,000,000 STL triangles, 1,024 bytes per ASCII STL line, and 128 characters per numeric token. These are plugin admission bounds, not advertised Fusion or format maxima. The parsers retain a bounded summary rather than a mesh-sized vertex collection and never extract an archive or expand compressed data.

The reviewed desktop STL producer requests binary output, one file for the selected geometry, explicit/default `mm` units, and explicit/default `high` refinement. Version 2 therefore rejects ASCII bytes from that producer even though the generic parser can inspect ASCII. Actual units cannot be recovered from STL coordinates: [Fusion's `STLExportOptions.unitType`](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/STLExportOptions_unitType.htm) is a producer setting. The receipt keeps requested/provider-reported units separate from coordinate bounds, whose unit is `file_coordinates_without_embedded_unit`.

## Portable provenance

The version 2 canonical manifest binds the artifact/root/relative filename/format, producing plan ID/hash, completion time, per-file size/hash/checks/validation, bounded provenance, and limitation text. Absolute local storage paths remain operational receipt fields; they are not included in the portable provenance projection. A SHA-256 is a consistency binding within the trusted local record store, not a digital signature or independently authenticated Autodesk attestation.

| Field | Evidence source |
| --- | --- |
| `producer.plan_id`, `plan_hash`, `operation`, handler/execution-contract/profile hashes | Stored producing plan admitted by the engine, with its complete immutable content binding recomputed at completion; its staged artifact must still match |
| `producer.provider_kind` | Actual broker provider instance: `native_mcp`, `typed_addin`, `synthetic_fixture`, or `unverified_provider` |
| `producer.evidence` | Explicit synthetic/provider-reported/unverified-response classification; never independent kernel qualification |
| `producer.fusion_version` | Optional already-observed diagnostic only when its session matches the prepared source session; otherwise `null` |
| `source.document_id`, observed session/document/cloud version/configuration, internal/display units | Whitelisted fields from the document observation used to prepare the plan; missing information remains `null` |
| `source.state_at_preparation`, `state_at_completion` | Prepared fingerprint and actual completion-response state, stored separately with their comparison |
| `request.format`, `options`, `png_dimensions` | Bound requested arguments, resolved pinned NC asset/unit settings, and documented reviewed-handler defaults |
| `completion.response_sha256`, future ID/status | Actual broker-retained successful response, bounded before hashing; the raw response is not copied into the portable projection |
| `completion.reported_output` | Whitelisted provider-reported format, hash, byte count and mesh settings; unknown values are `null` |
| `files[].validation` | Independent local parsing of the actual bytes, with explicit validator identity and limits |
| `known_losses`, `unknown_fields` | Format-specific caveats and unavailable observation categories; null members retain finer missing/not-applicable distinctions |

Provider kind identifies the transport implementation. It does not authenticate a kernel result. A native/add-in provider response is still provider-reported evidence; an arbitrary injected provider remains unverified. Synthetic fixture evidence never becomes live qualification, including when run under a real-mode profile. Build/session values in trusted qualification text, model arguments, or unsolicited response metadata cannot replace actual diagnostic observations. No approval/build/provenance fields are accepted as model-facing operation arguments.

Source configuration/version are historical observations. An asynchronous operation can finish after other document changes: the later state is recorded separately and is not substituted for the source fingerprint. These observations do not prove which intermediate geometry the provider rendered. NC post/machine/tool-library hashes and output-unit settings are bound producer inputs; they do not create an operator approval or establish that a machine executed those bytes.

## Legacy compatibility and tests

Completed version 1 receipts keep their original canonical hash shape, byte hashes, limitation text, and signature-only validation grades. Reads do not migrate them to version 2 or silently add stronger assertions. An old PNG can therefore remain valid at its historical signature-only grade without being accepted by the new PNG container validator. Attaching version 2 provenance/validation to a legacy receipt, deleting the version from a version 2 receipt, or downgrading an in-flight version 2 reservation is rejected. New production of the artifact is required for a new receipt; past evidence is preserved.

`tests/artifact-fidelity.test.mjs` uses locally generated byte fixtures and deterministic provider doubles. It covers PNG dimensions/CRC/framing/bounds, binary/ASCII STL record grammar and finite geometry, source/options/hash contradictions, exact future and diagnostic-session identity, pending quarantine, late completion-state differences, ignored unsolicited approval/build metadata, immutable receipts, and preserved legacy grades. Existing governance tests continue to cover unsafe paths, future recovery, package completion, trusted-profile checks, and replay prevention. These tests exercise the broker and parser contracts without Fusion and do not qualify geometric, visual, or manufacturing correctness.
