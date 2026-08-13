var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// ../../node_modules/.pnpm/non-layered-tidy-tree-layout@2.0.2/node_modules/non-layered-tidy-tree-layout/src/algorithm.js
var Tree = class {
  static {
    __name(this, "Tree");
  }
  constructor(width, height, y, children) {
    this.w = width;
    this.h = height;
    this.y = y;
    this.c = children;
    this.cs = children.length;
    this.x = 0;
    this.prelim = 0;
    this.mod = 0;
    this.shift = 0;
    this.change = 0;
    this.tl = null;
    this.tr = null;
    this.el = null;
    this.er = null;
    this.msel = 0;
    this.mser = 0;
  }
};
function setExtremes(tree) {
  if (tree.cs === 0) {
    tree.el = tree;
    tree.er = tree;
    tree.msel = tree.mser = 0;
  } else {
    tree.el = tree.c[0].el;
    tree.msel = tree.c[0].msel;
    tree.er = tree.c[tree.cs - 1].er;
    tree.mser = tree.c[tree.cs - 1].mser;
  }
}
__name(setExtremes, "setExtremes");
function bottom(tree) {
  return tree.y + tree.h;
}
__name(bottom, "bottom");
var IYL = class {
  static {
    __name(this, "IYL");
  }
  constructor(lowY, index, next) {
    this.lowY = lowY;
    this.index = index;
    this.next = next;
  }
};
function updateIYL(minY, i, ih) {
  while (ih !== null && minY >= ih.lowY) {
    ih = ih.next;
  }
  return new IYL(minY, i, ih);
}
__name(updateIYL, "updateIYL");
function distributeExtra(tree, i, si, distance) {
  if (si !== i - 1) {
    const nr = i - si;
    tree.c[si + 1].shift += distance / nr;
    tree.c[i].shift -= distance / nr;
    tree.c[i].change -= distance - distance / nr;
  }
}
__name(distributeExtra, "distributeExtra");
function moveSubtree(tree, i, si, distance) {
  tree.c[i].mod += distance;
  tree.c[i].msel += distance;
  tree.c[i].mser += distance;
  distributeExtra(tree, i, si, distance);
}
__name(moveSubtree, "moveSubtree");
function nextLeftContour(tree) {
  return tree.cs === 0 ? tree.tl : tree.c[0];
}
__name(nextLeftContour, "nextLeftContour");
function nextRightContour(tree) {
  return tree.cs === 0 ? tree.tr : tree.c[tree.cs - 1];
}
__name(nextRightContour, "nextRightContour");
function setLeftThread(tree, i, cl, modsumcl) {
  const li = tree.c[0].el;
  li.tl = cl;
  const diff = modsumcl - cl.mod - tree.c[0].msel;
  li.mod += diff;
  li.prelim -= diff;
  tree.c[0].el = tree.c[i].el;
  tree.c[0].msel = tree.c[i].msel;
}
__name(setLeftThread, "setLeftThread");
function setRightThread(tree, i, sr, modsumsr) {
  const ri = tree.c[i].er;
  ri.tr = sr;
  const diff = modsumsr - sr.mod - tree.c[i].mser;
  ri.mod += diff;
  ri.prelim -= diff;
  tree.c[i].er = tree.c[i - 1].er;
  tree.c[i].mser = tree.c[i - 1].mser;
}
__name(setRightThread, "setRightThread");
function seperate(tree, i, ih) {
  let sr = tree.c[i - 1];
  let mssr = sr.mod;
  let cl = tree.c[i];
  let mscl = cl.mod;
  while (sr !== null && cl !== null) {
    if (bottom(sr) > ih.lowY) {
      ih = ih.next;
    }
    const distance = mssr + sr.prelim + sr.w - (mscl + cl.prelim);
    if (distance > 0) {
      mscl += distance;
      moveSubtree(tree, i, ih.index, distance);
    }
    const sy = bottom(sr);
    const cy = bottom(cl);
    if (sy <= cy) {
      sr = nextRightContour(sr);
      if (sr !== null) {
        mssr += sr.mod;
      }
    }
    if (sy >= cy) {
      cl = nextLeftContour(cl);
      if (cl !== null) {
        mscl += cl.mod;
      }
    }
  }
  if (sr === null && cl !== null) {
    setLeftThread(tree, i, cl, mscl);
  } else if (sr !== null && cl === null) {
    setRightThread(tree, i, sr, mssr);
  }
}
__name(seperate, "seperate");
function positionRoot(tree) {
  tree.prelim = (tree.c[0].prelim + tree.c[0].mod + tree.c[tree.cs - 1].mod + tree.c[tree.cs - 1].prelim + tree.c[tree.cs - 1].w) / 2 - tree.w / 2;
}
__name(positionRoot, "positionRoot");
function firstWalk(tree) {
  if (tree.cs === 0) {
    setExtremes(tree);
    return;
  }
  firstWalk(tree.c[0]);
  let ih = updateIYL(bottom(tree.c[0].el), 0, null);
  for (let i = 1; i < tree.cs; i++) {
    firstWalk(tree.c[i]);
    const minY = bottom(tree.c[i].er);
    seperate(tree, i, ih);
    ih = updateIYL(minY, i, ih);
  }
  positionRoot(tree);
  setExtremes(tree);
}
__name(firstWalk, "firstWalk");
function addChildSpacing(tree) {
  let d = 0;
  let modsumdelta = 0;
  for (let i = 0; i < tree.cs; i++) {
    d += tree.c[i].shift;
    modsumdelta += d + tree.c[i].change;
    tree.c[i].mod += modsumdelta;
  }
}
__name(addChildSpacing, "addChildSpacing");
function secondWalk(tree, modsum) {
  modsum += tree.mod;
  tree.x = tree.prelim + modsum;
  addChildSpacing(tree);
  for (let i = 0; i < tree.cs; i++) {
    secondWalk(tree.c[i], modsum);
  }
}
__name(secondWalk, "secondWalk");
function layout(tree) {
  firstWalk(tree);
  secondWalk(tree, 0);
}
__name(layout, "layout");

// ../../node_modules/.pnpm/non-layered-tidy-tree-layout@2.0.2/node_modules/non-layered-tidy-tree-layout/src/helpers.js
var BoundingBox = class {
  static {
    __name(this, "BoundingBox");
  }
  /**
   * @param {number} gap - the gap between sibling nodes
   * @param {number} bottomPadding - the height reserved for connection drawing
   */
  constructor(gap, bottomPadding) {
    this.gap = gap;
    this.bottomPadding = bottomPadding;
  }
  addBoundingBox(width, height) {
    return { width: width + this.gap, height: height + this.bottomPadding };
  }
  /**
   * Return the coordinate without the bounding box for a node
   */
  removeBoundingBox(x, y) {
    return { x: x + this.gap / 2, y };
  }
};
var Layout = class {
  static {
    __name(this, "Layout");
  }
  constructor(boundingBox) {
    this.bb = boundingBox;
  }
  /**
   * Layout treeData.
   * Return modified treeData and the bounding box encompassing all the nodes.
   * 
   * See getSize() for more explanation.
   */
  layout(treeData) {
    const tree = this.convert(treeData);
    layout(tree);
    const { boundingBox, result } = this.assignLayout(tree, treeData);
    return { result, boundingBox };
  }
  /**
   * Returns Tree to layout, with bounding boxes added to each node.
   */
  convert(treeData, y = 0) {
    if (treeData === null) return null;
    const { width, height } = this.bb.addBoundingBox(
      treeData.width,
      treeData.height
    );
    let children = [];
    if (treeData.children && treeData.children.length) {
      for (let i = 0; i < treeData.children.length; i++) {
        children[i] = this.convert(treeData.children[i], y + height);
      }
    }
    return new Tree(width, height, y, children);
  }
  /**
   * Assign layout tree x, y coordinates back to treeData,
   * with bounding boxes removed.
   */
  assignCoordinates(tree, treeData) {
    const { x, y } = this.bb.removeBoundingBox(tree.x, tree.y);
    treeData.x = x;
    treeData.y = y;
    for (let i = 0; i < tree.c.length; i++) {
      this.assignCoordinates(tree.c[i], treeData.children[i]);
    }
  }
  /**
   * Return the bounding box that encompasses all the nodes.
   * The result has a structure of
   * { left: number, right: number, top: number, bottom: nubmer}.
   * This is not the same bounding box concept as the `BoundingBox` class
   * used to construct `Layout` class.
   */
  getSize(treeData, box = null) {
    const { x, y, width, height } = treeData;
    if (box === null) {
      box = { left: x, right: x + width, top: y, bottom: y + height };
    }
    box.left = Math.min(box.left, x);
    box.right = Math.max(box.right, x + width);
    box.top = Math.min(box.top, y);
    box.bottom = Math.max(box.bottom, y + height);
    if (treeData.children) {
      for (const child of treeData.children) {
        this.getSize(child, box);
      }
    }
    return box;
  }
  /**
   * This function does assignCoordinates and getSize in one pass.
   */
  assignLayout(tree, treeData, box = null) {
    const { x, y } = this.bb.removeBoundingBox(tree.x, tree.y);
    treeData.x = x;
    treeData.y = y;
    const { width, height } = treeData;
    if (box === null) {
      box = { left: x, right: x + width, top: y, bottom: y + height };
    }
    box.left = Math.min(box.left, x);
    box.right = Math.max(box.right, x + width);
    box.top = Math.min(box.top, y);
    box.bottom = Math.max(box.bottom, y + height);
    for (let i = 0; i < tree.c.length; i++) {
      this.assignLayout(tree.c[i], treeData.children[i], box);
    }
    return { result: treeData, boundingBox: box };
  }
};

// src/layout.ts
function executeTidyTreeLayout(data) {
  let intersectionShift = 50;
  return new Promise((resolve, reject) => {
    try {
      if (!data.nodes || !Array.isArray(data.nodes) || data.nodes.length === 0) {
        throw new Error("No nodes found in layout data");
      }
      if (!data.edges || !Array.isArray(data.edges)) {
        data.edges = [];
      }
      const { leftTree, rightTree, rootNode } = convertToDualTreeFormat(data);
      const gap = 20;
      const bottomPadding = 40;
      intersectionShift = 30;
      const bb = new BoundingBox(gap, bottomPadding);
      const layout2 = new Layout(bb);
      let leftResult = null;
      let rightResult = null;
      if (leftTree) {
        const leftLayoutResult = layout2.layout(leftTree);
        leftResult = leftLayoutResult.result;
      }
      if (rightTree) {
        const rightLayoutResult = layout2.layout(rightTree);
        rightResult = rightLayoutResult.result;
      }
      const positionedNodes = combineAndPositionTrees(rootNode, leftResult, rightResult);
      const positionedEdges = calculateEdgePositions(
        data.edges,
        positionedNodes,
        intersectionShift
      );
      resolve({
        nodes: positionedNodes,
        edges: positionedEdges
      });
    } catch (error) {
      reject(error);
    }
  });
}
__name(executeTidyTreeLayout, "executeTidyTreeLayout");
function convertToDualTreeFormat(data) {
  const { nodes, edges } = data;
  const nodeMap = /* @__PURE__ */ new Map();
  nodes.forEach((node) => nodeMap.set(node.id, node));
  const children = /* @__PURE__ */ new Map();
  const parents = /* @__PURE__ */ new Map();
  edges.forEach((edge) => {
    const parentId = edge.start;
    const childId = edge.end;
    if (parentId && childId) {
      if (!children.has(parentId)) {
        children.set(parentId, []);
      }
      children.get(parentId).push(childId);
      parents.set(childId, parentId);
    }
  });
  const rootNodeData = nodes.find((node) => !parents.has(node.id));
  if (!rootNodeData && nodes.length === 0) {
    throw new Error("No nodes available to create tree");
  }
  const actualRoot = rootNodeData ?? nodes[0];
  const rootNode = {
    id: actualRoot.id,
    width: actualRoot.width ?? 100,
    height: actualRoot.height ?? 50,
    _originalNode: actualRoot
  };
  const rootChildren = children.get(actualRoot.id) ?? [];
  const leftChildren = [];
  const rightChildren = [];
  rootChildren.forEach((childId, index) => {
    if (index % 2 === 0) {
      leftChildren.push(childId);
    } else {
      rightChildren.push(childId);
    }
  });
  const leftTree = leftChildren.length > 0 ? buildSubTree(leftChildren, children, nodeMap) : null;
  const rightTree = rightChildren.length > 0 ? buildSubTree(rightChildren, children, nodeMap) : null;
  return { leftTree, rightTree, rootNode };
}
__name(convertToDualTreeFormat, "convertToDualTreeFormat");
function buildSubTree(rootChildren, children, nodeMap) {
  const virtualRoot = {
    id: `virtual-root-${Math.random()}`,
    width: 1,
    height: 1,
    children: rootChildren.map((childId) => nodeMap.get(childId)).filter((child) => child !== void 0).map((child) => convertNodeToTidyTreeTransposed(child, children, nodeMap))
  };
  return virtualRoot;
}
__name(buildSubTree, "buildSubTree");
function convertNodeToTidyTreeTransposed(node, children, nodeMap) {
  const childIds = children.get(node.id) ?? [];
  const childNodes = childIds.map((childId) => nodeMap.get(childId)).filter((child) => child !== void 0).map((child) => convertNodeToTidyTreeTransposed(child, children, nodeMap));
  return {
    id: node.id,
    width: node.height ?? 50,
    height: node.width ?? 100,
    children: childNodes.length > 0 ? childNodes : void 0,
    _originalNode: node
  };
}
__name(convertNodeToTidyTreeTransposed, "convertNodeToTidyTreeTransposed");
function combineAndPositionTrees(rootNode, leftResult, rightResult) {
  const positionedNodes = [];
  const rootX = 0;
  const rootY = 0;
  const treeSpacing = rootNode.width / 2 + 30;
  const leftTreeNodes = [];
  const rightTreeNodes = [];
  if (leftResult?.children) {
    positionLeftTreeBidirectional(leftResult.children, leftTreeNodes, rootX - treeSpacing, rootY);
  }
  if (rightResult?.children) {
    positionRightTreeBidirectional(
      rightResult.children,
      rightTreeNodes,
      rootX + treeSpacing,
      rootY
    );
  }
  let leftTreeCenterY = 0;
  let rightTreeCenterY = 0;
  if (leftTreeNodes.length > 0) {
    const leftTreeXPositions = [...new Set(leftTreeNodes.map((node) => node.x))].sort(
      (a, b) => b - a
    );
    const firstLevelLeftX = leftTreeXPositions[0];
    const firstLevelLeftNodes = leftTreeNodes.filter((node) => node.x === firstLevelLeftX);
    if (firstLevelLeftNodes.length > 0) {
      const leftMinY = Math.min(
        ...firstLevelLeftNodes.map((node) => node.y - (node.height ?? 50) / 2)
      );
      const leftMaxY = Math.max(
        ...firstLevelLeftNodes.map((node) => node.y + (node.height ?? 50) / 2)
      );
      leftTreeCenterY = (leftMinY + leftMaxY) / 2;
    }
  }
  if (rightTreeNodes.length > 0) {
    const rightTreeXPositions = [...new Set(rightTreeNodes.map((node) => node.x))].sort(
      (a, b) => a - b
    );
    const firstLevelRightX = rightTreeXPositions[0];
    const firstLevelRightNodes = rightTreeNodes.filter((node) => node.x === firstLevelRightX);
    if (firstLevelRightNodes.length > 0) {
      const rightMinY = Math.min(
        ...firstLevelRightNodes.map((node) => node.y - (node.height ?? 50) / 2)
      );
      const rightMaxY = Math.max(
        ...firstLevelRightNodes.map((node) => node.y + (node.height ?? 50) / 2)
      );
      rightTreeCenterY = (rightMinY + rightMaxY) / 2;
    }
  }
  const leftTreeOffset = -leftTreeCenterY;
  const rightTreeOffset = -rightTreeCenterY;
  positionedNodes.push({
    id: String(rootNode.id),
    x: rootX,
    y: rootY + 20,
    section: "root",
    width: rootNode._originalNode?.width ?? rootNode.width,
    height: rootNode._originalNode?.height ?? rootNode.height,
    originalNode: rootNode._originalNode
  });
  const leftTreeNodesWithOffset = leftTreeNodes.map((node) => ({
    id: node.id,
    x: node.x - (node.width ?? 0) / 2,
    y: node.y + leftTreeOffset + (node.height ?? 0) / 2,
    section: "left",
    width: node.width,
    height: node.height,
    originalNode: node.originalNode
  }));
  const rightTreeNodesWithOffset = rightTreeNodes.map((node) => ({
    id: node.id,
    x: node.x + (node.width ?? 0) / 2,
    y: node.y + rightTreeOffset + (node.height ?? 0) / 2,
    section: "right",
    width: node.width,
    height: node.height,
    originalNode: node.originalNode
  }));
  positionedNodes.push(...leftTreeNodesWithOffset);
  positionedNodes.push(...rightTreeNodesWithOffset);
  return positionedNodes;
}
__name(combineAndPositionTrees, "combineAndPositionTrees");
function positionLeftTreeBidirectional(nodes, positionedNodes, offsetX, offsetY) {
  nodes.forEach((node) => {
    const distanceFromRoot = node.y ?? 0;
    const verticalPosition = node.x ?? 0;
    const originalWidth = node._originalNode?.width ?? 100;
    const originalHeight = node._originalNode?.height ?? 50;
    const adjustedY = offsetY + verticalPosition;
    positionedNodes.push({
      id: String(node.id),
      x: offsetX - distanceFromRoot,
      y: adjustedY,
      width: originalWidth,
      height: originalHeight,
      originalNode: node._originalNode
    });
    if (node.children) {
      positionLeftTreeBidirectional(node.children, positionedNodes, offsetX, offsetY);
    }
  });
}
__name(positionLeftTreeBidirectional, "positionLeftTreeBidirectional");
function positionRightTreeBidirectional(nodes, positionedNodes, offsetX, offsetY) {
  nodes.forEach((node) => {
    const distanceFromRoot = node.y ?? 0;
    const verticalPosition = node.x ?? 0;
    const originalWidth = node._originalNode?.width ?? 100;
    const originalHeight = node._originalNode?.height ?? 50;
    const adjustedY = offsetY + verticalPosition;
    positionedNodes.push({
      id: String(node.id),
      x: offsetX + distanceFromRoot,
      y: adjustedY,
      width: originalWidth,
      height: originalHeight,
      originalNode: node._originalNode
    });
    if (node.children) {
      positionRightTreeBidirectional(node.children, positionedNodes, offsetX, offsetY);
    }
  });
}
__name(positionRightTreeBidirectional, "positionRightTreeBidirectional");
function computeCircleEdgeIntersection(circle, lineStart, lineEnd) {
  const radius = Math.min(circle.width, circle.height) / 2;
  const dx = lineEnd.x - lineStart.x;
  const dy = lineEnd.y - lineStart.y;
  const length = Math.sqrt(dx * dx + dy * dy);
  if (length === 0) {
    return lineStart;
  }
  const nx = dx / length;
  const ny = dy / length;
  return {
    x: circle.x - nx * radius,
    y: circle.y - ny * radius
  };
}
__name(computeCircleEdgeIntersection, "computeCircleEdgeIntersection");
function intersection(node, outsidePoint, insidePoint) {
  const x = node.x;
  const y = node.y;
  if (!node.width || !node.height) {
    return { x: outsidePoint.x, y: outsidePoint.y };
  }
  const dx = Math.abs(x - insidePoint.x);
  const w = node?.width / 2;
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
    if (r === 0) {
      res.x = outsidePoint.x;
      res.y = outsidePoint.y;
    }
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
    if (r === 0) {
      _x = outsidePoint.x;
      _y = outsidePoint.y;
    }
    if (R === 0) {
      _x = outsidePoint.x;
    }
    if (Q === 0) {
      _y = outsidePoint.y;
    }
    return { x: _x, y: _y };
  }
}
__name(intersection, "intersection");
function calculateEdgePositions(edges, positionedNodes, intersectionShift) {
  const nodeInfo = /* @__PURE__ */ new Map();
  positionedNodes.forEach((node) => {
    nodeInfo.set(node.id, node);
  });
  return edges.map((edge) => {
    const sourceNode = nodeInfo.get(edge.start ?? "");
    const targetNode = nodeInfo.get(edge.end ?? "");
    if (!sourceNode || !targetNode) {
      return {
        id: edge.id,
        source: edge.start ?? "",
        target: edge.end ?? "",
        startX: 0,
        startY: 0,
        midX: 0,
        midY: 0,
        endX: 0,
        endY: 0,
        points: [{ x: 0, y: 0 }],
        sourceSection: void 0,
        targetSection: void 0,
        sourceWidth: void 0,
        sourceHeight: void 0,
        targetWidth: void 0,
        targetHeight: void 0
      };
    }
    const sourceCenter = { x: sourceNode.x, y: sourceNode.y };
    const targetCenter = { x: targetNode.x, y: targetNode.y };
    const isSourceRound = ["circle", "cloud", "bang"].includes(
      sourceNode.originalNode?.shape ?? ""
    );
    const isTargetRound = ["circle", "cloud", "bang"].includes(
      targetNode.originalNode?.shape ?? ""
    );
    let startPos = isSourceRound ? computeCircleEdgeIntersection(
      {
        x: sourceNode.x,
        y: sourceNode.y,
        width: sourceNode.width ?? 100,
        height: sourceNode.height ?? 100
      },
      targetCenter,
      sourceCenter
    ) : intersection(sourceNode, sourceCenter, targetCenter);
    let endPos = isTargetRound ? computeCircleEdgeIntersection(
      {
        x: targetNode.x,
        y: targetNode.y,
        width: targetNode.width ?? 100,
        height: targetNode.height ?? 100
      },
      sourceCenter,
      targetCenter
    ) : intersection(targetNode, targetCenter, sourceCenter);
    const midX = (startPos.x + endPos.x) / 2;
    const midY = (startPos.y + endPos.y) / 2;
    const points = [startPos];
    if (sourceNode.section === "left") {
      points.push({
        x: sourceNode.x - (sourceNode.width ?? 0) / 2 - intersectionShift,
        y: sourceNode.y
      });
    } else if (sourceNode.section === "right") {
      points.push({
        x: sourceNode.x + (sourceNode.width ?? 0) / 2 + intersectionShift,
        y: sourceNode.y
      });
    } else if (sourceNode.section === "root") {
      if (targetNode.section === "right") {
        points.push({
          x: sourceNode.x + (sourceNode.width ?? 0) / 2 + intersectionShift,
          y: sourceNode.y
        });
      } else if (targetNode.section === "left") {
        points.push({
          x: sourceNode.x - (sourceNode.width ?? 0) / 2 - intersectionShift,
          y: sourceNode.y
        });
      }
    }
    if (targetNode.section === "left") {
      points.push({
        x: targetNode.x + (targetNode.width ?? 0) / 2 + intersectionShift,
        y: targetNode.y
      });
    } else if (targetNode.section === "right") {
      points.push({
        x: targetNode.x - (targetNode.width ?? 0) / 2 - intersectionShift,
        y: targetNode.y
      });
    } else if (targetNode.section === "root") {
      if (sourceNode.section === "right") {
        points.push({
          x: targetNode.x + (targetNode.width ?? 0) / 2 + intersectionShift,
          y: targetNode.y
        });
      } else if (sourceNode.section === "left") {
        points.push({
          x: targetNode.x - (targetNode.width ?? 0) / 2 - intersectionShift,
          y: targetNode.y
        });
      }
    }
    points.push(endPos);
    const secondPoint = points.length > 1 ? points[1] : targetCenter;
    startPos = isSourceRound ? computeCircleEdgeIntersection(
      {
        x: sourceNode.x,
        y: sourceNode.y,
        width: sourceNode.width ?? 100,
        height: sourceNode.height ?? 100
      },
      secondPoint,
      sourceCenter
    ) : intersection(sourceNode, secondPoint, sourceCenter);
    points[0] = startPos;
    const secondLastPoint = points.length > 1 ? points[points.length - 2] : sourceCenter;
    endPos = isTargetRound ? computeCircleEdgeIntersection(
      {
        x: targetNode.x,
        y: targetNode.y,
        width: targetNode.width ?? 100,
        height: targetNode.height ?? 100
      },
      secondLastPoint,
      targetCenter
    ) : intersection(targetNode, secondLastPoint, targetCenter);
    points[points.length - 1] = endPos;
    return {
      id: edge.id,
      source: edge.start ?? "",
      target: edge.end ?? "",
      startX: startPos.x,
      startY: startPos.y,
      midX,
      midY,
      endX: endPos.x,
      endY: endPos.y,
      points,
      sourceSection: sourceNode?.section,
      targetSection: targetNode?.section,
      sourceWidth: sourceNode?.width,
      sourceHeight: sourceNode?.height,
      targetWidth: targetNode?.width,
      targetHeight: targetNode?.height
    };
  });
}
__name(calculateEdgePositions, "calculateEdgePositions");
function validateLayoutData(data) {
  if (!data) {
    throw new Error("Layout data is required");
  }
  if (!data.config) {
    throw new Error("Configuration is required in layout data");
  }
  if (!Array.isArray(data.nodes)) {
    throw new Error("Nodes array is required in layout data");
  }
  if (!Array.isArray(data.edges)) {
    throw new Error("Edges array is required in layout data");
  }
  return true;
}
__name(validateLayoutData, "validateLayoutData");

// src/render.ts
var render = /* @__PURE__ */ __name(async (data4Layout, svg, {
  insertCluster,
  insertEdge,
  insertEdgeLabel,
  insertMarkers,
  insertNode,
  log,
  positionEdgeLabel
}, { algorithm: _algorithm }) => {
  const nodeDb = {};
  const clusterDb = {};
  const element = svg.select("g");
  insertMarkers(element, data4Layout.markers, data4Layout.type, data4Layout.diagramId);
  const subGraphsEl = element.insert("g").attr("class", "subgraphs");
  const edgePaths = element.insert("g").attr("class", "edgePaths");
  const edgeLabels = element.insert("g").attr("class", "edgeLabels");
  const nodes = element.insert("g").attr("class", "nodes");
  log.debug("Inserting nodes into DOM for dimension calculation");
  await Promise.all(
    data4Layout.nodes.map(async (node) => {
      if (node.isGroup) {
        const clusterNode = {
          ...node,
          id: node.id,
          width: node.width,
          height: node.height
        };
        clusterDb[node.id] = clusterNode;
        nodeDb[node.id] = clusterNode;
        await insertCluster(subGraphsEl, node);
      } else {
        const nodeWithPosition = {
          ...node,
          id: node.id,
          width: node.width,
          height: node.height
        };
        nodeDb[node.id] = nodeWithPosition;
        const nodeEl = await insertNode(nodes, node, {
          config: data4Layout.config,
          dir: data4Layout.direction || "TB"
        });
        const boundingBox = nodeEl.node().getBBox();
        nodeWithPosition.width = boundingBox.width;
        nodeWithPosition.height = boundingBox.height;
        nodeWithPosition.domId = nodeEl;
        log.debug(`Node ${node.id} dimensions: ${boundingBox.width}x${boundingBox.height}`);
      }
    })
  );
  log.debug("Running bidirectional tidy-tree layout algorithm");
  const updatedLayoutData = {
    ...data4Layout,
    nodes: data4Layout.nodes.map((node) => {
      const nodeWithDimensions = nodeDb[node.id];
      return {
        ...node,
        width: nodeWithDimensions.width ?? node.width ?? 100,
        height: nodeWithDimensions.height ?? node.height ?? 50
      };
    })
  };
  const layoutResult = await executeTidyTreeLayout(updatedLayoutData);
  log.debug("Positioning nodes based on bidirectional layout results");
  layoutResult.nodes.forEach((positionedNode) => {
    const node = nodeDb[positionedNode.id];
    if (node?.domId) {
      node.domId.attr("transform", `translate(${positionedNode.x}, ${positionedNode.y})`);
      node.x = positionedNode.x;
      node.y = positionedNode.y;
      log.debug(`Positioned node ${node.id} at (${positionedNode.x}, ${positionedNode.y})`);
    }
  });
  log.debug("Inserting and positioning edges");
  await Promise.all(
    data4Layout.edges.map(async (edge) => {
      await insertEdgeLabel(edgeLabels, edge);
      const startNode = nodeDb[edge.start ?? ""];
      const endNode = nodeDb[edge.end ?? ""];
      if (startNode && endNode) {
        const positionedEdge = layoutResult.edges.find((e) => e.id === edge.id);
        if (positionedEdge) {
          log.debug("APA01 positionedEdge", positionedEdge);
          const edgeWithPath = {
            ...edge,
            points: positionedEdge.points
          };
          const paths = insertEdge(
            edgePaths,
            edgeWithPath,
            clusterDb,
            data4Layout.type,
            startNode,
            endNode,
            data4Layout.diagramId
          );
          positionEdgeLabel(edgeWithPath, paths);
        } else {
          const edgeWithPath = {
            ...edge,
            points: [
              { x: startNode.x ?? 0, y: startNode.y ?? 0 },
              { x: endNode.x ?? 0, y: endNode.y ?? 0 }
            ]
          };
          const paths = insertEdge(
            edgePaths,
            edgeWithPath,
            clusterDb,
            data4Layout.type,
            startNode,
            endNode,
            data4Layout.diagramId
          );
          positionEdgeLabel(edgeWithPath, paths);
        }
      }
    })
  );
  log.debug("Bidirectional tidy-tree rendering completed");
}, "render");

export {
  __name,
  executeTidyTreeLayout,
  validateLayoutData,
  render
};
