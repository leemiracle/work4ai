export interface P {
    x: number;
    y: number;
}
export interface RectLike {
    x: number;
    y: number;
    width: number;
    height: number;
    padding?: number;
}
export interface NodeLike {
    intersect?: (p: P) => P | null;
}
export declare const EPS = 1;
export declare const PUSH_OUT = 10;
export declare const onBorder: (bounds: RectLike, p: P, tol?: number) => boolean;
/**
 * Compute intersection between a rectangle (center x/y, width/height) and the line
 * segment from insidePoint -\> outsidePoint. Returns the point on the rectangle border.
 *
 * This version avoids snapping to outsidePoint when certain variables evaluate to 0
 * (previously caused vertical top/bottom cases to miss the border). It only enforces
 * axis-constant behavior for purely vertical/horizontal approaches.
 */
export declare const intersection: (node: RectLike, outsidePoint: P, insidePoint: P) => P;
export declare const outsideNode: (node: RectLike, point: P) => boolean;
export declare const ensureTrulyOutside: (bounds: RectLike, p: P, push?: number) => P;
export declare const makeInsidePoint: (bounds: RectLike, outside: P, center: P) => P;
export declare const tryNodeIntersect: (node: NodeLike, bounds: RectLike, outside: P) => P | null;
export declare const fallbackIntersection: (bounds: RectLike, outside: P, center: P) => P;
export declare const computeNodeIntersection: (node: NodeLike, bounds: RectLike, outside: P, center: P) => P;
export declare const replaceEndpoint: (points: P[], which: "start" | "end", value: P | null | undefined, tol?: number) => void;
