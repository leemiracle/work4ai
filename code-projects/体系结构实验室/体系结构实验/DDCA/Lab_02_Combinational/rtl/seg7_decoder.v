/**
 * Simple 7-segment decoder - DDCA Lab 02 / Lab 09 (FPGA)
 *
 * 与本项目 Lab02 (Nand2Tetris) 实现对照：
 * - Nand2Tetris HDL：用逻辑门搭（10+ 个 .hdl 文件）
 * - Verilog：一个 case 语句（15 行）
 *
 * 输出格式（共阳，0 = 亮）：{g, f, e, d, c, b, a}
 */
module seg7_decoder (
    input      [3:0]  hex_digit,
    output reg [6:0]  seg
);
    always @(*) begin
        case (hex_digit)
            4'h0: seg = 7'b1000000;
            4'h1: seg = 7'b1111001;
            4'h2: seg = 7'b0100100;
            4'h3: seg = 7'b0110000;
            4'h4: seg = 7'b0011001;
            4'h5: seg = 7'b0010010;
            4'h6: seg = 7'b0000010;
            4'h7: seg = 7'b1111000;
            4'h8: seg = 7'b0000000;
            4'h9: seg = 7'b0010000;
            4'hA: seg = 7'b0001000;
            4'hB: seg = 7'b0000011;
            4'hC: seg = 7'b1000110;
            4'hD: seg = 7'b0100001;
            4'hE: seg = 7'b0000110;
            4'hF: seg = 7'b0001110;
            default: seg = 7'bxxxxxxx;
        endcase
    end
endmodule
