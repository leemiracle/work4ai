# NVIDIA Icons

Official NVIDIA GUI icon packages for web and React applications: raw SVG
assets, and React components that render via a lightweight sprite-injection
runtime. All icon path data ships in the package and is bundled at install
time; there is no CDN or web-font dependency at runtime. See
[Rendering model](#rendering-model) below for how the React components work
and their SSR caveat.

## Overview

This repository publishes four npm packages under the `@nvidia` scope:

| Package | Description |
|---|---|
| [`@nvidia/gui-icons`](./packages/gui-icons) | Raw SVG assets + TypeScript constants (748 icons, `line` and `fill` variants) |
| [`@nvidia/react-gui-icons`](./packages/react-gui-icons) | React icon components for GUI Icons (sprite-based rendering) |
| [`@nvidia/micro-gui-icons`](./packages/micro-gui-icons) | Raw SVG assets + TypeScript constants for Micro GUI Icons (24 utility icons) |
| [`@nvidia/react-micro-gui-icons`](./packages/react-micro-gui-icons) | React icon components for Micro GUI Icons (sprite-based rendering) |

## Documentation

This README and the per-package READMEs linked above are the complete
documentation today. A browsable icon gallery and searchable docs site is
planned, but is **not yet available**. Until it ships, the authoritative list
of every icon name is the `IconNames` constant exported from
`@nvidia/gui-icons` and `@nvidia/micro-gui-icons`. To browse by keyword, use
`IconTagMap` from either package; to browse by category, use `IconCategoryMap`
from `@nvidia/gui-icons` (the Micro set ships no categories, see
[Finding an icon](#finding-an-icon)).

## Getting started

```sh
# Raw SVG assets + TypeScript constants
npm install @nvidia/gui-icons

# React icon components
npm install @nvidia/react-gui-icons
```

```tsx
import { NvidiaGuiIcon } from "@nvidia/react-gui-icons";

<NvidiaGuiIcon iconName="gpu" />;
```

## Requirements

- **Node.js:** 22 or newer (`engines.node` is `>=22`).
- **React** (React packages only): `^17.0.0 || ^18.0.0 || ^19.0.0` as a peer
  dependency. The base `@nvidia/gui-icons` / `@nvidia/micro-gui-icons` packages
  have no runtime dependencies.

## Usage

### React: generic component

```tsx
import { NvidiaGuiIcon } from "@nvidia/react-gui-icons";

// line variant (default)
<NvidiaGuiIcon iconName="gpu" />

// fill variant, custom size
<NvidiaGuiIcon iconName="gpu" variant="fill" size="24px" />
```

### React: tree-shakable named imports

```tsx
// barrel import (tree-shakable by bundlers with sideEffects: false support)
import { Gpu, Add, Close } from "@nvidia/react-gui-icons/icons";

// per-icon subpath import (explicit tree-shaking boundary)
import { Gpu } from "@nvidia/react-gui-icons/icons/Gpu";

<Gpu variant="line" size="1em" />
```

These packages do **not** use `external-svg-loader`, CDN-hosted SVG files, or
web fonts. All path data is bundled at install time; see
[Rendering model](#rendering-model) for how it reaches the DOM.

### Finding an icon

There is no hosted icon browser yet, so the icon set is searchable
programmatically instead. Every name, category and keyword ships with the
package as plain data, and all of it is typed.

```ts
import {
  IconNames,        // all 748 names
  IconTagMap,       // name -> search keywords
  IconCategoryMap,  // category -> names
  getIconCategory,  // name -> category
  isIconName,       // runtime type guard
} from "@nvidia/gui-icons";

// Search by name or keyword
const matches = IconNames.filter(
  (name) => name.includes("gpu") || IconTagMap[name]?.includes("gpu"),
);
// -> ["gpu", "gpu-card", "gpu-card-multi", "gpu-card-off", "gpu-off", "gpu-sync"]

getIconCategory("gpu");             // -> "hardware"
IconCategoryMap.hardware.length;    // -> 118
isIconName("not-an-icon");          // -> false
```

`IconCategories` lists the 14 categories and `IconTags` the full keyword
vocabulary. Both are exported as `const` arrays with matching `IconCategory`
and `IconTag` types, so an editor will autocomplete them and a typo is a
compile error rather than a blank icon.

`@nvidia/micro-gui-icons` exports the same name and keyword API: `IconNames`,
`isIconName`, `IconTags`, `IconTagMap`, and the `IconName` / `IconTag` types.
It ships **no categories**. At 24 icons the set is small enough to read in one
go, so `IconCategories`, `IconCategoryMap` and `getIconCategory` exist only on
`@nvidia/gui-icons`.

The React packages re-export the `IconName` and `Variant` types for their own
icon set. They do not re-export the name, tag or category *values*; import
those from the matching base package.

### Raw SVG assets

```ts
import { IconNames, isIconName } from "@nvidia/gui-icons";

// Resolve an SVG file's URL through the package's ./assets/* subpath export
const svgUrl = import.meta.resolve("@nvidia/gui-icons/assets/line/gpu.svg");
```

`import.meta.resolve` requires Node.js or a bundler that supports it (Vite,
webpack 5+, esbuild). If your bundler doesn't, resolve the package's install
path yourself (e.g. via `require.resolve` or your bundler's asset-URL syntax)
and join it with `assets/<variant>/<name>.svg`.

SVG files are available at `assets/fill/<name>.svg` and `assets/line/<name>.svg`
within each installed package.

### Rendering model

The React components do not inline `<path>` markup directly. Each renders
`<svg><use href="#<symbolId>" /></svg>` against a `<symbol>` definition that's
injected into `document.body` the first time that icon mounts (see
`runtime/sprite.tsx` in each React package). This keeps rendered markup small
and de-duplicates repeated icons, at the cost of one extra step between mount
and paint.

**SSR / no-JS caveat:** the injection runs in `useLayoutEffect` (falling back
to `useEffect` when `document` is undefined), so server-rendered HTML and any
render that never executes React effects (static export previews, `noscript`
fallbacks) will show an empty `<svg>` with no visible icon until hydration.

If you need icons to render in the initial HTML (SSR, static generation, or
snapshot testing), render `<NvidiaGuiIconSprite />` (or
`<NvidiaMicroGuiIconSprite />`) once, high in your tree. It renders each
`<symbol>` declaratively as part of the React tree instead of via an effect,
so the symbols are present in the markup on first paint and every `<Icon />`
that references them resolves immediately.

**Pass the icons you actually use.** `getNvidiaGuiIconSpriteSymbols` accepts
icon names, or `{ iconName, variant }` objects when you need a variant other
than `line`, and returns the symbol payloads with duplicates removed:

```tsx
import {
  NvidiaGuiIcon,
  NvidiaGuiIconSprite,
  getNvidiaGuiIconSpriteSymbols,
} from "@nvidia/react-gui-icons";

// Built once at module scope: the set is static, and hoisting keeps the prop
// identity stable across renders.
const SPRITE_SYMBOLS = getNvidiaGuiIconSpriteSymbols([
  "gpu",
  "trash",
  { iconName: "gpu", variant: "fill" },
]);

function App() {
  return (
    <>
      <NvidiaGuiIconSprite symbols={SPRITE_SYMBOLS} />
      <NvidiaGuiIcon iconName="gpu" />
      <NvidiaGuiIcon iconName="gpu" variant="fill" />
    </>
  );
}
```

Omitting `symbols` renders **every** symbol the package ships: that is 748
icons × 2 variants for `@nvidia/react-gui-icons`, and 24 × 2 for
`@nvidia/react-micro-gui-icons`. Every one of them lands in the markup of
every server-rendered response, so treat the bare `<NvidiaGuiIconSprite />`
as a quick way to check the wiring rather than the form to ship.

An icon whose symbol is missing from the sprite is not an error: it renders an
empty `<svg>` in the initial HTML and fills in once its own mount-time
injection runs on the client. So a name you forget to list degrades back to
the default rendering model rather than breaking, which also means a missing
entry will not show up in a client-side test. Check the server-rendered
output, not the hydrated DOM.

`getNvidiaMicroGuiIconSpriteSymbols` and `<NvidiaMicroGuiIconSprite />` are
the same API for the Micro GUI Icons package.

**Shadow DOM caveat:** the sprite is injected into `document.body`, and an SVG
`<use href="#id">` cannot resolve a `<symbol>` across a shadow boundary. Icons
rendered inside a shadow root (a web component, or a micro-frontend that
mounts into one) therefore render as an empty `<svg>` with no error. Render
`<NvidiaGuiIconSprite />` inside the same shadow root to give those icons a
`<symbol>` they can reach.

### Line and fill variants

Every icon ships in both `line` and `fill`. For glyphs that are pure strokes
with nothing to fill (arrows, chevrons, `add`, `check`, `close`), the two
variants are deliberately identical, so `variant="fill"` renders the same
artwork as `variant="line"`. That affects 98 of the 748 GUI Icons and 19 of
the 24 Micro GUI Icons.

Both variants exist for every icon regardless, so switching a whole icon set
between them never leaves a gap, and no call site needs to special-case which
glyphs have a distinct fill.

### Micro GUI Icons

The `@nvidia/micro-gui-icons` and `@nvidia/react-micro-gui-icons` packages
follow the same API shape for the 24-icon utility set.

### Bundle size guidance

| Import style | Bundle includes | Approx. cost |
|---|---|---|
| `import { NvidiaGuiIcon }` | Full inline map, all 748 icons | 490 KB (150 KB gzipped) |
| `import { Gpu } from ".../icons"` | Only `Gpu` path data (tree-shaken by bundler) | ~1 KB |
| `import { Gpu } from ".../icons/Gpu"` | Only `Gpu` path data (explicit subpath) | ~1 KB |

Figures are for `@nvidia/react-gui-icons` at 1.0.0, measured on the built
output. The Micro GUI Icons equivalent is 8.6 KB (1.5 KB gzipped) for its full
map.

The generic `NvidiaGuiIcon` component resolves icon names at runtime, so a
bundler cannot know which icons you use and has to include all of them. Reach
for it only when icon names genuinely are dynamic. For a fixed set of icons,
which is the common case, use the named subpath imports and pay for what you
render.

## Accessibility

Every generated icon component defaults to `aria-hidden="true"` and
`focusable="false"`. Icons are treated as decorative by default, invisible to
screen readers, and excluded from the tab order.

That default is deliberate. The same icon is decorative beside a visible label
and meaningful in an icon-only button, and only the call site knows which. An
icon announced next to the label it duplicates is noise.

If an icon carries meaning on its own, give it a name with `title`:

```tsx
<NvidiaGuiIcon iconName="trash" title="Delete item" />
```

That renders a `<title>`, sets `role="img"` and drops `aria-hidden` together,
so there is no half-configured state to land in.

**Name the action, not the glyph.** Write `title="Delete item"`, not
`title="trash"`. The library knows the shape it draws; only you know what it
does here. A wrong name is worse than none: every automated audit reports it
as passing.

An empty `title=""` is treated as decorative, so a name computed at runtime can
fall back to no name rather than an empty one.

The lower-level escape hatch still works, and `aria-label` takes precedence
over `title` if you set both:

```tsx
<NvidiaGuiIcon iconName="gpu" role="img" aria-label="GPU" aria-hidden={undefined} />
```

Note that `aria-hidden` removes the whole subtree from the accessibility tree,
so setting `aria-label` while leaving `aria-hidden` in place changes nothing a
user perceives. Prefer a visible text label next to the icon over an icon-only
control where practical.

## Releases and roadmap

Each package versions independently, starting at `1.0.0`: icon name removals
and renamed exports are breaking changes (semver MAJOR); new icons are minor
releases. See [CHANGELOG.md](./CHANGELOG.md) for release history.

The current support level is **Supported**. See [SUPPORT.md](./SUPPORT.md).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Icon design changes are not accepted as
direct contributions; open an issue to request icons; NVIDIA design/brand
owners review all requests internally.

## Governance

Project decision-making, maintainer responsibilities, and release authority are
described in [GOVERNANCE.md](./GOVERNANCE.md). Current maintainers are listed in
[MAINTAINERS.md](./MAINTAINERS.md).

## Security

See [SECURITY.md](./SECURITY.md) for the vulnerability reporting policy. Please
do not report security issues through public GitHub issues.

## Support

This project is **Supported**. For how to get help and what to expect, see
[SUPPORT.md](./SUPPORT.md).

## Community

Participation is governed by our [Code of Conduct](./CODE_OF_CONDUCT.md). Use
GitHub Issues for bug reports and icon requests, and GitHub Pull Requests for
code and documentation contributions.

## License

This project is licensed under Apache-2.0 for code and CC-BY-4.0 for
documentation, assets, and icons; see the [LICENSE](./LICENSE) file for details.

### Attribution

CC-BY-4.0 requires attribution when the icon assets are redistributed. When
you do, credit:

> "NVIDIA Icons" (<https://github.com/NVIDIA/icons>)

See [NOTICE](./NOTICE) for the full copyright and license notice, and each
package's `THIRD_PARTY_NOTICES` file for build-time dependency attributions
(none are bundled or distributed in the published tarballs).

### Trademarks

CC-BY-4.0 and Apache-2.0 cover the copyrighted content in this project; they
do **not** license NVIDIA's trademarks. "NVIDIA" and the NVIDIA logo remain
NVIDIA trademarks; see [NOTICE](./NOTICE) for the full trademark notice.

### Sub-package licensing

Each published package embeds its own copy of the root license file, as npm
requires a license file inside every tarball. Each package also ships its own
`NOTICE`, so attribution and trademark terms are present in the package
tarball itself.

The package `LICENSE` files are byte-identical to the root [LICENSE](./LICENSE)
and carry the same `CC-BY-4.0 AND Apache-2.0` terms:

- [`packages/gui-icons/LICENSE`](./packages/gui-icons/LICENSE)
- [`packages/micro-gui-icons/LICENSE`](./packages/micro-gui-icons/LICENSE)
- [`packages/react-gui-icons/LICENSE`](./packages/react-gui-icons/LICENSE)
- [`packages/react-micro-gui-icons/LICENSE`](./packages/react-micro-gui-icons/LICENSE)

The package `NOTICE` files are **not** byte-identical to the root
[NOTICE](./NOTICE): the CC-BY-4.0 "Credit as" line and the attribution
paragraph are narrowed to name the specific package and the icon family it
ships (`NVIDIA GUI Icons` or `NVIDIA Micro GUI Icons`), rather than the
umbrella project name, so a redistributor credits the product they actually
got assets from:

- [`packages/gui-icons/NOTICE`](./packages/gui-icons/NOTICE): "NVIDIA GUI Icons"
- [`packages/micro-gui-icons/NOTICE`](./packages/micro-gui-icons/NOTICE): "NVIDIA Micro GUI Icons"
- [`packages/react-gui-icons/NOTICE`](./packages/react-gui-icons/NOTICE): "NVIDIA GUI Icons"
- [`packages/react-micro-gui-icons/NOTICE`](./packages/react-micro-gui-icons/NOTICE): "NVIDIA Micro GUI Icons"
