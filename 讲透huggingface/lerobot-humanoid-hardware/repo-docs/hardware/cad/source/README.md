# CAD Source

Canonical CAD is maintained in Onshape:
- https://cad.onshape.com/documents/fb645318a27646d1d8840be6/w/d1cae8805fb652b4d1614997/e/804a1da43f242001a05129b4

Reference IDs:
- document: `fb645318a27646d1d8840be6`
- workspace: `d1cae8805fb652b4d1614997`
- default element: `804a1da43f242001a05129b4`

Current repo scope:
- biped platform only

CAD organization for this repo:
- `biped_platform/left_leg/`
- `biped_platform/right_leg/`
- `biped_platform/torso/`

Export policy:
1. Keep Onshape as source of truth.
2. Export `STL` for manufacturing where needed.
3. Include date/revision in exported filenames.
4. Update BOM and docs in the same commit.
