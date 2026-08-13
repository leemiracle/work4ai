import {
  __name,
  executeTidyTreeLayout,
  render,
  validateLayoutData
} from "./chunks/mermaid-layout-tidy-tree.core/chunk-Z6Y5CIZP.mjs";

// src/layouts.ts
var loader = /* @__PURE__ */ __name(async () => await import("./chunks/mermaid-layout-tidy-tree.core/render-DLZURBVE.mjs"), "loader");
var tidyTreeLayout = [
  {
    name: "tidy-tree",
    loader,
    algorithm: "tidy-tree"
  }
];
var layouts_default = tidyTreeLayout;
export {
  layouts_default as default,
  executeTidyTreeLayout,
  render,
  validateLayoutData
};
