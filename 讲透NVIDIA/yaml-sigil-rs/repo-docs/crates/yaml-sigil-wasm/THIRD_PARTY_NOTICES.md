# Third-Party Notices

NVIDIA-authored `yaml-sigil-wasm` material is licensed under the Apache
License 2.0. The following notices apply only to the identified standards-
derived validation and encoding rules packaged by this crate. That material
remains subject to its source terms and is not relicensed under Apache-2.0.

Identification of a source does not imply affiliation with or endorsement by
its authors, publishers, standards organizations, or copyright holders.
`yaml-sigil-wasm` is not an IETF RFC, an IRTF publication, or a Standards
for Efficient Cryptography Group (SECG) publication.

The packaged `tests/wasm.rs`, `tests/generated_api.cjs`, and
`tests/byte_inputs.cjs` construct P-256 public-key encodings through dependencies.
The README describes the same encoding boundary. This crate does not package
RFC 8032 reference vectors or reimplement dependency cryptographic algorithms.

## Standards for Efficient Cryptography material

The P-256 public-key boundary requires the uncompressed point encoding from
*Standards for Efficient Cryptography 1 (SEC 1): Elliptic Curve Cryptography*,
version 2.0, section 2.3.3.

The front page of *Standards for Efficient Cryptography 1 (SEC 1)* carries
this notice:

> Copyright © 2009 Certicom Corp.
>
> License to copy this document is granted provided it is identified as
> "Standards for Efficient Cryptography 1 (SEC 1)", in all material mentioning
> or referencing it.

Source: Standards for Efficient Cryptography Group,
*Standards for Efficient Cryptography 1 (SEC 1): Elliptic Curve Cryptography*,
version 2.0, May 21, 2009, <https://www.secg.org/sec1-v2.pdf>.

Section 1.5, "Intellectual Property," of
*Standards for Efficient Cryptography 1 (SEC 1)* states:

> The reader's attention is called to the possibility that compliance with
> this document may require use of an invention covered by patent rights. By
> publication of this document, no position is taken with respect to the
> validity of this claim or of any patent rights in connection therewith. The
> patent holder(s) may have filed with the SECG a statement of willingness to
> grant a license under these rights on reasonable and nondiscriminatory terms
> and conditions to applicants desiring to obtain such a license. Additional
> details may be obtained from the patent holder and from the SECG website,
> <http://www.secg.org>.

The SEC 1 material is not relicensed under Apache-2.0.

The names of Certicom Corp. and the Standards for Efficient Cryptography Group
are not used to endorse or promote `yaml-sigil-wasm`. No affiliation,
sponsorship, or endorsement is claimed or implied.
