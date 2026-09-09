/**
 * MIPS ALU - DDCA Lab 03
 *
 * 支持 6 种基本运算（Harris & Harris 表 5.1）
 * 配套 testbench: tb_mips_alu.v
 *
 * 与本项目 Expert_03/rtl/alu.v 的对照：
 * - Expert_03 实现 RV32I（10 条指令）
 * - 本文件实现 MIPS（6 条基础指令，可扩展）
 */
module mips_alu (
    input  [3:0]     alucont,        // 4-bit ALU control
    input  [31:0]    a, b,           // 操作数
    output reg [31:0] result,
    output           zero,
    output           overflow
);
    // 6 种控制位（Harris 风格）
    localparam ALU_AND = 4'b0000;
    localparam ALU_OR  = 4'b0001;
    localparam ALU_ADD = 4'b0010;
    localparam ALU_SUB = 4'b0110;
    localparam ALU_SLT = 4'b0111;
    localparam ALU_NOR = 4'b1100;

    // 加减结果
    wire [31:0] sum_a_b   = a + b;
    wire [31:0] diff_a_b  = a - b;

    // 溢出检测
    wire ovf_add = (a[31] == b[31])  && (sum_a_b[31]  != a[31]);
    wire ovf_sub = (a[31] != b[31])  && (diff_a_b[31] != a[31]);

    always @(*) begin
        case (alucont)
            ALU_AND: result = a & b;
            ALU_OR:  result = a | b;
            ALU_ADD: result = sum_a_b;
            ALU_SUB: result = diff_a_b;
            ALU_SLT: result = ($signed(a) < $signed(b)) ? 32'h1 : 32'h0;
            ALU_NOR: result = ~(a | b);
            default: result = 32'hxxxxxxxx;
        endcase
    end

    assign zero     = (result == 32'h0);
    assign overflow = (alucont == ALU_ADD) ? ovf_add :
                      (alucont == ALU_SUB) ? ovf_sub : 1'b0;
endmodule
