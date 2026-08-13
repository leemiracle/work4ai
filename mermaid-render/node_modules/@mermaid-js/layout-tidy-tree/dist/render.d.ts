import type { InternalHelpers, LayoutData, RenderOptions, SVG } from 'mermaid';
/**
 * Render function for bidirectional tidy-tree layout algorithm
 *
 * This follows the same pattern as ELK and dagre renderers:
 * 1. Insert nodes into DOM to get their actual dimensions
 * 2. Run the bidirectional tidy-tree layout algorithm to calculate positions
 * 3. Position the nodes and edges based on layout results
 *
 * The bidirectional layout creates two trees that grow horizontally in opposite
 * directions from a central root node:
 * - Left tree: grows horizontally to the left (children: 1st, 3rd, 5th...)
 * - Right tree: grows horizontally to the right (children: 2nd, 4th, 6th...)
 */
export declare const render: (data4Layout: LayoutData, svg: SVG, { insertCluster, insertEdge, insertEdgeLabel, insertMarkers, insertNode, log, positionEdgeLabel, }: InternalHelpers, { algorithm: _algorithm }: RenderOptions) => Promise<void>;
