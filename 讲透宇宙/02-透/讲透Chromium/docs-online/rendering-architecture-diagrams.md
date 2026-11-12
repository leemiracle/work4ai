---
title: "渲染架构图"
slug: rendering-architecture-diagrams
source: https://www.chromium.org/developers/design-documents/rendering-architecture-diagrams
fetched: 2026-10-09
---

# 渲染架构图（rendering-architecture-diagrams）

[For Developers](/developers) > [Design Documents](/developers/design-documents) >  
# Rendering Architecture Diagrams

 The following sequence diagrams illustrate various aspects of Chromium's rendering architecture. The first picture below shows how Javascript and CSS animations are scheduled using the requestAnimationFrame callback mechanism.

 [![image](/developers/design-documents/rendering-architecture-diagrams/chromium-request-anim-frame.png)](/developers/design-documents/rendering-architecture-diagrams/chromium-request-anim-frame.png)

 After the Javascript callback is executed or the CSS animations have been updated, the web contents view generally needs to be redrawn. The following (simplified) diagrams show the code execution flow during a repaint in the non-composited software rendering, composited software rendering and (threaded) composited GPU rendering modes. Note that the newer [multithreaded ("impl-side") rasterization mode](/developers/design-documents/impl-side-painting) is not shown below.

 
Non-composited SW rendering | Composited SW rendering | Composited GPU rendering
