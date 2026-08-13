import {
  __name
} from "./chunk-CJCKSLXZ.mjs";

// src/mermaidUtils.ts
var warning = /* @__PURE__ */ __name((s) => {
  console.error("Log function was called before initialization", s);
}, "warning");
var log = {
  trace: warning,
  debug: warning,
  info: warning,
  warn: warning,
  error: warning,
  fatal: warning
};
var setLogLevel;
var getConfig;
var sanitizeText;
var setupGraphViewbox;
var injectUtils = /* @__PURE__ */ __name((_log, _setLogLevel, _getConfig, _sanitizeText, _setupGraphViewbox) => {
  _log.info("Mermaid utils injected");
  log.trace = _log.trace;
  log.debug = _log.debug;
  log.info = _log.info;
  log.warn = _log.warn;
  log.error = _log.error;
  log.fatal = _log.fatal;
  setLogLevel = _setLogLevel;
  getConfig = _getConfig;
  sanitizeText = _sanitizeText;
  setupGraphViewbox = _setupGraphViewbox;
}, "injectUtils");

// src/parser.ts
var parser_default = {
  parse: /* @__PURE__ */ __name(() => {
  }, "parse")
};

// src/zenumlRenderer.ts
import { renderToSvg } from "@zenuml/core";
var regexp = /^\s*zenuml/;
var calculateSvgSizeAttrs = /* @__PURE__ */ __name((width, height, useMaxWidth) => {
  const attrs = /* @__PURE__ */ new Map();
  if (useMaxWidth) {
    attrs.set("width", "100%");
    attrs.set("style", `max-width: ${width}px;`);
  } else {
    attrs.set("width", String(width));
    attrs.set("height", String(height));
  }
  return attrs;
}, "calculateSvgSizeAttrs");
var selectSvgElement = /* @__PURE__ */ __name((id) => {
  const { securityLevel } = getConfig();
  let root = document;
  if (securityLevel === "sandbox") {
    const sandboxElement = document.querySelector(`#i${id}`);
    root = sandboxElement?.contentDocument ?? document;
  }
  return root.querySelector(`#${id}`);
}, "selectSvgElement");
var configureSvgSize = /* @__PURE__ */ __name((svgEl, width, height, useMaxWidth) => {
  const attrs = calculateSvgSizeAttrs(width, height, useMaxWidth);
  svgEl.removeAttribute("height");
  svgEl.style.removeProperty("max-width");
  for (const [attr, value] of attrs) {
    svgEl.setAttribute(attr, value);
  }
}, "configureSvgSize");
var draw = /* @__PURE__ */ __name(function(text, id) {
  log.info("draw with ZenUML native SVG renderer");
  const code = text.replace(regexp, "");
  const config = getConfig();
  const useMaxWidth = config.sequence?.useMaxWidth ?? true;
  const svgEl = selectSvgElement(id);
  if (!svgEl) {
    log.error("Cannot find svg element");
    return Promise.resolve();
  }
  const result = renderToSvg(code);
  configureSvgSize(svgEl, result.width, result.height, useMaxWidth);
  svgEl.setAttribute("viewBox", result.viewBox);
  svgEl.innerHTML = result.innerSvg;
  return Promise.resolve();
}, "draw");
var zenumlRenderer_default = {
  draw
};

// src/zenuml-definition.ts
var diagram = {
  db: {
    clear: /* @__PURE__ */ __name(() => {
    }, "clear")
  },
  renderer: zenumlRenderer_default,
  parser: parser_default,
  styles: /* @__PURE__ */ __name(() => {
  }, "styles"),
  injectUtils
};
export {
  diagram
};
