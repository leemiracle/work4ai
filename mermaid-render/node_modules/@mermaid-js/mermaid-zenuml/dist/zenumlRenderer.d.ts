export declare const calculateSvgSizeAttrs: (width: number, height: number, useMaxWidth: boolean) => Map<string, string>;
/**
 * Draws a ZenUML diagram in the SVG element with id: id based on the
 * graph definition in text, using native SVG rendering.
 *
 * @param text - The text of the diagram
 * @param id - The id of the diagram which will be used as a DOM element id
 */
export declare const draw: (text: string, id: string) => Promise<void>;
declare const _default: {
    draw: (text: string, id: string) => Promise<void>;
};
export default _default;
