# @nvidia/gui-icons

Raw SVG assets and TypeScript constants for **NVIDIA GUI Icons** (748 icons,
`line` and `fill` variants).

## Install

```sh
npm install @nvidia/gui-icons
```

## Usage

```ts
import { IconNames, isIconName } from "@nvidia/gui-icons";

// SVG files ship at assets/line/<name>.svg and assets/fill/<name>.svg
```

For React components, see
[`@nvidia/react-gui-icons`](https://github.com/NVIDIA/icons/tree/main/packages/react-gui-icons).

## Line and fill variants

Every icon ships in both `line` and `fill`. For glyphs that are pure strokes
with nothing to fill (arrows, chevrons, `add`, `check`, `close`), the two
variants are deliberately identical, so selecting `fill` renders the same
artwork as `line`. That affects 98 of the 748 icons in this set.

Both variants exist for every icon regardless, so switching a set between them
never leaves a gap, and no call site needs to special-case which glyphs have a
distinct fill.

## License

Dual-licensed: **Apache-2.0** for code and **CC-BY-4.0** for the icon assets;
see [LICENSE](./LICENSE). When redistributing the icons, attribute
"NVIDIA GUI Icons" with a link to <https://github.com/NVIDIA/icons>.

CC-BY-4.0 does not license NVIDIA's trademarks; see
[NOTICE](https://github.com/NVIDIA/icons/blob/main/NOTICE).

Part of the [NVIDIA Icons](https://github.com/NVIDIA/icons) project.
