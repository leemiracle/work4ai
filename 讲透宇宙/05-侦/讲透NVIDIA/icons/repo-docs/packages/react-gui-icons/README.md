# @nvidia/react-gui-icons

React icon components for **NVIDIA GUI Icons**. Icons render via a
sprite-injection runtime (`<use href="#id">`), not inline `<path>` markup;
see [Rendering model](https://github.com/NVIDIA/icons#rendering-model) in the
project README for how that works and its SSR caveat.

## Install

```sh
npm install @nvidia/react-gui-icons
```

`react` and `react-dom` are peer dependencies
(`^17.0.0 || ^18.0.0 || ^19.0.0`).

## Usage

```tsx
// Generic component (resolves any icon by name)
import { NvidiaGuiIcon } from "@nvidia/react-gui-icons";
<NvidiaGuiIcon iconName="gpu" variant="line" size="1em" />;

// Tree-shakable per-icon imports
import { Gpu } from "@nvidia/react-gui-icons/icons/Gpu";
<Gpu variant="fill" />;
```

Icons default to `aria-hidden="true"` and `focusable="false"` (decorative),
because only the call site knows whether an icon repeats a nearby label or
carries the meaning itself. For a meaningful icon, pass `title`: it renders a
`<title>`, sets `role="img"` and drops `aria-hidden` in one step:

```tsx
<NvidiaGuiIcon iconName="trash" title="Delete item" />
```

Name the action, not the glyph: `title="Delete item"`, not `title="trash"`. See
the [project README](https://github.com/NVIDIA/icons) for rendering notes and
full usage.

## RTL / directional icons

Directional icons (`arrow-*`, `chevron-*`, and similar) render with a fixed
orientation: there is no built-in RTL/logical-direction handling, and most
icons (shapes, objects, status glyphs) should **not** be mirrored.

**Prefer choosing the mirrored icon over mirroring with CSS.** Every direction
is a named icon, so the set already contains the counterpart you need:
`arrow-right` is artwork drawn and hinted for the 16px grid, whereas
`transform: scaleX(-1)` on `arrow-left` is a flipped copy of a different glyph.
Picking the name also keeps the transform out of your stacking contexts and
animations.

```tsx
const back = dir === "rtl" ? "arrow-right" : "arrow-left";

<NvidiaGuiIcon iconName={back} title="Back" />;
```

If the name cannot be chosen at render time, fall back to CSS scoped to
`[dir="rtl"]`:

```css
[dir="rtl"] .icon-directional {
  transform: scaleX(-1);
}
```

Apply that class to the specific directional icons your UI uses. Which icons
should mirror is a decision only your application can make: alignment icons,
for example, mirror only if your alignment is logical (`start`/`end`) rather
than physical (`left`/`right`).

## Line and fill variants

Every icon ships in both `line` and `fill`. For glyphs that are pure strokes
with nothing to fill (arrows, chevrons, `add`, `check`, `close`), the two
variants are deliberately identical, so selecting `fill` renders the same
artwork as `line`. That affects 98 of the 748 icons in this set.

Both variants exist for every icon regardless, so switching a set between them
never leaves a gap, and no call site needs to special-case which glyphs have a
distinct fill.

## License

Dual-licensed: **Apache-2.0** for code and **CC-BY-4.0** for the bundled icon
path data; see [LICENSE](./LICENSE). When redistributing the icons, attribute
"NVIDIA GUI Icons" with a link to <https://github.com/NVIDIA/icons>.

CC-BY-4.0 does not license NVIDIA's trademarks; see
[NOTICE](https://github.com/NVIDIA/icons/blob/main/NOTICE).

Part of the [NVIDIA Icons](https://github.com/NVIDIA/icons) project.
