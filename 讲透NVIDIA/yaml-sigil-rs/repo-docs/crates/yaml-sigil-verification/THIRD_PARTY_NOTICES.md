# Third-Party Notices

NVIDIA-authored `yaml-sigil-verification` material is licensed under the
Apache License 2.0. The following notices apply only to the identified
third-party material. That material remains subject to its source terms and is
not relicensed under Apache-2.0.

Identification of a source does not imply affiliation with or endorsement by
its authors, publishers, standards organizations, or copyright holders.
`yaml-sigil-verification` is not an IETF RFC, an IRTF publication, or a
Standards for Efficient Cryptography Group (SECG) publication.

## RFC 8032 material

RFC 8032 is an IRTF Stream RFC. Section 8(g) of the IETF Trust Legal
Provisions in effect when RFC 8032 was published states that the provisions
for IETF Code Components do not apply to documents in the IRTF Document
Stream. This crate does not characterize the RFC-derived values as IETF Code
Components or apply the Revised BSD License to them. They are third-party RFC
material used with attribution under the applicable BCP 78 and IETF Trust
framework.

Copyright (c) 2017 IETF Trust and the persons identified as the document
authors. All rights reserved.

RFC 8032 states that the document is subject to BCP 78 and the IETF Trust's
Legal Provisions Relating to IETF Documents in effect on its publication
date. Section 7(a) of those provisions supplies this warranty disclaimer:

> ALL DOCUMENTS AND THE INFORMATION CONTAINED THEREIN ARE PROVIDED ON AN
> "AS IS" BASIS AND THE CONTRIBUTOR, THE ORGANIZATION HE/SHE REPRESENTS OR
> IS SPONSORED BY (IF ANY), THE INTERNET SOCIETY, THE IETF TRUST, THE
> INTERNET ENGINEERING TASK FORCE AND ANY APPLICABLE MANAGERS OF ALTERNATE
> STREAM DOCUMENTS, AS DEFINED IN SECTION 8 BELOW, DISCLAIM ALL WARRANTIES,
> EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTY THAT THE USE
> OF THE INFORMATION THEREIN WILL NOT INFRINGE ANY RIGHTS OR ANY IMPLIED
> WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.

Source: Simon Josefsson and Ilari Liusvaara, RFC 8032, *Edwards-Curve Digital
Signature Algorithm (EdDSA)*, January 2017:

- RFC information and copyright notice:
  <https://www.rfc-editor.org/info/rfc8032/>.
- Sections 5.1, 5.1.7, and 7.1:
  <https://www.rfc-editor.org/rfc/rfc8032#section-5.1>,
  <https://www.rfc-editor.org/rfc/rfc8032#section-5.1.7>, and
  <https://www.rfc-editor.org/rfc/rfc8032#section-7.1>.
- BCP 78: <https://www.rfc-editor.org/info/bcp78>.
- IETF Trust Legal Provisions, version 5.0:
  <https://trustee.ietf.org/documents/trust-legal-provisions/tlp-5/>.

The names of the document authors, the Crypto Forum Research Group, the IRTF,
the IETF, the IETF Trust, and the RFC Editor are not used to endorse or promote
`yaml-sigil-verification`. No affiliation, sponsorship, or endorsement is
claimed or implied.

This crate adapts RFC 8032 sections 5.1, 5.1.2, and 5.1.7 into Rust constants,
point decoding, canonical-encoding checks, challenge computation, cofactored
verification, and fixed provider-qualification vectors. It reproduces one
section 7.1 test-vector public key and signature. Section 3(c) of the IETF
Trust Legal Provisions, version 5.0, addresses reproduction outside the IETF
Standards Process. Section 5(a) states that no patent license is granted, and
sections 7(b) through 7(d) provide the intellectual-property-rights caveat.
The Rust representations and verifier-state mappings are identified
`yaml-sigil-verification` adaptations.

## Standards for Efficient Cryptography

The crate's P-256 public-key resolver and fixed provider-qualification public
key follow point-encoding behavior from
*Standards for Efficient Cryptography 1 (SEC 1)*, Version 2.0.

The front page of *Standards for Efficient Cryptography 1 (SEC 1)* carries
this notice:

> Copyright © 2009 Certicom Corp.
>
> License to copy this document is granted provided it is identified as
> "Standards for Efficient Cryptography 1 (SEC 1)", in all material mentioning
> or referencing it.

Section 1.5, "Intellectual Property," of *Standards for Efficient Cryptography
1 (SEC 1)* states:

> The reader's attention is called to the possibility that compliance with
> this document may require use of an invention covered by patent rights. By
> publication of this document, no position is taken with respect to the
> validity of this claim or of any patent rights in connection therewith. The
> patent holder(s) may have filed with the SECG a statement of willingness to
> grant a license under these rights on reasonable and nondiscriminatory terms
> and conditions to applicants desiring to obtain such a license. Additional
> details may be obtained from the patent holder and from the SECG website,
> <http://www.secg.org>.

Source:

- *Standards for Efficient Cryptography 1 (SEC 1): Elliptic Curve
  Cryptography*, Version 2.0, May 21, 2009,
  <https://www.secg.org/sec1-v2.pdf>.

The SEC 1 material is not relicensed under Apache-2.0.
`yaml-sigil-verification` is not affiliated with, sponsored by, or endorsed by
SECG or Certicom Corp.
