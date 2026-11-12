# @nvidia/micro-gui-icons

Raw SVG assets and TypeScript constants for **NVIDIA Micro GUI Icons**: a
24-icon utility set, `line` and `fill` variants.

## Install

```sh
npm install @nvidia/micro-gui-icons
```

## Usage

```ts
import { IconNames, isIconName } from "@nvidia/micro-gui-icons";

// SVG files ship at assets/line/<name>.svg and assets/fill/<name>.svg
```

For React components, see
[`@nvidia/react-micro-gui-icons`](https://github.com/NVIDIA/icons/tree/main/packages/react-micro-gui-icons).

## Line and fill variants

Every icon ships in both `line` and `fill`. For glyphs that are pure strokes
with nothing to fill (arrows, chevrons, `add`, `check`, `close`), the two
variants are deliberately identical, so selecting `fill` renders the same
artwork as `line`. That affects 19 of the 24 icons in this set.

Both variants exist for every icon regardless, so switching a set between them
never leaves a gap, and no call site needs to special-case which glyphs have a
distinct fill.

## License

Dual-licensed: **Apache-2.0** for code and **CC-BY-4.0** for the icon assets;
see [LICENSE](./LICENSE). When redistributing the icons, attribute
"NVIDIA Micro GUI Icons" with a link to <https://github.com/NVIDIA/icons>.

Part of the [NVIDIA Icons](https://github.com/NVIDIA/icons) project.
