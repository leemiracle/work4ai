# Third-Party Notices

NVIDIA-authored `yaml-sigil-core` material is licensed under the Apache
License 2.0. The following notice applies only to the RFC 4648-derived
base64url canonical-encoding rules copied into the packaged signature-document
JSON Schema and related schema-conformance tests. That material remains subject
to its source terms and is not relicensed under Apache-2.0.

Identification of a source does not imply affiliation with or endorsement by
its authors, publishers, standards organizations, or copyright holders.
`yaml-sigil-core` is not an IETF RFC.

## RFC 4648 material

The specification and conformance generator use the canonical-encoding rules,
base64url alphabet, and test values from RFC 4648 sections 3, 5, and 10.
RFC 4648 section 15 provides these copying conditions for the abstract and
sections 1, 3, 8, 10, 12, 13, and 14:

> Copyright (c) 2000-2006 Simon Josefsson
>
> Regarding the abstract and sections 1, 3, 8, 10, 12, 13, and 14 of this
> document, that were written by Simon Josefsson ("the author", for the
> remainder of this section), the author makes no guarantees and is not
> responsible for any damage resulting from its use. The author grants
> irrevocable permission to anyone to use, modify, and distribute it in any
> way that does not diminish the rights of anyone else to use, modify, and
> distribute it, provided that redistributed derivative works do not contain
> misleading author or version information and do not falsely purport to be
> IETF RFC documents. Derivative works need not be licensed under similar
> terms.

RFC 4648 also includes this full copyright and warranty statement:

> Copyright (C) The Internet Society (2006).
>
> This document is subject to the rights, licenses and restrictions contained
> in BCP 78, and except as set forth therein, the authors retain all their
> rights.
>
> This document and the information contained herein are provided on an
> "AS IS" basis and THE CONTRIBUTOR, THE ORGANIZATION HE/SHE REPRESENTS OR
> IS SPONSORED BY (IF ANY), THE INTERNET SOCIETY AND THE INTERNET ENGINEERING
> TASK FORCE DISCLAIM ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT
> LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT
> INFRINGE ANY RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS
> FOR A PARTICULAR PURPOSE.

This project identifies its derived specification, implementation, and tests
as YamlSigil material and does not represent them as an IETF RFC. It reproduces
only the RFC material needed to explain and test conformance.

Source: Simon Josefsson, RFC 4648, *The Base16, Base32, and Base64 Data
Encodings*, October 2006, <https://www.rfc-editor.org/rfc/rfc4648>.

The RFC's intellectual-property notice states that the IETF takes no position
on the validity or scope of asserted rights or their availability for license,
has made no independent effort to identify such rights, and invites rights
holders to disclose them through the IETF process.

The schema and related tests identified above are `yaml-sigil-core`
adaptations.

## Standards for Efficient Cryptography material

In addition to the RFC 4648 material identified above, the compressed and
uncompressed public-key selection in `src/p256_encoding.rs` follows
*Standards for Efficient Cryptography 1 (SEC 1): Elliptic Curve Cryptography*,
version 2.0, section 2.3.3. Parsing and point validation use the RustCrypto
dependency. The helper selects the encodings accepted before the algorithm
boundary and emits the existing uncompressed public-key representation.

The front page of *Standards for Efficient Cryptography 1 (SEC 1)* carries
this notice:

> Copyright © 2009 Certicom Corp.
>
> License to copy this document is granted provided it is identified as
> "Standards for Efficient Cryptography 1 (SEC 1)", in all material mentioning
> or referencing it.

Source:

- *Standards for Efficient Cryptography 1 (SEC 1): Elliptic Curve Cryptography*,
  Version 2.0, May 21, 2009, <https://www.secg.org/sec1-v2.pdf>.

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
`yaml-sigil-core` is not affiliated with, sponsored by, or endorsed by
SECG or Certicom Corp.
