import {
  __name
} from "./chunk-ZW26E7AF.mjs";

// src/render.ts
import { curveLinear } from "d3";
import ELK from "elkjs/lib/elk.bundled.js";

// src/find-common-ancestor.ts
var findCommonAncestor = /* @__PURE__ */ __name((id1, id2, { parentById }) => {
  const visited = /* @__PURE__ */ new Set();
  let currentId = id1;
  if (id1 === id2) {
    return parentById[id1] || "root";
  }
  while (currentId) {
    visited.add(currentId);
    if (currentId === id2) {
      return currentId;
    }
    currentId = parentById[currentId];
  }
  currentId = id2;
  while (currentId) {
    if (visited.has(currentId)) {
      return currentId;
    }
    currentId = parentById[currentId];
  }
  return "root";
}, "findCommonAncestor");

// src/geometry.ts
var EPS = 1;
var PUSH_OUT = 10;
var onBorder = /* @__PURE__ */ __name((bounds, p, tol = 0.5) => {
  const halfW = bounds.width / 2;
  const halfH = bounds.height / 2;
  const left = bounds.x - halfW;
  const right = bounds.x + halfW;
  const top = bounds.y - halfH;
  const bottom = bounds.y + halfH;
  const onLeft = Math.abs(p.x - left) <= tol && p.y >= top - tol && p.y <= bottom + tol;
  const onRight = Math.abs(p.x - right) <= tol && p.y >= top - tol && p.y <= bottom + tol;
  const onTop = Math.abs(p.y - top) <= tol && p.x >= left - tol && p.x <= right + tol;
  const onBottom = Math.abs(p.y - bottom) <= tol && p.x >= left - tol && p.x <= right + tol;
  return onLeft || onRight || onTop || onBottom;
}, "onBorder");
var intersection = /* @__PURE__ */ __name((node, outsidePoint, insidePoint) => {
  const x = node.x;
  const y = node.y;
  const dx = Math.abs(x - insidePoint.x);
  const w = node.width / 2;
  let r = insidePoint.x < outsidePoint.x ? w - dx : w + dx;
  const h = node.height / 2;
  const Q = Math.abs(outsidePoint.y - insidePoint.y);
  const R = Math.abs(outsidePoint.x - insidePoint.x);
  if (Math.abs(y - outsidePoint.y) * w > Math.abs(x - outsidePoint.x) * h) {
    const q = insidePoint.y < outsidePoint.y ? outsidePoint.y - h - y : y - h - outsidePoint.y;
    r = R * q / Q;
    const res = {
      x: insidePoint.x < outsidePoint.x ? insidePoint.x + r : insidePoint.x - R + r,
      y: insidePoint.y < outsidePoint.y ? insidePoint.y + Q - q : insidePoint.y - Q + q
    };
    if (R === 0) {
      res.x = outsidePoint.x;
    }
    if (Q === 0) {
      res.y = outsidePoint.y;
    }
    return res;
  } else {
    if (insidePoint.x < outsidePoint.x) {
      r = outsidePoint.x - w - x;
    } else {
      r = x - w - outsidePoint.x;
    }
    const q = Q * r / R;
    let _x = insidePoint.x < outsidePoint.x ? insidePoint.x + R - r : insidePoint.x - R + r;
    let _y = insidePoint.y < outsidePoint.y ? insidePoint.y + q : insidePoint.y - q;
    if (R === 0) {
      _x = outsidePoint.x;
    }
    if (Q === 0) {
      _y = outsidePoint.y;
    }
    return { x: _x, y: _y };
  }
}, "intersection");
var outsideNode = /* @__PURE__ */ __name((node, point) => {
  const x = node.x;
  const y = node.y;
  const dx = Math.abs(point.x - x);
  const dy = Math.abs(point.y - y);
  const w = node.width / 2;
  const h = node.height / 2;
  return dx >= w || dy >= h;
}, "outsideNode");
var ensureTrulyOutside = /* @__PURE__ */ __name((bounds, p, push = PUSH_OUT) => {
  const dx = Math.abs(p.x - bounds.x);
  const dy = Math.abs(p.y - bounds.y);
  const w = bounds.width / 2;
  const h = bounds.height / 2;
  if (Math.abs(dx - w) < EPS || Math.abs(dy - h) < EPS) {
    const dirX = p.x - bounds.x;
    const dirY = p.y - bounds.y;
    const len = Math.sqrt(dirX * dirX + dirY * dirY);
    if (len > 0) {
      return {
        x: bounds.x + dirX / len * (len + push),
        y: bounds.y + dirY / len * (len + push)
      };
    }
  }
  return p;
}, "ensureTrulyOutside");
var makeInsidePoint = /* @__PURE__ */ __name((bounds, outside, center) => {
  const isVertical = Math.abs(outside.x - bounds.x) < EPS;
  const isHorizontal = Math.abs(outside.y - bounds.y) < EPS;
  return {
    x: isVertical ? outside.x : outside.x < bounds.x ? bounds.x - bounds.width / 4 : bounds.x + bounds.width / 4,
    y: isHorizontal ? outside.y : center.y
  };
}, "makeInsidePoint");
var tryNodeIntersect = /* @__PURE__ */ __name((node, bounds, outside) => {
  if (!node?.intersect) {
    return null;
  }
  const res = node.intersect(outside);
  if (!res) {
    return null;
  }
  const wrongSide = outside.x < bounds.x && res.x > bounds.x || outside.x > bounds.x && res.x < bounds.x;
  if (wrongSide) {
    return null;
  }
  const dist = Math.hypot(outside.x - res.x, outside.y - res.y);
  if (dist <= EPS) {
    return null;
  }
  return res;
}, "tryNodeIntersect");
var fallbackIntersection = /* @__PURE__ */ __name((bounds, outside, center) => {
  const inside = makeInsidePoint(bounds, outside, center);
  return intersection(bounds, outside, inside);
}, "fallbackIntersection");
var computeNodeIntersection = /* @__PURE__ */ __name((node, bounds, outside, center) => {
  const outside2 = ensureTrulyOutside(bounds, outside);
  return tryNodeIntersect(node, bounds, outside2) ?? fallbackIntersection(bounds, outside2, center);
}, "computeNodeIntersection");
var replaceEndpoint = /* @__PURE__ */ __name((points, which, value, tol = 0.1) => {
  if (!value || points.length === 0) {
    return;
  }
  if (which === "start") {
    if (points.length > 0 && Math.abs(points[0].x - value.x) < tol && Math.abs(points[0].y - value.y) < tol) {
      points.shift();
    } else {
      points[0] = value;
    }
  } else {
    const last = points.length - 1;
    if (points.length > 0 && Math.abs(points[last].x - value.x) < tol && Math.abs(points[last].y - value.y) < tol) {
      points.pop();
    } else {
      points[last] = value;
    }
  }
}, "replaceEndpoint");

// src/render.ts
function dir2ElkDirection(dir) {
  switch (dir) {
    case "LR":
      return "RIGHT";
    case "RL":
      return "LEFT";
    case "TB":
    case "TD":
      return "DOWN";
    case "BT":
      return "UP";
    default:
      return "DOWN";
  }
}
__name(dir2ElkDirection, "dir2ElkDirection");
function buildSubgraphLayoutOptions(node, elkConfig, algorithm) {
  const layoutOptions = {
    "spacing.baseValue": 30,
    "nodeLabels.placement": "[H_CENTER V_TOP, INSIDE]",
    "elk.layered.mergeEdges": elkConfig?.mergeEdges,
    "nodePlacement.strategy": elkConfig?.nodePlacementStrategy
  };
  if (node.dir) {
    layoutOptions["elk.algorithm"] = algorithm;
    layoutOptions["elk.direction"] = dir2ElkDirection(node.dir);
    layoutOptions["elk.hierarchyHandling"] = "SEPARATE_CHILDREN";
  }
  return layoutOptions;
}
__name(buildSubgraphLayoutOptions, "buildSubgraphLayoutOptions");
var render = /* @__PURE__ */ __name(async (data4Layout, svg, {
  common,
  getConfig,
  insertCluster,
  insertEdge,
  insertEdgeLabel,
  insertMarkers,
  insertNode,
  interpolateToCurve,
  labelHelper,
  log,
  positionEdgeLabel
}, { algorithm }) => {
  const nodeDb = {};
  const clusterDb = {};
  const addVertex = /* @__PURE__ */ __name(async (nodeEl2, graph, nodeArr, node) => {
    const labelData = { width: 0, height: 0 };
    const config = getConfig();
    if (!node.isGroup) {
      const child = {
        id: node.id,
        width: node.width,
        height: node.height,
        // Store the original node data for later use
        label: node.label,
        isGroup: node.isGroup,
        shape: node.shape,
        padding: node.padding,
        cssClasses: node.cssClasses,
        cssStyles: node.cssStyles,
        look: node.look,
        // Include parentId for subgraph processing
        parentId: node.parentId
      };
      graph.children.push(child);
      nodeDb[node.id] = node;
      const childNodeEl = await insertNode(nodeEl2, node, { config, dir: node.dir });
      const boundingBox = childNodeEl.node().getBBox();
      child.domId = childNodeEl;
      child.width = boundingBox.width;
      child.height = boundingBox.height;
    } else {
      const child = {
        ...node,
        domId: void 0,
        children: []
      };
      graph.children.push(child);
      nodeDb[node.id] = child;
      await addVertices(nodeEl2, nodeArr, child, node.id);
      if (node.label) {
        const { shapeSvg, bbox } = await labelHelper(nodeEl2, node, void 0, true);
        labelData.width = bbox.width;
        labelData.wrappingWidth = config.flowchart.wrappingWidth;
        labelData.height = bbox.height - 2;
        labelData.labelNode = shapeSvg.node();
        shapeSvg.remove();
      } else {
        labelData.width = 0;
        labelData.height = 0;
      }
      child.labelData = labelData;
      child.domId = nodeEl2;
    }
  }, "addVertex");
  const addVertices = /* @__PURE__ */ __name(async function(nodeEl2, nodeArr, graph, parentId) {
    const siblings = nodeArr.filter((node) => node?.parentId === parentId);
    log.info("addVertices APA12", siblings, parentId);
    await Promise.all(
      siblings.map(async (node) => {
        await addVertex(nodeEl2, graph, nodeArr, node);
      })
    );
    return graph;
  }, "addVertices");
  const drawNodes = /* @__PURE__ */ __name(async (relX, relY, nodeArray, svg2, subgraphsEl, depth) => {
    await Promise.all(
      nodeArray.map(async function(node) {
        if (node) {
          nodeDb[node.id] ??= {};
          nodeDb[node.id].offset = {
            posX: node.x + relX,
            posY: node.y + relY,
            x: relX,
            y: relY,
            depth,
            width: Math.max(node.width, node.labels ? node.labels[0]?.width || 0 : 0),
            height: node.height
          };
          if (node.isGroup) {
            log.debug("Id abc88 subgraph = ", node.id, node.x, node.y, node.labelData);
            const subgraphEl = subgraphsEl.insert("g").attr("class", "subgraph");
            const clusterNode = JSON.parse(JSON.stringify(node));
            clusterNode.x = node.offset.posX + node.width / 2;
            clusterNode.y = node.offset.posY + node.height / 2;
            clusterNode.width = Math.max(clusterNode.width, node.labelData.width);
            await insertCluster(subgraphEl, clusterNode);
            log.debug("Id (UIO)= ", node.id, node.width, node.shape, node.labels);
          } else {
            log.info(
              "Id NODE = ",
              node.id,
              node.x,
              node.y,
              relX,
              relY,
              node.domId.node(),
              `translate(${node.x + relX + node.width / 2}, ${node.y + relY + node.height / 2})`
            );
            node.domId.attr(
              "transform",
              `translate(${node.x + relX + node.width / 2}, ${node.y + relY + node.height / 2})`
            );
          }
        }
      })
    );
    await Promise.all(
      nodeArray.map(async function(node) {
        if (node?.isGroup) {
          await drawNodes(relX + node.x, relY + node.y, node.children, svg2, subgraphsEl, depth + 1);
        }
      })
    );
  }, "drawNodes");
  const addSubGraphs = /* @__PURE__ */ __name((nodeArr) => {
    const parentLookupDb2 = { parentById: {}, childrenById: {} };
    const subgraphs = nodeArr.filter((node) => node.isGroup);
    log.info("Subgraphs - ", subgraphs);
    subgraphs.forEach((subgraph) => {
      const children = nodeArr.filter((node) => node.parentId === subgraph.id);
      children.forEach((node) => {
        parentLookupDb2.parentById[node.id] = subgraph.id;
        if (parentLookupDb2.childrenById[subgraph.id] === void 0) {
          parentLookupDb2.childrenById[subgraph.id] = [];
        }
        parentLookupDb2.childrenById[subgraph.id].push(node);
      });
    });
    return parentLookupDb2;
  }, "addSubGraphs");
  const getEdgeStartEndPoint = /* @__PURE__ */ __name((edge) => {
    const sourceId = edge.start;
    const targetId = edge.end;
    const source = sourceId;
    const target = targetId;
    const startNode = nodeDb[sourceId];
    const endNode = nodeDb[targetId];
    if (!startNode || !endNode) {
      return { source, target };
    }
    return { source, target, sourceId, targetId };
  }, "getEdgeStartEndPoint");
  const calcOffset = /* @__PURE__ */ __name(function(src, dest, parentLookupDb2) {
    const ancestor = findCommonAncestor(src, dest, parentLookupDb2);
    if (ancestor === void 0 || ancestor === "root") {
      return { x: 0, y: 0 };
    }
    const ancestorOffset = nodeDb[ancestor].offset;
    return { x: ancestorOffset.posX, y: ancestorOffset.posY };
  }, "calcOffset");
  const ARROW_MAP = {
    arrow_open: ["arrow_open", "arrow_open"],
    arrow_cross: ["arrow_open", "arrow_cross"],
    double_arrow_cross: ["arrow_cross", "arrow_cross"],
    arrow_point: ["arrow_open", "arrow_point"],
    double_arrow_point: ["arrow_point", "arrow_point"],
    arrow_circle: ["arrow_open", "arrow_circle"],
    double_arrow_circle: ["arrow_circle", "arrow_circle"]
  };
  const computeStroke = /* @__PURE__ */ __name((stroke, defaultStyle, defaultLabelStyle) => {
    let thickness = "normal";
    let pattern = "solid";
    let style = "";
    let labelStyle = "";
    if (stroke === "dotted") {
      pattern = "dotted";
      style = "fill:none;stroke-width:2px;stroke-dasharray:3;";
    } else if (stroke === "thick") {
      thickness = "thick";
      style = "stroke-width: 3.5px;fill:none;";
    } else {
      style = defaultStyle ?? "fill:none;";
      if (defaultLabelStyle !== void 0) {
        labelStyle = defaultLabelStyle;
      }
    }
    return { thickness, pattern, style, labelStyle };
  }, "computeStroke");
  const getCurve = /* @__PURE__ */ __name((edgeInterpolate, edgesDefaultInterpolate, confCurve) => {
    if (edgeInterpolate !== void 0) {
      return interpolateToCurve(edgeInterpolate, curveLinear);
    }
    if (edgesDefaultInterpolate !== void 0) {
      return interpolateToCurve(edgesDefaultInterpolate, curveLinear);
    }
    return interpolateToCurve(confCurve, curveLinear);
  }, "getCurve");
  const buildEdgeData = /* @__PURE__ */ __name((edge, defaults, common2) => {
    const edgeData = { style: "", labelStyle: "" };
    edgeData.minlen = edge.length || 1;
    edge.text = edge.label;
    edgeData.arrowhead = edge.type === "arrow_open" ? "none" : "normal";
    const arrowMap = ARROW_MAP[edge.type] ?? ARROW_MAP.arrow_open;
    edgeData.arrowTypeStart = arrowMap[0];
    edgeData.arrowTypeEnd = arrowMap[1];
    edgeData.startLabelRight = edge.startLabelRight;
    edgeData.endLabelLeft = edge.endLabelLeft;
    const strokeRes = computeStroke(edge.stroke, defaults.defaultStyle, defaults.defaultLabelStyle);
    edgeData.thickness = strokeRes.thickness;
    edgeData.pattern = strokeRes.pattern;
    edgeData.style = (edgeData.style || "") + (strokeRes.style || "");
    edgeData.labelStyle = (edgeData.labelStyle || "") + (strokeRes.labelStyle || "");
    edgeData.curve = getCurve(edge.interpolate, defaults.defaultInterpolate, defaults.confCurve);
    const hasText = (edge?.text ?? "") !== "";
    if (hasText) {
      edgeData.arrowheadStyle = "fill: #333";
      edgeData.labelpos = "c";
    } else if (edge.style !== void 0) {
      edgeData.arrowheadStyle = "fill: #333";
    }
    edgeData.labelType = edge.labelType;
    edgeData.label = (edge?.text ?? "").replace(common2.lineBreakRegex, "\n");
    if (edge.style === void 0) {
      edgeData.style = edgeData.style ?? "stroke: #333; stroke-width: 1.5px;fill:none;";
    }
    edgeData.labelStyle = edgeData.labelStyle.replace("color:", "fill:");
    return edgeData;
  }, "buildEdgeData");
  const addEdges = /* @__PURE__ */ __name(async function(dataForLayout, graph, svg2) {
    log.info("abc78 DAGA edges = ", dataForLayout);
    const edges = dataForLayout.edges;
    const labelsEl = svg2.insert("g").attr("class", "edgeLabels");
    const linkIdCnt = {};
    let defaultStyle;
    let defaultLabelStyle;
    await Promise.all(
      edges.map(async function(edge) {
        const linkIdBase = edge.id;
        if (linkIdCnt[linkIdBase] === void 0) {
          linkIdCnt[linkIdBase] = 0;
          log.info("abc78 new entry", linkIdBase, linkIdCnt[linkIdBase]);
        } else {
          linkIdCnt[linkIdBase]++;
          log.info("abc78 new entry", linkIdBase, linkIdCnt[linkIdBase]);
        }
        const linkId = linkIdBase;
        edge.id = linkId;
        log.info("abc78 new link id to be used is", linkIdBase, linkId, linkIdCnt[linkIdBase]);
        const linkNameStart = "LS_" + edge.start;
        const linkNameEnd = "LE_" + edge.end;
        const conf = getConfig();
        const edgeData = buildEdgeData(
          edge,
          {
            defaultStyle,
            defaultLabelStyle,
            defaultInterpolate: edges.defaultInterpolate,
            // @ts-ignore - conf.curve exists at runtime but is missing from typing
            confCurve: conf.curve
          },
          common
        );
        edgeData.id = linkId;
        edgeData.classes = "flowchart-link " + linkNameStart + " " + linkNameEnd;
        const labelEl = await insertEdgeLabel(labelsEl, edgeData);
        const { source, target, sourceId, targetId } = getEdgeStartEndPoint(edge);
        log.debug("abc78 source and target", source, target);
        graph.edges.push({
          ...edge,
          sources: [source],
          targets: [target],
          sourceId,
          targetId,
          labelEl,
          labels: [
            {
              width: edgeData.width,
              height: edgeData.height,
              orgWidth: edgeData.width,
              orgHeight: edgeData.height,
              text: edgeData.label,
              layoutOptions: {
                "edgeLabels.inline": "true",
                "edgeLabels.placement": "CENTER"
              }
            }
          ],
          edgeData
        });
      })
    );
    return graph;
  }, "addEdges");
  function setIncludeChildrenPolicy(nodeId, ancestorId) {
    const node = nodeDb[nodeId];
    if (!node) {
      return;
    }
    if (node?.layoutOptions === void 0) {
      node.layoutOptions = {};
    }
    node.layoutOptions["elk.hierarchyHandling"] = "INCLUDE_CHILDREN";
    if (node.id !== ancestorId) {
      setIncludeChildrenPolicy(node.parentId, ancestorId);
    }
  }
  __name(setIncludeChildrenPolicy, "setIncludeChildrenPolicy");
  const getEffectiveGroupWidth = /* @__PURE__ */ __name((node) => {
    const labelW = node?.labels?.[0]?.width ?? 0;
    const padding = node?.padding ?? 0;
    return Math.max(node.width ?? 0, labelW + padding);
  }, "getEffectiveGroupWidth");
  const boundsFor = /* @__PURE__ */ __name((node) => {
    const width = node?.isGroup ? getEffectiveGroupWidth(node) : node.width;
    return {
      x: node.offset.posX + node.width / 2,
      y: node.offset.posY + node.height / 2,
      width,
      height: node.height,
      padding: node.padding
    };
  }, "boundsFor");
  const approxEq = /* @__PURE__ */ __name((a, b, eps = 1e-6) => Math.abs(a - b) < eps, "approxEq");
  const isCenterApprox = /* @__PURE__ */ __name((pt, node) => approxEq(pt.x, node.x) && approxEq(pt.y, node.y), "isCenterApprox");
  const getCandidateBorderPoint = /* @__PURE__ */ __name((points, node, side) => {
    if (!points?.length) {
      return { candidate: { x: node.x, y: node.y }, centerApprox: true };
    }
    if (side === "start") {
      const first = points[0];
      const centerApprox = isCenterApprox(first, node);
      const candidate = centerApprox && points.length > 1 ? points[1] : first;
      return { candidate, centerApprox };
    } else {
      const last = points[points.length - 1];
      const centerApprox = isCenterApprox(last, node);
      const candidate = centerApprox && points.length > 1 ? points[points.length - 2] : last;
      return { candidate, centerApprox };
    }
  }, "getCandidateBorderPoint");
  const dropAutoCenterPoint = /* @__PURE__ */ __name((points, side, doDrop) => {
    if (!doDrop) {
      return;
    }
    if (side === "start") {
      if (points.length > 0) {
        points.shift();
      }
    } else {
      if (points.length > 0) {
        points.pop();
      }
    }
  }, "dropAutoCenterPoint");
  const applyStartIntersectionIfNeeded = /* @__PURE__ */ __name((points, startNode, startBounds) => {
    let firstOutsideStartIndex = -1;
    for (const [i, p] of points.entries()) {
      if (outsideNode(startBounds, p)) {
        firstOutsideStartIndex = i;
        break;
      }
    }
    if (firstOutsideStartIndex !== -1) {
      const outsidePointForStart = points[firstOutsideStartIndex];
      const startCenter = points[0];
      const startIntersection = computeNodeIntersection(
        startNode,
        startBounds,
        outsidePointForStart,
        startCenter
      );
      replaceEndpoint(points, "start", startIntersection);
      log.debug("UIO cutter2: start-only intersection applied", { startIntersection });
    }
  }, "applyStartIntersectionIfNeeded");
  const applyEndIntersectionIfNeeded = /* @__PURE__ */ __name((points, endNode, endBounds) => {
    let outsideIndexForEnd = -1;
    for (let i = points.length - 1; i >= 0; i--) {
      if (outsideNode(endBounds, points[i])) {
        outsideIndexForEnd = i;
        break;
      }
    }
    if (outsideIndexForEnd !== -1) {
      const outsidePointForEnd = points[outsideIndexForEnd];
      const endCenter = points[points.length - 1];
      const endIntersection = computeNodeIntersection(
        endNode,
        endBounds,
        outsidePointForEnd,
        endCenter
      );
      replaceEndpoint(points, "end", endIntersection);
      log.debug("UIO cutter2: end-only intersection applied", { endIntersection });
    }
  }, "applyEndIntersectionIfNeeded");
  const cutter2 = /* @__PURE__ */ __name((startNode, endNode, _points) => {
    const startBounds = boundsFor(startNode);
    const endBounds = boundsFor(endNode);
    if (_points.length === 0) {
      return [];
    }
    const points = [..._points];
    const startCenter = points[0];
    const endCenter = points[points.length - 1];
    log.debug("PPP cutter2: bounds", { startBounds, endBounds });
    log.debug("PPP cutter2: original points", _points);
    let firstOutsideStartIndex = -1;
    for (const [i, point] of points.entries()) {
      if (firstOutsideStartIndex === -1 && outsideNode(startBounds, point)) {
        firstOutsideStartIndex = i;
      }
      if (outsideNode(endBounds, point)) {
      }
    }
    if (firstOutsideStartIndex !== -1) {
      const outsidePointForStart = points[firstOutsideStartIndex];
      const startIntersection = computeNodeIntersection(
        startNode,
        startBounds,
        outsidePointForStart,
        startCenter
      );
      log.debug("UIO cutter2: start intersection", startIntersection);
      replaceEndpoint(points, "start", startIntersection);
    }
    let outsidePointForEnd = null;
    let outsideIndexForEnd = -1;
    for (let i = points.length - 1; i >= 0; i--) {
      if (outsideNode(endBounds, points[i])) {
        outsidePointForEnd = points[i];
        outsideIndexForEnd = i;
        break;
      }
    }
    if (!outsidePointForEnd && points.length > 1) {
      outsidePointForEnd = points[points.length - 2];
      outsideIndexForEnd = points.length - 2;
    }
    if (outsidePointForEnd) {
      const endIntersection = computeNodeIntersection(
        endNode,
        endBounds,
        outsidePointForEnd,
        endCenter
      );
      log.debug("UIO cutter2: end intersection", { endIntersection, outsideIndexForEnd });
      replaceEndpoint(points, "end", endIntersection);
    }
    if (points.length > 1) {
      const lastPoint = points[points.length - 1];
      const secondLastPoint = points[points.length - 2];
      const distance = Math.sqrt(
        (lastPoint.x - secondLastPoint.x) ** 2 + (lastPoint.y - secondLastPoint.y) ** 2
      );
      if (distance < 2) {
        log.debug("UIO cutter2: trimming tail point (too close)", {
          distance,
          lastPoint,
          secondLastPoint
        });
        points.pop();
      }
    }
    log.debug("UIO cutter2: final points", points);
    return points;
  }, "cutter2");
  const elk = new ELK();
  const element = svg.select("g");
  insertMarkers(element, data4Layout.markers, data4Layout.type, data4Layout.diagramId);
  let elkGraph = {
    id: "root",
    layoutOptions: {
      "elk.hierarchyHandling": "INCLUDE_CHILDREN",
      "elk.algorithm": algorithm,
      "nodePlacement.strategy": data4Layout.config.elk?.nodePlacementStrategy,
      "elk.layered.mergeEdges": data4Layout.config.elk?.mergeEdges,
      "elk.direction": "DOWN",
      "spacing.baseValue": 40,
      "elk.layered.crossingMinimization.forceNodeModelOrder": data4Layout.config.elk?.forceNodeModelOrder,
      "elk.layered.considerModelOrder.strategy": data4Layout.config.elk?.considerModelOrder,
      "elk.layered.unnecessaryBendpoints": true,
      "elk.layered.cycleBreaking.strategy": data4Layout.config.elk?.cycleBreakingStrategy,
      // 'elk.layered.cycleBreaking.strategy': 'GREEDY_MODEL_ORDER',
      // 'elk.layered.cycleBreaking.strategy': 'MODEL_ORDER',
      // 'spacing.nodeNode': 20,
      // 'spacing.nodeNodeBetweenLayers': 25,
      // 'spacing.edgeNode': 20,
      // 'spacing.edgeNodeBetweenLayers': 10,
      // 'spacing.edgeEdge': 10,
      // 'spacing.edgeEdgeBetweenLayers': 20,
      // 'spacing.nodeSelfLoop': 20,
      // Tweaking options
      // 'nodePlacement.favorStraightEdges': true,
      // 'elk.layered.nodePlacement.favorStraightEdges': true,
      // 'nodePlacement.feedbackEdges': true,
      "elk.layered.wrapping.multiEdge.improveCuts": true,
      "elk.layered.wrapping.multiEdge.improveWrappedEdges": true,
      // 'elk.layered.wrapping.strategy': 'MULTI_EDGE',
      // 'elk.layered.wrapping.strategy': 'SINGLE_EDGE',
      "elk.layered.edgeRouting.selfLoopDistribution": "EQUALLY",
      "elk.layered.mergeHierarchyEdges": true
      // 'elk.layered.feedbackEdges': true,
      // 'elk.layered.crossingMinimization.semiInteractive': true,
      // 'elk.layered.edgeRouting.splines.sloppy.layerSpacingFactor': 1,
      // 'elk.layered.edgeRouting.polyline.slopedEdgeZoneWidth': 4.0,
      // 'elk.layered.wrapping.validify.strategy': 'LOOK_BACK',
      // 'elk.insideSelfLoops.activate': true,
      // 'elk.separateConnectedComponents': true,
      // 'elk.alg.layered.options.EdgeStraighteningStrategy': 'NONE',
      // 'elk.layered.considerModelOrder.strategy': 'NODES_AND_EDGES', // NODES_AND_EDGES
      // 'elk.layered.considerModelOrder.strategy': 'EDGES', // NODES_AND_EDGES
      // 'elk.layered.wrapping.cutting.strategy': 'ARD', // NODES_AND_EDGES
    },
    children: [],
    edges: []
  };
  log.info("Drawing flowchart using v4 renderer", elk);
  const dir = data4Layout.direction ?? "DOWN";
  elkGraph.layoutOptions["elk.direction"] = dir2ElkDirection(dir);
  const parentLookupDb = addSubGraphs(data4Layout.nodes);
  const subGraphsEl = svg.insert("g").attr("class", "subgraphs");
  const nodeEl = svg.insert("g").attr("class", "nodes");
  elkGraph = await addVertices(nodeEl, data4Layout.nodes, elkGraph);
  const edgesEl = svg.insert("g").attr("class", "edges edgePaths");
  elkGraph = await addEdges(data4Layout, elkGraph, svg);
  const nodes = data4Layout.nodes;
  nodes.forEach((n) => {
    const node = nodeDb[n.id];
    if (parentLookupDb.childrenById[node.id] !== void 0) {
      node.labels = [
        {
          text: node.label,
          width: node?.labelData?.width ?? 50,
          height: node?.labelData?.height ?? 50
        }
      ];
      node.width = node.width + 2 * node.padding;
      log.debug("UIO node label", node?.labelData?.width, node.padding);
      node.layoutOptions = buildSubgraphLayoutOptions(node, data4Layout.config.elk, algorithm);
      delete node.x;
      delete node.y;
      delete node.width;
      delete node.height;
    }
  });
  log.debug("APA01 processing edges, count:", elkGraph.edges.length);
  elkGraph.edges.forEach((edge, index) => {
    log.debug("APA01 processing edge", index, ":", edge);
    const source = edge.sources[0];
    const target = edge.targets[0];
    log.debug("APA01 source:", source, "target:", target);
    log.debug("APA01 nodeDb[source]:", nodeDb[source]);
    log.debug("APA01 nodeDb[target]:", nodeDb[target]);
    if (nodeDb[source] && nodeDb[target] && nodeDb[source].parentId !== nodeDb[target].parentId) {
      const ancestorId = findCommonAncestor(source, target, parentLookupDb);
      setIncludeChildrenPolicy(source, ancestorId);
      setIncludeChildrenPolicy(target, ancestorId);
    }
  });
  log.debug("APA01 before");
  log.debug("APA01 elkGraph structure:", JSON.stringify(elkGraph, null, 2));
  log.debug("APA01 elkGraph.children length:", elkGraph.children?.length);
  log.debug("APA01 elkGraph.edges length:", elkGraph.edges?.length);
  elkGraph.edges?.forEach((edge, index) => {
    log.debug(`APA01 validating edge ${index}:`, edge);
    if (edge.sources) {
      edge.sources.forEach((sourceId) => {
        const sourceExists = elkGraph.children?.some((child) => child.id === sourceId);
        log.debug(`APA01 source ${sourceId} exists:`, sourceExists);
      });
    }
    if (edge.targets) {
      edge.targets.forEach((targetId) => {
        const targetExists = elkGraph.children?.some((child) => child.id === targetId);
        log.debug(`APA01 target ${targetId} exists:`, targetExists);
      });
    }
  });
  let g;
  try {
    g = await elk.layout(elkGraph);
    log.debug("APA01 after - success");
    log.info("APA01 layout result:", JSON.stringify(g, null, 2));
  } catch (error) {
    log.error("APA01 ELK layout error:", error);
    log.error("APA01 elkGraph that caused error:", JSON.stringify(elkGraph, null, 2));
    throw error;
  }
  await drawNodes(0, 0, g.children, svg, subGraphsEl, 0);
  g.edges?.map(
    (edge) => {
      const startNode = nodeDb[edge.sources[0]];
      const startCluster = parentLookupDb[edge.sources[0]];
      const endNode = nodeDb[edge.targets[0]];
      const sourceId = edge.start;
      const targetId = edge.end;
      const offset = calcOffset(sourceId, targetId, parentLookupDb);
      log.debug(
        "APA18 offset",
        offset,
        sourceId,
        " ==> ",
        targetId,
        "edge:",
        edge,
        "cluster:",
        startCluster,
        startNode
      );
      if (edge.sections) {
        const src = edge.sections[0].startPoint;
        const dest = edge.sections[0].endPoint;
        const segments = edge.sections[0].bendPoints ? edge.sections[0].bendPoints : [];
        const segPoints = segments.map((segment) => {
          return { x: segment.x + offset.x, y: segment.y + offset.y };
        });
        edge.points = [
          { x: src.x + offset.x, y: src.y + offset.y },
          ...segPoints,
          { x: dest.x + offset.x, y: dest.y + offset.y }
        ];
        let sw = startNode.width;
        let ew = endNode.width;
        if (startNode.isGroup) {
          const bbox = startNode.domId.node().getBBox();
          sw = Math.max(startNode.width, startNode.labels[0].width + startNode.padding);
          log.info(
            "UIO width",
            startNode.id,
            startNode.width,
            "bbox.width=",
            bbox.width,
            "lw=",
            startNode.labels[0].width,
            "node:",
            startNode.width,
            "SW = ",
            sw
            // 'HTML:',
            // startNode.domId.node().innerHTML
          );
        }
        if (endNode.isGroup) {
          const bbox = endNode.domId.node().getBBox();
          ew = Math.max(endNode.width, endNode.labels[0].width + endNode.padding);
          log.debug(
            "UIO width",
            startNode.id,
            startNode.width,
            bbox.width,
            "EW = ",
            ew,
            "HTML:",
            startNode.innerHTML
          );
        }
        startNode.x = startNode.offset.posX + startNode.width / 2;
        startNode.y = startNode.offset.posY + startNode.height / 2;
        endNode.x = endNode.offset.posX + endNode.width / 2;
        endNode.y = endNode.offset.posY + endNode.height / 2;
        const shouldAddStartCenter = startNode.shape !== "rect33";
        const shouldAddEndCenter = endNode.shape !== "rect33";
        if (shouldAddStartCenter) {
          edge.points.unshift({
            x: startNode.x,
            y: startNode.y
          });
        }
        if (shouldAddEndCenter) {
          edge.points.push({
            x: endNode.x,
            y: endNode.y
          });
        }
        const prevPoints = Array.isArray(edge.points) ? [...edge.points] : [];
        const endBounds = boundsFor(endNode);
        log.debug(
          "PPP cutter2: Points before cutter2:",
          JSON.stringify(edge.points),
          "endBounds:",
          endBounds,
          onBorder(endBounds, edge.points[edge.points.length - 1])
        );
        {
          const startBounds = boundsFor(startNode);
          const endBounds2 = boundsFor(endNode);
          const startIsGroup = !!startNode?.isGroup;
          const endIsGroup = !!endNode?.isGroup;
          const { candidate: startCandidate, centerApprox: startCenterApprox } = getCandidateBorderPoint(prevPoints, startNode, "start");
          const { candidate: endCandidate, centerApprox: endCenterApprox } = getCandidateBorderPoint(prevPoints, endNode, "end");
          const skipStart = startIsGroup && onBorder(startBounds, startCandidate);
          const skipEnd = endIsGroup && onBorder(endBounds2, endCandidate);
          dropAutoCenterPoint(prevPoints, "start", skipStart && startCenterApprox);
          dropAutoCenterPoint(prevPoints, "end", skipEnd && endCenterApprox);
          if (skipStart || skipEnd) {
            if (!skipStart) {
              applyStartIntersectionIfNeeded(prevPoints, startNode, startBounds);
            }
            if (!skipEnd) {
              applyEndIntersectionIfNeeded(prevPoints, endNode, endBounds2);
            }
            log.debug("PPP cutter2: skipping cutter2 due to on-border group endpoint(s)", {
              skipStart,
              skipEnd,
              startCenterApprox,
              endCenterApprox,
              startCandidate,
              endCandidate
            });
            edge.points = prevPoints;
          } else {
            edge.points = cutter2(startNode, endNode, prevPoints);
          }
        }
        log.debug("PPP cutter2: Points after cutter2:", JSON.stringify(edge.points));
        const hasNaN = /* @__PURE__ */ __name((pts) => pts?.some((p) => !Number.isFinite(p?.x) || !Number.isFinite(p?.y)), "hasNaN");
        if (!Array.isArray(edge.points) || edge.points.length < 2 || hasNaN(edge.points)) {
          log.warn(
            "POI cutter2: Invalid points from cutter2, falling back to prevPoints",
            edge.points
          );
          const cleaned = prevPoints.filter((p) => Number.isFinite(p?.x) && Number.isFinite(p?.y));
          edge.points = cleaned.length >= 2 ? cleaned : prevPoints;
        }
        log.debug("UIO cutter2: Points after cutter2 (sanitized):", edge.points);
        const deduped = edge.points.filter(
          (p, i, arr) => {
            if (i === 0) {
              return true;
            }
            const prev = arr[i - 1];
            return Math.abs(p.x - prev.x) > 1e-6 || Math.abs(p.y - prev.y) > 1e-6;
          }
        );
        if (deduped.length !== edge.points.length) {
          log.debug("UIO cutter2: removed consecutive duplicate points", {
            before: edge.points,
            after: deduped
          });
        }
        edge.points = deduped;
        edge.curve = "rounded";
        const paths = insertEdge(
          edgesEl,
          edge,
          clusterDb,
          data4Layout.type,
          startNode,
          endNode,
          data4Layout.diagramId,
          true
        );
        log.info("APA12 edge points after insert", JSON.stringify(edge.points));
        edge.x = edge.labels[0].x + offset.x + edge.labels[0].width / 2;
        edge.y = edge.labels[0].y + offset.y + edge.labels[0].height / 2;
        positionEdgeLabel(edge, paths);
      }
    }
  );
}, "render");
export {
  buildSubgraphLayoutOptions,
  dir2ElkDirection,
  render
};
