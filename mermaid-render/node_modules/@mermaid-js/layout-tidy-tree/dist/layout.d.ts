import type { LayoutData } from 'mermaid';
import type { LayoutResult } from './types.js';
/**
 * Execute the tidy-tree layout algorithm on generic layout data
 *
 * This function takes layout data and uses the non-layered-tidy-tree-layout
 * algorithm to calculate optimal node positions for tree structures.
 *
 * @param data - The layout data containing nodes, edges, and configuration
 * @param config - Mermaid configuration object
 * @returns Promise resolving to layout result with positioned nodes and edges
 */
export declare function executeTidyTreeLayout(data: LayoutData): Promise<LayoutResult>;
/**
 * Validate layout data structure
 * @param data - The data to validate
 * @returns True if data is valid, throws error otherwise
 */
export declare function validateLayoutData(data: LayoutData): boolean;
